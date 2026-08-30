# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
CPE Scorer — Cumulative PII Exposure Scoring
AP: AP-CPE-SCORER-v1.0.0
⬡ OMEGA ⬡ P3 ⬡ cpe_scorer ⬡ CAMP-INSPIRED

Implements R19 Soul Privacy Model Part 2.2:
CAMP-Inspired Cumulative PII Exposure (CPE) Scoring

Adapted from Panjwani et al. (2026) — arXiv:2604.16521
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

# Optional: Faker for pseudonymization
try:
    from faker import Faker

    _HAS_FAKER = True
except ImportError:
    _HAS_FAKER = False


class CPEAction(Enum):
    """Action to take based on CPE score."""

    PASS = "pass"  # CPE < MODERATE threshold — send original
    WARN = "warn"  # CPE >= MODERATE — log but allow
    PSEUDONYMIZE = "pseudonymize"  # CPE >= HIGH — rewrite history
    BLOCK = "block"  # CPE >= CRITICAL — hard stop


@dataclass
class PIIEntity:
    """Represents a detected PII entity."""

    value: str
    type: str
    turn: int
    span: Tuple[int, int]  # (start, end) character positions
    confidence: float = 1.0


@dataclass
class CPEResult:
    """Result of CPE processing for a turn."""

    action: CPEAction
    cpe_score: float
    entities_detected: List[PIIEntity]
    pseudonymized_text: Optional[str] = None
    warning_message: Optional[str] = None


