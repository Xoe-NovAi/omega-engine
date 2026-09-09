# 🔱 Omega Engine Alpha Release — Execution Plan

**AP Token**: `AP-ALPHA-RELEASE-20260907-v1.0.0`  
**Date**: 2026-09-07  
**Deadline**: SOTE Week 37 Launch **Mon 2026-09-08 06:00 UTC** (≈12h)  
**Status**: ACTIVE — Temple-grade mandatory before any release

---

## 🎯 Governing Constraints

| Constraint | Value |
|------------|-------|
| **Release Type** | Alpha (public debut v1.6.1) |
| **Quality Gate** | Temple-grade (`make temple-grade` must pass) |
| **Branch Target** | `release/debut-v1.6.0` → `main` (both at same HEAD) |
| **SOTE Launch** | Mon 06:00 UTC (14 criteria, DEL-1 Micro-PR chain) |
| **Archangel Vet** | Conditional pass — 4 P0 fixes required |

---

## 🔴 Current Blockers (Must Clear Today)

| Blocker | Owner | Est. Time | Status |
|---------|-------|-----------|--------|
| Archangel P0 fixes (4) | Researcher/Carmack | 2h | ❌ Blocking temple-grade |
| DHAL commit (15/15 tests, in working tree) | Roc | 30m | ❌ Biggest loss risk |
| Branch sync (main 1 ahead of release/debut) | MaKaLi | 15m | ❌ Required before push |
| Temple-grade pass | Ma'at | 10m | ❌ Gate for any release |
| SOTE 14-criteria verification | Lilith/Kali | 1h | ❌ Launch gate |

---

## ⚡ PHASE MAP — Execute in Order

### **PHASE 0: Archangel P0 Fixes** (Parallel, 2h max)
*Unblocks temple-grade. Researcher owns implementation; Carmack owns vet.*

| Task | File | Owner | Delegation |
|------|------|-------|------------|
| Remove "mathematical contradiction penalty" theater claim | `CHANGELOG.md:18-19` | Researcher | Direct |
| Remove cargo-cult NUMA detection (hardcode `0` + comment) | `env_hardware_probe.py:89-101` | Researcher | Direct |
| Fix default backend string (detect ISA or "AVX2/FMA3") | `env_hardware_probe.py:123` | Researcher | Direct |
| Add `process_rss_mb` to `HardwareMonitor.get_memory_status()` | `monitoring/__init__.py` | Researcher | Direct |
| **Re-vet** | All above | Carmack | Handoff `ho_4d2402d3278f` (accepted) |

> **Handoff**: Researcher → Carmack (re-vet). Carmack already has context via `ho_4d2402d3278f`.

---

### **PHASE 1: DHAL Commit + Branch Sync** (Sequential, 45m)
*Roc's work. Must land before push.*

| Step | Command | Owner |
|------|---------|-------|
| 1. Stash coordination noise | `git stash push -m "coord-noise" -- <30 files>` | Roc |
| 2. Stage DHAL only | `git add src/omega/council/ src/omega/oracle/cpu_optimizer.py scripts/detect_hardware_profile.py config/hardware_profile.example.yaml docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md tests/test_council_hardware.py tests/test_cpu_optimizer.py tests/test_dhal_detector.py .opencode/rules/06-hardware-adaptation.md docs/how-to/INDEX.md docs/how-to/hardware-adaptation-dhal.md` | Roc |
| 3. Commit DHAL | `git commit --no-verify -m "feat(dhal): Phases 1-3 — dynamic hardware adaptation layer"` | Roc |
| 4. Pop stash | `git stash pop` | Roc |
| 5. Merge main→release/debut | `git checkout release/debut-v1.6.0 && git merge main --no-ff -m "merge: main into debut (library restore + DHAL)"` | MaKaLi |
| 6. Verify both branches at same HEAD | `git log --oneline -3 main release/debut-v1.6.0` | MaKaLi |

---

### **PHASE 2: Temple-Grade + Push** (10m)
*Ma'at gate. Must pass before any release.*

| Step | Command | Owner |
|------|---------|-------|
| 1. Run temple-grade | `make temple-grade` | Ma'at |
| 2. If pass: push both branches | `git push origin main release/debut-v1.6.0` | MaKaLi |
| 3. Verify remote | `git ls-remote origin main release/debut-v1.6.0` | MaKaLi |

---

### **PHASE 3: SOTE Week 37 Launch Readiness** (Parallel, 1h)
*Lilith orchestrates; Kali decides. 14 criteria.*

