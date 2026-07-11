# 🔱 omega-vetala — YAML Policy Loader
# ⬡ OMEGA ⬡ P10-VALIDATION ⬡ POLICY-LOADER
#
# AP Token: AP-MODERATION-P10-v1.0.0
# [Worse is Better: Gabriel 1991] — YAML config is simpler than a DSL
#
"""YAML-based policy configuration loader.

Policies are defined as YAML files, enabling non-developers to tune
moderation behaviour without code changes.

Example YAML::

    # config/policies/standard.yaml
    name: standard
    description: Standard moderation policy
    rules:
      - name: block_high_confidence
        description: Block high-confidence flagged content
        action: block
        min_confidence: 0.9
        require_flagged: true

      - name: warn_medium
        description: Warn on medium-confidence flagged content
        action: warn
        min_confidence: 0.5
        require_flagged: true

      - name: allow_clean
        description: Allow everything else
        action: allow
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from omega_vetala.policies.policy import (
    Action,
    ModerationPolicy,
    PolicyRule,
)


class PolicyLoadError(Exception):
    """Raised when a policy file cannot be loaded or parsed."""


class PolicyLoader:
    """Load and cache :class:`ModerationPolicy` instances from YAML files.

    Usage::

        loader = PolicyLoader()
        policy = loader.load("config/policies/standard.yaml")
        policy = loader.load("config/policies/standard.yaml")  # cached

    Args:
        cache: If ``True`` (default), cache loaded policies in memory.
    """

    def __init__(self, cache: bool = True) -> None:
        self._cache: dict[str, ModerationPolicy] = {}
        self._use_cache = cache

    def load(self, path: str) -> ModerationPolicy:
        """Load a policy from a YAML file.

        Args:
            path: Filesystem path to the YAML policy file.

        Returns:
            A parsed :class:`ModerationPolicy`.

        Raises:
            PolicyLoadError: If the file cannot be read or parsed.
            FileNotFoundError: If the file does not exist.
        """
        if self._use_cache and path in self._cache:
            return self._cache[path]

        with open(path) as fh:
            raw: dict[str, Any] = yaml.safe_load(fh)

        if not isinstance(raw, dict):
            raise PolicyLoadError(
                f"Expected a YAML mapping in {path}, got {type(raw).__name__}"
            )

        try:
            policy = self._parse(raw)
        except (KeyError, ValueError, TypeError) as exc:
            raise PolicyLoadError(
                f"Failed to parse policy {path}: {exc}"
            ) from exc

        if self._use_cache:
            self._cache[path] = policy

        return policy

    def load_from_string(self, yaml_str: str) -> ModerationPolicy:
        """Load a policy from a YAML string (useful for testing).

        Args:
            yaml_str: YAML content as a string.

        Returns:
            A parsed :class:`ModerationPolicy`.

        Raises:
            PolicyLoadError: If the YAML cannot be parsed.
        """
        raw: dict[str, Any] = yaml.safe_load(yaml_str)
        if not isinstance(raw, dict):
            raise PolicyLoadError(
                f"Expected a YAML mapping, got {type(raw).__name__}"
            )
        try:
            return self._parse(raw)
        except (KeyError, ValueError, TypeError) as exc:
            raise PolicyLoadError(
                f"Failed to parse policy string: {exc}"
            ) from exc

    def clear_cache(self) -> None:
        """Clear the in-memory policy cache."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(raw: dict[str, Any]) -> ModerationPolicy:
        """Parse a raw dict into a :class:`ModerationPolicy`.

        Args:
            raw: Parsed YAML content.

        Returns:
            A validated :class:`ModerationPolicy`.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        name = raw["name"]
        description = raw.get("description", "")
        rules_raw: list[dict[str, Any]] = raw.get("rules", [])

        rules: list[PolicyRule] = []
        for entry in rules_raw:
            action_str = entry.get("action", "allow").lower()
            try:
                action = Action(action_str)
            except ValueError:
                raise ValueError(
                    f"Unknown action '{action_str}' in rule '{entry.get('name', '?')}'"
                )

            rule = PolicyRule(
                name=entry.get("name", ""),
                description=entry.get("description", ""),
                action=action,
                min_confidence=float(entry.get("min_confidence", 0.0)),
                max_confidence=float(entry.get("max_confidence", 1.0)),
                require_flagged=bool(entry.get("require_flagged", False)),
                category=entry.get("category", ""),
                category_min_score=float(entry.get("category_min_score", 0.0)),
            )
            rules.append(rule)

        return ModerationPolicy(
            name=name,
            description=description,
            rules=rules,
        )

    def list_cache(self) -> dict[str, str]:
        """Return cached policy names keyed by file path."""
        return {k: v.name for k, v in self._cache.items()}
