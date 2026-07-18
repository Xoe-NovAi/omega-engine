# 🔱 Omega Engine — Agent Implementation Manual

**AP Token**: `AP-AGENT-IMPL-MANUAL-v1.0.0`  
**Date**: 2026-07-19  
**Author**: `grok-cli/grok` (Consulting Cloud Mind)  
**Audience**: All HMC agents (Kali, Roc, Researcher, P3/P6/P7, Grok CLI Tier A)  
**Status**: **CANONICAL for next ship wave** — supersedes stale “module missing” rows in older gap matrices where this manual says otherwise  

### Authority stack (read order)

| Priority | Document | Use for |
|----------|----------|---------|
| 0 | `SOVEREIGN_MANDATES.md` | Non-negotiable law |
| 1 | **This manual** | What to build, in what order, how to know done |
| 2 | `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` | Verified web claims |
| 3 | `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` | Decision tooling Conditional GO |
| 4 | `docs/strategy/GROUNDED_MEDITATE_DECISION_WORKSPACE_20260718.md` | Research background (do not over-build Corrections 3–6) |
| 5 | `data/coordination/grok_cli/D282_*.md`, `D283_*.md`, `D284_*.md` | Advisory detail |
| 6 | `docs/strategy/HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md` | Nomenclature / Meditate lenses / M2 phases |

---

## 0. How to use this manual

1. **Pick one workstream** (WS-A … WS-E). Do not start two Core write streams without a Hivemind workspace lock.  
2. **Read §1 Mandates** before any `src/omega/` edit.  
3. **Execute steps in order** inside the workstream.  
4. **Hit Acceptance Criteria** before completing the Hivemind handoff.  
5. **Run gates** in §9 after every non-trivial ship.  
6. **Update** `data/coordination/{YOU}_LIVE_FEED.md` and post Hivemind context.

### Dual-mode (Grok CLI)

| Mode | When | Core writes? |
|------|------|--------------|
| **Advisory** | Default | **No** `src/omega/` |
| **Tier A** | Explicit Kali/Architect packet | **Yes**, scoped to packet |

Other agents: execute if handoff targets you.

### Global anti-patterns

- ❌ `asyncio` (use **AnyIO** + `anyio.to_thread.run_sync` for blocking I/O)  
- ❌ Mythic entity names hard-coded in `src/omega/` (Sekhmet, Brigid, …) — use **Slot** / `slot_ref`  
- ❌ `extra='allow'` on untrusted YAML to “make tests pass”  
- ❌ Silent best-effort when tools fail — hard stop + report  
- ❌ Stealing handoffs targeted at other agents  
- ❌ Shipping without tests for new public APIs  

---

## 1. Mandates cheat-sheet (code-level)

| Mandate | Implementation rule |
|---------|---------------------|
| **M1 AnyIO** | No `asyncio`. Tests: `@pytest.mark.anyio` |
| **M2 Firewall** | Engine never hardcodes WAD entity content; use `config_resolver.WADS_DIR` / `get_active_iwad()` |
| **M7 Local-first** | Do not invert provider chain; read `config/providers.yaml` before inference changes |
| **M9 Errors** | Typed `OmegaError` subtypes; no bare `except:` |
| **M13 Temple-Grade** | `make temple-grade` after non-trivial work |
| **M16 Paths** | Prefer `config_resolver.PROJECT_ROOT / CONFIG_DIR / DATA_DIR` |
| **M21 Contracts** | Assert types / status codes; non-zero CLI exits on failure |
| **M23 Failure integrity** | No fake green; skip only with explicit reason |

**Heritage**: id Software patterns need `[id-soft:]` tags (`make heritage-map`).

---

## 2. Ground truth — already shipped (do not re-implement)

