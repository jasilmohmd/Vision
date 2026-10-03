# Software / firmware plan review

Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).
Reviewed SOFTWARE_PLAN.md's working-tree changes against HEAD 891274f, and the
complete FIRMWARE_PLAN.md. This was a documentation review only; no firmware,
software implementation, flashing, toolchain install, commit or push performed.

## User direction

The user will run a separate session for firmware. This session (A) follows the
updated software plan. Session B follows FIRMWARE_PLAN.md. Never implement or
modify firmware in Session A. Refresh project context before every commit.

## Changes adopted for Session A

- SOFTWARE_PLAN.md section 2 remains byte-for-byte equivalent in text to the
  previous contract section. Existing Phase 1/2 interfaces need no change for
  this plan update. Preserve endpoints, ports, PCM format and light states.
- Never guess unknown IPs/ports. Existing config addresses remain illustrative,
  not confirmed board addresses. Ports already specified by the contract are known.
- app/, root tools/, deploy/ and config.yaml belong to Session A.
- All of firmware/ belongs to Session B, including sketches, bench programs,
  status, secret examples and hardware-check tools. Session A must not create,
  edit, move or delete files there, including firmware/AGENTS.md.
- Software Phase 4 is skipped: firmware is developed independently by Session B.
  After Phase 3 acceptance, Session A reaches Gate 0 and waits for GATE 0 DONE.
  It does not compile or implement firmware to satisfy the old Phase 4 wording.
- Canonical hardware check paths are firmware/tools/check_camera.py and
  firmware/tools/check_voice_unit.py. Session A may run them at the appropriate
  gates, but reports firmware bugs to the user for Session B to fix.
- Root tools/check_camera.py and check_voice_unit.py are leftover scaffold
  placeholders, not canonical implementations. They were left untouched.

## Gate / handoff dependencies

| Session A milestone | Required Session B handoff |
| --- | --- |
| Gate 0 -> Phase 5 | Hotspot, Uno Q SSH and confirmed Uno Q/S3/C3 IP plan; no S3 pin-map work in A |
| Gate A -> Phase 6 | camera_head flashed by B, F2 DONE/pass evidence, S3 IP |
| Gate B -> Phase 7 | voice_unit flashed by B, F3 DONE/pass evidence, C3 IP, UNOQ_IP set to Uno Q |
| Gate C -> Phase 8 | Battery assembly and 15-minute stability evidence; firmware F4 diagnostics support |

Software gate phrases are GATE 0 DONE / GATE A DONE / GATE B DONE / GATE C DONE.
Firmware gate phrases are F0 DONE through F4 DONE. One session's gate approval
is not a replacement for another's checklist. Print exact current checklist
from the applicable plan when reached; no gate has been reached or acknowledged.
Session B's F0-F5 work is independent of software phase order and may proceed
while Session A awaits Phase 2 microphone acceptance.

At firmware handoff, obtain board model, confirmed pins/IPs, capture resolution,
I2S SHIFT, colour order, known limits and contract-check evidence from
firmware/STATUS.md or a user-pasted handoff. Do not treat planned values as measured.
No firmware STATUS or hardware evidence existed at this review.

## Review findings to carry into Session B (not implemented here)

1. HARDWARE_PLAN.md is referenced for H0/H1/H2/H3 and wiring gates but is absent
   from the repository. Obtain it before relying on those phase/wiring references.
2. Context ownership initially needed coordination before firmware commits.
   RESOLVED: user explicitly approved shared root context updates for Session B,
   as recorded in firmware/STATUS.md. The following records the original conflict: Root AGENTS.md
   requires root context updates before EVERY commit, while FIRMWARE_PLAN.md
   permits B to edit only firmware/. B must not silently waive either rule. Have
   Session A update shared context before B's commit, or get an explicit user
   resolution for firmware-owned context records. This review grants no exception.
   F0's ignore additions can be firmware/.gitignore (existing root secrets.h rule
   already ignores that basename); no root edit is required for that task.
3. Raw PCM packets have no sequence/timestamp. The firmware check tool can report
   packet counts, gaps or an estimated loss rate, not exact packet loss/reordering.
   Adding headers would change the shared contract and requires user approval.
4. F4 proposes counting UDP audio while the app runs. A second independent bind
   to the same :5005 consumer cannot reliably observe every packet. Coordinate
   app counters/taps or a dedicated test window; don't change the production
   port/payload or assume reuse gives both consumers the entire stream.
   Gate B explicitly stops the app before its audio check, which avoids contention.
5. Firmware /move replies with clamped target angles while servos slew toward
   them. The software client must not equate that acknowledgement with settled
   physical position. /status pan/tilt target-versus-actual semantics need a clear
   handoff; extra heap/PSRAM/reset fields are additive diagnostics. Keep mandatory
   status keys and types; ask before any incompatible contract change.
6. Confirm exact board model/pins at F0 before board-specific compilation or
   pin-map selection. The firmware plan's table is a proposed build, not proof
   that pins or hardware have been confirmed.

## Shared-workspace coordination

Use explicit owned file paths when staging. Do not sweep another session's
unfinished changes into a commit, reset/discard its work or overwrite shared
handoff files without coordination. Inspect status and staged paths immediately
before committing; both sessions share the repo/index if run in this directory.
No autonomous messages were sent to another session; handoff is via these files
and the user, as requested.

## Current software state

Phase 0 complete (de1dfad); Phase 1 complete (891274f). Phase 2 implemented and
uncommitted; latest app evidence is 70 tests passed. Live all-command recognition
at 0.5-1 m/background-chatter acceptance is still unrun. Phase 3 has not started.
The plan review does not pass that acceptance or authorize Phase 3 work.

Current update: Phase 2 temporary headset setup accepted after final-hardware
clarification. Ready for user software commit; no Phase 3 work. Firmware
preparation commit 993e3d5 now exists; earlier plan-review snapshots are historical.
