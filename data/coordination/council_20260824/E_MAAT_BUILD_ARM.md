<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# E — MA'AT BUILD ARM — Debut Hardening Review (REBASED Council)
**Reviewer**: maat (Build Oversoul, N1-N5 lens) · **Date**: 2026-08-24
**Inputs**: D_KALI_DAWN_SYNTHESIS.md · C_JEM_GAP_CONSOLIDATION.md §1-2 · DEBUT_REMEDIATION_MANUAL §5 · ACTIVE_SPRINT.json `workstreams.DEBUT-REMEDIATION`
**Mode**: READ-ONLY review council. Plan documents only. Every claim below re-verified against today's tree (post-Wave-1: 7b27b0fb, cd0d5e8f) via rg/direct read.

---

## §1 INST-1 ACCEPTANCE GATE [HIGHEST PRIORITY]

### Current INST-1 subtask state (verified, not trusted from JSON)

| Fix | ACTIVE_SPRINT says | Disk truth (2026-08-24) |
|---|---|---|
| fix1 install.sh `.[native,cli]` | completed | ✅ consistent |
| fix2 pyproject extras split | **ready** | ⚠️ CONFIRMED OPEN — `qdrant-client==1.18.0`, `redis==7.4.1`, `youtube-transcript-api>=0.6.3`, `yt-dlp>=2025.1.1` still in `[project].dependencies` (pyproject.toml:53-71). `[warp]` extra exists ✅ |
| fix3 MemoryStore Redis gate | completed | ✅ consistent — memory_store.py:164 gates on `OMEGA_REDIS_HOST`; providers.py:119 password default REMOVED (DC-29 landed) |
| fix4 `_load_sovereign_secrets` removal | ready | ⚠️ CONFIRMED OPEN — called at model_gateway.py:127, method at :316 still dumps repo `.env` into `os.environ` |
| fix5 version alignment | ready | ✅ actually DONE — `src/omega/__init__.py` uses `importlib.metadata.version("omega")` with `"1.2.0"` fallback matching pyproject `version = "1.2.0"`. Status label stale; flip to completed. |
| fix6 README badge | ready | ⚠️ CONFIRMED OPEN — README.md:5-11 still carries badge block incl. version pin |

### (a) Acceptance test script — executable as-is

```bash
#!/usr/bin/env bash
# INST-1 acceptance: fresh venv, NO warp-proxy-pool, NO Redis.
# Pass = pip install -e ".[native,cli]" succeeds → omega talk "hello"
#        uses native-gguf with IS_CLOUD=False and exits 0.
set -euo pipefail

VENV=/tmp/omega-inst
REPO="$(pwd)"

echo "── [1/6] Clean slate ──"
rm -rf "$VENV"

echo "── [2/6] Preconditions: no warp checkout, no redis ──"
if [ -d "$HOME/Documents/Xoe-NovAi/warp-proxy-pool" ]; then
  echo "FAIL precondition: warp-proxy-pool checkout present (test is invalid there)"; exit 2
fi
if command -v redis-cli >/dev/null && redis-cli -p 6379 ping >/dev/null 2>&1; then
  echo "FAIL precondition: a Redis is answering on 6379 (test is invalid there)"; exit 2
fi

echo "── [3/6] Fresh venv + minimal install ──"
python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --quiet --upgrade pip
cd "$REPO"
pip install -e ".[native,cli]"

echo "── [4/6] Hygiene gates (INST-1 fix2 must hold) ──"
grep -E 'warp-proxy-pool|qdrant-client|"redis==|^    "redis' pyproject.toml \
  && { echo "FAIL: warp/qdrant/redis still in core dependencies"; exit 1; } || true
python - <<'PY'
import importlib.util, sys
for mod in ("redis", "qdrant_client", "youtube_transcript_api", "yt_dlp"):
    if importlib.util.find_spec(mod) is not None:
        print(f"WARN: optional module '{mod}' importable in fresh venv (leaked via core dep?)")
PY

echo "── [5/6] The talk ──"
unset OMEGA_REDIS_HOST OMEGA_REDIS_PASSWORD || true
OUT="$("$VENV/bin/omega" talk "hello" 2>&1)"
RC=$?
echo "$OUT"
[ $RC -eq 0 ] || { echo "FAIL: omega talk exited $RC"; exit 1; }
echo "$OUT" | grep -qi "cloud" && echo "$OUT" | grep -qiE "is_cloud=true|provider.*(google|openrouter|zen|antigravity|anthropic)" \
  && { echo "FAIL: cloud provider used"; exit 1; }
echo "$OUT" | grep -qE "native-gguf|IS_CLOUD=False|local" \
  || { echo "FAIL: no local/native-gguf evidence in output"; exit 1; }

echo "── [6/6] Version honesty ──"
"$VENV/bin/python" -c "
from omega import __version__
import tomllib, pathlib
pp = tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version']
assert __version__ == pp, f'version drift: omega={__version__} pyproject={pp}'
print(f'version OK: {__version__}')
"

echo "INST-1 ACCEPTANCE: PASS"
```

