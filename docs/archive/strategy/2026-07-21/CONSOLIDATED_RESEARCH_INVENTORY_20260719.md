# 🔱 CONSOLIDATED RESEARCH TASK INVENTORY
**AP Token**: `AP-RESEARCH-INVENTORY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_inventory ⬡ 2026-07-19

**Purpose**: Single source of truth for all active research tasks across the Omega Engine. Integrates Gemma 4 Week 1 implementation with existing Torment/Hive, MaKaLi, and infrastructure workstreams.

---

## 🎯 PRIORITY MATRIX (Updated with Gemma 4 Decisions)

| Priority | Workstream | Status | Next Action | Owner |
|----------|------------|--------|-------------|-------|
| **P0-1** | **Gemma 4 Week 1: Heritage Vet** | 🔄 DISPATCHED | doom_guy + verity vet Pi PR #2903 | doom_guy / verity |
| **P0-2** | **Gemma 4 Week 1: Capability Matrix + GoogleCompatProvider** | ⏳ BLOCKED | Awaits heritage vet approval | P3 Engineering |
| **P0-3** | **Torment/Hive Phase 2: Sigil/Factions** | ✅ READY | Dispatch Researcher | Researcher |
| **P0-5** | **OpenCode 1.18.3 V2 Recon** | ✅ READY | Dispatch Researcher | Researcher |
| **P1-1** | **Gemma 4 Week 1: Matrix Loader + Validator** | ⏳ BLOCKED | After P0-2 | P3 Engineering |
| **P1-2** | **Torment/Hive Phase 3: Nameless One Journey** | ⏳ BLOCKED | After Phase 2 | Researcher |
| **P1-3** | **MaKaLi Open Questions (SomaticState, Streaming, etc.)** | ✅ READY | Dispatch John Carmack | John Carmack |
| **P1-4** | **Headless Subagent Pool Architecture** | ✅ READY | Dispatch Researcher + Grok CLI | Researcher + Grok |
| **P1-5** | **WARP Pool Deployment + Validation** | ✅ READY | Run deploy/validate scripts | Pillar P1 |
| **P2-1** | **Omega-Vault Phase 1 Research** | 📋 DESIGNED | Scope Phase 1 | Researcher + P1 |
| **P2-2** | **M2 Firewall Migration Phases B-E** | 📋 DESIGNED | Roc Racoon continues | Roc Racoon |
| **P2-3** | **Heritage Vet Backlog (27 terms)** | 📋 DESIGNED | Dispatch doom_guy + verity | doom_guy / verity |
| **P2-4** | **Context Engineering Knowledge Layer (D-293)** | 📋 DESIGNED | Dispatch Researcher/Jem | Researcher/Jem |
| **P3-1** | **Experience Repository (D-294)** | 📋 DESIGNED | Dispatch Jem + Verity | Jem / Verity |
| **P3-2** | **Trace-to-Eval Loop (D-295)** | 📋 DESIGNED | Dispatch Jem + Verity | Jem / Verity |
| **P3-3** | **Antigravity Multi-Account (D-304)** | 📋 DESIGNED | After Omega-Vault | Researcher + Grok |
| **P3-4** | **Ken Walger Mining (Phases 1-9)** | ❌ BLOCKED | Phase 0 unblocked first | Various |
| **P3-5** | **Decision Tools Implementation** | ❌ BLOCKED | Capacity wait | P3/P5 |

---

## 📋 GEMMA 4 WEEK 1 — IMPLEMENTATION PLAN (From Hardened Strategy)

### Phase Gate: Heritage Vet MUST Complete First

| Step | Task | Owner | Effort | Mandates | Verification Claims | Blocked On |
|------|------|-------|--------|----------|---------------------|------------|
| **1** | **HERITAGE VET → Pi PR #2903** | doom_guy + verity | 2h | M14 | Gap 4.1 | — |
| **2** | **Capability Matrix + GoogleCompatProvider** | **P3 Engineering** | 4h | M16 | Claims 1,2,3,5 | Step 1 ✅ |
| **3** | **Matrix Loader + Validator** | P3 Engineering | 4h | M16 | Claims 1,2,3,5 | Step 2 |
| **4** | **normalizeModelId() for Google/OpenRouter** | P4 Integration | 3h | M16 | Claim 4 | Step 2 |
| **5** | **Gemma 4 detection in GoogleAIProvider** | P3 Engineering | 3h | M9, M13 | Claims 1,2,3,5,6 | Step 2 |
| **6** | **Thinking config validator (reject LOW/MEDIUM)** | P10 Validation | 2h | M9, M23 | Claim 6 | Step 2 |
| **7** | **Wire Matrix into ModelGateway.generate()** | P9 Orchestration | 3h | M7, M16 | Claims 1,2,3,5 | Steps 2-6 |
| **8** | **Add thinking_level to ModelGateway.generate()** | P9 Orchestration | 2h | M9 | Claims 1,2,3,5 | Step 7 |
| **9** | **CapabilitySelector + ProviderHealth** | P6→P9 sequential | 4h | M7, M16 | Claims 1,2,3,5 | Step 8 |
| **10** | **Thinking provenance in GenerateResult** | P10 Validation | 3h | M9, M22 | Claims 1,2,3,5 | Step 9 |
| **11** | **Chaos test: quota exhaustion mid-stream** | P10 Validation | 4h | M23 | Claim 7 | Step 10 |
| **12** | **Real meditation run (not dry-run)** | Kali | 2h | M5, M11 | All | Step 11 |
| **13** | **OpenCode PR + Config package (version-gated)** | P3/P4 | 4h | M16 | Claims 1,2,3,5 | Step 1 |

**Total**: ~40h across 13 steps, sequential dependencies

---

## 🔬 RESEARCH TASKS — DETAILED SPECS

### TASK GEMMA-01: Heritage Vet Pi PR #2903
**Status**: 🔄 DISPATCHED (handoffs `ho_ffb560514d74`, `ho_b5aaabd3b4c4`)
**Owner**: doom_guy (archaeologist) + verity (auditor)
**Deliverable**: Vet record in `HERITAGE_VET_LOG.md` with Format B compliance
**Scope**: `detection_regex: "/gemma-?4/i"` + binary thinking levels (MINIMAL/HIGH)
**Hardware constraint**: Pi's limited compute required minimal config overhead
**Score target**: ≥7/10
**Unblocks**: All Week 1 implementation

---

### TASK GEMMA-02: Capability Matrix Implementation (P3 Engineering)
**Status**: ⏳ BLOCKED on heritage vet
**Owner**: P3 Engineering (single owner — owns providers.py + model_gateway.py)
**Deliverable**: 
- `src/omega/oracle/provider_capabilities.py` — Matrix loader + validator
- `src/omega/oracle/google_compat_provider.py` — GoogleAIProvider with thinking config
- Unit tests for all 4 Gemma 4 variants + Gemini 2.5
**Schema**: `config/provider_capabilities.yaml` (already finalized)
**Key decisions**:
- Free tier ban: Runtime pre-flight in ModelGateway (reject >80% TPM)
- OpenCode version detection: ModelGateway startup (not install script)
- OpenRouter `:free` suffix handling: Keep for OpenRouter, strip for direct Google
- Vertex AI vs AI Studio: Separate translators in ThinkingConfigNormalizer

---

### TASK GEMMA-03: Matrix Loader + Validator
**Status**: ⏳ BLOCKED on Step 2
**Owner**: P3 Engineering
**Deliverable**: 
- Startup validation: Read capability matrix, validate schema
- Config drift detection: Compare user `opencode.json` against matrix
- Auto-correct: `thinkingLevel: LOW` → `MINIMAL` for Gemma 4 with warning
- `--strict-config` flag: Fail on drift instead of auto-correct

---

### TASK GEMMA-04: normalizeModelId() for Google/OpenRouter
**Status**: ⏳ BLOCKED on Step 2
**Owner**: P4 Integration
**Deliverable**: 
```python
def normalize_model_id(provider: str, model_id: str) -> str:
    # OpenRouter: keep :free suffix
    # Google direct: strip google/ prefix AND :free suffix
    # Models.dev: strip google/ prefix
