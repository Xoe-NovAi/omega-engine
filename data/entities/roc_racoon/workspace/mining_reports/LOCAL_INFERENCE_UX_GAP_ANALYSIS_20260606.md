<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Mining Report: Local Inference + UX Gap Analysis
**⬡ OMEGA ⬡ ROC_RACOON ⬡ MINING-REPORT ⬡ 2026-06-06**
**AP Token**: AP-MINING-LOCAL-INFERENCE-v1.0.0

---

## Executive Summary

We have **the architecture** for local inference — but the **plumbing is severed in 3 places** and the **models don't exist on disk** for the primary path. The UX/UI is **functional but unpolished**: command-line Typer/Rich (no TUI, no streaming, no full-screen interaction).

**Verdict**: 2-3 days of focused work gets a working local inference engine with a coherent Textual-based TUI. 5-7 days gets feature parity with Qwen Code CLI's user experience.

---

## §1 What We Have — Complete Inventory

### 1.1 Provider Fabric (The Architecture)

| Provider | Config Priority | Status | Model Dir on Disk? | Runtime? |
|----------|----------------|--------|-------------------|----------|
| `native-gguf` | **0 (PRIMARY)** | 🔴 **BROKEN** | ❌ Path doesn't exist | ❌ `llama-cpp-python` not installed |
| `lmster` | 1 | 🟡 **DORMANT** | ✅ Models in `lmstudio-models/` | ❌ Server OFF (`lms server start`) |
| `ollama` | 2 | 🟡 **DORMANT** | ❌ Only `qwen2.5:0.5b` pulled | ✅ Daemon running, has 1 tiny model |
| `google` | 3 | 🟢 CLOUD | N/A | ✅ API if key set |
| `opencode-zen` | 4 | 🟢 CLOUD | N/A | ✅ API if key set |

### 1.2 Models on Disk (ACTUAL LOCATION: `/media/arcana-novai/omega_library/lmstudio-models/local/all/`)

| Model | Size | Purpose (from models.yaml) | On Disk? |
|-------|------|---------------------------|----------|
| `RocRacoon-3b.Q5_K_M.gguf` | 2.1 GB | Roc Racoon mining | ✅ |
| `Phi-4-mini-reasoning-heretic-i1-Q5_K_M.gguf` | 3.8 GB | SOPHIA deep analysis | ✅ (but wrong quantization vs config) |
| `Phi-2-OmniMatrix.i1-Q4_K_M.gguf` | 2.5 GB | Brigid creative | ✅ |
| `embeddinggemma-300m-Q6_K.gguf` | 200 MB | Embeddings | ✅ |
| `all-MiniLM-L6-v2-f16.gguf` | ~90 MB | MiniLM embeddings | ✅ |

### 1.3 Models MISSING from Disk (9 of 12 configured models)

