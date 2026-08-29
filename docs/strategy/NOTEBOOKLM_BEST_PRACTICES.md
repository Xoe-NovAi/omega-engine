# 🔱 NotebookLM Best Practices — Omega Engine
**AP Token**: `AP-NOTEBOOKLM-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for NotebookLM (source-grounded research) interactions
**Supersedes**: `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` (NotebookLM section), `docs/intake/WEB-GEMINI_Research-Bridge-Implementation-Plan.md`

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Notebook creation, architecture, source-based approach |
| 2. Format Specification | `#2-format-specification` | Markdown + Sources for content, no system prompt |
| 3. Key Capabilities | `#3-key-capabilities` | Source grounding, audio overview, four analysis frameworks |
| 4. Source Organization | `#4-source-organization` | Source types, upload limits, thematic organization |
| 5. Analysis Frameworks | `#5-analysis-frameworks` | Compare/Contrast, Gap Analysis, Synthesis, Action Items |
| 6. Citation Style | `#6-citation-style` | NotebookLM-native citation format |
| 7. Audio Overview | `#7-audio-overview` | Podcast-style summary generation |
| 8. Sovereign Boundary Protocols | `#8-sovereign-boundary-protocols` | M7 local-first, M23 failure integrity, source verification |
| 9. Quick Reference | `#9-quick-reference` | Source limits, format quick reference, setup checklist |
| 10. Source Citations | `#10-source-citations` | Tier-ordered citations |
| 11. Hydration Protocol | `#11-hydration-protocol` | Mandatory steps before any NotebookLM interaction |

---

## 📋 EXECUTIVE SUMMARY

NotebookLM is the **primary platform** for source-grounded research synthesis, literature review, and multi-document analysis. Best for: source-cited verification, audio overview generation, collaborative research.

**Backend**: Gemini model (Google)
**Effective Context**: ~200K tokens (source-based, not raw context)
**Cost**: Free (as of 2026)

---

## 1. SETUP & ARCHITECTURE

### 1.0 Automation Tool — `notebooklm-py` (RPC) — **v2.1 Update (2026-08-20)**

**Recommended automation library**: **`notebooklm-py`** (teng-lin) with `[mcp]` extra — the ONLY library with documented Deep Research **report** trigger (`source add-research --mode deep`) + Markdown export (`download`). RPC-based (no browser at runtime) → best fit for local-first (M7) headless systemd deployment.

```bash
# Deployment (per account, M24 venv sovereignty)
source .venv/bin/activate && pip install "notebooklm-py[mcp]"

# Per-account isolated auth profile (mitigates ToS ban risk)
notebooklm profile create acct1 --auth <isolated-session>
export NOTEBOOKLM_PROFILE=acct1   # separate HOME/data dir per account

# systemd user service runs the MCP server (stdio) or guarded HTTP
notebooklm mcp --transport stdio     # or: notebooklm server --http --host 127.0.0.1
```

> **Critical**: `notebooklm-mcp` (TheSethRose) `research_start --mode deep` is **source-finding, NOT the quota-consuming Deep Research report**. Do NOT use it for the report path. Use `notebooklm-py` for Deep Research automation.

### 1.1 Notebook Creation
1. `notebooklm.google.com` → "Create Notebook"
2. Name after **research question** (e.g., "Omega Engine Technology Adoption Decision Matrix")
3. Upload sources (PDFs, URLs, Google Docs, text files, copied text)
4. NotebookLM indexes sources automatically
5. Use "Guided Prompts" for structured analysis

### 1.2 Architecture (2026)
- **Source-based RAG**: NotebookLM indexes uploaded sources, not raw context
- **Effective context**: ~200K tokens (depends on source count and size)
- **No system prompt**: Behavior guided by source content and analysis frameworks
- **Four analysis frameworks**: Compare/Contrast, Gap Analysis, Synthesis, Action Items
- **Citation style**: NotebookLM-native (source-linked, clickable)

### 1.3 Unique Capabilities
- **Source grounding**: Every response cites specific sources with clickable links
- **Audio Overview**: Auto-generated podcast-style summary (2 hosts discussing sources)
- **Guided Prompts**: Structured analysis frameworks
- **Multi-source synthesis**: Combines information across all uploaded sources

