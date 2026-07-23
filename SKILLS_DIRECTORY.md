# AI Tools Skills Directory

## Overview
Full documentation for each skill including inputs, outputs, and usage examples.

---

## jira-call
**Path**: `skills/jira/jira-call/`
**Description**: Make authenticated calls to the FDA Jira REST API (`https://sde.fda.gov/jira`).
Auto-loads the Bearer PAT from KeePass (`DevOps/FDA Jira PAT (sde.fda.gov)`).
Includes convenience wrappers: `get_issue`, `search`, `create_issue`, `transition_issue`.
**Inputs**: `path` (required), `method` (default GET), `body` (dict), `pat` (override), `base_url` (override), `verify_ssl` (default False)
**Outputs**: `status_code`, `body`, `ok`
**Projects**: SERIO, SHIELD, PREDICT (and others on the FDA Jira instance)
**Import**: Use `importlib.util.spec_from_file_location` (directory name has a hyphen).
**See**: `skills/jira/jira-call/skill.md` for full docs and examples.

---

## jenkins-call
**Path**: `skills/jenkins/jenkins-call/`
**Description**: Make authenticated calls to the FDA Jenkins CI/CD server (`https://jenkins.fda.gov`).
Auto-loads the API token and username from KeePass (`DevOps/FDA Jenkins API token (jenkins.fda.gov)`).
Includes convenience wrappers: `list_jobs`, `get_job`, `get_last_build`, `get_build`, `get_console`, `trigger_build`.
**Inputs**: `path` (required), `method` (default GET), `body` (dict), `token` (override), `user` (override), `base_url` (override), `verify_ssl` (default False)
**Outputs**: `status_code`, `body`, `ok`
**KeePass entry**: `DevOps/FDA Jenkins API token (jenkins.fda.gov)` — Password = API token, UserName = `anthony.dourish`
**Env vars**: `FDA_JENKINS_TOKEN` (token), `FDA_JENKINS_USER` (username)
**Access**: FDA GFE laptop only; full-tunnel VPN required.
**Import**: Use `importlib.util.spec_from_file_location` (directory name has a hyphen).
**See**: `skills/jenkins/jenkins-call/skill.md` for full docs and examples.

---

## keepass-lookup
**Path**: `skills/keepass-lookup/`
**Description**: Look up any secret from the FDA automation KeePass vault (`automation-keys.kdbx`). Use whenever you need a credential — Jira PAT, Jenkins token, Oracle DB password, ELSA keys, etc. Wraps `keepassxc-cli` with key-file auth (no password prompt). Auto-discovers the vault on both the FDA GFE laptop (`C:\keys\`) and REI laptop (`G:\My Drive\Areas\Keys\`).
**Runtime**: Python (`shared/keepass_helper.py`) or PowerShell (`tools/keepass/Get-KeePassAttr.ps1`)
**Requires**: KeePassXC installed; `keepassxc-cli` on PATH; vault + key file present.
**Known entries**:
- `DevOps/FDA Jira PAT (sde.fda.gov)` — Password = PAT
- `DevOps/FDA Jenkins API token (jenkins.fda.gov)` — Password = token, UserName = username
- `Database/SERIO Oracle DB (oasis_er) Dev-Test` — Password = DB password
- `API/SEMOSS-Elsa-Dev` — Password = ELSA secret, UserName = ELSA access key
**Env overrides**: `KEEPASS_DB`, `KEEPASS_KEY` (Python) / `KEEPASS_DB`, `KEEPASS_KEYFILE` (PowerShell)
**See**: `skills/keepass-lookup/SKILL.md` for full docs, CLI usage, and troubleshooting.

---

## gitlab-call
**Path**: `skills/gitlab/gitlab-call/`
**Description**: Make authenticated calls to the FDA GitLab instance (`https://git.fda.gov/api/v4`).
Auto-loads the `glpat-*` Personal Access Token from Windows Credential Manager (stored when you `git push` to git.fda.gov). Falls back to `GITLAB_TOKEN` env var.
Includes convenience wrappers: `list_projects`, `find_project_id`, `list_merge_requests`, `get_merge_request`, `create_merge_request`, `update_merge_request`, `approve_merge_request`, `add_mr_note`, `list_branches`, `get_branch`, `list_commits`, `list_issues`, `create_issue`, `list_pipelines`, `trigger_pipeline`, `get_current_user`, `find_user`.
**Inputs**: `path` (required), `method` (default GET), `body` (dict), `token` (override), `base_url` (override), `verify_ssl` (default False), `params` (dict)
**Outputs**: `status_code`, `body`, `ok`
**GitLab version**: 19.0.2-EE — `https://git.fda.gov`
**Token scopes**: `api`, `read_api`, `read_repository`, `write_repository`, `read_user` (expires 2026-08-14)
**Env var**: `GITLAB_TOKEN` (override)
**Access**: FDA GFE laptop only; full-tunnel VPN required.
**Import**: Use `importlib.util.spec_from_file_location` (directory path contains a hyphen).
**See**: `skills/gitlab/gitlab-call/SKILL.md` for full docs and `docs/runbooks/RUNBOOK-gitlab-call.md` for setup.