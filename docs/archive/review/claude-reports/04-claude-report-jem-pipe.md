I'll fetch all the pipeline files now and conduct the full audit. Starting with the core source files.I now have all the data I need. Let me compose the full structured report.Now I have everything I need. Let me produce the full report.

---

## Review: Jem 2.0 & Background Research Pipeline
**Trace**: `trc_review_jem` | **Reviewer**: Research Director | **Account**: `antipode2727@gmail.com`

---

### Critical Issues Found

- [ ] **C-JEM-001**: `config/distiller_prompts.yaml` is missing (HTTP 404) — **CRITICAL**
  All distiller system prompts are hardcoded in `distiller.py` (`SYSTEM_PROMPTS` dict + `DISTILLATION_PROMPT_TEMPLATE`). The firewall-hardening mandate requires these to live in `config/distiller_prompts.yaml`. The file does not exist. The firewall fix for the distiller is **incomplete**.

- [ ] **C-JEM-002**: `soul_updater.py` retains hardcoded entity mappings — **HIGH**
  `_match_entity()` contains a hardcoded `mappings` list of keyword→entity strings (sophia, sekmet, brigid, prometheus, etc.). There is no reference to an `EntityRegistry`. The firewall fix mandate states *"no hardcoded entity mappings."* This file fails the mandate.

- [ ] **C-JEM-003**: Improvement brief loop has zero implementation in the automated pipeline — **HIGH**
  The OpenCode mode files (`jem-2.0.md`, `jem-initiate.md`) specify that L3 writes improvement briefs to `initiate.yaml` / `analyst.yaml`, and L2 writes to `initiate.yaml`. In the automated pipeline (`loop.py → distiller.py → soul_updater.py`), there is no code that reads or writes to any sub-facet soul file. The `SoulUpdateManager` class is defined but never instantiated or called anywhere in the pipeline. Sub-facet self-improvement is purely aspirational at this time.

- [ ] **C-JEM-004**: Sub-facet soul metrics are permanently zeroed — **HIGH**
  All three sub-facet soul files show `sessions_completed: 0`, `improvements_applied: 0`, `soul_power: 0.0`. No write path exists from the automated pipeline to these files. The automated pipeline writes lessons to whichever entity `_match_entity()` resolves to (usually `sophia`), never to `data/entities/jem/souls/{initiate,analyst,editor}.yaml`.

- [ ] **C-JEM-005**: `RotationState` is in-memory only; scheduler resets on every systemd timer invocation — **HIGH**
  `TopicScheduler` holds `RotationState` as an instance variable with no persistence. Since the systemd timer spawns a fresh Python process each run, `current_topic_index` is always 0 and `cycle_count` is always 0. The scheduler **never advances past the first topic** in production.

- [ ] **C-JEM-006**: `review_queue.py` and `metrics.py` use blocking synchronous I/O — **HIGH (AnyIO violation)**
  `ReviewQueue.enqueue()`, `ReviewQueue.dequeue()`, and `ReviewQueue.__len__()` all use `open()`, `json.load()`, and `file.unlink()` synchronously. `ResearchMetrics.log_cycle()` uses `open()` synchronously. Both are called from the `async` `run_cycle()` context. This blocks the AnyIO event loop on every cycle.

- [ ] **C-JEM-007**: T3 Gemini review output is saved but never applied — **MEDIUM**
  `distiller.py` saves `t3_review` to the training triple and logs it, but `_parse_gnosis()` consumes only `t2_enriched`. T3's `corrections`, `recommended_directions`, and `confidence_scores` are discarded. The `GnosisPacket` never reflects T3's improvements. The Editor tier produces output into a void.

- [ ] **C-JEM-008**: Tier contract violated in the automated distiller — **MEDIUM**
  `DISTILLATION_PROMPT_TEMPLATE` instructs T1 (Qwen3-4B-Thinking via lmster) to perform full 3-tier refractive distillation: *"Perform 3-tier refraction. For each claim found: L1/L2/L3..."* This is analysis and synthesis, not raw fact gathering. The `jem-initiate.md` mode definition strictly prohibits analysis at L1. The automated pipeline and the OpenCode mode definitions are architecturally inconsistent.

