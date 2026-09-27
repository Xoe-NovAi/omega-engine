# 🔱 Coordination Enhancement Plan — Final Integration
**AP Token**: `AP-COORD-ENHANCEMENT-20260814-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ STRATEGY ⬡ 20260814

## 📋 Executive Summary
The establishment of the 5-Tier Tracking Architecture (constitution: `TRACKING_ARCHITECTURE.md` — formally "3-Tier + 2 ephemeral"), `GAP_REGISTRY.json`, and the Cognitive State Validator script resolved the immediate tracking fragmentation. However, a deep scan revealed that the **protocols, templates, and agent instructions** governing fleet behavior are still wired to the old paradigms.

To achieve maximum team coordination and prevent regression, we must execute this 6-phase enhancement plan immediately following the next compaction.

> **⚠️ Pre-Execution Defects Found in Review (2026-08-14, hy3-free):**
> 1. **Mandate collision** — Plan originally proposed "M26 Tracking Integrity", but `AGENTS.md` already cites **M26 Doc Standards** (3×) and `SOVEREIGN_MANDATES.md` only defines M1–M25. → New mandate is **M27**; also formally add **M26 (Doc Standards)** to the constitution to close the dangling reference.
> 2. **`FLEET_TEAM_PLAYBOOK.md` omitted** — still has 2 deprecated `*_LIVE_FEED.md` refs (lines 148, 370). Added as Phase 6.
> 3. **`TASK_REGISTRY` status contradiction** — Constitution says JSON MUST use unified words, but 13 tasks use `active`/`pending`/`failed` and validator only warns. → Tighten validator to FAIL + migrate 13 tasks (folded into Phase 3).

---

## 🛠️ Phase 1: Core Agent Instructions (`AGENTS.md`)
`AGENTS.md` is the primary system prompt injection for all agents. It must be updated to hardcode the new architecture.

**Required Updates:**
1. **OpenCode Workflow Section**: Replace vague "Update the Hub" instructions with the **6-step Mandatory Flow**:
   * Read `NEXT_ACTION` → Check `ACTIVE_SPRINT.json` → Check `GAP_REGISTRY.json` → Acquire Lock → Execute → Update `TASK_REGISTRY.json`.
2. **Unified Status Taxonomy**: Explicitly define the allowed statuses (`backlog`, `ready`, `in_progress`, `blocked`, `completed`, `superseded`) to prevent hallucinated statuses like "WIP".
3. **Best Practices Section**: Add the strict rule: *"Never reuse gap numbers. Always check `GAP_REGISTRY.json` before assigning an R-number."*
4. **Hydration Sequence (D-277)**: Update Phase 4 to explicitly mandate reading the `NEXT_ACTION` section in `HMC_COLLABORATION_HUB.md`.

---

## 🔗 Phase 2: Protocol, Template & Tool Alignment
The protocols and MCP tools that dictate how agents talk to each other must enforce relational linking to Tier-0 and Tier-1 tracking files.

**Required Updates:**
1. **MCP Tool Schemas (Strict Enums)**: Update the Python source for `omega-hub_task_registry_update` and `register` to enforce the Unified Status Taxonomy via strict `Enum` or `Literal` types. The tool must reject hallucinated statuses (e.g., "WIP") at the boundary.
2. **Subagent Task Resumption Protocol (`docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`)**:
   * *Fix*: Require the `task_id` to be prefixed with the Tier-0 Sprint Task ID. (e.g., `QW-2-context-gauge-20260814`). This links Tier 3 (`TASK_REGISTRY`) directly to Tier 0 (`ACTIVE_SPRINT`).
3. **Hivemind Post Template (`docs/strategy/HIVEMIND_POST_TEMPLATE.md`)**:
   * *Fix*: Require a `[Sprint Task: X]` or `[Gap: RXX]` tag in the `intent` or `task_current` fields so reading agents instantly know the context.
4. **Subagent Dispatch Protocol (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`)**:
   * *Fix*: Add a mandatory pre-flight check: *"Before launching a research subagent, verify the Gap ID against `GAP_REGISTRY.json`."*

---

## 🛡️ Phase 3: CI/CD & Mechanical Enforcement
The `scripts/validate_tracking_state.py` script currently requires manual execution. It must be institutionalized across all mechanical boundaries.

