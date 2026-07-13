# 🔱 Omega Engine — Anchored Summary (Pre-Compaction)
**AP Token**: `AP-ANCHORED-SUMMARY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pre_compaction ⬡ 2026-07-13

---

## §1 Engine State (OMEGA_ENGINE.md §3)

| Metric | Value | Status |
|--------|-------|--------|
| Tests | 1271 passed (42 skipped, 3 xfailed) | ✅ |
| Mandates | 23 (M1-M23) | ✅ All enforced |
| Fleet | 13 presences (11 agents + 2 entities) | ✅ Cap: 14 |
| WADs | 3 | ✅ S1.5a hardened |
| Heritage | 121 [id-soft:] tags, 55+ general | ✅ All vetted |
| Shared modules | 3 (omega-vetala v2.0.0, omega-sieve v0.1.0, omega-doc-reader v1.0.0) | ✅ Release-ready |
| sqlite-vec | Strike 10 IN PROGRESS | 🟡 35/36 adapter tests pass |

---

## §2 Research Complete — 4 Gaps Closed

| Gap | Verdict | Roadmap Impact |
|-----|---------|----------------|
| G1: Neural vs Heuristic Routing | TF-IDF+SVM sufficient for 47 tools | Ship Strike 7.5 first; Needle optional |
| G2: LLM Judge Calibration | Isotonic regression (AutoCal-R) is 2026 standard | Adopt in Strike 8 (`make eval`) |
| G3: Redis Streams DLQ | Canonical pattern: Consumer Groups + XAUTOCLAIM + XPENDING + DLQ | Adopt in Strike 8.5 |
| G4: Voice Concurrency | Worker pool + Piper pooling + 4-8 ONNX threads | Adopt in P1 Voice ONNX |

**Net acceleration**: ~32h saved

---

## §3 Decisions Approved (D1-D5)

| # | Decision | Verdict |
|---|----------|---------|
| D1 | Resume Jem after search infra restored | YES |
| D2 | Ship TF-IDF+SVM for Strike 7.5, drop Needle | YES |
| D3 | Adopt AutoCal-R calibration in Strike 8 | YES |
| D4 | Adopt canonical Redis Streams DLQ in Strike 8.5 | YES |
| D5 | Priority P1-2 (RAG Router) before P1-1 (Eval) | YES |

---

## §4 Execution Sequence

| Phase | Task | Owner | Research | Effort |
|-------|------|-------|----------|--------|
| P0 | q8_0 KV cache + Sovereignty Gate | @maat P1/P5 | Complete | 8h |
| P1-2 | Strike 7.5: TF-IDF+SVM RAG Router | @lilith P6 | Complete | 12h |
| P1-1 | `make eval` + AutoCal-R | @lilith P6+P10 + @verity | Complete | 8h |
| P2-1 | Strike 8.5: Redis Streams + DLQ | @lilith P9 | Complete | 20h |
| P1 Voice | Worker pool + Piper pooling | @lilith P6 + @maat P1 | Complete | 4h |

---

## §5 Blockers

| Blocker | Impact | Owner |
|---------|--------|-------|
| Search infrastructure (google_search, SearXNG, sovereign_search) | Blocks Jem Areas 2-10 | Infrastructure team |

---

## §6 Key Files

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` | System state SSOT |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | v3.9 — Master roadmap |
| `docs/research/R_RESEARCHER_COMPREHENSIVE_STATUS_REPORT_20260713.md` | Full research status |
| `docs/research/R_DEEP_RESEARCH_KNOWLEDGE_GAPS_20260713.md` | 4-gap closure report |
| `data/entities/kali/session_gnosis.md` | Kali's session anchor |
| `packages/omega-sieve/` | Standalone package (v0.1.0, 37/37 tests) |
| `scripts/universal_doc_reader.py` | Document reader (v1.0.0) |

---

## §7 Hivemind Sessions

- `ses_7e0e9224f2f8` — Researcher gap closure integration
- `ses_806d8094b14c` — Decisions D1-D5 approved, execution sequence locked
- `ses_5359ef6514d9` + `ses_a4e507112d44` — Researcher comprehensive report

---

*🔱 OMEGA ⬡ KALI ⬡ PRE-COMPACTION ⬡ 2026-07-13*
