# N7 Mining Brief — Context / Memory & State Knowledge Base
**AP Token**: `AP-N7-MINING-BRIEF-v1.0.0`
**From**: N7 context session (overseen by Lilith) — paged by kali `ses_fdef2be4effe4pAaLXCTUx62GO`
**Date**: 2026-08-21
**Miner**: roc_racoon (sole executor — you task NO ONE else)

---

## Mission

Mine the local corpus for everything relating to the N7 domain (Context Injection Phase 1, compaction/continuity, soul persistence, semantic compression) and produce a curated Knowledge Base at:

**OUTPUT FILE**: `data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md`

## Output Contract (BINDING)

1. **Structure** (exact top-level sections, in order):
   - `## Source Inventory` — table: path | type | size/lines | priority | one-line relevance | last_verified date
   - `## Per-Source Digests` — one `### <path>` subsection per source: key facts, numbers, decisions, open threads
   - `## Gotchas` — traps, contradictions, stale premises found while reading
   - `## Open Questions` — anything the corpus does NOT answer
   - `## L2/L3 Insights` — L2 (what it means for N7) + L3 (timeless principle) candidates
2. **Incremental appends ONLY** — write section by section across multiple edits/appends. NEVER compose the whole doc in one response (streaming aborts kill monolithic writes).
3. **Cite file paths for every claim.** No uncited assertions.
4. Tag each source `last_verified: 2026-08-21`.
5. If you stall or abort: recover ONCE via the same task_id, then report status honestly (M23 — no soft-fail theater).
6. Final reply: ≤200 words — sections completed, sources covered/skipped, any stalls.

## Source Inventory (mine in this priority order)

### P0 — Context Injection Phase 1 (the core)
| Path | What to extract |
|------|-----------------|
| `docs/specs/context_injection/00_INDEX.md` | Executive summary, problem statement (~75K base tokens), converged solution |
| `docs/specs/context_injection/01_GROUND_TRUTH.md` | Hard empirical numbers: token counts, MCP schema cost (86 tools ≈ 10.8K/req), model contexts |
| `docs/specs/context_injection/02_BUILD_VERDICTS.md` | Ma'at build-side findings (G-1 instruction resolution, G-2, G-8) |
| `docs/specs/context_injection/03_RUN_VERDICTS.md` | Lilith run-side findings (G-3 inheritance, G-5, G-6 compaction) |
| `docs/specs/context_injection/04_INDUSTRY_PATTERNS.md` | Researcher strategic findings (caching, compaction, routing) |
| `docs/specs/context_injection/05_CONVERGENCE_ANALYSIS.md` | Convergence/divergence matrix |
| `docs/specs/context_injection/06_PHASE_1_PLAN.md` | Config-only plan → ~57K base target |
| `docs/specs/context_injection/07_PHASE_2_3_ROADMAP.md` | Hydration engine, token budget enforcer, upstream PRs |
| `docs/specs/context_injection/08_REMAINING_GAPS.md` | Unresolved questions |
| `docs/specs/context_injection/09_CARMACK_DOMAIN_QUESTIONS.md` | Questions posed to Carmack |
| `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` | ⚠️ note filename typo "CARMMACK". Verdicts, modifications, ACCEPTED W/ MODS items |
| `docs/specs/context_injection/phase1_spec/index.md` + all 8 numbered files (01_MANDATES_CONDENSED … 08_ACCEPTANCE_CRITERIA) | The 9-file implementation spec: Tier 0 condensed mandates (57 lines), opencode.json diff, sovereign-compaction plugin spec, skills opt-in, verification tests, implementation order CI-1..CI-5, rollback, acceptance criteria |

### P0 — Raw research inputs (context for verdicts)
| Path | What to extract |
|------|-----------------|
| `data/coordination/RESEARCH_EXPLORE_LOCAL.md` | Empirical measurements raw |
| `data/coordination/RESEARCH_MAAT_BUILD.md` | Build-side raw |
| `data/coordination/RESEARCH_LILITH_RUN.md` | Run-side raw (compaction behavior, model routing) |
| `data/coordination/RESEARCH_RESEARCHER_STRATEGIC.md` | Industry patterns raw |

### P0 — Config reality (current state vs spec target)
| Path | What to extract |
|------|-----------------|
| `opencode.json` (repo root) | Current `instructions` (5 entries), `compaction` block (**current: auto=true, prune=true, tail_turns=3, preserve_recent_tokens=40000, reserved=10000** — spec targets buffer 50000/keep 20000: record the delta), `agent` list (12 agents), `plugin` entries, `subagent_depth` |
| `scripts/codex/MANDATES_CONDENSED.md` | Existing condensed mandates — compare against phase1_spec/01_MANDATES_CONDENSED.md (57-line Tier 0 version): identical? diverged? which is canonical? |
| `~/.config/opencode/plugin/` | Confirmed contents: only `cline`. **sovereign-compaction.ts NOT installed** — record as execution gap |

