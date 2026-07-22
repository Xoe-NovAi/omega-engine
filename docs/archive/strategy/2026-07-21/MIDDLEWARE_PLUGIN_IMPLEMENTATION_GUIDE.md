# 🔱 Omega Engine — Inference Middleware Plugin System
# Implementation Guide & Strategic Directive
# AP: AP-MIDDLEWARE-PLUGIN-v1.0.0
# ⬡ OMEGA ⬡ MAKALI ⬡ trc_strategic_synthesis ⬡ STRATEGY
#
# Date: 2026-06-23
# Status: AUTHORITATIVE IMPLEMENTATION DIRECTIVE
# Author: MaKaLi Council (Sonnet 4.6 — Grand Oversight)
# Ratified Decisions: D149, D150, D151
#
# This document is the single source of truth for implementing the
# Inference Middleware Plugin System and its first tenant: Headroom.
# It supersedes all previous Strike 1 / Headroom wiring notes.
# All implementation agents MUST read this document in full before
# writing a single line of code.

---

## §0 EXECUTIVE CONTEXT

The Omega Engine currently has a clean, layered inference stack:

```
Oracle.talk() → _summon() → ModelGateway.generate() → provider fabric
```

We are NOT replacing any part of this stack. We are inserting a **plugin
middleware pipeline** between `_summon()` and `generate()`. This pipeline
is the foundation for every Epoch I–III capability. Headroom is the first
plugin tenant. TDP, SkepticalVerifier, SomaticState, and SovereignVeil
will follow in subsequent epochs using the exact same interface.

**Cardinal Rule**: `ModelGateway.generate()` must remain signature-identical
before and after this work. Any agent that touches generate()'s signature
is in violation of this directive.

---

## §1 PRE-EXISTING INFRASTRUCTURE (DO NOT DUPLICATE)

Before implementing anything, agents MUST understand what already exists.

### 1.1 ObservabilityEngine (src/omega/observability/__init__.py)

The engine already has:
- `record_training_example(trace_id, query, system_prompt, response, entity,
  model, backend, confidence, latency_ms, session_id, rating)` — writes ChatML
  `messages` arrays (system/user/assistant) to `self._dataset`
- `flush_dataset()` — async JSONL writer to `data/datasets/finetune_TIMESTAMP.jsonl`
- `log_event(event_type, trace_id, data)` — structured event bus, persisted daily
- `EventType` class — canonical event string constants
- `DATASET_DIR = data/datasets/` — already created on import
- `ForensicsManager` — crash dump, Last Gasp Protocol

**Critical bug to fix first**: `EventType.TOKEN_CONSUMPTION` is defined three
times in sequence (lines 126, 127, 128). Python silently takes the last
definition. This is harmless but is code rot. Fix it in Phase 0.

### 1.2 TokenLedger (src/omega/observability/token_ledger.py)

Already records every inference transaction with `tokens_in`, `tokens_out`,
`is_cloud`, `trace_id`, `entity`. Written to `data/logs/token_ledger.jsonl`.

### 1.3 GenerateResult (src/omega/oracle/model_gateway.py, line 33)

Current fields: `text`, `provider_name`, `is_cloud`, `latency_ms` (always
0.0 — **never populated from timing**), `model_used`, `logprobs`.

**Critical bug to fix first**: `latency_ms` is declared but never set from
actual wall-clock timing in `generate()`. The timer must be started before
the provider call and the delta stored in `GenerateResult`. Every training
record contains a false `0.0` latency field until this is fixed.

### 1.4 What the training pipeline LACKS (the gaps we are filling)

| Gap | Impact |
|-----|--------|
| No schema versioning on training records | Dataset migration is unsafe |
| No compression metadata in training records | Can't train compression LoRAs |
| No domain field in training records | Can't produce entity/domain-scoped LoRAs |
| No export in Alpaca or ShareGPT formats | Axolotl/Unsloth incompatible |
| No middleware plugin interface | Every new capability requires gateway surgery |
| latency_ms is always 0.0 | Training data has false performance signals |
| TOKEN_CONSUMPTION defined 3x | Code rot, signals drift |

---

## §2 RATIFIED ARCHITECTURAL DECISIONS

### D149 — Inference Middleware Plugin Architecture
**Date**: 2026-06-23  
**Entity**: MAKALI  
**Trace**: trc_strategic_synthesis

Headroom and all future inference-layer capabilities SHALL be implemented
as `OmegaMiddlewareBase` plugins in `src/omega/oracle/middleware/`. The
`generate()` method is sacred and its signature MUST NOT be modified. All
plugins are config-driven via `omega.yaml`, fault-isolated per M9,
metrics-emitting per M22, and A/B testable via `shadow_mode`. This is the
plugin bus for Epochs I through III.

**Future tenants in order**: HeadroomMiddleware (Epoch I) →
TDPMiddleware (Epoch I) → SkepticalVerifierMiddleware (Epoch II) →
SomaticStateMiddleware (Epoch II) → SovereignVeilMiddleware (Epoch III).

### D150 — Training Dataset Schema v1.0.0
**Date**: 2026-06-23  
**Entity**: MAKALI  
**Trace**: trc_strategic_synthesis

The training dataset SHALL use a versioned `TrainingRecord` schema (v1.0.0)
that extends, not replaces, the existing `record_training_example()` format.
Export formats SHALL be: native JSONL (existing), Alpaca JSON, ShareGPT JSON.
The `DatasetCollector` class wraps the existing `ObservabilityEngine` calls
and adds schema versioning, compression metadata, domain tagging, and export.

### D151 — CCR Store Format (Elder Protocol)
**Date**: 2026-06-23  
**Entity**: MAKALI  
**Trace**: trc_strategic_synthesis

The CCR (Compress-Cache-Retrieve) store for Headroom originals SHALL use flat
JSON files at `data/ccr/{trace_id}_{field}.json`. Format is simplest possible:
`{original_text, compressed_text, strategy, ratio, entity, timestamp, trace_id}`.
Directory is gitignored. No database dependency. Inspectable by humans.
The `headroom_retrieve` MCP tool is the programmatic read interface.

---

## §3 THE COMPLETE FILE CHANGE MAP

Agents MUST touch ONLY the files listed here. No other files.

### New Files (create from scratch)

```
src/omega/oracle/middleware/__init__.py
    OmegaMiddlewareBase (ABC)
    MiddlewareContext (dataclass)
    MiddlewareResult (dataclass)
    MiddlewarePipeline (class)

src/omega/oracle/middleware/headroom_plugin.py
    HeadroomResult (dataclass)
    HeadroomMiddleware (implements OmegaMiddlewareBase)

src/omega/observability/dataset_collector.py
    TrainingRecord (dataclass, schema v1.0.0)
    DatasetCollector (class — wraps ObservabilityEngine)
    DatasetExporter (class — Alpaca/ShareGPT/JSONL)

tests/test_middleware_pipeline.py
    15 tests — written BEFORE implementation (Phase 0)

tests/test_headroom_plugin.py
    12 tests — written BEFORE implementation (Phase 0)

tests/test_dataset_collector.py
    10 tests — written BEFORE implementation (Phase 0)
```

