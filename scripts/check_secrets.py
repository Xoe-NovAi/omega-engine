#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 John Carmack <john@omega-engine.ai>
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

# --- Patterns (fail-closed: any new pattern defaults to scanning everything) ---
# Each pattern: (id, regex, severity, description)
SECRET_PATTERNS: list[tuple[str, str, str, str]] = [
    # Google OAuth public client secret (allowlisted via secrets-public.toml)
    ("google-oauth-client-secret", r"GOCSPX-[A-Za-z0-9_\-]{20,}", "high",
     "Google OAuth client secret (GOCSPX-)"),
    # AWS Access Key
    ("aws-access-key", r"AKIA[0-9A-Z]{16}", "critical",
     "AWS Access Key ID"),
    # GitHub PAT (classic)
    ("github-pat", r"ghp_[A-Za-z0-9]{36,}", "critical",
     "GitHub Personal Access Token (classic)"),
    # GitHub fine-grained PAT
    ("github-fine-grained-pat", r"github_pat_[A-Za-z0-9_]{82}", "critical",
     "GitHub Fine-Grained Personal Access Token"),
    # GitHub OAuth
    ("github-oauth", r"gho_[A-Za-z0-9]{36,}", "critical",
     "GitHub OAuth Access Token"),
    # Anthropic API key
    ("anthropic-api-key", r"sk-ant-[A-Za-z0-9_\-]{32,}", "critical",
     "Anthropic API Key"),
    # OpenAI API key (legacy)
    ("openai-api-key-legacy", r"sk-[A-Za-z0-9]{32,}", "high",
     "OpenAI API Key (legacy sk- format)"),
    # OpenAI API key (project)
    ("openai-api-key-project", r"sk-proj-[A-Za-z0-9_\-]{32,}", "critical",
     "OpenAI Project API Key"),
    # Slack token
    ("slack-token", r"xox[baprs]-[A-Za-z0-9\-]{10,}", "high",
     "Slack Token"),
    # Generic private key block
    ("private-key-block", r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",
     "critical", "Private Key block"),
    # Generic high-entropy hex (32+ chars) — high false-positive rate, low priority
    # Disabled by default to avoid noise. Uncomment to enable.
    # ("generic-high-entropy", r"\b[A-Fa-f0-9]{64}\b", "low", "High-entropy hex"),
]

# Directories to skip (vendored, generated, or known noisy)
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".opencode", ".claude", "third-party", "data/knowledge/HALL_OF_RECORDS",
    "data/llm-cache", "data/library", "data/library_cache",
    "data/secrets-public.toml",  # the allowlist itself
    ".gitleaksignore",           # baseline file
}
# File extensions to scan (text-like)
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".sh", ".bash", ".zsh", ".fish",
    ".yaml", ".yml", ".toml", ".json", ".xml",
    ".md", ".txt", ".rst",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".swift",
    ".html", ".css", ".scss", ".sass",
    ".env", ".cfg", ".ini", ".conf",
}

ALLOWLIST_PATH = Path("data/secrets-public.toml")
GITLEAKS_IGNORE_PATH = Path(".gitleaksignore")


def load_allowlist() -> dict[str, Any] | None:
    """Load and validate the public secret allowlist. Returns None on failure."""
    if not ALLOWLIST_PATH.exists():
        return None
    try:
        with ALLOWLIST_PATH.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        print(f"❌ ALLOWLIST UNPARSEABLE: {ALLOWLIST_PATH}: {e}", file=sys.stderr)
        return None

    if "secret" not in data and "allowlist" not in data:
        print(f"❌ ALLOWLIST MALFORMED: missing [[secret]] or [[allowlist]] section", file=sys.stderr)
        return None

    entries = data.get("secret") or data.get("allowlist") or []
    validated: list[dict[str, Any]] = []
    for entry in entries:
        # Validate required fields per M35 amendment
        missing = []
        for field in ("client_secret", "primary_source_url", "verified_by"):
            if field not in entry or not entry[field]:
                missing.append(field)
        if missing:
            entry_id = entry.get("id", "<unknown>")
            print(f"⚠️  ALLOWLIST ENTRY INVALID: id={entry_id} missing={missing}", file=sys.stderr)
            continue
        if "approved_by" not in entry and "status" not in entry:
            entry_id = entry.get("id", "<unknown>")
            print(f"⚠️  ALLOWLIST ENTRY INCOMPLETE: id={entry_id} missing approved_by or status", file=sys.stderr)
            continue
        validated.append(entry)
    # Parse exceptions (coordination-doc historical record, etc.)
    exceptions = data.get("exceptions", {})
    return {"secrets": validated, "exceptions": exceptions}


def load_gitleaks_ignore() -> set[str]:
    """Load baseline of known-false-positive fingerprints from .gitleaksignore."""
    if not GITLEAKS_IGNORE_PATH.exists():
        return set()
    ignore = set()
    with GITLEAKS_IGNORE_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ignore.add(line)
    return ignore


def get_tracked_files(staged: bool = False) -> list[Path]:
    """Get all git-tracked files (or staged only)."""
    cmd = ["git", "ls-files"]
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [Path(p) for p in result.stdout.splitlines() if p]
    except subprocess.CalledProcessError as e:
        print(f"❌ git ls-files failed: {e}", file=sys.stderr)
        sys.exit(2)


