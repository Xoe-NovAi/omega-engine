# AP: AP-MANDATE-ENFORCER-v1.0.0
"""
🔱 MANDATE ENFORCER
Role: Automated enforcement of the Sovereign Mandates.
Integrates the Sentinel Score to trigger sovereign gates and 
compliance alerts.

Follows Mandate 5 (Gnosis Preservation) and Mandate 13 (Temple-Grade).
"""

import logging
import anyio
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass

from omega.oracle.sentinel import SentinelScore, SentinelResult, THRESHOLD_YELLOW, THRESHOLD_GREEN
from omega.errors import OmegaError, BoundaryViolationError

logger = logging.getLogger("mandate_enforcer")

# ============================================================================
# MODELS
# ============================================================================

@dataclass
class ComplianceReport:
    """Detailed report of mandate compliance."""
    is_compliant: bool
    score: float
    grade: str
    violations: List[str]
    recommendations: List[str]

# ============================================================================
# ENFORCER ENGINE
# ============================================================================

class MandateEnforcer:
    """
    Automates the enforcement of Sovereign Mandates.
    
    The Enforcer acts as the 'Immune System' of the Omega Engine, 
    using the Sentinel Score to detect and respond to architectural drift.
    """

    def __init__(self, sentinel: SentinelScore, hivemind_client=None):
        self.sentinel = sentinel
        self.hivemind = hivemind_client
        self._block_non_critical = False

    async def check_compliance(self) -> ComplianceReport:
        """
        Perform a full compliance audit using the Sentinel Score.
        
        Returns:
            ComplianceReport containing the current state and required actions.
        """
        result = await self.sentinel.compute_score()
        
        violations = []
        recommendations = []
        
        # Identify critical violations from the sub-metrics
        for name, metric in result.metrics.items():
            if metric.status == "Red":
                violations.append(f"{name}: {metric.details}")
                recommendations.append(f"Remediate {name} to improve Sentinel Score")
        
        # Update internal block state based on grade
        self._block_non_critical = (result.grade == "Red")
        
        if self._block_non_critical:
            logger.critical("Sovereign Gate ACTIVE: Sentinel Score is RED (%s). Non-critical operations blocked.", result.total_score)
        
        return ComplianceReport(
            is_compliant=(result.grade == "Green"),
            score=result.total_score,
            grade=result.grade,
            violations=violations,
            recommendations=recommendations
        )

    async def validate_operation(self, op_priority: str = "normal") -> bool:
        """
        Sovereign Gate: Validates if an operation can proceed based on current compliance.
        
        Args:
            op_priority: "critical" or "normal". Critical ops always proceed.
            
        Returns:
            True if operation is permitted, False otherwise.
        """
        if op_priority == "critical":
            return True
        
        if self._block_non_critical:
            logger.warning("Operation blocked by Sovereign Gate: Sentinel Score is RED")
            return False
            
        return True

    async def trigger_compliance_alert(self, report: ComplianceReport, result: 'SentinelResult'):
        """Post a compliance alert to the Hivemind if the score is Yellow or Red.
        
        Args:
            report: The compliance report from check_compliance().
            result: The SentinelResult from the same computation (avoids re-computing).
        """
        if report.grade == "Green":
            return

        if self.hivemind:
            pulse = await self.sentinel.generate_pulse_report(result)
            
            await self.hivemind.post_context(
                intent="compliance_alert",
                status=f"Sovereign Grade: {report.grade} ({report.score}/100)",
                continuation=f"Violations: {', '.join(report.violations)}. Recommended: {', '.join(report.recommendations)}",
                # ... other fields as required by post_context
            )

# ============================================================================
# INTEGRATION
# ============================================================================

async def start_mandate_enforcer(sentinel: SentinelScore, hivemind_client=None):
    """Helper to initialize the Mandate Enforcer."""
    return MandateEnforcer(sentinel, hivemind_client)
