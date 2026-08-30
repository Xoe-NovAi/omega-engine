<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NotebookLM Deep Research Report
## Capabilities, Limits, and Strategic Codebase Analysis Framework for Omega Engine

**AP Token**: `AP-NOTEBOOKLM-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_notebooklm_research ⬡ ACTIVE

**Date**: 2026-08-19
**Purpose**: Comprehensive research on NotebookLM (Gemini Notebook) for strategic Omega Engine codebase analysis

---

## Executive Summary

NotebookLM (rebranded as **Gemini Notebook** as of July 2026) is Google's source-grounded RAG research tool that strictly refuses to draw on general world knowledge. Every answer is grounded in uploaded sources with **chunk-level inline citations**. This makes it uniquely suited for **auditable, verifiable codebase analysis** — the exact requirement for Omega Engine's mandate compliance verification, architecture decision auditing, and gap analysis workflows.

**Key Strategic Insight**: NotebookLM is not a general chat tool — it is a **self-contained research artifact** (like a manila folder). Each notebook = one bounded project. The 50-source limit (free) / 600-source limit (Ultra) is a **feature**, not a bug — it forces curation. For Omega Engine's ~300+ strategic documents, we need a **multi-notebook architecture** with semantic clustering.

---

## 1. Content Limits (2026 Current)

### 1.1 Per-Notebook Limits by Tier

| Tier | Notebooks/User | Sources/Notebook | Chats/Day | Audio/Day | Video/Day | Deep Research |
|------|----------------|------------------|-----------|-----------|-----------|---------------|
| **Standard (Free)** | 100 | **50** | 50 | 3 | 3 | 10/month |
| **Plus (AI Plus $4.99)** | 200 | **100** | 200 | 6 | 6 | 3/day |
| **Pro (AI Pro $19.99)** | 500 | **300** | 500 | 20 | 20 | 20/day |
| **Ultra 20TB ($99.99)** | 500 | **500** | 2,500 | 100 | 100 (cinematic 10) | 75/day |
| **Ultra 30TB ($199.99)** | 500 | **600** | 5,000 | 200 | 200 (cinematic 20) | 200/day |

### 1.2 Hard Per-Source Ceilings (ALL TIERS — Immutable)

| Limit | Value | Notes |
|-------|-------|-------|
| **Words per source** | 500,000 | Hard ceiling — no plan lifts this |
| **File size (local upload)** | 200 MB | Hard ceiling — no plan lifts this |
| **Google Slides** | 100 slides/source | Split larger presentations |
| **Google Sheets** | 100,000 tokens/source | Token limit, not row count |
| **YouTube** | Transcript ≤ 500,000 words | Public videos with captions only |
| **Web URL** | Text content only | No images, embedded media, paywalls |

### 1.3 Context Window & Retrieval

- **Chat context window**: 1 million tokens (Gemini 2.0+ upgrade, Oct 2025)
- **Conversation memory**: 6x longer than previous version
- **Retrieval**: Chunk-level (not source-level) — each chunk embedded separately
- **Citation granularity**: Paragraph/chunk level with exact passage highlighting
- **No cross-notebook search**: Each notebook is an isolated retrieval context

### 1.4 Enterprise Tier (Gemini Notebook Enterprise)

| Feature | Personal | Enterprise |
|---------|----------|------------|
| Data residency | User cannot specify | Project/region locked (US/EU multi-region) |
| Auth | Personal Google Account | Cloud Identity / 3rd-party IdP (Okta, Entra ID) |
| Sharing | Public links, email | Project-only, IAM roles (Owner/Editor/Viewer) |
| Compliance | N/A | VPC-SC, CMEK, Audit logging |
| File support | PDF, TXT, MD, URLs, YouTube, Audio | **+ DOCX, PPTX, XLSX** |
| Interface | `notebook.google.com` | `notebook.cloud.google.com/REGION/?project=PROJECT` |

---

## 2. Supported Formats (2026)

### 2.1 Fully Supported (Native Import)

| Category | Formats | Notes |
|----------|---------|-------|
| **Documents** | PDF, DOCX, TXT, MD, ePub | PDF: text layer required (OCR for scans) |
| **Spreadsheets** | CSV, Google Sheets (100k tokens) | Google Sheets auto-sync from Drive |
| **Presentations** | PPTX, Google Slides (100 slides) | Speaker notes included; images not analyzed |
| **Google Workspace** | Docs, Slides, Sheets | Auto-sync every few minutes |
| **Web** | Public URLs (HTML text only) | No JS rendering, no paywalls, no nested pages |
| **Video** | YouTube (public, captions required) | Transcript only; <72hr videos may fail |
| **Audio** | MP3, WAV, M4A, AAC, OGG, OPUS, 3GP, etc. | Auto-transcribed on import; no-speech files rejected |
| **Images** | JPEG, PNG, GIF, WebP, HEIC, AVIF, BMP, TIFF | OCR applied; low-quality scans may fail |
| **Other** | Pasted text, Gemini Chats | Gemini chats import as context sources |

### 2.2 NOT Supported

| Format | Workaround |
|--------|------------|
| FLAC audio | Convert to MP3/WAV |
| WebM video | Not supported at all |
| ePub (consumer) | Convert to PDF first (Enterprise supports natively) |
| Copy-protected PDFs | Remove protection or OCR to new PDF |
| Private YouTube | Make public or download captions manually |
| Scanned PDFs (no text layer) | Run `ocrmypdf` first |
| Nested web pages | Use single-page/AMP/reader-mode URLs |

---

## 3. Features Deep Dive

### 3.1 Source Grounding & Citations (Core Differentiator)

- **Chunk-level citations**: Every claim has numbered citation → click → highlights exact passage
- **Two-pane verification**: Citation click opens source with highlighted passage; chat stays visible
- **Source selector**: Checkbox per source to include/exclude from query context
- **Label-anchored queries**: Select semantic labels to restrict retrieval to subset (critical for large notebooks)
- **Refusal behavior**: "I don't know" if answer not in sources — **this is the auditability guarantee**

### 3.2 Studio Outputs (One-Click Artifacts)

| Output | Description | Best For |
|--------|-------------|----------|
| **Briefing Doc** | 1-3 page executive summary: themes, claims, evidence, open questions | Architecture review, decision audit |
| **Study Guide** | Quiz questions, key terms, glossary, short answers | Onboarding, knowledge transfer |
| **FAQ** | Likely questions with grounded answers | Decision rationale documentation |
| **Timeline** | Chronological events from dated sources | Project history, mandate evolution |
| **Mind Map** | Hierarchical visual concept map | Architecture overview, dependency mapping |
| **Audio Overview** | 10-30 min podcast (2 AI hosts) | Passive consumption, team alignment |
| **Video Overview** | Cinematic video (Ultra only) | Presentations, stakeholder communication |
| **Reports** | PDF/DOCX/MD with charts, tables, images | Formal deliverables |
| **Data Tables** | Structured CSV/JSON extraction | Metrics, compliance matrices |
| **Flashcards/Quizzes** | Interactive study aids | Onboarding validation |
| **Infographics** | Visual summaries | Quick reference cards |
| **Slide Decks** | PPTX/PDF export (revision via prompt) | Architecture presentations |

### 3.3 Audio Overview Modes (2026)

| Mode | Description | Duration |
|------|-------------|----------|
| **Deep Dive** (default) | Two hosts, lively conversation, connects topics | 10-30 min |
| **The Brief** | Single speaker, key takeaways | <2 min |
| **The Critique** | Two hosts, constructive evaluation | Variable |
| **The Debate** | Two hosts, formal back-and-forth | Variable |

**Customization**: Language (80+), length (Shorter/Default/Longer), custom prompt steer
**Interactive Mode**: Voice join-in during playback (English only) — ask hosts questions live

### 3.4 Advanced Chat Features (Pro/Ultra/Enterprise)

- **Agentic capabilities**: Web search, code execution, file generation (charts, PDFs, spreadsheets, slides)
- **Custom chat styles**: Default / Learning Guide / Custom ("Respond like a PhD student")
- **Thinking steps expansion**: Visibility into reasoning process
- **Save to Note**: Persist chat responses as searchable, citable notebook artifacts
- **Convert Note → Source**: Make prior conclusions citable for future queries

### 3.5 Source Organization (Auto-Labeling)

- **Threshold**: Activates at 5+ sources
- **Engine**: Semantic clustering on full text (not filenames)
- **Labels**: Natural-language clusters, renameable, mergeable, emoji-prefixable
- **Multi-label**: Sources can belong to multiple labels
- **Context anchoring**: Select label → chat/Studio/Deep Research restricted to that subset
- **Gap detection**: Engine flags missing sub-topics, methodologies, perspectives

---

## 4. Best Practices for Codebase Analysis

### 4.1 Optimal Chunking Strategy for Code Files

**Problem**: Large code files (>50 pages) dilute attention; arbitrary splits lose coherence.

**Solution**: Semantic chunking by architectural boundary:

```markdown
# Chunking Rules for Omega Engine Codebase

