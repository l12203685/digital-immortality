/**
 * sidepanel.js — Side Panel UI for 永生樹 Mission Control.
 *
 * Layout:
 *   - Toolbar: server health + SSE indicator + reload/open
 *   - Tabs: 即時 (realtime chat + status + tree) | 日常 (iframe combined.html)
 *
 * Data flow:
 *   - All HTTP lives in background.js.
 *   - We sendMessage({type:"GET_STATE"}) on load and register a
 *     chrome.runtime.onMessage listener for push updates
 *     (STATE_UPDATE / INBOX_NEW / OUTBOX_NEW / SSE_STATUS).
 *   - 日常 tab iframes http://localhost:7878/ (combined.html).
 */

// v0.6.0: MC_BASE is discovered dynamically via background.js. The side
// panel asks for the current backend URL on load and whenever the
// background signals TUNNEL_URL_CHANGE.
// v0.7.1: RELAY_BASE (stable zero-relay.pages.dev) is the off-LAN fallback
// used by the 日常 iframe when localhost is unreachable.
const LOCAL_BASE = "http://127.0.0.1:7878";
const RELAY_BASE = "https://zero-relay.pages.dev";
let MC_BASE = LOCAL_BASE; // updated async via GET_BACKEND_INFO

// ── Utilities ────────────────────────────────────────────────────────────────

function esc(s) {
  const d = document.createElement("div");
  d.textContent = String(s ?? "");
  return d.innerHTML;
}

function formatTs(iso) {
  if (!iso) return "–";
  try {
    return new Date(iso).toLocaleTimeString("zh-TW", {
      timeZone: "Asia/Taipei",
      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
    });
  } catch { return String(iso).slice(11, 19) || iso; }
}

function colorClass(v) {
  if (!v) return "";
  const s = String(v).toLowerCase();
  if (s === "green" || s === "yellow" || s === "red") return s;
  if (s === "offline") return "offline";
  return "";
}

function sendMsg(type, extra = {}) {
  return new Promise((res, rej) => {
    chrome.runtime.sendMessage({ type, ...extra }, (r) => {
      if (chrome.runtime.lastError) {
        rej(new Error(chrome.runtime.lastError.message));
        return;
      }
      res(r);
    });
  });
}

function classifyMsg(entry) {
  // Returns "in" (Edward/discord), "out" (agent reply), "self" (extension)
  const ch = String(entry.channel || "").toLowerCase();
  if (ch === "extension" || ch === "web_mc") return "self";
  if (entry._origin === "outbox") return "out";
  return "in";
}

function entryId(e) {
  if (e.id) return String(e.id);
  const t = String(e.ts || "");
  const c = String(e.channel || "");
  const x = String(e.text || e.content || "").slice(0, 60);
  return `${t}|${c}|${x}`;
}

// ── DOM references ───────────────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

const sseDot     = $("sse-dot");
const healthDotTb= $("health-dot-tb");
const healthDot  = $("health-dot");
const healthLbl  = $("health-label");
const healthSub  = $("health-sub");
const branchList = $("branch-list");
const chatScroll = $("chat-scroll");
const cmdInput   = $("cmd-input");
const cmdBtn     = $("cmd-btn");
const cmdStatus  = $("cmd-status");
const paneReal   = $("pane-realtime");
const paneDaily  = $("pane-daily");
const paneAsk    = $("pane-askpage");
const dashFrame  = $("dash-frame");
const offlineNotice = $("offline-notice");
const btnRetry   = $("btn-retry");
const btnReload  = $("btn-reload");
const btnOpen    = $("btn-open");

const meterCpu = $("meter-cpu");
const meterRam = $("meter-ram");
const meterDisk = $("meter-disk");
const meterCtx = $("meter-ctx");

// ── Merged chat stream (inbox + outbox, sorted by ts) ────────────────────────

let chatSeen = new Set();
let chatEntries = []; // [{...entry, _origin:"inbox"|"outbox"}]

