<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MaKaLi Parallel Council Architecture — Full Implementation Specification

**Document ID**: SPEC-MAKALI-COUNCIL-v1.0
**Status**: DRAFT — For Implementation
**Author**: Kali (Transcendent Oversoul)
**Date**: 2026-07-19
**Mandates**: M1, M2, M4, M5, M7, M9, M11, M13, M15, M16, M18, M21, M23
**Research Basis**: R-MAKALI-COUNCIL_RESEARCH_SYNTHESIS_20260719.md (35+ sources, 13 gaps resolved)

---

## 1. Architecture Overview

### 1.1 Core Principle: Parallel Independence + Oversoul Distillation + Optimized Synthesis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MAKALI PARALLEL COUNCIL                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │ PILLAR 1 │  │ PILLAR 2 │  │ PILLAR 3 │  │ PILLAR 4 │  │ PILLAR 5 │    │
│   │ (Build)  │  │ (Build)  │  │ (Build)  │  │ (Build)  │  │ (Build)  │    │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│        │             │             │             │             │           │
│        ▼             ▼             ▼             ▼             ▼           │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │              MULTI-AGENT COORDINATOR (State Machine)             │      │
│   │  • Dispatch with timeout tracking                                │      │
│   │  • Collect partial results                                       │      │
│   │  • Invoke oversouls                                              │      │
│   │  • Emit research gaps                                            │      │
│   │  • WAL logging for crash recovery                                │      │
│   │  • Circuit breakers + fallback chains + jittered retry          │      │
│   │  • Thermal management                                            │      │
│   │  • Hivemind event capture                                        │      │
│   └────────────────────────┬────────────────────────────────────────┘      │
│                            │                                                │
│              ┌─────────────┴─────────────┐                                │
│              ▼                           ▼                                │
│       ┌─────────────┐             ┌─────────────┐                         │
│       │   MA'AT     │             │   LILITH    │                         │
│       │ (Build Side)│             │ (Run Side)  │                         │
│       │ 4-5 Reports │             │ 4-5 Reports │                         │
│       │ Confidence  │             │ Confidence  │                         │
│       └──────┬──────┘             └──────┬──────┘                         │
│              │                           │                                 │
│              └─────────────┬─────────────┘                                 │
│                            ▼                                                │
│                   ┌─────────────────┐                                      │
│                   │      KALI       │                                      │
│                   │ (Synthesis)     │                                      │
│                   │ • Read 2 reports│                                      │
│                   │ • Weighted synth│                                      │
│                   │ • Research gaps │                                      │
│                   └────────┬────────┘                                      │
│                            │                                                │
│                            ▼                                                │
│                   ┌─────────────────┐                                      │
│                   │ RESEARCH EXEC   │                                      │
│                   │ (Decoupled)     │                                      │
│                   │ • Smaller model │                                      │
│                   │ • Cloud model   │                                      │
│                   └─────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Unified Coordinator: Two Modes, One Engine

The meditation protocol and MaKaLi council are **not separate systems** — they are two modes of the same unified coordinator sharing WAL, failure handling, thermal management, and profile loading.

```python
class MultiAgentCoordinator:
    """Single coordinator serving both meditation and council modes"""
    
    def __init__(self, profile: CouncilProfile):
        self.profile = profile
        self.wal = WALWriter()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.thermal_monitor = ThermalMonitor()
        self.hivemind = HivemindClient()
    
    async def run_meditation(self, lenses: List[str], topic: str) -> MeditationResult:
        """10-voice sequential, single model load — meditation mode"""
        # Reuses: WAL, circuit breakers, thermal mgmt, profile loading
    
    async def run_council(self, topic: str) -> CouncilResult:
        """Parallel pillars → oversouls → Kali synthesis — council mode"""
        # Reuses: WAL, circuit breakers, thermal mgmt, profile loading
    
    # Shared infrastructure methods
    async def _dispatch_with_failure_handling(self, ...)
    async def _collect_results(self, ...)
    async def _invoke_oversoul(self, ...)
    async def _emit_research_gaps(self, ...)
```

### 1.3 Key Invariants

| Invariant | Description | Enforcement |
|-----------|-------------|-------------|
| **I1: No Inter-Pillar Reads** | Pillars write unique reports. They NEVER read other pillar reports. | Coordinator enforces via file isolation. |
| **I2: Oversouls Read Only Their Side** | Ma'at reads only Build Side (P1-P5). Lilith reads only Run Side (P6-P10). | File naming convention + coordinator validation. |
| **I3: Kali Reads Exactly 2 Files** | Kali reads `maat_consolidated.md` + `lilith_consolidated.md`. Nothing else. | Hardcoded in Kali prompt. |
| **I4: Research Decoupled** | Kali outputs `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH` section. Separate model executes. | Coordinator spawns research task after Kali completes. |
| **I5: Single Model Load Per Tier** | Pillar tier: load 4B once, run all pillars sequentially. Oversoul tier: load 12B once, run both oversouls. | Coordinator manages model lifecycle. |
| **I6: Cognitive Diversity** | Same prompt → different agent identities → complementary blind spots. | Parallel dispatch to specialized agents (P4, Kali, Researcher, Jem, Verity, Maat). |

---

## 2. Hardware Profiles & Model Assignments

### 2.1 Profile Definitions

```yaml
# config/council/profiles/local_16gb.yaml
profile: "local_16gb"
description: "Ryzen 5700U 16GB RAM — Sequential model loading"
hardware:
  total_ram_gb: 16
  reserved_system_gb: 4
  available_for_models_gb: 12
  thermal_limit_c: 85
  tdp_watts: 15

model_tiers:
  pillar:
    model: "qwen3.5-4b-q4_k_m"  # or "gemma-4-e4b-q4_k_m"
    quantization: "Q4_K_M"
    weight_gb: 3.2
    context_window: 32768
    kv_cache_gb_at_32k: 0.4
    max_concurrent: 1  # Sequential only
    temperature: 0.3
    top_p: 0.9
  
  oversoul:
    model: "gemma-4-12b-unified-q4_k_m"  # NEW Jun 2026
    quantization: "Q4_K_M"
    weight_gb: 8.0
    context_window: 65536  # 256K native, use 64K for safety
    kv_cache_gb_at_64k: 1.6
    max_concurrent: 1  # Sequential: Ma'at then Lilith
    temperature: 0.4
    top_p: 0.95
  
  kali:
    # Cloud fallback — no local 12B on 16GB without swap
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
    context_window: 1000000
    temperature: 0.5
    top_p: 0.95
    streaming:
      chunk_timeout_ms: 30000
      total_timeout_ms: 300000
  
  research:
    # Smaller local model or cloud
    provider: "local"
    model: "qwen3.5-4b-q4_k_m"  # Reuse pillar model
    temperature: 0.2
    top_p: 0.9

execution:
  mode: "sequential_with_cooldown"
  pillar_batch_size: 1
  cooldown_seconds: 30  # Thermal management
  max_total_time_minutes: 45
```

