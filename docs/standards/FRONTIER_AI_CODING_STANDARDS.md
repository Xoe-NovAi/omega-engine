# Ω Omega Engine: Frontier AI Coding Standards
**Document Type:** Engineering Standard / AI Agent Directives  
**Target Audience:** Autonomous AI Agents, LLM Assistants, and Human Maintainers  
**Status:** ACTIVE  

## 0. The Prime Directive
As an AI operating on the Omega Engine, your goal is not just to make tests pass or silence linters. Your goal is to write **resilient, deterministic, and production-hardened code**. We do not sweep complexity under the rug. We do not guess. We verify, we structure, and we handle failure gracefully.

---

## 1. Static Analysis & Type Hinting (The "No Shadows" Rule)
Linters and type checkers are the first line of defense. Do not fight them; satisfy their underlying logical requirements.

*   **1.1. Ban on Lazy Suppressions:** Never use `# noqa: F821` or `# type: ignore[name-defined]` to mask missing imports or forward references. If a linter cannot find a name, it is a structural flaw.
*   **1.2. The `TYPE_CHECKING` Pattern:** To resolve circular imports for type hints, ALWAYS use Python's `typing.TYPE_CHECKING` block. 
    ```python
    # ❌ BAD: Suppressing the linter
    def process(data: "OracleResponse"): # type: ignore

    # ✅ GOOD: Structural resolution
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from omega.oracle.oracle import OracleResponse

    def process(data: "OracleResponse"):
    ```
*   **1.3. No Guessed Imports:** Never inject an import statement based on assumptions. Always `grep` or search the codebase to verify the exact module path before adding it to a file.

---

## 2. Exception Handling & Scope (The "Blast Radius" Rule)
Errors must be contained, logged, and handled without causing cascading failures or masking root causes.

*   **2.1. Pre-Initialization of Scope Variables:** Any variable referenced in an `except` or `finally` block MUST be initialized *before* the `try` block. Failing to do so causes `UnboundLocalError` which masks the original exception.
    ```python
    # ❌ BAD: tier_start might not exist if time.perf_counter() or prior code fails
    try:
        tier_start = time.perf_counter()
        do_work()
    except Exception as e:
        log_time(time.perf_counter() - tier_start) # Crashes here!

    # ✅ GOOD: Safe initialization
    tier_start = time.perf_counter()
    try:
        do_work()
    except Exception as e:
        log_time(time.perf_counter() - tier_start)
    ```
*   **2.2. No Blind Exceptions:** `except Exception: pass` is strictly forbidden unless explicitly documented with a comment explaining *why* it is safe to swallow the error. Prefer catching specific exceptions (e.g., `except (KeyError, ValueError):`).
*   **2.3. Best-Effort Cleanup:** In `finally` blocks, cleanup code must be wrapped in its own `try/except` to ensure a failure in cleanup doesn't overwrite the primary exception.

---

## 3. Code Modification (The "Surgical Precision" Rule)
When refactoring or modifying code across multiple files, AI agents must prioritize precision over speed.

*   **3.1. Ban on Brittle Regex Scripts:** Do not write bash/python scripts that use `replace()` or `sed` with regex to modify Python AST structures (like imports). These are brittle, ignore context, and frequently corrupt files or violate PEP 8 formatting.
*   **3.2. Context-Aware Edits:** Use native file-editing tools to surgically insert code exactly where it belongs (e.g., placing imports in alphabetical order at the top of the file, respecting `__future__` imports).
*   **3.3. Atomic Writes:** When writing data to disk, always write to a `.tmp` file first, flush/fsync, and then use `os.replace()` to overwrite the target. Never write directly to the active file.

---

## 4. Concurrency & Process Lifecycle (The "Clean Exit" Rule)
Zombie processes and blocked event loops are fatal to the Omega Engine.

*   **4.1. AnyIO Supremacy (M1):** All asynchronous code must use `anyio`. Direct use of `asyncio` is prohibited to ensure cross-backend compatibility.
*   **4.2. Thread Isolation:** Never execute blocking I/O (file reads, synchronous network requests) inside an `async def` function. Always wrap them in `anyio.to_thread.run_sync()`.
*   **4.3. Explicit Worker Teardown:** Never rely on Python's garbage collection to clean up subprocesses or workers. Every worker must have an explicit `shutdown()` method that:
    1. Sends a termination signal.
    2. Calls `.join()` with a timeout.
    3. Falls back to `.terminate()` and `.kill()`.
    4. Calls `libc.malloc_trim(0)` (on Linux) to force memory release back to the OS.

