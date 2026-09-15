param(
    [string]$Agent,
    [string]$Path,
    [string]$HomeRoot,
    [ValidateSet('single', 'multi')][string]$Profile = 'single',
    [switch]$DryRun,
    [switch]$Replace,
    [switch]$Help
)
$ErrorActionPreference = 'Stop'
$InstallArgs = @((Join-Path $PSScriptRoot 'install.py'))
if ($Help) { $InstallArgs += '--help' }
else {
    $InstallArgs += @('--agent', $Agent, '--profile', $Profile)
    if ($Path) { $InstallArgs += @('--path', $Path) }
    if ($HomeRoot) { $InstallArgs += @('--home', $HomeRoot) }
    if ($DryRun) { $InstallArgs += '--dry-run' }
    if ($Replace) { $InstallArgs += '--replace' }
}
$PythonCommand = if ($env:CELLS_AGENT_PYTHON) { $env:CELLS_AGENT_PYTHON } else { 'python' }
& $PythonCommand @InstallArgs
exit $LASTEXITCODE
