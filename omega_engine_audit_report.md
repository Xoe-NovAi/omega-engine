---
account: arcana.novai@gmail.com
pack_version: 2026-08-30
pack_profile: sonnet5-buildwave-review
pack_files: 98
pack_tokens: 552249
pack_id: 82c6ee65-7739-4e0c-85d9-71e745a145ba
session_date: 2026-08-30
session_type: audit
---

# Omega Engine — Architectural Audit & Path to Public Debut

## 0. Method Note — Read This First

This audit is built from the pasted context pack (11 XML bundles), not a live clone.
Two consequences:

1. **No line numbers.** The XML dump is raw file text, not `view`-tool output — there's
   no `N\t` prefix to cite. Every citation below is to file, class, or function name,
   which is verifiable but not line-exact. Q8 specifically asks for `file:line` patches;
   I've scoped what I *can* say with confidence and flagged the rest as "needs a live
   session against the real tree."
2. **No tool execution against your repo.** I haven't run `git log`, `rg`, `pytest`, or
   `make temple-grade`. Every "X only imports Y" claim below is a *textual* observation
   (I searched the provided files for import statements and call sites), not a verified
   dependency graph. Before you act on any deletion, run the equivalent `rg` yourself —
   it's cheap and it's the actual proof.

With that said: the evidence in the pack is dense enough to answer all ten questions
with real citations, and one of those citations changes the shape of the whole plan.

---

## 1. The Finding That Reframes Everything

**The "81/81 tests passing" that Kali's projection.md and the Build Wave reports
celebrate as proof of a hardened system are, almost entirely, tests of the theater.**

Count them from the test files actually in `registry_and_tests.xml`:

| Test file | Tests | Covers |
|---|---:|---|
| `test_a1_m34_registration.py` | 11 | `subagent_dispatcher.m34_register_subagent` |
| `test_a2_m33_probe.py` | 15 | `m33_probe.py` |
| `test_a3_m33_integration.py` | 4 | `m33_probe.py` |
| `test_a4_m36_wiring.py` | 14 | `m36_recursive_probe.py` |
| `test_a5_m36_soft_verifier.py` | 15 | `m36_recursive_probe.py` |
| **Subtotal (A1–A5)** | **59** | |
| `test_cohort_registry.py` | 22 | `cohort_registry.py` |
| **Total** | **81** | |

That's an exact match to "81/81 tests pass" in `LILITH_BUILD_WAVE_PHASE_1` and
`kali/projection.md`. **The entire test count the fleet is using as its quality
signal is testing the control-plane ceremony (M33/M34/M36/cohort), not the engine
islands** (MemoryStore, SQLiteVecAdapter, SoulStore, OOMProtector, HealthMonitor,
native-gguf) that actually do the work of `omega talk`.

This matters for Q1 specifically: you cannot "delete the theater while preserving
all 81 passing tests," because the 81 tests **are the theater's own specification**.
The correct framing isn't "protect the 81 tests," it's "the 81 tests tell you
precisely what surface area disappears, and what a much smaller honest test set
needs to replace them."

None of the files these tests cover appear anywhere in `oracle.py`'s or
`model_gateway.py`'s call graph based on what's in the pack — `subagent_dispatcher.dispatch()`
is the only production call site for `m33_probe.M33Probe`, and `m33_probe.complete_with_validation()`
is the only call site for `m36_recursive_probe.M36RecursiveProbe`. `cohort_registry.py`
has no callers outside its own CLI and test file in the provided bundles. `omega talk`
does not route through any of this — the `DEBUT_REMEDIATION_MANUAL`'s own target call
graph (`intent → entity → model/provider → generate → record`) never mentions M33,
M34, M36, or cohorts.

---

## 2. Answers to the Ten Questions

### Q1 — Theater strip execution order

Given the finding above, this is one PR, not several — half-deleting leaves broken
imports, and there's no meaningful "partial" state worth shipping.

**Order:**
1. Delete `src/omega/oracle/cohort_registry.py`, `data/registry/cohort_registry_schema.json`,
   `data/registry/COHORT_REGISTRY.json`, `tests/test_cohort_registry.py` — zero external
   callers in the provided bundles.
