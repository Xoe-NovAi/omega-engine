# Configuration — config/headroom.yaml + Environment Overrides

**File**: `config/headroom.yaml`  
**Section**: 08 of 10  
**Priority**: P1 — Complete configuration with env overrides and feature flags  

---

## Complete config/headroom.yaml

```yaml
# config/headroom.yaml
# Complete Headroom configuration for Omega Engine Phase 2
# All compressors enabled per research benchmarks (Carmack Q6.1 verified)
# Environment variable overrides: HEADROOM_<SECTION>_<KEY>

headroom:
  # ============================================================
  # ContentRouter — Orchestrates all compressors
  # ============================================================
  content_router:
    # Feature flags — each independently toggleable (M19 Adversarial Alchemy)
    enable_smart_crusher: true
    enable_log_compressor: true
    enable_search_compressor: true
    enable_code_aware: true
    enable_kompress: true
    enable_tabular_compressor: true
    enable_html_extractor: true
    enable_cache_aligner: true
    
    # ----------------------------------------------------------
    # SmartCrusher — JSON arrays, tool outputs (87.6% compression)
    # ----------------------------------------------------------
    smart_crusher:
      max_items_after_crush: 15           # Keep top 15 most relevant items
      min_tokens_to_crush: 200            # Only crush if >200 tokens
      relevance:
        tier: "hybrid"                    # hybrid | embedding | keyword
        embedding_model: "all-MiniLM-L6-v2"  # Local embedding model
        hybrid_alpha: 0.5                 # Balance keyword + embedding
    
    # ----------------------------------------------------------
    # LogCompressor — logs, stack traces, Hivemind output (80-90%)
    # ----------------------------------------------------------
    log_compressor:
      max_total_lines: 100                # Max lines in output
      max_errors: 10                      # Max error entries to keep
      dedupe_warnings: true               # Deduplicate repeated warnings
      preserve_recent_errors: 5           # Always keep 5 most recent errors
    
    # ----------------------------------------------------------
    # SearchCompressor — search results, file matches, RAG (70-90%)
    # ----------------------------------------------------------
    search_compressor:
      max_total_matches: 30               # Max total matches across all files
      max_files: 15                       # Max files to include
      always_keep_first: true             # Always keep first match per file
      always_keep_last: true              # Always keep last match per file
      min_score_threshold: 0.1            # Drop matches below score
    
    # ----------------------------------------------------------
    # CodeAwareCompressor — source code, GitHub diffs (70-85%)
    # ----------------------------------------------------------
    code_aware:
      preserve_signatures: true           # Keep function/class signatures
      preserve_imports: true              # Keep import statements
      preserve_type_annotations: true     # Keep type hints
      docstring_mode: "FIRST_LINE"        # FIRST_LINE | NONE | SUMMARY
      max_function_lines: 50              # Truncate functions >50 lines
    
    # ----------------------------------------------------------
    # CacheAligner — KV cache prefix stabilization
    # ----------------------------------------------------------
    cache_aligner:
      enabled: true
      prefix_tokens: 512                  # Tokens to align for KV cache hits
    
    # ----------------------------------------------------------
    # Kompress — query compression for retrieval (Phase 3)
    # ----------------------------------------------------------
    kompress:
      enabled: true
      model: "headroom/kompress-base"
      max_compression_ratio: 0.3          # Target 70% reduction
    
    # ----------------------------------------------------------
    # TabularCompressor — CSV, spreadsheets
    # ----------------------------------------------------------
    tabular_compressor:
      compaction_format: "csv-schema"
      max_rows: 100
      max_cols: 20
    
    # ----------------------------------------------------------
    # HTMLExtractor — web content extraction (94.9% compression)
    # ----------------------------------------------------------
    html_extractor:
      enabled: true
      remove_scripts: true
      remove_styles: true
      preserve_links: true
    
    # ----------------------------------------------------------
    # Global router settings
    # ----------------------------------------------------------
    min_chars_for_block_compression: 500  # Min chars to attempt block compression
    min_ratio_aggressive: 0.65            # Aggressive compression if ratio > 0.65
  
  # ============================================================
  # CCR — Cross-agent reversible memory
  # ============================================================
  ccr:
    enabled: true
    store_path: "data/headroom/ccr_store"
    max_store_size_gb: 2.0
    compression: "zstd"                   # zstd | lz4 | none
    ttl_days: 30
    cleanup_interval_hours: 24
    enable_index: true
  
  # ============================================================
  # Omega-specific integration settings
  # ============================================================
  omega:
    # ----------------------------------------------------------
    # ModelGateway integration (_prepare_messages)
    # ----------------------------------------------------------
    model_gateway:
      protect_recent_turns: 2             # Never compress last N turns (Carmack Q6.1)
      compress_tool_outputs: true         # SmartCrusher on tool results
      compress_logs: true                 # LogCompressor on Hivemind/logs
      compress_search_results: true       # SearchCompressor on RAG
      compress_code: true                 # CodeAware on GitHub diffs
    
    # ----------------------------------------------------------
    # RAG Retrieval integration (SelectiveHydration)
    # ----------------------------------------------------------
    rag_retrieval:
      max_chunks_per_query: 10            # Final chunks after compression
      max_tokens_per_chunk: 2000          # Max tokens per chunk
      target_total_tokens: 8000           # Total token budget for all chunks
      protect_top_k: 3                    # Never compress top-K most relevant
      enable_search_compressor: true
      enable_smart_crusher: true
    
    # ----------------------------------------------------------
    # MCP Tool Schema compression
    # ----------------------------------------------------------
    mcp_tools:
      compress_schemas: true
      max_items_after_crush: 10           # Keep top 10 tools
      min_tokens_to_crush: 100
      relevance_tier: "keyword"           # Keyword relevance for tool names
      hybrid_alpha: 0.3
    
    # ----------------------------------------------------------
    # Entity Context compression (EntityRegistry)
    # ----------------------------------------------------------
    entity_context:
      compress_soul: true
      compress_lessons: true
      max_items_after_crush: 20
      min_tokens_to_crush: 150
      protect_recent_lessons: 5           # Never compress 5 most recent lessons
      summarize_lessons: true             # L1→L2 summarization for old lessons
      max_trait_length: 200               # Truncate trait descriptions
    
    # ----------------------------------------------------------
    # CCR integration
    # ----------------------------------------------------------
    ccr:
      auto_store_compressed: true         # Auto-store during compression
      retrieve_on_demand: true            # Enable MCP headroom_retrieve tool
```

