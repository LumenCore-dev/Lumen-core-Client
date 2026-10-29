$ErrorActionPreference = 'Stop'
$taskIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$taskPrincipal = [Security.Principal.WindowsPrincipal]::new($taskIdentity)
if (-not $taskPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $PSCommandPath + '"'))
    exit
}
try {
    $taskWireGuard = 'C:\Program Files\WireGuard\wireguard.exe'
    if (Get-Service -Name 'WireGuardTunnel$halo4-windows' -ErrorAction SilentlyContinue) {
        $taskRemove = Start-Process -FilePath $taskWireGuard -WindowStyle Hidden -Wait -PassThru -ArgumentList @('/uninstalltunnelservice','halo4-windows')
        if ($taskRemove.ExitCode -ne 0) { throw 'VPN-Dienst konnte nicht entfernt werden.' }
    }
    Get-NetFirewallRule -Name 'Halo4-VPN-UDP' -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    if (Test-Path -LiteralPath $taskWireGuard) {
        $taskRemove = Start-Process -FilePath 'msiexec.exe' -WindowStyle Hidden -Wait -PassThru -ArgumentList @('/x',('"' + (Join-Path $PSScriptRoot 'wireguard-amd64-1.1.1.msi') + '"'),'/qn','/norestart')
        if ($taskRemove.ExitCode -notin @(0,1605,3010)) { throw "WireGuard konnte nicht entfernt werden: $($taskRemove.ExitCode)" }
    }
    Remove-Item -LiteralPath (Join-Path $PSScriptRoot 'halo4-windows.conf') -ErrorAction SilentlyContinue
    'VPN-Dienst, eigene Firewallregel und WireGuard-Installation entfernt.' | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'VPN-Ruecknahme-Status.txt') -Encoding UTF8
} catch {
    $_.Exception.Message | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'VPN-Ruecknahme-Status.txt') -Encoding UTF8
    exit 1
}
