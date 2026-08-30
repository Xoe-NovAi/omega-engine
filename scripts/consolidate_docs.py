#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Deep consolidation of strategy, coordination, and research docs.
Classifies: CURRENT / SUPERSEDED / ARCHIVE / DELETE
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path("/home/arcana-novai/Documents/Xoe-NovAi/omega-engine")

# ============================================================
# CLASSIFICATION RULES
# ============================================================

# Strategy docs - CURRENT (SSOT)
STRATEGY_CURRENT = {
    "DEBUT_REMEDIATION_MANUAL_20260817.md",      # Sprint SSOT
    "SOVEREIGN_MANDATES.md",                      # 27 Mandates (v3.8.0)
    "MANDATES_CONDENSED.md",                      # Tier-0 injection
    "AGENTS.md",                                  # Agent landing
    "STRATEGY_INDEX.md",                          # Strategy map
    "STRATEGY_CORPUS_MAP.md",                     # Corpus map
    "PIVOT_LOG.md",                               # Decisions D-521+
    "PIVOT_LOG_CANONICAL.md",                     # Ancient decisions
    "PIVOT_LOG_ARCHIVE_20260522_20260810.md",    # Pre-campaign
    "HOLISTIC_ARCHITECTURE_PLAN_20260820.md",    # Architecture
    "SOVEREIGN_ARK_BLUEPRINT.md",                 # Vision (read-only)
    "EVOLVER_SDP_SUCCESSOR.md",                   # SDP successor
    "NOTEBOOKLM_UNIFIED_STRATEGY.md",             # NotebookLM
    "HEADROOM_SPEC.md",                           # Headroom spec
    "QDRANT_MIGRATION_PLAN.md",                   # Qdrant migration
}

# Strategy docs - SUPERSEDED (explicit version chains)
STRATEGY_SUPERSEDED = {
    "CANONICAL_ROADMAP_20260721.md": "superseded by HOLISTIC_ARCHITECTURE_PLAN_20260820.md",
    "ENHANCED_COORDINATION_STRATEGY_v2_20260730.md": "superseded by COORDINATION_ENHANCEMENT_PLAN_20260814.md",
    "CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md": "superseded by CONTEXT_PACKER_ENHANCEMENT_PLAN.md",
    "CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md": "superseded by DEBUT_REMEDIATION_MANUAL_20260817.md",
    "FINAL_INSPECTION_REPORT_20260722.md": "superseded by CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md",
    "ENGINE_DECISIONS_CONSOLIDATED_20260817.md": "superseded by PIVOT_LOG.md",
}

# Coordination - CURRENT (active sprint artifacts)
COORD_CURRENT = {
    "ACTIVE_SPRINT.json",
    "HMC_COLLABORATION_HUB.md",
    "GAP_REGISTRY.json",
    "WAKE_STATE.json",
    "PRE_COMPACTION_MASTER_INDEX_20260828.md",
    "MASTER_BRIEFING_LILITH_FOR_KALI_20260828.md",
    "DEFINITIVE_SYNTHESIS_LILITH_FOR_KALI_20260828.md",
    "STRATEGIC_REVIEW_SYNTHESIS_20260828.md",
    "ARCHITECT_DECISIONS_BREAKDOWN_20260828.md",
    "CLINE_FULL_REVIEW_ROLLUP_20260828.md",
    "CLINE_TO_KALI_HARDENING_BRIEFING_V2_20260828.md",
    "COMMUNITY_LAUNCH_NARRATIVE_20260828.md",
    "NO_PUNT_DOCTRINE_20260828.md",
    "SECRET_ROTATION_LOG.md",
    "SECRET_ROTATION_LOG.yaml",
    "TRACKING_ARCHITECTURE.md",
    "TASK_REGISTRY.json",
    "NODE_EXPERT_SESSIONS_PLAN.md",
    "EXPERT_SESSION_REGISTRY.md",
    "EXPERT_SESSION_REGISTRY_NARRATIVE.md",
    "HANDOFF_PACKET_SCHEMA.md",
    "SUBAGENT_DISPATCH_PROTOCOL.md",
    "CONVERSATIONAL_SUBAGENT_PROTOCOL.md",
    "NODE_ONBOARDING_PROTOCOL.md",
    "STALLED_SUBAGENT_RECOVERY.md",
    "AUTONOMOUS_MEDITATION.md",
}

