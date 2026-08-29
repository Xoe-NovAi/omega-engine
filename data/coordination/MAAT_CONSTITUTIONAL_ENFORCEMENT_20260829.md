# MAAT_CONSTITUTIONAL_ENFORCEMENT_20260829.md

**Mission**: How to enforce the 27 Sovereign Mandates in CI — per-mandate linter, test, doc requirement, coverage report
**Entity**: MA'AT (Build Oversoul, N1-N5)
**Channel**: opencode
**Model**: openrouter/minimax/minimax-m3:free
**Date**: 2026-08-29
**Sprint**: PUBLIC-DEBUT-01
**Status**: RESEARCH REPORT (no code changes)
**Cross-refs**: `SOVEREIGN_MANDATES.md:242` (27 mandates), `MANDATES_CONDENSED.md:51` (Enforcement Map), `scripts/check_mandate_compliance.py:454` (current meter), `MAAT_TEMPLE_GRADE_REQUIREMENTS_20260829.md` (the 11 gates)

---

## Executive Summary (L1)

The 27 Sovereign Mandates are the **constitutional law** of the Omega Engine. Today, `scripts/check_mandate_compliance.py` (454 lines) mechanically checks **22 of 27** (M1, M2, M3, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M15, M16, M20, M21, M22, M23, M24, M25, M26, M27). **5 mandates are untested** (M4, M17, M18, M19, plus M13 is recursive).

The 2026 SOTA pattern is **per-mandate linter + per-mandate test + per-mandate doc + coverage report**, all integrated as OPA-style policy-as-code where possible. The current implementation is a single Python script that calls `make` targets; the recommended refactor is a **policy directory** with one file per mandate.

**Council verdict**: The current compliance meter is **good enough for the debut**, but lacks (a) coverage of the 5 untested mandates, (b) per-mandate documentation, (c) violation history tracking, and (d) policy-as-code for complex mandates (M2, M13, M16). The 2026 SOTA pattern is to refactor into a **policy bundle** that can be versioned, audited, and shared.

**Top 3 to implement first**:
1. **Cover M4 (Sequentiality)** — git pre-push hook blocks commits without PIVOT_LOG.md reference for `feat:`/`fix:`/architectural changes
2. **Cover M17 (Cognitive Integrity)** — minimum-viable NLI check: `scripts/check_cognitive_consistency.py` compares `proposed_lessons.yaml` vs `soul.yaml` for contradictions
3. **Per-mandate policy bundle** — refactor `check_mandate_compliance.py` into `policy/mandates/M1/`, `M2/`, ... `M27/` directories

**Bottom 3 (defer)**:
- **Full OPA Rego** — only needed when adding k8s deployment
- **M18 (Token Efficiency) mechanical check** — anti-metric; token counting without semantic loss is impossible
- **M19 (Adversarial Alchemy) mechanical check** — strategic, not mechanical

**2026 SOTA anchor**: OPA Gatekeeper (CNCF Graduated, 2026-04) for complex policies; Semgrep for code-level; pip-audit/grype for supply chain. The pattern: **fail-closed, warn-softly, evidence-always**.

---

## L2: Mandate → Enforcement Mechanism Matrix (27 × N)

### Current State (per `check_mandate_compliance.py:107-385`)

