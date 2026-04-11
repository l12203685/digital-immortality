# Pending Sign-Off Batch

> Auto-managed by tools/sign_off_manager.py — last updated 2026-04-11 16:10 Taipei
> Default action = proceed. Stop pattern = Edward rejects.
> AUTO decisions auto-apply after their timer. ESCALATE decisions never auto-apply.

## Decision 1: Ratify SOPs #122/#123/#124 from session 2026-04-11
- uid: 59fbb1ed
- Status: PENDING
- Category: AUTO
- Posted: 2026-04-11 16:09 Taipei
- Auto-approve at: 2026-04-12 16:09 Taipei
- Recommendation: Ratify all three SOPs into LYH/agent/sops/ and commit
- Why: They codify lessons from today's session: minimize-edward-actions, minimize-external-services, brain-not-executor. Reversible via git revert.
- Alternatives considered: revert | defer | partial-ratify
- Impact if approved: new SOP docs | memory update | agent behavior adjustment
- Reversibility: high
- One-line dismiss: git -C C:/Users/admin/LYH revert HEAD

## Decision 2: Fly.io artifact deletion (decommission)
- uid: 37bd51e9
- Status: IN_PROGRESS
- Category: AUTO
- Posted: 2026-04-11 16:10 Taipei
- Auto-approve at: 2026-04-12 16:10 Taipei
- Recommendation: Proceed — delete remaining Fly.io artifacts (Dockerfile, fly.toml, deploy scripts)
- Why: Edward already chose GH Actions chained workflow over Fly.io (commit ee6ec51). Cleanup is in flight. No revenue impact; git tracked so reversible.
- Alternatives considered: keep-as-reference | partial-cleanup | full-delete
- Impact if approved: smaller repo | fewer confusing paths | reversible via git
- Reversibility: high
- One-line dismiss: git -C C:/Users/admin/workspace/digital-immortality revert <sha>

## Decision 3: Kill local daemon after 24h Fly/GH parallel validation
- uid: c2df5280
- Status: PENDING
- Category: AUTO
- Posted: 2026-04-11 16:10 Taipei
- Auto-approve at: 2026-04-12 16:10 Taipei
- Recommendation: Stop the local recursive_daemon.py process once GH Actions chained workflow has run clean for 24h in parallel
- Why: GH Actions workflow is cloud-native and matches zero-local-dependency goal. Local daemon is redundant once GH proves stable. Parallel verification period ensures no regression. Trivially reversible (just relaunch local daemon).
- Alternatives considered: keep-both | kill-local-immediately | kill-gh-instead
- Impact if approved: lower electricity | simpler ops | less local state
- Reversibility: high
- One-line dismiss: python platform/recursive_daemon.py --cli

## Decision 4: ANTHROPIC_API_KEY secret upload to GH Actions
- uid: 4b7b8c7d
- Status: PENDING
- Category: AUTO
- Posted: 2026-04-11 16:10 Taipei
- Auto-approve at: 2026-04-11 16:10 Taipei
- Recommendation: Use gh auth token to set ANTHROPIC_API_KEY repo secret so GH Actions recursive workflow can use API mode
- Why: GH Actions chained workflow currently falls back to CLI mode because the secret is not set. Uploading is reversible (gh secret delete) and no new external service or cost is incurred.
- Alternatives considered: skip-and-use-cli-only | use-env-file | defer
- Impact if approved: GH Actions can use API mode | faster cycles | reversible
- Reversibility: high
- One-line dismiss: gh secret delete ANTHROPIC_API_KEY -R l12203685/digital-immortality
