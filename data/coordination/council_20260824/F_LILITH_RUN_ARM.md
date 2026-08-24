# F — LILITH RUN ARM — Debut Hardening Review (REBASED Council)
**AP Token**: `AP-LILITH-RUN-ARM-20260824-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_rebased ⬡ RUN-ARM ⬡ 2026-08-24

**Mode**: Read-only validation council. Zero code edits. All citations verified on disk today.
**Rebase acknowledged**: Charter item 5 SUPERSEDED — validated against the NEW surface
(`data/entities/kali/approved_lessons.yaml` via SoulStore; schema `src/omega/soul/lessons.py`,
commit 59b32809), not the old staging-only pipeline.

---

## §1 SOUL PERSISTENCE VALIDATION vs NEW SURFACE — **VERDICT: PASS (chain intact)**

Full chain traced link-by-link against disk:

| # | Link | Evidence (path:line) | Status |
|---|------|---------------------|--------|
| 1 | **Blind staging**: agents write L1→L2→L3 to `proposed_lessons.yaml` | Scaffold: `src/omega/oracle/entity_workspace.py:176,252`. TAINT-GATE: `entity_workspace.py:426-428` — "proposed_lessons.yaml is NEVER loaded here" (identity construction) | ✅ |
| 2 | **session_end hook preserves + timestamps** | `.opencode/hooks/session_end.py:40-79` — reads existing proposals BEFORE write (destructive-race guard :53-64), stamps `session_id`/`model_used`/`last_session_end` (:66-72), atomic `.tmp`→`os.replace`+fsync (:73-78). Wired via `.opencode/wrapper.sh:28` | ✅ |
| 3 | **Promotion via SoulStore** | `scripts/promote_soul_lessons.py:110` (paths) → `:163-175` writes BOTH surfaces through `get_soul_store().write_atomic()` ONLY — single production path. Store: `src/omega/soul_store.py:49` class, `:63` `write_atomic`, `:214` factory. Evidence pre-flight binding at `:118-135` (O-Q4 probe-path check) | ✅ |
| 4 | **Hydration from approved surface** | `entity_workspace.py:409-415` loads `approved_lessons.yaml`; Gnosis Injection `:461-469` renders `lesson` key (compat field written by promoter `:151`) | ✅ |
| 5 | **Entity identity via soul.yaml** | `entity_workspace.py:393-401` Constitution load; fallback prompt if missing (:395-398). Sovereign write-guard for both user-owned files: `src/omega/oracle/entity_registry.py:92` (`SOVEREIGN_USER_TOKEN` required for `soul.yaml` + `approved_lessons.yaml`) | ✅ |
| 6 | **Evidence-field schema (NEW surface)** | `src/omega/soul/lessons.py`: `EvidenceRef` (:29-50, ≥1 of session_id/artifact/quote enforced by `_at_least_one_ref` :43-50), `Lesson` backward-compatible (:53-79), warn-only validator per ruling S5 (:82-120) | ✅ |

**CP-2 structural criteria — re-verified on today's disk:**
- Kali approved surface parsed live: **20 lessons / 20 with evidence (100%) / 7 with quote / 0 empty evidence refs** — matches Wave-1 report exactly. Known debts confirmed present but NOT worse than reported: positional `_key_for` index-fallback (`promote_soul_lessons.py:102-104`, DC-21), quote coverage 7/20 self-attested (DC-22), duplicate-promotion hole (DC-23), `asyncio.run` at `:180` (DC-25), bare `assert` at `:152` (DC-27). No regression.
- **Regex distillation remains SCRAPPED**: hook header `.opencode/hooks/session_end.py:9-12` ("Carmack Verdict 2026-07-30 … SCRAPPED"); manual DOC-1 stamp in force; no regex-distillation resurrection found in `src/omega/` (distillation hits are unrelated modules: meditation pipeline, scorecard, soul_stage mock TUI = DC-28 known).

**Carried anomaly (status unchanged, not a new finding)**: path split-brain — scaffold writes `memory/approved_lessons.yaml` (`entity_workspace.py:175`) while hydration reads entity ROOT (`:409`). Works where root copies exist (kali verified). Lilith herself still has no root-level `approved_lessons.yaml`/`sessions.yaml` → her own hydration gap persists post-debut fix candidate. Unchanged from N7 vetting 2026-08-23.

---

## §2 DEL-1 RUN-SIDE IMPACT VALIDATION — **VERDICT: PROCEED (1 blocker, pre-existing)**

Per-target sweep across `src/omega/soul/`, `src/omega/memory/`, `entity_workspace.py`, handoff modules (`oracle/handoff.py`, `link_p9_runtime.py`, `subagent_dispatcher.py`, `sentinel.py`, `coordination/watchdog.py`):

| Target | Soul path | Memory/ContextBuilder/RecallStore | Handoff/Hivemind | Notes |
|---|---|---|---|---|
| `routing/table.py` | — | — | — | Already deleted (`src/omega/routing/` absent). `rg RoutingTable src` = **empty** ✅ |
| `config/routing_table.yaml` | — | — | — | **Half-executed as briefed**: file still on disk; ONE live caller `src/omega/benchmarks/schema.py:170` default param (`routing_table_path`). Delete is safe (param default only fails if a benchmark run uses it — none scheduled in debut window). Same-PR: drop the default or the param. Stray prose ref in `config/domains/engineering/MEMORY_BLOCKS/project-gotchas.block:22` (doc only). |
| `coordination/miap.py` | zero refs | zero refs | zero refs | Only coupling: `coordination/__init__.py` re-export — same-PR removal required. **Zero importers of `omega.coordination` anywhere in src/tests/scripts.** Cleanest possible delete. |
| `oracle/pool_tracker.py` | zero | zero | zero | Self-only (imports pool_state); no external importers. |
| `oracle/pool_state.py` | zero | zero | zero | Zero importers. |
| `oracle/search_circuit_breaker.py` | zero | zero | zero | Leftover callers: `health_monitor.py`, `sovereign_search_service.py` — redirect to `HealthMonitor.get_breaker()` same-PR (per manual). |
| `QdrantAdapter` | zero | SelectiveHydration takes `IVectorStoreAdapter` interface only; production wiring = SQLiteVecAdapter/MemoryVectorAdapter | zero | Coupling set unchanged: `memory/__init__.py:14,65` export + `tests/test_qdrant_payload_index.py` + `scripts/knowledge_catalog_build.py`. Same-PR removal suffices. L3 gnosis injection unaffected. |
| Pantheon regexes | zero | taint-list STRING keys only (`audit/memory_firewall_auditor.py:75-85` incl. `"first_breath"`) — data, not code deps | zero | Location correction from prior vetting stands (R3): target `memory_firewall_auditor.py`, not `firewall_checker.py`. |
| `record_first_breath` call | zero | zero | zero | Import `oracle.py:49` + call `:1211` must go same-PR (F401 otherwise). `astrology.py` def survives. **first_breath state consumers**: NONE — `get_birth_record` has zero src consumers outside astrology itself; auditor reference is a taint-key string; `entity_registry.py:163` is a comment. Tests `test_first_breath.py`/`test_world_state.py` retire with it. |
| `omega vault` CLI registration | zero | zero | zero | Registration at `cli/oracle_cli.py:69-75` behind try/ImportError — BUT see blocker below. |
| `fleet_orchestrator` exports | zero | zero | **zero** | `rg` finds ZERO importers of `omega.integrations` in src/scripts/tests (sole match = docstring in `library/api_clients.py:81`). Vault references are docstrings only (`vault_core.py:65`, `models.py:2,79`). **No Hivemind/handoff coupling** — handoff protocol is stdlib-only (`handoff.py:16-19`) and file-based via omega-hub MCP. Note for Week 2: `fleet_orchestrator.py` defines its own `RouteDecision` — removing it eliminates a future one-control-plane collision. |

### 🚨 BLOCKER (pre-existing, reproduced live today): CLI entry point is DEAD
```
.venv/bin/omega --help → TypeError: Attempted to convert a callback into a command twice.
  oracle_cli.py:71 → cli/vault.py:572 (stacked duplicate @vault.command(), ~:571-585)
