#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Omega Engine - Check Hardcoded Secrets Tool
Detects hardcoded API keys, tokens, passwords, and other secrets in source code.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns for detecting secrets
SECRET_PATTERNS = [
    # Generic API keys
    (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API Key"),
    (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Secret Key"),
    (
        r'(?i)(access[_-]?token|accesstoken)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Access Token",
    ),
    (
        r'(?i)(refresh[_-]?token|refreshtoken)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Refresh Token",
    ),
    (
        r'(?i)(bearer[_-]?token|bearertoken)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Bearer Token",
    ),
    # Specific providers
    (
        r'(?i)(openrouter[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "OpenRouter API Key",
    ),
    (r'(?i)(exa[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Exa API Key"),
    (
        r'(?i)(firecrawl[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Firecrawl API Key",
    ),
    (r'(?i)(google[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Google API Key"),
    (
        r'(?i)(anthropic[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Anthropic API Key",
    ),
    (r'(?i)(openai[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "OpenAI API Key"),
    (r'(?i)(grok[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Grok API Key"),
    (
        r'(?i)(huggingface[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "HuggingFace API Key",
    ),
    (
        r'(?i)(replicate[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Replicate API Key",
    ),
    (
        r'(?i)(together[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Together API Key",
    ),
    (r'(?i)(nvidia[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "NVIDIA API Key"),
    (
        r'(?i)(cerebras[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "Cerebras API Key",
    ),
    (r'(?i)(groq[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Groq API Key"),
    (
        r'(?i)(sambanova[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "SambaNova API Key",
    ),
    (r'(?i)(xai[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "xAI API Key"),
    (
        r'(?i)(opencode[_-]?zen[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "OpenCode Zen API Key",
    ),
    (r'(?i)(cline[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Cline API Key"),
    (r'(?i)(copilot[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Copilot API Key"),
    # Database/connection strings
    (r'(?i)(postgres(?:ql)?://[^\s"\']+)', "PostgreSQL Connection String"),
    (r'(?i)(mysql://[^\s"\']+)', "MySQL Connection String"),
    (r'(?i)(mongodb://[^\s"\']+)', "MongoDB Connection String"),
    (r'(?i)(redis://[^\s"\']+)', "Redis Connection String"),
    # Cloud provider keys
    (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']([A-Z0-9]{20})["\']', "AWS Access Key ID"),
    (
        r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']',
        "AWS Secret Access Key",
    ),
    (
        r'(?i)(gcp[_-]?service[_-]?account[_-]?key)\s*[:=]\s*["\']([^"\']+)["\']',
        "GCP Service Account Key",
    ),
    (r'(?i)(azure[_-]?client[_-]?secret)\s*[:=]\s*["\']([^"\']+)["\']', "Azure Client Secret"),
    # Generic password patterns
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']', "Password"),
    (r'(?i)(private[_-]?key)\s*[:=]\s*["\']([^"\']+)["\']', "Private Key"),
    # JWT tokens
    (r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+", "JWT Token"),
    # SSH keys
    (r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----", "SSH Private Key"),
    (r"ssh-(?:rsa|dss|ed25519) [A-Za-z0-9+/]+[=]{0,3}", "SSH Public Key"),
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "test_",
    "tests/",
    "__pycache__",
    ".venv",
    "venv/",
    "docs/",
    "data/",
    "scripts/",
    "archive/",
    "old/",
    ".git/",
    ".env",
    ".env.",
    "*.key",
    "*.pem",
    "*.crt",
    "detect_api_keys.py",
    "enforce_vaultcore.py",
    "check_hardcoded_secrets.py",
]


def should_exclude(filepath: Path) -> bool:
    path_str = str(filepath)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def check_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Check a file for hardcoded secrets. Returns list of (line_num, secret_type, matched_text)."""
    if should_exclude(filepath):
        return []

    results = []
    try:
        content = filepath.read_text()
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue

            for pattern, secret_type in SECRET_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Get the matched secret (group 2 if exists, else group 0)
                    secret = (
                        match.group(2)
                        if match.lastindex and match.lastindex >= 2
                        else match.group(0)
                    )
                    # Truncate for display
                    display = secret[:50] + "..." if len(secret) > 50 else secret
                    results.append((i, secret_type, display))
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect hardcoded secrets in source code")
    parser.add_argument("files", nargs="*", type=Path, help="Files to check")
    parser.add_argument("--strict", action="store_true", help="Exit with error on findings")
    parser.add_argument("--all", action="store_true", help="Check all files in project")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.all:
        files = list(Path(".").rglob("*"))
        files = [
            f
            for f in files
            if f.is_file()
            and f.suffix
            in [
                ".py",
                ".js",
                ".ts",
                ".json",
                ".yaml",
                ".yml",
                ".toml",
                ".ini",
                ".cfg",
                ".conf",
                ".sh",
                ".bash",
                ".zsh",
                ".md",
                ".txt",
            ]
        ]
    else:
        files = args.files if args.files else list(Path(".").rglob("*"))
        files = [f for f in files if f.is_file()]

    all_findings = []
    for filepath in files:
        findings = check_file(filepath)
        if findings:
            all_findings.append((str(filepath), findings))

    if args.json:
        import json

        output = {
            "findings": [
                {"file": f, "secrets": [{"line": l, "type": t, "value": v} for l, t, v in findings]}
                for f, findings in all_findings
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        if all_findings:
            print(
                f"\n❌ Found {sum(len(f) for _, f in all_findings)} hardcoded secrets in {len(all_findings)} files:"
            )
            for filepath, findings in all_findings:
                print(f"\n{filepath}:")
                for line_num, secret_type, value in findings:
                    print(f"  Line {line_num}: {secret_type} - {value}")
        else:
            print("✅ No hardcoded secrets found")

    if all_findings and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
