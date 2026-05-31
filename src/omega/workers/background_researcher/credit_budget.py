# 🔱 Omega Engine — API Credit Budget Tracker
# AP: AP-BACKGROUND-RESEARCHER-BUDGET-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ sovereign ⬡ budget ⬡ WORKER
#
# Tracks monthly API usage across all search/extraction providers.
# Persists to disk so quotas survive restarts.

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class APICreditExhausted(Exception):
    """Raised when a provider's monthly quota is exhausted."""
    pass


@dataclass
class ProviderBudget:
    total: int = 1000
    used: int = 0
    reserved_emergency: int = 100

    @property
    def remaining(self) -> int:
        return self.total - self.used

    def consume(self, units: int = 1) -> bool:
        if self.remaining - units < self.reserved_emergency:
            return False
        self.used += units
        return True

    def reset(self):
        self.used = 0


class APICreditBudget:
    """Tracks monthly API credits across all providers.

    Resets on month change automatically. Saves to data/research/credit_budget.json.
    """

    DEFAULT_BUDGETS = {
        "exa": ProviderBudget(total=1000, reserved_emergency=100),
        "tavily": ProviderBudget(total=1000, reserved_emergency=100),
        "firecrawl": ProviderBudget(total=1000, reserved_emergency=100),
        "serper": ProviderBudget(total=2500, reserved_emergency=500),
        "jina": ProviderBudget(total=10000, reserved_emergency=1000),  # token-based, generous
    }

    DAILY_LIMITS = {
        "search_ops": 30,
        "deep_extracts": 5,
        "gemma_calls": 20,
    }

    def __init__(self, path: Path = Path("data/research/credit_budget.json")):
        self.path = path
        self.month: str = ""
        self.budgets: dict[str, ProviderBudget] = {}
        self.daily_used: dict[str, int] = {}
        self._today: str = ""
        self._load()

    # ── Public API ──────────────────────────────────────────────────────────

    def has_quota(self, api: str, min_needed: int = 1) -> bool:
        """Check if a provider has enough remaining credits."""
        if api == "search":
            return any(
                p.remaining >= min_needed
                for name, p in self.budgets.items()
                if name in ("exa", "tavily", "serper", "jina")
            )
        budget = self.budgets.get(api)
        if not budget:
            return False
        return budget.remaining >= min_needed

    def consume(self, api: str, units: int = 1) -> None:
        """Consume credits from a provider. Raises APICreditExhausted if insufficient."""
        if api == "search":
            # Prefer Tavily (cheaper) over Exa, Jina, Serper
            for name in ("tavily", "serper", "jina", "exa"):
                budget = self.budgets.get(name)
                if budget and budget.consume(units):
                    logger.debug(f"Consumed {units} credit(s) from {name}")
                    self._save()
                    return
            raise APICreditExhausted("All search providers exhausted")

        budget = self.budgets.get(api)
        if not budget or not budget.consume(units):
            raise APICreditExhausted(f"{api} exhausted")
        self._save()

    def check_daily_limit(self, operation: str) -> bool:
        """Check if we've hit the daily limit for an operation type."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._today != today:
            self.daily_used = {}
            self._today = today
        limit = self.DAILY_LIMITS.get(operation, float("inf"))
        used = self.daily_used.get(operation, 0)
        return used < limit

    def increment_daily(self, operation: str) -> None:
        """Increment daily counter for an operation type."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._today != today:
            self.daily_used = {}
            self._today = today
        self.daily_used[operation] = self.daily_used.get(operation, 0) + 1

    def get_status(self) -> dict:
        """Return a snapshot of current budget state for reporting."""
        return {
            "month": self.month,
            "daily_used": dict(self.daily_used),
            "budgets": {
                name: {
                    "total": b.total,
                    "used": b.used,
                    "remaining": b.remaining,
                    "reserved": b.reserved_emergency,
                }
                for name, b in self.budgets.items()
            },
        }

    def select_search_provider(self) -> str:
        """Select the best available search provider based on remaining quota."""
        # Check each in priority order
        for name in ("tavily", "serper", "jina", "exa"):
            budget = self.budgets.get(name)
            if budget and budget.remaining > budget.reserved_emergency:
                return name
        # Fall back to anything with remaining credits
        for name, budget in self.budgets.items():
            if budget and budget.remaining > 0:
                return name
        raise APICreditExhausted("All search providers exhausted")

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load budget state from disk. Reset if month changed."""
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                if data.get("month") == current_month:
                    self.month = current_month
                    self.budgets = {
                        name: ProviderBudget(**b)
                        for name, b in data.get("budgets", {}).items()
                    }
                    self.daily_used = data.get("daily_used", {})
                    self._today = data.get("today", "")
                    return
            except (json.JSONDecodeError, KeyError, TypeError):
                logger.warning("Corrupted credit budget file, resetting.")
        self._reset_month()

    def _save(self) -> None:
        """Persist budget state to disk atomically."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "month": self.month,
            "today": self._today,
            "daily_used": self.daily_used,
            "budgets": {name: asdict(b) for name, b in self.budgets.items()},
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(self.path)

    def _reset_month(self) -> None:
        """Reset all budgets for a new month."""
        self.month = datetime.now(timezone.utc).strftime("%Y-%m")
        self.budgets = {name: ProviderBudget(**asdict(b)) for name, b in self.DEFAULT_BUDGETS.items()}
        self.daily_used = {}
        self._today = ""
        self._save()
        logger.info(f"Credit budgets reset for {self.month}")
