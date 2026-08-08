# 🔱 Web Gemini Best Practices — Omega Engine
**AP Token**: `AP-WEB-GEMINI-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Web Gemini (AI Studio, Gems, API) interactions
**Supersedes**: `docs/research/GEMINI_DEEP_AUDIT_TASK.md`, `docs/research/GEMINI_CLI_QUICK_REF.md`, `docs/research/LEGACY_GEMINI_STRATEGY.md`, `docs/research/R_GEMINI_CLI_TECHNICAL_REPORT.md`

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Gem creation, architecture, model capabilities |
| 2. Format Specification | `#2-format-specification` | Markdown for system prompt and knowledge files |
| 3. Key Capabilities | `#3-key-capabilities` | Code execution, parallel search, Workspace integration |
| 4. File Organization | `#4-file-organization` | File count limits, structure, source grounding |
| 5. System Prompt Template | `#5-system-prompt-template` | Markdown-based template with Gemini-specific directives |
| 6. Cost Optimization | `#6-cost-optimization` | Model selection, pricing, batch strategies |
| 7. Source Grounding & Citations | `#7-source-grounding--citations` | Citation format, parallel search hints, verification snippets |
| 8. Sovereign Boundary Protocols | `#8-sovereign-boundary-protocols` | M7 local-first, M23 failure integrity, PII protection |
| 9. Quick Reference | `#9-quick-reference` | Model comparison, format quick reference, setup checklist |
| 10. Source Citations | `#10-source-citations` | Tier-ordered citations |
| 11. Hydration Protocol | `#11-hydration-protocol` | Mandatory steps before any Web Gemini interaction |

---

## 📋 EXECUTIVE SUMMARY

Web Gemini (Google AI Studio) is the **primary platform** for broad research synthesis, benchmark comparison, and code execution verification. Best for: GPQA (92.7% for Flash), Deep Research (30+ parallel searches), code execution sandbox.

**Available Models (Free Tier — as of August 2026)**: 
| Model | Context | Free? | Best For |
|-------|---------|-------|----------|
| **Gemini 3.5 Flash** | 1M | ✅ | Flagship free model, coding, research |
| **Gemini 3.6 Flash** | 1M | ✅ | Newer Flash variant |
| **Gemini 3.1 Flash-Lite** | 1M | ✅ | Cost-optimized, high-volume |
| **Gemini 3 Flash (Preview)** | 1M | ✅ | Previous-gen Flash |
| ~~Gemini 3.1 Pro~~ | ~~10M~~ | ❌ | **Paid only** ($2/$12/MTok) |
| ~~Gemini 3 Pro~~ | ~~1-2M~~ | ❌ | **Paid only** ($1.25/$2.50/MTok) |

> **Key fact**: Pro-series models moved off the free tier on April 1, 2026. Only Flash and Flash-Lite variants remain free. Gemini 3.5 Flash (launched May 19, 2026) is the current flagship free model — ~25% cheaper than Gemini 3.1 Pro on coding tasks while delivering comparable quality. SWE-bench Verified: 78.8%. GPQA Diamond: 92.7%.

---

## 1. SETUP & ARCHITECTURE

### 1.1 Gem Creation
1. `aistudio.google.com` → "Create Gem"
2. Name after **outcome** (e.g., "Omega Engine Technology Adoption Research")
3. Add Custom Instructions (Markdown format)
4. Upload files to Gem's knowledge
5. Enable "Code Execution" and "Grounding with Google Search" as needed
6. Test retrieval: "Based on `file.md` in knowledge, what is X?"

### 1.2 Architecture (2026)
- **1-10M context window** (model-dependent)
- **Parallel Web Search**: Multiple search queries in parallel via "Grounding with Google Search"
- **Code Execution**: Built-in Python sandbox (30s max, 5 retries)
- **Google Workspace**: Native Drive, Docs, Sheets, Gmail access
- **Video Understanding**: Native video input (up to 2M tokens)

### 1.3 Model Capabilities
| Model | Context | SWE-bench | GPQA | Free? | Best For |
|-------|---------|-----------|------|-------|----------|
| **Gemini 3.5 Flash** | 1M | 78.8% | 92.7% | ✅ | Flagship free, coding, research |
| **Gemini 3.6 Flash** | 1M | — | — | ✅ | Newer Flash variant |
| **Gemini 3.1 Flash-Lite** | 1M | — | — | ✅ | Cost-optimized, high-volume |
| Gemini 3.1 Pro | 10M | 65.2% | 95.3% | ❌ | Ultra-long context (paid only) |
| Gemini 3 Pro | 1-2M | 63.8% | 94.1% | ❌ | Flagship (paid only) |

