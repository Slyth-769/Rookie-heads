# 🚨 Rookies • Disaster Management Alert System
### Mobile-First Emergency Alert, Multilingual Delivery, Kin Auto-Dial & SOS Rescue Hub
*Compliant with National & State Disaster Management Guidelines (NDMA / OSDMA / IMD)*

---

## 📌 Executive Summary
**Rookies** is a life-critical, mobile-first disaster alert and emergency tracking application designed to broadcast emergency notifications to citizens during severe hazards (Cyclones, Floods, Earthquakes, Heatwaves, Landslides, Tsunamis).

It features:
1. **Automated Multi-Channel Escalation Loop**:
   $$\text{PUSH Notification} \xrightarrow{\text{30s}} \text{SMS Alert} \xrightarrow{\text{30s}} \text{Automated IVR Voice Call} \xrightarrow{\text{30s}} \text{EMERGENCY KIN CALL} + \text{WARDEN DISPATCH}$$
2. **Automated 30-Second Emergency Kin Call**: If a citizen in danger does not acknowledge the alert within 30 seconds, an automated voice call & SMS is dispatched immediately to their saved contact (`secondary_name`, `secondary_phone`) informing them that their loved one is in active danger and unresponsive.
3. **Dedicated SOS & Unresponsive Citizens Hub**: A real-time command deck tracking:
   - Citizens unresponsive beyond the 30-second timeline with interactive Kin call voice playback.
   - Citizens requesting immediate evacuation rescue (`RESCUE` / `SOS`).
4. **"Under No-Network Area" Offline Toolkit**:
   - High-Frequency Acoustic Rescue Whistle ($3.1\,\text{kHz}$).
   - High-Intensity Strobe Flashlight (Morse code SOS: $\cdot\cdot\cdot ---\cdot\cdot\cdot$).
   - Offline GPS Coordinate Lock with precision telemetry.
   - 2G Cellular SMS fallback (`sms:112?body=SAFE`) & USSD signaling (`*112*1#`).
   - Service Worker offline PWA with local acknowledgment queuing.
5. **Pre-Verified Deterministic Translations**: Fixed fields translated without semantic distortion across **7 languages** (Odia, Hindi, English, Bengali, Telugu, Tamil, Urdu) with SMS lengths strictly $\le 160$ characters.
6. **Modern Green & Cool Blue Aesthetic**: Clean tactical palette featuring Deep Spruce/Pine Green (`#10261f`, `#3e7d60`, `#c7e1d5`) with Electric & Ice Blue highlights (`#0284c7`, `#38bdf8`, `#eef8fe`).

---

## 🌟 Architecture & Application Layout

```
disaster-alert-system/
├── app.py                     # Main Flask REST server & Real-time Distress APIs
├── requirements.txt           # Python dependencies (Flask>=2.2.0)
├── run.bat                    # Windows startup batch file
├── test_system.py             # Automated test suite
├── disaster_alert.db          # SQLite database (Citizens, Wardens, Alerts, Logs, Telecom)
├── README.md                  # Comprehensive technical documentation & user manual
├── engine/
│   ├── templates.py           # Pre-verified 7-language hazard dictionaries & SMS 160-char format
│   ├── delivery_engine.py     # Multi-channel escalation loop & 30s Kin auto-dialer daemon
│   ├── geo.py                 # Haversine distance, circle containment & polygon ray-casting
│   └── database.py            # SQLite schema, tables & realistic coastal seed dataset
└── static/
    ├── index.html             # Unified Single-Page Application (Citizen, Admin, SOS, Telecom, Directory)
    ├── sw.js                  # Service Worker for offline PWA caching & background sync
    ├── css/
    │   └── style.css          # Green Majority + Cool Blue UI, mobile frame & animations
    └── js/
        ├── citizen.js         # Mobile app client, Web Audio siren, whistle, strobe & offline queue
        ├── admin.js           # Authority dashboard, Leaflet mapping & delivery tracking funnel
        ├── distress.js        # SOS & Unresponsive Hub, Kin voice playback & warden dispatcher
        └── simulator.js       # SMS/USSD/IVR voice synthesizer & gateway console
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Available via Anaconda or system Python)
- Web Browser (Chrome, Edge, Firefox, Brave)

### Installation & Launch
1. Unzip the project archive.
2. Open a terminal in the project directory:
```bash
pip install -r requirements.txt
python app.py
```
*(Or double-click `run.bat` on Windows)*

3. Open your browser and navigate to:
👉 **`http://127.0.0.1:5050`**

---

## 🧭 Key Tabs & Working Guide

### 1. 📱 Citizen Mobile App
- Realistic mobile viewport simulator with live profile switcher.
- **Multilingual Alert Banner**: Displays hazard, severity, affected area, and recommended action in citizen's chosen language.
- **Immediate Response Actions**:
  - `✓ I AM SAFE`: Confirms citizen well-being.
  - `🆘 NEED RESCUE`: Requests immediate physical rescue.
- **Under No-Network Area Toolkit**:
  - 🔊 **Acoustic Rescue Whistle**: Plays piercing continuous audio tone to guide search and rescue teams.
  - 💡 **SOS Night Strobe**: Flashes high-contrast Morse code screen signal for nighttime visibility.
  - 📍 **Offline GPS Lock**: Captures device coordinates without requiring map tile data.
  - 📱 **2G SMS / USSD Fallback**: Direct cellular links when 4G/5G data is disabled.
  - ✈️ **Cut Internet Simulation**: Queues responses in local storage and auto-syncs when online.

### 2. 🛡️ Authority Command Center
- **Hazard Dispatch Form**: Select Hazard, Severity, Radius/Polygon, Affected District, and Action.
- **Interactive Leaflet Geospatial Map**: Visualizes blast radius, citizen markers, and real-time statuses.
- **7-Language Instant Preview**: Verifies exact wording and character counts ($\le 160$ chars).
- **Delivery Tracking Funnel**: Sent $\to$ Delivered $\to$ Read $\to$ Acknowledged.

### 3. 🆘 SOS & Unresponsive Citizens Hub
- **Unresponsive Citizens Deck (>30s Timeline)**:
  - Displays all citizens who have not acknowledged alerts within 30 seconds.
  - Automatically dispatches an automated voice call to their saved emergency contact (`secondary_name`).
  - **🔊 Listen / Simulate Kin Voice Call**: Plays the automated call spoken aloud in browser using Web Speech Synthesis.
  - **🚨 Dispatch Warden**: Instantly deploys local field warden to the citizen's GPS coordinates.
- **Active SOS Rescue Requests Deck**:
  - Highlights citizens in extreme distress who selected `NEED RESCUE`.
  - Displays live coordinates and block/village details for NDRF dispatch.

### 4. 📡 Telecom & Gateway Simulator
- Test inbound SMS reply codes (`1` = Safe, `2` = Rescue).
- Test 2G USSD cellular codes (`*112*1#`).
- Test interactive IVR voice phone calls with DTMF keypad simulation.

### 5. 👥 Citizen Directory
- Search, filter, and register new citizens with device types, preferred languages, and next-of-kin emergency contacts.

---

## 🛡️ Standards Compliance
- **NDMA / OSDMA / IMD Guidelines**: CAP-compliant categories and hazard urgency levels.
- **Telecom Regulatory Standards**: SMS payload strictly conforms to the standard 160 GSM 7-bit character envelope to prevent multi-part message fragmentation.
- **Deterministic Translations**: Human-verified native phrasing for safety-critical instructions.
