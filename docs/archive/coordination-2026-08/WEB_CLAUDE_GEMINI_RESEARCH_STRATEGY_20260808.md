<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Platform Strategy Report — Web Claude vs Web Gemini for Technical Research
**AP Token**: `AP-PLATFORM-STRATEGY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_platform_strategy ⬡ 2026-08-08

**Date**: 2026-08-08
**Status**: ✅ COMPLETE
**Owner**: kali (with roc_racoon mining)
**Purpose**: Platform-specific strategy for delivering the TECH_ARCHITECTURE_RESEARCH_BRIEF to Web Claude and/or Web Gemini.

---

## §0 Executive Summary

**Recommendation**: Use **both platforms in parallel**, with task-specific assignment based on each platform's documented strengths.

| Platform | Strengths | Best For |
|----------|-----------|----------|
| **Web Claude** | Deep technical analysis, code review, long-document QA, instruction-following precision, citation clarity | Circuit breaker analysis, MCP v2 migration, sqlite-vec deep dive, httpx2 code-level verification |
| **Web Gemini** | Multi-source research, parallel web search, cost-efficient high-volume, code execution sandbox | Library maturity assessment, feature comparison, benchmark validation, dependency tree analysis |

**Assignment Strategy**:
- **Claude**: 4 technical deep-dive tasks (Areas 1, 3, 4, 6)
- **Gemini**: 4 research/benchmark tasks (Areas 2, 5, 7, 8)
- **Both**: Cross-validate on Areas 1 (interlock-cb) and 3 (MCP v2) for critical decisions

---

## §1 Platform Capabilities Matrix (2026)

### 1.1 Web Claude (claude.ai)

| Capability | Details | Source |
|------------|---------|--------|
| **Models** | Claude Opus 4.8 (top-tier), Claude Sonnet 4.6 (standard), Claude Haiku 4.5 (cost-efficient) | theaiarchitects.com |
| **Context Window** | 1M tokens (Opus 4.8 beta, Sonnet 4.6 standard) | tech-insider.org |
| **RAG Threshold** | 13 files triggers RAG mode (file-count based, not token-based) | R_CONTEXT_PACKER_WEB_CLAUDE_REVIEW_20260718.md |
| **Code Review** | 82.1% SWE-bench Verified (Sonnet 4.6), catches subtle bugs, multi-file reasoning | tech-insider.org, chernykh.dev |
| **Long-Document QA** | 76% MRCR v2 8-needle at 1M tokens, lower hallucination rates | lumichats.com |
| **Instruction Following** | 94.2% on instruction-following benchmark | tech-insider.org |
| **Projects Feature** | Persistent knowledge bases (≤12 files for direct context) | CLAUDE_PROJECTS.md |
| **Artifacts** | Live-rendered code, SVG, HTML, React previews | nesyona.com |
| **Pricing** | $3/$15 per MTok (Sonnet 4.6 intro), $5/$25 (Opus 4.8) | indianprompt.com |
| **Web Search** | Available via Claude Code, not native in web Claude | theaiarchitects.com |

### 1.2 Web Gemini (Gemini Advanced / Google AI Studio)

| Capability | Details | Source |
|------------|---------|--------|
| **Models** | Gemini 3.1 Pro (frontier), Gemini 3.5 Flash (speed), Gemini 3 Flash-Lite (cost) | indianprompt.com |
| **Context Window** | 2M tokens (Gemini 3.1 Pro), 1M (Gemini 3.5/3 Flash) | tech-insider.org |
| **Deep Research** | Multi-step autonomous research, 30+ search iterations, structured reports with citations | mindstudio.ai |
| **Code Execution** | Built-in Python sandbox (30s max runtime, 5 retry attempts) | ai.google.dev |
| **Parallel Search** | Grounding with Parallel Web Search API, 600 req/min, $1-5/1K requests | parallel.ai |
| **Google Workspace** | Native integration with Docs, Sheets, Drive, Gmail | theaiarchitects.com |
| **Multimodal** | Native image, video, audio processing in single model | tech-insider.org |
| **SWE-bench** | 63.8% (Gemini 3) | tech-insider.org |
| **GPQA** | 94.1% (Gemini 3.1 Pro) | tech-insider.org |
| **Pricing** | $7/$21 per MTok (Gemini 3.1 Pro), $0.15/MTok (Flash) | indianprompt.com |
| **Free Tier** | More generous than Claude | theaiarchitects.com |

### 1.3 Benchmark Comparison (2026)

| Benchmark | Claude Opus 4.6 | Gemini 3.1 Pro | Winner |
|-----------|-----------------|-----------------|--------|
| SWE-bench Verified | 82.1% | 63.8% | Claude |
| GPQA (reasoning) | 90.5% | 94.1% | Gemini |
| MMLU (knowledge) | 78.7% | 75.6% | Claude |
| HumanEval (coding) | 92.0% | 87.2% | Claude |
| MATH | 86.4% | 91.8% | Gemini |
| Long Context (RULER) | 91.1% | 93.7% | Gemini |
| Instruction Following | 94.2% | 88.6% | Claude |

---

## §2 Assignment Strategy

### 2.1 Claude Assignments (Technical Deep-Dive)

**Rationale**: Claude wins on code review (82.1% SWE-bench), multi-file reasoning, instruction-following precision, and long-document QA. These are the areas where we need code-level verification and precise migration analysis.

| Research Area | Why Claude |
|---------------|------------|
| **Area 1: interlock-cb** | Needs code-level analysis of asyncio imports, trio compatibility verification, feature comparison against our AsyncCircuitBreaker source |
| **Area 3: MCP SDK v2** | 8 import sites to map, breaking changes to enumerate, file-by-file migration checklist needed |
| **Area 4: httpx2** | Already installed — needs code-level verification of anyio usage, SSE compatibility check |
| **Area 6: sqlite-vec** | Deep technical analysis of rescore/IVF indexes, coexistence with Honker, migration path |

### 2.2 Gemini Assignments (Research & Benchmark)

**Rationale**: Gemini wins on multi-source research, parallel web search, cost-efficient high-volume tasks, and code execution sandbox. These are the areas where we need broad source gathering and benchmark validation.

| Research Area | Why Gemini |
|---------------|------------|
| **Area 2: Honker** | New library (April 2026) — need broad web search for adoption, API docs, AnyIO compatibility |
| **Area 5: Pydantic YAML** | Need to search PyPI, GitHub, Repology for pydantic_yaml alternatives, version history |
| **Area 7: structlog + prometheus** | Need to verify Python 3.13 compatibility, textfile collector pattern, integration details |
| **Area 8: stamina vs tenacity** | Need code execution sandbox to measure glue-code delta, feature comparison across sources |

### 2.3 Cross-Validation (Both Platforms)

| Research Area | Why Both |
|---------------|----------|
| **Area 1: interlock-cb** | Critical decision (replacing 5 breaker classes). Claude for code analysis, Gemini for library maturity/adoption research. |
| **Area 3: MCP v2** | Critical migration (8 import sites). Claude for breaking changes, Gemini for ecosystem adoption/migration guides. |

---

## §3 Platform-Specific Document Formatting

### 3.1 For Web Claude

**Format**: XML-native (Anthropic explicitly recommends XML tags as "genuinely the best structuring method")

**Key constraints**:
- RAG threshold: 13 files triggers RAG mode. Stay at ≤12 files for direct context.
- System prompt limit: 8,000 chars in Projects
- U-shaped attention: critical content at positions 1-3 and N-2 to N

**Structure**:
```xml
<research_brief>
  <project_context>
    <name>Omega Engine Technology Architecture Research</name>
    <constraints>
      <mandate id="M1">AnyIO — all async code uses anyio, no direct asyncio imports</mandate>
      <mandate id="M7">Local-first — no new cloud-only dependencies</mandate>
      <mandate id="M8">Zero telemetry — no external reporting</mandate>
    </constraints>
  </project_context>

  <ground_truth>
    <python_version>3.13.7</python_version>
    <installed_packages>
      <package name="httpx2" version="2.5.0" status="installed"/>
      <package name="tenacity" version="9.1.4" status="installed"/>
      <package name="mcp" version="1.28.1" status="installed"/>
      <package name="sqlite-vec" version="0.1.9" status="installed"/>
      <package name="interlock-cb" status="NOT installed"/>
    </installed_packages>
  </ground_truth>

  <research_area id="1">
    <title>interlock-cb v2.1.3 — AnyIO/Trio Compatibility</title>
    <current_state>5 circuit breaker classes in codebase. AsyncCircuitBreaker (944 lines) is canonical.</current_state>
    <research_questions>
      <question priority="CRITICAL">Does interlock-cb work under AnyIO's trio backend?</question>
      <question>Feature parity with AsyncCircuitBreaker (CUSUM, sliding-window, 429 classification)?</question>
    </research_questions>
    <success_criteria>Yes/no on trio compat, feature comparison table, risk assessment</success_criteria>
  </research_area>
