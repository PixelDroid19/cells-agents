#Requires -Version 5.1

<#
.SYNOPSIS
    Cells Agent Bundle — Full Setup Script for Windows
.DESCRIPTION
    Detects installed agents, copies skills, and configures orchestrator prompts.
    Idempotent: safe to run multiple times (uses markers to avoid duplication).
.PARAMETER Agent
    Install for a specific agent.
    Valid values: claude-code, opencode, gemini-cli, cursor, vscode, codex
.PARAMETER All
    Auto-detect and install for all found agents.
.PARAMETER OpenCodeMode
    OpenCode agent mode: 'single' (default) or 'multi' (one agent per phase with its own model).
.PARAMETER NonInteractive
    No prompts (for external installers).
.EXAMPLE
    .\setup.ps1
.EXAMPLE
    .\setup.ps1 -All
.EXAMPLE
    .\setup.ps1 -Agent opencode -OpenCodeMode multi
.EXAMPLE
    .\setup.ps1 -NonInteractive
#>

[CmdletBinding()]
param(
    [ValidateSet('claude-code', 'opencode', 'gemini-cli', 'cursor', 'vscode', 'codex')]
    [string]$Agent,
    [ValidateSet('single', 'multi')]
    [string]$OpenCodeMode,
    [switch]$All,
    [switch]$NonInteractive,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# ============================================================================
# Paths
# ============================================================================

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoDir = Split-Path -Parent $ScriptRoot
$SkillsSrc = Join-Path $RepoDir 'skills'
$ExamplesDir = Join-Path $RepoDir 'examples'

$MarkerBegin = '<!-- BEGIN:cells-agent-bundle -->'
$MarkerEnd = '<!-- END:cells-agent-bundle -->'

# Backward-compat markers we can upgrade in place
$OldMarkerBegin = '<!-- BEGIN:agent-teams-lite -->'
$OldMarkerEnd = '<!-- END:agent-teams-lite -->'
$GaiMarkerBegin = '<!-- gentle-ai:cells-orchestrator -->'
$GaiMarkerEnd = '<!-- /gentle-ai:cells-orchestrator -->'

$OrchestratorHeadings = @(
    '## Spec-Driven Development (CELLS) Orchestrator',
    '## Spec-Driven Development (CELLS)',
    '## Agent Teams Orchestrator'
)

$SkillsPaths = @{
    'claude-code' = Join-Path $env:USERPROFILE '.claude\skills'
    'opencode'    = Join-Path $env:USERPROFILE '.config\opencode\skills'
    'gemini-cli'  = Join-Path $env:USERPROFILE '.gemini\skills'
    'cursor'      = Join-Path $env:USERPROFILE '.cursor\skills'
    'vscode'      = Join-Path $env:USERPROFILE '.copilot\skills'
    'codex'       = Join-Path $env:USERPROFILE '.codex\skills'
}

$PromptPaths = @{
    'claude-code' = Join-Path $env:USERPROFILE '.claude\CLAUDE.md'
    'opencode'    = Join-Path $env:USERPROFILE '.config\opencode\AGENTS.md'
    'gemini-cli'  = Join-Path $env:USERPROFILE '.gemini\GEMINI.md'
    'cursor'      = Join-Path $env:USERPROFILE '.cursor\rules\cells-agent-bundle.mdc'
    'vscode'      = Join-Path $env:APPDATA 'Code\User\prompts\cells-agent-bundle.instructions.md'
    'codex'       = Join-Path $env:USERPROFILE '.codex\agents.md'
}

$ExampleFiles = @{
    'claude-code' = Join-Path $ExamplesDir 'claude-code\CLAUDE.md'
    'gemini-cli'  = Join-Path $ExamplesDir 'gemini-cli\GEMINI.md'
    'cursor'      = Join-Path $ExamplesDir 'cursor\.cursorrules'
    'vscode'      = Join-Path $RepoDir '.github\\instructions\\copilot-instructions.md'
    'codex'       = Join-Path $ExamplesDir 'codex\agents.md'
}

$AgentBinaries = @{
    'claude-code' = 'claude'
    'opencode'    = 'opencode'
    'gemini-cli'  = 'gemini'
    'cursor'      = 'cursor'
    'vscode'      = 'code'
    'codex'       = 'codex'
}

# ============================================================================
# Display Helpers
# ============================================================================

function Write-Ok    { param([string]$Msg) Write-Host '  ' -NoNewline; Write-Host ([char]0x2713) -ForegroundColor Green -NoNewline; Write-Host " $Msg" }
function Write-Warn  { param([string]$Msg) Write-Host '  ! ' -ForegroundColor Yellow -NoNewline; Write-Host $Msg }
function Write-Fail  { param([string]$Msg) Write-Host '  ' -NoNewline; Write-Host ([char]0x2717) -ForegroundColor Red -NoNewline; Write-Host " $Msg" }
function Write-Info  { param([string]$Msg) Write-Host '  ' -NoNewline; Write-Host ([char]0x2192) -ForegroundColor Blue -NoNewline; Write-Host " $Msg" }
function Write-Head  { param([string]$Msg) Write-Host ''; Write-Host $Msg -ForegroundColor Cyan }

# ============================================================================
# Agent Detection
# ============================================================================

function Find-Agents {
    Write-Head 'Detecting installed agents...'

    $found = @()
    foreach ($agent in $AgentBinaries.Keys | Sort-Object) {
        $binary = $AgentBinaries[$agent]
        $cmd = Get-Command $binary -ErrorAction SilentlyContinue
        if ($cmd) {
            Write-Ok "$agent ($binary found in PATH)"
            $found += $agent
        }
    }

    Write-Host ''
    if ($found.Count -eq 0) {
        Write-Warn 'No agents detected in PATH'
        Write-Info 'You can still install manually with: .\install.ps1'
    } else {
        Write-Host "  $($found.Count) agent(s) detected" -ForegroundColor Green
    }

    return $found
}

# ============================================================================
# Install Skills
# ============================================================================

function Install-SkillDirectory {
    param(
        [string]$SourceDir,
        [string]$TargetRoot
    )

    $skillName = Split-Path -Leaf $SourceDir
    $skillFile = Join-Path $SourceDir 'SKILL.md'
    if (-not (Test-Path $skillFile)) {
        Write-Warn "Skipping $skillName (SKILL.md not found in source)"
        return
    }

    $targetDir = Join-Path $TargetRoot $skillName
    if (Test-Path $targetDir) {
        Remove-Item -Path $targetDir -Recurse -Force
    }

    Copy-Item -Path $SourceDir -Destination $targetDir -Recurse -Force

    Get-ChildItem -Path $targetDir -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
    }

    Write-Ok $skillName
}

