---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "cline_review_gap_analysis"
document_id: "cline-review-gap-analysis-phases-20260828"
title: "Cline — Repo Review Gap Analysis + Targeted Categorical Phases (Launch Day)"
status: "ACTIVE — companion to CLINE_FULL_REVIEW_ROLLUP_20260828.md v2"
date: "2026-08-28"
---

# 🔱 Repo Review Gap Analysis + Targeted Categorical Phases
**AP**: `AP-CLINE-GAP-PHASES-20260828-v1.0.0` · ⬡ OMEGA ⬡ CLINE ⬡ deepseek-v4-flash (1M) ⬡ cline ⬡ trc_alpha_launch

> Companion to the deep rollup. Answers: what did the 8-dim sweep STILL miss, and how do we execute the remediation as targeted categorical phases with hard gates?

---

## §1 GAPS FOUND BEYOND THE 8-DIM SWEEP (this session, all verified)

### G-1 [P1] Twelve PHANTOM Makefile commands documented as real
- `.clinerules` + AGENTS.md claimed `mandate-gates`, `mcp-check`, `doctor`, `fleet-status`, `sovereignty`, `link-p9-heartbeat/agents/dispatch/inbox`, `start-infra`, `stop-infra`, `firewall-check`. **None exist** in Makefile (`grep -E '^[a-z-]+:' Makefile` exhaustive).
- Real equivalents: `check-mandate-compliance`, `gate-secrets`, `check-tracking-state`, `m23-baseline`, `observe`, `install-guarded`, `sweep-tasks`, `check-asyncio-import`; infra = podman quadlet; hivemind = MCP tools.
- **Action**: docs fixed in `.clinerules` v8.0.0 (this session). AGENTS.md + CLINE_CLI_BRIEFING pending same pass (Phase 5).

### G-2 [P1] test.yml does NOT cover release/debut
- `.github/workflows/test.yml` triggers: `push: [main, develop]`, `pull_request: [main]`. The launch branch is invisible to the suite that matters.
- **Action**: add `release/debut` (+ `release/initial-v1`) to triggers, or a dedicated `debut-test.yml`. (secret-scan/allowlist-check DO cover release/debut ✓.)

### G-3 [P1] CI calls a nonexistent target: `make verify-mining`
- `.github/workflows/test.yml` step "Verify Mining Ports (P3 BuildMaster)" runs `make verify-mining` — **no such target in Makefile**. First CI run on a branch that reaches that step reds. Also `make … ` inside test.yml references `make verify-mining` only.
- **Action**: implement a real `verify-mining` target (port probe for the mining workers) or delete the step. Phase 2.

### G-4 [P1/M2] Hardcoded absolute path in core
- `src/omega/memory/embeddings.py:472`: `model_path="/media/arcana-novai/omega_library/models/embeddings/embeddinggemma-300m-Q6_K.gguf"`. Breaks any machine that isn't this box; violates "no hardcoded paths in src/omega/" (M2/Engine-Stack + SEC-06).
- **Action**: route through `env:OMEGA_MODELS_DIR` like the rest of config/models.yaml (Phase 4, with G-13 sibling).

### G-5 [P1] The P1-1 logger landmine is LIVE on this machine
- `data/vault/keys.json.enc` exists (modified **2026-08-28 11:58**). oracle_cli.py:83 calls `_inject_vault_to_env()`; on decrypt success L85 `logger.info` fires before `logger = …` (L106); on decrypt failure L80 `logger.debug` fires first. Any master key present (keyring/`~/.config/omega/vault_master.key`) → **import-time NameError**.
- `--help` passed only because this session's decrypt path returned 0 without hitting either branch. Reproduce in CI with a fake vault fixture.
- **Action**: PR-C (move logger above L80) + regression test with fake vault. Phase 1.

### G-6 [P1/SEC] Dependency vulnerability posture UNKNOWN
- `pip-audit` produced a **0-byte JSON and no process** (silent failure; likely no network/not installed). No CVE sweep evidence anywhere in the tree or CI.
- **Action**: decision — treat as out-of-scope for debut WITH a documented waiver (SEC-08 fallback), or run once in CI (Phase 7 observatory). Not silently both.

