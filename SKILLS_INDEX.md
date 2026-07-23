# AI Tools Skills Index

## Purpose
This index maps skill names to their locations and brief descriptions for quick lookup.

## Skills

| Skill | Runtime | Path | Description |
|-------|---------|------|-------------|
| [jenkins-call](skills/jenkins/jenkins-call/skill.md) | Python | `skills/jenkins/jenkins-call/` | Authenticated FDA Jenkins REST API (list jobs, trigger builds, get console) — auto-loads token from KeePass |
| [jira-call](skills/jira/jira-call/skill.md) | Python | `skills/jira/jira-call/` | Authenticated FDA Jira REST API (get, search, create, transition) — auto-loads PAT from KeePass |
| [db-query](skills/db-query/SKILL.md) | Node.js | `skills/db-query/` | Query SERIO Oracle database (dev/test) via VPN |
| [mermaid-section-508](skills/mermaid-section-508/SKILL.md) | (prompt) | `skills/mermaid-section-508/` | Section 508-compliant Mermaid diagrams |
| [section-508-color-palette](skills/section-508-color-palette/SKILL.md) | (prompt) | `skills/section-508-color-palette/` | Accessible color palette helper |
| [section-508-compliance](skills/section-508-compliance/SKILL.md) | (prompt) | `skills/section-508-compliance/` | Section 508 compliance checker |
| [serio-dev-environment](skills/serio-dev-environment/SKILL.md) | (prompt) | `skills/serio-dev-environment/` | SERIO WebLogic dev environment setup |
| [serioplus-add-pdf-endpoint](skills/serioplus-add-pdf-endpoint/SKILL.md) | (prompt) | `skills/serioplus-add-pdf-endpoint/` | Add PDF endpoint to SERIO+ |
| [serioplus-local-run](skills/serioplus-local-run/SKILL.md) | (prompt) | `skills/serioplus-local-run/` | Build and run SERIO+ locally |
| [keepass-lookup](skills/keepass-lookup/SKILL.md) | Python / PS | `skills/keepass-lookup/` | Look up any secret from the FDA automation KeePass vault |
| [gitlab-call](skills/gitlab/gitlab-call/SKILL.md) | Python | `skills/gitlab/gitlab-call/` | Authenticated FDA GitLab REST API (projects, MRs, branches, pipelines, issues) — token auto-loaded from Windows Credential Manager |

## Shared Utilities

| Module | Description |
|--------|-------------|
| `shared/keepass_helper.py` | Retrieve secrets from KeePass vault |
| `shared/http_client.py` | Thin stdlib HTTP wrapper (no third-party deps) |
| `shared/logger.py` | Structured logger |

## Tools

| Tool | Description |
|------|-------------|
| `tools/claude-code/` | Claude Code ELSA launcher, installer, and statusline |
| `tools/keepass/` | `Get-KeePassAttr.ps1` — PowerShell KeePass helper (dot-source and call) |