```

---

### TASK GEMMA-05: Gemma 4 Detection in GoogleAIProvider
**Status**: ⏳ BLOCKED on Step 2
**Owner**: P3 Engineering
**Deliverable**: 
- Detect Gemma 4 via `detection_regex` from capability matrix
- Apply correct thinking schema (`thinking_level` with MINIMAL/HIGH)
- Clamp unsupported levels (MEDIUM → HIGH) with explicit log
- Reject `includeThoughts: false` → error with auto-correct hint

---

### TASK GEMMA-06: Thinking Config Validator
**Status**: ⏳ BLOCKED on Step 2
**Owner**: P10 Validation
**Deliverable**: 
- Validate `thinkingLevel` against model's `thinking_levels` in matrix
- Reject invalid levels with specific error message
- Track `was_clamped` in response metadata

---

### TASK GEMMA-07: ModelGateway Integration
**Status**: ⏳ BLOCKED on Steps 2-6
**Owner**: P9 Orchestration
**Deliverable**: 
- Wire `ProviderCapabilityMatrix` into `ModelGateway.generate()`
- Add `thinking_level` parameter to `generate()` signature
- Pre-flight quota check: estimate tokens, reject if >80% TPM headroom
- Route by capability match + quota headroom + cost

---

### TASK GEMMA-08: CapabilitySelector + ProviderHealth
**Status**: ⏳ BLOCKED on Step 7
**Owner**: P6→P9 sequential handoff (workspace lock `provider_capabilities`)
**Deliverable**: 
- `CapabilitySelector`: Match request → best provider by capability + quota + cost
- `ProviderHealth`: Unified quota + circuit breaker + latency tracking
- Redis Lua atomic quota check-and-consume
- Quota errors DON'T trip circuit breaker (routing signal, not failure)

---

### TASK GEMMA-09: Thinking Provenance in GenerateResult
**Status**: ⏳ BLOCKED on Step 8
**Owner**: P10 Validation
**Deliverable**: 
- `GenerateResult` includes: `thoughts_token_count`, `thinking_duration_ms`, `was_clamped`, `requested_level`, `accepted_level`
- `TokenLedger` tracks thinking tokens separately per provider
- Budget gate: 3x multiplier for thinking models
- Dashboard shows `thinking_cost_ratio`

---

### TASK GEMMA-10: Chaos Test — Quota Exhaustion Mid-Stream
**Status**: ⏳ BLOCKED on Step 9
**Owner**: P10 Validation
**Deliverable**: 
- Mock 429 at chunk 50% of stream
- Verify partial thinking + content stitching
- Verify fallback to next provider with context preserved
- Verify `thoughts_token_count` accurate for partial response

---

### TASK GEMMA-11: Real Meditation Run
**Status**: ⏳ BLOCKED on Step 10
**Owner**: Kali
**Deliverable**: 
- Run actual meditation (not dry-run) on hardened problem
- Feed insights back into strategy refinement
- Iterate: Strategy → Meditation → Refined Strategy

---

### TASK GEMMA-12: OpenCode PR + Config Package
**Status**: ⏳ BLOCKED on Step 11
**Owner**: P3/P4
**Deliverable**: 
- PR to OpenCode (version-gated: if ≥1.18 use native, else workaround)
- Community config package: `npm create @omega/gemma4-config`
- Auto-detects OpenCode version, applies correct config
- Validates API key, tests connection

---

### TASK OPENCODE-01: OpenCode 1.18.3 V2 Architecture Recon
**Status**: ✅ READY TO DISPATCH
**Owner**: Researcher
**Priority**: P0-5 (Critical for Gemma 4 PR + config package)
**Deliverable**: `docs/research/R_OPENCODE_V2_RECON_20260719.md`

#### Scope
Full recon on OpenCode 1.17.20 → 1.18.3 changes with focus on:
1. **Provider transformation layer** (`packages/opencode/src/provider/transform.ts`) — 1764 lines, NOT generated, NOT deprecated
2. **V2 session format** — Event-sourced, message parts (`ReasoningPart`, `ToolPart`, `StepStartPart`, etc.)
3. **AI SDK usage** — Still used via `streamText` in `ProviderTransform.options()`
4. **Models.dev integration** — Unchanged, still canonical model registry
5. **Per-prompt model selection** — New in 1.18.0 composer
6. **Subagent depth limit** — New in 1.18.2 (`subagent_depth` config)
7. **Desktop v2 migration** — Completed in 1.18.0

#### Key Findings (Preliminary)
- **transform.ts is VALID PR target** for 1.17.x and 1.18.x
- V2 changes session persistence, NOT provider protocol
- Gemma 4 thinking config must handle V2 `ReasoningPart` extraction
- Pi PR #2903 pattern directly applicable to `transform.ts`

#### Required Outputs
1. Version compatibility matrix (1.17.x vs 1.18.x provider behavior)
2. V2 message part → thinking token extraction logic
3. Config merge behavior verification (arrays still replaced entirely?)
4. Version detection method for config package (ModelGateway startup vs install script)
5. Breaking changes list for community config package version-gating

---

### TASK OPENCODE-01: OpenCode 1.18.3 V2 Architecture Recon
**Status**: ✅ READY TO DISPATCH
**Owner**: Researcher
**Priority**: P0-5 (Critical for Gemma 4 PR + config package)
**Deliverable**: `docs/research/R_OPENCODE_V2_RECON_20260719.md`

#### Scope
Full recon on OpenCode 1.17.20 → 1.18.3 changes with focus on:
1. **Provider transformation layer** (`packages/opencode/src/provider/transform.ts`) — 1764 lines, NOT generated, NOT deprecated
2. **V2 session format** — Event-sourced, message parts (`ReasoningPart`, `ToolPart`, `StepStartPart`, etc.)
3. **AI SDK usage** — Still used via `streamText` in `ProviderTransform.options()`
4. **Models.dev integration** — Unchanged, still canonical model registry
5. **Per-prompt model selection** — New in 1.18.0 composer
6. **Subagent depth limit** — New in 1.18.2 (`subagent_depth` config)
7. **Desktop v2 migration** — Completed in 1.18.0

#### Key Findings (Preliminary)
- **transform.ts is VALID PR target** for 1.17.x and 1.18.x
- V2 changes session persistence, NOT provider protocol
- Gemma 4 thinking config must handle V2 `ReasoningPart` extraction
- Pi PR #2903 pattern directly applicable to `transform.ts`

#### Required Outputs
1. Version compatibility matrix (1.17.x vs 1.18.x provider behavior)
2. V2 message part → thinking token extraction logic
3. Config merge behavior verification (arrays still replaced entirely?)
4. Version detection method for config package (ModelGateway startup vs install script)
5. Breaking changes list for community config package version-gating

---

### TASK INFRA-01: Version Change Watchdog System
**Status**: 📋 DESIGNED — NEW SYSTEMIC INFRASTRUCTURE
**Owner**: Researcher + Pillar P1 (Infrastructure)
**Priority**: P1 — Prevents future manual recon gaps
**Deliverable**: `docs/strategy/VERSION_CHANGE_WATCHDOG_SPEC_20260719.md` + implementation plan

#### Problem Statement
We upgraded OpenCode 1.17.20 → 1.18.3 this morning with **zero automated detection**. The Gemma 4 strategy had an entire oversight (Oversight 1) based on stale V2 assumptions. We need a system that:

1. **Monitors** local tool versions (OpenCode, Bun, Node, Python packages, Docker images)
2. **Detects** version changes on startup or scheduled interval
3. **Triggers** background research task automatically
4. **Collects** changelogs, breaking changes, migration guides, known issues
5. **Writes** structured briefing to disk (`data/briefings/version_change_<tool>_<version>.md`)
6. **Queues** for human review/oversight via Hivemind handoff

#### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ VERSION CHANGE WATCHDOG                                      │
├─────────────────────────────────────────────────────────────┤
│ 1. VERSION MONITOR (daemon/cron)                            │
│    - Checks: opencode --version, bun --version, pip list,   │
│      docker images, npm/yarn lockfiles                      │
│    - Stores: data/state/version_registry.json               │
│    - Triggers: on diff from last known state                │
│                                                              │
│ 2. RESEARCH TRIGGER (background task)                       │
│    - Spawns Researcher subagent with:                       │
│      * Tool name, old version, new version                  │
│      * Priority: P0 (breaking) / P1 (feature) / P2 (patch)  │
│    - Researcher uses Sovereign Search (T1-T4)               │
│                                                              │
│ 3. BRIEFING GENERATOR                                        │
│    - Template: data/templates/version_change_briefing.md    │
│    - Sections: Changelog, Breaking Changes, Migration,      │
│      Known Issues, Impact Assessment, Action Items          │
│    - Writes: data/briefings/version_change_<tool>_<ver>.md  │
│                                                              │
│ 4. OVERSIGHT QUEUE                                           │
│    - Hivemind handoff to Kali (or designated overseer)      │
│    - Packet: "VERSION CHANGE BRIEFING: <tool> <old>→<new>"  │
│    - Priority: 2 (high) for breaking, 1 for feature         │
│    - Human reviews, approves/defers/escalates               │
└─────────────────────────────────────────────────────────────┘
```