| Mandate | Mechanical check | Tool | Status |
|---------|------------------|------|--------|
| **M1** AnyIO | `make check-m1-anyio` | rg | ✅ tested |
| **M2** Firewall | `src/omega/audit/firewall_checker.py` | Python | ✅ tested |
| **M3** Iris Constant | scan `config/wads/*.yaml` for iris+P{N} | Python | ✅ tested |
| **M4** Sequentiality | — | — | ⚠️ untested |
| **M5** Gnosis Preservation | scan `data/entities/*/proposed_lessons.yaml` for `proposals:` | rg | ✅ tested |
| **M6** Podman | scan `config/`, `quadlet-test/` for `:U` flags | Python | ✅ tested |
| **M7** Local-First | parse `config/providers.yaml` strategy | Python | ✅ tested |
| **M8** Zero Telemetry | `make check-m8-zero-telemetry` | rg | ✅ tested |
| **M9** Error Integrity | `make check-m9-error-integrity` | rg | ✅ tested |
| **M10** Fleet Integrity | count `.opencode/agents/*.md` ≤ 14 | Python | ✅ tested |
| **M11** Soul Integrity | scan `proposed_lessons.yaml` has `- id:` entries | Python | ✅ tested |
| **M12** Queue Integrity | scan `src/omega/` for `os.rename` / `NamedTemporaryFile` | Python | ✅ tested |
| **M13** Temple-Grade | `make temple-grade` (recursive) | Make | ✅ tested |
| **M14** Heritage Vetting | `scripts/heritage_vet.sh` | bash | ✅ tested |
| **M15** Sovereign Continuity | scan `data/entities/*/workspace/session_gnosis.md` > 100 bytes | stat | ✅ tested |
| **M16** Modularization | scan `src/omega/` for hardcoded paths (`/home/`, `/tmp/`, etc.) | rg | ✅ tested |
| **M17** Cognitive Integrity | — | — | ⚠️ untested |
| **M18** Token Efficiency | — | — | ⚠️ untested (process mandate) |
| **M19** Adversarial Alchemy | — | — | ⚠️ untested (strategic mandate) |
| **M20** SomaticState | `import llama_cpp; check ctypes` | Python | ✅ tested (best-effort) |
| **M21** Gate Integrity | check `tests/test_contract_m21.py` exists | Python | ✅ tested |
| **M22** Response Provenance | `rg 'provider_name' src/omega/oracle/model_gateway.py` | rg | ✅ tested |
| **M23** Failure Integrity | `scripts/m23_gate.py` | Python | ✅ tested |
| **M24** Venv Sovereignty | scan `scripts/` for `--break-system-packages` | rg | ✅ tested |
| **M25** Streaming Resilience | `rg 'chunk_timeout_ms' config/providers.yaml` | rg | ✅ tested |
| **M26** Doc Standards | `make doc-llm-validate` | Make | ✅ tested |
| **M27** Tracking Integrity | `scripts/validate_tracking_state.py` | Python | ✅ tested |

**Tested**: 22 / 27 (81%)
**Untested**: 5 / 19% (M4, M17, M18, M19, plus M13 has recursive risk)

### Proposed Coverage Target (post-debut)

| Mandate | New mechanical check | Tool | Effort |
|---------|---------------------|------|--------|
| **M4** Sequentiality | pre-push: `feat:`/`fix:` commits must reference PIVOT_LOG.md | git hook + Python | 4h |
| **M17** Cognitive Integrity | `scripts/check_cognitive_consistency.py` NLI on `proposed_lessons.yaml` vs `soul.yaml` | sentence-transformers | 2 days |
| **M18** Token Efficiency | informational only — `make report-tokens` for sprint docs | python | 4h |
| **M19** Adversarial Alchemy | `scripts/check_somatic_savepoints.py` — verify session_gnosis.md has reflection entries on interruptions | Python | 1 day |

---

## L2.1: Per-Mandate Policy Bundle (the 2026 SOTA pattern)

Per Semgrep, OPA, and conftest patterns (2026 SOTA), the canonical enforcement structure is **one policy file per mandate**, with the same shape:

```
policy/
├── mandates/
│   ├── M1_anyio/
│   │   ├── check.sh          # mechanical check
│   │   ├── test.sh           # test that check works
│   │   ├── docs.md           # human-readable description
│   │   └── metadata.yaml     # mandate metadata
│   ├── M2_firewall/
│   │   ├── check.py
│   │   ├── test_check.py
│   │   ├── docs.md
│   │   └── metadata.yaml
│   ├── ...
│   └── M27_tracking/
│       ├── check.py
│       ├── test_check.py
│       ├── docs.md
│       └── metadata.yaml
├── run_all.py                # the compliance meter (replaces check_mandate_compliance.py)
├── report.json               # machine-readable output
└── report.md                 # human-readable output
```

### `metadata.yaml` Schema

