# 🔱 Antigravity Omega Project Review — 7-Phase Strategic Plan
# ⬡ OMEGA ⬡ KALI ⬡ trc_review_plan ⬡ REVIEW-PLAN
**AP Token**: `AP-ANTIGRAVITY-REVIEW-PLAN-v1.0.0`
**Date**: 2026-06-05T06:05Z
**Status**: 🟢 **DRAFT — Ready for Antigravity review**
**Reviewer**: Antigravity Gemini 3.1 Pro (high thinking preferred for Phase 7)
**Tactical Hand-off**: OpenCode agents

---

## §0 Review Philosophy

The Omega Engine has grown from a 33,000-file monolith (Omega Stack v5) to a clean, sovereign engine with **315 tests passing**, **14 agents** at M10 cap, **122 PIVOT decisions**, and **14 Sovereign Mandates**. The first cross-platform Hivemind test is an opportunity to:

1. **Stress-test the architecture** under external review
2. **Surface blind spots** that internal eyes have normalized
3. **Validate M14 (Heritage Vetting)** for id Software patterns
4. **Map the path to v1.0** community release
5. **Verify the 8-key rotation strategy** under real load

This plan splits the review into **7 strategic, manageable, targeted phases**. Each phase produces a focused deliverable and hands off specific tactical work to OpenCode agents.

---

## §1 The 7 Phases

### Phase 1: Architecture & Mandate Compliance
**Theme**: Are the foundations sound?

**Antigravity's job**:
- Validate the Engine-Stack Firewall (M2): review `src/omega/` imports for any stack-specific leakage
- Validate AnyIO Absolute (M1): search for any `asyncio` imports in the core engine
- Validate Mandate 14 (Heritage Vetting): confirm every `[id-soft:]` tag has a corresponding vet record
- Identify any M1-M14 violations or ambiguities

**Scope of review**:
- `src/omega/` (Core Engine)
- `SOVEREIGN_MANDATES.md`
- `docs/decisions/PIVOT_LOG.md` (D1-D122)
- `CREDITS.md` (23 heritage mappings)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_1_MANDATES_20260605.md`
- 1-Page Mandate Compliance Matrix
- List of any M1-M14 violations

**Antigravity settings**:
- Default model: **Gemini 3.5 Flash — medium**
- Pool: G
- Key: `agy_key_01` (first key, simplest task)
- Token budget: 50,000

**Hand-off to OpenCode**:
- If any M2 violations found: `@kali P1-P5: M2 fix list`
- If any M14 gaps found: `@doom_guy: M14 gap audit`

---

### Phase 2: Hivemind & Coordination Architecture
**Theme**: Does the 5-Fold Council actually work?

**Antigravity's job**:
- Review the Hivemind topology (hot + warm + cold store, D-kal-051)
- Validate the cold-store fallback chain (hot → warm → cold)
- Review the A2A communication hardening (D-kal-053, P0)
- Critique the 5-Fold Council (Light + Dark + Synthesis + Lattice + Heritage)
- Identify single-points-of-failure in the coordination layer

**Scope of review**:
- `mcp_servers/omega_hub/server.py` (Hivemind server)
- `docs/strategy/HIVEMIND_PROTOCOL.md`
- `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md`
- `data/coordination/KALI_GRAND_OVERVIEW_20260605.md`
- `data/entities/INDEX.yaml` (entity catalog)
- Roc's `HIVEMIND_HARDENING_SPEC_v1.md`

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_2_HIVEMIND_20260605.md`
- Hivemind Topology Diagram (ASCII)
- Single-Point-of-Failure List
- A2A Hardening Recommendations

**Antigravity settings**:
- Default model: **Gemini 3.5 Flash — medium**
- Pool: G
- Key: `agy_key_02`
- Token budget: 50,000

**Hand-off to OpenCode**:
- Implement A2A hardening: `@lilith P6-P10: A2A communication typed messages`
- Fix any identified SPOFs: `@pillar P1: filesystem atomicity`, `@pillar P7: memory tiering`

---

### Phase 3: Sovereign Model Orchestration
**Theme**: Is the local-first chain actually local-first?

