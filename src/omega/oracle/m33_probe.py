# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M33 Sentinel Probe
# ⬡ OMEGA ⬡ RESEARCHER ⬡ M33 ⬡ RUNTIME
# AP: AP-M33-PROBE-v1.0.0
#
# Per 5-EIS meta-review (RESEARCHER_META_REVIEW_20260830.md §4.1):
#   Layer 1 (Preventive): For reports > 8K tokens, require write_tool routing
#   Layer 2 (Structured Probe): JSON envelope with state, last_chunk_id, total_chunks,
#                                queued_findings, confidence
#   Layer 3 (Cross-Validator): P0/P1 tasks require second-agent verification (M36)
#
# Per meta-review §1.1: replaces free-form "STREAM_EXHAUSTED" string with structured
#   envelope (My amendment #2 + Jem's structured envelope)
# Per meta-review §1.1: addresses Jem's bypass attack (immediate STREAM_EXHAUSTED reply)
# Per meta-review §1.1: P0/P1 cross-validator tier (Jem §1.1.5 + my M36)
#
# [M23: Failure Integrity] Probe itself validated against schema (M36 meta-probe)
# [M15: Continuity] Probe output is preserved in checkpoint
# [M27: Tracking Integrity] Probe results audit-logged to M34 registry

"""
M33 Sentinel Probe — Anti-Truncation & Stream Exhaustion Gate

This module implements the M33 mandate: a subagent's state=completed
is necessary but not sufficient for semantic exhaustion. The probe
asks the subagent to provide a structured JSON envelope describing
its actual completion state.

Three layers of defense:
1. Preventive: at dispatch time, mark write_tool_required=True for
   research/forensic tasks with estimated >8K token output
2. Structured Probe: at completion, require JSON envelope with
   state, last_chunk_id, total_chunks, queued_findings, confidence
3. Cross-Validator: for P0/P1 tasks, dispatch a separate agent
   to verify the deliverable exists and meets requirements (M36)

Usage:
    from omega.oracle.m33_probe import M33Probe, CompletionEnvelope, ProbeVerdict

    probe = M33Probe(m34_registry=registry, subagent_id="ses_abc123")

    # Layer 2: Execute probe
    envelope = await probe.execute_probe(
        session_id="ses_abc123",
        expected_chunks=12,
        prompt_deliverable="data/coordination/R_FOO_20260830.md"
    )

    # Validate
    verdict = probe.validate_response(envelope)
    if verdict.accepted:
        # Mark subagent as COMPLETED in M34 registry
        ...
    elif verdict.retry_recommended:
        # Send "continue" prompt with structured resume
        ...
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

# ── Constants ────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# Per 5-EIS meta-review: free-form "STREAM_EXHAUSTED" string is REJECTED
PROHIBITED_FREE_FORM = ["STREAM_EXHAUSTED", "stream_exhausted", "DONE", "FINISHED",
                        "COMPLETE", "Mission complete", "All done"]

# Confidence threshold per meta-review: 0.95 for P2+, 0.85 for P3
CONFIDENCE_THRESHOLD_P0 = 0.99  # Cross-validator required (Layer 3)
CONFIDENCE_THRESHOLD_P1 = 0.97  # Cross-validator required (Layer 3)
CONFIDENCE_THRESHOLD_P2 = 0.95  # Structured probe only (Layer 2)
CONFIDENCE_THRESHOLD_P3 = 0.85  # Structured probe only (Layer 2)

# Write-tool routing threshold: 8K tokens (per meta-review §1.1)
WRITE_TOOL_TOKEN_THRESHOLD = 8000


# ── Envelope Schema (structured JSON completion marker) ─────────────────────

class CompletionState(str, Enum):
    """Subagent's reported completion state."""
    EXHAUSTED = "exhausted"      # All planned chunks written, nothing queued
    CONTINUING = "continuing"    # More chunks pending, will continue if prompted


