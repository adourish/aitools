# Runbook — Claude Code against the FDA ELSA gateway

**What this is:** how to run the **Claude Code** terminal against the FDA's **ELSA** LLM gateway
(FDA-hosted Claude, **Sonnet 4.6**) instead of a public Anthropic account — so the coding assistant
stays inside FDA data-handling rules. Installer + status line live in
[`tools/claude-code/`](../../tools/claude-code/).

> **Why ELSA and not a public account:** the AI coding tools may talk to **SEMOSS / ELSA only**,
> never an outside AI service (see [`RUNBOOK-ai-agent-coding-tools.md`](RUNBOOK-ai-agent-coding-tools.md)).
> ELSA is the FDA-approved model endpoint. Access is granted by **Vijay Bhagwati** (approver **Venu
> Boppana**) — see `SERIO-TEAM-CONTACTS.md`.

---

## The connection, in one place

| Setting | Value |
|---|---|
| **Endpoint (base URL)** | `https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai` |
| **Model** | `8405ac40-89c6-4613-848c-3d89986fbc01` — **Claude Sonnet 4.6** |
| **Auth** | HTTP Bearer, token = **`<access-key>:<secret-key>`** (the ELSA dev keys) |
| **Keys live in** | automation KeePass, entry **`SEMOSS-Elsa-Dev`** (UserName = access, Password = secret) — **never in the repo** |
| **Network** | reachable **only on the FDA full-tunnel VPN**; the endpoint presents the **internal CA** |

Claude Code is pointed at ELSA through its standard environment variables:

| Env var | Set to |
|---|---|
| `ANTHROPIC_BASE_URL` | the endpoint above |
| `ANTHROPIC_AUTH_TOKEN` | `<access>:<secret>` (Bearer) |
| `ANTHROPIC_MODEL` | `8405ac40-89c6-4613-848c-3d89986fbc01` |
| `ANTHROPIC_SMALL_FAST_MODEL` | same id (ELSA serves one model) |

> **Format note.** The path ends in `/model/openai` (an OpenAI-compatible surface). The values above
> are what we were granted; `claude-elsa.ps1` takes the base URL and model as overrides
> (`ELSA_CLAUDE_BASE_URL`, `ELSA_CLAUDE_MODEL`) so if ELSA exposes an Anthropic-format path or a new
> model id, you change one env var, not the script.

---

## Prerequisites

1. **On the FDA full-tunnel VPN** — `elsa-dev.preprod.fda.gov` only resolves there.
2. **Internal CA trusted** — otherwise HTTPS fails with "self-signed certificate in chain"
   (see [`RUNBOOK-internal-git-cert.md`](RUNBOOK-internal-git-cert.md) / FS-009).
3. **ELSA keys in the automation KeePass** as entry `SEMOSS-Elsa-Dev` (on the FDA laptop the vault is
   `C:\keys\automation-keys.kdbx` + `C:\keys\automation-keys.keyfile`; see the CLAUDE.md secret-storage
   section). **KeePassXC** installed (`Install-DevWorkstation.ps1 -Only keepassxc`).
4. **Claude Code** and **Git Bash** installed (Claude Code runs the status line via `bash`).

---

## Install (one time)

```powershell
# from the fda-serio repo on the FDA laptop
C:\projects\fda-serio\tools\claude-code\Install-ClaudeCodeElsa.ps1 -Only elsa   # ELSA launcher (priority)
# optional, adds the status line + settings:
C:\projects\fda-serio\tools\claude-code\Install-ClaudeCodeElsa.ps1 -Only statusline
```

`-Only elsa` copies `claude-elsa.ps1` (+ a `claude-elsa.cmd` shim) into `%USERPROFILE%\bin` and adds
that folder to your user PATH. **Open a new terminal** afterward so the PATH change takes effect.

---

## Run

