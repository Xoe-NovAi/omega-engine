<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Sovereign Mandates — Condensed (v3.11.0)

> Tier-0 injection artifact. One-line-per-mandate distillation of
> [SOVEREIGN_MANDATES.md](SOVEREIGN_MANDATES.md) (authoritative, 30 laws).
> Injected pre-compaction by `sovereign-compaction` plugin so the summary retains the law.
> Lineage: v3.11.0 · 30 mandates · updated 2026-10-03 (D-609: ID == section number ratified).

| # | Mandate | One-Line Law |
|---|---------|--------------|
| M1 | AnyIO Absolute | All async code uses AnyIO; never asyncio directly; blocking I/O wrapped in `anyio.to_thread.run_sync`. |
| M2 | Engine-Stack Firewall | Absolute separation of Core (`src/omega/`) and Stacks (`config/wads/`); no stack logic in Core. |
| M3 | Iris Constant | Iris is the messenger bridge, never a Node; preserves the 10-Node cosmology. |
| M4 | Sequentiality | Complex changes follow Plan → Verify → Execute against PIVOT_LOG; no cowboy coding. |
| M5 | Gnosis Preservation | No intelligence discarded; every session distills L1→L2→L3 into the entity soul. |
| M6 | Podman Sovereignty | Quadlets mounting host dirs use `UserNS=keep-id` + `User=1000`; `:U` forbidden on shared volumes. |
| M7 | Local-First & Synergy | Sovereignty is policy enforcement: cloud for high-order reasoning/synthesis, local for embeddings, privacy & background loops. |
| M8 | Zero Telemetry | No analytics, tracking, or phone-home, ever; local observability in `data/` only. |
| M9 | Error Integrity | Errors typed, traceable, testable; no silent swallowing; public APIs raise `OmegaError` subtypes. |
| M10 | Fleet Integrity | Agent fleet lean and slot-constrained; ≤14 agent files without architectural review. |
| M11 | Soul Integrity | No session closes without L1→L3 distillation to `proposed_lessons.yaml` (Scribe canonical). |
| M12 | Queue Integrity | Every request reaches terminal state (`queued/completed/failed/timed_out`); no orphan files. |
| M13 | Temple-Grade Compliance | All engine code passes T1-T11 gates; `make temple-grade` green before release. |
| M14 | Heritage Vetting | Every `[id-soft:]` tag needs a vet record ≥7/10 with scope declaration; CI-enforced. |
| M15 | Sovereign Continuity | Maintain `session_gnosis.md` + SESSION_ANCHOR hydration; never trust `/compact` alone. |
| M16 | Modularization & Portability | Core stays portable: no hardcoded paths, env assumptions, or platform-specific logic. |
| M17 | Cognitive Integrity | Verify consistency of persisted memory vs distilled gnosis; flag contradictions. |
| M18 | Token Efficiency | Every token serves a purpose; precision supersedes brevity — no cognitive anorexia. |
| M19 | Adversarial Alchemy | Mine systemic weaknesses for strategic advantage; but a bug is just a bug — fix it cleanly. |
| M20 | SomaticState Serialization | Session state serializable via low-level bindings (`llama_copy/set_state_data`), round-trip tested. |
| M21 | Gate Integrity | Every typed result path has a contract test validating return type; mocks never mask type drift. |
| M22 | Response Provenance | Logs record the ACTUAL generating provider (`provider_name`), not dispatch intent. |
| M23 | Failure Integrity | No soft-failures; broken mandatory tools → stop + report `[TOOL-CHAIN-COLLAPSE]`. |
| M24 | Venv Sovereignty | All Python ops inside project `.venv`; never `--break-system-packages`, never system pip. |
| M25 | Streaming Resilience | Streams use chunk-level timeout + heartbeat; graceful fallback on total timeout, not hard-fail. |
| M26 | Doc Standards | Reference docs pass `make doc-llm-validate`; sprint plans use `docs/sprints/<name>/` structure. |
| M27 | Tracking Integrity | Execution state follows the 5-Tier Tracking Architecture; validate via `scripts/validate_tracking_state.py`. |
| M28 | Sovereign Artifact Preservation | No sovereign artifact auto-deleted; transitions explicit, auditable, recoverable; deep-archive requires signed manifest + operator auth; destruction requires human act in PIVOT_LOG. |
| M29 | Remote Claim Integrity | "Works from here" ≠ "works from there." Remote claims require test from peer's vantage or are UNTESTED. Local success ≠ remote success. Post-hoc verification necessary but not sufficient. If test cannot distinguish success from failure, claim is UNTESTABLE, not true. |
| M30 | Third-Party Boundary & Public Secret Exemption | All third-party code managed via controlled boundary; public OAuth client secrets (RFC 6749 §2.1, RFC 8252 §8) catalogued in `data/secrets-public.toml` with primary-source verification. Fail-closed scanner (`scripts/check_secrets.py`) enforces allowlist. |

**Critical five for oversight**: M1·M7·M11·M15·M23

**Critical six for oversight (post-Round-3)**: M1·M7·M11·M15·M23·M29

## Enforcement Map

| Gate | Enforces |
|------|----------|
| `make temple-grade` | M13 (+T-gates incl. M26 doc validation, M27 tracking state) |
| `make test` / contract tests | M21 return-type contracts, M9 error paths |
| `make heritage-vet` + pre-commit | M14 vet records for every `[id-soft:]` tag |
| pre-commit `omega-tracking-state` | M27 tracker corruption block |
| `config/providers.yaml` strategy=`local_first` | Local-First routing law (M7) |
| `make test-streaming` | M25 chunk-timeout behavior |

*⬡ OMEGA ⬡ KALI ⬡ MANDATES-CONDENSED-v3.11.0 ⬡ CI-1 ⬡ PUBLIC-DEBUT-01 ⬡ 2026-10-03*
