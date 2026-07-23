---
name: serioplus-common-lib
description: Build and install the SERIOPlusCommonLibraries shared JAR (serioplus-common-library:13.0.0-SNAPSHOT) into the local Maven repository. This is always step 1 before building any SERIO+ service — every data and business service depends on this SNAPSHOT. Covers the version-coordinate gotcha, quoting in PowerShell, and how to verify the jar contains your class.
metadata:
  version: "1.0.0"
  runtime: powershell
  repo: SERIOPlusCommonLibraries
  artifact: "gov.fda.oii.serioplus:serioplus-common-library:13.0.0-SNAPSHOT"
---

# Skill: serioplus-common-lib

Build and install the **SERIOPlusCommonLibraries** shared JAR into the local Maven repository.

## What this is

`serioplus-common-library` is the shared Maven JAR (`gov.fda.oii.serioplus:serioplus-common-library`)
containing shared DTOs, entities, JWT/util classes, and configuration consumed by every SERIO+
Spring Boot service. **Build this first** before building any data or business service.

## The version coordinate gotcha (read before you build)

The `pom.xml` defaults `<revision>` to `13.0.0` (no SNAPSHOT). But **every service declares a
dependency on `13.0.0-SNAPSHOT`**. If you install under `13.0.0`, services resolve the stale
snapshot from Nexus (which may not have your changes) and you get `package …dto… does not exist`.

**Always install under the SNAPSHOT coordinate:**

```powershell
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install
```

> ⚠️ **Quote the `-Drevision` argument in PowerShell.** Without quotes, PowerShell splits on `=`
> and passes `-Drevision` and `13.0.0-SNAPSHOT` as separate args — Maven sees version `13` and
> lifecycle phase `.0.0-SNAPSHOT` and dies.

## Build

```powershell
# 1. Set JDK 17 (required — Lombok breaks on 21+)
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
java -version   # must say 17.x

# 2. Build from the subfolder (pom.xml is in serioplus-common-library/, not the repo root)
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install
```

### Via SerioPlusStack.ps1

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action build -Only common-lib
```

## Verify the jar has your class

```powershell
$jar = "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library\13.0.0-SNAPSHOT\serioplus-common-library-13.0.0-SNAPSHOT.jar"
jar tf $jar | Select-String 'SeizureMemo'    # or your class name
```

If your class isn't listed, the install didn't pick it up — check for compile errors in the build output.

## Purge a stale snapshot

If a service still can't resolve your new class after reinstalling:

```powershell
# 1. Purge from local .m2
Remove-Item -Recurse -Force "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library"

# 2. Reinstall
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn '-Drevision=13.0.0-SNAPSHOT' -DskipTests clean install

# 3. Rebuild the service with -nsu (no snapshot updates — use local)
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu -pl serioplus-document-service clean install
```

## What's in the JAR

Key packages (illustrative — exact contents depend on the branch):
- `gov.fda.oii.serioplus.common.dto.*` — shared DTOs (entry, seizure, OGA, compliance, etc.)
- `gov.fda.oii.serioplus.common.entity.*` — JPA entities
- `gov.fda.oii.serioplus.common.util.*` — JWT helpers, utilities
- `gov.fda.oii.serioplus.common.configuration.*` — `FilterConfig`, `AccessFilter`, common security

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `package …dto… does not exist` | Stale snapshot in .m2 | Purge + reinstall + `-nsu` in service build |
| PowerShell splits `-Drevision` | No quotes | Use `'-Drevision=13.0.0-SNAPSHOT'` (with single quotes) |
| Build fails with Lombok `NoSuchFieldError` | JDK 21 | Switch to JDK 17 |
| Services resolve old class | pom revision mismatch | Always install as `-SNAPSHOT` |

## Related

- `skills/serioplus-data-services/SKILL.md` — builds next, after common-lib
- `skills/serioplus-business-services/SKILL.md` — also depends on this SNAPSHOT
- `tools/serioplus/SerioPlusStack.ps1` — wraps this as the `common-lib` build step
