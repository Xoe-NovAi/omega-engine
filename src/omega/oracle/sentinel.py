# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SENTINEL-SCORE-v1.0.0
"""
🔱 SENTINEL SCORE AUTOMATION
Role: S5 Governance Metric Engine.
Computes the "Sentinel Score" — a weighted composite of 7 sub-metrics
that measure the engine's documentation hygiene and mandate compliance.

Follows the definition in data/reviews/opt_final_p5_governance.md.
"""

import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from dataclasses import dataclass, field

import anyio

logger = logging.getLogger("sentinel")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Weights from opt_final_p5_governance.md
WEIGHTS = {
    "decision_clock_drift": 0.20,
    "unprocessed_proposals": 0.15,
    "stale_file_burden": 0.15,
    "soul_compliance": 0.15,
    "handoff_completion": 0.15,
    "heritage_coverage": 0.10,
    "proposal_cycle_time": 0.10,
}

# Thresholds
THRESHOLD_GREEN = 80
THRESHOLD_YELLOW = 60

# Tracking Directories (Sovereign-by-Design)
TRACKED_DIRS = [
    "data/entities",
    "data/coordination",
    "data/handoff",
    "docs/strategy",
    "docs/research",
]

# ============================================================================
# MODELS
# ============================================================================


@dataclass
class SubMetric:
    name: str
    value: float  # Raw value
    score: float  # Normalized 0-100
    weight: float
    status: str  # "Green", "Yellow", "Red"
    details: str


@dataclass
class SentinelResult:
    total_score: float
    grade: str
    metrics: Dict[str, SubMetric]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# SENTINEL ENGINE
# ============================================================================


