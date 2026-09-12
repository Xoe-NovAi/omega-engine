#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Heritage Tag Migration Script
Converts legacy [id-soft: GAME-YEAR] tags to [id-soft: vet-XXX] format
based on HERITAGE_VET_LOG.md mappings.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping from (file_pattern, legacy_tag, context_keyword) -> vet_tag
# This uses file location and context to determine the correct vet number
MIGRATION_RULES: List[Tuple[str, str, str, str]] = [
    # === monitoring/__init__.py ===
    ("monitoring/__init__.py", r"\[id-soft: quake-1996\]", "Surface Cache", "[id-soft: vet-038]"),
    ("monitoring/__init__.py", r"\[id-soft: doom3-2004\]", "idHeap", "[id-soft: vet-039]"),
    
    # === constants.py ===
    ("constants.py", r"\[id-soft: doom-1993\]", "ZONEID", "[id-soft: vet-015]"),
    ("constants.py", r"\[id-soft: quake3-1999\]", "Cvar System", "[id-soft: vet-016]"),
    
    # === cvar_table.py ===
    ("cvar_table.py", r"\[id-soft: doom-1993\]", "ZONEID", "[id-soft: vet-015]"),
    ("cvar_table.py", r"\[id-soft: quake3-1999\]", "Cvar System", "[id-soft: vet-016]"),
    ("cvar_table.py", r"\[id-soft: doom-1993\]", "Precomputed Lookup", "[id-soft: vet-023]"),
    ("cvar_table.py", r"\[id-soft: doom-1993\]", "Lazy Deletion", "[id-soft: vet-008]"),
    
    # === memory_store.py ===
    ("memory_store.py", r"\[id-soft: quake-1996\]", "Grace Period", "[id-soft: vet-008]"),
    ("memory_store.py", r"\[id-soft: doom-1993\]", "ZONEID", "[id-soft: vet-015]"),
    ("memory_store.py", r"\[id-soft: doom-1993\]", "Lazy Deletion", "[id-soft: vet-008]"),
    ("memory_store.py", r"\[id-soft: quake-1996\]", "Temp Tier", "[id-soft: vet-037]"),
    ("memory_store.py", r"\[id-soft: doom-1993\]", "Lazy Deletion", "[id-soft: vet-008]"),
    
    # === mcp_runtime.py ===
    ("mcp_runtime.py", r"\[id-soft: quake-1996\]", "Zone Memory", "[id-soft: vet-008]"),
    
    # === governance/sovereign_vetter.py ===
    ("governance/sovereign_vetter.py", r"\[id-soft: GAME-YEAR\]", "", "[id-soft: vet-XXX]"),  # placeholder
    
    # === oracle/__init__.py ===
    ("oracle/__init__.py", r"\[id-soft: doom-1993\]", "WAD System", "[id-soft: vet-043]"),
    
    # === oracle/backends/__init__.py ===
    ("oracle/backends/__init__.py", r"\[id-soft: quake3-1999\]", "4-Path VFS", "[id-soft: vet-044]"),
    
    # === oracle/capability_registry.py ===
    ("oracle/capability_registry.py", r"\[id-soft: quake3-1999\]", "VM System", "[id-soft: vet-045]"),
    
    # === oracle/context_builder.py ===
    ("oracle/context_builder.py", r"\[id-soft: doom-1993\]", "BSP Culling", "[id-soft: vet-046]"),
    
    # === oracle/entity_affinity.py ===
    ("oracle/entity_affinity.py", r"\[id-soft: quake3-1999\]", "Hard-Boundary", "[id-soft: vet-047]"),
    
    # === oracle/entity_registry.py ===
    ("oracle/entity_registry.py", r"\[id-soft: doom-1993\]", "WAD System", "[id-soft: vet-048]"),
    ("oracle/entity_registry.py", r"\[id-soft: doom-1993\]", "High-Bit Trick", "[id-soft: vet-049]"),
    ("oracle/entity_registry.py", r"\[id-soft: quake3-1999\]", "Hard-Boundary", "[id-soft: vet-050]"),
    ("oracle/entity_registry.py", r"\[id-soft: doom-1993\]", "High-Bit Trick", "[id-soft: vet-051]"),
    ("oracle/entity_registry.py", r"\[id-soft: quake3-1999\]", "Hard-Boundary Struct", "[id-soft: vet-052]"),
    ("oracle/entity_registry.py", r"\[id-soft: quake3-1999\]", "Hard-Boundary", "[id-soft: vet-053]"),
    ("oracle/entity_registry.py", r"\[id-soft: doom-1993\]", "High-Bit Trick", "[id-soft: vet-054]"),
    ("oracle/entity_registry.py", r"\[id-soft: doom-1993\]", "Dual-Linking", "[id-soft: vet-065]"),
    
    # === oracle/model_gateway.py ===
    ("oracle/model_gateway.py", r"\[id-soft: doom-1993\]", "Fixed-Size Active Set", "[id-soft: vet-055]"),
    ("oracle/model_gateway.py", r"\[id-soft: quake3-1999\]", "Triage Routing", "[id-soft: vet-056]"),
    ("oracle/model_gateway.py", r"\[id-soft: doom-1993\]", "BSP Culling", "[id-soft: vet-046]"),
    ("oracle/model_gateway.py", r"\[id-soft: vet-057\]", "Atomic Swap", "[id-soft: vet-057]"),
    ("oracle/model_gateway.py", r"\[id-soft: vet-058\]", "Rollback", "[id-soft: vet-058]"),
    
    # === oracle/oracle.py ===
    ("oracle/oracle.py", r"\[id-soft: quake3-1999\]", "Speculative Decode", "[id-soft: vet-069]"),
    ("oracle/oracle.py", r"\[id-soft: quake3-1999\]", "Triage Routing", "[id-soft: vet-056]"),
    
    # === oracle/providers.py ===
    ("oracle/providers.py", r"\[id-soft: vet-057\]", "Atomic Swap", "[id-soft: vet-057]"),
    ("oracle/providers.py", r"\[id-soft: vet-058\]", "Rollback", "[id-soft: vet-058]"),
    
    # === oracle/selective_hydration.py ===
    ("oracle/selective_hydration.py", r"\[id-soft: doom-1993\]", "BSP Culling", "[id-soft: vet-046]"),
    
    # === oracle/semantic_router.py ===
    ("oracle/semantic_router.py", r"\[id-soft: doom-1993\]", "BSP Culling", "[id-soft: vet-046]"),
    
    # === oracle/session_lifecycle.py ===
    ("oracle/session_lifecycle.py", r"\[id-soft: quake-1996\]", "Cache Tier", "[id-soft: vet-067]"),
    ("oracle/session_lifecycle.py", r"\[id-soft: quake-1996\]", "Save-game", "[id-soft: vet-070]"),
    
    # === oracle/soul_distiller.py (DELETED 2026-07-30 — Carmack scrap) ===
    
    # === oracle/spatial_resolver.py ===
    ("oracle/spatial_resolver.py", r"\[id-soft: doom-1993\]", "BSP Culling", "[id-soft: vet-046]"),
    
    # === oracle/skeptical_verifier.py ===
    ("oracle/skeptical_verifier.py", r"\[id-soft: doom3-2004\]", "Knowledge Leak Detection", "[id-soft: vet-022]"),
    
    # === cli/oracle_cli.py ===
    ("cli/oracle_cli.py", r"\[id-soft: quake-1996\]", "netchan header", "[id-soft: vet-071]"),
    
    # === observability/__init__.py ===
    ("observability/__init__.py", r"\[id-soft: doom3-2004\]", "Event System", "[id-soft: vet-040]"),
    
    # === regression_watcher.py ===
    ("regression_watcher.py", r"\[id-soft: doom3-2004\]", "Event System", "[id-soft: vet-041]"),
    
    # === bleg.py ===
    ("bleg.py", r"\[id-soft: quake-1996\]", "Right Approximation", "[id-soft: vet-042]"),
    
    # === library/library.py ===
    ("library/library.py", r"\[id-soft: doom-1993\]", "FTS5 Index Rebuild", "[id-soft: vet-064]"),
    
    # === orchestrator.py ===
    ("orchestrator.py", r"\[id-soft: quake-1996\]", "Dedicated Server Model", "[id-soft: vet-068]"),
    ("orchestrator.py", r"\[id-soft: doom3bfg-2012\]", "Job-Worker Queue", "[id-soft: vet-029]"),
    
    # === coordinator.py ===
    ("coordinator.py", r"\[id-soft: doom3bfg-2012\]", "Job-Worker Queue", "[id-soft: vet-029]"),
    
    # === extractor.py ===
    ("extractor.py", r"\[id-soft: doom-1993\]", "SSRF Gate", "[id-soft: vet-030]"),
    ("extractor.py", r"\[id-soft: quake-1996\]", "Size Gate", "[id-soft: vet-031]"),
    ("extractor.py", r"\[id-soft: quake-1996\]", "Path Scope Gate", "[id-soft: vet-032]"),
    
    # === security.py ===
    ("security.py", r"\[id-soft: doom-1993\]", "SSRF Guard", "[id-soft: vet-033]"),
    ("security.py", r"\[id-soft: quake-1996\]", "Path Scope Guard", "[id-soft: vet-034]"),
    ("security.py", r"\[id-soft: quake-1996\]", "Download Size Guard", "[id-soft: vet-035]"),
    
    # === fts_index.py ===
    ("fts_index.py", r"\[id-soft: quake-1996\]", "WAL journal mode", "[id-soft: vet-036]"),
    
    # === link_p9_runtime.py ===
    ("link_p9_runtime.py", r"\[id-soft: doom3-2004\]", "idEntity event system", "[id-soft: vet-066]"),
    
    # === api_clients.py ===
    ("api_clients.py", r"\[id-soft: quake3-1999\]", "Hard-Boundary Struct", "[id-soft: vet-025]"),
    ("api_clients.py", r"\[id-soft: quake-1996\]", "Hard-Boundary", "[id-soft: vet-026]"),
    ("api_clients.py", r"\[id-soft: doom-1993\]", "WAD System", "[id-soft: vet-027]"),
    ("api_clients.py", r"\[id-soft: doom-1993\]", "WAD System", "[id-soft: vet-028]"),
]

