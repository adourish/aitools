# Skill: db-query

Run an arbitrary SQL query against the **SERIO dev Oracle database**.

- **Dev:** `gi-22040-22041.fda.gov:1523` / service `ORAD1T23`
- **Test:** `gi-27042-27043.fda.gov:1523` / service `ORAT1T23`
- **Schema owner:** `OASIS` (same login for both environments)
- **KeePass entry:** `Database/SERIO Oracle DB (oasis_er) Dev-Test`

> ⚠️ **FDA VPN required.** The Oracle DB hosts are only reachable on the FDA full-tunnel VPN.

## Prerequisites

- Node.js installed
- Dependencies installed (one-time):
  ```powershell
  cd C:\projects\fda-serio\skills\db-query
  npm install
  ```
- KeePass DB + key file (auto-discovered in this order):
  1. Env vars `KEEPASS_DB` / `KEEPASS_KEY`
  2. `C:\keys\automation-keys.kdbx` + `C:\keys\automation-keys.keyfile` (FDA laptop & Shared-AI-Service)
  3. `G:\My Drive\Areas\Keys\automation-keys.kdbx` + `C:\Users\adourish\.keepass\automation-keys.keyfile` (REI laptop)

## Usage

```powershell
node C:\projects\fda-serio\skills\db-query\db-query.js "<SQL>"
```

Returns JSON rows to stdout.

## Examples

```powershell
# Sanity check (requires VPN)
node C:\projects\fda-serio\skills\db-query\db-query.js "SELECT 1 FROM DUAL"

# List tables in the OASIS schema
node C:\projects\fda-serio\skills\db-query\db-query.js "SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME"

# Sample rows from a table
node C:\projects\fda-serio\skills\db-query\db-query.js "SELECT * FROM SERIO_ENTRY FETCH FIRST 5 ROWS ONLY"
```

## Switching to Test environment

The KeePass entry URL points to Dev. To query Test, override the connect string:

```powershell
# In a custom script:
const { runQuery } = require('C:/projects/fda-serio/skills/db-query/db-query.js');
# Or pass a different connectString directly to oracledb.getConnection
```

Or temporarily edit the KeePass entry URL to `gi-27042-27043.fda.gov:1523/ORAT1T23`.

## How it works

1. Reads `UserName`, `Password`, `URL` from the automation KeePass via `keepassxc-cli`.
2. Connects via `oracledb` (node-oracledb).
3. Runs the SQL and prints `result.rows` as JSON.

## Notes

- Credentials are **never** stored in the repo — always pulled live from KeePass.
- KeePass paths are auto-discovered — no env vars needed on the FDA laptop or Shared-AI-Service machine.
- Always run with the full path (`node C:\projects\fda-serio\skills\db-query\db-query.js`) so Node
  finds the `oracledb` module in the skill's `node_modules\`.
- Oracle syntax: use `FETCH FIRST n ROWS ONLY` (not `LIMIT`), `SYSDATE` (not `NOW()`), etc.
- For parameterised queries, use the exported `runQuery(sql, binds)` function from your own script.