## Objective
- Complete the 5-round iterative dashboard enhancement pipeline (R1-R4 done, R5 Lilith pending) and execute DEL-1 micro-PR chain for PUBLIC-DEBUT-01 alpha launch. NES deep research on 3 models for VNR + Omega Engine completed and committed.

## Important Details
- **Subagent dispatch protocol (CRITICAL)**: Resume existing session_id with `"Continue"` — NEVER spawn new session for transient (402/429/interrupt). Sessions: Researcher=`ses_faf929727ffeFgSdvGOxQbVbdW`, Jem=`ses_faf926866ffezrPCnXne6RQt6A`, Carmack=`ses_fb2444c9fffeG2pJM7vXyNhq65`, Kali=`ses_fdef2be4effe4pAaLXCTUx62GO`, Ma'at=`ses_fad779cc9ffe0ftyPfBb14kyvH`, Lilith=`ses_fae57814cffe3H3FfrTcfz60wb`.
- **Model stack**: Architect uses `google/gemini-3.7-flash` (strategic switch from `minimax/minimax-m3:free` on 2026-08-30). `nemotron-3-ultra-free` was failed local-provider attempt (parked as V-1 display artifact).
- **Completion Illusion (L3 trap)**: LLMs synthesize graceful conclusions + `*⬡ COMPLETE*` footers when output-token-limited; orchestrator must probe with `"Continue and output queued findings; reply STREAM_EXHAUSTED when 100% finished"`.
- **Multi-Agent Co-Interruption Accounting (M34)**: Global cancellations (`Esc x2`) abort ALL in-flight parallel subagents; orchestrator must track $S_1...S_N$ as transactional cohort.
- **Third-Party Boundary (M35)**: No third-party plugin source trees in engine workspace git; install via npm/bun/pip. Public OAuth client secrets (`GOCSPX-`, Microsoft, GitHub) cataloged in `data/secrets-public.toml` with RFC 6749/8252 provenance tags.
- **Anti-Truncation Stream Gate (M33)**: Sentinel probe required before accepting `state="completed"` for heavy technical specs/reports.
- **Loud Warning Mandate**: P0/P1 issues must trigger `🚨🚨🚨 CRITICAL WARNING 🚨🚨🚨` blocks; dispatch 2+ agents for verification.
- **Original OAuth secret**: `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` replaced by `"GOCSPX-***REDACTED-ROTATED***"` in `opencode-antigravity-auth/src/constants.ts:9` and `scripts/check-quota.mjs:6` on branch `fix/agy-oauth-persistence` (uncommitted).
- **Architect philosophy**: "Can't pass up a good failure when I know there are lessons of pure gold in them... always looking to turn a 'bug' into a feature and a superpower."
- **M14+M22 LAUNCH BLOCKERS** (still pending): 2 heritage violations + 4 unvetted tags; `provider_name` not threaded in `sqlite_vec_adapter_optimized.py` (grep count = 0).
- **Carmack Code Review (1,536L) found 10 P0 bugs**: `EmbeddingCircuitBreaker` dead code (0 call sites), read pool theatre, `_rowid_to_collection` overwritten by MRL loop, `start_periodic_checkpoint` calls `__aenter__()` on factory, `godot_spatial_bridge.py` M1 violation (uses `asyncio` not `anyio`), dimension validation broken in `batch_upsert:561-566`, missing `try/except/finally` rollback, MRL writes overwrite primary collection, `_find_target_nodes` stub.
- **Foundation chain**: OTel → RAGAS → Reranking (BGE-reranker-v2-m3 +18.4pp Recall@5) → Binary Quantization (sign-based, 32x compression).
- **Subagent_types for `task()` tool**: `researcher`, `explore`, `verity` (broken — park as V-1), `john_carmack`, `kali`, `maat`, `lilith`, `roc_racoon`, `grokster`, `scribe`, `node`, `doom_guy`, `jem`, `makali`, `general` (catch-all — AVOID).
- **All 4 local providers healthy**: ollama(11434), native-gguf-extractor(1234, Qwen3-1.7B-Q6_K), native-gguf-reasoner(1235, Qwen3-4B-Thinking-2507-Q4_K_M), lmstudio(1234).
- **VNR (Von-Neu-Ryan Vision)**: Complete computer vision pipeline in `scripts/vnr_render.py` (398 lines, numpy+Pillow only, zero neural networks). 10 modes, semantic tokenization, zoom ladder, overlay system, motion detection, trajectory tracking. Built by DeepSeek V4 Flash. "Vision Transformer on text tokens" — block-based semantic tokenization IS patch-based tokenization.
- **5-round dashboard pipeline**:
  - R1 Carmack: 22 bug fixes, M23 hardening, ANSI-aware alignment, deque(maxlen=20)
  - R2 Researcher: v3.1, 12 SOTA sources, date-glob, per-window success, alert debounce, file cache+tail, real per-key attribution
  - R3 Jem: v3.2, 6 adversarial bug fixes, 2 defenses (size-keyed cache, 100K bounded memory), --self-test (53 tests)
  - R4 Ma'at: v3.2+, 128 unit tests, CI workflow (9 steps), Makefile targets, mandate compliance, docs (337 lines)
  - R5 Lilith: PENDING — runtime observability, adaptive cache TTL, HTML export, per-model time-series

