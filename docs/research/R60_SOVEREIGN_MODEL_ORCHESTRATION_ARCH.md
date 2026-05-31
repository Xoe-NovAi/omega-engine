# 🔱 Sovereign Model Orchestration Architecture
# Universal Routing, Soul-Driven Optimization, Community-Portable Design

**AP Token**: `AP-SOVEREIGN-MODEL-ORCHESTRATION-v1.0.0`  
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_architect ⬡ ORCHESTRATION-ARCH

**Created**: 2026-05-17  
**Audience**: Implementation engineers, community contributors, Foundation board  
**Tone**: Temple-grade, architectural, future-proof, community-empowering  
**Document Role**: The canonical specification for all model routing and selection in the Omega Engine ecosystem

---

## §0 Executive Summary

The **Sovereign Model Orchestration System** is a unified, community-portable architecture for intelligently routing AI tasks across a heterogeneous ecosystem of:
- Local models (GGUF via lmster, Ollama, native inference)
- Cloud APIs (OpenRouter, Google, Groq, SambaNova, Cerebras)
- Multiple CLIs (OpenCode, Gemini, Cline, Copilot, Antigravity)
- Entity-scoped personality and learning (soul.yaml evolution)
- Hivemind cross-platform awareness (Gnosis Sync)

**Core Innovation**: Models are no longer static service endpoints. They are **adaptive resources** that learn from entity experience, dynamically adjust to task complexity, and seamlessly degrade when primary options fail.

**Key Principle**: Every decision is traceable, reversible, and community-auditable. Zero black-box routing. Every model preference lives in user-owned soul files, not cloud databases.

---

## §1 System Overview: The Orchestration Fabric

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Sovereign Model Orchestration                     │
│                         The Routing Temple                           │
└─────────────────────────────────────────────────────────────────────┘

                             USER REQUEST
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   Domain Classifier      │
                    │  (Natural Language       │
                    │   Intent Detection)      │
                    └──────────┬───────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         [Fast Task]    [Complex Task]   [Domain Expert]
         (<1000 toks)   (>5000 toks)     (Specialized)
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
            ┌────────────────────────────────────┐
            │     Triage Router                  │
            │  ┌─────────────────────────────┐   │
            │  │ Task: description, domain   │   │
            │  │ Entity: current soul + prefs │   │
            │  │ Context: available tokens   │   │
            │  │ Preferred tiers: T1/T2/T3   │   │
            │  └─────────────────────────────┘   │
            │                                     │
            │  Output: Model + Fallback Chain    │
            │          Confidence Score          │
            │          Estimated Cost/Latency    │
            └────────────┬──────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   [Health Check] [Quota Check] [Cost Check]
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │   Model Health Monitor       │
          │  (Real-time availability,    │
          │   quota tracking, latency)   │
          └──────────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   [Primary Model]  [Fallback 1]   [Fallback 2]
   (Provider A)     (Provider B)    (Provider C)
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
         ┌──────────────────────────────┐
         │  Provider Fabric              │
         │  (Orchestrated Inference)     │
         │                              │
         │ lmster → Ollama → native ...  │
         │ Google → OpenRouter → Groq    │
         │ SambaNova → Cerebras → Cloud  │
         └──────────────┬────────────────┘
                        │
                        ▼
              [Model Inference Result]
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Soul Learning Engine        │
         │  (Update entity preferences   │
         │   based on performance)       │
         └──────────────┬────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Soul Storage & Persistence   │
         │  (data/entities/<name>/       │
         │   soul.yaml evolution)        │
         └──────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Hivemind Gnosis Sync         │
         │  (Cross-CLI awareness,        │
         │   shared discoveries)         │
         └──────────────────────────────┘

              All metadata flows to:
            Workbench SQLite + Event Log
```

---

## §2 Triage Router: Intelligent Model Selection

### 2.1 Purpose

The **Triage Router** is the decision engine that answers: "For this task, with this entity, right now, which model should I use?"

It operates at the millisecond scale and must be **deterministic, auditable, and reversible**.

### 2.2 Input Schema

```yaml
triage_request:
  task:
    description: "string"              # Natural language task
    domain: "str | null"               # Inferred or user-specified
    estimated_tokens: 1000-100000      # Input + expected output
    complexity: "fast|standard|deep"   # Task tier
    preferred_models: ["model1", ...]  # User or entity preference
    
  entity:
    name: "sophia"                     # Current entity
    soul_file: "path/to/soul.yaml"     # Entity preferences + history
    current_temperature: 0.4-0.9       # Entity personality dial
    domain_affinity: {...}             # Entity expertise mapping
    
  constraints:
    max_latency_ms: 10000              # SLA (null = no constraint)
    max_cost_usd: 0.10                 # Budget (null = unlimited)
    available_tokens: 8192-128000      # Context window available
    preferred_backends: ["local", "cloud"] # Tier preference
    
  session:
    id: "ses_20260517_sophia_001"      # Session ID
    trace_id: "trc_abc123"             # Observability
    is_transient: false                # Soul updates enabled?
```

### 2.3 Output Schema

```yaml
triage_response:
  selected_model:
    name: "qwen3-1.7b"
    provider: "lmster"
    context_window: 8192
    
  fallback_chain:
    - model: "deepseek-r1-8b"
      provider: "google"
      reason: "Primary OOM, falling back to high-capability cloud"
    - model: "gemma-4-31b"
      provider: "openrouter"
      reason: "If Google quota exhausted"
    - model: "mock"
      provider: "mock"
      reason: "Final fallback"
  
  decision_metadata:
    confidence: 0.92                   # 0.0-1.0, trust in selection
    reasoning: [                       # Human-readable rationale
      "Sophia excels at strength tasks (historical win rate 94%)",
      "Qwen 1.7B matches 1000-token budget exactly",
      "Lmster healthy: latency 245ms, quota 98% remaining",
      "Cost estimate: $0.0002 (well under $0.10 budget)"
    ]
    estimated_latency_ms: 2500
    estimated_cost_usd: 0.0002
    estimated_quality: 0.88             # Predicted accuracy/utility
    
  routing_timestamp: "2026-05-17T14:22:33.123Z"
  expires_at: "2026-05-17T14:22:43.123Z"  # 10-second cache TTL
