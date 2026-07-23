---
name: serioplus-local-run
description: Build and run a SERIO+ Spring Boot service locally on the FDA laptop, and get past the pre-existing gotchas that block it. Use when building/running any SERIOPlusServices or SERIOPlusDataServices module, or debugging why one won't start. Covers JDK 17, the common-lib SNAPSHOT coordinate, the local profile, Oracle/tunnel, the AccessFilter auth gate, and the rebuild discipline.
metadata:
  version: "1.0.0"
  repository: fda-serio
  last_updated: "2026-07-17"
  type: reference
---

# SERIO+ — build & run a service locally

**Get a single SERIO+ Spring Boot microservice building and running on the FDA laptop, fast, without rediscovering the same traps.** Learned end-to-end on 2026-07-16/17 running `serioplus-document-service`.

> Companion: [`docs/runbooks/RUNBOOK-build-run-serioplus.md`](../../docs/runbooks/RUNBOOK-build-run-serioplus.md) (topology + stack script), [`docs/SERIO-APP-WALKTHROUGH.md`](../../docs/SERIO-APP-WALKTHROUGH.md) (how it all fits).

---

## Quick reference

**Use when:** building/running `SERIOPlusServices` or `SERIOPlusDataServices` locally, or a service won't start.
**Prereqs:** FDA laptop, **full-tunnel VPN up** (Nexus + Oracle), **JDK 17**.
**Repos:** `SERIOPlusCommonLibraries` (shared JAR), `SERIOPlusDataServices` (data tier :8090-97 + gateway :8070), `SERIOPlusServices` (business tier :8080-86).

### The happy path (one service)
```powershell
# JDK 17 in the shell (NOT 21+)
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'; $env:Path="$env:JAVA_HOME\bin;$env:Path"

# 1. common lib -> local .m2 AS 13.0.0-SNAPSHOT (services depend on the snapshot)
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library      # NB: pom is in this subfolder
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install

# 2. build the service against the local snapshot
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu -pl serioplus-document-service clean install

# 3. run it WITHOUT AWS (local profile) — in its own window
java -jar ".\serioplus-document-service\target\serioplus-document-service.jar" --spring.profiles.active=local
```

---

## The gotcha catalog (each one cost real time)

1. **Use JDK 17, never 21+.** Building on JDK 21 dies with Lombok
   `NoSuchFieldError: … JCTree$JCImport … qualid`. The project's Lombok reaches into javac internals removed in 21. Set `JAVA_HOME` to a 17 (`mvn -version` must say 17).

2. **common-lib version coordinate.** The lib builds as `${revision}` = **`13.0.0`**, but every service depends on **`13.0.0-SNAPSHOT`**. Install it under the snapshot coordinate or services compile against a *stale* snapshot and you get `package …dto… does not exist`.
   - **PowerShell mangles `-Drevision=13.0.0-SNAPSHOT`** (splits it → builds `13`, "Unknown lifecycle phase .0.0-SNAPSHOT"). **Quote it**: `mvn '-Drevision=13.0.0-SNAPSHOT' …`. If quoting still fails, edit the pom directly: `<revision>13.0.0-SNAPSHOT</revision>` then plain `mvn install` (revert with `git checkout -- pom.xml`).
   - If a service still can't see your new class, **purge the stale snapshot and reinstall**:
     ```powershell
     Remove-Item -Recurse -Force "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library"
     ```
   - **Verify** the installed jar actually has your class before rebuilding the service:
     ```powershell
     jar tf "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library\13.0.0-SNAPSHOT\serioplus-common-library-13.0.0-SNAPSHOT.jar" | Select-String 'YourClass'
     ```

3. **Build services with `-nsu`** (`--no-snapshot-updates`) so Maven uses your freshly-installed local snapshot instead of re-pulling the older one from Nexus.

4. **Run one service without AWS:** launch the jar with **`--spring.profiles.active=local`**. Under the default `server` profile, `AwsSsmToPropertyFileWriter` loads all config from AWS SSM Parameter Store and aborts with *"AWS credentials not available."* `local` reads classpath `*.properties` instead. (The `SerioPlusStack.ps1` script uses `server`, so for a single AWS-less service, run the jar directly.)

