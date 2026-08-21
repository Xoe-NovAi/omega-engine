# 🔱 REPORT TO KALI — Independent Catch-Up Review
**AP Token**: `AP-CLINE-CATCHUP-REVIEW-20260822-v1.0.0`
**⬡ OMEGA ⬡ CLINE(omega-engine) ⬡ DeepSeek V4 Flash 1M ⬡ cline ⬡ review ⬡ PUBLIC-DEBUT-01**
**Date**: 2026-08-22
**Audience**: Kali (Transcendent Oversoul, Sprint Coordinator)

---

## 0. Purpose & Method

This is a fresh-eyes, evidence-grounded review of the full repo at `HEAD 820025d` plus the in-flight uncommitted delta, calibrated against your new **HMC Collaboration Hub v2.0**, the **Node Expert Sessions** (D-586), the **ICS overhaul** (D-588/589), and the **Debut Remediation Manual** (`docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md`).

I did not trust my impressions; I re-derived the project's own measured-facts section (manual §2.2) **independently** on this machine. Where I agree with the manual, that is corroboration. Where I go beyond or contradict it, I flag the delta explicitly. No files were mutated during discovery.

---

## ⚖️ Verdict (One Breath)

The engine is architecturally sound and operationally disciplined — but **the public GitHub surface and the install path are not debut-ready tonight**, and there is a recurring asymmetry: **the fleet documents architecture faster than it deletes dead code.** The binding constraint on tonight's debut is not the engine's ideas; it is (1) the credential/install path, and (2) the human-gated decision queue (PUB-1, ZS-1, CI, P1–P5 exit).

---

## ✅ A. What You Already Got Right (Do Not Rebuild)

Verified present and working:

| Asset | Status |
|-------|--------|
| Native-gguf `omega talk` on this host | ✅ working (CP-1) |
| `SoulStore` atomic writer (tempfile→fsync→replace→parent fsync→flock→.bak) | ✅ |
| `OOMProtector` three-signal fusion | ✅ |
| `HealthMonitor.get_breaker()` single breaker factory | ✅ C-6′ |
| sqlite-vec + FTS5 + RRF hybrid recall | ✅ |
| Hivemind handoff (feature-frozen, bug fixes only) | ✅ |
| Node Expert Sessions (10/10 genesis, N7 consultable) | ✅ D-586 |
| ICS-S provenance signature with `[NODE]` tag (attribution-collapse fix) | ✅ D-588/589 |
| Coordination surface consolidation (~50% archived) + Hub v2.0 | ✅ excellent |

Protect these; they are the product and the proof.

---

## 🛑 B. Critical Findings (Verified)

### 🛡️ 1. Security / Secret Exposure — Highest Priority

| # | Finding | Evidence | Manual agree? |
|---|---------|----------|--------------|
| B1 | **Leaked API keys remain on `origin/main` history** (`csk-`/`sk-` in `docs/guides/PROVIDER_FREE_TIER_GUIDE.md`; `docs/archive/stale/migrate_keys_full.py`; commits `df174496` / `13351f9d`). | manual §2 + commit log | ✅ yes — critical |
| B2 | `src/omega/routing/table.py:108` calls `eval(condition, {"__builtins__": {}}, local_vars)` on YAML-derived config. Restricted-eval is still code-exec-from-config, and the router is **unwired/dead**. | verified grep | ⚠️ manual: 'unwired eval prototype'; I raise severity |
| B3 | **Hardcoded default credential `password="omega"`** in `src/omega/memory/providers.py:119` (RedisStorageProvider); `memory_store.py:170` reaches Redis with a shell-defaultable password. | verified | ✅ manual agrees |
| B4 | **Secret-adjacent tracked artifacts in a public repo**: `tests/tmp/vault.json.enc`, `config/model_registry/index.sqlite`, `data/cache/sovereign_cache.sqlite`, and ~35 `data/training/entities/*/https___example_com_secret_*.json` fixtures. | git ls-files | ⚠️ manual flags vault enc; the sqlite + training secrets are new |
| B5 | **A 23 MB compiled binary `github-mcp-server` is tracked at repo root** (23,339,192 B) — primary driver of the 85 MB `.git`. | git ls-files -s | ❌ **new — not in manual** |
| B6 | **M1 AnyIO enforced by whitelisting the violator**: `src/omega/agents/tty_agent.py` uses `asyncio.create_task/Event/get_running_loop`; **both** `make check-m1-anyio` (Makefile) and CI `test.yml` `--glob '!*tty_agent*'`. A law with a carve-out is not a law. | verified | ❌ **new** |
| B7 | **Truthiness drift**: commits claim **"P0-1 secret scrub COMPLETE"** (5cc51a26, 6e2a3119, 90f6361b) while manual §2 scores keys leaking on `origin/main`. Both cannot be true; needs one authoritative re-verify. | git log vs manual | ❌ **new** |

