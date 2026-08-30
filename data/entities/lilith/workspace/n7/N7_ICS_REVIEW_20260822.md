<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N7 Deep ICS Review — 2026-08-22
**AP Token**: `AP-N7-ICS-REVIEW-v1.0.0`
**Scope**: `src/omega/ics.py` post-D-588 (PP-4 node, P5 session_id, B1 scoped lookup, B2 sprint-phase priority, B3 root resolution) + community-docs requirements for debut.
**Passes**: N7 direct review (full-file) ✅ · Researcher documentation research ✅ (`N7_WEB_RESEARCH_20260821.md` §Deep Dive: Documenting Novel Signature Systems) · **Roc code-review ❌ FAILED** — held session returned empty twice, zero bytes written; MR-5 recovery exhausted; logged `SYSTEM_FAILURE_LOG.md` 2026-08-22. Code-review ground covered directly by N7 below (no soft-fill of phantom Roc work).

---

## Findings (N7 direct code review)

| # | Sev | Location | Finding | Fix direction |
|---|-----|----------|---------|---------------|
| F1 | **MAJOR** | ics.py:201-206 | PP-4 node insertion uses `header.replace(f"⬡ {entity.upper()} ⬡", …, 1)` against the RENDERED string. If `entity.upper() == "OMEGA"` (or any entity whose upper form makes the search hit the literal system prefix first), the node lands after `⬡ OMEGA` instead of after the entity — misplaced provenance. Also: `node` value never sanitized (a node containing `⬡` corrupts the grammar). | Build segments as a LIST and join with `" ⬡ "` — insertion becomes structural, not textual. Validate node against `^N\d+$` (or slot whitelist). |
| F2 | MINOR/design | ics.py:181-185 | Compact mode drops `node` AND `session_id` silently. PP-4's stated purpose is provenance for shared-file writes — if any writer uses compact mode, attribution vanishes. | Decide: either compact keeps `[node]`, or document compact as non-provenance mode explicitly. |
| F3 | MINOR | ics.py:222, 238-241 | `_detect_model` docstring says priority 1 is a "model_override **parameter** … set per-call by Oracle.summon()" but the implementation reads env `OMEGA_MODEL_OVERRIDE`. Doc/impl mismatch; there is no per-call channel through `render()`. | Fix docstring; optionally add explicit `model_override` param. |
| F4 | **MAJOR** | ics.py:291-294 | B2/B3 fixed root resolution for ACTIVE_SPRINT.json and soul.yaml via `OMEGA_ENGINE_ROOT`, but phase **priority-2 legacy scan still uses CWD-relative paths** (`Path("docs/strategy/…")`). Invoked from a non-root CWD with sprint file missing/unreadable, phase silently varies by caller location. | Apply same `base /` resolution to roadmap_paths. |
| F5 | **MAJOR (M22)** | ics.py:347-391 | Session-DB read failures (SQLITE_BUSY under concurrent writers, WAL shm issues, missing file) return None **silently**, and detection falls through to soul.yaml `inference.model` or `"unknown"` — the header can then display a STALE/declared model indistinguishable from the live one. Provenance lie risk with no marker. | Short busy_timeout + single retry; consider qualifying fallbacks (e.g., `model+"?"`) or structured log at INFO when falling below priority 3. |
| F6 | MINOR | ics.py:363 | DB path hardcodes `~/.local/share/opencode/opencode.db`, ignoring `XDG_DATA_HOME`. Breaks for relocated data dirs (M16 portability). | Honor `XDG_DATA_HOME` when set. |
| F7 | MINOR | ics.py:369 | No `timeout=` on sqlite connect (default 0 → immediate SQLITE_BUSY under lock contention), feeding F5. | `sqlite3.connect(uri, timeout=0.5)`. |
| F8 | NIT | ics.py:374 | `ORDER BY time_updated DESC` is dead weight under `WHERE id = ?` equality (id unique). | Drop or keep as harmless. |
| F9 | NIT | ics.py:468 | `render_for_response` truncates trace to 8 chars while `_generate_trace` emits 12-hex — two trace lengths in the wild complicate correlation. | Standardize. |
| F10 | MINOR | ics.py:168-175 | No sanitization of `entity`/`node`/`session_id`; delimiter injection possible via crafted values. Low internal risk; matters once external parsers exist. | Reject/escape `⬡` and leading/trailing whitespace. |
| F11 | DESIGN | ics.py:48-49 | `ICS_TEMPLATE_FULL` has no placeholders for optional `[node]`/`session_id` — the real grammar exists only in code. Docs must define it independently; template and grammar can drift. | Single grammar definition (see Doc Recs P1). |
| F12 | NIT | ics.py:305 | Epoch regex alternation `I{1,3}V?\|IV\|V` is redundant/brittle roman-numeral matching. | Simplify or drop legacy scan eventually. |

