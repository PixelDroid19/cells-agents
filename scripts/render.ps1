#Requires -Version 5.1

[CmdletBinding()]
param(
    [ValidateSet('vscode', 'codex', 'opencode', 'all')]
    [string]$HostName = 'all',
    [ValidateSet('single', 'multi')]
    [string]$Profile = 'single',
    [string]$Output = (Join-Path (Split-Path -Parent $PSScriptRoot) 'dist'),
    [switch]$Force
)

$Python = Get-Command python -ErrorAction SilentlyContinue
$Prefix = @()
if (-not $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
    $Prefix = @('-3')
}
if (-not $Python) { throw 'Python 3 is required.' }

$ArgsList = @(
    (Join-Path $PSScriptRoot 'cells_agent.py'),
    'render',
    '--host', $HostName,
    '--profile', $Profile,
    '--output', $Output
)
if ($Force) { $ArgsList += '--force' }
& $Python.Source @Prefix @ArgsList
exit $LASTEXITCODE
