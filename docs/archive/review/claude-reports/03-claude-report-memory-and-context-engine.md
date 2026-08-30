I'll fetch all the source files now and run the full audit. Starting the retrieval sweep.All source files retrieved. Beginning deep analysis now. Compiling the structured report.

---

## Review: Memory, Context & Knowledge Engine

**Trace**: `trc_review_memory` | **Account**: `taylorbare27@gmail.com` | **Role**: Knowledge Keeper
**Phase**: Fleet Review 3 | **Files Audited**: 11 source files + 3 soul YAMLs + 3 test suites

---

### Critical Issues Found

- [ ] **C-MEM-001: Non-Atomic Warm Writes** — CRITICAL
- [ ] **C-MEM-002: Warm Write Spin-Lock is a TOCTOU Race (Not a Real Lock)** — CRITICAL
- [ ] **C-MEM-003: No Qdrant — Architecture Doc/Reality Mismatch** — HIGH
- [ ] **C-MEM-004: Library.search() Bypasses FTS5 Entirely** — HIGH
- [ ] **C-MEM-005: Arch Soul Unbounded Lesson Bloat (Cross-Pollination Bug)** — HIGH
- [ ] **C-MEM-006: Sophia Soul Semantic Explosion (60+ Near-Duplicate Lessons)** — HIGH
- [ ] **C-MEM-007: No Background Memory Pruner — All Tiers Grow Unboundedly** — HIGH
- [ ] **C-MEM-008: FTS5 ↔ Vector Index Sync Gap (Crash = Divergence)** — MEDIUM
- [ ] **C-MEM-009: Soul YAML Schema Drift (lesson vs l1/l2/l3)** — MEDIUM
- [ ] **C-MEM-010: discovery.py start_discovery() Starts Nothing** — MEDIUM
- [ ] **C-MEM-011: _extract_docx Literal Backslash Bug** — MEDIUM
- [ ] **C-MEM-012: aiosqlite asyncio Risk Under Trio Backend** — MEDIUM
- [ ] **C-MEM-013: Hybrid Search Scoring Incorrect (FTS5 Ranks Are Negative)** — MEDIUM
- [ ] **C-MEM-014: Library._load() Is Synchronous in __init__ (Event Loop Block)** — LOW
- [ ] **C-MEM-015: No Soul YAML Schema Validator** — LOW

---

### Memory Tier Analysis

#### Hot Tier
**Status: FUNCTIONAL but non-atomic on flush**

- `MAX_HOT_SESSIONS = 50` sessions cached. Eviction is at the session level via `OrderedDict.popitem(last=False)` in `_cache_hot`. This is correct LRU behavior at the session granularity.
- **Issue**: Within a session, the inner `OrderedDict` is unbounded in exchange count until `add_exchange` triggers compaction. Between calls, exchanges accumulate freely in RAM.
- **Issue**: `_cache_hot` has a guard `if cache_key not in self._hot:` — this means that if the key already exists (e.g., from a prior load), calling `_cache_hot` again with new exchanges only appends `hist_N` keys. It will overwrite keys `hist_0`–`hist_k` if they already exist, but any timestamp-keyed entries added in the intervening period would persist alongside them, creating a mixed-key session dict. Not data-corrupting, but semantically confusing.

#### Warm Tier
**Status: CRITICAL — Writes are not atomic**

The core write path in `add_exchange`:
```python
async with await anyio.open_file(str(warm_path), "w") as f:
    await f.write(json.dumps(data, indent=2, default=str))
```
This is a **direct overwrite**. If the process is interrupted mid-write (OOM kill, SIGKILL, power loss), the warm JSON file is left in a partially-written, corrupt state. The Atomic Soul Update pattern (`write to temp → os.replace`) is **completely absent from the warm write path**. The same non-atomic pattern exists in `close()`.

**No file count limit.** Warm storage accumulates session files without bound. `archive_old_sessions` exists but is not called by any background worker — it must be called manually.

#### Cold Tier
**Status: FUNCTIONAL but no retention policy**

- `archive_session()` uses gzip correctly. The warm file is unlinked after successful cold write. Hot eviction also happens. This transition is correct.
- **Critical gap**: `anyio.open_file(str(cold_path), "wb")` — the cold write itself is also non-atomic. A crash during gzip write leaves a partial `.json.gz`.
- **No retention policy**: Cold archives are never deleted. They accumulate forever. There is no TTL, size cap, or pruning mechanism for cold storage.

