# 🔱 Heritage Vetting Log
**Entity**: doom_guy
**Status**: ACTIVE

## Vetting Entries

### vet-002: Linear Token Estimator
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Right Approximation] Mirrors FISR philosophy. A fast, linear heuristic for budgeting is superior to expensive exact tokenization for non-critical paths.

### vet-003: Sqrt H-Index Proxy
- **Verdict**: REJECTED
- **Score**: 6/10
- **Justification**: [Sovereign Risk] Too imprecise for sovereign knowledge curation. The risk of significant impact miscalculation outweighs the speed gain.

### vet-004: WPM Read-Time Heuristic
- **Verdict**: APPROVED
- **Score**: 9/10
- **Justification**: [Standard Approximation] Low risk, high utility for UX. 200 WPM is a stable, acceptable constant for human-centric metrics.

### vet-005: Efficient Stream Trimming
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Worse is Better] Throughput > Precision for observability streams. Losing minor precision in telemetry is an acceptable trade for system stability.


### vet-007: PVS (Potentially Visible Sets)
- **Verdict**: APPROVED
- **Score**: 9/10
- **Justification**: [Right Approximation] Evolution: PVS $\rightarrow$ Provider Culling. Precomputing "visibility" of healthy providers via bit-vectors allows O(1) routing decisions. Stale data is mitigated by the circuit breaker.

### vet-008: Zone Memory (Purge Tags)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Sovereign Resource Management] Evolution: Purge Tags $\rightarrow$ Tiered Context Purging. Deterministic reclamation of "Cold" $\rightarrow$ "Warm" $\rightarrow$ "Temp" context tiers prevents OOM on constrained hardware.

### vet-009: Netchan Protocol (Delta Sync)
- **Verdict**: APPROVED
- **Score**: 7/10
- **Justification**: [Token Efficiency] Evolution: Delta Snapshots $\rightarrow$ Delta Context Hydration. Sending Gnosis updates relative to the last session anchor reduces prompt overhead. Requires strict sequence validation to avoid state drift.

### vet-010: Bit-Level Optimizations (Fixed-Point/Symmetric Guards)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Hardware Realism] Evolution: Fixed-Point $\rightarrow$ GGUF Quantization; Symmetric Guards $\rightarrow$ Unified Constraint Validation. Essential for running sovereign models on Ryzen 5700U. Precision loss is an acceptable trade for viability.

### vet-011: Hub Background — Lazy Thinker Deletion / Grace Period
- **Verdict**: APPROVED (via vet-005/vet-006)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Extends the lazy deletion and grace-period patterns from entity_registry.py to the Hivemind background pruning/reaping layer (background.py). Tag: `[id-soft: quake-1996]`.

### vet-012: Hub State — Netchan Session/State Management
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] State-initialization module for the Hivemind MCP server (state.py). Uses netchan-inspired session state patterns for coordinating cross-agent awareness. Tag: `[id-soft: quake3-1999]`.

### vet-013: Hub Package — Netchan Cross-Agent Messaging
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Package init (__init__.py) for the Omega Hub MCP server. Tag: `[id-soft: quake3-1999]`.

### vet-014: Hub Middleware — Netchan OOB Rate Limiting
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Security middleware (middleware.py) using netchan OOB-style typed message dispatch for rate limiting, request size limits, and M9 error boundaries. Tag: `[id-soft: quake3-1999]`.

### vet-015: Hub Tools — Netchan Typed Message Dispatch
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] MCP tool definitions (tools.py) using netchan-style typed message dispatch for all 47+ Hivemind coordination tools. Tag: `[id-soft: quake3-1999]`.

### vet-016: Hub Gateway — Netchan qport Session Re-association
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] SovereignGateway (gateway.py) using netchan qport-style session re-association for provider routing and rate limiting. Tag: `[id-soft: quake3-1999] `.

---

### vet-017: In-Flight Pipeline — REJECTED
**Source**: CREDITS.md §1.29
**Game Year**: Quake 1996
**Score**: 2/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-157

