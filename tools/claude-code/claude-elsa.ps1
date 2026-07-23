# claude-elsa.ps1 - launch Claude Code against the FDA ELSA gateway (Claude Sonnet 4.6).
#
# Points Claude Code at ELSA by setting the ANTHROPIC_* env vars for THIS process only, then
# hands off to `claude`. ELSA access/secret are pulled from the automation KeePass at launch
# (never hardcoded, never written to the repo). Any arguments are forwarded to claude.
#
#   claude-elsa                     # interactive session against ELSA
#   claude-elsa -p "say hi"         # headless, prints response
#   claude-elsa --model <id>        # forwarded to claude (overrides ANTHROPIC_MODEL)
#
# Overrides (env vars, all optional):
#   ELSA_CLAUDE_BASE_URL   default https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai
#   ELSA_CLAUDE_MODEL      default 8405ac40-89c6-4613-848c-3d89986fbc01  (Claude Sonnet 4.6)
#   ELSA_ACCESS_KEY / ELSA_SECRET_KEY   skip KeePass and use these directly
[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)] $ClaudeArgs)
$ErrorActionPreference = 'Stop'

$BaseUrl = if ($env:ELSA_CLAUDE_BASE_URL) { $env:ELSA_CLAUDE_BASE_URL } else { 'https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai' }
$Model   = if ($env:ELSA_CLAUDE_MODEL)    { $env:ELSA_CLAUDE_MODEL }    else { '8405ac40-89c6-4613-848c-3d89986fbc01' }  # Claude Sonnet 4.6

# --- ELSA credentials: env first, then the automation KeePass (access=UserName, secret=Password) ---
$access = $env:ELSA_ACCESS_KEY
$secret = $env:ELSA_SECRET_KEY
if (-not $access -or -not $secret) {
    $cli = 'C:\Program Files\KeePassXC\keepassxc-cli.exe'
    $kf  = @("C:\keys\automation-keys.keyfile", "$env:USERPROFILE\.keepass\automation-keys.keyfile") | Where-Object { Test-Path $_ } | Select-Object -First 1
    $db  = @("C:\keys\automation-keys.kdbx", "G:\My Drive\Areas\Keys\automation-keys.kdbx")            | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ((Test-Path $cli) -and $kf -and $db) {
        foreach ($entry in @('API/SEMOSS-Elsa-Dev', 'Other/SEMOSS-Elsa-Dev', 'SEMOSS-Elsa-Dev', 'aitools-environments/SEMOSS-Elsa-Dev')) {
            $s = (& $cli show --key-file $kf --no-password -a Password $db $entry 2>$null | Select-Object -First 1)
            if ($s) {
                $access = ((& $cli show --key-file $kf --no-password -a UserName $db $entry 2>$null | Select-Object -First 1) -as [string]).Trim()
                $secret = ($s -as [string]).Trim()
                Write-Host "loaded ELSA credentials from KeePass entry: $entry" -ForegroundColor DarkGray
                break
            }
        }
    } else {
        Write-Host "KeePassXC / automation vault not found; set ELSA_ACCESS_KEY + ELSA_SECRET_KEY instead." -ForegroundColor Yellow
    }
}
if (-not $access -or -not $secret) {
    Write-Error "ELSA credentials not found. Set ELSA_ACCESS_KEY + ELSA_SECRET_KEY, or add KeePass entry 'SEMOSS-Elsa-Dev' (UserName=access, Password=secret)."
    exit 2
}

# --- point Claude Code at ELSA (this process only) ---
$env:ANTHROPIC_BASE_URL         = $BaseUrl
$env:ANTHROPIC_AUTH_TOKEN       = "${access}:${secret}"   # ELSA Bearer format: <access>:<secret>
$env:ANTHROPIC_MODEL            = $Model
$env:ANTHROPIC_SMALL_FAST_MODEL = $Model
# Locked-down FDA env: keep non-essential outbound traffic off. Comment out if not wanted.
$env:DISABLE_TELEMETRY          = '1'
$env:DISABLE_ERROR_REPORTING    = '1'
$env:DISABLE_AUTOUPDATER        = '1'

Write-Host ("Claude Code -> ELSA  |  url={0}  model={1}  auth=set" -f $BaseUrl, $Model) -ForegroundColor Cyan

# Requires the FDA full-tunnel VPN (elsa-dev.preprod.fda.gov resolves only on it) and the internal
# CA trusted. If you get a TLS/self-signed error, see RUNBOOK-internal-git-cert.md / FS-009.
& claude @ClaudeArgs
exit $LASTEXITCODE
