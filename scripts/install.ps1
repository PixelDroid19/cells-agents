#Requires -Version 5.1

<#
.SYNOPSIS
    Cells Agent Bundle installer for Windows
.DESCRIPTION
    Copies CELLS skills to your AI coding assistant's skill directory.
.PARAMETER Agent
    Install for a specific agent (non-interactive).
    Valid values: opencode, vscode, project-local, all-global, custom
.PARAMETER Path
    Custom install path (use with -Agent custom)
.PARAMETER Help
    Show help
.EXAMPLE
    .\install.ps1
.EXAMPLE
    .\install.ps1 -Agent opencode
.EXAMPLE
    .\install.ps1 -Agent custom -Path C:\my\skills
#>

[CmdletBinding()]
param(
    [ValidateSet('opencode', 'vscode', 'project-local', 'all-global', 'custom')]
    [string]$Agent,
    [string]$Path,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# ============================================================================
# Path Resolution
# ============================================================================

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoDir = Split-Path -Parent $ScriptRoot
$SkillsSrc = Join-Path $RepoDir 'skills'

$ToolPaths = @{
    'opencode'          = Join-Path $env:USERPROFILE '.config\opencode\skills'
    'opencode-commands' = Join-Path $env:USERPROFILE '.config\opencode\commands'
    'vscode'            = Join-Path '.' '.github\skills'
    'project-local'     = Join-Path '.' 'skills'
}

$CoreWorkflowCommands = @(
    'cells-init.md',
    'cells-explore.md',
    'cells-new.md',
    'cells-continue.md',
    'cells-ff.md',
    'cells-apply.md',
    'cells-verify.md',
    'cells-archive.md'
)

# ============================================================================
# Display Helpers
# ============================================================================

function Write-Header {
    Write-Host ''
    Write-Host ([char]0x2554 + ([string][char]0x2550 * 42) + [char]0x2557) -ForegroundColor Cyan
    Write-Host ([char]0x2551 + '      Cells Agent Bundle - Installer      ' + [char]0x2551) -ForegroundColor Cyan
    Write-Host ([char]0x2551 + '    CELLS workflows for AI assistants     ' + [char]0x2551) -ForegroundColor Cyan
    Write-Host ([char]0x255A + ([string][char]0x2550 * 42) + [char]0x255D) -ForegroundColor Cyan
    Write-Host ''
    Write-Host "  Detected: Windows (PowerShell $($PSVersionTable.PSVersion))" -ForegroundColor White
    Write-Host ''
}

function Write-Skill {
    param([string]$Name)
    Write-Host '  ' -NoNewline
    Write-Host ([char]0x2713) -ForegroundColor Green -NoNewline
    Write-Host " $Name"
}

function Write-Warn {
    param([string]$Message)
    Write-Host '  ! ' -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Err {
    param([string]$Message)
    Write-Host '  ' -NoNewline
    Write-Host ([char]0x2717) -ForegroundColor Red -NoNewline
    Write-Host " $Message"
}

function Write-NextStep {
    param(
        [string]$ConfigFile,
        [string]$ExampleFile
    )
    Write-Host ''
    Write-Host 'Next step: ' -ForegroundColor Yellow -NoNewline
    Write-Host "Add the orchestrator to your " -NoNewline
    Write-Host $ConfigFile -ForegroundColor White
    Write-Host "  See: " -NoNewline
    Write-Host $ExampleFile -ForegroundColor Cyan
}

function Write-EngramNote {
    Write-Host ''
    Write-Host 'Recommended persistence backend: ' -ForegroundColor Yellow -NoNewline
    Write-Host 'Engram' -ForegroundColor White
    Write-Host '  Engram repository' -ForegroundColor Cyan
    Write-Host '  If Engram is available, it will be used automatically (recommended)'
    Write-Host '  If not, falls back to ' -NoNewline
    Write-Host 'none' -ForegroundColor White -NoNewline
    Write-Host ' - enable ' -NoNewline
    Write-Host 'engram' -ForegroundColor White -NoNewline
    Write-Host ' or ' -NoNewline
    Write-Host 'openspec' -ForegroundColor White -NoNewline
    Write-Host ' for better results'
}

function Show-Usage {
    Write-Host 'Usage: .\install.ps1 [OPTIONS]'
    Write-Host ''
    Write-Host 'Options:'
    Write-Host '  -Agent NAME    Install for a specific agent (non-interactive)'
    Write-Host '  -Path DIR      Custom install path (use with -Agent custom)'
    Write-Host '  -Help          Show this help'
    Write-Host ''
    Write-Host 'Agents: opencode, vscode, project-local, all-global'
}

# ============================================================================
# Install Functions
# ============================================================================

function Test-SourceTree {
    $missing = 0
    $skillDirs = Get-ChildItem -Path $SkillsSrc -Directory -Filter 'cells-*'
    foreach ($skillDir in $skillDirs) {
        $skillFile = Join-Path $skillDir.FullName 'SKILL.md'
        if (-not (Test-Path $skillFile)) {
            Write-Err "Missing: $($skillDir.Name)/SKILL.md"
            $missing++
        }
    }

    $agentBrowserDir = Join-Path $SkillsSrc 'agent-browser'
    if ((Test-Path $agentBrowserDir) -and (-not (Test-Path (Join-Path $agentBrowserDir 'SKILL.md')))) {
        Write-Err 'Missing: agent-browser/SKILL.md'
        $missing++
    }
    if (-not (Test-Path (Join-Path $SkillsSrc '_shared'))) {
        Write-Err 'Missing: _shared/ directory'
        $missing++
    }
    if ($missing -gt 0) {
        Write-Host ''
        Write-Host 'Source validation failed. Is this a complete clone of the repository?' -ForegroundColor Red
        Write-Host ''
        exit 1
    }
}

function Install-Skills {
    param(
        [string]$TargetDir,
        [string]$ToolName
    )

    Write-Host ''
    Write-Host "Installing skills for " -ForegroundColor Blue -NoNewline
    Write-Host "$ToolName" -ForegroundColor White -NoNewline
    Write-Host '...' -ForegroundColor Blue

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    # Copy shared convention files (_shared/)
    $sharedSrc = Join-Path $SkillsSrc '_shared'
    $sharedTarget = Join-Path $TargetDir '_shared'

    if (Test-Path $sharedSrc) {
        New-Item -ItemType Directory -Path $sharedTarget -Force | Out-Null
        $sharedFiles = Get-ChildItem -Path $sharedSrc -Filter '*.md'
        $sharedCount = 0
        foreach ($file in $sharedFiles) {
            Copy-Item -Path $file.FullName -Destination $sharedTarget -Force
            $sharedCount++
        }
        if ($sharedCount -gt 0) {
            Write-Skill "_shared ($sharedCount convention files)"
        } else {
            Write-Warn "_shared directory found but no .md files to copy"
        }
    }

    $count = 0
    $skillDirs = Get-ChildItem -Path $SkillsSrc -Directory -Filter 'cells-*'

    foreach ($skillDir in $skillDirs) {
        $skillName = $skillDir.Name
        $skillFile = Join-Path $skillDir.FullName 'SKILL.md'

        if (-not (Test-Path $skillFile)) {
            Write-Warn "Skipping $skillName (SKILL.md not found in source)"
            continue
        }

        $targetSkillDir = Join-Path $TargetDir $skillName
        if (Test-Path $targetSkillDir) {
            Remove-Item -Path $targetSkillDir -Recurse -Force
        }

        Copy-Item -Path $skillDir.FullName -Destination $TargetDir -Recurse -Force

        $pycache = Join-Path $targetSkillDir '__pycache__'
        if (Test-Path $pycache) {
            Remove-Item -Path $pycache -Recurse -Force
        }

        Get-ChildItem -Path $targetSkillDir -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item -Path $_.FullName -Recurse -Force
        }

        Write-Skill $skillName
        $count++
    }

    $agentBrowserDir = Join-Path $SkillsSrc 'agent-browser'
    if (Test-Path $agentBrowserDir) {
        $agentBrowserSkill = Join-Path $agentBrowserDir 'SKILL.md'
        if (Test-Path $agentBrowserSkill) {
            $targetAgentBrowserDir = Join-Path $TargetDir 'agent-browser'
            if (Test-Path $targetAgentBrowserDir) {
                Remove-Item -Path $targetAgentBrowserDir -Recurse -Force
            }

            Copy-Item -Path $agentBrowserDir -Destination $TargetDir -Recurse -Force

            Get-ChildItem -Path $targetAgentBrowserDir -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue | ForEach-Object {
                Remove-Item -Path $_.FullName -Recurse -Force
            }

            Write-Skill 'agent-browser'
            $count++
        }
        else {
            Write-Warn 'Skipping agent-browser (SKILL.md not found in source)'
        }
    }

    $registryDir = Join-Path $SkillsSrc 'skill-registry'
    if (Test-Path (Join-Path $registryDir 'SKILL.md')) {
        $targetRegistryDir = Join-Path $TargetDir 'skill-registry'
        if (Test-Path $targetRegistryDir) {
            Remove-Item -Path $targetRegistryDir -Recurse -Force
        }
        Copy-Item -Path $registryDir -Destination $TargetDir -Recurse -Force
        Write-Skill 'skill-registry'
        $count++
    }

    Write-Host ''
    Write-Host "  $count skills installed" -ForegroundColor Green -NoNewline
    Write-Host " -> $TargetDir"
}

function Install-OpenCodeCommands {
    $commandsSrc = Join-Path $RepoDir 'examples\opencode\commands'
    $commandsTarget = $ToolPaths['opencode-commands']

    Write-Host ''
    Write-Host 'Installing OpenCode commands...' -ForegroundColor Blue

    New-Item -ItemType Directory -Path $commandsTarget -Force | Out-Null

    $count = 0
    foreach ($cmdName in $CoreWorkflowCommands) {
        $sourceFile = Join-Path $commandsSrc $cmdName
        if (Test-Path $sourceFile) {
            Copy-Item -Path $sourceFile -Destination (Join-Path $commandsTarget $cmdName) -Force
            Write-Skill ([System.IO.Path]::GetFileNameWithoutExtension($cmdName))
            $count++
        }
        else {
            Write-Warn "Skipping missing workflow command: $([System.IO.Path]::GetFileNameWithoutExtension($cmdName))"
        }
    }

    Write-Host ''
    Write-Host "  $count commands installed" -ForegroundColor Green -NoNewline
    Write-Host " -> $commandsTarget"
}

function Install-OpenCodePlugins {
    $pluginsSrc = Join-Path $RepoDir 'examples\opencode\plugins'
    if (-not (Test-Path $pluginsSrc)) {
        Write-Warn "Skipping OpenCode plugin assets (source not found: $pluginsSrc)"
        return
    }

    $pluginsTarget = Join-Path $env:USERPROFILE '.config\opencode\plugins'

    New-Item -ItemType Directory -Path $pluginsTarget -Force | Out-Null
    Copy-Item -Path (Join-Path $pluginsSrc 'background-agents.ts') -Destination (Join-Path $pluginsTarget 'background-agents.ts') -Force
    Copy-Item -Path (Join-Path $pluginsSrc 'BACKGROUND-AGENTS-README.md') -Destination (Join-Path $pluginsTarget 'BACKGROUND-AGENTS-README.md') -Force
    Write-Skill 'OpenCode optional background delegation assets'
}

# ============================================================================
# Agent Install Dispatcher
# ============================================================================

function Install-ForAgent {
    param([string]$AgentName)

    switch ($AgentName) {
        'opencode' {
            Install-Skills -TargetDir $ToolPaths['opencode'] -ToolName 'OpenCode'
            Install-OpenCodeCommands
            Install-OpenCodePlugins
            Write-Host ''
            Write-Host ([char]0x2554 + ([string][char]0x2550 * 62) + [char]0x2557) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '  ACTION REQUIRED: Add the cells-orchestrator agent config     ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '                                                              ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '  Copy the agent block from:                                  ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '    examples\opencode\opencode.json                           ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '  Into your:                                                  ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + "    $env:APPDATA\opencode\opencode.json                       " + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '                                                              ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x2551 + '  Without this, /cells-* commands will not find the agent.      ' + [char]0x2551) -ForegroundColor Yellow
            Write-Host ([char]0x255A + ([string][char]0x2550 * 62) + [char]0x255D) -ForegroundColor Yellow
        }
        'vscode' {
            Install-Skills -TargetDir $ToolPaths['vscode'] -ToolName 'VS Code (Copilot)'
            Write-NextStep '.github\copilot-instructions.md' '.github\instructions\copilot-instructions.md'
            Write-Warn 'Skills installed in current project (.github\skills\)'
        }
        'project-local' {
            Install-Skills -TargetDir $ToolPaths['project-local'] -ToolName 'Project-local'
            Write-Host ''
            Write-Warn "Skills installed in .\skills\ - relative to this project"
            Write-Warn "Compatibility: project-local no longer creates .\.opencode\ ; use examples\opencode\ with user-level .config\opencode setup instead"
        }
        'all-global' {
            Install-Skills -TargetDir $ToolPaths['opencode'] -ToolName 'OpenCode'
            Install-OpenCodeCommands
            Install-OpenCodePlugins
            Write-Host ''
            Write-Host 'Next steps:' -ForegroundColor Yellow
            Write-Host '  1. ' -NoNewline
            Write-Host '[REQUIRED] ' -ForegroundColor Yellow -NoNewline
            Write-Host 'Add orchestrator agent to ' -NoNewline
            Write-Host "$env:APPDATA\opencode\opencode.json" -ForegroundColor White
            Write-Host '     See: examples\opencode\opencode.json — without this, /cells-* commands will not work' -ForegroundColor Yellow
        }
        'custom' {
            $customPath = $Path
            if (-not $customPath) {
                $customPath = Read-Host 'Enter target path'
            }
            if (-not $customPath) {
                Write-Err 'No path provided'
                exit 1
            }
            Install-Skills -TargetDir $customPath -ToolName 'Custom'
        }
        default {
            Write-Err "Unknown agent: $AgentName"
            Write-Host ''
            Show-Usage
            exit 1
        }
    }
}