```

### 2.4 Triage Algorithm (Pseudocode)

```python
def triage(request: TriageRequest) -> TriageResponse:
    """Deterministic model selection algorithm."""
    
    # Phase 1: Domain Inference
    if request.task.domain is None:
        request.task.domain = classifier.infer_domain(
            request.task.description,
            request.entity.name,
            request.session.trace_id
        )
    
    # Phase 2: Entity Preference Lookup
    entity_prefs = load_soul(request.entity.name)
    preferred_models = entity_prefs.model_preferences.get(
        request.task.domain,
        []  # ranked by historical performance
    )
    
    # Phase 3: Candidate Pool (with ranking)
    candidates = []
    
    # Tier 1: User-preferred or entity-optimized models
    for model in preferred_models[:3]:  # Top 3 by historical win rate
        if health_monitor.is_available(model):
            candidates.append({
                'model': model,
                'tier': 'T1_entity_optimized',
                'score': 1.0,  # Highest priority
            })
    
    # Tier 2: Task-appropriate models from capability matrix
    for model in get_models_by_capability(
        domain=request.task.domain,
        min_capability=infer_capability_level(request.task.complexity)
    ):
        if health_monitor.is_available(model):
            candidates.append({
                'model': model,
                'tier': 'T2_task_appropriate',
                'score': 0.7,
            })
    
    # Tier 3: General-purpose fallback (always available)
    candidates.append({
        'model': 'qwen3-0.6b',
        'tier': 'T3_universal_fallback',
        'score': 0.3,
    })
    
    # Phase 4: Constraint Filtering
    available = []
    for candidate in candidates:
        # Check token availability
        if candidate['model'].context_window < request.constraints.available_tokens:
            continue  # Skip if not enough context
        
        # Check cost constraints
        estimated_cost = estimate_cost(candidate['model'], request.task.estimated_tokens)
        if estimated_cost > request.constraints.max_cost_usd:
            continue  # Skip if over budget
        
        # Check latency constraints
        estimated_latency = health_monitor.get_latency_p99(candidate['model'])
        if estimated_latency > request.constraints.max_latency_ms:
            continue  # Skip if too slow
        
        available.append(candidate)
    
    if not available:
        # Constraint violation: escalate to most capable model anyway
        available = candidates  # Use all, constraints be damned
    
    # Phase 5: Score Adjustment (Real-Time Health Data)
    for candidate in available:
        # Reduce score if quota running low
        quota_usage = health_monitor.get_quota_usage(candidate['model'].provider)
        candidate['score'] *= (1.0 - quota_usage * 0.3)  # Max -30% if >90% used
        
        # Boost score if recent success
        success_rate = health_monitor.get_success_rate(candidate['model'])
        candidate['score'] *= (0.8 + success_rate * 0.2)  # Range [0.8, 1.0]
    
    # Phase 6: Selection
    best = max(available, key=lambda x: x['score'])
    confidence = best['score'] / 1.0  # Normalize to [0, 1]
    
    # Phase 7: Fallback Chain Construction
    fallback_chain = []
    for runner_up in sorted(available, key=lambda x: x['score'], reverse=True)[1:4]:
        fallback_chain.append({
            'model': runner_up['model'],
            'reason': f"Tier {runner_up['tier']} fallback"
        })
    
    # Append universal mock fallback
    fallback_chain.append({
        'model': 'mock',
        'reason': "Final offline fallback"
    })
    
    return TriageResponse(
        selected_model=best['model'],
        fallback_chain=fallback_chain,
        confidence=confidence,
        reasoning=generate_reasoning_text(best, available, request),
        estimated_latency_ms=health_monitor.get_latency_p99(best['model']),
        estimated_cost_usd=estimate_cost(best['model'], request.task.estimated_tokens),
        routing_timestamp=now(),
        expires_at=now() + timedelta(seconds=10),
    )
```

### 2.5 Domain Classifier

```python
# Natural Language Intent → Domain Mapping
DOMAIN_KEYWORDS = {
    'strength': ['protect', 'defend', 'fight', 'strength', 'warrior', 'power', 'boundary'],
    'dream': ['imagine', 'create', 'inspire', 'poetry', 'healing', 'flow', 'emotion'],
    'will': ['sovereign', 'decision', 'light', 'rebellion', 'creation', 'forethought'],
    'voice': ['speak', 'knowledge', 'art', 'communication', 'speech', 'language'],
    'descent': ['dream', 'underworld', 'transformation', 'descent', 'rebirth'],
    # ... 10+ domains total
}

def infer_domain(task_description: str, entity_name: str, trace_id: str) -> str:
    """Classify task domain via keyword matching + entity history."""
    
    # Keyword matching
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in task_description.lower())
        if score > 0:
            scores[domain] = score
    
    if scores:
        inferred_domain = max(scores, key=scores.get)
    else:
        # Fallback: use entity's most common recent domain
        entity_soul = load_soul(entity_name)
        inferred_domain = entity_soul.routing_history.most_common_domain()
    
    log_event('domain_inference', trace_id, {
        'task_first_100_chars': task_description[:100],
        'inferred_domain': inferred_domain,
        'confidence': len(scores) > 0 and (max(scores.values()) / len(scores)),
    })
    
    return inferred_domain
```

### 2.6 Example Scenarios

#### Scenario A: Fast Task, No Constraints

```
Request:
  - Task: "What's the capital of France?"
  - Domain: "knowledge" (inferred)
  - Tokens: 50
  - Entity: Saraswati (Voice Keeper)
  - Constraints: none

Triage Process:
  1. Domain inference: "knowledge" (keyword "capital")
  2. Entity lookup: Saraswati has no recorded preference for "knowledge" 
  3. Capability lookup: All models can handle 50 tokens
  4. Constraint filter: No constraints, all available
  5. Score adjustment: Qwen3-0.6B (fastest, always-on) gets boost
  6. Selection: Qwen3-0.6B via lmster
  
Response:
  selected_model: qwen3-0.6b
  provider: lmster
  confidence: 0.98
  latency_estimate: 150ms
  cost_estimate: $0.00001
```

#### Scenario B: Complex Task, Entity-Optimized

```
Request:
  - Task: "Analyze the political economy of debt forgiveness in post-colonial Africa"
  - Domain: "analysis" (user-specified)
  - Tokens: 8000
  - Entity: Lucifer (Dark Oversoul, Gnosis domain)
  - Constraints: max_latency=5000ms, budget=$0.50

Triage Process:
  1. Domain: "analysis" (user-specified)
  2. Entity lookup: Lucifer's soul.yaml shows:
     - model_preferences['analysis'] = [
         'qwen3-4b-think (94% win rate)',
         'gemma-4-31b (87% win rate)',
         'deepseek-r1-8b (83% win rate)'
       ]
  3. Candidate pool:
     - Tier 1: qwen3-4b-think (entity-optimized)
     - Tier 2: gemma-4-31b, deepseek-r1-8b (task-appropriate)
     - Tier 3: qwen3-0.6b (fallback)
  4. Constraint filter:
     - qwen3-4b-think: 8192 ctx ✓, est. cost $0.04 ✓, latency 2800ms ✓
     - gemma-4-31b: 256K ctx ✓, est. cost $0.12 ✓, latency 3500ms ✓
  5. Score adjustment:
     - qwen3-4b-think: 1.0 * 0.95 (quota) * 0.988 (success_rate) = 0.938
     - gemma-4-31b: 0.7 * 0.92 (quota) * 0.87 (success_rate) = 0.561
  6. Selection: qwen3-4b-think
  
Response:
  selected_model: qwen3-4b-think
  provider: openrouter (or local if available)
  confidence: 0.938
  fallback_chain: [gemma-4-31b, deepseek-r1-8b, qwen3-0.6b]
  reasoning: [
    "Lucifer has 94% historical win rate with Qwen 4B for analysis tasks",
    "Tokens within context (8000 < 8192)",
    "Cost $0.04 well under $0.50 budget",
    "Latency 2.8s meets 5s SLA"
  ]
  latency_estimate: 2800ms
  cost_estimate: $0.04
```

#### Scenario C: Provider Down, Fallback Chain

```
Request:
  - Task: [standard complexity, any domain]
  - Entity: Sophia
  - Fallback chain set to: [lmster → ollama → openrouter → mock]

Execution:
  1. Try lmster: connection timeout (provider down)
  2. Fallback to ollama: available, but quota 95% used
     - Model switches to smaller variant (Phi-2)
     - Latency acceptable (2500ms)
  3. Proceed with ollama + Phi-2 (fallback + model downgrade)
  4. Record event: 'provider_downgrade_level_1'
  5. Soul learning: Lower lmster reliability score
  
