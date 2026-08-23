---
name: keepass-lookup
description: Retrieve credentials, API tokens, database passwords and org logins from the automation KeePass vault (automation-keys.kdbx) instead of hardcoding them. Use whenever a script, skill or agent needs a secret — a Jira/Jenkins/GitLab PAT, a Salesforce sandbox login, an Oracle or SQL Server password, an API key — or when the user asks "where is the password for X", "get my token", "what's the connection string", or a command fails with an auth error.
---

# KeePass Lookup — the automation vault

Every secret this library uses lives in the **automation KeePass vault**. It is unlocked with a
**key file and no master password**, so agents and unattended scripts can read it without a prompt.

**Never** paste a secret into a script, a doc, a commit, a task file, or chat. Reference it by
its vault entry title and read it at runtime.

## Setup (one-time per machine)

```bash
pip install -r _tools/keepass/requirements.txt
```

Put the vault and key file where the helper looks for them:

| | Windows | Linux / macOS |
|---|---|---|
| database | `C:\keys\automation-keys.kdbx` | `~/keys/automation-keys.kdbx` |
| key file | `C:\keys\automation-keys.keyfile` | `~/keys/automation-keys.keyfile` |

Or point at them explicitly with `KEEPASS_DB` / `KEEPASS_KEY`. On the personal machine the
master copy lives in `G:\My Drive\Areas\Keys\` — but **the key file never goes on Google
Drive and never goes in a repo.**

Verify:

```bash
python _tools/keepass/keepass_lookup.py doctor
```

## Use it

```bash
# See what's in the vault — never prints a secret
python _tools/keepass/keepass_lookup.py list
python _tools/keepass/keepass_lookup.py list --group DevOps
python _tools/keepass/keepass_lookup.py find jenkins

# Read one field
python _tools/keepass/keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)" --field password
python _tools/keepass/keepass_lookup.py get "Database/SERIO Oracle DB (oasis_er) Dev-Test" --field username
```

From Python:

```python
import sys; sys.path.insert(0, r"C:\projects\aitools\_tools\keepass")
from keepass_lookup import get_secret

pat = get_secret("DevOps/FDA Jira PAT (sde.fda.gov)")
```

From PowerShell:

```powershell
$env:JIRA_PAT = python C:\projects\aitools\_tools\keepass\keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)"
```

## What's in the vault

| Group | Holds |
|-------|-------|
| `Salesforce/` | BPHC + DME sandbox logins (COM, LGP, PRM, PWPM, REI QA/UAT, DME Dev 5/7), Enterprise Hub |
| `API/` | GitHub, Todoist, Amplenote, Figma, OpenRouter, Gmail, Microsoft 365 |
| `Database/` | SERIO Oracle (`oasis_er`), GEMS, BHCMIS |
| `DevOps/` | FDA Jira PAT, FDA Jenkins API token, FDA GitLab PAT, Azure DevOps (HRSA + REI) |
| `Other/` | Misc personal logins |
| `aitools-environments/` | Machine-generated environment records — EHBs UTL/SBX/PERF, Salesforce orgs, ADO, M365 |
| root | UniFi, Chrome Remote Desktop, SEMOSS/ELSA dev + service account, AWS GovCloud (SAML/PIV) |

Run `list` for the current, authoritative titles — the table above is a map, not a source of truth.

## Rules

- `list` / `find` / `doctor` never print secret values. `get` prints exactly one field so it can be
  captured into a variable — do not tee it into a log file.
- Adding a credential: `keepassxc-cli add` into the right group, then reference it in the runbook
  **by entry title only**.
- If the vault or key file is missing, `doctor` says which one and where it looked. Do not work
  around it by hardcoding — fix the path.

Background and the older `keys pass.kdbx` database: `integrations/skill_keepass_integration.md`.
