# Project context - start here

This folder is the durable handoff for any new session. Read it before changing
code. Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

## Read order

1. ../AGENTS.md - mandatory working and before-commit rules.
2. HANDOFF.md - current state, exact next action, blockers and local setup.
3. ../STATUS.md and PROGRESS.md - acceptance and phase history.
4. PROJECT.md - scope, architecture, contracts and file map.
5. DECISIONS.md - choices that must be preserved and unresolved questions.
6. TESTING.md - commands, last observed results and remaining acceptance.
7. [PLAN_REVIEW.md](PLAN_REVIEW.md) - software/firmware ownership, revised gates and review findings.
8. ../SOFTWARE_PLAN.md - authoritative software tasks and word-for-word gates.
9. ../FIRMWARE_PLAN.md - read for cross-session dependencies; Session B owns implementation.

## Mandatory maintenance

Before EVERY commit, including documentation-only commits:

- Update HANDOFF.md with the current phase, outstanding work, blockers, user
  instructions, relevant Git state and the next action for a new session.
- Update PROGRESS.md with changes, acceptance status and work still pending.
- Update TESTING.md with checks actually run, their results and unrun checks.
- Update DECISIONS.md and PROJECT.md when choices, scope, contracts or file
  responsibilities change. Never invent a decision to fill a gap.
- Update ../STATUS.md and keep it consistent with this folder.
- Review and stage the relevant context updates alongside the implementation.
  Do not commit until context describes the state that commit will contain.

Record the existing HEAD and intended commit message before committing; do not
invent the future commit hash. The next context update can record its real hash.
When stopping without a commit, still leave HANDOFF.md and STATUS.md current.
Do not save credentials, hotspot passwords, tokens or private photo/audio data.
Do not label acceptance complete merely because code or automated tests pass.

The plan defines desired behavior; this folder describes actual progress and
accepted decisions. If records conflict, inspect code/Git and ask only for
information that cannot be verified. Preserve explicit user instructions.

Session A never edits firmware/. Session B has independent F0-F5 phases.
See PLAN_REVIEW.md for the unresolved shared-context maintenance boundary.
