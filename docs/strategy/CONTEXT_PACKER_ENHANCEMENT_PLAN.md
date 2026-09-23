# �� 🔱 Omega Engine — Context Packer Enhancement Plan
## Canonical v1.0.0 — Recovery from Drift

**AP Token**: `AP-CONTEXT-PACKER-ENHANCEMENT-PLAN-v1.0.0`
��⬡ OMEGA �� ⬡ KALI �� ⬡ nemotron-3-ultra-free �� ⬡ opencode �� ⬡ trc_architecture �� ⬡ ACTIVE

**Date**: 2026-08-08
**Purpose**: Recovery plan for context packer systems enhancement after drift detection. Documents the gap between research specifications and current implementation, with prioritized recovery roadmap.

---

## �� 📋 Executive Summary

The Omega Engine Context Packer has undergone significant hardening research, but implementation has drifted from the canonical specifications. This plan documents:

1. **What's implemented**: Core hardening enhancements (8/8 complete)
2. **What's missing**: 
   - Entire platform-specific architecture (0/40 features from platform tuning research)
   - Short-term enhancements (0/4 from hardening spec)
   - Format selection critical fix (system prompt XML tags)
3. **Prioritized recovery roadmap**: Immediate fixes → platform architecture → short-term enhancements → advanced features

**Status**: Core hardening is solid. Platform-specific features are entirely missing despite being specified in `packer-config.yaml` and research documents.

---

## � ✅ WHAT'S FULLY IMPLEMENTED (Core Hardening)

| Enhancement | Implementation | Mandates |
|-------------|----------------|----------|
| **1. Ed25519 Manifest Signing** | `_sign_manifest()` lines 500-558 | M21, M23 |
| **2. Injection Pattern Scanner** | 25 regexes + `_scan_for_injection()` | M23 |
| **3. Per-Bundle Token Limits** | `MAX_BUNDLE_TOKENS=15000`, `_enforce_token_limits()` | M18 |
| **4. Bundle Consolidation (≤12)** | `_consolidate_bundles()` | Gap 5 |
| **5. Lost-in-the-Middle Reordering** | `_reorder_bundles_for_litm()` | Gap 6 |
| **6. PII Masking (TOKENIZE)** | Integrated `PIIMasker` | M8, M23 |
| **7. Full XML Body Escaping** | `_escape_bare_xml_chars()` | M9, M23 |
| **8. Decision-Workspace-Review Pack** | 12 files, 87K tokens, signed | All |

**Verification**: `make doc-llm-validate` � ✅ and `make temple-grade` � ✅ (M1, M2, M7, M8, M9, M13, M16, M18, M21, M23 pass)

---

## �� 🔴 WHAT'S MISSING: Platform-Specific Architecture (0/40 Features)

**Critical Finding**: The **entire platform-specific system** from `R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` is **NOT IMPLEMENTED**. The `packer-config.yaml` contains 10 complete profiles with platform-specific fields, but `enhanced_packer.py` ignores them entirely.

### 1. Platform Detection & Profile Selection (Missing)
```python
# Specified in platform tuning research §2.1 - NOT IMPLEMENTED
class PlatformProfile(Enum):
    WEB_CLAUDE_SONNET5 = "web-claude-sonnet5"
    WEB_GROK_4_3 = "web-grok-4.3"
    WEB_GROK_4_1_FAST = "web-grok-4.1-fast"
    WEB_GEMINI_3_PRO = "web-gemini-3-pro"
    WEB_GEMINI_3_1_PRO = "web-gemini-3.1-pro"
    NOTEBOOKLM_RESEARCH = "notebooklm-research"

class PlatformConfig:
    def get_format(self) -> str: ...
    def get_max_slots(self) -> int: ...
    def get_token_budget(self) -> dict: ...
    def supports_prompt_caching(self) -> bool: ...
    def get_bundle_ordering_strategy(self) -> str: ...
```

### 2. Format Adapters (Missing - Critical for Multi-Platform)
```python
# Specified in platform tuning research §2.2 - NOT IMPLEMENTED
class FormatAdapter(ABC):
    @abstractmethod
    def render_bundle(self, content: str, metadata: dict) -> str: ...
    @abstractmethod
    def render_manifest(self, bundles: list, metadata: dict) -> str: ...

class XMLFormatAdapter(FormatAdapter):           # Claude - XML native
class XMLMarkdownHybridAdapter(FormatAdapter):   # Grok - XML + Markdown
class MarkdownStructuredAdapter(FormatAdapter):  # Gemini - Markdown + frontmatter
class MarkdownSourcesAdapter(FormatAdapter):     # NotebookLM - Source files with citations
```

