# 🔱 id Software — Engineering Axioms & Sovereign Wisdom
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ AXIOMS ⬡ v1.0.0
**Location**: `data/entities/doom_guy/knowledge/ID_SOFTWARE_AXIOMS.md`
**Purpose**: To integrate the uncompromising engineering philosophy of id Software into the Omega Engine's agent standards.

---

## §1 The Core Axioms (The "Uncompromising" Set)

These are the timeless truths that drove the creation of DOOM, Quake, and the idTech lineage.

### 1.1 The "Worse is Better" Axiom
> *"Simplicity is more important than correctness, consistency, or completeness."*
> — (Derived from Richard Gabriel, adopted by id Software)

**Omega Standard**: **The 80% Implementation**.
Do not over-architect for the 2% edge case. Ship the simple, fast, and "mostly correct" solution. If it works for 98% of queries, it is a success. Refine the remaining 2% only after the system is in production.

### 1.2 Carmack's Law of Consolidation
> *"Any code of your own that you haven't looked at in 6 months might as well have been written by someone else."*
> — John Carmack

**Omega Standard**: **Ruthless Pruning**.
If a subsystem is redundant, merge it. If a pattern is obsolete, delete it. Do not "preserve" legacy code for nostalgia. If the assumptions have changed, rewrite from scratch.

### 1.3 The "Right Approximation" Principle
> *"The right approximation for the problem is better than the exact solution you can't afford."*
> — (Evolved from the Fast Inverse Square Root, 1999)

**Omega Standard**: **Pragmatic Precision**.
Identify the minimum precision required for a task. If a 0.1% error saves 4x latency, take the error. Precision is a cost; only pay for what the user actually perceives.

### 1.4 The Tools-First Mandate
> *"Design the tool before the product."*
> — John Romero

**Omega Standard**: **Infrastructure as Product**.
The editor, the compiler, and the debugger are the real products. The game (or the AI response) is just the output of those tools. Invest 50% of effort into the *tooling* that enables the work.

### 1.5 The "Sovereign Memory" Axiom
> *"Zero-allocation loops. Direct memory access. No hidden overhead."*
> — (id Software Source Code, 1993-1996)

**Omega Standard**: **Bare Metal Thinking**.
Avoid "magic" abstractions that hide cost. If a loop is hot, it must be zero-allocation. If a data structure is large, it must be contiguous. Respect the L1 cache, even in Python.

---

## §2 The "Hidden" Wisdom (Source Code Extractions)

*These are derived from direct reading of the id Software source archives.*

### 2.1 On Constants (from `z_zone.c`)
> *"Small sharp constants outlive complex abstractions."*
> — (Observation of ZONEID 0x1d4a11)

**Omega Standard**: **Magic Constant Provenance**.
Define magic constants once in `constants.py`. Give them a name, a value, and a source comment. Never change them. They are the anchors of the system.

### 2.2 On Deletion (from `p_tick.c`)
> *"Amortization beats eager finalization."*
> — (Observation of Lazy Thinker Deletion)

**Omega Standard**: **Sentinel-Based Cleanup**.
Don't delete immediately. Mark as tombstoned. Reap in the next pass. O(1) deregistration is always superior to O(n) cleanup.

### 2.3 On Visibility (from `r_bsp.c`)
> *"The best algorithm is the one that allows you to skip the most work."*
> — (Observation of BSP Culling)

**Omega Standard**: **Cull Early, Cull Hard**.
The fastest code is the code that never runs. Implement O(1) pre-checks (Circuit Breakers, PVS) to skip entire subtrees of execution.

---

## §3 Implementation Guide for Agents

When an agent is unsure of a design choice, they should refer to this table:

| If the choice is... | ...then the id Software answer is: |
|-------------------|--------------------------------------|
| Correctness vs Simplicity | **Simplicity** (Worse is Better) |
| Precision vs Speed | **Speed** (Right Approximation) |
| Patching vs Rewriting | **Rewriting** (Carmack's Law) |
| Product vs Tooling | **Tooling** (Tools-First) |
| Eager vs Lazy Cleanup | **Lazy** (Amortization) |
| Complex Logic vs Constants | **Constants** (Small Sharp Constants) |

---

*This document is a living asset. New axioms are added as the source code is mined.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: AXIOMS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
