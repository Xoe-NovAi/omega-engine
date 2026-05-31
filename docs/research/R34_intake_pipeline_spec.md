# 🔱 Omega Engine — Modern Intake Pipeline (The Sentinel)
**AP Token**: `AP-RESEARCH-R34-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ MVE-PHASE

## Purpose
To replace legacy, fragile scrapers with a robust, sovereign "Intake Pipeline" (codenamed **The Sentinel**). The goal is to transform unstructured web and document data into high-fidelity "Gnosis Packs" that are ready for holographic indexing and entity consumption.

## Scope
This specification defines the four stages of the pipeline:
1. **Sovereign Crawling** (The Net)
2. **High-Fidelity Conversion** (The Scribe)
3. **Gnostic Curation** (The Filter)
4. **Vector Indexing** (The Anchor)

## Specification: The Pipeline Flow

### 1. Sovereign Crawling (via Crawl4AI)
The engine will use `Crawl4AI` as the primary web extraction tool.
- **Adaptive Crawling**: Use "Information Foraging" algorithms to determine when a page has sufficient information to answer a query, preventing unnecessary tokens.
- **LLM-Friendly Markdown**: Extract content directly into a clean markdown format, removing boilerplate (headers, footers, ads) before it ever reaches the LLM.
- **Session Management**: Use `AsyncWebCrawler` for parallel, high-velocity data gathering.

### 2. High-Fidelity Conversion (via Marker)
For non-HTML documents (PDFs, DOCX, Images), the engine will use `Marker`.
- **Structural Preservation**: Use Marker to convert PDFs to markdown while preserving complex tables, inline LaTeX equations, and multi-column layouts.
- **Sovereign-Lite Path**: Run Marker on the CPU (Ryzen 5700U) using the default CPU-optimized configuration.
- **Hybrid Mode**: For critical documents, trigger the `--use_llm` flag (using a local model like Qwen3-1.7B via `NativeBackend`) to merge fragmented tables.

### 3. Gnostic Curation (The Curator)
Raw markdown is not "Gnosis." It must be curated:
- **Refractive Compression**: Apply the `GnosisPacker` (RCF) logic to distill raw markdown into high-density summaries.
- **Noise Removal**: Filter out "boilerplate" phrases and redundant information.
- **Archetype Tagging**: Tag the curated content with a "Domain Resonance" score (per R-31) to determine which entity it belongs to.

### 4. Vector Indexing (The Anchor)
Final curated packs are anchored into the holographic memory:
- **Indexing**: Use `Qdrant` as the primary vector store.
- **Holographic Mapping**: Store the content as a multi-vector "Hologram" (per R-33), with separate vectors for the Logic, Sovereignty, and Synergy lenses.

## Hardware Impact (Ryzen 5700U)
- **RAM**: Marker and Crawl4AI can be memory-intensive.
  - **Mitigation**: Run the pipeline as a **Sequential Queue** (one document at a time) rather than parallel, to stay within the 14GB RAM limit.
- **CPU**: High load during Marker's OCR and distillation phase.
  - **Mitigation**: Pin the Sentinel process to cores 0-3, leaving cores 4-7 for the active inference engine.

## Implementation Note
To the Builder: The pipeline should be implemented as a set of AnyIO TaskGroups. The `Crawl4AI` and `Marker` tools should be wrapped in an `IntakeService` class. Ensure that all intermediate files (raw markdown) are stored in `data/intake/raw/` before being moved to `data/entities/<name>/knowledge/` after curation.

## References
- `docs/research/R33_holographic_memory_spec.md`
- `docs/research/R31_cross_pollination_spec.md`
- `Crawl4AI Documentation`
- `Marker GitHub Repository`
