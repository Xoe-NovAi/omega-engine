"""Exemplar-echo instrumentation.

The phase-1 run showed a 0.767 exact-match that was produced by copying the
few-shot exemplars rather than by inferring the answer (see
docs/research/LFM25_SMS_REAL_DATASET_20261008.md §5.1). Aggregate accuracy alone
cannot distinguish "correct" from "copied", so every aggregate in the gauntlet
carries these four numbers:

  distinct_output_ratio  distinct normalized raw outputs / n
  modal_output_share     count of the single most common normalized output / n
  copy_suspect_n         how many cases share that single most common output
  copy_suspect           distinct_output_ratio < 0.35 AND n >= 8

Normalization is whitespace-collapsed, case-folded and punctuation-stripped, so
"identical answer" means identical modulo surface form, not byte-identical.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Iterable

#: Below this distinct-output ratio a group is considered degenerate.
ECHO_RATIO_THRESHOLD = 0.35

#: Below this n the ratio is too noisy to accuse — small groups are not flagged.
ECHO_MIN_N = 8

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]")


def normalize(raw: str) -> str:
    """Collapse an output to its echo-comparable form."""
    if not isinstance(raw, str):
        raw = "" if raw is None else str(raw)
    text = raw.strip().lower()
    try:
        text = json.dumps(json.loads(text), sort_keys=True, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    text = _PUNCT.sub(" ", text)
    return _WS.sub(" ", text).strip()


def echo_metrics(raws: Iterable[str]) -> dict:
    """Echo statistics over one (model, role) group's raw outputs."""
    outs = [normalize(r) for r in raws]
    n = len(outs)
    if n == 0:
        return {
            "n": 0,
            "distinct_outputs": 0,
            "distinct_output_ratio": 0.0,
            "modal_output_share": 0.0,
            "copy_suspect_n": 0,
            "copy_suspect": False,
        }
    counts = Counter(outs)
    modal = max(counts.values())
    distinct = len(counts)
    ratio = distinct / n
    return {
        "n": n,
        "distinct_outputs": distinct,
        "distinct_output_ratio": round(ratio, 3),
        "modal_output_share": round(modal / n, 3),
        "copy_suspect_n": modal,
        "copy_suspect": bool(n >= ECHO_MIN_N and ratio < ECHO_RATIO_THRESHOLD),
    }