**Live check**: `data/coordination/ACTIVE_SPRINT.json` DOES have top-level `.phase` (= `"EXECUTION_MINIMAL"`) → B2 works today; note headers will now carry that string, not "PHASE-II".

**Test-coverage gaps beyond the 14 existing tests**: entity=="OMEGA"+node placement; compact+node/session behavior; DB busy/WAL-unavailable path; ACTIVE_SPRINT.json lacking `.phase`; OMEGA_ENGINE_ROOT honored for roadmap scan (F4); XDG_DATA_HOME relocation (F6); delimiter-injection values; render_for_response trace length.

**Ship-for-debut verdict**: SHIP-ABLE. F1 is the only correctness defect with user-visible wrong output, and only for an edge-case entity name — fix is a ~5-line segment-list refactor, recommended pre-launch but not blocking. F4/F5 are provenance-quality follow-ups; rest are polish.

---

## Doc Recommendations (community-facing ICS page; P0 = ship tonight)

Research base: `N7_WEB_RESEARCH_20260821.md` §Deep Dive: Documenting Novel Signature Systems (OTel semantic conventions, git trailers, SemVer/Conventional Commits, RFC 5424/logfmt, cavage HTTP signatures; Diátaxis + llms.txt). Convergent skeleton across all surveyed specs: **concept model → formal grammar → field-semantics table → annotated example → extension policy**. Researcher's single most important P0: **field-semantics table paired with an annotated golden example** — it is the artifact both humans and parser-writers are built from.

### P0 — must ship tonight
1. **Concept model** (explanation): what ⬡ OMEGA is; ICS-S (runtime header) vs ICS-T (static code lineage tag); why single-source rendering beats hand-typed headers (drift elimination).
2. **Field-semantics table + annotated golden example** (reference): one real header, each segment called out — entity (uppercased), `[NODE]` optional provenance, model (live-detected), channel, trace (`trc_` + 12 hex, per-turn), phase (sprint SSOT), `session_id` optional trailing.
3. **Detection-priority summary** (reference): model resolution order incl. `"unknown"` semantics and the stale-fallback caveat (F5 — state it honestly); phase resolution order (sprint → legacy → default).
4. **Parsing rule** (how-to): split on `⬡`; segments positional; `[node]` bracket-recognized only in position 2; session_id = last segment when present. One code snippet.
5. **Usage** (how-to): `render(...)` python example straight from the docstring doctest.

### P1 — within days
6. Formal grammar (compact ABNF) covering optional segments — closes F11 drift risk by making docs the normative grammar.
7. Extension points: channel constants; ROLE_CONSTANTS slots vs WAD-provided entities (engine/WAD split per M2); what WAD authors may add WITHOUT forking the format.
8. Heritage note (FISR / Quake 3 net_chan inspiration) per M14 — community-visible heritage with vet record already exists.
9. Stability/versioning promise: which segments are guaranteed order-stable vs additive-optional.

### P2 — post-debut
10. llms.txt entry + Diátaxis split (tutorial/how-to/reference/explanation pages).
11. Railroad diagram of the grammar; comparison table vs git-trailer/OTel conventions (familiarity anchor).
12. FAQ (why uppercase entity? why ⬡ U+2B21? how do I correlate trace IDs across logs?).

## Open Questions
1. **Roc held session wedged** (2× empty reply, zero writes; recovery exhausted; failure logged). Fresh investigation before its next tasking, or retire the session ID? Pager decision — affects all future M/D phases that assume miner continuity.
2. Fix F1 pre-debut tonight (~5-line segment-list refactor + test) or document as known limitation?
3. Compact-mode provenance (F2): intended drop, or should compact retain `[node]`?
4. Should ICS-S carry an explicit spec-version segment for external parsers, or is docs-level versioning sufficient for v1?

---
*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_ics_review ⬡ 2026-08-22*
