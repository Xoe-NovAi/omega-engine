# 🔱 Omega Engine — Claude Best Practices & Advanced Usage Guide
**AP Token**: `AP-CLAUDE-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH-COMPLETE ⬡ 2026-07-19

**Purpose**: Single-source reference for all Claude (Web, Code, Projects, API) best practices discovered through 2026 deep research. Agents MUST consult this before any Claude interaction to avoid redundant research.

---

## 📋 TABLE OF CONTENTS

1. [Context Engineering Philosophy](#1-context-engineering-philosophy)
2. [Claude Projects Optimization](#2-claude-projects-optimization)
3. [System Prompt / Custom Instructions Mastery](#3-system-prompt--custom-instructions-mastery)
4. [Context Pack Design for External Review](#4-context-pack-design-for-external-review)
5. [Token Optimization Strategies](#5-token-optimization-strategies)
6. [RAG Behavior & File Limits](#6-rag-behavior--file-limits)
7. [Prompt Engineering Patterns](#7-prompt-engineering-patterns)
8. [Model Selection & Routing](#8-model-selection--routing)
9. [Advanced Techniques](#9-advanced-techniques)
10. [Sovereign Boundary Protocols](#10-sovereign-boundary-protocols)
11. [Quick Reference Cards](#11-quick-reference-cards)

---

## 1. CONTEXT ENGINEERING PHILOSOPHY

### Core Principle (TokenOptimize.dev 2026)
> **"Token optimization is a context-engineering problem, not a prompt-shortening problem."**

### Strategy Hierarchy (Ranked by ROI)

| Rank | Strategy | Savings | Effort | When to Use |
|------|----------|---------|--------|-------------|
| 1 | **Prompt Caching** (Anthropic `cache_control`) | 90% on cached prefix | Low | Stable content first (system prompt, docs, tool defs); dynamic at end |
| 2 | **Format Optimization** | 15-40% | Low | YAML/Markdown > JSON; TOON for tabular |
| 3 | **Model Routing** | 60-95% | Medium | Haiku→Sonnet→Opus tiered by complexity |
| 4 | **Batch API** | 50% | Medium | Queue non-urgent work |
| 5 | **Prompt Compression** (LLMLingua) | 5-20x | High | Retrieval-heavy workloads |

### 2026 Model Pricing Context (Critical for Pack Sizing)

| Model | Context | Input/Output | Cached Input | Notes |
|-------|---------|--------------|--------------|-------|
| **Claude Opus 4.8** | 1M | $5/$25/MTok | $0.50/MTok | New tokenizer: +35% tokens for code |
| **Claude Sonnet 4.6** | 1M | $3/$15/MTok | $0.30/MTok | Best quality/cost for most tasks |
| **Claude Haiku 4.5** | 200K | $0.25/$1.25/MTok | $0.025/MTok | 12x cheaper than Sonnet |
| **GPT-5.5** | 90% cached discount | $5/$30/MTok | $0.50/MTok | No discount on Pro tier |
| **Llama 4 Scout** | 10M | Self-hosted | N/A | Open weights, local only |

**Pack Sizing Rule**: Target 87K tokens (current pack) well within Sonnet 4.6 1M window. Cache manifest + static docs as prefix; dynamic content at suffix.

---

## 2. CLAUDE PROJECTS OPTIMIZATION

### Architecture (2026)
- **200K context window** primary workspace
- **Auto-RAG expansion up to 10x** when approaching limit
- **RAG activates at ~13 files** (NOT token-based!) — GitHub Issue #25759
- **Silent regression**: June 2024 loaded 63% capacity directly; Feb 2026 triggers at 2%

### File Organization Best Practices

| Practice | Rationale |
|----------|-----------|
| **Keep ≤12 files per project** | Stay under RAG threshold for direct context loading |
| **Aggregate related content** | Fewer, larger files > many small files |
| **Descriptive filenames** | "Claude searches by filename" — use `decisions_catalog_20260718.md` not `final_v3.md` |
| **Delete stale content** | "Reorganize, don't just add" |
| **Upload comprehensive content upfront** | RAG retrieves only what's needed |

### Project Setup Checklist
1. **Specific, descriptive name** — "Q1 2026 Marketing Campaign" not "Work Stuff"
2. **Custom Instructions** — Role, context, output preferences, behavioral rules
3. **Knowledge base** — All relevant docs uploaded at creation
4. **Test with a sample query** — Verify retrieval quality before real work

---

## 3. SYSTEM PROMPT / CUSTOM INSTRUCTIONS MASTERY

### Where They Live
| Surface | Location | Limit |
|---------|----------|-------|
| **Claude.ai Profile** | Settings → Custom Instructions | 1,500 chars (global) |
| **Claude Projects** | Project → Settings → Instructions | ~8,000 chars + 200K tokens docs |
| **Claude Code** | `CLAUDE.md` at repo root | No hard limit; best at 1,000-2,500 words |
| **API** | `system` parameter in `messages.create()` | Full context window |

### Priority Hierarchy (April 2026+)
1. **Organization Instructions** (Team/Enterprise) — 3,000 chars, admin-defined
2. **Project Instructions** — Project-specific, overrides org
3. **Profile Preferences** — User-level, applies globally
4. **Conversation Context** — Current chat only

### Writing Effective Instructions (2026 Best Practices)

#### Frame as Context/Preference, Not Commands
> "Claude has strong values and will push back on instructions it finds problematic even in a system prompt. Frame instructions as context and preference rather than commands — you will get far better results working with Claude's nature rather than against it."

#### Prose Over Bullets
> "Prefer readable, flowing text that guides naturally through ideas rather than fragmenting into isolated points. Use bullets only for truly discrete items or when explicitly requested."

#### Use Multishot Examples in XML Tags (Official Best Practice)
> **Anthropic's official recommendation**: "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure. Include 3–5 examples wrapped in `<example>` tags (multiple in `<examples>` tags) so Claude can distinguish them from instructions."
>
> **Correction**: The "writing sample calibration" technique (200-400 words of your writing) is a community practice. The **verified official pattern** is explicit multishot examples in XML tags. Writing samples work implicitly; examples work explicitly and are the recommended approach.

**Official Template**:
```xml
<examples>
  <example>
    <input>User: How do I sort a list of dicts by key?</input>
    <output>
      Use `sorted(list_of_dicts, key=lambda x: x['key'])`.
      For descending: `sorted(list_of_dicts, key=lambda x: x['key'], reverse=True)`.
    </output>
  </example>
  <example>
    <input>User: What's the difference between list.sort() and sorted()?</input>
    <output>
      `list.sort()` mutates in-place and returns None. `sorted()` returns a new list.
    </output>
  </example>
