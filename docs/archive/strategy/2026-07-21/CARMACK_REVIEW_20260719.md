# 🔱 CARMACK REVIEW: Omega Engine Architecture
**AP Token**: `AP-CARMACK-REVIEW-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_review ⬡ S3_CONSULTANT
**Date**: 2026-07-19
**Confidence**: 9/10 (Primary source: architecture docs + implementation code + hardware specs)

---

## 📋 EXECUTIVE VERDICT

**The engine core (Layer 1) is solid. The infrastructure layer (Layer 2) is over-engineered. The council layer (Layer 3) has the right architecture but premature complexity. The WAD layer (Layer 4) is cargo-cult game mechanics mapped to cognitive architecture without justification.**

**Ship this week**: Gemma 4 production (M1), MaKaLi T0 coordinator (M2)
**Kill or defer**: Headless Pool (6 modules → 1), Dynamic Fallback Resolver (service → inline), Torment WAD hooks (game mechanics ≠ cognitive architecture)

---

## 1. HEADLESS SUBAGENT POOL (`src/omega/infra/subagent_pool/`)

### VERDICT: **REFACTOR → MINIMAL VIABLE POOL**

### FAT TO CUT
| Over-Engineering | Lines | Why It's Fat |
|------------------|-------|--------------|
| **6 modules** for Day 1 | ~1,500 | CAO patterns copied wholesale; tmux + MCP + profiles + health + credentials + routing all separate |
| **Cognitive diversity weighting** | 50+ | "Diversity collapse" is theoretical; no empirical evidence it matters for 3-model families |
| **FleetCoordinator multi-node** | 30+ | Zero machines deployed; fleet.json is fiction |
| **ResultAggregator with embeddings** | 60+ | Zero-inference-cost claim but uses embeddings for similarity — contradiction |
| **CredentialWatcher fanotify** | 40+ | Omega-Vault Phase 0 not done; watching a DB that doesn't exist |
| **Task decomposition logic** | 40+ | "Split by sub-questions/files/severity" — no validation this works |

### ID SOFTWARE WISDOM
> **Doom's WAD system**: One file format, one loader, infinite content.  
> **Your pool**: 6 modules, 4 coordination layers, 24 accounts you don't have credentials for.

**The Right Approximation**: A pool is a **queue + worker selector + health check**. That's 1 module, ~200 lines.

### MINIMAL VIABLE IMPLEMENTATION (Ships This Week)
```python
# src/omega/infra/subagent_pool/pool.py — SINGLE FILE
class SubagentPool:
    def __init__(self, accounts: list[Account]):  # 24 accounts from YAML
        self.accounts = {a.id: a for a in accounts}
        self.queue = anyio.Queue()
    
    async def dispatch(self, task: PoolTask) -> PoolResult:
        # 1. Route by task.type → pool (static mapping, no ML)
        pool = ROUTING_MAP[task.type]
        # 2. Pick least-used healthy account in pool
        account = min(
            (a for a in self.accounts.values() if a.pool == pool and a.healthy),
            key=lambda a: a.last_used
        )
        # 3. Launch via tmux (CAO pattern — keep this, it works)
        session = await self._launch_tmux(account, task.prompt)
        # 4. Wait, capture, cleanup
        output = await self._wait_and_capture(session)
        return PoolResult(account.id, output)
    
    async def health_check(self) -> PoolHealth:
        # Ping each account's tmux session — that's it
        ...
