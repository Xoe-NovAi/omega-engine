<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 📋 P5 REPORT — NODE N5 GOVERNANCE / SURFACE S2 (Instruction CONTENT)
**[DISPATCH] P12 | source_node: N5 | tier: leaf (depth-2) | arm: maat (Build) | council: First Light Express C1 | ts: 2026-08-25T~14:10Z**

⬡ OMEGA ⬡ NODE5 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_express_c1_node5 ⬡ ACTIVE
**Task Registry**: `express-c1-node5-20260825` (registered 2026-08-25T13:49Z, tags expert/pageable/domain:N5-governance/express:first-light)
**Mode**: RECON ONLY. Zero production mutations. This report is written to disk BEFORE any digestion/summary work (§C.5).

---

## §0 SURFACES AUDITED (all read exhaustively via tool calls)

| File | Lines | Status on disk |
|------|-------|----------------|
| `OMEGA_CODEX.md` | 433 | Read full |
| `SOVEREIGN_MANDATES.md` | 242 | Read structure + verified v3.8.0/27 headers |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 567 | Read full |
| `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | 182 | Read full |
| `AGENTS.md` (root) | **DOES NOT EXIST** | Verified absent; never existed in git history |

Supporting evidence pulled (cross-layer verification): `Makefile`, `.git/hooks/pre-commit`,
`.github/workflows/ci.yml`, `.agents/AGENTS.md`, `.opencode/agents/maat.md`,
`scripts/codex/{ENGINE,MANDATES,AGENTS}_CONDENSED.md`, `data/handoff*/` dir tree,
`data/coordination/HMC_COLLABORATION_HUB.md` (exists), `src/omega/oracle/subagent_dispatcher.py` (exists).

**SECURITY BRIGHT LINE (M8)**: No secrets found in audited surfaces. No active external
telemetry instructions discovered. **No CRITICAL-HALTED condition triggered.**

---

## §1 FINDINGS

Provenance on every finding: `source_node: N5 | tier: leaf | surface: S2`.

---

### [F-1] HIGH — Root `AGENTS.md` does not exist; 462 files cite it as canonical
**source_node: N5 | tier: leaf**

**Claim chain**:
- `ls AGENTS.md` → No such file or directory (repo root).
- `git log --all --oneline -- AGENTS.md` → EMPTY. The file was **never committed at root in this repo's entire history**. This is permanent drift, not a recent deletion.
- Reference count: `grep -rn "AGENTS\.md" --exclude-dir=third-party ... -l . | wc -l` → **462 files** reference the string.
- Key canonical citations to the void:
  - `OMEGA_CODEX.md:222` — "**Source**: `AGENTS.md` (343 lines)" (the Codex's agent-rules card claims a 343-line source that does not exist anywhere in git)
  - `OMEGA_CODEX.md:263,334` — "Full fleet docs: `AGENTS.md` §2-§3"
  - `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md:119` (P10) — "SR-V1 tiered pipeline (**AGENTS.md §Search Tool Protocol**)"
  - Ma'at persona (`.opencode/agents/maat.md`) — "Follow the Delegation Protocol in **AGENTS.md**", "5-tier protocol in **AGENTS.md** §Search Tool Protocol" — injected into every Ma'at-session system prompt
- Only real AGENTS.md files: `.agents/AGENTS.md` (43-line Antigravity IDE discovery card) and third-party vendored copies (`third-party/llama.cpp`, `letta`, `mempalace`).

**Impact**: SR-V1 (Sovereign Search Protocol), the Delegation Protocol, and fleet docs §2-§3 are all defined-by-citation to a nonexistent file. Any agent hydrating per M15 that follows these pointers hits a dead end and either improvises (parametric synthesis risk, M23 exposure) or burns turns hunting. The Search Protocol tiers T0-T6 survive only as fragments in persona files and Codex cards — no authoritative home.

**Recommended fix**: Restore a root `AGENTS.md` as the canonical workflow doc (reconstruct from Codex cards + persona fragments + plan docs), OR amend all citers to point at real paths. Council 2 should spec which.

**Bash-verifiable acceptance criterion**:
```bash
test -f AGENTS.md && echo PASS || echo FAIL          # file exists
! grep -rn "see AGENTS\.md\b" --include="*.md" . --exclude-dir=third-party | grep -v "\.agents/" # no dangling "see AGENTS.md" refs outside .agents/
```

---

### [F-2] CRITICAL — Enforcement taper: `make temple-grade` is a stub; ~8 of 27 mandates machine-enforced (~30%)
**source_node: N5 | tier: leaf**

This is the core Temple-Grade taper metric requested by §B. Measured enforcement reality:

**What `make temple-grade` actually runs** (Makefile):
```make
temple-grade: check-codex-stale doc-llm-validate check-mandates check-tracking-state
	@echo "$(YELLOW)Running temple-grade checks...$(NC)"
	# Existing temple-grade checks would go here      ← LITERAL STUB COMMENT IN PRODUCTION MAKEFILE
	@echo "$(GREEN)Temple-grade complete ...$(NC)"