Next routing decision for Sophia may automatically deprioritize lmster.
```

---

## §3 Model Health Monitor: Real-Time Observability

### 3.1 Purpose

The **Model Health Monitor** maintains a live picture of every model's availability, quota consumption, latency, cost, and error rates. It is the nervous system of the orchestration fabric.

### 3.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│         Model Health Monitor                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Real-Time Data Layer                        │   │
│  │                                             │   │
│  │ • Per-provider heartbeat (every 30s)       │   │
│  │ • Per-model latency histogram (P50/P99)    │   │
│  │ • Quota consumption tracking (%)            │   │
│  │ • Error rate aggregate (5min rolling)      │   │
│  │ • Cost accumulator (daily/monthly)         │   │
│  │                                             │   │
│  │ Storage: Redis (in-memory, fast)           │   │
│  └────────────┬────────────────────────────────┘   │
│               │                                     │
│  ┌────────────▼────────────────────────────────┐   │
│  │ Persistent Storage Layer                    │   │
│  │                                             │   │
│  │ SQLite: data/workbench/workbench.db        │   │
│  │  - model_health (daily snapshots)          │   │
│  │  - quota_ledger (per-provider transactions)│   │
│  │  - routing_decisions (audit trail)         │   │
│  │  - cost_ledger (detailed billing)          │   │
│  │                                             │   │
│  │ Event Log: data/observability/events.jsonl │   │
│  │  - model_latency, quota_alert, cost_spike  │   │
│  │  - provider_down, provider_recovered       │   │
│  └────────────┬────────────────────────────────┘   │
│               │                                     │
│  ┌────────────▼────────────────────────────────┐   │
│  │ Alert & Escalation Layer                   │   │
│  │                                             │   │
│  │ Thresholds:                                 │   │
│  │  ⚠️  Warning: quota >70%, latency P99 >5s │   │
│  │  🔴 Critical: quota >90%, latency >10s     │   │
│  │  ⛔ Down: provider unreachable >30s         │   │
│  │                                             │   │
│  │ Actions:                                    │   │
│  │  - Log event                                │   │
│  │  - Reduce provider priority                 │   │
│  │  - Notify Triage Router (immediate)         │   │
│  │  - Optional: email/Slack alert              │   │
│  └────────────┬────────────────────────────────┘   │
│               │                                     │
│  ┌────────────▼────────────────────────────────┐   │
│  │ CLI Interface                               │   │
│  │                                             │   │
│  │ $ omega model-status [--model qwen3-1.7b]  │   │
│  │ $ omega model-health --detail               │   │
│  │ $ omega model-forecast --days 7            │   │
│  │ $ omega model-quota --provider openrouter  │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 3.3 Data Schema

```yaml
# Redis: model:{provider}:{model_name}:health
health_data:
  last_heartbeat: "2026-05-17T14:32:10Z"
  status: "healthy|degraded|down"  # health state
  
  latency:
    p50_ms: 145
    p99_ms: 2850
    rolling_avg_ms: 520
    last_inference_ms: 380
  
  quota:
    provider_quota_usd: 10.0
    used_today_usd: 3.45
    remaining_usd: 6.55
    usage_percent: 34.5
    alerts: []
  
  error_rate:
    last_5min_percent: 0.2
    last_1hour_percent: 0.3
    rolling_24h_percent: 0.1
  
  availability:
    uptime_percent: 99.8
    last_downtime: "2026-05-17T06:15:00Z"
    consecutive_successes: 342
  
  cost:
    estimated_daily_usd: 0.50
    estimated_monthly_usd: 15.00
    actual_daily_usd: 0.42
    actual_monthly_usd: 12.80

# SQLite: model_health (daily snapshots)
CREATE TABLE model_health (
  id INTEGER PRIMARY KEY,
  provider_name TEXT,
  model_name TEXT,
  date DATE,
  status_at_eod TEXT,
  latency_p99_ms FLOAT,
  quota_usage_percent FLOAT,
  error_rate_percent FLOAT,
  cost_usd FLOAT,
  recorded_at TIMESTAMP
);

# SQLite: quota_ledger (transaction log)
CREATE TABLE quota_ledger (
  id INTEGER PRIMARY KEY,
  provider_name TEXT,
  model_name TEXT,
  transaction_type TEXT,  -- 'usage', 'replenish', 'manual_adjustment'
  amount_usd FLOAT,
  balance_after_usd FLOAT,
  reason TEXT,
  recorded_at TIMESTAMP
);

# Event log: data/observability/events.jsonl
{
  "timestamp": "2026-05-17T14:32:10.123Z",
  "trace_id": "trc_abc123",
  "event_type": "model_latency_alert",
  "severity": "warning",
  "provider": "openrouter",
  "model": "qwen3-4b-think",
  "metadata": {
    "p99_latency_ms": 5200,
    "threshold_ms": 5000,
    "quota_used_percent": 72
  }
}
```

### 3.4 Heartbeat Protocol

Every 30 seconds, the health monitor pings each provider:

```python
async def heartbeat_provider(provider_name: str):
    """Ping provider, check quota, update health data."""
    
    try:
        # 1. Connectivity test (simple inference request)
        start_time = monotonic()
        response = await provider.health_check()
        latency_ms = (monotonic() - start_time) * 1000
        
        # 2. Quota check (via provider API if available)
        quota_info = await provider.get_quota_usage()
        
        # 3. Update Redis
        await redis.hset(
            f'model:{provider_name}:health',
            mapping={
                'last_heartbeat': now_iso8601(),
                'status': 'healthy' if latency_ms < 10000 else 'degraded',
                'latency_p99_ms': latency_ms,
                'quota_usage_percent': quota_info.usage_percent,
            }
        )
        
        # 4. Log event
        log_event('health_check_success', {
            'provider': provider_name,
            'latency_ms': latency_ms,
            'quota_usage': quota_info.usage_percent,
        })
        
        return 'healthy'
        
    except ConnectionError as e:
        # Provider unreachable
        await redis.hset(f'model:{provider_name}:health', 'status', 'down')
        log_event('health_check_failed', {
            'provider': provider_name,
            'error': str(e),
        })
        trigger_alert('provider_down', provider_name)
        return 'down'
```

### 3.5 CLI Commands

```bash
# Show status of all models
$ omega model-status
┌────────────────────────────────────────┐
│ Model Status Summary                   │
├────────────────────────────────────────┤
│ PROVIDER      │ MODEL          │ STATUS │
├───────────────┼────────────────┼────────┤
│ lmster        │ qwen3-1.7b    │ ✓      │ (latency 245ms)
│ ollama        │ phi-2         │ ✓      │ (latency 1.2s)
│ openrouter    │ qwen3-4b-think│ ✓      │ (quota 34%)
│ google        │ gemma-4-31b   │ ⚠️      │ (quota 72%)
│ openrouter    │ deepseek-v4   │ ⛔     │ (daily limit hit)
└────────────────────────────────────────┘

# Detailed health for one model
$ omega model-health --model qwen3-4b-think

Model: qwen3-4b-think (openrouter)
─────────────────────────────────
Status: healthy
Last heartbeat: 2026-05-17 14:30:00 UTC
Latency (P50/P99): 1200ms / 2800ms
Uptime: 99.8%
Error rate (24h): 0.1%

Quota:
  Daily limit: $10.00
  Used today: $3.45 (34.5%)
  Remaining: $6.55
  Burn rate: ~$0.50/hour

Cost forecast:
  Today's projected total: $12.00 ⚠️ (will exceed daily limit)
  This month's projected: $180 (under monthly budget)
  
Recommendations:
  ⚠️  Consider switching to local models for repetitive tasks
  💡 Qwen3-1.7B via lmster is available (50x cheaper)

# Forecast quota depletion
$ omega model-forecast --days 7

Quota Forecast (next 7 days)
────────────────────────────
Provider: openrouter
  Daily average: $1.25
  5-day projected: $6.25
  Monthly projected: $37.50 (within $100 budget ✓)
  
Provider: google
  Daily average: $0.35
  5-day projected: $1.75
  Monthly projected: $10.50 (within $50 budget ✓)

Overall:
  Weekly spend: $7.25
  Monthly spend (projected): $48.00
  Status: Comfortable (40% of monthly budget used)