#### Integration Points
- **M1 AnyIO**: Background task via `anyio.create_task_group()`
- **M9 Error Integrity**: Typed errors, no silent failures
- **M11 Soul Integrity**: Briefings become session gnosis
- **M15 Sovereign Continuity**: Version registry persists across sessions
- **M23 Failure Integrity**: If research fails → queue with `[TOOL-CHAIN-COLLAPSE]` flag

#### MVP Scope (Week 1)
1. Version registry JSON + monitor script (cron @reboot + daily)
2. Researcher handoff template for version changes
3. Briefing template + disk writer
4. Hivemind handoff integration
5. Test with OpenCode 1.18.3 as first case

#### Future Extensions
- GitHub Release webhook subscription (real-time)
- Automated PR generation for config updates
- Dependency graph impact analysis (what Omega modules use this tool?)
- Cross-platform (Cline, Cursor, VS Code extension versions)

---

## 🔬 TASK TORMENT-02: Sigil & 15 Factions Deep Dive
**Status**: ✅ READY TO DISPATCH
**Owner**: Researcher
**Brief**: `data/coordination/RESEARCH_BRIEF_TORMENT_HIVE_20260719.md` (Phase 2)
**Deliverable**: `docs/research/R_TORMENT_SIGIL_FACTIONS_20260719.md`
**Mapping**: 15 factions → cognitive architectures (Athar=Skeptical Verifier, Godsmen=Growth Optimizer, etc.)
**Lady of Pain**: System Boundary Enforcer (M2 firewall personified)
**Portals**: Inter-agent communication channels
**Gate Towns**: Context drift / alignment shift detection
**Wards**: Cognitive domains / agent territories

