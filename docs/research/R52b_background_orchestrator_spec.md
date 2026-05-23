# 🔱 Omega Engine — Background Orchestrator Specification
## R-52b: "Phone-a-Friend" Sovereign Background Orchestration

**AP Token**: `AP-Sovereign-Orch-v1.0.0`
**Status**: PROPOSED / IMPLEMENTATION-READY
**Target Implementation Agent**: MiniMax M2.5 (High SWE-bench)
**Priority**: 🔴 Critical (Blocks "Living World" Vision)

---

## §1 Executive Summary

The **Background Orchestrator** is a sovereign concurrency layer designed to transform the Omega Engine from a request-response chat interface into an autonomous research engine. It enables the execution of complex, multi-stage research tasks in the background, leveraging a pool of 8 OpenRouter API keys to bypass rate limits and employing a "Phone-a-Friend" routing model to ensure high-fidelity outputs through cross-model verification.

### Core Objectives
1. **Parallelism**: Execute up to 8 concurrent LLM calls using `anyio.TaskGroup` and `Semaphore(8)`.
2. **Sovereign Routing**: Assign specialized roles (Lead Researcher, Reviewer, Fact Checker) to the best available free-tier models.
3. **Verification Loop**: Implement a mandatory "Reviewer" gate before any background finding is committed to the permanent knowledge base.
4. **Automated Recording**: Seamlessly pipe accepted findings from the worker to the Omega Library and into structured research documents.

---

## §2 Architecture: The `BackgroundWorker`

The `BackgroundWorker` should be implemented as a singleton or a managed component within the `Orchestrator` (`src/omega/oracle/orchestrator.py`).

### Class Specification: `BackgroundWorker`

```python
class BackgroundWorker:
    """
    Manages a pool of concurrent background research tasks.
    Ensures rate-limit compliance via a key-rotating semaphore.
    """
    def __init__(self, api_keys: List[str]):
        self.keys = api_keys  # Pool of 8 OpenRouter keys
        self.semaphore = anyio.Semaphore(len(api_keys))
        self.key_index = 0
        self.active_tasks: Dict[str, anyio.Task] = {}

    async def _get_next_key(self) -> str:
        """Round-robin key rotation."""
        key = self.keys[self.key_index]
        self.key_index = (self.key_index + 1) % len(self.keys)
        return key

    async def submit_task(self, task_id: str, role: str, prompt: str, context: str = ""):
        """
        Submits a task to the background group.
        Returns a future/task handle.
        """
        # Implementation using anyio.TaskGroup
        pass

    async def _execute_with_retry(self, role: str, prompt: str, context: str, retries: int = 2):
        """
        The core execution loop:
        1. Acquire semaphore
        2. Get rotated key
        3. Call ProviderFabric with the model assigned to 'role'
        4. Handle rate limits with exponential backoff
        """
        pass
```

### Concurrency Model
- **Runtime**: `anyio.TaskGroup` for structured concurrency.
- **Throttling**: `anyio.Semaphore(8)` ensures exactly 8 concurrent requests, matching the key pool size.
- **Key Rotation**: Round-robin selection of keys from `.env` to maximize throughput across 8 distinct quotas.

---

## §3 "Phone-a-Friend" Routing Map

Based on the May 16, 2026 Model Catalog, the following routing map is mandated for the background fabric:

> **Note**: This spec is superseded by the Jem 2.0 Speculative Decoding Pipeline (`docs/research/JEM_SPECULATIVE_DECODING_PIPELINE.md`). The model assignments below have been rearchitected into a 3-tier pipeline where Gemma 4 31B is the primary researcher (Tier 1) and the "Phone-a-Friend" routing map now applies to Tiers 2 and 3 via the split test framework.

| Role | Model | Provider | Responsibility |
|------|-------|----------|----------------|
| **Lead Researcher (Jem 2.0)** | `google/gemma-4-31b-it` | Google AI Studio | Deep dive, exhaustive research, initial drafting (Tier 1) |
| **Reviewer / Fact Checker** | Split test (A: Gemma 4 31B, B/D: `kilo/deepseek/deepseek-v4-flash:free`) | Google / OpenCode Zen | Verification, citation check, gap detection (Tier 2) |
| **Synthesizer / Strategist** | Split test (A/B: Gemma 4 31B, C/D: DeepSeek V4 Flash) | Google / OpenCode Zen | Strategic integration, knowledge gap dispatch (Tier 3) |

---

## §4 The Verification Loop (The Gate)

No background output is committed directly to `docs/research/`. It must pass through the **Verification Loop**.

### Loop Logic
1. **Drafting**: `Lead Researcher` generates a finding $\rightarrow$ `Draft_Response`.
2. **Review**: `Draft_Response` is passed to a `Reviewer` (Role depends on content: Code $\rightarrow$ Code Reviewer, Fact $\rightarrow$ Fact Checker).
3. **Judgment**:
   - **ACCEPTED**: Proceed to Recording Pipeline.
   - **REJECTED**: Reviewer provides specific critical feedback $\rightarrow$ `Draft_Response` is sent back to `Lead Researcher` for revision.
4. **Termination**: Max 2 revision cycles. If still rejected, the task is marked as `UNCERTAIN` and flagged for human (Architect) review.

### Reviewer Prompt Template
```markdown
SYSTEM: You are the Omega Sovereign Reviewer. Your goal is to ensure absolute technical accuracy and alignment with the Omega Engine's local-first, sovereign architecture.

INPUT:
- Original Task: {task_prompt}
- Proposed Finding: {draft_response}

CRITERIA:
1. Is the information factually correct?
2. Does it introduce any "Temple Grade" cruft or cloud-dependencies?
3. Is the logic sound and implementation-ready?

RESPONSE FORMAT:
- JUDGMENT: [ACCEPTED | REJECTED]
- REASONING: <Concise explanation of flaws or confirmation of accuracy>
- SUGGESTIONS: <Specific changes required for acceptance>
```

---

## §5 Recording Pipeline

Once a response is `ACCEPTED`, it follows the automated recording path:

**`Accepted Response` $\rightarrow$ `Library Store` $\rightarrow$ `Research Doc`**

1. **Library Store**: 
   - The response is passed to `src/omega/library/indexer.py`.
   - It is indexed as a "Background Discovery" with metadata: `{trace_id, lead_model, reviewer_model, timestamp}`.
2. **Research Doc**:
   - The `BackgroundWorker` identifies the target research file (e.g., `docs/research/R52b_...md`).
   - It appends the finding under a `## Background Discoveries` section using a standardized template:
     ```markdown
     ### Discovery: [Short Title]
     - **Source**: Lead Researcher ({model}) / Verified by {reviewer}
     - **Timestamp**: {ISO_DATE}
     - **Finding**: {content}
     ```

---

## §6 Implementation Roadmap for MiniMax M2.5

1. **Phase 1: Core Worker**: Implement `BackgroundWorker` class with `anyio.TaskGroup` and `Semaphore(8)` in `src/omega/oracle/orchestrator.py`.
2. **Phase 2: Key Rotation**: Wire `.env` key pool into the worker's rotation logic.
3. **Phase 3: Routing & Loop**: Implement the "Phone-a-Friend" map and the `Lead $\rightarrow$ Reviewer $\rightarrow$ Lead` loop.
4. **Phase 4: Recording**: Integrate with `Indexer` and implement the markdown appending logic.
5. **Phase 5: Validation**: Create `tests/test_background_worker.py` to verify concurrency and verification loops in mock mode.
