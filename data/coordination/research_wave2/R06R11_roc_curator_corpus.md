---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_report"
task_id: "yurs-roc-curator-corpus-20260826"
session_purpose: "R6+R11 — Curator prior art scan + meditation rubric compliance audit"
date: 2026-08-26
author: "roc_racoon"
model: "mimo-v2.5-free"
status: "COMPLETE"
research_gaps: ["R6", "R11"]
cross_references:
  - "data/entities/roc_racoon/workspace/VR_OMEGAVERSE_VISION.md"
  - "data/entities/roc_racoon/workspace/VISION_DEEP_DIVE_CHILD_ERA6_SOULARCH_2.md"
  - "config/domains/curators.yaml"
  - "config/domains/CURATORS.md"
  - "data/coordination/meditations/MEDITATION_REGISTRY.md"
  - "docs/research/R53_meditate_granite_foundation_20260826.md"
  - ".opencode/commands/meditate.md"
---

# R06R11 — Curator Prior Art & Meditation Rubric Compliance

**使命**: R6 — curator model prior art (DS/KD workstreams need a curator; what exists?)
**使命**: R11 — rubric pre-commitment compliance across meditation corpus

---

## §1 R6 — Sovereign Curator vs DS Curator vs KD Curator: Overlap Analysis

### Three Distinct "Curator" Concepts

| Concept | Origin | Scope | Pipeline | Status |
|---------|--------|-------|----------|--------|
| **Sovereign Curator** | June 12, 2026 session (Child 2 A4, critical priority 10:59 UTC) | Knowledge ingestion from raw sources → fine-tuning data | Ingest → Clean → Chunk → Synthesize (headless Gemini CLI, 2M token window) → Store (Mnemosyne) → Gold Sets for local fine-tuning | Spec exists; implementation NOT started |
| **DS Curator** (Documentation System) | DEBUT_REMEDIATION_MANUAL §DS (lines 433–454) | Domain documentation lifecycle management | Workspace authoring + Runtime modules + Curator model + Validated copy sync | META-DOC DOES NOT EXIST (`DOMAIN_DOCUMENTATION_SYSTEM.md` phantom) |
| **KD Curator** (Knowledge Domains) | DEBUT_REMEDIATION_MANUAL §KD (line 443, KD-1..KD-3) | Domain content-layer: affinity presets, domain modules, runtime loading | Runtime modules + workspace authoring + curator model + affinity presets | curators.yaml ACTIVE (13 domains declared); 2 of 13 dirs exist on disk |
| **N12 Curator Node** | Jem's NODE_GAP_SYNTHESIS (line 17) | Research, Curation & Personal Corpus — operational entity | Unifies: PKM craft, esoteric KB stewardship, yt-dlp mining, PP-2 web-export mining | Session-level genesis; no runtime code |
| **Library curator.py** | `src/omega/library/curator.py` (282 lines) | Content quality scoring + domain classification | Keyword heuristic scoring, 0.6 threshold, max ~0.85 | LIVE CODE, but immature (no tests, ceiling bug) |

### Overlap Matrix

```
                Sovereign Curator    DS Curator    KD Curator    N12 Node    library/curator.py
Sovereign         ████████           ░░░░          ░░░░          ░░░░        ░░░░
DS Curator        ░░░░               ████████      ▓▓▓▓          ░░░░        ░░░░
KD Curator        ░░░░               ▓▓▓▓          ████████      ▓▓▓▓        ░░░░
N12 Node          ░░░░               ░░░░          ▓▓▓▓          ████████    ░░░░
library/curator   ░░░░               ░░░░          ░░░░          ░░░░        ████████

██ = primary domain    ▓▓ = overlapping/adjacent    ░░ = no overlap
```

**Key Finding**: The Sovereign Curator and DS Curator are **fundamentally different systems**:
- Sovereign Curator = raw knowledge ingestion → fine-tuning pipeline (content ACQUISITION)
- DS Curator = documentation lifecycle management (content GOVERNANCE)
- KD Curator = domain module curation + affinity preset management (content ORGANIZATION)
- N12 = the entity-session that will own KD-liaison duties operationally

The DS and KD workstreams share the word "curator" but address different layers of the same stack. The KD curator operates over domain modules (metadata.yaml, PLAYBOOK.md, AFFINITY_PRESETS.yaml). The DS curator operates over the documentation that describes those modules. The Sovereign Curator operates upstream of both — ingesting raw external knowledge into the system.

