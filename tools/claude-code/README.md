# tools/claude-code — Claude Code on ELSA + status line

Run **Claude Code** against the FDA **ELSA** gateway (FDA-hosted Claude **Sonnet 4.6**), plus the
shared two-line status line. Full instructions: [`docs/runbooks/RUNBOOK-claude-code-elsa.md`](../../docs/runbooks/RUNBOOK-claude-code-elsa.md).

## Quick start (on the FDA laptop, on the VPN)

```powershell
.\Install-ClaudeCodeElsa.ps1 -Only elsa      # installs the launcher onto your PATH (priority)
# new terminal, then:
claude-elsa -p "reply with OK"               # smoke test against ELSA
claude-elsa                                  # interactive session
```

Add the status line too:
```powershell
.\Install-ClaudeCodeElsa.ps1 -Only statusline
```

## What's here

| File | Purpose |
|------|---------|
| `claude-elsa.ps1` | Launcher — pulls ELSA keys from KeePass (`SEMOSS-Elsa-Dev`), sets the `ANTHROPIC_*` env vars for that process, runs `claude`. |
| `Install-ClaudeCodeElsa.ps1` | Installer: `-Only elsa`, `-Only statusline`, or `all`. |
| `statusline-command.sh` | Two-line emoji status line (context %, tokens, rate limits, model, git, process animations). ELSA-aware: shows `S4.6`. |
| `settings.template.json` | Sanitized Claude Code settings — **no secrets** (empty `permissions`). |

## Rules

- **Never hardcode the ELSA keys.** They come from KeePass or `ELSA_ACCESS_KEY`/`ELSA_SECRET_KEY`.
- **Never commit a real `~/.claude/settings.json`** — permission entries can hold tokens.
- ELSA needs the **full-tunnel VPN** up and the **internal CA** trusted.
