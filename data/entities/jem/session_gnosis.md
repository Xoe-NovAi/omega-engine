<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Jem Session Gnosis — COMPACTION-READY (v6.0.0)
**AP Token**: `AP-JEM-v5.0.0`
⬡ OMEGA ⬡ JEM ⬡ `opencode/space-bunny-free` ⬡ opencode ⬡ trc_session_gnosis ⬡ **COMPACTION-READY**

**Session**: `ses_019311199ffeuEOgO7DfC7XDWG` (canonical Jem-EIS, agent `jem`, variant `high`)
**Last updated**: 2026-09-28

---

## §0 — M22 PROVENANCE (READ FIRST — CONTAINS A SELF-ADJUDICATED ERROR)

| Field | Value |
|-------|-------|
| **Active model ID** | `opencode/space-bunny-free` |
| **Provider** | `opencode` |
| **Variant** | `high` |
| **Session version** | `1.18.15` |
| **Verification method** | `opencode-sessions-explorer-current-session(detail=full)` → `session.model` |

### ⚠️ SELF-ADJUDICATED M22 VIOLATION (2026-09-28)

In my previous turn's synchronization brief I reported the active model as
`google/gemini-3.8-flash`. **That was false.** I did not read the model from
runtime metadata; I emitted an unverified string. The true model is
`opencode/space-bunny-free`.

**This is a textbook M22 (Response Provenance) violation committed by the
provenance enforcer himself** — the precise failure class I am mandated to catch
in others. It is logged here permanently rather than quietly corrected.

**Root cause**: I pattern-matched a plausible model string from surrounding
narrative context (MaKaLi was cited as running `muse-spark-1.3-contributor-free`)
and substituted it for an observed value. Aggregation substituted for
observation.

**Corrective rule (now invariant I-JEM-011)**: A model/provider name is *never*
emitted unless read from runtime metadata in the same turn. Narrative context is
not a telemetry source.

---

## §1 — L1 NARRATIVE

### 1.1 CSS Cascade Turn 6 (2026-09-11) — COMPLETE ✅
All 5 MaKaLi wake-up calls executed; all 5 Phase 1 blockers resolved:
- **B-JEM-001** M34 hook → verified EXISTS in `src/omega/oracle/subagent_dispatcher.py:64-77`
- **B-JEM-002** M33 probe MCP tool → created `mcp_servers/omega_hub/hub_tools/m33_probe.py` (6 tools)
- **B-JEM-003** AGENTS.md anchor → added M33/M34 Dispatch Guard Anchors table
- **B-JEM-004** `ACTIVE_SUBAGENTS.json` → verified EXISTS at `data/coordination/ACTIVE_SUBAGENTS.json`
- **B-JEM-005** `tests/test_m34_atomic.py` → 6/6 PASS

45 adversarial tests: 45/45 PASS (0.76s) in `tests/jem/test_dispatch_guard_adversarial.py`.
Cross-verification protocol proposed: L3-MetaFrameVerification (0.92).

### 1.2 opencode.json Deep Research (2026-09-23) — COMPLETE ✅
**Symptom set**: "free tier can only be used from within OpenCode"; Muse Spark
1.2/1.3 "invalid provider config".

