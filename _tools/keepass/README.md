# keepass_lookup

Reads credentials out of the **automation KeePass vault** (`automation-keys.kdbx`), which is
unlocked with a **key file and no master password** so unattended scripts and agents never hit a
password prompt.

## Install

```bash
pip install -r requirements.txt
```

## Where it looks

| | Windows | Linux / macOS |
|---|---|---|
| database | `C:\keys\automation-keys.kdbx` | `~/keys/automation-keys.kdbx` |
| key file | `C:\keys\automation-keys.keyfile` | `~/keys/automation-keys.keyfile` |

`KEEPASS_DB` and `KEEPASS_KEY` override both. It also falls back to
`G:\My Drive\Areas\Keys\automation-keys.kdbx` (the master copy) and
`~/.keepass/automation-keys.keyfile`.

**The key file never goes on Google Drive and never goes in a repo.** `*.kdbx` and `*.keyfile` are
git-ignored here for exactly that reason.

## Commands

```bash
python keepass_lookup.py doctor                      # which vault, which key file, does it unlock
python keepass_lookup.py list                        # every entry path — no secrets printed
python keepass_lookup.py list --group DevOps
python keepass_lookup.py find jenkins                # search title / username / url
python keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)"
python keepass_lookup.py get "Database/SERIO Oracle DB (oasis_er) Dev-Test" --field username
```

`get` writes exactly one field to stdout so it can be captured:

```bash
TOKEN=$(python keepass_lookup.py get "DevOps/FDA Jenkins API token (jenkins.fda.gov)")
```

```powershell
$env:JIRA_PAT = python C:\projects\aitools\_tools\keepass\keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)"
```

## As a library

```python
import sys; sys.path.insert(0, r"C:\projects\aitools\_tools\keepass")
from keepass_lookup import get_secret, open_vault

pat  = get_secret("DevOps/FDA GitLab PAT (git.fda.gov)")
user = get_secret("Database/SERIO Oracle DB (oasis_er) Dev-Test", field="username")
```

## Naming an entry

Pass the full group path (`DevOps/FDA Jira PAT (sde.fda.gov)`) or a title unique enough to match
one entry. An ambiguous name fails with a list of candidates rather than guessing.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | success |
| 1 | entry found but the requested field is empty |
| 2 | vault/key file not found, would not unlock, or entry not found / ambiguous |
| 3 | `pykeepass` not installed |

## Don't

- Don't tee `get` output into a log file, a commit, or a task file.
- Don't add a credential by hand-editing anything here — put it in the vault
  (`keepassxc-cli add`) and reference it by title.
