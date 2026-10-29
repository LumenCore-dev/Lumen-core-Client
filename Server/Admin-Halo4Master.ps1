param(
    [ValidateSet('Users','Banlist','Ban','Unban','TrustServer','UntrustServer')][string]$Action = 'Users',
    [ValidateRange(1024,65535)][int]$Port = 49175,
    [ValidateSet('fingerprint','ip')][string]$Kind = 'fingerprint',
    [string]$Target = '',
    [ValidateRange(0,10000)][int]$Offset = 0,
    [ValidateRange(0,31536000)][int]$Seconds = 0,
    [string]$Reason = 'Master action',
    [string]$TokenFile = (Join-Path $PSScriptRoot 'data/master.admin-token.txt')
)
$ErrorActionPreference = 'Stop'
$token = [IO.File]::ReadAllText($TokenFile).Trim()
if ($token -cnotmatch '^[a-fA-F0-9]{64}$') { throw 'Invalid master token file.' }
if ($Reason.Trim().Length -eq 0 -or $Reason.Length -gt 32 -or $Reason -match '[\x00-\x1f]') { throw 'Reason must have 1..32 characters without control characters.' }
$encoded = -join ([Text.Encoding]::UTF8.GetBytes($Reason) | ForEach-Object { $_.ToString('x2') })
if ($Action -in 'Ban','Unban') {
    if ($Kind -eq 'fingerprint') { if ($Target -cnotmatch '^[a-fA-F0-9]{64}$') { throw 'Full fingerprint required.' }; $Target=$Target.ToLowerInvariant() }
    else { $address=$null; if (-not [Net.IPAddress]::TryParse($Target,[ref]$address)) { throw 'Valid IP required.' }; $Target=$address.ToString() }
}
$command = switch ($Action) {
    'TrustServer' { if ($Target -cnotmatch '^[a-fA-F0-9]{64}$') { throw 'Full server fingerprint required.' }; "TRUSTSERVER $($Target.ToLowerInvariant())" }
    'UntrustServer' { if ($Target -cnotmatch '^[a-fA-F0-9]{64}$') { throw 'Full server fingerprint required.' }; "UNTRUSTSERVER $($Target.ToLowerInvariant())" }
    'Users' { "USERS $Offset" }
    'Banlist' { 'LIST' }
    'Ban' { "BAN $Kind $Target $Seconds $encoded" }
    'Unban' { "UNBAN $Kind $Target" }
}
$client=[Net.Sockets.TcpClient]::new()
try {
    $client.Connect('127.0.0.1',$Port)
    $stream=$client.GetStream(); $stream.ReadTimeout=3000; $stream.WriteTimeout=3000
    $reader=[IO.StreamReader]::new($stream,[Text.Encoding]::ASCII)
    $writer=[IO.StreamWriter]::new($stream,[Text.Encoding]::ASCII); $writer.NewLine="`n"; $writer.AutoFlush=$true
    $writer.WriteLine("MASTERADMIN $token")
    $response=$reader.ReadLine(); if ($response -ne 'OK MASTER AUTHENTICATED') { throw "Master authentication failed: $response" }
    $writer.WriteLine($command); $response=$reader.ReadLine()
    if ($response -like 'ERR *') { throw $response }
    if ($Action -in 'Users','Banlist') {
        foreach ($entry in $response.Split(' ') | Select-Object -Skip 2) {
            if (-not $entry) { continue }; $fields=$entry.Split(',')
            $hex=if ($Action -eq 'Users') { $fields[2] } else { $fields[3] }
            $bytes=for ($i=0;$i -lt $hex.Length;$i+=2) { [Convert]::ToByte($hex.Substring($i,2),16) }
            $decoded=[Text.Encoding]::UTF8.GetString([byte[]]@($bytes))
            if ($Action -eq 'Users') { [pscustomobject]@{ Fingerprint=$fields[0]; ProfileKey=$fields[1]; Name=$decoded; LastObservedIP=$fields[3] } }
            else { [pscustomobject]@{ Kind=$fields[0]; Target=$fields[1]; ExpiresUnix=$fields[2]; Reason=$decoded } }
        }
    } else { Write-Output $response }
    $writer.WriteLine('QUIT')
} finally { $client.Dispose() }
