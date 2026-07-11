"""Policy tests — YAML loading, threshold config, action mapping.

Tests the :class:`ModerationPolicy`, :class:`PolicyRule`, and
:class:`PolicyLoader` classes.

All rules use confidence/flag-based thresholds — NO static slur lists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from omega_vetala.policies.loader import PolicyLoader, PolicyLoadError
from omega_vetala.policies.policy import (
    Action,
    ModerationPolicy,
    PolicyRule,
    resolve_action,
)


class TestActionEnum:
    """Action enumeration values."""

    def test_action_values(self) -> None:
        """Actions should have correct string values."""
        assert Action.ALLOW.value == "allow"
        assert Action.WARN.value == "warn"
        assert Action.BLOCK.value == "block"
        assert Action.REVIEW.value == "review"
        assert Action.LOG_ONLY.value == "log_only"

    def test_action_from_string(self) -> None:
        """Actions should be constructable from string."""
        assert Action("allow") == Action.ALLOW
        assert Action("block") == Action.BLOCK

    def test_invalid_action_raises(self) -> None:
        """Invalid action string should raise ValueError."""
        with pytest.raises(ValueError):
            Action("nonexistent_action")


class TestPolicyRule:
    """PolicyRule dataclass behaviour."""

    def test_default_values(self) -> None:
        """Default rule should allow everything."""
        rule = PolicyRule()
        assert rule.action == Action.ALLOW
        assert rule.min_confidence == 0.0
        assert rule.max_confidence == 1.0
        assert rule.require_flagged is False

    def test_rule_with_all_fields(self) -> None:
        """Rule with explicit fields."""
        rule = PolicyRule(
            name="test_rule",
            description="A test rule",
            action=Action.BLOCK,
            min_confidence=0.8,
            max_confidence=1.0,
            require_flagged=True,
            category="toxicity",
            category_min_score=0.7,
        )
        assert rule.name == "test_rule"
        assert rule.action == Action.BLOCK
        assert rule.min_confidence == 0.8
        assert rule.category == "toxicity"

    def test_rule_allow_all_defaults(self) -> None:
        """Rule with no conditions should match everything."""
        rule = PolicyRule()
        assert rule.require_flagged is False
        assert rule.min_confidence == 0.0
        assert rule.max_confidence == 1.0


class TestModerationPolicy:
    """ModerationPolicy collection behaviour."""

    def test_empty_policy(self) -> None:
        """Empty policy should have no rules."""
        policy = ModerationPolicy(name="empty")
        assert policy.name == "empty"
        assert len(policy.rules) == 0

    def test_policy_with_rules(self) -> None:
        """Policy with rules should iterate correctly."""
        policy = ModerationPolicy(
            name="test",
            rules=[
                PolicyRule(name="rule1", action=Action.BLOCK),
                PolicyRule(name="rule2", action=Action.WARN),
            ],
        )
        assert len(policy.rules) == 2
        assert policy.rules[0].name == "rule1"

    def test_policy_rules_ordered(self) -> None:
        """Rules should maintain insertion order (first match wins)."""
        policy = ModerationPolicy(
            name="ordered",
            rules=[
                PolicyRule(name="first", action=Action.BLOCK),
                PolicyRule(name="second", action=Action.WARN),
            ],
        )
        names = [r.name for r in policy.rules]
        assert names == ["first", "second"]


class TestResolveAction:
    """Policy action resolution from moderation results."""

    def test_no_policy_returns_allow(self) -> None:
        """Without a policy, always return ALLOW."""
        assert resolve_action(True, 0.95) == Action.ALLOW

    def test_block_high_confidence(self, sample_standard_policy: ModerationPolicy) -> None:
        """High-confidence flagged content should be BLOCK."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.95,
            policy=sample_standard_policy,
        )
        assert action == Action.BLOCK

    def test_warn_medium_confidence(
        self, sample_standard_policy: ModerationPolicy
    ) -> None:
        """Medium-confidence flagged content should be WARN."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.6,
            policy=sample_standard_policy,
        )
        assert action == Action.WARN

    def test_review_low_confidence(
        self, sample_standard_policy: ModerationPolicy
    ) -> None:
        """Low-confidence flagged content should be REVIEW."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.35,
            policy=sample_standard_policy,
        )
        assert action == Action.REVIEW

    def test_log_very_low(
        self, sample_standard_policy: ModerationPolicy
    ) -> None:
        """Very low-confidence flagged content should be LOG_ONLY."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.15,
            policy=sample_standard_policy,
        )
        assert action == Action.LOG_ONLY

    def test_allow_clean(self, sample_standard_policy: ModerationPolicy) -> None:
        """Non-flagged content should be ALLOW."""
        action = resolve_action(
            is_flagged=False,
            confidence=0.05,
            policy=sample_standard_policy,
        )
        assert action == Action.ALLOW

    def test_strict_policy_block_everything(
        self, sample_strict_policy: ModerationPolicy
    ) -> None:
        """Strict policy blocks flagged content at lower threshold."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.5,
            policy=sample_strict_policy,
        )
        assert action == Action.BLOCK

    def test_relaxed_policy_allows_more(
        self, sample_relaxed_policy: ModerationPolicy
    ) -> None:
        """Relaxed policy allows flagged content below high threshold."""
        action = resolve_action(
            is_flagged=True,
            confidence=0.85,
            policy=sample_relaxed_policy,
        )
        assert action == Action.WARN  # Below 0.95 block threshold

    def test_category_specific_threshold(self) -> None:
        """Category-specific thresholds should work."""
        policy = ModerationPolicy(
            name="cat_test",
            rules=[
                PolicyRule(
                    name="toxicity_block",
                    action=Action.BLOCK,
                    min_confidence=0.5,
                    require_flagged=True,
                    category="toxicity",
                    category_min_score=0.9,
                ),
                PolicyRule(
                    name="catch_all",
                    action=Action.WARN,
                    min_confidence=0.5,
                    require_flagged=True,
                ),
            ],
        )
        # High confidence but low toxicity score — should NOT match toxicity_block
        action1 = resolve_action(
            is_flagged=True,
            confidence=0.9,
            categories={"toxicity": 0.5, "insult": 0.9},
            policy=policy,
        )
        assert action1 == Action.WARN  # Falls through to catch_all

        # High toxicity score — should match toxicity_block
        action2 = resolve_action(
            is_flagged=True,
            confidence=0.9,
            categories={"toxicity": 0.95, "insult": 0.9},
            policy=policy,
        )
        assert action2 == Action.BLOCK


