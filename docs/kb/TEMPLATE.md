---
id: kb-TEMPLATE
type: template
domain: meta
tags: [template, conventions, metadata]
sensitivity: internal
maintainer: system
created: 2026-06-13
reviewed: 2026-06-13
modified: 2026-06-13
supersedes: null
superseded_by: null
status: ACTIVE
---

# 🔱 Knowledge Base Entry Template

**Domain**: [Single domain this entry covers — one concept, one KB]
**Version**: 1.0.0
**Last Updated**: YYYY-MM-DD
**Maintainer**: [Entity name — who owns this domain]
**Status**: ACTIVE | DRAFT | DEPRECATED

This template conforms to the **Agent-KB Protocol v1** standard. Every KB entry MUST include YAML frontmatter (the block between `---` delimiters) for agent-discovery purposes. See `docs/kb/AGENT_KB_PROTOCOL.md` for the full specification.

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| YYYY-MM-DD | 1.0.0 | [Entity] | Initial creation |

---

## Frontmatter Reference

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique KB identifier (kb-NNNN format) |
| `type` | Yes | `knowledge` for content, `template` for templates, `index` for catalogs |
| `domain` | Yes | One of: `architecture`, `patterns`, `protocols`, `integrations`, `operations`, `reference`, `meta` |
| `tags` | Yes | Array of relevant keywords for filtering |
| `sensitivity` | No (`internal`) | `internal`, `sovereign`, `public` |
| `maintainer` | Yes | Entity name responsible for this entry |
| `created` | Yes | ISO date of initial creation |
| `reviewed` | Yes | ISO date of last accuracy verification |
| `modified` | Yes | ISO date of last any change |
| `supersedes` | No (`null`) | ID of entry this replaces |
| `superseded_by` | No (`null`) | ID of entry that replaces this |
| `research_source` | No (`null`) | Path to research doc that informed this entry |
| `reinforcement_count` | No (`0`) | How many times agents have referenced this entry |

## Domain Overview

[2-4 sentences describing what domain this covers and why it exists. Who needs this knowledge?]

## Core Knowledge

### [Key Concept 1]
[Essential knowledge. Be specific, be actionable. Include code snippets, configuration examples, or command patterns where applicable.]

### [Key Concept 2]
[Continue as needed...]

## Known Antipatterns

| Antipattern | Symptom | Correct Approach |
|-------------|---------|-----------------|
| [What not to do] | [How you know you're doing it] | [What to do instead] |

## References

- [Link to relevant source document]
- [Link to PIVOT_LOG decision]
- [Link to related KB]

## Evolution Notes

[Open space for future contributors. What's known to be incomplete? What edge cases haven't been explored? What should the next maintainer investigate?]

---

*⬡ OMEGA ⬡ KB-TEMPLATE ⬡ trc_knowledge_base*
