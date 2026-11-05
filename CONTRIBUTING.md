# Contributing

How to propose, check and merge changes to the Atletico Hub repository: Git, pull requests, OpenSpec and the Definition of Done.

- Code principles, patterns and how to write tests: [CODE_GUIDELINES.md](CODE_GUIDELINES.md).
- Technology stack, local stack, worktrees, commands, hooks, CI and how to run the tests: [Setup and development](docs/documents/developer-guide/setup/README.md).

---

## Git workflow

We follow a `develop` branch with release branches ([ADR-0001](docs/documents/architecture/adr/0001-develop-branch-with-release-branches.md)). The repository is on GitHub: [matar993/atletico-hub](https://github.com/matar993/atletico-hub).

- Branch from `develop`, and rebase on `origin/develop`: `feat/<topic>`, `fix/<topic>`, `chore/<topic>`, `docs/<topic>`, `build/<topic>`, `ci/<topic>`. Every pull request targets `develop`, or the branch below it in a stack.
- A fix for a release lands in `develop` first, then is cherry-picked with `git cherry-pick -x` into the release branch `release/vX.Y`.
- A release is a tag `vX.Y.Z` on its release branch.
- Pull requests are always squashed: each becomes one commit on `develop`. Its title is the commit subject. Merge with the full commit message: subject, body, and a `Pull request: <URL>` footer (see the [`gh`](.agents/skills/gh/SKILL.md#ready-update-and-merge) skill).
- A pull request description has two sections: **Why** and **What it brings** (`.github/pull_request_template.md`).
- Docs-only changes (OpenSpec artifacts, ADRs, documentation, skills) need no skip flag: the CI workflow runs only the jobs of the areas a change touches. Never use `[skip ci]`: it also skips `ci-ok`, the required check, and the pull request cannot merge.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/) (see `.agents/skills/conventional-commits`). Mark breaking changes with `!` and a `BREAKING CHANGE:` footer.
- Put the OpenSpec change id in the commit body and in the pull request description, for example `Change: add-player-roster`.
- Stage files by name, never a whole folder: local files such as `.tokensave/` must not reach a commit.
- Write every document (README, CONTRIBUTING, docs/, OpenSpec artifacts, skills), every comment and every commit in English.

### Branch protection

`develop` and `release/**` are protected on GitHub: changes arrive only through pull requests, the `ci-ok` check must pass, and one approval of another developer is required. Only squash merges are allowed.

### Stacked pull requests

A large piece of work is split into small pull requests, each readable on its own.

- Keep one phase of work in a stack at a time: merge it into `develop` before opening the next phase.
- When a pull request is merged, retarget the next one to `develop` (`gh pr edit <pr> --base develop`) and rebase it. The one below was squashed, so skip its original commits: `git rebase --onto origin/develop <branch-below> <branch>`.

---

## Agentic workflow

Changes are planned and implemented by a coding agent with [OpenSpec](https://github.com/Fission-AI/OpenSpec); humans review and decide. Specs live in `openspec/specs/<capability>/spec.md`, work in progress in `openspec/changes/<change-id>/`, finished work in `openspec/changes/archive/`.

Every change that alters behavior follows these steps:

1. **Propose**: `/openspec-propose`. Check `openspec list --specs` first and reuse existing capabilities.
2. **Review**: open a pull request with the change alone, or with its first commits, and agree on it before most of the code.
3. **Apply**: `/openspec-apply-change`.
4. **Verify** (optional): `/openspec-verify-change`.
5. **Archive**: `/openspec-archive-change`, in the pull request that implements the change. Never archive a plan in a separate pull request.

Pure refactors, tooling and docs may skip OpenSpec, or use a change with `skip_specs: true`. Ideas not ready for a change go to GitHub issues (template `Idea`).

Decisions that span the whole project are recorded as ADRs in `docs/documents/architecture/adr/` (skill `architecture-decision-records`); decisions of a single change stay in its `design.md`.

---

## Delegation to subagents

The rules (agent, one task per subagent, async, one writer per checkout) are in [AGENTS.md](AGENTS.md#9-delegation-and-git-protocol). The handoff to an `implementer` holds:

- the text of the task, copied from `tasks.md`;
- the files to read: the change artifacts and the code the task touches;
- the test layout of [CODE_GUIDELINES.md](CODE_GUIDELINES.md#tests);
- the commands to run and report, from the [Definition of Done](#definition-of-done);
- the report format of the [`implementer`](.agents/agents/implementer.md) agent: changed files, tasks completed, validation results, deviations, risks.

The main agent reviews each result before it launches the next task.

## Definition of Done

- Before every commit on backend code, run `make lint-fix`, `make autoformat` and `make typecheck`, and fix every failure.
- Before every push of code changes, run `make test` and fix every failure. Skip it when the commits since the last green run change only docs, comments or other chores that cannot affect the code, or when a maintainer asks to skip it: the CI workflow is the final safety net. The 90% coverage floor stays (see [Commands and checks](docs/documents/developer-guide/setup/README.md#commands-and-checks)).
- `make ui-checks` and `make ui-e2e` pass when the web app changes.
- After a change to an API route, `make ui-gen-api` ran and `frontend/src/lib/api/schema.d.ts` is committed.
- Code follows [CODE_GUIDELINES.md](CODE_GUIDELINES.md) and the architectural boundaries of [ARCHITECTURE.md](./ARCHITECTURE.md).
- The documentation is up to date with the change: `README.md`, `CONTRIBUTING.md`, `CODE_GUIDELINES.md`, `AGENTS.md`, `docs/` and the skills describe the repository as it is after the merge. A new feature has its page in the [user guide](docs/documents/user-guide/README.md).
- The OpenSpec change, if any, is archived in the same pull request as its implementation, so `openspec/specs/` describes the new behavior. Never archive in a separate pull request.
- `make validate` passes.
- A project-wide decision taken or changed by the pull request is recorded as an ADR, or its ADR is updated or superseded.

### Merge protocol

The rules above hold at merge time. Do these steps in order. The agent merges only when the CI workflow is green and every step is done.

1. Take the pull request out of draft: `gh pr ready <pr>`.
2. Update the pull request description so it covers all the changes: `gh pr edit <pr> --body-file -`.
3. Close every open point of the current session. Read the threads on the pull request with `gh pr view <pr> --comments` and resolve each one.
4. Rebase on the latest `develop`, or on the branch below it in a stack: `git fetch origin develop && git rebase origin/develop`.
5. Run the checks of this section again on the rebased branch.
6. Push every commit, with `git push --force-with-lease` after a rebase. `git status -sb` shows the branch level with its remote.
7. Check that the OpenSpec change is archived in this pull request (see [Agentic workflow](#agentic-workflow)).
8. Review the final diff with the [`code-review`](.agents/skills/code-review/SKILL.md) skill.
9. Write the squash commit message (see [Git workflow](#git-workflow)).
10. Get the user's review of the pull request, the approval of another developer, and the authorization to merge.
11. Check that the CI workflow ran on the latest commit. An `implementer` subagent monitors it (`gh pr checks <pr> --watch`) and reports when it ends.
12. Merge with the command of the [`gh`](.agents/skills/gh/SKILL.md#ready-update-and-merge) skill.
