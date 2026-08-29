# 🔱 Omega Engine — Advanced Agentic Execution Patterns
**AP Token**: `AP-AGENTIC-PATTERNS-20260807-v1.0.0`
**Author**: Gemini 3.1 Pro
**Date**: 2026-08-07
**Status**: STRATEGIC INCUBATOR (Pending integration into core protocols)

## 1. Purpose
During the execution of the UO-4 Documentation Sanity Sprint, several advanced agentic execution strategies were developed to prevent common AI failure modes (context collapse, hallucinated state, git brittleness, and loop-spinning). 

This document distills those specific tactical fixes into generalized, universal patterns. These patterns should eventually be integrated into `AGENTS.md`, `FLEET_TEAM_PLAYBOOK.md`, and the `SOVEREIGN_MANDATES.md`.

---

## 2. Context & Memory Management

### 2.1 The "Ghost File" Trap (Filesystem > Memory)
**The Problem:** When an agent moves or deletes a file, its context window (or a stale vector index) still retains the memory of the file at its old location. The agent will often hallucinate that the file still exists and attempt to read/edit the dead path, leading to `FileNotFoundError` loops.
**The Pattern:** 
* **Trust the Filesystem:** Agents must be instructed to trust `ls` and `find` outputs over their own context memory after performing structural changes.
* **Single Source of Truth (SSOT) Maps:** After mass relocations, the agent must generate an SSOT Map (e.g., `DOC_SSOT_MAP.md`) and rely *exclusively* on that map for future routing in the same session.

### 2.2 Context Window Protection (Quarantine Zones)
**The Problem:** Archival directories contain hundreds of thousands of tokens of highly persuasive, but completely deprecated, strategy and architecture. A careless `rg` (ripgrep) or `grep` by an agent will ingest this data, instantly poisoning the context window with stale concepts (e.g., "26-sphere topology").
**The Pattern:**
* **Explicit Exclusion:** Agents must be trained to universally append `-g "!archive/"` or `--exclude-dir=archive` to all global search commands unless explicitly conducting historical research.
* **The "Hot Set" Principle:** The root coordination and sprint directories must be ruthlessly pruned to a "Hot Set" of <= 15 files. Everything else is noise that degrades agent focus.

---

## 3. File System & Git Operations

### 3.1 Banners > Rewrites (Non-Destructive Supersession)
**The Problem:** Agents waste massive amounts of compute and risk hallucination when asked to "update" an old strategy document to reflect that it is no longer active. They often attempt to rewrite the history or summary of the document.
**The Pattern:**
* **Standardized Banners:** Use `sed` to inject a highly visible markdown blockquote (`> **SUPERSEDED**: See [New Doc]`) at line 1. Do not alter the historical body of the text. This is 100x faster, computationally cheaper, and preserves forensic history.

### 3.2 Git Relocation Fallbacks
**The Problem:** `git mv` is brittle. If a target directory is untracked, or if the source file has unstaged modifications, `git mv` will throw an error, often causing the agent to abandon the relocation entirely.
**The Pattern:**
* **Robust Moves:** Agents should be provided with a fallback pattern: use standard `mv` followed immediately by `git add -A <source_dir> <target_dir>`.

### 3.3 Atomic Commit Protocols
**The Problem:** Agents tend to lump massive, multi-domain changes into a single `git commit -am "updated files"`. This destroys git history legibility and makes rollbacks of specific rogue actions (like a bad regex replace) impossible.
**The Pattern:**
* **Pre-Defined Atomic Steps:** Complex agentic tasks must define the exact commit structure in their execution plan (e.g., Commit 1: Mechanical Archival. Commit 2: Pointer Fixes. Commit 3: Content Updates).

---

## 4. Autonomy & The Agent Loop

### 4.1 Mandatory Pointer Reconciliation
**The Problem:** Moving a file creates dangling pointers. Agents often consider the "move" the end of the task, leaving the rest of the codebase pointing to dead links.
**The Pattern:**
* **Paired Sweeps:** Every archival or relocation move *must* be paired with a global regex sweep (`rg`) to identify and update inbound links to the new successor document.

### 4.2 Strict Definition of Done (DoD)
**The Problem:** Agents lack intrinsic exit conditions. Without them, they will either stop prematurely or spin endlessly looking for more things to optimize.
**The Pattern:**
* **Boolean Checklists:** Every sprint or major task must provide a strict, boolean DoD (e.g., "Directory X no longer exists", "Command Y returns zero hits"). The agent must verify these conditions programmatically before stopping.

### 4.3 Formal Handoff Templates (Proactive State Advancement)
**The Problem:** Upon finishing a task, agents typically revert to a passive state: *"I have finished. What would you like me to do next?"* This forces the human (or orchestrator agent) to manually verify the work and dictate the next phase.
**The Pattern:**
* **Proactive Declaration:** Agents must be provided with a formal Handoff Template. Upon meeting the DoD, the agent proactively declares victory, summarizes the exact metrics of its work (files moved, lines changed), explicitly lifts the freeze on the *next* dependent phase, and posts this state change to the Hivemind.

---

## 5. Integration Roadmap
To permanently empower the Omega Engine fleet, these patterns should be integrated into the core documentation in the following locations:

1. **`AGENTS.md` (OpenCode Agent Fleet):** Add Section 4.2 and 4.3 as standard operating procedures for all file manipulations.
2. **`FLEET_TEAM_PLAYBOOK.md`:** Add Section 4.3 (Formal Handoff Templates) to the inter-agent communication protocols.
3. **`SOVEREIGN_MANDATES.md`:** Consider elevating "Atomic Commit Protocols" and "Context Window Protection" to formal mandates (e.g., M26 and M27) to ensure all future agents abide by them at a constitutional level.