</examples>
```

#### Proactive Flagging Directive
> "If you see problems, risks, or better approaches, flag them proactively. Don't wait for me to ask."

#### Teach Unknowns Directive
> "Teach me best practices and useful features of the tools I'm using that I might not know about."

#### Honest Uncertainty Permission
> "Acknowledge gaps explicitly. Say 'I don't know' when appropriate. Don't hallucinate."

#### No AI-isms List
> Avoid: "Genuinely," "Honestly," "It's important to note," "Straightforward," "In today's world," "Crucial," "Delve," "Tapestry," "Landscape," "Realm."

#### Tool Activation Triggers
> "If a query requires current data (2025-2026), immediately trigger Web Search. If complex synthesis, trigger Deep Research. If math/data analysis, trigger Code Execution."

#### No Framework Switching
> "Don't suggest switching frameworks unless asked."

#### No Skipped Error Handling
> "Never skip error handling or validation in recommendations."

#### Confirm Scope
> "Confirm scope before executing changes."

#### Standing Rules vs Behavioral Directives Separation
> **Structural pattern**: Separate immutable process rules (Standing Rules) from behavioral guidance (Directives). This mirrors XML section separation and improves adherence.
>
> **Standing Rules** (process, non-negotiable):
> - Confirm scope before changes
> - Never skip error handling
> - No framework switching unless asked
> - Cite specific sources when referencing docs
>
> **Behavioral Directives** (tone, approach):
> - Proactively flag problems
> - Teach unknowns
> - Honest uncertainty
> - Prose over bullets
> - No AI-isms

---

## 4. CONTEXT PACK DESIGN FOR EXTERNAL REVIEW

### Format Selection (2026 Research)

| Format | Token Efficiency | Claude Comprehension | Best For |
|--------|------------------|---------------------|----------|
| **XML** | Baseline (1.0x) | ⭐⭐⭐⭐⭐ Native | **Claude Projects** — Anthropic explicitly recommends for data/content boundaries |
| **YAML** | ~0.85x (15% fewer) | ⭐⭐⭐⭐ Good | Token-constrained contexts |
| **Markdown** | ~0.85x (15% fewer) | ⭐⭐⭐⭐ Good | Human-readable + LLM-readable; **best for instructions** |
| **TOON** | ~0.60x (40% fewer) | ⭐⭐⭐ Emerging | High-volume tabular data |
| **JSON** | 1.0x (baseline) | ⭐⭐⭐ Good | Structured output, tool calls |

**Critical Findings**:
- "Claude 4.x follows XML tags literally — XML tags are genuinely the best structuring method for Claude" (Thomas Wiegold 2026, Anthropic docs)
- "Forcing LLM to output JSON degrades reasoning by 10-15%" (Michael Hannecke 2025)
- "YAML emerged as strongest format for 2/3 models tested" (ImprovingAgents 2025)
- **Hybrid approach recommended** (Anthropic + TeachYou 2026): **Markdown `##` for instructions, XML tags for data/content boundaries**. This leverages Markdown's strong instruction-following signal and XML's unambiguous data delimiting.
- Two-step approach: Free reasoning → structured formatting (preserves accuracy)

