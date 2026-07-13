# Enhanced Context Pack Manifest: youtube-research-primer
Generated: 2026-07-12T01:51:00.756226
Description: YouTube Research Module context — spec, implementation, and integration points
Total Files: 20
Estimated Total Tokens: 58608
Max Slots: 12

## Theme Breakdown
- spec: 1 files, ~5846 tokens
  - docs/research/R_YOUTUBE_RESEARCH_MODULE_SPEC.md (5846 tokens)
- implementation: 9 files, ~14708 tokens
  - src/omega_youtube_research/sieve.py (3012 tokens)
  - src/omega_youtube_research/persistence.py (2782 tokens)
  - src/omega_youtube_research/signer.py (2324 tokens)
  - ... and 6 more
- tests: 1 files, ~4556 tokens
  - tests/test_youtube_research_module.py (4556 tokens)
- ingestion_queue: 1 files, ~1677 tokens
  - youtube-links-for-ingestion.txt (1677 tokens)
- memory_integration: 8 files, ~31821 tokens
  - src/omega/memory_store.py (11337 tokens)
  - src/omega/memory/embeddings.py (4638 tokens)
  - src/omega/memory/providers.py (4590 tokens)
  - ... and 5 more

## Usage Notes
- This pack uses XML format for optimal Claude comprehension
- Each file is wrapped in <file> tags with metadata attributes
- The manifest should be reviewed first to understand the pack structure
- Token counts are estimates using cl100k_base encoder (Claude's tokenizer)