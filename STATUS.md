# Project status

## Firmware Session B - 2026-10-04

F0 started at user request; toolchain/scaffold ready, both generic compile probes
passed. Board facts and F0 DONE pending; F1-F5 not started. No flashing or
firmware commit. See firmware/STATUS.md. User allowed shared context updates.
That firmware paragraph is a pre-commit snapshot: preparation committed as
993e3d5; F0 board facts remain pending. Current software result is below.

- Phase 0: complete and committed (de1dfad).
- Phase 1: complete and committed (891274f); all acceptance checks passed.
- Phase 2: complete for accepted temporary headset setup; 70 tests passed; ready for user commit.
- Updated: 2026-10-04T01:17:16+05:30 (Asia/Calcutta).

## What works

- YOLOv8n exported on the laptop to models/yolov8n.onnx: static FP32 input
  (1, 3, 320, 320), raw output (1, 84, 2100), opset 17, no embedded NMS.
- ONNX Runtime detector with RGB letterboxing, class filtering, NMS and
  inverse-coordinate mapping/clipping. No PyTorch runtime imports.
- YuNet FaceDetectorYN with matching detection tuples.
- CSRT tracking with KCF fallback, per-frame updates, configured detection
  interval, immediate re-detection after failure and nearest-box association.
- Per-frame target box or None, with normalised dx/dy (positive right/down).
- Webcam/video demo with overlay, printed offsets and headless option.
- Detector-only and detector+tracker benchmark with optional JSON report.
- Cross-platform model downloader and shell wrapper. YuNet and Vosk small
  English models downloaded locally. Models are ignored by Git.
- Runtime uses opencv-contrib-python (headless contrib for Uno Q) so CSRT/KCF
  are available. Export dependencies are separate in requirements-export.txt
  to prevent simultaneous installation of conflicting cv2 distributions.

## Verification

- Python 3.13.5, OpenCV contrib 4.14.0, ONNX Runtime 1.30.0, NumPy 2.5.3.
- python -m pytest: 23 passed (15 config/CLI tests plus 8 vision tests).
- Vision tests cover letterboxing, inverse box mapping, class filtering/NMS,
  clipping, offset signs/bounds, detection cadence, identity association,
  failure recovery, real CSRT/KCF initialization, fallback and missing models.
- YOLO export succeeded; official bus sample yielded 3 people with YOLO and
  2 faces with YuNet. Both real models loaded and ran successfully.
- Webcam headless smoke: person tracking over 10 frames, face tracking over
  3 frames; boxes and offsets printed.
- Main, demo, export and download CLI help checks passed.
- pip check: no broken requirements. git diff --check: passed.

## Laptop webcam benchmark

Source 0, person, CSRT, 320x240, detect_every_n_frames=5; CPU processing only,
excluding camera acquisition and model load (same cached frames for both runs):

- Frames: 100.
- Detector-only: 68.39 FPS.
- Detector+tracker: 19.13 FPS.
- Detected frames: 100/100.
- Tracked frames: 100/100.
- Local report: models/benchmark-webcam.json (Git ignored).

## Pending and known issues

- Visible person demo passed on 2026-10-04. User confirmed smooth tracking
  and changing offsets. Numerical logs showed tracking without errors. Command:
  .\.venv\Scripts\python.exe -m tools.demo_vision --target person
- Phase 1 acceptance and commit complete: 891274f.
- Phase 2 is implemented; live 19-command/chatter acceptance at 0.5-1 m is pending.
- Phase 3 has not started. Software Phase 4 is skipped/owned by separate Session B.
- Later software phases have not started; firmware progress is not confirmed here.
- Actual network addresses remain unconfirmed for Gate 0; board/pin facts belong
  to Session B Gate F0, and firmware/ is outside this session's edit scope.
- Normal sandbox command runner still fails during setup; verification and
  file changes ran through approved escalated commands.

## Licence

Ultralytics YOLOv8 weights are AGPL-3.0, as flagged in SOFTWARE_PLAN.md.
Ultralytics/PyTorch were used on this laptop only for export. The deployed
vision code uses ONNX Runtime/OpenCV; never install export dependencies on Uno Q.

## Durable session handoff

- context/README.md indexes the handoff, project scope, decisions, progress and
  verification records. Read context/HANDOFF.md first in a new session.
- User requires context updates BEFORE EVERY commit; AGENTS.md records this
  mandatory rule, including documentation-only commits.
- Context files and guidance are included in Phase 1 commit 891274f.
- Context refreshed for Phase 2; no Phase 2 commit until live acceptance passes.

## Phase 2 voice

- Exact typed command parsing and grammar for all 19 wake-word phrases.
- Laptop microphone and UDP PCM sources; bounded jitter queue, packet checks,
  silence on underrun, backlog dropping and resource cleanup.
- Vosk word-confidence/wake-word gate; queued heard, command, low_confidence events.
- Standalone demo and guided 19-command plus 20-second chatter checklist.
- 70 tests passed; real Vosk model/grammar, silence, mic and finite demos verified.
- Default input is a virtual Elgato line; device 3 was the verified AMD mic array.
- Live acceptance command:
  .\.venv\Scripts\python.exe -m tools.demo_voice --device 3 --checklist --report logs/phase2-voice-check.json
- Await user's result/distance confirmation; no raw audio saved, no Phase 3 work.

User confirmed the live checklist has not been run yet. Incomplete-checklist
reporting was verified to fail correctly; final regression remains 70 passed.

## Updated software / firmware plans reviewed

- Reviewed SOFTWARE_PLAN.md changes and FIRMWARE_PLAN.md; shared contract unchanged.
- Session A owns software/mocks/deployment; never edits firmware/. Software Phase 4
  skipped. Session B owns independent firmware F0-F5 and its own hardware checks.
- At software Gates A/B use firmware/tools/check_camera.py and check_voice_unit.py
  after firmware session F2/F3 pass; no flashing or firmware fixes in this session.
- context/PLAN_REVIEW.md records ownership, revised gate dependencies and review
  findings (missing HARDWARE_PLAN.md, context ownership, raw-UDP diagnostics and
  simultaneous UDP consumers). Source plans were reviewed, not edited.
- Phase 2 acceptance remains pending. No implementation/phase advance/commit/push
  was performed for this context update.

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

## Phase 2 accepted / ready for user commit

User accepted the temporary headset workflow after confirming the final
INMP441 -> ESP32-C3 -> UDP -> Uno Q path, and requested commit commands.
Headset result: all 19 commands, 20.09-second background check, zero false events;
latest regression 70 passed. Original built-in-mic 0.5-1 m test unverified; this
is an accepted temporary-setup deviation. Final real-MEMS checks are still due
at firmware F3/software Phase 7; no final hardware acceptance claimed.

Context updated before commit handoff. Intended message: phase 2: laptop voice
and recognition. Current HEAD 993e3d5 (firmware preparation). No software
commit/push by this session; Phase 3 not started. Earlier pending-choice/active
check entries above are historical and superseded by this acceptance record.
