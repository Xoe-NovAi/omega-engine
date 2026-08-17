# 🔱 Omega Engine — Sovereignty Gate (P0-2)
# ⬡ OMEGA ⬡ MA'AT ⬡ N5 ⬡ 2026-07-12
# AP: AP-SOVEREIGNTY-GATE-v1.0.0
#
# [heritage: sovereign-kliewer 2026] In-path governance — "no fast path that
# skips governance, no trusted caller that bypasses evaluation." This gate
# enforces Mandate 7 (Local-First) at the build boundary: the recorded local
# inference ratio must be >= MIN_LOCAL_RATIO.
#
# Reuses omega.observability.sovereignty.get_sovereignty_ratio(), which reads
# the MetricsDB `performance` table. The `is_cloud` field is set per-response
# by the ModelGateway (M22 Response Provenance), so the ratio is forensic, not
# configured intent.

import argparse
import logging
import sys
from pathlib import Path
from typing import Union

from omega.observability.sovereignty import get_sovereignty_ratio

logger = logging.getLogger(__name__)

DEFAULT_METRICS_DB = "data/observability/metrics.db"


class SovereigntyGate:
    """CI gate enforcing the local-first inference ratio (Mandate 7).

    [M7: Local-First] Local inference is PRIMARY; cloud is FALLBACK. This gate
    fails the build if the recorded local inference ratio drops below the
    threshold.
    """

    MIN_LOCAL_RATIO = 0.80

    def __init__(self, min_local_ratio: float = MIN_LOCAL_RATIO):
        self.min_local_ratio = min_local_ratio

    def check(self, metrics_db_path: Union[str, Path] = DEFAULT_METRICS_DB) -> bool:
        """Return True if the local inference ratio >= threshold.

        If no inference is recorded (empty/absent DB), returns True with a
        logged warning — sovereignty is violated only by *actual* cloud
        inference, never by the absence of inference. This keeps the gate
        honest in CI where models are not loaded (M23: no soft-failure, but
        also no false-positive on a system that performed zero inference).
        """
        report = get_sovereignty_ratio(metrics_db_path)
        total = report.get("total", 0)
        if total == 0:
            logger.warning(
                "SOVEREIGNTY GATE: no inference recorded (total=0) — passing (nothing to gate)"
            )
            return True
        ratio_local = report.get("ratio_local", 0.0)
        passed = ratio_local >= self.min_local_ratio
        if not passed:
            logger.error(
                "SOVEREIGNTY GATE FAILED: local ratio %.2f < threshold %.2f (total=%d)",
                ratio_local,
                self.min_local_ratio,
                total,
            )
        else:
            logger.info(
                "SOVEREIGNTY GATE PASSED: local ratio %.2f >= %.2f (total=%d)",
                ratio_local,
                self.min_local_ratio,
                total,
            )
        return passed

    def check_strict(self, metrics_db_path: Union[str, Path] = DEFAULT_METRICS_DB) -> bool:
        """Strict variant: no inference data => FAIL.

        Use in production CI that actually runs local inference — there, a
        missing metrics DB means the gate was never exercised, which is a
        sovereignty violation in its own right.
        """
        report = get_sovereignty_ratio(metrics_db_path)
        total = report.get("total", 0)
        if total == 0:
            logger.error("SOVEREIGNTY GATE (strict) FAILED: no inference recorded")
            return False
        ratio_local = report.get("ratio_local", 0.0)
        return ratio_local >= self.min_local_ratio


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Omega Sovereignty Gate (M7 Local-First)")
    parser.add_argument(
        "--min-ratio",
        type=float,
        default=SovereigntyGate.MIN_LOCAL_RATIO,
        help="Minimum local inference ratio (default 0.80)",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=DEFAULT_METRICS_DB,
        help="Path to MetricsDB (default data/observability/metrics.db)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if no inference is recorded (prod CI that runs real inference)",
    )
    args = parser.parse_args(argv)

    gate = SovereigntyGate(min_local_ratio=args.min_ratio)
    passed = gate.check_strict(args.db_path) if args.strict else gate.check(args.db_path)
    if passed:
        print(f"✅ SOVEREIGNTY GATE PASSED (local ratio >= {args.min_ratio})")
        return 0
    print(f"❌ SOVEREIGNTY GATE FAILED (local ratio < {args.min_ratio})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
