#!/usr/bin/env python3
"""
C3 Gitleaks Mirror — Standalone Secret Detection for Pre-Commit/CI

[INST-1-C3] Per DEBUT_REMEDIATION_MANUAL §5 P0-1c:
- Catches sk-, csk-, AIza, ghp_, xai-, age-secret-key patterns
- Stdin- or filename-based input
- Exits 1 on detection, 0 on clean
- Designed as a BACKUP to gitleaks (works without network)
- Honors M24 venv sovereignty: pure stdlib

Pattern Authority (per DEBUT §5 P0-1d):
- sk-      — OpenAI/Cerebras-style
- csk-     — Cerebras-style
- AIza     — Google API key
- ghp_     — GitHub personal access token
- xai-     — xAI/Grok
- age-     — Age encryption secret
- age-secret-key — Age secret key file content

Usage:
    python scripts/ci_secret_scan.py <file>
    python scripts/ci_secret_scan.py --stdin
    find . -name '*.py' | xargs python scripts/ci_secret_scan.py

Exit codes:
    0 — clean
    1 — secret(s) detected
    2 — error (file unreadable, bad args)
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple


# Pattern catalogue (canonical, per DEBUT §5 P0-1d)
SECRET_PATTERNS: List[Tuple[str, str, str]] = [
    # (regex, name, severity)
    (r"\bsk-[A-Za-z0-9]{20,}\b", "OpenAI-style key (sk-)", "CRITICAL"),
    (r"\bcsk-[A-Za-z0-9]{20,}\b", "Cerebras-style key (csk-)", "CRITICAL"),
    (r"\bAIza[A-Za-z0-9_\-]{35,}\b", "Google API key (AIza)", "CRITICAL"),
    (r"\bghp_[A-Za-z0-9]{36,}\b", "GitHub PAT (ghp_)", "CRITICAL"),
    (r"\bxai-[A-Za-z0-9]{20,}\b", "xAI/Grok key (xai-)", "CRITICAL"),
    # Age secret key — actual format is "AGE-SECRET-KEY-1..." base64 (50+ chars total).
    # Be strict to avoid matching the literal string in docs.
    (r"\bAGE-SECRET-KEY-[A-Z0-9]{50,}\b", "Age secret key (AGE-SECRET-KEY-1...)", "CRITICAL"),
    # Bearer-style tokens (high-entropy 40+)
    (r"\bsk_(live|test)_[A-Za-z0-9]{24,}\b", "Stripe key", "CRITICAL"),
    (r"\bxoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{24,}\b", "Slack token", "CRITICAL"),
    # Generic AWS
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS Access Key", "CRITICAL"),
]

# Allowlist (false-positive guards) — ONLY for KNOWN test fixtures, not real patterns.
# Per DEBUT §5 P0-1c, planted sk-/csk-/AIza must FAIL. No allowlist for real patterns.
FALSE_POSITIVE_ALLOWLIST = {
    # None for now. Any future test fixture should use a clearly-tagged pattern
    # (e.g., "sk-TEST-FIXTURE-...") and add to this list.
}


def scan_text(text: str, source_name: str = "<input>") -> List[dict]:
    """Scan text for secrets. Returns list of findings."""
    findings = []
    for pattern, name, severity in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            matched = match.group(0)
            if matched in FALSE_POSITIVE_ALLOWLIST:
                continue
            # Compute line number
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_no = text[:line_start].count("\n") + 1
            findings.append({
                "file": source_name,
                "line": line_no,
                "pattern": name,
                "severity": severity,
                "match": matched[:16] + "***REDACTED***",  # Redact
            })
    return findings


def scan_file(path: Path) -> List[dict]:
    """Scan a file for secrets."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return scan_text(text, str(path))
    except Exception as e:
        return [{
            "file": str(path),
            "line": 0,
            "pattern": "READ_ERROR",
            "severity": "ERROR",
            "match": str(e),
        }]


def main() -> int:
    parser = argparse.ArgumentParser(description="C3 Secret Scanner (gitleaks mirror)")
    parser.add_argument("files", nargs="*", help="Files to scan (default: stdin via --stdin)")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[
            ".venv/",
            "node_modules/",
            "data/",
            ".git/",
            "docs/archive/",
            "tests/fixtures/",
            # Self-exclude: this script contains literal pattern strings.
            "scripts/ci_secret_scan.py",
        ],
        help="Path prefixes to exclude (can be repeated)",
    )
    args = parser.parse_args()

    all_findings: List[dict] = []

    if args.stdin:
        text = sys.stdin.read()
        all_findings.extend(scan_text(text, "<stdin>"))
    elif args.files:
        for fpath in args.files:
            path = Path(fpath)
            # Skip excluded prefixes
            if any(str(path).startswith(excl) for excl in args.exclude):
                continue
            all_findings.extend(scan_file(path))
    else:
        print("ERROR: provide files or --stdin", file=sys.stderr)
        return 2

    if all_findings:
        print(f"❌ C3 SECRET SCAN FAILED: {len(all_findings)} finding(s)")
        print("─" * 60)
        for f in all_findings:
            print(
                f"  [{f['severity']}] {f['file']}:{f['line']} — {f['pattern']}"
            )
            print(f"    match: {f['match']}")
        print("─" * 60)
        print("DO NOT COMMIT. Rotate the secret at the provider console first.")
        return 1

    print("✅ C3 SECRET SCAN: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