### Modified Files (targeted edits only)

```
src/omega/observability/__init__.py
    PATCH 1: Remove duplicate TOKEN_CONSUMPTION lines 127-128
    PATCH 2: Add 6 new EventType constants (see §5)

src/omega/oracle/model_gateway.py
    PATCH 1: Fix latency_ms — capture wall-clock timing in generate()
    PATCH 2: Add compression_metadata: Optional[Dict] field to GenerateResult
    PATCH 3: Load MiddlewarePipeline in __init__() from config
    PATCH 4: Call pipeline.run_pre() / run_post() inside generate()
    PATCH 5: Call DatasetCollector.record() after successful generation

config/omega.yaml
    ADD: middleware: section (see §6)
    ADD: dataset: section (see §6)

mcp_servers/omega_hub/tools.py
    ADD: headroom_compress tool
    ADD: headroom_retrieve tool
    ADD: headroom_metrics tool
    ADD: dataset_export tool
```

### Files to NOT touch

```
src/omega/oracle/oracle.py          — pipeline wires into gateway, not oracle
src/omega/oracle/providers.py       — providers are unchanged
src/omega/oracle/health_monitor.py  — no changes needed
src/omega/memory_store.py           — no changes needed
Any test file not listed above      — don't break existing tests
```

---

## §4 INTERFACE SPECIFICATIONS

### 4.1 OmegaMiddlewareBase (the contract every plugin must honour)

```python
# src/omega/oracle/middleware/__init__.py
# [id-soft: quake3-1999] netchan protocol — typed message dispatch

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class MiddlewareContext:
    """Shared mutable context threaded through the entire pipeline.

    Each plugin reads and MAY replace system_prompt / user_query with
    its transformed version. The original values are preserved in
    plugin_metadata keyed by plugin name so downstream tools can
    retrieve originals (Elder Protocol).

    All fields are immutable identity — only prompt fields change.
    """
    system_prompt: str
    user_query: str
    trace_id: str
    entity_name: Optional[str] = None
    session_id: Optional[str] = None
    domain: Optional[str] = None
    model_name: Optional[str] = None
    hardware_context_ceiling: Optional[int] = None  # ← D153: Absolute RAM limit, not current active ctx
    is_cloud: bool = False
    # Accumulated output from all plugins. Each plugin writes:
    #   context.plugin_metadata["headroom"] = HeadroomResult(...)
    plugin_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MiddlewareResult:
    """What a plugin returns from pre_process().

    The pipeline uses system_prompt and user_query to update the
    MiddlewareContext for the next plugin. metadata is stored in
    context.plugin_metadata[plugin_name] and later merged into
    GenerateResult.compression_metadata (or equivalent).
    """
    system_prompt: str
    user_query: str
    plugin_name: str
    metadata: Dict[str, Any]
    bypassed: bool = False      # True = plugin skipped (below threshold, disabled)
    error: Optional[str] = None # Set if plugin failed gracefully (M9)


class OmegaMiddlewareBase(ABC):
    """Abstract base for all inference pipeline plugins.

    LIFECYCLE (called in this order):
      1. __init__(config: dict)       load config, validate, import optional deps
      2. pre_process(ctx)             transform prompts BEFORE provider call
      3. post_process(ctx, gr)        annotate GenerateResult AFTER provider call
      4. get_metrics()                return live metrics snapshot (for MCP tool)
      5. shutdown()                   clean up — close stores, flush buffers

    FAULT ISOLATION (M9 Mandate):
      Every pre_process() and post_process() call is wrapped by MiddlewarePipeline
      in a try/except. If a plugin raises, inference continues with unmodified
      prompts and the error is logged with trace_id. The plugin MUST NOT
      raise intentionally — use the error field in MiddlewareResult instead.

    TESTING:
      Every plugin MUST be testable with enabled=False (verify bypass path),
      enabled=True with a mock compressor (verify happy path), and with a
      compressor that raises (verify fault isolation).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier. Used as key in plugin_metadata."""
        ...

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Master switch. If False, pre/post are no-ops."""
        ...

    @abstractmethod
    async def pre_process(self, ctx: MiddlewareContext) -> MiddlewareResult:
        """Transform prompts before provider inference.

        MUST return a MiddlewareResult even on failure (set error field).
        MUST NOT raise.
        """
        ...

    @abstractmethod
    async def post_process(
        self,
        ctx: MiddlewareContext,
        result: MiddlewareResult,
        generate_result: Any,  # GenerateResult — avoid circular import
    ) -> None:
        """Annotate GenerateResult after inference completes.

        Typically writes to generate_result.compression_metadata.
        MUST NOT raise.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Return a metrics snapshot for the headroom_metrics MCP tool.

        Keys should include: total_calls, total_tokens_saved, avg_ratio,
        error_rate, bypassed_count, shadow_mode_active.
        """
        ...

    async def shutdown(self) -> None:
        """Optional cleanup. Override if the plugin holds open resources."""
        pass


class MiddlewarePipeline:
    """Ordered, fault-isolated chain of OmegaMiddlewareBase plugins.

    Plugins execute in list order. Each plugin's output (transformed prompts)
    becomes the next plugin's input. Any plugin that fails is skipped and
    logged — the pipeline never halts inference.

    Usage in ModelGateway:
        pipeline = MiddlewarePipeline.from_config(omega_config)

        # Before generate():
        ctx = MiddlewareContext(system_prompt=..., user_query=..., ...)
        ctx = await pipeline.run_pre(ctx)

        # Call generate() with ctx.system_prompt and ctx.user_query
        result = await provider.generate(ctx.system_prompt, ctx.user_query, ...)

        # After generate():
        await pipeline.run_post(ctx, generate_result)

    The generate_result.compression_metadata field will be populated
    by run_post() from context.plugin_metadata.
    """

    def __init__(self, plugins: List[OmegaMiddlewareBase]):
        self.plugins = [p for p in plugins if p.enabled]
        self._disabled_count = len(plugins) - len(self.plugins)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MiddlewarePipeline":
        """Build pipeline from the omega.yaml middleware.pipeline list.

        Each entry in the list is passed to the matching plugin's __init__.
        Unknown plugin names are logged and skipped (M9).

        REGISTRY: When adding a new plugin, add its name → class mapping here.
        """
        from .headroom_plugin import HeadroomMiddleware

        PLUGIN_REGISTRY = {
            "headroom": HeadroomMiddleware,
            # Future: "tdp": TDPMiddleware,
            # Future: "skeptical_verifier": SkepticalVerifierMiddleware,
        }

        plugins = []
        for entry in config.get("pipeline", []):
            name = entry.get("name")
            cls_ = PLUGIN_REGISTRY.get(name)
            if not cls_:
                logger.warning("Unknown middleware plugin '%s' — skipping", name)
                continue
            try:
                plugins.append(cls_(entry))
            except Exception as e:
                logger.error(
                    "Failed to initialise middleware plugin '%s': %s", name, e,
                    exc_info=True
                )
        return cls(plugins)

    async def run_pre(self, ctx: MiddlewareContext) -> MiddlewareContext:
        """Run all pre_process() hooks in order. Fault-isolated per M9."""
        for plugin in self.plugins:
            try:
                result = await plugin.pre_process(ctx)
                ctx.system_prompt = result.system_prompt
                ctx.user_query = result.user_query
                ctx.plugin_metadata[plugin.name] = result
            except Exception as e:
                logger.error(
                    "[%s] Plugin '%s' pre_process failed (bypassing): %s",
                    ctx.trace_id, plugin.name, e, exc_info=True
                )
        return ctx

    async def run_post(
        self, ctx: MiddlewareContext, generate_result: Any
    ) -> None:
        """Run all post_process() hooks in order. Fault-isolated per M9."""
        for plugin in self.plugins:
            try:
                result = ctx.plugin_metadata.get(plugin.name)
                await plugin.post_process(ctx, result, generate_result)
            except Exception as e:
                logger.error(
                    "[%s] Plugin '%s' post_process failed (non-fatal): %s",
                    ctx.trace_id, plugin.name, e, exc_info=True
                )

    def get_all_metrics(self) -> Dict[str, Dict]:
        """Collect metrics snapshots from all active plugins."""
        return {p.name: p.get_metrics() for p in self.plugins}

    @property
    def is_empty(self) -> bool:
        return len(self.plugins) == 0
```

