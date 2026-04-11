# Sign-Off Decision Categories

> Determines which decision types auto-approve (AUTO) vs always escalate to Edward (ESCALATE).
> Managed by `tools/sign_off_manager.py`. Updated alongside any new category additions.

Default behavior: **AUTO = auto-approve unless Edward rejects within N hours (default 24h).**
ESCALATE decisions **never** auto-approve — they sit in `pending_sign_off.md` until Edward
explicitly approves or rejects via CLI, and they are batched into a single Discord ping
by `tools/escalation_batcher.py` on a configurable cadence (default 4h).

---

## AUTO — default-approve unless Edward rejects

Operational decisions within the agent's normal working scope. Reversible, non-strategic,
no external spend, no public exposure.

- Code refactoring within existing branch
- SOP additions / ratification
- New tests (unit, integration, e2e)
- Documentation updates (internal docs, READMEs, CLAUDE.md sections)
- Memory / feedback file updates (LYH/memory/*.md, .claude/projects/.../MEMORY.md)
- Dashboard improvements (non-destructive)
- Cron / GH Actions workflow additions
- Bug fixes with clear repro
- Repo / file renames (reversible via git)
- Internal tool builds (tools/*.py, platform/*.py)
- Dead-code cleanup (reversible via git)
- Dependency version bumps (minor/patch only)
- Dynamic tree branch additions
- Strategy backtest additions (trading/*, no execution)

## ESCALATE — always wait for Edward

Decisions with strategic weight, irreversible impact, external cost, or human-facing exposure.

- **DNA core values changes** — anything touching LYH/agent/edward_dna_v*.md
- **Trading mainnet activation** — flipping paper → live, Binance credential usage
- **Spending money / signing up paid services** — any service with recurring cost > $0
- **Sending DMs to Edward's contacts** — outreach execution, not drafting
- **Posting public content** — Twitter/X, blog, LinkedIn, GitHub public gists
- **Deleting non-recoverable data** — raw_inbox/, photos, GDrive originals
- **Anything touching 可可 / FIRE / health priorities directly** — 4-dim framework top-3
- **Git history rewriting** — force push, rebase across published commits, filter-branch
- **Dependency major version bumps** — anything semver major
- **New MCP server / plugin activation** — trust boundary expansion
- **Changes to ~/.claude/settings.json permissions section** — security-sensitive

---

## Classification rule of thumb

If in doubt, ask: "If this goes wrong, can the agent git revert and recover in under
5 minutes with zero external side effects?"

- **Yes** → AUTO
- **No** → ESCALATE

External side effects include: money spent, message sent to a human, public post,
trade executed on mainnet, data deleted that cannot be regenerated.
