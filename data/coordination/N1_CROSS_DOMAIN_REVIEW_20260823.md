<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Council — Cross-Domain Review (Node N1: Sysadmin / Infrastructure)
**AP Token**: `AP-N1-CROSS-REVIEW-20260823-v1.0.0`
⬡ OMEGA ⬡ N1 ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n1_cross_review ⬡ ACTIVE

**Date**: 2026-08-23
**Mission**: Final cross-domain review of MaKaLi Council reports from infrastructure perspective
**Workspace Lock**: `data/coordination/N1_WORKSPACE_LOCK_20260823.md` (acquired 2026-08-23T01:05:00Z)

---

## Executive Summary

As N1 (Sysadmin/Infrastructure), I have reviewed both the **Ma'at Build Report** (`MAAT_BUILD_SIDE_REPORT_20260823.md`) and **Lilith Run Report** (`RESEARCH_LILITH_RUN.md`) through the lens of infrastructure, installation, system-level operations, zswap, build RAM guards, and deployment scripts.

**Verdict**: **PROCEED WITH CONDITIONS**

The infrastructure foundation is solid. INST-1 verification script is well-designed but has gaps. DEL-1 Week 1 deletions are safe from an infrastructure perspective. Vault Path A (allowlist exclusion) has zero infrastructure impact. Router Collapse single PR is well-scoped but needs a rollback plan. Lilith's 5 critical blockers include 2 that directly impact infrastructure (dual admission gates, zombie breakers).

---

## 1. INST-1 Infrastructure Assessment

### 1.1 `install.sh` CMAKE_BUILD_PARALLEL_LEVEL=8 and RAM Guard Comments — **VERIFIED CORRECT**

**File**: `scripts/install.sh` lines 76-88

```bash
# RAM guard (14GiB host): cap native build parallelism (default 8 = physical cores).
# scikit-build-core calls `cmake --build` with NO -j; cmake then falls back to
# the documented CMAKE_BUILD_PARALLEL_LEVEL env var (ninja inherits it).
# NOTE: CMAKE_BUILD_PARALLEL_JOBS / MAKEFLAGS are NOT honored by this backend
# (verified against scikit-build-core 1.0.3 source, builder/builder.py:488).
# Measured 2026-08-21 (scripts/observe-build.sh, run llama6lvl-class):
#   6 jobs -> peak < 10GiB total WITH cline+opencode IDEs (~1GiB each) resident.
#   16 jobs (unpinned) -> ~13GiB RSS peak PLUS ~1.88GiB overflow into zRAM swap
#   (compressed size; true demand est. 17-19GiB on a 14GiB box) before OOM.
# 8 jobs ≈ physical core count on Ryzen 7 5700U; override via env if needed.
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-8}"
```

**Assessment**: 
- ✅ **Correct**: 8 jobs = physical cores on Ryzen 7 5700U (8C/16T)
- ✅ **Evidence-based**: Measured with `observe-build.sh` (lines 81-84)
- ✅ **Overrideable**: User can set `CMAKE_BUILD_PARALLEL_LEVEL` env var
- ✅ **Documented**: Comments explain *why* (scikit-build-core behavior verified in source)

**Risk**: The comment says "14GiB host" but the actual machine has 16GB RAM. The 14GiB figure accounts for ~2GiB reserved for OS/IDEs. This is accurate for the measured environment.

### 1.2 ZS-1 Zswap Subsystem Script Readiness — **READY FOR ARCHITECT SUDO**

**File**: `scripts/zswap_deploy.sh` (lines 1-59)

```bash
# 1. Enable zswap at runtime (requires root)
echo 1 > /sys/module/zswap/parameters/enabled
# 2. Set max_pool_percent=25
echo 25 > /sys/module/zswap/parameters/max_pool_percent
# 3. Set compressor=lzo_rle
echo lzo_rle > /sys/module/zswap/parameters/compressor
# 4. Verify zpool=zsmalloc (already set)
# 5. Set swappiness=100 (runtime + persistent)
sysctl -w vm.swappiness=100
# 6. Persist swappiness
cat > /etc/sysctl.d/99-omega-zswap.conf << 'SYSCTL_EOF'
vm.swappiness = 100
SYSCTL_EOF
```