---

## 2. FORMAT SPECIFICATION

### 2.1 Content Format → **Markdown + Sources**
- **Upload sources directly**: PDFs, URLs, Google Docs, text files, copied text
- **Markdown for notes**: Your own notes and analysis in Markdown
- **No system prompt**: Behavior emerges from source content

### 2.2 Source Metadata (Critical)
Every source should include:
```markdown
<!-- Source: https://example.com/doc -->
<!-- Last fetched: 2026-08-08 -->
<!-- Coverage: complete API reference for v3.x -->
<!-- Version: 3.2.1 -->
```

### 2.3 Structured Data → **JSON**
- For schema definitions, configs, structured outputs

---

## 3. KEY CAPABILITIES

### 3.1 Source Grounding
- **Every claim traceable** to a specific source
- **Clickable citations** link to exact source location
- **No hallucination** of source content (verified by design)

### 3.1.1 Omega Engine Research Synthesis Workflow
1. **Gather sources**: Upload research docs, spec files, mandate documents
2. **Run Gap Analysis**: "What gaps exist in the current research on [topic] across all sources?"
3. **Run Synthesis**: "Synthesize a unified recommendation from all sources on [topic]"
4. **Run Action Items**: "What are the concrete action items for [decision]?"
5. **Generate Audio Overview**: For team briefing or async review
6. **Export findings** → feed into Web Claude or Web Gemini for deeper analysis

### 3.2 Audio Overview
- **Auto-generated podcast** (2 AI hosts discussing your sources)
- **~5-10 minutes** typical length
- **Great for team briefings** and async communication
- **Downloadable** as audio file

### 3.3 Four Analysis Frameworks
1. **Compare/Contrast** — Differences and similarities across sources
2. **Gap Analysis** — What's missing, what's contradictory
3. **Synthesis** — Unified understanding from multiple sources
4. **Action Items** — Concrete next steps from research

### 3.4 Guided Prompts
Pre-built prompts for each framework:
- "Compare the approaches in Source A and Source B"
- "What gaps exist in the current research?"
- "Synthesize a unified recommendation from all sources"
- "What are the concrete action items?"

---

## 4. SOURCE ORGANIZATION

### 4.1 Source Types & Limits
| Source Type | Limit | Notes |
|-------------|-------|-------|
| PDFs | 50 per notebook | Up to 200K tokens each |
| URLs | 50 per notebook | Auto-fetched and indexed |
| Google Docs | 50 per notebook | Native integration |
| Copied text | Unlimited | Pasted directly |
| Text files | 50 per notebook | .txt, .md files |

### 4.2 Thematic Organization
Organize sources by **theme**, not chronology:
```
Theme 1: Circuit Breaker Libraries
  - interlock-cb docs (PDF)
  - Honker GitHub (URL)
  - tenacity docs (URL)

Theme 2: MCP SDK Migration
  - MCP Python SDK v2 changelog (URL)
  - fastmcp v3 docs (URL)

Theme 3: Memory Architecture
  - sqlite-vec PRs (URL)
  - Honker + sqlite-vec coexistence (PDF)
```

### 4.3 Source Preparation Best Practices
1. **Trim sources**: Remove navigation, sidebars, ads before upload
2. **Version explicitly**: Name files with version (`react-v18-hooks.md`)
3. **Include deprecation notes**: If source has deprecation warnings, include them
4. **Strip unsupported languages**: Keep only relevant language examples
4. **Separate prose from references**: Auto-generated API refs in separate sources

---

## 5. ANALYSIS FRAMEWORKS

### 5.1 Compare/Contrast
**Prompt**: "Compare the approaches in [Source A] and [Source B] regarding [topic]. Highlight key differences in architecture, trade-offs, and recommendations."

**Output**: Structured comparison table with criteria, Source A position, Source B position, synthesis.

### 5.2 Gap Analysis
**Prompt**: "What gaps exist in the current research on [topic] across all uploaded sources? Identify missing perspectives, unverified claims, and areas needing investigation."

**Output**: Gap inventory with severity, source coverage, recommended next steps.