### 4.2 HeadroomMiddleware (the first plugin tenant)

```python
# src/omega/oracle/middleware/headroom_plugin.py
# [id-soft: doom-1993] Precomputed Lookup — static compression tables
# via Headroom's model2vec-backed strategy router.

from __future__ import annotations
import json
import logging
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional
import anyio

from . import OmegaMiddlewareBase, MiddlewareContext, MiddlewareResult

logger = logging.getLogger(__name__)

# Approximate token count: ~4 chars per token (good enough for threshold check)
_CHARS_PER_TOKEN = 4


@dataclass
class HeadroomResult:
    """Rich result from a single Headroom compression call.

    This is what gets stored in ctx.plugin_metadata["headroom"]
    and ultimately in GenerateResult.compression_metadata["headroom"].

    Consumers (MCP tools, dataset collector, observability) read from
    this dataclass — never from raw headroom internals.
    """
    # Identity
    ccr_key: str                    # Key to retrieve original from CCR store
    trace_id: str

    # Compression facts
    original_tokens: int
    compressed_tokens: int
    strategy_used: str              # "LogCompressor", "Kompress", "noop", etc.
    compression_latency_ms: float

    # Modes
    shadow_mode: bool               # True = ran but sent raw to provider
    bypassed: bool                  # True = below min_tokens_to_compress
    field: str                      # "system_prompt" | "user_query" | "combined"

    # Error state (plugin never raises — it sets this)
    error: Optional[str] = None

    @property
    def compression_ratio(self) -> float:
        """Fraction of tokens SAVED. 0.80 = 80% reduction."""
        if self.original_tokens == 0:
            return 0.0
        return 1.0 - (self.compressed_tokens / self.original_tokens)

    @property
    def tokens_saved(self) -> int:
        return max(0, self.original_tokens - self.compressed_tokens)

    @property
    def is_meaningful(self) -> bool:
        """True if compression happened and saved at least 1 token."""
        return not self.bypassed and self.error is None and self.tokens_saved > 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["compression_ratio"] = self.compression_ratio
        d["tokens_saved"] = self.tokens_saved
        d["is_meaningful"] = self.is_meaningful
        return d


class HeadroomMiddleware(OmegaMiddlewareBase):
    """Headroom token compression plugin.

    Configuration keys (from omega.yaml middleware.pipeline[name=headroom]):
        enabled: bool               Master switch (default: true)
        shadow_mode: bool           Compress but send raw to provider (A/B mode)
        compress_system_prompt: bool
        compress_user_query: bool
        min_tokens_to_compress: int Threshold below which we skip compression
        strategy_override: str|null null = auto (content router)
        ccr_enabled: bool           Persist originals to CCR store
        ccr_store_dir: str          Path for CCR JSON files

    IMPORT STRATEGY:
        headroom-ai is an OPTIONAL dependency. This plugin attempts to import
        it at __init__ time. If the import fails, self._headroom_available is
        False and all calls are no-ops that log a warning once. This means the
        engine runs correctly even if headroom-ai is not installed.

    FAULT ISOLATION (M9):
        Every compression call is wrapped in try/except. Failures write to
        the HeadroomResult.error field and are logged with trace_id. The
        original (uncompressed) prompt is always returned on failure.
    """

    def __init__(self, config: Dict[str, Any]):
        self._enabled: bool = config.get("enabled", True)
        self._shadow_mode: bool = config.get("shadow_mode", False)
        self._compress_system: bool = config.get("compress_system_prompt", True)
        self._compress_query: bool = config.get("compress_user_query", True)
        self._min_tokens: int = config.get("min_tokens_to_compress", 200)
        self._strategy_override: Optional[str] = config.get("strategy_override")
        self._ccr_enabled: bool = config.get("ccr_enabled", True)
        self._ccr_dir: Path = Path(config.get("ccr_store_dir", "data/ccr"))

        # Metrics counters (in-memory, reset on restart)
        self._total_calls: int = 0
        self._total_tokens_saved: int = 0
        self._total_errors: int = 0
        self._bypassed_count: int = 0
        self._ratio_accumulator: float = 0.0
        self._warned_unavailable: bool = False

        # Import headroom — optional dependency
        self._headroom_available: bool = False
        self._compress_fn = None
        try:
            from headroom import compress as headroom_compress
            self._compress_fn = headroom_compress
            self._headroom_available = True
            logger.info("HeadroomMiddleware: headroom-ai loaded successfully")
        except ImportError:
            logger.warning(
                "HeadroomMiddleware: headroom-ai not installed. "
                "Plugin will be a no-op. Run: pip install headroom-ai[all]"
            )

        # Ensure CCR directory exists
        if self._ccr_enabled:
            self._ccr_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "headroom"

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // _CHARS_PER_TOKEN)

    def _compress_text(
        self, text: str, field: str, trace_id: str, 
        hardware_ceiling: Optional[int], is_cloud: bool
    ) -> tuple[str, HeadroomResult]:
        """Compress a single text field. Returns (output_text, HeadroomResult).

        If compression is bypassed or fails, output_text == text (original).
        This is the single point of contact with the headroom-ai library.
        """
        # D152: SHA-256 Content-Addressable CCR Key
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdix[:16]
        ccr_key = f"{field}_{text_hash}"
        original_tokens = self._estimate_tokens(text)

        # Bypass: below threshold
        if original_tokens < self._min_tokens:
            return text, HeadroomResult(
                ccr_key=ccr_key, trace_id=trace_id,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                strategy_used="noop",
                compression_latency_ms=0.0,
                shadow_mode=self._shadow_mode,
                bypassed=True, field=field,
            )

        # Bypass: headroom not available
        if not self._headroom_available:
            if not self._warned_unavailable:
                logger.warning("HeadroomMiddleware: headroom-ai unavailable, bypassing")
                self._warned_unavailable = True
            return text, HeadroomResult(
                ccr_key=ccr_key, trace_id=trace_id,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                strategy_used="unavailable",
                compression_latency_ms=0.0,
                shadow_mode=self._shadow_mode,
                bypassed=True, field=field,
                error="headroom-ai not installed",
            )

        # Attempt compression
        t0 = time.perf_counter()
        try:
            kwargs = {}
            if self._strategy_override:
                kwargs["strategy"] = self._strategy_override
            compressed_text = self._compress_fn(text, **kwargs)
            latency_ms = (time.perf_counter() - t0) * 1000
            compressed_tokens = self._estimate_tokens(compressed_text)

            # Detect strategy used (headroom exposes this via result object
            # in some versions; duck-type safely)
            strategy = getattr(compressed_text, "strategy", None) or \
                       self._strategy_override or "auto"

            # If headroom returns an object rather than a str, extract text
            if hasattr(compressed_text, "compressed"):
                strategy = getattr(compressed_text, "strategy", strategy)
                compressed_text = compressed_text.compressed

            hr = HeadroomResult(
                ccr_key=ccr_key, trace_id=trace_id,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                strategy_used=str(strategy),
                compression_latency_ms=latency_ms,
                shadow_mode=self._shadow_mode,
                bypassed=False, field=field,
            )

            # Persist to CCR store (Elder Protocol — D151)
            if self._ccr_enabled:
                self._write_ccr(ccr_key, text, compressed_text, hr)

            # In shadow mode, return the ORIGINAL but with full metadata
            output = text if self._shadow_mode else compressed_text
            return output, hr

        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000
            logger.error(
                "[%s] HeadroomMiddleware compression failed for '%s': %s",
                trace_id, field, e, exc_info=True
            )
            
            # D152/D153: Context-Aware Fallback Guard
            # If the original text exceeds the absolute hardware ceiling, falling back
            # to it will cause a catastrophic OOM crash in local llama.cpp, even with
            # Elastic Context Auto-Scaling.
            if hardware_ceiling and original_tokens > hardware_ceiling:
                if not is_cloud:
                    from omega.errors import ProviderValidationError
                    raise ProviderValidationError(
                        f"Compression failed and original text ({original_tokens} tokens) "
                        f"exceeds absolute hardware ceiling ({hardware_ceiling}). Cannot fallback safely."
                    ) from e
                else:
                    logger.warning(
                        "[%s] Original text (%d) exceeds hardware ceiling (%d), but is_cloud=True. "
                        "Proceeding with fallback; provider may reject.",
                        trace_id, original_tokens, hardware_ceiling
                    )
                
            return text, HeadroomResult(
                ccr_key=ccr_key, trace_id=trace_id,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                strategy_used="error",
                compression_latency_ms=latency_ms,
                shadow_mode=self._shadow_mode,
                bypassed=False, field=field,
                error=str(e),
            )

    async def _write_ccr(
        self, key: str, original: str, compressed: str, hr: HeadroomResult
    ) -> None:
        """Write CCR record to disk. D151: flat JSON, gitignored. D152: Async I/O."""
        try:
            path = self._ccr_dir / f"{key}.json"
            # D152: O(1) Cache Hit Check
            if await anyio.Path(path).exists():
                return  # Already cached, skip write
                
            record = {
                "ccr_key": key,
                "trace_id": hr.trace_id,
                "field": hr.field,
                "original_text": original,
                "compressed_text": compressed,
                "strategy": hr.strategy_used,
                "compression_ratio": hr.compression_ratio,
                "original_tokens": hr.original_tokens,
                "compressed_tokens": hr.compressed_tokens,
                "latency_ms": hr.compression_latency_ms,
                "shadow_mode": hr.shadow_mode,
            }
            await anyio.Path(path).write_text(
                json.dumps(record, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error("HeadroomMiddleware: CCR write failed for %s: %s", key, e)

    async def pre_process(self, ctx: MiddlewareContext) -> MiddlewareResult:
        """Compress system_prompt and/or user_query per config."""
        if not self._enabled:
            return MiddlewareResult(
                system_prompt=ctx.system_prompt,
                user_query=ctx.user_query,
                plugin_name=self.name,
                metadata={}, bypassed=True,
            )

        self._total_calls += 1
        results = []
        sys_out = ctx.system_prompt
        qry_out = ctx.user_query

        if self._compress_system:
            sys_out, hr_sys = self._compress_text(
                ctx.system_prompt, "system_prompt", ctx.trace_id, 
                ctx.hardware_context_ceiling, ctx.is_cloud
            )
            results.append(hr_sys)
            self._update_counters(hr_sys)

        if self._compress_query:
            qry_out, hr_qry = self._compress_text(
                ctx.user_query, "user_query", ctx.trace_id, 
                ctx.hardware_context_ceiling, ctx.is_cloud
            )
            results.append(hr_qry)
            self._update_counters(hr_qry)

        # Merge results into a combined metadata dict
        metadata = {
            "results": [r.to_dict() for r in results],
            "total_tokens_saved": sum(r.tokens_saved for r in results),
            "shadow_mode": self._shadow_mode,
        }

        return MiddlewareResult(
            system_prompt=sys_out,
            user_query=qry_out,
            plugin_name=self.name,
            metadata=metadata,
        )

    async def post_process(
        self, ctx: MiddlewareContext, result: Optional[MiddlewareResult],
        generate_result: Any
    ) -> None:
        """Write compression_metadata onto the GenerateResult."""
        if result is None:
            return
        # GenerateResult.compression_metadata is Optional[Dict]
        # Set to None if result was bypassed with no savings
        if hasattr(generate_result, "compression_metadata"):
            generate_result.compression_metadata = result.metadata or None

    def _update_counters(self, hr: HeadroomResult) -> None:
        if hr.error:
            self._total_errors += 1
        if hr.bypassed:
            self._bypassed_count += 1
        if hr.is_meaningful:
            self._total_tokens_saved += hr.tokens_saved
            self._ratio_accumulator += hr.compression_ratio

    def get_metrics(self) -> Dict[str, Any]:
        meaningful = self._total_calls - self._bypassed_count - self._total_errors
        avg_ratio = (
            self._ratio_accumulator / meaningful if meaningful > 0 else 0.0
        )
        return {
            "plugin": self.name,
            "enabled": self._enabled,
            "shadow_mode": self._shadow_mode,
            "headroom_available": self._headroom_available,
            "total_calls": self._total_calls,
            "bypassed_count": self._bypassed_count,
            "total_errors": self._total_errors,
            "total_tokens_saved": self._total_tokens_saved,
            "avg_compression_ratio": round(avg_ratio, 4),
            "ccr_enabled": self._ccr_enabled,
            "ccr_store_dir": str(self._ccr_dir),
            "min_tokens_threshold": self._min_tokens,
            "strategy_override": self._strategy_override,
        }

    async def shutdown(self) -> None:
        logger.info(
            "HeadroomMiddleware shutdown. Total tokens saved: %d",
            self._total_tokens_saved
        )
```

