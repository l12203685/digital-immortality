# SOP #123 — Daemon / Human-Session Coordination Protocol

**Domain**: Branch 3.1 (Recursive Distillation) + Branch 3 (Operating Model) — multi-writer concurrency
**Created**: 2026-04-11T UTC (cycle 321 candidate)
**Status**: DRAFT — awaiting Edward ratification
**Backing MDs**: distil114 I3 (human-session vs daemon task boundary); distil116 I3 (git-diff-first discipline); distil118 I3 (structural audit pattern); distil119 I3 (parallel branch push); distil121 I1 (priority-file-lag as cache gap)

---

## Problem this solves

When the recursive daemon and a live Claude Code session both write to the same repo in overlapping windows, three failure modes emerge:

1. **Stale-state collision** — daemon writes `daemon_next_priority.txt` at the start of a cycle; human session writes `memory/recursive_distillation.md` later in the same window; next boot reads the stale priority file and tries to redo already-done work
2. **Structural-write contention** — both try to update `results/dynamic_tree.md`, `staging/quick_status.md`, or `results/daily_log.md` — the 500-line summary docs — without full context, producing either lost edits or corrupt merges
3. **Un-atomic commits** — daemon accumulates 40+ uncommitted lines across multiple files; human session starts new work without `git diff` first; the two sets of changes get tangled in a single commit, losing the ability to trace which came from which writer

**Root behavioral trace**: Cycles 315-318. Daemon wrote distil113/114 as leaf appends but never updated tree. Human session cycle 316 then rewrote tree + committed — discovering 40+ lines of uncommitted daemon drift in `trading/engine.py`. Cycle 317 `daemon_next_priority.txt` said "distil116 DONE" but distil117 was already in HEAD. Distil114 I3 + distil116 I3 + distil118 I3 + distil121 I1 all touched this — this SOP crystallizes them.

---

## Core Principle

**Division of labor by context budget**:
- **Daemon** = low-context, high-frequency, append-only leaf writes
- **Human session** = high-context, low-frequency, structural/packaging writes

Neither writer is superior; they are specialized. The protocol ensures they don't collide.

---

## Write-Type Taxonomy

Before any write, classify it:

| Write type | Files | Who should write |
|---|---|---|
| **Leaf append** | `memory/recursive_distillation.md` (append), `results/*.jsonl` (append), `results/trading_engine_log.jsonl`, `staging/listen/*.md` | Daemon (primary), human session (allowed) |
| **Leaf update** | `staging/quick_status.md` (small fields), `daemon_next_priority.txt`, `results/*_status.json` | Daemon (primary) |
| **Structural rewrite** | `results/dynamic_tree.md`, `results/daily_log.md`, `staging/session_state.md`, `docs/knowledge_product_*.md` (new SOP), `templates/dna_core.md` | Human session ONLY |
| **Source code** | `trading/*.py`, `platform/*.py`, `tools/*.py`, `skills/*` | Human session ONLY |
| **Commit boundary** | `git add` + `git commit` + `git push` | Human session ONLY |

**Kill rule**: Daemon MUST NOT perform structural rewrites, source-code edits, or commits. If the daemon needs to structurally rewrite something, it writes a note in `staging/daemon_requests.md` and lets the next human session package the change.

---

## G0 — Human Session Boot Protocol

Before any new work, the human session MUST run a pre-flight check:

```bash
git status --short
git diff --stat
git show HEAD:memory/recursive_distillation.md | tail -30
cat staging/quick_status.md
cat daemon_next_priority.txt 2>/dev/null || echo "no priority file"
```

**Procedure**:

1. Identify uncommitted daemon drift: files modified but not committed
2. Compare `daemon_next_priority.txt` intent vs `HEAD:memory/recursive_distillation.md` actual state
3. If priority file lags HEAD → trust HEAD, do NOT redo already-committed work
4. Document the delta in `staging/session_state.md` before adding any new work

| State | Action |
|---|---|
| Clean working tree, priority file matches HEAD | Proceed normally |
| Uncommitted drift in `results/` or `staging/` only | Acceptable — package before new work |
| Uncommitted drift in `trading/`, `platform/`, or `tools/` | **STOP** — review, test, commit separately before new work |
| Priority file lags HEAD by ≥1 cycle | Trust HEAD, update priority file, proceed |
| Priority file ahead of HEAD | **STOP** — daemon may have crashed mid-cycle, investigate |

**PASS**: Pre-flight complete and documented → G1

---

## G1 — Write-Classification Gate

Before the session writes to any file, classify the write using the taxonomy above.

**Rule**: Human session may perform any write type. Daemon may only perform leaf-append and leaf-update.

If the session is editing a file normally reserved for structural writes, confirm the session is interactive (human-driven) and not a subagent running under daemon context. Subagents spawned by daemon inherit daemon permissions.

---

## G2 — Atomic Multi-Branch Packaging

When human session touches multiple branches in one session, the packaging rule is:

1. Read `dynamic_tree.md` once at session start
2. Execute branch work in parallel (parallel-branch-push discipline — distil119 I3)
3. Accumulate all changes in working tree
4. **Run `git diff` before the commit** — verify the change set is intended
5. Stage files by name (never `git add -A` — too broad, picks up daemon drift)
6. Single commit with multi-branch summary
7. Push

**Anti-pattern**: Sequential commit-per-branch — loses the atomicity property and multiplies push overhead.

**Anti-pattern**: `git add -A` followed by commit — silently bundles unrelated daemon drift into the commit, poisoning the history.

