# 🔱 Web Grok Best Practices — Omega Engine
**AP Token**: `AP-WEB-GROK-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Web Grok (SuperGrok, Grok Build, API) interactions
**Supersedes**: `docs/research/R_GROK_CLI_ARCHITECTURE.md`, `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md`, `docs/research/R_GROK_ECOSYSTEM_DEEP.md`, `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md`

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Project creation, architecture, model capabilities |
| 2. Format Specification | `#2-format-specification` | XML + Markdown hybrid for system prompt and knowledge files |
| 3. Key Capabilities | `#3-key-capabilities` | Real-time X search, Grok Skills, Connectors, Grok Build |
| 4. File Organization | `#4-file-organization` | File count limits, structure, connector metadata |
| 5. System Prompt Template | `#5-system-prompt-template` | XML + Markdown hybrid with Grok-specific directives |
| 6. Grok Skills | `#6-grok-skills` | Skill template, invocation, output format |
| 7. Cost Optimization | `#7-cost-optimization` | Model selection, pricing, economy tier strategies |
| 8. Connector Awareness | `#8-connector-awareness` | GitHub, Notion, Linear, Google Workspace, Microsoft 365 |
| 9. Sovereign Boundary Protocols | `#9-sovereign-boundary-protocols` | M7 local-first, M23 failure integrity, PII protection |
| 10. Quick Reference | `#10-quick-reference` | Model comparison, format quick reference, setup checklist |
| 11. Source Citations | `#11-source-citations` | Tier-ordered citations |
| 12. Hydration Protocol | `#12-hydration-protocol` | Mandatory steps before any Web Grok interaction |

---

## 📋 EXECUTIVE SUMMARY

Web Grok (xAI) is the **primary platform** for real-time intelligence, agentic workflows, and live data research. Best for: current best practices (post-2024), emerging vulnerabilities, active discussions on context engineering.

**Models**:
- Grok 4.3 (1M context, $1.25/$2.50/MTok) — general reasoning, agentic workflows
- Grok 4.20 Multi-Agent (2M context, $2.00/$4.00/MTok) — document analysis, complex orchestration
- Grok 4.1 Fast (2M context, $0.20/$0.50/MTok) — high-volume, latency-sensitive, cost-optimized
- Grok Build (256K context, $1.00/$2.00/MTok) — coding agent (70.8% SWE-Bench)

---

## 1. SETUP & ARCHITECTURE

### 1.1 Project Creation
1. `grok.x.ai` → SuperGrok → "New Project"
2. Name after **outcome** (e.g., "Omega Engine Real-Time Security Review")
3. Add Custom Instructions (XML + Markdown hybrid)
4. Upload files to project knowledge
5. Configure Grok Skills for reusable instruction bundles
6. Test retrieval: "Based on `file.xml` in project knowledge, what is X?"

### 1.2 Architecture (2026)
- **1-2M context window** (model-dependent)
- **Real-time X Search**: Integrated live search via X platform
- **Grok Skills**: Persistent instruction bundles (`/skillname` slash commands)
- **Connectors**: GitHub, Notion, Linear, Google Workspace, Microsoft 365, Vercel, Canva, S&P Global
- **Grok Build**: Terminal coding agent, 8 parallel sub-agents, MCP support

### 1.3 Model Capabilities
| Model | Context | SWE-bench | GPQA | Best For |
|-------|---------|-----------|------|----------|
| Grok 4.3 | 1M | 70.8% | 87.5% | General reasoning, agentic |
| Grok 4.20 Multi-Agent | 2M | 72.5% | 89.0% | Document analysis, orchestration |
| Grok 4.1 Fast | 2M | 65.0% | 82.0% | High-volume, cost-optimized |
| Grok Build | 256K | 70.8% | — | Coding agent |

---

## 2. FORMAT SPECIFICATION

### 2.1 System Prompt / Custom Instructions → **XML + Markdown Hybrid**
Grok follows XML tags but benefits from Markdown readability for human review.

### 2.2 Knowledge/Reference Files (Uploaded) → **XML + Markdown Hybrid**
- **XML** for structured data bundles (code, configs, schemas)
- **Markdown** for human-readable content (research, decisions, mandates)
- **Larger file count tolerance**: ~20 files before degradation (vs 13 for Claude)

### 2.3 Structured Data → **JSON**
- Machine-to-machine, schema enforcement

### 2.4 Grok Skills → **YAML**
- Skill definition format for `/skillname` invocation

---

## 3. KEY CAPABILITIES