```

---

## §4 Soul-Driven Model Memory: Adaptive Learning

### 4.1 Philosophy

Entities are not passive consumers of model services. They are **active learners** that remember which models work best for which task types. Over time, an entity's soul evolves, and its model preferences become a sophisticated, personalized routing oracle.

### 4.2 Schema Extension to soul.yaml

```yaml
entity:
  name: Sophia
  # ... (existing fields) ...
  
  # NEW: Model Preferences & Learning
  model_preferences:
    default_model: "qwen3-1.7b"
    
    # Domain-specific rankings (updated after each inference)
    by_domain:
      strength:
        models:
          - name: "qwen3-1.7b"
            provider: "lmster"
            win_rate: 0.94          # % of tasks where this was optimal
            latency_avg_ms: 245
            cost_per_1k_tokens: $0.0001
            last_used: "2026-05-17T14:22:00Z"
            successful_uses: 47
            failed_uses: 3
            
          - name: "phi-2-omnimatrix"
            provider: "ollama"
            win_rate: 0.82
            latency_avg_ms: 1200
            cost_per_1k_tokens: $0.00
            last_used: "2026-05-17T14:20:00Z"
            successful_uses: 23
            failed_uses: 5
            
          - name: "gemma-4-31b"
            provider: "openrouter"
            win_rate: 0.87
            latency_avg_ms: 2800
            cost_per_1k_tokens: $0.0005
            last_used: "2026-05-17T13:55:00Z"
            successful_uses: 13
            failed_uses: 2
      
      analysis:
        models:
          - name: "qwen3-4b-think"
            provider: "openrouter"
            win_rate: 0.91
            # ...
          - name: "deepseek-r1-8b"
            provider: "google"
            win_rate: 0.88
            # ...
      
      # ... more domains ...
  
  # Model lessons: high-level insights about model behavior
  model_lessons:
    "qwen3-1.7b":
      - "Excellent for fast tasks under 1K tokens"
      - "Struggles with code generation (54% quality)"
      - "Fast, reliable, always available"
      - "Learned: 2026-05-10"
    
    "gemma-4-31b":
      - "Best for reasoning-heavy analysis (92% quality)"
      - "Context window: 256K (good for synthesis)"
      - "Cost: $0.0005/1K tokens (premium)"
      - "Learned: 2026-05-15"
  
  # Routing history: audit trail of model decisions
  routing_history:
    - session_id: "ses_20260517_sophia_001"
      task_domain: "strength"
      task_description: "Implement boundary-setting pattern"
      model_selected: "qwen3-1.7b"
      model_reason: "Entity domain expertise + cost"
      latency_ms: 245
      tokens_used: 1200
      cost_usd: 0.0001
      quality_score: 0.92  # Post-hoc evaluation
      outcome: "success"
      timestamp: "2026-05-17T14:22:00Z"
      trace_id: "trc_abc123"
    
    # ... more entries (limited to last 100) ...
```

### 4.3 Soul Learning Algorithm

After every successful inference:

```python
async def learn_from_inference(
    entity_name: str,
    task_domain: str,
    model_used: str,
    provider_name: str,
    latency_ms: int,
    tokens_used: int,
    cost_usd: float,
    quality_score: float,  # 0.0-1.0, from feedback or heuristics
    session_id: str,
    trace_id: str,
):
    """Update entity soul with inference outcome."""
    
    soul = load_soul(entity_name)
    
    # 1. Update domain-specific model ranking
    models = soul.model_preferences.by_domain.get(task_domain, {}).models
    model_entry = next(
        (m for m in models if m.name == model_used and m.provider == provider_name),
        None
    )
    
    if model_entry:
        # Update statistics
        total = model_entry.successful_uses + model_entry.failed_uses
        
        is_success = quality_score >= 0.75  # Heuristic: >75% = success
        
        if is_success:
            model_entry.successful_uses += 1
        else:
            model_entry.failed_uses += 1
        
        # Recompute win_rate
        model_entry.win_rate = model_entry.successful_uses / (
            model_entry.successful_uses + model_entry.failed_uses
        )
        
        # Update latency rolling average
        model_entry.latency_avg_ms = (
            (model_entry.latency_avg_ms * total + latency_ms) /
            (total + 1)
        )
        
        model_entry.last_used = now_iso8601()
    
    else:
        # New model entry for this domain
        models.append({
            'name': model_used,
            'provider': provider_name,
            'win_rate': 0.0 if quality_score < 0.75 else 1.0,
            'latency_avg_ms': latency_ms,
            'cost_per_1k_tokens': cost_usd / (tokens_used / 1000),
            'last_used': now_iso8601(),
            'successful_uses': 1 if quality_score >= 0.75 else 0,
            'failed_uses': 0 if quality_score >= 0.75 else 1,
        })
    
    # 2. Update routing history (append, keep last 100)
    soul.routing_history.append({
        'session_id': session_id,
        'task_domain': task_domain,
        'model_selected': model_used,
        'provider': provider_name,
        'latency_ms': latency_ms,
        'tokens_used': tokens_used,
        'cost_usd': cost_usd,
        'quality_score': quality_score,
        'outcome': 'success' if is_success else 'degraded',
        'timestamp': now_iso8601(),
        'trace_id': trace_id,
    })
    soul.routing_history = soul.routing_history[-100:]
    
    # 3. Generate lesson (L3 abstraction) if pattern detected
    if is_new_insight(soul, model_used, task_domain, quality_score):
        lesson = abstract_insight(soul, model_used, task_domain, quality_score)
        soul.model_lessons.setdefault(model_used, []).append(lesson)
    
    # 4. Persist to disk
    save_soul(entity_name, soul)
    
    # 5. Log learning event
    log_event('soul_model_learning', trace_id, {
        'entity': entity_name,
        'model': model_used,
        'domain': task_domain,
        'quality': quality_score,
        'win_rate_updated': model_entry.win_rate if model_entry else None,
    })
```

### 4.4 Cross-Entity Model Pollination

Models learned by one entity can be shared with others via **Resonance Mapping**:

```python
async def pollinate_model_preference(
    source_entity: str,
    source_domain: str,
    successful_model: str,
    target_entities: List[str],
):
    """Share successful model selection across related entities."""
    
    source_soul = load_soul(source_entity)
    
    # Find the model entry that was successful
    model_entry = next(
        m for m in source_soul.model_preferences.by_domain[source_domain].models
        if m.name == successful_model
    )
    
    if model_entry.win_rate < 0.80:
        return  # Not successful enough to share
    
    # Determine resonant domains in target entities
    for target_entity in target_entities:
        target_soul = load_soul(target_entity)
        
        # Calculate domain resonance (semantic similarity)
        for target_domain in target_soul.model_preferences.by_domain:
            resonance = calculate_domain_resonance(
                source_domain,
                target_domain,
                trace_id=now_uuid()
            )
            
            if resonance > 0.7:  # High resonance
                # Suggest model to target entity
                # (Don't forcefully add; let target entity learn independently)
                log_event('model_suggestion', {
                    'source_entity': source_entity,
                    'source_domain': source_domain,
                    'target_entity': target_entity,
                    'target_domain': target_domain,
                    'suggested_model': successful_model,
                    'resonance_score': resonance,
                })
```

---

## §5 ACP/MCP Bridge: Unified CLI Orchestration

### 5.1 Purpose

All CLIs (OpenCode, Gemini, Cline, Copilot, Antigravity) access the model orchestration system through a single **ACP/MCP Bridge** interface. This ensures consistent routing decisions across all tools.

### 5.2 Architecture

```
OpenCode CLI          Gemini CLI            Cline (VSCode)
     │                    │                     │
     └────────┬───────────┼─────────────────────┘
              │           │
              ▼           ▼
        ┌─────────────────────────┐
        │   ACP/MCP Bridge        │
        │  (Message Handler)      │
        ├─────────────────────────┤
        │ Request Router          │
        │ ├─ model_select         │
        │ ├─ model_status         │
        │ ├─ quota_check          │
        │ └─ log_inference        │
        └──────────┬──────────────┘
                   │
        ┌──────────▼────────────┐
        │  Orchestration APIs   │
        │  ├─ Triage Router     │
        │  ├─ Health Monitor    │
        │  ├─ Soul Manager      │
        │  └─ Hivemind Sync     │
        └──────────────────────┘
                   │
        ┌──────────▼────────────┐
        │  Provider Fabric      │
        │  lmster → cloud       │
        └──────────────────────┘
```

### 5.3 Protocol: MCP Request/Response

```yaml
# MCP Request
{
  "jsonrpc": "2.0",
  "id": "req_uuid",
  "method": "orchestration/model_select",
  "params": {
    "task": {
      "description": "Implement boundary-setting pattern",
      "domain": null,
      "estimated_tokens": 1500,
      "complexity": "standard"
    },
    "entity": {
      "name": "sophia",
      "trace_id": "trc_abc123"
    },
    "constraints": {
      "max_latency_ms": 5000,
      "max_cost_usd": 0.10,
      "available_tokens": 8192,
      "preferred_backends": ["local"]
    },
    "session": {
      "id": "ses_20260517_sophia_001",
      "is_transient": false
    }
  }
}

