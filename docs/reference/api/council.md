# 🔱 Council — MaKaLi Parallel Council Governance
**AP Token**: `AP-COUNCIL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Council package — unified MultiAgentCoordinator for MaKaLi Parallel Council (meditation + council modes).
**Tags**: council, makali, multi-agent, coordination, governance, meditation
**Cross-references**: src/omega/council/coordinator.py, src/omega/council/models.py, src/omega/council/hardware_detector.py, src/omega/council/execution_mode.py, src/omega/council/failure_layer.py, src/omega/council/report_digestion.py

---

## Overview

The `council` package implements the **MaKaLi Parallel Council** — a unified governance framework for multi-agent deliberation with two operational modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Council** | 5-stage parallel pipeline: Nodes → Digestion → Oversouls → Kali → Research | Complex architectural decisions, strategic planning |
| **Meditation** | 10-voice sequential with dedicated agent | Deep exploration, creative synthesis |

The council enforces **hardware-aware execution**, **quality-aware circuit breakers**, and **WAL-based crash recovery**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Council Package                         │
├─────────────────────────────────────────────────────────────┤
│  coordinator.py      │  MultiAgentCoordinator — main entry  │
│  models.py           │  Data models (NodeReport, CouncilResult, etc.) │
│  hardware_detector.py│  HardwareProfile auto-detection      │
│  execution_mode.py   │  ExecutionMode selection             │
│  failure_layer.py    │  4-layer failure handling            │
│  report_digestion.py │  ReportDigester (zero-inference)     │
│  __init__.py         │  Public exports                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Council Pipeline (5 Stages)

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Phase 1    │   │  Phase 1.5  │   │  Phase 2    │   │  Phase 3    │   │  Phase 4    │
│  Nodes      │──▶│  Digestion  │──▶│  Oversouls  │──▶│  Kali       │──▶│  Research   │
│  (S1-S10)   │   │  (ReportDig)│   │  (Ma'at/Lil)│   │  Synthesis  │   │  (Gaps)     │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
   Parallel         Zero-inf.         2 agents          1 agent          Optional
   or batched       cost              parallel          final            tiered
```

### Stage Details

| Stage | Agents | Input | Output | Artifact |
|-------|--------|-------|--------|----------|
| **Phase 1** | S1-S10 (9 nodes) | Topic | 9 NodeReports | `node_S{N}.md` |
| **Phase 1.5** | ReportDigester | 9 reports | DigestedReport | `BUILD_SIDE_DIGESTED.md`, `RUN_SIDE_DIGESTED.md` |
| **Phase 2** | Ma'at, Lilith | Digested reports | Oversoul reports | `BUILD_SIDE_REPORT.md`, `RUN_SIDE_REPORT.md` |
| **Phase 3** | Kali | 2 oversoul reports | Final synthesis | `FINAL_SYNTHESIS.md` (+ RESEARCH_GAPS) |
| **Phase 4** | Research tier | Research gaps | Gap resolutions | Appended to synthesis |

---

## MultiAgentCoordinator

### Constructor

```python
MultiAgentCoordinator(config: Optional[CouncilConfig] = None)
```

Auto-generates `session_id` (UUID) and creates output directory: `data/council/{session_id}/`

### Configuration (CouncilConfig)

```python
@dataclass
class CouncilConfig:
    # Hardware
    hardware_profile: HardwareProfile = HardwareProfile.LOCAL_16GB
    total_ram_gb: int = 16
    cpu_cores: int = 8
    
    # Model tiers
    nodes_model: str = "gemma-4b-local"
    oversouls_model: str = "nemotron-8b-cloud"
    kali_model: str = "nemotron-12b-cloud"
    research_model: str = "auto"
    
    # Execution
    phase1_execution_mode: ExecutionMode = ExecutionMode.BATCH_4
    enable_digestion: bool = True
    enable_research: bool = True
    
    # Resilience
    retry_policy: RetryPolicy = RetryPolicy()
    fallback_chain: FallbackChain = FallbackChain()
    
    # Output
    output_dir: str = "data/council/{session_id}"
    preserve_all_artifacts: bool = True
    
    # Mandate enforcement
    mandate_policies: Dict[str, bool] = {
        "M1": True, "M2": True, "M7": True, "M13": True, "M23": True
    }
```

