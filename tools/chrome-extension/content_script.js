/**
 * content_script.js — ZERO Console Stage 1 + Stage 2.
 *
 * Responsibilities:
 *   Stage 1: On demand, extract the current page's {url, title, content}
 *            for the side panel's "問頁" tab. We never auto-stream the
 *            page; the side panel asks via chrome.runtime.sendMessage
 *            (type: "ZERO_GET_PAGE" — legacy "HERMES_GET_PAGE" accepted),
 *            and we respond with a trimmed snapshot (≤50 KB body innerText).
 *
 *   Stage 2: Render a lightweight floating rewrite toolbar when the user
 *            selects text inside an <input>, <textarea>, or
 *            [contenteditable]=true. Buttons: ✏️ Rewrite / 📝 Summarize /
 *            🌐 Translate / ✅ Grammar / 💡 Expand. On click we send the
 *            selection to the background service worker, which POSTs to
 *            /api/zero/rewrite (legacy /api/hermes/rewrite fallback) and
 *            streams the reply back; we apply the replacement at the
 *            caret/selection.
 *
 * Safety:
 *   - Denylist honoured up-front (bank / auth / payment sites). If the
 *     current hostname matches the denylist, this script becomes inert.
 *   - Toolbar and page-read only ever run on user-initiated events.
 *   - We never modify the page until an explicit toolbar click arrives.
 */

