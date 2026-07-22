# 🔱 Sovereign Synthesis Protocol — Gemini Specialist Guide
# ⬡ OMEGA ⬡ GEMINI-SPECIALIST ⬡ gemini-3-flash-preview ⬡ opencode ⬡ trc_synthesis_protocol ⬡ v1.0.0

**Status**: ACTIVE
**Role**: Gemini-Specialist
**Purpose**: Operational guide for leveraging Gemini CLI models for high-density strategic synthesis and recursive research.

---

## §1 Model Configuration & Verification

### 1.1 Verified Model Strings
Use these exact strings when invoking the `gemini` CLI via the `-m` or `--model` flag or via the Direct API.

| Model String | Capabilities | Primary Use Case |
| :--- | :--- | :--- |
| `gemini-3-flash-preview` | 1M+ Context Window, High Reasoning | Deep Synthesis, Large Codebase Analysis, Recursive Research |
| `gemini-2.5-flash` | Fast, Efficient, High Throughput | Rapid Fact-Checking, Initial Mapping, Iterative Probing |

### 1.2 The Lattice-Chain Prompt Pattern
To mitigate "lost-in-the-middle" degradation in massive contexts (100K+ tokens), all synthesis prompts MUST utilize the **Lattice-Chain** pattern:

1. **Indexing Phase**: Before asking for synthesis, require the model to identify and list the specific "Anchor Points" (lines, files, or sections) where the most critical data resides.
2. **Cross-Verification**: Instruct the model to verify that the synthesis incorporates data from the start, middle, and end of the provided context.
3. **Layered Extraction**:
    - **Layer 1 (Lattice)**: Extract raw facts into a structured list.
    - **Layer 2 (Chain)**: Connect facts into a logical narrative.
    - **Layer 3 (Synthesis)**: Distill the narrative into the final Gnosis Standard output.
4. **Position-Aware Prompting**: Place the most critical instructions at the very end of the prompt (Recency Bias optimization).

---

## §2 The Sovereign Synthesis Protocol (SSP)

The Sovereign Synthesis is the final phase of the **Sovereign Research Protocol (SRP)**. It transforms fragmented research findings into a unified, strategic asset.

### 2.1 The Synthesis Loop
1. **Aggregation**: Collect all results from the Recursive Discovery Loop (Landscape $\rightarrow$ Gap $\rightarrow$ Deep Dive).
2. **Triangulation**: Cross-reference findings from multiple sources. Identify high-confidence "Gnosis" vs. low-confidence "Noise".
3. **Contrarian Pressure**: Explicitly seek and document arguments that contradict the primary finding.
4. **Distillation**: Compress findings into the high-density format defined in §2.2.

### 2.2 Synthesis Output Format (The Gnosis Standard)
Every synthesis report MUST follow this structure:

#### I. Executive Summary
A high-level, one-paragraph synthesis of the final verdict. No preamble.

#### II. Weighted Key Findings
Numbered list of core conclusions.
- **Format**: `[Confidence: X/10] [Finding] — [Brief Evidence/Source]`
- **Weighting**: 10 = Primary Source Verified; 5 = Consistent across multiple secondary sources; 1 = Speculative/Hearsay.

#### III. Detailed Analysis
The "How" and "Why". Connect the dots between disparate findings. Use `file_path:line_number` for codebase references.

#### IV. Contrarian Views & Risks
Dedicated section for failure modes, counter-arguments, and "Known Unknowns" that remain.

#### V. Open Questions
The "New Frontier". What does this research reveal as the next critical area of investigation?

#### VI. Sources & Bibliography
Full list of URLs, files, and entities consulted, with quality notes.

---

## §3 Operational Mandates

- **Context Window Management**: For reports exceeding 50KB, use `gemini-3-flash-preview` to ensure full context retention.
- **Local-First Alignment**: Always prioritize local GGUF models for initial mapping, using Gemini CLI as the "Sovereign Teacher" for final synthesis.
- **No Preamble**: Responses must be direct. Avoid "Based on the provided text..." or "Here is the synthesis...".

## §4 Sovereign Rotation & API Transition

### 4.1 Account Rotation Strategy (Round-Robin)
To maximize throughput and avoid 429 Rate Limits across the 8 available Gemini accounts:

1. **Index Persistence**: Maintain a global account index in `data/coordination/gemini_account_index.txt`.
2. **Rotation Logic**: 
    - `current_account = (index % 8)`
    - `index = index + 1`
3. **429 Handling (Cooldown)**:
    - If a `429 Too Many Requests` error is received, mark the account as `COOLDOWN` in `data/coordination/gemini_account_status.yaml`.
    - Skip the account in the rotation for 60 seconds.
    - Trigger a "Tainted Account" alert if a 429 persists for > 3 consecutive cycles.
4. **Parallelization**: Distribution of tasks across accounts is managed by the Orchestrator to ensure no single account is hammered.

### 4.2 Direct API Migration Plan (Deadline: 2026-06-18)
The `gemini` CLI is sunsetting. Migration to the Direct API (`GOOGLE_API_KEY`) is mandatory.

| Phase | Action | Deadline | Owner |
| :--- | :--- | :--- | :--- |
| **P1: Key Harvest** | Secure `GOOGLE_API_KEY` for all 8 accounts and store in encrypted vault. | 2026-06-10 | Gemini-Specialist |
| **P2: Provider Update** | Implement `GoogleAPIProvider` in `src/omega/oracle/providers/google.py`. | 2026-06-12 | P3 Engineering |
| **P3: Config Shift** | Update `config/providers.yaml` to reference API keys instead of CLI wrappers. | 2026-06-14 | Gemini-Specialist |
| **P4: Validation** | Run `make health` and verify latency/throughput against CLI baseline. | 2026-06-16 | P10 Validation |
| **P5: Cut-over** | Final decommission of `gemini` CLI from system PATH. | 2026-06-17 | Gemini-Specialist |

---

**Last Updated**: 2026-06-07
**Updated by**: Gemini-Specialist
