/**
 * background.js — Service worker for 永生樹 Mission Control extension.
 *
 * v0.3.0: Real-time SSE push. The service worker opens a streaming
 * fetch to /api/events and parses text/event-stream frames. New inbox
 * / outbox entries, statusline snapshots and branch status arrive in
 * <1 s instead of the old 60 s alarm-poll cycle.
 *
 * Alarms are kept as a fallback — if the SSE stream dies (network,
 * laptop sleep, server restart) the alarm still refreshes state every
 * 60 s and reconnects the stream.
 *
 * Architecture:
 *   - Chrome MV3 service workers cannot use the EventSource class
 *     (not exposed to workers). Instead we `fetch(..., { body })`
 *     and read from the ReadableStream line by line.
 *   - All HTTP lives here. popup.js / sidepanel.html talk to this
 *     worker via chrome.runtime.sendMessage (pull) and
 *     chrome.runtime.sendMessage broadcasts (push).
 */

// v0.7.0: backend URL discovery with stable relay fallback.
// Resolution order per request:
//   1. LAN probe → LOCAL_BASE (fast, no external hop)
//   2. Cached relay / tunnel URL if still fresh
//   3. RELAY_BASE (stable Cloudflare Pages proxy — never rotates)
// The relay transparently forwards to whatever trycloudflare URL the
// laptop daemon has most recently pushed via /admin/set_url, so we no
// longer need to track raw trycloudflare URLs ourselves.
const LOCAL_BASE = "http://127.0.0.1:7878";
const RELAY_BASE = "https://zero-relay.pages.dev";
const POLL_STATUS_ALARM = "mc_poll_status";
const POLL_INBOX_ALARM = "mc_poll_inbox";
const SSE_WATCHDOG_ALARM = "mc_sse_watchdog";
const STATUS_POLL_MINS = 1;
const INBOX_POLL_MINS = 2;
const SSE_WATCHDOG_MINS = 1;
// Max retry backoff when SSE keeps failing (ms)
const SSE_MAX_BACKOFF_MS = 30_000;
// TTL for cached backend URL (ms) — we refresh after this even on success
// so the extension eventually discovers URL rotations on its own.
const BASE_URL_TTL_MS = 5 * 60 * 1000;
// Storage keys
const KS_BACKEND = "mc_backend_url";
const KS_BACKEND_AT = "mc_backend_url_at";
const KS_BACKEND_KIND = "mc_backend_kind"; // "local" or "tunnel"
const KS_TOKEN = "mc_token";

// ── Cached state (survives worker recycle via chrome.storage.session) ───────

let _cache = {
  statusline: null,
  branchStatus: null,
  inboxPending: 0,
  recentInbox: [],   // last N inbox entries (newest last)
  recentOutbox: [],  // last N outbox entries (newest last)
  lastOk: null,
  lastSseEventAt: null,
  sseConnected: false,
  offline: false,
};

async function _saveCache() {
  try {
    await chrome.storage.session.set({ mc_cache: _cache });
  } catch (e) {
    // session storage may not be available in tests
  }
}

// ── Backend URL discovery + MC_TOKEN bootstrap ──────────────────────────────
//
// Resolution order for each request:
//   1. Cached backend URL (chrome.storage.local) if still fresh
//   2. LOCAL_BASE probe (/health) — succeeds when on LAN
//   3. Last-known tunnel URL from storage
//   4. /api/public_url via tunnel URL → refresh + retry
//
// MC_TOKEN is picked up on first install via a LAN-only bootstrap to
// LOCAL_BASE/api/public_url? The token itself is NOT exposed by that
// endpoint; instead, we do a local-only read of /api/public_url first
// (which is unauth), then require the user to open the LAN landing page
// (http://localhost:7878/redirect) once so the token cookie can be read
// through the backend's share endpoint. For v0.6 the simplest bootstrap
// is: prompt the user to paste the token once, persist in
// chrome.storage.local. If the storage already has a token we reuse it.

async function _storageGet(keys) {
  try {
    return await chrome.storage.local.get(keys);
  } catch (_e) {
    return {};
  }
}

async function _storageSet(obj) {
  try {
    await chrome.storage.local.set(obj);
  } catch (_e) {
    // ignore
  }
}