**Assessment**:
- ✅ **Complete**: All ZS-1 parameters implemented (max_pool_percent=25, lzo_rle, zsmalloc, swappiness=100)
- ✅ **Persistent**: Writes `/etc/sysctl.d/99-omega-zswap.conf` for swappiness
- ✅ **Documented**: GRUB cmdline instructions for persistent zswap params (lines 52-56)
- ⚠️ **Requires sudo**: Lines 13, 18, 23, 31, 39 need root — Architect must run
- ⚠️ **ZS-2 not implemented**: `scripts/zswap_nvme_swap.sh` referenced but doesn't exist (line 58)

**Recommendation**: Create `zswap_nvme_swap.sh` for ZS-2 (16GB NVMe swapfile + systemd unit) before debut.

### 1.3 INST-1 Verification Script — **WELL-DESIGNED BUT GAPS EXIST**

**File**: `MAAT_BUILD_SIDE_REPORT_20260823.md` §1.1 (lines 23-133)

**Strengths**:
- ✅ Tests fresh clone in `/tmp`
- ✅ Verifies pyproject.toml extras split (warp, qdrant, redis, youtube in extras)
- ✅ Verifies `install.sh` uses `.[native,cli]`
- ✅ Creates venv, installs, downloads model, runs `omega talk "hello"`
- ✅ Checks for `native-gguf` in output and `IS_CLOUD=False`

**Gaps (Infrastructure Perspective)**:
| Gap | Impact | Fix |
|-----|--------|-----|
| No systemd/quadlet verification | User may expect background services | Add `systemctl --user status omega-*` check |
| No kernel param verification | zswap/swappiness not validated | Add `cat /sys/module/zswap/parameters/enabled` check |
| No swap verification | NVMe swapfile not checked | Add `swapon --show` check |
| No AppArmor/SELinux check | Container confinement (V-10 GAP) | Add `aa-status` or `sestatus` check |
| Assumes GitHub clone | CI uses local copy (line 47) | Document CI mode explicitly |
| 120s timeout | Slow machines may timeout | Make configurable via env var |

**Critical Finding**: The script **does not test what a stranger would experience** on a truly clean machine — it assumes the repo is already cloned or GitHub is reachable. A true stranger test needs:
1. Fresh VM/container
2. No pre-existing `.venv`, models, or config
3. Network latency simulation
4. Verification that `omega` command is on PATH after install

---

## 2. DEL-1 Operational Risk

### 2.1 What Happens If `omega talk` Breaks Mid-Deletion?

**Risk**: During DEL-1 Week 1 execution (10 sequential deletions), if `omega talk "hello"` fails at step 5 (search_circuit_breaker) or step 6 (QdrantAdapter), the user's machine is left in a **partially deleted state**.