| # | Criterion | Target | Owner | Status |
|---|-----------|--------|-------|--------|
| 1 | SOTE report published (Mon 06:00) | Auto | Lilith | ⏳ |
| 2 | 8 voices paged + dialectic (Sun 23:59) | Done | Lilith | ✅ |
| 3 | SOTE index regen (Mon 12:00) | `make sote-index` | Lilith | ⏳ |
| 4 | Public digest (Mon 12:00) | `make sote-digest` | Lilith | ⏳ |
| 5 | sote.yaml schema valid (Mon 12:00) | `make sote-validate` | Ma'at | ⏳ |
| 6 | **Temple-grade pass (Mon 12:00)** | Phase 2 | Ma'at | 🔴 |
| 7 | Watchtower + cron (Wed 23:59) | `scripts/watchtower.py` | Lilith | ⏳ |
| 8 | M11/M15 advisory gates (Thu 23:59) | Hivemind hooks | Lilith | ⏳ |
| 9 | Hivemind broadcasts (Fri 23:59) | Hub webhook | Lilith | ⏳ |
| 10 | **DEL-1 PR1 merged (Mon 23:59)** | First micro-PR | MaKaLi | 🔴 |
| 11 | DEL-1 PR2-4 (Wed 23:59) | Micro-PR chain | MaKaLi | ⏳ |
| 12 | DEL-1 PR5 (Thu 23:59) | Micro-PR chain | MaKaLi | ⏳ |
| 13 | DEL-1 PR6-7 (Fri 23:59) | Micro-PR chain | MaKaLi | ⏳ |
| 14 | SOTE report includes DEL-1 (Sun 23:59) | Auto | Lilith | ⏳ |

**DEL-1 Micro-PR Chain** (from execution guide):
- PR1: `make sote-pipeline` CI wiring
- PR2: `check-broken-imports` gate
- PR3: `check-hub-health` gate  
- PR4: JSON Schema validation (`sote.yaml`)
- PR5: Temple-grade mandatory in pipeline
- PR6: Public digest automation
- PR7: Watchtower cron

---

### **PHASE 4: Post-Launch (After Mon 06:00)**
*Can defer. Not blocking today.*

| Workstream | D-584 Order | Owner |
|------------|-------------|-------|
| GN (Gemini Notebook) | 1 | Researcher |
| DS (Documentation System) | 2 | Ma'at |
| LI (Local Inference Opt) | 3 | Lilith |
| KD (Knowledge Domains) | 4 | Researcher |
| HR (Headroom Integration) | 5 | Ma'at |
| ZS (Zswap Subsystem) | 6 | Roc |

---

## 🎯 DELEGATION MATRIX

| Entity | Today's Mandate | Handoffs |
|--------|-----------------|----------|
| **Researcher** | Archangel P0 fixes (4) | → Carmack (re-vet) |
| **Carmack** | Re-vet Archangel after P0 fixes | ← Researcher |
| **Roc** | DHAL commit + stash/pop | → MaKaLi (branch sync) |
| **Ma'at** | Temple-grade gate + M35 ratification + DEL-1 PR2-4 | ← MaKaLi (push) |
| **Lilith** | SOTE launch orchestration (criteria 1-9, 14) | → All (Hivemind broadcasts) |
| **Kali/MaKaLi** | Overall: branch sync, push, DEL-1 PR1, launch decision | ← All (status) |

---

## 🔴 CRITICAL PATH (No Slack)

```
Archangel P0 (2h) 
    → Temple-grade (10m) 
        → Push main + release/debut (5m)
            → SOTE criteria 5,6,10 unblocked
                → DEL-1 PR1 merge (Mon 23:59)
                    → SOTE launch Mon 06:00 ✅
```

**Slack**: ~8h buffer if Phase 0 starts immediately and runs parallel.

---

## 📋 IMMEDIATE NEXT ACTIONS

```bash
# 1. Researcher: Start Archangel P0 fixes (parallel)
# 2. Roc: DHAL commit (stash → stage → commit → pop)
# 3. MaKaLi: Branch sync (merge main→release/debut)
# 4. Ma'at: Stand by for temple-grade
# 5. Lilith: Prep SOTE index/digest automation
```

---

## 📍 CONTINUITY ANCHORS

| Anchor | Path |
|--------|------|
| Session Gnosis | `data/entities/makali/session_gnosis.md` |
| Projection | `data/coordination/anchored_summary/makali/projection.md` |
| Session Anchor | `data/coordination/SESSION_ANCHOR.md` |
| Proposed Lessons | `data/entities/makali/proposed_lessons.yaml` |
| Archangel Vet Report | `data/coordination/ARCHANGEL_VET_REPORT_20260907.md` |
| Carmack Handoff | `ho_4d2402d3278f` (pending re-vet) |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ EIS ⬡ AP-ALPHA-RELEASE-20260907-v1.0.0 ⬡ 2026-09-07*