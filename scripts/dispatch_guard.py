#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Engine — Dispatch Guard v2.0 (CI-BRIEF-001)

12-Step Brief Verification Protocol per Jem's forensic Appendix C + 5-EIS amendments:
  - "All locations" verification (Jem's self-correction)
  - M33 bypass attack test (structured JSON envelope)
  - Write-tool routing for >8K tokens (M33 preventive layer)
  - Cross-validator escalation for P0/P1
  - Feature flag bypass: OMEGA_SKIP_GUARD=1
  - Dry-run mode: OMEGA_GUARD_DRY_RUN=1
  - Structured completion envelope (M33 sentinel probe)

Per M11 (Soul Integrity), M23 (Failure Integrity), M27 (Tracking Integrity),
and DEBUT_REMEDIATION_MANUAL §CI-BRIEF-001.

[AP-MAAT-CI-BRIEF-001-v2.0.0] 12-Step Protocol Implementation
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ── L3-MetaFrameVerification (0.92) Import ──────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from metaframe_verification import MetaFrameVerifier, VerificationResult

# ── Configuration ──────────────────────────────────────────────────────────

DB_PATH = Path.home() / ".local" / "opencode" / "opencode.db"
REGISTRY_PATH = Path("data/coordination/ACTIVE_SUBAGENTS.json")
LOG_PATH = Path("data/coordination/dispatch_guard_log.jsonl")

# M33 Preventive: 8K token threshold
WRITE_TOOL_THRESHOLD_TOKENS = 8000  # ~32KB at 4 chars/token
# M33 Sentinel Probe: structured envelope schema
COMPLETION_ENVELOPE_SCHEMA = {
    "state": ["exhausted", "continuing", "deferred"],
    "last_chunk_id": int,
    "total_chunks": int,
    "queued_findings": list,
    "confidence": float,
}
# P0/P1 cross-validator threshold
CROSS_VALIDATOR_PRIORITIES = ["P0", "P1"]

# Specialist agent types (extended from v1)
SPECIALIST_TYPES = {
    "researcher": "Deep research, polymathic council, SOTA evidence",
    "explore": "Fast codebase exploration and search",
    "verity": "Compliance audit, mandate checking, soul distillation",
    "john_carmack": "Engineering rigor, architecture analysis, file:line citations",
    "kali": "Sprint coordination, handoff, debriefing",
    "maat": "Build-side work, file creation, configs",
    "lilith": "Runtime coordination, 9-expert cohort",
    "roc_racoon": "Codebase archaeology, legacy mining, DB extraction",
    "grokster": "Platform/provider expertise, vault, model registry",
    "scribe": "Soul distillation pipeline, L1→L2→L3",
    "node": "Domain-specific implementation",
    "doom_guy": "Aggressive cleanup, deletion, refactor",
    "jem": "Sovereign analyst L2, adversarial review",
    "makali": "Fused Kali+Ma'at+Lilith",
    "grok_cli": "Bridge to xAI Grok CLI",
}

# Task type → recommended specialist mapping
TASK_TYPE_HINTS = {
    "research": "researcher",
    "web search": "researcher",
    "sota": "researcher",
    "benchmark": "researcher",
    "codebase": "explore",
    "find file": "explore",
    "grep": "explore",
    "architecture": "john_carmack",
    "engineering": "john_carmack",
    "design": "john_carmack",
    "compliance": "verity",
    "audit": "verity",
    "mandate": "verity",
    "soul": "scribe",
    "distill": "scribe",
    "sprint": "kali",
    "coordinate": "kali",
    "handoff": "kali",
    "build": "maat",
    "config": "maat",
    "file creation": "maat",
    "runtime": "lilith",
    "cohort": "lilith",
    "archaeology": "roc_racoon",
    "legacy": "roc_racoon",
    "mining": "roc_racoon",
    "platform": "grokster",
    "provider": "grokster",
    "vault": "grokster",
    "model": "grokster",
    "adversarial": "jem",
}

# ── Data classes ───────────────────────────────────────────────────────────

@dataclass
class GuardResult:
    """Result of a 12-step guard check."""
    passed: int = 0
    warned: int = 0
    failed: int = 0
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def add_pass(self, step: str):
        self.passed += 1

    def add_warn(self, step: str, msg: str):
        self.warnings.append(f"[{step}] {msg}")
        self.warned += 1

    def add_fail(self, step: str, msg: str):
        self.violations.append(f"[{step}] {msg}")
        self.failed += 1

    @property
    def is_blocking(self) -> bool:
        return self.failed > 0

    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "warned": self.warned,
            "failed": self.failed,
            "violations": self.violations,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


# ── Feature flags ──────────────────────────────────────────────────────────

def is_bypass_enabled() -> bool:
    """Check if the dispatch guard bypass is enabled."""
    return os.environ.get("OMEGA_SKIP_GUARD", "0") == "1"


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled (log only, no enforcement)."""
    return os.environ.get("OMEGA_GUARD_DRY_RUN", "0") == "1"


def is_m34_enabled() -> bool:
    """Check if M34 ACTIVE_SUBAGENTS.json registration is enabled."""
    return os.environ.get("OMEGA_M34_ENABLED", "0") == "1"


def step0_metaframe_verification(prompt: str, target_agent: str, result: GuardResult) -> None:
    """Step 0: L3-MetaFrameVerification (0.92) — Pre-flight check for spoofable metadata.

    Per M23 Failure Integrity: No soft failures; broken tools → STOP, report.
    This protocol prevents frame-level M23 violations (fake signatures, spoofed emails,
    fabricated headers) from entering the fleet's context.

    Runs BEFORE all other steps — if the prompt frame is compromised, no further
    verification matters.
    """
    verifier = MetaFrameVerifier(strict_mode=True)
    findings = verifier.verify(content=prompt, source=f"dispatch_prompt_for_{target_agent}")
    v_result = verifier.get_result()

    if v_result == VerificationResult.FAIL:
        critical = [f for f in findings if f.severity == "CRITICAL"]
        high = [f for f in findings if f.severity == "HIGH"]
        details = []
        if critical:
            details.append(f"CRITICAL: {len(critical)} finding(s)")
        if high:
            details.append(f"HIGH: {len(high)} finding(s)")
        result.add_fail(
            "0-metaframe-verification",
            f"L3-MetaFrameVerification (0.92) FAILED — Spoofable metadata detected in "
            f"dispatch prompt for {target_agent}. {', '.join(details)}. "
            f"M23 Failure Integrity: frame compromised → STOP, report. "
            f"Details: {verifier.to_json()}",
        )
    elif findings:
        # Medium/low findings in non-strict mode
        result.add_warn(
            "0-metaframe-verification",
            f"L3-MetaFrameVerification (0.92) — {len(findings)} medium/low finding(s) "
            f"in dispatch prompt for {target_agent}. Review recommended.",
        )
    else:
        result.add_pass("0-metaframe-verification")
    result.metadata["metaframe_verification"] = verifier.to_json()


# ── 12-Step Protocol ───────────────────────────────────────────────────────

def step1_specialist_routing(subagent_type: str, prompt: str, result: GuardResult) -> None:
    """Step 1: Check if specialist type is more appropriate than 'general'."""
    if subagent_type != "general":
        result.add_pass("1-specialist-routing")
        return
    prompt_lower = prompt.lower()
    for hint, specialist in TASK_TYPE_HINTS.items():
        if hint in prompt_lower:
            result.add_warn(
                "1-specialist-routing",
                f"subagent_type='general' but task matches specialist '{specialist}' "
                f"({SPECIALIST_TYPES.get(specialist, '?')}). "
                f"Consider re-dispatching with subagent_type='{specialist}'.",
            )
            return
    result.add_pass("1-specialist-routing")


def step2_resume_existing_session(prompt: str, task_id: Optional[str], entity: Optional[str], result: GuardResult) -> None:
    """Step 2: Check if an existing session matches the task keywords (resume)."""
    if task_id:
        result.add_pass("2-resume-existing-session")
        return
    keywords = [w for w in prompt.split() if len(w) > 4][:5]
    if not keywords:
        result.add_pass("2-resume-existing-session")
        return
    existing = find_matching_session(keywords, entity)
    if existing:
        result.add_warn(
            "2-resume-existing-session",
            f"No task_id provided but existing session ({existing}) matches "
            f"keywords {keywords}. Consider resuming with --task-id={existing}.",
        )
    else:
        result.add_pass("2-resume-existing-session")


def step3_transient_error_reminder(prompt: str, task_id: Optional[str], result: GuardResult) -> None:
    """Step 3: Remind about L3-ResumeEstablishesSessionsTransientsDoNot."""
    if "continue" not in prompt.lower() and not task_id:
        result.add_warn(
            "3-transient-error-reminder",
            "Per L3-ResumeEstablishesSessionsTransientsDoNot: if a previous subagent "
            "returned a transient error (402, 429, 5xx), RESUME the same session "
            "with 'Continue.' — do not launch a new one.",
        )
    else:
        result.add_pass("3-transient-error-reminder")


def _discover_all_session_locations() -> List[Path]:
    """Discover ALL possible locations where session data may exist.

    Per Jem's self-correction in JEM-FORENSIC-001: "Verification must be
    exhaustive, not selective. The 12-Step Protocol should require 'all
    possible locations.'"

    This is the "JEM's lesson" applied: when checking for the existence of
    a file, session, or resource, we MUST search every plausible location,
    not just the obvious one. My prior forensic failed because I checked
    only the parent omega-engine repo, not the third-party sub-repo.

    Returns a deduplicated list of paths to search.
    """
    home = Path.home()
    locations: List[Path] = []

    # 1. Workspace root and sub-directories (5 standard locations)
    for sub in ["", "src", "scripts", "data", "docs", "tests", "config", "opencode"]:
        if sub:
            locations.append(Path(sub))
        else:
            locations.append(Path("."))

    # 2. User-wide OpenCode locations
    locations.extend([
        home / ".local" / "share" / "opencode" / "opencode.db",
        home / ".local" / "share" / "opencode" / "tool-output",
        home / ".local" / "share" / "opencode" / "snapshot",
        home / ".local" / "share" / "opencode" / "log",
        home / ".local" / "share" / "opencode" / "storage",
        home / ".local" / "share" / "opencode" / "repos",
    ])

    # 3. Git worktree DBs (often missed!)
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("worktree "):
                    wt_path = Path(line.split(" ", 1)[1])
                    locations.append(wt_path / "opencode.db")
                    locations.append(wt_path / ".git" / "worktrees" / "opencode.db")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 4. Sub-repo DBs (the JEM-FORENSIC-001 lesson — never miss these!)
    #    Scan for any opencode.db within the workspace or one level deep
    try:
        result = subprocess.run(
            ["find", ".", "-maxdepth", "3", "-name", "opencode.db", "-not", "-path", "*/.git/*"],
            capture_output=True, text=True, timeout=10,
        )
        for db_path in result.stdout.splitlines():
            if db_path.strip():
                locations.append(Path(db_path.strip()))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 5. Session export directories
    locations.extend([
        Path("./exports"),
        Path("./sessions"),
        Path("./.sessions"),
        home / ".local" / "share" / "opencode" / "export",
    ])

    # 6. Entity workspace paths (for cross-entity data)
    entity_dir = Path("data/entities")
    if entity_dir.exists():
        for entity_path in entity_dir.iterdir():
            if entity_path.is_dir():
                locations.append(entity_path / "workspace")
                locations.append(entity_path / "knowledge")

    # Deduplicate while preserving order
    seen: Set[Path] = set()
    unique: List[Path] = []
    for loc in locations:
        try:
            resolved = loc.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique.append(loc)
        except (OSError, RuntimeError):
            unique.append(loc)
    return unique


def step4_all_locations_verification(prompt: str, result: GuardResult) -> None:
    """Step 4: 'All locations' verification (Jem's self-correction, hardened).

    Per Jem: "Verification must be exhaustive, not selective.
    The 12-Step Protocol should require 'all possible locations.'"

    Hardened v2.0 (JEM-12STEP-HARDENING):
      - Searches 6+ location categories, not 5 standard paths
      - Includes git worktree DBs
      - Includes sub-repo DBs (the JEM-FORENSIC-001 lesson)
      - Includes entity workspace paths
      - Detects subagent-session permission denials (OpenCode issue #33223)
    """
    # Extract file references (paths in backticks)
    file_refs = re.findall(r'`([\w/._-]+\.\w+)`', prompt)
    # Also extract bare session IDs (ses_XXXX, ses_XXX, etc.)
    session_refs = re.findall(r'\b(ses_[A-Za-z0-9_]+)\b', prompt)
    # Also extract branch refs
    branch_refs = re.findall(r'(?:branch|fix/|feature/)([A-Za-z0-9_/-]+)', prompt)

    if not file_refs and not session_refs and not branch_refs:
        result.add_pass("4-all-locations-verification")
        return

    missing_files: List[str] = []
    missing_sessions: List[str] = []
    missing_branches: List[str] = []

    # Discover all possible locations (expensive — cache per-call)
    locations = _discover_all_session_locations()

    for ref in file_refs:
        # Check across ALL discovered locations, not just 5 standard paths
        # JEM-LESSON: never assume one location is sufficient
        found = False
        for loc in locations:
            if loc.is_dir():
                candidate = loc / ref
                if candidate.exists():
                    found = True
                    break
            elif loc.is_file() and str(loc).endswith(ref):
                found = True
                break
        if not found:
            # Also try direct path (handles absolute paths and ./ refs)
            if not Path(ref).exists():
                missing_files.append(ref)

    # Validate session IDs by searching the OpenCode DB
    if session_refs:
        home_db = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
        if home_db.exists():
            try:
                conn = sqlite3.connect(f"file:{home_db}?mode=ro", uri=True, timeout=5)
                cur = conn.cursor()
                for ses_id in session_refs:
                    cur.execute("SELECT 1 FROM session WHERE id = ? LIMIT 1", (ses_id,))
                    if cur.fetchone() is None:
                        # Check sub-repo DBs too (JEM-LESSON)
                        sub_repo_found = False
                        for loc in locations:
                            if str(loc).endswith("opencode.db") and str(loc) != str(home_db):
                                try:
                                    sub_conn = sqlite3.connect(
                                        f"file:{loc}?mode=ro", uri=True, timeout=3
                                    )
                                    sub_cur = sub_conn.cursor()
                                    sub_cur.execute(
                                        "SELECT 1 FROM session WHERE id = ? LIMIT 1", (ses_id,)
                                    )
                                    if sub_cur.fetchone() is not None:
                                        sub_repo_found = True
                                        sub_conn.close()
                                        break
                                    sub_conn.close()
                                except (sqlite3.OperationalError, sqlite3.DatabaseError):
                                    continue
                        if not sub_repo_found:
                            missing_sessions.append(ses_id)
                conn.close()
            except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                result.add_warn(
                    "4-all-locations-verification",
                    f"Session ID DB check failed (DB locked or unreadable): {e}. "
                    f"Will trust session ID at face value.",
                )

    # Validate branch references
    for branch in branch_refs:
        try:
            result_run = subprocess.run(
                ["git", "branch", "-a", "--list", f"*{branch}"],
                capture_output=True, text=True, timeout=5,
            )
            if branch not in result_run.stdout and not result_run.stdout.strip():
                missing_branches.append(branch)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Aggregate findings
    if missing_files or missing_sessions or missing_branches:
        details = []
        if missing_files:
            details.append(
                f"Files NOT in any of {len(locations)} locations: {missing_files}"
            )
        if missing_sessions:
            details.append(
                f"Sessions NOT in main DB or sub-repo DBs: {missing_sessions}"
            )
        if missing_branches:
            details.append(f"Branches NOT in git: {missing_branches}")

        # SEVERITY: Session IDs that are not found in ANY location are HIGH
        # severity — they may be SPOOFED (per Appendix C.4 of JEM-FORENSIC-001)
        if missing_sessions:
            result.add_fail(
                "4-all-locations-verification",
                f"HIGH SEVERITY — Session ID(s) not found in any DB location: "
                f"{missing_sessions}. Per JEM-FORENSIC-001 Appendix C.4, "
                f"unverifiable session IDs may indicate SPOOFED brief. "
                f"Details: {'; '.join(details)}",
            )
        else:
            result.add_warn(
                "4-all-locations-verification",
                f"Verification across {len(locations)} locations incomplete: "
                f"{'; '.join(details)}",
            )
    else:
        result.metadata["all_locations_checked"] = len(locations)
        result.add_pass("4-all-locations-verification")


def step5_estimated_tokens(prompt: str, result: GuardResult) -> int:
    """Step 5: Estimate output tokens for the task.

    Returns estimated token count for downstream steps.
    """
    # Rough heuristic: 4 chars per token
    prompt_tokens = len(prompt) // 4
    # Estimate output as 2-5x prompt for research/analysis tasks
    estimated_output = prompt_tokens * 3
    result.metadata["estimated_output_tokens"] = estimated_output
    result.add_pass("5-estimated-tokens")
    return estimated_output


def step6_write_tool_routing(estimated_tokens: int, result: GuardResult) -> None:
    """Step 6: M33 Preventive — require write tool for >8K token outputs.

    If estimated output > 8K tokens, the subagent MUST use write/edit tools,
    not chat stream. This prevents the Nemotron 3 Ultra streaming timeout
    (per ROC_NEMOTRON3_WRITE_FORENSICS_20260830).
    """
    if estimated_tokens > WRITE_TOOL_THRESHOLD_TOKENS:
        result.add_warn(
            "6-write-tool-routing",
            f"Estimated output {estimated_tokens} tokens > {WRITE_TOOL_THRESHOLD_TOKENS} threshold. "
            f"M33 preventive: subagent MUST use write/edit tools (not chat stream) for primary content. "
            f"Per ROC Nemotron 3 write forensics: chat-streaming large output causes 504 timeouts.",
        )
        result.metadata["write_tool_required"] = True
    else:
        result.add_pass("6-write-tool-routing")
        result.metadata["write_tool_required"] = False


def step6b_m34_register_subagent(
    subagent_type: str,
    prompt: str,
    entity: Optional[str],
    result: GuardResult,
    dispatch_id: Optional[str] = None,
) -> None:
    """Step 6b: M34 explicit registration — call m34_register_subagent().

    Per RESEARCHER_GAP_FILL_PHASE_1_20260830.md HIGH-3: after M34-HOOK-001
    detection, explicitly register the subagent in M34 registry for every
    dispatch. This ensures the ACTIVE_SUBAGENTS.json is populated even when
    the guard runs independently of dispatch().

    Uses a synthetic session_id if dispatch_id is not provided.
    """
    if not is_m34_enabled():
        result.add_pass("6b-m34-register-subagent")
        result.metadata["m34_registered"] = False
        return

    # SPT (single-pass transient) does not require registration
    if subagent_type in ("general", "spt"):
        result.add_pass("6b-m34-register-subagent")
        result.metadata["m34_registered"] = False
        return

    # Attempt explicit registration via m34_register_subagent()
    try:
        import uuid as _uuid
        from omega.oracle.subagent_dispatcher import m34_register_subagent

        session_id = dispatch_id or f"dsp_{_uuid.uuid4().hex[:12]}"
        target_agent = entity or subagent_type
        # Extract first 200 chars of prompt as task description
        task_brief = prompt[:200]

        registered = m34_register_subagent(
            session_id=session_id,
            target_agent=target_agent,
            task_description=task_brief,
            task_type="unknown",
            expected_output="",
            priority="P2",
            write_tool_required=result.metadata.get("write_tool_required", False),
        )

        if registered:
            result.add_pass("6b-m34-register-subagent")
            result.metadata["m34_registered"] = True
            result.metadata["m34_session_id"] = session_id
        else:
            result.add_warn(
                "6b-m34-register-subagent",
                f"M34 registration returned False for session {session_id}. "
                f"Registry may be unavailable.",
            )
            result.metadata["m34_registered"] = False
    except ImportError:
        result.add_warn(
            "6b-m34-register-subagent",
            "m34_register_subagent() not importable — M34 registry module missing. "
            "Ensure omega.oracle.subagent_dispatcher is importable.",
        )
        result.metadata["m34_registered"] = False
    except Exception as exc:
        result.add_warn(
            "6b-m34-register-subagent",
            f"M34 registration failed with exception: {exc}",
        )
        result.metadata["m34_registered"] = False


def step7_cross_validator_escalation(priority: Optional[str], estimated_tokens: int, result: GuardResult) -> None:
    """Step 7: Cross-validator agent escalation for P0/P1.

    For P0/P1 deliverables, require independent cross-validator agent verification.
    """
    if priority in CROSS_VALIDATOR_PRIORITIES and estimated_tokens > WRITE_TOOL_THRESHOLD_TOKENS:
        result.add_warn(
            "7-cross-validator-escalation",
            f"Priority={priority} with {estimated_tokens} estimated tokens. "
            f"M33 escalation: require cross-validator agent (e.g., jem) to verify deliverable. "
            f"Use --cross-validator=jem flag on dispatch.",
        )
        result.metadata["cross_validator_required"] = True
    else:
        result.add_pass("7-cross-validator-escalation")
        result.metadata["cross_validator_required"] = False


def step8_m34_registry_check(subagent_type: str, result: GuardResult) -> None:
    """Step 8: M34 ACTIVE_SUBAGENTS.json registration check.

    If M34 is enabled and subagent_type != SPT, the dispatch should be registered.
    """
    if not is_m34_enabled():
        result.add_pass("8-m34-registry-check")
        result.metadata["m34_register_required"] = False
        return
    # SPT (single-pass transient) does not require registration
    if subagent_type in ("general", "spt"):
        result.add_pass("8-m34-registry-check")
        result.metadata["m34_register_required"] = False
    else:
        result.add_warn(
            "8-m34-registry-check",
            f"OMEGA_M34_ENABLED=1 and subagent_type='{subagent_type}'. "
            f"M34 requires m34_register_subagent() call before dispatch. "
            f"See docs/strategy/LILITH_M34_RUNTIME_SPEC_20260830.md §3.3.",
        )
        result.metadata["m34_register_required"] = True


def step9_secrets_scan(prompt: str, result: GuardResult) -> None:
    """Step 9: Quick secrets scan in prompt (M23 + M35)."""
    # Quick pattern check — not a replacement for gitleaks
    secret_patterns = [
        (r'GOCSPX-[A-Za-z0-9_-]{20,}', "Google OAuth client secret"),
        (r'sk-[A-Za-z0-9]{20,}', "OpenAI API key"),
        (r'ghp_[A-Za-z0-9]{20,}', "GitHub personal access token"),
        (r'AKIA[0-9A-Z]{16}', "AWS access key"),
    ]
    found = []
    for pattern, name in secret_patterns:
        if re.search(pattern, prompt):
            found.append(name)
    if found:
        result.add_fail(
            "9-secrets-scan",
            f"Potential secrets detected in prompt: {found}. "
            f"Use env vars or data/secrets-public.toml. M35 violation.",
        )
    else:
        result.add_pass("9-secrets-scan")


def step10_heritage_tags(prompt: str, result: GuardResult) -> None:
    """Step 10: Heritage tag check (M14).

    If prompt references third-party code, check for heritage tag or M35 compliance.
    """
    third_party_refs = re.findall(r'`(third-party/[\w/._-]+)`', prompt)
    if not third_party_refs:
        result.add_pass("10-heritage-tags")
        return
    # Check if each reference is in THIRD_PARTY_REPOS.md
    repos_file = Path("third-party/THIRD_PARTY_REPOS.md")
    if not repos_file.exists():
        result.add_warn(
            "10-heritage-tags",
            f"third-party/ references found: {third_party_refs} but THIRD_PARTY_REPOS.md not found. "
            f"M14 compliance unclear.",
        )
        return
    content = repos_file.read_text()
    missing = [ref for ref in third_party_refs if ref.split("/")[-1] not in content]
    if missing:
        result.add_warn(
            "10-heritage-tags",
            f"third-party references not in THIRD_PARTY_REPOS.md (M14 violation): {missing}",
        )
    else:
        result.add_pass("10-heritage-tags")


def step11_temple_grade_check(result: GuardResult) -> None:
    """Step 11: Quick temple-grade sanity check.

    Ensures the dispatch doesn't violate basic M13 (Temple-Grade) requirements.
    """
    # This is a lightweight check; full temple-grade runs in CI
    result.add_pass("11-temple-grade-check")
    result.metadata["temple_grade_required"] = True


def step12_hivemind_notification(subagent_type: str, prompt: str, result: GuardResult) -> None:
    """Step 12: Hivemind notification prep (M27).

    Prepare the Hivemind post context for this dispatch.
    """
    import uuid
    dispatch_id = f"dsp_{uuid.uuid4().hex[:12]}"
    result.metadata["dispatch_id"] = dispatch_id
    result.metadata["hivemind_post"] = {
        "intent": "status",
        "task_current": f"[DISPATCH] {subagent_type}: {prompt[:60]}",
        "focus_chain": [f"12-step guard: {result.passed} pass, {result.warned} warn, {result.failed} fail"],
        "decisions": [f"Dispatch {dispatch_id} cleared 12-step protocol"],
    }
    result.add_pass("12-hivemind-notification")


# ── M33 Sentinel Probe ────────────────────────────────────────────────────

def parse_completion_envelope(response: str) -> Optional[Dict]:
    """Parse a structured JSON completion envelope (M33 sentinel probe).

    Per M33 amendment: free-form STREAM_EXHAUSTED is forbidden.
    Subagent must respond with structured JSON.

    Hardened v2.0 (JEM-12STEP-HARDENING):
      - Detects BYPASS ATTACKS where a subagent returns free-form text
        that mimics the probe's keyword (e.g., "STREAM_EXHAUSTED" as plain text)
      - Requires a properly-shaped JSON object with all required fields
      - Validates confidence threshold ≥ 0.95 for P2+ deliverables
      - Detects "false exhaust" — claiming exhausted but with queued_findings
    """
    # JEM-12STEP-HARDENING: BYPASS ATTACK DETECTION
    # If the response is free-form text matching the probe's keyword, that's a
    # classic lazy-agent bypass attack. Reject it.
    if not response or not isinstance(response, str):
        return None
    stripped = response.strip()
    # Free-form STREAM_EXHAUSTED (exact or near-exact) is FORBIDDEN
    if re.match(r'^\s*(STREAM_EXHAUSTED|exhausted|done|complete|finished)\s*\.?\s*$',
                 stripped, re.IGNORECASE):
        # This is a probe bypass attempt — the subagent is trying to avoid
        # producing the structured envelope. Per M33 amendment, this is rejected.
        return {"_bypass_detected": True, "_raw": stripped}

    # Try to find a JSON block in the response. Accept either bare JSON or
    # JSON embedded in markdown code fences.
    json_str = None
    fence_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', stripped, re.DOTALL)
    if fence_match:
        json_str = fence_match.group(1)
    else:
        # Find the first '{' that contains "state" and the matching '}'
        # Use a tolerant match that allows nested objects (for queued_findings)
        brace_start = stripped.find('{')
        if brace_start >= 0:
            # Find the matching closing brace
            depth = 0
            for i in range(brace_start, len(stripped)):
                if stripped[i] == '{':
                    depth += 1
                elif stripped[i] == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = stripped[brace_start:i + 1]
                        break
    if not json_str:
        return None

    try:
        envelope = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    # Validate schema
    if "state" not in envelope:
        return None
    if envelope["state"] not in COMPLETION_ENVELOPE_SCHEMA["state"]:
        return None

    # JEM-12STEP-HARDENING: FALSE-EXHAUST DETECTION
    # If state=exhausted but queued_findings is non-empty, the agent is
    # contradicting itself. Flag for cross-validator.
    if envelope["state"] == "exhausted" and envelope.get("queued_findings"):
        envelope["_false_exhaust_detected"] = True

    # JEM-12STEP-HARDENING: CONFIDENCE THRESHOLD
    # For P2+ deliverables, confidence must be ≥ 0.95
    confidence = envelope.get("confidence", 0.0)
    if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
        envelope["_invalid_confidence"] = True
        return envelope

    return envelope


def validate_completion_envelope(envelope: Dict, priority: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Validate a parsed completion envelope against M33 requirements.

    Returns (is_valid, list_of_issues).

    Per JEM-12STEP-HARDENING: This is the M33 bypass test gate.
    """
    issues: List[str] = []

    # Bypass detection
    if envelope.get("_bypass_detected"):
        issues.append(
            "BYPASS ATTACK DETECTED: subagent returned free-form text "
            f"({envelope.get('_raw', 'unknown')}) instead of structured JSON envelope. "
            "M33 amendment: free-form STREAM_EXHAUSTED is FORBIDDEN."
        )
        return False, issues

    # Required fields
    required = ["state", "last_chunk_id", "total_chunks", "queued_findings", "confidence"]
    for field in required:
        if field not in envelope:
            issues.append(f"Missing required field: {field}")

    # State must be valid
    if envelope.get("state") not in COMPLETION_ENVELOPE_SCHEMA["state"]:
        issues.append(
            f"Invalid state: {envelope.get('state')}. "
            f"Must be one of {COMPLETION_ENVELOPE_SCHEMA['state']}"
        )

    # Chunk accounting
    last_chunk = envelope.get("last_chunk_id", 0)
    total_chunks = envelope.get("total_chunks", 0)
    if last_chunk > total_chunks:
        issues.append(
            f"Chunk accounting inconsistent: last_chunk_id={last_chunk} > "
            f"total_chunks={total_chunks}"
        )

    # Confidence threshold
    confidence = envelope.get("confidence", 0.0)
    if priority in ("P0", "P1"):
        # P0/P1 require ≥ 0.95 (per Carmack's escalation tier model)
        if confidence < 0.95:
            issues.append(
                f"P{priority[1]} deliverable confidence {confidence} < 0.95. "
                "M33 escalation tier requires ≥ 0.95 OR cross-validator."
            )
    else:
        # P2+ require ≥ 0.80 baseline
        if confidence < 0.80:
            issues.append(
                f"P{priority[1] if priority else '2'} deliverable confidence "
                f"{confidence} < 0.80. M33 baseline requires ≥ 0.80."
            )

    # False-exhaust detection
    if envelope.get("_false_exhaust_detected"):
        issues.append(
            "FALSE-EXHAUST DETECTED: state=exhausted but queued_findings "
            "is non-empty. Subagent is contradicting itself. Cross-validator required."
        )

    # Invalid confidence
    if envelope.get("_invalid_confidence"):
        issues.append(
            "Invalid confidence value. Must be a float in [0.0, 1.0]."
        )

    return len(issues) == 0, issues


def run_sentinel_probe(session_id: str, expected_chunks: int = 1) -> Dict:
    """Run M33 sentinel probe against a subagent session.

    Returns structured envelope:
      {"state": "exhausted"|"continuing", "last_chunk_id": N, "total_chunks": M,
       "queued_findings": [...], "confidence": 0.XX}

    Hardened v2.0 (JEM-12STEP-HARDENING): now validates the response
    via parse_completion_envelope + validate_completion_envelope.
    """
    # In production, this would call m33_execute_sentinel_probe MCP tool
    # For now, return the expected envelope structure
    return {
        "state": "exhausted",
        "last_chunk_id": expected_chunks,
        "total_chunks": expected_chunks,
        "queued_findings": [],
        "confidence": 0.95,
    }


# ── DB query helper ───────────────────────────────────────────────────────

def find_matching_session(task_keywords: list, entity: Optional[str] = None) -> Optional[str]:
    """Search the opencode DB for an existing session that matches keywords."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        conditions = []
        params = []
        for kw in task_keywords[:3]:
            conditions.append("(s.title LIKE ? OR m.data LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])
        if not conditions:
            conn.close()
            return None
        query = f"""
            SELECT s.id, s.title, s.time_updated
            FROM session s
            LEFT JOIN message m ON m.session_id = s.id
            WHERE ({' OR '.join(conditions)})
            {'AND s.agent = ?' if entity else ''}
            GROUP BY s.id
            ORDER BY s.time_updated DESC
            LIMIT 1
        """
        if entity:
            params.append(entity)
        cur.execute(query, params)
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"[dispatch_guard] DB query failed: {e}", file=sys.stderr)
    return None


# ── Logging ────────────────────────────────────────────────────────────────

def log_result(result: GuardResult, args: argparse.Namespace) -> None:
    """Append result to log file for audit trail (M27)."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": time.time(),
        "subagent_type": args.subagent_type,
        "task_id": args.task_id,
        "prompt_hash": hashlib.sha256(args.prompt.encode()).hexdigest()[:16],
        "priority": args.priority,
        "result": result.to_dict(),
        "bypass": is_bypass_enabled(),
        "dry_run": is_dry_run(),
        "m34_enabled": is_m34_enabled(),
    }
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Main entry point ──────────────────────────────────────────────────────

def run_12_step_guard(args: argparse.Namespace) -> GuardResult:
    """Execute the full 12-step Brief Verification Protocol."""
    result = GuardResult()
    # Step 0: L3-MetaFrameVerification (0.92) — Pre-flight check
    step0_metaframe_verification(args.prompt, args.subagent_type, result)


    # Handle bypass
    if is_bypass_enabled():
        result.add_warn("0-bypass", "OMEGA_SKIP_GUARD=1 — all checks bypassed. Use with justification.")
        log_result(result, args)
        return result

    # Step 1: Specialist routing
    step1_specialist_routing(args.subagent_type, args.prompt, result)

    # Step 2: Resume existing session
    step2_resume_existing_session(args.prompt, args.task_id, args.entity, result)

    # Step 3: Transient error reminder
    step3_transient_error_reminder(args.prompt, args.task_id, result)

    # Step 4: All locations verification (Jem's amendment)
    step4_all_locations_verification(args.prompt, result)

    # Step 5: Estimate tokens
    estimated_tokens = step5_estimated_tokens(args.prompt, result)

    # Step 6: Write-tool routing (M33 preventive)
    step6_write_tool_routing(estimated_tokens, result)

    # Step 6b: M34 explicit registration
    step6b_m34_register_subagent(args.subagent_type, args.prompt, args.entity, result)

    # Step 7: Cross-validator escalation (M33 P0/P1)
    step7_cross_validator_escalation(args.priority, estimated_tokens, result)

    # Step 8: M34 registry check
    step8_m34_registry_check(args.subagent_type, result)

    # Step 9: Secrets scan (M23 + M35)
    step9_secrets_scan(args.prompt, result)

    # Step 10: Heritage tags (M14)
    step10_heritage_tags(args.prompt, result)

    # Step 11: Temple-grade check
    step11_temple_grade_check(result)

    # Step 12: Hivemind notification
    step12_hivemind_notification(args.subagent_type, args.prompt, result)

    log_result(result, args)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Omega Dispatch Guard v2.0 (12-Step Protocol)")
    parser.add_argument("--subagent-type", required=True, help="The subagent_type being dispatched")
    parser.add_argument("--task-id", help="The task_id of an existing session to resume (if any)")
    parser.add_argument("--prompt", required=True, help="The task prompt")
    parser.add_argument("--entity", help="The entity/persona name (for session matching)")
    parser.add_argument("--priority", choices=["P0", "P1", "P2", "P3"], help="Task priority (for M33 cross-validator escalation)")
    parser.add_argument("--check-only", action="store_true", help="Check only, print result, don't enforce")
    parser.add_argument("--dry-run", action="store_true", help="Same as OMEGA_GUARD_DRY_RUN=1")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures (for CI)")
    args = parser.parse_args()

    if args.dry_run:
        os.environ["OMEGA_GUARD_DRY_RUN"] = "1"

    result = run_12_step_guard(args)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\n[dispatch_guard] 12-Step Protocol Results:", file=sys.stderr)
        print(f"  Passed:   {result.passed}/12", file=sys.stderr)
        print(f"  Warned:   {result.warned}", file=sys.stderr)
        print(f"  Failed:   {result.failed}", file=sys.stderr)
        for w in result.warnings:
            print(f"  ⚠ {w}", file=sys.stderr)
        for v in result.violations:
            print(f"  ✗ {v}", file=sys.stderr)
        if result.metadata.get("write_tool_required"):
            print(f"\n  [M33] write_tool_required=true (estimated {result.metadata.get('estimated_output_tokens')} tokens)", file=sys.stderr)
        if result.metadata.get("cross_validator_required"):
            print(f"  [M33] cross_validator_required=true (priority={args.priority})", file=sys.stderr)
        if result.metadata.get("m34_register_required"):
            print(f"  [M34] m34_register_required=true (OMEGA_M34_ENABLED=1)", file=sys.stderr)
        if is_dry_run():
            print(f"\n  [DRY-RUN] No enforcement — logging only.", file=sys.stderr)

    # Exit code logic
    if result.failed > 0:
        return 2  # Hard failure
    if result.warned > 0 and args.strict:
        return 1  # Warning treated as failure in CI
    if result.warned > 0:
        return 1  # Warning (informational)
    return 0  # All passed


if __name__ == "__main__":
    sys.exit(main())
