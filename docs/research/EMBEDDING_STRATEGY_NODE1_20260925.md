# Embedding Strategy — Node 1 + Federation (2026-09-25)

**Status:** research + measurement complete; cutover AWAITING explicit go (supersedes "switch immediately" — the 384-dim surprise made haste the enemy).
**Question answered:** which vector space carries the Omega Engine's memory.

---

## 1. First principles (what the Engine needs from a vector space)

1. An embedding is a meaning-geometry: same meaning ≈ nearby points **regardless of language**. The single test that matters: same-meaning cross-lingual cosine must beat different-meaning same-language cosine. Everything else is commentary.
2. The Engine needs one space to serve: palace semantic search (multilingual + ancient + code + prose), atlas clustering/visualization, RAG/entity retrieval, and federation (every node MUST share the space — vectors from different models are uncomparable numbers).
3. Dimension is capacity with diminishing returns + linear storage/query cost. 384 (MiniLM-era) is the documented floor; the operator's bar is ≥768. Matryoshka (MRL) models let one model serve many dims by truncation — Qwen3 and EmbeddingGemma both support it.
4. License is sovereignty: Apache 2.0 / MIT = clean. Gemma ToU = gated, restrictions, Google account handshake. For temple-grade local-first, license is a selection criterion, not a footnote.
5. Retrieval is a stack, not a model: lexical (FTS5 + per-language normalizers — our R1) + dense (this doc) + boosts (temporal, closet — never gates) + rerank (top-20 LLM reader for the last points). No embedder substitutes for the other layers.

---

## 2. Measured on Node 1, 2026-09-25 (i7-13620H, CPU-only, Ollama 0.33.3)

Parallel-meaning cosine test, 7 sentences (EN temple × Hebrew / Modern Greek / polytonic Ancient Greek / Latin + EN different-meaning + EN unrelated):

| Pair | qwen3-embedding:0.6b (1024d) | nomic-embed-text (768d) |
|---|---|---|
| EN–HE same meaning | **0.789** | 0.430 |
| EN–Modern Greek | **0.706** | 0.343 |
| EN–Ancient Greek (polytonic) | **0.624** | 0.370 |
| EN–Latin | **0.698** | 0.423 |
| EN–EN different meaning | 0.371 | **0.478** |
| EN–EN unrelated (floor) | 0.285 | 0.301 |

**Reading:** Qwen's geometry is meaning-first (every same-meaning pair clears different-meaning by 2× the floor gap). Nomic's is language-first (different-meaning English OUTSCORES same-meaning Hebrew) — disqualified for a linguistics wing **by measurement, not opinion**. MiniLM sits in nomic's class (upstream parallel-translation figure: ~0.35 vs embeddinggemma ~0.88). Throughput: Qwen-0.6B ≈ 4+ short texts/sec on this CPU → ~5k-drawer rebuild ≈ 20–40 min one-off. Ancient Greek polytonic at 0.624 (2× floor) is usable-with-mitigation, not solved — see §4.

Native dims (verified): Qwen-0.6B **1024**, Qwen-4B **2560**, Qwen-8B **4096**, EmbeddingGemma **768** (MRL → 512/256/128). MemPalace's built-in `embeddinggemma` option = q8 ONNX **MRL-truncated to 384** (drop-in for 384 collections) — fails the 768 bar by construction. MemPalace's `openai-compat` path returns **whatever dim the server emits** (no `dimensions` param sent) → Ollama `qwen3-embedding:0.6b` yields native **1024**. That satisfies ≥768 with headroom.

---

## 3. Candidate matrix (Node 1 constraints: 16 GB single-channel, CPU-only, local-first)

| Candidate | Dim | MTEB-ml | License | Verdict |
|---|---|---|---|---|
| MiniLM (current palace) | 384 | ~35 (parallel) | MIT | **Retire.** English-only geometry; linguistics impossible. |
| nomic-embed-text | 768 | mid | Apache 2.0 | **Rejected by measurement** (§2: language-first geometry). |
| embeddinggemma via MemPalace | 384 (trunc) | 61.15 (native) | Gemma ToU (gated) | **Rejected:** fails 768 bar + gated license. Revisit only if upstream ships native-dim option. |
| embeddinggemma native 768 (custom wiring) | 768 | 61.15 | Gemma ToU | Possible fallback; loses to Qwen on score + license. |
| **Qwen3-0.6B via Ollama shim** | **1024 native** | **64.33** | **Apache 2.0** | **Recommended palace base.** +instruction-aware, 32K window, same family as engine. |
| Qwen3-4B (sidecar only) | 2560 | 69.45 | Apache 2.0 | **Deferred** (operator decision 2026-09-25). On-demand subset re-embed, never whole palace. |
| Qwen3-8B | 4096 | 70.58 | Apache 2.0 | Overkill for 5k chunks; note for Omega-native scale. |