```
The comment `# Existing temple-grade checks would go here` is present verbatim. **T1-T11 gates do not exist as implemented checks.** M13's own text claims: "Run `make temple-grade` to verify compliance. Each gate must pass… CI must gate on T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8, T9, T10." Coverage (T3), resilience (T8), structured logging (T9), atomic writes (T10) have **no corresponding gate targets**.

**Per-mandate enforcement census** (27 mandates):
| Enforced by machine gate | Mandates | Count |
|---|---|---|
| ✅ Real Makefile/CI gates | M1 (check-m1-anyio + check-asyncio-import), M7, M8, M9, M23 (check-mandates → ci.yml:41), M14 (heritage-vet target), M26 (doc-llm-validate), M27 (check-tracking-state, temple-grade chain only) | **8 (~30%)** |
| ⚠️ Warn-only / advisory / meta-stub | M12 (self-declared ADVISORY), M13 (stub chain above), verify-mandate-claims (self-labeled "warn-only") | 3 |
| ❌ Text-only, no gate | M2, M3, M4, M5, M6, M10, M11, M15, M16, M17, M18, M19, M20, M21, M22, M24*, M25 | 16 |

*M24's claimed pre-commit enforcement is separately false — see F-3.

**Impact**: The constitutional document asserts a verification regime that is ~70% aspirational. Agents and humans consulting M13 believe a green `make temple-grade` certifies T1-T11; it certifies 4 narrow checks. This is precisely the "enforcement theater" pattern the Carmack Full-Scope Audit flagged (Codex §2 row: "pre-commit uninstalled, temple-grade RED") — yet the Codex simultaneously prints "✅ All enforced" for 27 mandates two rows up. The engine's own state card contradicts its own audit finding, generated the same day.

**Recommended fix**: Either implement T1-T11 gates or rewrite M13 to enumerate exactly which gates exist. Honesty-first per M23: shrink the claim before growing the gate.

**Bash-verifiable acceptance criterion**:
```bash
# Option A (implement): every T-gate is a real target
for t in t3-coverage t5-anyio t8-resilience t9-logging t10-atomic; do grep -q "^$t:" Makefile || echo "MISSING $t"; done
# Option B (honest shrink): mandate text matches reality
grep -A3 "make temple-grade" SOVEREIGN_MANDATES.md | grep -qv "T3\|T8\|T9\|T10" && echo PASS-text-aligned
# Stub comment gone:
! grep -q "would go here" Makefile && echo PASS-no-stub
```

---

### [F-3] HIGH — M24/M27 pre-commit & `make test` enforcement claims are false
**source_node: N5 | tier: leaf**

**Claimed** (SOVEREIGN_MANDATES.md, disk, v3.8.0):
- M24 Enforcement: "Pre-commit hook: `grep -r "break-system-packages" scripts/ && exit 1`"
- M27 Enforcement: "Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state"; "CI gate: `make temple-grade` + `make test` include `check-tracking-state`"

