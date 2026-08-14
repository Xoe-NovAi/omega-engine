# Gap R26: Honker (Redis Replacement) Verification

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** UO-7 / Redis-removal decision (M7 local-first)
**Status:** ✅ RESOLVED

## ⚠️ PLAN CORRECTION
The research plan's Risk Mitigation row *"Honker doesn't exist → Keep Redis"* is **INVALID**. Honker **exists and is maintained** (verified 2026-08-14), and Wafris already migrated Redis→SQLite in production. The correct conclusion: Honker is a viable local-first Redis replacement for single-node deployments.

## Summary
**Honker** (`russellromney/honker`) is a SQLite extension that adds Postgres-style `NOTIFY`/`LISTEN`, durable pub/sub, task queues, and event streams — **with no daemon or broker**. Any language that can `SELECT load_extension('honker')` gets the features. Wafris (open-source WAF) rearchitected its v2 client from Redis to SQLite and measured **~3× faster** locally (no network round-trip). This makes Honker a credible local-first replacement for the engine's Redis pub/sub (Hivemind awareness, handoff queues).

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Honker (russellromney) | https://github.com/russellromney/honker | 2026 | SQLite pub/sub + task queue, no broker |
| Wafris Redis→SQLite | https://wafris.org/blog/rearchitecting-for-sqlite | 2026 | 3× faster, no network, headless v2 |
| Wafris headless concept | https://wafris.org/docs/concepts/headless/ | 2026 | SQLite-synced rules, no Redis |

## Findings
- **Honker**: `pip install honker` (bundles loadable extension); `SELECT load_extension('honker')` enables `NOTIFY`/`LISTEN`, durable queues, event streams. WAL mode for concurrent readers + single writer. Bindings: Python, Node, Ruby, .NET, Rust, Go, etc.
- **Wafris precedent**: moved from "bring-your-own Redis" to SQLite because (a) network latency dominated every request eval, (b) Redis added a second datastore + backup story + broker to manage, (c) SQLite was ~3× faster locally even before latency. Sync architecture: client pulls a fresh SQLite DB on interval.
- **Engine fit**: the engine uses Redis today for Hivemind pub/sub + handoff queues (via omega-hub). Honker could replace that for **single-node** deployments with zero external services (M7 local-first). Multi-node federation still needs a transport (Redis or another).

## Recommendation
For UO-7 / the Redis-removal decision: **evaluate Honker as the local-first replacement** for the engine's Redis pub/sub in standalone deployments. It removes the broker/daemon and keeps everything in the existing SQLite fabric. Keep Redis for multi-host federation. Caveats to verify before locking: Honker is newer/less battle-tested than Redis; benchmark pub/sub latency on this host; confirm `sqlite3` is compiled with `load_extension` enabled in the Python build; test multi-writer concurrency under WAL. Update the plan's Risk Mitigation row — "doesn't exist" is false.

## Confidence
**HIGH** — Honker's existence, API, and the Wafris production precedent are verified.

## Remaining Unknowns
- Pub/sub latency benchmark Honker vs Redis on this 4-core/16GB host.
- `sqlite3` `load_extension` availability in the venv Python build.
- Multi-writer concurrency behavior under WAL for the handoff queue use case.