### 3. Bundle Ordering Strategies (Missing)
```python
# Specified in platform tuning research §2.3 - NOT IMPLEMENTED
class LITMUShapedStrategy(BundleOrderingStrategy):      # Claude: critical at start/end
class PriorityWeightedStrategy(BundleOrderingStrategy): # Grok: weight by priority
class RelevanceDescendingStrategy(BundleOrderingStrategy): # Gemini: most relevant first
class HierarchicalStrategy(BundleOrderingStrategy):     # Gemini 3.1 Pro: overview→detail→appendix
class ThematicStrategy(BundleOrderingStrategy):         # NotebookLM: group by theme
```

### 4. Platform-Specific Config Fields (In Config But Ignored)
The `packer-config.yaml` has these fields for each profile, but `enhanced_packer.py` **only uses**: `max_slots`, `include`, `exclude`, `themes`, `description`

| Profile Field | Used? | Platform |
|---------------|-------|----------|
| `target_platform` | �� ❌ | All |
| `target_model` | �� ❌ | All |
| `format` | �� ❌ | All |
| `bundle_ordering` | �� ❌ | All |
| `prompt_caching.enabled` | �� ❌ | Claude |
| `prompt_caching.cache_prefix` | �� ❌ | Claude |
| `token_budget` | �� ❌ | All |
| `multishot_examples` | �� ❌ | Claude |
| `xml_delimiters` | �� ❌ | Claude |
| `real_time_injection` | �� ❌ | Grok |
| `grok_skills_export` | �� ❌ | Grok |
| `connector_metadata` | �� ❌ | Grok |
| `cost_tier` | �� ❌ | Grok |
| `source_grounding` | �� ❌ | Gemini |
| `parallel_search_hints` | �� ❌ | Gemini |
| `code_execution_ready` | �� ❌ | Gemini |
| `workspace_export` | �� ❌ | Gemini |
| `source_export` | �� ❌ | NotebookLM |
| `audio_overview_ready` | �� ❌ | NotebookLM |
| `guided_prompts` | �� ❌ | NotebookLM |
| `citation_format` | �� ❌ | NotebookLM |

### 5. Platform-Specific System Prompts & Chat Initiation (Missing)
- Grok system prompt addendum (real-time X search, Skills compatibility, connector awareness)
- Gemini system prompt addendum (source grounding, parallel search, code execution, workspace export)
- NotebookLM system prompt addendum (source-based analysis, guided frameworks, audio overview)
- Platform-tuned chat initiation prompts for each platform

---

## �� 🟡 WHAT'S MISSING: Short-Term Enhancements (0/4)

| # | Enhancement | Effort | Mandates | Status |
|---|-------------|--------|----------|--------|
| 6 | **Reversible PII Vault Persistence (OPF schema)** | 4h | M8, M23 | �� 🔴 NOT IMPLEMENTED |
| 7 | **Target model tier in profile config** | 1h | M7, M18 | �� 🔴 NOT IMPLEMENTED |
| 8 | **Bundle-level schema validation (XSD/RelaxNG)** | 3h | M21 | �� 🔴 NOT IMPLEMENTED |
| 9 | **Prompt caching hints in manifest (`cache_control`)** | 2h | M18 | �� 🔴 NOT IMPLEMENTED |

**Current PII Vault Status**: In-memory only (per validation checklist: "In-memory only; OPF schema vault pending (short-term)")

---

## �� 🔵 FORMAT SELECTION RESEARCH: Critical Fix Needed

Per `R_CONTEXT_PACK_FORMAT_MD_VS_XML_20260808.md`:

| Finding | Status | Action Required |
|---------|--------|-----------------|
| **Primary: XML for Claude** | � ✅ | Implemented - bundles are `.xml` with `<file>` wrappers |
| **Manifest: Markdown** | � ✅ | `00_PROJECT_MANIFEST.md` is Markdown |
| **Internal: YAML for token-critical** | �� ⚠��️ | Not implemented - all bundles are XML |
| **Never: Raw JSON** | � ✅ | No JSON output |
| **System Prompt: XML tags** | �� ❌ | **CRITICAL**: `CLAUDE_PROJECT_SYSTEM_PROMPT.md` uses markdown headers (`## ROLE`, `## CONTEXT`) instead of XML tags (`<role>`, `<context>`) |

**Per format research**: The system prompt is pasted into Custom Instructions (NOT uploaded), so it **must use XML tags** per Anthropic guidance and the ClaSSIC template.

---

## �� 🛡��️ MANDATE COMPLIANCE GAPS

| Mandate | Requirement | Current Status | Gap |
|---------|-------------|----------------|-----|
| **M7** | Local-first routing | `target_model` in config but not used | �� 🔴 |
| **M8** | PII vault persistence | In-memory only | �� 🔴 |
| **M16** | Profile config modularization | Platform fields ignored | �� 🔴 |
| **M18** | Prompt caching, token budgets | Config has budgets but not enforced | �� 🔴 |
| **M21** | Schema validation | Not implemented | �� 🔴 |
| **M23** | PII masking hard stop | � ✅ Implemented | � ✅ |

---

