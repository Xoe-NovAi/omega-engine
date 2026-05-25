import anyio
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
import json
import logging
from pathlib import Path

# --- Schemas ---

@dataclass
class TaskRequest:
    description: str
    domain: Optional[str] = None
    estimated_tokens: int = 1000
    complexity: str = "standard"  # fast | standard | deep
    preferred_models: List[str] = field(default_factory=list)

@dataclass
class EntityContext:
    name: str
    soul_path: Path
    current_temperature: Optional[float] = None
    domain_affinity: Dict[str, float] = field(default_factory=dict)

@dataclass
class Constraints:
    max_latency_ms: Optional[int] = None
    max_cost_usd: Optional[float] = None
    available_tokens: Optional[int] = None
    preferred_backends: List[str] = field(default_factory=lambda: ["local", "cloud"])

@dataclass
class SessionContext:
    id: str
    trace_id: str
    is_transient: bool = False

@dataclass
class TriageRequest:
    task: TaskRequest
    entity: EntityContext
    constraints: Constraints
    session: SessionContext

@dataclass
class ModelSelection:
    name: str
    provider: str
    context_window: int
    temperature: float

@dataclass
class FallbackOption:
    model: str
    provider: str
    reason: str

@dataclass
class TriageResponse:
    selected_model: ModelSelection
    fallback_chain: List[FallbackOption]
    confidence: float
    reasoning: List[str]
    estimated_latency_ms: int
    estimated_cost_usd: float
    routing_timestamp: str
    expires_at: str

# --- Triage Router ---