async function getMcToken() {
  const s = await _storageGet([KS_TOKEN]);
  return typeof s[KS_TOKEN] === "string" ? s[KS_TOKEN] : "";
}

async function setMcToken(token) {
  const t = String(token || "").trim();
  if (!t) return { ok: false, error: "empty" };
  await _storageSet({ [KS_TOKEN]: t });
  return { ok: true };
}

async function _probeLocal() {
  // /health is unauth; a 200 means the main machine is reachable.
  try {
    const c = new AbortController();
    const tid = setTimeout(() => c.abort(), 1500);
    const r = await fetch(LOCAL_BASE + "/health", {
      signal: c.signal, cache: "no-store",
    });
    clearTimeout(tid);
    return r.ok;
  } catch (_e) {
    return false;
  }
}

async function _fetchPublicUrl(base) {
  try {
    const c = new AbortController();
    const tid = setTimeout(() => c.abort(), 4000);
    const r = await fetch(base + "/api/public_url", {
      signal: c.signal, cache: "no-store",
    });
    clearTimeout(tid);
    if (!r.ok) return null;
    const data = await r.json();
    return data && typeof data.url === "string" ? data.url : null;
  } catch (_e) {
    return null;
  }
}

// Returns the currently-best MC base URL as a string (no trailing slash).
// Falls through: LAN > cached relay/tunnel > RELAY_BASE (stable) > LOCAL.
async function getCurrentBackendUrl({ force = false } = {}) {
  const s = await _storageGet([KS_BACKEND, KS_BACKEND_AT, KS_BACKEND_KIND]);
  const now = Date.now();
  const cached = typeof s[KS_BACKEND] === "string" ? s[KS_BACKEND] : "";
  const cachedAt = Number(s[KS_BACKEND_AT] || 0);
  const fresh = cached && (now - cachedAt) < BASE_URL_TTL_MS;
  if (!force && fresh) return cached;

  // 1. LAN probe — cheapest path when on home network.
  if (await _probeLocal()) {
    await _storageSet({
      [KS_BACKEND]: LOCAL_BASE,
      [KS_BACKEND_AT]: now,
      [KS_BACKEND_KIND]: "local",
    });
    return LOCAL_BASE;
  }

  // 2. Prefer the stable relay URL. It auto-forwards to whatever
  //    trycloudflare URL is currently current; no probing needed.
  await _storageSet({
    [KS_BACKEND]: RELAY_BASE,
    [KS_BACKEND_AT]: now,
    [KS_BACKEND_KIND]: "relay",
  });
  return RELAY_BASE;
}

async function setBackendUrl(url, kind = "tunnel") {
  if (!url) return;
  const cleaned = url.replace(/\/+$/, "");
  await _storageSet({
    [KS_BACKEND]: cleaned,
    [KS_BACKEND_AT]: Date.now(),
    [KS_BACKEND_KIND]: kind,
  });
}

async function _loadCache() {
  try {
    const s = await chrome.storage.session.get("mc_cache");
    if (s.mc_cache) _cache = { ..._cache, ...s.mc_cache };
  } catch (e) {
    // ignore
  }
}

// ── Broadcast to any open popup / side panel ─────────────────────────────────

function broadcast(type, payload) {
  chrome.runtime.sendMessage({ type, payload }).catch(() => {
    // No listeners — popup/side panel closed. Safe to ignore.
  });
}

// ── HTTP helpers ─────────────────────────────────────────────────────────────

async function _authHeaders(existing = {}) {
  const token = await getMcToken();
  const h = { ...(existing || {}) };
  if (token && !h.Authorization && !h.authorization) {
    h.Authorization = "Bearer " + token;
  }
  return h;
}

