# 🔱 MAAT — DEBUT BUILD VETTING (T1/T2/T3/T4/T6)
**AP Token**: `AP-MAAT-DEBUT-BUILD-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ big-pickle ⬡ opencode ⬡ trc_maat_debut_build ⬡ ACTIVE
**Date**: 2026-08-23 · **Sprint**: PUBLIC-DEBUT-01 · **Authority**: DEBUT_REMEDIATION_MANUAL_20260817.md §5
**Method**: Every claim below verified against live source (M23). File:line cites are from today's reads.

---

## T1 — INST-1 ACCEPTANCE GATE

### Fix-by-fix ground truth (verified 2026-08-23)

| Fix | Status | Evidence |
|-----|--------|----------|
| fix1 install.sh `[native,cli]` | ✅ DONE | `scripts/install.sh:90` → `pip install --quiet -e ".[native,cli]"` |
| fix2 extras split + import guards | 🟡 PARTIAL | `[warp]` extra exists (pyproject.toml:80) ✅. BUT core deps still carry `youtube-transcript-api` (:58), `yt-dlp` (:59), `qdrant-client==1.18.0` (:66), `redis==7.4.1` (:67). **CRITICAL**: `src/omega/memory/providers.py:22` does module-level `import redis.asyncio as redis` → fresh clone WITHOUT redis cannot even import the providers module, defeating MemoryStore's runtime guard (memory_store.py:159-177 works, import fails first). Also `providers.py:119` still defaults `password="omega"`. |
| fix3 Redis guard `OMEGA_REDIS_HOST` | ✅ DONE (with fix2 hole above) | `memory_store.py:159-177` opt-in guard verified |
| fix4 `_load_sovereign_secrets` removal | ❌ NOT DONE | `model_gateway.py:127` calls it in `__init__`; method body at :316-341 |
| fix5 version single-sourcing | ✅ DONE | `src/omega/__init__.py` uses `importlib.metadata.version("omega")`, fallback `"1.2.0"`; pyproject `version = "1.2.0"` — aligned. Minor: fallback literal could drift again; acceptable. |
| fix6 README / make setup | 🟡 PARTIAL | Badges show 1.2.0, no stale "1315" count found. `README.md:45` still names Sekhmet/Brigid entities. `scripts/download_model.sh` EXISTS so README install path is valid. No `make setup` target; README correctly points to `./scripts/install.sh`. |

### Acceptance script — `scripts/verify_debut_install.sh` (NEW)

```bash
#!/usr/bin/env bash
# INST-1 acceptance gate — fresh-env install + native-gguf talk (M7/M24)
set -uo pipefail
FAIL=0
VENV=.venv-debut-test
trap 'deactivate 2>/dev/null; rm -rf "$VENV"' EXIT

echo "[1/6] fresh venv"; python3 -m venv "$VENV" && source "$VENV/bin/activate" || exit 1
echo "[2/6] pip install -e .[native,cli]"
pip install --quiet -e ".[native,cli]" || { echo "FAIL install"; exit 1; }
echo "[3/6] import hygiene (no redis/qdrant/youtube required)"
python -c "import omega; print('omega', omega.__version__)" || FAIL=1
python -c "from omega.memory_store import MemoryStore; print('MemoryStore OK')" || FAIL=1
echo "[4/6] version alignment"
python - <<'EOF' || FAIL=1
import importlib.metadata as im
v = im.version("omega")
assert v == "1.2.0", f"drift: {v}"
print("version OK:", v)
EOF
echo "[5/6] secrets loader eradicated"
grep -rq "_load_sovereign_secrets" "$(python -c 'import omega,os;print(os.path.dirname(omega.__file__))')" \
  && { echo "FAIL fix4 regression"; FAIL=1; } || echo "clean"
