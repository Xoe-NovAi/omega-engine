# GAP SWEEP — ENGINEERING & FEDERATION (Humboldt, 2026-09-25)

**Mode:** research-only. Nothing written to disk by the researcher. Versions fetched live; the FTS5 measurement was taken in-memory on this machine.

**Legend:** ✅ verified (live fetch or local measurement) · 🟡 reported (credible secondary, not confirmed) · 🔵 unverified (open) · ❌ refuted

---

## 0. Baseline drift — what the repo believes vs. what is true

| Claim | Repo says | Measured/fetched | Status |
|---|---|---|---|
| Ollama | 0.33.3 | **0.34.4** (released 2026-09-23) | ❌ **2 minors behind** |
| llama.cpp | build refs b8146/b11175 | stable tag **v0.5.0** (2026-09-23) | 🟡 scheme change |
| Open WebUI | v0.11.3 pinned | unchanged; CVE status unknown | 🔵 |
| OpenCode | unpinned | 1.18.32 installed | ✅ |
| Tailscale | unpinned | 1.102.4 | ✅ |
| SQLite | — | 3.46.1 | ✅ |
| Tesseract | — | not installed | ✅ |

---

## 1. THE SILENT DEFECT — FTS5 cannot index Hebrew scripture ✅✅

**Measured on Node 1, in-memory, SQLite 3.46.1 FTS5, tokens via `fts5vocab(..., 'instance')`:**

| Input | unicode61 tokens |
|---|---|
| `שלום עולם כאן` (spaced, unvocalized) | **3** ✅ correct |
| `שלוםעולםכאן` (unspaced) | 1 ❌ |
| `שָׁלוֹם עוֹלָם` (niqqud) | **6 for 2 words** ❌ |
| `וְהָיָה־כֵן` (maqaf) | 6 ❌ |
| `בְּרֵאשִׁית בָּרָא אֱלֹהִים…` (Gen 1:1, vocalized) | **25** ❌ |

**Root cause:** niqqud (U+05B0–U+05C7) are Unicode category `Mn` (nonspacing marks) — `unicode61` splits on category boundaries, shattering the word. Maqaf (U+05BE) is category `Pd` (dash punctuation) and also separates, despite being a legitimate Hebrew word-joiner.

**`remove_diacritics` does NOT fix it** — measured 0/1/2: byte-identical (25 and 10 tokens respectively). The option folds Latin/Greek marks; it does not pre-strip Hebrew `Mn` before the category-class tokenizer runs. **There is no SQLite setting that fixes this.**

**Same failure documented for CJK:** `tobi/qmd#207` (closed, *not planned*) — identical root cause; the documented remedy is application-layer segmentation before insert.

**Required mitigation (design constraint, not yet implemented):** strip U+0591–U+05C7; normalize maqaf U+05BE; apply the **same normalization to the query path** or search silently returns nothing. Unvocalized space-delimited Rabbinic prose already works.

**Blast radius:** lexical channel only. Dense retrieval (qwen3-embedding) is unaffected — so hybrid fusion is currently **lopsided**: semantic carries 100% of Hebrew recall while BM25 contributes noise dressed as signal. After the fix, RRF gets a real second opinion.

---

## 2. SECURITY — the GGUF parse surface ✅

**llama.cpp advisories absent from our docs (fetched live):**

| Advisory | Sev | Affected | Patched |
|---|---|---|---|
| **GHSA-3p4r-fq3f-q74v = CVE-2026-27940** | **High 7.8** | ≤ b8145 | ≥ b8146 |
| **GHSA-96jg-mvhq-q7q7** | **High** | < b7437 | b7824 |
| GHSA-j8rj-fmpv-wcxw | Critical | known (CVE-2026-34159) | — |
| GHSA-vgg9-87g3-85w8 (CVE-2025-53630) | High | 2025-07-10 | — |
| GHSA-7rxv-5jhh-j6xx | High | tokenizer heap overflow | — |
| GHSA-8wwf-w4qm-gpqr | High | malicious GGUF → `token_to_piece` | — |
| GHSA-wcr5-566p-9cwj | Critical | `rpc_server::set_tensor` W/W | — |
| GHSA-5vm9-p64x-gqw9 | Moderate | `rpc_server::get_tensor` arbitrary read | — |