function Install-Skills {
    param([string]$TargetDir)

    Write-Info "Installing skills -> $TargetDir"
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    # Copy _shared conventions
    $sharedSrc = Join-Path $SkillsSrc '_shared'
    $sharedTarget = Join-Path $TargetDir '_shared'
    if (Test-Path $sharedSrc) {
        New-Item -ItemType Directory -Path $sharedTarget -Force | Out-Null
        Copy-Item -Path (Join-Path $sharedSrc '*.md') -Destination $sharedTarget -Force -ErrorAction SilentlyContinue
        Write-Ok '_shared conventions'
    }

    $count = 0

    # Copy all cells-* skills
    $cellsSkills = @(Get-ChildItem -Path $SkillsSrc -Directory -Filter 'cells-*')
    foreach ($skillDir in $cellsSkills) {
        Install-SkillDirectory -SourceDir $skillDir.FullName -TargetRoot $TargetDir
        $count++
    }

    # Copy skill-registry if present
    $registryDir = Join-Path $SkillsSrc 'skill-registry'
    if (Test-Path $registryDir) {
        Install-SkillDirectory -SourceDir $registryDir -TargetRoot $TargetDir
        $count++
    }

    # Copy agent-browser if present
    $browserDir = Join-Path $SkillsSrc 'agent-browser'
    if (Test-Path $browserDir) {
        Install-SkillDirectory -SourceDir $browserDir -TargetRoot $TargetDir
        $count++
    }

    Write-Ok "$count skills installed"
}

# ============================================================================
# Setup Orchestrator Prompt (idempotent with markers)
# ============================================================================

function Get-OrchestratorContent {
    param([string]$ExampleFile)

    $rawContent = Get-Content -Path $ExampleFile -Raw
    if ($rawContent -match '(?s)(## (Spec-Driven Development|Agent Teams).*)') {
        return $Matches[1]
    }

    return $rawContent
}

