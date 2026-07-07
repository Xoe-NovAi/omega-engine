# AP: AP-Sovereign-Hardening-v1.0.0
# 🔱 Omega Engine — FailureModeRegistry (M17 Cognitive Integrity)
# Generic failure mode detection with WAD-configurable naming.
#
# The engine uses descriptive English names. The WAD layer (e.g.,
# Arcana-NovAi) can map these to esoteric names via entities.yaml
# or a failure_modes.yaml WAD config. See M2 Engine-Stack Firewall.
#
# Ported from xna-omega-legacy Mnemosyne (claude_sonnet_4.6_20260426.md).

"""FailureModeRegistry — M17 Cognitive Integrity.

Five named failure modes with pattern-based detection, recovery paths,
and purity scoring. Engine-core uses generic English names; the WAD
layer provides esoteric mappings if desired.

Failure Modes (engine-generic):
    REDIS_LOSS     — Redis/cache loss → local fallback
    LEGACY_ROT     — Legacy import paths → migration detection
    TELEMETRY_LEAK — Telemetry references → zero-telemetry enforcement
    DUAL_IMPL      — Dual implementations → architectural anti-pattern
    DEAD_CODE      — Unused modules → dead code detection
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import logging

logger = logging.getLogger(__name__)


# ── Severity & Finding Types ──────────────────────────────────────────

class Severity(str, Enum):
    """Severity levels for failure mode findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class Finding:
    """A single detection result from a failure mode scanner."""
    name: str
    severity: Severity
    description: str
    match_preview: str = ""
    failure_mode: str = ""


@dataclass(frozen=True, slots=True)
class RecoveryPath:
    """A typed recovery action for a failure mode."""
    mode: str
    action: str
    description: str
    auto_recover: bool = False


# ── Pattern Registry ──────────────────────────────────────────────────

@dataclass(slots=True)
class PatternDef:
    """A single detection pattern."""
    name: str
    pattern: re.Pattern[str]
    severity: Severity
    description: str
    failure_mode: str


# Severity → purity deduction weights
SEVERITY_WEIGHT: Dict[Severity, float] = {
    Severity.CRITICAL: 0.40,
    Severity.HIGH: 0.20,
    Severity.MEDIUM: 0.10,
    Severity.LOW: 0.05,
}

# ── Detection Patterns (generic engine names) ─────────────────────────
# Esoteric name mapping (e.g., LEGACY_ROT → "BELIAL") is WAD-layer config.

_PATTERNS: List[PatternDef] = [
    # ── LEGACY_ROT: Legacy import paths ────────────────────────────────
    PatternDef(
        name="legacy_path_slash",
        pattern=re.compile(r"app[/\\]src\.omega|src\.omega\.", re.IGNORECASE),
        severity=Severity.MEDIUM,
        description="Legacy src.omega path detected — migrate to src/omega/",
        failure_mode="LEGACY_ROT",
    ),
    PatternDef(
        name="legacy_import_statement",
        pattern=re.compile(
            r"from\s+src\.omega\s+import|import\s+src\.omega", re.IGNORECASE
        ),
        severity=Severity.MEDIUM,
        description="Legacy src.omega import detected",
        failure_mode="LEGACY_ROT",
    ),

    # ── TELEMETRY_LEAK: Zero-telemetry enforcement (M8) ───────────────
    PatternDef(
        name="sentry_dsn",
        pattern=re.compile(r"https://[a-f0-9]+@o\d+\.ingest\.sentry\.io/\d+"),
        severity=Severity.CRITICAL,
        description="Sentry DSN detected — zero-telemetry violated (M8)",
        failure_mode="TELEMETRY_LEAK",
    ),
    PatternDef(
        name="telemetry_endpoint",
        pattern=re.compile(
            r"(?i)(?:TELEMETRY|ANALYTICS|SENTRY|DATADOG)[_\-]?"
            r"(?:URL|DSN|ENDPOINT)\s*[:=]\s*\S+"
        ),
        severity=Severity.HIGH,
        description="External telemetry endpoint reference detected",
        failure_mode="TELEMETRY_LEAK",
    ),

    # ── Credential leaks ──────────────────────────────────────────────
    PatternDef(
        name="api_key_literal",
        pattern=re.compile(
            r"(?:api[_-]?key|secret[_-]?key|password|token)"
            r"\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
            re.IGNORECASE,
        ),
        severity=Severity.HIGH,
        description="Potential secret assignment detected",
        failure_mode="TELEMETRY_LEAK",
    ),
]