---

## §5 OBSERVABILITY PATCHES

### 5.1 EventType additions (observability/__init__.py)

Add these constants to the EventType class. Remove the duplicate
TOKEN_CONSUMPTION lines at the same time (lines 127-128 are duplicates).

```python
# Middleware pipeline events — add after RESEARCH_COMPLETE
TOKEN_CONSUMPTION          = "token.consumption"   # keep single definition

# Middleware events (new)
MIDDLEWARE_PRE_START       = "middleware.pre.start"
MIDDLEWARE_PRE_DONE        = "middleware.pre.done"
MIDDLEWARE_POST_DONE       = "middleware.post.done"
MIDDLEWARE_PLUGIN_ERROR    = "middleware.plugin.error"
MIDDLEWARE_PLUGIN_BYPASS   = "middleware.plugin.bypass"

# Dataset events (new)
DATASET_RECORD_WRITTEN     = "dataset.record.written"
DATASET_EXPORT_COMPLETE    = "dataset.export.complete"
```

### 5.2 GenerateResult patch (model_gateway.py)

Add ONE field to the GenerateResult dataclass:

```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
    logprobs: Optional[list] = None
    compression_metadata: Optional[Dict] = None   # ← NEW (D149)
    # Shape when populated:
    # {
    #   "results": [HeadroomResult.to_dict(), ...],   # one per field compressed
    #   "total_tokens_saved": int,
    #   "shadow_mode": bool,
    # }
```

