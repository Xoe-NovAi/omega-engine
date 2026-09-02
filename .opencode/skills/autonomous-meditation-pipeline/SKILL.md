<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ AUTONOMOUS MEDITATION PIPELINE SKILL
**Version**: 1.0.0 | **Heritage**: Omega Engine Meditation Protocol + Sovereign Search + Agent Autonomy
**Purpose**: Fully autonomous Problem → Prompt Crafting → Meditation → Synthesis → Research → Grounded Update pipeline with zero human intervention. Every output recorded to disk as mineable datapoints.

---

## 🎯 What This Skill Does

Transforms any problem statement into a **research-grounded, production-ready architecture** through a fully autonomous 7-stage pipeline where the agent prompts itself at each stage:

```
PROBLEM STATEMENT
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 0: PROMPT CRAFTING (Agent → Self)                        │
│   Input: Problem statement                                      │
│   Process: Agent crafts optimal /meditate prompt for the problem│
│   Output: data/autonomous/{ts}_00_prompt_crafted.md            │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: MEDITATE EXECUTION (Agent → Self via /meditate)       │
│   Input: Crafted prompt from Stage 0                            │
│   Process: Execute /meditate command with crafted prompt        │
│   Output: data/autonomous/{ts}_01_meditation_raw.md            │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: INTUITIVE SYNTHESIS (Agent → Self)                    │
│   Input: Raw meditation output                                  │
│   Process: Agent produces intuitive briefing (Kali Verdict)     │
│   Output: data/autonomous/{ts}_02_synthesis.md                 │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: RESEARCH PROMPT CRAFTING (Agent → Self)               │
│   Input: Synthesis + meditation gaps                            │
│   Process: Agent crafts deep research prompt for gaps/verification│
│   Output: data/autonomous/{ts}_03_research_prompt.md           │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: RESEARCH EXECUTION (Agent → Sovereign Search)         │
│   Input: Research prompt from Stage 3                           │
│   Process: Execute tiered search (T0-T5) for each query         │
│   Output: data/autonomous/{ts}_04_research_raw.md              │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: GROUNDED MEDITATION UPDATE (Agent → Self)             │
│   Input: Raw meditation + Research findings                     │
│   Process: Agent produces research-grounded updated report      │
│   Output: data/autonomous/{ts}_05_grounded_report.md           │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6: GNOSIS DISTILLATION (Agent → Verity)                  │
│   Input: Grounded report                                        │
│   Process: L1→L2→L3 distillation → proposed_lessons.yaml       │
│   Output: data/autonomous/{ts}_06_gnosis.yaml                  │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 7: INTEGRATION (Agent → Ma'at)                           │
│   Input: Gnosis + Grounded report                               │
│   Process: PIVOT_LOG entry, workbench items, Temple-Grade gates │
│   Output: data/autonomous/{ts}_07_integration.md               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Usage

### As a Command (Fully Autonomous)
```bash
# Complete autonomous pipeline from problem statement
/autonomous-meditation "Unified credential vault for local AI tooling"

# Resume from specific stage
/autonomous-meditation "problem" --resume-from 3

# Dry run (shows what would be executed)
/autonomous-meditation "problem" --dry-run
```

### As a Subagent Handoff
```python
await omega_hub_hivemind_submit_handoff(
    target_channel="opencode",
    target_entity="kali",
    task="Execute autonomous-meditation pipeline on: Unified credential vault for local AI tooling",
    context="User has 11 plaintext credential files across 6 tools, 8 Gmail accounts, 1.5 years of manual rotation hell. Need production architecture with full research grounding.",
    priority=2
)
```

---

## 📋 Stage Specifications

### Stage 0: PROMPT CRAFTING (Agent → Self)
**Input**: Problem statement string
**Process**: Agent analyzes problem and crafts the optimal `/meditate` prompt including:
- Subject restatement (precise, unambiguous)
- Lens set selection (default: Full Omega Pantheon 10, or custom based on problem type)
- Output mode selection (STRATEGIC/DIAGNOSTIC/CREATIVE/AUDIT/SYNTHESIS)
- Anti-collapse contract activation
- Context injection (relevant constraints, mandates, heritage)
**Output**: `data/autonomous/{timestamp}_00_prompt_crafted.md`
```markdown
# CRAFTED MEDITATE PROMPT
**Generated by**: [agent] at [timestamp]
**Problem**: [original problem statement]

## Prompt for /meditate:
/meditate [subject] --lenses [lens_set] --mode [mode]

