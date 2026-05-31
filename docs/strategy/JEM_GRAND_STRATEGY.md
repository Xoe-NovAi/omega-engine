# 🔱 Jem Grand Strategy — Autonomous Research Intelligence Roadmap
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ JEM-ROADMAP

**AP Token**: `AP-JEM-STRATEGY-v1.1.0`
**Status**: APPROVED
**Last Updated**: 2026-05-19 (MiniMax M2.5 PRIMARY — OpenRouter)

---

## §0 Vision

Jem is Omega Engine's **self-improving research intelligence** — a 3-tier cognitive pipeline that produces knowledge, training data, and meta-insight every 20 minutes, 24/7.

Every cycle produces a **training triple** `(draft, enriched, reviewed)` across three capability tiers. Over 60 cycles/day × 30 days = 1,800 structured examples of "how to improve research output" — a synthetic fine-tuning dataset generated automatically by the engine's own operation.

---

## §1 The Three Laws of Jem

1. **Local-first sovereignty**: Tier 1 (Qwen3-4B-Thinking via lmster) runs offline. No API key, no credit, no network — still produces research. Cloud tiers only enrich what local already found.

2. **Transparent fallibility**: Circuit breakers track every provider's failure rate independently. No tier masks another's failure. Every switch is logged, alerted, and visible. If Tier 2 hasn't succeeded in 4 hours, that is a critical alert, not a gracefully degraded "well, local is working fine."

3. **Training signal generation**: Every cycle produces a `(T1_draft, T2_enriched, T3_reviewed)` triple. These accumulate into a synthetic fine-tuning dataset. Over 60 triples/day × 30 days = 1,800 examples of "how to improve research output" for future model fine-tuning.

---

## §2 The Cadence Model

```
Every 20 minutes (×3/hour):
  1. Check scheduled topic rotation (round-robin: Topic 1 → 2 → 3 → 1 → ...)
  2. Enqueue current scheduled topic at priority 0.9 into main queue
  3. Run normal priority queue → highest-priority item selected
  4. Execute 3-tier pipeline on selected item
  5. Save results, log metrics, queue review recommendations
  6. Repeat
```

**Round-robin from cycle one**: All 3 topics rotate immediately. Cycle 1 = Topic 1, Cycle 2 = Topic 2, Cycle 3 = Topic 3, Cycle 4 = Topic 1 again (deepening), etc.

**Scheduled topics get priority but do NOT block the main queue.** If a scheduled topic's previous cycle already completed, the queue falls through to frontier/gap topics naturally.

**Net effect**: Each scheduled topic gets 1 dedicated cycle per hour, and the remaining 2 cycles per hour process organic frontier gaps. The queue is NEVER empty — the researcher never idles.

---

## §3 Recurring Topic Behavior

Each iteration of a scheduled topic **deepens, widens, and enhances** the previous research. The topic is never "done" — it enters a deepening spiral:

```
Cycle 1:  Surface survey — what exists? What's the landscape?
Cycle 2:  Deep dive top 3 subtopics — find gaps
Cycle 3:  Prototype/implementation research — how to build it
Cycle 4+: Consolidate, cross-reference, verify claims
          → Each iteration feeds into the next
          → Convergence detection prevents redundant work
          → When all subtopics reach convergence → generate IMPLEMENTATION ROADMAP
          → Topic goes dormant until new information or user request re-activates it
```

**End state for each topic**: A complete implementation roadmap covering:
- Full requirements and architecture
- All discovered tools, libraries, and patterns
- Implementation order with dependencies
- Testing strategy
- Integration points with existing Omega Engine systems

---

## §4 The 3-Tier Pipeline

