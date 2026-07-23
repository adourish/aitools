# Skill: jenkins-call

Make authenticated calls to the FDA Jenkins CI/CD server (jenkins.fda.gov).

## When to use

- Check whether a SERIO / SERIOPlus build passed or failed
- Retrieve console output from a recent build to diagnose a failure
- Trigger a build from a script or agent task
- List available jobs to find the right job name

## Prerequisites

- VPN full tunnel connected (jenkins.fda.gov is only reachable on VPN)
- KeePass entry: DevOps/FDA Jenkins API token (jenkins.fda.gov) in the automation vault
  (C:\keys\automation-keys.kdbx on the FDA laptop)
- keepassxc-cli on PATH (installed via Install-DevWorkstation.ps1 -Only keepassxc)
- requests Python package (pip install requests)

## How it works

The skill reads the Jenkins API token from KeePass non-interactively, then calls the Jenkins
JSON API (/api/json) or the console text endpoint. All calls use HTTP Basic auth
(FDA_JENKINS_USER env var + token). The FDA internal CA is trusted via the system cert store
(set up by RUNBOOK-internal-git-cert.md).

## Inputs

| Parameter  | Type   | Required | Description |
|------------|--------|----------|-------------|
| path       | str    | Yes      | API path, e.g. /api/json |
| method     | str    | No       | HTTP method: GET or POST (default GET) |
| body       | dict   | No       | Request body for POST |
| token      | str    | No       | Jenkins API token (auto-loaded from KeePass) |
| user       | str    | No       | Jenkins username (auto-loaded from KeePass) |
| base_url   | str    | No       | Override base URL (default https://jenkins.fda.gov) |
| verify_ssl | bool   | No       | Verify SSL cert (default False -- FDA internal CA) |

## Outputs

| Field       | Type        | Description |
|-------------|-------------|-------------|
| status_code | int         | HTTP status code |
| body        | dict or str | Parsed JSON or raw text |
| ok          | bool        | True if status_code < 400 |

## Credentials

KeePass entry: DevOps/FDA Jenkins API token (jenkins.fda.gov)

- Password  -> Jenkins API token
- UserName  -> Jenkins username (e.g. anthony.dourish)

Credential lookup order:
1. Explicit token / user in inputs dict
2. Env vars: FDA_JENKINS_TOKEN, FDA_JENKINS_USER
3. KeePass entry above

## Convenience wrappers

| Function                          | Description |
|-----------------------------------|-------------|
| list_jobs()                       | All top-level jobs with last build result |
| get_job(job_name)                 | Full info for a single job |
| get_last_build(job_name)          | Last build status |
| get_build(job_name, build_number) | Specific build status |
| get_console(job_name, build_number) | Console log (defaults to lastBuild) |
| trigger_build(job_name, params)   | Trigger a parameterized build |

## Usage

```python
import sys
sys.path.insert(0, r"C:\projects\fda-serio")

from fdaskills.jenkins.jenkins_call.main import list_jobs, get_last_build, get_console

# List all jobs
jobs = list_jobs()

# Check if the last SERIO build passed
build = get_last_build("SERIO-build")
print(build["result"])   # SUCCESS / FAILURE / ABORTED / None (still running)

# Get console output to diagnose a failure
log = get_console("SERIO-build", build["number"])
print(log[-3000:])       # last 3000 chars
```

## run() interface

```python
from fdaskills.jenkins.jenkins_call.main import run

run({"action": "list_jobs"})
run({"action": "get_last_build", "job": "SERIO-build"})
run({"action": "get_console",    "job": "SERIO-build", "number": 42})
run({"action": "trigger_build",  "job": "SERIO-build", "params": {"BRANCH": "main"}})
```

## Related

- work/JENKINS.md -- auto-updated each runner cycle with current job health
- docs/runbooks/RUNBOOK-internal-git-cert.md -- FDA CA trust setup
- fdaskills/shared/keepass_helper.py -- KeePass secret retrieval
