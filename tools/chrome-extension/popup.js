/**
 * popup.js — UI logic for 永生樹 Mission Control extension popup.
 *
 * Talks to background.js via chrome.runtime.sendMessage.
 * No direct fetch calls — background owns all HTTP.
 */

// ── Helpers ──────────────────────────────────────────────────────────────────

function esc(s) {
  const d = document.createElement("div");
  d.textContent = String(s ?? "");
  return d.innerHTML;
}

function colorClass(v) {
  if (!v) return "";
  const s = v.toLowerCase();
  if (s === "green")  return "green";
  if (s === "yellow") return "yellow";
  if (s === "red")    return "red";
  return "";
}

function formatTs(iso) {
  if (!iso) return "–";
  try {
    return new Date(iso).toLocaleTimeString("zh-TW", {
      timeZone: "Asia/Taipei",
      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
    });
  } catch { return iso.slice(11, 19) || iso; }
}

function sendMsg(type, extra = {}) {
  return new Promise((res, rej) => {
    chrome.runtime.sendMessage({ type, ...extra }, (r) => {
      if (chrome.runtime.lastError) rej(new Error(chrome.runtime.lastError.message));
      else res(r);
    });
  });
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderState(cache) {
  const offline = cache.offline;
  const liveDot = document.getElementById("live-dot");
  liveDot.className = "live-dot" + (offline ? " offline" : "");

  // ── Health bar ──────────────────────────────────────────
  const sl  = cache.statusline  || {};
  const bs  = cache.branchStatus || {};

  // Derive health (mirrors background.js logic)
  let health = offline ? "offline" : "green";
  if (!offline) {
    if (sl.mc_http && !sl.mc_http.healthy) health = "yellow";
    const allBranches = Object.values(bs.pills || {}).flatMap(p => p.branches || []);
    if (allBranches.some(b => (b.status || "").toLowerCase() === "red")) health = "red";
    if ((sl.log_errors_last_60min || 0) > 5 && health === "green") health = "yellow";
  }

  const hDot   = document.getElementById("health-dot");
  const hLabel = document.getElementById("health-label");
  const hSub   = document.getElementById("health-sub");

  hDot.className = "health-dot " + colorClass(health);
  hLabel.textContent = health.charAt(0).toUpperCase() + health.slice(1);
  // Show context % and cost in subtitle
  const sess = sl.session || {};
  const ctxPct  = sess.ctx_pct != null ? Math.round(sess.ctx_pct) + "% ctx" : "";
  const costUsd = sess.cost_usd != null ? "$" + sess.cost_usd.toFixed(3) : "";
  hSub.textContent = [ctxPct, costUsd].filter(Boolean).join("  ") || "";

  // ── Branch cards ─────────────────────────────────────────
  // /api/branch_status returns { pills: { "1": { name, branches: [...] } } }
  // Each branch has: id, name, status, active_tasks, blockers, etc.
  const branchEl = document.getElementById("branch-list");

  // Flatten pills → one card per pill showing worst-case health
  const pills = bs.pills || {};
  const pillEntries = Object.entries(pills);

  function worstHealth(branches) {
    const order = ["red", "yellow", "green", "unknown"];
    let worst = "unknown";
    for (const b of branches) {
      const s = (b.status || "").toLowerCase();
      const idx = order.indexOf(s);
      if (idx < order.indexOf(worst)) worst = s;
    }
    return worst;
  }

  if (!pillEntries.length && !offline) {
    branchEl.innerHTML = '<div class="no-branches">No branch data (tree_registry empty?)</div>';
  } else if (offline) {
    branchEl.innerHTML = '<div class="no-branches">Server offline — check localhost:7878</div>';
  } else {
    branchEl.innerHTML = pillEntries.slice(0, 8).map(([, pill]) => {
      const branches = pill.branches || [];
      const health   = worstHealth(branches);
      const color    = colorClass(health);
      // Show first active task as status hint
      const firstTask = branches.flatMap(b => b.active_tasks || []).slice(0, 1)[0] || "";
      return `<div class="branch-card">
        <span class="b-dot ${color}"></span>
        <span class="b-name">${esc(pill.name || "–")}</span>
        <span class="b-status">${esc(firstTask.slice(0, 30) || pill.name)}</span>
      </div>`;
    }).join("");
  }

  // ── Agent output (latest 2 entries) ──────────────────────
  const outboxSection = document.getElementById("outbox-section");
  const outboxTitle   = document.getElementById("outbox-title");
  const outbox        = cache.statusline?.recent_outbox || cache.branchStatus?.recent_outbox || [];

  if (outbox.length) {
    outboxTitle.style.display = "";
    outboxSection.innerHTML = outbox.slice(0, 2).map(e => {
      const ts   = e.ts || e.time || "";
      const text = e.text || e.content || JSON.stringify(e);
      return `<div class="outbox-item">
        <span class="outbox-ts">${esc(formatTs(ts))}</span>${esc(text.slice(0, 200))}
      </div>`;
    }).join("");
  } else {
    outboxTitle.style.display = "none";
    outboxSection.innerHTML = "";
  }

  // ── Footer ────────────────────────────────────────────────
  const tsEl = document.getElementById("footer-ts");
  tsEl.textContent = cache.lastOk
    ? "updated " + formatTs(cache.lastOk)
    : (offline ? "offline" : "no data");
}

// ── Send command ──────────────────────────────────────────────────────────────

async function sendCommand() {
  const input  = document.getElementById("cmd-input");
  const btn    = document.getElementById("cmd-btn");
  const status = document.getElementById("cmd-status");
  const text   = input.value.trim();
  if (!text) return;

  btn.disabled = true;
  status.className = "cmd-status";
  status.textContent = "Sending…";

  try {
    const r = await sendMsg("SEND_COMMAND", { text });
    if (r?.ok) {
      status.className = "cmd-status ok";
      status.textContent = "Sent to MC inbox";
      input.value = "";
    } else {
      status.className = "cmd-status err";
      status.textContent = r?.error || "Failed";
    }
  } catch (e) {
    status.className = "cmd-status err";
    status.textContent = e.message;
  } finally {
    btn.disabled = false;
    setTimeout(() => { status.textContent = ""; status.className = "cmd-status"; }, 3000);
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  // Load cached state immediately (no flicker)
  try {
    const r = await sendMsg("GET_STATE");
    if (r?.cache) renderState(r.cache);
  } catch { /* background not ready */ }

  // Kick a fresh refresh
  try {
    const r = await sendMsg("REFRESH");
    if (r?.cache) renderState(r.cache);
  } catch (e) {
    document.getElementById("health-label").textContent = "Error: " + e.message;
  }

  // Wire up controls
  document.getElementById("refresh-btn").addEventListener("click", async () => {
    const btn = document.getElementById("refresh-btn");
    btn.style.opacity = ".4";
    try {
      const r = await sendMsg("REFRESH");
      if (r?.cache) renderState(r.cache);
    } finally {
      btn.style.opacity = "";
    }
  });

  const cmdInput = document.getElementById("cmd-input");
  const cmdBtn   = document.getElementById("cmd-btn");

  cmdBtn.addEventListener("click", sendCommand);
  cmdInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendCommand(); }
  });

  // "Side Panel" link in footer — open the full dashboard side panel.
  const panelLink = document.getElementById("open-panel-link");
  if (panelLink && chrome.sidePanel) {
    panelLink.addEventListener("click", (e) => {
      e.preventDefault();
      chrome.windows.getCurrent({}, (win) => {
        chrome.sidePanel.open({ windowId: win.id }).catch(() => {
          chrome.tabs.create({ url: "http://localhost:7878/" });
        });
      });
      window.close();
    });
  } else if (panelLink) {
    // Chrome < 114: fall back to opening a tab
    panelLink.href = "http://localhost:7878/";
    panelLink.target = "_blank";
  }
}

document.addEventListener("DOMContentLoaded", init);
