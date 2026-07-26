#Requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('vscode', 'codex', 'opencode')]
    [string]$HostName,

    [Parameter(Mandatory = $true)]
    [ValidateSet('user', 'workspace')]
    [string]$Scope,

    [ValidateSet('single', 'multi')]
    [string]$Profile = 'single',

    [string]$Target,
    [string]$Workspace,
    [string]$Catalog,
    [string]$Docs,
    [string]$CellsCli,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Harness = Join-Path $ScriptRoot 'cells_agent.py'

$Python = Get-Command python -ErrorAction SilentlyContinue
$PythonPrefix = @()
if (-not $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
    $PythonPrefix = @('-3')
}
if (-not $Python) {
    throw 'Python 3 is required to render and install the Cells agent harness.'
}

$HarnessArgs = @(
    $Harness,
    'install',
    '--host', $HostName,
    '--scope', $Scope,
    '--profile', $Profile
)
if ($Target) { $HarnessArgs += @('--target', $Target) }
if ($Workspace) { $HarnessArgs += @('--workspace', $Workspace) }
if ($Catalog) { $HarnessArgs += @('--catalog', $Catalog) }
if ($Docs) { $HarnessArgs += @('--docs', $Docs) }
if ($CellsCli) { $HarnessArgs += @('--cells-cli', $CellsCli) }
if ($Force) { $HarnessArgs += '--force' }

& $Python.Source @PythonPrefix @HarnessArgs
exit $LASTEXITCODE