class TriageRouter:
    """
    Sovereign Triage Router: Deterministic model selection based on 
    domain, entity soul, and real-time health.
    """
    
    DOMAIN_KEYWORDS = {
        'strength': ['protect', 'defend', 'fight', 'strength', 'warrior', 'power', 'boundary'],
        'dream': ['imagine', 'create', 'inspire', 'poetry', 'healing', 'flow', 'emotion'],
        'will': ['sovereign', 'decision', 'light', 'rebellion', 'creation', 'forethought'],
        'voice': ['speak', 'knowledge', 'art', 'communication', 'speech', 'language'],
        'descent': ['dream', 'underworld', 'transformation', 'descent', 'rebirth'],
        'analysis': ['analyze', 'research', 'audit', 'review', 'synthesize', 'compare'],
        'creation': ['code', 'implement', 'build', 'design', 'architect', 'write'],
    }

    def __init__(self, health_monitor=None, capability_matrix=None):
        self.logger = logging.getLogger("omega.triage")
        self.health_monitor = health_monitor
        self.capability_matrix = capability_matrix or {}

    async def select_model(self, request: TriageRequest) -> TriageResponse:
        """Main entry point for model selection."""
        
        # 1. Domain Inference
        domain = await self._infer_domain(request)
        
        # 2. Entity Preference Lookup
        soul = await self._load_soul(request.entity.soul_path)
        preferred_models = soul.get('model_preferences', {}).get('by_domain', {}).get(domain, [])
        
        # 3. Candidate Pool Assembly
        candidates = await self._assemble_candidates(domain, preferred_models)
        
        # 4. Constraint Filtering
        available = await self._filter_candidates(candidates, request)
        
        if not available:
            # Emergency escalation to most capable model
            available = candidates
            
        # 5. Score Adjustment (Health + Quota)
        scored_candidates = await self._score_candidates(available)
        
        # 6. Selection
        best = max(scored_candidates, key=lambda x: x['score'])
        confidence = best['score']
        
        # 7. Fallback Chain Construction
        fallback_chain = await self._build_fallback_chain(scored_candidates, best)
        
        # 8. Dynamic Temperature Calculation
        temperature = request.entity.current_temperature
        if temperature is None:
            # Logic for dynamic temperature based on complexity and domain
            complexity_map = {"fast": 0.3, "standard": 0.7, "deep": 0.5}
            temperature = complexity_map.get(request.task.complexity, 0.7)
            # Adjust based on domain (e.g., creative domains higher temp)
            creative_domains = ["dream", "art", "poetry"]
            if domain in creative_domains:
                temperature = min(1.0, temperature + 0.2)
        
        # 9. Metadata Generation
        now = datetime.now(timezone.utc)
        
        return TriageResponse(
            selected_model=ModelSelection(
                name=best['model'].name,
                provider=best['model'].provider,
                context_window=best['model'].context_window,
                temperature=temperature
            ),
            fallback_chain=fallback_chain,
            confidence=confidence,
            reasoning=self._generate_reasoning(best, available, request, domain),
            estimated_latency_ms=self.health_monitor.get_latency_p99(best['model'].name) if self.health_monitor else 1000,
            estimated_cost_usd=self._estimate_cost(best['model'], request.task.estimated_tokens),
            routing_timestamp=now.isoformat(),
            expires_at=(now + timedelta(seconds=10)).isoformat()
        )

    async def _infer_domain(self, request: TriageRequest) -> str:
        """Classify task domain via keyword matching + entity history."""
        if request.task.domain:
            return request.task.domain
            
        text = request.task.description.lower()
        scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[domain] = score
                
        if scores:
            return max(scores, key=scores.get)
            
        # Fallback to entity's most common recent domain
        soul = await self._load_soul(request.entity.soul_path)
        history = soul.get('routing_history', [])
        if history:
            domains = [h.get('task_domain') for h in history if h.get('task_domain')]
            if domains:
                return max(set(domains), key=domains.count)
                
        return "general"

    async def _load_soul(self, path: Path) -> Dict:
        """Load soul file using AnyIO thread pool to avoid blocking."""
        def _read():
            if not path.exists():
                return {}
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Failed to decode soul file at {path}: {e}")
                return {}
        return await anyio.to_thread.run_sync(_read)

    async def _assemble_candidates(self, domain: str, preferred_models: List[Any]) -> List[Dict]:
        """Build a ranked list of candidate models."""
        candidates = []
        
        # Tier 1: Entity-optimized (from soul.yaml)
        for model in preferred_models:
            if self.health_monitor and not self.health_monitor.is_available(model.name):
                continue
            candidates.append({
                'model': model,
                'tier': 'T1_entity_optimized',
                'score': 1.0,
            })
            
        # Tier 2: Task-appropriate (from capability matrix)
        domain_models = self.capability_matrix.get(domain, [])
        for model in domain_models:
            if any(m['model'] == model.name for m in preferred_models):
                continue
            if self.health_monitor and not self.health_monitor.is_available(model.name):
                continue
            candidates.append({
                'model': model,
                'tier': 'T2_task_appropriate',
                'score': 0.7,
            })
            
        # Tier 3: Universal Fallback
        universal = self.capability_matrix.get('universal')
        if universal:
            candidates.append({
                'model': universal,
                'tier': 'T3_universal_fallback',
                'score': 0.3,
            })
        else:
            # Absolute safety net: a mock model object
            class MockModel:
                name = "mock"
                provider = "mock"
                context_window = 4096
            candidates.append({
                'model': MockModel(),
                'tier': 'T3_universal_fallback',
                'score': 0.1,
            })
        
        return candidates

    async def _filter_candidates(self, candidates: List[Dict], request: TriageRequest) -> List[Dict]:
        """Filter candidates based on hard constraints."""
        available = []
        for c in candidates:
            model = c['model']
            if not model: continue
            
            # Context window check
            if request.constraints.available_tokens is not None and model.context_window < request.constraints.available_tokens:
                continue
                
            # Cost check
            cost = self._estimate_cost(model, request.task.estimated_tokens)
            if request.constraints.max_cost_usd and cost > request.constraints.max_cost_usd:
                continue
                
            # Latency check
            latency = self.health_monitor.get_latency_p99(model.name) if self.health_monitor else 1000
            if request.constraints.max_latency_ms and latency > request.constraints.max_latency_ms:
                continue
                
            available.append(c)
            
        return available

    async def _score_candidates(self, available: List[Dict]) -> List[Dict]:
        """Adjust scores based on real-time health and quota."""
        scored = []
        for c in available:
            score = c['score']
            model = c['model']
            
            if self.health_monitor:
                # Quota penalty (up to -30%)
                quota_usage = self.health_monitor.get_quota_usage(model.provider)
                score *= (1.0 - quota_usage * 0.3)
                
                # Success rate boost (up to +20%)
                success_rate = self.health_monitor.get_success_rate(model.name)
                score *= (0.8 + success_rate * 0.2)
                
            scored.append({**c, 'score': score})
            
        return scored

    async def _build_fallback_chain(self, scored: List[Dict], best: Dict) -> List[FallbackOption]:
        """Create a resilient fallback chain."""
        chain = []
        sorted_candidates = sorted(scored, key=lambda x: x['score'], reverse=True)
        
        for c in sorted_candidates:
            if c == best:
                continue
            chain.append(FallbackOption(
                model=c['model'].name,
                provider=c['model'].provider,
                reason=f"Tier {c['tier']} fallback"
            ))
            if len(chain) >= 3:
                break
                
        # Final safety net
        chain.append(FallbackOption(
            model="mock",
            provider="mock",
            reason="Final offline fallback"
        ))
        
        return chain

    def _estimate_cost(self, model: Any, tokens: int) -> float:
        """Simple cost estimation based on model metadata."""
        cost_per_1k = getattr(model, 'cost_per_1k_tokens', 0.0001)
        return (tokens / 1000) * cost_per_1k

    def _generate_reasoning(self, best: Dict, available: List[Dict], request: TriageRequest, domain: str) -> List[str]:
        """Generate human-readable rationale for the decision."""
        reasons = []
        reasons.append(f"Task classified as '{domain}' domain.")
        reasons.append(f"Selected {best['model'].name} via {best['model'].provider} (Confidence: {best['score']:.2f}).")
        reasons.append(f"Tier: {best['tier']}.")
        
        if best['tier'] == 'T1_entity_optimized':
            reasons.append(f"Model is optimized for {request.entity.name} in this domain.")
            
        return reasons
