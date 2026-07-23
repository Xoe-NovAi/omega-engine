"""
SoulDistiller — L1→L2→L3 distillation pipeline.
M5/M11 compliant: writes proposed_lessons.yaml (blind staging).

Architecture:
  L1 (Narrative): What happened?
  L2 (Insight): What does this mean?
  L3 (Universal Principle): What is the timeless truth?

Output: data/entities/{entity}/proposed_lessons.yaml (NOT soul.yaml)
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Literal
from dataclasses import dataclass, field

import yaml
import anyio

logger = logging.getLogger(__name__)

TierType = Literal["L1", "L2", "L3"]


@dataclass
class LessonProposal:
    """A single lesson proposal for proposed_lessons.yaml."""
    
    lesson_id: str
    tier: TierType
    principle: str = ""  # L3: Universal principle
    insight: str = ""    # L2: Pattern insight
    narrative: str = ""  # L1: What happened
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    source_sessions: List[str] = field(default_factory=list)
    mandate_refs: List[str] = field(default_factory=list)
    model_used: Optional[str] = None  # M22 provenance
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SoulDistiller:
    """
    L1→L2→L3 distillation pipeline.
    
    Writes to proposed_lessons.yaml (blind staging, NOT soul.yaml).
    M5/M11 compliant.
    """
    
    def __init__(self, entity_name: str, session_id: str, model: str = None):
        self.entity_name = entity_name
        self.session_id = session_id
        self.model = model  # M22 provenance
        self.entities_dir = Path("data/entities")
        self.entity_dir = self.entities_dir / entity_name
        self.proposed_path = self.entity_dir / "proposed_lessons.yaml"
        
        # Ensure entity dir exists
        self.entity_dir.mkdir(parents=True, exist_ok=True)
    
    async def distill_session(self) -> List[LessonProposal]:
        """Run full L1→L2→L3 pipeline for current session."""
        logger.info(f"[Scribe] Starting distillation for {self.entity_name} session {self.session_id}")
        
        # 1. Load session exchanges from MemoryStore
        exchanges = await self._load_session_exchanges()
        
        # 2. L1: Narrative distillation
        l1_proposals = self._distill_l1_narrative(exchanges)
        
        # 3. L2: Insight extraction
        l2_proposals = self._distill_l2_insight(l1_proposals)
        
        # 4. L3: Universal principle synthesis
        l3_proposals = self._distill_l3_principle(l2_proposals)
        
        # 5. All proposals
        all_proposals = l1_proposals + l2_proposals + l3_proposals
        
        # 6. Write proposed_lessons.yaml (blind staging)
        self._write_proposed_lessons(all_proposals)
        
        logger.info(f"[Scribe] Distilled {len(all_proposals)} lessons ({len(l1_proposals)} L1, {len(l2_proposals)} L2, {len(l3_proposals)} L3)")
        
        return all_proposals
    
    async def _load_session_exchanges(self) -> List[dict]:
        """Load exchanges from MemoryStore via Omega Hub."""
        logger.info(f"[Scribe] Loading exchanges for session {self.session_id}")
        
        try:
            # Import MemoryStore
            from omega.memory_store import get_memory_store
            
            memory_store = get_memory_store()
            if memory_store is None:
                logger.warning("[Scribe] MemoryStore not initialized, returning empty exchanges")
                return []
            
            # Get history for this entity and session
            exchanges = await memory_store.get_history(
                entity_name=self.entity_name,
                session_id=self.session_id,
                limit=100  # Limit to recent exchanges
            )
            
            logger.info(f"[Scribe] Loaded {len(exchanges)} exchanges from MemoryStore")
            return exchanges
            
        except Exception as e:
            logger.error(f"[Scribe] Failed to load session exchanges: {e}")
            return []
    
    def _distill_l1_narrative(self, exchanges: List[dict]) -> List[LessonProposal]:
        """L1: What happened? Structured narrative from raw exchanges."""
        proposals = []
        
        if not exchanges:
            # No exchanges to distill — return empty
            return proposals
        
        # Group exchanges into meaningful interactions
        interactions = self._group_into_interactions(exchanges)
        
        for i, interaction in enumerate(interactions):
            proposal = LessonProposal(
                lesson_id=f"l1-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{i:03d}",
                tier="L1",
                narrative=self._summarize_interaction(interaction),
                evidence=[f"exchange_{j}" for j in interaction.get("indices", [])],
                confidence=0.8,
                source_sessions=[self.session_id],
                model_used=self.model,
            )
            proposals.append(proposal)
        
        return proposals
    
    def _distill_l2_insight(self, l1_proposals: List[LessonProposal]) -> List[LessonProposal]:
        """L2: What does this mean? Pattern insights from narratives."""
        proposals = []
        
        if not l1_proposals:
            return proposals
        
        # Extract patterns from L1 narratives
        patterns = self._extract_patterns(l1_proposals)
        
        for i, pattern in enumerate(patterns):
            proposal = LessonProposal(
                lesson_id=f"l2-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{i:03d}",
                tier="L2",
                insight=pattern["insight"],
                evidence=pattern["evidence"],
                confidence=pattern["confidence"],
                source_sessions=[self.session_id],
                model_used=self.model,
            )
            proposals.append(proposal)
        
        return proposals
    
    def _distill_l3_principle(self, l2_proposals: List[LessonProposal]) -> List[LessonProposal]:
        """L3: What is the timeless truth? Universal principles from insights."""
        proposals = []
        
        if not l2_proposals:
            return proposals
        
        # Synthesize principles from L2 insights
        principles = self._synthesize_principles(l2_proposals)
        
        for i, principle in enumerate(principles):
            proposal = LessonProposal(
                lesson_id=f"l3-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{i:03d}",
                tier="L3",
                principle=principle["principle"],
                evidence=principle["evidence"],
                confidence=principle["confidence"],
                source_sessions=[self.session_id],
                mandate_refs=principle.get("mandate_refs", []),
                model_used=self.model,
            )
            proposals.append(proposal)
        
        return proposals
    
    def _group_into_interactions(self, exchanges: List[dict]) -> List[dict]:
        """Group exchanges into meaningful interactions."""
        # Simple grouping: each exchange is an interaction
        interactions = []
        for i, exchange in enumerate(exchanges):
            interactions.append({
                "indices": [i],
                "role": exchange.get("role", "unknown"),
                "content": exchange.get("content", ""),
            })
        return interactions
    
    def _summarize_interaction(self, interaction: dict) -> str:
        """Summarize an interaction into a narrative."""
        role = interaction.get("role", "unknown")
        content = interaction.get("content", "")
        # Truncate long content
        if len(content) > 200:
            content = content[:200] + "..."
        return f"[{role}] {content}"
    
    def _extract_patterns(self, l1_proposals: List[LessonProposal]) -> List[dict]:
        """Extract patterns from L1 narratives."""
        patterns = []
        for i, proposal in enumerate(l1_proposals):
            if proposal.narrative:
                patterns.append({
                    "insight": f"Pattern observed: {proposal.narrative[:100]}",
                    "evidence": proposal.evidence,
                    "confidence": proposal.confidence * 0.9,  # Slightly lower confidence for derived insight
                })
        return patterns
    
    def _synthesize_principles(self, l2_proposals: List[LessonProposal]) -> List[dict]:
        """Synthesize universal principles from L2 insights."""
        principles = []
        for i, proposal in enumerate(l2_proposals):
            if proposal.insight:
                principles.append({
                    "principle": f"Universal principle from: {proposal.insight[:100]}",
                    "evidence": proposal.evidence,
                    "confidence": proposal.confidence * 0.85,  # Lower confidence for derived principle
                    "mandate_refs": [],
                })
        return principles
    
    def _write_proposed_lessons(self, proposals: List[LessonProposal]) -> None:
        """Write proposals to proposed_lessons.yaml (blind staging)."""
        data = {
            "proposals": [],
            "metadata": {
                "entity": self.entity_name,
                "session_id": self.session_id,
                "model_used": self.model,  # M22 provenance
                "distilled_at": datetime.now(timezone.utc).isoformat(),
                "tier_counts": {
                    "L1": sum(1 for p in proposals if p.tier == "L1"),
                    "L2": sum(1 for p in proposals if p.tier == "L2"),
                    "L3": sum(1 for p in proposals if p.tier == "L3"),
                },
            },
        }
        
        for proposal in proposals:
            proposal_dict = {
                "lesson_id": proposal.lesson_id,
                "tier": proposal.tier,
            }
            if proposal.tier == "L1":
                proposal_dict["narrative"] = proposal.narrative
            elif proposal.tier == "L2":
                proposal_dict["insight"] = proposal.insight
            elif proposal.tier == "L3":
                proposal_dict["principle"] = proposal.principle
            
            proposal_dict["evidence"] = proposal.evidence
            proposal_dict["confidence"] = proposal.confidence
            proposal_dict["source_sessions"] = proposal.source_sessions
            proposal_dict["mandate_refs"] = proposal.mandate_refs
            proposal_dict["model_used"] = proposal.model_used
            proposal_dict["timestamp"] = proposal.timestamp
            
            data["proposals"].append(proposal_dict)
        
        # Atomic write: tmp → fsync → replace
        import os
        tmp_path = self.proposed_path.with_suffix(".yaml.tmp")
        try:
            with open(tmp_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(self.proposed_path))
            # Dir fsync
            dir_fd = os.open(str(self.entity_dir), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            logger.info(f"[Scribe] Wrote {len(proposals)} proposals to {self.proposed_path}")
        except Exception as e:
            logger.error(f"[Scribe] Failed to write proposed_lessons.yaml: {e}")
            raise