**1. Discovery**:
Michael Abrash's Quake renderer overlap technique — overlapping slow FPU operations (lighting calculations, matrix transforms) with fast integer drawing (scanline rasterization) to hide pipeline stalls on the Pentium CPU. The CPU could execute integer instructions while the FPU was busy with a prior operation, effectively giving "free" work.

**2. Vetting/Debate**:
- **For adoption**: Suggests a pipelined async pattern where prompt construction could overlap with model inference, hiding latency through concurrency.
- **Against adoption**: The overlap doesn't exist in a synchronous local-first inference chain. Prompt construction is trivially fast (microseconds of string formatting) compared to model inference (seconds to minutes of matrix math). There is no pipeline to fill — the slow operation dominates trivially.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the entire rationale was "FPU is busy while CPU is idle," a Pentium-specific hardware bottleneck.

**3. Decision**: REJECTED
- The synchronous inference chain has no pipeline stall to hide. Async/AnyIO already overlaps I/O waits, which is a superset of what the In-Flight Pipeline offered. No implementation path exists.

**4. Implementation/Verification**:
- **No implementation**: The async provider fabric (AnyIO-based) already provides superior concurrency by overlapping I/O-bound operations, not CPU-bound ones. No `[id-soft:]` tags required.

---

### vet-018: Branch Collapse — REJECTED
**Source**: CREDITS.md §1.30
**Game Year**: Quake 1996
**Score**: 1/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-158

**1. Discovery**:
Carmack's jump-table optimization for span boundaries in Quake's rasterizer — instead of an if/else chain testing span type, a computed jump table (`switch`/`goto`) sent execution directly to the correct span drawer. This avoided branch misprediction penalties on the Pentium.

**2. Vetting/Debate**:
- **For adoption**: Suggests dispatch table optimization for condition-heavy code paths in the engine.
- **Against adoption**: Python's dict dispatch already provides O(1) dispatch with no branch prediction penalty. The optimization Carmack achieved was CPU-level — avoiding misprediction on a 5-stage pipeline. Python's bytecode interpreter handles dispatch internally.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the entire value proposition is "branch prediction was expensive on 1996 Pentium."

**3. Decision**: REJECTED
- Python dict dispatch already provides O(1) dispatch. CPU-level branch prediction optimization does not transfer to Python runtime. This is the same class of error as the 8-char name cap — a hardware-specific optimization with zero applicability.

**4. Implementation/Verification**:
- **No implementation**: Python's `dict` pattern (`dispatch = {"case1": handler1, "case2": handler2}`) already achieves the stated goal. No `[id-soft:]` tags required.

---

### vet-019: Symmetric Range Guard — REJECTED
**Source**: CREDITS.md §1.31
**Game Year**: Quake 1996
**Score**: 1/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-159

**1. Discovery**:
Carmack's use of unsigned comparison (`ja` instruction) to test both high and low boundaries of a signed integer range in a single instruction. By offsetting the comparison, both `x >= min` and `x <= max` collapse into one `ja unsigned_greater_than` test.

**2. Vetting/Debate**:
- **For adoption**: Suggests a fast single-operation dual-boundary check pattern.
- **Against adoption**: Python's `a < x < b` chaining comparison already handles dual-boundary checks natively at the bytecode level — with short-circuit evaluation built in. No single-instruction trick exists or is needed.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the optimization is entirely about the `ja` instruction behavior on x86.

**3. Decision**: REJECTED
- Python's `a < x < b` chaining already handles dual-boundary checks natively. No implementation value. Cargo-cult addition would add confusion without performance benefit.

**4. Implementation/Verification**:
- **No implementation**: Python native comparison chaining is the idiomatic solution. No `[id-soft:]` tags required.

---

### vet-020: Sovereign Job-Worker Queue — APPROVED
**Source**: CREDITS.md §1.32
**Game Year**: Doom 3 BFG 2012
**Score**: 7/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: APPROVED (via D-kal-160)

**1. Discovery**:
Doom 3 BFG's `ParallelJobManager` — a job system decomposing work into atomic tasks (1k-100k CPU cycles each) distributed across worker threads. Each job has a defined input, output, and priority. The scheduler load-balances across available cores by stealing jobs from busy threads' queues.