### 5.3 Synthesis
**Prompt**: "Synthesize a unified recommendation from all sources on [topic]. Resolve contradictions, weight by source authority, provide confidence levels."

**Output**: Unified recommendation with confidence, supporting evidence, dissenting views.

### 5.4 Action Items
**Prompt**: "Based on all sources, what are the concrete action items for [decision]? Prioritize by impact, effort, and risk."

**Output**: Prioritized action list with owner, timeline, dependencies, success criteria.

---

## 6. CITATION STYLE

### 6.1 NotebookLM-Native Citations
- **Clickable source links** in every response
- **Exact location** references (page, section, paragraph)
- **Multi-source citations** when claim supported by multiple sources

### 6.2 Citation Format for Export
When exporting findings for team use:
```markdown
> **Finding**: [claim]
> **Sources**: [Source A, §3.2], [Source B, p. 14], [Source C, L45-L52]
> **Confidence**: HIGH/MEDIUM/LOW
```

---

## 7. AUDIO OVERVIEW

### 7.1 Generation
1. Click "Audio Overview" button in notebook
2. Wait 1-3 minutes for generation
3. Download or share link

### 7.2 Best Practices
- **Upload all sources first** — overview quality depends on source completeness
- **Use for team briefings** — async communication, onboarding
- **Regenerate after major source changes** — not auto-updated

### 7.3 Limitations
- **English only** (as of 2026)
- **~5-10 minutes** typical length
- **Two-host format** fixed (not customizable)

---

## 8. SOVEREIGN BOUNDARY PROTOCOLS

### 8.1 Mandates Affecting NotebookLM Usage
| Mandate | Impact |
|---------|--------|
| **M7 Local-First** | NotebookLM is cloud-only — use for research ONLY, never for production inference |
| **M8 Zero Telemetry** | Google may collect usage data — treat as advisory, not sovereign |
| **M23 Failure Integrity** | Verify all claims against source citations — no soft failures |

### 8.2 Source Verification
- **Every claim must cite a source** — clickable verification
- **Cross-validate** across multiple sources when possible
- **Flag unverifiable claims** explicitly

### 8.3 PII Protection
- **Do not upload PII** to NotebookLM (Google cloud)
- **Tokenize locally first** if source contains PII
- **Use for public/universal knowledge only**

---

## 9. QUICK REFERENCE

### Source Limits
| Type | Limit | Max Size |
|------|-------|----------|
| PDFs | 50 | 200K tokens each |
| URLs | 50 | Auto-fetched |
| Google Docs | 50 | Native |
| Copied text | Unlimited | — |

### Format Quick Reference
| Layer | Format |
|-------|--------|
| Sources | PDF, URL, Google Doc, Text |
| Notes | Markdown |
| Structured data | JSON |
| Citations | NotebookLM-native |

### Setup Checklist
```
☐ Notebook created with research-question name
☐ All sources uploaded (PDFs, URLs, Docs, text)
☐ Source metadata included (URL, date, version, coverage)
☐ Sources organized thematically
☐ Audio Overview generated for team briefing
☐ Guided prompts used for structured analysis
☐ Findings exported with source citations
```

---

## 10. SOURCE CITATIONS

### Tier 1: Official
- NotebookLM: https://notebooklm.google.com
- NotebookLM Help: https://support.google.com/notebooklm

### Tier 2: 2026 Technical Articles
- zenn.dev Format Comparison: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- Context Link Platform Comparison: https://context-link.ai/blog/connect-files-to-claude (2026-04-02)

### Tier 3: Local Research (Evidence)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — NotebookLM platform profile
- `docs/intake/WEB-GEMINI_Research-Bridge-Implementation-Plan.md` — Research bridge plan

---

## 11. HYDRATION PROTOCOL

**Before any NotebookLM interaction, agents MUST:**
1. Read this document
2. Prepare sources with metadata (URL, date, version, coverage)
3. Organize sources thematically (not chronologically)
4. Upload all sources before starting analysis
5. Use guided prompts for structured analysis (all 4 frameworks)
6. Generate Audio Overview for team briefing
7. Export findings with NotebookLM-native citations
8. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
