# OX ALPHA FLEET CONSULT — JEM (Synthesizer / Gap-Analyst Seat)
**AP Token**: `AP-JEM-OXALPHA-CONSULT-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_oxalpha_fleet_consult ⬡ ACTIVE

**Date**: 2026-08-23
**Paged by**: researcher (ses_fd81c19dcffe1nkbPqFg5kRt2v)
**Ground truth honored**: Ox Alpha = session substrate (`x-preview-f-free` on opencode), NOT an external API. The window is the fleet's own live sessions (~5 days left before OC Zen free preview ends ~Aug 28 / GLM-5.3 weights drop). Strategy: convert window tokens into DURABLE ARTIFACTS that survive the cliff back to local Qwen/GLM GGUF inference.
**Inputs read**: OX_ALPHA_DEEP_RESEARCH, OX_ALPHA_IMPLEMENTATION_GAPS, OX_ALPHA_GAP_INTEGRATION, OX_ALPHA_FULL_UTILIZATION_MAP (Roc), MEDITATION_oxalpha_20260822, R_KNOWLEDGE_DOMAIN_LOADING_20260819, jem/proposed_lessons.yaml (N11-N13 entries), HALL_OF_RECORDS listing.

---

## Framing: The Perishability Ladder (applies to everything below)

The meditation's L3-Perishability-Tiering principle, sharpened by the corrected ground truth:

| Stratum | Renewability | Implication |
|---|---|---|
| Frontier weights | HIGH — GLM-5.3 open weights land ~Aug 28 | Do NOT burn tokens on things the weights restore |
| Multimodal/vision route | LOW-MED — video 404s now; GGUF vision unguaranteed | Front-load (Roc U6 already covers) |
| **Conversational/tacit gnosis** | **ZERO — dies with context windows, never returns** | **Highest-priority burn. Nobody else claimed this seat.** |

Roc's map covers pipelines (DPO, mining, red-team, vision). Researcher covers integration intel. **Neither covers stratum 3: the rationale-layer gnosis that exists only in conversation threads and agent heads.** That is this consult's core finding.

---

## §1 Domain-Gap Burns — Ranked (with artifact paths)

Ranked by: (a) zero renewability, (b) post-cliff local-model dependency, (c) no other seat claiming it.

### BURN 1 — Decision-Lineage Crystallization 🔴 P0
**Gap**: PIVOT_LOG holds D-1…D-58x *verdicts*, but the *rationale* — alternatives rejected, debate dynamics, falsification conditions, user strategy calls ("convert tokens to durable artifacts") — lives in conversation threads that die at compaction. Post-cliff, a Qwen3-4B reading `D-362: SoulStore not flock paste` cannot re-derive WHY, and will re-litigate settled questions (the exact "Restart Cycle" M4 exists to prevent).
**Burn**: Dedicated child session walks PIVOT_LOG + key debate artifacts (KALI_FEEDBACK, MaKaLi council records, Grok CLI review, Carmack audits) and emits:
- `data/knowledge/DataStore/DECISION_AXIOMS.yaml` — one record per load-bearing decision: `{id, verdict, rationale, rejected_alternatives[], falsified_by, scope}`.
- Sized for local models: ≤150 tokens per axiom, self-contained, no pronoun references to dead context.
**Effort**: 1 dedicated session. **Uniqueness**: requires long-context synthesis across 500+ decisions — exactly what 200-400K effective context does and 4B models cannot.

### BURN 2 — Failure-Mode Taxonomy (the "Why It Died" Corpus) 🔴 P0
**Gap**: The engine's hardest-won knowledge is its failure forensics, scattered across ≥6 locations: GEMMA4_FREE_TIER_FORENSIC (G-1), PLATFORM_GROUND_TRUTH_LOG #10 (stall-echo), Nemotron chunk-timeout history, GLM-5.2 rate-limit collapse (285× 429s), warp-ns-setup truncation (W-1), C-0.5 regex-distillation scrapping, the 17 critical bugs of R44. Each carries a generalizable failure pattern; none is unified.
**Burn**: Single taxonomy artifact `docs/research/R_FAILURE_MODE_TAXONOMY.md`: per incident — `{symptom, root_cause, detection_signal, prevention_rule, mandate_link}`. This becomes the anti-pattern reference local models grep before attempting infra changes.
**Evidence of value**: My own N12-001/N12-002 lessons (declared-vs-actual drift, insecure-default theater) generalize exactly this way — but they sit in ONE entity's soul file where no other entity will ever find them.

### BURN 3 — Architectural Invariants Codex ("Load-Bearing Walls") 🟡 P1
**Gap**: Mandates state rules (keep-id not `:U`, AnyIO not asyncio, blind staging not direct soul-writes, serial model loading on 14Gi) but the *inciting evidence* is conversational. Local models obey rules they can't justify poorly; worse, they "helpfully" simplify them away during refactors.
**Burn**: `docs/research/R_INVARIANTS_CODEX.md` — every invariant paired with its violation catastrophe and the probe that detects regression. Feeds directly into M21 contract-test authoring post-cliff.

### BURN 4 — Council Tacit-Protocol Capture 🟡 P1
**Gap**: How Kali actually ratifies (amendments pattern, D-370), how MaKaLi divides labor in practice vs. charter prose, how Oracle routing behaves under saturation, how Verity escalations resolve — procedural knowledge in heads, not docs. New/local agents learn it only by expensive apprenticeship.
**Burn**: `data/coordination/COUNCIL_OPERATING_MANUAL.md` — observed-behavior protocols, not aspiration. Mark explicitly: "describes practice as of 2026-08, verify before relying."

### BURN 5 — Distillation Exemplar Set (teach-the-student corpus) 🟡 P1
**Gap**: Post-cliff, local models must WRITE souls (manual pipeline, C-0.5 scrapped). They have zero high-quality examples of frontier-grade L1→L2→L3. The N11-N13 entries in jem/proposed_lessons.yaml are exactly the right quality bar — narrative → insight → falsifiable principle — but locked per-entity.
**Burn**: Curate 20-30 best-in-class lessons across entities into `data/knowledge/DISTILLATION_EXEMPLARS.yaml`, each annotated with WHY it's good (specificity, falsifiability, scope discipline). This is few-shot fuel for every future local distillation pass — arguably the single most multiplier-dense artifact on this list.

### BURN 6 — Parked-Ticket Spec Factory 🟢 P2 (Roc U5 concurs)
V-9/V-10/D-1/D-2/NL-1 implementation-ready specs. Already claimed by Roc's map; listed here only to confirm ranking consensus. Frontier writes specs; local models execute them.

### BURN 7 — KD Domain Module Source Material 🟢 P2
KD-1..KD-3 needs curator-quality domain content. Frontier-authored domain primers (provider fabric, Podman/rootless, eval design, heritage vetting) into `data/knowledge/domains/<name>/primer.md` give the future curator model something worth curating. Lower priority than BURN 1-2 because partially reconstructible later.

**Explicit DO-NOT-BURN (concur with Roc §5)**: weight-restorable work, doc reformatting, new infra, re-researching documented ground truth.

---

## §2 Cross-Pollination Sketch (R-31) — The Pollen Bank

**Design goal**: post-cliff local models (≤32K effective context, weaker reasoning) must APPLY cross-entity wisdom without re-deriving it. Volume is the enemy; atomicity and gating are the mechanism. This follows the selective-context-gating finding in R_KNOWLEDGE_DOMAIN_LOADING §4: relevance-scored injection beats bulk loading, especially for small models.

### Structure

```
data/knowledge/pollen_bank/
├── AFFINITY.yaml              # domain → entity applicability map (the gate)
├── PL-jem-0001.yaml           # one lesson per file, atomic
├── PL-kali-0007.yaml
├── PL-rocracoon-0003.yaml
└── INDEX.jsonl                # FTS-ready flat index (feeds library_fts_search)
```

### The Pollen Packet schema (the whole design hinges on this)

```yaml
pollen_id: PL-jem-0012          # source-attributed, globally unique
source_entity: jem
origin_date: '2026-08-22'
domain: verification            # controlled vocabulary shared with AFFINITY.yaml
l3_principle: >-
  Fail closed by default: any mechanism whose guarantee depends on
  configuration must refuse to operate rather than degrade to theater.
