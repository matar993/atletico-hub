---
name: knowledge-base-docs-reading
description: "Internal document-retrieval procedure, delegated by the knowledge-base skill for a selected corpus in docs/documents/."
allowed-tools: Read, Grep, Glob
---

# Knowledge base — docs reading

`docs/documents/` holds **document corpora** the user brought in and the agent ingested as
trees built for progressive disclosure: every level tells you which child to open next, so an
answer costs a few small file reads instead of one huge one.

The `knowledge-base` router selects the relevant corpus before loading this procedure.

## Layout

```
docs/
├── facts/                    ← verified facts, not documents
└── documents/
    ├── README.md             ← index of corpora
    └── <corpus>/
        ├── README.md         ← L1: scope, source, owner, last update + "When to read" table
        └── <section>/
            ├── README.md     ← L2: the section, or a summary + table of its children
            └── <subsection>/README.md   ← deeper levels only where a node was split
```

## Retrieval procedure — descend, do not scan

1. **Read the selected corpus `README.md`.** Note its scope and last-update date, then use its table
   ("When to read" / "When read it") to pick the section(s).
2. **Open only the selected section**, and follow its own table or links to deeper nodes and
   anchors. Cross-corpus links (e.g. interviewer circle → engineering ladder) are normal: follow
   them only when the question needs them.
3. **If the tables do not route you, grep `docs/documents/<corpus>/`** for the term as it
   appears in the source (keep the source language and spelling).
4. **Stop as soon as the question is answered.** Do not read sibling sections "for context".

## Using what you read

- Cite the node you used as a relative link with its anchor, so the user can verify.
- Respect markers the corpus defines (e.g. `TBD`, `TO REVIEW`): report them, do not resolve them
  by inference.
- **Check the corpus last-update date** and any stated release cadence (e.g. the ladder is
  released every six months). If the document may be outdated for the question, say so.
- Report what the document says; do not extend it with general practice or guesses.

## Result

Return the answer and source node, or any gap, pending source, or correction, to the
`knowledge-base` router.
