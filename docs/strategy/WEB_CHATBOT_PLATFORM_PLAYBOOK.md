# 🔱 Web Chatbot Platform Playbook — Omega Engine
**AP Token**: `AP-WEB-CHATBOT-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Index for platform-specific best practices
**Purpose**: Agents start here, then navigate to platform-specific doc

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Platform Selection Matrix | `#1-platform-selection-matrix` | Choose the right platform for your task |
| 2. Format Decision Tree | `#2-format-decision-tree` | XML vs Markdown vs JSON by layer |
| 3. Platform-Specific Docs | `#3-platform-specific-docs` | Links to canonical best practices per platform |
| 4. Context Pack Delivery | `#4-context-pack-delivery` | Unified checklist for all platforms |
| 5. Sovereign Boundary Protocols | `#5-sovereign-boundary-protocols` | Universal mandates affecting all platforms |
| 6. Hydration Protocol | `#6-hydration-protocol` | Mandatory steps before any external chatbot interaction |

---

## 1. PLATFORM SELECTION MATRIX

### By Task Type

| Task | Best Platform | Free? | Why |
|------|---------------|-------|-----|
| Pre-refactor code review | **Web Claude** | ✅ Sonnet 5 | ~80-82% SWE-bench, instruction-following, XML system prompt |
| Architecture vetting | **Web Claude** | ✅ Sonnet 5 | Long-doc QA, structured reasoning, RAG mitigation patterns |
| Multi-source research synthesis | **Web Gemini** | ✅ Gemini 3.6 Flash | Deep Research, 1M context, code execution sandbox |
| Benchmark comparison | **Web Gemini** | ✅ Gemini 3.5 Flash | 92.7% GPQA Diamond, code execution for verification |
| Real-time data / current events | **Web Grok** | ✅ Grok 3/4 Mini | Live X firehose, real-time sentiment |
| Source-grounded analysis | **NotebookLM** | ✅ Free | Source citations, audio overview, multi-document synthesis |
| **Local terminal coding agent** | **Grok CLI (Grok Build)** | ⚠️ Promo | Grok 4.5 free during launch window; SuperGrok Heavy after |
| Cross-validation of critical decisions | **Claude + Gemini** | ✅ Both free | Independent verification of architecture decisions |

### Omega Engine Workflow Decision Matrix

| Omega Engine Task | Primary Platform | Secondary Platform | Local Integration |
|-------------------|-----------------|-------------------|-------------------|
| Pre-refactor code review | Web Claude | — | OpenCode CLI ingests artifact |
| Architecture decision vetting | Web Claude | Web Gemini (cross-check) | OpenCode CLI implements |
| Technology adoption research | Web Gemini | Web Grok (real-time) | NotebookLM synthesizes |
| Mandate compliance audit | Web Claude | — | OpenCode CLI enforces |
| Real-time trend monitoring | Web Grok | — | Findings feed Web Claude/Gemini |
| Research synthesis | NotebookLM | — | Summary feeds Web Claude/Gemini |
| Local code implementation | Grok CLI | OpenCode CLI | Direct file edits |
| Local code review | Grok CLI | OpenCode CLI | Sandbox-controlled |

### By Model Capability

