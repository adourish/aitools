---
name: keepass-lookup
description: Look up a secret from the FDA automation KeePass vault. Use whenever you need a credential (API token, password, username, URL) stored in the automation-keys.kdbx vault — Jenkins token, Jira PAT, ELSA keys, Oracle DB password, etc. Wraps keepassxc-cli; no password prompt needed (key-file auth). Works on both the FDA GFE laptop (C:\keys\) and the REI laptop (G:\My Drive\Areas\Keys\).
metadata:
  version: "1.0.0"
  runtime: python
  requires: keepassxc-cli on PATH (installed via KeePassXC MSI)
---

# Skill: keepass-lookup

Retrieve a single field from the **FDA automation KeePass vault** (`automation-keys.kdbx`).

## Vault locations (auto-discovered in order)

| Priority | DB path | Key file path | Machine |
|----------|---------|---------------|---------|
| 1 | `$KEEPASS_DB` env var | `$KEEPASS_KEY` env var | any |
| 2 | `C:\keys\automation-keys.kdbx` | `C:\keys\automation-keys.keyfile` | FDA GFE laptop |
| 3 | `G:\My Drive\Areas\Keys\automation-keys.kdbx` | `C:\Users\adourish\.keepass\automation-keys.keyfile` | REI laptop |

## Prerequisites

- **KeePassXC** installed (MSI from `tools/install/bundle/` or the FDA laptop's software center)
- `keepassxc-cli` on PATH — the MSI installs it to `C:\Program Files\KeePassXC\` but does **not** add it to PATH automatically. Add it:
  ```powershell
  $env:PATH += ";C:\Program Files\KeePassXC"
  ```
- The vault (`automation-keys.kdbx`) and key file present at one of the locations above.

## Known entry paths

| Entry path | Fields used | Used by |
|-----------|-------------|---------|
| `DevOps/FDA Jira PAT (sde.fda.gov)` | Password | jira-call, runner |
| `DevOps/FDA Jenkins API token (jenkins.fda.gov)` | Password, UserName | jenkins-call, runner |
| `Database/SERIO Oracle DB (oasis_er) Dev-Test` | Password, UserName | db-query |
| `API/SEMOSS-Elsa-Dev` (or `aitools-environments/SEMOSS-Elsa-Dev`) | Password (secret), UserName (access key) | claude-elsa |

## Python usage

```python
from shared.keepass_helper import get_secret

# Get the Jira PAT
pat = get_secret("DevOps/FDA Jira PAT (sde.fda.gov)")

# Get a specific field
user = get_secret("DevOps/FDA Jenkins API token (jenkins.fda.gov)", field="UserName")
token = get_secret("DevOps/FDA Jenkins API token (jenkins.fda.gov)", field="Password")

# Get Oracle DB password
db_pass = get_secret("Database/SERIO Oracle DB (oasis_er) Dev-Test")
```

## PowerShell usage

```powershell
# Inline (copy of the pattern used in claude-elsa.ps1 and Watch-FdaSerioCommands.ps1)
$cli = 'C:\Program Files\KeePassXC\keepassxc-cli.exe'
$kf  = @("C:\keys\automation-keys.keyfile", "$env:USERPROFILE\.keepass\automation-keys.keyfile") |
       Where-Object { Test-Path $_ } | Select-Object -First 1
$db  = @("C:\keys\automation-keys.kdbx", "G:\My Drive\Areas\Keys\automation-keys.kdbx") |
       Where-Object { Test-Path $_ } | Select-Object -First 1

$secret = (& $cli show --key-file $kf --no-password -a Password $db "DevOps/FDA Jira PAT (sde.fda.gov)" 2>$null |
           Select-Object -First 1) -as [string]
$secret = $secret.Trim()
```

Or use the reusable helper from `tools/keepass/Get-KeePassAttr.ps1`:

```powershell
. C:\projects\aitools\tools\keepass\Get-KeePassAttr.ps1

$pat   = Get-KeePassAttr "DevOps/FDA Jira PAT (sde.fda.gov)"
$token = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)"
$user  = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)" -Attr UserName
```

## CLI usage (quick lookup from terminal)

```powershell
$cli = 'C:\Program Files\KeePassXC\keepassxc-cli.exe'
$db  = 'C:\keys\automation-keys.kdbx'
$kf  = 'C:\keys\automation-keys.keyfile'

# List all entries
& $cli ls --key-file $kf --no-password $db

# Show all fields for an entry
& $cli show --key-file $kf --no-password $db "DevOps/FDA Jira PAT (sde.fda.gov)"

# Get just the password
& $cli show --key-file $kf --no-password -a Password $db "DevOps/FDA Jira PAT (sde.fda.gov)"
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `keepassxc-cli` not found | Add `C:\Program Files\KeePassXC` to PATH |
| `Database key error` | Check key file path — must match what the vault was saved with |
| `Entry not found` | Use `& $cli ls` to browse the entry hierarchy |
| `FileNotFoundError: KeePass vault not found` | Set `KEEPASS_DB` + `KEEPASS_KEY` env vars, or place vault at `C:\keys\` |
| FDA laptop has no vault | Copy `automation-keys.kdbx` + `automation-keys.keyfile` to `C:\keys\` (they're in the onboarding package) |