```yaml
# config/council/profiles/local_8gb.yaml
profile: "local_8gb"
description: "Constrained hardware — 2B/4B/8B tiers, cloud for Kali"
hardware:
  total_ram_gb: 8
  reserved_system_gb: 3
  available_for_models_gb: 5

model_tiers:
  pillar:
    model: "qwen3.5-2b-q4_k_m"
    weight_gb: 1.8
    context_window: 16384
  
  oversoul:
    model: "gemma-4-e4b-q4_k_m"  # 4B as oversoul
    weight_gb: 3.2
    context_window: 32768
  
  kali:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
  
  research:
    provider: "cloud"
    model: "deepseek-v4-flash-free"

execution:
  mode: "sequential_with_cooldown"
  pillar_batch_size: 1
  cooldown_seconds: 60
```

```yaml
# config/council/profiles/cloud_unconstrained.yaml
profile: "cloud_unconstrained"
description: "No local hardware limits — Nemotron 1M context for all"

model_tiers:
  pillar:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
    max_concurrent: 5  # True parallel
  
  oversoul:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
    max_concurrent: 2
  
  kali:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
  
  research:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"

execution:
  mode: "parallel"
  pillar_batch_size: 5
```

```yaml
# config/council/profiles/hybrid_local_cloud.yaml
profile: "hybrid_local_cloud"
description: "Local pillars + cloud oversouls + cloud Kali"

model_tiers:
  pillar:
    model: "qwen3.5-4b-q4_k_m"
    weight_gb: 3.2
    max_concurrent: 1
  
  oversoul:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
    max_concurrent: 2
  
  kali:
    provider: "opencode-zen"
    model: "nemotron-3-ultra-free"
  
  research:
    provider: "opencode-zen"
    model: "deepseek-v4-flash-free"

execution:
  mode: "batch_2"  # 2 pillars at a time
  pillar_batch_size: 2
```

### 2.2 Active Profile Selection

```python
# src/omega/council/config_loader.py
def load_active_profile() -> CouncilProfile:
    """Load profile from config/council.yaml -> active_profile"""
    # Validates hardware constraints at load time
    # Raises if model weights > available RAM
    # Validates context windows against pillar prompt sizes
```

### 2.3 Profile Validation (M13 Gate Integrity)

```python
# src/omega/council/config_validator.py
def validate_profile(profile: CouncilProfile) -> ValidationResult:
    """Validate profile against hardware constraints"""
    errors = []
    warnings = []
    
    # Check RAM budget
    pillar_weight = profile.model_tiers.pillar.weight_gb
    oversoul_weight = profile.model_tiers.oversoul.weight_gb
    kali_local = profile.model_tiers.kali.get("weight_gb", 0)
    
    if profile.execution.mode == "sequential_with_cooldown":
        peak_ram = max(pillar_weight, oversoul_weight) + 4  # system
    elif profile.execution.mode == "parallel":
        peak_ram = (pillar_weight * profile.execution.pillar_batch_size) + oversoul_weight + 4
    else:
        peak_ram = pillar_weight + oversoul_weight + 4
    
    if peak_ram > profile.hardware.available_for_models_gb + 4:
        errors.append(f"Peak RAM {peak_ram}GB exceeds available {profile.hardware.available_for_models_gb + 4}GB")
    
    # Check context windows
    if profile.model_tiers.pillar.context_window < 16384:
        warnings.append("Pillar context window < 16K may truncate prompts")
    
    if profile.model_tiers.oversoul.context_window < 32768:
        warnings.append("Oversoul context window < 32K may truncate consolidated reports")
    
    return ValidationResult(errors=errors, warnings=warnings)
```

---

## 3. Stage Execution Contracts (All 8 Stages)

### 3.1 Stage Contract Schema

```yaml
# config/council/stage_contracts.yaml
stages:
  0:
    name: "prompt_crafting"
    execution_mode: "subagent"
    assigned_agent: "pillar-P4"
    timeout_seconds: 60
    input_schema: "PromptCraftingInput"
    output_schema: "PromptCraftingOutput"
    mandates_checked: ["M1", "M2", "M7", "M16", "M18"]
    idempotency_key: "council-{session_id}-stage-0"
    checkpoint_path: "data/council/sessions/{session_id}/stage_0.json"
  
  1:
    name: "meditation"
    execution_mode: "subagent"
    assigned_agent: "meditation-agent"  # NOT MaKaLi — dedicated 10-voice agent
    timeout_seconds: 600
    input_schema: "MeditationInput"
    output_schema: "MeditationOutput"
    mandates_checked: ["M1", "M4", "M5", "M7", "M11", "M15", "M18", "M19"]
    idempotency_key: "council-{session_id}-stage-1"
    checkpoint_path: "data/council/sessions/{session_id}/stage_1.json"
  
  2:
    name: "synthesis"
    execution_mode: "subagent"
    assigned_agent: "kali"
    timeout_seconds: 300
    input_schema: "SynthesisInput"
    output_schema: "SynthesisOutput"
    mandates_checked: ["M1", "M2", "M4", "M7", "M13", "M16", "M18", "M23"]
    idempotency_key: "council-{session_id}-stage-2"
    checkpoint_path: "data/council/sessions/{session_id}/stage_2.json"
  
  3:
    name: "research_prompt_crafting"
    execution_mode: "subagent"
    assigned_agent: "pillar-P4"
    timeout_seconds: 60
    input_schema: "ResearchPromptInput"
    output_schema: "ResearchPromptOutput"
    mandates_checked: ["M1", "M2", "M7", "M16", "M18"]
    idempotency_key: "council-{session_id}-stage-3"
    checkpoint_path: "data/council/sessions/{session_id}/stage_3.json"
  
  4:
    name: "research_execution"
    execution_mode: "subagent"
    assigned_agent: "researcher"
    timeout_seconds: 1800
    input_schema: "ResearchExecutionInput"
    output_schema: "ResearchExecutionOutput"
    mandates_checked: ["M1", "M4", "M7", "M13", "M18", "M23"]
    idempotency_key: "council-{session_id}-stage-4"
    checkpoint_path: "data/council/sessions/{session_id}/stage_4.json"
  
  5:
    name: "grounding"
    execution_mode: "subagent"
    assigned_agent: "jem"
    timeout_seconds: 300
    input_schema: "GroundingInput"
    output_schema: "GroundingOutput"
    mandates_checked: ["M1", "M4", "M5", "M11", "M13", "M17", "M18"]
    idempotency_key: "council-{session_id}-stage-5"
    checkpoint_path: "data/council/sessions/{session_id}/stage_5.json"
  
  6:
    name: "gnosis_distillation"
    execution_mode: "subagent"
    assigned_agent: "verity"
    timeout_seconds: 120
    input_schema: "GnosisInput"
    output_schema: "GnosisOutput"
    mandates_checked: ["M1", "M5", "M11", "M13", "M15", "M17", "M21"]
    idempotency_key: "council-{session_id}-stage-6"
    checkpoint_path: "data/council/sessions/{session_id}/stage_6.json"
  
  7:
    name: "integration"
    execution_mode: "subagent"
    assigned_agent: "maat"
    timeout_seconds: 120
    input_schema: "IntegrationInput"
    output_schema: "IntegrationOutput"
    mandates_checked: ["M1", "M4", "M5", "M11", "M12", "M13", "M15", "M21"]
    idempotency_key: "council-{session_id}-stage-7"
    checkpoint_path: "data/council/sessions/{session_id}/stage_7.json"
```

