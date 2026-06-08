# AP Token: AP-ORACLE-RESTORE-v2.3.0
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

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

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
        """Read an entity's soul.yaml content."""
        soul_path = self._entities_dir / entity_name / "soul.yaml"
        if not soul_path.exists():
            logger.warning("Soul not found: %s", soul_path)
            return None
        return soul_path.read_text()

    def append_to_soul(
        self,
        entity_name: str,
        entries: Dict[AbstractionLevel, DistillationEntry],
        section: str = "embodied_experiences",
    ) -> bool:
        """Append distillation entries to an entity's soul.yaml.

        Appends to the specified section (default: embodied_experiences).
        Creates the section if it doesn't exist.
        """
        soul_path = self._entities_dir / entity_name / "soul.yaml"
        if not soul_path.exists():
            logger.error("Cannot append — soul not found: %s", soul_path)
            return False

        content = soul_path.read_text()

        # Build the new entries block
        new_lines = []
        new_lines.append(f"  # Auto-distilled {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        for level in ["L1", "L2", "L3"]:
            entry = entries.get(level)
            if entry:
                new_lines.append(entry.to_yaml_block(indent=4))

        new_block = "\n".join(new_lines) + "\n"

        # Try to append to existing section
        section_pattern = re.compile(
            rf"(^  {re.escape(section)}:\s*\n)",
            re.MULTILINE,
        )
        match = section_pattern.search(content)
        if match:
            # Insert after the section header
            insert_pos = match.end()
            content = content[:insert_pos] + new_block + content[insert_pos:]
        else:
            # Section doesn't exist — append at end
            content += f"\n  {section}:\n" + new_block

        soul_path.write_text(content)
        logger.info("Soul updated: %s (%s)", entity_name, section)
        return True

    def distill_and_save(
        self,
        session_transcript: str,
        entity_name: str,
        source_trace_id: Optional[str] = None,
        section: str = "embodied_experiences",
    ) -> bool:
        """Full pipeline: distill session → append to soul.yaml.

        This is the main entry point for auto-distillation on session end.
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

        # Save to soul.yaml
        success = self.append_to_soul(entity_name, entries, section)

        if success:
            logger.info("Distillation complete for %s — saved to soul.yaml", entity_name)
        else:
            logger.error("Distillation failed for %s — could not write soul.yaml", entity_name)

        return success

    # ── Batch Operations ───────────────────────────────────────────────

    def distill_all_entities(
        self,
        session_transcript: str,
        source_trace_id: Optional[str] = None,
    ) -> Dict[str, bool]:
        """Distill a session for all entities mentioned in the transcript.

        Returns dict of entity_name → success.
        """
        results = {}
        # Find all entity mentions in the transcript
        entity_mentions = re.findall(
            r"(?:entity|agent|from|to):\s*([A-Za-z_]+)",
            session_transcript,
            re.IGNORECASE,
        )
        unique_entities = set(entity_mentions)

        for entity in unique_entities:
            entity_dir = self._entities_dir / entity
            if entity_dir.exists() and (entity_dir / "soul.yaml").exists():
                results[entity] = self.distill_and_save(
                    session_transcript,
                    entity,
                    source_trace_id,
                )

        return results


# ── Singleton ────────────────────────────────────────────────────────────

_distiller: Optional[SoulDistiller] = None


def get_distiller(entities_dir: str = "data/entities") -> SoulDistiller:
    """Get or create the singleton distiller."""
    global _distiller
    if _distiller is None:
        _distiller = SoulDistiller(entities_dir)
    return _distiller
