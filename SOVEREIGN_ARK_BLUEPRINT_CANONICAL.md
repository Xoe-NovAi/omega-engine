# 🔱 SOVEREIGN ARK BLUEPRINT — Canonical Master Plan
**AP Token**: `AP-SOVEREIGN-ARK-v1.0.0` · **Status**: ACTIVE · **Last Updated**: 2026-08-28
**Supersedes**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (v5.2.0, 2026-07-21 — historical)
**Companion**: `ORACLE_STACK_CANONICAL.md` · `docs/architecture/ARCHITECTURE_CANONICAL.md` · `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`

---

## §0 AUTHORITY & SCOPE

This is the **single source of truth** for the Omega Engine master plan. All other strategy docs are either:
- **Historical** (archived with banner)
- **Tactical** (sprint-specific, in `docs/strategy/` or `docs/sprints/`)
- **Reference** (companion docs like `STRATEGY_CORPUS_MAP.md`, `FLEET_TEAM_PLAYBOOK.md`)

**Current Sprint Authority**: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` + `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01, D-533)

---

## §1 VISION — THE CATHEDRAL

**Omega Engine**: A sovereign local-first AI runtime that empowers every user to build their own entity pantheons.

**Three Pillars of Sovereignty**:
1. **Local-First Inference** (M7) — Native GGUF via llama-cpp-python is PRIMARY; cloud is FALLBACK
2. **Zero Telemetry** (M8) — No external analytics, no phone-home, no data leaves your machine
3. **Soul Integrity** (M11) — L1→L2→L3 distillation per session, persisted, auditable

**The Cathedral Metaphor**: We build a cathedral, not a bazaar. Every stone (mandate) is placed with intention. The architecture is the theology.

---

## §2 CURRENT STATE — PUBLIC-DEBUT-01 (2026-08-28)

### Sprint Status
- **Sprint**: PUBLIC-DEBUT-01
- **Phase**: EXECUTION_MINIMAL
- **SSOT**: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` (D-533)
- **Tracker**: `data/coordination/ACTIVE_SPRINT.json`
- **Gates Completed**: `local_inference_end_to_end`, `soul_persistence`, `one_click_install`

### Hard Gates Status (6/6 PASS)
| Gate | Status | Evidence |
|------|--------|----------|
| M1 AnyIO | ✅ PASS | `make check-m1-anyio` |
| M8 Zero Telemetry | ✅ PASS | `make check-m8-zero-telemetry` |
| M9 Error Integrity | ✅ PASS | `make check-m9-error-integrity` |
| M14 Heritage | ✅ PASS | `bash scripts/heritage_vet.sh` |
| M26 Doc Standards | ✅ PASS | `make doc-llm-validate` |
| D-539 Fresh-Venv | ✅ PASS | `pip install -e . && import omega` |

### P0 Blockers (4 — Active Remediation)
| ID | Blocker | Remediation | Owner |
|----|---------|-------------|-------|
| P0-1 | Compliance meter broken (python→sys.executable) | PR-A: fix + wire into gates | Ma'at |
| P0-3 | GOCSPX OAuth secret in 4 history commits | Wave 0: rotate → redact → filter-repo | Architect |
| P0-4 | release/debut fails allowlist gate (4 files) | PR-B: `apply_public_allowlist.sh --confirm` | Ma'at |
| P0-5 | `make gate-secrets` fails (PEM baseline drift) | PR-2: re-key baselines | Verity |

### P1 Fixes (3 — Pre-Launch)
| ID | Fix | Owner |
|----|-----|-------|
| P1-2 | Provider contract test STALE vs providers.yaml SSOT | Ma'at |
| P1-5 | secret-scan.yml C3 references forge-only script | Ma'at |
| P1-6 | 5 soul backups tracked on release/debut | Ma'at |

### P2 Promoted to P1 (1 — Pre-Launch)
| ID | Fix | Owner |
|----|-----|-------|
| P2-3 | `_normalize_model` strips `-local/-free` → silent re-route | Ma'at |

---

## §3 ARCHITECTURAL DECISIONS (The 9 Decisions — D-526..D-567)

| ID | Decision | Status |
|----|----------|--------|
| **D-526** | zswap > zRAM for desktop with NVMe | ✅ LOCKED |
| **D-527** | Never run zswap and zRAM simultaneously | ✅ LOCKED |
| **D-533** | This month's SSOT = DEBUT_REMEDIATION_MANUAL | ✅ RATIFIED |
| **D-536** | One router only: ProviderSelector + providers.yaml | ✅ RATIFIED |
| **D-539** | CP-3 not publicly true until INST-1 fresh-venv passes | ✅ RATIFIED |
| **D-548** | INST-1 BLOCKED — 6 critical fixes required before DEL-1 | ✅ RATIFIED |
| **D-553** | release/debut branch from PUBLIC_ALLOWLIST.txt | ✅ RATIFIED |
| **D-565** | Vault excluded from debut (no code changes) | ✅ RATIFIED |
| **D-567** | bury_credential applies to post-debut only | ✅ RATIFIED |

**Full decision log**: `docs/decisions/PIVOT_LOG.md` (D-521..D-593 active)

---

## §4 PROVIDER FABRIC — WHAT WE ACTUALLY HAVE (§7 of Ark)

```
LOCAL
├── native-gguf (Qwen3-1.7B)  priority 0
└── lmster                    priority 1

