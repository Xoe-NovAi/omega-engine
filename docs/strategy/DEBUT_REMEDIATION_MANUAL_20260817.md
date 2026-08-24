---
schema_version: "1.0"
document_type: "guide"
document_id: "debut-remediation-manual-20260817"
title: "Omega Engine — Debut Readiness Briefing & Remediations Manual"
status: "ACTIVE"
version: "1.0.0"
date: "2026-08-17"
owner: "kali"
author: "grok_cli"
tags: ["debut", "deletion", "publication", "install", "routing", "vault", "llm-friendly"]
priority: "P0"
depends_on: ["P0-1 key rotation"]
blocks: ["public debut announcement", "Phase 2 lint campaign", "vault wiring", "Qdrant migration"]
acceptance_gates:
  - "P0-1 keys rotated then history scrubbed"
  - "Fresh clone pip-installs without warp-proxy-pool"
  - "omega talk hello works with only native+cli extras"
  - "One router on the talk path"
  - "OMEGA_ENGINE.md matches ACTIVE_SPRINT.json"
cross_references:
  - "data/coordination/ACTIVE_SPRINT.json"
  - "data/coordination/HMC_COLLABORATION_HUB.md"
  - "docs/strategy/UNOVERENGINEERING_PLAN.md"
  - "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md"
  - "docs/strategy/STRATEGY_CORPUS_MAP.md"
  - "docs/strategy/TEST_UX_CARMACK_PLAN.md"
llm_metadata:
  token_budget: 12000
  chunk_strategy: "section_per_ticket"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Omega Engine — Debut Readiness Briefing & Remediations Manual
**AP Token**: `AP-DEBUT-REMEDIATION-20260817-v1.0.0`
⬡ OMEGA ⬡ GROK_CLI ⬡ grok-4.6 ⬡ opencode ⬡ trc_debut_remediation ⬡ ACTIVE