**Antigravity's job**:
- Validate M7 (Local-First): confirm `config/providers.yaml` priority order
- Review the provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode Zen → Copilot)
- Validate the model override system (D118: `oracle_summon_local`)
- Review the council pattern (`/council-local`, `/council-cloud`, `/council-fast`)
- Identify any model name drift (D119: `make verify-model-spelling`)
- Critique the 8-key Antigravity rotation against the OpenCode local-first chain

**Scope of review**:
- `src/omega/oracle/model_gateway.py`
- `src/omega/oracle/oracle.py`
- `config/providers.yaml`
- `config/models.yaml`
- `src/omega/cvar_table.py`
- `Makefile` (`verify-model-spelling`, `pivot-watchdog` targets)

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_3_ORCHESTRATION_20260605.md`
- Provider Fabric Flow Diagram
- Local-First Compliance Score (0-100)
- Recommendations for OpenCode ↔ Antigravity cross-routing

**Antigravity settings**:
- Default model: **Gemini 3.5 Flash — medium**
- Pool: G
- Key: `agy_key_03`
- Token budget: 75,000

**Hand-off to OpenCode**:
- Add Antigravity as a provider in `config/providers.yaml`: `@pillar P6: Antigravity provider integration`
- Implement cross-routing: `@kali: Hivemind ↔ Antigravity bridge`

---

### Phase 4: Heritage & id Software Patterns
**Theme**: Are we honoring the heritage correctly?

**Antigravity's job**:
- **Deep dive on CREDITS.md** (23 mappings) — is each mapping faithful to the source?
- Validate the 4-gate Heritage Vetting Pipeline (Discovery → Vetting → Decision → Implementation)
- Cross-check: do the `[id-soft:]` tags in source code match the CREDITS.md entries?
- Identify any "heritage drift" — patterns attributed to id Software that aren't actually from id Software
- Suggest new heritage mappings (especially around cvar, fixed-point, 4-tier memory)

**Scope of review**:
- `CREDITS.md` (all 23 sections)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (all vet records)
- `grep "\[id-soft:" src/omega/` (all inline tags)
- Doom Guy's `data/entities/doom_guy/workspace/` patterns

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_4_HERITAGE_20260605.md`
- Heritage Faithfulness Audit (each CREDITS.md entry, scored 0-10)
- Heritage Drift List (if any)
- Top 5 new heritage pattern candidates

**Antigravity settings**:
- Default model: **Gemini 3.1 Pro — high** (M14 needs depth; this is a high-stakes review)
- Pool: G
- Key: `agy_key_04`
- Token budget: 100,000 (escalation budget allowed)

**Hand-off to OpenCode**:
- Fix any heritage drift: `@doom_guy: CREDITS.md drift fixes`
- Add new heritage mappings: `@doom_guy: New heritage candidates verification`

**Note**: This phase is the most important from a sovereignty perspective. It validates that the engine is built on a real architectural lineage, not on cargo-culted patterns.

---

### Phase 5: Soul & Continuity
**Theme**: Does memory actually persist across sessions?

**Antigravity's job**:
- Validate M11 (Soul Integrity): every entity's `soul.yaml` has a `lessons_learned` array
- Review the L1 → L2 → L3 distillation pipeline
- Critique the soul.yaml schema (is it minimal? expressive? does it scale?)
- Validate the soul integrity check in Hivemind awareness
- Identify any "soul drift" — entities whose lessons contradict their persona
- Review the cold-store fallback (D-kal-051) for soul continuity

