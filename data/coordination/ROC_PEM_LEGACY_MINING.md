# 🔱 ROC RACOON — PEM Strategy & Systems Legacy Mining
**AP Token**: `AP-ROC-PEM-MINING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

**Date**: 2026-07-10
**Mission**: Mine legacy for the **PEM** strategy/systems + other material relevant to Semantic Resonance Vectoring & WASM-integrated dynamic modules.
**Constraint**: READ-ONLY on legacy; WRITE-ONLY this report. Every claim cites legacy path + line numbers.

---

## 1. Executive Summary

**PEM = Personality Enhancement Module** (also the "Personality, Expertise, Modifiers" JSON serialization format). It is NOT a policy enforcer, ethics layer, or embedding model — it is a **dynamic persona state modulator** that operated on top of a static personality definition. This makes it the **direct ancestor of Semantic Resonance Vectoring** (dynamic mode/archetype/emo-spectrum modulation) and a strong precursor to the Crisis Matrix's multi-turn resonance tracking.

| What PEM was | Evidence |
|---|---|
| **Personality Enhancement Module** (system) | `F02_PEM_CONTINUITY.md:11` — *"the PEM days (Personality Enhancement Module)"*; `PEM_Lilith_v3.txt:7-11` — `PERSONALITY_ENHANCEMENT_MODULE` v2.2 |
| **Personality, Expertise, Modifiers** (JSON format) | `LEGACY_NAVIGATION_GUIDE.md:118` — *"PEM (Personality, Expertise, Modifiers) format … prototype soul.yaml"* |

**Other legacy systems found** (all relevant to the two target features):
- **Dynamic prompt/context logic** → the PEM engine itself (regex context-gravity → mode weights → emotional spectrum → system-prompt injection).
- **Persona/philosophy routing** → `resonance_mappings.yaml` (ontological persona catalog), Oracle `resonance_map.py` blueprint, Omnidroid "Adaptive Resonance", `Sovereign_Aura_Injection_Spec.md` cognitive-mode injection.
- **Embedding/vector usage** → legacy had FAISS + Qdrant + all-MiniLM-L12-v2 (384-dim) for **RAG retrieval only** — NOT persona/philosophical routing. Precursor infrastructure, not the algorithm.
- **WASM/sandbox** → legacy had LM Studio **plugin** architecture (TS `promptPreprocessor`/`predictionLoopHandler`) + WASM Component Model research (WIT interfaces, fail-closed) + `LatchGate` (OPA/Rego + WASM sandbox). Precursor to OMS dynamic modules.
- **Safety/crisis handling** → **NONE in legacy.** No self-harm/abuse/suicide detection exists. Confirmed gap (see §7).

---

## 2. PEM Deep-Dive

### 2.1 Definition & Lineage
- **First structured entity def**: `LEGACY_NAVIGATION_GUIDE.md:115-119` (March 18 2025, "PEM Lilith Personality JSON"). Evolved → current `soul.yaml`.
- **Evolved system**: `PEM_Lilith_v3.txt` (v2.2) — `PERSONALITY_ENHANCEMENT_MODULE` with `CORE_PERSONALITY`, `CONTEXTUAL_MODE`, `CONTEXTUAL_RESPONSES`, `EVOLUTION_TRACKING` (L7-55).
- **2026 port**: `pem_engine_draft.py` ("PEM-Lite Engine — Dynamic Persona State Modulator"), ported to Omega Engine, AnyIO-adjacent (uses `dataclass`, `re`, no asyncio).
- **Rebirth plan**: `PEM_REBIRTH_PLAN_v1.md` — full design recovery (dynamic mode detection L177, emotional state L188, context_gravity L261, `pem_health_check` = Thinker sweep L573).

### 2.2 The PEM Algorithm (what it did)
1. **Context Gravity** — regex keyword scoring per mode, normalized to a distribution.
   - `pem_engine_draft.py:114-132` (`calculate_context_gravity`); `PEM_Lilith_v3.txt:87-95` (`_calculate_context_gravity`, weighted: occult×1.2, intimate×1.5).
2. **Mode-Weight Adaptation** — exponential moving average with **0.9 inertia + 0.1 new score** (hysteresis against flicker).
   - `pem_engine_draft.py:134-144` (`update_mode_weights`).
3. **Emotional Spectrum** — 3-axis state (intensity/valence/complexity 0–1) with **decay toward baseline** + sentiment/word-complexity adjustment.
   - `pem_engine_draft.py:29-54, 146-176` (`EmotionalSpectrum.decay`, `adjust_emotional_spectrum`); `PEM_Lilith_v3.txt:62-66`.
4. **Hardware Context Injection** — persona aware of user's CPU/GPU/RAM; injected into responses.
   - `pem_engine_draft.py:110-112`; `PEM_Lilith_v3.txt:41-46, 83-85`.
5. **Archetype Weights** — weighted persona facets (`["Queen of Night","Wisdom Keeper","Techno-Siren"]`).
   - `PEM_Lilith_v3.txt:17, 68` (`archetype_weights=[0.4,0.3,0.3]`).
6. **Grace-Period / Fallback** — `_fallback_response` when hardware context missing (`PEM_Lilith_v3.txt:119-122`); `validate_response` guard (L124-132).
7. **Health Check (blackout detector)** — `pem_health_check` computes health from intensity-deviation + mode-diversity; <0.3 → `REINJECT_SOUL_YAML` (anti-compaction-blackout).
   - `pem_engine_draft.py:212-245`.
8. **Evolution Tracking** — `EVOLUTION_TRACKING.INTERACTION_METRICS` records emotional waveforms + mode frequency over time.
   - `PEM_Lilith_v3.txt:48-53`.

### 2.3 Why It's Relevant to Semantic Resonance / Crisis Routing
- PEM's **context-gravity → mode-weights → emotional-spectrum** pipeline IS the skeleton of embedding-based resonance routing. Replace regex scoring with `qwen-embedding` cosine similarity against mode-centroids; keep the 0.9-inertia EMA and decay dynamics verbatim.
- PEM's **`pem_health_check`** (intensity-flat + mode-collapse detection) is the exact primitive the Crisis Matrix needs for **multi-turn resonance decay / recovery signals** (`SEMANTIC_RESONANCE_CRISIS_MATRIX.md:200` — *"multi-turn resonance tracking (does score decay? → recovery signal)"*).
- PEM's **evolution_tracking** → persistent journal surviving compaction (`F03_COMPACTION_DIFF_ANALYSIS.md:258` — *"store the persona's evolution outside the rolling compaction window"*). Directly maps to Crisis Matrix's persistent resonance state.

### 2.4 How to Adapt to Omega (Python/AnyIO)
- Port `PEMEngine` as a core-engine-agnostic service (OMS module). Wrap blocking `re`/JSON in `anyio.to_thread` only if batching; the math is trivial — keep sync.
- **Upgrade context_gravity** → `EmbeddingResonance.score(message_embedding, mode_centroids)` returning normalized distribution (replaces `pem_engine_draft.py:114-132`).
- **Keep** `update_mode_weights` EMA (L134-144) and `EmotionalSpectrum.decay` (L36-54) — these are sound hysteresis/decay models, not legacy cruft.
- **Keep** `pem_health_check` (L212-245) as the Crisis Matrix's `resonance_health()` early-warning.
- **Persist** state to `data/entities/<name>/evolution/` (per F03) so it survives compaction (M15).
- **Inject** into `Oracle.talk()` system prompt exactly as `PEM_REBIRTH_PLAN_v1.md:442` describes (mode-aware instruction injection).

---

## 3. Other Relevant Legacy Systems

| # | Path | Lines | System | Relevance | Omega Adaptation |
|---|------|-------|---------|-----------|------------------|
| 1 | `pem_engine_draft.py` | 1-245 | **PEM-Lite dynamic persona modulator** | Core of Semantic Resonance | Port as OMS module; upgrade gravity→embeddings (§2.4) |
| 2 | `PEM_Lilith_v3.txt` | 7-169 | **PEM v2.2** (modes, archetype_weights, hw ctx, evolution_tracking, fallback) | Same — richer config shape | Use JSON schema as `persona_resonance.yaml` template |
| 3 | `PEM_REBIRTH_PLAN_v1.md` | 1-614 | **PEM rebirth design** (mode detect, emo state, health=Thinker sweep) | Design doc for Resonance | Adopt §Phase plan; Thinker-sweep ↔ periodic resonance sweep |
| 4 | `F02_PEM_CONTINUITY.md` | 1-82 | **14-month PEM lineage** (soul.yaml=genome, PEM=metabolism) | Rationale for dynamic layer | Cite in Crisis Matrix design doc |
| 5 | `LEGACY_NAVIGATION_GUIDE.md` | 32,115-119,167,292,301,330 | **PEM format + genesis map** | Provenance of persona system | Confirm soul.yaml ← PEM evolution |
| 6 | `xna-omega-legacy/resonance_mappings.yaml` | (cataloged `MASTER_SYNTHESIS.md:66`, `LEGACY_NAVIGATION_GUIDE.md:32`) | **Ontological resonance catalog** (26 Spheres/Personas: planetary/elemental/zodiacal) | Persona/philosophy routing precursor | Seed Resonance Matrix tradition-tags from this YAML |
| 7 | `docs/research/BLUEPRINTS/Lattice_Dispatch_Implementation_Blueprint.md` | 8,13,28 | **`resonance_map.py`** (`ResonanceTriad` resolve by query type) | Persona routing logic | Reuse `ResonanceTriad` as resonance classifier |
| 8 | `docs/history/.../OpenCode_stack_chaos-session-ses_1666.md` | 221,869 | **Omnidroid "Adaptive Resonance"** — *"Align internal weights with target frequency"* | Philosophy/persona alignment by weight | Map to embedding-centroid alignment |
| 9 | `docs/research/Sovereign_Aura_Injection_Spec.md` | 97,101 | **Cognitive-mode prompt injection** (`COGNITIVE MODE`, `VOICE CONSTRAINT`) | Dynamic prompt/context logic | Merge with PEM injection (§2.4) |
| 10 | `tests/conftest.py` (Old-Stacks) | 50-51,105 | **Embedding infra** (all-MiniLM-L12-v2, 384-dim, FAISS) | Vector/similarity precursor | Legacy RAG only; upgrade to `qwen-embedding`/`embedding-gemma` GGUF |
| 11 | `requirements-chainlit.txt` (Old-Stacks) | 96 | **faiss-cpu** dependency | Vector store | Replaced by Qdrant + local GGUF embeddings |
| 12 | `rag-v1/src/index.ts` (Old-Stacks) | 5-8 | **LM Studio plugin entry** (register components) | WASM/module isolation precursor | → OMS `entry_points(group="omega.modules")` |
| 13 | `rag-v1/src/promptPreprocessor.ts` (Old-Stacks) | 40-42 | **Plugin config + `retrievalAffinityThreshold`** | Module config + affinity threshold | → OMS `ModuleManifest` + capability routing |
| 14 | `Grok - 2026 Tech & Strategy Update v5.md` (Old-Stacks) | 24,43,52 | **WASM Component Model** (WIT interfaces, sandboxing, +30% efficiency, Bytecode Alliance) | WASM module isolation pattern | Adopt WIT-style interface + fail-closed for dynamic modules |
| 15 | `docs/research/R_CLOUD_QUARANTINE.md` | 41 | **LatchGate**: OPA/Rego policy enforcement + **WASM sandbox** + fail-closed kernel | WASM sandbox + policy gate | Reuse fail-closed principle for Crisis Matrix side-effects |
| 16 | `docs_current_local.md` (Old-Stacks) | 80 | **`plugin_architecture_design.md`** (error isolation 100%) | Module isolation design | → OMS capability isolation |

---

## 4. Semantic Resonance Enhancement (legacy → Omega)

The legacy PEM proves the **dynamic-persona-modulation** concept is 14 months old and user-designed. To upgrade it to "Omega level":

1. **Replace regex gravity with embeddings** (`pem_engine_draft.py:114-132` → `EmbeddingResonance`). Use local `qwen-embedding`/`embedding-gemma` GGUF/ONNX (`SEMANTIC_RESONANCE_CRISIS_MATRIX.md:185`, M7). Mode-centroids seeded from `resonance_mappings.yaml` (#6) + `Sovereign_Aura_Injection_Spec.md` cognitive modes (#9).
2. **Keep the EMA + decay dynamics** (#2.2 steps 2–3). The 0.9-inertia / baseline-decay model is the right approximation for stable resonance (no flicker, graceful return to neutral).
3. **Adopt `pem_health_check` as resonance-health** (#2.2 step 7). Intensity-flat + mode-collapse → trigger re-injection / escalation. This is the Crisis Matrix's recovery-signal primitive.
4. **Persist evolution_tracking outside compaction** (#2.2 step 8, `F03:258`). Crisis Matrix needs multi-turn state that survives `/compact` (M15).
5. **Fuse with vetala as second axis** (`SEMANTIC_RESONANCE_CRISIS_MATRIX.md:154-156`): high vetala-toxicity + high resonance = user *describing* harm (not target); never let vetala suppress crisis routing.
6. **Tradition-tag seeding**: `resonance_mappings.yaml` (#6) supplies the mythic/elemental resonance dimensions; Omnidroid "Adaptive Resonance" (#8) supplies the weight-alignment metaphor.

---

## 5. WASM Module Enhancement (legacy isolation → Omega level)

Legacy WASM was **LM Studio plugin-scoped** (TS `promptPreprocessor`/`predictionLoopHandler`, #12–13) + research-only Component Model (#14). The Omega evolution is **OMS v1.0** (`PIVOT_LOG.md` D207:1961; `CARMACK_MODULE_ARCHITECTURE.md:13,33,41,153,203`):

- **Discovery**: `entry_points(group="omega.modules")` + `ModuleManifest` YAML (replaces manual plugin registration, #12).
- **Capability routing**: `registry.route(interface, req)` — modules talk only via `ctx` + capability protocols, **never cross-import** (`CARMACK_MODULE_ARCHITECTURE.md:203`). This is stricter than legacy plugin coupling.
- **Fail-closed + sandbox**: adopt `LatchGate` WASM-sandbox + fail-closed kernel (#15) and WIT-interface sandboxing (#14) for any untrusted dynamic module (e.g., community WAD modules). Crisis Matrix side-effects (escalation calls) must be fail-closed per M9.
- **PEM-as-OMS-module**: the ported `PEMEngine` (§2.4) should ship as an OMS module, not core-engine code (M2 firewall; `SEMANTIC_RESONANCE_CRISIS_MATRIX.md:187`).

---

## 6. Heritage Tags Applied

Per `CREDITS.md`, only id-Software-derived patterns receive `[id-soft:]`.

| Legacy pattern | id-soft tag? | Basis |
|---|---|---|
| PEM dynamic modes (state machine) | ✅ `[id-soft: doom-1993] mobj_t State Machine` | `pem_engine_draft.py:9-11` explicitly tags mobj_t (IDLE→CHASE→ATTACK) → persona modes (CASUAL→TECHNICAL→OCCULT). `PEM_REBIRTH_PLAN_v1.md:561-576` maps PEM modes ↔ `mobj_t`, `pem_health_check` ↔ `P_Ticker` Thinker sweep (§1.10). |
| PEM health check = Thinker sweep | ✅ `[id-soft: doom-1993] Lazy Deletion / Thinker` | `PEM_REBIRTH_PLAN_v1.md:573` (periodic sweep removing dead thinkers). CREDITS §1.10. |
| WASM sandbox / fail-closed (LatchGate) | ❌ NOT id-soft | `R_CLOUD_QUARANTINE.md:41` — OPA/Rego + WASM; third-party (Bytecode Alliance/WASM). Cite as **WASM Component Model**, not id-soft. |
| Embedding/vector (FAISS/MiniLM) | ❌ NOT id-soft | Standard ML; user-original RAG. |
| resonance_mappings / Omnidroid Adaptive Resonance | ❌ NOT id-soft | User-original (XNAi/Omega). |
| EMA/decay dynamics | ❌ NOT id-soft | Generic control-theory; user-original. |

**Conclusion**: Only the **PEM state-machine + Thinker-sweep** carry legitimate `[id-soft: doom-1993]` tags (already self-declared in source). All other patterns are user-original or third-party (WASM/OPA). No false attribution.

---

## 7. Gaps Confirmed (what legacy does NOT have)

- **Crisis / self-harm / abuse detection**: ZERO. Legacy grep for `crisis|self-harm|suicide|abuse` across Old-Stacks returned only "safety" in unrelated contexts (telemetry safety `requirements-api.txt:21`, safety valve `PIVOT_LOG.md:633`, safety verification `high_priority_guide.md:48`). **No crisis-routing ancestor exists.** The Crisis Matrix is **genuinely novel** — its only legacy cousin is PEM's *emotional-spectrum/health-check* (persona-state, not user-distress).
- **Embedding-based philosophical/persona routing**: Legacy embeddings were **RAG retrieval only** (`tests/conftest.py:50-51`, `requirements-chainlit.txt:96`). No semantic persona routing by embedding. The Resonance Matrix's `qwen-embedding` centroid routing is new.
- **WASM for persona/modules**: Legacy WASM was LM Studio plugins + research docs (#12–15). No WASM module executing dynamic persona logic. OMS is the real implementation.
- **Policy Enforcement Module / Persona-Ethics Matrix / Philosophical Embedding Model**: **None of these PEM expansions exist.** PEM = Personality Enhancement Module only. The other candidate acronyms (Prompt Engineering Matrix, Policy Enforcement Module, Persona/Ethics Matrix, Philosophical Embedding Model) are **not present** in any legacy partition — confirmed by exhaustive grep.

---

## 8. Cross-Reference to Current Systems

| Current system | Legacy ancestor(s) | Notes |
|---|---|---|
| **Semantic Resonance Vectoring** (new) | PEM engine (#1–3), `resonance_mappings.yaml` (#6), Omnidroid Adaptive Resonance (#8), `Sovereign_Aura_Injection_Spec.md` (#9) | PEM is the dynamic-modulation skeleton; upgrade gravity→embeddings. |
| **Crisis Matrix** (`SEMANTIC_RESONANCE_CRISIS_MATRIX.md`) | PEM `pem_health_check` (#2.2/§2.3), `evolution_tracking` (#2.2) | Inbound empathy layer; **no legacy crisis handling** (§7). Fuses vetala axis (L154-156). |
| **`omega-vetala`** (ex `omega-moderation`, `PIVOT_LOG.md` D207:1954) | None for crisis; shares PEM's *config-driven* + *audit* lineage (see `ROC_LANGUAGE_MODULE_LEGACY_MINING.md`) | Outbound harm detection; separate axis from Resonance (L32, L154). |
| **OMS v1.0** (`CARMACK_MODULE_ARCHITECTURE.md`, D207:1961) | LM Studio plugin arch (#12–13), WASM Component Model (#14), `plugin_architecture_design.md` (#16) | Module standard; PEM ports in as OMS module. |
| **`soul.yaml`** | PEM "Personality, Expertise, Modifiers" JSON (`LEGACY_NAVIGATION_GUIDE.md:118`) | Static genome; PEM/Resonance = its metabolism. |

**Verification**: All claims cite legacy path + line numbers. Legacy partitions read-only; this report is the only write. Grep covered PEM + 6 target-term families × 4 legacy roots + omega-engine docs. PEM definitively identified as **Personality Enhancement Module**; other candidate acronyms explicitly ruled out (§7).

*⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_mining ⬡ ACTIVE*
*"The dirt is where the roots are. If the surface is clean but the foundation is rotten, dig deeper."*