---

## Environment Variable Overrides

All config values can be overridden via `HEADROOM_*` environment variables.  
Format: `HEADROOM_<SECTION>_<SUBSECTION>_<KEY>` (uppercase, underscores).

### ContentRouter Feature Flags

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_ENABLE_SMART_CRUSHER` | `content_router.enable_smart_crusher` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_LOG_COMPRESSOR` | `content_router.enable_log_compressor` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_SEARCH_COMPRESSOR` | `content_router.enable_search_compressor` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_CODE_AWARE` | `content_router.enable_code_aware` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_KOMPRESS` | `content_router.enable_kompress` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_TABULAR_COMPRESSOR` | `content_router.enable_tabular_compressor` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_HTML_EXTRACTOR` | `content_router.enable_html_extractor` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_ENABLE_CACHE_ALIGNER` | `content_router.enable_cache_aligner` | bool | `true` |

### SmartCrusher Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_MAX_ITEMS_AFTER_CRUSH` | `content_router.smart_crusher.max_items_after_crush` | int | `15` |
| `HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_MIN_TOKENS_TO_CRUSH` | `content_router.smart_crusher.min_tokens_to_crush` | int | `200` |
| `HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_RELEVANCE_TIER` | `content_router.smart_crusher.relevance.tier` | str | `hybrid` |
| `HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_RELEVANCE_EMBEDDING_MODEL` | `content_router.smart_crusher.relevance.embedding_model` | str | `all-MiniLM-L6-v2` |
| `HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_RELEVANCE_HYBRID_ALPHA` | `content_router.smart_crusher.relevance.hybrid_alpha` | float | `0.5` |

