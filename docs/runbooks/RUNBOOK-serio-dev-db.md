# Runbook — SERIO dev / test database connection

**What this is:** how to connect to the SERIO **Oracle** database in the Dev and Test environments,
and how those connections map to what the application uses.

**Tracked as:** FS-012.

> **Password rule.** The DB password is **not** in this repo and must never be. It lives in KeePass
> (see [Credentials](#credentials)). Everything else here — hosts, ports, service names, the
> username — is connection metadata, fine in this private repo. Never make `fda-serio` public.

**Where this works:** on the FDA network (FDA laptop, full tunnel up). The `*.fda.gov` DB hosts only
resolve on the tunnel.

---

## Environments

| Environment | Host : Port | Oracle service name | Username |
|---|---|---|---|
| **Dev** | `gi-22040-22041.fda.gov:1523` | `ORAD1T23` | `oasis_er` |
| **Test** | `gi-27042-27043.fda.gov:1523` | `ORAT1T23` | `oasis_er` |

- Oracle listens on **1523** here (not the default 1521).
- Schema owner is **`OASIS`**; `oasis_er` is the connect account you were given (same user/password
  for Dev and Test).
- Connect by **service name**, not SID.

## JDBC URLs

```
Dev :  jdbc:oracle:thin:@//gi-22040-22041.fda.gov:1523/ORAD1T23
Test:  jdbc:oracle:thin:@//gi-27042-27043.fda.gov:1523/ORAT1T23
```

Driver: `oracle.jdbc.OracleDriver` (Oracle thin). The `@//host:port/service` form uses the service
name — the leading `//` matters.

## Credentials

The password is in the **automation KeePass** (`automation-keys.kdbx`, in Google Drive under *Keys*),
**not in this repo.** The same login works for both environments.

- **Entry:** `Database/SERIO Oracle DB (oasis_er) Dev-Test`  ·  **User:** `oasis_er`

Retrieve it non-interactively (see the aitools `keepass-integration` skill / CLAUDE.md):

```powershell
$cli = "C:\Program Files\KeePassXC\keepassxc-cli.exe"
$kf  = "C:\Users\adourish\.keepass\automation-keys.keyfile"
$db  = "G:\My Drive\Areas\Keys\automation-keys.kdbx"
& $cli show --key-file $kf --no-password -a Password $db "Database/SERIO Oracle DB (oasis_er) Dev-Test"
```

Or open `automation-keys.kdbx` in the KeePassXC GUI with that key file (no master password).

> **On the FDA box there is no Google Drive**, so the vault doesn't sync there. Copy both files
> into a local **`C:\keys`** folder (`C:\keys\automation-keys.kdbx` + `C:\keys\automation-keys.keyfile`)
> and point `--key-file` / the db path at those, e.g.
> `keepassxc-cli show --key-file C:\keys\automation-keys.keyfile --no-password C:\keys\automation-keys.kdbx "<entry>"`.
> Install KeePassXC itself from the workstation bundle: `Install-DevWorkstation.ps1 -Only keepassxc`.

> This password was shared over chat when it was first provided, so treat it as exposed — rotate it
> with the DBA when convenient and update the KeePass entry (`keepassxc-cli edit … --password`).

---

## Connecting with SQL Developer

SQL Developer is installed by the [workstation setup](RUNBOOK-dev-workstation-setup.md). New
connection:

1. **New Connection** (green `+`).
2. Name: `SERIO Dev`.
3. Username: `oasis_er`; Password: *(from KeePass)*. Tick **Save Password** only if local policy
   allows.
4. Connection type: **Basic**. Hostname: `gi-22040-22041.fda.gov`. Port: `1523`.
5. Choose **Service name** (not SID) and enter `ORAD1T23`.
6. **Test** → should say *Success* → **Connect**.

For Test, repeat with `gi-27042-27043.fda.gov` / `ORAT1T23`.

## Connecting with SQL*Plus

```powershell
sqlplus oasis_er@"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=gi-22040-22041.fda.gov)(PORT=1523))(CONNECT_DATA=(SERVICE_NAME=ORAD1T23)))"
# it prompts for the password - paste it from KeePass rather than putting it on the command line
```

Or add a `tnsnames.ora` alias:

```
SERIO_DEV =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = gi-22040-22041.fda.gov)(PORT = 1523))
    (CONNECT_DATA = (SERVICE_NAME = ORAD1T23)))

SERIO_TEST =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = gi-27042-27043.fda.gov)(PORT = 1523))
    (CONNECT_DATA = (SERVICE_NAME = ORAT1T23)))
```

then `sqlplus oasis_er@SERIO_DEV`.

---

## How SERIO itself uses the DB

The application does **not** read a JDBC URL or password from a file — it reaches Oracle only
through three **WebLogic JNDI datasources**, chosen at runtime by a Spring `AbstractRoutingDataSource`
(`DataSourceRouter`), wired in `serio-ws-war/.../WEB-INF/applicationContext.xml`:

| JNDI name | Role |
|---|---|
| `jdbc.SerioDS` | operational / default |
| `jdbc.SerioRptDS` | reporting |
| `jdbc.SerioMovDS` | mover |

So to point a locally-deployed SERIO at this dev DB, you create those three datasources in the
target WebLogic domain (via the WLS console, or the external `deploy_serio.yml` Ansible playbook)
with the Dev JDBC URL and the `oasis_er` login above. The app never sees the password directly —
WebLogic holds it.

Schema is **script-managed** by the hand-maintained Oracle scripts under `Database/` (no
Liquibase/Flyway); a DBA applies them. See the [build runbook](RUNBOOK-build-serio.md) (FS-011) and
the FS-012 handoff for the schema-version details.

---

## Login / user lookup (how SERIO decides who you are)

SERIO has no login form. It resolves your **username -> email via LDAP**, then finds your profile by
**email** in the OASIS DB. The auth query (from `FdaUserRepository`) joins two tables:

```sql
FROM FdaPersonnel f JOIN UserProfile up ON f.prsnId = up.prsnId
WHERE lower(f.emailAdrs) LIKE :email%
```

- Tables: **`FDA_PERSONNEL`** (email column `EMAIL_ADRS`) and **`USER_PROFILES`** (`ORACLE_USER_NAME`,
  joined on `PRSN_ID`). They live in the **`SHARED`** schema and resolve for `oasis_er` through
  **synonyms** — query them **unqualified** (prefixing `OASIS.` gives `ORA-00942`).
- A **`401 "An OASIS user profile was not found."`** means the whole stack works but your email has no
  matching `FDA_PERSONNEL` + `USER_PROFILES` rows — i.e. **your account isn't provisioned** in that
  environment. Fix: a DBA creates the rows for Dev/Test (request via the SERIO lead → DBA; see
  `SERIO-TEAM-CONTACTS.md`). Verify:
  ```sql
  SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
  FROM FDA_PERSONNEL p LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
  WHERE LOWER(p.EMAIL_ADRS) LIKE 'first.last%';
  ```

**JPA entity package convention** (from the guide, 2.1.6): generated entities are packaged
`gov.fda.ora.si.serio.entity.<schema>` — `...entity.oasis`, `...entity.shared`, `...entity.predict`
(for `oasis_predict`). The four schemas involved are `OASIS`, `SHARED`, `PREDICT_READ`, `OASIS_PREDICT`.

## Dump the schema (so the assistant can see it)

The assistant can't reach the DB. To give it visibility, dump the **structure only** (no data) and
commit it. On the FDA laptop, tunnel up:

```powershell
tools\db\Export-SerioSchema.ps1            # dev (default); -Env test for test
```

**First, install the CLI once** (so you don't need the SQL Developer spool step) — SQLcl is in the
workstation installer and downloads with no Oracle sign-in:

```powershell
tools\install\Install-DevWorkstation.ps1 -Only sqlcl    # unzips SQLcl, adds it to PATH
```

Then the dump is one command. For the password it uses, in order: `-PromptPassword`, then
`$env:SERIO_DB_PASSWORD`, then the automation KeePass (REI laptop only), else it prompts. **On the
FDA laptop there is no KeePass vault, so it just prompts** (or set `$env:SERIO_DB_PASSWORD` once to
skip the prompt). It runs [`tools/db/serio-schema-dump.sql`](../../tools/db/serio-schema-dump.sql)
(tables, columns, primary/unique keys, foreign-key relationships, indexes, views, sequences — all
from Oracle's `ALL_*` dictionary, **never the application rows**), and writes `logs/serio-schema-<env>-<stamp>.txt`.
Commit + push that file and the assistant can read it.

**No command-line Oracle client?** SQL Developer's GUI isn't one, so the script will stop and tell
you to use SQL Developer instead. In a worksheet on the SERIO Dev connection, paste these 3 lines
and press **F5 (Run Script — not F9)**:

```sql
SPOOL "C:\projects\fda-serio\logs\serio-schema-dev.txt"
@C:\projects\fda-serio\tools\db\serio-schema-dump.sql
SPOOL OFF
```

The `@` line runs the committed dump file (no editing needed). Then commit + push the `.txt`.

## Verify quickly

Once connected (SQL Developer or SQL*Plus):

```sql
select sys_context('USERENV','DB_NAME')      as db_name,
       sys_context('USERENV','SERVICE_NAME') as service,
       user                                  as connected_as
from dual;
-- expect service ORAD1T23 (Dev) / ORAT1T23 (Test), connected_as OASIS_ER
select count(*) from all_tables where owner = 'OASIS';   -- the SERIO schema
```

---

## Verification status

**Unverified — single-source.** These endpoints and the login were supplied on 2026-07-15 and have
**not** been connected to yet (needs the FDA laptop on the tunnel, and the password from KeePass).
Update this runbook after the first successful connection with anything that differs.