# Fallback mapping by legacy tag only (when context doesn't match)
FALLBACK_MAPPING: Dict[str, str] = {
    "[id-soft: doom-1993]": "[id-soft: vet-015]",  # Default to ZONEID
    "[id-soft: quake-1996]": "[id-soft: vet-008]",  # Default to Zone Memory
    "[id-soft: quake3-1999]": "[id-soft: vet-009]",  # Default to Netchan
    "[id-soft: doom3-2004]": "[id-soft: vet-039]",  # Default to idHeap
    "[id-soft: doom3bfg-2012]": "[id-soft: vet-017]",  # Default to Job-Worker
    "[id-soft: GAME-YEAR]": "[id-soft: vet-XXX]",  # Placeholder
}


def migrate_file(filepath: Path, dry_run: bool = True) -> Tuple[int, List[str]]:
    """Migrate heritage tags in a single file."""
    content = filepath.read_text(encoding="utf-8")
    original_content = content
    changes = []
    
    # Get relative path for rule matching
    rel_path = str(filepath.relative_to(Path("src/omega")))
    
    # Apply specific rules first
    for file_pattern, legacy_pattern, context_keyword, vet_tag in MIGRATION_RULES:
        if file_pattern in rel_path:
            # Find all occurrences of this legacy pattern in this file
            pattern = re.compile(re.escape(legacy_pattern) + r"[^\]]*" + re.escape(context_keyword) if context_keyword else re.escape(legacy_pattern))
            
            def replace_fn(match):
                old = match.group(0)
                new = old.replace(legacy_pattern, vet_tag)
                changes.append(f"  {old.strip()} -> {new.strip()}")
                return new
            
            content = pattern.sub(replace_fn, content)
    
    # Apply fallback for any remaining legacy tags
    for legacy_tag, vet_tag in FALLBACK_MAPPING.items():
        if legacy_tag in content and legacy_tag != "[id-soft: GAME-YEAR]":
            # Only replace if not already a vet tag
            pattern = re.compile(re.escape(legacy_tag) + r"(?!\s*vet-)")
            def fallback_replace(match):
                old = match.group(0)
                new = old.replace(legacy_tag, vet_tag)
                changes.append(f"  {old.strip()} -> {new.strip()} (fallback)")
                return new
            content = pattern.sub(fallback_replace, content)
    
    if content != original_content and not dry_run:
        filepath.write_text(content, encoding="utf-8")
    
    return len(changes), changes


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate heritage tags to vet format")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--file", help="Process specific file only")
    args = parser.parse_args()
    
    src_root = Path("src/omega")
    if not src_root.exists():
        print("Error: src/omega not found")
        return 1
    
    if args.file:
        files = [src_root / args.file]
    else:
        files = list(src_root.rglob("*.py"))
    
    total_changes = 0
    total_files = 0
    
    for filepath in files:
        if "__pycache__" in str(filepath):
            continue
        changes, details = migrate_file(filepath, dry_run=not args.apply)
        if changes > 0:
            total_changes += changes
            total_files += 1
            print(f"\n{filepath.relative_to(src_root)}: {changes} changes")
            for d in details:
                print(d)
    
    print(f"\n{'='*50}")
    print(f"Total: {total_files} files, {total_changes} changes")
    if not args.apply:
        print("DRY RUN - use --apply to write changes")
    
    return 0


if __name__ == "__main__":
    main()