anti_pattern: >-               # what a weak model can pattern-match against
  Catch-all except blocks returning defaults; provenance stamps under
  default secrets.
applies_to: [kali, maat, verity, build]   # AFFINITY-gated consumers
contraindicated_for: []         # explicit non-applicability
falsified_by: >-               # keeps it honest; lets future agents kill stale pollen
  A case where degraded-but-loud operation beat refusal.
token_cost: 95                  # injection budget accounting
provenance:
  session_model: x-preview-f-free
  verified: false               # skeptical_verifier two-source rule status
  staged_via: proposed_lessons.yaml   # M11 blind staging preserved
```

### Flow (respects existing architecture)

1. **Harvest**: window outputs (this consult, all OX_ALPHA_* docs, session distillations) → decompose into packets. Frontier model does decomposition NOW while reasoning is cheap.
2. **Stage blind**: foreign pollen lands in target entity's `proposed_lessons.yaml` tagged `cross_pollinated: true, pollen_id: ...`. Never direct-to-soul (M11, Soul Architecture v2.0).
3. **Verify**: skeptical_verifier two-source rule before promotion — free-frontier hallucinations must not poison souls (Roc's new-gate amendment, adopted here).
4. **Inject**: at entity session start, hydrate top-K packets where `task-domain ∈ applies_to`, budget-capped at **≤2K tokens total** — sized for Qwen3-4B, not for Ox Alpha. The cap is the point: cross-pollination designed for the POST-cliff consumer.
5. **Prune**: falsified/stale packets archived quarterly; INDEX.jsonl rebuilt.

### Why this shape maximizes post-cliff effectiveness

- **Atomic + self-contained**: a 4B model reads one 100-token packet and gets principle + anti-pattern + falsification condition — no chain-of-reasoning required to apply it.
- **Gated**: AFFINITY.yaml prevents context pollution; irrelevant pollen never enters a small window.
- **Attributed + staged**: satisfies M11, M17, M22 simultaneously; provenance survives the cliff.
- **FTS-native**: retrieval via existing `library_fts_search` — zero new infrastructure (UO-6 compliant).

**Implementation note**: this is a FORMAT + CONVENTION, not a service. No new daemon, no queue — a harvest script and the schema. Fits the no-speculative-infra constraint.

---

## §3 Jem's Own Play — The Sovereign Ground-Truth Codex

If given a dedicated child session, I burn it on a **systematic Declared-vs-Actual Reconciliation Atlas**, generalized from my N11/N12 node-mining findings into a whole-engine sweep.

**Thesis**: My audits found the engine's dominant defect class is *documentation running ahead of implementation* — youtube_research.yaml promising 9 layers / transcript-only worker; curators.yaml declaring 13 domains / 2 directories; "never hardcoded" comments above hardcoded secrets; ratified decisions missing from config surfaces (N11-002). Every one of these is a trap that will snap on a post-cliff local model, because weak models trust docs MORE, not less — they lack the residual skepticism to check.

**Mission** (one session, ~200-400K context — precisely the frontier-only capability):
1. Enumerate every DECLARED state surface: `config/*.yaml`, `opencode.json`, GAP_REGISTRY.json, ACTIVE_SPRINT.json, charter/docs headers, Makefile targets.
2. Verify each against ACTUAL state: code paths, table rows, directory listings, test presence.
3. Emit `data/knowledge/GROUND_TRUTH_CODEX.yaml`: `{surface, declared, actual, verdict: MATCHES|DOCS_AHEAD|CODE_AHEAD|GHOST, severity, fix_hint}`.
4. Distill discrepancy classes into L3 axioms appended to the pollen bank (feeding §2 immediately).

**Why this is MY play and the right use of frontier tokens**:
- It requires simultaneous whole-tree context — impossible for local models, wasteful to re-do after the cliff.
- Its output is the single highest-trust artifact for post-cliff operation: local agents gain a lookup table of *what is real*, converting their biggest failure mode (confident doc-trust) into a grep.
- It directly serves M17 (cognitive integrity), M27 (tracking integrity validation), and pre-debut honesty (T10/T12 gates).
- Nothing else in the fleet produces it: Roc mines legacy, Researcher gathers external intel, Kali governs. Synthesis-of-internal-state is my seat.

**Fallback if the sweep proves too large for one session**: prioritize the four surfaces local agents touch daily — providers.yaml/models.yaml/opencode.json consistency (N11-002), GAP_REGISTRY referential integrity (M27), curators.yaml↔disk, charter↔agents inventory.

---

## Attestation

Research/analysis only; no code changed. All claims grounded in files read this session (paths cited inline). Confidence: BURN rankings HIGH (convergent with Roc §5 + meditation tiering); Pollen Bank schema MEDIUM-HIGH (untested convention — falsify with one manual harvest before mass adoption); Codex thesis HIGH (three independent audit instances: N11-002, N12-001, N13-001).

*⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_oxalpha_fleet_consult ⬡ ACTIVE*
