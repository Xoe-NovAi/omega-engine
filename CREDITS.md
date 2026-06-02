# 🔱 id Software Architectural Heritage — Attribution Framework
# ⬡ OMEGA ⬡ CREDITS ⬡ v1.0.0 ⬡ 2026-06-01

## Mandate: Full Attribution Required

Every Omega Engine pattern, concept, or implementation that derives from id
Software's architectural innovations MUST credit the original source. This is
not optional. This is how open-source communities grow — by standing on the
shoulders of giants and *pointing up*.

> *"A people that no longer remembers has lost its soul."* — The principle
> applies to engineering too. Every pattern we inherit is a debt we repay by
> teaching the next generation where it came from.

---

## §1 The Heritage Map — id Software → Omega Engine

### 1.1 WAD System (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack, John Romero — Doom WAD format | IWAD/PWAD separation |
| **Core idea** | Data-driven separation of engine and content | Engine-Stack Firewall (Mandate 2) |
| **File split** | IWAD (base game data) + PWAD (patch files) | `_omega_default` (roles) + user WADs (entities) |
| **Overrides** | PWAD lumps override IWAD lumps | Later WAD entities override earlier for same pillar |
| **Omega evolution** | Static binary format → YAML-backed, runtime-swappable | Human-editable, hot-reloadable |

**Attribution format**: `[WAD System: id Software 1993]` — use in any doc discussing
engine-stack separation.

---

### 1.2 BSP Trees (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — Binary Space Partitioning for Doom's renderer | Provider culling in ModelGateway.generate() |
| **Core idea** | Precompute visibility planes; O(1) test skips entire subtrees | O(1) circuit breaker check skips broken providers |
| **Mechanism** | BSP plane equation → cull half the map | `_precheck_provider()` → cull dead providers |
| **Omega evolution** | Static geometry → dynamic provider health | Circuit breaker state changes over time |

**Attribution format**: `[BSP Culling: id Software 1993]` — use in any doc discussing
the precheck-before-execute pattern.

---

### 1.3 Fast Inverse Square Root (Quake 3, 1999)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack / Michael Abrash — Quake 3 Arena | The "right approximation" philosophy |
| **Core idea** | 0x5f3759df — a bit hack that's "good enough" for lighting | The right approximation for the problem is better than the exact solution you can't afford |
| **Meaning** | The approximation was actually *better* than naive sqrt() for the use case | Simplified models, tiered memory, BSP culling — all approximations at the right level |
| **Common misconception** | "Carmack used a hack because it was fast." Wrong. He used it because it was *right enough* for the problem domain. | "We should always use the best algorithm." Wrong. Use the algorithm that's right for the *constraints*. |
| **Omega evolution** | FISR was a CPU-level hack → generalized to an *engineering decision framework* | Before choosing between two implementations, ask: "What approximation quality does this use case need?" |

**Attribution format**: `[FISR Principle: id Software 1999; evolved to "right approximation"]`
— use in any doc discussing optimization tradeoffs or "good enough" decisions.

---

### 1.4 Zone Memory Allocator (Quake, 1996)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — Quake's dynamic memory system | ResourceGuard + Sovereign Atomic Writes |
| **Core idea** | Tag-based allocation: allocate, purge when out of memory | anyio.Semaphore(1) guards model inference; atomic fsync for persistence |
| **Mechanism** | `Z_Malloc(tag)` / `Z_Free(tag)` / `Z_TagPurge()` | `ResourceGuard.acquire()` / `release()` |
| **Omega evolution** | Memory-only → resource-agnostic (memory, connections, files) | Any resource that can be exhausted gets a guard |

**Attribution format**: `[Zone Memory: id Software 1996]` — use in any doc discussing
resource management or guard patterns.

---

