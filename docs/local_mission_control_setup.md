# Local Mission Control — Setup

> Phase 4a — local web UI that replaces the Discord channel as Edward's
> primary I/O surface and absorbs the GitHub Pages dashboard mirror.
> Runs entirely on Edward's Windows machine, stdlib Python only.

## What it is

One browser window at `http://localhost:7878/` that shows:

1. Header: model / cost / tokens / RAM / R: drive usage
2. Mission Control feed — last 30 events from `results/agent_progress.jsonl`
3. Pending sign-off cards — parsed from `staging/pending_sign_off.md`
4. Backlog top 5 — from `staging/agent_autonomous_backlog.md`
5. Daemon / Trading status — from `results/dashboard_state.json`
6. Input bar (sticky bottom) — text field + quick-command buttons +
   voice stub, writes to `staging/web_inbox.jsonl`

## Where it lives (per-machine, not in this repo)

```
C:/Users/admin/.claude/scripts/mission_control/
├── server.py                 # stdlib HTTP server, ~260 lines
├── index.html                # single-page UI, dark theme, ~385 lines
├── launch.bat                # double-click to start + open browser
└── PHASE_4B_BRIDGE_TODO.md   # how to wire inbox → main session
```

Support files:

```
C:/Users/admin/staging/
├── mc_buttons.json           # quick-command button config (editable)
├── web_inbox.jsonl           # queued user commands (pending_bridge)
└── web_outbox.jsonl          # reserved for Phase 4b replies
```

> These scripts are **not committed** — they're per-machine infrastructure.
> Only this docs file is tracked in the repo.

## Launching

### From Windows Explorer

Double-click `C:/Users/admin/.claude/scripts/mission_control/launch.bat`.
It opens the browser and runs the server in the foreground (Ctrl+C to
stop).

### From terminal

```bash
cd C:/Users/admin/.claude/scripts/mission_control
python server.py
```

Override the port with `MC_PORT=9000 python server.py`.

## Adding new buttons

Edit `C:/Users/admin/staging/mc_buttons.json`:

```json
{
  "buttons": [
    {"name": "my_cmd", "label": "我的指令", "prompt": "execute X", "color": "blue"}
  ]
}
```

Colours: `blue`, `yellow`, `green`. The UI reloads buttons on each
5-second poll — no server restart needed.

## Phase 4a limitations (known)

- **No input injection into the running session.** The web UI writes
  commands to `web_inbox.jsonl` with `status: "pending_bridge"`. Nothing
  consumes them yet. Edward processes them manually, or the main session
  tails the file during idle cycles.
- **Voice button is a stub.** Phase 4b hooks `webkitSpeechRecognition`.
- **No auth.** Binds to `127.0.0.1` only — trusts local machine.

## Phase 4b — SHIPPED 2026-04-11

Phase 4b is live. Three pieces wired together:

### Pieces

- **Voice-bridge watcher** — `C:/Users/admin/GoogleDrive/staging/voice-bridge/watcher.py`
  Polls ntfy topic `edward-vb-x9k4m2p7w1-listen` every 10 s, verifies
  HMAC-SHA256 signatures, writes accepted messages to both
  `voice_input.md` (legacy) and `staging/web_inbox.jsonl` (Mission
  Control). Rejects unsigned/tampered messages. Launches via
  `python watcher.py` — lock file `.watcher_lock`.

- **Mission Control MCP server** — `C:/Users/admin/.claude/plugins/mission-control/server.py`
  Pure stdlib JSON-RPC MCP server (no external deps). Exposes three
  tools to the main Claude Code session:
  - `mc_fetch_inbox(since_ts?)` — pull new pending_bridge entries
  - `mc_reply(text)` — append to web_outbox.jsonl
  - `mc_mark_delivered(ts)` — mark an inbox entry delivered
  Registered in `~/.claude/plugins/installed_plugins.json` as
  `mission-control@local`. `.mcp.json` declares the stdio launch.

- **Listen PWA (listen.html)** — signs each outbound message:
  1. Biometric gate via `navigator.credentials.get()` (Touch ID /
     Windows Hello / Face ID)
  2. HMAC-SHA256 over `text|ts` using the shared secret stored in
     localStorage
  3. POST JSON envelope `{text, ts, sig}` to ntfy

## How to set up biometric lock

Open `https://listen-<yourvercel>.vercel.app/listen.html` on your
phone. First send prompts for the HMAC key — copy it from
`C:/Users/admin/.claude/credentials/voicebridge_hmac.key` and paste
once. The PWA stores it in localStorage. On the next send the browser
will prompt for biometric (fingerprint / face). On iOS Safari 16+ and
Android Chrome 108+ this triggers Touch ID / Face ID / Windows Hello
via the platform authenticator. If biometric is unavailable the PWA
falls back to a confirm dialog — still protected by HMAC + PIN.

## Two security layers explained (plain language)

**Layer 1 — Biometric (on your phone).** When you hit "send" in the
PWA, the phone asks for your fingerprint or face. This makes sure
only _you_ can send, even if someone grabs your unlocked phone. The
browser enforces this — no server-side registry needed for the MVP.

**Layer 2 — HMAC signature (on the watcher).** The PWA computes a
cryptographic fingerprint of your message using a secret only your
phone and the watcher know. If anyone else posts to the ntfy topic
(even guessing the topic name), the watcher sees the signature
doesn't match and drops the message. Combined: biometric stops
unauthorized senders on your phone, HMAC stops unauthorized senders
on the network. The PIN (Layer 0) unlocks the PWA session itself.
Three independent gates — any one failing blocks the message.

## How to deprecate the Discord plugin

Once Mission Control has been used end-to-end for a week without
losing messages, remove the `discord@claude-plugins-official` entry
from `~/.claude/plugins/installed_plugins.json` (or flip it to
`"enabled": false` if the schema supports it). The Discord bot on
Render can keep running as a fallback but stop wiring replies through
it — all I/O goes through Mission Control web UI (home) + listen.html
PWA (phone). Rotate the Discord bot token and revoke its channel
permissions as the final step.

## E2E verification (2026-04-11)

Phone-style message → watcher.py → web_inbox.jsonl → mission-control
MCP fetch → mc_reply → web_outbox.jsonl → `/api/outbox` — all stages
passed. HMAC rejection of unsigned payload also confirmed. See
`C:/Users/admin/GoogleDrive/staging/voice-bridge/watcher.log` for the
live trace.
