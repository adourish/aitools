# Runbook — mirroring internal FDA repos to private GitHub (so the REI-side assistant can read them)

**What this is:** how to copy an internal FDA source repo from `git.fda.gov` into a **private**
GitHub repo, so the capable assistant running on the **REI laptop** (which cannot see the FDA GFE
laptop directly — see [CLAUDE.md → Working environment](../../CLAUDE.md)) can read the code.

**The shape of it:**

```
  FDA GFE laptop                 GitHub (private)                 REI laptop (assistant)
  git.fda.gov  ──clone──►  adourish/<repo>  ──pull──►  C:\projects\<repo>
               (push --mirror)                        (read-only, never pushed back)
```

---

## ⚠️ Read this first — it's FDA source code

- **Every mirror MUST be private.** FDA-internal / SIRCE source in a public repo is a disclosure
  incident. Confirm `private=true` on every repo (this runbook's commands set it).
- **This is a data-handling decision, not just a convenience.** Copying government source to a
  personal GitHub account should be something you're authorized to do. If in doubt, ask before
  mirroring.
- **Scan every repo for committed secrets** (below) and rotate anything you find **at the FDA
  source**, not just on the mirror. Real credentials have already turned up this way (a Google
  service-account key in SERIO, a Nexus `_authToken` in SERIOPlusAIML).
- **The mirror is read-only downstream.** The REI-side clone is for reading; never push changes
  back through it. Real work still flows through the [agent bridge](RUNBOOK-agent-bridge-overview.md).

---

## Prerequisites

- The FDA laptop can already clone from `git.fda.gov` — cert trusted and a GitLab PAT working. If
  not, do [`RUNBOOK-internal-git-cert.md`](RUNBOOK-internal-git-cert.md) first.
- A GitHub account (`adourish`) with a token cached on the REI laptop (Git Credential Manager
  already has it, since we push `fda-serio` from there).

---

## Step 1 — Create the GitHub mirror (REI side): PRIVATE and EMPTY

**Empty means no README, no license, no `.gitignore`.** An auto-created README makes a root commit
with a history unrelated to the FDA repo, and the first push then fails with *"failed to push some
refs … non-fast-forward"* / *"refusing to merge unrelated histories."* An empty target fast-forwards
cleanly.

The assistant does this from the REI laptop with the cached GitHub token (name only, never printed):

```bash
R=<repo-name>
token=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill 2>/dev/null | sed -n 's/^password=//p')
curl -s -H "Authorization: token $token" -H "User-Agent: cc" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$R\",\"private\":true,\"auto_init\":false,\"description\":\"Private mirror of git.fda.gov FDA/ORA/SI/$R\"}"
unset token
```

(Or, if you have the `gh` CLI: `gh repo create adourish/$R --private`.)

## Step 2 — Push from the FDA laptop — push EVERYTHING, not one branch

⚠️ **Do NOT push from your everyday working clone.** `git push github --all` pushes only *local*
branches, and a normal clone has just ONE (the default). Even `git push github --mirror` from a
working clone can miss content that lives on a branch you never checked out. Both failed for
`shared-ui-component-library` — only a 1-file `master` stub went over while the real 580-object
content stayed behind.

**Use a bare `--mirror` clone — the bulletproof method.** A bare mirror clone pulls *every* ref as a
real ref, so `git push --mirror` copies all of it:

```powershell
$repo = "<repo-name>"
cd C:\projects
git clone --mirror https://git.fda.gov/FDA/ORA/SI/$repo.git "$repo-mirror"
cd "$repo-mirror"
git push --mirror https://github.com/adourish/$repo.git
cd ..
Remove-Item -Recurse -Force "$repo-mirror"        # optional cleanup
```

> `git push --mirror` makes the GitHub repo an *exact* copy of the source's refs (it will delete
> refs on GitHub that aren't in the source). For these one-way FDA→GitHub mirrors that's exactly what
> we want. Never run `--mirror` toward a repo that has commits of its own you want to keep.

### ⚠️ Gotcha — GitHub rejects any file over 100 MB (and it's in *history*, not just the tree)

GitHub hard-rejects a push containing **any single file > 100 MB**, even one buried in an old
commit. A full `--mirror` push carries all history, so a big binary that was committed once and
deleted later **still blocks the whole push**. This has bitten us three times: a **155 MB `.mp4`**
KT recording, a **456 MB SQL Developer** bundle, and a **122 MB `terraform-providers.tar.gz`**
(vendored provider cache in `serioplusapp/test/terraform/...` on the AWS devops repo). None belong
in a read-for-analysis mirror.

The error looks like:

```
remote: error: File <path> is 122.18 MB; this exceeds GitHub's file size limit of 100.00 MB
 ! [remote rejected] <branch> -> <branch> (pre-receive hook declined)
```

**Fix — mirror a clean single-commit snapshot of the tree instead of full history.** Because we only
need the *current* code to read, drop history entirely (that also strips the offending blobs from
history, not just the tree) and log what you removed so the mirror stays honest:

```powershell
$repo   = "<repo>"          # e.g. aws  (GitHub side: si-devops-aws)
$branch = "release/1.0.0"   # the branch that has the code
$gh     = "https://github.com/adourish/si-devops-aws.git"
cd C:\projects
git clone --depth 1 --branch $branch "https://git.fda.gov/FDA/ORA/SI/devops/$repo.git" "$repo-snap"
cd "$repo-snap"
Remove-Item -Recurse -Force .git                      # drop all history

$root = (Get-Location).Path
$big  = Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 100MB }
$big | ForEach-Object { "{0,8:N1} MB  {1}" -f ($_.Length/1MB), $_.FullName.Substring($root.Length+1) }
"Stripped from the GitHub mirror (exceed GitHub's 100 MB/file limit; re-fetch from git.fda.gov):" |
  Out-File MIRROR-NOTES.md -Encoding utf8
$big | ForEach-Object { "- {0} ({1:N1} MB)" -f $_.FullName.Substring($root.Length+1), ($_.Length/1MB) } |
  Out-File MIRROR-NOTES.md -Append -Encoding utf8
$big | Remove-Item -Force

git init -q
git add -A
git commit -q -m "$repo snapshot ($branch) — files >100MB stripped; see MIRROR-NOTES.md"
git branch -M $branch
git remote add github $gh
git push github $branch --force
```

Two separate failure modes hide here — don't confuse them:
> - **`fatal: did not receive expected object … / index-pack failed`** on a `--depth 1` clone is the
>   **shallow-push** limitation (the thin pack references grafted parents the remote lacks), *not* a
>   size problem. The `Remove-Item .git; git init` re-init above fixes it too, since it rebuilds a
>   complete single-commit pack.
> - **`exceeds GitHub's file size limit`** is the 100 MB rule — fixed by stripping the big files
>   (above). You can hit the shallow error first, fix it, then hit the size error next; expect both.

Prefer this snapshot method whenever a `--mirror` push fails on size. You lose history (fine for a
read-only mirror) but gain a guaranteed-pushable tree.

## Step 3 — Pull on the REI side

The assistant pulls and checks out the branch that actually has content:

```bash
cd /c/projects/<repo-name>
git fetch origin --prune
b=$(git remote show origin | sed -n 's/.*HEAD branch: //p')   # the default branch
git checkout -B "$b" "origin/$b"
```

⚠️ **Watch the default-branch trap.** Some FDA repos put real code on **`master`** while the mirror's
default is **`main`** (or vice-versa). SERIO is like this: 3,466 files on `master`, an empty `main`.
If a pull lands you on a 1-file branch, the code is on the *other* branch — check
`git ls-remote --heads origin` and check out the populated one.

## Step 4 — Make the default branch match the code (REI side)

So future pulls don't drop back to an empty branch, point the GitHub default at the real branch:

```bash
R=<repo-name>; B=<branch-with-code>    # e.g. master
token=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill 2>/dev/null | sed -n 's/^password=//p')
curl -s -X PATCH -H "Authorization: token $token" -H "User-Agent: cc" \
  https://api.github.com/repos/adourish/$R -d "{\"default_branch\":\"$B\"}"
unset token
```

## Step 5 — Scan for committed secrets

On the REI-side clone, before relying on the repo:

```bash
cd /c/projects/<repo-name>
git ls-files | grep -iE '\.env$|credential|secret|\.pem$|\.p12$|\.jks$|\.keystore$|_key\.json$|-key\.json$|\.npmrc|application.*\.properties$' | grep -viE '\.example$|\.sample$'
git grep -liE '_authToken=|private_key|BEGIN (RSA|PRIVATE)|client_secret|password\s*=\s*\S' -- .
```

Anything real: **rotate it at the source** and remove it from the FDA repo (history included) — not
just from the mirror. See the checklist below.

---

## Updating an existing mirror later

FDA side (pick up new commits and re-mirror):

```powershell
cd C:\projects\<repo-name>
git pull                        # from git.fda.gov (origin)
git push github --mirror        # re-sync the GitHub copy
```

REI side (assistant re-pulls all mirrors):

```bash
for R in SERIO SERIOPlusAIML SERIOPlusCommonLibraries Shared-AI-Service shared-ui-component-library; do
  cd /c/projects/$R || continue
  git fetch origin --prune --quiet
  b=$(git remote show origin | sed -n 's/.*HEAD branch: //p')
  git checkout -B "$b" "origin/$b" --quiet
done
```

---

## Switch every repo to its latest release branch

Handy when you want each clone on the newest `release/<version>` branch rather than `main`/`master`.
Two things make this correct: filter to real `release/NN.NN(.NN)` branches (so oddballs like
`release-after-detention` are ignored), and sort by **version number**, not alphabetically — otherwise
`release/9.x` sorts *after* `release/12.x` and you get the wrong one.

**PowerShell (FDA laptop or REI laptop):**

```powershell
$repos = "SERIO","SERIOPlusAIML","SERIOPlusCommonLibraries","Shared-AI-Service","shared-ui-component-library"
foreach ($r in $repos) {
  Set-Location C:\projects\$r
  git fetch origin --prune 2>$null
  $rel = git for-each-ref --format='%(refname:short)' refs/remotes/origin |
         ForEach-Object { $_ -replace '^origin/','' } |
         Where-Object { $_ -match '^release/\d+(\.\d+)+$' } |            # only release/NN.NN(.NN)
         Sort-Object { [version]($_ -replace '^release/','') } |         # true numeric-version sort
         Select-Object -Last 1
  if (-not $rel) { $rel = (git remote show origin | Select-String 'HEAD branch:').Line.Split(':')[-1].Trim() }
  git -c advice.detachedHead=false checkout -B $rel "origin/$rel" 2>$null
  Write-Host "$r -> $rel  ($((git ls-files | Measure-Object).Count) files)"
}
```

**Bash (REI laptop):**

```bash
for R in SERIO SERIOPlusAIML SERIOPlusCommonLibraries Shared-AI-Service shared-ui-component-library; do
  cd /c/projects/$R || continue
  git fetch origin --prune --quiet
  rel=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin \
        | sed 's#^origin/##' | grep -E '^release/[0-9]+(\.[0-9]+)+$' | sort -V | tail -1)
  [ -z "$rel" ] && rel=$(git remote show origin | sed -n 's/.*HEAD branch: //p')
  git checkout -B "$rel" "origin/$rel" --quiet
  echo "$R -> $rel ($(git ls-files | wc -l) files)"
done
```

> Notes: the red `git : Switched to a new branch…` lines in PowerShell are **not errors** — git writes
> that message to stderr, which PowerShell paints red; `2>$null` hides it. And this only works on the
> **REI side** for repos whose `release/*` branches actually reached GitHub — a repo pushed before the
> bare-`--mirror` step (Step 2) may have only `main`/`master`, so re-mirror it first.

---

## Current mirrors (all private)

| FDA repo (`git.fda.gov/FDA/ORA/SI/`) | GitHub mirror | Default branch | REI-side |
|---|---|---|---|
| SERIO | adourish/SERIO | `master` | ✅ release/13.0.0 = 3,466 files (Java 21 / WLS 14.1.2.0) |
| serioplusaiml | adourish/SERIOPlusAIML | `main` | ✅ 1,101 files (needs `dev` pushed to set default) |
| SERIOPlusApp | adourish/SERIOPlusApp | `dev` | ✅ 1,224 files |
| SERIOPlusServices | adourish/SERIOPlusServices | `dev` | ✅ 296 files (business microservices) |
| SERIOPlusDataServices | adourish/SERIOPlusDataServices | `dev` | ✅ 617 files (data microservices) |
| serioplusintegrationservices | adourish/serioplusintegrationservices | `dev` | ⚠️ `dev` is a 1-file stub — real content likely on another branch |
| SERIOPlusCommonLibraries | adourish/SERIOPlusCommonLibraries | `dev` | ✅ 488 files |
| Shared-AI-Service | adourish/Shared-AI-Service | `main` | ✅ README-only stub on FDA side |
| shared-ui-component-library | adourish/shared-ui-component-library | `release/1.0.0` | ✅ 147 files — content on `release/1.0.0`; `master` is a 1-file stub. |

## Secret-remediation checklist (rotate at the FDA source)

- [ ] **SERIO** — Google service-account private key committed at
  `serio-ws-war/src/main/resources/config/google_application_credentials.json`
  (project `serio-303617`, client `serio-web@…`). Rotate in GCP, remove from history, feed via
  env/secret instead.
- [ ] **SERIOPlusAIML** — Nexus registry `_authToken` in `.npmrc-bk`
  (`nexus2.fda.gov/repository/npm-snapshot/`). Revoke/rotate the Nexus token, delete the `-bk`
  backup from the repo and history.
- [ ] **shared-ui-component-library** — base64 Nexus `_auth` token in
  `shared-service-ui/projects/shared-service-common-ui/.npmrc`
  (`si-cmtools.dev.fda.gov:8081/repository/npm-snapshot`). Rotate the Nexus credential and remove
  the committed `.npmrc` from the repo and history.
- [ ] **Shared-AI-Service** — live-looking `token_auth` **client id/secret + apiKey** for the preprod
  flow in `docs/CONFIGURATION_REFERENCE.md`. Rotate at the source, move to a secret store, and scrub
  from history. (Found 2026-07-20 while mapping the IDP code — see `kt/SERIO-IDP-PROCESS.md` §7.)
- [ ] **SERIOPlusDataServices** — a **real Oracle DB password** (`serioplus.datasource.password`)
  committed in `serioplus-application-service/src/main/resources/application.properties` **and** a
  leftover `application1.properties.backup` (a different, older password). **Highest priority** —
  rotate the DB password, delete the `.backup`, and externalize (env / AWS Secrets Manager, which
  the services already use via `AwsSecretsClient`).
- [ ] **SERIOPlusApp** — Nexus `_authToken` in `.npmrc-bk` (`nexus2.fda.gov/.../npm-snapshot`).
  Rotate + delete the `-bk` backup.

---

## Where this came from

Built while mirroring the SERIO / SERIO+ repos on 2026-07-15 so the REI-side assistant could read
code it otherwise cannot reach. The `--all`-only-pushes-local-branches and `main`-vs-`master`
default-branch traps are both from real misfires during that work. Tracked as FS-010.
