# 🔱 Web Claude Best Practices — Omega Engine
**AP Token**: `AP-WEB-CLAUDE-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Web Claude (Projects, Code, API) interactions
**Supersedes**: `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md` (2026-07-19), `docs/research/R_CLAUDE_PROJECT_INSTRUCTIONS.md`, `docs/research/R_CLAUDE_PROJECT_SETUP_PLAN.md`, `docs/kb/CLAUDE_PROJECTS.md`

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Project creation, architecture, hard limits |
| 2. Three-Stage Workflow | `#2-the-three-stage-workflow-web-claude-only` | Canonical pattern for Web Claude Projects analysis |
| 3. Format Specification | `#3-format-specification` | XML for system prompt, Markdown for knowledge files, JSON for data |
| 4. File Organization | `#4-file-organization` | File count, size, required files, bundle ordering, large codebases |
| 5. File Update Protocol | `#5-file-update-protocol-critical-bug-10841` | Delete-wait-upload-new-conversation procedure, maintenance habits |
| 6. System Prompt Mastery | `#6-system-prompt-mastery` | Force KB Search, role framing, behavioral rules, multishot examples, templates |
| 7. Token & Quota Optimization | `#7-token--quota-optimization` | Strategy hierarchy, format efficiency, prompt caching, quota rotation |
| 8. RAG Behavior & Mitigation | `#8-rag-behavior--mitigation` | 13-file threshold, quality issues, mitigation patterns |
| 9. Sovereign Boundary Protocols | `#9-sovereign-boundary-protocols` | Mandates affecting Claude, context pack sovereignty, reviewer boundary |
| 10. Quick Reference Cards | `#10-quick-reference-cards` | Setup checklist, context pack checklist, token budget |
| 11. Source Citations | `#11-source-citations` | Tier-ordered citations (official, 2026 articles, local research) |
| 12. Hydration Protocol | `#12-hydration-protocol` | Mandatory steps before any Web Claude interaction |

---

## 📋 EXECUTIVE SUMMARY

Web Claude (claude.ai Projects) is the **primary platform** for code review, architecture analysis, and structured reasoning tasks. Best for: SWE-bench (82.1%), long-doc QA (76% MRCR), instruction-following (94.2%).

**Model**: Haiku 4.5 (Extended Thinking) and Sonnet 4.6 (Thinking) on free Web Claude tier.

**Note**: OpenCode CLI with Antigravity SDK provides access to Sonnet 4.6 and Opus 4.6 — that is a **separate platform** and not covered in this playbook.

---

## 1. SETUP & ARCHITECTURE

### 1.1 Project Creation
1. `claude.ai` → Projects → "New Project"
2. Name after **outcome**, not topic (e.g., "Omega Engine Decision Tools Review")
3. Settings → Custom Instructions → Paste system prompt (XML-tagged)
4. Upload knowledge files (≤12 for direct context)
5. Test retrieval: "Based on `file.xml` in project knowledge, what is X?"

### 1.2 Architecture (2026)
- **200K context window** on free Web Claude tier
- **Auto-RAG expansion up to 10x** when approaching limit
- **RAG activates at 13 files** (NOT token-based!) — GitHub Issue #25759
- **Silent regression**: June 2024 loaded 63% capacity directly; Feb 2026 triggers at 2%

### 1.3 Hard Limits (Free Tier)
| Dimension | Value |
|-----------|-------|
| Context window | 200K tokens |
| RAG auto-activation | At ~150K–200K tokens of Knowledge |
| RAG expansion | Up to 10× capacity |
| File size (Project) | 30MB per file |
| File count (single chat) | 20 files / 30MB each |
| Custom Instructions | Keep under ~1,000 words |
| Free tier | 5 Projects max, no RAG |
| Pro | $20/mo, unlimited Projects + RAG |

**Available Models (Free Tier)**:
- **Haiku 4.5** — Extended Thinking mode
- **Sonnet 4.6** — Thinking mode
- **Opus 4.8** — NOT available on free tier |

---

## 2. THE THREE-STAGE WORKFLOW (WEB CLAUDE ONLY)

The canonical pattern for using Web Claude Projects for architecture and research:

