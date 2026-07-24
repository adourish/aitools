# RUNBOOK — SERIOPlusApp (Angular UI)

Build and run the SERIO+ Angular 19 frontend locally.
Served at `http://localhost:4201/serioplus/`.

> **Start the business and data layers first** (or use the hosted dev environment).
> See `RUNBOOK-serioplus-business-services.md` and `RUNBOOK-serioplus-data-services.md`.

---

## Hosted environments (no local setup needed)

| Environment | URL |
|-------------|-----|
| **Dev** | `https://oii-cloud.dev.fda.gov/serioplus/#/?acceptBanner=true` |
| **Test** | `https://oii-cloud.test.fda.gov/serioplus/#/?acceptBanner=true` |
| **Pre-prod** | `https://oii-cloud.preprod.fda.gov/serioplus/#/?acceptBanner=true` |

> Dev is unstable during work hours — people merge throughout the day. Use **Test** for reliable verification.
> Sign in first: `https://sso2.fda.gov/idp/startSSO.ping?PartnerSpId=FDA_AWS_GovCloud`

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| FDA laptop, full-tunnel VPN up | Nexus npm registry reachable |
| Node.js (18, 20, or 22) | `node --version` |
| npm | `npm --version` |
| `.npmrc` in `SERIOPlusApp/` | Copy from `.npmrc.example` if missing (one-time) |

---

## Step 1 — Copy .npmrc (one-time)

```powershell
cd C:\projects\SERIOPlusApp
if (-not (Test-Path .npmrc)) { Copy-Item .npmrc.example .npmrc }
```

---

## Step 2 — Install dependencies

```powershell
cd C:\projects\SERIOPlusApp
npm install
```

---

## Step 3 — Start the dev server

```powershell
cd C:\projects\SERIOPlusApp
npm start
```

Open: **`http://localhost:4201/serioplus/#/?acceptBanner=true`**

---

## Alternative — SerioPlusStack.ps1 (headless)

```powershell
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action start -Only app
# Log → C:\projects\.serioplus-stack\app-ngserve.log
```

---

## Stop

```powershell
# In-terminal: Ctrl+C

# If running headless via SerioPlusStack:
C:\projects\aitools\tools\serioplus\SerioPlusStack.ps1 -Action stop

# Find and kill manually:
Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
  Where-Object { $_.CommandLine -like '*ng serve*' -or $_.CommandLine -like '*SERIOPlusApp*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

---

## Verify it's up

```powershell
try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',4201); $c.Close(); 'UP' } catch { 'DOWN' }

# Open in browser
Start-Process 'http://localhost:4201/serioplus/#/?acceptBanner=true'
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `npm install` 401/404 | `.npmrc` missing or VPN down | Copy `.npmrc.example` → `.npmrc`; VPN full-tunnel |
| `EADDRINUSE :4201` | Another `ng serve` running | `Stop-Process -Name node -Force` (or be selective) |
| App loads, API calls fail | Business layer not running | Start data + business tiers first |
| Blank page / can't log in | OASIS user not provisioned | Request from Kaustav Lahiri → Soumen Kundu (DBA) |
| `401 "An OASIS user profile was not found."` | Account not in OASIS dev DB | Same — request provisioning for Dev + Test |

---

## OASIS user provisioning

The app authenticates by matching your email in `FDA_PERSONNEL`. Without a row, you get `401` everywhere. Request provisioning from **Kaustav Lahiri** → **Soumen Kundu (DBA)** for **Dev** and **Test**.

Verify (SQLcl / SQL Developer, connect as `oasis_er`, tunnel up):
```sql
SELECT p.PRSN_ID, p.EMAIL_ADRS, up.ORACLE_USER_NAME
FROM FDA_PERSONNEL p
LEFT JOIN USER_PROFILES up ON up.PRSN_ID = p.PRSN_ID
WHERE LOWER(p.EMAIL_ADRS) LIKE 'anthony.dourish%';
```

---

## Related

- `RUNBOOK-serioplus-business-services.md` — business layer the UI calls
- `RUNBOOK-serioplus-data-services.md` — data layer
- `skills/serioplus-app/SKILL.md` — skill reference
- `tools/serioplus/SerioPlusStack.ps1` — full-stack orchestration