function Set-Orchestrator {
    param([string]$PromptPath, [string]$ExampleFile)

    if (-not $ExampleFile -or -not (Test-Path $ExampleFile)) { return }

    $promptDir = Split-Path -Parent $PromptPath
    New-Item -ItemType Directory -Path $promptDir -Force | Out-Null

    $content = Get-OrchestratorContent -ExampleFile $ExampleFile

    if (Test-Path $PromptPath) {
        $existing = Get-Content -Path $PromptPath -Raw

        if ($existing -match [regex]::Escape($MarkerBegin)) {
            $pattern = "(?s)$([regex]::Escape($MarkerBegin)).*?$([regex]::Escape($MarkerEnd))"
            $replacement = "$MarkerBegin`n$content`n$MarkerEnd"
            $updated = [regex]::Replace($existing, $pattern, $replacement)
            Set-Content -Path $PromptPath -Value $updated -NoNewline
            Write-Ok "Orchestrator updated in $PromptPath"
        }
        elseif ($existing -match [regex]::Escape($OldMarkerBegin)) {
            $pattern = "(?s)$([regex]::Escape($OldMarkerBegin)).*?$([regex]::Escape($OldMarkerEnd))"
            $replacement = "$MarkerBegin`n$content`n$MarkerEnd"
            $updated = [regex]::Replace($existing, $pattern, $replacement)
            Set-Content -Path $PromptPath -Value $updated -NoNewline
            Write-Ok "Orchestrator updated in $PromptPath (upgraded old markers)"
        }
        elseif ($existing -match [regex]::Escape($GaiMarkerBegin)) {
            $pattern = "(?s)$([regex]::Escape($GaiMarkerBegin)).*?$([regex]::Escape($GaiMarkerEnd))"
            $replacement = "$MarkerBegin`n$content`n$MarkerEnd"
            $updated = [regex]::Replace($existing, $pattern, $replacement)
            Set-Content -Path $PromptPath -Value $updated -NoNewline
            Write-Ok "Orchestrator updated in $PromptPath (replaced gentle-ai section)"
        }
        else {
            $alreadyPresent = $false
            foreach ($heading in $OrchestratorHeadings) {
                if ($existing.Contains($heading)) {
                    $alreadyPresent = $true
                    break
                }
            }

            if ($alreadyPresent) {
                Write-Warn "Orchestrator already present in $PromptPath (no markers found)"
                Write-Info "To enable auto-updates, wrap the CELLS section with:"
                Write-Info "  $MarkerBegin"
                Write-Info "  $MarkerEnd"
            }
            else {
                $appendContent = "`n`n$MarkerBegin`n$content`n$MarkerEnd"
                Add-Content -Path $PromptPath -Value $appendContent
                Write-Ok "Orchestrator appended to $PromptPath"
            }
        }
    }
    else {
        $newContent = "$MarkerBegin`n$content`n$MarkerEnd"
        Set-Content -Path $PromptPath -Value $newContent
        Write-Ok "Orchestrator created at $PromptPath"
    }
}

# ============================================================================
# OpenCode Special Handling
# ============================================================================

function Ask-OpenCodeMode {
    # If already set via parameter, skip
    if ($script:OpenCodeMode) { return }

    # Non-interactive defaults to single
    if ($NonInteractive) {
        $script:OpenCodeMode = 'single'
        return
    }

    Write-Host ''
    Write-Host '  OpenCode agent mode:' -ForegroundColor White
    Write-Host ''
    Write-Host '  1) Single model  - one agent handles all phases (simple, recommended)'
    Write-Host '  2) Multi-model   - one agent per phase, each with its own model'
    Write-Host ''
    $choice = Read-Host '  Choice [1]'
    if (-not $choice) { $choice = '1' }

    switch ($choice) {
        { $_ -eq '2' -or $_ -eq 'multi' } { $script:OpenCodeMode = 'multi' }
        default { $script:OpenCodeMode = 'single' }
    }
}

function Get-MultiPhaseAgent {
    param([string]$CommandName)

    switch ($CommandName) {
        'cells-init'    { return 'cells-init' }
        'cells-explore' { return 'cells-explore' }
        'cells-apply'   { return 'cells-apply' }
        'cells-verify'  { return 'cells-verify' }
        'cells-archive' { return 'cells-archive' }
        default         { return '' }
    }
}

