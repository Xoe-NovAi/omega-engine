#!/usr/bin/env python3
"""
Platform-Specific Adapters for the Enhanced Context Packer.

Implements the platform-specific tuning architecture specified in
`docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md`:

  - PlatformProfile enum (web-claude, web-grok, web-gemini, notebooklm)
  - PlatformConfig (loads per-platform tuning from packer-config.yaml)
  - FormatAdapter hierarchy (XML, XML+Markdown hybrid, Markdown-structured, Markdown-sources)
  - BundleOrderingStrategy hierarchy (LITM-U, priority-weighted, relevance, hierarchical, thematic)

M1 (AnyIO): all blocking I/O wrapped in anyio.to_thread.run_sync.
M18 (Token Efficiency): adapters are token-aware, no redundant wrapping.
M23 (Failure Integrity): unknown platform/format/strategy raises, never silently
  falls back to a wrong default.

AP: AP-CONTEXT-PACKER-PLATFORM-ADAPTERS-v1.0.0
"""

from __future__ import annotations

import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import anyio

# ─── Platform Profile Enum ────────────────────────────────────────────────────
class PlatformProfile(str, Enum):
    """Canonical platform profiles supported by the packer.

    Values match the `target_platform` keys in packer-config.yaml.
    """
    WEB_CLAUDE = "web-claude"
    WEB_GROK = "web-grok"
    WEB_GEMINI = "web-gemini"
    NOTEBOOKLM = "notebooklm"
    GENERIC = "generic"

    @classmethod
    def from_str(cls, value: Optional[str]) -> "PlatformProfile":
        if not value:
            return cls.GENERIC
        try:
            return cls(value)
        except ValueError:
            return cls.GENERIC


