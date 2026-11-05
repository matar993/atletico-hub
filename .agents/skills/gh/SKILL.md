---
name: gh
description: "Use whenever a task requires interacting with the GitHub repository from the terminal: pull requests, reviews, issues, workflow runs."
allowed-tools: Bash, Read, Grep, Glob
---

# GitHub CLI (gh) Skill

Reference for `gh`, the official GitHub CLI.

## Prerequisites

Verify the installation before executing any commands:

```bash
gh --version
```

**If gh is not installed, inform the user and give platform-specific installation guidance** (`brew install gh` on macOS).

## Authentication

```bash
gh auth status
```

**If not authenticated, ask the user to run `gh auth login`.** Never ask for a token in the chat.

## Repository Context

gh resolves the repository from the `origin` remote of the current directory. Inside a worktree it works the same way. To target the repository explicitly, add `--repo matar993/atletico-hub`.

## Pull Requests

### Create

**The branch must already exist on the remote.** Push it first:

```bash
git push -u origin <branch>
```

```bash
gh pr create --draft --base develop --title "<Title>" --body-file - <<'BODY_END'
## Why

<why>

## What it brings

<what>
BODY_END
```

In a stack of pull requests, set `--base` to the branch of the pull request below instead of `develop` (see [Stacked pull requests](../../../CONTRIBUTING.md#stacked-pull-requests)).

Pass bodies through a quoted heredoc, never with `--body "<text>"`: inside double quotes the shell runs backticks and `$` as commands.

### Inspect

```bash
gh pr list --search "review-requested:@me"
gh pr view <pr>
gh pr view <pr> --comments
gh pr diff <pr>
gh pr checkout <pr>
gh pr view <pr> --json headRefOid,headRefName,baseRefName
```

### Comment

```bash
# On the pull request as a whole
gh pr comment <pr> --body-file - <<'COMMENT_END'
<comment>
COMMENT_END
```

Comments anchored to a line go through a review: see the [`code-review`](../code-review/SKILL.md) skill.

### Ready, update and merge

```bash
gh pr ready <pr>                                 # clear draft status
gh pr edit <pr> --body-file - <<'BODY_END'       # replace the description
<text>
BODY_END
gh pr checks <pr> --watch                        # wait for the workflow runs
```

Merge with a squash and the full squash message, as [CONTRIBUTING.md](../../../CONTRIBUTING.md#git-workflow) requires:

```bash
gh pr merge <pr> --squash --delete-branch --subject "<type>(<scope>): <description>" --body-file - <<'EOF'
<body>

Pull request: <pull request URL>
EOF
```

Never merge without the user's authorization and a green run on the latest commit.

## Issues

```bash
gh issue list --assignee @me
gh issue create --title "..." --label bug --body-file - <<'BODY_END'
<body>
BODY_END
gh issue view <issue>
```

## Workflow runs (CI)

```bash
gh run list --branch <branch> --limit 5   # latest runs of a branch
gh run watch <run-id> --exit-status       # follow a run, fail when it fails
gh run view <run-id> --log-failed         # logs of the failed steps
gh run rerun <run-id> --failed            # rerun the failed jobs
```

## Raw API

For anything the subcommands do not cover, use `gh api`. `{owner}` and `{repo}` resolve from the current repository:

```bash
gh api repos/{owner}/{repo}/pulls/<pr>/comments
gh api repos/{owner}/{repo}/branches/develop/protection
```

`gh <command> --help` is authoritative for the installed version.