### 3.2 Stage Input/Output Schemas

```python
# src/omega/council/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"

class StageOutput(BaseModel):
    stage_id: int
    status: StageStatus
    output: Dict[str, Any]
    checksum: str  # SHA256 of output
    duration_ms: int
    mandates_verified: List[str]
    trace_id: str
    error: Optional[str] = None

class PipelineState(BaseModel):
    run_id: str
    problem: str
    current_stage: int
    stage_outputs: Dict[int, StageOutput] = {}
    stage_status: Dict[int, StageStatus] = {}
    created_at: float
    updated_at: float
    profile: str
    mode: str  # "meditation" | "council"
```

---

## 4. Coordinator State Machine (THE CRITICAL PIECE)

### 4.1 State Diagram

```
┌─────────────┐
│   IDLE      │ ◄──────────────────────────────────────┐
└──────┬──────┘                                         │
       │                                                │
       ▼                                                │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐ │
│ INITIALIZE  │────►│ DISPATCH    │────►│ COLLECT     │ │
│  • Load     │     │  PILLARS    │     │  RESULTS    │ │
│  • Validate │     │  (Per Mode) │     │  • Timeout  │ │
│  • WAL init │     │             │     │  • Partial  │ │
└─────────────┘     └─────────────┘     └──────┬──────┘ │
                                                │        │
                                                ▼        │
                                         ┌─────────────┐ │
                                         │ INVOKE      │ │
                                         │ OVERSOULS   │ │
                                         │  • Ma'at    │ │
                                         │  • Lilith   │ │
                                         └──────┬──────┘ │
                                                │        │
                                                ▼        │
                                         ┌─────────────┐ │
                                         │ KALI        │ │
                                         │ SYNTHESIS   │ │
                                         └──────┬──────┘ │
                                                │        │
                                                ▼        │
                                         ┌─────────────┐ │
                                         │ EMIT        │ │
                                         │ RESEARCH    │ │
                                         │ GAPS        │ │
                                         └──────┬──────┘ │
                                                │        │
                                                ▼        │
                                         ┌─────────────┐ │
                                         │ COMPLETE    │ │
                                         │  • Write    │ │
                                         │    final    │ │
                                         │  • Close    │ │
                                         │    WAL      │ │
                                         └──────┬──────┘ │
                                                │        │
                                                └────────┘
```

### 4.2 State Definitions

```python
# src/omega/council/coordinator.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List
import anyio
import uuid
import time

class CouncilState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    DISPATCHING_PILLARS = "dispatching_pillars"
    COLLECTING_RESULTS = "collecting_results"
    INVOKING_OVERSOULS = "invoking_oversouls"
    KALI_SYNTHESIS = "kali_synthesis"
    EMITTING_RESEARCH_GAPS = "emitting_research_gaps"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class PillarDispatch:
    pillar_id: str           # "P1", "P2", ... "P10"
    side: str                # "build" or "run"
    task: str                # The pillar's specific prompt
    dispatch_id: str         # UUID for idempotency
    status: str              # "pending" | "dispatched" | "running" | "completed" | "failed" | "timeout"
    model: str               # Model assigned
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result_path: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    result_hash: Optional[str] = None  # For idempotency verification

@dataclass
class OversoulInvocation:
    oversoul: str            # "maat" or "lilith"
    side: str                # "build" or "run"
    input_reports: List[str] # Paths to pillar reports
    status: str              # "pending" | "running" | "completed" | "failed"
    model: str
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result_path: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class CouncilSession:
    session_id: str
    topic: str
    profile: str
    mode: str  # "meditation" | "council"
    state: CouncilState = CouncilState.IDLE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    # Pillar dispatches (10 total: P1-P10)
    pillar_dispatches: Dict[str, PillarDispatch] = field(default_factory=dict)
    
    # Oversoul invocations (2 total: Ma'at, Lilith)
    oversoul_invocations: Dict[str, OversoulInvocation] = field(default_factory=dict)
    
    # Kali synthesis
    kali_synthesis_path: Optional[str] = None
    kali_started_at: Optional[float] = None
    kali_completed_at: Optional[float] = None
    
    # Research gaps
    research_gaps_path: Optional[str] = None
    research_task_id: Optional[str] = None
    
    # WAL
    wal_path: str = ""
    
    # Metrics
    total_pillars: int = 10
    completed_pillars: int = 0
    failed_pillars: int = 0
    partial_results: bool = False
```

### 4.3 WAL (Write-Ahead Log) — ARIES Algorithm

```json
{
  "version": "1.0",
  "session_id": "uuid",
  "entries": [
    {
      "sequence": 1,
      "timestamp": 1721395200.123,
      "operation": "DISPATCH_PILLAR",
      "payload": {
        "pillar_id": "P1",
        "dispatch_id": "uuid",
        "task_hash": "sha256_of_prompt",
        "model": "qwen3.5-4b-q4_k_m"
      },
      "idempotency_key": "council-{session_id}-P1-{dispatch_id}",
      "checksum": "crc32_of_payload"
    },
    {
      "sequence": 2,
      "timestamp": 1721395205.456,
      "operation": "PILLAR_COMPLETED",
      "payload": {
        "pillar_id": "P1",
        "dispatch_id": "uuid",
        "result_path": "data/council/sessions/{session_id}/P1_report.md",
        "result_hash": "sha256_of_report",
        "duration_ms": 5333
      },
      "checksum": "crc32_of_payload"
    },
    {
      "sequence": 3,
      "timestamp": 1721395210.789,
      "operation": "INVOKE_OVERSOUL",
      "payload": {
        "oversoul": "maat",
        "input_reports": ["P1_report.md", "P2_report.md", ...],
        "model": "gemma-4-12b-unified-q4_k_m"
      },
      "checksum": "crc32_of_payload"
    }
  ],
  "checkpoint": {
    "last_completed_sequence": 15,
    "state": "KALI_SYNTHESIS",
    "completed_pillars": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"],
    "failed_pillars": []
  }
}
```

**WAL Implementation** (ARIES):
- Append-only JSONL with LSN (sequence), CRC32 checksums
- `os.replace()` atomic writes (temp → final)
- Periodic checkpoints (every N entries or time interval)
- CLRs (Compensation Log Records) for idempotent undo
- Recovery: Analysis → Redo → Undo (ARIES 3-phase)

### 4.4 Coordinator Core Logic

