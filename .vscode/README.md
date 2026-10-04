# Firmware editor setup

The C/C++ profiles use a shared generated compile database so original S3 and
C3 `.ino` files resolve to their own board compiler settings. Arduino's normal
database describes generated `.ino.cpp` files instead. Headers without a mapped
translation unit use the selected board profile and its SDK response files.

After compiling firmware, refresh the editor database from repository root:

```powershell
./.venv/Scripts/python.exe .vscode/refresh_firmware_intellisense.py
```

For C3 headers select **C/C++: Select a Configuration -> ESP32-C3 SuperMini**.
Then run **C/C++: Reset IntelliSense Database** and **Developer: Reload Window**
if old diagnostics remain. Use the S3 profile when editing standalone S3 headers.
The generated database remains ignored under firmware/.build. No credentials
are read by the refresh script. Do not disable error squiggles to hide problems.
