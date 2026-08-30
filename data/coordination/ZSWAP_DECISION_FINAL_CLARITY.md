---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: decision_clarity
task_id: R03-maat-zswap-clarity
session_purpose: "Final clarity on zswap vs zRAM to end recurring regression"
date: 2026-08-26
author: maat (Zswap Specialist)
paged_by: kali (Sprint Coordinator) via grokster-pattern-page
status: EXECUTED (purge applied 2026-08-26 by kali per Architect authorization)
---

# ZSWAP DECISION — FINAL CLARITY

**Purpose**: Permanently resolve the zswap-vs-zRAM contradiction that recurs in `HOLISTIC_ARCHITECTURE_PLAN_20260820.md`.

---

## §1 — OFFICIAL DECISION (Authoritative)

> **The Omega Engine uses zswap + NVMe swap file. zRAM is DISABLED. They are never run simultaneously.**

### Ratified Authority Chain

| Decision | Status | Text |
|---|---|---|
| **ADR-2026-08-10-001** | ACCEPTED | "Memory Architecture — zswap + NVMe Swap over zRAM" (Carmack + Researcher + Jem + LongCat + Nemotron 3 Ultra). Source: `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md:35` |
| **D-526** | ✅ RATIFIED | "zswap > zRAM for Desktop with NVMe — Migrate from zRAM to zswap + NVMe swap file. zswap: 25% pool (max_pool_percent), lzo_rle compressor, zsmalloc allocator. Confirmed by Chris Down (kernel developer), Fedora Project, kernel docs. Never run both simultaneously." Source: `docs/decisions/PIVOT_LOG_ARCHIVE_20260522_20260810.md:24` |
| **D-527** | ✅ LOCKED | "Never Run zswap + zRAM Simultaneously — They fight each other. Migration path: swapoff -a → rmmod zram → enable zswap → create NVMe swap → swapon -a." Source: `docs/decisions/PIVOT_LOG_ARCHIVE_20260522_20260810.md:25` |
| **D-581** | ✅ RATIFIED | "zswap + NVMe Swap Confirmed — D-526 REAFFIRMED (2026-08-20)". Corrects prior inversion that claimed zswap was "rejected detour." Source: `docs/decisions/PIVOT_LOG.md:224` |
| **D-584** | ✅ RATIFIED | "zswap + NVMe Swap Locked — D-526 REAFFIRMED (2026-08-20)". Reaffirms D-526 + D-527. Source: `docs/decisions/PIVOT_LOG.md:256` |
| **PIVOT_LOG Summary** | ✅ LOCKED | "D-526/D-527/D-581/D-584 | zswap + NVMe swap over zRAM; never both | ✅ LOCKED" Source: `docs/decisions/PIVOT_LOG.md:17` |

### Validated Configuration (from D-526/D-581/D-584)

```
16GB NVMe swap file (backing store)
zswap enabled:
  max_pool_percent = 25
  compressor       = lzo_rle
  zpool            = zsmalloc
  shrinker_enabled = Y
vm.swappiness      = 100
zRAM               = DISABLED (module unloaded / generator neutralized)
cgroup MemoryMax   = 6G (omega-engine, omega-hub)
```

### Carmack's Rationale (why zRAM was rejected)

> "Hard capacity cliff with no graceful degradation." — Carmack, MEMORY_SYSTEMS_DEFINITIVE_REPORT.md

zRAM locks a fixed RAM allocation in compression buffers (was 4.1 GB — 81-98% of available process RAM). zswap provides a **dynamic pool (0–3.6 GiB)** with graceful degradation via NVMe eviction, kernel-integrated reclaim, and lower CPU overhead (lzo_rle).

---

## §2 — Contradiction Source (Identified)

**File**: `data/coordination/HOLISTIC_ARCHITECTURE_PLAN_20260820.md`

| Location | System | Current Text | Verdict |
|---|---|---|---|
| **Line 150** (§"Mandatory Startup Optimizations") | System 3 | `# zRAM (not zswap) + THP + core pinning` | ❌ **CONTRADICTS** D-526/D-581/D-584 |
| **Line 261–263** (§SYSTEM 6) | System 6 | `## 💾 SYSTEM 6: zswap + NVMe SWAP SUBSYSTEM — VALIDATED CONFIG` / `### Decision: **zswap + NVMe Swap, zRAM DISABLED** (ADR-2026-08-10-001 ACCEPTED, D-526 RATIFIED)` | ✅ **CORRECT** (aligns with authority chain) |

