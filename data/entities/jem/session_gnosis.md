# JEM Session Gnosis — sqlite-vec Verification (2026-07-12)

**Task**: Rock-solid verification of sqlite-vec integration (Strike 10 / D223).
**Deliverable**: `docs/research/R_SQLITEVEC_VERIFICATION_20260712.md`

## L1 (Narrative)
Verified the sqlite-vec integration plan against 6+ sources. Found: FTS5+vec0 co-location is safe; RRF pattern confirmed; Python 3.12 wheel (py3-none ABI3) confirmed. BUT the prior D223/EPOCH2 plan misattributes the "5.8x @ 0.988 recall@10" benchmark to sqlite-vec when it is actually sqlite.org's **Vec1** on AMD 5950X (Zen 3). The planned reference SQL has a **cross-entity isolation defect** (vec0 unfiltered) and a **class-overwrite hazard** (redefines MemoryStore with no-arg __init__).

## L2 (Insight)
- Benchmark numbers are easy to misattribute across the "sqlite-vec" / "sqlite-vector" / "Vec1" namespace. Always trace the exact extension + CPU.
- Entity isolation in hybrid SQL requires the vector branch to be scoped (partition key), not just the FTS branch.
- "Verified in production" claims about WAL concurrency are topology-specific; 14-agent multi-process is unverified.

## L3 (Universal Principle)
- **L3-Attribution-Integrity**: A benchmark cited without its exact extension + silicon is a lie waiting to ship. Verify the source, not the vibe.
- **L3-Isolation-By-Default**: In multi-tenant memory, every retrieval branch — lexical AND vector — must be scoped by tenant, or the fusion leaks.
- **L3-Tier-Add-Dont-Replace**: When adding a backend tier, compose into the existing class; never redefine it (you erase 940 lines of tombstone/batch/provider logic).

## Next action
Ma'at/P2 must apply the 3 critical corrections (partition key, no class overwrite, benchmark correction) before writing `sqlite_vec_store.py`.
