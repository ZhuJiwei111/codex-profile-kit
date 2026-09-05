param([Parameter(Mandatory)][string]$Config)
$ErrorActionPreference = 'Stop'
$settings = Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json
if ($settings.version -ne 1 -or $settings.enabled -ne $true) { throw 'Bridge is disabled.' }
if (-not [System.IO.Path]::IsPathFullyQualified($settings.stateRoot)) { throw 'State path must be absolute.' }
$state = [System.IO.Path]::GetFullPath($settings.stateRoot).TrimEnd('\','/')
if (Test-Path -LiteralPath $state) { throw 'Preparation requires a new empty state directory; existing state is preserved.' }
if (-not (Test-Path -LiteralPath (Join-Path $settings.sourceApp 'resources/app.asar'))) { throw 'Source app archive missing.' }
New-Item -ItemType Directory -Path $state | Out-Null
@{component='remote-task-bridge';stateRoot=$state} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $state 'bridge-owner.json') -Encoding utf8
. (Join-Path $PSScriptRoot 'common.ps1')
# Copy program files only. No existing user-data or CODEX_HOME is copied.
& robocopy $sourceRoot $runtimeRoot /E /COPY:DAT /DCOPY:DAT /R:0 /W:0 /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -ge 8) { throw 'Program copy failed; partial state retained for inspection.' }
New-Item -ItemType Directory -Path (Join-Path $state 'user-data'),(Join-Path $state 'codex-home') | Out-Null
'Prepared independent runtime and empty profile directories. Sign in manually after build/install.'