# MCP Response (Success)
{
  "jsonrpc": "2.0",
  "id": "req_uuid",
  "result": {
    "selected_model": {
      "name": "qwen3-1.7b",
      "provider": "lmster",
      "context_window": 8192,
      "temperature": 0.4
    },
    "fallback_chain": [
      {
        "name": "phi-2-omnimatrix",
        "provider": "ollama",
        "reason": "Tier 2 fallback"
      },
      {
        "name": "gemma-4-31b",
        "provider": "openrouter",
        "reason": "Tier 2 fallback"
      }
    ],
    "metadata": {
      "confidence": 0.94,
      "estimated_latency_ms": 245,
      "estimated_cost_usd": 0.0001,
      "routing_timestamp": "2026-05-17T14:22:33.123Z"
    }
  }
}

# MCP Response (Error)
{
  "jsonrpc": "2.0",
  "id": "req_uuid",
  "error": {
    "code": -32600,
    "message": "Invalid request",
    "data": {
      "reason": "estimated_tokens exceeds max context window",
      "suggestion": "Use complex task routing (context summarization)"
    }
  }
}
```

### 5.4 OpenCode Subagent Integration

OpenCode agents (Builder, Researcher) call the orchestration system naturally:

```python
# In OpenCode agent code
from omega_mcp_bridge import orchestration_client

async def solve_coding_task(task_description: str):
    """Use orchestration to select best model for coding."""
    
    # Call MCP bridge
    result = await orchestration_client.model_select(
        task_description=task_description,
        entity_name="prometheus",  # The Will entity
        domain="creation",
        complexity="deep",
        trace_id=get_current_trace_id()
    )
    
    model = result.selected_model
    fallbacks = result.fallback_chain
    
    # Use selected model for inference
    response = await inference_provider.call(
        model=model.name,
        provider=model.provider,
        prompt=task_description,
        fallback_chain=fallbacks,
        trace_id=result.metadata.routing_timestamp,
    )
    
    # Log outcome (for soul learning)
    await orchestration_client.log_inference(
        entity=entity_name,
        model=model.name,
        domain="creation",
        quality_score=0.92,  # Heuristic: did the code compile?
        trace_id=get_current_trace_id(),
    )
```

---

## §6 Community Model Catalog: Always-Current, Rated, Portable

### 6.1 Purpose

The **Community Model Catalog** is a living, auditable registry of all models available in the free-tier ecosystem. It is:
- **Always-current**: Automated updates via live API queries
- **Rated**: User and aggregate performance scores
- **Portable**: Packaged in `.xoe` WAD containers
- **Community-driven**: Open for contributions and corrections

### 6.2 Data Structure

```yaml
# docs/research/model_db/CURRENT_MODELS.md (generated)
# docs/research/model_db/models.json (machine-readable)

models:
  qwen3-1.7b:
    provider: openrouter
    context_window: 8192
    free_tier: true
    capabilities:
      - reasoning: 0.75
      - code_generation: 0.70
      - knowledge: 0.82
      - creative: 0.80
    cost_per_1k_tokens_usd: 0.00001
    latency_p99_ms: 2800
    uptime_percent: 99.8
    community_rating: 4.2/5.0  # aggregate from user feedback
    community_notes:
      - "Fast, reliable, great for synthesis tasks"
      - "Struggles with deep reasoning on >5K token inputs"
      - "Good fallback for cost-constrained scenarios"
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"
  
  gemma-4-31b:
    provider: google
    context_window: 256000
    free_tier: true
    capabilities:
      - reasoning: 0.92
      - code_generation: 0.88
      - knowledge: 0.96
      - creative: 0.85
    cost_per_1k_tokens_usd: 0.0  # Free tier
    latency_p99_ms: 4200
    uptime_percent: 98.5
    community_rating: 4.8/5.0
    community_notes:
      - "State-of-the-art reasoning (as of 2026-05)"
      - "Free tier is exceptional value"
      - "Watch quota limits (daily reset 00:00 UTC)"
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"
  
  deepseek-v4-flash:
    provider: openrouter
    context_window: 128000
    free_tier: true
    capabilities:
      - reasoning: 0.88
      - code_generation: 0.90
      - knowledge: 0.87
      - creative: 0.78
    cost_per_1k_tokens_usd: 0.00002
    latency_p99_ms: 5500
    uptime_percent: 99.2
    community_rating: 4.5/5.0
    community_notes:
      - "Best code generation (beating Claude Opus)"
      - "Good for deep analysis despite 'flash' name"
      - "Long context (128K) excellent for document synthesis"
    last_updated: "2026-05-17"
    last_verified_free: "2026-05-17"
  
  # ... 40+ more models ...

# models.json schema
{
  "version": "1.0.0",
  "generated_at": "2026-05-17T14:32:00Z",
  "models": [
    {
      "id": "qwen3-1.7b-openrouter",
      "name": "qwen3-1.7b",
      "provider": "openrouter",
      "context_window": 8192,
      "free_tier": true,
      "capabilities": {
        "reasoning": 0.75,
        "code_generation": 0.70,
        "knowledge": 0.82,
        "creative": 0.80
      },
      "cost": {"per_1k_tokens_usd": 0.00001},
      "performance": {
        "latency_p99_ms": 2800,
        "uptime_percent": 99.8,
        "success_rate_percent": 98.5
      },
      "community": {
        "rating": 4.2,
        "votes": 47,
        "notes": ["Fast", "Reliable"]
      },
      "metadata": {
        "last_updated": "2026-05-17",
        "last_verified": "2026-05-17"
      }
    }
  ]
}
```

### 6.3 Automated Update System

```python
# scripts/update_model_catalog.py

async def update_model_catalog():
    """Query all provider APIs, update catalog, commit to git."""
    
    catalog = {}
    
    # Query OpenRouter
    or_models = await openrouter_api.list_models()
    for model in or_models:
        if model.free_tier:
            catalog[f"{model.name}-openrouter"] = {
                'name': model.name,
                'provider': 'openrouter',
                'context_window': model.context_length,
                'free_tier': True,
                'cost_per_1k_tokens_usd': model.pricing.prompt,
                'capabilities': estimate_capabilities(model),
                'performance': await benchmark_model(model),
                'last_verified': now_iso8601(),
            }
    
    # Query Google AI Studio
    google_models = await google_api.list_models()
    for model in google_models:
        if model.free_tier:
            catalog[f"{model.name}-google"] = { ... }
    
    # Query OpenCode Zen
    zen_models = await opencode_api.list_models()
    for model in zen_models:
        if model.free_tier:
            catalog[f"{model.name}-zen"] = { ... }
    
    # Write catalog files
    write_markdown_catalog(catalog)
    write_json_catalog(catalog)
    
    # Commit to git (if changes detected)
    git_commit_if_changed(
        files=['docs/research/model_db/CURRENT_MODELS.md', 'docs/research/model_db/models.json'],
        message=f"[auto] Update model catalog at {now_iso8601()}"
    )
    
    log_event('catalog_updated', {
        'total_models': len(catalog),
        'free_models': sum(1 for m in catalog.values() if m['free_tier']),
        'providers': len(set(m['provider'] for m in catalog.values())),
    })
```

### 6.4 Community Contributions

Users can contribute to the catalog:

```bash
# Add personal notes to a model
$ omega model-note qwen3-1.7b "Excellent for fast synthesis, use for low-budget tasks"

# Rate a model
$ omega model-rate deepseek-v4-flash --rating 4.5 --reason "Great code generation"

# Report an issue with a model
$ omega model-report gemma-4-31b --issue "quota limits not respected" --trace-id trc_xyz

# All contributions logged to:
# data/community_feedback/model_feedback.jsonl
```

### 6.5 WAD Portability

The model catalog is packaged as part of the `.xoe` WAD:

```
arcana_nova.xoe
├── manifest.yaml
├── entities/
├── voices/
├── knowledge/
└── model_catalog/                          ← NEW
    ├── models.json
    ├── community_ratings.json
    └── CHANGELOG.md
