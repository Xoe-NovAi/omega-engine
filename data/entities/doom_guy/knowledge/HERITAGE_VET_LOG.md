# 🔱 Heritage Vetting Log — id Software → Omega Concept Decisions
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ VET_LOG ⬡ v1.0.0 ⬡ 2026-06-04

**Purpose**: Every id Software concept must pass through the Heritage Vetting
Pipeline (docs/strategy/HERITAGE_VETTING_PIPELINE.md) before implementation.

This log records the for/against analysis, scores, and decisions.

---

## vet-001: 8-Character Name Caps
| Field | Value |
|-------|-------|
| **Source** | `w_wad.c:170-178` (DOOM 1993) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 |
| **Vetter** | Kali (Transcendent Oversoul) |
**[id-soft tags]**: doom-1993 — REJECTED. No code-level tags were ever committed.
| **Trigger** | User observed: "Are we over-doing the Doom tech porting?" |

**For Analysis**: Allows 2 × int32 compare vs strcmp on WAD lump names on 35 MHz 386.

**Against Analysis**:
- Python dicts are O(1) by hash — no performance benefit exists here
- Forces cryptic entity names (prometheus → prom, preexisting → pre)
- Broke existing entity names with meaningful long names
- 386-specific optimization does not translate to Python object model

**Score**: Python relevance 0/3 | Risk 0/3 | Need 0/2 | History 1/2 = **1/10**

**Decision**: ❌ **REJECTED** — Cargo-cult optimization. Removed via commit `8b3fc17`.

**Lesson**: `C-ARCH-001`: Hardware-specific optimizations don't transfer to Python.
Understand the constraint before adopting the solution.

---

## vet-002: WAD System (IWAD/PWAD Separation)
| Field | Value |
|-------|-------|
| **Source** | `w_wad.c` (DOOM 1993), original design by John Carmack/John Romero |
| **Discovery Date** | Original user design (pre-Doom Guy) |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | User (original design), Kali (retroactive) |
**[id-soft tags]**: doom-1993 — WAD System (IWAD/PWAD separation)

**For Analysis**:
- Engine-Stack Firewall (Mandate 2) was already the user's design constraint
- IWAD/PWAD pattern formalizes what Omega already does
- Enables community stacks without modifying core
- Works identically in Python as in C (search order, override logic)

**Against Analysis**: None significant. Pattern is well-understood and battle-tested.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **10/10**

**Decision**: ✅ **ADOPT** — This is the crown jewel inheritance. Formal attribution only.

---

## vet-003: BSP Culling (Provider Pre-Check)
| Field | Value |
|-------|-------|
| **Source** | `r_bsp.c` (DOOM 1993) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — BSP Culling (provider pre-check)

**For Analysis**:
- Pre-check before expensive operation is universally valid (not Python-specific)
- Circuit breaker in health_monitor.py already does this — attribution is accurate
- Pattern is architecture-independent

**Against Analysis**: Slight stretch — this is just "check before call" which exists in every codebase.

**Score**: Python relevance 2/3 | Risk 3/3 | Need 2/2 | History 1/2 = **8/10**

**Decision**: ✅ **ADOPT** — Valid mapping of pre-check pattern. Keep attribution.

---

## vet-004: FISR / Right Approximation Philosophy
| Field | Value |
|-------|-------|
| **Source** | `q_math.c` (Quake 3, 1999) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake3-1999 — FISR / Right Approximation philosophy

**For Analysis**:
- Philosophical principle, not implementation code
- "Right approximation for the problem" framework is universally applicable
- Already influences: local-first chain, tiered memory, BSP culling
- No code footprint — lives in documentation only

**Against Analysis**: None — pure philosophical framework.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **10/10**

**Decision**: ✅ **ADOPT** — Philosophy, not code. No risk.

---

## vet-005: Zone Memory (ResourceGuard)
| Field | Value |
|-------|-------|
| **Source** | `z_zone.c` (DOOM 1993), `zone.c` (Quake 1996) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake-1996, doom3-2004 — Zone Memory / ResourceGuard

