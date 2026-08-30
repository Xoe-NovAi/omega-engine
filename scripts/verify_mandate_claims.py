#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""verify-mandate-claims — Mechanical claims-harness (Ruling S7, Team-Study #1).

P0 harness born from the C2-class finding (4 documents asserted an uninstalled
pre-commit hook). Verifies that written CLAIMS match DISK STATE, and runs three
provenance/sanitation detectors over NEW/MODIFIED files:

  1. Claims-vs-disk gate : data-driven rules (config/mandate_claims.yaml);
                           a document asserting a fact requires its probe-paths
                           to exist on disk (O-Q4: probe-path bound to claim).
  2. Sanitation detector : flags real-name contamination patterns from
                           THE_VISION_CANONICAL_DRAFT_20260823.md section 8.2
                           (foreign home-dirs, shell prompts, email/social
                           handles, marker-file hits).
  3. FP-11 detector      : flags @-mention wrapper imperatives presented as
                           principal speech (FORENSIC_PATTERNS.md FP-11).
  4. T0 assertion support: model-attribution claims must carry message-level
                           modelID evidence (Tier 0), never session-level joins
                           alone (FP-04 hierarchy).

MODE: WARN-ONLY this phase (ruling S5 / Ma'at Fork 2). All findings emit
structured warnings with file:line; exit code stays 0. Use --strict to fail
on findings once the probation period ends.

SANITATION LAW: this script NEVER embeds the Architect's real name. Exact
markers (real name, account handles, personal domains) are read from an
UNTRACKED local file: data/knowledge/safety/sanitation_markers.local.yaml
(placeholder token in docs/config: <ARCHITECT_NAME>). Committed code carries
structural heuristics only.

Usage:
    .venv/bin/python scripts/verify_mandate_claims.py                 # working-tree diff vs HEAD
    .venv/bin/python scripts/verify_mandate_claims.py --files a b c   # explicit files
    .venv/bin/python scripts/verify_mandate_claims.py --diff main     # diff vs branch
    .venv/bin/python scripts/verify_mandate_claims.py --json          # machine output
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Constants ──────────────────────────────────────────────────────────

MARKERS_LOCAL_PATH = REPO_ROOT / "data/knowledge/safety/sanitation_markers.local.yaml"
CLAIMS_CONFIG_PATH = REPO_ROOT / "config/mandate_claims.yaml"

TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".rst"}
CODE_EXTS = {".py", ".sh", ".bash", ".ts", ".js", ".toml", ".cfg", ".ini"}

# Home-directory usernames that are legitimate in this repo (host user +
# system accounts). Anything else under /home/<name>/ is flagged as a
# potential foreign home-dir leak (section 8.2 pattern class).
HOME_DIR_ALLOWLIST = {"arcana-novai", "root", "user", "runner", "vscode"}

# Email domains that are legitimate in this repo.
EMAIL_DOMAIN_ALLOWLIST = {
    "xoe-nov.ai",
    "example.com",
    "example.org",
    "noreply.github.com",
    "users.noreply.github.com",
}

# Known fleet handles — @-mentions of these agents are routing hints, not
# social-handle contamination (.opencode/MANIFEST.md roster).
FLEET_HANDLE_ALLOWLIST = {
    "kali", "maat", "lilith", "roc_racoon", "researcher", "carmack",
    "jem", "grokster", "doom_guy", "sophia", "verity", "node", "makali",
    "sysadmin", "pillar_p1", "iris", "oracle", "scribe", "ox_alpha",
}

RE_HOME_DIR = re.compile(r"(?<![\w./~-])/home/([A-Za-z0-9_.-]+)(?=/|\b)")
RE_SHELL_PROMPT = re.compile(r"\b([A-Za-z0-9._-]+)@([A-Za-z0-9_-]+)(:[~\w/-]*)?[$#]\s")
RE_EMAIL = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)\b")
RE_SOCIAL_HANDLE = re.compile(r"(?<![\w.@])@([A-Za-z0-9_]{4,30})\b")
RE_FENCE = re.compile(r"^\s*(```|~~~)")

