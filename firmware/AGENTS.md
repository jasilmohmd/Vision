# Firmware session (Session B)

Follow ../FIRMWARE_PLAN.md phase by phase. This user request starts Session B;
the root file's Session A ownership clause describes the software session.
Preserve SOFTWARE_PLAN.md section 2. Do not edit app/, root tools/, deploy/,
or config.yaml. Never guess camera pin maps or confirmed addresses.

Stop at each firmware gate and wait for its exact resume phrase. Flash only
with explicit confirmation and a board the user identifies as connected.

Maintain STATUS.md and context/ here. User explicitly allowed shared root
context updates; preserve Session A records and refresh root handoff/progress/
testing before each commit. Stage only this session's explicit paths.

On 2026-10-04 the user explicitly directed implementation of all four F1 bench
sketches for team testing while remaining F0 checks are ongoing. This authorizes
F1 preparation without claiming F0 hardware acceptance. Stop at F1 hardware
testing and await F1 DONE; do not implement F2 ahead of those results.

Prototype scope: user deferred IR to TODO.md on 2026-10-04. IR is omitted from
current physical acceptance; future voice firmware defaults USE_IR=0. Retain
the compiled ir_test for later use. User later resumed camera work, acknowledged
F1 DONE and approved DHCP for the first F2 bench check. Gate F2 confirmation is
still required before camera upload; do not mark acceptance passed until tested.
Uno Q setup belongs to the other session; do not operate it here.