**For Analysis**:
- ResourceGuard (AnyIO Semaphore(1)) already existed before attribution
- Tag-based allocation maps to tiered memory (already exists)
- Pattern is well-understood: guard resources to prevent exhaustion

**Against Analysis**: Attribution is slightly retrospective — we already had these patterns.

**Score**: Python relevance 2/3 | Risk 3/3 | Need 2/2 | History 2/2 = **9/10**

**Decision**: ✅ **ADOPT** — Accurate mapping, no implementation risk.

---

## vet-006: Surface Cache / PVS
| Field | Value |
|-------|-------|
| **Source** | Quake 1996 (Michael Abrash, John Carmack) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake-1996 — Surface Cache / PVS (tiered memory attribution)

**For Analysis**:
- Precomputation of visibility is a valid pattern
- Omega's hot/warm/cold memory tiers (user's own design) already embody this
- Attribution clarifies the design lineage but adds no new code

**Against Analysis**: Tiered memory was the user's independent design. Attribution may over-claim.

**Score**: Python relevance 2/3 | Risk 2/3 | Need 1/2 | History 2/2 = **7/10**

**Decision**: ✅ **ADOPT** — With the caveat that tiered memory is the user's own design. Attribution should say "enhances" not "derives."

---

## vet-007: Worse is Better Philosophy
| Field | Value |
|-------|-------|
| **Source** | Richard P. Gabriel (Lisp), adopted by John Carmack |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: — Worse is Better philosophy (no code-level tags)

**For Analysis**: Pure philosophy. No implementation. Universally applicable.

**Against Analysis**: None.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **10/10**

**Decision**: ✅ **ADOPT**

---

## vet-008: Carmack's Law (Consolidation)
| Field | Value |
|-------|-------|
| **Source** | John Carmack — observed engineering practice |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: — Carmack's Law (no code-level tags)

**For Analysis**: Pure philosophy. Drives circuit breaker consolidation, which was validated.

**Against Analysis**: None.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **10/10**

**Decision**: ✅ **ADOPT**

---

## vet-009: Circuit Breaker Consolidation
| Field | Value |
|-------|-------|
| **Source** | Multiple legacy implementations across eras |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: — Circuit Breaker Consolidation (no code-level tags)

**For Analysis**:
- Consolidated 3 implementations into 1 (AsyncCircuitBreaker)
- Bug fixes proved value: T2.2 (direct provider check), T2.3 (None→TimeoutError)
- Reduces code entropy per Carmack's Law

**Against Analysis**: None — consolidation was clearly beneficial.

**Score**: Python relevance 3/3 | Risk 2/3 | Need 2/2 | History 2/2 = **9/10**

**Decision**: ✅ **ADOPT**

---

## vet-010: ZONEID Constants
| Field | Value |
|-------|-------|
| **Source** | `z_zone.c:33` (DOOM 1993), `zone.c:24` (Quake 1996) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — ZONEID constants

**For Analysis**:
- Magic sentinel for corruption detection is architecture-independent
- Catches use-after-free, double-free, serialization corruption
- Works identically in Python (validate_zoneid())
- Verified against actual id Software source (not secondary sources)

**Against Analysis**: Python doesn't have use-after-free, but serialization corruption is real.

**Score**: Python relevance 2/3 | Risk 3/3 | Need 2/2 | History 2/2 = **9/10**

**Decision**: ✅ **ADOPT**

---

## vet-011: Lazy Deletion with Grace Period
| Field | Value |
|-------|-------|
| **Source** | `p_tick.c:62-103` (DOOM 1993), `pr_edict.c:73-92` (Quake 1996) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993, quake-1996 — Lazy Deletion with Grace Period

**For Analysis**:
- Mark-and-sweep with grace period is a standard concurrent pattern
- O(1) deregistration with safe in-flight operation completion
- 0.5s grace period prevents stale-reference issues
- Verified against actual id Software source