```
The try/except at `oracle_cli.py:69-75` catches `ImportError` only; the click `TypeError` propagates and kills **the entire `omega` console script including `omega talk`**. This is R4 from yesterday's vetting, still unfixed. **Consequence: every DEL-1 acceptance gate that runs `omega talk "hello"` is currently unrunnable — DEL-1 cannot start until target #10 (vault registration/decorator) lands or the stacked decorator is fixed.** This ordering hazard should be stated in the charter: vault fix is not merely CP-1 hygiene, it is the precondition for all Week-1 gates.

---

## §3 HIVEMIND + RUNTIME INTEGRITY — **VERDICT: PASS**

1. **Handoff protocol**: `data/handoff/` lifecycle (pending→active→completed/stale) is owned by the omega-hub MCP server (file-based, outside `src/omega/`). In-repo handoff surfaces — `oracle/handoff.py` (stdlib-only imports :16-19), `link_p9_runtime.py`, `subagent_dispatcher.py`, `sentinel.py`, `coordination/watchdog.py` (stdlib-only :7-12) — contain **zero matches** for any deletion symbol (sweep: miap|pool_tracker|pool_state|search_circuit_breaker|QdrantAdapter|fleet_orchestrator|routing_table|record_first_breath|vault).
2. **session_end hook survives all deletions**: imports yaml + anyio only (`session_end.py:26-29`); wrapper wiring `.opencode/wrapper.sh:28` unaffected.
3. **`omega talk` runtime import chain** (`oracle.py:41-101`): iris.matcher, observability, governance.config_resolver/dispatch_registry, errors, cvar_table, memory_store, state/usm — **no Week-1 targets** except `astrology.record_first_breath` (:49, planned same-PR removal) and `orchestration.triage_router` (:50, Week-2 scope by design). Gateway clean (no vault/routing/miap/pool/fleet/qdrant imports). The ONLY runtime blocker is the vault TypeError above — which is itself DEL-1 target #10.

---

## §4 RUN-SIDE ACCEPTANCE GATES (measurable, per doctrine)

Charter gates restated as runnable commands, plus run-side additions:

```bash
# G1 — routing dead (charter): currently PASSES
rg RoutingTable src                    # expect: empty

