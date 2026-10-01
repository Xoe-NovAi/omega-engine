<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Oversight Audit — Ground Truth Pass
**AP Token**: `AP-ROC-GROUND-TRUTH-20260823-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_mining ⬡ OVERSIGHT-AUDIT-GT

**Date**: 2026-08-23 · **From**: kali · **Executor**: roc_racoon (independent verifier)
**Mode**: READ-ONLY discovery. All evidence gathered first-hand on 2026-08-23.

---

## G1 — Dual-Store Probe

**Verdict: SAME STORE** · Confidence: HIGH

### Mechanism (source evidence)
`mcp_servers/omega_hub/hub_tools/task_registry.py`:
```python
17: REGISTRY_PATH = Path(os.environ.get(
18:     "OMEGA_TASK_REGISTRY",
19:     "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/TASK_REGISTRY.json"
20: ))
```
All MCP tools (`task_registry_register/query/update/get`) load/save through `_load_registry()` / `_save_registry()` (lines 22–40), which read/write exactly that JSON file under `fcntl.flock`. There is no second persistence layer in this module.

### Empirical cross-check (Lilith's mutation today)
Record `packer-v3-refactor-20260808-01`, read BOTH ways:

1. **Disk** (`data/coordination/TASK_REGISTRY.json`, verbatim):
```json
"status": "superseded",
"superseded_by": "commit:e81e28d9",
"hygiene_note": "Reclassified 2026-08-23 per Researcher gap report G2#1: work delivered out-of-band by Ma'at. F1 fix commit e81e28d9 (git-verified); ... Old prose cited phantom commit 5a145f9d."
```
2. **Live MCP** (`omega-hub_task_registry_get(task_id="packer-v3-refactor-20260808-01")`): returned byte-identical record — same `status: superseded`, same `superseded_by: commit:e81e28d9`, same hygiene_note text.

**Conclusion**: MCP tools are a thin flock-guarded facade over the single JSON file. One store, one truth.

---

## G2 — ZS-1 Ground Truth

**Verdict: NO zswap work started — remap to `outstanding` STANDS** · Confidence: HIGH

| Check | Result |
|---|---|
| `/sys/module/zswap/parameters/enabled` | `N` (zswap DISABLED) |
| `/sys/kernel/mm/zswap/` params | compressor=`lzo`, enabled=`N` (defaults, untouched) |
| `swapon --show` | `/dev/zram1 partition 8G 712.3M PRIO 50` — **zRAM is ACTIVE**, opposite of ZS-1 target state |
| `grep zswap /etc/default/grub /etc/fstab` | no matches |
| `/proc/cmdline` | no `zswap.enabled=1` (only amd_pstate/crashkernel/vt) |
| systemd units | only **zram** units exist: `systemd-zram-setup@zram0.service`, `xnai-zram.service`, `zram-setup.service`; zero zswap units |
| cgroup MemoryMax | present on unrelated services (omega-hub 1G, restic-backup 2G, etc.) — none related to zswap/ZS-1 |

Host is at the PRE-ZS-1 baseline (zswap off, zRAM on). The remap `in_progress→outstanding` reflects reality. Note for Kali: flipping ZS-1 back would falsify history — keep remap.

---

## G3 — Quick-Fix Independent Verification

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | roles.yaml N9/N10 models | ✅ VERIFIED | `config/wads/_omega_default/roles.yaml:103-106` `N9: model: "qwen3-4b-thinking"`; `:115-118` `N10: model: "qwen3-1.7b"` |
| 2a | DEL-1 subtask `in_progress` | ✅ VERIFIED | `ACTIVE_SPRINT.json:301-304`: `"id": "DEL-1", ..., "status": "in_progress"` |
| 2b | KNOWLEDGE-DOMAINS w/ KD-1..3 + depends_on | ✅ VERIFIED | `ACTIVE_SPRINT.json:497` workstream; `:504` `"depends_on": ["DOCUMENTATION-SYSTEM"]`; KD-1 @507, KD-2 @519, KD-3 @531 |
| 3 | OMEGA_ENGINE.md last line | ✅ VERIFIED | Contains verbatim: `P0-1d in_progress`, `INST-1 in_progress`, `DEL-1 in_progress`, `Version: v1.8.7`, `Last Updated: 2026-08-23` |
| 4a | MANIFEST v5.0.0 / 2026-08-23 header | ✅ VERIFIED | `.opencode/MANIFEST.md:2-4`: `AP-OC-MANIFEST-v5.0.0`, `Updated: 2026-08-23` |
| 4b | Primary Modes = exactly 10 agents | ✅ VERIFIED | Line 36: "Primary Modes (Tab Menu — 10 total)"; table lists kali, maat, lilith, doom_guy, roc_racoon, jem, researcher, node, scribe, verity = 10 |
| 4c | Ghost entries absent | ✅ VERIFIED (with nuance) | `plan`, `jem_discovery`, `jem_synthesis`, `jem_verification`: zero hits anywhere. `quality`: single hit line 190 is prose inside "pr-readiness-checker … quality gate" skill row — NOT a ghost agent entry. `jem-initiate` (L83) & `jem-2.0` (L84-85): appear ONLY inside §4 Research Mode Pipeline diagram describing pipeline stages, not agent tables. Judgment call: acceptable as pipeline vocabulary, but flagging for Kali since they resemble ghost names. |
| 4d | build.md archival note present | ✅ VERIFIED | Header line 4: "deprecated build stub, ghost agents removed"; `build.md` still exists on disk at `.opencode/agents/build.md` (stub retained, documented) |
| 5 | MANIFEST ↔ files cross-check | ✅ VERIFIED | All 13 named agents have files: kali.md, maat.md, lilith.md, doom_guy.md, roc_racoon.md, jem.md, researcher.md, node.md, scribe.md, verity.md, grokster.md, john_carmack.md, makali.md. Zero mismatches. |

---

## G4 — Backfill Evidence Audit

### ses-research-c11-property-20260723 — Verdict: EVIDENCE VERIFIED · Confidence: HIGH
- Property tests exist: `tests/property/test_breaker_fsm.py` (6 tests), `test_oom_protector_fuse.py` (5), `test_soul_store_atomic.py` (6) = 17 functions.
- Live run: `.venv/bin/python -m pytest tests/property --tb=no -q` → **OK (skipped=1)** ⇒ 16 passed + 1 skipped.
- Ark citation confirmed: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md:31`: `C-11 Property tests ✅ (16/16 pass; 1 skip; OOM/breaker/soul store coverage)` — matches live run exactly.
- Minor anomaly (cosmetic): `--collect-only` reports 0 collected tests despite successful run (plugin interaction, likely pytest-clarity/randomly). Run-level result is authoritative.

