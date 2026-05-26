# 🔱 Omega Engine — Strategic Audit Remediation Build Brief
# Overseer → Gemma 4 31B (Builder Mode)

**AP Token**: `AP-BUILDER-BRIEF-AUDIT-REMEDIATION-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_builder_handoff ⬡ AUDIT-REMEDIATION
**Recommended Model**: `gemma-4-31b-it` (Google AI Studio — unlimited usage, 262K context)
**Recommended Mode**: `builder` (`.opencode/agents/builder.md`)
**Vision**: NOT required for these tasks (all file-based code changes)

---

## §0 How to Use This Brief

This brief contains the prioritized action plan to remediate the findings from the **Overseer's Strategic Audit (2026-05-26)**. 

### Your Operating Rules

1. **Read the file before editing** — Every `edit()` call must be preceded by a `read()` of the target file.
2. **`make test` after every task** — Run `make test` after each commit-worthy change. If tests break, fix before moving on.
3. **Commit after every task** — `git add -A && git commit -m "Audit Remediation: <task description>"`. This creates a checkpoint trail.
4. **Ask about ANY ambiguity** — If a file path is wrong, a line number is off, or a fix seems wrong, stop and ask. Do NOT guess.

---

## §1 Priority Queue

| Priority | # | Task | Files | Est. | Depends On |
|----------|---|------|-------|------|------------|
| **P0** | 1 | Fix `_grow_frontier()` to parse `MASTER_LEDGER.md` | `src/omega/workers/background_researcher/loop.py` | 15 min | — |
| **P1** | 2 | Document Dual-Load & Native GGUF Roadmap | `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` | 10 min | — |
| **Final** | 3 | `make lint` + `make test` + git commit | — | 10 min | All above |

---

## §2 Detailed Tasks

### TASK 1: Fix `_grow_frontier()` to parse `MASTER_LEDGER.md` (P0 — 15 minutes)

**File**: `src/omega/workers/background_researcher/loop.py`
**Lines**: 363-372
**Bug**: The method attempts to parse `docs/ROADMAP.md` to seed the research queue with uncompleted roadmap tasks. However, `docs/ROADMAP.md` has been superseded by `docs/MASTER_LEDGER.md` and is now a simple redirect file. This causes the parser to silently return zero candidates from the roadmap.

**Current code** (lines 363-372):
```python
        roadmap_path = Path("docs/ROADMAP.md")
        if roadmap_path.exists():
            text = roadmap_path.read_text()
            current_phase: Optional[str] = None
            for line in text.split("\n"):
                phase_match = re.match(r"^### Phase (\w+):", line)
                if phase_match: current_phase = phase_match.group(1)
                task_match = re.match(r"^\|\s*(\w[\w.]*)\s*\|.*?\|.*?\|.*?(🔴|🟡)", line)
                if task_match and current_phase:
                    candidates.append({"topic": f"Phase {current_phase} task {task_match.group(1)} — implementation research", "source": "roadmap", "priority": 0.6, "depth": 1})
```

**Fix**: Update the method to parse `docs/MASTER_LEDGER.md` instead. In `docs/MASTER_LEDGER.md`, the uncompleted phases are listed in a markdown table under `## Current Phases` and are marked with `📅`, `🔴`, or `🟡` icons.

Replace the block with:
```python
        ledger_path = Path("docs/MASTER_LEDGER.md")
        if ledger_path.exists():
            text = ledger_path.read_text()
            for line in text.split("\n"):
                if line.startswith("|") and any(icon in line for icon in ("📅", "🔴", "🟡")):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        phase_raw = parts[1].replace("**", "").strip()
                        goal = parts[2].strip()
                        candidates.append({
                            "topic": f"{phase_raw} — {goal} research",
                            "source": "master_ledger",
                            "priority": 0.6,
                            "depth": 1
                        })
```

**Verification**:
- Run `make test` to ensure no regressions.
- (Optional) Run the background researcher loop once to verify it successfully seeds uncompleted phases from the Master Ledger into the queue.

---

### TASK 2: Document Dual-Load & Native GGUF Roadmap (P1 — 10 minutes)

**File**: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`
**Action**: Add a new section `## §16: Strategic Roadmap Gaps` to document the migration timeline for deprecating `config/entities.yaml` (resolving the dual-load debt) and the path to full native GGUF integration in v0.6.0.

Append the following content to the end of the file:
```markdown

---

## §16: Strategic Roadmap Gaps (Audit Remediation)

During the pre-PR strategic audit, two key architectural gaps were identified and deferred to the v0.6.0 release cycle to ensure immediate PR stability:

### 1. Deprecation of `config/entities.yaml` (Dual-Load Resolution)
- **Gap**: The engine currently loads baseline entities from `config/entities.yaml` (via `EntityRegistry`) and then overlays stack-specific entities via the `WADLoader`. This dual-loading mechanism introduces minor performance overhead and potential namespace collisions.
- **Roadmap**: In v0.6.0, `config/entities.yaml` will be fully deprecated. All entity configurations will be migrated into their respective IWAD directories (e.g., `config/wads/_omega_default/entities/`). The `EntityRegistry` will load exclusively from the active IWAD stack, enforcing a clean Engine-Stack Firewall.

### 2. Native GGUF Integration Path
- **Gap**: Native GGUF inference (`llama-cpp-python`) is currently deferred to v0.6.0 to avoid environment-specific C++ compilation risks during the PR sprint.
- **Roadmap**: In v0.6.0, native GGUF will be promoted to the primary local inference provider. The engine will ship with pre-compiled wheels or a streamlined one-click compilation script for Zen 2 (AVX2) architectures, ensuring true out-of-the-box local-first sovereignty.
```

**Verification**:
- Verify the file compiles cleanly as markdown.

---

## §3 Final Verification

Once both tasks are complete, run the final quality gates:
1. `make test` — All 259 tests must pass.
2. `make lint` — Code style must be clean.
3. Commit the changes:
   ```bash
   git add -A
   git commit -m "Audit Remediation: Fix background researcher loop and document strategic gaps"
   ```

---
*Remediation brief approved by Overseer. Proceed to execution.*