| Model | SWE-bench | MRCR | GPQA | Context | Free? | Best Use |
|-------|-----------|------|------|---------|-------|----------|
| **Claude Sonnet 5** | ~80-82% | ~75% | ~90% | 1M | ✅ | Code review, deep analysis |
| **Claude Haiku 4.5** | ~70% | ~65% | ~85% | 1M | ✅ | Quick answers, summaries |
| ~~Claude Opus 4.8~~ | ~~82.1%~~ | ~~76%~~ | ~~90.5%~~ | ~~1M~~ | ❌ | ~~Deep reasoning (paid only)~~ |
| **Gemini 3.6 Flash** | — | — | — | 1M | ✅ | Default free, everyday tasks |
| **Gemini 3.5 Flash** | 78.8% | — | 92.7% | 1M | ✅ | Coding, research, benchmarks |
| **Gemini 3.1 Pro** | 65.2% | 70% | 95.3% | 2M | ⚠️ Varying | Deeper reasoning (switches to Flash) |
| **Grok 3 / 4 Mini** | — | — | — | 1M | ✅ | Quick questions, fact checks |
| ~~Grok 4.5 (Web)~~ | ~~70.8%~~ | ~~65%~~ | ~~87.5%~~ | ~~1M~~ | ❌ | ~~Agentic, real-time X (paid)~~ |
| **Grok 4.5 (Build CLI)** | — | — | — | 500K | ⚠️ Promo | Coding agent (limited-time free) |
| **grok-code-fast-1 (CLI)** | 70.8% | — | — | — | ❌ | Local coding, sub-agents |

---

## 2. FORMAT DECISION TREE

> **Core principle**: Format follows layer, not file type.

```
Is this...
├── A system prompt / custom instructions? → XML tags (Claude) / Markdown (Gemini/Grok/NotebookLM)
├── A knowledge/reference file (uploaded)? → Markdown (.md)
├── Structured data / schema? → JSON
├── Source document for NotebookLM? → Markdown with source metadata
├── Local CLI config/rules/skills? → TOML (config), Markdown (rules/skills)
└── Sandbox profiles? → TOML
```

### Detailed Format Guidance

#### System Prompt / Custom Instructions
| Platform | Format | Why |
|----------|--------|-----|
| **Web Claude** | **XML tags** (`<role>`, `<context>`, `<constraints>`, `<rules>`, `<output_format>`) | Claude's training data is XML-rich; Anthropic official docs recommend. Closing tags prevent instruction/input boundary confusion. |
| **Web Gemini** | **Markdown** (`##` headings) | Gemini's long-context handles structure; MD delimiters sufficient per Google docs. |
| **Web Grok** | **Markdown** | Long-context handles structure; MD delimiters sufficient. |
| **Grok CLI (Grok Build)** | **Markdown** (rules files) + **TOML** (config) | Local files; rules appended to system prompt, config in TOML. |
| **NotebookLM** | **Markdown** | Source-grounded; MD with source metadata. |

#### Knowledge/Reference Files (uploaded to Project Knowledge)
| Platform | Format | File Limit | Why |
|----------|--------|------------|-----|
| **Web Claude** | **Markdown (.md)** | 13 files (RAG at 14+) | Token-efficient (~15% fewer than XML), Claude parses headings/lists for RAG retrieval. XML tags consume tokens without RAG benefit. |
| **Web Gemini** | **Markdown (.md)** | 20-100 files | MD with clear headings; Gemini's long context handles large KBs. |
| **Web Grok** | **Markdown (.md) + file uploads** | 20-50 files | MD for notes, file uploads for PDFs/docs via web UI. |
| **Grok CLI (Grok Build)** | **Local files** (workspace) | Unlimited (local) | Direct filesystem access; respects `.gitignore`; sandbox controls writes. |
| **NotebookLM** | **Markdown + Sources** | Source-based | Upload sources (PDFs, URLs, docs); NotebookLM indexes them. |

#### Key Decision Rule (TeachYou 2026)
> **"Is this piece of the prompt data, or is it instructions? If it's data (variable, untrusted, multiple similar blocks), wrap in XML tags. If it's instructions (authored by you), use Markdown headings."**

---

## 3. PLATFORM-SPECIFIC DOCS

