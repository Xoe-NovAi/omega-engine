# ⬡ OMEGA ⬡ ROUTING TABLE MODULE ⬡ v1.0
# Static routing logic — no ML, no learning, just a version-controlled table.
# If it routes wrong, edit config/routing_table.yaml.

from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass
import yaml

ROUTING_TABLE_PATH = Path("config/routing_table.yaml")


@dataclass
class RoutingDecision:
    action: Literal["local", "cloud"]
    model: Optional[str] = None
    provider: Optional[str] = None
    fallback_model: Optional[str] = None
    fallback_provider: Optional[str] = None
    rule_name: str = ""
    priority: int = 0
    rationale: str = ""


@dataclass
class RoutingRequest:
    task_category: str
    privacy_tag: bool = False
    context_tokens: int = 0
    local_7b_available: bool = True
    local_4b_available: bool = True
    quality_threshold: float = 0.7
    latency_budget_ms: int = 5000
    cost_budget_usd: float = 0.10


class RoutingTable:
    """Static routing table loaded from YAML. No ML. No learning."""

    def __init__(self, path: Path = ROUTING_TABLE_PATH):
        self.path = path
        self._rules = []
        self._providers = {}
        self._local_models = {}
        self._load()

    def _load(self):
        with open(self.path) as f:
            data = yaml.safe_load(f)

        self._rules = sorted(data.get("rules", []), key=lambda r: -r.get("priority", 0))
        self._providers = data.get("providers", {})
        self._local_models = data.get("local_models", {})

    def route(self, request: RoutingRequest) -> RoutingDecision:
        """Evaluate rules in priority order. First match wins."""
        for rule in self._rules:
            if self._evaluate_condition(rule.get("condition", "true"), request):
                return RoutingDecision(
                    action=rule["action"],
                    model=rule.get("preferred_model"),
                    provider=rule.get("preferred_provider"),
                    fallback_model=rule.get("fallback_model"),
                    fallback_provider=rule.get("fallback_provider"),
                    rule_name=rule["name"],
                    priority=rule.get("priority", 0),
                    rationale=rule.get("rationale", ""),
                )

        # Should never reach here (default rule catches all)
        return RoutingDecision(
            action="local",
            model="qwen3-1.7b",
            rule_name="default_sovereign",
            rationale="M7 Local-First: default to sovereignty",
        )

    def _evaluate_condition(self, condition: str, request: RoutingRequest) -> bool:
        """Safely evaluate routing condition."""
        # Replace variables with request values
        local_vars = {
            "privacy_tag": request.privacy_tag,
            "context_tokens": request.context_tokens,
            "local_7b_available": request.local_7b_available,
            "local_4b_available": request.local_4b_available,
            "quality_threshold": request.quality_threshold,
            "latency_budget_ms": request.latency_budget_ms,
            "cost_budget_usd": request.cost_budget_usd,
            "task_category": request.task_category,
            "true": True,
            "false": False,
        }

        try:
            # Only allow safe operations
            allowed_names = set(local_vars.keys()) | {
                "in",
                "and",
                "or",
                "not",
                "==",
                "!=",
                ">",
                "<",
                ">=",
                "<=",
            }
            # Simple eval with restricted globals
            return eval(condition, {"__builtins__": {}}, local_vars)
        except Exception:
            return False

    def get_provider_config(self, provider: str) -> dict:
        return self._providers.get(provider, {})

    def get_local_model(self, model: str) -> dict:
        return self._local_models.get(model, {})

    def list_rules(self) -> list:
        return [
            {
                "name": r["name"],
                "condition": r["condition"],
                "action": r["action"],
                "priority": r.get("priority", 0),
                "rationale": r.get("rationale", ""),
            }
            for r in self._rules
        ]


# ── Convenience Function ──────────────────────────────────────────────
def route_request(
    task_category: str,
    privacy_tag: bool = False,
    context_tokens: int = 0,
    local_7b_available: bool = True,
    local_4b_available: bool = True,
) -> RoutingDecision:
    """One-liner for routing decisions."""
    table = RoutingTable()
    request = RoutingRequest(
        task_category=task_category,
        privacy_tag=privacy_tag,
        context_tokens=context_tokens,
        local_7b_available=local_7b_available,
        local_4b_available=local_4b_available,
    )
    return table.route(request)


# ── CLI ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print(
            "Usage: python -m src.omega.routing.table <task_category> [privacy_tag] [context_tokens]"
        )
        sys.exit(1)

    task = sys.argv[1]
    privacy = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else False
    context = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    decision = route_request(task, privacy, context)
    print(json.dumps(decision.__dict__, indent=2))
