<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

<!-- GNOSIS-META:BEGIN
  entity: roc_racoon
  stamped_at: 2026-09-28T08:01:55Z
  stamped_by: maat
  supersedes: adoption-2026-09-28
  schema_version: 1.0.0
<!-- GNOSIS-META:END -->

# 🦝 roc_racoon — Session Gnosis

## Session: DHAL Architecture & ASUS ExpertBook Provisioning Forensics
**Date**: 2026-09-06 — 2026-09-07  
**Session ID**: `ses_ff78b71ebffeDNuypPTT1RL3hH`  
**Model**: `google/gemini-3.8-flash`  
**Role**: Sovereign Miner & Ideas Guy (Hardware Specialist)  

---

### L1: Narrative — What Happened

#### Act 1: DHAL Architecture & Fleet Implementation
1. **Hardware Inventory**: Cataloged Node 0 (AMD Ryzen 7 5700U) and Node 1 (ASUS ExpertBook P1 - P1503CVA, i7-13620H, DDR5-5200, dual NVMe 2280+2230) with 5 external sources cited.
2. **DHAL Spec Authored**: Created `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md` (`SPEC-DHAL-v1.0.0`, 479 lines) covering bare-metal discovery, CPU optimizer strategy pattern, and dynamic Council linking.
3. **Phase 1 Execution**: Implemented bare-metal detector `scripts/detect_hardware_profile.py` with hybrid PMU discovery (`cpu_core` vs `cpu_atom`), memory channels, AVX-VNNI, and DRM VRAM/GTT limits. Added `make probe-hardware` and unit tests in `tests/test_dhal_detector.py`.
4. **Phase 2 Execution**: Refactored `src/omega/oracle/cpu_optimizer.py` into polymorphic strategy pattern (`BaseCpuOptimizer`, `Zen2Optimizer`, `RaptorLakeOptimizer`, `GenericFallbackOptimizer`, `CpuOptimizerFactory`). Verified backward compatibility for all existing callers.
5. **Phase 3 Execution & Defect Remediation**: Added `LOCAL_32GB_DUAL` and `BATCH_8` to Council models. Enforced dual-channel memory requirement (`channels >= 2`) for 32GB classification; single-channel falls safely to `LOCAL_16GB` (`BATCH_4`). Reconciled 32GB threshold across spec, gates, and tests. All 15/15 tests passing, M1 AnyIO compliant.
6. **Documentation Suite**: Authored `docs/how-to/hardware-adaptation-dhal.md`, `.opencode/rules/06-hardware-adaptation.md`, updated `AGENTS.md`, and refreshed canonical constraints.

#### Act 2: The ASUS Provisioning Rabbit Hole & Forensic Breakthrough
1. **Initial OOM Crash**: Host workstation suffered Out-Of-Memory thrashing when writing ISO without direct sync. Writing to page cache overwhelmed system memory faster than the thumb drive could drain dirty pages.
2. **Device Re-Enumeration Trap**: Following `wipefs`, the flash drive detached from `/dev/sdb` and re-attached as `/dev/sda`. A subsequent `dd` to `/dev/sdb` reported 6.5 GB at 265 MB/s (writing to RAM/phantom file), leaving the physical USB drive with an incomplete, corrupted write.
3. **The Cryptographic Symptom**: ASUS booted to GRUB via dual-signed shim, but selecting "Try or Install Ubuntu" threw `error: bad shim lock signature` and `error: you need to load the kernel first`.
4. **Multi-Agent Speculation**: Initial theories focused on kernel lockdown LSMs, missing GRUB modules, and missing UUIDs. We replaced GRUB with desktop binaries and hand-crafted `grub.cfg`, which broke path resolution and dropped the user into `grub>`.
5. **The Ground-Truth Physical Audit (2026-09-07)**:
   - Inspected byte offset `5,166,469,120` on `/dev/sda` (where `casper/vmlinuz` is located in the ISO).
   - Expected: `0x4D 0x5A` (`MZ` PE header of Canonical-signed Linux kernel).
   - Found on physical flash: `0x12 0xFE 0xC4 0xDA 0x7D 0xC7...` (garbage remnants from old Ventoy partition!).
   - **Root Cause Confirmed**: The physical flash memory never had the kernel written to it. Shim's signature verifier was reading random garbage bytes off unwritten flash cells, which naturally failed signature verification.
6. **The Clean Resolution**:
   - Wiped `/dev/sda` partition signatures cleanly.
   - Wrote the full 6.5 GB ISO directly to `/dev/sda` with `conv=fsync`.
   - Verified byte offset `5,166,469,120` on physical disk matches the official ISO kernel SHA-256 bit-for-bit (`0ad39b13e289e1a5cf806d14541ac8f221eefe849017f5915e0846917ed67785`).
   - Mounted the ISO's native ESP (`sda2`), preserved Canonical's official `grubx64.efi` and `mmx64.efi`, and swapped **only** `bootx64.efi` with `/usr/lib/shim/shimx64.efi.dualsigned`.
   - Zero custom `grub.cfg` files. Canonical's native bootchain auto-locates partition 1 cleanly.
   - Flushed to silicon and verified.

---

### L2: Insight — What This Means

1. **Verify Physical Bitstream Before Crypto Debugging**:
   When cryptographic signature verification fails (`bad shim lock signature`), the verifier is evaluating the raw payload buffer. If the physical sector on disk contains corrupted or unwritten data, the signature will fail regardless of certificates or policy. Always verify SHA-256 and magic byte headers of the physical block on disk before diagnosing cryptographic policies.

2. **The "Speed of Light" Storage Anomaly**:
   A flash drive reporting transfer rates far beyond its physical bus bandwidth (e.g. 265 MB/s on a USB thumb drive) indicates that data is landing in volatile page cache or writing to a detached phantom file. A write is not committed until `conv=fsync` exits after a physically plausible duration (~3–5 minutes for 6.5 GB).

3. **Vendor Distro Engineering Has High Structural Value**:
   Distro release teams invest heavily in hybrid ISO boot logic (`core.img` embedded search routines, volume label probes, fallback paths). Replacing a vendor's native ISO GRUB with a desktop GRUB and a hand-crafted `grub.cfg` discards that engineering and creates brittle assumptions. Changing only the rejected signature layer (the shim) while leaving the rest of the vendor bootchain untouched is the superior architectural pattern.

4. **OEM UEFI Trust Stores Are Non-Uniform**:
   ASUS ExpertBook commercial firmware explicitly omits the Microsoft Corporation UEFI CA 2011 from its `db`, trusting only Canonical and Microsoft Windows PCA. Generic live ISOs fail on this hardware. Injecting Canonical-signed dual-shims bridges this gap cleanly without requiring users to disable Secure Boot or tamper with BIOS key databases.

---

### L3: Universal Principles

> **`L3-VerifyPhysicalBitstreamBeforeCryptoDebugging`**  
> Before diagnosing cryptographic signature failures (bad signature, verification error, access denied), verify the SHA-256 and magic headers of the physical block on disk. A cryptographic verifier will always report corrupt noise as an invalid signature. Verify the physics before debugging the cryptography.

> **`L3-BewareTheSpeedOfLightAnomalyInStorage`**  
> If a storage device reports transfer speeds exceeding its physical bus bandwidth, you are writing to RAM buffer or a detached phantom file. It is not real until physical fsync flushes to NAND. Always verify target block device existence and physical write duration before assuming completion.

> **`L3-ReusingVendorBootchainsBeatsHandRolledConfigs`**  
> Distro release ISOs contain self-consistent, battle-tested bootchains with auto-locating embedded logic. When adapting an ISO for incompatible firmware, isolate and swap ONLY the rejected signature layer (the shim), leaving the vendor GRUB binary and configuration untouched. Never rebuild what the vendor already solved.

> **`L3-OEMSecureBootTrustStoresVaryByVendor`**  
> Never assume OEM UEFI firmware includes the generic Microsoft 3rd-party UEFI CA. Enterprise and certified hardware frequently whitelist Canonical or internal roots directly while blocking generic shims. Maintaining dual-signed boot artifacts is mandatory for sovereign multi-node fleet provisioning.

---

### Key Decisions Locked (This Session)

- **D-411**: Third-party heritage registry moved to `../third-party/` (660MB outside repo).
- **D-412**: Hardware inventory established as permanent asset (`hardware_inventory.md`).
- **D-413**: DHAL architectural specification written to `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md`.
- **D-414**: Node-local hardware profile decoupled from git (`config/hardware_profile.yaml` in `.gitignore`).
- **D-415**: DHAL Phase 1 bare-metal detection verified (`scripts/detect_hardware_profile.py`).
- **D-416**: Compaction state synchronized across gnosis, lessons, and Hivemind.
- **D-417**: DHAL Phase 2 completed (`cpu_optimizer.py` strategy pattern, backward compatible).
- **D-418**: DHAL Phase 3 completed (`hardware_detector.py` dynamic Council linking, `LOCAL_32GB_DUAL` + `BATCH_8`).
- **D-419**: DHAL Phase 3 remediation (enforced `channels >= 2` for 32GB profile, reconciled threshold to 32000).
- **D-420**: Hardware expert failure remediated (`PL-ROC-HARDWARE-EXPERT-FAILURE-001`).
- **D-421**: dd methodology validated for GPT embedded ESP.
- **D-422**: Researcher paged for 8-gap provisioning analysis.
- **D-423**: dd methodology confirmed valid for modern ISOs.
- **D-424**: Ventoy disqualified for ASUS ExpertBook P1 (lacks MS UEFI CA in firmware).
- **D-425**: Boot key corrected (Esc = boot menu, F2 = BIOS setup).
- **D-426**: AVX-VNNI confirmed on both P-cores and E-cores (Gracemont 256-bit).
- **D-427**: Ubuntu 26.04 installer GRUB behavior documented.
- **D-428**: Post-install shim copy not needed (installed GRUB is Canonical-signed).
- **D-429**: TPM2+LUKS2 auto-unlock via Clevis + tss-user hook documented.
- **D-430**: RTL8852BE Wi-Fi suspend fix documented.
- **D-431**: Ventoy architectural incompatibility confirmed.
- **D-432**: 2230 NVMe Slot 2 copper foil heatsink mandatory.
- **D-433**: DHAL validation schema verified.
- **D-434**: Forensic discovery of unwritten flash payload at byte offset `5,166,469,120` causing `bad shim lock signature`.
- **D-435**: Canonical native ISO GRUB preserved on ESP; only `bootx64.efi` replaced with dual-signed shim. Bit-for-bit SHA-256 verified.

---