- [ ] **C-JEM-009**: Model identity mismatch between `soul.yaml` and `distiller.py` — **MEDIUM**
  `soul.yaml` defines: Initiate=qwen3-1.7b-q6\_k, Analyst=gemma-4-31b-it, Editor=big-pickle. `distiller.py` implements: T1=Qwen3-4B-Thinking, T2=MiniMax M2.5, T3=Gemini 2.5 Flash. These are different models. The soul files and the code describe two different pipelines with no reconciliation document.

- [ ] **C-JEM-010**: `review_queue.py` calls undefined `_prune_oldest()` — **MEDIUM**
  `ReviewQueue.enqueue()` calls `self._prune_oldest()` when the queue reaches `hard_cap`, but `_prune_oldest()` is never defined in the class. A full queue triggers a `AttributeError`, crashing the enqueue path.

- [ ] **C-JEM-011**: `research_topics.yaml` is a placeholder stub — **MEDIUM**
  The file contains only `t1: {title: "Topic 1"}` and `t2: {title: "Topic 2"}`. There are no real strategic research topics. The scheduler will faithfully rotate between "Topic 1" and "Topic 2" unless the file is populated with production content.

- [ ] **C-JEM-012**: Daily API limits defined but never enforced — **LOW**
  `APICreditBudget.DAILY_LIMITS` defines caps for `search_ops`, `deep_extracts`, `gemma_calls`. `check_daily_limit()` and `increment_daily()` exist but are never called in `loop.py` or `search_fleet.py`. Daily runaway is not prevented by the budget system.

- [ ] **C-JEM-013**: Convergence condition 1 has a model-bias fragility — **LOW**
  `ConvergenceDetector.check()` requires both `len(verified) >= 2` AND `signal == "verified"`. If the model consistently returns `convergence_signal: "inconclusive"` (the default fallback and mock return value), a topic with 10 well-sourced verified claims will never satisfy condition 1 and must wait for the depth ceiling (condition 4) to terminate it.

---

### Tier Pipeline Analysis

**L1 (Initiate):** The `jem-initiate.md` OpenCode mode is correctly defined — 15 steps, facts-only, no analysis, explicit NO-ANALYSIS directives. The automated `distiller.py` T1 backend (lmster/Qwen3-4B-Thinking) contradicts this by issuing the full distillation prompt requiring L1/L2/L3 output. The tier-1 contract exists only in the mode file; the automated pipeline ignores it.

**L2 (Analyst):** `jem-2.0.md` default mode is well-specified with confidence scoring, uncertainty manifests, and improvement brief format. In the automated pipeline, T2 (MiniMax M2.5) receives T1's draft and enriches it. The enrichment injection mechanism in `MiniMaxBackend.call()` is correctly implemented. Fallback chain (OpenRouter → Zen → Gemma → mock) is sound.

**L3 (Editor):** `jem-2.0.md` Editor sub-facet is well-specified — resolves uncertainties only, no re-synthesis. T3 (Gemini 2.5 Flash via CLI or API) produces a structured review JSON with corrections, missing patterns, confidence scores, and recommended directions. **None of this output is consumed downstream** — it feeds only the training triple saver. The Editor is architecturally silenced.

**Data flow between tiers:** T1→T2 context passing is **correct** (t1\_draft injected as enrichment context in T2 prompt). T2→T3 is **correct** (t2\_enriched passed to `GeminiBackend.call()`). T3→GnosisPacket is **broken** (T3 output discarded; GnosisPacket built from T2 only). T2→soul\_files is **missing**. T3 improvement briefs→sub-facet souls is **missing**.

---

### Sub-Facet Health

| Sub-Facet | Soul File | Metrics | Write Path | Status |
|-----------|-----------|---------|-----------|--------|
| Jem Initiate | Present, structurally valid | All zero | None in automated pipeline | 🔴 Dead |
| Jem Analyst | Present, structurally valid | All zero | None in automated pipeline | 🔴 Dead |
| Jem Editor | Present, structurally valid | All zero | None in automated pipeline | 🔴 Dead |