class CPESession:
    """
    Tracks cumulative PII exposure across conversation turns.

    Implements CAMP (Cumulative PII Exposure) scoring from Panjwani et al. (2026):
    CPE = Σ(entity_weight * count) + α * Σ(edge_weight * cooccurrence_boost)
    """

    # Entity type weights (from CAMP paper, adapted for Omega)
    ENTITY_WEIGHTS = {
        "PERSON": 0.3,
        "LOCATION": 0.2,
        "ORGANIZATION": 0.25,
        "FINANCIAL": 0.5,
        "MEDICAL": 0.6,
        "CREDENTIAL": 0.8,
        "CONTACT": 0.25,
        "IDENTITY": 0.4,
        "EMAIL": 0.35,
        "PHONE": 0.3,
        "SSN": 0.7,
        "CREDIT_CARD": 0.75,
        "API_KEY": 0.8,
        "PASSWORD": 0.85,
        "PRIVATE_KEY": 0.9,
    }

    # Co-occurrence boosts (when two entity types appear in same turn)
    COOCCURRENCE_BOOST = {
        ("PERSON", "FINANCIAL"): 0.4,
        ("PERSON", "MEDICAL"): 0.5,
        ("PERSON", "CREDENTIAL"): 0.45,
        ("PERSON", "IDENTITY"): 0.35,
        ("LOCATION", "IDENTITY"): 0.3,
        ("LOCATION", "MEDICAL"): 0.4,
        ("ORGANIZATION", "CREDENTIAL"): 0.45,
        ("ORGANIZATION", "FINANCIAL"): 0.4,
        ("EMAIL", "PASSWORD"): 0.5,
        ("API_KEY", "ORGANIZATION"): 0.4,
        ("PRIVATE_KEY", "CREDENTIAL"): 0.5,
    }

    # Thresholds for action decisions
    THRESHOLDS = {
        "LOW": 1.0,  # Pass — send original
        "MODERATE": 2.0,  # Warn — log but allow
        "HIGH": 3.0,  # Pseudonymize — rewrite history
        "CRITICAL": 4.0,  # Block — hard stop
    }

    def __init__(
        self,
        threshold: float = 2.0,
        alpha: float = 0.3,
        custom_weights: Optional[Dict[str, float]] = None,
        custom_boosts: Optional[Dict[Tuple[str, str], float]] = None,
        custom_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize CPE session.

        Args:
            threshold: Base threshold for MODERATE (default 2.0)
            alpha: Graph amplifier for co-occurrence (default 0.3)
            custom_weights: Override entity weights
            custom_boosts: Override co-occurrence boosts
            custom_thresholds: Override thresholds
        """
        self.threshold = threshold
        self.alpha = alpha

        self.entity_weights = {**self.ENTITY_WEIGHTS, **(custom_weights or {})}
        self.cooccurrence_boost = {**self.COOCCURRENCE_BOOST, **(custom_boosts or {})}
        self.thresholds = {**self.THRESHOLDS, **(custom_thresholds or {})}

        # Registry of detected entities by type
        self.registry: Dict[str, List[PIIEntity]] = defaultdict(list)

        # Co-occurrence graph
        self.cooccurrence_graph: nx.Graph = nx.Graph()

        # Pseudonymization map for consistent replacement
        self.pseudonym_map: Dict[str, str] = {}

        # Turn counter
        self.turn_count = 0

        # History for pseudonymization
        self.history: List[Dict[str, Any]] = []

    def _extract_pii(self, text: str) -> List[PIIEntity]:
        """
        Extract PII entities from text using regex patterns.

        In production, this would use Presidio or similar NER.
        This is a simplified implementation for demonstration.
        """
        entities = []

        # Define regex patterns for common PII types
        patterns = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "API_KEY": r"\b(?:sk|pk|api)[_-]?[A-Za-z0-9]{20,}\b",
            "PASSWORD": r"(?i)(?:password|passwd|pwd)\s*[:=]\s*\S+",
            "PRIVATE_KEY": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
            "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "URL_WITH_AUTH": r"https?://[^:\s]+:[^@\s]+@[^\s]+",
        }

        for pii_type, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(
                    PIIEntity(
                        value=match.group(),
                        type=pii_type,
                        turn=self.turn_count,
                        span=(match.start(), match.end()),
                    )
                )

        # Named entity patterns (simplified - would use spaCy/Presidio in production)
        # PERSON names (capitalized words)
        person_pattern = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
        for match in re.finditer(person_pattern, text):
            # Avoid matching common false positives
            matched = match.group()
            if not any(word in matched for word in ["The ", "This ", "That ", "These ", "Those "]):
                entities.append(
                    PIIEntity(
                        value=matched,
                        type="PERSON",
                        turn=self.turn_count,
                        span=(match.start(), match.end()),
                        confidence=0.7,
                    )
                )

        # Financial amounts
        financial_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"
        for match in re.finditer(financial_pattern, text):
            entities.append(
                PIIEntity(
                    value=match.group(),
                    type="FINANCIAL",
                    turn=self.turn_count,
                    span=(match.start(), match.end()),
                )
            )

        return entities

    def _compute_cpe(self) -> float:
        """
        Compute CPE score.

        CPE = Σ(entity_weight * count) + α * Σ(edge_weight * cooccurrence_boost)
        """
        # Base score: sum of entity weights * counts
        base = sum(self.entity_weights.get(t, 0.1) * len(ents) for t, ents in self.registry.items())

        # Graph boost: sum of co-occurrence boosts * edge weights
        graph_boost = 0.0
        for u, v, data in self.cooccurrence_graph.edges(data=True):
            boost = self.cooccurrence_boost.get((u, v)) or self.cooccurrence_boost.get((v, u), 0)
            weight = data.get("weight", 1)
            graph_boost += boost * weight

        return base + self.alpha * graph_boost

    def _decide_action(self, cpe: float) -> CPEAction:
        """Decide action based on CPE score."""
        if cpe >= self.thresholds["CRITICAL"]:
            return CPEAction.BLOCK
        elif cpe >= self.thresholds["HIGH"]:
            return CPEAction.PSEUDONYMIZE
        elif cpe >= self.thresholds["MODERATE"]:
            return CPEAction.WARN
        return CPEAction.PASS

    def _generate_pseudonym(self, entity: PIIEntity) -> str:
        """Generate consistent pseudonym for an entity value."""
        if entity.value in self.pseudonym_map:
            return self.pseudonym_map[entity.value]

        if not _HAS_FAKER:
            # Fallback without Faker
            fake_val = f"<<{entity.type}_{len(self.pseudonym_map)}>>"
        else:
            fake = Faker()
            if entity.type == "PERSON":
                fake_val = fake.name()
            elif entity.type == "LOCATION":
                fake_val = fake.city()
            elif entity.type == "ORGANIZATION":
                fake_val = fake.company()
            elif entity.type == "FINANCIAL":
                fake_val = f"${fake.random_int(1000, 100000)}"
            elif entity.type == "EMAIL":
                fake_val = fake.email()
            elif entity.type == "PHONE":
                fake_val = fake.phone_number()
            elif entity.type == "SSN":
                fake_val = f"{fake.random_int(100, 999)}-{fake.random_int(10, 99)}-{fake.random_int(1000, 9999)}"
            elif entity.type == "CREDIT_CARD":
                fake_val = " ".join(str(fake.random_int(1000, 9999)) for _ in range(4))
            elif entity.type in ("API_KEY", "PASSWORD", "PRIVATE_KEY"):
                fake_val = f"<<{entity.type}_{len(self.pseudonym_map)}>>"
            else:
                fake_val = f"<<{entity.type}_{len(self.pseudonym_map)}>>"

        self.pseudonym_map[entity.value] = fake_val
        return fake_val

    def process_turn(self, text: str) -> CPEResult:
        """
        Process a conversation turn: extract PII, update CPE, decide action.

        Args:
            text: The turn text to process

        Returns:
            CPEResult with action, score, and pseudonymized text if applicable
        """
        self.turn_count += 1

        # Extract PII entities
        entities = self._extract_pii(text)

        # Update registry
        for ent in entities:
            self.registry[ent.type].append(ent)
            self.cooccurrence_graph.add_node(ent.type)

        # Add co-occurrence edges
        types_in_turn = {e.type for e in entities}
        for t1 in types_in_turn:
            for t2 in types_in_turn:
                if t1 != t2:
                    if self.cooccurrence_graph.has_edge(t1, t2):
                        self.cooccurrence_graph[t1][t2]["weight"] += 1
                    else:
                        self.cooccurrence_graph.add_edge(t1, t2, weight=1)

        # Compute CPE
        cpe = self._compute_cpe()

        # Decide action
        action = self._decide_action(cpe)

        # Handle pseudonymization if needed
        pseudonymized_text = None
        warning_message = None

        if action == CPEAction.PSEUDONYMIZE:
            pseudonymized_text = self._pseudonymize_text(text, entities)
        elif action == CPEAction.WARN:
            warning_message = (
                f"CPE score {cpe:.2f} exceeds MODERATE threshold ({self.thresholds['MODERATE']})"
            )
        elif action == CPEAction.BLOCK:
            warning_message = f"CPE score {cpe:.2f} exceeds CRITICAL threshold ({self.thresholds['CRITICAL']}) — BLOCKED"

        # Store in history
        self.history.append(
            {
                "turn": self.turn_count,
                "original_text": text,
                "entities": [{"value": e.value, "type": e.type, "span": e.span} for e in entities],
                "cpe_score": cpe,
                "action": action.value,
                "pseudonymized_text": pseudonymized_text,
            }
        )

        return CPEResult(
            action=action,
            cpe_score=cpe,
            entities_detected=entities,
            pseudonymized_text=pseudonymized_text,
            warning_message=warning_message,
        )

    def _pseudonymize_text(self, text: str, entities: List[PIIEntity]) -> str:
        """Replace PII entities with pseudonyms in text."""
        # Sort by span start descending to avoid index shifting
        sorted_entities = sorted(entities, key=lambda e: e.span[0], reverse=True)

        result = text
        for ent in sorted_entities:
            pseudonym = self._generate_pseudonym(ent)
            start, end = ent.span
            result = result[:start] + pseudonym + result[end:]

        return result

    def pseudonymize_history(self) -> List[Dict[str, Any]]:
        """
        Retroactively pseudonymize entire conversation history.

        Returns:
            List of turns with pseudonymized text
        """
        rewritten = []

        for turn in self.history:
            original = turn["original_text"]
            rewritten_text = original

            for ent_data in turn["entities"]:
                real_value = ent_data["value"]
                if real_value in self.pseudonym_map:
                    fake_value = self.pseudonym_map[real_value]
                    rewritten_text = rewritten_text.replace(real_value, fake_value)

            rewritten.append(
                {
                    "turn": turn["turn"],
                    "text": rewritten_text,
                    "role": turn.get("role", "user"),
                    "cpe_score": turn["cpe_score"],
                }
            )

        return rewritten

    def demask_response(self, response: str) -> str:
        """
        Restore original values in LLM response before showing user.

        Args:
            response: LLM response with pseudonyms

        Returns:
            Response with original values restored
        """
        result = response
        for real, fake in self.pseudonym_map.items():
            result = result.replace(fake, real)
        return result

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of CPE session."""
        return {
            "turns_processed": self.turn_count,
            "entity_counts": {t: len(e) for t, e in self.registry.items()},
            "current_cpe": self._compute_cpe(),
            "thresholds": self.thresholds,
            "pseudonym_map_size": len(self.pseudonym_map),
            "cooccurrence_edges": list(self.cooccurrence_graph.edges(data=True)),
        }

    def reset(self) -> None:
        """Reset session state."""
        self.registry.clear()
        self.cooccurrence_graph.clear()
        self.pseudonym_map.clear()
        self.history.clear()
        self.turn_count = 0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_cpe_session(threshold: float = 2.0, alpha: float = 0.3, **kwargs) -> CPESession:
    """Factory: create a CPE session with default or custom config."""
    return CPESession(threshold=threshold, alpha=alpha, **kwargs)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CPESession",
    "CPEAction",
    "PIIEntity",
    "CPEResult",
    "create_cpe_session",
]
