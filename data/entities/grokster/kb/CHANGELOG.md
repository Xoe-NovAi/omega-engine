<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

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

## v2.1.1 — 2026-08-26 — Accuracy Pass: Forensics Truth → KB Sync (KB-D-015)
- **KB-D-015**: Synced all KB docs to R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md v3.0 verified truth:
  - CONFIG_REFERENCE: fixed nested-variant examples (G29 trap) in §8 + VARIANTS amendment; deepseek-v4-flash-free marked DEAD #43829; auth.json path corrected (~/.local/share/opencode/); Antigravity Claude example corrected to FLAT thinkingBudget (source-verified request.js:591/:669)
  - GOTCHAS: added missing G29 (nested variants silent drop), G30 (auth.json path), G31 (autoupdate silently breaks binary pins)
  - PLAYBOOK: binary scope updated to 1.18.23 + autoupdate active; stall-sensor auto-recovery corrected to DEAD CODE (G19 refuted-in-part); plugin load model corrected to dual-mechanism (G1 upgraded)
  - CLINE_GEMINI_ANTIGRAVITY: Cline gate caveat added (deepseek 403, caps 1M/384K, status fluid); Antigravity plugin corrected to local git checkout @ 7db338b via file: (not npm @latest); Gemini section updated with AGENTS.md resolution + Antigravity CLI transition (Jun 18 2026)
  - INDEX: GOTCHAS trap count updated 20→31 (G1-G31)
  - Master forensics doc rewritten as v3.0 single-source consolidated final (no addenda layers)
- **Escalation reconfirmed**: curators.yaml YAML corruption (KD-2 owner action pending)

