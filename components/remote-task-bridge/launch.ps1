param([Parameter(Mandatory)][string]$Config)
. (Join-Path $PSScriptRoot 'common.ps1')
$startInfo = [System.Diagnostics.ProcessStartInfo]::new($appPath)
$startInfo.UseShellExecute = $false
$startInfo.WorkingDirectory = $runtimeRoot
foreach ($name in @($startInfo.Environment.Keys)) {
    if ($name -match '^(CODEX_|OPENAI_|CHATGPT_|ELECTRON_|OWL_|REMOTE_TASKS_)') { $startInfo.Environment.Remove($name) | Out-Null }
}
$startInfo.Environment['CODEX_HOME'] = Join-Path $experimentRoot 'codex-home'
$startInfo.Environment['CODEX_ELECTRON_USER_DATA_PATH'] = Join-Path $experimentRoot 'user-data'
$startInfo.Environment['REMOTE_TASKS_HOME'] = $experimentRoot
$startInfo.ArgumentList.Add('--user-data-dir=' + (Join-Path $experimentRoot 'user-data'))
# This visible window is the interactive isolated application, not a background service.
$proc = [System.Diagnostics.Process]::Start($startInfo)
Write-Output ('Started isolated app PID: ' + $proc.Id)
