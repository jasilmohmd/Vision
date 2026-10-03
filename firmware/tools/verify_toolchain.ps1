param(
    # Generic architecture probe only; actual camera board/profile awaits F0.
    [string]$S3Fqbn = 'esp32:esp32:esp32s3:PSRAM=opi',
    [string]$C3Fqbn = 'esp32:esp32:esp32c3:CDCOnBoot=cdc'
)
$ErrorActionPreference = 'Stop'
$fwRoot = Split-Path $PSScriptRoot -Parent
$fwCli = Join-Path $fwRoot '.toolchain/arduino-cli.exe'
if (!(Test-Path -LiteralPath $fwCli)) { throw 'Install portable arduino-cli in firmware/.toolchain first.' }
$fwPreviousUser = $env:ARDUINO_DIRECTORIES_USER
try {
    $env:ARDUINO_DIRECTORIES_USER = Join-Path $fwRoot '.toolchain/user'
    foreach ($fwTarget in @(@{Name='s3'; Fqbn=$S3Fqbn}, @{Name='c3'; Fqbn=$C3Fqbn})) {
        Write-Host "Compile-only probe: $($fwTarget.Fqbn)"
        & $fwCli compile --fqbn $fwTarget.Fqbn --warnings all --build-path (Join-Path $fwRoot ".build/$($fwTarget.Name)") (Join-Path $fwRoot 'toolchain_probe')
        if ($LASTEXITCODE -ne 0) { throw "Compile failed for $($fwTarget.Fqbn)" }
    }
} finally {
    $env:ARDUINO_DIRECTORIES_USER = $fwPreviousUser
}