# FP-11: wrapper-synthesized imperatives (never authored by the Principal).
RE_WRAPPER_IMPERATIVE = re.compile(
    r"(call the task tool with subagent\s*:|use the above message\b"
    r"|use the above message and context)",
    re.IGNORECASE,
)
# FP-11: attribution-intro framing (text presented as principal speech).
RE_ATTRIBUTION_INTRO = re.compile(
    r"\b(the user|the principal|the architect|he|she|they)\s+"
    r"(explicitly\s+)?(says|said|says\s*:|instructs|instructed|demands|requested)"
    r"(\s+that)?\s*[:]?",
    re.IGNORECASE,
)

# T0 (FP-04): model-attribution claim lines.
RE_T0_CLAIM = re.compile(
    r"\b(claimed_model|model_used|asserted_model|generated_by|actual_models)\b\s*[:=]",
    re.IGNORECASE,
)
# Message-level (Tier 0) evidence refs — the REQUIRED grade.
RE_MSG_LEVEL_EVIDENCE = re.compile(
    r"(msg_[0-9a-zA-Z]+|message_id|messages\.modelID|messages\.model_id|\bmodelID\b|\bTier ?0\b)",
    re.IGNORECASE,
)
# Session-level refs — INSUFFICIENT alone (stale metadata per FP-04).
RE_SESSION_REF = re.compile(r"\bses_[0-9a-zA-Z]+\b")

T0_CONTEXT_WINDOW = 3  # lines after a claim line to look for evidence refs


# ── Data model ─────────────────────────────────────────────────────────


@dataclass
class Finding:
    """One structured warning. WARN-ONLY: never affects exit code this phase."""

    detector: str
    rule: str
    path: str
    line: int
    message: str
    snippet: str = ""

    def render(self) -> str:
        loc = f"{self.path}:{self.line}"
        snip = self.snippet.strip()
        if len(snip) > 120:
            snip = snip[:117] + "..."
        return f"[WARN][{self.detector}] {loc}: {self.rule} — {self.message}" + (
            f" | {snip}" if snip else ""
        )


@dataclass
class ScanResult:
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    claims_checked: int = 0

    def merge(self, other: "ScanResult") -> None:
        self.findings.extend(other.findings)
        self.files_scanned += other.files_scanned
        self.claims_checked += other.claims_checked


# ── Helpers ────────────────────────────────────────────────────────────


def _strip_inline_code(line: str) -> str:
    """Remove inline-code spans so documented examples don't false-positive."""
    return re.sub(r"`[^`]*`", '""', line)


EXEMPT_TAG = "verify-claims:exempt"


def _is_exempt(line: str) -> bool:
    """Line-level exemption for legitimate fixtures/examples (gitleaks-
    signerline pattern). The tag must appear ON the triggering line."""
    return EXEMPT_TAG in line


def _iter_content_lines(text: str, skip_fences: bool):
    """Yield (lineno, line). With skip_fences, fenced blocks are omitted."""
    in_fence = False
    fence_marker = ""
    for i, line in enumerate(text.splitlines(), start=1):
        if skip_fences:
            m = RE_FENCE.match(line)
            if m:
                if not in_fence:
                    in_fence = True
                    fence_marker = m.group(1)[:3]
                elif line.strip().startswith(fence_marker):
                    in_fence = False
                continue
            if in_fence:
                continue
        yield i, line


def load_local_markers() -> list[str]:
    """Load exact sanitation markers from the UNTRACKED local file.

    The file format is a flat YAML list:
        - <ARCHITECT_NAME>
        - TaylorBare27-style-account-marker
    Missing file = structural heuristics only (committed default).
    """
    if not MARKERS_LOCAL_PATH.exists():
        return []
    try:
        import yaml

        data = yaml.safe_load(MARKERS_LOCAL_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(m) for m in data if str(m).strip()]
    except Exception as e:  # noqa: BLE001 — probe must never crash the harness
        print(f"[WARN][harness] unreadable markers file {MARKERS_LOCAL_PATH}: {e}",
              file=sys.stderr)
    return []