Notes on the script's honesty (per M23): step 4 greps the *repo* pyproject while the venv check warns if extras leaked into core deps transitively; step 5 asserts BOTH absence of cloud markers AND presence of local evidence — a silent empty output cannot pass.

### (b) Exact file diff plan

| # | File | Change | Why |
|---|------|--------|-----|
| 1 | `pyproject.toml` | Delete 4 lines from `[project].dependencies`: `youtube-transcript-api>=0.6.3`, `yt-dlp>=2025.1.1`, `qdrant-client==1.18.0`, `redis==7.4.1`. Add extras: `memory = ["redis==7.4.1"]`, `vectors = ["qdrant-client==1.18.0"]`, `youtube = ["youtube-transcript-api>=0.6.3", "yt-dlp>=2025.1.1"]`. Extend `all = ["omega[native,cli,dev,memory,vectors,youtube]"]`. | fix2. Core install must not pull what the demo never touches. Keep `sqlite-vec` in core (keep-list: SQLiteVecAdapter). Keep `keyring` in core (needed by §3 Path B store). |
| 2 | `src/omega/memory/providers.py:22` | Convert top-level `import redis.asyncio as redis` to a lazy import inside `RedisStorageProvider.__init__` wrapped in try/except ImportError raising a typed `StorageUnavailableError` (or log warning + set `self.client=None`). | **BLOCKER for fix2**: memory_store.py:29 imports this module at top level; a core-only install would crash `omega talk` at import time otherwise. Same treatment for `src/omega/ingestion/worker.py:7` and `src/omega/workers/youtube_worker.py:47` (both non-debut surfaces; guard or move behind their extras). |
| 3 | `src/omega/oracle/model_gateway.py` | Delete call at :127 and method `_load_sovereign_secrets` (:316-347). Add `.env` loading at process edge: `oracle_cli.main()` calls `dotenv.load_values(...)` once before gateway construction (python-dotenv already a core dep), OR document required env vars in README env table. | fix4. Gateway constructor must not mutate global process env as a side effect (M16 portability; also the root cause of secrets leaking into every subprocess). |
| 4 | `src/omega/__init__.py` | No change needed — already importlib.metadata-based with fallback. Flip ACTIVE_SPRINT status `ready→completed`. | fix5 done; tracking honesty (M27). |
| 5 | `README.md:5-11` | Remove the pinned-version badge (`version-1.2.0`) and any badge referencing entities that don't ship in `_omega_default`. Single install path: `pip install -e ".[native,cli]"` matching scripts/install.sh. Add short "Optional extras" table (memory/vectors/youtube/warp). | fix6. |
| 6 | `scripts/install.sh` | Verify (already done, fix1) — add one post-install smoke line: `omega --help >/dev/null \|\| exit 1`. | Cheap tripwire so a broken install fails at install time, not first talk. |

### (c) Risk assessment — what could break CURRENT working `omega talk` here