| Platform | Canonical Doc | Purpose |
|----------|---------------|---------|
| **Web Claude** | `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` | Setup, XML system prompt, file org, RAG, token optimization, sovereign boundaries |
| **Web Gemini** | `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md` | Setup, Markdown system prompt, code execution, parallel search, source grounding |
| **Web Grok** | `docs/strategy/WEB_GROK_BEST_PRACTICES.md` | Setup, Markdown system prompt, real-time X search, Connectors, Grok Skills (cloud) |
| **Grok CLI (Grok Build)** | `docs/strategy/GROK_CLI_BEST_PRACTICES.md` | Local CLI, TUI/headless/ACP, sandbox, local skills, local-first architecture |
| **NotebookLM** | `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` | Source upload, analysis frameworks, audio overview, citation style |

**Agents MUST read the platform-specific doc for their target platform before any interaction.**

---

## 4. CONTEXT PACK DELIVERY CHECKLIST

### For Web Claude
- [ ] System prompt converted to XML tags (ClaSSIC template)
- [ ] Force KB Search directive at top of Custom Instructions
- [ ] Knowledge files: ≤12 `.md` files
- [ ] Each file ≤500 lines, one topic per file
- [ ] `PROJECT_KNOWLEDGE_INDEX.md` included
- [ ] File update protocol documented (delete → wait → upload → new conversation)

### For Web Gemini
- [ ] System prompt in Markdown format
- [ ] Code execution snippets included where relevant
- [ ] Source citations in bundles
- [ ] Parallel search hints structured

### For Web Grok
- [ ] System prompt in Markdown format
- [ ] Real-time X search enabled (explicit x_search directives)
- [ ] Connectors configured (GitHub, Notion, Linear, etc.)
- [ ] Grok Skills created for reusable workflows
- [ ] Source metadata included for uploads

### For Grok CLI (Grok Build)
- [ ] SuperGrok Heavy subscription verified
- [ ] Sandbox profile selected (`workspace` for dev, `strict` for untrusted)
- [ ] Custom rules for Omega Engine mandates (M1, M7, M8, M13, M23)
- [ ] Local skills in `~/.grok/skills/` for reusable workflows
- [ ] `.gitignore` respected (secrets excluded by default)
- [ ] For headless/ACP: `grok agent stdio` or `-p` with `--output-format streaming-json`

### For NotebookLM
- [ ] Sources uploaded (not context pack)
- [ ] Source metadata included
- [ ] Analysis frameworks specified

---

## 5. SOVEREIGN BOUNDARY PROTOCOLS (Universal)

### M7 Local-First (Non-Negotiable)
- External chatbot reviews are **advisory only** — never cloud-only dependencies
- All recommendations must be implementable locally
- **Grok CLI (Grok Build) aligns with M7** — local-first architecture, snippet-only transmission
- No telemetry, no phone-home from any reviewed library

### M23 Failure Integrity
- External reviewers must not simulate rigor
- Every claim must cite a source URL
- "It should work" is disqualifying — we need proof

### PII Protection
- All context packs must use TOKENIZE mode for PII (Presidio/OPF/Privalyse)
- XML body escaping: escape ALL `<`, `>`, `&` in content
- Injection pattern scanning: 25 OWASP/Microsoft/Google patterns
- **Never upload PII/secrets** to cloud platforms (Web Grok, Web Gemini, Web Claude, NotebookLM)
- **Grok CLI**: Sandbox deny lists for credential files (`**/.env`, `**/*.pem`)

---

## 6. INTEGRATION FLOW (How Platforms Work Together)

### 6.1 The Omega Engine Multi-Platform Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE CLI (Local)                     │
│                                                             │
│  1. PLAN: Identify what needs external review               │
│     (code review? arch vet? research synthesis?)            │
│                                                             │
│  2. PACK: Run Context Packer → context_packs/<profile>/     │
│     (≤12 files, PII-masked, Ed25519 signed)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Web Claude   │ │ Web Gemini   │ │ Web Grok     │
│ (deep review)│ │ (research)   │ │ (real-time)  │
│              │ │              │ │              │
│ Upload pack  │ │ Upload pack  │ │ Upload pack  │
│ Run review   │ │ Run research │ │ Run search   │
│ Download     │ │ Download     │ │ Download     │
│ artifact     │ │ artifact     │ │ artifact     │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE CLI (Local)                     │
│                                                             │
│  3. INGEST: Read all artifacts, cross-validate             │
│     → Compare Claude/Gemini findings                       │
│     → Flag contradictions                                    │
│     → Make final decision (local context is arbiter)       │
│                                                             │
│  4. IMPLEMENT: Apply decisions via OpenCode CLI            │
│     or Grok CLI (sandbox)                                    │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Platform Handoff Protocol

