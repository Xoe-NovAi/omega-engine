# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Shared TokenEstimator — single source of truth for Context Packer v3.

AP Token: AP-PACKER-V3-TOKEN-ESTIMATOR-20260808
SSOT:     docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md §1.5, §1.7.6

The Context Packer v2 hardcoded `tiktoken.get_encoding("cl100k_base")` and a
magic 1.3 margin inside packer.py. The v3 doctrine mandates ONE shared estimator
used by BOTH the curator (`curate_packs.py`) and the packer (`packer.py`) so the
two can never drift (manual §1.5 — zero-drift guarantee).

Platform-specific encoding (manual §1.7.6):
  * Claude      -> cl100k_base (GPT-4/Claude compatible)
  * Grok/Gemini -> o200k_base (GPT-4o)

Margin handling (manual §1.5, §1.7.6):
  tiktoken undercounts by 10-30% vs the model's real tokenizer (researcher
  finding). v2 hardcoded 1.3. v3 pulls the multiplier from PlatformConfig
  (`token_margin_multiplier`, default 1.3) and passes it explicitly.

M1 (AnyIO): tiktoken encoding is CPU-bound — the caller should wrap it in
`anyio.to_thread.run_sync`; this module exposes a pure, synchronous function
plus a small async wrapper for convenience.
"""

from __future__ import annotations

import os

try:
    import tiktoken
except ImportError:  # pragma: no cover - graceful degradation
    tiktoken = None

import anyio

# Default margin mirrors the researcher finding (tiktoken undercounts 10-30%).
DEFAULT_TOKEN_MARGIN = 1.3


def estimate_tokens(
    text: str,
    model: str = "cl100k_base",
    margin: float = DEFAULT_TOKEN_MARGIN,
) -> int:
    """Estimate the token count for ``text`` using ``tiktoken``.

    Args:
        text: The content whose token count is being estimated.
        model: tiktoken encoding name. ``cl100k_base`` (Claude), ``o200k_base``
            (Grok/Gemini). Passed through directly to ``tiktoken.get_encoding``.
        margin: Safety multiplier applied on top of the raw tiktoken count.
            Defaults to 1.3 (undercount guard). 0.0 or 1.0 disables the margin.

    Returns:
        Estimated token count as an int. Always >= 0.

    Raises:
        ValueError: if ``tiktoken`` is unavailable at runtime (M23 hard stop —
            no silent fallback to a char-count approximation).
    """
    if tiktoken is None:
        raise ValueError(
            "[PACK-FAIL] tiktoken unavailable — refusing to estimate tokens "
            "with a char-count approximation (M23, no soft-failure)."
        )

    enc = tiktoken.get_encoding(model)
    raw = len(enc.encode(text))
    return int(raw * margin)


async def estimate_tokens_async(
    text: str,
    model: str = "cl100k_base",
    margin: float = DEFAULT_TOKEN_MARGIN,
) -> int:
    """Async wrapper around :func:`estimate_tokens` (M1: CPU-bound -> thread)."""
    return await anyio.to_thread.run_sync(estimate_tokens, text, model, margin)


def tokens_for_file(
    path: os.PathLike,
    model: str = "cl100k_base",
    margin: float = DEFAULT_TOKEN_MARGIN,
) -> int:
    """Read a file and estimate its token count (M1-friendly sync helper)."""
    with open(os.fspath(path), "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return estimate_tokens(content, model=model, margin=margin)


async def tokens_for_file_async(
    path: os.PathLike,
    model: str = "cl100k_base",
    margin: float = DEFAULT_TOKEN_MARGIN,
) -> int:
    """Async file token estimation (M1: blocking I/O + CPU -> thread)."""
    return await anyio.to_thread.run_sync(tokens_for_file, path, model, margin)
