# Install-ClaudeCodeElsa.ps1 - set up Claude Code to run against the FDA ELSA gateway, plus the
# shared status line + settings. Idempotent; backs up any existing settings.json before merging.
#
#   .\Install-ClaudeCodeElsa.ps1                 # install ELSA launcher + status line + settings
#   .\Install-ClaudeCodeElsa.ps1 -Only elsa      # ELSA launcher only (top priority)
#   .\Install-ClaudeCodeElsa.ps1 -Only statusline # status line + settings only
[CmdletBinding()]
param(
    [ValidateSet('all', 'elsa', 'statusline')]
    [string]$Only = 'all',
    [string]$InstallDir = "$env:USERPROFILE\bin"   # where claude-elsa.ps1 goes (put this on PATH)
)
$ErrorActionPreference = 'Stop'
$src = $PSScriptRoot
$claudeDir = Join-Path $env:USERPROFILE '.claude'
New-Item -ItemType Directory -Force $claudeDir | Out-Null

# ---------- ELSA launcher (top priority) ----------
if ($Only -in 'all', 'elsa') {
    New-Item -ItemType Directory -Force $InstallDir | Out-Null
    Copy-Item (Join-Path $src 'claude-elsa.ps1') (Join-Path $InstallDir 'claude-elsa.ps1') -Force
    Write-Host "OK  installed claude-elsa.ps1 -> $InstallDir" -ForegroundColor Green

    # add a convenience CMD shim so `claude-elsa` works from any shell on PATH
    $shim = Join-Path $InstallDir 'claude-elsa.cmd'
    "@echo off`r`npowershell -NoProfile -ExecutionPolicy Bypass -File `"%~dp0claude-elsa.ps1`" %*" |
        Set-Content -Encoding ASCII $shim
    Write-Host "OK  wrote shim claude-elsa.cmd" -ForegroundColor Green

    # ensure InstallDir is on the user PATH
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$InstallDir", 'User')
        Write-Host "OK  added $InstallDir to your user PATH (open a new terminal to pick it up)" -ForegroundColor Green
    }
    Write-Host "    -> run 'claude-elsa' to start Claude Code against ELSA (Sonnet 4.6)." -ForegroundColor DarkGray
}

# ---------- status line + settings (secondary) ----------
if ($Only -in 'all', 'statusline') {
    Copy-Item (Join-Path $src 'statusline-command.sh') (Join-Path $claudeDir 'statusline-command.sh') -Force
    Write-Host "OK  installed statusline-command.sh" -ForegroundColor Green

    $settingsPath = Join-Path $claudeDir 'settings.json'
    $template = Get-Content -Raw (Join-Path $src 'settings.template.json') | ConvertFrom-Json
    if (Test-Path $settingsPath) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        Copy-Item $settingsPath "$settingsPath.backup-$stamp"
        $cur = Get-Content -Raw $settingsPath | ConvertFrom-Json
        # Set ONLY the statusLine key. Everything else (env, permissions, enabledPlugins,
        # MCP servers, theme, model, secrets) is personal to this machine and is left untouched.
        $cur | Add-Member -NotePropertyName 'statusLine' -NotePropertyValue $template.statusLine -Force
        ($cur | ConvertTo-Json -Depth 20) | Set-Content -Encoding UTF8 $settingsPath
        Write-Host "OK  set statusLine in settings.json (backup: settings.json.backup-$stamp; everything else preserved)" -ForegroundColor Green
    } else {
        ($template | ConvertTo-Json -Depth 20) | Set-Content -Encoding UTF8 $settingsPath
        Write-Host "OK  wrote new settings.json from template" -ForegroundColor Green
    }
    Write-Host "    -> status line is active on the next Claude Code start." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Done. Verify ELSA:  claude-elsa -p 'reply with OK'" -ForegroundColor Cyan