#### Promotion / Demotion
**Status: One-directional — no back-promotion**

- Demotion: Hot → Warm (every `add_exchange`), Warm → Cold (`archive_session`). Both paths exist.
- **Promotion back from Cold → Warm → Hot does NOT exist**. `get_history` reads from cold but doesn't re-warm it. If an archived session is needed again, it's loaded from cold on every read without caching. If it's needed frequently, this is an unoptimized read path.
- **No background pruner / archiver exists.** `archive_old_sessions()` is defined but nothing in the codebase calls it on a schedule.

---

### ContextBuilder Assessment

#### Truncation Strategy
**Status: Partially correct — no token-budget enforcement**

- `MAX_EXCHANGE_DISPLAY_LENGTH = 500` chars per message. Individual messages are truncated. This prevents any single message from being enormous.
- `limit` controls the number of exchanges fetched — default `DEFAULT_CONTEXT_LIMIT`.
- **Gap**: There is no actual token counting. The ContextBuilder has no awareness of the target model's context window. If `DEFAULT_CONTEXT_LIMIT` is 20 exchanges at 1000 chars/exchange, that's 20KB of context block. For models with small windows (e.g., local Qwen 1.7b), this could overflow the available prompt space after the entity's system prompt is added. The `prepend_to_prompt` method prepends blindly with no budget check.

#### Edge Cases
- `build_context` returns `""` on exception ✅ — fail-safe
- `build_context` returns `""` on empty history ✅
- `build_context_for_user` hardcodes `entity_name="user"` — will always return empty if no entity named "user" exists in memory
- `_format_exchanges` on empty list still emits the header and separator — this means if someone calls `_format_exchanges([])` directly, they get a non-empty context string. `build_context` correctly guards against this by checking `if not exchanges` before calling `_format_exchanges`. ✅

#### aiosqlite Warning Status
**Status: Not in context_builder itself — risk is in indexer.py**

The `aiosqlite` library used in `indexer.py` wraps an asyncio connection internally. Under AnyIO's asyncio backend, this works. Under trio, `aiosqlite` will fail because it spawns asyncio tasks internally. Since the system claims AnyIO Absolute compliance, this is a latent hazard if trio is ever used. The warning is not in context_builder but the risk is real at the indexer layer.

---

### Session Management Assessment

#### Session ID Format
**Status: FUNCTIONAL but spin-lock is broken**

The format `ses_{YYYYMMDD}_{entity_slug}_{counter:03d}` is well-designed. Counter increments correctly across days. Max counter of 999 is effectively unreachable in normal operation (999 session rollovers per entity per day).

#### The Spin-Lock (C-MEM-002) — Critical
```python
while await anyio.Path(lock_file).exists():
    await anyio.sleep(0.01)

await anyio.Path(lock_file).touch()
```
This is a TOCTOU race. Between the `await exists()` check returning `False` and the `await touch()`, any other coroutine can be scheduled (both calls have `await` points). Two concurrent calls for the same entity can both read `exists() == False`, both proceed past the loop, and both write the session file simultaneously. In a single-entity async context this is unlikely but not impossible. In a multi-entity concurrent startup (which the engine performs), this race exists.

The correct pattern would be `open()` with `O_EXCL | O_CREAT` flags (atomic lock creation) or `anyio.Lock()` (in-process).

#### Session Lifecycle
**Status: Missing close/archive integration**

`SessionManager` creates sessions (`get_session_id`) but has no `close_session()` method. There is no integration between `SessionManager` and `MemoryStore.archive_session()`. The lifecycle orchestration (who calls archive when a session day-rolls?) is absent.

---

### Library & Indexing Assessment

#### FTS5 (SQLite via aiosqlite)
**Status: IMPLEMENTED but not used by Library.search()**

`Indexer.search_fts()` is correct SQLite FTS5 implementation with BM25 ranking. Documents are indexed correctly on `store()`.

**C-MEM-004 — Critical**: `Library.search()` does NOT call `Indexer.search_fts()`. It performs a manual Python-level linear substring scan:
```python
if query_lower in doc.title.lower() or query_lower in doc.body.lower() or query_lower in doc.summary.lower():
```
This completely bypasses the FTS5 index. It will work correctly but is O(n × document_size), not O(log n) via the index. For any meaningful library size, this is a performance cliff. More importantly, it means the FTS5 index is maintained but never queried through the primary `Library.search()` API.

