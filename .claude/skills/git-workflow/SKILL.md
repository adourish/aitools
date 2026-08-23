---
name: git-workflow
description: Git and GitHub workflow — branching (gitflow), commit hygiene, pull requests, and pushing a repo to several remotes. Use for "make a branch", "open the PR", "what's the commit convention", "push to all remotes", or when a git operation needs the house workflow rather than ad-hoc commands.
---

# Git & GitHub workflow

| Task | Guide |
|------|-------|
| Everyday git — branches, commits, history, recovery | `development/skill_git_version_control.md` |
| Gitflow branching model (feature/release/hotfix) | `development/skill_gitflow_workflow.md` |
| Pull requests — create, review, merge | `development/skill_github_pull_requests.md` |
| Pushing one repo to multiple remotes | `system/skill_push_all_remotes.md` |

## House rules

- **Never `git add -A`.** Name the specific files you intend to commit.
- Branch per ticket, PR back to the integration branch — not straight to `main`.
- Credentials (GitHub PAT, GitLab PAT) come from the KeePass vault `API/` and `DevOps/` groups.
- Nothing secret ever enters a commit: no `.kdbx`, `.keyfile`, `.env`, `environments.json`, or token.
