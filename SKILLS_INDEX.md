# AI Tools Skills Index

## Purpose
This index maps skill names to their locations and brief descriptions for quick lookup.

## Skills

| Skill | Runtime | Path | Description |
|-------|---------|------|-------------|
| [jenkins-call](skills/jenkins/jenkins-call/skill.md) | Python | `skills/jenkins/jenkins-call/` | Authenticated FDA Jenkins REST API (list jobs, trigger builds, get console) — auto-loads token from KeePass |
| [jira-call](skills/jira/jira-call/skill.md) | Python | `skills/jira/jira-call/` | Authenticated FDA Jira REST API (get, search, create, transition) — auto-loads PAT from KeePass |
| [gitlab-call](skills/gitlab/gitlab-call/SKILL.md) | Python | `skills/gitlab/gitlab-call/` | Authenticated FDA GitLab REST API (projects, MRs, branches, pipelines, issues) — token auto-loaded from Windows Credential Manager |
| [db-query](skills/db-query/SKILL.md) | Node.js | `skills/db-query/` | Query SERIO Oracle database (dev/test) via VPN |
| [keepass-lookup](skills/keepass-lookup/SKILL.md) | Python / PS | `skills/keepass-lookup/` | Look up any secret from the FDA automation KeePass vault |
| [mermaid-section-508](skills/mermaid-section-508/SKILL.md) | (prompt) | `skills/mermaid-section-508/` | Section 508-compliant Mermaid diagrams |
| [section-508-color-palette](skills/section-508-color-palette/SKILL.md) | (prompt) | `skills/section-508-color-palette/` | Accessible color palette helper |
| [section-508-compliance](skills/section-508-compliance/SKILL.md) | (prompt) | `skills/section-508-compliance/` | Section 508 compliance checker |
| [serio-dev-environment](skills/serio-dev-environment/SKILL.md) | (prompt) | `skills/serio-dev-environment/` | SERIO WebLogic dev environment setup |
| [serio-cli](skills/serio-cli/SKILL.md) | PowerShell | `skills/serio-cli/` | **`serio start\|stop\|restart\|build\|status <target>`** — one tool for all SERIO/SERIO+ services |
| [serio-monolith](skills/serio-monolith/SKILL.md) | PowerShell | `skills/serio-monolith/` | Build and run the SERIO monolith (WebLogic :7001 + Angular :4200, JDK 21) |
| [serioplus-common-lib](skills/serioplus-common-lib/SKILL.md) | PowerShell | `skills/serioplus-common-lib/` | Build and install serioplus-common-library:13.0.0-SNAPSHOT — always step 1 before building any SERIO+ service |
| [serioplus-data-services](skills/serioplus-data-services/SKILL.md) | PowerShell | `skills/serioplus-data-services/` | Build and run SERIOPlusDataServices (8 Spring Boot data-tier services :8090-8097 + gateway :8070) |
| [serioplus-business-services](skills/serioplus-business-services/SKILL.md) | PowerShell | `skills/serioplus-business-services/` | Build and run SERIOPlusServices (7 Spring Boot business-tier services :8080-8086) |
| [serioplus-app](skills/serioplus-app/SKILL.md) | Node.js | `skills/serioplus-app/` | Build and run SERIOPlusApp Angular UI (ng serve :4201, /serioplus/) |
| [serioplus-add-pdf-endpoint](skills/serioplus-add-pdf-endpoint/SKILL.md) | (prompt) | `skills/serioplus-add-pdf-endpoint/` | Add PDF endpoint to SERIO+ |
| [serioplus-local-run](skills/serioplus-local-run/SKILL.md) | (prompt) | `skills/serioplus-local-run/` | Single-service detailed gotcha reference for running any SERIO+ service locally |

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
| `tools/serioplus/` | `SerioPlusStack.ps1` — build, start, stop, and status for the full SERIO+ stack (all tiers) |
| `tools/serio/` | `Serio.ps1` + `Install-SerioAlias.ps1` — the `serio` CLI: start/stop/restart/build/status for all tiers |