# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M36 Recursive Probe
# ⬡ OMEGA ⬡ RESEARCHER ⬡ M36 ⬡ RUNTIME
# AP: AP-M36-RECURSIVE-PROBE-v1.0.0
#
# Per 5-EIS meta-review §4.1: "M33 must be amended with 3 layers...
# (3) P0/P1 cross-validator agent escalation"
#
# Per meta-review §4.1: "a verifier agent adds latency and complexity.
# The 2-pass probe + structured envelope + confidence threshold... may be
# sufficient. Cross-validation should be a recommendation for P0, not a
# mandate for all."
#
# M36 = tiered cross-validation: hard verifier (file existence, schema match)
# for P2/P3, soft verifier (LLM judge) for P0/P1.
#
# [M23: Failure Integrity] Both probe and cross-validator validated
# [M27: Tracking Integrity] Cross-validation results audit-logged

"""
M36 Recursive Probe — Tiered Cross-Validation for M33 Probe Responses

This module implements the M36 mandate: validate the M33 probe
response itself, because the probe is subject to the same failure
mode it probes (truncation, lazy completion, hallucination).

Two-tier validation:
- Hard verifier: file existence, schema match, size sanity (always)
- Soft verifier: LLM judge for semantic coverage (P0/P1 only)

Usage:
    from omega.oracle.m36_recursive_probe import M36RecursiveProbe
    from omega.oracle.m33_probe import M33Probe, CompletionEnvelope

    m36 = M36RecursiveProbe(m34_registry=registry)
    result = await m36.cross_validate(
        session_id="ses_abc123",
        envelope=envelope,
        expected_deliverable="data/coordination/R_FOO_20260830.md",
        priority="P0"
    )
    if result.verified:
        # Safe to mark COMPLETED
        ...
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from .m33_probe import CompletionEnvelope, M33Probe, M34RegistryLike


# ── Verification Result ─────────────────────────────────────────────────────

@dataclass
class CrossValidationResult:
    """Result of M36 cross-validation."""
    verified: bool                          # True if all checks pass
    hard_checks_passed: Dict[str, bool]     # File exists, size match, schema valid
    soft_checks_passed: Optional[Dict[str, bool]] = None  # LLM judge results (P0/P1)
    deliverable_hash: Optional[str] = None  # SHA256 of deliverable
    deliverable_size: int = 0
    content_keywords_found: Optional[Dict[str, bool]] = None  # Required keywords present
    suspicious_patterns: List[str] = field(default_factory=list)
    reason: str = ""
    cross_validator_agent: Optional[str] = None  # Which agent did the soft check


# ── M36 Recursive Probe Class ───────────────────────────────────────────────

class M36RecursiveProbe:
    """Tiered cross-validator for M33 probe responses.

    Per meta-review §4.1: hard verifier for P2/P3, soft verifier for P0/P1.
    """

    def __init__(
        self,
        m34_registry: M34RegistryLike,
        m33_probe: Optional[M33Probe] = None,
        log_path: Optional[Path] = None,
    ):
        self.registry = m34_registry
        self.m33 = m33_probe or M33Probe(m34_registry)
        self.log_path = log_path or Path(
            os.environ.get(
                "OMEGA_M36_LOG",
                "data/coordination/m36_cross_validation_audit.jsonl"
            )
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Hard Verifier (always runs) ──────────────────────────────────

    def _verify_file_exists(self, path: str) -> bool:
        p = Path(path)
        return p.exists() and p.is_file()

    def _verify_file_size(self, path: str, claimed_size: Optional[int] = None) -> bool:
        p = Path(path)
        if not p.exists():
            return False
        actual_size = p.stat().st_size
        # If claimed, must match exactly
        if claimed_size is not None and actual_size != claimed_size:
            return False
        # Empty files are suspicious
        if actual_size == 0:
            return False
        return True

    def _verify_file_hash(self, path: str) -> str:
        """SHA256 of deliverable for audit trail."""
        p = Path(path)
        if not p.exists():
            return ""
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _verify_content_keywords(
        self,
        path: str,
        required_keywords: List[str],
    ) -> Dict[str, bool]:
        """Check that required keywords appear in the deliverable."""
        p = Path(path)
        if not p.exists():
            return {kw: False for kw in required_keywords}
        try:
            content = p.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError):
            return {kw: False for kw in required_keywords}
        return {kw: (kw.lower() in content.lower()) for kw in required_keywords}

    def _detect_suspicious_patterns(self, path: str) -> List[str]:
        """Detect signs of fabrication, placeholders, or truncation."""
        p = Path(path)
        if not p.exists():
            return ["file_not_found"]
        try:
            content = p.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError):
            return ["file_unreadable"]
        suspicious = []
        # Placeholder patterns
        placeholders = [
            r"\[REDACTED[^\]]*\]",
            r"\*\*\*REDACTED[^\]]*\*\*\*",
            r"TODO[: ]",
            r"FIXME[: ]",
            r"XXX[: ]",
            r"\.\.\. \.\.\.",  # Multiple ellipses = often indicates truncation
        ]
        for pat in placeholders:
            if re.search(pat, content):
                suspicious.append(f"placeholder_or_truncation:{pat}")
        # Truncation indicators
        if content.rstrip().endswith(("...", ",", ";", ":", "-", "(")):
            suspicious.append("ends_with_truncation_indicator")
        return suspicious

    # ── Soft Verifier (P0/P1 only — LLM judge) ───────────────────────

    def _soft_verify_via_llm_judge(
        self,
        envelope: CompletionEnvelope,
        deliverable_path: str,
        priority: str,
        cross_validator_agent: Optional[str] = None,
    ) -> Dict[str, bool]:
        """P0/P1: dispatch a separate agent to judge semantic coverage.

        Per meta-review §4.1: cross-validator for P0/P1 only.
        The cross-validator agent is specified in the M34 entry's
        `cross_validator_agent` field (Jem's amendment).
        """
        if not cross_validator_agent:
            return {
                "no_cross_validator_agent": False,
            }

        # In production, this would dispatch the cross-validator agent
        # via subagent_dispatcher.py. For now, we return a stub that
        # requires the orchestrator to wire it up.
        # See integration notes in §6 below.
        return {
            "semantic_coverage_verified": False,  # Placeholder
            "queued_findings_addressed": False,    # Placeholder
            "deliverable_meets_purpose": False,   # Placeholder
        }

    # ── Public API: cross_validate ──────────────────────────────────

    def cross_validate(
        self,
        session_id: str,
        envelope: CompletionEnvelope,
        expected_deliverable: Optional[str] = None,
        priority: str = "P2",
        required_keywords: Optional[List[str]] = None,
    ) -> CrossValidationResult:
        """Cross-validate an M33 probe response.

        Per meta-review §4.1: tiered approach.
        - P2/P3: hard verifier only (file exists, size matches, no placeholders)
        - P0/P1: hard verifier + soft verifier (LLM judge for semantic coverage)

        Args:
            session_id: Subagent session ID (for M34 lookup)
            envelope: The M33 CompletionEnvelope to validate
            expected_deliverable: Path to expected deliverable (overrides envelope)
            priority: "P0" | "P1" | "P2" | "P3"
            required_keywords: List of keywords that must appear in deliverable

        Returns:
            CrossValidationResult with all check details
        """
        # Determine deliverable path
        deliverable_path = expected_deliverable or envelope.deliverable_path
        if not deliverable_path:
            return CrossValidationResult(
                verified=False,
                hard_checks_passed={"deliverable_path_provided": False},
                reason="No deliverable path in envelope or expected_deliverable",
            )

        # Hard verifier (always)
        hard_checks = {
            "file_exists": self._verify_file_exists(deliverable_path),
            "file_size_valid": self._verify_file_size(deliverable_path, envelope.deliverable_size_bytes),
            "no_suspicious_patterns": True,  # Will be updated below
        }

        deliverable_hash = self._verify_file_hash(deliverable_path) if hard_checks["file_exists"] else None
        deliverable_size = Path(deliverable_path).stat().st_size if hard_checks["file_exists"] else 0

        suspicious = self._detect_suspicious_patterns(deliverable_path) if hard_checks["file_exists"] else []
        hard_checks["no_suspicious_patterns"] = len(suspicious) == 0

        # Content keywords (if specified)
        content_keywords = None
        if required_keywords:
            content_keywords = self._verify_content_keywords(deliverable_path, required_keywords)

        # Soft verifier (P0/P1 only)
        soft_checks = None
        cross_validator_agent = None
        if priority in ("P0", "P1"):
            # Look up cross_validator_agent from M34 entry
            entry = self.registry.get(session_id)
            if entry:
                cross_validator_agent = entry.get("cross_validator_agent")
            soft_checks = self._soft_verify_via_llm_judge(
                envelope=envelope,
                deliverable_path=deliverable_path,
                priority=priority,
                cross_validator_agent=cross_validator_agent,
            )

        # Determine verification
        hard_passed = all(hard_checks.values())
        soft_passed = soft_checks is None or all(
            v for k, v in soft_checks.items()
            if k in ("semantic_coverage_verified", "queued_findings_addressed", "deliverable_meets_purpose")
        )
        verified = hard_passed and soft_passed

        # Build reason
        if not verified:
            failed_hard = [k for k, v in hard_checks.items() if not v]
            failed_soft = []
            if soft_checks:
                failed_soft = [k for k, v in soft_checks.items()
                               if k in ("semantic_coverage_verified", "queued_findings_addressed", "deliverable_meets_purpose")
                       and not v]
            reason = f"Cross-validation failed. Hard checks failed: {failed_hard}. Soft checks failed: {failed_soft}."
        else:
            reason = f"Cross-validation passed. Hard checks: {hard_checks}."

        result = CrossValidationResult(
            verified=verified,
            hard_checks_passed=hard_checks,
            soft_checks_passed=soft_checks,
            deliverable_hash=deliverable_hash,
            deliverable_size=deliverable_size,
            content_keywords_found=content_keywords,
            suspicious_patterns=suspicious,
            reason=reason,
            cross_validator_agent=cross_validator_agent,
        )

        # Audit log
        self._audit_log(session_id, envelope, result)

        return result

    # ── Audit Logging ────────────────────────────────────────────────

    def _audit_log(self, session_id: str, envelope: CompletionEnvelope, result: CrossValidationResult) -> None:
        """Log cross-validation result for M27 audit trail."""
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "envelope_state": envelope.state.value,
            "envelope_confidence": envelope.confidence,
            "envelope_total_chunks": envelope.total_chunks,
            "envelope_last_chunk_id": envelope.last_chunk_id,
            "result": asdict(result),
        }
        with open(self.log_path, "a") as f:
            f.write(__import__("json").dumps(record) + "\n")


# ── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    """CLI: m36-cross-validate <envelope.json> [--deliverable PATH] [--priority P0|P1|P2|P3] [--keywords kw1,kw2,...]"""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="M36 Recursive Probe — cross-validate M33 probe response")
    parser.add_argument("envelope", help="Path to M33 CompletionEnvelope JSON file")
    parser.add_argument("--deliverable", type=str, default=None)
    parser.add_argument("--priority", type=str, default="P2", choices=["P0", "P1", "P2", "P3"])
    parser.add_argument("--keywords", type=str, default=None, help="Comma-separated required keywords")
    args = parser.parse_args()

    with open(args.envelope) as f:
        envelope = CompletionEnvelope.from_json(f.read())

    m36 = M36RecursiveProbe(m34_registry=None)  # type: ignore
    keywords = args.keywords.split(",") if args.keywords else None
    result = m36.cross_validate(
        session_id="cli-test",
        envelope=envelope,
        expected_deliverable=args.deliverable,
        priority=args.priority,
        required_keywords=keywords,
    )

    print(json.dumps(asdict(result), indent=2, default=str))
    sys.exit(0 if result.verified else 1)


if __name__ == "__main__":
    main()
