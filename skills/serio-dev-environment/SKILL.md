---
name: serio-dev-environment
description: Set up the SERIO (WebLogic monolith) developer environment on the FDA laptop — Maven, JDK, WebLogic 14.1.2, Eclipse, and the Angular front end. Use when standing up a fresh SERIO dev box, or when a build/deploy step fails on version or environment-variable gotchas. This is the classic SERIO app (serioWeb + serioNg on WebLogic), NOT the SERIO+ Spring Boot microservices.
metadata:
  version: "1.0.0"
  repository: fda-serio
  last_updated: "2026-07-17"
  type: reference
---

# SERIO dev environment (WebLogic monolith)

**Everything needed to build and run the classic SERIO app locally: the Java server tier (Maven +
JDK 21 + WebLogic 14.1.2) and the Angular front end (Node + Angular CLI).** Distilled from the
official **SERIO Developer Guide** (`temp/SERIO Developer Guide_Weblogic14c_05012026.docx`, dated
2026-05-01). This skill is the map; the runbooks carry the click-by-click detail.

> **Not the same app as SERIO+.** This is the WebLogic-hosted SERIO (`serioWeb` API + `serioNg`
> Angular). The **SERIO+** microservices are a separate stack on **JDK 17** — see
> [`serioplus-local-run`](../serioplus-local-run/SKILL.md). Don't cross the JDK versions.

> Deep-detail runbooks: [`RUNBOOK-dev-workstation-setup.md`](../../docs/runbooks/RUNBOOK-dev-workstation-setup.md),
> [`RUNBOOK-serio-weblogic-setup.md`](../../docs/runbooks/RUNBOOK-serio-weblogic-setup.md),
> [`RUNBOOK-build-serio.md`](../../docs/runbooks/RUNBOOK-build-serio.md),
> [`RUNBOOK-run-serio.md`](../../docs/runbooks/RUNBOOK-run-serio.md).

---

## Quick reference

**Use when:** setting up a SERIO dev box, or a build/deploy step trips on versions or env vars.
**Prereqs:** FDA GFE laptop, full-tunnel VPN up (for `git.fda.gov` and the Oracle DB), and
**temporary local admin rights** (request these first — WebLogic and Eclipse installs need them).
**Source:** `git@git.fda.gov:FDA/ORA/SI/SERIO.git` (see the internal-cert runbook if the clone fails
with a self-signed-certificate error).

### The stack at a glance

| Piece | Version | Install dir | Env var |
|-------|---------|-------------|---------|
| Maven | **3.2.5** | `C:\sA\Apps\Maven\apache-maven-3.2.5` | `MVN_HOME` → install dir; copy `settings.xml` into `~/.m2` |
| JDK | **21** (`jdk21.0.11`) | `C:\FDA\Apps\Java\jdk21.0.11` | `JAVA_HOME` → install dir; add `…\bin` to `PATH`, then reboot |
| WebLogic | **14.1.2.0.0** | `C:\FDA\AppServer\Oracle_Home_14120` | Oracle Home (set during install) |
| Eclipse | JEE | `C:\FDA\Apps\eclipse\…` | workspace `C:\FDA\workspace\…` |
| Node.js | 12.20.2 (per guide) | `C:\FDA\Apps\Node.js` | add npm global dir to `PATH` |
| Angular CLI | 6 (per guide) | `npm install -g @angular/cli` | — |

**Automation:** the WebLogic install + domain creation are scripted —
[`tools/serio/Install-SerioWebLogic.ps1`](../../tools/serio/Install-SerioWebLogic.ps1) and
[`tools/serio/New-SerioDomain.ps1`](../../tools/serio/New-SerioDomain.ps1). Prefer these over clicking
through the installer; the runbook explains what they do.

---

## Server tier — the key steps

1. **Maven 3.2.5.** Set `MVN_HOME`; copy the guide's `settings.xml` into your `~/.m2` folder (create
   `.m2` if missing).