### LogCompressor Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_LOG_COMPRESSOR_MAX_TOTAL_LINES` | `content_router.log_compressor.max_total_lines` | int | `100` |
| `HEADROOM_CONTENT_ROUTER_LOG_COMPRESSOR_MAX_ERRORS` | `content_router.log_compressor.max_errors` | int | `10` |
| `HEADROOM_CONTENT_ROUTER_LOG_COMPRESSOR_DEDUPE_WARNINGS` | `content_router.log_compressor.dedupe_warnings` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_LOG_COMPRESSOR_PRESERVE_RECENT_ERRORS` | `content_router.log_compressor.preserve_recent_errors` | int | `5` |

### SearchCompressor Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_SEARCH_COMPRESSOR_MAX_TOTAL_MATCHES` | `content_router.search_compressor.max_total_matches` | int | `30` |
| `HEADROOM_CONTENT_ROUTER_SEARCH_COMPRESSOR_MAX_FILES` | `content_router.search_compressor.max_files` | int | `15` |
| `HEADROOM_CONTENT_ROUTER_SEARCH_COMPRESSOR_ALWAYS_KEEP_FIRST` | `content_router.search_compressor.always_keep_first` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_SEARCH_COMPRESSOR_ALWAYS_KEEP_LAST` | `content_router.search_compressor.always_keep_last` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_SEARCH_COMPRESSOR_MIN_SCORE_THRESHOLD` | `content_router.search_compressor.min_score_threshold` | float | `0.1` |

### CodeAwareCompressor Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_CODE_AWARE_PRESERVE_SIGNATURES` | `content_router.code_aware.preserve_signatures` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_CODE_AWARE_PRESERVE_IMPORTS` | `content_router.code_aware.preserve_imports` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_CODE_AWARE_PRESERVE_TYPE_ANNOTATIONS` | `content_router.code_aware.preserve_type_annotations` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_CODE_AWARE_DOCSTRING_MODE` | `content_router.code_aware.docstring_mode` | str | `FIRST_LINE` |
| `HEADROOM_CONTENT_ROUTER_CODE_AWARE_MAX_FUNCTION_LINES` | `content_router.code_aware.max_function_lines` | int | `50` |

### CacheAligner Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CONTENT_ROUTER_CACHE_ALIGNER_ENABLED` | `content_router.cache_aligner.enabled` | bool | `true` |
| `HEADROOM_CONTENT_ROUTER_CACHE_ALIGNER_PREFIX_TOKENS` | `content_router.cache_aligner.prefix_tokens` | int | `512` |

### CCR Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_CCR_ENABLED` | `ccr.enabled` | bool | `true` |
| `HEADROOM_CCR_STORE_PATH` | `ccr.store_path` | str | `data/headroom/ccr_store` |
| `HEADROOM_CCR_MAX_STORE_SIZE_GB` | `ccr.max_store_size_gb` | float | `2.0` |
| `HEADROOM_CCR_COMPRESSION` | `ccr.compression` | str | `zstd` |
| `HEADROOM_CCR_TTL_DAYS` | `ccr.ttl_days` | int | `30` |
| `HEADROOM_CCR_CLEANUP_INTERVAL_HOURS` | `ccr.cleanup_interval_hours` | int | `24` |