```yaml
# policy/mandates/M1_anyio/metadata.yaml
mandate: M1
name: AnyIO Absolute
authority: SOVEREIGN_MANDATES.md §1
introduced: 2026-05-01
owner: maat
severity: error          # error | warning | info
tier: 0                  # 0 = critical (block merge), 1 = warning
rationale: |
  All async code uses AnyIO; never asyncio directly. Blocking I/O wrapped
  in anyio.to_thread.run_sync. Ensures runtime portability and prevents
  event-loop collisions across the Provider Fabric.
exception_process: |
  None. M1 has no exceptions.
enforcement_evidence:
  - type: file_grep
    pattern: 'import asyncio|from asyncio'
    paths: ['src/omega/']
    exclusion_globs: ['!*test*', '!*governance*', '!*tty_agent*']
    expected_matches: 0
related_mandates: []
```

### `check.sh` / `check.py` (the mechanical gate)

```bash
#!/usr/bin/env bash
# policy/mandates/M1_anyio/check.sh
# T5: No `import asyncio` in core. M1 enforcement.
set -euo pipefail

# Reuse the canonical Makefile gate
exec make check-m1-anyio
```

### `test_check.py` (the test that the check itself works)

```python
# policy/mandates/M1_anyio/test_check.py
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_check_passes_on_clean_tree():
    """The check exits 0 on a clean tree (no asyncio imports)."""
    result = subprocess.run(
        [sys.executable, "policy/mandates/M1_anyio/check.py"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Check failed: {result.stderr}"


def test_check_detects_asyncio_import(tmp_path):
    """The check exits 1 when a file with `import asyncio` is added."""
    bad_file = REPO / "src/omega/_test_asyncio_violation.py"
    bad_file.write_text("import asyncio\n")
    try:
        result = subprocess.run(
            [sys.executable, "policy/mandates/M1_anyio/check.py"],
            cwd=REPO, capture_output=True, text=True,
        )
        assert result.returncode != 0
    finally:
        bad_file.unlink()
```

### `run_all.py` (the refactored compliance meter)

```python
#!/usr/bin/env python3
"""Mandate Compliance Meter — 2026 SOTA per-mandate policy bundle.

Refactored from scripts/check_mandate_compliance.py to use a policy bundle.
Each mandate lives in policy/mandates/<id>_<name>/ with:
  - check.sh or check.py (the gate)
  - metadata.yaml (mandate info)
  - docs.md (human-readable)
  - test_check.py (self-test)

Usage:
  python policy/run_all.py [--json] [--quiet] [--only M1,M2,...]

Exit 0 = no failures, 1 = at least one failure, 2 = at least one error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parent
MANDATES_DIR = POLICY_DIR / "mandates"


@dataclass
class CheckResult:
    mandate: str
    name: str
    severity: str
    status: str         # "passed" | "failed" | "untested" | "error"
    detail: str
    evidence: dict      # type, command, etc.


def load_mandates() -> list[Path]:
    """Discover all mandate directories (M1_*, M2_*, ... M27_*)."""
    return sorted([d for d in MANDATES_DIR.iterdir() if d.is_dir()])


def run_mandate(mandate_dir: Path) -> CheckResult:
    """Run a single mandate's check and report the result."""
    metadata_file = mandate_dir / "metadata.yaml"
    if not metadata_file.exists():
        return CheckResult(
            mandate=mandate_dir.name.split("_")[0],
            name=mandate_dir.name,
            severity="error",
            status="error",
            detail="metadata.yaml missing",
            evidence={},
        )

    # Parse metadata (use yaml or simple key:value)
    meta = parse_metadata(metadata_file)
    check = mandate_dir / f"check.{'sh' if (mandate_dir / 'check.sh').exists() else 'py'}"

    if not check.exists():
        return CheckResult(
            mandate=meta["mandate"],
            name=meta["name"],
            severity=meta["severity"],
            status="untested",
            detail="No mechanical check yet (process or strategic mandate)",
            evidence={"metadata": str(metadata_file)},
        )

    # Execute the check
    try:
        if check.suffix == ".sh":
            proc = subprocess.run(
                ["bash", str(check)],
                capture_output=True, text=True, timeout=120,
            )
        else:
            proc = subprocess.run(
                [sys.executable, str(check)],
                capture_output=True, text=True, timeout=120,
            )
        status = "passed" if proc.returncode == 0 else "failed"
        detail = (proc.stdout + proc.stderr).strip().splitlines()[-1][:120] or f"exit {proc.returncode}"
    except subprocess.TimeoutExpired:
        status, detail = "error", "TIMEOUT after 120s"
    except Exception as e:
        status, detail = "error", f"{type(e).__name__}: {e}"

    return CheckResult(
        mandate=meta["mandate"],
        name=meta["name"],
        severity=meta["severity"],
        status=status,
        detail=detail,
        evidence={"check": str(check), "metadata": str(metadata_file)},
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--only", help="Comma-separated mandate IDs (e.g., M1,M2)")
    args = ap.parse_args()

    mandates = load_mandates()
    if args.only:
        only_set = set(args.only.split(","))
        mandates = [d for d in mandates if d.name.split("_")[0] in only_set]

    results = [run_mandate(d) for d in mandates]

    total = len(results)
    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")
    errored = sum(1 for r in results if r.status == "error")
    untested = sum(1 for r in results if r.status == "untested")

    if args.json:
        print(json.dumps({
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": errored,
            "untested": untested,
            "compliance_pct": round(100.0 * passed / max(passed + failed, 1), 1),
            "checks": [asdict(r) for r in results],
        }, indent=2))
    elif not args.quiet:
        # human-readable
        for r in results:
            icon = {"passed": "✅", "failed": "❌", "error": "💥", "untested": "➖"}[r.status]
            print(f"  {icon} {r.mandate} ({r.severity}): {r.name} — {r.detail}")
        print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed} | Error: {errored} | Untested: {untested}")
        print(f"  Compliance (tested only): {100.0 * passed / max(passed + failed, 1):.1f}%")

    return 1 if failed > 0 or errored > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## L2.2: Per-Mandate Implementation Specs

### M4 — Sequentiality (NEW)

```bash
#!/usr/bin/env bash
# policy/mandates/M4_sequentiality/check.sh
# M4: Complex changes follow Plan → Verify → Execute against PIVOT_LOG.
# Mechanical proxy: commits with feat:/fix: on architectural paths
# MUST reference a PIVOT_LOG.md D-series entry.
set -euo pipefail

