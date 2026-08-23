---
name: environments-credentials
description: Find where a credential, environment record or connection string lives across KeePass, environments.json, .env files and the credential resolver, and set up a new integration's auth. Use for "where are my credentials", "set up an API key", "which environment is X", "configure a new integration", or when a script fails with an authentication error and you need the lookup order.
---

# Environments & Credentials

The lookup order for any secret is: **KeePass vault → `environments.json` → `.env`**.

1. **KeePass first** — see the `keepass-lookup` skill. That is where anything new should go.
2. **`environments.json`** — per-environment records (EHBs, Salesforce orgs, databases). Git-ignored.
3. **`.env`** — per-project runtime config. Git-ignored. Never a place for a long-lived secret.

## Read these

| Need | Guide |
|------|-------|
| Full credential-management guide, storage layout, security checklist | `system/skill_environments_credentials.md` |
| KeePass access patterns (Python + PowerShell), search examples | `integrations/skill_keepass_integration.md` |
| Vault backup automation | `automation/skill_keepass_backup_automation.md` |

## Working code

| File | What it does |
|------|--------------|
| `_tools/keepass/keepass_lookup.py` | Read the automation vault (key file, no prompt) |
| `_automation/credential_resolver.py` | Cascading resolver across pskills → aitools → skills → Keys, with AES-encrypted fields |
| `_automation/auth_manager.py` | OAuth token management + refresh for Gmail / Todoist / Amplenote |
| `_scripts/Resolve-Credential.ps1` | PowerShell equivalent of the resolver |
| `_scripts/setup_*_oauth.py` | First-time OAuth setup for Gmail / Microsoft 365 |

## Non-negotiables

- Never commit a credential, a `.kdbx`, a `.keyfile`, an `environments.json`, or a token cache.
- Never print a secret to a log, a console transcript, or a commit message.
- Rotate quarterly; use least-privilege tokens.
