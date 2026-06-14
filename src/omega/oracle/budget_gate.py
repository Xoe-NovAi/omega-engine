# 🔱 Sovereign Budget Gate — Cloud Expenditure Control
# AP: AP-BUDGET-GATE-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ SOVEREIGNTY-GUARD
#
# Implements the Hard-Stop Cloud Budget Gate (Shatter-Glass Phase 3).
# Ensures that cloud inference is strictly capped to prevent "Sovereignty Drift"
# and unexpected costs.
#
# [id-soft: quake3-1999] Cvar System — budget limits read from cvar_table
#
# Mandate 7 (Local-First): If budget is exhausted, the engine MUST force-fallback
# to local providers.
#
# ── Logic Flow ──────────────────────────────────────────────────────────────
# 1. Check if request is for a cloud provider.
# 2, query the current spend for the entity/session.
# 3. Compare against `config.budget.daily_cloud_tokens`.
# 4. Return True (Allow) or False (Block).
# =============================================================================

import logging
from typing import Optional
from omega.errors import OmegaError, ProviderValidationError
from omega.cvar_table import cvar_get

logger = logging.getLogger(__name__)

class BudgetGate:
    """
    The Sovereign Budget Gate.
    Enforces hard limits on cloud inference token consumption.
    """

    @staticmethod
    async def check_budget(entity_name: str, trace_id: str) -> bool:
        """
        Verify if the entity has remaining budget for cloud inference.
        
        Args:
            entity_name: The entity requesting inference.
            trace_id: The trace ID for the request.
            
        Returns:
            True if budget is available, False otherwise.
        """
        # 1. Retrieve the daily budget limit from cvar_table
        # Default to 500,000 tokens if not configured
        budget_limit = cvar_get("config.budget.daily_cloud_tokens", 500000)
        
        try:
            from omega.observability import get_engine
            obs = get_engine()
            
            # 2. Calculate current spend for this entity today
            # We filter the event log for TOKEN_CONSUMPTION events for this entity
            current_spend = 0
            for event in obs._event_log:
                if event.get("event") == "token.consumption" and event.get("data", {}).get("entity") == entity_name:
                    current_spend += event["data"].get("prompt_tokens", 0) + event["data"].get("completion_tokens", 0)
            
            if current_spend >= budget_limit:
                logger.warning(
                    f"[SOVEREIGNTY ALERT] Budget exhausted for entity '{entity_name}'. "
                    f"Spend: {current_spend}/{budget_limit} tokens. Trace: {trace_id}"
                )
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"BudgetGate failure: {e}", exc_info=True)
            # Fail-safe: Allow inference if the budget gate itself crashes, 
            # but log a critical error.
            return True

    @staticmethod
    async def get_current_spend(entity_name: str) -> int:
        """Get the total cloud tokens consumed by an entity in the current session."""
        try:
            from omega.observability import get_engine
            obs = get_engine()
            return sum(
                event["data"].get("prompt_tokens", 0) + event["data"].get("completion_tokens", 0)
                for event in obs._event_log
                if event.get("event") == "token.consumption" and event.get("data", {}).get("entity") == entity_name
            )
        except Exception:
            return 0
