# Runbook — trusting an internal FDA git/HTTPS server certificate

**What this is:** how to fix a `git clone` (or any HTTPS call) that fails with

> `SSL certificate problem: self-signed certificate in certificate chain`

against an **internal** FDA server such as `git.fda.gov` — and then how to **sign in** to it,
because that server is GitLab and needs a personal access token, not a password. Two separate walls,
in this order: trust the certificate, then authenticate.

**Script:** [`tools/certs/Import-InternalGitCert.ps1`](../../tools/certs/Import-InternalGitCert.ps1)

**Related:** [`RUNBOOK-dev-workstation-setup.md`](RUNBOOK-dev-workstation-setup.md) (developer
software) · [`RUNBOOK-ai-agent-coding-tools.md`](RUNBOOK-ai-agent-coding-tools.md) — the Elsa
`elsa-dev.pem` set-up is the same idea, a certificate the machine does not trust by default.

---

## Why this happens

Internal FDA servers are signed by an **internal certificate authority (CA)** — the FDA's own,
not a public one. Git for Windows uses the **OpenSSL** backend by default, and OpenSSL only trusts
a fixed file of *public* CAs (`ca-bundle.crt`). It has never heard of the FDA's internal CA, so it
rejects the certificate. Your **browser** works on the same site because browsers use the
**Windows certificate store**, which — on some machines but not all — has the internal CA
installed.

So there are two ways to fix it, and the script does both:

1. **Point Git at the certificate** for that one host (nothing else changes, no admin).
2. **Install the CA into Windows** so Git (via the schannel backend), the browser, and everything
   else trust it.

> **Important:** if all your Windows CAs still don't fix it, the internal CA simply **isn't on
> your machine yet**. You cannot borrow it from the public bundle — you have to capture it from
> the server (below) or get it from the infrastructure team.

---

## The quick fix