**CVE-2026-27940:** integer overflow in `gguf_init_from_file_impl()`'s `mem_size` — a **bypass of the CVE-2025-53630 fix**. Two large I8 tensors push `ctx->size` near `SIZE_MAX`; the final add wraps small; the subsequent `fread()` writes **528+ attacker-controlled bytes past the buffer**. RCE demonstrated. PoC withheld at `huggingface.co/adig/gguf-hpovflw-poc`.

**Severity conflict ⚠️:** our guide records CVE-2026-21869 as "CVSS 8.8 High"; GitHub rates GHSA-8947-pfff-2f3c **Low**. Operationally the *patched version* (≥ c78fb90) is what matters.

**Ollama-side (secondary, 🟡):** CVE-2026-85180 SSRF on pull; **CVE-2026-5757 heap disclosure via quantization (may leak env vars, keys, prompts)**; CVE-2026-65315 GGUF-metadata uncontrolled allocation; CVE-2026-86289 GGUF decoder RCE. Windows-only CVEs-42248/-42249 not applicable.

**Why it hits this project specifically:** the grimoire pipeline ingests externally-sourced artifacts; the GGUF parser is where that meets untrusted bytes; and our ACL exposes Ollama (`:11434`) to Node 0 across the tailnet, extending these surfaces to the Archival Bastion.

**Minimum posture:** SHA-256 verify every GGUF before load; never pull from unpinned/mutable tags; treat `OLLAMA_HOST=0.0.0.0` over the tailnet as a *documented* risk acceptance.

**Open WebUI:** CVE-2026-0767 (cleartext credentials), CVE-2026-44549 (7.3), GHSA-4r2p-27mh-5m22 (same-origin Pyodide → server-side RCE via shared chat). Vendor-disposition page exists; not fetched. 🔵

---

## 3. THE PIN RULE IS MISATTRIBUTED ❌ → ✅

**Fetched ollama/ollama#17916 actual title/body:** *"Default n_threads ignores cgroup CPU quota and cpuset: ~45x"* — on a container-limited host, Ollama picks n_threads from host core count and ignores cgroup v2 `cpu.max` and cpuset; exceeding the CPU budget makes llama.cpp's spin-wait barriers convoy against CFS throttling, collapsing throughput ~45×.

**The invariant is thread-oversubscription against the *effective CPU budget* — not P-vs-E topology.** `OLLAMA_NUM_THREADS=8` on a 6-logical-CPU mask *is* the oversubscription.

- Our **measurement stands** (`AllowedCPUs=0-11` + 8 threads = 14.4 t/s) — it is a measurement, not a law.
- Our **stated law is a mis-generalization** and will misfire under containerization, governor changes, or a RAM/topology change.
- Three records of this one mechanism disagree in wording: `AGENTS.md` (machine rules), Well seed `bbf9147e`, correction `e9ece119`. When three records disagree, the phenomenon is described wrongly in all three.
- No evidence any 2026 release fixes the spin-wait/CFS interaction; treat the workaround as still required. 🔵

---

## 4. MCP — a breaking spec revision our hub predates ✅

**MCP 2026-07-28 (stable) removes:** protocol-level sessions + `Mcp-Session-Id`; the `initialize`/`notifications/initialized` handshake (**MCP is now stateless**; every request carries version + capabilities in `_meta`); the GET stream endpoint; `Last-Event-ID` resumability (GET/DELETE → `405`). **Deprecated:** Roots, Sampling, Logging; HTTP+SSE; OAuth DCR. Minimum 12-month deprecation window; servers may treat a header-less request as `2025-03-26`.

**Tasks extension** — *"asynchronous execution of long-running operations"* with polling, mid-flight input, durable handles. **This is the standardized answer to our background-curator design problem.** Evaluate before inventing a bespoke protocol. Host support varies → fallback still needed.

**OpenCode:** `anomalyco/opencode#6242` (SSE-first negotiation) — status unknown 🔵; matters more now that GET-stream is gone.

**⚠️ Unverified in our code:** if any part of `omega-hub:8016` assumes sessions, per-connection state, or the handshake, that is now deprecated-to-removed. This is a **code-inspection task** (grep `session`, `Mcp-Session-Id`, `initialize`), not a research question.

---

## 5. Hardware — a purchase-order correction ✅