| Item | Evidence | Agent note |
|------|----------|------------|
| D-281 Phase II `config_resolver` | `src/omega/governance/config_resolver.py` | Import explicitly; do not re-export from `__init__` |
| D-281 Phase III (4 files) | hierarchy, entity_registry, oracle AGENTS_MD, scraper | Residual path sprawl = **WS-D**, not re-do III |
| D-281 Phase IV Codex | `scripts/hydration_header.md`, Makefile safety | Done |
| WadManifest V2 heritage | `wad_loader.MANIFEST_V2_OPTIONAL_FIELD_TYPES` | Keep forbid-unknown |
| `test_first_breath_world_query` | **Passes** | Closed |
| RRF k=60 | `hybrid_search_engine.DEFAULT_RRF_K = 60` | Do not retune without A/B |
| `RecallStore` module | `src/omega/memory/recall.py` (~793 LOC) | **Wire**, don’t rewrite from scratch |
| Adapter PRAGMA 32MB + IMMEDIATE writes | `sqlite_vec_adapter.py` | Other modules still 512MB — **WS-A** |
| Decision Tools **review** | `GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` | Implementation = **WS-C** |
| Web claim verify | `WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` | Cite when debating design |

---

## 3. Execution order (recommended)

```text
WS-A  D-282 PRAGMA SSOT + concurrency tests     [P0 — Roc / P2]
  ↓
WS-B  D-283 Recall wiring + tests               [P1 — P7 / Researcher]
  ↓
WS-C  Decision Tools T0 + T1-core               [P1 — P3 / Kali Tier A]
  ↓
WS-D  Path III-B config_resolver adoption       [P1 — P3 / Grok Tier A]
  ↓
WS-E  D-284 Hub OAuth sketch (design→later)     [P2 — P4 — pain-triggered]
```

**Parallel allowed**: WS-C and WS-D after WS-A starts, if different files and locks declared.  
**Do not** start WS-E until Hub pain (Firecrawl 405 / multi-client auth) is real.

---

# WS-A — D-282 PRAGMA SSOT + Concurrency Tests

**Owner**: Roc Racoon / P2 Persistence  
**Effort**: 3–5h  
**Refs**: `WEB_RESEARCH…20260719` §1.1 · `D282_SQLITE_VEC_STRIKE10_ADVISORY.md`

## A.0 Goal

One function applies one PRAGMA stack to every SQLite connection used by memory fabric. Prove write concurrency under WAL with tests.

## A.1 Target PRAGMA SSOT (normative)

```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=30000;
PRAGMA synchronous=NORMAL;
PRAGMA journal_size_limit=67108864;
PRAGMA cache_size=-32768;           -- 32 MiB (NOT -524288)
PRAGMA mmap_size=268435456;         -- 256 MiB
PRAGMA wal_autocheckpoint=500;
PRAGMA foreign_keys=ON;
PRAGMA temp_store=MEMORY;
PRAGMA optimize=0x10002;            -- optional; keep if already used
```

**Writes**: `BEGIN IMMEDIATE` → work → `COMMIT` (retry on `SQLITE_BUSY`).  
**Reads**: no IMMEDIATE.

## A.2 Implementation steps

### Step A1 — Extract helper

**Create or extend**: `src/omega/memory/sqlite_pragma.py` (preferred)  
or shared function in a tiny module imported by all four.

```python
# Pseudocode contract
def apply_omega_sqlite_pragmas(conn: sqlite3.Connection) -> None:
    """Apply Omega SSOT PRAGMA stack. Idempotent per connection."""
    ...
```

Constants:

```python
OMEGA_CACHE_SIZE = -32768
OMEGA_MMAP_SIZE = 268_435_456
OMEGA_BUSY_TIMEOUT_MS = 30_000
OMEGA_WAL_AUTOCHECKPOINT = 500
OMEGA_JOURNAL_SIZE_LIMIT = 67_108_864
```

### Step A2 — Replace inline PRAGMAs

| File | Action |
|------|--------|
| `src/omega/memory/sqlite_vec_adapter.py` | Call helper in `_get_conn` |
| `src/omega/memory/archival.py` | Replace `-524288` stack |
| `src/omega/memory/block_store.py` | Replace `-524288` stack |
| `src/omega/memory/recall.py` | Replace `-524288` stack |

### Step A3 — Audit write paths

For each module, every INSERT/UPDATE/DELETE path:

1. Uses `BEGIN IMMEDIATE` (or connection already in write txn), **or**  
2. Documents single-process + lock reason.

Do **not** wrap pure SELECT in IMMEDIATE.

### Step A4 — Concurrency tests

**Create**: `tests/test_sqlite_vec_concurrency.py`