**Date**: 2026-08-17
**Purpose**: Single execution brief for the fleet. Why the debut is not ready, what to delete, what to keep, and the exact ticket order.
**Tags**: debut, deletion, publication, install-honesty, one-router
**Cross-references**: `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md`, `UNOVERENGINEERING_PLAN.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `STRATEGY_CORPUS_MAP.md`, `TEST_UX_CARMACK_PLAN.md`
**Supersedes (for THIS MONTH's work only)**: Ark §4 priority stack, Hub “Phase 2 lint next”, UO §2 library-swap Phase 1, Corpus Map ACTIVE flags for G-1/W-1/Qdrant/Instruction Router
**Does not supersede**: `SOVEREIGN_MANDATES.md` (law), `TEST_UX_CARMACK_PLAN.md` (test UX)

---

## 0. Answer first — do this order

```
P0-1   Architect rotates leaked keys, THEN Roc scrubs git history
PUB-1  Publication allowlist (what GitHub is)
INST-1 Install honesty (stranger can pip install + omega talk)
DEL-1  Delete dead modules, then collapse to one router / one admission
DOC-1  Stamp strategy docs so agents stop rebuilding 2025
P2     Lint ONLY the files that survived
P3/P4  CI + debut polish
```

**Do not** start Phase 2 lint, vault wiring, Qdrant, SDP implementation, Instruction Router, Keyblind/Authy/Agent Vault, or WARP.

**Do not** `git add -A`. Path-stage every commit.

**Do not** interleave `git filter-repo` with a 200-file deletion PR. Scrub first.

---

## 1. How agents must use this document

| Role | What to do |
|------|------------|
| Every agent, session start | Read §0 + §2 + the ticket you own in §5. Do not start work listed in §4. |
| Kali | Ratify Hub `NEXT_ACTION` against this file. Block any ticket not in §5. |
| Ma'at / N3 | Own INST-1 and DEL-1 code. |
| Roc | Own P0-1b/d scrub + DEL-1 week-1 deletes (no replacements). |
| Verity | Own P0-1c gitleaks, INST-1 clone verification, DOC-1 stamp review. |
| Lilith / N7 | Soul path only if DEL-1 touches ContextBuilder / RecallStore. |
| Architect (Node 0) | P0-1a key rotation. Confirm PUB-1 allowlist. |

**Status vocab (M27, mandatory):** `backlog | ready | in_progress | blocked | completed | superseded`.

**Conflict rule for this month:**

1. Law → `SOVEREIGN_MANDATES.md`
2. **This month's work** → this file + `ACTIVE_SPRINT.json`
3. Live pointer → Hub `NEXT_ACTION`
4. Long-horizon vision → Ark (read-only unless Architect reopens)
5. Ideas graveyard → Corpus Map (`PARKED` / `ARCHIVE` only)

If Ark §4, Corpus Map, or UO Phase 1 disagree with this file, **this file wins until Kali marks it `superseded`.**

---

## 2. Briefing — what is true as of 2026-08-17

### 2.1 Verdict

The three-item critical path (local `omega talk`, soul persist, installer) can be demoed **on this machine**. The GitHub repo is not a product. It is a personal forge (4,506 tracked files, ~82k LOC in `src/omega`) with overlapping control planes, a stale SSOT, and leaked keys on `origin/main`.

Do not announce “the Omega Engine” as this tree. Announce a **narrow demo** only after P0-1 + INST-1.

### 2.2 Measured facts (re-probe before treating as stale)

| Fact | Evidence |
|------|----------|
| Tracked files | `git ls-files \| wc -l` → 4506 |
| `src/omega` Python | ~259 files, ~81,977 lines |
| Hub live Python | ~6,786 lines; `mcp_servers/omega_hub/hub_tools/tools.py` = 3649 |
| Strategy markdown | 123 files under `docs/strategy/` |
| Tracked research + archive | 585 + 464 |
| Tracked entity files | 1072 (`john_carmack` 473, `roc_racoon` 259) |
| Working tree weight | ~4.7 GB (mostly untracked `third-party/`, `data/`, `opencode-antigravity-auth/`) |
| `warp-proxy-pool` | Hard dep in `pyproject.toml`. **Not on PyPI.** Editable install from `~/Documents/Xoe-NovAi/warp-proxy-pool`. Fresh clone install **fails**. |
| README `make setup` / `make model-download` | **Targets do not exist** |
| README badge | Still claims 1315 passing |
| Version split | `pyproject.toml` = 1.2.0; `src/omega/__init__.py` = 1.0.0-alpha |
| `install.sh` | `pip install -e ".[all]"` pulls native + cli + **dev** + qdrant + redis + youtube + warp |
| Talk import | `omega.cli.oracle_cli:main` → `from omega.oracle import Oracle` → `Oracle.__init__` constructs ~20 subsystems |
| MemoryStore | Always constructs `RedisStorageProvider(password="omega")` unless `OMEGA_ENV=test` |
| Keys on `origin/main` | `docs/guides/PROVIDER_FREE_TIER_GUIDE.md` (`csk-`/`sk-`); `docs/archive/stale/migrate_keys_full.py`; commits `df174496`, `13351f9d` |
| Routers | `SemanticRouter` (entity) + `TriageRouter` (model) + `ProviderSelector` (backend) + unwired `RoutingTable` (`eval` of YAML) + per-turn `RAGRouter` |
| Vault | `VaultCore.bury_credential` exists. CLI still calls `store_credential`. Gateway dumps `.env` into `os.environ`. Vault is a sidecar, not the secret path. |
| `OMEGA_ENGINE.md` | Stale vs sprint (UNOVERENGINEER-01 / 25 mandates vs PUBLIC-DEBUT-01 / 27 mandates) |

### 2.3 What already works (do not rebuild)

- Native-gguf `omega talk` on this host (CP-1)
- Agents write L1→L2→L3 to `proposed_lessons.yaml` (CP-2). Regex distillation is **scrapped**.
- `SoulStore` atomic writer (tempfile → fsync → replace → parent fsync → flock → `.bak`)
- `OOMProtector` three-signal fusion
- `HealthMonitor.get_breaker()` as the canonical breaker factory
- `SQLiteVecAdapter` + FTS5 + RRF hybrid search
- Hivemind awareness / handoff (feature-freeze; bug fixes only)
- Dual-artifact **process** (executor reads one comment-free plan) — human protocol, not an engine ticket
- `TEST_UX_CARMACK_PLAN.md` — 50-line Makefile, 2 test tiers

### 2.4 Code-judo thesis

The engine already has the debut pieces. It does not have **one owner per decision**. A query can pass RAGRouter → Iris → SemanticRouter → TriageRouter → ProviderSelector → Gateway fallback → optional RoutingTable. That is five historical answers left in the path.

**Publication** is a separate cut from **runtime**. Deleting routers inside an unfiltered 4,506-file public repo still debuts the forge.

---

## 3. Two boundaries

### 3.1 PUB-1 — What GitHub is

Public `omega-engine` is an **allowlist**, not “gitignore harder.”

**Allow on the public surface**

- `src/omega/` after DEL-1
- Tests that exercise talk / summon / soul / sqlite-vec / firewall import-path
- `config/models.yaml`, `config/providers.yaml` (local-first chain), `config/omega.yaml`, `config/wads/_omega_default/`
- `scripts/install.sh` installing `.[native,cli]` only
- `README.md`, `LICENSE`, slim mandates, `CONTRIBUTING.md`
- `.github/workflows` with unit tests + gitleaks

**Forge (this machine, or private `omega-forge`)**

- `docs/strategy/` (except this file + mandates pointers), `docs/research/`, `docs/archive/`
- `data/entities/*` workspaces except one `default` soul
- `data/coordination/` runtime dumps, `data/handoff/`, `data/autonomous/`, `data/training/`
- YouTube worker, vault experiments, WARP, `third-party/`, `opencode-antigravity-auth/`

Preferred mechanic: branch or export `release/debut` from the allowlist. In-place `git rm` of 2,000 docs on `main` the same week as filter-repo will fail.

### 3.2 DEL-1 — What `omega talk` loads

Target call graph after week 2:

```
intent (talk | summon)
  → entity (registry keyword OR one embed, not both stacked)
  → model+provider (ProviderSelector over config/providers.yaml local-first list)
  → generate
  → record (optional)
```

One admission (`ResourceGuard` + one `OOMProtector`). One breaker factory (`HealthMonitor.get_breaker()`).

---

## 4. Forbidden until this manual is `superseded`

| Item | Why forbidden | Where it still pretends to be next |
|------|---------------|-------------------------------------|
| Phase 2 lint of 11,400 flake8 hits | Lints dead code; delete first | Hub `NEXT_ACTION`, `ACTIVE_SPRINT` P2 |
| Wire VaultCore into ModelGateway | Sidecar is unused and CLI-broken | Ark V-1, sprint notes |
| Replace vault with Keyblind + Authy + Agent Vault | Five runtimes to delete an unused sidecar | UO §2.6 |
| `RoutingTable` on the live path | Unwired `eval()` prototype | `src/omega/routing/table.py` |
| `ModelAwareInstructionRouter` | Fifth router | `POST_PR_ROSTER.md` item #1 |
| Qdrant migration / 6G container | Contradicts sqlite-vec SSOT; OOM on 8G UMA | `RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md` |
| JIT Adaptive + Graph + SQL RAG | Another routing pile on HybridSearch | JIT RAG briefs 2026-08-16 |
| Implement SDP gauge / pool_tracker / RHP tools | Human protocol, not engine work | `SDP_*.md` CANONICAL |
| Autodidactic CI / synaptic sync / shadow router | Horizon; cheats tests; merges bad lessons | `COGNITIVE_SOVEREIGNTY_EVOLUTION.md` §7 |
| G-1 / W-1 as P0 engine work | Ops / billing; Laguna already replaced Gemma as workhorse | Ark §4, Corpus Map |
| `git add -A` | Recommits secrets, entity DBs, screenshots | Agent habit |
| New `make check-*` gates | Existing gates already pass falsely | UO Phase 5 |

**Corpus Map rule 2 is inverted for this campaign:**

> An idea without a living ticket in `ACTIVE_SPRINT.json` is dead. `PARKED` means do not implement. `ARCHIVE` means do not read unless mining history.

---

## 5. Ticket sequence (execute in order)

### P0-1 — Live key incident
**Status to set:** `in_progress` — PARTIAL (blocked on Architect for 1a rotation confirm; pending the SECURITY_AUDIT residual below)
**Owners:** Architect (1a) → Roc (1b, 1d) → Ma'at/Verity (1c)

| ID | Action | Acceptance |
|----|--------|------------|
| P0-1a | Rotate every key in `PROVIDER_FREE_TIER_GUIDE.md` and `docs/archive/stale/migrate_keys_full.py` at the provider consoles (Cerebras, SiliconFlow, any OpenAI-style key). | ✓ **DONE 2026-08-17** — repo was private; 3 named files scrubbed from all reachable history via `git filter-repo` (migrate_keys_full.py, PROVIDER_FREE_TIER_GUIDE.md, test_failure_registry.py; branches main + release/initial-v1 + sprint/*). |
| P0-1b | `git filter-repo` (or equivalent) on **all branches** for those files and any other hits from 1d. | ⚠️ **PARTIAL.** 3 named files are gone from all reachable history. **RESIDUAL: `docs/security/SECURITY_AUDIT_2026_05_19.md` at ancestor commit `0c40b108` still carries 3 real-format keys (sk-/csk-/sk-P) under "Revoke current key" and is reachable from HEAD.** Confirm those 3 are revoked/rotated, then one more filter-repo pass for that file + `git gc --prune=now` + prune stale `refs/cline/checkpoints`. `git log -S 'csk-' --all` is NOT clean until then. |
| P0-1c | Add gitleaks or trufflehog to pre-commit **and** CI. | `backlog` — not yet wired. A planted `sk-` fixture in a non-allowlisted path must fail CI. |
| P0-1d | Full sweep: `sk-`, `csk-`, `AIza`, `ghp_`, `xai-`, `age-secret-key`. | ⚠️ **PARTIAL.** Working tree is CLEAN of real secrets (only `ghp_placeholder` literals + URL/prose false positives). Residual = the SECURITY_AUDIT blob in 1b above. |

**Files:** `docs/guides/PROVIDER_FREE_TIER_GUIDE.md`, `docs/archive/stale/migrate_keys_full.py`, **`docs/security/SECURITY_AUDIT_2026_05_19.md` (residual)**, `.pre-commit-config.yaml`, `.github/workflows/*`

---

### PUB-1 — Publication allowlist
**Depends on:** P0-1b complete (history rewrite first)
**Owner:** Kali + Architect
**Status to set:** `ready` after P0-1b

**Do**

1. Write `docs/strategy/PUBLIC_ALLOWLIST.txt` (one path pattern per line). Start from §3.1.
2. Prefer creating `release/debut` from the allowlist over mass-deleting `main`.
3. If staying on one repo: `git rm --cached` forge paths; do not delete Architect’s local copies.

**Do not** delete `data/entities/*/soul.yaml` for the default demo entity. Do not commit `config/model_registry/index.sqlite`.

**Acceptance**

- A clone of the public ref has no `docs/research/` corpus, no agent workspace dumps, no handoff JSON.
- `git ls-files data/entities` is a short default-soul set, not 1,072 files.

---

### INST-1 — Install honesty
**Depends on:** nothing except not conflicting with P0-1b rewrite
**Owner:** Ma'at / N3
**Can start in parallel with P0-1a** (code-only; no history rewrite)

| Step | Change | File |
|------|--------|------|
| 1 | Remove `warp-proxy-pool` from `[project].dependencies`. Optional extra `[warp]`. Guard Oracle/Gateway import with try/except. | `pyproject.toml`, `src/omega/oracle/oracle.py`, `src/omega/oracle/model_gateway.py` |
| 2 | Move `qdrant-client`, `redis`, `youtube-transcript-api`, `yt-dlp` to extras. | `pyproject.toml` |
| 3 | `install.sh` uses `pip install -e ".[native,cli]"` — **not** `.[all]`. | `scripts/install.sh` |
| 4 | Add `make setup` that matches install.sh **or** delete those lines from README. | `Makefile`, `README.md` |
| 5 | MemoryStore: do **not** construct Redis unless `OMEGA_REDIS_HOST` is set. Delete default password `"omega"`. | `src/omega/memory_store.py`, `src/omega/memory/providers.py` |
| 6 | Stop `ModelGateway._load_sovereign_secrets` dumping `.env` into `os.environ`. Load env at process edge (`oracle_cli` / install) or document required env vars. | `src/omega/oracle/model_gateway.py` |
| 7 | Align version: `src/omega/__init__.py` == `pyproject.toml`. | both |
| 8 | README: remove 1315 badge; one install path; no Sekhmet/Brigid unless `_omega_default` actually ships them. | `README.md` |

**Acceptance**

```bash
# On a machine WITHOUT ~/Documents/Xoe-NovAi/warp-proxy-pool and WITHOUT Redis:
python3 -m venv /tmp/omega-inst && source /tmp/omega-inst/bin/activate
pip install -e ".[native,cli]"
omega talk "hello"    # native-gguf, IS_CLOUD=False, exit 0
```

If that fails, INST-1 is not done. Do not mark CP-3 complete in public docs until this passes.

**Execution note (2026-08-24, N2 / council DAG)**: Steps 2+6 landed as ONE fused commit
(`feat(n2)`) per H_KALI_UNIFIED_VERDICT — extras split fused with redis.asyncio lazy-guards
at `src/omega/memory/providers.py`, `src/omega/ingestion/worker.py`,
`src/omega/workers/youtube_worker.py` (pattern: `governance/budget_guard.py:23-29`).
Extras: `[memory]` (redis), `[vectors]` (qdrant-client), `[youtube]` (transcript-api + yt-dlp + redis);
core install is `.[native,cli]`. `.env` loading lives solely at the CLI process edge
(`oracle_cli.load_dotenv()`); `ModelGateway._load_sovereign_secrets` deleted.

---

### DEL-1 — Deletion campaign
**Depends on:** INST-1 green enough that talk still works after each delete
**Owner:** Roc (week 1) + Ma'at (week 2)
**Rule:** every delete ships with its tests removed or rewritten. No “leave the test, skip the import.”

#### Week 1 — delete without replacements

| Path | Why | Tests to retire/update |
|------|-----|------------------------|
| `src/omega/routing/table.py` | No callers; `eval()` | none (self-only) |
| `config/routing_table.yaml` | Orphan config | — |
| `src/omega/coordination/miap.py` | Tests only; MIAP cancelled | `tests/test_miap.py` |
| `src/omega/oracle/pool_tracker.py` | Self-only SDP leftover | any pool_tracker tests |
| `src/omega/oracle/pool_state.py` | Self-only | — |
| `src/omega/oracle/search_circuit_breaker.py` | Deprecated; redirect leftover caller to `HealthMonitor.get_breaker()` | search-breaker tests |
| `QdrantAdapter` class in `src/omega/memory/vector_adapters.py` | Leftover impl | `tests/test_qdrant_*.py` that only mock Qdrant |
| Pantheon name regexes in `src/omega/audit/firewall_checker.py` | Forbids and allowlists the same names | keep import-path rules only |
| `record_first_breath` call in `Oracle._route_by_domain` | Astrology on every routed turn | astrology tests if any |
| `omega vault` default CLI registration | CLI calls missing `store_credential` | hide behind extra or delete subcommand |
| `src/omega/integrations/fleet_orchestrator.py` from default exports | Unused control plane | — |

Also stop **constructing** in `Oracle.__init__` (lazy or delete): DPO recorder, compaction harvester, iterative researcher, WARP pool, A2A bridge, audience calibrator (keep function if summon needs it, do not allocate at import).

**Week 1 acceptance:** `omega talk "hello"` still local; `rg RoutingTable src` empty; `rg miap src/omega` empty.

#### Week 2 — one control plane (single PR)

This is a **rewrite of the talk path**, not a drive-by `rm`.

1. Keep `ProviderSelector` + `config/providers.yaml` local-first list.
2. Delete `TriageRouter` **and** `SemanticRouter` in the **same** change as `Oracle._select_model` / `Oracle._route_by_domain`.
3. Entity pick: `EntityRegistry.find_by_domain` (keyword) is enough for debut. Optional one embed call later — not stacked.
4. Merge `LocalInferenceAdmission` into `ResourceGuard`. One semaphore, one `OOMProtector`.
5. Remove per-turn `RAGRouter()` construction in `Oracle.talk`.
6. Deduplicate `_route_by_domain` (backend/sigil assigned twice; `record_interaction` copied four times in `talk()`).
7. Freeze file sizes: do **not** grow `oracle.py`, `model_gateway.py`, `observability/__init__.py`, `hub_tools/tools.py`. Split only after talk is thin.

**Week 2 acceptance**

- One contract test: a single `RouteDecision` (entity, model, provider, reason). Fails if a second router module is imported on the talk path.
- Two concurrent `omega talk` calls: one local slot; user-visible busy or explicit cloud warning (`cost_warning`), never a silent cloud leak.
- `rg TriageRouter src/omega` and `rg SemanticRouter src/omega` empty (tests may mention the delete).

#### Week 3 — vault honesty

Pick **one**:

- **A (debut):** delete `src/omega/vault/` from the product surface; keep `crypto.py` in forge if wanted later.
- **B (minimal):** `crypto.py` + ≤50-line store; Gateway reads env/keyring only.

**Do not** adopt Keyblind, Authy, Agent Vault, or Presidio for debut.

**Acceptance:** `omega vault` is gone or works. Gateway does not import VaultCore.

---

### DOC-1 — Strategy stamps (so the fleet does not undo DEL-1)
**Owner:** Kali + Verity
**Depends on:** can start anytime; must land before the next multi-agent day

| File | Required edit |
|------|----------------|
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §4 | Banner: sprint authority moved to this manual + `ACTIVE_SPRINT.json`. G-1/W-1/V-1/SDP/NL-1 = `PARKED`. C-0.5 regex distillation = `SCRAPPED`. |
| `docs/strategy/STRATEGY_INDEX.md` | Header: this file is this month's execution SSOT. Remove “P0 TODAY = Gemma.” Mandates count 27 not 25. |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Invert rule 2. Flip G-1, W-1, Instruction Router, Qdrant, JIT Graph RAG, UO library swaps, Vault lease/FleetOrchestrator, Identity Fluidity to `PARKED`/`ARCHIVE`/`SCRATCH`. |
| `docs/strategy/UNOVERENGINEERING_PLAN.md` | Replace Phase 1 library swaps with DEL-1. **Delete §2.6** as an action (leave as rejected option). |
| All `docs/strategy/SDP_*.md` | Header stamp: `HUMAN PROTOCOL — DO NOT IMPLEMENT`. |
| `docs/strategy/RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md` | `ARCHIVE — DO NOT IMPLEMENT`. |
| JIT RAG briefs (Researcher + Roc, 2026-08-16) | `PARKED`. JIT = ContextBuilder may call HybridSearch. No new package. |
| `docs/strategy/POST_PR_ROSTER.md` | Scratch item #1 Instruction Router. |
| `docs/strategy/COGNITIVE_SOVEREIGNTY_EVOLUTION.md` | Header: `HORIZON — do not implement until DEL-1 + INST-1`. |
| `docs/strategy/VOS_HYBRID_PLAN_20260815.md` | Complete after Phase 0. Do not add realm validators. |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` §0 | Priority = `ACTIVE_SPRINT.json`. Compact: “do not add a control plane.” |
| `OMEGA_ENGINE.md` | Rewrite current-state table from probes, or replace metrics with a pointer to `ACTIVE_SPRINT.json`. |