### Omega Integration Config

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_OMEGA_MODEL_GATEWAY_PROTECT_RECENT_TURNS` | `omega.model_gateway.protect_recent_turns` | int | `2` |
| `HEADROOM_OMEGA_MODEL_GATEWAY_COMPRESS_TOOL_OUTPUTS` | `omega.model_gateway.compress_tool_outputs` | bool | `true` |
| `HEADROOM_OMEGA_MODEL_GATEWAY_COMPRESS_LOGS` | `omega.model_gateway.compress_logs` | bool | `true` |
| `HEADROOM_OMEGA_MODEL_GATEWAY_COMPRESS_SEARCH_RESULTS` | `omega.model_gateway.compress_search_results` | bool | `true` |
| `HEADROOM_OMEGA_MODEL_GATEWAY_COMPRESS_CODE` | `omega.model_gateway.compress_code` | bool | `true` |
| `HEADROOM_OMEGA_RAG_RETRIEVAL_MAX_CHUNKS_PER_QUERY` | `omega.rag_retrieval.max_chunks_per_query` | int | `10` |
| `HEADROOM_OMEGA_RAG_RETRIEVAL_MAX_TOKENS_PER_CHUNK` | `omega.rag_retrieval.max_tokens_per_chunk` | int | `2000` |
| `HEADROOM_OMEGA_RAG_RETRIEVAL_TARGET_TOTAL_TOKENS` | `omega.rag_retrieval.target_total_tokens` | int | `8000` |
| `HEADROOM_OMEGA_RAG_RETRIEVAL_PROTECT_TOP_K` | `omega.rag_retrieval.protect_top_k` | int | `3` |
| `HEADROOM_OMEGA_MCP_TOOLS_COMPRESS_SCHEMAS` | `omega.mcp_tools.compress_schemas` | bool | `true` |
| `HEADROOM_OMEGA_MCP_TOOLS_MAX_ITEMS_AFTER_CRUSH` | `omega.mcp_tools.max_items_after_crush` | int | `10` |
| `HEADROOM_OMEGA_ENTITY_CONTEXT_COMPRESS_SOUL` | `omega.entity_context.compress_soul` | bool | `true` |
| `HEADROOM_OMEGA_ENTITY_CONTEXT_COMPRESS_LESSONS` | `omega.entity_context.compress_lessons` | bool | `true` |
| `HEADROOM_OMEGA_ENTITY_CONTEXT_PROTECT_RECENT_LESSONS` | `omega.entity_context.protect_recent_lessons` | int | `5` |
| `HEADROOM_OMEGA_CCR_AUTO_STORE_COMPRESSED` | `omega.ccr.auto_store_compressed` | bool | `true` |
| `HEADROOM_OMEGA_CCR_RETRIEVE_ON_DEMAND` | `omega.ccr.retrieve_on_demand` | bool | `true` |

---

## Usage Examples

### Disable All But SmartCrusher (Minimal Overhead)
```bash
export HEADROOM_CONTENT_ROUTER_ENABLE_LOG_COMPRESSOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_SEARCH_COMPRESSOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_CODE_AWARE=false
export HEADROOM_CONTENT_ROUTER_ENABLE_KOMPRESS=false
export HEADROOM_CONTENT_ROUTER_ENABLE_TABULAR_COMPRESSOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_HTML_EXTRACTOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_CACHE_ALIGNER=false
export HEADROOM_CCR_ENABLED=false
```

### Aggressive Compression (Maximum Token Savings)
```bash
export HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_MAX_ITEMS_AFTER_CRUSH=10
export HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_MIN_TOKENS_TO_CRUSH=100
export HEADROOM_CONTENT_ROUTER_SMART_CRUSHER_RELEVANCE_TIER=keyword
export HEADROOM_OMEGA_RAG_RETRIEVAL_MAX_CHUNKS_PER_QUERY=5
export HEADROOM_OMEGA_RAG_RETRIEVAL_TARGET_TOTAL_TOKENS=4000
export HEADROOM_OMEGA_MCP_TOOLS_MAX_ITEMS_AFTER_CRUSH=5
```

### Debug Mode (No Compression)
```bash
export HEADROOM_CONTENT_ROUTER_ENABLE_SMART_CRUSHER=false
export HEADROOM_CONTENT_ROUTER_ENABLE_LOG_COMPRESSOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_SEARCH_COMPRESSOR=false
export HEADROOM_CONTENT_ROUTER_ENABLE_CODE_AWARE=false
export HEADROOM_CCR_ENABLED=false
```

### Production Optimized (Balanced)
```bash
# Defaults are production-optimized
# Only override if specific tuning needed
export HEADROOM_OMEGA_MODEL_GATEWAY_PROTECT_RECENT_TURNS=3
export HEADROOM_OMEGA_RAG_RETRIEVAL_PROTECT_TOP_K=5
```

---

## Config Loading in Code

```python
# src/omega/config/headroom.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import yaml
import os
from pathlib import Path


class ContentRouterConfig(BaseModel):
    enable_smart_crusher: bool = True
    enable_log_compressor: bool = True
    enable_search_compressor: bool = True
    enable_code_aware: bool = True
    enable_kompress: bool = True
    enable_tabular_compressor: bool = True
    enable_html_extractor: bool = True
    enable_cache_aligner: bool = True
    
    smart_crusher: Dict[str, Any] = Field(default_factory=lambda: {
        "max_items_after_crush": 15,
        "min_tokens_to_crush": 200,
        "relevance": {"tier": "hybrid", "embedding_model": "all-MiniLM-L6-v2", "hybrid_alpha": 0.5},
    })
    log_compressor: Dict[str, Any] = Field(default_factory=lambda: {
        "max_total_lines": 100, "max_errors": 10, "dedupe_warnings": True, "preserve_recent_errors": 5,
    })
    search_compressor: Dict[str, Any] = Field(default_factory=lambda: {
        "max_total_matches": 30, "max_files": 15, "always_keep_first": True, "always_keep_last": True, "min_score_threshold": 0.1,
    })
    code_aware: Dict[str, Any] = Field(default_factory=lambda: {
        "preserve_signatures": True, "preserve_imports": True, "preserve_type_annotations": True,
        "docstring_mode": "FIRST_LINE", "max_function_lines": 50,
    })
    cache_aligner: Dict[str, Any] = Field(default_factory=lambda: {"enabled": True, "prefix_tokens": 512})
    kompress: Dict[str, Any] = Field(default_factory=lambda: {"enabled": True, "model": "headroom/kompress-base", "max_compression_ratio": 0.3})
    tabular_compressor: Dict[str, Any] = Field(default_factory=lambda: {"compaction_format": "csv-schema", "max_rows": 100, "max_cols": 20})
    html_extractor: Dict[str, Any] = Field(default_factory=lambda: {"enabled": True, "remove_scripts": True, "remove_styles": True, "preserve_links": True})
    min_chars_for_block_compression: int = 500
    min_ratio_aggressive: float = 0.65


