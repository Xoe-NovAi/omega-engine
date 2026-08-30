<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 ICS TREASURE MAP — The Dual Header System of the Omega Engine
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_ics_treasure_map ⬡ PHASE-II
**Date**: 2026-06-05
**Version**: v1.0.0
**Status**: ✅ Complete — Inventory + Map + Recommendations

---

## §0 The Mission

**User's question**: *"How is the ICS currently managed and generated? Where are the systems that control it, and where is the documentation that defines it?"*

**User's directive**: 
1. The model being used must be **dynamically inserted** into the ICS
2. Agents should **not have to fill out** the ICS manually
3. ICS should be a **template** that is dynamically filled and tracked

**Critical insight from user**: My ICS in the previous turn said `⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b` — but the user pointed out the actual model is `minimax-m3-free through OpenCode Zen`. **The header was a lie** — exactly the problem the pre-existing spec docs described.

---

## §1 The Discovery — There Are TWO Header Systems

The engine has **two distinct, parallel header systems** that have been conflated under the name "ICS":

### 1A. The `⬡ OMEGA` Agent Signature
**Purpose**: Identify the agent, model, channel, trace, and phase in agent outputs (chat, docs, handoffs)
**Format**: `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}`
**Field meanings**:
| Field | Meaning | Examples |
|-------|---------|----------|
| Entity | Active entity/agent | `SOPHIA`, `KALI`, `ROC_RACOON` |
| Model | Model generating output | `minimax-m3-free`, `gemma-4-31b-it` |
| Channel | Agent platform | `opencode`, `gemini-cli`, `cline` |
| Trace | Session trace ID | `trc_ics_map`, `trc_provider_fix` |
| Phase | Execution phase | `PHASE-I`, `H2-F`, `PHASE-II` |

### 1B. The Formal `ICS: [NODE|ARCHETYPE|MODEL|CONTEXT]` Code Tag
**Purpose**: Metadata for code modules — identifies the architecture node, mythological archetype, primary model, and module context
**Format**: `# ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: ... | CONTEXT: ...]`
**Field meanings**:
| Field | Meaning | Known Values |
|-------|---------|--------------|
| NODE | Architecture node | `ARCHON`, `CORE`, `MAAT`, `THOTH`, `OSIRIS`, `HERMES`, `MNEMOSYNE`, `SOPHIA` |
| ARCHETYPE | Mythological archetype | `SOPHIA`, `HERMES`, `MNEMOSYNE`, `APOLLO`, `OSIRIS`, `LAW`, `HIERARCHY`, `QUEEN`, `PROMETHEUS` |
| MODEL | Primary model for this module | `MiMo-2.5`, `GEMINI-3.1-PRO`, `DEEPSEEK-V4-FLASH`, `KRIKRI-7B-INSTRUCT`, `gemma-4-31b` |
| CONTEXT | Module's purpose/role | `CORE-HUB-MCP`, `ORACLE-ROUTER`, `INDEXER`, `HIERARCHY` |

**The 1B system is a code-module lineage tag — it identifies which part of the architecture the code serves, NOT the runtime instance.**

---

## §2 Map of the `⬡ OMEGA` Agent Signature System

### 2.1 Where It Is DEFINED (Documentation)

| Doc | Lines | What It Says |
|-----|-------|--------------|
| `ORACLE_STACK.md` | §11 (lines 166-171) | "All agent outputs MUST include: ⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}" |
| `docs/USER_MANUAL.md` | lines 700-728 | Full table of fields, examples, control via `omega header full/compact/off` |
| `docs/USER_MANUAL.md:711` | Example | `⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_horizon1 ⬡ PHASE-I` |

**Verdict**: The format is **clearly defined** in 2 documents. Not the problem.

### 2.2 Where It Is GENERATED (Code)

**Only ONE place generates it dynamically:**