function mergeIntoChat(entries, origin) {
  let added = 0;
  for (const e of entries || []) {
    const id = origin + ":" + entryId(e);
    if (chatSeen.has(id)) continue;
    chatSeen.add(id);
    chatEntries.push({ ...e, _origin: origin });
    added++;
  }
  if (!added) return false;
  chatEntries.sort((a, b) => String(a.ts || "").localeCompare(String(b.ts || "")));
  if (chatEntries.length > 120) chatEntries = chatEntries.slice(-120);
  return true;
}

function renderChat() {
  if (!chatEntries.length) {
    chatScroll.innerHTML = '<div class="msg-empty">尚無訊息。</div>';
    return;
  }
  const html = chatEntries.map((e) => {
    const cls = classifyMsg(e);
    const ch = e._origin === "outbox" ? "agent" : (e.channel || "?");
    const text = e.text || e.content || "";
    return `<div class="msg ${cls}">
      <div class="msg-meta">
        <span class="msg-ch">${esc(ch)}</span>
        <span>${esc(formatTs(e.ts))}</span>
      </div>
      ${esc(text)}
    </div>`;
  }).join("");
  const wasAtBottom = chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight < 40;
  chatScroll.innerHTML = html;
  if (wasAtBottom) {
    chatScroll.scrollTop = chatScroll.scrollHeight;
  }
}

// ── Render: health strip / meters / branches ─────────────────────────────────

function deriveHealth(cache) {
  if (cache.offline) return "offline";
  const sl = cache.statusline || {};
  const bs = cache.branchStatus || {};
  let health = "green";
  if (sl?.mc_http && !sl.mc_http.healthy) health = "yellow";
  if (bs?.pills) {
    const all = Object.values(bs.pills).flatMap(p => p.branches || []);
    if (all.some(b => (b.status || "").toLowerCase() === "red")) health = "red";
  }
  if ((sl?.log_errors_last_60min || 0) > 5 && health === "green") health = "yellow";
  return health;
}

function renderHealth(cache) {
  const health = deriveHealth(cache);
  healthDot.className   = "health-dot " + colorClass(health);
  healthDotTb.className = "tb-dot " + colorClass(health);
  healthLbl.textContent = cache.offline
    ? "Offline"
    : health.charAt(0).toUpperCase() + health.slice(1);

  const sl = cache.statusline || {};
  const sess = sl.session || {};
  const bits = [];
  if (sess.ctx_pct != null) bits.push(Math.round(sess.ctx_pct) + "% ctx");
  if (sess.cost_usd != null) bits.push("$" + Number(sess.cost_usd).toFixed(3));
  if (cache.lastSseEventAt) bits.push(formatTs(cache.lastSseEventAt));
  healthSub.textContent = bits.join(" · ");
}

function setMeter(el, label, value, warnAt, alertAt) {
  if (!el) return;
  const lbl = el.querySelector(".m-lbl");
  const val = el.querySelector(".m-val");
  if (lbl) lbl.textContent = label;
  if (val) val.textContent = value;
  el.classList.remove("warn", "alert");
  if (typeof warnAt === "number" && typeof alertAt === "number") {
    const n = parseFloat(String(value).replace(/[^\d.-]/g, ""));
    if (!isNaN(n)) {
      if (n >= alertAt) el.classList.add("alert");
      else if (n >= warnAt) el.classList.add("warn");
    }
  }
}

function renderMeters(cache) {
  const sl = cache.statusline || {};
  // statusline compact doesn't include system; fall back to embedded fields if present
  const sys = sl.system || sl.sys || {};
  const cpu = sys.cpu_pct ?? sys.cpu ?? null;
  const ram = sys.ram_pct ?? sys.ram ?? null;
  const disk = sys.disk_pct ?? sys.disk ?? null;
  const ctx = sl.session?.ctx_pct ?? null;
  setMeter(meterCpu, "CPU",  cpu  != null ? Math.round(cpu) + "%"  : "–", 70, 90);
  setMeter(meterRam, "RAM",  ram  != null ? Math.round(ram) + "%"  : "–", 75, 90);
  setMeter(meterDisk,"DISK", disk != null ? Math.round(disk) + "%" : "–", 80, 92);
  setMeter(meterCtx, "CTX",  ctx  != null ? Math.round(ctx) + "%"  : "–", 70, 85);
}

