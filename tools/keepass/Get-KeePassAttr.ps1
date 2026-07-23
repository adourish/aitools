# Get-KeePassAttr.ps1
# Retrieve a single attribute from the FDA automation KeePass vault.
#
# Vault locations auto-discovered in this order (env overrides win):
#   1. $env:KEEPASS_DB / $env:KEEPASS_KEYFILE
#   2. C:\keys\automation-keys.kdbx + C:\keys\automation-keys.keyfile         (FDA GFE laptop)
#   3. G:\My Drive\Areas\Keys\automation-keys.kdbx + C:\Users\<you>\.keepass  (REI laptop)
#
# Requires: KeePassXC installed (keepassxc-cli.exe in Program Files)
#
# Usage (dot-source then call):
#   . C:\projects\aitools\tools\keepass\Get-KeePassAttr.ps1
#   $pat   = Get-KeePassAttr "DevOps/FDA Jira PAT (sde.fda.gov)"
#   $token = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)"
#   $user  = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)" -Attr UserName
#
# Known entries:
#   DevOps/FDA Jira PAT (sde.fda.gov)                    Password = PAT
#   DevOps/FDA Jenkins API token (jenkins.fda.gov)        Password = API token, UserName = username
#   Database/SERIO Oracle DB (oasis_er) Dev-Test          Password = DB password
#   API/SEMOSS-Elsa-Dev (or aitools-environments/...)     Password = secret, UserName = access key

function Get-KeePassAttr {
    <#
    .SYNOPSIS
        Retrieve a single field from the automation KeePass vault.

    .PARAMETER Entry
        Full KeePass entry path, e.g. "DevOps/FDA Jira PAT (sde.fda.gov)".

    .PARAMETER Attr
        Field to read: Password (default), UserName, URL, Notes, or any custom attribute.

    .OUTPUTS
        String value of the field, or $null if not found / vault unavailable.

    .EXAMPLE
        $pat = Get-KeePassAttr "DevOps/FDA Jira PAT (sde.fda.gov)"
        $user = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)" -Attr UserName
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, Position = 0)]
        [string] $Entry,

        [Parameter(Position = 1)]
        [string] $Attr = 'Password'
    )

    if (-not $Entry) { return $null }

    $cli = 'C:\Program Files\KeePassXC\keepassxc-cli.exe'
    if (-not (Test-Path $cli)) {
        Write-Warning "keepassxc-cli not found at '$cli'. Install KeePassXC or add it to PATH."
        return $null
    }

    # Discover key file
    $kf = @(
        $env:KEEPASS_KEYFILE,
        'C:\keys\automation-keys.keyfile',
        "$env:USERPROFILE\.keepass\automation-keys.keyfile",
        'C:\Users\adourish\.keepass\automation-keys.keyfile'
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    # Discover vault DB
    $db = @(
        $env:KEEPASS_DB,
        'C:\keys\automation-keys.kdbx',
        'G:\My Drive\Areas\Keys\automation-keys.kdbx'
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    if (-not $kf) {
        Write-Warning "KeePass key file not found. Set `$env:KEEPASS_KEYFILE or place it at C:\keys\automation-keys.keyfile"
        return $null
    }
    if (-not $db) {
        Write-Warning "KeePass vault not found. Set `$env:KEEPASS_DB or place it at C:\keys\automation-keys.kdbx"
        return $null
    }

    try {
        $value = & $cli show --key-file $kf --no-password -a $Attr $db $Entry 2>$null |
                 Select-Object -First 1
        if ($value) { return ($value -as [string]).Trim() }
    } catch {
        Write-Warning "keepassxc-cli error for entry '$Entry': $_"
    }

    return $null
}


# ---------------------------------------------------------------------------
# Get-Secret: layered lookup — env var, then file, then KeePass
# Useful for scripts that want a single call regardless of where the secret lives.
# ---------------------------------------------------------------------------
function Get-Secret {
    <#
    .SYNOPSIS
        Get a secret via: env var -> file -> KeePass (in that order).

    .PARAMETER EnvVar
        Environment variable name to check first.

    .PARAMETER File
        Path to a git-ignored file containing the raw secret (plain text).

    .PARAMETER KeePassEntry
        KeePass entry path to fall back to.

    .PARAMETER Attr
        KeePass field (default: Password).

    .EXAMPLE
        $pat = Get-Secret -EnvVar FDA_JIRA_PAT -File .jira-pat -KeePassEntry "DevOps/FDA Jira PAT (sde.fda.gov)"
    #>
    [CmdletBinding()]
    param(
        [string] $EnvVar,
        [string] $File,
        [string] $KeePassEntry,
        [string] $Attr = 'Password'
    )

    if ($EnvVar) {
        $v = [Environment]::GetEnvironmentVariable($EnvVar)
        if ($v) { return $v.Trim() }
    }

    if ($File -and (Test-Path $File)) {
        $v = Get-Content $File -Raw -ErrorAction SilentlyContinue
        if ($v) { return $v.Trim() }
    }

    if ($KeePassEntry) {
        return (Get-KeePassAttr -Entry $KeePassEntry -Attr $Attr)
    }

    return $null
}
