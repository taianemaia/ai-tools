# install.ps1 — symlink agents/skills into %USERPROFILE%\.claude\ and copy agents into VS Code Copilot
#
# Requirements:
#   - Windows 10 1703+ with Developer Mode enabled, OR run as Administrator (for symlinks)
#   - PowerShell 5.1+
#
# Usage:
#   .\install.ps1
#   .\install.ps1 -DryRun     # preview without creating anything

param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot        = $PSScriptRoot
$claudeDir       = Join-Path $env:USERPROFILE ".claude"
# VS Code Copilot user agents dir — global, available in all workspaces
$vsCodePromptsDir = Join-Path $env:USERPROFILE ".copilot\agents"

function Write-Status($symbol, $color, $message) {
    Write-Host "  $symbol  $message" -ForegroundColor $color
}

# ── Claude Code: symlink each agents/ and skills/ subdirectory ────────────────

function Sync-ClaudeLinks($srcRoot, $dstRoot) {
    if (-not (Test-Path $srcRoot)) { return }
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstRoot -Force | Out-Null }

    Get-ChildItem -Path $srcRoot -Directory | ForEach-Object {
        $name    = $_.Name
        $srcPath = $_.FullName
        $dstPath = Join-Path $dstRoot $name

        if (Test-Path $dstPath) {
            $existing = Get-Item $dstPath
            if ($existing.LinkType -eq "SymbolicLink") {
                if ($existing.Target -eq $srcPath) {
                    Write-Status "=" White "Already linked (Claude): $name"
                    return
                }
                if (-not $DryRun) { Remove-Item $dstPath -Force }
                if (-not $DryRun) { New-Item -ItemType SymbolicLink -Path $dstPath -Target $srcPath | Out-Null }
                Write-Status "~" Yellow "Updated stale link (Claude): $name"
            } else {
                Write-Status "!" Red "Skipped — real directory exists, remove manually: $dstPath"
            }
            return
        }

        if ($DryRun) {
            Write-Status "?" Cyan "Would link (Claude): $dstPath -> $srcPath"
        } else {
            New-Item -ItemType SymbolicLink -Path $dstPath -Target $srcPath | Out-Null
            Write-Status "+" Green "Linked (Claude): $name"
        }
    }
}

# ── VS Code Copilot: copy main .md as <name>.agent.md into flat agents dir ───

function Sync-VSCodeAgents($srcRoot, $dstDir) {
    if (-not (Test-Path $srcRoot)) { return }
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }

    Get-ChildItem -Path $srcRoot -Directory | ForEach-Object {
        $name  = $_.Name
        $srcMd = Join-Path $_.FullName "$name.md"
        $dstMd = Join-Path $dstDir "$name.agent.md"

        if (-not (Test-Path $srcMd)) { return }   # skip agents with no matching .md file

        if ($DryRun) {
            Write-Status "?" Cyan "Would write (VS Code agents): $name.agent.md"
        } else {
            Copy-Item -Path $srcMd -Destination $dstMd -Force
            Write-Status "+" Green "Copied (VS Code agents): $name.agent.md"
        }
    }
}

# ── VS Code Copilot: copy each skill dir to %USERPROFILE%\.copilot\skills\<name>\ ──

function Sync-VSCodeSkills($srcRoot, $dstRoot) {
    if (-not (Test-Path $srcRoot)) { return }
    if (-not $DryRun) { New-Item -ItemType Directory -Path $dstRoot -Force | Out-Null }

    Get-ChildItem -Path $srcRoot -Directory | ForEach-Object {
        $name   = $_.Name
        $srcDir = $_.FullName
        $dstDir = Join-Path $dstRoot $name

        if ($DryRun) {
            Write-Status "?" Cyan "Would copy (VS Code skills): $name/"
        } else {
            if (Test-Path $dstDir) { Remove-Item $dstDir -Recurse -Force }
            Copy-Item -Path $srcDir -Destination $dstDir -Recurse -Force
            Write-Status "+" Green "Copied (VS Code skills): $name/"
        }
    }
}

# ── run ──────────────────────────────────────────────────────────────────────

Write-Host "Claude Code" -ForegroundColor White
Sync-ClaudeLinks (Join-Path $repoRoot "agents") (Join-Path $claudeDir "agents")
Sync-ClaudeLinks (Join-Path $repoRoot "skills") (Join-Path $claudeDir "skills")

Write-Host ""
Write-Host "VS Code Copilot" -ForegroundColor White
Sync-VSCodeAgents (Join-Path $repoRoot "agents") $vsCodePromptsDir
Sync-VSCodeSkills (Join-Path $repoRoot "skills") (Join-Path $env:USERPROFILE ".copilot\skills")

if ($DryRun) {
    Write-Host "`nDry run complete — nothing was changed." -ForegroundColor Cyan
} else {
    Write-Host "`nDone. Restart VS Code for agent changes to take effect." -ForegroundColor Green
}
