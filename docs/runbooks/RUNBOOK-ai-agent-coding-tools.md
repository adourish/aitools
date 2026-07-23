# Runbook — AI agent coding tools in VS Code (SEMOSS Elsa-Dev)

**What this is:** how to install VS Code and an AI coding assistant, and point it at the FDA's
own AI models (SEMOSS Elsa-Dev) so it works inside FDA rules.

**The one rule that matters:** these plugins may **only** be connected to SEMOSS Dev and an
approved SEMOSS model. **Do not connect them to any AI account outside the FDA** (no personal
OpenAI, Anthropic, or similar keys). The whole point of the SEMOSS set-up below is that your
code and prompts stay inside FDA systems.

**Roughly how long:** 30 minutes, plus waiting on the ERIC ticket and the access request.

**Related:** [`RUNBOOK-elsa-sirce-access.md`](RUNBOOK-elsa-sirce-access.md) (getting access in
the first place) · [`RUNBOOK-dev-workstation-setup.md`](RUNBOOK-dev-workstation-setup.md) (Java,
Node, WebLogic and the rest of the developer software).

---

## Before you start

1. **Get SEMOSS access approved.** This has to be requested and approved before anything below
   works — the AI models live behind SEMOSS Elsa-Dev
   (`https://elsa-dev.preprod.fda.gov/SemossWeb/packages/client/dist/`). The flow:
   - Ask **Vijay Bhagwati** (infrastructure) for access to the SEMOSS AI models. New REI
     contractors: say who you are and that you need SEMOSS AI model access.
   - Vijay routes it for approval — **an approval email goes to Venu Boppana**. (Amlan Das, the
     project manager, is typically in the loop.)
   - Once Venu approves, **Vishnu Vardhan VenkatachalamSrinivasan** (infrastructure) provisions
     your SEMOSS Dev access and adds you to the coding-assistant team. Only then can you generate a
     token (Step 2) and reach the models. You'll get an email confirming access is granted.
2. **VS Code installed.** You cannot install it yourself on a locked-down FDA machine. Submit an
   **ERIC ticket** asking for the latest version of Visual Studio Code. (If you are also setting
   up the rest of the developer software, see the workstation runbook above.)

---

## Step 0 — Confirm you can reach Elsa-Dev

Before configuring anything, prove your access actually works. You must be on the **FDA GFE laptop
with the full tunnel connected** — Elsa-Dev is internal to the FDA network.

**Quickest check:** open the Elsa-Dev site in a browser:
`https://elsa-dev.preprod.fda.gov/SemossWeb/packages/client/dist/`
If it loads (or asks you to sign in), your access works — go to Step 1.

**Or run the check script**, which also tells you *why* if it fails:

```powershell
tools\elsa\Test-ElsaAccess.ps1
```

> **"running scripts is disabled on this system"?** The FDA laptop blocks `.ps1` files by default.
> Either run it without changing any setting —
> `powershell -ExecutionPolicy Bypass -File .\Test-ElsaAccess.ps1` — or unblock the current window
> only with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (reverts when you close it;
> no admin needed).

It checks, in order: is the tunnel up (can it resolve the host), does the web app answer, is the
certificate trusted. What it tells you:

- **"connect the VPN"** — the full tunnel is down. Connect it and re-run.
- **certificate not trusted** — the internal FDA CA. Point the check at the pem:
  `tools\elsa\Test-ElsaAccess.ps1 -CertPath C:\Users\<you>\elsa-dev.pem` (that pem is Step 3), or
  install the internal CA per [`RUNBOOK-internal-git-cert.md`](RUNBOOK-internal-git-cert.md).
- **HTTP 200 / a sign-in redirect** — you're good.

Once you have a token (Step 2) and a model id (Step 4), you can prove the models actually answer —
the real test that the plugins will work:

```powershell
$env:ELSA_API_KEY = "ACCESSKEY:SECRETKEY"
tools\elsa\Test-ElsaAccess.ps1 -Model <model-id>
```

The token is never printed or saved by the script.

> **Confirmed working 2026-07-15** on the GFE laptop with the tunnel up: the check passed (host
> resolved to an internal `10.x` address, certificate accepted with no pem needed, HTTP 200) and a
> model replied through the endpoint. So if your run reaches step 4 and the model answers, your
> token and model id are good and the VS Code plugin will work with the same values.

---

## Step 1 — Install one of the approved plugins

Three AI coding plugins have been checked and are allowed:

| Plugin | Marketplace name |
|--------|------------------|
| **Continue** | Continue — open-source AI code agent |
| **Cline** | Cline |
| **Roo Code** | Roo Code |

