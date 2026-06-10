# AP Token: AP-ORACLE-RESTORE-v2.3.0
# 🔱 The Oracle — Routing, Summoning, and Entity Intelligence
# ⬡ OMEGA ⬡ ORACLE ⬡ oracle.py (1100 lines)
#
# Single-source-of-truth for query routing, speculative decoding, entity summoning,
# and soul evolution. Acts as the gateway between user intent and the 10-pillar council.
#
# [id-soft: doom-1993] Oracle Summoning Pattern — Direct entity dispatch via _summon()
# [id-soft: quake-1996] Memory Zone — Long-term learning via soul.yaml
# [id-soft: quake3-1999] Triage Routing — Intent classification and entity selection

import logging
import os
import re
import errno
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import anyio
import yaml

from .session_manager import SessionManager
from .orchestrator import Orchestrator
from .model_gateway import ModelGateway
from .health_monitor import HealthMonitor
from .soul_distiller import get_distiller
from .wad_loader import WADLoader
from .search import SovereignSearcher
from .security import TDPGate, TaintedData
from .context_builder import ContextBuilder

from ..observability import new_trace_id, ObservabilityEngine, TraceSession, get_engine, DATA_DIR
from ..errors import OmegaError, SovereignDiskFullError, SoulCorruptionError, StateIntegrityError
from ..cvar_table import cvar_get, cvar_set, cvar_namespace
from .entity_registry import EntityRegistry, Entity
from ..memory_store import get_memory_store
from ..orchestration.triage_router import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext, ModelSelection

logger = logging.getLogger(__name__)

# Configuration
IRIS_CONFIDENCE_THRESHOLD = 0.6


@dataclass
class OracleResponse:
    """Structured response from the Oracle."""
    text: str
    entity: str = "Oracle"
    confidence: float = 0.5
    trace_id: str = ""
    sigil: Optional[str] = None
    glyph: Optional[str] = None
    pantheon: Optional[str] = None
    pillars: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    backend: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    escalated: bool = False
    cost_warning: Optional[str] = None