---

## 🔬 TASK TORMENT-03: Nameless One's Journey
**Status**: ⏳ BLOCKED on TORMENT-02
**Owner**: Researcher
**Brief**: Phase 3 of Research Brief
**Deliverable**: `docs/research/R_TORMENT_NAMELESS_ONE_JOURNEY_20260719.md`
**Mapping**: 3 incarnations → entity facets; companions as Hivemind mirrors; 16 answers → ideal pathways; Fortress of Regrets → Qliphoth

---

## 🔬 TASK TORMENT-04: Planescape Cosmology Architecture
**Status**: ⏳ BLOCKED on TORMENT-03
**Owner**: Researcher
**Brief**: Phase 4 of Research Brief
**Deliverable**: `docs/research/R_TORMENT_COSMOLOGY_ARCHITECTURE_20260719.md`
**Mapping**: Great Wheel → cognitive realm topology; Outer Planes → agent specializations; Blood War → exploitation vs exploration; Petitioners→Proxies→Powers → User→Agent→Oversoul→Architect

---

## 🔬 TASK MAKALI-01: Open Questions Research
**Status**: ✅ READY TO DISPATCH
**Owner**: John Carmack (architectural review) + Researcher (SOTA survey)
**Questions**:
1. **SomaticState Integration**: Warm-start council models (30-90s load → near-zero)
2. **Cross-Council Memory**: Phase 4 research → next council's context?
3. **Streaming Council**: Pillars stream partial results for early distillation?
4. **Adaptive Tier Selection**: Dynamic model tier based on topic complexity?
5. **Council Chaining**: FINAL_SYNTHESIS → pillar input for higher council?