---

## G3 — Daemon Request Channel

When the daemon encounters work that requires structural/source/commit writes, it appends a request to `staging/daemon_requests.md`:

```
### Request — 2026-04-12T03:15Z — cycle 324
Type: structural | source | commit
File: results/dynamic_tree.md
Reason: Branch 1.1 needs tree node update for SOP#118 G3 recovery
Suggested change: <concrete patch or instruction>
Priority: low | medium | high
Blocker: no | yes (blocks: ...)
```

The next human session reads `staging/daemon_requests.md` at G0, executes or declines each request, and clears the processed entries.

**Kill rule**: Daemon must not make the structural change directly even if "simple". Always route through requests.

---

## G4 — Cache-Lag Tolerance Rule

When two sources disagree, apply the canonical priority order:

1. **HEAD of git** (committed state) — authoritative
2. **Distillation file tail** (append-only) — reliable
3. **quick_status.md** (human-maintained) — recent-intent
4. **daemon_next_priority.txt** (daemon-written) — may lag

**Rule**: If `daemon_next_priority.txt` contradicts the distillation file tail, trust the distillation file. The priority file is a convenience cache, not a source of truth. Never redo work because a cache lagged.

---

## G5 — Post-Session Handoff

Before `/clear` or session end, human session MUST:

1. Commit and push all intended changes (not daemon drift)
2. Update `staging/session_state.md` with: branches touched, artifacts written, next-cycle priority
3. Update `daemon_next_priority.txt` so daemon resumes correctly
4. Clear processed entries from `staging/daemon_requests.md`

**PASS**: Handoff complete → session ends cleanly.

**Failure**: Leaving uncommitted drift + stale priority file = next session boots into confusion.

---

## Kill Condition

This SOP should NOT be applied when:

1. Only one writer is active (pure daemon-only or pure human-only session) — no coordination needed
2. Running from a cold-start with known-clean tree and no daemon history — can skip pre-flight
3. Emergency fix where coordination overhead is more expensive than the risk (but log it)

---

## Anti-Patterns

| Pattern | Why it fails |
|---|---|
| Human session starts new work without `git diff` | Daemon drift gets bundled into the commit, poisoning history |
| Daemon rewrites `dynamic_tree.md` "just to keep it current" | Daemon lacks context; produces lossy summary; overwrites human-session edits |
| `git add -A` or `git add .` in human session | Silently stages daemon drift the human didn't intend to commit |
| Trusting `daemon_next_priority.txt` over HEAD | Priority file is a cache; cache lag is normal, not a signal |
| Running subagents without classifying them as daemon or human | Subagents inherit permissions of their spawner — a daemon-spawned subagent must follow daemon rules |
| Sequential one-file commits in human session | Loses atomicity; fragments multi-branch work into disconnected commits |

---

## Self-Test Scenario

**Scenario**: Edward opens Claude Code at 21:00. Daemon has been running and committed cycles 315, 316, 317 autonomously. `daemon_next_priority.txt` says "distil116 DONE". `trading/engine.py` has 40+ uncommitted lines (daemon added SOP#118 recovery logic). `results/dynamic_tree.md` was last updated at cycle 310.

**Correct behavior (SOP#123 applied)**:
1. G0 pre-flight: `git status` shows `trading/engine.py` modified; `git show HEAD:memory/recursive_distillation.md | tail -10` shows distil117 already committed; priority file lags by 1 cycle
2. Classify the engine.py drift: SOURCE write — must be reviewed, tested, committed separately
3. Commit engine.py changes first with a dedicated commit message
4. Update priority file to reflect HEAD state
5. Only NOW start new work (e.g., cycle 318 distillation + tree update)
6. Package new work atomically, commit, push
7. Handoff: update `session_state.md`, clean daemon_requests

**Failure mode (SOP#123 not applied)**:
- New distillation work piled on top of uncommitted engine.py drift
- `git add -A` bundles everything into one commit
- Commit message says "cycle 318 distillation" but half the diff is SOP#118 recovery logic from 3 cycles ago
- History is poisoned; rollback becomes impossible

---

## Revenue Connection

Coordination overhead directly limits throughput in a multi-agent / daemon+human system. Every collision costs a cycle; every poisoned commit costs a rollback. As Edward scales toward multi-daemon or team operation, SOP#123 becomes the infrastructure protocol that makes parallelism safe.

**Productization**:
- Standalone SOP for teams running Claude Code daemons alongside interactive sessions
- Component of "agent-ops playbook" bundle with SOP#122

---

## Backing MDs & Related SOPs

- **distil114 I3** — human-session-vs-daemon-task-boundary (originating observation)
- **distil116 I3** — git-diff-first discipline
- **distil118 I3** — human-session structural-audit pattern
- **distil119 I3** — parallel-branch-push-as-session-discipline
- **distil121 I1** — daemon-priority-file-lag-as-cache-gap
- **SOP#122** — Gate-Constrained Regime Operating Protocol (sister SOP)
- **SOP#108** — Cold-start drift detection (adjacent: detects drift, SOP#123 prevents it)

---

## Related Files

- `staging/session_state.md` — primary handoff file
- `staging/quick_status.md` — branch state summary
- `staging/daemon_requests.md` — daemon→human request channel (create if missing)
- `daemon_next_priority.txt` — daemon intent cache (may lag)
- `memory/recursive_distillation.md` — append-only source of truth
- `results/dynamic_tree.md` — structural tree (human-write only)
- `platform/recursive_daemon.py` — daemon implementation