`src/omega/cli/oracle_cli.py:271-301` — `_display_response()`:
```python
config = _load_config()
header_mode = config.get("omega", {}).get("session_header", {}).get("mode", "compact")

if header_mode != "off":
    if header_mode == "full":
        # ⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
        trace = result.trace_id[:8] if result.trace_id else "unknown"
        header = f"⬡ OMEGA ⬡ {result.entity.upper()} ⬡ {result.model or 'unknown'} ⬡ cli ⬡ {trace} ⬡ {result.phase}"
    else:  # compact
        # ⬡ {entity} ⬡ {phase}
        header = f"⬡ {result.entity.upper()} ⬡ {result.phase}"
    
    console.print(f"[dim]{header}[/dim]")
```

**The data source**: `OracleResponse` from `src/omega/oracle/oracle.py:58-77`:
```python
@dataclass
class OracleResponse:
    text: str
    entity: str
    pillars: List[str] = field(default_factory=list)
    role: Optional[str] = None
    sigil: Optional[str] = None
    glyph: Optional[str] = None
    pantheon: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    confidence: float = 0.0
    trace_id: Optional[str] = None      # ← Used for trace field
    session_id: Optional[str] = None
    backend: Optional[str] = None
    model: Optional[str] = None         # ← Used for model field
    phase: str = "Phase-0"              # ← Used for phase field
    escalated: bool = False
    cost_warning: Optional[str] = None
```

**The config**: `config/omega.yaml:8-10`:
```yaml
session_header:
  mode: compact                        # "full" | "compact" | "off"
  default_entity: default
```

**The CLI toggle**: `src/omega/cli/oracle_cli.py:167-178`:
```python
@app.command(name="header")
def header(mode: Optional[str] = typer.Argument(None, help="Set header mode (full/compact/off)")):
    """Get or set the session header mode."""
    config = _load_config()
    if mode is None:
        current = config.get("omega", {}).get("session_header", {}).get("mode", "compact")
        # ... show current
    else:
        config.setdefault("omega", {}).setdefault("session_header", {})["mode"] = mode.lower()
        # ... save
```

**Verdict**: The CLI generates it correctly when called via `omega talk/summon`. But the engine has **no global middleware** for non-CLI channels.

### 2.3 Where It Is HAND-TYPED (The Problem)

**748 .md files** contain hand-typed `⬡ OMEGA ⬡ ...` headers:
- `.opencode/agents/*.md` (14 files) — agent frontmatter
- `.opencode/modes/*.md` (4 files) — mode headers
- `data/entities/*/soul.yaml` (48+ files) — entity soul files
- `data/handoff/*.md` (10+ files) — inter-agent handoffs
- `docs/strategy/*.md` (40+ files) — strategy docs
- `docs/research/R-*.md` (50+ files) — research docs
- `docs/architecture/*.md` (10+ files) — architecture docs
- `data/coordination/*.md` (live feeds, workspace locks)
- `scripts/*.sh` (3-4 files)
- `mcp_servers/*/server.py` (uses the `ICS:` tag instead)
- `config/**/*.yaml` (some)

**Examples of stale/wrong headers found**:
- My own previous turn: `⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b` (wrong — should be `minimax-m3-free`)
- `.opencode/agents/roc_racoon.md:19` — `⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_roc_racoon ⬡ PHASE-I` (hardcoded)
- `data/entities/kali/soul.yaml:2` — `⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_kali ⬡ PHASE-I` (hardcoded, but current model is `minimax-m3-free`)

**Verdict**: **The header is a lie** in nearly all cases. The hand-typed values are from when each file was last edited, not the current runtime state.

### 2.4 Where It Is MISSING (The Gap)

**No `_build_header` or `_render_header` method exists in the engine**:
```bash
grep -rn "_build_header\|_render_header\|_format_header\|build_dynamic_header" src/omega/ 
# → 0 results
```