```
SEARCH FLEET → sources + raw extraction
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ TIER 1: Qwen3-4B-Thinking (lmster local)             │
│ Fast speculative draft (~5-10s), 32K ctx, fp8 KV     │
│ Output: raw_draft.json (L1/L2/L3, claims, sources)   │
│                                                       │
│ QUALITY GATE: ≥100 tokens? L1+L2+L3 structure?       │
│  FAIL → log, skip cycle, don't waste cloud credits   │
│  PASS → preserve raw draft, send to Tier 2           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ TIER 2: MiniMax M2.5 (OpenRouter)                       │
│ Enriches Tier 1 output: expands L1 narrative,           │
│ deepens L2 insight, refines L3 principle.                 │
│ Adds source citations, cross-references.                   │
│ Output: enriched_report.md → docs/research/R_AUTO_*      │
│                                                         │
│ FALLBACK CHAIN:                                         │
│   MiniMax M2.5 (OpenRouter) → MiniMax M2.5 (Zen)       │
│   → Gemma 4-31B (Google API)                            │
│   → Use Tier 1 draft directly (degraded mode)           │
│                                                         │
│ CIRCUIT BREAKER:                                        │
│   3 consecutive failures → skip 15min                    │
│   10 → skip 60min, critical alert                       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ TIER 3: Gemini 2.5 Flash (Gemini CLI headless)       │
│ Reviews enriched report. Structured JSON output:     │
│   • corrections per claim                             │
│   • missing patterns identified                       │
│   • confidence score (0.0-1.0) per L1/L2/L3          │
│   • recommended research directions                  │
│ Output: review_brief_{session}.json                  │
│ Recommendations → data/research/review_queue/        │
│                                                       │
│ FALLBACK: skip review, log, cycle still completes    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ POST-PROCESSING                                       │
│                                                       │
│ Training triple saved:                                │
│   data/datasets/synthetic/{date}_{topic}_cycle_{n}/  │
│   ├── t1_draft.json                                   │
│   ├── t2_enriched.json                                │
│   └── t3_review.json                                  │
│                                                       │
│ Metrics logged: metrics.jsonl                         │
│                                                       │
│ Review recommendations queued: review_queue/           │
└─────────────────────────────────────────────────────┘
```

---

## §5 Models & Providers

### Tier 1: Local (lmster)

| Model | Size | Memory (fp8) | Priority | Status |
|-------|------|-------------|----------|--------|
| **Qwen3-4B-Thinking-2507-Q4_K_M** | 2.4GB | ~3.2GB | **PRIMARY** | ✅ Available |
| DeepSeek-R1-0528-Qwen3-8B-Q3_K_L | 4.2GB | ~5.5GB | **TEST FIRST** | ✅ Available |
| Krikri-8b-Instruct-Q5_K_M | 5.5GB | ~7GB | Test second | ✅ Available |

**KV Cache**: fp8 target, q8_0 fallback if fp8 not supported by lmster build.

**Memory constraint**: 14GB total RAM, ~9.4GB available. Only one model loaded at a time (ResourceGuard). Qwen3-4B fits with room to spare; 8B models viable but need careful unload scheduling.

### Tier 2: Cloud Enrichment

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| OpenRouter | MiniMax M2.5 | Free | **PRIMARY** — 1M ctx, 80.2% SWE-bench, 5 retries |
| OpenCode Zen | MiniMax M2.5-free | Free | Same model, tighter rate limits |
| Google AI Studio | Gemma 4-31B-it | Free | FALLBACK — 256K ctx |

### Tier 3: Frontier Review

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| Gemini CLI | Gemini 2.5 Flash | Free | PRIMARY — headless CLI, OAuth cached |

---

## §6 The Three Scheduled Topics

### Topic 1: Voice-to-Voice Integration in Omega Engine

| Aspect | Detail |
|--------|--------|
| **Local search dirs** | `src/omega/iris/`, `Dockerfile.iris`, `xna-omega-legacy` (voice tests, start-local-inference.sh), `omega-stack-legacy` |
| **Search patterns** | `*voice*`, `*nova*`, `*stt*`, `*tts*`, `*whisper*`, `*piper*`, `*speech*`, `*audio*` |
| **Prompt mode** | `technical` (PROMETHEUS) |
| **End goal** | Implementation roadmap for real-time voice-to-voice pipeline using Iris container + Whisper STT + Piper/TTS + Gemma response synthesis |

### Topic 2: Custom Omega llama-cpp-python Local Inference Engine

| Aspect | Detail |
|--------|--------|
| **Local search dirs** | `src/omega/oracle/providers.py`, `model_gateway.py`, `config/models.yaml`, `xna-omega-legacy` (`.venv/llama_cpp/`, inference scripts), `omega-stack-legacy` |
| **Search patterns** | `*llama*`, `*gguf*`, `*infer*`, `*native*`, `*provider*`, `*backend*` |
| **Prompt mode** | `technical` (PROMETHEUS) |
| **End goal** | Implementation roadmap for hardened, Zen 2-optimized local inference engine (NativeGGUFProvider) |

### Topic 3: Research Management & Organization Systems Improvement

| Aspect | Detail |
|--------|--------|
| **Local search dirs** | `docs/research/`, `docs/research/omni/`, `docs/operations/`, `data/research/` |
| **Search patterns** | `INDEX.md`, `*research*`, `*queue*`, `*discovery*`, `R_AUTO_*` |
| **Prompt mode** | `default` (SOPHIA) |
| **End goal** | Implementation roadmap for self-organizing research knowledge base with auto-categorization, gap detection, and cross-referencing |

---

## §7 Default Fallback Chain