To install one:

1. Open VS Code.
2. Click the **Extensions** icon in the left sidebar. (Hover over the icons if you are not sure
   which one it is — the label says *Extensions*.)
3. In the **Search Extensions in Marketplace** box, type the plugin name from the table above.
4. Click **Install** and follow the prompts.
5. When it finishes, check that the plugin's icon has appeared in the left-hand Activity Bar.

You only need one of the three. Pick whichever you prefer; all three are configured the same way
(an "OpenAI-compatible" connection pointed at SEMOSS).

---

## Step 2 — Create your SEMOSS access token

The plugin signs in to SEMOSS with a **personal access token** — a pair of values, an *access
key* and a *secret key*.

1. Go to the SEMOSS Elsa-Dev site:
   `https://elsa-dev.preprod.fda.gov/SemossWeb/packages/client/dist/`
2. Click the **menu** in the top-left corner (to the left of the word *SEMOSS*).
3. Go to **Settings** → **My Profile**.
4. Scroll to **Personal Access Tokens** and click **+ New Key**.
5. Name it `VS Code` and click **Generate**.
6. **Copy both the Access Key and the Secret Key somewhere safe right now.** SEMOSS will not show
   the secret key again.

> Treat these two values like a password. Do not paste them into a shared document, a ticket, or
> a git repository.

---

## Step 3 — Install the certificate file

The Elsa-Dev site uses an internal certificate that your machine does not trust by default, so
you need its `.pem` file locally.

1. Open File Explorer and go to your home folder — `C:\Users\<your-username>`.
2. Copy the provided zip file there, unzip it, and leave **`elsa-dev.pem`** in that folder.

The result should be a file at `C:\Users\<your-username>\elsa-dev.pem`.

> The zip is distributed by the infrastructure team — it is not in this repository. Ask Vijay
> Bhagwati if you do not have it.

---

## Step 4 — Find the model ID

1. On the Elsa-Dev site, open the left menu and go to **Models**.
2. You get a list of the available models, each with an **ID**.
3. Copy the ID of the model you want. You need it in the next step.

Any model on the SEMOSS Dev instance is fair game — but it must be a SEMOSS one.

---

## Step 5 — Configure your plugin

Everything below uses the same three facts: the SEMOSS address, your two keys joined by a colon,
and the model ID.

- **Base URL:** `https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai`
- **API key:** `<your-access-key>:<your-secret-key>` — note the **colon** between them, with no
  spaces. This is one single string, not two fields.
- **Model ID:** whichever you copied in Step 4.
- **API provider:** *OpenAI Compatible*

### Continue

Continue is configured from a file rather than a screen.

1. Open `C:\Users\<your-username>\.continue\config.yaml` in a text editor.
2. Replace the whole contents with the following, then fill in the three placeholders:

```yaml
name: Local Assistant
version: 1.0.0
schema: v1
models:
  - name: Elsa_PPDev-Sonnet4.5
    provider: openai
    model: <paste-the-model-id-here>
    apiBase: https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai
    apiKey: <your-access-key>:<your-secret-key>
    requestOptions:
      caBundlePath: C:\Users\<your-username>\elsa-dev.pem
    roles:
      - autocomplete
      - chat
      - edit
      - apply
```

3. Save and close the file.

Three things to get right, and they are the usual causes of failure:
- The **model** line takes the ID from Step 4, not a friendly name.
- The **apiKey** line is access key, then a colon, then secret key.
- The **caBundlePath** line must use *your* username, matching the folder name in File Explorer.

### Cline

Cline asks for its settings the first time you click its icon:

- **API Provider:** OpenAI Compatible
- **Base URL:** `https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai`
- **OpenAI Compatible Key:** `<your-access-key>:<your-secret-key>`
- **Model ID:** any model from SEMOSS Dev

### Roo Code

Roo Code also asks on first click:

- **Configuration Profile:** Default
- **API Provider:** OpenAI Compatible
- **Base URL:** `https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai`
- **API Key:** `<your-access-key>:<your-secret-key>`
- **Model:** any model from SEMOSS Dev

---

## Step 6 — Restart and test

1. Close VS Code completely and reopen it.
2. Click the plugin's icon in the Activity Bar.
3. Type any prompt. You should get a reply.

If you do, the connection works. Next, how to actually use it.

---

## Step 7 — Using the agent in VS Code

**Open a project folder first** (File → Open Folder). The agent works on whatever workspace is
open — it reads and changes files in that folder.

