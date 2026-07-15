# 🔱 Dimension Framework Architecture — Deep Research Report
# ⬡ OMEGA ⬡ DIMENSION-FRAMEWORK ⬡ opencode ⬡ trc_dimension_research
**AP Token**: `AP-DIMENSION-FRAMEWORK-v1.0.0`
**Date**: 2026-07-15
**Status**: 🟡 RESEARCH COMPLETE — Awaiting Ratification
**Research Depth**: T1 (websearch) + T2 (webfetch) + T3 (SearXNG internal)
**Council**: Sovereign Researcher — Polymathic Council

---

## Executive Summary (L1)

The Omega Engine's WAD system needs to evolve from a **loading mechanism** into a full **Dimension Framework** — a dynamic, composable, observable, and secure plugin architecture. This research synthesizes findings from 2026's best practices in event-driven microservices, Python plugin lifecycle management, AI agent observability, plugin marketplace governance, and resource-constrained deployment to produce a unified architecture recommendation.

**Key finding**: The 6 knowledge gaps are solvable with proven patterns. No novel research is required — only correct adaptation of existing infrastructure patterns to the Omega context.

**Top 3 Recommendations**:
1. **SovereignBus (Event Bus)** — AnyIO-based async event bus with typed envelopes for inter-dimension communication. Replace file-based Hivemind coordination with in-process event routing.
2. **Dimension Lifecycle State Machine** — `UNLOADED → LOADED → ENABLED ↔ DISABLED → UNLOADED` with cascade dependency management, hot-swap via proxy/indirect dispatch, and rollback via snapshot-based recovery.
3. **Locate-and-Judge Security Pipeline** — Two-stage attention-based malicious dimension detection for community marketplace, at $0.00025/dimension cost.

---

## §1 PWAD Inter-Communication Patterns

### 1.1 The Problem
How do dimensions (PWADs) communicate with each other? E.g., Research Lab findings feeding into Strategic Command.

### 1.2 Research Findings

