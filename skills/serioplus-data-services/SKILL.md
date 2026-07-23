---
name: serioplus-data-services
description: Build and run the SERIOPlusDataServices tier — 8 Spring Boot data-layer microservices (Java 17, :8090-8097) plus the local gateway (:8070) that fronts them. Use when you need to build, start, stop, or debug any of the SERIO+ data services. Covers the full dependency chain (common-lib first), all gotchas (JDK 17, SNAPSHOT coordinate, -nsu, Oracle tunnel, AccessFilter, jar-lock), and log locations.
metadata:
  version: "1.0.0"
  runtime: powershell
  repo: SERIOPlusDataServices
  ports: "gateway :8070 | entry :8090 | lookup :8091 | user-org :8092 | work :8093 | application :8094 | document :8095 | screening :8096 | filer-eval :8097"
---

# Skill: serioplus-data-services

Build and run the **SERIOPlusDataServices** tier — the data layer of the SERIO+ microservice stack.

## What this is

A Maven multi-module reactor (`serioplus-data-services`, Java 17) containing 8 Spring Boot services
and a Spring Cloud Gateway that fronts them locally. The data layer is the **only** tier that talks
directly to the OASIS Oracle database.

| Module | Port | Purpose |
|--------|------|---------|
| `local-gateway-service` | **:8070** | Routes all data-tier calls; entry point for business layer |
| `serioplus-entry-data-service` | :8090 | Entry/import data |
| `serioplus-lookup-data-service` | :8091 | Lookup / reference data |
| `serioplus-user-org-data-service` | :8092 | User / org data |
| `serioplus-work-data-service` | :8093 | Work items / SZR workflow |
| `serioplus-application-service` | :8094 | Application data |
| `serioplus-document-service` | :8095 | Document generation (PDF — OGA, SZR) |
| `serioplus-screening-data-service` | :8096 | Screening data |
| `serioplus-filer-eval-data-service` | :8097 | Filer evaluation data |

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop | This tier cannot run off-network |
| **Full-tunnel VPN up** | Nexus (to build) + Oracle `gi-22040-22041.fda.gov:1523` (to run) |
| **JDK 17** on PATH | `java -version` → `17.x`. **NOT JDK 21** — Lombok breaks |
| Maven on PATH | `mvn -version` |
| FDA Nexus access | `~/.m2/settings.xml` pointing at Nexus |
| common-lib SNAPSHOT installed | Step 1 below |

## Build

### Step 1 — install common-lib as 13.0.0-SNAPSHOT (do this first, every session)

```powershell
# Set JDK 17
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"

cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install
```

> ⚠️ **Quote the `-Drevision` flag in PowerShell** — without quotes, PowerShell splits it and Maven
> sees `13` as the version and `.0.0-SNAPSHOT` as a lifecycle phase.

### Step 2 — build the data services

```powershell
cd C:\projects\SERIOPlusDataServices

# Full reactor build (all 8 services + gateway)
mvn -DskipTests -nsu clean install

# OR build a single service (faster)
mvn -DskipTests -nsu -pl serioplus-document-service clean install
mvn -DskipTests -nsu -pl serioplus-work-data-service clean install
mvn -DskipTests -nsu -pl serioplus-entry-data-service clean install
```

> `-nsu` (`--no-snapshot-updates`) makes Maven use your freshly-installed local snapshot instead of
> pulling the stale one from Nexus.

### Using SerioPlusStack.ps1

```powershell
# Build all (common-lib → data only)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action build -Only data
```

## Run

### Single service (local profile — no AWS)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"

# Document service (:8095)
java -jar C:\projects\SERIOPlusDataServices\serioplus-document-service\target\serioplus-document-service.jar `
  --spring.profiles.active=local

# Work data service (:8093)
java -jar C:\projects\SERIOPlusDataServices\serioplus-work-data-service\target\serioplus-work-data-service.jar `
  --spring.profiles.active=local
```

### Full data tier via SerioPlusStack.ps1

```powershell
# Start all data services + gateway (local profile, no AWS)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only data