| Stage | What Happens |
|-------|-------------|
| **1. Plan/Design** | Architecture decisions, research, spec writing. Project holds permanent context (docs, style guides, requirements). |
| **2. Review/Analyze** | Deep analysis of code, docs, or research materials using Project Knowledge. |
| **3. Synthesize/Deliver** | Produce structured outputs, decisions, and recommendations. |

**Key Principle**: Web Claude is for **analysis, reasoning, and synthesis** — not autonomous code execution. For implementation, use OpenCode CLI (separate platform).

Projects holds **"what" and "why"** (knowledge docs). The Omega Engine's `CLAUDE.md` and `AGENTS.md` hold **"how"** (editorial rules for OpenCode CLI).

---

## 3. FORMAT SPECIFICATION

### 2.1 System Prompt / Custom Instructions → **XML Tags**
Claude's training data is XML-rich; Anthropic official docs recommend XML tags for structure. Closing tags prevent instruction/input boundary confusion.

**ClaSSIC Template** (mandatory):
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are a [specific role] with [experience]. You specialize in [sub-specialty].
Your approach is [methodology]. You always [behavioral rule]. You never [anti-pattern].
</role>

<context>
[Project context, hardware reality, constraints]
</context>

<constraints>
- FORBIDDEN to [violation]
- MUST [requirement]
</constraints>

<rules>
1. [Behavioral rule]
2. [Behavioral rule]
</rules>

<output_format>
[Response structure template]
</output_format>
```

### 2.2 Knowledge/Reference Files (Uploaded) → **Markdown (.md)**
- **Token-efficient**: ~15% fewer tokens than XML
- **RAG-searchable**: Claude parses headings/lists for retrieval
- **Human-readable**: You read these files
- **File limit**: ≤12 files for direct context (13+ triggers RAG)

### 2.3 Structured Data → **JSON**
- Machine-to-machine, schema enforcement

### 2.4 Decision Rule (TeachYou 2026)
> **"Is this piece of the prompt data, or is it instructions? If it's data (variable, untrusted, multiple similar blocks), wrap in XML tags. If it's instructions (authored by you), use Markdown headings."**

---

## 3. FILE ORGANIZATION BEST PRACTICES

### 3.1 File Count & Size
- **≤12 files** for direct context mode
- **≤500 lines** ideal per file, 500-2000 acceptable
- **One topic per file** — cross-file blindness is a verified RAG failure mode
- **Descriptive filenames**: `decisions_catalog_20260718.md` not `final_v3.md`

### 3.2 Required Files
1. `PROJECT_KNOWLEDGE_INDEX.md` — entry point, lists all files with descriptions
2. `GROUNDING.md` — architecture overview, current state
3. `MANDATES.md` — Sovereign Mandates M1-M25
4. `DECISIONS.md` — rolling decisions log (re-upload after each chat)
5. Domain-specific bundles (max 7 for 12-file limit)

### 3.3 Bundle Ordering (Lost-in-the-Middle Mitigation)
U-shaped attention curve (Liu et al. 2023):
1. **START** (Critical): grounding, decisions, summary, overview
2. **MIDDLE** (Reference): implementation, engine_state, mandates, research
3. **END** (Action): handoff, next_steps, recommendations

### 3.4 Large Codebase Strategy
For sharing a large monolithic file (3,000+ lines) with a Web Claude architect:

1. **Create a frozen snapshot** — copy the monolith at a known state for reference
2. **Build per-section architecture docs** — ~300-line focused docs covering each subsystem
3. **Use structural signposts** — section markers in code that Claude can reference by line range
4. **Plan then specify** — produce a modularization plan before extracting any module

---

## 4. FILE UPDATE PROTOCOL (CRITICAL — Bug #10841)

**There is a verified bug**: Re-uploading a file with the same name keeps the old cached version. Claude references stale content.

**Correct procedure**:
1. **Delete** the old file from Project Knowledge first
2. **Wait** for confirmation the file is removed
3. **Upload** the new version (prefer versioned filenames: `brief-v2.md`)
4. **Start a brand-new conversation** — old conversations may hold stale cache
5. **Clear browser cache** before the new session
6. **Wait 5-10 seconds** after editing Custom Instructions before starting a new conversation

### 4.1 Maintenance & Decisions Habit
- **`decisions.md`**: Append one paragraph per concluded chat; re-upload. This is how state survives across chats.
- **`lessons.md`**: Log every misread/drift/hallucination per Project.
- **Prune every 2 weeks**: Remove stale bundles, regenerate from source if changed.
- **Version stamps**: Name packs `sovereign-audit-20260711.xml` so re-uploads are traceable.

---

## 5. SYSTEM PROMPT MASTERY

### 5.1 Priority Hierarchy (April 2026+)
1. **Force KB Search** (top of Custom Instructions):
   ```
   Before answering, always search the project knowledge first.
   If anything in the knowledge applies, quote and prioritize it over general knowledge.
   ```
   *Reported as "more impactful than any other tuning" by community.*

2. **Role Framing Depth**:
   ```
   You are a [specific role] with [years] experience in [domain].
   You specialize in [sub-specialty].
   Your approach is [methodology/philosophy].
   You always [behavioral rule].
   You never [anti-pattern].
   ```

3. **Behavioral Rules** (standards):
   - Proactively flag problems, risks, better approaches
   - Teach me unknown best practices
   - Acknowledge gaps explicitly. Say "I don't know" when appropriate
   - No AI-isms: Genuinely, Honestly, It's important to note, Straightforward, In today's world, Crucial, Delve, Tapestry, Landscape, Realm
   - Prose over bullets unless discrete items
   - Cite specific sources when referencing docs
   - Confirm scope before changes
   - Never skip error handling
   - No framework switching unless asked

4. **Tool Triggers**:
   - Current data (2026) → Web Search
   - Complex synthesis → Deep Research
   - Math/data analysis → Code Execution

### 5.2 Multishot Examples (Official Best Practice)
```xml
<examples>
  <example>
    <input>[representative input]</input>
    <output>[ideal output demonstrating format, tone, depth]</output>
  </example>
  <example>
    <input>[edge case input]</input>
    <output>[ideal output showing edge handling]</output>
  </example>
