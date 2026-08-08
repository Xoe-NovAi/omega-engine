# 🔱 Context Packer Skill

The **Context Packer** is a sovereign tool designed to optimize codebase ingestion for high-context LLM platforms
  (Web Claude, Web Grok, Web Gemini, NotebookLM) by consolidating sprawling files into a limited number of
  high-density "Context Packs".

## 🎯 Purpose
Maximize signal-to-noise ratio and adhere to platform file limits while preserving architectural mapping,
  file provenance, PII protection, and cryptographic integrity.

## 🛠️ Usage
The packer is driven by `packer-config.yaml`. You can define multiple "Profiles" based on the task at hand.
Each profile may carry a **platform-specific tuning block** (`target_platform`, `target_model`, `format`,
`bundle_ordering`, `prompt_caching`, `token_budget`, etc.).

### Execution
Run the packer via the CLI (canonical v2 implementation):
```bash
python .opencode/skills/context-packer/packer.py <profile_name>
```

### Configuration (`packer-config.yaml`)
Define profiles with:
- `include`: Glob patterns for files to capture.
- `exclude`: Glob patterns for noise reduction.
- `themes`: Mapping of patterns to themed bundles (e.g., `core_logic`, `docs`).
- `max_slots`: The hard limit for output files (default: 12).
- **Platform tuning** (optional): `target_platform`, `target_model`, `format`, `bundle_ordering`,
  `prompt_caching`, `token_budget`, `multishot_examples`, `xml_delimiters`, `source_grounding`,
  `parallel_search_hints`, `code_execution_ready`, `workspace_export`, `real_time_injection`,
  `grok_skills_export`, `connector_metadata`, `cost_tier`, `source_export`, `audio_overview_ready`,
  `guided_prompts`, `citation_format`.

### Platform Profiles & Formats
| Platform | Format | Bundle Ordering | Extension |
|----------|--------|-----------------|-----------|
| Web Claude (Sonnet 5) | `xml` | `litm-u-shaped` | `.xml` |
| Web Grok (4.3 / 4.1 Fast) | `xml-markdown-hybrid` | `priority-weighted` | `.md` |
| Web Gemini (3 Pro / 3.1 Pro) | `markdown-structured` | `relevance-descending` / `hierarchical` | `.md` |
| NotebookLM | `markdown-sources` | `thematic` | `.md` |

Format adapters and ordering strategies live in `platform_adapters.py` (`FormatAdapter` hierarchy +
`BundleOrderingStrategy` hierarchy). Unknown format/strategy raises (M21) — never silently falls back.

## 🛡️ Sovereign Mandates Compliance
- **M1 (AnyIO Absolute)**: Fully AnyIO-native. No `asyncio` used.
- **M7 (Local-First)**: PII masking is local-only; no telemetry.
- **M8 (Zero Telemetry)**: PII masked before external upload; reversible vault stored locally.
- **M12 (Queue Integrity)**: Atomic writes (`.tmp` → final) for all output packs.
- **M18 (Token Efficiency)**: Per-bundle token limits, platform token budgets.
- **M21 (Gate Integrity)**: Contract tests validate output types.
- **M23 (Failure Integrity)**: Missing PIIMasker → hard stop (never emit unmasked pack).
- **Provenance**: Every bundled file is prepended with a metadata header containing `FILE`, `SIZE`, `LANG`,
  `SHA256`, and `PURPOSE`.
- **Integrity**: Manifest signed with Ed25519; reversible PII vault persisted (OPF schema).

## ⚙️ Pipeline
1. **Selection**: Filters files based on include/exclude patterns.
2. **Consolidation**: Groups files into themed bundles.
3. **Pruning**: Collapses whitespace; merges low-priority themes if `max_slots` is exceeded.
4. **Token enforcement**: Splits oversized bundles; trims to total budget.
5. **Ordering**: Applies platform-specific bundle ordering strategy (LITM-U, priority, relevance, etc.).
6. **Packaging**: Renders bundles via the platform format adapter; writes `00_PROJECT_MANIFEST.md`.
7. **PII masking**: Detects + tokenizes PII; persists reversible vault to `data/coordination/pii_vaults/`.
8. **Signing**: Signs manifest with Ed25519 for integrity verification.

## 📄 System Prompt Format
Per `docs/research/R_CONTEXT_PACK_FORMAT_MD_VS_XML_20260808.md`, the **system prompt** (pasted into the
Custom Instructions box, NOT uploaded) must use **XML tags** (`<role> <context> <constraints> <rules>
<project_files> <output_format>`), not markdown headers. Use the template at
`templates/SYSTEM_PROMPT_XML_TEMPLATE.md`. Knowledge/reference files stay Markdown (token-efficient,
RAG-searchable).