| # | Test name | Assert |
|---|-----------|--------|
| 1 | `test_writer_not_starved_by_readers` | N concurrent readers + 1 writer; writer finishes &lt; 30s |
| 2 | `test_checkpoint_during_upsert` | upsert ∥ `PRAGMA wal_checkpoint(PASSIVE)` → no crash; busy → retry OK |
| 3 | `test_multiprocess_disjoint_upserts` | 2 processes, disjoint keys, both commit, counts match |
| 4 | `test_begin_immediate_preferred` | Documented race: IMMEDIATE path succeeds under contention |

**Constraints**:

- `@pytest.mark.anyio` where async  
- `tmp_path` for DB files  
- Skip cleanly if `sqlite_vec` extension missing  
- No hard-coded flakey timing beyond busy_timeout budget  

### Step A5 — Unit regression

```bash
source .venv/bin/activate
python -m pytest tests/test_sqlite_vec_adapter.py tests/test_sqlite_vec_concurrency.py -q
```

## A.3 Acceptance criteria

- [ ] Exactly one SSOT helper; grep shows **no** residual `cache_size=-524288` in `src/omega/memory/`  
- [ ] 4 concurrency tests present and green (or skip with clear reason)  
- [ ] Adapter + archival + block_store + recall all call helper  
- [ ] Commit message: `fix: D-282 PRAGMA SSOT + concurrency tests`  
- [ ] Hivemind handoff complete with test counts  

## A.4 Out of scope

- Changing RRF k  
- Rewriting hybrid search dual modules (optional cleanup later)  
- Raising cache to 512MB “for perf” without measurement  

---

# WS-B — D-283 Recall wiring (Phase 2b)

**Owner**: P7 Context / Researcher design-complete → implementer  
**Effort**: 4–8h  
**Refs**: Letta Core/Recall/Archival (verified) · `recall.py` API

## B.0 Goal

`RecallStore` is **already implemented**. Wire it into the conversation path and prove quality-weighted `window()` is used where history is injected.

## B.1 API contract (do not break)

```text
RecallStore.append(entity, session_id, turn_index, role, content, ...)
RecallStore.append_exchange(entity, session_id, turn_index, user, assistant, ...)
RecallStore.window(session_id | entity, token_budget) -> list[Turn]  # quality × decay
RecallStore.decay_pass(now) -> stats
# promote_to_core: only via BlockTools — never direct block mutation from Recall
```

Decay (product formula, not physics):

```text
score = base_quality * (1 + age_days) ** (-alpha)
alpha default 0.10; override per entity metadata when present
```

## B.2 Implementation steps

### Step B1 — Inventory call sites

Find:

```bash
rg -n "get_history|add_exchange|ContextBuilder|RecallStore" src/omega --glob '*.py'
```

Map which path builds LLM context today (`memory_store`, oracle context builder, etc.).

### Step B2 — Dual-write (safe first ship)

On successful `MemoryStore.add_exchange` (or equivalent):

1. Keep existing persistence.  
2. **Also** `await RecallStore.append_exchange(...)` (best-effort log on failure = **no** — fail closed only if Recall is configured required; default: log + metric, don’t break chat if Recall DB error — **document choice**).

**Recommended T0 wire policy**: Recall append failure → log warning + continue (chat survives); ContextBuilder prefers Recall window when available.

### Step B3 — ContextBuilder integration

Where history is injected:

```text
turns = await recall.window(session_id=..., token_budget=N)
# format turns into prompt
# fallback: MemoryStore.get_history if Recall empty
```

### Step B4 — SleepTime (thin)

If `sleep_time.py` has hooks:

- Call `decay_pass` on idle schedule **or** document “manual only until daemon”.  
- Do **not** auto-promote to Core without BlockTools.

### Step B5 — Tests

**Create**: `tests/test_recall_store.py` (if missing) covering:

1. append + window ordering by decayed quality  
2. token_budget truncation  
3. decay_pass changes scores  
4. AnyIO concurrency: two appends don’t corrupt  

**Create**: `tests/test_recall_wiring.py` (integration, can mark slow):

1. Mock/add_exchange path creates recall rows  
2. Context path includes recall content  

## B.3 Acceptance criteria