**Against Analysis**: Minor — this is a universal CS pattern, not id Software specific.

**Score**: Python relevance 2/3 | Risk 3/3 | Need 2/2 | History 2/2 = **9/10**

**Decision**: ✅ **ADOPT**

---

## vet-012: Heritage Inline Tag Protocol
| Field | Value |
|-------|-------|
| **Source** | CREDITS.md §2a — original design by Kali/Doom Guy |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: — Heritage Inline Tag Protocol (meta, no code-level tags)

**For Analysis**:
- Process improvement, not code
- Enables CI enforcement (make heritage-map)
- Proven value: found unport items

**Against Analysis**: None.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **10/10**

**Decision**: ✅ **ADOPT**

---

## vet-013: cvar Table
| Field | Value |
|-------|-------|
| **Source** | `cvar.c:24-224` (Quake 1996) + `cvar.c:187-279` (Q3A 1999) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake-1996, quake3-1999 — cvar Table

**For Analysis**:
- Named constants with flags (archive, readonly, latch) are useful in any language
- modificationCount pattern enables change detection
- Cleaner than scattered module-level constants

**Against Analysis**:
- Python doesn't need MAX_CVARS=1024 — we can grow dynamically
- Some features (CVAR_LATCH requiring restart) have no Python equivalent

**Score**: Python relevance 2/3 | Risk 2/3 | Need 1/2 | History 2/2 = **7/10**

**Decision**: ✅ **ADAPT** — Keep the flags/namespace pattern. Remove C-specific constraints (MAX_CVARS, CVAR_LATCH).

---

## vet-014: 4-Tier Memory Architecture
| Field | Value |
|-------|-------|
| **Source** | `zone.h:24-80` (Quake 1996) — Hunk/Zone/Cache/Temp |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake-1996, doom3-2004 — 4-Tier Memory Architecture

**For Analysis**:
- Omega already has 3 tiers (Hot/Warm/Cold)
- Adding 4th "static" tier for long-lived config data
- Temp tier for transient inference results is useful

**Against Analysis**:
- 3 tiers are working. Adding a 4th is speculative.
- Quake's Hunk/Zone split was for memory-limited systems (4MB RAM)
- Omega runs on 14GB RAM — the constraint doesn't exist
- Risk of over-engineering what already works

**Score**: Python relevance 1/3 | Risk 1/3 | Need 1/2 | History 2/2 = **5/10**

**Decision**: ⏸ **DEFER** — 3 tiers work. Only implement if profiling shows a bottleneck.

**Trigger for revisit**: Profiling shows tier contention or memory fragmentation.

---

## vet-015: Multi-Index Entity / Dual-Linking
| Field | Value |
|-------|-------|
| **Source** | `p_mobj.h:1-100` (DOOM 1993) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — Multi-Index Entity / Dual-Linking

**For Analysis**:
- Dual-index lookup (domain + capability) already partially implemented
- O(1) capability discovery is useful for entity routing
- Pattern is clear and well-understood

**Against Analysis**: Already exists in code. Attribution formalizes what's built.

**Score**: Python relevance 2/3 | Risk 2/3 | Need 2/2 | History 1/2 = **7/10**

**Decision**: ✅ **ADOPT** — Already partially built. Complete the capability index population.

---

## vet-016: QuakeC Flat-Field Entity
| Field | Value |
|-------|-------|
| **Source** | `QW/progs/progdefs.h:5-110` (Quake 1996) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake-1996 — QuakeC Flat-Field Entity

**For Analysis**:
- Data-driven entity schema is already what Omega does (YAML entities)
- Flat bag-of-fields pattern is already how entities work

**Against Analysis**:
- Pure observation — Omega already implements this
- No actionable implementation remaining
- Attribution is backwards-looking only

**Score**: Python relevance 2/3 | Risk 2/3 | Need 0/2 | History 0/2 = **4/10**