# ============================================================================
# Interactive Menu
# ============================================================================

function Show-Menu {
    Write-Host 'Select your AI coding assistant:' -ForegroundColor White
    Write-Host ''
    Write-Host "   1) OpenCode       ($($ToolPaths['opencode']))"
    Write-Host "   2) VS Code        ($($ToolPaths['vscode']))"
    Write-Host "   3) Project-local  ($($ToolPaths['project-local']))"
    Write-Host '   4) All global     (OpenCode)'
    Write-Host '   5) Custom path'
    Write-Host ''

    $choice = Read-Host 'Choice [1-5]'

    $agentMap = @{
        '1'  = 'opencode'
        '2'  = 'vscode'
        '3'  = 'project-local'
        '4'  = 'all-global'
        '5' = 'custom'
    }

    if ($agentMap.ContainsKey($choice)) {
        Install-ForAgent $agentMap[$choice]
    }
    else {
        Write-Err 'Invalid choice'
        exit 1
    }
}

# ============================================================================
# Main
# ============================================================================

try {
    if ($Help) {
        Show-Usage
        exit 0
    }

    Write-Header
    Test-SourceTree

    if ($Agent) {
        Install-ForAgent $Agent
    }
    else {
        Show-Menu
    }

    Write-Host ''
    Write-Host 'Done!' -ForegroundColor Green -NoNewline
    Write-Host ' Start using CELLS with: ' -NoNewline
    Write-Host '/cells-init' -ForegroundColor Cyan -NoNewline
    Write-Host ' in your project'

    Write-EngramNote
    Write-Host ''
}
catch {
    Write-Host ''
    Write-Err "Installation failed: $_"
    Write-Host ''
    exit 1
}
