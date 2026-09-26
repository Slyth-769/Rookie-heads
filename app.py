"""
Disaster Management Alert System — Main Backend Application
Serves REST APIs, Webhooks, Multi-channel Delivery Engine, and Mobile/Admin Frontends.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, send_file

from engine.database import get_db, init_db
from engine.templates import (
    LANGUAGES, HAZARDS, SEVERITY_LEVELS,
    render_alert_text, get_all_translations_preview
)
from engine.geo import DISTRICT_CENTROIDS, haversine_distance_km, is_point_in_radius, is_point_in_polygon
from engine.delivery_engine import delivery_engine

app = Flask(__name__, static_folder="static", static_url_path="")

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

# ----------------- Static Frontend Routes -----------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")

@app.route("/download/zip")
def download_zip():
    zip_path = os.path.join(os.path.dirname(__file__), "static", "rookies-disaster-alert-system.zip")
    return send_file(zip_path, as_attachment=True, download_name="rookies-disaster-alert-system.zip")

# ----------------- Reference & Template APIs -----------------
@app.route("/api/languages", methods=["GET"])
def get_languages():
    return jsonify(LANGUAGES)

@app.route("/api/hazards", methods=["GET"])
def get_hazards():
    hazard_list = []
    for k, v in HAZARDS.items():
        hazard_list.append({
            "id": k,
            "name": k,
            "icon": v["icon"],
            "default_helpline": v["default_helpline"]
        })
    return jsonify({
        "hazards": hazard_list,
        "severities": SEVERITY_LEVELS
    })

@app.route("/api/districts", methods=["GET"])
def get_districts():
    return jsonify(DISTRICT_CENTROIDS)

@app.route("/api/template/preview", methods=["POST"])
def preview_templates():
    data = request.json or {}
    hazard_type = data.get("hazard_type", "Cyclone")
    severity = data.get("severity", "Warning")
    area_name = data.get("area_name", "Puri Coastal Zone")
    helpline = data.get("helpline")
    
    previews = get_all_translations_preview(hazard_type, severity, area_name, helpline)
    return jsonify({
        "hazard_type": hazard_type,
        "severity": severity,
        "area_name": area_name,
        "previews": previews
    })

# ----------------- Citizen Management APIs -----------------
@app.route("/api/citizens", methods=["GET"])
def list_citizens():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    SELECT c.*, w.name as warden_name, w.phone as warden_phone
    FROM citizens c
    LEFT JOIN wardens w ON c.warden_id = w.id
    ORDER BY c.district, c.name
    """)
    citizens = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(citizens)