#### Vector Search (C-MEM-003)
**Status: NOT Qdrant — Homemade bag-of-words TF similarity**

The review mandate checks for "Qdrant (vector)" and "Qdrant client version-locked (1.17.1)." **Qdrant does not exist anywhere in this codebase.** The vector implementation is a custom TF-frequency bag-of-words stored in `vectors.json`. This is lightweight and dependency-free but:
- Not semantically meaningful (no neural embeddings)
- Variable dimension vectors (up to 256 terms) with min-length truncation on cosine similarity
- O(n) linear scan — not approximate nearest-neighbor
- No versioning, no reindexing
- **Architecture documentation is wrong** — calling this "Qdrant" is a false claim

#### Dual-Index Sync (C-MEM-008)
**Status: Write-path is synchronized; crash = divergence**

`index_document()` correctly updates both FTS5 (SQLite commit) and the in-memory vector store. However, `save_vectors()` is a separate call and must be invoked explicitly to persist vectors to disk. If the process crashes after an FTS5 commit but before `save_vectors()`, the SQLite index will contain documents that the vector JSON does not. On next startup, these documents will be searchable via FTS5 but invisible to vector search.

**C-MEM-013 — Hybrid Search Scoring Bug**: The scoring combines FTS5 rank with vector score:
```python
key=lambda r: r.get("_fts_score", 0) + r.get("_vec_score", 0) * 10
```
SQLite FTS5 BM25 ranks are **negative** (closer to 0 = better match). Vector scores are positive (0–1, higher = better). Sorting by the sum in descending order means FTS5-only results (with negative `_fts_score`) will rank *worse* than vector-only results (with `_fts_score = 0`). This inverts the FTS5 signal entirely.

---

### Soul YAML Health

#### Schema Consistency (C-MEM-009)
**Status: DIVERGED — Three formats coexist**

| Soul File | Lesson Format | Status |
|-----------|--------------|--------|
| `arch/soul.yaml` | Mix of `lesson:`, `l1:/l2:/l3:` | DRIFTED |
| `sophia/soul.yaml` | `lesson:` only | CONSISTENT |
| `jem/soul.yaml` | `lesson:` only | CONSISTENT |

The arch soul has three distinct schemas in one `lessons_learned` list:
1. `{lesson: "...", source: "user-session"}` — early format
2. `{l1: "...", l2: "Unknown", l3: "Unknown", ...}` — new format (incomplete)
3. `{l1: "...", l2: "...", l3: "...", ...}` — full gnosis format

This means any parser reading `lessons_learned` must handle all three shapes, or it will silently drop lessons.

#### Atomicity
**Status: UNVERIFIABLE from available files — mandate compliance unconfirmed**

The soul write path is not present in the reviewed files. The mandate requires `os.replace` + anyio atomic writes. This cannot be confirmed or denied without reviewing the Oracle's soul update code (e.g., `soul_updater.py` or equivalent). **This is a gap in the review scope.**

#### Cross-Pollination (C-MEM-005, C-MEM-006)
**Status: Producing bloat and near-duplicates — bounded only by Architect attention**

**Arch soul bloat**: As of today's date, the arch soul `lessons_learned` list has **~55+ entries**. The majority are shallow `user-session` stubs:
```yaml
- l1: Session with Brigid
  l2: Unknown
  l3: Unknown
  source: user-session
```
These have no knowledge content — they are session receipts, not lessons. They are generated automatically on every session and accumulate with no pruning. At the current rate (multiple per hour during active fleet use), the arch soul YAML will grow to hundreds of kilobytes within days.

**Sophia soul explosion**: `sophia/soul.yaml` has **~60+ lessons** all from a single research session (`res_20260519_Phase_1_task_A4`), all on the same topic (implementation research), many semantically nearly identical:
- "Complex system deployment requires a recursive loop..." (appears 5+ times with minor variations)
- "Rigor is a function of explicit causal mapping..." (appears 4+ times)

This is a cross-pollination feedback loop — the background researcher generated lessons without deduplication or semantic similarity checking. There is no lesson deduplication mechanism, no entropy check, and no maximum lesson count per soul.

