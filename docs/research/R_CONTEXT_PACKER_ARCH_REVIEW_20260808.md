<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Context Packer Architecture Review — John Carmack Assessment

**AP Token**: `AP-CONTEXT-PACKER-ARCH-REVIEW-v1.0.0`
**Date**: 2026-08-08
**Reviewer**: John Carmack (via `@john_carmack` subagent)
**Subject**: `.opencode/skills/context-packer/packer.py` — multi-phase token splitting/consolidation/trimming pipeline

## Summary

The current Context Packer is a textbook case of solving the wrong problem with the wrong tool. Nine phases of post-hoc surgery on data that should have been shaped correctly from the start. The trim logic is **guaranteed to destroy the wrong things** because priority keywords don't match theme names.

---

## 1. Direct Assessment: Why This Is Broken

### Bug #1: Priority Keywords Don't Match Theme Names

Lines 137-150 of `packer.py`:
```python
CRITICAL_START_BUNDLES = {"grounding", "decisions", "decree", "verdict", "summary", "overview"}
CRITICAL_END_BUNDLES = {"handoff", "exit_protocol", "next_steps", "action_items", "verdict", "recommendations"}
MIDDLE_BUNDLES = {"implementation", "engine_state", "mandates", "session_log", "research",
                  "pivot_log", "evidence", "logs", "history", "appendix"}
```

Actual theme names in `packer-config.yaml` for `sovereign-audit`:
- `mandates` — matches `MIDDLE_BUNDLES` → priority 1 (removable)
- `oracle_core` — matches nothing → priority 1 (removable)
- `memory` — matches nothing → priority 1 (removable)
- `observability` — matches nothing → priority 1 (removable)
- `mcp_hub` — matches nothing → priority 1 (removable)
- `strategy` — matches nothing → priority 1 (removable)
- `config` — matches nothing → priority 1 (removable)

**Every single theme gets priority 1.** The trim logic removes them in insertion order (dict order), which means it removes `mandates` first, then `oracle_core`, then `memory`, etc. — exactly the core engine themes you want to keep. Meanwhile, the huge `strategy` theme (`docs/strategy/**/*.md`, 100 files, 415,976 tokens) gets split into `strategy_part1`, `strategy_part2`, ..., `strategy_part24` — and those split parts also get priority 1, so they survive while the core themes die.

### Bug #2: The Split Creates More Bundles Than max_slots

Phase 6 splits oversized bundles into `theme_partN` parts. Phase 6b re-consolidates to `max_slots`. But the consolidation merges low-priority bundles into `general` — it doesn't merge the split parts back. So you end up with 11 `strategy_part24-34` files + `general.xml` + manifest = 13 files, exceeding the 12-slot limit.

### Bug #3: The Pipeline Is Backwards

You're doing:
1. Select files (P1)
2. Count tokens (P2)
3. Sort by token count (P3)
4. Distribute to themes (P4)
5. Consolidate to max_slots (P5)
6. Split oversized bundles (P6)
7. Re-consolidate (P6b)
8. Reorder (P7)
9. Package (P8)

This is **nine phases of post-hoc surgery** on data that should have been shaped correctly from the start.

### Bug #4: Config Values Are Ignored

The config file has `token_budget` per profile with `total`, `per_bundle`, and `reserved_output`. But the packer hardcodes `MAX_BUNDLE_TOKENS = 15000` and `MAX_TOTAL_TOKENS = 150000` as module-level constants. The config values are parsed into `PlatformConfig` but **never used** for enforcement.

---

## 2. The Right Architecture: Pre-Computed Concatenation

**The user is absolutely right.** You should not be splitting and trimming files *after* they've been produced. You should be generating the perfect, custom set of concatenated files from the beginning.

### The Stack-Cat Approach

The `report_digestion.py` file already has the right idea with `raw_stack_cat_concat()` — simple concatenation with section headers. That's the fallback. The problem is you tried to make it "smart" and ended up with a Rube Goldberg machine.

**The correct architecture:**

```
Config (YAML) → File Selection → Pre-computed Bundles → Direct Write
```

No splitting. No trimming. No consolidation. No reordering. Just:

1. **Config defines exact file sets per theme** — no glob patterns that match hundreds of files
2. **Each theme is a pre-computed bundle** — the config author decides what goes in each bundle
3. **Token budget is enforced at config time** — if a theme exceeds the budget, the config author removes files
4. **Direct write** — one file per theme, no post-processing