```powershell
claude-elsa                       # interactive Claude Code session against ELSA
claude-elsa -p "reply with OK"    # headless smoke test (fastest way to confirm it works)
claude-elsa --model <other-id>    # any args are forwarded to claude
```

`claude-elsa` pulls the ELSA keys from KeePass, sets the `ANTHROPIC_*` env vars **for that process
only**, and launches `claude`. Nothing is written to disk; close the window and the env is gone.

**No KeePass on this box?** Set the keys inline for the session instead:
```powershell
$env:ELSA_ACCESS_KEY = '<access>'; $env:ELSA_SECRET_KEY = '<secret>'
claude-elsa
```

**Manual (no launcher), if you just want to point plain `claude` at ELSA once:**
```powershell
$env:ANTHROPIC_BASE_URL = 'https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai'
$env:ANTHROPIC_AUTH_TOKEN = '<access>:<secret>'
$env:ANTHROPIC_MODEL = '8405ac40-89c6-4613-848c-3d89986fbc01'
$env:ANTHROPIC_SMALL_FAST_MODEL = '8405ac40-89c6-4613-848c-3d89986fbc01'
claude
```

---

## Verify

- `claude-elsa -p "reply with OK"` prints a response → the endpoint, auth, and model are good.
- In an interactive session the **status line** (if installed) shows **`🤖 S4.6`** — that's ELSA's
  Sonnet 4.6 (the launcher maps the model id `8405ac40…` to `S4.6`).

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `getaddrinfo`/DNS failure on `elsa-dev.preprod.fda.gov` | **VPN full tunnel is down** — connect it first. |
| `self-signed certificate in certificate chain` / TLS error | internal CA not trusted — [`RUNBOOK-internal-git-cert.md`](RUNBOOK-internal-git-cert.md) / FS-009. |
| `401`/`403` or an auth redirect (302) | wrong/expired keys, or token not in `<access>:<secret>` form. Re-check the `SEMOSS-Elsa-Dev` KeePass entry. |
| "model not found" / empty responses | the model id changed — set `ELSA_CLAUDE_MODEL` to the current id (Sonnet 4.6 today is `8405ac40…`). |
| `claude-elsa` not recognized | open a **new** terminal (PATH), or run the `.ps1` by full path. |

---

## Security

- **ELSA keys never touch the repo** — they come from KeePass (`SEMOSS-Elsa-Dev`) or per-session env
  vars. The launcher only ever prints `auth=set`, never the value. These dev keys are **flagged for
  rotation** (pasted in chat historically).
- **`ANTHROPIC_AUTH_TOKEN` is a session credential** — set per-process by the launcher, not persisted.
- **Do not** commit a machine's `~/.claude/settings.json` to any repo — it can contain tokens in
  permission entries. The template in this folder is deliberately sanitized (empty `permissions`).

---

## Files

| File | What it is |
|---|---|
| [`tools/claude-code/claude-elsa.ps1`](../../tools/claude-code/claude-elsa.ps1) | the launcher — sets `ANTHROPIC_*` from KeePass and runs `claude` |
| [`tools/claude-code/Install-ClaudeCodeElsa.ps1`](../../tools/claude-code/Install-ClaudeCodeElsa.ps1) | installer (`-Only elsa` / `-Only statusline` / `all`) |
| [`tools/claude-code/statusline-command.sh`](../../tools/claude-code/statusline-command.sh) | the two-line emoji status line (ELSA-aware: shows `S4.6`) |
| [`tools/claude-code/settings.template.json`](../../tools/claude-code/settings.template.json) | sanitized Claude Code settings (status line, plugins, voice) — no secrets |

## Sources / verification

`single-source` — endpoint, model id (Sonnet 4.6), and Bearer `<access>:<secret>` auth provided by
the developer 2026-07-23; the `ANTHROPIC_*` env vars are Claude Code's standard custom-endpoint
configuration. The OpenAI-vs-Anthropic request-format detail on `/model/openai` is not independently
verified — the base URL and model are parameterized so they can be corrected without code changes.