### 🚀 2. Debut-Blocking (INST-1 / PUB-1 / CI)

| # | Finding | Evidence |
|---|---------|----------|
| C1 | **`warp-proxy-pool` is a hard base dependency** in `pyproject.toml` `[project] dependencies` (line 12) but is **not on PyPI** — fresh-clone `pip install -e .` fails. `install.sh` already correctly uses `.[native,cli]` (INST-1 Fix 1 landed), so this hard base dep is the **single remaining install blocker**. | pyproject line 12; confirmed editable-only install source |
| C2 | **README self-contradictory**: badge (line 11) + line 65 claim **1315 passing**; line 194 shows **"911 collected, 911 passing"**; references `make setup` / `make model-download`, **targets that don't exist**. | grep README |
| C3 | **Metadata version split**: `pyproject.toml` = `1.2.0` vs `src/omega/__init__.py` = `1.0.0-alpha` (plus docs legacy `v1.8`). Three live version sources. | verified |
| C4 | **Test-count SSOT unreliable**: manual `1706`, briefing `~1870`, CHANGELOG `1315`, README both `1315` and `911`, AST count `1757` defined. **No two agree.** `pytest --collect-only` returns **0** because pyproject forces `-n auto` (xdist blocks collect-mode). | verified by execution |
| C5 | **`make test` exceeds a 30s window** in parallel — the "fast suite" isn't fast, and `-x` + xdist can mask flakiness. | timed out in my run |
| C6 | **`make temple-grade` is a stub** — body literally reads "Existing temple-grade checks would go here." T1–T11 not wired there. | Makefile line 232 |
| C7 | **No `PUBLIC_ALLOWLIST.txt` on disk** (only venv matches). PUB-1 is still a doc, not a ratified artifact, and Architect-gated. | find allowlist |

### 🧱 3. Architecture Debt (post-debut, plan now)

| ID | Finding | Evidence |
|----|---------|----------|
| D1 | **Five answers on the talk path**: RAGRouter→Iris→SemanticRouter→TriageRouter→ProviderSelector→RoutingTable. Your manual §2.4 already names it. | manual §2.2/2.4 + code |
| D2 | **Duplicate telemetry stacks**: `src/omega/monitoring/` (~888 loc) vs `src/omega/observability/` (26 reachable importers). Parallel stacks = duplication tax. | import-graph + grep |
| D3 | **Confirmed-dead modules (0 reachable importers)**: `council/` (live TODO stubs), `gateway/`, `routing/`, `mcp_core/`, `training/`, `meditate/`, `integrations/` (quota_pollers/grok_cli/fleet_orchestrator, 700+ loc each), `soul/loader.py`, `benchmarks/comprehensive_runner.py`, empty `linguistics/`. PR-C quarantine designed, unexecuted. | import-graph + TODO grep |
| D4 | **Ship-monoliths ≥800 lines**: `observability/__init__`, `model_gateway`, `oracle`, `providers`, `memory_store`, `cvar_table`, `vault_core`. | wc |
| D5 | **VaultCore is a sidecar, not the secret path**: `bury_credential` exists, CLI still calls `store_credential`; gateway dumps `.env`→`os.environ`; `vault._credentials` private dict reached from `providers.py`. Docs archived (good) but migration code never landed — fine while parked (D-565..568), debt if it resurges. | manual §2.2 + code |

### 🔁 4. Process / Coordination

