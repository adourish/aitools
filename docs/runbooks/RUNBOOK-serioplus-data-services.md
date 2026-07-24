# RUNBOOK — SERIOPlusDataServices (data layer)

Build and run the SERIO+ data-layer services locally.
**8 Spring Boot services + a gateway.** Ports: gateway `:8070`, services `:8090–8097`.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop | Off-network: builds fail (Nexus), runtime fails (Oracle) |
| **Full-tunnel VPN up** | Nexus for builds; Oracle `gi-22040-22041.fda.gov:1523` for runtime |
| **JDK 17** | `java -version` → `17.x` — **NOT 21** (Lombok breaks) |
| Maven on PATH | `mvn -version` |
| `~/.m2/settings.xml` → Nexus | FDA Nexus must be reachable |
| common-lib SNAPSHOT installed | See Step 1 below |

---

## Step 1 — Set JDK 17 (every terminal session)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
java -version   # must say 17.x
```

---

## Step 2 — Install common-lib as SNAPSHOT (once per session)

```powershell
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn -DskipTests clean install
```

---

## Step 3 — Build data services

```powershell
# Full reactor (all 8 services)
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu clean install

# OR build individual services (faster for targeted work)
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu -pl serioplus-work-data-service clean install
mvn -DskipTests -nsu -pl serioplus-document-service clean install
```

> `-nsu` = `--no-snapshot-updates` — uses your locally-installed common-lib snapshot instead of pulling from Nexus.

---

## Step 4 — Start services (each in its own terminal)

Run the JDK 17 env block in each terminal first, then:

### Data services (:8090–8097)

```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-entry-data-service
java -jar target\serioplus-entry-data-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-lookup-data-service
java -jar target\serioplus-lookup-data-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-user-org-data-service
java -jar target\serioplus-user-org-data-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-work-data-service
java -jar target\serioplus-work-data-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-application-service
java -jar target\serioplus-application-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-document-service
java -jar target\serioplus-document-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-screening-data-service
java -jar target\serioplus-screening-data-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusDataServices\serioplus-filer-eval-data-service
java -jar target\serioplus-filer-eval-data-service.jar --spring.profiles.active=local
```

### Gateway (:8070) — start last in this tier

```powershell
cd C:\projects\SERIOPlusDataServices\local-gateway-service
java -jar target\local-gateway-service.jar --spring.profiles.active=local
```

---

## Alternative — SerioPlusStack.ps1 (headless, all at once)

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only data
# Logs → C:\projects\.serioplus-stack\<service-name>.log
```

---

## Verify ports are up

```powershell
8070,8090,8091,8092,8093,8094,8095,8096,8097 | ForEach-Object {
    $up = $false
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$_); $c.Close(); $up=$true } catch {}
    [pscustomobject]@{ Port=$_; Up=$up }
} | Format-Table
```

---

## Stop a service

```powershell
# Kill by service name (safe — only kills that jar)
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
  Where-Object { $_.CommandLine -like '*serioplus-document-service*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# Stop everything tracked by SerioPlusStack
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop
```

> ⚠️ **Kill the process BEFORE rebuilding.** `java -jar` holds a lock on the jar file — `mvn clean` will fail with "Cannot delete jar" if the service is still running.

---

## Port reference

| Port | Service | Notes |
|------|---------|-------|
| :8070 | `local-gateway-service` | Entry point for business layer — start last |
| :8090 | `serioplus-entry-data-service` | Entry / import data |
| :8091 | `serioplus-lookup-data-service` | Reference / lookup data |
| :8092 | `serioplus-user-org-data-service` | User / org data |
| :8093 | `serioplus-work-data-service` | Work items / SZR |
| :8094 | `serioplus-application-service` | Application data |
| :8095 | `serioplus-document-service` | PDF generation (OGA, SZR) |
| :8096 | `serioplus-screening-data-service` | Screening |
| :8097 | `serioplus-filer-eval-data-service` | Filer evaluation |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Lombok NoSuchFieldError: JCImport.qualid` | JDK 21 | Switch to JDK 17 |
| `package …dto… does not exist` | Stale common-lib snapshot | Purge `~/.m2/…/serioplus-common-library`, reinstall, use `-nsu` |
| Boot hangs / `ORA-12541` | Oracle unreachable | VPN full-tunnel up |
| `403 Forbidden` on API call | `AccessFilter` — path not whitelisted | Add path to `noUserApis` in `FilterConfig`, rebuild |
| `AWS credentials not available` | Wrong Spring profile | Use `--spring.profiles.active=local` |
| `Port 809x already in use` | Old instance still running | Kill by command line (see Stop section) |
| `Cannot delete … .jar` during `mvn clean` | Jar locked by running process | Kill the java process first |
| `iText license validation failed` (500) | License file missing | Place `itext-*_license.json` at `C:/u07/wls_12214/serio/config/` |

---

## Related

- `RUNBOOK-serioplus-business-services.md` — start after this tier
- `RUNBOOK-serioplus-app.md` — Angular UI (top of stack)
- `skills/serioplus-data-services/SKILL.md` — skill reference
- `tools/serioplus/SerioPlusStack.ps1` — full-stack orchestration
