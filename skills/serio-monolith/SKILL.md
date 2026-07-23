---
name: serio-monolith
description: Build and run the SERIO monolith (WebLogic 14.1.2.0 + Spring EAR backend + Angular UI :4200). Use when working on the on-prem SERIO app (as opposed to the SERIO+ microservice rewrite). Covers WebLogic startup, EAR deployment via Maven developer profile, ng serve, JDK 21, and the OASIS Oracle DB requirement.
metadata:
  version: "1.0.0"
  runtime: powershell
  repo: SERIO
  ports: "WebLogic :7001 | Angular UI :4200"
  url_local: "http://localhost:4200"
  url_dev: "https://oii.dev.fda.gov/serio"
---

# Skill: serio-monolith

Build and run the **SERIO monolith** — the on-prem Java EE / Angular app that SERIO+ is replacing.

## What this is

SERIO is two deployables + a database:

| Piece | What it is | Local URL |
|-------|-----------|-----------|
| **Backend** | `serio-ws.ear` — Spring web services deployed to WebLogic 14.1.2.0 | `http://localhost:7001/serio/ws` |
| **Frontend** | `serio-app-war` — Angular app (`ng serve` or deployed as WAR) | `http://localhost:4200` |
| **Database** | Oracle OASIS (`ORAD1T23`) — 3 JNDI datasources in WebLogic | Reached via `SerioDS`, `SerioDS_RPT`, `SerioDS_AWS` |

> **Verified end-to-end 2026-07-16.** Full local stack ran: WebLogic + domain + datasources →
> serio-ws.ear deployed → ng serve → `/serio/ws/api` querying OASIS dev DB.

## Hosted environments

| Environment | URL |
|-------------|-----|
| **Dev** | `https://oii.dev.fda.gov/serio` |
| **Test** | `https://oii.test.fda.gov/serio` |
| **Pre-prod** | `https://oii.preprod.fda.gov/serio` |

> Dev is unstable during work hours. Use Test for reliable testing.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| FDA laptop | Cannot run off-network |
| **Full-tunnel VPN up** | Nexus (to build) + Oracle `gi-22040-22041.fda.gov:1523` (to run) |
| **JDK 21** | SERIO 13.0.0 requires Java 21 (unlike SERIO+ which needs 17) |
| Maven on PATH | `mvn -version` |
| **WebLogic 14.1.2.0** installed | `C:\FDA\AppServer\Oracle_Home_14120` |
| `serio` domain created | Installed by `Install-SerioWebLogic.ps1` + `New-SerioDomain.ps1` |
| `SerioDS` datasources configured | 3 datasources in the domain (FS-012) |
| Node / npm / ng | For Angular frontend |
| OASIS user provisioned | Without it: `401 "An OASIS user profile was not found."` |

## Run (full stack) — Start-SerioMonolith.ps1

The orchestration script lives in `fda-serio/tools/serio/`:

```powershell
# Full stack: WebLogic → EAR deploy → Angular
C:\projects\fda-serio\tools\serio\Start-SerioMonolith.ps1

# Just WebLogic
C:\projects\fda-serio\tools\serio\Start-SerioMonolith.ps1 -Action weblogic

# Just re-deploy the EAR (WebLogic must already be up)
C:\projects\fda-serio\tools\serio\Start-SerioMonolith.ps1 -Action deploy

# Just the Angular frontend
C:\projects\fda-serio\tools\serio\Start-SerioMonolith.ps1 -Action frontend
```

## Manual steps

### 1. Set JDK 21

```powershell
# Auto-discovery (script does this; manual override:)
$jdk = Get-ChildItem 'C:\Program Files\Eclipse Adoptium' -Directory |
       Where-Object { $_.Name -match 'jdk-?21' -and (Test-Path "$($_.FullName)\bin\java.exe") } |
       Select-Object -First 1
$env:JAVA_HOME = $jdk.FullName
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
java -version   # must say 21.x
```

### 2. Start WebLogic

```powershell
Start-Process -FilePath 'C:\FDA\AppServer\Oracle_Home_14120\user_projects\domains\serio\bin\startWebLogic.cmd' `
  -WindowStyle Normal   # leave window open so you see WebLogic logs

