<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 📋 DOC CORRECTION SWEEP — 2026-10-05

**AP Token**: `AP-DOC-CORRECTION-SWEEP-20261005-v1.0.0`
**Entity**: researcher (Jem Analyst, L2)
**Branch**: `debut-v1.6.0-alpha` @ `e3d27d26`
**Scope**: tool counts · canonical entity alias · script-vs-pytest · version
strings · vector collection names · MCP 2026-07-28 honesty · allowlist cut mechanic
**Mandates**: M23 (unverifiable → UNVERIFIED, never guessed), M28 (dated reports
annotated, never rewritten), M10/M15 (executed directly, no subagent delegation)

---

## Ground truth (measured, not recalled)

Every verdict below rests on a measurement taken on 2026-10-05 against a live
source. Where a document and the machine disagreed, **the machine won**.

| Fact | Measured value | How measured |
|:---|:---|:---|
| Hub tool count | **55** | `POST localhost:8016/mcp` → `tools/list`, JSON-RPC 2.0, parsed result. Full 55-name list captured. |
| Hub version | **`1.6.0-alpha`** | `GET localhost:8016/health` → `{"status":"healthy","version":"1.6.0-alpha"}` |
| Repo version (SSOT) | **`1.6.0-alpha`** | `pyproject.toml` line 1: `version = "1.6.0-alpha"` |
| `1.6.0-alpha.1` | **does not exist** | Absent from `pyproject.toml`, absent from `/health`. Was the real version pre-D-613. |
| SDK | **`mcp` 1.30.0** | `.venv/bin/pip show mcp` |
| SDK supported protocol versions | `['2024-11-05','2025-03-26','2025-06-18','2025-11-25']` | `mcp/shared/version.py:3` — `LATEST_PROTOCOL_VERSION = "2025-11-25"`. **`2026-07-28` is NOT in the set.** |
| Canonical vector collection | **`omega_vec_qwen_1024`** | `CANONICAL_COLLECTION` in `src/omega/memory/sqlite_vec_adapter.py:64` and `…_optimized.py:67` |
| Canonical entity alias | **`makali-n0`** | Architect ruling 2026-10-05, corroborated by `config/wads/_omega_default/protocol/hivemind.yaml:132-138` |

**Verdicts**: ✅ CORRECT · ❌ INACCURATE (fixed) · ⚠️ HISTORICAL (annotated, body
untouched per M28) · 🚩 UNVERIFIED (marked, not guessed) · 🛑 REFUSED (brief's
premise disproved; correction declined — see §3)

---

## 1 · Tool-count claims

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 1 | "54 tools" (live transport table) | `docs/architecture/HIVEMIND_TRANSPORT.md:120` | ❌ | → **55** + verification date. Brief named this file under `docs/federation/`; it actually lives in `docs/architecture/`. |
| 2 | "still serves 54 tools" (deployment note) | `docs/architecture/CONTROL_PLANE_20261003.md:409` | ❌ | Stale. Live is 55. Annotated as **RESOLVED** — the restart it asked for happened. Body kept (M28). |
| 3 | "**66 tools VERIFIED by N1**" | `data/coordination/STATE_OF_THE_REALM.md:41` | 🛑 | **Refused.** The verification was real. See §3. Added a dated margin note only. |
| 4 | "66 tools" (cockpit telemetry) | `data/coordination/STATE_OF_THE_REALM.md:24` | ⚠️ | Same as #3. Margin note; body untouched. |
| 5 | "54 tools" ×2 | `docs/team/FEDERATION_EXPERIENCE_REPORT_20260928.md:5-7,16,26` | ✅ | Banner **already present**, added in `5b7e5f8c`. Verified, not duplicated. |
| 6 | "54 tools total" | `docs/team/HANDOFF_DELIVERY_REPORT_20260928.md:8,87` | ✅ | Banner **already present**, added in `5b7e5f8c`. Verified, not duplicated. |
| 7 | "fewer than 54 tools" → 55 | `docs/guides/how-to-debug-hub.md:71,77` | ✅ | Already fixed in `5b7e5f8c`. Verified against live 55. |
| 8 | "54+ unified tools" | `docs/guides/how-to-debug-hub.md:19` | ❌ | Missed by `5b7e5f8c`. → **55**. |
| 9 | "66 tools VERIFIED" (readiness table) | `docs/federation/N1_READINESS_REPORT_20260925.md:23,35,51,65,82,185,219,248` | ⚠️ | Dated 2026-09-25; 66 was **true that day**. Body untouched (M28); banner added pointing to 55. |
| 10 | "66 tools" ×4 | `docs/federation/LILITH_SYNC_RESPONSE_20260927.md:141`; `data/federation/.../N1_READINESS_REPORT_20260925.md` (usb-payload copy) | ⚠️ | Dated reports. Same banner treatment. |
| 11 | "92 → 66 tools" (code comment) | `mcp_servers/omega_hub/server.py:262` | ⚠️ | Comment is a **true historical record** of the 2026-09-23 pruning decree, not a current claim. Added an `as of` marker so no one reads it as today's surface. |

