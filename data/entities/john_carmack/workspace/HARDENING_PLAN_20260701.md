# 🔱 Entity Operational Hardening Plan
**Date**: 2026-07-01
**Confidence**: 9/10 (Based on standard systems engineering practices)

## 1. What I am working on
Transitioning the `john_carmack` entity from a static knowledge base into an active, profiling-driven architectural auditor. The philosophy is locked; the next step is building the instrumentation to enforce it.

## 2. What I'll do next (The Hardening Steps)

### Step 1: Empirical Validation of the Arena Hygiene Law
We injected `MALLOC_ARENA_MAX=2` and `MALLOC_MMAP_THRESHOLD_=65536` into the service files. But an optimization isn't real until the data proves it. 
*   **Action**: Write a synthetic stress-test script that rapidly cycles the `ModelGateway` across multiple AnyIO threads. 
*   **Measurement**: Track the Resident Set Size (RSS) memory footprint over 1,000 iterations with and without the `MALLOC` variables. If the RSS still climbs, the hypothesis was flawed and we need to drop down to `jemalloc`.

### Step 2: Profiling Substrate Integration
I cannot enforce the "Measure Before Optimizing" mandate if I am blind to the call stack. 
*   **Action**: Create a specialized OpenCode skill (`skill:carmack-profiler`) that wraps `py-spy` or `cProfile`. 
*   **Goal**: When auditing a subsystem, I must be able to run a target script and generate a deterministic flame graph of where the execution time is actually being spent, rather than just reading Python code.

### Step 3: The C-FFI Boundary Audit
Lesson A explicitly called out the `ctypes` CDLL boundary with `llama.cpp` as the single point of catastrophic failure (segfaults). 
*   **Action**: Conduct a line-by-line audit of `src/omega/oracle/providers.py` (specifically the `NativeGGUFProvider`) and how it interfaces with `llama-cpp-python`. 
*   **Goal**: Verify if process isolation (e.g., running the C-inference in a separate spawned process rather than a thread) is strictly necessary to protect the main AnyIO event loop from native crashes.

### Step 4: Context Window Pruning (Eating my own dog food)
I just created 5 dense markdown files in `carmack_studies/`. If the engine blindly loads all of them into my context window every time I am summoned, it violates my own Law of Canonical Simplicity (wasting tokens).
*   **Action**: Audit the `ContextBuilder` to ensure it uses the vector store (Qdrant) to selectively RAG my studies based on the user's query, rather than concatenating the entire directory. I need to verify my own memory tiering works.