async function mcFetch(path, opts = {}) {
  // Resolve the backend base for every call so URL rotations take effect
  // within one request. On 401, we DO NOT retry — the caller (user) must
  // set the MC_TOKEN via the popup / options flow.
  const base = await getCurrentBackendUrl();
  const headers = await _authHeaders(opts.headers || {});
  const controller = new AbortController();
  const tid = setTimeout(() => controller.abort(), 4000);
  try {
    const r = await fetch(base + path, {
      signal: controller.signal,
      cache: "no-store",
      ...opts,
      headers,
    });
    clearTimeout(tid);
    if (r.status === 401) {
      throw new Error("HTTP 401 — MC_TOKEN missing or wrong");
    }
    if (!r.ok) {
      // Refresh base URL on 5xx / 502 so next call can rediscover.
      if (r.status >= 500) {
        await getCurrentBackendUrl({ force: true });
      }
      throw new Error(`HTTP ${r.status}`);
    }
    return await r.json();
  } catch (e) {
    clearTimeout(tid);
    throw e;
  }
}

// ── Badge helpers ────────────────────────────────────────────────────────────

function _colorFor(health) {
  if (!health || health === "unknown") return "#555555";
  const h = health.toLowerCase();
  if (h === "green") return "#22c55e";
  if (h === "yellow") return "#f59e0b";
  if (h === "red") return "#ef4444";
  return "#555555";
}

async function updateBadge(health, text) {
  const color = _colorFor(health);
  try {
    await chrome.action.setBadgeBackgroundColor({ color });
    await chrome.action.setBadgeText({ text: text || "" });
  } catch (e) {
    // ignore
  }
}

function _deriveHealth() {
  const sl = _cache.statusline || {};
  const bs = _cache.branchStatus || {};
  if (_cache.offline) return "offline";
  let health = "green";
  if (sl?.mc_http && !sl.mc_http.healthy) health = "yellow";
  if (bs?.pills) {
    const allBranches = Object.values(bs.pills).flatMap((p) => p.branches || []);
    if (allBranches.some((b) => (b.status || "").toLowerCase() === "red")) {
      health = "red";
    }
  }
  const logErrs = sl?.log_errors_last_60min ?? 0;
  if (logErrs > 5 && health === "green") health = "yellow";
  return health;
}

async function refreshBadge() {
  const health = _deriveHealth();
  const pending = _cache.inboxPending;
  const text = pending > 0 ? String(pending) : "";
  await updateBadge(health, text);
}

// ── Desktop notifications for Edward-directed messages ───────────────────────

// An "Edward-directed" message is one Edward himself sent into the dashboard
// or Discord. Heuristic: entry has channel in {"discord","line","voice"} OR
// entry.meta.from === "edward". Skip our own web_mc sends.
function isEdwardDirected(entry) {
  if (!entry) return false;
  const ch = String(entry.channel || "").toLowerCase();
  if (ch === "web_mc" || ch === "extension") return false;
  if (["discord", "line", "voice", "telegram"].includes(ch)) return true;
  const meta = entry.meta || {};
  if (String(meta.from || "").toLowerCase() === "edward") return true;
  return false;
}

const _notifiedIds = new Set();

function _entryId(e) {
  // Prefer explicit id, else synthesize from ts+channel+text hash
  if (e.id) return String(e.id);
  const t = String(e.ts || "");
  const c = String(e.channel || "");
  const x = String(e.text || e.content || "").slice(0, 60);
  return `${t}|${c}|${x}`;
}

function _truncate(s, n) {
  s = String(s || "");
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}

async function notifyInboxEntry(entry) {
  if (!isEdwardDirected(entry)) return;
  const id = _entryId(entry);
  if (_notifiedIds.has(id)) return;
  _notifiedIds.add(id);
  // cap memory
  if (_notifiedIds.size > 200) {
    const first = _notifiedIds.values().next().value;
    _notifiedIds.delete(first);
  }
  const text = entry.text || entry.content || "(no text)";
  const ch = entry.channel || "edward";
  try {
    await chrome.notifications.create("mc_edward_" + Date.now(), {
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: `Edward · ${ch}`,
      message: _truncate(text, 180),
      priority: 2,
    });
  } catch (e) {
    // ignore
  }
}

// ── SSE stream — fetch + ReadableStream parser ───────────────────────────────

let _sseController = null;
let _sseRetryMs = 1000;
let _sseLoopRunning = false;

async function ensureSSE() {
  if (_sseLoopRunning) return;
  _sseLoopRunning = true;
  // Fire-and-forget; loop self-manages reconnects.
  runSSELoop().catch(() => {
    _sseLoopRunning = false;
  });
}

