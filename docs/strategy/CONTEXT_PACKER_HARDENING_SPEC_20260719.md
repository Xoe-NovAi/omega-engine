# 🔱 Omega Engine — Context Packer Hardening Specification
## Canonical v2.0 Specification (Cross-Validated: Research + Implementation + Best Practices)

**AP Token**: `AP-CONTEXT-PACKER-HARDENING-SPEC-v2.0.0`  
**Date**: 2026-07-19  
**Status**: **CANONICAL — Supersedes all prior scattered docs for hardening purposes**  
**Authority Stack**:  
1. `SOVEREIGN_MANDATES.md` (non-negotiable law)  
2. **This specification** (what to build, in what order, how to know done)  
3. `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` (7 gaps, 2026 research, 40+ sources)  
4. `.opencode/skills/context-packer/enhanced_packer.py` (v2 implementation, 885 lines)  
5. `.opencode/skills/context-packer/packer-config.yaml` (8 profiles, 12-slot limit)  

**Source Documents Preserved (Historical Trail — Do Not Delete)**:
| Document | Role | Location |
|---|---|---|
| Context Packer Knowledge Gaps | 7 gaps, 40+ sources, 2026 research | `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` |
| Enhanced Packer Implementation | v2 with 8 hardening enhancements | `.opencode/skills/context-packer/enhanced_packer.py` |
| Packer Config Profiles | 8 profiles, 12-slot limit | `.opencode/skills/context-packer/packer-config.yaml` |
| Decision Workspace Review Pack | Generated pack (12 files, 87K tokens) | `context_packs/decision-tools-review/` |
| Kali Oversight Pack | Generated pack (9 files, 75K tokens) | `context_packs/kali-oversight/` |

---

## 🎯 EXECUTIVE SUMMARY

The Context Packer transforms internal Omega Engine state into **sovereign, PII-masked, XML-structured artifacts** for external review (Web Claude, Grok CLI). This spec consolidates **7 researched knowledge gaps**, **8 implemented enhancements**, and **8 active profiles** into a single hardening roadmap.

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
| 8 | **Decision-Workspace-Review Pack** | 12 files (1 manifest + 11 bundles), 87K tokens, Ed25519 signed, valid XML | All | ✅ Generated |

### 📦 VERIFICATION RESULTS

| Pack | Files | Total Tokens | XML Valid | Ed25519 Signed | Within 12-Slot Limit |
|------|-------|--------------|-----------|----------------|---------------------|
| `decision-tools-review` | 12 (1 manifest + 11 bundles) | 87,206 | ✅ All 11 | ✅ | ✅ (at limit) |
| `kali-oversight` | 9 (1 manifest + 8 bundles) | 75,262 | ✅ All 8 | ✅ | ✅ (well under) |

### 🔀 BUNDLE ORDERING (Lost-in-the-Middle Mitigation)

**decision-tools-review** (critical at positions 1-3 and 11-12):
```
START:  decree, grounding_part1, grounding_part2, decisions
MIDDLE: implementation, research, general, mandates, session_log, engine_state
END:    exit_protocol, handoff
```

**kali-oversight** (critical at positions 1-3 and 8-9):
```
START:  fleet_part1, fleet_part2, fleet_part3
MIDDLE: mandates, roadmap, coordination_part1, coordination_part2
END:    heritage
```

---

## 🎯 7 KNOWLEDGE GAPS — RESEARCH FINDINGS (P0/P1)

### Gap 1: Token Optimization & Context Engineering (P0) ✅ RESOLVED
> **"Token optimization is a context-engineering problem, not a prompt-shortening problem."** — TokenOptimize.dev 2026

| Strategy | Savings | Effort | Packer Application |
|---|---|---|---|
| **Prompt Caching** (Anthropic `cache_control`) | 90% on cached prefix | Low | Cache manifest + static docs (mandates, engine state) as prefix |
| **Format Optimization** | 15-40% | Low | XML for Claude comprehension; YAML for token-critical bundles |
| **Model Routing** | 60-95% | Medium | Profile config: `target_model: claude-sonnet-4.6` |
| **Batch API** | 50% | Medium | Queue non-urgent packs |
| **Prompt Compression** (LLMLingua) | 5-20x | High | Horizon 1 for retrieval-heavy packs |

**2026 Model Pricing Context**:
| Model | Context | Input/Output | Cached Input | Notes |
|---|---|---|---|---|
| **Claude Opus 4.8** | 1M | $5/$25/MTok | $0.50/MTok | New tokenizer: +35% tokens for code |
| **Claude Sonnet 4.6** | 1M | $3/$15/MTok | $0.30/MTok | Best quality/cost for most tasks |
| **Claude Haiku 4.5** | 200K | $0.25/$1.25/MTok | $0.025/MTok | 12x cheaper than Sonnet |

**Packer Implications**: Target 87K tokens well within Sonnet 4.6 1M window. Cache manifest + static docs as prefix. Dynamic content (session logs, decisions) at suffix.

---

### Gap 2: Data Format Selection (P0) ✅ RESOLVED

| Format | Token Efficiency | Claude Comprehension | Best For |
|---|---|---|---|
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
|---|---|---|---|---|---|
| **Microsoft Presidio** | NER + anonymizer | ✅ ReversibleAnonymizer | In-memory mapping | ~50ms | MIT |
| **OPF (OpenAI Privacy Filter)** | `opf.tokenize()` | ✅ `opf.reversible.v1` schema | External vault | <50ms | Apache-2.0 |
| **Privalyse (pyveil)** | Semantic placeholders | ✅ Mapping returned | Local dict | <10ms | MIT |
| **CloakPipe** | Sidecar proxy | ✅ Encrypted vault | File/Redis | <5ms | MIT |
| **AegisGate** | Rust, <50ms | ✅ Deterministic tokens | Encrypted vault | <5ms | MIT |

