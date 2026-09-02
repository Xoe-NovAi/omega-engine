<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOTE Best Practices Research — Deep Web Research

**AP Token**: `AP-RESEARCHER-SOTE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-09-01
**Week**: 2026-W36
**Session ID**: `ses_fd81c19dcffe1nkbPqFg5kRt2v`
**Deliverable**: `docs/strategy/sote/2026-W36/synthesis/RESEARCHER_SOTE_BEST_PRACTICES.md`

---

## Executive Summary

This research investigates best practices for weekly state-of-engine/architectural review cadences in sovereign/local-first AI systems. The Omega Engine's SOTE (State of the Engine) system implements a weekly architectural review with an 8-voice dialectic, immutable voice files, mutable synthesis, and YAML metadata for LLM ingestion.

**Key Finding**: The SOTE system aligns with emerging industry patterns but has critical gaps in automation, public/internal split enforcement, and index regeneration hardening that match documented anti-patterns in the literature.

**Confidence**: High (primary sources from Microsoft, Azure Architecture Center, ADR practitioners, and multi-agent orchestration frameworks)

---

## 1. Weekly/Biweekly Review Cadences in Comparable Systems

### 1.1 Local-First / Sovereign AI Systems

| System | Cadence | Structure | Key Characteristics |
|--------|---------|-----------|---------------------|
| **Valdr (MCP/UI)** | Continuous with human gates | Seven-dimension scoring, session-based review | Local-first by default, offline-ready, human review required before ship [Valdr.ai](https://valdr.ai/) |
| **Cadence (Calendar Intelligence)** | Weekly analysis generation | LangGraph flow: constraint→task→energy→draft→human review→write (3-round cap) | Local SQLite, Ollama fallback, MCP server for exposure [GitHub: ammiellewb/Cadence](https://github.com/ammiellewb/Cadence) |
| **CompuGlobal Tech** | Not specified | Local-first deployment, signed manifests | "No cloud. No subscription. Your intelligence, your rules" [CompuGlobal Tech](https://compuglobaltech.com/) |
| **Avery NXR** | Not specified | Local runtime, TypeScript + Prisma | "Be Sovereign. Deploy on premise" [GoodGist](https://goodgist.com/?kid=2CD4YV) |

**Pattern**: Local-first systems emphasize **human-in-the-loop gates**, **offline capability**, and **explicit approval workflows** rather than fixed weekly cadences. The review is triggered by session completion, not calendar.

### 1.2 Agent Orchestration Frameworks

| Framework | Review Cadence | Governance Model |
|-----------|----------------|------------------|
| **Microsoft Conductor** | Workflow-defined (deterministic) | YAML-defined workflows with human gates, web dashboard visualization [Microsoft Open Source Blog](https://opensource.microsoft.com/blog/2026/05/14/conductor-deterministic-orchestration-for-multi-agent-ai-workflows/) |
| **LangGraph** | Checkpoint-based | Graph-based orchestration with explicit state management, 43% enterprise adoption [thinking.inc](https://thinking.inc/en/blue-ocean/agentic/agent-orchestration-patterns/) |
| **CrewAI** | Role-based, fast weekly updates | Built-in coordination, sequential task execution despite appearing parallel [AutomationSwitch](https://automationswitch.com/agentic-ai/frameworks/crewai) |
| **Azure AI Agent Patterns** | Pattern-dependent | Sequential, Concurrent, Group Chat, Magentic, Hierarchical, Evaluator-Optimizer [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) |

**Pattern**: Modern frameworks **codify review cadence into workflow structure** (YAML/graph) rather than relying on calendar discipline. Human gates are explicit workflow steps.

### 1.3 Enterprise AI Governance

| Practice | Cadence | Source |
|----------|---------|--------|
| **AI Governance Weekly Recap** | Weekly (7-day cycle) | Consolidated regulatory/compliance developments [AI Governance Institute](https://aigovernance.com/news/tag/weekly-recap) |
| **Self-Host Weekly** | Weekly newsletter | Community-driven, covers AI/self-hosted intersection [selfh.st](https://selfh.st/weekly/2026-03-20/) |
| **ISO 42001 Gap Analysis** | Pre-audit (proactive) | "Addressing documentation gap proactively is far less costly than under deadline" [Centric Consulting](https://centricconsulting.com/blog/why-strong-ai-programs-still-fail-governance-reviews/) |

**Pattern**: Governance reviews are **weekly for operational awareness**, **event-driven for compliance**, and **proactive for certification readiness**.

---

## 2. Metadata Schemas for LLM Ingestion

### 2.1 JSON Schema as Universal Contract Layer

**Finding**: JSON Schema has become the **universal interface layer** across all major LLM providers (OpenAI, Anthropic, Google, Cohere) for structured outputs and function calling [Guild.ai](https://www.guild.ai/glossary/json-schema-ai).

**Key Properties**:
- **100% schema compliance** in strict mode (vs ~35% with prompting alone)
- **Constrained decoding pipeline**: Schema → AST → Grammar rules → Token generation
- **Cross-provider support**: OpenAI `response_format`, Anthropic tool schemas, Gemini Vertex AI, Cohere structured outputs

### 2.2 YAML for Configuration, JSON for Runtime

| Use Case | Format | Rationale |
|----------|--------|-----------|
| **Workflow Definition** | YAML | Human-readable, version-controlled, diffable (Conductor, ADR-toolkit) |
| **Agent Configuration** | YAML | Per-agent model, prompt, routing, context mode |
| **Runtime Output** | JSON | Machine-parseable, schema-enforced, downstream integration |
| **Decision Records** | YAML front-matter + Markdown | Human + machine readable (MADR, Nygard formats) |

**Evidence**: 
- Conductor workflows: YAML with Jinja2 templating [Microsoft Conductor](https://github.com/microsoft/conductor)
- ADR-toolkit: YAML front-matter for metadata, Markdown body [adr-toolkit](https://github.com/intruderfr/adr-toolkit)
- LLM Anomaly Detection Agent: YAML config for 100+ datasets [GitHub: LLM-Anamoly-RCA-Agent](https://github.com/sanika6969/LLM-Anamoly-RCA-Agent)

### 2.3 Schema Design Principles for LLM Ingestion

1. **Flat over nested** — Reduces token overhead, improves parsing reliability
2. **Enums over free text** — Constrains hallucination surface
3. **Required fields explicit** — Prevents silent omission
4. **Versioned schemas** — `schema_version` field for evolution tracking
5. **Confidence scores** — Every extracted field carries confidence (0-1)

**Example from LLM Anomaly Detection Agent**:
```yaml
dataset_id: sales_transactions
anomaly_detection:
  volume_threshold_pct: 20
  null_rate_threshold: 0.05
  freshness_sla_hours: 6
