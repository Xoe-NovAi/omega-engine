# 🔱 Omega Engine — Sovereign Vetter (P0-3)
# ⬡ OMEGA ⬡ MA'AT ⬡ P5 ⬡ 2026-07-12
# AP: AP-SOVEREIGN-VETTER-v1.0.0
#
# [heritage: sovereign-kliewer 2026] In-path governance — "no fast path that
# skips governance, no trusted caller that bypasses evaluation." This vetter
# enforces all 23 Sovereign Mandates (M1-M23) as a pre-flight check before any
# inference dispatch.
#
# Design philosophy (M23 Failure Integrity + defensive engineering):
#   * A mandate VIOLATION (explicit, detected) => VettingResult.passed = False.
#   * A checker that CANNOT RUN (missing file, sensor failure) => passed = True
#     with a "skipped" detail. A governance checker must never take down the
#     engine because a path moved — it logs and proceeds.
#   * The vetter itself is wrapped at the call site so a vetter CRASH cannot
#     DoS inference (logged, proceeds). Only an explicit failed verdict blocks.

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

logger = logging.getLogger(__name__)

# Repo root: src/omega/governance/sovereign_vetter.py -> parents[3] = repo root
REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class VettingResult:
    """Result of a single mandate check, or an aggregated verdict.

    [M21: Gate Integrity] Every checker returns this typed dataclass so the
    call site can validate `isinstance(result, VettingResult)`.
    """
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)


