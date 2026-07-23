# CLAUDE.md — aitools

This file provides guidance to Claude Code when working in this repository.

---

## What this repo is

**aitools** is the shared FDA AI tools and skills library — reusable agentic skills, scripts, and
runbooks for automation on the FDA GFE laptop and the REI development laptop.

It is intended to be the canonical, standalone home for skills and tools that were previously
living inside `fda-serio`. Anything in here should be usable across multiple projects.

**Repo:** `https://git.fda.gov/FDA/ORA/SI/aitools.git`

---

## Branch strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, tested skills and tools |
| `dev` | Integration branch — merge feature branches here first |
| `feature/*` | New skills, tools, or major updates |

**Always branch from `dev`, PR back to `dev`, then `dev` → `main` when stable.**

---

## Structure

```
aitools/
  skills/                   # Agentic skills (each has a SKILL.md entry point)
    jenkins/jenkins-call/   # Call FDA Jenkins CI/CD API
    jira/jira-call/         # Call FDA Jira REST API
    db-query/               # Query SERIO Oracle DB (Node.js)
    mermaid-section-508/    # Section 508-compliant Mermaid diagrams
    section-508-color-palette/  # Accessible color palette helper
    section-508-compliance/ # Section 508 compliance checker
    serio-dev-environment/  # SERIO dev environment setup
    serioplus-add-pdf-endpoint/ # Add PDF endpoints to SERIO+
    serioplus-local-run/    # Run SERIO+ locally
  shared/                   # Python utilities imported by all skills
    keepass_helper.py       # Retrieve secrets from KeePass vault
    http_client.py          # Thin stdlib HTTP wrapper (no third-party deps)
    logger.py               # Structured logger
  tools/
    claude-code/            # Claude Code ELSA launcher + statusline
  docs/
    runbooks/               # How-to runbooks for common tasks
  SKILLS_INDEX.md           # Quick lookup table
  SKILLS_DIRECTORY.md       # Full skill documentation
```

---

## Environment

Skills run on the **FDA GFE laptop** (government-furnished equipment) which:
- Is behind the FDA network / full-tunnel VPN
- Uses the FDA internal CA (self-signed certs are normal — `verify_ssl=False` is intentional)
- Stores secrets in KeePass at `C:\keys\automation-keys.kdbx`
- Signs in with ALT-PIV card + personal access tokens

The **REI laptop** can access this repo on GitHub but cannot reach FDA internal systems directly.

---

## Secrets / KeePass

All skills load credentials from the automation KeePass vault automatically.  
**Never hardcode tokens, passwords, or API keys.**

Default vault path: `C:\keys\automation-keys.kdbx`  
Key file: `C:\keys\automation-keys.keyfile`

Override via env vars: `KEEPASS_DB`, `KEEPASS_KEY`

See `shared/keepass_helper.py` for vault discovery logic.

---

## Import pattern (Python skills)

```python
import importlib.util, sys

# Skills with hyphenated dirs must use importlib:
spec = importlib.util.spec_from_file_location(
    "jira_call",
    r"C:\projects\aitools\skills\jira\jira-call\main.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
result = mod.run({"path": "/rest/api/2/issue/SERIO-42"})
```

Or add `C:\projects\aitools` to `sys.path` and use:
```python
from shared.keepass_helper import get_secret
```

---

## Import pattern (Node.js skills)

```powershell
node C:\projects\aitools\skills\db-query\db-query.js "SELECT * FROM shipments FETCH FIRST 5 ROWS ONLY"
```

Install deps first (one-time per environment):
```powershell
cd C:\projects\aitools\skills\db-query
npm install
```

---

## Adding a new skill

1. Create `skills/<category>/<skill-name>/` 
2. Add `main.py` (Python) or `<skill>.js` (Node.js) with a `run(inputs)` entry point
3. Add `SKILL.md` — this is the Claude Code skill descriptor (YAML front matter + docs)
4. Update `SKILLS_INDEX.md` and `SKILLS_DIRECTORY.md`
5. Branch from `dev`, PR back to `dev`

---

## Claude Code / ELSA

To run Claude Code against the FDA ELSA gateway on the GFE laptop:

```powershell
cd C:\projects\aitools\tools\claude-code
.\Install-ClaudeCodeElsa.ps1 -Only elsa
# new terminal:
claude-elsa -p "reply with OK"
```

See `tools/claude-code/README.md` and `docs/runbooks/RUNBOOK-claude-code-elsa.md`.
