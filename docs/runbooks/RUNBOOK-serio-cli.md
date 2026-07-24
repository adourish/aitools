# RUNBOOK -- serio CLI

The `serio` command starts, stops, restarts, builds, and checks status of any SERIO or SERIO+
service from a single tool.

---

## Install (one-time per machine)

```powershell
C:\projects\aitools\tools\serio\Install-SerioAlias.ps1
. $PROFILE
```

Verify:

```powershell
serio status
```

---

## Quick reference

```powershell
serio start   all                          # full SERIO+ stack
serio start   monolith                     # SERIO WebLogic + EAR + Angular :4200
serio start   data                         # data tier only (:8090-8097 + gateway :8070)
serio start   business                     # business tier only (:8080-8086)
serio start   app                          # Angular UI only (:4201)
serio start   serioplus-document-service   # single service by name

serio stop    all
serio stop    monolith
serio stop    data
serio stop    serioplus-document-service

serio restart all
serio restart business
serio restart serioplus-work-data-service

serio build   all                          # common-lib -> data -> business -> app
serio build   common-lib                   # just the shared JAR
serio build   data
serio build   business
serio build   app                          # npm install

serio status                               # port health + tracked PIDs
```

---

## First run -- build before start

The jars must be built before `serio start` can find them. On a fresh checkout or after a code change:

```powershell
serio build all
serio start all
```

---

## Start order (what `serio start all` does automatically)

1. Build check -- warns if jars are missing
2. **Data layer** -- starts all 8 data services + gateway; waits for :8070
3. **Business layer** -- starts all 7 business services
4. **UI** -- starts ng serve :4201

---

## Logs

All logs go to `C:\projects\.serio-stack\`:

```
.serio-stack\
  serioplus-document-service.log
  serioplus-document-service.err.log
  local-gateway-service.log
  serioplus-general-admin-service.log
  serioplus-app.log
  weblogic.log          (monolith only)
  serio-app.log         (monolith only)
  state.json            tracked PIDs
```

Tail a log while a service starts:

```powershell
Get-Content C:\projects\.serio-stack\serioplus-document-service.log -Wait -Tail 40
```

---

## Port reference

| Port | Service |
|------|---------|
| :4200 | SERIO monolith Angular |
| :4201 | SERIO+ Angular UI |
| :7001 | WebLogic (monolith) |
| :8070 | local-gateway-service |
| :8080 | serioplus-general-admin-service |
| :8081 | serioplus-user-option-service |
| :8082 | serioplus-aiml-services |
| :8083 | serioplus-workflow-service |
| :8084 | serioplus-notice-service |
| :8085 | serioplus-screening-service |
| :8086 | serioplus-filer-eval-service |
| :8090 | serioplus-entry-data-service |
| :8091 | serioplus-lookup-data-service |
| :8092 | serioplus-user-org-data-service |
| :8093 | serioplus-work-data-service |
| :8094 | serioplus-application-service |
| :8095 | serioplus-document-service |
| :8096 | serioplus-screening-data-service |
| :8097 | serioplus-filer-eval-data-service |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `serio: not recognized` | Profile not reloaded | `. $PROFILE` |
| `jar not found` | Not built yet | `serio build data` (or `business`) |
| `already up on :XXXX` | Service already running | `serio restart <target>` |
| `Gateway :8070 not up` warning | Data tier not started | `serio start data` first |
| Service exits immediately | Boot error -- check log | `Get-Content C:\projects\.serio-stack\<name>.log -Tail 50` |
| `Port XXXX already in use` | Orphaned process | See "Kill orphaned processes" below |
| `JDK 17/21 not found` | Wrong Eclipse Adoptium path | Update `$JDK17`/`$JDK21` in `Serio.ps1` |
| Monolith EAR deploy fails | antrun bug (FS-011) | Apply `Fix-SerioWsEar.ps1` then retry |
| `WARN: serio already in profile` | Already installed | Already good -- just `. $PROFILE` |
| `. $PROFILE` errors | Profile path has spaces | Use `& $PROFILE` or open a new terminal |

### Kill orphaned processes

If a service is running but not tracked (started manually or survived a crash):

```powershell
# Find it
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
    Where-Object { $_.CommandLine -like '*serioplus-document-service*' } |
    Select-Object ProcessId, CommandLine

# Kill it
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
    Where-Object { $_.CommandLine -like '*serioplus-document-service*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# Kill all java (nuclear)
Get-Process -Name java -EA 0 | Stop-Process -Force
```

### Clear stale state

If `serio status` shows PIDs that don't exist:

```powershell
Remove-Item C:\projects\.serio-stack\state.json
```

---

## Reload after code change (typical workflow)

```powershell
# 1. Stop what you're changing
serio stop serioplus-document-service

# 2. Rebuild (common-lib first if you changed a DTO)
serio build common-lib
serio build data

# 3. Restart
serio start serioplus-document-service
```

Or for a full reset:

```powershell
serio stop all
serio build all
serio start all
```

---

## Related

- `skills/serio-cli/SKILL.md` -- skill reference
- `tools/serio/Serio.ps1` -- implementation
- `tools/serio/Install-SerioAlias.ps1` -- profile installer
- `docs/runbooks/RUNBOOK-serioplus-full-stack.md` -- manual start commands without the CLI
