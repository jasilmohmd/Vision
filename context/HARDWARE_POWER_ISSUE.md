# S3 power brownouts during real tracking - 2026-10-04

Actual `logs/vision-COM19.log` contains repeated `E BOD: Brownout detector was
triggered`, followed by ROM boot/reinitialization. Recent sequence includes
stream open + moves52/79,52/80,52/82, then brownout; later stream open + move48/82,
then another brownout. Voice command was accepted on Uno Q; camera stream and
/move then timed out because board repeatedly reset/unavailable. The precise
weak supply/cable/connection/load remains unmeasured; don't guess its component.

Official Espressif meaning: brownout detector resets chip when supply falls
below safe level (https://docs.espressif.com/projects/esp-idf/en/release-v5.2/esp32s3/api-guides/fatal-errors.html).
No firmware edit/flash or brownout-detector bypass done. No timeout increase.

Hardware-team next action follows SOFTWARE_PLAN Gate A:
- Verify S3/servo shared ground, continuous rails and sound power connections.
- Check short/thick USB feed from planned supply, C2 470uF by S3 feed and C1
  470uF by servo headers, correct polarity, and mechanically free bracket.
- Measure S3 5V pin under both-servo load; project acceptance about >=4.6V.
  This project feed criterion is not the chip's internal brownout threshold.
- Report actual supply topology/measurement; correct hardware first, then repeat
  controlled camera/motion/stream checks with no reset and resume live tracking.

User's current power topology requested asynchronously, reply pending. Stop
integration until corrected; earlier Gate A readiness does not negate observed
failure. Existing software source129tests pass, physical acceptance now failed.

Runtime already ended with Ctrl+C/exit0 when checked; app/8080/5005 absent.
Signaled owned serial readers to stop; no background auto-restart configured.
C3 standalone USB logging issue is separate in FIRMWARE_AUDIO_ISSUE.md.


## Confirmed supply description correction - 2026-10-04
User reports power bank -> S3 USB -> S3 5V/GND -> both servos. The initial
PD-charger description was corrected. Servos share S3 ground and USB power path.
Current voltage stability/brownout recurrence is untested; cause unresolved.
No new hardware check or wiring change. Measure under camera/both-servo load
when testing resumes; do not infer a defective power bank from old reset logs.