---

## 🔬 TASK SUBAGENT-01: Headless Subagent Pool Architecture
**Status**: ✅ READY TO DISPATCH
**Owner**: Researcher + Grok CLI (advisory)
**Deliverable**: Architecture doc for 24-account unified compute (8 Grok + 8 Copilot + 8 Cline)
**Unknowns**: Pool orchestrator design, credential integration with Omega-Vault, task decomposition algorithm, result aggregation with cognitive diversity weighting

---

## 🔬 TASK WARP-01: WARP Pool Deployment + Validation
**Status**: ✅ READY TO EXECUTE
**Owner**: Pillar P1 (Infrastructure)
**Action**: 
```bash
sudo ./scripts/deploy_warp_pool.sh
bash scripts/validate_warp_pool.sh
```
**Unknowns**: WireGuard compat, 3 namespace routing, Podman network integration, OCZ Nemotron rate limit verification

---

## 🔬 TASK OMEGA-VAULT-01: Phase 1 Research
**Status**: 📋 DESIGNED
**Owner**: Researcher + Pillar P1
**Deliverable**: OS keyring backend survey (secret-service vs gnome-keyring vs kwallet), provider schema research for 6+ APIs, fanotify/inotify passive watcher feasibility, Textual TUI design

---

## 🔬 TASK M2-FIREWALL-B-E: Migration Phases B-E
**Status**: 📋 DESIGNED (Phase A complete by Roc)
**Owner**: Roc Racoon
**Phases**:
- **B**: `subagent_dispatcher.py` — ROLE constants → WAD YAML (15 violations)
- **C**: `oracle.py` — Iris routing, MaKaLi logic (10 violations)
- **D**: `ics.py` — Channel constants, doc examples (7 violations)
- **E**: `fleet_status_tui.py` — TUI tree from WAD registry (18 violations)