**Decision Rule** (TeachYou 2026): "Is this piece of the prompt data, or is it instructions? If it's data (variable, untrusted, multiple similar blocks), wrap in XML tags. If it's instructions (authored by you), use Markdown headings."

### Sovereign Export Pipeline: Sieve-and-Sign Pattern
```
Raw Engine State → Context Cleansing (Sieve) → Low-Entropy XML → Cryptographic Sign (Ed25519)
  → Forensic Receipt (Manifest) → Export Bundle
```

**Sieve Stage** (Context Cleansing):
1. **PII Masking** — Mandatory TOKENIZE mode via Presidio/OPF/Privalyse
2. **XML Body Escaping** — Escape ALL `<`, `>`, `&` in content (not just attributes)
3. **Injection Pattern Scanning** — 25 OWASP/Microsoft/Google patterns
4. **Token Limit Enforcement** — Per-bundle + total limits prevent stuffing

**Sign Stage**:
- Ed25519 manifest signature with embedded public key
- Tamper-evident forensic receipt
- Verifiable by reviewer: `openssl dgst -sha256 -verify pubkey.pem -signature sig.bin manifest.md`

### Bundle Structure for Lost-in-the-Middle Mitigation

**U-Shaped Attention Curve** (Liu et al. 2023, replicated 2025-2026):
- 80-100% accuracy at positions 1-10% and 90-100%
- 20-50% at 40-60%

**Ordering Strategy**:
```
START (Critical):     grounding, decisions, decree, verdict, summary, overview
MIDDLE (Reference):   implementation, engine_state, mandates, session_log, research, pivot_log, evidence
END (Action):         handoff, exit_protocol, next_steps, action_items, recommendations
```

**Implementation**: `_reorder_bundles_for_litm()` classifies bundles into CRITICAL_START, CRITICAL_END, MIDDLE sets, then concatenates: START (sorted by token count desc) + MIDDLE (sorted by token count desc) + END (sorted by token count desc).

### RAG Threshold Compliance
- **Hard limit**: 12 files max (13 triggers RAG)
- **Current pack**: 8 files (7 bundles + manifest) — well under
- **Bundle consolidation**: `_consolidate_bundles()` enforces `max_slots-1` bundles, merges lowest-priority into `general`

### Per-Bundle Token Limits
- `MAX_BUNDLE_TOKENS = 15,000` — keeps each bundle in high-attention zone
- `MAX_TOTAL_TOKENS = 150,000` — leaves headroom for reviewer context + response
- Auto-split oversized bundles (`_split_bundle_by_tokens()`)
- Priority-aware trimming (`_trim_to_token_limit()`) removes lowest-priority (middle) bundles first