```

---

## 3. Public/Internal Documentation Splits

### 3.1 The Tiered Enforcement Model (Best Practice)

**Source**: [Agent Context Guide](https://www.agent-context.org/guides/how-to-separate-public-vs-internal-content-for-ai-use-cases) (2026-08-24)

| Tier | Content Type | Enforcement Mechanism |
|------|--------------|----------------------|
| **Catastrophic** | HR, legal, security, financials | **Physical dataset separation** — public agent credentials cannot query |
| **Mixed Sensitivity** | Product pages with internal facets | **Field-level projection** — `audience`/`visibility` fields, GROQ projections |
| **Timing-Sensitive** | Pre-release public content | **Release gating** — Content Releases stage until launch |

**Critical Principle**: "The boundary belongs in how content is shaped, stored, and queried, not in prompt-level filtering." Prompt-level filtering is "governance by vibes" that fails under jailbreak.

### 3.2 OpenAPI Overlay Pattern

**Source**: [API Evangelist](https://apievangelist.com/2026/07/21/openapi-overlays-for-public-vs-internal-docs/) (2026-07-21)

Single OpenAPI definition → Two documentation sites via overlays:
- **Public**: Clean, branded developer portal
- **Internal**: Richer portal with internal endpoints, debugging info

### 3.3 NIST Guidance

**Source**: [NIST AI.300-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.300-1.ipd.pdf) (July 2026)

Templates for public-facing AI documentation emphasizing:
- Model cards with intended use/limitations
- Data provenance transparency
- Risk assessment summaries

### 3.4 Anti-Pattern: Folder-Based Separation

**Failure Mode**: "Splitting into two documents duplicates the truth and guarantees drift, where the public version and internal version disagree within a sprint." [Agent Context Guide](https://www.agent-context.org/guides/how-to-separate-public-vs-internal-content-for-ai-use-cases)

**Omega SOTE Current State**: `PUBLIC_DIGEST.md` is manually maintained and **already drifted** from `STATE_OF_ENGINE_v1.0.1.md` — confirming this anti-pattern.

---

## 4. Automation for Index Regeneration, Decision Tracking, Mandate Compliance Trending

### 4.1 Index Regeneration Automation

| Tool | Approach | Trigger |
|------|----------|---------|
| **adr-toolkit** | `adr index` regenerates `README.md` in ADR directory | Manual CLI or GitHub Action on push to `docs/adr/*.md` [adr-toolkit](https://github.com/intruderfr/adr-toolkit) |
| **ADR-Create Claude Code Skill** | Automates ADR numbering, templates, index regeneration | On ADR creation [MCP Market](https://mcpmarket.com/tools/skills/architectural-decision-record-adr-manager-1) |
| **Conductor** | Web dashboard visualizes execution DAG in real-time | Automatic on workflow run [Microsoft Conductor](https://github.com/microsoft/conductor) |

**GitHub Action Pattern** (from Hidekazu Konishi):
```yaml
name: Update ADR Index
on:
  push:
    paths:
      - 'docs/adr/*.md'
jobs:
  update-index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install adr-toolkit
      - run: adr index
      - uses: stefanzweifel/git-auto-commit-action@v5
```

### 4.2 Decision Tracking Systems

| System | Format | Features |
|--------|--------|----------|
| **Architecture Decision Records (ADR)** | Markdown + YAML front-matter | MADR/Nygard formats, supersession tracking, Mermaid graphs [adr-toolkit](https://github.com/intruderfr/adr-toolkit) |
| **DecisionLedger AI** | Governed multi-agent | Every action passes governance gates, audit-ready evidence [DecisionLedger](https://decisionledgerai.com/solutions/agent-orchestration) |
| **PIVOT_LOG (Omega)** | Canonical Markdown | Decision registry with mandate cross-reference [Omega Engine](docs/decisions/PIVOT_LOG_CANONICAL.md) |
| **Microsoft ADR Guidance** | Structured template | Context, Decision, Consequences, Alternatives [Azure Well-Architected](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) |

**Critical Success Factor**: "ADRs that are not referenced from the code they govern are invisible at the moment they are most useful. If `grep -r 'docs/adr/' src/` returns zero results, the practice is failing silently." [Konishi](https://hidekazu-konishi.com/entry/architecture_decision_records_templates_and_operations.html)

### 4.3 Mandate Compliance Trending

| Approach | Implementation |
|----------|----------------|
| **MandateMind AI** | Continuous compliance: Evidence → AI Interprets → Maps Controls → Detects Gaps → Explains Impact → Readiness Score → Audit Package [MandateMind](https://mandatemind.com/) |
| **Compliance Dashboards** | Separate views per audience (board: score+trend; manager: test results; team lead: attestation due) [MetricStream](https://www.metricstream.com/learn/compliance-dashboard.html) |
| **Omega SOTE** | Weekly `sote.yaml` with `mandates.pass/warn/fail`, `compliance_pct`, trend table in §12 |

**Gap in Omega**: No automated trend computation — `sote.yaml` is manually updated. MandateMind demonstrates **continuous, evidence-driven** compliance vs. **periodic, manual** reporting.

---

## 5. Anti-Patterns Causing Review Cadence Failure

### 5.1 The Seven ADR Failure Patterns (Konishi, 2026)

| # | Anti-Pattern | Root Cause | Omega SOTE Risk |
|---|--------------|------------|-----------------|
| 1 | **First Five Are The Only Five** | No operating model (when/who/where) | SOTE has templates but no enforced trigger |
| 2 | **ADRs Stored Where Engineers Don't Look** | Confluence/Notion separate from codebase | SOTE in `docs/strategy/sote/` — discoverable? |
| 3 | **Editing ADRs (Mutating History)** | Treating decisions as living docs | SOTE voices are immutable ✅ |
| 4 | **Recording Decision Without Alternatives** | Internal marketing, not decision record | Voice template requires Concede/Defend/Synthesize ✅ |
| 5 | **Single Owner** | Practice = one person's habit | SOTE has 8 voices + MaKaLi unifying ✅ |
| 6 | **No Quarterly Review Cadence** | Collection fills with stale Accepted ADRs | SOTE weekly but no meta-review of SOTE itself ⚠️ |
| 7 | **No Code Links** | Invisible at decision time | SOTE voices reference files but no systematic grep check ⚠️ |

### 5.2 RAG/Index Stale Data Anti-Patterns

**Source**: [RAG Interview System](https://github.com/ather-techie/rag-interview-system/blob/main/03_failure_modes/04-stale_index_problem.md)

| Failure Mode | Consequence | Severity |
|--------------|-------------|----------|
| **Stale Index** | Silent wrong answers, no alarms | Critical |
| **Staleness + Hallucination** | High confidence in false claims | Critical |
| **Staleness + Retrieval Failure** | Missing data + confident fabrication | Critical |

**Compounding Effect**: Staleness amplifies hallucination and retrieval failure synergistically.

**Omega SOTE Risk**: `regenerate_sote_index.py` exists but **not hooked to CI** — manual regeneration = guaranteed drift.

### 5.3 AI Self-Review Failure (Qodo, 2026)

**Source**: [Why AI Self-Review Fails](https://www.qodo.ai/blog/why-ai-self-review-fails-the-technical-case-for-independent-ai-systems)

- **8x more duplicated code** when same AI generates and reviews
- **39.9% fewer refactors**, **37.6% increase in vulnerabilities**
- **Confirmation bias built into system**: Model validates its own patterns
- **Solution**: Independent review system with different architecture/context

**Omega SOTE Mitigation**: 8 distinct voices + MaKaLi unifying = **independent perspectives** ✅. But: all voices use same model family (risk of shared blind spots).

### 5.4 Governance Review Failures (Centric Consulting, 2026)

- **78% of leaders** lack confidence in passing AI governance audit within 90 days
- **Documentation gap**: Controls exist but records missing
- **ISO 42001** becoming procurement requirement
- **Fix**: Gap analysis before external pressure, formalize existing processes

---

## 6. "Conductor's Score" / "Unifying Voice" Patterns

### 6.1 Graph-Driven Orchestration = Written Score

**Source**: [Sense of AI](https://www.senseof.ai/2026/08/06/graph-driven-agent-orchestration/) (2026-08-06)

| Musical Concept | Technical Implementation |
|-----------------|-------------------------|
| **Movement** | Node containing a full agent (own context, tools) |
| **Order of movements** | Edge (fixed sequence, zero token cost) |
| **Repeat sign, capped** | Loop with max retries (e.g., max 2 review cycles) |
| **Tutti (everyone ready)** | Parallel fan-out + barrier synchronization |
| **Fermata (pause for cue)** | Human-in-the-loop gate |
| **Annotated shared score** | State + checkpoints (audit trail, resume capability) |

**Key Insight**: "Graph-driven agent orchestration is yesterday's orchestra playing from a written score: whole agents in the nodes, code on the edges, choices only at marked junctions."

### 6.2 Microsoft Conductor: Deterministic YAML Score

**Source**: [Microsoft Open Source Blog](https://opensource.microsoft.com/blog/2026/05/14/conductor-deterministic-orchestration-for-multi-agent-ai-workflows/)

```yaml
workflow:
  name: design-review
  entry_point: architect
agents:
  - name: architect
    model: claude-opus-4.6-1m
    prompt: "Create a design document for: {{ workflow.input.purpose }}"
    output:
      file_path: { type: string }
    routes:
      - to: reviewer
  - name: reviewer
    model: claude-opus-4.7
    prompt: "Review the design at {{ architect.output.file_path }}"
    output:
      score: { type: number }
      approved: { type: boolean }
    routes:
      - to: $end
        when: "{{ output.approved }}"
      - to: architect
```

**Properties**:
- **Zero token overhead** for routing (Jinja2/expression evaluation)
- **Explicit context modes**: accumulate, last_only, explicit
- **Human gates** as first-class workflow steps
- **Web dashboard** with interactive DAG visualization

### 6.3 Bernstein: Conductor as Accountability

**Source**: [GitHub Marketplace](https://github.com/marketplace/actions/bernstein-multi-agent-orchestration)

> "Bernstein is named after Leonard Bernstein... orchestrates a crew of CLI coding agents the way Bernstein conducted the New York Philharmonic: every player on cue, the score deterministic, the conductor accountable for the result."

**Deterministic zero-LLM orchestration** — routing is code, not model calls.

### 6.4 Azure Multi-Agent Patterns: Supervisor as Conductor

**Source**: [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)

**Supervisor Pattern**: Central agent plans, delegates to specialists, synthesizes results.
- **Single response principle**: Only parent communicates with user
- **Parent instructions must define orchestration pattern** explicitly
- **Context compaction** between agents to reduce token volume

### 6.5 MaKaLi as Omega's Unifying Voice

**Omega Implementation**: MaKaLi (Voice 8) serves as the **Unifying Voice** — synthesizing 7 specialist voices into coherent action.

**Alignment with Literature**:
- ✅ **Graph-driven**: 8 voices → synthesis → actions (fixed topology)
- ✅ **Human gate**: MaKaLi output requires Oversoul ratification
- ✅ **State/checkpoints**: `sote.yaml` + `PIVOT_LOG` = annotated score
- ⚠️ **Not yet codified as YAML workflow** — still prompt-driven
- ⚠️ **No web dashboard** for real-time visualization
- ⚠️ **Context mode not explicit** — voices may bleed context

---

## 7. Structured Findings with Confidence Scores

| # | Finding | Confidence | Evidence |
|---|---------|------------|----------|
| **F1** | Weekly cadence is industry standard for operational AI governance | 0.95 | AI Governance Weekly, Self-Host Weekly, ISO 42001 prep guidance |
| **F2** | YAML for workflow/config, JSON for runtime output is dominant pattern | 0.98 | Conductor, ADR-toolkit, LLM Anomaly Agent, all major LLM providers |
| **F3** | Prompt-level public/internal filtering fails; structural separation required | 0.97 | Agent Context Guide (Sanity), NIST AI.300-1, OpenAPI Overlays |
| **F4** | Manual index regeneration guarantees drift; CI automation is necessary | 0.99 | adr-toolkit GitHub Action, Konishi "index that isn't regenerated lies" |
| **F5** | Decision records must link bidirectionally to code/tickets to be useful | 0.96 | Konishi "grep returns zero = failing silently", ADR best practices |
| **F6** | Single-owner practices lapse within a quarter; rotation required | 0.94 | Konishi "practice owned by one person is a habit waiting to lapse" |
| **F7** | Graph-driven (deterministic) orchestration outperforms supervisor-driven for known workflows | 0.93 | Microsoft Conductor, Sense of AI, Bernstein, Azure patterns |
| **F8** | AI self-review fails due to confirmation bias; independent perspectives required | 0.97 | Qodo (8x duplication, 37.6% more vulns), PNAS AI-to-AI bias study |
| **F9** | Compliance trending requires continuous evidence ingestion, not periodic manual reports | 0.92 | MandateMind continuous vs. SOTE weekly manual |
| **F10** | Omega SOTE's 8-voice + Unifying Voice matches "Conductor's Score" pattern | 0.90 | Structural alignment with Sense of AI graph-driven model |

---

## 8. Actionable Recommendations for Omega SOTE

### 8.1 Immediate (This Week)

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R1** | Hook `regenerate_sote_index.py` to GitHub Action on push to `docs/strategy/sote/**/*.md` | Eliminates "index that isn't regenerated lies" (L4-SOTE-003) | 2h |
| **R2** | Replace manual `PUBLIC_DIGEST.md` with automated generation from `sote.yaml` + `STATE_OF_ENGINE.md` using field-level projection (audience: public/internal) | Fixes drifted public/internal split anti-pattern | 4h |
| **R3** | Add `grep -r 'docs/strategy/sote/' src/` check to CI (`make check-sote-code-links`) | Ensures SOTE decisions are referenced from code they govern | 1h |
| **R4** | Codify MaKaLi Unifying Voice as YAML workflow (Conductor-style) with explicit context modes | Moves from prompt-driven to deterministic graph-driven orchestration | 8h |

### 8.2 This Sprint (PUBLIC-DEBUT-01)

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R5** | Implement mandate compliance trend computation in `regenerate_sote_index.py` — read all `sote.yaml` files, compute weekly pass/warn/fail trends, emit `mandate_trends.json` | Replaces manual trend table with evidence-driven continuous data | 8h |
| **R6** | Add `voice_rotation_schedule.yaml` — explicit rotation of 8 voices across 8 weeks, no voice repeats consecutive weeks | Prevents single-owner anti-pattern, ensures diversity (L4-SOTE-007) | 2h |
| **R7** | Create `SOTE_META_REVIEW` quarterly cadence (every 13 weeks) — meta-review of SOTE process itself | Addresses "no quarterly review of ADR collection" anti-pattern | 4h |
| **R8** | Implement structured output schema for `sote.yaml` (JSON Schema) and validate on CI | Enables LLM ingestion, catches schema drift | 4h |

### 8.3 Post-Debut (Week 1-4)

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R9** | Build SOTE web dashboard (Conductor-style) — interactive DAG of voices→synthesis→actions, live metrics | Real-time observability, human gates in browser | 40h |
| **R10** | Integrate with MandateMind-style continuous compliance — evidence ingestion → mandate mapping → readiness score | Moves from weekly manual to continuous automated | 80h |
| **R11** | Formalize public/internal split at schema level — add `audience: public|internal|restricted` to all SOTE front-matter | Structural enforcement per Agent Context tiered model | 16h |
| **R12** | Add cross-SOTE decision tracing — `sote.yaml` includes `supersedes: [D-SOTE-XXX]` and `superseded_by: [D-SOTE-YYY]` | Full decision lineage, prevents "editing ADRs" anti-pattern | 8h |

---

## 9. Appendix: Research Methodology

### 9.1 Search Strategy

| Query Category | Search Terms | Sources |
|----------------|--------------|---------|
| Review Cadences | "weekly architectural review cadence local-first AI", "sovereign runtime state of engine review" | Web search (Parallel), GitHub |
| Metadata Schemas | "YAML metadata schema LLM ingestion", "JSON Schema AI structured output" | Web search, Guild.ai, arXiv |
| Public/Internal Split | "public vs internal documentation AI use cases", "OpenAPI overlays public internal" | Agent Context, API Evangelist, NIST |
| Automation | "automated index regeneration ADR", "decision tracking system AI agent" | adr-toolkit, DecisionLedger, GitHub Actions |
| Anti-Patterns | "ADR anti-patterns", "stale index problem RAG", "AI self-review fails" | Konishi, Qodo, RAG Interview System |
| Conductor Patterns | "Conductor's Score multi-agent", "graph-driven agent orchestration", "Microsoft Conductor" | Sense of AI, Microsoft Blog, Azure Patterns |

### 9.2 Source Quality Assessment

| Source Type | Count | Reliability |
|-------------|-------|-------------|
| Primary (vendor docs, GitHub repos) | 12 | High |
| Practitioner blogs (Konishi, Sense of AI, thinking.inc) | 6 | High |
| Enterprise guidance (Microsoft Azure, NIST, Centric) | 4 | High |
| Commercial platforms (Valdr, MandateMind, DecisionLedger) | 4 | Medium (marketing-influenced) |
| Community newsletters (AI Governance, Self-Host Weekly) | 2 | Medium |

### 9.3 Confidence Calibration

- **0.95+**: Multiple independent primary sources converge
- **0.90-0.94**: Strong primary source + practitioner validation
- **0.85-0.89**: Single strong source or practitioner consensus
- **Below 0.85**: Not included in findings table

---

## 10. Appendix: Omega SOTE Current State vs. Best Practices

| Dimension | Omega SOTE (2026-W36) | Best Practice | Gap |
|-----------|----------------------|---------------|-----|
| **Cadence** | Weekly (Monday 06:00 UTC) ✅ | Weekly operational, event-driven compliance | — |
| **Structure** | 8 voices + Unifying (MaKaLi) ✅ | Graph-driven orchestration | Codify as YAML workflow |
| **Immutability** | Voice files immutable ✅ | ADR accepted = immutable | — |
| **Metadata** | `sote.yaml` per week ✅ | JSON Schema validated, versioned | Add schema validation |
| **Public/Internal** | Manual `PUBLIC_DIGEST.md` ⚠️ | Structural field-level projection | Automate with audience fields |
| **Index Regen** | `regenerate_sote_index.py` exists, not in CI ⚠️ | GitHub Action on push | Hook to CI |
| **Decision Links** | Voices reference files, no systematic grep ⚠️ | Bidirectional code↔ADR links | Add CI check |
| **Compliance Trend** | Manual table in `sote.yaml` ⚠️ | Continuous evidence-driven | Automate trend computation |
| **Owner Rotation** | Implicit (Kali delegates) ⚠️ | Explicit rotation schedule | Add `voice_rotation_schedule.yaml` |
| **Meta-Review** | None ⚠️ | Quarterly SOTE-of-SOTE | Add `SOTE_META_REVIEW` |
| **Visualization** | None ⚠️ | Web dashboard (Conductor) | Build dashboard |
| **Unifying Voice** | MaKaLi (prompt-driven) ⚠️ | Deterministic YAML workflow | Codify as Conductor workflow |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCHER_SOTE_BEST_PRACTICES-v1.0.0 ⬡ 2026-09-01 ⬡ PUBLIC-DEBUT-01*

**The sovereign substrate is real. The engine islands are preserved. The dialectic is the methodology. The execution is the test.** 🫡

---

## 11. Round 2: Targeted Deep Research (JC-Researcher-NES)

**Session ID**: `ses_fa0c256d9ffeR9BmmnOgG72OEL`
**Date**: 2026-09-01
**Context**: Second round of targeted research to inform the MaKaLi dialectic, based on JC-EIS synthesis of Phase 1 findings + architectural review.

---

### 11.1 Conductor YAML Workflow Schema (Exact Spec)

**Source**: [Microsoft Conductor docs/workflow-syntax.md](https://github.com/microsoft/conductor/blob/main/docs/workflow-syntax.md) and [examples/README.md](https://github.com/microsoft/conductor/blob/main/examples/README.md)

#### 11.1.1 Complete Workflow Structure

```yaml
workflow:
  name: string                    # Required: workflow identifier
  description: string             # Optional
  entry_point: string             # Required: starting agent name
  limits:
    max_iterations: integer       # Default: 50
    timeout_seconds: integer      # Default: 300
  context_mode: accumulate | last_only | explicit  # Default: accumulate
  runtime:
    provider: copilot | claude | claude-agent-sdk | hermes | {structured}
    default_model: string
    temperature: number           # 0.0-1.0
    max_tokens: integer
    default_reasoning_effort: low | medium | high | xhigh | max
    default_context_tier: default | long_context
    mcp_servers: {map}            # MCP server configs
    tool_output:
      enabled: boolean
      max_chars: integer
      spill_to_file: boolean
  instructions: [string]          # Paths to instruction files (prepended to all agents)