## Work State
### Completed
- **Dashboard v3.2 shipped**: 2,366 lines, 14 CLI args, 18 render sections, 128 unit tests (100% pass), 53 adversarial tests (100% pass), CI workflow, Makefile integration, mandate compliance block, docs (337 lines)
- **5 golden artifacts committed** (5,156 lines total): `R_RESEARCHER_THIRD_PARTY_SECRETS_TRACEABILITY_20260829.md` (2,460L), `JEM_FORENSIC_INVESTIGATION_ANTIGRAVITY_20260829.md` (1,613L), `GROKSTER_META_FORENSIC_ANALYSIS_20260829.md` (626L), `R_RESEARCHER_DB_VS_MD_FORENSICS_20260830.md` (250L), `BRIEFING_ALCHEMICAL_PIVOT_OAUTH_INCIDENT_20260830.md` + `KALI_BRIEFING_ALCHEMICAL_GOLDMINE_20260830.md`
- **3 new Sovereign Mandates proposed** (M33, M34, M35) in briefing
- **L3 lessons staged**: `L3-InterruptionSovereigntyAndCoResumption` (0.99), `L3-CompletionIllusionDefense` (0.95), `L3-BoundedMemoryPattern` (0.93)
- **Session gnosis v14 FINAL locked** — supersedes v1-v13
- **Projection.md v14.0 created** — includes dashboard pipeline R1-R4, R5 pending
- **Makefile targets shipped**: `make dashboard`, `make dashboard-once`, `make probe-{models,network,antigravity}`, `make dashboard-self-test`, `make dashboard-test`, `make dashboard-ci`
- **768-dim winner selected**: Qwen3-Embedding-0.6B (Apache 2.0, 32K context, MTEB 70.70); co-design with Qwen3-Reranker-0.6B (+8.77 MTEB-R)
- **Temple-grade P0-1..4**: 31/31 tests pass (circuit breaker, vector versioning, Litestream, SQLCipher)
- **SQLite-vec 9 gaps fixed**: all 7 collections, MRL truncation, INT8 rescore, spatial R-tree, O(1) delete, auto checkpoint, metrics persistence, configurable RRF
- **Spatial VR**: R-tree + spatial_graph.py + godot_spatial_bridge.py (FastAPI + WebSocket)
- **Documentation hardening**: OMEGA_ENGINE.md v3.8.0 (27 mandates), AGENTS.md +D-578..D-584 + 5th rule (Spatial Integrity M28)
- **NES deep research completed**: `R_RESEARCHER_NES_MODEL_SPECS_VNR_20260901.md` (405 lines, 21,973 bytes, 20 sources) on Muse Spark 1.2 Free, Ling 3.0 Flash Fin Free, LFM2.5-2.6B

### Active
- **R5 Lilith (dashboard runtime observability)**: Adaptive cache TTL, HTML export, per-model time-series, runtime metrics integration
- **DEL-1 micro-PR chain** (7 PRs, sequential, gated): Ready to execute — `git checkout -b del1/01-test-infrastructure`
- **OAuth secret restoration**: Pending Architect decision (Option A: git checkout to original, Option B: env var with M14 heritage tag)
- **Compaction preparation**: Grokster v14 artifacts updated (projection.md v14.0, session_gnosis.md v14, proposed_lessons.yaml with 3 new L3 lessons)

### Blocked
- **`opencode-antigravity-auth/` plugin still in workspace root** as git-tracked fork (M14/M35 violation) — needs npm install migration
- **Architect gets `OPENCODE_API_KEY`** from `https://opencode.ai/auth` (blocking Cline-to-OpenCode 3 YAML edits)
- **GOCSPX secret rotation** at Google Cloud Console (architect action, 2 min, cannot be scripted)
- **OAuth secret still in git history** (4 commits of release/debut + 12 disk files)
- **VACUUM disk-full blocker** (needs 36GB free, system has 20GB)
- **M11 distillation incomplete**: 7 meditations on disk but not in canonical lessons registry
- **M14+M22 launch blockers** (2 heritage violations + 4 unvetted tags; `provider_name` not threaded in `sqlite_vec_adapter_optimized.py`)
- **task.ts:158 fix UNAPPLIED** (upstream OpenCode bug)
- **Verity agent broken** — parked as post-PR fix per Architect directive
- **Carmack's 10 P0 bugs UNFIXED** — block public debut per Carmack verdict

