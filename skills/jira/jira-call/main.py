"""
Skill: jira-call
Make authenticated calls to the FDA Jira REST API (sde.fda.gov/jira).

Inputs:
    method      (str)  HTTP method: GET | POST | PUT | DELETE (default GET)
    path        (str)  API path, e.g. "/rest/api/2/myself" or "/rest/api/2/issue/SERIO-42"
    body        (dict) Request body for POST/PUT (optional)
    pat         (str)  Bearer token -- if omitted, loaded from KeePass automatically
    base_url    (str)  Override base URL (default https://sde.fda.gov/jira)
    verify_ssl  (bool) Whether to verify SSL cert (default False -- FDA internal CA)

Outputs:
    status_code (int)
    body        (dict | str)  Parsed JSON or raw text
    ok          (bool)  True if status_code < 400

KeePass entry: DevOps/FDA Jira PAT (sde.fda.gov)
"""

import sys
import os

# Allow importing shared utilities from the aitools root
_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILLS_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_AITOOLS_ROOT = os.path.abspath(os.path.join(_SKILLS_ROOT, "..", ".."))
if _AITOOLS_ROOT not in sys.path:
    sys.path.insert(0, _AITOOLS_ROOT)

from shared.keepass_helper import get_secret
from shared.http_client import make_request
from shared.logger import logger

JIRA_BASE_URL = "https://sde.fda.gov/jira"
JIRA_KEEPASS_ENTRY = "DevOps/FDA Jira PAT (sde.fda.gov)"


def run(inputs: dict) -> dict:
    method = inputs.get("method", "GET").upper()
    path = inputs["path"]
    body = inputs.get("body")
    base_url = inputs.get("base_url", JIRA_BASE_URL).rstrip("/")
    verify_ssl = inputs.get("verify_ssl", False)

    # Resolve PAT -- caller can pass it directly or we pull from KeePass
    pat = inputs.get("pat") or get_secret(JIRA_KEEPASS_ENTRY)

    url = f"{base_url}{path}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    logger.info("jira-call %s %s", method, url)
    status_code, response_body = make_request(
        method=method,
        url=url,
        headers=headers,
        body=body,
        verify_ssl=verify_ssl,
    )
    ok = status_code < 400
    if not ok:
        logger.warning("jira-call got %s: %s", status_code, str(response_body)[:200])
    else:
        logger.info("jira-call %s OK", status_code)

    return {
        "status_code": status_code,
        "body": response_body,
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Convenience wrappers (importable by other skills)
# ---------------------------------------------------------------------------

def get_issue(issue_key: str, **kwargs) -> dict:
    """Fetch a single Jira issue by key, e.g. 'SERIO-42'."""
    return run({"path": f"/rest/api/2/issue/{issue_key}", **kwargs})


def search(jql: str, max_results: int = 50, fields: list = None, **kwargs) -> dict:
    """Search Jira with a JQL string."""
    body = {"jql": jql, "maxResults": max_results}
    if fields:
        body["fields"] = fields
    return run({"method": "POST", "path": "/rest/api/2/search", "body": body, **kwargs})


def create_issue(project_key: str, summary: str, issue_type: str = "Task",
                 description: str = "", extra_fields: dict = None, **kwargs) -> dict:
    """Create a Jira issue. Returns the full API response."""
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    if description:
        fields["description"] = description
    if extra_fields:
        fields.update(extra_fields)
    return run({"method": "POST", "path": "/rest/api/2/issue",
                "body": {"fields": fields}, **kwargs})


def transition_issue(issue_key: str, transition_name: str, **kwargs) -> dict:
    """Transition an issue to a new workflow state by name."""
    # First fetch available transitions
    t_resp = run({"path": f"/rest/api/2/issue/{issue_key}/transitions", **kwargs})
    if not t_resp["ok"]:
        return t_resp
    transitions = t_resp["body"].get("transitions", [])
    match = next(
        (t for t in transitions if t["name"].lower() == transition_name.lower()), None
    )
    if not match:
        available = [t["name"] for t in transitions]
        return {
            "status_code": 400,
            "body": f"Transition '{transition_name}' not found. Available: {available}",
            "ok": False,
        }
    transition_id = match["id"]
    return run({
        "method": "POST",
        "path": f"/rest/api/2/issue/{issue_key}/transitions",
        "body": {"transition": {"id": transition_id}},
        **kwargs,
    })