**The standing rule still applies:** the agent may only talk to SEMOSS Dev and an approved SEMOSS
model. Never repoint it at an outside AI account.

The three plugins fall into two styles.

### Cline / Roo Code — the autonomous agents

These are the "agents": you describe a task in plain English and they plan it, read and edit files,
and run terminal commands to carry it out.

1. Click the **Cline** (or **Roo Code**) icon in the left Activity Bar.
2. Type a task — e.g. *"Add input validation to the login form and write a test for it."*
3. The agent proposes a plan and the edits / commands it wants to run. **Review each step.**
4. **Approve or reject** each file change and each terminal command. Both default to asking first.
   You can enable auto-approve for low-risk actions later — start with it **off** until you trust it.
5. It iterates, showing diffs you accept or reject, until the task is done.

- **Roo Code** has **modes** (a dropdown): *Ask* is read-only Q&A, *Code* makes changes,
  *Architect* plans, *Debug* investigates. Pick the one that matches what you want.
- **Cline** has **Plan** vs **Act**: Plan talks through the approach without touching files; Act does
  the work. Start in Plan for anything non-trivial.

### Continue — assistant + inline edits

Continue is an in-editor assistant (chat, edit, autocomplete), with an agent mode in newer builds:

- **Chat:** `Ctrl+L` — ask about the open file or project.
- **Edit in place:** select code, `Ctrl+I`, describe the change; accept/reject the diff.
- **Autocomplete:** suggestions appear as you type; `Tab` to accept.
- **Agent mode** (if your version has it): a chat mode that can use tools and edit across files,
  like Cline.

### Good habits

- **Open the right folder** — that's the agent's whole context.
- **Be specific** — name files, state the outcome and any constraints.
- **Review every diff and command before approving.** The agent is fast, not infallible; you own
  what lands.
- **Work in small steps and commit as you go**, so you can undo cleanly.
- **Keep it on SEMOSS.** Never switch the model to an external account.

---

## Troubleshooting

**Roo Code stops working after a VS Code update.**
From VS Code **1.122.0** onward, Roo Code can become unusable. VS Code moved where it keeps the
bundled `ripgrep` search tool, and Roo Code still looks for it on the old path. This affects
other extensions too (Todo-Tree, for example). It is a known VS Code regression, tracked as
[microsoft/vscode issue #318691](https://github.com/microsoft/vscode/issues/318691).
If you hit it, use Continue or Cline until it is fixed upstream.

**Certificate or SSL errors.** Almost always the `caBundlePath` line: check the file really is at
`C:\Users\<your-username>\elsa-dev.pem` and that the username in the path matches your own.

**401 / authentication errors.** Re-check the API key is `accesskey:secretkey` — one string, one
colon, no spaces. If in doubt, generate a fresh token (Step 2); the secret key is only ever shown
once, so a mistyped copy cannot be recovered, only replaced.

---

## Useful links

| Link | What it's for |
|------|---------------|
| [Elsa — token usage](https://elsa.fda.gov/beta/#/embed/token-usage) | See how many tokens you have used against the Elsa AI models. Worth checking if the plugin starts refusing requests or slows down — you may be near a limit. |
| [Elsa-Dev (SEMOSS)](https://elsa-dev.preprod.fda.gov/SemossWeb/packages/client/dist/) | Where you generate your personal access token (Step 2) and find the model IDs (Step 3). |
| [Elsa-Dev model API endpoint](https://elsa-dev.preprod.fda.gov/Monolith/api/model/openai) | The `apiBase` / Base URL value every plugin needs. Not a page to visit — a value to paste. |
| [microsoft/vscode issue 318691](https://github.com/microsoft/vscode/issues/318691) | The VS Code 1.122.0 `ripgrep` regression that breaks Roo Code (see Troubleshooting). |

Note the token-usage page is on **`elsa.fda.gov`**, which is a different host from the
**`elsa-dev.preprod.fda.gov`** used everywhere else in this runbook. They are not the same
environment, so if your usage figures look wrong or empty, that is the first thing to check.

All the FDA links need you to be on the FDA network and signed in.

---

## Support

Technical support for this set-up: **Vijay Bhagwati** (infrastructure team). A distribution email
is expected to replace this single contact later.

---

## Where this came from

Adapted from the FDA document *"Installation of Visual Studio Code and Plugin"*, version 1.0,
dated 2026-01-30. Rewritten in plain English; the steps and values are unchanged.

The original has screenshots at several steps (the Elsa-Dev landing page, the e3530 role picker,
the model list). They are not reproduced here — this runbook describes what to look for instead.