async function runSSELoop() {
  while (true) {
    try {
      await openSSE();
      // openSSE returns normally when server says "bye" — reconnect
      _sseRetryMs = 1000;
    } catch (e) {
      _cache.sseConnected = false;
      await _saveCache();
      broadcast("SSE_STATUS", { connected: false, error: String(e && e.message || e) });
      // Exponential backoff, capped
      _sseRetryMs = Math.min(_sseRetryMs * 2, SSE_MAX_BACKOFF_MS);
    }
    // Gap between connect attempts
    await new Promise((r) => setTimeout(r, _sseRetryMs));
  }
}

async function openSSE() {
  // Abort any previous stream
  try {
    if (_sseController) _sseController.abort();
  } catch (e) {
    // ignore
  }
  _sseController = new AbortController();
  // Force-refresh base URL on SSE reconnect so an invalidated tunnel URL
  // doesn't keep reconnecting to a dead endpoint.
  const base = await getCurrentBackendUrl({ force: true });
  const headers = await _authHeaders({ Accept: "text/event-stream" });
  const r = await fetch(base + "/api/events", {
    cache: "no-store",
    signal: _sseController.signal,
    headers,
  });
  if (!r.ok || !r.body) {
    throw new Error(`SSE HTTP ${r.status}`);
  }
  _cache.sseConnected = true;
  _cache.offline = false;
  await _saveCache();
  broadcast("SSE_STATUS", { connected: true });

  const reader = r.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let currentEvent = "message";
  let currentData = [];

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      // Stream closed by server — loop will reconnect
      _cache.sseConnected = false;
      await _saveCache();
      broadcast("SSE_STATUS", { connected: false });
      return;
    }
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by double newline
    let idx;
    while ((idx = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, idx).replace(/\r$/, "");
      buffer = buffer.slice(idx + 1);

      if (line === "") {
        // End of one event — dispatch
        if (currentData.length) {
          const dataStr = currentData.join("\n");
          try {
            const parsed = JSON.parse(dataStr);
            await handleSseEvent(currentEvent, parsed);
          } catch (e) {
            // bad frame — skip
          }
        }
        currentEvent = "message";
        currentData = [];
        continue;
      }
      if (line.startsWith(":")) {
        // Keepalive comment — just bump timestamp
        _cache.lastSseEventAt = new Date().toISOString();
        continue;
      }
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        currentData.push(line.slice(5).replace(/^ /, ""));
      }
      // Ignore id: / retry: — not used
    }
  }
}