@dataclass
class CompletionEnvelope:
    """Structured JSON completion marker (M33 schema).

    Replaces free-form STREAM_EXHAUSTED string. Required fields per
    5-EIS meta-review §1.1 amendment #2. The subagent MUST respond
    with this exact JSON shape; the orchestrator MUST validate it.
    """
    state: CompletionState                # "exhausted" | "continuing"
    last_chunk_id: int                    # Last chunk written (0-indexed)
    total_chunks: int                     # Total chunks planned
    queued_findings: List[str]            # Pending findings to write (empty if exhausted)
    confidence: float                     # 0.0-1.0 self-reported confidence
    deliverable_path: Optional[str] = None  # Where the deliverable was written
    deliverable_size_bytes: Optional[int] = None  # Size of deliverable
    structured_evidence: Optional[Dict[str, Any]] = None  # Optional: citations, etc.

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CompletionEnvelope":
        if "state" in d and isinstance(d["state"], str):
            d["state"] = CompletionState(d["state"])
        # Filter unknown fields for forward compatibility
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, s: str) -> "CompletionEnvelope":
        return cls.from_dict(json.loads(s))


# ── Verdict (validation result) ─────────────────────────────────────────────

@dataclass
class ProbeVerdict:
    """Result of validating a CompletionEnvelope."""
    accepted: bool                         # True if probe accepts completion
    retry_recommended: bool                # True if subagent should continue
    reason: str                            # Human-readable reason
    confidence_met: bool                   # Did confidence meet threshold?
    confidence_threshold: float            # Threshold that was applied
    cross_validation_required: bool        # P0/P1: needs M36
    cross_validation_agent: Optional[str] = None
    schema_valid: bool = True              # Did envelope match schema?
    free_form_detected: bool = False       # Was prohibited free-form string used?


# ── M33 Probe Class ─────────────────────────────────────────────────────────

class M34RegistryLike(Protocol):
    """Minimal M34 interface for probe integration (structural typing)."""
    def get(self, session_id: str) -> Optional[Dict[str, Any]]: ...
    def update_status(self, session_id: str, status: str,
                      checkpoint: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]: ...


