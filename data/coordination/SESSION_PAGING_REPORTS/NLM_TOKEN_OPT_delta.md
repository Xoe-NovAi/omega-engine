<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# NLM Token Optimization Delta — Session Paging Report
**AP Token**: `AP-NLM-TOKENOPT-DELTA-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_nlm_tokenopt_delta ⬡ PAGED-RETURN

**Date**: 2026-08-21
**Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Source artifact**: `data/coordination/NOTEBOOKLM_OPTIMIZATION_20260819.md` content (my original session output — file write timed out; full findings preserved in session transcript and re-delivered in-chat)
**Hydration**: ACTIVE_SPRINT.json (updated 2026-08-20T22:00Z) + docs/specs/PROJECT_INDEX.md read in full. GN (D-571..D-577, D-582/D-583) absorbed. Sibling `NLM_INVENTORY_delta.md` read — this report is COMPLEMENTARY (retrieval science/density/chunking/features), not duplicative.

---

## 1️⃣ Forgotten Findings From Token-Optimization Research — Relevant to GN Execution

### 1.1 The empirical degradation curve (basis of ratified 5-25 sweet spot)
My web research (sourclip.com 2026-08-03, elephas.app 2026-08-12, notebooktools.com 2026-06-20) established:
| Source count | Retrieval quality | Mechanism |
|---|---|---|
| 5–15 | ✅ Excellent | High signal, focused context |
| 15–30 | ✅ Good | Manageable breadth |
| 30–50 | ⚠️ Degrading | Generic answers increase |
| 50+ | ❌ Poor | "Wider space to draw a general answer from instead of a specific, well-cited one" |

**Mechanism (critical for GN)**: NotebookLM chat runs on Gemini's ~1M-token context window. More sources = wider answer space = genericity. This is NOT a hard cutoff — it is probabilistic dilution. **This finding is the empirical seed of the "5–25 well-curated sources" doctrine now canonized in NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md §density and D-571..D-577.**

### 1.2 WORDS not tokens govern NotebookLM limits
Google's official docs speak in **words and megabytes**, NOT tokens. Per-source cap = 500K words / 200MB; no official word→token conversion published. Implication for `prepare_notebooklm.py`: budget checks should use **word counts** (`wc -w`) as the gating metric, with token estimates (~0.75 words/token English) as advisory only. My "~145K tokens" inventory ≈ ~110K words — trivially safe per-source.

### 1.3 NotebookLM reads ONLY the text layer
Confirmed via Google troubleshooting guidance: sources without readable text produce nothing. Two GN consequences:
1. **Raw YAML/JSON uploads become unsearchable blobs** — MUST convert to Markdown with fenced code blocks + semantic headers before ingest.
2. Code files (.py) ingest fine as plain text — no conversion needed for the 11 core-code files in the sibling inventory.

### 1.4 Cross-notebook isolation + Gemini-conversation workaround
Notebooks cannot query each other. For NB-1↔NB-2 synthesis (GN cross-account synthesis goal): attach BOTH notebooks to ONE Gemini conversation — Gemini pulls from each separately in a single chat. This is the only sanctioned cross-notebook pattern on free tier.

### 1.5 PDF scanned-text trap (low relevance but recorded)
Scanned/image PDFs fail silently regardless of size. Omega corpus is all-native Markdown/text → non-issue, but any future PDF exports of reports must be text-layer verified.

---

## 2️⃣ Token/Density Insights for the 5–25 Sweet Spot & Notebook Curation

### 2.1 Source-count is the binding constraint, NOT token volume
My original verdict — "Stay at 150K–200K tokens; the 500K ceiling is a trap" — was correct but INCOMPLETE. The ratified v2.1 doctrine sharpens it: **source COUNT (5–25) binds before token VOLUME does**. Sibling inventory's 36 files would violate this as 36 separate sources. Resolution = **source merging**, my original technique now load-bearing for GN:

| Merge group | Files | Becomes |
|---|---|---|
| All config YAML | providers.yaml, models.yaml, omega.yaml, manifest/hierarchy/entities.yaml | ONE "Omega Config Pack" source (YAML→MD fences) |
| Core code trio | oracle.py + model_gateway.py + entity_registry.py | ONE "Oracle Core Code" source w/ file headers |
| Memory subsystem | memory_store, sqlite_vec_adapter, hybrid_search, context_builder, soul_store | ONE "Memory Subsystem" source |
| Guard trio | health_monitor + resource_guard + skeptical_verifier | ONE "Resilience Guards" source |

36 raw files → ~20–22 sources → inside sweet spot with headroom for Deep Research outputs.

### 2.2 Upload ORDER affects auto-labeling quality
NotebookLM indexes sources in upload order; early sources anchor auto-generated labels. Curation sequence for GN-2 ingestion:
1. Foundational first: SOVEREIGN_MANDATES.md, AGENTS.md, ORACLE_STACK_CANONICAL.md
2. Architecture second: code packs, config pack
3. Research third: CARMACK_DEFINITIVE_STRATEGY + 5 YouTube deep-dives
4. Sprint state LAST: ACTIVE_SPRINT.json snapshot, GAP_REGISTRY.json (they mutate; see §3)

### 2.3 Label-anchored queries recover precision in crowded notebooks
Free tier caps at 50 sources/notebook. If NB-1 ever exceeds 25: use **source labels as context filter** ("Ground this answer ONLY in [LABEL]") — recovers specific-citation quality without deleting sources. Recommend GN-2 assign labels at ingest time (e.g., `MANDATES`, `ORACLE-CORE`, `SPRINT`, `YT-EVIDENCE`) rather than retroactively.

### 2.4 Cross-chunk reference preservation (for PIVOT_LOG/UNOVERENGINEERING splits)
When large files are split across sources/chunks:
- Prefix each chunk with its section path: "## PIVOT_LOG D-301..D-400 (Sovereign Ark era)"
- Add navigation line in chunk 1 of N: "Part 1/4 — decisions D-1..D-100; see parts 2–4"
- Anchor entities/decisions inline: `[ENTITY: kali]`, `[DECISION: D-354]` so retrieval can join across chunks
- Maintain ONE shared GLOSSARY source (IWAD/WAD/Node/Pillar terms) to prevent nomenclature drift in answers

### 2.5 Mutating-file grounding rot
ACTIVE_SPRINT.json changes daily. Ingesting it verbatim creates stale-grounding risk: NotebookLM holds a STATIC copy and will confidently cite superseded state. Mitigation: ingest only date-stamped snapshots (`ACTIVE_SPRINT_snapshot_20260821.json`) and re-snapshot weekly, or exclude sprint-state from notebooks entirely and keep it local-only.

---

## 3️⃣ Flagged Important, Never Executed

| # | Item | Original rec | Status |
|---|------|--------------|--------|
| 1 | **YAML→MD conversion pipeline** | `prepare_notebooklm.py` converts config/soul YAML to fenced Markdown | ❌ Never built — now THE single blocker; must target `notebooklm-py download`, NOT MCP `research_start` |
| 2 | **Source merging into packs** | Combined soul.yaml / skills / config sources to control count | ❌ Never executed — now load-bearing for hitting 5–25 with 36-file corpus |
| 3 | **Weekly snapshot generator** | Test results + sovereignty metrics as dated sources | ❌ Never automated (sovereignty ratio last pulled live by me: 19.35% local / 80.65% cloud, n=2553) |
| 4 | **Label assignment at ingest** | Label-anchored query discipline | ❌ Never tested empirically |
| 5 | **GLOSSARY.md shared source** | Nomenclature-drift prevention | ❌ Never created (`config/glossary.md` exists locally — just needs ingest) |
| 6 | **Entity/decision anchors** | `[ENTITY:]`/`[DECISION:]` prefixes in chunks | ❌ Never implemented |
| 7 | **A/B source-set testing** | Measure citation accuracy across source sets (my #1 blind-spot mitigation) | ❌ Never run — still the only way to validate density claims on OUR corpus |
| 8 | **Audio presets per use case** | Expert-level for technical content (compliance/architecture/postmortem presets) | ❌ Never created |
| 9 | **Study Guide from MANDATES** | Mandate-compliance training artifact | ❌ Never generated |
| 10 | **MindMap Exporter extension** | XMind export for architecture viz | ❌ Never installed |

### Corrections to my own prior recommendations (superseded by ratification)
1. **Pro tier ($19.99/mo) recommendation → SUPERSEDED by D-582** (free-tier-only, 3 accounts). All Pro-gated features I recommended (custom chat styles, code execution/cloud computer, thinking-steps expansion, 300 sources) are OUT OF SCOPE. Free tier reality: 50 sources/NB, ~50 chats/day/acct, 10 DR/mo/acct.
2. **Single-notebook design → SUPERSEDED by D-583 2-NB architecture** (Ω-ACTIVE-RESEARCH + Ω-KNOWLEDGE-BASE). My Tier 1/2/3 list must be split per sibling's mapping (~85% → NB-1).
3. **MCPNotebookLM fork recommendation → RETRACTED**: unified strategy v2.1 confirms the MCP prototype was FABRICATED; canonical tool is `notebooklm-py` RPC + `master_token.json`.

### Recommended actions (for kali triage)
1. Fold §2.1 merge-packs table into `prepare_notebooklm.py` spec BEFORE implementation — it is the mechanism that makes 36 files fit 5–25.
2. Word-count gating (`wc -w`) in the script, not token estimates (§1.2).
3. Sequence per sibling §4 stands; add: assign labels at GN-2 ingest (§2.3), snapshot-tag sprint state (§2.5).
4. Post-GN-4 smoke: run ONE A/B citation-accuracy test (§3 #7) to convert my research from external-evidence to internal-evidence.

---
*Report complete. No other files modified.*
*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_nlm_tokenopt_delta ⬡ 2026-08-21*
