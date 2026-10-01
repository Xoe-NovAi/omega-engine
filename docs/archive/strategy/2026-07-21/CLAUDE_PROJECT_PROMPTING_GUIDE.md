<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Claude Project Prompting & Knowledge Guide
**Version**: 1.0.0
**Status**: SOVEREIGN STANDARD
**Scope**: Claude.ai Projects / Custom Instructions

This guide defines the definitive strategy for configuring Claude Projects to ensure maximum adherence, architectural precision, and context stability.

---

## 🛡️ The Core Philosophy: Direct Context > RAG
 
Claude Projects operate in two distinct modes: **Direct Context** and **RAG (Retrieval Augmented Generation)**.
 
1.  **Direct Context**: All project files are loaded into the context window. Claude has "perfect" recall of every line.
2.  **RAG Mode**: Claude searches the project knowledge base and retrieves only the most "relevant" chunks. This is faster for massive datasets but introduces **Retrieval Gaps** (missing critical edge cases or architectural links).
 
### ⚠️ The 13-File Threshold & The 1M Window
**CRITICAL**: Even with the expansion to a **1M token context window** (for Max/Team/Enterprise), Claude Projects typically switch from Direct Context to RAG mode when the number of project files exceeds **~13 files**.
 
**The Sovereign Strategy**: To maintain "Temple-Grade" architectural audits and avoid "RAG-induced blind spots" (where the retriever may trigger prematurely or miss non-obvious links), you MUST consolidate your project knowledge into **12 or fewer high-density files**. This forces Claude to stay in Direct Context mode, ensuring absolute recall.

---

## 🌐 GitHub Integration & Tiered Context Strategy

When the codebase exceeds the 13-file "Direct Context" limit, do not simply upload more files (which triggers RAG and introduces blind spots). Instead, implement a **Tiered Context Model** using the native GitHub integration.

### 1. The Native GitHub Connector
Claude Projects now feature a native GitHub integration. 
**How to use**: Click the `+` button in the Project Knowledge section $\rightarrow$ Select **GitHub** $\rightarrow$ Paste Repository URL or search for your repo $\rightarrow$ Select specific files/folders.

### 2. The Tiered Context Model
Organize your project knowledge into three tiers of priority to balance **Perfect Recall** vs. **Deep Coverage**.

| Tier | Content Type | Delivery Method | Recall Mode | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Core** | High-density consolidated packs (e.g., `architecture_spec.md`, `mandates.md`) | **Manual Upload** ($\le 12$ files) | **Direct Context** | Absolute recall of architectural "North Star" and non-negotiable rules. |
| **Tier 2: Deep** | Specific source files, module implementations, detailed API specs | **GitHub Integration** (Selected files/folders) | **RAG** | Targeted deep-dives into implementation details. |
| **Tier 3: Wide** | External documentation, legacy archives, broad dependency maps | **GitHub URLs** (Referenced in prompt) | **External Reference** | Broad context and cross-referencing. |

### 3. Sovereign Execution Workflow
When interacting with a Web Claude Architect:
1. **Anchor the Core**: Ensure Tier 1 files are uploaded and the project is $\le 12$ files to maintain Direct Context for the "Rules of Engagement".
2. **Targeted Expansion**: If the AI needs to see a specific implementation, instruct it: *"Please reference [File X] via the GitHub integration to analyze the logic."*
3. **Sync Regularly**: Use the "Sync" icon in the GitHub connector to ensure the AI is not working on stale code.

 
## 🏗️ Optimal Custom Instruction Structure
 
Use **XML Tags** to structure custom instructions. Claude's architecture is specifically tuned to parse XML, which prevents "instruction drift" and ensures constraints are treated as hard boundaries.
 
