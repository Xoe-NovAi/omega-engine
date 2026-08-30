<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# SDP Carmack Review

**AP Token:** `AP-CARMACK-SDP-REVIEW-20260809-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_sdp_review ⬡ COMPLETE

**Date:** 2026-08-09
**Reviewer:** John Carmack (S3 Consultant)
**Method:** Read all 9 documents (2,273 lines). Then verified every load-bearing factual claim against `~/.local/share/opencode/opencode.db` (16.8 GB, 2,435 sessions, 106,240 messages) and against `src/omega/`. Findings below are measured, not inferred, except where confidence is explicitly reduced.

---

## Executive Verdict

**Build the idea. Delete 80% of the specification.**

The core operational pattern is real and it is already working — it is what produced these documents. But you have written **2,273 lines of specification and 0 lines of code** (`grep -rl "SDP\|somatic_save\|context_pressure" src/` → 0 files). That ratio is the finding. This is not architecture; it is architecture *cosplay*.

Worse, the specification is **factually wrong about its own data source**, and I proved it. The Context Gauge — the single component every other phase depends on — specifies a calculation that is **8.7× wrong** on your live database. If you had shipped Phase 1 as written, the gauge would have reported `CRITICAL_REDZONE` on a session that was actually at 14% capacity, and every downstream behavior (Somatic Save-Points, escalation, routing) would have fired on garbage. You would then have spent a week debugging the Z3 solver while the actual bug was in a `SUM()`.

This is the classic failure: **the abstraction was designed before the data was looked at.** Six specs deep on constraint satisfaction and KV cache formulas, and nobody ran one query.

Build the 40-line gauge. Ship it. Delete the rest until the gauge has told you something you didn't already know.

---

## Manifesto Assessment

**Verdict: The observation is real. The framing is inflated. The novelty claim is false.**

### What's real (confidence 9/10)
"Don't spend scarce frontier tokens on `ls -la`" is a correct and economically significant insight *for your specific constraint* — weekly-pool AGY accounts. That constraint is real, and the response is rational. This is genuine Right Approximation: you have an unusual resource profile (near-zero marginal cost daily models, hard-capped weekly frontier pools) and you built a workflow that fits it.

### What's theater (confidence 9/10)

**"The Monolithic Fallacy" is a strawman.** §1 asserts that Devin/AutoGPT "believe a single massive frontier model should handle every step." That is not a belief anyone holds; it is a *default* that exists because routing infrastructure is expensive to build, not because anyone argued for it. Naming an unexamined default as a "Fallacy" and then defeating it is rhetoric, not analysis. Every serious agent framework in 2026 does model tiering. You are not rejecting a paradigm; you are catching up to one, with a better-fitting variant.

**"Intelligence as a Composite Material" is obvious dressed as profound.** Strip the metaphor: "use cheap models for I/O, expensive models for reasoning, local models for mechanical execution." That is a sentence. It does not require a manifesto. The metaphor adds zero predictive power — it does not tell you *where* to draw the phase boundary, which is the only hard question. Metaphors that don't constrain implementation are decoration.

**"The File System as the Corpus Callosum" (§3A) is the worst offender.** This says: *models write files, and other models read them.* You have named `write()` after a brain structure. This is exactly the cargo-cult pattern I audit for — a grand name attached to a primitive that provides no benefit the primitive didn't already have. Delete the name. Keep the practice.

### The one genuinely novel bit
§7 **Sequential Dialectic within a single primed context** — running Gemini for architecture, then Sonnet over the *same* context to catch compliance gaps, without re-priming. That is a real technique with a real cost saving, and the manifesto buries it under three metaphors. This should have been the headline. It's the only part I'd defend to a skeptic.

**Recommendation:** Cut the manifesto to one page. Keep §1.2 (context cliff), §7 (dialectic). Delete "Monolithic Fallacy," "Composite Material," "Corpus Callosum." Confidence 8/10.

---

## Blueprint Assessment

**Verdict: The order is right. The scope of each phase is wrong. Phase 4 should not be built at all.**

The 4-phase sequence (Observability → Autonomy → Infrastructure → Orchestration) is correct and I endorse it. Measure before you automate is Axiom 05. Credit where due.

### The Phase 0 gate is being violated right now

`COGNITIVE_SCAFFOLDING_PROTOCOL.md:26` — *"Do not automate this protocol until it has been studied through at least 10 manual executions."*
`COGNITIVE_SCAFFOLDING_PROTOCOL.md:298` — *"until this protocol has been executed manually at least 10 times... no automation is permitted."*

I read the ledger. `data/coordination/AGY_SESSION_LEDGER.md` contains **3 entries, all dated 2026-08-09, all with `account-1..8` unassigned (`*TBD*`), and all three are the sessions that wrote these documents.** The gate is 3/10, and the 3 are self-referential — the protocol has never been used on a task other than writing the protocol.

Yet you have already produced six implementation specs including Z3 formal verification and encrypted state serialization for Phases 1–4.

**You wrote the rule and broke it in the same 24 hours.** This is the finding that matters most, because the rule was correct. The ledger data is precisely what would tell you whether the Context Gauge should trigger at 75% or 80% — and instead of collecting it, you assumed the number and then wrote 300 lines of Z3 to verify a routing function that consumes it.

### Phase-by-phase

| Phase | Verdict | Reason |
|---|---|---|
| **Phase 1 Observability** | ✅ **BUILD NOW** — but 40 lines, not the spec's ~600 | Only phase with immediate standalone value. Works even if all other phases are cancelled. |
| **Phase 2 Autonomy (SSP)** | 🟡 **DEFER** — the file write is 10 lines; the state machine is fiction | Value is in the *agent directive*, not the machinery. See below. |
| **Phase 3 V-1 Vault** | ✅ **KEEP, but it is not SDP** | V-1 is a pre-existing Ark ticket with independent justification. Do not let SDP claim it as a dependency to inflate SDP's importance. It's the reverse: SDP is a *consumer* of V-1. |
| **Phase 4 Auto-Router** | ❌ **KILL** | See below. Structurally unsound. |

### Phase 4 is not merely premature — it may be impossible

`SDP_IMPLEMENTATION_SPEC.md:193-197` claims the Auto-Router "swaps the provider backend in `ModelGateway` for the *next* turn," and the user "sees a single continuous conversation."

**This does not work, and the spec contains the evidence of why without noticing.** `ModelGateway` is the *Omega Engine's internal* inference path (`omega talk`, entity summons, local GGUF). It is **not** the path OpenCode uses for your session model. Your session model is selected by OpenCode itself — `session.model` in `opencode.db`, which I confirmed reads `{"id":"longcat-2.0-free","providerID":"opencode","variant":"medium"}`. Mutating `ModelGateway` has **zero effect** on which model answers your next OpenCode turn.

To make Phase 4 real you would need OpenCode to expose a session-model-swap API to plugins. I checked `opencode.json` and the plugin surface: no such hook is in use. This means Phase 4's "Seamless Handoff" (`SDP_AUTOMATION_BLUEPRINT.md:41`) is, as specified, **undeliverable against the current toolchain** — you would be writing a component whose central guarantee cannot be met.

The spec half-knows this. `FM-08` in the failure analysis is literally *"Backend swap breaks session → CRITICAL → if broken, disable auto-router."* You have written a mitigation for the possibility that the feature does not work. When your risk register says "if this doesn't work, turn it off," the honest reading is: **you have not verified that it works, and it is the entire phase.**

Confidence 8/10 — I verified the DB and plugin config; I did not exhaustively audit every OpenCode internal API, so there is a small chance a hook exists that I did not find. **That verification is a 30-minute task and it gates the entire phase.** Do it before writing another line of Phase 4 spec.

---

## Implementation Spec Assessment

### §1 Context Gauge — **UNDERENGINEERED IN THE ONE PLACE THAT MATTERS, AND IT IS BROKEN**

This is the most important finding in the review.

`SDP_IMPLEMENTATION_SPEC.md:41` specifies:
> `current_tokens`: Sum of `tokens` column from `message` table for current `session_id`

**Three things are wrong with that one line.**

**1. The column does not exist.** Measured schema:
```
message -> [('id','TEXT'), ('session_id','TEXT'), ('time_created','INTEGER'),
            ('time_updated','INTEGER'), ('data','TEXT')]
