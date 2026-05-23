# 🔱 Jem Phase 2 — Scheduling & Rotation: Comprehensive Research Brief
⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_jem_ph2_rsch ⬡ RESEARCH-BRIEF

**AP Token**: `AP-PHASE2-RESEARCH-v1.0.0`
**Date**: 2026-05-19
**Status**: ✅ COMPLETE — All Phase 2 components researched, enhanced, and ready for implementation

---

## §0 Executive Summary

Phase 2 transforms the background researcher from a single-cycle execution into a **self-scheduling research intelligence** with topic rotation, priority management, review queuing, and cycle-level observability. The research below covers every component with best practices from industry, academia, and production-tested patterns.

**11 enhancement opportunities** were discovered beyond the original 5 tasks. Key upgrades:
- Multi-tier priority queue instead of single heap (prevents starvation)
- File-based cycle lock instead of in-memory bool (crash-safe)
- Aging mechanism for scheduled topics (prevents dominance)
- WatchdogSec + RuntimeMaxSec in systemd service (crash containment)
- Discovery-first local scan integrated into topic rotation (zero-cost enrichment before cloud spend)
- Triage upgrade to use Qwen3-4B-Thinking via lmster (model-based, not heuristic)
- Semantic deduplication for frontier growth (not just exact string match)
- Metrics + backlog → periodic review queue processing (every 10 cycles, not just "when main queue empty")

---

## §1 Systemd Timer & Service Best Practices (Task 2.1)

### Researched Patterns

| Source | Key Insight | Applied to Omega |
|--------|-------------|------------------|
| freedesktop.org systemd.timer(5) | `OnUnitActiveSec=20min` for relative interval; `Persistent=true` catches missed runs; `RandomizedDelaySec` prevents thundering herd | ✅ Timer: OnUnitActiveSec=20min, Persistent=true, RandomizedDelaySec=3min |
| SUSE Enterprise Server 15 SP7 | Monotonic timers (event-based) vs calendar-based; `OnBootSec` for initial delay | ✅ OnBootSec=5min ensures lmster/SearXNG ready |
| RHEL 9 migration guide | `AccuracySec=1min` for power coalescing while maintaining timing | ✅ AccuracySec=1min |
| Linux workaround: service on every boot | Remove `Requires=` from timer [Unit] — implicit Before= dependency | ✅ Timer has NO Requires= (implicit by .timer→.service naming) |
| Production worker best practices (Lorbic) | `Restart=on-failure`, `RestartSec=30s`, `TimeoutStartSec` | ✅ Already configured; add `RuntimeMaxSec=600` |
| Watchdog pattern | `WatchdogSec=120s` detects frozen processes | 🔲 Add to Phase 2 |
| Failure action pattern | `FailureAction=notify` on critical circuit breaker | 🔲 Add to Phase 2 |

### Recommended Timer Config

```ini
[Unit]
Description=Omega Background Researcher — 20-Minute Research Cycle
Documentation=https://github.com/Xoe-NovAi/omega-engine

[Timer]
OnBootSec=5min
OnUnitActiveSec=20min
RandomizedDelaySec=3min
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
```

### Recommended Service Enhancements

```ini
[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-engine/.venv/bin/python3 -m omega.workers.background_researcher.run
WorkingDirectory=%h/Documents/Xoe-NovAi/omega-engine
Environment=PYTHONPATH=%h/Documents/Xoe-NovAi/omega-engine/src
EnvironmentFile=%h/Documents/Xoe-NovAi/omega-engine/.env
Environment=OMEGA_ENV=production
StandardOutput=journal
StandardError=journal

# Memory protection
MemoryMax=512M
MemoryHigh=384M

# Timeout — single cycle should never exceed 10 minutes
RuntimeMaxSec=600
TimeoutStartSec=120

# Auto-restart on failure
Restart=on-failure
RestartSec=30s

# Watchdog — if no heartbeat for 2 minutes, kill and restart
WatchdogSec=120

# Security
ProtectSystem=full
ReadWritePaths=%h/Documents/Xoe-NovAi/omega-engine/data %h/Documents/Xoe-NovAi/omega-engine/docs
PrivateTmp=yes
NoNewPrivileges=yes
```

