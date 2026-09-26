/**
 * Authority Command Center (Admin Dashboard) Logic
 * Features:
 * - Interactive Leaflet Map for geofencing & real-time citizen pins
 * - Multilingual Template Composer with instant 7-language preview
 * - Real-time Delivery & Acknowledgment Tracking Funnel
 * - Manual Overrides (Immediate IVR, Force SMS, Dispatch Warden)
 */

const AdminApp = {
  map: null,
  centerMarker: null,
  radiusCircle: null,
  citizenMarkers: [],
  selectedLat: 19.8135,
  selectedLng: 85.8312,
  selectedRadius: 35,
  allCitizens: [],
  activeAlertId: null,
  pollTimer: null,
  currentPreviewLang: "or",
  previewsCache: {},

  init() {
    this.initMap();
    this.bindEvents();
    this.loadDistricts();
    this.loadCitizens();
    this.refreshTemplatePreview();
    this.loadAlertsList();
    this.startTrackingPoll();
  },

  initMap() {
    // Leaflet map centered on coastal Odisha
    if (typeof L === "undefined") {
      console.warn("Leaflet library not loaded");
      return;
    }

    this.map = L.map("alertMap").setView([this.selectedLat, this.selectedLng], 9);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "© OpenStreetMap contributors"
    }).addTo(this.map);

    // Initial Center Marker & Radius
    this.updateMapCircle(this.selectedLat, this.selectedLng, this.selectedRadius);

    // Click to move epicenter
    this.map.on("click", (e) => {
      this.selectedLat = e.latlng.lat;
      this.selectedLng = e.latlng.lng;
      document.getElementById("centerLatInput").value = this.selectedLat.toFixed(4);
      document.getElementById("centerLngInput").value = this.selectedLng.toFixed(4);
      this.updateMapCircle(this.selectedLat, this.selectedLng, this.selectedRadius);
      this.updateTargetAudienceCount();
    });
  },

  updateMapCircle(lat, lng, radiusKm, color = "#ef4444") {
    if (!this.map) return;
    if (this.centerMarker) this.map.removeLayer(this.centerMarker);
    if (this.radiusCircle) this.map.removeLayer(this.radiusCircle);

    this.centerMarker = L.marker([lat, lng], { draggable: true }).addTo(this.map);
    this.centerMarker.bindPopup("<b>Epicenter / Alert Core</b>").openPopup();

    this.centerMarker.on("dragend", (e) => {
      const pos = e.target.getLatLng();
      this.selectedLat = pos.lat;
      this.selectedLng = pos.lng;
      document.getElementById("centerLatInput").value = this.selectedLat.toFixed(4);
      document.getElementById("centerLngInput").value = this.selectedLng.toFixed(4);
      this.updateMapCircle(pos.lat, pos.lng, this.selectedRadius);
      this.updateTargetAudienceCount();
    });

    this.radiusCircle = L.circle([lat, lng], {
      color: color,
      fillColor: color,
      fillOpacity: 0.25,
      radius: radiusKm * 1000
    }).addTo(this.map);
  },

  bindEvents() {
    // Hazard & Severity selectors change preview
    ["hazardTypeSelect", "severitySelect", "areaNameInput"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener("change", () => this.refreshTemplatePreview());
        el.addEventListener("input", () => this.refreshTemplatePreview());
      }
    });

    // Radius slider
    const radiusInput = document.getElementById("radiusKmInput");
    if (radiusInput) {
      radiusInput.addEventListener("input", (e) => {
        this.selectedRadius = parseFloat(e.target.value);
        document.getElementById("radiusValueDisplay").textContent = `${this.selectedRadius} km`;
        this.updateMapCircle(this.selectedLat, this.selectedLng, this.selectedRadius);
        this.updateTargetAudienceCount();
      });
    }

    // District Quick Select
    const districtSelect = document.getElementById("quickDistrictSelect");
    if (districtSelect) {
      districtSelect.addEventListener("change", (e) => {
        this.onDistrictSelect(e.target.value);
      });
    }

    // Form Submit
    const form = document.getElementById("composeAlertForm");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.submitAlert();
      });
    }

    // Language Preview Tabs
    document.querySelectorAll(".lang-tab").forEach((tab) => {
      tab.addEventListener("click", (e) => {
        document.querySelectorAll(".lang-tab").forEach((t) => t.classList.remove("active"));
        e.target.classList.add("active");
        this.currentPreviewLang = e.target.dataset.lang;
        this.displayPreview(this.currentPreviewLang);
      });
    });

    // Active alert selector for tracking
    const alertTrackSelect = document.getElementById("activeAlertSelect");
    if (alertTrackSelect) {
      alertTrackSelect.addEventListener("change", (e) => {
        this.activeAlertId = e.target.value;
        this.fetchTrackingData();
      });
    }
  },

  async loadDistricts() {
    try {
      const res = await fetch("/api/districts");
      const districts = await res.json();
      const sel = document.getElementById("quickDistrictSelect");
      if (!sel) return;
      sel.innerHTML = '<option value="">-- Quick Pick Coastal District --</option>';
      for (const [name, d] of Object.entries(districts)) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = `${name} (${d.risk})`;
        sel.appendChild(opt);
      }
    } catch (e) {
      console.error("Error loading districts:", e);
    }
  },

  async onDistrictSelect(districtName) {
    if (!districtName) return;
    try {
      const res = await fetch("/api/districts");
      const districts = await res.json();
      const d = districts[districtName];
      if (d) {
        this.selectedLat = d.lat;
        this.selectedLng = d.lng;
        this.selectedRadius = d.radius_km;

        document.getElementById("centerLatInput").value = d.lat;
        document.getElementById("centerLngInput").value = d.lng;
        document.getElementById("radiusKmInput").value = d.radius_km;
        document.getElementById("radiusValueDisplay").textContent = `${d.radius_km} km`;
        document.getElementById("areaNameInput").value = `${districtName} Coastal Sector`;

        if (this.map) {
          this.map.setView([d.lat, d.lng], 10);
        }
        this.updateMapCircle(d.lat, d.lng, d.radius_km);
        this.updateTargetAudienceCount();
        this.refreshTemplatePreview();
      }
    } catch (e) {}
  },

  async loadCitizens() {
    try {
      const res = await fetch("/api/citizens");
      this.allCitizens = await res.json();
      this.renderCitizenMarkers();
      this.updateTargetAudienceCount();
    } catch (e) {
      console.error("Error loading citizens:", e);
    }
  },

  renderCitizenMarkers() {
    if (!this.map) return;
    // Clear old citizen pins
    this.citizenMarkers.forEach((m) => this.map.removeLayer(m));
    this.citizenMarkers = [];

    this.allCitizens.forEach((c) => {
      const pin = L.circleMarker([c.lat, c.lng], {
        radius: 6,
        fillColor: "#3b82f6",
        color: "#fff",
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.85
      }).addTo(this.map);

      pin.bindPopup(`
        <strong>${c.name}</strong> (${c.language.toUpperCase()})<br/>
        ${c.block_village}, ${c.district}<br/>
        Phone: ${c.phone}<br/>
        Device: ${c.device_type}
      `);
      this.citizenMarkers.push(pin);
    });
  },

  updateTargetAudienceCount() {
    if (!this.allCitizens.length) return;
    let count = 0;
    this.allCitizens.forEach((c) => {
      const dist = this.haversine(this.selectedLat, this.selectedLng, c.lat, c.lng);
      if (dist <= this.selectedRadius) {
        count++;
      }
    });

    const display = document.getElementById("targetAudienceCount");
    if (display) {
      display.textContent = `${count} Citizens`;
    }
  },

  haversine(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  },

  async refreshTemplatePreview() {
    const hazardType = document.getElementById("hazardTypeSelect").value;
    const severity = document.getElementById("severitySelect").value;
    const areaName = document.getElementById("areaNameInput").value || "Disaster Zone";

    try {
      const res = await fetch("/api/template/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hazard_type: hazardType, severity, area_name: areaName })
      });
      const data = await res.json();
      this.previewsCache = data.previews || {};
      this.displayPreview(this.currentPreviewLang);
    } catch (e) {
      console.error("Preview fetch error:", e);
    }
  },

  displayPreview(lang) {
    const p = this.previewsCache[lang];
    if (!p) return;

    document.getElementById("previewHeadline").textContent = p.headline;
    document.getElementById("previewAction").textContent = p.recommended_action;
    document.getElementById("previewHelplines").textContent = p.helplines;
    document.getElementById("previewSms").textContent = p.short_sms;
    
    const charCounter = document.getElementById("previewSmsCharCount");
    if (charCounter) {
      charCounter.textContent = `${p.sms_length} / 160 characters (GSM/Unicode compliant)`;
      charCounter.className = p.sms_length <= 160 ? "sms-char-counter" : "sms-char-counter warning";
    }
  },

  async submitAlert() {
    const hazardType = document.getElementById("hazardTypeSelect").value;
    const severity = document.getElementById("severitySelect").value;
    const areaName = document.getElementById("areaNameInput").value || "Designated Coastal Sector";
    const ackTimeout = parseInt(document.getElementById("ackTimeoutInput").value || 30);
    const helplines = document.getElementById("helplineInput").value || "112, 1070";

    const payload = {
      hazard_type: hazardType,
      severity: severity,
      area_name: areaName,
      center_lat: this.selectedLat,
      center_lng: this.selectedLng,
      radius_km: this.selectedRadius,
      ack_timeout_seconds: ackTimeout,
      helplines: helplines,
      max_retries: 3
    };

    if (!confirm(`Issue ${severity.toUpperCase()} Alert for ${areaName} across Push, SMS, and IVR?`)) {
      return;
    }

    try {
      const res = await fetch("/api/alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        alert(`Emergency Alert ${data.alert_id} broadcasted! Targeted ${data.dispatch.targeted_citizens} citizens.`);
        this.activeAlertId = data.alert_id;
        await this.loadAlertsList();
        this.fetchTrackingData();
        
        // Refresh Citizen App view too
        if (window.CitizenApp) {
          window.CitizenApp.loadCitizenView();
        }
      }
    } catch (e) {
      console.error("Alert submission error:", e);
      alert("Failed to submit alert.");
    }
  },

  async loadAlertsList() {
    try {
      const res = await fetch("/api/alerts");
      const alerts = await res.json();
      const sel = document.getElementById("activeAlertSelect");
      if (!sel) return;
      sel.innerHTML = "";

      alerts.forEach((a) => {
        const opt = document.createElement("option");
        opt.value = a.id;
        opt.textContent = `${a.id} - ${a.hazard_type} (${a.severity}) in ${a.area_name}`;
        sel.appendChild(opt);
      });

      if (alerts.length > 0 && !this.activeAlertId) {
        this.activeAlertId = alerts[0].id;
      }
      if (this.activeAlertId) {
        sel.value = this.activeAlertId;
        this.fetchTrackingData();
      }
    } catch (e) {
      console.error("Error loading alerts:", e);
    }
  },

  async fetchTrackingData() {
    if (!this.activeAlertId) return;

    try {
      const res = await fetch(`/api/alerts/${this.activeAlertId}/tracking`);
      if (res.status === 404) return;
      const data = await res.json();
      this.renderTrackingDashboard(data);
    } catch (e) {
      console.error("Tracking error:", e);
    }
  },

  renderTrackingDashboard(data) {
    const s = data.summary;
    document.getElementById("kpiTotalTargeted").textContent = s.total_targeted;
    document.getElementById("kpiAcknowledged").textContent = `${s.acknowledged} (${s.ack_percentage}%)`;
    document.getElementById("kpiSafe").textContent = s.safe_count;
    document.getElementById("kpiRescue").textContent = s.rescue_count;
    document.getElementById("kpiEscalated").textContent = s.escalated;

    // Channel breakdown
    document.getElementById("countPush").textContent = s.channels.PUSH || 0;
    document.getElementById("countSms").textContent = s.channels.SMS || 0;
    document.getElementById("countIvr").textContent = s.channels.IVR || 0;
    document.getElementById("countWarden").textContent = s.channels.WARDEN || 0;

    // Per-citizen table
    const tbody = document.getElementById("trackingTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.delivery_logs.forEach((log) => {
      const tr = document.createElement("tr");

      let statusBadge = "";
      if (log.status === "ACKNOWLEDGED") {
        const ackType = log.ack_response === "RESCUE" ? "badge-rescue" : "badge-safe";
        statusBadge = `<span class="badge ${ackType}">✓ Safe (${log.ack_response})</span>`;
      } else if (log.status === "ESCALATED") {
        statusBadge = `<span class="badge badge-extreme">⚠️ WARDEN DISPATCHED</span>`;
      } else if (log.status === "DELIVERED") {
        statusBadge = `<span class="badge badge-warning">Delivered / Awaiting Ack</span>`;
      } else {
        statusBadge = `<span class="badge badge-push">${log.status}</span>`;
      }

      let channelBadge = `<span class="badge badge-push">${log.channel}</span>`;
      if (log.channel === "SMS") channelBadge = `<span class="badge badge-sms">SMS</span>`;
      if (log.channel === "IVR") channelBadge = `<span class="badge badge-ivr">IVR Voice</span>`;
      if (log.channel === "WARDEN") channelBadge = `<span class="badge badge-warden">Warden</span>`;

      tr.innerHTML = `
        <td><strong>${log.name}</strong><br/><small class="text-muted">${log.phone} (${log.language.toUpperCase()})</small></td>
        <td>${log.block_village}, ${log.district}</td>
        <td>${channelBadge}</td>
        <td>${statusBadge}</td>
        <td>${log.retry_count} retries</td>
        <td>
          <div style="display:flex; gap: 0.3rem;">
            ${log.status !== "ACKNOWLEDGED" ? `
              <button class="btn btn-sm btn-warning" onclick="AdminApp.manualOverride('${log.citizen_id}', 'ESCALATE_CHANNEL', 'IVR')">📞 IVR</button>
              <button class="btn btn-sm btn-danger" onclick="AdminApp.manualOverride('${log.citizen_id}', 'DISPATCH_WARDEN')">🚨 Warden</button>
              <button class="btn btn-sm btn-success" onclick="AdminApp.manualOverride('${log.citizen_id}', 'MARK_SAFE')">✓ Safe</button>
            ` : `<span style="color:#10b981; font-weight:600; font-size:0.8rem;">Ack Recorded</span>`}
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Update Map Pins with live status colors
    this.updateLiveMapPins(data.delivery_logs);
  },

  updateLiveMapPins(logs) {
    if (!this.map) return;
    this.citizenMarkers.forEach((m) => this.map.removeLayer(m));
    this.citizenMarkers = [];

    logs.forEach((l) => {
      let pinColor = "#60a5fa"; // default push
      if (l.status === "ACKNOWLEDGED") {
        pinColor = l.ack_response === "RESCUE" ? "#ef4444" : "#34d399";
      } else if (l.status === "ESCALATED") {
        pinColor = "#dc2626";
      } else if (l.channel === "SMS") {
        pinColor = "#c084fc";
      } else if (l.channel === "IVR") {
        pinColor = "#fcd34d";
      }

      const marker = L.circleMarker([l.lat, l.lng], {
        radius: l.status === "ESCALATED" ? 9 : 7,
        fillColor: pinColor,
        color: "#ffffff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(this.map);

      marker.bindPopup(`
        <strong>${l.name}</strong> (${l.phone})<br/>
        Village: ${l.block_village}<br/>
        Channel: <b>${l.channel}</b><br/>
        Status: <b>${l.status}</b> (${l.ack_response})<br/>
        Warden: ${l.warden_name || "Assigned Local Warden"}
      `);

      this.citizenMarkers.push(marker);
    });
  },

  async manualOverride(citizenId, action, channel = "IVR") {
    if (!this.activeAlertId) return;
    try {
      const res = await fetch(`/api/alerts/${this.activeAlertId}/manual-override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: action,
          citizen_id: parseInt(citizenId),
          channel: channel
        })
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        this.fetchTrackingData();
      }
    } catch (e) {
      console.error("Override error:", e);
    }
  },

  startTrackingPoll() {
    this.pollTimer = setInterval(() => {
      this.fetchTrackingData();
    }, 2500);
  }
};

window.AdminApp = AdminApp;