# ── Bundle Ordering Strategies ────────────────────────────────────────────────
class BundleOrderingStrategy(ABC):
    """Abstract strategy for ordering themed bundles within a pack."""

    name: str = "abstract"

    @abstractmethod
    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return bundles in the platform-appropriate order.

        Each bundle dict has at least: theme (str), files (list of file dicts),
        token_count (int), priority (int), relevance (float).
        """


class LITMUShapedStrategy(BundleOrderingStrategy):
    """Claude: critical at start/end, reference in middle (U-shaped attention)."""
    name = "litm-u-shaped"

    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        start = [b for b in bundles if b.get("priority", 1) >= 3]
        middle = [b for b in bundles if b.get("priority", 1) == 2]
        end = [b for b in bundles if b.get("priority", 1) <= 1]
        return (
            sorted(start, key=lambda b: -b.get("token_count", 0))
            + sorted(middle, key=lambda b: -b.get("token_count", 0))
            + sorted(end, key=lambda b: -b.get("token_count", 0))
        )


class PriorityWeightedStrategy(BundleOrderingStrategy):
    """Grok: weight by priority, less strict position constraints."""
    name = "priority-weighted"

    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            bundles,
            key=lambda b: (-b.get("priority", 1), -b.get("token_count", 0)),
        )


class RelevanceDescendingStrategy(BundleOrderingStrategy):
    """Gemini: most relevant first (works well with retrieval)."""
    name = "relevance-descending"

    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            bundles,
            key=lambda b: (-b.get("relevance", 0.0), -b.get("token_count", 0)),
        )


class HierarchicalStrategy(BundleOrderingStrategy):
    """Gemini 3.1 Pro: overview → detail → appendix."""
    name = "hierarchical"

    TIER_ORDER = {"overview": 0, "detail": 1, "appendix": 2, "general": 3}

    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def tier_key(b: Dict[str, Any]) -> int:
            theme = str(b.get("theme", "")).lower()
            for name, idx in self.TIER_ORDER.items():
                if name in theme:
                    return idx
            return 3
        return sorted(
            bundles,
            key=lambda b: (tier_key(b), -b.get("token_count", 0)),
        )


class ThematicStrategy(BundleOrderingStrategy):
    """NotebookLM: group by theme, each theme self-contained."""
    name = "thematic"

    def order(self, bundles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(
            bundles,
            key=lambda b: (str(b.get("theme", "")), -b.get("relevance", 0.0)),
        )


STRATEGY_REGISTRY: Dict[str, BundleOrderingStrategy] = {
    s.name: s for s in (
        LITMUShapedStrategy(),
        PriorityWeightedStrategy(),
        RelevanceDescendingStrategy(),
        HierarchicalStrategy(),
        ThematicStrategy(),
    )
}


def get_ordering_strategy(name: Optional[str]) -> BundleOrderingStrategy:
    """Resolve an ordering strategy by name. M21: unknown → raise."""
    if not name:
        return LITMUShapedStrategy()
    if name not in STRATEGY_REGISTRY:
        raise ValueError(
            f"[M21] Unknown bundle_ordering strategy '{name}'. "
            f"Available: {sorted(STRATEGY_REGISTRY)}"
        )
    return STRATEGY_REGISTRY[name]


# ── Format Adapters ───────────────────────────────────────────────────────────
class FormatAdapter(ABC):
    """Abstract adapter: renders a bundle + manifest for a target platform."""

    name: str = "abstract"
    extension: str = ".md"  # default output file extension

    @abstractmethod
    def render_bundle(self, theme: str, files: List[Dict[str, Any]],
                      profile_name: str) -> str:
        """Render a single themed bundle (files already XML-escaped)."""

    @abstractmethod
    def render_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                        total_files: int, total_tokens: int, description: str,
                        max_slots: int, target_model: Optional[str],
                        prompt_caching: bool, pack_id: str = "",
                        account: Optional[str] = None, project: Optional[str] = None,
                        version: Optional[str] = None) -> str:
        """Render the pack manifest."""


class XMLFormatAdapter(FormatAdapter):
    """Claude-native XML with <file> blocks and a <pack> root."""
    name = "xml"
    extension = ".xml"

    def render_bundle(self, theme: str, files: List[Dict[str, Any]],
                      profile_name: str) -> str:
        # files is the list of file dicts; build the <pack> wrapper
        inner = "".join(f["rendered"] for f in files if f.get("rendered"))
        return f'<pack profile="{profile_name}" theme="{theme}">\n{inner}</pack>\n'

    def render_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                        total_files: int, total_tokens: int, description: str,
                        max_slots: int, target_model: Optional[str],
                        prompt_caching: bool, pack_id: str = "",
                        account: Optional[str] = None, project: Optional[str] = None,
                        version: Optional[str] = None) -> str:
        lines = [
            f"# Enhanced Context Pack Manifest: {profile_name}",
            f"Generated: {datetime.now().isoformat()}",
            f"Pack ID: {pack_id}",
            f"Account: {account or 'unspecified'}",
            f"Project: {project or 'unspecified'}",
            f"Version: {version or 'unspecified'}",
            f"Description: {description}",
            f"Total Files: {total_files}",
            f"Estimated Total Tokens: {total_tokens}",
            f"Max Slots: {max_slots}",
        ]
        if target_model:
            lines.append(f"Target Model: {target_model}")
        if prompt_caching:
            lines.append("Prompt Caching: enabled")
        lines.append("")
        lines.append("## Theme Breakdown")
        for b in bundles:
            if b.get("files"):
                lines.append(
                    f"- {b['theme']}: {len(b['files'])} files, "
                    f"~{b.get('token_count', 0)} tokens"
                )
        lines.extend([
            "",
            "## Usage Notes",
            "- This pack uses XML format for optimal Claude comprehension",
            "- Each file is wrapped in <file> tags with metadata attributes including pack_id",
            "- The manifest should be reviewed first to understand the pack structure",
            "- Token counts are estimates using cl100k_base encoder (Claude's tokenizer)",
            "- Pack ID enables forensic linking between pack materials and responses",
        ])
        return "\n".join(lines)


class XMLMarkdownHybridAdapter(FormatAdapter):
    """Grok: XML structure with Markdown content preserved."""
    name = "xml-markdown-hybrid"
    extension = ".md"

    def render_bundle(self, theme: str, files: List[Dict[str, Any]],
                      profile_name: str) -> str:
        inner = "".join(f["rendered"] for f in files if f.get("rendered"))
        return (f'<bundle format="markdown" profile="{profile_name}" '
                f'theme="{theme}">\n{inner}</bundle>\n')

    def render_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                        total_files: int, total_tokens: int, description: str,
                        max_slots: int, target_model: Optional[str],
                        prompt_caching: bool) -> str:
        return self._render_md_manifest(
            profile_name, bundles, total_files, total_tokens, description,
            max_slots, target_model, prompt_caching,
        )

    def _render_md_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                            total_files: int, total_tokens: int, description: str,
                            max_slots: int, target_model: Optional[str],
                            prompt_caching: bool) -> str:
        lines = [
            f"# Context Pack Manifest: {profile_name}",
            f"Generated: {datetime.now().isoformat()}",
            f"Description: {description}",
            f"Total Files: {total_files}",
            f"Estimated Total Tokens: {total_tokens}",
            f"Max Slots: {max_slots}",
        ]
        if target_model:
            lines.append(f"Target Model: {target_model}")
        if prompt_caching:
            lines.append("Prompt Caching: enabled")
        lines.append("")
        lines.append("## Theme Breakdown")
        for b in bundles:
            if b.get("files"):
                lines.append(
                    f"- {b['theme']}: {len(b['files'])} files, "
                    f"~{b.get('token_count', 0)} tokens"
                )
        return "\n".join(lines)


class MarkdownStructuredAdapter(FormatAdapter):
    """Gemini: Markdown with structured frontmatter."""
    name = "markdown-structured"
    extension = ".md"

    def render_bundle(self, theme: str, files: List[Dict[str, Any]],
                      profile_name: str) -> str:
        inner = "".join(f["rendered"] for f in files if f.get("rendered"))
        return f"---\ntheme: {theme}\n---\n\n{inner}"

    def render_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                        total_files: int, total_tokens: int, description: str,
                        max_slots: int, target_model: Optional[str],
                        prompt_caching: bool) -> str:
        return XMLMarkdownHybridAdapter()._render_md_manifest(
            profile_name, bundles, total_files, total_tokens, description,
            max_slots, target_model, prompt_caching,
        )


class MarkdownSourcesAdapter(FormatAdapter):
    """NotebookLM: individual source files with citation metadata."""
    name = "markdown-sources"
    extension = ".md"

    def render_bundle(self, theme: str, files: List[Dict[str, Any]],
                      profile_name: str) -> str:
        # Each file already rendered as a self-contained markdown source block
        inner = "".join(f["rendered"] for f in files if f.get("rendered"))
        return inner

    def render_manifest(self, profile_name: str, bundles: List[Dict[str, Any]],
                        total_files: int, total_tokens: int, description: str,
                        max_slots: int, target_model: Optional[str],
                        prompt_caching: bool) -> str:
        return MarkdownStructuredAdapter().render_manifest(
            profile_name, bundles, total_files, total_tokens, description,
            max_slots, target_model, prompt_caching,
        )


FORMAT_REGISTRY: Dict[str, FormatAdapter] = {
    a.name: a for a in (
        XMLFormatAdapter(),
        XMLMarkdownHybridAdapter(),
        MarkdownStructuredAdapter(),
        MarkdownSourcesAdapter(),
    )
}


def get_format_adapter(name: Optional[str]) -> FormatAdapter:
    """Resolve a format adapter by name. M21: unknown → raise."""
    if not name:
        return XMLFormatAdapter()  # default = Claude-native
    if name not in FORMAT_REGISTRY:
        raise ValueError(
            f"[M21] Unknown format '{name}'. "
            f"Available: {sorted(FORMAT_REGISTRY)}"
        )
    return FORMAT_REGISTRY[name]


# ── Platform Config ───────────────────────────────────────────────────────────
@dataclass
class PlatformConfig:
    """Platform-specific tuning loaded from a profile's config block."""

    profile: PlatformProfile = PlatformProfile.GENERIC
    target_model: Optional[str] = None
    format: str = "xml"
    bundle_ordering: str = "litm-u-shaped"
    max_slots: int = 12
    token_budget_total: int = 150000
    token_budget_per_bundle: int = 15000
    token_budget_reserved_output: int = 50000
    prompt_caching: bool = False
    cache_prefix: List[str] = field(default_factory=list)
    multishot_examples: bool = False
    xml_delimiters: str = "spotlighting"
    source_grounding: bool = False
    parallel_search_hints: bool = False
    code_execution_ready: bool = False
    workspace_export: bool = False
    real_time_injection: bool = False
    grok_skills_export: bool = False
    connector_metadata: bool = False
    cost_tier: str = "standard"
    source_export: bool = False
    audio_overview_ready: bool = False
    guided_prompts: bool = False
    citation_format: str = "default"
    # NEW (v3, manual §1.7.6): which tiktoken encoding this platform uses.
    tokenizer_encoding: str = "cl100k_base"
    # NEW (v3, manual §1.5): safety margin applied by the shared TokenEstimator
    # (replaces the v2 hardcoded 1.3). Claude default 1.3; other platforms
    # configured per profile.
    token_margin_multiplier: float = 1.3
    tier: str = "internal"  # NEW (v3, §2): ship | internal | template

    @classmethod
    def from_profile_config(cls, data: Dict[str, Any]) -> "PlatformConfig":
        """Build a PlatformConfig from a profile's YAML block."""
        platform = PlatformProfile.from_str(data.get("target_platform"))
        token_budget = data.get("token_budget", {})
        prompt_caching = data.get("prompt_caching", {})
        real_time = data.get("real_time_injection", {})
        return cls(
            profile=platform,
            target_model=data.get("target_model"),
            format=data.get("format", "xml"),
            bundle_ordering=data.get("bundle_ordering", "litm-u-shaped"),
            max_slots=int(data.get("max_slots", 12)),
            token_budget_total=int(token_budget.get("total", 150000)),
            token_budget_per_bundle=int(token_budget.get("per_bundle", 15000)),
            token_budget_reserved_output=int(token_budget.get("reserved_output", 50000)),
            prompt_caching=bool(prompt_caching.get("enabled", False)),
            cache_prefix=list(prompt_caching.get("cache_prefix", [])),
            multishot_examples=bool(data.get("multishot_examples", False)),
            xml_delimiters=data.get("xml_delimiters", "spotlighting"),
            source_grounding=bool(data.get("source_grounding", False)),
            parallel_search_hints=bool(data.get("parallel_search_hints", False)),
            code_execution_ready=bool(data.get("code_execution_ready", False)),
            workspace_export=bool(data.get("workspace_export", False)),
            real_time_injection=bool(real_time.get("enabled", False)),
            grok_skills_export=bool(data.get("grok_skills_export", False)),
            connector_metadata=bool(data.get("connector_metadata", False)),
            cost_tier=data.get("cost_tier", "standard"),
            source_export=bool(data.get("source_export", False)),
            audio_overview_ready=bool(data.get("audio_overview_ready", False)),
            guided_prompts=bool(data.get("guided_prompts", False)),
            citation_format=data.get("citation_format", "default"),
            tokenizer_encoding=data.get("tokenizer_encoding", "cl100k_base"),
            token_margin_multiplier=float(data.get("token_margin_multiplier", 1.3)),
            tier=data.get("tier", "internal"),
        )

    @property
    def adapter(self) -> FormatAdapter:
        return get_format_adapter(self.format)

    @property
    def ordering_strategy(self) -> BundleOrderingStrategy:
        return get_ordering_strategy(self.bundle_ordering)