### 5.3 latency_ms fix (model_gateway.py — generate())

Immediately before the provider loop begins (line ~783), add:

```python
_generate_start = time.monotonic()
```

In the success block where GenerateResult is constructed (line ~910), replace:

```python
return GenerateResult(
    text=result,
    provider_name=success_provider.name,
    is_cloud=self._is_cloud_provider(success_provider),
    logprobs=logprobs,
)
```

With:

```python
return GenerateResult(
    text=result,
    provider_name=success_provider.name,
    is_cloud=self._is_cloud_provider(success_provider),
    latency_ms=(time.monotonic() - _generate_start) * 1000,  # ← FIX
    logprobs=logprobs,
    # compression_metadata populated by pipeline.run_post()
)
```

Note: `time` is already imported in model_gateway.py.

---

## §6 omega.yaml ADDITIONS

Add these two blocks at the end of config/omega.yaml:

```yaml
# ── Inference Middleware Pipeline (D149) ───────────────────────────────
middleware:
  pipeline:
    - name: headroom
      enabled: true
      shadow_mode: false           # true = compress & measure but send raw (A/B)
      compress_system_prompt: true
      compress_user_query: true
      min_tokens_to_compress: 200  # tokens (not chars). Below = bypass.
      strategy_override: null      # null = auto. Options: SmartCrusher, Kompress,
                                   # LogCompressor, CodeAware
      ccr_enabled: true
      ccr_store_dir: data/ccr      # gitignored — runtime artifact

# ── Training Dataset Collection (D150) ────────────────────────────────
dataset:
  enabled: true
  schema_version: "1.0.0"
  collect_inference: true          # Record every inference as a training sample
  collect_compression: true        # Record every compression event separately
  collect_preferences: false       # A/B preference pairs (requires shadow_mode)
  min_quality_score: 0.0           # 0.0 = collect everything, curate later
  export_formats:
    - jsonl                        # Native (already working via flush_dataset)
    - alpaca                       # Axolotl / LLaMA-Factory compatible
    - sharegpt                     # Unsloth / FastChat compatible
  exclude_transient: true          # Don't train on ephemeral/transient sessions
  exclude_entities: []             # Entity names to exclude (privacy)
  max_records_per_file: 10000      # Rotate files at this threshold
```

---

## §7 DATASET COLLECTOR SPECIFICATION

The `DatasetCollector` class wraps the existing `ObservabilityEngine`
infrastructure. It does NOT replace it. It adds schema versioning,
compression metadata, domain tagging, and export format support.

### 7.1 TrainingRecord schema (v1.0.0)

```python
# src/omega/observability/dataset_collector.py

@dataclass
class TrainingRecord:
    """Sovereign Training Record — versioned schema for LoRA/fine-tuning.

    v1.0.0 — Initial schema.
    Compatible with: Axolotl, LLaMA-Factory, Unsloth (via export formats).

    RELATIONSHIP TO ObservabilityEngine.record_training_example():
        This class extends the existing format. The existing method writes
        the messages[] array. DatasetCollector adds schema_version,
        compression_metadata, domain, and quality signals on top.
        Both write to data/datasets/ — they are complementary.
    """
    # Versioning (safe migration)
    schema_version: str = "1.0.0"
    record_type: str = "inference"   # inference | compression | preference

    # Identity & provenance (M22)
    trace_id: str = ""
    timestamp: str = ""              # ISO8601 UTC
    entity_name: str = ""
    provider_name: str = ""          # ACTUAL provider (not configured intent)
    is_cloud: bool = False
    model_used: Optional[str] = None

    # The conversation (ChatML — same as existing record_training_example)
    system_prompt: str = ""          # ORIGINAL (pre-compression) always
    user_input: str = ""             # ORIGINAL (pre-compression) always
    assistant_output: str = ""

    # Compression metadata (None if Headroom disabled or bypassed)
    compression_metadata: Optional[Dict] = None

    # Quality signals — critical for LoRA training
    latency_ms: float = 0.0          # ACTUAL timing (fixed from GenerateResult)
    token_count_in: int = 0          # Input tokens (estimated from chars)
    token_count_out: int = 0         # Output tokens (estimated from chars)
    confidence: float = 0.0          # Oracle routing confidence score
    rating: Optional[int] = None     # Human rating 1-5 (future: RLHF)

    # Domain context (for task-specific LoRA)
    domain: Optional[str] = None     # e.g. "engineering", "research", "soul"
    session_id: Optional[str] = None

    # Curation flags
    is_transient: bool = False        # Ephemeral sessions = lower quality
    quality_score: Optional[float] = None  # 0.0-1.0 from background curator
    flagged_for_review: bool = False
```