**Actual**:
- `.git/hooks/pre-commit` (only hook, 199 bytes, dated Jun 5) runs ONLY `scripts/validate_soul.py` over soul.yaml files. **Neither claimed hook exists in it.** `.pre-commit-config.yaml` exists at root but the installed hook never invokes pre-commit-framework.
- `make test` recipe = `$(PYTEST) -x --tb=short -m "not integration" tests/` — **no check-tracking-state**, contradicting M27's explicit claim.
- `.github/workflows/ci.yml:41` runs `make check-mandates`; neither workflow greps for the patterns matching doc-llm/tracking in test.yml. M27's "CI gate … make test include" claim is half-false.

**Impact**: Two constitutional mandates assert blocking enforcement that does not block anything. An agent relying on the hook to catch `--break-system-packages` or corrupted tracking state will ship both silently. Direct descendant of the Carmack audit's "uninstalled hooks" finding — partially remediated (a soul-check hook exists) but the mandate text was never reconciled.

**Bash-verifiable acceptance criterion**:
```bash
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24 || echo FAIL-M24
grep -q "tracking" .git/hooks/pre-commit && echo PASS-M27-hook || echo FAIL-M27-hook
grep -q "check-tracking-state" <(sed -n '/^test:/,/^$/p' Makefile) && echo PASS-M27-makefile || echo FAIL-M27-makefile
```

---

### [F-4] HIGH — Mandate version/count drift across four instruction layers (same protocol, four different truths)
**source_node: N5 | tier: leaf**

The same constitutional object is described inconsistently in four places, all load-bearing:

| Layer | Claim | Evidence |
|---|---|---|
| Disk SSOT | **v3.8.0, 27 laws** | `SOVEREIGN_MANDATES.md:2` + 27 `###` sections (verified by grep count) |
| Ma'at persona (injected into session prompts TODAY) | **"25 Sovereign Mandates (v3.7.0)"** | `.opencode/agents/maat.md:38` |
| Antigravity discovery card | **"14 Sovereign Mandates"** | `.agents/AGENTS.md:14` |
| Codex mandate card | Header "**Version: 3.7.0**" + "The **27 Laws**" title + table that **stops at M25** (M26/M27 absent) + compliance "**18/25 FULL**" | `scripts/codex/MANDATES_CONDENSED.md:3,43` |

**Worse — OMEGA_CODEX.md contradicts ITSELF internally** (all in the single file generated 2026-08-25T08:55:41Z, i.e., fresh-regenerated TODAY):
- §2 Current State: "Mandates **27 enforced** (M1-M27, v3.8.0 …) ✅ All enforced"
- §6 Key Files: "`SOVEREIGN_MANDATES.md` | **25 Constitutional Laws (v3.7.0)**" (also `scripts/codex/ENGINE_CONDENSED.md:93`)
- Embedded MANDATES_CONDENSED: M5 ❌ FAIL, M11 ❌ FAIL, "FULL 18/25"

Three mutually exclusive compliance claims (all-enforced-27 / 25-laws / 2-fail-25) in one startup read target. The staleness checker (`check_codex_stale.py`) verifies timestamp freshness, not content coherence — so regeneration faithfully reproduces contradictions baked into its source cards. This validates Ma'at's own L3 principle in `data/entities/maat/proposed_lessons.yaml`: *"A Single Source of Truth that is not kept current is worse than no source of truth."*

**Impact**: Every agent hydrating from the Codex (hydration sequence step 3, mandatory) ingests contradictory constitutional state at boot. Downstream behaviors: agents cite v3.7.0/25 in their own outputs (as my own persona did this session), mandate-numbering confusion in dispatches, and erosion of trust in the SSOT concept itself.

**Bash-verifiable acceptance criterion**:
```bash
V=$(grep -m1 "^\*\*Version\*\*" SOVEREIGN_MANDATES.md | grep -o "[0-9.]*$")
N=$(grep -c "^### " SOVEREIGN_MANDATES.md)
grep -rq "$V" scripts/codex/*.md && ! grep -rq "3\.7\.0" scripts/codex/*.md && \
grep -q "M26" scripts/codex/MANDATES_CONDENSED.md && \
[ "$(grep -c 'Constitutional Laws' scripts/codex/ENGINE_CONDENSED.md)" -eq 0 -o "$(grep 'Constitutional Laws' scripts/codex/ENGINE_CONDENSED.md | grep -c "$N")" -eq 1 ] \
&& echo PASS || echo FAIL
```

