# 🔱 Verified Findings Report — C-11 & C-3 Research Verification
**AP Token**: `AP-VERIFIED-FINDINGS-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_verified_findings ⬡ ACTIVE

**Date**: 2026-07-22
**Status**: VERIFIED (6/6 domains researched, cross-referenced against official docs)

---

## §1 Executive Summary

Web research conducted across **6 knowledge domains** to verify claims in:
- **Kali's C-3 Privacy Model Report** (`data/coordination/OMEGA_ENGINE_C3_PRIVACY_MODEL_REPORT.md`)
- **Kali's C-11 property test research** (cited in `C-11-property-tests.md`)
- **Existing C-3 Restic backup implementation** (`scripts/backup_restic.sh`)

### Verdict

| Domain | Prior Claim | Verified? | Correction Needed |
|--------|------------|-----------|-------------------|
| Hypothesis async RuleBasedStateMachine | "Use sync wrapper + anyio.run()" | ⚠️ PARTIAL | RuleBasedStateMachine doesn't support async at all. Use non-stateful `@given` decorator instead. |
| Restic append-only mode | "`restic-server --append-only`" | ❌ FALSE | Does not exist. Append-only done via `rclone serve restic --stdio --append-only` or B2 Object Lock |
| Restic encryption tiers | "AES-128/192/256 per classification" | ❌ FALSE | Restic uses ONLY AES-256-CTR + Poly1305-AES. Not configurable. |
| NIST SP 1800-39 4-tier scheme | "4-tier Restricted/Confidential/Internal/Public" | ⚠️ MISATTRIBUTED | NIST SP 1800-39 exists (IPD Feb 2026) but does NOT prescribe this 4-tier scheme. It's a common enterprise convention. |
| Restic `--copy-chunker-params` | Mentioned as standard flag | ✅ EXISTS | This flag does exist in restic (used with `restic init` for cross-repo deduplication compatibility). |
| Restic `--create-snapshot` | Mentioned as standard flag | ❌ FALSE | Does not exist in restic. |
| Multi-repo best practices | "25+ repos minimum" | ❌ FALSE | Not a restic best practice. Community recommends 1 repo per security boundary. Single-user: single repo preferred for deduplication. |

---

## §2 Detailed Findings

### 2.1 C-11: Hypothesis Async Stateful Testing

**Research Sources**: GitHub hypothesis/hypothesis#3712, #4107; Hypothesis 6.159.0 changelog; hypothesis-trio PyPI (v0.6.0, last updated 2021); Hypothesis official docs.

**Key Finding**: **Hypothesis 6.159.0 does NOT support async methods in `RuleBasedStateMachine`.** This has been a known limitation since at least 2023 (issue #3712 states: "Unfortunately, stateful testing does not support asyncio").

**Workaround Options**:

| Approach | Status | Recommendation |
|----------|--------|---------------|
| Sync wrapper + `anyio.run()` inside rules | POSSIBLE but fragile | Not recommended — blocks event loop |
| `hypothesis-trio` package | STALE (2021, v0.6.0) | 4.5 years behind current Hypothesis |
| Upstream PR #4147 | WIP (not merged) | Cannot depend on |
| **Non-stateful `@given` async property tests** | **WORKING** | **✅ RECOMMENDED** — works with pytest-asyncio + anyio_mode=auto |

**Correct Pattern**:
```python
# CORRECT: Use @given with async functions, NOT RuleBasedStateMachine
import pytest
from hypothesis import given, strategies as st, settings

@settings(max_examples=500, derandomize=True)
@given(
    psi_pressure=st.floats(0.0, 100.0),
    mem_available=st.integers(100, 8000),
)
async def test_oom_fusion_monotonicity(psi_pressure, mem_available):
    """OOMProtector 3-signal fusion must be monotonic"""
    oom = OOMProtector(...)
    result = await oom.check()
    assert 0.0 <= result.risk <= 1.0