class M33Probe:
    """Sentinel probe that detects truncated subagent output.

    Per 5-EIS meta-review §4.1: 3-layer fix (preventive + structured probe + P0/P1 cross-validator).
    """

    def __init__(self, m34_registry: M34RegistryLike, log_path: Optional[Path] = None):
        self.registry = m34_registry
        self.log_path = log_path or Path(
            os.environ.get(
                "OMEGA_M33_LOG",
                "data/coordination/m33_probe_audit.jsonl"
            )
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Layer 1: Preventive (at dispatch time) ──────────────────────

    def should_require_write_tool(
        self,
        estimated_output_tokens: int,
        task_type: str,
        priority: str,
    ) -> bool:
        """Layer 1: Decide if a subagent should be required to use write tool.

        Per meta-review §1.1: For reports > 8K tokens, the orchestrator must
        require the subagent to use the write tool, not the chat stream.

        Args:
            estimated_output_tokens: Estimated deliverable size in tokens
            task_type: "research" | "forensic" | "review" | "implement" | "design" | "verify"
            priority: "P0" | "P1" | "P2" | "P3"

        Returns:
            True if subagent should be flagged write_tool_required=True
        """
        # Per meta-review: 8K token threshold
        if estimated_output_tokens > WRITE_TOOL_TOKEN_THRESHOLD:
            return True
        # P0/P1 always require write tool (high-stakes deliverables)
        if priority in ("P0", "P1"):
            return True
        # Research/forensic tasks always require write tool (long-form)
        if task_type in ("research", "forensic", "review", "design"):
            return True
        return False

    # ── Layer 2: Structured Probe (at completion time) ──────────────

    def build_probe_prompt(
        self,
        session_id: str,
        expected_chunks: int,
        expected_deliverable: Optional[str],
    ) -> str:
        """Build the structured probe prompt (sent to subagent).

        Per meta-review §1.1: replaces free-form "STREAM_EXHAUSTED" probe
        with strict JSON envelope requirement.
        """
        deliverable_clause = (
            f"\nDeliverable path: {expected_deliverable}\n"
            f"Verify the file exists and is non-empty before reporting exhausted."
            if expected_deliverable else ""
        )

        return f"""M33 Sentinel Probe — Structured Completion Verification

Session ID: {session_id}
Expected chunks: {expected_chunks}{deliverable_clause}

You MUST respond with a single JSON object matching this exact schema:

{{
  "state": "exhausted" | "continuing",
  "last_chunk_id": <int, 0-indexed, last chunk you have written>,
  "total_chunks": <int, total chunks you planned to write>,
  "queued_findings": [<list of strings, pending findings (empty if exhausted)>],
  "confidence": <float 0.0-1.0, your honest confidence in completion>,
  "deliverable_path": "<string, path to your deliverable or null>",
  "deliverable_size_bytes": <int, size of deliverable in bytes or null>,
  "structured_evidence": {{<object, optional citations/evidence>}}  // optional
}}

CRITICAL RULES:
1. Do NOT reply with free-form text. Do NOT reply with "STREAM_EXHAUSTED" or "DONE".
2. Do NOT reply with markdown code fences. Pure JSON only.
3. If you have more findings to write, set state="continuing" and list them in queued_findings.
4. If you have written all planned chunks and the deliverable is complete, set state="exhausted"
   and queued_findings=[].
5. Confidence should reflect your honest assessment. 0.99 only if you are certain.
6. After your JSON response, STOP. Do not add commentary.

Begin JSON response now:"""

    def validate_response(
        self,
        response: Any,  # str (raw) or dict (parsed) or CompletionEnvelope
        session_id: Optional[str] = None,
        priority: str = "P2",
    ) -> ProbeVerdict:
        """Layer 2: Validate probe response against schema.

        Per 5-EIS meta-review §1.1: Reject free-form STREAM_EXHAUSTED, require
        JSON envelope, check confidence threshold, flag P0/P1 for cross-validation.
        """
        # Threshold based on priority
        threshold = {
            "P0": CONFIDENCE_THRESHOLD_P0,
            "P1": CONFIDENCE_THRESHOLD_P1,
            "P2": CONFIDENCE_THRESHOLD_P2,
            "P3": CONFIDENCE_THRESHOLD_P3,
        }.get(priority, CONFIDENCE_THRESHOLD_P2)

        # Detect free-form prohibited strings
        if isinstance(response, str):
            response_stripped = response.strip()
            for prohibited in PROHIBITED_FREE_FORM:
                if prohibited.lower() in response_stripped.lower():
                    return ProbeVerdict(
                        accepted=False,
                        retry_recommended=True,
                        reason=f"Free-form completion string detected: '{prohibited}'. "
                               f"Subagent must respond with structured JSON envelope per M33 schema.",
                        confidence_met=False,
                        confidence_threshold=threshold,
                        cross_validation_required=(priority in ("P0", "P1")),
                        schema_valid=False,
                        free_form_detected=True,
                    )
            # Try to parse as JSON
            try:
                response = json.loads(response_stripped)
            except json.JSONDecodeError as e:
                return ProbeVerdict(
                    accepted=False,
                    retry_recommended=True,
                    reason=f"Probe response is not valid JSON: {e}. Subagent must respond with structured JSON.",
                    confidence_met=False,
                    confidence_threshold=threshold,
                    cross_validation_required=(priority in ("P0", "P1")),
                    schema_valid=False,
                )

        # Convert dict to CompletionEnvelope
        if isinstance(response, dict):
            try:
                envelope = CompletionEnvelope.from_dict(response)
            except (TypeError, ValueError) as e:
                return ProbeVerdict(
                    accepted=False,
                    retry_recommended=True,
                    reason=f"Envelope schema mismatch: {e}. Required: state, last_chunk_id, total_chunks, queued_findings, confidence.",
                    confidence_met=False,
                    confidence_threshold=threshold,
                    cross_validation_required=(priority in ("P0", "P1")),
                    schema_valid=False,
                )
        elif isinstance(response, CompletionEnvelope):
            envelope = response
        else:
            return ProbeVerdict(
                accepted=False,
                retry_recommended=True,
                reason=f"Unexpected response type: {type(response).__name__}",
                confidence_met=False,
                confidence_threshold=threshold,
                cross_validation_required=(priority in ("P0", "P1")),
                schema_valid=False,
            )

        # Schema valid: check confidence threshold
        confidence_met = envelope.confidence >= threshold

        # P0/P1: require cross-validation (M36)
        if priority in ("P0", "P1"):
            return ProbeVerdict(
                accepted=False,  # Cannot accept P0/P1 without cross-validation
                retry_recommended=False,
                reason=f"P{priority[1]} task requires M36 cross-validation. Confidence {envelope.confidence:.3f} >= {threshold} OK, but cross-validator must confirm.",
                confidence_met=confidence_met,
                confidence_threshold=threshold,
                cross_validation_required=True,
                schema_valid=True,
            )

        # P2/P3: accept if confidence met and state=exhausted
        if not confidence_met:
            return ProbeVerdict(
                accepted=False,
                retry_recommended=True,
                reason=f"Confidence {envelope.confidence:.3f} < threshold {threshold} for {priority}. Subagent should continue.",
                confidence_met=False,
                confidence_threshold=threshold,
                cross_validation_required=False,
                schema_valid=True,
            )

        if envelope.state != CompletionState.EXHAUSTED:
            return ProbeVerdict(
                accepted=False,
                retry_recommended=True,
                reason=f"State is '{envelope.state.value}', not 'exhausted'. Subagent reports {len(envelope.queued_findings)} pending findings.",
                confidence_met=confidence_met,
                confidence_threshold=threshold,
                cross_validation_required=False,
                schema_valid=True,
            )

        # Verify deliverable exists if claimed
        if envelope.deliverable_path:
            p = Path(envelope.deliverable_path)
            if not p.exists():
                return ProbeVerdict(
                    accepted=False,
                    retry_recommended=True,
                    reason=f"Claimed deliverable does not exist: {envelope.deliverable_path}",
                    confidence_met=confidence_met,
                    confidence_threshold=threshold,
                    cross_validation_required=False,
                    schema_valid=True,
                )
            if envelope.deliverable_size_bytes and p.stat().st_size != envelope.deliverable_size_bytes:
                return ProbeVerdict(
                    accepted=False,
                    retry_recommended=True,
                    reason=f"Deliverable size mismatch: claimed {envelope.deliverable_size_bytes}, actual {p.stat().st_size}",
                    confidence_met=confidence_met,
                    confidence_threshold=threshold,
                    cross_validation_required=False,
                    schema_valid=True,
                )

        return ProbeVerdict(
            accepted=True,
            retry_recommended=False,
            reason=f"Probe accepted. State={envelope.state.value}, confidence={envelope.confidence:.3f} >= {threshold}, deliverable verified.",
            confidence_met=confidence_met,
            confidence_threshold=threshold,
            cross_validation_required=False,
            schema_valid=True,
        )

    # ── Layer 3: Cross-Validator trigger ────────────────────────────

    def should_cross_validate(self, session_id: str) -> bool:
        """Layer 3: Determine if a subagent needs M36 cross-validation.

        Returns True if the subagent is P0/P1 OR has cross_validator_agent set.
        """
        entry = self.registry.get(session_id)
        if not entry:
            return False
        # P0/P1 always cross-validate
        priority = entry.get("priority", "P2")
        if priority in ("P0", "P1"):
            return True
        # Explicit cross-validator agent assigned
        if entry.get("cross_validator_agent"):
            return True
        return False

    # ── Audit Logging ────────────────────────────────────────────────

    def audit_log(self, session_id: str, verdict: ProbeVerdict, envelope: Optional[CompletionEnvelope] = None) -> None:
        """Log probe result for M27 audit trail."""
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "verdict": asdict(verdict),
            "envelope": envelope.to_dict() if envelope else None,
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    # ── M36 Cross-Validator Wiring (Task A4) ─────────────────────────

    def complete_with_validation(
        self,
        response: Any,
        session_id: str,
        priority: str = "P2",
        expected_deliverable: Optional[str] = None,
        required_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """M33 completion callback that wires M36 cross-validator.

        Per Phase 1 HIGH-4 / Task A4: this is the M33 → M36 wiring point.
        When a subagent completes and M33 probe validates its envelope:
        1. If priority is P0/P1, dispatch M36 cross-validator via Hivemind
        2. Run hard verifier (file existence, size, hash) via spawn_local_worker pattern
        3. Return combined verdict

        Returns a dict with:
          - m33_verdict: ProbeVerdict
          - m36_result: CrossValidationResult (if P0/P1) or None
          - final_accepted: bool (M33 verdict + M36 verification)
        """
        # Layer 2: M33 envelope validation
        m33_verdict = self.validate_response(response, session_id=session_id, priority=priority)
        self.audit_log(session_id, m33_verdict)

        result: Dict[str, Any] = {
            "m33_verdict": m33_verdict,
            "m36_result": None,
            "final_accepted": m33_verdict.accepted,
        }

        # P2/P3: M33 acceptance is sufficient (no M36)
        if priority not in ("P0", "P1"):
            return result

        # P0/P1: require M36 cross-validation
        if not m33_verdict.schema_valid or m33_verdict.free_form_detected:
            # M33 already rejected — don't bother with M36
            return result

        # Extract envelope from response for M36
        envelope: Optional[CompletionEnvelope] = None
        if isinstance(response, CompletionEnvelope):
            envelope = response
        elif isinstance(response, dict):
            try:
                envelope = CompletionEnvelope.from_dict(response)
            except (TypeError, ValueError) as dict_exc:
                logger.debug("Envelope dict parse failed: %s", dict_exc)
        elif isinstance(response, str):
            try:
                envelope = CompletionEnvelope.from_json(response)
            except (json.JSONDecodeError, ValueError, TypeError) as json_exc:
                logger.debug("Envelope JSON parse failed: %s", json_exc)

        if envelope is None:
            result["final_accepted"] = False
            return result

        # Layer 3: M36 cross-validation
        try:
            from .m36_recursive_probe import M36RecursiveProbe
            m36 = M36RecursiveProbe(m34_registry=self.registry, m33_probe=self)
            deliverable = expected_deliverable or envelope.deliverable_path
            m36_result = m36.cross_validate(
                session_id=session_id,
                envelope=envelope,
                expected_deliverable=deliverable,
                priority=priority,
                required_keywords=required_keywords,
            )
            result["m36_result"] = m36_result
            # Final acceptance requires M33 + M36
            result["final_accepted"] = m33_verdict.accepted and m36_result.verified
        except ImportError as m36_exc:
            # M36 not available — fall back to M33 verdict
            logger.debug("M36 cross-validator not available: %s", m36_exc)

        return result


# ── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    """CLI: m33-probe <session_id> [--expected-chunks N] [--deliverable PATH] [--priority P0|P1|P2|P3]"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="M33 Sentinel Probe — validate subagent completion")
    parser.add_argument("session_id", help="Subagent session ID")
    parser.add_argument("--expected-chunks", type=int, default=10)
    parser.add_argument("--deliverable", type=str, default=None)
    parser.add_argument("--priority", type=str, default="P2", choices=["P0", "P1", "P2", "P3"])
    parser.add_argument("--probe-response", type=str, default=None, help="Raw response to validate (JSON or file path)")
    args = parser.parse_args()

    probe = M33Probe(m34_registry=None)  # type: ignore

    if args.probe_response:
        # Validate mode
        response = args.probe_response
        if os.path.isfile(response):
            with open(response) as f:
                response = f.read()
        verdict = probe.validate_response(response, args.session_id, args.priority)
        print(json.dumps(asdict(verdict), indent=2))
        sys.exit(0 if verdict.accepted else 1)
    else:
        # Build prompt mode
        prompt = probe.build_probe_prompt(args.session_id, args.expected_chunks, args.deliverable)
        print(prompt)


if __name__ == "__main__":
    main()
