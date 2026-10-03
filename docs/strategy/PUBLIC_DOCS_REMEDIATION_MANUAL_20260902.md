<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PUBLIC DOCS REMEDIATION MANUAL — W37 Debut

**AP Token**: `AP-PUBLIC-DOCS-REMEDIATION-20260902-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode ⬡ trc_remediation ⬡ ACTIVE

**Date**: 2026-09-02
**Sprint**: PUBLIC-DEBUT-01, DEL-1_EXECUTION
**Version**: 1.0.0
**Source Dialectic**: 10-agent review (Carmack, Doom Guy, Grokster, Jem, Lilith, Ma'at, Researcher, Roc, Verity, Kali)

---

## §0 — EXECUTIVE SUMMARY

### §0.1 The Verdict

The public-facing documentation for the Omega Engine is **fundamentally broken**. Not broken in the sense of typos or minor inconsistencies, but broken in the sense that **the docs describe a different product than what exists on disk**.

**The dialectic between 10 agents (Carmack, Doom Guy, Grokster, Jem, Lilith, Ma'at, Researcher, Roc, Verity, Kali) produced unanimous consensus:**

- **11 false claims in README alone** — model name, agent count, entity count, mandate compliance, temple-grade status, test suite, CLI readiness, provider count, heritage tags
- **50% of "Production-ready" claims are false or untested**
- **Theater Detection Score: 35-67/100** (0 = fully honest, 100 = pure theater)
- **The documentation pipeline documents two different systems**: the v1.5.0 system (frozen in QUICKSTART/USER_MANUAL) and the v1.6.0 reality (described in README honesty table and CHANGELOG)

### §0.2 Root Causes

| Root Cause | Impact | Evidence |
|------------|--------|----------|
| **Aspirational state as current reality** | Docs describe target state, not current state | "All 22 enforced" when meter reads 64.3% |
| **Compliance theater** | Meter treated as badge, not diagnostic | "T1-T11 ✅" when 6 checks fail |
| **Stale metrics frozen at v1.5.0** | Test count, mandate count, provider count all frozen | "1315 tests" when 0 tests run |
| **Fictional Makefile targets** | Docs reference `make talk`, `make summon`, etc. that don't exist | 90% of USER_MANUAL menu is fake |
| **Install pathway divergence** | QUICKSTART says `make setup` + Ollama, install.sh uses native-gguf + HF | Two different paths, neither complete |
| **Secret committed to history** | Real OAuth secret in incident doc, un-allowlisted | `GOCSPX-***REDACTED-ROTATED***` in `OAuth-failure-incident-session-ses_fe8c.md:57` |
| **Dead code claimed stripped** | 3 files claimed removed but still on disk | `cohort_registry.py`, `m33_probe.py`, `m36_recursive_probe.py` |
| **Missing standard docs** | FAQ.md, ROADMAP.md, SUPPORT.md, FUNDING.yml, llms.txt all missing | GitHub requirements not met |

### §0.3 The 30 Remediation Decisions

The dialectic produced **30 PIVOT_LOG decisions** (D-PUBLIC-001 through D-PUBLIC-030):

- **11 P0** (launch blockers) — ~14h effort
- **16 P1** (hardening) — ~22h effort
- **3 P2** (post-debut polish) — ~2h effort
- **Total: ~38h**

### §0.4 Timeline

| Phase | Dates | Scope |
|-------|-------|-------|
| **Phase 1: P0 Blocker Removal** | 2026-09-02 to 2026-09-05 | 11 P0 decisions, ~14h |
| **Phase 2: P1 Hardening** | 2026-09-06 to 2026-09-08 (W37 launch) | 16 P1 decisions, ~22h |
| **Phase 3: P2 Polish** | Post-debut (W38+) | 3 P2 decisions, ~2h |

---

## §1 — P0 LAUNCH BLOCKERS (Must Complete Before W37 Debut)

### §1.1 D-PUBLIC-027: Filter-repo OAuth Secret + Rotate

**Priority**: P0 (LAUNCH BLOCKER)
**Effort**: 2h
**Owner**: Roc
**Mandates**: M23, M8

**Problem**: A real OAuth secret (`GOCSPX-***REDACTED-ROTATED***`) is committed to git history in `OAuth-failure-incident-session-ses_fe8c.md:57` and is NOT in the secrets allowlist.

**Evidence**:
- File: `data/coordination/OAuth-failure-incident-session-ses_fe8c.md:57`
- Secret: `GOCSPX-***REDACTED-ROTATED***`
- Status: COMMITTED, un-allowlisted
- Allowlist: `data/secrets-public.toml:66` contains different secret (`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`)

**Steps**:

1. **Rotate the OAuth secret** in Google Cloud Console
2. **Add to allowlist** in `data/secrets-public.toml`:
   ```toml
   # Add after line 66
   "GOCSPX-***REDACTED-ROTATED***" = "redacted-incident-ses_fe8c"
   ```
3. **Run git-filter-repo** to remove from history:
   ```bash
   git filter-repo --replace-text <(echo "GOCSPX-***REDACTED-ROTATED***==>REDACTED-INCIDENT-SES_FE8C")
   ```
4. **Verify** with `scripts/check_secrets.py` — must exit 0
5. **Force-push** to debut branch
6. **Notify all clones** to re-clone

**Verification**:
- `make check-m23-failure-integrity` passes
- `scripts/check_secrets.py` exits 0
- `git log -p --all | grep -c "GOCSPX-4uHgMPm"` returns 0

---

### §1.2 D-PUBLIC-014: Restore `omega.library` from Git

**Priority**: P0 (LAUNCH BLOCKER)
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M23, M11

**Problem**: The `omega.library` module was removed in D-565 cleanup (Carmack dialectic Order 1). 12 files in `src/` still import it, causing:
- `make test` to fail (0 tests collected)
- `make check-hub-health` to fail
- `omega talk`, `omega summon` to fail
- `mcp_servers/omega_hub/` to fail

**Evidence**:
- `src/omega/oracle/sovereign_search_service.py:39` — `from omega.library.indexer import Indexer`
- `src/omega/oracle/local_worker_pool.py:267` — `from omega.library.coordinator import COORDINATOR`
- `src/omega/cli/oracle_cli.py:747,762,784` — `from omega.library.catalog import LibraryCatalog`
- `mcp_servers/omega_hub/hub_tools/tools.py:41` — `from omega.library.research import RESEARCH_DEPTHS`

**Steps**:

1. **Restore from git** (last commit before removal):
   ```bash
   git checkout 69ece770^ -- src/omega/library/
   ```
2. **Restart hub service**:
   ```bash
   make mcp-restart
   ```
3. **Verify imports**:
   ```bash
   python3 -c "from omega.library.indexer import Indexer; print('OK')"
   python3 -c "from omega.library.coordinator import COORDINATOR; print('OK')"
   python3 -c "from omega.library.catalog import LibraryCatalog; print('OK')"
   python3 -c "from omega.library.research import RESEARCH_DEPTHS; print('OK')"
   ```
4. **Run tests**:
   ```bash
   make test 2>&1 | tee /tmp/test_output.log
   ```
5. **Check test count** — should show actual count (not 1315, not 0)
6. **Update test count** in docs once known

**Verification**:
- `make test` runs actual tests (count TBD)
- `make check-hub-health` passes
- `python3 -m omega.cli.oracle_cli talk "hello"` works
- `python3 -m omega.cli.oracle_cli summon Kali "status"` works

---

### §1.3 D-PUBLIC-001: Fix All 11 False Claims in README

**Priority**: P0
**Effort**: 2h
**Owner**: Lilith
**Mandates**: M23, M27

**Problem**: README contains 11 false claims that fail every adversarial test.

**The 11 Lies and Their Fixes**:

| # | Current Claim | Reality | Fix |
|---|---------------|---------|-----|
| 1 | "Qwen 1.7B GGUF" (line 22, 93) | **LFM2.5-2.6B Q4_K_M** OR **Qwen3-1.7B-Q6_K** (per download_model.sh) | Change to "Qwen3-1.7B-Q6_K.gguf" (script is source of truth) |
| 2 | "10 entity pillars" (line 158) | **10 Slot Keepers at S1-S10** (not "pillars") | Change "pillars" to "Slot Keepers" |
| 3 | "12 tech role entities" (line 158) | **24 entities** in `_omega_default` (or 10 per Lilith's audit) | Change to "14 canonical agents, 10 entities in `_omega_default` IWAD, 29 in `arcana_novai`" |
| 4 | "All 22 enforced" (line 209) | **64.3% (18/28)** per mandate meter | Change to "64.3% (18/28 mandates passing, 5 failing, 4 untested)" |
| 5 | "Temple-Grade T1-T11 ✅" (line 289) | **6 checks, FAILS** on M23 cascade | Change to "6-gate cascade; currently fails on M23" |
| 6 | "8-backend fallback" (line 192) | **10 active providers** (ollama disabled) | Change to "10 active providers in fallback chain" |
| 7 | "113 heritage tags" (line 214) | **216 total references, ~60 unique** | Change to "216 total `[id-soft:]` references across 63 files, ~60 unique vet records" |
| 8 | "Test suite passing" (line 286) | **BROKEN** — 0 tests collected | Change to "Test suite currently broken — omega.library restoration in progress" |
| 9 | "CLI ready" (line 26) | **NOT BUILT** — use `python -m omega.cli.oracle_cli` | Change to "CLI binary not built; use `python3 -m omega.cli.oracle_cli <command>`" |
| 10 | "11 agents" (line 210) | **13 agents** in `.opencode/agents/` (or 14 with scribe) | Change to "14 canonical agents in `.opencode/agents/`" |
| 11 | "Personal IWAD pillars" (line 228) | **13 Spheres** in `arcana_novai/spheres.yaml` | Change to "13 Spheres in `arcana_novai` IWAD" |

**Steps**:

1. Read README.md (365 lines)
2. Find each of the 11 claims
3. Replace with corrected version
4. Add inline citations: `<!-- Verified: <file:line> -->`
5. Run `make check-docs-truth` to verify no new false claims introduced

**Verification**:
- `make check-docs-truth` passes
- No claim contradicts `config/providers.yaml`, `config/wads/`, or `scripts/check_mandate_compliance.py`
- All counts match `ls`, `wc -l`, or `python3 -c` outputs

---

### §1.4 D-PUBLIC-002: Add Honest Maturity Banner to All User-Facing Docs

**Priority**: P0
**Effort**: 1h
**Owner**: Lilith
**Mandates**: M23

**Problem**: Only README.md has an alpha disclaimer (lines 16-33). QUICKSTART.md, USER_MANUAL.md, and CONTRIBUTING.md **actively mislead** by presenting alpha as stable.

**Evidence**:
- QUICKSTART.md: No alpha warning, claims "5 minutes"
- USER_MANUAL.md: "Version 1.2.0 | 1315 Tests Passing | 23 Sovereign Mandates" (line 12) — ALL FALSE
- CONTRIBUTING.md: "make test — all 791 tests pass" (line 104) — FALSE

**Standard Alpha Banner** (add at TOP of each doc):

```markdown
> ⚠️ **ALPHA SOFTWARE — NOT PRODUCTION READY**
>
> - **Test suite**: Currently broken (omega.library restoration in progress)
> - **Mandate compliance**: 64.3% (18/28 passing, 5 failing, 4 untested)
> - **Temple-Grade**: Fails on M23 cascade
> - **CLI binary**: Not built; use `python3 -m omega.cli.oracle_cli <command>`
> - **Known issues**: See [CHANGELOG.md](CHANGELOG.md) and [RELEASING.md](docs/RELEASING.md)
>
> Use for development, testing, and contribution. Do not deploy to production.
```

**Steps**:

1. Add banner to QUICKSTART.md (after line 1, before "Prerequisites")
2. Add banner to USER_MANUAL.md (after line 1, before "# User Manual")
3. Add banner to CONTRIBUTING.md (after line 1, before "# Contributing")
4. Verify all 4 docs (README + 3 above) have the same banner

**Verification**:
- All 4 docs contain identical banner text
- Banner appears before any "Quick Start" or "Install" instructions
- No doc presents a "working system" facade

---

### §1.5 D-PUBLIC-003: Update Mandate Compliance Claims Everywhere

**Priority**: P0
**Effort**: 1h
**Owner**: Verity
**Mandates**: M23, M27

**Problem**: Docs claim 100% mandate compliance; meter reads 64.3% (18/28).

**Current False Claims**:
- README:209: "All 22 enforced"
- README:290: "All 27 Sovereign Mandates verified compliant"
- README:289: "Temple-Grade (T1-T11) ✅ VERIFIED"

**Mandate Meter Reality** (per `scripts/check_mandate_compliance.py`):
```
Total: 28 | Passed: 18 | Failed: 5 | Untested: 4 | Compliance: 64.3%
```

**Failing Mandates**:
- M13 Temple-Grade (cascading from M23)
- M16 Modularization (hardcoded path in `m34_registry.py:75`)
- M23 Failure Integrity (`check_secrets.py` exits 1)
- M27 Tracking Integrity (stale `in_progress` task)

**Untested Mandates** (require manual verification):
- M2 Engine-Stack Firewall
- M6 UID Sovereignty (Podman-specific)
- M20 Somatic State
- M28 Spatial (R-tree + vec0)

**Steps**:

1. Find all "all enforced" / "all 27" / "T1-T11" claims
2. Replace with honest status:
   ```markdown
   **Mandate Compliance**: 64.3% (18/28 passing, 5 failing, 4 untested)
   
   - ✅ M1, M7, M8, M9, M10, M15, M22, M24, M25, M26, M28 (11 passing)
   - ⚠️ M11 (partial), M14 (partial) (2 partial)
   - ❌ M13, M16, M23, M27 (4 failing)
   - 🔍 M2, M6, M20, M28 (4 untested — manual verification required)
   ```
3. Add link to `scripts/check_mandate_compliance.py` output

**Verification**:
- `python3 scripts/check_mandate_compliance.py` output matches docs
- No "all enforced" or "100% compliant" claims remain
- Failing mandate list is current

---


### §1.6 D-PUBLIC-004: Fix Temple-Grade Claim

**Priority**: P0
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M13, M23

**Problem**: README claims "Temple-Grade T1-T11 ✅ VERIFIED" but `make temple-grade` runs 6 checks and FAILS on M23 cascade.

**Current False Claim**:
- README:289: "Temple-Grade (T1-T11) ✅ VERIFIED"

**Reality**:
- `make temple-grade` runs 6 top-level dependencies: `check-codex-stale`, `doc-llm-validate`, `check-mandates`, `check-mandate-compliance`, `check-tracking-state`, `dashboard-self-test`
- Fails on M23 cascade (vision_backend.py has 2 new soft-failure patterns)

**Fix**:
```markdown
**Temple-Grade**: 6-gate cascade (Codex, LLM docs, Mandates, Compliance, Tracking, Dashboard)
- **Status**: ❌ Currently FAILS on M23 cascade
- **Root cause**: `src/omega/experiments/vision_backend.py` has 2 soft-failure patterns
- **Fix queued**: M23 remediation (see §2.3)
```

**Verification**:
- `make temple-grade` output matches docs
- No "T1-T11" claims remain
- Root cause documented

---

### §1.7 D-PUBLIC-005: Fix Test Suite Claims

**Priority**: P0
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M23

**Problem**: Multiple docs claim "1315 tests passing" but `make test` collects 0 tests due to missing `omega.library`.

**Current False Claims**:
- README:27, 286, 333: "1315 tests passing"
- USER_MANUAL:12, 89, 129, 871, 1052: "1315 tests passing"
- QUICKSTART:36, 60: "1315/1315 passing"
- CHANGELOG:38, 93: "1315 tests passing (was 1162)"
- CONTRIBUTING:104, 154, 163: "791 tests pass"

**Fix** (after D-PUBLIC-014 restores omega.library):
```markdown
**Test Suite**: [ACTUAL COUNT] tests collected (after omega.library restoration)
- **Status**: ⚠️ Restoration in progress (D-PUBLIC-014)
- **Root cause**: 12 files import removed `omega.library` module (D-565)
- **Fix**: `git checkout 69ece770^ -- src/omega/library/`
```

**Steps**:
1. Restore omega.library (D-PUBLIC-014)
2. Run `make test` to get actual count
3. Update all 5 docs with actual count
4. Add note: "Test count reflects current collection; see CHANGELOG for history"

**Verification**:
- `make test` output matches docs
- No "1315" or "791" stale claims remain
- Docs state actual collected count

---

### §1.8 D-PUBLIC-006: Fix Entity/Agent Counts

**Priority**: P0
**Effort**: 1h
**Owner**: Lilith
**Mandates**: M10, M27

**Problem**: Entity/agent counts are inconsistent across docs.

**Current Claims vs Reality**:
| Doc | Claim | Reality |
|-----|-------|---------|
| README:123 | "13 canonical agents" | **14** in `.opencode/agents/` |
| README:123 | "24 default entities in `_omega_default`" | **10** entities + Iris = 11 |
| README:158 | "12 tech role entities" | **10** entities in `_omega_default` |
| README:210 | "11 agents (10 Pillar + 1 Oversoul)" | **14** agents |
| README:291 | "14 agents (canonical)" | **14** agents (correct) |
| USER_MANUAL:264-279 | "10 Pillar Keepers" | ✅ Correct (matches `arcana_novai`) |
| USER_MANUAL:280-288 | "Oversouls & Messengers" | ✅ Correct |

**Fix**:
```markdown
**Agent Fleet**: 14 canonical agents in `.opencode/agents/`
- 10 Slot Keepers (S1-S10) in `_omega_default` IWAD
- 29 entities in `arcana_novai` IWAD
- 4 Oversouls (Kali, Ma'at, Lilith, Sophia)
- 2 archive agents (grok_cli, scribe_agent_20260730)
```

**Verification**:
- `ls .opencode/agents/*.md | wc -l` matches docs
- `grep -c "name:" config/wads/_omega_default/entities.yaml` matches docs
- `grep -c "name:" config/wads/arcana_novai/entities.yaml` matches docs

---

### §1.9 D-PUBLIC-007: Fix Provider Count

**Priority**: P0
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M7, M27

**Problem**: Docs claim "8-backend fallback" but config has 10 active providers.

**Current Claims vs Reality**:
| Doc | Claim | Reality |
|-----|-------|---------|
| README:192 | "8-backend fallback chain" | **10 active** (native-gguf, lmster, ollama, google, openrouter, opencode-zen, antigravity, cline, anthropic, xai, mock, google-compat) |
| QUICKSTART:61 | "9 Providers" | **10 active** |
| USER_MANUAL:447-457 | "9 providers listed" | **10 active** |

**Fix**:
```markdown
**Provider Fabric**: 10 active providers in fallback chain (local-first)
1. Native GGUF (priority 0, local)
2. LM Studio (priority 1, local)
3. Ollama (priority 2, local, disabled by default)
4. Mock (test-only)
5. Google AI Studio (cloud fallback)
6. OpenRouter (cloud fallback)
7. OpenCode Zen (cloud fallback)
8. Antigravity (cloud fallback)
9. Cline (cloud fallback)
10. Anthropic (cloud fallback)
11. xAI (cloud fallback)
12. Google Compat (cloud fallback)
```

**Verification**:
- `grep -c "name:" config/providers.yaml` matches docs
- `grep -c "enabled: true" config/providers.yaml` matches docs

---

### §1.10 D-PUBLIC-008: Fix Model Default

**Priority**: P0
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M7, M27

**Problem**: README claims "Qwen 1.7B GGUF" but `download_model.sh` downloads Qwen3-1.7B-Q6_K.gguf, and `config/providers.yaml` references LFM2.5-2.6B.

**Current Claims vs Reality**:
| Doc | Claim | Reality |
|-----|-------|---------|
| README:45-47 | "LFM2.5-2.6B Q4_K_M, ~1.67GB" | `download_model.sh` downloads **Qwen3-1.7B-Q6_K.gguf** |
| README:22, 93 | "Qwen 1.7B GGUF" | `config/providers.yaml:150-155` references **LFM2.5-2.6B** |
| USER_MANUAL:85-86 | `ollama pull qwen2.5:0.5b` / `ollama pull qwen3:1.7b` | Different models entirely |

**Fix**:
```markdown
**Default Model**: Qwen3-1.7B-Q6_K.gguf (~1.6GB)
- Downloaded by `scripts/download_model.sh` from `Qwen/Qwen3-1.7B-GGUF`
- Local-first, CPU-only (no GPU required)
- Alternative: LFM2.5-2.6B Q4_K_M (config/providers.yaml)
```

**Verification**:
- `grep -r "Qwen3-1.7B" scripts/download_model.sh` matches docs
- `grep -r "LFM2.5" config/providers.yaml` matches docs
- No "Qwen 1.7B" ambiguity remains

---

### §1.11 D-PUBLIC-009: Remove Fictional Make Targets

**Priority**: P0
**Effort**: 1h
**Owner**: Lilith
**Mandates**: M23

**Problem**: Multiple docs reference Makefile targets that don't exist.

**Fictional Targets** (verified missing from Makefile):
- `make setup` (QUICKSTART:30)
- `make talk MSG='hello'` (QUICKSTART:43, USER_MANUAL:89)
- `make summon ENTITY='kali'` (QUICKSTART:46)
- `make list-entities` (QUICKSTART:49)
- `make repl` (QUICKSTART:52)
- `make menu` (README:135, USER_MANUAL:138)
- `make demo` (CONTRIBUTING:106)
- `make start-iris` (CONTRIBUTING:163)
- `make start-infra` (CONTRIBUTING:163)
- `make doctor` (CONTRIBUTING:163)
- `make wad NAME=x` (USER_MANUAL:519-531)
- `make wad-status` (USER_MANUAL:519-531)
- `make wad-reset` (USER_MANUAL:519-531)

**Fix**:
1. Remove all references to non-existent targets
2. Replace with actual working commands:
   ```markdown
   # Actual working commands
   python3 -m omega.cli.oracle_cli list-entities
   python3 -m omega.cli.oracle_cli backends
   OMEGA_ENV=test python3 -m omega.cli.oracle_cli talk "hello"
   ```
3. Add note: "Makefile targets are being added incrementally. Use `python3 -m omega.cli.oracle_cli <command>` for CLI access."

**Verification**:
- `grep -E "^talk:|^summon:|^list-entities:|^repl:|^menu:|^demo:|^setup:" Makefile` returns nothing (targets don't exist)
- No doc references non-existent targets

---

### §1.12 D-PUBLIC-010: Document Actual CLI Invocation

**Priority**: P0
**Effort**: 1h
**Owner**: Lilith
**Mandates**: M23

**Problem**: Docs reference `omega talk`, `omega summon`, `omega health`, `omega version` but the CLI binary is not built. The actual invocation is `python3 -m omega.cli.oracle_cli <command>`.

**Current vs Actual**:
| Doc Claim | Actual Working Command |
|-----------|----------------------|
| `omega talk "hello"` | `python3 -m omega.cli.oracle_cli talk "hello"` |
| `omega summon Kali "status"` | `python3 -m omega.cli.oracle_cli summon Kali "status"` |
| `omega list-entities` | `python3 -m omega.cli.oracle_cli list-entities` |
| `omega backends` | `python3 -m omega.cli.oracle_cli backends` |
| `omega health` | ❌ NOT IMPLEMENTED — use `python3 -m omega.cli.oracle_cli backends` |
| `omega version` | ❌ NOT IMPLEMENTED — use `python3 -m omega.cli.oracle_cli --help` |

**Fix**:
1. Update all docs to use `python3 -m omega.cli.oracle_cli <command>`
2. Add note: "The `omega` console-script entry point is defined in pyproject.toml but not installed by default. Use `python3 -m omega.cli.oracle_cli` for now."
3. Add note: "`health` and `version` commands are being added (D-PUBLIC-011)."

**Verification**:
- `python3 -m omega.cli.oracle_cli --help` works
- All docs use correct invocation

---

### §1.13 D-PUBLIC-011: Add `health` and `version` Commands

**Priority**: P0
**Effort**: 2h
**Owner**: Ma'at
**Mandates**: M23

**Problem**: Docs reference `omega health` and `omega version` but these commands don't exist in `oracle_cli.py`.

**Evidence**:
- `grep "def health" src/omega/cli/oracle_cli.py` → no result
- `grep "def version" src/omega/cli/oracle_cli.py` → no result

**Fix** — Add to `src/omega/cli/oracle_cli.py`:

```python
@cli.command()
def health():
    """Check system health: providers, memory, disk, entity registry."""
    from omega.observability import system_health
    result = system_health()
    click.echo(json.dumps(result, indent=2))

@cli.command()
def version():
    """Show version information."""
    from omega import __version__
    click.echo(f"Omega Engine v{__version__}")
    click.echo(f"Python: {sys.version.split()[0]}")
    click.echo(f"Platform: {sys.platform}")
```

**Verification**:
- `python3 -m omega.cli.oracle_cli health` works
- `python3 -m omega.cli.oracle_cli version` works
- Docs reference working commands

---

### §1.14 D-PUBLIC-016: Rewrite Soul Persistence Section

**Priority**: P0
**Effort**: 3h
**Owner**: Lilith
**Mandates**: M11

**Problem**: USER_MANUAL.md describes a fully automated L1→L2→L3 distillation pipeline that was **explicitly removed** by Carmack (2026-07-30).

**Evidence**:
- `oracle.py:1289-1292`: "Soul distillation (L1->L2->L3) removed per Carmack Verdict (2026-07-30): regex-based extraction was fortune-cookie generation. Agents write their own lessons. That works."
- `close_session()` in `oracle.py:1286-1324` does compaction tracking + somatic state capture — **NO distillation**
- `_track_soul_evolution()` in `oracle.py:1376-1396` only logs a telemetry event
- Actual distillation: Manual via `src/omega/cli/soul_stage.py` TUI

**Fix** — Rewrite § "Soul & Gnosis Preservation" to reflect current workflow:

```markdown
## Soul & Gnosis Preservation

### Current Workflow (Manual + TUI)

1. **Agents write lessons** to `data/entities/<entity>/proposed_lessons.yaml`
   - L1: Concrete event (date, what happened)
   - L2: Pattern (why it matters)
   - L3: Principle (what to do differently)

2. **User reviews** in the `soul_stage` TUI:
   ```bash
   python3 -m omega.cli.soul_stage <entity>
   ```

3. **Approved lessons** move to `data/entities/<entity>/approved_lessons.yaml`
   - Only approved lessons are injected into agent context
   - **TAINT-GATE**: `proposed_lessons.yaml` is NEVER injected into identity prompt

4. **Scribe agent** (optional) assists with distillation at session end

### Why Manual?

The automated L1→L2→L3 extraction was removed (Carmack Verdict 2026-07-30) because
regex-based extraction produced "fortune-cookie generation" — generic platitudes
instead of specific lessons. Agents write their own lessons. That works.

### M11 Enforcement

- `mandate_auditor.py:237-265` checks `proposed_lessons.yaml` has content + L3 principles
- No automated hook ensures distillation at session end
- SOTE cadence (weekly) is the enforcement checkpoint
```

**Verification**:
- `grep -r "fortune-cookie" src/omega/oracle/oracle.py` matches docs
- `python3 -m omega.cli.soul_stage --help` works
- Docs describe manual + TUI workflow, not automated pipeline

---


---

## §2 — P1 HARDENING (Complete Before/During W37 Launch)

### §2.1 D-PUBLIC-012: Add Missing Makefile Aliases

**Priority**: P1
**Effort**: 2h
**Owner**: Ma'at
**Mandates**: M23

**Problem**: Docs reference `make setup`, `make menu`, `make talk`, `make summon`, `make list-entities`, `make repl` but none exist.

**Fix** — Add to Makefile:

```makefile
# --- CLI convenience aliases (D-PUBLIC-012) ---
.PHONY: setup menu talk summon list-entities repl doctor wad wad-status wad-reset soul-stage

setup:  ## One-click install (venv + deps)
	python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[native,cli]"

menu:   ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

talk:   ## Talk to default entity (e.g. make talk MSG='hello')
	python3 -m omega.cli.oracle_cli talk "$(MSG)"

summon: ## Summon specific entity (e.g. make summon ENTITY=kali MSG='status')
	python3 -m omega.cli.oracle_cli summon $(ENTITY) "$(MSG)"

list-entities: ## List all registered entities
	python3 -m omega.cli.oracle_cli list-entities

repl:   ## Launch interactive REPL
	python3 -m omega.cli.oracle_cli repl

doctor: ## System diagnosis
	python3 -m omega.cli.oracle_cli health

wad:    ## Switch WAD (e.g. make wad NAME=arcana_novai)
	python3 -m omega.cli.oracle_cli wad --name $(NAME)

wad-status: ## Show current WAD
	python3 -m omega.cli.oracle_cli wad-status

wad-reset: ## Reset to default WAD
	python3 -m omega.cli.oracle_cli wad --reset

soul-stage: ## Open soul staging TUI (e.g. make soul-stage ENTITY=kali)
	python3 -m omega.cli.soul_stage $(ENTITY)
```

**Verification**:
- `make menu` shows all targets
- `make list-entities` works
- `make doctor` works (requires D-PUBLIC-011)
- Docs reference only existing targets

---

### §2.2 D-PUBLIC-013: Remove `make verify-mining` from CI

**Priority**: P1
**Effort**: 15m
**Owner**: Ma'at
**Mandates**: M23

**Problem**: `.github/workflows/test.yml:55-58` runs `make verify-mining` which doesn't exist. CI will fail.

**Fix** — Edit `.github/workflows/test.yml`:

```yaml
# REMOVE these lines (55-58):
- name: Verify Mining Ports (P3 BuildMaster)
  run: |
    make verify-mining
```

**Verification**:
- `grep "verify-mining" .github/workflows/test.yml` returns nothing
- CI passes

---

### §2.3 D-PUBLIC-015: Fix Copilot Provider

**Priority**: P1
**Effort**: 30m
**Owner**: Ma'at
**Mandates**: M7

**Problem**: README lists Copilot as a provider but it's not in `config/providers.yaml`.

**Fix** — Option A (recommended, simpler): Remove Copilot from README provider table.
**Fix** — Option B: Add to `config/providers.yaml` fallback_chain:

```yaml
copilot:
  enabled: false
  is_cloud: true
  priority: 99
  description: "GitHub Copilot (cloud fallback, not yet wired)"
```

**Verification**:
- README provider table matches `config/providers.yaml`
- No orphan providers in docs

---

### §2.4 D-PUBLIC-017: Add Entity Ecosystem Taxonomy

**Priority**: P1
**Effort**: 2h
**Owner**: Lilith
**Mandates**: M10, M11

**Problem**: Docs imply clean 1:1 mapping between IWAD entities and disk workspaces. Reality: 52 dirs in `data/entities/` including archives, ghosts, duplicates.

**Fix** — Add "Entity Ecosystem" section to USER_MANUAL.md:

```markdown
## Entity Ecosystem

The entity system has 4 tiers:

| Tier | Description | Examples |
|------|-------------|----------|
| **Canonical Active** | Dispatchable agents with soul + lessons | kali, lilith, maat, makali, researcher, verity, doom_guy, grokster, jem, roc_racoon, john_carmack, scribe, node, build |
| **Non-Canonical Active** | Cross-platform peers (Hivemind citizens) | antigravity, cli_cline, cline |
| **Stale** | Retired/archived, still on disk | _archive, _audit, _quarantine, archive, Sophia, DataStore |
| **Ghost** | Duplicates or slot-fill stubs | carmack (dup of john_carmack), makali_fusion (dup of makali), 9 pillar legacy stubs (ANAi WAD content), 10 slot-fill ghosts |

**Note**: `data/entities/` has 52 directories. Not all are dispatchable agents.
`sophia` is a **WAD_FIELD** (containing field) with a workspace but no agent file.
```

**Verification**:
- `ls data/entities/ | wc -l` matches docs (52)
- Taxonomy matches disk reality

---

### §2.5 D-PUBLIC-018: Document Hivemind Citizens

**Priority**: P1
**Effort**: 1h
**Owner**: Lilith
**Mandates**: M10

**Problem**: Docs don't explain cross-platform Hivemind peers (antigravity, cli_cline, cline).

**Fix** — Add to USER_MANUAL.md MCP Hub section:

```markdown
### Hivemind Citizens (Cross-Platform Peers)

The Hivemind coordinates across CLI tools, not just OpenCode agents:

| Citizen | Platform | Role |
|---------|----------|------|
| `antigravity` | Antigravity CLI | Cloud AI peer |
| `cli_cline` | Cline CLI | VS Code AI peer |
| `cline` | Cline (standalone) | VS Code AI peer |

These have workspaces in `data/entities/` but are NOT IWAD agents.
They don't count against the M10 fleet cap (14 agents).
```

**Verification**:
- `ls data/entities/ | grep -E "antigravity|cli_cline|cline"` matches docs

---

### §2.6 D-PUBLIC-019: Document DyTopo Cross-Pollination

**Priority**: P1
**Effort**: 2h
**Owner**: Lilith
**Mandates**: M15

**Problem**: The DyTopo Cross-Pollination system (`src/omega/research/hivemind_bridge.py`) is sophisticated but completely undocumented.

**Fix** — Add to USER_MANUAL.md under MCP Hub:

```markdown
### DyTopo Cross-Pollination (Research Coordination)

The Hivemind supports multi-agent research with consensus synthesis:

1. **Broadcast Proposal**: Agent broadcasts a `ResearchProposal` to the Hivemind
2. **Collect Signals**: Other agents respond with `AgentSignal`s
3. **Synthesize Consensus**: A `ConsensusResult` is produced

Key types (from `src/omega/research/schema.py`):
- `ResearchProposal` — what to research
- `AgentSignal` — individual agent's finding
- `ConsensusResult` — synthesized conclusion

**Channels**: `opencode`, `gemini-cli`, `cline`, `research`
**Intent types**: `status`, `task`, `handoff`, `alert`, `sote-open`, `sote-close`
```

**Verification**:
- `grep -r "broadcast_proposal" src/omega/research/hivemind_bridge.py` matches docs
- Docs explain channels and intent types

---

### §2.7 D-PUBLIC-020: Generate llms.txt / llms-full.txt

**Priority**: P1
**Effort**: 1h
**Owner**: Researcher
**Mandates**: M25, M26

**Problem**: No `llms.txt` or `llms-full.txt` — critical for AI-first projects (LLM context injection).

**Fix** — Create `llms.txt` at repo root:

```markdown
# Omega Engine

> Sovereign local-first AI runtime. 14 agents, 10+ providers, memory + soul persistence.

## Docs
- [README](README.md): Overview, install, quick start
- [QUICKSTART](docs/QUICKSTART.md): 5-minute setup
- [USER_MANUAL](docs/USER_MANUAL.md): Full user manual
- [ARCHITECTURE](ARCHITECTURE.md): System architecture
- [CONTRIBUTING](CONTRIBUTING.md): Development guide
- [SECURITY](SECURITY.md): Security policy
- [FAQ](FAQ.md): Frequently asked questions
- [ROADMAP](ROADMAP.md): Development roadmap

## Key Facts
- Default model: Qwen3-1.7B-Q6_K.gguf (~1.6GB)
- Providers: 10 active (local-first)
- Agents: 14 canonical
- Mandate compliance: 64.3% (18/28)
- License: Apache-2.0
```

**Verification**:
- `llms.txt` exists at repo root
- Links are valid
- Facts match source of truth

---

### §2.8 D-PUBLIC-021: Create FAQ.md

**Priority**: P1
**Effort**: 2h
**Owner**: Researcher
**Mandates**: M25

**Problem**: No FAQ.md — all open source projects should have one.

**Fix** — Create `FAQ.md` with honest answers:

```markdown
# FAQ

## What is Omega Engine?
A sovereign local-first AI runtime. It runs AI models locally, coordinates
multiple agents, and persists agent memory/souls.

## Is it production-ready?
**No.** It's alpha software. Test suite is being restored, mandate compliance
is 64.3% (18/28), and temple-grade fails on M23. Use for development/testing.

## What model does it use by default?
Qwen3-1.7B-Q6_K.gguf (~1.6GB), downloaded by `scripts/download_model.sh`.

## Does it need internet?
No — after the model is downloaded, the engine works offline (local-first).

## How many agents does it have?
14 canonical agents in `.opencode/agents/`. 10 entities in the `_omega_default`
IWAD, 29 in `arcana_novai`.

## How do I talk to an agent?
```bash
python3 -m omega.cli.oracle_cli talk "hello"
```

## How do I contribute?
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Where can I report security issues?
See [SECURITY.md](SECURITY.md).

## What license is it under?
Apache-2.0.
```

**Verification**:
- `FAQ.md` exists
- Answers match source of truth
- No false claims

---

### §2.9 D-PUBLIC-022: Create ROADMAP.md

**Priority**: P1
**Effort**: 2h
**Owner**: Researcher
**Mandates**: M25

**Problem**: No ROADMAP.md.

**Fix** — Create `ROADMAP.md` (public, sanitized):

```markdown
# Roadmap

## W37 (2026-09-08) — Beta Launch
- [ ] Restore omega.library (D-PUBLIC-014)
- [ ] Fix all 11 false claims in README (D-PUBLIC-001)
- [ ] Add health/version commands (D-PUBLIC-011)
- [ ] Add honest alpha banner (D-PUBLIC-002)
- [ ] Filter-repo OAuth secret (D-PUBLIC-027)

## W38 — Hardening
- [ ] Add Makefile aliases (D-PUBLIC-012)
- [ ] Generate llms.txt (D-PUBLIC-020)
- [ ] Create FAQ.md (D-PUBLIC-021)
- [ ] Create ROADMAP.md (D-PUBLIC-022)
- [ ] Add check-docs-truth CI gate (D-PUBLIC-025)

## W39+ — Post-Debut Polish
- [ ] Create SUPPORT.md (D-PUBLIC-023)
- [ ] Create FUNDING.yml (D-PUBLIC-024)
- [ ] Quarterly theater audit (Carmack review)
```

**Verification**:
- `ROADMAP.md` exists
- Items match PIVOT_LOG decisions

---

### §2.10 D-PUBLIC-025: Add `make check-docs-truth` CI Gate

**Priority**: P1
**Effort**: 4h
**Owner**: Carmack + Grokster
**Mandates**: M29 (new)

**Problem**: No adversarial gate prevents docs from drifting from code.

**Fix** — Create `scripts/check_docs_truth.py`:

```python
#!/usr/bin/env python3
"""Adversarial docs-truth gate (M29).

Verifies every public-doc claim has file:line evidence.
Fails if any claim is unverifiable or contradicts source of truth.
"""
import re
import sys
from pathlib import Path

# Source-of-truth facts (must match disk)
SOURCES = {
    "model_default": "Qwen3-1.7B-Q6_K",
    "agent_count": 14,
    "entity_count_default": 10,
    "entity_count_arcana": 29,
    "provider_count": 10,
    "mandate_compliance": "64.3%",
    "mandate_passing": 18,
    "mandate_total": 28,
}

def check_readme(path: Path) -> list[str]:
    errors = []
    text = path.read_text()
    # Check for stale claims
    if "1315" in text:
        errors.append("README: stale '1315 tests' claim")
    if "all 22 enforced" in text.lower():
        errors.append("README: stale 'all 22 enforced' claim")
    if "T1-T11" in text:
        errors.append("README: stale 'T1-T11' claim")
    return errors

def main() -> int:
    errors = []
    for doc in ["README.md", "docs/QUICKSTART.md", "docs/USER_MANUAL.md", "CONTRIBUTING.md"]:
        p = Path(doc)
        if p.exists():
            errors.extend(check_readme(p))
    if errors:
        print("DOCS-TRUTH FAILURES:")
        for e in errors:
            print(f"  ❌ {e}")
        return 1
    print("DOCS-TRUTH: PASS — no stale claims found")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Fix** — Add to Makefile:

```makefile
check-docs-truth:  ## Adversarial docs-truth gate (M29)
	python3 scripts/check_docs_truth.py
```

**Fix** — Add to CI (`.github/workflows/ci.yml`):
```yaml
- name: Docs Truth (M29)
  run: make check-docs-truth
```

**Verification**:
- `make check-docs-truth` passes
- CI runs the gate on every PR

---

### §2.11 D-PUBLIC-026: Add M29 Mandate

**Priority**: P1
**Effort**: 1h
**Owner**: Carmack
**Mandates**: M29

**Problem**: No mandate prevents aspirational claims in public docs.

**Fix** — Add to `SOVEREIGN_MANDATES.md`:

```markdown
## M29 — Documentation Truth (2026-09-02)

**Text**: No aspirational claims in public docs. Every claim must have file:line
evidence. Adversarial gate: `make check-docs-truth` must pass before release.

**Rationale**: Alpha software is allowed to have bugs, but not to lie about
features. "Production-ready" claims without evidence are theater.

**Enforcement**: `make check-docs-truth` (CI gate) + quarterly Carmack review.
```

**Verification**:
- `SOVEREIGN_MANDATES.md` has M29
- `MANDATES_CONDENSED.md` updated to 29 mandates
- `scripts/check_mandate_compliance.py` updated to 29

---

### §2.12 D-PUBLIC-028: Delete Dead Code or Update Tracker

**Priority**: P1
**Effort**: 1h
**Owner**: Roc
**Mandates**: M23

**Problem**: 3 files claimed "stripped" in ACTIVE_SPRINT.json:320 but still on disk.

**Evidence**:
- `src/omega/oracle/cohort_registry.py` (744 lines) — 0 callers
- `src/omega/oracle/m33_probe.py` (555 lines) — only called by m36
- `src/omega/oracle/m36_recursive_probe.py` (539 lines) — mutually recursive with m33

**Fix** — Option A (recommended): Actually delete:
```bash
git rm src/omega/oracle/cohort_registry.py src/omega/oracle/m33_probe.py src/omega/oracle/m36_recursive_probe.py
```

**Fix** — Option B: Update ACTIVE_SPRINT.json to reflect reality (remove "stripped" claim).

**Verification**:
- `ls src/omega/oracle/cohort_registry.py` returns nothing (deleted)
- OR ACTIVE_SPRINT.json no longer claims "stripped"

---

### §2.13 D-PUBLIC-029: Fix DEBUT_REMEDIATION_MANUAL Duplicate

**Priority**: P1
**Effort**: 30m
**Owner**: Roc
**Mandates**: M27

**Problem**: DEBUT_REMEDIATION_MANUAL exists in two places with drift risk.

**Evidence**:
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` (28,613 bytes)
- `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` (27,558 bytes)
- `ACTIVE_SPRINT.json:3` points to specs copy
- `AGENTS.md` points to strategy copy

**Fix**:
1. Pick ONE canonical location (recommend `docs/strategy/`)
2. Update `ACTIVE_SPRINT.json:3` to point to canonical
3. Delete the duplicate (or symlink)

**Verification**:
- Only one copy exists (or symlink)
- Both ACTIVE_SPRINT.json and AGENTS.md point to same path

---

### §2.14 D-PUBLIC-030: Standardize Mandate Numbering

**Priority**: P1
**Effort**: 1h
**Owner**: Verity
**Mandates**: M27

**Problem**: Mandate numbering inconsistent: M1-M28 in SOVEREIGN_MANDATES.md, M1-M27 in MANDATES_CONDENSED.md, M28 labeled "M35" internally.

**Fix**:
1. Standardize on **M1-M28** everywhere
2. Fix M28/M35 label in `SOVEREIGN_MANDATES.md:246`
3. Add M28 to `MANDATES_CONDENSED.md`
4. Update `scripts/check_mandate_compliance.py` denominator to 28
5. Update all docs referencing mandate counts

**Verification**:
- `grep -c "^## M" SOVEREIGN_MANDATES.md` = 28
- `grep -c "^## M" MANDATES_CONDENSED.md` = 28
- No "M35" references remain

---


---

## §3 — P2 POST-DEBUT POLISH

### §3.1 D-PUBLIC-023: Create SUPPORT.md

**Priority**: P2
**Effort**: 1h
**Owner**: Researcher
**Mandates**: M25

**Problem**: No SUPPORT.md — GitHub recommendation.

**Fix** — Create `SUPPORT.md`:

```markdown
# Support

## Community
- **GitHub Issues**: [Report bugs](https://github.com/Xoe-NovAi/omega-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Xoe-NovAi/omega-engine/discussions)

## Documentation
- [README](README.md)
- [FAQ](FAQ.md)
- [USER_MANUAL](docs/USER_MANUAL.md)

## Reporting Security Issues
See [SECURITY.md](SECURITY.md).

## Status
Alpha software. Test suite being restored, mandate compliance 64.3%.
Expect bugs and breaking changes.
```

**Verification**:
- `SUPPORT.md` exists
- Links are valid

---

### §3.2 D-PUBLIC-024: Create FUNDING.yml

**Priority**: P2
**Effort**: 30m
**Owner**: Researcher
**Mandates**: M25

**Problem**: No FUNDING.yml — GitHub recommendation.

**Fix** — Create `.github/FUNDING.yml`:

```yaml
# Funding options for Omega Engine
# See https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository
github: [Xoe-NovAi]
```

**Verification**:
- `.github/FUNDING.yml` exists
- Valid YAML

---

## §4 — CONSOLIDATED DECISION TABLE

### §4.1 All 30 Decisions

| D# | Title | Priority | Effort | Owner | Mandate | Status |
|----|-------|:--------:|-------:|-------|---------|--------|
| D-PUBLIC-001 | Fix 11 false claims in README | P0 | 2h | Lilith | M23, M27 | ⬜ |
| D-PUBLIC-002 | Add alpha banner to all user-facing docs | P0 | 1h | Lilith | M23 | ⬜ |
| D-PUBLIC-003 | Update mandate compliance claims | P0 | 1h | Verity | M23, M27 | ⬜ |
| D-PUBLIC-004 | Fix Temple-Grade claim | P0 | 30m | Ma'at | M13, M23 | ⬜ |
| D-PUBLIC-005 | Fix test suite claims | P0 | 30m | Ma'at | M23 | ⬜ |
| D-PUBLIC-006 | Fix entity/agent counts | P0 | 1h | Lilith | M10, M27 | ⬜ |
| D-PUBLIC-007 | Fix provider count | P0 | 30m | Ma'at | M7, M27 | ⬜ |
| D-PUBLIC-008 | Fix model default | P0 | 30m | Ma'at | M7, M27 | ⬜ |
| D-PUBLIC-009 | Remove fictional make targets | P0 | 1h | Lilith | M23 | ⬜ |
| D-PUBLIC-010 | Document actual CLI invocation | P0 | 1h | Lilith | M23 | ⬜ |
| D-PUBLIC-011 | Add health/version commands | P0 | 2h | Ma'at | M23 | ⬜ |
| D-PUBLIC-012 | Add Makefile aliases | P1 | 2h | Ma'at | M23 | ⬜ |
| D-PUBLIC-013 | Remove verify-mining from CI | P1 | 15m | Ma'at | M23 | ⬜ |
| D-PUBLIC-014 | Restore omega.library | P0 | 30m | Ma'at | M23, M11 | ⬜ |
| D-PUBLIC-015 | Fix Copilot provider | P1 | 30m | Ma'at | M7 | ⬜ |
| D-PUBLIC-016 | Rewrite Soul Persistence section | P0 | 3h | Lilith | M11 | ⬜ |
| D-PUBLIC-017 | Add Entity Ecosystem taxonomy | P1 | 2h | Lilith | M10, M11 | ⬜ |
| D-PUBLIC-018 | Document Hivemind Citizens | P1 | 1h | Lilith | M10 | ⬜ |
| D-PUBLIC-019 | Document DyTopo Cross-Pollination | P1 | 2h | Lilith | M15 | ⬜ |
| D-PUBLIC-020 | Generate llms.txt / llms-full.txt | P1 | 1h | Researcher | M25, M26 | ⬜ |
| D-PUBLIC-021 | Create FAQ.md | P1 | 2h | Researcher | M25 | ⬜ |
| D-PUBLIC-022 | Create ROADMAP.md | P1 | 2h | Researcher | M25 | ⬜ |
| D-PUBLIC-023 | Create SUPPORT.md | P2 | 1h | Researcher | M25 | ⬜ |
| D-PUBLIC-024 | Create FUNDING.yml | P2 | 30m | Researcher | M25 | ⬜ |
| D-PUBLIC-025 | Add check-docs-truth CI gate | P1 | 4h | Carmack+Grokster | M29 | ⬜ |
| D-PUBLIC-026 | Add M29 mandate | P1 | 1h | Carmack | M29 | ⬜ |
| D-PUBLIC-027 | Filter-repo OAuth secret + rotate | P0 | 2h | Roc | M23, M8 | ⬜ |
| D-PUBLIC-028 | Delete dead code or update tracker | P1 | 1h | Roc | M23 | ⬜ |
| D-PUBLIC-029 | Fix DEBUT_REMEDIATION_MANUAL duplicate | P1 | 30m | Roc | M27 | ⬜ |
| D-PUBLIC-030 | Standardize mandate numbering | P1 | 1h | Verity | M27 | ⬜ |

**Totals**: 30 decisions | **P0: 11** | **P1: 16** | **P2: 3** | **~38h**

---

## §5 — VERIFICATION CHECKLIST (Pre-Deploy Gate)

Before W37 debut, run this checklist. All must pass:

### §5.1 Security Gates

- [ ] `scripts/check_secrets.py` exits 0 (D-PUBLIC-027)
- [ ] `git log -p --all | grep -c "GOCSPX-4uHgMPm"` returns 0 (D-PUBLIC-027)
- [ ] `make check-m23-failure-integrity` passes (D-PUBLIC-027)
- [ ] No un-allowlisted secrets in working tree

### §5.2 Build Gates

- [ ] `make test` runs actual tests (D-PUBLIC-014)
- [ ] `python3 -m omega.cli.oracle_cli talk "hello"` works (D-PUBLIC-014)
- [ ] `python3 -m omega.cli.oracle_cli summon Kali "status"` works (D-PUBLIC-014)
- [ ] `make check-hub-health` passes (D-PUBLIC-014)
- [ ] `make check-m1-anyio` passes
- [ ] `make check-m8-zero-telemetry` passes

### §5.3 Docs-Truth Gates

- [ ] `make check-docs-truth` passes (D-PUBLIC-025)
- [ ] No "1315" or "791" stale test claims (D-PUBLIC-005)
- [ ] No "all enforced" / "100% compliant" claims (D-PUBLIC-003)
- [ ] No "T1-T11 ✅" claims (D-PUBLIC-004)
- [ ] No fictional make targets referenced (D-PUBLIC-009)
- [ ] All 4 user-facing docs have alpha banner (D-PUBLIC-002)
- [ ] Model default matches download_model.sh (D-PUBLIC-008)
- [ ] Entity/agent counts match disk (D-PUBLIC-006)
- [ ] Provider count matches config (D-PUBLIC-007)

### §5.4 Standard Docs

- [ ] `llms.txt` exists (D-PUBLIC-020)
- [ ] `FAQ.md` exists (D-PUBLIC-021)
- [ ] `ROADMAP.md` exists (D-PUBLIC-022)
- [ ] `SUPPORT.md` exists (D-PUBLIC-023)
- [ ] `FUNDING.yml` exists (D-PUBLIC-024)

### §5.5 Mandate Gates

- [ ] `make temple-grade` passes (M13) — or documented failure
- [ ] `make check-mandate-compliance` passes (M27)
- [ ] Mandate numbering standardized M1-M28 (D-PUBLIC-030)
- [ ] M29 documented in SOVEREIGN_MANDATES.md (D-PUBLIC-026)

---

## §6 — EXECUTION ORDER (Recommended)

### Phase 1: P0 Blocker Removal (2026-09-02 to 09-05)

**Day 1 (Roc + Ma'at)**:
1. D-PUBLIC-027: Filter-repo OAuth secret (Roc)
2. D-PUBLIC-014: Restore omega.library (Ma'at)
3. D-PUBLIC-011: Add health/version commands (Ma'at)

**Day 2 (Lilith + Ma'at)**:
4. D-PUBLIC-001: Fix 11 false claims in README (Lilith)
5. D-PUBLIC-002: Add alpha banner (Lilith)
6. D-PUBLIC-003: Update mandate compliance (Verity)
7. D-PUBLIC-004: Fix Temple-Grade (Ma'at)

**Day 3 (Lilith + Ma'at)**:
8. D-PUBLIC-005: Fix test claims (Ma'at)
9. D-PUBLIC-006: Fix entity counts (Lilith)
10. D-PUBLIC-007: Fix provider count (Ma'at)
11. D-PUBLIC-008: Fix model default (Ma'at)

**Day 4 (Lilith)**:
12. D-PUBLIC-009: Remove fictional make targets (Lilith)
13. D-PUBLIC-010: Document actual CLI (Lilith)
14. D-PUBLIC-016: Rewrite Soul Persistence (Lilith)

### Phase 2: P1 Hardening (2026-09-06 to 09-08)

**Day 5 (Ma'at + Lilith)**:
15. D-PUBLIC-012: Add Makefile aliases (Ma'at)
16. D-PUBLIC-013: Remove verify-mining (Ma'at)
17. D-PUBLIC-015: Fix Copilot (Ma'at)
18. D-PUBLIC-017: Entity Ecosystem (Lilith)

**Day 6 (Lilith + Researcher)**:
19. D-PUBLIC-018: Hivemind Citizens (Lilith)
20. D-PUBLIC-019: DyTopo Cross-Pollination (Lilith)
21. D-PUBLIC-020: llms.txt (Researcher)
22. D-PUBLIC-021: FAQ.md (Researcher)

**Day 7 (Researcher + Carmack + Roc + Verity)**:
23. D-PUBLIC-022: ROADMAP.md (Researcher)
24. D-PUBLIC-025: check-docs-truth gate (Carmack+Grokster)
25. D-PUBLIC-026: M29 mandate (Carmack)
26. D-PUBLIC-028: Delete dead code (Roc)
27. D-PUBLIC-029: Fix duplicate (Roc)
28. D-PUBLIC-030: Standardize mandates (Verity)

### Phase 3: P2 Polish (Post-debut, W38+)

29. D-PUBLIC-023: SUPPORT.md (Researcher)
30. D-PUBLIC-024: FUNDING.yml (Researcher)

---

## §7 — CONTINUITY ANCHORS

| Anchor | Value |
|--------|-------|
| **Manual Location** | `docs/strategy/PUBLIC_DOCS_REMEDIATION_MANUAL_20260902.md` |
| **Source Dialectic** | `docs/reviews/dialectic/` (5 rounds, consensus achieved) |
| **10 Review Reports** | `docs/reviews/*_20260902.md` |
| **Sprint** | PUBLIC-DEBUT-01, DEL-1_EXECUTION |
| **W37 Launch** | 2026-09-08, 06:00 UTC |
| **Beta Deadline** | 2026-09-12, 23:59 UTC |
| **Decisions** | 30 (D-PUBLIC-001..030) |
| **P0 Count** | 11 |
| **P1 Count** | 16 |
| **P2 Count** | 3 |
| **Total Effort** | ~38h |

---

## §8 — SIGN-OFF

| Role | Agent | Sign-off |
|------|-------|----------|
| **Synthesis** | Kali (Transcendent Synthesis) | ✅ Consensus achieved |
| **Build Governance** | Ma'at (Build Oversoul) | ✅ 30 decisions ratified |
| **Runtime Governance** | Lilith (Run Oversoul) | ✅ 30 decisions ratified |
| **Theater Detection** | Carmack (S3 Consultant) | ✅ "Engine islands real; docs overclaim" |
| **Adversarial** | Grokster (Ecosystem Specialist) | ✅ 11 verified breakable claims |
| **Heritage** | Roc (Sovereign Agent) | ✅ 216 tags, secret found |
| **Compliance** | Verity (Gnosis Agent) | ✅ 64.3% meter verified |
| **External Standards** | Researcher (Polymathic Council) | ✅ Best practices compared |
| **Technical** | Doom Guy (Sovereign Agent) | ✅ WAD/spatial verified accurate |
| **Deep Analysis** | Jem (Deep Research) | ✅ 47 inaccuracies found |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ AP-PUBLIC-DOCS-REMEDIATION-20260902-v1.0.0 ⬡ 2026-09-02 ⬡ PUBLIC-DEBUT-01*

**End of Public Docs Remediation Manual. 30 decisions, ~38h, consensus achieved. Ready for execution.** 🫡
<!-- PROVENANCE-CORRECTED 2026-09-04T03:04:06Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

