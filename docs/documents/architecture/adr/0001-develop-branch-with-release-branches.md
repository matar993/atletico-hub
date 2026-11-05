# ADR-0001: `develop` branch with release branches

**Date**: 2026-11-05
**Status**: accepted
**Deciders**: Marco Scalzo

## Context

The app is developed mostly with coding agents. The repository needs a branching model that keeps integration continuous, makes releases explicit and keeps every pull request small enough to review. The team already knows this flow from other projects.

## Decision

`develop` is the default branch and the integration branch: every pull request targets it, or the branch below it in a stack of pull requests, and is squash-merged. A release is cut from `develop` as `release/v<major>.<minor>` and tagged `v<major>.<minor>.<patch>` there. A fix for a release lands in `develop` first and is cherry-picked into the release branch ("upstream first").

## Alternatives Considered

### Alternative 1: Trunk-based development on `main` without release branches
- **Pros**: one branch, the simplest flow
- **Cons**: a released version cannot get a fix without shipping everything merged since
- **Why not**: released versions must stay supportable while the next one is built, and the team already knows this flow

### Alternative 2: Git Flow
- **Pros**: well known, explicit release and hotfix branches
- **Cons**: a second long-lived branch (`master`), hotfix branches and the double merge into `master` and `develop` add ceremony and merge conflicts
- **Why not**: release branches with upstream-first cherry-picks give the same support with one long-lived branch and fewer merges

## Consequences

### Positive
- `develop` always holds the latest integrated work; each release is a tag, with its own branch for fixes
- The squash merge keeps one commit per pull request on `develop`

### Negative
- A fix for a release needs two merges: into `develop`, then a cherry-pick into the release branch

### Risks
- A fix applied only to a release branch is lost in the next release. Mitigation: upstream first, and `git cherry-pick -x` so the origin of each fix stays traceable