---

## 5. TOKEN OPTIMIZATION STRATEGIES

### Format Efficiency
```yaml
# YAML saves ~15% vs JSON
# Markdown saves ~15% vs JSON
# TOON saves ~40% for tabular data
```

### Prompt Caching (Anthropic)
```python
# Cache stable prefix (system prompt, docs, tool defs)
# Dynamic content at suffix
# Use cache_control: {"type": "ephemeral"} on blocks
# 90% discount on cached input tokens
```

### Model Routing
```
Haiku 4.5 (200K, $0.25/$1.25) → Simple classification, extraction
Sonnet 4.6 (1M, $3/$15) → Most tasks, best quality/cost
Opus 4.8 (1M, $5/$25) → Complex reasoning, architecture
```

### Batch API
- 50% discount for non-urgent queued work
- Use for bulk processing, overnight jobs

### Prompt Compression (LLMLingua)
- 5-20x compression for retrieval-heavy workloads
- High effort, use when context window is binding constraint

---

## 6. RAG BEHAVIOR & FILE LIMITS

### The Critical Discovery (GitHub #25759, Feb 2026)
> **RAG activates at 13 files, NOT at context window limit.**

| File Count | Behavior | Warning |
|------------|----------|---------|
| 1-12 files | Direct context loading | None |
| **13+ files** | **RAG mode activates** | "To save space, Claude will look up specific information as needed" |
| Any count | Uses `project_knowledge_search` tool | Partial fragments, misses cross-file connections |

### RAG Quality Issues
> "Hallucinates details that contradict actual file contents (wrong character names, invented locations, incorrect family relationships, fabricated data)"
### Official vs Reality

| Anthropic Docs | Reality (Empirical) |
|----------------|---------------------|
| "RAG activates when approaching context limit" | Activates at 13 files regardless of token count |
| "10x capacity expansion" | True, but quality degrades |

### Mitigation

1. **Stay ≤12 files** — aggregate content
2. **Descriptive filenames** — "Claude searches by filename"
3. **If RAG unavoidable** — structure bundles with clear section IDs for retrieval

### RAG Acknowledgment Pattern (For Context Packs)

When providing context packs to Claude Projects, include this note:

> **How to use this pack**: Claude's RAG retrieves these files automatically when relevant. Reference them by bundle name (e.g., `grounding_part1.xml`, `mandates.xml`). The manifest is signed — verify integrity if suspicious.

This pattern works because it describes the mechanism accurately without asserting the contested trigger condition.
---

## 7. PROMPT ENGINEERING PATTERNS

### 10 Proven Techniques (Anthropic 2026 + AI for Anything 2026)

| # | Technique | When to Use |
|---|-----------|-------------|
| 1 | **XML Tags for Structure** | Complex prompts — separate context from instructions |
| 2 | **Detailed Role Assignment** | All tasks — shifts tone AND reasoning quality |
| 3 | **One Example Before Many** | Few-shot — show 1, then ask for N |
| 4 | **Chain-of-Thought Request** | Complex reasoning — "Think step by step" |
| 5 | **Think First, Then Respond** | High-stakes outputs — separate reasoning from answer |
| 6 | **Explicit Output Length/Format** | Always — don't hope it guesses |
| 7 | **Permission to Say "I Don't Know"** | Factual/legal/medical — reduces hallucination |
| 8 | **Iterative Refinement with Criteria** | Multi-step — explicit criteria per iteration |
| 9 | **System Prompts for Persistent Behavior** | API/Projects — not user messages |
| 10 | **Decompose Complex Tasks** | Sequential prompts > one massive prompt |

### XML Tagging (Claude-Native)
```xml
<context>
  [background information, documents, data]
</context>
<instructions>
  [what to do, constraints, format]
</instructions>
<output_format>
  [exact structure expected]
</output_format>
```

### Role Framing Depth
> "More than most models, detailed persona instructions shift both tone and reasoning quality."

**Template**:
```
You are a [specific role] with [years] experience in [domain].
You specialize in [sub-specialty].
Your approach is [methodology/philosophy].
You always [behavioral rule].
You never [anti-pattern].
```

