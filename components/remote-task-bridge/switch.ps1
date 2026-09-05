param([Parameter(Mandatory)][string]$Config, [switch]$Rollback, [switch]$StopOnly)
$ErrorActionPreference = 'Stop'
if ($Rollback -and $StopOnly) { throw 'Select only one operation.' }
. (Join-Path $PSScriptRoot 'common.ps1')
$stagingRoot = Join-Path $experimentRoot 'daily-build'
$backupRoot = Join-Path $experimentRoot 'before-daily-v1'
$appPath = Join-Path $runtimeRoot 'ChatGPT.exe'
$archivePath = Join-Path $runtimeRoot 'resources/app.asar'
if (-not $Rollback -and -not $StopOnly) {
    foreach ($name in @('app.asar','ChatGPT.exe','remote-tasks/core.cjs','remote-tasks/desktop.cjs','remote-tasks/config.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $stagingRoot $name))) { throw ('Missing staged file: ' + $name) }
    }
} elseif ($Rollback -and -not (Test-Path -LiteralPath (Join-Path $backupRoot 'app.asar'))) { throw 'No previous build available.' }
# Stop only the exact app copy and SSH process recorded by this extension.
$owned = @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $appPath })
$ids = @($owned.ProcessId)
$roots = @($owned | Where-Object { $_.ParentProcessId -notin $ids })
foreach ($item in $roots) { Stop-Process -Id $item.ProcessId }
if ($owned.Count -gt 0) { Start-Sleep -Seconds 2 }
foreach ($item in $owned) {
    $current = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $item.ProcessId)
    if ($null -ne $current -and $current.ExecutablePath -eq $appPath) { Stop-Process -Id $current.ProcessId }
}
$recordPath = Join-Path $experimentRoot 'daily-v1/runtime.json'
if (Test-Path -LiteralPath $recordPath) {
    $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    if ($null -ne $record.sshPid) {
        $tunnel = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + [int]$record.sshPid)
        if ($null -ne $tunnel -and $tunnel.ExecutablePath -eq $settings.sshExecutable -and
            $tunnel.CommandLine.Contains($record.remoteSocket + ':127.0.0.1:')) { Stop-Process -Id $tunnel.ProcessId }
    }
}
if ($StopOnly) { Write-Output 'Stopped isolated Desktop and its recorded SSH channel. Program and user files retained.'; return }
if ($Rollback) {
    Copy-Item -LiteralPath (Join-Path $backupRoot 'app.asar') -Destination $archivePath
    Copy-Item -LiteralPath (Join-Path $backupRoot 'ChatGPT.exe') -Destination $appPath
    Write-Output 'Restored previous isolated build. User data retained. Previous POC tunnel is not restarted.'
} else {
    if (-not (Test-Path -LiteralPath $backupRoot)) {
        New-Item -ItemType Directory -Path $backupRoot | Out-Null
        Copy-Item -LiteralPath $archivePath -Destination (Join-Path $backupRoot 'app.asar')
        Copy-Item -LiteralPath $appPath -Destination (Join-Path $backupRoot 'ChatGPT.exe')
    }
    $moduleRoot = Join-Path $runtimeRoot 'resources/remote-tasks'
    New-Item -ItemType Directory -Path $moduleRoot -Force | Out-Null
    foreach ($name in @('core.cjs','desktop.cjs','config.json')) {
        Copy-Item -LiteralPath (Join-Path $stagingRoot ('remote-tasks/' + $name)) -Destination (Join-Path $moduleRoot $name)
    }
    Copy-Item -LiteralPath (Join-Path $stagingRoot 'app.asar') -Destination $archivePath
    Copy-Item -LiteralPath (Join-Path $stagingRoot 'ChatGPT.exe') -Destination $appPath
    Write-Output 'Installed staged build into isolated runtime. Previous build retained.'
}
if ($Rollback) {
    & (Join-Path $PSScriptRoot 'launch.ps1') -Config $Config
} else {
    & (Join-Path $PSScriptRoot 'start.ps1') -Config $Config
}