### Key Design Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| `Type=oneshot` NOT `Type=simple` | Task completes, exits. Not a daemon. | freedesktop.org |
| `Restart=on-failure` NOT `always` | If cycle succeeds normally, don't restart (would re-run immediately) | OneUpTime guide |
| `RuntimeMaxSec=600` | 20-min timer with 10-min max runtime leaves 10-min headroom | Production worker pattern |
| `WatchdogSec=120` | If lmster hangs or subprocess deadlocks, systemd detects within 2 min | Lorbic worker best practices |
| `Persistent=true` | If system was off during a cycle window, runs catch-up immediately | SUSE doc, RHEL migration |
| `RandomizedDelaySec=3min` | Spreads load across hosts in multi-instance deployment | freedesktop.org |
| `AccuracySec=1min` | Allows systemd to coalesce wake-ups for power efficiency | freedesktop.org |

---

## §2 Topic Schedule & Rotation Metadata (Task 2.2 — config/research_topics.yaml)

### Enhanced Schema Design

Building on the basic 3-topic structure from the Grand Strategy, each topic needs rich metadata for the scheduler:

```yaml
# config/research_topics.yaml
version: 2
created: 2026-05-19

rotation:
  strategy: round_robin  # round_robin | weighted | adaptive
  cycle_order: [voice_to_voice, local_inference, research_management]
  aging_decay_per_cycle: 0.85  # priority multiplier per N-th cycle on same topic
  deepening_factor: 1.15       # priority boost when depth increases
  max_consecutive: 2           # never schedule same topic twice in a row
  priority_floor: 0.3          # min priority a topic can decay to

scheduled_topics:
  voice_to_voice:
    title: "Voice-to-Voice Integration in Omega Engine"
    prompt_mode: technical
    end_goal: "Implementation roadmap for real-time voice-to-voice pipeline using Iris container + Whisper STT + Piper/TTS + Gemma response synthesis"
    local_search:
      dirs:
        - "src/omega/iris/"
        - "xna-omega-legacy/**/*voice*"
        - "omega-stack-legacy/**/*voice*"
      patterns:
        - "*voice*"
        - "*nova*"
        - "*stt*"
        - "*tts*"
        - "*whisper*"
        - "*piper*"
        - "*speech*"
    cloud_search:
      primary_prompt: "What are the best open-source voice-to-voice AI architectures in 2026?"
      depth: 2
    convergence:
      max_iterations: 12
      goal: "implementation_roadmap"
      success_criteria:
        - "All subtopics reach convergence"
        - "Implementation roadmap with dependencies generated"
        - "At least 3 verified sources per major claim"

  local_inference:
    title: "Custom Omega llama-cpp-python Local Inference Engine"
    prompt_mode: technical
    end_goal: "Implementation roadmap for hardened, Zen 2-optimized local inference engine (NativeGGUFProvider)"
    local_search:
      dirs:
        - "src/omega/oracle/providers.py"
        - "src/omega/oracle/model_gateway.py"
        - "config/models.yaml"
        - "xna-omega-legacy/.venv/llama_cpp/"
        - "omega-stack-legacy/**/*infer*"
      patterns:
        - "*llama*"
        - "*gguf*"
        - "*infer*"
        - "*native*"
        - "*provider*"
        - "*backend*"
    cloud_search:
      primary_prompt: "What are the latest llama-cpp-python GGUF optimization techniques for Zen 2 (AVX2) in 2026?"
      depth: 2
    convergence:
      max_iterations: 10
      goal: "implementation_roadmap"
      success_criteria:
        - "NativeGGUFProvider fully specified"
        - "KV cache configuration finalized"
        - "Performance benchmarks against lmster"

  research_management:
    title: "Research Management & Organization Systems Improvement"
    prompt_mode: default
    end_goal: "Implementation roadmap for self-organizing research knowledge base with auto-categorization, gap detection, and cross-referencing"
    local_search:
      dirs:
        - "docs/research/"
        - "docs/research/omni/"
        - "docs/operations/"
        - "data/research/"
      patterns:
        - "INDEX.md"
        - "*research*"
        - "*queue*"
        - "*discovery*"
        - "R_AUTO_*"
    cloud_search:
      primary_prompt: "What are the best practices for self-organizing research knowledge bases in AI systems 2026?"
      depth: 2
    convergence:
      max_iterations: 10
      goal: "implementation_roadmap"
      success_criteria:
        - "Auto-categorization system designed"
        - "Gap detection heuristic validated"
        - "Cross-referencing pipeline specified"
```