**Root cause**: System 3 (line 150) was written from an older mental model (pre-ADR-2026-08-10-001) and was never updated when D-526/D-581/D-584 ratified zswap. System 6 was added later and correctly reflects the ratified decision. The two systems now contradict each other within the same document.

**Evidence of regression**: The same inversion pattern appeared in D-581/D-584's *prior* erroneous text ("zswap was a rejected detour") — already corrected by D-581/D-584 themselves. System 3 (line 150) is the last surviving instance of that inversion.

---

## §3 — Recommended Purge Action (for Architect Authorization)

**Two valid options — either resolves the regression. Option A is preferred for auditability.**

### Option A (PREFERRED): Stamp System 3 as SUPERSEDED

Add a banner immediately above line 150 (System 3 "Mandatory Startup Optimizations"):

```markdown
> ⚠️ **SUPERSEDED BY D-526/D-581/D-584** (2026-08-20). zRAM is DISABLED.
> The correct swap subsystem is **zswap + NVMe swap file** (see SYSTEM 6, line 261).
> This section's zRAM instruction is VOID. Do not execute `modprobe zram`.
```

Then either:
- Delete lines 150–154 (the zRAM modprobe/swapon block), OR
- Leave the code block but mark it `<!-- SUPERSEDED -->` so the historical trace remains.

### Option B (MINIMAL): Correct the line in place

Change line 150 from:
```bash
# zRAM (not zswap) + THP + core pinning
```
to:
```bash
# zswap + NVMe Swap (zRAM DISABLED) + THP + core pinning
```
And change line 151–154 from the zRAM setup block to a pointer:
```bash
# Swap subsystem: see SYSTEM 6 (line 261) — zswap + NVMe, zRAM DISABLED
# Do NOT run: modprobe zram / mkswap /dev/zram0 / swapon --priority 100 /dev/zram0
```

**Recommendation**: **Option A** — explicit SUPERSEDED stamp is stronger against future regressions and matches the D-581/D-584 correction style (which used "Correction:" blocks). It also preserves the historical record for forensic continuity (M15/M23).

---

## §4 — Canonical One-Line Statement (cite to end regression)

> **"Per D-526/D-581/D-584 + ADR-2026-08-10-001: Omega Engine uses zswap + NVMe swap file with zRAM DISABLED. Never run both (D-527 LOCKED). Any doc stating 'zRAM not zswap' is superseded."**

Agents should paste this line when encountering the contradiction. It cites the full authority chain and names the exact failure mode ("zRAM not zswap" = superseded).

---

## §5 — Cross-Reference to My R03 Recon

My prior reconnaissance (`data/coordination/research_wave2/R03_maat_zswap_system_recon.md`) is **already aligned** with D-526/D-527:
- §2 Delta Table: "zRAM DISABLED", "zswap enabled=Y", "compressor=lzo_rle", "max_pool_percent=25", "swappiness=100", "MemoryMax=6G"
- §4 Implementation Steps: Phase 2 disables zram, Phase 3 enables zswap, Phase 4 sets swappiness=100
- §5 Risk: notes "zram + zswap simultaneously would compress twice" — confirms D-527's "never both" mandate

No change needed to R03 — it is correct and can be used as the implementation blueprint once the NVMe space blocker (§2.4 of R03) is resolved.

---

## §6 — Action Items for Architect

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | Authorize purge of System 3 line 150 (Option A preferred) | Architect | ✅ AUTHORIZED + EXECUTED |
| 2 | Apply SUPERSEDED stamp or line correction to `HOLISTIC_ARCHITECTURE_PLAN_20260820.md` | kali (delegate) | ✅ DONE (line 150 stamped SUPERSEDED) |
| 3 | Add regression test: grep for "zRAM (not zswap)" in `data/coordination/*.md` → fail if found (ignore SUPERSEDED-marked lines) | Verity agent | ⏳ PENDING (recommend for Wave 2 quality gate) |
| 4 | Confirm R03 recon remains the build blueprint | maat (Zswap Specialist) | ✅ VERIFIED |
| 5 | Stamp CARMCK_REVIEW_HEADROOM_20260820.md (2 occurrences + file header) | kali (delegate) | ✅ DONE (SUPERSEDED stamps applied) |

---

*⬡ OMEGA ⬡ MAAT ⬡ mimo-v2.5-free ⬡ opencode ⬡ ZSWAP-CLARITY ⬡ AWAITING-AUTH*