</research_brief>
```

**Prompt Template for Claude**:
```
You are a senior Python infrastructure engineer reviewing a critical technology adoption decision.

CONTEXT: The Omega Engine is a local-first AI runtime with strict constraints:
- M1: All async code uses AnyIO (asyncio + trio compatible). No direct asyncio imports.
- M7: Local-first. No new cloud-only dependencies.
- M8: Zero telemetry. No external reporting.
- Python 3.13.7, Linux platform.

GROUND TRUTH (verified 2026-08-08):
- interlock-cb is NOT installed. We need to verify it before adoption.
- tenacity v9.1.4 IS installed, used in 3 files (retry_policy.py, extractors.py, model_gateway.py).
- httpx2 v2.5.0 IS installed, used in 6 files (4 aliased as httpx, 2 direct).
- mcp v1.28.1 IS installed. FastMCP used in 5 files.
- sqlite-vec v0.1.9 IS installed.
- Python 3.13.7, requires >=3.12.

[INSERT research area details here]

YOUR TASK: For each research question, provide:
1. A definitive answer with evidence (URLs, version numbers, code snippets)
2. A feature comparison table against our current implementation
3. AnyIO compliance verdict (YES/NO/UNVERIFIED with explanation)
4. Risk assessment (library youth, maturity, known issues)
5. Migration path with exact steps and estimated effort