### Key Design Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| `aging_decay_per_cycle: 0.85` | After 4 consecutive cycles on same topic, priority halves (0.85^4 ≈ 0.52). Prevents topic from dominating. | CPU scheduling: priority aging (IEEE paper) |
| `deepening_factor: 1.15` | Going deeper on a topic gets slight priority boost — proven valuable content deserves more cycles | Adaptive RR scheduling research |
| `priority_floor: 0.3` | Never let a topic fall below this — ensures all topics eventually get their turn | Starvation prevention (OS scheduling) |
| `max_consecutive: 2` | Same topic never runs 3 times in a row, even if high priority | Round-robin fairness |
| `convergence.max_iterations` | Topic that isn't converging after this many cycles goes dormant | Engineering best practice |
| `success_criteria` | Explicit definition of "done" prevents infinite deepening spiral | Strategy requirement |

---

## §3 Topic Rotation Engine (Task 2.3 — TopicScheduler)

### Architecture

The TopicScheduler is a new component in `src/omega/workers/background_researcher/scheduler.py`. It manages:
1. Round-robin cycle ordering with aging
2. Rotation state persistence (`data/research/rotation_state.json`)
3. Integration with the existing PriorityQueue
4. Discovery-first local scan before cloud search for each topic

### Algorithm: Weighted Round-Robin with Aging

```
Every cycle:
  1. Load rotation state from rotation_state.json
  2. Get current scheduled topic (cycle_order[cycles_completed % len(cycle_order)])
  3. Compute topic priority:
       base = 0.9 (scheduled topics get high base)
       decayed = base * aging_decay_per_cycle^times_on_topic
       boosted = decayed * deepening_depth_factor
       final = max(boosted, priority_floor)
  4. Check convergence:
       If topic has been processed N times AND not approaching convergence:
         → Set priority to 0.1 (leaves room for frontier gaps but stays in rotation)
       If topic has reached success_criteria:
         → Remove from schedule, replace with next topic in pipeline
  5. If topic priority > 0.3, enqueue at computed priority
  6. Increment rotation counter
  7. Save rotation state

After main pipeline execution:
  8. Post-process: update rotation_state with results
     - Did the topic produce valuable output?
     - Did the topic deepen (depth increased)?
     - How close to convergence?
```

### Rotation State JSON (`data/research/rotation_state.json`)

```json
{
  "version": 2,
  "current_index": 0,
  "cycles_completed": 47,
  "last_cycle_id": "cycle_20260519_123000_48",
  "topic_states": {
    "voice_to_voice": {
      "times_processed": 16,
      "current_depth": 1.0,
      "last_cycle_id": "cycle_20260519_113000_45",
      "last_cycle_at": "2026-05-19T11:30:00Z",
      "total_cycles": 16,
      "convergence_score": 0.45,
      "convergence_subtopics_done": 2,
      "convergence_subtopics_total": 7,
      "current_iteration_type": "deep_dive"
    },
    "local_inference": {
      "times_processed": 15,
      "current_depth": 1.0,
      "last_cycle_id": "cycle_20260519_115000_46",
      "last_cycle_at": "2026-05-19T11:50:00Z",
      "total_cycles": 15,
      "convergence_score": 0.30,
      "convergence_subtopics_done": 1,
      "convergence_subtopics_total": 7,
      "current_iteration_type": "surface_survey"
    },
    "research_management": {
      "times_processed": 16,
      "current_depth": 1.0,
      "last_cycle_id": "cycle_20260519_121000_47",
      "last_cycle_at": "2026-05-19T12:10:00Z",
      "total_cycles": 16,
      "convergence_score": 0.50,
      "convergence_subtopics_done": 3,
      "convergence_subtopics_total": 6,
      "current_iteration_type": "deep_dive"
    }
  },
  "total_training_triples": 47
}
```

### Integration with PriorityQueue

The TopicScheduler does NOT replace the PriorityQueue — it feeds it:

```python
async def _get_next_task(self) -> Optional[ResearchTask]:
    """Enhanced: inject scheduled topic, then check priority queue."""
    # Step 1: Inject current scheduled topic at high priority
    scheduled = await self.topic_scheduler.get_current_topic()
    if scheduled:
        task = self.queue.enqueue(
            topic=scheduled.title,
            base_priority=scheduled.priority,
            current_depth=scheduled.current_depth,
            scheduled_topic=True,  # new flag in ResearchTask
            prompt_mode=scheduled.prompt_mode,
        )
        logger.info(f"Scheduled topic injected: '{scheduled.title}' (p={scheduled.priority:.2f})")

    # Step 2: Dequeue highest priority task
    task = self.queue.dequeue()
    if not task:
        pending = await self.checkpoint.load_all_pending()
        if pending:
            pending.sort(key=lambda t: t.priority, reverse=True)
            return pending[0]
    return task
```

### Key Design Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| TopicScheduler feeds PriorityQueue, not replaces it | Preserves flexibility: urgent user requests still get priority 3.0× boost | Priority queue pattern |
| State persistence via JSON (not in-memory) | Survives system crash, timer restart, or machine reboot | Distributed queueing research |
| Convergence scoring | Prevents infinite cycles on a topic that's already "done" | Strategy requirement |
| Iteration type tracking | Surface survey → deep dive → prototype/impl → consolidate → done | Deepening spiral model |
| Aging prevents dominance | No single topic can starve others even if high-value | OS scheduling starvation prevention |

### Enhancement: Triage Upgrade (Discovered)

**Current issue**: `_triage()` is pure heuristic (keyword matching on topic string). The strategy doc (loop.py line 237) explicitly notes "will upgrade to model-based triage in a future iteration."

**Research finding**: Qwen3-4B-Thinking is already loaded in lmster on :1234. It can do triage in under 5 seconds — cheaper and more accurate than heuristic.

**Recommendation**: Add model-based triage as optional mode in Phase 2:

```python
async def _triage_model_based(self, task: ResearchTask) -> TriageResult:
    """Fast triage via Qwen3-4B-Thinking — better than heuristic."""
    prompt = f"""Assess this research topic for value and depth needed:
Topic: {task.topic}
Respond with JSON: {{"score": 0.0-1.0, "depth_plan": 1-3, "reason": "...", "skip": true/false}}"""
    try:
        resp = await self.lmster_backend.call(prompt, temperature=0.1)
        return TriageResult.from_json(resp)
    except Exception:
        return self._triage_heuristic(task)  # fallback
```

---

## §4 Review Queue System (Task 2.4)

### Architecture: 3-Tier Filesystem Queue

Based on research of Redis priority queues, RQ deferred job registries, and Celery latency-based queueing:

```
data/research/review_queue/
├── high/                    # T3 items with priority ≥ 0.7
│   └── {topic_slug}_{date}_{cycle_id}.json
├── normal/                  # T3 items with priority 0.4-0.7
│   └── {topic_slug}_{date}_{cycle_id}.json
└── low/                     # T3 items with priority < 0.4
    └── {topic_slug}_{date}_{cycle_id}.json

processed/                   # Completed review items (for training data)
ttl_sweep.json               # Last sweep timestamp for performance
```

### Item Schema

```json
{
  "topic": "Recommended follow-up topic",
  "reason": "why this direction matters",
  "priority": 0.85,
  "depth": 2,
  "prompt_mode": "technical",
  "source_cycle_id": "cycle_20260519_123000_48",
  "source_topic": "Voice-to-Voice Integration",
  "created_at": "2026-05-19T12:30:00Z",
  "ttl_days": 7,
  "expires_at": "2026-05-26T12:30:00Z",
  "status": "pending",
  "processed_at": null
}
```

### Processing Rules

| Rule | Threshold | Implementation |
|------|-----------|----------------|
| **Priority tiers** | High ≥ 0.7, Normal 0.4-0.7, Low < 0.4 | 3-folder filesystem for O(1) peek |
| **TTL expiration** | 7 days default; Low priority → 2 days | Background sweep at cycle start |
| **Hard cap** | 100 items total | Oldest 10 auto-expire when cap hit |
| **Processing frequency** | Every 10 research cycles | Process up to 1 item per run |
| **Post-processing** | Processed items → `processed/` with timestamp | Training data for future iterations |
| **Locking** | File-based lock (`{item}.lock`) | Prevents concurrent processing |

### ReviewQueueProcessor Algorithm