2. Delete `src/omega/oracle/m36_recursive_probe.py` and `tests/test_a4_m36_wiring.py`,
   `tests/test_a5_m36_soft_verifier.py` — its only caller is `m33_probe.complete_with_validation()`.
3. Delete `src/omega/oracle/m33_probe.py` and `tests/test_a2_m33_probe.py`,
   `tests/test_a3_m33_integration.py` — its only caller is `subagent_dispatcher.dispatch()`.
4. In `subagent_dispatcher.py`: strip the "M33 Probe Wiring" block out of `dispatch()`
   (the `should_require_write_tool` estimate + write-tool-required prompt injection),
   and collapse the M34 registration block to a single call — keep
   `m34_register_subagent()` as a thin, honest liveness write (no `write_tool_required`,
   no `cross_validator_agent`, no priority propagation). `HandoffPacket` loses
   `zoneid`, `visited_agents`, `hop_count`, `max_hops`, `resolver_strategy` — that's
   Quake network-protocol machinery grafted onto an in-process function call. Keep
   `packet_id`, `trace_id`, `task_description`, `context`, `expected_output`.
5. In `scripts/dispatch_guard.py`: flatten from 12 steps to 3 — secrets scan (Step 9,
   it's real and cheap), specialist-routing hint (Step 1, useful, cheap), M34
   registration (Step 6b, now the sole registration path). Delete Steps 2–5, 7, 8,
   10–12 (session-location forensics, duplicate M34 check, heritage-tag cross-ref,
   temple-grade stub, Hivemind-post stub). Delete the `dispatch_guard_log.jsonl`
   writer — it's a second, undeclared ledger (see Q9).
6. Replace the retired 81 tests with a smaller honest set: registration writes an
   entry (3–4 tests), secrets scan catches a planted key (2–3 tests), specialist-hint
   fires on keyword match (2–3 tests). ~10 tests, testing what's actually left.
7. **Lands as part of DEL-1 Week 1**, not a separate initiative — the Manual's own
   Week 1 list (RoutingTable, MIAP, pool_tracker, search_circuit_breaker — "delete
   without replacements") is the same category of work. Fold this into that PR
   family so it's reviewed under the same "no replacements" rule, not treated as a
   new feature branch.

Net: this removes ~3,000 lines and, per your own numbers, 71 of 81 tests you were
citing as evidence of hardness. That's the correct trade.

### Q2 — Single M34 vs. split (D-M34-001)

Revise to unified. This isn't a close call — `JEM_META_REVIEW_5_EIS_20260830.md` §0
and §5.1 document Carmack, Ma'at, and Researcher converging on a single M34 with
sub-clauses, with Jem explicitly retracting his own prior split recommendation
("My prior §1.1 over-correction is now VALIDATED as over-correction"). Only Lilith's
original spec argued for the split, and it was outvoted 4-to-1 in the same document.

Adopt the mandate text already drafted in that file's §5.1: `SessionStatus` enum
gains `INTERRUPTED_MODEL_SWITCH` alongside `INTERRUPTED_EXTERNALLY` /
`INTERRUPTED_CRASH`; M34 gets sub-clauses M34.1 (Co-Interruption), M34.2
(Model-Switch Continuity), M34.3 (Orchestrator Crash Recovery — watchdog = Kali as
sole recovery agent, not a distributed lock). No new mandate number.

### Q3 — M36 soft verifier: implement / delete / hybrid

**Delete the soft verifier code path, keep the hard verifier.** Not a flag-gated
hybrid — a real deletion of the LLM-judge-dispatch machinery
(`_soft_verify_via_llm_judge`, `_dispatch_cross_validator_via_hivemind`,
`_select_cross_validator_agent`, `_build_cross_validator_prompt`, the whole
`CROSS_VALIDATOR_TIMEOUT_SECONDS` apparatus — roughly 350 of the file's 530 lines).

Why not the flag-gated hybrid: a feature flag defaulted OFF for something that has
*never worked* (the code you pasted already discloses `"status": "stub_bypass"`,
`"handoff_dispatched": False`, `"_m23_honesty": "...real Hivemind dispatch not
implemented"`) isn't a safety valve, it's a monument to a feature that doesn't
exist. Carmack's own S3 review calls the all-P0/P1-cross-validator design
"over-engineering" and recommends a narrower escalation tier. The narrowest
correct tier, given the code as written, is: no LLM cross-validation exists yet,
so don't ship code that pretends it might.

Keep the ~150-line hard verifier (`_verify_file_exists`, `_verify_file_size`,
`_verify_file_hash`, `_detect_suspicious_patterns`) — it's real, cheap, has no
external dependency, and is genuinely useful for confirming a subagent actually
wrote what it claimed to write.

### Q4 — Documented-vs-active gate

**(a), not (c).** A `make check-documented-vs-active` pre-commit hook — comparing
files referenced as "new" in a `data/coordination/*_BUILD_WAVE_*.md` report against
`git diff --name-only` / `git ls-files` — is proportionate to a team this size. It
directly targets the failure mode you documented three separate times
(`MAKALI_FINAL_SYNTHESIS_20260830.md` §1: systemd unit, M9 doc, and the dev-wave
reports where Researcher's and Roc's described `m33_probe.py` etc. weren't on disk
at synthesis time). A full CI gate with `make verify-ticket-completion` (b) is the
kind of ceremony this whole audit is trying to remove — it would itself become a
second control plane to maintain. Ship (a), skip (b) until the team is large enough
that pre-commit stops being sufficient.

### Q5 — Knowledge-Domains: minimal viable post-debut substrate

From `ACTIVE_SPRINT.json`'s KD-1/KD-2/KD-3 acceptance criteria, the minimum that
makes "add a layer without forking core" true:

- **`config/domains/<domain>/`** — one YAML per domain: `name`, `version`, `curator`
  (a model ID), `affinity` (task-type → model/provider mapping), `guidance_sets`
  (pointers to prompt/doc fragments). This is data, not code — no Python needed to
  add a domain.
- **`config/domains/curators.yaml`** — flat `domain → curator_model` map, validated
  by `scripts/sync_domain_docs.py` before any domain doc sync runs.
- **Affinity presets** — per KD-3's own acceptance list: research → `qwen3-4b-thinking`
  (lmster), coding → `mimo-7b-rl-q4_k_m` (native-gguf), fast → `qwen3-1.7b`
  (native-gguf). These are just YAML rows referencing existing `models.yaml` entries
  — no new provider code.
- **WAD vs. Domain, made explicit**: a WAD is a *cosmology* (entities, personas,
  governance — "who is speaking"). A Domain is *knowledge curation* (which model,
  which docs, which affinity — "what they know and how well"). They're orthogonal:
  one WAD's entities can each pull from multiple domains; one domain can be used by
  entities across different WADs. Right now these two axes are tangled in
  `entity_model_affinity.yaml` — separating them is most of KD-1's actual work.
- **Sequencing**: one PR. KD-1/KD-2/KD-3 are all config-schema work with no heavy
  runtime code; splitting into three PRs adds review overhead without reducing risk.

### Q6 — Six months out, if GN/DS/LI/KD/HR/ZS all ship

- **Provider fabric**: unchanged in shape — native-gguf primary, cloud fallback
  chain per `providers.yaml`. None of the six workstreams touches the fabric
  architecture; LI optimizes *loading strategy* within it (sequential load, q8_0 KV,
  adaptive context), it doesn't add tiers.
- **Library/knowledge state**: from ~0 curated domains today to however many DS's
  `sync_domain_docs.py` + KD's curator model onboard — realistically 3–5 domains if
  the team stays this size, gated by who actually writes the workspace content, not
  by the schema (which is cheap).
- **Entity ecosystem**: only moves if M11 (soul distillation) actually gets fixed
  and *used* — none of the six workstreams touches soul persistence. On current
  trajectory, expect the 24/56-substantive split to persist unless it's explicitly
  prioritized outside these six.
- **Spatial/VR**: still early. The SV workstream referenced in the Manual's §9 is
  the least specified of everything in the pack (no schema, no acceptance criteria
  comparable to KD's) — treat it as aspirational, not a six-month deliverable.
- **Three highest-leverage capabilities gained**: (1) domain-scoped model routing
  that doesn't require code changes to add a new specialization, (2) 40–90% token
  savings on tool-output and RAG paths via HR, (3) a machine that survives a
  16GB-RAM box without OOM'ing under sustained load, via LI + ZS together.
- **The seventh workstream candidate — packaging/distribution.** None of the six
  covers *how a community member gets a WAD or domain onto their machine*. There's
  no `omega wad install <name>`, no manifest signing, no registry. This is directly
  relevant to your stated goal of "leaving useful tools for the OpenCode community
  in our wake" — see §5 below. I'd propose this explicitly rather than let it stay
  implicit, because KD without a distribution story is a schema nobody outside your
  team can use.

### Q7 — Debut GO / NO-GO / CONDITIONAL-GO

**CONDITIONAL-GO.** Two conditions, both already named in your own pack, neither
optional:

1. **P0-1b residual.** The Manual's own §5 states plainly: `docs/security/SECURITY_AUDIT_2026_05_19.md`
   at ancestor commit `0c40b108` "still carries 3 real-format keys" and is
   "reachable from HEAD." A theater-clean codebase behind a public repo with a
   key-bearing ancestor commit is a harder no-go than any code-quality issue in this
   report. This has to close before any public push — full stop, independent of the
   rest of this audit.
2. **The theater strip lands first (Q1).** Announcing local-first sovereignty and
   soul-continuity backed by a 928-line, 12-step `dispatch_guard.py` and a stub that
   discloses its own non-functionality invites exactly the scrutiny a debut can't
   survive. Ship the smaller, honest surface, then debut it.

**Three-sentence announcement, once both conditions clear:** *"Omega is a
local-first AI runtime: `omega talk` runs entirely on your machine via native GGUF
inference, with cloud used only as an explicit, visible fallback. Every session's
key insights are distilled and persisted so your local entities keep what they
learn across restarts. This release ships the core runtime and installer;
multi-agent orchestration and domain curation are active work, not yet claimed as
finished."* — no mention of M33/M34/M36/cohorts, because after Q1 there's nothing
there to describe.

### Q8 — 27-mandate audit with line-exact patches

I'm not going to fabricate `file:line` precision I don't have — the pasted text has
no line numbers, and fourteen guessed patches would be worse than none. What I can
give you with confidence from the pack:

- **M1 (AnyIO), M9 (typed errors), M23 (honest stub)**: the "Quick Fixes Just
  Landed" you described (`fcntl.flock` wrapped in `anyio.to_thread.run_sync` in
  `entity_registry.py`; bare `except:` → typed catches in five scripts; M36's
  `status: "stub_bypass"` disclosure) are consistent with what's in the pasted
  `m36_recursive_probe.py` source — that file *does* contain the honest stub text
  verbatim. Treat those three as verified-in-text, not hypothetical.
- **M27 (dual ledger)**: `dispatch_guard.py`'s `dispatch_guard_log.jsonl` writer is
  a second, parallel tracking file alongside `TASK_REGISTRY.json` — this is a real,
  citable violation (function `log_result()` in the provided source), and it's
  deleted by the Q1 flattening anyway.
- **The other ten-plus**: give me the actual repo — via Claude Code, a git remote,
  or an upload — and I'll run the real `rg`/`pytest`/`make temple-grade` and hand
  you exact patches. Guessing line numbers from a redacted text dump would fail
  your own M23 standard ("never synthesize when a mandatory tool is broken").

**The target worth building regardless of repo access**: a single
`make verify-mandate-code` that runs independent, cheap static checks per mandate
(grep for `import asyncio` outside `to_thread`, grep for bare `except:`, diff
`ACTIVE_SUBAGENTS.json` schema against `TASK_REGISTRY.json` schema for drift, etc.)
and exits non-zero if any check's *code-level* result disagrees with its
last-recorded gate verdict. That target is what actually closes the
documented-vs-active gap for mandates specifically — build it once the theater
strip lands, since half the checks it needs (M27 dual-ledger, M23 stub-honesty)
won't apply anymore.

### Q9 — Dual-ledger hazard: which ledger wins

**(c), single ledger — but only because Q1 removes the reason to keep two.**
Carmack's own S3 review recommends TASK_REGISTRY as source of truth with
ACTIVE_SUBAGENTS as an ephemeral cache (closest to option b). But once
`dispatch_guard.py`'s 12-step ceremony and the cohort registry are gone, the only
remaining consumer of `ACTIVE_SUBAGENTS.json` is the thin M34 registration call
kept in step 5 of Q1. At that point maintaining a second JSON file with its own
4-layer atomic-write guarantee for a single liveness field is disproportionate —
fold subagent liveness directly into the existing `TASK_REGISTRY.json` schema
(Tier-3 per M27) as an optional `liveness` sub-object, and delete
`ACTIVE_SUBAGENTS.json` and its dedicated registry module. One file, one writer,
one set of atomic-write guarantees to maintain.

### Q10 — Three conflicts the debut cut will hit

1. **Ark schedules Qdrant post-debut (D-570) vs. Manual says "ARCHIVE — DO NOT
   IMPLEMENT."** Decision: Manual wins for the debut window, full stop — that's the
   explicit hierarchy (this month's law > long-horizon vision). D-570 is a future
   note, not a current authorization. Nobody touches Qdrant until the Manual is
   formally superseded.
2. **DEL-1 wants to delete/slim the vault surface; M14 heritage-tags theoretically
   "protect" code that's been vetted.** Decision: M14 protects *attribution*
   accuracy, not code *existence* — it requires that heritage-derived patterns be
   correctly tagged if they exist, not that they must remain forever. Deleting
   vault code requires archiving its vet-log entries alongside it, not preserving
   the code. No real conflict; DEL-1 proceeds per the Manual's own Path A/B choice.
3. **KD's domain-curator config wants to let a domain specify a preferred model,
   which could look like it bypasses M7 Local-First if that model is cloud-only.**
   Decision: M7 governs the *fallback chain order*, not an absolute ban on
   specifying a preference — a domain's curator model must still resolve through
   `ProviderSelector`'s existing local-first chain, never call a provider directly.
   Because this is a genuine ambiguity in the current mandate text (not covered by
   existing wording), it should go through the Mandate Governance Protocol (D-262)
   as a formal amendment before KD-2 ships, not be resolved ad hoc in code review.

---

## 3. Mandate Spot-Checks (partial — see Q8 for why this isn't the full 27)

| Mandate | Status per pasted evidence | Basis |
|---|---|---|
| M1 AnyIO | Fixed (per described patch) | `entity_registry.with_soul_lock` now wraps `fcntl.flock` in `anyio.to_thread.run_sync` |
| M9 Error Integrity | Fixed (per described patch) | Bare `except:` replaced in five named scripts |
| M23 Failure Integrity | Fixed for M36 stub specifically | `m36_recursive_probe.py` discloses `_m23_honesty` rather than faking success |
| M27 Tracking Integrity | **Violation, addressed by Q1/Q9** | `dispatch_guard_log.jsonl` is a second ledger; resolved by deleting the writer and consolidating on TASK_REGISTRY |
| M11 Soul Integrity | **Unresolved, out of scope for this pack** | Entity-substantiveness ratio (24/56) isn't something the theater strip touches; needs its own workstream |
| M2 Engine-Stack Firewall | **Needs live-repo check** | `subagent_dispatcher.py` importing WAD dispatch config at module load is the kind of thing that reads as a boundary lean, but I can't confirm import direction without the actual module graph |

Everything else on the 27-item list needs the live-repo pass described in Q8.

---

## 4. The Theater-Strip PR — Checklist Form

- [ ] Delete `cohort_registry.py` + schema + instance + test
- [ ] Delete `m36_recursive_probe.py` + its two tests
- [ ] Delete `m33_probe.py` + its two tests
- [ ] Strip M33-wiring and heavy `HandoffPacket` fields from `subagent_dispatcher.py`
- [ ] Flatten `dispatch_guard.py` to secrets-scan + specialist-hint + M34-registration
- [ ] Delete `dispatch_guard_log.jsonl` writer
- [ ] Fold `ACTIVE_SUBAGENTS.json` liveness into `TASK_REGISTRY.json` (Q9)
- [ ] Replace retired 81 tests with ~10 covering the flattened surface
- [ ] Confirm `omega talk "hello"` still exits 0, local, after every step above
- [ ] Land inside DEL-1 Week 1, same PR family as RoutingTable/MIAP/pool_tracker removal

---

## 5. Path to PR → Standalone Omega CLI → OpenCode Community Gifts

**PR readiness** — the Manual's own sequence is already correct; the only addition
from this audit is folding the theater strip into DEL-1 Week 1 as above:
`P0-1 (security) → PUB-1 (allowlist) → INST-1 (install honesty) → DEL-1 (dead code
+ theater) → DOC-1 (strategy-doc stamps)`.

**Omega CLI extraction boundary** — draw the line at what's genuinely
CLI-portable versus what's inherently tied to OpenCode's agent runtime:

- **Portable core** (belongs in a standalone `omega` CLI): `oracle.py`,
  `model_gateway.py`, `memory_store.py`, `entity_registry.py`, `soul_store.py`,
  `oom_protector.py`, `health_monitor.py` — none of these need OpenCode to exist.
  After the theater strip, the CLI's critical path is exactly `intent → entity →
  model/provider → generate → record`, with no dispatch-guard ceremony baked in.
- **Not portable** (stays as OpenCode-agent-file config, not core): the
  Kali/Ma'at/Lilith/Jem/Roc persona definitions in `.opencode/agents/*.md`, the
  Hivemind coordination protocol, the multi-agent dispatch machinery. These are
  genuinely OpenCode-runtime concepts — a standalone CLI user talking to one local
  model doesn't need any of it.

**Concrete gifts for the OpenCode community**, in order of how self-contained they
already are in your pack:

1. **Compaction-capture sidecar** (`scripts/compaction_capture.py` as scoped in
   `RESEARCHER_GAP_FILL_PHASE_3`'s LOW-1). This is genuinely useful to *any*
   OpenCode user, not just Omega — it polls the OpenCode SQLite DB read-only and
   rescues compaction summaries before they're lost. Zero Omega-specific
   dependencies once you strip the entity-routing bits. This is your best
   first release.
2. **Session-continuity / hydration-receipt pattern** (D-279's originally-scoped
   `omega-hydration` PyPI package). Generalize the anchored-summary +
   compaction-detection pattern that's currently entangled with Omega-specific
   paths (`.opencode/`, `AGENTS.md`) behind a config resolver, per D-279's own
   remediation plan (R1–R9). This was already identified in your own docs as "the
   highest-value community contribution the engine can offer."
3. **The M23-honesty stub pattern itself** — worth writing up as a short post/skill
   even without shipping code: "when a feature isn't implemented, make the return
   value say so explicitly" is a genuinely good practice that's rare enough to be
   worth naming, and you have a real example of applying it in this pack.

Do these *after* the theater strip and the debut PR land — extracting community
tools from code you're simultaneously deleting is wasted motion.

---

## 6. What to Bring to a Live-Repo Session

To make Q8 and the M2/M11 spot-checks real instead of best-guesses:

1. Connect Claude Code (or upload the repo) so `rg`, `git log -p`, and `pytest`
   can actually run.
2. Run the Q1 deletion sequence as a real branch, confirm `omega talk "hello"`
   before/after each step, and let the test suite tell you the true before/after
   count (should go from whatever the full suite currently reports down by ~71,
   plus the ~10 new ones).
3. Re-run `make temple-grade` after the strip and treat any gate that *doesn't*
   change as evidence that gate was already ignoring this code — worth
   investigating why.