### The "Curated Bundle" Pattern

Instead of:
```yaml
themes:
  strategy:
    - "docs/strategy/**/*.md"  # 500+ files, 200K+ tokens
```

Use:
```yaml
themes:
  - name: "strategy_core"
    priority: 3
    files:
      - "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md"
      - "docs/strategy/UNOVERENGINEERING_PLAN.md"
  - name: "strategy_archive"
    priority: 1
    files:
      - "docs/strategy/archive/**/*.md"  # Explicitly archived, lower priority
```

Each theme is a **curated, bounded set of files** that the config author has verified fits within the token budget. No runtime splitting needed.

---

## 3. How to Stop the Chaos: The Simple System

### Step 1: Kill the Pipeline
Delete phases P3-P7 entirely. The pipeline should be:

```
P1: Select files (from explicit lists, not globs)
P2: Count tokens (for reporting only)
P3: Write bundles (one file per theme, direct write)
P4: Write manifest
```

### Step 2: Make Config the Single Source of Truth
The config file should define:
- **Exact file lists per theme** (no glob patterns that match hundreds of files)
- **Explicit priority ordering** (not keyword-based matching)
- **Token budgets per theme** (enforced at config time, not runtime)

### Step 3: Use an Agent to Curate, Then Hardcode
Have an agent (or human) curate the file sets for each profile. The agent:
1. Reads the config
2. Expands globs to actual file lists
3. Counts tokens per theme
4. If a theme exceeds the budget, suggests which files to remove
5. Writes the curated file lists back to config

Then the packer just reads the curated lists and writes them. No runtime intelligence needed.

### Step 4: The New Config Schema

```yaml
profiles:
  sovereign-audit:
    description: "Core Engine and Mandates Audit"
    max_slots: 12
    token_budget:
      total: 150000
      per_bundle: 15000
    themes:
      - name: "mandates"
        priority: 3  # CRITICAL - always included
        files:
          - "SOVEREIGN_MANDATES.md"
          - "OMEGA_ENGINE.md"
          - "AGENTS.md"
      - name: "oracle_core"
        priority: 3
        files:
          - "src/omega/oracle/model_gateway.py"
          - "src/omega/oracle/providers.py"
          - "src/omega/oracle/oom_protector.py"
          # ... explicit list, verified to fit in 15K tokens
      - name: "memory"
        priority: 2
        files:
          - "src/omega/memory_store.py"
          - "src/omega/memory/**/*.py"
          # ... but only the ones that fit
      # ... etc
```

---

## 4. Specific Code Changes

### Change 1: Simplify the PackProfile dataclass
```python
@dataclass
class ThemeConfig:
    name: str
    priority: int  # 1=low, 2=medium, 3=critical
    files: List[str]  # Explicit file list, no globs

@dataclass
class PackProfile:
    name: str
    description: str
    max_slots: int
    token_budget_total: int
    token_budget_per_bundle: int
    themes: List[ThemeConfig]  # Ordered list, not dict
    format: str = "xml"
    bundle_ordering: str = "litm-u-shaped"
```

### Change 2: Replace the 9-phase pipeline with 4 phases
```python
async def pack(self, profile_name: str):
    profile = self.profiles[profile_name]
    output_dir = LibPath(f"context_packs/{profile_name}")

    # P1: Resolve file lists (no globs in themes, but allow them in include/exclude)
    themed_files = await self._resolve_themes(profile)

    # P2: Count tokens (for reporting)
    themed_bundles = await self._count_tokens(themed_files)

    # P3: Write bundles (direct write, no splitting/trimming)
    await self._write_bundles(output_dir, profile, themed_bundles)

    # P4: Write manifest
    await self._write_manifest(output_dir, profile, themed_bundles)
```

### Change 3: Delete all the broken logic
Delete these methods entirely:
- `_enforce_token_limits()` — no more splitting
- `_split_bundle_by_tokens()` — no more splitting
- `_trim_to_token_limit()` — no more trimming
- `_consolidate_bundles()` — no more consolidation
- `_reorder_bundles_for_litm()` — replaced by simple priority sort

