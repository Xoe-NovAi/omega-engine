# 🔱 omega-vetala — HuggingFace Transformers Provider
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ HUGGINGFACE-PROVIDER
#
# [id-soft: doom3-2004] Leak Detection — detect harmful content leakage
#   Adapted from DOOM 3's leak detection approach: detect, don't enumerate.
#
# Local transformer model inference for privacy-preserving moderation.
# Model is loaded lazily on first call and runs in a thread to avoid
# blocking the AnyIO event loop.

from __future__ import annotations

import logging
from typing import Any

import anyio

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
    ProviderError,
)

logger = logging.getLogger(__name__)

# Default model — fine-tuned for toxicity classification.
_DEFAULT_MODEL = "unitary/toxic-bert"

# Fallback model — smaller, for low-memory environments.
_FALLBACK_MODEL = "unitary/unbiased-toxic-roberta"

# Pipeline task identifier
_PIPELINE_TASK = "text-classification"


class HuggingFaceProvider(ModelProvider):
    """Privacy-preserving moderation via a local HuggingFace transformer.

    The model is loaded **lazily** — the first call to :meth:`analyze`
    triggers model download and pipeline initialisation.  If the primary
    model causes an OOM or import error, a smaller fallback model is used.

    All inference runs inside ``anyio.to_thread.run_sync`` to keep the
    event loop responsive.

    Attributes:
        supports_offline: True — works entirely offline once the model
            is cached.
    """

    supports_offline: bool = True

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        fallback_model: str = _FALLBACK_MODEL,
        device: int = -1,
    ) -> None:
        """Initialise provider.

        Args:
            model_name: HuggingFace model ID for the primary model.
            fallback_model: Smaller model to try if the primary fails.
            device: Device ID (-1 for CPU).
        """
        self._model_name = model_name
        self._fallback_model = fallback_model
        self._device = device

        # Lazy-loaded pipeline (None until first analyze call)
        self._pipeline: Any = None
        self._loaded_model_name: str = ""

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------

    async def _ensure_model(self) -> None:
        """Load the transformer pipeline if not already loaded.

        Runs synchronously inside a thread to avoid blocking the
        event loop during model download / loading.
        """
        if self._pipeline is not None:
            return

        def _load(name: str) -> Any:
            # Late import so the package works without torch/transformers
            from transformers import pipeline  # type: ignore[import-untyped]

            logger.info("Loading HF model: %s (device=%d)", name, self._device)
            return pipeline(
                _PIPELINE_TASK,
                model=name,
                device=self._device,
            )

        # Try primary model
        try:
            self._pipeline = await anyio.to_thread.run_sync(
                _load, self._model_name, abandon_on_cancel=True,
            )
            self._loaded_model_name = self._model_name
            logger.info("Loaded primary model: %s", self._model_name)
            return
        except (ImportError, OSError, RuntimeError, MemoryError) as exc:
            logger.warning(
                "Primary model %s failed (%s), trying fallback %s",
                self._model_name,
                exc,
                self._fallback_model,
            )

        # Try fallback
        try:
            self._pipeline = await anyio.to_thread.run_sync(
                _load, self._fallback_model, abandon_on_cancel=True,
            )
            self._loaded_model_name = self._fallback_model
            logger.info("Loaded fallback model: %s", self._fallback_model)
            return
        except (ImportError, OSError, RuntimeError, MemoryError) as exc:
            logger.exception(
                "Fallback model %s also failed: %s",
                self._fallback_model,
                exc,
            )
            raise ProviderError(
                f"Could not load any HuggingFace model: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* using a local transformer model.

        Args:
            text: Content to moderate.

        Returns:
            :class:`ModerationResult` with toxicity scores.
        """
        if not text.strip():
            return ModerationResult(provider_name="huggingface")

        # Lazy-load the model (first call only)
        try:
            await self._ensure_model()
        except ProviderError as exc:
            logger.error("HuggingFace provider unavailable: %s", exc)
            return ModerationResult(
                provider_name="huggingface",
                categories={"__load_failed__": 1.0},
            )

        def _infer(t: str) -> list[dict[str, Any]]:
            assert self._pipeline is not None
            return self._pipeline(t)

        try:
            raw: list[dict[str, Any]] = await anyio.to_thread.run_sync(
                _infer, text, abandon_on_cancel=True,
            )
        except Exception as exc:
            logger.exception("HF inference failed: %s", exc)
            return ModerationResult(
                provider_name="huggingface",
                categories={"__inference_error__": 1.0},
            )

        # Parse pipeline output
        # Typical output: [{"label": "toxic", "score": 0.98}, ...]
        categories: dict[str, float] = {}
        for entry in raw:
            label: str = entry.get("label", "unknown").lower()
            score: float = entry.get("score", 0.0)
            categories[label] = score

        # For binary classifiers (toxic / not-toxic) we create a single key
        if not categories:
            return ModerationResult(provider_name="huggingface")

        # Determine if flagged — use the "toxic" label or the highest negative
        toxic_score = categories.get("toxic", 0.0)
        is_flagged = toxic_score >= 0.5
        confidence = max(categories.values())

        return ModerationResult(
            is_flagged=is_flagged,
            confidence=confidence,
            categories=categories,
            provider_name="huggingface",
        )