**Current Mitigation** (Ma'at §2.3): Run `omega talk "hello"` after **EACH** delete.

**Infrastructure Assessment**: 
- ✅ **Atomic per-step**: Each deletion is a single file removal
- ✅ **Verification after each**: `omega talk` smoke test catches regressions immediately
- ⚠️ **No automated rollback**: If step 5 breaks, steps 1-4 are already gone
- ⚠️ **No snapshot/backup**: No `git stash` or backup before deletion sequence

**Recommendation**: Add pre-DEL-1 snapshot:
```bash
# Before DEL-1 Week 1
git stash push -m "pre-del1-snapshot-$(date +%s)" -- src/omega/oracle/search_circuit_breaker.py src/omega/memory/vector_adapters.py src/omega/audit/firewall_checker.py src/omega/oracle/oracle.py src/omega/cli/vault.py src/omega/integrations/fleet_orchestrator.py config/routing_table.yaml src/omega/coordination/miap.py src/omega/oracle/pool_tracker.py src/omega/oracle/pool_state.py
```

### 2.2 Verification Script Sufficiency for CI/CD Gate

**Current Script** (Ma'at §2.3):
```bash
omega talk "hello"  # Must still work, local, exit 0
rg RoutingTable src/omega          # Must be empty
rg miap src/omega                  # Must be empty
rg "search_circuit_breaker" src/omega  # Must be empty (except tests)
rg "QdrantAdapter" src/omega       # Must be empty (class deleted)
rg "record_first_breath" src/omega/oracle/oracle.py  # Must be empty
rg "fleet_orchestrator" src/omega --include="*.py" | grep -v test  # Must be empty
```

**Assessment**: 
- ✅ **Functional smoke test**: `omega talk` verifies end-to-end path
- ✅ **Deletion verification**: `rg` checks confirm files gone
- ❌ **No performance regression check**: No latency/memory comparison
- ❌ **No provider fabric check**: Doesn't verify all providers still load
- ❌ **No MCP Hub check**: Doesn't verify MCP tools still register

**Recommendation**: Extend CI gate with:
```bash
# Performance baseline
omega hardware-stats --oom  # Quick OOM risk check
# Provider fabric integrity
omega backends  # All providers should show HEALTHY
# MCP Hub registration
omega mcp list  # All tools should be present
```

### 2.3 Infrastructure Dependencies Not Captured

| Dependency | Captured? | Risk |
|------------|-----------|------|
| systemd user units | ❌ | `omega mcp_restart` uses `systemctl --user` (oracle_cli.py:488) |
| Kernel params (zswap, swappiness) | ❌ | ZS-1 requires specific kernel config |
| NVMe swapfile | ❌ | ZS-2 not implemented |
| AppArmor profiles | ❌ | V-10 GAP — containers unconfined |
| Podman rootless + UserNS=keep-id | ⚠️ Partial | M6 documented but not verified in install |
| `.env` file for secrets | ⚠️ Partial | model_gateway.py:322 loads `.env`; INST-1 Fix 4 removes this |

**Critical**: The `_load_sovereign_secrets()` removal (INST-1 Fix 4) means `.env` is no longer auto-loaded. The CLI entry point (`oracle_cli.py:22-24`) still loads `.env` via `dotenv`, but ModelGateway no longer does. This is **correct** (env vars should come from shell), but must be documented.

---

## 3. Vault Path A — Infrastructure Impact

### 3.1 Path A: `PUBLIC_ALLOWLIST.txt` Excludes `src/omega/vault/` — **ZERO INFRASTRUCTURE IMPACT**

**File**: `docs/strategy/PUBLIC_ALLOWLIST.txt` (lines 14-46, 48-88)

**Allowlist includes**: `src/omega/` (line 18) — but vault is excluded via FORGE section (line 54 implicitly)

**Verification**:
- ✅ No systemd units reference `omega vault`
- ✅ No container configs (quadlets) mount vault paths
- ✅ No deployment scripts call `omega vault`
- ✅ `oracle_cli.py` lines 69-75: vault CLI is behind `try/except ImportError` — graceful degradation
- ✅ ModelGateway does NOT import `VaultCore` (Ma'at §3.1 confirmed)

**Search for `omega vault` usage in automation**:
```bash
# Results: Only in vault.py itself (CLI help text) and oracle_cli.py registration
# No CI scripts, no systemd units, no deployment automation
```

**Assessment**: **Path A is infrastructure-safe**. Zero code changes, zero deployment impact. The `omega vault` CLI is already optional (guarded by import).

---

## 4. Router Collapse — System Integration

### 4.1 Single PR Scope — **WELL-DEFINED**

**Files to delete/modify** (Ma'at §4.2):
| File | Change | Infrastructure Risk |
|------|--------|---------------------|
| `src/omega/oracle/oracle.py` | Delete TriageRouter, SemanticRouter, RAGRouter imports; rewrite `_route_by_domain`, `_select_model`; delete `record_first_breath` call | **MEDIUM** — Core routing logic rewritten |
| `src/omega/orchestration/triage_router.py` | DELETE ENTIRE FILE | **LOW** — No callers in core (verified) |
| `src/omega/oracle/semantic_router.py` | DELETE ENTIRE FILE | **LOW** — No callers in core (verified) |
| `src/omega/oracle/provider_selector.py` | KEEP — enhance with `RouteDecision` dataclass | **LOW** — Enhancement only |
| `config/providers.yaml` | KEEP — local-first list is routing config | **NONE** |
| `src/omega/oracle/health_monitor.py` | KEEP — canonical breaker factory | **NONE** |

### 4.2 Rollback Plan — **MISSING (CRITICAL GAP)**

**Current State**: No documented rollback procedure for the Router Collapse PR.

**Required Rollback Plan**:
```bash
# 1. Tag pre-collapse state
git tag pre-router-collapse-$(date +%s)

# 2. If PR breaks `omega talk`:
git revert <pr-merge-commit>  # Single revert restores all 3 files

# 3. If partial break (e.g., ProviderSelector regression):
git checkout pre-router-collapse -- src/omega/oracle/provider_selector.py
git checkout pre-router-collapse -- src/omega/oracle/oracle.py

# 4. Verify
omega talk "hello"  # Must work
```

**Recommendation**: Document this in PR description and add to `DEBUT_REMEDIATION_MANUAL`.

### 4.3 ProviderSelector Enhancement — **NO NEW SYSTEM DEPENDENCIES**

**File**: `src/omega/oracle/provider_selector.py` (lines 15-93)

**Assessment**:
- ✅ Pure Python, no new imports
- ✅ Uses existing `HealthMonitor.get_breaker()` (canonical factory)
- ✅ Uses existing `PIIMasker` from ModelGateway
- ✅ No new system calls, no new config files
- ✅ `RouteDecision` dataclass is self-contained

**No infrastructure dependencies introduced**.

---

## 5. Lilith's 5 CRITICAL BLOCKERS — Infrastructure Lens

| Blocker | Infrastructure Assessment | File:Line Evidence |
|---------|---------------------------|-------------------|
| **Missing RouteDecision contract test** | **HIGH RISK** — Contract test (Ma'at §4.3) verifies single router path but is NOT YET IMPLEMENTED. Without it, Router Collapse PR could silently break routing. | `MAAT_BUILD_SIDE_REPORT_20260823.md` §4.3 lines 337-415 (test spec exists but not in codebase) |
| **Dual admission gates (ResourceGuard + LocalInferenceAdmission)** | **MEDIUM RISK** — Two admission control paths create confusion. `ResourceGuard` (model_gateway.py:139) + `LocalInferenceAdmission` (not found in codebase — may be planned). Need single admission authority. | `model_gateway.py:139` `self.resource_guard = get_resource_guard()`; `LocalInferenceAdmission` not found in `rg` search |
| **Zombie breakers (search_circuit_breaker + 3 enum duplicates)** | **HIGH RISK** — `search_circuit_breaker.py` (321 lines) still used by `sovereign_search_service.py` (lines 48-51, 184-188). HealthMonitor has canonical breaker but migration incomplete. Enum duplicates: `CircuitState` in both `search_circuit_breaker.py:30` and `health_monitor.py:52`. | `sovereign_search_service.py:48-51,184-188`; `search_circuit_breaker.py:30`; `health_monitor.py:52` |
| **M8 false positive ("segments" in comment)** | **LOW RISK** — False positive in telemetry scan. "segments" appears in comment, not code. M8 (Zero Telemetry) not violated. | Need to locate — likely in observability code |
| **MIAP→Hivemind gap (no automated gnosis projection)** | **MEDIUM RISK** — Infrastructure gap: no automated pipeline to project session gnosis to Hivemind. Manual process only. Affects continuity (M15). | `RESEARCH_LILITH_RUN.md` §G-3/G-5; `SOVEREIGN_MANDATES.md` M15 |

---

## 6. Cross-Domain Synthesis

### 6.1 What Build Report Misses (Infrastructure Perspective)

| Missing Item | Why It Matters |
|--------------|----------------|
| **ZS-2 NVMe swapfile implementation** | ZS-1 script references `zswap_nvme_swap.sh` which doesn't exist. 16GB swapfile + systemd unit needed for MemoryMax=6G cgroup (D-584). |
| **AppArmor container hardening (V-10)** | Containers run unconfined. `PUBLIC_ALLOWLIST.txt` doesn't address container security. |
| **Systemd unit verification in INST-1** | Install script doesn't verify `omega-*` services install/start correctly. |
| **Kernel parameter persistence** | ZS-1 GRUB cmdline changes require reboot — not tested in verification. |
| **`.env` loading behavior change** | INST-1 Fix 4 removes `_load_sovereign_secrets()` but CLI still loads `.env`. Documentation gap. |
| **Backup/restic verification** | C-3 (Restic 3-2-1) amended to "local repo acceptable; timer not enabled" — not verified in INST-1. |

### 6.2 What Run Report Misses (Infrastructure Perspective)

| Missing Item | Why It Matters |
|--------------|----------------|
| **Subagent model routing infrastructure** | Lilith's G-6 shows per-agent model config works, but no infrastructure for model download/management per agent. |
| **Compaction plugin deployment** | Sovereign compaction plugin (G-5) requires `~/.config/opencode/plugin/` — not managed by install.sh. |
| **Hivemind Redis dependency** | Run-side assumes Redis for pub/sub (Hivemind), but INST-1 makes Redis optional (`OMEGA_REDIS_HOST`). Conflict. |
| **Session anchor persistence** | M15 requires `SESSION_ANCHOR.md` but no infrastructure to maintain it across reboots. |

### 6.3 Conflicts: Ma'at "Safe to Proceed" vs Lilith "5 Critical Blockers"

| Area | Ma'at Assessment | Lilith Blocker | Resolution |
|------|------------------|----------------|------------|
| **Router Collapse** | "Contract well-defined, single PR" | Missing RouteDecision contract test | **BLOCKER** — Contract test MUST land before Router Collapse PR |
| **Circuit Breakers** | "C-6′ unification complete (5/7 deprecated)" | Zombie breakers still in use | **BLOCKER** — Must complete migration before DEL-1 #5 |
| **Admission Control** | "C-10 admission control complete" | Dual gates (ResourceGuard + LocalInferenceAdmission) | **INVESTIGATE** — LocalInferenceAdmission not found in codebase |
| **Vault** | "Path A safe, zero code changes" | Not mentioned | **ALIGNED** |
| **INST-1** | "Ready for execution" | Not mentioned | **ALIGNED** |

**Key Conflict**: Ma'at says C-6′ breaker unification is "5/7 clones deprecated; 2 clones unmigrated — P-5 ticket open" but Lilith flags "zombie breakers" as CRITICAL. The 2 unmigrated clones ARE the zombie breakers. **This must be resolved before DEL-1 Week 1 executes deletion #5 (search_circuit_breaker.py).**

---

## 7. N1 Proposed Lessons (L1→L2→L3) — Tagged `[N_1]`

```yaml
# To be appended to data/entities/maat/proposed_lessons.yaml
- narrative: "N1 verified install.sh CMAKE_BUILD_PARALLEL_LEVEL=8 RAM guard with measured evidence (observe-build.sh). ZS-1 zswap script complete but requires Architect sudo; ZS-2 NVMe swapfile script missing. INST-1 verification script well-designed but doesn't test true stranger experience (no systemd, kernel, swap, AppArmor checks)."
  insight: "Infrastructure verification must include kernel params, swap, container confinement, and service management — not just 'omega talk works'. The RAM guard is evidence-based but environment-specific (14GiB available on 16GB box)."
  principle: "Install honesty requires verifying the entire sovereign stack (kernel → swap → containers → services → CLI), not just the entrypoint command. Infrastructure gates must be automated in CI, not manual sudo scripts."
  tags: ["N_1", "INST-1", "ZS-1", "infrastructure", "verification"]

- narrative: "N1 assessed DEL-1 Week 1 operational risk: 10 sequential deletions with per-step omega talk verification. No automated rollback, no pre-deletion snapshot. Infrastructure dependencies (systemd, kernel params, AppArmor, NVMe swap) not captured in verification script."
  insight: "Sequential deletions without rollback capability create irreversible partial states. Infrastructure verification must include provider fabric, MCP Hub, and system services — not just CLI smoke test."
  principle: "Destructive operations require atomic transactions or documented rollback procedures. Verification gates must exercise the full system surface, not a single happy path."
  tags: ["N_1", "DEL-1", "operational-risk", "rollback", "verification"]

- narrative: "N1 confirmed Vault Path A (PUBLIC_ALLOWLIST exclusion) has zero infrastructure impact. No systemd units, container configs, or deployment scripts reference omega vault. CLI is import-guarded."
  insight: "Allowlist-based exclusion is cleaner than code deletion for infrastructure — no runtime paths to break."
  principle: "Publication surface control via allowlist is superior to runtime deletion for infrastructure-isolated components. Delete from distribution, not from runtime."
  tags: ["N_1", "VAULT", "PUBLIC_ALLOWLIST", "infrastructure"]

- narrative: "N1 vetted Router Collapse single PR: well-scoped (3 files deleted, 1 enhanced), no new system dependencies. CRITICAL GAP: No documented rollback plan. Contract test (RouteDecision) specified but not implemented."
  insight: "Single-PR architectural changes need explicit rollback tags and contract tests as merge gates. The ProviderSelector enhancement is infrastructure-safe."
  principle: "Architectural rewrites require: (1) pre-merge tag, (2) contract test as CI gate, (3) documented 3-command rollback. No exceptions."
  tags: ["N_1", "ROUTER_COLLAPSE", "rollback", "contract-test", "ProviderSelector"]

- narrative: "N1 assessed Lilith's 5 blockers through infrastructure lens: 2 HIGH (missing RouteDecision contract test, zombie breakers), 1 MEDIUM (dual admission gates), 1 LOW (M8 false positive), 1 MEDIUM (MIAP→Hivemind gap). The zombie breakers directly conflict with Ma'at's claim that C-6′ unification is '5/7 deprecated'."
  insight: "Cross-domain reviews surface conflicts that single-domain reviews miss. The '2 unmigrated clones' in Ma'at's P-5 ticket ARE Lilith's zombie breakers. This must be resolved before DEL-1 executes."
  principle: "Critical blocker resolution requires cross-domain consensus. A 'completed' unification with known unmigrated clones is not complete — it's a known vulnerability."
  tags: ["N_1", "BLOCKERS", "circuit-breaker", "admission-control", "cross-domain"]
```

---

## 8. Final Verdict & Conditions

### VERDICT: **PROCEED WITH CONDITIONS**

### Conditions (Must Resolve Before DEL-1 Week 1 Execution):

1. **RouteDecision Contract Test** — Implement `tests/test_router_collapse_contract.py` (Ma'at §4.3 spec) and add to `make test` gate. **BLOCKS Router Collapse PR.**

2. **Zombie Breaker Migration Complete** — Migrate `sovereign_search_service.py` from `search_circuit_breaker.py` to `HealthMonitor.get_breaker()` fully. Delete `search_circuit_breaker.py` ONLY after migration verified. **BLOCKS DEL-1 #5.**

3. **Dual Admission Gates Resolution** — Audit for `LocalInferenceAdmission` class. If exists, consolidate with `ResourceGuard`. If not, document why `ResourceGuard` alone is sufficient. **BLOCKS C-10 admission control claim.**

4. **INST-1 Verification Script Hardening** — Add checks for: systemd units, kernel params (zswap/swappiness), swap, AppArmor status, provider fabric (`omega backends`), MCP Hub (`omega mcp list`). Make timeout configurable.

5. **ZS-2 NVMe Swapfile Implementation** — Create `scripts/zswap_nvme_swap.sh` with 16GB swapfile + systemd unit per D-584.

6. **Rollback Plan for Router Collapse** — Document 3-command rollback in PR description and `DEBUT_REMEDIATION_MANUAL`.

7. **Pre-DEL-1 Git Snapshot** — Add `git stash` snapshot step to DEL-1 execution protocol.

---

## 9. Hivemind Post

Posting cross-domain review to Hivemind for Kali's synthesis...
<tool_call>
<function=omega-hub_hivemind_post_context>
<parameter=channel>
opencode
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
