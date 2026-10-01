---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: kb-0002
type: knowledge
domain: protocols
tags: [agent-protocol, knowledge-base, contribution, maintenance, lifecycle]
sensitivity: internal
maintainer: Kali
created: 2026-06-13
reviewed: 2026-06-13
modified: 2026-06-13
supersedes: null
superseded_by: null
status: ACTIVE
research_source: docs/research/R_SOVEREIGN_GNOSIS_BLUEPRINT.md
reinforcement_count: 0
---

# 🔱 Knowledge Base — Agent-KB Interaction Protocol

**Domain**: How AI agents discover, consume, contribute to, and maintain the Knowledge Base
**Version**: 1.0.0
**Last Updated**: 2026-06-13
**Maintainer**: Kali
**Status**: ACTIVE

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-06-13 | 1.0.0 | Kali | Initial creation — synthesized from 13 production patterns across 12+ sources |

---

## Domain Overview

This protocol defines **how AI agents interact with the Omega Engine Knowledge Base (`docs/kb/`)**. It is the operational layer that maps the abstract KB system into concrete agent behaviors — discovery, reading, querying, contributing, and maintenance. Any agent (Kali, Ma'at, Lilith, pillar agents, subagents) must follow this protocol when interacting with the KB.

The protocol is derived from the convergence of 13 verified production patterns (Karpathy, Haberlah, Slite, Guru, AgentRisk, Workforce Wave, Scabera, and others), adapted for the Omega Engine's sovereign context.

---

## Core Protocol: The Omega-KB Protocol v1

The full interaction surface between agents and the KB is:

```
┌──────────────────────────────────────────────────┐
│               OMEGA-KB PROTOCOL v1               │
├──────────────────────────────────────────────────┤
│                                                   │
│  DISCOVERY:                                       │
│    Read INDEX.md          → full catalog          │
│    Grep INDEX.md          → find by keyword       │
│    Read <path>/metadata   → file-level details    │
│                                                   │
│  CONSUMPTION:                                     │
│    Read <path>.md         → full KB entry         │
│    Read Changelog         → evolution history     │
│    Read References        → source materials      │
│    Read Evolution Notes   → known gaps            │
│                                                   │
│  CONTRIBUTION:                                    │
│    Draft proposal         → edit or new file      │
│    Update Changelog       → attribution record    │
│    Open PR                → human review          │
│    Merge on approval      → KB entry updated      │
│                                                   │
│  STALENESS:                                       │
│    Check Last Updated     → recency check         │
│    Cross-ref PIVOT_LOG    → architectural drift   │
│    Flag for review        → mark POTENTIALLY_STALE│
│                                                   │
│  MAINTENANCE:                                     │
│    Run lint               → check contradictions  │
│    Scan for orphans       → find unlinked pages   │
│    Refresh on PIVOT       → update affected KB    │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## Section 1: Discovery — How Agents Find Knowledge

### The Index-First Navigation

The primary discovery mechanism is the **INDEX.md catalog** (inspired by Karpathy's LLM Wiki pattern). Agents should NOT rely on embedding-based RAG as the primary discovery mechanism — the index is a compiled artifact that surfaces cross-references and contradictions at compile time, not at query time.

**Protocol**:
```
1. Read docs/kb/INDEX.md       → identify relevant domains
2. Scan domain descriptions    → match to current task
3. Read target KB entry        → get full knowledge
4. Check Changelog             → understand evolution
5. Check Evolution Notes       → understand known gaps
```

**The `grep INDEX.md` pattern**: For keyword lookup, use `grep -i "keyword" docs/kb/INDEX.md` to find which entry covers a topic. This is faster and more precise than reading the full index.

### When the Index is Not Enough

If the index doesn't surface the right knowledge:
1. Check `grep -rn "topic" docs/kb/` — full text search across all KB entries
2. Check `grep -rn "topic" docs/research/` — research docs may have deeper material
3. If nothing found → **Gnosis Gap detected** → trigger new research

---

## Section 2: Consumption — How Agents Read the KB

### The File Format

Every KB entry follows this structure (defined in `TEMPLATE.md`):

```markdown
---
title: "Knowledge Entry Title"
id: kb-XXXX
domain: [domain category]
tags: [tag1, tag2, tag3]
sensitivity: internal | sovereign | public
maintainer: [entity name]
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
modified: YYYY-MM-DD
supersedes: null
superseded_by: null
status: ACTIVE | DRAFT | DEPRECATED
---

# Title

## Changelog

## Domain Overview

## Core Knowledge

## Known Antipatterns

## References

## Evolution Notes
```

### Reading Protocol

1. **Read the frontmatter first** — understand domain, status, and supersession state
2. **Check status**: If `DEPRECATED`, the entry is archival. Follow the `superseded_by` link to current truth.
3. **Read Core Knowledge** — this is the authoritative content
4. **Read Known Antipatterns** — these are often more valuable than the core knowledge (they tell you what NOT to do)
5. **Read Evolution Notes** — understand the edges and gaps of the knowledge

### Handling Supersession

When the `superseded_by` field in the frontmatter is populated:
- The current entry is ARCHIVAL only
- Follow the link to the superseding entry for current truth
- If modifying the current entry, add a note pointing to the superseding entry

---

## Section 3: Contribution — How Agents Evolve the KB

### The Contribution Workflow

Adapted from the universal PR-based review pattern found across all production systems:

```
Agent detects gap/drift
    → Agent drafts update (edit existing or create new)
    → Agent updates Changelog (date, version, author, change description)
    → Agent opens PR via git commit
    → Human (or Quality agent) reviews
    → Merge on approval
    → KB updated
```

### When to Contribute

| Condition | Action | Example |
|-----------|--------|---------|
| Fact is verified and new | New KB entry or update existing | "Found that Claude Projects RAG threshold is 13 files, not token-based" |
| Fact contradicts existing KB | Update the KB, document the contradiction in Changelog | "Decision 61 changed the provider priority ordering" |
| Fact was found during research | Add to an existing entry's Core Knowledge | "New pattern discovered: Index-First Navigation" |
| Fact is speculative | Put in Evolution Notes | "Unknown: How does file re-upload affect RAG quality?" |

### The Changelog Standard

Every change to a KB entry MUST be recorded in the Changelog with:
- **Date**: When the change was made
- **Version**: Semantic version (MAJOR.MINOR.PATCH)
- **Author**: Entity name of the agent who made the change
- **Change**: What changed and why

### Versioning Convention
- **MAJOR** (1.0.0 → 2.0.0): Structural rewrite, domain redefinition, or supersession
- **MINOR** (1.0.0 → 1.1.0): New knowledge added, new sections
- **PATCH** (1.0.0 → 1.0.1): Corrections, clarifications, link fixes

### When NOT to Contribute

- **Don't duplicate**: Check INDEX.md and grep for the topic first
- **Don't editorialize**: KB entries document facts and patterns, not opinions
- **Don't remove without supersession**: Deprecate, don't delete. Leave a trail.
- **Don't guess**: If uncertain, put it in Evolution Notes, not Core Knowledge

---

## Section 4: Staleness Detection — How Agents Keep the KB Fresh

### The 3-Tier Staleness Classification

Adapted from Workforce Wave and Scabera's Knowledge Rot research:

| Tier | Definition | Examples | Action |
|------|-----------|----------|--------|
| **Critical** | Knowledge that can cause HARM if wrong | M1-M14 mandate interpretations, API endpoint specs, PIVOT decisions | Immediate flag + update within session |
| **Moderate** | Knowledge that hurts QUALITY if wrong | Best practices, pattern recommendations, design principles | Batch into next review queue |
| **Cosmetic** | Knowledge that drifts in BRAND if wrong | File naming conventions, tag examples, template usage | Weekly digest, lowest priority |

### Staleness Triggers

| Trigger | How to Check | Action |
|---------|-------------|--------|
| **PIVOT Decision published** | `grep "Decision" PIVOT_LOG.md` and cross-ref KB entries | Update affected KB entries within 1 session |
| **Entry >30 days without update** | Check `modified` date in frontmatter | Flag as `POTENTIALLY_STALE` in Evolution Notes |
| **Test failure reveals contradiction** | Tests reference KB facts that don't match behavior | Escalate to maintainer for review |
| **Research finds superseding information** | New fleet research contradicts existing KB | Submit PR to update or deprecate |

### The Staleness Resolution Protocol

```
1. Agent detects potential staleness
2. Agent checks PIVOT_LOG.md for relevant decisions
3. Agent cross-references with current code/tests
4. If confirmed stale:
   a. Update the KB entry
   b. Update Changelog with what changed and why
   c. Update `reviewed` and `modified` dates in frontmatter
5. If NOT stale:
   a. Update `reviewed` date in frontmatter
   b. Add note to Evolution Notes confirming reviewed
```

### Freshness-Weighted Retrieval

When reading the KB, agents should prioritize entries with recent `reviewed` dates. An entry reviewed yesterday is more reliable than an entry reviewed 6 months ago, even if it hasn't been "modified" (modified = any edit; reviewed = verified accurate).

---

## Section 5: Maintenance — How the KB Stays Healthy

### The Lint Protocol

Adapted from Karpathy's weekly lint and the Living KB pattern. Agents should perform these checks periodically:

```
Lint Checklist (run when task involves KB):
- [ ] INDEX.md matches actual files in docs/kb/
- [ ] No entries with status ACTIVE that have no update in 30+ days
- [ ] No contradictory claims across entries (cross-ref by domain)
- [ ] All references resolve (no 404 links)
- [ ] Evolution Notes capture known gaps honestly
- [ ] Supersession chains are complete (no broken links)
```

### The Orphan Scan

Check for entries that exist but have no inbound links from INDEX.md or other entries. An orphan entry is knowledge the fleet cannot discover.

### The Refresh Cycle

On significant architectural events (new PIVOT, new research fleet findings, major engine update):
1. Run the lint protocol
2. Scan for affected KB entries
3. Update or flag each affected entry
4. Close the cycle by updating INDEX.md

---

## Section 6: Integration with the Sovereign Tri-Store

The KB system feeds the broader Sovereign Gnosis architecture:

```
docs/kb/ (Curated KB)
    │
    ├──→ Leaf Store (Vector): KB entries are chunked into Qdrant for semantic retrieval
    ├──→ Concept Graph (Graph): KB domains and cross-refs become graph nodes and edges
    └──→ Gnosis Tree (Hierarchical): L1→L2→L3 distillation feeds recursive summaries
```

The `docs/kb/` system is the **human-and-agent-curated layer**. It is the authoritative source that feeds the automated vector/graph stores, but is never replaced by them. Automation may suggest updates; only the curated contribution protocol can apply them.

---

## Section 7: File Format Standard

Every KB entry file MUST begin with YAML frontmatter. This is the primary interface for agent discovery and filtering.

```yaml
---
title: "Knowledge Entry Title"
id: kb-XXXX
domain: architecture | patterns | protocols | integrations | operations | reference
tags: [list, of, relevant, tags]
sensitivity: internal           # internal = engine-team only; sovereign = public-facing
maintainer: entity-name
created: YYYY-MM-DD
reviewed: YYYY-MM-DD            # last verification of accuracy
modified: YYYY-MM-DD            # last change of any kind
supersedes: null                 # id of entry this replaces
superseded_by: null              # id of entry that replaces this
status: ACTIVE                   # ACTIVE | DRAFT | DEPRECATED
research_source: null            # id of research doc that produced this
reinforcement_count: 0           # incremented each time an agent references this entry
---
```

### Required Fields
- `title`, `id`, `domain`, `tags`, `maintainer`, `created`, `reviewed`, `modified`, `status`

### Optional Fields
- `sensitivity` (defaults to `internal`)
- `supersedes`, `superseded_by` (for deprecation chains)
- `research_source` (for traceability to research docs)
- `reinforcement_count` (for health tracking)

---

## Known Antipatterns

| Antipattern | Symptom | Correct Approach |
|-------------|---------|-----------------|
| Skipping INDEX.md | "I'll just search directly" → misses relevant entries | Always read INDEX.md first, grep for precision |
| Contributing without cross-ref | Duplicate knowledge, conflicting advice | Grep the whole KB and PIVOT_LOG before writing |
| Never updating reviewed date | Entry hasn't been verified in months, appears stale | Update `reviewed` date even if content hasn't changed |
| Deprecating without superseding | Orphaned entries, broken links | Always set `superseded_by` when deprecating |
| Writing speculatively | Core Knowledge contains guesses | Speculation belongs in Evolution Notes, not Core Knowledge |
| Ignoring Evolution Notes | Known gaps never get closed | Each session should check if it can close an Evolution Note |

---

## References

- Karpathy, "LLM Wiki" — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Haberlah, "Documentation Is Infrastructure Now" — https://medium.com/@haberlah/documentation-is-infrastructure-now-9b8b0e44af1d
- AgentRisk — agent-first knowledge base — https://agentrisk.com/
- Slite MCP for self-maintaining KB — https://slite.com/
- Workforce Wave, "KB Staleness Problem" — https://www.workforcewave.com/blog/kb-staleness-problem
- Scabera, "Knowledge Rot: Hidden Cost of Stale Enterprise AI" — https://scabera.com/blog/knowledge-rot-enterprise-ai-hidden-cost
- Guru MCP Server — https://getguru.com/features/mcp-server
- Dev.to, "How I Use AI Agents to Maintain a Living KB" — https://dev.to/aegiswizard/how-i-use-ai-agents-to-maintain-a-living-knowledge-base-for-my-team-490c
- Apraj, "Building Agentic Documentation Workflows" — https://nikitaapraj.com/2026/04/17/building-agentic-documentation-workflows/
- Anthropic — RAG for Projects — https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- Sovereign Gnosis Blueprint — `docs/research/R_SOVEREIGN_GNOSIS_BLUEPRINT.md`
- Sovereign Knowledge Maintenance Protocols — `docs/research/R_KNOWLEDGE_LIFECYCLE_PROTOCOLS.md`

## Evolution Notes

- **Known gap**: The `reinforcement_count` field is defined but not yet instrumented. No tool currently increments it when an agent reads an entry.
- **Known gap**: The lint protocol is documented but not automated. A `make kb-lint` target would be valuable.
- **Known gap**: The integration with the Tri-Store architecture (Leaf Store, Concept Graph, Gnosis Tree) is designed but not implemented. The KB currently exists as flat files only.
- **To investigate**: Whether PR-based review scales when agents are the primary contributors. AgentRisk suggests autonomous validation may be viable, but the omega engine's sovereign context may prefer human-in-the-loop.
- **To investigate**: Whether the 3-tier staleness classification needs a fourth tier for "certainty level" (speculative vs. confirmed vs. proven).

---

*⬡ OMEGA ⬡ KB-AGENT-PROTOCOL ⬡ trc_knowledge_base*
