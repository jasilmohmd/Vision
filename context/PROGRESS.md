# Progress ledger

## Firmware Session B - 2026-10-04

User requested FIRMWARE_PLAN.md work and approved shared context updates.
F0: portable Arduino CLI 1.5.1 checksum verified, existing ESP32 core 3.3.11
reused, ESP32Servo 3.2.1 and Adafruit NeoPixel 1.15.5 installed locally.
Firmware scaffold, ignore rules, placeholder secrets and compile-only probe
created. Generic S3 and C3 compilation passed with upstream library warnings.
Exact camera board/profile, pins, IPs/ports and F0 DONE remain pending.
F0 is not complete; no F1 work, upload, commit or push. Software progress below
is preserved. No app tests rerun for firmware scaffolding.

Updated: 2026-10-04T01:04:13+05:30 (Asia/Calcutta).

| Phase | State | Remaining acceptance |
| --- | --- | --- |
| 0 Scaffold/config/contract | Complete; de1dfad | None |
| 1 Laptop vision | Complete; 891274f | None |
| 2 Laptop voice | Headset live check passed; uncommitted | Accept headset setup or run original laptop-mic/distance check |
| 3 Control/mocks/gallery | Not started | All planned checks |
| 4 Firmware | Skipped by Session A; owned by Session B | Independent F0-F5 checks; no firmware evidence yet |
| 5 Uno Q with mocks | Not started | Gate 0 first; all checks |
| 6 Real camera | Not started | Gate A first; all checks |
| 7 Real voice | Not started | Gate B first; all checks |
| 8 Robustness/autostart | Not started | Gate C first; all checks |
| 9 Demo/final checks | Not started | All checks; final rehearsal gate |

## Hardware stops

No gates reached or acknowledged. After Phase 3 acceptance, skip software
Phase 4 and reach Gate 0 / GATE 0 DONE.
After Phase 5: Gate A / GATE A DONE. After Phase 6: Gate B / GATE B DONE.
After Phase 7: Gate C / GATE C DONE. After Phase 9: final rehearsal.
Print the exact checklist from SOFTWARE_PLAN.md when reaching a gate; never
paraphrase it from this index or work ahead past it.

## Work history

### 2026-10-03 - Phase 0

Created repository scaffold, config, requirements, CLI and 15 tests. Initial
sandbox/network errors blocked dependency installation; user installed PyYAML
and pytest. Approved escalated execution later allowed verification and commit.
CLI and tests passed. Commit de1dfad. User configured GitHub origin afterward.

### 2026-10-04 - Phase 1 implementation

Implemented detector, face wrapper, tracking, export/download tools, demo,
benchmark, tests and environment documentation. Downloaded/exported models.
23 tests passed. Headless webcam checks ran for person and face. The longer
100-frame webcam benchmark tracked a person in all frames. At that time, human smoothness
acceptance was pending; user said the demo was not run yet.
There was no Phase 1 commit or Phase 2 implementation at that point.

### 2026-10-04 - Durable context rule

User requested a context folder covering the project and a mandatory update
before every commit. Added README/index, HANDOFF, PROJECT, DECISIONS, PROGRESS
and TESTING documents; updated root AGENTS/README/STATUS. Documentation checks
are recorded in TESTING. At that point this work was uncommitted alongside Phase 1, with the phase
acceptance boundary in force. See the completion entry below for the final state.

## Phase 1 completion and commit

On 2026-10-04, after viewing the webcam preview and moving, user confirmed:
"Yes?tracking is smooth and offsets change". This passes the remaining visual
acceptance check. Previously recorded automated checks and benchmark passed.
Context and STATUS were updated before preparing the required Phase 1 commit:
`phase 1: laptop vision and tracking`. Resolve the real hash from git log after
creation. Phase 2 has not started. No remote push is included.

## 2026-10-04 - Phase 2 implementation

User started Phase 2 after Phase 1 commit 891274f. Implemented exact command
parser, laptop/UDP PCM audio sources, confidence-gated Vosk event recognizer,
voice demo and guided acceptance checklist. Installed Vosk/sounddevice locally.
70 tests passed; real model contains every grammar word; silence emitted no
events; laptop mic produced correctly sized PCM without overflows. Finite UDP
and laptop demos ran successfully. No raw audio saved. Live 19-command recognition
from 0.5-1 m plus background-chatter acceptance remains pending. No Phase 2 commit;
Phase 3 not started. Context updated while waiting for that evidence.

