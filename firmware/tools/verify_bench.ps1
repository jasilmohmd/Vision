param(
    [string]$Cli = '',
    [string]$S3Fqbn = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=16M',
    [string]$C3Fqbn = 'esp32:esp32:esp32c3:CDCOnBoot=cdc',
    [switch]$IncludeServoStress
)
$ErrorActionPreference = 'Stop'
$fwRoot = Split-Path $PSScriptRoot -Parent
if (!$Cli) {
    $fwPortable = Join-Path $fwRoot '.toolchain/arduino-cli.exe'
    if (Test-Path -LiteralPath $fwPortable) { $Cli = $fwPortable }
    else { $Cli = (Get-Command arduino-cli -ErrorAction Stop).Source }
}
$fwLibraryArgs = @()
$fwLibraries = Join-Path $fwRoot '.toolchain/user/libraries'
if (Test-Path -LiteralPath $fwLibraries) { $fwLibraryArgs = @('--libraries', $fwLibraries) }
$fwTargets = @(
    @{Sketch='servo_sweep'; Fqbn=$S3Fqbn; Build='servo_sweep'; Flags=''},
    @{Sketch='neopixel_test'; Fqbn=$C3Fqbn; Build='neopixel_test'; Flags=''},
    @{Sketch='mic_level'; Fqbn=$C3Fqbn; Build='mic_level'; Flags=''},
    @{Sketch='ir_test'; Fqbn=$C3Fqbn; Build='ir_test'; Flags=''}
)
if ($IncludeServoStress) {
    $fwTargets += @{Sketch='servo_sweep'; Fqbn=$S3Fqbn; Build='servo_sweep_both'; Flags='-DBOTH_TOGETHER=1'}
}
foreach ($fwTarget in $fwTargets) {
    Write-Host "Compile $($fwTarget.Build): $($fwTarget.Fqbn)"
    $fwCompileArgs = @('compile', '--fqbn', $fwTarget.Fqbn, '--warnings', 'all',
        '--build-path', (Join-Path $fwRoot ".build/$($fwTarget.Build)")) + $fwLibraryArgs
    if ($fwTarget.Flags) { $fwCompileArgs += @('--build-property', "compiler.cpp.extra_flags=$($fwTarget.Flags)") }
    $fwCompileArgs += Join-Path $fwRoot "bench/$($fwTarget.Sketch)"
    & $Cli @fwCompileArgs
    if ($LASTEXITCODE -ne 0) { throw "Compile failed: $($fwTarget.Build)" }
}
Write-Host 'PASS: all requested bench sketches compiled. No upload or hardware test performed.'