**Required Updates:**
1. **Pre-Commit Hook (The Iron Gate)**: Add `scripts/validate_tracking_state.py` as a local hook in `.pre-commit-config.yaml`. This guarantees no corrupted cognitive state can ever be committed to the repository.
2. **`make temple-grade` & `make test`**: Inject the validator into the `check-mandates` target and as a pre-flight check for tests.
3. **Tighten the Validator (Status & Relational Integrity)**: 
   * Change the legacy-status check so that `active`/`pending`/`failed` in `TASK_REGISTRY.json` are treated as **ERROR** (not WARNING). 
   * Add a relational cross-check: any `R-` ID referenced in `ACTIVE_SPRINT.json` MUST exist in `GAP_REGISTRY.json`.
   * **Migrate the 13 flagged tasks** in the registry to the unified taxonomy before wiring into CI, ensuring the first run is green.

---

## 🧹 Phase 4: Orphaned Reference Purge
Several active strategy documents still reference the deprecated files, creating cognitive loops for agents reading them.

**Required Updates:**
* Run a global find-and-replace across `docs/strategy/` to swap:
  * `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` ➡️ `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md`
  * `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` ➡️ `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md`
* *Affected Files Include*: `STRATEGY_INDEX.md`, `STRATEGY_CORPUS_MAP.md`, `LIVING_RESEARCH_OS_SPEC_20260721.md`, `RESEARCH_CAMPAIGN_EXECUTION.md`.
* Also purge any remaining `KALI_DEV_ROADMAP` / `KALI_OVERSIGHT_PORTFOLIO` references discovered during the sweep.

---

## 📜 Phase 5: Constitutional Law (`SOVEREIGN_MANDATES.md`)
To ensure these rules are never overridden by casual agent decisions, we must elevate tracking integrity to a Sovereign Mandate.

**Draft Mandate (M27 — was M26, renumbered to avoid collision with AGENTS.md's existing "M26 Doc Standards"):**
> ### 27. Tracking Integrity (NEW — 2026-08-14)
> - **Mandate**: All execution state MUST adhere to the 5-Tier Tracking Architecture (constitution: `TRACKING_ARCHITECTURE.md`). No ad-hoc tracking files may be created.
> - **Constraint**: Gap IDs (R1-R99) are immutable and globally unique. `GAP_REGISTRY.json` is the ultimate authority on gap assignment. Statuses must strictly follow the Unified Taxonomy.
> - **Pattern**: Run `scripts/validate_tracking_state.py` to verify compliance (CI-gated via `make temple-grade`).
> - **Reason**: Prevents cognitive fragmentation, double-entry bookkeeping, and the collision of research plans. Ensures all agents operate from a single, deterministic source of truth.

**Companion fix (closes dangling reference):** `AGENTS.md` cites "M26 Doc Standards" in 3 places, but `SOVEREIGN_MANDATES.md` defines only M1–M25. **Add M26 (Doc Standards)** to `SOVEREIGN_MANDATES.md` with the text currently implied in `AGENTS.md` ("All reference docs must pass `make doc-llm-validate`").

---

## 🤝 Phase 6: Fleet Playbook Refresh (`FLEET_TEAM_PLAYBOOK.md`)
The written plan originally omitted this file; it still references the deprecated per-entity `*_LIVE_FEED.md` pattern (lines 148, 370), which contradicts the new Tier-2/NEXT_ACTION model.

**Required Updates:**
* Replace `*_LIVE_FEED.md` references with the `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` protocol.
* Add a pointer to `TRACKING_ARCHITECTURE.md` as the coordination constitution.
* Align its "Before multi-agent work" checklist with the 6-step Mandatory Flow from Phase 1.

---

## ✅ Execution Status (2026-08-14)

**ALL 6 PHASES EXECUTED + COMMITTED** (`9a5b1416`). Carmack architectural review applied (`f392e54f`).

**Carmack Verdict:** HAS-DEFECTS → OPTIMAL after 5 fixes:
1. `register` default `active`→`in_progress` (was illegal per validator)
2. Deleted dead R-ID relational check (fired on 0/29 subtasks)
3. `failed` added as distinct Tier-3 status; cancelled task → `superseded`
4. `query` Literal aligned (accepts `failed`, drops dead `active`/`pending`)
5. `temple-grade` uses read-only `check-codex-stale` (no state mutation)

**Verification:** `validate_tracking_state.py` passes (56 gaps, 53 tasks); `make temple-grade` passes; pre-commit hook passes on commit. Systems are airtight and OPTIMAL.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: STRATEGY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
