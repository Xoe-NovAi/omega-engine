# 🔱 Omega Engine — Report Digestion Layer
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# Zero-inference-cost Python preprocessing for MaKaLi Parallel Council.
# Phase 1.5: Transforms raw pillar reports into LLM-optimized digests.
#
# Research doc: docs/research/R_REPORT_DIGESTION_LAYER_OPTIMIZATION_20260719.md
#
# TODO (T0 Session 2):
# - Executive summary extraction (3-tier fallback: explicit section → first-sentence → first-N-paragraphs)
# - Cross-reference index (mandate tags + entity references + shared keywords)
# - Conflict detection (numeric conflicts + mandate compliance conflicts)
# - Mandate compliance matrix ([M1]-[M23] per pillar)
# - Token budget allocation (adaptive fusion: confidence + mandate criticality + novelty)
# - M23 fallback: raw stack-cat concatenation on failure

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class PillarReport:
    """A single pillar's independent output."""
    pillar_id: str
    domain: str
    content: str
    file_path: Path


@dataclass
class Conflict:
    concept: str
    values: Dict[str, str]
    severity: str = "INFO"


@dataclass
class DigestedReport:
    side: str
    pillars: List[PillarReport]
    executive_summary: str
    pillar_summaries: Dict[str, str]
    cross_reference_index: Dict[str, List[str]]
    conflict_map: List[Conflict]
    mandate_compliance: Dict[str, Dict[str, str]]
    token_budget_allocation: Dict[str, int]


