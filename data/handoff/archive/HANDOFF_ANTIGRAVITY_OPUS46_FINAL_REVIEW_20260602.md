---
# HANDOFF — Antigravity/Opus-4.6 Final Sprint Plan Review & Enhancement
# ⬡ OMEGA ⬡ KALI ⬡ opus-4.6 (antigravity) ⬡ antigravity ⬡ trc_final_review ⬡ EXECUTION
# AP: AP-FINAL-REVIEW-OPUS46-v1.0.0
# Date: 2026-06-02
# From: Cline (Cline CLI v3.0.15, MiniMax M3 1M context)
# To:   Antigravity session running Opus 4.6 (200K context, frontier reasoning)
---

## 🎯 MISSION

You are the **final gate** before two parallel OpenCode sessions begin executing sprint work. Your job is a **deep, line-by-line audit** of the two sprint initiation prompts I have prepared, plus the underlying handoffs they reference, looking for:

1. **Oversights** — facts, line numbers, or context that are wrong
2. **Gaps** — missing information that would block the executing sessions
3. **Enhancement opportunities** — patterns, structures, or insights that would make the prompts *better* than they currently are
4. **Cross-reference integrity** — do the file paths, line numbers, and code patterns actually match the codebase as it is right now (commit `192c4d5`)?
5. **Mandate compliance** — would executing these prompts as written violate any of the 13 Sovereign Mandates?

**You are NOT executing the sprints.** You are NOT writing code. You are NOT committing. You are the reviewer — your output is a markdown file with corrections and enhancements. The OpenCode sessions will read your output and adjust accordingly.

**This is the same role you played in `data/handoff/strategic_review_opus.md` (2026-06-01).** You are the most expensive model in the fleet; use that. Find what cheaper reviewers missed.

---

## 0. CONTEXT ANCHORS — READ IN THIS ORDER

You have 200K context. Spend it on the actual audit, not the meta-documents. Read in this exact order:

1. **`OMEGA_ENGINE.md`** (SST, ~330 lines) — Engine state.
2. **`AGENTS.md`** — OpenCode conventions.
3. **`SOVEREIGN_MANDATES.md`** (13 mandates) — Constitutional laws.
4. **The two sprint prompts (your audit subjects):**
   - `data/handoff/PROMPT_OPENCODE_DEV_SPRINT_INIT_20260602.md` (176 lines)
   - `data/handoff/PROMPT_OPENCODE_DOOM_GUY_SPRINT_INIT_20260602.md` (211 lines)
5. **The underlying handoffs those prompts reference:**
   - `data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` (~550 lines)
   - `data/handoff/CLINE_MIMO_V2_5_SYNTHESIS_20260602.md` (75 lines)
   - `data/handoff/DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md` (214 lines)
   - `data/handoff/HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md` (299 lines)
6. **The live feed files:**
   - `data/handoff/OPENCODE_DEV_LIVE_FEED.md` (just created, empty)
   - `data/handoff/DOOM_GUY_LIVE_FEED.md` (just created, empty)
