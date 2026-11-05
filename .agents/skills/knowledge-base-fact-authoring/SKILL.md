---
name: knowledge-base-fact-authoring
description: "Internal fact-maintenance procedure, delegated by the knowledge-base skill to record, correct, or retire a selected verified claim."

allowed-tools: Read, Write, Edit, Grep, Glob
---

# Knowledge base — fact authoring

`docs/facts/` is the agent's own persistent memory of **verified hard facts**, built up as it works.
It is domain-agnostic: whatever tools, sources, and conventions the agent meets, a fact that was
costly to discover goes here. It exists to kill the cost of rediscovery: a fact written once is
read in one file read forever after.

> **An unverified claim here is worse than silence.** It persists, so it is trusted. If you
> cannot state how you verified it, either verify it now or do not write it.

The `knowledge-base` router selects this operation and handles requests belonging to another layer.

## Admission tests — all four must hold

1. **Hard** — a concrete claim (an identifier, a field meaning, a rule, a location, a tool
   behaviour), not an opinion, a plan, or a guess.
2. **Verified** — confirmed against a source; the note says which, with a date. Valid sources:
   - the output of a tool or command you ran (state the command);
   - a document or web page (state the URL or path);
   - an explicit statement by the user (quote it).
   An inference of yours is **not** a source.
3. **Durable** — still true next week. Live state (current statuses, schedules, counts, who is
   doing what now) fails this test: re-read it from its source each time.
4. **Costly to rediscover** — took several calls, searches, or a question to the user. If a single
   lookup returns it directly, it does not belong here.

Fail any one → do not write it. Keep the bar high. A thin layer that is fully trusted beats a
thick one that is not.

## Never write

- **Personal data**: names, contacts, evaluations, salaries, health or private details about
  people. Use roles or stable opaque IDs only when the ID itself is the fact.
- **Secrets**: tokens, credentials, private links with access keys.
- **Snapshots of data**: lists, counts, or states at a given date.
- **Copies of existing docs**: if it is written down in a source — including a node in
  `docs/documents/` — link to it instead.

## Write as you go, report it

Write the note **as soon as** the fact passes the tests — do not wait for the end of the task, or
it will be lost. Do not interrupt the user to ask. At the end of your reply, list in one line each
the notes you created, changed, or deleted, so the user can object.

## Before writing: check it is not already there

Use the existing notes located by the router's reading operation. If a note already covers the fact, **update that note**
instead of adding a second one. One fact, one note.

## Layout

```
docs/
└── facts/
    ├── README.md        ← index of areas, the four tests, start-here notes
    └── <area>/
        ├── README.md    ← what belongs here and what does not + index of its notes
        └── <kebab-case-claim>.md
```

Areas emerge from the facts: name one after the tool, source, or topic the facts are about. Create
an area only when its first fact arrives — the point is that a new fact has an **obvious home**.
Every folder carries a `README.md` stating what belongs in it *and what does not*, plus an index of
its notes. Read that before adding.

## Operations

### Write a fact

1. Apply the four tests and the "never write" list.
2. Pick the area; read its `README.md` to confirm the fact belongs there.
3. Create `docs/facts/<area>/<kebab-case-claim>.md`:

```markdown
---
name: <the claim, as a sentence>
description: <one line — what a reader GAINS, not what the note is "about">
type: reference | gotcha | practice
verified: YYYY-MM-DD
---

## The fact

<the claim, stated concretely — exact names, identifiers, syntax, titles, error strings>

## Why it matters

<what it costs to get wrong: a wrong answer, wasted calls, a rule misapplied>

## How this was verified

<source and date — the command and what it returned, the URL/path, or the user's quote>
```

- **Name the file by what someone would search for**: the thing, field, or question — not the
  conversation you hit it in.
- **One fact per note.** If the title needs "and", it is two notes.
- Use `##` sections so the note can be anchor-linked.
- Include the strings a future grep will actually use: names, keys, terms in the language they
  appear in.

4. **Add the note to its area `README.md` index**: one line, ≤120 characters, a hook that helps a
   reader decide whether to open it — never a summary of it.
5. Add it to the charter's start-here list **only if it would change the first move on a
   request where you would not know to look for it**. That bar is high; most notes do not clear it.

### Correct or retire a fact

When a note is contradicted by a fresh source — including a newly ingested or updated document in
`docs/documents/` — trust the source, tell the user, and fix the note
right away:

- **Contradicted but still a useful lesson** → keep it, retitle around the transferable part, state
  plainly at the top what changed and when, bump `verified`.
- **Simply wrong or obsolete** → delete it. Prefer deleting to hedging.
- **Only names/IDs/URLs moved** → fix them and bump `verified`.

Either way, update the area index and any note linking to it. **Never leave a half-true note.**

### Sweep before finishing a task

Ask: *would I have to redo any of these calls, searches, or questions next time?* Look for things
that took several attempts to understand, information that was hard to locate, rules the user had
to explain, and corrections to something previously believed. Write what passes the tests. Skip
narrative, one-off answers, and anything unverified.

### Re-verify stale notes

External tools and documents change without notice. When you rely on a note whose `verified` date
is old, re-check it cheaply against its source first; if it no longer holds, apply "Correct or
retire".

## Where a fact goes

```
Live/changing state?                          → its source; re-read it, NOT here
Personal data or secrets?                     → nowhere
A document the user brought to organise?      → return to the knowledge-base router
Already written in a doc, page, or skill?     → nowhere; link to it instead
Verified + durable + costly to rediscover?    → docs/facts/  (this skill)
```

**Do not mirror documentation into `docs/facts/`.** It will drift, and a drifted note is
trusted. A note *pointing* to the right page or document node for a recurring question is fine.

## Checks before saving

- Frontmatter complete: `name`, `description`, `type`, `verified`.
- The `name` is a claim, and the filename matches it in kebab-case.
- Every claim has a stated source — no "should", no "presumably", no inference of yours.
- The note appears in its area index; every relative link resolves.
- No personal data, no secrets, no data snapshots.

## Bootstrapping

If `docs/facts/` does not exist, create the one area folder your first fact needs —
`docs/facts/<area>/` with its own `README.md` — and add the area to the facts index in
`docs/facts/README.md`. Do not scaffold areas speculatively.

Return results and any required follow-up operation to the `knowledge-base` router.
