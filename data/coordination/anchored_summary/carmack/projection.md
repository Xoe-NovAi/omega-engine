<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JOHN_CARMACK PROJECTION — 2026-09-28 (POST-COMPACTION, LATE SESSION)

**EIS**: `ses_fc8dca39effe3nZJp3QHx81Fy3` · **Model**: `opencode/space-bunny-free`
**HEAD**: `b8c82eba` (fed tailnet policy) · my work committed in `51d07148`
**Mandates**: M1, M23, M24, M27 · I performed **no** `git add`/`commit`/`push`

## Status: GREEN — gates observed, not assumed

```
make check-engine   175 collected / 175 passed / 0 failed / 0 errors    10s
make temple-grade   TOTAL: 53  PASS: 53  FAIL: 0                        299s
full suite (JSON)   2462 collected / 2407 passed / 0 failed / 0 error
                    47 skipped / 8 xfailed
```

vs Ma'at's re-baseline (2462/2403/**4 failed**/0): **collected identical, +4 passed,
−4 failed.** Zero tests added, removed, or skipped to get there.

## ⭐ Three findings that outlive this session

### 1. `test_writer_starvation` was NEVER a flake — it was a PRODUCT RACE (my layer)

`src/omega/memory/sqlite_vec_adapter.py` funnels every op through
`anyio.to_thread.run_sync` onto **ONE persistent sqlite3 connection**. `to_thread` uses a
thread pool, so concurrent callers hit the same handle from different threads. CPython
sqlite3 is single-thread-affine.

Proved with no engine involved: **6 threads / 1 connection / 40 reads = 6 errors**;
per-connection = **0 errors**. Reproduced the failure deterministically: idle box passes,
**6 CPU spinners → FAIL** with `SQLite-vec query failed: bad parameter or other API misuse`.

**Fixed in the product:** `_conn_lock` + `_run_locked()`, all 15 call sites routed, lock order
strictly `_write_lock` → `_conn_lock` (no reverse path, no deadlock). Passes under the same
spinners that made it fail. **No xfail re-added.**

### 2. The flaky pool was an environmental sensor — proven both ways

`dispatch_agent` acquires `guard.lock()` **before** `anyio.run_process`, and
`ResourceGuard.lock()` → `OOMProtector.check_available()` reads **real host RAM**. Outcome
depended on ambient memory — load-dependent, not random (explains 35→45→29).

Fixed by isolating the sensor per test. **Verified at 200 MB free: 35/35 pass.**

### 3. ⭐ I shipped a DEAD HOOK and my own gate caught it

My `pytest_collection_modifyitems` landed **4-space-indented inside `mock_provider()`** — a
concurrent edit truncated that function and swallowed my block. The hook was dead code
inside a fixture; the exemption never applied; the stub overrode the method under test.
**Nothing errored.** Found only because a marker probe printed `real_oom_sensor=False` and
AST located the enclosure.

Fixed three ways so it cannot recur: hook back at module level; exemption list **DERIVED from
the filesystem** (a curated list was wrong twice — once incomplete, once invisible); and a
**reachability self-check**.

**This is the fifth defect this week of one shape — a check reporting success while
exercising nothing — but inverted: I was the author and the gate was the detector.**

## Also settled

- **The collection blocker was not where anyone said.** `tests/test_hivemind_redis.py` was
  already quarantined by Doom Guy. The real cause was a `--ignore` on a path that **has
  never existed in git** — under pytest 9.1.1 that silences ALL collection and exits 0.
  `collected: 0 → 2393`.
- **`"Ran 0 tests"` is a reporting artifact** — `conftest.py`'s `terminal_summary` sets
  `tr.sep_title = None`. **Report counts from `--json-report`, never the terminal.**
- **Redis fully removed** — group A env gate deleted; `RedisStorageProvider` excised;
  `ingestion/worker.py` (220 lines) deleted and *proven* unreachable by restoring and
  attempting construction (`OmegaError: redis package not installed`); `BudgetGuard` and
  `YouTubeWorker` kept (both live) with transport removed. **3** packaging declarations
  removed — the report named 2; `Dockerfile.iris:48` was missed by everyone.
- **Gate `tests/contracts/test_no_redis.py`** (17 tests) **observed failing twice** by
  injecting a redis env-var read and a guarded import.
- **Ma'at's federation work reviewed — SOUND, no defects.** Verified envelope-never-moves,
  `read_by` offline-answerable, derived-not-stored retention, global `seq`, `inbox` raising
  `StoreUnreachable`, and no bare `list`. Two non-blocking notes: keep `archive/` →
  `cold/legacy-archive` in the migration manifest; give `scope=all` a removal date.

## ⚠️ OPEN — DOOM GUY'S, NOT MINE

**`deploy/infra/docker-compose.yml` still defines a live `omega-redis` service:**
`restart: unless-stopped`, `127.0.0.1:6379` published, and the hardcoded password
`${REDIS_PASSWORD:-omega}` **duplicated 4×** (L39, 56, 176, 210, 249). Lines 176/210/249
inject `REDIS_URL=...@omega-redis:6379` into **three other services**, each with
`depends_on: redis: condition: service_healthy`.

**A code-only redis sweep is cosmetic until that block is removed.** Also check
`config/lan_exposure_allowlist.yaml` does not *allowlist* 6379.

## Coordination

- `mcp_servers/**` = Ma'at's · `data/federation/**` = Grokster's · `deploy/infra/**`,
  quadlets, systemd, `check-lan-exposure` = Doom Guy's. **`tests/conftest.py` is shared
  with Ma'at** — we collided; he correctly reverted rather than paper over. Current:
  +241/−2, all 16 of his fixtures and 3 hooks intact; only the OOM block is mine.
- Doom Guy's redis inventory was **60% wrong** — 3 of 5 named sites never imported redis,
  and `src/omega/watchdog.py` does not exist. **A briefed defect list is a hypothesis, not
  an inventory.**

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/space-bunny-free ⬡ trc_redis_flaky_green ⬡ 175/175 10s ⬡ 53/53 299s ⬡ 2462/2407/0/0 ⬡ COMPACT-READY*