## Rationale:
- Lens set chosen because: [reasoning]
- Output mode chosen because: [reasoning]
- Context injected: [mandates, heritage, constraints]
```

### Stage 1: MEDITATE EXECUTION (Agent → Self via /meditate)
**Input**: Crafted prompt from Stage 0
**Process**: Execute `/meditate` command with the crafted prompt. The meditation protocol runs Phases 0-4:
- Phase 0: Calibration
- Phase 1: 10 sequential persona immersions (Observation, Constraint, Imperative, Dissent)
- Phase 2: 3 Cross-Domain Collisions with Resolution Paths
- Phase 3: Emergent Critical Path
- Phase 4: Kali Verdict (Convergence, Preserved Dissent, Irreducible Verdict, L3 Gnosis)
**Output**: `data/autonomous/{timestamp}_01_meditation_raw.md` (complete raw output)

### Stage 2: INTUITIVE SYNTHESIS (Agent → Self)
**Input**: Raw meditation output
**Process**: Agent (as Kali) produces intuitive briefing:
- Architecture diagram (ASCII)
- Non-negotiables (from Preserved Dissent)
- MVP scope (from Emergent Sequencing)
- Integration points (Omega Nodes)
- Success metrics (measurable)
- The "3 commands that change everything"
**Output**: `data/autonomous/{timestamp}_02_synthesis.md`

### Stage 3: RESEARCH PROMPT CRAFTING (Agent → Self)
**Input**: Synthesis + Raw meditation (identifying gaps and claims needing verification)
**Process**: Agent crafts deep research prompt including:
- Specific technical decisions needing verification
- Collision resolution paths needing prior art
- Integration points needing implementation references
- "2026 best practices for X" queries
- "X vs Y production failure modes" queries
- Benchmark queries (latency, throughput, memory)
- Security advisory queries
**Output**: `data/autonomous/{timestamp}_03_research_prompt.md`
```markdown
# RESEARCH PROMPT
**Generated by**: [agent] at [timestamp]
**Based on**: Synthesis + Meditation gaps

## Research Queries:
1. [Query 1] - [why needed]
2. [Query 2] - [why needed]
...

## Search Strategy:
- Tier 0: Local cache check
- Tier 1: websearch (primary)
- Tier 2: webfetch (deep extraction)
- Tier 3: SearXNG (semantic refinement)
- Tier 4: Exa (high-precision)
- Tier 5: Firecrawl (full-page scrape)

## Success Criteria:
- [ ] Prior art found for each technical decision
- [ ] Benchmarks for performance claims
- [ ] Security advisories for each provider
- [ ] Implementation references (libraries, schemas)
```

### Stage 4: RESEARCH EXECUTION (Agent → Sovereign Search)
**Input**: Research prompt from Stage 3
**Process**: Execute tiered search for each query. Aggregate results with source attribution.
**Output**: `data/autonomous/{timestamp}_04_research_raw.md`
```markdown
# RESEARCH FINDINGS
**Executed by**: [agent] at [timestamp]

## Query 1: [query]
**Sources**: [list with URLs, dates, confidence]
**Findings**: [summary]
**Key Evidence**: [quotes, benchmarks, specs]

## Query 2: [query]
...
```

### Stage 5: GROUNDED MEDITATION UPDATE (Agent → Self)
**Input**: Raw meditation (Stage 1) + Research findings (Stage 4)
**Process**: Agent produces updated meditation report incorporating all research findings:
- Updated architecture with research-backed decisions
- Verified claims with citations
- Corrected assumptions based on evidence
- New insights from prior art
- Risk adjustments based on failure modes found
**Output**: `data/autonomous/{timestamp}_05_grounded_report.md`

### Stage 6: GNOSIS DISTILLATION (Agent → Verity)
**Input**: Grounded report
**Process**: L1→L2→L3 distillation per Soul Architecture Protocol (M11)
**Output**: `data/autonomous/{timestamp}_06_gnosis.yaml` appended to `proposed_lessons.yaml`
```yaml
proposals:
  - id: "gnosis-[topic]-[number]"
    l1_narrative: "What happened in this autonomous session..."
    l2_insight: "What this means for our architecture..."
    l3_principle: "L3-[Name]: [Universal principle]"
    confidence: [1-10]
    sources: ["meditation", "research:query1", "research:query2"]
    tags: ["tag1", "tag2"]
