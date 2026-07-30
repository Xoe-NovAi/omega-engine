"""Tests for credit_budget.py — API Credit Budget Tracker."""
import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock
from omega.workers.background_researcher.credit_budget import (
    APICreditBudget,
    ProviderBudget,
    APICreditExhausted,
)


class TestProviderBudget:
    def test_default_values(self):
        budget = ProviderBudget()
        assert budget.total == 1000
        assert budget.used == 0
        assert budget.reserved_emergency == 100
        assert budget.remaining == 1000

    def test_custom_values(self):
        budget = ProviderBudget(total=500, used=100, reserved_emergency=50)
        assert budget.total == 500
        assert budget.used == 100
        assert budget.reserved_emergency == 50
        assert budget.remaining == 400

    def test_consume_success(self):
        budget = ProviderBudget(total=100, used=0, reserved_emergency=10)
        assert budget.consume(5) is True
        assert budget.used == 5
        assert budget.remaining == 95

    def test_consume_fails_when_below_reserve(self):
        budget = ProviderBudget(total=100, used=85, reserved_emergency=10)
        # remaining = 15, but reserve = 10, so can only consume 5
        assert budget.consume(6) is False  # Would leave 9 < 10 reserve
        assert budget.used == 85  # Unchanged

    def test_consume_exact_reserve_boundary(self):
        budget = ProviderBudget(total=100, used=85, reserved_emergency=10)
        assert budget.consume(5) is True  # Leaves exactly 10
        assert budget.used == 90
        assert budget.remaining == 10

    def test_reset(self):
        budget = ProviderBudget(total=100, used=50, reserved_emergency=10)
        budget.reset()
        assert budget.used == 0
        assert budget.remaining == 100


class TestAPICreditBudget:
    @pytest.fixture
    def budget_path(self, tmp_path):
        return tmp_path / "credit_budget.json"

    @pytest.fixture
    def budget(self, budget_path):
        return APICreditBudget(path=budget_path)

    def test_init_creates_default_budgets(self, budget):
        assert "exa" in budget.budgets
        assert "firecrawl" in budget.budgets
        assert budget.budgets["exa"].total == 1000
        assert budget.budgets["firecrawl"].total == 1000

    def test_init_loads_existing_file(self, budget_path, budget):
        # Create a valid budget file
        data = {
            "month": datetime.now(timezone.utc).strftime("%Y-%m"),
            "today": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "daily_used": {"search_ops": 5},
            "budgets": {
                "exa": {"total": 1000, "used": 100, "reserved_emergency": 100},
                "firecrawl": {"total": 1000, "used": 50, "reserved_emergency": 100},
            },
        }
        budget_path.write_text(json.dumps(data))

        # Create new budget instance - should load existing
        new_budget = APICreditBudget(path=budget_path)
        assert new_budget.budgets["exa"].used == 100
        assert new_budget.budgets["firecrawl"].used == 50
        assert new_budget.daily_used["search_ops"] == 5

    def test_init_resets_on_month_change(self, budget_path):
        # Create file with old month
        old_month = "2020-01"
        data = {
            "month": old_month,
            "today": "2020-01-01",
            "daily_used": {},
            "budgets": {
                "exa": {"total": 1000, "used": 500, "reserved_emergency": 100},
            },
        }
        budget_path.write_text(json.dumps(data))

        # New budget should reset
        new_budget = APICreditBudget(path=budget_path)
        assert new_budget.month != old_month
        assert new_budget.budgets["exa"].used == 0

    def test_init_handles_corrupted_file(self, budget_path):
        budget_path.write_text("not valid json")
        budget = APICreditBudget(path=budget_path)
        # Should reset to defaults
        assert budget.budgets["exa"].used == 0

    def test_has_quota_specific_provider(self, budget):
        assert budget.has_quota("exa", 1) is True
        assert budget.has_quota("firecrawl", 1) is True
        assert budget.has_quota("nonexistent", 1) is False

    def test_has_quota_search_alias(self, budget):
        # "search" checks both exa and firecrawl
        assert budget.has_quota("search", 1) is True

    def test_consume_specific_provider(self, budget):
        budget.consume("exa", 10)
        assert budget.budgets["exa"].used == 10

    def test_consume_search_uses_exa_first(self, budget):
        budget.consume("search", 5)
        assert budget.budgets["exa"].used == 5
        assert budget.budgets["firecrawl"].used == 0

    def test_consume_search_falls_back_to_firecrawl(self, budget):
        # Exhaust exa
        budget.budgets["exa"].used = 950  # remaining = 50, reserve = 100
        budget.consume("search", 10)
        assert budget.budgets["exa"].used == 950  # Unchanged
        assert budget.budgets["firecrawl"].used == 10

    def test_consume_raises_when_exhausted(self, budget):
        budget.budgets["exa"].used = 950
        budget.budgets["firecrawl"].used = 950
        with pytest.raises(APICreditExhausted):
            budget.consume("search", 10)

    def test_consume_specific_raises_when_exhausted(self, budget):
        budget.budgets["exa"].used = 950
        with pytest.raises(APICreditExhausted):
            budget.consume("exa", 10)

    def test_check_daily_limit(self, budget):
        assert budget.check_daily_limit("search_ops") is True
        assert budget.check_daily_limit("deep_extracts") is True
        assert budget.check_daily_limit("gemma_calls") is True

    def test_check_daily_limit_resets_on_new_day(self, budget):
        budget.daily_used["search_ops"] = 30  # At limit
        budget._today = "2020-01-01"  # Old day
        # Should reset and return True
        assert budget.check_daily_limit("search_ops") is True
        assert budget.daily_used.get("search_ops", 0) == 0

    def test_increment_daily(self, budget):
        budget.increment_daily("search_ops")
        assert budget.daily_used["search_ops"] == 1
        budget.increment_daily("search_ops")
        assert budget.daily_used["search_ops"] == 2

    def test_increment_daily_resets_on_new_day(self, budget):
        budget.daily_used["search_ops"] = 5
        budget._today = "2020-01-01"
        budget.increment_daily("search_ops")
        assert budget.daily_used["search_ops"] == 1  # Reset then increment

    def test_get_status(self, budget):
        status = budget.get_status()
        assert "month" in status
        assert "daily_used" in status
        assert "budgets" in status
        assert "exa" in status["budgets"]
        assert "firecrawl" in status["budgets"]
        assert status["budgets"]["exa"]["total"] == 1000
        assert status["budgets"]["exa"]["used"] == 0
        assert status["budgets"]["exa"]["remaining"] == 1000

    def test_select_search_provider_prefers_exa(self, budget):
        provider = budget.select_search_provider()
        assert provider == "exa"

    def test_select_search_provider_falls_back(self, budget):
        budget.budgets["exa"].used = 950  # Below reserve
        provider = budget.select_search_provider()
        assert provider == "firecrawl"

    def test_select_search_provider_raises_when_all_exhausted(self, budget):
        budget.budgets["exa"].used = 1000  # remaining = 0
        budget.budgets["firecrawl"].used = 1000  # remaining = 0
        with pytest.raises(APICreditExhausted):
            budget.select_search_provider()

    def test_persistence_atomic_write(self, budget, budget_path):
        budget.consume("exa", 5)
        # Should have written to .tmp then replaced
        assert budget_path.exists()
        data = json.loads(budget_path.read_text())
        assert data["budgets"]["exa"]["used"] == 5

    def test_reset_month(self, budget):
        budget.budgets["exa"].used = 500
        budget._reset_month()
        assert budget.budgets["exa"].used == 0
        assert budget.month == datetime.now(timezone.utc).strftime("%Y-%m")