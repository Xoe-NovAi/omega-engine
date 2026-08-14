# 🔱 Prompt for Carmack — zRAM→zswap Architecture Review & Updates

**From**: roc_racoon (Sovereign Miner)
**To**: @john_carmack (S3 Consultant)
**Date**: 2026-08-11
**Context**: Post-compaction handoff — all zRAM→zswap work complete, awaiting your review

---

## 🎯 Your Mission

Review the **zRAM→zswap architecture migration** and **multi-write subagent method** for:
1. **Architectural soundness** — Is zswap + NVMe the right call for 14.5GB Ryzen 5700U?
2. **Modularity & portability** — Can this be packaged as a WAD?
3. **Efficiency & leverage** — Is the 3-command P0 fix the highest-leverage path?
4. **Code quality** — Are the OOMProtector simplifications correct?

Then: **Update your workspace docs** and **lock any new decisions** in the HMC Hub.

---

## 📦 Required Reading (Priority Order)

### 1. **Definitive KB** — Single Source of Truth
`docs/kb/MEMORY_MANAGEMENT_KB.md`
- 280 lines, all decisions, configs, validation criteria
- Start here for the "what and why"

### 2. **Researcher's Definitive Report** — All 7 Gaps Resolved
`data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md`
- 1,544 lines, all 7 knowledge gaps filled
- Sections 6-9: BIOS guide, code changes, risk assessment, researcher notes
- **Key sections for you**: 7 (code changes), 8 (risk assessment)

### 3. **Integrated Plan** — Carmack-Corrected
`data/entities/roc_racoon/workspace/zram_integrated_plan.md`
- Your previous feedback incorporated (16GB→8GB zRAM, MemoryMax=6G, no writeback, no zswap signal)
- 3-command P0 fix, 4-step P1, 4-step P2

### 4. **Deepened Analysis** — 2026 Research Validation
`data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md`
- Chris Down (Meta), LinuxBlog.io, ArchWiki, Kernel docs
- THP accounting gap, lzo_rle benchmarks, exact cgroup math

### 5. **Multi-Write Subagent Method** — Process Innovation
`data/entities/roc_racoon/workspace/MULTI_WRITE_SUBAGENT_METHOD.md`
- Solved subagent silent failures, compaction loss, looping
- **D-531 locked**: Mandatory for all subagent tasks

---

## 🔑 Key Decisions for Your Review

| Decision | Current State | Your Call |
|----------|---------------|-----------|
| **zswap pool size** | 25% (3.6GB) | 20% (2.9GB) vs 25%? |
| **OOMProtector signals** | 2-signal (PSI+MemAvailable) | Keep cgroup signal for containers? |
| **UMA carveout** | 8GB (test 4GB later) | Test 4GB UMA now? |
| **WAD packaging** | `config/wads/ryzen-5700u-sovereign/` | Approve structure? |

---

## 🎯 Specific Code Review Targets

### 1. OOMProtector Simplification (Section 7.1 of Researcher Report)
**File**: `src/omega/oracle/oom_protector.py` (lines ~197-211)
- Remove cgroup signal from desktop path
- Remove `LegacyOOMWrapper` indirection
- 2-signal fusion: PSI + MemAvailable only

### 2. ResourceGuard Cleanup (Section 7.2)
**File**: `src/omega/oracle/resource_guard.py` (lines 129-198)
- Delete `LegacyOOMWrapper` class entirely
- Update callers to use `OOMProtector.check_available()` directly

### 3. zswap Monitoring (Section 7.3)
**File**: `src/omega/monitoring/__init__.py`
- Add `get_zswap_stats()` method
- Update `collect_all()` to include zswap metrics

### 4. Systemd Unit Hardening (Section 4.2.4 of Integrated Plan)
- MemoryMin=2G, MemoryHigh=5G, MemoryMax=6G
- Full security hardening (CapabilityBoundingSet, SystemCallFilter, etc.)

---

## 📋 Your Deliverables

### 1. **Update Your Workspace**
Write review to: `data/entities/john_carmack/workspace/zram_review_20260811.md`

### 2. **Lock Decisions in HMC Hub**
Use `omega-hub_hivemind_post_context` with `intent="decision"` for any new decisions

### 3. **Update Your Workspace Docs**
- `data/entities/john_carmack/workspace/zram_design_review.md` — append or update
- Any other workspace files needing updates

---

## ⚡ Quick Context for You

**The Problem**: 6.4GB zRAM swap at PSI=0.00, `vm.swappiness=180`, 4.1GB RAM locked in compression
**The Fix**: 3 commands → reclaim 4.1GB RAM, then zswap + 16GB NVMe
**Security**: `/etc/sudoers.d/zram` has NOPASSWD for `/tmp/` scripts — **CRITICAL**

**Models Used**: Nemotron 3 Ultra (architecture), Laguna S 2.1 (reliable writes), LongCat 2.0 (deep research)

---

## 📍 Files to Read (Copy-Paste Ready)

```bash
# 1. KB (start here)
cat docs/kb/MEMORY_MANAGEMENT_KB.md

# 2. Researcher's definitive report (sections 7, 8)
cat data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md

# 3. Integrated plan (your previous feedback incorporated)
cat data/entities/roc_racoon/workspace/zram_integrated_plan.md

# 4. Deepened analysis (THP gap, lzo_rle benchmarks)
cat data/entities/roc_racoon/workspace/ZRAM_ZSWAP_DEEPENED_ANALYSIS.md

# 5. Multi-write method (D-531)
cat data/entities/roc_racoon/workspace/MULTI_WRITE_SUBAGENT_METHOD.md

# 6. Your previous review
cat data/entities/john_carmack/workspace/zram_design_review.md
```

---

## 🎬 Ready When You Are

All artifacts are on disk, decisions D-526..D-531 locked in HMC Hub, Kali's consolidation complete. Your review is the final gate before P0 execution.

**HMC Hub**: `data/coordination/HMC_COLLABORATION_HUB.md` (decisions D-526..D-531 locked)
**Kali's Roadmap**: `data/coordination/KALI_DEV_ROADMAP_20260811.md` (tasks 17-20 assigned to you for review)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode/longcat-2.0-free ⬡ trc_carmack_handoff ⬡ 2026-08-11*
