# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-MEMORY-FIREWALL-AUDITOR-v1.0.0
# 🔱 MemoryFirewallAuditor — Validates WAD content isolation in memory tiers
#
# M2 Firewall: Memory tiers store opaque metadata dicts.
# Engine Core NEVER inspects WAD-specific keys (element, chakra, sigil, etc.)
# All WAD-specific content MUST be nested under metadata["symbolic"] sub-dict.

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Set

from omega.oracle.entity_registry import Entity

logger = logging.getLogger(__name__)


@dataclass
class MemoryViolation:
    """A single firewall violation in entity metadata."""

    key: str
    location: str  # e.g., "metadata.element" or "metadata.symbolic.element"
    severity: Literal["error", "warning"]
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


@dataclass
class MemoryAuditReport:
    """Audit report for a single entity's metadata."""

    entity_name: str
    tier: str
    violations: List[MemoryViolation] = field(default_factory=list)
    clean: bool = True


class MemoryFirewallAuditor:
    """Audits that MemoryStore tiers (Hot/Warm/Cold) only contain
    engine-agnostic metadata — no WAD-specific semantic leakage.

    M2 Firewall: Memory tiers store opaque metadata dicts.
    Engine Core NEVER inspects WAD-specific keys (element, chakra, sigil, etc.)
    """

    # Engine-agnostic metadata keys allowed at root of metadata dict
    ENGINE_METADATA_KEYS: Set[str] = {
        "name",
        "domains",
        "capabilities",
        "model",
        "personality",
        "temperature",
        "context_window",
        "slots",
        "role",
        "container",
        "port",
        "wad_source",
        "priority",
        "symbolic",
    }

    # WAD-specific keys FORBIDDEN at root of metadata dict
    # These MUST be nested under metadata["symbolic"]
    FORBIDDEN_WAD_KEYS: Set[str] = {
        "element",
        "chakra",
        "planet",
        "sigil",
        "invocation",
        "archetypal_ally",
        "celestial_body",
        "energy_center",
        "tarot",
        "sefirot",
        "qliphoth",
        "pantheon",
        "octave",
        "glyph",
        "first_breath",
        "secondary_keeper",
        "traits",
    }

    # Valid keys for SymbolicMetadata sub-dict (from TypedDict)
    VALID_SYMBOLIC_KEYS: Set[str] = {
        "element",
        "energy_center",
        "celestial_body",
        "archetypal_ally",
        "glyph",
        "invocation",
    }

    def __init__(self):
        self._audit_count = 0

    def audit_entity_metadata(self, entity: Entity) -> MemoryAuditReport:
        """Check entity.metadata for forbidden WAD keys outside 'symbolic' sub-dict.

        Args:
            entity: Entity to audit

        Returns:
            MemoryAuditReport with violations and clean status
        """
        self._audit_count += 1
        trace_prefix = uuid.uuid4().hex[:8]

        report = MemoryAuditReport(
            entity_name=entity.name, tier="entity", violations=[], clean=True
        )

        metadata = entity.metadata or {}

        # Check root-level metadata for forbidden WAD keys
        for key in metadata:
            if key in self.FORBIDDEN_WAD_KEYS:
                report.violations.append(
                    MemoryViolation(
                        key=key, location=f"metadata.{key}", severity="error", trace_id=trace_prefix
                    )
                )
                report.clean = False

        # Check symbolic sub-dict for invalid keys
        symbolic = metadata.get("symbolic")
        if isinstance(symbolic, dict):
            for key in symbolic:
                if key not in self.VALID_SYMBOLIC_KEYS:
                    report.violations.append(
                        MemoryViolation(
                            key=key,
                            location=f"metadata.symbolic.{key}",
                            severity="warning",
                            trace_id=trace_prefix,
                        )
                    )
                    report.clean = False

        if report.violations:
            logger.warning(
                "Memory firewall audit failed for entity '%s': %d violations",
                entity.name,
                len(report.violations),
            )
            for v in report.violations:
                logger.warning(
                    "  %s: %s (severity=%s, trace=%s)", v.location, v.key, v.severity, v.trace_id
                )
        else:
            logger.debug("Memory firewall audit passed for entity '%s'", entity.name)

        return report

    def audit_memory_tier(
        self, tier: Literal["hot", "warm", "cold"], entities: Optional[List[Entity]] = None
    ) -> List[MemoryAuditReport]:
        """Scan all entities in a memory tier for leakage.

        Args:
            tier: Memory tier to audit ("hot", "warm", "cold")
            entities: Optional list of entities. If None, loads from registry.

        Returns:
            List of MemoryAuditReport for each entity
        """
        if entities is None:
            from omega.oracle.entity_registry import EntityRegistry

            registry = EntityRegistry()
            entities = list(registry.active_iter())

        reports = []
        for entity in entities:
            report = self.audit_entity_metadata(entity)
            report.tier = tier
            reports.append(report)

        return reports

    def audit_all_tiers(
        self, entities: Optional[List[Entity]] = None
    ) -> Dict[str, List[MemoryAuditReport]]:
        """Audit all three memory tiers.

        Args:
            entities: Optional list of entities to audit

        Returns:
            Dict mapping tier name to list of reports
        """
        return {
            "hot": self.audit_memory_tier("hot", entities),
            "warm": self.audit_memory_tier("warm", entities),
            "cold": self.audit_memory_tier("cold", entities),
        }

    def get_summary(self, reports: List[MemoryAuditReport]) -> Dict[str, Any]:
        """Generate summary statistics from audit reports.

        Args:
            reports: List of MemoryAuditReport objects

        Returns:
            Dict with compliance statistics
        """
        total = len(reports)
        clean = sum(1 for r in reports if r.clean)
        violated = total - clean
        total_violations = sum(len(r.violations) for r in reports)
        error_violations = sum(1 for r in reports for v in r.violations if v.severity == "error")
        warning_violations = sum(
            1 for r in reports for v in r.violations if v.severity == "warning"
        )

        return {
            "total_entities": total,
            "clean_entities": clean,
            "violated_entities": violated,
            "total_violations": total_violations,
            "error_violations": error_violations,
            "warning_violations": warning_violations,
            "compliance_rate": clean / total if total > 0 else 1.0,
        }

    def audit_symbolic_metadata(self, entity: Entity) -> MemoryAuditReport:
        """Validate entity's symbolic metadata against SymbolicMetadata schema.

        Uses the TypedDict validation from Entity.get_symbolic_metadata().

        Args:
            entity: Entity to validate

        Returns:
            MemoryAuditReport with validation results
        """
        self._audit_count += 1
        trace_prefix = uuid.uuid4().hex[:8]

        report = MemoryAuditReport(
            entity_name=entity.name, tier="symbolic", violations=[], clean=True
        )

        symbolic = entity.get_symbolic_metadata()

        # Check for keys that were filtered out (unknown keys in raw symbolic)
        raw_symbolic = entity.metadata.get("symbolic", {})
        if isinstance(raw_symbolic, dict):
            for key in raw_symbolic:
                if key not in self.VALID_SYMBOLIC_KEYS:
                    report.violations.append(
                        MemoryViolation(
                            key=key,
                            location=f"metadata.symbolic.{key}",
                            severity="warning",
                            trace_id=trace_prefix,
                        )
                    )
                    report.clean = False

        return report
