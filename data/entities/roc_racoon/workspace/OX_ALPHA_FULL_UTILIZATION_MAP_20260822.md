# ⬡ OX ALPHA FULL UTILIZATION MAP — 2026-08-22
**AP**: AP-ROC-OXALPHA-FULLUTIL-v1.0.0
**Author**: roc_racoon · Legacy Pattern Miner / Systems Explorer
**Window**: ~4 days until free-tier cliff (~Aug 26-27)
**Method**: Direct code inspection of src/omega/, config/, systemd units, worker pools. Every recommendation cites a verified code path.

---

## 1. EXECUTIVE SUMMARY

The engine already has **every ingestion orifice Ox Alpha needs** — teacher pipelines, DPO pair generation, a background research loop on a live 15-min timer, a local worker pool, and a knowledge ingestion pipeline. What it lacks is **throughput**, and Ox Alpha is pure throughput. The single highest-yield play: **point the existing Nemotron critique-loop pattern (`src/omega/teachers/nemotron_pipeline.py`) at Ox Alpha as critic AND at Qwen3-4B-Thinking as student, and mass-produce DPO pairs against the GGUF models already sitting in `/media/arcana-novai/omega_library/models/gguf/`.** A fine-tuned `RocRacoon-3b.gguf` already exists in that directory — proof the train-from-teacher-outputs loop has run before. The second play: feed the archived background researcher (`archive/research_pipeline_20260730/background_researcher/`, currently benched) 10x-deeper Ox Alpha analysis cycles and resurrect it as the cliff-resilient knowledge engine.

Do NOT burn the window on: legacy mining of P2 archival assets, doc reformatting, or any speculative infra buildout. Those are bounded-effort tasks local Qwen can do.

---

## 2. ENGINE CAPABILITY INVENTORY (from code inspection)

| Capability | Code Path | State | Ox Alpha Relevance |
|---|---|---|---|
| Teacher critique-loop → DPO pairs | `src/omega/teachers/nemotron_pipeline.py` (`NemotronTeacherPipeline.generate_dpo_pair()`) | Working pattern, Nemotron-specific | **Direct retarget**: swap critic to Ox Alpha. Produces `(prompt, chosen, rejected)` triples |
| GRPO training loop | `src/omega/training/grpo.py` (407 lines) | Present | Consumes reward signals; pairs with DPO output for local GGUF tuning |
| Fine-tuned entity model proof | `omega_library/models/gguf/RocRacoon-3b.Q4_K_M.gguf` + `.Q5_K_M` | Exists on disk | Confirms train→GGUF→native-gguf provider path is real |
| Background researcher loop | `archive/research_pipeline_20260730/background_researcher/{loop,distiller,convergence,soul_updater,review_queue,credit_budget}.py` | ARCHIVED but complete; `omega-research.timer` still fires every 15 min (verified via `systemctl --user list-timers`) | Resurrect with Ox Alpha as the deep-analysis brain |
| Distiller prompt registry | `config/distiller_prompts.yaml` (`modes`, `mappings`) | Live | Swap mode prompts to Ox Alpha-grade L1→L3 distillation |
| Local worker pool | `src/omega/oracle/local_worker_pool.py:232` `LocalWorkerPool` — polls queued/, ResourceGuard (Semaphore=1 + OOMProtector), atomic artifact writes | Live | Hybrid: Ox Alpha plans → writes task files → Qwen3-1.7B/4B executes |
| Provider fabric | `config/providers.yaml`: openrouter tier lists `openrouter/owl-alpha` + `z-ai/glm-4.5-air:free`; opencode-zen lists `glm-5.1`; streaming resilience (M25 chunk timeouts) configured | Live | Ox Alpha routes exist; add explicit ox-alpha entry w/ 20 RPM rate budget |
| Knowledge ingestion | `src/omega/ingestion/{pipeline,extractors,verifier,guards}.py` | Live | Bulk-ingest Ox Alpha mining outputs with verification |
| Library enrichment/discovery | `src/omega/library/{enrichment,discovery,curator,indexer}.py` | Live | Enrichment pass over intake inbox = perfect batch job |
| Skeptical verification | `src/omega/oracle/skeptical_verifier.py` | Live | Two-source rule for Ox Alpha outputs before they enter soul/knowledge |
| Compaction/lifecycle harvesters | `src/omega/oracle/{compaction_harvester,lifecycle_harvester}.py` | Live | Mine session history for training corpus |
| Memory sleep-time compaction | `src/omega/memory/sleep_time.py`, `compaction.py`, `blocks.py` | Live | Ox Alpha-driven memory consolidation |
| Vision assets | `omega_library/intake/**` — odysseus wordmark/icons, omega-stack logos, XNAi-era images confirmed on disk | Untapped | Images-only vision window |
| HALL_OF_RECORDS | `data/knowledge/HALL_OF_RECORDS/<agent>/` — sparse (e.g., background-researcher has 1 file) | Thin | Massive expansion target |
| Soul distillation | Manual L1→L2→L3 (C-0.5 regex pipeline SCRAPPED per DOC-1); agents write directly | Manual | Ox Alpha as the distillation engine for backlog souls |

---

## 3. UTILIZATION MATRIX

