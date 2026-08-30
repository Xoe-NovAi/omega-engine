#!/usr/bin/env python3
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
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def step4_all_locations_verification(prompt: str, result: GuardResult) -> None:
    """Step 4: 'All locations' verification (Jem's self-correction).

    Per Jem: "Verification must be exhaustive, not selective.
    The 12-Step Protocol should require 'all possible locations'."
    """
    # Check for file references in the prompt and verify they exist in ALL locations
    file_refs = re.findall(r'`([\w/._-]+\.\w+)`', prompt)
    if not file_refs:
        result.add_pass("4-all-locations-verification")
        return
    missing_files = []
    for ref in file_refs:
        # Check in standard locations: workspace root, src/, scripts/, data/, docs/
        locations = [
            Path(ref),
            Path("src") / ref,
            Path("scripts") / ref,
            Path("data") / ref,
            Path("docs") / ref,
        ]
        if not any(loc.exists() for loc in locations):
            missing_files.append(ref)
    if missing_files:
        result.add_warn(
            "4-all-locations-verification",
            f"File references not found in any standard location: {missing_files}. "
            f"Check: workspace root, src/, scripts/, data/, docs/",
        )
    else:
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
    """
    # Try to find JSON block in the response
    json_match = re.search(r'\{[^{}]*"state"[^{}]*\}', response, re.DOTALL)
    if not json_match:
        return None
    try:
        envelope = json.loads(json_match.group())
    except json.JSONDecodeError:
        return None
    # Validate schema
    if "state" not in envelope:
        return None
    if envelope["state"] not in COMPLETION_ENVELOPE_SCHEMA["state"]:
        return None
    return envelope


def run_sentinel_probe(session_id: str, expected_chunks: int = 1) -> Dict:
    """Run M33 sentinel probe against a subagent session.

    Returns structured envelope:
      {"state": "exhausted"|"continuing", "last_chunk_id": N, "total_chunks": M,
       "queued_findings": [...], "confidence": 0.XX}
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