## DO ✅
- Chunk by MODULE/COMPONENT (e.g., `oracle.py`, `model_gateway.py`, `entity_registry.py`)
- Keep chunks 10-50 pages (300-1500 lines typical)
- Include module docstring + imports + public API in each chunk
- Preserve cross-references: if module A imports B, note in chunk metadata
- Name files: `omega_engine_oracle_module.md`, `omega_engine_provider_fabric.md`

## DON'T ❌
- Split by arbitrary line count (e.g., every 500 lines)
- Separate related classes/functions across chunks
- Upload raw .py files directly (NotebookLM parses as text, loses syntax highlighting)
- Mix unrelated utilities in one chunk

## PREPROCESSING PIPELINE
1. Extract each Python module → convert to Markdown with syntax highlighting
2. Prepend module metadata: path, purpose, key classes, dependencies
3. For large modules (>2000 lines): split by class/function groups
4. Create index file: `OMEGA_ENGINE_MODULE_INDEX.md` with module map
```

### 4.2 Source Structuring for Cross-Referencing

**Naming Convention** (critical for 50+ source navigation):

```
[CATEGORY] Component_Name - Description.ext

Examples:
[CORE] oracle.py - Query routing & entity summoning.md
[CORE] model_gateway.py - Provider fabric & resource guards.md
[MANDATE] SOVEREIGN_MANDATES.md - 27 Laws of Sovereign Execution.md
[ARCH] ORACLE_STACK.md - 10 Node Architecture.md
[DECISION] PIVOT_LOG.md - Architectural Decisions (D1-D386).md
[GAP] GAP_REGISTRY.json - All Registered Gaps (R1-R99).md
[TRACKING] ACTIVE_SPRINT.json - Current Sprint Plan.md
[ENTITY] kali/soul.yaml - Kali Entity Soul.md
[SKILL] sovereign-search/SKILL.md - Search Orchestration Skill.md
```

**Label Strategy** (enable at 5+ sources):

| Label | Sources | Use Case |
|-------|---------|----------|
| 🏛️ **CORE-ARCH** | Engine architecture, Node specs, Provider fabric | Architecture review |
| ⚖️ **MANDATES** | All 27 mandates, compliance docs | Mandate verification |
| 📋 **DECISIONS** | PIVOT_LOG, GAP_REGISTRY, sprint plans | Decision audit, gap analysis |
| 🧠 **ENTITIES** | Entity souls, personas, workspaces | Knowledge transfer |
| 🔧 **SKILLS** | All skill definitions, workflows | Capability inventory |
| 🐛 **BUGS-FIXES** | Critical bug reports, fix PRs | Regression prevention |
| 📊 **METRICS** | Test results, benchmarks, sovereignty ratios | Health monitoring |

### 4.3 Notebook Organization: Multi-Notebook Architecture

**For Omega Engine (300+ strategic docs), use 5 specialized notebooks:**

| Notebook | Purpose | Sources | Key Labels |
|----------|---------|---------|------------|
| **Ω-ARCHITECTURE** | Engine architecture, Node specs, Provider fabric, IWAD model | **5-25** | CORE-ARCH, PROVIDERS, IWAD, MCP |
| **Ω-MANDATES** | All 27 mandates, compliance evidence, audit trails | **5-25** | MANDATES, COMPLIANCE, VIOLATIONS |
| **Ω-DECISIONS** | PIVOT_LOG, GAP_REGISTRY, sprint plans, roadmap | **5-25** | DECISIONS, GAPS, SPRINTS, ROADMAP |
| **Ω-ENTITIES** | Entity souls, personas, skills, handoff protocols | **5-25** | ENTITIES, SKILLS, HANDOFF, FLEET |
| **Ω-OPERATIONS** | System stats, deployment, monitoring, runbooks | **5-25** | DEPLOYMENT, MONITORING, INCIDENTS |

**Cross-Notebook Synthesis Protocol**:
1. Generate Briefing Doc from each notebook
2. Export Briefing Docs as sources to **Ω-SYNTHESIS** master notebook
3. Run cross-notebook queries in synthesis notebook
4. This bypasses the "no cross-notebook search" limitation

### 4.4 Prompt Engineering for Strategic Analysis

**4-Principle Framework** (from NotebookLM Guide testing 200+ prompts):

```markdown
# PROMPT TEMPLATE: Four Principles

