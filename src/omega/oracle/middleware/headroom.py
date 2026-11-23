# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-HEADROOM-MIDDLEWARE-v2.0.0
# [heritage: headroom-ai 2025] Semantic compression middleware for context optimization
#
# v2.0.0 (2026-11-23) — Headroom Enhancement Plan, Phases 1-3:
#   - resolve entity model to a NETURAL, network-free tokenizer model (estimator)
#   - pass entity context_window as `model_limit` (no more 200K default)
#   - capture REAL CompressResult metrics + per-message estimates + aggregate stats
#   - token-budget gate (skip compression under threshold)
#   - entity compression profiles loaded from config/headroom_profiles.yaml
#   - HEADROOM_OFFLINE=1 via os.environ.setdefault + headroom.offline.apply_offline_env()
#   - Omega-owned bounded/TTL CCR store (headroom.retrieve() does not exist in v0.45.0)
#
# DocRef: docs/HEADROOM_ENHANCEMENT_PLAN.md
from __future__ import annotations

import hashlib
import logging
import os
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field, fields
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio
import yaml

from omega.errors import OmegaError
from omega.governance.config_resolver import CONFIG_DIR
from omega.oracle.entity_registry import EntityRegistry

# [M1 AnyIO Absolute] headroom-ai is an optional dep; gracefully degrade
# if not installed (fallback behavior in each method)
try:
    import headroom

    HAS_HEADROOM = True
except ImportError:  # pragma: no cover - env dependent
    headroom = None  # type: ignore[assignment]
    HAS_HEADROOM = False

logger = logging.getLogger("omega.headroom")

DEFAULT_CONTEXT_WINDOW = 8192
#: Matches no headroom MODEL_PATTERN -> EstimatingTokenCounter (no HF download, no PyTorch).
NEUTRAL_TOKENIZER_MODEL = "omega-engine-local"
_CCR_PREFIX = "ccr:"

# Local classification only — never calls headroom (which may try to fetch a tokenizer).
_BACKEND_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"^gpt-", "tiktoken"),
    (r"^claude-", "anthropic-estimate"),
    (r"^(llama|meta-llama|codellama|qwen|phi-|deepseek|yi-|falcon|mpt-|starcoder|codegen)",
     "huggingface"),
    (r"^(mistral|mixtral|codestral|ministral|pixtral)", "mistral"),
    (r"^(gemini|palm)", "google-estimate"),
)


def _classify_backend(model: str) -> str:
    lowered = model.lower()
    for pattern, backend in _BACKEND_PATTERNS:
        if re.match(pattern, lowered):
            return backend
    return "estimating"


@dataclass
class HeadroomSettings:
    """Global Headroom settings (config/headroom.yaml)."""

    enabled: bool = True
    offline: bool = True
    tokenizer_model: str = NEUTRAL_TOKENIZER_MODEL
    #: Explicit, operator-approved override. None = always use the neutral estimator.
    tokenizer_model_override: Optional[str] = None
    default_context_window: int = DEFAULT_CONTEXT_WINDOW
    budget_threshold: float = 0.70
    max_cached_originals: int = 256
    ttl_seconds: float = 1800.0


@dataclass
class CompressionSummary:
    """Authoritative metrics for one compress_context() call."""

    entity: str
    model: str
    model_limit: int
    tokens_before: int = 0
    tokens_after: int = 0
    tokens_saved: int = 0
    compression_ratio: float = 0.0
    transforms_applied: List[str] = field(default_factory=list)
    lossless: Optional[bool] = None
    reverted_messages: int = 0
    elapsed_ms: float = 0.0
    compressed: bool = False
    skipped_reason: Optional[str] = None


@dataclass
class HeadroomResult:
    """Per-message compression metadata.

    ``tokens_saved`` is the per-message estimate (counter before vs after);
    ``summary`` carries the batch-level authoritative CompressResult metrics.
    """

    compressed_text: str
    original_ref: Optional[str] = None
    tokens_saved: int = 0
    tokens_before: int = 0
    tokens_after: int = 0
    lossless: Optional[bool] = None
    summary: Optional[CompressionSummary] = None