### The Sovereign Template
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
Define the persona, expertise level, and primary objective. 
Example: "You are the Sovereign Hub Architect. Your goal is to modularize a monolith into Temple-Grade components."
</role>
...
```


<context>
Provide the high-level state of the project, current phase, and the "Why" behind the work.
Example: "The Omega Engine is in Sprint C. We are currently splitting server.py into 5 modules."
</context>

<constraints>
List non-negotiable rules. Use "MUST" and "FORBIDDEN".
Example: 
- MUST use AnyIO for all async code.
- FORBIDDEN to modify src/omega/oracle/ without a verified plan.
</constraints>

<design_principles>
Codify the architectural "North Star".
Example: "Simplicity > Correctness > Consistency. Use the 'Right Approximation' principle."
</design_principles>

<standing_rules>
Operational rules for the session.
Example: "Always check active-tracker.md before proposing new tasks."
</standing_rules>

<project_files>
List the key files in the project and their purpose. This helps Claude map the codebase.
Example:
- `server.py`: The monolith being split.
- `active-tracker.md`: The source of truth for task state.
</project_files>

<output_format>
Define exactly how responses should be structured to avoid verbosity.
Example: "Use structured markdown with Session ID, Status, and Next Action."
</output_format>
```

---

## 📚 Project Knowledge Management

### 1. The `CLAUDE.md` Pattern
Upload a `CLAUDE.md` file to your Project Knowledge. This acts as a "Code-Native" system prompt. Claude often prioritizes this file for operational context.
**Include in `CLAUDE.md`**:
- Build/Test commands (e.g., `make test`, `make temple-grade`).
- Coding style guides (e.g., "Use Google-style docstrings").
- Project-specific terminology (Glossary).

### 2. High-Density Consolidation
Instead of uploading 50 small files, merge them into logical "Knowledge Bundles":
- `architecture_spec.md`: Merge all design docs and RFCs.
- `api_reference.md`: Merge all endpoint definitions and schemas.
- `heritage_and_mandates.md`: Merge `SOVEREIGN_MANDATES.md` and `CREDITS.md`.

### 3. RAG Optimization (If > 13 files is mandatory)
If you must exceed the 13-file limit:
- **Descriptive Filenames**: Use `Sovereign_Mandates_v3.md` instead of `mandates.md`.
- **Internal Headers**: Use clear `# H1` and `## H2` headers within files to help the retriever find the correct chunk.
- **Cross-Referencing**: Explicitly mention other files in your text (e.g., "See `api_spec.md` for details").

---

## 🎯 Prompting for Architectural Audits

To ensure Claude doesn't hallucinate or miss a detail during a deep audit:

1.  **The "Chain-of-Thought" Trigger**: Start the prompt with: `"Analyze the following files step-by-step. First, map the data flow, then identify the violation, then propose the fix."`
2.  **The "Skeptical Verifier" Prompt**: After a solution is proposed, ask: `"Now act as the Adversary. Find three ways this proposed fix could break the system or violate a Sovereign Mandate."`
3.  **The "Direct Reference" Requirement**: Command Claude to cite line numbers or specific file sections: `"Your answer MUST include direct quotes from the project files to justify the change."`

---

## 🚀 Advanced Architectural Orchestration

For high-stakes architectural reviews where "good enough" is a failure, move from single-turn prompting to **Orchestrated Forensic Auditing**.

### 1. Multi-Turn Forensic Review (The Audit Pipeline)
Do not ask for a "review" in one prompt. Execute a sequenced pipeline to prevent Claude from skipping details.

| Phase | Prompt Intent | Key Instruction |
| :--- | :--- | :--- |
| **1. Structural Map** | Establish Ground Truth | "Map every call site of [Feature X]. Create a dependency graph of all affected modules. Do not propose fixes yet." |
| **2. Mandate Audit** | Identify Violations | "Compare the structural map against `SOVEREIGN_MANDATES.md`. Identify every point of friction or violation. Cite the Mandate number." |
| **3. Logic Stress-Test** | Find Failure Modes | "Simulate a failure at [Point A]. How does the system react? Does it fail silently? Search for race conditions or OOM risks." |
| **4. Remediation Synthesis** | Final Plan | "Propose a fix that resolves all identified frictions and failure modes. Ensure the fix does not introduce new mandate violations." |

### 2. Cross-Project Domain Synthesis
When the codebase exceeds the 13-file "Direct Context" limit, split the engine into **Domain Projects** and synthesize the results.

**Example Domain Split**:
- **Project: Omega-Providers**: `ModelGateway`, `providers.yaml`, `backends/`
- **Project: Omega-Soul**: `EntityRegistry`, `soul_distiller.py`, `soul.yaml`
- **Project: Omega-Hivemind**: `mcp_servers/omega_hub`, `HIVEMIND_PROTOCOL.md`

