# RUNBOOK — SERIO+ Full Stack (all tiers)

Start the complete SERIO+ stack locally from scratch — common-lib through Angular UI.

---

## Quick start (one command)

```powershell
# Build everything
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action build

# Start everything (data → business → UI)
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start

# Check status
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action status

# Stop everything
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop
```

Open: **`http://localhost:4201/serioplus/#/?acceptBanner=true`**

---

## Manual start — step by step

> **Prerequisites:** FDA laptop, full-tunnel VPN, JDK 17, Maven, Node/npm, `~/.m2/settings.xml` → Nexus.

### 0 — Set JDK 17 (every session, in every terminal)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
```

### 1 — Install common-lib

```powershell
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn -DskipTests clean install
```

### 2 — Build data services

```powershell
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu clean install
```

### 3 — Build business services

```powershell
cd C:\projects\SERIOPlusServices
mvn -DskipTests -nsu clean install
```

### 4 — Install Angular deps (first time)

```powershell
cd C:\projects\SERIOPlusApp
if (-not (Test-Path .npmrc)) { Copy-Item .npmrc.example .npmrc }
npm install
```

### 5 — Start data layer (9 terminals — data first, gateway last)

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
```powershell
# Gateway last — business layer connects to this
cd C:\projects\SERIOPlusDataServices\local-gateway-service
java -jar target\local-gateway-service.jar --spring.profiles.active=local
```

### 6 — Start business layer (7 terminals, after gateway :8070 is up)

```powershell
cd C:\projects\SERIOPlusServices\serioplus-general-admin-service
java -jar target\serioplus-general-admin-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-user-option-service
java -jar target\serioplus-user-option-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-aiml-services
java -jar target\serioplus-aiml-services.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-workflow-service
java -jar target\serioplus-workflow-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-notice-service
java -jar target\serioplus-notice-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-screening-service
java -jar target\serioplus-screening-service.jar --spring.profiles.active=local
```
```powershell
cd C:\projects\SERIOPlusServices\serioplus-filer-eval-service
java -jar target\serioplus-filer-eval-service.jar --spring.profiles.active=local
```

### 7 — Start Angular UI

```powershell
cd C:\projects\SERIOPlusApp
npm start
# → http://localhost:4201/serioplus/#/?acceptBanner=true
```

---

## Port map

| Port | Service | Tier |
|------|---------|------|
| **4201** | SERIOPlusApp (ng serve) | UI |
| **8070** | local-gateway-service | Data gateway |
| 8080 | serioplus-general-admin-service | Business |
| 8081 | serioplus-user-option-service | Business |
| 8082 | serioplus-aiml-services | Business |
| 8083 | serioplus-workflow-service | Business |
| 8084 | serioplus-notice-service | Business |
| 8085 | serioplus-screening-service | Business |
| 8086 | serioplus-filer-eval-service | Business |
| 8090 | serioplus-entry-data-service | Data |
| 8091 | serioplus-lookup-data-service | Data |
| 8092 | serioplus-user-org-data-service | Data |
| 8093 | serioplus-work-data-service | Data |
| 8094 | serioplus-application-service | Data |
| 8095 | serioplus-document-service | Data |
| 8096 | serioplus-screening-data-service | Data |
| 8097 | serioplus-filer-eval-data-service | Data |

---

## Check all ports at once

```powershell
4201,8070,8080,8081,8082,8083,8084,8085,8086,8090,8091,8092,8093,8094,8095,8096,8097 | ForEach-Object {
    $up = $false
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$_); $c.Close(); $up=$true } catch {}
    [pscustomobject]@{ Port=$_; Up=$up }
} | Format-Table
```

---

## Stop all services

```powershell
# Via SerioPlusStack (if started with it):
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop

# Nuclear option — kill all java.exe processes:
Get-Process -Name java -EA 0 | Stop-Process -Force
```

---

## Related runbooks

| Runbook | What |
|---------|------|
| `RUNBOOK-serioplus-common-lib.md` | Common lib build detail |
| `RUNBOOK-serioplus-data-services.md` | Data tier detail + troubleshooting |
| `RUNBOOK-serioplus-business-services.md` | Business tier detail |
| `RUNBOOK-serioplus-app.md` | Angular UI detail |
| `RUNBOOK-serio-monolith.md` | SERIO monolith (separate stack) |
