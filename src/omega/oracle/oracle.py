# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 The Oracle - Routing, Summoning, and Entity Intelligence
# ⬡ OMEGA ⬡ ORACLE ⬡ oracle.py (1100 lines)
#
# Single-source-of-truth for query routing, speculative decoding, entity summoning,
# and soul evolution. Acts as the gateway between user intent and the 10-node council.
#
# [id-soft: vet-056] Oracle Summoning Pattern - Direct entity dispatch via _summon()
# [id-soft: vet-009] Memory Zone - Long-term learning via soul.yaml
# [id-soft: vet-056] Triage Routing - Intent classification and entity selection

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union


from .session_manager import SessionManager
from .orchestrator import Orchestrator
from .model_gateway import ModelGateway
from .wad_loader import WADLoader
from .search import SovereignSearcher
from .iterative_research import IterativeResearcher
from .skeptical_verifier import SkepticalVerifier, VerificationResult
from .security import TDPGate, TaintedData
from .pii_masker import PIIMasker
from .context_builder import ContextBuilder
from .semantic_router import SemanticRouter
from .selective_hydration import SelectiveHydration
from .failure_registry import get_failure_registry
from .soul_edit_history import SoulEditHistory
from .compaction_harvester import CompactionHarvester
from .timeout_manager import TimeoutManager
from .degradation import DegradationManager
from .session_lifecycle import SessionLifecycleManager
from .audience_calibrator import get_audience_calibrator
from .dpo_logger import initialize_dpo_recorder
from ..iris.matcher import IntentMatcher

from ..observability import TraceSession, get_engine, DATA_DIR
from omega.governance.config_resolver import AGENTS_MD
from ..errors import OmegaError
from ..cvar_table import cvar_get
from .entity_registry import EntityRegistry
from ..memory_store import get_memory_store
from ..orchestration.triage_router import (
    TriageRouter,
    TriageRequest,
    TaskRequest,
    EntityContext,
    Constraints,
    SessionContext,
)
from ..state import get_usm, initialize_usm
from omega.errors import OmegaError

# WARP Proxy Pool - optional, for OpenCode Zen rate limit bypass
try:
    from ..proxy_pool import EphemeralWarpPool

    _WARP_AVAILABLE = True
except ImportError:
    EphemeralWarpPool = None
    _WARP_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuration
IRIS_CONFIDENCE_THRESHOLD = 0.6

# ROLE_CONSTANTS - engine-defined slots (NOT entity names).
# WAD YAML (config/wads/<iwad>/entities/dispatch.yaml) maps ROLE -> entity.
# These constants are engine architecture, not WAD content (M2-compliant).
ROLE_CONSTANTS: Dict[str, str] = {
    "MESSENGER_BRIDGE": "MESSENGER_BRIDGE",  # Iris role
    "MAKALI_COUNCIL": "MAKALI_COUNCIL",  # MaKaLi synthesis role
    "GRAND_OVERSIGHT": "GRAND_OVERSIGHT",  # Kali role
    "BUILD_OVERSOUL": "BUILD_OVERSOUL",  # Ma'at role (Build-side, N1-N5)
    "RUNTIME_OVERSOUL": "RUNTIME_OVERSOUL",  # Lilith role (Run-side, N6-N10)
    "CONTAINING_FIELD": "CONTAINING_FIELD",  # Sophia role
    "N1": "N1",
    "N2": "N2",
    "N3": "N3",
    "N4": "N4",
    "N5": "N5",
    "N6": "N6",
    "N7": "N7",
    "N8": "N8",
    "N9": "N9",
    "N10": "N10",
}

# WAD-backed dispatch config loader (M2 Firewall Phase C).
# Delegates to dispatch_registry - single source of truth.
# DISPATCH_CONFIG_FILENAME retained for compatibility.

from omega.governance.dispatch_registry import get_entity_by_role as _registry_get_entity_by_role


def _get_entity_by_role(role: str, iwad: str | None = None) -> Optional[str]:
    """WAD-loadable entity lookup by role constant.

    Returns the entity name (e.g., "iris") for a given role (e.g., "MESSENGER_BRIDGE"),
    or None if not found in the active WAD.
    """
    entity = _registry_get_entity_by_role(role, iwad)
    if entity:
        return str(entity.get("name", "")).lower()
    return None


@dataclass
class OracleResponse:
    """Structured response from the Oracle.

    Engine fields: text, entity, confidence, trace_id, slots, domains.
    WAD-specific display fields (sigil, glyph, pantheon, etc.) are in
    the Entity.metadata dict - accessed via entity.metadata.get("sigil").
    """

    text: str
    entity: str = "Oracle"
    confidence: float = 0.5
    trace_id: str = ""
    slots: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    backend: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    escalated: bool = False
    cost_warning: Optional[str] = None
    # [S3] Tiny-Critic RAG Router classification (informational signal)
    rag_complexity: Optional[str] = None
    # [S7] Audience profile applied to this response (None = default register)
    audience: Optional[str] = None