class ReportDigester:
    """Zero-inference-cost report digestion using Python analysis only.
    
    Features:
    - Executive summary extraction (explicit section → first-sentence → first-N-paragraphs)
    - Cross-reference index (mandate tags + entity references + shared keywords)
    - Conflict detection (numeric + mandate compliance)
    - Mandate compliance matrix
    - Token budget allocation
    - M23: raw stack-cat fallback on failure
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
    
    def digest(self, build_pillars: List[PillarReport], run_pillars: List[PillarReport]) -> Tuple[DigestedReport, DigestedReport]:
        """Main entry point — returns (build_digested, run_digested)."""
        build_digested = self._digest_side("BUILD", build_pillars)
        run_digested = self._digest_side("RUN", run_pillars)
        return build_digested, run_digested
    
    def _digest_side(self, side: str, pillars: List[PillarReport]) -> DigestedReport:
        """Digest a single side (BUILD or RUN)."""
        # TODO: T0 Session 2 implementation
        # This is a pass-through stub for now
        return DigestedReport(
            side=side,
            pillars=pillars,
            executive_summary="",
            pillar_summaries={},
            cross_reference_index={},
            conflict_map=[],
            mandate_compliance={},
            token_budget_allocation={},
        )
    
    def _extract_summary(self, content: str, max_chars: int = 500) -> str:
        """Extract executive summary with 3-tier fallback.
        
        Tier 1: ## Summary or ## Executive Summary section
        Tier 2: First sentence of each ## section
        Tier 3: First 3 paragraphs
        """
        # Tier 1: Explicit summary section
        for header in [r'## (Executive )?Summary', r'## TL;DR', r'## Overview']:
            if match := re.search(
                rf'{header}\n(.+?)(?=\n## |\Z)', content, re.DOTALL
            ):
                return match.group(1).strip()[:max_chars]
        
        # Tier 2: First sentence of each section
        sections = re.split(r'\n## ', content)
        sentences = []
        for sec in sections[1:]:  # Skip preamble
            if '. ' in sec:
                first_sent = sec.split('. ')[0].strip()
                if first_sent:
                    sentences.append(first_sent)
        if sentences:
            result = '\n'.join(sentences)
            return result[:max_chars]
        
        # Tier 3: First 3 paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        result = '\n\n'.join(paragraphs[:3])
        return result[:max_chars]
    
    def _build_cross_reference(self, pillars: List[PillarReport]) -> Dict[str, List[str]]:
        """Build cross-reference index across pillars.
        
        Sources:
        1. Mandate tags [M1]-[M23]
        2. Source file paths (src/omega/...)
        3. Entity references (P1-P10)
        """
        cross_ref: Dict[str, List[str]] = {}
        
        for pillar in pillars:
            # Strategy 1: Mandate tags
            for tag in re.findall(r'\[M(\d+)\]', pillar.content):
                cross_ref.setdefault(f'Mandate M{tag}', []).append(pillar.pillar_id)
            
            # Strategy 2: Source file paths
            for path in re.findall(r'(src/omega/[\w/]+\.\w+)', pillar.content):
                cross_ref.setdefault(f'File: {path}', []).append(pillar.pillar_id)
            
            # Strategy 3: Pillar cross-references
            for ref in re.findall(r'P\d+', pillar.content):
                if ref != pillar.pillar_id:  # Don't self-reference
                    cross_ref.setdefault(f'Reference: {ref}', []).append(pillar.pillar_id)
        
        return cross_ref
    
    def _detect_conflicts(self, pillars: List[PillarReport]) -> List[Conflict]:
        """Detect conflicts across pillars.
        
        Types:
        1. Numeric conflicts: same entity, different values
        2. Mandate compliance conflicts: same mandate, different compliance
        """
        conflicts: List[Conflict] = []
        
        # Numeric conflicts
        numeric_params: Dict[str, Dict[str, int]] = {}
        for p in pillars:
            for match in re.finditer(r'(\w[\w_]+):\s*(\d+)', p.content):
                key, val = match.groups()
                numeric_params.setdefault(key, {})[p.pillar_id] = int(val)
        
        for key, values in numeric_params.items():
            if len(set(values.values())) > 1:
                vals = list(values.values())
                max_diff = max(vals) - min(vals)
                severity = "WARNING" if max_diff > 0.5 * max(vals) else "INFO"
                conflicts.append(Conflict(
                    concept=key,
                    values={pid: str(v) for pid, v in values.items()},
                    severity=severity,
                ))
        
        return conflicts
    
    def _build_mandate_matrix(self, pillars: List[PillarReport]) -> Dict[str, Dict[str, str]]:
        """Build mandate compliance matrix.
        
        Returns: {pillar_id: {mandate: "✅"|"❌"|"⚠️"|""}}
        """
        matrix: Dict[str, Dict[str, str]] = {}
        mandates = [f"M{i}" for i in range(1, 24)]
        
        for pillar in pillars:
            pillar_matrix: Dict[str, str] = {}
            for mandate in mandates:
                if re.search(rf'{re.escape(mandate)}\s*(✅|❌|⚠️)', pillar.content):
                    match = re.search(rf'{re.escape(mandate)}\s*(✅|❌|⚠️)', pillar.content)
                    pillar_matrix[mandate] = match.group(1) if match else ""
                else:
                    pillar_matrix[mandate] = ""  # Not mentioned
            
            matrix[pillar.pillar_id] = pillar_matrix
        
        return matrix
    
    def _allocate_budget(self, pillars: List[PillarReport], total_budget: int = 32000) -> Dict[str, int]:
        """Allocate token budget across pillars using adaptive fusion.
        
        Formula: 
        score = 0.5 * confidence + 0.3 * mandate_criticality + 0.2 * novelty
        """
        scores: Dict[str, float] = {}
        
        for p in pillars:
            words = p.content.split()
            unique_words = len(set(words))
            
            confidence = 0.5  # TODO: extract from confidence keywords
            mandate_criticality = len(self._build_mandate_matrix([p]).get(p.pillar_id, {})) / 23
            novelty = unique_words / max(len(words), 1)  # Type-token ratio
            
            scores[p.pillar_id] = 0.5 * confidence + 0.3 * mandate_criticality + 0.2 * novelty
        
        total_score = sum(scores.values()) or 1
        return {
            pid: int(total_budget * score / total_score)
            for pid, score in scores.items()
        }


def raw_stack_cat_concat(pillars: List[PillarReport]) -> str:
    """M23 fallback: raw concatenation without any intelligence layer."""
    sections = []
    for p in pillars:
        sections.append(f"## PILLAR {p.pillar_id}: {p.domain}\n\n{p.content}")
    return "\n\n---\n\n".join(sections)