### 7.2 Export format mappings

**Alpaca format** (`instruction`, `input`, `output`):
```json
{
  "instruction": "<system_prompt>",
  "input": "<user_input>",
  "output": "<assistant_output>"
}
```

**ShareGPT format** (`conversations` with `from`/`value`):
```json
{
  "conversations": [
    {"from": "system", "value": "<system_prompt>"},
    {"from": "human",  "value": "<user_input>"},
    {"from": "gpt",    "value": "<assistant_output>"}
  ]
}
```

**JSONL format**: full `TrainingRecord` dict, one per line.

The `DatasetExporter.export(format, since_days, entity_filter)` method
reads from `data/datasets/inference/*.jsonl`, filters, and writes to
`data/datasets/exports/alpaca_YYYYMMDD.json` etc.

---

## §8 MCP TOOL SPECIFICATIONS

### 8.1 headroom_compress

```
Tool name:  headroom_compress
Purpose:    Compress text and return compressed + full metadata
Arguments:
  text: str               Text to compress
  strategy: str = null    Optional strategy override
Returns:
  {
    compressed: str,          The compressed text
    original_length: int,     Char count of original
    compressed_length: int,   Char count of compressed
    tokens_saved: int,        Estimated tokens saved
    compression_ratio: float, e.g. 0.80 for 80% reduction
    strategy_used: str,       Which strategy was applied
    ccr_key: str,             Key to retrieve original
    latency_ms: float
  }
Errors: M9-safe — returns error field on failure, never raises
```

### 8.2 headroom_retrieve

```
Tool name:  headroom_retrieve
Purpose:    Retrieve the original uncompressed text from the CCR store
            (Elder Protocol — D151)
Arguments:
  ccr_key: str            The key returned by headroom_compress or
                          found in GenerateResult.compression_metadata
Returns:
  {
    original_text: str,
    compressed_text: str,
    strategy: str,
    compression_ratio: float,
    trace_id: str,
    field: str,           "system_prompt" | "user_query"
    error: str|null       Set if key not found
  }
```

### 8.3 headroom_metrics

```
Tool name:  headroom_metrics
Purpose:    Return live compression metrics dashboard
Arguments:
  window_minutes: int = 60    (future — currently returns all-time counters)
Returns:
  {
    plugin: "headroom",
    enabled: bool,
    shadow_mode: bool,
    headroom_available: bool,
    total_calls: int,
    bypassed_count: int,
    total_errors: int,
    total_tokens_saved: int,
    avg_compression_ratio: float,
    ccr_enabled: bool,
    ccr_store_dir: str,
    min_tokens_threshold: int,
    strategy_override: str|null,
    # Derived fields (compute from above):
    effective_calls: int,         # total_calls - bypassed_count
    error_rate: float,            # total_errors / total_calls
    estimated_cost_avoided_usd: float   # total_tokens_saved * cloud rate
  }
```

### 8.4 dataset_export

```
Tool name:  dataset_export
Purpose:    Export collected training records in a specific format.
            Surfaces the sovereign training dataset to agents for
            inspection or Hugging Face Hub upload.
Arguments:
  format: str = "alpaca"      "alpaca" | "sharegpt" | "jsonl"
  since_days: int = 7         How many days of records to include
  entity_filter: str = null   Filter to a single entity
Returns:
  {
    export_path: str,          Absolute path to the export file
    record_count: int,
    schema_version: "1.0.0",
    format: str,
    size_bytes: int,
    since_days: int,
    entity_filter: str|null,
    error: str|null
  }
```

---

## §9 MODELGATEWAY WIRE-UP (the minimal change)

### 9.1 In __init__

After `self._health_monitor = health_monitor` (line ~158), add:

```python
# ── Inference Middleware Pipeline (D149) ────────────────────────────────
self._middleware = self._load_middleware_pipeline()
```

Add a private method:

```python
def _load_middleware_pipeline(self):
    """Load the middleware pipeline from omega.yaml.

    Returns an empty MiddlewarePipeline if middleware config is absent
    or if loading fails (M9 — gateway must boot even if plugins fail).
    """
    from omega.oracle.middleware import MiddlewarePipeline
    try:
        omega_cfg_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "config" / "omega.yaml"
        )
        with open(omega_cfg_path) as f:
            omega_cfg = yaml.safe_load(f)
        middleware_cfg = omega_cfg.get("middleware", {})
        pipeline = MiddlewarePipeline.from_config(middleware_cfg)
        logger.info(
            "Middleware pipeline loaded: %d plugins active",
            len(pipeline.plugins)
        )
        return pipeline
    except Exception as e:
        logger.warning(
            "Middleware pipeline failed to load (%s) — running without plugins", e
        )
        from omega.oracle.middleware import MiddlewarePipeline
        return MiddlewarePipeline([])
```

### 9.2 In generate()

**Before the provider search loop** (after the errors = [] line):

```python
# ── Middleware: pre-process (compress prompts, etc.) ────────────────────
import time as _time
_generate_start = _time.monotonic()

if not self._middleware.is_empty:
    from omega.oracle.middleware import MiddlewareContext
    _mw_ctx = MiddlewareContext(
        system_prompt=system_prompt,
        user_query=user_query,
        trace_id=trace_id or "unknown",
        entity_name=entity_name,
        session_id=session_id,
        model_name=model_name,
        hardware_context_ceiling=self.get_model_spec(model_name).get("context_length"),
        is_cloud=self._is_cloud_provider(self.get_provider_for_model(model_name)) if hasattr(self, 'get_provider_for_model') else False
    )
    _mw_ctx = await self._middleware.run_pre(_mw_ctx)
    # Use transformed prompts for provider calls
    system_prompt = _mw_ctx.system_prompt
    user_query = _mw_ctx.user_query
else:
    _mw_ctx = None
```

**In the success block** where `GenerateResult` is built (~line 910):

```python
_latency = (_time.monotonic() - _generate_start) * 1000
logprobs = getattr(success_provider, '_last_logprobs', None)
gr = GenerateResult(
    text=result,
    provider_name=success_provider.name,
    is_cloud=self._is_cloud_provider(success_provider),
    latency_ms=_latency,
    logprobs=logprobs,
)

# Middleware: post-process (populate compression_metadata, etc.)
if _mw_ctx is not None:
    await self._middleware.run_post(_mw_ctx, gr)

# Dataset collection
await self._record_training_sample(
    gr, system_prompt, user_query, trace_id, entity_name, session_id
)

return gr
```

