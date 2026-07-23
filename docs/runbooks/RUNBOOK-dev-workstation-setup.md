# Runbook — FDA SERIO developer workstation setup

**What this is:** how to set up a new developer's Windows machine for the FDA SERIO work — Java,
Node, WebLogic, the two IDEs, SQL Developer and Maven.

**Where the request came from:** FDA Service Portal request **REQ1061439**.

**Scripts:** [`tools/install/`](../../tools/install/)

| File | What it's for |
|---|---|
| `Save-OfflineBundle.ps1` | Downloads every installer into `bundle/`. Run once, on a machine that has internet. |
| `Install-DevWorkstation.ps1` | Installs everything. Uses the bundle if it's there, downloads if it isn't. |
| `software-manifest.psd1` | The list of software. **To add software, edit this — not the scripts.** |
| `bundle-checksums.txt` | A SHA256 for every file in the bundle. Checked before anything is installed. |

**Roughly how long:** about an hour. Most of it is downloading, and you only pay that once if you
keep the bundle. The two Oracle products need a person with an Oracle account.

**Related:** [`RUNBOOK-ai-agent-coding-tools.md`](RUNBOOK-ai-agent-coding-tools.md) — setting up the
VS Code AI plugins against SEMOSS Elsa-Dev, once VS Code is installed.

---

## The short version

```powershell
# Run this FIRST, in the same PowerShell window, or the script is blocked (see below).
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

git clone https://github.com/adourish/fda-serio.git
cd fda-serio
git lfs pull                              # fetches the installers (~1 GB)

cd tools\install
.\Install-DevWorkstation.ps1 -WhatIf      # look before you leap. No admin needed.
.\Install-DevWorkstation.ps1              # for real. Run as Administrator.
```