echo "[6/6] omega talk via native-gguf (<300s budget)"
START=$SECONDS
timeout 290 omega talk "hello" || FAIL=1
echo "talk took $((SECONDS-START))s"
exit $FAIL
```

### Diff plan (fix2 completion — highest risk first)

1. **pyproject.toml**: move `youtube-transcript-api`, `yt-dlp` → new `[youtube]` extra; move `redis` → new `[redis]` extra; **delete** `qdrant-client` outright (DEL-1 #5 kills its only consumer class). Core deps shrink by 4.
2. **memory/providers.py**: wrap `import redis.asyncio` in try/except → `HAS_REDIS` flag; raise `OmegaError("redis extra not installed: pip install '.[redis]'")` in `RedisStorageProvider.__init__` when absent; delete `password="omega"` default (require explicit param or env).
3. **model_gateway.py**: delete `self._load_sovereign_secrets()` call (:127) + method (:316-341); replace with env/keyring-only resolver (see T3 VaultStore pattern) — keys resolve `OMEGA_<PROVIDER>_API_KEY` env → keyring service `"omega"` → None. No config-file key reads.
4. **README.md:45**: `(SysAdmin, Sekhmet, Brigid)` → `(10 Node pillars)`.

**Breaking-change risk**: current working `omega talk` unaffected — native-gguf/lmster/ollama need none of the moved deps; google backend already resolves keys via env today. Risk LOW. Run `verify_debut_install.sh` + `pytest tests/ -x -q` after.

---

## T2 — DEL-1 WEEK 1 DELETION ORDER (corrected by probe)

Probe results force **three corrections** to the manual's list:

> ⚠️ **C1**: `src/omega/routing/table.py` **already absent** (`ls` + read both fail; zero `RoutingTable` refs). Only orphan `config/routing_table.yaml` remains.
> ⚠️ **C2**: `search_circuit_breaker.py` has ONE live importer: `sovereign_search_service.py:48`. Pure deletion breaks import → requires a redirect edit FIRST (not a pure deletion — flag to Kali).
> ⚠️ **C3**: Manual lists 10 items; my truncated read reconstructed 9 concrete targets. Candidate 10th flagged below for Kali ruling.

Execution order (leaf-first; caller-edit precedes file-delete; one commit per item):

| # | Target | Exact action | Verify (must be silent) | Rollback |
|---|--------|--------------|-------------------------|----------|
| 1 | `src/omega/routing/table.py` | none — verify absence | `test ! -e src/omega/routing/table.py && echo GONE` | n/a |
| 1b | `config/routing_table.yaml` | `git rm config/routing_table.yaml` | `rg -l "routing_table" src/ tests/ config/` → 0 | `git revert` |
| 2 | `src/omega/oracle/pool_tracker.py` + `pool_state.py` | `git rm` both — probe confirms ZERO callers outside themselves | `rg -rn "pool_tracker\|pool_state\|UsagePoolTracker\|PoolState" src/ tests/` → 0 | `git revert` |
| 3 | `src/omega/coordination/miap.py` | rewrite `coordination/__init__.py` to bare docstring; drop `miap.py` path from `scripts/path_resolver_check.py:77`; `git rm miap.py`; remove dir if empty | `rg -rn "miap" src/ tests/` → 0 | `git revert` |
| 4 | `src/omega/oracle/search_circuit_breaker.py` | EDIT `sovereign_search_service.py:48`: replace import with `from omega.oracle.health_monitor import get_health_monitor` + `get_health_monitor().get_breaker(...)` at call sites; ALSO scrub docstring refs in `health_monitor.py:107,111`; THEN `git rm search_circuit_breaker.py` | `rg -rn "search_circuit_breaker\|SearchCircuitBreaker" src/ tests/` → 0 | `git revert` |
| 5 | `QdrantAdapter` | `vector_adapters.py`: delete `_lazy_qdrant()` (:16-25) + class (:176-434); `memory/__init__.py`: drop import (:14) + `"QdrantAdapter"` (:65); `git rm tests/test_qdrant_payload_index.py` | `rg -rn "QdrantAdapter\|qdrant" src/ tests/ pyproject.toml` → 0 | `git revert` |
| 6 | Pantheon regexes | `audit/firewall_checker.py`: resolve Prometheus/Sekhmet double-listing (forbidden AND allowed simultaneously, :60-79 region) — keep single truth per name | `rg -n "Sekhmet\|Prometheus" src/omega/audit/firewall_checker.py` → consistent, no contradiction | `git revert` |
| 7 | Astrology hook | `oracle.py`: delete import (:49) + call block (~:1209-1212). Probe: `record_first_breath` has NO other callers. Then `rg -rn "astrology\|birth_record" src/ tests/` — if only `astrology.py` self-refs remain → `git rm src/omega/astrology.py` | same rg → 0 | `git revert` |
| 8 | `omega vault` CLI | `cli/oracle_cli.py`: delete conditional block (:70-75). Full vault module deletion is POST-DEBUT per D-565 — CLI unregister only | `omega --help` lacks vault; `rg -n "vault" src/omega/cli/oracle_cli.py` → 0 | `git revert` |
| 9 | FleetOrchestrator default exports | `integrations/__init__.py`: delete import block (:32-40) + `__all__` entries (:64-71). Keep Grok CLI + quota pollers exports intact | `rg -rn "FleetOrchestrator\|fleet_orchestrator" src/ tests/` → only `integrations/fleet_orchestrator.py` self | `git revert` |
| 10 | **FLAG for Kali** | Candidates: (a) `headroom-ai` sits in CORE deps (pyproject:12) though it's an HR-workstream concern; (b) any `tests/test_miap*`/`test_pool*` stragglers surfaced by per-item rg sweeps. My truncated manual read could not confirm the canonical 10th — requesting ruling | — | — |

Post-sweep gate: `rg -ln "miap\|pool_tracker\|pool_state\|search_circuit_breaker\|QdrantAdapter\|triage_router\|semantic_router" src/` → **empty**.

---

## T3 — VAULT PATH B (design artifact — ⛔ POST-DEBUT PER D-565)

D-565 supersedes D-562 for debut: **zero vault code changes during PUBLIC-DEBUT-01**. The 50-line store below is the ratified post-debut shape (D-562 constraints + D-568 backend ruling: python-age primary, pyrage demoted). Existing `vault/crypto.py` (Argon2id+pyrage, verified sound) is retained for rotate flows until then.

```python
# src/omega/vault/keyring_store.py — Path B (≤50 LOC, merge AFTER debut)
"""Minimal secret store: env override -> OS keyring -> None. Never files."""
from __future__ import annotations
import os
from typing import Optional