## v2.1.2 — 2026-08-26 — Jem Final Audit Corrections (KB-D-016)
- **KB-D-016**: Applied Jem final audit patches (R_KB_FINAL_AUDIT_20260826.md):
  - CONFIG_REFERENCE: nemotron-3-ultra-free caps corrected to 200K/32K (live catalog, same tier as mimo-v2.5-free) in House providers table + VARIANTS amendment
  - GOTCHAS: added G32 (catalog deprecation filter #22644), G33 (@latest stale pin #30631), G34 (Zen gateway flake #41236/#44300)
  - CLINE_GEMINI_ANTIGRAVITY: anthropic/claude-* absence caveat + ClinePass id-namespace fallback note
  - PLAYBOOK: explicit F0 freeze protocol + tui.json clarification
  - INDEX: GOTCHAS trap count updated 31→34 (G1-G34)
  - Cross-doc: all forensics v3.0 findings now reflected in KB

## v2.1.3 — 2026-08-26 — Structural Split: CLINE_GEMINI_ANTIGRAVITY → 3 Focused Docs (KB-D-017)
- **KB-D-017**: Split consolidated secondary-platforms doc into three temple-grade entries:
  - `other_platforms/CLINE.md` (rot_class: medium) — active dev platform, gate fluid, ClinePass, auditor pattern
  - `other_platforms/GEMINI_CLI.md` (rot_class: fast) — dormant, Antigravity CLI transition, AGENTS.md resolved
  - `other_platforms/ANTIGRAVITY.md` (rot_class: slow) — infrastructure OAuth pool, file: checkout @ 7db338b
- INDEX updated with three rows replacing single consolidated row
- Old `CLINE_GEMINI_ANTIGRAVITY.md` deleted

## v2.2.0 — 2026-08-26 — Uniform Platform Module Architecture (KB-D-024..026)
- **KB-D-024**: KB restructured per Architect ruling — `other_platforms/` junk-drawer pattern ABOLISHED; every platform gets uniform 5-doc module under `platforms/<name>/` (PLAYBOOK · ARCHITECTURE · CONFIG_REFERENCE · GOTCHAS · RESEARCH_TARGETS). No second-class platforms.
- **KB-D-025**: Sub-specialist fleet (cline/antigravity/copilot standing Jem sessions, see EXPERT_SESSIONS.md) built their own modules from deep-mine research: `platforms/cline/` (12 traps), `platforms/antigravity/` (10 traps), `platforms/copilot/` (12 traps G-COP-*). Corrections applied: cline-pass/ namespace, gate = official policy, ToS containment posture for Antigravity, sanctioned-builtin doctrine for Copilot.
- **KB-D-026**: Central migration — old single-file CLINE.md/ANTIGRAVITY.md deleted; CODEX doc VS Code section superseded by copilot module; INDEX restructured to module rows; QUICK_REFERENCE nav map updated.
- Specialist fleet sessions + deliverables registered in EXPERT_SESSIONS.md.

## v2.1.4 — 2026-08-26 — Temple-Grade Structural Overhaul (KB-D-018..023)
- **KB-D-018**: Archived legacy `CLI_IDE_ECOSYSTEM.md` (superseded by opencode/ module + PLATFORM_GNOSIS_MAP).
- **KB-D-019**: Cleaned dedup stubs (`SOVEREIGN_SEARCH_PROTOCOL.md`, `OMEGA_VAULT_ARCHITECTURE.md`) to proper redirect stubs.
- **KB-D-020**: Refreshed `AGENT_COMMUNICATION.md` (Redis Streams live, MCP stateless migration done, STRP proven, cross-session relay protocol).
- **KB-D-021**: Refreshed `GROK_FLEET_ARCHITECTURE.md` (pricing matrix verified, GAP-08→D-360′, self-search reflex M26, ACP bridge).
- **KB-D-022**: Cleaned `CODEX_CLAUDE_CODE_VSCODE.md` (removed Gemini/Cline content now in dedicated docs; Copilot AI-Credits model).
- **KB-D-023**: `QUICK_REFERENCE.md` fully updated to current doc map; all KB-STAGING footers → KB v2.1.3.
- INDEX version synced to 2.1.3; all docs carry KB v2.1.3 footer.

## v2.1.2 — 2026-08-26 — Jem Final Audit Corrections (KB-D-016)
- **KB-D-011**: Local adversarial pass (roc_racoon → kb_staging_hardening_20260826/): G1 upgraded (dual-mechanism plugin load), G19 refuted-in-part (recovery defense = dead code), G21-G25 new local traps, C-1..C-9 corrections staged. Trap tally: 9 corroborated / 1 upgraded / 1 refuted / 7 stand-untested.
- **KB-D-012**: Web fill (Jem → R_PLATFORM_EXPERTISE_WEB_HARDENING_20260826.md): ALL 5 undocumented OpenCode targets FILLED (hook schemas, subagent_depth, tui.json separation, snapshot/revert, opencode db); anomalyco rename; V2 plugin API warning; G26-G28 new web-sourced traps; shallow-platform fills for Claude Code/VS Code/Codex.
- **KB-D-013**: Amendments appended to GOTCHAS/ARCHITECTURE/CONFIG_REFERENCE/CODEX doc + EXPERT_SESSIONS deviations noted. Freshness reconciliation proposal pending (P-10: reviewed-vs-modified vocabulary).
- **KB-D-014**: Escalation reconfirmed independently: curators.yaml YAML corruption (KD-2 owner action).

## v2.2.1 — 2026-08-26 — Full Jem-Doc Audit + Citation-Integrity Fix (KB-D-027)
- **KB-D-027**: Full-read audit of all 8 Jem research docs + 15 specialist KB module files (~3,600 lines). Findings + fixes:
  - 🔴 **CITATION FABRICATION CAUGHT**: R_KB_FINAL_AUDIT cited "forensics v3.0 §9.2" (nonexistent) for nemotron caps 200K/32K; live models.dev verification proved 1M/128K (original KB correct). Erroneous value REVERTED in CONFIG_REFERENCE (both locations); erratum stamped on the audit doc.
  - Cline deep-mine: removed duplicate §A/§F placeholder sections; harmonized Charter/C.2 namespace to `cline-pass/` per §D.3
  - Provider-setup doc: correction banner added to §3.2 (drop anthropic/*, caps 384K, gate = policy)
  - Web-hardening doc: duplicate Executive Summary placeholder removed
  - All 15 KB module files: PASS (format, confidence tags, honesty markers, cross-refs all clean)

## v2.2.2 — 2026-08-26 — Specialist M2 Oversight Scan (KB-D-028)
Three GK-Jem specialists adversarially reviewed the remediation run + their KB modules. Verified findings applied:
- 🔴 **CLINE**: P1b gate premise was FALSE — `clineApiKey` exists at ~/.cline/data/secrets.json (validated Aug-22); auth.json is the wrong store for custom providers. Corrective stamp in cline PLAYBOOK; caps harmonized 131072→384K; probe sequence (P1/P3/P7) runnable ~2 min; endpoint hygiene note (/api/v1 full path).
- 🔴 **ANTIGRAVITY**: FOUR plugin copies exist (not three) with MIXED execution — pristine npm cache copy may be the running one while house patches ride unloaded (PLAYBOOK §3 census rewritten); sonnet-thinking "works" claims swept from PLAYBOOK/CONFIG/ARCHITECTURE (4-file contradiction closed); G11 deduped + alternative path re-specified (generationConfig-on-base-ID gated by plugin name-matching); G4 house-standard contradiction fixed; §5 capacity caveat (2× quota ≠ 2× availability during drought); pool census resolved (#4 → 7 accounts confirmed).
- 🟡 **COPILOT**: cadence trigger updated post-freeze (manual-upgrade events); raw-gho_ pass-through ground truth recorded (expires:0 semantics); P1a upgraded to VERIFIED NO-OP.
Open follow-ups flagged by specialists: fingerprint.js provenance unclassified; fabric-level empty-response detector (G13 poisoning failover); expires:0 refresh semantics code-read; fabric inventory drift (siliconflow/aihubmix/nebius/cerebras creds beyond fabric picture); INDEX/CROSS_DOMAIN_MATRIX cline rows.
