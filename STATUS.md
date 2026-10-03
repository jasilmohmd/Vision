# Project status

- Phase: 0 - complete; acceptance checks passed.
- Updated: 2026-10-03 23:44:07 +05:30 (local time).

## What works

- Planned repository layout with clearly labeled future-phase placeholders.
- Separate laptop and Uno Q requirements; export dependencies are laptop-only.
- YAML configuration with contract ports, example IPs, thresholds and servo limits.
- Frozen typed configuration with type/range checks and unknown-key rejection.
- Relative photo paths resolved beside the selected configuration file.
- CLI with --help, --config, --mock and --mic laptop|udp.
- Configuration/CLI tests, setup instructions, and ignore rules for generated
  files, local environments and firmware secrets.

## Verification

Run using .venv on Python 3.13.5 with PyYAML 6.0.3 and pytest 9.1.1:

- python -m app.main --help: passed.
- python -m app.main --config config.yaml: passed.
- python -m pytest: 15 tests passed.
- Tests cover default contract values, configuration overrides, photo path
  resolution, invalid types/ranges and CLI help.

## Pending and known issues

- Phase 1 has not started; vision, voice, control, mocks, gallery, firmware and
  deployment files are placeholders for their specified phases.
- Hardware board models, pin maps and actual network addresses are unconfirmed.
- The normal sandbox command runner currently fails during setup. Phase 0 checks
  ran through approved escalated commands. Git commands use a per-command
  safe.directory setting because the repository was created by the sandbox user;
  no global Git trust setting was changed.
- No known Phase 0 implementation failures.