**Acceptance:** `rg -n "P0 TODAY" docs/strategy/STRATEGY_INDEX.md` is gone. A cold-start agent who reads Index + Hub lands here, not on Gemma/WARP.

---

### P2 / P3 / P4 — only after DEL-1 week 1

P2 lint on survivors. P2-5 `make heritage-map` may run anytime (mechanical).

P3: CI runs the real suite without vanity counts; no `--exit-zero` on lint for E9/F63/F7/F82.

P4: README already handled in INST-1; remaining polish is tag + CONTRIBUTING.

---

## 6. Keep list (do not “simplify” these away)

- `SoulStore` (`src/omega/soul_store.py`)
- `OOMProtector` — **one** instance, used by ResourceGuard
- `HealthMonitor.get_breaker()` — only factory
- `SQLiteVecAdapter` + FTS5 + existing `HybridSearchEngine`
- Entity registry + thin WAD loader (`config/wads/_omega_default/`)
- Hivemind get_awareness / post_context / handoff (no new features)
- Agent-authored `proposed_lessons.yaml`
- Dual-artifact as a writing rule for handoffs
- `TEST_UX_CARMACK_PLAN.md` targets (`make test`, `test-prepush`, `test-all`)

`recall.py` / sleep-time compaction: **candidate after** ContextBuilder uses FTS/hybrid only. Not week-1 if it risks the demo.