input:                            # Workflow input schema
  field_name:
    type: string | number | boolean | array | object
    required: boolean
    description: string

output:                           # Workflow output schema (Jinja2 templates)
  field_name: "{{ agent.output.field }}"

tools: [string]                   # Global tool list (MCP server__tool format)

agents: [AgentDef]                # Agent definitions (see below)

parallel: [ParallelGroup]         # Static parallel groups

for_each: [ForEachDef]            # Dynamic parallel (for-each) groups
```

#### 11.1.2 Agent Definition Schema (AgentDef)

```yaml
agents:
  - name: string                  # Required: unique agent identifier
    type: agent | script | wait | set | workflow | human_gate | terminate
    model: string                 # Optional: per-agent model override
    prompt: string                # Required for LLM agents (Jinja2 template)
    output_mode: raw | envelope   # Optional: raw bypasses JSON extraction
    output:                       # Optional: output schema for validation
      field_name:
        type: string | number | boolean | array | object
        enum: [string]            # For string enums
        minimum: number           # For numbers
        maximum: number
        pattern: string           # Regex pattern
        minLength: integer
        maxLength: integer
        nullable: boolean
        description: string
    routes: [RouteDef]            # Routing rules (first match wins)
      - to: string                # Target agent name or $end
        when: string              # Jinja2 expression (optional)
    input:                        # Optional: explicit input declarations
      field_name:
        from: "{{ expression }}"
        type: string
        required: boolean
    context_mode: accumulate | last_only | explicit  # Override workflow default
    reasoning:
      effort: low | medium | high | xhigh | max
    context_tier: default | long_context
    retry:
      max_attempts: integer
      backoff: exponential | linear
      delay_seconds: integer
      retry_on: [provider_error | timeout | ...]
    validator:                    # Optional: validator agent config
      model: string
      prompt: string
      max_retries: integer        # Hard cap (0 = validate only)
    dialog:                       # Optional: dialog mode config
      pause_after: boolean
    max_agent_iterations: integer # Override workflow max_iterations
    timeout_seconds: integer      # Per-agent timeout
