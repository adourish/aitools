---
name: daily-productivity
description: Personal productivity automation — the daily Kanban plan, email triage into tasks, PARA filing of downloads and notes, the process-new intake pipeline, routing rules, and the quick-command reference. Use for "plan my day", "process my inbox", "file these downloads", "process new", "morning routine", or "where does this file go".
---

# Daily productivity & PARA

| Task | Guide | Run |
|------|-------|-----|
| Daily Kanban + task prioritisation | `automation/skill_daily_planning.md` | `python _automation/run_process_new_v2.py` |
| Intake pipeline (all 9 steps) | `system/skill_process_new.md`, `_automation/README.md` | same orchestrator |
| Email → tasks | `automation/skill_email_processing.md` | `_automation/gmail_tools.py`, `_automation/comprehensive_analyzer.py` |
| PARA filing of downloads and notes | `automation/skill_file_organization.md` | — |
| Where does this go — routing rules | `system/skill_routing_rules.md` | — |
| Quick filing / tool filing cheatsheets | `_tools/skill_quick_filing.md`, `_tools/skill_tool_filing.md` | — |
| Command cheatsheet | `system/skill_user_commands.md` | — |
| Archive recovery, torrent downloads | `automation/skill_archive_parts_recovery.md`, `automation/skill_torrent_downloads.md` | — |

Paths come from `skills_config.json` (`SKILLS_ROOT`, `PARA_ROOT`) — don't hardcode `G:\My Drive`.
API tokens come from the KeePass vault via `keepass-lookup`.

**`skills_manifest.json` commands are stale here.** It still points at `run_process_new.py` under
`G:\My Drive\06_Skills\_tools` and at an `email_processor.py` that no longer exists. The single
live entry point is `_automation/run_process_new_v2.py`; the v1 scripts were deprecated and removed.