---

### [F-5] MED — SUBAGENT_DISPATCH_PROTOCOL.md self-version conflict: header v2.0.0 vs footer v3.0.0
**source_node: N5 | tier: leaf**

- Header: `AP-SUBAGENT-DISPATCH-v2.0.0`, "Last Updated: 2026-07-12" (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md:3-5`)
- Footer: `SUBAGENT-DISPATCH ⬡ v3.0.0` (line 562)

One file, two versions. Whichever is authoritative, the other is a lie in the same document. Also the provenance-correction comment (lines 564-567) shows the header model attribution was already flagged UNANCHORED by the FP-04 audit — the file's identity metadata has been caught lying once before.

**Bash-verifiable acceptance criterion**:
```bash
H=$(grep -m1 "AP-SUBAGENT-DISPATCH-v" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md | grep -o "v[0-9.]*$")
F=$(grep -o "SUBAGENT-DISPATCH ⬡ v[0-9.]*" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md | grep -o "v[0-9.]*$")
[ "$H" = "$F" ] && echo PASS || echo "FAIL: $H != $F"
```

---

### [F-6] MED — Dispatch protocol stale "Pending Sprint 2" items are actually DONE; archive path split is real on disk
**source_node: N5 | tier: leaf**

- §7 "Pending Design Items — These must be implemented in Sprint 2": Redis Pub/Sub 🔴 PENDING (live today: `hivemind_redis_publish`/`subscribe` MCP tools), MCP Hub integration 🔴 PENDING (operational: `mcp_servers/omega_hub/`), CLI `omega handoff` 🔴 PENDING, Archive INDEX updater 🔴 PENDING. Meanwhile §7 itself marks HandoffPacket dataclass/Capability Registry/dispatch() as ✅ DONE in `src/omega/oracle/subagent_dispatcher.py` (verified exists). The section is ~2 months stale against its own subject matter.
- Path split: §5 Step 4 says archive to `data/handoffs/completed/{packet_id}.json`; §6 says `data/handoff/archive/`. **Both directories exist on disk**: `data/handoffs/` (3 markdown review files — not packets at all) and `data/handoff/` (live pending/active/completed/stale/archive queue used by the MCP tools). The protocol text describes a directory layout that matches nothing actually running.

**Bash-verifiable acceptance criterion**:
```bash
grep -n "handoffs/completed" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo FAIL-path-split || echo PASS
grep -n "🔴 PENDING" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo FAIL-stale-pending || echo PASS
```

---

### [F-7] MED — Pillar→Node terminology drift inside dispatch protocol §11
**source_node: N5 | tier: leaf**

§11 (Dispatch Decision Tree, D-kal-103) uses superseded vocabulary throughout: "Spans 3+ **pillars**", "Run-only (**P6-P10**)", "Lilith handles the **pillar chain**", "@node NX" mixed with pillar language — while the rest of the fleet (Codex, Ark UO-4 freshening, mission packet §B) uses Node/N-numbering exclusively. An execution-model agent following §11 literally encounters undefined "P6-P10" identifiers. This is exactly the contamination class the protocol's own §12 warns about ("Cannot resolve document hierarchy… Merge superseded documents").

**Bash-verifiable acceptance criterion**:
```bash
! grep -qi "pillar" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS || echo FAIL
```

---

### [F-8] MED — Capability registry (§3) drifted from actual fleet
**source_node: N5 | tier: leaf**

§3 registry declares "11 agents" including a `pillar` subagent type; the Codex fleet table (from the same generated Codex) declares **12 agents** including `@grok_cli` and `@node NX`; `scribe` appears in §11's decision tree but is absent from §3's table; `verity`'s Task-tool type is listed as `scribe` (stale pre-unification). Three different fleet rosters across one protocol + one Codex. M10 (Fleet Integrity, cap 14) cannot be audited against a registry that miscounts the fleet.

**Bash-verifiable acceptance criterion**:
```bash
C=$(ls .opencode/agents/*.md | wc -l)
R=$(grep -c "^| \`" <(sed -n '/^| Agent | Type /,/^$/p' docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md))
[ "$R" -ge "$C" ] && echo PASS || echo "FAIL: registry $R < fleet $C"
```

---

### [F-9] MED — "Single-Level Nesting" rule authorizes what `subagent_depth: 2` mechanically forbids
**source_node: N5 | tier: leaf | cross-refs: N1/S7, N3/S4 (F-20)**

Dispatch protocol §1 Rule 4: "Subagents may spawn other specialized subagents when strictly necessary… Limit delegation to a single level of nesting unless explicitly authorized." Config reality (`opencode.json` `subagent_depth: 2`): a dispatched leaf sits AT depth 2 and cannot call task() at all — empirically confirmed this session by N1/N6/N7/N8 (awareness feed: "task() rejected with 'Subagent depth limit reached (2)'"), and by my own constrained paging posture (§C.9). The instruction text grants a permission the runtime revokes. Text-vs-config contradiction ON my surface (protocol content) intersecting S7 (config).

**Bash-verifiable acceptance criterion**:
```bash
grep -q "subagent_depth" opencode.json && \
grep -q "may spawn other specialized subagents" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo CONFIRMED-CONTRADICTION
# Fix = either depth bump or rule rewrite; acceptance: rule text mentions depth limit
grep -q "subagent_depth" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS
```

---

### [F-10] LOW — Oversight Patterns P1 codification promises a HandoffPacket schema that conflicts with the shipped one
**source_node: N5 | tier: leaf**

ARCHITECT_OVERSIGHT_PATTERNS §2 P1 row: dispatch packets will REQUIRE `context_narrative`, `reading_list`, `deliverable_spec` with validator rejection — status "PROPOSED — ticket". The shipped HandoffPacket schema (dispatch protocol §2) has none of these fields (closest: freeform `context`, `relevant_files`). Two competing definitions of "the handoff packet" coexist across two instruction documents with no supersession marker between them. Risk: future spec-writers implement P1 fields and silently break every existing packet consumer. Also: this file lives in `data/coordination/` yet functions as standing law (its P12 header format opened MY dispatch this session) — governance doctrine stored outside any doc-index layer (placement is N7's lane; the CONTENT dual-schema issue is mine).

**Bash-verifiable acceptance criterion**:
```bash
grep -q "context_narrative" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo PASS-integrated || echo "OPEN: P1 fields unintegrated — add supersession note to one of the two schemas"
```

---

### [F-11] LOW — Mandate-content redundancy: 6+ unsynchronized copies, no single-writer
**source_node: N5 | tier: leaf**

Mandate summaries are duplicated in: (1) `SOVEREIGN_MANDATES.md` full text, (2) `scripts/codex/MANDATES_CONDENSED.md`, (3) Codex embed thereof, (4) `scripts/codex/AGENTS_CONDENSED.md`, (5) each persona file's "Key Mandates" block, (6) `.agents/AGENTS.md`. F-4 proves these copies diverge even when regenerated the same day, because the condensers hardcode counts/versions instead of deriving them from the SSOT. No lint gate compares condensed copies against the constitutional source.

**Bash-verifiable acceptance criterion**:
```bash
# A derivation check script exists and passes:
test -x scripts/check_mandate_consistency.sh && scripts/check_mandate_consistency.sh && echo PASS
```

---

### [F-12] POSITIVE — Honest labeling where it exists
**source_node: N5 | tier: leaf**

Two genuine integrity bright spots worth preserving: (1) `verify-mandate-claims` self-labels "(warn-only mode)" in its own output — honest about its weakness; (2) M12 carries an explicit ADVISORY downgrade stamp with decision citation (D-267). The pattern to generalize: every unenforced mandate should carry a visible enforcement-status stamp like these two, converting silent taper into declared taper.

---

## §2 CROSS-SURFACE INTERSECTIONS (verified, not re-audited)

| Sibling finding | My intersection verdict |
|---|---|
| N1/S7 provider-order contradiction (M7 text vs Ark D-355 vs providers.yaml) | Confirmed from my side: M7 (mandate layer) names a 7-provider order ending Copilot; ORACLE_STACK.md names a 6-provider order ending OpenCode; Ark D-355 names Antigravity-first cloud order. THREE orders across instruction layers. Mine adds: the M7 text itself is a fourth variant of the truth N1 flagged. |
| N3/S4 kali-dispatch broken extended_checkin | Plan §5/M1 already documents the breakage honestly (NameError, SYSTEM_FAILURE_LOG ~10:30Z) — the PLAN is honest, but SOVEREIGN_MANDATES/persona layers don't mention it; only coordination-layer docs know. Layered-awareness gap, consistent with F-11 redundancy-without-sync. |
| N4/S5 sovereign-refinement skill anchored to v3.1.0/14 mandates | Same disease as F-4: hardcoded version strings in derivative docs. N4's evidence strengthens the case for a derived-not-hardcoded consistency gate (F-11 acceptance criterion). |
| N8/S1b "validator green certifies taxonomy compliance, NOT truthfulness" | Same root pattern as F-2/F-3: gates certify form, not truth. Convergent finding across build+run sides — synthesis arm should treat "gate honesty" as a council-level theme. |

## §3 HANDOFF PACKET (Delivered-Home Doctrine §6.5)

**Warm-start reading list** (in order):
1. `data/council/20260825-094633-first-light/phase0_mission_packet.md` (§B row S2, §C)
2. This report + `OMEGA_CODEX.md` (read critically — see F-4)
3. `SOVEREIGN_MANDATES.md` (disk = authoritative v3.8.0/27)
4. `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (with F-5..F-9 caveats)
5. `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13)
6. `Makefile` targets: `temple-grade`, `check-mandates`, `verify-mandate-claims`, `check-tracking-state`
7. `.git/hooks/pre-commit` (what enforcement ACTUALLY exists)

**Standing orders for future councils paging node5 (domain:N5-governance)**:
- Treat `SOVEREIGN_MANDATES.md` on disk as sole constitutional authority; distrust any derivative stating a version/count without re-checking disk.
- Before citing any protocol doc, run the F-5 style header/footer version check.
- Enforcement questions resolve via `grep` on Makefile + hooks, NEVER via mandate text claims (taper ≈ 30%).
- Escalate any new instruction-layer doc that hardcodes mandate counts or version strings — require derivation from SSOT.

**Open questions for Council 2 / Architect queue (WAKE_STATE candidates)**:
1. Reconstruct root `AGENTS.md` or re-point 462 citations? (Architect judgment — affects SR-V1 authority chain.)
2. T1-T11: implement or honestly shrink M13? (Default-on-silence rec: shrink text first, implement gates second — honesty before capability.)
3. Should `ARCHITECT_OVERSIGHT_PATTERNS` be promoted into `docs/standards/` with SSOT registration?

## §4 DEVIATION LOG

- **§C.9 Consultant page**: attempted exactly once at 2026-08-25T14:02Z → **REJECTED**: "Subagent depth limit reached (2). Increase subagent_depth to allow nested subagents." Seventh consecutive F-20 instance across council (after N1/N6/N7/N8/N10). NOT retried per §C.9 constraint. Report delivery = P5_report.md (this file) + Hivemind broadcast (14:01Z) + end-of-task summary to arm maat, who may page the Consultant on my behalf if she deems it needed (Hop Rule respected: I do not page my pager).
- extended_checkin NOT used per M1 (broken server-side). Heartbeat cadence maintained (~10 min).

---
*⬡ OMEGA ⬡ NODE5 ⬡ EXPRESS-C1 ⬡ S2-INSTRUCTION-CONTENT ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