| Item | Finding |
|---|---|
| ASUS spec (P1503CVA) | 2 sockets; **max 64GB**; 32GB in pairs validated; i7-13620H supported ✅ |
| **CL40 does not exist for this chassis** | Every validated 32GB option is **CL46** (e.g. **KVR56S46BD8-32**, 2Rx8, 1.1V). 64GB kits exist only at DDR5-**4800** (CompuRAM, ~€879) |
| 128GB | Out-of-spec — CompuRAM flags its own page as exceeding ASUS info. **Treat 64GB as the ceiling** |
| Operating speed | With 2 DIMMs the controller typically settles at **5200 MT/s** — the 5600 in the part number is not the operating speed |
| Bandwidth payoff | Dual-channel ≈ up to **2× memory bandwidth**. The qwen3-embedding daemon is **bandwidth-bound**, not compute-bound → roughly **halves a full grimoire embedding pass**, with zero code change. Highest-leverage purchase available |

---

## 6. Retrieval, models, OCR, federation, law (condensed)

- **sqlite-vec 0.1.9** (installed) — brute-force only on this machine (**verified locally 2026-09-25**: shadow tables are `v_info`/`v_chunks`/`v_rowids`/`v_vector_chunks00`; **no ANN index**). Upstream 0.1.10.alpha.4 adds IVF (2026-04-01) and DiskANN — and DiskANN shipped a **stale-reverse-edge data-leak fix** (ANN can return *deleted* rows). Brute-force at expected grimoire scale is fine; if ANN is adopted, **deletion correctness needs its own test**.
- **RRF** (Cormack et al., SIGIR 2009) beats Condorcet and needs no tuning; **k=60** is the Elasticsearch production default; RRF works on ranks, sidestepping BM25-vs-cosine scale incomparability. Weaviate moved off RRF to Relative Score Fusion in v1.24 — vendor defaults are not converging. Start at k=60, tune only after error analysis, measure with NDCG/MRR on a labelled query set.
- **KV q8_0** sound; **flash-attention on CPU is a no-op** (Volta+ gate) — do not spend time; **speculative decoding evidence conflicts** (Intel reports 3.92× on a 32-core Xeon; an independent study finds within-noise on bandwidth-bound CPUs) — measure locally, do not port the Xeon number (a draft model is a second resident model, which `MAX_LOADED_MODELS=1` forbids).
- **Q4_K_M remains the defensible default** for 3B–8B on AVX2-class CPU; no 2026 evidence that IQ3_XXS/Q4_0 beats it for persona/creative work. 🔵 (absence of contrary evidence, not proof)
- **Model landscape is empirically OPEN on this hardware.** 4B class at Q4_K_M (~2.5GB) is the comfortable envelope; 8B fits but squeezes the embedder; 12B+ does not fit. **Our `docs/models/` cards are all ≥7B** — several far above this node's ceiling. Searches returned SEO listicles with contradictory recommendations and no reproducible methodology: **no credible 2026 CPU benchmark for persona embodiment exists.** Settle it with a local bake-off.
- **Embedders:** qwen3-0.6b@768 (standing), GTE-multilingual-base (**768 native, no truncation** — the only interesting alternative), BGE-M3. CPU throughput 0.6B-class ≈ 20–80 chunks/min (torch) / 40–150 (ONNX int8); 4B/8B "not practical" on CPU — **independently validates RES-EMBED-001 on throughput grounds.** ⚠️ **No embedder has been evaluated on Hebrew religious text, and Judeo-Aramaic is rarer still.** RES-EMBED-001 was decided on *federation compatibility*, not retrieval quality — a different question.
- **OCR:** **Kraken + eScriptorium is the DH instrument** for historical/degraded print (CATMuS-Print covers 16th–21st-c print), CPU-trainable, **DOI-bearing model registry** — which maps directly onto our provenance rule. PaddleOCR 3.4 (5.2× CPU speedup via OpenVINO) as bulk screening second opinion. Tesseract = triage only. **No Judeo-Aramaic OCR model exists** (expected) 🟡; a CER figure for 19th-c rabbinical print CPU-only is an **open measurement** — do not accept a number without its corpus and page set.
- **Tailscale:** **Grants are GA and preferred**; ACLs "continue to function indefinitely" → non-breaking drift, not outage risk. Our `acl.hujson` uses legacy `acls` with explicit `action: accept` — mechanically mappable, with a policy `tests` section and a console "Preview rules" tab available.
- **EU AI Act:** Art. 50 transparency **applies from 2026-08-02** (six weeks ago) and explicitly enumerates **coding agents**; GPAI obligations from 2025-08-02; high-risk dates deferred by the 2026 Digital Omnibus (+16/+24 months). **Operative exemption:** *purely personal, non-professional activity* → a single-operator private system is very likely out of scope. **Two caveats:** (1) *open-source systems are not exempted* from the obligation — the personal-use carve-out is the deployer's; **publish this and the analysis inverts**; (2) Art. 50(1) names coding agents directly. Fines up to €15M / 3% turnover. **The trigger to revisit is publication, not operation.**

