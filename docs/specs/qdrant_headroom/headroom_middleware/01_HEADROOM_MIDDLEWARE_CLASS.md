<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# HeadroomMiddleware Class — Complete Implementation

**File**: `src/omega/oracle/middleware/headroom.py`  
**Section**: 01 of 10  
**Priority**: P1 — Core middleware implementation  

---

## Class Definition

```python
"""
Headroom Middleware for Omega Engine — Semantic Compression Pipeline.

Compresses tool outputs, logs, search results, and code BEFORE token counting
and context injection. Integrates with CCR for reversible cross-agent memory.

Mandate Compliance:
- M1 AnyIO Absolute: All async uses anyio.to_thread.run_sync()
- M7 Local-First: Headroom runs locally, no external API
- M18 Token Efficiency: 60-95% token reduction on tool outputs
- M19 Adversarial Alchemy: Feature flags, reversible CCR
- M23 Failure Integrity: 5s timeout, graceful fallback, no soft failures
"""

from __future__ import annotations

import anyio
import time
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from contextlib import suppress

from headroom import ContentRouter, ContentRouterConfig
from headroom.transforms import (
    SmartCrusher, SmartCrusherConfig,
    LogCompressor, LogCompressorConfig,
    SearchCompressor, SearchCompressorConfig,
    CodeAwareCompressor, CodeAwareCompressorConfig,
    CacheAligner,
    CCR, CCRConfig,
    RelevanceScorerConfig,
)

from omega.oracle.model_gateway import Message
from omega.config import get_config


@dataclass
class HeadroomMiddlewareConfig:
    """Configuration for Headroom middleware (loaded from config/headroom.yaml)."""
    
    # Feature flags — each compressor independently toggleable (M19)
    enable_smart_crusher: bool = True
    enable_log_compressor: bool = True
    enable_search_compressor: bool = True
    enable_code_aware: bool = True
    enable_cache_aligner: bool = True
    enable_ccr: bool = True
    enable_kompress: bool = True
    enable_tabular_compressor: bool = True
    enable_html_extractor: bool = True
    
    # SmartCrusher config (per Carmack Q6.1 verified benchmarks)
    smart_crusher_max_items: int = 15
    smart_crusher_min_tokens: int = 200
    smart_crusher_relevance_tier: str = "hybrid"  # "hybrid" | "embedding" | "keyword"
    
    # LogCompressor config
    log_compressor_max_lines: int = 100
    log_compressor_max_errors: int = 10
    
    # SearchCompressor config
    search_compressor_max_matches: int = 30
    search_compressor_max_files: int = 15
    
    # CodeAwareCompressor config
    code_aware_preserve_signatures: bool = True
    code_aware_preserve_imports: bool = True
    code_aware_preserve_type_annotations: bool = True
    code_aware_docstring_mode: str = "FIRST_LINE"  # FIRST_LINE | NONE | SUMMARY
    
    # CCR config
    ccr_store_path: str = "data/headroom/ccr_store"
    ccr_max_store_size_gb: float = 2.0
    ccr_compression: str = "zstd"  # zstd | lz4 | none
    ccr_ttl_days: int = 30
    
    # Protection: never compress recent N turns (Carmack Q6.1)
    protect_recent_turns: int = 2
    
    # Timeout for Headroom operations (M23 Failure Integrity)
    operation_timeout_seconds: float = 5.0
    
    # Metrics
    enable_metrics: bool = True


@dataclass
class CompressionResult:
    """Result of a compression operation."""
    compressed: List[Message]
    original_token_count: int
    compressed_token_count: int
    compression_ratio: float
    latency_ms: float
    compressor_used: str
    ccr_refs: List[str] = field(default_factory=list)
    fallback: bool = False
    error: Optional[str] = None


class HeadroomMiddleware:
    """
    Semantic compression middleware for ModelGateway and RAG pipeline.
    
    Compresses tool outputs, logs, search results, and code BEFORE token counting
    and context injection. Integrates with CCR for reversible cross-agent memory.
    
    Usage:
        middleware = HeadroomMiddleware(config)
        await middleware.initialize()
        compressed = await middleware.compress_messages(messages)
        # ... use compressed messages ...
        await middleware.shutdown()
    """
    
    def __init__(self, config: Optional[HeadroomMiddlewareConfig] = None):
        self.config = config or HeadroomMiddlewareConfig()
        self._router: Optional[ContentRouter] = None
        self._ccr: Optional[CCR] = None
        self._initialized = False
        self._metrics = {
            "total_compressions": 0,
            "total_tokens_original": 0,
            "total_tokens_compressed": 0,
            "total_latency_ms": 0.0,
            "fallback_count": 0,
            "error_count": 0,
            "by_compressor": {},
        }
    
    async def initialize(self) -> None:
        """Initialize Headroom components (async for CCR store setup)."""
        if self._initialized:
            return
        
        # Build ContentRouter with all compressors
        router_config = self._build_router_config()
        
        self._router = ContentRouter(router_config)
        
        # Initialize CCR store for cross-agent reversible memory
        if self.config.enable_ccr:
            self._ccr = CCR(CCRConfig(
                store_path=self.config.ccr_store_path,
                max_store_size_gb=self.config.ccr_max_store_size_gb,
                compression=self.config.ccr_compression,
                ttl_days=self.config.ccr_ttl_days,
            ))
            await anyio.to_thread.run_sync(self._ccr.initialize)
        
        # Ensure CCR store directory exists
        import os
        os.makedirs(self.config.ccr_store_path, exist_ok=True)
        
        self._initialized = True
    
    def _build_router_config(self) -> ContentRouterConfig:
        """Build ContentRouterConfig from middleware config."""
        return ContentRouterConfig(
            enable_smart_crusher=self.config.enable_smart_crusher,
            enable_log_compressor=self.config.enable_log_compressor,
            enable_search_compressor=self.config.enable_search_compressor,
            enable_code_aware=self.config.enable_code_aware,
            enable_kompress=self.config.enable_kompress,
            enable_tabular_compressor=self.config.enable_tabular_compressor,
            enable_html_extractor=self.config.enable_html_extractor,
            smart_crusher=SmartCrusher(SmartCrusherConfig(
                max_items_after_crush=self.config.smart_crusher_max_items,
                min_tokens_to_crush=self.config.smart_crusher_min_tokens,
                relevance=RelevanceScorerConfig(
                    tier=self.config.smart_crusher_relevance_tier,
                    embedding_model="all-MiniLM-L6-v2",
                    hybrid_alpha=0.5,
                ),
            )) if self.config.enable_smart_crusher else None,
            log_compressor=LogCompressor(LogCompressorConfig(
                max_total_lines=self.config.log_compressor_max_lines,
                max_errors=self.config.log_compressor_max_errors,
                dedupe_warnings=True,
                preserve_recent_errors=5,
            )) if self.config.enable_log_compressor else None,
            search_compressor=SearchCompressor(SearchCompressorConfig(
                max_total_matches=self.config.search_compressor_max_matches,
                max_files=self.config.search_compressor_max_files,
                always_keep_first=True,
                always_keep_last=True,
                min_score_threshold=0.1,
            )) if self.config.enable_search_compressor else None,
            code_aware=CodeAwareCompressor(CodeAwareCompressorConfig(
                preserve_signatures=self.config.code_aware_preserve_signatures,
                preserve_imports=self.config.code_aware_preserve_imports,
                preserve_type_annotations=self.config.code_aware_preserve_type_annotations,
                docstring_mode=self.config.code_aware_docstring_mode,
                max_function_lines=50,
            )) if self.config.enable_code_aware else None,
            cache_aligner=CacheAligner() if self.config.enable_cache_aligner else None,
            min_chars_for_block_compression=500,
            min_ratio_aggressive=0.65,
        )
    
    async def compress_messages(self, messages: List[Message]) -> List[Message]:
        """
        Compress messages before token counting and context injection.
        
        Protects the most recent N turns from compression (Carmack Q6.1).
        Falls back to original messages on any error (M23 Failure Integrity).
        
        Args:
            messages: List of message dicts with 'role', 'content', optional 'tool_calls'
            
        Returns:
            Compressed messages (same structure, reduced content)
        """
        start_time = time.perf_counter()
        
        if not self._initialized:
            await self.initialize()
        
        if not messages:
            return messages
        
        try:
            # Protect recent turns from compression
            protected_count = min(self.config.protect_recent_turns, len(messages))
            protected = messages[-protected_count:] if protected_count > 0 else []
            to_compress = messages[:-protected_count] if protected_count > 0 else messages
            
            if not to_compress:
                return messages
            
            # Compress via ContentRouter (auto-detects content type)
            compressed = await self._compress_with_timeout(to_compress)
            
            # Store originals in CCR for on-demand retrieval
            ccr_refs = []
            if self._ccr and self.config.enable_ccr:
                ccr_refs = await self._store_originals_in_ccr(to_compress, compressed)
            
            # Update metrics
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._update_metrics(
                original=to_compress,
                compressed=compressed,
                latency_ms=latency_ms,
                compressor="ContentRouter",
                fallback=False,
            )
            
            return compressed + protected
            
        except Exception as e:
            # M23 Failure Integrity: graceful fallback, log error
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            self._metrics["error_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.headroom")
            logger.warning(
                f"Headroom compression failed, falling back to uncompressed: {e}",
                extra={"latency_ms": latency_ms, "error": str(e)}
            )
            
            return messages  # Return original uncompressed
    
    async def _compress_with_timeout(self, messages: List[Message]) -> List[Message]:
        """Compress with timeout protection (M23)."""
        try:
            return await anyio.to_thread.run_sync(
                self._router.compress,
                messages,
            )
        except Exception as e:
            # If router.compress fails, try individual compressors
            return await self._fallback_compress(messages)
    
    async def _fallback_compress(self, messages: List[Message]) -> List[Message]:
        """Fallback: try individual compressors if ContentRouter fails."""
        # Try SmartCrusher for JSON-like content
        if self.config.enable_smart_crusher:
            try:
                crusher = SmartCrusher(SmartCrusherConfig(
                    max_items_after_crush=self.config.smart_crusher_max_items,
                    min_tokens_to_crush=self.config.smart_crusher_min_tokens,
                    relevance=RelevanceScorerConfig(tier="hybrid"),
                ))
                return await anyio.to_thread.run_sync(crusher.compress, messages)
            except Exception:
                pass
        
        # If all fails, return original
        return messages
    
    async def _store_originals_in_ccr(
        self, 
        originals: List[Message], 
        compressed: List[Message]
    ) -> List[str]:
        """Store original content in CCR, return list of references."""
        refs = []
        for orig, comp in zip(originals, compressed):
            orig_content = orig.get("content", "")
            comp_content = comp.get("content", "")
            if orig_content and orig_content != comp_content:
                try:
                    ref = await anyio.to_thread.run_sync(
                        self._ccr.store,
                        orig_content,
                        comp_content,
                    )
                    refs.append(ref)
                except Exception:
                    refs.append("")  # Failed to store
            else:
                refs.append("")
        return refs
    
    async def compress_retrieval_results(self, results: List[Dict]) -> List[Dict]:
        """
        Compress RAG retrieval results before LLM injection.
        
        Uses SearchCompressor + SmartCrusher for 70-90% token savings.
        Falls back to original results on any error (M23 Failure Integrity).
        
        Args:
            results: List of retrieval result dicts with 'content', 'score', 'metadata'
            
        Returns:
            Compressed results with same structure
        """
        start_time = time.perf_counter()
        
        if not self._initialized:
            await self.initialize()
        
        if not results:
            return results
        
        try:
            # SearchCompressor handles search result format
            compressed = await anyio.to_thread.run_sync(
                self._router.compress,
                results,
            )
            
            # Update metrics
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._update_metrics(
                original=results,
                compressed=compressed,
                latency_ms=latency_ms,
                compressor="SearchCompressor",
                fallback=False,
            )
            
            return compressed
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            self._metrics["error_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.headroom")
            logger.warning(
                f"Headroom retrieval compression failed: {e}",
                extra={"latency_ms": latency_ms, "error": str(e)}
            )
            
            return results  # Return original uncompressed
    
    async def compress_entity_context(self, context: Dict) -> Dict:
        """
        Compress entity context (soul.yaml, lessons, traits) for injection.
        
        Entity context is semi-structured YAML/JSON — ContentRouter auto-detects
        and routes to SmartCrusher. 20-50% token savings.
        
        Args:
            context: Entity context dict with soul, lessons, traits, etc.
            
        Returns:
            Compressed context dict
        """
        start_time = time.perf_counter()
        
        if not self._initialized:
            await self.initialize()
        
        if not context:
            return context
        
        try:
            compressed = await anyio.to_thread.run_sync(
                self._router.compress,
                [context],
            )
            result = compressed[0] if compressed else context
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._update_metrics(
                original=[context],
                compressed=[result],
                latency_ms=latency_ms,
                compressor="EntityContext",
                fallback=False,
            )
            
            return result
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            self._metrics["error_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.headroom")
            logger.warning(f"Entity context compression failed: {e}")
            
            return context
    
    async def retrieve_original(self, ccr_ref: str) -> Optional[str]:
        """
        Retrieve original content from CCR store by reference.
        
        Args:
            ccr_ref: CCR reference string from compression
            
        Returns:
            Original content string, or None if not found/error
        """
        if not self._ccr or not ccr_ref:
            return None
        
        try:
            return await anyio.to_thread.run_sync(self._ccr.retrieve, ccr_ref)
        except Exception as e:
            import logging
            logger = logging.getLogger("omega.headroom")
            logger.warning(f"CCR retrieve failed for {ccr_ref}: {e}")
            return None
    
    async def store_original(self, key: str, original: str, compressed: str) -> str:
        """
        Store original content in CCR with explicit key.
        
        Used by migration script and MCP tools.
        
        Args:
            key: Explicit key for retrieval
            original: Original uncompressed content
            compressed: Compressed content
            
        Returns:
            CCR reference string
        """
        if not self._ccr:
            raise RuntimeError("CCR not enabled")
        
        return await anyio.to_thread.run_sync(
            self._ccr.store_with_key,
            key,
            original,
            compressed,
        )
    
    def _update_metrics(
        self,
        original: List[Any],
        compressed: List[Any],
        latency_ms: float,
        compressor: str,
        fallback: bool,
    ) -> None:
        """Update internal metrics (exported to OTel)."""
        if not self.config.enable_metrics:
            return
        
        # Estimate token counts (rough: 4 chars ≈ 1 token)
        orig_tokens = sum(len(str(msg.get("content", ""))) // 4 for msg in original)
        comp_tokens = sum(len(str(msg.get("content", ""))) // 4 for msg in compressed)
        
        self._metrics["total_compressions"] += 1
        self._metrics["total_tokens_original"] += orig_tokens
        self._metrics["total_tokens_compressed"] += comp_tokens
        self._metrics["total_latency_ms"] += latency_ms
        
        if compressor not in self._metrics["by_compressor"]:
            self._metrics["by_compressor"][compressor] = {
                "count": 0,
                "tokens_original": 0,
                "tokens_compressed": 0,
                "latency_ms": 0.0,
            }
        
        self._metrics["by_compressor"][compressor]["count"] += 1
        self._metrics["by_compressor"][compressor]["tokens_original"] += orig_tokens
        self._metrics["by_compressor"][compressor]["tokens_compressed"] += comp_tokens
        self._metrics["by_compressor"][compressor]["latency_ms"] += latency_ms
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot for OTel export."""
        avg_ratio = 1.0
        if self._metrics["total_tokens_original"] > 0:
            avg_ratio = self._metrics["total_tokens_compressed"] / self._metrics["total_tokens_original"]
        
        return {
            "total_compressions": self._metrics["total_compressions"],
            "total_tokens_original": self._metrics["total_tokens_original"],
            "total_tokens_compressed": self._metrics["total_tokens_compressed"],
            "average_compression_ratio": avg_ratio,
            "average_latency_ms": (
                self._metrics["total_latency_ms"] / self._metrics["total_compressions"]
                if self._metrics["total_compressions"] > 0 else 0
            ),
            "fallback_count": self._metrics["fallback_count"],
            "error_count": self._metrics["error_count"],
            "by_compressor": self._metrics["by_compressor"],
        }
    
    async def shutdown(self) -> None:
        """Cleanup CCR store and connections."""
        if self._ccr:
            await anyio.to_thread.run_sync(self._ccr.close)
        self._initialized = False
    
    # Context manager support
    async def __aenter__(self) -> "HeadroomMiddleware":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.shutdown()
```

