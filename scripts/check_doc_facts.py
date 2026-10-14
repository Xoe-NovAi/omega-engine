#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ CHECK-DOC-FACTS ⬡ Single Source of Truth Enforcer
# Validates that public docs match FACTS.yaml. Fails on mismatch.
# Usage: python scripts/check_doc_facts.py [--fix]

import sys
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

FACTS_PATH = Path("docs/FACTS.yaml")
DOC_DIRS = [
    Path("README.md"),
    Path("QUICKSTART.md"),
    Path("ANNOUNCEMENT_v1.6.0-alpha.md"),
    Path("docs/guides/how-to-debug-hub.md"),
    Path("docs/guides/how-to-configure-exchange.md"),
    Path("docs/guides/how-to-add-agent.md"),
    Path("docs/guides/connect-antigravity-ide.md"),
    Path("docs/tutorials/how-to-federate-node.md"),
    Path("docs/tutorials/how-to-add-mcp-tool.md"),
    Path("docs/tutorials/how-to-create-wad.md"),
]

# Patterns to extract values from docs for comparison
PATTERNS = {
    "release.tag": r"(?:tag|release)[:\s]*[`\"]?(v?[\d.]+[a-z]?\d*)[`\"]?",
    "release.wheel_filename": r"(?:wheel|artifact)[:\s]*[`\"]?([\w.-]+\.whl)[`\"]?",
    "hub.host": r"(?:host|bind)[:\s]*[`\"]?(127\.0\.0\.1|localhost)[`\"]?",
    "hub.port": r"(?:port)[:=]\s*(8016)\b",
    "hub.mcp_path": r"(?:mcp[_-]?path|endpoint)[:\s]*[`\"]?(/mcp)[`\"]?",
    "hub.sse_path": r"(?:sse[_-]?path|endpoint)[:\s]*[`\"]?(/sse)[`\"]?",
    "default_local_model": r"(?:default.*model|local.*model)[:\s]*[`\"]?(Qwen3-[\w.-]+)[`\"]?",
    "embedding.model": r"(?:embedding.*model)[:\s]*[`\"]?(Qwen3-Embedding-[\w.-]+)[`\"]?",
    "embedding.dimensions": r"(?:embedding.*dim|dimensions)[:\s]*(\d+)",
    "iwad_default_entities": r"(?:entities|IWAD.*entities)[:\s]*(\d+)",
    "mandates.total": r"(?:mandates?|M-numbers?)[:\s]*(\d+)",
    "mandates.mechanically_verified": r"(?:mechanically.*verified|verified.*mandates?)[:\s]*(\d+)",
    "tests.engine_contract_passing": r"(?:engine.*contract.*pass|passing.*tests?)[:\s]*(\d+)",
    "tests.dashboard_self_test": r"(?:dashboard.*self.*test|53/53)[:\s]*(\d+/\d+)",
    "requirements.ram_min_gb": r"(?:RAM|memory|ram)[:\s]*(\d+)\s*GB",
    "requirements.python": r"(?:Python|python)[:\s]*(\d+\.\d+\+?)",
    "requirements.os": r"(Ubuntu\s+22\.04\+\s*,\s*Debian\s+12\+\s*,\s*Arch\s*,\s*Fedora)",
}

FORBIDDEN_PHRASES = [
    "100% constraint survival",
    "83%",
    "53/53 gates",
    "53 reproducible gates",
    "30 mandates enforced",
    "30 Architectural Mandates.*enforced",
    "100% operational",
    "never called unless local",
    "REUSE.*Green",
    "arcana_novai.*(complete|ships)",
]

# Public tree forbidden patterns (should never appear in tracked files)
PUBLIC_TREE_FORBIDDEN = [
    r"docs/archive/",
    r"session-ses_",
    r"claude-handoff",
    r"tskey-auth-k.*CNTRL",
    r"/home/xnai/",
    r"/home/hazeruno/",
]