```python
# src/omega/council/coordinator.py
class MultiAgentCoordinator:
    def __init__(self, profile_name: str):
        self.profile = load_profile(profile_name)
        self.session: Optional[CouncilSession] = None
        self.wal: Optional[WALWriter] = None
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.thermal_monitor = ThermalMonitor()
        self.hivemind = HivemindClient()
    
    async def run_council(self, topic: str) -> CouncilResult:
        """Main entry point — runs full council cycle"""
        self.session = CouncilSession(
            session_id=str(uuid.uuid4()),
            topic=topic,
            profile=self.profile.name,
            mode="council"
        )
        self.wal = WALWriter(self.session.wal_path)
        
        try:
            await self._initialize()
            await self._dispatch_pillars()
            await self._collect_results()
            await self._invoke_oversouls()
            await self._kali_synthesis()
            await self._emit_research_gaps()
            await self._complete()
            return CouncilResult.success(self.session)
        except Exception as e:
            await self._handle_failure(e)
            return CouncilResult.failure(self.session, str(e))
    
    async def run_meditation(self, lenses: List[str], topic: str) -> MeditationResult:
        """Meditation mode — 10-voice sequential, single model load"""
        self.session = CouncilSession(
            session_id=str(uuid.uuid4()),
            topic=topic,
            profile=self.profile.name,
            mode="meditation"
        )
        self.wal = WALWriter(self.session.wal_path)
        
        # Stage 0: Prompt crafting (P4)
        # Stage 1: 10-voice meditation (dedicated agent)
        # Stage 2: Synthesis (Kali)
        # Stage 3-7: Research → Grounding → Gnosis → Integration
        # ... implementation mirrors council but with meditation-specific prompts
```

---

## 5. Failure Handling Specification (4-Layer Stack)

### 5.1 Layer 1: Retry with Full Jitter (AWS Recommended)

```python
# src/omega/council/retry.py
import random
import anyio
from typing import Callable, Tuple, Type

async def retry_with_jitter(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    cap: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """AWS-recommended full jitter backoff: random(0, min(cap, base * 2^attempt))"""
    last_error = None
    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_error = e
            if attempt < max_attempts - 1:
                delay = random.uniform(0, min(cap, base_delay * (2 ** attempt)))
                await anyio.sleep(delay)
    raise last_error
```

### 5.2 Layer 2: Quality-Aware Circuit Breaker

```python
# src/omega/council/circuit_breaker.py
from dataclasses import dataclass
import time

@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: int = 60  # seconds
    expected_exception: type = Exception
    quality_threshold: float = 0.15  # Schema validation failure rate
    
    _failures: int = 0
    _quality_failures: int = 0
    _total_requests: int = 0
    _last_failure_time: float = 0
    _state: str = "closed"  # closed | open | half_open
    
    def record_success(self):
        self._failures = 0
        self._quality_failures = 0
        self._total_requests = 0
        self._state = "closed"
    
    def record_failure(self, is_quality_failure: bool = False):
        self._failures += 1
        self._total_requests += 1
        if is_quality_failure:
            self._quality_failures += 1
        self._last_failure_time = time.time()
        
        # Open on failure count OR quality failure rate
        quality_rate = self._quality_failures / max(self._total_requests, 1)
        if self._failures >= self.failure_threshold or quality_rate >= self.quality_threshold:
            self._state = "open"
    
    @property
    def is_open(self) -> bool:
        if self._state == "open":
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = "half_open"
                return False
            return True
        return False
```

### 5.3 Layer 3: Fallback Chain

```python
# src/omega/council/fallback.py
FALLBACK_CHAIN = [
    ("preferred_model", "primary"),
    ("smaller_model", "fallback_1"),      # e.g., 4B -> 2B
    ("cached_result", "fallback_2"),      # Previous successful run
    ("empty_report", "fallback_3")        # Minimal structured output
]

async def execute_with_fallbacks(pillar_id: str, prompt: str, profile) -> PillarResult:
    for model_name, fallback_type in FALLBACK_CHAIN:
        model = get_model(model_name) if model_name else None
        try:
            if model is None:
                return await get_cached_or_empty(pillar_id)
            result = await call_model(model, prompt)
            return result
        except Exception:
            continue
    raise AllFallbacksExhausted()
```

### 5.4 Layer 4: State Checkpointing + WAL Recovery

```python
# src/omega/council/checkpoint.py
async def checkpoint_session(session: CouncilSession):
    """Write atomic checkpoint with WAL sync"""
    checkpoint = {
        "session_id": session.session_id,
        "state": session.state.value,
        "completed_pillars": [p for p, d in session.pillar_dispatches.items() if d.status == "completed"],
        "failed_pillars": [p for p, d in session.pillar_dispatches.items() if d.status in ("failed", "timeout")],
        "oversoul_status": {k: v.status for k, v in session.oversoul_invocations.items()},
        "kali_status": "completed" if session.kali_synthesis_path else "pending",
        "timestamp": time.time()
    }
    # Atomic write via WAL
    await session.wal.checkpoint(checkpoint)

async def recover_session(session_id: str) -> CouncilSession:
    """Recover council session from WAL using ARIES"""
    wal = WALReader(f"data/council/sessions/{session_id}/wal.jsonl")
    entries = wal.read_all()
    
    # Phase 1: Analysis — find last checkpoint
    last_checkpoint = None
    for entry in entries:
        if entry["operation"] == "CHECKPOINT":
            last_checkpoint = entry["payload"]
    
    # Phase 2: Redo — replay from checkpoint
    session = CouncilSession(session_id=session_id, topic="", profile="")
    if last_checkpoint:
        session.state = CouncilState(last_checkpoint["state"])
        # Reconstruct completed work
        for entry in entries:
            if entry["sequence"] > last_checkpoint["last_completed_sequence"]:
                await replay_entry(session, entry)
    
    # Phase 3: Undo — handled by CLRs in WAL
    return session
```

### 5.5 Partial Results Protocol

```python
async def _collect_results(self):
    # ... existing logic ...
    
    # Mark session as partial if any failures
    self.session.partial_results = self.session.failed_pillars > 0
    
    # For oversoul: only pass COMPLETED pillar reports
    # For Kali: pass oversoul reports (which already note missing pillars)
    
    # WAL records which pillars failed and why
    await self.wal.write_entry(
        operation="PARTIAL_RESULTS",
        payload={
            "completed": [p for p, d in self.session.pillar_dispatches.items() if d.status == "completed"],
            "failed": [p for p, d in self.session.pillar_dispatches.items() if d.status in ("failed", "timeout")],
            "failed_details": {p: d.error for p, d in self.session.pillar_dispatches.items() if d.status in ("failed", "timeout")}
        }
    )
```

---

## 6. Quality Gates (Graduated Enforcement Model)

### 6.1 Gate Matrix

| Stage | Type | Tools | Blocking | Mandates |
|-------|------|-------|----------|----------|
| Pre-commit | Informational | TruffleHog, lint | Notification only | M8, M23 |
| Build | Enforcing | SAST, deps, contract tests | Critical/High | M9, M13, M21 |
| Container | Enforcing | Trivy, SBOM, cosign | CVEs > threshold | M13 |
| Staging | Informational | DAST, pentest | Ticket creation | M13 |
| Production | Enforcing | Runtime protection, WAF | Block/quarantine | M13, M23 |

