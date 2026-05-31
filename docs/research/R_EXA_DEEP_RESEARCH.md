# 🔱 Omega Engine — Exa Deep Research Pattern
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-EXA-DEEP

**AP Token**: `AP-RESEARCH-EXA-DEEP-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-14
**Status**: READY

---

## Summary
Analysis of the `exa-deep-researcher` architectural pattern. Implements an asynchronous, supervisor-led research loop that decouples information gathering from conversational interaction.

## Findings

### The Async-Research Pattern
Unlike synchronous agents, this pattern treats research as a background job:
1. **Job Initiation**: User trigger $\rightarrow$ `start_research_job`.
2. **Background Execution**: The agent remains conversationally available while a separate loop runs.
3. **Streaming Updates**: Progress and findings are streamed to the UI via RPC.

### The Supervisor Loop
The core logic follows an iterative "Supervisor Pattern":
- **Decomposition**: Supervisor LLM breaks the topic into subtopics.
- **Iterative Search**: For each subtopic $\rightarrow$ EXA Search $\rightarrow$ Content Fetch $\rightarrow$ Synthesis.
- **Evaluation**: Supervisor evaluates synthesized notes.
- **Decision**: Either "Research Complete" or "Choose Next Topic".
- **Smart Compression**: Notes are compressed periodicallly to manage token limits.

### Tooling
- **Exa API**: Used for AI-native search and content extraction.
- **LiveKit**: Used for voice-interface and real-time RPC streaming.

## Recommendations
1. **Implement Background Jobs**: Move `gnosis-analyst` tasks to a background queue in `omega-hub`.
2. **Adopt the Supervisor Loop**: Implement iterative subtopic decomposition for deep research tasks.
3. **Voice Status Updates**: Use rate-limited "Concise Voice Updates" for Iris to report background progress.

## Sources
- `livekit-examples/dev-day-demos/exa-deep-researcher`
- Exa AI API Documentation

## Implementation Note
_For: Sovereign Builder / Gemini CLI_
Implement the `ResearchOrchestrator` in `omega-hub`. The `Sovereign Plugin` should be able to trigger this orchestrator and subscribe to its progress events via a websocket or SSE.
