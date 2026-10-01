# 🔱 Omega Engine — Context Packer v2 Implementation Manual
## Canonical Specification with Integrated Research, Cross-Validated Reviews & Platform Tuning

**AP Token**: `AP-CONTEXT-PACKER-IMPL-MANUAL-v2.0.0`  
**Date**: 2026-07-19  
**Status**: **CANONICAL — Supersedes all prior scattered docs for implementation purposes**  
**Authority Stack**:
1. `SOVEREIGN_MANDATES.md` (non-negotiable law)
2. **This manual** (what to build, in what order, how to know done)
3. `docs/strategy/CONTEXT_PACKER_HARDENING_SPEC_20260719.md` (base hardening spec)
4. `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` (7 gaps, 40+ sources)
5. `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` (4 platform profiles)
6. `context_packs/decision-tools-review/pack-results/DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V2_AFTER_GROK_REVIEW.md` (Web Claude V2)
7. `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` (Grok CLI Conditional GO)
8. `context_packs/decision-tools-review/pack-results/DUAL_REVIEW_RETROSPECTIVE_20260719.md` (process analysis)
9. `docs/strategy/DECISION_TOOLS_IMPLEMENTATION_SPEC_20260719.md` (consolidated spec)
10. `.opencode/skills/context-packer/enhanced_packer.py` (v2 implementation, 885 lines)
11. `.opencode/skills/context-packer/packer-config.yaml` (10 profiles, 12-slot limit)

---

## 🎯 EXECUTIVE SUMMARY

The Context Packer transforms internal Omega Engine state into **sovereign, PII-masked, XML-structured, cryptographically signed artifacts** for external review (Web Claude, Web Grok, Web Gemini, NotebookLM). This manual consolidates:

| Artifact | Status | Key Finding |
|----------|--------|-------------|
| **8 Hardening Enhancements** | ✅ Implemented | Ed25519 signing, injection scanner, token limits, bundle consolidation, LiTM reordering, PII masking, XML escaping, decision-tools-review pack |
| **7 Knowledge Gaps** | ✅ Researched | Token optimization, format selection, PII masking, XML escaping, Claude RAG threshold (13 files), LiTM mitigation, sovereign export patterns |
| **4 Platform Profiles** | ✅ Specified | Web Claude (12 files, XML), Web Grok (20 files, XML-MD hybrid), Web Gemini (30-100 files, Markdown), NotebookLM (50 sources, Markdown-sources) |
| **Dual Review Convergence** | ✅ Validated | Web Claude (curated pack + web search) + Grok CLI (native repo access) = same conclusions on all load-bearing decisions |
| **Implementation Spec** | ✅ Consolidated | T0+T1 = 9-11h honest; two-PR migration; slot-keyed not persona-keyed; no numeric BE math in T1 |

**Core Principle**: **Sieve-and-Sign** (Sovereign Systems Spec 2026) — Raw Engine State → Context Cleansing (PII mask, redact secrets) → Low-Entropy XML → Cryptographic Sign (Ed25519) → Forensic Receipt → Export Bundle.

---

## 📊 IMPLEMENTATION STATUS (v2.0 — 2026-07-19)

### ✅ COMPLETED THIS SPRINT (8 Enhancements)

| # | Enhancement | Implementation | Mandate | Verification |
|---|-------------|----------------|---------|--------------|
| 1 | **Ed25519 Manifest Signing** | `_sign_manifest()` generates keypair, signs manifest, appends signature + public key | M21, M23 | ✅ Both packs signed |
| 2 | **Injection Pattern Scanner** | 25 compiled regexes from OWASP LLM Top 10 2026 + Microsoft Spotlighting + Google research | M23 | ✅ Scans every file |
| 3 | **Per-Bundle Token Limits** | `MAX_BUNDLE_TOKENS=15000`, `MAX_TOTAL_TOKENS=150000`; auto-split + trim lowest-priority | M18 | ✅ Enforced |
| 4 | **Bundle Consolidation (≤12)** | `_consolidate_bundles()` enforces `max_slots-1`, merges lowest-priority into `general` | Gap 5 | ✅ 12/12 files |
| 5 | **Lost-in-the-Middle Reordering** | `_reorder_bundles_for_litm()` places critical bundles at start/end (U-shaped attention) | Gap 6 | ✅ Applied |
| 6 | **PII Masking (TOKENIZE)** | Integrated `PIIMasker` from `src/omega/oracle/pii_masker.py` with reversible placeholders | M8, M23 | ✅ Active |
| 7 | **Full XML Body Escaping** | `_escape_bare_xml_chars()` escapes all `<`, `>`, `&` in body content | M9, M23 | ✅ Valid XML |
| 8 | **Decision-Tools-Review Pack** | 12 files (1 manifest + 11 bundles), 87K tokens, Ed25519 signed, valid XML | All | ✅ Generated |

### 📦 VERIFICATION RESULTS

| Pack | Files | Total Tokens | XML Valid | Ed25519 Signed | Within 12-Slot Limit |
|------|-------|--------------|-----------|----------------|---------------------|
| `decision-tools-review` | 12 (1 manifest + 11 bundles) | 87,206 | ✅ All 11 | ✅ | ✅ (at limit) |
| `kali-oversight` | 9 (1 manifest + 8 bundles) | 75,262 | ✅ All 8 | ✅ | ✅ (well under) |

### 🔀 BUNDLE ORDERING (Lost-in-the-Middle Mitigation)

**decision-tools-review** (critical at positions 1-3 and 11-12):
```
START:  grounding_part1, grounding_part2, decisions, decree
MIDDLE: implementation_part1, implementation_part2, research, mandates, session_log, engine_state
END:    handoff, exit_protocol
```

**kali-oversight** (critical at positions 1-3 and 8-9):
```
START:  fleet_part1, fleet_part2, fleet_part3
MIDDLE: mandates, roadmap, coordination_part1, coordination_part2
END:    heritage
```

---

## 🎯 7 KNOWLEDGE GAPS — RESEARCH FINDINGS INTEGRATED

### Gap 1: Token Optimization & Context Engineering (P0) ✅ RESOLVED

> **"Token optimization is a context-engineering problem, not a prompt-shortening problem."** — TokenOptimize.dev 2026

| Strategy | Savings | Effort | Packer Application |
|----------|---------|--------|-------------------|
| **Prompt Caching** (Anthropic `cache_control`) | 90% on cached prefix | Low | Cache manifest + static docs (mandates, engine state) as prefix |
| **Format Optimization** | 15-40% | Low | XML for Claude comprehension; YAML for token-critical bundles |
| **Model Routing** | 60-95% | Medium | Profile config: `target_model: claude-sonnet-5` |
| **Batch API** | 50% | Medium | Queue non-urgent packs |
| **Prompt Compression** (LLMLingua) | 5-20x | High | Horizon 1 for retrieval-heavy packs |

**2026 Model Pricing Context (Updated for Web Claude + Antigravity SDK)**:

| Model | Context | Input/Output | Cached Input | Notes | Access |
|-------|---------|--------------|--------------|-------|--------|
| **Claude Opus 4.6** | 1M | $5/$25/MTok | $0.50/MTok | New tokenizer: +35% tokens for code | Antigravity SDK |
| **Claude Sonnet 5** | 1M | $3/$15/MTok | $0.30/MTok | Best quality/cost for most tasks | Web Claude (free) |
| **Claude Haiku 4.5** | 200K | $0.25/$1.25/MTok | $0.025/MTok | 12x cheaper than Sonnet | Web Claude (free) |
| **GPT-OSS-120B** | 128K | Local | N/A | Open weights, local only | Antigravity SDK |