# Coordination - SUPERSEDED (version chains)
COORD_SUPERSEDED = {
    "CLINE_FULL_REVIEW_ROLLUP_20260828.md": "v1 superseded by v2 (same name, updated)",
    "CLINE_TO_KALI_HARDENING_BRIEFING_20260828.md": "superseded by V2",
    "CLINE_FINAL_REVIEW_20260820.md": "superseded by CLINE_FULL_REVIEW_ROLLUP",
    "CLINE_DEEP_PASS_AMENDMENT_20260818.md": "superseded by later reviews",
    "CLINE_KALI_CONSOLIDATION_20260817.md": "superseded by later coordination",
    "CLINE_KALI_REPORT_20260817.md": "superseded by later coordination",
    "CLINE_KALI_VERIFICATION_20260817.md": "superseded by later verification",
    "CLINE_COMPLETION_REPORT_20260822.md": "superseded by later completion",
    "CLINE_INSIGHTS_Q1_Q7_20260818.md": "superseded by later insights",
    "CARMCK_REVIEW_HEADROOM_20260820.md": "superseded by CARMCK_FINAL_READINESS",
    "CARMCK_VAULT_AUDIT_20260818.md": "superseded by later vault audit",
    "CARMCK_FINAL_READINESS_20260828.md": "CURRENT - final readiness",
    "CARMACK_FULL_REPO_REVIEW_CHECKLIST_20260828.md": "superseded by VALIDATED version",
    "CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md": "CURRENT - validated",
    "CARMACK_ALPHA_LAUNCH_VERDICT_20260828.md": "CURRENT - launch verdict",
    "ARCHITECT_DECISIONS_BREAKDOWN_20260828.md": "CURRENT - decisions breakdown",
    "ARCHITECT_OVERSIGHT_PATTERNS_20260823.md": "superseded by 2028 version",
    "AGENT_COLLAB_TEMPLATES_20260826.md": "CURRENT - templates",
    "COORDINATION_HUB_v1_FINAL.md": "superseded by HMC_COLLABORATION_HUB.md",
}

# Research - CANONICAL (final validated)
RESEARCH_CANONICAL = {
    "R_CARMACK_FINAL_READINESS_20260828.md",
    "R_CARMACK_GOOGLE_INTEGRATION_20260828.md",
    "R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md",
    "R_CARMACK_MODEL_STRATEGY_20260828.md",
    "R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md",
    "R_CLINE_FULL_REVIEW_ROLLUP_20260828.md",  # Wait, this is in coordination
    "R_CLINE_GOOGLE_ROTATION_20260828.md",
    "R_COPILOT_FINAL_READINESS_20260828.md",
    "R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md",
    "R_ANTIGRAVITY_FINAL_READINESS_20260828.md",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md",
    "R_ANTIGRAVITY_AUDIT_VALIDATION_20260828.md",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md",
    "R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md",
    "R_GROKSTER_CONTEXT_MYSTERY_SYNTHESIS_20260828.md",
    "R_GROKSTER_GOOGLE_API_RESEARCH_20260828.md",
    "R_GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md",
    "R_JEM_AGENT_HIERARCHIES_20260828.md",
    "R_402_FORENSIC_20260827.md",
    "R_VAULT_COPILOT_ROUND4_20260828.md",
    "R_VAULT_ANTIGRAVITY_DEEPER_20260827.md",
    "R_REVIEW_VERITY_20260828.md",
    "R_CARMACK_ARTIFACT_AUDIT_20260827.md",
    "R_CARMACK_FINAL_READINESS_20260828.md",
    "R_CARMACK_GOOGLE_INTEGRATION_20260828.md",
}

