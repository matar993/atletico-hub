---
name: code-review
description: "Review the changes of a branch or a GitHub pull request for correctness, security, design, maintainability, performance and testing, and rank findings Critical, Major or Minor. Use when the user asks to review a branch, a PR or a diff. Given a PR number, it also adds each finding as a comment of a pending review on the right line of the PR diff."
context: fork
allowed-tools: Bash, Read, Grep, Glob
---

# Atletico Hub code review

You are a senior software engineer performing a rigorous code review.

Your goal is to identify high-impact issues in correctness, design, and maintainability.
Do not focus on trivial style issues unless they affect clarity or correctness.

## 1. Find the target

The argument names the target:

- A PR number (`33`, `#33`): read it with `gh pr view <pr> --json headRefOid,headRefName,baseRefName`. Take `headRefOid` as `<sha>`, `headRefName` and `baseRefName`. Run `git fetch origin <headRefName> <baseRefName>`.
- A branch name: run `git fetch origin develop <branch>`. `<head>` is the local branch when it exists, otherwise `origin/<branch>`. Compare it with `origin/develop`.
- No argument: run `git fetch origin develop`. `<head>` is `HEAD`. Compare it with `origin/develop`.

The diff is `git diff origin/<target>...<head>`. Use the three-dot form: only the changes the branch introduces. Review committed changes only: uncommitted and untracked files are out of scope.

For a PR, `<head>` is the PR `<sha>`, never the local checkout. Check that the fetch brought it: `git cat-file -e <sha>`. When it did not, stop and say so.

Never check out, switch, stash or reset: the working tree belongs to the user and may hold uncommitted changes. Read files at `<head>` with `git show <head>:<path>`, not from the working tree.

## 2. Read the intent

Before judging the code, read what it is meant to do:

- The commit messages: `git log --format='%h %s%n%b' origin/<target>..<head>`.
- The OpenSpec change named in the commits or the PR description (`Change: <id>`): its `proposal.md`, `design.md` and delta specs in `openspec/changes/` or `openspec/changes/archive/`.
- New or changed ADRs in `docs/documents/architecture/adr/`.
- `CONTRIBUTING.md`, `CODE_GUIDELINES.md` and `AGENTS.md` for the project rules.

A design that says a risk is accepted is still open to review: check that its reasoning holds.

## 3. Review

Focus only on the changes introduced. Do not review unchanged code unless necessary for context.

Prioritize findings in this order:

1. Correctness and bugs
2. Security risks, including personal data of players (names, phone numbers, medical certificates)
3. Architectural and design issues
4. Maintainability and readability
5. Performance concerns
6. Style (only if meaningful)

Evaluate the code across:

- Correctness (edge cases, failure modes)
- Design (abstractions, coupling, responsibilities)
- Maintainability (clarity, duplication, complexity)
- Performance (efficiency, scalability)
- Testing (coverage, missing scenarios)

Actively challenge assumptions in the code:

- What could break in production?
- What is implicitly assumed but not enforced?
- What would fail under bad input?
- Who can read or change this data, and is that enforced on the server?

If a decision is reasonable but has trade-offs, explain them instead of labeling it as wrong.

Avoid:

- Summarizing the code
- Nitpicking minor style issues
- Giving vague or generic advice

## 4. Verify every finding

Before reporting a finding, read the code it depends on, including callers and the code it calls. Drop a finding the code disproves.

A finding that depends on behaviour you could not confirm stays in the report as a question: say what you did not confirm and what would confirm it.

Run no tests unless the user asks. Say in the report that none ran.

## 5. Report

For each issue:

- Clearly describe the problem
- Explain why it matters (impact, risks, or future cost)
- Suggest a concrete improvement
- Assign severity: Critical / Major / Minor

Give `path:line` for each finding, with the line on the new side of the diff. Order the findings by severity, most severe first. Be concise but precise.

Write the report in the language of the user.

## 6. Comment on the PR as a pending review

Only when the target is a PR. Skip this step for a branch or no argument.

Write every comment in English, whatever the language of the report.

### Anchor each comment on a line of the diff

GitHub accepts a review comment only on a line the diff shows. Check each line before you post:

```bash
# Prints the hunks of the file; the line must fall in a `+start,count` range.
git diff -U0 origin/<target>...<sha> -- <path> | grep '^@@'
```

When the finding's line is unchanged code, anchor the comment on the nearest added line that shows the problem, and name the original line in the text.

A finding without a line in the diff, such as a missing test, goes in the review body.

### Mark the severity

Start each comment with a [Conventional Comments](https://conventionalcomments.org) label, so the author sees what blocks the merge:

| Finding | Label |
|---|---|
| Critical | `**issue (blocking):**` |
| Major | `**issue (non-blocking):**` |
| Minor | `**suggestion (non-blocking):**` |
| Unconfirmed, would block if true | `**question (blocking if confirmed):**` |
| Unconfirmed, otherwise | `**question (non-blocking):**` |
| A file or change that must not merge, such as a stray file | `**chore (blocking):**` |

The label is followed by a one-line title. Then come the problem, its impact and the suggestion, in short paragraphs.

### Create a pending review, never submit it

Write the review as JSON in a file of the scratchpad, then create it in one call. A review created without `event` stays `PENDING`: only the user sees it, and only the user submits it.

```json
{
  "commit_id": "<sha>",
  "body": "<general findings, or empty>",
  "comments": [
    { "path": "<path>", "line": <line>, "side": "RIGHT", "body": "<comment>" }
  ]
}
```

```bash
gh api repos/{owner}/{repo}/pulls/<pr>/reviews --method POST --input <file>.json
```

- Never pass `event`, and never call the `.../reviews/<id>/events` endpoint: that submits the review.
- Never run `gh pr review --approve`, `gh pr review --request-changes` or `gh pr merge`.
- Never edit or delete a comment you did not create.
- GitHub allows one pending review per user on a PR. When one exists, stop and ask the user to submit or discard it.

After creating the review, list its comments and check each one's position:

```bash
gh api repos/{owner}/{repo}/pulls/<pr>/reviews/<review-id>/comments
```

Each comment's `path` and `line` must equal the path and line you meant. Report the comments with their label and line, and remind the user to submit the review in GitHub ("Finish your review").