2. **JDK 21.** Extract under `C:\FDA\Apps\Java\`, set `JAVA_HOME` + `PATH`, **reboot** so the vars take.
3. **WebLogic 14.1.2.** Install `fmw_14.1.2.0.0_wls.jar` into Oracle Home
   `C:\FDA\AppServer\Oracle_Home_14120` (`java -jar fmw_14.1.2.0.0_wls.jar`).
4. **Create the `serio` domain** with `Oracle_Home_14120\oracle_common\common\bin\config.cmd`:
   - domain location `…\user_projects\domains\serio`
   - admin account **`weblogic` / `weblogic14c`**, Development mode, point it at your JDK
   - afterwards copy **`DemoIdentity.jks`** into `…\domains\serio\security` if it isn't there.
5. **Admin via the WebLogic Remote Console.** In 14.1.2 the old browser admin console is **removed** —
   administration is done through the separate **WebLogic Remote Console** app. Create a connection to
   the local AdminServer and connect.
6. **Data source + local user.** Create the `SerioDS` GridLink data source (Oracle thin, service
   `ORAD1T23`, user `oasis_er` — password from the DBA/lead, **never** committed) and add a local
   WebLogic realm user (`first.last` / `Welcome1`) to log into SERIO locally.
7. **Build & deploy** (full detail in `RUNBOOK-build-serio.md`):
   ```
   mvn clean install -pl serio-ws-ear,serio-ws-war -DskipTests -P developer
   ```
   The `developer` profile builds and auto-deploys to your local WebLogic domain. Start the server and
   open <http://localhost:7001/serio>.

## Front end — the Angular app (`serioNg` / `serio-app-war`)

- Install Node.js + Angular CLI (`npm install -g @angular/cli`), then in `serioNg` run `npm install`
  (do **not** commit `node_modules`).
- **Full local build/deploy:** set `local.domain` / `local.apiUrl` in `serio-app-war/build.properties`,
  then `mvn clean install -P developer` deploys to your domain; app at <http://localhost:7001/serio>.
- **Fast front-end loop (no WebLogic redeploy):** fill in `serio-app-war/src/ngServeAppConfig/env.js`
  (`localUsername`, `localPassword`, `apiUrl` = your local WS, e.g.
  `http://localhost:7001/serio/ws/api`), `npm install --unsafe-perm`, then **`ng serve`**. App at
  <http://localhost:4200>. See [`RUNBOOK-run-serio.md`](../../docs/runbooks/RUNBOOK-run-serio.md).
- **SERIO Mobile** (NativeScript) is a separate, mostly **Mac/iOS** track (Xcode, `tns run ios`) —
  covered in the guide's §3 if you ever need it; not part of the Windows dev box.

---

## Gotchas (each costs real time)

- **`config.cmd` says "Files was unexpected at this time."** → your `PATH` contains **quotes**. Remove
  every `"` from `PATH` and rerun. (Classic `C:\Program Files` quoting problem.)
- **Wrong JDK.** SERIO here wants **JDK 21**; SERIO+ microservices want **JDK 17**. Mixing them causes
  build failures — check `mvn -version` / `java -version` in the shell you're building in.
- **`git.fda.gov` clone fails "self-signed certificate in certificate chain."** → the FDA internal CA
  isn't trusted yet. Fix per
  [`RUNBOOK-internal-git-cert.md`](../../docs/runbooks/RUNBOOK-internal-git-cert.md) (FS-009). Also:
  internal `*.fda.gov` hosts only resolve with the **full tunnel up**.
- **Admin console 404 / can't find it.** There isn't one in 14.1.2 — use the **WebLogic Remote
  Console** app instead.
- **DB password / secrets.** The `oasis_er` password lives in the automation KeePass
  (`Database/SERIO Oracle DB (oasis_er) Dev-Test`), never in a tracked file. Same for any PAT/token.
- **Admin rights are per-install.** Request temporary local admin before the WebLogic and Eclipse
  installs; they won't complete without it.
