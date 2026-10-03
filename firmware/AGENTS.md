# Firmware session (Session B)

Follow ../FIRMWARE_PLAN.md phase by phase. This user request starts Session B;
the root file's Session A ownership clause describes the software session.
Preserve SOFTWARE_PLAN.md section 2. Do not edit app/, root tools/, deploy/,
or config.yaml. Never guess camera pin maps or confirmed addresses.

Stop at each firmware gate and wait for its exact resume phrase. Flash only
with explicit confirmation and a board the user identifies as connected.

Maintain STATUS.md and context/ here. Root shared-context ownership requires
user resolution before a firmware commit; do not waive the root before-commit
maintenance rule. Stage only this session's explicit paths.
