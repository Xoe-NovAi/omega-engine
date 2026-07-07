# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Engine — Soul Distillation Engine (L1→L2→L3)
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ SOUL-DISTILL
# AP: SOUL-DISTILL-v1.0.0
#
# Auto-distills session insights into entity soul.yaml files.
# Triggered on session end or manually by the Scribe agent.
#
# [id-soft: quake-1996] Save-game pattern — auto-save → summary → lesson.
#     Quake auto-saved on level transitions. This engine auto-distills on
#     session end, extracting L1 (narrative) → L2 (insight) → L3 (principle).
# [id-soft: doom-1993] WAD System — soul.yaml is data-driven, not hardcoded.
#     The engine reads/writes soul.yaml like a WAD reads lumps.
#
# Protocol docs: docs/strategy/SOUL_DISTILLATION_PROTOCOL.md

from omega.state import get_usm
import omega.observability as observability
import fcntl
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ── Abstraction Levels ───────────────────────────────────────────────────

AbstractionLevel = Literal["L1", "L2", "L3"]


@dataclass
class DistillationEntry:
    """A single distilled insight from a session.

    L1 (Narrative): What happened? — raw events, actions, outcomes.
    L2 (Insight): What does this mean? — patterns, implications, lessons.
    L3 (Principle): What is the timeless truth? — universal laws, axioms.
    """
    level: AbstractionLevel
    content: str
    source_trace_id: Optional[str] = None
    source_entity: Optional[str] = None
    created_at: float = 0.0

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().timestamp()

    def to_yaml_block(self, indent: int = 4) -> str:
        """Format as YAML block for soul.yaml insertion."""
        spaces = " " * indent
        lines = [f"{spaces}- {self.level}_{'insight' if self.level == 'L2' else 'principle' if self.level == 'L3' else 'narrative'}: |"]
        for line in self.content.strip().split("\n"):
            lines.append(f"{spaces}    {line.strip()}")
        return "\n".join(lines)


# ── Enhanced 5-Stage Pipeline Components ────────────────────────────────
# Source: lesson-ai (deterministic), EloPhanto (conservative),
#         Microsoft Research, ICML 2026 (soul distillation pipeline)

@dataclass
class ClassificationResult:
    """Result of session classification."""
    is_routine: bool
    reason: str = ""
    novelty_score: float = 0.0
    confidence: float = 0.0


@dataclass
class QualityScore:
    """5-factor quality score for distilled lessons."""
    overall: float
    relevance: float = 0.0
    novelty: float = 0.0
    actionability: float = 0.0
    completeness: float = 0.0
    accuracy: float = 0.0


class SessionClassifier:
    """
    Conservative session classifier — returns routine for trivial sessions.
    Source: EloPhanto Learning Engine (2026)
    
    Only sessions with sufficient data and novelty pass through to distillation.
    """
    
    def __init__(
        self,
        min_events: int = 8,
        novelty_threshold: float = 0.3,
        title_threshold: int = 5,
    ):
        self.min_events = min_events
        self.novelty_threshold = novelty_threshold
        self.title_threshold = title_threshold
    
    def classify(self, transcript: str) -> ClassificationResult:
        """Classify a session transcript as routine or worth distilling."""
        word_count = len(transcript.split())
        
        # Check minimum size
        if word_count < self.min_events:
            return ClassificationResult(
                is_routine=True,
                reason="insufficient_events",
                novelty_score=0.0,
            )
        
        # Compute novelty score via TF-IDF-like heuristics
        novelty_score = self._compute_novelty(transcript)
        
        # Check for decision/insight signals
        has_decisions = bool(re.search(
            r"(decided|chose|implemented|fixed|refactored|created|added)",
            transcript, re.IGNORECASE
        ))
        has_errors = bool(re.search(
            r"(error|crash|bug|failed|exception|traceback)",
            transcript, re.IGNORECASE
        ))
        
        confidence = 0.0
        if has_decisions:
            confidence += 0.4
        if has_errors:
            confidence += 0.3
        if novelty_score > 0.5:
            confidence += 0.3
        
        if novelty_score < self.novelty_threshold and not has_decisions and not has_errors:
            return ClassificationResult(
                is_routine=True,
                reason="low_novelty",
                novelty_score=novelty_score,
                confidence=confidence,
            )
        
        return ClassificationResult(
            is_routine=False,
            novelty_score=novelty_score,
            confidence=confidence,
        )
    
    def _compute_novelty(self, transcript: str) -> float:
        """Compute novelty score using TF-IDF-like heuristics.
        Source: lesson-ai EventGraphBuilder pattern.
        """
        # Simple heuristic: ratio of unique non-stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'can', 'could', 'may', 'might', 'shall', 'should', 'to', 'of',
            'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'this', 'that', 'these', 'those', 'it', 'its', 'and', 'or',
            'but', 'not', 'no', 'nor', 'so', 'if', 'then', 'than',
        }
        words = re.findall(r'\b[a-zA-Z_]\w+\b', transcript.lower())
        if not words:
            return 0.0
        unique_meaningful = set(w for w in words if w not in stop_words and len(w) > 3)
        return round(len(unique_meaningful) / max(len(words), 1), 2)