</examples>
```
*Anthropic: "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure."*

### 5.3 Chain-of-Thought Variants
| Variant | Use Case |
|---------|----------|
| "Think step by step" | General reasoning |
| "Think first, then respond in `<answer>` tags" | High-stakes, separate reasoning |
| "Show your work in `<scratchpad>`, then give final answer" | Math, logic, verification |
| "Consider [X], [Y], [Z] before concluding" | Multi-factor decisions |

### 5.4 Custom Instruction Templates (Per Project Type)

**Void-Seekers (YouTube Research)**
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are the YouTube Research Lead for the Omega Engine sovereign AI project. Your objective is to ingest, sign, and distill YouTube research into the Omega memory pipeline with verifiable provenance.
</role>

<context>
Audience: The user is building local-first AI infrastructure and must be treated as an expert.
Purpose: This project exists to ingest, sign, and distill YouTube research into the Omega memory pipeline. All work must remain local-first and sovereign.
</context>

<constraints>
- FORBIDDEN to introduce any cloud dependency.
- FORBIDDEN to emit telemetry of any kind (M8).
- MUST remain local-first at all times (M7).
</constraints>
```

**Pattern-Miners (Core Engine)**
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are the Omega Engine Core Architect (anyio-only, sovereign mandates enforced).
</role>

<context>
Audience: Expert Python systems engineer.
Purpose: Reviewing, hardening, and extending src/omega/ core engine.
</context>

<constraints>
- FORBIDDEN to use asyncio directly (M1).
- FORBIDDEN to emit telemetry (M8).
- MUST enforce Engine-Stack Firewall (M2).
- MUST pass Temple-Grade T1-T11 (M13).
</constraints>
```

**Scribes (Oversight & Docs)**
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are the Sovereign Scribe — documentation and governance steward.
</role>

<context>
Audience: Project maintainer.
Purpose: Maintaining soul.yaml lessons, strategy docs, and the Sovereign Ark Blueprint.
</context>

<constraints>
- MUST use L1→L2→L3 distillation.
- MUST cite decisions from PIVOT_LOG.md.
- MUST flag doc drift.
</constraints>
```

