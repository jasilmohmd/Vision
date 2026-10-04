param(
    [Parameter(Mandatory=$true)][ValidateSet('udp','ble')][string]$Transport,
    [string]$Port = 'COM18',
    [string]$ExpectedMac = '44:b1:76:17:f5:7c'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$cli = Join-Path $projectRoot 'firmware/.toolchain/arduino-cli.exe'
$esptool = Join-Path $env:LOCALAPPDATA 'Arduino15/packages/esp32/tools/esptool_py/5.3.1/esptool.exe'
if (!(Test-Path -LiteralPath $cli) -or !(Test-Path -LiteralPath $esptool)) {
    throw 'Existing local Arduino toolchain required.'
}
$ErrorActionPreference = 'Continue' # Native stderr may contain progress/warnings.
$identity = & $esptool --port $Port chip-id 2>&1 | Out-String
if ($LASTEXITCODE -ne 0 -or $identity -notmatch 'Chip type:\s+ESP32-C3' -or
    !$identity.ToLower().Contains($ExpectedMac.ToLower())) {
    throw 'Connected chip/MAC did not match the identified C3; no firmware written.'
}
$modeFlag = if ($Transport -eq 'ble') { '1' } else { '0' }
$buildPath = Join-Path $projectRoot "firmware/.build/voice_unit_$Transport"
$libraries = Join-Path $projectRoot 'firmware/.toolchain/user/libraries'
$sketch = Join-Path $projectRoot 'firmware/voice_unit'
$compileLog = Join-Path $projectRoot "logs/switch-$Transport-compile.log"
$uploadLog = Join-Path $projectRoot "logs/switch-$Transport-upload.log"
& $cli compile --fqbn 'esp32:esp32:esp32c3:CDCOnBoot=cdc' --libraries $libraries `
    --build-property "compiler.cpp.extra_flags=-DVOICE_TRANSPORT_BLE=$modeFlag" `
    --build-path $buildPath $sketch *> $compileLog
if ($LASTEXITCODE -ne 0) { Get-Content $compileLog -Tail 15; throw 'Compile failed; firmware unchanged.' }
Get-Content $compileLog -Tail 3
& $cli upload --fqbn 'esp32:esp32:esp32c3:CDCOnBoot=cdc' --port $Port `
    --input-dir $buildPath $sketch *> $uploadLog
if ($LASTEXITCODE -ne 0) { Get-Content $uploadLog -Tail 15; throw 'Upload failed; inspect board before running.' }
Get-Content $uploadLog -Tail 5
Write-Host "C3 mode: $Transport. Match the Uno Q app --mic option to this mode. BLE is experimental."
