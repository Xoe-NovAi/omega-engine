# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Model Registry Query Interface
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-19

Extends query_model_study.py with unified registry queries.
"""

from typing import Optional
from dataclasses import dataclass

from .registry import ModelRegistry


@dataclass
class QueryResult:
    """Query result with metadata."""

    rows: list[dict]
    count: int
    sql: str


class ModelRegistryQuery:
    """Query interface for model registry."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def query(self, sql: str, params: tuple = ()) -> QueryResult:
        """Execute raw SQL query."""
        rows = self.registry.query(sql, params)
        return QueryResult(rows=rows, count=len(rows), sql=sql)

    # Model queries
    def get_all_models(self) -> QueryResult:
        return self.query("SELECT * FROM models ORDER BY tier, provider, model_id")

    def get_models_by_tier(self, tier: str) -> QueryResult:
        return self.query(
            "SELECT * FROM models WHERE tier = ? ORDER BY provider, model_id", (tier,)
        )

    def get_models_by_platform(self, platform: str) -> QueryResult:
        return self.query(
            "SELECT * FROM models WHERE platform = ? ORDER BY tier, model_id", (platform,)
        )

    def get_models_by_provider(self, provider: str) -> QueryResult:
        return self.query(
            "SELECT * FROM models WHERE provider = ? ORDER BY tier, model_id", (provider,)
        )

    def get_free_models(self) -> QueryResult:
        return self.query(
            "SELECT * FROM models WHERE free_tier = 1 ORDER BY tier, provider, model_id"
        )

    def get_engine_routable_models(self) -> QueryResult:
        return self.query(
            "SELECT * FROM models WHERE engine_routable = 1 ORDER BY tier, provider, model_id"
        )

    def get_model_by_id(self, model_id: str) -> Optional[dict]:
        rows = self.query("SELECT * FROM models WHERE model_id = ?", (model_id,))
        return rows.rows[0] if rows.rows else None

    def search_models(self, search_term: str) -> QueryResult:
        return self.query(
            """
            SELECT * FROM models
            WHERE model_id LIKE ? OR display_name LIKE ? OR tags LIKE ?
            ORDER BY tier, provider, model_id
        """,
            (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"),
        )

    def get_capability_leaders(self, capability: str, limit: int = 5) -> QueryResult:
        """Get top models by capability score. Supports extended capability fields."""
        valid_caps = [
            "reasoning",
            "code_generation",
            "knowledge",
            "creative",
            "tool_use",
            "structured_output",
            "multimodal",
            "code_execution",
            "parallel_search",
            "workspace_integration",
        ]
        if capability not in valid_caps:
            raise ValueError(f"Invalid capability: {capability}. Must be one of {valid_caps}")
        return self.query(
            f"""
            SELECT model_id, display_name, provider, tier, {capability}
            FROM models
            WHERE {capability} > 0
            ORDER BY {capability} DESC
            LIMIT ?
        """,
            (limit,),
        )

    def get_provider_chain(self) -> QueryResult:
        """Get provider fallback chain ordered by priority."""
        return self.query("SELECT * FROM providers WHERE enabled = 1 ORDER BY priority")

    def get_research_profile(self, profile: str) -> Optional[dict]:
        rows = self.query("SELECT * FROM research_profiles WHERE profile = ?", (profile,))
        return rows.rows[0] if rows.rows else None

    def get_all_research_profiles(self) -> QueryResult:
        return self.query("SELECT * FROM research_profiles")

    # Statistics
    def get_stats(self) -> dict:
        """Get registry statistics."""
        stats = {}
        stats["total_models"] = self.query("SELECT COUNT(*) as c FROM models").rows[0]["c"]
        stats["total_providers"] = self.query(
            "SELECT COUNT(*) as c FROM providers WHERE enabled = 1"
        ).rows[0]["c"]
        stats["total_research_profiles"] = self.query(
            "SELECT COUNT(*) as c FROM research_profiles"
        ).rows[0]["c"]

        stats["by_tier"] = {
            row["tier"]: row["c"]
            for row in self.query("SELECT tier, COUNT(*) as c FROM models GROUP BY tier").rows
        }
        stats["by_platform"] = {
            row["platform"]: row["c"]
            for row in self.query(
                "SELECT platform, COUNT(*) as c FROM models GROUP BY platform"
            ).rows
        }
        stats["by_provider"] = {
            row["provider"]: row["c"]
            for row in self.query(
                "SELECT provider, COUNT(*) as c FROM models GROUP BY provider"
            ).rows
        }
        stats["free_models"] = self.query(
            "SELECT COUNT(*) as c FROM models WHERE free_tier = 1"
        ).rows[0]["c"]
        stats["engine_routable"] = self.query(
            "SELECT COUNT(*) as c FROM models WHERE engine_routable = 1"
        ).rows[0]["c"]

        return stats


def main():
    """CLI entry point."""
    import sys

    registry = ModelRegistry()
    registry.load_all()
    registry.build_index()

    query = ModelRegistryQuery(registry)

    if len(sys.argv) < 2:
        print("Usage: model_registry_query.py <command> [args...]")
        print("Commands:")
        print("  stats                    - Show registry statistics")
        print("  models                   - List all models")
        print("  models --tier T1         - Filter by tier")
        print("  models --platform cloud  - Filter by platform")
        print("  models --provider openrouter - Filter by provider")
        print("  models --free            - Free tier models only")
        print("  models --routable        - Engine routable models only")
        print("  model <model_id>         - Get model by ID")
        print("  search <term>            - Search models")
        print("  leaders <capability>     - Top models by capability")
        print("  providers                - Provider fallback chain")
        print("  profile <name>           - Research profile")
        return

    cmd = sys.argv[1]

    if cmd == "stats":
        stats = query.get_stats()
        print(f"Total Models: {stats['total_models']}")
        print(f"Total Providers: {stats['total_providers']}")
        print(f"Total Research Profiles: {stats['total_research_profiles']}")
        print(f"Free Models: {stats['free_models']}")
        print(f"Engine Routable: {stats['engine_routable']}")
        print(f"\nBy Tier: {stats['by_tier']}")
        print(f"By Platform: {stats['by_platform']}")
        print(f"By Provider: {stats['by_provider']}")

    elif cmd == "models":
        # Parse filters
        tier = None
        platform = None
        provider = None
        free_only = False
        routable_only = False

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--tier" and i + 1 < len(sys.argv):
                tier = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--platform" and i + 1 < len(sys.argv):
                platform = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
                provider = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--free":
                free_only = True
                i += 1
            elif sys.argv[i] == "--routable":
                routable_only = True
                i += 1
            else:
                i += 1

        if free_only:
            result = query.get_free_models()
        elif routable_only:
            result = query.get_engine_routable_models()
        elif tier:
            result = query.get_models_by_tier(tier)
        elif platform:
            result = query.get_models_by_platform(platform)
        elif provider:
            result = query.get_models_by_provider(provider)
        else:
            result = query.get_all_models()

        for row in result.rows:
            print(
                f"{row['model_id']:50s} | {row['tier']:3s} | {row['platform']:6s} | {row['provider']:15s} | free={row['free_tier']} | routable={row['engine_routable']}"
            )

    elif cmd == "model":
        if len(sys.argv) < 3:
            print("Usage: model_registry_query.py model <model_id>")
            return
        model = query.get_model_by_id(sys.argv[2])
        if model:
            for k, v in model.items():
                print(f"{k}: {v}")
        else:
            print(f"Model not found: {sys.argv[2]}")

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: model_registry_query.py search <term>")
            return
        result = query.search_models(sys.argv[2])
        for row in result.rows:
            print(
                f"{row['model_id']:50s} | {row['tier']:3s} | {row['platform']:6s} | {row['provider']:15s}"
            )

    elif cmd == "leaders":
        if len(sys.argv) < 3:
            print("Usage: model_registry_query.py leaders <capability>")
            print("Capabilities: reasoning, code_generation, knowledge, creative")
            return
        result = query.get_capability_leaders(sys.argv[2])
        for row in result.rows:
            print(
                f"{row['model_id']:50s} | {row['capability']:.2f} | {row['tier']:3s} | {row['provider']:15s}"
            )

    elif cmd == "providers":
        result = query.get_provider_chain()
        for row in result.rows:
            print(
                f"Priority {row['priority']:2d}: {row['provider']:20s} | enabled={row['enabled']} | {row['description']}"
            )

    elif cmd == "profile":
        if len(sys.argv) < 3:
            print("Usage: model_registry_query.py profile <name>")
            return
        profile = query.get_research_profile(sys.argv[2])
        if profile:
            for k, v in profile.items():
                print(f"{k}: {v}")
        else:
            print(f"Profile not found: {sys.argv[2]}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