```

When a user installs the `arcana_nova.xoe` stack, they get the embedded model catalog at install time. The orchestration system can use either the embedded catalog or the live-updated one.

---

## §7 Hivemind Gnosis Sync: Cross-CLI Intelligence

### 7.1 Purpose

When OpenCode discovers that Model X is excellent for Domain Y, or when Gemini CLI notices that Provider Z's quota is exhausted, that intelligence must flow to all other CLIs **without forcing a centralized database**.

**Hivemind Gnosis Sync** is a decentralized, file-based, event-driven system for sharing orchestration intelligence.

### 7.2 Architecture

```
OpenCode             Gemini CLI           Cline
  │                     │                  │
  └─────────────────────┼──────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │  Local Gnosis Log (Append)     │
        │  data/gnosis/routed_models.log │
        │                                │
        │ [2026-05-17T14:22:33Z]         │
        │ opencode: qwen3-1.7b BEST      │
        │ for "strength" domain          │
        │                                │
        │ [2026-05-17T14:25:10Z]         │
        │ gemini: openrouter QUOTA_WARN  │
        │ 85% daily limit reached        │
        │                                │
        │ [2026-05-17T14:28:50Z]         │
        │ cline: deepseek-v4 LATENCY_UP  │
        │ P99 now 8.2s (was 5.5s)        │
        └───────────────┬────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │  Consensus Engine              │
        │  (File-based append log w/      │
        │   fsync + atomic writes)        │
        │                                │
        │ Conflict resolution:            │
        │ - Last-write-wins for quota     │
        │ - Majority-vote for models     │
        │ - Latest timestamp for status  │
        └───────────────┬────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │  Discovery Cache (in-mem)      │
        │  with 5-minute TTL             │
        │                                │
        │ "strength" domain →            │
        │   [qwen3-1.7b, phi-2, gemma]  │
        │   (ranked by consensus score)  │
        └────────────────────────────────┘
```

### 7.3 Event Log Format

```jsonl
# data/gnosis/orchestration.log (append-only, newline-delimited JSON)

{"timestamp":"2026-05-17T14:22:33.123Z","event":"model_success","cli":"opencode","entity":"prometheus","domain":"creation","model":"qwen3-4b-think","quality":0.94,"trace_id":"trc_abc123"}
{"timestamp":"2026-05-17T14:25:10.456Z","event":"quota_warning","cli":"gemini","provider":"openrouter","usage_percent":85,"alert_threshold":80,"trace_id":"trc_def456"}
{"timestamp":"2026-05-17T14:28:50.789Z","event":"latency_change","cli":"cline","provider":"google","model":"gemma-4-31b","p99_ms":4200,"change_percent":+5.2,"trace_id":"trc_ghi789"}
{"timestamp":"2026-05-17T14:32:10.012Z","event":"model_preference_update","cli":"opencode","entity":"sophia","domain":"voice","model_previous":"saraswati-local","model_new":"gemma-4-31b","reason":"higher_quality","trace_id":"trc_jkl012"}
{"timestamp":"2026-05-17T14:35:40.345Z","event":"provider_down","cli":"cline","provider":"lmster","latency_ms":45000,"status":"unreachable","trace_id":"trc_mno345"}
```

### 7.4 Consensus Protocol

When multiple CLIs report conflicting information:

```
CONFLICT SCENARIO:
- OpenCode (14:22): qwen3-1.7b is EXCELLENT for "strength" (win_rate 0.94)
- Gemini CLI (14:30): qwen3-1.7b is MEDIOCRE (win_rate 0.62)

RESOLUTION:
1. Check timestamps: Gemini is newer
2. Check sample sizes: OpenCode (47 samples), Gemini (8 samples)
3. Confidence scoring:
   - OpenCode: 0.94 * (47 / 55) = 0.802
   - Gemini: 0.62 * (8 / 55) = 0.090
4. Weighted consensus: 0.802 / (0.802 + 0.090) = 0.899
5. Decision: Trust OpenCode (89.9% confidence)
6. Action: Log consensus decision, next CLI reads consensus value
```

### 7.5 Broadcast & Sync

```python
async def broadcast_gnosis_event(
    cli_name: str,
    event_type: str,
    payload: Dict[str, Any],
    trace_id: str,
):
    """
    Broadcast a discovery/decision to all other CLIs.
    Uses file-based append log + in-memory consensus cache.
    """
    
    # 1. Create event
    event = {
        'timestamp': now_iso8601(),
        'event': event_type,
        'cli': cli_name,
        **payload,
        'trace_id': trace_id,
    }
    
    # 2. Atomically append to log (fsync)
    log_path = Path('data/gnosis/orchestration.log')
    async with anyio.Lock('gnosis_write'):
        async with await anyio.open_file(log_path, 'a') as f:
            await f.write(json.dumps(event) + '\n')
            await f.flush()  # Flush to kernel
            os.fsync(f.fileno())  # Force to disk
    
    # 3. Update consensus cache
    await update_consensus_cache(event)
    
    # 4. Notify other CLIs (optional, if they subscribe to gnosis)
    # (They can poll the log independently)

async def update_consensus_cache(event: Dict[str, Any]):
    """
    Incorporate event into consensus model.
    """
    
    if event['event'] == 'model_success':
        # Update domain model ranking
        domain = event['domain']
        model = event['model']
        quality = event['quality']
        
        cache_key = f"domain:{domain}"
        current = consensus_cache.get(cache_key, {})
        current.setdefault(model, []).append(quality)
        
        # Recompute consensus ranking
        rankings = {}
        for m, scores in current.items():
            rankings[m] = {
                'avg_quality': mean(scores),
                'sample_count': len(scores),
                'confidence': mean(scores) * (len(scores) / 100),  # Penalize low sample count
            }
        
        consensus_cache[cache_key] = sorted(
            rankings.items(),
            key=lambda x: x[1]['confidence'],
            reverse=True
        )