**Token Format Standards**:

| Standard | Format | Example | Collision Resistance |
|---|---|---|---|
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
|---|---|---|
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
|---|---|---|
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
  target_model: "claude-sonnet-4.6"  # Quality tier
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
|---|---|---|
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

## 🔧 PROFILE REGISTRY (8 Active Profiles)

| Profile | Purpose | Max Slots | Themes | Status |
|---|---|---|---|---|
| `sovereign-audit` | Core Engine + Mandates audit | 12 | mandates, oracle_core, memory, providers, observability, mcp_hub, strategy | ✅ Hardened |
| `engineering-p3` | P3 Engineering Pillar context | 12 | core_logic, validation, docs | ✅ Working |
| `kali-oversight` | Grand Oversight — mandates, fleet, decisions | 12 | mandates, fleet, roadmap, coordination, heritage | ✅ Generated |
| `youtube-research-primer` | YouTube Research Module context | 12 | spec, implementation, tests, ingestion_queue, memory_integration | ✅ |
| `decision-tools-review` | **Implementation review** (NOT content decisions) | 12 | grounding, implementation, research, mandates, engine_state, handoff | ✅ Generated |
| `sprint-context` | Current sprint research + implementation | 12 | analysis, spec, implementation, mandates | ✅ |
| *(2 legacy profiles)* | — | — | — | Archived |

**Rule**: `max_slots: 12` = **HARD LIMIT** (1 below Claude Projects RAG threshold of 13). Reserve 1 slot for manifest.

---

## 🔗 SOURCE CITATIONS (Tier-Ordered)

### Tier 1: Official Documentation
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — 90% discount, `cache_control`
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

### Tier 3: Architectural Specifications
- [Sovereign Systems Specification](https://kenwalger.github.io/sovereign-system-spec/PATTERNS.html) — Sieve-and-Sign, Intent-Based Namespace, Context Compression, Hybrid Retrieval, Multi-Model Routing
- [Sovereign AI Stack 2026](https://www.topailearninghub.com/2026/05/sovereign-ai-stack-2026-why-i-left.html) — Local-first architecture

### Tier 4: Academic/ArXiv
- [arXiv:2511.13900](https://arxiv.org/abs/2511.13900) — GM-Extract, lost-in-the-middle mitigations
- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — CaMeL: Provable prompt injection defense
- [Liu et al. 2023](https://arxiv.org/abs/2307.03172) — Original lost-in-the-middle paper

---

## ✅ VALIDATION CHECKLIST FOR PACKER v2 (IMPLEMENTED)

| Requirement | Status | Evidence |
|---|---|---|
| XML format for Claude comprehension | ✅ | Profile uses XML bundles |
| ≤12 files to avoid RAG threshold | ✅ | 11 bundles + manifest = 12 (decision-workspace-review) |
| Critical content at start/end | ✅ | `_reorder_bundles_for_litm()` implemented |
| Full body XML escaping | ✅ | `_escape_bare_xml_chars()` implemented |
| PII masking (TOKENIZE mode) | ✅ | PIIMasker integrated |
| Reversible tokenization vault | ⚠️ | In-memory only; OPF schema vault pending (short-term) |
| Manifest as entry point | ✅ | `00_PROJECT_MANIFEST.md` |
| Injection pattern scanning | ✅ | 25 OWASP/Microsoft/Google patterns in `_scan_for_injection()` |
| Per-bundle token limits | ✅ | `MAX_BUNDLE_TOKENS=15000`, split + trim in `_enforce_token_limits()` |
| Cryptographic manifest signature | ✅ | Ed25519 signature in manifest footer |
| Target model tier in config | ⚠️ | Not in packer-config.yaml (short-term) |
| Cache control hints | ⚠️ | Not in manifest (short-term) |

---

## 📦 GENERATED PACKS (Ready for Review)

| Pack | Profile | Files | Tokens | XML Valid | Ed25519 Signed | Use Case |
|---|---|---|---|---|---|---|
| `context_packs/decision-tools-review/` | decision-tools-review | 12 | 87,206 | ✅ All 11 | ✅ | Grok CLI + Web Claude parallel review |
| `context_packs/kali-oversight/` | kali-oversight | 9 | 75,262 | ✅ All 8 | ✅ | Kali fleet oversight snapshot |

---

## 🎯 NEXT ACTIONS (Post-Compaction)

1. **Short-term (Next Sprint)**:
   - Implement reversible PII vault persistence (OPF schema)
   - Add `target_model` field to packer-config.yaml profiles
   - Add bundle-level XSD/RelaxNG schema validation
   - Add `cache_control` hints to manifest for prompt caching

2. **Medium-term (Horizon 1)**:
   - Hybrid retrieval index (manifest + bundle FTS5)
   - Context compression pipeline (LLMLingua integration)
   - Multi-profile packer (audit, review, handoff, archive)
   - Sovereign gateway integration (pre-flight namespace)

3. **Immediate**: Upload `context_packs/decision-tools-review/` to claude.ai Projects for Web Claude parallel review of Decision Tools implementation.

---

*⬡ OMEGA ⬡ CONTEXT-PACKER-HARDENING-SPEC ⬡ v2.0 ⬡ 2026-07-19*