| Model | Config Path (doesn't exist) | Purpose |
|-------|----------------------------|---------|
| `Qwen3-1.7B-Q6_K.gguf` | Never downloaded | Nova — always-on, Iris fallback |
| `Qwen3-0.6B-Q6_K.gguf` | Never downloaded | Iris — speculative decoder |
| `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | Never downloaded | Ma'at/Anubis — reasoning |
| `DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | Never downloaded | Lucifer — deep reasoning |
| `Krikri-8B-Instruct.Q4_K_M.gguf` | Never downloaded | Inanna/Isis/Lilith — knowledge |
| `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | Never downloaded | Brigid (fallback) |
| `phi-4-mini-reasoning-abliterated-q4_k_m.gguf` | Never downloaded | SOPHIA abliterated |
| `Qwen3-1.7B-Q6_K.gguf` (second copy) | Never downloaded | Sekhmet/Hecate |
| `Qwen3-0.6B-Q6_K.gguf` (second use) | Never downloaded | Iris |

### 1.4 CLI/UX Surface

| Interface | Framework | Lines | Features | Quality |
|-----------|-----------|-------|----------|---------|
| `omega` CLI | Typer + Rich | 672 | 25 commands, Tables, colored output | ✅ Functional, no streaming |
| `omega talk` | Typer → AnyIO | 11-line wrapper | Print response to console | ⚠️ No streaming, no TUI |
| `omega summon` | Typer → AnyIO | 17-line wrapper | Print response to console | ⚠️ No streaming, no TUI |
| `omega repl` | Not implemented | — | — | ❌ MISSING |
| `omega shell` | Not implemented | — | — | ❌ MISSING |
| MCP Hub | SSE tool server | Active | 45 tools | ✅ But not exposed as AI tool system |
| `make menu` | Makefile | Categorized | Shortcut collection | ⚠️ Not TUI, just colored help |

### 1.5 Inference Pipeline (End-to-End)

```
Query → Oracle.talk()
  → bootstrap() loads WADs
  → TDPGate.isolate() sanitizes
  → TraceSession creates trace_id
  → SessionManager resolves session_id
  → _detect_summon() / _detect_consult() check summon patterns
  → _assess_iris_confidence() decides: Iris vs escalate
  → _respond_as_iris() OR _route_by_domain()
    → _prepare_system_prompt() injects memory + context
    → _select_model() via TriageRouter
    → ModelGateway.generate()
      → ResourceGuard.lock() (sempahore)
      → Provider fabric iteration (native-gguf → lmster → Ollama → Google → ...)
      → Each provider: _precheck_provider() (circuit breaker)
      → provider.generate() (actual inference)
    → OracleResponse assembled
    → _record_interaction() (memory + soul + hivemind)
  → _display_response() (CLI console print)
```

---

## §2 What We Need — Gap Analysis by Layer

### Layer 1: Runtime — 3 Critical Bugs Blocking the Engine

| # | Bug | Location | Impact | Fix Time |
|---|-----|----------|--------|----------|
| **B1** | `Union` not imported in `typing` import | `oracle.py:25` | Engine CANNOT import — `NameError: name 'Union' is not defined` | 1 minute |
| **B2** | `entity` referenced but never defined in `_respond_as_iris` | `oracle.py:665-713` | Method will raise `NameError` if called (Iris direct response path) | 5 minutes |
| **B3** | `model_override` referenced but not in method signature | `oracle.py:669` | Same method — `NameError` | 5 minutes |

> ⚠️ **B1 alone means `omega talk` and `omega summon` crash on import.**

### Layer 2: Models — Missing = No Inference

| Priority | Model | Size | Source | Action |
|----------|-------|------|--------|--------|
| **P0** | `Qwen3-1.7B-Q6_K.gguf` | 1.6 GB | HuggingFace (Qwen) | `hf qwen/Qwen3-1.7B-Q6_K.gguf` |
| **P0** | `Qwen3-0.6B-Q6_K.gguf` | 0.47 GB | HuggingFace (Qwen) | `hf qwen/Qwen3-0.6B-Q6_K.gguf` |
| **P1** | `Qwen3-4B-Thinking-Q4_K_M.gguf` | 2.4 GB | HuggingFace (Qwen) | `hf qwen/Qwen3-4B-Thinking-2507-Q4_K_M.gguf` |
| **P1** | `DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | 4.2 GB | HuggingFace (DeepSeek) | Download |
| **P2** | `Krikri-8B-Instruct.Q4_K_M.gguf` | 4.7 GB | HuggingFace (Rinna) | Download |
| **P2** | `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | 2.5 GB | HuggingFace (Mistral) | Download |
| **P2** | `phi-4-mini-reasoning-abliterated-q4_k_m.gguf` | 3.8 GB | Local/abliterated | Already have heretic variant |

### Layer 3: Path Configuration — Config Points to Wrong Directory

```
models.yaml says:   /media/arcana-novai/omega_library/models/gguf/local/all/  ❌ DOES NOT EXIST
Models are at:      /media/arcana-novai/omega_library/lmstudio-models/local/all/   ✅ EXISTS
```

Fix: Either symlink or update `models.yaml` paths. Add a models directory creation step in setup.

### Layer 4: llama-cpp-python NOT Installed

native-gguf provider (priority 0) requires `llama-cpp-python`. Not installed. RM: 14GB RAM, Zen 2.

```
pip install llama-cpp-python \
  --config-settings=cmake.args="-DLLAMA_AVX2=ON;-DLLAMA_FMA=ON;-DLLAMA_F16C=ON;-DLLAMA_NO_AVX512=ON"
```

Estimated compile time: 15-30 minutes on Zen 2.

### Layer 5: LM Studio Server OFF

`lms` CLI is installed. `lms server start` will turn it on with the models at `lmstudio-models/local/all/`. Once running, lmster provider (priority 1) will pick them up via OpenAI-compatible API on :1234.

### Layer 6: UX/UI — Missing Textual TUI

| Feature | Current | Target | Gap |
|---------|---------|--------|-----|
| Full-screen TUI | ❌ None | ✅ Textual | Need to build `src/omega/terminal/` |
| Streaming output | ❌ Buffered print | ✅ Chunked SSE-style | Need streaming in ModelGateway |
| Markdown rendering | ❌ Raw text | ✅ Rich markdown in terminal | Textual has this built-in |
| Syntax highlighting | ❌ None | ✅ For code in responses | Textual has this |
| Progress indicators | ❌ None | ✅ Spinner/progress bar | Textual has built-in |
| Entity switching UI | ❌ Only via `--model` flag | ✅ Entity selector sidebar | Custom component |
| Conversation history | ❌ Hidden in files | ✅ Scrollable session view | Needs Textual chat widget |
| `/` commands | ❌ None | ✅ Slash commands (like Qwen) | Need to design and implement |

### Layer 7: REPL — Missing Interactive Shell

| Feature | Current | Target | Gap |
|---------|---------|--------|-----|
| Multi-turn conversation | ✅ Via sessions | ✅ Working | None |
| REPL loop | ❌ None | ✅ `omega shell` | 50-line loop |
| Tab completion | ❌ None | ✅ Entity names, commands | prompt_toolkit built-in |
| History browsing | ❌ None | ✅ Up/down arrow history | prompt_toolkit built-in |
| Ctrl+C interrupt | ❌ None | ✅ Graceful handling | anyio native |

---

## §3 Remediation Roadmap (Priority Order)

### Phase A: Unblock the Engine (1-2 hours)
```
A1. Fix oracle.py B1-B3 (Union import + entity definition)
A2. Symlink or update models.yaml path: /media/.../models/gguf/ → ../lmstudio-models/
A3. Start LM Studio server: lms server start 
A4. Verify: omega talk "hello" → should respond via lmster (fallback 1)
```

### Phase B: Install Native GGUF (2-3 hours, mostly compile time)
```
B1. Install llama-cpp-python with Zen 2 flags (15-30 min compile)
B2. Download missing P0 models (Qwen3-1.7B + Qwen3-0.6B)
B3. Verify: omega summon nova "hello" → should respond via native-gguf (primary)
B4. Test speculative decode: Iris gateway check → escalation
```

### Phase C: Build Textual TUI (3-5 days)
```
C1. Create src/omega/terminal/ package
C2. Implement LoginView → main chat view
C3. Wire Oracle.talk() to streaming output
C4. Add entity sidebar (selector from registry)
C5. Add session history viewer
C6. Add /commands (summon, switch, help, etc.)
```

### Phase D: Build REPL (1-2 days, can overlap C)
```
D1. Create omega shell command using prompt_toolkit
D2. Tab-completion from entity registry
D3. History persistence across sessions
D4. Ctrl+C graceful shutdown
```

### Phase E: LLM Tool System (2-3 days)
```
E1. Create src/omega/oracle/tool_registry.py
E2. Register file_read/write, shell_exec, web_fetch, library_search tools
E3. Wire TDP security gates on tool execution
E4. Expose tools to summoned entities via Oracle.talk()
```

---

## §4 Recommended Order of Operations

```
Day 1 (Today):
  ├── Fix oracle.py bugs (B1-B3) — 10 min
  ├── Symlink models directory — 5 min
  ├── Start LM Studio server — 2 min
  ├── Test: omega talk "what entities do you have" → 🟢 WORKING (via lmster)
  │
  Day 2:
  ├── Install llama-cpp-python — 30 min (background compile)
  ├── Download Qwen3-1.7B + Qwen3-0.6B — 20 min (background download)
  ├── Design Textual TUI layout — 1 hr
  ├── Start implementing TUI shell — 2 hr
  │
  Day 3:
  ├── Finish basic TUI (chat window + input bar) — 3 hr
  ├── Build REPL with prompt_toolkit — 2 hr
  ├── Test end-to-end: TUI → Oracle → LM Studio → response → display
  │
  Day 4-7:
  ├── Polish TUI (entity sidebar, session history, markdown rendering)
  ├── Streaming output (chunked from model via AnyIO)
  ├── Progress indicators (model loading, inference)
  └── Testing + bug fixing
```

---

## §5 The Runtime Bugs (B1-B3 Detail)

### B1 — `Union` Not Imported
```python
# oracle.py:25 (current)
from typing import Any, Dict, List, Optional, Set, Tuple    # ← Union MISSING

# oracle.py:314 (usage)
async def talk(self, query: Union[str, TaintedData], transient: bool = False) -> OracleResponse:
                    ^^^^^  NameError: name 'Union' is not defined
```

Fix: Add `Union` to the typing import.

### B2 — `entity` Not Defined in `_respond_as_iris`
```python
# oracle.py:665
system_prompt = await self._prepare_system_prompt(entity.name, session_id, entity.personality, query=query)
                                                    ^^^^^^  NameError in context

# The entity was supposed to be `self.iris_entity` (lower half of speculative decoder)
```

Fix: Replace `entity` with `self.iris_entity` (or `self.iris_entity if self.iris_entity else self.default_entity`).

### B3 — `model_override` Not in Method Signature
```python
# oracle.py:669
if model_override:
   ^^^^^^^^^^^^^  NameError — parameter doesn't exist in _respond_as_iris()
```

Fix: Add `model_override: Optional[str] = None` parameter to `_respond_as_iris()` signature.

---

**⬡ OMEGA ⬡ ROC_RACOON ⬡ MINING-COMPLETE ⬡**

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: MINING-REPORT | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