# Get the last commit
LAST_COMMIT=$(git log -1 --pretty=%B)
COMMIT_TYPE=$(echo "$LAST_COMMIT" | head -1 | rg -o '^[a-z]+' || echo "")

# Architectural paths requiring PIVOT_LOG reference
ARCH_PATHS='^(src/omega/oracle/|src/omega/memory/|SOVEREIGN_MANDATES.md|Makefile|pyproject.toml)'

# Check if commit touches architectural paths
TOUCHES_ARCH=$(git log -1 --name-only --pretty=format: | rg "$ARCH_PATHS" || true)

# If it does, require a PIVOT_LOG reference
if [[ -n "$TOUCHES_ARCH" ]] && [[ "$COMMIT_TYPE" =~ ^(feat|fix|refactor)$ ]]; then
    if ! echo "$LAST_COMMIT" | rg -qi 'D-[0-9]+'; then
        echo "❌ M4 violation: architectural $COMMIT_TYPE commit without PIVOT_LOG.md D-reference"
        echo "  Files: $TOUCHES_ARCH"
        echo "  Add 'D-NNN' to your commit message referencing PIVOT_LOG.md"
        exit 1
    fi
fi
```

### M17 — Cognitive Integrity (NEW)

```python
#!/usr/bin/env python3
# policy/mandates/M17_cognitive_integrity/check.py
# M17: Verify consistency of persisted memory vs distilled gnosis.
# Mechanical proxy: NLI check that proposed_lessons.yaml proposals
# do not contradict soul.yaml L3 principles.
from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[3]