**Packer Implications**: Target 87K tokens well within Sonnet 5 1M window. Cache manifest + static docs as prefix. Dynamic content (session logs, decisions) at suffix.

---

### Gap 2: Data Format Selection (P0) ✅ RESOLVED

| Format | Token Efficiency | Claude Comprehension | Best For |
|--------|------------------|---------------------|----------|
| **XML** | Baseline (1.0x) | ⭐⭐⭐⭐⭐ Native | **Claude Projects** — Anthropic explicitly recommends |
| **YAML** | ~0.85x (15% fewer) | ⭐⭐⭐⭐ Good | Token-constrained contexts |
| **Markdown** | ~0.85x (15% fewer) | ⭐⭐⭐⭐ Good | Human-readable + LLM-readable |
| **TOON** | ~0.60x (40% fewer) | ⭐⭐⭐ Emerging | High-volume tabular data |
| **JSON** | 1.0x (baseline) | ⭐⭐⭐ Good | Structured output, tool calls |

**Critical Findings**:
1. **Claude 4.x follows XML tags literally** — "XML tags are genuinely the best structuring method for Claude" (Thomas Wiegold 2026, Anthropic docs)
2. **JSON degrades reasoning by 10-15%** — "Forcing LLM to output JSON degrades reasoning" (Michael Hannecke 2025)
3. **YAML is strong default** — "YAML emerged as strongest format for 2/3 models tested" (ImprovingAgents 2025)
4. **Two-step approach** — Free reasoning → structured formatting (preserves accuracy)

**Packer Decision**:
- **Primary**: XML (Claude-native, best comprehension)
- **Manifest**: Markdown (human entry point)
- **Internal**: Consider YAML for token-critical bundles
- **Never**: Raw JSON for context injection

---

### Gap 3: PII Masking / Reversible Tokenization (P0) ✅ RESOLVED

**Architecture Pattern**: **Sieve-and-Sign** (Sovereign Systems Spec 2026)
```
Raw Payload → Context Cleansing (Sieve) → Low-Entropy State → Cryptographic Sign → Forensic Receipt → Sovereign Ledger
```

**Reversible Tokenization Options (2026)**:

| Tool | Approach | Reversibility | Vault | Latency | License |
|------|----------|---------------|-------|---------|---------|
| **Microsoft Presidio** | NER + anonymizer | ✅ ReversibleAnonymizer | In-memory mapping | ~50ms | MIT |
| **OPF (OpenAI Privacy Filter)** | `opf.tokenize()` | ✅ `opf.reversible.v1` schema | External vault | <50ms | Apache-2.0 |
| **Privalyse (pyveil)** | Semantic placeholders | ✅ Mapping returned | Local dict | <10ms | MIT |
| **CloakPipe** | Sidecar proxy | ✅ Encrypted vault | File/Redis | <5ms | MIT |
| **AegisGate** | Rust, <50ms | ✅ Deterministic tokens | Encrypted vault | <5ms | MIT |

**Token Format Standards**:

| Standard | Format | Example | Collision Resistance |
|----------|--------|---------|---------------------|
| **Presidio** | `<TYPE_HASH>` | `<PERSON_a8f3>` | Salted hash |
| **OPF** | `<TYPE_INDEX>` | `<private_person_1>` | Sequential per vault |
| **Privalyse** | `{Type_Hash}` | `{Name_a8f}` | Truncated hash |
| **NimbleSoft** | `[TYPE_xxxxxxxx]` | `[PERSON_3a7f1c08]` | Salted truncated |

**Compliance Notes (2026)**:
- **GDPR**: Pseudonymized data = still personal data (Recital 26); vault = same protection tier
- **EU AI Act Article 10**: Lineage requirement → vault must be auditable
- **DPDPA 2023 (India)**: Per-tenant CMK mandatory
- **Zero-Retention Contracts**: Only with Enterprise Anthropic/OpenAI

**Packer Implementation**:
```python
# Current: PIIMasker from src/omega/oracle/pii_masker.py
# Enhancement: Add reversible mode with vault persistence
# Mode: TOKENIZE (reversible) vs REDACT (irreversible)
# Vault: Encrypted JSON at data/coordination/pii_vaults/{session_id}.json
```

---

### Gap 4: XML Escaping & Prompt Injection Defense (P0) ✅ RESOLVED

**Threat Model**: Packer exports internal engine state to external LLMs (Web Claude). Malicious content in exported data could:
1. Inject prompts into the reviewing LLM
2. Exfiltrate the reviewer's system prompt
3. Trigger tool calls in agentic reviewers

**Defense-in-Depth (OWASP LLM Top 10 2026)**:

#### Layer 1: Structural Delimiting (Spotlighting)
```xml
<!-- Google/Microsoft "Spotlighting" technique -->
<CONTEXT_PACK_MANIFEST>
  <METADATA>
    <source>omega-engine</source>
    <session>2026-07-19</session>
  </METADATA>
  <USER_DATA_START>          <!-- Explicit delimiter -->
    <bundle name="decisions">
      <!-- Escaped content here -->
    </bundle>
  <USER_DATA_END>
</CONTEXT_PACK_MANIFEST>
```
**Google Finding**: "Explicit security reminders + structural delimiters reduced successful prompt injection by 67%"

#### Layer 2: Full Body XML Escaping (Current Implementation) ✅
```python
def _escape_bare_xml_chars(text: str) -> str:
    """Escape ALL < > & in body content — not just attribute values"""
    text = text.replace("&", "&")   # MUST BE FIRST
    text = text.replace("<", "<")
    text = text.replace(">", ">")
    return text
```
✅ **Already implemented** in `enhanced_packer.py:44`

#### Layer 3: Input Validation & Sanitization
- Reject content containing known injection patterns (`ignore previous`, `act as`, `DAN`, `system prompt`)
- Length limits per bundle (prevent context stuffing)
- Schema validation on pack generation

#### Layer 4: Output Monitoring (Reviewer Side)
- Parse reviewer response for leakage markers
- Validate no tool calls were triggered by packed content
- Audit trail: pack_id → reviewer_response → findings

#### Microsoft CaMeL Architecture (2025)
> **"Untrusted data retrieved by the LLM can never impact the program flow"**
- Separate control flow from data flow at architectural level
- Protective system layer around LLM
- Capability system prevents data exfiltration
- **Result**: 77% task success with **provable security guarantees**

**Packer Hardening Checklist**:
- ✅ Full body XML escaping (`&` `<` `>`)
- ✅ Manifest-first structure (entry point control)
- ✅ Explicit `USER_DATA_START/END` delimiters
- ✅ Injection pattern scanner on bundle content (25 patterns)
- ✅ Per-bundle token limits (prevent stuffing)
- ⬜ Output validation schema for reviewer responses

---

### Gap 5: Claude Projects RAG Behavior & File Limits (P0) ✅ RESOLVED

**Critical Discovery**: **File-Count Threshold, Not Token-Based**

> **GitHub Issue #25759 (anthropics/claude-code, Feb 2026)**: RAG activates at **13 files**, not at context window limit.

| File Count | Behavior | Warning |
|------------|----------|---------|
| 1-12 files | Direct context loading | None |
| **13+ files** | **RAG mode activates** | "To save space, Claude will look up specific information as needed" |
| Any count | Uses `project_knowledge_search` tool | Partial fragments, misses cross-file connections |