async function handleSseEvent(event, data) {
  _cache.lastSseEventAt = new Date().toISOString();
  _cache.lastOk = _cache.lastSseEventAt;
  _cache.offline = false;

  switch (event) {
    case "hello":
      // initial handshake — nothing else to do
      break;

    case "statusline":
      _cache.statusline = data;
      await refreshBadge();
      broadcast("STATE_UPDATE", { patch: { statusline: data } });
      break;

    case "branch_status":
      _cache.branchStatus = data;
      await refreshBadge();
      broadcast("STATE_UPDATE", { patch: { branchStatus: data } });
      break;

    case "inbox_recent":
      // initial hydration
      if (data && Array.isArray(data.entries)) {
        _cache.recentInbox = data.entries;
        broadcast("STATE_UPDATE", { patch: { recentInbox: data.entries } });
      }
      break;

    case "outbox_recent":
      if (data && Array.isArray(data.entries)) {
        _cache.recentOutbox = data.entries;
        broadcast("STATE_UPDATE", { patch: { recentOutbox: data.entries } });
      }
      break;

    case "inbox_new": {
      if (!data || !Array.isArray(data.entries)) break;
      const existingIds = new Set((_cache.recentInbox || []).map(_entryId));
      const fresh = data.entries.filter((e) => !existingIds.has(_entryId(e)));
      _cache.recentInbox = [...(_cache.recentInbox || []), ...fresh].slice(-40);
      broadcast("INBOX_NEW", { entries: fresh });
      broadcast("STATE_UPDATE", { patch: { recentInbox: _cache.recentInbox } });
      // Fire desktop notifications for Edward-directed messages
      for (const entry of fresh) {
        await notifyInboxEntry(entry);
      }
      break;
    }

    case "outbox_new": {
      if (!data || !Array.isArray(data.entries)) break;
      const existingIds = new Set((_cache.recentOutbox || []).map(_entryId));
      const fresh = data.entries.filter((e) => !existingIds.has(_entryId(e)));
      _cache.recentOutbox = [...(_cache.recentOutbox || []), ...fresh].slice(-40);
      broadcast("OUTBOX_NEW", { entries: fresh });
      broadcast("STATE_UPDATE", { patch: { recentOutbox: _cache.recentOutbox } });
      break;
    }

    case "tunnel_url":
    case "tunnel_url_change": {
      // Server signaled that the trycloudflare URL has rotated. With the
      // stable zero-relay.pages.dev in front, we don't need to track the
      // raw tunnel URL ourselves — the relay will auto-forward. We still
      // broadcast the event for UI surfaces that care, and if we were on
      // a raw trycloudflare URL (pre-relay install) we switch to the
      // relay for future stability.
      const newUrl = data && typeof data.url === "string" ? data.url : "";
      if (newUrl) {
        broadcast("TUNNEL_URL_CHANGE", { url: newUrl, status: data.status });
        // If our cached base is a raw trycloudflare URL, migrate to relay.
        const s = await _storageGet([KS_BACKEND, KS_BACKEND_KIND]);
        const cached = typeof s[KS_BACKEND] === "string" ? s[KS_BACKEND] : "";
        if (cached.includes(".trycloudflare.com")) {
          await setBackendUrl(RELAY_BASE, "relay");
        }
      }
      break;
    }

    case "bye":
      // Server voluntarily closed — just reconnect
      _cache.sseConnected = false;
      break;

    default:
      // Unknown event — ignore
      break;
  }
  await _saveCache();
}

// ── Poll fallbacks (when SSE is down) ────────────────────────────────────────

async function pollStatus() {
  try {
    const [sl, bs] = await Promise.all([
      mcFetch("/api/statusline/compact"),
      mcFetch("/api/branch_status"),
    ]);
    _cache.statusline = sl;
    _cache.branchStatus = bs;
    _cache.lastOk = new Date().toISOString();
    _cache.offline = false;
    await refreshBadge();
    broadcast("STATE_UPDATE", {
      patch: { statusline: sl, branchStatus: bs, offline: false },
    });
  } catch {
    _cache.offline = true;
    await updateBadge(null, "?");
    broadcast("STATE_UPDATE", { patch: { offline: true } });
  }
  await _saveCache();
}

async function pollInbox() {
  try {
    const data = await mcFetch("/api/inbox_status");
    const prev = _cache.inboxPending;
    const count = data?.stale_count ?? data?.pending_count ?? 0;
    _cache.inboxPending = count;
    if (count > 0 && count > prev) {
      try {
        await chrome.notifications.create("mc_inbox_stale_" + Date.now(), {
          type: "basic",
          iconUrl: "icons/icon48.png",
          title: "MC Inbox",
          message: `${count} pending message${count > 1 ? "s" : ""} in Mission Control`,
          priority: 1,
        });
      } catch (e) {
        // ignore
      }
    }
    await refreshBadge();
  } catch {
    // offline — leave count unchanged
  }
  await _saveCache();
}

// ── ZERO: ask_page / rewrite streaming helpers ───────────────────────────────
//
// Both endpoints return text/event-stream on the POST response body. We
// parse the stream line-by-line and relay either to the side panel (for
// ask_page) via chrome.runtime.sendMessage, or to the sender tab's
// content script (for rewrite) by resolving a promise with the final text.

async function _parseZeroStream(resp, onDelta) {
  if (!resp || !resp.ok || !resp.body) {
    throw new Error(`ZERO HTTP ${resp && resp.status}`);
  }
  const reader = resp.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let currentEvent = "message";
  let dataBuf = [];
  let aggregated = "";
  let doneReason = null;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, idx).replace(/\r$/, "");
      buffer = buffer.slice(idx + 1);
      if (line === "") {
        if (dataBuf.length) {
          const dataStr = dataBuf.join("\n");
          try {
            const parsed = JSON.parse(dataStr);
            if (currentEvent === "done") {
              doneReason = parsed && parsed.reason;
            } else if (parsed && typeof parsed.delta === "string") {
              aggregated += parsed.delta;
              if (onDelta) onDelta(currentEvent, parsed.delta, aggregated);
            }
          } catch (e) {
            // malformed — skip
          }
        }
        dataBuf = [];
        currentEvent = "message";
        continue;
      }
      if (line.startsWith(":")) continue;
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataBuf.push(line.slice(5).replace(/^ /, ""));
      }
    }
  }
  return { text: aggregated, reason: doneReason };
}