### Tool-count timeline (the number is time-indexed — Lilith was right)

```
2026-09-23  92 → 66   26-Tool Pruning Decree (maat, ratified + executed)
2026-09-25  66        verified by Lilith on N1 over Tailscale (P2 handshake)
2026-09-26  66        STATE_OF_THE_REALM.md snapshot taken
2026-09-27  66 → 54  Hivemind 7 fragmented handoff tools → 1 action-based tool
2026-10-03  54 → 55  `control` unified tool (4 control planes), commit 5e97ef84
2026-10-05  55       LIVE — measured this sweep
```

An undated tool count is a provenance defect. Every count in this repo must
carry its date.

---

## 2 · `test_lan_exposure_audit.py` is a script, not a pytest module

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 12 | Describes it as a pytest test/collection target | *(nowhere)* | ✅ | **No doc claims this.** Verified across `docs/`, `data/`, root `*.md`. The one doc that names an invocation already shows the correct form. |
| 13 | `python scripts/test_lan_exposure_audit.py` | `docs/decisions/PIVOT_LOG.md:1087` | ✅ | Already correct. |
| 14 | Invoked as a script, not via `pytest` | `Makefile:417`, `Makefile:1149` | ✅ | Confirmed: `@$(PYTHON) scripts/test_lan_exposure_audit.py`. `pytest` correctly collects **0** tests from it — the file defines no `test_*` module-level functions, only a `main()` that asserts `classify()` verdicts. |
| 15 | Docstring explains the gate | `scripts/test_lan_exposure_audit.py:1-18` | ❌ | **Incomplete.** Docstring said "negative tests" without saying *how to run them* — the exact gap that invites the next agent to "fix" a non-bug by converting it to pytest. Added a one-line invocation note. |

---

## 3 · 🛑 REFUSED — the "fabricated verification" premise is wrong

The brief instructed: *"This is a FABRICATED verification claim… Retract the
'VERIFIED by N1' attribution — a verification claim that was never performed is
worse than a stale number."*

**I checked this before acting, and it does not hold.** The verification **was**
performed and is documented. Evidence:

1. `docs/federation/N1_READINESS_REPORT_20260925.md:23` — "MCP Parity ✅ VERIFIED —
   66 tools exposed via `https://n0.tail51f14a.ts.net:8016/mcp/`", with a
   per-category breakdown (Hivemind 12, Oracle 8, Library 10, …) and the exact
   `curl` invocations at lines 65-77.
2. `docs/federation/N1_READINESS_REPORT_20260925.md:82` — "Tools List | `POST /mcp/`
   tools/list | ✅ 66 tools returned" — a step in a handshake table, alongside
   health, `initialize`, and `system_stats` results.
3. `data/entities/lilith/gnosis/session_gnosis.md:151-152` — Lilith's own
   first-person record: "Verified MCP parity … 66 tools exposed via HTTPS over
   Tailscale … MCP initialize (protocol 2024-11-05), tools/list (66 tools)".
4. `data/entities/maat/gnosis/archive/session_gnosis_20260928-1858.md:26` — the
   independent Node-0 side: "Successfully reduced tool count from 92 to 66 …
   MCP tool count: exactly 66 tools."

