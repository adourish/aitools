---
name: powershell-automation
description: PowerShell scripting patterns for this toolkit — script structure, parameters, error handling, and the Windows-specific gotchas (execution policy, UTF-8 BOM, calling scripts by full path). Use when writing or fixing a .ps1, or when a PowerShell script fails to parse or run.
---

# PowerShell automation

Main guide: `automation/skill_powershell_automation.md`.

## Gotchas that have cost real time

- **Save scripts as UTF-8 with BOM** so Windows PowerShell 5.1 parses them correctly, and keep
  the contents ASCII.
- **Call scripts by full path** (`C:\projects\aitools\_scripts\sfsync.ps1`). A bare relative
  path like `_scripts\x.ps1` makes PowerShell try to load a *module* named `_scripts` and fail.
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for a one-off run.
- `2>&1` on a native exe in PS 5.1 renders stderr as red "errors" — cosmetic, not a failure.
- A script run by a watcher or scheduler gets `-NoProfile`, so it does **not** inherit your
  interactive PATH/JAVA_HOME. Set the toolchain inside the script.

Existing scripts to copy from: `_scripts/Resolve-Credential.ps1`, `_scripts/sfsync.ps1`.