function renderBranches(cache) {
  const pills = cache.branchStatus?.pills || {};
  const entries = Object.entries(pills);
  if (!entries.length) {
    branchList.innerHTML = cache.offline
      ? '<div class="msg-empty">Offline</div>'
      : '<div class="msg-empty">No tree data</div>';
    return;
  }
  const order = ["red", "yellow", "green", "unknown"];
  branchList.innerHTML = entries.slice(0, 12).map(([, pill]) => {
    const branches = pill.branches || [];
    let worst = "unknown";
    for (const b of branches) {
      const s = (b.status || "").toLowerCase();
      if (order.indexOf(s) < order.indexOf(worst)) worst = s;
    }
    const firstTask = branches.flatMap(b => b.active_tasks || []).slice(0, 1)[0] || "";
    const status = firstTask || pill.summary || "";
    return `<div class="branch-card">
      <span class="b-dot ${colorClass(worst)}"></span>
      <span class="b-name">${esc(pill.name || "–")}</span>
      <span class="b-status">${esc(String(status).slice(0, 60))}</span>
    </div>`;
  }).join("");
}

function setSseIndicator(connected) {
  sseDot.className = "tb-dot " + (connected ? "live" : "offline");
  sseDot.title = connected ? "SSE connected" : "SSE disconnected";
}

// ── Render all from full cache ───────────────────────────────────────────────

function renderAll(cache) {
  if (!cache) return;
  renderHealth(cache);
  renderMeters(cache);
  renderBranches(cache);
  // Hydrate chat with recentInbox + recentOutbox
  if (Array.isArray(cache.recentInbox))  mergeIntoChat(cache.recentInbox, "inbox");
  if (Array.isArray(cache.recentOutbox)) mergeIntoChat(cache.recentOutbox, "outbox");
  renderChat();
  setSseIndicator(!!cache.sseConnected);
}

// ── Tabs ─────────────────────────────────────────────────────────────────────

async function switchTab(name) {
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === name);
  });
  paneReal.classList.toggle("active", name === "realtime");
  paneDaily.classList.toggle("active", name === "daily");
  if (paneAsk) paneAsk.classList.toggle("active", name === "askpage");
  if (name === "daily") {
    await loadDailyFrame();
  }
}

// ── Daily pane iframe ────────────────────────────────────────────────────────

async function _probeBase(base, timeoutMs = 3000) {
  try {
    const ctrl = new AbortController();
    const tid = setTimeout(() => ctrl.abort(), timeoutMs);
    const r = await fetch(base + "/api/statusline/compact", {
      signal: ctrl.signal, cache: "no-store",
    });
    clearTimeout(tid);
    return r.ok;
  } catch { return false; }
}

async function checkOnline() {
  return await _probeBase(MC_BASE);
}

// v0.7.1: Resolve the best base for the 日常 iframe. Prefer MC_BASE (which
// background.js has already discovered as LAN/tunnel/relay). If that fails,
// explicitly probe the stable relay URL so off-LAN users still get a live
// dashboard instead of the "Cannot reach localhost:7878" card.
async function _resolveDailyBase() {
  if (await _probeBase(MC_BASE)) return MC_BASE;
  if (MC_BASE !== RELAY_BASE && await _probeBase(RELAY_BASE, 5000)) {
    return RELAY_BASE;
  }
  return null;
}

async function _dashFrameUrl(base = MC_BASE) {
  // When running over the tunnel, prepend ?t=<token> so the iframe lands
  // pre-authenticated via the set-cookie redirect. On LAN (LOCAL_BASE)
  // auth is usually a no-op anyway, but including ?t= is harmless.
  let token = "";
  try {
    const info = await sendMsg("GET_BACKEND_INFO");
    if (info?.ok && info.has_token) {
      // We can't read the token here; instead ask the backend iframe to
      // use the redirect landing page which embeds the token server-side.
      // For the extension, route through the /redirect page which already
      // embeds MC_TOKEN in the emitted link.
      token = "use_redirect";
    }
  } catch (_e) { /* ignore */ }
  if (token === "use_redirect") {
    return base + "/redirect";
  }
  return base + "/";
}