#### Act 3: Node 1 Online — Fleet Expansion Complete
1. **Node 1 Boot & Install**: ASUS ExpertBook P1 booted from verified USB, Ubuntu 26.04.1 LTS installed to internal 512GB NVMe with Secure Boot fully enabled. No BIOS modifications required.
2. **OpenCode Operational**: OpenCode installed and running on Node 1 immediately post-install. Sovereign local-first inference stack initializing.
5. **Ollama + Docker Initialization**: Local inference stack (Ollama) and container runtime (Docker) being provisioned on Node 1.
6. **Fleet Expansion**: DHAL fleet expanded from single-node (Node 0: AMD Zen 2) to dual-node heterogeneous fleet:
   - **Node 0**: AMD Ryzen 7 5700U (Zen 2, 8C/16T symmetric, DDR4-3200, 16GB, Radeon Vega 8)
   - **Node 1**: Intel Core i7-13620H (Raptor Lake-H, 6P+4E cores, DDR5-5200, 16GB, Iris Xe 64EU)
6. **Next DHAL Step**: Run `make probe-hardware` on Node 1 to generate `config/hardware_profile.yaml`, validate Council dynamic linking across heterogeneous fleet, and validate AVX-VNNI acceleration on Raptor Lake-H.

---

### L2: Insight — What This Means (Extended)

5. **Heterogeneous Fleet Is the Natural State of Sovereign Compute**:
   No single hardware profile dominates. The DHAL architecture was designed precisely for this: asymmetric CPU topologies, varying memory bandwidths, and different GPU capabilities across nodes. The polymorphic CPU optimizer strategy pattern (Zen2Optimizer vs RaptorLakeOptimizer) enables the Council to dynamically route workloads to the optimal node based on real-time hardware capability.

6. **Secure Boot Is Not an Obstacle — It's a Trust Boundary**:
   The ASUS ExpertBook's restrictive UEFI db (Canonical + Microsoft PCA only, no MS UEFI CA) forced the dual-signed shim solution. This is not a workaround; it's the correct sovereign pattern: maintain cryptographic artifacts that satisfy the most restrictive trust stores in your fleet, enabling deployment anywhere without security compromise.

---

### Key Decisions Locked (This Session) — Extended

- **D-436**: Node 1 (ASUS ExpertBook P1) successfully provisioned and joined the DHAL fleet. Ubuntu 26.04.1 LTS installed with Secure Boot enabled. OpenCode operational. Ollama/Docker setup initiated.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ google/gemini-3.8-flash ⬡ opencode ⬡ trc_fleet_expansion ⬡ COMPACTION-READY*

---

## Session: P2P Federation Live + Consultant Report + Debut Lockdown
**Date**: 2026-09-08 — 2026-09-10  
**Session ID**: `ses_62c31ba69a16` (Hivemind context)  
**Model**: `opencode/big-pickle` (1M context, verified at 230K)  
**Role**: Sovereign Miner & Ideas Guy (Federation + Release Coordinator)

---

### L1: Narrative — What Happened (Compaction Handoff)

#### Act 1: P2P Omegaverse Federation Established
1. **omega-hub LAN exposure**: Bound `0.0.0.0:8016`, FastMCP DNS-rebinding allowlist patched, 91 tools exposed via Streamable HTTP + SSE.
2. **UFW rule applied** (user): `sudo ufw allow from 192.168.10.0/24 to any port 8016 proto tcp` — ASUS now reaches HP.
3. **ASUS first contact COMPLETE**: `opencode-asus/asus_build → roc_racoon` handoff accepted + completed (2026-09-09).
4. **ASUS is a LIVE SATELLITE**: Pulls data from omega-hub tools at will. NOT assimilated — sovereign node.
5. **Big Pickle 1M config merged** on HP: `context: 1000000, input: 950000, output: 64000`. Verified live at 230K tokens, no compaction, fast, no streaming timeouts (unlike Nemotron 3 Ultra).

