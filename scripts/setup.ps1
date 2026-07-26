#Requires -Version 5.1

Write-Warning 'setup.ps1 is now an alias of the environment-neutral installer.'
& (Join-Path $PSScriptRoot 'install.ps1') @args
exit $LASTEXITCODE
