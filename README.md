# Hands-free photography rig

Follow SOFTWARE_PLAN.md for the interface contract and phase requirements.
Read STATUS.md before resuming work. Future-phase files are labeled placeholders.

## Phase 0 setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyyaml pytest
.\.venv\Scripts\python.exe -m app.main --help
.\.venv\Scripts\python.exe -m app.main --config config.yaml
.\.venv\Scripts\python.exe -m pytest
```

Only PyYAML and pytest are needed for Phase 0. The requirements files list
later laptop and Uno Q dependencies. Ultralytics is laptop-only for export;
never install it or PyTorch on the Uno Q.

The CLI supports --config, --mock, and --mic laptop|udp. In Phase 0 it validates
configuration and exits. Hardware, mocks, voice, and gallery runtime are pending.
Relative photos_dir values resolve beside the selected YAML file. IP defaults
are examples awaiting confirmation at Gate 0. Ports follow the source contract.
