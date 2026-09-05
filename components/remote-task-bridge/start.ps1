param([Parameter(Mandatory)][string]$Config)
. (Join-Path $PSScriptRoot 'common.ps1')
$running = @(Get-Process -Name ChatGPT -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $appPath })
if ($running.Count -gt 0) { Write-Output 'Isolated Desktop is already running. No duplicate started.'; return }
$deployed = Get-Content -LiteralPath (Join-Path $runtimeRoot 'resources/remote-tasks/config.json') -Raw | ConvertFrom-Json
$deployed.sshExecutable = [System.IO.Path]::GetFullPath($deployed.sshExecutable)
foreach ($key in @('hostId','sshAlias','remoteDirectory','remotePython','sshExecutable')) {
    if ($settings.$key -ne $deployed.$key) { throw 'Configuration changed; rebuild and install before starting.' }
}
if (($settings.projects | ConvertTo-Json -Compress) -ne ($deployed.projects | ConvertTo-Json -Compress)) { throw 'Project authorization changed; rebuild first.' }
$info = [System.Diagnostics.ProcessStartInfo]::new($settings.sshExecutable)
$info.UseShellExecute = $false
$info.CreateNoWindow = $true
$info.RedirectStandardInput = $true
$info.RedirectStandardError = $true
$remote = $settings.remoteDirectory
$python = $settings.remotePython
foreach ($arg in @('-T','-o','BatchMode=yes',$settings.sshAlias,"umask 077; mkdir -p $remote && cat > $remote/mcp.py && $python -m py_compile $remote/mcp.py && $python $remote/mcp.py --prepare-socket")) {
    $info.ArgumentList.Add($arg)
}
$proc = [System.Diagnostics.Process]::Start($info)
$stderr = $proc.StandardError.ReadToEndAsync()
$proc.StandardInput.Write([System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'mcp.py')))
$proc.StandardInput.Close()
if (-not $proc.WaitForExit(30000)) { $proc.Kill(); throw 'Helper provisioning timed out. Desktop was not started.' }
if ($proc.ExitCode -ne 0) { throw 'Helper provisioning failed. Desktop was not started.' }
& (Join-Path $PSScriptRoot 'launch.ps1') -Config $Config