def get_staged_files() -> list[Path]:
    """Get files staged for commit."""
    return get_tracked_files(staged=True)


def get_git_root() -> Path:
    """Get the git root directory."""
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, check=True)
    return Path(result.stdout.strip())


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    p_str = str(path)
    for skip in SKIP_DIRS:
        if skip in p_str:
            return True
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return True
    return False


def scan_file(path: Path) -> list[dict[str, Any]]:
    """Scan a single file for secret patterns. Returns list of findings."""
    findings = []
    try:
        content = path.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern_id, pattern, severity, desc in SECRET_PATTERNS:
            matches = re.finditer(pattern, line)
            for m in matches:
                findings.append({
                    "file": str(path),
                    "line": line_num,
                    "pattern_id": pattern_id,
                    "severity": severity,
                    "description": desc,
                    "match": m.group(0)[:60] + ("..." if len(m.group(0)) > 60 else ""),
                })
    return findings


def is_allowlisted(finding: dict[str, Any], allowlist: dict[str, Any] | None) -> bool:
    """Check if a finding is in the public secret allowlist."""
    if allowlist is None:
        return False
    for entry in allowlist["secrets"]:
        if entry["client_secret"] in finding["match"]:
            return True
        # Also check substring match for long secrets
        if len(entry["client_secret"]) >= 30 and entry["client_secret"][:30] in finding["match"]:
            return True
    # Check path-based exceptions (coordination docs, etc.)
    file_path = Path(finding["file"])
    exceptions = allowlist.get("exceptions", {})
    for exc_name, exc in exceptions.items():
        paths = exc.get("paths", [])
        for path_glob in paths:
            if file_path.match(path_glob):
                patterns = exc.get("patterns_allowed", [])
                for pat in patterns:
                    if re.search(pat, finding["match"]):
                        return True
    return False


def scan(staged: bool = False, scan_path: str | None = None) -> dict[str, Any]:
    """Run the full scan. Returns results dict."""
    results: dict[str, Any] = {
        "allowlist_status": "missing",
        "allowlist_entries": 0,
        "files_scanned": 0,
        "findings": [],
        "violations": [],
    }

    # Load allowlist (fail-closed if missing)
    allowlist = load_allowlist()
    if allowlist is None:
        results["allowlist_status"] = "missing_or_invalid"
        results["violations"].append({
            "type": "allowlist_missing",
            "message": f"{ALLOWLIST_PATH} is missing or unparseable. M35 fail-closed.",
        })
        return results
    results["allowlist_status"] = "ok"
    results["allowlist_entries"] = len(allowlist["secrets"])

    # Get file list
    if scan_path:
        path = Path(scan_path)
        if path.is_file():
            files = [path]
        else:
            files = list(path.rglob("*"))
            files = [f for f in files if f.is_file()]
    elif staged:
        files = get_staged_files()
    else:
        files = get_tracked_files()

    # Filter
    files = [f for f in files if not should_skip(f)]
    results["files_scanned"] = len(files)

    # Scan
    for f in files:
        findings = scan_file(f)
        for finding in findings:
            if is_allowlisted(finding, allowlist):
                continue
            results["violations"].append({
                "type": "secret_found",
                "file": finding["file"],
                "line": finding["line"],
                "pattern_id": finding["pattern_id"],
                "severity": finding["severity"],
                "description": finding["description"],
                "match": finding["match"],
            })

    return results


def lint_allowlist() -> dict[str, Any]:
    """Only lint the allowlist file structure (no file scan)."""
    results: dict[str, Any] = {
        "allowlist_status": "missing",
        "violations": [],
    }
    allowlist = load_allowlist()
    if allowlist is None:
        results["violations"].append({
            "type": "allowlist_missing",
            "message": f"{ALLOWLIST_PATH} is missing or unparseable. M35 fail-closed.",
        })
        return results
    results["allowlist_status"] = "ok"
    results["allowlist_entries"] = len(allowlist["secrets"])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="M35 Fail-Closed Secret Scanner")
    parser.add_argument("--staged", action="store_true", help="Scan staged changes only")
    parser.add_argument("--path", type=str, help="Scan specific path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--allowlist-lint", action="store_true",
                        help="Only lint the allowlist file (no scan)")
    args = parser.parse_args()

    if args.allowlist_lint:
        results = lint_allowlist()
    else:
        results = scan(staged=args.staged, scan_path=args.path)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Human-readable output
        print("🔱 M35 Fail-Closed Secret Scanner")
        print(f"  Allowlist: {results['allowlist_status']} "
              f"({results.get('allowlist_entries', 0)} entries)")
        if "files_scanned" in results:
            print(f"  Files scanned: {results['files_scanned']}")
        print(f"  Violations: {len(results['violations'])}")
        for v in results["violations"]:
            if v["type"] == "allowlist_missing":
                print(f"    ❌ {v['message']}")
            elif v["type"] == "secret_found":
                print(f"    ❌ {v['file']}:{v['line']} — {v['pattern_id']} "
                      f"({v['severity']}): {v['match']}")

    # Exit codes per M23
    if results["violations"]:
        return 1  # M23: hard fail on secret
    return 0


if __name__ == "__main__":
    sys.exit(main())