**Decision**: ⏸ **DEFER** — No actionable implementation needed. Pure documentation.

---

## vet-017: Hard-Boundary Struct
| Field | Value |
|-------|-------|
| **Source** | `g_local.h:42-49` (Q3A 1999) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake3-1999 — Hard-Boundary Struct

**For Analysis**:
- Engine zone vs game zone separation prevents accidental mutation
- Sentinel-based enforcement (__engine_zone__ / __game_zone__)
- Already implemented in entity_registry.py Entity class

**Against Analysis**:
- Python doesn't have the same mutation problem as C (no raw pointer access)
- Sentinel attributes add complexity for marginal benefit
- Q3A's "DO NOT MODIFY" comment was convention, not enforcement — same as Python

**Score**: Python relevance 1/3 | Risk 2/3 | Need 1/2 | History 1/2 = **5/10**

**Decision**: ⏸ **RE-EVALUATE** — Implemented but worth auditing. May be over-engineering.

---

## vet-018: 4-Path Virtual Filesystem
| Field | Value |
|-------|-------|
| **Source** | `files.c:39-75` (Q3A 1999) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake3-1999 — 4-Path Virtual Filesystem

**For Analysis**:
- Search order: home → base → cd is already how WAD loader works
- PWAD override pattern is identical to Omega's WAD stacking

**Against Analysis**:
- Q3A's 4-path system was for CD-ROM distribution — not relevant
- Omega's 2-path (IWAD + PWAD) is sufficient and simpler
- Adding more tiers adds complexity without demonstrated need

**Score**: Python relevance 1/3 | Risk 2/3 | Need 1/2 | History 2/2 = **6/10**

**Decision**: ⏸ **DEFER** — Existing WAD loader is sufficient. Only expand if user stacks need more tiers.

---

## vet-019: High-Bit Leaf Trick
| Field | Value |
|-------|-------|
| **Source** | `doomdata.h:124-138` (DOOM 1993) — NF_SUBSECTOR = 0x8000 |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — High-Bit Leaf Trick

**For Analysis**:
- Using high bit of flags for system marker is a clean pattern
- FLAG_SYSTEM = 0x80000000 saves one boolean field
- Single-bit-check is cheaper than two-field-check

**Against Analysis**:
- In Python, saving one boolean field is negligible (object overhead dominates)
- Pattern works but the "optimization" claim is exaggerated
- Acceptable as an encoding choice, not a performance optimization

**Score**: Python relevance 1/3 | Risk 3/3 | Need 1/2 | History 1/2 = **6/10**

**Decision**: ✅ **ADOPT** — Keep as encoding convention. Drop performance claims from documentation.

---

## vet-020: Fixed-Size Active Set (32)
| Field | Value |
|-------|-------|
| **Source** | `r_bsp.c:74-78` (DOOM 1993) — MAXVISPLANES = 32 |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — Fixed-Size Active Set (32)

**For Analysis**:
- Bounded active set prevents unbounded iteration
- 32 is a reasonable default for active providers

**Against Analysis**:
- DOOM's 32 was because 32 × 8 bytes = 256 bytes = L1 cache line
- Python objects don't fit in L1 cache (each Python object is ~56 bytes minimum)
- The 32 limit is arbitrary in Python context
- Risk of hitting limit with many providers

**Score**: Python relevance 1/3 | Risk 2/3 | Need 1/2 | History 0/2 = **4/10**

**Decision**: ⏸ **DEFER** — Keep the bounded-set pattern. Remove the hard 32 limit. Use dynamic sizing.

---

## vet-021: Network Channel (netchan) Protocol
| Field | Value |
|-------|-------|
| **Source** | `net_chan.c:35-235` (Q3A 1999) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: quake3-1999 — netchan Network Channel Protocol

**For Analysis**:
- OOB messages map to stateless HTTP endpoints — already exists
- Fragmentation maps to streamable chunks — already exists in AnyIO
- qport NAT workaround maps to session_id — already exists in MCP Hub

