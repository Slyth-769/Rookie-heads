"""
Multi-Channel Delivery & Escalation Engine
Handles:
1. Targeted dispatch across Push, SMS, and IVR
2. Automatic escalation loop: Push -> SMS -> IVR -> Warden
3. Configurable acknowledgment timeout windows
4. SMS/USSD/IVR/App acknowledgment resolution
5. Secondary Contact & Local Warden escalation
"""

import threading
import time
import json
from datetime import datetime, timedelta
from .database import get_db
from .geo import is_point_in_radius, is_point_in_polygon
from .templates import render_alert_text, HAZARDS, SEVERITY_LEVELS

class DeliveryEngine:
    def __init__(self):
        self.running = False
        self._thread = None
        self.lock = threading.Lock()
        
    def start(self):
        """Starts the background retry & escalation daemon"""
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._run_escalation_loop, daemon=True)
            self._thread.start()
            print("[DeliveryEngine] Multi-channel retry & escalation daemon started.")

    def stop(self):
        self.running = False

    def dispatch_alert(self, alert_id):
        """
        Dispatches a new alert to all citizens within the geofenced perimeter.
        Initial channel is PUSH for smartphones, SMS for basic/feature phones.
        """
        conn = get_db()
        c = conn.cursor()

        # Fetch alert details
        c.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        alert = c.fetchone()
        if not alert:
            conn.close()
            return {"error": "Alert not found"}

        hazard_type = alert["hazard_type"]
        severity = alert["severity"]
        area_name = alert["area_name"]
        center_lat = alert["center_lat"]
        center_lng = alert["center_lng"]
        radius_km = alert["radius_km"]
        polygon_json = alert["polygon_json"]
        helplines = alert["helplines"]

        polygon_coords = json.loads(polygon_json) if polygon_json else None

        # Fetch all active citizens
        c.execute("SELECT * FROM citizens")
        citizens = c.fetchall()

        targeted_count = 0
        now = datetime.now().isoformat()

        for citizen in citizens:
            # Spatial filter: within radius or polygon or district match
            in_zone = False
            dist_km = 0.0

            if polygon_coords and len(polygon_coords) >= 3:
                in_zone = is_point_in_polygon(citizen["lat"], citizen["lng"], polygon_coords)
            elif radius_km > 0:
                in_zone, dist_km = is_point_in_radius(citizen["lat"], citizen["lng"], center_lat, center_lng, radius_km)
            else:
                # District name match fallback
                in_zone = citizen["district"].lower() in area_name.lower()

            if in_zone:
                targeted_count += 1
                lang = citizen["language"]
                payload = render_alert_text(hazard_type, severity, area_name, lang, helplines)

                # Channel priority: PUSH for smartphone, SMS for feature phone
                initial_channel = "PUSH" if citizen["device_type"] == "smartphone" else "SMS"

                # Check if already logged
                c.execute("SELECT id FROM delivery_logs WHERE alert_id = ? AND citizen_id = ?", (alert_id, citizen["id"]))
                existing = c.fetchone()

                if not existing:
                    c.execute("""
                    INSERT INTO delivery_logs 
                    (alert_id, citizen_id, channel, status, retry_count, ack_response, sent_at, delivered_at, notes)
                    VALUES (?, ?, ?, 'DELIVERED', 0, 'NONE', ?, ?, ?)
                    """, (alert_id, citizen["id"], initial_channel, now, now, 
                          f"Dispatched via {initial_channel} to {citizen['name']} ({citizen['phone']})"))

                    # Log to telecom simulator events
                    telecom_msg = payload["headline"] if initial_channel == "PUSH" else payload["short_sms"]
                    c.execute("""
                    INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                    VALUES ('OUTBOUND', ?, ?, ?, ?, 'SENT', ?)
                    """, (initial_channel, citizen["phone"], telecom_msg, alert_id, now))

        conn.commit()
        conn.close()
        return {"status": "SUCCESS", "targeted_citizens": targeted_count}

    def _run_escalation_loop(self):
        """
        Background loop checking active alerts and unacknowledged citizens.
        Escalation path: PUSH (timeout) -> SMS (timeout) -> IVR (timeout) -> WARDEN ESCALATION
        """
        while self.running:
            try:
                self._check_and_escalate_unacknowledged()
            except Exception as e:
                print(f"[DeliveryEngine] Escalation loop error: {e}")
            time.sleep(2)  # Check every 2 seconds

    def _check_and_escalate_unacknowledged(self):
        conn = get_db()
        c = conn.cursor()

        # Fetch active alerts
        c.execute("SELECT * FROM alerts WHERE status = 'ACTIVE'")
        active_alerts = c.fetchall()

        now_dt = datetime.now()

        for alert in active_alerts:
            alert_id = alert["id"]
            timeout_sec = alert["ack_timeout_seconds"]
            max_retries = alert["max_retries"]
            area_name = alert["area_name"]
            hazard_type = alert["hazard_type"]
            severity = alert["severity"]
            helplines = alert["helplines"]

            # Fetch logs that are DELIVERED or SENT or READ, but NOT ACKNOWLEDGED and NOT ESCALATED
            c.execute("""
            SELECT l.*, c.name as citizen_name, c.phone as citizen_phone, c.language as citizen_lang,
                   c.device_type, c.secondary_name, c.secondary_phone, c.warden_id, c.block_village,
                   w.name as warden_name, w.phone as warden_phone
            FROM delivery_logs l
            JOIN citizens c ON l.citizen_id = c.id
            LEFT JOIN wardens w ON c.warden_id = w.id
            WHERE l.alert_id = ? AND l.status IN ('SENT', 'DELIVERED', 'READ')
            """, (alert_id,))
            pending_logs = c.fetchall()

            for log in pending_logs:
                sent_time_str = log["sent_at"]
                if not sent_time_str:
                    continue

                sent_dt = datetime.fromisoformat(sent_time_str)
                elapsed = (now_dt - sent_dt).total_seconds()

                if elapsed >= timeout_sec:
                    current_channel = log["channel"]
                    retry_count = log["retry_count"]
                    citizen_phone = log["citizen_phone"]
                    citizen_name = log["citizen_name"]
                    lang = log["citizen_lang"]
                    payload = render_alert_text(hazard_type, severity, area_name, lang, helplines)
                    iso_now = now_dt.isoformat()

                    if current_channel == "PUSH":
                        # Escalate to SMS
                        next_channel = "SMS"
                        c.execute("""
                        UPDATE delivery_logs 
                        SET channel = ?, status = 'DELIVERED', retry_count = retry_count + 1, sent_at = ?, delivered_at = ?,
                            notes = 'Auto-escalated from PUSH to SMS due to acknowledgment timeout'
                        WHERE id = ?
                        """, (next_channel, iso_now, iso_now, log["id"]))

                        c.execute("""
                        INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                        VALUES ('OUTBOUND', 'SMS', ?, ?, ?, 'SENT', ?)
                        """, (citizen_phone, f"[ESCALATION 1/SMS] {payload['short_sms']}", alert_id, iso_now))
                        conn.commit()
                        print(f"[DeliveryEngine] ESCALATED: {citizen_name} -> SMS")

                    elif current_channel == "SMS":
                        # Escalate to Automated IVR Voice Call
                        next_channel = "IVR"
                        c.execute("""
                        UPDATE delivery_logs 
                        SET channel = ?, status = 'DELIVERED', retry_count = retry_count + 1, sent_at = ?, delivered_at = ?,
                            notes = 'Auto-escalated from SMS to IVR Voice Call'
                        WHERE id = ?
                        """, (next_channel, iso_now, iso_now, log["id"]))

                        c.execute("""
                        INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                        VALUES ('OUTBOUND', 'IVR', ?, ?, ?, 'CALL_RINGING', ?)
                        """, (citizen_phone, f"[ESCALATION 2/IVR VOICE CALL] Script: {payload['ivr_script']}", alert_id, iso_now))
                        conn.commit()
                        print(f"[DeliveryEngine] ESCALATED: {citizen_name} -> IVR Voice Call")

                    elif current_channel == "IVR" or retry_count >= max_retries:
                        # Unresponsive across direct channels:
                        # DISPATCH AUTOMATED EMERGENCY CALL TO SAVED CONTACT (KIN) & FIELD WARDEN
                        warden_name = log["warden_name"] or "Sector Incident Warden"
                        warden_phone = log["warden_phone"] or "+919861011111"
                        sec_name = log["secondary_name"] or "Emergency Kin Contact"
                        sec_phone = log["secondary_phone"] or "N/A"
                        village = log["block_village"]

                        # Script for the automated voice call to the saved contact
                        kin_call_script = (
                            f"[ROOKIES EMERGENCY KIN CALL] Urgent Alert for {sec_name}: Your saved contact, "
                            f"{citizen_name} at {village}, has NOT responded to the {hazard_type} {severity} alert "
                            f"within the 30-second emergency timeline. They are in active danger. Please contact them "
                            f"immediately or assist evacuation. Emergency Hotline: 112."
                        )

                        escalation_note = (
                            f"UNRESPONSIVE >30s: Emergency voice call dispatched to saved contact {sec_name} ({sec_phone}). "
                            f"Civil Defense Warden {warden_name} alerted."
                        )

                        c.execute("""
                        UPDATE delivery_logs 
                        SET channel = 'WARDEN', status = 'ESCALATED', retry_count = retry_count + 1, sent_at = ?,
                            notes = ?
                        WHERE id = ?
                        """, (iso_now, escalation_note, log["id"]))

                        # 1. DISPATCH AUTOMATED VOICE CALL TO SAVED CONTACT
                        if sec_phone and sec_phone != "N/A":
                            c.execute("""
                            INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                            VALUES ('OUTBOUND', 'IVR', ?, ?, ?, 'KIN_EMERGENCY_CALL', ?)
                            """, (sec_phone, kin_call_script, alert_id, iso_now))

                            # Also send urgent SMS to saved contact
                            kin_sms = (
                                f"[ROOKIES KIN ALERT] URGENT: {citizen_name} has NOT responded to {hazard_type} {severity} "
                                f"at {village}. They may be in danger. Please check on them immediately! Helpline: 112."
                            )
                            c.execute("""
                            INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                            VALUES ('OUTBOUND', 'SMS', ?, ?, ?, 'KIN_SMS_SENT', ?)
                            """, (sec_phone, kin_sms, alert_id, iso_now))

                        # 2. DISPATCH LOCAL CIVIL DEFENSE WARDEN
                        warden_sms = (
                            f"[WARDEN DISPATCH] CRITICAL: Unresponsive citizen {citizen_name} ({citizen_phone}) "
                            f"at {village} during {hazard_type} {severity}. Saved Kin {sec_name} ({sec_phone}) called. "
                            f"Please conduct physical verification/evacuation."
                        )
                        c.execute("""
                        INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
                        VALUES ('OUTBOUND', 'SMS', ?, ?, ?, 'WARDEN_DISPATCHED', ?)
                        """, (warden_phone, warden_sms, alert_id, iso_now))

                        conn.commit()
                        print(f"[DeliveryEngine] EMERGENCY KIN CALL DISPATCHED: {sec_name} ({sec_phone}) for {citizen_name}")

        conn.close()

    def record_acknowledgment(self, alert_id, citizen_id=None, phone=None, response_type="SAFE", channel="APP", offline=0):
        """
        Records citizen acknowledgment and halts further escalation.
        Response types: 'SAFE', 'RESCUE', 'NEED_SUPPLIES'
        """
        conn = get_db()
        c = conn.cursor()
        now = datetime.now().isoformat()

        # If citizen_id is not provided, look up by phone
        if not citizen_id and phone:
            c.execute("SELECT id FROM citizens WHERE phone = ?", (phone,))
            row = c.fetchone()
            if row:
                citizen_id = row["id"]

        if not citizen_id:
            conn.close()
            return {"error": "Citizen not identified"}

        # Find delivery log for this alert & citizen
        c.execute("""
        SELECT id, channel, status FROM delivery_logs 
        WHERE alert_id = ? AND citizen_id = ?
        """, (alert_id, citizen_id))
        log = c.fetchone()

        if log:
            c.execute("""
            UPDATE delivery_logs 
            SET status = 'ACKNOWLEDGED', ack_response = ?, acknowledged_at = ?, offline_cached = ?,
                notes = ?
            WHERE id = ?
            """, (response_type, now, 1 if offline else 0, 
                  f"Acknowledged via {channel} as '{response_type}'", log["id"]))
        else:
            # If log not found, create acknowledged record
            c.execute("""
            INSERT INTO delivery_logs 
            (alert_id, citizen_id, channel, status, retry_count, ack_response, acknowledged_at, offline_cached, notes)
            VALUES (?, ?, ?, 'ACKNOWLEDGED', 0, ?, ?, ?, ?)
            """, (alert_id, citizen_id, channel, response_type, now, 1 if offline else 0, f"Direct Acknowledgment via {channel}"))

        conn.commit()
        conn.close()
        return {"status": "SUCCESS", "citizen_id": citizen_id, "response": response_type, "timestamp": now}

    def simulate_incoming_sms(self, phone, text):
        """
        Processes simulated incoming SMS from citizen or feature phone.
        e.g., '1' -> SAFE, '2' -> RESCUE, 'OK' -> SAFE, 'HELP' -> RESCUE
        """
        text_clean = text.strip().upper()
        now = datetime.now().isoformat()
        conn = get_db()
        c = conn.cursor()

        # Find latest active alert
        c.execute("SELECT id FROM alerts WHERE status = 'ACTIVE' ORDER BY created_at DESC LIMIT 1")
        alert = c.fetchone()
        
        c.execute("""
        INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
        VALUES ('INBOUND', 'SMS', ?, ?, ?, 'RECEIVED', ?)
        """, (phone, text, alert["id"] if alert else None, now))
        conn.commit()
        conn.close()

        if not alert:
            return {"status": "NO_ACTIVE_ALERT", "message": "No active emergency alert found"}

        alert_id = alert["id"]
        response_type = "SAFE"
        if text_clean in ["2", "RESCUE", "HELP", "SOS"]:
            response_type = "RESCUE"
        elif text_clean in ["1", "OK", "SAFE", "YES", "HAAN", "THEEK"]:
            response_type = "SAFE"

        return self.record_acknowledgment(alert_id, phone=phone, response_type=response_type, channel="SMS")

    def simulate_ussd_dial(self, phone, ussd_code):
        """
        Simulates USSD dial code: e.g. *112*1# (Safe) or *112*2# (Rescue)
        Allows instant 2G/GSM offline network-level signaling.
        """
        now = datetime.now().isoformat()
        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT id FROM alerts WHERE status = 'ACTIVE' ORDER BY created_at DESC LIMIT 1")
        alert = c.fetchone()

        c.execute("""
        INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
        VALUES ('INBOUND', 'USSD', ?, ?, ?, 'EXECUTED', ?)
        """, (phone, f"USSD Dial: {ussd_code}", alert["id"] if alert else None, now))
        conn.commit()
        conn.close()

        if not alert:
            return {"status": "NO_ACTIVE_ALERT", "message": "USSD: No active disaster session"}

        alert_id = alert["id"]
        response_type = "RESCUE" if "*2#" in ussd_code else "SAFE"
        return self.record_acknowledgment(alert_id, phone=phone, response_type=response_type, channel="USSD")

# Global singleton
delivery_engine = DeliveryEngine()
