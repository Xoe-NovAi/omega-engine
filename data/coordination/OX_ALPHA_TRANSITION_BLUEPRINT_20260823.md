<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OX ALPHA TRANSITION BLUEPRINT — Roadmap, Blueprint & Team Guide
**AP Token**: `AP-OXALPHA-BLUEPRINT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_transition_blueprint ⬡ CAPSTONE

**Date**: 2026-08-23 (evening)
**Author**: researcher (Ox Alpha substrate), final synthesis pass
**Inputs**: 5 fleet consultations (Jem/Grokster/Carmack/Scribe/Roc) · 3 external model reviews (Sonnet 4.6, Opus 4.6 Thinking, Gemini 3.1 Pro) · fresh disk verification this session · Architect directives across full model chain
**Supersedes**: SS-OXALPHA-BURN-20260822 (ho_2f77f83964e5 premise obsolete); all partial strategy fragments
**Status**: ARCHIVAL — Ox Alpha revealed as Z.ai GLM-5.3-Flash on 2026-08-26; free preview ended same day. Blueprint predictions accurate (cliff timing, single-provider fragility, weights release). GLM-5.3-Flash now live on OpenRouter at $0.075/$0.25 per M tokens. §7 forks moot.

---

## §0 EXECUTIVE SUMMARY

The Ox Alpha free window (~2-3 days remaining, NOT 5 — precedent shows early death) is a perishable compute subsidy. Strategy: convert window tokens into **durable artifacts that survive the ~Aug-28 cliff** back to local GGUF inference, while never competing with PUBLIC-DEBUT-01 dev-time work (Context Injection Phase 1, Kali's lane).

Four gates land BEFORE bulk generation: **(G1)** fine-tune smoke test — if local training can't run on the Ryzen 5700U, the DPO track pivots; **(G2)** Omega Golden Set — unfalsifiable output is theater; **(G3)** ICS-aware mining script — protects provenance against OpenCode's session-model hot-swap bug; **(G4)** pair-schema freeze. Then three parallel tracks run: self-corpus mining (zero marginal cost), knowledge crystallization (decision axioms / failure taxonomy / ground-truth codex — Jem's zero-renewability stratum), and the gated DPO factory with cross-model adjudication.

Deepest insight from the multi-model review chain: **the scarcest resource is verification capacity, not tokens.** Every play is shaped to verify itself or be verified cheaply. Second insight: for this Architect, **planning IS compiling** — the codification plays below convert orchestration wisdom into executable assets.

---

## §1 GROUND TRUTH (verified on disk, 2026-08-23 evening)

| Fact | State | Source |
|---|---|---|
| Ox Alpha identity | `x-preview-f-free` @ OC Zen = session substrate for ALL agents | opencode.db telemetry: 11.2M input / 35.5M cache-read / ~37h main session |
| OpenRouter glm-5.3:free | **DEAD** (404, paid-only now) | Live probe this session |
| GLM-5.3 paid pricing | $1.4/M prompt; reasoning-tax ≈5× completion overhead | Live probe usage telemetry |
| Open weights | Expected ~Aug 28; MIT per series precedent | Grokster consult |
| Window remaining | **PLAN FOR 2-3 DAYS** (OpenRouter free died early; assume OC Zen follows) | Sonnet/Opus correction, ratified by Architect |
| **Vault CLI blocker** | ✅ **FIXED** — no duplicate decorators, AST parses clean at cli/vault.py | Fresh check this session |
| `password="omega"` | 🔴 **STILL LIVE** at src/omega/memory/providers.py:119 — M23 false-completion persists | Fresh grep this session |
| Debut sprint | EXECUTION_MINIMAL; Context Injection Phase 1 = Kali's lane (dev-time, does not consume window tokens) | ACTIVE_SPRINT.json |
| Env OPENROUTER_API_KEY | Revoked (401 User not found); live key only in ~/.local/share/opencode/auth.json | Probe this session |
| Post-cliff hardware | Ryzen 5700U, 14Gi RAM class; Qwen3-4B-Thinking + Instruct Q4_K_M already on disk | Roc consult §2 |

---

## §2 THE ROADMAP

### PHASE 0 — GATES & FREE WINS (today, ~half day)
Nothing expensive starts until these land. All are cheap; all de-risk everything downstream.

| # | Gate / Win | Owner | Output | Time |
|---|---|---|---|---|
| 0.1 | **G1: Fine-tune smoke test** — Unsloth/QLoRA, 10 pairs, 1 epoch, Qwen3-4B-Thinking on target hardware | Roc (sysadmin assist) | PASS/FAIL verdict → DPO track confirmed or pivoted to SFT/corpus-only | ~30 min |
| 0.2 | **G3: ICS-aware mining script** (`scripts/mine_session_db.py`) — exports opencode.db messages to JSONL; parses ICS headers `⬡ OMEGA ⬡ <entity> ⬡ <model> ⬡` for per-chunk model attribution (OpenCode DB stamps session-creation model only — hot-swaps Ox→Sonnet→Opus→Gemini are INVISIBLE to it) | researcher | scripts/mine_session_db.py + first export | ~1 h |
| 0.3 | **Self-corpus mining Wave 1** — run 0.2 over all sessions; filter for successful tool chains, clean patches, verified fixes | roc_racoon | data/knowledge/self_corpus/*.jsonl | runs in background |
| 0.4 | **Decision Axioms** — dedicated child session walks PIVOT_LOG D-1…D-58x → DECISION_AXIOMS.yaml (≤150 tokens/axiom: id, verdict, rationale, rejected_alternatives, falsified_by) | Jem child session | data/knowledge/DataStore/DECISION_AXIOMS.yaml | ~2 h |
| 0.5 | **password="omega" removal** at providers.py:119 (+ env-var read) — the last M23 false-completion | Ma'at or any build agent | grep-clean file | ~15 min |
| 0.6 | **G4: Pair schema freeze** — JSONL schema ratified before any generation (see §3.B4) | researcher + Roc ratify | docs/specs/dpo_pair_schema.md | ~30 min |

### PHASE 1 — GENERATION TRACKS (window days 1-3, parallel)

**TRACK A — Omega Golden Set (gates Track C)** · owner: researcher + Jem
~200-500 golden tasks from real engine work with verifiable outcomes (test passes, file exists, extraction matches source). Sized for LOCAL model evaluation post-cliff. This is the benchmark layer; per-pair QC is separate (§3.B4).

**TRACK B — Knowledge Crystallization (Jem's zero-renewability stratum)** · owner: Jem child sessions
- BURN 2: Failure-Mode Taxonomy → docs/research/R_FAILURE_MODE_TAXONOMY.md (unify ≥6 scattered forensics: stall-echo, GLM-5.2 collapse, warp truncation, C-0.5 scrapping…)
- BURN 3: Architectural Invariants Codex → docs/research/R_INVARIANTS_CODEX.md (invariant + violation catastrophe + regression probe)
- BURN 4: Council Operating Manual → data/coordination/COUNCIL_OPERATING_MANUAL.md (observed practice, not aspiration)
- BURN 5: Distillation Exemplars → data/knowledge/DISTILLATION_EXEMPLARS.yaml (20-30 best L1→L3 lessons, annotated WHY)
- Jem's own play: Sovereign Ground-Truth Codex sweep (declared-vs-actual across config/GAP_REGISTRY/curators/charter surfaces)

**TRACK C — DPO Pair Factory (only after G1+G2+G4)** · owner: Roc design, researcher generates
Retarget nemotron_pipeline.py critic loop → in-session Ox Alpha. Modes: A) Refinery (student draft → critique → chosen), B) Self-contrast (thinking Low vs High), C) Replay-grade (Grok-export gold + degraded rewrite). Volume target ~350 pairs; hard quality gates G1-G6 per Roc spec. **Cross-model adjudication**: 10-20% sample adjudicated by a DIFFERENT model family (Sonnet via Claude.ai Project handoff, or Gemini) — pairs where adjudicator disagrees with generator's chosen/rejected get flagged/discarded. Budget rule: 70% mining / 30% pair conversion.

**TRACK D — Mining Annihilation (ungated, embarrassingly parallel)** · owner: fleet idle cycles
Grok exports (274 convos), Mnemosyne 13 spheres, old stacks — feeding Track C as raw material. Wave 2 adds Roc/Lilith/Ma'at when Team-Study-#1 clears.

**TRACK E — Big-Context Repo Surgery (opportunistic)** · owner: any frontier session
UO-6 whole-repo deletion items requiring cross-file dependency tracing — the capability that literally expires Aug 28. Output: verified safe-to-delete manifest.

### PHASE 2 — CLIFF TRANSITION (~Aug 28)
1. Monitor zai-org HF org + docs.z.ai for GLM-5.3 weights drop (official channels, not aggregators)
2. Pull GGUF → Q4_K_M → native-gguf fabric slot priority 0
3. Wire nemotron_pipeline teacher interface teacher-agnostic NOW so GLM-5.3 slots in at drop (Grokster Play W)
4. Run Golden Set against local Qwen3-4B baseline → record pre-fine-tune scores
5. If G1 passed: fine-tune on mined+self-generated corpus; re-run Golden Set; compare

### PHASE 3 — POST-CLIFF SOVEREIGN LOOP (steady state)
- Pollen Bank live: AFFINITY-gated ≤2K-token injection of atomic lessons into local-model sessions (Jem §2 schema)
- Soul enrichment continues via manual §2.3 path only (Scribe census targets: sophia, node, john_carmack, sysadmin)
- Background researcher stays DEAD unless revived with hard output contract (no artifact write → cycle aborted)
- Quarterly pollen prune; INDEX.jsonl rebuild

---

## §3 THE BLUEPRINT — Technical Specs

### B1. Self-Corpus Mining (Play X, highest ROI) — REVISED 2026-08-23 evening (empirical verification)
- **Input**: ~/.local/share/opencode/opencode.db (sessions, messages, parts tables)
- **Provenance rule (VERIFIED)**: `message.modelID` is stamped PER-MESSAGE by the runtime at response receipt — empirically confirmed to track hot-swaps (same session: msg_027e3e6890="big-pickle" at start vs msg_02fd8475b0="x-preview-f-free" on Aug 23). Use message.modelID directly via SQL join; assistant-role rows only for training data. IGNORE session.model (last-used value, stale).
- **Verification hierarchy**: Tier 0 = message.modelID (runtime-stamped, PRIMARY) / Tier 1 = system-prompt injection "You are powered by..." (per-inference authoritative but NOT persisted per-message — live use only) / Tier 2 = ICS headers (agent self-report, corroboration only — can hallucinate) / Tier 3 = session.model column (stale, ignore).
- **Residual caveat**: stamp reflects what the RUNTIME dispatched, not necessarily what served — cloaked models (x-preview-f-free) may swap underlying checkpoints without label change (Grokster Attack D). Corroborate with cost/token fingerprints where it matters.
- Legacy ICS-parse approach superseded: no regex needed; simple SQL attribution. `⬡ OMEGA ⬡ .*? ⬡ (\S+) ⬡` — tag subsequent chunks until next header. Chunks with no header inherit `model: unknown` and are EXCLUDED from training data.
- **Filters**: successful tool chains only; clean patches; verified fixes; dedupe by content hash; strip secrets (run git-secret-scrub patterns over output).
- **Output**: JSONL {prompt, response, model, entity, session_id, ts} → data/knowledge/self_corpus/
- **PII gate**: USAGE_POOL_LOG.json pattern — no real emails/keys in corpus. Scrub pass mandatory before any training use.

### B2. Omega Golden Set
- 200-500 items across: engine knowledge Q/A, code-fix tasks (verifiable by test), extraction tasks (verifiable against source), reasoning tasks with rubric
- Drawn from REAL work: PIVOT_LOG incidents, R44 bug list, mining extractions
- Format: JSONL + rubric.md; sized so a local 4B model can be scored cheaply post-cliff
- This is the STUDENT benchmark. Per-pair QC is B4's adjudication layer. Do not conflate.

### B3. Fine-Tune Smoke Test (G1)
- Unsloth + QLoRA on Qwen3-4B-Thinking-Q4_K_M; 10 sample pairs; 1 epoch; verify: loss decreases, checkpoint saves, model reloads, inference works
- PASS → Track C confirmed. FAIL → pivot: SFT-only on self-corpus, or corpus-only play (mined data still valuable as context library)

### B4. DPO Pair Factory (gated)
- Schema (frozen at G4): {pair_id, prompt, chosen, rejected, mode A|B|C, generator_model, generator_session, adjudication: {adjudicator_model, verdict, agreement: bool}, created_ts}
- Quality gates G1-G6 per Roc spec, including: kill "use last response" fallback; position-swap judging (keep only label-consistent across permutations); K-sample self-consistency where feasible
- Cross-model adjudication: 10-20% sample to Sonnet (via export-claude-project handoff) or Gemini; disagreement rate >15% → halt line, diagnose
- Hard quotas per domain — small-N high-curation beats volume (distillation lit is unambiguous)
- Teacher-agnostic wiring: critic slot takes any OpenAI-compat endpoint OR in-session mode → GLM-5.3 slots in at weights drop

### B5. Knowledge Crystallization Suite (Jem burns 1-5)
Specs per OX_ALPHA_FLEET_CONSULT_JEM_20260823.md §1. Key constraints:
- Every axiom ≤150 tokens, self-contained, no pronoun refs to dead context
- Failure taxonomy entries: {symptom, root_cause, detection_signal, prevention_rule, mandate_link}
- Invariants codex pairs each rule with its violation catastrophe + regression probe (feeds M21 contract tests post-cliff)

### B6. Pollen Bank (R-31 cross-pollination)
- data/knowledge/pollen_bank/: AFFINITY.yaml gate + atomic PL-*.yaml packets (~100 tokens: principle, anti_pattern, applies_to, contraindicated_for, falsified_by, token_cost) + INDEX.jsonl (FTS-ready)
- Flow: harvest window outputs NOW (frontier decomposition is the perishable step) → blind-stage to proposed_lessons.yaml tagged cross_pollinated → skeptical-verifier two-source rule before promotion → inject top-K ≤2K tokens at session start
- FORMAT + CONVENTION ONLY — no daemon, no queue (UO-6 compliant). Falsify with one manual harvest before mass adoption.

### B7. Soul Enrichment (bounded, per Scribe census)
- Targets ONLY Tier B thin entities: sophia (empty staging), node (empty), john_carmack (6L + case-dup dir to consolidate), sysadmin (48d stale)
- Five legitimacy conditions per Scribe §2: agent-authored evidence-grounded, blind staging, M22 provenance, per-entity domain fit, NO fabricated experience for never-run entities
- Dedup: FTS5 prefilter + embedding gate (≥0.85 merge, 0.70-0.85 flag); bloat caps 12/8/5 L3 per wave tier; utility floor 0.6; QA = 20% Verity audit, halt >15% fail
- ~19 Tier D stub dirs → separate discard ticket, NOT enrichment

### B8-B10. Mining / Repo Surgery / Harness Artifacts
- Mining: Master Synthesis §2 plan, fleet-parallel, feeds factory
- Repo surgery: UO-6 whole-repo items only; output = safe-to-delete manifest with dependency traces
- Harness artifacts: convert THIS strategy into .opencode/skills/ — council-dispatch skill (the Architect's 4-wave protocol), export-claude-project skill (state bundling for Claude.ai review). Skills survive every model cliff BY CONSTRUCTION.

---

## §4 TEAM GUIDE — Roles & Dispatch Protocol

### Assignments
| Agent | Phase 0 | Phase 1 | Notes |
|---|---|---|---|
| researcher | G3 script, G4 schema | Track A lead, Track C generation | Orchestrator; owns blueprint execution |
| roc_racoon | G1 smoke test | Self-corpus Wave 1, Track C design, Track D wave 2 | Joins after Team-Study-#1 clears |
| jem | Decision Axioms (0.4) | Track B suite (BURNS 2-5 + Codex) | Dedicated child sessions |
| scribe | — | B7 soul enrichment (after ratification forks clear) | Bounded census targets only |
| grokster | — | Adversarial QC sampling; teacher-agnostic wiring spec | Verification-capacity seat |
| maat/lilith | password fix (0.5) | Track D wave 2 | After Team-Study-#1 |
| carmack | — | Rolling audit of Track C output quality | Kill-switch authority |
| ARCHITECT (human) | Fork rulings (§7) | Claude.ai Project adjudication passes | The cross-model judge of record |

### Dispatch Protocol Rules (hardened this session)
1. **R-3**: Record session ID + artifact path at MISSION COMPLETION, never session end
2. **R-4a**: On free-tier 429 → page-don't-respawn (worked for N9)
3. **R-4b (Prompt Firewall)**: Relay to child sessions must be child-addressed prompts wrapped in <child_directive> tags — NEVER forward parent meta-instructions verbatim (the triple-page incident)
4. **M22 ICS discipline**: every major output carries the ICS header with TRUE model id — training-data provenance depends on it
5. **Grep-Gate**: no task flips to completed without mechanical disk verification (the providers.py:119 lesson — claimed fixed, still live)
6. **Registration-at-completion**: every dispatch lands in TASK_REGISTRY.json immediately (13-dispatch backfill was the warning)

---

## §5 KILL LIST (ratified across all model passes — do not resurrect without new evidence)
1. Background researcher loop (token incinerator; revive ONLY with hard output contract)
2. Vision archaeology (no free direct-API path; text-only harness)
3. Standalone Context Packer sprint in-window (dev-time work; merge into CONTEXT-INJECTION Phase 1 — BUT see §7 Fork 3: post-cliff it becomes an attention-compression survival mechanism, not a delivery mechanism)
4. Mass fleet-wide soul enrichment (bloat = negative durable artifact; bounded census targets only)
5. Standalone knowledge-gap-filling track (fold into mining)
6. Re-researching documented ground truth / weight-restorable work

## §6 SUCCESS METRICS (window close-out audit)
- [ ] G1 smoke test verdict recorded
- [ ] Golden Set ≥200 items, scored against local baseline
- [ ] Self-corpus ≥1M filtered tokens, ICS-attributed, PII-scrubbed
- [ ] DECISION_AXIOMS.yaml covers all load-bearing D-series decisions
- [ ] Failure taxonomy + invariants codex on disk
- [ ] ≥150 adjudicated DPO pairs (if G1 passed) with agreement rate ≥85%
- [ ] Pollen Bank seeded ≥50 packets + one manual harvest validation
- [ ] 4 thin souls enriched within bloat caps
- [ ] password="omega" gone from providers.py:119
- [ ] council-dispatch + export-claude-project skills committed

## §7 OPEN FORKS — ARCHITECT RULING REQUIRED
| # | Fork | Options | Recommendation |
|---|---|---|---|
| F1 | Post-cliff training owner | (a) Roc owns fine-tuning ops · (b) sysadmin entity chartered for it · (c) Architect runs manually per runbook | (a) Roc — already designed the factory |
| F2 | Cross-model adjudicator | (a) Sonnet via Claude.ai Project handoffs · (b) Gemini free tier · (c) skip adjudication (NOT recommended) | (a) — different model family = real signal; batched daily |
| F3 | Packer post-cliff role | (a) build attention-compressor variant post-cliff · (b) rely on Pollen Bank + RAG only | Decide AFTER first week on local models — evidence over speculation |
| F4 | Scribe ratifications | batch≠regex one-liner + soul-enrichment workspace lock | Grant both — conditions in B7 are sufficient guardrails |
| F5 | ho_2f77f83964e5 disposition | annotate superseded by this blueprint | Yes — closes the stale-premise handoff |

## §8 CONTINUITY POINTERS (one-read hydration)
1. This blueprint — data/coordination/OX_ALPHA_TRANSITION_BLUEPRINT_20260823.md
2. Fleet consults — data/entities/{jem,grokster,scribe,roc_racoon}/workspace/OX_ALPHA_*20260823*.md + CARMACK_WINDOW_RANKING_20260823.md (researcher workspace)
3. Session gnosis — data/entities/researcher/session_gnosis.md (incl. strategy correction addendum)
4. Standard-model codex — data/coordination/STANDARD_MODEL_OPERATING_GUIDE.md (Gemini pass)
5. Kali anchor — data/coordination/SESSION_ANCHOR.md
6. Meditation record — data/coordination/meditations/records/MEDITATION_oxalpha_20260822_OX_ALPHA_FULL_UTILIZATION.md

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ OX ALPHA TRANSITION BLUEPRINT v1.0 ⬡ CAPSTONE SYNTHESIS ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