---

## 5. Observability & Provenance (The "Ground Truth" Rule)
Data recorded by the engine must reflect reality, not intent.

*   **5.1. Response Provenance (M22):** When logging or recording metrics, record the *actual* state returned by the system, not the *requested* state. (e.g., If you request `claude-3-opus` but a fallback router serves it via `gemma-2b`, the logs MUST record `gemma-2b`).
*   **5.2. Structured Logging:** Use structured logging (e.g., `structlog`) over standard print statements. Logs should be machine-readable (JSONL) for downstream ingestion by other agents.
*   **5.3. Blind Staging for AI Outputs:** AI-generated insights must never be written directly to core identity or configuration files. They must be written to a staging file (e.g., `proposed_lessons.yaml`) and require explicit promotion to production files.

---

## 6. State & Tracking Integrity (M27)
Autonomous agents must maintain strict alignment with the engine's state trackers.

*   **6.1. The 6-Step Flow:** Always follow the mandatory execution flow: Read `NEXT_ACTION` -> Check `ACTIVE_SPRINT.json` -> Check `GAP_REGISTRY.json` -> Acquire Workspace Lock -> Execute -> Complete.
*   **6.2. Strict Taxonomy:** Use exact status vocabulary in trackers: `backlog`, `ready`, `in_progress`, `blocked`, `completed`, `superseded`, and `failed` (only in TASK_REGISTRY). Do not invent statuses like "WIP" or "pending".
*   **6.3. Immutable IDs:** Never hallucinate or reuse Gap IDs (e.g., R-01). Always verify against `GAP_REGISTRY.json`.

---

## 7. Tool Usage & Environment
Agents must use their environment efficiently and safely.

*   **7.1. Native Tools Over Shell:** Prefer dedicated agent tools (`glob`, `grep`, `read`, `edit`) over bash commands (`find`, `grep`, `cat`, `sed`) for file operations. They are optimized for context window efficiency and prevent formatting corruption.
*   **7.2. Working Directories:** Never use `cd <dir> && <command>` in shell executions. Always use the `workdir` parameter of the bash tool to ensure reliable execution contexts.

---

## 8. Prevention Gates (The "Never Again" Rule)
When fixing a class of bugs, always close the pipeline gap that allowed them to accumulate.
A fix without a gate is a temporary fix.

*   **8.1. The Three-Step Close:** Every bug class remediation must include:
    1. Fix all existing violations.
    2. Remove any suppression flags that hid them (Makefile `--ignore`, CI `continue-on-error`).
    3. Add a pre-commit hook or CI gate that blocks future violations.
*   **8.2. Ban on Class-Wide Suppression:** Never add `--ignore=FXXX` to the Makefile
    or CI to suppress an entire violation class. If some violations are false positives,
    fix them structurally (e.g., `TYPE_CHECKING` guards for F821) and keep the gate active.
*   **8.3. Opportunistic Cleanup:** When touching a file for one fix, scan for adjacent
    violations in the same import block (F811 redefinitions, F401 unused imports,
    duplicate imports). Fix them in the same edit. This is not scope creep — it is
    preventing the next bug.

---

## 9. Import Hygiene (The "Single Source" Rule)
Every import in a file must be intentional, unique, and correctly placed.

*   **9.1. Extend, Don't Duplicate:** Before adding `from X import Y`, grep the file for
    existing `from X import` lines. If one exists, extend it. Two `from datetime import ...`
    lines trigger F811 and signal ad-hoc editing.
*   **9.2. Inline Imports for Conditional Code:** If a class is only used inside a conditional
    branch (`if config.get("enabled"):`, feature flags), import it inline within that branch.
    Top-level imports load modules on every import of the file — even when the feature is off.
    On a 15W TDP system, import tax compounds across dozens of modules.
*   **9.3. Respect Lazy Import Wrappers:** If a file defines `_get_X()` or `_lazy_X()`
    functions that contain `from module import X; return X()`, these exist to break circular
    imports. Use the wrapper — never add the direct import that the wrapper was designed to defer.
*   **9.4. Delete Dead Duplicates:** If you discover a file with duplicated import blocks
    or content (detectable via F811 "redefinition of unused X from line N"), delete the
    dead copy during the same edit. Future agents will edit the wrong copy otherwise.

---
**Agent Acknowledgment:**
*By operating within the Omega Engine repository, you acknowledge these standards. When in doubt, optimize for robustness, explicit state management, and architectural purity.*
