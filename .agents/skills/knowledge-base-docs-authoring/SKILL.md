---
name: knowledge-base-docs-authoring
description: "Use after any change that alters documented behaviour or adds something worth documenting, and when the user hands over a document: update the affected docs or add new ones."
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Knowledge base — docs authoring

`docs/documents/` holds **document corpora**; `docs/facts/` holds verified facts.

**Every write optimises future reading.** A reader must reach any answer by descending a few small
nodes, each telling them which child to open next. A faithful but monolithic document fails this.

> **Faithful to the truth.** The truth is the code, the tests, the user's statement, or a source you
> can name. Never invent, soften, or "improve". A document that says more than its source is worse
> than a document that says less. Mark gaps with `TBD` instead of filling them.

## Docs are part of the task — no one asks for them

Updating docs is a step of the work, not a follow-up. Do it automatically, in the same change as the
code, without asking the user. Before finishing any task, ask: *does a reader of `docs/documents/` now get a
wrong or missing answer?*

| Situation | Action |
|---|---|
| Change alters behaviour, API, config, or a flow that a node describes | Update that node, in the same change |
| Change makes a node false or obsolete | Fix it or [retire](#retire) it; never leave it half-true |
| New feature, component, or concept with no home | Add a node (or a corpus) following the tree rules |
| Architectural decision with alternatives and consequences | Write an ADR with the `architecture-decision-records` skill, then link it from the relevant node |
| User hands over a document or a page to keep | Ingest it on the spot (see [Ingest](#ingest-a-source)) |
| Pure refactor, test-only change, or no behaviour change | Do nothing |

Locate the affected nodes with the router's reading operation, not by scanning `docs/documents/`.

## Admission

Content is admitted when:

1. **It has a known source** — the code, a test, the user's statement, or a page/file you can name
   (URL or path). Record the source when it is external.
2. **It is readable with the available tools.** If a format cannot be read, stop and tell the user.
   Do not write scripts to convert it.
3. **It is durable reference material**, not live state (current queues, who is doing what now,
   counts at a date). Live state stays in its source.

## Never write

- **Secrets**: tokens, credentials, private links with access keys. Drop them and tell the user.
- **New personal data**: names, contacts, evaluations, salaries, health details. Use roles unless
  the user explicitly says otherwise. Flag it to the user.
- **Your own inferences** presented as document content. Mark gaps with `TBD`.
- **Task narrative**: what you did, how, in which order. Docs describe the system, not the work.

## Tree rules

```
docs/documents/<corpus>/
├── README.md                    ← L1
└── <section>/
    ├── README.md                ← L2
    └── <subsection>/README.md   ← only when a node is split
```

- **Corpus = one coherent body of material**, kebab-case, named after what a reader would look for.
- **No numeric prefix on folders.** Keep existing folder names; order lives in the parent's reading
  table. Renaming a folder means fixing every link to it, so do not rename without need.
- **L1 `README.md`** opens with: title, one-line purpose, a metadata block (source, owner role if
  known, last update, scope, corpus markers such as `TBD`/`TO REVIEW`), then a reading table
  `| Node | When to read it |` linking every section. Nothing else heavy.
- **A node is a folder with a `README.md`, or a leaf page `<name>.md`** (no children) linked from the
  reading table of its parent `README.md`. ADRs are leaf pages. A leaf page that must be split becomes
  a folder; fix every link to it. Use `##` headings so nodes are anchor-linkable.
- **Split rule:** when a node exceeds roughly **200 lines** or mixes topics a reader would want
  separately, split it into child folders. The parent keeps a short summary and a reading table of
  its children.
- **Reading-table hooks** are ≤120 characters and say *when* to open the node — not a summary of it.
- **One home per paragraph.** Every piece of content lands in exactly one node; other nodes link to
  it. Duplication drifts.
- **Relative links only** within and across corpora; every link and anchor must resolve.
- Keep the source's language and terminology: future greps use its words.

## Operations

### Update a corpus

1. Edit the affected nodes in place; respect the one-home rule. Split nodes that now exceed the
   split rule.
2. Update the L1 last-update date, and any reading table whose hooks changed.
3. Verify links.
4. If the change contradicts a note in `docs/facts/`, report it to the router.

### Add a node or corpus

1. Check `docs/documents/README.md`: does it belong to an **existing corpus**? If yes, add a section there —
   do not create a parallel corpus.
2. Design the tree: list sections and the reading question each answers; apply the split rule.
3. Write L1, then each node.
4. Add the new corpus to the index in `docs/documents/README.md` with a ≤120-char hook, and the new section to
   its parent's reading table.
5. Verify links.

### Ingest a source

For a document or page the user hands over on the spot (a file path, a URL, pasted text):

1. Read the whole source. Check admission and the "never write" list.
2. Follow [Add a node or corpus](#add-a-node-or-corpus). Move content, do not paraphrase it away.
3. **Verify coverage**: walk the source section by section and confirm every part has a home in the
   tree (or was deliberately dropped under "never write" — say which).
4. Leave the original where it is. Delete it only if the user asks.

### Retire

- **A section is obsolete** → delete the node, remove it from its parent's reading table, and fix
  every link pointing to it. If the corpus keeps history on purpose (e.g. ADRs), keep it and mark
  its status instead.
- **A whole corpus is obsolete** → confirm with the user, then delete it and its index line.

## Report

At the end of your reply, list in one line each the nodes created, changed, moved, or deleted, and
anything flagged (personal data, unreadable formats, content dropped).

## Checks before finishing

- Every node is a folder with a `README.md` or a leaf page linked from its parent; no node exceeds the split rule without reason.
- L1 has its metadata block and a reading table covering every section.
- Every statement traces to the code, a test, the user, or a named source; nothing invented.
- All relative links and anchors resolve; `docs/documents/README.md` lists every corpus.

Return results and any required follow-up operation to the `knowledge-base` router.