function Set-OpenCode {
    $commandsSrc = Join-Path $ExamplesDir 'opencode\commands'
    $commandsTarget = Join-Path $env:USERPROFILE '.config\opencode\commands'
    $configFile = Join-Path $env:USERPROFILE '.config\opencode\opencode.json'

    Ask-OpenCodeMode

    $exampleConfig = Join-Path $ExamplesDir "opencode\opencode.$($script:OpenCodeMode).json"
    if (-not (Test-Path $exampleConfig) -and $script:OpenCodeMode -eq 'single') {
        $exampleConfig = Join-Path $ExamplesDir 'opencode\opencode.json'
    }

    Write-Info "OpenCode mode: $($script:OpenCodeMode)"

    # Install commands
    if (Test-Path $commandsSrc) {
        New-Item -ItemType Directory -Path $commandsTarget -Force | Out-Null
        $count = 0

        Get-ChildItem -Path $commandsSrc -Filter 'cells-*.md' | ForEach-Object {
            $cmdName = $_.BaseName
            $content = Get-Content -Path $_.FullName -Raw

            if ($script:OpenCodeMode -eq 'multi' -and $content -match '(?m)^subtask:') {
                $mapped = Get-MultiPhaseAgent -CommandName $cmdName
                if ($mapped) {
                    $modified = $content -replace '(?m)^agent: cells-orchestrator', "agent: $mapped"
                    Set-Content -Path (Join-Path $commandsTarget $_.Name) -Value $modified -NoNewline
                }
                else {
                    Copy-Item -Path $_.FullName -Destination (Join-Path $commandsTarget $_.Name) -Force
                }
            }
            else {
                Copy-Item -Path $_.FullName -Destination (Join-Path $commandsTarget $_.Name) -Force
            }

            $count++
        }

        Write-Ok "$count OpenCode commands installed ($($script:OpenCodeMode) mode)"
    }

    # Merge opencode.json
    if (Test-Path $exampleConfig) {
        if (Test-Path $configFile) {
            try {
                $existing = Get-Content -Path $configFile -Raw | ConvertFrom-Json
                $example = Get-Content -Path $exampleConfig -Raw | ConvertFrom-Json

                if ($example.PSObject.Properties['agent']) {
                    if (-not $existing.PSObject.Properties['agent']) {
                        $existing | Add-Member -NotePropertyName 'agent' -NotePropertyValue ([PSCustomObject]@{})
                    }

                    # 1. Save existing model fields from phase agents
                    $savedModels = @{}
                    foreach ($prop in @($existing.agent.PSObject.Properties)) {
                        if (($prop.Name -like 'cells-*' -or $prop.Name -like 'sdd-*') -and $prop.Value.PSObject.Properties['model']) {
                            $savedModels[$prop.Name] = $prop.Value.model
                        }
                    }

                    # 2. Remove old cells/sdd agents
                    foreach ($prop in @($existing.agent.PSObject.Properties)) {
                        if ($prop.Name -like 'cells-*' -or $prop.Name -like 'sdd-*') {
                            $existing.agent.PSObject.Properties.Remove($prop.Name)
                        }
                    }

                    # 3. Add new agents from template
                    foreach ($prop in $example.agent.PSObject.Properties) {
                        $existing.agent | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value -Force
                    }

                    # 4. Restore user model choices
                    foreach ($name in $savedModels.Keys) {
                        $agentProp = $existing.agent.PSObject.Properties[$name]
                        if ($agentProp) {
                            $agentObj = $agentProp.Value
                            $agentObj | Add-Member -NotePropertyName 'model' -NotePropertyValue $savedModels[$name] -Force
                        }
                    }
                }

                # Clean stale plural key from older configs
                if ($existing.PSObject.Properties['agents']) {
                    $existing.PSObject.Properties.Remove('agents')
                }

                $existing | ConvertTo-Json -Depth 20 | Set-Content -Path $configFile
                Write-Ok "Agent config merged into $configFile ($($script:OpenCodeMode) mode)"
            }
            catch {
                Write-Warn "Could not merge opencode.json: $_"
                Write-Info "Merge manually from examples\opencode\opencode.$($script:OpenCodeMode).json"
            }
        }
        else {
            $configDir = Split-Path -Parent $configFile
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
            Copy-Item -Path $exampleConfig -Destination $configFile
            Write-Ok "Config created at $configFile ($($script:OpenCodeMode) mode)"
        }
    }
}

# ============================================================================
# Full Setup for One Agent
# ============================================================================

function Set-Agent {
    param([string]$AgentName)

    Write-Head "Setting up $AgentName"

    $skillsPath = $SkillsPaths[$AgentName]
    Install-Skills -TargetDir $skillsPath

    if ($AgentName -eq 'opencode') {
        Set-OpenCode
    }
    else {
        $promptPath = $PromptPaths[$AgentName]
        $exampleFile = $ExampleFiles[$AgentName]
        if ($exampleFile) {
            Set-Orchestrator -PromptPath $promptPath -ExampleFile $exampleFile
        }
    }
}

# ============================================================================
# Main
# ============================================================================