**Key Evidence**:
- **Threshold is file-count based**: 13 files at 73K tokens → RAG; 9 files at 90K tokens → direct load
- **Silent regression**: June 2024 launch loaded 63% capacity directly; Feb 2026 triggers at 2%
- **RAG quality issues**: "Hallucinates details that contradict actual file contents (wrong character names, invented locations, incorrect family relationships, fabricated data)"

**Official Anthropic Guidance (March 2026)**:
> "RAG for Projects expands capacity up to **10x** while maintaining quality. Automatic activation when approaching context limit."

**But reality**: Activates at 2% displayed capacity based on file count.

**File Organization Best Practices**:
1. **Keep ≤12 files per project** for direct context loading
2. **Aggregate related content** into fewer, larger files
3. **Clear, descriptive filenames** — "Claude searches by filename"
4. **Avoid**: `final_v3_really_final.md` — use `decisions_catalog_20260718.md`
5. **Delete stale content** — "Reorganize, don't just add"

**Packer Profile Design**:
```yaml
# packer-config.yaml
decision-tools-review:
  max_slots: 12              # HARD LIMIT: Stay under RAG threshold
  current: 12                # 11 bundles + 1 manifest = 12 files ✅
  bundle_strategy: aggregate # Combine related docs into single bundles
  naming_convention: "{theme}_{date}.xml"
```

**Current Pack**: **12 files** (11 bundles + manifest) — **AT LIMIT**
- Do not add more bundles without consolidating
- Consider merging `engine_state` + `mandates` + `session_log` → `core_context.xml`

---

### Gap 6: Lost-in-the-Middle Mitigation (P1) ✅ RESOLVED

**The Problem**:
> **U-shaped attention curve**: 80-100% accuracy at positions 1-10% and 90-100%; 20-50% at 40-60% (Liu et al. 2023, replicated 2025-2026)

**Mitigation Strategies (Ranked)**:

| Strategy | Effectiveness | Implementation |
|----------|---------------|----------------|
| **Critical content at extremes** | High | Place decisions, mandates, key findings at START and END |
| **Structured headers/numbering** | High | `<section id="D1">`, `<section id="D23">` — improves retrieval |
| **Progressive disclosure** | Medium | Summary → detail; avoid middle-stuffing |
| **Query-anchored placement** | Medium | Put answer-relevant content near query |
| **Chunking + RAG** | High | But loses cross-document connections |
| **Few-shot at END** | High | Examples just before query outperform mid-context |

**Packer Application** — Current Bundle Order (manifest.xml lists):
1. `grounding.xml` — Grounded Meditation + Jem Verification ⭐ **CRITICAL → START**
2. `decisions.xml` — 23 Decisions Catalog ⭐ **CRITICAL → START**
3. `decree.xml` — D-297 Architecture Inversion ⭐ **CRITICAL → START**
4. `exit_protocol.xml` — Sovereign Exit Protocol
5. `implementation.xml` — HMC Manual + Blueprint
6. `engine_state.xml` — OMEGA_ENGINE.md
7. `mandates.xml` — SOVEREIGN_MANDATES.md
8. `session_log.xml` — KALI_LIVE_FEED.md
9. `research.xml` — Grok CLI Research
10. `handoff.xml` — Kali→Grok CLI Handoff
11. `pivot_log.xml` — PIVOT_LOG.md

**Recommended Reordering for Reviewer**:
```
MANIFEST
├── grounding.xml          (START - framing)
├── decisions.xml          (START - primary artifact)
├── decree.xml             (START - architecture)
├── implementation.xml     (MIDDLE - supporting detail)
├── engine_state.xml       (MIDDLE - reference)
├── mandates.xml           (MIDDLE - reference)
├── research.xml           (MIDDLE - evidence)
├── session_log.xml        (MIDDLE - evidence)
├── handoff.xml            (END - action items)
├── pivot_log.xml          (END - history)
└── exit_protocol.xml      (END - framing)
```

**Key Principle**: The **review questions** and **decision catalog** must be at positions 1-2 and 11-12.

---

### Gap 7: Sovereign Export Architecture Patterns (P1) ✅ RESOLVED

From **Sovereign Systems Specification** (Ken Alger 2026):

#### 1. Sieve-and-Sign Pattern (State Integrity) ✅
```
Raw Engine State → Context Cleansing (PII mask, redact secrets) 
  → Low-Entropy XML → Cryptographic Sign (Ed25519) 
  → Forensic Receipt → Export Bundle
```
**Packer Status**: PII masking ✅, XML structuring ✅, Signing ✅ (Ed25519 manifest signature)

#### 2. Intent-Based Namespace Exposure (Pre-Flight Gating) ✅
> "Interceptively restrict an autonomous agent's available tool infrastructure to a deterministic, token-scoped namespace based on pre-evaluated session intent"

**Packer Application**: The packer profile (`decision-tools-review`) IS the intent declaration. It defines exactly what crosses the boundary — no more, no less.

#### 3. Context Compression Pattern (Efficiency) ✅
```
RAG Retrieval → Compression Layer → Condensed Prompt → Inference
```
**Packer Application**: Bundles ARE compression — 13 source files → 11 curated bundles (~87K tokens vs ~200K raw)

#### 4. Hybrid Retrieval Pattern (Structural Retrieval) ✅
> "Dual-channel retrieval combining semantic vector search with sparse keyword retrieval"

**Packer Application**: Manifest provides keyword index (bundle names, themes); bundles provide semantic content. Reviewer can search both.

#### 5. Multi-Model Routing (Agentic Reliability) ⬜
> "Lightweight classifier routes requests to most cost-effective capable model"

**Packer Application**: Profile could specify target model tier:
```yaml
decision-tools-review:
  target_model: "claude-sonnet-5"  # Quality tier
  fallback: "claude-haiku-4.5"       # Cost tier
  reasoning: "Complex synthesis requires Sonnet+"
```

---

## 🏗️ CONSOLIDATED ENHANCEMENT ROADMAP

### Immediate (This Sprint) — ✅ COMPLETE
| # | Enhancement | Effort | Mandate | Status |
|---|-------------|--------|---------|--------|
| 1 | Add manifest cryptographic signature (Ed25519) | 2h | M21, M23 | ✅ DONE |
| 2 | Injection pattern scanner on bundle content | 3h | M23 | ✅ DONE |
| 3 | Per-bundle token limit enforcement | 1h | M18 | ✅ DONE |
| 4 | Consolidate bundles to stay ≤12 files | 2h | Gap 5 | ✅ DONE |
| 5 | Reorder bundles for lost-in-the-middle mitigation | 1h | Gap 6 | ✅ DONE |

### Short-Term (Next Sprint)
| # | Enhancement | Effort | Mandate | Status |
|---|-------------|--------|---------|--------|
| 6 | Reversible PII vault persistence (OPF schema) | 4h | M8, M23 | 🔴 Open |
| 7 | Target model tier in profile config | 1h | M7, M18 | 🔴 Open |
| 8 | Bundle-level schema validation (XSD/RelaxNG) | 3h | M21 | 🔴 Open |
| 9 | Prompt caching hints in manifest (`cache_control`) | 2h | M18 | 🔴 Open |