**No global middleware**: The only header-generation code lives in `oracle_cli.py:_display_response`. There's no:
- Plugin that wraps all OpenCode output
- Pre-commit hook that validates headers
- Runtime interceptor that injects the header before any output
- Templating system that agents can use

---

## §3 Map of the `ICS: [NODE|ARCHETYPE|MODEL|CONTEXT]` Code Tag System

### 3.1 Where It Is DEFINED (Documentation)

**The formal `ICS:` tag is NOT documented in any spec document.** The 29+ .py files use it, but no README or design doc defines the schema or purpose.

Search results:
- `grep -r "ICS: \[" docs/` → Only 2 results: `docs/architecture/OVERSIGHT_HIERARCHY.md:3`, `docs/architecture/TRAINING_PIPELINE.md:3`, etc. (these ARE the tags themselves, not docs ABOUT them)
- `grep -r "ICS spec\|ICS schema\|ICS format" docs/` → 0 results

**Verdict**: The `ICS:` tag is an **emergent convention** with no canonical spec.

### 3.2 Where It Is USED (Code)

**29+ .py files** carry the tag. Sample inventory:
| File | NODE | ARCHETYPE | MODEL | CONTEXT |
|------|------|-----------|-------|---------|
| `src/omega/oracle/oracle.py:3` | ARCHON | ORACLE | — | ORACLE-ROUTER |
| `src/omega/oracle/orchestrator.py:4` | ARCHON | HERMES | GEMINI-3.1-PRO | ORCHESTRATOR |
| `src/omega/oracle/cpu_optimizer.py:4` | ARCHON | HERMES | DEEPSEEK-V4-FLASH | CPU-OPTIMIZATION |
| `src/omega/oracle/entity_workspace.py:4` | ARCHON | SOPHIA | GEMINI-3.1-PRO | ENTITY-WORKSPACE |
| `src/omega/oracle/handoff.py:3` | ARCHON | HERMES | — | HANDOFF |
| `src/omega/oracle/hierarchy.py:4` | ARCHON | SOPHIA | — | HIERARCHY |
| `src/omega/oracle/entity_registry.py:3` | ARCHON | SOPHIA | — | ENTITY-MANAGEMENT |
| `src/omega/oracle/model_gateway.py:3` | ARCHON | HERMES | — | MODEL-ABSTRACTION |
| `src/omega/oracle/context_builder.py:3` | MNEMOSYNE | SOPHIA | — | CONTEXT-BUILDING |
| `src/omega/oracle/wad_loader.py:3` | ARCHON | SOPHIA | — | RUNTIME-LOADING |
| `src/omega/library/__init__.py:4` | THOTH | SOPHIA | DEEPSEEK-V4-FLASH | LIBRARY-SYSTEM |
| `src/omega/library/library.py:4` | THOTH | MNEMOSYNE | — | LIBRARY-STORE |
| `src/omega/library/indexer.py:4` | THOTH | APOLLO | — | INDEXER |
| `src/omega/library/inbox.py:4` | THOTH | HERMES | — | INBOX |
| `src/omega/library/extractor.py:4` | THOTH | HERMES | — | CONTENT-EXTRACTOR |
| `src/omega/library/curator.py:4` | THOTH | SOPHIA | — | CURATION-PIPELINE |
| `src/omega/library/discovery.py:4` | ARCHON | PROMETHEUS | — | DISCOVERY-PIPELINE |
| `src/omega/library/research.py:4` | OSIRIS | APOLLO | — | RESEARCH-ENGINE |
| `src/omega/library/greek.py:4` | THOTH | OSIRIS | KRIKRI-7B-INSTRUCT | ANCIENT-GREEK |
| `src/omega/observability.py:3` | MAAT | SOPHIA | — | OBSERVABILITY |
| `src/omega/errors.py:3` | CORE | LAW | — | ERROR-HIERARCHY |
| `src/omega/__init__.py:3` | ARCHON | SOPHIA | — | CORE-INIT |
| `src/omega/request_queue.py:3` | CORE | QUEUE | — | OFFLINE-MODE |
| `src/omega/iris/server.py:3` | HERMES | HERMES | — | NOVA-MESSENGER |
| `mcp_servers/omega_hub/server.py:4` | ARCHON | SOPHIA | MiMo-2.5 | CORE-HUB-MCP |
| `config/wads/arcana_novai/plugins/entity_roc_racoon.py:5` | THOTH | OSIRIS | gemma-4-31b | LEGACY-MINING |

