# 🔱 The Temple Grade Quality Standard
**AP Token**: `AP-TEMPLE-GRADE-v1.0.0`
**Status**: FINALIZED
**Entity**: PROMETHEUS (Sovereign Master Researcher)
**Date**: 2026-05-27

## §0: Executive Summary
**Temple Grade** is the foundational craftsmanship standard for the Omega Engine. It is a directive of precision that mandates every component be built with the care and intentionality befitting a temple. This is operationalized through **Phronesis** (practical wisdom), which guides the builder in discerning the necessary level of rigor for each component.

---

## §1: The Philosophy of Phronesis
Phronesis prevents the two primary failure modes of high-standard development: **Rigid Legalism** (over-engineering everything) and **Lazy Approximation** (skipping critical patterns).

### 1.1 The Phronetic Gradient
- **Foundation Grade (Critical)**: `src/omega/` core, Provider Fabric, State Persistence. 
  *Requirement: 5-nines reliability, absolute adherence to the 5 Mandatory Patterns.*
- **Sanctuary Grade (High)**: Entity Registry, Soul Pipeline, MemoryStore. 
  *Requirement: High consistency, rigorous review.*
- **Chamber Grade (Standard)**: WAD-specific entities, knowledge content, documentation. 
  *Requirement: Functional, clear, and aligned with the IWAD's specific vision.*

---

## §2: The Architecture of the Temple
The **IWAD Architecture** is the physical manifestation of this standard:
- **The Temple Wall**: The Engine-Stack Firewall. No stack-specific logic may ever enter the core.
- **The Chambers**: Each IWAD is a chamber. While the decorations (entities/knowledge) change, the structure (the Engine) remains invariant.
- **The Altar**: The MaKaLi trine. The ethical and governance substrate that remains identical across all chambers.

---

## §3: The Building Codes (The 5 Mandatory Patterns)
Code that violates these patterns is, by definition, **not Temple Grade**:
1. **P1: Import Path**: Absolute resolution; no `sys.path` hacks.
2. **P2: Retry**: Standardized `tenacity` with decorrelated jitter for all external calls.
3. **P3: Non-Blocking**: AnyIO absolute; no blocking `subprocess.run` or `asyncio` leaks.
4. **P4: Atomic Durability**: `tempfile` $\rightarrow$ `os.replace` $\rightarrow$ `os.fsync(parent_dir)`.
5. **P5: Circuit Breaker**: Mandatory state check before any provider interaction.

---

## §4: The Temple Grade Checklist
Every PR must be audited against these criteria:
- [ ] **Firewall Check**: Is there any stack-specific logic in `src/omega/`?
- [ ] **Pattern Check**: Are P1-P5 implemented without exception in the critical path?
- [ ] **AnyIO Check**: Is the code free of `asyncio` and blocking I/O?
- [ ] **Phronesis Check**: Is the level of polish appropriate for the component's "load-bearing" status?