**The Synthesis Step**:
Once domain audits are complete, feed the *summaries* of those audits into a "Master Orchestrator" prompt:
> "I have audited the Provider Fabric and the Soul Engine separately. Here are the findings from both. Identify the architectural intersection where these two domains clash or create a bottleneck."

### 3. Deep Skeptical Prompting (The Adversary's Toolkit)
Force Claude to break its own solutions using "Devil's Advocate" prompts.

- **The Regression Hunt**: *"Assume this fix is correct. Now, find the most obscure reason why it would cause a regression in [Module Y] or break a legacy pattern."*
- **The Mandate Clash**: *"This fix satisfies M1 (AnyIO). Now, argue why it might violate M18 (Token Efficiency) or M13 (Temple-Grade). Be ruthless."*
- **The "Lying Code" Test**: *"Ignore the docstrings and comments. Based strictly on the implementation logic, what is this function actually doing? Does it match the stated intent?"*

### 4. The Forensic Auditor Persona
Refine the 'Sovereign Architect' into a **Forensic Auditor**. A forensic auditor does not "suggest"; they "evidence."

**Linguistic Markers to Enforce**:
- **Evidence-Based**: "The evidence in `oracle.py:153` suggests..."
- **Drift Detection**: "This implementation represents architectural drift from the original spec..."
- **Traceable Lineage**: "This pattern violates the lineage established in `PIVOT_LOG.md`..."

**Reasoning Patterns**:
- **Contra-positive Reasoning**: "If the system were Temple-Grade, we would see [X]. We do not see [X], therefore the system is not Temple-Grade."
- **First-Principles Audit**: "Strip away the framework. What is the raw data movement here? Is it efficient?"

## 🌐 External SOTA & Benchmarks (2026 Update)

Based on SOTA research and community benchmarks for Claude 3.5/4.0/4.6, the following patterns are mandated for high-stakes architectural work.

### 1. The XML "Hard Boundary" Mandate
Recent analysis of Claude 4.x fine-tuning indicates that **XML tags are not merely structural suggestions—they are hard logical boundaries** used during the model's training phase. 
- **SOTA Pattern**: Use XML for the "Container" (e.g., `<constraints>`, `<role>`) and Markdown for the "Content" inside.
- **Why**: This prevents "Instruction Leakage" where the model confuses a project file's content with a system instruction.
- **Source**: *Anthropic Platform Docs / PromptSera XML Metaprompt Guide (2026)*.

### 2. The RAG Trigger Confirmation
The "13-File Threshold" is a verified systemic trigger.
- **Benchmark**: Claude Projects switch from direct context loading to `project_knowledge_search` (RAG) at approximately **13 files**, regardless of whether the total token count is well under the 200K limit.
- **Sovereign Action**: To ensure "Perfect Recall," strictly maintain $\le 12$ files. If the project grows, use "High-Density Consolidation" (see §📚).
- **Source**: *Community benchmarks and practitioner reports (2026)*.

### 3. Context Window & "Lost-in-the-Middle" Mitigation
While Claude supports massive context windows, the standard Project UI (200K) still suffers from mid-context degradation.
- **Mitigation: Markdown State Machines**: Instead of a linear chat, maintain a `STATE.md` file in the project. Update this file at the end of every turn to "anchor" the current focus and progress.
- **Mitigation: Manual Compaction**: For sessions exceeding 100K tokens, trigger a "Context Reset" by starting a new chat and feeding it the current `STATE.md` and the most recent 3 turns.
- **Source**: *Albertsikkema AI Development Reports (2026)*.

### 4. Persona Construction for High-Stakes Audits
For "Sovereign Architect" or "Forensic Auditor" roles, avoid generic descriptions. Use **Operational Sovereignty** markers:
- **Confidence Scoring**: Require Claude to provide a "Field-Level Confidence Score" (0.0-1.0) for every architectural claim.
- **First-Principles Anchor**: Command the persona to "Strip away all framework assumptions and analyze the raw data movement" before proposing a solution.
- **Source**: *Sovereign AI in Financial Services / Lexology Forensic Reports (2026)*.
