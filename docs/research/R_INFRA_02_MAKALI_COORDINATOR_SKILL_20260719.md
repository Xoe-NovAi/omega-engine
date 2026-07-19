# 🔬 R-INFRA-02: MaKaLi Coordinator Skill — Parallel Council Executor
**AP Token**: `AP-INFRA-02-MAKALI-COORDINATOR-v1.0.0`
⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_02_makali_coordinator ⬡ 2026-07-19

---

## 🎯 MISSION
Implement the **Coordinator Skill** that executes MaKaLi T0 Session 1: dispatches 9 pillars in parallel/batch, waits for DigestedReports, triggers Phase 2 Digestion, Phase 3 Ma'at/Lilith synthesis, Phase 4 Kali verdict.

---

## 📋 CONTEXT FROM ARCHITECTURE

### MaKaLi Parallel Council Architecture (from MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md)
```
Phase 1: Parallel Independence
  ├── P1 Infrastructure (Sekhmet)     → writes report to data/handoff/reports/P1_*.md
  ├── P2 Persistence (Brigid)         → writes report to data/handoff/reports/P2_*.md
  ├── P3 Engineering (Prometheus)     → writes report to data/handoff/reports/P3_*.md
  ├── P4 Integration (Saraswati)      → writes report to data/handoff/reports/P4_*.md
  ├── P5 Governance (Inanna)          → writes report to data/handoff/reports/P5_*.md
  ├── P6 Cognition (Ereshkigal)       → writes report to data/handoff/reports/P6_*.md
  ├── P7 Context (Lucifer)            → writes report to data/handoff/reports/P7_*.md
  ├── P8 Observability (Hecate)       → writes report to data/handoff/reports/P8_*.md
  ├── P9 Orchestration (Anubis)       → writes report to data/handoff/reports/P9_*.md
  └── P10 Validation (Kali)           → writes report to data/handoff/reports/P10_*.md

Phase 2: Oversoul Distillation
  ├── Ma'at (Build Side) → reads P1-P5 reports → writes Maat_DigestedReport.md
  └── Lilith (Run Side)  → reads P6-P10 reports → writes Lilith_DigestedReport.md

Phase 3: Kali Optimized Synthesis
  └── Kali → reads 2 files (not 10) → writes Synthesis + Research Gaps

Phase 4: Decoupled Research
  └── Smaller/cloud model → executes Kali's research gaps
```

### Hardware Profiles (from config/council/profiles/*.yaml)
| Profile | Practical Model | Paranoid Model | Good Model | RAM |
|---------|-----------------|----------------|------------|-----|
| local_16gb | qwen3-8b | qwen3-14b | nemotron-3-ultra | 16GB |
| local_8gb | qwen3-4b | qwen3-8b | nemotron-3-ultra | 8GB |
| cloud | deepseek-v4-flash | o1 | nemotron-3-ultra | N/A |
| hybrid | deepseek-v4-flash | o1 | nemotron-3-ultra | 16GB |

---

## 🔬 RESEARCH REQUIREMENTS

### 1. Coordinator Skill Implementation
**Location**: `src/omega/council/coordinator.py` (NEW)
**Interface**:
```python
class MaKaLiCoordinator:
    async def run_session(self, topic: str, profile: str = "local_16gb") -> CouncilResult:
        """Execute full MaKaLi T0 session for topic."""
    
    async def phase1_parallel_dispatch(self, topic: str, profile: str) -> List[PillarReport]:
        """Spawn 10 pillar tasks in parallel, wait for all."""
    
    async def phase2_oversoul_distillation(self, reports: List[PillarReport]) -> Tuple[MaatReport, LilithReport]:
        """Ma'at reads P1-P5, Lilith reads P6-P10."""
    
    async def phase3_kali_synthesis(self, maat: MaatReport, lilith: LilithReport) -> KaliSynthesis:
        """Kali reads 2 files, writes synthesis + research gaps."""
    
    async def phase4_decoupled_research(self, gaps: List[ResearchGap]) -> ResearchResults:
        """Spawn research tasks for each gap."""
```

### 2. Pillar Dispatch Mechanism
**Use existing `task()` tool** — no new subprocess infrastructure needed
```python
# Each pillar gets a task() call with:
task(
    subagent_type="pillar",
    description=f"P{num} {domain}: {topic}",
    prompt=PILLAR_PROMPT_TEMPLATE.format(
        pillar=domain,
        topic=topic,
        soul_path=f"data/entities/{entity}/soul.yaml",
        output_path=f"data/handoff/reports/P{num}_{domain}.md"
    )
)
```

