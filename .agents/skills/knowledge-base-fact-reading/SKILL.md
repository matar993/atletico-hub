---
name: knowledge-base-fact-reading
description: "Internal fact-retrieval procedure, delegated by the knowledge-base skill for a selected area in docs/facts/."
allowed-tools: Read, Grep, Glob
---

# Knowledge base — fact reading

The `docs/facts/` directory holds **verified hard facts** the agent collected while working, that
were expensive to discover the first time: how a tool or data source actually behaves, where some
information lives, rules and conventions the user stated.

**The point of reading it first is cost.** Rediscovering a fact costs several tool calls, a document search, a wrong assumption, or a question the user already answered once. Reading a note costs one
file read.

> If a note contradicts what you are about to assume, the note wins until you disprove it —
> then return the correction to the `knowledge-base` router.

The `knowledge-base` router selects the relevant fact area before loading this procedure.

## Layout

```
docs/
└── facts/
    ├── README.md        ← index of areas + start-here notes
    └── <area>/
        ├── README.md    ← what belongs in this area and what does not + index of its notes
        └── <kebab-case-claim>.md
```

Areas emerge from the facts collected so far; use the area selected from the index.

If `docs/facts/` does not exist yet, report that there is nothing to read to the router.

## Retrieval procedure — cheapest first

1. **Read the `README.md` of the selected `facts/` area.** It indexes that area's notes with a
   one-line hook each — enough to decide what to open.
2. **Open only the notes the hooks point at.** Notes are one fact each and short by construction.
3. **If the indexes do not answer you, grep `docs/facts/`** by what you are actually dealing with: an
   error message, a field or resource name, a term from a document, the name of a rule. A note may
   exist without an index line — grep is how it is reached.
4. **If no note answers the question, report the gap to the router.**

Stop as soon as you have the fact. Do not read the whole layer.

## Reading a note

Every note carries frontmatter:

```yaml
name: <the claim, as a sentence>
description: <what a reader gains>
type: reference | gotcha | practice
verified: YYYY-MM-DD
```

- `name` **is the claim.** If the title answers your question, you may not need the body.
- The body states the fact, why it matters / what it costs to get wrong, and a
  `## How this was verified` section naming the source (command, document, or user quote) and date.
- **Check `verified`.** External tools, documents, and team conventions change without notice. An
  old note deserves a cheap re-check against its source before you act on it.

## Result

Return the answer and source note, or the gap, stale evidence, or contradiction, to the
`knowledge-base` router. Say briefly which note answered the question in the user's response.
