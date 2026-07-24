# RUNBOOK — SERIOPlusServices (business layer)

Build and run the SERIO+ business-layer services locally.
**7 Spring Boot services.** Ports: `:8080–8086`.

> **Start the data layer first.** These services call the gateway at `localhost:8070`.
> See `RUNBOOK-serioplus-data-services.md`.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus for builds |
| **JDK 17** | `java -version` → `17.x` — **NOT 21** |
| Maven on PATH | `mvn -version` |
| common-lib SNAPSHOT installed | `RUNBOOK-serioplus-data-services.md` Step 2 |
| **Data layer gateway up** (:8070) | `Test-NetConnection localhost -Port 8070 -InformationLevel Quiet` |

---

## Step 1 — Set JDK 17 (every terminal session)

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
java -version   # must say 17.x
```

---

## Step 2 — Build business services

```powershell
# Full reactor (all 7 services)
cd C:\projects\SERIOPlusServices
mvn -DskipTests -nsu clean install

# OR single service
cd C:\projects\SERIOPlusServices
mvn -DskipTests -nsu -pl serioplus-workflow-service clean install
mvn -DskipTests -nsu -pl serioplus-general-admin-service clean install
```

---

## Step 3 — Start services (each in its own terminal)

Run the JDK 17 env block in each terminal first, then:

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

---

## Alternative — SerioPlusStack.ps1 (headless, all at once)

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only services
# Logs → C:\projects\.serioplus-stack\<service-name>.log
```

---

## Verify ports are up

```powershell
8080,8081,8082,8083,8084,8085,8086 | ForEach-Object {
    $up = $false
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$_); $c.Close(); $up=$true } catch {}
    [pscustomobject]@{ Port=$_; Up=$up }
} | Format-Table
```

---

## Stop a service

```powershell
# Kill by service name
Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
  Where-Object { $_.CommandLine -like '*serioplus-workflow-service*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# Stop everything tracked by SerioPlusStack
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop
```

---

## Port reference

| Port | Service | Purpose |
|------|---------|---------|
| :8080 | `serioplus-general-admin-service` | Core / admin orchestration |
| :8081 | `serioplus-user-option-service` | User preferences |
| :8082 | `serioplus-aiml-services` | AI/ML integration |
| :8083 | `serioplus-workflow-service` | SZR / workflow logic |
| :8084 | `serioplus-notice-service` | Notices |
| :8085 | `serioplus-screening-service` | Screening business logic |
| :8086 | `serioplus-filer-eval-service` | Filer evaluation |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Service fails to connect at startup | Data gateway :8070 not up | Start data tier first |
| `Lombok NoSuchFieldError` | JDK 21 | Switch to JDK 17 |
| `403 Forbidden` | `AccessFilter` — path not whitelisted | Add to `noUserApis`, rebuild |
| `AWS credentials not available` | Wrong Spring profile | Use `--spring.profiles.active=local` |
| `Port 808x already in use` | Old instance running | Kill by command line |
| `Cannot delete … .jar` during `mvn clean` | Jar locked | Kill java process first |

---

## Related

- `RUNBOOK-serioplus-data-services.md` — start the data tier before this
- `RUNBOOK-serioplus-app.md` — Angular UI (top of stack)
- `skills/serioplus-business-services/SKILL.md` — skill reference
- `tools/serioplus/SerioPlusStack.ps1` — full-stack orchestration