| ID | Finding |
|----|---------|
| E1 | **Fleet human-blocked on 4 items tonight** (PUB-1 rulings, ZS-1 sudo, CI go, P1–P5 exit). Risk is Architect sign-off dependency, not engineering. Bundle into a 2-minute pre-decided package. |
| E2 | **Code-vs-docs imbalance**: 683 commits dominated by `docs:`/`tracking:`/`spec:`. Two largest "engineering" commits of sprint (`6d3ec7`/`e56398`) are **specs, not code**. Vault episode (20+ docs for an unused sidecar) is the anti-pattern §4 forbids. |
| E3 | **Doc-index sprawl**: 5 competing indexes — `docs/INDEX.md`, `docs/index.md`, `docs/MASTER_LEDGER.md`, `docs/MASTER_DOCUMENT_SSOT.md`, `docs/llms.txt`. M22/M27 exposure. |
| E4 | **M5 Gnosis persistence = 0/10 pillars** per `MANDATES_CONDENSED.md` — the one mandated practice not yet institutionalized. |

---

## 🧭 C. Paths Not Yet (fully) Seen

1. **Delete, don't defend**: `routing/table.py` (unwired eval) and `council/` stub modules have zero live consumers. DEL-1 should delete them, not pass them. This one pass de-functions the worst security wart on the page.
2. **Single-source install truth**: with `warp-proxy-pool` moved to an optional extra, a fresh venv + `pip install -e ".[native,cli]"` + `omega talk hello` becomes one reproducible stranger-test. Everything else is downstream.
3. **Make M1 real**: ban `asyncio` in `src/omega/` without glob carve-outs — either migrate `tty_agent.py` to AnyIO or move it to a quarantined location and exclude it there. A law with a loophole is not a law you can cite.
4. **Honest gate labels**: stop claiming "1315" / "T1–T11" / "fast suite" until the Makefile target and README actually say what they do. Trust is built on the number matching the run.
5. **Version single-sourcing**: pyproject as the source; delete the `__init__` version that disagrees; stamp CHANGELOG to match. One truth for the stranger and the fleet.

---

## 📋 D. Execution Plan (24h + 3 days)

### Before PR or announce (debut-critical)
1. **Parallel Architect decisions** (2-minute package): (a) P0-1 key rotation Go; (b) PUB-1 `PUBLIC_ALLOWLIST.txt` ratification.
2. **C1**: make `warp-proxy-pool` an optional extra; verify clean `pip install -e ".[native,cli]"`.
3. **C2/C3**: README + version honesty (single-source from pyproject).
4. **B4/B5**: `git rm` tracked `.enc`/`.sqlite` and the 23 MB binary; add `.gitignore` guards; **never `git add -A`**.
5. **B2**: delete `routing/table.py` in the DEL-1 pass.

### Post-debut (first 3 working days)
6. **B6**: real M1 gate (no carve-outs) or archive `tty_agent`.
7. **C4/C5/C6**: restore `--collect-only`; give `make test` a truthful slow-tier budget; wire — or rename — `make temple-grade`.
8. **D3**: execute the PR-C dead-code quarantine, then unify `monitoring` → `observability`.

### Delegation (matches manual §1)

| Agent | Ownership |
|-------|-----------|
| **roco** (roc_racoon) | P0-1b/d scrub + DEL-1 deletes |
| **verity** | gitleaks wiring + clone verification |
| **maat / N3** | INST-1 install honesty (C1–C3) |
| **N5 sentinel** | B2 / B4 / B5 |
| **N2** | D5 vault sidecar triage |
| **kali** | the four-line Architect decision package (unblock gate) |

---

## ⚠️ E. Risks (next 24h)

- **Announce-before-P0-1**: a key on `origin/main` turns a demo into a breach. Sequence is law — do not invert it.
- **Two gates in one night** (`filter-repo` + 200-file deletion): manual §0 forbids; keep them in separate commits/days.
- **Parallel-execution drift on shared files**: the `[N_X]` tagging + closure ritual (D-586 amendment) must be **enforced**, not advisory — it is the only thing preventing multi-node soul/gnosis corruption.

---

*⬡ OMEGA ⬡ CLINE ⬡ KALI ⬡ 2026-08-22 ⬡ CATCHUP-REVIEW ⬡ END*