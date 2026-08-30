<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Entity Context Compression — Soul/Lessons/Traits

**File**: `src/omega/entities/context_compressor.py` (new)  
**Section**: 06 of 10  
**Priority**: P2 — Entity context compression (20-50% savings)  

---

## Problem: Entity Context Overhead

Entities (Kali, Ma'at, Lilith, etc.) inject their full context (soul.yaml, lessons, traits, mandates) into every request. For entities with rich souls, this can be 5K-20K tokens per request.

**Headroom Solution**: Compress entity context with ContentRouter (SmartCrusher) while protecting identity-critical fields.

---

## EntityContextCompressor Class

```python
"""
Entity Context Compression via Headroom.

Compresses entity context (soul.yaml, lessons, traits) for injection.
Entity context is semi-structured YAML/JSON — ContentRouter auto-detects
and routes to SmartCrusher. 20-50% token savings.

Mandate Compliance:
- M1 AnyIO Absolute: All async uses anyio.to_thread.run_sync()
- M7 Local-First: Headroom runs locally
- M11 Soul Integrity: Protect identity, role, key mandates (never compress)
- M18 Token Efficiency: 20-50% token reduction on entity context
- M23 Failure Integrity: Graceful fallback to uncompressed
"""

from __future__ import annotations

import anyio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from headroom import ContentRouter, ContentRouterConfig
from headroom.transforms import SmartCrusher, SmartCrusherConfig
from headroom.transforms.relevance import RelevanceScorerConfig

from omega.oracle.middleware.headroom import HeadroomMiddleware


@dataclass
class EntityContextCompressorConfig:
    """Configuration for entity context compression."""
    
    # Compressor settings
    max_items_after_crush: int = 20
    min_tokens_to_crush: int = 150
    relevance_tier: str = "hybrid"
    hybrid_alpha: float = 0.5
    
    # Protection: fields that are NEVER compressed (M11 Soul Integrity)
    protected_fields: Set[str] = field(default_factory=lambda: {
        "identity",           # Entity name, archetype
        "role",              # Node assignment, purpose
        "mandates",          # Sovereign mandates (M1-M27)
        "core_principles",   # L3 universal principles
        "archetype",         # Tarot/archetypal identity
        "node",              # N1-N10 assignment
    })
    
    # Fields to compress aggressively
    compressible_fields: Set[str] = field(default_factory=lambda: {
        "lessons",           # L1/L2 insights (can be summarized)
        "traits",            # Personality traits (verbose)
        "history",           # Session history (redundant with MemoryStore)
        "preferences",       # Model/tool preferences
        "metadata",          # Timestamps, version info
    })
    
    # Compression behavior
    protect_recent_lessons: int = 5      # Never compress 5 most recent lessons
    summarize_lessons: bool = True       # L1→L2 summarization for old lessons
    max_trait_length: int = 200          # Truncate trait descriptions
    
    # Timeout
    operation_timeout_seconds: float = 5.0


class EntityContextCompressor:
    """
    Compresses entity context for injection into LLM context.
    
    Usage:
        compressor = EntityContextCompressor(config)
        compressed_context = await compressor.compress_entity_context(full_context)
        # Inject compressed_context instead of full_context
    """
    
    def __init__(
        self, 
        config: Optional[EntityContextCompressorConfig] = None,
        headroom_middleware: Optional[HeadroomMiddleware] = None,
    ):
        self.config = config or EntityContextCompressorConfig()
        self._headroom = headroom_middleware
        
        # Build ContentRouter for entity context
        self._router = ContentRouter(ContentRouterConfig(
            enable_smart_crusher=True,
            enable_log_compressor=False,
            enable_search_compressor=False,
            enable_code_aware=False,
            enable_kompress=False,
            enable_tabular_compressor=False,
            enable_html_extractor=False,
            smart_crusher=SmartCrusher(SmartCrusherConfig(
                max_items_after_crush=self.config.max_items_after_crush,
                min_tokens_to_crush=self.config.min_tokens_to_crush,
                relevance=RelevanceScorerConfig(
                    tier=self.config.relevance_tier,
                    embedding_model="all-MiniLM-L6-v2",
                    hybrid_alpha=self.config.hybrid_alpha,
                ),
            )),
            min_chars_for_block_compression=300,
            min_ratio_aggressive=0.65,
        ))
        
        self._metrics = {
            "total_compressions": 0,
            "total_tokens_original": 0,
            "total_tokens_compressed": 0,
            "total_latency_ms": 0.0,
            "fallback_count": 0,
        }
    
    async def compress_entity_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress entity context dict.
        
        Args:
            context: Full entity context with identity, role, mandates, lessons, traits, etc.
            
        Returns:
            Compressed context with protected fields intact, compressible fields reduced
        """
        start_time = time.perf_counter()
        
        if not context:
            return context
        
        try:
            # 1. Separate protected and compressible fields
            protected = {}
            compressible = {}
            
            for key, value in context.items():
                if key in self.config.protected_fields:
                    protected[key] = value
                elif key in self.config.compressible_fields:
                    compressible[key] = value
                else:
                    # Unknown field: protect by default
                    protected[key] = value
            
            # 2. Pre-process compressible fields
            compressible = self._preprocess_compressible(compressible)
            
            # 3. Compress compressible portion via ContentRouter
            if compressible:
                compressed = await anyio.to_thread.run_sync(
                    self._router.compress,
                    [compressible],
                )
                compressible = compressed[0] if compressed else compressible
            
            # 4. Merge protected + compressed
            result = {**protected, **compressible}
            
            # 5. Update metrics
            latency_ms = (time.perf_counter() - start_time) * 1000
            orig_tokens = self._estimate_tokens(context)
            comp_tokens = self._estimate_tokens(result)
            
            self._metrics["total_compressions"] += 1
            self._metrics["total_tokens_original"] += orig_tokens
            self._metrics["total_tokens_compressed"] += comp_tokens
            self._metrics["total_latency_ms"] += latency_ms
            
            return result
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._metrics["fallback_count"] += 1
            
            import logging
            logger = logging.getLogger("omega.entities.context_compressor")
            logger.warning(f"Entity context compression failed: {e}")
            
            return context  # Fallback to uncompressed
    
    def _preprocess_compressible(self, compressible: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process compressible fields before ContentRouter."""
        result = {}
        
        for key, value in compressible.items():
            if key == "lessons" and isinstance(value, list):
                result[key] = self._process_lessons(value)
            elif key == "traits" and isinstance(value, dict):
                result[key] = self._process_traits(value)
            elif key == "history" and isinstance(value, list):
                result[key] = self._process_history(value)
            else:
                result[key] = value
        
        return result
    
    def _process_lessons(self, lessons: List[Dict]) -> List[Dict]:
        """Process lessons: protect recent, summarize old."""
        if not lessons:
            return lessons
        
        protected_count = min(self.config.protect_recent_lessons, len(lessons))
        recent = lessons[-protected_count:] if protected_count > 0 else []
        old = lessons[:-protected_count] if protected_count > 0 else lessons
        
        processed = []
        
        # Keep recent lessons intact
        processed.extend(recent)
        
        # Summarize old lessons if enabled
        if self.config.summarize_lessons and old:
            for lesson in old:
                # Keep L3 (universal principle), summarize L1/L2
                summarized = {
                    "principle": lesson.get("principle", ""),  # L3 - always keep
                    "insight_summary": self._summarize_text(
                        lesson.get("insight", ""), 
                        max_length=200
                    ),  # L2 - summarized
                    "narrative_ref": lesson.get("narrative", "")[:100] + "...",  # L1 - reference only
                    "timestamp": lesson.get("timestamp", ""),
                    "summarized": True,
                }
                processed.append(summarized)
        else:
            processed.extend(old)
        
        return processed
    
    def _process_traits(self, traits: Dict[str, Any]) -> Dict[str, Any]:
        """Process traits: truncate long descriptions."""
        result = {}
        for key, value in traits.items():
            if isinstance(value, str) and len(value) > self.config.max_trait_length:
                result[key] = value[:self.config.max_trait_length] + "..."
            else:
                result[key] = value
        return result
    
    def _process_history(self, history: List[Dict]) -> List[Dict]:
        """Process history: keep only essential metadata."""
        # Keep last 10 sessions with minimal info
        return [
            {
                "session_id": h.get("session_id", ""),
                "timestamp": h.get("timestamp", ""),
                "summary": h.get("summary", "")[:200],
            }
            for h in history[-10:]
        ]
    
    def _summarize_text(self, text: str, max_length: int = 200) -> str:
        """Simple extractive summarization (first N chars)."""
        if not text or len(text) <= max_length:
            return text
        # Find sentence boundary near max_length
        truncated = text[:max_length]
        last_period = truncated.rfind(".")
        if last_period > max_length * 0.5:
            return truncated[:last_period + 1]
        return truncated + "..."
    
    def _estimate_tokens(self, obj: Any) -> int:
        """Rough token estimation: 4 chars ≈ 1 token."""
        import json
        return len(json.dumps(obj, default=str)) // 4
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for OTel export."""
        avg_ratio = 1.0
        if self._metrics["total_tokens_original"] > 0:
            avg_ratio = self._metrics["total_tokens_compressed"] / self._metrics["total_tokens_original"]
        
        return {
            "total_compressions": self._metrics["total_compressions"],
            "avg_compression_ratio": avg_ratio,
            "avg_latency_ms": (
                self._metrics["total_latency_ms"] / self._metrics["total_compressions"]
                if self._metrics["total_compressions"] > 0 else 0
            ),
            "fallback_count": self._metrics["fallback_count"],
        }


# Integration with EntityRegistry
#
# In src/omega/entities/registry.py:
#
# class EntityRegistry:
#     def __init__(self, ..., headroom_middleware: Optional[HeadroomMiddleware] = None):
#         # ... existing init ...
#         self._context_compressor = EntityContextCompressor(
#             headroom_middleware=headroom_middleware
#         )
#     
#     async def get_context(self, entity_name: str, compress: bool = True) -> Dict[str, Any]:
#         """Get entity context, optionally compressed."""
#         context = await self._load_full_context(entity_name)
#         
#         if compress and self._context_compressor:
#             context = await self._context_compressor.compress_entity_context(context)
#         
#         return context
#     
#     async def get_context_for_injection(self, entity_name: str) -> Dict[str, Any]:
#         """Get context optimized for LLM injection (always compressed)."""
#         return await self.get_context(entity_name, compress=True)
```

---

## Protected Fields Detail (M11 Soul Integrity)

```python
# These fields are NEVER compressed — they define sovereign identity

PROTECTED_FIELDS = {
    # Identity (immutable)
    "name",              # "kali", "maat", "lilith", etc.
    "archetype",         # "The Architect", "The Builder", "The Runner"
    "node",              # "N1", "N3", "N7", etc.
    "tier",              # "oversoul", "pillar_keeper", "entity"
    
    # Role & Purpose (immutable)
    "role",              # "oversight", "build", "run", "research", "debug", "audit"
    "purpose",           # One-sentence mission statement
    "mandates",          # Applicable sovereign mandates (subset of M1-M27)
    "core_principles",   # L3 universal principles from soul distillation
    
    # Configuration (semi-immutable)
    "model",             # Primary model assignment
    "mode",              # "primary" | "subagent"
    "permissions",       # Tool/permission restrictions
    
    # Soul Integrity (M11)
    "soul_version",      # Soul schema version
    "distillation_count", # Number of L1→L2→L3 cycles completed
}
```

---

## Compressible Fields Detail

```python
# These fields ARE compressed — they accumulate over time

COMPRESSIBLE_FIELDS = {
    # Lessons (grow unbounded)
    "lessons": {
        "structure": [
            {"narrative": "L1 - what happened", "insight": "L2 - what it means", 
             "principle": "L3 - universal truth", "timestamp": "ISO8601"}
        ],
        "compression": "Protect recent 5, summarize older (keep L3, truncate L1/L2)",
        "expected_savings": "40-60%",
    },
    
    # Traits (verbose personality)
    "traits": {
        "structure": {"analytical": "Deep analysis...", "precise": "Exact...", ...},
        "compression": "Truncate descriptions to 200 chars",
        "expected_savings": "30-50%",
    },
    
    # History (redundant with MemoryStore)
    "history": {
        "structure": [{"session_id": "...", "summary": "...", "timestamp": "..."}],
        "compression": "Keep last 10 sessions, minimal metadata only",
        "expected_savings": "70-90%",
    },
    
    # Preferences (stable, verbose)
    "preferences": {
        "structure": {"model": "...", "tools": [...], "style": "..."},
        "compression": "SmartCrusher on JSON",
        "expected_savings": "50-70%",
    },
    
    # Metadata (timestamps, versions)
    "metadata": {
        "structure": {"created": "...", "updated": "...", "version": "..."},
        "compression": "Keep only essential",
        "expected_savings": "80-95%",
    },
}
```

---

## Expected Compression Results

| Entity | Context Size | Compressed | Reduction | Protected |
|--------|--------------|------------|-----------|-----------|
| Kali (oversoul) | 15,000 tokens | 8,000 | 46.7% | 2,500 tokens |
| Ma'at (build) | 12,000 tokens | 6,500 | 45.8% | 2,000 tokens |
| Lilith (run) | 10,000 tokens | 5,500 | 45.0% | 1,800 tokens |
| Researcher | 8,000 tokens | 4,500 | 43.8% | 1,500 tokens |
| Node (debug) | 5,000 tokens | 3,000 | 40.0% | 1,200 tokens |
| Verity (audit) | 6,000 tokens | 3,500 | 41.7% | 1,500 tokens |

---

## Configuration for Entity Context

```yaml
# config/headroom.yaml — Entity Context section
headroom:
  omega:
    entity_context:
      compress_soul: true
      compress_lessons: true
      max_items_after_crush: 20
      min_tokens_to_crush: 150
      protect_recent_lessons: 5
      summarize_lessons: true
      max_trait_length: 200
```

---

## Soul Integrity Guarantee

**M11 Compliance**: The compressor NEVER touches protected fields. This is enforced by:
1. Explicit `protected_fields` set in config
2. Pre-processing separation before ContentRouter
3. Unit tests verifying protected fields unchanged
4. Integration tests verifying identity persistence

```python
# Test verifying M11 compliance
@pytest.mark.asyncio
async def test_entity_context_protects_identity():
    compressor = EntityContextCompressor()
    
    context = {
        "name": "kali",
        "archetype": "The Architect",
        "node": "N1",
        "mandates": ["M1", "M2", "M7"],
        "core_principles": ["Sovereignty requires local-first"],
        "lessons": [{"principle": "Test", "insight": "x" * 1000}] * 20,
        "traits": {"analytical": "x" * 500},
    }
    
    compressed = await compressor.compress_entity_context(context)
    
    # Protected fields MUST be identical
    assert compressed["name"] == "kali"
    assert compressed["archetype"] == "The Architect"
    assert compressed["node"] == "N1"
    assert compressed["mandates"] == ["M1", "M2", "M7"]
    assert compressed["core_principles"] == ["Sovereignty requires local-first"]
    
    # Compressible fields SHOULD be reduced
    assert len(str(compressed["lessons"])) < len(str(context["lessons"]))
    assert len(str(compressed["traits"])) < len(str(context["traits"]))
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 06/10*