"""
Skill: gitlab-call
Make authenticated calls to the FDA GitLab instance (git.fda.gov).

Credentials are loaded automatically from the Windows Git Credential Manager
(where the glpat-* token is stored by git when you authenticate).
Override with the GITLAB_TOKEN env var or by passing token= in inputs.

Inputs:
    path        (str)  API path, e.g. "/projects/7255/merge_requests"
    method      (str)  HTTP method: GET | POST | PUT | DELETE (default GET)
    body        (dict) Request body for POST/PUT (optional)
    token       (str)  Override PRIVATE-TOKEN (auto-loaded if omitted)
    base_url    (str)  Override base URL (default https://git.fda.gov/api/v4)
    verify_ssl  (bool) Verify SSL cert (default False -- FDA internal CA)
    params      (dict) Query-string parameters (merged into URL)

Outputs:
    status_code (int)
    body        (dict | list | str)  Parsed JSON or raw text
    ok          (bool)  True if status_code < 400

KeePass / credential discovery order:
    1. token= in inputs dict
    2. GITLAB_TOKEN environment variable
    3. Windows Git Credential Manager for host git.fda.gov
"""

import os
import subprocess
import sys
import json as _json

_HERE = os.path.dirname(os.path.abspath(__file__))
# skills/gitlab/gitlab-call/ -> skills/gitlab/ -> skills/ -> aitools/
_AITOOLS_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
if _AITOOLS_ROOT not in sys.path:
    sys.path.insert(0, _AITOOLS_ROOT)

from shared.http_client import make_request
from shared.logger import logger

GITLAB_BASE_URL = "https://git.fda.gov/api/v4"
GITLAB_HOST = "git.fda.gov"


# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------

def _get_token_from_git_credential() -> str:
    """Ask the Windows Git Credential Manager for the stored glpat-* token."""
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=git.fda.gov\n\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as exc:
        logger.debug("git credential fill failed: %s", exc)
    return ""


def _get_token(override=None) -> str:
    token = (
        override
        or os.environ.get("GITLAB_TOKEN", "")
        or _get_token_from_git_credential()
    )
    if not token:
        raise RuntimeError(
            "No GitLab token found. Set GITLAB_TOKEN env var or ensure "
            "the token is stored in Windows Credential Manager for git.fda.gov."
        )
    return token


# ---------------------------------------------------------------------------
# Core run()
# ---------------------------------------------------------------------------

def run(inputs: dict) -> dict:
    """Generic GitLab API call."""
    path = inputs["path"].lstrip("/")
    method = inputs.get("method", "GET").upper()
    body = inputs.get("body")
    base_url = inputs.get("base_url", GITLAB_BASE_URL).rstrip("/")
    verify_ssl = inputs.get("verify_ssl", False)
    params = inputs.get("params", {})

    token = _get_token(inputs.get("token"))
    headers = {
        "PRIVATE-TOKEN": token,
        "Content-Type": "application/json",
    }

    url = f"{base_url}/{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"

    logger.info("gitlab-call %s %s", method, url)
    status_code, response_body = make_request(
        method=method,
        url=url,
        headers=headers,
        body=body,
        verify_ssl=verify_ssl,
    )
    ok = status_code < 400
    if not ok:
        logger.warning("gitlab-call got %s: %s", status_code, str(response_body)[:300])
    else:
        logger.info("gitlab-call %s OK", status_code)

    return {"status_code": status_code, "body": response_body, "ok": ok}


# ---------------------------------------------------------------------------
# Convenience wrappers — Projects
# ---------------------------------------------------------------------------

def get_project(project_id, **kwargs) -> dict:
    """Get project metadata by numeric ID or URL-encoded path."""
    return run({"path": f"/projects/{project_id}", **kwargs})


def list_projects(search=None, membership=True, per_page=20, **kwargs) -> list:
    """List projects. Pass search= to filter by name."""
    params = {"per_page": per_page, "membership": str(membership).lower()}
    if search:
        params["search"] = search
    result = run({"path": "/projects", "params": params, **kwargs})
    return result["body"] if result["ok"] else []


def find_project_id(namespace_path: str, **kwargs) -> int | None:
    """
    Look up a project's numeric ID by its full path, e.g.
    'FDA/ORA/SI/SERIOPlusDataServices'.
    Returns None if not found.
    """
    encoded = namespace_path.replace("/", "%2F")
    result = run({"path": f"/projects/{encoded}", **kwargs})
    if result["ok"] and isinstance(result["body"], dict):
        return result["body"].get("id")
    return None


# ---------------------------------------------------------------------------
# Convenience wrappers — Merge Requests
# ---------------------------------------------------------------------------

def list_merge_requests(project_id, state="opened", per_page=20, **kwargs) -> list:
    """List merge requests for a project."""
    result = run({
        "path": f"/projects/{project_id}/merge_requests",
        "params": {"state": state, "per_page": per_page},
        **kwargs,
    })
    return result["body"] if result["ok"] else []


def get_merge_request(project_id, mr_iid: int, **kwargs) -> dict:
    """Get a single merge request by its IID (project-local ID)."""
    return run({"path": f"/projects/{project_id}/merge_requests/{mr_iid}", **kwargs})


