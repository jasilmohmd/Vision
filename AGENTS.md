# Mandatory project instructions

Follow SOFTWARE_PLAN.md phase by phase. Before resuming work, read
context/README.md, context/HANDOFF.md and STATUS.md, then the relevant context
files and phase requirements. Treat context/ as the durable session handoff.

Keep changes within the requested phase; do not implement future phases early.
Run the phase acceptance checks and update STATUS.md before committing.
Honor every hardware gate and never guess board pin maps.

## Critical rule: update context before every commit

Before EVERY commit, including documentation-only commits, update context/ to
accurately describe the state being committed. Always refresh HANDOFF.md,
PROGRESS.md and TESTING.md; update DECISIONS.md and PROJECT.md when relevant.
Keep STATUS.md consistent. Review and include these updates in the same commit.
Do not commit first and promise to update context afterward.

Record completed work, actual test results, pending/unrun acceptance, decisions,
blockers, user instructions and the exact next action. Never claim checks passed
without evidence. Record the existing HEAD and intended message, not an invented
future commit hash. Do not put credentials or private media in context files.

Before ending a session, update the handoff even when no commit is made.
Do not mark a phase complete or start the next phase while acceptance is pending.

## Software session ownership (updated plans)

This session is Session A. Follow the updated SOFTWARE_PLAN.md; never create,
edit, move or delete files inside firmware/. Software Phase 4 is skipped.
Read context/PLAN_REVIEW.md for cross-session dependencies. FIRMWARE_PLAN.md
is implemented only by the separate Session B, with its independent F0-F5
sequence and firmware-only ownership; software phase order does not prevent
that separate session from proceeding. No firmware implementation in Session A.

SOFTWARE_PLAN.md section 2 is the shared contract. Ask the user before changing
it. Never guess unknown IPs or ports. Run firmware-owned checks only at the
appropriate integration gates; report firmware bugs through the user for B.
Shared context must still be updated before every commit; coordinate ownership
for B rather than silently waiving the existing maintenance rule.
