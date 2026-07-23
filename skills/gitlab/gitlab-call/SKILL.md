# Skill: gitlab-call

Read and write FDA GitLab resources on the internal instance (git.fda.gov).

## When to use

- Look up a project, branch, or commit on git.fda.gov
- List or open merge requests across SERIO+ repos
- Post a comment or approve an MR
- Trigger a pipeline or check pipeline status
- Create an issue in a GitLab project
- Look up a GitLab user's numeric ID for assignee fields

## Prerequisites

- **VPN full-tunnel connected** — git.fda.gov is only reachable on VPN
- **Token in Windows Credential Manager** — when you `git push` or `git pull`
  against `https://git.fda.gov` and enter your `glpat-*` token, Windows stores it
  automatically. The skill reads it from there non-interactively.
  Alternatively set the `GITLAB_TOKEN` environment variable.
- **Python stdlib only** — no third-party packages required (uses `shared/http_client.py`)

## How it works

1. Token is resolved: explicit `token=` input → `GITLAB_TOKEN` env var →
   Windows Git Credential Manager (`git credential fill` for host `git.fda.gov`)
2. Every call hits `https://git.fda.gov/api/v4/<path>` with a
   `PRIVATE-TOKEN: <token>` header (GitLab API v4)
3. FDA internal CA is in use — `verify_ssl=False` is intentional

## GitLab instance

| Property | Value |
|----------|-------|
| Base URL | `https://git.fda.gov/api/v4` |
| Version | GitLab 19.0.2-EE |
| Auth | Personal Access Token (`PRIVATE-TOKEN` header) |
| Token scopes | `api`, `read_api`, `read_repository`, `write_repository`, `read_user` |

## Known project IDs (FDA/ORA/SI)

| Repo | GitLab project ID |
|------|:-----------------:|
| aitools | 9639 |
| ai-sdlc-playbook | 8410 |
| SERIOPlusApp | 7256 |
| SERIOPlusCommonLibraries | 7254 |
| SERIOPlusDataServices | 7255 |
| SERIOPlusServices | 7253 |
| serioplusintegrationservices | 7271 |
| serioplusaiml | 7680 |
| Shared-AI-Service | 7882 |

Use `find_project_id("FDA/ORA/SI/<repo>")` to look up others dynamically.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | str | **Yes** | API path, e.g. `/projects/7255/merge_requests` |
| `method` | str | No | HTTP method: GET, POST, PUT, DELETE (default GET) |
| `body` | dict | No | Request body for POST/PUT |
| `token` | str | No | Override PRIVATE-TOKEN (auto-loaded if omitted) |
| `base_url` | str | No | Override base URL (default `https://git.fda.gov/api/v4`) |
| `verify_ssl` | bool | No | Verify SSL cert (default False — FDA internal CA) |
| `params` | dict | No | Query-string parameters appended to URL |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `status_code` | int | HTTP status code |
| `body` | dict \| list \| str | Parsed JSON or raw text |
| `ok` | bool | True if status_code < 400 |

## Convenience wrappers

### Projects
| Function | Description |
|----------|-------------|
| `get_project(project_id)` | Get project metadata |
| `list_projects(search, membership, per_page)` | List/search accessible projects |
| `find_project_id(namespace_path)` | Resolve full path → numeric ID |

### Merge Requests
| Function | Description |
|----------|-------------|
| `list_merge_requests(project_id, state, per_page)` | List MRs (state: opened/closed/merged/all) |
| `get_merge_request(project_id, mr_iid)` | Get a single MR by its project-local IID |
| `create_merge_request(project_id, source_branch, target_branch, title, ...)` | Open a new MR |
| `update_merge_request(project_id, mr_iid, updates)` | Update title, description, assignee, labels, state |
| `approve_merge_request(project_id, mr_iid)` | Approve an MR |
| `add_mr_note(project_id, mr_iid, body)` | Post a comment on an MR |