**Against Analysis**:
- Pure observation — all patterns already exist in Omega independently
- No actionable implementation remaining

**Score**: Python relevance 1/3 | Risk 2/3 | Need 0/2 | History 0/2 = **3/10**

**Decision**: ⏸ **DEFER** — Pure documentation. No code to implement.

---

## vet-022: Unified Memory Allocator (idHeap)
| Field | Value |
|-------|-------|
| **Source** | `Heap.cpp:45-143` (DOOM 3, 2004) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom3-2004 — Unified Memory Allocator (idHeap)

**For Analysis**:
- 3-tier allocator (Small/Medium/Large) maps to Hot/Warm/Cold — already exists
- Defrag Block (big allocation at startup) maps to ResourceGuard — already exists

**Against Analysis**:
- Pure observation — Omega already implements all tiers
- Small-tag allocator (1-255 bytes) has no Python equivalent (Python objects are heap-allocated)
- Attributing existing patterns may over-claim independent design

**Score**: Python relevance 1/3 | Risk 2/3 | Need 1/2 | History 1/2 = **5/10**

**Decision**: ⏸ **DEFER** — Documented as observation. No implementation needed.

---

## vet-023: Fixed-Point Math
| Field | Value |
|-------|-------|
| **Source** | `m_fixed.c:43-87` (DOOM 1993) |
| **Discovery Date** | 2026-06-02 |
| **Vet Date** | 2026-06-04 (retroactive) |
| **Vetter** | Kali (retroactive) |
**[id-soft tags]**: doom-1993 — Fixed-Point Math (quantization)

**For Analysis**:
- Principle: "use integer math when FPU is slow" → "use quantization when FP16 is slow"
- Translation to Q4_K_M / Q8_0 quantization is valid
- Zen 2 AVX2 flags (-mavx2 -mfma) are legitimate optimization

**Against Analysis**:
- The specific 16.16 fixed-point format is 386-specific
- The translation to quantization is a philosophical leap, not a direct mapping
- GPU/CPU now have fast FPU — the constraint is memory bandwidth, not math

**Score**: Python relevance 2/3 | Risk 2/3 | Need 1/2 | History 1/2 = **6/10**

**Decision**: ✅ **ADAPT** — Keep the "right approximation" principle in documentation.
Drop 16.16 fixed-point specifics. The quantization mapping is valid but document as
philosophical, not implementation-level.

---

## Summary
## vet-024: netchan → H-13 (Network Channel Protocol)
| Field | Value |
|-------|-------|
| **Source** | `net_chan.c:35-235` (Q3A 1999) |
| **Discovery Date** | 2026-06-05 |
| **Vet Date** | 2026-06-05 |
| **Vetter** | Doom Guy |
**[id-soft tags]**: quake3-1999 — netchan Message Types

**For Analysis**:
- OOB sequence (-1) $\rightarrow$ Continuation (bypasses state)
- Reliable fragment sequencing $\rightarrow$ Decision (multi-decision thread)
- qport NAT remap $\rightarrow$ Handoff (session_id re-association)
- Connection state machine $\rightarrow$ Ack (state confirmation)

**Against Analysis**:
- The general netchan pattern was deferred (vet-021) as "pure documentation", but the H-13 application is a concrete implementation of the same structural isomorphism.

**Score**: Python relevance 3/3 | Risk 2/3 | Need 2/2 | History 2/2 = **9/10**

**Decision**: ✅ **ADOPT** — The H-13 typed message system is a direct architectural descendant of the netchan protocol.

---

## vet-025: Sovereign-Siloing (Doom 1993)
| Field | Value |
|-------|-------|
| **Source** | `w_wad.c` (DOOM 1993) |
| **Discovery Date** | 2026-06-05 |
| **Vet Date** | 2026-06-05 |
| **Vetter** | Doom Guy |
**[id-soft tags]**: doom-1993 — Sovereign-Siloing