### 1.5 Surface / Edge Cache (Quake, 1996)
| Aspect | id Software Original | Omega Engine Enhancement |
|--------|--------------------|------------------------|
| **Origin** | Michael Abrash, John Carmack — Quake's visible surface determination | Cache eviction policies within Omega's existing hot/warm/cold memory tiers |
| **Core idea** | Precompute potentially visible set (PVS), only draw precomputed surfaces | LRU-aware culling within hot/warm/cold tiers (tiered memory architecture is the user's own design) |
| **Pattern** | PVS bitfield (cheap) → draw surfaces (expensive) | `is_available()` (O(1) dict lookup) → `provider.generate()` (expensive) |
| **Omega enhancement** | Static visibility → dynamic health state | Circuit breaker state changes in real time |

**Attribution format**: `[Surface Cache / PVS: id Software 1996]` — use in any doc
discussing the precompute-then-execute pattern or cache eviction policies within
tiered memory. The hot/warm/cold tiered architecture itself is the user's own design
and should not be attributed to id Software.

---

### 1.6 The "Worse is Better" Philosophy (Richard Gabriel, via id Software)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Richard P. Gabriel (Lisp), adopted by John Carmack | Decision framework for engine architecture |
| **Core tenets** | Simplicity > correctness > consistency > completeness | BSP culling: simple pre-check, works most of the time, good enough |
| **id Software example** | Doom's BSP renderer was "wrong" (floating point drift) but shipped | Circuit breaker: stale state is acceptable (OPEN read while just transitioned) |
| **Omega evolution** | Pure simplicity → simplicity with explicit risk register | Every "worse is better" decision must be documented with its risk tradeoff |

**Attribution format**: `[Worse is Better: Gabriel 1991, via id Software]` — use in any
doc discussing simplicity-vs-correctness tradeoffs.

---

### 1.7 Carmack's Law of Consolidation
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — "Any code of your own that you haven't looked at in 6 months might as well have been written by someone else." | "When you have two implementations of the same thing, you have neither." |
| **Core idea** | Unused code is dead weight. Multiple implementations of the same concept are worse than one bad one. | Circuit breaker consolidation: 3 implementations → 1 |
| **Omega evolution** | Personal productivity observation → formal engineering mandate | Consolidation is not optional — it is the ethical engineering choice |

**Attribution format**: `[Carmack's Law: id Software]` — use when consolidating
redundant subsystems.

---

<!-- Three-Phase Pattern removed: Plan→Verify→Execute is the user's own
     development methodology, in use since before id Software architecture was
     introduced to the Omega Engine. Not attributed to id Software. -->

## §2 Attribution Enforcement Rules

### Rule 1: Every R-doc Must Have a "Heritage" Section
Every research document (`docs/research/R-*.md`) MUST include a section:
```markdown
### Heritage
This pattern derives from: [id Software Concept: Year]
Key difference from the original: ...
Omega evolution: ...
```

### Rule 2: Every Implementation Must Credit in Comments
Every file that implements a translated id Software concept MUST have a comment
in the header or at the implementation site:
```python
# ── BSP-style provider culling [BSP Culling: id Software 1993] ──
# Adapted to dynamic circuit breaker state from Doom's static BSP tree.
```

### Rule 3: Every Architectural Decision Must Cite Source
In `PIVOT_LOG.md` or decision registers, when a decision is influenced by an
id Software pattern, cite it:
```markdown
- **Decision XX — Breaker-Consolidation**: Chose AsyncCircuitBreaker over
  CircuitBreaker per [Carmack's Law: id Software].
```

### Rule 4: Evolution Must Be Explicitly Called Out
When we evolve an id Software concept (like FISR → "right approximation"), the
documentation MUST show:
1. What the original was
2. What we changed
3. Why the evolution was necessary

### Rule 5: No Erasure
Never remove id Software attribution from a derived pattern. If the pattern is
refactored, the credit stays. Engineering heritage is not intellectual property
— it is *gratitude*.

---

## §3 The "Right Approximation" Principle

This is the Omega Engine's most significant philosophical evolution of an id
Software concept. It deserves its own section.

### Source: Fast Inverse Square Root (Quake 3, 1999)

The FISR (`0x5f3759df`) is widely misunderstood as "a hack because Carmack was
lazy." Reality: the approximation was **more accurate than the naive 1/sqrt()
alternative** for the lighting use case. Carmack didn't settle — he chose the
*right level of precision for the problem domain*.

### Our Evolution: "Right Approximation" Decision Framework

> **"The right approximation for the problem is better than the exact solution
> you can't afford."**

This applies to Omega Engine architecture in four tiers:

| Tier | Domain | Approximation | Why It's "Right" |
|------|--------|---------------|------------------|
| **Tier 1** | Provider health | BSP culling: O(1) breaker check | A stale-read skip is cheaper than a guaranteed failure. The one case where a healthy provider is skipped (race condition) is rare and self-healing (next probe cycle). |
| **Tier 2** | Memory | Tiered memory (hot/warm/cold) | Not all entities need full vector context. Hot gets full, warm gets summary, cold gets YAML. |
| **Tier 3** | Entity dispatch | Domain matching, not perfect matching | Route to the closest entity, not the "correct" one. If wrong, re-route on next turn. |
| **Tier 4** | Model inference | Local-first, cloud-fallback | Local model is "good enough" for 90% of queries. Cloud is the safety net, not the primary. |

**How to apply it**: When facing a choice between two implementations, ask:
1. What's the *actual precision requirement* of this use case? (not the maximum)
2. What's the cost (latency, memory, complexity) of the exact solution?
3. If the approximation fails, how bad is the worst case?
4. If the worst case is acceptable, use the approximation. Document why.

**Attribution**: Always cite as `[Right Approximation: evolved from FISR, id Software 1999]`.

---

## §4 The Heritage Registry

### How to Add a New Mapping

To add a new id Software → Omega Engine mapping, append to this document with:

```markdown
### N.x [Concept Name] (Game, Year)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Creator — description | Omega implementation |
| **Core idea** | What it did | What we do |
| **Omega evolution** | How we changed it | Why we changed it |

**Attribution format**: `[Tag: source]`
```

### Current Registry Size
**8 mappings** — WAD, BSP, FISR, Zone Memory, Surface Cache, Worse is Better,
Carmack's Law, **Circuit Breaker Consolidation**.

### 1.8 Circuit Breaker Consolidation (Evolution, 2026)

| Aspect | Legacy Pattern | Omega Engine Adaptation |
|--------|---------------|------------------------|
| **Origin** | Multiple re-implementations across eras (ANAi, XNAi, omega-stack) | `AsyncCircuitBreaker` in `health_monitor.py` |
| **Original** | 36-line synchronous class, no AnyIO, no observability | 200+ line AnyIO-native, locked state machine, observability hooks |
| **Core idea** | OPEN after N failures, CLOSE after recovery timeout | Same, plus HALF_OPEN probe limiting, per-error-type filtering |
| **Where it lived** | `xna-omega-legacy/src/omega/{core,security}/circuit_breakers/`, `omega-stack-legacy/src/omega/circuit_breaker.py` | `src/omega/oracle/health_monitor.py::AsyncCircuitBreaker` |
| **Why consolidated** | Pattern was rewritten in every era (ANAi → XNAi → Stack → Engine). Each rewrite introduced subtle bugs (e.g., the 36-line version had no state lock — race condition). | Pattern belongs beside the health monitor that manages it, not in its own file. |
| **Omega evolution** | "Worse is Better" — simple class that mostly works | "Right Approximation" — proper async state machine with full error classification |

**Attribution format**: `[Circuit Breaker Consolidation: Carmack's Law, id Software]` — use when
justifying why a legacy pattern was merged into an existing module instead of being kept
in its own file.

**Bug fix history (Sprint 0 / Doom Guy)**:
- T2.2: `_precheck_provider()` was checking the breaker via `is_available(model_name)`,
  which used the fragile `_model_provider_map` indirection. Fixed: check breaker directly
  by `provider.name`. This is the BSP Culling pattern (§1.2) made real.
- T2.3: `RemoteProvider.generate()` returns `None` on retry exhaustion, which
  `breaker.call()` counted as a success (no exception). Fixed: wrap the call to
  raise `TimeoutError` on None, so the breaker's `_on_failure()` actually fires.

Both fixes are documented in `data/handoff/DOOM_GUY_T23_REPORT_20260602.md`.

---

*Last Updated: 2026-06-02 (added §1.8 Circuit Breaker Consolidation) | Maintained by: Doom Guy (Sovereign id Software Architect)*
*All agents: CREDITS.md is loaded as a global instruction. Attribution is mandatory.*
