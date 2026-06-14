# 🔱 Omega Engine — Knowledge Base

**⬡ OMEGA ⬡ SOPHIA ⬡ trc_core ⬡ KNOWLEDGE-BASE-INDEX**

**Purpose**: Curated, specialized domain knowledge that any agent can reference, evolve, and enhance. Each KB entry is a living document — versioned, attributed, and perpetually maintainable.

**Location**: `docs/kb/`

---

## Active KB Entries

| Domain | File | Version | Last Updated | Maintainer |
|--------|------|---------|-------------|------------|
| Agent-KB Interaction Protocol | `AGENT_KB_PROTOCOL.md` | 1.0.0 | 2026-06-13 | Kali |
| Claude Projects Collaboration | `CLAUDE_PROJECTS.md` | 2.0.0 | 2026-06-13 | Kali |
| Entry Template | `TEMPLATE.md` | 1.0.0 | 2026-06-13 | System |

---

## How to Use This KB

1. **Find the domain**: Scan INDEX.md for the topic you need
2. **Read the entry**: Each file is self-contained with version, changelog, and the knowledge
3. **Evolve it**: Found something missing or outdated? Add an entry to the changelog and append to the body. See `AGENT_KB_PROTOCOL.md §3` for the contribution workflow.
4. **Check staleness**: If the `reviewed` date in the frontmatter is >30 days old, flag for review.

## How to Add a New KB Entry

1. Copy `TEMPLATE.md` to `docs/kb/YOUR_DOMAIN.md`
2. Fill in the YAML frontmatter (id, domain, tags, maintainer, dates)
3. Write the knowledge with clear sections
4. Add an entry to this INDEX.md (keep alphabetical by region)
5. Announce the new KB in Hivemind so the fleet knows it exists
6. Follow the contribution workflow in `AGENT_KB_PROTOCOL.md §3`

## Guiding Principles

- **Living documents**: Entries are never "done" — they evolve with experience
- **Attribution**: Every changelog entry records who made the change and why
- **Discoverability**: INDEX.md is the single entry point. Keep it current.
- **No fragmentation**: KB lives ONLY in `docs/kb/`. If it's not here, it's not KB.
- **Frontmatter is mandatory**: Every entry must begin with YAML frontmatter for agent-based discovery
- **Review regularly**: Entries unreviewed for >30 days should be flagged for freshness check