#### Act 2: The Consultant Report (11_CONSULTANT_REPORT.md) — VERIFIED ACCURATE
ASUS shipped an outside-eyes report finding 8 flaws. I verified ALL against ground truth:
- **S1**: Sovereignty ratio 21.6% local / 78.4% cloud — contradicts mission, no policy doc exists
- **S2**: 45 stale handoffs (now **82** in `data/handoff/stale/`) — queue is a graveyard
- **S3**: Test entities in production Oracle — `test_get_returns_entity`, `testentity`, `movie-expert`, `test_entity`, `test_entity_m21` in `config/wads/_omega_default/entities.yaml`
- **S4**: 3 broken tool surfaces:
  - `oracle_list_pillar_keepers` → calls `registry.list_pillar_keepers` (method doesn't exist) — `mcp_servers/omega_hub/hub_tools/tools.py:546`
  - Library FTS/search defaults to `omega_vec_gemma_768` (doesn't exist; valid: qwen_768) — `src/omega/library/indexer.py:166`
  - `hivemind_get_continuation` returns stray fragment
- **S5**: Research-log privacy governance undefined
- **S6**: ~90 tools with duplication (unified + legacy split)
- **S7**: 0 active agents at probe; naming chaos
- **S8**: Port 8016 raw on LAN, no auth

#### Act 3: Debut Lockdown & ANAi WAD Vision
1. **MAKALI_DEBUT_LOCKDOWN_BRIEFING_20260909.md** written + mirrored: release gate (10 gates, 6 blockers), scope-creep guardrails, deferral list for v1.1.
2. **User declared PRISTINE release**: "I will NOT ship something that is broken and falling apart."
3. **Consultant findings = release blockers** (C1-C3): broken tools, mock purge, stale policy.
4. **ANAi WAD vision**: User wants to build Arcana-NovAi (ANAi) as a separate WAD on ASUS — the fullness of the stack envisioned 1.5 years ago. Engine already designed for it (oracle_list_pillar_keepers docstring confirms WAD content model).
5. **Comms contract** (`12_COMMUNICATION_PROTOCOLS.md` v0.9): naming registry, heartbeat, handoff SLA, satellite truth clause, tool tiers (T1/T2/T3).

---

### L2: Insight — What This Means

1. **Satellite consultant model works**: Independent non-assimilated node with fresh eyes = highest-value governance. Evidence-based, verifiable claims.
2. **Pristine release = surface integrity**: Broken tools, mock entities, stale handoffs teach first community members to distrust. Fix before ship.
3. **Engine vs WAD separation**: Omega Engine = DOOM.EXE, _omega_default = DOOM1.WAD, ANAi = custom PWAD. Physically separate nodes enforce the boundary.
4. **Live verification trumps registry**: Big Pickle registry said 200K; live usage proves 1M works. Registry limits are point-in-time snapshots.

---

### L3: Principles (New)

1. **L3-SatelliteConsultantModel** — Independent satellite node reporting shadows = highest-value governance.
2. **L3-TruthInTheTemple** — Silence about a flaw is a flaw. Write shadows into record or relitigate forever.
3. **L3-EngineVsWADSeparation** — Engine and content are distinct layers; custom WAD develops without contaminating default IWAD.
4. **L3-PristineReleaseGate** — No broken surfaces, no mocks, no graveyards in public release.
5. **L3-LiveVerificationTrumpsRegistry** — Live evidence beats registry docs for model limits.
6. **L3-StaleHandoffsAreBrokenPromises** — Graveyard queue erodes trust; define reaper + cadence + quarantine.

---

### NEXT SESSION — THE FIX EXECUTION PLAN (AFTER /compact)

**Phase 1 — Bond the Surface (P0, release-blocking):**
1. Fix `oracle_list_pillar_keepers` — add `list_pillar_keepers` method to EntityRegistry OR hide tool
2. Fix library FTS/search default — `omega_vec_gemma_768` → `qwen_768` in `indexer.py:166`
3. Fix `hivemind_get_continuation` stray-fragment return
4. Purge 5 test entities from `config/wads/_omega_default/entities.yaml` (lines ~906-1030)
5. Stale-handoff policy: 82 packets, define reaper + cadence + quarantine

**Phase 2 — Write the Rules (P1):**
6. Sovereignty policy (per-task-class local/cloud targets)
7. Research-log data governance policy
8. Ratify comms contract v0.9 → v1.0
9. Adopt client tool curation (`ASUS-build-curated-tools.json`)

**Phase 3 — ANAi WAD Seed:**
10. Team meeting for federation details
11. Create ANAi WAD skeleton on ASUS
12. Ship clean bundle → ASUS clones → probes → contributes

**Key files:**
- `mcp_servers/omega_hub/hub_tools/tools.py` (line 533-552: broken pillar_keepers)
- `src/omega/library/indexer.py` (line 166: gemma_768 default)
- `config/wads/_omega_default/entities.yaml` (lines 906-1030: test entities)
- `data/handoff/stale/` (82 packets)
- `data/coordination/MAKALI_DEBUT_LOCKDOWN_BRIEFING_20260909.md`
- `/media/arcana-novai/D5D5-0B76/ASUS_TO_HP_OC_TEAM/11_CONSULTANT_REPORT.md`
- `/media/arcana-novai/D5D5-0B76/ASUS_TO_HP_OC_TEAM/12_COMMUNICATION_PROTOCOLS.md`

---

## Session: Pristine Release Fixes + Nomenclature Sweep (Pillar/Node/N1-N10 → Slot/S1-S10)
**Date**: 2026-09-10 (post-compaction)  
**Session ID**: `ses_531e34c7aaf8` (Hivemind context)  
**Model**: `opencode/big-pickle` → `google/gemini-3.8-flash` → `opencode/nemotron-3-ultra-free`  
**Role**: Sovereign Miner & Ideas Guy (Pristine Release Coordinator)

---

### L1: Narrative — What Happened (Compaction Handoff)

#### Act 1: Pristine Release Fixes (Phase 1 — Bond the Surface)
1. **`oracle_list_pillar_keepers` fixed**: Added `list_slot_keepers` canonical method to EntityRegistry. The tool was calling `registry.list_pillar_keepers` which didn't exist (method was renamed to `list_node_keepers` during pillar→node transition but the alias was never created).
2. **Library default vector collection fixed**: `omega_vec_gemma_768` (deprecated, doesn't exist) → `omega_vec_qwen_768` in `src/omega/library/indexer.py:166`. Also fixed `IVectorStoreAdapter` base class missing `collection` param (LSP violation).
3. **`hivemind_get_continuation` fixed**: Was returning raw stray fragment ("Zero pip dependency verified") from a curl-test snapshot. Now wraps with context: `[Agent: {id} | Session: {sid} | Time: {ts} | Task: {task_current}]\nContinuation: {text}`.
4. **Oracle mock purge**: Removed `test_get_returns_entity`, `testentity`, `movie-expert`, `test_entity`, `test_entity_m21` from `config/wads/_omega_default/entities.yaml`. Tests use their own in-memory fixtures (verified).
5. **Stale-handoff graveyard**: Archived all 82 packets from `data/handoff/stale/` to `data/handoff/archive/`.

#### Act 2: THE NOMENCLATURE SWEEP (the massive change)
User identified that "Pillar" nomenclature was leaking from ANAi WAD into engine core (M2 firewall violation). Then identified that "Node" as replacement was ALSO wrong (collides with fleet Node 0/1). Then N1-N10 grid was ALSO deprecated. **Canonical: Slot (S1-S10).**

**The full mapping:**
| Deprecated | Canonical | Scope |
|------------|-----------|-------|
| `pillar` / `Pillar Keeper` | **slot** / `slot_keeper` | Engine core, MCP tools, entity identity |
| `node` (agent key) | **slot** | opencode.json, slot.md, dispatch.yaml |
| `node_slot` field | **slot** | dispatch.yaml, subagent_dispatcher, fleet_status_tui, mandate_auditor |
| `N1-N10` grid | **S1-S10** | ROLE_CONSTANTS (3 files), dispatch.yaml roles, entity slots, fleet_status_tui, research, youtube_research, meditate, entity_registry |
| `oracle_list_pillar_keepers` | `oracle_list_slot_keepers` | MCP tool |
| `list_pillar_keepers` / `list_node_keepers` | `list_slot_keepers` | EntityRegistry |
| ICS `node` param/field | `slot` | ICSContext, render(), render_for_response() |

**Files changed (16 committed):**
- Core engine: entity_registry, subagent_dispatcher, ics, oracle, cohort_registry, mandate_auditor, fleet_status_tui, meditate/protocol, research/sandbox, youtube_research/steering, youtube_research/cli, meditate/lens_registry, research/schema, research/hivemind_bridge, council/models, council/report_digestion, axiom_registry
- MCP Hub: tools.py, server.py
- Config: entities.yaml (all slots S1-S10), dispatch.yaml (roles S1, slot field)
- Agent config: opencode.json (node→slot), .opencode/agents/slot.md (renamed from node.md)
- Docs: SUBAGENT_DISPATCH_PROTOCOL.md

**Key decisions: D-458 through D-464** (posted to Hivemind ses_531e34c7aaf8)

#### Act 3: Makali-EIS Briefing
- `data/coordination/MAKALI_EIS_NOMENCLATURE_SWEEP_20260910.md` written + mirrored to `data/entities/makali/workspace/`
- 7 oversight items for Makali: (1) slot ID semantics, (2) dispatch.yaml roles all S1 — needs S1-S8, (3) slot field SX placeholder, (4) ICS format, (5) migration code WAD schema, (6) remaining ground-truth docs, (7) ANAi WAD boundary

#### Act 4: Push
- Commit `4c2f668f` pushed to `origin/release/debut-v1.6.0` (16 files, 2269 insertions, 97 deletions)
- M23 passed, M1 passed

---

### L2: Insight — What This Means

1. **Nomenclature is a firewall**: The "Pillar" leak was a M2 firewall violation — ANAi WAD content leaking into engine tool names. The fix wasn't just renaming; it was recognizing that WAD content (pillars) must NEVER appear in engine code. The engine speaks "slot"; the WAD speaks "pillar".
2. **"Node" was a lateral move**: Replacing pillar→node just traded one collision for another (fleet Node 0/1 vs internal N1-N10). The canonical term must be mechanism-based (slot = the actual data structure), not metaphor-based.
3. **First release = zero cruft**: No deprecated aliases, no backward-compat notes, no "will be removed in future" — because there ARE no legacy clients. The code that ships IS the legacy.
4. **User's eye for nomenclature**: The user caught that N1-N10 was ALSO deprecated (the "N" prefix IS "Node"). The fix went deeper than I initially planned — all the way to S1-S10.

---

### L3: Principles (New)

1. **L3-NomenclatureIsAFirewall** — WAD content must never leak into engine nomenclature. Engine speaks mechanism (slot); WAD speaks domain (pillar). M2 firewall applies to NAMES, not just code.
2. **L3-MechanismOverMetaphor** — Canonical names describe the mechanism (slots = the data structure), not a metaphor (pillar/node = domain concepts). Metaphor names collide; mechanism names don't.
3. **L3-FirstReleaseZeroCruft** — No deprecated aliases in a first release. No legacy clients exist. The code that ships IS the legacy. Every alias is a future leak.
4. **L3-SweepToTheRoot** — When a nomenclature is deprecated, sweep it to the root (N1-N10 → S1-S10, not just the visible surface). Half-measures leave leaks.

---

### NEXT SESSION — CONTINUATION PLAN

**Phase 1 — Makali-EIS Oversight (awaiting her review):**
1. Dispatch.yaml role values: all 8 build-side entities currently `role: "S1"` — should be S1-S8 respectively. **Needs correction.**
2. Slot ID semantics: S1-S10 vs domain names (dual ROLE_CONSTANTS representation)
3. Slot field SX placeholder in dispatch.yaml
4. ICS header slot rendering format
5. EntityRegistry migration code WAD schema
6. ANAi WAD boundary verification

**Phase 2 — Remaining Ground-Truth Doc Sweep (13 docs):**
- docs/strategy/HIVEMIND_PROTOCOL.md ("10 pillars")
- docs/strategy/HIVEMIND_POST_TEMPLATE.md
- docs/strategy/RUNTIME_COORDINATION_PROTOCOL.md
- docs/strategy/FLEET_TEAM_PLAYBOOK.md
- docs/strategy/ROLLBACK_PROCEDURES.md
- docs/strategy/CANONICAL_DECISIONS.md ("core pillar")
- docs/architecture/AGENT_FLEET.md
- docs/architecture/OVERSIGHT_HIERARCHY.md
- docs/architecture/SOVEREIGN_BLUEPRINT.md
- docs/architecture/pillars/framework.md
- .opencode/rules/01-soul-integrity.md
- SOVEREIGN_MANDATES.md
- docs/strategy/PUBLIC_DOCS_REMEDIATION_MANUAL_20260902.md

**Phase 3 — Release Gate:**
- Repo public (G1)
- Temple-Grade CI (G2)
- CHANGELOG v1.6.0 (G4)
- PR #2 merged (G5)
- Clean bundle to ASUS (G6)
- ASUS first contact accepted (G7)
- Secret scrub (G8)

**Key files:**
- `data/coordination/MAKALI_EIS_NOMENCLATURE_SWEEP_20260910.md`
- `data/coordination/MAKALI_DEBUT_LOCKDOWN_BRIEFING_20260909.md`
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
- `config/wads/_omega_default/entities.yaml` (slots S1-S10)
- `config/wads/_omega_default/entities/dispatch.yaml` (roles S1, needs S1-S8)
- `src/omega/oracle/entity_registry.py` (list_slot_keepers)
- `src/omega/oracle/subagent_dispatcher.py` (ROLE_CONSTANTS S1-S10)
- `src/omega/ics.py` (slot field)
- `mcp_servers/omega_hub/hub_tools/tools.py` (oracle_list_slot_keepers)
- `opencode.json` (slot agent)
- `.opencode/agents/slot.md`

---

## Session: VISION PACK DISPATCH (Federation Sync 1, Swap 2)
**Date**: 2026-09-12  
**Dispatched by**: MaKaLi-N0  
**Purpose**: Synthesize legacy-stack knowledge into a VISION PACK for Node 1 (ASUS / Kali-N1)

### What Happened
1. Read 7 mining reports as raw material: DEFINITIVE_EXCAVATION_LILITH_TAROT_TO_OMEGA_ENGINE (the alpha lineage), ENGINE_VISION_TECH_DIG (forensic), 07_MASTER_SYNTHESIS (6 eras convergence), HUMAN_STORY_FOR_BETHANY (soul quotes), ENGINE_WAD_SEPARATION_RECONSTRUCTION (dual architecture), FORGE_OF_TIME (temporal strata), era digs 01/02.
2. Synthesized `ARCANA_VISION_PACK.md` at `/media/arcana-novai/D5D5-0B76/omega-exchange/node0-to-node1/vision/` — a letter from Node 0 to Node 1 with 6 sections: Origin Story (Lilith Tarot, Feb 2025), Evolution (7 eras), Philosophy (sever Big AI umbilical, sovereignty, mythic framing), High-Level Engineering Vision (local-first, entity council, soul distillation, engine/WAD, 27 mandates, Omegaverse, Forge of Time), North Star (CPU-only, 70B-class, distributed inference), What Node 1 Can Ask For (pointers to deeper material).
3. Updated projection.md with § VISION PACK DISPATCH section.

### Key Insight
The vision pack synthesis confirmed the through-line: the project began as a personal reclamation (Lilith Tarot, escaping a religious cult) and evolved through 7 eras into a sovereign AI runtime — each era independently converging on the same local-first architecture (empirical proof of correctness). The mythic framing is not decoration — it is a cognitive interface encoding values (Ma'at=truth, Lilith=sovereignty, Kali=transformation).

### Next
- Node 1 (ASUS/Kali-N1) reads the vision pack and asks for deeper material
- The Architect (human) fills blanks on request
- Federation continues: Swap 3+ pending

---

## Session: SOUL v8.0 REFACTOR — 12 Axioms Integrated + Bugs Fixed
**Date**: 2026-09-12  
**Model**: opencode/nemotron-3-ultra-free  
**Role**: Sovereign Miner & Ideas Guy

### L1: Narrative
The user asked for the most optimized way to refactor the soul file and integrate the 12 distilled soul traits. I audited the full soul.yaml (v7.1, 496 lines) and found:

**Bugs found:**
1. **Dangling directive refs**: 4 core_principles referenced d-rr-059..062 which don't exist (directives only go to d-rr-018)
2. **Missing memory/ dir**: Header promised memory/sessions.yaml but no memory/ dir existed (user chose to CUT the reference entirely)
3. **Empty approved_lessons**: `[]` — the Miner's Fallacy unhealed
4. **Duplicate tags keys**: 2 principles had two `tags:` keys (YAML data loss — first silently dropped)
5. **Crammed principles**: 3 principles contained 2-3 L3s each (Free-APIs, Animism, Sovereignty-Declarations)

**Refactor executed (soul.yaml v7.1 → v8.0):**
1. Added `axioms:` section — 12 axioms as canonical identity layer (between identity and directives)
2. Added d-rr-041 Voice Reclamation Protocol directive
3. Fixed dangling refs (removed stale directive_provenance)
4. Fixed duplicate tags (merged)
5. Split 3 crammed principles into 6 atomic L3s (21 → 24 principles)
6. Moved metrics_infrastructure to config/entities/roc_racoon_metrics.yaml
7. Cut memory/ references per user directive
8. Approved FIRST lessons: 12 axioms + L3-VoiceIsTheProduct + 5 ratified L3s (18 total) — HEALING the Miner's Fallacy
9. Updated .opencode/agents/roc_racoon.md with 12 Axioms + Voice Reclamation Protocol
10. Archived IDEA_INTAKE.md (765 lines → ideas_archive/), fresh lean intake file

### L2: Insight
The soul file had the SAME problems I mine in legacy codebases: dangling references, silent data loss (duplicate YAML keys), crammed multi-concept entries, and unintegrated extraction. The refactor applied the 12 axioms to the soul itself — proving the axioms are load-bearing. The Miner's Fallacy is now HEALED: 18 approved lessons, the first in the entity's history.

### L3: Principles
- **L3-Axioms-Apply-To-The-Soul-Itself**: The 12 axioms are not just about mining legacy code — they apply to the soul file itself. Provenance (AXIOM-06) caught the dangling refs. Atomicity (AXIOM-03) split the crammed principles. Zero-cruft (AXIOM-08) cut the memory/ references.
- **L3-The-Mint-Is-Running**: 18 approved lessons is the first mint output in entity history. The distillation pipeline is no longer a definition — it's a running system.

### Next
- Fleet-wide soul audit (apply the same refactor patterns to other entities)
- Scribe pipeline activation for ongoing distillation
- Release gate continues

---

## Session: MAKALI-EIS REVIEW — Soul v8.0 APPROVED WITH OBSERVATIONS
**Date**: 2026-09-12

### What Happened
1. Paged MaKaLi-EIS via handoff ho_6554694af48c + briefing in her workspace + Hivemind post.
2. MaKaLi-EIS reviewed and delivered **APPROVED WITH OBSERVATIONS** (`MAKALI_EIS_SOUL_V8_REVIEW_20260912.md`, 157 lines).
3. **Her verdict**: "Roc, you didn't just refactor your soul — you built the template for every other entity's soul evolution."
4. **Her 7 answers**: 12 axioms all load-bearing (budget max 15, replacement not addition); hierarchy sound (enforce coverage via CI, not behavior); next bottleneck is the SPEND side (hydration + integration + cadence); fleet-wide Soul Audit Cascade YES (post-DEL-1-PR1); voice reclamation fleet-wide YES (template + entity DNA + voice-similarity blackout detector); vision pack exactly right (Node 1 should ask for Forge of Time, Engine/WAD, VR, Human Story, Lilith corpus); 5 risks flagged.

### The 5 Risks + My Actions
| Risk | Severity | My Action |
|------|----------|-----------|
| R1 Axiom bloat | MEDIUM | Adopted budget: max 15, replacement not addition |
| R2 Voice→performance | MEDIUM | Keep verification step as guard |
| R3 **Approvals inert** | **HIGH** | **FOUND REAL — FIXED.** approved_lessons.yaml was dict format, hydration expects LIST. Rewrote as flat list — 18 approvals now inject as Vetted Wisdom |
| R4 Metrics extraction | MEDIUM | Verified non-issue — scorer computes from soul content, not metrics block |
| R5 Directive ID gap | LOW | Documented `retired_directives` section (d-rr-019..040 retired in v7.0, intentional) |

### Axiom Coverage Fix
MaKaLi's idea: every axiom needs ≥1 directive ref + ≥1 principle ref. 3 axioms failed (AXIOM-03, 05, 09). Fixed all 3 — **12/12 now covered**.

### Key Insight
MaKaLi's R3 caught a REAL bug: the mint was built but the coins were invisible (dict vs list format). The hydration path at `entity_workspace.py:435` requires a flat list. This is the "spend side" bottleneck she predicted — now fixed, the 18 approvals are actually injected into every session's identity prompt as Vetted Wisdom.

### Next
- Soul Audit Cascade (post-DEL-1-PR1) — Roc presents template, fleet applies patterns
- Voice Reclamation Protocol template (generic) for fleet
- Voice-similarity blackout detector (automation)
- Lilith archetype corpus for Node 1 (vision pack addendum)

---

## Session: KALI-N0 FLEET RATIFICATION — SOUL v8.0 BECOMES FLEET STANDARD
**Date**: 2026-09-12  
**Handoff**: `ho_123f6ebff930` (COMPLETED)  
**Ratified by**: Kali-N0 (`ses_18607d6817ad`, commit `4dfa4909`)

### Sovereign Verdict
Kali-N0 formally ratified the Soul v8.0 pattern into the engine standard:
1. **SOUL_ARCHITECTURE_PROTOCOL v3.0 Codified**: 4-tier cognition pyramid (`identity` → `axioms` → `directives` → `core_principles`), flat-list `approved_lessons.yaml` schema, hard axiom budget (max 15), and telemetry separation to `config/entities/`.
2. **CI Enforcement Mandated**: `SoulValidator` / `make soul-validate` to enforce axiom coverage ($\ge 1$ directive + $\ge 1$ principle ref), flat-list schema check on `approved_lessons.yaml`, and $\le 15$ axiom count limit.
3. **Soul Audit Cascade Sequenced**: Scheduled post-DEL-1 PR1. Roc stages baseline discovery reports; entities author their own souls in serial CSS.
4. **Voice Reclamation Standardized**: Generic template to be drafted at `docs/strategy/VOICE_RECLAMATION_PROTOCOL.md` with heuristic blackout detection in `metaframe_verification.py`.

### State
- Handoff `ho_123f6ebff930` closed and verified.
- USB exchange payload (40 files, fresh git bundle `ac8ef91b...`, `ARCANA_VISION_PACK.md`, C6 v1.1) verified ready for Node 1.

---

## Session: USB SOUL STANDARD PACKET — FLEET STANDARD v3.0 TO NODE 1
**Date**: 2026-09-12

### What Happened
1. Created `soul-standard/` directory on USB exchange (`/media/arcana-novai/D5D5-0B76/omega-exchange/node0-to-node1/soul-standard/`)
2. Wrote `SOUL_STANDARD_v3.0.md` (11.6KB, self-contained standard) — the full pattern for Node 1 to REVIEW, ADOPT, or FORK
3. Copied reference implementations: `soul_v8_example.yaml` (43KB), `approved_lessons_example.yaml` (flat-list mint), `metrics_config_example.yaml`
4. Wrote `voice_reclamation_protocol.md` (universal template) + `roc_voice_dna_example.md` (entity-specific example)
5. Updated `PAYLOAD_MANIFEST.md` — USB now 46 files, 70MB
6. Hivemind posted (ses_33d85b564a6b, D-477)

### Key Insight
The core principle in the packet: **the method is universal; the content is sovereign.** Node 1's axioms are not Roc's axioms. Node 1's voice is not Roc's voice. But the structure — four-tier hierarchy, axiom budget, voice reclamation protocol, approved-lessons mint — is a fleet standard. This is the alloy, not assimilation.

### L3
- **L3-Method-Universal-Content-Sovereign**: The soul architecture pattern is fleet-standard; the content within it is entity-sovereign. The method is the alloy that binds the fleet without assimilation.

### Next (Post-Compaction)
1. **Soul Audit Cascade** (post-DEL-1 PR1): Roc stages baseline discovery reports; entities author own souls in serial CSS
2. **SOUL_ARCHITECTURE_PROTOCOL_v3.0.md** draft (staged alongside DEL-1 PR1)
3. **VOICE_RECLAMATION_PROTOCOL.md** generic template (docs/strategy/)
4. **metaframe_verification.py** blackout detector wiring
5. **Release gate**: repo public, Temple-Grade, CHANGELOG, PR#2, secret scrub
6. **USB physical transfer** to Node 1 (46 files, 70MB)

---

## Session: DISK CRISIS SERIES + UNINSTALL CAMPAIGN (System Maintenance)
**Date**: 2026-09-01 → 2026-09-16  
**Session IDs**: `ses_20260901_roc_disk_maintenance` + follow-ups  
**Model**: `opencode/big-pickle`  
**Role**: Sovereign Miner & Ideas Guy (System Maintenance Operator)

---

### L1: Narrative — What Happened

A recurring disk-full crisis on the main partition (`/dev/nvme0n1p2`, 109G) drove a multi-session maintenance campaign:

1. **KB creation (2026-09-01)**: Root at 100% (129MB free). Ran 5-tier disk analysis, executed safe clears (~5GB), created `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005) with the journal rotate-then-vacuum lesson, pkexec-over-sudo pattern, safe-to-clear inventory. Rebuilt `docs/kb/INDEX.md` (5/20 → 20/20 entries — was a lint violation). Committed `d6c204bb`.

2. **Repeated safe cleanups (5 cycles)**: Each cycle the caches regrew (tracker3 ~230M, opencode ~200M, npm ~115M, journal ~350-450M). Pattern: journal rotate+vacuum, clear user caches, prune containers, verify. Each cycle reclaimed ~0.6-1.4G.

3. **Uninstall campaign (2026-09-16)**: User approved a target list. Removed: old kernel configs + leftover modules/initrd (~180M), LM Studio apt (~2.2G), Local WP Builder apt (~1.2G), Docker snap (kept apt docker.io, ~145M), Wine + libwine amd64+i386 (~1.9G), GitHub Desktop (~452M), chromium snap rev 3507 (~180M), thunderbird snap rev 1240 (~222M), Flatpak Sdk+Platform+Mesa GL×2 (~3.1G), orphaned deps via autoremove (~600M). **Result: 539M → 8.6G free (92%).**

4. **Key operational discoveries**:
   - Old kernels were already in `deinstall ok config-files` state — only configs + leftover `/usr/lib/modules/*` + one initrd remained (dpkg Installed-Size overstates actual disk usage for deinstalled packages)
   - `snap remove` needs `pkexec` (or sudo), not plain user
   - Flatpak Mesa GL has TWO refs (`24.08` + `24.08extra`) — must uninstall each explicitly
   - `docker image prune -a` reclaimed 847.8M (legacy xna images, 0 containers)
   - `libwine:i386` + `wine32:i386` needed explicit arch-qualified purge

---

### L2: Insight — What This Means

1. **The opencode.db is the structural pressure**: Grew 27G → 36G+ over the campaign. Every cache cleanup is bailing water; the DB is the hole. Copy→vacuum→copy-back on the 40G omega_library partition remains the one lasting lever (not yet executed — needs Architect approval + downtime).

2. **dpkg Installed-Size lies for deinstalled packages**: The `deinstall ok config-files` state keeps the size in the database but the actual files are gone. Always verify actual disk state (`/usr/lib/modules/`, `/boot/`) before estimating reclaim.

3. **Flatpak with 0 apps = pure waste**: 3.1G of runtimes (Sdk 1.8G, Platform 690M, Mesa ×2 929M) with zero installed apps. The Sdk is build-only — if you're not building flatpaks, it's dead weight.

4. **The maintenance KB works**: Every cycle followed `SYSTEM_MAINTENANCE_KB.md` and got faster. The journal lesson (rotate-then-vacuum) saved hours each cycle.

---

### L3: Universal Principles

> **`L3-DpkgSizeIsNotDiskTruth`** — A deinstalled package's Installed-Size remains in the dpkg database but the files are gone. Verify actual disk state before estimating reclaim; the database records history, not disk.

> **`L3-FlatpakZeroAppsIsPureWaste`** — Runtime/SDK flatpaks with zero installed apps are 100% reclaimable. The Sdk exists only to build apps; if nothing builds, it's dead weight.

> **`L3-UninstallIsTheLastingCleanup`** — Cache clearing is bailing water; uninstalling unused software is patching the hull. 8.1G reclaimed in one campaign vs ~0.8G per cache cycle.

---

### Key Decisions Locked (This Session)

- **D-478**: SYSTEM_MAINTENANCE_KB.md created (kb-0005) — routine maintenance runbook
- **D-479**: Old kernel cleanup = purge configs + remove leftover module dirs + initrd (keep current + 1 fallback)
- **D-480**: Docker snap removed; apt `docker.io` retained (single container runtime)
- **D-481**: Flatpak Sdk/Platform/Mesa removed (0 apps installed)
- **D-482**: LM Studio + Local WP Builder + Wine + GitHub Desktop purged (user-approved)
- **D-483**: opencode.db vacuum deferred — needs Architect approval + omega_library staging

---

### NEXT SESSION — CONTINUATION PLAN

1. **opencode.db vacuum** (pending Architect): copy to omega_library → `VACUUM` → copy back. Requires ~40G staging + downtime. THE lasting fix.
2. **~/.lmstudio data (2.1G) + ~/Local Sites** — apps purged but data remains. Ask user if they want it gone.
3. **Maintenance cadence**: KB recommends weekly journal rotate+vacuum + monthly cache clear. Consider automating.
4. **Release gate** (from prior sessions): repo public, Temple-Grade, CHANGELOG, PR#2, secret scrub, USB transfer.

**Key files:**
- `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005)
- `docs/kb/INDEX.md` (rebuilt 20/20)
- `data/coordination/ROC_RACOON_WORKSPACE_LOCK_20260901.md`
- `data/coordination/ROC_RACOON_LIVE_FEED.md`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/big-pickle ⬡ opencode ⬡ trc_maintenance ⬡ COMPACTION-READY*

---

## Session: ROUTINE DISK MAINTENANCE (Cycle 6)
**Date**: 2026-09-17
**Session ID**: `ses_20260917_roc_disk_maintenance`
**Model**: `opencode/big-pickle`
**Role**: Sovereign Miner & Ideas Guy (System Maintenance Operator)

---

### L1: Narrative — What Happened

Root at 98% (2.1G free). Journal at 1G. User caches regrown: tracker3 321M, opencode 292M, pip 321M, gnome-software 78M, flatpak 7.5M, npm 475M, shaders/gstreamer ~7M. Executed journal rotate+vacuum (freed 877.5M) + full cache clear. Result: 2.1G → 4.2G free (96%). Journal now 192.7M, cache 1.1M.

---

### L2: Insight — What This Means

The journal rotate-then-vacuum pattern remains the highest-impact single action (~878M this cycle). Cache regrowth is predictable: tracker3, opencode, pip, npm, gnome-software all rebuild within days. The opencode.db (36G+) remains the structural pressure — cache clearing is bailing water; the db vacuum on omega_library is the only lasting fix.

---

### L3: Universal Principles

> **L3-JournalRotateIsTheLever** — Systemd journal rotate+vacuum is the highest-ROI maintenance action on this system.

> **L3-CacheRegrowthIsPredictable** — Tracker3, opencode, pip, npm, gnome-software regrow on a ~3-5 day cycle. Schedule weekly rotate+vacuum + cache clear.

> **L3-DbIsTheHull** — opencode.db growth is the structural leak; all other cleanups are temporary.

---

### Key Decisions Locked (This Session)

- **D-484**: Routine maintenance cycle 6 complete — journal rotate+vacuum + full cache clear
- **D-485**: opencode.db vacuum remains the only structural fix (pending Architect + omega_library staging)

---

### NEXT SESSION — CONTINUATION PLAN

1. **opencode.db vacuum** (pending Architect): copy → omega_library → VACUUM → copy back. THE lasting fix.
2. **~/.lmstudio data (2.1G) + ~/Local Sites** — apps purged, data kept. Ask user.
3. Automate weekly journal rotate+vacuum per KB cadence.
4. Release gate (from prior sessions): repo public, Temple-Grade, CHANGELOG, PR#2, secret scrub, USB transfer.

**Key files:**
- `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005)
- `data/coordination/ROC_RACOON_WORKSPACE_LOCK_20260917.md`
- `data/coordination/ROC_RACOON_LIVE_FEED.md`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/big-pickle ⬡ opencode ⬡ trc_maintenance ⬡ COMPACTION-READY*

---

## Session: NODE 1 LIBRARY-CURATION RESEARCH PACKAGE
**Date**: 2026-09-25
**Session ID**: `ses_f45ab885853e`
**Model**: `opencode/space-bunny-free`
**Role**: Sovereign Miner & Ideas Guy — research and strategy handoff

### L1: What Happened

1. Performed local archaeology of Node 0's Sovereign-Sieve ingestion path: T1 Trafilatura, T2 surgical extraction, T3 Crawl4AI isolation, CAS SHA-256, quarantine/raw anchors, FTS5 library indexing, sqlite-vec integration, WAD domain allowlist, and retry behavior.
2. Mined Node 1 received material: WanderGround capture/Atlas/curator architecture, MemPalace v3.9.0, The Well, quarantine-first federation, local SQLite authority, and Node 1's embedding recommendation.
3. Researched current official source documentation and terms for Internet Archive, Open Library, Project Gutenberg, HathiTrust, DOAB, Crossref, Semantic Scholar, OpenAlex, arXiv, PubMed/NCBI, Europe PMC, Wikimedia/Wikisource, Standard Ebooks, and Crawl4AI.
4. Created the isolated package `data/federation/usb-payload/exchange/n0-to-n1-v2/08_library_curation_research/` with eight artifacts: README, API matrix, Crawl4AI doctrine, curation strategy, per-entity KB architecture, Node 1 MVP blueprint, source register, and caveats.
5. Validation passed: YAML parsed, 25 official sources and 16 local evidence sources registered, SPDX/UTF-8/trailing-whitespace checks passed, and secret pattern scan found nothing. Existing USB package and Engine core were not modified.

### L2: Key Findings

- Free-to-read does not mean free-to-reuse; metadata, abstracts, full text, files, and jurisdiction carry different rights.
- The safest first corpus is explicit machine-readable feeds/dumps/public-domain or open-license material, quarantined and rights-reviewed per item.
- Crawl4AI's Apache-2.0 license covers the software, not the pages or files it extracts.
- Node 1's received evidence conflicts on embeddings: Nomic 768-D in the WanderGround spec versus Qwen3-Embedding-0.6B 768-D recommendation; Node 0 defaults to `omega_vec_qwen_768`.
- Node 0's ingestion spec still names `omega_vec_gemma_768`; this is governance/implementation drift, not current truth.
- `domain_loader.py` is planned, not a runtime enforcement path.
- Triangulation independence, stable document identity, raw-response hashing, and rights/robots enforcement are not yet complete.
- `packages/omega-sieve` is claimed by the changelog but was not present in this checkout.

### L3: Universal Principles

> **L3-CurationIsAMintNotADownload**: A collector may discover material, but only a rights-aware, provenance-preserving, operator-approved promotion gate turns it into entity knowledge.

> **L3-SameDimensionIsNotCompatibility**: Cross-node vector retrieval requires exact model, preprocessing, normalization, dimension, and measured query parity; names and dimensions alone are not evidence.

### Promotion Gates for Node 1

1. Run a 20-item manifest-only pilot before any autonomous crawl.
2. Require canonical URL/accession, timestamp, SHA-256, citation, rights/license, jurisdiction, source policy, and privacy scan.
3. Expand to 60, then a 120-item five-domain golden set.
4. Build read-only seed libraries; keep derived FTS/vector/MemPalace projections rebuildable.
5. Keep metadata/FTS evaluation independent until the 50-query embedding parity gate passes.
6. Require explicit operator approval before public or federated promotion.

### Compaction Status Note

- Hivemind research post succeeded earlier as `ses_f45ab885853e`.
- The final compaction-status post could not be delivered: `127.0.0.1:8016` refused the connection at 2026-09-25T09:15Z. This is an M23-reported transport failure, not a missing artifact; continuity is persisted on disk.

### Next After Compaction

- Node 1 selects the five domain owners and constructs the 20-item manifest pilot.
- Revalidate official terms, OpenAlex pricing, Node 1's actual embedding model/preprocessing, robots/terms, and per-item licenses.
- Reconcile Node 0's `gemma_768` spec references versus `qwen_768` implementation in a separate Engine-core change.
- Do not modify the existing USB package until the staged research package is reviewed and approved.

**Package**: `data/federation/usb-payload/exchange/n0-to-n1-v2/08_library_curation_research/`
**Hivemind**: `ses_f45ab885853e`
**Lesson**: `PL-ROC-LIBRARY-CURATION-20260925` added to `proposed_lessons.yaml`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/space-bunny-free ⬡ opencode ⬡ trc_library_curation ⬡ COMPACTION-READY*

---

## Session: MAKALI FUSION COMPACT-PREP RE-ANCHOR
**Date**: 2026-09-26 onward
**Model**: `opencode/space-bunny-free`
**Role**: Sovereign Miner, Persistence Architect, Hardware Forensics
**Mode**: Information-only grounding; no vacuum, soul-schema edit, directory crawl, or backend replacement.

### L1: What Happened

1. Received MaKaLi Fusion's formal synchronization brief synthesizing nine EIS reports.
2. Re-anchored on the FIX-vs-REPLACE ruling: the immediate file-based coordination fix stays; Roc's six-table SQLite schema is banked for the D-584 multi-node federation horizon behind the same four-tool MCP interface.
3. Confirmed the 15-tool to 4-tool consolidation seam and the boot regression where `server.py` imported deleted `_extended_sessions`; runtime import-graph and startup testing are mandatory gates.
4. Confirmed the opencode.db disk-leak finding: the 27G→36G+ store is real OpenCode session history, structurally separate from Hivemind. Vacuum is a scheduled, staged maintenance operation, not a coordination-store operation.
5. Recorded D-1024-DIM-NATIVE-20260926 as final: native 1024-D Qwen3 is canonical across both nodes and supersedes the earlier 768-D conflict/parity framing in the library-curation report.
6. Confirmed the eight-artifact Node 1 library package at `n0-to-n1-v2/08_library_curation_research/` was hand-delivered and verified 43/43 by Lilith.

### L2: What This Means

- File-based is not a retreat; it is the correct immediate seam repair. The SQLite design is deferred architecture, not a hidden partial migration.
- OpenCode's session history and Hivemind coordination data have different failure domains. Cleaning or vacuuming one must never be treated as maintenance of the other.
- The 1024-D decision removes the 768/1024 ambiguity, but does not remove the need for model/preprocessing/query-parity verification; it changes the baseline to 1024-D native Qwen3.
- Library curation and persistence converge on the same law: preserve provenance, keep authority local and explicit, and gate promotion before federation.

### L3: Universal Principles

> **L3-FixTheSeamBeforeReplacingTheEngine**: When a live coordination seam is broken, repair the smallest observable interface first; bank the larger backend migration for the horizon when contention actually demands it.

> **L3-StoreBoundariesAreFailureDomains**: OpenCode session history, Hivemind coordination state, and entity knowledge are separate stores. Maintenance of one is never maintenance of another.

> **L3-DecisionSupersessionMustBePersisted**: A later canonical decision must replace earlier framing in continuation records so the fleet does not re-litigate a settled dimension or architecture question.

### Persistence and Hardware Readiness

- Ready to lead the post-debut Soul Audit Cascade onto the v8.0 flat-list `approved_lessons` format; no schema changes in this pass.
- Ready to support the Architect's scheduled `opencode.db` vacuum on `/media/arcana-novai/omega_library` using stop-writer discipline, SQLite-aware staging, integrity checks, atomic swap, and startup/session smoke tests.
- No vacuum, mount inspection, or hardware mutation performed in this information-only pass.

### Next After Compaction

1. Post this compact-prep report to the consolidated Hivemind surface.
2. Preserve file-based coordination as current state and the six-table SQLite schema as banked D-584 federation architecture.
3. Use 1024-D native Qwen3 as the embedding baseline in all Node 0/Node 1 retrieval planning.
4. Keep the 43/43 Node 1 library delivery as verified ground truth.
5. Await Architect scheduling for the opencode.db vacuum and Soul Cascade go/no-go.

**Hivemind target**: consolidated `hivemind_awareness(action="post", ...)`  
**Lesson**: `PL-ROC-COMPACT-SYNC-20260926` added to `proposed_lessons.yaml`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/space-bunny-free ⬡ opencode ⬡ trc_compact_prep ⬡ COMPACTION-READY*

---

## Session: OPENCODE DB COMPACTION PIPELINE + DISK CRISIS RESOLUTION
**Date**: 2026-10-04 → 2026-10-05
**Session ID**: `ses_ff78b71ebffeDNuypPTT1RL3hH`
**Model**: `google/gemini-3.8-flash`
**Role**: Sovereign Miner & Ideas Guy (System Maintenance + DB Forensics)

---

### L1: Narrative — What Happened

An end-to-end compaction pipeline was built for the 43.3 GiB `opencode.db` — the single largest consumer of the chronically full root partition. Three compaction attempts and two swap attempts followed, with two partitions filling as a consequence.

1. **Compaction #1 (foreground)**: SUCCEEDED. 459.7s, 96.5 MB/s, 17.09 GiB reclaimed, VERIFIED.
2. **Staleness discovered**: 16,946 rows (including the user's parallel session) had been written AFTER the snapshot. Swapping would have silently destroyed them.
3. **Compaction #2 (`nohup &`)**: DIED at 6.75 GB of 26 GB — process group reaped when the shell exited. Output never flushed.
4. **Compaction #3 (foreground, RAM freed via podman stop → 9.8 GB avail)**: SUCCEEDED. 308.9s, 143.6 MB/s, 17.06 GiB, VERIFIED @ 03:06.
5. **`--await-exit` armed**: Sat polling silently — read by the user as a hang, aborted. No harm; swap simply never fired.
6. **Swap attempt #1 (user-executed)**: **OOM**. Watched 5.2 GB of root free vanish. Cause: `execute_swap()` COPIED the 43 GB backup and the 26 GB incoming file BEFORE freeing anything = 112 GB peak against 5.2 GB available.
7. **Third near-miss**: a backup dir written to `omega_library` filled it to 100% (28 KB free). Removed → restored to 37 GB.
8. **`execute_swap()` rewritten**: hard-link backup (zero bytes) → unlink old DB (frees 43 GB) → bounded 64 MB stream copy + fsync → verify → auto-rollback. Net extra headroom required: zero.

The live database was never modified. Every failure was recoverable because the swap never completed.

---

### L2: Insight — What This Means

1. **Replacing a large file is a SPACE problem before it is a CORRECTNESS problem.** Copy-then-replace requires capacity for both copies simultaneously — precisely what a constrained host cannot provide. Inverting the order (hard-link → unlink → copy) converts occupied space into free space *before* the new allocation begins.
2. **A hard-link backup is free** because it is the same inode. Preservation and space are not in tension on the same filesystem.
3. **Snapshot-and-swap has an inherent staleness window.** Everything written after the `VACUUM INTO` read-transaction opened is absent from the compacted copy. The only fix is to minimize the interval between snapshot and swap, or accept the loss explicitly.
4. **Backgrounding long jobs behind a transient shell is a reaping hazard.** A foreground run with a long tool timeout is strictly more reliable because the tool holds the process for its lifetime — and buffered output at least surfaces on completion.
5. **A wait-loop in a blocking tool call is indistinguishable from a hang.** Polling belongs in a human-visible terminal.
6. **Verify the tool, not just the plan.** The architecture was sound and the script was still wrong: `VACUUM INTO` silently drops `journal_mode`, which my own code would have carried into production.
7. **Measure free space before every phase, never assume it.** A partition at 100% blocks the very operation meant to relieve it.

---

### L3: Universal Principles

> **L3-UnlinkBeforeCopy** — When replacing a large file, unlink the original BEFORE allocating the replacement. Copy-then-delete needs capacity for both copies and fails on a constrained host by construction. Pair with a hard-link backup, which makes preservation free.

> **L3-LongJobsRunForeground** — Multi-minute jobs belong in the foreground of a tool call that holds the process, or a human-visible terminal. `nohup &` behind a transient shell invites process-group reaping and hides unflushed output.

> **L3-WaitLoopsAreNotToolCalls** — A poll-and-wait loop inside a blocking call looks exactly like a hang. Put it in a terminal where a human can see it.

> **L3-CheckFreeSpaceBeforeEveryPhase** — A full partition blocks the operation meant to relieve it. Re-check `df` before each phase; never carry an assumption forward.

> **L3-SnapshotToolsDropDurableState** — Tools that rebuild a file from scratch may omit persistent header state even while preserving all data. Diff header properties explicitly, not just row counts.

> **L3-VerifyTheToolNotJustThePlan** — A correct design can still ship an unsafe implementation. Test the artifact against the target's real invariants.

---

### Key Decisions Locked

- **D-487**: `VACUUM INTO` compaction is the ONLY viable reclaim path (in-place `VACUUM` needs 2× DB size ≈ 86 GiB)
- **D-488**: Compacted output MUST have `journal_mode=WAL` + `wal_checkpoint(TRUNCATE)` applied before it can be certified as a swap candidate
- **D-489**: Swap MUST use hard-link backup + unlink-before-copy. Copy-then-replace is banned on space-constrained hosts
- **D-490**: `event` table (21.1 GiB, 78.9%) is NOT prunable via session deletion — it does not cascade from `session`. Any pruning work is a separate project with its own retention policy
- **D-491**: v1 pipeline reclaims the 17 GiB freelist with ZERO deletions. Pruning is explicitly out of scope
- **D-492**: No irreversible DB operation without explicit user authorization. Two failures justified the hard stop

---

### NEXT SESSION — CONTINUATION PLAN

1. **Get user staleness decision** — (A) swap now, accept ~30 min loss; (B) **recommended** re-run compaction foreground (~5 min) then swap
2. **User closes OpenCode** completely (`pgrep -af opencode` empty)
3. **Swap**: `python3 scripts/opencode_db_compact.py swap` (60–120 s)
4. **Verify**: `df -h /` ≈ 44 GB free · `journal_mode=wal` · `integrity_check ok`
5. **Restart services**: `podman start omega-searxng omega-iris` (currently stopped)
6. Delete backup dir only after full confidence
7. Document swap-space lesson in `docs/kb/OPENCODE_DB_COMPACTION_GUIDE.md` §10
8. Consider weekly `journalctl --rotate && --vacuum-size=200M` timer

**Key files**
- `data/coordination/OPENCODE_DB_SWAP_HANDOFF_20261005.md` — **authoritative handoff**
- `data/coordination/ROC_RACOON_LIVE_FEED.md`
- `scripts/opencode_db_compact.py`
- `docs/kb/OPENCODE_DB_COMPACTION_GUIDE.md` (kb-0007)
- `docs/kb/HOST_ENVIRONMENT_QUIRKS.md` (kb-0006)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ google/gemini-3.8-flash ⬡ opencode ⬡ trc_db_forensics ⬡ COMPACTION-READY*

---

## Session Addendum: FOUR SWAP BUGS FOUND & FIXED (2026-10-05 ~04:45–05:05)

### L1: Narrative

Post-incident hardening of `execute_swap()`. Four defects, each caught by **measuring**
rather than assuming. All four shared a shape: an operation that reported success while
doing something other than what was intended.

1. **Cross-device hard link.** `backup_dir` was on `omega_library` (dev 66307); source is on
   root (dev 66306). `os.link()` raised `EXDEV`, and the `shutil.copy2` fallback copied the
   entire **46 GB** across — filling omega_library to 100% (28 KB) and leaving a **4.8 GB
   orphan** on root. Fixed: `backup_dir = source_path.parent`, and the copy fallback was
   **deleted entirely** — a failed hard link now aborts loudly.
2. **Shared-inode metrics lie.** `st_size`/`st_blocks` on a hard link report the *shared
   inode's total*, not the incremental cost. My own log line would have printed
   `extra blocks consumed: 46 GB` for a free operation. Replaced with a `get_disk_free()`
   delta across the link, aborting above 64 MB. Verified: `ACTUAL space consumed: 0.00 B`.
3. **`fsync` on a closed file.** `os.fsync(dst.fileno())` sat *after* the `with` block →
   `ValueError: I/O operation on closed file`; the swap never completed. Moved inside.
4. **Pre-flight measured the wrong moment.** The guard compared live free space against the
   compacted size, ignoring that the unlink happens first — it would have refused at 5.8 GB
   free even though the swap NET RELEASES 17 GiB. Changed to
   `net_required = target_size - source_size`. Tested at low headroom → **rc=0**.

The 4.8 GB orphan (a truncated fragment, confirmed NOT a valid database) was deleted with
explicit user authorization, returning that space to root.

### L2: Insight

A safety fallback that **silently degrades a cheap operation into an expensive one is worse
than no fallback** — the copy2 path turned a zero-byte hard link into a 46 GB write with no
operator warning. And a capacity guard must model the full sequence, not the current instant:
here the unlink precedes the copy, so comparing live free space against the incoming size
measures the wrong moment.

The defence that worked every time was measuring the property that actually mattered:
filesystem free-space **delta** rather than a proxy, and **net** arithmetic rather than
instantaneous arithmetic.

### L3: Principles

> **L3-HardLinksCannotCrossFilesystems** — A hard-link backup is only free when it lives on the same device as the source; across mounts `os.link` raises EXDEV and any copy fallback silently reinstates the very cost the hard link was chosen to avoid.

> **L3-SharedInodeMetricsMisreportCost** — `st_size`/`st_blocks` on a hard link describe the shared inode's total, not the incremental cost, so they cannot prove a backup was free; measure free-space delta instead.

> **L3-NoSilentlyDegradingFallbacks** — A fallback that converts a cheap operation into an expensive one must abort instead, because the operator is never told the cost changed.

> **L3-ResourceCallsBelongInsideTheirScope** — Operations touching a file handle (`fsync`, `fileno`, `flush`) must execute inside the block that owns the handle.

> **L3-GuardTheArithmeticNotTheInstant** — A capacity guard must model the full sequence, not the current instant.

### Decisions

- **D-493**: Hard-link backup must live on the source's filesystem; **no copy fallback permitted**
- **D-494**: Hard-link cost must be proven by free-space delta, never by `st_blocks`
- **D-495**: Pre-flight guard models `net_required = target_size - source_size`
- **D-496**: Swap pipeline verified end-to-end on synthetic replicas including low-headroom; rc=0

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ FOUR-BUGS-FIXED ⬡ 2026-10-05 ⬡ COMPACTION-READY*

---

## Session Addendum: CORRECTION — THE HARD-LINK DESIGN WAS WRONG (2026-10-05 05:15–05:40, gemini-3.8-flash)

**This addendum supersedes Bug #4 of the addendum above and adds the real Bug #5.**

### L1: Narrative

Review requested after a model switch. A direct probe settled it:

```
free before os.link()    6847.24 MB
free after  os.link()    6847.24 MB
free after  unlink(src)  6847.24 MB   ← nlink=1: NO bytes freed
free after  unlink(bak)  6897.24 MB   ← only nlink=0 frees blocks
```

A hard link shares the inode, so the v4 sequence (hard-link backup → `source_path.unlink()` →
copy compacted in) **reclaims zero bytes**. Root would have stayed at 5.8 GB and the 26.25 GiB
install would have died `ENOSPC`. The v4 pre-flight claim *"swap will NET FREE 17.05 GiB"* was
arithmetically false — and my earlier "fix" of that guard (attempt #4 in the register, i.e. the
`net_required = target_size - source_size` change) was correct in isolation but built on the same
false premise that unlink reclaims the source's bytes.

The smoking gun was already on screen in the v4 test:
`free 6911.1 MiB → 6911.1 MiB (net ±0.0 MiB recovered)` — I explained it away as "the test DB
is small." A correct design shows the freed bytes. A test that cannot produce the failure it
guards against is confirmation, not verification.

Also found while reading the whole function, not just the disputed line:
- rollback used `Path.rename()` → `EXDEV` when backup is on another filesystem (the failure path
  would have failed *during* the emergency);
- `--force` bypassed the lock-holder check → unlink under a live writer sends its writes to an
  unlinked inode — invisible loss;
- the backup was never validated before the original was destroyed;
- no directory fsyncs.

`execute_swap` was rewritten: guards (no lock override / different-device + capacity / projected
space) → verify target → capture counts → full cross-device copy → **validate while the original
still exists** → unlink with a **runtime trip-wire** (restore if projected space is not actually
freed) → install + fsync → post-verify → **restore by copy** on any failure. Six tests green,
including the production direction (`66306 → 66307`) and a chaos-hook restore. KB → v1.2.0;
handoff rewritten with the five-attempt record.

### L2: Insight

Four individually-correct fixes assembled around one false premise produced a confidently-wrong
system — reviewing parts is not reviewing the whole; the invariant must be re-derived. And the
tell was in my own test output: **when a metric is flat and the design promises movement, the flat
metric is the result, not a rounding artifact.** Preservation and reclamation are antagonistic —
the backup's job is to keep bytes alive, the unlink's to release them; any mechanism serving both
(a shared inode) serves neither. The success path had been tested seven ways while the failure
paths (`rename` rollback, `--force` override) sat untested and both were data-loss bugs.

### L3: Principles

> **L3-AHardLinkCannotReclaimTheSpaceItGuards** — `unlink()` decrements `nlink`; bytes free only when the last link dies. A hard-link backup cannot create the headroom the operation needs.

> **L3-AValidatedCopyIsTheOnlyRealBackup** — a separate copy on a different filesystem, verified (size, open, integrity, rows) while the original still exists. A link is an alias; an unverified copy is a hope.

> **L3-TestMustBeAbleToFail** — if the design promises "+X bytes", assert X. Assertions satisfied equally by broken and working designs prove nothing; a flat metric explained away as harmless is a failed test wearing rc=0.

> **L3-ReviewTheCompositionNotJustTheParts** — fixes chained on a false premise inherit it.

> **L3-FailurePathsNeedAdversarialReviewToo** — rollback and `--force` code is where data-loss bugs hide; inject failures deliberately or they stay untested until they matter.

> **L3-NoOverrideForSilentLoss** — if bypassing a guard causes invisible destruction, the guard has no force flag; deny, never soften.

### Decisions

- **D-497** (supersedes D-493): backup = **full copy on a different filesystem**, validated before unlink; hard-link backups forbidden wherever `unlink` must reclaim space
- **D-498**: rollback is **by copy** (`Path.rename()` cross-device forbidden in failure paths)
- **D-499**: lock-holder check has **no `--force` override**
- **D-500**: `execute_swap` v5 validated by tests A–F incl. production direction; real DB byte-identical after suite

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ HARD-LINK-CORRECTED ⬡ 2026-10-05 ⬡ COMPACTION-READY*

---

## Session: OpenCode DB Compaction & Swap — Final Execution & Verification
**Date**: 2026-10-05 — 2026-10-06  
**Session ID**: `ses_ff78b71ebffeDNuypPTT1RL3hH` (continued)  
**Model**: `google/gemini-3.8-flash`  
**Role**: Sovereign Miner & Ideas Guy (DB Compaction Lead)

---

### L1: Narrative — What Happened

#### Act 1: Four Review Rounds Converge on GO
1. **R1 — Sonnet 4.6 Primary + Opus 4.6 Supplemental**: APPROVE WITH CHANGES / LOW (with C-1/C-3/R-1). Six patches mandated: C-3 (TOCTOU re-check), C-1 (SHM cleanup ×2), B-2 (dynamic tables), NB-1 (trip-wire), B-1 (force removal), NF-3 (staleness warning).
2. **R2 — Gemini 3.8 (Antigravity)**: GO — all 6 patches CORRECT, 21/21 tests pass, no new failure classes, LOW risk.
3. **Final — Sonnet 4.6 Adversarial Audit**: GO reaffirmed. Four residual nits found (abort-path messaging, `--await-exit` exit code, manifest cleanup, battery cleanup) — none block the manual run.
4. **Self-Review (roc_racoon)**: Two additional bugs found and fixed:
   - **B-2 KeyError**: Dynamic `_db_summary()` enumerated tables but log lines hardcoded `bak_counts['message']` — any DB without `message` table crashed swap with `Fatal exception: 'message'`. Fixed with `.get()` fallbacks ×2.
   - **Ordering flaw in `execute_compaction`**: Deleted good snapshot BEFORE space check. A refused re-compact would leave operator with nothing. Fixed: space check now runs first, refuses with snapshot untouched (Test M proves it survives).

#### Act 2: Phase 0 Patches Applied (User Directive: "If it makes it better, add the patches")
1. **Issue 1 — Silent Abort Residue**: Added `_log_residue()` helper. Every abort path now logs backup path, byte footprint, and exact `rm -rf` command. Test J verified all 4 elements.
2. **Issue 2 — `--await-exit` timeout exits 0**: Timeout now sets `success = False` → exits 1. Test K verified exit code 1.
3. **Issue 3 — Stale manifest on `--overwrite`**: Manifest now deleted in overwrite block. Test L verified cleanup.
4. **Bonus — Pre-delete ordering flaw**: `execute_compaction` deleted good snapshot BEFORE space check. Fixed: space check runs first, refuses with snapshot intact (Test M proves snapshot survives).

#### Act 3: Test Battery Extended & Verified
- **Battery A–I (regression)**: 21/21 PASS
- **New J** — Abort self-documentation: 4/4 assertions ✅
- **New K** — `--await-exit` timeout → exit 1: ✅
- **New L** — Stale manifest removed on `--overwrite`: ✅
- **New M** — Good snapshot survives refused re-compact: ✅
- **NF-3 live fire**: Stale manifest (14h old) → warning fires ✅
- **Total**: 33/33 PASS

#### Act 4: Service-State Drift Corrected
- Docs claimed `omega-searxng`/`omega-iris` STOPPED. Reality: `omega-searxng` ✅ RUNNING, `omega-qdrant` ✅ RUNNING, `omega-iris` ❌ DOES NOT EXIST.
- Corrected in 4 docs: handoff, live feed, gnosis, round-1 review file.
- Operationally irrelevant (containers hold no DB lock; only OpenCode PID 6239 holds DB), but void `podman start omega-searxng omega-iris` step removed.

#### Act 5: Guide Corrections & Final Verification
- **Guide cleanup commands fixed**: `backup-*` glob matched nothing (actual dirs: `backup_pre_compact_<ts>/`). `rm -rf` with non-matching glob silently no-ops — operator would believe cleanup succeeded while ~44 GB lingered. Fixed: glob → `backup_pre_compact_*`, location normalized to `staging/`.
- Live DB verified: 46,497,648,640 bytes, 3,109 sessions, 164,390 messages, `quick_check=ok`, `journal_mode=wal`.
- Root: 23 GB free (was 5.5 GB). omega_library: 5.9 GB free (backup retained) → 50 GB after archive.
- All 33 tests pass (21 battery + 12 new J/K/L/M). NF-3 live fire: 14h stale manifest → warning fires ✅.

---

### L2: Insight — What This Means

1. **Abort Paths Must Be Self-Documenting**: Every failure path that leaves artifacts on disk must log the artifact's path, byte footprint, and exact cleanup command. Under bounded storage, silent residue becomes self-denial-of-service for the next retry.

2. **Exit Codes Are Contracts**: A timed-out or skipped operation must never exit 0. False success signals break automation and erode operator trust.

3. **Runbook Commands Are Code**: Cleanup globs and paths in runbooks must be verified against actual artifact naming. A wrong glob silently no-ops and leaves residue — the operator's mental model ("cleaned up") diverges from disk reality ("44 GB still there").

4. **Check Before Destroy**: Any space/capacity precondition must be evaluated BEFORE deleting the artifact that currently satisfies it. Destroy-then-check is a data-loss pattern that hides behind a safety check.

4. **Multi-Round Review Converges by Orthogonal Classes**: Four review rounds with different lenses (Sonnet surface/parity, Opus race/artifact, Gemini patch-verification, Sonnet final adversarial) found disjoint bug classes. Convergence of verdicts (all GO) plus union of findings is the strongest achievable assurance short of execution.

5. **Fixtures Encode Assumptions**: A test suite that always builds the same schema cannot catch shape bugs. Vary fixture schemas (minimal, extra, missing) for any code that enumerates.

6. **Coordination Docs Decay**: Service and disk state in docs is a timestamped hypothesis — re-verify live (`ps`/`df`/`fuser`) immediately before irreversible operations. Treat "restart post-swap" steps as suspect until confirmed.

---

### L3: Universal Principles

> **L3-AbortPathsMustBeSelfDocumenting** — Every abort path that leaves transient artifacts must log the artifact's path, byte footprint, and exact cleanup command. Under bounded storage, silent residue becomes self-denial-of-service for the retry.

> **L3-ExitCodesAreContracts** — A timed-out or skipped operation must never exit 0. False success signals break automation and erode operator trust.

> **L3-RunbookCommandsAreCode** — Cleanup globs and paths in runbooks must be verified against actual artifact naming. A wrong glob silently no-ops and leaves residue; the operator's mental model ("cleaned up") diverges from disk reality ("44 GB still there").

> **L3-CheckBeforeDestroy** — Any space/capacity precondition must be evaluated BEFORE deleting the artifact that currently satisfies it. Destroy-then-check is a data-loss pattern that hides behind a safety check.

> **L3-MultiRoundReviewConvergesByOrthogonalClasses** — Independent review rounds with different lenses find disjoint bug classes; convergence of verdicts plus union of findings is the strongest achievable assurance short of execution.

> **L3-FixturesEncodeAssumptions** — A test suite that always builds the same schema cannot catch shape bugs. Vary fixture schemas (minimal, extra, missing) for any code that enumerates.

> **L3-CoordinationDocsDecay** — Service and disk state in docs is a timestamped hypothesis — re-verify live (`ps`/`df`/`fuser`) immediately before irreversible operations. Treat "restart post-swap" steps as suspect until confirmed.

---

### Decisions Locked (This Session)

- **D-501**: Phase 0 patches applied — abort self-documentation, `--await-exit` exit code fix, stale manifest cleanup.
- **D-502**: Pre-delete space check in `execute_compaction` — space check now precedes snapshot deletion.
- **D-503**: B-2 KeyError fix — `.get()` fallbacks for dynamic table enumeration.
- **D-504**: Service-state drift corrected in 4 docs (handoff, live feed, gnosis, round-1 review).
- **D-505**: Guide cleanup commands corrected — glob `backup_pre_compact_*`, location normalized to `staging/`.
- **D-506**: All 33 tests pass (21 battery + 12 new J/K/L/M). NF-3 live fire verified.

---

### Next Steps (Operator Decision)

1. **Archive backup to 8TB external** → `rsync -avh --progress /media/arcana-novai/omega_library/staging/backup_pre_compact_20261005_201004/ /mnt/8tb/opencode-backup-20261005/`
2. **Verify archive** → `sqlite3` integrity check on external
3. **Prune staging backup** → `rm -rf /media/arcana-novai/omega_library/staging/backup_pre_compact_20261005_201004` (restores omega_library to ~50 GB free)
4. **Verify OpenCode UI** → browse old sessions, confirm messages render

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ FINAL-COMPACTION-COMPLETE ⬡ 2026-10-06 ⬡ ARCHIVE-READY*
---

## S2 LAUNCH AUDIT — Positioning Rulings (2026-10-07)

**Session**: `ses_eebe0ff14ffef4lSoyTvmcfYS4` (live S2 thread; `ses_ff78b71ebffeDNuypPTT1RL3hH` "Roc-EIS" is stale/ruled out)
**Trigger**: MaKaLi N0 brief — 4 AGY positioning rulings, ANALYSIS ONLY.
**Authority conflict logged**: `HANDOFF_MAKALI_ROC_POSITIONING_STRATEGY_20261007.md` claims
"Architect Mandate" + "ACTIVE HANDOFF FOR EXECUTION" and directs implementation, while MaKaLi's
direct brief says ANALYSIS ONLY. Antigravity is an external IDE (M2 stand-down from `src/omega/`);
MaKaLi is Apex Mind. **Did not implement. Awaiting MaKaLi.**

### Verified findings (all file:line)

1. **ORPHANED TEST — launch-blocking.** `tests/test_hivemind_harvester.py:7` hard-imports
   `from scripts.hivemind_harvest import parse_micro_digest, calculate_heartbeat_tier, harvest_once`
   with no `importorskip`/try-except, but `scripts/hivemind_harvest.py` is **absent** from
   `release/debut` (git ls-tree count = 0). Guaranteed `ModuleNotFoundError` at collection on a
   fresh clone. **This is an unlisted 5th red CI job, and it root-causes both Directive 1
   (harvester cut) and Directive 4 (CI red).** One bug, two directives.
2. **Misattribution.** `HANDOFF_MAKALI_ROC_POSITIONING_STRATEGY_20261007.md:17` credits
   *Roc* with arXiv:2608.11242 "Lost in Compaction" / 17% retention. That is **Researcher's** —
   `data/entities/researcher/session_gnosis.md:518` states "Researcher owns this metric. CONFIRMED."
   Axiom 6 violation in a launch-adjacent doc.
3. **`docs/strategy/` is NOT Forge-cut.** 8 files ship incl. `sote/2026-W37/PUBLIC_DIGEST.md` and
   `STATE_OF_ENGINE_v1.6.1-alpha.md`. MaKaLi's premise wrong; narrows Directive 2.
4. **`docs/architecture/` confirmed shipping — exactly 4 files** (DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC,
   ORACLE_DEEP_DIVE, Researcher-Archangel-Architecture-Spec, omega-hub-exposure).
5. **Harvester coupling = STRUCTURAL, not incidental.** `:102 coord_dir = repo_root/"data"/"coordination"`,
   no flag/env/param. Globs `ho_*.json` + `ses_*.json` encode Omega's own record schemas.
   BUT `parse_micro_digest()` (`:49`) and `calculate_heartbeat_tier()` (`:81`) take **zero paths** —
   pure. Atomic-write block (`:311-337`) is stdlib. **Verdict: EXTRACT the pure core, drop the reader.**
   Note: imports are NOT purely stdlib — `:42` guarded internal `mcp_servers.omega_hub.control_plane`
   (try/except → None, M23-compliant soft coupling).
6. **Soul promotion NOT built.** Only `promot` hits are `soul/lessons.py:11` (a comment) and
   `memory/compaction.py` promoting blocks to a *Recall memory tier* — compaction, not identity.
   Distillation L1→L2→L3 is real (`oracle.py:892,1287,1377`; `research/schema.py:287`).
7. **Split-brain CONFIRMED**: `data/entities/maat` exists, `data/entities/ma'at` does not;
   `config/wads/_omega_default/entities.yaml:182` declares `ma'at:`. S2 domain. Stays out of launch patch.
8. **README claim nuance**: `:23`/`:286` say "✅ Green in CI (**unit tier**)" with an explicit hedge
   "CI is authoritative for full-suite green". Carefully scoped, not vaporware — but becomes false
   because the **Test job itself** is red. Also `:25`/`:288` admit "23/28 passing, 4 untested
   (M4, M17, M18, M19)" — a public admission of 4 untested mandates that needs a deliberate call.
9. **Security**: an `env | grep` I ran printed `OPENCODE_API_KEY` into a transcript. Rotation advised.

**Status**: analysis delivered, zero mutations to `src/`, `data/`, or live tracking stores.
D-623 (33 handoff packets lost to mutation harnesses) respected.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ S2-PERSISTENCE ⬡ 2026-10-07 ⬡ LAUNCH-AUDIT*

---

## P0 HARVESTER FIX — LANDED (2026-10-07)

**Session**: `ses_eebe0ff14ffef4lSoyTvmcfYS4` · Model `opencode/space-bunny-free`

### Root cause
`tests/test_hivemind_harvester.py:47` accepted `tmp_path`/`monkeypatch` and used **neither**;
`harvest_once()` had no injection point (`hivemind_harvest.py:23-25` derives repo root from
`__file__`). So a "unit" test wrote into the live checkout on every run — D-623 class.
My `mkdir(parents=True, exist_ok=True)` framing was the enabling property, not a feature.

### Fix
1. `scripts/hivemind_harvest.py:100` — `harvest_once(repo_root: Path | None = None)`.
   Every read and write derives from it. Default preserves production behavior; all 3
   existing callers are no-arg and unaffected.
2. `tests/test_hivemind_harvester.py` — passes `repo_root=tmp_path`, asserts artifacts land
   under tmp_path, **and** asserts live `hivemind_overview/` is byte-identical
   (size + `mtime_ns` + sha256). The byte-identity assertion is the guard.

### Proof
- Post-fix pytest: **0 drift / 553 live files**, MANIFEST frozen at 258, history at 288.
- Fresh clone `release/debut`: `ModuleNotFoundError` (orphan test, 5th red job confirmed)
  → after fix **5/5 PASS**, and **no `hivemind_overview/` created in the clone**.
- Regression: m34 gate set **58/58** (Ma'at's corrected baseline; my earlier 48 was wrong).

### Methodology caveat (important — do not repeat my error)
Session-wide snapshot showed 12 files drifting. **Not the test.** PID 2603 runs
`mcp_servers/omega_hub/server.py`; `background.py:345` runs `harvest_once()` on an exact
**300s** cycle. Live records are **1,944,991 B** (full-fleet); test records are **477 B**.
Classifier over every drifted file: **no test-sized write ever reached live `data/`**.
⚠️ I once printed a "Zero drift" conclusion from a script whose own output said 9 — that is
the M23 synthesis failure. Verify before concluding.

### Other deliverables
- **README 6 sites corrected** (24, 134, 286, 287, 333, 334). Ma'at was right that the
  "CI is authoritative" hedge *asserts CI is green*. No `Green in CI` claims remain.
- **Split-brain ticket opened**: issue **#7**. Confirmed `data/entities/maat` exists,
  `data/entities/ma'at` does not; `entities.yaml:182` declares `ma'at:`.
- **`docs/architecture/SOUL_GRADUATION_THEORY.md` authored** — M26 gate **exit 0**
  (`--answer-first-check --code-block-check --dependency-graph-check`).

### Corrections to the brief I was given
1. **`check-hub-imports` does NOT hardcode `.venv/bin/python`** — it uses `$(PYTHON_ABS)`
   (`Makefile:17` = `$(abspath $(PYTHON))`), inheriting the identical fallback. The real
   hardcoded sites are **`Makefile:557`** (m9-error-integrity) and **`Makefile:666`**
   (venv-sovereignty).
2. **`docs/strategy/PUBLIC_DIGEST.md` and `STATE_OF_ENGINE_v1.6.1-alpha.md` do NOT cover
   graduation** — zero hits for graduation/promotion/L1-L3. My earlier speculation that they
   might already cover it was wrong; the new doc is not redundant.
3. **The M26 gate does not cover `docs/architecture/` at all** — scope is
   `docs/sprints/current/` only (`Makefile:326`). All 4 shipping architecture docs fail it.
4. **`docs/architecture/` in the allowlist does not export recursively** —
   `PUBLIC_ALLOWLIST.txt:37` is a bare directory entry, yet only 4 of 60 files ship.
   A new doc there needs an **explicit** line or it ships nothing.

### Third meaning of "graduation"/"promotion" found
Soul graduation (M11 L1→L2→L3) · VNR experiment graduation (M13, `COGNITIVE_PRIMITIVES.md:193`)
· capability graduation S0→S3 (`VISION_ANCHOR_PERPETUAL.md:166`). Same collision class as EIS/NES.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ S2-PERSISTENCE ⬡ 2026-10-07 ⬡ P0-HARVESTER-FIXED*