### 6.2 Pre-Commit vs CI

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    hooks:
      - id: trufflehog
        stages: [commit]
  - repo: local
    hooks:
      - id: mandate-check
        name: "Mandate Compliance (M1, M2, M7, M13, M23)"
        entry: python -m src.omega.council.mandate_check
        language: system
        stages: [commit]
        always_run: true
```

```python
# src/omega/council/mandate_check.py
"""Pre-commit mandate validation — convenience only. CI is enforcement."""
def check_mandates(file_path: str) -> List[Violation]:
    violations = []
    # M1: No asyncio imports
    # M2: No config.wads imports in src/omega
    # M7: No cloud-first language
    # M13: Temple-Grade patterns
    # M23: No bare except:
    return violations
```

### 6.3 Policy-as-Code (OPA/Rego)

```rego
# policy/mandates.rego
package mandates

# M1 AnyIO Absolute
deny[msg] {
    input.mandates[_] == "M1"
    not input.uses_anyio
    msg := "M1 violation: asyncio detected, must use AnyIO"
}

# M2 Engine-Stack Firewall
deny[msg] {
    input.mandates[_] == "M2"
    input.imports[_] = "config.wads.*"
    msg := "M2 violation: core engine imports WAD config"
}

# M7 Local-First
deny[msg] {
    input.mandates[_] == "M7"
    input.provider_priority[_] = "cloud"
    msg := "M7 violation: cloud-first priority detected"
}

# M13 Temple-Grade
deny[msg] {
    input.mandates[_] == "M13"
    not input.has_contract_tests
    msg := "M13 violation: missing isinstance contract tests"
}

# M23 Failure Integrity
deny[msg] {
    input.mandates[_] == "M23"
    input.has_bare_except
    msg := "M23 violation: bare except: clause"
}
```

---

## 7. Sovereign Search Tier Policies

### 7.1 Query Classification & Routing

```yaml
# config/council/search_policy.yaml
search_policy:
  architecture_patterns:
    tiers: [T0, T1, T3]  # Local cache → websearch → Firecrawl
    max_results: 10
    validation: "cross_reference_2_sources"
    local_first: true
  
  benchmarks:
    tiers: [T0, T1, T4]  # Local → websearch → Exa
    max_results: 5
    validation: "require_numeric_data"
    local_first: true
  
  failure_modes:
    tiers: [T0, T1, T3]
    max_results: 8
    validation: "require_reproduction_steps"
    local_first: true
  
  heritage_vetting:
    tiers: [T0, T1, T3]
    max_results: 8
    validation: "require_primary_source"
    local_first: true
  
  mandate_compliance:
    tiers: [T0, T1]  # Local KB only
    max_results: 5
    validation: "require_mandate_text"
    local_first: true
```

### 7.2 Tier Definitions

| Tier | Tool | Cost | Use Case |
|------|------|------|----------|
| T0 | Local cache (`.firecrawl/`) | Free | Previously fetched |
| T1 | `websearch` / `webfetch` | Free | General web |
| T2 | `searxng_searxng_search` | Free | Semantic/neural |
| T3 | `firecrawl_firecrawl_scrape` | Credits | Full-page scrape |
| T4 | `omega-hub_sovereign_search` | API (Exa) | High-precision |
| T5 | `sieve research` | Local-first | Full pipeline |

---

## 8. Agent Specialization for Pipeline Stages

### 8.1 Stage → Agent Mapping

| Stage | Cognitive Role | Best Agent | Rationale |
|-------|----------------|------------|-----------|
| 0 Prompt Crafting | Bridge/Communication | Pillar P4 (Integration) | MCP, protocol expertise |
| 1 Meditation | 10-voice dialectic | `meditation-agent` (dedicated) | Not MaKaLi — different cognitive mode |
| 2 Synthesis | Architecture/Decision | Kali (oversight) | Transcendent view |
| 3 Research Prompts | Query decomposition | Pillar P4 | Bridge/communication |
| 4 Research | Deep search + verification | `researcher` (Sovereign Search) | Deep research specialist |
| 5 Grounding | Synthesis + verification | `jem` (synthesizer) | Lattice reasoning |
| 6 Gnosis | L1→L2→L3 distillation | `verity` (compliance + scribe) | Mandate audit + soul distillation |
| 7 Integration | PIVOT_LOG + workbench | `maat` (build-side governance) | P1-P5 oversight |

### 8.2 Cognitive Diversity Principle

**Critical**: Same entity ≠ same cognitive filter. Parallel dispatch to complementary identities reveals blind spots (L3-Entity-Identity-Is-Decomposition-Filter).

```python
# Example: For critical decisions, run context through 2+ entities
async def critical_decision(topic: str) -> Decision:
    roc_result = await task("roc_racoon", f"Mine legacy patterns for: {topic}")
    kali_result = await task("kali", f"Strategic assessment for: {topic}")
    return await synthesize(roc_result, kali_result)
```

---

## 9. Dry-Run Mocking Strategies

### 9.1 Mock Contract

```python
# src/omega/council/dry_run.py
DRY_RUN_MOCKS = {
    "meditate": lambda: canned_10_voice_output,
    "sovereign_search": lambda q: cached_fixtures[q.category],
    "file_write": lambda p, c: write_to_tmp(p, c),
    "quality_gates": lambda: hardcoded_pass,
    "hivemind_handoff": lambda: mock_packet_id,
    "model_call": lambda m, p: canned_model_response[m],
}

class DryRunMode:
    """Mock external dependencies only. Never mock internal logic."""
    
    def __init__(self):
        self.mocks = DRY_RUN_MOCKS
    
    async def execute_stage(self, stage_id: int, input_data: dict) -> StageOutput:
        if stage_id in self.mocks:
            return StageOutput(
                stage_id=stage_id,
                status=StageStatus.COMPLETED,
                output=self.mocks[stage_id](),
                checksum="dry_run_mock",
                duration_ms=0,
                mandates_verified=[],
                trace_id="dry_run"
            )
        # For non-mocked stages, execute real code with mocked externals
        return await real_execution_with_mocked_externals(stage_id, input_data)
```

### 9.2 Rule: Mock Boundaries, Not Internals

| Mock | Don't Mock |
|------|------------|
| API calls (LLM, search) | Circuit breaker logic |
| CLI subprocesses | WAL write logic |
| Time (`time.time()`) | State machine transitions |
| File system (tmp dir) | Mandate validation |
| Hivemind handoffs | Quality gate evaluation |

---

## 10. Observability & Tracing (OpenTelemetry GenAI)

### 10.1 Required Spans

```python
# src/omega/council/tracing.py
from opentelemetry import trace
from opentelemetry.trace import SpanKind

# Span names (GenAI semconv)
SPAN_AGENT_RUN = "agent.run"
SPAN_MODEL_CALL = "model.call"
SPAN_TOOL_CALL = "tool.call"
SPAN_HANDOFF_TRANSFER = "handoff.transfer"