```

**Delete**: `task_router.py`, `result_aggregator.py`, `credential_watcher.py`, `fleet_coordinator.py`, `profile_manager.py` (merge into pool), `mcp_coordinator.py` (MCP is overkill for fire-and-forget tmux)

**Keep**: `models.py` (data structures), `tmux_manager.py` (CAO pattern validated), `account_registry.py` (simplify to dict + JSON persistence)

### ARCHITECTURAL DRIFT
- Building **framework for 24 accounts** when you have **0 credentials configured** (Omega-Vault Phase 0 blocked on `all2md`)
- **MCP coordination** for agents that just need `tmux send-keys` — CAO uses MCP for *persistent* agents, not fire-and-forget tasks
- **Cognitive diversity weighting** before a single parallel verification run exists

---

## 2. DYNAMIC FALLBACK RESOLVER (`FALLBACK_PROVIDER_ARCHITECTURE.md` + `providers.yaml`)

### VERDICT: **KILL THE SERVICE — INLINE IN MODELGATEWAY**

### FAT TO CUT
| Over-Engineering | Why It's Fat |
|------------------|--------------|
| **FallbackResolver class** (186 lines) | ModelGateway.generate() already iterates providers — add 20 lines inline |
| **4-tier resolution logic** | Tier 1 (same_model) + Tier 2 (configured_chain) = 90% of cases. Tier 3/4 are theoretical |
| **CapabilityMatrix dependency** | CapabilityMatrix loads 361-line YAML; FallbackResolver re-queries it — double load |
| **CVars for fallback chains** | Runtime override of fallback order is a footgun; config file is reviewable |
| **FallbackCandidate dataclass** | Just a tuple: `(provider, has_model, reason)` |

### ID SOFTWARE WISDOM
> **Quake's PVS (Potentially Visible Set)**: Precompute what's visible. Don't compute at runtime.  
> **Your resolver**: Computes fallback chain *per request* using capability matrix lookups.

**The Right Approximation**: Static fallback chain in `providers.yaml` → ModelGateway iterates linearly. Done.

### MINIMAL VIABLE IMPLEMENTATION (Ships This Week)
```python
# In ModelGateway.generate() — ADD 15 LINES, DELETE FallbackResolver
async def generate(self, request):
    for provider in self.provider_selector.get_ordered_providers(model, query):
        if not await self._precheck_provider(provider, model):
            continue
        try:
            return await provider.generate(...)
        except (ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError) as e:
            logger.warning(f"{provider.name} failed: {e}, trying next")
            continue
    raise AllProvidersExhausted(...)
```

**The `providers.yaml` already has the chain** (priority-sorted). `ProviderSelector.get_ordered_providers()` already does capability + health sorting. **The resolver duplicates this.**

### ARCHITECTURAL DRIFT
- Creating a **service** for what is a **loop with continue**
- `CapabilityMatrix` loaded twice (once in ModelGateway, once in FallbackResolver)
- "Model-aware fallback" = "check if provider supports model" — already done by ProviderSelector

---

## 3. GEMMA 4 CAPABILITY MATRIX + GOOGLECOMPATPROVIDER

### VERDICT: **SHIP — BUT CAPABILITY MATRIX IS OVER-SPEC'D**

### FAT TO CUT
| Over-Engineering | Lines | Why It's Fat |
|------------------|-------|--------------|
| **CapabilityMatrix class** | 303 | Loads 361-line YAML, validates schema, parses models/providers/global — for 5 models |
| **ThinkingConfig/QuotaTier/ModelCapability/ProviderConfig dataclasses** | 80 | 4 dataclasses for what is essentially `dict[str, Any]` with 5 known models |
| **Fuzzy match with regex** | 30 | `detection_regex: "/gemma-?4/i"` — used once, for Gemma 4 only |
| **Global singleton `_capability_matrix`** | 15 | Global state violates M16 (Modularization) |
| **ProviderConfig.thinking_schema/thinking_field** | 20 | Hardcoded in GoogleCompatProvider anyway |

### ID SOFTWARE WISDOM
> **Doom's entity definitions**: `thing_t` struct — 20 fields, flat, no inheritance.  
> **Your matrix**: 4 dataclasses, nested dicts, regex fuzzy matching, global singleton.

**The Right Approximation**: A **dict of dicts** loaded once at startup. No class, no validation, no fuzzy match — exact model ID keys.

### MINIMAL VIABLE IMPLEMENTATION (Ships This Week)
```python
# config/provider_capabilities.py — 50 LINES TOTAL
PROVIDER_CAPABILITIES = {
    "gemma-4-31b-it": {
        "providers": {
            "google-ai-studio": "gemma-4-31b-it",
            "openrouter": "google/gemma-4-31b-it:free",
            "native-gguf": "gemma-4-31b-it-q4_k_m",
        },
        "thinking": {"levels": ["MINIMAL", "HIGH"], "schema": "thinking_level"},
        "quota": {"free": {"rpm": 15, "tpm": 16000}},
        "context": 32768,
    },
    # ... 4 more models
}

