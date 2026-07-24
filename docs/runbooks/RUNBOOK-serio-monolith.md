# RUNBOOK — SERIO Monolith (WebLogic + Angular)

Build and run the SERIO monolith locally — the on-prem Java EE app.
WebLogic `:7001` (backend) + Angular `:4200` (frontend).

> This is a **separate stack** from SERIO+. It uses **JDK 21** (not 17) and WebLogic (not Spring Boot jars).

---

## Hosted environments (no local setup needed)

| Environment | URL |
|-------------|-----|
| **Dev** | `https://oii.dev.fda.gov/serio` |
| **Test** | `https://oii.test.fda.gov/serio` |
| **Pre-prod** | `https://oii.preprod.fda.gov/serio` |

> Dev is unstable during work hours. Use **Test** for reliable verification.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus + Oracle `gi-22040-22041.fda.gov:1523` |
| **JDK 21** | `java -version` → `21.x` (opposite of SERIO+) |
| Maven on PATH | `mvn -version` |
| **WebLogic 14.1.2.0** installed | `C:\FDA\AppServer\Oracle_Home_14120` exists |
| `serio` domain configured | `...\domains\serio\bin\startWebLogic.cmd` exists |
| `SerioDS` datasources set up | See `RUNBOOK-serio-weblogic-setup.md` in `fda-serio` |
| Node / npm | For Angular frontend |
| OASIS user provisioned | Request from Kaustav Lahiri → Soumen Kundu (DBA) |

---

## One command (full stack)

```powershell
C:\projects\fda-serio\tools\serio\Start-SerioMonolith.ps1
# → http://localhost:4200
```

Actions: `up` (default) | `weblogic` | `deploy` | `frontend`

---

## Manual steps

### Step 1 — Set JDK 21

```powershell
$jdk = Get-ChildItem 'C:\Program Files\Eclipse Adoptium' -Directory |
       Where-Object { $_.Name -match 'jdk-?21' -and (Test-Path "$($_.FullName)\bin\java.exe") } |
       Select-Object -First 1
$env:JAVA_HOME = $jdk.FullName
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version   # must say 21.x
```

### Step 2 — Start WebLogic (in its own terminal)

```powershell
Start-Process 'C:\FDA\AppServer\Oracle_Home_14120\user_projects\domains\serio\bin\startWebLogic.cmd' -WindowStyle Normal
```

Wait for WebLogic to be up on `:7001`:
```powershell
while (-not (Test-NetConnection localhost -Port 7001 -InformationLevel Quiet -EA 0)) {
    Write-Host "waiting..."; Start-Sleep 5
}
Write-Host "WebLogic up on :7001"
```

### Step 3 — Build and deploy the EAR

```powershell
cd C:\projects\SERIO
mvn -DskipTests -Pdeveloper clean package
```

The `developer` Maven profile copies `serio-ws.ear` to WebLogic's autodeploy folder. WebLogic picks it up automatically.

> ⚠️ If the build fails with antrun `<tasks>` vs `<target>` error (FS-011), apply the fix first:
> `C:\projects\fda-serio\handoff\serio-39310\Fix-SerioWsEar.ps1`
> Or use: `Start-SerioMonolith.ps1 -Action deploy -FixAntrun`

### Step 4 — Start the Angular frontend

```powershell
cd C:\projects\SERIO\serio-app-war
npm install   # first time or after dependency changes
npm start
# → http://localhost:4200
```

---

## Verify it's running

```powershell
# Backend
Test-NetConnection localhost -Port 7001 -InformationLevel Quiet

# Frontend
Test-NetConnection localhost -Port 4200 -InformationLevel Quiet

# Open in browser
Start-Process 'http://localhost:4200'
```

---

## Stop

```powershell
# Angular frontend: Ctrl+C in its terminal

# WebLogic: close the WebLogic terminal window, or:
C:\FDA\AppServer\Oracle_Home_14120\user_projects\domains\serio\bin\stopWebLogic.cmd
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| EAR deploy fails (antrun) | `<tasks>` vs `<target>` bug (FS-011) | Apply `Fix-SerioWsEar.ps1` or use `-FixAntrun` flag |
| `401 "An OASIS user profile was not found."` | OASIS account not provisioned | Request from Kaustav Lahiri → Soumen Kundu |
| WebLogic won't start | Datasources misconfigured | See `RUNBOOK-serio-weblogic-setup.md` |
| Nexus 401 during build | VPN down | Full-tunnel VPN up |
| Wrong JDK | JDK 17 in PATH | SERIO needs JDK **21** — check `java -version` |

---

## OASIS user provisioning

Verify with SQL (connect as `oasis_er`, tunnel up):
```sql
SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
FROM FDA_PERSONNEL p
LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
WHERE LOWER(p.EMAIL_ADRS) LIKE 'anthony.dourish%';
```

---

## SERIO vs SERIO+ at a glance

| | SERIO (monolith) | SERIO+ (microservices) |
|--|------------------|-----------------------|
| **JDK** | **21** | **17** |
| **Server** | WebLogic :7001 | Spring Boot jars :8070-8097 |
| **UI port** | :4200 | :4201 |
| **Deploy** | EAR via Maven `developer` profile | `java -jar` |

---

## Related

- `fda-serio/tools/serio/Start-SerioMonolith.ps1` — orchestration script
- `fda-serio/docs/runbooks/RUNBOOK-run-serio.md` — detailed runbook (FS-014, verified end-to-end)
- `fda-serio/docs/runbooks/RUNBOOK-serio-weblogic-setup.md` — domain + datasource setup
- `skills/serio-monolith/SKILL.md` — skill reference