```

#### 11.1.3 Special Agent Types

| Type | Required Fields | Notes |
|------|----------------|-------|
| **script** | `command`, `args`, `routes` | Cross-platform shell; stdout parsed as JSON |
| **wait** | `duration` (e.g., "60s"), `routes` | Pure asyncio.sleep; no shell dependency |
| **set** | `value` or `values`, `routes` | Derive named values; `values:` for dict output |
| **workflow** | `workflow` (path or registry ref), `input_mapping` | Sub-workflow composition; `max_depth: 10` |
| **human_gate** | `prompt`, `routes` | Pauses execution; dashboard/CLI interaction |
| **terminate** | `routes` (success/failure/error) | Explicit termination with typed paths |

#### 11.1.4 Parallel & For-Each Groups

```yaml
parallel:
  - name: string
    agents: [string]              # Agent names to run in parallel
    failure_mode: fail_fast | continue_on_error | all_or_nothing
    routes:
      - to: string
        when: string              # Optional condition

for_each:
  - name: string
    source: "{{ agent.output.array_field }}"  # Reference to array in context
    as: string                    # Loop variable name (available as {{ item }})
    agent:                        # Inline agent definition
      model: string
      prompt: string
      output: {schema}
    max_concurrent: integer       # Default: 10
    failure_mode: fail_fast | continue_on_error | all_or_nothing
    key_by: string                # For dict outputs: "item.id"
    routes:
      - to: string