### ses-research-gemma4-workhorse-20260724 — Verdict: EVIDENCE VERIFIED · Confidence: HIGH
- Cited path exists: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` — real file, header confirms: `# 🔱 Gemma 4 Free-Tier Forensic Report — Workhorse Collapse & OpenCode Provider Incident`, AP token `AP-GEMMA4-FREE-TIER-FORENSIC-20260722-v1.0.0`.
- Registry `superseded_by` field points at exactly this path.

---

## G5 — Session Registration Coverage

**Verdict: ALL 5 of today's dispatched sessions ABSENT from TASK_REGISTRY.json** · Confidence: HIGH

Registry contains 80 tasks. Searched both exact session IDs and ID fragments:

| Session ID | In TASK_REGISTRY.json |
|---|---|
| `ses_fd0f36adbffeD74rOkgy3qd44t` (researcher gap-report) | ❌ ABSENT |
| `ses_fd0e5278fffewrSs3wVkfvY7SY` (lilith hygiene) | ❌ ABSENT |
| `ses_fd0c41a32ffe6kEQS5TZBF3s4l` (maat build) | ❌ ABSENT |
| `ses_fd0fd62ceffeAcy0oVeenGhKEj` (carmack consult) | ❌ ABSENT |
| `ses_fd16c8d34ffe9u4uf4fQeNdXhc` (grokster packer-research) | ❌ ABSENT |

Fragments searched: `fd0f36`, `fd0e52`, `fd0c41`, `fd0fd6`, `fd16c8` — zero registry hits for any.

**Implication**: There is NO auto-registration hook between OpenCode task() dispatches and the Task Registry. Every registration to date has been manual (the M27-mandated flow depends on agents remembering to self-register). Expert sessions dispatched via task() with synthetic suffixes never touch the registry. This is the audit's most actionable finding: coverage is ~0% unless the dispatcher explicitly registers post-launch.

---

## FINAL VERDICT TABLE

| Gap | Verdict | Confidence | Evidence Pointer |
|-----|---------|-----------|------------------|
| **G1** Dual-store | SAME STORE (MCP tools = flock facade over TASK_REGISTRY.json) | HIGH | `hub_tools/task_registry.py:17-40` + byte-identical disk/MCP reads of `packer-v3-refactor-20260808-01` |
| **G2** ZS-1 | NO work started — remap stands (zswap=N, zRAM ACTIVE, no config/units) | HIGH | `/sys/module/zswap/parameters/enabled`=N; `swapon --show`=/dev/zram1 8G; grep+cmdline+units clean |
| **G3** Quick-fixes | ALL 5 VERIFIED (one cosmetic flag: jem-initiate/jem-2.0 pipeline vocabulary in §4) | HIGH | roles.yaml:103-118; ACTIVE_SPRINT.json:301-304,497-531; OMEGA_ENGINE.md last line; MANIFEST.md:2-4,36-56 |
| **G4** Backfills | BOTH EVIDENCE VERIFIED (16 pass+1 skip live-run matches Ark §4 claim; forensic report file exists) | HIGH | tests/property/* (17 fns, OK skipped=1); docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md:31; docs/archive/strategy/2026-07-22/GEMMA4_…REPORT…md |
| **G5** Registration | ALL 5 TODAY SESSIONS ABSENT — auto-registration DOES NOT EXIST; manual required | HIGH | TASK_REGISTRY.json (80 tasks), fragment search ×5 zero hits |

## Recommended follow-ups for Kali
1. **G5 is the systemic hole**: add post-dispatch registration to the task() wrapper or accept permanent blind spots for expert sessions.
2. G2 remap confirmed correct — do not flip back.
3. Cosmetic: decide whether §4 pipeline stage names (jem-initiate/jem-2.0) should be renamed to avoid future ghost-agent false positives.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