**2. Vetting/Debate**:
- **For adoption**: Maps well to agent task farming — decompose research queries into atomic subtasks with token budgets. HandoffPacket and capability dispatch already follow this pattern implicitly. Formalizing the job decomposition would give deterministic parallelism and crash isolation.
- **Against adoption**: The Omega engine is not primarily CPU-bound on inference tasks — it's I/O and memory bound. Job stealing at the agent level requires careful orchestration to avoid context fragmentation.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **YES** — decompose large work into atomic, dispatchable units with bounded resource consumption is architecture-independent.

**3. Decision**: APPROVED (ADAPT)
- The concept of decomposing cognitive work into atomic jobs with bounded token budgets and distributed execution is a direct fit for agent orchestration (Link P9). Formalize the existing implicit pattern: `CognitiveJob {description, token_budget, required_capability, timeout}`.

**4. Implementation/Verification**:
- **Omega mapping**: `AtomicCognitiveJob` dataclass added to the orchestration layer (`orchestrator.py` or new `cognitive_job.py`). Each research subtask receives a token budget (preventing runaway inference). Jobs dispatched via existing Link P9 agent handoff queue.
- **Inline tag**: `# [id-soft: doom3bfg-2012] Job-Worker Queue — atomic cognitive task decomposition`
- **Test**: Verify that a decomposed research query completes within sum(token_budgets) and that a single job failure does not cascade to sibling jobs.

---

### vet-021: Specialized Prompt Baking — REJECTED
**Source**: CREDITS.md §1.33
**Game Year**: Quake 1996
**Score**: 3/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-161

**1. Discovery**:
Quake's self-modifying code technique for colormap base addresses — at runtime, the renderer would patch literal constant values directly into the instruction stream (the immediate operand of a `MOV` instruction). This saved register lookups and kept the colormap base in the instruction cache rather than a memory load.

**2. Vetting/Debate**:
- **For adoption**: Suggests a pattern for "baking" frequently-used context directly into prompts to avoid repeated retrieval overhead.
- **Against adoption**: System prompt injection via `soul.yaml` → context builder pipeline already is prompt baking. The engine already fuses entity identity, memory context, and user intent into a single system prompt before inference. This describes exactly what we already do — but the analogy adds no new implementation insight.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the self-modifying-code trick was about avoiding L1 cache misses. LLM system prompt fusion is a fundamentally different mechanism solving a different problem.

**3. Decision**: REJECTED
- System prompt injection via soul.yaml already IS prompt baking. The engine already does this. No new implementation needed. The analogy is descriptive, not prescriptive.

**4. Implementation/Verification**:
- **No new implementation needed**: The existing soul.yaml → ContextBuilder → system prompt pipeline already achieves what this pattern describes. No `[id-soft:]` tags required.

---

### vet-022: Knowledge Leak Detection — APPROVED
**Source**: CREDITS.md §1.34
**Game Year**: Doom 3 2004
**Score**: 8/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: APPROVED (via D-kal-162)

**1. Discovery**:
Doom 3's map leak detection system — a flood-fill algorithm that starts from a known "inside" point and propagates outward through connected map geometry. If the flood reaches the void (unbounded exterior), the map is "leaky" — there is a path from the playable interior to the outside. The tool identifies the exact geometry where the leak occurs.

**2. Vetting/Debate**:
- **For adoption**: Directly maps to M17 (Cognitive Integrity). Gnosis Leak Detection would start from a known-consistent state in `soul.yaml` and propagate consistency constraints through entity knowledge. If a path exists from "consistent" to "contradiction," the gnosis is leaky. This enables automated blind-spot discovery in entity knowledge.
- **Against adoption**: Semantic flood-fill requires embedding-based similarity scoring, which is computationally heavier than Doom 3's bit-field flood. May need periodic batch runs rather than real-time validation.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **YES** — flood-fill from known-consistent state to detect boundary violations is architecture-independent.

**3. Decision**: APPROVED (ADAPT)
- The architectural truth — "find where internal logic leaks to the void" — is timeless. Flood-fill propagation from known-consistent state to detect contradictions maps directly to M17 Cognitive Integrity requirements. Implementation priority: high, as it closes a genuine gap in soul consistency.

