# RUNBOOK — SERIOPlusCommonLibraries (shared JAR)

Install `serioplus-common-library:13.0.0-SNAPSHOT` into your local Maven repository.
**Always do this first** before building any SERIO+ data or business service.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus reachable |
| **JDK 17** | `java -version` → `17.x` — **NOT 21** |
| Maven on PATH | `mvn -version` |

---

## Step 1 — Set JDK 17

```powershell
$env:JAVA_HOME='C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
java -version   # must say 17.x
```

---

## Step 2 — Build and install

```powershell
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn -DskipTests clean install
```

> The `pom.xml` already has `<revision>13.0.0-SNAPSHOT</revision>` — plain `mvn install` installs the correct coordinate.

---

## Step 3 — Verify the JAR is installed

```powershell
$jar = "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library\13.0.0-SNAPSHOT\serioplus-common-library-13.0.0-SNAPSHOT.jar"
Test-Path $jar   # must be True

# Verify a specific class is inside (e.g. after adding a new DTO)
jar tf $jar | Select-String 'SeizureMemo'
```

---

## Purge a stale snapshot (if services still can't see your class)

```powershell
# 1. Remove the cached snapshot
Remove-Item -Recurse -Force "$env:USERPROFILE\.m2\repository\gov\fda\oii\si\serioplus\serioplus-common-library"

# 2. Reinstall
cd C:\projects\SERIOPlusCommonLibraries\serioplus-common-library
mvn -DskipTests clean install

# 3. Rebuild the service using -nsu (no snapshot updates — forces use of local)
cd C:\projects\SERIOPlusDataServices
mvn -DskipTests -nsu -pl serioplus-document-service clean install
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `package …dto… does not exist` in a service build | Stale/wrong snapshot in `.m2` | Purge + reinstall + `-nsu` |
| `Lombok NoSuchFieldError: JCImport.qualid` | JDK 21 | Switch to JDK 17 |
| Nexus 401 during build | VPN down or settings.xml wrong | Full-tunnel VPN; check `~/.m2/settings.xml` |
| Class not found after install | Build output has compile error | Check `mvn` output for errors before proceeding |

---

## Related

- `RUNBOOK-serioplus-data-services.md` — build data services after this
- `RUNBOOK-serioplus-business-services.md` — build business services after this
- `skills/serioplus-common-lib/SKILL.md` — skill reference