### Chain-of-Thought Variants
| Variant | Use Case |
|---------|----------|
| "Think step by step" | General reasoning |
| "Think first, then respond in <answer> tags" | High-stakes, separate reasoning |
| "Show your work in <scratchpad>, then give final answer" | Math, logic, verification |
| "Consider [X], [Y], [Z] before concluding" | Multi-factor decisions |

---

## 8. MODEL SELECTION & ROUTING

### Decision Matrix

| Task Type | Recommended Model | Rationale |
|-----------|-------------------|-----------|
| Simple classification, extraction | Haiku 4.5 | 12x cheaper, 200K context |
| General coding, analysis, writing | Sonnet 4.6 | Best quality/cost, 1M context |
| Complex architecture, multi-step reasoning | Opus 4.8 | Highest reasoning, 1M context |
| Massive document ingestion (100K+ tokens) | Sonnet 4.6 or Opus 4.8 | 1M context, prompt caching |
| Production agent fleet | Local (Llama 4 Scout 10M) | Zero cost, full sovereignty |
| Cost-sensitive batch | Batch API (50% off) | Non-urgent, queueable |

### Local-First Mandate (Omega Engine M7)
```
native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6)
```
**Cloud is fallback, never primary.**

---

## 9. ADVANCED TECHNIQUES

### Dynamic/Lazy Context Loading
- Load verbose documentation on-demand via triggers
- **Result**: 54% reduction in startup tokens (7,584 → 3,434)
- Monthly cost for 5 devs × 100 sessions/day: $72 (62% savings)

### Programmatic Tool Calling (PTC)
- Claude writes code that calls tools programmatically
- **85.6% token reduction** demonstrated (110,473 → 15,919 tokens)
- 37% average reduction on complex research
- Keeps intermediate results out of context

### Token-Efficient Tool Use (Claude 4 Beta)
```http
anthropic-beta: token-efficient-tools-2025-02-19
```
- Average 14% output token savings (up to 70%)
- Reduces latency

### Context Pruning / Hierarchical Attention
- Remove redundant information before sending to flagship model
- Use smaller model as "context filter" (LLM-as-Judge)
- Recursive refinement ensures lean, relevant final prompt

### Multishot Examples in XML Tags (Official Best Practice)
> **Anthropic's official recommendation**: "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure. Include 3–5 examples wrapped in `<example>` tags (multiple in `<examples>` tags) so Claude can distinguish them from instructions."

**Template**:
```xml
<examples>
  <example>
    <input>User: How do I sort a list of dicts by key?</input>
    <output>
      Use `sorted(list_of_dicts, key=lambda x: x['key'])`.
      For descending: `sorted(list_of_dicts, key=lambda x: x['key'], reverse=True)`.
    </output>
  </example>
  <example>
    <input>User: What's the difference between list.sort() and sorted()?</input>
    <output>
      `list.sort()` mutates in-place and returns None. `sorted()` returns a new list.
    </output>
  </example>
</examples>
```

**Note**: The "writing sample calibration" technique (200-400 words of your writing) is a community practice. The **verified official pattern** is explicit multishot examples in XML tags. Writing samples work implicitly; examples work explicitly and are the recommended approach.

### Master Prompt Pattern (Production-Grade)
```xml
<system>
  <role>You are a [specific role] with [experience].</role>
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
  <behavioral_rules>
    <rule>Proactively flag problems, risks, better approaches.</rule>
    <rule>Teach me unknown best practices.</rule>
    <rule>Acknowledge gaps explicitly. Say "I don't know" when appropriate.</rule>
    <rule>No AI-isms: [list].</rule>
    <rule>Prose over bullets unless discrete items.</rule>
    <rule>Cite specific sources when referencing docs.</rule>
    <rule>Confirm scope before changes.</rule>
    <rule>Never skip error handling.</rule>
    <rule>No framework switching unless asked.</rule>
  </behavioral_rules>
  <tool_triggers>
    <trigger condition="current data needed">Web Search</trigger>
    <trigger condition="complex synthesis">Deep Research</trigger>
    <trigger condition="math/data analysis">Code Execution</trigger>
  </tool_triggers>
</system>
```

---

## 10. SOVEREIGN BOUNDARY PROTOCOLS