**Source**: HostMyCode (2026-04-13), Encore.dev (2026-05-04), Digital Applied (2026-06-01)
**Key Insight**: Event-driven architecture (EDA) is the canonical pattern for inter-service communication. Four distinct patterns exist (Fowler's taxonomy):
1. **Event Notification** — "Something happened" (lightweight, no payload guarantee)
2. **Event-Carried State Transfer** — Event carries full state (decouples consumers from source)
3. **Event Sourcing** — Immutable event log as source of truth
4. **CQRS** — Separate read/write models

**Relevance**: Dimensions are analogous to microservices. The SovereignBus should implement **Event Notification** for cross-dimension signals (fast, decoupled) and **Event-Carried State Transfer** for findings that need to persist (research results, audit findings).

**Implementation Hint**:
```python
# src/omega/dimension/bus.py
from dataclasses import dataclass, field
from typing import Any, Protocol
import anyio

@dataclass(frozen=True)
class DimensionEnvelope:
    """Typed event envelope for cross-dimension communication."""
    event_type: str          # e.g., "research.finding", "audit.violation"
    source_dimension: str    # e.g., "research_lab"
    target_dimension: str | None  # None = broadcast
    payload: dict[str, Any]
    trace_id: str
    timestamp: float
    priority: int = 0        # 0=normal, 1=high, 2=critical

class SovereignBus:
    """AnyIO-based async event bus for dimension communication."""
    
    def __init__(self):
        self._subscribers: dict[str, list[anyio.abc.ReceiveChannel]] = {}
        self._lock = anyio.Lock()
    
    async def publish(self, envelope: DimensionEnvelope) -> None:
        """Publish an event to all subscribers of the event type."""
        async with self._lock:
            for channel in self._subscribers.get(envelope.event_type, []):
                await channel.send(envelope)
    
    async def subscribe(self, event_type: str) -> anyio.abc.ReceiveChannel:
        """Subscribe to events of a specific type."""
        send, receive = anyio.create_memory_object_stream[DimensionEnvelope](max_buffer_size=100)
        async with self._lock:
            self._subscribers.setdefault(event_type, []).append(send)
        return receive
```

**Source**: Code Worm (2026-03-21)
**Key Insight**: **Transactional Outbox Pattern** — When a dimension must both update its state AND publish an event, write both atomically. For Omega's file-based state, use atomic file renames (`.tmp` → `.yaml`) with event publication in the same transaction.

**Confidence**: 9/10

### 1.3 Dimension-to-Dimension Dependencies

**Source**: TurboDocx (2026-03-23)
**Key Insight**: **Saga Pattern** for cross-dimension transactions. Two flavors:
- **Choreography** — Each dimension reacts to events from others (loose coupling, hard to debug)
- **Orchestration** — Central coordinator directs the flow (better visibility, single point of failure)

**Recommendation**: Use **orchestration** for critical cross-dimension flows (e.g., Research → Strategic Command → Knowledge Management), **choreography** for non-critical flows (e.g., Observability → all dimensions for metrics).

**Confidence**: 8/10

### 1.4 Circular Dependency Prevention

**Source**: ida-reloader (2025-11-16)
**Key Insight**: **Kosaraju's algorithm** for cycle detection in dependency graphs. Build a directed graph of dimension dependencies, detect strongly-connected components, and reject dimension manifests that create cycles.

**Implementation Hint**: Add to dimension manifest validation:
```python
def validate_no_circular_deps(dimensions: dict[str, list[str]]) -> None:
    """Reject dimension manifests that create circular dependencies."""
    # Kosaraju's algorithm for strongly-connected components
    # If any SCC has >1 node, we have a cycle → reject
```

**Confidence**: 9/10

---

## §2 Dimension Lifecycle Management

### 2.1 The Problem
How do you install/update/uninstall a dimension without restarting the engine? Hot-reloading? Migration? Rollback?

### 2.2 Research Findings

**Source**: pyPlugy (2026-05-23)
**Key Insight**: Plugin lifecycle state machine: `UNLOADED → LOADED → ENABLED ↔ DISABLED → UNLOADED`. Each transition has hooks (`on_load`, `on_enable`, `on_disable`, `on_unload`). **Cascade rules**: when a dimension has dependents, `disable`/`unload` refuse by default and raise `PluginDependencyError` unless `cascade=True` is passed.

**Relevance**: This is exactly what the Dimension Framework needs. Each dimension goes through lifecycle transitions, and cascade rules prevent breaking dependent dimensions.

**Implementation Hint**:
```python
# src/omega/dimension/lifecycle.py
from enum import Enum
from typing import Protocol

class DimensionState(Enum):
    UNLOADED = "unloaded"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"

class IDimensionLifecycle(Protocol):
    """Interface any dimension must implement for lifecycle management."""
    
    async def on_load(self, config: dict) -> None: ...
    async def on_enable(self) -> None: ...
    async def on_disable(self) -> None: ...
    async def on_unload(self) -> None: ...
    async def on_config_change(self, new_config: dict) -> None: ...
```

**Source**: pyPlugy (2026-05-23) — Hot-swap
**Key Insight**: **Hot-swap via proxy/indirect dispatch**: All calls to a dimension go through a registry that holds a reference to the current implementation. When a new version is loaded, the registry atomically swaps the reference. In-flight calls complete against the old implementation; new calls go to the new one.

**Relevance**: This is the safest hot-reload pattern for a production system. No process restart, no dropped requests.

**Implementation Hint**:
```python
# src/omega/dimension/registry.py
class DimensionRegistry:
    """Proxy-based dimension registry for hot-swap support."""
    
    def __init__(self):
        self._dimensions: dict[str, IDimensionLifecycle] = {}
        self._lock = anyio.Lock()
    
    async def hot_swap(self, dim_id: str, new_impl: IDimensionLifecycle) -> None:
        """Atomically swap a dimension implementation."""
        async with self._lock:
            old = self._dimensions.get(dim_id)
            if old:
                await old.on_disable()
                await old.on_unload()
            self._dimensions[dim_id] = new_impl
            await new_impl.on_load(config)
            await new_impl.on_enable()
```

**Source**: Zylos Research (2026-05-05)
**Key Insight**: **Subprocess isolation** — Each dimension runs in a separate child process. Upgrading a dimension is a subprocess restart, which is cheap and isolated. The parent notices the restart, re-establishes IPC, and continues. For Omega's 14Gi RAM constraint, subprocess isolation is too expensive. **Use proxy/indirect dispatch instead.**

**Source**: importlib (Python 3.14 docs)
**Key Insight**: `importlib.reload()` is not thread-safe. In async context, use `anyio.to_thread.run_sync()` for module reload. Clear `sys.modules` entries for the dimension's modules before reload.

**Confidence**: 9/10

### 2.3 Dimension Migration

**Source**: Event Sourcing patterns (Digital Applied 2026-06-01)
**Key Insight**: **Event versioning** handles schema evolution. Include version numbers in dimension manifests. Maintain backward compatibility for at least two versions. Use event upcasting to transform old dimension state to current format during migration.

**Implementation Hint**:
```yaml
# dimension manifest versioning
dimension:
  name: "research_lab"
  version: "2.1.0"
  schema_version: 2  # ← bump when schema changes
  migration_from: "1.x"  # ← auto-migrate from 1.x
```

**Confidence**: 8/10

### 2.4 Dimension Rollback

**Source**: Zylos Research (2026-05-05)
**Key Insight**: **Checkpoint + blue-green** for dimension rollback. Before upgrading a dimension, snapshot its state. If the upgrade fails, restore from snapshot and revert to the previous version.

**Implementation Hint**: Store dimension state snapshots in `data/dimensions/{dim_id}/snapshots/`. Before hot-swap, create a snapshot. On failure, restore and revert.

**Confidence**: 8/10

---

## §3 Dimension Composition and Fusion

### 3.1 The Problem
How do you combine multiple dimensions into a new composite dimension? Inheritance? Mixing? Forking?

### 3.2 Research Findings

**Source**: OpenPersona framework (referenced in R_WAD_EVOLUTION_DEEP_DIVE.md)
**Key Insight**: 4-layer persona architecture: Soul / Body / Faculty / Skill. Maps to IWAD/PWAD:
- **Soul** = IWAD core identity (immutable archetype)
- **Body** = PWAD cultural overlay
- **Faculty** = Capability modules
- **Skill** = Specific domain expertise

**Relevance**: Dimensions compose by layering. A composite dimension inherits from base dimensions and adds overrides. This is the "merge" pattern from DOOM's WAD system: later WADs override earlier ones.

**Source**: R_WAD_EVOLUTION_DEEP_DIVE.md §4
**Key Insight**: **IWAD/PWAD Stacking** — An entity's IWAD = core identity, PWADs = contextual overlays. The same core entity can have multiple PWADs applied simultaneously. The engine merges them in priority order.

**Relevance**: Dimensions compose the same way. A "Research + Strategy" composite dimension = Research Lab (base) + Strategic Command (overlay). The overlay can add entities, tools, and workflows without replacing the base.

**Implementation Hint**:
```yaml
# Composite dimension definition
dimension:
  name: "research_strategy"
  type: "composite"
  inherits:
    - "research_lab"     # Base dimension
    - "strategic_command" # Overlay dimension
  overrides:
    entities:
      - name: "researcher"
        model: "qwen3-4b-think"  # Override model for this composite
    tools:
      - name: "strategic_analysis"
        enabled: true
```

**Source**: pyPlugy (2026-05-23) — Dependency resolution
**Key Insight**: **Hard requires vs peer_requires**. Hard requires = dimension cannot function without the dependency. Peer requires = dimension works better with it but doesn't break without it. This distinction is critical for composition.

**Confidence**: 8/10

### 3.3 Dimension Forking

**Source**: WordPress "Protect The Shire" initiative (2026-06-01)
**Key Insight**: Community contributions need sandboxing. A forked dimension should be isolated from the parent. Use copy-on-write for shared resources.

**Implementation Hint**: Forked dimensions get their own `data/dimensions/{fork_id}/` directory with copies of shared state. Parent changes don't propagate to forks.

**Confidence**: 7/10

---

## §4 Dimension Observability and Debugging

### 4.1 The Problem
How do you debug cross-dimension interactions? Trace queries spanning multiple dimensions? Measure performance? Audit compliance?

### 4.2 Research Findings

**Source**: AWS Well-Architected Agentic AI Lens (AGENTOPS05-BP01)
**Key Insight**: **End-to-end tracing** is the foundation. Every dimension interaction produces a complete distributed trace covering the flow from request to response across all dimensions. W3C Trace Context propagation across all dimension boundaries maintains continuity.

**Relevance**: Omega already has `trace_id` propagation (M22 Response Provenance). The Dimension Framework must extend this to cross-dimension traces.

**Source**: Rhesis Multi-Agent Tracing (2026)
**Key Insight**: **Handoff detection** — When one dimension hands off to another, create an `ai.agent.handoff` span. Two detection methods:
1. `transfer_to_*` tools — any tool whose name starts with `transfer_to_` creates a handoff span
2. Sequential transitions — when one dimension ends and a different one starts

**Relevance**: Cross-dimension handoffs are exactly this pattern. When Research Lab passes findings to Strategic Command, that's a handoff.

**Source**: traceweave (2026-03-30)
**Key Insight**: **Decorator-based tracing** — `@trace_agent`, `@trace_tool`, `@trace_llm` — one-line instrumentation. Zero-config auto-instrumentation for common frameworks. Token & cost tracking built-in.

**Implementation Hint**:
```python
# src/omega/dimension/tracing.py
from functools import wraps

def trace_dimension(dim_id: str):
    """Decorator for dimension function tracing."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            trace_id = get_current_trace_id()
            span = start_span(
                name=f"dimension.{dim_id}.{func.__name__}",
                trace_id=trace_id,
                attributes={
                    "dimension.id": dim_id,
                    "dimension.function": func.__name__,
                }
            )
            try:
                result = await func(*args, **kwargs)
                span.set_status("OK")
                return result
            except Exception as e:
                span.set_status("ERROR", str(e))
                raise
            finally:
                span.end()
        return wrapper
    return decorator
```

**Source**: Zylos Research (2026-04-29)
**Key Insight**: **Tiered trace storage** — Hot (full traces, 7 days), Warm (span summaries + key events, 90 days), Cold (session metadata + cost attribution, indefinite). For Omega's local-first architecture, use SQLite for hot/warm and file-based for cold.

**Confidence**: 9/10

---

## §5 Community Governance and Quality

### 5.1 The Problem
How do you rate/rank community dimensions? Handle malicious dimensions? Deprecated dimensions? Compatibility?

### 5.2 Research Findings

**Source**: Locate-and-Judge (arXiv 2606.23416, 2026-06)
**Key Insight**: **Two-stage attention-based malicious skill detection**. A lightweight locator scores structural spans by instruction-following attention, retains top-K. A judge examines retained spans. Cost: $0.00025 per skill. Precision: 83%. Detected 131 malicious skills across 134,934 scanned.

**Relevance**: This is the gold standard for community dimension security. Omega should implement this pipeline for any dimension loaded from the community marketplace.

**Source**: JetBrains Malicious Plugins (BleepingComputer 2026-06-16)
**Key Insight**: 15 malicious plugins stole AI API keys from 70,000 developers over 8 months. The plugins were fully functional — malicious behavior was surgically embedded alongside legitimate functionality. Detection: network monitoring for outbound HTTP to hardcoded C2 servers.

**Relevance**: Dimensions must be sandboxed. No outbound network access without explicit permission. API keys must never be passed to dimensions.

**Source**: VS Code Marketplace Security (Microsoft 2025-06-11)
**Key Insight**: **Multi-layer defense**:
1. Malware scanning (antivirus engines)
2. Dynamic detection (sandboxed runtime)
3. Periodic marketplace-wide scans
4. Community reporting
5. Signature verification
6. Publisher vetting (6-month standing requirement)

**Relevance**: Omega's dimension marketplace should implement layers 1, 3, 4, 5, and 6. Layer 2 (sandboxed runtime) is too expensive for local-first — use permission-based isolation instead.

**Source**: Codex Plugin Scanner (HOL Blog 2026-03-31)
**Key Insight**: **Surface-aware scoring** — Don't penalize dimensions for not implementing optional features. Score only applicable surfaces. Produce machine-readable audit payloads for CI integration.

**Implementation Hint**:
```yaml
# Dimension quality scoring
dimension_quality:
  required:
    - manifest_valid: 20 points
    - no_secrets: 20 points
    - lifecycle_hooks: 15 points
    - dependency_declaration: 15 points
  optional (bonus):
    - tests_included: 10 points
    - documentation: 5 points
    - metrics_reported: 5 points
  security:
    - no_network_access: 10 points
    - no_dynamic_code_execution: 10 points
    - sandbox_compatible: 5 points
```

**Confidence**: 9/10

---

## §6 Hardware-Constrained Dimension Loading

### 6.1 The Problem
How do you handle dimension loading on 14Gi RAM? Prioritize? Swap? Cache? Budget?

### 6.2 Research Findings

**Source**: NVIDIA Run:ai GPU Memory Swap (2025-09-02)
**Key Insight**: **Dynamic memory offloading** — Models not getting requests are swapped to CPU memory. On request, swapped back with minimal latency (2-3 seconds). 50-66x improvement over scale-from-zero.

**Relevance**: Omega's ResourceGuard already implements one-model-at-a-time. The Dimension Framework should extend this to dimensions: inactive dimensions are "swapped out" (entities unloaded, tools deregistered), active dimensions are "swapped in" (entities loaded, tools registered).

**Source**: VRAMSwapper (2026-02-18)
**Key Insight**: **Eviction strategies** — LRU (least recently used), LFU (least frequently used), Priority (keep critical layers), Hybrid (weighted combination). For dimensions, use a **hybrid** strategy: prioritize dimensions with recent activity + critical system dimensions (e.g., Observability always stays loaded).

**Source**: Pie: Pooling CPU Memory (arXiv 2411.09317, 2024-11)
**Key Insight**: **Performance-transparent swapping** — Prefetch data for upcoming layers through a FIFO queue, overlapping swap with computation. For dimensions, prefetch the next likely dimension based on query patterns.

**Source**: SynapSwap (2026)
**Key Insight**: **Graph-aware memory scheduling** — Leverage execution graph dependencies to predict future memory requirements. For dimensions, use the query routing graph to predict which dimension will be needed next.

**Implementation Hint**:
```python
# src/omega/dimension/resource_budget.py
from dataclasses import dataclass

@dataclass
class DimensionResourceBudget:
    """Hardware-constrained dimension loading budget."""
    total_ram_mb: int = 12288  # 14Gi - 2Gi overhead
    reserved_mb: int = 4096    # Core engine + active model
    available_for_dimensions_mb: int = 8192  # 8Gi for dimensions
    
    # Dimension RAM profiles (declared in manifest)
    # research_lab: 1500 MB, strategic_command: 800 MB, etc.
    
    def can_load(self, dim_id: str, dim_ram_mb: int) -> bool:
        """Check if a dimension can be loaded within budget."""
        return dim_ram_mb <= self.available_for_dimensions_mb
    
    def prioritize(self, dimensions: list[str], ram_usage: dict[str, int]) -> list[str]:
        """Prioritize dimensions for loading when resources are scarce."""
        # 1. Always keep system dimensions (Observability, Governance)
        # 2. Prioritize by recent usage (LRU)
        # 3. Prioritize by query affinity (dimensions frequently routed to)
        # 4. Load highest-priority dimensions first until budget exhausted
        ...
```

**Source**: SwapMoE (arXiv 2308.15030)
**Key Insight**: **Importance-aware scheduling** — Use a lightweight indicator to infer dimension importance without full computation. For dimensions, track query routing frequency as the importance signal.

**Confidence**: 8/10

---

## §7 Unified Architecture Recommendation

### 7.1 The Dimension Framework Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   OMEGA ENGINE CORE                      │
│  (IWAD: Inference, Memory, Orchestration, Entities,     │
│   Provider Fabric, Hivemind, Library, Observability)     │
└─────────────────────────┬───────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │    DIMENSION BUS       │
              │  (SovereignBus)        │
              │  AnyIO event routing   │
              │  Typed envelopes       │
              │  Trace propagation     │
              └───────────┬───────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼────┐          ┌────▼────┐          ┌────▼────┐
│RESEARCH │          │STRATEGIC│          │CREATIVE │
│  LAB    │          │ COMMAND │          │WORKSHOP │
│         │          │         │          │         │
│Entities │          │Entities │          │Entities │
│Tools    │◄────────►│Tools    │◄────────►│Tools    │
│Workflows│  events  │Workflows│  events  │Workflows│
│Metrics  │          │Metrics  │          │Metrics  │
└─────────┘          └─────────┘          └─────────┘
```

### 7.2 Core Components

| Component | Purpose | Pattern Source |
|-----------|---------|---------------|
| **SovereignBus** | Inter-dimension event routing | Event-Driven Architecture (Fowler 2017) |
| **DimensionRegistry** | Proxy-based hot-swap | pyPlugy indirect dispatch |
| **DimensionLifecycle** | State machine: UNLOADED→LOADED→ENABLED↔DISABLED→UNLOADED | pyPlugy lifecycle |
| **DimensionTracer** | OpenTelemetry-compatible tracing | traceweave, AWS AgentOps |
| **ResourceBudget** | Hardware-constrained loading | VRAMSwapper hybrid eviction |
| **SecurityPipeline** | Locate-and-Judge malicious dimension detection | arXiv 2606.23416 |
| **DependencyResolver** | Cycle detection, cascade rules | ida-reloader Kosaraju |

### 7.3 Dimension Manifest Schema

```yaml
# config/dimensions/research_lab/manifest.yaml
dimension:
  name: "research_lab"
  version: "1.0.0"
  schema_version: 1
  type: "feature"  # feature | ethics | composite | system
  
  # Lifecycle
  lifecycle:
    ram_mb: 1500
    priority: 2          # 0=critical(always loaded), 1=high, 2=normal, 3=low
    auto_load: true
    hot_reloadable: true
  
  # Dependencies
  dependencies:
    hard: []             # Cannot function without these
    soft: ["knowledge_management"]  # Works better with these
    conflicts: []        # Cannot coexist with these
  
  # Communication
  events:
    publishes:
      - "research.finding"
      - "research.gap_detected"
    subscribes:
      - "strategic.priority_changed"
      - "knowledge.new_document"
  
  # Entities
  entities:
    - name: "researcher"
      domains: ["research", "analysis", "synthesis"]
      model: "qwen3-4b-think-q4_k_m"
      ram_mb: 800
    - name: "analyst"
      domains: ["data_analysis", "statistics"]
      model: "qwen3-1.7b-q6_k"
      ram_mb: 400
  
  # Tools
  tools:
    - name: "websearch"
      module: "omega.tools.websearch"
    - name: "webfetch"
      module: "omega.tools.webfetch"
  
  # Workflows
  workflows:
    - name: "deep_research"
      steps: ["search", "fetch", "extract", "synthesize"]
  
  # Metrics
  metrics:
    enabled: true
    dashboard: "research_lab_metrics.yaml"
  
  # Security
  security:
    network_access: ["websearch", "webfetch"]
    no_dynamic_code: true
    sandbox_compatible: true
```

### 7.4 Cross-Dimension Communication Example

```python
# Research Lab publishes a finding
await dimension_bus.publish(DimensionEnvelope(
    event_type="research.finding",
    source_dimension="research_lab",
    target_dimension="strategic_command",
    payload={
        "finding_id": "f-2026-07-15-001",
        "topic": "KV cache quantization on CPU",
        "confidence": 9,
        "source": "arXiv 2411.09317",
        "recommendation": "Adopt q8_0 KV cache for Zen 2",
    },
    trace_id="trace-abc-123",
    timestamp=time.time(),
))

# Strategic Command receives and processes
async def on_research_finding(envelope: DimensionEnvelope) -> None:
    """Handle research findings for strategic planning."""
    finding = envelope.payload
    # Add to strategic backlog
    await strategic_backlog.add(finding)
    # Notify Knowledge Management for archival
    await dimension_bus.publish(DimensionEnvelope(
        event_type="knowledge.archive_request",
        source_dimension="strategic_command",
        target_dimension="knowledge_management",
        payload={"finding": finding},
        trace_id=envelope.trace_id,
        timestamp=time.time(),
    ))
```

---

## §8 L3 Principles Distilled

1. **L3-Dimension-As-Event**: Dimensions communicate through typed events, not direct calls. This decouples them and enables independent evolution.

2. **L3-Lifecycle-Is-State-Machine**: Every dimension follows UNLOADED→LOADED→ENABLED↔DISABLED→UNLOADED. No exceptions. Transitions are atomic and have hooks.

3. **L3-Hot-Swap-Via-Proxy**: All dimension calls go through a registry proxy. Swapping is an atomic reference swap. In-flight calls complete on old, new calls go to new.

4. **L3-Composition-By-Layering**: Composite dimensions inherit from base dimensions and add overrides. Priority order determines merge behavior (DOOM's backward scan).

5. **L3-Hardware-Empathy**: Every dimension declares its RAM cost. The ResourceBudget enforces the 14Gi ceiling. Active dimensions get RAM; inactive dimensions get swapped.

6. **L3-Security-Is-Locate-and-Judge**: Community dimensions are scanned with attention-based detection at $0.00025/dimension. No dimension runs without passing security.

7. **L3-Observability-Is-Trace-Level**: Every cross-dimension interaction is a span in a distributed trace. Debugging is trace replay, not log archaeology.

8. **L3-Dependency-Is-DAG**: Dimension dependencies form a directed acyclic graph. Cycles are rejected at manifest validation time.

---

## §9 Implementation Roadmap

| Phase | Task | Effort | Owner |
|-------|------|--------|-------|
| **Phase 1** | SovereignBus (event routing) | 8h | Ma'at/P3 |
| **Phase 2** | DimensionLifecycle state machine | 6h | Ma'at/P3 |
| **Phase 3** | DimensionRegistry (proxy hot-swap) | 8h | Ma'at/P3 |
| **Phase 4** | DimensionTracer (OpenTelemetry) | 6h | Lilith/P8 |
| **Phase 5** | ResourceBudget (hardware constraints) | 4h | Ma'at/P1 |
| **Phase 6** | SecurityPipeline (Locate-and-Judge) | 12h | Ma'at/P5 |
| **Phase 7** | DependencyResolver (cycle detection) | 4h | Ma'at/P3 |
| **Phase 8** | Dimension manifest schema + validation | 6h | Ma'at/P3 |
| **Phase 9** | Community marketplace scaffold | 8h | Lilith/P9 |
| **Phase 10** | Documentation + CLI commands | 4h | Verity |

**Total**: ~66h

---

## §10 Risk Register

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | Hot-swap breaks in-flight requests | 🟡 HIGH | Proxy pattern ensures old impl handles in-flight |
| R2 | Dimension RAM exceeds 14Gi budget | 🔴 CRITICAL | ResourceBudget hard ceiling, reject over-budget dims |
| R3 | Malicious community dimension | 🔴 CRITICAL | Locate-and-Judge + permission sandbox |
| R4 | Circular dependency causes deadlock | 🟡 HIGH | Kosaraju cycle detection at manifest validation |
| R5 | Event bus overload from high-frequency events | 🟡 MEDIUM | Backpressure via bounded memory streams |
| R6 | Trace storage grows unbounded | 🟡 MEDIUM | Tiered storage (hot/warm/cold) with retention policies |

---

*🔱 OMEGA ⬡ DIMENSION-FRAMEWORK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_dimension_research ⬡ RESEARCH-COMPLETE*