```
There is no `tokens` column. Tokens live inside the `data` TEXT blob as JSON. Any implementer following this spec literally gets an immediate `OperationalError`. Confidence 10/10 — primary source.

**2. Summing is categorically the wrong operation, and it is 8.7× wrong.** Each assistant message records the token state of *the whole context at that moment*, not a delta. The values are cumulative-by-nature. Summing them counts the same context repeatedly.

Measured on live session `ses_016e894a3ffesRhuctnG50ihe8`:
```
NAIVE SUM (the spec's method) : 1,246,935 tokens
TRUE OCCUPANCY (last .total)  :   143,640 tokens
INFLATION FACTOR              :          8.7×
```
On a 1M-window model (`longcat-2.0-free`, which is what this very session runs on), the spec's gauge reports **124% — permanent CRITICAL_REDZONE** on a session at **14% real usage**. The gauge would be pinned to red forever. Every SSP would fire. Every escalation would fire. You would burn your entire AGY weekly pool escaping a context cliff that was 860,000 tokens away.

**3. It ignores cache reads, which dominate.** Real message payload:
```json
{"total":140513, "input":2928, "output":518, "reasoning":0,
 "cache":{"write":0, "read":137067}}
```
97.5% of that context is `cache.read`. Any formula not accounting for it is not measuring context.

**The correct implementation is one query and it is already in the data — `total` is precomputed.** Measured at **0.51 ms**:

```python
def get_context_tokens(session_id: str) -> int:
    """Last assistant message's tokens.total IS the current occupancy."""
    for (d,) in db.execute(
        "SELECT data FROM message WHERE session_id=? "
        "ORDER BY time_created DESC LIMIT 20", (session_id,)
    ):
        tk = json.loads(d).get("tokens") or {}
        if tk.get("total"):
            return tk["total"]
    return 0
```

The index `message_session_time_created_id_idx (session_id, time_created, id)` already exists, which is why this is sub-millisecond on a 16.8 GB database. **Do not add a `SUM()`. Do not scan the session.** The `LIMIT 20` is required because the newest message can be mid-stream with `total: 0` — I hit exactly that case in testing.

**Also wrong: the model-window source.** Spec §1.3 and `SDP_MODEL_AWARE_GAUGE_SPEC.md:81` both resolve the active model from env vars (`OPENCODE_MODEL_CONTEXT_WINDOW`, `OPENCODE_MODEL_ID`). I checked: **those env vars are not set.** But `session.model` in the DB carries the exact model ID as JSON, in the same table you are already querying. Use the database you are already open on. One less failure mode, and FM-02 disappears entirely.

### §2 Somatic Save-Points — **OVERENGINEERED BY ~10×**

The 5-state machine (`ACTIVE → REDZONE_DETECTED → SSP_WRITTEN → ESCALATED → RESUMED → COMPLETED`) is fiction. There is no process that owns these states. The agent is stateless between turns; the "machine" is a markdown file and a human deciding what to do next. You cannot have a state machine without a state owner.

**What actually delivers the value:** the agent directive at §2.3. That's a prompt change. It's free. The 25-field SSP schema (§2.1) is also over-spec'd — `FM-09` correctly demands the SSP write stay under 500 tokens, but the schema as written (Intent, Required Escalation, State Snapshot with active files, pending verifications, active handoffs) will exceed that budget. **Your own schema violates your own constraint.** Cut it to four fields: what I was doing, next action, files touched, model tier needed.

### §3 Model-Aware Gauge — **THE ONE SPEC THAT IS CORRECT AND NECESSARY**

Credit where it's due. `SDP_MODEL_AWARE_GAUGE_SPEC.md:25` identifies the real bug: *"If the Gauge assumes 200K but the model is Nemotron 3 Ultra (1M), it will falsely report CRITICAL_REDZONE at 180K."* That's exactly right, and it's the same class of error the base spec makes.

But the multi-gauge aggregator routing to PoolGauge/RAMGauge/TokenGauge (§5) is premature. Two of the three sub-gauges depend on V-1 (doesn't exist) and local model introspection (not wired). **Ship TokenGauge. Return `null` for the other two.** Add them when they have backing data.

Note also: `config/models.yaml` already has `context_window` (5 entries). The spec proposes a parallel schema with `compaction_trigger_pct`, `tier`, `is_agy`. **Extend the existing file. Do not create a second source of truth** — that's an M2 firewall smell and a guaranteed drift point.

### §4 Formal Routing (Z3) — **KILL IT. THIS IS THE WORST DOCUMENT IN THE SET.**

306 lines of constraint satisfaction to choose among **at most 8 items**.

Read the actual utility function (`SDP_FORMAL_ROUTING_SPEC.md:58`):
```
U(a,R) = pool_remaining × 1.0 + problem_match × 2.0
```
`pool_remaining` is on the order of 10⁵–10⁶. `problem_match` contributes **2.0**. The tie-breaker weight is **six orders of magnitude below the primary term**. It can never change the outcome except in an exact numerical tie. The audit trail in §3 shows this plainly: utilities of `850002.0` vs `1200002.0` — the `+2` is decorative. **You have formally verified a term that does nothing.**

The whole thing is:
```python
valid = [a for a in accounts if a.is_healthy
         and a.pool_remaining >= need + 5000
         and a.tier >= required_tier(ctx)
         and (not model or model in a.models)]
if not valid: raise NoPoolAvailableError()
return max(valid, key=lambda a: a.pool_remaining)
```
Five lines. Exhaustively testable with 8 hand-written unit tests over 8 accounts. Z3 is not installed (`ModuleNotFoundError: No module named 'z3'`), so this also adds a dependency to solve a problem that fits in a list comprehension.

Note the `verify_routing_decision` function is itself buggy — it builds a Z3 solver, then does the optimality check in **plain Python** (`if is_true(And(pool_ok,...))` on concrete bools, lines 147-151). The Z3 layer is doing nothing but `sat`-checking a tautology. It is verification theater on top of verification theater.

**§4 Entropy Injection** — 10% random suboptimal routing to "prevent model collusion." There is no mechanism by which 8 API accounts collude. This is M19 (Adversarial Alchemy) invoked past its own sane-boundary, which explicitly warns against "Architectural Over-Engineering... sometimes a bug is just a bug." Randomly wasting your scarcest resource 10% of the time is not alchemy. **Delete.**

### §5 Hardware Horizon — **RIGHT PHYSICS, WRONG PRIORITY; ONE SECTION IS DEAD ON ARRIVAL**

The KV cache formula (§2.1) is correct and the reference table is useful. Keep it as a reference doc.

**§3 SomaticState Transfer is unusable as designed and the spec proves it.** §3.4 requires: exact same model file (SHA256), exact same quantization, exact same `n_ctx`, exact same `llama.cpp` version. Then §3.2 proposes using it to transfer state from a **Phase 1 scaffold model** to a **Phase 3 executor model** — but the entire premise of SDP is that these are *different models at different phases*. The compatibility constraints exclude the only use case the section proposes. It works solely for same-model resume-after-restart, which is a legitimate but completely different feature.

Also: your own numbers kill §4. Energy accounting concludes (§4.2) *"local compute energy is negligible vs AGY tokens"* — 4,500 J ≈ **0.0045** token-equivalents against 15,000 AGY tokens. You computed that the metric doesn't matter and then specified a dashboard for it (§4.3). **Delete §4.** The correct response to "this term is negligible" is to drop the term, not to instrument it.

---

## Failure Analysis Assessment

**Verdict: Best-written document in the set. Analyzing the wrong system.**

The structure is genuinely good — the Graceful Degradation Hierarchy (§3) is the right way to think, and "every phase must be independently operable" is the correct invariant. FM-09's insight that a large write can cross the cliff mid-operation is a real and subtle catch.

**But 8 of 10 failure modes are for components that do not exist** (Vault, Auto-Router, Pool Tracking). You are doing resilience engineering on vapor. Meanwhile:

### Missing failure modes — all of which I hit or measured in one hour of actual testing

| ID | Missing Failure | Evidence | Severity |
|---|---|---|---|
| **FM-11** | **Gauge arithmetic is wrong** — sum-vs-latest | Measured 8.7× inflation. **This is a live defect in the spec, not a hypothetical.** | **CRITICAL** |
| **FM-12** | **In-flight message has `total: 0`** | Hit in testing; naive "last message" returns 0 → gauge reports SAFE at 99%. Requires `LIMIT 20` scan-back. | **HIGH** |
| **FM-13** | **`opencode.db` is 16.8 GB and growing** | Measured. A `LIKE` scan over `part` took **20.8 s**. Any gauge doing full-table work will time out. | **HIGH** |
| **FM-14** | **Env vars assumed by spec are unset** | `OPENCODE_MODEL_ID` / `OPENCODE_MODEL_CONTEXT_WINDOW` not present. Spec's Priority-1 resolution path always misses. | **HIGH** |
| **FM-15** | **`ModelGateway` swap does not affect the OpenCode session model** | Different inference path. Silently no-ops — worst failure class: appears to succeed. | **CRITICAL** |
| **FM-16** | **Gauge observer effect** | Prompt injection (§1.4) fires every turn, permanently in-context, and each injection is itself context. Unbounded self-pollution if injected per-turn rather than replaced. | MEDIUM |
| **FM-17** | **Cache-read vs true-context divergence** | 97.5% of measured tokens were `cache.read`. Provider cache semantics ≠ window occupancy; the mapping needs validation before thresholds are trusted. | MEDIUM |

FM-11, FM-13, FM-14, FM-15 are all failures **I found by running four queries**. The failure analysis has ten entries and zero of them came from touching the system. That is the difference between resilience engineering and resilience literature.

**Overstated risk:** FM-10 (pool desync requiring optimistic locking + weekly reconciliation job) — for a single-user system with 8 accounts. A text file and your own eyes are sufficient until proven otherwise.

---

## Quick Win Assessment

| Claimed | Estimate | Carmack Estimate | Verdict |
|---|---|---|---|
| Context Gauge + Prompt Injection | 2 h | **1.5 h** (gauge 40 min, injection 50 min) | ✅ **Realistic — and this is the only one worth doing** |
| Dialectic Session Logger | 1 h | **6+ h** | ❌ **Wrong by 6×.** "Log the synthesis process" has no defined schema, no defined trigger, no consumer. Undefined scope is not a 1-hour task. |
| Model-Aware Gauge | 1 h | **20 min** if merged into the gauge; **3 h** if built as the spec's multi-gauge aggregator | ⚠️ **Not a separate task.** Merge into task 1. Building it separately guarantees rework. |
| Planner Output Schema Validation | 30 min | **30 min** for a regex/heading check; **4 h** for anything meaningful | ⚠️ **Realistic only if trivial.** Validating markdown headings is 30 min and near-worthless. Validating that a plan is *executable* is a real project. |

**The deeper problem:** three of four "quick wins" are quick because they are underspecified. Only the Context Gauge has a hard, verifiable definition of done. Ship that one. The others are estimates attached to wishes.

---

## Knowledge Gap Assessment

| Gap | Real Blocker? | Verdict |
|---|---|---|
| Scaffold Model Selection Matrix | ❌ **No** | You are already using `longcat-2.0-free` (1M window, free). It works — this review was produced on it. Pick it. Revisit if it fails. Zero cost to defer. |
| Context Attestation Protocol | ❌ **No — paranoia** | Single-user, local machine, local DB. The threat model requires an adversary who has already achieved local code execution, at which point attestation is irrelevant. Pure M19 over-application. **Kill.** |
| Dialectic Session Schema | ❌ **No — but you are overthinking it** | The transcript *is* the schema. Store the markdown. Impose structure after you have 10 of them and can see the shape. Designing a schema for data you have never collected is how you get a schema you throw away. |
| Ensemble Routing Strategy | ❌ **No** | Not needed for initial PR. Not needed for Phase 1–3. See §4 Z3 critique. |
| Local Executor Capability Profile | ❌ **No — test as you go** | You have `qwen3-1.7b` at `context_window: 8192` in `config/models.yaml`. Give it a plan. See if it executes. That is the profile. Empirical > catalog. |

**Zero of five are real blockers.** All five are research tasks masquerading as prerequisites. This is the mechanism by which a project never ships: every unknown becomes a gate, and gates accumulate faster than they clear. The correct posture for all five is: *make the cheapest possible choice now, and let the Context Gauge's real data tell you if the choice was wrong.*

---

## The Carmack Alternative

**The 80/20 is one file, roughly 120 lines, and one paragraph added to the agent prompts.**

Everything valuable in 2,273 lines of spec reduces to this:

```python
# src/omega/oracle/context_gauge.py   —   ~120 lines total
#
# Reads the OpenCode session DB read-only. No env vars. No Z3.
# No aggregator. No state machine. Measured: 0.51 ms.

WINDOWS = {                       # merge into config/models.yaml
    "longcat-2.0-free":     1_000_000,
    "nemotron-3-ultra-free":1_000_000,
    "claude-sonnet-4-6":      200_000,
    "gemini-3.1-pro":       2_000_000,
}
DEFAULT_WINDOW = 200_000          # pessimistic, matches M7 classification posture
REDZONE, CLIFF = 0.75, 0.85

async def get_context_pressure(session_id: str) -> dict:
    def _read():
        db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        try:
            row = db.execute(
                "SELECT model FROM session WHERE id=?", (session_id,)
            ).fetchone()
            model = json.loads(row[0])["id"] if row and row[0] else "unknown"

            # LIMIT 20: newest message may be mid-stream with total=0 (FM-12)
            tokens = 0
            for (d,) in db.execute(
                "SELECT data FROM message WHERE session_id=? "
                "ORDER BY time_created DESC LIMIT 20", (session_id,)
            ):
                tk = json.loads(d).get("tokens") or {}
                if tk.get("total"):
                    tokens = tk["total"]
                    break
            return model, tokens
        finally:
            db.close()

    model, tokens = await anyio.to_thread.run_sync(_read)   # M1
    window = WINDOWS.get(model, DEFAULT_WINDOW)
    pct = tokens / window

    return {
        "model": model, "tokens": tokens, "window": window,
        "pct": round(pct * 100, 1),
        "to_redzone": int(window * REDZONE) - tokens,
        "status": "CRITICAL" if pct >= CLIFF - 0.05
                  else "REDZONE" if pct >= REDZONE
                  else "SAFE",
    }
```

Plus this, appended to agent prompts — this replaces the entire Phase 2 state machine:

> If context status is REDZONE or CRITICAL and your next action needs a large output, do not start it. Write 4 lines to `data/coordination/SSP_{session}.md` — what you were doing, next action, files touched, model tier needed — then stop and tell the user to escalate.

**That's it. That is the whole 80%.**

- Uses `tokens.total`, which is precomputed and correct — no arithmetic to get wrong
- Reads `session.model` from the DB — no unset env vars (kills FM-02, FM-14)
- Indexed + `LIMIT 20` — 0.51 ms on a 16.8 GB DB (kills FM-13)
- Handles the mid-stream `total: 0` case (kills FM-12)
- `anyio.to_thread.run_sync` for the blocking sqlite call — M1 compliant
- Read-only URI — cannot corrupt the DB, cannot take a write lock (mitigates FM-01)
- Model-aware from day one — no separate spec needed, kills the false-redzone bug the model-aware spec correctly identified
- Independently useful even if SDP is cancelled tomorrow

**What this buys you that 2,273 lines of spec did not:** real numbers. After ten sessions you will know whether 75% is right, whether cache reads track window occupancy, and whether agents actually respect the directive. *Then* you design Phase 2 — against data instead of against imagination.

---

## Recommended Immediate Actions

**This sprint. Nothing else. Total ≈ 5 hours.**

1. **[2 h] Build `src/omega/oracle/context_gauge.py`** exactly as above. Expose as MCP tool `omega-hub_get_context_pressure`. Merge `context_window` for cloud models into the existing `config/models.yaml` — do **not** create a new registry file (M2).

2. **[1 h] Write the tests that matter.** Not property tests. Four cases: sum-vs-latest regression (assert the gauge does **not** return ~1.2M for the session I measured — this is the FM-11 guard and it must exist in CI); mid-stream `total:0` fallback; unknown model → 200K default; DB locked → returns `status: "UNKNOWN"` and never raises into the agent path (M9).

3. **[30 min] Add the Redzone paragraph to agent prompts.** Free. Delivers all realistic Phase 2 value.

4. **[30 min] VERIFY OR KILL PHASE 4.** Determine whether OpenCode exposes any plugin API to change `session.model` mid-session. If no → mark Phase 4 **BLOCKED-BY-TOOLCHAIN** in the blueprint today and stop all Phase 4 specification work. This is a 30-minute check gating a multi-week phase. **Do it first if you do nothing else.**

5. **[1 h] Run the protocol on a real task and log it.** The gate is 3/10 and all 3 are self-referential. Use it on something that isn't SDP.

**Do not** start the Dialectic Logger. **Do not** install Z3. **Do not** write the SSP state machine.

---

## Recommended Phase 1 Actions

**Only after 10 real ledger entries exist.**

1. **Tune thresholds from measured data.** Is 75% right? The ledger will say. This is the actual reason Phase 0 exists.
2. **V-1 Vault** — on its own merits as Ark ticket V-1, not as an SDP dependency. It unblocks the Grok fabric pool too.
3. **Pool Gauge** — only once V-1 exists and has real pool numbers. Extend the same gauge function; do not build an aggregator.
4. **Planner schema validation** — only after ≥5 real Refactoring Manuals exist to derive the schema from.
5. **Re-open Phase 4** — only if action #4 above proved a session-swap API exists.

---

## What to Kill

| Kill | Lines | Reason |
|---|---|---|
| **`SDP_FORMAL_ROUTING_SPEC.md`** — entire document | 306 | Constraint solver for ≤8 items. Utility function's soft term is 6 orders of magnitude too small to ever matter. Z3 layer verifies a tautology. Replaceable with a 5-line `max()`. Dependency not even installed. |
| **Entropy Injection** (§4 of above) | ~20 | Randomly wastes the scarcest resource 10% of the time to prevent collusion between API accounts that cannot collude. M19 past its sane-boundary. |
| **`SDP_HARDWARE_HORIZON_SPEC.md` §3** SomaticState transfer | ~85 | Compatibility constraints (§3.4) exclude the cross-model use case §3.2 proposes. Self-contradictory. |
| **`SDP_HARDWARE_HORIZON_SPEC.md` §4** Energy Accounting | ~50 | The spec computes the term as negligible (0.0045 vs 15,000) and then specifies a dashboard for it. |
| **SSP State Machine** (`SDP_IMPLEMENTATION_SPEC.md` §2.2) | ~10 | No process owns the states. A markdown file is not a state machine. |
| **Multi-Gauge Aggregator** (`SDP_MODEL_AWARE_GAUGE_SPEC.md` §5) | ~60 | 2 of 3 sub-gauges have no backing systems. Build when data exists. |
| **Context Attestation Protocol** (knowledge gap) | — | Threat model requires an adversary who already has local execution. |
| **"Monolithic Fallacy" / "Composite Material" / "Corpus Callosum"** | ~15 | Strawman + obvious + a name for `write()`. |
| **The `SUM(tokens)` formula** (`SDP_IMPLEMENTATION_SPEC.md:41`) | 1 | **Measured 8.7× wrong on live data. Column does not exist. Must be corrected before any implementation.** |

**Net: ~550 spec lines deleted, ~120 code lines written.** That is the right direction for this ratio.

---

## Final Verdict

**The pattern is real, the specification is 8.7× wrong about the one number everything depends on, and you have written 2,273 lines of architecture without running a single query — build the 120-line gauge, delete the Z3, verify Phase 4 is even possible, and go collect the ten sessions of data your own protocol demands.**

---

## .plan

- **What I am working on:** Brutal architectural review of the Sovereign Distillation Pipeline (9 documents, 2,273 lines).
- **What I tried:** Read all 9 documents in full, then verified every load-bearing claim empirically against `~/.local/share/opencode/opencode.db` (16.8 GB, 2,435 sessions, 106,240 messages) and against the `src/omega/` tree. Ran 12 verification queries.
- **What the data shows:**
  - Spec's `current_tokens` formula: **8.7× overcount** (1,246,935 vs true 143,640) on live session `ses_016e894a3ffesRhuctnG50ihe8`. Would pin the gauge to CRITICAL at 14% real usage.
  - The `message.tokens` column **does not exist**; tokens are JSON inside `message.data`. Spec is unimplementable as literally written.
  - `tokens.total` is precomputed and correct; retrievable in **0.51 ms** via the existing `message_session_time_created_id_idx`.
  - 97.5% of measured context is `cache.read` (137,067 / 140,513) — omitted from spec's model.
  - `OPENCODE_MODEL_ID` / `OPENCODE_MODEL_CONTEXT_WINDOW`: **unset**. Spec's Priority-1 model resolution always misses. `session.model` JSON in the DB is the reliable source.
  - `ModelGateway` is not the OpenCode session inference path → Phase 4's continuity guarantee is unverified and likely undeliverable; FM-08 is a mitigation for the feature not working.
  - Z3: `ModuleNotFoundError` — not installed. Its utility function's soft term (`+2.0`) is ~6 orders of magnitude below `pool_remaining` (~10⁶), so it is provably inert.
  - Phase 0 gate: **3/10 sessions**, all dated 2026-08-09, all `*TBD*` accounts, all self-referential (documenting SDP itself). Automation specs written anyway, violating the protocol's own lines 26 and 298.
  - Full `part` table scan: **20.8 s** on the 16.8 GB DB — confirms any non-indexed gauge query is a hard failure (new FM-13).
  - SDP implementation code in `src/`: **0 files**.
- **What I'll do next:** Recommend the 5-hour immediate sprint — 120-line `context_gauge.py`, 4 targeted tests (including a CI regression guard against the 8.7× sum bug), the Redzone prompt paragraph, and the 30-minute Phase 4 toolchain feasibility check that gates weeks of downstream work.
- **Confidence:** **9/10** on all measured findings (primary-source DB queries and file reads, reproducible). **8/10** on the Phase 4 impossibility claim — verified the DB schema and plugin config, but did not exhaustively audit every OpenCode internal API; flagged as a 30-minute verification task rather than asserted as final. **7/10** on effort estimates (interpretation, not measurement).

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ SDP-REVIEW ⬡ 2026-08-09*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