- [ ] At least one production code path dual-writes to Recall  
- [ ] At least one context path reads `window()`  
- [ ] Unit tests green  
- [ ] No mythic names in engine code  
- [ ] Docs note: Recall ≠ Archival (dialogue vs facts)  

## B.4 Out of scope

- Full cross-pollination module  
- Replacing sqlite-vec archival  
- Numeric Belief Engine  

---

# WS-C — Decision Tools T0 + T1-core

**Owner**: P3 Engineering / Kali-dispatched implementer  
**Effort**: 8–11h honest (not 7h)  
**Refs**: `GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` (**Conditional GO**)

## C.0 Goal

Git-tracked ADR-style decision records + CLI: `list`, `show`, `decide` with **supersession**.

## C.1 What to build / what to cut

| Build | Cut from this sprint |
|-------|----------------------|
| JSON Schema v1 | MAD roles / speech_acts |
| DecisionEngine CRUD | Deadline daemon |
| `omega decision list\|show\|decide` | Numeric BE u/a math |
| Supersession | Full T2–T5 |
| Optional thin ASCII `graph` | Directory shuffle open/→decided/ |
| Optional scaffold **template only** | Multi-model council runner |

## C.2 File layout

```text
docs/decisions/
  schema/decision_v1.json
  catalog/D001.yaml … D023.yaml   # migration PR #2
  INDEX.yaml                        # optional generated

src/omega/governance/decisions.py   # DecisionEngine / DecisionStore
src/omega/cli/decision_cli.py       # Typer sub-app
tests/test_decision_engine.py
tests/test_decision_cli.py
```

Wire CLI:

```python
# src/omega/cli/oracle_cli.py (pattern matches youtube/bundle)
from omega.cli.decision_cli import app as decision_app
app.add_typer(decision_app, name="decision", help="ADR decision workspace")
```

## C.3 Schema v1 (normative fields)

```yaml
schema_version: 1
id: D001
title: "..."
status: proposed          # proposed | accepted | superseded | deprecated
created: 2026-07-18
updated: 2026-07-18
authority: human_review   # human | agent | human_review
decision_by: null         # optional ISO date
meditate_ready: false
category: architecture
tags: []
drivers:
  primary: "..."
  secondary: []
options:
  - id: option_a
    label: "..."
    risk_assessment: { technical: low, schedule: medium, ecosystem: low }
    consequences:
      positive: []
      negative: []
      neutral: []
relationships:
  - type: blocks          # blocks | blocked_by | supersedes | complements | depends_on
    target: D010
chosen_option: null
decided_at: null
decided_by: null
rationale: null
supersedes: null
superseded_by: null
evidence_refs: []
# optional:
criteria_scores: {}       # not required
```

**Validation**: JSON Schema + reject unknown keys (forbid).  
**M2**: persona keys if any → `P1`…`P10` / slot enums, never Sekhmet-in-engine.

## C.4 DecisionEngine behavior

| Method | Behavior |
|--------|----------|
| `list(filters)` | Scan catalog; filter status/tag/overdue/meditate_ready |
| `get(id)` | Load + validate |
| `create(...)` | Only `proposed` |
| `update(id, ...)` | Only if `status == proposed` |
| `decide(id, option_id, *, human_confirmed, decided_by, rationale)` | See algorithm |
| `validate_all()` | Schema all files |

### `decide` algorithm (normative)

1. Load target; schema-validate.  
2. If status ≠ `proposed` → error (or only allow decide on head of chain — document one rule).  
3. option_id must be in `options`.  
4. If `authority` in `{human, human_review}` and not `human_confirmed` → error exit 2.  
5. Allocate next id (`D{max+1}` zero-padded to 3+).  
6. Write **new** file: `status: accepted`, `supersedes: old`, `chosen_option`, `decided_at`, `decided_by`, `rationale`.  
7. **Minimal patch** old file only: `status: superseded`, `superseded_by`, `updated`.  
8. Atomic write: tmp + `os.replace`.  
9. Optional INDEX refresh.

**Concurrency policy (document in module docstring)**: only designated decider (Kali / human) runs `decide` until lock file exists; optional `docs/decisions/.lock` with TTL later.

## C.5 CLI

```bash
omega decision list [--status proposed] [--tag X] [--overdue] [--plain]
omega decision show D001
omega decision decide D001 --option amend --human-confirmed --rationale "..."
omega decision validate
# stretch:
omega decision graph [--focus D001] [--depth 2]
```