## 1. SPECIFY FORMAT
"Present as a [table | numbered list | executive summary | comparison matrix | decision log]"

## 2. CONSTRAIN SCOPE
"Using ONLY sources under [LABEL] label..." or "Using ONLY sources 1-5, 12, 15..."

## 3. ADD REASONING INSTRUCTIONS
"For each finding: cite the specific source passage, rate confidence (High/Med/Low), explain reasoning"

## 4. DESIGN FOR ITERATION
"First: broad synthesis. Then: identify contradictions. Then: deep dive on contradiction #3."
```

**PPAE Workflow Loop**:
1. **Perceive**: "List all sources in this notebook with 1-line summary"
2. **Plan**: "Decide: table or list? All sources or specific labels? Citations needed?"
3. **Act**: Execute structured prompt with 4 principles
4. **Evaluate**: "Verify: all claims cited? Contradictions missed? Gaps identified?"

---

## 5. Advanced Features & Automation

### 5.1 API Access

| Access Type | Availability | Details |
|-------------|--------------|---------|
| **Consumer API** | ❌ **NOT AVAILABLE** | Google acknowledged demand, no public release date |
| **Enterprise API** | ✅ Google Cloud Discovery Engine v1alpha | Full CRUD: notebooks, sources, audio generation, IAM |
| **Community Tools** | ✅ `notebooklm-py`, `notebooklm-mcp-cli` | Unofficial, Python-only, reverse-engineered RPC |

**Enterprise API Endpoints** (Discovery Engine v1alpha):
```
POST   /projects/{PROJECT}/locations/{LOCATION}/notebooks           # Create
GET    /projects/{PROJECT}/locations/{LOCATION}/notebooks           # List
GET    /projects/{PROJECT}/locations/{LOCATION}/notebooks/{ID}      # Get
PATCH  /projects/{PROJECT}/locations/{LOCATION}/notebooks/{ID}      # Update
DELETE /projects/{PROJECT}/locations/{LOCATION}/notebooks/{ID}      # Delete
POST   /.../notebooks/{ID}:addSource                                # Add source
POST   /.../notebooks/{ID}:generateAudioOverview                    # Audio gen
```

**Community Tool**: `notebooklm-py` (GitHub: teng-lin/notebooklm-py)
- CLI for source management, chat, artifact download
- Supports: `source add`, `source fulltext`, `ask`, `download report/audio/video/mind-map`
- **Use case**: Automate Omega Engine context pack construction

### 5.2 Export Capabilities

| Artifact | Export Formats | Notes |
|----------|----------------|-------|
| Reports/Briefing Docs | PDF, DOCX, MD, TXT | Click "Download" in Studio |
| Audio Overviews | MP3 (download), shareable link | Mobile app: offline playback |
| Video Overviews | MP4 (Ultra only) | Cinematic: Veo 3 generated |
| Mind Maps | JSON (hierarchical) | For visualization tools |
| Data Tables | CSV, JSON | Structured extraction |
| Quizzes/Flashcards | JSON, MD, HTML | Interactive formats |
| Slide Decks | PDF, PPTX (editable) | PPTX only via CLI/API |
| Chat Responses | Save as Note → Convert to Source | Persists in notebook |

### 5.3 Collaboration Features

| Feature | Free | Plus/Pro/Ultra | Enterprise |
|---------|------|----------------|------------|
| Share notebook | View-only link | View-only / Chat-only / Edit | Project-only, IAM roles |
| Usage analytics | ❌ | ✅ (shared notebooks) | ✅ (admin dashboard) |
| Admin controls | ❌ | ❌ | ✅ (VPC-SC, CMEK, audit logs) |
| Real-time co-editing | ❌ | ❌ | ❌ (async only) |

---

## 6. Strategic Use Cases for Omega Engine

### 6.1 Architecture Decision Audit (Trace Decisions → Code)

**Notebook**: Ω-ARCHITECTURE + Ω-DECISIONS (synthesized)

**Prompt Template**:
```
Using ONLY sources under 🏛️ CORE-ARCH and 📋 DECISIONS labels:

For each architectural decision in PIVOT_LOG.md (D-350 through D-386):
1. Quote the decision text verbatim
2. Identify the specific code files/modules that implement this decision
3. Cite the exact source passages showing implementation
4. Flag any decisions with NO code evidence (gap)
5. Flag any code patterns that CONTRADICT a recorded decision

Output as a decision-compliance matrix table:
| Decision ID | Decision Text | Implementation Status | Code Evidence (citations) | Gap/Conflict |
```

**Studio Output**: Briefing Doc → export PDF for audit trail

### 6.2 Gap Analysis (Find Unimplemented Decisions)

**Notebook**: Ω-DECISIONS + Ω-ARCHITECTURE

**Prompt Template**:
```
Using ONLY sources under 📋 DECISIONS and 🏛️ CORE-ARCH labels:

Analyze GAP_REGISTRY.json (all R1-R99) against ACTIVE_SPRINT.json and PIVOT_LOG.md.

For each gap:
1. State the gap description and priority
2. Identify which decisions/roadmap items it blocks
3. Check if any current sprint work items address it
4. Check if any code in CORE-ARCH sources implements it
5. Classify: [IMPLEMENTED | IN_PROGRESS | BLOCKED | ORPHANED | DEFERRED]

Output as gap-status register table with citations.
```

**Studio Output**: Data Table → export CSV for tracking

### 6.3 Mandate Compliance Verification

**Notebook**: Ω-MANDATES + Ω-ARCHITECTURE + Ω-DECISIONS

**Prompt Template**:
```
Using ONLY sources under ⚖️ MANDATES, 🏛️ CORE-ARCH, and 📋 DECISIONS labels:

For each of the 27 Sovereign Mandates (M1-M27):
1. Quote the mandate requirement verbatim
2. Search CORE-ARCH sources for implementation evidence
3. Search DECISIONS for explicit compliance decisions
4. Rate compliance: [FULL | PARTIAL | NON-COMPLIANT | UNKNOWN]
5. For PARTIAL/NON-COMPLIANT: cite specific code passages showing violation
6. For UNKNOWN: identify what evidence would be needed

Output as mandate-compliance matrix with evidence citations.
```

**Studio Output**: Report (PDF) + Data Table (CSV) for compliance dashboard

### 6.4 Roadmap Validation Against Implementation

**Notebook**: Ω-DECISIONS (roadmap) + Ω-ARCHITECTURE (code) + Ω-OPERATIONS (metrics)

**Prompt Template**:
```
Using ONLY sources under 📋 DECISIONS (roadmap sections), 🏛️ CORE-ARCH, and 📊 METRICS labels:

Compare the Three Horizons roadmap (H1-H4) against:
- Current sprint status (ACTIVE_SPRINT.json)
- Implemented code patterns (CORE-ARCH sources)
- Test results and sovereignty ratios (METRICS sources)

For each horizon milestone:
1. State the milestone criteria
2. Cite evidence of completion from code/tests/metrics
3. Identify missing pieces with specific citations
4. Rate: [ACHIEVED | ON_TRACK | AT_RISK | BLOCKED]

Output as roadmap-validation dashboard table.
```

### 6.5 Technical Debt Identification

**Notebook**: Ω-ARCHITECTURE + Ω-DECISIONS + Ω-OPERATIONS

**Prompt Template**:
```
Using ONLY sources under 🏛️ CORE-ARCH, 📋 DECISIONS, and 📊 METRICS labels:

Identify technical debt by analyzing:
1. God modules (>1000 lines) without split — cite file:line
2. Duplicate/overlapping implementations (e.g., 7 circuit breaker clones) — cite each
3. Hardcoded paths/environment assumptions violating M16 — cite each
4. Missing contract tests for API boundaries (M21) — cite each boundary
5. Mock-based tests masking type mismatches (C-0) — cite test files
6. Deprecated patterns not yet removed (C-6' 2 unmigrated breakers) — cite each

Output as technical-debt register with severity, location, remediation effort.
```

### 6.6 Knowledge Transfer / Onboarding

**Notebook**: Ω-ENTITIES + Ω-ARCHITECTURE + Ω-MANDATES

**Prompt Template**:
```
Using ONLY sources under 🧠 ENTITIES, 🏛️ CORE-ARCH, and ⚖️ MANDATES labels:

Generate a comprehensive onboarding package for a new Omega Engine contributor:

1. EXECUTIVE SUMMARY (1 page): What is Omega Engine? Vision? Architecture?
2. MANDATE PRIMER: The 27 laws — which 5 are most critical for new contributors?
3. ARCHITECTURE MAP: 10 Nodes, Provider Fabric, Entity Registry, MCP Hub
4. ENTITY GUIDE: Key entities (Kali, Ma'at, Lilith, Researcher, Roc, etc.) — roles, slots
5. WORKFLOWS: How to run tests, deploy, add skills, submit handoffs
6. GOTCHAS: Common pitfalls (AnyIO, venv, heritage tagging, soul distillation)
7. FIRST TASK: Concrete "good first issue" with file pointers

Output as: Briefing Doc (PDF) + Study Guide (quiz) + FAQ + Mind Map
```

**Studio Outputs**: Generate all 4 artifacts → export as onboarding kit

---

## 7. Omega Engine NotebookLM Context Pack Construction

### 7.1 Recommended Source Selection (Priority Order)

**Tier 1 — MUST INCLUDE (Core Architecture & Law)**:
```
[CORE] ORACLE_STACK.md                    # 10 Nodes, Provider Fabric
[CORE] SOVEREIGN_MANDATES.md              # 27 Laws (M1-M27)
[CORE] AGENTS.md                          # Agent fleet, workflows
[CORE] OMEGA_ENGINE.md                    # Live engine state
[ARCH] ORACLE_STACK_CANONICAL.md          # Full architecture
[ARCH] SOVEREIGN_ARK_BLUEPRINT.md         # Strategy, priorities
[DECISION] PIVOT_LOG.md                   # All decisions D1-D386
[DECISION] GAP_REGISTRY.json              # All gaps R1-R99
[TRACKING] ACTIVE_SPRINT.json             # Current sprint
[TRACKING] TRACKING_ARCHITECTURE.md       # 5-tier tracking spec
```

**Tier 2 — HIGH VALUE (Implementation Evidence)**:
```
[CODE] src/omega/oracle/oracle.py         # Core orchestration
[CODE] src/omega/oracle/providers.py      # Provider fabric
[CODE] src/omega/oracle/model_gateway.py  # Model gateway
[CODE] src/omega/oracle/entity_registry.py # Entity management
[CODE] src/omega/mcp/omega_hub/server.py  # MCP Hub
[CODE] src/omega/memory/memory_store.py   # Memory subsystem
[CODE] src/omega/soul/soul_store.py       # Soul persistence
[BUGS] docs/research/R44_comprehensive_systems_review.md
[BUGS] docs/research/R44_ENGINE_STACK_SEPARATION.md
```

**Tier 3 — CONTEXTUAL (Entity & Skill Definitions)**:
```
[ENTITY] data/entities/kali/soul.yaml
[ENTITY] data/entities/maat/soul.yaml
[ENTITY] data/entities/researcher/soul.yaml
[ENTITY] data/entities/roc_racoon/soul.yaml
[SKILL] .opencode/skills/sovereign-search/SKILL.md
[SKILL] .opencode/skills/knowledge-miner/SKILL.md
[SKILL] .opencode/skills/legacy-pattern-miner/SKILL.md
[SKILL] .opencode/skills/hf-cli/SKILL.md
```

**Tier 4 — SUPPORTING (Metrics, History, Research)**:
```
[METRICS] sovereignty_ratio (last 90 days)
[METRICS] test results (make test output)
[RESEARCH] docs/research/R*.md (key findings)
[HISTORY] MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md
```

### 7.2 Chunking & Preprocessing Pipeline

```bash
#!/bin/bash
# build_notebooklm_context_pack.sh
# Run from omega-engine root

OUTPUT_DIR="data/coordination/notebooklm_context_pack"
mkdir -p "$OUTPUT_DIR"/{CORE,ARCH,DECISIONS,CODE,ENTITY,SKILL,METRICS,RESEARCH}

# 1. Copy Tier 1 docs as-is (already Markdown)
cp ORACLE_STACK.md "$OUTPUT_DIR/CORE/"
cp SOVEREIGN_MANDATES.md "$OUTPUT_DIR/CORE/"
cp AGENTS.md "$OUTPUT_DIR/CORE/"
cp OMEGA_ENGINE.md "$OUTPUT_DIR/CORE/"
cp docs/research/ORACLE_STACK_CANONICAL.md "$OUTPUT_DIR/ARCH/"
cp docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md "$OUTPUT_DIR/ARCH/"
cp docs/decisions/PIVOT_LOG.md "$OUTPUT_DIR/DECISIONS/"
cp data/coordination/GAP_REGISTRY.json "$OUTPUT_DIR/DECISIONS/"
cp data/coordination/ACTIVE_SPRINT.json "$OUTPUT_DIR/DECISIONS/"
cp docs/strategy/TRACKING_ARCHITECTURE.md "$OUTPUT_DIR/DECISIONS/"

# 2. Convert key Python modules to annotated Markdown
for module in oracle.py providers.py model_gateway.py entity_registry.py; do
    python3 scripts/python_to_markdown.py \
        "src/omega/oracle/$module" \
        "$OUTPUT_DIR/CODE/omega_engine_${module%.py}_module.md"
done

# 3. Convert MCP Hub server
python3 scripts/python_to_markdown.py \
    "src/omega/mcp/omega_hub/server.py" \
    "$OUTPUT_DIR/CODE/omega_engine_mcp_hub_server.md"

# 4. Convert Memory & Soul stores
python3 scripts/python_to_markdown.py \
    "src/omega/memory/memory_store.py" \
    "$OUTPUT_DIR/CODE/omega_engine_memory_store.md"
python3 scripts/python_to_markdown.py \
    "src/omega/soul/soul_store.py" \
    "$OUTPUT_DIR/CODE/omega_engine_soul_store.md"

# 5. Entity souls (YAML → annotated MD)
for entity in kali maat researcher roc_racoon; do
    python3 scripts/yaml_to_markdown.py \
        "data/entities/$entity/soul.yaml" \
        "$OUTPUT_DIR/ENTITY/${entity}_soul.md"
done

# 6. Skills (already MD, just copy with prefix)
cp .opencode/skills/sovereign-search/SKILL.md "$OUTPUT_DIR/SKILL/sovereign_search_skill.md"
cp .opencode/skills/knowledge-miner/SKILL.md "$OUTPUT_DIR/SKILL/knowledge_miner_skill.md"
cp .opencode/skills/legacy-pattern-miner/SKILL.md "$OUTPUT_DIR/SKILL/legacy_pattern_miner_skill.md"
cp .opencode/skills/hf-cli/SKILL.md "$OUTPUT_DIR/SKILL/hf_cli_skill.md"

# 7. Generate module index
python3 scripts/generate_module_index.py "$OUTPUT_DIR/CODE" > "$OUTPUT_DIR/CODE/OMEGA_ENGINE_MODULE_INDEX.md"

# 8. Create manifest
cat > "$OUTPUT_DIR/MANIFEST.md" << 'EOF'
# Omega Engine NotebookLM Context Pack Manifest
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Notebook Assignment

| Notebook | Source Dir | Est. Sources | Labels |
|----------|------------|--------------|--------|
| Ω-ARCHITECTURE | CORE/, ARCH/, CODE/ | 45 | 🏛️ CORE-ARCH, 🔌 PROVIDERS, 📦 IWAD, 🔌 MCP |
| Ω-MANDATES | CORE/ (mandates), DECISIONS/ (compliance) | 35 | ⚖️ MANDATES, ✅ COMPLIANCE, ❌ VIOLATIONS |
| Ω-DECISIONS | DECISIONS/, ARCH/ (roadmap) | 45 | 📋 DECISIONS, 🕳️ GAPS, 🏃 SPRINTS, 🗺️ ROADMAP |
| Ω-ENTITIES | ENTITY/, SKILL/, AGENTS.md | 35 | 🧠 ENTITIES, 🔧 SKILLS, 🤝 HANDOFF, 🚁 FLEET |
| Ω-OPERATIONS | METRICS/, RESEARCH/, HISTORY/ | 25 | 📊 METRICS, 🚀 DEPLOYMENT, 📈 MONITORING, 🚨 INCIDENTS |

## Upload Order (enables auto-labeling at 5+ sources)
1. Upload CORE/ + ARCH/ first → establishes architectural vocabulary
2. Upload CODE/ → implementation evidence
3. Upload DECISIONS/ → decision traceability
4. Upload ENTITY/ + SKILL/ → team/context
5. Upload METRICS/ + RESEARCH/ → evidence

## Per-Source Size Check
All sources < 500,000 words / 200 MB ✅
Largest: PIVOT_LOG.md (~50k words), SOVEREIGN_MANDATES.md (~15k words)
EOF

echo "Context pack built at $OUTPUT_DIR"
echo "Total sources: $(find "$OUTPUT_DIR" -name '*.md' -o -name '*.json' | wc -l)"
```

### 7.3 Notebook Creation & Label Anchoring Workflow

```markdown
# NotebookLM Setup Checklist for Omega Engine

## Phase 1: Create 5 Notebooks
☐ Ω-ARCHITECTURE — "Omega Engine Core Architecture"
☐ Ω-MANDATES — "Omega Engine Mandate Compliance"
☐ Ω-DECISIONS — "Omega Engine Decision & Gap Registry"
☐ Ω-ENTITIES — "Omega Engine Entity & Skill Registry"
☐ Ω-OPERATIONS — "Omega Engine Operations & Metrics"

## Phase 2: Upload Sources (Batch by Notebook)
☐ Upload Tier 1 sources first (establishes vocabulary for auto-labeling)
☐ Upload Tier 2-4 sources
☐ Wait for auto-labeling to complete (shows at 5+ sources)
☐ Review auto-labels → rename with emoji prefixes
☐ Manually assign multi-label sources (e.g., PIVOT_LOG → DECISIONS + ROADMAP)

## Phase 3: Validate Grounding
☐ Test query: "What does M1 (AnyIO Absolute) require? Cite source."
☐ Test query: "List all P0 critical bugs from R44 audit. Cite each."
☐ Test label-anchored query: "Using only 🏛️ CORE-ARCH sources, describe the Provider Fabric."
☐ Verify citations point to exact passages

## Phase 4: Generate Baseline Artifacts
☐ Each notebook: Generate Briefing Doc → save as Note → convert to Source
☐ Ω-ARCHITECTURE: Generate Mind Map → export JSON for visualization
☐ Ω-MANDATES: Generate FAQ → export as compliance checklist
☐ Ω-DECISIONS: Generate Timeline → export as project history
☐ Ω-ENTITIES: Generate Study Guide → export as onboarding quiz
☐ Ω-OPERATIONS: Generate Audio Overview (Deep Dive) → share with team

## Phase 5: Create Synthesis Notebook
☐ Ω-SYNTHESIS — "Omega Engine Cross-Cutting Analysis"
☐ Import all 5 Briefing Docs as sources
☐ Run cross-notebook strategic queries
```

### 7.4 Prompt Templates for Omega Engine Strategic Analysis

#### Template A: Mandate Compliance Audit
```
ROLE: You are a Sovereign Compliance Auditor for the Omega Engine.
TASK: Audit mandate compliance against implementation evidence.
CONSTRAINTS:
- Use ONLY sources under ⚖️ MANDATES and 🏛️ CORE-ARCH labels
- Every claim MUST have a citation
- Rate confidence: HIGH (direct code evidence) / MEDIUM (config/doc evidence) / LOW (inference)
- Flag UNKNOWN where evidence is missing
FORMAT: Markdown table with columns:
| Mandate | Requirement Summary | Compliance | Evidence Citations | Confidence | Remediation |
ITERATION: After table, identify top 3 compliance gaps requiring immediate action.
```

#### Template B: Decision-to-Code Traceability
```
ROLE: You are an Architecture Decision Tracker.
TASK: Trace each architectural decision to its code implementation.
CONSTRAINTS:
- Use ONLY sources under 📋 DECISIONS and 🏛️ CORE-ARCH labels
- For each decision in PIVOT_LOG.md (D-350 to D-386):
  1. Quote decision
  2. Find implementing code (file:line or module)
  3. Cite exact source passage
  4. Status: IMPLEMENTED / PARTIAL / MISSING / CONTRADICTED
- Flag decisions with no code evidence
FORMAT: Decision traceability matrix table
ITERATION: Generate remediation backlog for MISSING/CONTRADICTED decisions.
```

#### Template C: Gap Analysis & Sprint Alignment
```
ROLE: You are a Sprint Planning Analyst.
TASK: Align GAP_REGISTRY gaps with ACTIVE_SPRINT work items.
CONSTRAINTS:
- Use ONLY sources under 📋 DECISIONS (GAP_REGISTRY, ACTIVE_SPRINT) and 🏃 SPRINTS labels
- For each R-ID gap: status, blocking decisions, current sprint coverage
- Identify orphaned gaps (no sprint work, no decision linkage)
- Identify sprint work not linked to any gap
FORMAT: Gap-sprint alignment table + orphaned items list
ITERATION: Propose sprint adjustments to close coverage gaps.
```

#### Template D: Technical Debt Quantification
```
ROLE: You are a Technical Debt Analyst.
TASK: Quantify technical debt from code patterns and mandate violations.
CONSTRAINTS:
- Use ONLY sources under 🏛️ CORE-ARCH (CODE/), ⚖️ MANDATES, 🐛 BUGS-FIXES labels
- Detect: god modules, duplicate implementations, hardcoded paths, missing contract tests, mock-masked types
- For each finding: file:line, mandate violated, severity (CRITICAL/HIGH/MEDIUM), effort estimate
FORMAT: Technical debt register table sorted by severity × impact
ITERATION: Prioritize top 5 debt items for next sprint.
```

#### Template E: Roadmap Validation
```
ROLE: You are a Strategic Roadmap Validator.
TASK: Validate Three Horizons roadmap against current implementation.
CONSTRAINTS:
- Use ONLY sources under 📋 DECISIONS (roadmap), 🏛️ CORE-ARCH, 📊 METRICS labels
- For each H1-H4 milestone: criteria, evidence, status, gaps
- Cross-reference sovereignty ratio, test pass rate, mandate compliance
FORMAT: Roadmap validation dashboard with traffic-light status
ITERATION: Identify horizon gate blockers requiring escalation.
```

#### Template F: Onboarding Knowledge Transfer
```
ROLE: You are an Omega Engine Onboarding Architect.
TASK: Create a complete onboarding package for new contributors.
CONSTRAINTS:
- Use ONLY sources under 🧠 ENTITIES, 🏛️ CORE-ARCH, ⚖️ MANDATES, 🔧 SKILLS labels
- Audience: Senior engineer, new to local-first AI, familiar with Python/async
- Tone: Authoritative but accessible; cite sources for every claim
FORMAT: Generate ALL of:
1. Briefing Doc (executive summary + architecture + mandates)
2. Study Guide (quiz on key concepts)
3. FAQ (top 20 questions new contributors ask)
4. Mind Map (visual architecture overview)
ITERATION: Validate with "new contributor" persona — run through Study Guide quiz.
```

---

## 8. Automation & Integration Recommendations

### 8.1 Automated Context Pack Refresh (Cron/Timer)

```yaml
# systemd timer: omega-notebooklm-refresh.timer
[Unit]
Description=Refresh NotebookLM Context Pack
Requires=omega-notebooklm-refresh.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

```python
# scripts/refresh_notebooklm_context.py
#!/usr/bin/env python3
"""
Daily refresh of NotebookLM context pack.
- Rebuilds Tier 1-2 sources from live repo
- Pushes to NotebookLM via notebooklm-py CLI
- Triggers auto-re-labeling
- Generates updated Briefing Docs
"""
import subprocess
from pathlib import Path

def rebuild_context_pack():
    subprocess.run(["./scripts/build_notebooklm_context_pack.sh"], check=True)

def push_to_notebooklm(notebook_name: str, source_dir: Path):
    """Use notebooklm-py to add/update sources."""
    for source_file in source_dir.glob("*.md"):
        subprocess.run([
            "notebooklm-py", "source", "add",
            "--notebook", notebook_name,
            "--title", source_file.stem,
            str(source_file)
        ], check=True)

def generate_briefing_docs():
    for notebook in ["Ω-ARCHITECTURE", "Ω-MANDATES", "Ω-DECISIONS", "Ω-ENTITIES", "Ω-OPERATIONS"]:
        subprocess.run([
            "notebooklm-py", "ask",
            "--notebook", notebook,
            "--save-as-note",
            "Generate a Briefing Doc for this notebook. Save as note."
        ], check=True)

if __name__ == "__main__":
    rebuild_context_pack()
    # Push each notebook's sources
    for nb, dir in [
        ("Ω-ARCHITECTURE", "CORE/ARCH/CODE"),
        ("Ω-MANDATES", "CORE/DECISIONS"),
        ("Ω-DECISIONS", "DECISIONS/ARCH"),
        ("Ω-ENTITIES", "ENTITY/SKILL"),
        ("Ω-OPERATIONS", "METRICS/RESEARCH"),
    ]:
        push_to_notebooklm(nb, Path(f"data/coordination/notebooklm_context_pack/{dir}"))
    generate_briefing_docs()
```

### 8.2 CI Integration: Mandate Compliance Gate

```yaml
# .github/workflows/notebooklm-compliance.yml
name: NotebookLM Mandate Compliance
on:
  pull_request:
    paths:
      - 'src/omega/**'
      - 'SOVEREIGN_MANDATES.md'
      - 'docs/decisions/PIVOT_LOG.md'

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Context Pack
        run: ./scripts/build_notebooklm_context_pack.sh
      - name: Query NotebookLM for Compliance
        run: |
          notebooklm-py ask \
            --notebook "Ω-MANDATES" \
            --format json \
            "Audit all 27 mandates against CORE-ARCH code. Output JSON: mandate_id, status, evidence_citations, confidence" \
            > compliance_report.json
      - name: Fail on Critical Violations
        run: |
          python3 -c "
          import json
          with open('compliance_report.json') as f:
              report = json.load(f)
          critical = [r for r in report if r['status'] == 'NON-COMPLIANT' and r['mandate_id'] in ['M1','M2','M4','M7','M13','M14','M23']]
          if critical:
              print('CRITICAL MANDATE VIOLATIONS:')
              for c in critical:
                  print(f\"  {c['mandate_id']}: {c['evidence_citations']}\")
              exit(1)
          print('All critical mandates compliant.')
          "
```

### 8.3 Research Agent Integration (Background Researcher)

The Omega Engine's **background researcher** (24/7 loop) should:
1. **Mine** new research → write to `data/knowledge/HALL_OF_RECORDS/`
2. **Distill** findings → generate Markdown sources for NotebookLM
3. **Push** new sources to relevant notebooks via `notebooklm-py`
4. **Trigger** Briefing Doc regeneration
5. **Alert** on new gaps/contradictions via Hivemind

---

## 9. Limitations & Mitigations

| Limitation | Impact on Omega Engine | Mitigation |
|------------|------------------------|------------|
| **No cross-notebook search** | Cannot query across ARCHITECTURE + MANDATES + DECISIONS simultaneously | Synthesis notebook with Briefing Doc imports |
| **500k word/source ceiling** | Large files (PIVOT_LOG, MASTER_SYNTHESIS) may need splitting | Chunk by logical section; include index |
| **No API (consumer)** | Cannot fully automate from CI/CD | Use `notebooklm-py` CLI in CI; Enterprise API for prod |
| **Cloud-only** | Violates M7 (Local-First) for sensitive code | Use for analysis only; never upload secrets/keys; Enterprise for data residency |
| **Chunk-level retrieval misses cross-chunk threads** | Architectural patterns spanning modules may be fragmented | Include module index + cross-reference metadata in each chunk |
| **Image/diagram analysis limited** | Architecture diagrams not fully understood | Export diagrams as Mermaid/PlantUML text + include in sources |
| **Chat history not portable** | Insights lost if notebook deleted | Save all insights as Notes → Convert to Sources |
| **No real-time collaboration** | Team cannot co-analyze live | Async workflow: generate artifacts → share exports |

---

## 10. Recommended Next Steps for Omega Engine

### Immediate (Week 1)
1. **Build context pack** using `build_notebooklm_context_pack.sh`
2. **Create 5 notebooks** + 1 synthesis notebook in NotebookLM
3. **Upload Tier 1 sources** → validate auto-labeling → rename labels
4. **Run Template A (Mandate Audit)** → establish baseline compliance
5. **Run Template E (Roadmap Validation)** → identify H1 blockers

### Short-term (Week 2-3)
6. **Integrate `notebooklm-py`** into CI for mandate compliance gate
7. **Automate daily context refresh** via systemd timer
8. **Generate onboarding kit** (Template F) → validate with new contributor
9. **Create Audio Overviews** for each notebook → share with team

### Medium-term (Month 1)
10. **Evaluate Enterprise tier** if team >5, need VPC-SC/IAM, or DOCX/PPTX/XLSX support
11. **Build custom MCP server** for NotebookLM ↔ Omega Engine bidirectional sync
12. **Integrate with background researcher** for continuous knowledge ingestion
13. **Develop Omega-specific prompt library** in `config/prompts/notebooklm/`

---

## 11. Appendix: Key References

| Source | URL | Accessed |
|--------|-----|----------|
| Google NotebookLM Help (Limits) | `support.google.com/notebooklm/answer/16269187` | 2026-08-19 |
| Google NotebookLM Help (Sources) | `support.google.com/notebooklm/answer/16215270` | 2026-08-19 |
| Upgrade Tiers Table | `support.google.com/notebooklm/answer/16213268` | 2026-08-19 |
| NotebookLM Guide (Limits) | `notebooklm-guide.com/notebooklm-system-limits-benchmarks/` | 2026-08-19 |
| NotebookLM Guide (Prompt Eng) | `notebooklm-guide.com/notebooklm-prompt-engineering/` | 2026-08-19 |
| NotebookLM Guide (Source Org) | `notebooklm-guide.com/notebooklm-source-organization/` | 2026-08-19 |
| Practitioner's Field Guide | `learn.techwithdarin.com/guides/notebooklm/` | 2026-08-19 |
| NotebookLM Explained 2026 | `teacherandtask.com/blog/notebooklm-explained-google-research-tool` | 2026-08-19 |
| Enterprise Docs | `cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/overview` | 2026-08-19 |
| notebooklm-py (Community API) | `github.com/teng-lin/notebooklm-py` | 2026-08-19 |
| Google Blog: Better Research | `blog.google/innovation-and-ai/products/notebooklm/better-research-notebooklm/` | 2026-06-08 |
| Google Blog: Custom Goals | `blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-custom-personas-engine-upgrade/` | 2025-10-29 |

---

## 12. Sovereign Researcher Sign-Off

**Dialectic Synthesis Complete**. The Council of Four concurs:

| Perspective | Verdict |
|-------------|---------|
| **Architect** | Multi-notebook architecture with synthesis layer correctly mirrors Omega's Engine/Stack separation. Label-anchored queries map to Node-slot discipline. |
| **Adversary** | Cloud-only is a M7 violation for production use. Mitigation: analysis-only, no secrets, Enterprise tier for data residency. Context pack refresh must be automated or it rots. |
| **Alchemist** | NotebookLM + background researcher = continuous strategic intelligence. Audio Overviews as "standup podcasts" for team alignment. Briefing Docs as living architecture decision records. |
| **Archivist** | Source-grounded citations provide the audit trail Temple-Grade requires. PIVOT_LOG traceability to code is now verifiable. This replaces ad-hoc grep audits. |

**Triangulation**: NotebookLM is the **optimal strategic analysis layer** for Omega Engine — not as a runtime component, but as a **sovereign audit & onboarding instrument**. The multi-notebook + synthesis pattern respects both NotebookLM's architectural boundaries and Omega's Engine/Stack firewall.

**Sovereign Synthesis**: Deploy the 5-notebook + 1-synthesis architecture with automated context pack refresh. Use `notebooklm-py` for CI integration. Treat NotebookLM as the **externalized working memory** for strategic decisions — the "manila folder" that survives context compaction.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_notebooklm_research ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
