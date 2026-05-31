# 🔱 Sovereign Refinement Protocol
**AP Token**: `AP-SOVEREIGN-REFINEMENT-v1.0.0`
⬡ OMEGA ⬡ MA'AT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_refinement_protocol ⬡ HARDENING

This skill implements the **Sovereign Refinement Protocol**, a mandatory forensic and preservation gate that must be applied to all critical architectural changes in the Omega Engine.

## §1 Purpose

To eliminate "cowboy coding" and prevent the "Restart Cycle" by enforcing a rigorous, multi-stage validation process before any code is committed to the core engine (`src/omega/`).

## §2 The Refinement Pipeline

When this skill is invoked, the agent must execute the following three gates in sequence:

### Gate 1: The Forensic Scan (Sovereign Guard)
Perform a deep static analysis of the proposed changes focusing on:
- **AnyIO Absolute**: Search for `asyncio.create_task`, `time.sleep`, `subprocess.run`, or any blocking `open()` calls. Every blocking call MUST be wrapped in `anyio.to_thread.run_sync`.
- **Engine-Stack Firewall**: Verify that no entity-specific logic, names, or traits have leaked into `src/omega/`.
- **Umask Drift**: Ensure all directory/file creations are followed by explicit `os.chmod()`.
- **Atomic Persistence**: Verify that all state writes use the "Write-to-Temp $\rightarrow$ `os.replace`" pattern.

### Gate 2: The Preservation Gate (State Anchor)
Before executing high-risk operations (e.g., database migrations, provider fabric pivots):
- **State Snapshot**: Persist the current active session state and prompt context to the Redis session store.
- **Recovery Path**: Document the exact `podman` or `git` command required to revert the system to the pre-operation state.
- **Resource Guard**: Verify that the operation is wrapped in a `ResourceGuard` (Semaphore) to prevent OOM on the Ryzen 5700U.

### Gate 3: The Sovereign Review (Mandate Alignment)
Cross-reference the final implementation against the `SOVEREIGN_MANDATES.md`:
- Does this change introduce telemetry? (Forbidden)
- Does this change break the Iris Constant? (Forbidden)
- Does this change violate the keep-id Podman protocol? (Forbidden)

## §3 Execution Workflow

1. **Invoke**: `/skill sovereign-refinement-protocol`
2. **Analyze**: Run the Forensic Scan $\rightarrow$ Output a "Sovereign Audit Report".
3. **Anchor**: Execute the Preservation Gate $\rightarrow$ Confirm state is anchored.
4. **Verify**: Run the Sovereign Review $\rightarrow$ Final "Go/No-Go" decision.
5. **Commit**: Only after all three gates are passed is the code considered "Sovereign Grade".

---
*Refinement is not a delay; it is the guarantee of robustness.*