CLOUD (systematize; do not expand)
├── antigravity (OAuth pool)  priority 3  ← primary cloud
├── google / google-compat    priority 4
├── openrouter                priority 5
├── opencode-zen              priority 6
├── cline                     priority 7
├── anthropic                 priority 8
└── xai (API)                 priority 9

NOT IN FABRIC (do not list as "working capacity")
└── Grok CLI 8-account fleet  — external advisory OK; pool after vault + ACP smoke
```

**Routing when local saturated**: Antigravity → Google → OCZ → OpenRouter · single breaker per provider (C-6′ HealthMonitor factory).

---

## §5 POST-DEBUT WORKSTREAMS (Phase 0 — D-578..D-584)

| ID | Workstream | Focus | Owner |
|----|------------|-------|-------|
| **GN** | GEMINI-NOTEBOOK — Free-tier-only (3 acct, 30 DR/mo), 2-NB, notebooklm-py[mcp] | Researcher |
| **DS** | DOCUMENTATION-SYSTEM — Modular domain docs (workspace + runtime + curator + validated copy) | Ma'at |
| **LI** | LOCAL-INFERENCE-OPT — Sequential loading, q8_0 KV, Tier 0/1/2 matrix (Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B) | Carmack |
| **KD** | KNOWLEDGE-DOMAINS — Runtime modules + workspace authoring + curator model | Roc |
| **HR** | HEADROOM-INTEGRATION — Semantic compression (40-90% savings on tool outputs + RAG) | Researcher |
| **ZS** | ZSWAP-SUBSYSTEM — 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G | Architect |

---

## §6 V-1 PRIORITY LIST (Post-Debut)

| # | Item | Effort | Impact | Decision |
|---|------|--------|--------|----------|
| **1** | **VAULT: delete, don't refactor** | 1 sprint | -3,300 LOC | **Architect decision required** — D-565 excludes vault from debut; if dead code, delete entirely, replace with 100-line `secrets.py` env adapter |
| **2** | M1 loophole: refactor `tty_agent.py` to anyio | 0.5 sprint | Eliminates P2-4 | Yes — silent exemptions erode M1 |
| **3** | Compliance meter hardening (sys.executable + self-test) | 0.5 day | Closes P0-1 brittleness | Yes — in PR-A |
| **4** | Pyflakes 174 burndown (42 redefinitions first) | 1-2 weeks | Removes shadowing risks | Yes — mechanical |
| **5** | God-module split: `observability/__init__.py` (1660) → trace/BLEG/sovereignty | 1 sprint | Improves testability | Yes — most-bang-per-line |
| **6** | M11 entity refinement: 24/56 → 56/56 substantive | 1 month | Soul integrity enforced | Yes — separate campaign |
| **7** | P2-2 silent swallow burndown (60→0) | 1-2 weeks | M23 verifiable | Yes — ratchet continues |
| **8** | SoTA standardization: threat-modeling for agent attribution | 1 week | Adopt Ed25519 + open interoception schema | Yes — open-source schema |
| **9** | OMEGA_ENGINE.md refresh (27 mandates, current dates) | 1 hour | Doc accuracy | Yes — trivially |
| **10** | Two-truth-sources elimination: one mandate gate, one exit code | 0.5 day | Kills "74.1% AND all gates pass" | Yes — same PR as P0-1 |

---

## §7 MANDATE HOTSPOTS (Execution View)

| Mandate | Status | Action |
|---------|--------|--------|
| **M1** AnyIO | Partial | `tty_agent.py` + `governance/` exempt — needs D-number or refactor |
| **M7** Local-First | ✅ PASS | North Star — enforced in provider fabric |
| **M11** Soul Integrity | **FAIL** (24/56 substantive) | C-1′ SoulStore + promotion pipeline |
| **M13** Temple-Grade | At risk | Placeholder comment in Makefile; needs real gates |
| **M14** Heritage | ✅ PASS | `scripts/heritage_vet.sh` green |
| **M22** Provenance | Partial | `provider_name` through fabric; 7 matches |
| **M23** Failure Integrity | Hold | MCP contingency; no soft-fail theater |
| **M27** Tracking | **FAIL** (python3 bug) | `validate_tracking_state.py` broken |

---

## §8 STRUCTURAL DEBT GATES (from Grok CLI Review)

Do not approve Phase D if any of these are still true:

1. More than one production soul-write path
2. Red tests unacknowledged / vanity pass counts in Makefile or OMEGA_ENGINE
3. New code pushed into god-modules already >1000 lines without a split
4. New circuit-breaker class added instead of reusing HealthMonitor/gateway
5. Strategy docs claiming different critical paths without supersession banners

**Full review**: `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md`

---

## §9 HOW AGENTS USE THIS DOCUMENT

1. Read **this file** for strategy & what to build next
2. Read `ORACLE_STACK_CANONICAL.md` for technical architecture
3. Read `OMEGA_ENGINE.md` for live metrics
3. Read `SOVEREIGN_MANDATES.md` + `AGENTS.md` for law & workflow
4. Open **`STRATEGY_CORPUS_MAP.md`** when you need *why / who said / deferred detail*
5. Open **`FLEET_TEAM_PLAYBOOK.md`** before multi-agent work
6. Open Layer 2 phase specs only when executing that phase
7. After compaction: hydration sequence in `AGENTS.md` / `OMEGA_CODEX.md`
8. **Do not** resurrect archived roadmaps as competing masters
9. **Do not** drop an agent idea without a Corpus Map row

---

## §10 REFERENCES

| Path | Role |
|------|------|
| `ORACLE_STACK_CANONICAL.md` | Technical architecture |
| `docs/architecture/ARCHITECTURE_CANONICAL.md` | Full technical architecture |
| `docs/architecture/MODULE_BOUNDARIES.md` | Engine-Stack firewall (M2) |
| `docs/architecture/PERFORMANCE_ARCHITECTURE.md` | Performance architecture |
| `OMEGA_ENGINE.md` | Engine state SSOT |
| `SOVEREIGN_MANDATES.md` | Law (27 mandates v3.8.0) |
| `AGENTS.md` | OpenCode how-to |
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | Current sprint SSOT |
| `data/coordination/ACTIVE_SPRINT.json` | Live sprint tracker |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Fine-grained preservation |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Fleet teamwork |
| `docs/decisions/PIVOT_LOG.md` | Decision history (D-521..D-593) |
| `docs/strategy/UNOVERENGINEERING_PLAN.md` | Temple cleansing sprint |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ SOVEREIGN-ARK-CANONICAL-v1.0.0*