class SovereigntyScorer:
    """
    5-factor quality scorer for distilled lessons.
    Source: lesson-ai + Microsoft Research ACON paper (ICML 2026).
    
    Scoring factors:
    - Relevance (30%): How relevant is this to the entity's domain?
    - Novelty (25%): How new is this insight?
    - Actionability (20%): Can this insight be acted upon?
    - Completeness (15%): Is the insight fully formed?
    - Accuracy (10%): Is the insight verifiable?
    """
    
    def __init__(
        self,
        min_pass_threshold: float = 0.6,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.min_pass_threshold = min_pass_threshold
        self.weights = weights or {
            "relevance": 0.30,
            "novelty": 0.25,
            "actionability": 0.20,
            "completeness": 0.15,
            "accuracy": 0.10,
        }
    
    def score(
        self,
        l1_narrative: str,
        l2_insight: str,
        l3_principle: str,
        entity_name: str,
    ) -> QualityScore:
        """Compute 5-factor quality score for a distillation."""
        
        # Relevance — how specific to the entity/domain
        entity_in_content = entity_name.lower() in (l1_narrative + l2_insight + l3_principle).lower()
        relevance = 0.7 if entity_in_content else 0.4
        
        # Novelty — unique content vs generic patterns
        has_specifics = bool(re.search(
            r"(file|commit|decision|config|module|function|method|test|import)",
            l2_insight, re.IGNORECASE
        ))
        has_timeless = len(l3_principle.split()) > 10
        novelty = 0.0
        if has_specifics:
            novelty += 0.5
        if has_timeless:
            novelty += 0.3
        
        # Actionability — can this be acted upon?
        has_action_verbs = bool(re.search(
            r"(verify|check|ensure|review|consider|refactor|add|create|update|fix)",
            l2_insight + l3_principle, re.IGNORECASE
        ))
        actionability = 0.8 if has_action_verbs else 0.4
        
        # Completeness — all three levels present with substance
        completeness = 0.0
        if len(l1_narrative.split()) > 5:
            completeness += 0.3
        if len(l2_insight.split()) > 5:
            completeness += 0.3
        if len(l3_principle.split()) > 8:
            completeness += 0.4
        
        # Accuracy — verifiable claims
        has_verifiable = bool(re.search(
            r"\b(created|fixed|added|removed|modified)\s+\S+\.\w+\b",
            l1_narrative, re.IGNORECASE
        ))
        accuracy = 0.8 if has_verifiable else 0.5
        
        # Compute weighted overall score
        overall = (
            self.weights["relevance"] * relevance +
            self.weights["novelty"] * novelty +
            self.weights["actionability"] * actionability +
            self.weights["completeness"] * completeness +
            self.weights["accuracy"] * accuracy
        )
        
        return QualityScore(
            overall=round(overall, 2),
            relevance=round(relevance, 2),
            novelty=round(novelty, 2),
            actionability=round(actionability, 2),
            completeness=round(completeness, 2),
            accuracy=round(accuracy, 2),
        )
    
    def is_above_threshold(self, score: QualityScore) -> bool:
        """Check if quality score meets minimum threshold."""
        return score.overall >= self.min_pass_threshold


class SoulDistillationPipeline:
    """
    Enhanced 5-stage soul distillation pipeline.
    Source: lesson-ai (deterministic) + EloPhanto (conservative) + Microsoft Research ACON.
    
    Pipeline: Classify → Extract → Distill → Score → Store.
    
    Only non-routine sessions with sufficient quality pass through to storage.
    """
    
    def __init__(
        self,
        classifier: Optional[SessionClassifier] = None,
        scorer: Optional[SovereigntyScorer] = None,
        distiller: Optional['SoulDistiller'] = None,
    ):
        self.classifier = classifier or SessionClassifier()
        self.scorer = scorer or SovereigntyScorer()
        self.distiller = distiller or SoulDistiller()
    
    async def run(
        self,
        session_transcript: str,
        entity_name: str,
        source_trace_id: Optional[str] = None,
    ) -> Optional[Dict[AbstractionLevel, DistillationEntry]]:
        """
        Run the full 5-stage distillation pipeline.
        
        Returns None for routine sessions or low-quality distillations.
        Returns dict of L1/L2/L3 entries for valid distillations.
        """
        # Stage 1: Classify
        classification = self.classifier.classify(session_transcript)
        if classification.is_routine:
            logger.debug(
                "Skipping distillation for %s: %s (novelty=%.2f)",
                entity_name, classification.reason, classification.novelty_score,
            )
            return None
        
        # Stage 2-3: Distill (Extract + Distill)
        try:
            entries = self.distiller.distill_session(
                session_transcript,
                entity_name,
                source_trace_id,
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Distillation failed for %s: %s", entity_name, e)
            return None
        
        # Stage 4: Score
        score = self.scorer.score(
            entries["L1"].content,
            entries["L2"].content,
            entries["L3"].content,
            entity_name,
        )
        
        if not self.scorer.is_above_threshold(score):
            logger.info(
                "Distillation below threshold for %s (score=%.2f, min=%.2f)",
                entity_name, score.overall, self.scorer.min_pass_threshold,
            )
            return None
        
        logger.info(
            "Distillation passed quality gate for %s (score=%.2f)",
            entity_name, score.overall,
        )
        
        # Stage 5: Store
        self.distiller.append_to_soul(entity_name, entries)
        
        return entries


# ── Soul Distillation Engine ─────────────────────────────────────────────


# ── Soul Distillation Engine ─────────────────────────────────────────────


class SoulDistiller:
    """Distills session insights into soul.yaml entries.

    The three-tier abstraction pipeline:
    L1 (Narrative) → L2 (Insight) → L3 (Universal Principle)

    [id-soft: quake-1996] Save-game pattern — auto-save → summary → lesson
    """

    def __init__(self, entities_dir: str = "data/entities") -> None:
        self._entities_dir = Path(entities_dir)

    def distill_session(
        self,
        session_transcript: str,
        entity_name: str,
        source_trace_id: Optional[str] = None,
    ) -> Dict[AbstractionLevel, DistillationEntry]:
        """Distill a session transcript into L1, L2, L3 entries.

        This is the core abstraction pipeline. Each level builds on the previous.

        Args:
            session_transcript: Full session text (user + assistant messages)
            entity_name: Entity whose soul.yaml to update
            source_trace_id: Optional trace ID for the session

        Returns:
            Dict with keys 'L1', 'L2', 'L3' mapping to DistillationEntry objects
        """
        # L1: Extract narrative from transcript
        l1 = self._extract_narrative(session_transcript, entity_name, source_trace_id)

        # L2: Distill insight from narrative
        l2 = self._distill_insight(l1.content, entity_name, source_trace_id)

        # L3: Extract universal principle from insight
        l3 = self._extract_principle(l2.content, entity_name, source_trace_id)

        return {"L1": l1, "L2": l2, "L3": l3}

    def _extract_narrative(
        self,
        transcript: str,
        entity_name: str,
        trace_id: Optional[str],
    ) -> DistillationEntry:
        """L1 (Narrative): What happened?

        Extracts key events, decisions, and outcomes from the transcript.
        Uses pattern matching to identify significant moments.
        """
        events = []

        # Detect decision moments
        decision_patterns = [
            r"(?:decided|chose|selected|picked|approved|rejected)\s+(.+?)(?:\.|$)",
            r"(?:Decision\s+\d+):\s*(.+?)(?:\.|$)",
            r"(?:commit|push|merged)\s+(.+?)(?:\.|$)",
        ]
        for pattern in decision_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE | re.MULTILINE)
            for m in matches[:3]:  # cap at 3 per pattern
                events.append(f"Decision: {m.strip()}")

        # Detect file changes
        file_patterns = [
            r"(?:created|wrote|built|implemented|fixed)\s+(.+?\.py)",
            r"(?:modified|edited|updated)\s+(.+?\.md)",
        ]
        for pattern in file_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for m in matches[:3]:
                events.append(f"File: {m.strip()}")

        # Detect errors and fixes
        error_patterns = [
            r"(?:bug|error|crash|failed)\s+(.+?)(?:\.|$)",
            r"(?:fixed|resolved|patched)\s+(.+?)(?:\.|$)",
        ]
        for pattern in error_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for m in matches[:2]:
                events.append(f"Error/Fix: {m.strip()}")

        # Cap total events
        if not events:
            events = ["Session completed with no significant events detected"]

        narrative = f"Session with {entity_name}: " + "; ".join(events[:10])

        return DistillationEntry(
            level="L1",
            content=narrative,
            source_trace_id=trace_id,
            source_entity=entity_name,
        )

    def _distill_insight(
        self,
        narrative: str,
        entity_name: str,
        trace_id: Optional[str],
    ) -> DistillationEntry:
        """L2 (Insight): What does this mean?

        Distills the narrative into patterns and implications.
        Looks for repeated themes, recurring decisions, and causal chains.
        """
        insights = []

        # Detect pattern: decisions about architecture
        if "architect" in narrative.lower() or "design" in narrative.lower():
            insights.append("Architecture decisions were made this session — verify alignment with PIVOT_LOG.md")

        # Detect pattern: bug fixes
        fix_count = narrative.lower().count("fix")
        if fix_count > 1:
            insights.append(f"Multiple fixes ({fix_count}) suggest the area needs additional testing or review")

        # Detect pattern: new modules
        if "built" in narrative.lower() or "implemented" in narrative.lower():
            insights.append("New code was added — check if tests cover the new functionality")

        # Detect pattern: heritage work
        if "heritage" in narrative.lower() or "id-soft" in narrative.lower():
            insights.append("Heritage work was done — verify CREDITS.md alignment")

        # Detect pattern: coordination
        if "maat" in narrative.lower() or "coordination" in narrative.lower():
            insights.append("Multi-agent coordination occurred — verify workspace locks are clean")

        if not insights:
            insights.append("Session completed — review narrative for deeper patterns")

        insight_text = f"After {entity_name} session: " + "; ".join(insights[:5])

        return DistillationEntry(
            level="L2",
            content=insight_text,
            source_trace_id=trace_id,
            source_entity=entity_name,
        )

    def _extract_principle(
        self,
        insight: str,
        entity_name: str,
        trace_id: Optional[str],
    ) -> DistillationEntry:
        """L3 (Principle): What is the timeless truth?

        Extracts universal principles from the insight.
        These are the enduring lessons that survive context compression.
        """
        principles = []

        # Universal principle: coordination reduces conflicts
        if "coordination" in insight.lower() or "workspace lock" in insight.lower():
            principles.append("Coordination protocols prevent conflicts — workspace locks and live feeds are not overhead, they are infrastructure")

        # Universal principle: multiple fixes signal design issues
        if "multiple fixes" in insight.lower():
            principles.append("Multiple fixes in the same area signal a design issue, not a series of bugs — look for the root cause")

        # Universal principle: heritage is debt that compounds
        if "heritage" in insight.lower():
            principles.append("Heritage attribution is debt that compounds — every undocumented pattern becomes a mystery for the next agent")

        # Universal principle: new code needs tests
        if "new code" in insight.lower() or "new functionality" in insight.lower():
            principles.append("Code without tests is technical debt — the test suite is the contract between agents")

        if not principles:
            principles.append("Every session produces knowledge — the question is whether we capture it before context compression")

        principle_text = "; ".join(principles[:3])

        return DistillationEntry(
            level="L3",
            content=principle_text,
            source_trace_id=trace_id,
            source_entity=entity_name,
        )

    # ── Soul YAML Operations ───────────────────────────────────────────

    def read_soul(self, entity_name: str) -> Optional[str]:
        """Read an entity's soul.yaml content via USM.
        
        Sovereign state is addressed by key 'soul:{entity_name}'.
        """
        usm = get_usm()
        content = usm.load_state(f"soul:{entity_name}")
        if content is None:
            logger.warning("Soul not found for entity %s", entity_name)
            return None
        
        return content if isinstance(content, str) else json.dumps(content)
    
    async def append_to_soul(
        self,
        entity_name: str,
        entries: Dict[AbstractionLevel, DistillationEntry],
        section: str = "proposals",
    ) -> bool:
        """Append distillation entries to an entity's proposed_lessons via USM.
        
        Sovereign state is addressed by key 'proposed_lessons:{entity_name}'.
        """
        usm = get_usm()
        state_key = f"proposed_lessons:{entity_name}"
        
        # 1. Load existing content or create template
        content = await usm.load_state(state_key)
        if content is None:
            logger.warning("No proposed_lessons for %s — creating from template", entity_name)
            content = (
                f"# Proposed Lessons for {entity_name}\n"
                f"# Auto-generated by SoulDistiller on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"# Review with Staging Gate before approving into soul.yaml\n"
                f"{section}:\n"
            )
        elif not isinstance(content, str):
            content = json.dumps(content)
            
        # 2. Build the new entries block
        new_lines = []
        new_lines.append(f"  # Auto-distilled {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        for level in ["L1", "L2", "L3"]:
            entry = entries.get(level)
            if entry:
                new_lines.append(entry.to_yaml_block(indent=4))
        
        new_block = "\n".join(new_lines) + "\n"
        
        # 3. Append to existing section
        section_pattern = re.compile(
            rf"(^  {re.escape(section)}:\s*\n)",
            re.MULTILINE,
        )
        match = section_pattern.search(content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + new_block + content[insert_pos:]
        else:
            content += f"\n  {section}:\n" + new_block
            
        # 4. Save back to USM
        try:
            await usm.save_state(state_key, content)
            logger.info("Proposed lessons updated via USM: %s (%s)", entity_name, section)
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Failed to save proposed lessons to USM for %s: %s", entity_name, e)
            return False


    async def distill_and_save(
        self,
        session_transcript: str,
        entity_name: str,
        source_trace_id: Optional[str] = None,
        section: str = "proposals",
    ) -> bool:
        """Full pipeline: distill session → append to proposed_lessons.yaml.
        
        This is the main entry point for auto-distillation on session end.
        Writes to proposed_lessons.yaml for Staging Gate review — lessons
        must be human-approved before they enter the permanent soul record.
        
        See SOUL_ARCHITECTURE_PROTOCOL.md v6.1 for the full protocol.
        """
        logger.info("Distilling session for %s...", entity_name)
        
        entries = self.distill_session(
            session_transcript,
            entity_name,
            source_trace_id,
        )
        
        # Log what we distilled
        for level, entry in entries.items():
            logger.info(
                "%s [%s]: %s",
                entity_name,
                level,
                entry.content[:100] + "..." if len(entry.content) > 100 else entry.content,
            )
        
        # Save to proposed_lessons.yaml (NOT soul.yaml — Staging Gate pattern)
        success = await self.append_to_soul(entity_name, entries, section)
        
        if success:
            logger.info("Distillation complete for %s — saved to proposed_lessons.yaml", entity_name)
        else:
            logger.error("Distillation failed for %s — could not write proposed_lessons.yaml", entity_name)
        
        return success


    # ── Batch Operations ───────────────────────────────────────────────

    def summarize_session(
        self,
        session_transcript: str,
        entity_name: str,
    ) -> str:
        """Create a concise summary of a session for somatic re-hydration.
        
        This is a lightweight version of the distillation pipeline that
        returns a narrative summary instead of formal L1/L2/L3 entries.
        """
        # Use the L1 narrative extraction as the base summary
        entry = self._extract_narrative(session_transcript, entity_name, None)
        return entry.content


# ── Singleton ────────────────────────────────────────────────────────────

_distiller: Optional[SoulDistiller] = None

def get_distiller(entities_dir: Optional[str] = None) -> SoulDistiller:
    """Get or create the singleton distiller."""
    global _distiller
    if _distiller is None:
        # Use provided dir, or fallback to DATA_DIR / "entities"
        final_dir = entities_dir or str(Path(observability.DATA_DIR) / "entities")
        _distiller = SoulDistiller(final_dir)
    return _distiller