```python
async def process_review_queue(self) -> Optional[str]:
    """Process the highest-priority unexpired review item.
    
    Returns the topic of the processed item, or None if nothing to process.
    """
    # Step 1: Sweep expired items
    self._sweep_expired()
    
    # Step 2: Get highest priority item (check high → normal → low)
    item = self._get_next_review_item()
    if not item:
        return None
    
    # Step 3: Acquire lock (atomic mkdir)
    lock_path = self.queue_dir / "locks" / f"{item['topic'][:30]}.lock"
    try:
        os.mkdir(lock_path)  # atomic on Linux
    except FileExistsError:
        return None  # being processed by concurrent run
    
    try:
        # Step 4: Enqueue as a research task
        topic = item["topic"]
        self.parent_queue.enqueue(
            topic=topic,
            base_priority=item["priority"],
            current_depth=item.get("depth", 2),
            user_requested=False,
            scheduled_topic=False,
        )
        logger.info(f"Review queue → research queue: '{topic}'")
        
        # Step 5: Mark processed
        self._mark_processed(item)
        return topic
    finally:
        # Step 6: Release lock
        try:
            os.rmdir(lock_path)
        except OSError:
            pass
```

### Comparison: Filesystem vs Redis vs Database

| Criterion | Filesystem (Chosen) | Redis | SQLite |
|-----------|---------------------|-------|--------|
| Crash survival | ✅ Atomic mkdir + rename | ⚠️ Depends on AOF/RDB | ✅ WAL mode |
| No external deps | ✅ Zero | ❌ Requires Redis container | ⚠️ Requires aiosqlite |
| O(1) peek by priority | ✅ 3-tier dirs | ✅ Sorted set | ❌ Requires query |
| TTL sweep | ✅ Stat-based | ✅ TTL keys | ✅ Query |
| Locking | ✅ Atomic mkdir | ❌ Must implement | ✅ BEGIN IMMEDIATE |
| Complexity | Low | Medium | Medium |

**Verdict**: Filesystem wins for Phase 2 — zero new infrastructure, atomic operations on Linux, and the 100-item cap keeps things manageable. Can upgrade to Redis in Phase 4+ when volume grows.

---

## §5 Tier-Level Metrics Collection (Task 2.5)

### Metrics Schema

Every cycle produces one line in `data/research/metrics.jsonl`:

```json
{
  "version": 2,
  "cycle_id": "cycle_20260519_123000_48",
  "topic": "Voice-to-Voice Integration in Omega Engine",
  "depth": 1.0,
  "triage_score": 0.78,
  "triage_method": "model",
  "sources_found": 12,
  "sources_providers": ["searxng", "tavily"],
  
  "tier1": {
    "success": true,
    "latency_ms": 4230,
    "tokens_in": 520,
    "tokens_out": 387,
    "reasoning_tokens": 180,
    "quality_gate_passed": true,
    "quality_gate_tokens": 387,
    "model": "qwen3-4b-thinking"
  },
  "tier2": {
    "success": true,
    "latency_ms": 12540,
    "provider": "openrouter",
    "model": "minimax-m2.5",
    "fallback_chain_used": false,
    "enrichment_delta": "medium"
  },
  "tier3": {
    "success": true,
    "latency_ms": 8340,
    "method": "cli",
    "model": "gemini-2.5-flash",
    "corrections_count": 2,
    "reviewed_directions": 1,
    "confidence_l1": 0.85,
    "confidence_l2": 0.70,
    "confidence_l3": 0.65,
    "overall_quality": "good"
  },
  
  "circuit_breakers": {
    "lmster": {"state": "closed", "failures": 0},
    "minimax_openrouter": {"state": "closed", "failures": 0},
    "minimax_zen": {"state": "closed", "failures": 0},
    "gemma_google": {"state": "closed", "failures": 0},
    "gemini_cli": {"state": "closed", "failures": 0}
  },
  
  "training_triple_saved": true,
  "training_triple_path": "data/datasets/synthetic/20260519_voice_to_voice/cycle_48/",
  
  "soul_update_written": true,
  "converged": false,
  "recommendation": "write_to_soul",
  
  "timestamp": "2026-05-19T12:30:00Z",
  "elapsed_since_last_cycle_s": 1200
}
```

### Metrics Dashboard (For `omega health` CLI)

Using the JSONL data, the CLI can display:

