---
name: serioplus-app
description: Build and run the SERIOPlusApp Angular 19 UI (:4201, /serioplus/). Use when you need to install deps, start the dev server, or debug the SERIO+ frontend. The app proxies to the business layer at localhost:8070. Covers npm/Nexus setup, ng serve, the acceptBanner query param, and hosted dev/test environments.
metadata:
  version: "1.0.0"
  runtime: node
  repo: SERIOPlusApp
  port: "4201"
  url: "http://localhost:4201/serioplus/"
---

# Skill: serioplus-app

Build and run the **SERIOPlusApp** — the Angular 19 frontend of the SERIO+ application.

## What this is

An Angular 19 workspace (`serioplus` app + `shared-lib` / `cv-helper` libraries). Served at
`http://localhost:4201/serioplus/`. The app calls the SERIO+ business layer and various external
`*.dev.fda.gov` services; it deep-links to the on-prem SERIO monolith using `?acceptBanner=true`.

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus npm registry + external FDA services reachable |
| Node.js (18, 20, or 22) | `node --version` |
| npm | `npm --version` |
| Angular CLI | `ng version` (or use `npx ng`) |
| FDA Nexus `.npmrc` | `.npmrc` file present in `SERIOPlusApp/` (copied from `.npmrc.example`) |
| **Business layer up** (optional for pure UI work) | `Test-NetConnection localhost -Port 8070` |

## Hosted environments (no local setup needed)

| Environment | URL |
|-------------|-----|
| **Dev** | `https://oii-cloud.dev.fda.gov/serioplus/#/?acceptBanner=true` |
| **Test** | `https://oii-cloud.test.fda.gov/serioplus/#/?acceptBanner=true` |
| **Pre-prod** | `https://oii-cloud.preprod.fda.gov/serioplus/#/?acceptBanner=true` |

> **Dev is unstable during work hours** (people merging throughout the day). Use **Test** for
> reliable verification. Sign in via SSO first: `https://sso2.fda.gov/idp/startSSO.ping?PartnerSpId=FDA_AWS_GovCloud`

## Build / install

### One-time: copy the Nexus .npmrc

```powershell
cd C:\projects\SERIOPlusApp
Copy-Item .npmrc.example .npmrc    # only if .npmrc doesn't exist yet
```

### Install dependencies

```powershell
cd C:\projects\SERIOPlusApp
npm install
```

### Via SerioPlusStack.ps1

```powershell
# Install deps (npm install only — 'start' action serves it)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action build -Only app
```

## Run (dev server)

```powershell
cd C:\projects\SERIOPlusApp
npm start
# OR
npx ng serve

# Served at: http://localhost:4201/serioplus/
```

### Via SerioPlusStack.ps1

```powershell
# Start the UI only (headless, log to .serioplus-stack\app-ngserve.log)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only app

# Full stack: data → business → UI
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start
```

### Open in browser

```powershell
Start-Process "http://localhost:4201/serioplus/#/?acceptBanner=true"
```

## Deep-link format

The `?acceptBanner=true` query param auto-accepts the US Government warning banner — include it on
every direct link so you land in the app without the click-through. SERIO uses it on all cross-app
links too.

## Stop the dev server

```powershell
# If run via SerioPlusStack.ps1:
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop

# If run manually in a terminal: Ctrl+C in the terminal window.

# If running headless and you need to find it:
Get-Process -Name 'node' | Where-Object { $_.CommandLine -like '*ng serve*' -or $_.MainWindowTitle -like '*ng serve*' }
```

## Status check

```powershell
# Port up?
try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',4201); $c.Close(); 'UP' } catch { 'DOWN' }

# Or via SerioPlusStack.ps1:
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action status
```

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `npm install` fails with 401/404 | `.npmrc` missing or wrong registry | Copy `.npmrc.example` → `.npmrc`; VPN must be up |
| `Package 'cv-helper' not found` | Nexus unreachable | Full-tunnel VPN up |
| App loads but API calls fail | Business layer not running | Start business tier first |
| `EADDRINUSE :4201` | Another `ng serve` already running | Kill it: `Stop-Process -Name node -Force` (or be selective) |
| Blank page after login | OASIS user not provisioned | Request provisioning from Kaustav Lahiri → Soumen Kundu (DBA) |
| `?acceptBanner=true` does nothing | Angular not loaded yet | Wait for the app to fully load; it's read by NavigationService |

## OASIS user provisioning

The app authenticates you by matching your email in the OASIS DB. Until a DBA creates your row in
`FDA_PERSONNEL` and `USER_PROFILES`, you get `401 "An OASIS user profile was not found."` everywhere.
Request provisioning from **Kaustav Lahiri** (SERIO lead) → **Soumen Kundu** (DBA) for **Dev** and
**Test** environments.

Verify with SQL (tunnel + SQL Developer / SQLcl, connect as `oasis_er`):
```sql
SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
FROM FDA_PERSONNEL p
LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
WHERE LOWER(p.EMAIL_ADRS) LIKE 'anthony.dourish%';
```

## Build-lib: shared-ui-component-library (if needed)

The app imports `@ora/shared-service-common-ui` from `shared-ui-component-library`. Usually you get
this from Nexus automatically. Only rebuild locally if you're changing that library:

```powershell
cd C:\projects\shared-ui-component-library\shared-service-ui   # find pkg with build-lib script
npm install
npm run build-lib
```

## Runtime topology

```
Browser
  → http://localhost:4201/serioplus/
    SERIOPlusApp (ng serve)  ← this tier
      → SERIOPlusServices :8080-8086 (business layer)
        → gateway :8070 → SERIOPlusDataServices :8090-8097
      → *.dev.fda.gov (external FDA services, via VPN)
      ↔ SERIO monolith (:7001 or oii.dev.fda.gov/serio) via deep links
```

## Related

- `skills/serioplus-business-services/SKILL.md` — the business tier the UI calls
- `skills/serioplus-data-services/SKILL.md` — the data tier
- `tools/serioplus/SerioPlusStack.ps1` — full-stack build + start + stop