(() => {
  "use strict";

  // ── Denylist (defence in depth; manifest already excludes these) ─────────
  const DENYLIST = [
    "twbank.com.tw", "ctbcbank.com", "e-sunbank.com.tw", "cathaybk.com.tw",
    "accounts.google.com", "login.microsoftonline.com",
    "line.me", "access.line.me",
    "paypal.com",
  ];
  function hostDenied() {
    const host = (location.hostname || "").toLowerCase();
    if (!host) return true;
    for (const bad of DENYLIST) {
      if (host === bad || host.endsWith("." + bad)) return true;
    }
    // Additional path-level guards
    if (host === "github.com" && location.pathname.startsWith("/login")) return true;
    return false;
  }
  if (hostDenied()) return;

  const MAX_CONTENT_BYTES = 50 * 1024;

  function trimToBytes(str, maxBytes) {
    if (!str) return "";
    const enc = new TextEncoder();
    const bytes = enc.encode(str);
    if (bytes.length <= maxBytes) return str;
    const dec = new TextDecoder("utf-8", { fatal: false });
    return dec.decode(bytes.slice(0, maxBytes)) + "\n\n[...truncated]";
  }

  function extractPageSnapshot() {
    const text = (document.body && document.body.innerText) || "";
    return {
      url: location.href,
      title: document.title || "",
      content: trimToBytes(text, MAX_CONTENT_BYTES),
      extracted_at: new Date().toISOString(),
    };
  }

  // ── Selection utilities ──────────────────────────────────────────────────

  function getActiveEditable() {
    const el = document.activeElement;
    if (!el) return null;
    const tag = (el.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea") return el;
    if (el.isContentEditable) return el;
    return null;
  }

  function getSelectionText() {
    const editable = getActiveEditable();
    if (editable) {
      const tag = (editable.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea") {
        const s = editable.selectionStart ?? 0;
        const e = editable.selectionEnd ?? 0;
        if (e > s) return editable.value.substring(s, e);
        return editable.value;
      }
      const sel = window.getSelection();
      return sel ? String(sel.toString() || "") : "";
    }
    const sel = window.getSelection();
    return sel ? String(sel.toString() || "") : "";
  }

  function replaceSelectionWith(text) {
    const editable = getActiveEditable();
    if (editable) {
      const tag = (editable.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea") {
        const s = editable.selectionStart ?? 0;
        const e = editable.selectionEnd ?? editable.value.length;
        const v = editable.value;
        editable.value = v.substring(0, s) + text + v.substring(e);
        const caret = s + text.length;
        editable.setSelectionRange(caret, caret);
        editable.dispatchEvent(new Event("input", { bubbles: true }));
        return true;
      }
    }
    // contenteditable or plain document selection
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return false;
    const range = sel.getRangeAt(0);
    range.deleteContents();
    range.insertNode(document.createTextNode(text));
    sel.removeAllRanges();
    return true;
  }

  // ── Floating toolbar ─────────────────────────────────────────────────────

  let toolbarEl = null;
  let toolbarBusy = false;
  let lastSelectionSnapshot = { text: "" };

  const ACTIONS = [
    { id: "rewrite", emoji: "✏️", label: "Rewrite" },
    { id: "summarize", emoji: "📝", label: "Summarize" },
    { id: "translate_zh_tw", emoji: "🌐", label: "ZH-TW" },
    { id: "fix_grammar", emoji: "✅", label: "Grammar" },
    { id: "expand", emoji: "💡", label: "Expand" },
  ];

  function ensureToolbar() {
    if (toolbarEl) return toolbarEl;
    const root = document.createElement("div");
    // id kept as "hermes-toolbar" so toolbar.css selectors (#hermes-toolbar)
    // continue to match. Rename planned for v0.6 once CSS is updated.
    root.id = "hermes-toolbar";
    root.setAttribute("data-zero", "toolbar");
    root.innerHTML = ACTIONS.map(
      (a) => `<button data-action="${a.id}" title="${a.label}">${a.emoji}<span>${a.label}</span></button>`
    ).join("") + `<span class="hermes-status" data-role="status"></span>`;
    // Prevent clicks from bubbling to the page (which might collapse sel).
    root.addEventListener("mousedown", (e) => e.preventDefault());
    root.addEventListener("click", onToolbarClick);
    document.documentElement.appendChild(root);
    toolbarEl = root;
    return root;
  }

  function hideToolbar() {
    if (toolbarEl) toolbarEl.style.display = "none";
  }

  function positionToolbarAtSelection() {
    ensureToolbar();
    const rect = computeSelectionRect();
    if (!rect) return false;
    const bar = toolbarEl;
    bar.style.display = "flex";
    bar.style.top = (window.scrollY + rect.top - 38) + "px";
    // Clamp horizontally so it stays in viewport
    const left = Math.max(8, Math.min(window.scrollX + rect.left,
      window.scrollX + window.innerWidth - 320));
    bar.style.left = left + "px";
    return true;
  }

  function computeSelectionRect() {
    const editable = getActiveEditable();
    if (editable) {
      const tag = (editable.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea") {
        const r = editable.getBoundingClientRect();
        return { top: r.top, left: r.left };
      }
    }
    const sel = window.getSelection();
    if (sel && sel.rangeCount > 0) {
      const range = sel.getRangeAt(0);
      const r = range.getBoundingClientRect();
      if (r.width || r.height) return { top: r.top, left: r.left };
    }
    return null;
  }

  function snapshotSelection() {
    lastSelectionSnapshot = { text: getSelectionText() };
    return lastSelectionSnapshot;
  }

  function setStatus(msg, isError) {
    if (!toolbarEl) return;
    const span = toolbarEl.querySelector("[data-role=status]");
    if (!span) return;
    span.textContent = msg || "";
    span.className = "hermes-status" + (isError ? " err" : "");
  }

  async function onToolbarClick(ev) {
    const btn = ev.target.closest("button[data-action]");
    if (!btn) return;
    if (toolbarBusy) return;
    const action = btn.getAttribute("data-action");
    const selection = lastSelectionSnapshot.text || getSelectionText();
    if (!selection) {
      setStatus("no selection", true);
      return;
    }
    toolbarBusy = true;
    setStatus("…thinking");
    try {
      const reply = await chrome.runtime.sendMessage({
        type: "ZERO_REWRITE",
        payload: { selection, action, url: location.href },
      });
      if (reply && reply.ok && typeof reply.text === "string") {
        replaceSelectionWith(reply.text);
        setStatus("done");
        setTimeout(hideToolbar, 600);
      } else {
        setStatus((reply && reply.error) || "failed", true);
      }
    } catch (e) {
      setStatus(String(e && e.message || e), true);
    } finally {
      toolbarBusy = false;
    }
  }

  // ── Selection listeners ─────────────────────────────────────────────────

  function onSelectionChanged() {
    if (toolbarBusy) return;
    const txt = getSelectionText();
    if (!txt || !txt.trim()) {
      hideToolbar();
      return;
    }
    snapshotSelection();
    if (!positionToolbarAtSelection()) hideToolbar();
  }

  document.addEventListener("mouseup", () => setTimeout(onSelectionChanged, 10));
  document.addEventListener("keyup", (e) => {
    // Only react to shift-selection keys to avoid flicker on typing.
    if (e.shiftKey || e.key === "Shift" || e.key === "ArrowLeft" ||
        e.key === "ArrowRight" || e.key === "ArrowUp" ||
        e.key === "ArrowDown" || e.key === "Home" || e.key === "End") {
      setTimeout(onSelectionChanged, 10);
    }
  });
  document.addEventListener("mousedown", (e) => {
    if (toolbarEl && !toolbarEl.contains(e.target)) hideToolbar();
  });

  // Keyboard shortcut (from background.js command dispatch)
  function openToolbarFromShortcut() {
    snapshotSelection();
    if (!lastSelectionSnapshot.text) {
      // Nothing selected — select the full active editable if possible.
      const ed = getActiveEditable();
      if (ed) {
        const tag = (ed.tagName || "").toLowerCase();
        if (tag === "input" || tag === "textarea") {
          ed.select();
        }
      }
      snapshotSelection();
    }
    if (lastSelectionSnapshot.text) positionToolbarAtSelection();
  }

  // ── Message bridge with background / sidepanel ───────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, send) => {
    if (!msg || !msg.type) return;
    switch (msg.type) {
      case "ZERO_GET_PAGE":
      case "HERMES_GET_PAGE": { // legacy alias — remove after v0.6
        const snap = extractPageSnapshot();
        send({ ok: true, snapshot: snap });
        break;
      }
      case "ZERO_OPEN_TOOLBAR":
      case "HERMES_OPEN_TOOLBAR": { // legacy alias — remove after v0.6
        openToolbarFromShortcut();
        send({ ok: true });
        break;
      }
      default:
        break;
    }
    return true;
  });
})();