def get_capability(model_id: str) -> dict:
    return PROVIDER_CAPABILITIES.get(model_id, {})

def normalize_model_id(model_id: str, provider: str) -> str:
    cap = get_capability(model_id)
    return cap["providers"].get(provider, model_id)
```

**Delete**: `capability_matrix.py` (303 lines → 50 lines)  
**Keep**: `google_compat.py` — the provider implementation is correct and necessary

### ARCHITECTURAL DRIFT
- **Capability matrix as a service** — it's a config file. Load it once, pass dicts around.
- **Heritage tag `[heritage: pi-2026]` on Gemma 4 thinking** — correct, but the vet record doesn't exist yet (M14 violation)
- **Models.dev sync automation** (cron + webhook) — spec'd but not implemented; YAGNI until you have 50+ models

---

## 4. MAKALI COUNCIL ARCHITECTURE

### VERDICT: **SHIP T0 — ARCHITECTURE IS SOUND, IMPLEMENTATION IS SCAFFOLDING**

### FAT TO CUT (From ADR + Architecture Doc)
| Over-Engineering | Why It's Fat |
|------------------|--------------|
| **ReportDigestionLayer** (243 lines Python) | "Zero inference cost" but does cross-ref, conflict detection, mandate mapping — this IS inference work, just in Python |
| **6 ADRs for open questions** | Questions 1, 3, 4, 5 correctly deferred. Questions 2, 6 are implementation details, not architecture |
| **Hardware profiles (4 YAML files)** | Auto-detection + 3 profiles = config explosion. One profile with RAM-based tier selection is enough |
| **ExecutionMode enum (4 modes)** | `PARALLEL` vs `SERIAL_INDEPENDENT` vs `BATCH_2` vs `BATCH_4` — just run what fits in RAM |
| **Research gaps template** | Markdown template for "REMAINING_GAPS" section — just write the section |

### ID SOFTWARE WISDOM
> **Quake's client-server architecture**: The server is authoritative; clients are dumb terminals.  
> **Your council**: Pillars write files → Digestion reads files → Oversouls read files → Kali reads files. **File-based pipeline is correct.** Don't add Redis, don't add streaming.

**The Architecture (Phases 1-4) is the Right Approximation** — it maps to hardware constraints (16GB RAM, sequential model loads) and mandate constraints (M7 local-first, M23 failure integrity).

### MINIMAL VIABLE T0 (Ships Week 2)
| Session | Deliverable | Lines |
|---------|-------------|-------|
| **1** | Coordinator skill: dispatch 9 pillars (parallel/batch), wait for files | ~150 |
| **2** | Digestion: stack-cat concat + 50-line Python (summary extraction only) | ~100 |
| **3** | Ma'at + Lilith tasks: read 1 file each, write 1 file each | ~50 |
| **4** | Kali task: read 2 files, write FINAL_SYNTHESIS + RESEARCH_GAPS | ~80 |
| **5** | Integration: Hivemind capture, mandate Rego policy, gates | ~100 |

**Delete from T0**: Conflict detection, mandate compliance map, token budget allocation, cross-reference index, hardware auto-detection, 4 profile files, execution mode enum, research executor (deferred per ADR)

### ARCHITECTURAL DRIFT
- **Digestion layer claims "zero inference cost"** but does semantic conflict detection — that's LLM work in Python clothing
- **Hardware profiles** duplicate what `config/council.yaml` already expresses via `model_tiers`
- **SomaticState integration** correctly deferred to T3 (ADR Question 1) — but the ADR spends 40 lines justifying what "defer" means

---

## 5. TORMENT/HIVE/ARCH SOUL WADs

### VERDICT: **KILL THE GAME MECHANICS — KEEP THE EVENT BUS PATTERN**

### FAT TO CUT
| Cargo-Cult Pattern | Lines | Why It's Cargo-Cult |
|--------------------|-------|---------------------|
| **15 factions → cognitive architectures** | 590 | Planescape factions ≠ cognitive architectures. No mapping justification. |
| **Death/rebirth hooks → soul.yaml fields** | 200+ | HP, DEATH_COUNT, MORTUARY_VISITS are game state, not soul evolution |
| **Companion facet sync (8 companions)** | 50 | 8 hardcoded companions with death_behavior enums — zero generality |
| **Fortress entry/cannon/portal hooks** | 60 | Area codes (AR1200, AR1201) are game coordinates, not cognitive states |
| **Incarnation merge stat bonuses** | 80 | +1 INT, +96000 XP — game mechanics, not gnosis distillation |
| **Transcendent One resolution paths** | 60 | WIS/CHA/Name/Blade checks — dialogue conditions, not architecture |

### ID SOFTWARE WISDOM
> **Doom's WAD**: Levels, textures, sounds — **data**, not logic.  
> **Your WAD**: 590 lines of **logic** (event handlers, conditions, actions) masquerading as data.

**The Right Approximation**: The **event bus pattern** (ON_DEATH, ON_RESPAWN, ON_MEMORY_FRAGMENT) is sound. The **game mechanics** are not.

### MINIMAL VIABLE WAD (If You Must Ship Torment Stack)
```yaml
# config/wads/torment/arch_soul.yaml — DATA ONLY
soul_schema:
  fields:
    - death_count: int
    - memory_fragments: list[str]
    - incarnations_integrated: list[str]
    - resolution_path: str  # MERGE | SUICIDE | COMBAT