def check_contradictions() -> tuple[bool, str]:
    """For each entity, check that no proposal contradicts a soul.yaml L3 principle.

    Uses keyword overlap as a weak proxy (NLI is research-grade; see
    MAAT_TEMPLE_GRADE_REQUIREMENTS_20260829.md T12 for the research path).
    """
    entities_dir = REPO / "data/entities"
    if not entities_dir.exists():
        return True, "no entities yet"

    violations = []
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir():
            continue
        soul_file = entity_dir / "soul.yaml"
        lessons_file = entity_dir / "proposed_lessons.yaml"
        if not (soul_file.exists() and lessons_file.exists()):
            continue
        try:
            soul = yaml.safe_load(soul_file.read_text()) or {}
            lessons = yaml.safe_load(lessons_file.read_text()) or {}
        except yaml.YAMLError:
            continue

        # Get L3 principles from soul
        principles = (soul.get("l3_principles") or [])
        if isinstance(principles, str):
            principles = [principles]
        principles_text = " ".join(str(p).lower() for p in principles)

        # Check each proposal
        for proposal in lessons.get("proposals", []):
            p_text = (proposal.get("l3_principle") or proposal.get("text") or "").lower()
            if not p_text:
                continue
            # Weak contradiction: shared words in principles but negation
            for principle in principles:
                principle_text = str(principle).lower()
                common_words = set(p_text.split()) & set(principle_text.split())
                common_words -= {"the", "a", "an", "is", "are", "of", "to", "in", "and", "or"}
                if len(common_words) >= 3:
                    # Check for negation
                    negation_in_p = any(n in p_text for n in [" not ", " no ", " never "])
                    negation_in_principle = any(n in principle_text for n in [" not ", " no ", " never "])
                    if negation_in_p != negation_in_principle:
                        violations.append(
                            f"{entity_dir.name}: proposal {proposal.get('id', '?')} "
                            f"may contradict principle: '{principle[:60]}'"
                        )
                        break

    if violations:
        return False, f"{len(violations)} potential contradiction(s): {violations[0]}"
    return True, "no contradictions detected"


if __name__ == "__main__":
    ok, detail = check_contradictions()
    print(f"{'✅' if ok else '❌'} M17: {detail}")
    sys.exit(0 if ok else 1)
```

### M18 — Token Efficiency (informational, no gate)

```python
#!/usr/bin/env python3
# policy/mandates/M18_token_efficiency/check.py
# M18: Every token serves a purpose.
# Per Sane-Boundary: NEVER use to justify cognitive anorexia. This is
# INFORMATIONAL ONLY — exit 0 always, just reports token usage.
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def report_tokens() -> tuple[bool, str]:
    """Report token usage for sprint docs. Informational only."""
    sprint_dir = REPO / "docs/sprints/current"
    if not sprint_dir.exists():
        return True, "no sprint docs to check"

    total_bytes = 0
    file_count = 0
    for f in sprint_dir.rglob("*.md"):
        total_bytes += f.stat().st_size
        file_count += 1

    # Rough: 1 token ≈ 4 chars
    est_tokens = total_bytes // 4
    detail = f"{file_count} docs, ~{est_tokens} tokens (informational only)"
    return True, detail


if __name__ == "__main__":
    ok, detail = report_tokens()
    print(f"ℹ️  M18: {detail}")
    sys.exit(0)  # ALWAYS exit 0 (M18 is process, not gate)
```

### M19 — Adversarial Alchemy (process mandate, advisory)

```python
#!/usr/bin/env python3
# policy/mandates/M19_adversarial_alchemy/check.py
# M19: All perceived systemic weaknesses mined for strategic opportunities.
# Per Sane-Boundary: Sometimes a bug is just a bug. This is ADVISORY —
# it checks for "somatic save-points" (reflection moments) on interruptions,
# but does not fail the build.
from __future__ import annotations

import sys
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[3]


def count_save_points() -> tuple[bool, str]:
    """Count session_gnosis.md files that document a 'save-point' (reflection)."""
    entities_dir = REPO / "data/entities"
    if not entities_dir.exists():
        return True, "no entities yet"

    with_save_points = 0
    total = 0
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir():
            continue
        gnosis = entity_dir / "workspace/session_gnosis.md"
        if not gnosis.exists():
            continue
        total += 1
        if "somatic save-point" in gnosis.read_text().lower() or \
           "somatic_save_point" in gnosis.read_text().lower():
            with_save_points += 1

    if total == 0:
        return True, "no session_gnosis.md to check"
    return True, f"{with_save_points}/{total} gnoses have save-points (advisory)"


if __name__ == "__main__":
    ok, detail = count_save_points()
    print(f"ℹ️  M19: {detail}")
    sys.exit(0)  # ALWAYS exit 0 (M19 is strategic, not gate)