```text
═══ Jem Research Metrics ═══

Last 24 hours:
  Cycles completed: 63/72 (87.5%)
  Avg cycle time: 4m23s
  Training triples: 63
  Quality gate pass rate: 100%
  Convergence rate: 12.7%

Tier Health (24h window):
  T1 (Qwen3-4B):     ✅ 100%     Avg 4.2s   0 failures
  T2 (MiniMax OR):   ✅ 93.7%    Avg 12.5s  4 failures (all 429)
  T2 (MiniMax Zen):  ⚠️ Not used (OR primary)
  T2 (Gemma):        ⚠️ Not used (MiniMax primary)
  T3 (Gemini Flash): ✅ 96.8%    Avg 8.3s   2 failures

Review Queue: 12 items (3 high, 7 normal, 2 low)
Synthetic Dataset: 63 triples (1.2MB)
```

### Metrics Janitor

```python
async def janitorial_sweep(self):
    """Archive metrics > 30 days to cold storage."""
    archive_dir = self.metrics_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now(timezone.utc).timestamp() - (30 * 86400)
    
    for path in Path(self.metrics_dir).glob("*.jsonl"):
        if path.stat().st_mtime < cutoff:
            archive_path = archive_dir / path.name
            await anyio.Path(path).rename(archive_path)
            logger.info(f"Archived metrics: {path.name} → archive/")
```

---

## §6 Priority Queue Enhancements (Discovered Enhancement)

### Current Limitation

The existing `PriorityQueue` is a single max-heap. Research shows this has two problems:
1. **Starvation**: Low-priority items may never be dequeued if high-priority items keep arriving
2. **No fairness**: A user-requested item (3.0× multiplier) can block everything for days

### Recommended: Two-Tier Queue with Weighted Fair Scheduling

```python
class EnhancedPriorityQueue:
    """Two-tier priority queue with fairness guarantees.
    
    High-priority queue: user requests, scheduled topics (strict priority)
    Normal queue: frontier gaps, review items, deferred tasks (weighted fair)
    """
    
    def __init__(self):
        self._high: list[tuple[float, int, ResearchTask]] = []  # strict priority
        self._normal: list[tuple[float, int, ResearchTask]] = []  # weighted fair
        self._fairness_counter = 0  # ensures normal queue gets at least 1/3 of cycles
    
    def enqueue(self, ...):
        if user_requested or scheduled_topic:
            heapq.heappush(self._high, ...)
        else:
            heapq.heappush(self._normal, ...)
    
    def dequeue(self) -> Optional[ResearchTask]:
        """Fair dequeue: 2 high : 1 normal ratio, preventing starvation."""
        self._fairness_counter += 1
        if self._high and (self._fairness_counter % 3 != 0 or not self._normal):
            return heapq.heappop(self._high)[2]
        elif self._normal:
            return heapq.heappop(self._normal)[2]
        elif self._high:
            return heapq.heappop(self._high)[2]
        return None
```

---

## §7 Discovery-First Local Scan (Phase 3 Prep — Researched Now)

### Pattern: Local First, Cloud Second

The research shows a clear best practice: **scan local files before querying cloud APIs**. Multiple production systems use this pattern:

| System | Pattern | Apply to Jem |
|--------|---------|-------------|
| DeepDoc (Quansight) | Local PDF → embeddings → RAG before web | Each topic's `local_search.dirs` scanned first |
| File Brain | Real-time file system indexing | Use `glob` + `grep` patterns from `research_topics.yaml` |
| Hybrid AI Architecture (LiteLLM) | Route 85-95% local, 5-15% cloud | TopicScheduler does local scan first, then enriches via cloud |
| AssemblyZero | JSONL telemetry buffer before remote flush | Metrics accumulate locally, shipped on next cycle |

### Discovery-First Algorithm

```python
async def _discovery_first(self, topic_config: TopicConfig) -> Optional[str]:
    """Scan local files for patterns before making cloud API calls.
    
    1. Glob the topic's configured search dirs for pattern matches
    2. Grep matching files for content related to the topic
    3. Summarize findings (up to 3000 chars)
    4. Return as enrichment context for T2 cloud call
    """
    content_chunks = []
    
    for search_dir in topic_config.local_search.dirs:
        expanded = Path(search_dir).expanduser()
        if not expanded.exists():
            continue
        for pattern in topic_config.local_search.patterns:
            for path in expanded.glob(f"**/{pattern}"):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    # Extract relevant section (first 500 chars around keyword)
                    for keyword in topic_config.topic.lower().split()[:3]:
                        idx = text.lower().find(keyword)
                        if idx >= 0:
                            start = max(0, idx - 200)
                            end = min(len(text), idx + 500)
                            snippet = text[start:end]
                            content_chunks.append(f"#[{path.relative_to(project_root)}]\n{snippet}")
                            break
                except (IOError, OSError):
                    continue
    
    if content_chunks:
        summary = "\n\n---\n\n".join(content_chunks[:10])
        return f"[LOCAL DISCOVERY from {len(content_chunks)} files]\n{summary[:3000]}"
    return None
```