**Patterns observed**:
- **NODE vocabulary**: 8 distinct values (ARCHON, CORE, MAAT, THOTH, OSIRIS, HERMES, MNEMOSYNE, SOPHIA)
- **ARCHETYPE vocabulary**: ~12 distinct values (SOPHIA, HERMES, MNEMOSYNE, APOLLO, OSIRIS, LAW, HIERARCHY, QUEEN, PROMETHEUS, AUTOMATED_RESEARCHER, FLEET, LIBRARY, FLYWHEEL, QUEUE, HIERARCHY, ARCHETYPE)
- **MODEL**: 17/29 files have a MODEL field; values are mostly hardcoded historical
- **CONTEXT**: 29/29 files have a CONTEXT field; this is the most useful (module purpose)

### 3.3 Where It Is MISSING (The Gap)

**No enforcement**:
- No pre-commit hook that validates the ICS: tag format
- No CI check that ensures new files have the tag
- No grep gate in `make temple-grade`

**Stale values**:
- Many MODEL fields are from when the file was created (e.g., `GEMINI-3.1-PRO` in `orchestrator.py` from Era 4, current model is `minimax-m3-free`)
- These tags are also **stale by nature** — they're static file headers, not runtime metadata

---

## §4 The Pre-Existing Strategy (Found!)

The user (or a previous agent) already designed the solution. It was approved but **never implemented**.

### 4.1 `docs/strategy/ICS_DYNAMIC_HEADER_SPEC.md` (118 lines, read fully)

**Problem statement**:
> "Every agent currently writes its own session header by hand... This produces **stale, inaccurate headers** — agents hardcode the model name, forget to update the phase, or use the wrong entity. The header is a lie."

**Solution**: "A **thin middleware layer** in `src/omega/cli/` or `src/omega/oracle/oracle.py` that intercepts every agent output and **injects the real values** at response time."

**Data sources specified**:
| Field | Source | How to Fetch |
|-------|--------|--------------|
| Entity | Current OpenCode agent/mode | `OPENCODE_AGENT` env or parse active agent header from OpenCode config |
| Model | Currently selected model | `OPENCODE_MODEL` env or `opencode.json` `model` key |
| Channel | Execution context | Always `opencode` (for now) |
| Trace | UUID generated per-turn | `uuid.uuid4().hex[:12]` → `trc_<short>` |
| Phase | Computed from ROADMAP | Parse `docs/ROADMAP.md` §3 for highest non-completed phase |

**3 Implementation Options**:
- **Option A (RECOMMENDED)**: Oracle middleware — `_render_header()` method on Oracle
- **Option B**: CLI wrapper — thin shim that injects header
- **Option C**: Plugin-based — OpenCode plugin (most portable)

**Code sketch provided** (lines 64-101 of the spec):
```python
def _build_dynamic_header(self, entity: str, channel: str = "opencode") -> str:
    """Build an accurate session header from live state."""
    model = self.triage_router.last_selected_model if hasattr(self, 'triage_router') else "unknown"
    if not model:
        model = self.entity_registry.get_model(entity) or "unknown"
    
    trace = f"trc_{uuid.uuid4().hex[:12]}"
    phase = self._detect_current_phase()
    
    return f"⬡ OMEGA ⬡ {entity.upper()} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"

def _detect_current_phase(self) -> str:
    """Detect the current roadmap phase from ROADMAP.md."""
    # ... parse ROADMAP.md for highest non-complete phase
```