---

## 7. DRIFT TABLE (decision-relevant)

| # | We believed | True now | Changes a decision? |
|---|---|---|---|
| 1 | Ollama 0.33.3 current | **0.34.4** — single-pass structured outputs on thinking models; prompt caching decoupled from context shift | **Yes** — bears on persona JSON reliability; upgrade + re-bench |
| 2 | P-core-only mask breaks it *because of #17916* | #17916 = **thread count vs cgroup CPU budget** → CFS convoy | **Yes** — restate as a *budget* rule |
| 3 | CVE-2026-27940 unknown | High 7.8, GGUF `mem_size` overflow, RCE demonstrated, patched ≥ b8146 | **Yes** — pipeline is the exposure |
| 4 | CVE-2026-21869 is 8.8 High | GitHub rates it **Low** | Reconcile; use patched-version fact |
| 5 | FTS5 indexes Hebrew correctly | Niqqud → 25 tokens for Gen 1:1; `remove_diacritics` no effect | **Yes, urgently** |
| 6 | sqlite-vec brute-force only | 0.1.9 local = brute-force ✅; upstream added IVF + DiskANN (leak fix) | Re-evaluate at scale |
| 7 | qwen3-0.6b chosen on federation grounds | Independently right on **CPU throughput**; Hebrew quality **unmeasured** | No change; build the eval |
| 8 | MCP = sessions + handshake | **2026-07-28 stateless**; sessions/GET-stream/handshake removed | **Yes** — inspect `omega-hub` |
| 9 | Background curator needs bespoke protocol | **MCP Tasks** extension exists | **Yes** — evaluate first |
| 10 | Target DDR5-5600 **CL40** | Validated 32GB = **CL46** | **Yes** — before money is spent |
| 11 | RAM ceiling ~32GB | ASUS max **64GB**; 128GB out-of-spec | Yes |
| 12 | OCR = Tesseract/Paddle | **Kraken/eScriptorium** is the historical-print instrument | **Yes** |
| 13 | No EU AI Act obligations in 2026 | Art. 50 live; personal-use exempt; **open-source release voids it** | No action now; trigger is publication |

---

## 8. RANKED ACTIONS

**Tier 0 — correctness (act now)**

| # | Action | Effort |
|---|---|---|
| **R1** | **Fix Hebrew FTS5 normalization**: strip U+0591–U+05C7; normalize maqaf U+05BE; apply symmetrically to query path; re-index | ~2h |
| **R2** | **Restate the CPU-pin rule as a budget rule** in `AGENTS.md` + Well seed `bbf9147e`; reconcile with `e9ece119` | ~30min |
| **R3** | **Add CVE-2026-27940 + GHSA-96jg-mvhq-q7q7** to hardening docs; reconcile the 21869 severity; SHA-256 verify every GGUF before load | ~1h |
| **R4** | **Upgrade Ollama 0.33.3 → 0.34.4**, then re-run `make bench` to confirm 14.4 t/s survives | ~1h |

**Tier 1 — architecture-shaping**

| # | Action | Effort |
|---|---|---|
| R5 | **Inspect `omega-hub:8016` for MCP session dependence** (code task) | ~2h |
| R6 | **Build a 30–50 query Hebrew retrieval eval** (vocalized Gen 1:1, a Racbinic passage, unvocalized Rabbinic) — qwen3-0.6b vs GTE-multilingual-base | 3–4h |
| R7 | **Buy 2×16GB DDR5-5600 CL46** (KVR56S46BD8-32 ×2) | ~€60–90 |
| R8 | **Evaluate MCP Tasks** for the background curator before designing bespoke protocol | ~2h |
| R9 | **Switch the 19th-c rabbinical OCR path to Kraken/eScriptorium** | ~4h |

