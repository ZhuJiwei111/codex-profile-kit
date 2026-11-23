# Dot-source only after the caller supplies -Config. Configuration stays outside Git.
$ErrorActionPreference = 'Stop'
$settings = Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json
if ($settings.version -ne 1 -or $settings.enabled -ne $true) { throw 'Bridge is disabled. Review a host-local configuration before enabling.' }
if ($settings.sshAlias -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$' -or
    $settings.hostId -ne ('remote-ssh-discovered:' + $settings.sshAlias)) { throw 'Invalid SSH binding.' }
foreach ($remotePath in @($settings.remoteDirectory,$settings.remotePython)) {
    if ($remotePath -notmatch '^/[A-Za-z0-9_./-]+$' -or $remotePath.Split('/') -contains '..') { throw 'Remote paths must be absolute without shell metacharacters or traversal.' }
}
if (@($settings.projects).Count -eq 0) { throw 'No projects authorized.' }
foreach ($projectPath in $settings.projects) {
    if ($projectPath -notmatch '^/' -or $projectPath.Split('/') -contains '..') { throw 'Project paths must be absolute without traversal.' }
}
if (-not [System.IO.Path]::IsPathFullyQualified($settings.stateRoot) -or
    -not [System.IO.Path]::IsPathFullyQualified($settings.sourceApp)) { throw 'Local paths must be absolute.' }
$experimentRoot = [System.IO.Path]::GetFullPath($settings.stateRoot).TrimEnd('\','/')
$sourceRoot = [System.IO.Path]::GetFullPath($settings.sourceApp).TrimEnd('\','/')
$settings.sshExecutable = [System.IO.Path]::GetFullPath($settings.sshExecutable)
if ($experimentRoot.Length -lt 6 -or $experimentRoot -eq $sourceRoot -or
    $experimentRoot.StartsWith($sourceRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or
    $sourceRoot.StartsWith($experimentRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Source and isolated state must be separate.' }
$runtimeRoot = Join-Path $experimentRoot 'runtime'
$appPath = Join-Path $runtimeRoot 'ChatGPT.exe'
$ownerPath = Join-Path $experimentRoot 'bridge-owner.json'
if (-not (Test-Path -LiteralPath $ownerPath)) { throw 'Run prepare.ps1 first.' }
$owner = Get-Content -LiteralPath $ownerPath -Raw | ConvertFrom-Json
if ($owner.component -ne 'remote-task-bridge' -or $owner.stateRoot -ne $experimentRoot) { throw 'State ownership mismatch.' }