// Endpoint paths. Primary = /api/zero/*. Legacy /api/hermes/* aliases are
// kept on the server side (deprecated, remove in v0.6) and used as fallback
// here only if the primary returns 404.
const ZERO_ASK_PAGE_PATH = "/api/zero/ask_page";
const ZERO_REWRITE_PATH = "/api/zero/rewrite";
const LEGACY_ASK_PAGE_PATH = "/api/hermes/ask_page";
const LEGACY_REWRITE_PATH = "/api/hermes/rewrite";

async function _postZeroStream(primaryPath, legacyPath, body) {
  const base = await getCurrentBackendUrl();
  const headers = await _authHeaders({
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
  });
  // Try primary path first; fall back to legacy only on 404.
  let resp = await fetch(base + primaryPath, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (resp.status === 404) {
    resp = await fetch(base + legacyPath, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  }
  return resp;
}

async function zeroAskPage({ url, title, content, question, streamId }) {
  const resp = await _postZeroStream(
    ZERO_ASK_PAGE_PATH, LEGACY_ASK_PAGE_PATH,
    { url, title, content, question },
  );
  return await _parseZeroStream(resp, (event, delta, aggregated) => {
    if (event === "ask_page_reply") {
      broadcast("ZERO_ASK_PAGE_DELTA", {
        streamId, delta, aggregated,
      });
    }
  });
}

async function zeroRewrite({ selection, action, url }) {
  const resp = await _postZeroStream(
    ZERO_REWRITE_PATH, LEGACY_REWRITE_PATH,
    { selection, action, url },
  );
  // Rewrite doesn't stream deltas to the side panel — we collect the
  // full text and return it to the content script in one shot so it can
  // replace the selection atomically.
  return await _parseZeroStream(resp, null);
}

// ── Page snapshot (content_script bridge) ────────────────────────────────────

// v0.7.1: restricted URL patterns where content scripts cannot be injected.
// Surfacing these early with a friendly error keeps the 問頁 tab from
// showing the cryptic "Receiving end does not exist" Chrome runtime error.
const _RESTRICTED_URL_RE = /^(chrome|chrome-extension|edge|about|devtools|view-source|file|data):/i;
const _CHROME_STORE_RE = /^https?:\/\/chromewebstore\.google\.com\//i;

function _isRestrictedUrl(url) {
  if (!url) return true;
  if (_RESTRICTED_URL_RE.test(url)) return true;
  if (_CHROME_STORE_RE.test(url)) return true;
  return false;
}

async function _programmaticSnapshot(tabId) {
  // MV3 dynamic injection fallback — runs when the static content_script
  // isn't loaded (e.g. the tab opened before the extension was installed,
  // or the page's navigation raced document_idle). Uses the `scripting`
  // permission which is already declared in manifest.json.
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        try {
          const text = (document.body && document.body.innerText) || "";
          const MAX = 50 * 1024;
          const enc = new TextEncoder();
          const bytes = enc.encode(text);
          let body = text;
          if (bytes.length > MAX) {
            const dec = new TextDecoder("utf-8", { fatal: false });
            body = dec.decode(bytes.slice(0, MAX)) + "\n\n[...truncated]";
          }
          return {
            url: location.href,
            title: document.title || "",
            content: body,
            extracted_at: new Date().toISOString(),
          };
        } catch (e) {
          return { error: String(e && e.message || e) };
        }
      },
    });
    const first = results && results[0];
    if (first && first.result && !first.result.error) return first.result;
    throw new Error((first && first.result && first.result.error) || "exec_failed");
  } catch (e) {
    throw new Error(e.message || String(e));
  }
}