---

## 2. FORMAT SPECIFICATION

### 2.1 System Prompt / Custom Instructions → **Markdown**
Gemini's long-context handles structure; Markdown delimiters sufficient per Google docs. No XML tags needed.

### 2.2 Knowledge/Reference Files (Uploaded) → **Markdown (.md)**
- **Token-efficient** and human-readable
- **Larger file count tolerance**: 20-100 files effectively
- **Source grounding**: Include source citations in bundles

### 2.3 Structured Data → **JSON**
- Machine-to-machine, schema enforcement

### 2.4 Source Documents → **Markdown + Source Metadata**
- For NotebookLM-style source-grounded analysis
- Include source URLs, access dates, version info

---

## 3. KEY CAPABILITIES

### 3.1 Code Execution (Built-in Python Sandbox)
- **30s max execution time**, 5 retries
- Use for verification scripts, benchmark runs, data analysis
- Include runnable snippets in bundles:
```python
# Verification: Ed25519 signature check
import nacl.signing, nacl.encoding
vk = nacl.signing.VerifyKey(PUBLIC_KEY, encoder=nacl.encoding.HexEncoder)
vk.verify(b"MANIFEST_CONTENT", bytes.fromhex(SIGNATURE))
print("✅ Signature valid")
```

### 3.2 Parallel Web Search (Grounding with Google Search)
- Multiple search queries in parallel
- Structure bundles for parallel verification:
  - Group related checks (all security, all mandate compliance, all token limits)
  - Each group can be verified independently

### 3.3 Google Workspace Integration
- Native Drive, Docs, Sheets, Gmail access
- Export findings as Google Docs/Sheets compatible format

### 3.4 Long Context Handling
- **20-100 files** effectively (vs 13 for Claude)
- **Explicit budget allocation** across categories:
  - System prompt
  - Retrieved context
  - Conversation history
  - Working space
  - Output reserve

---

## 4. FILE ORGANIZATION

### 4.1 File Count & Structure
- **20-100 files** effectively (no hard RAG threshold like Claude)
- **One topic per file** — but can handle larger files
- **Source grounding**: Every claim traceable to a source bundle
- **Citation format**: `[spec.md §3.2]` for spec references, `[impl_part1.md:L312]` for implementation

### 4.2 Required Files
1. `PROJECT_KNOWLEDGE_INDEX.md` — entry point with descriptions
2. `GROUNDING.md` — architecture overview, current state
3. `MANDATES.md` — Sovereign Mandates M1-M25
4. Domain-specific bundles (thematic organization)

### 4.3 Bundle Ordering
- **Relevance-descending** for research tasks
- **Hierarchical** for ultra-long context (Gemini 3.1 Pro)
- **Thematic** for source-grounded analysis

---

## 5. SYSTEM PROMPT TEMPLATE (Markdown)

```markdown
## Role
You are a [specific role] with [experience] in [domain].
You specialize in [sub-specialty].
Your approach is [methodology].

## Context
[Project context, hardware reality, constraints]

## Constraints
- FORBIDDEN to [violation]
- MUST [requirement]

## Rules
1. [Behavioral rule]
2. [Behavioral rule]

## Output Format
[Response structure template]

## Gemini-Specific Directives

### Source Grounding
Every claim must be traceable to a source bundle. Use citation format:
- `[spec.md §3.2]` for spec references
- `[impl_part1.md:L312]` for implementation line references

### Parallel Search Optimization
Structure your review to enable parallel verification:
- Group related checks (all security, all mandate compliance, all token limits)
- Each group can be verified independently

### Code Execution Ready
Include runnable verification snippets where applicable.

### Workspace Export
Format findings for Google Docs/Sheets export:
- Tables as Markdown (auto-converts)
- Findings as structured rows
- Severity as filterable column
```

---

## 6. COST OPTIMIZATION

### 6.1 Model Selection
| Task Type | Model | Cost (input/output) | Context | Free? |
|-----------|-------|---------------------|---------|-------|
| General research/analysis | **Gemini 3.5 Flash** | Free | 1M | ✅ |
| High-volume, simple | Gemini 3.1 Flash-Lite | Free | 1M | ✅ |
| Ultra-long context | ~~Gemini 3.1 Pro~~ | $2/$12/MTok | 10M | ❌ |
| Cost-sensitive batch | Batch API | 50% off | — | ❌ |