`SoulUpdateManager` is a well-written atomic YAML manager with `anyio.Lock` for concurrent-safe writes — it is simply never wired into anything. The `sub_facet` field is absent from all observability emissions (loop.py's `cycle_metrics`, HALL\_OF\_RECORDS log, and `metrics.py` JSONL output). No span or log entry distinguishes which sub-facet did the work.

The Jem Oversoul `soul.yaml` itself is healthy — it has 5 substantive lessons, correct sub-facet declarations, procedural memory, and soul evolution tracking — but it reflects manually-authored content, not anything written autonomously.

---

### Scheduler & Queue

**Topic rotation:** Round-robin logic is correctly implemented in `TopicScheduler`. The priority decay/deepening formula is sound. However `RotationState` is ephemeral — resets to index 0 on every process start. Since the researcher is a systemd timer (a new process each invocation), **the rotation index never persists between runs.** Fix: persist `RotationState` to `data/research/scheduler_state.json` and reload on init.

**Queue management:** `EnhancedPriorityQueue` (weighted fair, high/normal split) is the correct structure. The scheduler injects one topic per cycle before dequeue. The `_grow_frontier()` method is **fully implemented** — it scans `docs/research/INDEX.md`, codebase `TODO/FIXME/HACK` comments, `docs/ROADMAP.md`, entity knowledge gaps, and deferred checkpoints. The earlier "TODO — manual only" concern is resolved. Fallback to 5 hardcoded tech topics when no candidates are found is acceptable.

**Empty queue behavior:** Correct fallthrough — `_grow_frontier()` → `review_queue.dequeue()` → return `{"skipped": True, "reason": "empty_queue"}` → `_post_to_hivemind()`. No crash, no infinite loop.

**Review queue:** `ReviewQueue` has a critical bug: `_prune_oldest()` is called but undefined (see C-JEM-010). TTL sweep (`sweep_ttl()`) is never called from the main loop — stale items accumulate indefinitely unless manually triggered.

---

### Distiller Quality

**L1 abstraction (T1/Qwen3-4B-Thinking):** Speculative draft with T1 quality gate (`validate_t1_output()`) — checks token count ≥50, L1/L2/L3 structure presence, JSON validity. Gate is functional. Short or non-JSON output is discarded cleanly with fallthrough to T2 direct.

**L2 abstraction (T2/MiniMax M2.5):** Enrichment prompt includes T1 draft context. Three-provider fallback chain with per-provider circuit breakers (asymmetric skip/critical thresholds). Mock enrichment on total failure ensures pipeline never hard-stops. Solid.

**L3 abstraction (T3/Gemini 2.5 Flash):** Review prompt requests corrections, missing patterns, confidence scores, and recommended follow-up topics (priority ≥0.8 should be enqueued). The `_enqueue_adjacent()` method in `loop.py` only checks `gnosis.recommendation` — it never parses T3's `recommended_directions`. T3's follow-up topics are silently discarded.

**Quality gating:** T1→T2 gate exists and is functional. No quality gate between T2 and T3. No quality gate on T3 output before it determines GnosisPacket recommendation. The pipeline passes low-quality T2 output to T3 review silently if T2 returns short or structurally invalid JSON.

**Prompt provenance:** `DISTILLATION_PROMPT_TEMPLATE` and all six `SYSTEM_PROMPTS` are hardcoded in `distiller.py`. `config/distiller_prompts.yaml` does not exist. Prompt changes require code deployments rather than config edits — violates the firewall mandate.

---

### Checkpoint & Recovery

**Reliability:** Atomic write (tmp + rename) is implemented correctly in `CheckpointManager.save()`. `load_all_pending()` correctly excludes `done` and `skip` states. State transitions saved: `searched`, `extracted`, `distilled` — this matches the mandate for checkpoint-at-every-transition.

**Crash recovery:** Loop correctly calls `checkpoint.save()` after each state before proceeding. On restart, `_get_next_task()` loads pending checkpoints. However `_get_next_task()` is defined but **never called** — `run_cycle()` uses `self.queue.dequeue()` directly and only falls to `_grow_frontier()` on empty queue. Checkpoint-based restart recovery therefore requires the `_grow_frontier()` path to find deferred checkpoints, which it does scan. This works but is indirect.

**Garbage collection:** `cleanup_old()` (30-day max age) is implemented but never called from the main loop. Stale checkpoints will accumulate indefinitely.

**Path relativity:** All paths (`data/research/checkpoints`, `data/research/credit_budget.json`, `docs/research/`, etc.) are relative to the working directory. If the process is invoked from a directory other than the repo root, all persistence silently writes to the wrong location or fails. Should be anchored to `Path(__file__).resolve().parents[N]`.

---

### Report Card

| Metric | Grade | Notes |
|--------|-------|-------|
| AnyIO Compliance | C | `run.py`, `loop.py`, `soul_updater.py`, `checkpoint.py`, `distiller.py`, `convergence.py` all compliant. `review_queue.py` and `metrics.py` use blocking I/O in async context — violations. `soul_update_manager.py` is AnyIO-correct but unused. |
| Tier Contract Correctness | C | L1/L2 data-passing works in automated pipeline. L3 output discarded. Improvement brief loop not implemented. Tier role definitions (mode files) contradict automated pipeline prompts. |
| Firewall Fix Completion | D | `config/distiller_prompts.yaml` missing (404). `soul_updater.py` retains hardcoded entity map. No `EntityRegistry` reference found anywhere. Two of two mandated fixes are incomplete. |
| Sub-Facet Identity | D | Three soul files present and structured. All metrics at zero. No write path from automated pipeline. `SoulUpdateManager` unused. `sub_facet` absent from all observability. |
| Convergence Logic | B | Four stopping conditions are sound and cover the main cases. Depth ceiling prevents infinite loops. Fragility on `"inconclusive"` signal bias is a minor design issue, not a showstopper. Human review queue is wired correctly. |
| Scheduler & Queue | C | Queue logic is correct. `_grow_frontier()` is implemented and functional (not a TODO). Critical bug: `RotationState` not persisted, scheduler resets every run. `research_topics.yaml` is a stub. |
| Credit Budget | B | Per-provider budgets, emergency reserves, monthly reset, and provider selection logic are well-implemented. Daily limits defined but not enforced. `select_search_provider()` not wired to search path in `loop.py`. |
| Checkpoint & Recovery | B | Atomic writes, correct state coverage, crash recovery via `_grow_frontier()` checkpoint scan. `cleanup_old()` never called. Path relativity issue. `_get_next_task()` defined but unused. |
| Training Triple Generation | A | Every cycle saves (T1, T2, T3) triple to `data/datasets/synthetic/`. Metadata is rich. Clean save structure. The best-functioning autonomous output in the pipeline. |
| Autonomous Operation | D | System can run without supervision for search and distillation. But sub-facets never self-improve, rotation never advances, improvement briefs are never written, and T3 review is silently discarded. The engine cannot learn from its own output. |

---

### Strategic Recommendations (Top 3)

**1. Wire the improvement brief loop — this is the entire self-improvement mechanism.**
`SoulUpdateManager` is already written and correct. The missing work is: (a) after T3 produces its review JSON, parse `recommended_directions` and enqueue high-priority follow-ups; (b) parse T3's `corrections` and write them as lessons to `data/entities/jem/souls/editor.yaml`; (c) have `loop.py` or `distiller.py` call `SoulUpdateManager` to write the improvement brief items from T2 output to `initiate.yaml` and from T3 output to both `initiate.yaml` and `analyst.yaml`; (d) increment `metrics.sessions_completed` and `soul_power` on each sub-facet's soul file. Without this, Jem cannot accumulate operating experience — the "the correction delta is the training signal" lesson in `soul.yaml` is written but not lived.

**2. Persist `RotationState` and populate `research_topics.yaml` with real content.**
These two fixes together make the scheduler functional. `RotationState` should serialize to `data/research/scheduler_state.json` at the end of `get_next_topic()` and reload in `__init__`. `research_topics.yaml` should be populated with the engine's actual strategic research agenda (AI model releases, AnyIO patterns, MCP protocol updates, sovereign hardware optimization, etc.) — the fallback topics in `_grow_frontier()` are a good starting point. Until both are done, the scheduler is decorative.

**3. Move all prompts to `config/distiller_prompts.yaml` and apply T3 output to the GnosisPacket.**
Two changes with high leverage: First, extract `SYSTEM_PROMPTS` and `DISTILLATION_PROMPT_TEMPLATE` from `distiller.py` into `config/distiller_prompts.yaml`, loaded at init via PyYAML. This completes the firewall fix and makes prompt iteration possible without code deployment. Second, after `GeminiBackend.call()` returns, parse the T3 review JSON and apply corrections to `gnosis.distillations` before returning the `GnosisPacket` — at minimum, have T3's `recommended_directions` (priority ≥ 0.8) feed into `_enqueue_adjacent()`. This makes the Editor tier produce actual downstream value rather than writing exclusively to the training dataset.

---

*`trc_review_jem` — Review complete. The pipeline can search, distill, and checkpoint reliably. The autonomous learning loop — the reason Jem 2.0 was built — is architecturally present but not functionally closed. The three recommendations above, in order, are the path to closing it.*