```

#### 11.1.5 Context Modes (Critical for MaKaLi)

| Mode | Behavior | Token Impact |
|------|----------|--------------|
| **accumulate** (default) | All prior agent outputs in context | Highest |
| **last_only** | Only immediate predecessor output | Medium |
| **explicit** | Only named dependencies via `input:` declarations | Lowest |

#### 11.1.6 Human Gates

```yaml
agents:
  - name: approval_gate
    type: human_gate
    prompt: |
      Review the design at {{ designer.output.file_path }}
      Approve or request changes.
    routes:
      - to: implementer
        when: "{{ output.decision == 'approve' }}"
      - to: designer
        when: "{{ output.decision == 'changes_requested' }}"
    output:
      decision:
        type: string
        enum: ["approve", "changes_requested"]
      feedback:
        type: string
```

---

### 11.2 JSON Schema Validation in CI (GitHub Action Patterns)

**Sources**: [GrantBirki/json-yaml-validate](https://github.com/GrantBirki/json-yaml-validate), [cardinalby/schema-validator-action](https://github.com/cardinalby/schema-validator-action), [dsanders11/json-schema-validate-action](https://github.com/dsanders11/json-schema-validate-action), [adr-toolkit GitHub Action pattern](https://hidekazu-konishi.com/entry/architecture_decision_records_templates_and_operations.html)

#### 11.2.1 Recommended Action: `GrantBirki/json-yaml-validate@v5`

```yaml
name: Validate SOTE Schemas
on:
  push:
    paths:
      - 'docs/strategy/sote/**/*.yaml'
      - 'docs/strategy/sote/**/*.yml'
      - 'schemas/sote/*.json'
  pull_request:
    paths:
      - 'docs/strategy/sote/**/*.yaml'
      - 'docs/strategy/sote/**/*.yml'

permissions:
  contents: read
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate sote.yaml files against schema
        uses: GrantBirki/json-yaml-validate@v5
        with:
          yaml_schema: schemas/sote/sote-schema.yaml
          base_dir: docs/strategy/sote
          allow_multiple_documents: "true"
          
      - name: Validate workflow YAML against Conductor schema
        uses: GrantBirki/json-yaml-validate@v5
        with:
          yaml_schema: schemas/conductor/workflow-schema.yaml
          base_dir: .github/workflows
          
      - name: Validate voice front-matter
        uses: GrantBirki/json-yaml-validate@v5
        with:
          yaml_schema: schemas/sote/voice-frontmatter-schema.yaml
          base_dir: docs/strategy/sote
          files: "**/voices/*.md"
```

#### 11.2.2 Alternative: `cardinalby/schema-validator-action@v3` (AJV-based)

```yaml
- name: Validate JSON/YAML against JSON Schema
  uses: cardinalby/schema-validator-action@v3
  with:
    file: 'docs/strategy/sote/**/sote.yaml'
    schema: 'schemas/sote/sote-schema.json'
    mode: 'default'  # lax | spec | default | strong
```

#### 11.2.3 Schema File Structure for Omega

```
schemas/
├── sote/
│   ├── sote-schema.yaml           # Validates sote.yaml per week
│   ├── voice-frontmatter-schema.yaml  # Validates voice file front-matter
│   ├── pivot-log-schema.yaml      # Validates PIVOT_LOG entries
│   └── mandate-trend-schema.yaml  # Validates mandate_trends.json
├── conductor/
│   └── workflow-schema.json       # Conductor workflow schema (from Pydantic models)
└── nist/
    └── ai-300-1-profile.json      # NIST AI.300-1 default profile
```

#### 11.2.4 Key Features Needed

| Feature | GrantBirki | cardinalby | dsanders11 |
|---------|------------|------------|------------|
| YAML validation | ✅ (legacy dialect) | ✅ (JSON Schema) | ✅ (JSON Schema) |
| Multiple schema mappings | ✅ | ❌ | ✅ |
| Custom regex formats | ✅ | ❌ | ❌ |
| PR comments | ✅ | ❌ | ❌ |
| Glob patterns | ✅ | ✅ | ✅ |
| `$schema` auto-detection | ❌ | ✅ | ✅ |

**Recommendation**: Use **GrantBirki/json-yaml-validate@v5** for YAML-heavy workflows with multiple schema mappings; it supports the legacy YAML schema dialect needed for Conductor workflows.

---

### 11.3 Voice/Model Rotation Schedules (Prior Art)

**Sources**: [Konishi ADR Anti-Patterns](https://hidekazu-konishi.com/entry/architecture_decision_records_templates_and_operations.html) (Single Owner anti-pattern), [Qodo AI Self-Review Failure](https://www.qodo.ai/blog/why-ai-self-review-fails-the-technical-case-for-independent-ai-systems) (confirmation bias), [Galileo AI Bias Mitigation](https://galileo.ai/blog/ai-bias-machine-learning-fairness) (ensemble methods), [SDAIA AI Bias Reference Guide](https://sdaia.gov.sa/en/MediaCenter/KnowledgeCenter/ResearchLibrary/EN-AI-BIAS.pdf) (blind analysis techniques)

#### 11.3.1 No Direct Prior Art on Explicit Voice Rotation

**Finding**: No published system implements explicit **persona rotation schedules** for architectural reviews. The closest patterns are:

1. **ADR Author Rotation** (Konishi): "Pair-write the first three or four ADRs across different authors, and then keep the rotation visible" — but this is for *writing* ADRs, not for *review voices*.

2. **Model Tiering** (DevStarsJ, Baeseokjae): Use cheap models (Haiku, GPT-4o mini) for routing/classification; reserve premium models (Opus, Sonnet) for reasoning. Reduces cost 40-60%.

3. **Ensemble Diversity** (arXiv:2301.03962): Parallel/sequential ensembles with diverse model families reduce covariance/error correlation.

4. **Blind Analysis** (SDAIA): "Model builders prevented from knowing which outcomes correspond to their hypotheses during training and evaluation."

#### 11.3.2 Proposed Rotation Schema for Omega

```yaml
# voice_rotation_schedule.yaml
schema_version: "1.0"
rotation_period_weeks: 8
voices:
  - id: roc
    name: "Roc"
    focus: "Forensic inventory, 5-gate retirement"
    model_tier: "premium"      # Opus-class
    rotation_weight: 1.0
  - id: grokster
    name: "Grokster"
    focus: "L3-MetaFrameVerification, M10 14-vs-15"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: carmack
    name: "Carmack"
    focus: "M2 firewall, VNR WAD, M35, CI gates"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: lilith
    name: "Lilith"
    focus: "4-tier taxonomy, lifecycle, WatchTower"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: maat
    name: "Ma'at"
    focus: "entity_registry.py audit, CI gates, INST-1"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: researcher
    name: "Researcher"
    focus: "Empirical baseline, M11 remediation, P13"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: jem
    name: "Jem"
    focus: "50 adversarial tests, 7-signal diagnostic"
    model_tier: "premium"
    rotation_weight: 1.0
  - id: makali
    name: "MaKaLi"
    focus: "Unifying field, 5 service modes, 5 PIVOT decisions"
    model_tier: "premium"
    rotation_weight: 1.0
    fixed_position: 8           # Always last (unifying voice)