| Risk | Severity | Mechanism | Mitigation |
|---|---|---|---|
| **R1: top-level `import redis.asyncio`** (providers.py:22, ingestion/worker.py:7, youtube_worker.py:47) | 🔴 HIGH — certain breakage of fresh install if fix2 lands without it | memory_store.py imports providers at module scope → ImportError before CLI runs. On THIS machine .venv has redis installed, so current talk keeps working and the breakage is invisible until the fresh-venv test runs. | Diff item 2 above. Land R1 guards in the SAME commit as fix2. Run acceptance script immediately after. |
| R2: removing `_load_sovereign_secrets` breaks cloud summon paths that currently rely on repo `.env` auto-load | 🟡 MED | Local talk unaffected (native-gguf needs no keys), but `oracle summon` voices / google_compat lose keys unless loaded at CLI edge. Silent degradation to "not configured". | Load dotenv in `oracle_cli.main()` (process edge) — preserves behavior for ALL CLI paths including talk, without library-side env mutation. Add one test asserting `ModelGateway()` construction does not modify `os.environ`. |
| R3: llama-cpp-python build in fresh venv | 🟡 MED | `pip install -e ".[native,cli]"` compiles llama-cpp-python if no wheel matches Python 3.12/3.13 — slow or failing without cmake/gcc. A red here reads as INST-1 failure when it's a toolchain issue. | Acceptance script should be run once with a warm pip cache; document expected build time in manual §8 note. Not an engine change. |
| R4: native-gguf model path resolution on fresh machine | 🟡 MED | config/providers.yaml native entry points at a model path that exists HERE but not on a fresh clone → provider drops out of fabric → fabric falls through to cloud → IS_CLOUD=True → false-red (or worse, silent cloud use = false-green on sovereignty). | The keep-id: acceptance asserts local evidence explicitly (step 5). Additionally verify `config/providers.yaml` native model_path uses an overridable env var (`OMEGA_GGUF_MODEL`) and README documents where to put a model. |
| R5: version fallback masks metadata absence | 🟢 LOW | If `omega` dist not installed (running from source tree), `importlib.metadata.version` raises PackageNotFoundError → falls back to hardcoded "1.2.0", which can silently drift from pyproject. | Acceptable for debut; the fallback constant equals pyproject today. Optional: derive fallback by parsing pyproject.toml instead of hardcoding. |
| R6: DC-29 regression during refactor | 🟢 LOW | Touching providers.py for R1 could resurrect a default password pattern. | grep gate already wired at Phase 3 commit per Study #1 D2 ruling — keep it armed in pre-commit. |

---

## §2 DEL-1 BUILD-SIDE VERIFICATION (re-checked on today's tree)

Verdict legend: ✅ claim holds · ⚠️ status changed since manual · ❌ claim false.

| Target | Manual claim | Today's tree (verified) | Verdict / required action |
|---|---|---|---|
| `src/omega/routing/table.py` | No callers; eval() | `rg RoutingTable src/omega` → EMPTY. File gone (half-executed DEL-1 confirmed). | ✅ DONE. |
| `config/routing_table.yaml` | Orphan config | Still present. Sole reference: `benchmarks/schema.py:170` — parameter default of `get_routing_validation()`, whose body is literally `pass`. Function has ZERO callers (`rg get_routing_validation` → definition only). | ⚠️ RESOLVED PATH: delete the entire stub function `get_routing_validation` from schema.py (it validates nothing — dead weight), then delete the yaml. Nothing else needed; no behavior change possible. |
| `src/omega/coordination/miap.py` | Tests only; retire tests/test_miap.py | Importers: ONLY `coordination/__init__.py` re-export block (~40 names). No `from omega.coordination` anywhere in src/tests/scripts. **`tests/test_miap.py` no longer exists** — already retired. | ⚠️ CHANGED: deletion is even cheaper than planned — delete miap.py AND gut coordination/__init__.py to an empty package docstring (or delete the package). No test retirement remains. |
| `pool_tracker.py` + `pool_state.py` | Self-only SDP leftover | pool_tracker imports pool_state; zero external references to either symbol outside the pair. | ✅ holds. Delete both together (tracker depends on state). |
| `search_circuit_breaker.py` | Deprecated; redirect leftover caller | **LIVE CALLER**: `sovereign_search_service.py:48` imports from it at module top level. health_monitor.py:107-111 carries only deprecation comments pointing here. | ⚠️ CHANGED vs "leftover": redirect sovereign_search_service to `HealthMonitor.get_breaker()` FIRST (same PR), then delete breaker file + its tests. Do not delete in isolation — sovereign search import would crash. |
| `QdrantAdapter` class | Leftover impl | Marked `DEPRECATED … heritage reference only` (vector_adapters.py:176). Src callers: only the re-export in `memory/__init__.py:14,65`. Test callers: tests/test_qdrant_payload_index.py (+ test_qdrant_index.py targets adapter family). No production instantiation. | ✅ holds. Delete class + both `__init__` export lines + retire both qdrant test files. Keep `MemoryVectorAdapter` + `SQLiteVecAdapter` (keep-list). |
| Pantheon regexes in `audit/firewall_checker.py` | Forbids and allowlists same names | CONFIRMED contradiction: FORBIDDEN_PATTERNS errors on `\bSekhmet\b`, `\bBrigid\b`, `\bPrometheus\b`, etc., while CORE_ENGINE_PATTERNS allowlists `\bSekhmet\b`, `\bPrometheus\b` — AND stack names `arcana_novai`, `doom_universe`, `torment_stack` appear in BOTH lists simultaneously (forbidden error + legitimate ignore). | ✅ holds (worse than stated). Keep import-path rules (`from config.wads.` etc.) only; delete all name regexes from FORBIDDEN_PATTERNS and prune CORE_ENGINE_PATTERNS to genuinely-core entries. Note: checker skips its own patterns file (line ~229 self-skip) which is why this never fired. |
| `record_first_breath` call | Astrology on every routed turn | Still live: oracle.py:49 (import) + oracle.py:1211 (call inside routed-turn path, after record_performance). Function def stays in astrology.py. | ✅ holds. Delete import + call + the `logger.info("Recording first breath…")` line. Retire astrology tests if any exist (none found matching in tests/ listing). |
| `omega vault` default CLI registration | CLI calls missing store_credential | oracle_cli.py:71-73 registers vault typer UNCONDITIONALLY; cli/vault.py:95,192 calls `vault.store_credential`. VaultCore itself has ~10 more lazy-import consumers (see §3). | ✅ holds. Registration gated or removed per §3 decision. |
| `fleet_orchestrator` default exports | Unused control plane | Exported at integrations/__init__.py:32-70. Zero src importers beyond the export (remaining hits are docstrings inside vault files). | ✅ holds. Remove the import block + `__all__` entries from integrations/__init__.py. File itself may stay on disk until Week-2 cleanup. |