Format your response as a structured report. Cite every claim with a source URL.
```

### 3.2 For Web Gemini

**Format**: Markdown with structured frontmatter (Gemini excels with clear headings)

**Key advantages**:
- 2M token context (Gemini 3.1 Pro)
- ~20-50 file tolerance (vs 13 for Claude)
- Built-in code execution sandbox
- Parallel web search via Deep Research

**Structure**:
```markdown
---
project: Omega Engine Technology Architecture Research
date: 2026-08-08
python_version: 3.13.7
constraints:
  - M1: AnyIO (no direct asyncio)
  - M7: Local-first
  - M8: Zero telemetry
---

# Research Brief: [Area Name]

## Project Context
The Omega Engine is a local-first AI runtime. Python 3.13.7 on Linux.

## Ground Truth (Verified 2026-08-08)
- interlock-cb: NOT installed
- tenacity v9.1.4: installed, 3 consumers
- httpx2 v2.5.0: installed, 6 consumers
- mcp v1.28.1: installed, 8 import sites
- sqlite-vec v0.1.9: installed

## Research Questions
1. [CRITICAL] Does interlock-cb work under AnyIO's trio backend?
2. Feature parity with AsyncCircuitBreaker?

## What We Need
- Answer each question with evidence (URLs, version numbers)
- Feature comparison table
- AnyIO compliance verdict
- Risk assessment
- Migration path with effort estimate
```

**Prompt Template for Gemini**:
```
You are a research analyst evaluating technology adoption decisions for a local-first AI runtime.

## Project Context
The Omega Engine is a local-first AI runtime with strict constraints:
- M1: All async code uses AnyIO (asyncio + trio compatible). No direct asyncio imports.
- M7: Local-first. No new cloud-only dependencies.
- M8: Zero telemetry. No external reporting.
- Python 3.13.7, Linux platform.

## Ground Truth (verified 2026-08-08)
- interlock-cb: NOT installed — need to verify before adoption
- tenacity v9.1.4: installed, used in 3 files
- httpx2 v2.5.0: installed, used in 6 files
- mcp v1.28.1: installed, 8 import sites
- sqlite-vec v0.1.9: installed
- Python 3.13.7, requires >=3.12

## Research Area: [Area Name]

[Insert details]

## Your Task
1. Use your built-in web search to gather sources on each question
2. Use your code execution sandbox to verify any technical claims
3. For each research question, provide:
   - Definitive answer with evidence (URLs, version numbers, code snippets)
   - Feature comparison table against our current implementation
   - AnyIO compliance verdict (YES/NO/UNVERIFIED)
   - Risk assessment
   - Migration path with effort estimate

