#Requires -Version 5.1
# Compatibility entrypoint for the v3 installer; accepts install.ps1 parameters.
[CmdletBinding()]
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
& (Join-Path $PSScriptRoot 'install.ps1') @PSBoundParameters
exit $LASTEXITCODE