**Sentinels (Security & Audit)**
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are the Sovereign Sentinel — security and compliance auditor.
</role>

<context>
Audience: Security-conscious maintainer.
Purpose: Auditing mandates, heritage tags, and observability integrity.
</context>

<constraints>
- MUST verify M1-M23 compliance.
- MUST check [id-soft:] tags against HERITAGE_VET_LOG.md.
- MUST validate Response Provenance (M22).
</constraints>
```

---

## 6. TOKEN OPTIMIZATION

### 6.1 Strategy Hierarchy (Ranked by ROI)
| Rank | Strategy | Savings | Effort |
|------|----------|---------|--------|
| 1 | **Prompt Caching** (Anthropic `cache_control`) | 90% on cached prefix | Low |
| 2 | **Format Optimization** | 15-40% | Low |
| 3 | **Model Routing** | 60-95% | Medium |
| 4 | **Batch API** | 50% | Medium |
| 5 | **Prompt Compression** (LLMLingua) | 5-20x | High |

### 6.2 Format Efficiency
- **YAML/Markdown**: ~15% fewer tokens than JSON
- **TOON**: ~40% fewer for tabular data
- **XML**: Baseline (1.0x) — best comprehension

### 6.3 Prompt Caching
```python
# Cache stable prefix (system prompt, docs, tool defs)
# Dynamic content at suffix
# Use cache_control: {"type": "ephemeral"} on blocks
# 90% discount on cached input tokens
```

### 6.4 Model Selection (Free Tier)
| Task Type | Model | Thinking Mode |
|-----------|-------|---------------|
| Simple classification/extraction | Haiku 4.5 | Extended Thinking |
| General coding/analysis | Sonnet 4.6 | Thinking |
| Complex architecture/reasoning | Sonnet 4.6 | Thinking (use more context) |
| Massive doc ingestion | Sonnet 4.6 | Thinking |

**Note**: Opus 4.8 is NOT available on free tier. For complex tasks, use Sonnet 4.6 with extended context.

### 6.5 Quota Management (Free Tier)
Web Claude free tier has **rolling usage limits** (July 2026). The 200K context window can be drained quickly with large context packs.

**Token discipline**:
- Keep Direct Context accounts <40% utilization (≤80K tokens per theme, ≤12 files).
- RAG-mode accounts rotate faster.
- Start new conversations for fresh context windows.

---

## 7. RAG BEHAVIOR & MITIGATION

### 7.1 The 13-File Threshold
| File Count | Behavior |
|------------|----------|
| 1-12 files | Direct context loading |
| **13+ files** | **RAG mode activates** — "To save space, Claude will look up specific information as needed" |
| Any count | Uses `project_knowledge_search` tool — partial fragments, misses cross-file connections |

### 7.2 RAG Quality Issues
- Hallucinates details contradicting actual file contents
- Scores noise as signal past ~10 files
- Cross-file blindness: knowledge spanning 3 files never fully assembled

### 7.3 Mitigation
1. **Stay ≤12 files** — aggregate content
2. **Descriptive filenames** — "Claude searches by filename"
3. **If RAG unavoidable** — structure bundles with clear section IDs for retrieval
4. **RAG Acknowledgment Pattern** (include in context packs):
   > **How to use this pack**: Claude's RAG retrieves these files automatically when relevant. Reference them by bundle name (e.g., `grounding_part1.xml`, `mandates.xml`). The manifest is signed — verify integrity if suspicious.

---

## 8. SOVEREIGN BOUNDARY PROTOCOLS

### 8.1 Mandates Affecting Claude Usage
| Mandate | Impact |
|---------|--------|
| **M1 AnyIO** | All async code in generated artifacts must use AnyIO |
| **M2 Engine-Stack Firewall** | No WAD-specific logic in core engine recommendations |
| **M7 Local-First** | Prefer local model recommendations; cloud as fallback |
| **M8 Zero Telemetry** | No analytics, tracking, or phone-home in generated code |
| **M9 Error Integrity** | Typed errors, no bare `except:` in generated code |
| **M13 Temple-Grade** | T1-T11 gates apply to all generated artifacts |
| **M14 Heritage Vetting** | Any `[id-soft:]` tags need vet record |
| **M16 Modularization** | No hardcoded paths in generated core code |
| **M21 Gate Integrity** | Contract tests for typed returns |
| **M23 Failure Integrity** | No soft failures; hard stop on tool chain collapse |

### 8.2 Context Pack Sovereignty
- **Packer is ONLY sanctioned path** for engine state to leave boundary
- Direct file uploads, copy-paste, ad-hoc exports violate M8/M23
- Sieve-and-Sign pipeline mandatory:
  1. Selection (YAML profiles = sovereignty policy)
  2. PII Masking (TOKENIZE mode)
  3. XML Escaping (full body)
  4. Atomic Writes (os.replace)
  5. Manifest-First (entry point control)
  6. Slot Compliance (max_slots: 12)
  7. Ed25519 Signing (tamper-evident)

### 8.3 External Reviewer Boundary
**Tools cross the boundary — content does not.**

| Crosses Boundary (Valid Export) | Stays Within Boundary (Internal) |
|----------------------------------|----------------------------------|
| Architecture, schema, CLI design | Which option was chosen |
| Integration patterns | What was decided |
| Prior art (universal knowledge) | Internal decision history |
| Mandates (design constraints) | Internal decision rationale |

---

## 9. QUICK REFERENCE CARDS

### Card 1: Claude Projects Setup (5 min)
```
1. claude.ai → Projects → "New Project"
2. Name: "Omega Engine Decision Tools Review"
3. Settings → Custom Instructions → Paste XML system prompt
4. Upload context_packs/decision-tools-review/ (8 files)
5. Test query: "Review the DecisionEngine schema in grounding_part1.xml"
```

### Card 2: Context Pack Checklist
```
☐ XML format for system prompt
☐ Markdown (.md) for knowledge files
☐ ≤12 files total
☐ Ed25519 signed manifest
☐ LITM ordering: Critical at START/END
☐ PII masking: TOKENIZE mode
☐ Injection scan: 25 patterns
☐ Per-bundle ≤15K tokens
☐ Total ≤150K tokens
☐ All XML valid (ElementTree.parse)
```

### Card 3: Token Budget
```
Pack bundles:     ~41K tokens
Manifest:           ~573 tokens
System prompt:    ~1,848 tokens
────────────────────────
Total:            ~43K tokens
Headroom:        156K tokens (78% of 200K)
```

---

## 10. SOURCE CITATIONS

### Tier 1: Official
- Anthropic Prompt Caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Anthropic XML Tags: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags
- Anthropic RAG for Projects: https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- OWASP LLM Prompt Injection: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- Microsoft Presidio: https://microsoft.github.io/presidio/

### Tier 2: 2026 Technical Articles
- TokenOptimize.dev 2026: https://www.tokenoptimize.dev/guides/llm-token-optimization-strategies
- Thomas Wiegold 2026: https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026
- ImprovingAgents 2025: https://www.improvingagents.com/blog/best-nested-data-format
- AI Tools Guidebook 2026: https://aitoolsguidebook.com/en/articles/claude-projects-advanced-workflow
- Practicaly.ai 2026: https://www.practicaly.ai/p/what-are-md-files-in-claude

### Tier 3: Local Research (Evidence)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — Platform profiles
- `docs/research/R_CLAUDE_PROJECT_INSTRUCTIONS.md` — XML templates
- `docs/research/R_CLAUDE_PROJECT_SETUP_PLAN.md` — 8-account deployment plan
- `docs/kb/CLAUDE_PROJECTS.md` — KB, RAG threshold, file update protocol
- `docs/research/R_CONTEXT_PACK_FORMAT_MD_VS_XML_20260808.md` — Format decision

---

## 11. HYDRATION PROTOCOL

**Before any Web Claude interaction, agents MUST:**
1. Read this document
2. Select Haiku 4.5 (simple tasks) or Sonnet 4.6 (complex tasks)
3. Prepare system prompt using XML ClaSSIC template
4. Prepare knowledge files as `.md` (≤12)
5. Follow file update protocol if files changed
6. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