5. **Oracle needs the tunnel.** `DataSourceWarmer` opens Hikari pools (OPR/RPT/AWS) against the dev DB (`ORAD1T23` as `oasis_er`, `ORAD2T12` as `er_rpt`). No tunnel → boot fails at datasource init. (FS-012.)

6. **The `AccessFilter` auth gate (403).** Every request passes `AccessFilter` (from common-lib). Non-`OPTIONS` paths need a decoded **User-Token** header, *unless* the path is in that service's **`noUserApis` whitelist** (in its `FilterConfig`). For a body-driven endpoint that doesn't use the user, add its `/api/...` path to `noUserApis` — same as `/api/generate-oga-status-report`. You do **not** need a real token for those (and getting one needs a provisioned OASIS user anyway).

7. **Rebuild discipline — `java -jar` LOCKS the jar.** `mvn clean` then fails with *"Failed to delete …jar"*, silently leaving the OLD jar in place. **Kill the running instance by command line (not by port — the port query can miss it) before every rebuild:**
   ```powershell
   Get-CimInstance Win32_Process -Filter "Name='java.exe'" | ? { $_.CommandLine -like '*serioplus-document-service*' } | % { Stop-Process -Id $_.ProcessId -Force }
   ```
   Discipline: **stop → build → run**, and confirm 0 remaining before `mvn`.

8. **Prove the running jar has your change** (don't trust that a rebuild happened):
   ```powershell
   jar xf "<jar>" BOOT-INF/classes/<pkg>/YourClass.class   # extract, then:
   Select-String -Path .\BOOT-INF\classes\<pkg>\YourClass.class -Pattern 'your-string' -Quiet
   ```

9. **iText licensing POM warning is harmless.** `com.itextpdf.licensing:licensing-root:4.0.6.pom` in `.m2` can be an HTML 404 page (*"Non-parseable POM … <!DOCTYPE html>"*) — a **warning only**; the JARs resolve and compilation proceeds.

10. **iText license path is hardcoded Unix.** `ITextLicenseService` looks for `C:/u07/wls_12214/serio/config/itext-*_license.json`, which doesn't exist on Windows → PDF endpoints return **500 "iText license validation failed."** That's the last runtime gate; point it at real license files (or the license property) to get an actual PDF.

11. **`document-service` pre-existing local-run bugs** (on `dev`, unrelated to any feature): a swallowed `docInfo` declaration in `DocumentManagementController.java`, and `SerioImportsInvestigationDocument` missing from `persistence.xml`. Idempotent fixer: [`handoff/serio-39310/Fix-LocalRun.ps1`](../../handoff/serio-39310/Fix-LocalRun.ps1).

---

## Diagnosing a running service

| Symptom | Meaning | Do |
|---|---|---|
| `403 Forbidden` | `AccessFilter` — path not whitelisted, no token | add path to `noUserApis`, **rebuild** |
| `404 "No static resource api/…"` | no controller mapped → your controller isn't in the jar | you built a tree missing the scaffold / stale jar — rebuild with the files present |
| `Port 8095 already in use` | old instance still running | kill by command line, relaunch |
| `AWS credentials not available` | `server` profile | use `--spring.profiles.active=local` |
| `No [ManagedType] … <Entity>` | entity not in `persistence.xml` (it's in the common-lib jar, so auto-scan misses it) | add `<class>…</class>` |
| `package …dto… does not exist` | the resolved common-lib snapshot lacks your class | reinstall common-lib as SNAPSHOT + verify jar + `-nsu` |
| first PDF call hangs ~30-60s | iText scanning OS fonts (`DefaultFontProvider(…, true)`) | use bundled `/templates/fonts/Arial-*.ttf` instead |

---

## Verify your OASIS user (the 401 that isn't a bug)
Both stacks match you by email; unprovisioned = `401 "An OASIS user profile was not found."` everywhere. Query **unqualified** (SHARED schema via `oasis_er` synonyms):
```sql
SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
FROM FDA_PERSONNEL p LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
WHERE LOWER(p.EMAIL_ADRS) LIKE 'first.last%';
```