def changed_files(base: str) -> list[Path]:
    """Files NEW or MODIFIED vs `base` (working tree included)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACM", f"{base}"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30, check=True,
        )
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[WARN][harness] git diff failed ({e}); scanning nothing", file=sys.stderr)
        return []
    return [
        REPO_ROOT / p.strip()
        for p in out.stdout.splitlines()
        if p.strip() and (REPO_ROOT / p.strip()).is_file()
    ]


# ── Detector 1: Sanitation (section 8.2 contamination classes) ────────


def detect_sanitation(path: Path, text: str, markers: list[str]) -> ScanResult:
    result = ScanResult()
    rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    is_code = path.suffix.lower() in CODE_EXTS

    for lineno, raw in _iter_content_lines(text, skip_fences=False):
        if _is_exempt(raw):
            continue
        # Fenced/inline code still scanned for sanitation (contamination is
        # contamination wherever it sits) — but inline spans stripped only for
        # handle noise reduction, not for path/prompt classes.
        line = raw

        # (a) Foreign home-dir paths: /home/<unknown-user>/
        m = RE_HOME_DIR.search(line)
        if m and m.group(1).lower() not in HOME_DIR_ALLOWLIST:
            result.findings.append(Finding(
                "sanitation", "home-dir-path", rel, lineno,
                f"foreign home-dir '/home/{m.group(1)}/' — possible real-name "
                "contamination (vision-canonical 8.2 class)", line))

        # (b) Shell-prompt fragments: user@host:~$ (catches truncated names too)
        m = RE_SHELL_PROMPT.search(line)
        if m and m.group(1).lower() not in HOME_DIR_ALLOWLIST:
            result.findings.append(Finding(
                "sanitation", "shell-prompt", rel, lineno,
                f"shell-prompt fragment '{m.group(0).strip()}' — possible "
                "real-name leak via prompt echo", line))

        # (c) Email handles outside sovereign domains
        for m in RE_EMAIL.finditer(line):
            dom = m.group(2).lower()
            if dom not in EMAIL_DOMAIN_ALLOWLIST and not dom.endswith("xoe-nov.ai"):
                result.findings.append(Finding(
                    "sanitation", "email-handle", rel, lineno,
                    f"email handle '{m.group(0)}' outside allowlist domains", line))
                break

        # (d) Social handles in prose files only (code decorators/annotations
        # would flood); fleet handles allowlisted.
        if not is_code and path.suffix.lower() in TEXT_EXTS:
            clean = _strip_inline_code(line)
            for m in RE_SOCIAL_HANDLE.finditer(clean):
                if m.group(1).lower() in FLEET_HANDLE_ALLOWLIST:
                    continue
                result.findings.append(Finding(
                    "sanitation", "social-handle", rel, lineno,
                    f"@-handle '{m.group(0)}' not in fleet roster — verify it is "
                    "not a personal/social handle", line))
                break

        # (e) Exact markers from untracked local file (SANITATION LAW: the
        # real name itself never lives in this repo's tracked files).
        for marker in markers:
            if marker.lower() in line.lower():
                result.findings.append(Finding(
                    "sanitation", "local-marker", rel, lineno,
                    "exact sanitation marker hit",
                    # Redact snippet: the warning must not echo the marker.
                    snippet="[redacted — marker match]"))
                break

    return result


# ── Detector 2: FP-11 @-wrapper attribution forgery ────────────────────


def detect_fp11(path: Path, text: str) -> ScanResult:
    """Flag wrapper imperatives presented as principal speech.

    Heuristics (warn-only, FP-11 spec):
      fp11-quote-block : wrapper imperative inside a blockquote (presented as
                         quoted speech).
      fp11-attribution : attribution-intro ('the user explicitly says:')
                         followed within ATTR_WINDOW lines by a wrapper
                         imperative.
    Inline code spans and fenced blocks are SKIPPED — documenting the pattern
    (as FORENSIC_PATTERNS.md does) must not trip the detector.
    """
    result = ScanResult()
    rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    ATTR_WINDOW = 3
    attr_lines: list[tuple[int, str]] = []

    for lineno, raw in _iter_content_lines(text, skip_fences=True):
        if _is_exempt(raw):
            continue
        line = _strip_inline_code(raw)

        # Blockquote containing a wrapper imperative = quoted forgery risk.
        if line.lstrip().startswith(">") and RE_WRAPPER_IMPERATIVE.search(line):
            result.findings.append(Finding(
                "fp11", "fp11-quote-block", rel, lineno,
                "wrapper imperative inside blockquote — possible @-mention "
                "attribution forgery presented as quoted speech", raw))

        # Attribution intro near a wrapper imperative.
        if RE_ATTRIBUTION_INTRO.search(line):
            attr_lines.append((lineno, line))
        for a_lineno, a_line in list(attr_lines):
            if lineno - a_lineno > ATTR_WINDOW:
                attr_lines.remove((a_lineno, a_line))
                continue
            if a_lineno != lineno and RE_WRAPPER_IMPERATIVE.search(line):
                result.findings.append(Finding(
                    "fp11", "fp11-attribution", rel, lineno,
                    f"wrapper imperative {lineno - a_lineno} line(s) below "
                    f"attribution intro at :{a_lineno} — synthetic wrapper text "
                    "may be presented as principal speech", raw))
                attr_lines.remove((a_lineno, a_line))

    return result


# ── Detector 3: T0 assertion support (FP-04 evidence grade) ───────────


def detect_t0_attribution(path: Path, text: str) -> ScanResult:
    """Model-attribution claims must cite message-level modelID evidence.

    Per FP-04 tier order: messages.modelID is retroactive ground truth;
    sessions.model alone is stale. A claim whose context window carries only
    session-level refs (or no refs) gets a WARN.
    """
    result = ScanResult()
    rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    # Attribution claims are authored assertions — scan text formats only.
    # Code that PROCESSES claim strings (provenance tools) would false-fire.
    if path.suffix.lower() not in TEXT_EXTS:
        return result
    lines = text.splitlines()

    for lineno, raw in enumerate(lines, start=1):
        if _is_exempt(raw) or not RE_T0_CLAIM.search(raw):
            continue
        window = "\n".join(lines[lineno - 1: lineno + T0_CONTEXT_WINDOW])
        has_msg = bool(RE_MSG_LEVEL_EVIDENCE.search(window))
        has_session = bool(RE_SESSION_REF.search(window))
        if has_msg:
            continue  # correct grade — Tier 0 anchored
        if has_session:
            result.findings.append(Finding(
                "t0", "session-level-join", rel, lineno,
                "model-attribution claim cites session-level refs only — "
                "requires message-level modelID evidence (FP-04 Tier 0)", raw))
        else:
            result.findings.append(Finding(
                "t0", "missing-evidence", rel, lineno,
                "model-attribution claim carries no evidence reference — "
                "add message-level modelID ref (msg_/modelID/Tier 0)", raw))

    return result


# ── Gate 0: claims-vs-disk (data-driven, C2-class) ─────────────────────


def load_claim_rules() -> list[dict]:
    """Load claim rules from config/mandate_claims.yaml.

    Schema:
        claims:
          - id: tracking-hook-installed
            pattern: 'pre-commit hook .*installed|hook is now active'
            file_globs: ['**/*.md']
            probe_paths: ['.pre-commit-config.yaml']   # must exist on disk
            probe_contains: ['omega-tracking-state']   # optional content check
    Missing config = gate disabled (warn once).
    """
    if not CLAIMS_CONFIG_PATH.exists():
        return []
    try:
        import yaml

        data = yaml.safe_load(CLAIMS_CONFIG_PATH.read_text(encoding="utf-8")) or {}
        return list(data.get("claims") or [])
    except Exception as e:  # noqa: BLE001
        print(f"[WARN][harness] unreadable claims config {CLAIMS_CONFIG_PATH}: {e}",
              file=sys.stderr)
        return []


def detect_claim_violations(path: Path, text: str, rules: list[dict]) -> ScanResult:
    import fnmatch

    result = ScanResult()
    rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)

    for rule in rules:
        globs = rule.get("file_globs") or ["**/*.md"]
        if not any(fnmatch.fnmatch(rel, g) for g in globs):
            continue
        try:
            rx = re.compile(rule["pattern"], re.IGNORECASE)
        except (KeyError, re.error) as e:
            print(f"[WARN][harness] bad rule '{rule.get('id')}': {e}", file=sys.stderr)
            continue
        for lineno, raw in enumerate(text.splitlines(), start=1):
            if not rx.search(raw):
                continue
            result.claims_checked += 1
            missing = [p for p in (rule.get("probe_paths") or []) if not (REPO_ROOT / p).exists()]
            if not missing and rule.get("probe_contains"):
                for pp in rule.get("probe_paths") or []:
                    f = REPO_ROOT / pp
                    if f.exists():
                        content = f.read_text(encoding="utf-8", errors="replace")
                        if not all(c in content for c in rule["probe_contains"]):
                            missing.append(pp)
                            break
            if missing:
                result.findings.append(Finding(
                    "claims", f"unverified-claim:{rule.get('id')}", rel, lineno,
                    f"document asserts claim but probe path(s) missing/incomplete: "
                    f"{missing} (C2-class: claimed ≠ disk)", raw))
    return result


def load_forbidden_rules() -> list[dict]:
    """Load HARD-FAIL forbidden-pattern rules from config/mandate_claims.yaml.

    Schema (under ``forbidden:``):
        - id: d593-hardcoded-redis-password
          pattern: 'password\\s*=\\s*["'']omega["'']'
          file_globs: ['src/**/*.py']
          reference: 'why + fix pointer'

    Unlike claim rules, forbidden rules scan the WHOLE tree and exit 1 on
    any hit regardless of warn-only phase (DC-29: some regressions are too
    cheap to prevent to allow warn-only).
    """
    if not CLAIMS_CONFIG_PATH.exists():
        return []
    try:
        import yaml

        data = yaml.safe_load(CLAIMS_CONFIG_PATH.read_text(encoding="utf-8")) or {}
        return list(data.get("forbidden") or [])
    except Exception as e:  # noqa: BLE001
        print(f"[WARN][harness] unreadable forbidden rules in {CLAIMS_CONFIG_PATH}: {e}",
              file=sys.stderr)
        return []


def _glob_match(rel: str, pattern: str) -> bool:
    """Glob match with proper ``**`` semantics (fnmatch treats it as one *).

    ``src/**/*.py`` must match ``src/a.py`` AND ``src/x/y/a.py``.
    """
    if "**" not in pattern:
        return fnmatch.fnmatch(rel, pattern)
    rx = re.escape(pattern)
    rx = rx.replace(re.escape("**/"), "(?:[^/]+/)*")
    rx = rx.replace(re.escape("*"), "[^/]*")
    rx = rx.replace(re.escape("?"), "[^/]")
    return re.fullmatch(rx, rel) is not None


def detect_forbidden(
    path: Path, text: str, rules: list[dict], rel_override: str | None = None
) -> ScanResult:
    """Scan one file against hard-fail forbidden patterns.

    Args:
        rel_override: repo-relative path used for glob matching when the
            physical path lives outside REPO_ROOT (unit-test fixtures).
    """
    result = ScanResult()
    if rel_override is not None:
        rel = rel_override
    else:
        rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    for rule in rules:
        globs = rule.get("file_globs") or []
        if not any(_glob_match(rel, g) for g in globs):
            continue
        try:
            rx = re.compile(rule["pattern"])
        except (KeyError, re.error) as e:
            print(f"[WARN][harness] bad forbidden rule '{rule.get('id')}': {e}",
                  file=sys.stderr)
            continue
        for lineno, raw in enumerate(text.splitlines(), start=1):
            if _is_exempt(raw) or not rx.search(raw):
                continue
            result.findings.append(Finding(
                "forbidden", f"hard-fail:{rule.get('id')}", rel, lineno,
                f"FORBIDDEN pattern present — {rule.get('reference', 'see rule id')}",
                raw))
    return result


def forbidden_scan_targets(rules: list[dict]) -> list[Path]:
    """All tracked-tree files matching any forbidden rule's globs."""
    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", ".ruff_cache"}
    targets: dict[str, Path] = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            rel = str(Path(root, name).relative_to(REPO_ROOT))
            if rel not in targets and any(
                _glob_match(rel, g) for r in rules for g in (r.get("file_globs") or [])
            ):
                targets[rel] = REPO_ROOT / rel
    return sorted(targets.values())