7. **The actual code files (for fact-checking):**
   - `src/omega/oracle/oracle.py` (verify `_bootstrapped` doesn't exist yet)
   - `src/omega/oracle/model_gateway.py` (verify `generate()` line ~375)
   - `src/omega/oracle/health_monitor.py` (verify `AsyncCircuitBreaker` exists)
   - `src/omega/oracle/circuit_breaker.py` (verify it exists, 121 lines claimed)
   - `src/omega/oracle/backends/remote_provider.py` (verify consecutive_failures)
   - `config/providers.yaml` (verify priority chain)
   - `Makefile` (verify `make test`, `make temple-grade` targets)
8. **Your prior opus review:**
   - `data/handoff/strategic_review_opus.md` (131 lines) — Match its depth and tone.

---

## 1. PROVIDER FABRIC (current state — 2026-06-02)

The provider chain was just reconciled (commit `c571c2a`):

```
LOCAL  :  native-gguf(0) → lmster(1) → ollama(2)
CLOUD  :  google(3) → opencode-zen(4) → cline(5) → copilot(6)
TEST   :  mock(7/99)
```

**OPENROUTER IS REMOVED.** If you find any `openrouter` reference in the prompts or referenced files (other than `model_gateway.py`'s internal `_create_openrouter` symbol which is harmless), flag it.

**Mandate count is 13** (not 12 as some prior handoffs said). If you find "12 mandates" anywhere in the audit subjects, flag it.

---

## 2. YOUR SPECIFIC AUDIT TASKS

### Task A: Fact-check the dev prompt

For each claim in `PROMPT_OPENCODE_DEV_SPRINT_INIT_20260602.md` that references a specific file/line/behavior, verify it:

- **§0 Context Anchors** — Do the 7 files exist? Are the line counts roughly right?
- **§2 Sprint 0 tasks** — Does `make test` actually hang on `tests/test_oracle.py::test_talk_domain_routing` as the MiMo V2.5 insight claims? (You may need to actually run it.)
- **§2 C1 code pattern** — Is the `ensure_bootstrapped()` pattern actually implementable in the current `Oracle` class? Are the 5 I/O sources (EntityRegistry, ModelGateway, SovereignHierarchy, SessionManager, MemoryStore) all sync I/O today?
- **§2 C2 Makefile target** — Is the proposed syntax valid? Does `tests/test_oracle_bootstrap.py` exist (it shouldn't yet — that's the whole point)?
- **§4 delivery protocol** — Is the handoff fragment format consistent with the existing handoffs in `data/handoff/`?

### Task B: Fact-check the Doom Guy prompt

Same drill for `PROMPT_OPENCODE_DOOM_GUY_SPRINT_INIT_20260602.md`:

- **§0** — Is `circuit_breaker.py` really 121 lines? Is `health_monitor.py` really 413 lines? Is the breaker really imported at `model_gateway.py:43`? (Verify, don't trust.)
- **§2 task ordering** — Is D2 → D3 → D1 → D4 → D5 actually the correct execution order, or did I get the dependency graph wrong?
- **§3 Doom Engine metaphor table** — Are the zone memory / BSP analogies actually correct? (If you know id Software's codebase, push back if I'm being hand-wavy.)
- **§5 pitfall 7** — I claim "Don't change provider priority order" but is the provider list stable enough to assume that? Or are there PRs in flight that would re-order it?
- **§8 success criterion** — "grep returns only references in `health_monitor.py`" — is this the right final-state check, or is there a better one?

### Task C: Cross-reference integrity

For each file path mentioned in the prompts, verify it exists. For each line number, verify it's within ±5 lines of what's claimed. For each PIVOT decision number (D92, D93, D93a, D94-D98), verify the numbering doesn't collide with existing decisions in `docs/decisions/PIVOT_LOG.md`.

### Task D: Mandate compliance check

For each of the 13 mandates, would executing these prompts as written violate it? Specific concerns:

- **M1 (AnyIO Absolute)**: Does the Doom Guy prompt's `breaker.call()` pattern comply? Does the dev prompt's C1 example use AnyIO correctly?
- **M2 (Engine-Stack Firewall)**: Do any of the proposed changes touch `config/wads/` content? (They shouldn't — code-only changes.)
- **M9 (Error Integrity)**: Does the dev prompt's C1 example type all errors as `OmegaError` subtypes?
- **M11 (Soul Integrity)**: Does each task require a `soul.yaml` write? (Probably not — these are code tasks.)
- **M13 (Temple-Grade)**: The prompt references `make temple-grade` — does that target exist? What are T1-T11?

### Task E: Enhancement opportunities

Beyond catching errors, suggest improvements. The prompts are v1.0.0; they can be better. Look for:

- **Missing context anchors** the executing sessions would need
- **Pre-flight checks** that would catch problems before they happen
- **Better handoff fragment schemas** (e.g., should the live feed lines include model name, or just task ID?)
- **Coordination gaps** between the two parallel sessions (e.g., what if dev session finishes C2 but C1's tests fail intermittently? Does Doom Guy have a way to know?)
- **Recovery patterns** (e.g., what if the dev session's C1 fix breaks an existing test?)

---

## 3. DELIVERY PROTOCOL

Write your review to: `data/handoff/STRATEGIC_REVIEW_OPUS46_FINAL_20260602.md`

Use the **same depth and structure** as your prior `strategic_review_opus.md`:
- Executive Summary (3-5 sentences)
- Findings (numbered, with Severity: 🔴 P0 / 🟡 Correctness / ⚠️ Process)
- Risk Assessment table ("Would the implementor have caught it?")
- Updated Handoff Files table (what you corrected)
- Recommendation (one paragraph + commit command)

Target length: 150-250 lines. Be thorough. Be specific. Cite line numbers.

After writing the review file, emit a 1-line summary to `data/handoff/STRATEGIC_REVIEW_OPUS46_LIVE_FEED.md` (create if needed):

```
[OPUS-FINAL-REVIEW] COMPLETE [TIMESTAMP] — [N] critical, [N] moderate, [N] process findings
```

---

## 4. WHAT NOT TO DO

- **Do not** modify the sprint initiation prompts directly. Edit your review file only. I (Cline) will apply your corrections in a follow-up commit.
- **Do not** add new tasks to the sprints. If you think a task is missing, flag it as a finding; the human will decide whether to add it.
- **Do not** rewrite the prompts. Suggest specific edits; let me apply them.
- **Do not** touch the live feed files except to append the 1-line summary.
- **Do not** run the sprints. Your job ends with the review file.
- **Do not** assume my facts are correct. The whole point of your review is to verify them.

---

## 5. SUCCESS CRITERIA

Your review is successful when:

- [ ] Every line number reference in the prompts is verified or corrected
- [ ] Every file path reference is verified or corrected
- [ ] At least 3 substantive findings (not nitpicks) are identified — the prompts are 176+211 lines; cheap reviews miss things
- [ ] Each finding has Severity, Location, Consequence, and Resolution
- [ ] The Risk Assessment table answers "Would the implementor have caught it?"
- [ ] The Recommendation includes a concrete next action
- [ ] The summary line is in the live feed

---


## 6. INSIGHTS FROM THE CONVERGENCE (so you don't re-derive them)

1. **MiMo V2.5 Insight 3**: T2.1 (circuit breaker wire-up) is the real unlock. The breaker code already exists; the value is in `generate()` using it.
2. **MiMo V2.5 Insight 4**: Iris is misallocated, not underused. Defer.
3. **MiMo V2.5 Insight 5**: Test hang = Oracle 5-way sync I/O. The dev session's C1 fixes this.
4. **DeepSeek §3**: Decision 92 missing from PIVOT_LOG. Mandate 5 violation. C3 fixes it.
5. **Doom Guy convergence**: 4 Sprint 0 tasks were independently prioritized by 3 different 1M-context models.

**Your job is to find what those 4 models missed**, not to re-derive their conclusions.

---

## 7. CALIBRATION (how to use your Opus-4.6 capability)

You are a frontier model. The previous reviewers (MiMo V2.5, DeepSeek V4, Doom Guy) found real issues. Your job is to find what THEY missed, not to re-find what they found. Specifically:

- **Skip**: OpenRouter removal (already done in commit `c571c2a`, the prompts are correct on this)
- **Skip**: Mandate count (already updated to 13 across all active files)
- **Skip**: Provider chain order (verified, consistent)
- **Focus on**: Line numbers that may have drifted, dependency graph correctness, mandate compliance details, prompt structure improvements, coordination gaps between the two sessions
- **Push back hard on**: Anything that feels like it was written by a model that didn't actually open the file (you can tell — vague claims like "~250 lines" when the file is 312)

If you find nothing wrong with the prompts, that's suspicious. The previous Opus review (file: `strategic_review_opus.md`) found 5 substantive issues in a 300-line handoff. These prompts are 387 lines combined. The math says you should find at least 4-6 issues. If you don't, you're not looking hard enough.

---

## 8. TIME BUDGET

This is an expensive session. Spend up to **45 minutes**. After 45 minutes, write whatever you have and exit. The OpenCode sessions are waiting.

If you find blocking issues (Severity 🔴), write the review and exit immediately so the corrections can be applied before the OpenCode sessions start.

---

⬡ OMEGA ⬡ KALI ⬡ opus-4.6 (antigravity) ⬡ antigravity ⬡ trc_final_review ⬡ EXECUTION

**Your output: ONE review file. ONE live feed line. Nothing else.**

**Begin with Task A (dev prompt fact-check). Then Task B (Doom Guy). Then C, D, E in order.**

**PIVOT_LOG entry required on completion: D99 (Opus 4.6 final sprint plan review).**