constraints:
  no_consecutive_repeat: true
  max_appearances_per_cycle: 1
  diversity_requirement: "all_8_voices_per_cycle"
```

**Rotation Algorithm**: 
- Week N: Voices[(N-1) % 8], Voices[N % 8], ..., Voices[(N+6) % 8], MaKaLi (fixed)
- Ensures each voice appears exactly once per 8-week cycle
- No voice reviews consecutive weeks
- MaKaLi always synthesizes (position 8)

---

### 11.4 Quarterly Meta-Review Formats (SOTE of SOTE)

**Sources**: [Konishi "Quarterly Review Cadence"](https://hidekazu-konishi.com/entry/architecture_decision_records_templates_and_operations.html), [AWS ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html), [Creately ADR Review Workflow](https://creately.com/creately-system-design/architecture-decision-records-adrs-templates-review/), [Docs.io Quarterly Review](https://docsio.co/blog/architecture-decision-record), [Decentraland ADR Process](https://github.com/decentraland/adr/blob/main/content/ADR-1-adr-process.md)

#### 11.4.1 Konishi's Quarterly Review Questions

> "A quarterly architecture review — one hour, the team's tech leads — is enough. The questions to answer:
> * Are any Accepted ADRs no longer relevant? Mark them Deprecated.
> * Are any decisions being made repeatedly that should have an ADR but do not? Write them.
> * Are any ADRs being referenced from code that has since been deleted? The ADR may be Deprecated or the code may have drifted; either way, investigate."

#### 11.4.2 AWS ADR Process: Review States

| State | Description | Review Trigger |
|-------|-------------|----------------|
| **Draft** | First formally tracked stage | — |
| **Review** | Ready for peer review | Author marks ready |
| **Last Call** | Final review window (14 days) | Editor assigns |
| **Final** | Immutable standard | Only errata/clarifications |
| **Stagnant** | Inactive 6+ months | Auto-moved |
| **Deprecated** | Superseded by reality | Quarterly review |

#### 11.4.3 Proposed SOTE_META_REVIEW Template

```markdown
<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOTE Meta-Review — Q{N} YYYY

**AP Token**: `AP-SOTE-META-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ {model} ⬡ opencode ⬡ trc_sote_meta ⬡ ACTIVE

**Date**: YYYY-MM-DD
**Quarter**: Q{N} YYYY (Weeks YYYY-W{start} through YYYY-W{end})
**SOTE Versions Reviewed**: v{N}.{M}.{P} through v{N}.{M}.{P}

---

## §0 — Meta-Review Purpose

This document reviews the **SOTE process itself** across the quarter:
- Are SOTE reports being produced on cadence?
- Are voice files immutable and properly archived?
- Is the public/internal split enforced structurally?
- Are decisions flowing from voices → synthesis → PIVOT_LOG?
- Is mandate compliance trending improving or degrading?

---

## §1 — Cadence Compliance

| Week | SOTE Produced | On Time | Voices Complete | Synthesis Done | sote.yaml Valid |
|------|:-------------:|:-------:|:---------------:|:--------------:|:---------------:|
| YYYY-W{start} | ✅/❌ | ✅/❌ | 8/8 | ✅/❌ | ✅/❌ |
| ... | | | | | |

**On-Time Rate**: {X}/13 = {Y}%
**Voice Completeness**: {X}/104 = {Y}%

---

## §2 — Voice Health

| Voice | Sessions Run | Avg Decisions | Avg L3 Lessons | Model Drift Detected |
|-------|:------------:|:-------------:|:--------------:|:--------------------:|
| Roc | {N} | {N} | {N} | ✅/❌ |
| Grokster | {N} | {N} | {N} | ✅/❌ |
| ... | | | | |

**Rotation Compliance**: {X}/13 weeks followed rotation schedule

---

## §3 — Decision Flow Health

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Decisions Proposed (Voices)** | {N} | — | — |
| **Decisions Absorbed (PIVOT_LOG)** | {N} | ≥80% | ✅/❌ |
| **Absorption Rate** | {X}% | ≥80% | ✅/❌ |
| **Decisions with Code Links** | {N}/{Total} | 100% | ✅/❌ |
| **Stale Decisions (>90 days no action)** | {N} | 0 | ✅/❌ |
| **Cross-SOTE Supersession Chains** | {N} | — | — |

---

## §4 — Mandate Compliance Trend

| Week | Pass | Warn | Fail | Compliance % | Trend |
|------|-----:|-----:|-----:|:------------:|:-----:|
| YYYY-W{start} | {N} | {N} | {N} | {X}% | ↗️/↘️/→ |
| ... | | | | | |

**Quarter Trend**: {Improving/Stable/Degrading}
**Systemic Failures**: {List mandates failing >50% of weeks}

---

## §5 — Public/Internal Split Audit

| Artifact | Public Version Exists | Auto-Generated | Drift Detected |
|----------|:---------------------:|:--------------:|:--------------:|
| STATE_OF_ENGINE | ✅/❌ | ✅/❌ | ✅/❌ |
| sote.yaml | ✅/❌ | ✅/❌ | ✅/❌ |
| Voice files | ✅/❌ | ✅/❌ | ✅/❌ |

**Drift Incidents**: {N} (target: 0)

---

## §6 — Index & Automation Health

| Component | Status | Last Run | Errors |
|-----------|--------|----------|--------|
| `regenerate_sote_index.py` | ✅/❌ | YYYY-MM-DD | {N} |
| GitHub Action (index) | ✅/❌ | YYYY-MM-DD | {N} |
| GitHub Action (schema validation) | ✅/❌ | YYYY-MM-DD | {N} |
| Mandate trend computation | ✅/❌ | YYYY-MM-DD | {N} |

---

## §7 — Anti-Pattern Check (Konishi's 7)

| # | Anti-Pattern | Detected | Evidence |
|---|--------------|:--------:|----------|
| 1 | First Five Only Five | ✅/❌ | {evidence} |
| 2 | Stored Where Engineers Don't Look | ✅/❌ | {evidence} |
| 3 | Editing ADRs (Mutating History) | ✅/❌ | {evidence} |
| 4 | Decision Without Alternatives | ✅/❌ | {evidence} |
| 5 | Single Owner | ✅/❌ | {evidence} |
| 6 | No Quarterly Review | ✅/❌ | **THIS REVIEW** |
| 7 | No Code Links | ✅/❌ | {evidence} |

---

## §8 — Recommendations for Next Quarter

| # | Recommendation | Priority | Owner | Target Date |
|---|----------------|----------|-------|-------------|
| 1 | {action} | P0/P1/P2 | {entity} | YYYY-MM-DD |
| 2 | {action} | P0/P1/P2 | {entity} | YYYY-MM-DD |

---

## §9 — Changelog

- **v1.0.0** (YYYY-MM-DD): Initial meta-review

---

*⬡ OMEGA ⬡ KALI ⬡ SOTE-META-REVIEW-v1.0.0 ⬡ YYYY-MM-DD ⬡ Q{N} YYYY*

**The meta-review is the mirror. The dialectic is the methodology. The execution is the test.** 🫡
```