class TestPolicyLoader:
    """YAML policy loader."""

    def test_load_from_string_standard(
        self, sample_policy_yaml: str
    ) -> None:
        """Load standard policy from YAML string."""
        loader = PolicyLoader(cache=False)
        policy = loader.load_from_string(sample_policy_yaml)
        assert policy.name == "standard"
        assert len(policy.rules) == 5

    def test_load_from_string_strict(
        self, sample_policy_strict_yaml: str
    ) -> None:
        """Load strict policy from YAML string."""
        loader = PolicyLoader(cache=False)
        policy = loader.load_from_string(sample_policy_strict_yaml)
        assert policy.name == "strict"
        assert len(policy.rules) == 3

    def test_load_from_string_relaxed(
        self, sample_policy_relaxed_yaml: str
    ) -> None:
        """Load relaxed policy from YAML string."""
        loader = PolicyLoader(cache=False)
        policy = loader.load_from_string(sample_policy_relaxed_yaml)
        assert policy.name == "relaxed"
        assert len(policy.rules) == 3

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Load policy from file."""
        config_path = tmp_path / "policy.yaml"
        config_path.write_text("""
name: file_test
description: Loaded from file
rules:
  - name: block_all
    action: block
    min_confidence: 0.5
    require_flagged: true
  - name: allow_rest
    action: allow
""")
        loader = PolicyLoader(cache=False)
        policy = loader.load(str(config_path))
        assert policy.name == "file_test"
        assert len(policy.rules) == 2

    def test_file_not_found(self) -> None:
        """Loading non-existent file should raise FileNotFoundError."""
        loader = PolicyLoader(cache=False)
        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/policy.yaml")

    def test_invalid_yaml(self) -> None:
        """Invalid YAML should raise a YAML parsing error."""
        loader = PolicyLoader(cache=False)
        import yaml as yaml_lib
        with pytest.raises((PolicyLoadError, yaml_lib.YAMLError)):
            loader.load_from_string("{invalid yaml: ")

    def test_invalid_action_value(self) -> None:
        """Invalid action string should raise PolicyLoadError."""
        loader = PolicyLoader(cache=False)
        with pytest.raises(PolicyLoadError):
            loader.load_from_string("""
name: invalid
rules:
  - name: bad_action
    action: nonexistent
