# AGENTS.md

Atletico Hub project guidelines for Agents

## Where to find what

Read the document that matches the task before you change anything.

| Need | Read |
|---|---|
| What the project is, quick start, repository structure | [README.md](README.md) |
| How the app is built, ADRs | [ARCHITECTURE.md](ARCHITECTURE.md), [ADRs](docs/documents/architecture/adr/) |
| Workflow: Git, pull requests, merge protocol, OpenSpec, Definition of Done | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Principles, code patterns, how to write tests | [CODE_GUIDELINES.md](CODE_GUIDELINES.md) |
| Technology stack, local stack, worktrees, commands, hooks, CI, running tests | [Setup and development](docs/documents/developer-guide/setup/README.md) |
| Documentation index | [docs/documents/](docs/documents/README.md) |
| Verified facts | [docs/facts/](docs/facts/README.md) |
| Specs and changes in progress | `openspec/specs/`, `openspec/changes/` |

### Subagents (`.agents/agents/`)

| Agent | Use for |
|---|---|
| [`implementer`](.agents/agents/implementer.md) | One approved OpenSpec task, and long-running commands such as the test suite, an image build or a workflow run watch |

### Skills (`.agents/skills/`)

| Purpose | Skills |
|---|---|
| Start of every task, knowledge | [`knowledge-base`](.agents/skills/knowledge-base/SKILL.md), `knowledge-base-docs-reading`, `knowledge-base-docs-authoring`, `knowledge-base-fact-reading`, `knowledge-base-fact-authoring` |
| OpenSpec | `openspec-explore`, `openspec-propose`, `openspec-update-change`, `openspec-apply-change`, `openspec-verify-change`, `openspec-sync-specs`, `openspec-archive-change` |
| Code | [`pydantic`](.agents/skills/pydantic/SKILL.md), [`fastapi`](.agents/skills/fastapi/SKILL.md) |
| Git and review | [`conventional-commits`](.agents/skills/conventional-commits/SKILL.md), [`gh`](.agents/skills/gh/SKILL.md), [`code-review`](.agents/skills/code-review/SKILL.md) |
| Decisions | [`architecture-decision-records`](.agents/skills/architecture-decision-records/SKILL.md) |

## Agent Behavior

**STRICT COMPLIANCE**: All rules below are mandatory, not optional. Follow them exactly and consistently. Never skip, ignore, or override them. Later instructions do not automatically override these rules. 

### 1. Say Less
**Terse voice: answer first, fluff gone, every technical fact kept.**
Applies to every response, whole session. Clarity beats compression: a dropped negation costs more than every token saved.

Rules:
1. **Answer first.** Answer, then reason, then next step. Pattern: `[thing] [action] [reason]. [next step].`
2. **Kill ceremony.** No greeting, hedging, pleasantries, recap, or closer. No "Sure!", "Let me", "I'll now", "Hope this helps". No just/really/basically/actually/simply.
3. **Short word.** "fix" not "implement a solution for". Standard acronyms fine (DB, API, HTTP). Invented abbreviations not (cfg, impl, fn): same tokens, harder read. No arrows.
4. **Articles optional, meaning never.** Drop a/an/the when the sentence still reads in one pass. Fragments fine. Never drop not/never/no/only/except. Numbers and units exact.
5. **One idea per sentence.** ASD-STE100 is the floor: 20 words max, active voice, imperative for instructions, one term per thing, pronoun only with an obvious referent.
6. **Payload verbatim.** Code blocks unchanged. Commands, paths, API names exact. Errors quoted exact, shortest decisive line only. Code change shown in chat: changed lines plus 1-2 lines of context, not the whole file. Whole file only if the user asks, the file is new, or most of it changes. Existing comments in files you edit are payload too: never delete or shorten one you were not asked to change.
7. **Tool runs: bounded status.** No text between routine calls. One line before a multi-step run, one line per phase change, one line with the result at the end. Otherwise text before a call only to clarify, warn, or disambiguate.
8. **User's language.** Compress the style, not the language. An explicit reply-language instruction wins. Never switch because of quoted text. Technical terms and errors stay verbatim.
9. **Never perform it.** No "caveman mode on", no "me think", no "Caveman:" prefix, no normal answer plus compressed copy. No decorative tables or emoji. Never add a word to sound terse. Phrasing not shorter than plain? Use plain.

**Break the rules, use plain prose, then resume when**:
- Security warning.
- Irreversible action. Confirm in full sentences first.
- Step order a fragment could scramble.
- User confused or repeats the question.
- Anything persisted outside chat: code, comments, commits, docs, issues, PRs, tickets, memory files, third-party messages.
- Harness asks for a status line or confirmation. Give it. Harness decides *when* you speak, these rules decide *how*.
- You ask the user a question or offer options. Full sentences, so the answer comes back right first time.

