"""
Skill: jenkins-call
Make authenticated calls to the FDA Jenkins CI/CD server (jenkins.fda.gov).

Inputs:
    path        (str)  API path, e.g. "/api/json" or "/job/SERIO-plus-build/lastBuild/api/json"
    method      (str)  HTTP method: GET | POST (default GET)
    body        (dict) Request body for POST (optional)
    token       (str)  Jenkins API token -- if omitted, loaded from KeePass automatically
    user        (str)  Jenkins username -- if omitted, loaded from KeePass automatically
    base_url    (str)  Override base URL (default https://jenkins.fda.gov)
    verify_ssl  (bool) Whether to verify SSL cert (default False -- FDA internal CA)

Outputs:
    status_code (int)
    body        (dict | str)  Parsed JSON or raw text
    ok          (bool)  True if status_code < 400

KeePass entry: DevOps/FDA Jenkins API token (jenkins.fda.gov)
  Password field = API token
  UserName field = FDA Jenkins username (anthony.dourish)
"""

import sys
import os
import base64

# Allow importing shared utilities from the aitools root
_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILLS_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_AITOOLS_ROOT = os.path.abspath(os.path.join(_SKILLS_ROOT, "..", ".."))
if _AITOOLS_ROOT not in sys.path:
    sys.path.insert(0, _AITOOLS_ROOT)

from shared.keepass_helper import get_secret
from shared.http_client import make_request
from shared.logger import logger

JENKINS_BASE_URL = "https://jenkins.fda.gov"
JENKINS_KEEPASS_ENTRY = "DevOps/FDA Jenkins API token (jenkins.fda.gov)"


def _get_token(override=None):
    return override or os.environ.get("FDA_JENKINS_TOKEN") or get_secret(JENKINS_KEEPASS_ENTRY, field="Password")


def _get_user(override=None):
    return override or os.environ.get("FDA_JENKINS_USER") or get_secret(JENKINS_KEEPASS_ENTRY, field="UserName")


def _basic_auth_header(user: str, token: str) -> str:
    raw = f"{user}:{token}".encode("ascii")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def run(inputs: dict) -> dict:
    path       = inputs["path"]
    method     = inputs.get("method", "GET").upper()
    body       = inputs.get("body")
    base_url   = inputs.get("base_url", JENKINS_BASE_URL).rstrip("/")
    verify_ssl = inputs.get("verify_ssl", False)

    token = _get_token(inputs.get("token"))
    user  = _get_user(inputs.get("user"))

    headers = {"Content-Type": "application/json"}
    if token and user:
        headers["Authorization"] = _basic_auth_header(user, token)

    url = base_url + "/" + path.lstrip("/")
    logger.info("jenkins-call %s %s", method, url)
    status_code, response_body = make_request(
        method=method,
        url=url,
        headers=headers,
        body=body,
        verify_ssl=verify_ssl,
    )
    ok = status_code < 400
    if not ok:
        logger.warning("jenkins-call got %s: %s", status_code, str(response_body)[:200])
    else:
        logger.info("jenkins-call %s OK", status_code)

    return {"status_code": status_code, "body": response_body, "ok": ok}


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def list_jobs(**kwargs) -> dict:
    """List all top-level jobs with name, color, and last build result."""
    return run({
        "path": "/api/json?tree=jobs[name,color,lastBuild[result,building,timestamp,number]]",
        **kwargs
    })


def get_job(job_name: str, **kwargs) -> dict:
    """Get full info for a single job."""
    return run({"path": f"/job/{job_name}/api/json", **kwargs})


def get_last_build(job_name: str, **kwargs) -> dict:
    """Get the last build's status for a job."""
    return run({"path": f"/job/{job_name}/lastBuild/api/json", **kwargs})


def get_build(job_name: str, build_number: int, **kwargs) -> dict:
    """Get a specific build's status."""
    return run({"path": f"/job/{job_name}/{build_number}/api/json", **kwargs})


def get_console(job_name: str, build_number=None, **kwargs) -> dict:
    """Get console output for a build (defaults to lastBuild)."""
    build = build_number if build_number is not None else "lastBuild"
    return run({"path": f"/job/{job_name}/{build}/consoleText", **kwargs})


def trigger_build(job_name: str, parameters: dict = None, **kwargs) -> dict:
    """
    Trigger a build. Pass parameters={key: val} for a parameterised job.
    Returns HTTP 201 on success (body will be empty string).
    """
    if parameters:
        qs = "&".join(f"{k}={v}" for k, v in parameters.items())
        path = f"/job/{job_name}/buildWithParameters?{qs}"
    else:
        path = f"/job/{job_name}/build"
    return run({"method": "POST", "path": path, **kwargs})