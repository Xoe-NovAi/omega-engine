<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔭 THREE-LENS RECON SYNTHESIS — 2026-08-26
**AP Token**: `AP-RECON-SYNTH-v1.0` · ⬡ OMEGA ⬡ KALI ⬡ Consultant synthesis of 3 read-only recon dispatches
**Dispatches**: explore `ses_fc471f913ffe5fsxacVK3ILu9w` (code) · verity `ses_fc471cca4ffeTBdCQWQuKTMjvA` (docs/compliance) · jem `ses_fc4719bd2ffesoXAfGtl57djwN` (machinery). Full raw reports in session task results.

## VERDICT
The engine's SUBSTANCE is real; its CERTIFICATION LAYER lies in exactly the ways the Zero-Trust Doctrine was written to kill. Two agents independently found the flagship gate red on a regex bug; the codex teaches a superseded constitution; the declared defense-in-depth is not installed.

## CRITICAL — certification-layer lies (fix before any CI wiring)
| # | Finding | Evidence | Cross-val |
|---|---|---|---|
| C1 | `make temple-grade` RED (exit 2): M8 regex `from (segment\|...)` unanchored, matches COMMENT "Build header from segments" @ ics.py:197 | Makefile:293 + ics.py:197 | verity+jem |
| C2 | Codex delivers stale ground truth: embedded MANDATES card v3.7.0/25 laws vs actual v3.8.0/27; "Next Phase Γ" vs actual PUBLIC-DEBUT-01/EXECUTION_MINIMAL; phantom MIAP module (no src/omega/coordination/miap.py); sqlite_policy path stale (infra/, not persistence/); roster 12 vs 13 files. Freshness timestamp masks source-card rot | OMEGA_CODEX §3/§4 vs SOVEREIGN_MANDATES.md:2-5, ACTIVE_SPRINT.json | explore+verity |
| C3 | Pre-commit framework DORMANT: .pre-commit-config.yaml has 20 hooks (detect-secrets, F821, M27 Iron Gate) but installed .git/hooks/pre-commit is a 6-line soul-check bash script. Nobody ran `pre-commit install`. Defense-in-depth decorative | .git/hooks/pre-commit vs .pre-commit-config.yaml | jem |
| C4 | AGENTS.md is a GHOST: cited by constitution + hundreds of files, absent from disk AND git history. infra_inventory flags GHOST | inventory baseline; SPEC-E premise confirmed | all three |

## STRUCTURAL
| # | Finding | Evidence |
|---|---|---|
| S1 | Soul single-writer doctrine UNACHIEVED: ≥4 divergent in-package writers + 1 script writer; only SoulStore-routed one is DORMANT (zero callers); observability learn() NON-ATOMIC (observability/__init__.py:583-641); M11 functionally INERT on hot path (_track_soul_evolution = event stub, oracle.py:1362-1385) | oracle.py, entity_registry.py:87-104, entity_workspace.py:528-609 |
| S2 | 11 god-modules >1000 LOC; 4 of top 5 are hot-path (model_gateway 1582, oracle 1451, providers 1303, memory_store 1224); oracle pkg = 32% of core | structural debt gate #3 breached |
| S3 | M25 streaming = ONLY unenforced mandate: config complies (all 8 cloud providers have streaming sections), zero mechanical gate exists | providers.yaml:211-358; Makefile grep |
| S4 | Gap-pointer rot: legacy plan-keys dangling in 5/8 sampled GAP_REGISTRY entries; DS-1 report pointer HARD-BROKEN (DOMAIN_DOCUMENTATION_SYSTEM.md nowhere in repo); R15 dangling in TASK_REGISTRY; ACTIVE_SPRINT references ZERO R-IDs → relational gate vacuous | verity+jem probes |
| S5 | SPEC-A..E all GATE-REFERENCED, zero GATE-SHIPPED (honest plans, no mechanisms yet); live proof: BLOCKER-B status="resolved" passes validator green today | docs/specs/team_infra/ |

## HYGIENE
- M1 violation: tty_agent.py asyncio-native throughout (:14,:201,:244,:724,:738) — 1 file of 269
- omega.yaml duplicate `sovereignty_gate` :51+:73 persists (byte-identical today, silent last-wins)
- google/google-compat PRIORITY TIE at 4 (providers.yaml:86,133)
- Bare python/python3 in framework entries + Makefile doc targets (M24 hazards)
- Dead surface: write_soul_file/update_soul zero callers; ExperimentCircuitBreaker dormant clone (sandbox.py:617); fallback_resolver dead config (providers.yaml:19-60); empty gateway//orchestrator/ pkgs; stale cloud-first docstring (model_gateway.py:717 — comment lies, code correct)
- Scribe residue: WAD configs (arcana_novai entities.yaml:1977, spheres.yaml:140/159, _omega_default entities.yaml:880/950 — NOTE: inside Architect's pending 214-line diff), m23_baseline.txt:71 stale hmc row
- 27 tracking warnings: 14 inverted clocks, 2 unresolved superseded_by, 11 failed-without-subtask

## VERIFIED REAL (the good news)
- Local-first enforced at SIX independent points (config order, fabric sort, selector score, PII penalty, budget gate, cloud lock-timeout inversion)
- Hardening chain executes in strict order inside generate() (:1181-1261): OOM 3-signal → admission semaphore → resource guard → breaker precheck → 429 guard → rate limiter
- M22 provenance end-to-end (GenerateResult.provider_name → MetricsDB)
- Heritage vetting genuinely passes (79 scope declarations); trackers minutes-fresh; codex honestly admits M5/M11 FAIL; velocity 166 commits/10d, disciplined conventional prefixes

## RECOMMENDED FIX ORDER (evidence-ranked)
1. **C1**: anchor M8 regex `^\s*(from\|import)\s+(segment\|posthog\|datadog\|amplitude\|mixpanel)\b` → temple-grade green (one line)
2. **C2**: regenerate codex source cards from current mandates/sprint/roster
3. **C3**: decide framework fate — repoint bare python→.venv/bin/python then `pre-commit install`, or delete config (no zombie gates)
4. **C4**: AGENTS.md restore-or-dewire (SPEC-E already sequences validator-first)
5. **S5**: ship SPEC-A WI-2 so blockers[] vocabulary stops passing green
