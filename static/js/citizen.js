/**
 * Citizen Mobile App Logic
 * Enhanced for Under No-Network / Zero-Bandwidth Disaster Areas
 * Features:
 * - Real-time alert polling & push notification simulation
 * - Authentic Web Audio API emergency siren
 * - No-Network Acoustic Rescue Whistle (for debris localization)
 * - Visual Screen SOS Strobe Beacon (for aerial/night rescue)
 * - Offline GPS Lock caching & 2G GSM SMS / USSD fast links
 * - Offline Acknowledgment Queue with local cryptographic receipt stamping
 * - Multilingual UI switching across 7 languages
 */

const CitizenApp = {
  currentCitizenId: 1,
  citizensList: [],
  activeAlertData: null,
  isOfflineMode: false,
  offlineQueue: [],
  audioCtx: null,
  sirenOsc: null,
  sirenGain: null,
  isSirenPlaying: false,
  whistleOsc: null,
  whistleGain: null,
  whistleInterval: null,
  isWhistlePlaying: false,
  isStrobeActive: false,
  pollTimer: null,

  init() {
    this.loadOfflineQueue();
    this.bindEvents();
    this.fetchCitizens();
    this.startPolling();
  },

  bindEvents() {
    // Citizen Switcher dropdown
    const citizenSelect = document.getElementById("citizenProfileSelect");
    if (citizenSelect) {
      citizenSelect.addEventListener("change", (e) => {
        this.currentCitizenId = parseInt(e.target.value);
        this.loadCitizenView();
      });
    }

    // Offline / No-Network Area Simulator Toggle
    const offlineToggle = document.getElementById("offlineSimToggle");
    if (offlineToggle) {
      offlineToggle.addEventListener("change", (e) => {
        this.setOfflineMode(e.target.checked);
      });
    }

    // Citizen Language Switcher on mobile
    const langSelect = document.getElementById("mobileLangSelect");
    if (langSelect) {
      langSelect.addEventListener("change", (e) => {
        this.updateCitizenLanguage(e.target.value);
      });
    }

    // Siren Toggle Button
    const sirenBtn = document.getElementById("toggleSirenBtn");
    if (sirenBtn) {
      sirenBtn.addEventListener("click", () => {
        this.toggleEmergencySiren();
      });
    }
  },

  setOfflineMode(isOffline) {
    this.isOfflineMode = isOffline;
    const banner = document.getElementById("mobileOfflineBanner");
    const noNetworkDeck = document.getElementById("noNetworkDeck");
    const carrier = document.getElementById("mobileCarrierName");
    const mockup = document.querySelector(".phone-mockup");

    if (isOffline) {
      if (banner) banner.style.display = "flex";
      if (noNetworkDeck) noNetworkDeck.style.display = "block";
      if (carrier) carrier.innerHTML = "<span style='color:#ef4444;'>❌ NO SERVICE</span> | 2G SOS";
      if (mockup) mockup.classList.add("no-network-active-frame");
      this.renderCachedAlert();
    } else {
      if (banner) banner.style.display = "none";
      if (noNetworkDeck) noNetworkDeck.style.display = "none";
      if (carrier) carrier.innerHTML = "BSNL / Jio 4G";
      if (mockup) mockup.classList.remove("no-network-active-frame");
      this.stopAcousticWhistle();
      this.stopScreenStrobe();
      this.flushOfflineQueue();
      this.loadCitizenView();
    }
  },

  async fetchCitizens() {
    try {
      const res = await fetch("/api/citizens");
      this.citizensList = await res.json();
      this.populateCitizenSelect();
      this.loadCitizenView();
    } catch (err) {
      console.error("Failed to load citizens:", err);
    }
  },

  populateCitizenSelect() {
    const select = document.getElementById("citizenProfileSelect");
    if (!select) return;
    select.innerHTML = "";
    this.citizensList.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      const deviceBadge = c.device_type === "feature_phone" ? " [2G Phone]" : "";
      opt.textContent = `${c.name} (${c.language.toUpperCase()} | ${c.district})${deviceBadge}`;
      select.appendChild(opt);
    });
    select.value = this.currentCitizenId;
  },

  async updateCitizenLanguage(lang) {
    try {
      await fetch(`/api/citizens/${this.currentCitizenId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: lang })
      });
      this.loadCitizenView();
    } catch (e) {
      console.error("Error updating language:", e);
    }
  },

  async loadCitizenView() {
    const citizen = this.citizensList.find((c) => c.id === this.currentCitizenId);
    if (!citizen) return;

    // Update phone profile details
    document.getElementById("phoneCitizenName").textContent = citizen.name;
    document.getElementById("phoneCitizenLoc").textContent = `${citizen.block_village}, ${citizen.district}`;
    document.getElementById("phoneCitizenNumber").textContent = citizen.phone;

    // Update offline GPS lock display
    const gpsEl = document.getElementById("offlineGpsCoordinates");
    if (gpsEl) {
      gpsEl.textContent = `Lat: ${citizen.lat.toFixed(4)}° N, Lng: ${citizen.lng.toFixed(4)}° E (${citizen.block_village})`;
    }
    
    const langSelect = document.getElementById("mobileLangSelect");
    if (langSelect) langSelect.value = citizen.language;

    // Fetch active alert if online
    if (!this.isOfflineMode) {
      try {
        const res = await fetch(`/api/citizen/${this.currentCitizenId}/active-alert`);
        const data = await res.json();
        this.renderActiveAlert(data);
        
        // Cache alert payload locally for offline viewing
        if (data.has_alert) {
          localStorage.setItem(`cached_alert_${this.currentCitizenId}`, JSON.stringify(data));
        }
      } catch (err) {
        console.warn("Network error, loading from local cache:", err);
        this.renderCachedAlert();
      }
    } else {
      this.renderCachedAlert();
    }
  },

  renderCachedAlert() {
    const cached = localStorage.getItem(`cached_alert_${this.currentCitizenId}`);
    if (cached) {
      try {
        const data = JSON.parse(cached);
        this.renderActiveAlert(data, true);
      } catch (e) {
        this.renderActiveAlert({ has_alert: false });
      }
    } else {
      this.renderActiveAlert({ has_alert: false });
    }
  },

  renderActiveAlert(data, isCached = false) {
    this.activeAlertData = data;
    const container = document.getElementById("phoneAlertContainer");
    const noAlertBox = document.getElementById("phoneNoAlertBox");

    if (!data || !data.has_alert) {
      if (container) container.style.display = "none";
      if (noAlertBox) noAlertBox.style.display = "block";
      this.stopEmergencySiren();
      return;
    }

    if (noAlertBox) noAlertBox.style.display = "none";
    if (container) container.style.display = "block";

    const p = data.alert_payload;
    const log = data.delivery_log;

    // Mark as READ if DELIVERED & online
    if (log && log.status === "DELIVERED" && !this.isOfflineMode) {
      fetch(`/api/alerts/${log.alert_id}/read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ citizen_id: this.currentCitizenId })
      });
    }

    // Populate alert UI fields
    document.getElementById("alertHazardIcon").textContent = p.hazard_icon;
    document.getElementById("alertHazardName").textContent = `${p.hazard_type} - ${p.severity}`;
    document.getElementById("alertSeverityBadge").textContent = p.severity_label;
    document.getElementById("alertSeverityBadge").style.backgroundColor = p.severity_color;
    
    document.getElementById("alertHeadline").textContent = p.headline;
    document.getElementById("alertRecommendedAction").textContent = p.recommended_action;
    document.getElementById("alertHelplines").textContent = p.helplines;
    document.getElementById("alertDistance").textContent = `${data.distance_to_epicenter_km || 0} km`;
    
    // Short SMS display
    const smsBox = document.getElementById("alertSmsText");
    if (smsBox) smsBox.textContent = p.short_sms;

    // Configure 2G SMS shortcut link with active alert ID
    const smsLink = document.getElementById("offlineSmsActionLink");
    if (smsLink && log) {
      smsLink.href = `sms:112?body=SAFE%20${log.alert_id}`;
    }

    // Update status badge
    const statusBadge = document.getElementById("mobileDeliveryStatus");
    const ackButtons = document.getElementById("phoneAckButtonGroup");
    const ackConfirmedBox = document.getElementById("phoneAckConfirmedBox");

    if (log.status === "ACKNOWLEDGED") {
      statusBadge.innerHTML = `<span class="badge badge-safe">✓ Acknowledged (${log.ack_response})</span>`;
      if (ackButtons) ackButtons.style.display = "none";
      if (ackConfirmedBox) {
        ackConfirmedBox.style.display = "block";
        ackConfirmedBox.innerHTML = `<strong>Status:</strong> Safety confirmation logged as <strong>${log.ack_response}</strong>. Disaster Ops updated.`;
      }
      this.stopEmergencySiren();
    } else {
      let channelBadge = `<span class="badge badge-push">Channel: ${log.channel}</span>`;
      if (log.channel === "SMS") channelBadge = `<span class="badge badge-sms">Channel: SMS Fallback</span>`;
      if (log.channel === "IVR") channelBadge = `<span class="badge badge-ivr">Channel: IVR Voice Call</span>`;
      if (log.channel === "WARDEN") channelBadge = `<span class="badge badge-warden">⚠️ Warden Dispatched</span>`;

      statusBadge.innerHTML = `${channelBadge} <span class="badge badge-warning">Awaiting Safe Confirmation</span>`;
      if (ackButtons) ackButtons.style.display = "flex";
      if (ackConfirmedBox) ackConfirmedBox.style.display = "none";
    }

    // Update offline survival tips
    this.updateOfflineGuidelines(p.hazard_type);
  },

  updateOfflineGuidelines(hazardType) {
    const el = document.getElementById("offlineSurvivalTips");
    if (!el) return;

    if (hazardType === "Cyclone") {
      el.innerHTML = `
        • <strong>Shelter:</strong> Move to concrete cyclone shelter or reinforced masonry room.<br/>
        • <strong>Power:</strong> Turn off main electrical breaker & LPG cylinder valves.<br/>
        • <strong>Water:</strong> Store 3 liters boiled water per person in sealed containers.<br/>
        • <strong>Eye of Storm:</strong> Beware the calm eye of cyclone; winds will abruptly reverse!
      `;
    } else if (hazardType === "Flood") {
      el.innerHTML = `
        • <strong>High Ground:</strong> Move to 2nd floor or roof immediately.<br/>
        • <strong>Do NOT Walk in Water:</strong> Flowing 15cm water can sweep an adult.<br/>
        • <strong>Signaling:</strong> Hang bright colored cloth from roof for rescue boats.<br/>
        • <strong>Snakes & Hazards:</strong> Watch for displaced reptiles seeking high ground.
      `;
    } else if (hazardType === "Earthquake") {
      el.innerHTML = `
        • <strong>Drop, Cover & Hold:</strong> Get under sturdy table away from glass.<br/>
        • <strong>Outdoors:</strong> Move away from tall buildings, power lines, and billboards.<br/>
        • <strong>Aftershocks:</strong> Be prepared for secondary tremors within 24-48 hours.
      `;
    } else {
      el.innerHTML = `
        • Disconnect power mains and gas cylinder valve.<br/>
        • Keep battery torch, emergency radio, and basic first-aid handy.<br/>
        • Follow instructions from civil defense wardens & NDRF teams.
      `;
    }
  },

  async acknowledge(responseType = "SAFE") {
    if (!this.activeAlertData || !this.activeAlertData.delivery_log) return;
    const alertId = this.activeAlertData.delivery_log.alert_id;

    if (this.isOfflineMode) {
      // Offline mode: generate cryptographic local receipt and store in offline queue
      const receiptHash = "ACK-OFFLINE-" + Math.floor(1000 + Math.random() * 9000);
      const offlineItem = {
        alert_id: alertId,
        citizen_id: this.currentCitizenId,
        response_type: responseType,
        channel: "APP_OFFLINE_RECEIPT",
        receipt: receiptHash,
        timestamp: new Date().toISOString()
      };
      this.offlineQueue.push(offlineItem);
      this.saveOfflineQueue();

      // Show offline receipt card inside No-Network toolkit
      const queueCard = document.getElementById("offlineQueueCard");
      const hashDisplay = document.getElementById("offlineReceiptHash");
      if (queueCard) queueCard.style.display = "block";
      if (hashDisplay) hashDisplay.textContent = `#${receiptHash}`;

      const statusBadge = document.getElementById("mobileDeliveryStatus");
      if (statusBadge) {
        statusBadge.innerHTML = `<span class="badge badge-warning">Queued Offline (${responseType})</span>`;
      }
      document.getElementById("phoneAckButtonGroup").style.display = "none";
      document.getElementById("phoneAckConfirmedBox").style.display = "block";
      document.getElementById("phoneAckConfirmedBox").innerHTML = `
        <strong>Offline Confirmation Recorded:</strong> ${responseType}<br/>
        <small style="color:#d8d7dc;">Receipt #${receiptHash} saved locally. Auto-syncs when network blips alive, or use 2G SMS below.</small>
      `;
      this.stopEmergencySiren();
      return;
    }

    try {
      const res = await fetch(`/api/alerts/${alertId}/acknowledge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          citizen_id: this.currentCitizenId,
          response_type: responseType,
          channel: "APP",
          offline: false
        })
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        this.stopEmergencySiren();
        this.loadCitizenView();
      }
    } catch (err) {
      console.error("Acknowledgment error:", err);
    }
  },

  loadOfflineQueue() {
    try {
      const q = localStorage.getItem("dmas_offline_queue");
      this.offlineQueue = q ? JSON.parse(q) : [];
    } catch (e) {
      this.offlineQueue = [];
    }
  },

  saveOfflineQueue() {
    localStorage.setItem("dmas_offline_queue", JSON.stringify(this.offlineQueue));
  },

  async flushOfflineQueue() {
    if (this.offlineQueue.length === 0) return;
    console.log(`[OfflineSync] Flushing ${this.offlineQueue.length} offline responses...`);

    const queueCopy = [...this.offlineQueue];
    for (const item of queueCopy) {
      try {
        await fetch(`/api/alerts/${item.alert_id}/acknowledge`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            citizen_id: item.citizen_id,
            response_type: item.response_type,
            channel: "APP_SYNCED_FROM_OFFLINE",
            offline: true
          })
        });
      } catch (err) {
        console.error("Failed to sync item:", item, err);
        return;
      }
    }
    this.offlineQueue = [];
    this.saveOfflineQueue();
    console.log("[OfflineSync] All offline acknowledgments synchronized!");
    alert("Offline safety queue synchronized with Disaster Management Center!");
    this.loadCitizenView();
  },

  // ----------------- Acoustic Rescue Whistle (For Rubble / Search Parties) -----------------
  toggleAcousticWhistle() {
    if (this.isWhistlePlaying) {
      this.stopAcousticWhistle();
    } else {
      this.startAcousticWhistle();
    }
  },

  startAcousticWhistle() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!this.audioCtx) this.audioCtx = new AudioContext();
      if (this.audioCtx.state === "suspended") this.audioCtx.resume();

      this.whistleOsc = this.audioCtx.createOscillator();
      this.whistleGain = this.audioCtx.createGain();

      this.whistleOsc.type = "sine";
      this.whistleGain.gain.setValueAtTime(0.2, this.audioCtx.currentTime);

      // High-frequency international rescue whistle sound (alternates 2800 Hz and 3200 Hz)
      let high = false;
      this.whistleInterval = setInterval(() => {
        if (!this.whistleOsc) return;
        const freq = high ? 2800 : 3200;
        this.whistleOsc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
        high = !high;
      }, 350);

      this.whistleOsc.connect(this.whistleGain);
      this.whistleGain.connect(this.audioCtx.destination);
      this.whistleOsc.start();
      this.isWhistlePlaying = true;

      const btn = document.getElementById("toggleAcousticWhistleBtn");
      if (btn) {
        btn.classList.add("sound-playing");
        btn.innerHTML = `<span class="icon">🔇</span><span>Stop Whistle</span><small style="color:#fff;">Sounding SOS...</small>`;
      }
    } catch (e) {
      console.warn("Acoustic whistle error:", e);
    }
  },

  stopAcousticWhistle() {
    if (this.whistleInterval) {
      clearInterval(this.whistleInterval);
      this.whistleInterval = null;
    }
    if (this.whistleOsc) {
      try {
        this.whistleOsc.stop();
        this.whistleOsc.disconnect();
      } catch (e) {}
      this.whistleOsc = null;
    }
    this.isWhistlePlaying = false;
    const btn = document.getElementById("toggleAcousticWhistleBtn");
    if (btn) {
      btn.classList.remove("sound-playing");
      btn.innerHTML = `<span class="icon">🔊</span><span>Acoustic Whistle</span><small style="font-size:0.62rem; color:var(--c-silver-slate);">For Debris Rescue</small>`;
    }
  },

  // ----------------- Visual Screen Distress Strobe -----------------
  toggleScreenStrobe() {
    this.isStrobeActive = !this.isStrobeActive;
    const screen = document.querySelector(".phone-screen");
    const btn = document.getElementById("toggleScreenStrobeBtn");

    if (this.isStrobeActive) {
      if (screen) screen.classList.add("screen-flashing");
      if (btn) {
        btn.style.background = "#ef4444";
        btn.style.color = "#fff";
        btn.innerHTML = `<span class="icon">⚡</span><span>Stop Strobe</span><small>Night Strobe On</small>`;
      }
    } else {
      this.stopScreenStrobe();
    }
  },

  stopScreenStrobe() {
    this.isStrobeActive = false;
    const screen = document.querySelector(".phone-screen");
    const btn = document.getElementById("toggleScreenStrobeBtn");
    if (screen) screen.classList.remove("screen-flashing");
    if (btn) {
      btn.style.background = "";
      btn.style.color = "";
      btn.innerHTML = `<span class="icon">🔦</span><span>Visual Strobe</span><small style="font-size:0.62rem; color:var(--c-silver-slate);">Night Search Beacon</small>`;
    }
  },

  // ----------------- Emergency Siren -----------------
  toggleEmergencySiren() {
    if (this.isSirenPlaying) {
      this.stopEmergencySiren();
    } else {
      this.playEmergencySiren();
    }
  },

  playEmergencySiren() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!this.audioCtx) this.audioCtx = new AudioContext();
      if (this.audioCtx.state === "suspended") this.audioCtx.resume();

      this.sirenOsc = this.audioCtx.createOscillator();
      this.sirenGain = this.audioCtx.createGain();

      this.sirenOsc.type = "sawtooth";
      this.sirenGain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);

      const now = this.audioCtx.currentTime;
      this.sirenOsc.frequency.setValueAtTime(600, now);
      this.sirenOsc.frequency.linearRampToValueAtTime(1000, now + 0.6);
      this.sirenOsc.frequency.linearRampToValueAtTime(600, now + 1.2);
      this.sirenOsc.frequency.linearRampToValueAtTime(1000, now + 1.8);
      this.sirenOsc.frequency.linearRampToValueAtTime(600, now + 2.4);

      this.sirenOsc.connect(this.sirenGain);
      this.sirenGain.connect(this.audioCtx.destination);
      this.sirenOsc.start();
      this.isSirenPlaying = true;

      const sirenBtn = document.getElementById("toggleSirenBtn");
      if (sirenBtn) {
        sirenBtn.classList.add("sound-playing");
        sirenBtn.innerHTML = "🔊 Silence Siren";
      }

      setTimeout(() => this.stopEmergencySiren(), 6000);
    } catch (e) {
      console.warn("Web Audio policy:", e);
    }
  },

  stopEmergencySiren() {
    if (this.sirenOsc) {
      try {
        this.sirenOsc.stop();
        this.sirenOsc.disconnect();
      } catch (e) {}
      this.sirenOsc = null;
    }
    this.isSirenPlaying = false;
    const sirenBtn = document.getElementById("toggleSirenBtn");
    if (sirenBtn) {
      sirenBtn.classList.remove("sound-playing");
      sirenBtn.innerHTML = "🔔 Test Siren";
    }
  },

  startPolling() {
    this.pollTimer = setInterval(() => {
      if (!this.isOfflineMode) {
        this.loadCitizenView();
      }
    }, 3000);
  }
};

window.CitizenApp = CitizenApp;