class SentinelScore:
    """
    Computes the composite Sentinel Score for the Omega Engine.

    The score is a measure of 'Tracking Debt' — the gap between
    architectural intent and documented reality.
    """

    def __init__(self, hivemind_client=None):
        self.hivemind = hivemind_client
        self.data_dir = Path(os.environ.get("OMEGA_DATA_DIR", "data"))

    async def compute_score(self) -> SentinelResult:
        """Compute all 7 sub-metrics and return the weighted composite."""
        metrics = {}

        # 1. Decision Clock Drift (20%)
        metrics["decision_clock_drift"] = await self._metric_decision_drift()

        # 2. Unprocessed Proposals Ratio (15%)
        metrics["unprocessed_proposals"] = await self._metric_unprocessed_proposals()

        # 3. Stale File Burden (15%)
        metrics["stale_file_burden"] = await self._metric_stale_files()

        # 4. Soul Compliance (15%)
        metrics["soul_compliance"] = await self._metric_soul_compliance()

        # 5. Handoff Completion Rate (15%)
        metrics["handoff_completion"] = await self._metric_handoff_completion()

        # 6. Heritage Tag Coverage (10%)
        metrics["heritage_coverage"] = await self._metric_heritage_coverage()

        # 7. Proposal-to-Soul Cycle Time (10%)
        metrics["proposal_cycle_time"] = await self._metric_proposal_cycle()

        # Calculate weighted total
        total_score = 0.0
        for name, metric in metrics.items():
            total_score += metric.score * WEIGHTS.get(name, 0.0)

        # Determine grade
        if total_score >= THRESHOLD_GREEN:
            grade = "Green"
        elif total_score >= THRESHOLD_YELLOW:
            grade = "Yellow"
        else:
            grade = "Red"

        return SentinelResult(total_score=round(total_score, 2), grade=grade, metrics=metrics)

    # ── Sub-Metric Implementations ──────────────────────────────────────────

    async def _metric_decision_drift(self) -> SubMetric:
        """Metric 1: Decision Clock Drift.
        Measures duplicate and out-of-sequence decisions in PIVOT_LOG.md.
        Target: 0 duplicates.
        """
        pivot_log = self.data_dir.parent / "docs/decisions/PIVOT_LOG.md"
        if not pivot_log.exists():
            return SubMetric(
                "Decision Clock Drift",
                0,
                0,
                WEIGHTS["decision_clock_drift"],
                "Red",
                "PIVOT_LOG.md missing",
            )

        content = await anyio.Path(pivot_log).read_text()
        # Find all "Decision XXX" headers
        decisions = re.findall(r"Decision (\d+)", content)

        duplicates = len(decisions) - len(set(decisions))
        # Check for sequence (simplified: check if sorted)
        is_sorted = decisions == sorted(decisions)

        drift_value = duplicates + (0 if is_sorted else 5)
        # Score: 100 if 0 drift, drops quickly
        score = max(0, 100 - (drift_value * 10))

        return SubMetric(
            name="Decision Clock Drift",
            value=float(drift_value),
            score=score,
            weight=WEIGHTS["decision_clock_drift"],
            status="Green" if drift_value == 0 else "Yellow" if drift_value < 5 else "Red",
            details=f"{duplicates} duplicates, sorted={is_sorted}",
        )

    async def _metric_unprocessed_proposals(self) -> SubMetric:
        """Metric 2: Unprocessed Proposals Ratio.
        Unprocessed proposals / total entities. Target: < 2 avg.
        """
        total_proposals = 0
        entity_count = 0

        entity_dir = self.data_dir / "entities"
        if not entity_dir.exists():
            return SubMetric(
                "Unprocessed Proposals",
                0,
                0,
                WEIGHTS["unprocessed_proposals"],
                "Red",
                "Entities dir missing",
            )

        async for ent_dir in anyio.Path(entity_dir).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue

            entity_count += 1
            prop_file = ent_dir / "proposed_lessons.yaml"
            if await anyio.Path(prop_file).exists():
                content = await anyio.Path(prop_file).read_text()
                # Simple count of "status: pending"
                total_proposals += content.count("status: pending")

        if entity_count == 0:
            return SubMetric(
                "Unprocessed Proposals",
                0,
                100,
                WEIGHTS["unprocessed_proposals"],
                "Green",
                "No entities",
            )

        ratio = total_proposals / entity_count
        # Score: 100 if ratio < 2, 0 if ratio > 10
        score = max(0, min(100, 100 - (ratio - 2) * 12.5))

        return SubMetric(
            name="Unprocessed Proposals",
            value=ratio,
            score=score,
            weight=WEIGHTS["unprocessed_proposals"],
            status="Green" if ratio < 2 else "Yellow" if ratio < 5 else "Red",
            details=f"{total_proposals} pending across {entity_count} entities (avg {ratio:.1f})",
        )

    async def _metric_stale_files(self) -> SubMetric:
        """Metric 3: Stale File Burden.
        Files > 14 days old in tracked stores. Target: < 10%.
        """
        total_files = 0
        stale_files = 0
        now = time.time()

        for d in TRACKED_DIRS:
            path = self.data_dir / d
            if not path.exists():
                continue

            # Recursive glob
            async for file in anyio.Path(path).glob("**/*"):
                if await anyio.Path(file).is_file():
                    total_files += 1
                    stat = await anyio.Path(file).stat()
                    if now - stat.st_mtime > (14 * 86400):
                        stale_files += 1

        if total_files == 0:
            return SubMetric(
                "Stale File Burden",
                0,
                100,
                WEIGHTS["stale_file_burden"],
                "Green",
                "No tracked files",
            )

        ratio = stale_files / total_files
        # Score: 100 if ratio < 0.1, 0 if ratio > 0.3
        score = max(0, min(100, 100 - (ratio - 0.1) * 500))

        return SubMetric(
            name="Stale File Burden",
            value=ratio,
            score=score,
            weight=WEIGHTS["stale_file_burden"],
            status="Green" if ratio < 0.1 else "Yellow" if ratio < 0.2 else "Red",
            details=f"{stale_files}/{total_files} files stale ({ratio:.1%})",
        )

    async def _metric_soul_compliance(self) -> SubMetric:
        """Metric 4: Soul Compliance.
        % entities on v6.0 soul format. Target: > 90%.
        """
        compliant = 0
        total = 0

        entity_dir = self.data_dir / "entities"
        if not entity_dir.exists():
            return SubMetric(
                "Soul Compliance", 0, 0, WEIGHTS["soul_compliance"], "Red", "Entities dir missing"
            )

        async for ent_dir in anyio.Path(entity_dir).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue

            total += 1
            soul_file = ent_dir / "soul.yaml"
            if await anyio.Path(soul_file).exists():
                content = await anyio.Path(soul_file).read_text()
                if "version: v6.0" in content or "version: v6.1" in content:
                    compliant += 1

        if total == 0:
            return SubMetric(
                "Soul Compliance", 0, 100, WEIGHTS["soul_compliance"], "Green", "No entities"
            )

        ratio = compliant / total
        score = ratio * 100

        return SubMetric(
            name="Soul Compliance",
            value=ratio,
            score=score,
            weight=WEIGHTS["soul_compliance"],
            status="Green" if ratio > 0.9 else "Yellow" if ratio > 0.5 else "Red",
            details=f"{compliant}/{total} entities compliant ({ratio:.1%})",
        )

    async def _metric_handoff_completion(self) -> SubMetric:
        """Metric 5: Handoff Completion Rate.
        Completed / total handoffs. Target: > 80%.
        """
        if not self.hivemind:
            return SubMetric(
                "Handoff Completion",
                0,
                50,
                WEIGHTS["handoff_completion"],
                "Yellow",
                "Hivemind client not provided",
            )

        try:
            metrics = await self.hivemind.get_metrics()
            # Expecting metrics to have handoff counts
            # This is a mock-up of the expected Hivemind response structure
            completed = metrics.get("handoffs", {}).get("completed", 0)
            total = metrics.get("handoffs", {}).get("total", 0)

            if total == 0:
                return SubMetric(
                    "Handoff Completion",
                    0,
                    100,
                    WEIGHTS["handoff_completion"],
                    "Green",
                    "No handoffs",
                )

            ratio = completed / total
            score = ratio * 100

            return SubMetric(
                name="Handoff Completion",
                value=ratio,
                score=score,
                weight=WEIGHTS["handoff_completion"],
                status="Green" if ratio > 0.8 else "Yellow" if ratio > 0.5 else "Red",
                details=f"{completed}/{total} handoffs completed ({ratio:.1%})",
            )
        except Exception as e:
            logger.error(f"Failed to fetch Hivemind metrics for Sentinel: {e}")
            return SubMetric(
                "Handoff Completion",
                0,
                0,
                WEIGHTS["handoff_completion"],
                "Red",
                f"Hivemind error: {e}",
            )

    async def _metric_heritage_coverage(self) -> SubMetric:
        """Metric 6: Heritage Tag Coverage.
        Heritage files with id-soft inline tags (format documented in CREDITS.md). Target: > 80%.
        """
        tagged = 0
        eligible = 0

        # Define what makes a file "heritage-eligible" (e.g., in a heritage dir or containing heritage keywords)
        # For this automation, we'll scan for files that mention "id Software" or "heritage" but lack the tag.

        async for path in self.data_dir.parent.glob("**/*.md"):
            if "heritage" in str(path).lower() or "legacy" in str(path).lower():
                eligible += 1
                content = await anyio.Path(path).read_text()
                if "[id-soft:" in content:
                    tagged += 1

        if eligible == 0:
            return SubMetric(
                "Heritage Coverage",
                0,
                100,
                WEIGHTS["heritage_coverage"],
                "Green",
                "No heritage files found",
            )

        ratio = tagged / eligible
        score = ratio * 100

        return SubMetric(
            name="Heritage Coverage",
            value=ratio,
            score=score,
            weight=WEIGHTS["heritage_coverage"],
            status="Green" if ratio > 0.8 else "Yellow" if ratio > 0.5 else "Red",
            details=f"{tagged}/{eligible} heritage files tagged ({ratio:.1%})",
        )

    async def _metric_proposal_cycle(self) -> SubMetric:
        """Metric 7: Proposal-to-Soul Cycle Time.
        Avg days from proposal -> soul.yaml. Target: < 7 days.
        """
        total_days = 0
        count = 0

        entity_dir = self.data_dir / "entities"
        if not entity_dir.exists():
            return SubMetric(
                "Proposal Cycle Time",
                0,
                0,
                WEIGHTS["proposal_cycle_time"],
                "Red",
                "Entities dir missing",
            )

        async for ent_dir in anyio.Path(entity_dir).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue

            prop_file = ent_dir / "proposed_lessons.yaml"
            if await anyio.Path(prop_file).exists():
                content = await anyio.Path(prop_file).read_text()
                # Find approved proposals and calculate diff
                # This is a simplified regex-based parser for the canonical schema
                matches = re.findall(
                    r"created_at: \"([^\"]+)\".*?approved_at: \"([^\"]+)\"", content, re.DOTALL
                )
                for created, approved in matches:
                    try:
                        d1 = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        d2 = datetime.fromisoformat(approved.replace("Z", "+00:00"))
                        total_days += (d2 - d1).days
                        count += 1
                    except ValueError:
                        continue

        if count == 0:
            return SubMetric(
                "Proposal Cycle Time",
                0,
                50,
                WEIGHTS["proposal_cycle_time"],
                "Yellow",
                "No approved proposals to measure",
            )

        avg_days = total_days / count
        # Score: 100 if < 7 days, 0 if > 30 days
        score = max(0, min(100, 100 - (avg_days - 7) * 4.16))

        return SubMetric(
            name="Proposal Cycle Time",
            value=avg_days,
            score=score,
            weight=WEIGHTS["proposal_cycle_time"],
            status="Green" if avg_days < 7 else "Yellow" if avg_days < 14 else "Red",
            details=f"Average cycle: {avg_days:.1f} days",
        )

    async def generate_pulse_report(self, result: SentinelResult) -> str:
        """Generate the 'Governance Pulse' Hivemind post."""
        lines = [
            "Entity: S5 Governance",
            "Intent: status",
            f"Sentinel Score: {result.total_score}/100 {self._get_emoji(result.grade)}",
            "Top Issue: " + self._get_top_issue(result),
            f"Metrics Breakdown:",
        ]
        for name, m in result.metrics.items():
            lines.append(f"- {name}: {m.score:.1f} ({m.details})")

        lines.append("\nTrend: " + self._get_trend(result))
        lines.append("Continuation: " + self._get_recommendation(result))

        return "\n".join(lines)

    def _get_emoji(self, grade: str) -> str:
        return {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}.get(grade, "⚪")

    def _get_top_issue(self, result: SentinelResult) -> str:
        # Find the metric with the lowest score
        worst = min(result.metrics.values(), key=lambda x: x.score)
        return f"{worst.name} is critical ({worst.score:.1f}) - {worst.details}"

    def _get_trend(self, result: SentinelResult) -> str:
        # In a real system, this would compare against a history file
        return "Stable (Baseline)"

    def _get_recommendation(self, result: SentinelResult) -> str:
        if result.grade == "Red":
            return "Sovereign Debt is critical. Schedule mandatory cleanup day and block non-critical sessions."
        if result.grade == "Yellow":
            return "Notify @verity for audit and prioritize proposal review pipeline."
        return "Hygiene is healthy. Continue normal operations."
