param(
    [ValidateSet('List','Banlist','Kicklist','Kick','Ban','Unban','Mute','Unmute','Next')][string]$Action = 'List',
    [ValidateRange(1024,65535)][int]$Port = 49180,
    [UInt64]$PlayerId = 0,
    [string]$ProfileKey = '',
    [ValidateSet('all','text','voice')][string]$Channel = 'all',
    [ValidateRange(0,31536000)][int]$Seconds = 0,
    [string]$Reason = 'Admin action',
    [string]$TokenFile = (Join-Path $PSScriptRoot 'data/admin-token.txt'),
    [string]$CertificateFile = (Join-Path $PSScriptRoot "data/lobby-$Port.tls/server.der")
)
$ErrorActionPreference = 'Stop'
if (-not ('Halo4PinnedTls' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Net.Security;
using System.Security.Authentication;
using System.Security.Cryptography.X509Certificates;
public static class Halo4PinnedTls {
    public static SslStream Open(System.IO.Stream socket, byte[] expected) {
        var stream = new SslStream(socket, false, (sender, certificate, chain, errors) => {
            if (certificate == null || (errors & SslPolicyErrors.RemoteCertificateNameMismatch) != 0) return false;
            var actual = certificate.GetRawCertData();
            if (actual.Length != expected.Length) return false;
            int diff = 0; for (int i = 0; i < actual.Length; ++i) diff |= actual[i] ^ expected[i];
            var parsed = new X509Certificate2(actual);
            return diff == 0 && DateTime.UtcNow >= parsed.NotBefore.ToUniversalTime() && DateTime.UtcNow <= parsed.NotAfter.ToUniversalTime();
        });
        stream.AuthenticateAsClient("halo4.local", null, (SslProtocols)12288, false);
        return stream;
    }
}
'@
}
$trustedCertificate = [IO.File]::ReadAllBytes($CertificateFile)
$token = [System.IO.File]::ReadAllText($TokenFile).Trim()
if ($token -cnotmatch '^[a-fA-F0-9]{64}$') { throw 'Invalid admin token file.' }
if ($Reason.Trim().Length -eq 0 -or $Reason.Length -gt 32 -or $Reason -match '[\x00-\x1f]') { throw 'Reason must have 1..32 characters without control characters.' }
$encoded = -join ([System.Text.Encoding]::UTF8.GetBytes($Reason) | ForEach-Object { $_.ToString('x2') })
$command = switch ($Action) {
    'List' { 'LIST' }
    'Banlist' { 'BANLIST' }
    'Kicklist' { 'BANLIST' }
    'Kick' { $target = if ($ProfileKey) { $ProfileKey.ToLowerInvariant() } else { [string]$PlayerId }; if ($target -notmatch '^(?:[a-f0-9]{32}|[a-f0-9]{64}|[1-9][0-9]*)$') { throw 'PlayerId or full ProfileKey/Fingerprint required.' }; "KICK $target 0 $encoded" }
    'Ban' { if ($ProfileKey) { if ($ProfileKey -notmatch '^(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{64})$') { throw 'Full ProfileKey/Fingerprint required.' }; "BANID $($ProfileKey.ToLowerInvariant()) $Seconds $encoded" } else { if ($PlayerId -eq 0) { throw 'PlayerId or ProfileKey required.' }; "BAN $PlayerId $Seconds $encoded" } }
    'Unban' { if ($ProfileKey -cnotmatch '^(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{64})$') { throw 'ProfileKey required.' }; "UNBAN $($ProfileKey.Substring(0,32).ToLowerInvariant())" }
    'Mute' { $target=if ($ProfileKey) { $ProfileKey.ToLowerInvariant() } else { [string]$PlayerId }; if ($target -notmatch '^(?:[a-f0-9]{32}|[a-f0-9]{64}|[1-9][0-9]*)$') { throw 'PlayerId or full ProfileKey/Fingerprint required.' }; "MUTE $target $Channel $Seconds" }
    'Unmute' { $target=if ($ProfileKey) { $ProfileKey.ToLowerInvariant() } else { [string]$PlayerId }; if ($target -notmatch '^(?:[a-f0-9]{32}|[a-f0-9]{64}|[1-9][0-9]*)$') { throw 'PlayerId or full ProfileKey/Fingerprint required.' }; "UNMUTE $target $Channel" }
    'Next' { 'NEXT' }
}
$client = [System.Net.Sockets.TcpClient]::new()
try {
    $client.Connect('127.0.0.1', $Port)
    $stream = $client.GetStream(); $stream.ReadTimeout = 3000; $stream.WriteTimeout = 3000
    $stream = [Halo4PinnedTls]::Open($stream, $trustedCertificate)
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII)
    $writer = [System.IO.StreamWriter]::new($stream, [System.Text.Encoding]::ASCII)
    $writer.NewLine = "`n"; $writer.AutoFlush = $true
    $writer.WriteLine("ADMIN $token")
    $response = $reader.ReadLine()
    if ($response -ne 'OK ADMIN AUTHENTICATED') { throw "Admin authentication failed: $response" }
    $writer.WriteLine($command)
    $response = $reader.ReadLine()
    if ($response -like 'ERR *') { throw $response }
    if ($Action -eq 'List' -and $response -like 'PLAYERS *') {
        $parts = $response.Split(' ')
        for ($i = 2; $i -lt $parts.Length; $i++) {
            $fields = $parts[$i].Split(':'); $hex = $fields[2]
            $nameBytes = for ($j = 0; $j -lt $hex.Length; $j += 2) { [Convert]::ToByte($hex.Substring($j,2),16) }
            [pscustomobject]@{ PlayerId = $fields[0]; ProfileKey = $fields[1]; Name = [System.Text.Encoding]::UTF8.GetString([byte[]]$nameBytes); Fingerprint = if ($fields.Length -gt 3) { $fields[3] } else { '-' }; IP = if ($fields.Length -gt 4) { $fields[4] } else { '-' }; Role = if ($fields.Length -gt 5) { $fields[5] } else { '0' } }
        }
        if ($parts[1] -eq '0') { Write-Output 'No players connected.' }
    } elseif ($Action -in 'Banlist','Kicklist' -and $response -like 'BANLIST *') {
        foreach ($entry in $response.Split(' ') | Select-Object -Skip 2) {
            if (-not $entry) { continue }; $fields = $entry.Split(','); if (($Action -eq 'Kicklist' -and $fields[0] -ne 'kick') -or ($Action -eq 'Banlist' -and $fields[0] -ne 'ban')) { continue }
            $bytes = for ($j=0; $j -lt $fields[3].Length; $j+=2) { [Convert]::ToByte($fields[3].Substring($j,2),16) }
            [pscustomobject]@{ Type=$fields[0]; ProfileKey=$fields[1]; ExpiresUnix=$fields[2]; Reason=[Text.Encoding]::UTF8.GetString([byte[]]$bytes) }
        }
    } else { Write-Output $response }
    $writer.WriteLine('QUIT')
} finally { $client.Dispose() }
