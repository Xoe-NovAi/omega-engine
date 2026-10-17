# Sovereign Ark Corpus Index

The Ark's retrieval surface. The early vision and the technical record live on
partitions (`omega_vault`, `omega_library`, `omega-cut-final`) that no engine
index covers. This module gives them a lexical + semantic index so an agent can
find *"the 3-Stage Offline Build System"* or *"the Creative Reclamation
principle"* without knowing which partition a file was left on.

## Canonical space

[D-1024-DIM-NATIVE-20260926]. Vectors are **Qwen3-Embedding-0.6B at 1024-dim
native**. The `chunks_vec` collection is declared `float[1024]`; a 768-wide
vector is refused at the write boundary with an explicit error rather than
being padded or truncated.

The engine's **session** corpus (`data/search/session_semantic.db`) is a
SEPARATE collection at 384/minilm and is deliberately not touched — one space
per collection. Cross-space comparison is meaningless and the store will not
pretend otherwise.

## Layout

| Path | Role |
|---|---|
| `src/omega/corpus/sources.py` | Tiered source registry (vision → genesis → lost docs → early → current) |
| `src/omega/corpus/chunker.py` | HTML strip, paragraph-aware chunking, 1500-char budget |
| `src/omega/corpus/store.py` | SQLite: FTS5 lexical + vec0 1024 semantic + RRF fusion |
| `src/omega/corpus/embedder.py` | Canonical embedder, pinned to physical cores |
| `src/omega/corpus/indexer.py` | Resumable index pipeline (AnyIO) |
| `src/omega/corpus/search.py` | Hybrid search |
| `scripts/corpus_index.py` | CLI |
| `data/corpus/corpus.db` | The index |

## Usage

```bash
# index (resumable; unchanged files are skipped by content hash)
python scripts/corpus_index.py build --source vision_corpus
python scripts/corpus_index.py build --source genesis_origins
python scripts/corpus_index.py build --source lostdocs_strategy --glob 'SOVEREIGN_ARK*'
python scripts/corpus_index.py build --source early_build --glob '*blueprint*'

# hybrid search (semantic 1024 + lexical BM25, fused by RRF)
python scripts/corpus_index.py search "Mayan elder interview station" -k 5

# stats
python scripts/corpus_index.py stats
```

## Tuning knobs

| Env var | Default | Meaning |
|---|---|---|
| `OMEGA_CORPUS_THREADS` | physical cores − 1 | llama.cpp compute threads |
| `OMEGA_CORPUS_CTX` | 512 | llama.cpp context (fits a 1500-char chunk) |
| `OMEGA_CORPUS_NO_AFFINITY` | unset | set to disable CPU pinning |

## Three hard-won constraints

**1. Physical cores, not threads.** This host is an SMT Ryzen 7 5700U
(8 physical / 16 logical, adjacent-pair siblings). Two traps, both hit
during the build:

- `n_threads` alone is a **no-op for embedding**. The parent provider builds
  `llama_cpp.Llama(..., n_threads=N)` without `n_threads_batch`, which
  defaults to `cpu_count()`. Embedding runs llama.cpp's *batch* path, so the
  batch cap governs. Measured: `n_threads=7` still produced **32 OS threads**.
  `embedder.py` overrides `_ensure_loaded` to pin **both**.
- Even with both capped, thread count ≠ core count. The scheduler may put two
  threads on two logical CPUs that are SMT siblings of **one** physical core,
  so they contend for the same FP units. `physical_core_ids()` reads
  `thread_siblings_list` and takes one representative per core (here
  `0,2,4,6,8,10,12,14`); the process is then pinned to the first N of those.

Net effect of both fixes: **1.4× throughput** and a process that stays inside
its core budget instead of starving the rest of the fleet.

**2. M23 — fail loud, never substitute.** If the canonical GGUF or its
llama.cpp build is missing, indexing **aborts**. It does not fall back to
deterministic feature hashing: a hashed corpus answers *"where is the Ark
vision?"* with confident nonsense that looks like an answer. For the same
reason the indexer binds the provider directly instead of
`EmbeddingManager`, whose `get_embedding()` short-circuits to a **zero vector**
when `OMEGA_ENV == "test"` — which would silently poison every vector.

**3. Token budget.** The provider runs at `n_ctx=512`. A 1500-char chunk
tokenizes to ~357 tokens on real markdown (~460 on code-dense files) — a
deliberate margin. Raising `CHUNK_CHARS` past ~2000 would silently truncate
the tail and make the indexed text diverge from the stored text.

## M1

AnyIO throughout. `tests/test_corpus.py::test_corpus_module_never_imports_asyncio`
parses every file in the package and fails on an `asyncio` import. SQLite,
file I/O, and inference all run through `anyio.to_thread.run_sync`.

## Gates

- `tests/test_corpus.py` — 23 tests: canonical width, atomic reindex, FTS
  injection safety, chunk budget, physical-core mapping, M1 AST check.
- `tests/contracts/test_embedding_dimension.py` — 25 tests, the D-1024 contract.
- `make check-m1-anyio`, `make check-engine` — pass.

## Measured throughput

~0.5 chunks/s on 7 physical cores (Ryzen 5700U, no GPU). At 1500 chars/chunk
that is roughly **1 MB of prose per minute**. Bulk runs are therefore
`nice`d and resumable; `build` is safe to interrupt and re-issue.