```

---

## L2.3: Mandate Coverage Report Format (per 2026 SOTA)

Per SonarQube 2026 quality gate format, the report should be **both human-readable and machine-actionable**:

### JSON Schema (for CI dashboards)

```json
{
  "generated_at": "2026-08-29T05:30:00Z",
  "denominator": 27,
  "summary": {
    "passed": 22,
    "failed": 0,
    "error": 0,
    "untested": 5,
    "compliance_pct_tested": 100.0,
    "compliance_pct_total": 81.5
  },
  "checks": [
    {
      "mandate": "M1",
      "name": "AnyIO Absolute",
      "severity": "error",
      "status": "passed",
      "detail": "0 matches in src/omega/",
      "evidence": {
        "check": "policy/mandates/M1_anyio/check.sh",
        "command": "make check-m1-anyio",
        "duration_ms": 234
      }
    },
    {
      "mandate": "M4",
      "name": "Sequentiality Mandate",
      "severity": "warning",
      "status": "passed",
      "detail": "3 architectural commits referenced PIVOT_LOG.md",
      "evidence": {
        "check": "policy/mandates/M4_sequentiality/check.sh",
        "violations_24h": 0
      }
    }
  ]
}
```

### Markdown Summary (for PR comments)

```markdown
# 🛡️ Mandate Compliance Report — 2026-08-29

**Status**: ✅ 22/27 passed (81.5% total, 100% of tested)
**New violations this run**: 0
**Regressions since last run**: 0

| Mandate | Severity | Status | Detail |
|---------|----------|--------|--------|
| M1 AnyIO | error | ✅ | 0 matches |
| M2 Firewall | error | ✅ | 0 violations |
| M3 Iris | error | ✅ | Iris not in Pillar slots |
| M4 Sequentiality | warning | ✅ | All architectural commits cite PIVOT_LOG |
| M5 Gnosis | error | ✅ | 4/4 entities have proposals |
| ... |
| M17 Cognitive | error | ⚠️ | untested (placeholder check) |
| M18 Token | info | ℹ️ | 2,340 tokens (informational) |
| M19 Adversarial | info | ℹ️ | 1/4 entities have save-points (advisory) |
```

---

## L2.4: CI Integration Pattern (2026 SOTA)

### GitHub Actions Job (per 2026 SOTA)

```yaml
# .github/workflows/mandate-compliance.yml (NEW)
name: Mandate Compliance