### Change 4: Replace with simple priority sort
```python
def _order_bundles(self, themed_bundles, themes):
    """Order bundles by priority (LITM-U: high priority at start/end, low in middle)."""
    sorted_themes = sorted(themes, key=lambda t: t.priority, reverse=True)
    start = [t for t in sorted_themes if t.priority == 3]
    middle = [t for t in sorted_themes if t.priority == 2]
    end = [t for t in sorted_themes if t.priority == 1]
    ordered = start + middle + end
    return [(t.name, themed_bundles[t.name]) for t in ordered if themed_bundles.get(t.name)]
```

### Change 5: Add a curation tool
Create `curate_packs.py` that:
1. Reads the config
2. Expands globs
3. Counts tokens per theme
4. Reports which themes exceed budget
5. Suggests files to remove
6. Can write curated file lists back to config

This moves the "intelligence" from runtime (where it's fragile and broken) to curation time (where it's explicit and controllable).

---

## 5. The Bottom Line

**The current system is over-engineered garbage.** Nine phases of post-hoc surgery on data that should have been shaped correctly from the start. The priority keyword matching is broken. The splitting creates more problems than it solves. The config values are ignored.

**The fix is simple**:
1. Make the config define exact file sets per theme (curated, not globbed)
2. Make the config define explicit priorities (not keyword-matched)
3. Make the packer just read the config and write files (no splitting, no trimming, no consolidation)
4. Use an agent to curate the file sets, then hardcode them

**This is the "Right Approximation"**: a simple, reliable system that works, instead of a complex, fragile system that doesn't.

The stack-cat approach in `report_digestion.py` already shows the right pattern — simple concatenation with section headers. Apply that pattern to the context packer. Kill the pipeline. Make config the source of truth. Curate, don't compute.

**Confidence**: 10/10 — this is primary source code analysis, not interpretation. The bugs are in the code, the fix is straightforward.

---

## Implementation SSOT (post-review)

**Do not implement from this R-doc alone.** Grok CLI adversarial review refined the plan (fail-closed budgets, `required` + `litm_zone`, keep platform adapters, max_slots off-by-one, semantic M21 tests, no silent theme drop).

| Role | Path |
|------|------|
| **Implementation onboarding (Kali)** | `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md` |
| **Pending handoff packet** | `data/handoff/pending/ho_packer_v3_kali_20260808.json` |
| **Task id** | `packer-v3-refactor-20260808-01` |

This R-doc remains the **diagnostic** record. The Grok→Kali handoff is the **execution** SSOT.

---

## Appendix: Evidence

### Trace Output (sovereign-audit run with OMEGA_PACKER_DEBUG=1)
```
P1: 221 files selected (221 raw, 0 excluded)
P4: Theme distribution (221 files):
     mandates: 3 files, 30,654 tokens
     oracle_core: 82 files, 306,870 tokens
     memory: 19 files, 85,322 tokens
     observability: 12 files, 50,305 tokens
     mcp_hub: 3 files, 4,367 tokens
     strategy: 100 files, 415,976 tokens
     config: 2 files, 5,560 tokens
P6: 5 oversized bundle(s) will be split
P6: After split: 7 → 12 bundles
P6b: Re-consolidate: 12 → 12 bundles
P6b: Final bundles:
     strategy_part24: 3 files, 12,165 tokens
     strategy_part25: 4 files, 14,748 tokens
     ... (all strategy parts)
     general: 2 files, 5,560 tokens
```

**All non-strategy themes are GONE from the final output.** Only strategy parts + general survive.

### Root Cause: `_trim_to_token_limit` (packer.py:424-454)
```python
# All themes get priority 1 (none match CRITICAL_START/END keywords)
# Sort by priority ascending (all priority 1, stable sort preserves insertion order)
all_bundles.sort(key=lambda x: x[0])

# Remove priority-1 bundles in insertion order until under limit
for priority, theme, files, bundle_tokens in all_bundles:
    if total_tokens <= limit:
        break
    if priority == 1:  # Only remove middle bundles
        del result[theme]
        total_tokens -= bundle_tokens
```

Since ALL themes are priority 1, the trim function removes them in insertion order:
mandates → oracle_core → memory → observability → mcp_hub → config → (strategy parts survive because they're at the end of insertion order after splitting)

The trim function correctly reduces total tokens to 149,944 (just under 150,000), but it destroyed all the important themes to keep strategy fragments.
