# Future firmware features

- [ ] Optional IR head/cheek photo trigger on the C3 SuperMini, OUT GPIO1.
  Deferred by user on 2026-10-04; omitted from this prototype.
  Before enabling: confirm sensor wiring and active polarity with ir_test;
  hold at least 1 second to send ASCII shoot to Uno Q UDP5007, with a 2-second
  lockout. Verify unintended-trigger rejection and the physical head/cheek
  placement with the user. Preserve the shared interface contract.

Prototype scope: voice-triggered photos, camera/servo control, mic and NeoPixel.
Future voice firmware should default USE_IR=0 for this prototype. The existing
ir_test bench sketch is retained for later validation; it has only been compiled,
not physically tested. Re-enable IR only on a future user request.
