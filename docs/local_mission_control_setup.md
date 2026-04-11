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

## Phase 4b plan

Build a local MCP server at
`C:/Users/admin/.claude/plugins/mission-control/` mirroring the Discord
plugin's pattern (same abstraction: MCP server exposes `mc_fetch_inbox`
/ `mc_reply` / `mc_mark_delivered` tools that the main session polls
on its recursion cycle). See `PHASE_4B_BRIDGE_TODO.md` in the scripts
directory for the full plan. Estimated effort: 1.5–2 hours.

Once Phase 4b is live, the Discord plugin can be deprecated.