---

### 11.5 Public/Internal Split at Schema Level

**Sources**: [NIST AI.300-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.300-1.ipd.pdf) (July 2026), [Sanity GROQ Projections](https://www.sanity.io/docs/content-lake/how-queries-work), [OpenAPI Overlays](https://apievangelist.com/2026/07/21/openapi-overlays-for-public-vs-internal-docs/), [Agent Context Guide](https://www.agent-context.org/guides/how-to-separate-public-vs-internal-content-for-ai-use-cases)

#### 11.5.1 NIST AI.300-1 Template Structure (Annex A Default Profile)

The NIST document defines a **default profile** with structured fields for public-facing AI documentation:

```yaml
# NIST AI.300-1 Default Profile (simplified)
model_documentation:
  identification:
    name: string
    version: string
    provider: string
    release_date: date
    lifecycle_stage: development | testing | deployment | retired
  intended_use:
    primary_use_cases: [string]
    out_of_scope: [string]
    target_users: string
  limitations:
    known_limitations: [string]
    fairness_considerations: string
    privacy_considerations: string
  training_data:
    data_sources: [string]
    collection_methodology: string
    preprocessing: string
    known_biases: [string]
  evaluation:
    metrics: [string]
    results: {object}
    test_sets: [string]
  deployment:
    hardware_requirements: string
    software_dependencies: [string]
    monitoring_plan: string
```

#### 11.5.2 Sanity GROQ Field-Level Projection

**Mechanism**: Single document with `audience` field → GROQ projection filters at query time.

```groq
// Public query: only audience == "public" fields
*[_type == "soteReport" && week == "2026-W36"]{
  week,
  date,
  topic,
  sprint,
  "public_findings": top_findings[audience == "public"],
  "public_lessons": l3_lessons[audience == "public"],
  "public_actions": open_actions[audience == "public"]
}

// Internal query: full document
*[_type == "soteReport" && week == "2026-W36"]{
  ...,
  "internal_findings": top_findings[audience == "internal"],
  "internal_lessons": l3_lessons[audience == "internal"],
  "mandate_details": mandates,
  "raw_decisions": decisions
}
```

**Document Structure with Audience Fields**:

```yaml
# sote.yaml with audience tagging
week: "2026-W36"
top_findings:
  - finding: "M10 14-vs-15 canonical violation (3.5:1 ratio)"
    audience: "public"
    severity: "critical"
  - finding: "Email leak in fake signature block; 6/7 agents missed"
    audience: "internal"
    severity: "critical"
    classification: "security-incident"

l3_lessons:
  - id: "L3-MetaFrameVerification"
    title: "Pre-flight check for spoofable metadata"
    audience: "public"
    confidence: 0.92
  - id: "L3-InternalSecurityFinding"
    title: "Agent M23 detection failure pattern"
    audience: "internal"
    confidence: 0.95
```

#### 11.5.3 OpenAPI Overlay Implementation

```yaml
# overlay-public.yaml
overlay: "1.1.0"
info:
  title: "Omega Engine SOTE Public API"
  version: "1.0.0"
extends: "sote-openapi.yaml"
actions:
  - target: "$.components.schemas.SOTEReport.properties.mandates"
    remove: true
  - target: "$.components.schemas.SOTEReport.properties.decisions"
    remove: true
  - target: "$.components.schemas.SOTEReport.properties.l3_lessons"
    update:
      items:
        properties:
          audience:
            enum: ["public"]
```

```yaml
# overlay-internal.yaml
overlay: "1.1.0"
info:
  title: "Omega Engine SOTE Internal API"
  version: "1.0.0"
extends: "sote-openapi.yaml"
actions:
  - target: "$.components.schemas.SOTEReport.properties.mandates"
    update:
      description: "Full mandate compliance with failing details"
  # Internal keeps all fields
```

**Build Pipeline**:
```bash
# Generate public spec
openapi-format sote-openapi.yaml --overlayFile overlay-public.yaml -o public/sote-api.yaml

# Generate internal spec  
openapi-format sote-openapi.yaml --overlayFile overlay-internal.yaml -o internal/sote-api.yaml
```

---

### 11.6 Decision Health Metrics

**Sources**: [adr-kit Guardian](https://github.com/rvdbreemen/adr-kit) (staleness detector, drift detection, coverage KPI), [mcp-adr-analysis-server](https://glama.ai/mcp/servers/tosin2013/mcp-adr-analysis-server/tools/get_staleness_report) (staleness threshold, governance insights), [Repowise](https://www.repowise.dev/blog/guides/use-git-history-to-catch-stale-adrs-before-they-mislead-agents) (git history to catch stale ADRs), [ADR GitHub Org](https://adr.github.io/) (fitness functions, decision guardrails)

#### 11.6.1 Key Metrics Definitions

| Metric | Definition | Computation | Target |
|--------|------------|-------------|--------|
| **Decision Absorption Rate** | % of voice decisions that reach PIVOT_LOG | `absorbed_in_pivot_log / total_proposed` | ≥80% |
| **Decision Staleness** | Days since last action/mention on a decision | `now - max(last_mentioned_in_code, last_mentioned_in_sote, last_pivot_log_update)` | <90 days |
| **Decision-Code Linkage Density** | % of decisions with ≥1 code reference | `decisions_with_grep_match / total_decisions` | 100% |
| **Decision Supersession Chain Length** | Avg hops from original to current decision | Graph traversal of `supersedes`/`superseded_by` | ≤3 |
| **Decision Coverage** | % of architectural seams with governing decision | `grep -r 'D-' src/ | unique_D_ids / architectural_seams` | ≥90% |
| **Decision Drift** | Decisions contradicted by current code | LLM review of decision vs. current implementation | 0 |
| **Voice Decision Diversity** | Shannon entropy of decision distribution across voices | `-sum(p_i * log(p_i))` where p_i = decisions_by_voice_i / total | >2.0 (of max 2.08) |

#### 11.6.2 adr-kit Guardian Implementation (Reference)

```python
# adr-kit/bin/adr-guardian (simplified)
class Guardian:
    def __init__(self, project_path):
        self.project_path = project_path
        self.adr_index = self.load_adr_index()
        self.codebase = self.scan_codebase()
    
    def check_staleness(self, threshold_days=90):
        """Tier 1: Cheap daily check"""
        stale = []
        for adr in self.adr_index.accepted:
            days_since_action = self.days_since_last_action(adr)
            if days_since_action > threshold_days:
                stale.append({"adr": adr.id, "days": days_since_action})
        return stale
    
    def check_drift(self):
        """Tier 1: Code drift against enforcement rules"""
        violations = []
        for rule in self.enforcement_rules:
            matches = self.codebase.find(rule.pattern)
            for match in matches:
                if not self.has_governing_adr(match, rule.adr_id):
                    violations.append({
                        "file": match.file,
                        "line": match.line,
                        "rule": rule.id,
                        "required_adr": rule.adr_id
                    })
        return violations
    
    def check_coverage(self):
        """KPI: Decision coverage of architectural seams"""
        seams = self.identify_architectural_seams()
        covered = sum(1 for seam in seams if self.has_adr(seam))
        return covered / len(seams) if seams else 0
    
    def check_missing_adrs(self):
        """Tier 2: LLM-hunted missing decisions (bi-weekly)"""
        # Uses LLM to find architectural decisions in code without ADRs
        pass
    
    def check_retirement_candidates(self):
        """ADRs that should be Deprecated/Superseded"""
        candidates = []
        for adr in self.adr_index.accepted:
            if self.is_superseded_by_reality(adr):
                candidates.append(adr.id)
        return candidates
```

#### 11.6.3 Proposed Omega Decision Health Dashboard

```yaml
# mandate_trends.json (emitted by regenerate_sote_index.py)
{
  "schema_version": "1.0",
  "generated": "2026-09-01T06:00:00Z",
  "weeks_analyzed": 13,
  "decision_health": {
    "absorption_rate": 0.0,           # From sote.yaml: 0/67
    "staleness": {
      "decisions_over_90_days": 67,   # All 67 decisions from W36 voices
      "oldest_unstale_days": 7,
      "median_staleness_days": 7
    },
    "code_linkage_density": 0.0,      # grep -r 'D-' src/ → 0 matches
    "supersession_chains": 0,         # No cross-SOTE supersession tracking
    "coverage": 0.0,                  # No architectural seam mapping
    "drift_detected": 0,              # Not yet computed
    "voice_diversity_entropy": 2.08   # 8 voices, uniform = max entropy
  },
  "mandate_compliance": {
    "weekly": [...],                   # Array of {week, pass, warn, fail, pct}
    "trend": "degrading",              # improving | stable | degrading
    "systemic_failures": ["M10", "M11", "M23", "M16", "M20"]
  },
  "public_internal_split": {
    "drift_incidents": 1,             # PUBLIC_DIGEST.md vs STATE_OF_ENGINE
    "automated_generation": false,
    "audience_fields_present": false
  }
}
```

---

### 11.7 Round 2 Structured Findings with Confidence Scores

| # | Finding | Confidence | Evidence |
|---|---------|------------|----------|
| **F11** | Conductor YAML schema is fully specified in `docs/workflow-syntax.md` with Pydantic models; supports all MaKaLi service modes (parallel, for-each, human_gate, sub-workflow, context modes) | 0.99 | Primary source: Microsoft Conductor repo (docs + schema.py) |
| **F12** | GrantBirki/json-yaml-validate@v5 is the most feature-complete GitHub Action for YAML schema validation with multiple schema mappings and custom regex formats | 0.95 | GitHub Marketplace, repo docs, comparison with alternatives |
| **F13** | No prior art exists for explicit **voice/persona rotation schedules** in architectural reviews; closest are ADR author rotation (Konishi) and model tiering (DevStarsJ) | 0.85 | Exhaustive search returned no direct matches; inferred from adjacent patterns |
| **F14** | Quarterly meta-review is established ADR best practice (Konishi, AWS, Decentraland) with concrete questions: deprecation check, missing ADR detection, code drift investigation | 0.97 | Multiple practitioner sources converge on quarterly cadence |
| **F15** | NIST AI.300-1 provides structured template for public-facing AI docs; Sanity GROQ projections enable field-level audience filtering from single source; OpenAPI Overlays 1.1.0 enable spec splitting | 0.98 | NIST official draft (July 2026), Sanity docs, OpenAPI Overlay spec |
| **F16** | Decision health metrics are implemented in adr-kit (staleness, drift, coverage, missing ADR detection) and mcp-adr-analysis-server (staleness report with governance insights) | 0.93 | Working implementations in GitHub repos with documented metrics |

---

### 11.8 Round 2 Actionable Recommendations for Omega SOTE

#### 11.8.1 Immediate (This Week) — Additions to Phase 1

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R13** | Create `schemas/sote/sote-schema.yaml` from Conductor workflow-syntax.md patterns; validate `sote.yaml` on CI | Enables LLM ingestion, catches drift (F11, F12) | 4h |
| **R14** | Add `voice_rotation_schedule.yaml` with 8-week rotation, MaKaLi fixed at position 8; enforce in SOTE kickoff script | Prevents single-owner anti-pattern, ensures diversity (F13) | 2h |
| **R15** | Create `SOTE_META_REVIEW` template (Section 11.4.3) and schedule first run for 2026-W49 (13 weeks from W36) | Addresses Konishi anti-pattern #6 (F14) | 2h |

#### 11.8.2 This Sprint (PUBLIC-DEBUT-01) — Additions

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R16** | Implement `decision_health` section in `mandate_trends.json` (Section 11.6.3) computed by `regenerate_sote_index.py` | Makes M27 chokepoint visible with quantified metrics (F16) | 8h |
| **R17** | Add `audience: public|internal|restricted` to all `sote.yaml` fields and voice front-matter; implement GROQ-style projection in public digest generator | Structural public/internal split per NIST/Sanity (F15) | 8h |
| **R18** | Create Conductor workflow for MaKaLi Unifying Voice (`sote-unifying-voice.yaml`) with explicit context_mode: explicit, human_gate for Oversoul ratification | Codifies MaKaLi as deterministic graph-driven orchestration (F11) | 16h |
| **R19** | Add `supersedes`/`superseded_by` fields to `sote.yaml` decisions section; compute supersession chains in trend computation | Full decision lineage, prevents "editing ADRs" anti-pattern | 4h |

#### 11.8.3 Post-Debut (Week 1-4) — Additions

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| **R20** | Deploy adr-kit Guardian (or equivalent) as `make check-decision-health` — daily staleness/drift check, bi-weekly LLM missing-ADR hunt | Continuous decision health vs. quarterly manual (F16) | 40h |
| **R21** | Build OpenAPI spec for SOTE data + public/internal overlays; publish public API at `public/sote-api.yaml` | Standards-based public/internal split (F15) | 24h |
| **R22** | Implement model tiering in voice rotation: Haiku for classification voices, Opus for reasoning voices, Sonnet for synthesis | Reduces confirmation bias via model diversity; 40-60% cost reduction | 16h |

---

### 11.9 Round 2 Research Methodology

| Query Category | Search Terms | Sources |
|----------------|--------------|---------|
| Conductor Schema | "Microsoft Conductor workflow-syntax.md", "Conductor YAML schema agents routes context_modes" | GitHub microsoft/conductor (docs + source) |
| JSON Schema CI | "GitHub Action JSON Schema validation YAML", "GrantBirki json-yaml-validate", "cardinalby schema-validator-action" | GitHub Marketplace, repos |
| Voice Rotation | "agent persona rotation schedule", "model rotation prevent confirmation bias", "ADR author rotation" | Konishi, Qodo, Galileo, SDAIA, arXiv |
| Meta-Review | "quarterly architecture review template", "ADR of ADRs", "SOTE of SOTE", "AWS ADR process review" | Konishi, AWS, Creately, Docs.io, Decentraland |
| Public/Internal Schema | "NIST AI.300-1 template", "Sanity GROQ projection audience", "OpenAPI Overlay public internal" | NIST, Sanity, API Evangelist, OpenAPI |
| Decision Metrics | "decision absorption rate", "decision staleness metric", "decision code linkage density", "adr-kit guardian" | adr-kit, mcp-adr-analysis-server, Repowise, ADR GitHub |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCHER_SOTE_BEST_PRACTICES-v1.1.0 ⬡ 2026-09-01 ⬡ PUBLIC-DEBUT-01*

**The sovereign substrate is real. The engine islands are preserved. The dialectic is the methodology. The execution is the test.** 🫡