def create_merge_request(
    project_id,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str = "",
    assignee_id: int = None,
    labels: list = None,
    remove_source_branch: bool = True,
    **kwargs,
) -> dict:
    """Open a new merge request."""
    body = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "description": description,
        "remove_source_branch": remove_source_branch,
    }
    if assignee_id:
        body["assignee_id"] = assignee_id
    if labels:
        body["labels"] = ",".join(labels)
    return run({"path": f"/projects/{project_id}/merge_requests", "method": "POST", "body": body, **kwargs})


def update_merge_request(project_id, mr_iid: int, updates: dict, **kwargs) -> dict:
    """Update an MR (title, description, assignee_id, state_event, labels, etc.)."""
    return run({
        "path": f"/projects/{project_id}/merge_requests/{mr_iid}",
        "method": "PUT",
        "body": updates,
        **kwargs,
    })


def approve_merge_request(project_id, mr_iid: int, **kwargs) -> dict:
    """Approve an MR (requires at least Developer role)."""
    return run({
        "path": f"/projects/{project_id}/merge_requests/{mr_iid}/approve",
        "method": "POST",
        **kwargs,
    })


def add_mr_note(project_id, mr_iid: int, body: str, **kwargs) -> dict:
    """Post a comment on an MR."""
    return run({
        "path": f"/projects/{project_id}/merge_requests/{mr_iid}/notes",
        "method": "POST",
        "body": {"body": body},
        **kwargs,
    })


# ---------------------------------------------------------------------------
# Convenience wrappers — Branches & Commits
# ---------------------------------------------------------------------------

def list_branches(project_id, search=None, per_page=20, **kwargs) -> list:
    """List branches for a project."""
    params = {"per_page": per_page}
    if search:
        params["search"] = search
    result = run({"path": f"/projects/{project_id}/repository/branches", "params": params, **kwargs})
    return result["body"] if result["ok"] else []


def get_branch(project_id, branch: str, **kwargs) -> dict:
    """Get a branch by name."""
    return run({"path": f"/projects/{project_id}/repository/branches/{branch}", **kwargs})


def list_commits(project_id, branch="main", per_page=10, **kwargs) -> list:
    """List recent commits on a branch."""
    result = run({
        "path": f"/projects/{project_id}/repository/commits",
        "params": {"ref_name": branch, "per_page": per_page},
        **kwargs,
    })
    return result["body"] if result["ok"] else []


# ---------------------------------------------------------------------------
# Convenience wrappers — Issues
# ---------------------------------------------------------------------------

def list_issues(project_id, state="opened", per_page=20, **kwargs) -> list:
    """List issues for a project."""
    result = run({
        "path": f"/projects/{project_id}/issues",
        "params": {"state": state, "per_page": per_page},
        **kwargs,
    })
    return result["body"] if result["ok"] else []


def create_issue(project_id, title: str, description: str = "", labels: list = None, **kwargs) -> dict:
    """Create a new issue."""
    body = {"title": title, "description": description}
    if labels:
        body["labels"] = ",".join(labels)
    return run({"path": f"/projects/{project_id}/issues", "method": "POST", "body": body, **kwargs})


# ---------------------------------------------------------------------------
# Convenience wrappers — Pipelines
# ---------------------------------------------------------------------------

def list_pipelines(project_id, ref=None, status=None, per_page=10, **kwargs) -> list:
    """List pipelines. Filter by ref (branch) and/or status."""
    params = {"per_page": per_page}
    if ref:
        params["ref"] = ref
    if status:
        params["status"] = status
    result = run({"path": f"/projects/{project_id}/pipelines", "params": params, **kwargs})
    return result["body"] if result["ok"] else []


def get_pipeline(project_id, pipeline_id: int, **kwargs) -> dict:
    """Get a single pipeline."""
    return run({"path": f"/projects/{project_id}/pipelines/{pipeline_id}", **kwargs})


def trigger_pipeline(project_id, ref: str = "main", variables: dict = None, **kwargs) -> dict:
    """Trigger a pipeline on a branch."""
    body = {"ref": ref}
    if variables:
        body["variables"] = [{"key": k, "value": v} for k, v in variables.items()]
    return run({
        "path": f"/projects/{project_id}/pipeline",
        "method": "POST",
        "body": body,
        **kwargs,
    })


# ---------------------------------------------------------------------------
# Convenience wrappers — Users
# ---------------------------------------------------------------------------

def get_current_user(**kwargs) -> dict:
    """Return the authenticated user's profile."""
    return run({"path": "/user", **kwargs})


def find_user(username: str, **kwargs) -> dict | None:
    """Look up a user by username. Returns the first match or None."""
    result = run({"path": "/users", "params": {"username": username}, **kwargs})
    if result["ok"] and isinstance(result["body"], list) and result["body"]:
        return result["body"][0]
    return None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FDA GitLab REST API caller")
    parser.add_argument("path", help="API path, e.g. /user")
    parser.add_argument("--method", default="GET", help="HTTP method (default GET)")
    parser.add_argument("--body", default=None, help="JSON body string for POST/PUT")
    parser.add_argument("--base-url", default=GITLAB_BASE_URL)
    args = parser.parse_args()

    body = _json.loads(args.body) if args.body else None
    result = run({
        "path": args.path,
        "method": args.method,
        "body": body,
        "base_url": args.base_url,
    })
    print(_json.dumps(result, indent=2, default=str))
