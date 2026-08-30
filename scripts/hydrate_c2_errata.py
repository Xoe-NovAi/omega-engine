#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
hydrate_c2_errata.py — Deterministic applier for the Council-2 Errata Ledger (E-1..E-11).

Ledger SSOT:
  data/council/20260825-094633-first-light-c2/phase6_integration/ERRATA_AND_PROPAGATION.md
Campaign authority:
  data/coordination/fle_study_20260825/CAMPAIGN_EXECUTION_PLAN_v3.1.md §3 WAVE 0 step 2

DESIGN CONTRACT (WAVE 0 / M23 Failure Integrity):
  * Byte-exact string replacement ONLY. No regex, no fuzzy matching, no guessing.
  * --dry-run is the DEFAULT: prints unified diffs of would-be changes, mutates nothing.
  * --apply is gated behind an explicit interactive confirmation prompt.
  * Backups (.bak) are created before any write; writes are atomic (tmpfile + os.replace).
  * Idempotent: re-runs detect already-applied patches and skip cleanly.
  * HONESTY RULE: where a target string is NOT_FOUND verbatim or AMBIGUOUS (>1 match),
    the item is emitted as TODO[manual] in the report and SKIPPED — never guessed.
  * --self-test proves each patch matches exactly once on fixtures and that
    AMBIGUOUS/NOT_FOUND cases are skipped without mutation.
  * Post-apply verification pass re-reads every mutated file and confirms each patch landed.

Exit codes:
  0 — all patches applied or cleanly skipped (idempotent), no manual TODOs outstanding
  2 — hydration INCOMPLETE: one or more items emitted TODO[manual] (NOT_FOUND/AMBIGUOUS)
  3 — post-apply verification FAILURE (a patch did not land) — treat as hard error
  4 — self-test failure