### 3.1 Real-Time X Search
- Integrated live search via X platform
- Use for: current best practices (post-2024), emerging vulnerabilities, active discussions
- Include X search results as dynamic bundles

### 3.2 Grok Skills
- Persistent instruction bundles invoked via `/skillname` slash commands
- Deterministic output format (tables, severity ratings)
- Tool usage specifications

### 3.3 Connectors
- **GitHub**: CI/CD integration patterns, repo structure
- **Notion**: Knowledge base structure, wiki organization
- **Linear**: Issue tracking integration, sprint planning
- **Google Workspace**: Docs, Sheets, Drive access
- **Microsoft 365**: Teams, Outlook, SharePoint
- **Vercel**: Deployment previews, edge functions
- **Canva**: Design assets, brand guidelines
- **S&P Global**: Financial data, market intelligence

### 3.4 Grok Build
- Terminal coding agent
- 8 parallel sub-agents
- MCP support
- Landlock/Seatbelt sandbox profiles

---

## 4. FILE ORGANIZATION

### 4.1 File Count & Structure
- **~20 files** before degradation (vs 13 for Claude)
- **Connector metadata**: Tag bundles with connector metadata (GitHub, Notion, etc.)
- **Real-time data injection**: Include X search results as dynamic bundles
- **Skill-compatible output**: Generate `.skill` packs for Grok Skills system

### 4.2 Required Files
1. `PROJECT_KNOWLEDGE_INDEX.md` — entry point with descriptions
2. `GROUNDING.md` — architecture overview, current state
3. `MANDATES.md` — Sovereign Mandates M1-M25
4. Domain-specific bundles (thematic organization)

### 4.3 Bundle Ordering
- **Priority-weighted** for agentic workflows
- **Real-time first** for live data tasks
- **Connector-aware** grouping

---

## 5. SYSTEM PROMPT TEMPLATE (XML + Markdown Hybrid)

```markdown
## PLATFORM: Web Grok (Grok 4.3 / 4.1 Fast)

### Grok-Specific Directives

#### Real-Time Intelligence
You have access to live X search. Use it for:
- Current best practices (post-2024)
- Emerging vulnerabilities
- Active discussions on context engineering

#### Grok Skills Compatibility
Your review output should be structured for potential Skill conversion:
- Clear name/description for `/skillname` invocation
- Deterministic output format (tables, severity ratings)
- Tool usage specifications

#### Connector Awareness
Bundles may include connector metadata (GitHub, Notion, Linear, etc.). Factor this into your review:
- GitHub bundles: Check for CI/CD integration patterns
- Notion bundles: Verify knowledge base structure
- Linear bundles: Assess issue tracking integration

#### Cost Consciousness
If reviewing for Grok 4.1 Fast (economy tier), prioritize:
- Token efficiency recommendations
- Bundle consolidation opportunities
- Caching strategies

### Grok Multishot Example

<examples>
  <example>
    <section>Security Review</section>
    <input>Review the PII masking implementation in enhanced_packer.py</input>
    <output>
## Security Review: PII Masking

| Check | Verdict | Evidence |
|-------|---------|----------|
| Reversible tokenization | ✅ PASS | Uses Presidio ReversibleAnonymizer with vault |
| Format preservation | ⚠️ PARTIAL | Email tokens preserve @ but not domain structure |
| Vault encryption | ❌ FAIL | In-memory only, no persistence |
| Streaming rehydration | ❌ FAIL | No SSE chunk handling |

**Severity**: HIGH (vault encryption missing)
**Recommendation**: Integrate CloakPipe or OPF for production vault
    </output>
  </example>
</examples>
```

---

## 6. GROK SKILLS

### 6.1 Skill Template (YAML)
```yaml
name: "your-skill-name"
description: "Brief description of what this skill does"
instructions: |
  You are a [role]. When invoked:
  - [specific task 1]
  - [specific task 2]
  - Output: structured findings table + severity ratings
```

### 6.2 Skill Design Principles
- **Deterministic output**: Tables, severity ratings, structured findings
- **Clear invocation**: `/skillname` should be intuitive
- **Tool specifications**: Define which tools the skill uses
- **Cost awareness**: For economy tier, prioritize token efficiency

---

## 7. COST OPTIMIZATION

### 7.1 Model Selection
| Task Type | Model | Cost (input/output) | Context |
|-----------|-------|---------------------|---------|
| General reasoning, agentic | Grok 4.3 | $1.25/$2.50/MTok | 1M |
| Document analysis, orchestration | Grok 4.20 Multi-Agent | $2.00/$4.00/MTok | 2M |
| High-volume, cost-sensitive | Grok 4.1 Fast | $0.20/$0.50/MTok | 2M |
| Coding agent | Grok Build | $1.00/$2.00/MTok | 256K |

