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
| Cline CLI Integration | `CLINE_CLI_INTEGRATION.md` | 1.0.0 | 2026-06-25 | Kali |
| Context Pack Creation | `CONTEXT_PACK_CREATION_GUIDE.md` | 1.0.0 | 2026-06-13 | Kali |
| GitHub Sovereign Knowledge Base | `GITHUB_Sovereign_Knowledge_Base.md` | 1.0.0 | 2026-06-13 | Kali |
| High-Performance Memory Management | `MEMORY_MANAGEMENT_KB.md` | 1.0.0 | 2026-08-10 | Roc |
| Model Study Knowledge Base | `MODEL_STUDY_KNOWLEDGE_BASE.md` | 1.0.0 | 2026-06-13 | Kali |
| Nemotron 3 Ultra Streaming Fix | `NEMOTRON3_ULTRA_STREAMING_FIX_20260730.md` | 1.0.0 | 2026-07-30 | Kali |
| Omega Hub Multi-Platform | `OMEGA_HUB_MULTI_PLATFORM.md` | 1.0.0 | 2026-06-25 | Kali |
| PYTHONPATH Resolution | `PYTHONPATH_RESOLUTION.md` | 1.0.0 | 2026-06-13 | Kali |
| Refinement Protocol | `REFINEMENT_PROTOCOL.md` | 1.0.0 | 2026-06-13 | Kali |
| Researcher Refinement Documentation Template | `RESEARCHER_REFINEMENT_DOCUMENTATION_TEMPLATE.md` | 1.0.0 | 2026-06-13 | Kali |
| Research Plan Refinement Process Case Study | `RESEARCH_PLAN_REFINEMENT_PROCESS_CASE_STUDY.md` | 1.0.0 | 2026-06-13 | Kali |
| Study: Iterative Human-AI Oversight | `STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md` | 1.0.0 | 2026-06-13 | Kali |
| Synthesis Framework Refinement Case Studies | `SYNTHESIS_FRAMEWORK_REFINEMENT_CASE_STUDIES.md` | 1.0.0 | 2026-06-13 | Kali |
| **Routine System Maintenance** | **`SYSTEM_MAINTENANCE_KB.md`** | **1.0.0** | **2026-09-01** | **Roc** |
| Entry Template | `TEMPLATE.md` | 1.0.0 | 2026-06-13 | System |
| WARP Sovereign Knowledge Base | `WARP_Sovereign_Knowledge_Base.md` | 1.0.0 | 2026-06-13 | Kali |
| Gemma 4 Model Comparison | `gemma4_comparison.md` | 1.0.0 | 2026-06-13 | Kali |

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

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-09-01 | 1.1.0 | roc_racoon | Rebuilt index to match actual files on disk (was 5/20 entries — lint violation). Added SYSTEM_MAINTENANCE_KB.md (kb-0005). |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_core | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->