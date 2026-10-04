# Combined prototype hardware acceptance — deferred

Run only when the user is ready. Automated checks do not substitute for these
observations. IR is omitted. New C3 logging firmware is compiled but not flashed.

1. Confirm S3/servo supply arrangement and shared ground; resolve the recorded
   brownouts. Confirm pan GPIO1, tilt GPIO2 and mechanical clearance. Recheck all
   three DHCP addresses and update local configuration without publishing secrets.
2. Flash the new C3 build with the board confirmed connected. Run sustained audio
   delivery with the serial monitor CLOSED for at least 40 seconds; record packet
   cadence, malformed packets and maximum gaps against the prior 2.513-second
   gap. Run the canonical microphone/light checker, listen to speech and observe
   all eight light states. Never run two receivers on UDP5005 simultaneously.
3. Deploy current software to the Uno Q, stop mocks and duplicate app/stream
   viewers, then launch the normal app with `--mic udp`. Give a clear “Speak now”
   cue for each phrase below and wait for its action before continuing. Check
   recognition logs separately from physical motion. Keep private photos/audio
   in ignored storage.

| Spoken phrase | Observe |
| --- | --- |
| camera track person / face / dog / cat | Test each with that subject visible; follows it, tracking light; missing subject produces search state |
| camera stop tracking | Stops following before manual movement tests |
| camera left / right / up / down | Each axis moves in the correct direction |
| camera a bit left / right / up / down | Each smaller nudge moves correctly |
| camera centre | Returns smoothly to neutral |
| camera shoot | One saved photo, saved light after storage/ACK, full-resolution phone gallery image |
| camera burst | Three saved photos, approximately 400 ms apart |
| camera timer | Countdown of three seconds, then one saved photo |
| camera sleep | Light off; other commands ignored |
| camera wake | Returns to ready and accepts commands |

4. With a tracking target selected, disconnect/reconnect the S3 safely: app and
   gallery stay alive, reconnect light appears, tracking resumes after fresh
   frames and status recovery. Stop C3 delivery for over five seconds: one warning,
   app stays alive; restore delivery and confirm recovery. Check daily JSON logs.
5. After these pass, activate the prepared service using deploy/README.md.
   Power-cycle the three boards in different orders and check the rig becomes
   usable within about 60 seconds without the laptop. Record results and failures
   before closing any software/firmware gate.

Service activation, physical checks and gate completion are pending. Phase9
demo presentation and the future IR feature are outside this coding change.