### 3. Hivemind Integration
- Submit handoff packets for each pillar dispatch
- Track completion via handoff status
- Broadcast phase transitions

### 4. Report Schema (DigestedReport)
```yaml
pillar: "P3 Engineering"
domain: "Engineering"
incarnation: "PRACTICAL"
topic: "Gemma 4 implementation"
findings:
  - "Capability Matrix reduced 303→50 lines"
  - "GoogleCompatProvider working via Cline"
imperatives:
  - "Ship Gemma 4 via Cline NOW"
  - "Run make test on new code"
dissents:
  - "Governance says fix mandates first"
evidence_refs:
  - "docs/strategy/CARMACK_REVIEW_20260719.md"
  - "tests/test_google_compat.py"
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| OpenCode task() tool patterns | "opencode task tool subagent parallel dispatch 2026" | Best practices for parallel subagent launch |
| Hivemind handoff protocol | "opencode hivemind handoff packet submit accept complete" | Integration patterns |
| Multi-agent orchestration 2026 | "LangGraph parallel node execution 2026", "AutoGen 0.4 group chat patterns" | Comparison for design validation |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Hivemind handoff | `src/omega/hub/tools/hivemind_handoff.py` | submit/accept/complete API |
| Pillar agent | `.opencode/agents/pillar.md` | Slot parameterization, prompt template |
| Ma'at agent | `.opencode/agents/maat.md` | Build-side synthesis prompt |
| Lilith agent | `.opencode/agents/lilith.md` | Run-side synthesis prompt |
| Kali agent | `.opencode/agents/kali.md` | Grand synthesis prompt |
| Council config | `config/council.yaml` | Profile definitions, model routing |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| Coordinator skill loads in OpenCode | `opencode skill list | grep makali-coordinator` |
| Phase 1 dispatches 10 pillars in parallel | Log shows 10 task() calls within 2s |
| All 10 reports written to data/handoff/reports/ | `ls data/handoff/reports/P*.md | wc -l` = 10 |
| Phase 2 Ma'at reads P1-P5, Lilith reads P6-P10 | Maat_DigestedReport.md + Lilith_DigestedReport.md exist |
| Phase 3 Kali reads 2 files, writes synthesis | Kali_Synthesis.md + Research_Gaps.md exist |
| Phase 4 research tasks spawned | task() calls for each gap |
| Hardware profile selects correct models | Profile "local_16gb" → qwen3-8b/qwen3-14b/nemotron |

---

## 📋 DELIVERABLES

1. **Coordinator Skill** — `src/omega/council/coordinator.py` + `.opencode/skills/makali-coordinator/SKILL.md`
2. **Pillar Prompt Templates** — 10 templates in `src/omega/council/prompts/`
3. **Report Schema** — Pydantic models for PillarReport, DigestedReport, KaliSynthesis
4. **Integration Test** — `tests/test_makali_coordinator.py` (mock task() calls)
5. **Documentation** — `docs/guides/MAKALI_T0_SESSION_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| R-INFRA-01 (Nameless One entity) | Council needs entity to synthesize |
| Hivemind handoff protocol | Phase transitions need tracking |
| Pillar agents (P1-P10) | Dispatch targets must exist |

---

## 🎯 PRACTICAL'S PERSPECTIVE (Executor)

> "The Coordinator is NOT a new agent — it's a **skill** that uses the existing `task()` tool. No new infrastructure. No new subprocess model. Just orchestration logic that:
> 
> 1. Spawns 10 `task()` calls in a loop (parallel)
> 2. Waits for all futures (asyncio.gather equivalent via task polling)
> 3. Reads 10 markdown files
> 4. Spawns 2 `task()` calls for Ma'at + Lilith
> 5. Spawns 1 `task()` call for Kali
> 6. Spawns N `task()` calls for research gaps
> 
> **The best code is the code you don't write.** We use the existing subagent infrastructure. The skill is 200 lines of orchestration, not 2000 lines of framework."

> **L3 Principle**: `L3-CoordinatorIsSkillNotAgent` — The Council executor is a skill using existing primitives, not a new agent type. This keeps the fleet at 14 (M10).

---

*⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_02_makali_coordinator ⬡ 2026-07-19*