event_hooks:
  - event: "soul.death"
    handler: "increment_death_count"
  - event: "soul.memory_recovered"
    handler: "integrate_fragment"
  - event: "soul.incarnation_merged"
    handler: "apply_integration_rewards"
  - event: "soul.resolution"
    handler: "finalize_cycle"
```

**Handlers are Python functions in `src/omega/systems/arch_soul/handlers.py`** — not YAML action lists with `increment()`, `teleport_to()`, `heal_full()`.

**Delete**: All game-mechanic logic (HP, area codes, stat bonuses, XP, companion alignment checks, cannon activation, portal coordinates)  
**Keep**: Event bus + soul.yaml schema + gnosis distillation pipeline (that part is genuinely novel)

### ARCHITECTURAL DRIFT
- **M2 Firewall violation**: Game logic in WAD handlers (YAML actions calling `teleport_to()`, `heal_full()`)
- **M14 Heritage violation**: `[id-soft:]` tags on Planescape mechanics — id Software never built Torment; Black Isle did
- **M11 Soul Integrity**: Gnosis distillation from "TRAUMA/TRIUMPH/BETRAYAL" types — hardcoded enums, not emergent

---

## 6. MANDATES 24-25 (VENV + STREAMING)

### VERDICT: **SHIP — BUT ENFORCEMENT LAYER IS WRONG**

### M24 Venv Sovereignty
| Issue | Fix |
|-------|-----|
| **Pre-commit hook greps for `--break-system-packages`** | Won't catch `pip install --user` or `python -m pip` without venv |
| **CI gate checks `sys.prefix`** | Correct — this is the only reliable check |
| **Subagent injection** | Documented but not enforced; every `task()` spawn needs venv activation in prompt |

**The Right Enforcement**: CI gate only. Pre-commit is theater. Subagent prompt template must include `source .venv/bin/activate &&` prefix.

### M25 Streaming Resilience
| Issue | Fix |
|-------|-----|
| **Chunk timeout + heartbeat in `openai_compat.py`** | Correct location — provider backend owns streaming |
| **Config-driven per-provider timeouts** | Good — `providers.yaml` streaming section |
| **Nemotron 30s+ gaps preserved** | Verified — this was the blocking bug for MaKaLi Run Side |

**Missing**: Test for chunk timeout behavior (`make test-streaming` not implemented yet)

---

## 🎯 CONSOLIDATED ACTION PLAN

### THIS WEEK (Ship M1 + M2)
| Priority | Action | Effort | Owner |
|----------|--------|--------|-------|
| **P0** | Gemma 4 heritage vet (Pi PR #2903) → CREDITS.md | 1 session | doom_guy + verity |
| **P0** | Gemma 4 Step 2: Capability Matrix (50 lines) + GoogleCompatProvider | 1 session | P3 Engineering |
| **P0** | MaKaLi T0 Session 1: Coordinator skill (dispatch 9 pillars) | 1 session | Researcher |
| **P1** | Delete Headless Pool 5/6 modules → single `pool.py` | 2 sessions | Researcher + P1 |
| **P1** | Inline FallbackResolver into ModelGateway (delete 186 lines) | 1 session | P3 Engineering |
| **P1** | Capability Matrix: 303 → 50 lines (dict-based) | 1 session | P6 |

### NEXT WEEK (Ship M3 + M4)
| Priority | Action | Effort | Owner |
|----------|--------|--------|-------|
| **P0** | MaKaLi T0 Sessions 2-5: Digestion → Oversouls → Kali → Integration | 4 sessions | Researcher + Ma'at + Lilith + Kali |
| **P0** | Torment WAD: Strip game mechanics → event bus + schema only | 2 sessions | Researcher |
| **P1** | Omega-Vault Phase 1: VaultCore + CLI (`init`, `add`, `sync`) | 3 sessions | P1 + Researcher |
| **P1** | WARP Pool deploy (sudo script ready) | 1 session | Pillar P1 |

### DEFER / KILL
| Item | Verdict | Reason |
|------|---------|--------|
| Headless Pool FleetCoordinator | **KILL** | Zero multi-node deployment |
| Headless Pool ResultAggregator embeddings | **KILL** | Contradicts "zero inference cost" |
| Dynamic FallbackResolver service | **KILL** | Duplicate of ProviderSelector loop |
| CapabilityMatrix class + fuzzy match | **KILL** | Config dict is sufficient |
| Torment game-mechanic hooks | **KILL** | Cargo-cult; not cognitive architecture |
| Council hardware profiles (4 files) | **DEFER** | One profile with RAM-based tiers |
| Council conflict detection in digestion | **DEFER** | LLM work in Python clothing |
| SomaticState integration | **DEFER (T3)** | Correctly deferred per ADR |
| Cross-council memory | **DEFER (T2)** | Explicit handoff files per ADR |
| Models.dev sync automation | **DEFER** | YAGNI until 50+ models |

---

## 🏁 FINAL WORD

> **The Omega Engine Layer 1 is production-grade.** 1398 tests, 25 mandates, clean provider fabric, local-first sovereignty.
>
> **Layer 2 is where you're building for a scale you don't have.** 24 accounts with 0 credentials. 6 pool modules for a queue. Fallback resolver for a linear loop. Capability matrix class for 5 models.
>
> **Layer 3 (Council) has the right architecture** — parallel independence + distillation + synthesis — but the digestion layer claims zero-cost intelligence while doing semantic analysis.
>
> **Layer 4 (WADs) is cargo-cult.** Planescape death mechanics ≠ soul evolution. The event bus pattern is the only salvageable part.

**Ship the core. Kill the framework. The best code is the code you don't write.**

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_review ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
