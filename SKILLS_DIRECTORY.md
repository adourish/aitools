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

## serio-monolith
**Path**: `skills/serio-monolith/`
**Description**: Build and run the SERIO monolith — WebLogic 14.1.2.0 + `serio-ws.ear` backend + Angular frontend (`:4200`). Separate from SERIO+; uses **JDK 21** (not 17). WebLogic domain + datasources must be set up first. Orchestration script: `fda-serio/tools/serio/Start-SerioMonolith.ps1` (actions: `up`, `weblogic`, `deploy`, `frontend`).
**Ports**: WebLogic `:7001` | Angular `:4200`
**JDK**: **21** (opposite of SERIO+)
**Hosted dev**: `https://oii.dev.fda.gov/serio`
**Prerequisites**: WebLogic installed, `serio` domain configured, OASIS Oracle DB + VPN, OASIS user provisioned.
**See**: `skills/serio-monolith/SKILL.md` | `fda-serio/docs/runbooks/RUNBOOK-run-serio.md`

---

## serioplus-common-lib
**Path**: `skills/serioplus-common-lib/`
**Description**: Build and install `serioplus-common-library:13.0.0-SNAPSHOT` into the local Maven repository. Always step 1 before building any SERIO+ service. Critical gotcha: must be installed as `-SNAPSHOT` even though the pom defaults to `13.0.0` — quote the `-Drevision` arg in PowerShell: `mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install`. Build from the `serioplus-common-library/` subdirectory, not the repo root.
**JDK**: 17
**Artifact**: `gov.fda.oii.serioplus:serioplus-common-library:13.0.0-SNAPSHOT`
**See**: `skills/serioplus-common-lib/SKILL.md`

---

## serioplus-data-services
**Path**: `skills/serioplus-data-services/`
**Description**: Build and run the SERIOPlusDataServices tier — 8 Spring Boot data-layer microservices (Java 17) plus the local-gateway-service that fronts them. The only tier that talks to OASIS Oracle. Build with `mvn -DskipTests -nsu clean install` (after common-lib). Run with `--spring.profiles.active=local` for local dev (no AWS). Gateway :8070 is the entry point for the business layer.
**Ports**: gateway `:8070` | entry `:8090` | lookup `:8091` | user-org `:8092` | work `:8093` | application `:8094` | document `:8095` | screening `:8096` | filer-eval `:8097`
**JDK**: 17 | **Oracle**: required at runtime | **VPN**: required (Nexus + Oracle)
**Tool**: `tools/serioplus/SerioPlusStack.ps1 -Action build -Only data` / `-Action start -Only data`
**See**: `skills/serioplus-data-services/SKILL.md`

---

## serioplus-business-services
**Path**: `skills/serioplus-business-services/`
**Description**: Build and run the SERIOPlusServices tier — 7 Spring Boot business-layer microservices (Java 17). Sits between the Angular UI and the data layer. Calls the data gateway at `localhost:8070`. Start after the data tier is up.
**Ports**: general-admin `:8080` | user-option `:8081` | aiml `:8082` | workflow `:8083` | notice `:8084` | screening `:8085` | filer-eval `:8086`
**JDK**: 17 | **Requires**: data tier gateway `:8070` running
**Tool**: `tools/serioplus/SerioPlusStack.ps1 -Action build -Only services` / `-Action start -Only services`
**See**: `skills/serioplus-business-services/SKILL.md`

---

## serioplus-app
**Path**: `skills/serioplus-app/`
**Description**: Build (npm install) and run (ng serve) the SERIOPlusApp Angular 19 UI. Served at `:4201/serioplus/`. Requires FDA Nexus `.npmrc` (copy from `.npmrc.example`). Add `?acceptBanner=true` to any URL to skip the government banner click-through. Hosted dev: `https://oii-cloud.dev.fda.gov/serioplus/`.
**Port**: `:4201` | **URL**: `http://localhost:4201/serioplus/#/?acceptBanner=true`
**Tool**: `tools/serioplus/SerioPlusStack.ps1 -Action build -Only app` / `-Action start -Only app`
**See**: `skills/serioplus-app/SKILL.md`

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