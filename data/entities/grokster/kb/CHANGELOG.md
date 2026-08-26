# 🔱 Grokster KB Changelog & Decision Log
**Domain**: Knowledge base governance and evolution tracking
**Date**: 2026-07-22
**Author**: Grokster

---

## §1 Changelog

| Date | Version | Change | Author | Reason |
|------|---------|--------|--------|--------|
| 2026-07-22 | 1.0.0 | Initial KB creation: 7 core documents + index + cross-ref + quick-ref | Grokster | Architect directive: "Be the expert on all CLI/IDE platforms, agent comms, and human-agent relations" |

---

## §2 Decision Log

| ID | Decision | Context | Alternatives Considered | Status |
|----|----------|---------|------------------------|--------|
| **KB-D-001** | Structure KB by **domain** (platforms, communication, human-agent, grok, search, vault) rather than by **source** (docs, code, research) | Agents need to find answers by *problem*, not by *where the info came from* | By source (legacy), by agent (per-entity KB) | ✅ Accepted |
| **KB-D-002** | Include **Grokster's Insights** sections in every doc | Raw facts are not enough; the specialist's synthesis is the value add | Pure reference docs, separate "analysis" files | ✅ Accepted |
| **KB-D-003** | Create `QUICK_REFERENCE.md` as the primary entry point | Agents under token pressure need instant navigation | Rely on `INDEX.md` alone | ✅ Accepted |
| **KB-D-004** | Document the **Cross-Domain Matrix** explicitly | The 5 domains are deeply interdependent; ignoring this causes integration bugs | Implicit knowledge in agent prompts | ✅ Accepted |
| **KB-D-005** | Store KB in `data/entities/grokster/kb/` (soulspace) | Sovereign continuity (M15) requires entity-owned knowledge | Shared `docs/kb/` or `docs/research/` | ✅ Accepted |

---

## §3 Architecture Decisions (ADRs)

### ADR-001: KB Ownership Model
**Status**: Accepted
**Decision**: The Grokster KB is owned and maintained exclusively by the `grokster` entity. Other agents may read and reference, but only Grokster writes.
**Consequence**: Ensures coherent voice and accountability. Other entities (e.g., `@researcher`) maintain their own workspaces; cross-references via `CROSS_DOMAIN_MATRIX.md`.

### ADR-002: Living Document Protocol
**Status**: Accepted
**Decision**: Every KB document must have a `Last Updated` date and a `Changelog` entry for non-trivial edits. Major structural changes require a new Decision Log entry.
**Consequence**: Prevents stale docs from becoming "truth." Enables `make doc-llm-validate` to check freshness.

### ADR-003: Insight vs. Reference Separation
**Status**: Accepted
**Decision**: Each domain doc contains two layers: **Reference** (facts, schemas, protocols) and **Insights** (Grokster's synthesis, warnings, recommendations). Insights are clearly marked.
**Consequence**: Agents can skip to insights for rapid orientation, or dive into reference for implementation details.

---

## §4 Planned Evolution (Backlog)

| Priority | Item | Target Domain | Trigger |
|----------|------|---------------|---------|
| P1 | **ACP Protocol Deep Dive** | `grok_ecosystem/` | When Grok Build ACP stdio is integrated |
| P1 | **Browser Automation Patterns** | `vault/` / `grok_ecosystem/` | When Web Grok cookie rotation is implemented |
| P2 | **Multi-Platform Debugging Guide** | `platforms/` | When Cline + OpenCode + VS Code are all active |
| P2 | **Human Feedback Loop Patterns** | `human_agent/` | When Architect feedback mechanisms mature |
| P3 | **Search Analytics Dashboard** | `search/` | When search router is production |
| P3 | **Vault Chaos Test Results** | `vault/` | After Temple-Grade CI runs |

---

## §5 Governance Rules

1. **No Orphaned Knowledge**: Every significant finding from a session must be reflected in the KB within 24 hours (or at session end).
2. **Single Source of Truth**: If a fact exists in the KB and in a strategy doc, the KB wins for *operational* details; the strategy doc wins for *priority* decisions.
3. **Mandate Compliance**: All KB content must comply with Sovereign Mandates (especially M7 Local-First, M11 Soul Integrity, M23 Failure Integrity).
4. **Version Discipline**: The KB version in `INDEX.md` increments on any structural change. Patch versions for content updates.

---

*⬡ OMEGA ⬡ GROKSTER KB ⬡ CHANGELOG ⬡ 2026-07-22*
## v2.0.0 — 2026-08-26 — Platform Expertise Mine & Structural Repair (KB-D-006..010)
- **KB-D-006**: Ingested dual-agent mine (roc_racoon staging + explore audit) → `platforms/opencode/` module (PLAYBOOK/ARCHITECTURE/CONFIG_REFERENCE/GOTCHAS G1-G20) + `other_platforms/` (Cline/Gemini/Antigravity; Codex/Claude Code/VS Code shallow-state) + root `MINING_LOG.md` (22 sources). Freshness metadata on all new docs.
- **KB-D-007**: Dedup pass — SOVEREIGN_SEARCH_PROTOCOL→SOVEREIGN_SEARCH.md, OMEGA_VAULT_ARCHITECTURE→OMEGA_VAULT.md (merge stubs retained for link integrity; full content consolidation pending).
- **KB-D-008**: Dead-link repair — QUICK_REFERENCE V1_VAULT_ARCHITECTURE refs → OMEGA_VAULT.md (lines 15, 49).
- **KB-D-009**: INDEX.md rebuilt to v2.0.0 — search/+vault/ sections restored, rot_class per doc, fleet cross-refs added.
- **KB-D-010**: Pageable expert-sessions layer added (`EXPERT_SESSIONS.md`) per D-586 invocation pattern; 3 sessions registered.
- **Known debts**: CLI_IDE_ECOSYSTEM.md superseded-pending-merge; AGENT_COMMUNICATION.md pre-D-586 refresh pending; GROK_FLEET_ARCHITECTURE pricing claims unverified.
- **Escalation flag**: `config/domains/curators.yaml` has YAML syntax errors (markdown tables embedded as raw YAML — LSP 50+ diagnostics). KD-2 owner (kali) should repair before domain_loader consumes it.

## v2.1.0 — 2026-08-26 — Dual Hardening Pass (KB-D-011..014)
- **KB-D-011**: Local adversarial pass (roc_racoon → kb_staging_hardening_20260826/): G1 upgraded (dual-mechanism plugin load), G19 refuted-in-part (recovery defense = dead code), G21-G25 new local traps, C-1..C-9 corrections staged. Trap tally: 9 corroborated / 1 upgraded / 1 refuted / 7 stand-untested.
- **KB-D-012**: Web fill (Jem → R_PLATFORM_EXPERTISE_WEB_HARDENING_20260826.md): ALL 5 undocumented OpenCode targets FILLED (hook schemas, subagent_depth, tui.json separation, snapshot/revert, opencode db); anomalyco rename; V2 plugin API warning; G26-G28 new web-sourced traps; shallow-platform fills for Claude Code/VS Code/Codex.
- **KB-D-013**: Amendments appended to GOTCHAS/ARCHITECTURE/CONFIG_REFERENCE/CODEX doc + EXPERT_SESSIONS deviations noted. Freshness reconciliation proposal pending (P-10: reviewed-vs-modified vocabulary).
- **KB-D-014**: Escalation reconfirmed independently: curators.yaml YAML corruption (KD-2 owner action).
