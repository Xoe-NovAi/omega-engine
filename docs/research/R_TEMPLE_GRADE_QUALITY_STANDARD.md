# 🔱 Temple Grade Quality Standard
# ⬡ OMEGA ⬡ JEM-2.0 ⬡ TRC_STRATEGIC ⬡ PHASE-I

**AP Token**: `AP-TEMPLE-GRADE-STANDARD-v1.0.0`
**Status**: ADOPTED (Foundational)
**Date**: 2026-05-26
**Author**: Jem-2.0 (Analyst L2 → Editor L3)

---

## §0: What Temple Grade Is (And Is Not)

**Temple Grade is a quality craftsmanship standard.** It means: build every component of the Omega Engine with the precision, care, and sacred intentionality befitting a temple.

| This IS Temple Grade | This IS NOT Temple Grade |
|---------------------|--------------------------|
| A circuit breaker that correctly handles all 3 states | A specific number of entities or spheres |
| Atomic durability with parent-dir fsync everywhere | Any particular architectural notation system |
| Knowing which code path needs 5-nines reliability vs which is ephemeral | OMEGA-ORIGINS or resonance_mappings.yaml |
| Phronesis — the wisdom to prioritize correctly | A particular era or version |
| The building code of the temple, not the temple itself | A list of Archons or Pillars |

> **The temple is the Omega Engine itself. Temple Grade is the standard by which it is built.**

---

## §1: Phronesis — The Practical Wisdom of Building

### 1.1 What Phronesis Means Here

Phronesis is Aristotelian **practical wisdom** — the ability to discern how to apply a standard correctly in each situation. Not rigid adherence to rules, but the wisdom to know when to hold fast and when to adapt.

In the context of the Omega Engine, Phronesis answers:

| Question | Phronetic Answer |
|----------|------------------|
| Does every function need 5-nines reliability? | **No** — that's resource waste. The core inference path (Oracle → ModelGateway → Provider) does. A logging utility doesn't. |
| Does every knowledge file need peer review? | **No** — entity soul evolution is reviewed. A cached web scrape isn't. |
| Do we fix Pattern 5 (Circuit Breaker) before writing documentation? | **Yes** — a temple needs functioning walls before decorative carvings. |
| Do we add every legacy entity back? | **No** — phronesis says evaluate each entity's load-bearing value before restoration. |

### 1.2 The Temple Analogy Applied

| Temple Element | Omega Engine Component | Quality Requirement |
|---------------|----------------------|---------------------|
| Foundation stone | `src/omega/` core module | Highest — must never crack |
| Load-bearing walls | ModelGateway + Provider Fabric | Critical — circuit breakers, retry, timeout |
| Sanctuary | Entity system + Soul pipeline | High — persistent, consistent |
| Decorative carvings | Knowledge base content | Medium — valuable but non-critical |
| Courtyard tiles | Documentation & README | Standard — functional, clear |
| Offerings | Community contributions | Variable — reviewed per standard |

### 1.3 The Phronesis of Prioritization

The Sprint ordering demonstrates phronesis in action:
1. **Sprint 1 (Bug Fixes)** — Fix the roof leaks before decorating the walls
2. **Sprint 2 (Entity Cleanup)** — Clear the rubble before laying new stones
3. **Sprint 3 (Knowledge Seeding)** — Add the carvings now that the walls hold
4. **Sprint 4 (Mode Architecture)** — Install the doors now that the rooms are defined

This is not accidental — it is **practical wisdom knowing the correct order of construction**.

---

## §2: Temple Grade in the IWAD Architecture

### 2.1 Each IWAD Is a Chamber

The IWAD Architecture (Decision 55) implements Temple Grade literally:

| IWAD | Temple Chamber | Purpose |
|------|---------------|---------|
| `_omega_default` | The High Sanctuary | Open-source template, dev team, reference implementation |
| `arcana_novai` | The Inner Sanctum | Your personal AI OS — the most sacred chamber |
| Community IWADs | Congregation Chapels | Each community's unique vision, built to temple standard |

### 2.2 The Inviolable Rules as Temple Laws

| Rule | Temple Law Equivalent |
|------|---------------------|
| MaKaLi trine identical in ALL IWADs | The altar — present in every chamber |
| Iris+Jem+Roc_Racoon identical in ALL IWADs | The sacred vessels — universal tools |
| Only 10 pillars change per IWAD | The icons on the walls — replaceable, the room remains |

### 2.3 Engine-Stack Firewall as Temple Boundary