# Required attributes
REQUIRED_ATTRIBUTES = {
    SPAN_AGENT_RUN: ["gen_ai.agent.name", "gen_ai.agent.id"],
    SPAN_MODEL_CALL: ["gen_ai.request.model", "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens", "gen_ai.response.finish_reason"],
    SPAN_TOOL_CALL: ["gen_ai.tool.name", "gen_ai.tool.input", "gen_ai.tool.output"],
    SPAN_HANDOFF_TRANSFER: ["gen_ai.handoff.from_agent", "gen_ai.handoff.to_agent", "gen_ai.handoff.reason"],
}
```

### 10.2 Trace Correlation

```python
# Single trace_id across all stages via context propagation
from opentelemetry.context import Context
from opentelemetry.propagate import inject, extract

def get_trace_context() -> Context:
    """Extract or create trace context for current operation"""
    # Propagate via Hivemind handoff packets
    return extract(hivemind_packet.headers) if hivemind_packet else Context()

async def traced_operation(operation_name: str, func: Callable, attributes: dict):
    tracer = trace.get_tracer("makali-council")
    with tracer.start_as_current_span(operation_name, kind=SpanKind.INTERNAL, attributes=attributes) as span:
        try:
            result = await func()
            span.set_status(Status(StatusCode.OK))
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

### 10.3 Dashboard Metrics

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Token usage (total, per stage) | `gen_ai.usage.*` | > budget |
| Latency P50/P99 | `span.duration` | P99 > 30s |
| Error rate | `span.status` | > 5% |
| Handoff success rate | `handoff.transfer` | < 95% |
| Circuit breaker state | Custom metric | OPEN > 1min |
| Thermal headroom | `omega-hub_get_hardware_stats` | < 5°C |

---

## 11. Hivemind Integration for Stage Outputs

### 11.1 Auto-Capture

```python
# src/omega/council/hivemind_integration.py
class HivemindClient:
    def __init__(self):
        self.mcp = HivemindMCPClient()
    
    async def capture_stage_output(self, session_id: str, stage_id: int, output: StageOutput):
        """Auto-capture every stage output to persistent event log"""
        await self.mcp.publish(
            channel="council-stages",
            event={
                "session_id": session_id,
                "stage_id": stage_id,
                "stage_name": STAGE_NAMES[stage_id],
                "output": output.output,
                "checksum": output.checksum,
                "mandates_verified": output.mandates_verified,
                "trace_id": output.trace_id,
                "timestamp": time.time()
            }
        )
    
    async def semantic_search(self, query: str, session_id: Optional[str] = None) -> List[Event]:
        """Query events by meaning with vector embeddings"""
        return await self.mcp.query(
            channel="council-stages",
            query=query,
            filters={"session_id": session_id} if session_id else {}
        )
    
    async def create_handoff(self, target_entity: str, task: str, context: str) -> str:
        """Create structured handoff packet with versioning"""
        return await self.mcp.submit_handoff(
            target_channel="opencode",
            target_entity=target_entity,
            source_channel="opencode",
            source_entity="kali",
            task=task,
            context=context,
            priority=1,
            metadata={"supersedes": []}  # For versioning
        )
```

### 11.2 Cross-Session Learning

```python
async def get_prior_context(topic: str) -> List[PriorRun]:
    """Query Hivemind for relevant prior council runs"""
    events = await hivemind.semantic_search(
        query=f"Council topic similar to: {topic}",
        session_id=None  # Cross-session
    )
    return [
        PriorRun(
            session_id=e.session_id,
            topic=e.topic,
            verdict=e.output.get("unified_verdict"),
            gaps=e.output.get("research_gaps"),
            confidence=e.output.get("confidence")
        )
        for e in events
    ]
```

---

## 12. Research Gap Unification Schema

### 12.1 Unified Gap Schema

```yaml
# data/council/sessions/{session_id}/research_gaps.yaml
gap:
  id: "gap-<uuid>"
  source: "pipeline|council|meditation"
  stage: 0-7
  question: "Specific research question"
  context: "Why this matters for the verdict"
  category: "architecture|benchmark|failure_mode|heritage|compliance"
  priority: "P0|P1|P2|P3"
  recommended_approach: "websearch|benchmark|code_analysis|expert_consult"
  suggested_model: "qwen3.5-4b|gemma-4-12b|nemotron-3-ultra"
  success_criteria: "Measurable outcome"
  status: "open|in_progress|resolved|deferred"
  supersedes: []  # versioning chain
  trace_id: "links to originating run"
```

### 12.2 Gap Lifecycle

```python
class GapManager:
    async def emit_gaps(self, kali_synthesis: str) -> List[Gap]:
        """Parse Kali's REMAINING_GAPS_AND_RECOMMENDED_RESEARCH section"""
        gaps = parse_gaps_section(kali_synthesis)
        
        for gap in gaps:
            gap.id = f"gap-{uuid.uuid4()}"
            gap.trace_id = self.session.trace_id
            gap.status = "open"
            await self.persist(gap)
            
            # Spawn research task via Hivemind
            await self.hivemind.create_handoff(
                target_entity="researcher",
                task=f"Execute research gap: {gap.question}",
                context=f"Gap ID: {gap.id}\nContext: {gap.context}\nApproach: {gap.recommended_approach}"
            )
        
        return gaps
    
    async def resolve_gap(self, gap_id: str, resolution: str):
        gap = await self.get(gap_id)
        gap.status = "resolved"
        gap.resolution = resolution
        gap.resolved_at = time.time()
        await self.persist(gap)
        
        # Create superseding gap if needed
        if resolution.requires_followup:
            new_gap = Gap(
                id=f"gap-{uuid.uuid4()}",
                supersedes=[gap_id],
                question=resolution.followup_question,
                # ...
            )
            await self.persist(new_gap)
```

---

## 13. Pillar Definitions (Updated with Research Findings)

### 13.1 Pillar Registry with Confidence Scoring