""")

    def test_non_mapping_yaml(self) -> None:
        """Non-mapping YAML should raise PolicyLoadError."""
        loader = PolicyLoader(cache=False)
        with pytest.raises(PolicyLoadError):
            loader.load_from_string("just a string")

    def test_list_yaml(self) -> None:
        """List YAML should raise PolicyLoadError."""
        loader = PolicyLoader(cache=False)
        with pytest.raises(PolicyLoadError):
            loader.load_from_string("- item1\n- item2")

    def test_cache_hits(self, tmp_path: Path) -> None:
        """Cached policies should return cached instance."""
        config_path = tmp_path / "cached.yaml"
        config_path.write_text("""
name: cached_policy
rules:
  - name: rule1
    action: allow
""")
        loader = PolicyLoader(cache=True)
        policy1 = loader.load(str(config_path))
        policy2 = loader.load(str(config_path))
        assert policy1 is policy2  # Same instance from cache

    def test_cache_bypass(self, tmp_path: Path) -> None:
        """Disabling cache should reload every time."""
        config_path = tmp_path / "nocache.yaml"
        config_path.write_text("""
name: nocache
rules:
  - name: rule1
    action: allow
""")
        loader = PolicyLoader(cache=False)
        policy1 = loader.load(str(config_path))
        policy2 = loader.load(str(config_path))
        assert policy1 is not policy2  # Different instances

    def test_clear_cache(self, tmp_path: Path) -> None:
        """Clearing cache should force reload."""
        config_path = tmp_path / "cleared.yaml"
        config_path.write_text("""
name: cleared
rules:
  - name: rule1
    action: allow
""")
        loader = PolicyLoader(cache=True)
        policy1 = loader.load(str(config_path))
        loader.clear_cache()
        policy2 = loader.load(str(config_path))
        assert policy1 is not policy2  # Different instances after clear

    def test_list_cache(self, tmp_path: Path) -> None:
        """list_cache should return cached file paths."""
        config_path = tmp_path / "listed.yaml"
        config_path.write_text("""
name: listed_policy
rules: []
""")
        loader = PolicyLoader(cache=True)
        loader.load(str(config_path))
        cache = loader.list_cache()
        assert str(config_path) in cache
        assert cache[str(config_path)] == "listed_policy"

    def test_rule_action_mapping(self) -> None:
        """Rules should have correct action mappings parsed from YAML."""
        loader = PolicyLoader(cache=False)
        policy = loader.load_from_string("""
name: mapping_test
rules:
  - name: block_rule
    action: block
    min_confidence: 0.5
    require_flagged: true
  - name: warn_rule
    action: warn
    min_confidence: 0.3
    max_confidence: 0.5
    require_flagged: true
  - name: review_rule
    action: review
    min_confidence: 0.1
    max_confidence: 0.3
    require_flagged: true
  - name: log_rule
    action: log_only
    min_confidence: 0.0
    max_confidence: 0.1
    require_flagged: true
  - name: allow_rule
    action: allow
""")
        assert policy.rules[0].action == Action.BLOCK
        assert policy.rules[1].action == Action.WARN
        assert policy.rules[2].action == Action.REVIEW
        assert policy.rules[3].action == Action.LOG_ONLY
        assert policy.rules[4].action == Action.ALLOW


class TestThresholdConfiguration:
    """Policy threshold configuration edge cases."""

    def test_zero_threshold_matches_everything(self) -> None:
        """min_confidence=0 with require_flagged=False matches all."""
        policy = ModerationPolicy(
            name="zero",
            rules=[
                PolicyRule(
                    name="catch_all",
                    action=Action.BLOCK,
                    min_confidence=0.0,
                ),
            ],
        )
        action = resolve_action(True, 0.0, policy=policy)
        assert action == Action.BLOCK

    def test_max_confidence_excludes_high(self) -> None:
        """max_confidence should exclude results above it."""
        policy = ModerationPolicy(
            name="max_test",
            rules=[
                PolicyRule(
                    name="only_low",
                    action=Action.REVIEW,
                    min_confidence=0.0,
                    max_confidence=0.5,
                    require_flagged=True,
                ),
                PolicyRule(
                    name="everything_else",
                    action=Action.ALLOW,
                ),
            ],
        )
        # High confidence should skip only_low rule
        action = resolve_action(
            is_flagged=True, confidence=0.9, policy=policy
        )
        assert action == Action.ALLOW

    def test_no_match_falls_to_default(self) -> None:
        """When no rule matches, should return ALLOW."""
        policy = ModerationPolicy(
            name="no_match",
            rules=[
                PolicyRule(
                    name="impossible",
                    action=Action.BLOCK,
                    min_confidence=2.0,  # Impossible threshold
                ),
            ],
        )
        action = resolve_action(True, 0.5, policy=policy)
        assert action == Action.ALLOW
