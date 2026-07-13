# 🔱 Sovereign Research Report: Context Engineering & System Integration
**AP Token**: `AP-RESEARCHER-CONTEXT-v1.0.0`
**Date**: 2026-07-11
**Author**: Sovereign Researcher (Gemini 3.1 Pro)
**Target Audience**: Kali (Grand Oversight), Ma'at (Build), Lilith (Run), dev team.
**Status**: PROPOSED FOR IMMEDIATE SPRINT INTEGRATION

> **⚠️ OPUS/SONNET AUDIT NOTE (2026-07-11):** This report incorrectly assesses the YouTube Research Module as "spec-only". It is actually fully implemented at the P0 structural level. See `R_SONNET46_FINAL_ANALYSIS.md` for the corrected code-grounded analysis and `R_IMPLEMENTATIONS_MANUAL.md` for the sprint execution plan.

---

## 1. Executive Summary (L1)
During the "Claude Fable 5 Maximization Sprint," a critical architectural opportunity was identified: **The Context Packer must evolve from a standalone script into the Omega Engine's "Universal Context Interface."** 

By upgrading the Context Packer to output token-aware, XML-structured bundles, and integrating it directly into the Entity Workspace, Background Researcher, and Soul Distiller, we can eliminate context fragmentation. Furthermore, the YouTube Research Module (Sieve-and-Sign) must be wired into the Background Researcher and Soul Distiller to convert ephemeral video data into permanent, cryptographically verified Gnosis.

## 2. Hardening & Enhancement (The Gemini 3.1 Pro Review)
The initial enhanced packer script was a strong prototype, but requires the following **Sovereign Hardening** before merging into `main`:

### 2.1. XML Integrity & Escaping (Critical Fix)
*   **Vulnerability**: The prototype used basic string replacement (`replace('"', '\"')`) for XML attributes. This will break Claude's XML parser if files contain unescaped `<`, `>`, or `&` characters.
*   **Hardening**: The packer MUST use standard XML escaping (e.g., `xml.sax.saxutils.escape` and `quoteattr`) for all file contents and metadata attributes to ensure strict well-formedness.

### 2.2. PII Masking Integration (Mandate 7 & 8 Compliance)
*   **Vulnerability**: Context packs generated for external LLMs (like Claude.ai) risk leaking local secrets, API keys, or PII.
*   **Hardening**: The Context Packer MUST route all file content through the engine's existing `pii_masker.py` *before* XML wrapping, ensuring zero sensitive data leaves the local machine.

### 2.3. WAD-Aware Packing (Mandate 2 Compliance)
*   **Vulnerability**: A generic pack might mix Core Engine logic with WAD-specific secrets, violating the Engine-Stack Firewall.
*   **Hardening**: Pack profiles must explicitly declare their WAD scope. The packer must reject attempts to bundle `src/omega/` and `config/wads/arcana_novai/` in the same theme unless explicitly overridden by a `cross_boundary: true` flag.

### 2.4. Ephemeral Pack Cleanup (Storage Hygiene)
*   **Vulnerability**: Generating large context packs repeatedly will bloat the disk.
*   **Hardening**: Implement a TTL (Time-To-Live) policy for `context_packs/`. Packs older than 7 days should be automatically purged by a background maintenance task.

---

## 3. The Universal Context Interface Architecture
The Context Packer will sit at the center of the Omega Engine's cognitive flow:

```text
External LLMs (Claude/OpenCode)        Local Models (Native-GGUF)
               ▲                                  ▲
               │                                  │
               └───────────────┬──────────────────┘
                               │
                    ┌──────────────────┐
                    │  Context Packer  │ ← XML, Token-Aware, PII-Masked
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 Entity Workspaces    Background Researcher   Soul Distiller
 (Hydration)          (Priming)               (Contextualization)
```

## 4. Cross-System Integration Blueprint (Sprint Tasks)

### Track A: Entity Workspace Hydration (Assign: Ma'at / P7)
*   **Task**: Modify `EntityWorkspaceManager.scaffold_workspace()`.
*   **Action**: Create a `context/` directory inside each entity's workspace.
*   **Action**: Add an `import_context_pack()` method to allow entities to load specific XML packs into their active memory context during initialization.

### Track B: Background Researcher Integration (Assign: Lilith / P6)
*   **Task**: Modify `BackgroundResearcherLoop._grow_frontier()`.
*   **Action**: Before initiating a deep research cycle, the loop should request a relevant context pack to prime its prompt, ensuring it doesn't research blindly.
*   **Action**: Add the **YouTube Research Module** as a formal gap source. The background loop should autonomously pull transcripts, run the Sieve-and-Sign pipeline, and output Atomic Knowledge Blocks.

### Track C: Soul Distiller Contextualization (Assign: Verity / P7)
*   **Task**: Modify `SoulDistiller.distill_session()`.
*   **Action**: When extracting L1 (Narrative) and L2 (Insight), the distiller should have access to the entity's active context pack. This prevents the distiller from hallucinating architectural details that are clearly defined in the pack.
*   **Action**: Ensure YouTube Atomic Knowledge Blocks are routed directly into the `proposed_lessons.yaml` pipeline for Staging Gate review.

### Track D: Hivemind Discovery (Assign: Link P9)
*   **Task**: Modify the Context Packer CLI/execution flow.
*   **Action**: Upon successful generation of a pack, the packer MUST call `hivemind_post_context` to broadcast the pack's availability, profile name, and token size to all active agents.

---

## 5. Immediate Next Steps for the Dev Team
1.  **Code Relocation**: Move `omega-enhanced-packer.py` to `.opencode/skills/context-packer/enhanced_packer.py`.
2.  **Apply Security Fixes**: Implement `xml.sax.saxutils` and `pii_masker` into the enhanced packer.
3.  **Update Dependencies**: Add `tiktoken` to `pyproject.toml`.
4.  **Update WAD Configs**: Add entity-specific profiles (e.g., `kali-oversight`, `youtube-research`) to `packer-config.yaml`.
5.  **Execute Sprint**: Deploy the 8-account strike teams using the newly generated, hardened context packs.

*End of Report.*