---

## 🔬 TASK HERITAGE-01: 27-Term Backlog
**Status**: 📋 DESIGNED
**Owner**: doom_guy + verity
**Source**: Ken Walger Mining plan (D-298)
**Process**: Discovery → Vetting/Debate → Decision → Implementation per M14 pipeline

---

## 📊 DISPATCH QUEUE (Ready Now)

| Order | Task | Agent | Handoff Needed |
|-------|------|-------|----------------|
| **1** | Torment Phase 2 (Sigil/Factions) | Researcher | Create handoff from Kali |
| **2** | MaKaLi Open Questions | John Carmack + Researcher | Create handoff from Kali |
| **3** | Headless Subagent Pool | Researcher + Grok CLI | Create handoff from Kali |
| **4** | WARP Pool Deploy | Pillar P1 | Direct execution |
| **5** | Gemma 4 Step 2 (after vet) | P3 Engineering | Auto-unblocks on vet approval |

---

## 🚫 BLOCKED / DEFERRED

| Task | Blocked On | Unblock Condition |
|------|------------|-------------------|
| Gemma 4 Steps 2-13 | Heritage vet approval | doom_guy + verity sign off |
| Torment Phases 3-4 | Phase 2 complete | Researcher delivers Phase 2 |
| Omega-Vault Phase 1 | Scope confirmation | Researcher + P1 align |
| Ken Walger Mining | Phase 0 (all2md + sqlite-vec fix) | all2md installed, sqlite-vec patched |
| Decision Tools | Capacity | P3/P5 availability |
| Antigravity Multi-Account | Omega-Vault provider | Omega-Vault Phase 1-2 |

---

## 📁 KEY FILES REFERENCE

| File | Purpose |
|------|---------|
| `config/provider_capabilities.yaml` | Canonical capability matrix (Gemma 4 + all Google models) |
| `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` | Battle-ready Week 1 plan with 7 oversights, 12 edge cases, 5 opportunities |
| `docs/research/R_GEMMA4_GAP_RESEARCH_20260719.md` | All 15 gaps with sources, findings, decision impacts |
| `data/coordination/RESEARCH_BRIEF_TORMENT_HIVE_20260719.md` | 4-phase Researcher dispatch for Torment |
| `docs/research/R_TORMENT_HIVE_MECHANICS_20260719.md` | Phase 1 COMPLETE — 28 mechanical findings |
| `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` | Council architecture with 6 open questions |
| `docs/research/R_REPORT_DIGESTION_LAYER_OPTIMIZATION_20260719.md` | Digestion layer research |
| `src/omega/council/` | T0 coordinator scaffolding (6 modules) |

---

## 🎯 NEXT ACTIONS FOR KALI

1. **Monitor heritage vet** — Wait for doom_guy + verity completion
2. **Dispatch Torment Phase 2** — Researcher handoff (unblocks Hive-0)
3. **Dispatch MaKaLi questions** — John Carmack + Researcher handoff
4. **Dispatch Headless Pool** — Researcher + Grok CLI handoff
5. **Execute WARP Pool** — Direct Pillar P1 execution
6. **Post Hivemind context** — Declare session focus chain

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_inventory ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