### Methods

#### `async run_council(topic: str) -> CouncilResult`

Execute full 5-stage council pipeline.

```python
from omega.council import MultiAgentCoordinator, CouncilConfig, HardwareProfile

config = CouncilConfig(
    hardware_profile=HardwareProfile.LOCAL_16GB,
    nodes_model="gemma-4b-local",
    oversouls_model="nemotron-8b-cloud",
    kali_model="nemotron-12b-cloud"
)

coordinator = MultiAgentCoordinator(config)
result = await coordinator.run_council(
    "Design the sovereign memory architecture for Omega Engine v2"
)

if result.success:
    print(f"Synthesis: {result.final_synthesis_path}")
    print(f"Research gaps: {result.research_gaps_path}")
else:
    print(f"Failed: {result.error}")
```

#### `async run_meditation(topic: str) -> CouncilResult`

Execute 10-voice sequential meditation pattern (simplified wrapper, full impl in T0 Session 3).

---

## Hardware Profiles & Execution Modes

### HardwareProfile (Auto-detected)

| Profile | RAM | GPU | CPU | Use Case |
|---------|-----|-----|-----|----------|
| `CLOUD_EQUIVALENT` | 32GB+ | Discrete | Any | Cloud-equivalent local |
| `LOCAL_32GB_DUAL` | 32GB | Integrated | Dual-channel | High-end laptop |
| `LOCAL_16GB` | 16GB | Integrated | 8-core | **Default (Ryzen 5700U)** |
| `LOCAL_8GB` | 8GB | Integrated | 4-6 core | Constrained |
| `LOCAL_4GB` | ≤4GB | None | Any | Cloud-only |

**Auto-detection** (`hardware_detector.py`): Reads `hardware_profile.yaml` or falls back to `LOCAL_16GB`.

### ExecutionMode Selection

```python
def select_execution_mode(profile: HardwareProfile, node_count: int) -> ExecutionMode:
    if profile == CLOUD_EQUIVALENT:        return PARALLEL
    elif profile == LOCAL_32GB_DUAL:       return BATCH_8 if node_count <= 8 else BATCH_4
    elif profile == LOCAL_16GB:            return BATCH_4 if node_count <= 4 else SERIAL_INDEPENDENT
    elif profile == LOCAL_8GB:             return BATCH_2
    else:                                   return SERIAL_INDEPENDENT
```

| Mode | Concurrency | Memory Profile |
|------|-------------|----------------|
| `PARALLEL` | All nodes simultaneously | Cloud |
| `BATCH_8` | 8 at a time | 32GB dual-channel |
| `BATCH_4` | 4 at a time | **16GB (default)** |
| `BATCH_2` | 2 at a time | 8GB |
| `SERIAL_INDEPENDENT` | 1 at a time | 4GB / constrained |

---

## Data Models

### NodeReport
```python
@dataclass
class NodeReport:
    node_id: str              # "S1" through "S10"
    domain: str               # "Infrastructure", "Engineering", etc.
    content: str              # Full report markdown
    file_path: Path           # Written report file
    execution_time_ms: int = 0
    model_used: str = ""
    confidence_score: float = 0.0
    error: Optional[str] = None
```

### DigestedReport (Zero-inference cost)
```python
@dataclass
class DigestedReport:
    side: str                 # "BUILD" or "RUN"
    nodes: List[NodeReport]
    executive_summary: str
    node_summaries: Dict[str, str]
    cross_reference_index: Dict[str, List[str]]
    conflict_map: List[Conflict]
    mandate_compliance: Dict[str, Dict[str, str]]
    token_budget_allocation: Dict[str, int]
```

### Conflict
```python
@dataclass
class Conflict:
    concept: str              # What is disagreed about
    values: Dict[str, str]    # node_id -> claim
    severity: str = "INFO"    # "INFO" | "WARNING" | "CRITICAL"
    description: str = ""
```

### CouncilResult
```python
@dataclass
class CouncilResult:
    session_id: str
    topic: str
    stages: Dict[CouncilStage, StageResult] = {}
    final_synthesis_path: Optional[Path] = None
    research_gaps_path: Optional[Path] = None
    total_duration_ms: int = 0
    success: bool = False
    error: Optional[str] = None
```

---