async function getActiveTabPageSnapshot() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) throw new Error("no_active_tab");
  const url = tab.url || "";
  // v0.7.1: restricted scheme guard — chrome://, about:, Web Store, etc.
  // Throw a stable error code the side panel can translate into Chinese.
  if (_isRestrictedUrl(url)) {
    throw new Error("restricted_url");
  }
  // Quick host denylist at the background layer for defence-in-depth.
  const denied = /^(https?:\/\/(?:[^/]+\.)?(?:twbank\.com\.tw|ctbcbank\.com|e-sunbank\.com\.tw|cathaybk\.com\.tw|accounts\.google\.com|login\.microsoftonline\.com|line\.me|paypal\.com)\/|https?:\/\/github\.com\/login)/i.test(url);
  if (denied) {
    throw new Error("denylisted_domain");
  }
  // Ask the content script for the snapshot. activeTab permission makes
  // this safe: the content script is already injected on document_idle
  // and the user clicked the extension icon (or the side panel button)
  // to reach this code path.
  //
  // v0.7.1: when the static content_script isn't present (no response or
  // "Receiving end does not exist"), fall back to a one-shot programmatic
  // injection via chrome.scripting.executeScript. This handles tabs that
  // existed before the extension was installed, and pages where the
  // content script hasn't run yet.
  const staticAttempt = await new Promise((resolve) => {
    try {
      chrome.tabs.sendMessage(tab.id, { type: "ZERO_GET_PAGE" }, (r) => {
        const err = chrome.runtime.lastError;
        if (err) {
          resolve({ ok: false, error: err.message || "no_content_script" });
          return;
        }
        if (r && r.ok && r.snapshot) resolve({ ok: true, snapshot: r.snapshot });
        else resolve({ ok: false, error: (r && r.error) || "snapshot_failed" });
      });
    } catch (e) {
      resolve({ ok: false, error: e.message || "send_failed" });
    }
  });
  if (staticAttempt.ok) return staticAttempt.snapshot;
  // Fallback path — MV3 dynamic injection.
  try {
    return await _programmaticSnapshot(tab.id);
  } catch (e) {
    // Preserve stable error codes; wrap anything unexpected.
    const msg = String(e && e.message || e);
    if (/cannot\s+access|cannot be scripted|Missing host permission/i.test(msg)) {
      throw new Error("restricted_url");
    }
    throw new Error("snapshot_failed:" + msg);
  }
}

// ── Send command (POST /api/inbox) ───────────────────────────────────────────

async function sendCommand(text) {
  const r = await mcFetch("/api/inbox", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, channel: "extension" }),
  });
  // SSE will push the new entry; still refresh once for safety
  await pollStatus();
  return r;
}

