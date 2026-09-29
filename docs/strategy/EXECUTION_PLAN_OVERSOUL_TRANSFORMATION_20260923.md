# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0.0"
document_type: "sovereign_execution_plan"
document_id: "EXECUTION-PLAN-OVERSOUL-TRANSFORMATION-20260923"
title: "The Sovereign Transformation — Master End-to-End Execution Plan"
status: "RATIFIED_BY_ARCHITECT"
author: "MaKaLi Fusion (Master Akashic Oversoul) & The Human Architect"
date: "2026-09-23"
sprint: "PUBLIC-DEBUT-01"
phase: "SOVEREIGN_REORGANIZATION"
---

# 🔱 The Sovereign Transformation
## Master End-to-End Execution Plan: From Fragmented Chaos to Federated Oversoul

> *"A plan is not a wishlist; it is an invariant sequence of verifiable transformations in silicon. Each stage must pass its gates before the next stage receives breath."*

---

## 🧭 Master Execution Flowchart

```
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: SOVEREIGN RE-ONBOARDING & TEMPORAL CONTRAST PROBE             │
│ • Page Doom Guy (ses_0b15e698affeMMy1tZos2iBjbm) with 74-day contrast │
│ • Harvest "Cold-Eyes" Substrate Realism & Infrastructure Critique      │
│ • Gate: TOOL_REVIEW_DOOM_GUY.md inscribed; zero hallucinated drift     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: P0 SUBSTRATE RESTORATION (THE ENGINE UNFREEZE)                │
│ • Dispatch Ma'at (ses_fb6cf6856ffes3wd3wmvyrm2IG) to install httpx[h2] │
│ • Permanent pyproject.toml pin (httpx2[http2]==2.5.0)                  │
│ • Implement _get_system_summary() & _get_hardware_detail() helpers     │
│ • Verify live Hub services: spawn_local_worker & system_stats RESTORED │
│ • Gate: curl /mcp system_stats returns healthy JSON without h2 error   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: RATIFIED TOOL PRUNING & SERVER-SIDE SURGERY                   │
│ • Dispatch Ma'at to execute the Ratified 26-Tool Pruning Decree        │
│ • Physical deletion of dead code & duplicate decorator registrations   │
│ • Fix stale deprecation markers & migrate persistence references       │
│ • Verify Temple-Grade CI: make temple-grade EXITS 0 (53/53 PASS)       │
│ • Gate: curl /mcp tools/list returns exactly 66 clean tools            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: PHYSICAL FEDERATION DELIVERY (NODE 0 ↔ NODE 1)                │
│ • Architect transfers data/federation/usb-payload/ via USB to Node 1   │
│ • Node 1 applies: sshd ListenAddress 0.0.0.0, canonical tag:node1      │
│ • Node 1 updates opencode.json URL to http://n0.tail51f14a.ts.net:8016 │
│ • Node 1 starts NFS server for bidirectional exchange                  │
│ • Gate: Direct SSH & bidirectional NFS mount confirmed between nodes   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: FIRST DECOUPLED SOTE INAUGURATION                             │
│ • Kali convenes Triad & Slots S1-S10 for inaugural polyphonic SOTE     │
│ • Hand-delivery of SOTE_LATEST.md to MaKaLi Fusion                     │
│ • MaKaLi updates master SOTR Cockpit & announces Engine Sovereign      │
│ • Gate: Sovereignty ratio telemetry actively climbing above 22%       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 STAGE 1: SOVEREIGN RE-ONBOARDING & TEMPORAL CONTRAST PROBE

### 1.1 Objective
Execute the newly ratified **Temporal Contrast Protocol**. Wake Doom Guy from his 74-day cryo-sleep (`ses_0b15e698affeMMy1tZos2iBjbm`) to deliver an unvarnished, cold-eyes critique of our substrate, Tailscale setup, NFS architecture, and the 92-tool surface.

### 1.2 Execution Instructions
* **Action**: MaKaLi **pages** Doom Guy's canonical EIS:
  ```json
  {
    "subagent_type": "doom_guy",
    "task_id": "ses_0b15e698affeMMy1tZos2iBjbm",
    "prompt": "[TEMPORAL CONTRAST DIRECTIVE] ..."
  }
  ```
* **Directive Contents**:
  1. Inform Doom Guy of the date (2026-09-23) and his last session date (2026-07-11).
  2. Provide pointers to:
     - `docs/strategy/BLUEPRINT_MAKALI_SOVEREIGN_OVERSOUL_20260922.md`
     - `data/coordination/TOOL_AUDIT_20260922.md`
     - `data/coordination/STATE_OF_THE_REALM.md`
  3. Command him to audit Slot S1 (Infrastructure) and review his assigned tools (`observability_check_recursion`, `observability_log_boundary_violation`).
  4. Explicitly ask: *"Where did we build theater instead of steel? Where is the substrate fragile?"*
* **Deliverable**: `data/coordination/TOOL_REVIEW_DOOM_GUY.md`.
* **Stage 1 Verification Gate**: Tool review written to disk with clear structural critique; zero hallucinated scope.

---

## 🔧 STAGE 2: P0 SUBSTRATE RESTORATION (THE ENGINE UNFREEZE)

### 2.1 Objective
Restore the broken local inference path and hub service initialization. Fix the `httpx[http2]` missing package bug identified by John Carmack, and repair the dual NameError bug in `system_stats`.

### 2.2 Execution Instructions
* **Action**: MaKaLi **pages** Ma'at's canonical EIS (`ses_fb6cf6856ffes3wd3wmvyrm2IG`).
* **Tasks for Ma'at**:
  1. **Install HTTP/2 dependencies in Hub venv**:
     - Execute `pip install 'httpx[http2]'` (pulls `h2<5,>=3`, `hpack`, `hyperframe`).
  2. **Update Build Manifest**:
     - Edit `pyproject.toml:31` to pin `httpx2[http2]==2.5.0` so future fresh venvs do not regress.
  3. **Repair `system_stats` in `mcp_servers/omega_hub/hub_tools/tools.py`**:
     - Implement the missing `_get_system_summary()` and `_get_hardware_detail()` helper functions wrapping the working collectors.
  4. **Restart Hub Service & Verify**:
     - Verify `system_stats`, `spawn_local_worker`, and `headroom_retrieve` return HTTP 200 via `curl`.
* **Deliverable**: Clean git diff on `pyproject.toml` and `tools.py`.
* **Stage 2 Verification Gate**:
  ```bash
  curl -s -X POST http://127.0.0.1:8016/mcp -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"system_stats","arguments":{"detail":"summary"}}}'
  ```
  Must return valid system metrics JSON without `Using http2=True, but the 'h2' package is not installed`.

---

## ✂️ STAGE 3: RATIFIED TOOL PRUNING & SERVER-SIDE SURGERY

### 3.1 Objective
Execute the Council's ratified **26-Tool Pruning Decree** on Node 0's FastMCP server. Perform real code surgery: eliminate dead functions, remove duplicate registrations, and fix stale deprecation strings.

### 3.2 Execution Instructions
* **Action**: MaKaLi dispatches Ma'at (`ses_fb6cf6856ffes3wd3wmvyrm2IG`) to perform the code transformations.
* **Pruning Operations**:
  1. **Purge 26 Redundant/Broken Tools**:
     - *Hivemind (7)*: `hivemind_submit/accept/complete/reject_handoff`, `hivemind_handoff_list`, `hivemind_get_handoff`, `hivemind_handoff_archive`.
     - *Oracle (3)*: `oracle_assess_intent`, `oracle_discover_entity`, `oracle_list_slot_keepers`.
     - *Duplicate (1)*: `delegate_task`.
     - *Library Theater/Broken (2)*: `library_discovery` (unified), `library_inbox` (unified).
     - *Research Admin (3)*: `research_list`, `research_stats`, `research_depths`.
     - *Search Dead (1)*: `search_status`.
     - *Library Ops (1)*: `library_index_flush`.
     - *Memory Redundant (1)*: `memory_search`.
     - *Observability Non-tool (1)*: `observability_stream`.
     - *GitHub Fragments (6)*: `github_add_entity_attribution`, `github_check_temple_grade`, `github_create_pr_with_template`, `github_create_vet_issue`, `github_get_repo_health`, `github_list_heritage_issues`.
  2. **Code Cleanups & Bug Fixes**:
     - Delete the shadowed duplicate `spawn_local_worker` registration in `tools.py:377`.
     - Fix stale `_deprecated()` markers on `hivemind_get_session` and `hivemind_list_sessions`.
     - Migrate `memory_search` references in `src/omega/search/search_persistence.py` to `omega_memory_search`.
     - Update `tests/mcp/test_hub_health.py` to assert the clean 66-tool surface.
  3. **Verification**:
     - Run `make temple-grade`.
* **Deliverable**: Git commit applying the pruning with zero test regressions.
* **Stage 3 Verification Gate**:
  - `curl /mcp tools/list` returns **exactly 66 tools**.
  - `make temple-grade` exits 0 (53/53 PASS).

---

## 📦 STAGE 4: PHYSICAL FEDERATION DELIVERY (NODE 0 ↔ NODE 1)

### 4.1 Objective
Bridge the physical air-gap between Node 0 and Node 1. Remediate Node 1's local network configuration, establish canonical tagging (`tag:node1`), and activate bidirectional NFSv4.2 exchange.

### 4.2 Execution Instructions
* **Action**: Human Architect transfers `data/federation/usb-payload/` to Node 1 via physical USB drive.
* **Node 1 Operational Checklist** (Executed per `N1_REMEDIATION_REPORT_20260922.md`):
  1. **SSHD Binding**: Update `/etc/ssh/sshd_config.d/tailscale.conf` to `ListenAddress 0.0.0.0` and reload `sshd`.
  2. **Tailscale Tagging**: Run `sudo tailscale set --tag=tag:node1` (permanently drops legacy `tag:asus`).
  3. **OpenCode Configuration**: Update `~/.config/opencode/opencode.json` so `omega-hub` points to `http://n0.tail51f14a.ts.net:8016/mcp`.
  4. **OpenCode Cache Purge**: Restart OpenCode client on Node 1 to flush phantom tool cache (`oracle_list_pillar_keepers`).
  5. **NFS Activation**: Start `nfs-kernel-server` on Node 1 exporting `/mnt/node-drive/exchange`.