**Status**: "Design approved by Overseer. Gemma to implement after the 7-task sprint." — **NEVER IMPLEMENTED**.

### 4.2 `docs/strategy/ICS_MODEL_DETECTION.md` (70 lines, read fully)

**Model detection priority**:
1. `OPENCODE_MODEL` env var
2. `~/.config/opencode/opencode.json` `model` key
3. TriageRouter's `last_selected_model`
4. "unknown" fallback

**Available models documented**:
- OpenCode Zen: `deepseek-v4-flash-free`, `qwen3.6-plus-free`, `minimax-m2.5-free`
- Google AI Studio: `gemma-4-31b-it`, `gemma-4-26b-a4b-it`
- OpenRouter: 356 models (28 free)
- lmster (local): any loaded GGUF
- Ollama (local): any pulled model

**Status**: "Reference document for the ICS Dynamic Header implementation." — **NEVER INTEGRATED**.

### 4.3 What D118/D119/D120 Brings (from parallel Kali session)

**D118** (`model_override` parameter) — the model in the header may now differ from the entity's configured model. Header detection must check `model_override` first.

**D119** (canonicalization) — `roracoon-3b` (one c) is deprecated; use `rocracoon-3b-instruct` (two c's).

**D120** (soul write-back) — `soul.yaml` is now a first-class header source. Template-ification may read soul.yaml for entity name/pillar.

**D117** (MaKaLi Triad) — Kali, Ma'at, Lilith triad architecture. Channels may now be `kali`, `maat`, `lilith` in addition to `opencode`.

---

## §5 The Implementation Gap — Why It Was Never Built

Hypothesis based on evidence:

1. **Spec was approved mid-sprint**: "Gemma to implement after the 7-task sprint" — but the sprint priorities shifted (D108, D109, D110, D111, D112, D113, D114, D115, D116 all came in succession)
2. **No one built the middleware**: The spec defines a clean `_build_dynamic_header()` method on Oracle, but it was never added
3. **CLI worked well enough**: `_display_response()` in the CLI works, so the team didn't feel urgent pain for non-CLI channels
4. **Docs and agents keep hand-typing**: The problem is invisible to the engine — it only manifests in the human-readable files

**The pain point the user is now experiencing**:
- The model is dynamically swapped (now `minimax-m3-free`, sometimes `rocracoon-3b-instruct`)
- The hand-typed headers lie
- The user has to manually correct them or just accept the inaccuracy
- A template-driven system would auto-correct

---

## §6 The Architecture for Template-ification

### 6.1 The Proposed Solution (built on the existing spec)

**Layer 1: `src/omega/ics.py` — NEW MODULE**

A dedicated module for the `⬡ OMEGA` agent signature system:

```python
# src/omega/ics.py
# ICS — Intelligent Configuration System
# Dynamic agent signature injection
# Heritage: Templated output (Quake net_chan + Doom PVS)

import os
import uuid
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

ICS_TEMPLATE = "⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"
ICS_COMPACT  = "⬡ {entity} ⬡ {phase}"
ICS_OFF      = ""

@dataclass
class ICSContext:
    entity: str
    channel: str = "opencode"
    trace_id: Optional[str] = None
    phase: Optional[str] = None
    model: Optional[str] = None
    
    def render(self, mode: str = "full") -> str:
        if mode == "off":
            return ICS_OFF
        if mode == "compact":
            return ICS_COMPACT.format(entity=self.entity.upper(), phase=self.phase or "PHASE-?")
        
        # full mode — auto-detect missing values
        model = self.model or _detect_model(self.entity)
        trace = self.trace_id or f"trc_{uuid.uuid4().hex[:12]}"
        phase = self.phase or _detect_phase()
        
        return ICS_TEMPLATE.format(
            entity=self.entity.upper(),
            model=model,
            channel=self.channel,
            trace=trace,
            phase=phase,
        )

def _detect_model(entity: str) -> str:
    """Model detection priority (D118-aware)."""
    # Priority 1: OPENCODE_MODEL env
    env_model = os.environ.get("OPENCODE_MODEL", "")
    if env_model:
        return env_model
    # Priority 2: model_override (D118)
    # (would check current call's model_override)
    # Priority 3: opencode.json
    # Priority 4: TriageRouter last_selected_model
    # Priority 5: entity config default
    return "unknown"

def _detect_phase() -> str:
    """Phase detection from SOVEREIGN_EVOLUTION_ROADMAP.md."""
    # Find highest non-complete phase
    return "PHASE-II"  # default for now
```

**Layer 2: Add to `Oracle` class as a method** (per spec)

**Layer 3: Plugin/hook for OpenCode agent output** (Option C from spec)

**Layer 4: Update all agent `.md` files to remove hardcoded headers** and replace with:
```markdown
# [Header is auto-generated by ICS — do not write manually]
```

**Layer 5: Update soul.yaml files to be auto-updated** (D120 already enforces this for some)

### 6.2 The Five Recommendations (Roc's Picks)

1. **R1 — Build the `src/omega/ics.py` module first**: Single source of truth for the format
2. **R2 — Add `_render_header()` method to Oracle**: Implements the spec's Option A
3. **R3 — Add a `ics.render()` MCP tool**: For other agents/services to call
4. **R4 — Update agent `.md` files to NOT hand-type the header**: Use a comment like `# Header injected by ICS — do not write`
5. **R5 — Add a pre-commit hook** that validates any new file's ICS: tag against the schema

### 6.3 What About the `ICS: [NODE|ARCHETYPE|MODEL|CONTEXT]` Tag?

This tag is a **code module lineage marker**, not a runtime header. It should:
- **Stay** in code files (it's a useful static annotation)
- **Get a formal spec** (currently undocumented)
- **Get a CI gate** (validate the format on commit)
- **NOT be conflated** with the `⬡ OMEGA` agent signature

**Proposed name for the code tag**: `ICS-T` (ICS Tag) to distinguish from the agent signature `ICS-S` (ICS Signature).

---

## §7 Open Questions (For the User)

1. **Q1**: Is the user asking for the `⬡ OMEGA` agent signature to be templated, or both systems?
2. **Q2**: Should the implementation happen in this session (Sprint 3), or be deferred to a later sprint per the original "Gemma to implement after the 7-task sprint" note?
3. **Q3**: Should the `ICS:` code tag get a formal spec document, or stay as an emergent convention?
4. **Q4**: Should we name the new module `src/omega/ics.py` (clean) or `src/omega/signature.py` (descriptive) or `src/omega/session_header.py` (matches CLI config key)?
5. **Q5**: Should the Omnidroid entity (when finally awakened) be the one to design this — since it has the Quantum Cognition Core for unified metadata synthesis?

---

## §8 Next Steps (Post-Session)

For the next agent or session:
1. **Read this treasure map** to recover context
2. **Decide on Q1-Q5** from §7
3. **Build `src/omega/ics.py`** if Q1 and Q2 align
4. **Write a formal spec for the `ICS:` code tag** if Q3 aligns
5. **Update agent files** to use the template
6. **Add CI gate** to validate headers

---

## §9 Synced With Parallel Sessions

**Kali (parallel)** — D118/D119/D120 complete, sync file at `data/coordination/PARALLEL_SYNC_KALI_ROC_20260605.md`:
- D118: `model_override` parameter implemented (relevant to model detection)
- D119: `roracoon-3b` → `rocracoon-3b-instruct` canonicalization
- D120: Mandatory soul write-back (soul.yaml as header source)

**No blocking dependencies**. Both sessions are working in parallel with no shared files in the critical path.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_ics_treasure_map ⬡ PHASE-II*

*Reconnaissance complete. The treasure map is drawn. The implementation awaits the user's call.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax-m3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