@app.route("/api/citizens", methods=["POST"])
def register_citizen():
    data = request.json or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    language = data.get("language", "or")
    lat = float(data.get("lat", 19.8135))
    lng = float(data.get("lng", 85.8312))
    district = data.get("district", "Puri")
    block_village = data.get("block_village", "Ward 1")
    device_type = data.get("device_type", "smartphone")
    secondary_name = data.get("secondary_name", "")
    secondary_phone = data.get("secondary_phone", "")

    if not name or not phone:
        return jsonify({"error": "Name and phone number are required"}), 400

    conn = get_db()
    c = conn.cursor()
    
    # Assign local warden if available
    c.execute("SELECT id FROM wardens WHERE district = ? LIMIT 1", (district,))
    w = c.fetchone()
    warden_id = w["id"] if w else 1

    now = datetime.now().isoformat()
    try:
        c.execute("""
        INSERT INTO citizens 
        (name, phone, language, lat, lng, district, block_village, device_type, secondary_name, secondary_phone, warden_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, language, lat, lng, district, block_village, device_type, secondary_name, secondary_phone, warden_id, now))
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        return jsonify({"status": "SUCCESS", "id": new_id, "message": "Citizen registered successfully"}), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Registration failed (phone may already exist): {str(e)}"}), 400

@app.route("/api/citizens/<int:citizen_id>", methods=["PUT"])
def update_citizen(citizen_id):
    data = request.json or {}
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,))
    existing = c.fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Citizen not found"}), 404

    language = data.get("language", existing["language"])
    lat = float(data.get("lat", existing["lat"]))
    lng = float(data.get("lng", existing["lng"]))
    district = data.get("district", existing["district"])
    block_village = data.get("block_village", existing["block_village"])
    device_type = data.get("device_type", existing["device_type"])

    c.execute("""
    UPDATE citizens 
    SET language = ?, lat = ?, lng = ?, district = ?, block_village = ?, device_type = ?
    WHERE id = ?
    """, (language, lat, lng, district, block_village, device_type, citizen_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "SUCCESS", "message": "Citizen preferences updated successfully"})

# ----------------- Alert Creation & Dispatch APIs -----------------
@app.route("/api/alerts", methods=["POST"])
def create_alert():
    data = request.json or {}
    hazard_type = data.get("hazard_type", "Cyclone")
    severity = data.get("severity", "Warning")
    area_name = data.get("area_name", "Puri Coastal Sector")
    center_lat = float(data.get("center_lat", 19.8135))
    center_lng = float(data.get("center_lng", 85.8312))
    radius_km = float(data.get("radius_km", 30))
    polygon_json = json.dumps(data.get("polygon_coords")) if data.get("polygon_coords") else None
    
    # Helplines
    default_helpline = HAZARDS.get(hazard_type, {}).get("default_helpline", "112, 1070")
    helplines = data.get("helplines") or default_helpline
    
    # Escalation config
    ack_timeout_seconds = int(data.get("ack_timeout_seconds", 30))  # Default 30s for live demonstration
    max_retries = int(data.get("max_retries", 3))

    alert_id = f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now()
    expires = (now + timedelta(hours=int(data.get("duration_hours", 24)))).isoformat()
    now_iso = now.isoformat()

    conn = get_db()
    c = conn.cursor()
    c.execute("""
    INSERT INTO alerts 
    (id, hazard_type, severity, area_name, center_lat, center_lng, radius_km, polygon_json, helplines, created_at, expires_at, status, ack_timeout_seconds, max_retries)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
    """, (alert_id, hazard_type, severity, area_name, center_lat, center_lng, radius_km, polygon_json, helplines, now_iso, expires, ack_timeout_seconds, max_retries))
    conn.commit()
    conn.close()

    # Dispatch immediately via multi-channel delivery engine
    dispatch_res = delivery_engine.dispatch_alert(alert_id)

    return jsonify({
        "status": "SUCCESS",
        "alert_id": alert_id,
        "dispatch": dispatch_res
    }), 201

@app.route("/api/alerts", methods=["GET"])
def list_alerts():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    SELECT a.*, 
           (SELECT COUNT(*) FROM delivery_logs WHERE alert_id = a.id) as total_targeted,
           (SELECT COUNT(*) FROM delivery_logs WHERE alert_id = a.id AND status = 'ACKNOWLEDGED') as acknowledged_count,
           (SELECT COUNT(*) FROM delivery_logs WHERE alert_id = a.id AND status = 'ESCALATED') as escalated_count
    FROM alerts a
    ORDER BY a.created_at DESC
    """)
    alerts = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(alerts)