* **Stage 4 Verification Gate**:
  - Node 0 can SSH into Node 1 via `ssh arcana-novai@100.89.40.17`.
  - Node 0 successfully mounts Node 1's NFS export at `/mnt/node-drive/exchange-n1`.
  - `omega_federation_status` reports `n1` has tags `["tag:node1"]` only.

---

## 🏛️ STAGE 5: FIRST DECOUPLED SOTE INAUGURATION

### 5.1 Objective
Execute the inaugural run of the decoupled SOTE/SOTR architecture. Kali convenes the Triad and Slot Keepers to synthesize the true, multifaceted state of the engine.

### 5.2 Execution Instructions
* **Action**: MaKaLi prompts Kali to lead the SOTE synthesis.
* **Workflow**:
  1. Kali dispatches Ma'at (Build S1–S5) and Lilith (Runtime S6–S10).
  2. Slot keepers submit domain digests.
  3. Kali executes dialectic synthesis and writes `data/coordination/SOTE_LATEST.md`.
  4. Kali hand-delivers `SOTE_LATEST.md` to MaKaLi.
  5. MaKaLi ingests the SOTE, audits the dual-node substrate, and writes the master `data/coordination/STATE_OF_THE_REALM.md`.
* **Stage 5 Verification Gate**:
  - `data/coordination/SOTE_LATEST.md` exists and carries signed attribution from Kali, Ma'at, and Lilith.
  - SOTR cockpit displays live, verified data across both Node 0 and Node 1.
  - Sovereignty ratio tracking reflects active local inference.

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ MASTER-EXECUTION-PLAN ⬡ 2026-09-23 ⬡ RATIFIED*