# Wait for :7001
while (-not (Test-NetConnection localhost -Port 7001 -InformationLevel Quiet -EA 0)) {
    Write-Host "waiting for WebLogic..." ; Start-Sleep 5
}
Write-Host "WebLogic up"
```

### 3. Build + deploy the EAR

```powershell
cd C:\projects\SERIO
mvn -DskipTests -Pdeveloper clean package   # builds serio-ws.ear; developer profile auto-deploys to WebLogic autodeploy
```

> The `developer` Maven profile in `serio-ws-ear/pom.xml` copies the EAR to WebLogic's autodeploy
> folder. WebLogic picks it up automatically if it's running.

> ⚠️ **FS-011 antrun fix.** If the build fails with `javax.xml.ws.…` or antrun tasks, apply the
> patch: `C:\projects\fda-serio\handoff\serio-39310\Fix-SerioWsEar.ps1` (or pass `-FixAntrun` to the script).

### 4. Start the Angular frontend

```powershell
cd C:\projects\SERIO\serio-app-war
npm install   # first time or after dependency changes
npm start     # ng serve → http://localhost:4200
```

## Stop

```powershell
# Stop ng serve: Ctrl+C in its terminal window (or Stop-Process -Name node)
# Stop WebLogic: close the WebLogic terminal window, or:
Stop-Process -Name 'java' -Force   # ⚠️ kills ALL java — be selective if SERIO+ is also running
```

## Verify it's running

```powershell
# Backend
Invoke-RestMethod 'http://localhost:7001/serio/ws/api/health' -EA 0
# or just check the port
Test-NetConnection localhost -Port 7001 -InformationLevel Quiet

# Frontend
Test-NetConnection localhost -Port 4200 -InformationLevel Quiet
Start-Process 'http://localhost:4200'
```

## OASIS user provisioning

Same as SERIO+ — the app matches you by email in `FDA_PERSONNEL`. Without a row there, you get
`401 "An OASIS user profile was not found."` everywhere. Request from Kaustav Lahiri → Soumen Kundu.

Verify:
```sql
SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
FROM FDA_PERSONNEL p
LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
WHERE LOWER(p.EMAIL_ADRS) LIKE 'anthony.dourish%';
```

## Key differences from SERIO+

| | SERIO (monolith) | SERIO+ (microservices) |
|--|------------------|-----------------------|
| **JDK** | **21** | **17** |
| **Server** | WebLogic 14.1.2.0 :7001 | Spring Boot jars :8070-8097 |
| **UI port** | :4200 | :4201 |
| **Deploy** | EAR via Maven `developer` profile | `java -jar` |
| **Config** | `serio-app-war/build.properties` | `application.properties` + profiles |
| **DB** | `ORAD1T23` via JNDI datasources | `ORAD1T23` via Hikari |

## Gotchas

| # | Gotcha | Fix |
|---|--------|-----|
| 1 | **WebLogic must be running before EAR deploy** | Wait for :7001; script does this |
| 2 | **antrun `<tasks>` vs `<target>` bug** (FS-011) | Apply `Fix-SerioWsEar.ps1` patch |
| 3 | **JDK 21 required** (opposite of SERIO+) | Ensure `JAVA_HOME` is JDK 21 |
| 4 | **Oracle datasources must be configured** | FS-012; `SerioDS` JNDI in the domain |
| 5 | **OASIS user must be provisioned** | Request from Kaustav / Soumen |

## Related

- `fda-serio/tools/serio/Start-SerioMonolith.ps1` — orchestration script
- `fda-serio/docs/runbooks/RUNBOOK-run-serio.md` — detailed runbook (FS-014)
- `fda-serio/docs/runbooks/RUNBOOK-build-serio.md` — build gotchas (FS-011)
- `fda-serio/docs/runbooks/RUNBOOK-serio-weblogic-setup.md` — WebLogic domain setup
- `skills/serioplus-data-services/SKILL.md` — SERIO+ data tier (separate stack)
