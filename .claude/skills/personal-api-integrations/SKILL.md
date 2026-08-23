---
name: personal-api-integrations
description: Wire up and troubleshoot the personal service APIs — Gmail, Todoist, Amplenote — including OAuth setup, token refresh, and the relay/automation scripts built on them. Use for "set up Gmail automation", "create a Todoist task", "sync to Amplenote", "my token expired", or when an integration script fails to authenticate.
---

# Personal API integrations

| Service | Guide | Scripts |
|---------|-------|---------|
| Gmail | `integrations/skill_gmail_automation.md`, `integrations/gmail-quick-start.txt` | `_scripts/setup_gmail_oauth.py`, `_automation/gmail_tools.py`, `_automation/gmail_thread_tools.py` |
| Todoist | `integrations/skill_todoist_api.md` | `_scripts/create_todoist_task.py`, `_scripts/update_todoist_task.py`, `_automation/todoist_tools.py` |
| Amplenote | `integrations/skill_amplenote_api.md`, `integrations/skill_amplenote_relay_systems.md` | `_scripts/refresh_amplenote_token.js`, `_automation/amplenote_tools.py` |
| Calendar | — | `_automation/calendar_tools.py`, `_scripts/get_calendar_events.py`, `_tools/list_calendars.py` |
| Microsoft 365 / Graph | `_scripts/GRAPH_API_TECH_SUPPORT_REQUEST.md` | `_scripts/setup_microsoft_oauth.py` |

OAuth tokens refresh through `_automation/auth_manager.py`, which reads credentials via
`_automation/credential_resolver.py`. Long-lived secrets live in the KeePass vault `API/` group —
see `keepass-lookup`. Run `python _scripts/authenticate_all.py` to re-auth everything at once.
