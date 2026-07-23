# tools/keepass — KeePass helpers

PowerShell helpers for reading secrets from the FDA automation KeePass vault.

## Files

| File | Purpose |
|------|---------|
| `Get-KeePassAttr.ps1` | `Get-KeePassAttr` + `Get-Secret` functions — dot-source and call |

## Quick start

```powershell
# Dot-source the helpers
. C:\projects\aitools\tools\keepass\Get-KeePassAttr.ps1

# Get a secret by KeePass entry path
$pat   = Get-KeePassAttr "DevOps/FDA Jira PAT (sde.fda.gov)"
$token = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)"
$user  = Get-KeePassAttr "DevOps/FDA Jenkins API token (jenkins.fda.gov)" -Attr UserName
$dbpw  = Get-KeePassAttr "Database/SERIO Oracle DB (oasis_er) Dev-Test"

# Layered lookup: env var -> file -> KeePass
$pat = Get-Secret -EnvVar FDA_JIRA_PAT `
                  -File   .jira-pat `
                  -KeePassEntry "DevOps/FDA Jira PAT (sde.fda.gov)"
```

## Vault locations (auto-discovered)

1. `$env:KEEPASS_DB` / `$env:KEEPASS_KEYFILE` — override via env
2. `C:\keys\automation-keys.kdbx` + `C:\keys\automation-keys.keyfile` — FDA GFE laptop
3. `G:\My Drive\Areas\Keys\automation-keys.kdbx` + `C:\Users\adourish\.keepass\automation-keys.keyfile` — REI laptop

## See also

- `skills/keepass-lookup/SKILL.md` — full docs including Python and CLI usage
- `shared/keepass_helper.py` — Python equivalent (`get_secret()`)