### Branches & Commits
| Function | Description |
|----------|-------------|
| `list_branches(project_id, search, per_page)` | List branches |
| `get_branch(project_id, branch)` | Get a branch by name |
| `list_commits(project_id, branch, per_page)` | List recent commits |

### Issues
| Function | Description |
|----------|-------------|
| `list_issues(project_id, state, per_page)` | List issues |
| `create_issue(project_id, title, description, labels)` | Create an issue |

### Pipelines
| Function | Description |
|----------|-------------|
| `list_pipelines(project_id, ref, status, per_page)` | List pipelines |
| `get_pipeline(project_id, pipeline_id)` | Get a single pipeline |
| `trigger_pipeline(project_id, ref, variables)` | Trigger a pipeline |

### Users
| Function | Description |
|----------|-------------|
| `get_current_user()` | Authenticated user's profile |
| `find_user(username)` | Look up a user by username |

## Usage examples

```python
import sys
sys.path.insert(0, r"C:\projects\aitools")

import importlib.util, os
spec = importlib.util.spec_from_file_location(
    "gitlab_call",
    r"C:\projects\aitools\skills\gitlab\gitlab-call\main.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ── Who am I? ──
me = mod.get_current_user()
print(me["body"]["username"])  # anthony.dourish

# ── List open MRs on SERIOPlusDataServices ──
mrs = mod.list_merge_requests(7255, state="opened")
for mr in mrs:
    print(mr["iid"], mr["title"], mr["source_branch"])

# ── Open a new MR ──
result = mod.create_merge_request(
    project_id=7255,
    source_branch="feature/SERIO-39310",
    target_branch="dev",
    title="feat(SERIO-39310): seizure memo PDF endpoint",
    description="Implements the POST /generate-seizure-memo endpoint.\n\nCloses SERIO-39310.",
    remove_source_branch=True,
)
print(result["body"]["web_url"])

# ── Comment on MR #2480 ──
mod.add_mr_note(7255, 2480, "✅ Reviewed and approved — logic matches the BDD spec.")

# ── List branches matching 'feature' ──
branches = mod.list_branches(7255, search="feature")
for b in branches:
    print(b["name"], b["commit"]["short_id"])

# ── List recent commits on dev ──
commits = mod.list_commits(7255, branch="dev", per_page=5)
for c in commits:
    print(c["short_id"], c["title"])

# ── Trigger a pipeline ──
mod.trigger_pipeline(7255, ref="feature/SERIO-39310")

# ── Raw API call ──
result = mod.run({"path": "/version"})
print(result["body"]["version"])  # 19.0.2-ee
```

## CLI usage

```powershell
cd C:\projects\aitools
python skills/gitlab/gitlab-call/main.py /user
python skills/gitlab/gitlab-call/main.py /projects/7255/merge_requests?state=opened
python skills/gitlab/gitlab-call/main.py /projects/7255/merge_requests --method POST --body '{"source_branch":"feature/SERIO-39310","target_branch":"dev","title":"My MR"}'
```

## run() interface

```python
mod.run({"path": "/user"})
mod.run({"path": "/projects/7255/merge_requests", "params": {"state": "opened"}})
mod.run({
    "path": "/projects/7255/merge_requests",
    "method": "POST",
    "body": {
        "source_branch": "feature/SERIO-39310",
        "target_branch": "dev",
        "title": "feat(SERIO-39310): seizure memo PDF"
    }
})
```

## Related

- `docs/runbooks/RUNBOOK-gitlab-call.md` — step-by-step setup and troubleshooting
- `shared/keepass_helper.py` — KeePass secret retrieval (used by other skills)
- `shared/http_client.py` — thin HTTP wrapper (used by this skill)
- `skills/jenkins/jenkins-call/` — Jenkins CI/CD API (same pattern)
- `skills/jira/jira-call/` — Jira REST API (same pattern)
