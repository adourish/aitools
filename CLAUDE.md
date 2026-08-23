# CLAUDE.md — aitools

Guidance for Claude Code working in this repository.

---

## What this repo is

**aitools** is the shared **skill library** for the REI laptop — roughly 70 reference guides plus
the working scripts behind them. It is *how-to knowledge*, not an application: there is no build,
no deploy, no test suite. The code that does exist (`_automation/`, `_scripts/`, `_tools/`) is
automation the guides tell you to run.

It covers four broad areas:

| Area | Examples |
|------|----------|
| Salesforce / BPHC delivery | Apex, LWC, SOQL, FLS, Copado, deployments, E2E tests |
| Enterprise tooling | Azure DevOps, Azure SQL, Splunk, git/GitHub, MCP servers |
| Documentation & accessibility | Feature docs, wireframes, Mermaid/Visio diagrams, Section 508, TEG templates |
| Personal automation | Daily planning, email triage, PARA filing, Gmail/Todoist/Amplenote |

On the FDA GFE laptop this repo does not exist — the equivalent libraries there are
`fda-serio/fdaskills/` and `ai-sdlc-playbook/skills/`. Keep shared helpers in step by hand.

---

## On session start

1. Skim `.claude/skills/` — those are the routers Claude Code loads.
2. `skills_manifest.json` is the machine-readable catalogue; `SKILLS_CONTEXT.md` says *when* to
   reach for what; `README.md` is the long-form version.
3. Check `skills_config.json` for `SKILLS_ROOT` / `PARA_ROOT` before touching anything path-dependent.

---

## How skills are wired

Two layers, on purpose:

```
.claude/skills/<name>/SKILL.md     router — frontmatter + when to use + pointers   (Claude loads these)
<category>/skill_<topic>.md        the deep guide — read when a router sends you there
_automation/ _scripts/ _tools/     the scripts the guides run
```

The routers stay short so many can be loaded cheaply; the deep guides stay long because they are
read on demand. Do not paste a deep guide into a router.

### The routers

| Skill | Covers |
|-------|--------|
| `keepass-lookup` | Read any credential out of the automation vault |
| `environments-credentials` | Where a secret lives, lookup order, OAuth setup |
| `salesforce-development` | Apex, LWC, SOQL, FLS, REST API, deployment, cache busting |
| `copado-cicd` | Copado CLI, user stories, promotion paths, deployments |
| `azure-devops` | ADO work items, BPHC feature/task conventions, Azure SQL, Splunk |
| `git-workflow` | Branching, gitflow, PRs, multi-remote push |
| `e2e-testing` | Playwright specs, browser automation |
| `mermaid-visio-diagrams` | Mermaid, Visio, icon libraries, conversions |
| `section-508` | Accessibility rules, colour palette, accessible diagrams |
| `feature-documentation` | Feature docs, wireframes, design process, handoff, definition of done |
| `teg-documents` | TEG discussion docs and one-pagers |
| `daily-productivity` | Daily plan, email triage, PARA filing, process-new, routing rules |
| `personal-api-integrations` | Gmail, Todoist, Amplenote, Calendar, Microsoft 365 |
| `powershell-automation` | PowerShell patterns and Windows gotchas |
| `mcp-servers` | MCP setup and building a server |
| `skill-library` | Navigate the library, add a skill, keep the indexes honest |
| `internal-comms` | Status reports, 3P updates, newsletters, incident reports |
| `doc-coauthoring` | Long-form writing with the user; docx/pdf/pptx/xlsx handling |

`team/` holds the BPHC agent personas (DEWEY, GORT, HUEY, LOUIE, ROBBY, VINCENT) plus `TEAM.md`.
They are agents, not skills — the `team` repo's `CLAUDE.md` owns how they are dispatched.

---

## Secrets — the automation KeePass vault

**Every credential comes from the vault at runtime. Nothing is hardcoded, nothing is committed.**

The vault (`automation-keys.kdbx`) is unlocked with a **key file and no master password**, so
agents and scheduled scripts can read it without a prompt.

| | Windows | Linux / macOS |
|---|---|---|
| database | `C:\keys\automation-keys.kdbx` | `~/keys/automation-keys.kdbx` |
| key file | `C:\keys\automation-keys.keyfile` | `~/keys/automation-keys.keyfile` |