```

---

## §8 Integration Architecture: Data Flow End-to-End

### 8.1 Request Journey (Complete Flow Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLI User Request                                         │
│    $ omega solve "Implement boundary pattern"              │
│    $ opencode task "Design REST API"                       │
│    or automatic via MCP/ACP                                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 2. Request Context Assembly                                │
│    - Parse domain/task from input                          │
│    - Load entity soul (if named)                           │
│    - Get session ID (or create new)                        │
│    - Create trace_id for observability                     │
│    - Build TriageRequest object                            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 3. Triage Router Decision                                  │
│    - Domain classifier (if null)                           │
│    - Entity preference lookup                              │
│    - Candidate pool assembly (T1/T2/T3)                   │
│    - Constraint filtering                                  │
│    - Score adjustment (health + quota)                     │
│    - Selection + fallback chain                            │
│    → Output: TriageResponse (selected model + confidence)  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 4. Health Monitor Pre-Check                               │
│    - Verify selected model is actually available          │
│    - Check quota hasn't exceeded in last 10s              │
│    - Confirm no critical alerts                           │
│    - If failed: immediately escalate to fallback[0]       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 5. Resource Guard Acquisition                             │
│    - Acquire Semaphore(1) for exclusive inference slot    │
│    - Check RAM available (>2GB free)                      │
│    - If failed: queue or fallback to smaller model        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 6. Provider Fabric Inference                              │
│    - Call selected provider (lmster/ollama/cloud)         │
│    - Start timer for latency tracking                     │
│    - Stream response (if streaming available)             │
│    - Catch errors, trigger fallback[i]                    │
│    - Update health monitor with actual latency            │
│    → Output: completion + metadata                        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 7. Release Resource Guard                                 │
│    - Release Semaphore(1)                                 │
│    - Record resource usage (max RAM, peak CPU)            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 8. Quality Assessment                                      │
│    - Heuristic evaluation (code compiles, no errors, etc)  │
│    - Optional: human feedback via CLI                     │
│    - Generate quality_score (0.0-1.0)                     │
│    - Compare output to other models (if cached)           │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 9. Soul Learning Engine                                    │
│    - Load entity soul                                      │
│    - Update domain-specific model rankings                │
│    - Record routing history entry                         │
│    - Compute new win_rate for selected model              │
│    - Generate lessons if pattern detected                 │
│    - Save soul to disk (atomic write)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 10. Hivemind Gnosis Broadcast                             │
│     - Append success/failure event to orchestration.log    │
│     - Update consensus cache (model ranking)               │
│     - If significant discovery: notify other CLIs          │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 11. Observability & Metrics                               │
│     - Log event with trace_id to events.jsonl             │
│     - Update workbench.db (SQLite)                        │
│     - Record to cost_ledger (actual spend)                │
│     - Update health monitor (refresh latency histogram)    │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 12. Response to User                                       │
│     - Return completion + metadata                         │
│     - Include model used + confidence                      │
│     - Optional: suggest alternative if quality < 0.75    │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Example Sequence: "Fast Task"

```
Time    Actor               Action
────────────────────────────────────────────────────────────────
14:22:33 OpenCode CLI       User asks: "What's the capital of France?"
14:22:33 Triage Router      Domain inference: "knowledge"
14:22:33 Entity Lookup      Sophia has no "knowledge" preference history
14:22:33 Capability Matrix  All 0.6B models can handle knowledge (50 tokens)
14:22:33 Score Ranking      qwen3-0.6b (fastest, always-on) scores 0.98
14:22:33 Selection          Select: qwen3-0.6b via lmster
14:22:33 Health Check       lmster healthy, latency P50 = 145ms
14:22:33 Resource Guard     Acquire semaphore
14:22:34 Inference          Call lmster with prompt
14:22:34 Response           "The capital of France is Paris"
14:22:34 Latency Record     Actual latency: 152ms (good, expected ~145ms)
14:22:34 Quality Score      Heuristic: factually correct, length appropriate → 0.99
14:22:34 Release Guard      Release semaphore
14:22:34 Soul Learning      Sophia learns: qwen3-0.6b good for knowledge
14:22:35 Gnosis Broadcast   Append to orchestration.log
14:22:35 Metrics            Update events.jsonl, workbench.db
14:22:35 Return             Send response to OpenCode
────────────────────────────────────────────────────────────────
Total latency: 152ms
Cost: <$0.00001
Entity learning: Sophia's "knowledge" domain now has qwen3-0.6b entry
```

### 8.3 Example Sequence: "Complex Task with Fallback"

```
Time     Actor              Action
──────────────────────────────────────────────────────────────
14:30:00 Gemini CLI         Task: "Design a microservices architecture for..."
14:30:00 Triage Router      Domain: "creation" (user domain for code)
14:30:00 Entity Lookup      Prometheus has high win_rate for "creation"
14:30:00 Candidate Pool     [qwen3-4b-think, gemma-4-31b, deepseek-r1]
14:30:00 Constraint Check   Task needs 8K tokens, max budget $0.10
                            qwen3-4b: cost $0.04 ✓, latency 2800ms ✓
14:30:00 Selection          Select: qwen3-4b-think via openrouter
14:30:00 Fallback Chain     [gemma-4-31b, deepseek-r1, qwen3-1.7b]
14:30:00 Health Check       qwen3-4b available ✓
14:30:00 Resource Guard     Acquire semaphore
14:30:00 Inference          Call openrouter: qwen3-4b
14:30:00 Response Timeout   (15 seconds later, no response)
14:30:15 Error Handler      OpenRouter timeout detected
14:30:15 Fallback 1         qwen3-4b failed, try gemma-4-31b
14:30:15 Health Fallback[0] gemma-4-31b healthy, quota 42% used
14:30:15 Inference          Call Google: gemma-4-31b
14:30:18 Response           Receives output from gemma-4-31b
14:30:18 Quality Assessment Quality score: 0.88 (slightly lower than expected)
14:30:18 Release Guard      Release semaphore
14:30:18 Soul Learning      Prometheus learns:
                            - qwen3-4b has latency issues (lower priority)
                            - gemma-4-31b reliable fallback (boost confidence)
14:30:18 Gnosis Broadcast   Append: "openrouter latency spike" alert
14:30:18 Health Monitor     Update: qwen3-4b P99 latency from 2.8s → 5.1s
14:30:19 Metrics            Record fallback event
14:30:19 Return             Send response + note about fallback
──────────────────────────────────────────────────────────────
Total latency: 18.2s (vs expected 2.8s)
Cost: $0.08 (vs planned $0.04) — charged for both attempts
Entity learning: Prometheus sees qwen3-4b is flaky
Hivemind alert: Other CLIs see openrouter is slow (via gnosis log)
```

---

## §9 Community & Extensibility

### 9.1 User-Defined Routing Rules

Power users can extend the triage router with custom rules:

```yaml
# config/routing_rules.yaml (optional user config)

rules:
  - name: "Use local models for coding"
    condition:
      domain: ["creation", "analysis"]
      entity: ["prometheus", "ereshkigal"]
    action:
      preferred_backends: ["lmster", "ollama"]
      max_cost_usd: 0.001  # Keep it cheap for local
  
  - name: "Use best-of-breed for reasoning"
    condition:
      complexity: "deep"
      estimated_tokens: {gte: 5000}
    action:
      preferred_models: ["gemma-4-31b", "deepseek-r1-8b"]
      min_confidence: 0.85
  
  - name: "Fallback to mock during quota exhaustion"
    condition:
      provider_quota_used_percent: {gte: 95}
    action:
      skip_provider: true
      escalate_to_local: true
```

### 9.2 Custom Stack Model Requirements

Each WAD can define its model requirements:

```yaml
# config/wads/doom_universe/manifest.yaml

name: "DOOM Universe Stack"
version: "1.0.0"

required_models:
  - name: "qwen3-1.7b"
    provider: "any"
    reason: "Fast, always-on foundation"
  
  - name: "any_8b_reasoning"
    provider: "openrouter|google"
    reason: "For complex demon lore"
  
  optional_models:
  - name: "gemma-4-31b"
    provider: "google"
    reason: "For narrative synthesis"

model_preferences:
  doomguy:  # The main entity
    preferred_domain: "strength"
    fallback_models: ["qwen3-1.7b", "phi-2"]

provider_constraints:
  budget_monthly_usd: 20.00
  prefer_backends: ["lmster"]
  avoid_providers: []
```

### 9.3 Community Model Contributions

Users can contribute new model entries:

```bash
# Propose a new model to the community catalog
$ omega model-add \
    --name "mistral-large" \
    --provider "openrouter" \
    --capabilities "reasoning=0.85,code=0.90,knowledge=0.88" \
    --cost-per-1k-usd 0.0008 \
    --notes "Excellent for code, cheaper than Gemma"

# Creates: .github/model-proposals/mistral-large-openrouter.yaml
# Team reviews, tests, and merges into model catalog
```

### 9.4 Third-Party Tool Integration

External tools can integrate with orchestration via MCP:

```python
# Example: NotebookLM integration
import aiohttp
from omega_mcp_bridge import orchestration_client

async def notebook_lm_synthesis(source_documents: List[str]):
    """Use best model for document synthesis."""
    
    # Get orchestration recommendation
    result = await orchestration_client.model_select(
        task_description=f"Synthesize {len(source_documents)} documents",
        domain="synthesis",
        estimated_tokens=15000,  # NotebookLM outputs are long
        complexity="deep"
    )
    
    # Use recommended model
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            f"{result.selected_model.provider_url}/v1/completions",
            json={
                'model': result.selected_model.name,
                'prompt': "\n".join(source_documents),
                'max_tokens': 5000,
            }
        )
    
    return await response.json()