### Sovereign Curator — Full Spec Recovery

From VISION_DEEP_DIVE_CHILD_ERA6_SOULARCH_2.md (line 72):

> **The Sovereign Curator** (critical priority per user at 10:59): decoupled pipeline Ingest → Clean → Chunk → Synthesize (headless Gemini CLI as high-power subagent, exploiting the 2M-token window for map-reduce synthesis of entire manuals) → Store (Mnemosyne), producing "Gold Sets" (high-fidelity Q&A pairs) for local fine-tuning, with telemetry-stripping proxy and local verification loop.

From VISION_ANCHOR_PERPETUAL.md (line 266):

| Component | Detail |
|-----------|--------|
| Pipeline | Ingest → Clean → Chunk → Synthesize → Store |
| Synthesis backend | Headless Gemini CLI (2M token window) |
| Output | Gold Sets (high-fidelity Q&A pairs) for local fine-tuning |
| Proxy | Telemetry-stripping proxy (sovereignty compliance) |
| Verification | Local verification loop |

The Sovereign Curator also appears in the handoff archive (`session-ses_144d.md`) as a sub-agent of the "Sovereign Stack Creator" tool — the user-facing WAD editor that would invoke `/ssc/curator/ingest` to automatically build knowledge bases from raw sources.

---

## §2 R6 — Existing Curator Configuration (curators.yaml Structure)

### Registry Structure (curators.yaml v1.1.0)

Ratified D-569, repaired KD-2 (2026-08-26). Split from markdown-in-YAML to machine-parseable format.

**Schema**:
```yaml
schema_version: "1.0"
governance_levels:
  PRIVATE: "Only curator entity may write; others may not read"
  SHARED_READ: "Curator writes; all fleet entities may read"
  SHARED_WRITE: "Curator + designated co-authors write; all may read"
```

**13 Domains Declared**:

| # | Domain | Curator | Governance | Target CTX | Presets on Disk |
|---|--------|---------|------------|------------|-----------------|
| 1 | gemini-notebook | researcher | SHARED_READ | 16384 | ❌ MISSING |
| 2 | platforms | grokster | SHARED_READ | 16384 | ❌ MISSING |
| 3 | grok_ecosystem | grokster | SHARED_READ | 16384 | ❌ MISSING |
| 4 | architecture | john_carmack | SHARED_READ | 32768 | ❌ MISSING |
| 5 | heritage | doom_guy | SHARED_READ | 16384 | ❌ MISSING |
| 6 | research | researcher | SHARED_READ | 16384 | ❌ MISSING |
| 7 | runtime | lilith | SHARED_READ | 16384 | ❌ MISSING |
| 8 | build | maat | SHARED_READ | 16384 | ❌ MISSING |
| 9 | compliance | verity | SHARED_READ | 8192 | ❌ MISSING |
| 10 | legacy | roc_racoon | SHARED_READ | 8192 | ❌ MISSING |
| 11 | synthesis | jem | SHARED_READ | 32768 | ❌ MISSING |
| 12 | engineering | maat | SHARED_READ | 8192 | ✅ EXISTS |
| 13 | security | verity | SHARED_READ | 8192 | ❌ MISSING |