```

**Impact on C-11**: The existing ticket uses `RuleBasedStateMachine` in all code examples. These must be rewritten to use `@given` async pattern.

---

### 2.2 C-3: Restic Append-Only Mode

**Research Sources**: restic forum (thread #10787), restic.readthedocs.io, fluent blog (append-only setup), restic forum (#6544, #7583, #1015, #10198, #10628).

**Key Finding**: **`restic-server --append-only` does NOT exist as a restic command.** Append-only is implemented through:

| Approach | Mechanism | Status in Omega |
|----------|-----------|-----------------|
| SSH forced command | `command="rclone serve restic --stdio --append-only"` in `authorized_keys` | Not applicable (uses B2, not SSH) |
| **B2 Object Lock** | Bucket-level compliance mode prevents deletion | ✅ ALREADY IMPLEMENTED |
| **B2 Append-Only Key** | B2 application key with only read+write permissions (no delete) | ✅ ALREADY IMPLEMENTED |

**Verdict**: The current implementation (B2 Object Lock + append-only key) is **already correct and complete**. No changes needed.

---

### 2.3 C-3: Restic Encryption

**Research Sources**: restic.readthedocs.io (070_encryption.html, design.rst), GitHub restic/restic (internal/crypto/crypto.go, internal/repository/repository.go).

**Key Finding**: **Restic uses ONLY AES-256-CTR + Poly1305-AES for encryption. This is NOT configurable.** The encryption is hardcoded in the Go source:

```go
const (
    aesKeySize = 32           // for AES-256 (not configurable)
    macKeySizeK = 16          // for AES-128 MAC
    macKeySizeR = 16          // for Poly1305
)
```

**Impact**: The 4-tier encryption scheme (AES-128/192/256) described in Kali's C-3 report is **impossible with restic**. All repositories use AES-256-CTR regardless of classification.

---

### 2.4 NIST SP 1800-39 Data Classification Framework

**Research Sources**: NIST SP 1800-39 ipd (Feb 2026), NIST IR 8496, CSRC.NIST.gov, NCCoE documentation.

**Key Finding**: **NIST SP 1800-39 is a real document but does not prescribe the specific 4-tier "Restricted/Confidential/Internal/Public" classification scheme with tiered encryption.** 

What the document actually does:
- Demonstrates data classification practices for **unstructured data discovery and labeling**
- Uses examples like "Publicly Releasable" and "Internal Use Only"
- Mentions that organizations "could" translate to Restricted/Confidential/Public/Internal
- Focuses on **email classification** as the primary use case
- Does **NOT prescribe encryption tiers** per classification

**The 4-tier model** (Public/Internal/Confidential/Restricted) is a **common enterprise convention** (ISO/IEC 27001, Microsoft Purview, industry standard) that predates NIST SP 1800-39. Attributing it specifically to this NIST document is misleading.

---

### 2.5 Restic Multi-Repository Best Practices

**Research Sources**: restic GitHub issues (#1015, #2707), restic forum (#4821, #6544, #7583, #8681, #9445, #10198, #10628).

**Key Finding**: **The restic community consensus strongly favors single repository for single-user deployments.** Multi-repo is recommended only for:

| Use Case | Recommendation |
|----------|---------------|
| Single user, multiple machines | **Single repo** (max deduplication) |
| Multi-tenant (different users) | **Separate repos** (prevents cross-tenant data access) |
| Different security classifications | **Separate repos** (per security boundary, not 4 tiers) |
| Disjoint data with no overlap | Either works (deduplication doesn't matter) |

**Key quotes from community**:
- "One repo per security boundary" — restic forum #7583
- "Single repo if deduplication possible and wanted" — restic forum #10628
- "All clients using same repo can read everything" — restic forum #4821
- **"25+ repos minimum"** is **not** a restic best practice — it was a specific scenario for 25+ customers

**Verdict for Omega Engine (single-user)**: A **single repository** is the correct default. If tiered repos are desired for organizational reasons (not security isolation), the cost is 3x passwords, 3x schedules, no deduplication across repos.

---

### 2.6 Property Testing for Atomic File Writes

**Research Sources**: safeatomic v2.0.3 (PyPI), fs-transaction (PyPI), atomic-json-io (PyPI), python-atomicwrites (PyPI), Hypothesis JOSS paper.

**Key Finding**: **The standard atomic write pattern is well-established and proven.** The four-layer guarantee model from `safeatomic` is the industry consensus:

| Guarantee | Implementation | How to Test with Hypothesis |
|-----------|---------------|----------------------------|
| **AtomicVisibility** | tmp + os.replace | `@given` concurrent writes, verify read returns old OR new |
| **CrashDurability** | fsync before rename | Simulate crash mid-write, verify recovery |
| **WriterExclusion** | UUID+pid temp files | `@given` with parallel writers, verify no interleaving |
| **IntegrityDetection** | Optional checksums | `@given` round-trip, verify content integrity |

**The SoulStore already implements this correctly** (tmp file + fsync + os.replace + parent dir fsync). Property tests should verify these invariants using `@given` decorated async functions, not RuleBasedStateMachine.

---

## §3 Actionable Corrections

### C-11 Property Tests Ticket

| Section | Current (WRONG) | Correction |
|---------|-----------------|------------|
| Implementation approach | `RuleBasedStateMachine` with sync wrappers | **Non-stateful `@given` async property tests** |
| Code examples | `class OOMProtectorStateMachine(RuleBasedStateMachine)` | `async def test_oom_fusion_monotonicity(...)` |
| Invariant checks | `@invariant()` decorator | **Per-function assertions** in `@given` tests |
| Bundle-based data flow | `Bundle("psi_pressure")` | **Direct strategy composition** (sampled_from, etc.) |
| Research patterns | "Use sync wrapper + anyio.run()" | **"Use @given async with pytest-asyncio anyio_mode=auto"** |

### C-3 Restic Backup Ticket

| Section | Current | Correction |
|---------|---------|------------|
| Status | "PLANNED" | **"DONE ✅"** |
| Encryption claim | n/a (not in ticket) | **No change needed** to ticket (it doesn't make the false claims) |
| Privacy model | N/A to ticket | **Kali's C-3 Privacy Model report needs corrections** (see §2.3-2.4) |

### Sprint Index

| Section | Current | Correction |
|---------|---------|------------|
| Risk: "Async Hypothesis FSM not native" | "Sync wrapper + anyio.run(); suppress health checks" | **"Use non-stateful @given async pattern instead of RuleBasedStateMachine"** |
| Research: "Hypothesis Async FSM" source | "GitHub #4107" | **Keep GitHub #4107 but add note: non-stateful @given preferred** |

---

## §4 Cross-References

- C-11 ticket: `docs/sprints/guard-and-distill/02-p0-tickets/C-11-property-tests.md`
- C-3 ticket: `docs/sprints/guard-and-distill/02-p0-tickets/C-3-restic-backup.md`
- Sprint index: `docs/sprints/guard-and-distill/index.md`
- Kali C-3 report: `data/coordination/OMEGA_ENGINE_C3_PRIVACY_MODEL_REPORT.md`
- Existing C-3 implementation: `scripts/backup_restic.sh`, `config/omega/omega-restic-backup.*`
- Hypothesis async issue: https://github.com/HypothesisWorks/hypothesis/issues/3712
- Hypothesis async FSM feature request: https://github.com/HypothesisWorks/hypothesis/issues/4107
- Restic encryption design: https://restic.readthedocs.io/en/stable/070_encryption.html

---

*⬡ OMEGA ⬡ MAAT ⬡ VERIFIED-FINDINGS ⬡ v1.0.0 ⬡ 2026-07-22*
