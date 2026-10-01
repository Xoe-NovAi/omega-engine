<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ContentRouter Configuration — Omega-Specific

**File**: `config/headroom.yaml` (primary) + `HeadroomMiddlewareConfig` (code)  
**Section**: 02 of 10  
**Priority**: P1 — Exact configuration for all compressors  

---

## Complete ContentRouterConfig (Code Representation)

```python
# Built in HeadroomMiddleware._build_router_config()
ContentRouterConfig(
    # Feature flags — each independently toggleable via config/headroom.yaml
    enable_smart_crusher=True,
    enable_log_compressor=True,
    enable_search_compressor=True,
    enable_code_aware=True,
    enable_kompress=True,
    enable_tabular_compressor=True,
    enable_html_extractor=True,
    
    # SmartCrusher — JSON arrays, tool outputs (87.6% compression benchmark)
    smart_crusher=SmartCrusher(SmartCrusherConfig(
        max_items_after_crush=15,           # Keep top 15 most relevant items
        min_tokens_to_crush=200,            # Only crush if >200 tokens
        relevance=RelevanceScorerConfig(
            tier="hybrid",                  # hybrid | embedding | keyword
            embedding_model="all-MiniLM-L6-v2",  # Local embedding model
            hybrid_alpha=0.5,               # Balance keyword + embedding
        ),
    )),
    
    # LogCompressor — logs, stack traces, Hivemind output (80-90% compression)
    log_compressor=LogCompressor(LogCompressorConfig(
        max_total_lines=100,                # Max lines in output
        max_errors=10,                      # Max error entries to keep
        dedupe_warnings=True,               # Deduplicate repeated warnings
        preserve_recent_errors=5,           # Always keep 5 most recent errors
    )),
    
    # SearchCompressor — search results, file matches, RAG chunks (70-90%)
    search_compressor=SearchCompressor(SearchCompressorConfig(
        max_total_matches=30,               # Max total matches across all files
        max_files=15,                       # Max files to include
        always_keep_first=True,             # Always keep first match per file
        always_keep_last=True,              # Always keep last match per file
        min_score_threshold=0.1,            # Drop matches below score
    )),
    
    # CodeAwareCompressor — source code, GitHub diffs (70-85%)
    code_aware=CodeAwareCompressor(CodeAwareCompressorConfig(
        preserve_signatures=True,           # Keep function/class signatures
        preserve_imports=True,              # Keep import statements
        preserve_type_annotations=True,     # Keep type hints
        docstring_mode="FIRST_LINE",        # FIRST_LINE | NONE | SUMMARY
        max_function_lines=50,              # Truncate functions >50 lines
    )),
    
    # CacheAligner — KV cache prefix stabilization for local models
    cache_aligner=CacheAligner(),           # No config needed, auto-aligns
    
    # Kompress — query compression for retrieval (Phase 3)
    # enable_kompress=True enables this
    
    # TabularCompressor — CSV, spreadsheets
    # enable_tabular_compressor=True enables this
    
    # HTMLExtractor — web content extraction (94.9% compression)
    # enable_html_extractor=True enables this
    
    # Global router settings
    min_chars_for_block_compression=500,    # Min chars to attempt block compression
    min_ratio_aggressive=0.65,              # Aggressive compression if ratio > 0.65
)
```

---

## Environment Variable Overrides

All config values can be overridden via `HEADROOM_*` environment variables:

| Env Variable | Config Path | Type | Default |
|--------------|-------------|------|---------|
| `HEADROOM_ENABLE_SMART_CRUSHER` | `enable_smart_crusher` | bool | `true` |
| `HEADROOM_ENABLE_LOG_COMPRESSOR` | `enable_log_compressor` | bool | `true` |
| `HEADROOM_ENABLE_SEARCH_COMPRESSOR` | `enable_search_compressor` | bool | `true` |
| `HEADROOM_ENABLE_CODE_AWARE` | `enable_code_aware` | bool | `true` |
| `HEADROOM_ENABLE_CACHE_ALIGNER` | `enable_cache_aligner` | bool | `true` |
| `HEADROOM_ENABLE_CCR` | `enable_ccr` | bool | `true` |
| `HEADROOM_ENABLE_KOMPRESS` | `enable_kompress` | bool | `true` |
| `HEADROOM_ENABLE_TABULAR` | `enable_tabular_compressor` | bool | `true` |
| `HEADROOM_ENABLE_HTML` | `enable_html_extractor` | bool | `true` |
| `HEADROOM_SMART_CRUSHER_MAX_ITEMS` | `smart_crusher_max_items` | int | `15` |
| `HEADROOM_SMART_CRUSHER_MIN_TOKENS` | `smart_crusher_min_tokens` | int | `200` |
| `HEADROOM_SMART_CRUSHER_TIER` | `smart_crusher_relevance_tier` | str | `hybrid` |
| `HEADROOM_LOG_MAX_LINES` | `log_compressor_max_lines` | int | `100` |
| `HEADROOM_LOG_MAX_ERRORS` | `log_compressor_max_errors` | int | `10` |
| `HEADROOM_SEARCH_MAX_MATCHES` | `search_compressor_max_matches` | int | `30` |
| `HEADROOM_SEARCH_MAX_FILES` | `search_compressor_max_files` | int | `15` |
| `HEADROOM_CODE_PRESERVE_SIGNATURES` | `code_aware_preserve_signatures` | bool | `true` |
| `HEADROOM_CODE_PRESERVE_IMPORTS` | `code_aware_preserve_imports` | bool | `true` |
| `HEADROOM_CODE_PRESERVE_TYPES` | `code_aware_preserve_type_annotations` | bool | `true` |
| `HEADROOM_CODE_DOCSTRING_MODE` | `code_aware_docstring_mode` | str | `FIRST_LINE` |
| `HEADROOM_CCR_STORE_PATH` | `ccr_store_path` | str | `data/headroom/ccr_store` |
| `HEADROOM_CCR_MAX_GB` | `ccr_max_store_size_gb` | float | `2.0` |
| `HEADROOM_CCR_COMPRESSION` | `ccr_compression` | str | `zstd` |
| `HEADROOM_CCR_TTL_DAYS` | `ccr_ttl_days` | int | `30` |
| `HEADROOM_PROTECT_RECENT` | `protect_recent_turns` | int | `2` |
| `HEADROOM_TIMEOUT_SECONDS` | `operation_timeout_seconds` | float | `5.0` |
| `HEADROOM_ENABLE_METRICS` | `enable_metrics` | bool | `true` |

**Usage**:
```bash
# Disable all but SmartCrusher for minimal overhead
export HEADROOM_ENABLE_LOG_COMPRESSOR=false
export HEADROOM_ENABLE_SEARCH_COMPRESSOR=false
export HEADROOM_ENABLE_CODE_AWARE=false

# Aggressive SmartCrusher for maximum token savings
export HEADROOM_SMART_CRUSHER_MAX_ITEMS=10
export HEADROOM_SMART_CRUSHER_MIN_TOKENS=100
export HEADROOM_SMART_CRUSHER_TIER=keyword
```

---

## Feature Flag Matrix

| Compressor | Default | Use Case | Token Savings | Latency |
|------------|---------|----------|---------------|---------|
| **SmartCrusher** | ✅ ON | JSON tool outputs, Hivemind, structured data | 60-87% | 2-15ms |
| **LogCompressor** | ✅ ON | Logs, stack traces, Hivemind awareness | 80-90% | 1-5ms |
| **SearchCompressor** | ✅ ON | RAG chunks, web search, file search | 70-90% | 5-10ms |
| **CodeAwareCompressor** | ✅ ON | GitHub diffs, source code, patches | 70-85% | 5-15ms |
| **CacheAligner** | ✅ ON | KV cache prefix stabilization | N/A | <1ms |
| **CCR** | ✅ ON | Cross-agent reversible memory | N/A | 1-3ms |
| **Kompress** | ✅ ON | Query compression (Phase 3) | 30-50% | 10-20ms |
| **TabularCompressor** | ✅ ON | CSV, spreadsheet data | 60-80% | 2-10ms |
| **HTMLExtractor** | ✅ ON | Web page content | 94.9% | 5-20ms |

**Disable selectively** via env vars or `config/headroom.yaml` for:
- Debugging (see raw content)
- Latency-critical paths (disable Kompress, HTMLExtractor)
- Memory-constrained environments (disable CCR store)

---

## Per-Use-Case Config Profiles