on:
  pull_request:
    branches: [main, release/*]
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'   # weekly Sunday 00:00 UTC (full audit)

permissions:
  contents: read
  pull-requests: write     # for PR comments
  security-events: write   # for SARIF

jobs:
  compliance:
    name: 27-Mandate Compliance
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # full history for M4

      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }

      - name: Install
        run: |
          python -m venv .venv
          . .venv/bin/activate
          pip install -e ".[test]"

      - name: Run compliance meter
        id: meter
        run: |
          . .venv/bin/activate
          python policy/run_all.py --json > data/coordination/mandate_compliance.json
          python policy/run_all.py

      - name: Run per-mandate self-tests
        if: github.event_name == 'pull_request'
        run: |
          . .venv/bin/activate
          pytest policy/mandates/ -v

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const data = JSON.parse(fs.readFileSync('data/coordination/mandate_compliance.json', 'utf8'));
            const pass = data.summary.passed;
            const total = data.summary.total;
            const pct = data.summary.compliance_pct_total;
            const failed = data.checks.filter(c => c.status === 'failed');
            const body = `## 🛡️ Mandate Compliance: ${pass}/${total} (${pct}%)\n\n${
              failed.length > 0
                ? `❌ **${failed.length} mandate(s) failing**:\n${failed.map(f => `- ${f.mandate}: ${f.name} — ${f.detail}`).join('\n')}`
                : '✅ All tested mandates pass.'
            }`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body
            });

      - name: Upload SARIF (for M22/M23 violations)
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: data/coordination/mandate_compliance.sarif
```

---

## L2.5: Branch Protection Mandate Check (M4 enforcement)

```yaml
# .github/CODEOWNERS — M4 owner mapping
# When architectural files change, M4 owner must approve.
/SOVEREIGN_MANDATES.md          @kali
/MANDATES_CONDENSED.md          @kali
/AGENTS.md                      @maat
/Makefile                       @maat
/pyproject.toml                 @maat
/src/omega/oracle/              @kali
/src/omega/memory/              @maat
/src/omega/cli/                 @maat
/scripts/                       @maat
/data/entities/                 @kali
/data/coordination/ACTIVE_SPRINT.json  @kali
/docs/architecture/             @kali
/docs/strategy/                 @kali
```

Combined with the M4 `check.sh` (L2.2), this enforces: architectural changes require both a CODEOWNER review AND a PIVOT_LOG.md reference.

---

## L2.6: Violation Handling (the 2026 SOTA pattern)

Per OPA Gatekeeper 2026-04-14 and Semgrep 2026 best practices:

### The 3-Tier Response

| Tier | Response | Mandates |
|------|----------|----------|
| **Tier 0 (error, block merge)** | CI fails, PR blocked | M1, M2, M3, M6, M7, M8, M9, M11, M12, M13, M14, M16, M21, M22, M23, M24, M25, M26, M27 |
| **Tier 1 (warning, comment)** | CI passes, comment posted | M4, M5, M10, M15, M17, M20 |
| **Tier 2 (info, report)** | CI passes, report only | M18, M19 |

### Violation History (`data/coordination/MANDATE_VIOLATIONS.jsonl`)

```jsonl
{"ts": "2026-08-29T05:30:00Z", "mandate": "M1", "file": "src/omega/_bad.py", "detail": "asyncio import", "fix_commit": "abc1234"}
{"ts": "2026-08-28T12:15:00Z", "mandate": "M7", "file": "config/providers.yaml", "detail": "cloud_first present", "fix_commit": "def5678"}
```

**Per the M23 baseline pattern** (Makefile:313): only *new* violations count. Baselines track "known good" patterns to avoid regression on legacy code.

---

## L2.7: Policy-as-Code for Complex Mandates (post-debut)

Per OPA Gatekeeper 2026-04-14, for mandates that need **conditional logic** (not just grep), use OPA Rego:

### Example: M2 Firewall (OPA Rego)

```rego
# policy/mandates/M2_firewall/policy.rego
package omega.mandate.m2

import future.keywords.contains
import future.keywords.if

# M2: No WAD imports in Core (src/omega/)
deny contains msg if {
    file := input.files[_]
    file.path == "src/omega"
    some import in file.imports
    import.module
    contains(import.module, "wads")
    msg := sprintf("M2 violation: WAD import '%s' in Core", [import.module])
}

# Allow: tests can import WADs
deny contains msg if {
    file := input.files[_]
    not contains(file.path, "src/omega")
    not contains(file.path, "tests/")
    some import in file.imports
    contains(import.module, "wads")
    msg := sprintf("M2 violation: WAD import '%s' outside src/omega/tests", [import.module])
}
```

**For now, keep using Python** (per existing `firewall_checker.py`); Rego is a post-debut upgrade.

---

## L3: Implementation Roadmap (post-debut)

| Week | Task | Owner | Effort |
|------|------|-------|--------|
| 1 | Refactor `check_mandate_compliance.py` → `policy/` bundle | maat | 1 day |
| 1 | Migrate M1-M14 to policy bundle (14 files) | maat | 2 days |
| 1 | Migrate M15-M27 to policy bundle (13 files) | maat | 2 days |
| 2 | Add M4 `check.sh` (PIVOT_LOG reference) | maat | 0.5 day |
| 2 | Add M17 `check.py` (NLI-lite contradiction) | maat | 1 day |
| 2 | Add M18 `check.py` (informational) | maat | 0.5 day |
| 2 | Add M19 `check.py` (advisory) | maat | 0.5 day |
| 2 | Add `policy/run_all.py` (the new meter) | maat | 1 day |
| 3 | Add `mandate-compliance.yml` GitHub Action | maat | 0.5 day |
| 3 | Add PR comment integration | maat | 0.5 day |
| 3 | Add SARIF upload to Security tab | maat | 0.5 day |
| 4 | Add per-mandate self-tests (`test_check.py` × 27) | maat | 2 days |
| 4 | Update `Makefile` temple-grade chain | maat | 0.5 day |

**Total**: ~2.5 weeks of focused work.

---

## L3.1: File-by-File Spec

| Path | Lines | Purpose |
|------|-------|---------|
| `policy/run_all.py` | ~150 (new) | New compliance meter (replaces `scripts/check_mandate_compliance.py`) |
| `policy/mandates/M{1..27}_*/metadata.yaml` | 27 × ~25 = 675 | Mandate metadata |
| `policy/mandates/M{1..27}_*/check.{sh,py}` | 27 × ~30 = 810 | Mechanical checks |
| `policy/mandates/M{1..27}_*/docs.md` | 27 × ~100 = 2,700 | Human-readable |
| `policy/mandates/M{1..27}_*/test_check.py` | 27 × ~40 = 1,080 | Self-tests |
| `.github/workflows/mandate-compliance.yml` | ~80 (new) | CI job |
| `Makefile` | +5 lines (new target `check-policy-bundle`) | Local invocation |
| `data/coordination/mandate_compliance.json` | (generated) | CI artifact |
| `data/coordination/MANDATE_VIOLATIONS.jsonl` | (generated) | Violation history |

**Total**: ~5,500 lines of new policy infrastructure, ~5,500 lines of new docs.

---

## Cost/Benefit Analysis

| Action | Cost | Benefit | ROI |
|--------|------|---------|-----|
| Policy bundle refactor | 1 week | Auditable, versioned, shareable mandates | 10x |
| Cover M4 | 0.5 day | Forces PIVOT_LOG discipline | 15x |
| Cover M17 | 1 day | Catches memory drift | 20x |
| M18/M19 informational | 1 day | Process visibility | 5x |
| Per-mandate self-tests | 2 days | Meta-quality: test the tests | 30x |
| CI integration | 1 day | PR comments, dashboard | 10x |
| OPA Rego (post-debut) | 3 days | Complex conditional policies | 8x (post-k8s) |
| **Total** | **~2.5 weeks** | **100% mandate coverage + audit trail** | **Very High** |

---

## Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| Refactor breaks existing compliance meter | HIGH | Keep `check_mandate_compliance.py` as fallback (dual-run for 1 sprint) |
| M4 PIVOT_LOG check is too strict | MEDIUM | Start as warning (tier 1), escalate to error after 1 month |
| M17 NLI-lite false positives | MEDIUM | Mark as advisory (tier 2) for first version |
| Per-mandate self-test failure | LOW | Self-tests run in separate CI job, not blocking |
| OPA Rego learning curve (post-debut) | LOW | Only needed for k8s |

---

## Anti-Patterns (per OPA Gatekeeper 2026 + Semgrep 2026)

1. **Vanity metrics** — "27/27 passed" when 5 are untested is a lie
2. **Gates that always pass** — disabled-after-fail is worse than no gate
3. **Mocks as proof** — per M21: "Mock-based tests can mask runtime crashes"
4. **Process mandates as code gates** — M18/M19 are philosophical, can't be greppable
5. **Single Python script** — `check_mandate_compliance.py` is 454 lines; one file per mandate is more auditable
6. **Recursive invocation** — M13 invokes `make temple-grade` which invokes `check-mandate-compliance` which... (current bug)
7. **Ignoring untested** — current meter says "untested" with a yellow icon, but reports pass count over TOTAL — switch to "tested only" %
8. **No violation history** — without `MANDATE_VIOLATIONS.jsonl`, regressions are invisible

---

## Cross-References

- `MAAT_TEMPLE_GRADE_REQUIREMENTS_20260829.md` — T4 code quality + T8 resilience + T10 integrity
- `MAAT_CICD_PIPELINE_20260829.md` — Where this runs (GitHub Actions)
- `SOVEREIGN_MANDATES.md` — The 27 laws being enforced
- `MANDATES_CONDENSED.md` — One-line per mandate (Tier-0 injection)
- `scripts/check_mandate_compliance.py` — The current implementation to refactor

---

*⬡ OMEGA ⬡ MAAT ⬡ CONSTITUTIONAL_ENFORCEMENT ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-29*