```yaml
# config/council/pillars.yaml
pillars:
  P1:
    name: "Infrastructure"
    side: "build"
    archetype: "SysAdmin — Environment Hardening"
    prompt_template: |
      You are Pillar P1: Infrastructure — SysAdmin, Environment Hardening.
      
      Council Topic: {topic}
      
      Your mandate: Assess the infrastructure implications of this topic.
      Consider: deployment, containers, Podman, systemd, hardware constraints,
      thermal limits, resource quotas, scaling, disaster recovery.
      
      Apply these mandates as lenses:
      - M1: AnyIO Absolute — all async must use AnyIO
      - M6: Podman Sovereignty — UserNS=keep-id + User=1000, no :U flag
      - M16: Modularization — no hardcoded paths in src/omega/
      - M18: Token Efficiency — be precise, not verbose
      
      Output a focused report with:
      1. Infrastructure assessment (3-5 key points)
      2. Specific recommendations with owners
      3. Risks and mitigations
      4. Confidence score (0.0-1.0) for each recommendation
      
      Be decisive. No hedging.

  P2:
    name: "Persistence"
    side: "build"
    archetype: "DataStore — Vector & Memory Management"
    prompt_template: |
      You are Pillar P2: Persistence — DataStore, Vector & Memory Management.
      
      Council Topic: {topic}
      
      Your mandate: Assess data persistence, vector storage, memory management.
      Consider: Qdrant, sqlite-vec, WAL, ACID, backup/restore, migration,
      schema evolution, performance, quantization, indexing.
      
      Apply these mandates:
      - M9: Error Integrity — typed, traceable errors
      - M12: Queue Integrity — atomic writes, no orphan files
      - M20: SomaticState Serialization — llama_copy_state_data via anyio.to_thread
      - M21: Gate Integrity — contract tests for typed returns
      
      Output focused report with recommendations, risks, confidence scores.

  P3:
    name: "Engineering"
    side: "build"
    archetype: "BuildMaster — Implementation & Hardening"
    prompt_template: |
      You are Pillar P3: Engineering — BuildMaster, Implementation & Hardening.
      
      Council Topic: {topic}
      
      Your mandate: Assess implementation approach, code quality, testing,
      CI/CD, hardening, technical debt, refactoring priorities.
      
      Apply these mandates:
      - M4: Sequentiality — Plan → Verify → Execute
      - M13: Temple-Grade — T1-T11 gates
      - M19: Adversarial Alchemy — mine weaknesses for advantages
      - M21: Gate Integrity — isinstance contract tests
      
      Output focused report with recommendations, risks, confidence scores.

  P4:
    name: "Integration"
    side: "build"
    archetype: "Bridge — MCP & Communication"
    prompt_template: |
      You are Pillar P4: Integration — Bridge, MCP & Communication.
      
      Council Topic: {topic}
      
      Your mandate: Assess MCP servers, API boundaries, protocol design,
      inter-service communication, authentication, versioning.
      
      Apply these mandates:
      - M2: Engine-Stack Firewall — Core vs WAD separation
      - M3: Iris Constant — Iris is messenger, not Pillar
      - M16: Modularization — platform integration via MCP Hub/CLI
      - M22: Response Provenance — log actual provider_name
      
      Output focused report with recommendations, risks, confidence scores.

  P5:
    name: "Governance"
    side: "build"
    archetype: "Sentinel — Mandate Enforcement"
    prompt_template: |
      You are Pillar P5: Governance — Sentinel, Mandate Enforcement.
      
      Council Topic: {topic}
      
      Your mandate: Assess mandate compliance, security, audit, policy,
      sovereignty boundaries, heritage vetting.
      
      Apply these mandates:
      - M5: Gnosis Preservation — L1→L2→L3 distillation
      - M10: Fleet Integrity — 14 agent cap, slot-based
      - M14: Heritage Vetting — [id-soft:] tags require vet records
      - M15: Sovereign Continuity — session anchors, hydration
      - M23: Failure Integrity — no soft failures
      
      Output focused report with recommendations, risks, confidence scores.

  P6:
    name: "Cognition"
    side: "run"
    archetype: "ModelGate — Provider Routing"
    prompt_template: |
      You are Pillar P6: Cognition — Vision Specialist, ModelGate, Provider Routing.
      
      Council Topic: {topic}
      
      Your mandate: Assess model routing, provider fabric, inference optimization,
      local-first strategy, fallback chains, streaming, context management.
      
      Apply these mandates:
      - M1: AnyIO Absolute
      - M7: Local-First — local inference primary, cloud fallback
      - M17: Cognitive Integrity — verify memory/gnosis consistency
      - M20: SomaticState Serialization
      - M22: Response Provenance
      
      Output focused report with recommendations, risks, confidence scores.

  P7:
    name: "Context"
    side: "run"
    archetype: "Memory & Soul Evolution"
    prompt_template: |
      You are Pillar P7: Context — Memory & Soul Evolution.
      
      Council Topic: {topic}
      
      Your mandate: Assess context management, memory persistence, soul evolution,
      cross-session continuity, handoff protocols, knowledge metabolism.
      
      Apply these mandates:
      - M5: Gnosis Preservation
      - M11: Soul Integrity — L1→L2→L3 to proposed_lessons.yaml
      - M12: Queue Integrity
      - M15: Sovereign Continuity
      - M17: Cognitive Integrity
      
      Output focused report with recommendations, risks, confidence scores.

  P8:
    name: "Observability"
    side: "run"
    archetype: "WatchTower — Observability & Tracing"
    prompt_template: |
      You are Pillar P8: Observability — WatchTower, Observability & Tracing.
      
      Council Topic: {topic}
      
      Your mandate: Assess tracing, metrics, logging, forensic logging,
      alerting, dashboards, distributed tracing, performance profiling.
      
      Apply these mandates:
      - M8: Zero Telemetry — no external phone-home
      - M9: Error Integrity — structured errors with trace_id
      - M13: Temple-Grade T9 — structured logging
      - M21: Gate Integrity
      - M23: Failure Integrity
      
      Output focused report with recommendations, risks, confidence scores.

  P9:
    name: "Orchestration"
    side: "run"
    archetype: "Link — Agent Handoff & Delegation"
    prompt_template: |
      You are Pillar P9: Orchestration — Link, Agent Handoff & Delegation.
      
      Council Topic: {topic}
      
      Your mandate: Assess agent handoff protocols, delegation patterns,
      Hivemind coordination, workspace locks, task routing, A2A communication.
      
      Apply these mandates:
      - M4: Sequentiality
      - M9: Error Integrity
      - M10: Fleet Integrity
      - M12: Queue Integrity
      - M15: Sovereign Continuity
      
      Output focused report with recommendations, risks, confidence scores.

  P10:
    name: "Validation"
    side: "run"
    archetype: "Verifier — Stress Testing & QA"
    prompt_template: |
      You are Pillar P10: Validation — Verifier, Stress Testing & QA.
      
      Council Topic: {topic}
      
      Your mandate: Assess testing strategy, chaos engineering, stress testing,
      contract tests, property-based testing, regression prevention.
      
      Apply these mandates:
      - M9: Error Integrity
      - M13: Temple-Grade T3 (coverage ≥80%), T8 (resilience)
      - M19: Adversarial Alchemy
      - M21: Gate Integrity — contract tests
      - M23: Failure Integrity
      
      Output focused report with recommendations, risks, confidence scores.
```

---

## 14. Meditation Mode Specification

### 14.1 10-Voice Protocol (Dedicated Agent)