def _read_yaml(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    """Read a config mapping; log loudly and fall back on any failure (M23)."""
    if not path.is_file():
        logger.warning("Headroom config missing: %s — using defaults", path)
        return dict(default)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        logger.error("Headroom config unreadable: %s — %s", path, e)
        return dict(default)
    if not isinstance(data, dict):
        logger.error("Headroom config is not a mapping: %s — using defaults", path)
        return dict(default)
    return data


def _apply_offline(enabled: bool) -> None:
    """Enforce air-gap before any headroom call (M8 Zero Telemetry)."""
    if not enabled:
        logger.warning("Headroom offline mode DISABLED by config — egress is not blocked")
        return
    os.environ.setdefault("HEADROOM_OFFLINE", "1")
    if not HAS_HEADROOM:
        return
    try:
        from headroom import offline as _offline

        _offline.apply_offline_env()  # idempotent; setdefault respects operator override
    except (ImportError, AttributeError, OSError) as e:
        logger.error("Failed to apply Headroom offline env: %s", e)


class HeadroomMiddleware:
    """Sovereign Semantic Compression Middleware (headroom-ai v0.45.0+, PyTorch-free)."""

    def __init__(
        self,
        entity_registry: Optional[EntityRegistry] = None,
        *,
        config_path: Optional[Path] = None,
        profiles_path: Optional[Path] = None,
    ) -> None:
        self.registry = entity_registry

        raw_settings = _read_yaml(
            config_path or (CONFIG_DIR / "headroom.yaml"), {}
        )
        settings_defaults = HeadroomSettings()
        self._settings = HeadroomSettings(
            **{
                f.name: raw_settings.get(f.name, getattr(settings_defaults, f.name))
                for f in fields(HeadroomSettings)
            }
        )
        _apply_offline(self._settings.offline)

        profiles_doc = _read_yaml(
            profiles_path or (CONFIG_DIR / "headroom_profiles.yaml"), {}
        )
        self._profiles: Dict[str, Dict[str, Any]] = {
            "default": {
                "mode": "agent",
                "compress_user_messages": False,
                "protect_recent": 4,
                "protect_analysis_context": True,
                "min_tokens_to_compress": 250,
            }
        }
        loaded = profiles_doc.get("profiles", {})
        if isinstance(loaded, dict):
            for name, prof in loaded.items():
                if isinstance(prof, dict):
                    self._profiles[str(name)] = dict(prof)
        raw_entities = profiles_doc.get("entity_profiles", {})
        self._entity_profiles: Dict[str, str] = (
            {str(k).lower(): str(v) for k, v in raw_entities.items()}
            if isinstance(raw_entities, dict)
            else {}
        )

        # Bounded, TTL'd local CCR store: ref -> (monotonic_ts, workspace_key, original_text)
        self._originals: "OrderedDict[str, Tuple[float, str, str]]" = OrderedDict()
        self._stats: Dict[str, Dict[str, Any]] = {}
        self._model_cache: Dict[str, str] = {}
        self._counter_cache: Dict[str, Any] = {}

        self._tracker: Optional[Any] = None
        if HAS_HEADROOM:
            try:
                from headroom.ccr import ContextTracker, ContextTrackerConfig

                self._tracker = ContextTracker(
                    ContextTrackerConfig(
                        max_context_age_seconds=max(300.0, float(self._settings.ttl_seconds))
                    )
                )
            except (ImportError, AttributeError, OSError, TypeError) as e:
                logger.warning("Headroom CCR ContextTracker unavailable: %s", e)

    # ── Phase 1.1: model resolution ──────────────────────────────────────────
    def resolve_headroom_model(self, entity_name: str) -> str:
        """Return the model string passed to headroom.compress().

        Omega's entity models are provider aliases (e.g. ``opencode/big-pickle``),
        which are not real tokenizer names. Feeding them to Headroom risks a
        HuggingFace download. We deliberately use a neutral name that resolves to
        ``EstimatingTokenCounter`` — network-free and PyTorch-free. Operators can
        opt into a real tokenizer via ``tokenizer_model_override``.
        """
        if entity_name in self._model_cache:
            return self._model_cache[entity_name]

        entity_model = NEUTRAL_TOKENIZER_MODEL
        if self.registry is not None:
            try:
                entity = self.registry.get(entity_name)
                if entity is not None and entity.model:
                    entity_model = entity.model
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning("Entity model lookup failed for %s: %s", entity_name, e)

        model = self._settings.tokenizer_model_override or self._settings.tokenizer_model
        self._model_cache[entity_name] = model
        logger.debug(
            "headroom.model_resolution entity=%s entity_model=%s tokenizer_model=%s backend=%s",
            entity_name,
            entity_model,
            model,
            _classify_backend(entity_model),
        )
        return model

    def _get_counter(self, model: str) -> Any:
        """Get (and cache) a Headroom TokenCounter. Neutral model => estimator, no I/O."""
        if model not in self._counter_cache:
            from headroom.tokenizers import get_tokenizer

            self._counter_cache[model] = get_tokenizer(model, fallback=True)
        return self._counter_cache[model]

    # ── Phase 2.2: profiles ──────────────────────────────────────────────────
    def _profile_for(self, entity_name: str) -> Dict[str, Any]:
        profile_name = self._entity_profiles.get(entity_name.lower(), "default")
        merged = dict(self._profiles.get("default", {}))
        merged.update(self._profiles.get(profile_name, {}))
        return merged

    def _build_compress_config(self, profile: Dict[str, Any]) -> Any:
        allowed = {f.name for f in fields(headroom.CompressConfig)}
        kwargs = {k: v for k, v in profile.items() if k in allowed}
        return headroom.CompressConfig(**kwargs)

    # ── Phase 3.1: local CCR store ──────────────────────────────────────────
    def _store_original(self, entity_name: str, session_id: str, text: str) -> str:
        ref = _CCR_PREFIX + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        workspace = f"{entity_name}:{session_id}"
        self._originals[ref] = (time.monotonic(), workspace, text)
        self._originals.move_to_end(ref)
        while len(self._originals) > max(1, self._settings.max_cached_originals):
            self._originals.popitem(last=False)
        return ref

    def _track_metadata(self, entity_name: str, session_id: str, summary: CompressionSummary) -> None:
        if self._tracker is None:
            return
        try:
            self._tracker.track_compression(
                hash_key=f"{entity_name}:{session_id}:{summary.tokens_saved}",
                turn_number=0,
                tool_name=None,
                original_count=summary.tokens_before,
                compressed_count=summary.tokens_after,
                workspace_key=f"{entity_name}:{session_id}",
                sample_content=",".join(summary.transforms_applied),
            )
        except (OmegaError, RuntimeError, OSError, TypeError, ValueError) as e:
            logger.warning("Headroom CCR metadata tracking failed: %s", e)

    # ── stats ────────────────────────────────────────────────────────────────
    def _record_summary(self, summary: CompressionSummary) -> None:
        stats = self._stats.setdefault(
            summary.entity,
            {
                "calls": 0,
                "compressed": 0,
                "skipped": 0,
                "errors": 0,
                "tokens_before": 0,
                "tokens_after": 0,
                "tokens_saved": 0,
                "last_ratio": 0.0,
                "model": summary.model,
                "model_limit": summary.model_limit,
            },
        )
        stats["calls"] += 1
        stats["model"] = summary.model
        stats["model_limit"] = summary.model_limit
        if summary.skipped_reason == "error":
            stats["errors"] += 1
        elif summary.skipped_reason:
            stats["skipped"] += 1
        else:
            stats["compressed"] += 1
        stats["tokens_before"] += summary.tokens_before
        stats["tokens_after"] += summary.tokens_after
        stats["tokens_saved"] += summary.tokens_saved
        stats["last_ratio"] = summary.compression_ratio

    def get_compression_stats(self) -> Dict[str, Any]:
        """Return per-entity and aggregate compression stats for Hivemind awareness."""
        per_entity = {name: dict(stats) for name, stats in self._stats.items()}
        totals = {
            key: sum(s[key] for s in self._stats.values())
            for key in ("calls", "compressed", "skipped", "errors",
                        "tokens_before", "tokens_after", "tokens_saved")
        }
        return {"per_entity": per_entity, "totals": totals}

    def reset_stats(self) -> None:
        """Clear accumulated stats and CCR cache (primarily for tests)."""
        self._stats.clear()
        self._originals.clear()

    # ── main entry point ─────────────────────────────────────────────────────
    async def compress_context(
        self,
        entity_name: str,
        messages: List[Dict[str, Any]],
        context_window: Optional[int] = None,
        session_id: str = "",
    ) -> Tuple[List[Dict[str, Any]], List[HeadroomResult]]:
        """Compress messages for an entity using its model/context window.

        Args:
            entity_name: Entity name (profile + cache isolation key).
            messages: Message dicts with ``role`` and ``content``.
            context_window: Entity context window (passed as headroom ``model_limit``).
            session_id: Session id, used to scope the local CCR store.

        Returns:
            (compressed_messages, per_message_results). Never raises: on any
            failure the original messages are returned (M23 fail-open, logged).
        """
        if not self._settings.enabled or not HAS_HEADROOM or not messages:
            return messages, []

        model = self.resolve_headroom_model(entity_name)
        limit = int(context_window or self._settings.default_context_window)
        summary = CompressionSummary(entity=entity_name, model=model, model_limit=limit)

        try:
            counter = self._get_counter(model)
            before_tokens = await anyio.to_thread.run_sync(
                partial(headroom.count_tokens_messages, messages, counter)
            )
            # Phase 2.1: budget gate — no compression when comfortably under limit
            if before_tokens < int(limit * float(self._settings.budget_threshold)):
                summary.skipped_reason = "under_budget"
                self._record_summary(summary)
                logger.debug(
                    "headroom.skip entity=%s tokens=%d limit=%d threshold=%.2f",
                    entity_name, before_tokens, limit, self._settings.budget_threshold,
                )
                return messages, [
                    HeadroomResult(m.get("content", ""), summary=summary) for m in messages
                ]

            profile = self._profile_for(entity_name)
            config = self._build_compress_config(profile)

            started = time.perf_counter()
            result = await anyio.to_thread.run_sync(
                partial(
                    headroom.compress,
                    messages,
                    model=model,
                    model_limit=limit,
                    config=config,
                )
            )
            summary.elapsed_ms = (time.perf_counter() - started) * 1000.0
            summary.tokens_before = result.tokens_before
            summary.tokens_after = result.tokens_after
            summary.tokens_saved = result.tokens_saved
            summary.compression_ratio = result.compression_ratio
            summary.transforms_applied = list(result.transforms_applied or [])
            summary.lossless = result.lossless
            summary.reverted_messages = result.reverted_messages
            summary.compressed = True

            compressed_messages = list(result.messages)
            results: List[HeadroomResult] = []
            for i, msg in enumerate(compressed_messages):
                original_text = messages[i].get("content", "") if i < len(messages) else ""
                new_text = msg.get("content", "")
                before = await anyio.to_thread.run_sync(counter.count_text, original_text)
                after = await anyio.to_thread.run_sync(counter.count_text, new_text)
                ref = self._store_original(entity_name, session_id, original_text) if new_text != original_text else None
                results.append(
                    HeadroomResult(
                        compressed_text=new_text,
                        original_ref=ref,
                        tokens_saved=max(0, before - after),
                        tokens_before=before,
                        tokens_after=after,
                        lossless=result.lossless,
                        summary=summary,
                    )
                )

            self._track_metadata(entity_name, session_id, summary)
            self._record_summary(summary)
            logger.info(
                "compression entity=%s before=%d after=%d saved=%d ratio=%.2f transforms=%s",
                entity_name,
                summary.tokens_before,
                summary.tokens_after,
                summary.tokens_saved,
                summary.compression_ratio,
                ",".join(summary.transforms_applied),
            )
            return compressed_messages, results

        except (OmegaError, RuntimeError, OSError, TypeError, ValueError) as e:
            logger.error("Headroom compression failed for %s: %s", entity_name, e)
            summary.skipped_reason = "error"
            self._record_summary(summary)
            return messages, []

    async def retrieve_original(self, ref_id: str) -> str:
        """Retrieve original content from the local CCR store (bounded + TTL'd)."""
        entry = self._originals.get(ref_id)
        if entry is None:
            return f"[[ERROR: Original content for {ref_id} could not be retrieved]]"
        stored_at, _workspace, text = entry
        if time.monotonic() - stored_at > self._settings.ttl_seconds:
            self._originals.pop(ref_id, None)
            return f"[[ERROR: Original content for {ref_id} expired]]"
        self._originals.move_to_end(ref_id)
        return text


_headroom_instance: Optional[HeadroomMiddleware] = None


def get_headroom_middleware() -> HeadroomMiddleware:
    """Singleton provider for HeadroomMiddleware."""
    global _headroom_instance
    if _headroom_instance is None:
        _headroom_instance = HeadroomMiddleware()
    return _headroom_instance