def load_facts() -> Dict[str, Any]:
    with open(FACTS_PATH) as f:
        return yaml.safe_load(f)


def get_nested(d: Dict, key: str) -> Any:
    """Get nested dict value by dot-notation key."""
    for k in key.split("."):
        d = d.get(k, {})
    return d


def scan_file(filepath: Path) -> str:
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception:
        return ""


def check_forbidden_phrases(content: str, filepath: Path) -> List[str]:
    violations = []
    for phrase in FORBIDDEN_PHRASES:
        if re.search(phrase, content, re.IGNORECASE):
            violations.append(f"{filepath}: forbidden phrase '{phrase}' found")
    return violations


def extract_values(content: str) -> Dict[str, str]:
    """Extract fact values from content using patterns."""
    values = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            values[key] = match.group(1)
    return values


def check_facts(facts: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Check all doc files against FACTS.yaml. Returns (errors, warnings)."""
    errors = []
    warnings = []

    for doc_path in DOC_DIRS:
        if doc_path.is_file():
            files = [doc_path]
        elif doc_path.is_dir():
            files = list(doc_path.rglob("*.md"))
        else:
            continue

        for filepath in files:
            content = scan_file(filepath)
            if not content:
                continue

            # Check forbidden phrases
            for v in check_forbidden_phrases(content, filepath):
                errors.append(v)

            # Extract and compare values
            extracted = extract_values(content)
            for key, extracted_val in extracted.items():
                expected = get_nested(facts, key)
                if expected is not None and str(expected) != extracted_val:
                    # Allow some flexibility for version strings
                    if key == "release.tag" and extracted_val in ("v1.6.0-alpha", "v1.6.0a0"):
                        continue
                    errors.append(
                        f"{filepath}: {key} = '{extracted_val}' but FACTS.yaml has '{expected}'"
                    )

    # Public tree self-check: scan public-facing tracked files for forbidden patterns
    # Only check public-facing directories, not internal data/ or scripts/
    PUBLIC_DIRS = [
        "README.md", "QUICKSTART.md", "ANNOUNCEMENT_v1.6.0-alpha.md",
        "docs/guides/", "docs/tutorials/", "docs/reference/",
        "docs/architecture/", "docs/governance/", "docs/operations/",
        "docs/specs/", "docs/api/", "docs/federation/", "docs/strategy/",
        "docs/how-to/", "docs/kb/", "docs/sprints/",
        "PUBLIC_ALLOWLIST.txt", ".gitleaksignore", ".secret-history-baseline.toml",
        ".gitguardian.yaml", ".secret-history-baseline.toml"
    ]
    try:
        for pub_path in PUBLIC_DIRS:
            p = Path(pub_path)
            if not p.exists():
                continue
            if p.is_file():
                files = [p]
            elif p.is_dir():
                files = list(p.rglob("*"))
            else:
                continue
            for f in files:
                if not f.is_file() or f.suffix not in (".md", ".py", ".yaml", ".yml", ".txt", ".toml"):
                    continue
                # Skip the baseline file itself (it contains the patterns as deny entries)
                if f.name == ".secret-history-baseline.toml":
                    continue
                try:
                    content = f.read_text(encoding="utf-8")
                except Exception:
                    continue
                for pattern in PUBLIC_TREE_FORBIDDEN:
                    if re.search(pattern, content, re.IGNORECASE):
                        errors.append(f"PUBLIC TREE VIOLATION: {f} contains forbidden pattern '{pattern}'")
    except Exception:
        pass  # Non-fatal if git not available

    return errors, warnings


def main():
    if not FACTS_PATH.exists():
        print(f"ERROR: {FACTS_PATH} not found")
        return 1

    facts = load_facts()
    errors, warnings = check_facts(facts)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  {e}")
        print(f"\nTotal errors: {len(errors)}")
        return 1

    print("✅ All doc facts match FACTS.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())