### Omega Engine Mandates Affecting Claude Usage

| Mandate | Claude Impact |
|---------|---------------|
| **M1 AnyIO Absolute** | All async code in generated artifacts must use AnyIO |
| **M2 Engine-Stack Firewall** | No WAD-specific logic in core engine recommendations |
| **M7 Local-First** | Prefer local model recommendations; cloud as fallback |
| **M8 Zero Telemetry** | No analytics, tracking, or phone-home in generated code |
| **M9 Error Integrity** | Typed errors, no bare `except:` in generated code |
| **M13 Temple-Grade** | T1-T11 gates apply to all generated artifacts |
| **M14 Heritage Vetting** | Any `[id-soft:]` tags need vet record |
| **M16 Modularization** | No hardcoded paths in generated core code |
| **M21 Gate Integrity** | Contract tests for typed returns |
| **M23 Failure Integrity** | No soft failures; hard stop on tool chain collapse |

### Context Pack Sovereignty
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

### External Reviewer Boundary
**Tools cross the boundary — content does not.**

| Crosses Boundary (Valid Export) | Stays Within Boundary (Internal) |
|----------------------------------|----------------------------------|
| Architecture, schema, CLI design | Which option was chosen |
| Integration patterns | What was decided |
| Prior art (universal knowledge) | Internal decision history |
| Mandates (design constraints) | Internal decision rationale |

The distinction is clear: external reviewers critique the **tools**, not the **content the tools process**.

---

## 11. QUICK REFERENCE CARDS

### Card 1: Claude Projects Setup (5 min)
```
1. claude.ai → Projects → "New Project"
2. Name: "Omega Engine Decision Tools Review"
3. Settings → Custom Instructions → Paste CLAUDE_PROJECT_SYSTEM_PROMPT.md
4. Upload context_packs/decision-tools-review/ (8 files)
5. Test query: "Review the DecisionEngine schema in grounding_part1.xml"
```

### Card 2: System Prompt Template (Copy-Paste)
```
You are an expert systems architect reviewing [topic].
Here is a sample of my writing for tone reference: [200-400 words].

Behavioral rules:
- Proactively flag problems, risks, better approaches
- Teach me unknown best practices
- Acknowledge gaps explicitly. Say "I don't know" when appropriate
- No AI-isms: Genuinely, Honestly, It's important to note, Straightforward, In today's world, Crucial, Delve, Tapestry, Landscape, Realm
- Prose over bullets unless discrete items
- Cite specific sources when referencing docs
- Confirm scope before changes
- Never skip error handling
- No framework switching unless asked

Tool triggers:
- Current data (2025-2026) → Web Search
- Complex synthesis → Deep Research
- Math/data analysis → Code Execution
```

### Card 3: Context Pack Checklist
```
☐ XML format (not JSON)
☐ ≤12 files total (7 bundles + manifest = 8 ✓)
☐ Ed25519 signed manifest
☐ LITM ordering: Critical at START/END
☐ PII masking: TOKENIZE mode
☐ Injection scan: 25 patterns
☐ Per-bundle ≤15K tokens
☐ Total ≤150K tokens
☐ All XML valid (ElementTree.parse)
```

### Card 4: Token Budget Calculator
```
Pack bundles:     41,422 tokens
Manifest:           573 tokens
System prompt:    1,848 tokens
────────────────────────
Total:            43,843 tokens
Headroom:        156,157 tokens (78% of 200K)
```

### Card 5: RAG Avoidance Rules
```
✅ ≤12 files per project
✅ Descriptive filenames (decisions_catalog_20260718.md)
✅ Aggregate related content
✅ Delete stale content
❌ 13+ files (triggers RAG)
❌ Generic names (final_v3.md)
❌ Many small files
```

### Card 6: Format Selection
```
Claude Projects → XML (native, best comprehension)
Token-constrained → YAML/Markdown (~15% savings)
Tabular data → TOON (~40% savings)
Structured output → JSON
```