---

## 7. God-module freeze (do not grow)

| File | Lines (2026-08-17) | Rule |
|------|-------------------:|------|
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3649 | No new tools in this file. Debut: document the 10 tools you will show; others must not throw on import. |
| `src/omega/observability/__init__.py` | 1583 | Do not add BudgetGate features here. Split only after talk is thin. |
| `src/omega/oracle/model_gateway.py` | 1481 | Load providers + generate. Nothing else new. |
| `src/omega/oracle/oracle.py` | 1253 | Dispatcher only; no new subsystems in `__init__`. |
| `src/omega/workers/youtube_worker.py` | 1181 | Not a debut surface; keep out of Hub import graph. |
| `src/omega/memory_store.py` | 1077 | Files + sqlite-vec; Redis opt-in only. |
| `src/omega/oracle/providers.py` | 1088 | No new backends for debut. |
| `src/omega/memory/sqlite_vec_adapter.py` | 992 | Freeze API. Do not add JIT/Qdrant flags. |

Crossing 1000 lines on a file that was under 1000 is a **presumptive blocker**.

---

## 8. Verification commands (honest, no vanity)

```bash
# Secrets (after rotation)
rg -n "sk-[a-zA-Z0-9]{16,}|csk-|AIza|ghp_|xai-" --glob '!docs/archive/**' --glob '!**/DEBUT_REMEDIATION_MANUAL*'

# Install surface
rg -n "warp-proxy-pool|qdrant-client|^    \"redis" pyproject.toml
rg -n 'pip install' scripts/install.sh

# Router uniqueness
rg -n "TriageRouter|SemanticRouter|RoutingTable|RAGRouter" src/omega

# Vault honesty
rg -n "store_credential|bury_credential|_load_sovereign_secrets" src/omega

# Talk still local
OMEGA_ENV=  source .venv/bin/activate && omega talk "hello"

# Tests: publish real counts
.venv/bin/python -m pytest -q --tb=no
# Report passed / failed / skipped / errors. Never a single “green” adjective.
```