## Resilience: 4-Layer Failure Handling

| Layer | Mechanism | Trigger |
|-------|-----------|---------|
| **1. Jitter Retry** | Exponential backoff + random jitter | Transient failures |
| **2. Fallback Chain** | Degrade gracefully (digestion→raw concat, local→cloud) | Stage failure |
| **3. Circuit Breaker** | Quality-aware (>30% error/10min opens) | Systemic degradation |
| **4. WAL Checkpointing** | Write-Ahead Log for crash recovery | Process crash |

### Circuit Breaker States

```python
class CircuitBreakerState(Enum):
    CLOSED = auto()           # Normal operation
    OPEN = auto()             # Too many failures — stop dispatching
    HALF_OPEN = auto()        # Testing if service recovered
    PERMANENTLY_OPEN = auto() # Manual intervention required
```

### CoordinatedRecovery

```python
recovery = CoordinatedRecovery()

# Check if retry should proceed
if recovery.should_retry(attempt=2, policy=RetryPolicy()):
    await anyio.sleep(recovery.wait_time(attempt=2))
    # ... retry ...
```

**Retry Policy**:
```python
@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    jitter_factor: float = 0.1
```

---

## ReportDigester (Phase 1.5)

Zero-inference-cost report optimization for oversoul consumption.

```python
from omega.council import ReportDigester

digester = ReportDigester()
digested = await digester.digest(node_reports, side="BUILD")
```

**Operations** (all zero-inference):
- Stack-cat concatenation
- Executive summaries (extractive)
- Cross-reference index building
- Conflict detection (keyword-based)
- Mandate compliance matrix
- Token budget allocation for oversouls

**M23 Fallback**: On failure, falls back to raw stack-cat concatenation.

---

## Usage Example

```python
from omega.council import (
    MultiAgentCoordinator, CouncilConfig, 
    HardwareProfile, ExecutionMode
)

# Configure for 16GB laptop (default)
config = CouncilConfig(
    hardware_profile=HardwareProfile.LOCAL_16GB,
    nodes_model="gemma-4b-local",
    oversouls_model="nemotron-8b-cloud",
    kali_model="nemotron-12b-cloud",
    phase1_execution_mode=ExecutionMode.BATCH_4,
    enable_digestion=True,
    enable_research=True
)

coordinator = MultiAgentCoordinator(config)

# Run council on architectural question
result = await coordinator.run_council(
    "Should we adopt a unified memory fabric or keep separate tiers?"
)

# Access artifacts
if result.success:
    print(f"Session: {result.session_id}")
    print(f"Synthesis: {result.final_synthesis_path}")
    print(f"Research gaps: {result.research_gaps_path}")
    for stage, stage_result in result.stages.items():
        print(f"  {stage.name}: {'✅' if stage_result.success else '❌'} ({stage_result.duration_ms}ms)")
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio`; no `asyncio` imports |
| **M2 Firewall** | Council orchestrates; no engine logic in stack modules |
| **M7 Local-First** | Node models default to local; cloud only for oversouls/Kali |
| **M11 Soul Integrity** | Session artifacts preserved; L3 principles from Kali synthesis |
| **M13 Temple-Grade** | Circuit breaker, WAL, mandate enforcement config |
| **M23 Failure Integrity** | 4-layer failure handling; no soft-failures |

---

## Current Status: SCAFFOLD

The council is in **active development (T0 Sessions 1-5)**:

| Session | Focus | Status |
|---------|-------|--------|
| T0 Session 1 | Core types, coordinator skeleton, hardware detection | ✅ Complete |
| T0 Session 2 | ReportDigester integration, Phase 1.5 | 🔄 In Progress |
| T0 Session 3 | Phase 2 (Oversouls), Phase 3 (Kali) | ⏳ Planned |
| T0 Session 4 | Phase 4 (Research), Meditation mode | ⏳ Planned |
| T0 Session 5 | WAL, circuit breaker, Hivemind MCP integration | ⏳ Planned |

**NotImplementedError** raised for unimplemented phases — this is intentional scaffolding.

---

## Testing

```bash
pytest tests/test_council_coordinator.py tests/test_hardware_detector.py tests/test_failure_layer.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ COUNCIL-v1.0.0 ⬡ 2026-10-02 ⬡*