async function loadDailyFrame() {
  // v0.7.1: try MC_BASE first, then fall back to the stable relay URL
  // before surfacing the offline card. This keeps the 日常 iframe alive
  // when Edward is off-LAN.
  const base = await _resolveDailyBase();
  if (base) {
    offlineNotice.classList.remove("visible");
    // Reload the iframe if its current src doesn't match the chosen base.
    if (dashFrame.src === "about:blank" || !dashFrame.src.startsWith(base)) {
      dashFrame.src = await _dashFrameUrl(base);
    }
    dashFrame.style.display = "";
  } else {
    dashFrame.style.display = "none";
    offlineNotice.classList.add("visible");
  }
}

// ── Command send ─────────────────────────────────────────────────────────────

async function sendCommand() {
  const text = cmdInput.value.trim();
  if (!text) return;
  cmdBtn.disabled = true;
  cmdStatus.className = "";
  cmdStatus.textContent = "Sending…";
  try {
    const r = await sendMsg("SEND_COMMAND", { text });
    if (r?.ok) {
      cmdStatus.className = "ok";
      cmdStatus.textContent = "Sent";
      cmdInput.value = "";
    } else {
      cmdStatus.className = "err";
      cmdStatus.textContent = r?.error || "Failed";
    }
  } catch (e) {
    cmdStatus.className = "err";
    cmdStatus.textContent = e.message;
  } finally {
    cmdBtn.disabled = false;
    setTimeout(() => { cmdStatus.textContent = ""; cmdStatus.className = ""; }, 3000);
  }
}

// ── Push listener (background → side panel) ─────────────────────────────────

let _latestCache = {};

chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || !msg.type) return;
  switch (msg.type) {
    case "STATE_UPDATE":
      if (msg.payload?.patch) {
        _latestCache = { ..._latestCache, ...msg.payload.patch };
        renderAll(_latestCache);
      }
      break;
    case "INBOX_NEW":
      if (msg.payload?.entries) {
        if (mergeIntoChat(msg.payload.entries, "inbox")) renderChat();
      }
      break;
    case "OUTBOX_NEW":
      if (msg.payload?.entries) {
        if (mergeIntoChat(msg.payload.entries, "outbox")) renderChat();
      }
      break;
    case "SSE_STATUS":
      setSseIndicator(!!msg.payload?.connected);
      break;
    case "TUNNEL_URL_CHANGE":
      if (msg.payload?.url) {
        MC_BASE = String(msg.payload.url).replace(/\/+$/, "");
        // Re-point the daily dashboard iframe so the user doesn't see
        // a dead frame after the URL rotated.
        if (paneDaily.classList.contains("active")) {
          dashFrame.src = MC_BASE + "/?_r=" + Date.now();
        }
      }
      break;
    case "ZERO_ASK_PAGE_DELTA":
    case "HERMES_ASK_PAGE_DELTA": // legacy alias — remove after v0.6
      if (msg.payload && msg.payload.streamId === _askStreamId) {
        askpageAppend(msg.payload.delta || "");
      }
      break;
    case "ZERO_ASK_PAGE_DONE":
    case "HERMES_ASK_PAGE_DONE": // legacy alias — remove after v0.6
      if (msg.payload && msg.payload.streamId === _askStreamId) {
        askpageFinish(msg.payload);
      }
      break;
  }
});

// ── Ask-this-page tab ────────────────────────────────────────────────────────

const askLoadBtn = $("askpage-load");
const askSumBtn  = $("askpage-summarize");
const askClrBtn  = $("askpage-clear");
const askInput   = $("askpage-input");
const askSendBtn = $("askpage-send");
const askOutput  = $("askpage-output");
const askMeta    = $("askpage-meta");
const askTitle   = $("askpage-title");
const askUrl     = $("askpage-url");

