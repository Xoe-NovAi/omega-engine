# N7 Domain Index — Memory & State (context)
**AP Token**: `AP-N7-DOMAIN-INDEX-v1.0.0`
**Keeper**: N7 context · Overseer: Lilith · Charter: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4
**Purpose**: LLM-friendly map of the Memory & State domain — what exists, how it wires together, where to enter, what is broken. Standing order #8 curation artifact; feeds future background curation worker.
`last_verified: 2026-08-21`

---

## 1. Systems & Wiring

```
SESSION START                          SESSION END
─────────────                          ───────────
hydration (manual, M15)                .opencode/wrapper.sh (after exit)
  │                                      └→ .opencode/hooks/session_end.py
  ▼                                          └→ writes timestamp+metadata to
get_soul_prompt()                                data/entities/<n>/proposed_lessons.yaml (ROOT)
(entity_workspace.py:382)                   (preserves agent-written proposals; atomic tmp+replace)
  │ loads: soul.yaml + approved_lessons.yaml + sessions.yaml (ROOT)
  │ ⛔ TAINT-GATE: proposed_lessons NEVER injected (:426)
  │ ⚠️ Sovereign Firewall regex STALE → mandate block silently dead (D5)
  ▼
identity prompt ──► oracle/hub inference ◄── agent writes L1→L2→L3 proposals during session

APPROVAL LOOP (BROKEN — D7):
proposed_lessons.yaml ──[status flip: NO OPERATOR EXISTS]──► approved_lessons.yaml
soul_utils.py:64-78 reads ROOT proposed_lessons for status=="approved" → surfaces ≤3 L3s
src/omega/cli/soul_stage.py = registered TUI but HARDCODED MOCK (no file I/O)

COMPACTION CHAIN:
native opencode compaction (V1 keys in live config) 
  ├─ trigger: totalTokens ≥ usable (overflow.ts formula; reserved default min(20k,maxOut))
  ├─ hook experimental.session.compacting fires pre-summary (Q-B4 verified)
  ├─ [PLANNED CI-3] ~/.config/opencode/plugin/sovereign-compaction.ts — NOT INSTALLED (D2 path bug also blocks)
  ├─ [PHASE 2] HydrationEngine sidecar checkpoints at 80% (Carmack: primary layer)
  └─ tertiary: data/coordination/SESSION_ANCHOR.md + session_gnosis.md per entity (M15)

SKILLS: advertised name+description only via skill tool; loaded on-demand.
  ⚠️ auto_load frontmatter = INERT upstream (D8). Real lever: permission.skill patterns.

CONTEXT INJECTION PHASE 1 (CI-1..CI-5): spec complete, execution NOT started.
  Artifacts: docs/specs/context_injection/ (+phase1_spec/ 9 files), KB below.
```

Adjacent systems (owned by other Nodes, wired here): MemoryStore FTS5+vector (`src/omega/memory/`, N2), SoulStore atomic writer C-1′ (N2), Headroom middleware specs (post-debut HR, `docs/specs/qdrant_headroom/`), provider fabric/model matrix (N6).

## 2. Key Files

