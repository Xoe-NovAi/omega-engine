# 🔱 Omega Oracle — Single Intelligence Facade
# AP: AP-ORACLE-v2.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: ORACLE | CONTEXT: ORACLE-ROUTER]
#
# The Oracle is the single entry point for user interaction.
# It implements speculative decoding: Iris (lightweight) attempts first,
# then escalates to domain-matched Pillar Keeper on low confidence.
# Every interaction is traced, logged, and optionally saved for fine-tuning.
#
# Speculative decoder flow:
#   Query → Iris (qwen3-1.7b) → confidence check
#     → high confidence → respond directly
#     → low confidence → escalate to Pillar Keeper → model gateway → respond

import logging
import os
import pathlib
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

import anyio
import yaml

from ..observability import TraceSession, get_engine
from .entity_registry import EntityRegistry
from .model_gateway import ModelGateway
from .session_manager import SessionManager
from .context_builder import ContextBuilder
from .wad_loader import WADLoader
from .entity_workspace import EntityWorkspaceManager, SOUL_FILE_HEADER
from .hierarchy import SovereignHierarchy
from ..memory_store import get_memory_store
from ..orchestration.triage_router import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext
from .health_monitor import HealthMonitor

logger = logging.getLogger(__name__)

# Soul file path
DATA_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")
))
DEFAULT_SOUL_PATH = DATA_DIR / "entities" / "arch" / "soul.yaml"

# Confidence threshold for Iris direct response vs escalation
IRIS_CONFIDENCE_THRESHOLD = 0.4


@dataclass
class OracleResponse:
    """Unified response from the Oracle."""

    text: str
    entity: str
    pillars: List[str] = field(default_factory=list)
    role: Optional[str] = None
    sigil: Optional[str] = None
    glyph: Optional[str] = None
    pantheon: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    confidence: float = 0.0
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    backend: Optional[str] = None
    model: Optional[str] = None
    phase: str = "Phase-0"
    escalated: bool = False