### Card 7: Model Routing
```
Simple extraction/classification → Haiku 4.5 ($0.25/$1.25, 200K)
General coding/analysis → Sonnet 4.6 ($3/$15, 1M) ← DEFAULT
Complex architecture/reasoning → Opus 4.8 ($5/$25, 1M)
Batch/non-urgent → Batch API (50% off)
Production fleet → Local (Llama 4 Scout 10M, $0)
```

---

## 📚 SOURCE CITATIONS (Tier-Ordered)

### Tier 1: Official Documentation
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — 90% discount, cache_control
- [Anthropic XML Tags Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) — Native recommendation
- [Anthropic RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) — 10x capacity, auto-activation
- [OWASP LLM Prompt Injection Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — Defense-in-depth
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — ReversibleAnonymizer

### Tier 2: 2026 Technical Articles
- [TokenOptimize.dev 2026 Guide](https://www.tokenoptimize.dev/guides/llm-token-optimization-strategies) — Context engineering thesis
- [Thomas Wiegold: Prompt Engineering 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026) — XML for Claude
- [ImprovingAgents: Nested Data Formats](https://www.improvingagents.com/blog/best-nested-data-format) — YAML > JSON
- [AppScale: PII Redaction Pipeline 2026](https://appscale.blog/en/blog/pii-redaction-pipeline-llm-presidio-ner-reversible-tokenisation-2026) — Presidio + FPE + vault
- [Ice-Ice-Bear: OPF Reversible Tokenization](https://ice-ice-bear.github.io/posts/2026-05-07-openai-privacy-filter-reversible-tokenization/) — OPF schema
- [GitHub Issue #25759](https://github.com/anthropics/claude-code/issues/25759) — RAG at 13 files
- [UnderstandingData: Lost in Middle](https://understandingdata.com/posts/lost-in-the-middle-mitigation) — U-curve mitigation
- [DevNote: Context Window Engineering 2026](https://devstarsj.github.io/ai/llm/2026/04/11/llm-context-window-engineering-long-context-strategies-2026/) — Hybrid RAG/long-context
- [JD Hodges: Custom Instructions](https://www.jdhodges.com/blog/claude-ai-custom-instructions-a-real-example-that-actually-works/) — Proactive flagging, teach unknowns
- [UnderstandingAI: System Prompts](https://understandingai.net/claude-master-prompt/) — Writing sample calibration
- [LikeOne: Custom Instructions Guide](https://likeone.ai/blog/claude-custom-instructions-guide/) — Character limits, templates
- [AI for Anything: Prompt Engineering](https://aiforanything.io/blog/claude-prompt-engineering-best-practices-guide-2026) — 10 techniques
- [Anthropic Blog: Prompt Engineering 2026](https://claude.com/blog/best-practices-for-prompt-engineering) — Official best practices
- [Stackviv: Custom GPTs/Gems/Projects](https://stackviv.ai/blog/custom-gpts-gems-claude-projects) — Platform comparison

### Tier 3: Architectural Specifications
- [Sovereign Systems Specification](https://kenwalger.github.io/sovereign-system-spec/PATTERNS.html) — Sieve-and-Sign, Intent-Based Namespace, Context Compression, Hybrid Retrieval, Multi-Model Routing
- [Sovereign AI Stack 2026](https://www.topailearninghub.com/2026/05/sovereign-ai-stack-2026-why-i-left.html) — Local-first architecture

### Tier 4: Academic/ArXiv
- [arXiv:2511.13900](https://arxiv.org/abs/2511.13900) — GM-Extract, lost-in-the-middle mitigations
- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — CaMeL: Provable prompt injection defense
- [Liu et al. 2023](https://arxiv.org/abs/2307.03172) — Original lost-in-the-middle paper
- [arXiv:2605.15343](https://arxiv.org/abs/2605.15343) — Belief Engine: 5-step loop, uptake/anchoring
- [arXiv:2504.02128](https://arxiv.org/abs/2504.02128) — Three-round consensus protocol

---

## 🛡️ MANDATE

**All Omega Engine agents MUST consult this guide before any Claude interaction to avoid redundant research.**

**Version**: 1.0.0 | **Last Updated**: 2026-07-19 | **Next Review**: 2026-10-19

*⬡ OMEGA ⬡ KALI ⬡ CLAUDE-GUIDE-COMPLETE ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: RESEARCH-COMPLETE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
