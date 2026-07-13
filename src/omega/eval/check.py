# 🔱 Omega Engine — Eval Result & Checker
# AP: AP-EVAL-CHECK-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ eval.check ⬡ S2
#
# Threshold checker for eval results.
# [heritage: ragas-2024] Evaluation metric vocabulary (faithfulness, etc.)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EvalResult:
    """Aggregated evaluation result for a golden dataset run.

    [S7 cross-link] ``audience_fit`` (0-1) scores whether the output matches the
    target audience's register (tone_preference + technical_level). Closes the
    input/output architectural asymmetry: sophisticated intent detection on
    input, now matched by register verification on output.
    """

    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    audience_fit: float = 1.0  # 1.0 when no audience profile is evaluated
    passed: bool = False
    n_samples: int = 0
    per_sample: List[Dict] = field(default_factory=list)
    details: Dict = field(default_factory=dict)


class EvalChecker:
    """Check eval results against configured thresholds."""

    DEFAULT_THRESHOLDS: Dict[str, float] = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": 0.75,
        "context_recall": 0.80,
    }

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)

    def check(self, result: EvalResult) -> bool:
        """Return True if all metrics meet thresholds."""
        for metric, threshold in self.thresholds.items():
            score = getattr(result, metric, None)
            if score is None:
                logger_missing(metric)
                return False
            if score < threshold:
                return False
        return True

    def failing_metrics(self, result: EvalResult) -> List[str]:
        """Return the list of metrics that fell below threshold."""
        failing = []
        for metric, threshold in self.thresholds.items():
            score = getattr(result, metric, None)
            if score is None or score < threshold:
                failing.append(metric)
        return failing


def logger_missing(metric: str) -> None:
    import logging
    logging.getLogger(__name__).warning("EvalResult missing metric %s — failing check", metric)