Run this on a machine/network that **can reach the server** (on VPN if that's what it takes).
No administrator rights needed.

```powershell
cd C:\projects\fda-serio\tools\certs
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # if scripts are blocked

# 1) Look first: capture the chain and print it, trust nothing yet
.\Import-InternalGitCert.ps1 -HostName git.fda.gov
```

Read what it prints. The last line of the chain, marked `<-- self-signed root`, is the FDA
internal CA you were missing. **Confirm it looks like an FDA / HHS / internal-CA name.** Then pick
one:

```powershell
# 2a) Least invasive: trust it for git.fda.gov only (Git only)
.\Import-InternalGitCert.ps1 -HostName git.fda.gov -ConfigureGit

# 2b) Or install it so the browser and everything else trust it too
.\Import-InternalGitCert.ps1 -HostName git.fda.gov -Install
```

Then clone:

```powershell
git clone https://git.fda.gov/FDA/ORA/SI/ai-sdlc-playbook.git
```

The certificate error is now gone. The clone will instead ask you to **sign in** — that's the next
step, [Authenticating to git.fda.gov](#authenticating-to-gitfdagov-gitlab-needs-a-token-not-a-password),
not another certificate problem.

---

## What each option actually does

| | `-ConfigureGit` | `-Install` |
|---|---|---|
| **Writes** | `%USERPROFILE%\git.fda.gov-ca.pem` | same file |
| **Git change** | `http.https://git.fda.gov/.sslCAInfo` -> the .pem (this host only) | `http.sslBackend schannel` (all hosts use the Windows store) |
| **Windows store** | untouched | adds the root CA to `Cert:\CurrentUser\Root` |
| **Also fixes the browser / other tools?** | no | yes |
| **Admin needed?** | no | no (current-user store) |
| **Best when** | you want the smallest possible change | you'll use several internal FDA sites |

**A note on upkeep:** the `.pem` from `-ConfigureGit` is a snapshot — if the FDA rotates its CA
you'll get the error again and re-run the script. `-Install` + schannel reads the live Windows
store, so it keeps working across rotations. Both are fine; pick by preference.

---

## Authenticating to git.fda.gov (GitLab needs a token, not a password)

Once the certificate is trusted, the clone gets *past* the SSL error and asks you to sign in.
git.fda.gov is a **GitLab** server, and GitLab does **not** accept your account password over Git —
you authenticate with a **personal access token (PAT)**. (Your ALT-PIV card signs you in to the
GitLab *website*; the Git command line uses the token.)

### 1. Create the token

1. Open the token page — sign in with your ALT-PIV / FDA SSO if prompted:
   <https://git.fda.gov/-/user_settings/personal_access_tokens>
2. **Add new token.** Give it a name (e.g. `git-cli`), set an expiry date, and tick the scopes:
   - **`read_repository`** — enough to **clone and pull**.
   - add **`write_repository`** — only if you also need to **push**.
3. Click **Create personal access token**, then **copy the `glpat-…` value right away** — GitLab
   shows it only once.

### 2. Use it

Clone (or pull / push) and paste the token as the **password**, not your account password:

```powershell
git clone https://git.fda.gov/FDA/ORA/SI/ai-sdlc-playbook.git
# Username for 'https://git.fda.gov':  <your GitLab username>     (or: oauth2)
# Password for 'https://git.fda.gov':  <paste the glpat-... token>
```

Git Credential Manager saves it to Windows Credential Manager, so you are **not** prompted again on
later pulls and pushes. If your username is rejected, GitLab also accepts **`oauth2`** as the
username with a PAT.

### 3. Keep the token in your vault

Store the PAT in KeePass so you can re-enter it if the credential cache is ever cleared. The `-p`
flag prompts for the token, so it never lands in your shell history:

```powershell
keepassxc-cli add -p -u "<your GitLab username>" --url "https://git.fda.gov" --notes "GitLab PAT for git.fda.gov" "G:\My Drive\Areas\Keys\automation-keys.kdbx" "FDA GitLab PAT - git.fda.gov"
```

It asks for your database master password first, then `Enter password for new entry:` — paste the
`glpat-…` token there.

> **Rotate an exposed token.** If a PAT ever ends up somewhere shared — a chat, an email, a ticket
> — revoke it on the same Access Tokens page and issue a fresh one. **Never commit a PAT to the
> repo.**

---

## If it still fails after `-Install`

The server didn't send its root, or the root it sent isn't self-signed. The script warns you when
that happens. Get the CA file (`.pem` / `.crt`) directly from the infrastructure team
(**Vijay Bhagwati**) and either:

```powershell
# trust that file for the host, Git only:
git config --global "http.https://git.fda.gov/.sslCAInfo" "C:/path/to/fda-internal-ca.pem"
```

or double-click the `.crt` -> **Install Certificate** -> **Current User** -> **Trusted Root
Certification Authorities**, then set `git config --global http.sslBackend schannel`.

---

## What NOT to do

**Do not** run `git config --global http.sslVerify false`. That turns off certificate checking for
**every** server, which is how access tokens get stolen by an intercepting proxy. If you ever need
a one-time bypass to test, scope it to a single command instead:

```powershell
git -c http.sslVerify=false clone https://git.fda.gov/...   # one-off only, not global
```

But with the script above you shouldn't need even that.

---

## The manual (GUI) version

If you'd rather click than script, this is the same as `-Install`:

1. Open `https://git.fda.gov` in Edge.
2. Click the padlock -> the certificate -> **Certification Path**.
3. Select the **top (root)** certificate -> **View Certificate** -> **Details** -> **Copy to
   File** -> export as a DER `.cer`.
4. Double-click the `.cer` -> **Install Certificate** -> **Current User** -> **Place all
   certificates in the following store** -> **Trusted Root Certification Authorities**.
5. `git config --global http.sslBackend schannel`.

---

## Where this came from

Real incident, 2026-07-15: `git clone https://git.fda.gov/FDA/ORA/SI/ai-sdlc-playbook.git` failed
with "self-signed certificate in certificate chain" on a workstation whose Git used the OpenSSL
backend, and the FDA internal CA was not present in the Windows store either. Switching Git to the
`schannel` backend trusted the FDA CA and cleared the error; the clone then succeeded once a GitLab
personal access token was supplied as the password. **Both halves verified end to end on
2026-07-15.** The script and this runbook are the reusable fix. Tracked as FS-009.
