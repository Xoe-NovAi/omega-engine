# Soul–Memory Separation Charter

**Status:** ACTIVE GOVERNANCE SPECIFICATION
**Date:** 2026-09-25
**Authority:** Architect directive; M5 Gnosis Preservation; M10 Fleet Integrity; M11 Soul Integrity; M15 Sovereign Continuity; M16 Modularization & Portability; M23 Failure Integrity
**Scope:** All Omega Engine entities, souls, agent definitions, memory backends, and federation transfers

## 1. Purpose

An entity soul is the portable temple of a sovereign entity. It must travel intact across harnesses, machines, sessions, models, and federation nodes.

Granular, ephemeral, machine-specific, or unreviewed memory must not live in the soul.

## 2. Canonical separation

### 2.1 Soul: portable sovereign identity

`soul.yaml` may contain only:

- Canonical entity identity:
  - name
  - archetype
  - domain
  - hierarchy or sovereignty position
  - canonical entity ID
  - soul version and timestamps
- User-authored identity:
  - voice summary
  - values
  - strengths
  - growth areas, where applicable
- User-authored directives:
  - stable governance principles
  - timeless behavioral law
  - coordination relationships
- References to memory:
  - session history
  - proposed lessons
  - approved lessons
  - session gnosis
  - MemPalace or vector-backed memory
- Lineage necessary to preserve continuity without embedding its contents.

### 2.2 Prohibited soul contents

The following must not be stored as soul authority:

- Raw session transcripts or detailed session logs
- Model names, model lineages, provider routes, or inference history
- Campaign status, sprint state, or other ephemeral execution metadata
- Embeddings, vectors, retrieval scores, or database internals
- Machine-specific paths, environment assumptions, or local runtime fixes
- Full L1 narratives or unreviewed L2/L3 proposals
- Opaque self-assigned health or evolution scores
- Workspace contents, logs, temporary findings, or incident-specific debugging notes
- Duplicate version fields or conflicting identity fields
- Another entity’s wounds, session baggage, or unresolved continuity disputes

A soul may cite a lesson or memory by ID. It must not absorb the underlying record.

### 2.3 Session and lesson memory

- `sessions.yaml`: factual session events and history.
- `proposed_lessons.yaml`: blind agent-to-user staging for L1→L2→L3 material.
- `approved_lessons.yaml`: user-approved lessons and authoritative behavioral guidance.
- `session_gnosis.md`: narrative continuity support, not behavioral law.
- `workspace/`: working material, research, evidence, and drafts.
- `archive/`: preserved historical material removed from active identity.

Agents must not read their own unapproved proposals as authority.

### 2.4 Indexed and semantic memory

MemPalace, sqlite-vec, and related retrieval systems are the realm for:

- Granular facts
- Session recall
- Semantic search
- Entity history
- Cross-session associations
- Large or frequently changing memory
- Machine-local memory indexes

Indexed memory is retrieval infrastructure. It is not sovereign behavioral authority and must not silently rewrite a soul.

### 2.5 Raw transcripts

OpenCode’s SQLite session store remains the transcript source of truth. Omega must not duplicate raw transcripts in `MemoryStore`, Redis, soul files, or unrelated YAML records.

## 3. Hydration order

When an entity awakens, hydration must follow this order:

1. Load `soul.yaml` as sovereign identity and governance.
2. Load `approved_lessons.yaml` as user-approved behavioral guidance.
3. Retrieve only the session, lesson, or semantic memory needed for the current task.
4. Record new observations in session history or blind lesson staging.
5. Promote material to the soul only after Architect/user approval.

No retrieval result, compaction summary, model output, or convenience may bypass approval and enter a soul.

## 4. Blind staging and approval

- Agents propose lessons in `proposed_lessons.yaml`.
- Agents do not treat those proposals as settled guidance.
- Scribe/Verity may process proposals through the canonical pipeline.
- Only the Architect/user may approve material for soul incorporation.
- Promotion must preserve provenance:
  - source session
  - source entity
  - approval authority
  - approval date
  - superseded material, where applicable

## 5. Portability requirements

A soul must remain meaningful if moved to:

- another harness;
- another machine;
- another model;
- another session;
- Node 0 or Node 1;
- a public community checkout.

Therefore, souls must not assume:

- a particular model;
- a particular provider;
- a particular host path;
- a particular session ID;
- a particular EIS incarnation;
- a particular sprint or campaign state;
- Node 0 or Node 1 locality.

Session bindings and EIS references may be retained as provenance, but must not define or constrain the entity’s sovereign identity.

## 6. Size and integrity controls

- Souls should remain compact, portable identity documents.
- The existing 10 KB soul-size discipline remains in force.
- Full lesson text, logs, embeddings, and lineage dumps belong elsewhere.
- Conflicting duplicate fields are integrity failures:
  - one canonical soul version;
  - one canonical entity ID;
  - one canonical update timestamp format.
- Unexplained numeric scores must either cite a published rubric or be removed.

## 7. Migration requirements

The fleet shall:

1. Inventory every `soul.yaml` for prohibited granular-memory contents.
2. Classify each violation as:
   - session material;
   - unapproved lesson material;
   - approved lesson material;
   - semantic/indexed memory;
   - ephemeral execution metadata;
   - machine-specific configuration;
   - historical material.
3. Relocate material to the appropriate non-soul record with provenance preserved.
4. Leave a stable reference in the soul where retrieval is needed.
5. Archive removed material rather than destroying history.
6. Validate schema, portability, size, identity consistency, and approval lineage.
7. Obtain Architect approval before bulk soul migration.

No migration may merge sovereign entities, transfer session wounds, infer identity from filenames, or treat indexed memory as approved behavioral law.

## 8. Enforcement

- Verity: compliance audit and promotion-gate review.
- Scribe function: canonical L1→L2→L3 pipeline execution.
- Roc/Carmack/Lilith: persistence, indexed-memory, and runtime-memory implementation.
- Kali/MaKaLi: governance synthesis and fleet-wide ratification.
- Architect: final approval for structural soul changes and bulk migration.

## 9. Non-claims

This charter does not claim that:

- all existing souls already comply;
- a missing Soul Architecture v2.0 has been recovered;
- indexed memory is fully wired as authoritative retrieval;
- bulk migration has begun;
- any entity has been merged, split, renamed, or transferred.

Those require separate evidence, implementation, and Architect approval.