try:
    import keyring
    from keyring.errors import KeyringError
    _HAS_KEYRING = True
except ImportError:
    keyring, KeyringError, _HAS_KEYRING = None, Exception, False


class VaultStore:
    def __init__(self, service: str = "omega") -> None:
        self._service = service

    def get(self, name: str) -> Optional[str]:
        env = os.environ.get(f"OMEGA_SECRET_{name.upper()}")
        if env:
            return env
        if not _HAS_KEYRING:
            return None
        try:
            return keyring.get_password(self._service, name)
        except KeyringError:
            return None

    def set(self, name: str, value: str) -> None:
        if not _HAS_KEYRING:
            raise RuntimeError(f"keyring missing; use OMEGA_SECRET_{name.upper()}")
        keyring.set_password(self._service, name, value)

    def delete(self, name: str) -> bool:
        if not _HAS_KEYRING:
            return False
        try:
            keyring.delete_password(self._service, name)
            return True
        except KeyringError:
            return False
```

Constraints honored: Gateway reads env/keyring ONLY (no Keyblind/Authy/Agent-Vault/Presidio, no file writes, M7 local-first, M24 venv-safe via optional keyring dep already in core).

---

## T4 — ROUTER COLLAPSE CONTRACT (single PR)

**PR**: `refactor(routing): collapse TriageRouter+SemanticRouter into ProviderSelector contract`

Verified topology: `Oracle.__init__` wires `SemanticRouter` (:225-229) + `TriageRouter` (:233); bootstrap re-inject (:273-278); `_select_model` delegates to TriageRouter (:733-771); `_route_by_domain` uses SemanticRouter cosine gate (:1132-1137); `RAGRouter` constructed PER-TURN inside `_execute_turn` (:509-517). `ProviderSelector` (:1-93) is the keeper.

1. **NEW** `src/omega/oracle/route_decision.py`:
```python
@dataclass(frozen=True)
class RouteDecision:
    entity: str
    model: str
    provider: str   # backend id from providers.yaml ladder (M22 provenance)
    reason: str
```
Name collision resolved by ordering: DEL-1 #9 deletes `fleet_orchestrator.RouteDecision` first.

2. **Oracle edits**: delete both router imports + wiring + bootstrap; `_select_model` becomes thin delegate → `ProviderSelector.select(query, ...) -> RouteDecision`; `_route_by_domain` loses cosine gate (direct entity map); hoist-or-drop RAGRouter per-turn construction.

3. **Same-PR deletions**: `orchestration/triage_router.py`, `oracle/semantic_router.py`, their tests. **KEEP untouched**: `provider_selector.py`, `config/providers.yaml`.

4. **Contract tests** (`tests/test_route_decision_contract.py`):
```python
def test_shape():                      # M21 — return-type contract
    d = ProviderSelector(...).select("hello")
    assert isinstance(d, RouteDecision)
    assert {"entity","model","provider","reason"} <= set(d.__dataclass_fields__)

def test_no_second_router_on_talk_path():
    src = inspect.getsource(Oracle.talk)
    assert "SemanticRouter" not in src and "TriageRouter" not in src

