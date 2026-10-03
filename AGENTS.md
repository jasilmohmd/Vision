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