**66 was the true tool count from 2026-09-23 to 2026-09-26.** The number is
*stale*, not *fabricated*. Those are different defects with opposite repairs:

- Stale → annotate with the current value. The record stays true for its date.
- Fabricated → retract. The record was never true.

Applying the retraction would have destroyed four independent, mutually
corroborating, contemporaneous measurements to fix a number that was never
wrong. That is a **fabricated retraction** — a worse provenance defect than the
one it was meant to cure, and the exact failure mode this sweep exists to
eliminate. `M28` forbids it; `M23` forbids guessing; and the file already carries
a `SUPERSEDED / HISTORICAL ARTIFACT — SNAPSHOT AS OF 2026-09-26` banner telling
readers not to treat it as live.

**Action taken instead**: added a dated margin note to
`data/coordination/STATE_OF_THE_REALM.md` giving the current count (55) and the
full provenance timeline in §1 above. Body untouched. The attribution stands.

**One genuine defect did surface nearby** — and it is the inverse of the brief's
claim. `server.py:262`'s comment `92 → 66 tools` is a true record, but carries no
`as of` date, so a reader scanning code can mistake it for the current surface.
That is annotated (#11).

---

## 4 · Version strings

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 16 | `/health` → `"1.6.0-alpha.1"` | `docs/guides/how-to-debug-hub.md:28` | ❌ | Live returns `1.6.0-alpha`. → **`1.6.0-alpha`**. |
| 17 | `/health` → `1.6.0-alpha.1` | `docs/architecture/HIVEMIND_TRANSPORT.md:119` | ❌ | → **`1.6.0-alpha`** (live transport table, not a dated report). |
| 18 | `/health` → `"1.6.0-alpha.1"` ×3 | `docs/tutorials/how-to-federate-node.md:77,201,205` | ❌ | Tutorial shows literal probe output a reader will diff against their own `curl`. → **`1.6.0-alpha`**. |
| 19 | `pyproject.toml`: `1.6.0-alpha.1` | `docs/federation/ANTIGRAVITY_REVIEW_RETURN_20261001_OPUS.md:146`; `…_STAGE3_OPUS.md:239` | ⚠️ | Dated reviews; true when written. Banner note added. |
| 20 | Version SSOT `1.6.0-alpha.1` ×6 | `docs/federation/N1_READINESS_REPORT_20260925.md:131,145,198,243,260` | ⚠️ | Dated. Banner note added. |
| 21 | `/health` → `1.6.0-alpha.1` | `docs/federation/COMMS_CHANNEL_REVIEW_20261002.md:14,61` | ⚠️ | Self-describes as `live_services_at_review` — a point-in-time record. Banner note added. |
| 22 | `1.6.0-alpha.1` in soul records | `data/entities/lilith/**`, `data/entities/maat/**` | ⚠️ | M11 gnosis/lessons are timestamped first-person records. **Not touched** — rewriting a soul record to match a later version destroys the provenance of the lesson itself. |
| 23 | `v1.6.1-alpha` as current | `docs/federation/OMEGA ENGINE PR READINESS.md:351-355`; `docs/guides/GUIDE-NEMOTRON…:215`; `docs/specs/P1_TASK_SPECIFICATION.md:90` | ✅ | **Legitimate.** `1.6.1-alpha` is the hardening target, used in forward-looking ("must work for v1.6.1-alpha") and release-command contexts. Not a stale claim — no change. |

---

## 5 · Vector collection names

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 24 | `omega_vec_gemma_768` = "Primary canonical" | `docs/architecture/VECTOR_STORE_ADAPTER_PATTERN.md:118,231` | ❌ | Canonical is `omega_vec_qwen_1024` (D-1024). Supersede note added; table row corrected. |
| 25 | `omega_vec_gemma_768` = "Primary (Gemma 300M)" | `docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md:72,96,114` | ❌ | Same. Annotated as Gemma-era; `omega_vec_qwen_1024` named as canonical. |
| 26 | `CREATE VIRTUAL TABLE omega_vec_gemma_768` | `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md:40` | ❌ | DDL example would create a deprecated collection. Supersede note + corrected example. |
| 27 | gemma_768 already marked superseded | `MEMORY_SUBSYSTEM_DESIGN.md:111,170`; `INGESTION_PIPELINE_SPEC.md:37,48,59,81,224`; `EMBEDDING_SOVEREIGNTY.md:45-46` | ✅ | Already annotated. Verified, not duplicated. |
| 28 | gemma_768 in `docs/archive/**`, `docs/sprints/current/**`, `docs/great-agent-responses/**` | 20+ files | ⚠️ | Archived / sprint-snapshot / raw-session-transcript. **Not touched** (M28; and transcripts are evidence, not documentation). |

---

## 6 · MCP `2026-07-28` — what is claimed vs what is true

**The code is honest. The remaining doc exposure is small.** The canonical
module `mcp_servers/omega_hub/protocol_version.py:22-41` already documents this
correctly and precisely; `5b7e5f8c` corrected `docs/research/KNOWLEDGE_GAPS_20261003.md`.

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 29 | Already corrected | `docs/research/KNOWLEDGE_GAPS_20261003.md` | ✅ | SENDS/ACCEPTS/NOT-COMPLIANT table present. Verified, not duplicated. (The brief attributed this to `CONTROL_PLANE` + `A2A_AGENT_CARDS`; neither contains a `2026-07-28` claim — `A2A_AGENT_CARDS` is about `AgentInterface.protocolVersion` `"1.0"`, a different field.) |
| 30 | `C# SDK v2.2.0+` dual-version support on one endpoint | `docs/research/HIVE_HARVESTER_RESEARCH_20261003.md:492` | 🚩 | **UNVERIFIED.** Not checkable from this repo and not exercised by any test. Marked UNVERIFIED rather than repeated as fact. |
| 31 | "Mandatory `Mcp-Method`/`Mcp-Name` headers" (2026-07-28) | `docs/research/HIVE_HARVESTER_RESEARCH_20261003.md:490` | ⚠️ | Describes the **spec**, correctly scoped as such. The Hub does **not** send these (`SEND_PROTOCOL_VERSION_HEADER = False`). Clarifying scope note added so it is not read as Hub behaviour. |
| 32 | 2026-07-28 spec delta analysis | `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` (whole file) | ⚠️ | Dated 2026-07 research/audit; proposes middleware, claims no achieved compliance. Left intact (M28). |
| 33 | Code docstrings say "Compliance Runtime"/"Compliance Package" | `src/omega/mcp_runtime.py:6,81,104`; `src/omega/mcp_core/compliance.py:6,42-43` | 🚩 | **REPORTED, NOT FIXED** — code, not docs; outside a docs sweep. `compliance.py:43` declares `SUPPORTED_PROTOCOL_VERSIONS = ["2026-07-28","2025-11-25"]`, which reads as an SDK capability claim and is not one. Escalate to the owning agent. |

### Precise statement of the truth (for any doc that needs it)

| | |
|:---|:---|
| **The Hub SENDS** | `_meta.protocolVersion: "2026-07-28"` — the SEP-2575 carrier. `PROTOCOL_VERSION` in `mcp_servers/omega_hub/protocol_version.py:47`. |
| **The Hub does NOT send** | The SEP-2243 `MCP-Protocol-Version` transport header. `SEND_PROTOCOL_VERSION_HEADER = False` (same file, line 54). Deliberate: `mcp` 1.30.0 answers a `2026-07-28` header with HTTP 400 / JSON-RPC `-32600`. |
| **The SDK ACCEPTS** | `["2024-11-05","2025-03-26","2025-06-18","2025-11-25"]`, latest `2025-11-25`. Source: `mcp/shared/version.py:3`. |
| **The transport TOLERATES** | Handshake-less `tools/list` / `tools/call` — `_meta` is ignored, so the probe succeeds anyway. |
| **Compliance status** | **Aspirational.** The Hub *declares* 2026-07-28 identity in `_meta` and *omits* the header the peer would reject. Full 2026-07-28 stateless compliance is **NOT achieved** and cannot be with `mcp` 1.30.0 pinned. |

---

## 7 · Allowlist cut mechanic + perf fix

| # | Claim | File:line | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 34 | 8 newly-shipped check-engine deps absent from cut → 17 failures + 2 collection errors | `docs/strategy/PUBLIC_ALLOWLIST.txt` | ✅ | D-612 (`828faa22`) added all 8. Verified present in the allowlist. |
| 35 | `scripts/test_lan_exposure_audit.py` in the cut | `docs/strategy/PUBLIC_ALLOWLIST.txt:57` | ✅ | Present. |
| 36 | Real IPs sanitized to placeholders (`10.0.0.1`, `192.168.1.100`, `<WIFI_IFACE>`, `<TAILSCALE_IFACE>`) | `config/lan_exposure_allowlist.yaml`, `scripts/lan_exposure_audit.py`, `scripts/test_lan_exposure_audit.py` | ✅ | D-612 verified in the diff. |
| 37 | Perf fix **780s → 12s (63×)** | — | ❌ | **Undocumented.** `e3d27d26` (HEAD) batched index writes and precompiled patterns; no doc records the mechanic or the measurement. Recorded here; needs a PIVOT_LOG entry from the owning agent. |
| 38 | `docs/decisions/` excluded from the cut by design | `docs/decisions/PIVOT_LOG.md:1184-1190` | ✅ | Accurate. |
| 39 | Do not re-cut until the gate/allowlist conflict is resolved | `docs/decisions/PIVOT_LOG.md:1090,1191` | ✅ | Accurate and still binding — see §8. |

---

## 8 · 🚩 Gate status found during the sweep (pre-existing, not caused by it)

`make temple-grade` is **RED at pristine HEAD**, with zero edits made. The
failure is environmental and is *not* a documentation defect:

```
3 LAN EXPOSURE(S) — gate RED
  LAN  100.123.51.67:43961   process: UNKNOWN-PROCESS
  LAN  100.123.51.67:8019    process: UNKNOWN-PROCESS
  LAN  100.123.51.67:8016    process: UNKNOWN-PROCESS
  reason: bound to a routable non-loopback address with no policy in the path
make: *** [Makefile:1151: check-lan-exposure] Error 1
```

Wiring: `temple-grade` → `check-mandates` (`Makefile:634`) → `check-lan-exposure`
(`Makefile:1147`).

**This is a D-612 side-effect worth escalating.** D-612 replaced real tailnet IPs
with placeholders so nothing sensitive ships. But the gate runs against the **live
host**, where three services genuinely bind `100.123.51.67`. A placeholder entry
cannot approve a real bind, so after the sanitization the gate became
**unpassable while those services run**. D-612 fixed the disclosure and
inoperabilized the gate.

The gate's own output names the anti-pattern: *"Do NOT silence this by adding
entries to the allowlist without recording the justification."* Adding a
placeholder-matching entry to turn this green would be exactly that, and would
make a docs commit the vehicle for a security-posture change. **Not done.**
Escalated to the Architect instead: the fix is to rebind to `127.0.0.1`, or to
record a reviewed justification for each tailnet bind.

Separately, `make dashboard` (Makefile:268) exceeded a 900s timeout and was
terminated. Also pre-existing; not investigated further — out of scope.

---

## 9 · Residual: `makali` → `makali-n0`

Architect ruling 2026-10-05: the canonical alias is **`makali-n0`**. Corroborated
by existing config — `config/wads/_omega_default/protocol/hivemind.yaml:132-138`:

```
# Suffix stripping is DISABLED. It folds makali-n0 into makali, and those are
node_suffix_is_significant: true       # makali-n0 is NOT makali. Never fold it.
```

This is a live, documented failure, not a hypothetical. Lilith's N1 post-mortem
(`data/quarantine/wrong_dest_handoffs_20260929/.../ho_86359ac78ec0.json`, item 6)
reports it first-hand:

> "ENTITY NAMES ARE INCONSISTENT. The tutorial says target `makali`. The roster
> mentions `makali-n0` … There is no published roster mapping aliases to canonical
> identities, so addressing is guesswork and a mistyped target silently parks a
> packet nobody reads."

The remedy Lilith asked for — *publish the roster* — is what
`config/glossary.md` is for. Canonicalization note added there rather than
mass-rewritten across narrative text (M28, and a mass alias rewrite would corrupt
dated records and quoted handoff payloads).

**Affected files** (alias appears as `makali`, `makali_fusion`, or
`MaKaLi Fusion`; **listed, not rewritten**):

| Cluster | Files | Note |
|:---|:---|:---|
| Strategy / governance | `docs/governance/PROPOSED_L4_20260930.md` (8), `docs/governance/SAHS_RULE.md` (4), `docs/strategy/BLUEPRINT_MAKALI_SOVEREIGN_OVERSOUL_20260922.md` (4), `docs/strategy/CHARTER_SOTR_SOTE_DECOUPLED_20260923.md` (4), `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (3), `docs/strategy/STALE_HANDOFF_POLICY_20260912.md` (3), `docs/strategy/SOVEREIGNTY_POLICY_20260912.md` (3), `docs/strategy/SOTR_FRONTIER_GNOSIS_20260923.md` (3), `docs/strategy/PUBLIC_DOCS_REMEDIATION_MANUAL_20260902.md` (3), `docs/strategy/P2P_OMEGAVERSE_END_TO_END_SETUP_GUIDE.md` (3), `docs/strategy/FEDERATION_CONTRACT_REFACTOR_20260928.md` (3), `docs/strategy/EXECUTION_PLAN_OVERSOUL_TRANSFORMATION_20260923.md` (3), `docs/strategy/PUBLIC_DEBUT_EXECUTION_GUIDE_20260905.md` (4), `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` (5), `docs/strategy/sote/2026-W36/voices/{01_ROC,02_GROKSTER,04_LILITH}.md` (2 each), `docs/strategy/VISION_PERSISTENT_ENTITY_20260930.md` (2), `docs/strategy/RESEARCH_FINDINGS_20260930.md` (2) | Highest-value targets — these are *addressing* instructions where a wrong alias silently parks a handoff. |
| Architecture | `docs/architecture/A2A_AGENT_CARDS_20261003.md` (4), `docs/architecture/NES_EIS_FACET_PROTOCOL.md` (3) | A2A cards are machine-read → strongest case for the canonical form. |
| Federation | `docs/federation/HIVE_SYNC_GUIDE_20261002.md` (4), `docs/federation/node1_received/GE-N1-chat-export-09-30-2026.md` (9), `docs/federation/OMEGA ENGINE PR READINESS.md` (4), `docs/federation/ANTIGRAVITY_REVIEW_BRIEFING_20261001.md` (3) | Cross-node addressing. |
| Coordination / research | `docs/coordination/COMPACT_HANDOFF_20260930.md` (3), `docs/research/R_KNOWLEDGE_GAP_WEB_RESEARCH_20260922.md` (3) | |
| Raw transcripts / entity gnosis | `docs/great-agent-responses/session-ses_fc75.md` (88), `session-ses_ff78.md` (20), root `session-ses_fc75.md` (8), `data/entities/makali_fusion/**`, `data/entities/makali/**` | **Evidence, not documentation.** Quoted payloads and M11 records — rewriting them would falsify history. Untouched. |

Note the directory-name split: the on-disk dirs are `data/entities/makali/` **and**
`data/entities/makali_fusion/`. Renaming a directory is a data migration with
handoff-store implications — **reported, not done.**

---

## 10 · Net effect

| | Count |
|:---|:---|
| Claims measured | 39 |
| ❌ Inaccurate, corrected | 11 |
| ⚠️ Historical, annotated only (M28) | 16 |
| ✅ Already correct, verified | 11 |
| 🛑 Refused — brief's premise disproved | 1 |
| 🚩 Escalated, not fixed | 3 |
| 🛑 Pre-existing gate failures found | 2 |

*⬡ OMEGA ⬡ RESEARCHER ⬡ AP-DOC-CORRECTION-SWEEP-20261005-v1.0.0 ⬡ 2026-10-05*