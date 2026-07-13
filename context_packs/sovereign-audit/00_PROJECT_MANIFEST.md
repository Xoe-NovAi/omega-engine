# Enhanced Context Pack Manifest: sovereign-audit
Generated: 2026-07-12T01:50:53.719422
Description: Core Engine and Mandates Audit — hardened 2026-07-11
Total Files: 277
Estimated Total Tokens: 942505
Max Slots: 12

## Theme Breakdown
- mandates: 3 files, ~17127 tokens
  - AGENTS.md (6221 tokens)
  - SOVEREIGN_MANDATES.md (5820 tokens)
  - OMEGA_ENGINE.md (5086 tokens)
- oracle_core_a: 3 files, ~27815 tokens (sub-split of oracle_core for RAG-mode Pattern-Miners)
   - src/omega/oracle/model_gateway.py (16968 tokens)
   - src/omega/oracle/oracle.py (15362 tokens)
   - src/omega/oracle/entity_registry.py (12096 tokens)
- oracle_core_b: 3 files, ~27815 tokens (sub-split of oracle_core)
   - ... 3 core engine files
- oracle_core_c: 3 files, ~27817 tokens (sub-split of oracle_core)
   - ... 3 core engine files
- oracle_core: 9 files, ~83447 tokens (SUPERSEDED by _a/_b/_c — do NOT upload)
- memory: 8 files, ~31821 tokens
  - src/omega/memory_store.py (11337 tokens)
  - src/omega/memory/embeddings.py (4638 tokens)
  - src/omega/memory/providers.py (4590 tokens)
  - ... and 5 more
- providers: 7 files, ~14548 tokens
  - src/omega/oracle/backends/remote_provider.py (4488 tokens)
  - config/models.yaml (3948 tokens)
  - src/omega/oracle/backends/openai_compat.py (2221 tokens)
  - ... and 4 more
- observability: 12 files, ~44810 tokens
  - src/omega/observability/__init__.py (15337 tokens)
  - src/omega/monitoring/__init__.py (7718 tokens)
  - src/omega/observability/observability_reader.py (3827 tokens)
  - ... and 9 more
- mcp_hub: 3 files, ~2755 tokens
  - src/omega/mcp_runtime.py (2230 tokens)
  - src/omega/hub.py (505 tokens)
  - src/omega/gateway/__init__.py (20 tokens)
- strategy: 105 files, ~393663 tokens
  - docs/strategy/REFINED_AGB_KRIKRI_STRATEGY.md (24856 tokens)
  - docs/strategy/MIDDLEWARE_PLUGIN_IMPLEMENTATION_GUIDE.md (17222 tokens)
  - docs/strategy/archive/HARDENING_IMPLEMENTATION_PLAN.md (16729 tokens)
  - ... and 102 more
- general: 130 files, ~354334 tokens
  - src/omega/workers/background_researcher/distiller.py (14001 tokens)
  - src/omega/workers/youtube_worker.py (12597 tokens)
  - src/omega/cli/oracle_cli.py (12533 tokens)
  - ... and 127 more

## Usage Notes
- This pack uses XML format for optimal Claude comprehension
- Each file is wrapped in <file> tags with metadata attributes
- The manifest should be reviewed first to understand the pack structure
- Token counts are estimates using cl100k_base encoder (Claude's tokenizer)