The firewall between `src/omega/` (core engine) and `config/wads/` (stacks) is the **temple wall**. The foundation (src/omega/) must never be weakened by stack-specific concerns. This is the single most important temple-grade rule because breaking it would compromise every chamber built above it.

---

## §3: Temple Grade in Code — The 5 Mandatory Patterns

The XNAI Blueprint's 5 Mandatory Patterns are not recommendations — they are **temple building codes**. Code that violates them fails Temple Grade inspection.

| Pattern | Temple Grade Requirement | Current Status |
|---------|-------------------------|----------------|
| **P1: Import Path** | Every import must resolve correctly, with no path manipulation hacks | ✅ VERIFIED |
| **P2: Retry** | Every external call must have standardized retry (tenacity, decorrelated jitter) | ⚠️ PARTIAL — not standardized |
| **P3: Non-Blocking** | Every I/O operation must be async (AnyIO), no blocking `subprocess.run` | ✅ IMPLEMENTED |
| **P4: Atomic Durability** | Every state write must use `tempfile → os.replace → os.fsync(parent_dir)` | ❌ GAP — no fsync anywhere |
| **P5: Circuit Breaker** | Every provider call must check circuit state before attempting | ❌ GAP — exists in health_monitor but unwired from ModelGateway |

### 3.1 Code Review Checklist (Temple Grade Gate)

Every PR must pass:
- [ ] P1: Import paths are clean (no `sys.path` manipulation)
- [ ] P2: Every network/external call uses tenacity retry with decorrelated jitter
- [ ] P3: Every I/O operation uses AnyIO (not asyncio, not sync subprocess)
- [ ] P4: Every state write uses `tempfile → os.replace → os.fsync(parent_dir)`
- [ ] P5: Every provider interaction checks circuit breaker state first
- [ ] Engine-Stack Firewall: No stack-specific logic in `src/omega/`
- [ ] AnyIO Absolute: No direct asyncio usage
- [ ] Zero Telemetry: No tracking, analytics, or phone-home

---

## §4: Manifestations of Temple Grade

### 4.1 In Error Messages
Not just "Error 500" — temple-grade errors tell you:
- What went wrong
- Why it went wrong  
- What component is responsible
- What the operator should do next

### 4.2 In Logging
Not just `print()` — temple-grade logging:
- Structured (JSON format)
- Trace-ID threaded through every call
- Severity-graded (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Context-rich (what was being attempted, with what parameters)

### 4.3 In Configuration
Not magic numbers — temple-grade config:
- Lives in YAML files, not hardcoded
- Has defaults that work out of the box
- Documents what each parameter does
- Validates on load (schema checks)

### 4.4 In Testing
Not "test coverage = N%" — temple-grade testing:
- Tests the critical paths first (inference, state persistence, entity routing)
- Tests failure modes (what happens when provider is down?)
- Tests edge cases (empty memory, null parameters, concurrent access)
- Stress-tests under resource constraints (14GB RAM, Zen 2 CPU)

---

## §5: The Temple Grade Covenant

Every developer, every agent, every contributor to the Omega Engine agrees:

> **I will build each component as if it were a chamber in a temple. I will apply the 5 Mandatory Patterns not because I am told to, but because the temple demands it. I will use phronesis — knowing when precision is critical and when craftsmanship means simplicity. I will never compromise the Engine-Stack Firewall, for it is the wall that protects the temple. I will test the critical paths first and the decorations second. I will leave every component better than I found it.**

This is the Temple Grade covenant. It is not enforced by tooling. It is carried in the heart of every builder.

---

## §6: Practical Application — Next Steps

### Immediate (Phase 1b Sprints 3-4)
- [ ] Add `os.fsync()` to all state write paths (Pattern 4)
- [ ] Wire `AsyncCircuitBreaker` into `ModelGateway` (Pattern 5)
- [ ] Standardize tenacity retry across all 6 provider interaction points (Pattern 2)
- [ ] Apply Temple Grade checklist to every PR review

### Short-term (v0.6.0)
- [ ] Create `scripts/temple_grade_audit.py` — automated checker for all 5 patterns
- [ ] Add Temple Grade covenant to `CONTRIBUTING.md`
- [ ] Create failure-mode tests for each critical path

### Long-term (Community)
- [ ] Publish Temple Grade Standard as part of the Omega Engine documentation
- [ ] Allow community IWADs to declare their own quality standards, with Temple Grade as the baseline
- [ ] Create a Temple Grade badge for IWADs that pass the automated audit