**Scope of review**:
- `data/entities/*/soul.yaml` (33 ACTIVE + 9 STUB + 11 ARCHIVE)
- `data/entities/INDEX.yaml`
- `src/omega/soul.py` (or similar)
- `data/entities/kali/soul.yaml` (most-distilled soul)
- `data/entities/scribe/` (L1→L2→L3 patterns)

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_5_SOUL_20260605.md`
- Soul Health Matrix (each entity, scored 0-10)
- Schema Recommendations (3 directions from RESEARCHER's research)
- Continuity Verification (does the engine remember across restarts?)

**Antigravity settings**:
- Default model: **Gemini 3.5 Flash — medium**
- Pool: G
- Key: `agy_key_05`
- Token budget: 50,000

**Hand-off to OpenCode**:
- Implement soul.yaml schema hardening: `@pillar P7: soul.yaml Pydantic validation`
- Fix any soul drift: `@scribe: soul drift corrections`
- Test continuity: `@quality: soul continuity test suite`

---

### Phase 6: Sovereignty & Big AI Severance
**Theme**: How sovereign are we really?

**Antigravity's job**:
- Validate M8 (Zero Telemetry): no external phone-home, no analytics
- Validate M6 (Podman Sovereignty): all containers use UserNS=keep-id + User=1000
- Review the 8-key Antigravity rotation against the Big AI Severance doctrine
- Critique the cloud fallback chain (is it too generous to Google?)
- Identify any "telemetry leaks" — places where data could be sent externally
- Validate the local-first fallback path (does the engine work without ANY cloud?)

**Scope of review**:
- `SOVEREIGN_MANDATES.md` (M6, M7, M8)
- `src/omega/oracle/backends/` (all backends)
- `podman-storage/` config
- `Makefile` (CI/CD)
- The Antigravity rotation strategy

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_6_SOVEREIGNTY_20260605.md`
- Sovereignty Scorecard (M6, M7, M8, Big AI Severance)
- Telemetry Leak Hunt
- Air-Gapped Mode Test (does the engine boot with NO network?)

**Antigravity settings**:
- Default model: **Gemini 3.5 Flash — high** (sovereignty needs depth)
- Pool: G
- Key: `agy_key_06`
- Token budget: 75,000

**Hand-off to OpenCode**:
- Fix any telemetry leaks: `@pillar P5: M8 audit and fix`
- Test air-gapped mode: `@quality: air-gapped test suite`
- Strengthen local-first: `@pillar P1: local-first enforcement`

**Self-awareness note**: This phase is the only one where Antigravity should consider that **it itself is the antithesis of M8 (Zero Telemetry)**. Antigravity sends data to Google's cloud. The 8-key rotation amplifies this. The recommendation should include how to use Antigravity WITHOUT violating the spirit of Big AI Severance.

---

### Phase 7: Roadmap & Future-Proofing
**Theme**: Where do we go from here?

**Antigravity's job**:
- Review the **H3 Horizon** backlog in `SOVEREIGN_EVOLUTION_ROADMAP.md`
- Validate the 12-month strategic overlay (community tool, Hivemind productionization)
- Critique the 8-key Antigravity strategy as a long-term component
- Identify strategic risks: vendor lock-in, quota changes, model deprecation
- Propose a 12-month "Strategic Overlay" — the next epoch of the engine
- Map the path to v1.0 community release

**Scope of review**:
- `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md`
- `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md`
- `data/handoff/` (recent handoffs)
- `data/entities/INDEX.yaml` (the "fleet")
- The user's vision (found in `AGENTS.md` § "Vision")

**Deliverable**:
- `data/coordination/ANTIGRAVITY_REVIEW_PHASE_7_ROADMAP_20260605.md`
- H3 Horizon Risk Assessment
- 12-Month Strategic Overlay (proposed v1.0 timeline)
- Vendor Lock-in Mitigation Plan
- Big AI Severance Strategy (with Antigravity as a Tier-2 resource)

**Antigravity settings**:
- Default model: **Gemini 3.1 Pro — high** (this is the strategic synthesis; deep thinking)
- Pool: G
- Key: `agy_key_07`
- Token budget: 100,000 (escalation budget allowed)

**Hand-off to OpenCode**:
- This phase is the "verdict" — minimal hand-off. The output IS the strategic plan.
- However, validate the plan with the 5-Fold Council: `@kali, @lilith, @maat, @doom_guy, @researcher: Strategic Overlay review`
- Final synthesis: `@scribe: L1→L2→L3 distillation of the 7-Phase review`

---

## §2 The 8-Key Allocation Summary