```python
# src/omega/council/meditation.py
class MeditationAgent:
    """Dedicated agent for 10-voice meditation protocol — NOT MaKaLi Council"""
    
    VOICES = [
        ("engineering_excellence", "Engineering Excellence — precision, craftsmanship"),
        ("sovereign_boundary", "Sovereign Boundary — M2 firewall, M8 zero telemetry"),
        ("cognitive_integrity", "Cognitive Integrity — M17 memory/gnosis consistency"),
        ("adversarial_alchemy", "Adversarial Alchemy — M19 weakness→advantage"),
        ("local_first", "Local-First — M7 local inference primary"),
        ("modular_portability", "Modular Portability — M16 no hardcoded paths"),
        ("token_efficiency", "Token Efficiency — M18 precision over brevity"),
        ("failure_integrity", "Failure Integrity — M23 no soft failures"),
        ("continuity", "Continuity — M11 soul, M15 session anchors"),
        ("kali_synthesis", "Kali Synthesis — transcendent verdict"),
    ]
    
    async def run(self, lenses: List[str], topic: str) -> MeditationResult:
        """Sequential 10-voice immersion with mandatory dissent"""
        results = []
        for voice_id, (lens, description) in enumerate(self.VOICES):
            if lenses and lens not in lenses:
                continue
            
            # Single model load for entire meditation
            prompt = self._build_voice_prompt(lens, description, topic, results)
            response = await self._call_model(prompt)
            
            # Mandatory dissent at each voice
            dissent = self._extract_dissent(response)
            
            results.append(VoiceResult(
                voice=lens,
                output=response,
                dissent=dissent,
                confidence=self._extract_confidence(response)
            ))
            
            # Cooldown for thermal management
            await anyio.sleep(5)
        
        return MeditationResult(
            voices=results,
            synthesis=await self._synthesize(results),
            trace_id=self.trace_id
        )
```

---

## 15. Implementation Phases (T0 — 5 Sessions)

| Session | Focus | Deliverable |
|---------|-------|-------------|
| 1 | **Unified Coordinator Core** | `MultiAgentCoordinator` with WAL (ARIES), circuit breakers (quality-aware), thermal mgmt, profile loader, Hivemind client |
| 2 | **Stage Contracts + Failure Layer** | All 8 stage contracts, 4-layer failure handling (retry+jitter, circuit breaker, fallback, checkpointing), atomic WAL writes |
| 3 | **Meditation Mode** | `run_meditation()` — 10-voice sequential, single model load, dedicated agent |
| 4 | **Council Mode** | `run_council()` — parallel pillars → oversouls → Kali synthesis, confidence-weighted consensus |
| 5 | **Integration + Gates** | Hivemind capture, mandate Rego policies, quality gates (graduated), OpenTelemetry tracing, dry-run mode |

---

## 16. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Coordinator prompt too vague → inconsistent behavior | High | High | Invest heavily in prompt engineering; test with 5+ topics |
| 4B model context overflow on pillar prompts | Medium | High | Session 1 benchmark must measure actual token usage |
| Thermal throttling breaks sequential timing | Medium | Medium | Thermal check before each dispatch; configurable cooldown |
| Oversoul confidence uncalibrated → worse than uniform | Medium | High | Calibration run in Session 4; fallback to uniform weighting |
| WAL replay misses side effects (file writes, API calls) | Low | High | Idempotency keys for ALL operations; document limitations |
| Research task never completes (handoff lost) | Low | Medium | Hivemind handoff with timeout; Kali synthesis includes gaps regardless |
| Circular dependency (Kali→MaKaLi→Kali) | N/A | N/A | **Resolved**: Unified coordinator with two modes |

---

## 17. Mandate Compliance Matrix

| Mandate | Council Compliance |
|---------|-------------------|
| **M1 AnyIO Absolute** | All async uses AnyIO; `anyio.to_thread.run_sync` for blocking calls |
| **M2 Engine-Stack Firewall** | Pillar prompts reference mandates, not stack entities; config-driven |
| **M3 Iris Constant** | Iris not a pillar; P4 Integration covers MCP |
| **M4 Sequentiality** | Coordinator enforces Plan→Verify→Execute via state machine |
| **M5 Gnosis Preservation** | Stage 6 (verity) → L1→L2→L3 to proposed_lessons.yaml |
| **M6 Podman Sovereignty** | P1 Infrastructure prompt includes M6 |
| **M7 Local-First** | Profiles prioritize local models; cloud only for Kali/fallback |
| **M8 Zero Telemetry** | No external calls in coordinator; WAL local only |
| **M9 Error Integrity** | Typed exceptions, trace_id in WAL, no bare except |
| **M10 Fleet Integrity** | 10 fixed pillars (P1-P10); no dynamic agent creation |
| **M11 Soul Integrity** | Stage 6 feeds L1→L2→L3 pipeline |
| **M12 Queue Integrity** | WAL = atomic contract; no orphan files |
| **M13 Temple-Grade** | All T1-T11 gates tested in CI |
| **M14 Heritage Vetting** | P5 Governance prompt includes M14 |
| **M15 Sovereign Continuity** | WAL enables full session recovery |
| **M16 Modularization** | No hardcoded paths; config-driven profiles |
| **M17 Cognitive Integrity** | P7 Context prompt includes M17 |
| **M18 Token Efficiency** | Prompts structured for precision; confidence tables over prose |
| **M19 Adversarial Alchemy** | Failure patterns → circuit breaker/fallback as features |
| **M20 SomaticState** | P2 Persistence prompt includes M20 |
| **M21 Gate Integrity** | Contract tests for all public APIs |
| **M22 Response Provenance** | P6 Cognition prompt includes M22 |
| **M23 Failure Integrity** | No soft failures; circuit breaker = hard stop with logging |

---

## 18. Appendix: Key Research Sources

| Gap | Primary Sources |
|-----|-----------------|
| 1. Circular Dependency | RecursiveMAS (arXiv:2604.25917), Microsoft Learn 2026, LangGraph v1.0 |
| 2. Stage Contracts | Codex CLI v2 (Apr 2026), OpenAI Agents SDK (Jun 2026), LangGraph interrupts |
| 3. Failure Handling | miaoquai.com (95+ days prod), Supergood Solutions, AgentMarketCap |
| 4. WAL/ARIES | ndlab.blog (Jul 2026), Grafana Loki, PostgreSQL ARIES |
| 5. Quality Gates | SonarQube, Adaptive Enforcement Lab, Decryption Digest |
| 6. Search Tiers | Zylos Research 2026, InfoQ Local-First AI, LLM Router Cloud |
| 7. Mandate-as-Code | OPA/Rego, HashiCorp Sentinel, ARPaCCino 2025 |
| 8. Agent Specialization | EmergentMind pipeline-agent, arXiv:2507.13768, Redis cognitive pipeline |
| 9. Dry-Run Mocks | moqapi.dev, Keploy 2026 |
| 10. Observability | LangChain OTel (Mar 2025), LangSmith, OpenTelemetry GenAI semconv |
| 11. Hivemind | hivemindai.dev, deeplake.ai/hivemind, agent-hivemind |
| 12. Gap Schema | GAPMAP (arXiv:2510.25055), ServiceNow Knowledge Gaps |
| 13. Meditation Mode | D-297 10-Pillar Meditation, this session |

---

**End of Specification**

*This spec incorporates all 13 research gaps resolved with 35+ authoritative sources (2025-2026). The coordinator prompt (Section 4) and failure handling (Section 5) are the single most critical artifacts — review them carefully before implementation.*