# Research - SUPERSEDED (version chains)
RESEARCH_SUPERSEDED = {
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded by later integration docs",
    "R_VAULT_COPILOT_ROUND3_20260827.md": "superseded by ROUND4",
    "R_VAULT_ANTIGRAVITY_DEEPER_20260827.md": "superseded by later vault docs",
    "R_CARMACK_ARTIFACT_AUDIT_20260827.md": "superseded by validation",
    "R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md": "superseded by final readiness",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded by validated checklist",
    "R_CLINE_GOOGLE_ROTATION_20260828.md": "superseded by rotation log",
    "R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md": "superseded by final readiness",
    "R_ANTIGRAVITY_AUDIT_VALIDATION_20260828.md": "superseded by final readiness",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md": "superseded by final readiness",
    "R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md": "CURRENT - final",
    "R_GROKSTER_CONTEXT_MYSTERY_SYNTHESIS_20260828.md": "superseded by final",
    "R_GROKSTER_GOOGLE_API_RESEARCH_20260828.md": "superseded by final",
    "R_GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md": "superseded by later ROI",
    "R_JEM_AGENT_HIERARCHIES_20260828.md": "CURRENT - hierarchies",
    "R_402_FORENSIC_20260827.md": "CURRENT - forensic",
    "R_VAULT_COPILOT_ROUND4_20260828.md": "CURRENT - round 4",
    "R_VAULT_ANTIGRAVITY_DEEPER_20260827.md": "superseded",
    "R_REVIEW_VERITY_20260828.md": "CURRENT - verity review",
    "R_CARMACK_ARTIFACT_AUDIT_20260827.md": "superseded",
    "R_CARMACK_FINAL_READINESS_20260828.md": "CURRENT - final",
    "R_CARMACK_GOOGLE_INTEGRATION_20260828.md": "CURRENT - integration",
    "R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md": "CURRENT - validation",
    "R_CARMACK_MODEL_STRATEGY_20260828.md": "CURRENT - strategy",
    "R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md": "superseded",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded",
    "R_CLINE_GOOGLE_ROTATION_20260828.md": "superseded",
    "R_COPILOT_FINAL_READINESS_20260828.md": "CURRENT - final",
    "R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md": "superseded",
    "R_ANTIGRAVITY_FINAL_READINESS_20260828.md": "CURRENT - final",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md": "superseded",
    "R_ANTIGRAVITY_AUDIT_VALIDATION_20260828.md": "superseded",
    "R_ANTIGRAVITY_GPT53_20260828.md": "superseded",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded",
    "R_CARMACK_FINAL_READINESS_20260828.md": "CURRENT",
    "R_CARMACK_GOOGLE_INTEGRATION_20260828.md": "CURRENT",
    "R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md": "CURRENT",
    "R_CARMACK_MODEL_STRATEGY_20260828.md": "CURRENT",
    "R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md": "superseded",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded",
    "R_CLINE_GOOGLE_ROTATION_20260828.md": "superseded",
    "R_COPILOT_FINAL_READINESS_20260828.md": "CURRENT",
    "R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md": "superseded",
    "R_ANTIGRAVITY_FINAL_READINESS_20260828.md": "CURRENT",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md": "superseded",
    "R_ANTIGRAVITY_AUDIT_VALIDATION_20260828.md": "superseded",
    "R_ANTIGRAVITY_GPT53_20260828.md": "superseded",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded",
    "R_CARMACK_FINAL_READINESS_20260828.md": "CURRENT",
    "R_CARMACK_GOOGLE_INTEGRATION_20260828.md": "CURRENT",
    "R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md": "CURRENT",
    "R_CARMACK_MODEL_STRATEGY_20260828.md": "CURRENT",
    "R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md": "superseded",
    "R_CARMACK_CLINE_TO_OPENCODE_20260828.md": "superseded",
    "R_CARMACK_DOCUMENTATION_QUALITY_20260828.md": "superseded",
    "R_CLINE_GOOGLE_ROTATION_20260828.md": "superseded",
    "R_COPILOT_FINAL_READINESS_20260828.md": "CURRENT",
    "R_COPILOT_GOOGLE_CODE_AUDIT_20260828.md": "superseded",
    "R_ANTIGRAVITY_FINAL_READINESS_20260828.md": "CURRENT",
    "R_ANTIGRAVITY_GOOGLE_BENCHMARKS_20260828.md": "superseded",
    "R_ANTIGRAVITY_AUDIT_VALIDATION_20260828.md": "superseded",
    "R_ANTIGRAVITY_GPT53_20260828.md": "superseded",
}

# DELETE patterns (garbage)
DELETE_PATTERNS = [
    r".*_DRAFT\.md$",
    r".*_TEMP\.md$",
    r".*_TMP\.md$",
    r".*_OLD\.md$",
    r".*_BAK\.md$",
    r".*_BACKUP\.md$",
    r"DEBUG_.*\.md$",
    r"TEST_.*\.md$",
    r".*_FAILED\.md$",
    r".*_CORRUPT\.md$",
    r"empty.*\.md$",
    r".*_EMPTY\.md$",
    r"trim_scope\.py",
    r"update_docs\.py",
    r"youtube-links.*\.txt",
    r"tui\.json",
    r"failed-subagent-copy-paste\.txt",
    r"file$",
    r"old-claude-sys-prompt\.md",
    r"migrate_heritage\.py",
]

