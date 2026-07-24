---
name: serio-cli
description: Start, stop, restart, and check status of any SERIO or SERIO+ service with simple commands. Use this skill whenever you need to run, restart, or check on any part of the SERIO/SERIO+ stack. Single tool covers all tiers -- data, business, Angular UI, and the SERIO monolith.
metadata:
  version: "1.0.0"
  runtime: powershell
  tool: tools/serio/Serio.ps1
---

# Skill: serio-cli

One command to start, stop, restart, build, and check status of any SERIO or SERIO+ service.

## Install (one-time)

```powershell
C:\projects\aitools\tools\serio\Install-SerioAlias.ps1
. $PROFILE
```

This adds `serio` as a function to your PowerShell profile so it works in every terminal.

## Commands

```
serio start   <target>
serio stop    <target>
serio restart <target>
serio build   <target>
serio status
```

## Targets

| Target | What |
|--------|------|
| `all` | Full SERIO+ stack: data -> business -> UI |
| `data` | SERIOPlusDataServices (:8090-8097 + gateway :8070) |
| `business` | SERIOPlusServices (:8080-8086) |
| `app` | SERIOPlusApp Angular UI (:4201) |
| `monolith` | SERIO monolith: WebLogic :7001 + Angular :4200 |
| `<service-name>` | Any single service, e.g. `serioplus-document-service` |

## Build targets

| Target | What |
|--------|------|
| `all` | common-lib -> data -> business -> app |
| `common-lib` | serioplus-common-library:13.0.0-SNAPSHOT |
| `data` | SERIOPlusDataServices (after common-lib) |
| `business` | SERIOPlusServices (after common-lib) |
| `app` | SERIOPlusApp npm install |

## Usage examples

```powershell
# Full SERIO+ stack
serio start all
serio stop all
serio restart all

# SERIO monolith
serio start monolith
serio stop monolith

# Individual tiers
serio start data
serio start business
serio start app

# Single service
serio start serioplus-document-service
serio stop serioplus-document-service
serio restart serioplus-work-data-service

# Build
serio build all
serio build data
serio build common-lib

# Check what's running
serio status
```

## What serio status shows

```
== SERIO Stack Status ==================================
  [UP]  :4201  SERIO+ Angular UI
  [UP]  :8070  local-gateway-service
  [UP]  :8095  document-service
  [  ]  :8090  entry-data-service
  ...
== Tracked PIDs ========================================
  [UP]  serioplus-document-service     PID 12345
  [UP]  local-gateway-service          PID 12346
```

## Service name reference

### Data tier (:8090-8097 + gateway :8070)

| Service name | Port |
|--------------|------|
| `local-gateway-service` | :8070 |
| `serioplus-entry-data-service` | :8090 |
| `serioplus-lookup-data-service` | :8091 |
| `serioplus-user-org-data-service` | :8092 |
| `serioplus-work-data-service` | :8093 |
| `serioplus-application-service` | :8094 |
| `serioplus-document-service` | :8095 |
| `serioplus-screening-data-service` | :8096 |
| `serioplus-filer-eval-data-service` | :8097 |

### Business tier (:8080-8086)

| Service name | Port |
|--------------|------|
| `serioplus-general-admin-service` | :8080 |
| `serioplus-user-option-service` | :8081 |
| `serioplus-aiml-services` | :8082 |
| `serioplus-workflow-service` | :8083 |
| `serioplus-notice-service` | :8084 |
| `serioplus-screening-service` | :8085 |
| `serioplus-filer-eval-service` | :8086 |

## How it works

- **Spring Boot services** are launched with `java -jar ... --spring.profiles.active=local` (no AWS required)
- **PIDs and logs** are tracked in `C:\projects\.serio-stack\` — one `.log` per service
- **JDK auto-selected**: JDK 17 for SERIO+ services, JDK 21 for the monolith
- **Gateway wait**: when starting `data` or `all`, waits for :8070 before continuing to business tier
- **Restart** = stop + 2s pause + start in one command

## Prerequisites

- FDA laptop, full-tunnel VPN up
- JDK 17 installed (Eclipse Adoptium) — for SERIO+
- JDK 21 installed (Eclipse Adoptium) — for SERIO monolith
- Maven on PATH — for builds
- Node/npm on PATH — for Angular
- Jars already built — run `serio build <target>` first if needed

## Related

- `tools/serio/Serio.ps1` — the implementation
- `tools/serio/Install-SerioAlias.ps1` — installs the `serio` shell alias
- `docs/runbooks/RUNBOOK-serio-cli.md` — setup and troubleshooting
