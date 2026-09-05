# Execute with PowerShell 7; no Desktop, SSH or repository mutations.
$ErrorActionPreference = 'Stop'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('bridge-config-test-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $fixture | Out-Null
try {
    $state = Join-Path $fixture 'state'
    New-Item -ItemType Directory -Path $state | Out-Null
    @{component='remote-task-bridge';stateRoot=$state} | ConvertTo-Json | Set-Content (Join-Path $state 'bridge-owner.json')
    $Config = Join-Path $fixture 'config.json'
    $value = @{version=1;enabled=$true;stateRoot=$state;sourceApp=(Join-Path $fixture 'source');sshExecutable=(Join-Path $fixture 'ssh.exe');sshAlias='fixture';hostId='remote-ssh-discovered:fixture';remotePython='/usr/bin/python3';remoteDirectory='/private/bridge';projects=@('/project')}
    $value | ConvertTo-Json | Set-Content $Config
    . (Join-Path $PSScriptRoot 'common.ps1')
    if ($experimentRoot -ne $state) { throw 'Path normalization failed.' }
    $value.sourceApp = Join-Path $state 'source'
    $value | ConvertTo-Json | Set-Content $Config
    $rejected=$false
    try { . (Join-Path $PSScriptRoot 'common.ps1') } catch { $rejected=$_.Exception.Message -like '*must be separate*' }
    if (-not $rejected) { throw 'Nested source path was accepted.' }
    'PowerShell configuration regression PASS'
} finally {
    # Exact unique test-owned directory; verify it is inside the intended temporary root.
    $resolved=[IO.Path]::GetFullPath($fixture)
    $temp=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([char]92,[char]47)
    if (-not $resolved.StartsWith($temp+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe test cleanup path.' }
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