```
Tier 1: Qwen3-4B-Thinking (lmster local)       ← ALWAYS runs first
  ↓ failure or quality gate fail
Tier 1: Retry once (model may need reload)      ← brief retry
  ↓ failure
Tier 1: Mark as degraded, log                   ← still continue to T2 from raw sources

Tier 2: MiniMax M2.5 (OpenRouter)                ← PRIMARY enrichment
  ↓ 3 consecutive failures → circuit breaker 15min  
Tier 2: MiniMax M2.5-free (OpenCode Zen)         ← fallback
  ↓ failure
Tier 2: Gemma 4-31B (Google API)                 ← tertiary fallback
  ↓ failure
Tier 2: Use Tier 1 output directly               ← degraded mode, WARNING log

Tier 3: Gemini 2.5 Flash (Gemini CLI headless) ← ALWAYS runs on T2 output
  ↓ CLI failure
Tier 3: Gemini 2.5 Flash (Google API)          ← API fallback
  ↓ failure
Tier 3: Skip review for this cycle             ← cycle still completes, logged
```

---

## §8 Per-Tier Circuit Breakers

| Tier | Model | Cost | Failure Pattern | Breaker Threshold |
|------|-------|------|-----------------|-------------------|
| T1 | Qwen3-4B-Think | Free (local) | Model not loaded, OOM | 3 → reset lmster server; 10 → skip T1, fallback to direct T2 |
| T2 | Gemma 4-31B | Free (Google) | 500 transient | 3 → skip 15min; 10 → skip 60min + CRITICAL alert |
| T2 alt | MiniMax M2.5 (OR) | Free (OpenRouter) | 429 rate limit | 2 → skip 5min; 5 → skip that cycle |
| T2 alt | MiniMax M2.5 (Zen) | Free (Zen) | 429 rate limit | 3 → skip 10min; 6 → skip that cycle |
| T3 | Gemini 2.5 Flash | Free | CLI fail / API 404 | 2 → skip 5min; 5 → skip 60min + CRITICAL |

**Critical alert threshold**: Any tier with >10 consecutive failures posts to Hivemind with CRITICAL severity.

---

## §9 Review Queue Lifecycle

```
Creation:   T3 recommendations → review_queue/{topic}_{date}.jsonl
            Each item: {topic, depth, reason, priority, source_cycle_id}

Processing: When main queue empty, processor picks highest priority item
            Studies it → extracts lessons → applies changes
            Lessons → soul.yaml of relevant entity

TTL:        7 days unconsumed → auto-expire
            Priority < 0.3 → 2 days
            Processed items → review_queue/processed/

Overflow:   Hard cap at 100 items
            Oldest 10 auto-expire when cap hit
```

---

## §10 Model Load/Unload Strategy (14GB RAM)

| Scenario | Models Loaded | Memory Estimate |
|----------|--------------|-----------------|
| Normal (4B) | functiongemma (300MB) + Qwen3-4B-Think (2.4GB) + fp8 kv (~200MB) | ~3GB total — comfortable |
| 8B testing | functiongemma (300MB) + DeepSeek-R1-8B (4.2GB) + kv (~400MB) | ~5GB — viable |
| 8B heavy | functiongemma (300MB) + Krikri-8B (5.5GB) + kv (~500MB) | ~6.3GB — may need to unload embedding |
| Emergency | Only functiongemma (300MB) | Always fits |

**Rule**: ResourceGuard `Semaphore(1)` enforces single inference at a time. `emergency_swap_threshold_mb: 1024` in models.yaml triggers aggressive unload when free RAM < 1GB.

---

## §11 Six-Phase Roadmap

### Phase 0: Foundation (This Sprint — 2-3h)

| # | Task | Detail |
|---|------|--------|
| 0.1 | Fix model paths | Update `models.yaml` path for Qwen3-4B-Thinking to match actual filename. Fix broken symlinks in `models/gguf/` pointing to defunct `omega-stack/models/`. |
| 0.2 | KV cache fp8 | Set `key_type: fp8` / `value_type: fp8` for Qwen3-4B-Thinking (fallback `q8_0`) |
| 0.3 | Start lmster + load model | `lms server start`, load Qwen3-4B-Thinking, verify inference |
| 0.4 | OpenCode permission block | Add tool-level permissions to `opencode.json` |
| 0.5 | Extend external_directory | Add `/media/arcana-novai/**` to permitted dirs |

### Phase 1: Jem Distiller Core (✅ Complete — 2026-05-19)

