# AP: AP-PR-READINESS-v1.0.0
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
from functools import lru_cache
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
from .iterative_research import IterativeResearcher
from .skeptical_verifier import SkepticalVerifier, VerificationResult
from .security import TDPGate, TaintedData
from .pii_masker import PIIMasker
from .context_builder import ContextBuilder
from .semantic_router import SemanticRouter
from ..iris.matcher import IntentMatcher

from ..observability import new_trace_id, ObservabilityEngine, TraceSession, get_engine, DATA_DIR
from ..errors import OmegaError, SovereignDiskFullError, SoulCorruptionError, StateIntegrityError
from ..cvar_table import cvar_get, cvar_set, cvar_namespace
from .entity_registry import EntityRegistry, Entity
from ..memory_store import get_memory_store
from ..astrology import record_first_breath
from ..orchestration.triage_router import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext, ModelSelection

logger = logging.getLogger(__name__)

# Configuration
IRIS_CONFIDENCE_THRESHOLD = 0.6


@dataclass
class OracleResponse:
    """Structured response from the Oracle.
    
    Engine fields: text, entity, confidence, trace_id, slots, domains.
    WAD-specific display fields (sigil, glyph, pantheon, etc.) are in
    the Entity.metadata dict — accessed via entity.metadata.get("sigil").
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
    
    _valid_agents_cache: Optional[Set[str]] = None

    def __init__(self, registry: Optional[EntityRegistry] = None, model_gateway: Optional[ModelGateway] = None):
        from omega.oracle.health_monitor import get_health_monitor
        self.registry = registry or EntityRegistry()
        self.default_entity = self.registry.get(cvar_get("config.entity.default", "default"))
        self.orchestrator = Orchestrator()
        self.health_monitor = get_health_monitor()
        # Accept injected model_gateway to prevent double initialization
        # (hub creates ModelGateway at module level; Oracle was creating a second one)
        self.model_gateway = model_gateway or ModelGateway(health_monitor=self.health_monitor)
        self.observability = get_engine()  # Get singleton observability engine
        self.distiller = get_distiller()
        self.session_manager = SessionManager()
        self.memory_store = get_memory_store()
        self.searcher = SovereignSearcher(self.memory_store)
        self.verifier = SkepticalVerifier(self.model_gateway)
        # [M11] Throttled soul distillation counter — triggers close_session
        # every N interactions to avoid per-interrupt soul.yaml I/O.
        self._interaction_counter: Dict[str, int] = {}
        self.researcher = IterativeResearcher(self.model_gateway, self.searcher, verifier=self.verifier)
        self.context_builder = ContextBuilder()
        self.pii_masker = PIIMasker()
        self.intent_matcher = IntentMatcher()
        
        # [D187] Semantic Router — embedding-based entity routing
        self.semantic_router = SemanticRouter(
            registry=self.registry,
            embedding_manager=self.memory_store.embedding_manager,
        )
        
        # Load WADs
        self.wad_loader = WADLoader(self.registry)
        self.triage_router = TriageRouter()
        
        # Load valid agents from AGENTS.md for mention validation
        self.valid_agents = self._get_valid_agents_from_md()
        
        self._bootstrapped = False

    async def bootstrap(self) -> None:
        """Initialize Oracle systems on first use."""
        if self._bootstrapped:
            return
        
        # Archive old sessions (M12 Queue Integrity)
        try:
            await self.memory_store.archive_old_sessions()
        except Exception as e:
            logger.warning(f"Session archival failed during bootstrap: {e}")

        # [D187] Bootstrap semantic router — pre-compute entity vectors
        try:
            await self.semantic_router.bootstrap()
        except Exception as e:
            logger.warning(f"Semantic router bootstrap failed: {e}")

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
            agents_md_path = Path(__file__).resolve().parent.parent.parent.parent / "AGENTS.md"
            if not agents_md_path.exists():
                return set()
            
            content = agents_md_path.read_text(encoding="utf-8")
            
            # Find the "Named Agents" table
            # We look for the section starting with "#### Named Agents" and take the table following it
            section_match = re.search(r'#### Named Agents.*?\n\| @-Mention \|.*?\|.*?\n\|---|---|---|---|', content, re.DOTALL | re.IGNORECASE)
            if not section_match:
                return set()
            
            # Extract the table body
            table_start = section_match.end()
            table_lines = content[table_start:].splitlines()
            
            agents = set()
            for line in table_lines:
                if line.strip() == "" or not line.startswith('|'):
                    break
                # The first column is the @-Mention: | `@kali` | ...
                cols = line.split('|')
                if len(cols) > 1:
                    mention = cols[1].strip().strip('`').strip()
                    if mention.startswith('@'):
                        agents.add(mention[1:].lower())
            
            Oracle._valid_agents_cache = agents
            return agents
        except Exception as e:
            logger.warning(f"Failed to parse AGENTS.md for valid agents: {e}")
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
        start_match = re.match(r'^@(\w+)\s+(.*)', query_stripped)
        if start_match:
            entity_name = start_match.group(1).lower()
            # Validate against registry AND AGENTS.md list
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, start_match.group(2))

        # Pattern 2: @Entity within text
        # Matches 'Hello @maat, help me' -> ('maat', 'Hello @maat, help me')
        # NOTE: Python 3.13+ rejects alternation inside lookbehinds; using (?:...) non-capturing group instead
        mentions = re.findall(r'(?:^|\s)@(\w+)', query_stripped)
        for m in mentions:
            entity_name = m.lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, query_stripped)

        # Pattern 3: hey Entity, query
        # Matches 'hey Maat, help me' -> ('maat', 'help me')
        hey_match = re.match(r'^(?:hey|hi|summon)\s+(\w+),?\s+(.*)', query_stripped, re.IGNORECASE)
        if hey_match:
            entity_name = hey_match.group(1).lower()
            if self.registry.get(entity_name) or entity_name in self.valid_agents:
                return (entity_name, hey_match.group(2))

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
        
        [D-kal-053] Refactored to use IntentMatcher for whole-word matching.
        """
        if self.intent_matcher.is_iris_capable(query):
            return 0.9
        
        # Zero-confidence patterns (escalate immediately)
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["explain the meaning", "why is", "how does", 
                                              "meaning of", "purpose of", "philosophy",
                                              "metaphysical", "abstract", "gravity",
                                              "justice", "morality", "ethics"]):
            return 0.0
        
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
            session_id=None,
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
            # [D-kal-054] Restrict Iris to local chat channels only per user instruction.
            # Bypassed for OpenCode, Gemini, Cline, and Antigravity.
            channel = cvar_get("config.channel", "unknown")
            skip_iris = channel in ["opencode", "gemini-cli", "cline", "antigravity"]
            
            iris_confidence = self._assess_iris_confidence(processed_query) if not skip_iris else 0.0
            trace.log("iris.speculative", confidence=iris_confidence, query=processed_query, channel=channel, skipped=skip_iris)
            
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


    async def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> VerificationResult:
        """
        Public API to verify a claim against evidence using the Skeptical Verifier.
        """
        return await self.verifier.verify(claim, evidence)

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
                task=TaskRequest(description=query, domain=domain or "general"),
                entity=entity_ctx,
                constraints=Constraints(),
                session=SessionContext(id=session_id, trace_id=trace_id)
            )
            
            response = await self.triage_router.select_model(req)
            return response.selected_model.name or entity.model or "default"
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
            from omega.oracle.context_builder import ContextBuilder
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

        # Throttled soul distillation — close_session every 5 interactions
        # [M11: Soul Integrity] Ensures L1→L2→L3 distillation happens continuously
        # on the hot path, not just from orchestrator.py CLI dispatch.
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
                except Exception:
                    logger.warning("Throttled soul distillation failed for %s (non-fatal)", resp.entity)

    async def _respond_as_iris(self, query: str, trace: TraceSession, confidence: float, session_id: Optional[str] = None, transient: bool = False) -> OracleResponse:
        """Iris (speculative decoder) responds directly without invoking a pillar.
        
        [id-soft: quake3-1999] Speculative Decode — lightweight, fast path for
        simple queries that don't require domain expertise.
        
        [D-kal-053] Now attempts model invocation for Iris via _summon.
        """
        try:
            # Attempt to invoke Iris as a real model-backed entity
            if self.registry.get("iris"):
                return await self._summon("iris", query, trace, session_id, transient=transient)
        except Exception as e:
            logger.warning(f"Iris model invocation failed (falling back to hardcoded): {e}")

        # Fallback to hardcoded response if Iris entity is missing or fails
        text = self.intent_matcher.iris_response(query) or "Hello! I'm Iris, the voice of the Oracle. How can I help you today?"
        
        backend = await self.model_gateway.get_preferred_backend()
        
        result = OracleResponse(
            text=text,
            entity="Iris",
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
                session_id=session_id,
            )
        
        trace.log("summon.direct", entity=entity.name, query=query, session_id=session_id,
                 model_override=model_override)
        
        # Build context and prepend to personality
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality, query=query)
        
        # Select model: use override if provided, otherwise use TriageRouter
        if model_override:
            model_name = model_override
        else:
            # [Sovereign Fix] Use currently selected session model from environment if available
            session_model = os.environ.get("OPENCODE_MODEL")
            if session_model:
                model_name = session_model
            else:
                model_name = await self._select_model(entity.name, query, session_id, trace.trace_id)
        
        # Resolve entity affinity for inference presets (temperature, system_prompt, context window)
        # [id-soft: quake-1996] cvar pattern — YAML-backed affinity DB, hot-reloadable
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
            if affinity_result.inference_presets.temperature and affinity_result.inference_presets.temperature != 0.7:
                effective_temperature = affinity_result.inference_presets.temperature
            if affinity_result.inference_presets.system_prompt:
                effective_system_prompt = (
                    f"{affinity_result.inference_presets.system_prompt}\n\n"
                    f"{system_prompt}"
                )
            if affinity_result.inference_presets.preferred_context:
                effective_max_tokens = min(affinity_result.inference_presets.preferred_context, 4096)
        
        # [PII Masking] Check if cloud provider will be used and mask PII if so
        # Use get_preferred_backend to determine if we're likely sending to cloud
        preferred_backend = await self.model_gateway.get_preferred_backend()
        if self.pii_masker.should_mask(preferred_backend):
            masked_prompt, masked_query, token_map = await self.pii_masker.process_system_prompt(
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
            # Local provider — no PII masking needed
            res = await self.model_gateway.generate(
                model_name=model_name,
                system_prompt=effective_system_prompt,
                user_query=query,
                temperature=effective_temperature,
                max_tokens=effective_max_tokens,
                trace_id=trace.trace_id,
            )
        
        # Use the ACTUAL provider that served the response, not the preferred one
        backend = res.provider_name
        # [id-soft: quake3-1999] Hard-Boundary — WAD display fields accessed
        # via metadata dict, not as engine-level OracleResponse fields.
        sigil_tag = entity.metadata.get("sigil", "")
        sigil_str = f" {sigil_tag}" if sigil_tag else ""
        
        result = OracleResponse(
            text=f"{entity.name} says: {res.text}{sigil_str}",
            entity=entity.name,
            slots=entity.slots,
            domains=entity.domains,
            confidence=1.0,
            trace_id=trace.trace_id,
            backend=backend,
            model=model_name,
            session_id=session_id,
            escalated=False,
            cost_warning="\n\n⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. Local inference was unavailable or bypassed." if res.is_cloud else None,
        )
        
        trace.log("model.completed", entity=entity.name, backend=backend, escalated=False,
                   session_id=session_id, model_override=model_override)
        trace.record(
            query=query,
            system_prompt=system_prompt,
            response=res.text,
            entity=entity.name,
            model=model_name,
            backend=backend,
            confidence=1.0,
            session_id=session_id,
        )
        # [Sovereign] Record the "First Breath" for astrological alignment
        await record_first_breath(entity.name, res.text, trace.trace_id)
        return result

    async def _route_by_domain(self, text: str, trace: TraceSession, session_id: str, transient: bool = False) -> OracleResponse:
        """Route query to entity by domain keyword matching.
        
        [D187] Routing chain: semantic → keyword → default.
        """
        # [D187] Semantic routing — embedding-based entity matching
        keyword_entity = self.registry.find_by_domain(text)
        entity, confidence, method = await self.semantic_router.route(
            query=text,
            keyword_fallback=keyword_entity,
            default_entity=self.default_entity,
        )
        
        trace.log("domain.routed", entity=entity.name if entity else None, confidence=confidence, method=method, session_id=session_id)
        
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
        system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality, query=text)
        
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
        
        result = OracleResponse(
            text=f"{entity.name} says: {res.text}{sigil_str}",
            entity=entity.name,
            slots=entity.slots,
            domains=entity.domains,
            confidence=confidence,
            trace_id=trace.trace_id,
            backend=backend,
            model=model_name,
            session_id=session_id,
            escalated=True,
            cost_warning="\n\n⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. Local inference was unavailable or bypassed." if res.is_cloud else None,
        )
        
        trace.log("model.completed", entity=entity.name, backend=backend, escalated=True, session_id=session_id)
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
        # [Sovereign] Record the "First Breath" for astrological alignment
        logger.info(f"Recording first breath for routed entity: {entity.name}")
        await record_first_breath(entity.name, res.text, trace.trace_id)
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
                user_msg = ex.get("user", "")
                asst_msg = ex.get("assistant", "")
                if user_msg:
                    lines.append(f"[user]: {user_msg}")
                if asst_msg:
                    lines.append(f"[assistant]: {asst_msg}")
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