# Start with the server profile (reads AWS SSM — needs AWS creds)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only data -Profile server
```

### Stop

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop

# Or kill a specific service by name:
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
  Where-Object { $_.CommandLine -like '*serioplus-document-service*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## Verify it's up

```powershell
# Gateway health
Invoke-RestMethod http://localhost:8070/actuator/health -ErrorAction SilentlyContinue

# Document service direct
Invoke-RestMethod http://localhost:8095/actuator/health -ErrorAction SilentlyContinue

# Check all ports
8070,8090,8091,8092,8093,8094,8095,8096,8097 | ForEach-Object {
    $up = $false
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$_); $c.Close(); $up=$true } catch {}
    [pscustomobject]@{ Port=$_; Up=$up }
} | Format-Table
```

## Gotcha catalog

| # | Gotcha | Fix |
|---|--------|-----|
| 1 | **JDK 21 → Lombok breaks** (`NoSuchFieldError: JCImport.qualid`) | Set `JAVA_HOME` to JDK 17 before `mvn` |
| 2 | **common-lib version** — services need `13.0.0-SNAPSHOT`; lib builds as `13.0.0` | Install with `'-Drevision=13.0.0-SNAPSHOT'` (quoted) |
| 3 | **Stale snapshot from Nexus** — `-nsu` ignored without it | Always use `mvn … -nsu` for data/services build |
| 4 | **Purge stale snapshot** if service still can't see your new class | `Remove-Item -Recurse -Force "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library"` then reinstall |
| 5 | **Oracle tunnel required** — `DataSourceWarmer` opens Hikari pools at boot | VPN full-tunnel up; `gi-22040-22041.fda.gov:1523` must be reachable |
| 6 | **`AccessFilter` → 403** on non-whitelisted paths | Add path to `noUserApis` in `FilterConfig`, rebuild |
| 7 | **`java -jar` locks the jar** — `mvn clean` fails with "Cannot delete jar" | Kill java process by command line BEFORE rebuild |
| 8 | **`server` profile → AWS abort** | Use `--spring.profiles.active=local` for local dev |
| 9 | **iText license** — 500 on PDF endpoints | `C:/u07/wls_12214/serio/config/itext-*_license.json` must exist |
| 10 | **`docInfo` compile bug** on `dev` branch | Run `handoff/serio-39310/Fix-LocalRun.ps1` (idempotent) |
| 11 | **`SerioImportsInvestigationDocument` missing from `persistence.xml`** | Same fix script above |

## Logs

When run via `SerioPlusStack.ps1`, logs land in `C:\projects\.serioplus-stack\`:

```
.serioplus-stack\
  local-gateway-service.log
  serioplus-entry-data-service.log
  serioplus-document-service.log
  serioplus-work-data-service.log
  ... (one per service)
  state.json   ← tracked PIDs
```

When run manually, stdout goes to your terminal.

## Symptom → diagnosis

| Symptom | Cause | Fix |
|---------|-------|-----|
| `403 Forbidden` | `AccessFilter` — path not in `noUserApis` | Add path, rebuild |
| `404 No static resource api/…` | Controller not in jar (stale build) | Stop → rebuild → restart |
| `Port 809x already in use` | Old instance running | Kill by command line |
| `AWS credentials not available` | Wrong Spring profile | Use `--spring.profiles.active=local` |
| `No [ManagedType] …` | Entity missing from `persistence.xml` | Add `<class>` entry |
| `package …dto… does not exist` | Wrong common-lib snapshot resolved | Purge + reinstall + `-nsu` |
| Boot hangs / ORA-12541 | Oracle unreachable | VPN full-tunnel up; verify tunnel |
| 500 on `/generate-seizure-memo` | iText license missing | Place license files or override path |

## Related

- `skills/serioplus-business-services/SKILL.md` — the business tier that calls this gateway
- `skills/serioplus-local-run/SKILL.md` — single-service detailed gotcha reference
- `tools/serioplus/SerioPlusStack.ps1` — orchestrates build + start + stop + status
- `RUNBOOK-build-run-serioplus.md` in `fda-serio/docs/runbooks/` — topology + build order