try {
    if ($Help) {
        Write-Host 'Usage: .\setup.ps1 [OPTIONS]'
        Write-Host ''
        Write-Host 'Options:'
        Write-Host '  -All               Auto-detect and install for all found agents'
        Write-Host '  -Agent NAME        Install for a specific agent'
        Write-Host '  -OpenCodeMode M    OpenCode agent mode: single or multi (per-phase models)'
        Write-Host '  -NonInteractive    No prompts (for external installers)'
        Write-Host '  -Help              Show this help'
        Write-Host ''
        Write-Host 'Agents: claude-code, opencode, gemini-cli, cursor, vscode, codex'
        exit 0
    }

    Write-Host ''
    Write-Host ([char]0x2554 + ([string][char]0x2550 * 42) + [char]0x2557) -ForegroundColor Cyan
    Write-Host ([char]0x2551 + '    Cells Agent Bundle - Full Setup        ' + [char]0x2551) -ForegroundColor Cyan
    Write-Host ([char]0x2551 + '   Detect - Install - Configure            ' + [char]0x2551) -ForegroundColor Cyan
    Write-Host ([char]0x255A + ([string][char]0x2550 * 42) + [char]0x255D) -ForegroundColor Cyan

    # Validate source
    if (-not (Test-Path (Join-Path $SkillsSrc '_shared'))) {
        Write-Fail 'Missing: skills\_shared'
        exit 1
    }

    $cellsSkills = @(Get-ChildItem -Path $SkillsSrc -Directory -Filter 'cells-*')
    if ($cellsSkills.Count -eq 0) {
        Write-Fail "No cells-* skills found in $SkillsSrc"
        exit 1
    }

    foreach ($dir in $cellsSkills) {
        if (-not (Test-Path (Join-Path $dir.FullName 'SKILL.md'))) {
            Write-Fail "Missing: $($dir.Name)\SKILL.md"
            exit 1
        }
    }

    $installedAgents = @()

    if ($Agent) {
        Set-Agent -AgentName $Agent
        $installedAgents += $Agent
    }
    elseif ($All -or $NonInteractive) {
        $detected = Find-Agents
        foreach ($a in $detected) {
            Set-Agent -AgentName $a
            $installedAgents += $a
        }
    }
    else {
        $detected = Find-Agents
        if ($detected.Count -eq 0) {
            Write-Host ''
            Write-Warn 'No agents detected. Use .\install.ps1 for manual installation.'
            exit 0
        }

        Write-Host ''
        $answer = Read-Host 'Set up all detected agents? [Y/n]'
        if (-not $answer -or $answer -match '^[Yy]') {
            foreach ($a in $detected) {
                Set-Agent -AgentName $a
                $installedAgents += $a
            }
        }
        else {
            Write-Host ''
            Write-Host 'Select agents to set up (space-separated numbers):' -ForegroundColor White
            Write-Host ''
            $i = 1
            foreach ($a in $detected) {
                Write-Host "  $i) $a"
                $i++
            }
            Write-Host ''
            $choices = (Read-Host 'Choice') -split '\s+'
            foreach ($c in $choices) {
                $idx = [int]$c - 1
                if ($idx -ge 0 -and $idx -lt $detected.Count) {
                    Set-Agent -AgentName $detected[$idx]
                    $installedAgents += $detected[$idx]
                }
            }
        }
    }

    # Summary
    if ($installedAgents.Count -gt 0) {
        Write-Head 'Setup Complete'
        Write-Host ''
        foreach ($a in $installedAgents) {
            Write-Host '  ' -NoNewline
            Write-Host ([char]0x2713) -ForegroundColor Green -NoNewline
            Write-Host " $a" -ForegroundColor White
            Write-Host "    Skills: $($SkillsPaths[$a])"
            Write-Host "    Prompt: $($PromptPaths[$a])"
        }
        Write-Host ''
        Write-Host 'Done!' -ForegroundColor Green -NoNewline
        Write-Host ' Start using Cells workflow commands like ' -NoNewline
        Write-Host '/cells-init' -ForegroundColor Cyan
        Write-Host ''
        Write-Host 'Recommended: ' -ForegroundColor Yellow -NoNewline
        Write-Host 'Install Engram for cross-session persistence'
        Write-Host '  https://github.com/gentleman-programming/engram' -ForegroundColor Cyan
        Write-Host ''
    }
    else {
        Write-Host ''
        Write-Warn 'No agents were set up.'
    }
}
catch {
    Write-Host ''
    Write-Fail "Setup failed: $_"
    Write-Host ''
    exit 1
}