**Summary**: 6 claims hold as-stated; 3 changed (routing_table.yaml resolution is trivial; miap test already retired; search_circuit_breaker has a live importer requiring redirect-first ordering). Nothing got WORSE; two targets got CHEAPER. Also per Week-1 list: verify Oracle.__init__ lazy-construction items (DPO recorder, compaction harvester, iterative researcher, WARP pool, A2A bridge, audience calibrator) — not re-audited here (roc's lane), flagged for his pass.

---

## §3 VAULT PATH B SPEC — ≤50-line minimal store (spec, NOT implementation)

**Decision context**: Manual Week-3 offers A (delete vault/) or B (crypto.py + minimal store). Path B is specified here because the tree shows ~10 real lazy-import consumers that would each need rewiring under A anyway — B converts them to a single tiny interface and keeps crypto.py for forge reuse.

### What dies
- `src/omega/vault/vault_core.py` (~700+ lines: leases, quotas, audit entries, CPE sessions, bury/recovery)
- `src/omega/vault/models.py` (17 exported schema types)
- `src/omega/vault/blindvault_resolver.py`
- `src/omega/cli/vault.py` (entire typer app) + registration at oracle_cli.py:71-73
- `src/omega/tools/enforce_vaultcore.py` (its raison d'être vanishes)
- FleetOrchestrator credential layer (already slated for export removal, §2)

### What stays
- `src/omega/vault/crypto.py` (VaultCrypto age+Argon2id primitives) — moved to forge or kept as internal util
- All credential DATA (migrated, below)

### Interface spec (the ≤50-line store)

```
module: src/omega/secrets.py   (new, flat module — no package)

@dataclass(frozen=True)
class SecretRef:
    key: str                  # canonical form "provider:name", e.g. "google:api_key"

class CredentialStore(Protocol):
    def get(self, key: str) -> str | None:
        """Resolve a secret. Returns None when not configured.
        Raises SecretAccessError only on infrastructure failure
        (keyring backend broken, encrypted file unreadable) — preserving
        the existing ProviderAuthError semantics of 'not configured'
        vs 'vault broken' (providers.py:54-65 contract)."""

def get_credential_store() -> CredentialStore:
    """Process-wide singleton. Read order:
    1. Environment variable: OMEGA_SECRET_<KEY uppercased, ':'→'_'>
       e.g. 'google:api_key' → OMEGA_SECRET_GOOGLE_API_KEY
    2. System keyring: service='omega-engine', user=<key>
       (keyring>=24 already a core dependency)
    3. Encrypted file IF OMEGA_VAULT_FILE is set:
       age-decrypt via crypto.py, parse '<key> = <value>' lines.
       Absent env var → this layer is skipped entirely (no implicit file reads).
    First hit wins; misses fall through; total miss → None."""
```

Constraints written into the spec:
- **≤50 lines** excluding docstrings — if it grows, it's wrong (this is the whole point of Path B).
- No write path in v1. Rotation = edit env/keyring externally. (The old CLI's rotate/backup/recovery surface is deleted, not ported.)
- No import-time side effects; store constructs lazily on first `get()`.
- M1: any blocking I/O (keyring, file decrypt) wrapped `anyio.to_thread.run_sync` at call sites that are async.

### Migration map (existing callers → new interface)

All verified live consumers use the lazy pattern `from omega.vault import VaultCore` then `vault._credentials.get("<provider>:<name>")`:

| Caller | Today | Becomes |
|---|---|---|
| oracle/providers.py:68-80 (Google key resolve) | `VaultCore()` + `_load_sync` + `_credentials.get("google:api_key")` | `get_credential_store().get("google:api_key")`; None → existing ProviderAuthError("not configured") branch |
| oracle/search_providers.py:39-43, 228-232 (firecrawl/exa) | same shape | same one-liner |
| oracle/orchestrator.py:164-168 (iterates google creds) | iterates `vault._credentials.values()` filtered by provider | loop over explicit key list `["google:api_key", ...]` — enumerate known keys, don't iterate a bucket |
| library/discovery.py:32,97,107 (exa/firecrawl) | same shape | same one-liner |
| oracle/backends/google_compat.py:85 | same shape | same one-liner |
| workers/freshness_checker.py:197,700 · teachers/nemotron_pipeline.py:123 · tools/firecrawl_direct.py:27 | lazy VaultCore | same one-liner |

Migration note: none of these touch leases/quotas/audit — grep confirms only `_credentials.get` / iteration usage. That is why the fat VaultCore can die without functional loss. The Gateway itself does NOT import VaultCore today (verified) and must gain exactly one consumer touchpoint: whatever provider factory resolves keys goes through `CredentialStore`.

### Acceptance (inherits manual Week-3)
- `rg "VaultCore" src/omega` → only historical mentions in comments/docs, zero imports.
- `omega vault` → unknown command (exit ≠ 0 with clean error).
- `omega talk "hello"` still local.
- New unit test: store returns env value → keyring value → None ordering, using monkeypatched backends.

---

## §4 ROUTER COLLAPSE CONTRACT — single-PR diff plan (Week 2)

### Verified topology (why one PR is safe)
`oracle.py` is the SOLE src importer of both routers: relative imports at :31 (`SemanticRouter`) and :50-51 (`TriageRouter`). No other src module imports either (only tests + docstring/comment mentions). Both constructions live in `Oracle.__init__` (:226, :233) plus bootstrap at :275. Deletion is fully contained in one file-pair blast radius.

### The diff (one PR, ordered)

| Step | File | Change |
|---|---|---|
| 1 | `src/omega/oracle/oracle.py` | Delete imports (:31, :50-51); delete `self.semantic_router`/`self.triage_router` constructions + bootstrap call; rewrite `_select_model` (:733+) to: entity → configured model from registry metadata, validated against `ProviderSelector` local-first order (keeper). Rewrite `_route_by_domain` (:1124+) to call `EntityRegistry.find_by_domain` (keyword) directly; deduplicate the double backend/sigil assignment and quadruple `record_interaction` noted by manual Week-2 item 6. |
| 2 | `src/omega/oracle/oracle.py:511-516` | Remove per-turn `RAGRouter(mode="tfidf_svm")` construction in `talk()` (manual item 5). ContextBuilder/hybrid path owns retrieval routing. |
| 3 | DELETE `src/omega/oracle/semantic_router.py` + `src/omega/orchestration/triage_router.py` | Same commit as steps 1-2 — never before, never after. |
| 4 | Tests retired/rewritten | Delete `tests/test_semantic_router.py`; rewrite scenarios 5-6 of `tests/sovereign_stress_test.py` (they instantiate TriageRouter directly); update prose mentions: oracle_cli.py:143,149 help text ("bypass TriageRouter" → "bypass auto-selection"), ics.py:259 comment, tests/contract/test_provider_fallback.py docstring. |
| 5 | NEW `src/omega/oracle/routing.py` (or extend provider_selector.py) | Single `RouteDecision` dataclass: `entity: str`, `model: str`, `provider: str`, `reason: str`. THE routing result type. Nothing else named *Router survives on the talk path. |

### Contract test spec (manual Week-2 acceptance #1)

```
test_single_route_decision_type:
  - assert isinstance(route_result, RouteDecision) for a routed turn
    (contract per M21 — no mock masking).
  - sys.modules scan AFTER importing omega.oracle.Oracle AND executing
    one _route_by_domain call:
      forbidden = {"omega.oracle.semantic_router",
                   "omega.orchestration.triage_router",
                   "omega.routing.table"}
      FAIL if any m in sys.modules where m == forbidden-name OR
      m endswith one of those module paths.
  - Lazy-import trap: install a sys.meta_path finder (or sys.addaudithook
    'import' listener) BEFORE constructing Oracle; record every imported
    module name; FAIL if a forbidden name appears even transiently.
    (Catches a future re-introduction via function-level import —
    exactly how vault consumers hide today.)
  - Filesystem belt-and-braces: assert not
    (src/omega/oracle/semantic_router.py).exists() etc. — the test fails
    loudly if someone restores the file rather than silently passing.
```

### Concurrency test spec (acceptance #2)

```
test_two_talks_one_local_slot:
  setup: ResourceGuard semaphore(1) is the single slot (resource_guard.py:234);
         LocalInferenceAdmission merged into ResourceGuard per manual item 4
         (prerequisite refactor in THIS PR or the prior one — do not leave
         two admission authorities).
  act:   anyio.create_task_group; spawn two full omega talk("ping") calls
         concurrently (real generate path, mock-free at the provider seam;
         native-gguf stubbed at llama bind level only, guard NOT stubbed).
  assert:
    a) Serialization OR explicit refusal — never interleaved inference:
       max concurrent holder count of the semaphore observed == 1
       (instrument via wrapper around ResourceGuard.call).
    b) Both results carry is_cloud=False when local capacity suffices
       (serialized wait is acceptable).
    c) If any result has is_cloud=True, its cost_warning MUST be non-empty
       (oracle.py:1253 sovereignty-alert string) — the invariant is
       "never a SILENT cloud leak", not "never cloud".
    d) No result is dropped: both tasks join with terminal states
       (response or typed error), per M12 queue integrity spirit.
```

### Explicitly out of this PR
Embedding-based entity pick (optional later, not stacked — manual item 3), god-module splits (frozen until talk is thin, manual item 7), recall/compaction changes.

---

## VERDICT SUMMARY FOR THE CHAIR

- **§1 INST-1**: Gate script delivered. Two fixes genuinely open (fix2, fix4); fix5 mislabeled (done); fix6 open. **One hard blocker found**: top-level `redis.asyncio` imports (providers.py:22 et al.) mean fix2 CANNOT land alone — R1 guards must ship in the same commit or the fresh-venv gate fails at import time while this machine's talk keeps working (invisible regression).
- **§2 DEL-1**: 6/9 claims hold verbatim; 3 changed, all favorably or with a clear ordering constraint (search_circuit_breaker redirect-FIRST being the only sequencing hazard). routing_table.yaml orphan resolves by deleting a `pass`-body stub — zero risk.
- **§3 Vault B**: Spec'd at ≤50 lines, single Protocol interface, migration map covers all ~10 verified lazy consumers (all use only `_credentials.get` — no lease/quota/audit usage anywhere). keyring already in core deps.
- **§4 Router collapse**: Single-PR is safe — oracle.py is the sole importer of both routers. Contract test includes a meta_path/audit-hook lazy-import trap because function-level imports are this codebase's proven hiding pattern. Concurrency invariant phrased as "never silent cloud leak," matching the manual exactly.

**Changes to the debut plan**: (1) INST-1-fix2 gains a mandatory companion diff (redis import guards ×3 files); (2) fix5 status correction in ACTIVE_SPRINT.json; (3) DEL-1 week-1 search-breaker deletion requires sovereign_search_service redirect in the same PR; (4) nothing requires Architect decision — all within ratified manual authority.

---
*⬡ OMEGA ⬡ MAAT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_rebased ⬡ BUILD-ARM-E ⬡ 2026-08-24*