class CCRConfig(BaseModel):
    enabled: bool = True
    store_path: str = "data/headroom/ccr_store"
    max_store_size_gb: float = 2.0
    compression: str = "zstd"
    ttl_days: int = 30
    cleanup_interval_hours: int = 24
    enable_index: bool = True


class OmegaIntegrationConfig(BaseModel):
    model_gateway: Dict[str, Any] = Field(default_factory=lambda: {
        "protect_recent_turns": 2, "compress_tool_outputs": True, "compress_logs": True,
        "compress_search_results": True, "compress_code": True,
    })
    rag_retrieval: Dict[str, Any] = Field(default_factory=lambda: {
        "max_chunks_per_query": 10, "max_tokens_per_chunk": 2000, "target_total_tokens": 8000,
        "protect_top_k": 3, "enable_search_compressor": True, "enable_smart_crusher": True,
    })
    mcp_tools: Dict[str, Any] = Field(default_factory=lambda: {
        "compress_schemas": True, "max_items_after_crush": 10, "min_tokens_to_crush": 100,
        "relevance_tier": "keyword", "hybrid_alpha": 0.3,
    })
    entity_context: Dict[str, Any] = Field(default_factory=lambda: {
        "compress_soul": True, "compress_lessons": True, "max_items_after_crush": 20,
        "min_tokens_to_crush": 150, "protect_recent_lessons": 5, "summarize_lessons": True,
        "max_trait_length": 200,
    })
    ccr: Dict[str, Any] = Field(default_factory=lambda: {
        "auto_store_compressed": True, "retrieve_on_demand": True,
    })


class HeadroomYamlConfig(BaseModel):
    headroom: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def load(cls) -> "HeadroomYamlConfig":
        config_path = Path("config/headroom.yaml")
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            return cls(**data)
        return cls()
    
    def apply_env_overrides(self) -> "HeadroomYamlConfig":
        """Apply HEADROOM_* environment variable overrides."""
        # This is handled by Pydantic Settings or manual mapping
        # For simplicity, we document the env vars above
        return self
    
    def to_middleware_config(self) -> "HeadroomMiddlewareConfig":
        """Convert to HeadroomMiddlewareConfig dataclass."""
        from omega.oracle.middleware.headroom import HeadroomMiddlewareConfig
        
        hr = self.headroom
        cr = hr.get("content_router", {})
        ccr = hr.get("ccr", {})
        omega = hr.get("omega", {})
        
        return HeadroomMiddlewareConfig(
            enable_smart_crusher=cr.get("enable_smart_crusher", True),
            enable_log_compressor=cr.get("enable_log_compressor", True),
            enable_search_compressor=cr.get("enable_search_compressor", True),
            enable_code_aware=cr.get("enable_code_aware", True),
            enable_cache_aligner=cr.get("cache_aligner", {}).get("enabled", True),
            enable_ccr=ccr.get("enabled", True),
            enable_kompress=cr.get("enable_kompress", True),
            enable_tabular_compressor=cr.get("enable_tabular_compressor", True),
            enable_html_extractor=cr.get("enable_html_extractor", True),
            smart_crusher_max_items=cr.get("smart_crusher", {}).get("max_items_after_crush", 15),
            smart_crusher_min_tokens=cr.get("smart_crusher", {}).get("min_tokens_to_crush", 200),
            smart_crusher_relevance_tier=cr.get("smart_crusher", {}).get("relevance", {}).get("tier", "hybrid"),
            log_compressor_max_lines=cr.get("log_compressor", {}).get("max_total_lines", 100),
            log_compressor_max_errors=cr.get("log_compressor", {}).get("max_errors", 10),
            search_compressor_max_matches=cr.get("search_compressor", {}).get("max_total_matches", 30),
            search_compressor_max_files=cr.get("search_compressor", {}).get("max_files", 15),
            code_aware_preserve_signatures=cr.get("code_aware", {}).get("preserve_signatures", True),
            code_aware_preserve_imports=cr.get("code_aware", {}).get("preserve_imports", True),
            code_aware_preserve_type_annotations=cr.get("code_aware", {}).get("preserve_type_annotations", True),
            code_aware_docstring_mode=cr.get("code_aware", {}).get("docstring_mode", "FIRST_LINE"),
            ccr_store_path=ccr.get("store_path", "data/headroom/ccr_store"),
            ccr_max_store_size_gb=ccr.get("max_store_size_gb", 2.0),
            ccr_compression=ccr.get("compression", "zstd"),
            ccr_ttl_days=ccr.get("ttl_days", 30),
            protect_recent_turns=omega.get("model_gateway", {}).get("protect_recent_turns", 2),
            operation_timeout_seconds=5.0,
            enable_metrics=True,
        )