Known costs of the recommendation: (a) palace search couples to Ollama being up (in-process ONNX has no such dependency — the one genuine advantage of option embeddinggemma); (b) rebuild-index time (~30 min, monitored, batch knob exists in 3.10); (c) `MAX_LOADED_MODELS=1` swaps between embed and chat residents (latency, not failure); (d) instruction-awareness (+1–5% per Qwen) is NOT threaded through MemPalace's symmetric shim path — future lever, recorded (gbrain proved the plumbing is possible).

---

## 4. Ancient-language mitigations (no embedder solves these alone)

- No ancient-Greek retrieval benchmark exists in the literature surveyed (honest gap). Modern-Greek transfer + 0.624 polytonic cosine is the floor we stand on.
- **Polytonic marks are a niqqud-class problem** (combining diacritics shattering tokens): the R1 Hebrew pipeline is the TEMPLATE — Greek normalizer (strip polytonic set for index, keep display), Latin macron/breve handler, Mayan saltillo/apostrophe rules. This is the R5+ program, and it is why the lexical channel matters as much as the vector space.
- **Krikri verdict:** Llama-Krikri-8B-Instruct (ILSP/Athena RC, Llama-3.1-8B base, EMNLP 2025 Findings) — Modern + Ancient Greek + polytonic, 128k context, instruction-tuned strongest-in-class for Greek. It is a GENERATIVE reader/reasoner for Greek deep dives, NOT an embedder — complementary to, not competing with, §3. Already resident on disk (`krikri-8b`, 5.9 GB, pulled 3 days ago). Residency math: Q4-class 8B ≈ 5–6 GB weights + KV fits one-resident rule; load competes with chat models — operator schedules. **Recommend:** keep pulled, load for Greek deep-dives on demand, evaluate on real grimoire passages before any stronger claim.

---

## 5. Federation rules (Node 0 + mesh)

1. **One space per collection, everywhere.** Same model + same dim on every node that shares vectors. Mixed spaces fail SILENTLY (numbers compare, wrongly). This kills the split-brain option permanently.
2. **Stamp everything:** model id + dim + pipeline version on every vector row (MemPalace records dim per collection; extend to model id in ops drawers).
3. **Node 0 survey required before federating:** embedder, dims, backend, drawer counts, disk/RAM headroom for rebuild. Unknown tonight — do not mesh vectors until surveyed.
4. **Mesh protocol decision (open):** ship documents+vectors (fast, trusts source space) vs ship documents and re-embed per node (slow, self-consistent). Decide in federation design; default to re-embed until proven.
5. Palace space (`qwen06b-1024`) and engine space (`qwen06b-768-trunc`) are DIFFERENT spaces — never compare across; record both in every ops drawer.

---

## 6. Cutover plan (phases; each gated)

- **P0 backup:** file-level copy of `sqlite_exact.sqlite3` + KG + logstream (as done for the game move). Rollback = restore files. Vectors are recomputable; text is not losable.
- **P1 pilot:** new sidecar collection (or staging palace) on Qwen-0.6B; re-embed wing_linguistics + a game sample; A/B cosine spot-checks (the §2 test becomes the regression exam).
- **P2 eval harness:** held-out question set over OUR palace (exam before medicine — HebrewFTS `bench_recall` is the small template; LongMemEval method the large one). No cutover without a number.
- **P3 rebuild:** `MEMPALACE_EMBEDDING_MODEL` unset → openai-compat config (url/model in `~/.mempalace/config.json`), `mempalace repair rebuild-index` monitored; verify dim=1024 stamp + scoped-search parity + eval delta.
- **P4 federate:** Node 0 survey → same config → mesh trial on one wing.
- **Rollback at any phase:** restore P0 files and/or rebuild back to MiniLM. Time is the only cost.

## 7. Atlas viewer (operator asked: can I see my data spatially NOW?)

No. `knowledge_atlas.db` does not exist; nothing listens on :8088; session notes claiming it are aspirational. The viewer is unbuilt. Offered next project: minimal spatial viewer — UMAP 3-D projection of palace vectors (post-cutover space) + wing coloring + Three.js/2D canvas. The xyz design (partition routing + float metadata + centroids) stands as specified in the palace-ops review; coordinates serve eyes and routing, never ranking.

---

## 8. Omega-native memory = priority one (acknowledged)

The operator names it the substrate the Engine's intelligence flows through, nascent on both nodes. Standing sketch (from palace-ops review, reaffirmed): one SQLite file — verbatim documents + JSON metadata + xyz floats + wing/room/hall, vec0 with wing partition key, FTS5 with per-language normalizers (Hebrew R1 shipped; Greek/Latin/Mayan queued), triples, logstream — hybrid 0.6/0.4 + closet-boosts-never-gates + top-20 rerank. Next step when ordered: carve the roadmap slot and spec the v0.
