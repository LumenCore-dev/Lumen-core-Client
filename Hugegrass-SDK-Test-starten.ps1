param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskKit = 'D:\SteamLibrary\steamapps\common\H4EK'
$taskScenario = 'levels\custom\hugegrass_fidelity\ground_pattern_v30\hugegrass_port'
$taskSource = Join-Path $taskKit ('tags\' + $taskScenario + '.scenario')
$taskExpected = 'e6b0b00c52f8f0ba08e5b4970586df9aa182afaf4c8d75ec2e750d9a62a8a510'
$taskExe = Join-Path $taskKit 'halo4_tag_test.exe'
if (-not (Test-Path -LiteralPath $taskExe)) { throw 'Das H4 Editing Kit wurde am erwarteten Ort nicht gefunden.' }
if ((Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskExpected) { throw 'Der gepruefte Editorstand wurde veraendert. Teststart abgebrochen.' }
$taskProof = Get-Content -LiteralPath (Join-Path $taskRoot 'Source\assets\map-ports\hugegrass\fidelity\ground-v30-player-start\graphics-comparison.json') -Raw | ConvertFrom-Json
if (-not $taskProof.scriptCompleted -or -not $taskProof.sourcePlayerPresentVerified -or $taskProof.sourceScenarioSha256 -ne $taskExpected) { throw 'Die geprueften Engine-Aufnahmen mit bestaetigtem Spielerstart fehlen.' }
if ($ValidateOnly) { Write-Output 'SDK_TEST_START_VALIDATED: Boden V27, 123 Fahrzeuge, Scarab, 128 Respawns, acht sichere Startpunkte; keine Programme gestartet.'; return }
if (Get-Process halo4_tag_test,halo4_tag_play,sapien,sapien_play -ErrorAction SilentlyContinue) { throw 'Bitte den bereits offenen Editing-Kit-Test oder Editor zuerst schliessen.' }
$taskRun = Join-Path $taskRoot ('Source\assets\map-ports\hugegrass\fidelity\manual-sdk-test-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $taskRun | Out-Null
$taskInit = Join-Path $taskKit 'bonobo_init.txt'
$taskHadInit = Test-Path -LiteralPath $taskInit
$taskPrevious = if ($taskHadInit) { [IO.File]::ReadAllBytes($taskInit) } else { $null }
if ($taskHadInit) { [IO.File]::WriteAllBytes((Join-Path $taskRun 'bonobo_init-before.txt'), $taskPrevious) }
$taskCommands = @(
    'game_multiplayer megalo', 'game_player_count 1', 'run_game_scripts 1',
    'game_set_variant "H4_Slayer"', 'game_splitscreen 1',
    'events_debug_spam_render 0', 'terminal_render 0', 'error_geometry_hide_all',
    'debug_structure false', 'debug_objects false',
    'render_default_lighting false', 'cheat_deathless_player false', 'cheat_infinite_ammo false',
    ('game_start "' + $taskScenario + '"')
)
try {
    [IO.File]::WriteAllText($taskInit, (($taskCommands -join "`r`n") + "`r`n"), [Text.Encoding]::ASCII)
    Write-Host 'Hugegrass startet als spielbarer H4-SDK-Test mit neuem Boden und allen 123 Fahrzeugen.'
    Write-Host 'Du startest etwa 100 Meter vom Scarab entfernt und blickst zum seitlichen Einstieg.'
    Write-Host 'WASD: bewegen. Benutzen-Taste (meist E): Einstieg versuchen. Im Scarab WASD, zum Aussteigen erneut Benutzen.'
    Write-Host 'Dieser Test nutzt das Editing Kit. Einstieg mit der Benutzen-Taste und MCC-Netzwerk sind noch nicht als bestanden bestaetigt.'
    $taskGame = Start-Process -FilePath $taskExe -WorkingDirectory $taskKit -WindowStyle Normal -PassThru
    @{pid=$taskGame.Id;sourceScenario=$taskSource;sourceSha256=$taskExpected;interactiveUserTest=$true;forcedBoarding=$false;forcedCamera=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRun 'manual-test.json') -Encoding utf8
    $taskGame.WaitForExit()
} finally {
    if ($taskHadInit) { [IO.File]::WriteAllBytes($taskInit, $taskPrevious) }
    elseif (Test-Path -LiteralPath $taskInit) { Remove-Item -LiteralPath $taskInit }
}
