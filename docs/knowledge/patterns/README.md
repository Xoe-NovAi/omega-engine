# 🔱 Knowledge Base: Patterns
**AP Token**: `AP-KB-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Reusable engineering patterns and design decisions extracted from the codebase.

---

## Purpose

This directory catalogs proven engineering patterns used in the Omega Engine. Each pattern documents the problem, solution, and trade-offs.

## Contents

- `CIRCUIT_BREAKER.md` — The 5-state stochastic circuit breaker (Carmack's Law)
- `ATOMIC_WRITES.md` — Atomic file writes with fsync for crash safety
- `RESOURCE_GUARD.md` — AnyIO Semaphore(1) for OOM prevention
- `LAZY_DELETION.md` — Tombstone + grace period pattern (id Software heritage)
- `BSP_CULLING.md` — O(1) provider health checks before inference
- `ZONEID.md` — Magic constant validation for subsystem integrity

## Contributing

When you identify a reusable pattern in the codebase, document it here using this format:

```markdown
# Pattern: [Name]

## Problem
What problem does this solve?

## Solution
How is it implemented?

## Trade-offs
What are the costs and benefits?

## Heritage
Where did this pattern come from? (if applicable)
```