# Archive date for this consolidation
ARCHIVE_DATE = "20260828"
ARCHIVE_REASON = "deep_consolidation"


def classify_strategy(filepath: Path) -> tuple:
    """Classify a strategy doc."""
    name = filepath.name
    
    if name in STRATEGY_CURRENT:
        return "CURRENT", "SSOT"
    if name in STRATEGY_SUPERSEDED:
        return "SUPERSEDED", STRATEGY_SUPERSEDED[name]
    
    # Check for version patterns
    if re.search(r"_v\d+_", name) or re.search(r"_202\d{4}\.md$", name):
        # Check if there's a newer version
        base = re.sub(r"_v\d+", "", name)
        base = re.sub(r"_202\d{4}", "", base)
        # For now, mark dated files as SUPERSEDED if not in CURRENT
        if name not in STRATEGY_CURRENT:
            return "SUPERSEDED", f"dated version, likely superseded by newer"
    
    # Check delete patterns
    for pattern in DELETE_PATTERNS:
        if re.match(pattern, name):
            return "DELETE", "garbage pattern"
    
    # Default: ARCHIVE (historical reference)
    return "ARCHIVE", "historical reference"


def classify_coordination(filepath: Path) -> tuple:
    """Classify a coordination doc."""
    name = filepath.name
    
    if name in COORD_CURRENT:
        return "CURRENT", "active sprint artifact"
    if name in COORD_SUPERSEDED:
        return "SUPERSEDED", COORD_SUPERSEDED[name]
    
    # Check for R_* research reports (handled separately)
    if name.startswith("R_"):
        return "RESEARCH", "research report (see research classification)"
    
    # Check delete patterns
    for pattern in DELETE_PATTERNS:
        if re.match(pattern, name):
            return "DELETE", "garbage pattern"
    
    # Dated coordination docs - likely historical
    if re.search(r"_202\d{4}\.md$", name) and name not in COORD_CURRENT:
        return "ARCHIVE", "historical coordination artifact"
    
    return "ARCHIVE", "historical coordination artifact"


def classify_research(filepath: Path) -> tuple:
    """Classify a research report."""
    name = filepath.name
    
    if name in RESEARCH_CANONICAL:
        return "CANONICAL", "final validated report"
    if name in RESEARCH_SUPERSEDED:
        return "SUPERSEDED", RESEARCH_SUPERSEDED[name]
    
    # Version chains: v1, v2, ROUND3, ROUND4
    if re.search(r"_v\d+_", name) or re.search(r"ROUND\d+", name):
        # Check if there's a higher version
        return "SUPERSEDED", "version chain, likely superseded"
    
    # Dated research - check if there's a newer version
    if re.search(r"_202\d{4}\.md$", name):
        return "SUPERSEDED", "dated research, likely superseded"
    
    return "ARCHIVE", "historical research"


def main():
    results = {
        "strategy": {"CURRENT": [], "SUPERSEDED": [], "ARCHIVE": [], "DELETE": []},
        "coordination": {"CURRENT": [], "SUPERSEDED": [], "ARCHIVE": [], "DELETE": [], "RESEARCH": []},
        "research": {"CANONICAL": [], "SUPERSEDED": [], "ARCHIVE": [], "DELETE": []},
    }
    
    # Classify strategy
    for f in Path(ROOT / "docs/strategy").glob("*.md"):
        cat, reason = classify_strategy(f)
        results["strategy"][cat].append({"file": f.name, "reason": reason, "path": str(f)})
    
    # Classify coordination
    for f in Path(ROOT / "data/coordination").glob("*.md"):
        if f.name.startswith("R_"):
            cat, reason = classify_research(f)
            results["coordination"]["RESEARCH"].append({"file": f.name, "reason": reason, "path": str(f)})
        else:
            cat, reason = classify_coordination(f)
            results["coordination"][cat].append({"file": f.name, "reason": reason, "path": str(f)})
    
    # Classify research (R_* files)
    for f in Path(ROOT / "data/coordination").glob("R_*.md"):
        cat, reason = classify_research(f)
        results["research"][cat].append({"file": f.name, "reason": reason, "path": str(f)})
    
    # Print summary
    print("=== CLASSIFICATION SUMMARY ===")
    for domain, cats in results.items():
        print(f"\n{domain.upper()}:")
        for cat, items in cats.items():
            print(f"  {cat}: {len(items)}")
    
    # Save detailed results
    with open(ROOT / "data/coordination/CLASSIFICATION_RESULTS_20260828.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == "__main__":
    main()