When an external platform produces an artifact:

1. **Save** the artifact with proper naming: `<platform>-<task>-<date>-<account>.md`
2. **Log** in `data/coordination/WEB_CLAUDE_ARTIFACT_REGISTRY.md` (or platform-specific registry)
3. **Ingest** into the OpenCode CLI session that created the context pack
4. **Validate** using the platform-specific quality checklist (§7)
5. **Integrate** or **reject** with documented reasoning

### 6.3 Cross-Platform Validation

For critical decisions (architecture, mandate compliance, security):

1. **Same context pack** → Web Claude + Web Gemini (parallel)
2. **Compare findings** — look for agreement/disagreement
3. **Disagreements** → flag for OpenCode CLI arbitration (local files are ground truth)
4. **Real-time needs** → Web Grok for current X discussions on the topic
5. **Multi-source synthesis** → NotebookLM for literature review

### 6.4 Multi-Account Coordination

| Platform | Accounts | Rotation Strategy |
|----------|----------|-------------------|
| Web Claude | 8 | Sequential drain, parallel streams for different tasks |
| Web Gemini | 1-2 | Sequential, longer sessions |
| Web Grok | 1-2 | Sequential, real-time focused |
| NotebookLM | Unlimited | No quota limits, source-based |

---

## 7. PLATFORM-SPECIFIC VALIDATION CHECKLISTS

### Web Claude Artifact Validation
```
☐ Findings reference actual bundled file content (not hallucinated)
☐ Recommendations are mandate-compliant (M1, M2, M7, M8, M13)
☐ No cloud dependencies introduced (M7)
☐ No asyncio recommended (M1)
☐ AnyIO patterns correctly suggested
☐ Any [id-soft:] heritage tags have vet records in HERITAGE_VET_LOG.md
☐ Recommended tests use anyio.pytest_plugin
☐ Recommendations are consistent with PIVOT_LOG decisions
```

### Web Gemini Artifact Validation
```
☐ Claims cite specific source bundles with line references
☐ Code execution snippets are runnable and produce expected output
☐ Recommendations are implementable locally (M7)
☐ No asyncio in generated code (M1)
☐ Cross-check with Web Claude findings for contradictions
```

### Web Grok Artifact Validation
```
☐ X search results are from 2026 (not stale)
☐ Real-time sentiment is contextualized (not just raw numbers)
☐ Connector data is verified against actual repos
☐ Recommendations are grounded in current X discussions
```

### NotebookLM Artifact Validation
```
☐ Every claim has a clickable source citation
☐ Synthesis resolves contradictions across sources
☐ Confidence levels are stated for each finding
☐ Action items are prioritized by impact/effort/risk
```

---

## 8. HYDRATION PROTOCOL

**Before any external chatbot/CLI interaction, agents MUST:**
1. Read this playbook (`docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`)
2. Select the appropriate platform using the Selection Matrix (§1) and Workflow Decision Matrix (§1.2)
3. Read the platform-specific best practices doc (§3)
4. Follow the format guidance for that platform (§2)
5. Use the delivery checklist (§4) to prepare context packs
6. Review the platform-specific validation checklist (§7)
7. Log the interaction in `data/coordination/HMC_COLLABORATION_HUB.md`
8. After receiving artifacts: follow the Integration Flow (§6) for ingestion and cross-validation

**This playbook + platform-specific docs supersede all prior platform-specific docs for agent hydration.**

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