## �� 📋 PRIORITIZED RECOVERY ROADMAP

### �� 🚨 IMMEDIATE (This Session) - Critical Fixes

| # | Task | Effort | Why |
|---|------|--------|-----|
| 1 | **Fix system prompt format** - Convert all `CLAUDE_PROJECT_SYSTEM_PROMPT.md` files to XML tags | 30 min | Required for Claude Projects per format research |
| 2 | **Add `target_model` to profile config usage** | 1h | Enables model routing (M7, M18) |
| 3 | **Add prompt caching hints to manifest** | 2h | 90% cost reduction on cached prefix (M18) |

### �� 🔴 HIGH PRIORITY (Next Sprint) - Platform Architecture

| # | Task | Effort | Why |
|---|------|--------|-----|
| 4 | **Implement PlatformProfile enum & PlatformConfig** | 4h | Foundation for all platform features |
| 5 | **Implement FormatAdapter hierarchy** | 8h | Required for Grok/Gemini/NotebookLM support |
| 6 | **Implement BundleOrderingStrategy hierarchy** | 4h | Platform-appropriate ordering |
| 7 | **Wire profile config fields to packer logic** | 4h | Use `format`, `bundle_ordering`, `token_budget`, etc. |
| 8 | **Reversible PII vault persistence (OPF schema)** | 4h | M8/M23 compliance - currently in-memory only |

### �� 🟡 MEDIUM PRIORITY (Horizon 1) - Platform Polish

| # | Task | Effort | Why |
|---|------|--------|-----|
| 9 | **Bundle-level schema validation (XSD/RelaxNG)** | 3h | M21 Gate Integrity |
| 10 | **Platform-specific system prompts & chat initiation** | 4h | Optimal reviewer experience per platform |
| 11 | **Grok real-time injection & Skills export** | 8h | Grok-specific value add |
| 12 | **Gemini source grounding & code execution bundles** | 6h | Gemini-specific value add |
| 13 | **NotebookLM source export & audio overview** | 6h | NotebookLM-specific value add |

### �� 🟢 LONG-TERM (Horizon 1+) - Advanced Features

| # | Task | Effort | Why |
|---|------|--------|-----|
| 14 | **Hybrid retrieval index (FTS5)** | 8h | Gap 7 - Hybrid Retrieval Pattern |
| 15 | **Context compression pipeline (LLMLingua)** | 16h | M18 - Token efficiency |
| 16 | **Multi-profile packer workflow** | 8h | M16 - Modularization |
| 17 | **Sovereign gateway integration** | 16h | Gap 7 - Intent-Based Namespace |

---

## �� 📁 FILES REQUIRING CHANGES

| File | Changes Needed |
|------|----------------|
| `.opencode/skills/context-packer/enhanced_packer.py` | Major: PlatformProfile, PlatformConfig, FormatAdapter, BundleOrderingStrategy, wire config fields |
| `.opencode/skills/context-packer/packer-config.yaml` | Minor: Ensure all profiles have complete platform fields |
| `context_packs/*/CLAUDE_PROJECT_SYSTEM_PROMPT.md` | **Critical**: Convert markdown headers to XML tags |
| `.opencode/skills/context-packer/SKILL.md` | Update documentation for new platform features |
| `tests/` | Add contract tests for platform-specific outputs |

---

## �� 📊 VERIFICATION CHECKLIST FOR RECOVERY

After implementing each priority level, verify:

### Immediate Fixes
- [ ] System prompt files use XML tags (`<role>`, `<context>`, etc.)
- [ ] Packer reads and uses `target_model` from profiles
- [ ] Manifest includes `cache_control` hints for prompt caching

### High Priority (Platform Architecture)
- [ ] PlatformProfile enum and PlatformConfig class implemented
- [ ] FormatAdapter hierarchy renders correct format per platform
- [ ] BundleOrderingStrategy hierarchy applies correct ordering
- [ ] All profile config fields are used (`format`, `bundle_ordering`, `token_budget`, `prompt_caching`, etc.)
- [ ] Reversible PII vault persistence with OPF schema implemented

### Medium Priority
- [ ] Bundle-level schema validation rejects invalid content
- [ ] Platform-specific system prompts match research specifications
- [ ] Grok real-time injection and Skills export functional
- [ ] Gemini source grounding and code execution bundles working
- [ ] NotebookLM source export and audio overview ready

---

## �� 🎯 Recovery Principle

> **The context packer must be a platform-agnostic engine** that uses profile configuration to generate platform-tuned outputs. The current implementation ignores the rich platform specification in `packer-config.yaml` and research documents, creating drift between intention and execution.

This plan recovers the canonical architecture by implementing the platform-specific features that were researched, specified in config, but never coded.

---

*��⬡ OMEGA �� ⬡ CONTEXT-PACKER-ENHANCEMENT-PLAN �� ⬡ v1.0 �� ⬡ 2026-08-08*