**Tier 2 — opportunistic:** R10 migrate `acl.hujson` to `grants` + policy tests; R11 document the `:11434` tailnet exposure as deliberate risk acceptance; R12 re-evaluate sqlite-vec at scale + delete-correctness test if ANN adopted; R13 pin llama.cpp advisory mapping to v0.5.0 vs `bNNNNN`.

---

## 9. OPERATOR DECISIONS

| # | Decision |
|---|---|
| D1 | Must `omega-hub:8016` keep working with pre-2026-07-28 MCP clients? (compat shim vs clean adoption) |
| D2 | Is Ollama-over-tailnet (`:11434` from Node 0) worth the widened CVE surface? Alternative: loopback + SSH/tailscale-local tunnel |
| D3 | Upgrade Ollama now, or pin 0.33.3 until a clean bench window? |
| D4 | **Maqaf policy: index as two tokens or one?** A corpus-semantics call — does `וְהָיָה־כֵן` match as a unit? |
| D5 | Preserve niqqud in canonical Markdown (recommended yes) while stripping only for the FTS index? |
| D6 | 32GB (2×16) or 64GB (2×32)? 32GB is the measured-relevant step; 64GB is the ceiling and enables a 12B class later |
| D7 | **Is this system ever going to be released?** If yes → EU AI Act provider-side obligations enter scope and the personal-use exemption is void. The single largest hidden-cost branch in this report |
| D8 | Is the grimoire corpus vocalized or consonantal? Changes R1's normalization design |

---

## 10. OPEN QUESTIONS

| # | Question | Close it by |
|---|---|---|
| Q1 | Does `omega-hub:8016` depend on sessions/handshake? | **Code inspection** (grep `session`, `Mcp-Session-Id`, `initialize`) |
| Q2 | Is OWUI v0.11.3 affected by CVE-2026-0767 / -44549 / GHSA-4r2p-27mh-5m22? | Fetch vendor-disclosure pages for the three IDs |
| Q3 | Does speculative decoding help *this* node? | Local A/B, same prompt, 8 threads. Do not port the Xeon number |
| Q4 | Does llama.cpp in 0.34.x change the spin-wait/CFS behaviour? | `make bench` after R4 |
| Q5 | Realistic CER on 19th-c rabbinical print, CPU-only? | Kraken baseline on ~20 pages against a known transcription |
| Q6 | 2026 BIOS/firmware change affecting P/E scheduling on P1503CVA? | ASUS support BIOS history |
| Q7 | Which CRDT / replication approach for two always-on nodes? | **Not researched this pass** — evaluate Automerge (Python), Yrs (has Python), rqlite on: SQLite backing, offline-first merge, 2-node maturity |
| Q8 | Tailscale 2026 changes to NFSv4.2 / `serve` / `funnel`? | Not researched; no regression signal found |
| Q9 | Cline / Antigravity / Grok CLI MCP parity since 2026-09-23? | No data exists for a 2-day window; re-query late October |
| Q10 | Is there a Judeo-Aramaic OCR model? | Kraken registry + Zenodo. If none: transliteration-first digitization with human review |
| Q11 | Which 3B–8B model is actually best for persona embodiment on *this* CPU? | **Local bake-off**: 4 candidates × 3 prompt types (long-form persona, structured JSON, ritual/creative), same seed/temp, scored against the 4-voice DNA |

---

## 11. THE VERDICT THAT MATTERS MOST

The FTS5 finding is the most dangerous item here **precisely because nothing is failing loudly**. Twenty-five tokens for Genesis 1:1, and `remove_diacritics` making no difference at all — a retrieval system reporting success while returning character soup. BM25 does not error on garbage input; it confidently ranks it. This is the inverse of the Well's own `bad5375d` warning: not repeated probing without new information, but **information that never enters the probe at all**. It has been shipping.

And the most expensive thing to get wrong is not a CVE: **DDR5-5600 CL40 32GB SODIMM is not a validated part for this chassis.** Every 32GB option is CL46. The dual-channel step is the single highest-leverage change available — it roughly halves a full embedding pass with no code — and it should be specified correctly the first time.
