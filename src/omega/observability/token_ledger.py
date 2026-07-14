# 🔱 Sovereign Token Ledger — Usage Tracking & Auditing
# AP: AP-TOKEN-LEDGER-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ OBSERVABILITY
#
# Implements the precise token tracking required for the Sovereign Intelligence Economy.
# Every inference transaction is recorded to ensure budget compliance and 
# provider efficiency analysis.
#
# [id-soft: vet-016] Cvar System — ledger persistence settings from cvar_table
#
# ── Logic Flow ──────────────────────────────────────────────────────────────
# 1. Receive transaction data (trace_id, entity, tokens_in, tokens_out, is_cloud).
# 2. Log to the ObservabilityEngine event stream (Sovereign Event Log).
# 3. Persist to a local JSONL ledger for long-term auditing.
# =============================================================================


# DocRef: docs/explanation/metrics-pipeline.md
import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import anyio

from omega.observability import get_engine, EventType
from omega.cvar_table import cvar_get
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

class TokenLedger:
    """
    The Sovereign Token Ledger.
    Tracks every token consumed by the engine to enforce budget gates.
    """

    def __init__(self):
        self.ledger_path = Path("data/logs/token_ledger.jsonl")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    async def record_transaction(
        self, 
        trace_id: str, 
        entity: str, 
        tokens_in: int, 
        tokens_out: int, 
        provider_name: str
    ) -> None:
        """
        Record the token usage of a completed inference transaction.
        
        Args:
            trace_id: Unique identifier for the trace.
            entity: The entity that generated the response.
            tokens_in: Number of input tokens.
            tokens_out: Number of output tokens.
            provider_name: The name of the provider that served the response.
        """
        # 1. Log to the ObservabilityEngine event stream
        # This allows the BudgetGate to query current spend in real-time.
        obs = get_engine()
        obs.log_event(
            EventType.TOKEN_CONSUMPTION,
            trace_id,
            {
                "entity": entity,
                "prompt_tokens": tokens_in,
                "completion_tokens": tokens_out,
                "total_tokens": tokens_in + tokens_out,
                "provider_name": provider_name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # 1b. Persist to MetricsDB for performance and cost analytics
        obs.record_performance(
            latency_ms=0.0, # Latency is handled by LatencyTracker, but we record tokens here
            provider=provider_name,
            prompt_tokens=tokens_in,
            completion_tokens=tokens_out,
            trace_id=trace_id
        )
        
        # 2. Persist to the local JSONL ledger for auditing
        transaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "entity": entity,
            "prompt_tokens": tokens_in,
            "completion_tokens": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "provider_name": provider_name,
        }
        
        try:
            async with await anyio.open_file(str(self.ledger_path), mode="a", encoding="utf-8") as f:
                await f.write(json.dumps(transaction) + "\n")
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to persist token transaction to ledger: {e}")

    async def get_entity_spend(self, entity_name: str) -> int:
        """
        Calculate total tokens consumed by an entity from the persisted ledger.
        
        Note: For real-time budget gating, the BudgetGate queries the 
        ObservabilityEngine's in-memory event log. This method is for auditing.
        """
        total = 0
        if not self.ledger_path.exists():
            return 0
            
        try:
            async with await anyio.open_file(str(self.ledger_path), mode="r", encoding="utf-8") as f:
                async for line in f:
                    tx = json.loads(line)
                    if tx.get("entity") == entity_name:
                        total += tx.get("total_tokens", 0)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to read token ledger for spend calculation: {e}")
            
        return total
