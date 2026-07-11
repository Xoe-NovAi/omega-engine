# 🔱 omega-vetala — Policy Data Types
# ⬡ OMEGA ⬡ P10-VALIDATION ⬡ POLICY-TYPES
#
# AP Token: AP-MODERATION-P10-v1.0.0
"""Core policy types for moderation threshold configuration.

Defines the :class:`ModerationPolicy`, :class:`PolicyRule`, and
:class:`Action` types used to configure how the moderation system
responds to provider results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Action — what to do when a rule matches
# ---------------------------------------------------------------------------


class Action(str, Enum):
    """Moderation action to take when a policy rule fires."""

    ALLOW = "allow"
    """Content is allowed through without restriction."""

    WARN = "warn"
    """Content is allowed but the user receives a warning."""

    BLOCK = "block"
    """Content is blocked from being published."""

    REVIEW = "review"
    """Content is held for human review."""

    LOG_ONLY = "log_only"
    """Content is allowed but the event is logged for analysis."""


# ---------------------------------------------------------------------------
# PolicyRule — a single threshold rule
# ---------------------------------------------------------------------------


@dataclass
class PolicyRule:
    """A single threshold-based moderation rule.

    Rules are evaluated in order.  The first matching rule determines
    the action taken.  Rules can match on flag status, minimum confidence,
    and/or specific category scores.

    Attributes:
        name: Human-readable rule identifier.
        description: Explanation of what this rule detects.
        action: The :class:`Action` to take when this rule matches.
        min_confidence: Minimum confidence threshold (0.0–1.0).
        require_flagged: If ``True``, the result must be flagged.
        max_confidence: Maximum confidence threshold (0.0–1.0).
            Useful for catch-all rules that match low-confidence results.
        category: Optional category name to match (e.g. ``toxicity``).
        category_min_score: Minimum score for the specified category.
    """

    name: str = ""
    description: str = ""
    action: Action = Action.ALLOW
    min_confidence: float = 0.0
    require_flagged: bool = False
    max_confidence: float = 1.0
    category: str = ""
    category_min_score: float = 0.0


# ---------------------------------------------------------------------------
# ModerationPolicy — a collection of rules
# ---------------------------------------------------------------------------


@dataclass
class ModerationPolicy:
    """A complete moderation policy with ordered rules.

    Usage::

        policy = ModerationPolicy(
            name="standard",
            rules=[
                PolicyRule(
                    name="block_hate",
                    action=Action.BLOCK,
                    min_confidence=0.9,
                    require_flagged=True,
                ),
                PolicyRule(
                    name="warn_medium",
                    action=Action.WARN,
                    min_confidence=0.5,
                    require_flagged=True,
                ),
                PolicyRule(
                    name="allow_clean",
                    action=Action.ALLOW,
                ),
            ],
        )

    Attributes:
        name: Policy name (e.g. ``standard``, ``strict``, ``relaxed``).
        description: Human-readable description.
        rules: Ordered list of :class:`PolicyRule` instances.
            Evaluated top-to-bottom; first match wins.
    """

    name: str = ""
    description: str = ""
    rules: list[PolicyRule] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


def resolve_action(
    is_flagged: bool,
    confidence: float,
    categories: dict[str, float] | None = None,
    policy: ModerationPolicy | None = None,
) -> Action:
    """Resolve the action for a moderation result against a policy.

    Iterates through the policy's rules in order and returns the action
    for the **first** matching rule.  If no rule matches, returns
    ``Action.ALLOW`` as the safe default.

    Args:
        is_flagged: Whether the provider flagged the content.
        confidence: Confidence score (0.0–1.0).
        categories: Per-category scores (optional).
        policy: The :class:`ModerationPolicy` to evaluate against.
            If ``None``, returns ``Action.ALLOW``.

    Returns:
        The :class:`Action` determined by the first matching rule.
    """
    if policy is None:
        return Action.ALLOW

    categories = categories or {}

    for rule in policy.rules:
        # Check flag requirement
        if rule.require_flagged and not is_flagged:
            continue

        # Check confidence range
        if confidence < rule.min_confidence:
            continue
        if confidence > rule.max_confidence:
            continue

        # Check category-specific threshold
        if rule.category:
            cat_score = categories.get(rule.category, 0.0)
            if cat_score < rule.category_min_score:
                continue

        # All conditions met
        return rule.action

    # Safe default
    return Action.ALLOW