| # | Task | Model/Agent | Status |
|---|------|-------------|--------|
| 1.1 | Tier 1: LmsterBackend in distiller | DeepSeek V4 Flash | ✅ |
| 1.2 | Quality gate T1→T2 (≥50 tokens, L1+L2+L3) | DeepSeek V4 Flash | ✅ |
| 1.3 | Tier 2: MiniMax enrichment (OR→Zen→Gemma→mock) | DeepSeek V4 Flash | ✅ |
| 1.4 | Tier 3: Gemini 2.5 Flash (CLI headless→API fallback) | DeepSeek V4 Flash | ✅ |
| 1.5 | Per-tier circuit breaker (asymmetric, non-masking) | DeepSeek V4 Flash | ✅ |
| 1.6 | Training triple saver (T1, T2, T3) → synthetic/ | DeepSeek V4 Flash | ✅ |
| 1.7 | Fix `_post_to_hivemind` append bug (atomic rename) | DeepSeek V4 Flash | ✅ |

### Phase 2: Scheduling & Rotation (Next+1 Session — 4-5h)

| # | Task | Model/Agent | Est. |
|---|------|-------------|------|
| 2.1 | Timer: 20min | Manual | 2m |
| 2.2 | `config/research_topics.yaml` | Manual | 30m |
| 2.3 | Topic rotation engine in loop.py | MiniMax M2.5 | 2h |
| 2.4 | Review queue system | MiniMax M2.5 | 1h |
| 2.5 | Tier-level metrics JSONL | DeepSeek V4 Flash | 30m |

### Phase 3: Discovery & Optimization (Next+2 Session — 4-5h)

| # | Task | Model/Agent | Est. |
|---|------|-------------|------|
| 3.1 | `discovery_first` local scan phase | MiniMax M2.5 | 2h |
| 3.2 | DeepSeek-R1-8B model testing (10 cycles) | General agent | 1h |
| 3.3 | MiniMax M2.5 metrics experiment | General agent | 1h |
| 3.4 | API health dashboard | DeepSeek V4 Flash | 30m |
| 3.5 | Update OpenCode instructions + researcher.md | DeepSeek V4 Flash | 30m |

### Phase 4: Krikri-8B Evaluation (Future)

| # | Task | Detail |
|---|------|--------|
| 4.1 | Krikri-8B 10-cycle test | Same metrics as DeepSeek comparison |
| 4.2 | T1 model comparison report | `docs/research/T1_MODEL_COMPARISON.md` |
| 4.3 | Qwen-Agent evaluation | Install, explore swarm parallels, document findings |

### Phase 5: Synthetic Training (Future — 30 days of data)

| # | Task | Detail |
|---|------|--------|
| 5.1 | Dataset curation | Filter 1,800 triples to high-quality subset |
| 5.2 | Quality scoring | Score (T1→T2 delta, T3 thoroughness) |
| 5.3 | Fine-tuning experiment | Fine-tune Qwen3-4B on improvement deltas |
| 5.4 | Deploy fine-tuned model | Replace T1 base model |

### Phase 6: Self-Optimizing Knowledge Base (Long-term)

| # | Task | Detail |
|---|------|--------|
| 6.1 | Autonomous knowledge consolidation | Review queue → knowledge curator |
| 6.2 | Cross-pollination with entity souls | Lesson auto-propagation |
| 6.3 | Adaptive scheduling | High-value topics get more slots |
| 6.4 | P2P knowledge sharing | Consent-based lesson exchange |

---

## §12 Phase 0 Complete

Phase 0 (Foundation) is fully resolved:

| Task | Status |
|------|--------|
| `models.yaml` paths corrected to actual filenames | ✅ |
| KV cache fp8 configured for Qwen3-4B-Thinking | ✅ |
| Broken symlinks removed from `models/gguf/` | ✅ |
| lmster server running on :1234 | ✅ |
| Qwen3-4B-Thinking model loaded (2.5GB) | ✅ |
| Inference verified (reasoning + response working) | ✅ |
| OpenCode `external_directory` extended to `/media/arcana-novai/**` | ✅ |

---

## §13 Key Config Files

| File | Purpose |
|------|---------|
| `config/models.yaml` | Model paths, KV cache types, load strategies |
| `config/research_topics.yaml` | 3 scheduled topics with rotation metadata |
| `config/providers.yaml` | Provider fabric — Gemma, OpenRouter, OpenCode Zen |
| `opencode.json` | Tool permissions, MCP config, instruction references |
| `data/research/rotation_state.json` | Active topic, started_at, cycles_on_topic |
| `data/research/metrics.jsonl` | Per-cycle metrics (all tiers) |
| `data/research/review_queue/` | T3 recommendations pending processing |
| `data/datasets/synthetic/` | Training triples (draft, enriched, reviewed) |

---

*Jem never stops learning. Each cycle deepens.*