### 7.2 Economy Tier Strategies (Grok 4.1 Fast)
- **Token efficiency**: Prioritize recommendations that reduce token usage
- **Bundle consolidation**: Merge related content into fewer files
- **Caching strategies**: Cache stable prefixes, dynamic content at suffix
- **Cost consciousness**: Flag expensive operations, suggest alternatives

---

## 8. CONNECTOR AWARENESS

### 8.1 Connector Metadata Tagging
Tag bundles with connector metadata:
```markdown
<!-- Connector: GitHub -->
<!-- Repo: Xoe-NovAi/omega-engine -->
<!-- Branch: main -->
```

### 8.2 Connector-Specific Review Focus
| Connector | Review Focus |
|-----------|--------------|
| GitHub | CI/CD integration, repo structure, branch strategy |
| Notion | Knowledge base structure, wiki organization, linking |
| Linear | Issue tracking, sprint planning, milestone mapping |
| Google Workspace | Docs/Sheets access, Drive organization |
| Microsoft 365 | Teams integration, SharePoint structure |
| Vercel | Deployment previews, edge function config |
| Canva | Design assets, brand guidelines, template structure |
| S&P Global | Financial data schemas, market data formats |

---

## 9. SOVEREIGN BOUNDARY PROTOCOLS

### 9.1 Mandates Affecting Grok Usage
| Mandate | Impact |
|---------|--------|
| **M1 AnyIO** | All async code in generated artifacts must use AnyIO |
| **M7 Local-First** | Prefer local model recommendations; cloud as fallback |
| **M8 Zero Telemetry** | No analytics, tracking, or phone-home in generated code |
| **M13 Temple-Grade** | T1-T11 gates apply to all generated artifacts |
| **M23 Failure Integrity** | No soft failures; hard stop on tool chain collapse |

### 9.2 PII Protection
- All context packs must use TOKENIZE mode for PII (Presidio/OPF/Privalyse)
- Injection pattern scanning: 25 OWASP/Microsoft/Google patterns

---

## 10. QUICK REFERENCE

### Model Comparison
| Model | Context | Input/Output | Best For |
|-------|---------|--------------|----------|
| Grok 4.3 | 1M | $1.25/$2.50/MTok | General reasoning, agentic |
| Grok 4.20 Multi-Agent | 2M | $2.00/$4.00/MTok | Document analysis, orchestration |
| Grok 4.1 Fast | 2M | $0.20/$0.50/MTok | High-volume, cost-optimized |
| Grok Build | 256K | $1.00/$2.00/MTok | Coding agent |

### Format Quick Reference
| Layer | Format |
|-------|--------|
| System prompt | XML + Markdown hybrid |
| Knowledge files | XML + Markdown hybrid |
| Structured data | JSON |
| Grok Skills | YAML |

### Setup Checklist
```
☐ Project created with outcome-based name
☐ Custom Instructions in XML + Markdown hybrid
☐ Grok Skills configured for reusable workflows
☐ Connectors configured (GitHub, Notion, Linear, etc.)
☐ Real-time X search enabled
☐ Knowledge files uploaded (XML + MD hybrid)
☐ Connector metadata tagged
☐ Cost tier selected (standard/economy)
```

---

## 11. SOURCE CITATIONS

### Tier 1: Official
- xAI Grok Skills: https://grok.x.ai/skills
- xAI Grok Build: https://grok.x.ai/build
- xAI Connectors: https://grok.x.ai/connectors

### Tier 2: 2026 Technical Articles
- zenn.dev Format Comparison: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- AI Tools Recap Grok Skills: https://aitoolsrecap.com/grok-skills (2026)

### Tier 3: Local Research (Evidence)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — Platform profiles, system prompts, multishot examples
- `docs/research/R_GROK_CLI_ARCHITECTURE.md` — CLI architecture, components
- `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` — Comprehensive research
- `docs/research/R_GROK_ECOSYSTEM_DEEP.md` — Ecosystem deep dive

---

## 12. HYDRATION PROTOCOL

**Before any Web Grok interaction, agents MUST:**
1. Read this document
2. Select appropriate model (4.3/4.20/4.1 Fast/Build)
3. Prepare system prompt in XML + Markdown hybrid format
4. Prepare knowledge files as XML + Markdown hybrid
5. Configure Grok Skills and Connectors as needed
6. Enable real-time X search for current data
7. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