### G-7 [P1/M27] OMEGA_ENGINE.md state SSOT stale
- §2 claims 25 mandates v3.7.0 (actual 27 v3.8.0), 1706 tests, dates 2026-07-30, fleet 13 — contradicts ACTIVE_SPRINT.json and this review. DEBUT_REMEDIATION_MANUAL acceptance gate literally requires "OMEGA_ENGINE.md matches ACTIVE_SPRINT.json".
- **Action**: refresh table (mandates 27, 161 test files, 14/14 fleet, sprint PUBLIC-DEBUT-01 EXECUTION_MINIMAL, D-603, launch-gate status) + LAST_VERIFIED cadence. Phase 5.

### G-8 [P1/M10] Fleet at hard cap
- `.opencode/agents/` = **14** entries (M10 max 14). New agents require slot eviction + gap analysis; fleet lists in docs are stale (AGENTS.md says 13).
- **Action**: record in OMEGA_ENGINE.md + policy for slot review. Phase 5/7.

### G-9 [P1/M11] Soul layout non-uniform, 24/56 substantive
- `find data/entities -name proposed_lessons.yaml -size +500c` = 24 of 56 entities; files split between `<entity>/proposed_lessons.yaml` and `<entity>/memory/proposed_lessons.yaml`. NEW-04 baseline validated.
- **Action**: canonical layout + 56/56 target. Phase 4/7.

### G-10 [P1] .gitleaksignore baseline drift
- Makefile gate comment claims "31 baselined FPs in .gitleaksignore"; file has 66 lines; gitleaks still reports 53 findings. After P0-3 scrub the ignore file must be rebuilt (fingerprint-per-leak with WHY line) so a clean scan = 0.
- **Action**: part of PR-2 (Wave 0). Phase 0.

### G-11 [P1] Full-suite green never proven on CI
- No CI evidence of a full `pytest tests/` green run (test.yml not on release/debut + verify-mining breakage). Dev-box run died without summary. "1706 collected" baselines in docs are unverifiable.
- **Action**: first true full-suite CI green becomes a named deliverable. Phase 2.

### G-12 [P2] Provider config precedence ambiguity
- `google` (p4) and `google-compat` (p4) share priority and both list `gemini-2.5-pro`; `fallback_chain` includes both with duplicate is_cloud. Ambiguity for model→provider resolution and for `fallback_resolver` cvars.
- **Action**: normalize (drop one legacy alias or split priorities); contract test. Phase 3.

### G-13 [P2] Flat-chain vs rich-map provider config (SSOT bend)
- providers.yaml:103-104 comment: factory passes ONLY the flat `fallback_chain` entry — the rich per-provider `base_url`/`api_key` maps are NOT read for all providers. opencode-zen works via env; others may silently default. Needs a contract test asserting each provider's effective base_url/api_key source. Phase 3.

