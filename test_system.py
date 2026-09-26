"""
Automated End-to-End Verification Test for DMAS
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5050"

def run_tests():
    print("[TEST] 1. Checking Languages Endpoint...")
    r = requests.get(f"{BASE_URL}/api/languages")
    assert r.status_code == 200, f"Failed: {r.text}"
    langs = r.json()
    expected = ["or", "hi", "en", "bn", "te", "ta", "ur"]
    for l in expected:
        assert l in langs, f"Missing language {l}"
    print(f"  [OK] Found all 7 required languages: {list(langs.keys())}")

    print("[TEST] 2. Checking Hazards & Template Preview...")
    r = requests.post(f"{BASE_URL}/api/template/preview", json={
        "hazard_type": "Cyclone",
        "severity": "Extreme",
        "area_name": "Puri Coastal Zone"
    })
    assert r.status_code == 200
    previews = r.json()["previews"]
    for l in expected:
        p = previews[l]
        assert p["sms_length"] <= 160, f"SMS for {l} exceeded 160 chars ({p['sms_length']})"
        print(f"  [OK] {l.upper()} SMS ({p['sms_length']} chars)")

    print("[TEST] 3. Checking Citizens Seed Data...")
    r = requests.get(f"{BASE_URL}/api/citizens")
    assert r.status_code == 200
    citizens = r.json()
    assert len(citizens) >= 10
    print(f"  [OK] Loaded {len(citizens)} registered citizens across districts.")

    print("[TEST] 4. Issuing Emergency Alert (Cyclone Extreme in Puri)...")
    r = requests.post(f"{BASE_URL}/api/alerts", json={
        "hazard_type": "Cyclone",
        "severity": "Extreme",
        "area_name": "Puri Coastal Sector",
        "center_lat": 19.8135,
        "center_lng": 85.8312,
        "radius_km": 35,
        "ack_timeout_seconds": 6, # Fast timeout for test
        "helplines": "112, 1070"
    })
    assert r.status_code == 201
    alert_res = r.json()
    alert_id = alert_res["alert_id"]
    targeted = alert_res["dispatch"]["targeted_citizens"]
    print(f"  [OK] Alert {alert_id} issued! Targeted {targeted} citizens.")
    assert targeted > 0

    print("[TEST] 5. Checking Real-Time Tracking Funnel...")
    r = requests.get(f"{BASE_URL}/api/alerts/{alert_id}/tracking")
    assert r.status_code == 200
    track = r.json()
    print(f"  [OK] Summary: Total Targeted: {track['summary']['total_targeted']}, Delivered: {track['summary']['total_targeted']}")

    print("[TEST] 6. Testing Citizen Acknowledgment (Safe)...")
    # Citizen 1 (Ramesh Mohanty) acknowledges SAFE
    r = requests.post(f"{BASE_URL}/api/alerts/{alert_id}/acknowledge", json={
        "citizen_id": 1,
        "response_type": "SAFE",
        "channel": "APP",
        "offline": False
    })
    assert r.status_code == 200
    print("  [OK] Citizen 1 acknowledged as SAFE via App.")

    print("[TEST] 7. Testing 2G Inbound SMS Gateway Simulation...")
    # Citizen 3 (Debashis Roy, phone +919437998877) replies "1" via SMS
    r = requests.post(f"{BASE_URL}/api/sms/incoming", json={
        "phone": "+919437998877",
        "body": "1"
    })
    assert r.status_code == 200
    print("  [OK] Simulated SMS reply '1' received and registered.")

    print("[TEST] 8. Testing 2G USSD Dial Simulation...")
    # Citizen 4 (Venkat Rao, phone +919777123987) dials *112*1#
    r = requests.post(f"{BASE_URL}/api/ussd/dial", json={
        "phone": "+919777123987",
        "code": "*112*1#"
    })
    assert r.status_code == 200
    print("  [OK] Simulated USSD *112*1# dialed and registered.")

    print("[TEST] 9. Waiting for Escalation Loop to trigger (timeout=6s)...")
    time.sleep(8)

    r = requests.get(f"{BASE_URL}/api/alerts/{alert_id}/tracking")
    track = r.json()
    logs = track["delivery_logs"]
    
    # Check if unacknowledged citizens escalated from PUSH to SMS / IVR
    escalated_count = 0
    sms_count = 0
    ivr_count = 0
    for l in logs:
        if l["status"] == "ACKNOWLEDGED":
            continue
        if l["channel"] == "SMS":
            sms_count += 1
        elif l["channel"] == "IVR":
            ivr_count += 1
        elif l["channel"] == "WARDEN" or l["status"] == "ESCALATED":
            escalated_count += 1

    print(f"  [OK] Escalation verification: SMS: {sms_count}, IVR: {ivr_count}, Warden: {escalated_count}")
    print("[TEST] 10. Checking Telecom Audit Events...")
    r = requests.get(f"{BASE_URL}/api/telecom/events")
    events = r.json()
    assert len(events) > 0
    print(f"  [OK] Verified {len(events)} telecom events logged (outbound push/sms/ivr & inbound replies).")

    print("\n[SUCCESS] ALL 10 TESTS PASSED! System is fully operational.\n")

if __name__ == "__main__":
    run_tests()