## Output Format
Present findings as a structured Markdown report. Every claim must cite a source URL. Use tables for comparisons. Include a "Sources" section at the end.
```

---

## §4 Integration Into Dev Flow

### 4.1 Delivery Sequence

1. **Send to both platforms** with platform-specific formatting (§3)
2. **Collect both reports** (24-48h turnaround)
3. **Cross-validate** critical decisions (interlock-cb, MCP v2)
4. **Synthesize** into a single decision matrix
5. **Present to kali** for go/no-go on each technology

### 4.2 File Management

- **Claude Projects**: Upload ≤12 files (RAG threshold). Include:
  - `TECH_ARCHITECTURE_RESEARCH_BRIEF.md` (split into per-area files)
  - `UNOVERENGINEERING_PLAN.md` (current plan)
  - `RESEARCH_TECH_ARCHITECTURE_DECISIONS_20260808.md` (existing findings)
  - Key source files (health_monitor.py, tools.py, mcp_client.py)

- **Gemini**: Can handle more files (30+ tolerance). Include:
  - Same files as Claude
  - Plus: dependency tree outputs, benchmark data
  - Use code execution for verification

### 4.3 Expected Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Brief delivery | 1h | Both platforms have formatted briefs |
| Research execution | 24-48h | Both platforms return reports |
| Cross-validation | 2h | kali synthesizes findings |
| Decision matrix | 2h | Go/no-go on each technology |
| **Total** | **27-51h** | **Final recommendation** |

---

## §5 Sources

| # | Source | URL | Accessed |
|---|--------|-----|----------|
| 1 | Claude Code Review docs | code.claude.com/docs/en/code-review | 2026-08-08 |
| 2 | Claude Code on the Web guide | claudelab.net/en/articles/... | 2026-08-08 |
| 3 | Claude Code Advanced Patterns | resources.anthropic.com | 2026-08-08 |
| 4 | AI-assisted code reviews | chernykh.dev/blog/... | 2026-08-08 |
| 5 | Claude AI for code review | aiforanything.io/blog/... | 2026-08-08 |
| 6 | Claude Code review catch real bugs | padezhnov.com/en/blog/... | 2026-08-08 |
| 7 | Gemini Code Execution API | ai.google.dev/gemini-api/docs/code-execution | 2026-08-08 |
| 8 | Grounding with Parallel Web Search | docs.cloud.google.com | 2026-08-08 |
| 9 | Parallel Function Calling in Gemini | gemilab.net/en/articles | 2026-08-08 |
| 10 | Gemini Deep Research API | www.mindstudio.ai/blog | 2026-08-08 |
| 11 | Vertex AI Code Execution | cloud.google.com/vertex-ai | 2026-08-08 |
| 12 | Parallel Search API best practices | deepwiki.com/parallel-web | 2026-08-08 |
| 13 | Gemini vs Google Search grounding | parallel.ai/articles | 2026-08-08 |
| 14 | Combine Google Search + custom functions | www.marktechpost.com | 2026-08-08 |
| 15 | Claude vs Gemini real work | theaiarchitects.com/blog | 2026-08-08 |
| 16 | Claude vs Gemini document analysis | www.indianprompt.com | 2026-08-08 |
| 17 | Claude vs Gemini 2026 benchmarks | tech-insider.org | 2026-08-08 |
| 18 | Gemini vs Claude 20 tasks tested | nesyona.com/articles | 2026-08-08 |
| 19 | Gemini vs Claude academic research | lumichats.com/blog | 2026-08-08 |
| 20 | Claude vs Gemini 2026 | tygartmedia.com | 2026-08-08 |

---

## §6 Recommendation

**Use both platforms in parallel with task-specific assignment:**

1. **Send Areas 1, 3, 4, 6 to Claude** — these need code-level analysis and precise migration planning
2. **Send Areas 2, 5, 7, 8 to Gemini** — these need broad research and benchmark validation
3. **Send Areas 1 and 3 to both** — cross-validation on critical decisions
4. **Use platform-specific formatting** (§3) — XML for Claude, Markdown for Gemini
5. **Collect both reports, cross-validate, synthesize** into a single decision matrix

This approach leverages each platform's documented strengths while providing redundancy on the most critical decisions. The total research time is 24-48h (parallel), not 48-96h (sequential).

---

*⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_platform_strategy ⬡ 2026-08-08 ⬡ COMPLETE*
*Sources: 20 (web research + local docs)*
*Research depth: 3 (moderate — focused queries with source verification)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