### G-14 [P2] Manual duplicated across two paths
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` AND `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` both exist; ACTIVE_SPRINT.json campaign → specs path; AGENTS.md → strategy path. Drift risk.
- **Action**: canonical one; other becomes symlink/redirect stub. Phase 5.

### G-15 [P2] `omega health` documented but not verified
- CLI `--help` surface (verified): talk, summon, youtube, list-entities, backends, entity-info, model-status, hardware-stats, local-queue, bench-*, library-*, header, mcp-restart, process-queue, demand-*, check-feed, add-entity, default-entity, bundle… **`health` and `verify` were not observed**. Either confirm or remove from docs (removed from .clinerules v8). Phase 5.

### G-16 [P2] MCP server states unprobed this session
- omega-hub proven (65+ tools live). searxng/firecrawl/exa/github tool availability NOT exercised in-session; exa needs EXA_API_KEY (known).
- **Action**: one probe workflow (`mcp-check` equivalent via curls) as part of Phase 7 observatory.

### G-17 [P1/PRIVACY] Entity souls overshared in public cut
- PUBLIC_ALLOWLIST.txt says data/entities ships "one default soul"; reality: **37 entity soul/backup files** on release/debut (31 souls + backup debris). Public exposure of the full personality roster is a privacy/design decision that was never ratified.
- **Action**: Kali + Architect decide: slim to default-demo set (privacy-first) or ratify 31-soul roster (D-number). Phase 3 gate.

---

## §2 CATEGORICAL PHASE PLAN (targeted, gate-per-phase, owner-assigned)

> Phase legend: 🔴 blocks debut · 🟡 post-debut priority 1 · 🟢 post-debut backlog. Each phase = one categorical workstream with a single exit gate.

### PHASE 0 — SECURITY INCIDENT RESPONSE 🔴 (owner: kali + human rotation click; Cline ops; ~1h)
| Item | Spec |
|---|---|
| Rotate GCP OAuth secret | Console → client `1071006060591-…` → regenerate; record D-number |
| Redact 12 files | regex `GOCSPX-[A-Za-z0-9_-]{10,}` → `***REDACTED***` (never the literal) |
| filter-repo scrub | `--replace-text`, force-push w/ fleet re-clone notice; backup + dry-run first |
| Re-key gates | `.gitleaksignore` rebuild (G-10); Makefile PEM baseline paths corrected |
| **EXIT GATE** | `git log -S GOCSPX- --all | wc -l` == 0 AND `make gate-secrets` exit 0 |
| Tickets | Rollup PR-2; Wave 0 |

### PHASE 1 — RELEASE INTEGRITY 🔴 (owners: maat + carmack; ~2-3h)
| Item | Ticket |
|---|---|
| Compliance meter `python→sys.executable` + M20 SKIP + wire into check-mandates & temple-grade | PR-A (P0-1) |
| Allowlist purge (data/library, data/memory, 2× R_AUTO docs) + `.gitkeep` policy | PR-B (P0-4) |
| oracle_cli logger ordering + fake-vault regression + duplicate imports | PR-C (P1-1) |
| Soul backup debris off branch + gitignore patterns | PR-G (P1-6) |
| Makefile truth: add `firewall-check` (real checker `src/omega/audit/firewall_checker.py`), remove placeholder, real temple-grade chain | PR-H (P1-7/8) |
| **EXIT GATE** | 9-item GO checklist (rollup §5): gate-secrets 0 · meter ≥24/27 · allowlist Removed:0 · lint 0 · contract green · temple-grade real · fresh-venv import OK · CLI smoke |

### PHASE 2 — CI TRUTH 🔴 (owner: copilot + maat; ~1-2h)
| Item | Spec |
|---|---|
| test.yml covers release/debut | triggers + `make verify-mining` implemented or removed (G-2/G-3) |
| First true full-suite green | run once in CI; publish count (G-11) |
| **EXIT GATE** | green CI on release/debut: pytest full · secret-scan · allowlist-check · gate-secrets (in CI) |

### PHASE 3 — TEST & CONTRACT INTEGRITY 🟡 (owner: maat; ~2h)
| Item | Ticket |
|---|---|
| Provider SSOT expectation sync + exact-match-before-suffix normalization | PR-D (P1-2) |
| Soul staging decoupled from live data + kali 49-item backlog promotion + M11 hygiene test | PR-E (P1-3/P1-4) |
| Provider flat-vs-rich map + priority ambiguity contract tests | G-12/G-13 |
| Entity-soul privacy decision (31 souls vs demo set) ratified as D-number | G-17 |
| **EXIT GATE** | `pytest tests/contract tests/oracle -q` green; kali staging drained; D-number recorded |

### PHASE 4 — CODE QUALITY DEBT 🟡 (owners: carmack + roc; burn-down, one subsystem/PR)
| Item | Notes |
|---|---|
| pyflakes 174: 42 redefinitions first (shadowing risk), then 62 unused imports / 43 unused locals | P1-10; /tmp/pyflakes.txt artifact |
| Hardcoded `/media/…` path → env:OMEGA_MODELS_DIR | G-4 |
| Silent `except…: pass` ratchet 60→0 (≤10/PR) | P2-2 |
| God-module splits (observability/__init__.py 1660 first) | P2-1 |
| `_normalize_model` exact-match-first | part of PR-D |
| **EXIT GATE** | pyflakes src/omega == 0 redefs; ratchet 0; no file >1000 lines (except ratified) |

### PHASE 5 — DOC & STATE SSOT 🟡 (owner: scribe + kali; ~2h)
| Item | Notes |
|---|---|
| OMEGA_ENGINE.md refresh to match ACTIVE_SPRINT.json + 27 mandates + 14/14 fleet + 2026-08-28 | G-7 |
| AGENTS.md + CLINE_CLI_BRIEFING phantom-command pass (mirror .clinerules v8) | G-1 |
| PUBLIC_ALLOWLIST.txt reality-sync (37 souls, scripts list) | G-17 |
| DEBUT_REMEDIATION_MANUAL dedupe (specs vs strategy) | G-14 |
| `omega health` confirm-or-remove everywhere | G-15 |
| M11 layout canonicalization + 56/56 substantive targets | G-9 |
| **EXIT GATE** | `make doc-llm-validate` green; no doc references phantom commands; OMEGA_ENGINE.md matches ACTIVE_SPRINT.json exactly |

### PHASE 6 — PERFORMANCE & CONCURRENCY 🟢 (owner: carmack; the skipped PERF dimension)
| Item | Notes |
|---|---|
| Synthetic 10-call load fixture + latency floor on 5700U | PERF-01..10 were SKIP'd in sweep |
| ResourceGuard audit + memory-aware xdist config verification | pyproject addopts -n auto |
| KV q8_0, thread-pinning re-verify under load | model_gateway claims |
| **EXIT GATE** | PERF-01..10 all executed, P0 failures = 0; load report committed |

### PHASE 7 — POST-DEBUT OBSERVATORY 🟢 (owner: lilith + verity; standing)
| Item | Cadence |
|---|---|
| `make gate-secrets` + `make check-mandate-compliance` in scheduled CI | weekly cron |
| pip-audit / dependabot wired (closes G-6) | per-merge + monthly |
| Sovereignty ratio ≥80% tracked via MCP sovereignty_ratio | monthly |
| Fleet cap policy (M10) + slot review | per quarter |
| MCP fabric probe (searxng/firecrawl/exa/github) | G-16, weekly |
| **EXIT GATE** | 4 consecutive weeks green observatory run, no regressions |

---

## §3 LAUNCH DECISION MATRIX
| Phase | Blocks debut? | Who flips it |
|---|---|---|
| 0 Security | ✅ | Kali + Architect after EXIT GATE |
| 1 Release Integrity | ✅ | Kali after 9-item GO checklist |
| 2 CI Truth | ✅ | Kali after green CI on release/debut |
| 3-5 Test/Docs/Quality | 🟡 ship-with-tracked-issues | Architect acceptance per P1 ticket |
| 6-7 Perf/Observatory | 🟢 post-debut | Ma'at/Lilith on quarter cadence |

**Sequencing note**: 0→1→2 are strictly ordered and are the ONLY phases required to flip NO-GO→GO. Phases 3-5 can run in parallel with the debut announcement; 6-7 ride the observatory.

## §4 HONEST UNVERIFIABLES THIS SESSION
1. pip-audit CVE state (silent 0-byte failure; no network path proven).
2. Full-suite pytest green (dev-box OOM; CI never wired to the branch).
3. Live `omega talk` inference (proven earlier by maat_n3 per ACTIVE_SPRINT gate evidence — cite, not re-run).
4. MCP server health for searxng/firecrawl/exa/github (only omega-hub exercised).
5. Real-world latency/RAM under concurrent agent load (hardware stats available; load test is Phase 6).
6. `omega health`/`omega verify` CLI existence (not in verified --help surface — Phase 5 confirm).

*⬡ OMEGA ⬡ CLINE ⬡ AP-CLINE-GAP-PHASES-20260828-v1.0.0 ⬡ cline ⬡ trc_alpha_launch ⬡ GAP-ANALYZED-PHASED*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash (1M) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