**For Analysis**:
- Absolute separation of engine binary and WAD data.
- Omega Evolution: Strict separation of `src/omega/` and `config/wads/` (Mandate 2).

**Against Analysis**:
- Fundamental architectural principle; no significant risk.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 3/3 | History 3/3 = **10/10**

**Decision**: ✅ **ADOPT** — The Engine-Stack Firewall is the modern instantiation of the WAD silo.

---

## vet-026: Lattice-Culling (Doom 1993)
| Field | Value |
|-------|-------|
| **Source** | `r_bsp.c` (DOOM 1993) |
| **Discovery Date** | 2026-06-05 |
| **Vet Date** | 2026-06-05 |
| **Vetter** | Doom Guy |
**[id-soft tags]**: doom-1993 — Lattice-Culling

**For Analysis**:
- BSP-style pre-computation to skip entire subtrees of non-visible geometry.
- Omega Evolution: O(1) circuit breaker check to skip dead providers before inference.

**Against Analysis**:
- Conceptual translation from geometry to provider health.

**Score**: Python relevance 2/3 | Risk 3/3 | Need 2/2 | History 2/2 = **8/10**

**Decision**: ✅ **ADOPT** — Provider culling is a direct application of the BSP culling principle.

---

## vet-027: Sovereign-Symmetry (Quake 1996)
| Field | Value |
|-------|-------|
| **Source** | `zone.c` (Quake 1996) |
| **Discovery Date** | 2026-06-05 |
| **Vet Date** | 2026-06-05 |
| **Vetter** | Doom Guy |
**[id-soft tags]**: quake-1996 — Sovereign-Symmetry

**For Analysis**:
- Dual-inference / mirrored state for stability and verification.
- Omega Evolution: Ma'at (Light) + Lilith (Dark) synthesis via Kali.

**Against Analysis**:
- Philosophical evolution; less direct than technical mappings.

**Score**: Python relevance 2/3 | Risk 2/3 | Need 2/2 | History 2/2 = **7/10**

**Decision**: ✅ **ADOPT** — The MaKaLi Triad is a cognitive evolution of the mirrored-state stability pattern.

---

## vet-028: Sovereign-Symmetry (Quake III 1999)
| Field | Value |
|-------|-------|
| **Source** | `g_local.h` (Q3A 1999) |
| **Discovery Date** | 2026-06-05 |
| **Vet Date** | 2026-06-05 |
| **Vetter** | Doom Guy |
**[id-soft tags]**: quake3-1999 — Sovereign-Symmetry

**For Analysis**:
- Local-first primary with cloud-fallback safety net.
- Omega Evolution: `native-gguf` $\rightarrow$ `Google` $\rightarrow$ `OpenCode` provider chain (Mandate 7).

**Against Analysis**:
- Practical implementation of the symmetry principle.

**Score**: Python relevance 3/3 | Risk 3/3 | Need 2/2 | History 2/2 = **8/10**

**Decision**: ✅ **ADOPT** — The Dual-Inference Mandate is a direct descendant of the local-first symmetry pattern.

---

## Summary

| Status | Count | Concepts |
|--------|-------|----------|
| ✅ ADOPT | 20 | WAD, BSP, FISR, Zone, Cache, Worse, Carmack, CB, ZONEID, Lazy, Tags, cvar, Multi, High-Bit, Math, netchan-H13, Siloing, Lattice-Cull, Symmetry-MaKaLi, Symmetry-D118 |
| 🔄 ADAPT | 2 | cvar (remove C constraints), Fixed-Point (philosophical only) |
| ❌ REJECT | 1 | 8-Char Name (removed) |
| ⏸ DEFER | 6 | 4-Tier, QuakeC, VFS, ActiveSet, netchan, idHeap |
| ⏸ RE-EVAL | 1 | Hard-Boundary (implemented, borderline) |
| **Total** | **28** | All concepts accounted for |

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ VET_LOG ⬡ v1.0.0*
*Last Updated: 2026-06-05 | Maintained by: Kali / Doom Guy*