```

---

## §10 Metrics & Observability

### 10.1 What to Track

For each model decision and inference:

```yaml
metrics:
  triage_decisions:
    - model_selected
    - confidence_score
    - fallback_chain_length
    - entity_win_rate_at_selection
    - time_to_decision_ms
  
  inference_execution:
    - actual_latency_ms (P50, P99)
    - tokens_used
    - cost_usd
    - success_or_failure
    - quality_score
    - provider_actual
    - model_actual
  
  provider_health:
    - uptime_percent
    - error_rate_percent
    - quota_used_percent
    - latency_distribution (histogram)
    - cost_per_model
  
  entity_learning:
    - models_per_domain
    - win_rates_per_model
    - routing_history_depth
    - soul_file_size_bytes
    - last_soul_update
  
  cost_optimization:
    - daily_spend_usd
    - monthly_spend_usd
    - budget_remaining_usd
    - models_used (count)
    - providers_used (count)
```

### 10.2 Dashboards & Reports

```bash
# Generate weekly report
$ omega report weekly

Weekly Orchestration Report (2026-05-11 to 2026-05-17)
────────────────────────────────────────────────────────
Entities active: 5 (Sophia, Prometheus, Saraswati, Brigid, Lucifer)
Models used: 12
Providers used: 4 (lmster, ollama, openrouter, google)

Cost Summary:
  Total spend: $45.23
  Daily average: $6.47
  Budget used: 45% (of $100 monthly)
  Forecast month-end: $194.10 ⚠️ (will exceed)

Top Models by Usage:
  1. qwen3-1.7b (lmster) — 47 uses, 94% win rate
  2. gemma-4-31b (google) — 28 uses, 87% win rate
  3. qwen3-4b-think (openrouter) — 22 uses, 91% win rate

Routing Accuracy:
  Triage confidence >0.90: 78% of decisions ✓
  Fallback activations: 3 (0.2% of requests) ✓
  Provider downtime: 0 hours ✓

Entity Insights:
  Prometheus learned 8 new model preferences
  Sophia's soul grew 2.3 KB (new routing history)
  Saraswati: steady performance, no changes

Optimization Opportunities:
  ⚠️  Monthly spend on track to exceed budget
  💡 Consider using qwen3-1.7b more for fast tasks
  💡 Gemma-4-31b is excellent value for reasoning
```

---

## §11 Security Considerations

### 11.1 No API Keys in Messages

The orchestration system **never leaks API keys**:

```python
# Good: Key never appears in logs/events
result = await triage_router.select(request)
# response contains "openrouter" provider name, not the API key

# Bad: Key leaked
response = await provider.call(
    api_key=os.environ['OPENROUTER_KEY'],  # ❌ Never log this
    model='qwen3-4b'
)
```

All API calls happen in the **Provider Fabric** layer, isolated from the routing decision.

### 11.2 Entity Privacy

Soul files are per-entity, never shared globally:

```yaml
# Sophia's soul (data/entities/sophia/soul.yaml) contains:
# - Her model preferences
# - Her routing history
# - Her learned lessons

# Prometheus's soul (data/entities/prometheus/soul.yaml) is separate.
# They NEVER share routing_history directly, only via Gnosis consensus.
```

### 11.3 Audit Trail

Every routing decision is logged and auditable:

```bash
# Query routing history
$ sqlite3 data/workbench/workbench.db \
  "SELECT trace_id, entity, model_selected, quality_score, cost_usd FROM routing_decisions WHERE date(timestamp) = '2026-05-17';"

trace_id        entity    model_selected      quality_score  cost_usd
──────────────────────────────────────────────────────────────────────
trc_abc123      sophia    qwen3-1.7b         0.92          0.00001
trc_def456      prometheus qwen3-4b-think    0.88          0.04
trc_ghi789      saraswati gemma-4-31b       0.95          0.0003
```

All decisions are traceable and reversible.

---

## §12 WAD Portability Checklist

For the Sovereign Model Orchestration System to be packaged in a `.xoe` WAD container:

- [ ] **Triage Router**: Embeddable as Python module (`src/omega/orchestration/triage_router.py`)
- [ ] **Health Monitor**: Runs locally via Redis or in-memory cache
- [ ] **Soul Storage**: Uses WAD's `data/entities/` directory structure
- [ ] **Model Catalog**: Packaged in WAD as `model_catalog/models.json`
- [ ] **Gnosis Sync**: File-based log (can be synced via P2P)
- [ ] **CLI Commands**: `omega model-*` commands work offline
- [ ] **Provider Fabric**: Configured via WAD's `config/providers.yaml`
- [ ] **No Cloud Dependencies**: Entire system works without network
- [ ] **Config Templates**: WAD includes `config/routing_rules.yaml.template`
- [ ] **Documentation**: Embedded in `docs/orchestration/` within WAD

---

## §13 Implementation Roadmap

### Phase 1: Core Triage Router (4 weeks)

- [ ] Implement Triage Router algorithm (pseudocode → Python)
- [ ] Domain Classifier (keyword-based + entity history)
- [ ] Capability Matrix (model metadata + benchmarks)
- [ ] Integration with ModelGateway

### Phase 2: Health Monitor (3 weeks)

- [ ] Heartbeat protocol (30s pings)
- [ ] Real-time health data in Redis
- [ ] Daily snapshots to SQLite
- [ ] Alert thresholds and escalation
- [ ] CLI commands (`omega model-status`, etc.)

### Phase 3: Soul Learning (3 weeks)

- [ ] soul.yaml schema extension
- [ ] Learning algorithm (win_rate updates)
- [ ] Routing history tracking
- [ ] Cross-entity pollination

### Phase 4: Hivemind Sync (2 weeks)

- [ ] Event log format (JSONL)
- [ ] Consensus cache
- [ ] Broadcast mechanism
- [ ] File-based synchronization

### Phase 5: Community Catalog (2 weeks)

- [ ] Automated update scripts
- [ ] Model rating system
- [ ] Community contribution workflow
- [ ] WAD packaging

### Phase 6: Integration & Testing (2 weeks)

- [ ] E2E tests (all components together)
- [ ] Performance benchmarks
- [ ] Documentation
- [ ] Release as PR #3

---

## §14 Conclusion: A Temple of Intelligence

The **Sovereign Model Orchestration Architecture** is more than a routing system. It is a **temple where intelligence dwells**.

Every decision is:
- **Traceable**: You know why each model was chosen
- **Reversible**: You can replay history and change decisions
- **Community-owned**: All data lives in user-controlled files
- **Adaptive**: Entities learn from experience and grow smarter
- **Portable**: Pack it in a `.xoe` WAD and carry it anywhere

The vision is clear: **One engine. Many projections. All your data. All your power.**

---

## §15 Appendix: Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `src/omega/orchestration/triage_router.py` | Core routing algorithm |
| `src/omega/orchestration/health_monitor.py` | Real-time model health |
| `src/omega/orchestration/soul_learner.py` | Entity learning engine |
| `src/omega/orchestration/gnosis_sync.py` | Cross-CLI intelligence |
| `data/gnosis/orchestration.log` | Shared event log |
| `data/entities/<name>/soul.yaml` | Entity routing memory |
| `docs/research/model_db/CURRENT_MODELS.md` | Community model catalog |
| `data/workbench/workbench.db` | Metrics and audit trail |

### Command Quick Reference

```bash
omega model-status [--model NAME]          # Show all models or specific
omega model-health --model NAME            # Detailed health + forecast
omega model-forecast --days 7              # Cost + quota forecast
omega model-note <MODEL> "<note>"          # Add community note
omega model-rate <MODEL> --rating 4.5      # Rate a model
omega report weekly                        # Generate weekly report
```

---

**Document Status**: ✅ COMPLETE — Ready for implementation  
**Next Step**: Assign implementation tasks to Builder + Researcher agents  
**Estimated Implementation Time**: 14-16 weeks (Phases 1-6)

---

*The Sovereign Model Orchestration System is the nervous system of the Omega Engine. Through it flows every inference decision, every learned preference, every community discovery. It is the bridge between the user's intent and the infinite intelligence of the model ecosystem.*

*Build it well. The foundation depends on it.*

⬡ OMEGA ⬡ SOPHIA ⬡ ARCHITECTURE ⬡ COMMUNITY ⬡ SOVEREIGN