### 6.2 Omega Engine Use Cases
| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Multi-source library research | Gemini 3 Pro | 94.1% GPQA, parallel search |
| Technology adoption comparison | Gemini 3 Pro | Benchmark comparison, code execution |
| Long-doc architecture review | Gemini 3.1 Pro | 10M context, no truncation |
| Verification scripts | Gemini 3 Pro | Code execution sandbox |
| Cross-validation of Claude findings | Gemini 3 Pro | Independent model perspective |

### 6.3 Pricing Notes (2026)
- **Gemini 3 Pro**: $1.25/$2.50/MTok (<200K), $2.50/$5.00/MTok (>200K)
- **Context window** = prompt tokens + response tokens + system overhead
- **Truncation** happens when limit reached — summarize earlier content
- **File uploads** count toward context (text extracted from PDFs, etc.)

---

## 7. SOURCE GROUNDING & CITATIONS

### 7.1 Citation Format
- Spec references: `[spec.md §3.2]`
- Implementation: `[impl_part1.md:L312]`
- Research: `[research_report.md §4.3]`

### 7.2 Parallel Search Hints
Structure bundles to enable independent verification:
```
Security Checks → [bundle_security.md]
Mandate Compliance → [bundle_mandates.md]
Token Limits → [bundle_tokens.md]
```

### 7.3 Verification Snippets
Include runnable code for critical verifications (see §3.1).

---

## 8. SOVEREIGN BOUNDARY PROTOCOLS

### 8.1 Mandates Affecting Gemini Usage
| Mandate | Impact |
|---------|--------|
| **M1 AnyIO** | All async code in generated artifacts must use AnyIO |
| **M7 Local-First** | Prefer local model recommendations; cloud as fallback |
| **M8 Zero Telemetry** | No analytics, tracking, or phone-home in generated code |
| **M13 Temple-Grade** | T1-T11 gates apply to all generated artifacts |
| **M23 Failure Integrity** | No soft failures; hard stop on tool chain collapse |

### 8.2 PII Protection
- All context packs must use TOKENIZE mode for PII (Presidio/OPF/Privalyse)
- Injection pattern scanning: 25 OWASP/Microsoft/Google patterns

---

## 9. QUICK REFERENCE

### Model Comparison
| Model | Context | Input/Output | Best For |
|-------|---------|--------------|----------|
| Gemini 3 Flash | 1M | $0.075/$0.30/MTok | Cost-optimized, high-volume |
| Gemini 3 Pro | 1-2M | $1.25/$2.50/MTok | Flagship, balanced |
| Gemini 3.1 Pro | 10M | Preview | Ultra-long context |

### Format Quick Reference
| Layer | Format |
|-------|--------|
| System prompt | Markdown |
| Knowledge files | Markdown (.md) |
| Structured data | JSON |
| Source documents | Markdown + metadata |

### Setup Checklist
```
☐ Gem created with outcome-based name
☐ Custom Instructions in Markdown format
☐ Code Execution enabled
☐ Grounding with Google Search enabled
☐ Knowledge files uploaded as .md
☐ Source citations included
☐ Parallel search hints structured
```

---

## 10. SOURCE CITATIONS

### Tier 1: Official
- Google AI Studio Code Execution: https://ai.google.dev/gemini-api/docs/code-execution
- Google AI Studio Grounding: https://ai.google.dev/gemini-api/docs/grounding
- Google AI Studio Context Windows: https://ai.google.dev/gemini-api/docs/context-windows

### Tier 2: 2026 Technical Articles
- zenn.dev Format Comparison: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- Context Link Platform Comparison: https://context-link.ai/blog/connect-files-to-claude (2026-04-02)

### Tier 3: Local Research (Evidence)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — Platform profiles, system prompts
- `docs/research/R_GEMINI_CLI_TECHNICAL_REPORT.md` — CLI technical details
- `docs/research/GEMINI_DEEP_AUDIT_TASK.md` — Deep audit findings

---

## 11. HYDRATION PROTOCOL

**Before any Web Gemini interaction, agents MUST:**
1. Read this document
2. Select appropriate model (Flash/Pro/3.1 Pro)
3. Prepare system prompt in Markdown format
4. Prepare knowledge files as `.md` with source citations
5. Enable Code Execution and Grounding as needed
6. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