User subsequently confirmed the live checklist has not been run yet.
All 70 tests pass; incomplete-checklist reporting verified. No phase commit.

## 2026-10-04 - Updated plans / separate firmware session

Reviewed updated SOFTWARE_PLAN.md and FIRMWARE_PLAN.md at user request.
Section 2 contract unchanged. Session A no longer owns firmware Phase 4 or
flashing/check-tool implementation. Session B owns all firmware/ and independent
F0-F5 work. Revised Gates A/B depend on B's F2/F3 completion and actual IPs;
Gate 0 is network/Uno Q readiness. Recorded review findings in PLAN_REVIEW.md.
No implementation or firmware changes in this review. Phase 2 live acceptance
still pending; no Phase 3, commit or push. HARDWARE_PLAN.md absent.

## Live microphone check launched (2026-10-04)

User authorized the check. Opened a visible console running demo_voice with
AMD mic device 3, --checklist --seconds 600 and summary-only report at
logs/phase2-live-voice-check.json. Await all 19 commands, 20-second real chatter
with zero command events, and user confirmation of 0.5-1 m distance. No raw
audio saved. No Phase 2 commit or Phase 3 work until acceptance passes.

## Live voice check retry (2026-10-04)

User reported the first console did not run properly and requested a restart;
no specific error/phrase supplied yet. Closed only the identified first voice
workers/console to release the mic. Launched a new visible console titled
Vision - Phase 2 live voice check (console PID 24896 at launch), with clear
instructions and unbuffered output. Verified voice worker is running; Vosk
startup diagnostics show model/grammar loading, no failure at inspection.
Current result: logs/phase2-live-voice-retry.json. Startup diagnostics:
logs/phase2-voice-retry-startup.log. Launcher: logs/launch-voice-check.ps1.
All are ignored local test artifacts. This retry supersedes the previous
live-check console; wait for its report plus distance/chatter confirmation.
No acceptance pass, phase commit or Phase 3 work has been recorded.

## Microphone selection diagnosis (2026-10-04)

User reported no recognition and said headphones were in use. Verified the
running checklist used device 3 (AMD laptop array), not the headphones. Newly
available headset: boAt Rockerz 255 Pro+, device 4 (MME); 16 kHz mono int16
format check passed. Vosk model/grammar startup showed no error. Stopped only
the owned laptop-mic workers/console and switched the diagnostic to device 4.
The earlier timeout/incomplete runs have not passed acceptance.

Added demo --levels (normalised RMS/peak once per second) and explicit input
device display. Full regression after change: 70 passed. No threshold change.
Headset diagnostic console PID 25368 at launch, --device 4 --levels --checklist,
600-second limit. Summary logs/phase2-headset-diagnostic.json; startup diagnostics
logs/phase2-headset-startup.log. Both ignored; no raw audio saved. Await user
report of input levels and heard/command events. This supersedes previous active
laptop check consoles; verify process IDs before any cleanup.

Headset diagnosis does not satisfy the specified laptop microphone check from
0.5-1 m. After fixing input/recognition, return to verified laptop-mic acceptance
or obtain an explicit user-approved acceptance change. No Phase 2 commit or
Phase 3 advancement; no firmware edits.

## Headset live check result (2026-10-04)

User reported all checks passed. Verified logs/phase2-headset-diagnostic.json:
19/19 supported commands, zero missing commands, 20.09 seconds background test,
zero background command events, confidence threshold 0.7, device 4 boAt headset,
checks_passed true. No raw audio recorded. Latest full regression remains 70 passed.

The headset result is passing evidence for that setup. Original built-in laptop
microphone at 0.5-1 m remains unverified. Asked the user to choose accepting the
headset setup as Phase 2 acceptance or running the original mic/distance check.
Await that answer before phase completion/commit. No Phase 3 work. Firmware B
has its own new files; none edited or staged in this task. Earlier active-run
entries above are historical and superseded by this completed headset result.