### Profile: ModelGateway Tool Outputs (Default)
```yaml
# Optimized for: Oracle tool results, Hivemind, GitHub API responses
enable_smart_crusher: true
enable_log_compressor: true
enable_search_compressor: true
enable_code_aware: true
smart_crusher_max_items: 15
smart_crusher_min_tokens: 200
protect_recent_turns: 2
```

### Profile: RAG Retrieval (Aggressive)
```yaml
# Optimized for: Vector search results, document chunks
enable_search_compressor: true
enable_smart_crusher: true
search_compressor_max_matches: 20
search_compressor_max_files: 10
smart_crusher_max_items: 10
smart_crusher_min_tokens: 100
protect_top_k: 3
```

### Profile: MCP Tool Schemas (Maximum)
```yaml
# Optimized for: Tool schema JSON (86 tools → 5-10)
enable_smart_crusher: true
smart_crusher_max_items: 10
smart_crusher_min_tokens: 100
smart_crusher_relevance_tier: "keyword"  # Keyword relevance for tool names
```

### Profile: Entity Context (Conservative)
```yaml
# Optimized for: Soul.yaml, lessons, traits (preserve identity)
enable_smart_crusher: true
smart_crusher_max_items: 20
smart_crusher_min_tokens: 150
protect_recent_turns: 0  # No recent protection for static context
```

### Profile: Minimal (Debug/Latency-Critical)
```yaml
# Only SmartCrusher, no CCR, no CacheAligner
enable_smart_crusher: true
enable_log_compressor: false
enable_search_compressor: false
enable_code_aware: false
enable_cache_aligner: false
enable_ccr: false
enable_kompress: false
enable_tabular_compressor: false
enable_html_extractor: false
```

---

## Config Loading in Code

```python
# src/omega/config/headroom.py
from pydantic import BaseModel, Field
from typing import Optional
import yaml
from pathlib import Path


class HeadroomYamlConfig(BaseModel):
    """Pydantic model for config/headroom.yaml validation."""
    
    headroom: dict = Field(default_factory=dict)
    
    @classmethod
    def load(cls) -> "HeadroomYamlConfig":
        config_path = Path("config/headroom.yaml")
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            return cls(**data)
        return cls()  # Defaults
    
    def to_middleware_config(self) -> HeadroomMiddlewareConfig:
        """Convert YAML config to middleware config dataclass."""
        hr = self.headroom
        cr = hr.get("content_router", {})
        omega = hr.get("omega", {})
        
        return HeadroomMiddlewareConfig(
            enable_smart_crusher=cr.get("enable_smart_crusher", True),
            enable_log_compressor=cr.get("enable_log_compressor", True),
            enable_search_compressor=cr.get("enable_search_compressor", True),
            enable_code_aware=cr.get("enable_code_aware", True),
            enable_cache_aligner=cr.get("cache_aligner", {}).get("enabled", True),
            enable_ccr=hr.get("ccr", {}).get("enabled", True),
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
            ccr_store_path=hr.get("ccr", {}).get("store_path", "data/headroom/ccr_store"),
            ccr_max_store_size_gb=hr.get("ccr", {}).get("max_store_size_gb", 2.0),
            ccr_compression=hr.get("ccr", {}).get("compression", "zstd"),
            ccr_ttl_days=hr.get("ccr", {}).get("ttl_days", 30),
            protect_recent_turns=omega.get("model_gateway", {}).get("protect_recent_turns", 2),
            operation_timeout_seconds=5.0,
            enable_metrics=True,
        )
```

---

## Validation Rules

| Parameter | Min | Max | Validation |
|-----------|-----|-----|------------|
| `smart_crusher_max_items` | 1 | 100 | Must be > 0 |
| `smart_crusher_min_tokens` | 1 | 10000 | Must be > 0 |
| `log_compressor_max_lines` | 10 | 10000 | Must be > 0 |
| `log_compressor_max_errors` | 1 | 1000 | Must be > 0 |
| `search_compressor_max_matches` | 1 | 1000 | Must be > 0 |
| `search_compressor_max_files` | 1 | 100 | Must be > 0 |
| `protect_recent_turns` | 0 | 10 | Must be ≥ 0 |
| `operation_timeout_seconds` | 0.1 | 60 | Must be > 0 |
| `ccr_max_store_size_gb` | 0.1 | 50 | Must be > 0 |
| `ccr_ttl_days` | 1 | 365 | Must be > 0 |

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 02/10*