# ----------------- Real-time Alert Tracking & Funnel -----------------
@app.route("/api/alerts/<alert_id>/tracking", methods=["GET"])
def get_alert_tracking(alert_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = c.fetchone()
    if not alert:
        conn.close()
        return jsonify({"error": "Alert not found"}), 404

    # Detailed per-citizen logs
    c.execute("""
    SELECT l.*, c.name, c.phone, c.language, c.lat, c.lng, c.district, c.block_village, c.device_type,
           c.secondary_name, c.secondary_phone,
           w.name as warden_name, w.phone as warden_phone
    FROM delivery_logs l
    JOIN citizens c ON l.citizen_id = c.id
    LEFT JOIN wardens w ON c.warden_id = w.id
    WHERE l.alert_id = ?
    ORDER BY 
        CASE l.status
            WHEN 'ESCALATED' THEN 1
            WHEN 'DELIVERED' THEN 2
            WHEN 'READ' THEN 3
            WHEN 'ACKNOWLEDGED' THEN 4
            ELSE 5
        END, l.id
    """, (alert_id,))
    logs = [dict(row) for row in c.fetchall()]

    # Summary metrics
    total = len(logs)
    acknowledged = sum(1 for x in logs if x["status"] == "ACKNOWLEDGED")
    safe_count = sum(1 for x in logs if x["status"] == "ACKNOWLEDGED" and x["ack_response"] == "SAFE")
    rescue_count = sum(1 for x in logs if x["status"] == "ACKNOWLEDGED" and x["ack_response"] == "RESCUE")
    escalated = sum(1 for x in logs if x["status"] == "ESCALATED")
    unacknowledged = total - acknowledged

    channel_breakdown = {
        "PUSH": sum(1 for x in logs if x["channel"] == "PUSH"),
        "SMS": sum(1 for x in logs if x["channel"] == "SMS"),
        "IVR": sum(1 for x in logs if x["channel"] == "IVR"),
        "WARDEN": sum(1 for x in logs if x["channel"] == "WARDEN")
    }

    conn.close()
    return jsonify({
        "alert": dict(alert),
        "summary": {
            "total_targeted": total,
            "acknowledged": acknowledged,
            "safe_count": safe_count,
            "rescue_count": rescue_count,
            "escalated": escalated,
            "unacknowledged": unacknowledged,
            "ack_percentage": round((acknowledged / total * 100), 1) if total > 0 else 0,
            "channels": channel_breakdown
        },
        "delivery_logs": logs
    })

# ----------------- Citizen App & Acknowledgment Endpoints -----------------
@app.route("/api/citizen/<int:citizen_id>/active-alert", methods=["GET"])
def get_citizen_active_alert(citizen_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,))
    citizen = c.fetchone()
    if not citizen:
        conn.close()
        return jsonify({"error": "Citizen not found"}), 404

    # Check latest delivery log for this citizen
    c.execute("""
    SELECT l.*, a.hazard_type, a.severity, a.area_name, a.center_lat, a.center_lng, a.radius_km, a.helplines, a.expires_at, a.ack_timeout_seconds
    FROM delivery_logs l
    JOIN alerts a ON l.alert_id = a.id
    WHERE l.citizen_id = ? AND a.status = 'ACTIVE'
    ORDER BY l.id DESC LIMIT 1
    """, (citizen_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"has_alert": False, "citizen": dict(citizen)})

    lang = citizen["language"]
    payload = render_alert_text(row["hazard_type"], row["severity"], row["area_name"], lang, row["helplines"])

    # Calculate distance to epicenter
    dist_km = round(haversine_distance_km(citizen["lat"], citizen["lng"], row["center_lat"], row["center_lng"]), 1)

    return jsonify({
        "has_alert": True,
        "citizen": dict(citizen),
        "delivery_log": {
            "id": row["id"],
            "alert_id": row["alert_id"],
            "channel": row["channel"],
            "status": row["status"],
            "ack_response": row["ack_response"],
            "sent_at": row["sent_at"],
            "acknowledged_at": row["acknowledged_at"],
            "retry_count": row["retry_count"]
        },
        "alert_payload": payload,
        "distance_to_epicenter_km": dist_km,
        "expires_at": row["expires_at"]
    })

