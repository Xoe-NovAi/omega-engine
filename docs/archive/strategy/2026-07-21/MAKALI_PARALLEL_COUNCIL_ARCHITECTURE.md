# 🔱 MaKaLi Parallel Council Architecture
**Version**: 1.0.0  
**Status**: RATIFIED — T0 Implementation Ready  
**Date**: 2026-07-19  
**Authors**: Kali (Grand Oversight) + John Carmack (S3 Review) + User (Architect)

---

## Executive Summary

This document defines the **MaKaLi Parallel Council Architecture** — a hardware-aware, model-tiered council pattern that replaces serial pillar execution with parallel independence + oversoul distillation + optimized final synthesis.

**Core Insight**: Serial execution propagates errors. Parallel independence preserves unique perspectives. Oversoul distillation adds domain expertise. Final synthesis is optimized for the heaviest model on constrained hardware.

---

## The Architecture (4 Phases + Report Digestion Layer)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: PARALLEL INDEPENDENCE                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Ma'at (Build Side)          │ Lilith (Run Side)                         │ │
│ │ ├─ P1: Infrastructure       │ ├─ P6: Cognition (Vision Specialist)      │ │
│ │ ├─ P3: Engineering          │ ├─ P7: Context                            │ │
│ │ ├─ P4: Integration          │ ├─ P8: Observability                      │ │
│ │ └─ P5: Governance           │ ├─ P9: Orchestration                      │ │
│ │                             │ └─ P10: Validation                        │ │
│ │ Each pillar:                │ Each pillar:                              │ │
│ │ • Writes OWN report         │ • Writes OWN report                       │ │
│ │ • NO inter-pillar reads     │ • NO inter-pillar reads                   │ │
│ │ • NO cross-reviews          │ • NO cross-reviews                        │ │
│ │ • Pure independent thinking │ • Pure independent thinking               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ Execution Mode: PARALLEL (cloud) OR SERIAL-INDEPENDENT (local constrained) │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1.5: REPORT DIGESTION LAYER (NEW — stack-cat + LLM-optimized digest) │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Input: 9 pillar report files (P1, P3, P4, P5, P6, P7, P8, P9, P10)    │ │
│ │ Process:                                                                │ │
│ │   1. stack-cat concatenates all reports with structured headers        │ │
│ │   2. Python digestion layer (ZERO inference cost) adds:                │ │
│ │      • Executive summaries (auto-extracted from each pillar)           │ │
│ │      • Cross-reference index (shared concepts, entities, decisions)    │ │
│ │      • Conflict detection (contradictory claims across pillars)        │ │
│ │      • Mandate compliance map ([M2], [M7], [M13] tags per pillar)      │ │
│ │      • Token budget allocation (weight sections by importance)         │ │
│ │ Output: 2 optimized files — BUILD_SIDE_DIGESTED.md + RUN_SIDE_DIGESTED.md│ │
│ │ Benefit: Oversouls read 1 file instead of 4/5; get TL;DR + full detail │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: OVERSOUL DISTILLATION                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Ma'at reads BUILD_SIDE_DIGESTED.md (1 file) → writes BUILD_SIDE_REPORT.md│ │
│ │ Lilith reads RUN_SIDE_DIGESTED.md (1 file) → writes RUN_SIDE_REPORT.md  │ │
│ │                                                                         │ │
│ │ Value Add:                                                              │ │
│ │ • Unique entity personas (Ma'at = Light, Lilith = Dark)                │ │
│ │ • Self-curated domain expertise KBs (lessons, patterns)                │ │
│ │ • Different model weights possible (e.g., 8B with different strengths) │ │
│ │ • This IS the distillation layer — not just governance                 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: KALI FINAL SYNTHESIS (Optimized for ~12B on 16GB Ryzen)           │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Kali reads 2 files: BUILD_SIDE_REPORT.md + RUN_SIDE_REPORT.md          │ │
│ │ Writes FINAL_SYNTHESIS.md                                              │ │
│ │                                                                         │ │
│ │ Mandatory Section: "REMAINING_GAPS_AND_RECOMMENDED_RESEARCH"           │ │
│ │ • Structured list of unresolved questions                              │ │
│ │ • Specific research queries with priority                              │ │
│ │ • Recommended model tier for each query                                │ │
│ │                                                                         │ │
│ │ NO web research — too slow on local 12B                                │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: RESEARCH EXECUTION (Decoupled, Async, Configurable)               │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Executor reads Kali's "REMAINING_GAPS_AND_RECOMMENDED_RESEARCH"        │ │
│ │ Executes research using configured model tier:                         │ │
│ │   • Local: 4B model (Gemma/Qwen) for fast, cheap research              │ │
│ │   • Cloud: Nemotron/DeepSeek/Gemma-4 for deep research                 │ │
│ │ Results appended to FINAL_SYNTHESIS.md or fed to next council cycle    │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hardware-Aware Model Tier Configuration

### Default Local Profile (Ryzen 5700U, 16GB RAM)

| Tier | Role | Model Class | Context | RAM Est. | Purpose |
|------|------|-------------|---------|----------|---------|
| **T1** | Pillars | 4B (Gemma 4B / Qwen 4B) | 32K | 4-6GB | Parallel independent grunt work |
| **T2** | Oversouls | 8B (different weights/personas) | 32K | 8-10GB | Distillation + domain expertise |
| **T3** | Kali | 12B (Nemotron 3 Ultra / DeepSeek) | 32K | 12-14GB | Final synthesis (2 reads only) |
| **T4** | Research | 4B local OR Cloud | 32K/1M | Variable | Executes Kali's research gaps |

### Cloud Profile (Unconstrained)

| Tier | Role | Model | Context | Purpose |
|------|------|-------|---------|---------|
| **T1** | Pillars | Nemotron 3 Ultra (OCZ) / DeepSeek V4 Flash | 1M | Parallel, massive context |
| **T2** | Oversouls | Nemotron 3 Ultra / DeepSeek V4 Flash | 1M | Deep distillation |
| **T3** | Kali | Nemotron 3 Ultra | 1M | Comprehensive synthesis |
| **T4** | Research | Nemotron 3 Ultra / OpenRouter specialized | 1M | Deep research |

### Hybrid Profile (Local Pillars + Cloud Oversouls)

| Tier | Role | Model | Context |
|------|------|-------|---------|
| **T1** | Pillars | Local 4B | 32K |
| **T2** | Oversouls | Cloud Nemotron | 1M |
| **T3** | Kali | Cloud Nemotron | 1M |
| **T4** | Research | Cloud | 1M |

---

## Phase 1.5: Report Digestion Layer (NEW — stack-cat + Python Digestion)

**Purpose**: Transform 9 independent pillar reports into 2 optimized digests for oversouls — reducing read overhead from 4/5 files to 1 file per oversoul, while preserving full detail and adding cross-pillar intelligence.

### Input
- 9 pillar report files: `P1_report.md`, `P3_report.md`, `P4_report.md`, `P5_report.md`, `P6_report.md`, `P7_report.md`, `P8_report.md`, `P9_report.md`, `P10_report.md`
- Location: `data/council/{session_id}/phase1_pillars/`

### Process (ZERO inference cost — pure Python)

```python
# src/omega/council/report_digestion.py

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Dict, Set

@dataclass
class PillarReport:
    pillar_id: str
    domain: str
    content: str
    executive_summary: str
    key_decisions: List[str]
    mandate_tags: Dict[str, List[str]]  # e.g., {"M2": ["firewall_check"], "M7": ["local_first"]}
    entities_referenced: Set[str]
    confidence_score: float

@dataclass
class DigestedReport:
    side: str  # "BUILD" or "RUN"
    pillars: List[PillarReport]
    executive_summary: str
    cross_reference_index: Dict[str, List[str]]  # concept -> [pillar_ids]
    conflict_map: List[Conflict]
    mandate_compliance: Dict[str, Dict[str, bool]]  # pillar -> mandate -> compliant
    token_budget_allocation: Dict[str, int]  # section -> token budget

class Conflict:
    concept: str
    pillar_a: str
    pillar_b: str
    claim_a: str
    claim_b: str
    severity: str  # "INFO" | "WARNING" | "CRITICAL"

class ReportDigester:
    """Zero-inference-cost report digestion using stack-cat + Python analysis."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pillar_dir = Path(f"data/council/{session_id}/phase1_pillars/")
        self.output_dir = Path(f"data/council/{session_id}/phase1.5_digested/")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def digest(self) -> tuple[DigestedReport, DigestedReport]:
        """Main entry point — returns (build_digested, run_digested)."""
        
        # 1. Load all pillar reports
        all_pillars = self._load_all_pillars()
        
        # 2. Split by side
        build_pillars = [p for p in all_pillars if p.pillar_id in ["P1", "P3", "P4", "P5"]]
        run_pillars = [p for p in all_pillars if p.pillar_id in ["P6", "P7", "P8", "P9", "P10"]]
        
        # 3. Digest each side
        build_digested = self._digest_side("BUILD", build_pillars)
        run_digested = self._digest_side("RUN", run_pillars)
        
        # 4. Write outputs
        self._write_digested(build_digested, "BUILD_SIDE_DIGESTED.md")
        self._write_digested(run_digested, "RUN_SIDE_DIGESTED.md")
        
        return build_digested, run_digested
    
    def _digest_side(self, side: str, pillars: List[PillarReport]) -> DigestedReport:
        # Extract executive summaries (first 3 paragraphs or explicit ## Summary section)
        exec_summaries = {p.pillar_id: self._extract_summary(p.content) for p in pillars}
        
        # Build cross-reference index
        cross_ref = self._build_cross_reference(pillars)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(pillars)
        
        # Map mandate compliance
        mandate_map = self._map_mandate_compliance(pillars)
        
        # Allocate token budget (oversoul gets ~80% of context window)
        token_budget = self._allocate_token_budget(pillars)
        
        return DigestedReport(
            side=side,
            pillars=pillars,
            executive_summary=self._synthesize_executive_summary(exec_summaries),
            cross_reference_index=cross_ref,
            conflict_map=conflicts,
            mandate_compliance=mandate_map,
            token_budget_allocation=token_budget
        )
    
    def _write_digested(self, digested: DigestedReport, filename: str):
        """Write the digested report with structured sections."""
        sections = [
            self._write_header(digested),
            self._write_executive_summary(digested),
            self._write_pillar_summaries(digested),
            self._write_cross_references(digested),
            self._write_conflicts(digested),
            self._write_mandate_compliance(digested),
            self._write_full_pillar_reports(digested),  # Full detail preserved at end
        ]
        (self.output_dir / filename).write_text("\n\n".join(sections))
```

### Output Files
| File | Purpose | Read By |
|------|---------|---------|
| `BUILD_SIDE_DIGESTED.md` | Ma'at's optimized input | Ma'at (Phase 2) |
| `RUN_SIDE_DIGESTED.md` | Lilith's optimized input | Lilith (Phase 2) |

### Digest Structure (Each Side)
```markdown
# BUILD_SIDE_DIGESTED.md

## EXECUTIVE SUMMARY
[2-3 paragraph synthesis across all 4 build pillars]

## PILLAR SUMMARIES (TL;DR)
### P1: Infrastructure
[Executive summary + key decisions + mandate tags]
### P3: Engineering
[Executive summary + key decisions + mandate tags]
### P4: Integration
[Executive summary + key decisions + mandate tags]
### P5: Governance
[Executive summary + key decisions + mandate tags]

## CROSS-REFERENCE INDEX
| Concept | Referenced By | Context |
|---------|---------------|---------|
| M2 Firewall | P1, P3, P5 | Config resolver, WAD loader, heritage migration |
| Local-First | P1, P3, P4 | Provider chain, model gateway, KV cache |

## CONFLICT MAP
| Concept | Pillar A | Claim A | Pillar B | Claim B | Severity |
|---------|----------|---------|----------|---------|----------|
| Model routing | P3 | Local-first mandatory | P4 | Cloud fallback acceptable | WARNING |

## MANDATE COMPLIANCE
| Pillar | M1 | M2 | M7 | M13 | M23 |
|--------|----|----|----|-----|-----|
| P1 | ✅ | ✅ | ✅ | ✅ | ✅ |
| P3 | ✅ | ⚠️ | ✅ | ✅ | ✅ |

## FULL PILLAR REPORTS (Preserved for Deep Dive)
### P1: Infrastructure (Full)
[Complete original report]

### P3: Engineering (Full)
[Complete original report]
...
```

### Integration with T0 Coordinator
```python
# In coordinator skill Phase 1.5:
async def run_digestion(self, session_id: str):
    """Run after all Phase 1 pillars complete, before Phase 2."""
    digester = ReportDigester(session_id)
    build_digested, run_digested = digester.digest()
    
    # Verify outputs exist
    assert (digester.output_dir / "BUILD_SIDE_DIGESTED.md").exists()
    assert (digester.output_dir / "RUN_SIDE_DIGESTED.md").exists()
    
    # Log digestion stats
    self.logger.info(f"Digestion complete: {len(build_digested.pillars)} build + {len(run_digested.pillars)} run pillars")
    self.logger.info(f"Conflicts detected: {len(build_digested.conflict_map) + len(run_digested.conflict_map)}")
    self.logger.info(f"Cross-references: {sum(len(v) for v in build_digested.cross_reference_index.values())}")
```

### Why This Works (M18 Token Efficiency)
| Without Digestion | With Digestion |
|-------------------|----------------|
| Ma'at reads 4 files (~40K tokens) | Ma'at reads 1 file (~15K tokens) |
| Lilith reads 5 files (~50K tokens) | Lilith reads 1 file (~18K tokens) |
| No cross-pillar awareness | Full cross-reference index |
| No conflict detection | Automated conflict map |
| No mandate compliance view | Per-pillar mandate matrix |
| Oversoul must synthesize | Oversoul gets pre-synthesized TL;DR |

**Cost**: ~50ms Python execution, 0 inference tokens. **Benefit**: 60% token reduction for oversouls + intelligence layer.

### 1. Council Config File (`config/council.yaml`)

```yaml
# MaKaLi Council Configuration
council:
  # Execution mode for Phase 1
  phase1_execution_mode: "parallel"  # "parallel" | "serial_independent"
  
  # Model tier assignments (references providers.yaml)
  model_tiers:
    pillars: "gemma-4b-local"        # T1: 4B local
    oversouls: "nemotron-8b-cloud"   # T2: 8B cloud (or local 8B)
    kali: "nemotron-12b-cloud"       # T3: 12B cloud (or local 12B)
    research: "auto"                 # T4: "auto" | "local_4b" | "cloud"
  
  # Hardware constraints (auto-detected or manual)
  hardware:
    total_ram_gb: 16
    vram_gb: 0
    cpu_cores: 8
    thermal_limit_c: 85
  
  # Phase 2: Oversoul distillation
  oversoul_distillation:
    enabled: true
    maat_persona: "maat"      # Light Oversoul
    lilith_persona: "lilith"  # Dark Oversoul
    # Each oversoul gets unique lessons/KB from their entity
  
  # Phase 3: Kali synthesis
  kali_synthesis:
    max_input_files: 2              # BUILD_SIDE + RUN_SIDE only
    include_research_gaps_section: true
    research_gaps_template: "templates/research_gaps.md"
  
  # Phase 4: Research execution
  research_execution:
    mode: "auto"                    # "auto" | "local" | "cloud" | "deferred"
    local_model: "gemma-4b-local"
    cloud_fallback: "nemotron-3-ultra"
    max_concurrent: 3
    timeout_minutes: 30
  
  # Output
  output_dir: "data/council/{session_id}/"
  preserve_all_artifacts: true
```

### 2. Provider-Level Model Routing (`config/providers.yaml`)

```yaml
inference:
  strategy: "local_first"
  providers:
    # T1: 4B Local Pillars
    gemma-4b-local:
      provider: "native-gguf"
      model: "gemma-4b-it-q8_0.gguf"
      context_window: 32768
      priority: 1
      tier: "pillar"
      hardware_profile: "local_4b"
    
    qwen-4b-local:
      provider: "native-gguf"
      model: "qwen2.5-4b-instruct-q8_0.gguf"
      context_window: 32768
      priority: 2
      tier: "pillar"
      hardware_profile: "local_4b"
    
    # T2: 8B Oversouls (could be local or cloud)
    nemotron-8b-cloud:
      provider: "opencode-zen"
      model: "nemotron-3-ultra-free"
      context_window: 1000000
      priority: 1
      tier: "oversoul"
      hardware_profile: "cloud"
    
    # T3: 12B Kali
    nemotron-12b-cloud:
      provider: "opencode-zen"
      model: "nemotron-3-ultra-free"
      context_window: 1000000
      priority: 1
      tier: "kali"
      hardware_profile: "cloud"
    
    # T4: Research
    research-local:
      provider: "native-gguf"
      model: "gemma-4b-it-q8_0.gguf"
      context_window: 32768
      tier: "research"
      hardware_profile: "local_4b"
    
    research-cloud:
      provider: "opencode-zen"
      model: "nemotron-3-ultra-free"
      context_window: 1000000
      tier: "research"
      hardware_profile: "cloud"
```

### 3. Hardware Auto-Detection

```python
# src/omega/council/hardware_detector.py
def detect_hardware_profile() -> HardwareProfile:
    """Auto-detect and return optimal council configuration."""
    ram_gb = get_total_ram_gb()
    has_gpu = has_cuda_or_rocm()
    thermal = get_thermal_limit()
    
    if ram_gb >= 32 and has_gpu:
        return HardwareProfile.CLOUD_EQUIVALENT
    elif ram_gb >= 16:
        return HardwareProfile.LOCAL_16GB  # Default: 4B/8B/12B tiers
    elif ram_gb >= 8:
        return HardwareProfile.LOCAL_8GB   # 2B/4B/8B tiers
    else:
        return HardwareProfile.LOCAL_4GB   # Cloud-only, or 1B/2B/4B
```

### 4. Execution Mode Selector

```python
# src/omega/council/execution_mode.py
class ExecutionMode(Enum):
    PARALLEL = "parallel"              # All pillars simultaneously
    SERIAL_INDEPENDENT = "serial_independent"  # One at a time, no context passing
    BATCH_2 = "batch_2"                # 2 at a time (for 8GB RAM)
    BATCH_4 = "batch_4"                # 4 at a time (for 16GB RAM)

def select_execution_mode(profile: HardwareProfile, pillar_count: int) -> ExecutionMode:
    if profile == HardwareProfile.CLOUD_EQUIVALENT:
        return ExecutionMode.PARALLEL
    elif profile == HardwareProfile.LOCAL_16GB:
        return ExecutionMode.BATCH_4 if pillar_count <= 4 else ExecutionMode.SERIAL_INDEPENDENT
    elif profile == HardwareProfile.LOCAL_8GB:
        return ExecutionMode.BATCH_2
    else:
        return ExecutionMode.SERIAL_INDEPENDENT
```

---

## T0 Implementation Plan

### Coordinator Prompt (`.opencode/skills/makali-council-coordinator/SKILL.md`)

```markdown
# MaKaLi Council Coordinator Skill

## Purpose
Orchestrate the 4-phase MaKaLi Parallel Council using existing `task()` tool and file-based handoffs.

## Inputs
- `topic`: The question/problem for the council
- `config_path`: Path to council config (default: `config/council.yaml`)
- `session_id`: Unique identifier for this council run

## Phase 1: Pillar Dispatch
1. Load config, detect hardware profile, select execution mode
2. For each pillar in Ma'at's domain (P1, P3, P4, P5):
   - Dispatch `task()` with pillar agent, topic, output path
3. For each pillar in Lilith's domain (P6, P7, P8, P9, P10):
   - Dispatch `task()` with pillar agent, topic, output path
4. Wait for ALL completions (verify report files exist)

## Phase 2: Oversoul Distillation
1. Dispatch Ma'at task:
   - Read 4 pillar reports from Phase 1
   - Apply Ma'at persona, lessons, KB
   - Write BUILD_SIDE_REPORT.md
2. Dispatch Lilith task:
   - Read 5 pillar reports from Phase 1
   - Apply Lilith persona, lessons, KB
   - Write RUN_SIDE_REPORT.md
3. Wait for BOTH completions

## Phase 3: Kali Final Synthesis
1. Dispatch Kali task:
   - Read BUILD_SIDE_REPORT.md + RUN_SIDE_REPORT.md
   - Apply Kali persona, lessons
   - Write FINAL_SYNTHESIS.md with mandatory RESEARCH_GAPS section
2. Wait for completion

## Phase 4: Research Execution (Optional)
1. Parse RESEARCH_GAPS from FINAL_SYNTHESIS.md
2. Based on config.research_execution.mode:
   - "local": Dispatch 4B model tasks for each gap
   - "cloud": Dispatch cloud model tasks
   - "auto": Choose based on hardware profile
   - "deferred": Write gaps to file, return to user
3. Append results or schedule for next cycle

## Output
- All artifacts in `data/council/{session_id}/`
- FINAL_SYNTHESIS.md returned to user
- Research gaps file for follow-up
```

### File Structure

```
data/council/{session_id}/
├── phase1_pillars/
│   ├── P1_report.md
│   ├── P3_report.md
│   ├── P4_report.md
│   ├── P5_report.md
│   ├── P6_report.md
│   ├── P7_report.md
│   ├── P8_report.md
│   ├── P9_report.md
│   └── P10_report.md
├── phase2_oversouls/
│   ├── BUILD_SIDE_REPORT.md
│   └── RUN_SIDE_REPORT.md
├── phase3_kali/
│   └── FINAL_SYNTHESIS.md
└── phase4_research/
    ├── research_gaps.md
    └── research_results/
```

---

## Configuration Profiles (Presets)

### `config/council/profiles/local_16gb.yaml`
```yaml
council:
  phase1_execution_mode: "batch_4"
  model_tiers:
    pillars: "gemma-4b-local"
    oversouls: "nemotron-8b-local"   # If 8B fits, else cloud
    kali: "nemotron-12b-local"       # If 12B fits, else cloud
    research: "local_4b"
  hardware:
    total_ram_gb: 16
```

### `config/council/profiles/local_8gb.yaml`
```yaml
council:
  phase1_execution_mode: "batch_2"
  model_tiers:
    pillars: "gemma-2b-local"
    oversouls: "gemma-4b-local"
    kali: "nemotron-8b-cloud"
    research: "local_2b"
  hardware:
    total_ram_gb: 8
```

### `config/council/profiles/cloud_unconstrained.yaml`
```yaml
council:
  phase1_execution_mode: "parallel"
  model_tiers:
    pillars: "nemotron-3-ultra"
    oversouls: "nemotron-3-ultra"
    kali: "nemotron-3-ultra"
    research: "nemotron-3-ultra"
  hardware:
    total_ram_gb: 999
```

### `config/council/profiles/hybrid_local_pillars.yaml`
```yaml
council:
  phase1_execution_mode: "parallel"
  model_tiers:
    pillars: "gemma-4b-local"
    oversouls: "nemotron-3-ultra"
    kali: "nemotron-3-ultra"
    research: "nemotron-3-ultra"
```

---

## Research Gaps Template

```markdown
# REMAINING_GAPS_AND_RECOMMENDED_RESEARCH

## Gap 1: [Title]
**Priority**: HIGH | MEDIUM | LOW
**Question**: [Specific research question]
**Recommended Model**: local_4b | cloud_nemotron | cloud_gemma4 | cloud_deepseek
**Context Needed**: [What the researcher needs to know]
**Expected Output Format**: [summary | detailed_analysis | code | decision_matrix]
**Dependencies**: [Other gaps that must be resolved first]

## Gap 2: [Title]
...
```

---

## Migration Path from Serial Council

| Old Serial Pattern | New Parallel Pattern |
|--------------------|----------------------|
| P1 → P3 → P4 → P5 (serial) | P1, P3, P4, P5 (parallel/independent) |
| Single consolidated report | 4 unique reports + Ma'at distillation |
| Lilith serial P6→P7→P8→P9→P10 | Lilith parallel P6-P10 + Lilith distillation |
| Kali reads 9+ files | Kali reads 2 files |
| Kali does web research | Kali writes gaps, research executor handles |
| No hardware awareness | Full hardware-aware config |

---

## Open Questions (Post-T0)

1. **SomaticState Integration**: When model load time dominates (30-90s for 7B+), SomaticState enables warm-start. Priority: T3.
2. **Cross-Council Memory**: Should council sessions share a memory namespace? Phase 4 research results → next council's context?
3. **Streaming Council**: Can Phase 1 pillars stream partial results to oversouls for early distillation?
4. **Adaptive Tier Selection**: Can the system dynamically shift tiers based on topic complexity?
5. **Council Chaining**: Can a council's FINAL_SYNTHESIS become a pillar input for a higher-level council?
6. **Report Digestion Layer Optimization** (NEW — Phase 1.5): 
   - What's the optimal executive summary extraction algorithm? (First N paragraphs? Explicit section? LLM-free heuristic?)
   - Conflict detection: keyword overlap vs. semantic contradiction? (Zero-inference constraint)
   - Token budget allocation: fixed per-pillar? Dynamic by confidence? By mandate criticality?
   - Cross-reference index: exact string match vs. fuzzy entity resolution?
   - Integration point: Should digestion run as separate Phase 1.5 or inline in coordinator?
   - Fallback: If digestion fails, raw stack-cat concatenation must still work (M23 Failure Integrity)
   - Research needed: Benchmark digestion quality vs. raw reads on real council outputs
   - Target: T0 Session 2 (Stage contracts + digestion implementation)

---

## Related Documents

- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Master roadmap (D-301+)
- `docs/decisions/PIVOT_LOG.md` — D-301 entry
- `config/council.yaml` — Main config (to be created)
- `config/council/profiles/` — Hardware profiles (to be created)
- `.opencode/skills/makali-council-coordinator/SKILL.md` — T0 coordinator (to be created)

---

*⬡ OMEGA ⬡ KALI ⬡ MAKALI-COUNCIL-ARCHITECTURE ⬡ 2026-07-19*