let _askSnapshot = null;   // {url, title, content, extracted_at}
let _askStreamId = null;   // current in-flight stream id
let _askBusy     = false;

function askpageSetEmpty() {
  askOutput.innerHTML = '<div class="askpage-empty">點「讀取此頁」抓取當前分頁內容，然後問任何問題。</div>';
  askMeta.textContent = "";
}

function askpageClearOutput() {
  askOutput.textContent = "";
}

function askpageAppend(text) {
  // If currently showing the empty placeholder, swap to plain text.
  if (askOutput.querySelector(".askpage-empty")) askOutput.textContent = "";
  askOutput.textContent += text;
  const atBottom = askOutput.scrollHeight - askOutput.scrollTop - askOutput.clientHeight < 80;
  if (atBottom) askOutput.scrollTop = askOutput.scrollHeight;
}

function askpageFinish(payload) {
  _askBusy = false;
  askSendBtn.disabled = !_askSnapshot;
  askSumBtn.disabled = !_askSnapshot;
  if (payload && payload.error) {
    askMeta.textContent = "error: " + payload.error;
  } else if (payload && payload.reason) {
    askMeta.textContent = "done · " + payload.reason;
  } else {
    askMeta.textContent = "done";
  }
}

// v0.7.1: translate background error codes into the 問頁 tab's output area
// with a friendly zh-Hant message so Edward isn't staring at raw Chrome
// runtime strings like "Could not establish connection".
function _askpageRenderError(errCode) {
  const code = String(errCode || "");
  const human = (() => {
    if (/^restricted_url$/i.test(code) || /cannot\s+access|cannot be scripted|Missing host permission/i.test(code)) {
      return "此頁面無法讀取（Chrome 內部頁或受限頁）。\n請切到一般網頁（https:// 開頭）再用。";
    }
    if (/^denylisted_domain$/i.test(code)) {
      return "此網站在安全清單內（銀行／登入／金流頁），為保護不讀取。";
    }
    if (/^no_active_tab$/i.test(code)) {
      return "找不到使用中的分頁。請先切到要讀取的網頁。";
    }
    if (/Receiving end does not exist|no_content_script/i.test(code)) {
      return "此分頁未載入擴充腳本。請重新整理分頁（F5），或切到其他頁面再回來。";
    }
    return "讀取失敗：" + code;
  })();
  askOutput.innerHTML = '';
  const box = document.createElement('div');
  box.className = 'askpage-empty';
  box.style.whiteSpace = 'pre-wrap';
  box.style.textAlign = 'left';
  box.style.lineHeight = '1.6';
  box.textContent = human;
  askOutput.appendChild(box);
}

async function askpageLoad() {
  askLoadBtn.disabled = true;
  askMeta.textContent = "reading page…";
  try {
    const r = await sendMsg("ZERO_GET_PAGE_SNAPSHOT");
    if (!r || !r.ok) throw new Error((r && r.error) || "failed");
    _askSnapshot = r.snapshot;
    askTitle.textContent = _askSnapshot.title || "(no title)";
    askUrl.textContent   = _askSnapshot.url || "";
    const kb = (_askSnapshot.content || "").length / 1024;
    askMeta.textContent = `loaded · ${kb.toFixed(1)} KB · ${formatTs(_askSnapshot.extracted_at)}`;
    askSendBtn.disabled = false;
    askSumBtn.disabled = false;
    askClrBtn.disabled = false;
    askInput.disabled = false;
    askpageSetEmpty();
  } catch (e) {
    const raw = String(e.message || e);
    askMeta.textContent = "error";
    _askpageRenderError(raw);
  } finally {
    askLoadBtn.disabled = false;
  }
}