---

## §8 Strategy Enhancement Opportunities — 11 Findings

During this research, 11 enhancement opportunities were identified beyond the original Phase 2 scope:

| # | Opportunity | Phase | Impact | Effort |
|---|-------------|-------|--------|--------|
| 1 | Multi-tier priority queue (high/normal) | 2.3 | Prevents starvations; fairness guarantee | +30min |
| 2 | File-based cycle lock (not in-memory bool) | 2.3 | Crash-safe cycle protection | +15min |
| 3 | Aging mechanism for topic priority decay | 2.3 | Prevents topic dominance | +15min |
| 4 | WatchdogSec + RuntimeMaxSec in systemd | 2.1 | Crash containment; freeze detection | +5min |
| 5 | Triage upgrade to Qwen3-4B model-based | 2.3 | Better topic scoring than heuristic | +45min |
| 6 | Semantic deduplication for frontier growth | 2.3 | Reduces redundant research topics | +30min |
| 7 | Review queue processor (not just "when empty") | 2.4 | Periodic processing every 10 cycles | +20min |
| 8 | Metrics janitorial sweep (30-day archive) | 2.5 | Prevents metrics directory bloat | +15min |
| 9 | Discovery-first local scan integrated into rotation | 3.1 prep | Zero-cost enrichment before cloud spend | Already in scope |
| 10 | Watchdog-based failure notifications | 2.1 | Systemd-level alert on crash | +10min |
| 11 | Training triple count tracked in metrics | 2.5 | Dataset growth visibility | +5min |

---

## §9 Implementation Order & Dependencies

```
Phase 2 Implementation Order:

Task 2.1 (Timer: 20min)          ← No deps
  ↓
Task 2.2 (config/research_topics.yaml)  ← Must exist before TopicScheduler
  ↓
Task 2.3a: EnhancedPriorityQueue    ← Must exist before TopicScheduler
  ↓
Task 2.3b: TopicScheduler + rotation_state.json  ← Depends on 2.2 + 2.3a
  ↓
Task 2.4: ReviewQueueSystem    ← Independent of scheduler (runs on 10-cycle counter)
  ↓
Task 2.5: Metrics collection     ← Depends on 2.3b (needs rotation data)
  │
  └── Enhancement: Metrics janitor
```

---

## §10 Sources

| Area | Source Type | Reference |
|------|-------------|-----------|
| systemd timers | freedesktop.org | `systemd.timer(5)` — OnUnitActiveSec, Persistent, RandomizedDelaySec, AccuracySec |
| systemd production use | OneUpTime / SUSE / RHEL guides 2025-2026 | WatchdogSec, RuntimeMaxSec, FailureAction, Type=oneshot patterns |
| Priority + round-robin scheduling | IEEE papers (2018-2022) | MPPBRRACBDQ, aging mechanisms, starvation prevention |
| Priority queue patterns | Azure / AWS architecture guides 2025-2026 | Multi-queue priority, BLPOP pattern, weighted fair scheduling |
| Background workers production | Lorbic 2026 / TheLinuxCode 2026 | Bounded concurrency, TTL for deferred jobs, graceful shutdown |
| Review queue with TTL | RQ (rq/rq#1685, #2111) | Deferred job TTL, expired job cleanup, registry patterns |
| ML pipeline observability | OneUpTime / MLflow / OTEL 2026 | Structured JSONL, tiered storage, trace ID linking |
| Local-first discovery | Quansight DeepDoc / Local AI Master 2026 | Local scan → RAG → cloud enrich pattern |
| Hybrid routing | Local AI Master 2026 / LiteLLM | 85-95% local, route by complexity, circuit breakers |
| File-based atomic locking | POSIX standard | `mkdir` atomicity, `rename` atomicity on same filesystem |