Temple-grade after non-trivial changes (M13). If a mandatory tool is broken → `[TOOL-CHAIN-COLLAPSE]`. Do not simulate rigor.

---

## 9. Post-Debut Phase (Phase B — Week 2-6)

**Authority**: `ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01) + `SOVEREIGN_ARK_BLUEPRINT.md` §4 Priority Stack (Phase 0 Post-Debut Workstreams)

**6 New Workstreams** (added 2026-08-20, D-578..D-584):

| Workstream | Prefix | Owner | Scope |
|------------|--------|-------|-------|
| **GEMINI-NOTEBOOK** | GN | researcher | Free-tier-only (3 acct, 30 DR/mo), 2-NB (Active Research + Knowledge Base), notebooklm-py[mcp], master_token.json auth, SDP §10 gate honored |
| **DOCUMENTATION-SYSTEM** | DS | kali | Modular domain docs (workspace + runtime + curator + validated copy sync), `scripts/sync_domain_docs.py`, `config/domains/curators.yaml` |
| **LOCAL-INFERENCE-OPT** | LI | maat_n3 | Sequential loading, q8_0 KV cache, adaptive context buffer, Tier 0/1/2 matrix (Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B), llama-fit-params probe |
| **KNOWLEDGE-DOMAINS** | KD | kali | Runtime modules + workspace authoring + curator model, affinity presets per domain |
| **HEADROOM-INTEGRATION** | HR | maat_n3 | Semantic compression for tool outputs + RAG (40-90% savings), HeadroomMiddleware, MCP headroom tools |
| **ZSWAP-SUBSYSTEM** | ZS | maat_n3 | 16GB NVMe swap, zswap enabled (max_pool_percent=25, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMin=2G/MemoryHigh=5G/MemoryMax=6G |

**Execution Order** (after PUB-1 allowlist + INST-1 + DEL-1 Week 1):
1. **GN-1..GN-5**: Deploy notebooklm-py[mcp], create 2 strategic notebooks, free-tier fetch pipeline, smoke test, SDP distillation
2. **DS-1..DS-5**: Create DOMAIN_DOCUMENTATION_SYSTEM.md, workspace structure, runtime modules, sync script, STRATEGY_INDEX/CORPUS_MAP updates
3. **LI-1..LI-5**: AdaptiveContextBuffer, SequentialModelLoader, llama-fit-params, Tier 0 matrix, startup script
4. **KD-1..KD-3**: Domain module schema, curator model, affinity presets
5. **HR-1..HR-3**: HeadroomMiddleware, adaptive context integration, MCP headroom tools
6. **ZS-1..ZS-3**: zswap sysctl + kernel cmdline, 16GB NVMe swap + systemd unit, WAD packaging

**Dependencies**: DEL-1 Week 2 (router collapse) → QDRANT-MIGRATION (H2) → COGNITIVE-ARCH (H3) → VAULT-SPRINT → P2/P3/P4

---

## 10. Commit and coordination rules

- Prefix: `fix:`, `refactor:`, `docs:`, `chore:`, `test:`, `ci:`, `feat:` (feat only for INST-1 extras split).
- One ticket per PR/commit cluster. DEL-1 week 1 ≠ week 2.
- After each ticket: update `ACTIVE_SPRINT.json` status, Hub `NEXT_ACTION` one-liner, Hivemind completion.
- Distill L1→L2→L3 into **your** `proposed_lessons.yaml` before marking `completed` (M5/M11).
- Workspace lock before edits if parallel (`data/coordination/{YOU}_WORKSPACE_LOCK_YYYYMMDD.md`).

---

## 10. Decision log (this review)

| ID | Decision |
|----|----------|
| D-533 | This month's execution SSOT is this manual, not Ark §4. |
| D-534 | Publication (PUB-1) and runtime deletion (DEL-1) are separate cuts. |
| D-535 | Vault is not wired for debut. Invert V-1 from “build/wire” to “hide or delete.” |
| D-536 | One router: ProviderSelector + providers.yaml. Delete Triage + Semantic + RoutingTable. |
| D-537 | UO Phase 1 library swaps and UO §2.6 three-vault adoption are rejected for debut. |
| D-538 | SDP / Cognitive Sovereignty §7 / Qdrant / JIT Graph RAG / Instruction Router are PARKED. |
| D-539 | CP-3 is not publicly true until INST-1 passes on a machine without warp-proxy-pool. |
| D-540 | Corpus Map “nothing deleted by silence” is inverted for this campaign. |

---

## 11. Provenance

Reviewer: Grok CLI (Consulting Cloud Mind), 2026-08-17, session with Architect.

Sources: live tree probes (`git ls-files`, `wc -l`, `pip show`, import/caller `rg`), `Oracle.talk` / `_route_by_domain` / `_select_model`, `ModelGateway._load_sovereign_secrets`, `MemoryStore` Redis init, `FirewallChecker` forbid+allowlist, `RoutingTable._evaluate_condition`, `VaultCore.bury_credential` vs `cli/vault.py`, Hub + `ACTIVE_SPRINT.json` + Ark §4 + UO plan + Corpus Map + SDP/JIT/Qdrant briefs + README/install.sh/pyproject.toml.

This document is the remediation. Do not write another strategy brief instead of executing §5.

---

*⬡ OMEGA ⬡ DEBUT-REMEDIATION ⬡ v1.0.0 ⬡ 2026-08-17*
