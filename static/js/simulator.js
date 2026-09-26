/**
 * Telecom Gateway, SMS/USSD, and IVR Voice Call Simulator
 * Provides interactive simulation of low-bandwidth cellular channels
 */

const TelecomSimulator = {
  citizens: [],
  pollTimer: null,
  activeIvrCitizen: null,

  init() {
    this.bindEvents();
    this.loadCitizensForSelector();
    this.fetchTelecomEvents();
    this.startPolling();
  },

  bindEvents() {
    // SMS Reply form
    const smsForm = document.getElementById("simulateSmsForm");
    if (smsForm) {
      smsForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.sendSimulatedSms();
      });
    }

    // USSD form
    const ussdForm = document.getElementById("simulateUssdForm");
    if (ussdForm) {
      ussdForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.dialSimulatedUssd();
      });
    }

    // IVR Call button
    const testIvrBtn = document.getElementById("simulateIvrCallBtn");
    if (testIvrBtn) {
      testIvrBtn.addEventListener("click", () => {
        this.startSimulatedIvrCall();
      });
    }
  },

  async loadCitizensForSelector() {
    try {
      const res = await fetch("/api/citizens");
      this.citizens = await res.json();

      ["simSmsPhoneSelect", "simUssdPhoneSelect", "simIvrPhoneSelect"].forEach((id) => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = "";
        this.citizens.forEach((c) => {
          const opt = document.createElement("option");
          opt.value = c.phone;
          opt.textContent = `${c.name} (${c.phone}) - ${c.device_type}`;
          sel.appendChild(opt);
        });
      });
    } catch (e) {
      console.error("Error loading citizens for simulator:", e);
    }
  },

  async sendSimulatedSms(quickText = null) {
    const phone = document.getElementById("simSmsPhoneSelect").value;
    const text = quickText || document.getElementById("simSmsBodyInput").value;
    if (!phone || !text) return;

    try {
      const res = await fetch("/api/sms/incoming", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, body: text })
      });
      const data = await res.json();
      this.fetchTelecomEvents();
      if (window.AdminApp) window.AdminApp.fetchTrackingData();
      if (window.CitizenApp) window.CitizenApp.loadCitizenView();
      alert(`SMS sent from ${phone}: "${text}" -> Server acknowledged.`);
    } catch (e) {
      console.error("SMS simulation error:", e);
    }
  },

  async dialSimulatedUssd(code = null) {
    const phone = document.getElementById("simUssdPhoneSelect").value;
    const ussdCode = code || document.getElementById("simUssdCodeInput").value;
    if (!phone || !ussdCode) return;

    try {
      const res = await fetch("/api/ussd/dial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, code: ussdCode })
      });
      const data = await res.json();
      this.fetchTelecomEvents();
      if (window.AdminApp) window.AdminApp.fetchTrackingData();
      if (window.CitizenApp) window.CitizenApp.loadCitizenView();
      alert(`USSD Dialed: ${ussdCode}\nNetwork Response: "Acknowledged Safe via 2G USSD"`);
    } catch (e) {
      console.error("USSD error:", e);
    }
  },

  async startSimulatedIvrCall() {
    const phone = document.getElementById("simIvrPhoneSelect").value;
    const citizen = this.citizens.find((c) => c.phone === phone);
    if (!citizen) return;

    this.activeIvrCitizen = citizen;
    const callModal = document.getElementById("ivrCallModal");
    if (callModal) callModal.style.display = "flex";

    document.getElementById("ivrModalCaller").textContent = "EMERGENCY DISASTER IVR (112)";
    document.getElementById("ivrModalTarget").textContent = `Calling ${citizen.name} (${citizen.phone})...`;
    document.getElementById("ivrModalStatus").textContent = "CALL IN PROGRESS (Automated Voice)";

    // Fetch alert speech script
    try {
      const res = await fetch(`/api/citizen/${citizen.id}/active-alert`);
      const data = await res.json();
      let voiceScript = "Urgent Disaster Warning. If you are safe, press 1. If you need rescue, press 2.";
      if (data && data.has_alert) {
        voiceScript = data.alert_payload.ivr_script;
      }
      document.getElementById("ivrSpokenScriptDisplay").textContent = `"${voiceScript}"`;

      // Speak using SpeechSynthesis
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(voiceScript);
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
      }
    } catch (e) {
      console.error("IVR script error:", e);
    }
  },

  async respondIvrDtmf(digit) {
    if (!this.activeIvrCitizen) return;

    try {
      const res = await fetch("/api/ivr/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: this.activeIvrCitizen.phone,
          digit: digit
        })
      });
      const data = await res.json();

      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }

      const callModal = document.getElementById("ivrCallModal");
      if (callModal) callModal.style.display = "none";

      alert(`Keypad DTMF '${digit}' received. Call terminated. Citizen status updated to ${digit === '1' ? 'SAFE' : 'RESCUE'}!`);
      this.fetchTelecomEvents();
      if (window.AdminApp) window.AdminApp.fetchTrackingData();
      if (window.CitizenApp) window.CitizenApp.loadCitizenView();
    } catch (e) {
      console.error("IVR DTMF error:", e);
    }
  },

  closeIvrModal() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    const callModal = document.getElementById("ivrCallModal");
    if (callModal) callModal.style.display = "none";
  },

  async fetchTelecomEvents() {
    try {
      const res = await fetch("/api/telecom/events?limit=40");
      const events = await res.json();
      const container = document.getElementById("telecomEventFeed");
      if (!container) return;
      container.innerHTML = "";

      if (events.length === 0) {
        container.innerHTML = '<div style="color:#64748b; padding:1rem; text-align:center;">No telecom events logged yet.</div>';
        return;
      }

      events.forEach((ev) => {
        const item = document.createElement("div");
        item.style.padding = "0.6rem 0.8rem";
        item.style.borderBottom = "1px solid rgba(255,255,255,0.06)";
        item.style.fontSize = "0.8rem";
        item.style.display = "flex";
        item.style.flexDirection = "column";
        item.style.gap = "0.2rem";

        const dirBadge = ev.direction === "INBOUND" 
          ? `<span class="badge badge-safe">📥 INBOUND</span>` 
          : `<span class="badge badge-push">📤 OUTBOUND</span>`;

        let channelBadge = `<span class="badge badge-sms">${ev.channel}</span>`;
        if (ev.channel === "IVR") channelBadge = `<span class="badge badge-ivr">IVR CALL</span>`;
        if (ev.channel === "USSD") channelBadge = `<span class="badge badge-warning">USSD</span>`;

        const timeStr = new Date(ev.created_at).toLocaleTimeString();

        item.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>${dirBadge} ${channelBadge} <strong style="color:var(--c-pearl-lavender);">${ev.phone}</strong></div>
            <span style="color:var(--c-silver-slate); font-size:0.75rem;">${timeStr}</span>
          </div>
          <div style="color:var(--c-pearl-lavender); font-family:monospace; background:rgba(0,0,0,0.35); padding:0.35rem 0.5rem; border-radius:4px; border:1px solid var(--border-subtle);">
            ${ev.message}
          </div>
        `;
        container.appendChild(item);
      });
    } catch (e) {
      console.error("Telecom events error:", e);
    }
  },

  startPolling() {
    this.pollTimer = setInterval(() => {
      this.fetchTelecomEvents();
    }, 3000);
  }
};

window.TelecomSimulator = TelecomSimulator;