Exit codes: 0 ok · 1 validation · 2 auth · 3 not found.

## C.6 Migration of 23 decisions

**Prefer two commits/PRs**:

1. Engine + schema + empty catalog + tests  
2. Migrate content from `docs/strategy/OPEN_DECISIONS_CATALOG_20260718.md` into `D001`…`D023` YAML  

Do **not** decide content in this workstream — only structure.

## C.7 Tests

1. Schema rejects unknown field  
2. `decide` creates successor + marks superseded  
3. Human authority without flag fails  
4. `show` walks supersession chain  
5. CLI smoke (Typer runner)

## C.8 Acceptance criteria

- [ ] `omega decision list` works from venv  
- [ ] Supersession golden test  
- [ ] No MAD/BE numeric in v1 schema  
- [ ] Review conditions from Conditional GO satisfied  
- [ ] Docs: short `docs/strategy/DECISION_WORKSPACE_README.md` (optional 1-pager)

## C.9 Out of scope

- Implementing D1–D23 **answers**  
- TUI dashboard  
- Hivemind decision channel  

---

# WS-D — Path III-B (`config_resolver` adoption)

**Owner**: P3 / Grok Tier A  
**Effort**: 3–6h (batch by package)  
**Refs**: residual ~40 `Path(__file__)` sites

## D.0 Goal

Replace ad-hoc `Path(__file__).resolve().parent×N` with:

```python
from omega.governance.config_resolver import PROJECT_ROOT, CONFIG_DIR, DATA_DIR, WADS_DIR
```

**Do not** re-export from `governance/__init__.py` (circular import guard).

## D.1 Priority file batches

| Batch | Files (examples) | Notes |
|-------|------------------|-------|
| D1 | `oracle/session_manager.py`, `entity_workspace.py` | High traffic |
| D2 | `state/cas.py`, `state/usm.py` | DATA_DIR |
| D3 | `observability/*`, `vault/key_vault.py` | DATA_DIR |
| D4 | `cli/oracle_cli.py` config/data paths | Keep sys.path hacks only if required for script entry |
| D5 | `library/*`, `memory_store.py` | Careful parent-count bugs |
| D6 | workers / iris | Last |

**Parent-count rule**: `config_resolver.py` lives at `src/omega/governance/` → **4 parents** to repo root. Copying “3 parents” from other modules is a **bug**.

## D.2 Steps per batch

1. List sites: `rg -n 'Path\(__file__\)' src/omega/<pkg>`  
2. Replace with resolver constants  
3. Preserve `OMEGA_DATA_DIR` / `OMEGA_WADS_DIR` env overrides where already present  
4. Run package tests  
5. Commit per batch: `refactor: path SSOT batch D{n} — {pkg}`

## D.3 Acceptance criteria

- [ ] Target batch has zero raw parent walks for PROJECT/DATA/CONFIG (entry-point sys.path OK)  
- [ ] Tests for touched modules green  
- [ ] No WAD entity hardcoding introduced  

## D.4 Out of scope

- Full M2 Phases B–E entity renames (see HMC Quad-Forge manual)  
- Renaming mythic docs  

---

# WS-E — D-284 Sovereign Hub (deferred design-to-build)

**Owner**: P4 Integration  
**Trigger**: real multi-client OAuth pain or Streamable HTTP requirement  
**Refs**: MCP Authorization 2025-06-18 (verified)

## E.0 Spec non-negotiables (when building)

1. HTTP transport: Streamable HTTP primary  
2. OAuth **2.1** + **PKCE MUST**  
3. RFC 8707 `resource` parameter  
4. Protected Resource Metadata (RFC 9728)  
5. **No token passthrough**  
6. STDIO continues env credentials  
7. Self-hosted IdP for M7 (Keycloak/Ory) — not SaaS dependency  
8. Map to **real** entrypoints (`src/omega/iris/server.py`, hub modules) — **not** fictional `mcp_hub/` only  

## E.1 Phased build (when triggered)

| Phase | Deliverable |
|-------|-------------|
| E1 | Health + Streamable HTTP `/mcp` skeleton |
| E2 | OAuth metadata + PKCE client path |
| E3 | Token store (SQLite single-node) |
| E4 | Mutating-tool draft-then-commit (SHIELDMCP-style) |
| E5 | Hub agent-card |