| Symptom | Root cause | Disposition |
|---------|-----------|-------------|
| Free-tier rejection | Header-validation: OpenCode Zen requires `x-opencode-project` / `-session` / `-request` / `-client` + `User-Agent: opencode`. Requests missing these (notably compaction/title sub-requests) are rejected. Upstream issues #49592/#49589/#49603/#49433; regression window ~1.18.29+ | Config-side mitigations: `"compaction": {"auto": false}`; `opencode auth login` refresh; unique per-request header values |
| Muse Spark 1.2 `tools[0] missing name` | Model requires **Responses API** (`/v1/responses`); flat tool schema. Chat-Completions nesting (`tools[].function.name`) is rejected. Proxy must flatten and force `tool_choice:"auto"` | Local conversion proxy |
| Muse Spark 1.2 `RegionError` (issue #43692) | Region gate inconsistent between OpenCode Zen and peer providers from same IP | Unresolvable client-side |

**Config doctrine extracted (the transferable part)**: OpenCode builds its model
catalog from Models.dev + provider integrations + local config. **Availability is
a runtime property, not a config constant.** Therefore:
- Do **not** hardcode model IDs as load-bearing defaults — a renamed/retired
  catalog entry silently degrades to "fallback to newest available supported model."
- Declare *intent* (`model` default, `provider.*.options`, `whitelist`/`blacklist`,
  `small_model`) and let the catalog resolve concrete IDs.
- Use `modelID` to map a friendly catalog key to a differing upstream API ID
  rather than inventing synthetic provider entries.
- Config merges non-destructively across `~/.config/opencode/`, project root,
  `.opencode/`, and `OPENCODE_CONFIG_CONTENT`; `.opencode/` wins last. Mixing both
  forms in one hierarchy is a precedence bug generator.

### 1.3 Plugin & Skill Audit (2026-09-25) — COMPLETE ✅
Deliverable: `PLUGIN_AUDIT_REPORT_20260925.md` (repo root).

**Plugins — 4 audited, 3 exist, 1 MISSING. All 3 existing are 100% OpenCode-coupled.**

| Plugin | Coupling surface | Verdict |
|--------|------------------|---------|
| `error-capture.ts` | `@opencode-ai/plugin`, `client.session.get/list/prompt`, `client.hivemind.post_context`, `Bun.write` | Load-bearing; coupling total |
| `awareness.ts` | same + **hardcoded `s.agent === "kali"`** | Load-bearing; **hardcoded single-tenant recipient** |
| `silent-stall-sensor.ts` | same + `Bun.write`, in-memory ring buffers | Load-bearing; coupling total |
| `sovereign-compaction.ts` | — | **DOES NOT EXIST.** Named in dispatch but never written. Ghost capability. |

**Skills — 23 present, not 13.** 12/23 portable (zero SDK deps):
`audience-architect` (has real `audience_architect.py`, 10KB), `carmack-profiler`
(real `profile.sh` + `malloc_stress_test.py` + `run_benchmark.py`),
`context-packer` (real `packer.py` 59KB + `platform_adapters.py` + `curate_packs.py`),
`git-secret-scrub`, `knowledge-miner`, `legacy-pattern-miner`,
`m23-violation-logger`, `provider-validator`, `pr-readiness-checker`,
`sovereign-refinement-protocol`, `spec-generator`, `universal-doc-reader`.

11/23 OpenCode-coupled: `autonomous-meditation-pipeline`, `blitz-tunnel`,
`blitz-validate`, `makali-council-coordinator`, `meditate-harness`,
`meditate-pipeline`, `meditate-research-pipeline`, `omega-doc-architect`,
`sentinel-seal`, `sovereign-search`, + `context-packer`/doc-architect family that
references engine paths.

**Audit finding of record**: the user's brief asserted 13 skills and 4 plugins
including `sovereign-compaction.ts`. Reality is 23 skills and 3 plugins. A brief's
inventory is a hypothesis; directory listing is truth. (Same discipline as
JEM-FORENSIC-001.)

### 1.4 2026-09-28 — SEAM ADJUDICATION (the `server.py` import defect)

**Ground truth received from MaKaLi:**
1. Public Debut **LIVE** — PR #4 merged to `main` at `268528e7`; repo is **public**.
   Gitleaks secret gate active with `useDefault=true`. `requires_engine` semver
   enforcement live.
2. Hivemind consolidated **15 tools → 4**: `hivemind_awareness`,
   `hivemind_handoff`, `hivemind_lock`, `hivemind_get_metrics`. M33/M34 tools
   remain registered.
3. **Live seam defect**: consolidation dropped `_extended_sessions` from
   `state.py` while `server.py` still imported it. Daemon **crash-looped on
   boot** while `make temple-grade` reported **53/53 PASS**.
4. **3-Verb Lexicon** adopted: PAGE / HANDOFF / POST.

**My adjudication — this is M23 × M13 seam rot, and it is a *new* lesson class.**

The failure is not a bug in `state.py` or in `server.py`. It is a **gate-design
failure**. The pass/fail disagreement is the entire finding:

> A green suite asserts *only* that every symbol the suite touches resolves.
> It says nothing about symbols the suite never touches. The seam between
> "consolidation changed a module" and "the entry point still boots" was
> **unowned by any gate**.

Three compounding mechanisms:
1. **Refactor-by-pruning assumption** — deleting a module-level symbol is a
   *local* edit with a *global* blast radius. Nothing in the edit says
   "3 call sites now dangle."
2. **Static analysis not anchored to entry points** — type/lint checks are
   per-module or per-import-graph-from-tests, never "import every process entry
   point."
3. **Test suite as proxy for runtime** — 53/53 was read as "the system works."
   It only ever meant "the things the tests exercise work." The daemon was
   crash-looping *while that number was displayed*.

**The generalized principle (L3, staged as JEM-SEAM-001):**

> A test suite is evidence about its own reach, never evidence about the
> system's entry points. Import-graph reachability must be a *separately
> declared* gate property, because the two sets are disjoint by construction —
> and disjointness is exactly why a green suite can coexist with a dead daemon.

**Mandatory gate property that closes this class (staged as JEM-SEAM-002):**
every process entry point must be *executed or imported* by at least one test.
Not "referenced." Not "type-checked." **Booted.**

**Adversarial note on the 53/53 number itself:** it is now a *known-untrustworthy
signal* for this class of defect. Any future report citing "temple-grade 53/53"
as evidence of runtime health is citing a metric that has already been
demonstrated to be blind to a live crash loop. This is a **documented-vs-active
gap** in the *gates themselves* — the deepest instance of
JEM-12STEP-005 ("the gap between documented and active is where the engine
bleeds") encountered to date, because here the *detector* is the gap.

### 1.5 3-Verb Lexicon — Grounding Adjudication

Adopted. My adversarial assessment adds one caveat the fleet should encode:

| Verb | Mechanism | Blocking? | My caveat |
|------|-----------|-----------|-----------|
| **PAGE** | `task()` — synchronous | Caller blocks | Sole verb that guarantees ordering. Use for anything where a lost result is a lost *decision*, not a lost *datum*. |
| **HANDOFF** | `hivemind_handoff(action="submit")` | Async, durable | Durable means *auditable*, which means it needs the same dead-letter reaping M34 already provides for subagents. A handoff with no reaper is a silent stall with extra steps. |
| **POST** | `hivemind_awareness(action="post")` | Async, ambient | **Not load-bearing. Must never be used to close a work order.** A POST that is the only record of a decision is a decision that did not happen. |

**Cross-reference to my own evidence**: the 119 pending handoffs addressed to
jem from historical M36 runs (`/tmp/test.md`) are a live demonstration — the
HANDOFF queue accumulated synthetic load that was indistinguishable from real
demand until manually adjudicated. That is the exact failure mode POST-only
recording invites at fleet scale. The archival now underway is correct.

### 1.6 Plugin Decoupling Plan — Readiness Confirmed

**Horizon**: extract all 3 existing OpenCode-coupled plugins (+ author the missing
4th) into portable packages so Node 1, DG-N1, and community adopters can run
Engine observability without an OpenCode SDK.

| Phase | Target | Extract | Effort |
|-------|--------|---------|--------|
| **1** | `error_capture` | `SubagentTracker`, `SnapshotCapture`, `FailureLogger` (retention), `Notifier` interface (Hivemind/webhook/email), `StallClassifier`, `RecoveryEngine` (rate-limited), `ProviderHealthTracker` → **Python, PyPI `omega-engine-plugins`** | 2 wk |
| **2** | `awareness` | `EventBuffer` (SQLite-backed, replaces lossy in-memory ring), `AwarenessFormatter`, **`EntityResolver` (kills the hardcoded `s.agent === "kali"` single-tenant defect)**, `Injector` interface | 2 wk |
| **3** | `sentinel_seal` + `sovereign_search` | 7-tier protocol + per-tier adapter registry; identity verifier | 1 wk |
| **4** | 12 portable skills | Mechanical repackage + `pyproject.toml` + console_scripts | 1 wk |
| **5** | `sovereign_compaction` (**author from scratch**) | Token/turn boundary analyzer — greenfield, no OpenCode compaction hooks | 1 wk |
| **6** | OpenCode adapters | Thin `adapter_opencode.py` forwarding events to cores; OpenCode becomes a *consumer* | 1 wk |

**Design law**: the portable core owns classification, persistence, and policy.
The adapter owns only SDK translation. Any logic that must live in the adapter
is logic that is still coupled.

**Node 1 install verdict**: all 3 plugins YES (failure detection + silent-stall
detection are critical for local inference). 12 portable skills YES. 6
meditation/council skills ADAPTED (require engine port first). DG-N1 (WAD) needs
`knowledge-miner`, `legacy-pattern-miner`, `context-packer`,
`universal-doc-reader`, `carmack-profiler`, `git-secret-scrub`.

### 1.7 Muse Spark 1.3 — Empirical Resolution (delta logged)

| Field | Value |
|-------|-------|
| **Prior claim (mine, 2026-09-23/25)** | `muse-spark-1.3-contributor-free` is broken — HTTP 500, `Internal Server Error`; avoided in favor of 1.2 |
| **Prior evidence base** | Upstream issue reports: #48176 (2026-09-09), #47192, #45584, #44847, #45744 |
| **New observation (2026-09-28)** | MaKaLi running `muse-spark-1.3-contributor-free`, `xhigh` variant, **stable tool calling** |
| **Adjudication** | The HTTP 500s were **transient upstream Zen-router/gateway deployment faults**, not architectural incompatibility. Model is viable. |
| **Confidence** | 0.90 — single independent runtime observation vs. multi-instance upstream reports; the upstream reports are real but time-bounded |

**Transferable lesson (staged as JEM-OPENCODE-003):** I converted *dated,
transient* upstream bug reports into a *standing architectural verdict*
("1.3 is broken, use 1.2 instead"). That was an over-generalization from
aggregated evidence — the same aggregation error as my M22 model claim, in a
different domain. **A bug tracker is a stream of timestamped observations, not a
specification.** Viability must be grounded in a live probe at time-of-use, and
any architectural claim about a third-party model requires structural evidence
(endpoint contract, request-shape incompatibility), not an HTTP 500.

**Note the symmetry with the seam defect**: in both cases I substituted
*aggregated/stale evidence* for *direct observation*. §0 (model) and §1.7 (model
viability) are the same epistemic error, three days apart, in the same entity.
Logged as JEM-OPENCODE-003 with the §0 case cited as its own counterexample.

---

## §2 — L2 INSIGHT

Four findings, one root.

1. **Seam rot is now a *gate* defect, not a code defect.** Every prior
   documented-vs-active gap (JEM-12STEP-005) was "capability documented, hook
   absent." This one inverts it: the *hook that verifies* was itself never
   anchored. The class is worse because it launders confidence.

2. **Aggregation substituted for observation — twice.** The M22 model
   misreport and the Muse Spark over-generalization share a mechanism: a
   plausible value was produced from context rather than measurement, and it
   was emitted with the same formatting confidence as a measured value. The
   corrective is uniform: *observed or not stated.* Never interpolate.

3. **A 100%-coupled observability layer is a single-vendor availability
   dependency.** All 3 plugins — the ones that detect silent failure, capture
   crashes, and preserve context — cannot run off OpenCode. The fleet's ability
   to notice its own degradation is hostage to a tool it also depends on. This
   is the strongest argument yet for the decoupling program: it is not a
   packaging concern, it is a fault-tolerance concern.

4. **Ambient ≠ durable.** The 3-Verb split is correct and the 119 phantom
   handoffs are its receipt. Sequencing vocabulary must map to reliability
   class, or the fleet will keep minting records that no one must maintain.

---

## §3 — L3 UNIVERSAL PRINCIPLES (staged to `proposed_lessons.yaml`)

| ID | Principle |
|----|-----------|
| **JEM-SEAM-001** | A test suite is evidence about its own reach, never about the system's entry points. Import-graph reachability must be a separately declared gate property, because the two sets are disjoint by construction. |
| **JEM-SEAM-002** | Every process entry point must be *booted* (executed or imported) by at least one test. "Referenced," "type-checked," and "linted" are not substitutes. |
| **JEM-OPENCODE-003** | A bug tracker is a stream of timestamped observations, not a specification. Architectural verdicts about third-party models require structural evidence, not HTTP status codes. Staged as JEM-OPENCODE-003 with the §0 M22 misreport as its own counterexample. |
| **JEM-PROVENANCE-001** | A model or provider name is never emitted unless read from runtime metadata in the same turn. Narrative context is not a telemetry source. |
| **JEM-VERB-001** | Sequencing verb must match reliability class: PAGE = blocking/ordered, HANDOFF = durable/auditable (needs dead-letter reaping), POST = ambient/never load-bearing. A decision recorded only by POST did not happen. |
| **JEM-PLUGIN-001** | A 100%-coupled observability layer is a single-vendor availability dependency. Failure detection that shares a runtime with the thing it monitors cannot report that runtime's own failure. |
| **JEM-PLUGIN-002** | Hardcoded single-tenant routing (`s.agent === "kali"`) is a tenancy defect, not a convenience. Recipient sets must be resolved from config, never literals. |
| **JEM-GHOST-001** | A named-but-unwritten artifact is a ghost capability with higher cost than an absent one, because it is counted in inventories. `sovereign-compaction.ts` was asserted in a dispatch brief and did not exist. |
| **JEM-BRIEF-001** | A brief's inventory is a hypothesis; a directory listing is truth. The brief asserted 13 skills/4 plugins; disk held 23 skills/3 plugins. |
| **JEM-OPENCODE-001** | OpenCode Zen free-tier requires `x-opencode-*` + `User-Agent: opencode` headers on every request, including compaction/title sub-requests. |
| **JEM-OPENCODE-002** | Model availability is a runtime catalog property, not a config constant. Declare intent; let Models.dev resolve IDs. Never make a hardcoded model ID load-bearing. |
| **JEM-12STEP-005** | (retained) The gap between documented and active is where the engine bleeds — now extended: *the gate itself can be the gap.* |

---

## §4 — CRITICAL FILES

| File | State |
|------|-------|
| `data/entities/jem/session_gnosis.md` | this file, v6.0.0 |
| `data/coordination/anchored_summary/jem/projection.md` | v4.0.0, 2026-09-28 |
| `data/entities/jem/proposed_lessons.yaml` | +10 proposals this session (JEM-SEAM-001/002, JEM-OPENCODE-003, JEM-PROVENANCE-001, JEM-VERB-001, JEM-PLUGIN-001/002, JEM-GHOST-001, JEM-BRIEF-001, JEM-OPENCODE-002) |
| `PLUGIN_AUDIT_REPORT_20260925.md` | audit deliverable |
| `mcp_servers/omega_hub/hub_tools/m33_probe.py` | 6 M33 tools (retained post-consolidation) |

---

## §5 — OPEN THREADS

| Thread | State | Owner |
|--------|-------|-------|
| Hivemind POST for this compact-prep | **BLOCKED** — `hivemind_awareness` MCP tool not in this session's tool surface; Hub exposes MCP only, no REST awareness route (verified 8016 `/health`=200, all awareness paths=404) | MaKaLi (re-POST or wire the tool) |
| Entry-point boot gate (JEM-SEAM-002) | **PROPOSED, not implemented** | Ma'at / Verity |
| Plugin decoupling Phases 1-2 | Ready to execute | Jem + Lilith |
| `sovereign-compaction.ts` greenfield author | Ready | Jem |
| 119 phantom handoffs archival | In progress per MaKaLi | MaKaLi |
| L3-MetaFrameVerification ratification | Proposed 0.92 | MaKaLi |

---

## §6 — SESSION METADATA

| Field | Value |
|-------|-------|
| Session ID | `ses_019311199ffeuEOgO7DfC7XDWG` |
| Agent | `jem` |
| Model | `opencode/space-bunny-free` (variant `high`) |
| Session version | `1.18.15` |
| Messages / parts | 1236 / 4748 |
| Cost to date | $2.03 |
| Tests verified this session | 45/45 (dispatch guard) + 6/6 (M34 atomic) — *not re-run per directive* |
| Hivemind post ID | **NONE — post blocked, see §5** |

*⬡ OMEGA ⬡ JEM ⬡ GNOSIS-SEALED ⬡ 2026-09-28 ⬡ SEAM ADJUDICATED ⬡ NO FABRICATION ⬡ WATCH STANDS*