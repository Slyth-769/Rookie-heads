/**
 * Rookies — Distress & Unresponsive Citizens Hub Logic
 * Features:
 * - Real-time tracking of citizens unresponsive past the 30-second emergency timeline
 * - Automated emergency voice call to saved contact (Kin)
 * - Interactive Web Speech API audio playback of Kin call
 * - Direct warden dispatch and active SOS rescue monitoring
 */

const DistressHub = {
  unresponsiveList: [],
  rescueList: [],
  pollTimer: null,
  activeKinCitizen: null,

  init() {
    this.fetchDistressData();
    this.startPolling();
  },

  async fetchDistressData() {
    try {
      const res = await fetch("/api/emergency/distress");
      const data = await res.json();
      this.unresponsiveList = data.unresponsive_citizens || [];
      this.rescueList = data.sos_rescue_requests || [];

      this.updateCounts();
      this.renderUnresponsiveCards();
      this.renderRescueCards();
    } catch (e) {
      console.error("Distress Hub fetch error:", e);
    }
  },

  updateCounts() {
    const unrespCountEl = document.getElementById("countUnresponsiveBadge");
    const sosCountEl = document.getElementById("countSosBadge");
    const kinCallsCountEl = document.getElementById("kpiKinCallsCount");
    const totalDistressCountEl = document.getElementById("kpiTotalDistressCount");

    if (unrespCountEl) unrespCountEl.textContent = this.unresponsiveList.length;
    if (sosCountEl) sosCountEl.textContent = this.rescueList.length;
    if (totalDistressCountEl) totalDistressCountEl.textContent = this.unresponsiveList.length + this.rescueList.length;

    const kinCallsDispatched = this.unresponsiveList.filter((c) => c.kin_call_dispatched).length;
    if (kinCallsCountEl) kinCallsCountEl.textContent = kinCallsDispatched;
  },

  renderUnresponsiveCards() {
    const container = document.getElementById("unresponsiveCardsContainer");
    if (!container) return;
    container.innerHTML = "";

    if (this.unresponsiveList.length === 0) {
      container.innerHTML = `
        <div style="background:#0e2219; padding:2rem; border-radius:12px; text-align:center; border:1px dashed var(--border-color);">
          <div style="font-size:2rem; margin-bottom:0.5rem;">✅</div>
          <h4 style="color:#34d399; margin-bottom:0.25rem;">All Citizens Acknowledged</h4>
          <p style="color:var(--c-mint-sage); font-size:0.8rem;">No citizens currently overdue beyond the 30-second emergency timeline.</p>
        </div>
      `;
      return;
    }

    this.unresponsiveList.forEach((c) => {
      const card = document.createElement("div");
      card.className = "distress-card kin-alerted";

      const secName = c.secondary_name || "Emergency Kin Contact";
      const secPhone = c.secondary_phone || "+919861012346";
      const elapsedMin = Math.floor(c.elapsed_seconds / 60);
      const elapsedSec = c.elapsed_seconds % 60;
      const timeStr = elapsedMin > 0 ? `${elapsedMin}m ${elapsedSec}s` : `${elapsedSec}s`;

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span class="badge badge-extreme">⚠️ UNRESPONSIVE (${timeStr} OVERDUE)</span>
              <span class="badge badge-push">Channel: ${c.channel}</span>
            </div>
            <h3 style="font-size:1.1rem; font-weight:800; color:var(--c-blue-ice); margin-top:0.35rem;">
              ${c.name} <span style="font-size:0.8rem; font-weight:600; color:var(--c-blue-electric);">(${c.phone})</span>
            </h3>
            <p style="color:var(--c-mint-sage); font-size:0.78rem;">
              📍 <strong>${c.block_village}</strong>, ${c.district} • GPS: ${c.lat.toFixed(4)}°N, ${c.lng.toFixed(4)}°E
            </p>
          </div>

          <div style="display:flex; gap:0.4rem; align-items:center;">
            <button class="btn btn-sm btn-danger" onclick="DistressHub.dispatchWarden('${c.alert_id}', ${c.citizen_id})">
              🚨 Dispatch Warden
            </button>
            <button class="btn btn-sm btn-success" onclick="DistressHub.markSafe('${c.alert_id}', ${c.citizen_id})">
              ✓ Mark Safe
            </button>
          </div>
        </div>

        <!-- Saved Contact (Kin) Automated Emergency Call Card -->
        <div class="kin-call-box">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.4rem;">
            <div>
              <strong style="color:var(--c-blue-electric); font-size:0.82rem;">📞 Saved Emergency Contact:</strong>
              <span style="color:var(--c-blue-ice); font-weight:700;">${secName} (${secPhone})</span>
            </div>
            <span class="badge badge-kin-call">Automated Voice Call Active</span>
          </div>

          <div style="background:rgba(0,0,0,0.35); padding:0.5rem; border-radius:6px; color:var(--c-mint-sage); font-size:0.74rem; font-style:italic; line-height:1.4; border:1px solid rgba(56,189,248,0.2);">
            "${c.kin_call_script}"
          </div>

          <div style="display:flex; justify-content:flex-end; gap:0.5rem; margin-top:0.5rem;">
            <button class="btn btn-sm btn-blue" onclick="DistressHub.playKinVoiceCall('${c.name}', '${secName}', '${c.block_village}', '${c.hazard_type}', '${c.severity}')">
              🔊 Listen / Simulate Kin Voice Call
            </button>
            <button class="btn btn-sm btn-secondary" onclick="DistressHub.triggerKinEmergencyCall('${c.alert_id}', ${c.citizen_id})">
              📞 Redial Saved Contact
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  },

  renderRescueCards() {
    const container = document.getElementById("rescueCardsContainer");
    if (!container) return;
    container.innerHTML = "";

    if (this.rescueList.length === 0) {
      container.innerHTML = `
        <div style="background:#0e2219; padding:2rem; border-radius:12px; text-align:center; border:1px dashed var(--border-color);">
          <div style="font-size:2rem; margin-bottom:0.5rem;">🛡️</div>
          <h4 style="color:#34d399; margin-bottom:0.25rem;">No Active SOS Rescue Calls</h4>
          <p style="color:var(--c-mint-sage); font-size:0.8rem;">No citizens currently requesting emergency evacuation rescue.</p>
        </div>
      `;
      return;
    }

    this.rescueList.forEach((c) => {
      const card = document.createElement("div");
      card.className = "distress-card sos-active";

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <span class="badge badge-extreme">🆘 IMMEDIATE RESCUE REQUESTED</span>
            <h3 style="font-size:1.1rem; font-weight:800; color:#fca5a5; margin-top:0.35rem;">
              ${c.name} <span style="font-size:0.8rem; font-weight:600; color:var(--c-blue-ice);">(${c.phone})</span>
            </h3>
            <p style="color:var(--c-mint-sage); font-size:0.78rem;">
              📍 <strong>${c.block_village}</strong>, ${c.district} • GPS: <b>${c.lat.toFixed(4)}°N, ${c.lng.toFixed(4)}°E</b>
            </p>
            <p style="color:#fde68a; font-size:0.75rem; margin-top:0.25rem;">
              Hazard: ${c.hazard_type} (${c.severity}) in ${c.area_name}
            </p>
          </div>

          <div style="display:flex; gap:0.4rem; align-items:center;">
            <button class="btn btn-sm btn-danger" onclick="DistressHub.dispatchWarden('${c.alert_id}', ${c.citizen_id})">
              🚤 Dispatch NDRF / Warden
            </button>
            <button class="btn btn-sm btn-success" onclick="DistressHub.markSafe('${c.alert_id}', ${c.citizen_id})">
              ✓ Mark Rescued
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  },

  // ----------------- Simulate Kin Voice Call Audio -----------------
  playKinVoiceCall(citizenName, secName, village, hazard, severity) {
    const modal = document.getElementById("ivrCallModal");
    if (modal) modal.style.display = "flex";

    document.getElementById("ivrModalCaller").textContent = "ROOKIES EMERGENCY KIN ALERT";
    document.getElementById("ivrModalTarget").textContent = `Calling Saved Contact: ${secName}...`;
    document.getElementById("ivrModalStatus").textContent = "EMERGENCY KIN NOTIFICATION CONNECTED";

    const speechText = (
      `Emergency notification from Rookies Disaster Control. ` +
      `Your contact, ${citizenName} at ${village}, has not responded to the ${hazard} ${severity} alert within the 30-second emergency timeline. ` +
      `They are in active danger. Please contact them immediately or assist in their evacuation. Press 1 to acknowledge.`
    );

    document.getElementById("ivrSpokenScriptDisplay").textContent = `"${speechText}"`;

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  },

  async triggerKinEmergencyCall(alertId, citizenId) {
    try {
      const res = await fetch("/api/kin/emergency-call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ alert_id: alertId, citizen_id: citizenId })
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        alert(`Emergency Voice Call placed to saved contact ${data.kin_name} (${data.kin_phone})!`);
        this.fetchDistressData();
      }
    } catch (e) {
      console.error("Kin call error:", e);
    }
  },

  async dispatchWarden(alertId, citizenId) {
    try {
      const res = await fetch(`/api/alerts/${alertId}/manual-override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "DISPATCH_WARDEN", citizen_id: citizenId })
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        alert("Emergency Field Warden Dispatched to Citizen's Location!");
        this.fetchDistressData();
      }
    } catch (e) {
      console.error("Warden error:", e);
    }
  },

  async markSafe(alertId, citizenId) {
    try {
      const res = await fetch(`/api/alerts/${alertId}/manual-override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "MARK_SAFE", citizen_id: citizenId })
      });
      const data = await res.json();
      if (data.status === "SUCCESS") {
        this.fetchDistressData();
      }
    } catch (e) {
      console.error("Mark safe error:", e);
    }
  },

  startPolling() {
    this.pollTimer = setInterval(() => {
      this.fetchDistressData();
    }, 2500);
  }
};

window.DistressHub = DistressHub;