**Do not** start without Kali/Architect GO.

---

## 4. Cross-cutting: Hybrid search cleanup (optional)

| Issue | Action |
|-------|--------|
| Dual modules `hybrid_search.py` + `hybrid_search_engine.py` | Prefer **one** RRF SSOT (`hybrid_search_engine`); re-export shim from old name |
| k=60 | Keep |

Effort: 1–2h. Owner: P2. Not blocking WS-A.

---

## 5. Baseline test / gate hygiene

### Known classes

| Area | Status | Action |
|------|--------|--------|
| first_breath world query | **Fixed** | Protect with regression in CI narrative |
| speculative_decode section | Present in `models.yaml` | Re-run gemma MTP test |
| Empty GGUF path tests | Env-dependent | Fixture or skip-if-missing-model with clear mark |
| Full suite count | Changes over time | Never claim “1130” without measuring |

### After every workstream

```bash
source .venv/bin/activate
# Targeted first:
python -m pytest <your tests> -q
# Then broader as appropriate:
make test          # or documented subset if suite too long
make temple-grade  # non-trivial
make heritage-map  # if heritage touched
make lint          # if available
```

Pre-commit may require **docs with src** — ship a short research/strategy note with Core changes.

---

## 6. Hivemind protocol (mandatory multi-agent)

```text
1. hivemind_get_awareness
2. hivemind_handoff_list(pending|active)
3. Accept ONLY handoffs targeting you
4. Workspace lock: data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md
5. post_context (task_current, decisions, continuation)
6. heartbeat every 5–10 min on long work
7. complete_handoff(result=...) with commit SHAs + test counts
```

**Do not** complete another agent’s packet.

---

## 7. Commit & PR conventions

```text
feat: ...
fix: ...
refactor: ...
test: ...
docs: ...
chore: ...
```

Body: what / why / gates run. Link handoff id (`ho_…`).

---

## 8. Workstream → owner quick map

| WS | Primary | Secondary | Blocked by |
|----|---------|-----------|------------|
| A D-282 | Roc / P2 | P10 tests | — |
| B Recall wire | P7 | Researcher | A preferred |
| C Decisions | P3 | Kali | Review (done) |
| D Paths | P3 / Grok Tier A | — | — |
| E Hub | P4 | — | Pain trigger |

---

## 9. Definition of Done (fleet)

A workstream is **DONE** only when:

1. Acceptance checklist in that WS is checked  
2. Targeted tests green  
3. Commit(s) on `main` (or PR ready)  
4. Hivemind handoff completed with evidence  
5. Live feed updated  
6. No new M2 mythic hardcodes  
7. No new asyncio  

---

## 10. Agent prompt snippet (paste into handoff)

```text
Read docs/strategy/AGENT_IMPLEMENTATION_MANUAL_20260719.md
Execute ONLY workstream WS-X.
Follow Mandates M1/M2/M16/M23.
Do not expand scope into other WS.
Complete Hivemind handoff with test output + commit SHA.
```

---

## 11. Document map (related)

| Doc | Role |
|-----|------|
| This manual | **Execute** |
| `WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` | Verified claims |
| `KNOWLEDGE_GAP_MATRIX_20260717.md` | Historical matrix (partially stale) |
| `GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` | Decision Conditional GO |
| `GROUNDED_MEDITATE_DECISION_WORKSPACE_20260718.md` | Prior art (do not overbuild) |
| `HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md` | Nomenclature / Meditate / M2 A–E |
| `OPEN_DECISIONS_CATALOG_20260718.md` | Content for migration only |
| `SOVEREIGN_MANDATES.md` | Law |

---

## 12. Versioning

| Version | Date | Notes |
|---------|------|-------|
| v1.0.0 | 2026-07-19 | Initial full agent manual from Grok research + review + live tree audit |

**Maintainers**: Kali (authority), Grok CLI (advisory refresh), implementers (patch DoD after ship).

---

*⬡ OMEGA ⬡ AGENT-IMPLEMENTATION-MANUAL ⬡ FOLLOW-THE-WORKSTREAM ⬡ 2026-07-19*
