$ErrorActionPreference = 'Stop'
try {
    $testVersion = 'V73'
    $testReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-standard-vehicles-v73\user-test-deployment.json'
    if (-not (Test-Path -LiteralPath $testReceiptPath)) {
        $testVersion = 'V71'
        $testReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-standard-vehicles-v71\user-test-deployment.json'
    }
    if (-not (Test-Path -LiteralPath $testReceiptPath)) {
        $testVersion = 'V67'
        $testReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-client-test-v67\deployment.json'
    }
    if (Test-Path -LiteralPath $testReceiptPath) {
        $testReceipt = Get-Content -LiteralPath $testReceiptPath -Raw | ConvertFrom-Json
        $expectedStatus = if ($testVersion -in @('V71','V73')) { 'BUILT_FOR_USER_TEST' } else { 'VERIFIED_CTF_TEST_READY' }
        if ($testReceipt.status -ne $expectedStatus) { throw 'Der CTF-Teststand ist nicht bereit.' }
        $testDirectory = Join-Path $PSScriptRoot ('Client\Hugegrass-Test-' + $testVersion)
        if ([IO.Path]::GetFullPath($testReceipt.clientDirectory) -ne [IO.Path]::GetFullPath($testDirectory)) { throw 'Unerwarteter Testordner.' }
        foreach ($testBinary in @('LumenCore.exe','LumenCoreRuntime.dll','Halo4NativeClient.exe')) {
            if ((Get-FileHash -LiteralPath (Join-Path $testDirectory $testBinary) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $testReceipt.binarySha256.$testBinary) { throw 'Die gebaute Client-Testversion wurde veraendert.' }
        }
        if ((Get-FileHash -LiteralPath (Join-Path $testDirectory 'custom-maps\hugegrass_port.map') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $testReceipt.mapSha256) { throw 'Die gebaute Testkarte wurde veraendert.' }
        if (Get-Process LumenCore,Halo4NativeClient -ErrorAction SilentlyContinue) { throw 'Bitte den laufenden Client schliessen und Hugegrass-Test-starten.cmd erneut starten.' }
        $testLauncher = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Client\launcher.ini')
        $testGame = ($testLauncher | Where-Object { $_ -like 'GameDir=*' } | Select-Object -First 1).Substring(8).Trim()
        $testStart = New-Object System.Diagnostics.ProcessStartInfo
        $testStart.FileName = Join-Path $testDirectory 'LumenCore.exe'
        $testStart.WorkingDirectory = $testDirectory
        $testStart.UseShellExecute = $false
        $testStart.Arguments = '--game-dir "{0}" --load-multiplayer --map hugegrass_port --game-variant ctf' -f $testGame.TrimEnd('\')
        foreach ($testName in @($testStart.EnvironmentVariables.Keys)) {
            if ([string]$testName -like 'HALO4_*') { $testStart.EnvironmentVariables.Remove([string]$testName) }
        }
        $testProcess = [System.Diagnostics.Process]::Start($testStart)
        try { $testProcess.WaitForExit(); $testCode = $testProcess.ExitCode } finally { $testProcess.Dispose() }
        exit $testCode
    }
    $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-original-completeness-v68-startup-recovery\deployment.json'
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-original-completeness-v68\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-original-completeness-v67\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-original-completeness-v59\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-environment-v55\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-scarab-onboard-v54\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-scarab-onboard-v53\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-scarab-lifecycle\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-sky-scarab\deployment.json' }
    if (-not (Test-Path -LiteralPath $currentReceiptPath)) { $currentReceiptPath = Join-Path $PSScriptRoot 'Source\reports\hugegrass-camera-spawns\deployment.json' }
    if (Test-Path -LiteralPath $currentReceiptPath) {
        $currentReceipt = Get-Content -LiteralPath $currentReceiptPath -Raw | ConvertFrom-Json
        if ($currentReceipt.status -ne 'DEPLOYED') { throw 'Die aktuelle Hugegrass-Version ist noch nicht bereit.' }
        $currentExe = Join-Path $PSScriptRoot 'Client\LumenCore.exe'
        $currentMap = Join-Path $PSScriptRoot 'Client\custom-maps\hugegrass_port.map'
        if ((Get-FileHash -LiteralPath $currentExe -Algorithm SHA256).Hash.ToLowerInvariant() -ne $currentReceipt.binarySha256.'LumenCore.exe') { throw 'Die aktuelle Client-Version wurde veraendert.' }
        if ((Get-FileHash -LiteralPath $currentMap -Algorithm SHA256).Hash.ToLowerInvariant() -ne $currentReceipt.mapSha256) { throw 'Die aktuelle Hugegrass-Karte wurde veraendert.' }
        $currentLauncher = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Client\launcher.ini')
        $currentGame = ($currentLauncher | Where-Object { $_ -like 'GameDir=*' } | Select-Object -First 1).Substring(8).Trim()
        $currentStart = New-Object System.Diagnostics.ProcessStartInfo
        $currentStart.FileName = $currentExe
        $currentStart.WorkingDirectory = Split-Path $currentExe -Parent
        $currentStart.UseShellExecute = $false
        $currentStart.Arguments = '--game-dir "{0}" --load-multiplayer --map hugegrass_port --game-variant slayer' -f $currentGame.TrimEnd('\')
        foreach ($currentName in @($currentStart.EnvironmentVariables.Keys)) {
            if ([string]$currentName -like 'HALO4_*') { $currentStart.EnvironmentVariables.Remove([string]$currentName) }
        }
        $currentProcess = [System.Diagnostics.Process]::Start($currentStart)
        try { $currentProcess.WaitForExit(); $currentCode = $currentProcess.ExitCode } finally { $currentProcess.Dispose() }
        exit $currentCode
    }
    $taskReceiptPath = Join-Path $PSScriptRoot 'Source\assets\map-ports\hugegrass\fidelity\hugegrass-capacity-v45-playtest.json'
    if (-not (Test-Path -LiteralPath $taskReceiptPath)) { throw 'Der erweiterte Hugegrass-Test ist noch nicht fertig geprueft.' }
    $taskReceipt = Get-Content -LiteralPath $taskReceiptPath -Raw | ConvertFrom-Json
    if ($taskReceipt.status -ne 'PREPARED_VERIFIED' -or $taskReceipt.heapMB -ne 8 -or $taskReceipt.physicsCapacity -ne 2048 -or $taskReceipt.attachmentCapacity -ne 16) { throw 'Der Hugegrass-Test ist noch nicht freigegeben.' }
    if (Get-Process Halo4NativeClient -ErrorAction SilentlyContinue) { throw 'Bitte den laufenden Halo-4-Client zuerst schliessen.' }
    $taskExe = $taskReceipt.binaries.client.path
    $taskMap = Join-Path (Split-Path $taskExe -Parent) 'custom-maps\hugegrass_port.map'
    if ((Get-FileHash -LiteralPath $taskExe -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskReceipt.binaries.client.sha256) { throw 'Die Testversion des Clients wurde veraendert.' }
    if ((Get-FileHash -LiteralPath $taskMap -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskReceipt.mapSha256) { throw 'Die Testkarte wurde veraendert.' }
    $taskStart = New-Object System.Diagnostics.ProcessStartInfo
    $taskStart.FileName = $taskExe
    $taskStart.WorkingDirectory = Split-Path $taskExe -Parent
    $taskStart.UseShellExecute = $false
    $taskStart.Arguments = '--game-dir "{0}" --load-multiplayer --map hugegrass_port --game-variant slayer' -f $taskReceipt.gameDirectory.TrimEnd('\')
    foreach ($taskName in @($taskStart.EnvironmentVariables.Keys)) {
        if ([string]$taskName -like 'HALO4_*') { $taskStart.EnvironmentVariables.Remove([string]$taskName) }
    }
    $taskStart.EnvironmentVariables['HALO4_CAPACITY_LAB_PLAYERS'] = '128'
    $taskStart.EnvironmentVariables['HALO4_WIDE_SESSION_BANK'] = '1'
    $taskStart.EnvironmentVariables['HALO4_OBJECT_BODY_HEAP_MB'] = '8'
    $taskStart.EnvironmentVariables['HALO4_PHYSICS_CAPACITY'] = '2048'
    $taskStart.EnvironmentVariables['HALO4_ATTACHMENT_CAPACITY'] = '16'
    $taskProcess = [System.Diagnostics.Process]::Start($taskStart)
    try { $taskProcess.WaitForExit(); $taskCode = $taskProcess.ExitCode } finally { $taskProcess.Dispose() }
    exit $taskCode
} catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
