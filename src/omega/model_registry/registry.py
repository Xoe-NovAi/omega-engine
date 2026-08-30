# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Model Registry Service
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-18

Unified model registry loading YAML frontmatter model cards,
provider configs, and research profiles. Builds SQLite index.
"""

import yaml
import sqlite3
from pathlib import Path
from typing import Optional

from .models import (
    ModelCard,
    Platform,
    Tier,
    Status,
    Capabilities,
    Pricing,
    Routing,
    IdentityHistory,
    CommunityIntelligence,
    LiveAPIState,
    ResearchProfile,
    TestRun,
    Synergy,
    EmpiricalEvidence,
    ProviderFabric,
    Parameters,
    BenchmarkSources,
)
from .providers import ProviderConfig
from .research import ResearchProfile as ResearchProfileData


def _enum_ci(enum_cls, value):
    """Case-insensitive enum lookup (B2 fix).

    Model cards use inconsistent platform/tier/status casing (e.g. ``"LOCAL"``
    vs ``"local"``, ``"ACTIVE"`` vs ``"active"``).  Normalize to the enum's
    canonical value before construction so a single card can't break the
    whole registry index build.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Exact match first, then case-insensitive by member name, then by value.
    try:
        return enum_cls(s)
    except ValueError:
        pass
    for member in enum_cls:
        if member.name.lower() == s.lower() or str(member.value).lower() == s.lower():
            return member
    return None