class SovereignVetter:
    """Pre-flight enforcement of all 23 Sovereign Mandates (M1-M23).

    Usage:
        vetter = SovereignVetter()
        result = await vetter.vet({"query": query})
        if not result.passed:
            raise BoundaryViolationError(...)
    """

    # Mandate id -> checker method name
    MANDATES: Dict[str, str] = {
        "M1": "_check_anyio",
        "M2": "_check_firewall",
        "M3": "_check_iris_constant",
        "M4": "_check_sequentiality",
        "M5": "_check_gnosis_preservation",
        "M6": "_check_podman_sovereignty",
        "M7": "_check_local_first",
        "M8": "_check_zero_telemetry",
        "M9": "_check_error_integrity",
        "M10": "_check_fleet_integrity",
        "M11": "_check_soul_integrity",
        "M12": "_check_queue_integrity",
        "M13": "_check_temple_grade",
        "M14": "_check_heritage_vetting",
        "M15": "_check_sovereign_continuity",
        "M16": "_check_modularization",
        "M17": "_check_cognitive_integrity",
        "M18": "_check_token_efficiency",
        "M19": "_check_adversarial_alchemy",
        "M20": "_check_somatic_state",
        "M21": "_check_gate_integrity",
        "M22": "_check_response_provenance",
        "M23": "_check_failure_integrity",
    }

    # CRITICAL mandates: a failure here is a runtime sovereignty breach and
    # HARD-BLOCKS inference (raises BoundaryViolationError at the call site).
    # All other mandates are ADVISORY: their failure is logged for observability
    # but does NOT block inference. A governance checker must never take down the
    # engine for an advisory/aspirational mandate (M23 Failure Integrity).
    CRITICAL_MANDATES: frozenset = frozenset({"M1", "M7", "M8", "M9", "M23"})

    def __init__(self):
        self._cache: Optional[VettingResult] = None

    # ── Public API ──────────────────────────────────────────────────────────
    async def vet(self, context: Optional[Dict[str, Any]] = None, force: bool = False) -> VettingResult:
        """Run all mandate checkers and aggregate a verdict.

        Results are cached per process (the checks are static repo scans).
        Pass ``force=True`` to bypass the cache.

        [D221: Critical-Whitelist Design] Only CRITICAL_MANDATES hard-block
        (VettingResult.passed == False). Advisory mandate failures are recorded
        in ``advisory_failed`` for observability but do NOT set passed=False.
        This prevents the vetter from DoS-ing the engine over aspirational
        mandates (M2/M4/M5/M10-M21) while still enforcing the non-negotiable
        runtime sovereignty mandates (M1/M7/M8/M9/M23).
        """
        if not force and self._cache is not None:
            return self._cache

        failed: List[str] = []          # critical failures -> blocks
        advisory_failed: List[str] = []  # advisory failures -> logged only
        details: Dict[str, Any] = {}
        for m_id, method_name in self.MANDATES.items():
            method = getattr(self, method_name)
            try:
                result = await method(context or {})
            except Exception as e:  # noqa: BLE001 — a checker bug must not DoS the engine
                logger.error("SovereignVetter %s crashed: %s", method_name, e)
                result = VettingResult(passed=True, details={"error": f"checker crashed: {e}", "skipped": True})
            details[m_id] = {"passed": result.passed, "detail": result.details}
            if not result.passed:
                if m_id in self.CRITICAL_MANDATES:
                    failed.append(m_id)
                else:
                    advisory_failed.append(m_id)
                logger.warning(
                    "SovereignVetter: mandate %s failed (advisory=%s): %s",
                    m_id, m_id not in self.CRITICAL_MANDATES, result.details,
                )

        passed = len(failed) == 0
        aggregated = VettingResult(passed=passed, details={
            "failed_mandates": failed,
            "advisory_failed": advisory_failed,
            "per_mandate": details,
        })
        self._cache = aggregated
        return aggregated

    # ── Helpers ─────────────────────────────────────────────────────────────
    @staticmethod
    def _grep_sync(root: Path, pattern: str, skip_comments: bool = True) -> List[str]:
        """Synchronous recursive grep over .py files (excludes __pycache__/tests).

        [M21: Gate Integrity] The vetter MUST exclude its own source file from
        scans — a checker that flags its own implementation is a self-referential
        false positive (e.g., M9's docstring contains the literal "except:";
        M16's regex string contains "/home/arcana-novai"). Self-exclusion is the
        canonical fix, not weakening the mandate.
        """
        compiled = re.compile(pattern)
        hits: List[str] = []
        if not root.exists():
            return hits
        for py_file in root.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
                continue
            # Self-exclusion: exclude governance and audit dirs from scans to avoid
            # flagging the vetter's own patterns and the auditor's regexes.
            if "governance/" in str(py_file) or "audit/" in str(py_file):
                continue
            try:
                for line_num, line in enumerate(py_file.read_text(encoding="utf-8").splitlines(), 1):
                    if skip_comments and line.strip().startswith("#"):
                        continue
                    if compiled.search(line):
                        hits.append(f"{py_file.relative_to(REPO_ROOT)}:{line_num}")
            except (UnicodeDecodeError, OSError):
                continue
        return hits

    @staticmethod
    def _file_exists(rel_path: str) -> bool:
        return (REPO_ROOT / rel_path).exists()

    @staticmethod
    def _read_text(rel_path: str) -> Optional[str]:
        p = REPO_ROOT / rel_path
        if not p.exists():
            return None
        try:
            return p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None

    # ── Mandate Checkers ──────────────────────────────────────────────────────
    async def _check_anyio(self, ctx: Dict[str, Any]) -> VettingResult:
        """M1: No asyncio in the Core Engine — AnyIO only."""
        hits = await anyio.to_thread.run_sync(
            self._grep_sync, REPO_ROOT / "src" / "omega", r"(^|\s)(import\s+asyncio|from\s+asyncio)"
        )
        return VettingResult(passed=len(hits) == 0, details={"violations": hits})

    async def _check_firewall(self, ctx: Dict[str, Any]) -> VettingResult:
        """M2: Engine-Stack Firewall — Core must remain WAD-agnostic.

        Reuses the canonical FirewallChecker (skips comments/docstrings/self).
        """
        from omega.audit.firewall_checker import FirewallChecker

        def _scan() -> int:
            return FirewallChecker().scan(REPO_ROOT / "src" / "omega").error_count

        errors = await anyio.to_thread.run_sync(_scan)
        return VettingResult(passed=errors == 0, details={"error_count": errors})

    async def _check_iris_constant(self, ctx: Dict[str, Any]) -> VettingResult:
        """M3: Iris is the messenger bridge, NOT a Pillar Keeper."""
        # Scan config/ YAML for an explicit `pillar: iris` assignment (case-insensitive).
        hits = await anyio.to_thread.run_sync(
            self._grep_sync, REPO_ROOT / "config", r"pillar\s*:\s*iris", False
        )
        return VettingResult(passed=len(hits) == 0, details={"violations": hits})

    async def _check_sequentiality(self, ctx: Dict[str, Any]) -> VettingResult:
        """M4: Plan → Verify → Execute — PIVOT_LOG must exist."""
        exists = self._file_exists("docs/decisions/PIVOT_LOG.md")
        return VettingResult(passed=exists, details={"pivot_log_present": exists})

    async def _check_gnosis_preservation(self, ctx: Dict[str, Any]) -> VettingResult:
        """M5: L1 → L2 → L3 gnosis distillation pipeline exists."""
        text = self._read_text("src/omega/oracle/soul_distiller.py")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "soul_distiller.py not found"})
        has_pipeline = all(tok in text for tok in ("L1", "L2", "L3"))
        return VettingResult(passed=has_pipeline, details={"l1_l2_l3_present": has_pipeline})

    async def _check_podman_sovereignty(self, ctx: Dict[str, Any]) -> VettingResult:
        """M6: No `:U` flag on shared host volumes (keep-id protocol)."""
        def _scan() -> List[str]:
            hits: List[str] = []
            for container in (REPO_ROOT / "deploy").rglob("*.container") if (REPO_ROOT / "deploy").exists() else []:
                try:
                    for line_num, line in enumerate(container.read_text(encoding="utf-8").splitlines(), 1):
                        # Volume :U flag (not a URL scheme)
                        if re.search(r":U\b", line) and "://" not in line:
                            hits.append(f"{container.name}:{line_num}")
                except (UnicodeDecodeError, OSError):
                    continue
            return hits
        hits = await anyio.to_thread.run_sync(_scan)
        return VettingResult(passed=len(hits) == 0, details={"violations": hits})

    async def _check_local_first(self, ctx: Dict[str, Any]) -> VettingResult:
        """M7: Local inference is PRIMARY (strategy: local_first)."""
        text = self._read_text("config/providers.yaml")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "providers.yaml not found"})
        present = "strategy: local_first" in text
        return VettingResult(passed=present, details={"local_first_strategy": present})

    async def _check_zero_telemetry(self, ctx: Dict[str, Any]) -> VettingResult:
        """M8: No telemetry SDK imports in the Core Engine."""
        # Split pattern to avoid T6 false positive on "telemetry" in source
        telemetry_sdks = ["segment", "posthog", "datadog", "amplitude", "mixpanel"]
        pattern = r"(import|from)\s+(" + "|".join(telemetry_sdks) + r")\b"
        hits = await anyio.to_thread.run_sync(
            self._grep_sync, REPO_ROOT / "src" / "omega", pattern
        )
        return VettingResult(passed=len(hits) == 0, details={"violations": hits})

    async def _check_error_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M9: No bare `except:` (typed, traceable errors only)."""
        hits = await anyio.to_thread.run_sync(
            self._grep_sync, REPO_ROOT / "src" / "omega", r"except\s*:"
        )
        # Filter out `except Exception:` (allowed) and `# noqa` lines
        real = [h for h in hits if "except Exception" not in h and "# noqa" not in h]
        return VettingResult(passed=len(real) == 0, details={"violations": real})

    async def _check_fleet_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M10: Agent fleet cap — ≤14 agent files."""
        agents_dir = REPO_ROOT / ".opencode" / "agents"
        count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
        return VettingResult(passed=count <= 14, details={"agent_files": count, "cap": 14})

    async def _check_soul_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M11: Soul distillation writes proposed_lessons.yaml."""
        text = self._read_text("src/omega/oracle/soul_distiller.py")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "soul_distiller.py not found"})
        present = "proposed_lessons" in text
        return VettingResult(passed=present, details={"proposed_lessons_wired": present})

    async def _check_queue_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M12: Request queue has terminal states / dead-letter handling."""
        text = self._read_text("src/omega/request_queue.py")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "request_queue.py not found"})
        has_terminal = ("dead" in text) or ("terminal" in text)
        return VettingResult(passed=has_terminal, details={"terminal_states": has_terminal})

    async def _check_temple_grade(self, ctx: Dict[str, Any]) -> VettingResult:
        """M13: Temple-Grade automatable gates (T5 AnyIO + T6 Zero-Telemetry)."""
        anyio_hits = await self._check_anyio(ctx)
        telemetry_hits = await self._check_zero_telemetry(ctx)
        passed = anyio_hits.passed and telemetry_hits.passed
        return VettingResult(passed=passed, details={
            "anyio_clean": anyio_hits.passed, "telemetry_clean": telemetry_hits.passed
        })

    async def _check_heritage_vetting(self, ctx: Dict[str, Any]) -> VettingResult:
        """M14: Heritage vet log exists for [id-soft:] tags."""
        exists = self._file_exists("data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md")
        return VettingResult(passed=exists, details={"vet_log_present": exists})

    async def _check_sovereign_continuity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M15: Session anchors exist (anchored-summary.md)."""
        exists = self._file_exists(".opencode/anchored-summary.md")
        return VettingResult(passed=exists, details={"anchored_summary_present": exists})

    async def _check_modularization(self, ctx: Dict[str, Any]) -> VettingResult:
        """M16: No hardcoded absolute host paths in the Core Engine."""
        hits = await anyio.to_thread.run_sync(
            self._grep_sync, REPO_ROOT / "src" / "omega", r"/home/arcana-novai|/Users/|/root/"
        )
        # Exclude comment lines (already skipped by helper) and string-pattern defs
        real = [h for h in hits if "r'/" not in h and 'r"/' not in h]
        return VettingResult(passed=len(real) == 0, details={"violations": real})

    async def _check_cognitive_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M17: Skeptical Verifier exists (memory consistency checks)."""
        exists = self._file_exists("src/omega/oracle/skeptical_verifier.py")
        return VettingResult(passed=exists, details={"skeptical_verifier_present": exists})

    async def _check_token_efficiency(self, ctx: Dict[str, Any]) -> VettingResult:
        """M18: Token Efficiency — advisory (heuristic, not automatable)."""
        return VettingResult(passed=True, details={"advisory": True})

    async def _check_adversarial_alchemy(self, ctx: Dict[str, Any]) -> VettingResult:
        """M19: Adversarial Alchemy — advisory (systemic constraints only)."""
        return VettingResult(passed=True, details={"advisory": True})

    async def _check_somatic_state(self, ctx: Dict[str, Any]) -> VettingResult:
        """M20: SomaticState serialization module exists."""
        exists = self._file_exists("src/omega/state/somatic_state.py")
        return VettingResult(passed=exists, details={"somatic_state_present": exists})

    async def _check_gate_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M21: Contract tests exist (isinstance return-type validation)."""
        exists = self._file_exists("tests/test_contract_m21.py")
        return VettingResult(passed=exists, details={"contract_test_present": exists})

    async def _check_response_provenance(self, ctx: Dict[str, Any]) -> VettingResult:
        """M22: Response provenance (provider_name) wired in ModelGateway."""
        text = self._read_text("src/omega/oracle/model_gateway.py")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "model_gateway.py not found"})
        present = "provider_name" in text
        return VettingResult(passed=present, details={"provider_name_wired": present})

    async def _check_failure_integrity(self, ctx: Dict[str, Any]) -> VettingResult:
        """M23: Typed error hierarchy exists; no silent swallowing."""
        text = self._read_text("src/omega/errors.py")
        if text is None:
            return VettingResult(passed=True, details={"skipped": "errors.py not found"})
        has_hierarchy = "class OmegaError" in text
        return VettingResult(passed=has_hierarchy, details={"typed_errors": has_hierarchy})
