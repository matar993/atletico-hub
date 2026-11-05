---
name: knowledge-base
description: "Use at the START of every task, before discovery or questions, and whenever reading, ingesting, updating, correcting, or retiring knowledge. This is the single entry point for documents and verified facts"
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Knowledge base

`docs/` is the central place where all of your verified hard knowledge lives. It contains both documents and verified facts.

There are two different knowledge entities: documents and verified facts.
- `docs/documents/` are structured files that contain detailed information on a specific topic.
- `docs/facts/` are individual pieces of information that have been confirmed to be accurate and reliable.


## Read knowledge

1. Read the fact using the skill `knowledge-base-fact-reading`
2. Read the documents using the skill `knowledge-base-docs-reading`

## Write or Update knowledge


1. Do not duplicate information. Always check existing documents and facts before adding new facts or documents.
2. If facts of document exists you should update the existing ones rather then create a new one.

### Document

Docs are updated automatically as part of every task, without asking the user.

1. Before finishing a task that changes behaviour, adds a feature, or makes a node false, update or add the affected docs using the skill `knowledge-base-docs-authoring`.
2. A document the user hands over on the spot is ingested with the same skill.

## Fact

1. A costly new fact is discovered: it must be added using using the skill `knowledge-base-fact-authoring`
2. A Fact is contraddicted by a fresh source, trust the source, tell the user and update it using the standard using the skill `knowledge-base-fact-authoring`