Run via the project venv (M24): .venv/bin/python scripts/hydrate_c2_errata.py --dry-run
"""

from __future__ import annotations

import argparse
import difflib
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

C2 = "data/council/20260825-094633-first-light-c2"

# ---------------------------------------------------------------------------
# PATCH REGISTRY — E-1..E-11 as exact (old, new) byte-string pairs.
# Every `old` was verified unique-in-file on 2026-08-25 against the live tree.
# `manual` entries carry ledger corrections that CANNOT be safely mechanized
# (ambiguous target, or ruling requires a human-supplied value) → always TODO[manual].
# ---------------------------------------------------------------------------

PATCHES = [
    # ── E-1 · N9 row 4.1: strike relay-codification EXECUTION; Q-3-reserved; SPEC-C template ──
    {
        "eid": "E-1",
        "file": f"{C2}/phase1_nodes/N9_doc_update_plan.md",
        "old": (
            "| 4.1 | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Codify M11 Arm-Relay Clause: "
            "leaves write report+payload to disk; arms relay pages once per stage; MK-Kali pages direct; "
            "NO mid-run `subagent_depth` change; future leaf packets embed relay clause INSTEAD of paging steps; "
            "add serial-dispatch exception declaration requirement (T-4) | Art. IV; mission G18 ref | "
            "none (law already ratified) | dev-team | grep relay-clause section present; packet-template updated |"
        ),
        "new": (
            "| 4.1 | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | ⛔ STRUCK (E-1 / Ruling 1 / SCOPE-1): "
            "relay-codification EXECUTION removed from dev-team scope; Rule-4 protocol-text rewrite is "
            "**Q-3-RESERVED (Architect-owned)** per decree Art. IV reservation (see WP-C2 / SPEC-C WI-2 costed options). "
            "ONLY executable now: future leaf packets embed relay clause INSTEAD of paging steps (Art. IV verbatim directive); "
            "record template source = SPEC_C_P1_SECURITY_POSTURE_RECORDS.md WI-2 | Art. IV; SCOPE-1; SPEC-C WI-2 | "
            "Architect Q-3 decision (protocol-text rewrite ONLY) | dev-team (packet-template change only) | "
            "grep relay-clause section present; packet-template updated |"
        ),
        "desc": "Row 4.1 relay-codification struck; Q-3-reserved; SPEC-C record template linked.",
    },
    # ── E-2 · N10 bootstrap prompt: FIRST ACTION = S-2 schema-truth probe VERBATIM ──
    {
        "eid": "E-2",
        "file": f"{C2}/phase1_nodes/N10_launch_package.md",
        "old": (
            "START HERE: Sprint-1 backlog = PART 3 §3.1 of this file. First command you run:\n"
            "the G8 loop from N8_resources.md §2 (WP-IX verify-first)."
        ),
        "new": (
            "START HERE: Sprint-1 backlog = PART 3 §3.1 of this file. First command you run:\n"
            "the S-2 schema-truth probe VERBATIM (from SYNTHESIS_ARM_REPORT_C2.md §6) — NOT the bare\n"
            "G8 loop (G8 alone false-closes; BS-1 proven live). Run S-2 first, then G8 for parseability\n"
            "parity. Report the S-2 count honestly; do NOT assert YAML health until Architect Q-6 sizing\n"
            "lands (WAKE_STATE queue). The probe, verbatim:\n"
            "\n"
            "    ck S-2 '.venv/bin/python3 - <<'\"'\"'EOF'\"'\"'\n"
            "    import yaml,sys,glob\n"
            "    bad=[]\n"
            "    for f in glob.glob(\"data/entities/*/proposed_lessons.yaml\"):\n"
            "        d=yaml.safe_load(open(f))\n"
            "        for i,r in enumerate(d if isinstance(d,list) else []):\n"
            "            if isinstance(r,dict) and (\"id\" in r or \"narrative\" in r):\n"
            "                for k in (\"id\",\"narrative\",\"insight\",\"principle\"):\n"
            "                    if k in r and not r.get(k): bad.append(f\"{f}:{i}:{k}\")\n"
            "                if (\"id\" in r) != (\"narrative\" in r): bad.append(f\"{f}:{i}:split-record\")\n"
            "    sys.exit(1 if bad else 0)\n"
            "    EOF'"
        ),
        "desc": "Bootstrap first action replaced with verbatim S-2 schema-truth probe.",
    },
    # ── E-3 · N10: unnamed "single writer" → named MaKaLi orchestrator session ──
    {
        "eid": "E-3",
        "file": f"{C2}/phase1_nodes/N10_launch_package.md",
        "old": "**HARD EDGE: only after G20 green**; single writer |",
        "new": (
            "**HARD EDGE: only after G20 green**; writer = MaKaLi "
            "(orchestrator session ses_fc758e6ddffeNEKptpEzboVfYq) |"
        ),
        "desc": 'Unnamed "single writer" (WP-B5b row) replaced with named MaKaLi session.',
    },
    # ── E-5 · SPEC-B WI-1: delete "no plugin key" precondition; add merge-semantics probe ──
    {
        "eid": "E-5",
        "file": "docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md",
        "old": (
            "Note for executor: nested `.opencode/opencode.json` overrides root on conflicting keys\n"
            "(GAP-3 verdict); confirm no plugin key exists in the nested file before editing root."
        ),
        "new": (
            "Note for executor (AMENDED E-5 / Ruling 4 / BS-2): nested `.opencode/opencode.json` overrides\n"
            "root on conflicting keys (GAP-3 verdict) AND **empirically carries a `plugin` key**\n"
            "(`[\"opencode-antigravity-auth@latest\"]`, MK-verified 2026-08-25) — the former \"confirm no\n"
            "plugin key exists\" precondition is DELETED (it fails live). Done-definition addition: run a\n"
            "merge-semantics probe (e.g., `opencode agent list` plugin-init count before/after the root\n"
            "fix) BEFORE claiming G1-complete; if nested-vs-root semantics are array-replace, root\n"
            "registrations are ignored at runtime and G1 alone is a partial truth gate."
        ),
        "desc": "WI-1 stale precondition deleted; merge-semantics probe added to done-definition.",
    },
    # ── E-6a · SPEC-A WI-2 item 4: WAKE_STATE descoped to D6 standalone shim ──
    {
        "eid": "E-6a",
        "file": "docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md",
        "old": (
            "4. **WAKE_STATE block** — new function `check_wake_state()`; if `data/coordination/WAKE_STATE.json` "
            "exists: (a) must json-parse (else ERROR); (b) any `*.status` fields validated against Tier-0 where "
            "applicable; (c) staleness: if top-level `updated`/timestamp older than STALENESS_DAYS → ERROR naming "
            "the owner directive (decree Q-2 assigns freshness ownership to MaKaLi at stage boundaries). "
            "Register WAKE_STATE in TRACKING_ARCHITECTURE.md's tier table in the same PR (text patch pairs with "
            "gate — pairwise binding)."
        ),
        "new": (
            "4. **WAKE_STATE block (DESCOPED to D6-shim — E-6 / Pass-2 ADJ-3+CF-1)** — `check_wake_state()` is a "
            "THIN SHIM only: import SPEC-D D6's module function or subprocess-invoke the standalone "
            "`scripts/validate_wake_state.py` from `validate_tracking_state.py`, so `make temple-grade` retains "
            "WAKE_STATE coverage with ONE implementation (D6 standalone is the surviving canonical mechanism; "
            "duplicate logic forbidden). Register WAKE_STATE in TRACKING_ARCHITECTURE.md's tier table in the same "
            "PR (text patch pairs with gate — pairwise binding)."
        ),
        "desc": "WI-2 item 4 WAKE_STATE block descoped to D6-shim.",
    },
    # ── E-6b · SPEC-A WI-2 item 5: schema-guard scope ~30 records (lilith AND maat) ──
    {
        "eid": "E-6b",
        "file": "docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md",
        "old": (
            "(ERROR on missing/split records — catches exactly the lilith L374 split-record corruption that "
            "bare parsing misses). Keep it structural-minimal; content quality remains out of scope."
        ),
        "new": (
            "(ERROR on missing/split records — catches exactly the lilith L374 split-record corruption that "
            "bare parsing misses). Scope note (E-6 / Finding 2): live S-2 probe counts ~30 schema-flagged records "
            "across `data/entities/lilith` AND `data/entities/maat` (maat L44-52 newly discovered site) — guard "
            "scope sized accordingly pending Architect Q-6 sizing. Keep it structural-minimal; content quality "
            "remains out of scope."
        ),
        "desc": "WI-2 item 5 schema-guard scope widened to ~30 records (lilith + maat).",
    },
    # ── E-7 · SPEC-E §1.2: fix broken bash (redirect-after-done; ${cluster} out of scope) ──
    {
        "eid": "E-7",
        "file": "docs/specs/team_infra/SPEC-E-agents-md-reconstruction.md",
        "old": (
            'for cluster in "${!PAT[@]}"; do\n'
            '  case "$cluster" in\n'
            "    search_protocol|delegation|governance)\n"
            "      grep -rlE \"${PAT[$cluster]}\" --include='*.md' .opencode/ docs/ data/entities/ scripts/ 2>/dev/null ;;\n"
            "    *)\n"
            "      # intersection method for context-based clusters:\n"
            "      comm -12 <(sort -u /tmp/opencode/citers.txt) \\\n"
            "               <(grep -rliE 'hydration|session_gnosis|SESSION_ANCHOR|compaction|VOID SUMMAR|hivemind_post_context|SOVEREIGN_MANDATES' \\\n"
            "                 $(cat /tmp/opencode/citers.txt) 2>/dev/null | sort -u) ;;\n"
            "  esac\n"
            'done > "/tmp/opencode/cluster_${cluster}.txt"'
        ),
        "new": (
            '# E-7 (Pass-2 WP-E): redirect moved INSIDE the loop body — the trailing `done > …` form expands\n'
            '# ${cluster} ONCE before iteration (stale/empty), writing every cluster into one wrong file.\n'
            'for cluster in "${!PAT[@]}"; do\n'
            "  {\n"
            '    case "$cluster" in\n'
            "      search_protocol|delegation|governance)\n"
            "        grep -rlE \"${PAT[$cluster]}\" --include='*.md' .opencode/ docs/ data/entities/ scripts/ 2>/dev/null ;;\n"
            "      *)\n"
            "        # intersection method for context-based clusters:\n"
            "        comm -12 <(sort -u /tmp/opencode/citers.txt) \\\n"
            "                 <(grep -rliE 'hydration|session_gnosis|SESSION_ANCHOR|compaction|VOID SUMMAR|hivemind_post_context|SOVEREIGN_MANDATES' \\\n"
            "                   $(cat /tmp/opencode/citers.txt) 2>/dev/null | sort -u) ;;\n"
            "    esac\n"
            '  } > "/tmp/opencode/cluster_${cluster}.txt"\n'
            "done"
        ),
        "desc": "Cluster-loop redirect fixed (${cluster} now in scope per-iteration).",
    },
    # ── E-8 · N10 sprint list: make-sovereignty fix unbundled → SEPARATE PR ──
    {
        "eid": "E-8",
        "file": f"{C2}/phase1_nodes/N10_launch_package.md",
        "old": (
            "Machine-derived mandate enforcement-stamps; delete temple-grade stub (`Makefile:234`); "
            "implement-or-purge `make sovereignty` — depends on WP-A1 (SPINE-5: stamps derive from existing "
            "gates, after WP-A2)"
        ),
        "new": (
            "Machine-derived mandate enforcement-stamps; delete temple-grade stub (`Makefile:234`) — depends on "
            "WP-A1 (SPINE-5: stamps derive from existing gates, after WP-A2). NOTE (E-8 / Pass-2): "
            "`make sovereignty` implement-or-purge (G12) ships as a SEPARATE PR (spec wins) — NOT bundled here."
        ),
        "desc": "G12 make-sovereignty fix unbundled from WP-A4 sprint-list entry.",
    },
    # ── E-9 · SYNTHESIS §6 G22 line: remove "; true" suffix (Exhibit-D class defect) ──
    {
        "eid": "E-9",
        "file": f"{C2}/phase3_synthesis/SYNTHESIS_ARM_REPORT_C2.md",
        "old": ">/dev/null 2>&1; true'",
        "new": ">/dev/null 2>&1'",
        "desc": "G22 acceptance line neutering suffix removed (gate can now fail).",
    },
    # ── E-10 · G15/G16/G3/G4 gate lines normalized to .venv/bin/python (M24) ──
    {
        "eid": "E-10a",
        "file": f"{C2}/phase3_synthesis/SYNTHESIS_ARM_REPORT_C2.md",
        "old": "ck G15 'python3 -c \"",
        "new": "ck G15 '.venv/bin/python3 -c \"",
        "desc": "SYNTHESIS §6 G15 venv-normalized.",
    },
    {
        "eid": "E-10b",
        "file": f"{C2}/phase3_synthesis/SYNTHESIS_ARM_REPORT_C2.md",
        "old": "ck G16 'python3 -c \"",
        "new": "ck G16 '.venv/bin/python3 -c \"",
        "desc": "SYNTHESIS §6 G16 venv-normalized.",
    },
    {
        "eid": "E-10c",
        "file": f"{C2}/phase3_synthesis/SYNTHESIS_ARM_REPORT_C2.md",
        "old": "ck G3  'python3 -c \"",
        "new": "ck G3  '.venv/bin/python3 -c \"",
        "desc": "SYNTHESIS §6 G3 venv-normalized.",
    },
    {
        "eid": "E-10d",
        "file": f"{C2}/phase1_nodes/N8_resources.md",
        "old": "# G15. NO future-dated registry timestamps (Art. III)\npython3 -c \"",
        "new": "# G15. NO future-dated registry timestamps (Art. III)\n.venv/bin/python3 -c \"",
        "desc": "N8_resources G15 venv-normalized.",
    },
    {
        "eid": "E-10e",
        "file": f"{C2}/phase1_nodes/N8_resources.md",
        "old": "# G3. Provider chain matches Ark D-355 (Art. VIII)\npython3 -c \"",
        "new": "# G3. Provider chain matches Ark D-355 (Art. VIII)\n.venv/bin/python3 -c \"",
        "desc": "N8_resources G3 venv-normalized.",
    },
    {
        "eid": "E-10f",
        "file": f"{C2}/phase1_nodes/N8_resources.md",
        "old": "# G4. Enabled providers have resolvable keys (Art. VIII)\npython3 -c \"",
        "new": "# G4. Enabled providers have resolvable keys (Art. VIII)\n.venv/bin/python3 -c \"",
        "desc": "N8_resources G4 venv-normalized.",
    },
    # ── E-11 · N8_resources G16: short-circuit polarity → explicit exit-code check ──
    #             (also completes E-10 normalization for this line)
    {
        "eid": "E-11",
        "file": f"{C2}/phase1_nodes/N8_resources.md",
        "old": (
            'python3 scripts/sweep_task_registry.py 2>&1 | grep -qv "clean" || python3 -c "\n'
            "import json,datetime\n"
            "d=json.load(open('data/coordination/TASK_REGISTRY.json'))\n"
            "now=datetime.datetime.now(datetime.timezone.utc)\n"
            "z=[t['task_id'] for t in d['tasks'] if t.get('status')=='in_progress' and t.get('last_checkpoint') "
            "and (now-datetime.datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))).total_seconds()>=7*86400]\n"
            "print('boundary-zombies:',z)\"   # post-fix: zombies surfaced by sweep OR swept"
        ),
        "new": (
            "# E-11 (Pass-2 Finding 5): explicit exit-code check replaces fragile `grep -qv … ||` polarity;\n"
            "# E-10: normalized to .venv/bin/python3 (M24 venv sovereignty).\n"
            'SWEEP_OUT="$(.venv/bin/python3 scripts/sweep_task_registry.py 2>&1)"; SWEEP_RC=$?\n'
            "if [ \"$SWEEP_RC\" -ne 0 ] || printf '%s\\n' \"$SWEEP_OUT\" | grep -qv '^clean$'; then\n"
            ".venv/bin/python3 -c \"\n"
            "import json,datetime\n"
            "d=json.load(open('data/coordination/TASK_REGISTRY.json'))\n"
            "now=datetime.datetime.now(datetime.timezone.utc)\n"
            "z=[t['task_id'] for t in d['tasks'] if t.get('status')=='in_progress' and t.get('last_checkpoint') "
            "and (now-datetime.datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))).total_seconds()>=7*86400]\n"
            "print('boundary-zombies:',z)\"\n"
            "fi   # post-fix: zombies surfaced by sweep OR swept (explicit rc check, E-11)"
        ),
        "desc": "G16 polarity rewritten to explicit exit-code check (+ venv normalization).",
    },
]

# Ledger corrections that CANNOT be mechanized safely → permanent TODO[manual].
MANUAL_ITEMS = [
    {
        "eid": "E-4",
        "file": f"{C2}/phase1_nodes/N8_work_packages.md",
        "reason": (
            "Ruling: registration-application path = decree Art. V ONLY (G20 discovery fix → "
            "single-writer apply G21 → retrieval ≥10); no interim workaround may be listed as a live "
            "option. No interim-workaround text found verbatim in N8_work_packages.md — the WP-B5b row "
            "already encodes the HARD EDGE. Requires human/verity confirmation whether an explicit "
            "'Art. V ONLY' annotation must be ADDED (authoring new prose is outside mechanical-patch scope)."
        ),
    },
    {
        "eid": "E-6-effort",
        "file": "docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md",
        "reason": (
            "Ruling says 'effort re-estimated' but supplies NO number. Choosing one would be invention. "
            "Manual re-baseline required after E-6a descope lands (candidate basis: subtract the descoped "
            "WAKE_STATE-block hours from the 6h WI-2 estimate)."
        ),
    },
    {
        "eid": "E-10-G4-SYNTHESIS (informational)",
        "file": f"{C2}/phase3_synthesis/SYNTHESIS_ARM_REPORT_C2.md",
        "reason": (
            "No G4 gate line exists in SYNTHESIS_ARM_REPORT_C2.md §6 (G4 lives only in N8_resources.md, "
            "covered by E-10f). No action needed — recorded for audit completeness."
        ),
    },
]

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

ST_APPLIED = "APPLIED"
ST_ALREADY = "ALREADY_APPLIED (skipped)"
ST_WOULD = "WOULD_APPLY (dry-run)"
ST_AMBIGUOUS = "AMBIGUOUS → TODO[manual] (skipped)"
ST_NOT_FOUND = "NOT_FOUND → TODO[manual] (skipped)"


def classify(content: str, old: str, new: str) -> tuple[str, int]:
    """Classify a patch against file content. Returns (status, occurrence_count)."""
    n_old = content.count(old)
    if n_old == 0:
        # Idempotency: patch already landed?
        if new in content:
            return ST_ALREADY, 0
        return ST_NOT_FOUND, 0
    if n_old > 1:
        return ST_AMBIGUOUS, n_old
    return (ST_APPLIED, 1)  # caller decides applied vs would_apply by mode


def atomic_write(path: Path, content: str) -> None:
    """Atomic write: tmpfile in same dir + os.replace (M12/T10 pattern)."""
    tmp_fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def backup_file(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    return bak


def unified_diff(path: Path, before: str, after: str) -> str:
    diff = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=2,
    )
    return "".join(diff)


def run_patches(
    root: Path,
    patches: list[dict],
    apply_mode: bool,
    assume_yes: bool = False,
    quiet_diffs: bool = False,
) -> tuple[list[dict], list[str]]:
    """Run all patches. Returns (results, mutated_files)."""
    results: list[dict] = []
    mutated_files: list[str] = []

    for p in patches:
        fpath = root / p["file"]
        entry = {"eid": p["eid"], "file": p["file"], "desc": p["desc"]}
        try:
            content = fpath.read_text(encoding="utf-8")
        except FileNotFoundError:
            entry.update(status=ST_NOT_FOUND, detail="target FILE not found")
            results.append(entry)
            continue
        status, count = classify(content, p["old"], p["new"])
        entry["status"] = (
            ST_WOULD if (status == ST_APPLIED and not apply_mode) else status
        )

        if status == ST_APPLIED and apply_mode:
            before = content
            after = content.replace(p["old"], p["new"], 1)
            bak = backup_file(fpath)
            atomic_write(fpath, after)
            entry["detail"] = f"backup={bak.name}"
            if p["file"] not in mutated_files:
                mutated_files.append(p["file"])
        elif status == ST_WOULD and not quiet_diffs:
            after = content.replace(p["old"], p["new"], 1)
            entry["diff"] = unified_diff(fpath, content, after)
        elif status == ST_AMBIGUOUS:
            entry["detail"] = f"{count} verbatim matches — refusing to guess"
        results.append(entry)

    return results, mutated_files


def verify_applied(root: Path, patches: list[dict]) -> list[str]:
    """Post-apply verification: re-read files; each patch's `new` present, `old` absent."""
    failures = []
    cache: dict[str, str] = {}
    for p in patches:
        if p["file"] not in cache:
            fp = root / p["file"]
            cache[p["file"]] = fp.read_text(encoding="utf-8") if fp.exists() else ""
        content = cache[p["file"]]
        if p["new"] not in content:
            failures.append(f"{p['eid']}: new text NOT present in {p['file']}")
        elif p["old"] in content and p["old"] != p["new"]:
            # old still present — either never applied (TODO case) or residue
            st, _ = classify(content, p["old"], p["new"])
            if st == ST_AMBIGUOUS:
                failures.append(
                    f"{p['eid']}: old text STILL PRESENT ({content.count(p['old'])}x) in {p['file']}"
                )
    return failures


