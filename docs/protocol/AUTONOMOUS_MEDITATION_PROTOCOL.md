# ⬡ AUTONOMOUS MEDITATION PROTOCOL
**Version**: 1.0.0 | **Status**: ACTIVE
**Package**: `omega-meditation` | **Command**: `omega-meditation "problem"`
**Purpose**: Fully autonomous 7-stage pipeline: Problem → Prompt Crafting → Meditation → Synthesis → Research → Grounded Update → Gnosis → Integration

---

## 🎯 Protocol Overview

The Autonomous Meditation Protocol wraps the Meditation Protocol (`/meditate`) in a **fully autonomous pipeline** where the agent prompts itself at every stage, records all outputs to disk as mineable datapoints, and integrates results into project governance.

### Core Principle
> **Zero Human Intervention**: The agent crafts its own prompts, executes its own meditation, synthesizes its own verdict, crafts its own research queries, executes its own searches, grounds its own report, distills its own gnosis, and integrates its own results.

---

## 📋 7-Stage Pipeline Specification

### Stage 0: PROMPT CRAFTING (Agent → Self)
**Input**: Problem statement
**Process**: Agent analyzes problem → selects optimal lens set + mode → crafts `/meditate` prompt
**Output**: `data/autonomous/{ts}_00_prompt_crafted.md`

**Prompt Crafting Logic**:
- Architecture/Systemic → Full Pantheon 10 + STRATEGIC
- Bug/Diagnostic → Engineering,Validation,Observability,Infrastructure + DIAGNOSTIC
- Creative/Explore → Architect,Skeptic,Pragmatist,Ethicist + CREATIVE
- Audit/Compliance → Governance,Validation,Observability,Infrastructure + AUDIT

---

### Stage 1: MEDITATION EXECUTION (Agent → Self via `/meditate`)
**Input**: Crafted prompt from Stage 0
**Process**: Execute `/meditate` command with crafted prompt (Phases 0-4)
**Output**: `data/autonomous/{ts}_01_meditation_raw.md`

**Requirements**:
- Full Meditation Protocol compliance (10 voices, 3 collisions, L3 Gnosis)
- Anti-Collapse Contract: ACTIVE
- Raw output recorded verbatim

---

### Stage 2: INTUITIVE SYNTHESIS (Agent → Self as Kali)
**Input**: Raw meditation output
**Process**: Agent (as Kali) produces intuitive briefing:
1. Architecture diagram (ASCII)
2. Non-negotiables (from Preserved Dissent)
3. MVP scope (from Emergent Sequencing)
4. Integration points (Omega Pillars)
5. Success metrics (measurable)
6. "3 commands that change everything"
**Output**: `data/autonomous/{ts}_02_synthesis.md`

---

### Stage 3: RESEARCH PROMPT CRAFTING (Agent → Self)
**Input**: Synthesis + Raw meditation (identifying gaps/claims)
**Process**: Agent crafts deep research prompt with:
- Specific technical decisions needing verification
- Collision resolution paths needing prior art
- Integration points needing implementation references
- "2026 best practices for X" queries
- "X vs Y production failure modes" queries
**Output**: `data/autonomous/{ts}_03_research_prompt.md`

---

### Stage 4: RESEARCH EXECUTION (Agent → Sovereign Search)
**Input**: Research prompt from Stage 3
**Process**: Tiered search for each query:
- **T0**: Local cache (`data/research/internal-discovery/`)
- **T1**: `websearch` (primary, 2026 sources)
- **T2**: `webfetch` (deep extraction from key URLs)
- **T3**: `searxng` (semantic refinement)
- **T4**: `exa` (high-precision technical)
- **T5**: `firecrawl` (full-page scrape for docs)
**Output**: `data/autonomous/{ts}_04_research_raw.md` (structured findings with citations)

---

### Stage 5: GROUNDED REPORT (Agent → Self)
**Input**: Raw meditation (Stage 1) + Research findings (Stage 4)
**Process**: Agent produces updated meditation report:
- Architecture updated with research citations
- Claims verified against evidence
- Assumptions corrected based on evidence
- New insights from prior art
- Risk adjustments from failure modes
**Output**: `data/autonomous/{ts}_05_grounded_report.md`

---