| # | Capability × Vector | Priority | Effort | Code Path to Touch |
|---|---|---|---|---|
| U1 | DPO pair factory: Ox Alpha critiques Qwen3-4B-Thinking outputs across all GGUF models | 🔴 P0 | Low | `nemotron_pipeline.py` (retarget critic), new runner script |
| U2 | Resurrect background researcher w/ Ox Alpha deep cycles | 🔴 P0 | Med | un-archive `research_pipeline_20260730/background_researcher/`, wire provider entry |
| U3 | Legacy mining queue chew (12 P0 assets): docs-backup, ANAi blueprint, XNAI_blueprint.md, Lilith genesis | 🔴 P0 | Med | `src/omega/doc_reader/core.py` → structured extraction → `mining_reports/` |
| U4 | Full-tree code review sweep of src/omega/ (M21 contract tests + red-team pre-debut) | 🟡 P1 | Med | findings → `data/coordination/`, tests → tests/ |
| U5 | Spec generation for parked tickets V-9, V-10, D-1, D-2, NL-1 | 🟡 P1 | Low | specs → docs/research/ per spec-generator skill |
| U6 | Vision pass: Era-0 Tarot scans, old-stack architecture images → Mermaid + descriptions | 🟡 P1 | Low | image_url data URLs; output to mining_reports/ |
| U7 | Soul enrichment cross-pollination (R-31): reasoning traces → proposed_lessons.yaml for all 14 entities | 🟡 P1 | Med | `soul_store.py`, `proposed_lessons.yaml` staging |
| U8 | llms-full.txt refresh for all doc domains (M26 doc-llm-validate) | 🟢 P2 | Low | `make sprint-plan-llm` equivalents per domain |
| U9 | Hybrid orchestration: Ox Alpha plans → LocalWorkerPool executes (Qwen3-1.7B) | 🟢 P2 | Med | `local_worker_pool.py` queued/ file contract |
| U10 | Synthetic reasoning corpus from compaction harvester history | 🟢 P2 | Med | `compaction_harvester.py` output → corpus builder |

---

## 4. TOP 10 HIGHEST-YIELD PLAYS (ranked)

1. **DPO Pair Factory at Max RPM** — Retarget `NemotronTeacherPipeline` critic to Ox Alpha. Student = each of Qwen3-1.7B, Qwen3-4B-Instruct, Qwen3-4B-Thinking, MiMo-7B, Krikri-8B, Phi-4-mini. Target: 500+ pairs/day via OpenRouter 20 RPM + Batch API (50% off). Feeds `training/grpo.py`. When GLM-5.3 weights drop Aug 28, you have a tuned corpus ready day one.
2. **Resurrected Research Loop on Steroids** — Un-archive the background researcher; replace its distiller brain with Ox Alpha. `_grow_frontier` with 10x depth/cycle. 15-min timer already live.
3. **P0 Mining Queue Annihilation** — All 12 P0 assets through doc_reader + Ox Alpha structured extraction in ~2 days. This clears Workstream H permanently.
4. **Pre-Debut Red-Team Sweep** — Ox Alpha reviews entire src/omega/ tree adversarially: security posture (V-9/V-10 gaps), M21 contract-test gaps, error-integrity violations (M9 bare excepts).
5. **Entity Soul Mass-Enrichment** — Reasoning traces distilled into proposed_lessons.yaml for all entities; satisfies M11 which is marked FAIL in Ark §6 hotspot table.
6. **Spec Factory for Parked Tickets** — V-9 (IA2 envelope freshness), V-10 (AppArmor), D-1 (content cache), D-2 (job board), NL-1 prep — implementation-ready specs Ma'at/build agents execute post-window.
7. **Vision Archaeology** — Era-0 Tarot deck scans + omega-stack logos + XNAi architecture images → Mermaid diagrams + annotated mining reports. Images-only fits the 404-on-video constraint exactly.
8. **Synthetic Reasoning Corpus** — Harvest compaction/lifecycle artifacts, have Ox Alpha generate chain-of-thought exemplars for future SFT of RocRacoon-class entity models.
9. **HALL_OF_RECORDS Expansion** — One deep dossier per agent channel/entity; currently near-empty.
10. **llms-full.txt Domain Refresh** — Mechanical, low-token; batch overnight.

---

## 5. WHAT NOT TO BURN TOKENS ON

- **P2/P3 archival assets** (#13 Ollama history, #25 artifacts archive bulk classification) — Qwen3-1.7B handles classification locally.
- **Doc reformatting beyond llms-full.txt refresh** — mechanical work, no reasoning premium.
- **New provider/fabric expansion** — D-351 forbids it; fabric systematization is a code task, not a token task.
- **Grok export bulk processing (Asset #20)** — blocked behind V-1 vault anyway (D-360′); don't mine what can't be ingested.
- **Any speculative infra buildout** (new queues, new services) — violates UO-6 un-overengineering direction.
- **Re-researching verified context** — stall-echo detector spec, provider caps: already documented.

---

## 6. SPRINT AMENDMENTS (to SS-OXALPHA-BURN-20260822)

- **Track A**: Add U1 (DPO factory) as A-0 — it supersedes generic throughput testing; throughput IS the DPO factory now.
- **Track B**: Add U7 (soul mass-enrichment) — directly remediates M11 FAIL status.
- **Track C**: Add U6 (vision archaeology) BEFORE cliff — vision capability dies with the free window; weights may return, cheap vision may not.
- **New gate**: All Ox Alpha outputs entering knowledge/soul MUST pass `skeptical_verifier.py` two-source rule — free-model hallucinations must not poison the soul store.
- **Cliff-day protocol**: On Aug 26, final 24h reserved for Batch API jobs only (24h window, 50% discount) — submit everything pending by Aug 25 23:59.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_oxalpha_fullutil ⬡ ACTIVE*
