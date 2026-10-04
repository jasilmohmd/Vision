# Phase 5 source/model transfer. Run interactively for SSH/sudo prompts.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z_][A-Za-z0-9_.-]*$')][string]$User,
    [string]$UnoqIp = '10.153.76.45',
    [Parameter(Mandatory=$true)][string]$LaptopIp,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]*$')][string]$RemoteDirectory = 'Vision',
    [switch]$SkipInstall
)
$ErrorActionPreference = 'Stop'
$phase5Root = Split-Path -Parent $PSScriptRoot
$phase5Python = Join-Path $phase5Root '.venv\Scripts\python.exe'
$phase5Logs = Join-Path $phase5Root 'logs'
foreach ($phase5Address in @($UnoqIp, $LaptopIp)) {
    $phase5Parsed = [System.Net.IPAddress]::Parse($phase5Address)
    if ($phase5Parsed.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork) {
        throw 'Use IPv4 addresses for this deployment.'
    }
}
$phase5Peer = '{0}@{1}' -f $User, $UnoqIp
Push-Location -LiteralPath $phase5Root
try {
    & $phase5Python -m deploy.package_unoq --laptop-ip $LaptopIp --unoq-ip $UnoqIp --output $phase5Logs
    if ($LASTEXITCODE -ne 0) { throw 'Packaging failed; no transfer attempted.' }
    $phase5Prepare = 'mkdir -p -- "$HOME/{0}"' -f $RemoteDirectory
    & ssh.exe $phase5Peer $phase5Prepare
    if ($LASTEXITCODE -ne 0) { throw 'SSH setup failed.' }
    & scp.exe (Join-Path $phase5Logs 'phase5-source.tar.gz') (Join-Path $phase5Logs 'phase5-models.tar.gz') ('{0}:{1}/' -f $phase5Peer, $RemoteDirectory)
    if ($LASTEXITCODE -ne 0) { throw 'SCP transfer failed.' }
    $phase5Extract = 'tar -xzf "$HOME/{0}/phase5-source.tar.gz" -C "$HOME/{0}" && tar -xzf "$HOME/{0}/phase5-models.tar.gz" -C "$HOME/{0}"' -f $RemoteDirectory
    & ssh.exe $phase5Peer $phase5Extract
    if ($LASTEXITCODE -ne 0) { throw 'Remote extraction failed.' }
    if (-not $SkipInstall) {
        $phase5Install = 'bash "$HOME/{0}/deploy/install_unoq.sh"' -f $RemoteDirectory
        & ssh.exe -t $phase5Peer $phase5Install
        if ($LASTEXITCODE -ne 0) { throw 'Remote installation/check failed.' }
    }
    Write-Host ('Copied runtime/models to {0}:~/{1}. See deploy/README.md for acceptance.' -f $phase5Peer, $RemoteDirectory)
} finally {
    Pop-Location
}