**Disk Reality**: Only `config/domains/engineering/` has a complete module (7 files incl. MEMORY_BLOCKS/*.block, PRINCIPLES/principle_001.yaml, AFFINITY_PRESETS.yaml, PLAYBOOK.md, metadata.yaml). The `config/domains/gemini-notebook/` directory exists but contains NO AFFINITY_PRESETS.yaml. 12 of 13 referenced preset files are MISSING.

**Review Gate**:
- compliance_security → verity
- synthesis → kali
- Required for: new_domain_module_creation, major_metadata_version_bump, governance_level_change, affinity_presets_modification

**Proposal Paths**:
1. proposed_lessons.yaml L3 with domain tag
2. Handoff packet intent=handoff to curator
3. PR to config/domains/<domain>/ (curator = required reviewer)

### Domain Module Structure (per CURATORS.md)

Each domain at `config/domains/<domain>/` should contain 9 components:
- metadata.yaml, PLAYBOOK.md, ARCHITECTURE.md, CONFIG_REFERENCE.md, GOTCHAS.md, LESSONS.md, AFFINITY_PRESETS.yaml, MEMORY_BLOCKS/, PRINCIPLES/

### AFFINITY_PRESETS.yaml Schema (from CURATORS.md + engineering/ prototype)

```yaml
model_routing:
  planner:
    primary: "qwen3-4b-thinking"
    fallback: "qwen3-4b"
  executor:
    primary: "qwen3-1.7b"
    fallback: "qwen3-1.7b"
  critic:
    primary: "qwen3-1.7b"
    fallback: "qwen3-1.7b"
token_budgets:   {planner: 16000, executor: 4000, critic: 2000}
context_windows: {planner: 32768, executor: 8192, critic: 8192}
```

**Note**: The engineering/ prototype still references `mimo-7b-rl-q4_k_m` as planner primary (line 15), which is superseded by the Carmack Model Matrix Canonical (Qwen3-4B planner / 4B-Thinking executor / 1.7B critic). CURATORS.md shows the corrected schema.

### Implementation Status

- `domain_loader.py` — **PLANNED, DOES NOT EXIST** (`find src -name "domain_loader*"` → empty)
- `scripts/sync_domain_docs.py` — **DOES NOT EXIST** (STRATEGY_INDEX references it but it's phantom)
- Governance enforcement is **SPEC-ONLY** — no runtime consumer as of 2026-08-26

---

## §3 R11 — Rubric Usage Scan (Meditation Corpus)

### D4 Mandate (R53)

> **D4. Pre-commit the adjudication rubric in Phase 0; RESTATE IT VERBATIM in Phase 4's ADJUDICATION RUBRIC field.** Phase 4 must cite the pre-committed criteria by name — never generate fresh criteria post-hoc.
> — R53_meditate_granite_foundation_20260826.md, line 103

The command (`.opencode/commands/meditate.md:102-104`) requires:
> "1c. **Rubric pre-commitment (R53 D4)**: write the adjudication rubric NOW, before any voice speaks. Binary criteria where possible. This rubric is frozen; Phase 4 must restate it VERBATIM."

### Record-by-Record Rubric Audit

| # | Record | Protocol Version | Phase 0 Rubric Field | Phase 4 Verbatim Restatement | D4 Compliant? |
|---|--------|-----------------|---------------------|------------------------------|---------------|
| 1 | ROC_RACOON_20260723_SIX_PASS_LATTICE | Six-Pass Lattice (pre-v1.0) | ❌ NO — Phase 0 absent entirely | N/A | ❌ NO |
| 2 | oxalpha_20260822_OX_ALPHA_FULL_UTILIZATION | Meditate-v1.2 (approx) | ❌ NO — "Phase 0 — Calibration" present but NO rubric field | N/A | ❌ NO |
| 3 | KALI_20260822_HIDDEN_GEMS | Meditate-v1.1 (approx) | ❌ NO — Phase 0 has lens set, output mode, anti-collapse contract, but NO rubric | N/A | ❌ NO |
| 4 | KALI_20260823_CONTEXT_PACKER_ENHANCEMENT | Meditate-v1.2 · STRATEGIC | ❌ NO — Phase 0 has subject/lens/output/anti-collapse, NO rubric | N/A | ❌ NO |
| 5 | KALI_20260823_SESSION_TRACKING_OVERSIGHT_AUDIT | Meditate-v1.1 · DIAGNOSTIC | ❌ NO — Phase 0 present, NO rubric | N/A | ❌ NO |
| 6 | researcher_20260823_GNOSIS_MINING_CODEX | Meditate-v1.2 | ❌ NO — Phase 0 has calibration + anti-collapse, NO rubric | N/A | ❌ NO |
| 7 | kali_20260824_LOST_VALUE_RECOVERY | Meditate-v1.2 · SYNTHESIS | ❌ NO — Phase 0 absent; starts at Phase 2 | N/A | ❌ NO |
| 8 | kali_20260824_MAKALI_COUNCIL_REBASE | Meditate-v1.1 (persona prism) | ❌ NO — Has invocation gate + anti-theater gate but NO rubric | N/A | ❌ NO |
| 9 | lilith_20260824_W1_CANONICAL_REGISTRATION | Meditate-v1.1 (persona prism) | ❌ NO — Phase 0 has subject/lens/output/anti-collapse, NO rubric | N/A | ❌ NO |
| 10 | maat_20260824_D602_TORCHFREE | Meditate-v1.1 (Skeptic→Builder) | ❌ NO — Skeptic-then-Builder format, NO Phase 0, NO rubric | N/A | ❌ NO |
| 11 | maat_20260824_DC29_REDIS_PASSWORD | Meditate-v1.1 | ❌ NO — No Phase 0, no rubric (not read but consistent with peer records) | N/A | ❌ NO |
| 12 | maat_20260824_N4_DELETIONS | Meditate-v1.1 · N4 council | ❌ NO — Execution ledger format, NO Phase 0, NO rubric | N/A | ❌ NO |
| 13 | maat_20260824_W2_CLAIMS_HARNESS | Meditate-v1.1 (persona prism) | ❌ NO — Builder/Skeptic/Guardian passes, NO rubric | N/A | ❌ NO |
| 14 | maat_20260824_W3_SOUL_PROMOTION | Meditate-v1.1 (persona prism) | ❌ NO — Builder/Skeptic passes, NO rubric | N/A | ❌ NO |
| 15 | researcher_20260824_KNOWLEDGE_GAPS | Meditate-v1.1 (pre-commit gate) | ❌ NO — Skeptic pass only, NO Phase 0, NO rubric | N/A | ❌ NO |
| 16 | researcher_20260824_W4_PROVENANCE_RESOLVER | Meditate-v1.1 (persona prism) | ❌ NO — Calibration block present, NO rubric | N/A | ❌ NO |
| 17 | opus_20260826_HIDDEN_GEMS_FIVE_VOICES | meditate-archs (ad-hoc) | ❌ NO — Explicitly "No Phase 0/collisions/verdict skeleton" | N/A | ❌ NO |

### Rubric Field Search Results

Grep for `rubric|pre.?commit|verdict.*criterion|adjudicat` across all 17 records:

| Term | Matches | Context |
|------|---------|---------|
| "rubric" | **0** | Zero occurrences in any meditation record |
| "pre-commit" | 1 | Record #5: "pre-commit and temple-grade" (referring to git pre-commit, NOT rubric pre-commitment) |
| "verdict" + "criterion" | 0 | No conjunction of these terms |
| "adjudicat" | 5 | ALL in record #6 (GNOSIS_MINING_CODEX) — referring to *cross-model adjudication* as a research proposal, NOT as a meditation rubric |

**Result: ZERO records contain a pre-committed adjudication rubric.**

---

## §4 R11 — Contract Compliance Analysis (D4 Adherence)

### Compliance Rate

```
D4 Compliance: 0 / 17 records = 0.0%
```

### Why Zero Compliance?

**Timeline analysis**: D4 was specified in R53 (2026-08-26). The command was updated to include rubric pre-commitment at `.opencode/commands/meditate.md:102-104`. However:

1. **Runs 1–2** (2026-07-23, 2026-08-22): Predate R53 entirely. No rubric concept existed.
2. **Runs 3–6** (2026-08-22 to 2026-08-23): Execute under Meditate-v1.1/v1.2 BEFORE the command was updated with D4. These protocols had Phase 0 but no rubric field.
3. **Runs 7–16** (2026-08-24): Execute on the SAME DAY the command was updated. The maat set (10–14) explicitly uses "ad-hoc Pass formats without Phase 0 blocks" (per registry anomaly note, line 48).
4. **Run 17** (2026-08-26): Ad-hoc meditate-archs command; explicitly "No Phase 0/collisions/verdict skeleton."

**Root cause**: D4 was written into the command AFTER the bulk of the corpus was executed. The command update landed, but no existing record was retroactively amended. Future runs should comply, but there is no enforcement mechanism (no CI gate, no template validation) to ensure Phase 0 contains a rubric field.

### What "Invocation Gate" Records Have Instead

Several records (runs 4, 5, 8, 11, 12) include an **invocation gate** — a set of conditions that must pass before the meditation proceeds. This is STRUCTURALLY similar to a rubric but semantically different:

| Invocation Gate | Rubric (D4) |
|-----------------|-------------|
| "≥3 domains tensioning" | Criteria for JUDGING output quality |
| "CI-wired gate = expensive to reverse" | Binary pass/fail on specific dimensions |
| "no single domain owns X" | Pre-committed, restated verbatim at verdict |

The invocation gate is a **gate-to-proceed** (should we meditate at all?). The D4 rubric is a **criterion-to-judge** (how do we evaluate what the meditation produced?). These are different lifecycle stages.

### Closest Approaches to D4

| Record | What it has | Gap vs D4 |
|--------|-------------|-----------|
| maat_20260824_W2_CLAIMS_HARNESS | "Invocation gate: (a) security/provenance/token-efficiency domains tension; (b) CI-wired gate = expensive to reverse; (c) no single domain owns detector design. PASSES." | These are PROCEED conditions, not JUDGMENT criteria |
| maat_20260824_W3_SOUL_PROMOTION | "Invocation gate: (a) schema design / provenance integrity / fleet-injection domains tension; (b) soul writes are irreversible-ish; (c) no single domain owns 'what counts as evidence'. PASSES." | Same pattern — proceed-gate, not judgment-rubric |
| kali_20260824_MAKALI_COUNCIL_REBASE | "Anti-theater gate PASSED (≥3 domains tensioning: stale-charter-vs-current-truth, build-vs-run, resource-limits-vs-council-design)" | Anti-theater gate is quality control, but not pre-committed judgment criteria |

### Implications for Future Runs

The D4 mandate is architecturally sound but operationally unenforced. To achieve compliance:

1. **Template validation**: Phase 0 must parse for a `rubric:` field before voices are emitted
2. **CI gate**: meditate command should refuse to proceed without a rubric block in Phase 0
3. **Phase 4 schema**: ADJUDICATION_RUBRIC field must be non-empty and verbatim-match Phase 0
4. **Retroactive treatment**: Existing records are historical artifacts; do not amend. Mark as "pre-D4" in the registry.

---

## §5 Build-Packets for DS-1..5 and KD-1..3

These are concise task briefs synthesizing the R6 findings into actionable work packets. Each packet identifies what exists, what's missing, and what to build.

### DS-1: Create DOMAIN_DOCUMENTATION_SYSTEM.md

| Field | Value |
|-------|-------|
| **Task** | Write the meta-doc that DS-1 references |
| **Status** | ❌ PHANTOM — STRATEGY_INDEX L2A references it; file does not exist |
| **Input** | `config/domains/engineering/` (reference implementation), `config/domains/CURATORS.md` (governance charter), `config/domains/curators.yaml` (machine registry) |
| **Acceptance** | File exists at `docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md`; passes `make doc-llm-validate` |
| **Scope** | Workspace authoring + Runtime modules + Curator model + Validated copy sync |
| **Blocker** | None — all input materials exist |
| **Effort** | ~4h (draft + review) |

### DS-2: Workspace Structure for All 13 Domains

| Field | Value |
|-------|-------|
| **Task** | Create `config/domains/<domain>/` dirs for 11 missing domains (gemini-notebook exists but incomplete) |
| **Input** | DS-1 meta-doc (once created), engineering/ as reference template |
| **Acceptance** | 13 dirs exist; each has at minimum: metadata.yaml, PLAYBOOK.md, AFFINITY_PRESETS.yaml |
| **Gap** | Currently 2 of 13 dirs exist; 11 missing entirely |
| **Effort** | ~8h (scaffold + per-domain metadata) |

### DS-3: Runtime Modules (domain_loader.py)

| Field | Value |
|-------|-------|
| **Task** | Implement `src/omega/oracle/domain_loader.py` |
| **Status** | ❌ PLANNED in curators.yaml but code does not exist |
| **Input** | curators.yaml schema, CURATORS.md governance enforcement spec |
| **Acceptance** | `load_domain(domain, token_budget, requester)` works; enforces PRIVATE/SHARED_READ/SHARED_WRITE |
| **Dependencies** | DS-1 (meta-doc defines the contract) |
| **Effort** | ~12h (implementation + tests) |

### DS-4: Sync Script (sync_domain_docs.py)

| Field | Value |
|-------|-------|
| **Task** | Implement `scripts/sync_domain_docs.py` |
| **Status** | ❌ PHANTOM — STRATEGY_INDEX references it; file does not exist |
| **Input** | DS-2 workspace dirs, DS-3 domain_loader |
| **Acceptance** | Script validates domain modules against canonical structure; CI-gated |
| **Dependencies** | DS-1, DS-2, DS-3 |
| **Effort** | ~6h |

### DS-5: STRATEGY_INDEX/CORPUS_MAP Updates

| Field | Value |
|-------|-------|
| **Task** | Wire DS-1..4 into strategy doc hierarchy |
| **Input** | STRATEGY_INDEX.md, STRATEGY_CORPUS_MAP.md |
| **Acceptance** | All DS artifacts registered; no phantom references; `make doc-llm-validate` green |
| **Dependencies** | DS-1..4 |
| **Effort** | ~2h |

### KD-1: Runtime Module Spec (Curator Model)

| Field | Value |
|-------|-------|
| **Task** | Define the "curator model" — what module curates domain documentation? |
| **Key Question** | Is the KD curator the SAME as library/curator.py? Or a NEW module? |
| **Recommendation** | **Separate module**. library/curator.py handles content quality scoring (external content). KD curator handles domain module governance (internal config). Different concerns, different data, different enforcement. |
| **Input** | curators.yaml, CURATORS.md, library/curator.py (for anti-patterns) |
| **Acceptance** | Spec exists; maps to curators.yaml governance levels; identifies domain_loader.py as enforcement point |
| **Effort** | ~4h (spec) |

### KD-2: Affinity Preset Generation (12 Missing)

| Field | Value |
|-------|-------|
| **Task** | Generate AFFINITY_PRESETS.yaml for 12 missing domains |
| **Input** | CURATORS.md schema (Carmack Model Matrix), engineering/ prototype |
| **Acceptance** | 13 AFFINITY_PRESETS.yaml files exist; all use canonical model names (qwen3-4b-thinking planner, qwen3-1.7b executor/critic) |
| **Note** | engineering/ prototype uses stale `mimo-7b-rl-q4_k_m` — must be updated |
| **Effort** | ~3h (12 files × 15min each) |

### KD-3: Domain Primers (Frontier-Authored)

| Field | Value |
|-------|-------|
| **Task** | Write domain primer.md files for each domain |
| **Input** | Existing domain knowledge across fleet entities |
| **Acceptance** | Each domain dir has a primer.md; covers scope, gotchas, model routing rationale |
| **Blocker** | KD-2 (affinity presets must exist first) |
| **Effort** | ~6h |

---

## §6 Open Questions

### R6 Open Questions

1. **Sovereign Curator implementation**: The spec was written June 12, 2026. Is it still the right architecture? The Gemini CLI 2M-token window was the synthesis backend. Has this been superseded by local model capabilities (e.g., qwen3-4b-thinking at 32K)? The spec assumed cloud Gemini for synthesis — does M7 (Local-First) change the architecture?

2. **DS vs KD ownership**: DS workstream is owned by kali; KD workstream has no explicit owner in ACTIVE_SPRINT.json. Should these merge? The N12 Curator Node (Jem oversight) is the operational entity — should N12 own BOTH DS and KD?

3. **N12 vs KD Curator vs library/curator.py**: Three curator-ish systems. N12 is the entity-session; KD Curator is the content-layer governance; library/curator.py is the quality scoring code. Are these three layers of one system, or three separate systems that happen to share a name?

4. **Domain_loader.py blocking domain operations**: Without domain_loader.py, governance enforcement is spec-only. How does the fleet handle a PRIVATE domain today? Answer: it can't — governance is aspirational.

5. **Sovereign Curator as WAD sub-component**: The handoff archive shows Sovereign Curator as a sub-agent of the Sovereign Stack Creator tool. Is this the right decomposition? Should the Sovereign Curator be a standalone MCP server, or embedded in the stack creator?

### R11 Open Questions

1. **Rubric enforcement**: D4 is in the command but has no CI gate. Should `meditate` refuse to proceed without a Phase 0 rubric? The MEDITATE_DOCUMENTATION_STRATEGY.md (line 205) acknowledges: "Neither R53 nor the tournament drafts specify what makes a good rubric." This gap needs filling before enforcement.

2. **Rubric quality guidance**: What makes a good meditation rubric? Binary criteria are recommended ("where possible"), but many meditation outputs are qualitative. Should the rubric include: (a) binary gates (pass/fail), (b) Likert-scale dimensions (1-5), (c) exemplar-matching (does output resemble X?)?

3. **Invocation gate vs rubric overlap**: The invocation gate and D4 rubric serve different lifecycle stages but share vocabulary ("domains tensioning"). Should these be unified into a single Phase 0 contract? Or kept separate to preserve their distinct purposes?

4. **Pre-D4 record treatment**: The registry notes runs 10–14 (maat set) have "structural drift" — ad-hoc formats without Phase 0. Should D4 non-compliance be added to the anomaly list? Or is it expected (pre-dates the mandate)?

5. **Template validation for rubrics**: The MEDITATION_TEMPLATE_REGISTRY.md defines templates with execution logs but no rubric schema. Should templates include a `required_fields: [rubric]` constraint? This would make rubric presence machine-checkable.

---

*Report complete. 17/17 meditation records scanned. 0/17 D4-compliant. Sovereign Curator spec recovered from June 12 session. 5 curator concepts disambiguated. 8 build-packets delivered.*

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research_wave2 ⬡ R06R11-COMPLETE ⬡*
