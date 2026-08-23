---
name: skill-library
description: Navigate, maintain and extend this skills library — find the right guide out of ~70, add a new skill, keep the manifest and README in sync, and follow the organisation conventions. Use for "what skills do I have", "find a skill for X", "add a new skill", "update the skills index", or "how is this repo organised".
---

# The aitools skill library

~70 reference guides plus working scripts. Two layers:

- **`.claude/skills/*/SKILL.md`** — what Claude Code loads. Each one is a short router that points
  at the deep guides. You are reading one now.
- **`<category>/skill_*.md`** — the deep guides themselves. Read these when the router sends you there.

## Find something

| Index | What it gives you |
|-------|-------------------|
| `skills_manifest.json` | Machine-readable: id, path, category, tags, dependencies, command |
| `README.md` | The long-form catalogue |
| `SKILLS_CONTEXT.md` | When to reach for which skill |
| `SKILLS_DIAGRAM.md` | How the skills relate to each other |
| `QUICKSTART.md` | Getting started end to end |
| `CONFIGURATION.md`, `PATH_CONFIGURATION_SUMMARY.md` | `SKILLS_ROOT` / `PARA_ROOT` setup |

```bash
python -c "import json;print('\n'.join(f\"{s['id']:34}{s['path']}\" for s in json.load(open('skills_manifest.json'))['skills']))"
```

## Add or change a skill

1. Write the deep guide at `<category>/skill_<name>.md`.
2. Add or extend a `.claude/skills/<name>/SKILL.md` router so Claude Code can find it — frontmatter
   needs `name` and a `description` that says *when* to use it, in third person.
3. Add the entry to `skills_manifest.json`, and to `README.md` / `SKILLS_CONTEXT.md`.
4. Conventions: `system/skill_organizing_skills.md`. README upkeep: `system/skill_readme_maintenance.md`.
5. Building and evaluating a skill properly: `_tools/skill-creator/SKILL.md`.

## Paths

Never hardcode `G:\My Drive`. Read `SKILLS_ROOT` and `PARA_ROOT` from `skills_config.json`.