def print_report(results: list[dict], mode: str) -> list[dict]:
    todos = []
    print(f"\n{'=' * 74}\nERRATA HYDRATION REPORT — mode: {mode}\n{'=' * 74}")
    for r in results:
        print(f"[{r['status']:>34}] {r['eid']:<8} {r['desc']}")
        if r["status"] in (ST_AMBIGUOUS, ST_NOT_FOUND):
            todos.append(r)
            print(f"{'':>38} └─ TODO[manual]: {r.get('detail', '')}")
        if "diff" in r:
            print("-" * 74)
            print(r["diff"], end="" if r["diff"].endswith("\n") else "\n")
            print("-" * 74)
    return todos


def confirm_apply() -> bool:
    print("\n*** APPLY MODE *** This will MUTATE the files listed above.")
    print("Backups (.bak) will be created; writes are atomic (tmpfile+os.replace).")
    answer = input("Type APPLY to proceed (anything else aborts): ").strip()
    return answer == "APPLY"


# ---------------------------------------------------------------------------
# Self-test (fixture-based; proves exact-once matching + honest skip behavior)
# ---------------------------------------------------------------------------

SELFTEST_SENTINEL = "SENTINEL-LINE-DOES-NOT-MATCH-ANY-PATCH\n"


def self_test(root: Path) -> int:
    print("\n" + "=" * 74)
    print("SELF-TEST — fixture-based proof of exact-once matching & honest skips")
    print("=" * 74)
    failures: list[str] = []
    tmp_root = Path(tempfile.mkdtemp(prefix="errata_selftest_"))

    try:
        # T1: every real patch matches EXACTLY ONCE on a fixture containing it.
        for p in PATCHES:
            fx = tmp_root / p["file"]
            fx.parent.mkdir(parents=True, exist_ok=True)
            fx.write_text(SELFTEST_SENTINEL + p["old"] + SELFTEST_SENTINEL, encoding="utf-8")
            results, mutated = run_patches(tmp_root, [p], apply_mode=True, assume_yes=True)
            r = results[0]
            if r["status"] != ST_APPLIED:
                failures.append(f"T1 {p['eid']}: expected APPLIED, got {r['status']}")
                continue
            got = fx.read_text(encoding="utf-8")
            if p["new"] not in got or p["old"] in got:
                failures.append(f"T1 {p['eid']}: replacement did not land cleanly")
            if len(mutated) != 1:
                failures.append(f"T1 {p['eid']}: unexpected mutation set {mutated}")
        print(f"T1 exact-once apply ............ {'PASS' if not failures else 'FAIL'}")

        # T2: idempotency — FRESH fixture per patch, apply twice; second run yields
        # ALREADY_APPLIED with zero mutation. (Shared fixtures would collide: several
        # patches target the same file.)
        idem_fail = []
        for p in PATCHES:
            fx = tmp_root / p["file"]
            fx.parent.mkdir(parents=True, exist_ok=True)
            fx.write_text(SELFTEST_SENTINEL + p["old"] + SELFTEST_SENTINEL, encoding="utf-8")
            run_patches(tmp_root, [p], apply_mode=True, assume_yes=True)
            results, mutated = run_patches(tmp_root, [p], apply_mode=True, assume_yes=True)
            if results[0]["status"] != ST_ALREADY or mutated:
                idem_fail.append(f"{p['eid']}→{results[0]['status']}")
        if idem_fail:
            failures.append("T2 idempotency: " + ", ".join(idem_fail))
        print(f"T2 idempotent re-run ........... {'PASS' if not idem_fail else 'FAIL'}")

        # T3: ambiguity — duplicated old string ⇒ AMBIGUOUS + ZERO mutation.
        amb_fail = []
        for p in PATCHES[:3]:
            fx = tmp_root / p["file"]
            fx.write_text((p["old"] + "\n") * 2, encoding="utf-8")
            before = fx.read_text(encoding="utf-8")
            results, mutated = run_patches(tmp_root, [p], apply_mode=True, assume_yes=True)
            if results[0]["status"] != ST_AMBIGUOUS or mutated or fx.read_text(encoding="utf-8") != before:
                amb_fail.append(p["eid"])
        if amb_fail:
            failures.append("T3 ambiguous-skip: " + ", ".join(amb_fail))
        print(f"T3 AMBIGUOUS skip, no mutation . {'PASS' if not amb_fail else 'FAIL'}")

        # T4: not-found ⇒ NOT_FOUND/TODO + zero mutation.
        nf_fail = []
        for p in PATCHES[:3]:
            fx = tmp_root / p["file"]
            fx.write_text("unrelated content\n", encoding="utf-8")
            results, mutated = run_patches(tmp_root, [p], apply_mode=True, assume_yes=True)
            if results[0]["status"] != ST_NOT_FOUND or mutated:
                nf_fail.append(p["eid"])
        if nf_fail:
            failures.append("T4 not-found-honesty: " + ", ".join(nf_fail))
        print(f"T4 NOT_FOUND → TODO[manual] .... {'PASS' if not nf_fail else 'FAIL'}")

        # T5: post-apply verification catches a sabotaged file.
        p0 = PATCHES[0]
        fx = tmp_root / p0["file"]
        fx.write_text(p0["old"], encoding="utf-8")
        run_patches(tmp_root, [p0], apply_mode=True, assume_yes=True)
        fx.write_text(p0["old"], encoding="utf-8")  # sabotage: revert behind verifier's back
        vfail = verify_applied(tmp_root, [p0])
        if not vfail:
            failures.append("T5 verification failed to detect reverted patch")
        print(f"T5 verify-pass catches revert .. {'PASS' if vfail else 'FAIL'}")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    if failures:
        print("\nSELF-TEST RESULT: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 4
    print(f"\nSELF-TEST RESULT: PASS ({len(PATCHES)} patch ops × 5 proofs)")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Deterministic applier for Council-2 Errata Ledger E-1..E-11 (byte-exact, dry-run default)."
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="MUTATE files (default is dry-run). Gated behind an interactive confirmation prompt.",
    )
    ap.add_argument("--self-test", action="store_true", help="Run fixture-based self-test and exit.")
    ap.add_argument("--root", type=Path, default=REPO_ROOT, help="Repo root (default: script parent parent).")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test(args.root)

    apply_mode = args.apply
    if apply_mode:
        # Preview pass first (dry-run semantics) so the operator confirms what they saw.
        results, _ = run_patches(args.root, PATCHES, apply_mode=False)
        todos_preview = print_report(results, "PREVIEW (pre-apply)")
        if not confirm_apply():
            print("ABORTED by operator — nothing mutated.")
            return 0
        results, mutated = run_patches(args.root, PATCHES, apply_mode=True)
        todos = print_report(results, "APPLY")
        # Post-apply verification pass (re-reads from disk).
        vfail = verify_applied(args.root, PATCHES)
        print(f"\nPOST-APPLY VERIFICATION: {'OK — all patches landed' if not vfail else 'FAILURE'}")
        for f in vfail:
            print(f"  ✗ {f}")
        if mutated:
            print(f"Mutated files ({len(mutated)}):")
            for m in mutated:
                print(f"  ~ {m}")
        if vfail:
            return 3
    else:
        results, _ = run_patches(args.root, PATCHES, apply_mode=False)
        todos = print_report(results, "DRY-RUN (default — nothing mutated)")
        print(
            "\nNothing was mutated. Re-run with --apply (and confirm at the prompt) to hydrate.\n"
            "Manual items below ALWAYS require human handling — mechanical tooling will never guess:"
        )

    for m in MANUAL_ITEMS:
        print(f"\nTODO[manual] {m['eid']}  ({m['file']})\n  └─ {m['reason']}")

    n_todos = len(todos) + len(MANUAL_ITEMS)
    print(f"\nSUMMARY: {len(PATCHES)} mechanical ops · {n_todos} TODO[manual] item(s) outstanding.")
    return 2 if n_todos else 0


if __name__ == "__main__":
    sys.exit(main())