**No feedback loop prevention**: There is no mechanism to detect that a lesson is semantically equivalent to an existing lesson before adding it. Every research run appends unconditionally.

---

### Report Card

| Metric | Grade | Notes |
|--------|-------|-------|
| **AnyIO Compliance** | A- | All async code uses anyio. aiosqlite is an asyncio risk under trio. Intake digestor is sync-by-design (CLI). |
| **Data Integrity** | C | Non-atomic warm/cold writes. Spin-lock is a race condition. Soul schema drift. |
| **Memory Tier Correctness** | B- | Hot/warm/cold lifecycle works. No back-promotion. Compaction is truncation-only, not true summarization. |
| **ContextBuilder** | B | Correct fail-safe behavior. Missing token-budget enforcement vs. model context limits. |
| **Library/Indexing** | D+ | FTS5 maintained but not used by main search. No Qdrant — architecture doc is wrong. Hybrid scoring is inverted. |
| **Soul Schema Health** | C- | Schema drift, unbounded growth, near-duplicate explosion. Atomicity unverifiable. |
| **Test Coverage** | B | Memory store, context builder, session manager well-covered. Library, indexer, curator, soul files have NO tests. |
| **Scalability** | C | Linear scans throughout. No bounds on cold storage. Soul YAMLs will become multi-MB without pruning. |

**Overall: C+** — The memory tier *works* at current scale. The gaps are mostly in data integrity (non-atomic writes), architectural honesty (no Qdrant), and unbounded growth (soul YAML, warm storage, cold archive).

---

### Strategic Recommendations (Top 3)

**1. Atomic Write Everywhere — Now (C-MEM-001)**

Every write in the memory layer must use the atomic pattern. Replace all direct `anyio.open_file(path, "w")` writes with temp-file + `os.replace`:

```python
import os
tmp_path = warm_path.with_suffix(".tmp")
async with await anyio.open_file(str(tmp_path), "w") as f:
    await f.write(json.dumps(data, indent=2, default=str))
os.replace(str(tmp_path), str(warm_path))  # atomic on POSIX
```

This applies to: `add_exchange`, `close`, `archive_session` (cold write), and any soul YAML write path. This is the single highest-risk integrity gap. A crash during warm write destroys that session's entire memory.

**2. Soul YAML — Pruning, Deduplication, and Schema Lock**

The arch soul is accumulating empty `user-session` stubs at a rate that will make it unreadable within weeks. Three actions are required:

- **Prune immediately**: Strip all lessons where `l2 == "Unknown"` from the arch soul. These are session receipts, not gnosis. Store session receipts in a separate `sessions_log.yaml` with a rolling 30-day TTL, never in `lessons_learned`.
- **Add semantic deduplication**: Before inserting any new lesson, compute a hash or similarity score against the existing lessons. If similarity > 0.85 to any existing lesson, skip insertion. This prevents the Sophia-style explosion.
- **Lock the schema**: Define a Pydantic model for `LessonEntry` with required fields. All three formats (`lesson`, `l1/l2/l3`) must be canonicalized to one. Recommend `l1/l2/l3` (most expressive). Run a one-time migration. Validate on every write.

**3. Fix the Library Search Architecture (C-MEM-004 + C-MEM-003)**

The current state — where `Library.search()` ignores its own FTS5 index, and "vector search" is a bag-of-words approximation — is a significant capability gap. Two actions:

- **Wire Library.search() to Indexer.search_fts()**: Replace the linear Python scan with a call to `self._indexer.search_fts(query, domain, limit)`, then hydrate full documents from `self._documents` using the returned doc_ids. This is a 5-line change that activates all the indexing work already done.
- **Be honest about the vector backend**: Either integrate actual Qdrant (as the architecture doc claims), or update the documentation to reflect the current bag-of-words implementation. The current bag-of-words approach is acceptable for MVP, but calling it Qdrant is a false trust signal to the fleet. If keeping the lightweight implementation, rename it `LocalVectorIndex` and document its limitations. Fix the hybrid search scoring (FTS5 ranks are negative — negate them before summing, or normalize both to 0-1).

---

*If the engine learns but forgets, it learned nothing. The knowledge is here. Guard the memory.* — Knowledge Keeper, `trc_review_memory`