class Oracle:
    """
    The Oracle - unified routing, summoning, and entity intelligence.
    DocRef: docs/reference/api/oracle.md

    Responsibilities:
    1. Intent detection (talk vs @summon vs @consult patterns)
    2. Speculative decoding (Iris confidence assessment)
    3. Domain routing (escalation to Nodes)
    4. Entity summoning (direct dispatch to named entities)
    5. Soul evolution tracking (L1->L2->L3 learning)
    6. Cloud critique integration (TDP quarantine)
    """

    _valid_agents_cache: Optional[Set[str]] = None

    def __init__(
        self,
        registry: Optional[EntityRegistry] = None,
        model_gateway: Optional[ModelGateway] = None,
    ):
        from omega.oracle.health_monitor import get_health_monitor
        from .middleware.headroom import get_headroom_middleware

        self.registry = registry or EntityRegistry()
        self.default_entity = self.registry.get(cvar_get("config.entity.default", "default"))
        self.orchestrator = Orchestrator()
        self.health_monitor = get_health_monitor()
        self.timeout_manager = TimeoutManager()
        self.degradation_manager = DegradationManager()
        # Accept injected model_gateway to prevent double initialization
        # (hub creates ModelGateway at module level; Oracle was creating a second one)
        self.model_gateway = model_gateway or ModelGateway(health_monitor=self.health_monitor)

        # [M8 Zero Telemetry] WARP Proxy Pool - inject for OpenCode Zen rate limit bypass
        # Only activates if WARP pool is deployed and running (systemd units).
        if _WARP_AVAILABLE and EphemeralWarpPool is not None:
            try:
                self.model_gateway.proxy_pool = EphemeralWarpPool()
                logger.info("WARP Proxy Pool attached to ModelGateway (opencode-zen bypass active)")
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(
                    f"WARP Proxy Pool initialization failed (will run without bypass): {e}"
                )
                self.model_gateway.proxy_pool = None
        else:
            self.model_gateway.proxy_pool = None

        self.headroom = get_headroom_middleware()
        self.observability = get_engine()  # Get singleton observability engine
        self.session_manager = SessionManager()
        self.memory_store = get_memory_store()
        self.lifecycle = SessionLifecycleManager(self.memory_store)
        self.searcher = SovereignSearcher(self.memory_store)
        self.verifier = SkepticalVerifier(self.model_gateway)
        # [M11] Throttled soul distillation counter - triggers close_session
        # every N interactions to avoid per-interrupt soul.yaml I/O.
        self._interaction_counter: Dict[str, int] = {}
        # [Somatic Flush] Turn counter for somatic re-hydration
        self._turn_counter: Dict[str, int] = {}
        self.researcher = IterativeResearcher(
            self.model_gateway, self.searcher, verifier=self.verifier
        )
        # [Workstream B] Selective Hydration - L3 gnosis retrieval for context injection
        self.selective_hydration = SelectiveHydration(
            embedding_manager=self.memory_store.embedding_manager,
            vector_adapter=self.memory_store.vector_store,
        )
        self.context_builder = ContextBuilder(
            selective_hydration=self.selective_hydration,
        )
        self.pii_masker = PIIMasker()
        self.intent_matcher = IntentMatcher()

        # [D16-1] Audience Calibration Pipeline - output register transformation
        self.audience_calibrator = get_audience_calibrator()

        # [M11] Soul Edit History - immutable audit trail for soul.yaml changes
        self.soul_edit_history = SoulEditHistory()

        # [M12] Compaction Harvester - automated compaction monitoring and metrics
        self.compaction_harvester = CompactionHarvester()

        # [D187] Semantic Router - embedding-based entity routing.
        # NOTE: This is NOT a provider router. D-536 ("one router only: ProviderSelector")
        # refers to the *provider* routing layer (in provider_selector.py). The
        # SemanticRouter and TriageRouter below are entity/model routers, intentionally
        # coexisting with ProviderSelector. They select WHICH ENTITY to dispatch and
        # WHICH MODEL to use; ProviderSelector selects WHICH PROVIDER to call.
        # [M23-audit 2026-08-28: documented to address imposter auditor's confusion]
        self.semantic_router = SemanticRouter(
            registry=self.registry,
            embedding_manager=self.memory_store.embedding_manager,
        )

        # Load WADs
        self.wad_loader = WADLoader(self.registry)
        # TriageRouter — entity/model selection (NOT a provider router; see D-187
        # comment above). Coexists with ProviderSelector by design.
        self.triage_router = TriageRouter()

        # Load valid agents from AGENTS.md for mention validation
        self.valid_agents = self._get_valid_agents_from_md()

        # [D16-2] DPO recorder for training data collection
        self.dpo_recorder = None
        self._last_query = None

        self._bootstrapped = False

    async def bootstrap(self) -> None:
        """Initialize Oracle systems on first use."""
        if self._bootstrapped:
            return

        # Initialize Unified State Manager (USM)
        try:
            await initialize_usm()
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.error(f"USM initialization failed [{classification['mode']}]: {e}")

        # Run session lifecycle sweep (M12 Queue Integrity)
        # Active (0-7d) -> Archived (gzip) -> External (90d) -> Deleted (optional)
        try:
            stats = await self.lifecycle.run_lifecycle()
            if stats.archived or stats.externalized:
                logger.info(
                    "Session lifecycle sweep: archived=%d, externalized=%d, %.1fms",
                    stats.archived,
                    stats.externalized,
                    stats.duration_ms,
                )
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(
                f"Session lifecycle sweep failed during bootstrap [{classification['mode']}]: {e}"
            )

        # [D187] Bootstrap semantic router - pre-compute entity vectors
        try:
            await self.semantic_router.bootstrap()
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(f"Semantic router bootstrap failed [{classification['mode']}]: {e}")

        # [D16-2] Initialize DPO recorder for training data collection
        try:
            self.dpo_recorder = await initialize_dpo_recorder()
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(f"DPO recorder initialization failed [{classification['mode']}]: {e}")
            self.dpo_recorder = None

        # Registry is initialized in __init__, no bootstrap needed
        self._bootstrapped = True

    # ── INTENT DETECTION ───────────────────────────────────────────

    def _get_valid_agents_from_md(self) -> Set[str]:
        """Parse AGENTS.md to get a list of valid @-mention names.

        Returns a set of lowercase agent names found in the "Named Agents" table.
        """
        if Oracle._valid_agents_cache is not None:
            return Oracle._valid_agents_cache

        try:
            agents_md_path = AGENTS_MD  # D-281 Phase III: config_resolver (M2)
            if not agents_md_path.exists():
                return set()

            content = agents_md_path.read_text(encoding="utf-8")

            # Find the "Named Agents" table
            # We look for the section starting with "#### Named Agents" and take the table following it
            section_match = re.search(
                r"#### Named Agents.*?\n\| @-Mention \|.*?\|.*?\n\|---|---|---|---|",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            if not section_match:
                return set()

            # Extract the table body
            table_start = section_match.end()
            table_lines = content[table_start:].splitlines()

            agents = set()
            for line in table_lines:
                if line.strip() == "" or not line.startswith("|"):
                    break
                # The first column is the @-Mention: | `@kali` | ...
                cols = line.split("|")
                if len(cols) > 1:
                    mention = cols[1].strip().strip("`").strip()
                    if mention.startswith("@"):
                        agents.add(mention[1:].lower())

            Oracle._valid_agents_cache = agents
            return agents
        except (OSError, OmegaError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(
                f"Failed to parse AGENTS.md for valid agents [{classification['mode']}]: {e}"
            )
            return set()

    def _detect_summon(self, query: str) -> Optional[tuple]:
        """Detect Entity summon patterns.

        Supports:
        - @Entity query (at start)
        - @Entity within text (anywhere)
        - hey Entity, query
        - summon Entity, query

        Returns (entity_name, query) or None.
        """
        query_stripped = query.strip()
        if not query_stripped:
            return None

        # Pattern 1: @Entity query (at start)
        # Matches '@maat help me' -> ('maat', 'help me')
        start_match = re.match(r"^@(\w+)\s+(.*)", query_stripped)
        if start_match:
            entity_name = start_match.group(1).lower()
            # Validate against registry AND AGENTS.md list
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, start_match.group(2))

        # Pattern 2: @Entity within text
        # Matches 'Hello @maat, help me' -> ('maat', 'Hello @maat, help me')
        # NOTE: Python 3.13+ rejects alternation inside lookbehinds; using (?:...) non-capturing group instead
        mentions = re.findall(r"(?:^|\s)@(\w+)", query_stripped)
        for m in mentions:
            entity_name = m.lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, query_stripped)

        # Pattern 3: hey Entity, query
        # Matches 'hey Maat, help me' -> ('maat', 'help me')
        hey_match = re.match(r"^(?:hey|hi|summon)\s+(\w+),?\s+(.*)", query_stripped, re.IGNORECASE)
        if hey_match:
            entity_name = hey_match.group(1).lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, hey_match.group(2))

        return None

    def _detect_consult(self, query: str) -> Optional[tuple]:
        """Detect /consult Entity pattern. Returns (entity_name, query) or None."""
        match = re.match(r"^/consult\s+(\w+)\s+(.*)", query.strip())
        if match:
            return (match.group(1).lower(), match.group(2))
        return None

    def assess_confidence(self, query: str) -> float:
        """Public alias for _assess_iris_confidence (P0-B: M-A2b fix).

        [P0-B aligned: zero id-soft heritage, pure Python pattern.]
        """
        return self._assess_iris_confidence(query)

    def _assess_iris_confidence(self, query: str) -> float:
        """Assess whether Iris (speculative decoder) can answer alone.

        [D-kal-053] Refactored to use IntentMatcher for whole-word matching.
        """
        if self.intent_matcher.is_iris_capable(query):
            return 0.9

        # Zero-confidence patterns (escalate immediately)
        query_lower = query.lower()
        if any(
            kw in query_lower
            for kw in [
                "explain the meaning",
                "why is",
                "how does",
                "meaning of",
                "purpose of",
                "philosophy",
                "metaphysical",
                "abstract",
                "gravity",
                "justice",
                "morality",
                "ethics",
            ]
        ):
            return 0.0

        # Low-confidence patterns (escalate to nodes)
        if any(
            kw in query_lower
            for kw in [
                "@",
                "/",
                "code",
                "api",
                "architecture",
                "design",
                "plan",
                "deploy",
                "deploy",
                "debug",
                "error",
                "bug",
                "implement",
            ]
        ):
            return 0.2

        # Medium confidence for general queries
        return 0.5

    def _empty_response(self, trace: TraceSession) -> OracleResponse:
        """Generate response for empty query."""
        return OracleResponse(
            text="The Oracle awaits your question.",
            entity="Oracle",
            confidence=0.0,
            trace_id=trace.trace_id,
            session_id=None,
        )

    async def _update_system_pressure(self) -> None:
        """Update the degradation manager based on real-time hardware stats."""
        from omega.hub import get_hardware_stats

        try:
            stats = await get_hardware_stats()
            await self.degradation_manager.evaluate_pressure(
                {
                    "cpu_load": stats.get("cpu_usage", 0.0) / 100.0,
                    "ram_free_mb": stats.get("memory_available_mb", 1024),
                }
            )
            logger.debug(
                "System pressure updated. Current level: %s",
                self.degradation_manager.get_current_level(),
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning("Failed to update system pressure: %s", e)

    async def talk(
        self,
        query: Union[str, TaintedData],
        transient: bool = False,
        audience: Optional[str] = None,
    ) -> OracleResponse:
        """Route a query through the speculative decoder + escalation pipeline.

        Args:
            query: The user query (can be TaintedData for external input)
            transient: If True, do not record the interaction in the soul/memory
            audience: Optional audience profile name (S7). When set, the response
                register is adapted via the cognition AudienceCalibrator before
                delivery.
        """
        # Sanitize and isolate query if it's tainted

        processed_query = TDPGate.isolate(query) if isinstance(query, TaintedData) else query

        async def _execute_turn():
            async with self.observability.trace() as trace:
                # 0. Update system pressure for graceful degradation
                await self._update_system_pressure()

                trace.log("query.received", query=processed_query, transient=transient)

                # [S3] Tiny-Critic RAG Router - classify query complexity as an
                # ephemeral routing signal. Advisory only: never blocks the turn.
                rag_complexity = "simple"
                try:
                    from omega.rag.router import RAGRouter

                    router = RAGRouter(mode="tfidf_svm")
                    rag_complexity = await router.classify(processed_query)
                except Exception as e:  # noqa: BLE001 - router is advisory
                    logger.warning("RAGRouter classification skipped (non-fatal): %s", e)
                trace.log("rag.classify", complexity=rag_complexity, query=processed_query)

                # Get current session for the default entity
                default_name = (
                    self.default_entity.name
                    if self.default_entity
                    else cvar_get("config.entity.default", "default")
                )
                if transient:
                    session_id = self.session_manager.get_session_id_transient(trace.trace_id)
                else:
                    session_id = await self.session_manager.get_session_id(default_name)
                trace.log("session.active", session_id=session_id)

                # Early return for empty queries (still inside trace context)
                if not processed_query or not processed_query.strip():
                    resp = self._empty_response(trace)
                    resp.rag_complexity = rag_complexity
                    try:
                        await self._record_interaction(resp, processed_query, trace, transient)
                    except OmegaError as e:
                        classification = get_failure_registry().classify_error(e)
                        logger.error(
                            f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                        )
                    return resp

                # Step 1: Try explicit summon (bypasses speculative decoder)
                summoned = self._detect_summon(processed_query)
                if summoned:
                    entity_name, summon_query = summoned
                    session_id = await self.session_manager.get_session_id(entity_name)
                    trace.log(
                        "summon.detected",
                        entity=entity_name,
                        query=summon_query,
                        session_id=session_id,
                    )
                    resp = await self._summon(
                        entity_name, summon_query, trace, session_id, transient=transient
                    )
                    resp.rag_complexity = rag_complexity
                    try:
                        await self._record_interaction(resp, summon_query, trace, transient)
                    except OmegaError as e:
                        classification = get_failure_registry().classify_error(e)
                        logger.error(
                            f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                        )
                    return resp

                # Step 1.5: Try consult pattern
                consulted = self._detect_consult(processed_query)
                if consulted:
                    entity_name, consult_query = consulted
                    session_id = await self.session_manager.get_session_id(entity_name)
                    trace.log(
                        "summon.detected",
                        entity=entity_name,
                        query=consult_query,
                        pattern="consult",
                        session_id=session_id,
                    )
                    resp = await self._summon(
                        entity_name, consult_query, trace, session_id, transient=transient
                    )
                    resp.rag_complexity = rag_complexity
                    try:
                        await self._record_interaction(resp, consult_query, trace, transient)
                    except OmegaError as e:
                        classification = get_failure_registry().classify_error(e)
                        logger.error(
                            f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                        )
                    return resp

                # Step 2: Speculative decode - Iris tries first
                # [D-kal-054] Restrict Iris to local chat channels only per user instruction.
                # Bypassed for OpenCode, Gemini, Cline, and Antigravity.
                channel = cvar_get("config.channel", "unknown")
                skip_iris = channel in ["opencode", "gemini-cli", "cline", "antigravity"]

                iris_confidence = (
                    self._assess_iris_confidence(processed_query) if not skip_iris else 0.0
                )
                trace.log(
                    "iris.speculative",
                    confidence=iris_confidence,
                    query=processed_query,
                    channel=channel,
                    skipped=skip_iris,
                )

                if iris_confidence > IRIS_CONFIDENCE_THRESHOLD:
                    resp = await self._respond_as_iris(
                        processed_query, trace, iris_confidence, session_id, transient=transient
                    )
                    resp.rag_complexity = rag_complexity
                    try:
                        await self._record_interaction(resp, processed_query, trace, transient)
                    except OmegaError as e:
                        classification = get_failure_registry().classify_error(e)
                        logger.error(
                            f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                        )
                    return resp

                # Step 3: Escalate to domain-matched Node
                trace.log(
                    "escalation",
                    reason=f"iris_confidence={iris_confidence:.2f} <= threshold={IRIS_CONFIDENCE_THRESHOLD}",
                )
                resp = await self._route_by_domain(
                    processed_query, trace, session_id, transient=transient
                )
                resp.rag_complexity = rag_complexity
                try:
                    await self._record_interaction(resp, processed_query, trace, transient)
                except OmegaError as e:
                    classification = get_failure_registry().classify_error(e)
                    logger.error(
                        f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                    )
                return resp

        resp = await self.timeout_manager.execute("turn", _execute_turn)
        if audience:
            resp = await self._apply_cognition_audience(resp, audience)
        return resp

    async def _apply_cognition_audience(
        self, resp: "OracleResponse", audience: str
    ) -> "OracleResponse":
        """[S7] Adapt the response register to the named audience via the cognition
        AudienceCalibrator. Preserves entity soul (voice_anchor) and all facts.

        Opt-in layer keyed on the ``audience`` argument; the existing oracle/
        audience_calibrator pipeline (D16-1) still runs unconditionally. This is
        the canonical register-adaptation stage from DIRECTIVE_AUDIENCE_CALIBRATION.
        """
        try:
            cal = self.audience_calibrator
            prof = cal.get_profile(audience)
            if prof is None:
                logger.warning("Audience profile '%s' not found; skipping calibration", audience)
                return resp
            voice_anchor = resp.entity or "Oracle"
            calibrated = await cal.render(resp.text, prof, voice_anchor)
            resp.text = calibrated
            resp.audience = audience
        except Exception as e:  # noqa: BLE001 - audience adaptation is advisory
            logger.warning("Audience calibration skipped (non-fatal): %s", e)
        return resp

    async def summon(
        self,
        entity_name: str,
        query: Union[str, TaintedData],
        transient: bool = False,
        model_override: Optional[str] = None,
    ) -> OracleResponse:
        """Directly summon a specific entity by name.

        [D118 Dual-Inference Mandate] When model_override is provided, the
        TriageRouter is bypassed and the specified model is used directly.
        This enables opt-in local routing for the MAKALI_COUNCIL parallel council.

        Args:
            entity_name: Name of the entity to summon
            query: The user query (can be TaintedData for external input)
            transient: If True, do not record the interaction in the soul/memory
            model_override: Optional model name to bypass TriageRouter and use
                            a specific model directly (e.g., 'qwen3-1.7b' for local)
        """
        # Sanitize and isolate query if it's tainted
        processed_query = TDPGate.isolate(query) if isinstance(query, TaintedData) else query

        await self.bootstrap()
        async with self.observability.trace() as trace:
            if transient:
                session_id = self.session_manager.get_session_id_transient(trace.trace_id)
            else:
                session_id = await self.session_manager.get_session_id(entity_name)
            trace.log(
                "summon.detected",
                entity=entity_name,
                query=processed_query,
                transient=transient,
                session_id=session_id,
                model_override=model_override,
            )
            resp = await self._summon(
                entity_name,
                processed_query,
                trace,
                session_id,
                transient=transient,
                model_override=model_override,
            )
            try:
                await self._record_interaction(resp, processed_query, trace, transient)
            except OmegaError as e:
                classification = get_failure_registry().classify_error(e)
                logger.error(
                    f"Recording interaction failed (non-fatal) [{classification['mode']}]: {e}"
                )
            return resp

    async def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> VerificationResult:
        """
        Public API to verify a claim against evidence using the Skeptical Verifier.
        """
        return await self.verifier.verify(claim, evidence)

    # ── INTERNAL: Triage Router bridge ─────────────────────────────────

    async def _select_model(
        self,
        entity_name: str,
        query: str,
        session_id: str,
        trace_id: str,
        domain: Optional[str] = None,
    ) -> str:
        """Select the optimal model for an entity+query via TriageRouter.

        Returns the model name string to use for generation.
        Falls back to the entity's configured model if TriageRouter is unavailable.
        """
        entity = self.registry.get(entity_name)
        if not entity:
            return "default"

        try:
            soul_path = DATA_DIR / "entities" / entity_name.lower() / "soul.yaml"
            entity_ctx = EntityContext(
                name=entity.name,
                soul_path=soul_path,
            )

            req = TriageRequest(
                task=TaskRequest(description=query, domain=domain or "general"),
                entity=entity_ctx,
                constraints=Constraints(),
                session=SessionContext(id=session_id, trace_id=trace_id),
            )

            response = await self.triage_router.select_model(req)
            return response.selected_model.name or entity.model or "default"
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(
                f"TriageRouter unavailable (falling back to entity model) [{classification['mode']}]: {e}"
            )
            return entity.model or "default"

    async def _prepare_system_prompt(
        self, entity_name: str, session_id: str, personality: str, query: Optional[str] = None
    ) -> str:
        """Build the system prompt with context injection.

        Combines:
        1. Entity personality (role/voice)
        2. Recent memory (MemoryStore hot/warm tiers)
        3. Soul hints (L3 universal principles from soul.yaml)
        """
        # Start with base personality
        prompt_parts = [f"You are {personality}"]

        # Inject context from MemoryStore
        try:
            # Pass current degradation level to adjust token budget
            degradation_level = self.degradation_manager.get_current_level()
            memory_context = await self.context_builder.build_context(
                entity_name, session_id, degradation_level=degradation_level, query=query
            )
            if memory_context:
                prompt_parts.append(f"\nContext from recent interactions:\n{memory_context}")
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(f"Context injection failed (non-fatal) [{classification['mode']}]: {e}")

        # Inject soul context - multi-path extractor (D-277)
        from omega.soul_utils import load_entity_soul_context

        try:
            soul_context = load_entity_soul_context(entity_name, DATA_DIR)
            if soul_context:
                prompt_parts.append(f"\nSovereign Context:\n{soul_context}")
                logger.debug(
                    "Soul injection for '%s' successful: %d chars", entity_name, len(soul_context)
                )
            else:
                logger.warning(
                    "Soul injection for '%s' returned empty - check schema.", entity_name
                )
        except Exception as e:
            logger.warning("Soul injection failed (non-fatal) for '%s': %s", entity_name, e)

        return "\n".join(prompt_parts)

    async def _record_interaction(
        self, resp: OracleResponse, query: str, trace: TraceSession, transient: bool
    ) -> None:
        """Record query+response in MemoryStore and soul.yaml."""
        if transient:
            return

        try:
            session_id = resp.session_id or trace.trace_id
            await self.memory_store.add_exchange(
                entity_name=resp.entity,
                session_id=session_id,
                user_message=query,
                response=resp.text,
                metadata={
                    "trace_id": trace.trace_id,
                    "confidence": resp.confidence,
                    "model": resp.model or "unknown",
                    "backend": resp.backend or "unknown",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(f"MemoryStore record failed (non-fatal) [{classification['mode']}]: {e}")

        # Track soul evolution
        try:
            await self._track_soul_evolution(resp.entity, trace.trace_id)
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(
                f"Soul evolution tracking failed (non-fatal) [{classification['mode']}]: {e}"
            )

        # [D16-2] Record DPO training pair from interaction (implicit mode)
        try:
            if self.dpo_recorder and hasattr(self, "_last_query") and self._last_query:
                await self.dpo_recorder.infer_from_interaction(
                    query=self._last_query,
                    response=resp.text,
                    trace_id=trace.trace_id,
                    session_id=session_id,
                    entity_name=resp.entity,
                    model_name=resp.model,
                    follow_up_query=query,  # Current query becomes follow-up to previous
                )
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(f"DPO recording failed (non-fatal) [{classification['mode']}]: {e}")

        # Store current query for next interaction's DPO inference
        self._last_query = query

        # [Somatic Flush] Track turns for KV cache purge
        session_key = f"{resp.entity}:{session_id}"
        self._turn_counter[session_key] = self._turn_counter.get(session_key, 0) + 1
        if self._turn_counter[session_key] >= 20:
            self._turn_counter[session_key] = 0
            try:
                await self._somatic_flush(resp.entity, session_id)
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"Somatic flush failed for {session_key}: {e}")

        # Throttled soul distillation - close_session every 5 interactions
        # [M11: Soul Integrity] Ensures L1->L2->L3 distillation happens continuously
        # on the hot path, not and not just from orchestrator.py CLI dispatch.
        # [M11-FIX-2026-07-01] Root cause: anyio.create_task() does NOT exist in
        # AnyIO (silent AttributeError swallowed by outer try/except). Replaced with
        # direct await + guarded try/except. close_session was NEVER executing.
        entity_key = f"{resp.entity}:{resp.session_id or trace.trace_id}"
        self._interaction_counter[entity_key] = self._interaction_counter.get(entity_key, 0) + 1
        if self._interaction_counter[entity_key] >= 5:
            self._interaction_counter[entity_key] = 0
            if resp.session_id:
                try:
                    await self.close_session(resp.entity, resp.session_id)
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning(f"Throttled soul distillation failed for {resp.entity}: {e}")

    async def retrieve_headroom_content(self, ref_id: str) -> str:
        """
        Retrieve the original, uncompressed content for a given reference ID.

        This is the 'Retrieve' part of the CCR (Compress-Cache-Retrieve) pattern,
        allowing agents to recover high-fidelity data when semantic compression
        is too aggressive.
        """
        try:
            return await self.headroom.retrieve_original(ref_id)
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.error(f"Headroom retrieval failed for {ref_id} [{classification['mode']}]: {e}")
            return f"[[ERROR: Original content for {ref_id} could not be retrieved]]"

    async def _respond_as_iris(
        self,
        query: str,
        trace: TraceSession,
        confidence: float,
        session_id: Optional[str] = None,
        transient: bool = False,
    ) -> OracleResponse:
        """Iris (speculative decoder) responds directly without invoking a node.

        [id-soft: vet-069] Speculative Decode - lightweight, fast path for
        simple queries that don't require domain expertise.

        [D-kal-053] Now attempts model invocation for Messenger Bridge via _summon.
        """
        try:
            # Attempt to invoke Messenger Bridge as a real model-backed entity
            messenger_bridge = _get_entity_by_role(ROLE_CONSTANTS["MESSENGER_BRIDGE"])
            if messenger_bridge and self.registry.get(messenger_bridge):
                return await self._summon(
                    messenger_bridge, query, trace, session_id, transient=transient
                )
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.warning(
                f"Messenger Bridge model invocation failed (falling back to hardcoded) [{classification['mode']}]: {e}"
            )

        # Fallback to hardcoded response if Messenger Bridge entity is missing or fails
        messenger_bridge = _get_entity_by_role(ROLE_CONSTANTS["MESSENGER_BRIDGE"])
        entity_name = messenger_bridge or "Iris"  # fallback for display only
        text = (
            self.intent_matcher.iris_response(query)
            or f"Hello! I'm {entity_name}, the voice of the Oracle. How can I help you today?"
        )

        backend = await self.model_gateway.get_preferred_backend()

        result = OracleResponse(
            text=text,
            entity=entity_name,  # instead of hardcoded "Iris"
            confidence=confidence,
            trace_id=trace.trace_id,
            session_id=session_id,
            backend=backend,
            escalated=False,
        )

        trace.log("iris.responded", confidence=confidence, backend=backend, fallback=True)
        return result

    async def _summon(
        self,
        entity_name: str,
        query: str,
        trace: TraceSession,
        session_id: str,
        transient: bool = False,
        model_override: Optional[str] = None,
    ) -> OracleResponse:
        """It bypasses domain routing and directly communicates with the named entity."""

        async def _execute_summon():
            entity = self.registry.get(entity_name)

            if not entity:
                return OracleResponse(
                    text=f"Entity '{entity_name}' not found in the registry.",
                    entity="Oracle",
                    confidence=0.0,
                    trace_id=trace.trace_id,
                    session_id=session_id,
                )

            trace.log(
                "summon.direct",
                entity=entity.name,
                query=query,
                session_id=session_id,
                model_override=model_override,
            )

            # Build context and prepend to personality
            system_prompt = await self._prepare_system_prompt(
                entity.name, session_id, entity.personality, query=query
            )

            # Select model: use override if provided, otherwise use TriageRouter
            if model_override:
                model_name = model_override
            else:
                # [Sovereign Fix] Use currently selected session model from environment if available
                session_model = os.environ.get("OPENCODE_MODEL")
                if session_model:
                    model_name = session_model
                else:
                    model_name = await self._select_model(
                        entity.name, query, session_id, trace.trace_id
                    )

            # Resolve entity affinity for inference presets (temperature, system_prompt, context window)
            # [id-soft: vet-016] cvar pattern - YAML-backed affinity DB, hot-reloadable
            first_domain = entity.domains[0] if entity.domains else None
            affinity_result = await self.model_gateway.resolve_entity_affinity(
                entity_name=entity.name,
                query=query,
                context={"domain": first_domain},
            )
            effective_temperature = entity.temperature
            effective_system_prompt = system_prompt
            effective_max_tokens = 1024
            if affinity_result and affinity_result.inference_presets:
                # Affinity presets override entity defaults when present
                if (
                    affinity_result.inference_presets.temperature
                    and affinity_result.inference_presets.temperature != 0.7
                ):
                    effective_temperature = affinity_result.inference_presets.temperature
                if affinity_result.inference_presets.system_prompt:
                    effective_system_prompt = (
                        f"{affinity_result.inference_presets.system_prompt}\n\n{system_prompt}"
                    )
                if affinity_result.inference_presets.preferred_context:
                    effective_max_tokens = min(
                        affinity_result.inference_presets.preferred_context, 4096
                    )

            # [PII Masking] Check if cloud provider will be used and mask PII if so
            # Use get_preferred_backend to determine if we're likely sending to cloud
            preferred_backend = await self.model_gateway.get_preferred_backend()
            if self.pii_masker.should_mask(preferred_backend):
                (
                    masked_prompt,
                    masked_query,
                    token_map,
                ) = await self.pii_masker.process_system_prompt(
                    system_prompt=effective_system_prompt,
                    user_query=query,
                    provider_name=preferred_backend,
                )
                res = await self.model_gateway.generate(
                    model_name=model_name,
                    system_prompt=masked_prompt,
                    user_query=masked_query,
                    temperature=effective_temperature,
                    max_tokens=effective_max_tokens,
                    trace_id=trace.trace_id,
                )
                # Detokenize response to restore original PII values
                res.text = await self.pii_masker.process_response(res.text, token_map)
            else:
                # Local provider - no PII masking needed
                res = await self.model_gateway.generate(
                    model_name=model_name,
                    system_prompt=effective_system_prompt,
                    user_query=query,
                    temperature=effective_temperature,
                    max_tokens=effective_max_tokens,
                    trace_id=trace.trace_id,
                )

            # Record performance to MetricsDB
            await self.observability.record_performance(
                latency_ms=res.latency_ms,
                provider=res.provider_name,
                model_used=res.model_used,
                prompt_tokens=getattr(res, "prompt_tokens", 0),
                completion_tokens=getattr(res, "completion_tokens", 0),
                is_cloud=getattr(res, "is_cloud", False),
                trace_id=trace.trace_id,
                entity_id=entity.name,
            )

            # [D16-1] Audience Calibration - transform response to target register
            calibrated_text = res.text
            try:
                calibration_result = await self.audience_calibrator.calibrate(
                    response_text=res.text,
                    entity_personality=entity.personality,
                    query=query,
                    model_gateway=self.model_gateway,
                    trace_id=trace.trace_id,
                )
                calibrated_text = calibration_result.calibrated_text
                if calibration_result.token_ratio > 1.1:
                    logger.warning(
                        f"Audience calibration token ratio {calibration_result.token_ratio:.2f} exceeds 110% budget (profile: {calibration_result.profile_name})"
                    )
                trace.log(
                    "audience.calibrated",
                    profile=calibration_result.profile_name,
                    token_ratio=calibration_result.token_ratio,
                )
            except Exception as e:
                logger.warning(f"Audience calibration failed (non-fatal): {e}")
                trace.log("audience.calibration_failed", error=str(e))

            return OracleResponse(
                text=calibrated_text,
                entity=entity.name,
                slots=entity.slots if hasattr(entity, "slots") else None,
                domains=entity.domains if hasattr(entity, "domains") else None,
                confidence=1.0,
                trace_id=trace.trace_id,
                session_id=session_id,
                backend=res.provider_name,
                model=res.model_used,
            )

        return await self.timeout_manager.execute("group", _execute_summon)

    async def _route_by_domain(
        self, text: str, trace: TraceSession, session_id: str, transient: bool = False
    ) -> OracleResponse:
        """Route query to entity by domain keyword matching.

        [D187] Routing chain: semantic -> keyword -> default.
        """
        # [D187] Semantic routing - embedding-based entity matching
        keyword_entity = self.registry.find_by_domain(text)
        entity, confidence, method = await self.semantic_router.route(
            query=text,
            keyword_fallback=keyword_entity,
            default_entity=self.default_entity,
        )

        trace.log(
            "domain.routed",
            entity=entity.name if entity else None,
            confidence=confidence,
            method=method,
            session_id=session_id,
        )

        if not entity:
            return OracleResponse(
                text="The Oracle is here. Speak your question.",
                entity="Oracle",
                confidence=0.0,
                trace_id=trace.trace_id,
                session_id=session_id,
                escalated=True,
            )

        # Build context and prepend to personality
        system_prompt = await self._prepare_system_prompt(
            entity.name, session_id, entity.personality, query=text
        )

        # Generate response via model gateway with TriageRouter
        model_name = await self._select_model(entity.name, text, session_id, trace.trace_id)

        # [PII Masking] Check if cloud provider will be used and mask PII if so
        preferred_backend = await self.model_gateway.get_preferred_backend()
        if self.pii_masker.should_mask(preferred_backend):
            masked_prompt, masked_query, token_map = await self.pii_masker.process_system_prompt(
                system_prompt=system_prompt,
                user_query=text,
                provider_name=preferred_backend,
            )
            res = await self.model_gateway.generate(
                model_name=model_name,
                system_prompt=masked_prompt,
                user_query=masked_query,
                temperature=entity.temperature,
                max_tokens=1024,
                trace_id=trace.trace_id,
            )
            # Detokenize response
            res.text = await self.pii_masker.process_response(res.text, token_map)
        else:
            res = await self.model_gateway.generate(
                model_name=model_name,
                system_prompt=system_prompt,
                user_query=text,
                temperature=entity.temperature,
                max_tokens=1024,
                trace_id=trace.trace_id,
            )

        # Use the ACTUAL provider that served the response, not the preferred one
        backend = res.provider_name
        sigil_tag = entity.metadata.get("sigil", "")
        sigil_str = f" {sigil_tag}" if sigil_tag else ""

        # Record performance to MetricsDB
        await self.observability.record_performance(
            latency_ms=res.latency_ms,
            provider=res.provider_name,
            model_used=res.model_used,
            prompt_tokens=getattr(res, "prompt_tokens", 0),
            completion_tokens=getattr(res, "completion_tokens", 0),
            is_cloud=getattr(res, "is_cloud", False),
            trace_id=trace.trace_id,
            entity_id=entity.name,
        )

        # [D16-1] Audience Calibration - transform response to target register
        calibrated_text = res.text
        try:
            calibration_result = await self.audience_calibrator.calibrate(
                response_text=res.text,
                entity_personality=entity.personality,
                query=text,
                model_gateway=self.model_gateway,
                trace_id=trace.trace_id,
            )
            calibrated_text = calibration_result.calibrated_text
            if calibration_result.token_ratio > 1.1:
                logger.warning(
                    f"Audience calibration token ratio {calibration_result.token_ratio:.2f} exceeds 110% budget (profile: {calibration_result.profile_name})"
                )
            trace.log(
                "audience.calibrated",
                profile=calibration_result.profile_name,
                token_ratio=calibration_result.token_ratio,
            )
        except Exception as e:
            logger.warning(f"Audience calibration failed (non-fatal): {e}")
            trace.log("audience.calibration_failed", error=str(e))

        # Use the ACTUAL provider that served the response, not the preferred one
        backend = res.provider_name
        sigil_tag = entity.metadata.get("sigil", "")
        sigil_str = f" {sigil_tag}" if sigil_tag else ""

        result = OracleResponse(
            text=f"{entity.name} says: {calibrated_text}{sigil_str}",
            entity=entity.name,
            slots=entity.slots,
            domains=entity.domains,
            confidence=confidence,
            trace_id=trace.trace_id,
            backend=backend,
            model=model_name,
            session_id=session_id,
            escalated=True,
            cost_warning="\n\n⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. Local inference was unavailable or bypassed."
            if res.is_cloud
            else None,
        )

        trace.log(
            "model.completed",
            entity=entity.name,
            backend=backend,
            escalated=True,
            session_id=session_id,
        )
        trace.record(
            query=text,
            system_prompt=system_prompt,
            response=res.text,
            entity=entity.name,
            model=model_name,
            backend=backend,
            confidence=confidence,
            session_id=session_id,
        )
        return result

    # ── Soul evolution tracking ───────────────────────────────────────
    async def close_session(self, entity_name: str, session_id: str) -> bool:
        """Close a session - track compaction + capture somatic state.

        Soul distillation (L1->L2->L3) removed per Carmack Verdict (2026-07-30):
        regex-based extraction was fortune-cookie generation. Agents write
        their own lessons. That works.
        """
        try:
            exchanges = await self.memory_store.get_history(entity_name, session_id)
            if not exchanges:
                logger.info(f"No exchanges for session {session_id}, nothing to compact")
                return True

            # 1. Check session size and flag if near compaction threshold
            try:
                exchange_count = len(exchanges)
                report = self.compaction_harvester.assess_session(
                    entity_name,
                    session_id,
                    exchange_count,
                )
                if report.needs_compaction or report.near_threshold:
                    logger.info(
                        "Session %s for %s: %d exchanges (%s%s)",
                        session_id,
                        entity_name,
                        exchange_count,
                        "NEEDS COMPACTION" if report.needs_compaction else "",
                        "near threshold"
                        if report.near_threshold and not report.needs_compaction
                        else "",
                    )
                    after_count = max(exchange_count // 2, 15)
                    await self.compaction_harvester.record_compaction(
                        entity_name=entity_name,
                        session_id=session_id,
                        before_count=exchange_count,
                        after_count=after_count,
                        triggered_by="close_session",
                    )
            except (OmegaError, RuntimeError, OSError) as comp_exc:
                logger.warning(f"Compaction tracking failed for {session_id}: {comp_exc}")

            # 2. Capture somatic state (KV cache) if available
            try:
                somatic_hash = await self._capture_somatic_state(entity_name, session_id)
                if somatic_hash:
                    logger.info(
                        f"Captured somatic state for {entity_name} session {session_id}: {somatic_hash[:16]}..."
                    )
            except (OmegaError, RuntimeError, OSError) as somatic_exc:
                logger.warning(
                    f"Somatic capture failed for {entity_name} session {session_id}: {somatic_exc}"
                )

            return True
        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.error(
                f"Failed to close session {session_id} for {entity_name} [{classification['mode']}]: {e}"
            )
            return False

    async def _capture_somatic_state(self, entity_name: str, session_id: str) -> Optional[str]:
        """Capture KV cache state from the active provider and store in USM.

        Returns the CAS hash of the stored state, or None if not available.
        """
        try:
            # Get the provider that was used for this entity
            provider = self.model_gateway.get_provider_for_entity(entity_name)
            if not provider or not hasattr(provider, "save_state"):
                return None

            # Capture state from provider (runs in worker process)
            state_bytes = await provider.save_state()
            if not state_bytes:
                return None

            # Store in USM CAS
            usm = get_usm()
            state_key = f"somatic:{entity_name}:{session_id}"
            hash_ = await usm.save_state(state_key, state_bytes)
            return hash_
        except (OmegaError, RuntimeError, OSError, AttributeError) as e:
            logger.debug(f"Somatic capture not available for {entity_name}: {e}")
            return None

    async def _track_soul_evolution(self, entity_name: str, trace_id: str) -> None:
        """Update the entity's soul.yaml after each interaction.
        Implements the L1->L2->L3 refractive abstraction model for gnosis preservation.

        This is a lightweight real-time tracker - it logs a trace event.
        Full soul distillation (L1->L2->L3) is handled by close_session() on session end.

        [id-soft: vet-070] Save-game pattern - incremental autosave mirrors Quake's
        periodic state writes, gathering state progressively for the final save on exit.
        """
        if os.environ.get("OMEGA_ENV") == "test":
            return

        try:
            from omega.observability import EventType

            await get_engine().log_event(
                EventType.ENTITY_INTERACTION,
                trace_id,
                {"entity": entity_name, "event": "interaction_recorded"},
            )
        except (OmegaError, RuntimeError, OSError) as exc:
            logger.warning("Telemetry event failed for %s: %s", entity_name, exc)
            # Non-fatal - telemetry failure must not block the response

    async def _somatic_flush(self, entity_name: str, session_id: str) -> None:
        """Perform a somatic flush to clear KV cache and reset model state.

        1. Note exchange count as summary.
        2. Close session.
        3. Re-hydrate the entity with a minimal context note.
        """
        logger.info(f"Triggering Somatic Flush for {entity_name} [session={session_id}]")

        try:
            exchanges = await self.memory_store.get_history(entity_name, session_id)
            if not exchanges:
                return

            exchange_count = len(exchanges)
            summary = f"Somatic flush: {exchange_count} exchanges from session {session_id}"

            # 2. Close session
            await self.close_session(entity_name, session_id)

            # 3. Re-hydrate: Start new session and inject context note
            new_session_id = await self.session_manager.get_session_id(entity_name)
            await self.memory_store.add_exchange(
                entity_name=entity_name,
                session_id=new_session_id,
                user_message="[Somatic Flush]",
                response=summary,
                metadata={"type": "somatic_flush", "prev_session": session_id},
            )
            logger.info(f"Somatic Flush complete for {entity_name}. New session: {new_session_id}")

        except (OmegaError, RuntimeError, OSError) as e:
            classification = get_failure_registry().classify_error(e)
            logger.error(
                f"Somatic Flush failed for {entity_name} [{classification['mode']}]: {e}",
                exc_info=True,
            )

    # ── Somatic State API (M20) ──────────────────────────────────────────

    async def save_state(self, state_id: str) -> bool:
        """Save the current model's somatic state (KV cache) to disk.

        Delegates to the ModelGateway which finds the NativeGGUFProvider.

        Args:
            state_id: Unique identifier for the state snapshot.

        Returns:
            True if state was saved successfully, False otherwise.
        """
        return await self.model_gateway.save_state(state_id)

    async def load_state(self, state_id: str) -> bool:
        """Load a somatic state (KV cache) from disk into the current model.

        Delegates to the ModelGateway which finds the NativeGGUFProvider.

        Args:
            state_id: Unique identifier for the state snapshot.

        Returns:
            True if state was loaded successfully, False otherwise.
        """
        return await self.model_gateway.load_state(state_id)