# ── Orchestration ──────────────────────────────────────────────────────


def scan_file(
    path: Path,
    rules: list[dict],
    markers: list[str],
    forbidden_rules: list[dict] | None = None,
) -> ScanResult:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        result = ScanResult(files_scanned=1)
        result.findings.append(Finding(
            "harness", "unreadable-file", str(path), 0, f"could not read: {e}"))
        return result
    result = ScanResult(files_scanned=1)
    result.merge(detect_sanitation(path, text, markers))
    result.merge(detect_fp11(path, text))
    result.merge(detect_t0_attribution(path, text))
    result.merge(detect_claim_violations(path, text, rules))
    if forbidden_rules:
        result.merge(detect_forbidden(path, text, forbidden_rules))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_mandate_claims",
        description="Mechanical claims-harness: claims-vs-disk + sanitation/FP11/T0 detectors (warn-only).",
    )
    parser.add_argument("--files", nargs="*", help="explicit files to scan")
    parser.add_argument("--diff", default=None, help="git base to diff against (default: HEAD)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 on findings (POST-probation only; warn-only phase ignores)")
    args = parser.parse_args(argv)

    markers = load_local_markers()
    rules = load_claim_rules()
    forbidden_rules = load_forbidden_rules()

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = changed_files(args.diff or "HEAD")

    total = ScanResult()
    for f in files:
        total.merge(scan_file(f, rules, markers, forbidden_rules))

    # Forbidden rules scan the WHOLE tree (not just the diff): a regression
    # anywhere must break the gate. HARD-FAIL semantics per DC-29.
    if forbidden_rules:
        for f in forbidden_scan_targets(forbidden_rules):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            total.merge(detect_forbidden(f, text, forbidden_rules))

    forbidden_hits = [f for f in total.findings if f.detector == "forbidden"]

    if args.json:
        print(json.dumps({
            "mode": "warn-only+forbidden-hard-fail",
            "files_scanned": total.files_scanned,
            "claims_checked": total.claims_checked,
            "forbidden_hits": len(forbidden_hits),
            "findings": [f.__dict__ for f in total.findings],
        }, indent=2))
        # JSON mode: failure signal is the exit code + forbidden_hits field;
        # no trailing human text (would break parsers).
    else:
        print(f"verify-mandate-claims: scanned {total.files_scanned} file(s), "
              f"{total.claims_checked} claim assertion(s), "
              f"{len(total.findings)} warning(s) "
              f"[warn-only mode; forbidden rules hard-fail]")
        for f in total.findings:
            print(f.render())
        if forbidden_hits:
            print(f"[FAIL] {len(forbidden_hits)} forbidden-pattern hit(s) — see above. "
                  "These are hard-fail rules and do not respect warn-only phase.")

    # HARD-FAIL: forbidden-pattern hits exit 1 regardless of warn-only phase
    # (DC-29). --strict additionally fails on warn-only findings post-debut.
    if forbidden_hits:
        return 1
    if args.strict and total.findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
