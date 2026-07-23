---
name: serioplus-business-services
description: Build and run the SERIOPlusServices tier — 7 Spring Boot business-layer microservices (Java 17, :8080-8086). Use when you need to build, start, stop, or debug the SERIO+ business services (general-admin, user-option, aiml, workflow, notice, screening, filer-eval). Requires the data tier (SerioPlusStack gateway :8070) to be up first.
metadata:
  version: "1.0.0"
  runtime: powershell
  repo: SERIOPlusServices
  ports: "general-admin :8080 | user-option :8081 | aiml :8082 | workflow :8083 | notice :8084 | screening :8085 | filer-eval :8086"
---

# Skill: serioplus-business-services

Build and run the **SERIOPlusServices** tier — the business layer of the SERIO+ microservice stack.

## What this is

A Maven multi-module reactor (`serioplus-business-services`, Java 17) with 7 Spring Boot services.
This tier sits between the Angular UI and the data layer. It calls the data layer via the local
gateway at `localhost:8070`.

| Module | Port | Purpose |
|--------|------|---------|
| `serioplus-general-admin-service` | **:8080** | General admin / core orchestration |
| `serioplus-user-option-service` | :8081 | User preferences / options |
| `serioplus-aiml-services` | :8082 | AI/ML model integration |
| `serioplus-workflow-service` | :8083 | SZR / workflow business logic |
| `serioplus-notice-service` | :8084 | Notices |
| `serioplus-screening-service` | :8085 | Screening business logic |
| `serioplus-filer-eval-service` | :8086 | Filer evaluation |

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus + Oracle reachable |
| **JDK 17** on PATH | `java -version` → `17.x` — **NOT JDK 21** |
| Maven on PATH | `mvn -version` |
| common-lib 13.0.0-SNAPSHOT installed | `serioplus-data-services` SKILL step 1 |
| **Data tier up** (:8070 gateway responding) | `Test-NetConnection localhost -Port 8070` |

## Build

### Step 1 — install common-lib (if not already done this session)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"

cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install
```

### Step 2 — build the business services

```powershell
cd C:\projects\SERIOPlusServices

# Full reactor
mvn -DskipTests -nsu clean install

# Single service
mvn -DskipTests -nsu -pl serioplus-workflow-service clean install
mvn -DskipTests -nsu -pl serioplus-general-admin-service clean install
```

### Via SerioPlusStack.ps1

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action build -Only services
```

## Run

### Single service (local profile)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"

# Workflow service (:8083)
java -jar C:\projects\SERIOPlusServices\serioplus-workflow-service\target\serioplus-workflow-service.jar `
  --spring.profiles.active=local

# General admin (:8080)
java -jar C:\projects\SERIOPlusServices\serioplus-general-admin-service\target\serioplus-general-admin-service.jar `
  --spring.profiles.active=local
```

### Full business tier via SerioPlusStack.ps1

```powershell
# Start data first (if not running), then business layer
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only services

# Or start the full stack (data → services → UI)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start
```

### Stop

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop

# Kill specific service
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
  Where-Object { $_.CommandLine -like '*serioplus-workflow-service*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## Verify it's up

```powershell
# Check all business ports
8080,8081,8082,8083,8084,8085,8086 | ForEach-Object {
    $up = $false
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$_); $c.Close(); $up=$true } catch {}
    [pscustomobject]@{ Port=$_; Up=$up }
} | Format-Table

# Actuator health
Invoke-RestMethod http://localhost:8083/actuator/health -EA 0  # workflow
Invoke-RestMethod http://localhost:8080/actuator/health -EA 0  # general-admin
```

## Key gotchas

| # | Gotcha | Fix |
|---|--------|-----|
| 1 | **Data layer must be up first** — business services call `localhost:8070` at startup | Start data tier first; wait for gateway |
| 2 | **JDK 17 required** | Set `JAVA_HOME` to JDK 17 |
| 3 | **common-lib SNAPSHOT** | Install with quoted `-Drevision=13.0.0-SNAPSHOT`, use `-nsu` |
| 4 | **`AccessFilter` → 403** | Add path to `noUserApis` in `FilterConfig`, rebuild |
| 5 | **Jar locked on Windows** | Kill java by command line before rebuild |
| 6 | **`server` profile needs AWS creds** | Use `--spring.profiles.active=local` |

## Runtime topology

```
SERIOPlusApp :4201
     ↓
SERIOPlusServices :8080-8086  ← this tier
     ↓
local-gateway-service :8070
     ↓
SERIOPlusDataServices :8090-8097
     ↓
OASIS Oracle DB (gi-22040-22041.fda.gov:1523)
```

## Logs (via SerioPlusStack.ps1)

```
C:\projects\.serioplus-stack\
  serioplus-general-admin-service.log
  serioplus-workflow-service.log
  serioplus-aiml-services.log
  ... (one per service)
```

## Related

- `skills/serioplus-data-services/SKILL.md` — the data tier this calls
- `skills/serioplus-app/SKILL.md` — the Angular UI that calls this tier
- `skills/serioplus-local-run/SKILL.md` — single-service detailed reference
- `tools/serioplus/SerioPlusStack.ps1` — build + start + stop + status
