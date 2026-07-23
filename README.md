# aitools

Reusable agentic skills for automation tasks on the REI / FDA project.

## Structure
- `skills/` -- Individual skill modules (each has `main.py` + `skill.md`)
- `shared/` -- Shared utilities: `keepass_helper.py`, `http_client.py`, `logger.py`
- `SKILLS_INDEX.md` -- Quick lookup table
- `SKILLS_DIRECTORY.md` -- Full skill documentation

## Usage
Skills with hyphenated directory names (like `jira-call`) must be loaded via `importlib`:

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "jira_call",
    r"C:\projects\aitools\skills\jira\jira-call\main.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
get_issue = mod.get_issue
search = mod.search
```

Each skill's `run(inputs)` function is the standard entry point.

## KeePass
Secrets are stored in `C:\keys\automation-keys.kdbx` (key file: `C:\keys\automation-keys.keyfile`).
Skills load secrets automatically -- no need to pass credentials manually.