// ── Message router (popup / side panel → background) ────────────────────────

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  (async () => {
    switch (msg.type) {
      case "GET_STATE":
        await _loadCache();
        reply({ ok: true, cache: _cache });
        break;

      case "GET_BACKEND_INFO": {
        const base = await getCurrentBackendUrl();
        const token = await getMcToken();
        reply({
          ok: true,
          base,
          has_token: !!token,
          token_len: token ? token.length : 0,
        });
        break;
      }

      case "SET_MC_TOKEN": {
        const r = await setMcToken(msg.token || "");
        if (r.ok) {
          // Invalidate the cached base URL so next fetch re-probes LAN
          // with the fresh token on hand.
          await getCurrentBackendUrl({ force: true });
        }
        reply(r);
        break;
      }

      case "SET_BACKEND_URL": {
        await setBackendUrl(msg.url, msg.kind || "tunnel");
        // Force SSE reconnect against new URL
        try { if (_sseController) _sseController.abort(); } catch (_e) { /* ignore */ }
        reply({ ok: true });
        break;
      }

      case "REFRESH":
        await Promise.all([pollStatus(), pollInbox()]);
        ensureSSE();
        reply({ ok: true, cache: _cache });
        break;

      case "SEND_COMMAND":
        try {
          const r = await sendCommand(msg.text);
          reply({ ok: true, result: r });
        } catch (e) {
          reply({ ok: false, error: e.message });
        }
        break;

      case "ZERO_GET_PAGE_SNAPSHOT":
      case "HERMES_GET_PAGE_SNAPSHOT": // legacy alias — remove after v0.6
        try {
          const snap = await getActiveTabPageSnapshot();
          reply({ ok: true, snapshot: snap });
        } catch (e) {
          reply({ ok: false, error: e.message });
        }
        break;

      case "ZERO_ASK_PAGE":
      case "HERMES_ASK_PAGE": // legacy alias — remove after v0.6
        // Side panel → background. We fetch the page snapshot, then
        // POST-stream it to the MC server. Deltas are broadcast back to
        // the side panel via ZERO_ASK_PAGE_DELTA (legacy HERMES_* also emitted).
        try {
          const snap = msg.snapshot || (await getActiveTabPageSnapshot());
          const result = await zeroAskPage({
            url: snap.url,
            title: snap.title,
            content: snap.content,
            question: msg.question || "",
            streamId: msg.streamId || "default",
          });
          broadcast("ZERO_ASK_PAGE_DONE", {
            streamId: msg.streamId || "default",
            text: result.text,
            reason: result.reason,
          });
          reply({ ok: true, text: result.text, reason: result.reason });
        } catch (e) {
          broadcast("ZERO_ASK_PAGE_DONE", {
            streamId: msg.streamId || "default",
            text: "",
            reason: "error",
            error: e.message,
          });
          reply({ ok: false, error: e.message });
        }
        break;

      case "ZERO_REWRITE":
      case "HERMES_REWRITE": // legacy alias — remove after v0.6
        // Content script → background. Fire-and-collect: we stream the
        // Anthropic reply on the server side but surface only the final
        // text to the content script so it can atomically replace the
        // selection at the caret.
        try {
          const payload = msg.payload || {};
          const result = await zeroRewrite({
            selection: payload.selection || "",
            action: payload.action || "rewrite",
            url: payload.url || "",
          });
          reply({ ok: true, text: result.text, reason: result.reason });
        } catch (e) {
          reply({ ok: false, error: e.message });
        }
        break;

      default:
        reply({ ok: false, error: "unknown_type" });
    }
  })();
  return true; // keep channel open for async reply
});

// ── Alarm setup ──────────────────────────────────────────────────────────────

async function setupAlarms() {
  await chrome.alarms.clearAll();
  chrome.alarms.create(POLL_STATUS_ALARM, { periodInMinutes: STATUS_POLL_MINS });
  chrome.alarms.create(POLL_INBOX_ALARM, { periodInMinutes: INBOX_POLL_MINS });
  chrome.alarms.create(SSE_WATCHDOG_ALARM, { periodInMinutes: SSE_WATCHDOG_MINS });
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === POLL_STATUS_ALARM) pollStatus();
  if (alarm.name === POLL_INBOX_ALARM) pollInbox();
  if (alarm.name === SSE_WATCHDOG_ALARM) ensureSSE();
});

// ── Keyboard command: open ZERO rewrite toolbar ──────────────────────────────

if (chrome.commands && chrome.commands.onCommand) {
  chrome.commands.onCommand.addListener(async (command) => {
    // Accept both new "zero-open-toolbar" and legacy "hermes-open-toolbar"
    // in case a stale cached profile still holds the old binding.
    if (command !== "zero-open-toolbar" && command !== "hermes-open-toolbar") return;
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) return;
      chrome.tabs.sendMessage(tab.id, { type: "ZERO_OPEN_TOOLBAR" }, () => {
        // swallow lastError for tabs without content script (chrome://)
        void chrome.runtime.lastError;
      });
    } catch (e) {
      // ignore
    }
  });
}

// ── Side panel toggle ─────────────────────────────────────────────────────────

chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ windowId: tab.windowId }).catch(() => {
    chrome.tabs.create({ url: "http://localhost:7878/" });
  });
});

// ── Boot ─────────────────────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch(() => {});
  await setupAlarms();
  await pollStatus();
  await pollInbox();
  ensureSSE();
});

chrome.runtime.onStartup.addListener(async () => {
  await _loadCache();
  await setupAlarms();
  await pollStatus();
  ensureSSE();
});

// Initial run on service-worker activation
(async () => {
  await _loadCache();
  await pollStatus();
  ensureSSE();
})();
