# RUNBOOK: gitlab-call — FDA GitLab REST API

Use this skill to read and write FDA GitLab resources (merge requests, branches,
pipelines, issues, users) on the internal instance at `git.fda.gov`.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| VPN full-tunnel connected | `curl -sk https://git.fda.gov` returns HTML |
| GitLab token in Windows Credential Manager | `git credential fill` for `git.fda.gov` returns a `glpat-*` password |
| Python on PATH | `python --version` → 3.9+ |
| `aitools` repo cloned | `C:\projects\aitools` exists |

---

## Token setup (one-time)

Your `glpat-*` token was provisioned when you first authenticated to `git.fda.gov`.
It should already be in Windows Credential Manager if you have cloned or pushed any
FDA GitLab repo. To confirm:

```powershell
git credential fill
# type:
protocol=https
host=git.fda.gov
# (blank line, then Ctrl-D or Enter twice)
# Expected output:
# protocol=https
# host=git.fda.gov
# username=anthony.dourish
# password=glpat-...
```

If it's missing, generate a new Personal Access Token at:
`https://git.fda.gov/-/user_settings/personal_access_tokens`
Scopes needed: **api** (covers read_api, read_repository, write_repository, read_user).

Store it in Windows Credential Manager:

```powershell
git credential approve
# type:
protocol=https
host=git.fda.gov
username=anthony.dourish
password=glpat-YOURTOKEN
# (blank line)
```

Or set the environment variable for the session:

```powershell
$env:GITLAB_TOKEN = "glpat-YOURTOKEN"
```

---

## Token expiry

The current token expires **2026-08-14**. Check expiry with:

```python
import sys; sys.path.insert(0, r"C:\projects\aitools")
import importlib.util
spec = importlib.util.spec_from_file_location("gl", r"C:\projects\aitools\skills\gitlab\gitlab-call\main.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
r = mod.run({"path": "/personal_access_tokens/self"})
print(r["body"].get("expires_at"), r["body"].get("scopes"))
```

Rotate at: `https://git.fda.gov/-/user_settings/personal_access_tokens`

---

## Quick-start: verify connectivity

```powershell
cd C:\projects\aitools
python skills/gitlab/gitlab-call/main.py /user
```

Expected output (trimmed):
```json
{
  "status_code": 200,
  "body": {
    "username": "anthony.dourish",
    "name": "Anthony.Dourish",
    "state": "active"
  },
  "ok": true
}
```

---

## Common operations

### List your accessible projects

```powershell
python skills/gitlab/gitlab-call/main.py "/projects?membership=true&per_page=20"
```

### List open MRs on a project

```python
import sys; sys.path.insert(0, r"C:\projects\aitools")
import importlib.util
spec = importlib.util.spec_from_file_location("gl", r"C:\projects\aitools\skills\gitlab\gitlab-call\main.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

mrs = mod.list_merge_requests(7255, state="opened")   # SERIOPlusDataServices
for mr in mrs:
    print(mr["iid"], mr["source_branch"], mr["title"])
```

### Open a merge request

```python
result = mod.create_merge_request(
    project_id=7255,
    source_branch="feature/SERIO-39310",
    target_branch="dev",
    title="feat(SERIO-39310): seizure memo PDF endpoint",
    description="Implements POST /generate-seizure-memo.\n\nCloses SERIO-39310.",
)
print(result["body"]["web_url"])   # opens the MR URL in browser if you want
```

### Post a comment on an MR

```python
mod.add_mr_note(7255, 2480, "✅ BDD scenarios pass — ready for review.")
```

### List branches

```python
branches = mod.list_branches(7255, search="feature")
for b in branches:
    print(b["name"])
```

### Trigger a pipeline

```python
mod.trigger_pipeline(7255, ref="feature/SERIO-39310")
```

### Find a project ID by path

```python
pid = mod.find_project_id("FDA/ORA/SI/SERIOPlusServices")
print(pid)   # 7253
```

---

## Known project IDs

| Repo | ID |
|------|----|
| aitools | 9639 |
| ai-sdlc-playbook | 8410 |
| SERIOPlusApp | 7256 |
| SERIOPlusCommonLibraries | 7254 |
| SERIOPlusDataServices | 7255 |
| SERIOPlusServices | 7253 |
| serioplusintegrationservices | 7271 |
| serioplusaiml | 7680 |
| Shared-AI-Service | 7882 |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `401 Unauthorized` | Token missing or expired | Re-run `git credential fill` to confirm; rotate token at the GitLab settings URL above |
| `403 Forbidden` | Token lacks required scope | Regenerate with `api` scope |
| `curl: (6) Could not resolve host` | Not on VPN | Connect full-tunnel VPN |
| SSL error | FDA CA not trusted by Python's urllib | Confirm `verify_ssl=False` (default) |
| `RuntimeError: No GitLab token found` | Credential Manager empty | Set `$env:GITLAB_TOKEN` or run `git credential approve` |

---

## API reference

GitLab 19.0.2-EE (Enterprise Edition) — full API docs available on-instance:
`https://git.fda.gov/help/api/api_resources.md`

Common endpoint patterns:

```
GET  /projects/{id}
GET  /projects/{id}/merge_requests?state=opened
POST /projects/{id}/merge_requests
PUT  /projects/{id}/merge_requests/{iid}
POST /projects/{id}/merge_requests/{iid}/approve
POST /projects/{id}/merge_requests/{iid}/notes
GET  /projects/{id}/repository/branches
GET  /projects/{id}/repository/commits?ref_name={branch}
GET  /projects/{id}/pipelines
POST /projects/{id}/pipeline
GET  /user
GET  /personal_access_tokens/self
```

---

## Related

- `skills/gitlab/gitlab-call/SKILL.md` — full skill reference with all wrappers
- `skills/gitlab/gitlab-call/main.py` — implementation
- `skills/jenkins/jenkins-call/` — Jenkins CI/CD (same pattern, different auth)
- `skills/jira/jira-call/` — FDA Jira REST API