@app.route("/api/alerts/<alert_id>/read", methods=["POST"])
def mark_alert_read(alert_id):
    data = request.json or {}
    citizen_id = data.get("citizen_id")
    if not citizen_id:
        return jsonify({"error": "citizen_id required"}), 400

    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""
    UPDATE delivery_logs 
    SET status = 'READ', read_at = ?
    WHERE alert_id = ? AND citizen_id = ? AND status = 'DELIVERED'
    """, (now, alert_id, citizen_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "SUCCESS", "read_at": now})

@app.route("/api/alerts/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    """
    Called by Citizen App (Safe / Need Rescue) or offline queue batch sync.
    """
    data = request.json or {}
    citizen_id = data.get("citizen_id")
    phone = data.get("phone")
    response_type = data.get("response_type", "SAFE")  # SAFE or RESCUE
    channel = data.get("channel", "APP")
    offline = bool(data.get("offline", False))

    res = delivery_engine.record_acknowledgment(
        alert_id=alert_id,
        citizen_id=citizen_id,
        phone=phone,
        response_type=response_type,
        channel=channel,
        offline=offline
    )
    return jsonify(res)

# ----------------- Telecom Gateway Simulation APIs -----------------
@app.route("/api/sms/incoming", methods=["POST"])
def incoming_sms():
    """
    Simulates inbound SMS gateway (e.g. citizen texting '1' or 'SAFE' from basic phone).
    """
    data = request.json or {}
    phone = data.get("phone", "").strip()
    text = data.get("body", "").strip()
    if not phone or not text:
        return jsonify({"error": "Phone and body required"}), 400

    res = delivery_engine.simulate_incoming_sms(phone, text)
    return jsonify(res)

@app.route("/api/ussd/dial", methods=["POST"])
def dial_ussd():
    """
    Simulates dialing USSD code *112*1# or *112*2# on low-end phone.
    """
    data = request.json or {}
    phone = data.get("phone", "").strip()
    ussd_code = data.get("code", "*112*1#").strip()
    if not phone:
        return jsonify({"error": "Phone required"}), 400

    res = delivery_engine.simulate_ussd_dial(phone, ussd_code)
    return jsonify(res)

@app.route("/api/ivr/respond", methods=["POST"])
def ivr_respond():
    """
    Simulates citizen pressing DTMF digit during automated IVR voice call fallback.
    Digit 1 = SAFE, Digit 2 = RESCUE
    """
    data = request.json or {}
    alert_id = data.get("alert_id")
    phone = data.get("phone")
    digit = str(data.get("digit", "1")).strip()

    response_type = "SAFE" if digit == "1" else "RESCUE"
    res = delivery_engine.record_acknowledgment(
        alert_id=alert_id,
        phone=phone,
        response_type=response_type,
        channel="IVR"
    )
    return jsonify(res)

@app.route("/api/emergency/distress", methods=["GET"])
def get_emergency_distress():
    """
    Returns lists of:
    1. Unresponsive citizens in active alerts (>30s without acknowledgment or escalated)
    2. Citizens who actively requested SOS rescue
    """
    conn = get_db()
    c = conn.cursor()
    now_dt = datetime.now()

    # 1. Unresponsive citizens
    c.execute("""
    SELECT l.*, c.name, c.phone, c.language, c.lat, c.lng, c.district, c.block_village, c.device_type,
           c.secondary_name, c.secondary_phone,
           w.name as warden_name, w.phone as warden_phone,
           a.hazard_type, a.severity, a.area_name, a.ack_timeout_seconds
    FROM delivery_logs l
    JOIN citizens c ON l.citizen_id = c.id
    JOIN alerts a ON l.alert_id = a.id
    LEFT JOIN wardens w ON c.warden_id = w.id
    WHERE a.status = 'ACTIVE' AND l.status IN ('DELIVERED', 'READ', 'ESCALATED', 'SENT') AND l.status != 'ACKNOWLEDGED'
    ORDER BY l.sent_at ASC
    """)
    unresponsive_rows = []
    for r in c.fetchall():
        d = dict(r)
        sent_time_str = d["sent_at"]
        elapsed = 0
        if sent_time_str:
            sent_dt = datetime.fromisoformat(sent_time_str)
            elapsed = int((now_dt - sent_dt).total_seconds())
        d["elapsed_seconds"] = elapsed
        
        c2 = conn.cursor()
        c2.execute("SELECT message, created_at FROM telecom_events WHERE phone = ? AND status = 'KIN_EMERGENCY_CALL' ORDER BY id DESC LIMIT 1", (d["secondary_phone"],))
        kin_ev = c2.fetchone()
        d["kin_call_dispatched"] = True if kin_ev or d["status"] == "ESCALATED" or elapsed >= 30 else False
        d["kin_call_script"] = kin_ev[0] if kin_ev else f"[ROOKIES EMERGENCY KIN CALL] Urgent: Your contact {d['name']} at {d['block_village']} has NOT responded to the {d['hazard_type']} {d['severity']} warning after 30s. They are in active danger. Please check on them immediately! Helpline: 112."
        unresponsive_rows.append(d)

    # 2. Rescue SOS requests
    c.execute("""
    SELECT l.*, c.name, c.phone, c.language, c.lat, c.lng, c.district, c.block_village, c.device_type,
           c.secondary_name, c.secondary_phone,
           w.name as warden_name, w.phone as warden_phone,
           a.hazard_type, a.severity, a.area_name
    FROM delivery_logs l
    JOIN citizens c ON l.citizen_id = c.id
    JOIN alerts a ON l.alert_id = a.id
    LEFT JOIN wardens w ON c.warden_id = w.id
    WHERE a.status = 'ACTIVE' AND l.ack_response = 'RESCUE'
    ORDER BY l.acknowledged_at DESC
    """)
    rescue_rows = [dict(r) for r in c.fetchall()]

    conn.close()
    return jsonify({
        "unresponsive_citizens": unresponsive_rows,
        "sos_rescue_requests": rescue_rows
    })

@app.route("/api/kin/emergency-call", methods=["POST"])
def trigger_kin_call():
    """
    Manually triggers an automated emergency voice call to the saved contact
    """
    data = request.json or {}
    citizen_id = data.get("citizen_id")
    alert_id = data.get("alert_id")
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,))
    citizen = c.fetchone()
    if not citizen:
        conn.close()
        return jsonify({"error": "Citizen not found"}), 404

    c.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    alert = c.fetchone()
    hazard_type = alert["hazard_type"] if alert else "Disaster"
    severity = alert["severity"] if alert else "Emergency"

    sec_name = citizen["secondary_name"] or "Emergency Kin Contact"
    sec_phone = citizen["secondary_phone"] or "+919861012346"
    now_iso = datetime.now().isoformat()

    script = (
        f"[ROOKIES EMERGENCY KIN CALL] Urgent Alert for {sec_name}: Your saved contact, "
        f"{citizen['name']} at {citizen['block_village']}, has NOT responded to the {hazard_type} {severity} alert "
        f"within the 30-second emergency timeline. They are in active danger. Please contact them "
        f"immediately or assist evacuation. Emergency Hotline: 112."
    )

    c.execute("""
    INSERT INTO telecom_events (direction, channel, phone, message, alert_id, status, created_at)
    VALUES ('OUTBOUND', 'IVR', ?, ?, ?, 'KIN_EMERGENCY_CALL', ?)
    """, (sec_phone, script, alert_id, now_iso))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "SUCCESS",
        "kin_name": sec_name,
        "kin_phone": sec_phone,
        "script": script,
        "timestamp": now_iso
    })

@app.route("/api/telecom/events", methods=["GET"])
def get_telecom_events():
    conn = get_db()
    c = conn.cursor()
    limit = int(request.args.get("limit", 50))
    c.execute("SELECT * FROM telecom_events ORDER BY id DESC LIMIT ?", (limit,))
    events = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(events)

# ----------------- Admin Manual Override APIs -----------------
@app.route("/api/alerts/<alert_id>/manual-override", methods=["POST"])
def manual_override(alert_id):
    """
    Authority override:
    - action: 'ESCALATE_CHANNEL', 'DISPATCH_WARDEN', 'MARK_SAFE', 'CANCEL_ALERT'
    """
    data = request.json or {}
    action = data.get("action")
    citizen_id = data.get("citizen_id")
    target_channel = data.get("channel", "IVR")
    now = datetime.now().isoformat()

    conn = get_db()
    c = conn.cursor()

    if action == "ESCALATE_CHANNEL" and citizen_id:
        c.execute("""
        UPDATE delivery_logs 
        SET channel = ?, status = 'DELIVERED', retry_count = retry_count + 1, sent_at = ?,
            notes = 'Manual override: channel escalated by authority'
        WHERE alert_id = ? AND citizen_id = ?
        """, (target_channel, now, alert_id, citizen_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": f"Citizen escalated to {target_channel}"})

    elif action == "DISPATCH_WARDEN" and citizen_id:
        c.execute("""
        UPDATE delivery_logs 
        SET channel = 'WARDEN', status = 'ESCALATED', sent_at = ?,
            notes = 'Manual emergency field warden dispatched by authority'
        WHERE alert_id = ? AND citizen_id = ?
        """, (now, alert_id, citizen_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Emergency Warden dispatched!"})

    elif action == "MARK_SAFE" and citizen_id:
        delivery_engine.record_acknowledgment(alert_id, citizen_id=citizen_id, response_type="SAFE", channel="AUTHORITY_OVERRIDE")
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Citizen manually confirmed SAFE"})

    elif action == "CANCEL_ALERT":
        c.execute("UPDATE alerts SET status = 'CANCELLED' WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Alert cancelled"})

    conn.close()
    return jsonify({"error": "Invalid action"}), 400

# ----------------- Overview KPIs -----------------
@app.route("/api/stats/overview", methods=["GET"])
def get_stats_overview():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE'")
    active_alerts = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM citizens")
    total_citizens = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM delivery_logs WHERE status = 'ACKNOWLEDGED'")
    total_acked = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM delivery_logs WHERE status = 'ESCALATED'")
    total_escalated = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM telecom_events WHERE direction = 'OUTBOUND'")
    outbound_pings = c.fetchone()[0]

    conn.close()
    return jsonify({
        "active_alerts": active_alerts,
        "total_citizens": total_citizens,
        "total_acknowledged": total_acked,
        "total_escalated_to_warden": total_escalated,
        "outbound_telecom_messages": outbound_pings
    })

# Start delivery escalation daemon
delivery_engine.start()

if __name__ == "__main__":
    init_db()
    print("\n=======================================================")
    print(" DISASTER MANAGEMENT ALERT SYSTEM (NDMA/OSDMA Compliant)")
    print(" Running on http://127.0.0.1:5050")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=5050, debug=False)