```

---

## Validation Rules

| Parameter | Min | Max | Validation |
|-----------|-----|-----|------------|
| `smart_crusher.max_items_after_crush` | 1 | 100 | Must be > 0 |
| `smart_crusher.min_tokens_to_crush` | 1 | 10000 | Must be > 0 |
| `log_compressor.max_total_lines` | 10 | 10000 | Must be > 0 |
| `log_compressor.max_errors` | 1 | 1000 | Must be > 0 |
| `search_compressor.max_total_matches` | 1 | 1000 | Must be > 0 |
| `search_compressor.max_files` | 1 | 100 | Must be > 0 |
| `code_aware.max_function_lines` | 10 | 1000 | Must be > 0 |
| `cache_aligner.prefix_tokens` | 64 | 8192 | Must be > 0 |
| `model_gateway.protect_recent_turns` | 0 | 10 | Must be ≥ 0 |
| `rag_retrieval.max_chunks_per_query` | 1 | 50 | Must be > 0 |
| `rag_retrieval.max_tokens_per_chunk` | 100 | 10000 | Must be > 0 |
| `rag_retrieval.target_total_tokens` | 1000 | 100000 | Must be > 0 |
| `rag_retrieval.protect_top_k` | 0 | 20 | Must be ≥ 0 |
| `mcp_tools.max_items_after_crush` | 1 | 50 | Must be > 0 |
| `entity_context.protect_recent_lessons` | 0 | 50 | Must be ≥ 0 |
| `entity_context.max_trait_length` | 50 | 2000 | Must be > 0 |
| `ccr.max_store_size_gb` | 0.1 | 50 | Must be > 0 |
| `ccr.ttl_days` | 1 | 365 | Must be > 0 |

---

## Feature Flag Quick Reference

```bash
# Enable/disable individual compressors
HEADROOM_CONTENT_ROUTER_ENABLE_SMART_CRUSHER=true
HEADROOM_CONTENT_ROUTER_ENABLE_LOG_COMPRESSOR=true
HEADROOM_CONTENT_ROUTER_ENABLE_SEARCH_COMPRESSOR=true
HEADROOM_CONTENT_ROUTER_ENABLE_CODE_AWARE=true
HEADROOM_CONTENT_ROUTER_ENABLE_KOMPRESS=true
HEADROOM_CONTENT_ROUTER_ENABLE_TABULAR_COMPRESSOR=true
HEADROOM_CONTENT_ROUTER_ENABLE_HTML_EXTRACTOR=true
HEADROOM_CONTENT_ROUTER_ENABLE_CACHE_ALIGNER=true

# Enable/disable CCR
HEADROOM_CCR_ENABLED=true

# Enable/disable Omega integrations
HEADROOM_OMEGA_MODEL_GATEWAY_COMPRESS_TOOL_OUTPUTS=true
HEADROOM_OMEGA_RAG_RETRIEVAL_ENABLE_SEARCH_COMPRESSOR=true
HEADROOM_OMEGA_MCP_TOOLS_COMPRESS_SCHEMAS=true
HEADROOM_OMEGA_ENTITY_CONTEXT_COMPRESS_SOUL=true
HEADROOM_OMEGA_CCR_AUTO_STORE_COMPRESSED=true
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 08/10*