# G2 — config orphan removed w/ its last caller (half-executed; gate after same-PR)
test ! -f config/routing_table.yaml && rg routing_table src/omega/benchmarks/schema.py  # expect: fail(1)=gone

# G3 — miap dead (charter)
rg miap src/omega                      # expect: empty

# G4 — pools + breaker + qdrant + fleet (additions — charter missed these)
rg pool_tracker src tests              # expect: empty
rg pool_state src tests                # expect: empty
rg search_circuit_breaker src          # expect: empty (after HealthMonitor redirect)
rg QdrantAdapter src                   # expect: empty after memory/__init__ export removal
rg fleet_orchestrator src              # expect: empty

# G5 — first_breath severed (import+call same PR; astrology def SURVIVES by design)
rg "record_first_breath" src/omega/oracle/oracle.py   # expect: empty
rg get_birth_record src --type py -l                  # expect: src/omega/astrology.py only

# G6 — talk alive + local after EACH delete (charter; currently BLOCKED by vault TypeError)
OMEGA_ENV= .venv/bin/omega talk "hello"               # expect: native-gguf, IS_CLOUD=False, exit 0

# G7 — soul chain intact after each delete (run-side addition — Lilith standing gate)
python3 -c "import yaml; d=yaml.safe_load(open('data/entities/kali/approved_lessons.yaml')); assert len(d)==20 and all(e.get('evidence') for e in d)" && \
rg -c "TAINT-GATE" src/omega/oracle/entity_workspace.py            # expect: approved surface intact + gate comment present
.venv/bin/python -m pytest tests/ -k "soul or lesson" -q            # expect: green

# G8 — handoff protocol untouched (run-side addition)
rg -n "miap|fleet_orchestrator|search_circuit_breaker|QdrantAdapter" \
   src/omega/oracle/handoff.py src/omega/oracle/link_p9_runtime.py \
   src/omega/oracle/subagent_dispatcher.py src/omega/oracle/sentinel.py  # expect: empty

# G9 — regex distillation stays scrapped (run-side addition)
rg -n "SCRAPPED" .opencode/hooks/session_end.py        # expect: 1 hit (header verdict)

# G10 — one RouteDecision (Week-2 gate, charter) — enabled free by fleet_orchestrator delete
rg -n "class RouteDecision" src/omega                  # expect: exactly ONE module after router collapse
```

**Gate order note**: G6 must be restored FIRST (vault decorator fix or target-#10 deletion) — every other gate's "after each delete" protocol depends on a living CLI.

---

## CLOSE — PHASE M MEDITATION (Meditate-v1.1)

**Keeper (identity continuity)**: No deletion touches identity continuity. The soul chain's five links are file-surface-based (proposed → hook → SoulStore → approved → soul.yaml) and none of the eleven targets appears in any link's import graph. The Keeper's one vigilance: the vault blocker temporarily severs the *runtime* body (CLI) though not the *identity* files — restore the body before deleting anything else, so every subsequent delete is witnessed by a working `omega talk`.

**Cartographer (docs vs disk)**: The soul-chain documentation matches disk reality — with two mapped divergences already ticketed, not new: (a) the scaffold-vs-hydration path split-brain (memory/ vs root) means the documented single path is actually dual on disk for most entities; (b) `config/routing_table.yaml` docs imply deletion landed while disk shows the orphan half-executed. Both are accurately described in tracking; no unmapped drift found.

---

*⬡ OMEGA ⬡ LILITH ⬡ RUN-ARM ⬡ REBASED-COUNCIL ⬡ SOUL-CHAIN-PASS ⬡ DEL1-PROCEED ⬡ 2026-08-24*