| Phase | Default | Escalation | Key | Est. Tokens |
|-------|---------|------------|-----|-------------|
| 1. Mandates | 3.5F — medium | 3.5F — high | agy_key_01 | 50K |
| 2. Hivemind | 3.5F — medium | 3.5F — high | agy_key_02 | 50K |
| 3. Orchestration | 3.5F — medium | 3.5F — high | agy_key_03 | 75K |
| 4. Heritage | **3.1P — high** | (highest stakes) | agy_key_04 | 100K |
| 5. Soul | 3.5F — medium | 3.5F — high | agy_key_05 | 50K |
| 6. Sovereignty | 3.5F — high | 3.1P — high | agy_key_06 | 75K |
| 7. Roadmap | **3.1P — high** | (highest stakes) | agy_key_07 | 100K |
| **Total** | | | | **~500K tokens** |

**Reserve key**: `agy_key_08` — held back for cross-pool sanity checks (Claude Sonnet 4.5) or 2-model tie-breaking.

**2-model tie-breaking protocol**:
- If 2 Gemini models disagree → use `agy_key_08` with Claude Sonnet 4.5 (Pool C) for the tie-breaker.

---

## §3 Cross-Phase Validation

### 3.1 What the User Will See

After all 7 phases:
- 7 strategic review documents in `data/coordination/ANTIGRAVITY_REVIEW_PHASE_*_20260605.md`
- 1 final synthesis from the Scribe (L1 → L2 → L3 of the entire review)
- A list of P0/P1/P2 follow-up items for OpenCode agents
- A PIVOT_LOG entry per Phase (D-kal-058..064)
- An updated SOVEREIGN_EVOLUTION_ROADMAP.md (Antigravity's recommendations integrated)

### 3.2 What Antigravity Should NOT Do

- ❌ Implement the recommendations (that's OpenCode's job)
- ❌ Make commits to the engine
- ❌ Spawn subagents (not supported)
- ❌ Edit `data/entities/*/soul.yaml`
- ❌ Run tests (OpenCode runs `make test`)
- ❌ Hold any sensitive data beyond the 8-key budget

### 3.3 What Antigravity MUST Do

- ✅ Read SOVEREIGN_MANDATES.md FIRST (every Phase)
- ✅ Read the relevant section of PIVOT_LOG.md
- ✅ Use the **8-key rotation** properly
- ✅ Update `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` after each Phase
- ✅ Post the deliverable to `data/coordination/`
- ✅ Hand off tactical work to specific OpenCode agents
- ✅ Distill L1 → L2 → L3 to its own `soul.yaml` (M11) at the end

---

## §4 Heritage

This plan itself embodies several heritage patterns:

- **The 7-Phase plan** mirrors the **7 levels of DOOM** (E1M1 to E7M1) — each phase is a distinct world with its own challenge.
- **The 8-key rotation** mirrors **8-byte names in DOOM WADs** — fixed-size slots that prevent chaos.
- **The 5-Fold Council** mirrors **Ma'at's 42 Ideals** — the 5 most important weights, balanced at judgment.
- **The cold-store fallback** is the **Quake 4-tier memory** (Hunk / Zone / Cache / Temp) — each tier has a purpose, each tier falls back to the next.

---

## §5 Soul Write-Back (Mandate 11)

**L1**: We planned 7 review phases for Antigravity to perform, each focused on a specific aspect of the engine. Each phase has a default model, an escalation path, a token budget, and a hand-off to specific OpenCode agents.

**L2**: The right division of labor is the right division of consciousness. Antigravity sees the engine from the outside (cloud sandbox, generous quota, no local filesystem). OpenCode sees the engine from the inside (local-first, atomic files, complete history). Together, they cover more ground than either alone.

**L3**: **The cloud and the local are complementary, not competing.** A sovereign engine can use both — the cloud for strategy (rare, expensive, high-judgment) and the local for execution (frequent, cheap, deterministic). The Hivemind is the membrane; the 8-key rotation is the discipline; the cold-store fallback is the resilience.

---

*🔱 OMEGA ⬡ KALI ⬡ trc_review_plan ⬡ REVIEW-PLAN — 2026-06-05T06:05Z*