Add a private helper:

```python
async def _record_training_sample(
    self, gr: GenerateResult, system_prompt: str, user_query: str,
    trace_id: Optional[str], entity_name: Optional[str],
    session_id: Optional[str]
) -> None:
    """Write a TrainingRecord for this inference. Non-fatal on error (M9)."""
    try:
        from omega.observability.dataset_collector import DatasetCollector
        collector = DatasetCollector.get_instance()
        if collector.enabled:
            await collector.record_inference(
                trace_id=trace_id or "unknown",
                system_prompt=system_prompt,
                user_input=user_query,
                assistant_output=gr.text,
                entity_name=entity_name or "system",
                provider_name=gr.provider_name,
                is_cloud=gr.is_cloud,
                model_used=gr.model_used,
                latency_ms=gr.latency_ms,
                compression_metadata=gr.compression_metadata,
                session_id=session_id,
            )
    except Exception as e:
        logger.warning(
            "[%s] Dataset collection failed (non-fatal): %s", trace_id, e
        )
```

**IMPORTANT**: The `system_prompt` and `user_query` passed to
`_record_training_sample` MUST be the **original** values from the
`generate()` signature, not the compressed versions. Always store originals.
For this reason, save originals before the middleware pre-process block:

```python
_original_system_prompt = system_prompt
_original_user_query = user_query
```

Then pass `_original_system_prompt` and `_original_user_query` to
`_record_training_sample`. The compressed versions are what the provider
sees. The originals are what gets stored for training.

---

## §10 TEST SPECIFICATIONS (write tests FIRST — M21)

### test_middleware_pipeline.py (15 tests)

```
test_empty_pipeline_is_noop
    MiddlewarePipeline([]) — run_pre/run_post are no-ops, context unchanged

test_disabled_plugin_is_skipped
    Plugin with enabled=False not included in pipeline.plugins

test_single_plugin_pre_modifies_context
    Plugin returns modified system_prompt — context.system_prompt updated

test_multiple_plugins_chain_in_order
    Plugin A → Plugin B — B sees A's output, not original

test_plugin_pre_failure_does_not_halt_pipeline
    Plugin that raises in pre_process — context unchanged, next plugin runs

test_plugin_post_failure_is_non_fatal
    Plugin that raises in post_process — generate_result unchanged, no raise

test_get_all_metrics_aggregates_all_plugins
    Two plugins — get_all_metrics returns both dicts keyed by name

test_from_config_unknown_plugin_skipped
    Config with name="unknown_plugin" — pipeline loads, logs warning

test_from_config_headroom_disabled
    Config with enabled=false — pipeline has zero plugins

test_from_config_headroom_enabled
    Config with enabled=true — pipeline has one plugin

test_middleware_context_preserves_identity_fields
    trace_id, entity_name, session_id unchanged through pipeline

test_plugin_metadata_accumulated
    After two plugins, context.plugin_metadata has two keys

test_pipeline_is_empty_property
    Empty pipeline → is_empty is True

test_bypass_result_has_correct_fields
    Bypassed MiddlewareResult has bypassed=True, prompts unchanged

test_m9_fault_isolation_integration
    Both plugins fail — final ctx still has original prompts
```

### test_headroom_plugin.py (12 tests)

```
test_headroom_disabled_is_noop
    enabled=False — pre_process returns original prompts, bypassed=True

test_headroom_below_threshold_is_bypassed
    system_prompt < min_tokens_to_compress — HeadroomResult.bypassed=True

test_headroom_unavailable_graceful_bypass
    headroom-ai import patched to fail — no raise, returns original

test_headroom_compress_system_prompt
    Long system_prompt — HeadroomResult.tokens_saved > 0

test_headroom_compress_user_query
    Long user_query — HeadroomResult.tokens_saved > 0

test_shadow_mode_sends_original
    shadow_mode=True — ctx.system_prompt == original after pre_process

test_shadow_mode_records_compression_ratio
    shadow_mode=True — HeadroomResult.compression_ratio > 0

test_ccr_file_written
    ccr_enabled=True — data/ccr/{key}.json exists after compress

test_ccr_file_contains_original
    CCR file — original_text matches pre-compression input

test_compression_failure_returns_original
    Compress function raises — pre_process returns original, error field set

test_get_metrics_structure
    After 3 calls — get_metrics() has all required keys

test_post_process_populates_compression_metadata
    After pre + post — generate_result.compression_metadata is not None
```

### test_dataset_collector.py (10 tests)

```
test_training_record_schema_version
    TrainingRecord().schema_version == "1.0.0"

test_record_inference_writes_jsonl
    record_inference() — data/datasets/inference/YYYY-MM-DD.jsonl has 1 line

test_record_preserves_original_prompts
    system_prompt in record == original (not compressed)

test_compression_metadata_included_in_record
    compression_metadata dict written to JSONL correctly

test_export_alpaca_format
    export("alpaca") — JSON array with instruction/input/output keys

test_export_sharegpt_format
    export("sharegpt") — JSON array with conversations[from/value] keys

test_export_jsonl_format
    export("jsonl") — JSONL file, each line parses as dict with schema_version

test_exclude_transient_sessions
    is_transient=True records excluded from export by default

test_entity_filter_in_export
    export(entity_filter="kali") — only kali records in output

test_m21_contract_training_record_is_dataclass
    isinstance(TrainingRecord(), TrainingRecord) — trivial M21 gate
```

---

## §11 IMPLEMENTATION SEQUENCE (STRICT ORDER)

Agents MUST follow this order. Each phase is a discrete unit of work.

### Phase 0 — Bugfixes (implement first, commit separately)

1. `src/omega/observability/__init__.py`
   - Remove duplicate `TOKEN_CONSUMPTION` lines 127 and 128 (keep line 126)
   - Run `make test` — must still pass

2. `src/omega/oracle/model_gateway.py`
   - Add `import time as _time` if not already present (it is — `import time` exists)
   - Capture `_generate_start = time.monotonic()` at top of `generate()`
   - Pass `latency_ms=(time.monotonic() - _generate_start) * 1000` to GenerateResult
   - Run `make test` — must still pass. Commit: `fix: populate latency_ms in GenerateResult`

### Phase 0.5 — Async I/O Patch (implement before Phase 1)

1. `src/omega/observability/__init__.py`
   - In `_persist_event()`, the `with open(...)` call is synchronous and will block the event loop under heavy load.
   - Wrap the write operation in `anyio.to_thread.run_sync()` or use `anyio.open_file()`.
   - Run `make test` — must still pass. Commit: `fix: make observability event persistence async`

1. Write `tests/test_dataset_collector.py` (10 tests, all failing)
2. Write `src/omega/observability/dataset_collector.py` (TrainingRecord + DatasetCollector + DatasetExporter)
3. Add EventType constants to `observability/__init__.py`
4. Run `make test` — new tests pass. Commit: `feat: add DatasetCollector and TrainingRecord schema v1.0.0`

