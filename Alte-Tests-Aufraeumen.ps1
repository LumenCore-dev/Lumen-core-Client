param([switch]$Preview)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\')
$reports = Join-Path $root 'Source\reports'
$cutoff = (Get-Date).AddHours(-24)

function Assert-SafePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($reports + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Pfad ausserhalb der Testberichte: $full" }
    $item = Get-Item -LiteralPath $full -Force
    while ($item) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Verknuepfung wird nicht angefasst: $full" }
        $item = if ($item.PSIsContainer) { $item.Parent } else { $item.Directory }
    }
}
function Read-TestFiles([string]$Path) {
    Assert-SafePath $Path
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($Path)
    while ($pending.Count) {
        foreach ($entry in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if ($entry.PSIsContainer) { $pending.Push($entry.FullName) } else { $entry }
        }
    }
}
try {
    if (-not (Test-Path -LiteralPath $reports -PathType Container)) { throw 'Source\reports wurde nicht gefunden.' }
    Write-Host 'Pruefe alte, datierte native-network-Testkopien ...'
    Write-Host 'Aktuelle Tests (letzte 24 Stunden) werden ausgelassen.'
    Write-Host 'Spielstaende, Einstellungen und kleine Ergebnisdateien bleiben erhalten.'
    $files = New-Object 'System.Collections.Generic.List[object]'
    foreach ($dir in Get-ChildItem -LiteralPath $reports -Directory -Force) {
        if ($dir.Name -notmatch '^native-network-.*-20\d{6}[a-z0-9-]*$') { continue }
        try { $entries = @(Read-TestFiles $dir.FullName) } catch { Write-Host "Uebersprungen: $($dir.Name)"; continue }
        if ($dir.LastWriteTime -ge $cutoff -or @($entries | Where-Object LastWriteTime -ge $cutoff).Count) { continue }
        # Only bulky copied assets, copied programs and diagnostic output.
        $selected = @($entries | Where-Object { $_.Extension -in @('.h4mesh','.png','.dll','.exe','.pdb','.obj','.ilk','.log','.dmp','.temp') })
        if (-not $selected.Count) { continue }
        $size = ($selected | Measure-Object Length -Sum).Sum
        Write-Host ('{0,8:N2} GiB  {1}' -f ($size / 1GB), $dir.Name)
        foreach ($entry in $selected) { $files.Add($entry) }
    }
    $total = ($files | Measure-Object Length -Sum).Sum
    Write-Host ('Auswahl: {0} Dateien, {1:N2} GiB aufsummierte Dateigroesse.' -f $files.Count, ($total / 1GB))
    Write-Host 'Bei Hardlinks kann der tatsaechlich frei werdende Speicher kleiner sein.'
    if ($Preview -or -not $files.Count) { return }
    Write-Host 'Es werden ausschliesslich die oben aufgefuehrten alten Testkopien bereinigt.'
    if ((Read-Host 'Endgueltig loeschen? Tippe LOESCHEN') -cne 'LOESCHEN') { Write-Host 'Abgebrochen.'; return }
    $running = @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($reports + '\', [StringComparison]::OrdinalIgnoreCase) })
    if ($running.Count) { throw 'Es laufen Programme aus den Testordnern. Bitte diese zuerst beenden.' }
    $driveName = [IO.Path]::GetPathRoot($root).Substring(0,1)
    $before = (Get-PSDrive $driveName).Free
    $deleted = 0; $skipped = 0
    foreach ($file in $files) {
        try {
            Assert-SafePath $file.FullName
            $now = Get-Item -LiteralPath $file.FullName -Force
            if ($now.Length -ne $file.Length -or $now.LastWriteTimeUtc -ne $file.LastWriteTimeUtc) { throw 'Datei wurde inzwischen geaendert.' }
            Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
            $deleted++
        } catch { $skipped++ }
    }
    $after = (Get-PSDrive $driveName).Free
    Write-Host ('Fertig: {0} Dateien geloescht, {1} uebersprungen.' -f $deleted, $skipped)
    Write-Host ('Freier Speicher vorher: {0:N2} GiB; jetzt: {1:N2} GiB.' -f ($before/1GB), ($after/1GB))
} catch {
    Write-Host ('Abbruch: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
