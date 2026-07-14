#!/usr/bin/env python3
"""
Precise Heritage Tag Migration Script
Uses exact file:line locations from HERITAGE_VET_LOG.md
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Exact mappings from HERITAGE_VET_LOG.md: Location -> vet tag
# Format: (relative_file_path, line_number, legacy_pattern, vet_tag)
PRECISE_MAPPINGS: List[Tuple[str, int, str, str]] = [
    # api_clients.py (library/)
    ("library/api_clients.py", 6, r"\[id-soft: quake3-1999\]", "[id-soft: vet-025]"),
    ("library/api_clients.py", 117, r"\[id-soft: quake-1996\]", "[id-soft: vet-026]"),
    ("library/api_clients.py", 128, r"\[id-soft: doom-1993\]", "[id-soft: vet-027]"),
    ("library/api_clients.py", 470, r"\[id-soft: doom-1993\]", "[id-soft: vet-028]"),
    
    # coordinator.py (library/)
    ("library/coordinator.py", 5, r"\[id-soft: doom3bfg-2012\]", "[id-soft: vet-029]"),
    
    # extractor.py (library/)
    ("library/extractor.py", 134, r"\[id-soft: doom-1993\]", "[id-soft: vet-030]"),
    ("library/extractor.py", 144, r"\[id-soft: quake-1996\]", "[id-soft: vet-031]"),
    ("library/extractor.py", 282, r"\[id-soft: quake-1996\]", "[id-soft: vet-032]"),
    
    # security.py (library/)
    ("library/security.py", 29, r"\[id-soft: doom-1993\]", "[id-soft: vet-033]"),
    ("library/security.py", 93, r"\[id-soft: quake-1996\]", "[id-soft: vet-034]"),
    ("library/security.py", 130, r"\[id-soft: quake-1996\]", "[id-soft: vet-035]"),
    
    # fts_index.py (library/)
    ("library/fts_index.py", 32, r"\[id-soft: quake-1996\]", "[id-soft: vet-036]"),
    
    # memory_store.py
    ("memory_store.py", 119, r"\[id-soft: quake-1996\]", "[id-soft: vet-037]"),
    
    # monitoring/__init__.py
    ("monitoring/__init__.py", 13, r"\[id-soft: quake-1996\]", "[id-soft: vet-038]"),
    ("monitoring/__init__.py", 15, r"\[id-soft: doom3-2004\]", "[id-soft: vet-039]"),
    
    # observability/__init__.py
    ("observability/__init__.py", 753, r"\[id-soft: doom3-2004\]", "[id-soft: vet-040]"),
    
    # regression_watcher.py
    ("observability/regression_watcher.py", 9, r"\[id-soft: doom3-2004\]", "[id-soft: vet-041]"),
    
    # bleg.py
    ("bleg.py", 14, r"\[id-soft: quake-1996\]", "[id-soft: vet-042]"),
    
    # oracle/__init__.py
    ("oracle/__init__.py", 5, r"\[id-soft: doom-1993\]", "[id-soft: vet-043]"),
    
    # oracle/backends/__init__.py
    ("oracle/backends/__init__.py", 3, r"\[id-soft: quake3-1999\]", "[id-soft: vet-044]"),
    
    # oracle/capability_registry.py
    ("oracle/capability_registry.py", 5, r"\[id-soft: quake3-1999\]", "[id-soft: vet-045]"),
    
    # context_builder.py
    ("oracle/context_builder.py", 272, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    
    # entity_affinity.py
    ("oracle/entity_affinity.py", 18, r"\[id-soft: quake3-1999\]", "[id-soft: vet-047]"),
    
    # entity_registry.py
    ("oracle/entity_registry.py", 86, r"\[id-soft: doom-1993\]", "[id-soft: vet-048]"),
    ("oracle/entity_registry.py", 130, r"\[id-soft: doom-1993\]", "[id-soft: vet-049]"),
    ("oracle/entity_registry.py", 133, r"\[id-soft: quake3-1999\]", "[id-soft: vet-050]"),
    ("oracle/entity_registry.py", 220, r"\[id-soft: doom-1993\]", "[id-soft: vet-051]"),
    ("oracle/entity_registry.py", 225, r"\[id-soft: quake3-1999\]", "[id-soft: vet-052]"),
    ("oracle/entity_registry.py", 306, r"\[id-soft: quake3-1999\]", "[id-soft: vet-053]"),
    ("oracle/entity_registry.py", 559, r"\[id-soft: doom-1993\]", "[id-soft: vet-054]"),
    
    # model_gateway.py
    ("oracle/model_gateway.py", 148, r"\[id-soft: doom-1993\]", "[id-soft: vet-055]"),
    ("oracle/model_gateway.py", 756, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    
    # oracle.py
    ("oracle/oracle.py", 11, r"\[id-soft: quake3-1999\]", "[id-soft: vet-056]"),
    ("oracle/oracle.py", 702, r"\[id-soft: quake3-1999\]", "[id-soft: vet-069]"),
    
    # providers.py
    ("oracle/providers.py", 901, r"\[id-soft: vet-057\]", "[id-soft: vet-057]"),  # Already correct
    ("oracle/providers.py", 912, r"\[id-soft: vet-058\]", "[id-soft: vet-058]"),  # Already correct
    
    # selective_hydration.py
    ("oracle/selective_hydration.py", 8, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    
    # spatial_resolver.py
    ("oracle/spatial_resolver.py", 12, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    
    # semantic_router.py
    ("oracle/semantic_router.py", 8, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    ("oracle/semantic_router.py", 110, r"\[id-soft: doom-1993\]", "[id-soft: vet-046]"),
    
    # soul_distiller.py
    ("oracle/soul_distiller.py", 9, r"\[id-soft: quake-1996\]", "[id-soft: vet-070]"),
    
    # cli/oracle_cli.py
    ("cli/oracle_cli.py", 42, r"\[id-soft: quake-1996\]", "[id-soft: vet-071]"),
    
    # session_lifecycle.py
    ("oracle/session_lifecycle.py", 371, r"\[id-soft: quake-1996\]", "[id-soft: vet-067]"),
    
    # link_p9_runtime.py
    ("oracle/link_p9_runtime.py", 9, r"\[id-soft: doom3-2004\]", "[id-soft: vet-066]"),
    
    # orchestrator.py
    ("oracle/orchestrator.py", 10, r"\[id-soft: quake-1996\]", "[id-soft: vet-068]"),
    
    # library.py
    ("library/library.py", 68, r"\[id-soft: doom-1993\]", "[id-soft: vet-064]"),
    
    # entity_registry.py (mobj dual-linking)
    ("oracle/entity_registry.py", 667, r"\[id-soft: doom-1993\]", "[id-soft: vet-065]"),
    
    # constants.py
    ("constants.py", 16, r"\[id-soft: doom-1993\]", "[id-soft: vet-015]"),
    ("constants.py", 17, r"\[id-soft: quake3-1999\]", "[id-soft: vet-016]"),
    
    # cvar_table.py
    ("cvar_table.py", 11, r"\[id-soft: doom-1993\]", "[id-soft: vet-015]"),
    ("cvar_table.py", 15, r"\[id-soft: quake3-1999\]", "[id-soft: vet-016]"),
    ("cvar_table.py", 51, r"\[id-soft: quake3-1999\]", "[id-soft: vet-016]"),
    ("cvar_table.py", 95, r"\[id-soft: doom-1993\]", "[id-soft: vet-023]"),
    ("cvar_table.py", 101, r"\[id-soft: doom-1993\]", "[id-soft: vet-008]"),
    ("cvar_table.py", 112, r"\[id-soft: doom-1993\]", "[id-soft: vet-015]"),
    ("cvar_table.py", 560, r"\[id-soft: quake3-1999\]", "[id-soft: vet-016]"),
    
    # mcp_runtime.py
    ("mcp_runtime.py", 106, r"\[id-soft: quake-1996\]", "[id-soft: vet-008]"),
    
    # errors.py
    ("errors.py", 0, r"\[id-soft: doom-1993\]", "[id-soft: vet-015]"),  # Need to find actual line
    ("errors.py", 0, r"\[id-soft: quake-1996\]", "[id-soft: vet-008]"),
]

# Also add context-based mappings for files not in the vet log
CONTEXT_MAPPINGS: Dict[str, Dict[str, str]] = {
    "memory_store.py": {
        "Grace Period": "[id-soft: vet-008]",
        "ZONEID": "[id-soft: vet-015]",
        "Lazy Deletion": "[id-soft: vet-008]",
        "Temp Tier": "[id-soft: vet-037]",
    },
    "monitoring/__init__.py": {
        "Surface Cache": "[id-soft: vet-038]",
        "idHeap": "[id-soft: vet-039]",
    },
    "observability/__init__.py": {
        "Event System": "[id-soft: vet-040]",
    },
    "observability/regression_watcher.py": {
        "Event System": "[id-soft: vet-041]",
    },
    "bleg.py": {
        "Right Approximation": "[id-soft: vet-042]",
    },
    "oracle/__init__.py": {
        "WAD System": "[id-soft: vet-043]",
    },
    "oracle/backends/__init__.py": {
        "4-Path VFS": "[id-soft: vet-044]",
    },
    "oracle/capability_registry.py": {
        "VM System": "[id-soft: vet-045]",
    },
    "oracle/context_builder.py": {
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/entity_affinity.py": {
        "Hard-Boundary": "[id-soft: vet-047]",
    },
    "oracle/entity_registry.py": {
        "WAD System": "[id-soft: vet-048]",
        "High-Bit Trick": "[id-soft: vet-049]",
        "Hard-Boundary": "[id-soft: vet-050]",
        "High-Bit Trick": "[id-soft: vet-051]",
        "Hard-Boundary Struct": "[id-soft: vet-052]",
        "Hard-Boundary": "[id-soft: vet-053]",
        "High-Bit Trick": "[id-soft: vet-054]",
        "Mobj Dual-Linking": "[id-soft: vet-065]",
    },
    "oracle/model_gateway.py": {
        "Fixed-Size Active Set": "[id-soft: vet-055]",
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/oracle.py": {
        "Triage Routing": "[id-soft: vet-056]",
        "Speculative Decode": "[id-soft: vet-069]",
    },
    "oracle/providers.py": {
        "Atomic Swap": "[id-soft: vet-057]",
        "Rollback": "[id-soft: vet-058]",
    },
    "oracle/selective_hydration.py": {
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/spatial_resolver.py": {
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/semantic_router.py": {
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/soul_distiller.py": {
        "Save-game pattern": "[id-soft: vet-070]",
    },
    "cli/oracle_cli.py": {
        "netchan header": "[id-soft: vet-071]",
    },
    "oracle/session_lifecycle.py": {
        "Cache Tier": "[id-soft: vet-067]",
    },
    "oracle/link_p9_runtime.py": {
        "idEntity event system": "[id-soft: vet-066]",
    },
    "oracle/orchestrator.py": {
        "Dedicated Server Model": "[id-soft: vet-068]",
    },
    "library/library.py": {
        "FTS5 Index Rebuild": "[id-soft: vet-064]",
    },
    "library/api_clients.py": {
        "Hard-Boundary Struct": "[id-soft: vet-025]",
        "Hard-Boundary": "[id-soft: vet-026]",
        "WAD System": "[id-soft: vet-027]",
        "WAD System": "[id-soft: vet-028]",
    },
    "library/coordinator.py": {
        "Job-Worker Queue": "[id-soft: vet-029]",
    },
    "library/extractor.py": {
        "SSRF Gate": "[id-soft: vet-030]",
        "Size Gate": "[id-soft: vet-031]",
        "Path Scope Gate": "[id-soft: vet-032]",
    },
    "library/security.py": {
        "SSRF Guard": "[id-soft: vet-033]",
        "Path Scope Guard": "[id-soft: vet-034]",
        "Download Size Guard": "[id-soft: vet-035]",
    },
    "library/fts_index.py": {
        "WAL journal mode": "[id-soft: vet-036]",
    },
    "library/rate_limiter.py": {
        "Netchan": "[id-soft: vet-009]",
    },
    "cvar_table.py": {
        "ZONEID": "[id-soft: vet-015]",
        "Cvar System": "[id-soft: vet-016]",
        "Precomputed Lookup": "[id-soft: vet-023]",
        "Lazy Deletion": "[id-soft: vet-008]",
    },
    "constants.py": {
        "ZONEID": "[id-soft: vet-015]",
        "Cvar System": "[id-soft: vet-016]",
    },
    "mcp_runtime.py": {
        "Zone Memory": "[id-soft: vet-008]",
    },
    "errors.py": {
        "Lazy Deletion": "[id-soft: vet-008]",
        "Grace Period": "[id-soft: vet-008]",
        "ZONEID": "[id-soft: vet-015]",
    },
    "workers/background_researcher/searxng_client.py": {
        "WAD System": "[id-soft: vet-027]",
    },
    "library/extractor.py": {
        "SSRFGuard": "[id-soft: vet-033]",
        "DownloadSizeGuard": "[id-soft: vet-035]",
        "PathScopeGuard": "[id-soft: vet-034]",
    },
    "library/coordinator.py": {
        "Grace Period": "[id-soft: vet-008]",
    },
    "cli/oracle_cli.py": {
        "netchan header": "[id-soft: vet-071]",
        "netchan": "[id-soft: vet-071]",
    },
    "state/cas.py": {
        "ZONEID": "[id-soft: vet-015]",
    },
    "observability/ufl.py": {
        "Zone Memory": "[id-soft: vet-008]",
    },
    "observability/metrics_db.py": {
        "Event System": "[id-soft: vet-040]",
        "cvar": "[id-soft: vet-016]",
    },
    "observability/__init__.py": {
        "Event System": "[id-soft: vet-040]",
        "Zone Memory": "[id-soft: vet-008]",
        "ZONEID": "[id-soft: vet-015]",
    },
    "observability/regression_watcher.py": {
        "Thinker Chain": "[id-soft: vet-011]",
        "Event System": "[id-soft: vet-041]",
    },
    "observability/sovereignty.py": {
        "cvar": "[id-soft: vet-016]",
    },
    "observability/token_ledger.py": {
        "Cvar System": "[id-soft: vet-016]",
    },
    "vault/key_vault.py": {
        "Zone Memory": "[id-soft: vet-008]",
    },
    "vault/crypto.py": {
        "Zone Memory": "[id-soft: vet-008]",
    },
    "governance/sovereign_vetter.py": {
        "Heritage vet log": "[id-soft: vet-XXX]",
    },
    "oracle/entity_workspace.py": {
        "QuakeC Flat Entity": "[id-soft: vet-011]",
        "Precomputed Lookup": "[id-soft: vet-023]",
    },
    "oracle/session_lifecycle.py": {
        "4-Tier Memory": "[id-soft: vet-009]",
        "Lazy Deletion": "[id-soft: vet-008]",
        "Cache Tier": "[id-soft: vet-067]",
    },
    "oracle/resource_guard.py": {
        "ZONEID": "[id-soft: vet-015]",
    },
    "oracle/cpu_optimizer.py": {
        "FISR Principle": "[id-soft: vet-002]",
    },
    "oracle/soul_distiller.py": {
        "WAD System": "[id-soft: vet-043]",
    },
    "oracle/backends/remote_provider.py": {
        "cvar": "[id-soft: vet-016]",
        "Precomputed Lookup": "[id-soft: vet-023]",
    },
    "oracle/backends/antigravity_provider.py": {
        "Hard-Boundary": "[id-soft: vet-025]",
    },
    "oracle/soul_validator.py": {
        "ZONEID": "[id-soft: vet-015]",
        "Lazy Deletion": "[id-soft: vet-008]",
    },
    "oracle/session_manager.py": {
        "4-Tier Memory": "[id-soft: vet-009]",
        "Grace Period": "[id-soft: vet-008]",
    },
    "oracle/link_p9_runtime.py": {
        "ZONEID": "[id-soft: vet-015]",
        "Thinker chain": "[id-soft: vet-011]",
    },
    "oracle/feed_utils.py": {
        "ZONEID": "[id-soft: vet-015]",
    },
    "oracle/search_providers.py": {
        "Right Approximation": "[id-soft: vet-002]",
    },
    "oracle/oracle.py": {
        "Oracle Summoning Pattern": "[id-soft: vet-056]",
        "Memory Zone": "[id-soft: vet-009]",
        "cvar pattern": "[id-soft: vet-016]",
        "Save-game pattern": "[id-soft: vet-070]",
    },
    "oracle/wad_loader.py": {
        "WAD System": "[id-soft: vet-043]",
        "4-Path VFS": "[id-soft: vet-044]",
        "ZONEID": "[id-soft: vet-015]",
    },
    "oracle/health_monitor.py": {
        "ZONEID": "[id-soft: vet-015]",
    },
    "oracle/context_builder.py": {
        "Zone Memory": "[id-soft: vet-008]",
        "Precomputed Lookup": "[id-soft: vet-023]",
        "BSP Culling": "[id-soft: vet-046]",
    },
    "oracle/model_gateway.py": {
        "cvar pattern": "[id-soft: vet-016]",
    },
    "oracle/headroom.py": {
        "WAD System": "[id-soft: vet-043]",
    },
    "oracle/providers.py": {
        "Cvar System": "[id-soft: vet-016]",
        "Right Approximation": "[id-soft: vet-002]",
    },
    "oracle/subagent_dispatcher.py": {
        "ZONEID": "[id-soft: vet-015]",
        "GAME-YEAR": "[id-soft: vet-XXX]",
    },
    "oracle/entity_affinity.py": {
        "cvar pattern": "[id-soft: vet-016]",
    },
    "oracle/skeptical_verifier.py": {
        "ZONEID": "[id-soft: vet-015]",
    },
    "oracle/capability_registry.py": {
        "Multi-Index Entity": "[id-soft: vet-010]",
    },
    "oracle/hierarchy.py": {
        "Hard-Boundary Struct": "[id-soft: vet-047]",
    },
    "oracle/sentinel.py": {
        "GAME-YEAR": "[id-soft: vet-XXX]",
    },
    "oracle/soul_edit_history.py": {
        "Lazy Deletion": "[id-soft: vet-008]",
        "Realloc Grace": "[id-soft: vet-008]",
    },
    "oracle/handoff.py": {
        "Grace Period": "[id-soft: vet-008]",
    },
    "oracle/semantic_router.py": {
        "Precomputed Lookup": "[id-soft: vet-023]",
    },
    "oracle/selective_hydration.py": {
        "BSP Culling": "[id-soft: vet-046]",
    },
}


def migrate_file(file_path: Path, dry_run: bool = True) -> int:
    """Migrate a single file, return number of changes."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0
    
    lines = content.splitlines(keepends=True)
    changes = 0
    
    # Get relative path for mapping lookup
    try:
        rel_path = file_path.relative_to(Path("src/omega"))
    except ValueError:
        rel_path = file_path
    
    rel_str = str(rel_path).replace("\\", "/")
    
    # Check precise mappings first
    for mapping_file, line_num, pattern, vet_tag in PRECISE_MAPPINGS:
        if rel_str == mapping_file or rel_str.endswith("/" + mapping_file):
            # Line numbers are 1-indexed in the vet log
            idx = line_num - 1
            if 0 <= idx < len(lines):
                line = lines[idx]
                if re.search(pattern, line):
                    new_line = re.sub(pattern, vet_tag, line)
                    if new_line != line:
                        lines[idx] = new_line
                        changes += 1
                        print(f"  {rel_str}:{line_num} - {line.strip()[:80]} -> {vet_tag}")
    
    # Then apply context-based mappings for remaining legacy tags
    if rel_str in CONTEXT_MAPPINGS:
        context_map = CONTEXT_MAPPINGS[rel_str]
        for i, line in enumerate(lines):
            # Skip if already migrated (contains vet-)
            if "[id-soft: vet-" in line:
                continue
            
            # Check for legacy patterns
            for context_key, vet_tag in context_map.items():
                legacy_patterns = [
                    r"\[id-soft: doom-1993\]",
                    r"\[id-soft: quake-1996\]",
                    r"\[id-soft: quake3-1999\]",
                    r"\[id-soft: doom3-2004\]",
                    r"\[id-soft: doom3bfg-2012\]",
                ]
                for pattern in legacy_patterns:
                    if re.search(pattern, line) and context_key.lower() in line.lower():
                        new_line = re.sub(pattern, vet_tag, line)
                        if new_line != line:
                            lines[i] = new_line
                            changes += 1
                            print(f"  {rel_str}:{i+1} (context: {context_key}) - {line.strip()[:80]} -> {vet_tag}")
                        break
    
    if changes > 0 and not dry_run:
        file_path.write_text("".join(lines), encoding="utf-8")
    
    return changes


def main():
    import sys
    dry_run = "--apply" not in sys.argv
    
    if dry_run:
        print("=== DRY RUN (use --apply to write changes) ===\n")
    
    src_dir = Path("src/omega")
    total_changes = 0
    
    for py_file in src_dir.rglob("*.py"):
        # Skip test files and __pycache__
        if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
            continue
        
        changes = migrate_file(py_file, dry_run)
        if changes > 0:
            total_changes += changes
            print(f"  {py_file.relative_to(src_dir)}: {changes} changes")
    
    print(f"\n=== Total changes: {total_changes} ===")
    
    if dry_run:
        print("\nRun with --apply to write changes")


if __name__ == "__main__":
    main()