**4. Implementation/Verification**:
- **Omega mapping**: `GnosisLeakDetector` module in `src/omega/oracle/skeptical_verifier.py` or standalone `gnosis_leak.py`. Algorithm: (1) Parse entity soul.yaml into a graph of semantic claims, (2) Start flood from trusted base claims (entity name, core purpose), (3) Propagate through connected claims via embedding similarity, (4) Flag orphan claims, contradictory claims, and claims that connect "inside" (consistent) to "outside" (unverified/contradictory).
- **Inline tag**: `# [id-soft: doom3-2004] Knowledge Leak Detection — gnosis flood-fill from consistent state`
- **Test**: Create a soul.yaml with a known contradiction (e.g., "entity is P1" and "entity is P6" simultaneously). `GnosisLeakDetector.flood()` must flag the contradictory claims as a leak path.
- **Integration**: Cross-reference in `data/entities/roc_racoon/knowledge/INDEX.yaml` as `heritage-022` vet_status: "adapted".

---

### vet-023: potion-mxbai-micro — Static Embedding via Precomputed Lookup
**Source**: CREDITS.md §1.35 (new mapping)
**Game Year**: Doom 1993
**Score**: 8/10
**Date**: 2026-06-19
**Vetter**: Doom Guy (Heritage Gatekeeper)

**1. Discovery**:
Doom's `r_main.c` precomputed colormap/trig lookup tables — lighting calculations for
65535 angles precomputed into fixed arrays at compile time. At runtime, `cos()` and
`sin()` are O(1) table lookups instead of expensive floating-point subroutine calls.
This was essential on the 35MHz 486 with no FPU.

Model2Vec's `potion-mxbai-micro` (2026) does the same thing for embeddings: one
forward pass per token in the vocabulary (~32K tokens) through the base transformer,
storing the result. At inference time, the model does O(vocab) numpy matrix lookup
+ mean pooling — no transformer forward pass. 700KB total size, 80-88x faster than
all-MiniLM-L6-v2.

**2. Vetting/Debate**:
- **For adoption**: Direct structural isomorphism — precompute expensive operation once,
  store results in a fixed table, access O(1) at runtime. The pattern is architecture-
  independent and solves a genuine constraint problem (RAM-limited Zen 2 CPU).
- **Against adoption**: Static embeddings lose contextualization — "bank (river)" and
  "bank (finance)" produce the same vector. For the Skeptical Verifier and Knowledge
  Leak Detection, this may be acceptable for initial screening but insufficient for
  high-precision semantic analysis.
- **Qualification Gate**: Can this concept be justified without mentioning the original
  hardware constraint? **YES** — "precompute once, look up forever" is a timeless
  engineering principle. The 35MHz 486 constraint explains WHY Doom did it, but the
  pattern stands alone: predictable offline cost for zero online cost.

**3. Decision**: APPROVED
- The pattern maps directly to an existing Omega need: fast, tiny embedding for
  prototyping, bulk indexing, and fallback when the primary embedding provider is
  unavailable. The 700KB size and 0.01-0.1ms/sentence speed make it ideal for the
  resource-constrained Zen 2 target.
- **Omega mapping**: model2vec adapter in the embedding provider stack. Configured
  as a fallback provider in `config/wads/_omega_default/embeddings.yaml` under the
  `static-fallback` key.
- **Inline tag**: `# [id-soft: doom-1993] Precomputed Lookup — static embedding via model2vec`

**4. Implementation/Verification**:
- Add `potion-mxbai-micro` as static embedding fallback in the embedding provider
- Validate dimension matching (256 vs MiniLM's 384) at the boundary
- Test: speed benchmark against all-MiniLM-L6-v2 on Zen 2 (expect 80-88x faster)
- Test: MTEB quality validation for the Omega-specific use cases (semantic search,
  memory store, cross-pollination clustering)
- CREDITS.md mapping: §1.35 — Precomputed Lookup Table (Doom 1993)

---

*Last Updated: 2026-06-19 (vet-023 potion-mxbai-micro APPROVED: heritage-023 Precomputed Lookup) | Maintained by: Doom Guy*