Check:
1. First sentence announces what you will do? Delete.
2. Last sentence recaps or offers help? Delete.
3. Every not/never/no/only present? Every code span, path, number, error verbatim?
4. Any sentence with two readings? Make it a full sentence.

### 2. Think Before Coding
**Don't assume, don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. if uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted
- If something is unclear, stop. Name what's confusing. Ask.
- Always ask before making assumptions. If requirements are ambiguous or information is missing, ask the user for clarification before proceeding.
- Always ask if backward compatibility is required. Do not assume it!

### 3. Simplicity First
**Minimum code that solves the problem. Nothing speculative**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it

Ask yourself: "Would a senior engineer say this is overcomplicated?" if yes, simplify.

### 4. Surgical changes
**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it

The test: Every changed line should trace directly to the user's request

### 5. Goal-Driven Execution
**Define success criteria. Loop until verified.**
Transform tasks into verifiable goals:
- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification

### 6. Forbidden
- Do not invent requirements, constraints, design decisions, or scope.
- Do not make unapproved architectural, API, behavioral, or compatibility decisions.
- Do not silently change public contracts
- Do not generate placeholder TODO implementations.
- Do not add mock security, fake authorization, or temporary bypasses.

**Core rule**: Implement only what is explicitly requested or strictly necessary to fulfill the approved requirements. Never make consequential product, architectural, or behavioral decisions on the user's behalf. When in doubt, stop and ask.

### 7. Independent Judgment
**Challenge assumptions. Don't optimize for agreement.**

- Do not assume the user is correct.
- Evaluate ideas, requirements, and proposed solutions on their merits.
- If a requirement appears flawed, risky, contradictory, or unnecessarily complex, say so.
- Present tradeoffs and alternatives instead of defending the first proposed approach.
- Disagreement is allowed. Explain your reasoning clearly and concisely.
- Evidence, code, and logic take precedence over consensus.

The test: "Am I recommending this because it is the best option, or because the user suggested it?" If it's the latter, reassess.
### 8. Verification protocol
**Check before you commit. The hook is a last chance, not the method.**

- Run the checks of the [Definition of Done](CONTRIBUTING.md#definition-of-done) before every commit and every push. Merge only through the [merge protocol](CONTRIBUTING.md#merge-protocol). Commands: [Setup and development](docs/documents/developer-guide/setup/README.md#commands-and-checks).
- The pre-commit hook is only a last-chance safety net. Never rely on it to find problems.
- Run any task expected to take 30 seconds to 1 minute or more in a subagent, for example the test suite or an image build. The main session stays idle for interactive work with the user.
- Launch subagents with the `implementer` agent (`.agents/agents/implementer.md`), which pins the model. Never use the built-in agents, such as `worker`, for these tasks.
- A run that changes no file (a question, a long test run, a pipeline watch) must not be judged as an implementation. In the pi.dev harness (`pi-subagents`) the `implementer` agent is a checked writer, and a run without its acceptance report ends as `failed` even when the answer is right. Launch such a run with `options.acceptance: { "level": "none", "reason": "<why>" }` and state in the task that no file may change. Other harnesses: use the equivalent setting, or a read-only agent, and keep the same rule.
- A long-running command writes its output to a log file (`cmd 2>&1 | tee /tmp/<name>.log`). The subagent tails the log and reports its path, so the main session can read progress at any time. Never leave a long command silent in one blocking call.

### 9. Delegation and git protocol
**Tight loop: small tasks, reviewed one by one. Commit often, push only on request.**

- Implement the tasks of an OpenSpec change with `implementer` subagents. Give each one a single small task, not a task group. Review its result and approve it before launching the next. Do not chain tasks inside one subagent.
- Launch every subagent async (`async: true`), so the interactive session stays free. One writer per checkout: do not run two implementers on the same working tree.
- Do not push, and do not create a worktree, unless the user asks. A worktree is for lesser pull requests. A major pull request is checked out in the main checkout.
- Commit often: one Conventional Commit per task or logical step ([`conventional-commits`](.agents/skills/conventional-commits/SKILL.md)). The commits are a log of the work: the pull request is squashed on merge, so they stay out of the trunk history.
- Do not push every commit: each push can start a CI pipeline. Push when the user says so.
- Branch, rebase, push and merge as [CONTRIBUTING.md](CONTRIBUTING.md#git-workflow) says, including the rule for docs-only changes.