class ModelRegistry:
    """Unified model registry - files are source of truth, SQLite is derived index."""

    def __init__(self, registry_root: str = "config/model_registry"):
        self.registry_root = Path(registry_root)
        self.models_dir = self.registry_root / "models"
        self.providers_dir = self.registry_root / "providers"
        self.research_dir = self.registry_root / "research_profiles"
        self.model_db_dir = self.registry_root / "model_db"
        self.index_path = self.registry_root / "index.sqlite"

        # Caches
        self._model_cards: dict[str, ModelCard] = {}
        self._providers: dict[str, ProviderConfig] = {}
        self._research_profiles: dict[str, ResearchProfileData] = {}

    def load_all(self) -> None:
        """Load all model cards, providers, and research profiles."""
        self._load_model_cards()
        self._load_providers()
        self._load_research_profiles()

    def _load_model_cards(self) -> None:
        """Load model cards from YAML frontmatter files."""
        for model_file in self.models_dir.rglob("*.yaml.md"):
            try:
                with open(model_file) as f:
                    content = f.read()

                # Parse YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        model_card = self._parse_model_card(frontmatter)
                        self._model_cards[model_card.model_id] = model_card
            except Exception as e:
                print(f"Warning: Failed to load {model_file}: {e}")

        # Also load from model_db (legacy CURRENT_MODELS.md format)
        self._load_legacy_model_db()

    def _load_legacy_model_db(self) -> None:
        """Load models from legacy CURRENT_MODELS.md YAML section."""
        current_models = self.model_db_dir / "CURRENT_MODELS.md"
        if current_models.exists():
            try:
                with open(current_models) as f:
                    content = f.read()

                # Extract YAML section — only the fenced block between
                # ```yaml and the closing ``` (B2 fix: slicing from "models:"
                # to EOF pulled in trailing markdown + backticks → YAML error).
                yaml_content = None
                if "models:" in content:
                    fence_start = content.find("```yaml")
                    if fence_start != -1:
                        fence_start = content.find("models:", fence_start)
                        fence_end = content.find("```", fence_start)
                        if fence_end != -1:
                            yaml_content = content[fence_start:fence_end]
                    if yaml_content is None:  # fallback: old behavior
                        yaml_start = content.index("models:")
                        yaml_content = content[yaml_start:]
                if yaml_content:
                    data = yaml.safe_load(yaml_content)
                    if data and "models" in data:
                        for model_id, model_data in data["models"].items():
                            if model_id not in self._model_cards:
                                model_card = self._parse_legacy_model(model_id, model_data)
                                if model_card:
                                    self._model_cards[model_card.model_id] = model_card
            except Exception as e:
                print(f"Warning: Failed to load legacy model DB: {e}")

    def _parse_model_card(self, data: dict) -> ModelCard:
        """Parse model card from YAML frontmatter dict."""
        # Capabilities
        caps_data = data.get("capabilities", {})
        capabilities = Capabilities(
            reasoning=caps_data.get("reasoning", 0.0),
            code_generation=caps_data.get("code_generation", 0.0),
            knowledge=caps_data.get("knowledge", 0.0),
            creative=caps_data.get("creative", 0.0),
            tool_use=caps_data.get("tool_use", False),
            structured_output=caps_data.get("structured_output", False),
            multimodal=caps_data.get("multimodal", False),
            code_execution=caps_data.get("code_execution", False),
            parallel_search=caps_data.get("parallel_search", False),
            workspace_integration=caps_data.get("workspace_integration", False),
        )

        # Pricing
        pricing_data = data.get("pricing", {})
        pricing = Pricing(
            input_per_mtok=pricing_data.get("input_per_mtok", 0.0),
            output_per_mtok=pricing_data.get("output_per_mtok", 0.0),
            cached_input_per_mtok=pricing_data.get("cached_input_per_mtok", 0.0),
            batch_discount=pricing_data.get("batch_discount", 0.0),
            intro_pricing=pricing_data.get("intro_pricing"),
            free_tier=data.get("free_tier", False),
            cost_per_1k_tokens_usd=pricing_data.get("cost_per_1k_tokens_usd", 0.0),
        )

        # Routing
        routing_data = data.get("routing", {})
        routing = Routing(
            engine_routable=routing_data.get("engine_routable", True),
            opencode_cli_only=routing_data.get("opencode_cli_only", False),
            recommended_engine_alternative=routing_data.get("recommended_engine_alternative"),
        )

        # Identity History
        identity_history = None
        if data.get("identity_history"):
            ih = data["identity_history"]
            identity_history = IdentityHistory(
                original=ih.get("original", ""),
                current=ih.get("current", ""),
                swap_detected=ih.get("swap_detected", False),
                last_verified=ih.get("last_verified", ""),
            )

        # Community Intelligence
        community_intelligence = None
        if data.get("community_rating"):
            community_intelligence = CommunityIntelligence(
                rating=data.get("community_rating", ""),
                notes=data.get("community_notes", []),
            )

        # Live API State
        live_api_state = None
        if data.get("live_api_state"):
            las = data["live_api_state"]
            live_api_state = LiveAPIState(
                source=las.get("source", ""),
                last_verified=las.get("last_verified", ""),
                last_verified_free=las.get("last_verified_free"),
            )

        # Research Profile
        rp_data = data.get("research_profile", {})
        research_profile = ResearchProfile(
            reasoning_depth=rp_data.get("reasoning_depth", "iterative"),
            tool_fidelity=rp_data.get("tool_fidelity", "medium"),
            failure_signature=rp_data.get("failure_signature", "shallow"),
            shadow_focus=rp_data.get("shadow_focus", "force_deepening"),
            guardrails=rp_data.get("guardrails", []),
        )

        # Empirical Evidence
        empirical_evidence = EmpiricalEvidence()
        for tr in data.get("empirical_evidence", {}).get("test_runs", []):
            empirical_evidence.test_runs.append(TestRun(**tr))
        for sy in data.get("empirical_evidence", {}).get("synergies", []):
            empirical_evidence.synergies.append(Synergy(**sy))

        # Provider Fabric
        pf_data = data.get("provider_fabric", {})
        provider_fabric = ProviderFabric(
            available_via=pf_data.get("available_via", []),
            local_first_priority=pf_data.get("local_first_priority"),
        )

        # Parameters (T1)
        params_data = data.get("parameters", {})
        parameters = Parameters(
            temperature=params_data.get("temperature", 0.7),
            top_p=params_data.get("top_p", 0.95),
            top_k=params_data.get("top_k", 40),
            repetition_penalty=params_data.get("repetition_penalty", 1.1),
            max_tokens=params_data.get("max_tokens", 4096),
            stop_sequences=params_data.get("stop_sequences", []),
            presence_penalty=params_data.get("presence_penalty", 0.0),
            frequency_penalty=params_data.get("frequency_penalty", 0.0),
            logit_bias=params_data.get("logit_bias"),
            seed=params_data.get("seed"),
            model_specific_overrides=params_data.get("model_specific_overrides", {}),
        )

        # Benchmark Sources (P1)
        bm_data = data.get("benchmark_sources", {})
        benchmark_sources = BenchmarkSources(
            reasoning=bm_data.get("reasoning", ""),
            code_generation=bm_data.get("code_generation", ""),
            knowledge=bm_data.get("knowledge", ""),
            creative=bm_data.get("creative", ""),
            tool_use=bm_data.get("tool_use", ""),
            structured_output=bm_data.get("structured_output", ""),
            multimodal=bm_data.get("multimodal", ""),
            overall=bm_data.get("overall", ""),
        )

        return ModelCard(
            model_id=data["model_id"],
            display_name=data["display_name"],
            version=data["version"],
            provider=data["provider"],
            platform=_enum_ci(Platform, data["platform"]) or Platform.CLOUD,
            tier=_enum_ci(Tier, data["tier"]) or Tier.T1,
            status=_enum_ci(Status, data["status"]) or Status.ACTIVE,
            context_window=data["context_window"],
            max_output_tokens=data.get("max_output_tokens", 0),
            capabilities=capabilities,
            pricing=pricing,
            latency_p99_ms=data.get("latency_p99_ms", 0),
            uptime_percent=data.get("uptime_percent", 0.0),
            routing=routing,
            identity_history=identity_history,
            community_intelligence=community_intelligence,
            live_api_state=live_api_state,
            research_profile=research_profile,
            empirical_evidence=empirical_evidence,
            provider_fabric=provider_fabric,
            parameters=parameters,
            benchmark_sources=benchmark_sources,
            tags=data.get("tags", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            schema_version=data.get("schema_version", "1.0.0"),
        )

    def _parse_legacy_model(self, model_id: str, data: dict) -> Optional[ModelCard]:
        """Parse legacy model from CURRENT_MODELS.md format."""
        try:
            capabilities = Capabilities(
                reasoning=data.get("capabilities", {}).get("reasoning", 0.0),
                code_generation=data.get("capabilities", {}).get("code_generation", 0.0),
                knowledge=data.get("capabilities", {}).get("knowledge", 0.0),
                creative=data.get("capabilities", {}).get("creative", 0.0),
                tool_use=data.get("capabilities", {}).get("tool_use", False),
                structured_output=data.get("capabilities", {}).get("structured_output", False),
                code_execution=data.get("capabilities", {}).get("code_execution", False),
                parallel_search=data.get("capabilities", {}).get("parallel_search", False),
                workspace_integration=data.get("capabilities", {}).get(
                    "workspace_integration", False
                ),
            )

            pricing = Pricing(
                free_tier=data.get("free_tier", False),
                cost_per_1k_tokens_usd=data.get("cost_per_1k_tokens_usd", 0.0),
            )

            routing = Routing(
                engine_routable=data.get("routing", {}).get("engine_routable", True),
                opencode_cli_only=data.get("routing", {}).get("opencode_cli_only", False),
                recommended_engine_alternative=data.get("routing", {}).get(
                    "recommended_engine_alternative"
                ),
            )

            identity_history = None
            if data.get("identity_history"):
                ih = data["identity_history"]
                identity_history = IdentityHistory(
                    original=ih.get("original", ""),
                    current=ih.get("current", ""),
                    swap_detected=ih.get("swap_detected", False),
                    last_verified=ih.get("last_verified", ""),
                )

            community_intelligence = None
            if data.get("community_rating"):
                community_intelligence = CommunityIntelligence(
                    rating=data.get("community_rating", ""),
                    notes=data.get("community_notes", []),
                )

            live_api_state = None
            if data.get("last_verified_free"):
                live_api_state = LiveAPIState(
                    source=data.get("provider", "unknown"),
                    last_verified=data.get("last_updated", ""),
                    last_verified_free=data.get("last_verified_free", ""),
                )

            # Determine platform from provider.
            # Legacy CURRENT_MODELS.md uses the OLD provider taxonomy
            # (together, sambanova, openai, ...).  Normalize to a registered
            # provider in the current fabric so test_provider_in_registry holds
            # and queries can join cards to provider configs.
            provider = data.get("provider", "unknown")
            provider = {
                # Legacy router/aggregator names → current fabric provider
                "together": "openrouter",
                "sambanova": "openrouter",
                "openai": "openrouter",
                "zen": "opencode-zen",
            }.get(provider, provider)
            if provider in ["native-gguf", "lmster", "ollama"]:
                platform = Platform.LOCAL
            elif provider in ["opencode-zen", "cline"]:
                platform = Platform.CLI
            elif provider == "openrouter" and data.get("routing", {}).get("opencode_cli_only"):
                platform = Platform.STEALTH
            else:
                platform = Platform.CLOUD

            # Determine tier from context window and capabilities
            ctx = data.get("context_window", 0)
            if ctx >= 200000:
                tier = Tier.T3
            elif ctx >= 100000:
                tier = Tier.T2
            else:
                tier = Tier.T1

            return ModelCard(
                model_id=model_id,
                display_name=model_id,
                version=data.get("last_updated", "2026-01-01"),
                provider=provider,
                platform=platform,
                tier=tier,
                status=Status.ACTIVE,
                context_window=ctx,
                capabilities=capabilities,
                pricing=pricing,
                latency_p99_ms=data.get("latency_p99_ms", 0),
                uptime_percent=data.get("uptime_percent", 0.0),
                routing=routing,
                identity_history=identity_history,
                community_intelligence=community_intelligence,
                live_api_state=live_api_state,
                tags=data.get("tags", []),
                created_at=data.get("last_updated", "2026-01-01"),
                updated_at=data.get("last_updated", "2026-01-01"),
            )
        except Exception as e:
            print(f"Warning: Failed to parse legacy model {model_id}: {e}")
            return None

    def _load_providers(self) -> None:
        """Load provider configurations."""
        for provider_file in self.providers_dir.glob("*.yaml"):
            try:
                with open(provider_file) as f:
                    data = yaml.safe_load(f)
                provider = ProviderConfig(**data)
                self._providers[provider.provider] = provider
            except Exception as e:
                print(f"Warning: Failed to load provider {provider_file}: {e}")

    def _load_research_profiles(self) -> None:
        """Load research profiles."""
        for profile_file in self.research_dir.glob("*.yaml"):
            try:
                with open(profile_file) as f:
                    data = yaml.safe_load(f)
                profile = ResearchProfileData(**data)
                self._research_profiles[profile.profile] = profile
            except Exception as e:
                print(f"Warning: Failed to load research profile {profile_file}: {e}")

    def get_model(self, model_id: str) -> Optional[ModelCard]:
        """Get model card by ID."""
        return self._model_cards.get(model_id)

    def get_models(
        self,
        platform: Optional[Platform] = None,
        tier: Optional[Tier] = None,
        provider: Optional[str] = None,
    ) -> list[ModelCard]:
        """Get models with optional filters."""
        models = list(self._model_cards.values())
        if platform:
            models = [m for m in models if m.platform == platform]
        if tier:
            models = [m for m in models if m.tier == tier]
        if provider:
            models = [m for m in models if m.provider == provider]
        return models

    def get_provider(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get provider config by name."""
        return self._providers.get(provider_name)

    def get_providers(self) -> list[ProviderConfig]:
        """Get all providers sorted by priority."""
        return sorted(self._providers.values(), key=lambda p: p.priority)

    def get_research_profile(self, profile_name: str) -> Optional[ResearchProfileData]:
        """Get research profile by name."""
        return self._research_profiles.get(profile_name)

    def build_index(self) -> None:
        """Build SQLite index from loaded data.

        The index is DERIVED (files are source of truth per registry.yaml).
        Drop existing tables first to prevent schema drift — the old 83-column
        models table (from a richer past schema) would otherwise persist via
        CREATE TABLE IF NOT EXISTS while the INSERT supplies only the current
        column set, raising OperationalError.
        """
        conn = sqlite3.connect(self.index_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS models")
        cursor.execute("DROP TABLE IF EXISTS providers")
        cursor.execute("DROP TABLE IF EXISTS research_profiles")

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                model_id TEXT PRIMARY KEY,
                display_name TEXT,
                version TEXT,
                provider TEXT,
                platform TEXT,
                tier TEXT,
                status TEXT,
                context_window INTEGER,
                max_output_tokens INTEGER,
                reasoning REAL,
                code_generation REAL,
                knowledge REAL,
                creative REAL,
                tool_use BOOLEAN,
                structured_output BOOLEAN,
                multimodal BOOLEAN,
                code_execution BOOLEAN,
                parallel_search BOOLEAN,
                workspace_integration BOOLEAN,
                input_per_mtok REAL,
                output_per_mtok REAL,
                free_tier BOOLEAN,
                latency_p99_ms INTEGER,
                uptime_percent REAL,
                engine_routable BOOLEAN,
                opencode_cli_only BOOLEAN,
                recommended_engine_alternative TEXT,
                temperature REAL,
                top_p REAL,
                top_k INTEGER,
                repetition_penalty REAL,
                max_tokens INTEGER,
                stop_sequences TEXT,
                presence_penalty REAL,
                frequency_penalty REAL,
                tags TEXT,
                created_at TEXT,
                updated_at TEXT,
                schema_version TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                provider TEXT PRIMARY KEY,
                priority INTEGER,
                enabled BOOLEAN,
                description TEXT,
                api_key TEXT,
                base_url TEXT,
                endpoint TEXT,
                supported_models TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_profiles (
                profile TEXT PRIMARY KEY,
                context_window INTEGER,
                reasoning_depth TEXT,
                tool_fidelity TEXT,
                failure_signature TEXT,
                shadow_focus TEXT,
                guardrails TEXT
            )
        """)

        # Insert models
        for model in self._model_cards.values():
            cursor.execute(
                """
                INSERT OR REPLACE INTO models VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    model.model_id,
                    model.display_name,
                    model.version,
                    model.provider,
                    model.platform.value,
                    model.tier.value,
                    model.status.value,
                    model.context_window,
                    model.max_output_tokens,
                    model.capabilities.reasoning,
                    model.capabilities.code_generation,
                    model.capabilities.knowledge,
                    model.capabilities.creative,
                    model.capabilities.tool_use,
                    model.capabilities.structured_output,
                    model.capabilities.multimodal,
                    model.capabilities.code_execution,
                    model.capabilities.parallel_search,
                    model.capabilities.workspace_integration,
                    model.pricing.input_per_mtok,
                    model.pricing.output_per_mtok,
                    model.pricing.free_tier,
                    model.latency_p99_ms,
                    model.uptime_percent,
                    model.routing.engine_routable,
                    model.routing.opencode_cli_only,
                    model.routing.recommended_engine_alternative,
                    model.parameters.temperature,
                    model.parameters.top_p,
                    model.parameters.top_k,
                    model.parameters.repetition_penalty,
                    model.parameters.max_tokens,
                    ",".join(model.parameters.stop_sequences),
                    model.parameters.presence_penalty,
                    model.parameters.frequency_penalty,
                    ",".join(model.tags),
                    model.created_at,
                    model.updated_at,
                    model.schema_version,
                ),
            )

        # Insert providers
        for provider in self._providers.values():
            cursor.execute(
                """
                INSERT OR REPLACE INTO providers VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    provider.provider,
                    provider.priority,
                    provider.enabled,
                    provider.description,
                    provider.api_key,
                    provider.base_url,
                    provider.endpoint,
                    ",".join(provider.supported_models),
                ),
            )

        # Insert research profiles
        for profile in self._research_profiles.values():
            cursor.execute(
                """
                INSERT OR REPLACE INTO research_profiles VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    profile.profile,
                    profile.context_window,
                    profile.reasoning_depth,
                    profile.tool_fidelity,
                    profile.failure_signature,
                    profile.shadow_focus,
                    ",".join(profile.guardrails),
                ),
            )

        conn.commit()
        conn.close()
        print(f"Index built at {self.index_path}")

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute query on index."""
        conn = sqlite3.connect(self.index_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