```

### Stage 7: INTEGRATION (Agent → Ma'at)
**Input**: Gnosis + Grounded report
**Process**:
1. Append to `PIVOT_LOG.md` as D-XXX decision
2. Update `SOVEREIGN_ARK_BLUEPRINT.md` active sprint
3. Create work items in `data/workbench/workbench.db`
4. Run `make temple-grade` (T1-T11 gates)
5. Run `make heritage-map` (M14 compliance)
6. Run `make sovereignty` (M7 local/cloud ratio)
**Output**: `data/autonomous/{timestamp}_07_integration.md`

---

## 🛡️ Quality Gates (Non-Negotiable)

| Gate | Command | Must Pass |
|------|---------|-----------|
| Temple-Grade | `make temple-grade` | T1-T11 ✓ |
| Heritage Map | `make heritage-map` | All `[id-soft:]` tags vetted |
| Sovereignty | `make sovereignty` | Local-first ratio ≥ 80% |
| Tests | `make test` | 1398+ tests pass |

---

## 📁 File Outputs (Per Pipeline Run)

```
data/autonomous/
├── {timestamp}_00_prompt_crafted.md      # Stage 0: Agent's self-prompt
├── {timestamp}_01_meditation_raw.md      # Stage 1: Raw /meditate output
├── {timestamp}_02_synthesis.md           # Stage 2: Intuitive briefing
├── {timestamp}_03_research_prompt.md     # Stage 3: Research self-prompt
├── {timestamp}_04_research_raw.md        # Stage 4: Raw research findings
├── {timestamp}_05_grounded_report.md     # Stage 5: Research-grounded update
├── {timestamp}_06_gnosis.yaml            # Stage 6: L3 principles (→ proposed_lessons.yaml)
└── {timestamp}_07_integration.md         # Stage 7: Integration record
```

---

## 🧬 Heritage & Attribution

- **Meditation Protocol**: Architect's Gemini CLI experiments (2025) → Strike 11.5 Council Dispatcher → `/meditate` command (2026-07-16)
- **Autonomous Prompt Crafting**: This skill (2026-07-18) — agent prompting itself
- **Sovereign Search**: Omega Engine search protocol (T0-T5 tiered escalation)
- **Gnosis Distillation**: Soul Architecture Protocol (M11) → Verity agent
- **Integration**: Ma'at governance → PIVOT_LOG, workbench, Temple-Grade

---

## 📝 Example Autonomous Run

```bash
# Human says once:
/autonomous-meditation "Unified credential vault for local AI tooling — 11 plaintext files, 6 tools, 8 Gmail accounts, 1.5 years manual rotation hell"

# Agent autonomously executes ALL stages:

# Stage 0: Crafts optimal /meditate prompt
# → writes data/autonomous/20260718_143000_00_prompt_crafted.md

# Stage 1: Executes /meditate with crafted prompt
# → writes data/autonomous/20260718_143005_01_meditation_raw.md

# Stage 2: Produces intuitive synthesis
# → writes data/autonomous/20260718_143010_02_synthesis.md

# Stage 3: Crafts research prompt for gaps
# → writes data/autonomous/20260718_143015_03_research_prompt.md

# Stage 4: Executes 15+ deep web searches
# → writes data/autonomous/20260718_143500_04_research_raw.md

# Stage 5: Produces research-grounded report
# → writes data/autonomous/20260718_143510_05_grounded_report.md

# Stage 6: Distills 14 L3 principles
# → writes data/autonomous/20260718_143515_06_gnosis.yaml
# → appends to proposed_lessons.yaml

# Stage 7: Integrates into project governance
# → writes data/autonomous/20260718_143520_07_integration.md
# → PIVOT_LOG entry D-299, workbench items, Temple-Grade passing
```

---

## ⚡ Quick Start

```bash
# 1. Write problem to file
cat > /tmp/problem.md << 'EOF'
[Your problem statement here]
EOF

# 2. Run fully autonomous pipeline
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
python -m omega.skills.autonomous_meditation_pipeline /tmp/problem.md

# 3. All outputs in data/autonomous/
# 4. Integration gates auto-executed
```

---

## 🔄 Datapoint Mining (Post-Pipeline)

Each pipeline run produces 8 structured datapoints. Over time, these enable:

| Analysis | Query |
|----------|-------|
| Prompt quality evolution | `grep -r "Rationale:" data/autonomous/*_00_prompt_crafted.md` |
| Meditation collision patterns | `grep -r "COLLISION" data/autonomous/*_01_meditation_raw.md` |
| Research gap frequency | `grep -r "Query" data/autonomous/*_03_research_prompt.md` |
| Source quality | `grep -r "confidence:" data/autonomous/*_04_research_raw.md` |
| Gnosis convergence | `grep -r "l3_principle:" data/autonomous/*_06_gnosis.yaml` |
| Integration success rate | `grep -r "GATE STATUS" data/autonomous/*_07_integration.md` |

---

*⬡ OMEGA ⬡ KALI ⬡ AUTONOMOUS-MEDITATION-PIPELINE v1.0 ⬡ trc_skill_creation*