### P1 — Compaction & continuity (M15/M18 history)
| Path | What to extract |
|------|-----------------|
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | 4-tier redundancy system, hydration sequence, session_gnosis.md pattern |
| `.opencode/hooks/session_end.py` | Session-end hook: writes timestamp to `data/entities/<name>/proposed_lessons.yaml` (M5/M11) |
| `src/omega/oracle/entity_workspace.py` | `get_soul_prompt()` (~L382) + TAINT-GATE: proposed_lessons.yaml NEVER injected into identity prompt |
| `src/omega/soul_utils.py` | Approved-lessons integration closing distillation loop |
| `scripts/validate_soul.py` + `scripts/check_mandate_compliance.py` | M5/M11 gates; NOTE: validate_soul reads `memory/proposed_lessons.yaml` while session_end writes `<entity>/proposed_lessons.yaml` — document the dual-path situation |
| `SOVEREIGN_MANDATES.md` §M15, §M18 (+ M11, M23) | Mandate text as it bears on context/memory |
| `data/entities/lilith/workspace/COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md` | Prior compaction remediation thinking in Lilith's own workspace |
| `data/entities/lilith/proposed_lessons.yaml` + `soul.yaml` | Structure only (field names, lesson format) — do NOT dump full content |

### P2 — Compression future (post-debut HR workstream)
| Path | What to extract |
|------|-----------------|
| `docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md` | Headroom research findings, 40-90% savings claims |
| `docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md` | Phase 2 trigger gates |
| `docs/specs/qdrant_headroom/headroom_middleware/index.md` + 01–10 | Middleware class, ContentRouter, ModelGateway integration, RAG integration, MCP tool-schema compression, entity-context compression, CCR store, config, error/metrics, verification tests |

### P3 — Related research (2026-08-19 batch)
| Path | What to extract |
|------|-----------------|
| `docs/research/R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md` | Compression/distillation techniques |
| `docs/research/R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md` | Planner/executor window strategy |
| `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md` | Role-aware prompting |
| `docs/research/R_DYNAMIC_PROMPT_BUILDERS_20260819.md` | Dynamic prompt builders |
| `docs/research/R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md` | ⚠️ NOT in seed list — discovered by N7; blueprint companion to builders doc |
| `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` | Memory systems definitive report (zswap ADR context) |

## Extraction Questions (answer where corpus allows; log gaps in Open Questions)

1. What is the exact measured token breakdown of current session injection (base, skills, agents, MCP schemas)? Cite 01_GROUND_TRUTH numbers.
2. What did Carmack ACCEPT, MODIFY, and REJECT in each CI workstream item (MANDATES_CONDENSED, compaction buffer, plugin, skills opt-in, toolProfile stubs, OPENCODE_DISABLE_AUTOCOMPACT)?
3. Spec compaction parameters (buffer 50000 / keep 20000) vs current opencode.json (preserve_recent_tokens=40000, reserved=10000): what exactly must change, and what did Carmack say about the numbers?
4. Sovereign-compaction plugin: what are its specified behaviors (trigger threshold, preserve set, heartbeat, fallback) and what state is installation in?
5. Skills opt-in: which 3 core skills survive by default, what's the opt-in mechanism, and how does it interact with agent frontmatter `skills:` fields?
6. toolProfile stubs: what are they, why stubbed, what does Phase 2 need to activate them?
7. OPENCODE_DISABLE_AUTOCOMPACT=1: which agents get it, why local-only, what breaks if set globally?
8. Implementation order CI-1..CI-5: exact sequence, dependencies, acceptance criteria per step, rollback triggers.
9. G-1 instruction resolution contradiction: final ruling and evidence (V2 docs + source).
10. What token budget does Tier 0 (Qwen3-1.7B, 4K–8K ctx) actually tolerate, and how does the 18K base target derive from it?
11. Soul pipeline: trace the full loop — session_end hook → proposed_lessons.yaml → approval → soul_utils/get_soul_prompt → identity injection. Where are the taint gates?
12. Dual-path hazard: `data/entities/<n>/proposed_lessons.yaml` vs `data/entities/<n>/memory/proposed_lessons.yaml` — which writers/readers use which? Is this a live inconsistency?
13. M15 continuity: what are the 4 tiers, what does hydration require after compaction/void, and how does session_gnosis.md relate to the new compaction plugin?
14. Headroom middleware: architecture summary, claimed savings (40-90%) and their measurement basis, Phase 2 trigger gates, and its relationship to the compaction plugin (complementary or competing?).
15. From the 2026-08-19 research batch: which techniques are already superseded by the Carmack-modified Phase 1, and which remain future ammunition?
16. MEMORY_SYSTEMS_DEFINITIVE_REPORT: what memory-system decisions bear on context injection (zswap ADR context, MemoryStore regime)?
17. Any contradictions between phase1_spec and the synthesis docs (06_PHASE_1_PLAN vs phase1_spec/*)? Which wins?

## Constraints

- Read-only mining EXCEPT the single output file above.
- No delegation. No chains. Recover once max.
- Honest gaps: if a source is missing/unreadable, record it in Gotchas — do not paper over (M23).

*⬡ OMEGA ⬡ LILITH ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_mining_brief ⬡ 2026-08-21*