### Phase 2 — Middleware Interface (write tests first, then implement)

1. Write `tests/test_middleware_pipeline.py` (15 tests, all failing)
2. Write `src/omega/oracle/middleware/__init__.py`
3. Run `make test` — new tests pass. Commit: `feat: add OmegaMiddlewareBase and MiddlewarePipeline plugin bus`

### Phase 3 — Headroom Plugin (write tests first, then implement)

1. Write `tests/test_headroom_plugin.py` (12 tests, all failing)
2. Write `src/omega/oracle/middleware/headroom_plugin.py`
3. Run `make test` — new tests pass. Commit: `feat: add HeadroomMiddleware as first plugin tenant`

### Phase 4 — Wire-Up

1. Add `compression_metadata: Optional[Dict] = None` field to `GenerateResult`
2. Add `middleware:` and `dataset:` sections to `config/omega.yaml`
3. Add `_load_middleware_pipeline()` and `_record_training_sample()` to `ModelGateway`
4. Wire `pipeline.run_pre()` / `run_post()` into `generate()` (see §9)
5. Run `make test` — all tests pass. Commit: `feat: wire middleware pipeline into ModelGateway`

### Phase 5 — MCP Tools

1. Add 4 tools to `mcp_servers/omega_hub/tools.py` (see §8 for specs):
   `headroom_compress`, `headroom_retrieve`, `headroom_metrics`, `dataset_export`
2. All 4 must use `@m9_safe` decorator (existing pattern)
3. Run `make test` — all tests pass. Commit: `feat: add headroom and dataset MCP tools`

### Phase 6 — Verification

1. Run `make test` — expect 432 + 37 new = ~469 tests passing
2. Run `make temple-grade` — T3 (coverage), T5 (AnyIO), T9 (structured logging) must pass
3. Run `make heritage-map` — verify [id-soft:] tags present in new files
4. Manual smoke test: `OMEGA_ENV=test python -c "from omega.oracle.middleware import MiddlewarePipeline; print('OK')"`
5. Manual smoke test: `OMEGA_ENV=test python -c "from omega.oracle.middleware.headroom_plugin import HeadroomMiddleware; print('OK')"`
6. Commit final: `chore: Phase 6 verification complete — middleware plugin bus live`

---

## §12 MANDATE COMPLIANCE CHECKLIST

Every implementing agent MUST verify:

| Mandate | Requirement | Verification |
|---------|-------------|--------------|
| M1 AnyIO | No `asyncio` in new files | `grep -r "import asyncio" src/omega/oracle/middleware/` → 0 results |
| M2 Firewall | No WAD imports in middleware | `grep -r "config/wads" src/omega/oracle/middleware/` → 0 results |
| M8 Zero Telemetry | No network calls in HeadroomMiddleware | Audit `_compress_text` — local library call only |
| M9 Error Integrity | No bare `except:` | Every except catches specific type or `Exception as e` with logging |
| M13 Temple-Grade | Tests pass | `make temple-grade` passes |
| M14 Heritage Tags | New files with id-soft patterns tagged | `[id-soft: quake3-1999]` in middleware/__init__.py, `[id-soft: doom-1993]` in headroom_plugin.py |
| M16 Modular | No hardcoded paths | All paths via config or `Path(__file__).resolve()` |
| M21 Gate Integrity | Contract tests exist | All three new test files have isinstance() checks |
| M22 Response Provenance | Original prompts stored | `_original_system_prompt` / `_original_user_query` passed to DatasetCollector |

---

## §13 WHAT THE SYSTEM PRODUCES

Once live, every engine conversation automatically generates sovereign training capital:

| Asset | Location | Purpose |
|-------|----------|---------|
| Inference JSONL | `data/datasets/inference/YYYY-MM-DD.jsonl` | General instruction fine-tuning |
| Compression records | `data/datasets/compression/YYYY-MM-DD.jsonl` | Compression quality LoRA |
| Alpaca export | `data/datasets/exports/alpaca_YYYYMMDD.json` | Axolotl / LLaMA-Factory |
| ShareGPT export | `data/datasets/exports/sharegpt_YYYYMMDD.json` | Unsloth / FastChat |
| CCR store | `data/ccr/{key}.json` | Elder Protocol — original retrieval |
| Token ledger | `data/logs/token_ledger.jsonl` | Sovereignty cost audit |
| Metrics MCP | `headroom_metrics` tool | Live compression dashboard |

The `dataset_export` MCP tool lets any agent produce a file ready for
`huggingface-cli upload` in under one second.

---

## §14 WHAT COMES AFTER (DO NOT IMPLEMENT YET)

These are Epoch I Strike 2 and Strike 3 — separate work items.
Including here for context so implementing agents do not over-build.

- **Strike 2 (HardwareHAL)**: `src/omega/oracle/hardware_hal.py`
  A bare-metal llama-cpp-python wrapper. Wires Zen 2/AVX2 flags.
  Implements M20 SomaticState serialization. Does NOT touch middleware.

- **Strike 3 (OmegaHttpClient)**: `src/omega/oracle/omega_http_client.py`
  SSRF-guarded HTTP client. Byte-caps. Binary sandboxing.
  Routes scraped content through Headroom SmartCrusher before FTS5 index.
  Does NOT touch middleware.

- **Epoch II (Redis A2A)**: Separate sprint after all three Epoch I strikes land.

---

## §15 FINAL NOTES FOR IMPLEMENTING AGENTS

1. **Read §1 first**. The existing infrastructure is more complete than it looks.
   Do not duplicate `record_training_example()` — extend it.

2. **The `_original_system_prompt` / `_original_user_query` pattern (§9.2)
   is non-negotiable**. Training on compressed prompts defeats the purpose.
   Always store what the user actually said.

3. **headroom-ai is optional**. The plugin MUST work with `enabled: false`
   and MUST degrade gracefully when the library is not installed.
   Run `make test` in a fresh venv without headroom-ai installed to verify.

4. **Shadow mode is the A/B testing mechanism**. When `shadow_mode: true`,
   compression happens and metrics are collected, but the ORIGINAL prompt
   is sent to the provider. This allows quality comparison without affecting
   response quality. Toggle it in omega.yaml — no code change required.

5. **Commit discipline**: One commit per phase. Prefix: `feat:`, `fix:`, `chore:`.
   Do not bundle Phase 0 bugfixes with Phase 4 wire-up.

6. **M21 before implementation**: Write all 37 tests in Phases 1/2/3 BEFORE
   writing the implementation files. The tests are the specification.

---

*Document written: 2026-06-23*
*Author: MaKaLi Council (Sonnet 4.6)*
*Decisions ratified: D149, D150, D151*
*Next review: After Phase 6 verification complete*
