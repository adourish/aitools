# Skill: jira-call

Read and write Jira issues on the FDA Jira instance (sde.fda.gov/jira).

## When to use

- Look up the status, assignee, or description of a SERIO Jira ticket
- Search for all open issues assigned to you or in a given sprint
- Create a new issue to track a bug or task found during testing
- Transition an issue to a new status (e.g. In Progress -> Done)

## Prerequisites

- VPN full tunnel connected (sde.fda.gov is only reachable on VPN)
- Jira access granted -- request from Mehvish Ali (see SERIO-TEAM-CONTACTS.md)
- KeePass entry: DevOps/FDA Jira PAT (sde.fda.gov) in the automation vault
  (C:\keys\automation-keys.kdbx on the FDA laptop)
- keepassxc-cli on PATH (installed via Install-DevWorkstation.ps1 -Only keepassxc)
- requests Python package (pip install requests)

## How it works

The skill reads the Jira Personal Access Token (PAT) from KeePass non-interactively, then calls
the Jira REST API v2 (/rest/api/2/). Auth is Bearer token. The FDA internal CA is trusted via
the system cert store (set up by RUNBOOK-internal-git-cert.md).

## Inputs

| Parameter  | Type   | Required | Description |
|------------|--------|----------|-------------|
| method     | str    | No       | HTTP method: GET, POST, PUT, DELETE (default GET) |
| path       | str    | Yes      | API path, e.g. /rest/api/2/issue/SERIO-42 |
| body       | dict   | No       | Request body for POST/PUT |
| pat        | str    | No       | Bearer token (auto-loaded from KeePass) |
| base_url   | str    | No       | Override base URL (default https://sde.fda.gov/jira) |
| verify_ssl | bool   | No       | Verify SSL cert (default False -- FDA internal CA) |

## Outputs

| Field       | Type        | Description |
|-------------|-------------|-------------|
| status_code | int         | HTTP status code |
| body        | dict or str | Parsed JSON or raw text |
| ok          | bool        | True if status_code < 400 |

## Credentials

KeePass entry: DevOps/FDA Jira PAT (sde.fda.gov)

- Password -> Personal Access Token (used as Bearer token)

Credential lookup order:
1. Explicit pat in inputs dict
2. KeePass entry above

## Convenience wrappers

| Function                                              | Description |
|-------------------------------------------------------|-------------|
| get_issue(issue_key)                                  | Fetch a single issue by key |
| search(jql, max_results, fields)                      | Search with JQL |
| create_issue(project_key, summary, description, type) | Create a new issue |
| transition_issue(issue_key, transition_id)            | Move issue to new state |

## Usage

```python
import sys
sys.path.insert(0, r"C:\projects\fda-serio")

from fdaskills.jira.jira_call.main import get_issue, search, create_issue

# Look up a specific ticket
issue = get_issue("SERIO-123")
print(issue["fields"]["summary"])
print(issue["fields"]["status"]["name"])

# Find all open issues assigned to me
results = search("project = SERIO AND assignee = currentUser() AND resolution = Unresolved")
for r in results:
    print(r["key"], r["fields"]["summary"])

# Create a new bug
new = create_issue(
    project="SERIO",
    summary="Login page 508 contrast failure",
    description="The submit button fails WCAG AA contrast ratio.",
    issuetype="Bug"
)
print(new["key"])   # e.g. SERIO-456
```

## run() interface

```python
from fdaskills.jira.jira_call.main import run

run({"action": "get_issue",  "key": "SERIO-123"})
run({"action": "search",     "jql": "project = SERIO AND status = 'In Progress'"})
run({"action": "create_issue",
     "project": "SERIO", "summary": "Test issue", "description": "...", "issuetype": "Task"})
run({"action": "transition_issue", "key": "SERIO-123", "transition_id": "31"})
```

## Finding transition IDs

Transition IDs are Jira-instance-specific. To list available transitions for an issue:

```python
import sys, requests
sys.path.insert(0, r"C:\projects\fda-serio")
from fdaskills.shared.keepass_helper import get_secret
token = get_secret("DevOps/FDA Jira PAT (sde.fda.gov)")
r = requests.get("https://sde.fda.gov/jira/rest/api/2/issue/SERIO-123/transitions",
                 headers={"Authorization": f"Bearer {token}"}, verify=False)
print(r.json())
```

## Related

- work/JIRA.md -- auto-updated each runner cycle with your unresolved issues
- docs/runbooks/RUNBOOK-internal-git-cert.md -- FDA CA trust setup
- SERIO-TEAM-CONTACTS.md -- Mehvish Ali (Jira access requests)
- fdaskills/shared/keepass_helper.py -- KeePass secret retrieval