| File | Purpose |
|------|---------|
| `.opencode/hooks/session_end.py` | Session-end hook; writes lesson-file timestamps (M5/M11); anti-clobber read-first |
| `src/omega/oracle/entity_workspace.py` | `get_soul_prompt()` L382; Situated Identity v6.1; TAINT-GATE L426; stale firewall regex L455 |
| `src/omega/soul_utils.py` | Approved-L3 surfacing (≤3 items, M18 cap); loop-closer |
| `src/omega/cli/soul_stage.py` | Approval TUI — **MOCK, non-functional** |
| `scripts/validate_soul.py` | v6.x validator — enforces `memory/` subdir layout, hardcoded to kali |
| `scripts/check_mandate_compliance.py` | M5/M11 gates — scans ROOT lesson files |
| `scripts/migrate_soul_v6.py` | v6 migration; root↔memory path history |
| `opencode.json` (root) | Live config: instructions(5 doctrine files), V1 compaction keys, 12 agents, 4 plugins (2 dead paths) |
| `docs/specs/context_injection/` | CI synthesis (00–09) + Carmack review + phase1_spec/ (9 files, execution-ready) |
| `data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md` | **The KB** — 56 sources digested, Deep Dig II, N7 annotation, defect register |
| `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` | Web-verified answers Q-B1..B7 (ctx windows, compaction semantics, hooks, skills) |
| `data/entities/lilith/workspace/N7_MINING_BRIEF_20260821.md` | Original mining brief (superseded premise flagged inside KB Gotcha #1) |
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | M15 4-tier redundancy + hydration sequence |

## 3. Entry Points (start here)

1. **New to domain** → `N7_CONTEXT_KB_20260821.md` §Per-Source Digests: `00_INDEX.md` + `01_GROUND_TRUTH.md` digests (the numbers), then Carmack review digest (the verdicts).
2. **Executing CI Phase 1** → KB `## N7 Expert Annotation` P0 fixes FIRST, then `phase1_spec/07_IMPLEMENTATION_ORDER.md`.
3. **Touching soul pipeline** → KB Deep Dig II §DD-II-1 (approval flow truth) + Domain Index hazards D5–D7.
4. **Compaction work** → `N7_WEB_RESEARCH_20260821.md` Q-B2/Q-B3/Q-B4 + KB DD-II-2 reconciliation note.
5. **Skills work** → Q-B5 verdict (`permission.skill`, not `auto_load`).

## 4. Doc Map

| Layer | Location |
|-------|----------|
| Synthesis | `docs/specs/context_injection/00_INDEX.md` … `09_CARMACK_DOMAIN_QUESTIONS.md` |
| Verdict authority | `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` (⚠️ double-M filename is load-bearing) |
| Execution spec | `docs/specs/context_injection/phase1_spec/` (index + 01–08) |
| Raw research inputs | `data/coordination/RESEARCH_{EXPLORE_LOCAL,MAAT_BUILD,LILITH_RUN,RESEARCHER_STRATEGIC}.md` |
| Compression future | `docs/specs/qdrant_headroom/` (research, Phase 2 trigger gates, headroom_middleware/01–10) |
| Research batch | `docs/research/R_{PROMPT_COMPRESSION_CONTEXT_DISTILLATION,PLANNER_EXECUTOR_CONTEXT_WINDOW,ROLE_AWARE_PROMPTING,DYNAMIC_PROMPT_BUILDERS,DYNAMIC_PROMPT_SYSTEM_BLUEPRINT}_20260819.md` |
| Kernel-memory floor | `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` (zswap ADR — N1 adjacent) |
| Prior art | `data/entities/lilith/workspace/COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md` (PDI/VCR metrics = unimplemented gold) |
| Roc investigation | `CONTEXT_INJECTION_INVESTIGATION_20260820.md` (located in Deep Dig II; see KB) |

## 5. Known Hazards (defect register — live as of 2026-08-21)

| ID | Hazard | Evidence |
|----|--------|----------|
| D1 | CI-1 acceptance `wc -l = 57` unsatisfiable: spec Tier 0 file is 36 lines; 57 matches stale v3.7.0 codex snapshot | KB Gotcha #3 |
| D2 | opencode.json registers `.opencode/plugin/*` (singular) — dir doesn't exist; files at `.opencode/plugins/`. Blocks CI-3 verification | KB Gotcha #2 |
| D3 | Compaction key-family ambiguity: live config = V1 keys; spec target writes BOTH families; web says v1.x honors V1 only (V2 keys = separate product line); local binary strings show both consumed. Pin the running binary version before trusting any target block | Web Q-B2 + DD-II-2 reconciliation note |
| D4 | Spec models 6 agents; live config has 12 — unmodeled agents inherit invoker model, no toolProfile coverage | KB Gotcha #4 |
| D5 | Soul-prompt mandate injection silently dead: regex hunts "Fourteen Laws" vs actual "Twenty-Seven"; hardcoded "308/308 Tests Passing" presented as live health | KB Gotcha #6 |
| D6 | Dual-path lessons war: validators enforce `memory/`, hook+identity readers use ROOT, bundle prefers memory/. Both exist for kali+lilith | DD-II-1 |
| D7 | Approval operator DOES NOT EXIST: zero code sets `status: approved`; soul_stage TUI is a mock. Vetted-wisdom injection surfaces nothing | DD-II-1 + OQ#5 |
| D8 | `auto_load` frontmatter is NOT an opencode feature (zod parses only name/description) → CI-4 sed loops are a no-op. Real lever: `permission.skill` patterns | Web Q-B5 |
| D9 | `toolProfile` does not exist upstream; schema lacks `additionalProperties:false` so it's silently inert | Web Q-B6 |
| D10 | `OPENCODE_DISABLE_AUTOCOMPACT` is real+global-only, but provider-overflow recovery path bypasses it through ≥v1.17.7 (#32385) | Web Q-B3 |
| D11 | qwen3-4b ctx cap 8192 is a config choice, not model limit: base=32K native (128K YaRN), Thinking-2507=256K native. "8K–16K" prose wrong | Web Q-B1 |
| D12 | subagent_depth=2 inheritance ≈3× context cost (~423K/cycle at current numbers) | DD-II-4 |
| D13 | headroom_middleware/05 (MCP schema compression) conflicts with Carmack Q2.2 REJECT — scope tension for Phase 2 | DD-II-4 |

Open items: KB `## Open Questions` #4–#11 (some now answered by web research — supersession noted in KB annotation when updated).

*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_domain_index ⬡ 2026-08-21*