async function askpageAsk(question) {
  if (!_askSnapshot) {
    askMeta.textContent = "no page loaded";
    return;
  }
  if (_askBusy) return;
  _askBusy = true;
  askSendBtn.disabled = true;
  askSumBtn.disabled = true;
  _askStreamId = "ask_" + Date.now();
  askpageClearOutput();
  askMeta.textContent = "streaming…";
  try {
    const r = await sendMsg("ZERO_ASK_PAGE", {
      question,
      snapshot: _askSnapshot,
      streamId: _askStreamId,
    });
    // If background returned synchronously (edge case), use that text.
    if (r && r.ok && typeof r.text === "string" && !askOutput.textContent) {
      askpageAppend(r.text);
    }
    // Finish is driven by ZERO_ASK_PAGE_DONE broadcast (HERMES_* legacy
    // alias also accepted); still flip flags here as a safety net.
    if (r && !r.ok) askpageFinish({ error: r.error });
  } catch (e) {
    askpageFinish({ error: e.message });
  }
}

function askpageWireEvents() {
  if (!askLoadBtn) return;
  askLoadBtn.addEventListener("click", askpageLoad);
  askSumBtn.addEventListener("click", () => askpageAsk("Summarize this page in 5 concise bullet points."));
  askClrBtn.addEventListener("click", () => {
    askpageClearOutput();
    askpageSetEmpty();
  });
  askSendBtn.addEventListener("click", () => {
    const q = (askInput.value || "").trim();
    if (!q) return;
    askInput.value = "";
    askpageAsk(q);
  });
  askInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askSendBtn.click();
    }
  });
  askInput.addEventListener("input", () => {
    askInput.style.height = "auto";
    askInput.style.height = Math.min(askInput.scrollHeight, 80) + "px";
  });
}

// ── Init ─────────────────────────────────────────────────────────────────────

async function ensureBackendAndToken() {
  // Fetch the discovered backend URL + token presence from background.
  try {
    const info = await sendMsg("GET_BACKEND_INFO");
    if (info?.ok && info.base) {
      MC_BASE = String(info.base).replace(/\/+$/, "");
    }
    if (!info?.has_token) {
      // Soft prompt — Edward pastes MC_TOKEN once from
      // C:/Users/admin/.claude/scripts/mission_control/.mc_token
      const token = window.prompt(
        "Paste MC_TOKEN (from .mc_token file) to enable off-LAN access:",
        "",
      );
      if (token && token.trim()) {
        await sendMsg("SET_MC_TOKEN", { token: token.trim() });
      }
    }
  } catch (_e) {
    // background may not be awake yet — init() retries via REFRESH
  }
}

async function init() {
  // Resolve backend + token first so every subsequent call has the
  // right base + bearer header.
  await ensureBackendAndToken();

  // Wire tabs
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.addEventListener("click", () => switchTab(b.dataset.tab));
  });

  // Toolbar buttons — route via /redirect so the tab lands pre-auth.
  btnOpen.addEventListener("click", () => {
    chrome.tabs.create({ url: MC_BASE + "/redirect" });
  });
  btnReload.addEventListener("click", async () => {
    btnReload.style.opacity = ".4";
    try { await sendMsg("REFRESH"); } catch {}
    if (paneDaily.classList.contains("active")) {
      const base = await _dashFrameUrl();
      dashFrame.src = base + (base.includes("?") ? "&" : "?") + "_r=" + Date.now();
    }
    btnReload.style.opacity = "";
  });
  btnRetry.addEventListener("click", loadDailyFrame);

  // Command input
  cmdBtn.addEventListener("click", sendCommand);
  cmdInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendCommand();
    }
  });
  // Auto-grow
  cmdInput.addEventListener("input", () => {
    cmdInput.style.height = "auto";
    cmdInput.style.height = Math.min(cmdInput.scrollHeight, 80) + "px";
  });

  // Ask-this-page wiring
  askpageWireEvents();

  // Load cached state immediately
  try {
    const r = await sendMsg("GET_STATE");
    if (r?.cache) {
      _latestCache = r.cache;
      renderAll(_latestCache);
    }
  } catch { /* background not ready */ }

  // Kick a fresh refresh (opens SSE)
  try {
    const r = await sendMsg("REFRESH");
    if (r?.cache) {
      _latestCache = r.cache;
      renderAll(_latestCache);
    }
  } catch (e) {
    healthLbl.textContent = "Error: " + e.message;
  }
}

document.addEventListener("DOMContentLoaded", init);