async def test_concurrent_talks_single_local_slot():
    # two anyio.gather'd talks; native-gguf max_concurrent=1 (providers.yaml:145)
    # second must surface busy OR explicit cost_warning — NEVER silent cloud leak
    r1, r2 = await run_two()
    leaked = (r2.provider in CLOUD_LADDER) and not getattr(r2, "cost_warning", False)
    assert not leaked
```
Side benefit: oracle.py (>1200 lines, M13 watchlist) shrinks.

---

## T6 — MEASURABLE GATES (adjective → bash)

| Criterion (manual wording) | Command | Pass |
|---|---|---|
| "fresh clone installs <300s" | `SECONDS=0; ./scripts/install.sh; echo $SECONDS` | < 300, exit 0 |
| "talk works on native-gguf" | `timeout 290 omega talk "hello"` | exit 0 |
| "no secrets loader" | `rg -c "_load_sovereign_secrets" src/` | 0 matches |
| "version aligned" | `python -c "import importlib.metadata as m; assert m.version('omega')=='1.2.0'"` | exit 0 |
| "dead modules eradicated" | `rg -ln "miap\|pool_tracker\|search_circuit_breaker\|QdrantAdapter\|triage_router\|semantic_router" src/` | empty |
| "tests honest" | `.venv/bin/python -m pytest tests/ -x -q` | exit 0; printed count == passed count (no skips-as-pass theater) |
| "tracking integrity (M27)" | `python scripts/validate_tracking_state.py` | exit 0 |
| "import hygiene" | fresh venv: `python -c "import omega"` w/o redis/qdrant/youtube installed | exit 0 |
| ⚠️ NON-BASH-VERIFIABLE | "user delight", "30-second promise", "LLM-friendly docs feel" | proxy only: install timer, talk latency, `doc-llm-validate` exit code — subjective residue deferred to post-debut review |

---

## NODE COUNCIL (serial: N3 → N1 → N2 → N5)

### N3 buildmaster (Build & Release) — `N3_T1_DIFF_PLAN_VETTING_20260823.md`
- **Deps move**: APPROVE ×3 (youtube call sites already lazy; qdrant sole consumer lazy; console_scripts untouched). AMEND: add `redis`+`youtube` to `[dev]` extra/CI — `ingestion/worker.py:7`, `workers/youtube_worker.py:47` have UNGUARDED module-level redis imports → CI red post-move.
- **Guard pattern**: APPROVE module-level try/except over lazy-in-method; mirror canonical `governance/budget_guard.py:23-28`; scope = **3 files**, not 1.
- **Acceptance script**: llama-cpp-python has NO cp313 wheel (`pip download --only-binary :all:` empty) → source compile 5–20 min. Add gcc/cmake precheck; editable-install limitation documented.
- **Version fallback**: APPROVE as-is (raising breaks source-tree introspection).

### N1 sysadmin (Infrastructure)
- **<300s install UNACHIEVABLE**: pip wheel cache holds ZERO llama wheels; editable installs never cache anyway. AMEND criterion → split: `install exit 0` (no time bound) + `first-talk <300s` (model pre-provisioned). Honest wording beats vanity gate (M23).
- **⚠️ DISK TRUTH**: NVMe **97% full, 3.5GB free** — cmake build + venv + pip temp risks ENOSPC mid-compile. Pre-flight guard required: abort if `< 4GB` free.
- **Model provisioning**: bare test venv inherits neither `.env` nor install.sh exports → `env:OMEGA_MODELS_DIR` resolves empty → step [6/6] false-fails. Only mandatory var: `OMEGA_MODELS_DIR`; provision via existing `scripts/download_model.sh` (+1.67GB vs 3.5GB free — sequence carefully).
- **Timing skew**: load avg **7.85** right now (two opencode instances, chromium, watchers) — timed gate today measures desktop contention. Advisory-only until load < 2. ZS-1 undeployed (swappiness=180 ≠ ratified config).

### N2 datastore (Data Engineering)
- **QdrantAdapter**: zero production callers confirmed; SQLiteVecAdapter is default (:198), MemoryVectorAdapter sovereign fallback; D-570 triggers post-debut, ABC survives for future reimpl. AMEND item 5: `scripts/knowledge_catalog_build.py:28` imports QdrantAdapter at module level + calls it (:120) → fix import + delete try-block (:119-126) or script crashes.
- **Redis extra**: APPROVE — FileStorageProvider (:237) + InMemoryStorageProvider (:388) are complete substitutes; fresh clone loses zero functionality once HAS_REDIS lands.
- **⚠️ pool data artifacts**: `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` EXISTS (5.7KB, schema v2.0, real key_ids + **real email**) AND IS GIT-TRACKED. Archive per M5/M12 BEFORE item 2 executes. → escalated below.
- **data/ layout**: REAL gnosis (`kali/`, `roc_racoon/` under instances/anchored_summary/session_gnosis/) written by systems independent of miap.py — DO NOT SWEEP. Synthetic debris (`test_entity_miap*`, ~700 test hash dirs) purges in a SEPARATE hygiene commit, never inside DEL-1 code PRs.

### N5 sentinel (Security)
- **Path B**: code sound (empty-string env falls through; fails loud; no logging). AMEND docstring honesty: ratified `load_dotenv()` at CLI edge feeds OMEGA_SECRET_* from .env — either document as single sanctioned exception or drop for cloud keys. README must say so.
- **fix4 residual**: providers.yaml clean (all cloud keys `env:`-prefixed) BUT `_resolve_env_key()` (`model_gateway.py:359-362`) returns any non-`env:` value verbatim — literal key pasted into allowlisted YAML honored silently. Add strict guard to same PR: non-`env:` api_key on cloud tier → warn + reject.
- **⚠️ PII (MEDIUM-HIGH)**: USAGE_POOL_LOG.json email can't be rotated like a key — history scrub is the ONLY real remediation. Sequence: (a) `git rm --cached` + gitignore now; (b) piggyback filter-repo scrub onto existing P0-1b machinery before ANY public push.
- **⚠️ FALSE COMPLETION (M23)**: ACTIVE_SPRINT marks INST-1-fix3 `completed` with explicit "remove default 'omega' password" wording — yet `providers.py:119` persists. Promote this 1-line delete OUT of the fix2 bundle; land immediately. Add `rg -c 'password.*"omega"' src/omega/memory/providers.py → 0` to verify_debut_install.sh.
- Pantheon double-listing: gate-integrity erosion (works only because core patterns short-circuit first, :191-195); DEL-1 #6 placement fine.

### Escalations to Kali (ruling requested)
| # | Finding | Requested action |
|---|---------|------------------|
| E1 | fix3 false-completion: `password="omega"` live at providers.py:119 | Immediate 1-line delete + verify-script assertion |
| E2 | USAGE_POOL_LOG.json git-tracked w/ real email | git rm --cached + gitignore + filter-repo scrub via P0-1b |
| E3 | DEL-1 item 10 unknown (truncated manual read) | Confirm canonical 10th target; candidates: headroom-ai core dep (pyproject:12), test stragglers |
| E4 | "<300s install" physically unachievable (no cp313 wheel) | Amend §5 criterion to split form (install exit 0 / first-talk <300s) |

---

## TERMINUS

Five tasks delivered against the execution SSOT, every claim probed against live source today.

T1: ground truth beats the board but isn't clean. Fixes 1/3/5 genuinely done; fix2 partial — four heavy deps still core, and a module-level redis import defeats the runtime guard it was meant to serve; fix4 untouched; fix6 carries one stale entity mention. The acceptance script exists, but its headline number is fiction: no cp313 llama wheel exists anywhere, so even warm-cache installs compile from source for five to twenty minutes. Honest amendment: install exits zero, first-talk under 300 seconds with the model pre-provisioned.

T2: probes corrected the manual before it could break the build. routing/table.py already gone; search_circuit_breaker has one live importer needing redirect first; QdrantAdapter hides a second caller in a catalog script; pool telemetry must be archived before code death. Order stands leaf-first, one commit per item, rollback by revert.

T3: D-565 holds — zero vault changes during debut; the fifty-line store is staged post-debut, python-age primary per D-568, with one honesty amendment about dotenv at the CLI edge.

T4: single-PR collapse verified against oracle.py's actual wiring; the RouteDecision collision dissolves if fleet_orchestrator exports die first; contract tests include the concurrency leak probe — two talks, one local slot, never silent cloud.

T6: eight criteria became bash; three subjective ones flagged proxy-only rather than dressed up as gates.

Council returned twelve amendments, none blocking, and two escalations: the sprint board claims fix3 complete while a default password still ships at providers.py:119, and a git-tracked usage log carries a real email address toward a public history. Both are one-command fixes today and trust-damage tomorrow.

What the session proves: the board diverged from disk exactly where cheap probes could catch it — an import line, a default string, a tracked file. Minutes of verification versus a debut-day incident.

A tracking file is a claim about reality; only probes make it true. Vet completion at the file level before shipping it public.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