### Medium-Term (Horizon 1)
| # | Enhancement | Effort | Mandate | Status |
|---|-------------|--------|---------|--------|
| 10 | Hybrid retrieval index (manifest + bundle FTS5) | 8h | Gap 7 | 🔴 Open |
| 11 | Context compression pipeline (LLMLingua integration) | 16h | M18 | 🔴 Open |
| 12 | Multi-profile packer (audit, review, handoff, archive) | 8h | M16 | 🔴 Open |
| 13 | Sovereign gateway integration (pre-flight namespace) | 16h | Gap 7 | 🔴 Open |

---

## 📋 MANDATE COMPLIANCE CHECKLIST (Verify Before Merge)

| Mandate | Check | Status |
|---------|-------|--------|
| **M1 AnyIO Absolute** | `grep -rn "asyncio" enhanced_packer.py` returns nothing; all blocking I/O wrapped in `anyio.to_thread.run_sync` | ✅ |
| **M2 Engine-Stack Firewall** | No WAD-specific proper nouns in packer code; profiles reference files, not entities | ✅ |
| **M7 Local-First** | Packer runs locally; no cloud deps for core function | ✅ |
| **M8 Zero Telemetry** | No analytics, no phone-home, no metrics sent externally | ✅ |
| **M9 Error Integrity** | Typed exceptions; no bare `except:`; PIIMasker import failure = hard stop (M23) | ✅ |
| **M13 Temple-Grade** | `make temple-grade` passes after packer changes | ✅ |
| **M14 Heritage Vetting** | Any id Software patterns tagged `[id-soft:]` | N/A |
| **M16 Modularization** | No hardcoded paths; `config_resolver` for all paths | ✅ |
| **M18 Token Efficiency** | Token limits enforced; format optimization (XML for Claude) | ✅ |
| **M21 Gate Integrity** | Contract tests for packer output types | 🔴 Open |
| **M22 Response Provenance** | Manifest includes `provider_name` from actual response | N/A (packer is producer) |
| **M23 Failure Integrity** | PIIMasker import failure = hard stop; injection scanner logs but continues; no silent fallbacks | ✅ |

---

## 🔧 PROFILE REGISTRY (10 Active Profiles)

| Profile | Purpose | Max Slots | Themes | Status |
|---------|---------|-----------|--------|--------|
| `sovereign-audit` | Core Engine + Mandates audit | 12 | mandates, oracle_core, memory, providers, observability, mcp_hub, strategy | ✅ Hardened |
| `engineering-p3` | P3 Engineering Pillar context | 12 | core_logic, validation, docs | ✅ Working |
| `kali-oversight` | Grand Oversight — mandates, fleet, decisions | 12 | mandates, fleet, roadmap, coordination, heritage | ✅ Generated |
| `youtube-research-primer` | YouTube Research Module context | 12 | spec, implementation, tests, ingestion_queue, memory_integration | ✅ |
| `decision-tools-review` | **Implementation review** (NOT content decisions) | 12 | grounding, implementation, research, mandates, engine_state, handoff | ✅ Generated |
| `sprint-context` | Current sprint research + implementation | 12 | analysis, spec, implementation, mandates | ✅ |
| `context-packer-hardening-review` | Packer v2 hardening review | 12 | spec, gaps, platform_tuning, implementation, config, mandates, engine_state, roadmap | ✅ Generated |
| `web-claude-sonnet5` | Optimized for Claude Sonnet 5 / Opus 4.8 | 12 | spec, gaps, implementation, config, mandates, engine_state, roadmap | ✅ Configured |
| `web-grok-4.3` | Optimized for Grok 4.3 via Web Grok | 20 | spec, gaps, platform_tuning, implementation, config, mandates, engine_state, roadmap | ✅ Configured |
| `web-gemini-3-pro` | Optimized for Gemini 3 Pro via Google AI Studio | 30 | spec, gaps, platform_tuning, implementation, config, mandates, engine_state, roadmap | ✅ Configured |

**Rule**: `max_slots: 12` = **HARD LIMIT** (1 below Claude Projects RAG threshold of 13). Reserve 1 slot for manifest.

---

## 🔗 SOURCE CITATIONS (Tier-Ordered)