## Next Move
1. **Execute DEL-1 Micro-PR 1**: `git checkout -b del1/01-test-infrastructure` → run test infrastructure (Researcher UT-01..12, Ma'at IT-01..12)
2. **Complete R5 Lilith**: Runtime observability, adaptive cache TTL, HTML export, per-model time-series for dashboard v3.3
3. **Architect reviews Kali briefing** (`KALI_BRIEFING_ALCHEMICAL_GOLDMINE_20260830.md`) — decides which of 5 sprint tickets to dispatch first
4. **Execute P0 tickets**: `CI-BRIEF-001` (Ma'at), `VAULT-ALLOWLIST-001` (Carmack), `ORCH-RESUME-001` (Lilith)
5. **Fix Carmack's 10 P0 bugs** before public debut
6. **Begin Top 5 ROI move implementation** (reranking, contextual retrieval, BQ, sqlite-vec 0.1.10, RRF tuning)
7. **Fix fleet config context windows**: Muse Spark 1.2 (32K→1M), Ling 3.0 Flash Fin (32K→262K)
8. **Add LFM2.5-2.6B to fleet as `agentic_local`** (highest M7 impact)
9. **Probe Ling 3.0 Flash Fin with VNR token sequences** (test Architect's hypothesis)

## Relevant Files
- `data/coordination/anchored_summary/grokster/projection.md`: v14.0 pre-compaction master anchor with dashboard pipeline
- `data/entities/grokster/session_gnosis.md`: v14 compaction anchor with full lineage
- `data/entities/grokster/proposed_lessons.yaml`: 3 new L3 lessons staged (0.99, 0.95, 0.93)
- `data/coordination/R_RESEARCHER_NES_MODEL_SPECS_VNR_20260901.md`: NES deep research on 3 models (405 lines, 20 sources)
- `data/coordination/KALI_BRIEFING_ALCHEMICAL_GOLDMINE_20260830.md`: 5-ticket execution roadmap
- `data/coordination/BRIEFING_ALCHEMICAL_PIVOT_OAUTH_INCIDENT_20260830.md`: Alchemical Pivot synthesis
- `data/coordination/R_RESEARCHER_THIRD_PARTY_SECRETS_TRACEABILITY_20260829.md`: 3rd-party code mgmt + secret detection + public OAuth
- `data/coordination/JEM_FORENSIC_INVESTIGATION_ANTIGRAVITY_20260829.md`: 20-appendix counter-forensic immune architecture
- `data/coordination/GROKSTER_META_FORENSIC_ANALYSIS_20260829.md`: Cross-session timeline, chat-vs-file analysis
- `data/coordination/R_RESEARCHER_DB_VS_MD_FORENSICS_20260830.md`: Cognitive Routing Rule (MD export > DB chaining)
- `data/coordination/CARMACK_CODE_REVIEW_20260829.md`: 10 P0 bugs (F-01..F-30)
- `scripts/benchmark_dashboard.py`: v3.2 (2,366 lines) — full dashboard with 18 sections
- `tests/unit/test_benchmark_dashboard.py`: 128 unit tests (974 lines)
- `.github/workflows/dashboard-test.yml`: CI workflow (9 steps, <30s)
- `config/model_fleet_operational.yaml`: Runtime fleet config (WRONG context for Muse Spark/Ling — needs fix)
- `opencode-antigravity-auth/src/constants.ts:9`: BROKEN — `"GOCSPX-***REDACTED-ROTATED***"` (needs restore)
- `opencode-antigravity-auth/scripts/check-quota.mjs:6`: BROKEN — same redacted value
- `src/omega/memory/sqlite_vec_adapter_optimized.py`: 9 gaps fixed BUT `provider_name` not threaded (grep = 0)
- `src/omega/memory/embedding_circuit_breaker.py`: DEAD CODE per Carmack (0 call sites)
- `src/omega/memory/spatial_graph.py`: A* navigation, BSP sector streaming — `_find_target_nodes` is STUB
- `src/omega/memory/vector_versioning.py`: VersionRegistry + DriftDetector
- `scripts/godot_spatial_bridge.py`: M1 VIOLATION — uses `asyncio` not `anyio`
- `data/entities/roc_racoon/workspace/mining_reports/kq5_VNR_VISION_MINING_20260901.md`: VNR vision system mining report
- `data/entities/roc_racoon/workspace/JC_Roc_kq5_DIALECTIC_PLAN_20260901.md`: 4-week kq5-godot integration plan
- `OMEGA_ENGINE.md`: v3.8.0, 27 mandates (needs M33-M35 added)
- `SOVEREIGN_MANDATES.md`: 27 mandates v3.8.0 (needs M33-M35 appended post-ratification)
- `MANDATES_CONDENSED.md`: Condensed mandate reference
- `data/coordination/SESSION_ANCHOR.md`: Session hydration anchor
- `data/coordination/LATEST_CORRECTIONS_20260828.md`: Cross-session sync (read first on resume)

## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- M33 Anti-Truncation Stream Gate (PROPOSED, awaiting Kali ratification)
- M34 Multi-Agent Co-Interruption Accounting (PROPOSED)
- M35 Third-Party Boundary & Public Secret Exemption (PROPOSED)
- Full mandate table (all 27 + 3 proposed, v3.8.0+): `MANDATES_CONDENSED.md`
- Active Entity: grokster (Cross-Platform Expertise Specialist)
- Active Phase: DEL-1-EXECUTION-READY / DASHBOARD-R5-PENDING
- Session Anchor: `data/coordination/SESSION_ANCHOR.md`