Override either with `KEEPASS_DB` / `KEEPASS_KEY`. The master copy lives under
`G:\My Drive\Areas\Keys\` — **the key file never goes on Google Drive and never goes in a repo.**

```bash
pip install -r _tools/keepass/requirements.txt
python _tools/keepass/keepass_lookup.py doctor                       # confirm it unlocks
python _tools/keepass/keepass_lookup.py list --group DevOps          # never prints secrets
python _tools/keepass/keepass_lookup.py get "DevOps/FDA Jira PAT (sde.fda.gov)"
```

Groups: `Salesforce/` · `API/` · `Database/` · `DevOps/` · `Other/` · `aitools-environments/`.

Rules, without exception:

- **Never** put a secret in a script, doc, commit message, task file, log, or chat reply.
- Reference a credential **by its vault entry title**; resolve it at runtime.
- `list` / `find` / `doctor` are safe to run in front of anyone; only `get` emits a value, and its
  output must not be tee'd into a log.
- A new credential goes into the vault first, then gets referenced by title.
- `.kdbx`, `.keyfile`, `.env`, `environments.json` and token caches are git-ignored. Keep it that way.

Deeper background: `system/skill_environments_credentials.md` and
`integrations/skill_keepass_integration.md`.

---

## Paths

Nothing should hardcode `G:\My Drive`. `skills_config.json` defines:

- `SKILLS_ROOT` — where this library lives
- `PARA_ROOT` — the PARA root (Projects / Areas / Resources / Archive)

See `CONFIGURATION.md` and `PATH_CONFIGURATION_SUMMARY.md`. On Windows, call scripts by full path
(`C:\projects\aitools\_scripts\sfsync.ps1`) — a bare relative path makes PowerShell look for a
*module* by that name and fail.

---

## Adding or changing a skill

1. Write the deep guide at `<category>/skill_<name>.md`.
2. Add a router at `.claude/skills/<name>/SKILL.md` — frontmatter needs `name` and a `description`
   written in third person that says **when** to use it, including the phrases a user would type.
3. Update `skills_manifest.json`, `README.md`, and `SKILLS_CONTEXT.md`.
4. Conventions: `system/skill_organizing_skills.md`. README upkeep: `system/skill_readme_maintenance.md`.
   Evaluating a skill properly: `_tools/skill-creator/SKILL.md`.
5. Verify every path a router cites actually exists before committing. Stale pointers are the main
   failure mode of a library this size.

---

## Conventions

- **Never `git add -A`.** Name the specific files. This repo sits next to credential files.
- **Section 508 / WCAG on everything that ships** — UI, diagram, document. Colour is never the only
  signal; the palette is cyan / yellow / magenta, never red/green alone.
- **Plain language.** Deliverables should be handable to a non-technical reader; define a technical
  term in parentheses the first time it appears.
- **No author attribution** in deliverables — no personal names, no "Claude", no model names.
- **Absolute dates.** Write `2026-08-23`, not "today".
- **Playwright via the `npx playwright` CLI**, not the MCP Playwright tools.

---

## Known drift

`skills_manifest.json` (last updated 2026-03-31) still lists v1 commands that no longer exist —
`run_process_new.py` under `G:\My Drive\06_Skills\_tools`, and `_scripts/email_processor.py`. The
live intake entry point is `_automation/run_process_new_v2.py`. Fix a manifest entry when you touch
its skill rather than leaving it to rot.

---

## Related repos

| Repo | What it is |
|------|-----------|
| `team` | BPHC-GAM2010 team coordination, agent dispatch, handshake protocol |
| `fda-serio` | FDA SERIO research + the agent bridge to the FDA laptop; `fdaskills/` is the FDA-side library |
| `ai-sdlc-playbook` | FDA OII AI SDLC repo; `skills/` is the FDA-side skill set |
| `whitepapers` | Long-form writing, PARA-organised |
| `robodog` | Agentic terminal used to drive browsers on the FDA laptop |

If you change a shared helper here that also exists in `fda-serio/fdaskills/shared/` or
`ai-sdlc-playbook/shared/`, port the change by hand — they share a design but different import roots.
