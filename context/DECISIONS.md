# Decisions and constraints

## Firmware Session B authorization - 2026-10-04

User requested starting FIRMWARE_PLAN.md, selecting Session B for this task.
User explicitly answered "Allow shared context updates" to resolve firmware-only
ownership versus root before-commit maintenance. Session B may append root
context/ and STATUS.md while preserving software records. Software implementation
remains owned by A; stage only explicit B paths and its context changes.
Compile probes use generic chip profiles; actual S3 model/PSRAM/pins await F0.
Credentials are entered locally into ignored secrets.h; never put passwords in
chat/context. Confirm actual network addresses before using them.

Updated: 2026-10-04T01:04:13+05:30 (Asia/Calcutta).

## Mandatory user rules

- Work within the requested phase. No future-phase implementation ahead of time.
- Follow every hardware hard stop and wait for its exact resume phrase.
- Update context/ BEFORE EVERY commit, including documentation-only commits.
  This rule was explicitly requested on 2026-10-04 and is recorded in AGENTS.md.
- Keep durable handoff records current when ending a session without a commit.

## Implementation decisions

1. Phase 0: immutable typed dataclass for config; reject unknown keys, invalid
   types/ranges; resolve relative photos_dir beside selected YAML. CLI --config
   overrides the file; --mock/--mic advertise future runtime selections.
2. Phase 1: use YOLOv8n, static FP32 320x320 batch one, opset 17, no embedded
   NMS/simplification. Output (1,84,2100) decoded by ONNX Runtime code. Export
   happens only on laptop; runtime does not import Ultralytics/PyTorch.
3. Use OpenCV contrib >=4.10,<5 for CSRT/KCF instead of the original base OpenCV
   requirements. Use contrib headless on Uno Q. Change was communicated during
   Phase 1. Avoid installing multiple cv2 distributions in one environment.
4. Separate requirements-export.txt/.venv-export from laptop runtime because
   Ultralytics installs base OpenCV. The initial model was exported successfully
   before cleaning the runtime environment; the separate export venv is documented.
5. Python model downloader is the cross-platform implementation; the planned
   .sh entry point wraps it. Vosk is downloaded now per Phase 1 tasks, but no
   voice code is implemented until Phase 2.
6. Demo/benchmark process 320x240 frames. Benchmark preloads the same frames,
   warms detector first, excludes acquisition/model load, and reports target
   coverage so absent targets cannot inflate apparent tracking performance.
7. Highest-confidence initial target, nearest prior box-centre on re-detection.
   Immediate re-detection after tracker failure; missing detections clear target.
8. Phase acceptance includes human observation. Webcam smoke tests and FPS do
   not substitute for smooth visible person tracking.

## Licence

SOFTWARE_PLAN.md flags Ultralytics YOLO weights as AGPL-3.0. Preserve this note
in STATUS.md; using ONNX does not erase the model's licence obligations.

## Unresolved hardware choices

Do not guess board pin maps. Session B obtains board model and confirms pins
at firmware Gate F0. Session A obtains hotspot/Uno Q SSH and confirmed network
addresses at software Gate 0; it no longer implements pin maps or flashing.
Firmware pin comments are plans, not confirmations. No board-specific pin map
or hardware resume phrase has been supplied.

## Runtime and security boundaries

Never install PyTorch or Ultralytics on Uno Q. Firmware hotspot credentials
belong in ignored firmware secrets.h; Session B owns the non-secret example.
Do not put credentials or recordings/photos in context records. No hardware
flashing, deployment, or remote publish has occurred as part of Phase 1.

## Phase 2 decisions

- Immutable Command(action, target, direction, small) carries intent only;
  degrees and camera/control effects belong to Phase 3.
- Exact wake-word parser; no silent "center" alias or unsupported extra words.
- Fixed Vosk grammar: all 19 phrases plus [unk], SetWords(True), 16 kHz.
- Require complete matching word evidence and every confidence >= configured
  threshold (inclusive), finite and <=1. Missing evidence rejects the command.
- Partial camera word emits heard once per utterance; final/flush resets it.
  Empty/[unk] ignored; other rejected non-empty finals emit low_confidence.
- UDP has 3-packet startup jitter and 8-packet maximum by default, 32 ms playout,
  drops oldest backlog and fills underruns with silence. Arrival order only:
  no sequence numbers/timestamps exist in the specified raw PCM contract.
- Do not change system microphone defaults. Device selection belongs to demo CLI;
  AMD device 3 was verified here, while the default virtual line is unsuitable.
- Guided checklist summary stores accepted command coverage and background
  false-command counts only; no audio or background speech transcript is saved.
  Distance and actual chatter still require human confirmation.

## 2026-10-04 - Updated ownership decision

User's updated SOFTWARE_PLAN.md overrides the older software firmware tasks.
Never create/edit/move/delete anything under firmware/ in Session A; skip Phase 4.
FIRMWARE_PLAN.md governs the separate hardware-driven Session B. Read it for
integration, but do not implement it here. Section 2 contract unchanged; stop and
ask user before a change needed by either session. No guessing unknown IPs/ports.
Use firmware/tools/ checks at Gates A/B after B has flashed and passed F2/F3.
Report firmware defects via the user for B. Preserve before-every-commit context
rule; do not silently resolve B's firmware-only/root-context conflict.

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