### Tier 1: Official Documentation
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — 90% discount, `cache_control`
- [Anthropic XML Tags Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) — Native recommendation
- [Anthropic RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) — 10x capacity, auto-activation
- [OWASP LLM Prompt Injection Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — Defense-in-depth
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — ReversibleAnonymizer
- [xAI Prompt Caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching) — Automatic, `x-grok-conv-id`
- [Google AI Studio Context Windows](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Token budgets, truncation behavior

### Tier 2: 2026 Technical Articles
- [TokenOptimize.dev 2026 Guide](https://www.tokenoptimize.dev/guides/llm-token-optimization-strategies) — Context engineering thesis
- [Thomas Wiegold: Prompt Engineering 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026) — XML for Claude
- [ImprovingAgents: Nested Data Formats](https://www.improvingagents.com/blog/best-nested-data-format) — YAML > JSON
- [AppScale: PII Redaction Pipeline 2026](https://appscale.blog/en/blog/pii-redaction-pipeline-llm-presidio-ner-reversible-tokenisation-2026) — Presidio + FPE + vault
- [Ice-Ice-Bear: OPF Reversible Tokenization](https://ice-ice-bear.github.io/posts/2026-05-07-openai-privacy-filter-reversible-tokenization/) — OPF schema
- [GitHub Issue #25759](https://github.com/anthropics/claude-code/issues/25759) — RAG at 13 files
- [UnderstandingData: Lost in Middle](https://understandingdata.com/posts/lost-in-the-middle-mitigation) — U-curve mitigation
- [DevNote: Context Window Engineering 2026](https://devstarsj.github.io/ai/llm/2026/04/11/llm-context-window-engineering-long-context-strategies-2026/) — Hybrid RAG/long-context

### Tier 3: Architectural Specifications
- [Sovereign Systems Specification](https://kenwalger.github.io/sovereign-system-spec/PATTERNS.html) — Sieve-and-Sign, Intent-Based Namespace, Context Compression, Hybrid Retrieval, Multi-Model Routing
- [Sovereign AI Stack 2026](https://www.topailearninghub.com/2026/05/sovereign-ai-stack-2026-why-i-left.html) — Local-first architecture

### Tier 4: Academic/ArXiv
- [arXiv:2511.13900](https://arxiv.org/abs/2511.13900) — GM-Extract, lost-in-the-middle mitigations
- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — CaMeL: Provable prompt injection defense
- [Liu et al. 2023](https://arxiv.org/abs/2307.03172) — Original lost-in-the-middle paper
- [arXiv:2605.15343](https://arxiv.org/abs/2605.15343) — Belief Engine: 5-step loop, uptake/anchoring

---

## 📦 GENERATED PACKS (Ready for Review)

| Pack | Profile | Files | Tokens | XML Valid | Ed25519 Signed | Use Case |
|------|---------|-------|--------|-----------|----------------|----------|
| `context_packs/decision-tools-review/` | decision-tools-review | 12 | 87,206 | ✅ All 11 | ✅ | Grok CLI + Web Claude parallel review |
| `context_packs/kali-oversight/` | kali-oversight | 9 | 75,262 | ✅ All 8 | ✅ | Kali fleet oversight snapshot |
| `context_packs/context-packer-hardening-review/` | context-packer-hardening-review | 10 | 73,297 | ✅ All 9 | ✅ | Packer v2 hardening review |

---

## 🎯 NEXT ACTIONS (Post-Compaction)

### 1. Short-term (Next Sprint)
- Implement reversible PII vault persistence (OPF schema)
- Add `target_model` field to packer-config.yaml profiles
- Add bundle-level XSD/RelaxNG schema validation
- Add `cache_control` hints to manifest for prompt caching

### 2. Medium-term (Horizon 1)
- Hybrid retrieval index (manifest + bundle FTS5)
- Context compression pipeline (LLMLingua integration)
- Multi-profile packer (audit, review, handoff, archive)
- Sovereign gateway integration (pre-flight namespace)

### 3. Immediate
Upload `context_packs/decision-tools-review/` to claude.ai Projects for Web Claude parallel review of Decision Tools implementation.

---

## 🔬 PLATFORM-SPECIFIC TUNING — RESEARCH INTEGRATED

### Web Grok (xAI) — Real-Time Intelligence Platform

**Models (2026)**:
| Model | Context | Input/Output | Best For |
|-------|---------|--------------|----------|
| **Grok 4.3** | 1M | $1.25/$2.50/MTok | General reasoning, agentic workflows |
| **Grok 4.20 Multi-Agent** | 2M | $2.00/$4.00/MTok | Document analysis, complex orchestration |
| **Grok 4.1 Fast** | 2M | $0.20/$0.50/MTok | High-volume, latency-sensitive |
| **Grok Build (coding)** | 256K | $1.00/$2.00/MTok | Coding agent (70.8% SWE-Bench) |

**Unique Capabilities**:
- **Real-time X Search**: Integrated live search via X platform
- **Grok Skills**: Persistent instruction bundles (`/skillname` slash commands)
- **Connectors**: GitHub, Notion, Linear, Google Workspace, Microsoft 365, Vercel, Canva, S&P Global
- **Grok Build**: Terminal coding agent, 8 parallel sub-agents, MCP support

**Format Preference**: **XML + Markdown hybrid** — Grok follows XML tags but benefits from Markdown readability for human review

**Optimizations for Grok**:
- **Larger file count tolerance**: ~20 files before degradation (vs 13 for Claude)
- **Real-time data injection**: Include X search results as dynamic bundles
- **Skill-compatible output**: Generate `.skill` packs for Grok Skills system
- **Connector-aware**: Tag bundles with connector metadata (GitHub, Notion, etc.)
- **Cost optimization**: Use Grok 4.1 Fast for high-volume review tasks

**Prompt Caching**: Automatic on xAI API. Set `x-grok-conv-id` header to maximize cache hits. Cache reads at 0.25x input price. Works with streaming and tool calls.

**Grok Skills Template**:
```yaml
name: "context-packer-review"
description: "Review context packer implementation for security and correctness"
instructions: |
  You are a code review agent. When invoked:
  - Search for security vulnerabilities in packer code
  - Validate XML escaping, PII masking, token limits
  - Check mandate compliance (M1, M8, M9, M18, M21, M23)
  - Output: structured findings table + severity ratings
```

---

### Web Gemini (Google AI Studio) — Long-Context Specialist

**Models (2026)**:
| Model | Context | Pricing | Notes |
|-------|---------|---------|-------|
| **Gemini 3 Pro** | 1M-2M | $1.25/$2.50/MTok (<200K), $2.50/$5.00 (>200K) | Flagship |
| **Gemini 3.1 Pro** | 1M | Preview pricing | Ultra-long context |
| **Gemini 3 Flash** | 1M | $0.075/$0.30/MTok | Cost-optimized |

**Unique Capabilities**:
- **Google Workspace Integration**: Native Drive, Docs, Sheets, Gmail access
- **Grounding with Parallel Web Search**: Multiple search queries in parallel
- **Code Execution**: Built-in Python sandbox
- **Video Understanding**: Native video input (up to 2M tokens)
- **Gemini Gems**: Custom instructions (like Grok Skills / Claude Projects)

**Format Preference**: **Markdown + structured data** — Gemini excels with clear Markdown headings and structured sections

**Optimizations for Gemini**:
- **Larger effective context**: Can handle 20-50 files effectively
- **Source grounding**: Include source citations in bundles
- **Parallel search hints**: Structure bundles for parallel retrieval
- **Code execution ready**: Include runnable code snippets in bundles
- **Workspace integration**: Export as Google Docs/Drive compatible

**Key Research** (Google AI Studio docs 2026):
- Context window = prompt tokens + response tokens + system overhead
- Truncation happens when limit reached — summarize earlier content
- File uploads count toward context (text extracted from PDFs, etc.)
- **Best practice**: Explicit budget allocation across categories (system, retrieved, history, working, output)

---

### NotebookLM — Source-Grounded Research Platform

**Context Model**: **Source-based, not token-window-based**
- Upload sources (PDFs, Docs, URLs, YouTube, audio)
- System indexes sources, retrieves relevant passages per query
- **Effective context**: ~200K tokens of active retrieval
- **No traditional RAG threshold** — sources managed separately

**Unique Capabilities**:
- **Audio Overview**: Generate podcast-style summaries (2 hosts discussing sources)
- **Guided Analysis**: Structured prompts for comparison, synthesis, gap analysis
- **Source Citations**: Every claim linked to source document
- **Collaborative**: Shared notebooks with granular permissions

**Format Preference**: **Markdown + Source References** — NotebookLM works with uploaded sources, not raw context packs

**Optimizations for NotebookLM**:
- **Export as Sources**: Convert bundles to individual source documents
- **Structured Metadata**: Include source IDs, page numbers, section headers
- **Guided Prompts**: Include analysis frameworks (compare/contrast, gap analysis, synthesis)
- **Audio-Ready**: Structure for podcast generation (intro, sections, conclusion)

**NotebookLM Limits (2026)**:
| Plan | Price | Notebooks | Sources/Notebook | Chats/Day | Audio/Day |
|------|-------|-----------|------------------|-----------|-----------|
| Free | $0 | 100 | 50 | 50 | 3 |
| Plus (Google AI Plus) | $7.99/mo | 200 | 100 | 200 | - |
| Pro (Google AI Pro) | $19.99/mo | 500 | 300 | 500 | - |
| Ultra 20TB | $99.99/mo | 500 | 500 | 2,500 | 200 |
| Ultra 30TB | $200/mo | 500 | 600 | 5,000 | 500 |

**Per-Source Ceiling (All Plans)**: 500,000 words or 200 MB, no page limit. Copy-protected PDFs fail import.

**Audio Overview**: 10-20 minutes typical for 10-15 source notebook. Generation: 3-8 minutes. Free: 3/day, Ultra: 200/day. Customizable length: Shorter (~5 min), Default (~10 min), Longer (~20 min). New "Lecture" format testing at ~30 minutes (single host monologue).

---

## 🔧 IMPLEMENTATION REQUIREMENTS (From Platform Tuning Research)

### 1. Platform Detection & Profile Selection
```python
# enhanced_packer.py additions
class PlatformProfile(Enum):
    WEB_CLAUDE_SONNET5 = "web-claude-sonnet5"
    WEB_GROK_4_3 = "web-grok-4.3"
    WEB_GROK_4_1_FAST = "web-grok-4.1-fast"
    WEB_GEMINI_3_PRO = "web-gemini-3-pro"
    WEB_GEMINI_3_1_PRO = "web-gemini-3.1-pro"
    NOTEBOOKLM_RESEARCH = "notebooklm-research"

class PlatformConfig:
    def __init__(self, profile: PlatformProfile):
        self.profile = profile
        self.config = self._load_profile_config(profile)
    
    def get_format(self) -> str:
        return self.config.get("format", "xml")
    
    def get_max_slots(self) -> int:
        return self.config.get("max_slots", 12)
    
    def get_token_budget(self) -> dict:
        return self.config.get("token_budget", {})
    
    def supports_prompt_caching(self) -> bool:
        return self.config.get("prompt_caching", {}).get("enabled", False)
    
    def get_bundle_ordering_strategy(self) -> str:
        return self.config.get("bundle_ordering", "litm-u-shaped")
```

### 2. Format Adapters
```python
class FormatAdapter(ABC):
    @abstractmethod
    def render_bundle(self, content: str, metadata: dict) -> str:
        pass
    
    @abstractmethod
    def render_manifest(self, bundles: list, metadata: dict) -> str:
        pass

class XMLFormatAdapter(FormatAdapter):
    """Claude-native XML with spotlighting delimiters"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        escaped = self._escape_xml(content)
        attrs = " ".join(f'{k}="{v}"' for k, v in metadata.items())
        return f'<bundle {attrs}>\n{escaped}\n</bundle>'

class XMLMarkdownHybridAdapter(FormatAdapter):
    """Grok: XML structure with Markdown content"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        escaped = self._escape_xml(content)  # Still escape for safety
        return f'<bundle format="markdown" {attrs}>\n{escaped}\n</bundle>'

class MarkdownStructuredAdapter(FormatAdapter):
    """Gemini: Markdown with structured frontmatter"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        frontmatter = yaml.dump(metadata)
        return f"---\n{frontmatter}---\n\n{content}"

class MarkdownSourcesAdapter(FormatAdapter):
    """NotebookLM: Individual source files with citation metadata"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        return self._add_citation_markers(content, metadata)
```

### 3. Bundle Ordering Strategies
```python
class BundleOrderingStrategy(ABC):
    @abstractmethod
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        pass

class LITMUShapedStrategy(BundleOrderingStrategy):
    """Claude: Critical at start/end, reference in middle"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        critical = [b for b in bundles if b.priority == "critical"]
        middle = [b for b in bundles if b.priority == "reference"]
        action = [b for b in bundles if b.priority == "action"]
        return (sorted(critical, key=lambda b: -b.tokens) + 
                sorted(middle, key=lambda b: -b.tokens) + 
                sorted(action, key=lambda b: -b.tokens))

class PriorityWeightedStrategy(BundleOrderingStrategy):
    """Grok: Weight by priority, less strict position constraints"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        return sorted(bundles, key=lambda b: (-b.priority_weight, -b.tokens))

class RelevanceDescendingStrategy(BundleOrderingStrategy):
    """Gemini: Most relevant first (works with retrieval)"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        return sorted(bundles, key=lambda b: (-b.relevance_score, -b.tokens))

class HierarchicalStrategy(BundleOrderingStrategy):
    """Gemini 3.1 Pro: Hierarchical (overview → detail → appendix)"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        hierarchy = {"overview": 0, "detail": 1, "appendix": 2}
        return sorted(bundles, key=lambda b: (hierarchy.get(b.tier, 1), -b.tokens))

class ThematicStrategy(BundleOrderingStrategy):
    """NotebookLM: Group by theme, each theme self-contained"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        themes = defaultdict(list)
        for b in bundles:
            themes[b.theme].append(b)
        ordered = []
        for theme in sorted(themes.keys(), key=lambda t: -themes[t][0].importance):
            ordered.extend(sorted(themes[theme], key=lambda b: -b.relevance))
        return ordered
```

---

## 📋 UPDATED PACKER CONFIG (Complete)

See `.opencode/skills/context-packer/packer-config.yaml` for the full updated configuration with all 10 platform profiles.

---

## 🎯 PLATFORM-SPECIFIC SYSTEM PROMPTS

### Web Grok System Prompt Addendum
```markdown
## PLATFORM: Web Grok (Grok 4.3 / 4.1 Fast)

### Grok-Specific Directives

**Real-Time Intelligence**: You have access to live X search. Use it for:
- Current best practices (post-2024)
- Emerging vulnerabilities
- Active discussions on context engineering

**Grok Skills Compatibility**: Your review output should be structured for potential Skill conversion:
- Clear name/description for `/skillname` invocation
- Deterministic output format (tables, severity ratings)
- Tool usage specifications

**Connector Awareness**: Bundles may include connector metadata (GitHub, Notion, Linear, etc.). Factor this into your review:
- GitHub bundles: Check for CI/CD integration patterns
- Notion bundles: Verify knowledge base structure
- Linear bundles: Assess issue tracking integration

**Cost Consciousness**: If reviewing for Grok 4.1 Fast (economy tier), prioritize:
- Token efficiency recommendations
- Bundle consolidation opportunities
- Caching strategies
```

### Web Gemini System Prompt Addendum
```markdown
## PLATFORM: Web Gemini (Gemini 3 Pro / 3.1 Pro)

### Gemini-Specific Directives

**Source Grounding**: Every claim must be traceable to a source bundle. Use citation format:
- `[spec.xml §3.2]` for spec references
- `[impl_part1.xml:L312]` for implementation line references

**Parallel Search Optimization**: Structure your review to enable parallel verification:
- Group related checks (all security, all mandate compliance, all token limits)
- Each group can be verified independently

**Code Execution Ready**: Include runnable verification snippets:
```python
# Verification: Ed25519 signature check
import nacl.signing, nacl.encoding
vk = nacl.signing.VerifyKey(PUBLIC_KEY, encoder=nacl.encoding.HexEncoder)
vk.verify(b"MANIFEST_CONTENT", bytes.fromhex(SIGNATURE))
print("✅ Signature valid")
```

**Workspace Export**: Format findings for Google Docs/Sheets export:
- Tables as Markdown (auto-converts)
- Findings as structured rows
- Severity as filterable column
```

### NotebookLM System Prompt Addendum
```markdown
## PLATFORM: NotebookLM (Source-Grounded Research)

### NotebookLM-Specific Directives

**Source-Based Analysis**: You don't have a context window — you have SOURCES. Each bundle is a source document.

**Citation Format**: Use NotebookLM inline citations: `[^1]`, `[^2]` linking to source titles.

**Guided Analysis Frameworks**: Structure your review using these frameworks:
1. **Compare/Contrast**: "How does the packer's 4-layer injection defense (Spotlighting → XML escaping → Scanner → Output monitoring) compare to Google's CaMeL architecture for prompt injection defense?"
2. **Gap Analysis**: "What PII types are NOT covered by the current Presidio recognizers in `pii_masker.py`? Cross-reference with the 18 HIPAA identifiers and GDPR Article 9 special categories."
3. **Synthesis**: "Combine the 8 enhancements, 7 gap resolutions, and 10 platform profiles into a unified threat model. What attack vectors remain?"
4. **Action Items**: "Generate a prioritized remediation backlog with effort estimates, mapped to the short-term (4 items) and medium-term (4 items) roadmap."

**Output Format**: Structure for **Audio Overview** generation:
- **Intro** (30 sec): What is the Context Packer, why review it
- **Section 1** (2 min): Security architecture (Sieve-and-Sign)
- **Section 2** (2 min): Platform-specific tuning (4 platforms)
- **Section 3** (2 min): Top 5 findings with severity
- **Conclusion** (30 sec): Next steps, production readiness

**Collaborative Annotations**: Flag items for team review:
- `🔴 CRITICAL` — Blocks production
- `🟡 REVIEW` — Needs human judgment  
- `🟢 APPROVE` — Ready for production
- `💡 IDEA` — Enhancement opportunity
```

---

## 📋 UPDATED CHAT INITIATION PROMPTS

### Web Grok Chat Initiation
```markdown
# CHAT INITIATION PROMPT — Web Grok (Grok 4.3)

**Send this to Web Grok to begin the review**

---

## 🎯 Task: Review Context Packer v2 Hardening (Grok 4.3 Profile)

Hello Grok,

I need your expertise as an independent reviewer to assess the **Context Packer v2** — a sovereign context export tool for the Omega Engine that transforms internal engine state into **PII-masked, XML-structured, cryptographically signed artifacts** for external review.

### Platform Context
- **Target Model**: Grok 4.3 (1M context, $1.25/$2.50/MTok)
- **Profile**: `web-grok-4.3` — 20 bundles, XML-Markdown hybrid, real-time X search enabled
- **Grok Skills Export**: Enabled — structure findings for `/skillname` compatibility

### What Was Done This Sprint
**8 hardening enhancements** implemented in 885-line `enhanced_packer.py`:
1. **Ed25519 Manifest Signing** — Per-pack keypair, forensic receipt
2. **Injection Pattern Scanner** — 25 OWASP/Microsoft/Google patterns
3. **Per-Bundle Token Limits** — 15K/bundle, 150K total, auto-split + priority trim
4. **Bundle Consolidation (≤20)** — Priority-aware merge into `general`
5. **PII Masking (TOKENIZE)** — Presidio integration, reversible placeholders
6. **Full XML Body Escaping** — All `<` `>` `&` escaped in content
7. **Priority-Weighted Ordering** — Critical bundles weighted higher
8. **Decision-Tools-Review Pack v2** — 12 files, 87K tokens, signed

### What I Need From You
Your system prompt is set up in the project. Please read `CLAUDE_PROJECT_SYSTEM_PROMPT.md` first, then review the 8 XML bundles loaded into the project.

I need a thorough review covering these **8 sections**:

| # | Section | What to Evaluate |
|---|---------|------------------|
| 1 | **Enhancement Review** | Each of 8 enhancements — approve, approve-with-changes, or reject |
| 2 | **Gap Resolution Assessment** | Are the 7 knowledge gaps truly resolved or just claimed? |
| 3 | **Security Audit** | Layer-by-layer: Spotlighting, XML escaping, scanner coverage, output monitoring |
| 4 | **File Discipline** | 20-file tolerance (Grok) vs 13-file RAG threshold — any waste? |
| 5 | **Profile System Audit** | All 10 profiles correct? Overlaps? Missing includes? |
| 6 | **Mandate Compliance** | M1, M8, M9, M18, M21, M23 — verified against code? |
| 7 | **Roadmap Gap Analysis** | Priority ranking of 4 short-term + 4 medium-term items |
| 8 | **Overall Verdict** | Go / Go-with-conditions / Redesign — with single highest-priority fix |

### Key Documents in the Pack
| File | Read First? | Why |
|------|-------------|-----|
| `CLAUDE_PROJECT_SYSTEM_PROMPT.md` | **✅ YES — FIRST** | Your role, directives, multishot examples, output format |
| `spec.xml` | **✅ YES — SECOND** | Authoritative v2.0 spec (8 enhancements, 7 gaps, 10 profiles) |
| `implementation_part1.xml` | ✅ Next | Core `enhanced_packer.py` (885 lines) |
| `implementation_part2.xml` | ✅ Next | `pii_masker.py` + base `packer.py` |
| `gaps.xml` | ✅ Next | 7 knowledge gaps with 2026 research (40+ sources) |
| `config.xml` | ✅ | 10 platform profiles, 20-slot limits |
| `mandates.xml` | ✅ | 23 Sovereign Mandates (design constraints) |
| `roadmap.xml` | ✅ | Master execution roadmap |

### Verification Criteria
1. Every enhancement has specific line reference from `implementation_part1.xml`
2. Each gap has `✅ RESOLVED` / `🟡 PARTIALLY` / `🔴 OPEN` verdict
3. Security audit addresses all 4 defense layers from `spec.xml` §Gap 4
4. Mandate compliance cross-references actual code, not just spec claims
5. Overall verdict is decisive with actionable conditions

### Key Principle to Anchor Your Review
> **L3-Sieve-and-Sign** — Context export is a sovereignty boundary crossing. Every bundle must be cleansed (PII mask, redact secrets), structured (low-entropy XML), and signed (Ed25519) before export. The vault must be auditable for compliance (GDPR Recital 26, EU AI Act Art. 10).

---

**Begin when ready. I look forward to your review.**

*Model note: Use Grok 4.3 for this review. If token pressure exceeds 800K, switch to Grok 4.20 Multi-Agent (2M context). Real-time X search available for current best practices.*
```

### Web Gemini Chat Initiation
```markdown
# CHAT INITIATION PROMPT — Web Gemini (Gemini 3 Pro)

**Send this to Web Gemini / Google AI Studio to begin the review**

---

## 🎯 Task: Review Context Packer v2 Hardening (Gemini 3 Pro Profile)

Hello Gemini,

I need your expert review of the **Context Packer v2** — a sovereign context export tool that implements the **Sieve-and-Sign** pattern (cleanse → structure → sign) for safe external review of AI engine internals.

### Platform Context
- **Target Model**: Gemini 3 Pro (1M-2M context, parallel web search, code execution)
- **Profile**: `web-gemini-3-pro` — 30 bundles, Markdown-structured, source-grounded
- **Unique Capabilities**: Parallel search, code execution, Workspace export

### Pack Contents (30 Markdown-structured bundles)
Loaded into this project: `spec.md`, `gaps.md`, `impl_part1.md`, `impl_part2.md`, `config.md`, `mandates.md`, `roadmap.md`, `engine_state.md`, plus platform-specific bundles.

### Review Sections (8 Required)
Same 8 sections as Grok review, with these Gemini-specific angles:

1. **Source Grounding**: Every claim must cite source bundle + location
2. **Parallel Verification**: Structure findings for independent parallel checks
3. **Code Execution**: Include runnable verification snippets
4. **Workspace Export**: Format for Google Docs/Sheets export

### Key Principle
> **L3-Sieve-and-Sign** — Same sovereignty boundary. Your review must verify the pipeline: PII masking → XML/Markdown structuring → Ed25519 signing → forensic receipt.

---

**Begin by reading the system prompt addendum for Gemini, then work through the 8 review sections.**
```

### NotebookLM Chat Initiation
```markdown
# CHAT INITIATION PROMPT — NotebookLM

**Upload the 11 source documents to a new NotebookLM notebook, then send this prompt**

---

## 🎯 Task: Source-Grounded Review of Context Packer v2 Hardening

Hello. I've uploaded 11 source documents covering the Context Packer v2 hardening sprint. Please conduct a source-grounded review using NotebookLM's analysis frameworks.

### Sources Uploaded
1. `CONTEXT_PACKER_HARDENING_SPEC_20260719.md` — Authoritative spec
2. `R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` — 7 gaps, 40+ sources
3. `enhanced_packer.py` — 885-line implementation
4. `pii_masker.py` — PII masking implementation
5. `packer.py` — Base packer
6. `packer-config.yaml` — 10 platform profiles
7. `SOVEREIGN_MANDATES.md` — 23 constitutional laws
8. `SOVEREIGN_ARK_BLUEPRINT.md` — Master roadmap
9. `OMEGA_ENGINE.md` — Engine state SSOT
10. `CLAUDE_PROJECT_SYSTEM_PROMPT.md` — Reviewer instructions
11. `CHAT_INITIATION_PROMPT.md` — This prompt

### Analysis Frameworks (Use All Four)

#### 1. Compare/Contrast
> "How does the packer's 4-layer injection defense (Spotlighting → XML escaping → Scanner → Output monitoring) compare to Google's CaMeL architecture for prompt injection defense?"

#### 2. Gap Analysis
> "What PII types are NOT covered by the current Presidio recognizers in `pii_masker.py`? Cross-reference with the 18 HIPAA identifiers and GDPR Article 9 special categories."

#### 3. Synthesis
> "Combine the 8 enhancements, 7 gap resolutions, and 10 platform profiles into a unified threat model. What attack vectors remain?"

#### 4. Action Items
> "Generate a prioritized remediation backlog with effort estimates, mapped to the short-term (4 items) and medium-term (4 items) roadmap."

### Output Format
Structure for **Audio Overview** generation:
- **Intro** (30s): What is Context Packer, why review
- **Section 1** (2min): Security architecture (Sieve-and-Sign)
- **Section 2** (2min): Platform-specific tuning (4 platforms)
- **Section 3** (2min): Top 5 findings with severity
- **Conclusion** (30s): Next steps, production readiness

### Citation Style
Use NotebookLM inline citations: `[^1]`, `[^2]` linking to source titles.

### Collaborative Flags
Mark each finding:
- `🔴 CRITICAL` — Blocks production
- `🟡 REVIEW` — Needs human judgment
- `🟢 APPROVE` — Ready for production
- `💡 IDEA` — Enhancement opportunity

---

**Begin with the Compare/Contrast framework, then proceed through all four.**
```

---

## 🔬 RESEARCH GAPS REQUIRING FOLLOW-UP

| Gap | Priority | Research Needed |
|-----|----------|-----------------|
| **Grok 4.3 actual RAG threshold** | P1 | Empirical testing: at what file count does Grok degrade? |
| **Gemini 3.1 Pro 10M effective context** | P2 | Benchmark: usable tokens vs advertised |
| **NotebookLM source limit** | P1 | Max sources per notebook, max tokens per source |
| **Cross-platform bundle diffing** | P2 | Tool to compare platform-specific outputs |
| **Prompt caching on Grok/Gemini** | P1 | Does xAI/Google offer Anthropic-style `cache_control`? |
| **Grok Skills schema validation** | P2 | Formal schema for `.skill` export |
| **NotebookLM audio overview length limits** | P3 | Max duration, section count for podcast generation |

---

## 📚 SOURCE CITATIONS (Tier-Ordered)

### Tier 1: Official Documentation
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — 90% discount, `cache_control`
- [Anthropic XML Tags Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) — Native recommendation
- [Anthropic RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) — 10x capacity, auto-activation
- [OWASP LLM Prompt Injection Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — Defense-in-depth
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — ReversibleAnonymizer
- [xAI Prompt Caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching) — Automatic, `x-grok-conv-id`
- [Google AI Studio Context Windows](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Token budgets, truncation behavior
- [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) — OPF reversible tokenization schema

### Tier 2: 2026 Technical Articles
- [TokenOptimize.dev 2026 Guide](https://www.tokenoptimize.dev/guides/llm-token-optimization-strategies) — Context engineering thesis
- [Thomas Wiegold: Prompt Engineering 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026) — XML for Claude
- [ImprovingAgents: Nested Data Formats](https://www.improvingagents.com/blog/best-nested-data-format) — YAML > JSON
- [AppScale: PII Redaction Pipeline 2026](https://appscale.blog/en/blog/pii-redaction-pipeline-llm-presidio-ner-reversible-tokenisation-2026) — Presidio + FPE + vault
- [Ice-Ice-Bear: OPF Reversible Tokenization](https://ice-ice-bear.github.io/posts/2026-05-07-openai-privacy-filter-reversible-tokenization/) — OPF schema
- [GitHub Issue #25759](https://github.com/anthropics/claude-code/issues/25759) — RAG at 13 files
- [CloakPipe](https://github.com/rohansx/cloakpipe) — Rust privacy proxy, 3.2ms latency
- [Agentic Patterns: PII Tokenization](https://www.agentic-patterns.com/patterns/pii-tokenization) — MCP client layer integration

### Tier 3: Platform-Specific
- [Grok Build / Skills / Connectors](https://codersera.com/blog/xai-grok-build-skills-connectors-guide-2026/) — May 2026 launch details
- [Grok Agent Instructions](https://aitoolsrecap.com/Articles.aspx?article=grok-agent-instructions-examples-2026) — 8 Skill templates
- [NotebookLM Best Practices](https://www.datacamp.com/tutorial/notebooklm) — Source management, guided prompts
- [Gemini 3 Pro Prompting](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Structured prompting, code execution

### Tier 4: Academic/ArXiv
- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — CaMeL: Provable prompt injection defense
- [arXiv:2511.13900](https://arxiv.org/abs/2511.13900) — GM-Extract, lost-in-the-middle mitigations
- [Liu et al. 2023](https://arxiv.org/abs/2307.03172) — Original lost-in-the-middle paper
- [arXiv:2605.15343](https://arxiv.org/abs/2605.15343) — Belief Engine: 5-step loop, uptake/anchoring

---

## ✅ VALIDATION CHECKLIST

| Requirement | Status | Evidence |
|-------------|--------|----------|
| 4 platform profiles defined | ✅ | Web Claude, Web Grok, Web Gemini, NotebookLM |
| Format adapters specified | ✅ | XML, XML-Markdown, Markdown, Markdown-Sources |
| Bundle ordering strategies | ✅ | LITM-U, Priority, Relevance, Hierarchical, Thematic |
| Token budgets per platform | ✅ | 150K-2M total, 10K-50K per bundle |
| System prompt addenda | ✅ | Grok, Gemini, NotebookLM specific |
| Chat initiation prompts | ✅ | Platform-tuned for each |
| Multishot examples | ✅ | Platform-appropriate format |
| Research gaps identified | ✅ | 7 gaps with priority |
| Source citations tiered | ✅ | 4 tiers, 25+ sources |

---

## 🎯 L3 PRINCIPLES (for `proposed_lessons.yaml`, per Mandate 11)

**L3-Sieve-and-Sign** — Context export is a sovereignty boundary crossing. Every bundle must be cleansed (PII mask, redact secrets), structured (low-entropy XML), and signed (Ed25519) before export. The vault must be auditable for compliance (GDPR Recital 26, EU AI Act Art. 10).

**L3-Platform-Tuning-Is-Not-Optional** — One packer, multiple platform profiles. Each platform has distinct RAG thresholds, format preferences, and capability surfaces. Ignoring these differences wastes reviewer tokens and degrades review quality.

**L3-File-Count-Is-The-RAG-Trigger** — For Claude Projects, the 13-file threshold is a hard architectural constraint, not a suggestion. Bundle consolidation is mandatory, not optional.

**L3-Lost-in-the-Middle-Is-Real** — U-shaped attention is a measurable phenomenon. Critical content at positions 1-3 and 10-12 is not a preference — it's a requirement for review accuracy.

**L3-Parallel-Review-Convergence-Is-Signal** — When two independently-reasoning reviewers (Web Claude + Grok CLI) converge on a conclusion without access to each other's work, that convergence is stronger evidence than either review alone. Further scrutiny should move on.

---

*⬡ OMEGA ⬡ CONTEXT-PACKER-IMPL-MANUAL ⬡ v2.0 ⬡ 2026-07-19*