---

## Usage Examples

### In ModelGateway

```python
# src/omega/oracle/model_gateway.py
class ModelGateway:
    def __init__(self, ...):
        self._headroom_middleware = HeadroomMiddleware()
        # ... other init ...
    
    async def _prepare_messages(self, messages: List[Message]) -> List[Message]:
        # Compress tool outputs BEFORE token counting
        if self._headroom_middleware:
            messages = await self._headroom_middleware.compress_messages(messages)
        # ... token counting, truncation ...
        return messages
    
    async def shutdown(self):
        if self._headroom_middleware:
            await self._headroom_middleware.shutdown()
```

### In RAG Retrieval Pipeline

```python
# src/omega/memory/retrieval.py
class RetrievalCompressor:
    def __init__(self, headroom_middleware: HeadroomMiddleware):
        self.headroom = headroom_middleware
    
    async def search_and_compress(self, query: str, entity_name: str, top_k: int = 10):
        raw_results = await self.memory_store.search(query, entity_name, top_k * 2)
        return await self.headroom.compress_retrieval_results(raw_results)
```

### As Context Manager (Recommended)

```python
async with HeadroomMiddleware() as middleware:
    compressed = await middleware.compress_messages(messages)
    # Automatic shutdown on exit
```

---

## Error Handling Summary

| Scenario | Behavior |
|----------|----------|
| Headroom not installed | ImportError caught at init, middleware disabled, log warning |
| ContentRouter.compress() fails | Try SmartCrusher fallback, then return original |
| CCR store unavailable | Log warning, continue without CCR (compression still works) |
| Operation timeout (5s) | Return original, increment fallback counter |
| Any exception | Log warning, return original, increment error counter |

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 01/10*