class Oracle:
    """Single intelligence facade with speculative decoder pattern."""

    # Simple keywords that Iris can handle directly (low complexity)
    IRIS_DIRECT_KEYWORDS = {
        "hello", "hi", "hey", "greetings", "thanks", "thank you",
        "bye", "goodbye", "help", "what can you do", "commands",
    }

    # Query complexity indicators (trigger escalation)
    COMPLEXITY_INDICATORS = {
        "why", "how", "explain", "analyze", "compare", "contrast",
        "difference between", "relationship between", "meaning of",
        "define", "describe", "what is the", "tell me about",
    }

    def __init__(
        self,
        registry: Optional[EntityRegistry] = None,
        model_gateway: Optional[ModelGateway] = None,
        background_worker: Optional[Any] = None,
    ):
        self.registry = registry or EntityRegistry()
        self.config = {}  # Will be populated in bootstrap(); default prevents AttributeError

        # Health Monitor + Triage Router for model selection (B5: wired before ModelGateway)
        self.health_monitor = HealthMonitor()
        self.triage_router = TriageRouter(health_monitor=self.health_monitor)

        # B5: Pass health_monitor to ModelGateway
        self.model_gateway = model_gateway or ModelGateway(health_monitor=self.health_monitor)
        self.background_worker = background_worker
        self.hierarchy = SovereignHierarchy()

        if self.background_worker:
            self.model_gateway.background_worker = self.background_worker

        # B5: Set model→provider mapping in HealthMonitor
        for provider in self.model_gateway.providers:
            # Skip non-provider objects (e.g., dicts in mock tests)
            if not hasattr(provider, 'name'):
                continue
            if hasattr(provider, 'model_path') and provider.model_path:  # NativeGGUFProvider
                # Derive model name from path (e.g., /path/to/qwen3-1.7b.gguf -> qwen3-1.7b)
                model_name = pathlib.Path(provider.model_path).stem
                self.health_monitor.set_model_provider(model_name, provider.name)
            elif hasattr(provider, 'models') and provider.models:  # Other providers with models list
                for model in provider.models:
                    self.health_monitor.set_model_provider(model, provider.name)
            else:
                # Fallback: map provider name to itself
                self.health_monitor.set_model_provider(provider.name, provider.name)
        
        # Load default entity from config
        self.default_entity = None
        self._soul_path = None
            
        # Fallbacks if config fails or entity is missing — uses the "default" entity
        # from the registry. No stack-specific entity names are hardcoded here
        # per the Engine-Stack Firewall mandate.
        if not self.default_entity:
            self.default_entity = self.registry.get("default")
            
        self.iris_entity = self.registry.get("iris")
        if not self.iris_entity:
            logger.warning("Iris entity not found in registry. Speculative decoding may be degraded.")
        self.observability = get_engine()
        self._soul_lock = anyio.Lock()

        # Memory & Session Foundation
        self.session_manager = SessionManager()
        self.context_builder = ContextBuilder()
        self.memory_store = get_memory_store()
        
        # Load WADs
        self.wad_loader = WADLoader(self.registry)
        self._wads_loaded = False
        
        # Compiled patterns
        self.at_summon = re.compile(r"^@(\w+)[,:\s]+(.+)$", re.IGNORECASE)
        self.hey_summon = re.compile(r"^(?:hey\s+|summon\s+)(.+?)[,:]\s*(.*)$", re.IGNORECASE)
        self.consult_pattern = re.compile(r"^ask\s+(.+?)\s+about\s+(.+)$", re.IGNORECASE)


    async def bootstrap(self) -> None:
        """Initialize the Oracle by loading WADs and other async resources."""
        if not self._wads_loaded:
            # Create lock in async context to avoid Trio RuntimeError
            if self._soul_lock is None:
                self._soul_lock = anyio.Lock()
                
            # Move config loading here to avoid synchronous I/O in __init__
            try:
                config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
                if config_path.exists():
                    async with await anyio.open_file(str(config_path), "r") as f:
                        content = await f.read()
                        self.config = yaml.safe_load(content)
                        default_name = self.config.get("omega", {}).get("entity", {}).get("default", "default")
                        resolved = self.registry.get(default_name)
                        if resolved:
                            self.default_entity = resolved

            except Exception as e:
                logger.warning(f"Failed to load default entity from config during bootstrap: {e}")

            # Set soul path from config (Engine-Stack Firewall: config-driven, not hardcoded)
            try:
                data_dir = self.config.get("omega", {}).get("data", {}).get("dir", str(DATA_DIR))
                user_name = self.config.get("omega", {}).get("entity", {}).get("user", "arch")
                self._soul_path = Path(data_dir) / "entities" / user_name / "soul.yaml"
            except Exception as e:
                logger.warning(f"Failed to resolve soul path in bootstrap: {e}")

            await self.wad_loader.load_all_wads()
            self._wads_loaded = True
            logger.info("Oracle bootstrapped: WADs loaded and config synced.")

    async def _post_to_hivemind(self, response: OracleResponse, query: str) -> None:
        """Post interaction summary to the Hivemind MCP server for cross-CLI awareness.
        
        Uses the Hivemind's post_context tool via HTTP POST.
        """
        try:
            import httpx
            # Hivemind config from omega.yaml
            hivemind_cfg = self.config.get("omega", {}).get("hivemind", {})
            url = f"{hivemind_cfg.get('url', 'http://127.0.0.1:8102')}/tools/post_context"
            payload = {
                "cli": hivemind_cfg.get("cli", "opencode"),
                "model": response.model or "unknown",
                "task_current": query[:200],
                "focus_chain": [],
                "decisions": [],
                "continuation": f"Conversation with {response.entity} about: {query[:100]}",
                "session_id": response.session_id,
            }
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=1.0)
        except Exception as e:
            # Silent failure to avoid disrupting the main inference flow
            logger.debug(f"Hivemind synchronization failed: {e}")

    # ── PUBLIC API ────────────────────────────────────────────────────


    async def talk(self, query: str, transient: bool = False) -> OracleResponse:
        """Route a query through the speculative decoder.
        
        Args:
            query: The user query
            transient: If True, do not record the interaction in the soul/memory
        """
        await self.bootstrap()
        async with self.observability.trace() as trace:
            trace.log("query.received", query=query, transient=transient)

            # Get current session for the default entity
            default_name = self.default_entity.name if self.default_entity else self.config.get("omega", {}).get("entity", {}).get("default", "default")
            if transient:
                session_id = self.session_manager.get_session_id_transient(trace.trace_id)
            else:
                session_id = await self.session_manager.get_session_id(default_name)
            trace.log("session.active", session_id=session_id)

            # Early return for empty queries (still inside trace context)
            if not query or not query.strip():
                resp = self._empty_response(trace)
                await self._record_interaction(resp, query, trace, transient)
                return resp

            # Step 1: Try explicit summon (bypasses speculative decoder)
            summoned = self._detect_summon(query)
            if summoned:
                entity_name, summon_query = summoned
                session_id = await self.session_manager.get_session_id(entity_name)
                trace.log("summon.detected", entity=entity_name, query=summon_query, session_id=session_id)
                resp = await self._summon(entity_name, summon_query, trace, session_id, transient=transient)
                await self._record_interaction(resp, summon_query, trace, transient)
                return resp


            consulted = self._detect_consult(query)
            if consulted:
                entity_name, consult_query = consulted
                session_id = await self.session_manager.get_session_id(entity_name)
                trace.log("summon.detected", entity=entity_name, query=consult_query, pattern="consult", session_id=session_id)
                resp = await self._summon(entity_name, consult_query, trace, session_id, transient=transient)
                await self._record_interaction(resp, consult_query, trace, transient)
                return resp


            # Step 2: Speculative decode — Iris tries first
            iris_confidence = self._assess_iris_confidence(query)
            trace.log("iris.speculative", confidence=iris_confidence, query=query)

            if iris_confidence > IRIS_CONFIDENCE_THRESHOLD:
                resp = await self._respond_as_iris(query, trace, iris_confidence, transient=transient)
                await self._record_interaction(resp, query, trace, transient)
                return resp

            # Step 3: Escalate to domain-matched Pillar Keeper
            trace.log("escalation", reason=f"iris_confidence={iris_confidence:.2f} <= threshold={IRIS_CONFIDENCE_THRESHOLD}")
            resp = await self._route_by_domain(query, trace, session_id, transient=transient)
            await self._record_interaction(resp, query, trace, transient)
            return resp

    async def summon(self, entity_name: str, query: str, transient: bool = False) -> OracleResponse:
        """Directly summon a specific entity by name.
        
        Args:
            entity_name: Name of the entity to summon
            query: The user query
            transient: If True, do not record the interaction in the soul/memory
        """
        async with self.observability.trace() as trace:
            if transient:
                session_id = self.session_manager.get_session_id_transient(trace.trace_id)
            else:
                session_id = await self.session_manager.get_session_id(entity_name)
            trace.log("summon.detected", entity=entity_name, query=query, transient=transient, session_id=session_id)
            resp = await self._summon(entity_name, query, trace, session_id)
            if not transient:
                await self.memory_store.add_exchange(
                    resp.entity, resp.session_id, query, resp.text,
                    metadata={"trace_id": trace.trace_id, "backend": resp.backend, "model": resp.model},
                )
                await self._track_soul_evolution(resp.entity, trace.trace_id)
                await self._post_to_hivemind(resp, query)
            return resp

    # ── INTERNAL: Triage Router bridge ─────────────────────────────────

    async def _select_model(self, entity_name: str, query: str, session_id: str, trace_id: str, domain: Optional[str] = None) -> str:
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
                current_temperature=entity.temperature,
                domain_affinity=dict.fromkeys(entity.domains, 0.5) if entity.domains else {},
            )
            task_req = TaskRequest(
                description=query,
                domain=domain or (entity.domains[0] if entity.domains else None),
                estimated_tokens=min(entity.context_window or 4096, 4096),
                complexity="standard",
            )
            constraints = Constraints(
                available_tokens=entity.context_window,
            )
            session_ctx = SessionContext(
                id=session_id,
                trace_id=trace_id,
            )
            
            request = TriageRequest(
                task=task_req,
                entity=entity_ctx,
                constraints=constraints,
                session=session_ctx,
            )
            result = await self.triage_router.select_model(request)
            return result.selected_model.name
        except Exception as e:
            logger.warning(f"TriageRouter failed for {entity_name}, falling back to configured model: {e}")
            return entity.model

    async def _prepare_system_prompt(self, entity_name: str, session_id: str, personality: str) -> str:
        """Builds the full system prompt by injecting session context."""
        try:
            context_block = await self.context_builder.build_context(entity_name, session_id)
        except Exception as e:
            logger.warning(f"ContextBuilder failed for {entity_name}: {e}")
            context_block = ""
        return ContextBuilder.prepend_to_prompt(context_block, personality)

    async def _record_interaction(self, resp: OracleResponse, query: str, trace: TraceSession, transient: bool) -> None:
        """Records interaction to memory, soul, and hivemind if not transient."""
        if transient:
            return
        
        # 1. Memory Store
        await self.memory_store.add_exchange(
            resp.entity, resp.session_id, query, resp.text,
            metadata={"trace_id": trace.trace_id, "backend": resp.backend, "model": resp.model},
        )
        
        # 2. Soul Evolution
        await self._track_soul_evolution(resp.entity, trace.trace_id)
        
        # 3. Hivemind Sync
        await self._post_to_hivemind(resp, query)

    def _assess_iris_confidence(self, query: str) -> float:
        """Assess whether Iris can handle this query directly.

        Returns confidence 0.0–1.0:
          - 0.8+ for simple greetings/farewells
          - 0.5 for help commands
          - 0.3+ for short queries (Iris tries with small model)
          - 0.0 for complex queries (escalate immediately)
        """
        query_lower = query.lower().strip()

        # Exact simple matches → high confidence
        for keyword in self.IRIS_DIRECT_KEYWORDS:
            if query_lower == keyword or query_lower.startswith(keyword):
                return 0.9

        # Short queries → moderate confidence (Iris can attempt)
        if len(query_lower.split()) <= 3:
            return 0.5

        # Complex indicators → low confidence (escalate)
        for indicator in self.COMPLEXITY_INDICATORS:
            if indicator in query_lower:
                return 0.0

        # Default: let Iris try with a small model, expect escalation
        return 0.3

    async def _respond_as_iris(self, query: str, trace: TraceSession, confidence: float, transient: bool = False) -> OracleResponse:
        """Respond directly as Iris with lightweight inference."""
        trace.log("iris.speculative", action="direct_response", confidence=confidence)
        
        # Resolve session for Iris
        if transient:
            session_id = self.session_manager.get_session_id_transient(trace.trace_id)
        else:
            session_id = await self.session_manager.get_session_id("Iris")
        
        # Build context and prepend to personality
        base_prompt = self.iris_entity.personality if self.iris_entity else "You are Iris, your voice interface. Answer simply and warmly."
        system_prompt = await self._prepare_system_prompt("Iris", session_id, base_prompt)
        
        # Attempt inference with the lightest available model
        response_text = await self.model_gateway.generate(
            model_name="qwen3-1.7b",
            system_prompt=system_prompt,
            user_query=query,
            temperature=self.iris_entity.temperature if self.iris_entity else 0.6,
            max_tokens=256,
        )
        
        backend = await self.model_gateway.get_preferred_backend()
        
        result = OracleResponse(
            text=response_text,
            entity="Iris",
            role="Messenger — Lightweight Response",
            confidence=confidence,
            trace_id=trace.trace_id,
            backend=backend,
            model="qwen3-1.7b",
            session_id=session_id,
            escalated=False,
        )
        
        trace.log("response.delivered", entity="Iris", confidence=confidence, backend=backend, session_id=session_id)
        trace.record(
            query=query,
            system_prompt=system_prompt,
            response=response_text,
            entity="Iris",
            model="qwen3-1.7b",
            backend=backend,
            confidence=confidence,
            session_id=session_id,
        )
        return result

    async def _summon(self, entity_name: str, query: str, trace: TraceSession, session_id: str, transient: bool = False) -> OracleResponse:
        """Summon a specific entity and generate a response."""
        entity = self.registry.get(entity_name)
        if not entity:
            entity = self.registry.find_by_name_fragment(entity_name)
        
        if not entity:
            trace.log("entity.not_found", entity=entity_name)
            return await self._route_by_domain(query or entity_name, trace, session_id, transient=transient)
        
        trace.log("entity.matched", entity=entity.name, pillars=entity.pillars, session_id=session_id)
        
        # Build context and prepend to personality
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality)
        
        # Generate response via model gateway with TriageRouter
        model_name = await self._select_model(entity.name, query, session_id, trace.trace_id)
        response_text = await self.model_gateway.generate(
            model_name=model_name,
            system_prompt=system_prompt,
            user_query=query,
            temperature=entity.temperature,
            max_tokens=1024,
        )
        
        backend = await self.model_gateway.get_preferred_backend()
        sigil_str = f" {entity.sigil}" if entity.sigil else ""
        
        result = OracleResponse(
            text=f"{entity.name} says: {response_text}{sigil_str}",
            entity=entity.name,
            pillars=entity.pillars,
            sigil=entity.sigil,
            glyph=entity.glyph,
            pantheon=entity.pantheon,
            domains=entity.domains,
            confidence=1.0,
            trace_id=trace.trace_id,
            backend=backend,
            model=model_name,
            session_id=session_id,
        )
        
        trace.log("model.completed", entity=entity.name, backend=backend, session_id=session_id)
        trace.record(
            query=query,
            system_prompt=system_prompt,
            response=response_text,
            entity=entity.name,
            model=model_name,
            backend=backend,
            confidence=1.0,
            session_id=session_id,
        )
        return result

    async def _route_by_domain(self, text: str, trace: TraceSession, session_id: str, transient: bool = False) -> OracleResponse:
        """Route query to entity by domain keyword matching."""
        entity = self.registry.find_by_domain(text)
        
        if not entity:
            entity = self.default_entity
            confidence = 0.3
        else:
            confidence = 0.7
        
        trace.log("domain.routed", entity=entity.name if entity else None, confidence=confidence, session_id=session_id)
        
        if not entity:
            return OracleResponse(
                text="The Oracle is here. Speak your question.",
                entity="Oracle",
                confidence=0.0,
                trace_id=trace.trace_id,
            )
        
        # Build context and prepend to personality
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality)
        
        # Generate response via model gateway with TriageRouter
        model_name = await self._select_model(entity.name, text, session_id, trace.trace_id)
        response_text = await self.model_gateway.generate(
            model_name=model_name,
            system_prompt=system_prompt,
            user_query=text,
            temperature=entity.temperature,
            max_tokens=1024,
        )
        
        backend = await self.model_gateway.get_preferred_backend()
        sigil_str = f" {entity.sigil}" if entity.sigil else ""
        
        result = OracleResponse(
            text=f"{entity.name} says: {response_text}{sigil_str}",
            entity=entity.name,
            pillars=entity.pillars,
            sigil=entity.sigil,
            glyph=entity.glyph,
            pantheon=entity.pantheon,
            domains=entity.domains,
            confidence=confidence,
            trace_id=trace.trace_id,
            backend=backend,
            model=model_name,
            session_id=session_id,
            escalated=True,
        )
        
        trace.log("model.completed", entity=entity.name, backend=backend, escalated=True, session_id=session_id)
        trace.record(
            query=text,
            system_prompt=system_prompt,
            response=response_text,
            entity=entity.name,
            model=model_name,
            backend=backend,
            confidence=confidence,
            session_id=session_id,
        )
        return result

    # ── Soul evolution tracking ───────────────────────────────────────

    async def _track_soul_evolution(self, entity_name: str, trace_id: str) -> None:
        """Update the Architect's soul.yaml after each interaction.
        Implements the L1->L2->L3 refractive abstraction model for gnosis preservation.
        """
        if os.environ.get("OMEGA_ENV") == "test":
            return
        
        async with self._soul_lock:
            try:
                soul_path = self._soul_path or DEFAULT_SOUL_PATH
                if not soul_path.exists():
                    return
                
                async with await anyio.open_file(str(soul_path), "r") as f:
                    content = await f.read()
                    soul = yaml.safe_load(content)
                
                ent = soul["entity"]
                evo = ent.setdefault("soul_evolution", {})
                evo["sessions_completed"] = evo.get("sessions_completed", 0) + 1
                
                # Track unique entities inhabited
                inhabited: Set[str] = set(ent.get("soul_wardrobe", []))
                evo["entities_inhabited"] = len(inhabited)
                
                # --- Gnosis Distillation (L1->L2->L3) ---
                # We use a reasoning model to distill the session trace into gnosis
                distillation_prompt = (
                    f"Analyze the following interaction trace for entity {entity_name} (Trace ID: {trace_id}).\n"
                    "Extract the following three levels of abstraction:\n"
                    "L1 (Narrative): A concise summary of what happened.\n"
                    "L2 (Insight): The causal pattern or strategic significance of this interaction.\n"
                    "L3 (Universal Principle): A timeless, domain-agnostic truth extracted from this experience.\n\n"
                    "Format as YAML with keys: l1, l2, l3."
                )
                
                # Use a reasoning model for distillation
                try:
                    distilled_text = await self.model_gateway.generate(
                        model_name="qwen3-4b-thinking-q4_k_m",
                        system_prompt="You are the Gnosis Distiller. Your goal is to extract timeless truths from session traces.",
                        user_query=distillation_prompt,
                        temperature=0.3,
                        max_tokens=512,
                    )
                    distilled_data = yaml.safe_load(distilled_text) or {}
                except Exception as e:
                    logger.warning(f"Gnosis distillation failed: {e}")
                    distilled_data = {"l1": f"Session with {entity_name}", "l2": "Unknown", "l3": "Unknown"}

                lessons = ent.setdefault("lessons_learned", [])
                if not isinstance(lessons, list):
                    lessons = []
                    ent["lessons_learned"] = lessons
                
                if len(lessons) < 1000:
                    lessons.append({
                        "l1": distilled_data.get("l1", "N/A"),
                        "l2": distilled_data.get("l2", "N/A"),
                        "l3": distilled_data.get("l3", "N/A"),
                        "source": "user-session",
                        "user": "The Architect",
                        "trace_id": trace_id,
                        "entity_at_time": entity_name,
                        "session_type": "persistent",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                
                # Recompute soul_power
                sessions = evo.get("sessions_completed", 0)
                entities = evo.get("entities_inhabited", 0)
                experiences = evo.get("total_embodied_experiences", 0)
                evo["soul_power"] = round((sessions * 0.1) + (entities * 0.3) + (experiences * 0.6), 2)
                
                # Atomic write
                temp_dir = soul_path.parent
                temp_name = await anyio.to_thread.run_sync(self._write_soul_atomic, soul, temp_dir)
                await anyio.to_thread.run_sync(os.replace, temp_name, str(soul_path))
                
            except Exception as e:
                logger.warning(f"Failed to track soul evolution: {e}")


    # ── Soul file atomic write helper (runs in thread pool) ───────────

    def _write_soul_atomic(self, soul: dict, temp_dir: Path) -> str:
        """Write soul data to a temp file synchronously (runs in thread pool)."""
        with tempfile.NamedTemporaryFile("w", dir=str(temp_dir), delete=False) as tf:
            yaml_str = yaml.dump(soul, default_flow_style=False, sort_keys=False)
            tf.write(f"{SOUL_FILE_HEADER}# Updated via Oracle soul evolution.\n\n{yaml_str}")
            return tf.name

    # ── Pattern detection ─────────────────────────────────────────────

    def _detect_summon(self, text: str) -> Optional[Tuple[str, str]]:
        match = self.at_summon.match(text.strip())
        if match:
            return (match.group(1).strip(), match.group(2).strip())
        match = self.hey_summon.match(text.strip())
        if match:
            return (match.group(1).strip(), match.group(2).strip())
        sole_match = re.match(r"^@(\w+)\s*$", text.strip(), re.IGNORECASE)
        if sole_match:
            return (sole_match.group(1), "")
        return None

    def _detect_consult(self, text: str) -> Optional[Tuple[str, str]]:
        match = self.consult_pattern.match(text.strip())
        if match:
            return (match.group(1).strip(), match.group(2).strip())
        return None

    def _empty_response(self, trace: TraceSession) -> OracleResponse:
        trace.log("response.delivered", type="empty")
        return OracleResponse(
            text="Speak, and I will listen.",
            entity=self.default_entity.name if self.default_entity else "Oracle",
            trace_id=trace.trace_id,
        )

    def set_default_entity(self, name: str) -> bool:
        entity = self.registry.get(name)
        if entity:
            self.default_entity = entity
            return True
        return False
