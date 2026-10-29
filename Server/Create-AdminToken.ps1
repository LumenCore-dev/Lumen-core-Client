param([string]$Path = (Join-Path $PSScriptRoot 'data/admin-token.txt'))
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Path) { throw 'Admin token already exists. Keep the existing token.' }
$directory = Split-Path -Parent $Path
if ($directory) { [void](New-Item -ItemType Directory -Force -Path $directory) }
$bytes = New-Object byte[] 32
$random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $random.GetBytes($bytes) } finally { $random.Dispose() }
$token = -join ($bytes | ForEach-Object { $_.ToString('x2') })
[System.IO.File]::WriteAllText($Path, $token, [System.Text.Encoding]::ASCII)
Write-Output "Admin token created: $Path"