### Stage 6: GNOSIS DISTILLATION (Agent → Verity)
**Input**: Grounded report
**Process**: L1→L2→L3 distillation per Soul Architecture Protocol (M11):
- **L1 Narrative**: What happened in this session
- **L2 Insight**: What this means for architecture
- **L3 Principle**: Universal truth (format: `L3-Name: Principle`)
**Output**: `data/autonomous/{ts}_06_gnosis.md` → appended to `proposed_lessons.yaml` (blind staging)

---

### Stage 7: INTEGRATION (Agent → Ma'at)
**Input**: Gnosis + Grounded report
**Process**:
1. Append to `PIVOT_LOG.md` as D-XXX decision
2. Update `SOVEREIGN_ARK_BLUEPRINT.md` active sprint
3. Create work items in `data/workbench/workbench.db`
4. Run Temple-Grade gates:
   - `make temple-grade` (T1-T11)
   - `make heritage-map` (M14)
   - `make sovereignty` (M7)
   - `make test` (1398+ tests)
**Output**: `data/autonomous/{ts}_07_integration.md`

---

## 🔧 Command Interface

```bash
omega-meditation "Problem statement" [options]

Options:
  --mode <mode>         opencode | cli | standalone (default: opencode)
  --resume-from <N>     Resume from stage N (0-7)
  --dry-run             No external calls (null clients)
  --output-dir <path>   Custom output directory
  --version             Show version
```

### Platform Modes

| Mode | Factory | Oracle Client | Search Client |
|------|---------|---------------|---------------|
| `opencode` | `create_pipeline_opencode()` | MCP Hub `omega_hub_oracle_talk` | MCP Hub `omega_hub_library_web_search` + `webfetch` + `searxng` |
| `cli` | `create_pipeline_cli()` | Subprocess `opencode` | Subprocess `websearch` |
| `standalone` | `create_pipeline_standalone()` | Null (dry-run) | Null (dry-run) |

---

## 📁 Output Structure

```
data/autonomous/
├── {timestamp}_00_prompt_crafted.md      # Stage 0: Agent's self-prompt
├── {timestamp}_01_meditation_raw.md      # Stage 1: Raw /meditate output
├── {timestamp}_02_synthesis.md           # Stage 2: Kali Verdict briefing
├── {timestamp}_03_research_prompt.md     # Stage 3: Research self-prompt
├── {timestamp}_04_research_raw.md        # Stage 4: 15+ tiered searches
├── {timestamp}_05_grounded_report.md     # Stage 5: Verified architecture
├── {timestamp}_06_gnosis.md              # Stage 6: 14 L3 principles
└── {timestamp}_07_integration.md         # Stage 7: PIVOT_LOG + gates
```

---

## 🛡️ Quality Gates (Auto-Run Stage 7)

```bash
make temple-grade    # T1-T11: Version control, docs, tests, quality, arch, security, perf, resilience, observability, integrity, agent security
make heritage-map    # M14: All [id-soft:] tags vetted
make sovereignty     # M7: Local-first ratio ≥ 80%
make test            # 1398+ tests pass
```

---

## 🔗 Platform Abstraction (M16 Compliant)

```python
# Engine core receives clients via dependency injection
class PlatformClients:
    oracle: OracleClient      # Protocol: async talk(prompt) -> str
    search: SearchClient      # Protocol: async search/fetch/searxng

# Factories for each platform
PlatformClients.from_opencode()   # MCP Hub tools
PlatformClients.from_cli()        # Subprocess calls
PlatformClients.null()            # Dry-run
```

---

## 📚 Related Documents

| Document | Purpose |
|----------|---------|
| `MEDITATION_PROTOCOL.md` | Single meditation session (Phases 0-4) |
| `AUTONOMOUS_MEDITATION_QUICKREF.md` | One-page command reference |
| `SOUL_ARCHITECTURE_PROTOCOL.md` | L1→L2→L3 gnosis distillation |
| `R_SEARCH_TOOL_PROTOCOL_V1.md` | Sovereign Search T0-T5 tiered escalation |
| `PIVOT_LOG.md` | Immutable decision log |

---

## 🧬 Heritage

- **Meditation Protocol**: Architect's Gemini CLI (2025) → Strike 11.5 Council Dispatcher (2026-06) → `/meditate` (2026-07-16)
- **Autonomous Wrapper**: This protocol (2026-07-18)
- **Package**: `omega-meditation` (PyPI, Homebrew)

---

*⬡ OMEGA ⬡ AUTONOMOUS-MEDITATION-PROTOCOL v1.0 ⬡ trc_protocol_spec*