# ── FailureModeRegistry ───────────────────────────────────────────────

class FailureModeRegistry:
    """M17 Cognitive Integrity — named failure modes with recovery paths.

    Detects, classifies, and provides recovery paths for 5 systemic
    failure modes. Integrates with ObservabilityEngine.record_error()
    for automatic classification on every error.

    Engine-core uses generic English names. The WAD layer can provide
    esoteric name mappings via register_wad_names().

    Usage::

        registry = FailureModeRegistry()

        # Scan content for pattern-based failures
        findings = registry.scan(source_code)

        # Get purity score (1.0 = clean, 0.0 = fully compromised)
        report = registry.get_purity_report(source_code)

        # Classify a runtime error
        classification = registry.classify_error(some_exception)
    """

    def __init__(self) -> None:
        self._patterns = list(_PATTERNS)
        self._recovery_paths: Dict[str, List[RecoveryPath]] = {
            "REDIS_LOSS": [
                RecoveryPath(
                    mode="REDIS_LOSS",
                    action="fallback_to_local",
                    description="Redis unavailable — degrade to local file storage",
                    auto_recover=True,
                ),
            ],
            "LEGACY_ROT": [
                RecoveryPath(
                    mode="LEGACY_ROT",
                    action="log_and_flag",
                    description="Legacy import path detected — flag for migration",
                    auto_recover=False,
                ),
            ],
            "TELEMETRY_LEAK": [
                RecoveryPath(
                    mode="TELEMETRY_LEAK",
                    action="block_and_alert",
                    description="Telemetry leak detected — block and alert (M8 violation)",
                    auto_recover=False,
                ),
            ],
            "DUAL_IMPL": [
                RecoveryPath(
                    mode="DUAL_IMPL",
                    action="consolidate",
                    description="Dual implementation detected — consolidate to single impl",
                    auto_recover=False,
                ),
            ],
            "DEAD_CODE": [
                RecoveryPath(
                    mode="DEAD_CODE",
                    action="remove_dead_code",
                    description="Dead code detected — remove unused module",
                    auto_recover=False,
                ),
            ],
        }
        # WAD-layer name mapping: engine_name → wad_display_name
        # e.g., {"LEGACY_ROT": "BELIAL", "TELEMETRY_LEAK": "GOLACHAB"}
        self._wad_names: Dict[str, str] = {}
        self._findings_log: List[Finding] = []

    # ── WAD Name Mapping ──────────────────────────────────────────────

    def register_wad_names(self, mapping: Dict[str, str]) -> None:
        """Register WAD-layer display names for failure modes.

        The engine always uses generic names internally. WAD names are
        only for display/reporting in the WAD layer (M2 compliance).

        Args:
            mapping: {engine_name: wad_display_name}
                     e.g., {"LEGACY_ROT": "BELIAL", "TELEMETRY_LEAK": "GOLACHAB"}
        """
        self._wad_names.update(mapping)

    def get_display_name(self, engine_name: str) -> str:
        """Get the display name for a failure mode (WAD name if registered, else engine name)."""
        return self._wad_names.get(engine_name, engine_name)

    # ── Content Scanning ──────────────────────────────────────────────

    def scan(self, content: str) -> List[Finding]:
        """Scan content for pattern-based failure mode violations.

        Returns all findings with severity and preview. No content mutation.
        """
        findings: List[Finding] = []
        for pdef in self._patterns:
            match = pdef.pattern.search(content)
            if match:
                raw = match.group(0)
                preview = raw[:6] + "*" * min(len(raw) - 6, 24)
                findings.append(Finding(
                    name=pdef.name,
                    severity=pdef.severity,
                    description=pdef.description,
                    match_preview=preview,
                    failure_mode=pdef.failure_mode,
                ))
        return findings

    def sanitize(self, content: str) -> str:
        """Purge LEGACY_ROT patterns in-place. Returns cleaned content.

        Only removes legacy import patterns — other findings are flagged
        but not mutated.
        """
        sanitized = content
        for pdef in self._patterns:
            if pdef.failure_mode == "LEGACY_ROT":
                sanitized = pdef.pattern.sub("[LEGACY_ROT_PURGED]", sanitized)
        return sanitized

    # ── Purity Scoring ────────────────────────────────────────────────

    def get_purity_report(self, content: str) -> Dict[str, Any]:
        """Generate a purity compliance report.

        Purity score: 1.0 = clean, 0.0 = fully compromised.
        Compliant = no critical or high findings.
        """
        findings = self.scan(content)
        deduction = sum(
            SEVERITY_WEIGHT.get(f.severity, 0.1) for f in findings
        )
        purity_score = max(0.0, round(1.0 - deduction, 2))

        critical = [f for f in findings if f.severity == Severity.CRITICAL]
        high = [f for f in findings if f.severity == Severity.HIGH]
        medium = [f for f in findings if f.severity == Severity.MEDIUM]

        return {
            "compliant": len(critical) == 0 and len(high) == 0,
            "purity_score": purity_score,
            "findings": [f.name for f in findings],
            "findings_detail": [
                {"name": f.name, "severity": f.severity.value, "description": f.description}
                for f in findings
            ],
            "legacy_rot_detected": any(f.failure_mode == "LEGACY_ROT" for f in findings),
            "telemetry_leak_detected": any(f.failure_mode == "TELEMETRY_LEAK" for f in findings),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
        }

    # ── Runtime Error Classification ──────────────────────────────────

    def classify_error(self, error: Exception) -> Dict[str, Any]:
        """Classify a runtime error into a failure mode category.

        Maps exception types and messages to the 5 failure modes.
        Returns a classification dict with mode, recovery path, and metadata.
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # REDIS_LOSS: Redis/cache connection failures
        if any(kw in error_msg.lower() for kw in ("redis", "cache", "connection refused")):
            return self._classify("REDIS_LOSS", error_type, error_msg)

        # DUAL_IMPL: Import errors suggesting dual implementations
        if error_type == "ImportError" and "cannot import" in error_msg:
            return self._classify("DUAL_IMPL", error_type, error_msg)

        # LEGACY_ROT: Module not found (legacy path)
        if error_type == "ModuleNotFoundError" and "src.omega" in error_msg:
            return self._classify("LEGACY_ROT", error_type, error_msg)

        # DEAD_CODE: NameError (dead code reference)
        if error_type == "NameError":
            return self._classify("DEAD_CODE", error_type, error_msg)

        # Default: unclassified
        return {
            "mode": "UNCLASSIFIED",
            "error_type": error_type,
            "error_preview": error_msg[:200],
            "recovery": None,
            "auto_recover": False,
        }

    def _classify(self, mode: str, error_type: str, error_msg: str) -> Dict[str, Any]:
        """Internal: build a classification dict for a known failure mode."""
        paths = self._recovery_paths.get(mode, [])
        recovery = paths[0] if paths else None
        display = self.get_display_name(mode)
        return {
            "mode": mode,
            "display_name": display,
            "error_type": error_type,
            "error_preview": error_msg[:200],
            "recovery": {
                "action": recovery.action,
                "description": recovery.description,
            } if recovery else None,
            "auto_recover": recovery.auto_recover if recovery else False,
        }

    # ── Recovery Path Management ──────────────────────────────────────

    def get_recovery_paths(self, mode: str) -> List[RecoveryPath]:
        """Get recovery paths for a failure mode."""
        return list(self._recovery_paths.get(mode, []))

    def register_recovery_path(self, path: RecoveryPath) -> None:
        """Register a custom recovery path for a failure mode."""
        if path.mode not in self._recovery_paths:
            self._recovery_paths[path.mode] = []
        self._recovery_paths[path.mode].append(path)

    # ── Stats ─────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Return registry statistics."""
        return {
            "total_patterns": len(self._patterns),
            "failure_modes": list(self._recovery_paths.keys()),
            "total_recovery_paths": sum(
                len(paths) for paths in self._recovery_paths.values()
            ),
            "patterns_by_mode": {
                mode: sum(1 for p in self._patterns if p.failure_mode == mode)
                for mode in self._recovery_paths
            },
            "wad_names_registered": len(self._wad_names),
        }


# ── Module-level singleton ────────────────────────────────────────────
_registry: Optional[FailureModeRegistry] = None


def get_failure_registry() -> FailureModeRegistry:
    """Get or create the singleton FailureModeRegistry."""
    global _registry
    if _registry is None:
        _registry = FailureModeRegistry()
    return _registry