class Oracle:
    """
    The Oracle — unified routing, summoning, and entity intelligence.
    
    Responsibilities:
    1. Intent detection (talk vs @summon vs @consult patterns)
    2. Speculative decoding (Iris confidence assessment)
    3. Domain routing (escalation to Pillar Keepers)
    4. Entity summoning (direct dispatch to named entities)
    5. Soul evolution tracking (L1→L2→L3 learning)
    6. Cloud critique integration (TDP quarantine)
    """
    
    def __init__(self, registry: Optional[EntityRegistry] = None):
        from omega.oracle.health_monitor import get_health_monitor
        self.registry = registry or EntityRegistry()
        self.default_entity = self.registry.get("default") or self.registry.get("kali")
        self.orchestrator = Orchestrator()
        self.health_monitor = get_health_monitor()
        self.model_gateway = ModelGateway(health_monitor=self.health_monitor)
        self.observability = get_engine()  # Get singleton observability engine
        self.distiller = get_distiller()
        self.session_manager = SessionManager()
        self.memory_store = get_memory_store()
        self.searcher = SovereignSearcher(self.memory_store)
        self.context_builder = ContextBuilder()
        
        # Load WADs
        self.wad_loader = WADLoader(self.registry)
        self.triage_router = TriageRouter()
        
        self._bootstrapped = False

    async def bootstrap(self) -> None:
        """Initialize Oracle systems on first use."""
        if self._bootstrapped:
            return
        # Registry is initialized in __init__, no bootstrap needed
        self._bootstrapped = True

    # ── INTENT DETECTION ───────────────────────────────────────────
    
    def _detect_summon(self, query: str) -> Optional[tuple]:
        """Detect Entity summon patterns.
        
        Supports:
        - @Entity query
        - hey Entity, query
        - summon Entity, query
        
        Returns (entity_name, query) or None.
        """
        query_stripped = query.strip()
        
        # Pattern 1: @Entity query
        match = re.match(r'^@(\w+)\s+(.*)', query_stripped)
        if match:
            return (match.group(1).lower(), match.group(2))
        
        # Pattern 2: hey Entity, query
        match = re.match(r'^(?:hey|hi|summon)\s+(\w+),?\s+(.*)', query_stripped, re.IGNORECASE)
        if match:
            return (match.group(1).lower(), match.group(2))
        
        return None
    
    def _detect_consult(self, query: str) -> Optional[tuple]:
        """Detect /consult Entity pattern. Returns (entity_name, query) or None."""
        match = re.match(r'^/consult\s+(\w+)\s+(.*)', query.strip())
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
        
        Iris handles:
        - Greetings ("hello", "hi", "how are you")
        - Simple factual questions ("what time is it", "what's your name")
        - Meta-oracle questions ("how do you work", "who are you")
        
        Iris defers to pillars for:
        - Entity-specific queries (@entity pattern)
        - Complex technical queries (contain API, code, architecture, etc.)
        - Philosophical/abstract questions (meaning, why, metaphysical)
        - Multi-step workflows
        """
        query_lower = query.lower()
        
        # Zero-confidence patterns (escalate immediately)
        if any(kw in query_lower for kw in ["explain the meaning", "why is", "how does", 
                                              "meaning of", "purpose of", "philosophy",
                                              "metaphysical", "abstract", "gravity",
                                              "justice", "morality", "ethics"]):
            return 0.0
        
        # High-confidence patterns (Iris handles alone)
        if any(kw in query_lower for kw in ["hello", "hi", "hey", "greetings",
                                             "how are you", "what's your name", 
                                             "who are you", "how do you work",
                                             "what are you", "thanks", "thank you"]):
            return 0.9
        
        # Low-confidence patterns (escalate to pillars)
        if any(kw in query_lower for kw in ["@", "/", "code", "api", "architecture",
                                             "design", "plan", "deploy", "deploy",
                                             "debug", "error", "bug", "implement"]):
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
        )

    # ── PUBLIC API ────────────────────────────────────────────────────

    async def talk(self, query: Union[str, TaintedData], transient: bool = False) -> OracleResponse:
        """Route a query through the speculative decoder + escalation pipeline.
        
        Args:
            query: The user query (can be TaintedData for external input)
            transient: If True, do not record the interaction in the soul/memory
        """
        # Sanitize and isolate query if it's tainted
        processed_query = TDPGate.isolate(query) if isinstance(query, TaintedData) else query
        
        await self.bootstrap()
        async with self.observability.trace() as trace:
            trace.log("query.received", query=processed_query, transient=transient)
            
            # Get current session for the default entity
            default_name = self.default_entity.name if self.default_entity else cvar_get("config.entity.default", "default")
            if transient:
                session_id = self.session_manager.get_session_id_transient(trace.trace_id)
            else:
                session_id = await self.session_manager.get_session_id(default_name)
            trace.log("session.active", session_id=session_id)
            
            # Early return for empty queries (still inside trace context)
            if not processed_query or not processed_query.strip():
                resp = self._empty_response(trace)
                try:
                    await self._record_interaction(resp, processed_query, trace, transient)
                except OmegaError as e:
                    logger.error(f"Recording interaction failed (non-fatal): {e}")
                return resp
            
            # Step 1: Try explicit summon (bypasses speculative decoder)
            summoned = self._detect_summon(processed_query)
            if summoned:
                entity_name, summon_query = summoned
                session_id = await self.session_manager.get_session_id(entity_name)
                trace.log("summon.detected", entity=entity_name, query=summon_query, session_id=session_id)
                resp = await self._summon(entity_name, summon_query, trace, session_id, transient=transient)
                try:
                    await self._record_interaction(resp, summon_query, trace, transient)
                except OmegaError as e:
                    logger.error(f"Recording interaction failed (non-fatal): {e}")
                return resp
            
            # Step 1.5: Try consult pattern
            consulted = self._detect_consult(processed_query)
            if consulted:
                entity_name, consult_query = consulted
                session_id = await self.session_manager.get_session_id(entity_name)
                trace.log("summon.detected", entity=entity_name, query=consult_query, pattern="consult", session_id=session_id)
                resp = await self._summon(entity_name, consult_query, trace, session_id, transient=transient)
                try:
                    await self._record_interaction(resp, consult_query, trace, transient)
                except OmegaError as e:
                    logger.error(f"Recording interaction failed (non-fatal): {e}")
                return resp
            
            # Step 2: Speculative decode — Iris tries first
            iris_confidence = self._assess_iris_confidence(processed_query)
            trace.log("iris.speculative", confidence=iris_confidence, query=processed_query)
            
            if iris_confidence > IRIS_CONFIDENCE_THRESHOLD:
                resp = await self._respond_as_iris(processed_query, trace, iris_confidence, session_id, transient=transient)
                try:
                    await self._record_interaction(resp, processed_query, trace, transient)
                except OmegaError as e:
                    logger.error(f"Recording interaction failed (non-fatal): {e}")
                return resp
            
            # Step 3: Escalate to domain-matched Pillar Keeper
            trace.log("escalation", reason=f"iris_confidence={iris_confidence:.2f} <= threshold={IRIS_CONFIDENCE_THRESHOLD}")
            resp = await self._route_by_domain(processed_query, trace, session_id, transient=transient)
            try:
                await self._record_interaction(resp, processed_query, trace, transient)
            except OmegaError as e:
                logger.error(f"Recording interaction failed (non-fatal): {e}")
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
        This enables opt-in local routing for the MaKaLi parallel council.
        
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
            trace.log("summon.detected", entity=entity_name, query=processed_query, transient=transient,
                      session_id=session_id, model_override=model_override)
            resp = await self._summon(entity_name, processed_query, trace, session_id,
                                        transient=transient, model_override=model_override)
            try:
                await self._record_interaction(resp, processed_query, trace, transient)
            except OmegaError as e:
                logger.error(f"Recording interaction failed (non-fatal): {e}")
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
            )
            
            req = TriageRequest(
                entity=entity_ctx,
                query=query,
                domain=domain or "general",
                session_id=session_id,
                trace_id=trace_id,
                constraints=Constraints(),
            )
            
            selection = await self.triage_router.select(req)
            return selection.model_name or entity.model or "default"
        except Exception as e:
            logger.warning(f"TriageRouter unavailable (falling back to entity model): {e}")
            return entity.model or "default"

    async def _prepare_system_prompt(self, entity_name: str, session_id: str, personality: str, query: Optional[str] = None) -> str:
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
            from ..context_builder import ContextBuilder
            ctx_builder = ContextBuilder()
            memory_context = await ctx_builder.build_context(entity_name, session_id, query or "")
            if memory_context:
                prompt_parts.append(f"\nContext from recent interactions:\n{memory_context}")
        except Exception as e:
            logger.warning(f"Context injection failed (non-fatal): {e}")
        
        # Inject soul L3 principles
        try:
            soul_path = DATA_DIR / "entities" / entity_name.lower() / "soul.yaml"
            if soul_path.exists():
                with open(soul_path) as f:
                    soul = yaml.safe_load(f) or {}
                    lessons = soul.get("soul_evolution", {}).get("lessons_learned", [])
                    if lessons:
                        l3_principles = [L["L3"] for L in lessons if "L3" in L]
                        if l3_principles:
                            prompt_parts.append(f"\nUniversal Principles:\n" + "\n".join(f"- {p}" for p in l3_principles[-3:]))
        except Exception as e:
            logger.warning(f"Soul injection failed (non-fatal): {e}")
        
        return "\n".join(prompt_parts)

    async def _record_interaction(self, resp: OracleResponse, query: str, trace: TraceSession, transient: bool) -> None:
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
                }
            )
        except Exception as e:
            logger.warning(f"MemoryStore record failed (non-fatal): {e}")
        
        # Track soul evolution
        try:
            await self._track_soul_evolution(resp.entity, trace.trace_id)
        except Exception as e:
            logger.warning(f"Soul evolution tracking failed (non-fatal): {e}")

    async def _respond_as_iris(self, query: str, trace: TraceSession, confidence: float, session_id: Optional[str] = None, transient: bool = False) -> OracleResponse:
        """Iris (speculative decoder) responds directly without invoking a pillar.
        
        [id-soft: quake3-1999] Speculative Decode — lightweight, fast path for
        simple queries that don't require domain expertise.
        """
        # Determine Iris' response based on query content
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["hello", "hi", "hey"]):
            text = "Hello! I'm Iris, the voice of the Oracle. How can I help you today?"
        elif any(kw in query_lower for kw in ["who are you", "what are you"]):
            text = "I'm Iris, the speculative decoder for the Omega Engine. I handle simple questions and route complex queries to the appropriate Pillar Keeper."
        elif any(kw in query_lower for kw in ["how are you", "how do you do"]):
            text = "I'm operating normally and ready to assist. Thank you for asking!"
        elif any(kw in query_lower for kw in ["thanks", "thank you"]):
            text = "You're welcome! Is there anything else you'd like to know?"
        else:
            text = f"I'm not sure about that. Let me connect you with someone who might know better."
        
        backend = await self.model_gateway.get_preferred_backend()
        
        result = OracleResponse(
            text=text,
            entity="Iris",
            confidence=confidence,
            trace_id=trace.trace_id,
            session_id=session_id,  # Include session_id for memory recording
            backend=backend,
            escalated=False,
        )
        
        trace.log("iris.responded", confidence=confidence, backend=backend)
        trace.record(
            query=query,
            system_prompt="You are Iris, the speculative decoder.",
            response=text,
            entity="Iris",
            model="iris-speculative",
            backend=backend,
            confidence=confidence,
        )
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
        """Internal implementation: directly summon a specific entity by name.
        
        This is called by both the public summon() method and the talk() pattern detector.
        It bypasses domain routing and directly communicates with the named entity.
        """
        entity = self.registry.get(entity_name)
        
        if not entity:
            return OracleResponse(
                text=f"Entity '{entity_name}' not found in the registry.",
                entity="Oracle",
                confidence=0.0,
                trace_id=trace.trace_id,
            )
        
        trace.log("summon.direct", entity=entity.name, query=query, session_id=session_id,
                 model_override=model_override)
        
        # Build context and prepend to personality
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality, query=query)
        
        # Select model: use override if provided, otherwise use TriageRouter
        if model_override:
            model_name = model_override
        else:
            model_name = await self._select_model(entity.name, query, session_id, trace.trace_id)
        
        # Generate response via model gateway
        response_text, is_cloud = await self.model_gateway.generate(
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
            escalated=False,
            cost_warning="\n\n⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. Local inference was unavailable or bypassed." if is_cloud else None,
        )
        
        trace.log("model.completed", entity=entity.name, backend=backend, escalated=False,
                 session_id=session_id, model_override=model_override)
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
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality, query=text)
        
        # Generate response via model gateway with TriageRouter
        model_name = await self._select_model(entity.name, text, session_id, trace.trace_id)
        response_text, is_cloud = await self.model_gateway.generate(
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
            cost_warning="\n\n⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. Local inference was unavailable or bypassed." if is_cloud else None,
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
    async def close_session(self, entity_name: str, session_id: str) -> bool:
        """Trigger soul distillation for a session and close it.
        
        Implements Mandate 11 (Soul Integrity).
        
        [id-soft: quake-1996] Save-game pattern — auto-save on session end
        triggers L1→L2→L3 distillation, analogous to Quake's level-transition
        autosave.
        """
        try:
            # 1. Retrieve the session transcript from MemoryStore
            exchanges = await self.memory_store.get_history(entity_name, session_id)
            if not exchanges:
                logger.warning(f"No exchanges found for session {session_id}, skipping distillation")
                return False
            
            # Build a readable transcript from exchanges
            lines = []
            for ex in exchanges:
                role = ex.get("role", "unknown")
                content = ex.get("content", "")
                lines.append(f"[{role}]: {content}")
            transcript = "\n".join(lines)
            if not transcript:
                logger.warning(f"No transcript found for session {session_id}, skipping distillation")
                return False
            
            # 2. Distill and save to soul.yaml
            success = await self.distiller.distill_and_save(
                session_transcript=transcript,
                entity_name=entity_name,
                source_trace_id=session_id
            )
            
            if success:
                logger.info(f"Successfully distilled session {session_id} for {entity_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to close session {session_id} for {entity_name}: {e}")
            return False


    async def _track_soul_evolution(self, entity_name: str, trace_id: str) -> None:
        """Update the entity's soul.yaml after each interaction.
        Implements the L1->L2->L3 refractive abstraction model for gnosis preservation.
        
        This is a lightweight real-time tracker — it logs a trace event.
        Full soul distillation (L1→L2→L3) is handled by close_session() on session end.
        
        [id-soft: quake-1996] Save-game pattern — incremental autosave mirrors Quake's
        periodic state writes, gathering state progressively for the final save on exit.
        """
        if os.environ.get("OMEGA_ENV") == "test":
            return

        try:
            from omega.observability import EventType
            get_engine().log_event(
                EventType.ENTITY_INTERACTION, trace_id,
                {"entity": entity_name, "event": "interaction_recorded"}
            )
        except Exception as exc:
            logger.warning("Telemetry event failed for %s: %s", entity_name, exc)
            # Non-fatal — telemetry failure must not block the response

    async def _compact_soul(self, soul: dict) -> int:
        """Compact soul.yaml after growth. Returns final size in bytes."""
        pass