Then follow [Step 4](#step-4--the-two-oracle-products) for WebLogic and SQL Developer.

> **`... cannot be loaded because running scripts is disabled on this system`?**
> That is Windows' default script block, not a problem with the installer. Run the
> `Set-ExecutionPolicy` line above **first, in the same window**, then run the script again.
> It only affects that one window and changes no machine setting. Full explanation in
> [Step 1](#step-1--open-powershell-as-administrator).

> **`SSL certificate problem: self-signed certificate in certificate chain`** when cloning an
> **internal** FDA repo (e.g. `git.fda.gov`)? That's the FDA's internal certificate authority,
> which your machine may not trust yet. Fix it with one script — see
> [Trust an internal FDA git certificate](RUNBOOK-internal-git-cert.md):
> ```powershell
> cd C:\projects\fda-serio\tools\certs
> .\Import-InternalGitCert.ps1 -HostName git.fda.gov -Install
> ```
> (The public `github.com` clone above is unaffected — this only matters for internal FDA servers.)

---

## Where the files come from

For each piece of software the installer looks in this order:

1. **The offline bundle** — `tools/install/bundle/`
2. **The staging folder** — `C:\DevSetup\staging`
3. **The vendor's website** — downloads it

So on a machine with no internet, you copy the `bundle` folder across (share, USB, whatever) and
the install runs with no network at all. Everything is checked against `bundle-checksums.txt`
before it's installed; a file that doesn't match is **refused, not installed**.

Everything comes straight from the vendor. There is deliberately **no winget**: it can't pin the
versions this request needs (it no longer carries Node 22 at all), and it's often missing or
blocked on a locked-down FDA image.

### The installers are in the repo (Git LFS)

The binaries are **committed**, using **Git LFS**. So the fastest way to set up a new machine is:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # so the script can run
git clone https://github.com/adourish/fda-serio.git
cd fda-serio
git lfs pull                       # fetches the ~1 GB of installers
cd tools\install
.\Install-DevWorkstation.ps1       # as Administrator
```

Two things to know about that:

- **It has to be LFS.** GitHub rejects any single file over 100 MB, and four of these are bigger
  (Eclipse 530 MB, JDK 21 171 MB, JDK 17 161 MB, VS Code 160 MB). LFS keeps a small pointer in the
  repo and the real file outside it, so a plain `git clone` stays fast — you only pull the gigabyte
  if you want it. GitHub's free LFS allowance is 1 GiB of storage and 1 GiB of bandwidth a month,
  and this bundle is 1.04 GiB, so heavy use may need a data pack.
- **This depends on the repo staying private.** Oracle's WebLogic and SQL Developer are licensed to
  the account holder — your own copy is fine, handing it to other people is not. **If this repo is
  ever made public, or shared with anyone outside the Oracle licence, take the Oracle binaries out
  first.** Everything else in the bundle (Temurin, Node, VS Code, Eclipse, Maven) is open-source and
  redistributable.

`bundle-checksums.txt` records a SHA256 for every file, and the installer refuses to install
anything that doesn't match.

---

## Before you start

1. **Administrator rights** — for the install (not for the dry run, and not for the bundle
   download). The script installs for all users and sets machine-wide environment variables.
2. **Internet access**, *or* a bundle folder someone already filled for you.
3. **An Oracle account** (free) for WebLogic and SQL Developer.

---

## Step 1 — Open PowerShell as Administrator

Press Start, type `PowerShell`, right-click **Windows PowerShell**, choose **Run as
administrator**.

If the machine blocks scripts, allow them **for this window only** — this changes no machine
setting permanently:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## Step 2 — Get the installers

Normally there is nothing to do here: the installers are in the repo, so `git lfs pull` (Step 0
above) already fetched them.

You only need this if you're **adding new software** or **refreshing a version**:

```powershell
cd C:\projects\fda-serio\tools\install
.\Save-OfflineBundle.ps1
```

That pulls anything missing from the vendors (~1 GB from scratch, 10–20 minutes) and rewrites
`bundle-checksums.txt`. No admin rights — it only downloads. Files already there are left alone
unless you pass `-Force`.

Then commit the bundle and the checksums; the binaries go up through LFS.

---

## Step 3 — Dry run, then install

A dry run changes nothing, needs no admin rights, and tells you what *would* happen — including
whether any requested version actually exists:

```powershell
.\Install-DevWorkstation.ps1 -WhatIf
```

Then, for real:

```powershell
.\Install-DevWorkstation.ps1
```

| Software | How it's installed |
|---|---|
| Java 17 (Temurin JDK) | `.msi`, silent — `JAVA_HOME` points here |
| Java 21 (Temurin JDK) | `.msi`, silent — sits alongside 17 |
| Node.js 22 | `.msi` from nodejs.org |
| npm 10.9.7 | `npm install -g npm@10.9.7` (needs the network — npm has no offline installer) |
| Visual Studio Code | `.exe`, silent — **pinned to 1.121.0**, see below |
| Eclipse (Enterprise Java) | `.zip`, unzipped to `C:\DevTools` |
| Apache Maven | `.zip`, unzipped to `C:\DevTools` |
| KeePassXC (GUI + CLI) | `.msi`, silent — one package gives both `keepassxc.exe` and `keepassxc-cli.exe` in `C:\Program Files\KeePassXC` (added to `PATH`). The credential tool the runner + runbooks use; the *database* and *key file* are secrets, kept out of the bundle. |
| AWS CLI v2 (`awscli`) | `.msi`, silent — official AWS MSI to `C:\Program Files\Amazon\AWSCLIV2` (adds itself to `PATH`; open a NEW shell). For the GovCloud (`us-gov-west-1`) SERIO AWS accounts — the AI-flow / CV Bedrock work. After install: `aws configure sso` then `aws sts get-caller-identity`. Account/role map: [`serio-aws-environment.md`](../features/serio-aws-environment.md). One-off standalone installer: [`tools/install/Install-AwsCli.ps1`](../../tools/install/Install-AwsCli.ps1). |

It also sets `JAVA_HOME`, `M2_HOME` and `PATH`, prints a summary, and verifies what it did. The log
goes to `C:\DevSetup\staging\install-<date>.log`.

**Safe to run more than once** — anything already installed is reported and left alone.

When it's done, **close the window and open a new one**. A running terminal doesn't pick up `PATH`
changes.

### Why VS Code is pinned to 1.121.0

From VS Code **1.122.0** onward, **Roo Code stops working** — VS Code moved the bundled `ripgrep`
search tool and Roo Code still looks for it on the old path (microsoft/vscode issue 318691). The
FDA Elsa-Dev plugin guide calls this out, and the team is told to use Roo Code / Cline / Continue
against Elsa-Dev. So the installer pins the last version where all three work.

If nobody on your team uses Roo Code, set `Version = $null` for `vscode` in `software-manifest.psd1`
to get the latest instead. One line; no script change. See
[`RUNBOOK-ai-agent-coding-tools.md`](RUNBOOK-ai-agent-coding-tools.md).

### Doing only part of it

```powershell
.\Install-DevWorkstation.ps1 -Only java17,maven      # just these
.\Install-DevWorkstation.ps1 -Skip weblogic          # everything except this
```

Keys: `java17`, `java21`, `node`, `npm`, `vscode`, `eclipse`, `maven`, `weblogic`, `sqldeveloper`.

### What the exit codes mean

| Code | Meaning |
|---|---|
| 0 | Everything the script owns is done. Anything left is a manual Oracle step. |
| 1 | At least one item failed. Read the log. |
| 2 | It couldn't even start — not Administrator, or the manifest is missing. |

---

## Step 4 — The two Oracle products

Oracle requires a signed-in account and a licence click-through before it will release these files.
No script can do that. So: **you download the file, the script installs it.**

### WebLogic

1. Sign in at
   <https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html>
2. Download the **Generic Installer** — `fmw_14.1.1.0.0_wls_lite_generic.jar`.
3. Save it into `tools\install\bundle\`.
4. Run:
   ```powershell
   .\Install-DevWorkstation.ps1 -Only weblogic
   ```

The script writes the response file (the answers the Oracle installer would otherwise stop and ask
for), runs the silent install against **Java 17**, installs to
`C:\DevTools\Oracle\Middleware\Oracle_Home`, and sets `MW_HOME` and `WL_HOME`.

If it fails, Oracle writes its own log under `C:\DevTools\Oracle\oraInventory\logs` — read that
one, not ours.

### SQL Developer

1. Sign in at <https://www.oracle.com/database/sqldeveloper/technologies/download/>
2. Download the **Windows with JDK included** `.zip`.
3. Save it into `tools\install\bundle\`.
4. Run:
   ```powershell
   .\Install-DevWorkstation.ps1 -Only sqldeveloper
   ```

There's no installer to run — SQL Developer is just a folder. It gets unzipped to `C:\DevTools`
with a Start Menu shortcut.

---

## Step 5 — Check it worked

Open a **new** PowerShell window:

```powershell
java -version          # expect 17.x
node --version         # expect v22.x
npm --version          # expect 10.9.7
mvn --version          # expect Apache Maven 3.9.x
```

The script checks these itself, but doing it in a fresh window proves `PATH` is right for a normal
user, not just for the script.

---

## Working with two versions of Java

Both 17 and 21 get installed. `JAVA_HOME` points at **17**, because WebLogic 14.1.x is certified
against Java 17 — that's what the backend needs day to day. Both paths are recorded so you can
switch without hunting for them: `JAVA_HOME_17` and `JAVA_HOME_21`.

**Java 21 in one terminal only** (forgotten when you close the window):

```powershell
$env:JAVA_HOME = $env:JAVA_HOME_21
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
java -version
```

**Java 21 for the whole machine** (needs admin, and it affects WebLogic):

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME', $env:JAVA_HOME_21, 'Machine')
```

---

## Troubleshooting

**"...cannot be loaded because running scripts is disabled on this system."**
See Step 1 — `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

**A command isn't recognised right after installing.**
Your terminal is holding an old copy of `PATH`. Close it, open a new one. This is far and away the
most common "it didn't work" — it almost always did.

**A download fails, or the machine has no internet.**
Run `Save-OfflineBundle.ps1` on a machine that does, copy the `bundle` folder across, and run the
installer again. It prefers the bundle and never touches the network if the file is already there.
(The one exception is npm, which has no offline installer.)

**"DOES NOT MATCH its checksum."**
The file is corrupt, truncated, or not the version we pinned — so it is not installed. Re-fetch it
with `.\Save-OfflineBundle.ps1 -Force -Only <key>`. If you changed a version in the manifest on
purpose, regenerate the checksums by running `Save-OfflineBundle.ps1` again, or pass
`-SkipChecksumCheck` for a one-off.

**The script says a version doesn't exist.**
It's right — see below. It installs the closest real version in the same major line and tells you.
Nothing is ever silently swapped across major versions.

---

## Version numbers to confirm with the requester

Two of the requested versions don't match anything that ships. Neither blocks the install, but
somebody should confirm what was meant.

| Requested | The problem | What the script does |
|---|---|---|
| **Node 22.2.2** | No such release. The 22.2.x line stops at 22.2.0. | Installs the newest 22.x and warns. |
| **WebLogic 14.1.0** | Oracle doesn't publish a 14.1.0 — it's 14.1.1.0 or 14.1.2.0. | Nothing automatic; you choose the file you download. This runbook assumes 14.1.1.0. |
| **npm 10.9.7** | Real — no action needed. | Pins to exactly 10.9.7. |

Also worth confirming: **Java 17 and 21 were both requested.** Both are installed side by side,
with 17 as the default. Say the word and we'll flip it to 21.

---

## Adding software to the list

More software will be requested. **Don't edit the scripts** — add an entry to
`software-manifest.psd1` and both scripts pick it up.

```powershell
@{
    Key     = 'postman'                  # short name for -Only / -Skip
    Name    = 'Postman'                  # shows in the log and the summary
    Version = '11.2.0'                   # $null = whatever the vendor calls "latest"
    Kind    = 'exe'
    Url     = 'https://dl.pstmn.io/download/version/{VERSION}/windows64'
    File    = 'postman-{VERSION}-x64.exe'
    Args    = @('/VERYSILENT', '/NORESTART')
    Notes   = 'Requested by <who> for <what>.'
    Request = 'REQ1234567'               # the Service Portal request it came from
}
```

`{VERSION}` is filled in from the `Version` field, so bumping a version is a one-line change.

| `Kind` | Use it when |
|---|---|
| `msi` | It's a `.msi`. Installed with `msiexec /qn`. |
| `exe` | It's an installer `.exe`. Put its silent-install flags in `Args`. |
| `zip` | No installer, just a folder — like Eclipse and Maven. Unzipped into `C:\DevTools`. |
| `npm` | Installed by npm itself. |
| `manual` | A person must fetch it — a login or licence click-through is in the way (Oracle). |

Then:

```powershell
.\Save-OfflineBundle.ps1 -Only postman     # adds it to the bundle + checksums
.\Install-DevWorkstation.ps1 -WhatIf -Only postman
```

and commit the updated `bundle-checksums.txt`.

---

## Open question

The request included the address **`108.28.150.170:33890`** with no explanation. Nothing uses it
yet. If it's the remote dev server, a database for SQL Developer, or the WebLogic admin console,
say which and it can be added here.
