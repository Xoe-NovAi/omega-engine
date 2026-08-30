<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Technical Extraction Report: Iris Ancestor Patterns
**Sector**: B (Voice & Interface)
**Miner**: Roc Racoon
**Date**: 2026-07-02
**Status**: COMPLETED

## 1. Executive Summary
This report details the recovery of "Iris Ancestor" patterns from legacy Xoe-NovAi and XNAi repositories. The recovered patterns represent a transition from a specialized RAG-voice app to the current sovereign Omega Engine. Key recovered areas include robust regex-based command parsing, energy-based VAD, and background task orchestration within a Chainlit UI.

---

## 2. Recovered Patterns

### 2.1 Voice Command Parsing & Routing
**Source**: `voice_command_handler.py`

#### 🛠️ Pattern: Hybrid Command Matcher
- **Description**: A two-stage parsing pipeline that first attempts high-confidence regex matching and falls back to keyword-based fuzzy matching.
- **Logic**:
    - **Stage 1 (Regex)**: Uses a dictionary of `COMMAND_PATTERNS` (e.g., `(?:insert|add|save|store|remember|vault)\s+(.+?)`) to extract both the command type and the target content.
    - **Stage 2 (Fuzzy)**: Calculates keyword overlap (Intersection over Union) between the input text and predefined keyword sets for each command type.
- **Omega Mapping**: This pattern is a precursor to the current `Oracle.talk()` intent detection. The " laziest senior dev" approach of using regex for common commands is still highly effective for low-latency routing before hitting a full LLM.

### 2.2 Audio Interface & Voice Processing
**Source**: `voice_interface.py`

#### 🛠️ Pattern: Energy-Based VAD (Voice Activity Detection)
- **Description**: A lightweight, torch-free VAD implementation that monitors audio energy levels to detect speech boundaries.
- **Logic**:
    - Converts raw bytes to numpy `int16` arrays.
    - Calculates Root Mean Square (RMS) energy: `np.sqrt(np.mean(audio_array**2))`.
    - Uses a `silence_threshold` and `silence_duration` (1.5s) to mark the end of a speech segment.
- **Omega Mapping**: This is the "right approximation" for local audio processing. Current Nova/Iris implementations can benefit from this low-overhead boundary detection to reduce STT API costs/latency.

#### 🛠️ Pattern: Regex-Based Wake Word Detection
- **Description**: "Hey Nova" detection using probabilistic regex matching.
- **Logic**:
    - Uses a combination of phrase matching and a "confidence" score based on the match's position in the string and the relative length of the match.
- **Omega Mapping**: Pre-dates the current "Hey Nova" containerized wake-word system.

#### 🛠️ Pattern: Voice Circuit Breaker
- **Description**: A state-machine (`CLOSED`, `OPEN`, `HALF_OPEN`) protecting STT/TTS providers from cascading failures.
- **Omega Mapping**: Directly evolves into the current `AsyncCircuitBreaker` in `src/omega/oracle/health_monitor.py`.

### 2.3 Chainlit UI & Interface Logic
**Source**: `chainlit_app.py`

#### 🛠️ Pattern: Non-Blocking Background Curation
- **Description**: Dispatching long-running curation tasks (crawling/embedding) as detached subprocesses to maintain UI responsiveness.
- **Logic**:
    - Uses `subprocess.Popen` with `stdout=DEVNULL` and `start_new_session=True`.
    - Tracks active processes in a global `active_curations` dictionary.
- **Omega Mapping**: This pattern of "dispatch and forget" with a tracking ID is echoed in the current `Orchestrator` and `Hivemind` handoff mechanisms.

#### 🛠️ Pattern: Local LLM Fallback Chain
- **Description**: A graceful degradation strategy that switches from a remote RAG API to a local LLM instance upon `ConnectError` or `TimeoutException`.
- **Omega Mapping**: A direct ancestor of the **Local-First Mandate (M7)**. The "switch to local" logic in the UI is now centralized in the `ModelGateway` provider fabric.

---

## 3. Mapping to Current Implementation

| Legacy Pattern | Current Omega Implementation | Status | Dedup Status |
|----------------|------------------------------|--------|-------------|
| Regex Command Parser | `Oracle.talk()` Intent Matcher | 🔄 Evolved | **PORTED** — `oracle.py` intent matcher covers this pattern. |
| Energy-based VAD | Nova/Iris Audio Pipeline | 🟢 Retained/Optimized | **NOVEL** — Not in current engine. Nova/Iris use containerized wake-word. |
| Voice Circuit Breaker | `health_monitor.py:AsyncCircuitBreaker` | ✅ Fully Ported | **PORTED** — `health_monitor.py:AsyncCircuitBreaker` is the direct evolution. |
| Redis Session Mgmt | `MemoryStore` / Hivemind Sessions | ✅ Fully Ported | **PORTED** — `MemoryStore` + Hivemind sessions. |
| Subprocess Curation | `Orchestrator` / MCP Hub Tasks | 🔄 Evolved | **PORTED** — `Orchestrator` + MCP Hub tasks. |
| Local Fallback | `ModelGateway` Local-First Chain | ✅ Fully Ported | **PORTED** — `ModelGateway` local-first chain (M7). |

## 4. Mining Conclusion
The "Iris Ancestor" patterns reveal a strong emphasis on **resilience** (circuit breakers, fallbacks) and **efficiency** (torch-free TTS/STT, energy VAD). While the UI has shifted from Chainlit to a more sovereign MCP-driven architecture, the underlying philosophy of "Sovereign execution via local-first fallback" was already present in the XNAi era.
