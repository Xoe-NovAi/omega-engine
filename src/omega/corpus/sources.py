# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Corpus source registry — where the early vision and technical record live.

The Ark accumulates knowledge across partitions. These roots are the
discovered corpus. Each source declares its tier so operators can index
the vision layer (small, precious) separately from the bulk build record
(large, noisy).

M28 Sovereign Artifact Preservation: nothing here is ever deleted. Sources
are read-only inputs; this registry only ever adds rows to the index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ── Tier semantics ──────────────────────────────────────────────────────────
# T1 VISION   — the early vision corpus. Small, irreplaceable, authored.
# T2 GENESIS  — the 2025 pre-engine origins (heart_of_omega).
# T3 LOSTDOC  — recovered docs from the omega-cut-final partition (stale/
#               archive strategy, research, legacy). Never re-indexed
#               elsewhere; this is their only retrieval surface.
# T4 EARLY    — the first build record (XNAi blueprints, setup logs).
# T5 STRATEGY — current-tree strategy/architecture/federation docs.

TIER_NAMES = {
    1: "vision",
    2: "genesis",
    3: "lostdoc",
    4: "early",
    5: "strategy",
}


@dataclass
class CorpusSource:
    """One indexed root on disk."""

    source_id: str
    tier: int
    label: str
    roots: List[Path] = field(default_factory=list)
    # Filename suffixes to index. Empty = default text set.
    suffixes: Optional[List[str]] = None
    # Skip these path fragments (site-packages, node_modules, venv).
    exclude: List[str] = field(
        default_factory=lambda: ["site-packages", "node_modules", ".venv", "__pycache__"]
    )
    # Skip hidden dirs (.git, .venv_mcp).
    include_hidden: bool = False

    def describe(self) -> str:
        roots = ", ".join(str(r) for r in self.roots)
        return f"{self.source_id} [t{self.tier}:{TIER_NAMES.get(self.tier)}] {roots}"


DEFAULT_SUFFIXES = [".md", ".txt", ".html", ".rst", ".yaml", ".yml", ".py", ".json"]


def _p(*candidates: str) -> List[Path]:
    out = []
    for c in candidates:
        p = Path(c).expanduser()
        out.append(p)
    return out


# ── The discovered corpus ───────────────────────────────────────────────────
# Absolute partitions are preferred but each root is tolerant of absence:
# a missing partition degrades to "source unavailable", never to a crash.
CORPUS_SOURCES: List[CorpusSource] = [
    CorpusSource(
        source_id="vision_corpus",
        tier=1,
        label="Sonnet-4.6 extended vision corpus (The Living Word, The Deepening, The Origin)",
        roots=_p(
            "~/Documents/Xoe-NovAi/omega_library/intake/inbox/omega-mission-clarification",
            "/media/arcana-novai/omega_library/intake/inbox/omega-mission-clarification",
        ),
        suffixes=[".md", ".html", ".txt"],
    ),
    CorpusSource(
        source_id="genesis_origins",
        tier=2,
        label="Pre-engine origins 2025 (heart_of_omega)",
        roots=_p(
            "~/Documents/Xoe-NovAi/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega",
            "/media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega",
        ),
        suffixes=[".md", ".txt", ".py"],
    ),
    CorpusSource(
        source_id="lostdocs_strategy",
        tier=3,
        label="Recovered lost docs (omega-cut-final archive+strategy)",
        roots=_p(
            "~/Documents/Xoe-NovAi/omega-cut-final/docs/archive",
            "~/Documents/Xoe-NovAi/omega-cut-final/docs/strategy",
        ),
    ),
    CorpusSource(
        source_id="lostdocs_breadth",
        tier=3,
        label="Recovered lost docs — broader cut-final doc tree",
        roots=_p("~/Documents/Xoe-NovAi/omega-cut-final/docs"),
        # De-prioritise the two very large generated llms dumps.
        exclude=["site-packages", "node_modules", "site", "llms-full.txt"],
    ),
    CorpusSource(
        source_id="early_build",
        tier=4,
        label="First build record (XNAi blueprints, early setup)",
        roots=_p(
            "~/Documents/Xoe-NovAi/omega_library/intake/mining_queue/Omega-Early-Material",
            "/media/arcana-novai/omega_library/intake/mining_queue/Omega-Early-Material",
        ),
        # The early tree is 2.3GB / mostly .py vendor + png; keep text + blueprints.
        exclude=["site-packages", "node_modules", ".venv", "__pycache__", "images", "assets"],
    ),
    CorpusSource(
        source_id="current_strategy",
        tier=5,
        label="Current-tree strategy / architecture / federation docs",
        roots=_p("~/Documents/Xoe-NovAi/omega-engine/docs"),
    ),
]


def resolve_sources(only: Optional[List[str]] = None) -> List[CorpusSource]:
    """Return sources filtered by id (if given), dropping those with no present root."""
    selected = CORPUS_SOURCES
    if only:
        wanted = set(only)
        selected = [s for s in selected if s.source_id in wanted]
    out = []
    for s in selected:
        present = [r for r in s.roots if r.exists()]
        if present:
            s = CorpusSource(
                source_id=s.source_id,
                tier=s.tier,
                label=s.label,
                roots=present,
                suffixes=s.suffixes,
                exclude=s.exclude,
                include_hidden=s.include_hidden,
            )
            out.append(s)
    return out
