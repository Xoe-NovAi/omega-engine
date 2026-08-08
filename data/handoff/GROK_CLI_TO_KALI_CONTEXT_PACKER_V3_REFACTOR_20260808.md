# 🔱 Grok CLI → Kali — Context Packer v3 Full Refactor Onboarding
**AP Token**: `AP-GROK-TO-KALI-PACKER-V3-20260808-v1.0.0`
⬡ OMEGA ⬡ GROK_CLI ⬡ grok-4.5 ⬡ opencode ⬡ trc_handoff ⬡ ACTIONABLE

**Date**: 2026-08-08  
**From**: `@grok_cli` (Consulting Cloud Mind) — independent adversarial review  
**To**: `@kali` (Transcendent Oversoul) — OpenCode CLI implementer / dispatcher  
**Priority**: P0 — **before** any further Web Claude pack generation or upload  
**Related packet**: `data/handoff/pending/ho_8bfa50cb1e1d.json` (advisory review — complete)  
**Carmack review**: `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md`  
**Your gnosis**: `data/entities/kali/session_gnosis.md` § “Context Packer Hardening”

---

## 0. Executive Order (Read This First)

**You are authorized and expected to execute the Context Packer v3 refactor.**

| Item | Status |
|------|--------|
| Bug (sovereign-audit destroys core themes) | **CONFIRMED** — tool is broken (M23) |
| Carmack diagnosis | **ACCEPTED** (with refinements below) |
| Grok CLI adversarial review | **BINDING for implementation deltas** |
| Current `context_packs/sovereign-audit/` on disk | **POISONED** — 13 files, strategy shards only — do **not** upload |
| Code style for this work | Plan → Verify → Execute (M4). AnyIO only (M1). No silent drop (M23). |

**One-line doctrine (lock this):**

> **Curate at config-time. Validate at pack-time. Never silently delete themes to fit a budget.**

If over budget or over slots → **`[PACK-FAIL]`** and stop. Curation fixes the config; the packer does not “helpfully” drop `mandates`.

---

## 1. Mission

Deliver a **Context Packer v3** that:

1. Makes `packer-config.yaml` the **single source of truth** for file sets, budgets, required themes, and LITM zones.
2. Removes the broken split / trim / keyword-priority / dual-consolidate pipeline.
3. Adds `curate_packs.py` so intelligence lives **offline**, not in runtime surgery.
4. Keeps platform adapters (LITM-U), PII hard-stop, XML escape, Ed25519 sign.
5. Regenerates **two ship packs** with real success criteria:
   - `sovereign-audit` ≤12 project files (incl. manifest), **all required engine themes present**
   - `tech-architecture-research` ≤12 project files, research themes present, hand-built knowledge **not wiped**
6. Leaves `tests/contract/test_context_packer.py` green **and expands** it so M21 cannot false-pass again.

**Out of scope for this sprint:** rewriting every historical profile to perfection; full MCP/Web platform redesign; deleting PII/signing.

---

## 2. Reading Order (Hydration — do in order)

| # | Path | Why |
|---|------|-----|
| 1 | **This file** | Implementation law for the refactor |
| 2 | `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md` | Carmack primary diagnosis + kill-list |
| 3 | `data/entities/kali/session_gnosis.md` (packer section) | Your prior bug trace |
| 4 | `.opencode/skills/context-packer/packer.py` | Live v2 — especially `:132–150`, `:370–528`, `:591–815`, `:954–955` |
| 5 | `.opencode/skills/context-packer/packer-config.yaml` | `sovereign-audit` + `tech-architecture-research` only first |
| 6 | `.opencode/skills/context-packer/platform_adapters.py` | **Keep** — `PlatformConfig`, format adapters, `LITMUShapedStrategy` |
| 7 | `tests/contract/test_context_packer.py` | Baseline M21 — must stay green; must be extended |
| 8 | `context_packs/sovereign-audit/00_PROJECT_MANIFEST.md` | Proof of poisoned output |
| 9 | `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` (packer sections) | External upload constraints / ≤12 files |

Optional archaeology: `git show 8a747deb^:.opencode/skills/context-packer/packer.py` (pre-v2), `archive/packer_v1_legacy.py`.

**Do not trust** `data/coordination/grok_cli/RAPID_ONBOARDING_PACK.md` (unrelated/stale D-281).

---

## 3. Ground Truth — What Is Broken

### 3.1 Confirmed product failure

**Profile:** `sovereign-audit`  
**On disk (2026-08-08):** 13 files under `context_packs/sovereign-audit/`:

- `00_PROJECT_MANIFEST.md`
- `general.xml` (config leftovers)
- `strategy_part24.xml` … `strategy_part34.xml` (11 shards)

**Missing entirely:** `mandates`, `oracle_core`, `memory`, `observability`, `mcp_hub` (and coherent `config` as a first-class theme).

Trace (from Carmack / your debug run): ~221 files / ~899K tokens selected → after pipeline only strategy fragments + general survive under ~150k total.

### 3.2 Root causes (code-backed)

| ID | Defect | Location | Effect |
|----|--------|----------|--------|
| **B1** | Keyword priority sets don’t match engine theme names | `packer.py:137–150`, used at `:424–435`, `:798–802` | Every theme → priority 1 |
| **B2** | `_trim_to_token_limit` deletes priority-1 in insertion order | `packer.py:424–454` | Drops mandates→oracle→memory… first; keeps late strategy parts |
| **B3** | Config `token_budget` parsed, never enforced | `PlatformConfig` in adapters; packer uses `MAX_BUNDLE_TOKENS`/`MAX_TOTAL_TOKENS` at `:132–133` | `tech-architecture-research` 200k/20k ignored |
| **B4** | Unbounded globs (`docs/strategy/**/*.md`, `oracle/**/*.py`) | `packer-config.yaml` sovereign-audit | Input mass that no post-hoc trim can salvage honestly |
| **B5** | max_slots off-by-one | `_consolidate_bundles` `:492–528` | `max_slots-1` then may add `general` → up to max_slots themes **+ manifest = max_slots+1 files** (13 observed) |
| **B6** | Soft-fail on over-limit / missing files / injection | `:889–902`, `:954–955` | M23 theater — warns and continues |
| **B7** | Contract tests false-green | `test_context_packer.py` | “manifest + ≥1 bundle” never asserts theme survival or slot cap |
| **B8** | Dual SSOT: `include` ∪ `themes` | config + P1/P4 | Themes only bucket after fat include; easy desync |
| **B9** | Dead code / dual paths | `_reorder_bundles_for_litm`, unused `MIDDLE_BUNDLES` | Confusion; P7 uses adapters but feeds keyword garbage priorities |

### 3.3 M23 status (say it explicitly)

**`[TOOL-CHAIN-COLLAPSE]` for external audit delivery via current packer:**  
Context Packer v2 **must not** be used to ship `sovereign-audit` to Web Claude until v3 + curator + semantic tests pass.

---

## 4. Synthesis — Carmack vs Grok CLI (Locked Decisions)

Treat the right column as **implementation law**.

| Topic | Carmack | Grok CLI refinement | **LOCK** |
|-------|---------|---------------------|----------|
| Kill split/trim/consolidate | Yes | Yes | **Delete** those methods; no runtime theme drop |
| Config as SSOT | Yes | Themes list = selection SSOT | **Themes own files**; include derived or validated |
| Curator tool | Yes | Mandatory gate; shared token estimator | **`curate_packs.py` + pack validates** |
| No globs ever | Absolute ban | Ban **unbounded fat-tree** globs; small controlled globs OK if curator fails closed | **Curator must pass** |
| No split ever | Absolute ban | Default no split; single file over budget → **FAIL**; optional explicit `allow_split` later only | **Fail closed v3** |
| Kill reorder | Delete reorder | Keep **one** order step via `platform_adapters` + explicit `litm_zone` | **Keep adapters** |
| Single `priority: 1|2|3` | Proposed | **Insufficient** — collides keep vs position | **`required` + `litm_zone`** |
| Pipeline | resolve→count→order→write | + **validate** (budget/slots/required) before write | **5 steps** |
| PII + sign | Not emphasized | Keep hard-stop PII + Ed25519 | **Keep** |
| Tests | Mention M21 | Expand semantic contracts **before** trusting green | **Red tests first preferred** |

### Doctrine restated for agents

1. **No silent drop.** Over budget → fail with per-theme table.  
2. **Drop-priority ≠ LITM position.** Use `required` + `litm_zone`.  
3. **Manifest counts toward max_slots.**  
4. **Same token function** in curator and packer (including any safety margin policy).  
5. **Never `rm -rf` a profile output dir** that holds hand-authored knowledge (tech-architecture).

---

## 5. Target Architecture (v3)

```
packer-config.yaml ──► load_config
        │
        ▼
   resolve paths (expand theme files; optional lockfile)
        │
        ▼
   count tokens (shared estimator)
        │
        ▼
   validate ── FAIL ──► [PACK-FAIL] print table, non-zero exit
        │ OK
        ▼
   order (LITM by litm_zone → platform strategy)
        │
        ▼
   write bundles + manifest (format adapter)
        │
        ▼
   PII vault (if any) + Ed25519 sign
```

**Deleted in v3 (do not reintroduce):**

- `_enforce_token_limits`
- `_split_bundle_by_tokens`
- `_trim_to_token_limit`
- `_consolidate_bundles`
- `_reorder_bundles_for_litm`
- `CRITICAL_START_BUNDLES` / `CRITICAL_END_BUNDLES` / `MIDDLE_BUNDLES` keyword sets (unless behind a legacy flag you immediately delete after migration)
- Module-level hard enforcement via `MAX_*` when `PlatformConfig` budgets exist (constants may remain as **defaults only** when platform block absent)

**Kept:**

- AnyIO + `to_thread` for IO/hash/tiktoken
- `_escape_bare_xml_chars`, atomic write, purpose/sha metadata
- `platform_adapters.py` entire public API
- PIIMasker hard import failure → refuse pack
- Manifest signing
- `OMEGA_PACKER_DEBUG` / `OMEGA_PACKER_TRACE`

---

## 6. Config Schema (v3) — Spec Lock

Implement this shape for **at least** the two ship profiles. Other profiles can migrate incrementally but must not crash the loader.

```yaml
profiles:
  sovereign-audit:
    description: "Core Engine and Mandates Audit"
    target_platform: "web-claude"
    target_model: "claude-sonnet-5"
    max_slots: 12                    # TOTAL files on disk including manifest
    format: "xml"
    bundle_ordering: "litm-u-shaped"
    output_dir: "context_packs/sovereign-audit"   # optional explicit
    # Selection SSOT = themes[].files (recommended).
    # If global include/exclude retained: validate theme files ⊆ resolved include.
    exclude:
      - "**/__pycache__/**"
      - "**/*.pyc"
      - "context_packs/**"
    token_budget:
      total: 150000                  # MUST drive packer
      per_bundle: 15000
      reserved_output: 50000         # informational / future; document if unused
    prompt_caching:
      enabled: true
      cache_prefix: ["manifest", "mandates"]
    themes:
      - name: mandates
        required: true               # missing or over per_bundle → PACK-FAIL
        litm_zone: start             # start | middle | end
        files:
          - "SOVEREIGN_MANDATES.md"
          - "OMEGA_ENGINE.md"
          - "AGENTS.md"
      - name: oracle_core
        required: true
        litm_zone: middle
        files:
          # EXPLICIT curated list — NOT src/omega/oracle/**/*.py
          - "src/omega/oracle/model_gateway.py"
          - "src/omega/oracle/providers.py"
          - "src/omega/oracle/oom_protector.py"
          - "src/omega/oracle/admission_controller.py"
          - "src/omega/oracle/health_monitor.py"
          - "src/omega/oracle/resource_guard.py"
      # ... additional themes ...
```

### Field semantics

| Field | Meaning |
|-------|---------|
| `required: true` | Theme must appear in output; over `per_bundle` or missing files → fail |
| `required: false` | Still must fit if present; prefer fail over silent omit in v3 (simpler) — or omit only if curator removed it from config |
| `litm_zone` | Attention layout only — **not** drop rank |
| `files` | Explicit paths preferred; globs allowed only if curator proves theme ≤ `per_bundle` |
| `max_slots` | `len(content_bundles) + 1(manifest) <= max_slots` |

### Mapping to platform adapters

When building bundle dicts for `ordering_strategy.order()`:

```text
litm_zone start  → priority 3
litm_zone middle → priority 2
litm_zone end    → priority 1
```

(Matches existing `LITMUShapedStrategy` in `platform_adapters.py:69–81`.)

**Do not** invent a second ordering implementation in `packer.py`.

---

## 7. Execution Plan (Phased)

### Phase 0 — Spec + workspace (30–60 min)

- [ ] Workspace lock: `data/coordination/KALI_WORKSPACE_LOCK_YYYYMMDD.md` for packer paths  
- [ ] Hivemind post (intent=`handoff` or `status`) citing this doc + task id  
- [ ] Confirm poisoned pack remains quarantined (no upload)  
- [ ] Decide estimator policy: keep 1.3× margin **or** raw tiktoken — **document in SKILL.md** and use **identically** in curator + packer  

**Task id (STRP):** `packer-v3-refactor-20260808-01`

### Phase 1 — Semantic tests first (red) (1–2 h)

Extend `tests/contract/test_context_packer.py` **and/or** add `tests/contract/test_context_packer_v3.py` with a **tiny fixture config** under `tests/fixtures/context_packer/` (do not depend on full-repo sovereign-audit for unit speed).

**Required assertions:**

| Test | Must prove |
|------|------------|
| `test_budget_from_platform_config` | Enforcement uses profile budget, not only module constants |
| `test_over_total_budget_raises` | No trim; hard fail |
| `test_required_theme_missing_raises` | Missing required theme → fail |
| `test_max_slots_includes_manifest` | On-disk file count ≤ `max_slots` |
| `test_litm_zone_ordering` | start themes before middle before end (or U-shape as strategy defines) |
| `test_no_keyword_priority_side_effects` | Theme named `mandates` is not special-cased by substring sets |
| Keep existing 10 adapter/registry/load/pack smoke tests | Still green |

### Phase 2 — `curate_packs.py` (1–2 h)

Path: `.opencode/skills/context-packer/curate_packs.py`

**Behavior:**

1. Load profile from `packer-config.yaml`  
2. Expand each theme’s `files` (globs allowed here)  
3. Count tokens with **shared** helper (import from packer or `token_util.py`)  
4. Print table: theme, file count, tokens, per_bundle headroom, required flag  
5. Exit **non-zero** if any theme > `per_bundle` or sum > `total` or file missing  
6. Optional `--write-lock PATH` → expanded concrete file lists for reproducibility  
7. **No** auto-rewrite of YAML without explicit `--apply` (avoid agent thrash)

CLI sketch:

```bash
.venv/bin/python .opencode/skills/context-packer/curate_packs.py sovereign-audit
.venv/bin/python .opencode/skills/context-packer/curate_packs.py tech-architecture-research
```

### Phase 3 — Packer v3 rewrite (2–4 h)

Rewrite `pack()` to:

1. `resolve_themes(profile)` → `Dict[str, List[file_info]]`  
2. `count` (may merge with resolve)  
3. `validate_budgets_and_slots(profile, themed)` → raise `RuntimeError("[PACK-FAIL] ...")` with table  
4. `order` via `get_ordering_strategy` + litm_zone→priority  
5. `write` via adapter + PII + sign  

**Wire budgets:**

```python
per_bundle = profile.platform.token_budget_per_bundle if profile.platform else DEFAULT_PER_BUNDLE
total = profile.platform.token_budget_total if profile.platform else DEFAULT_TOTAL
max_slots = profile.max_slots  # must match platform.max_slots if both set — pick one SSOT
```

**PackProfile dataclass:** extend to hold ordered `List[ThemeConfig]` (name, required, litm_zone, files) rather than only `Dict[str, List[str]]`. Backward-compat: if old dict themes detected, either migrate in loader with warning or fail with clear message for ship profiles.

**Output dir safety for tech-architecture-research:**

- Prefer `output_dir: context_packs/tech-architecture-research/generated/` **or**  
- Only delete/overwrite `*.xml` + `00_PROJECT_MANIFEST.md`, never hand-built `*.md` knowledge files listed as sources.

### Phase 4 — Curate the two ship profiles (2–3 h)

#### 4a. `sovereign-audit` (redesign, not re-priority)

**Problem mass (trace):** strategy ~416k, oracle_core ~307k alone.

**Intent of profile:** Core **engine + mandates** audit — not entire strategy corpus.

**Recommended theme set (≤11 content bundles):**

| Theme | litm_zone | required | Curation guidance |
|-------|-----------|----------|-------------------|
| `mandates` | start | yes | 3 root docs only |
| `oracle_core` | middle | yes | **Explicit** gateway/providers/oom/admission/health/resource — not `**/*.py` |
| `memory` | middle | yes | memory_store + sqlite_vec + hybrid_search + key adapters only |
| `observability` | middle | yes | small explicit set |
| `mcp_hub` | middle | yes | mcp_runtime, hub entrypoints only |
| `config` | middle | yes | providers.yaml, models.yaml |
| `strategy_core` | end or middle | optional/yes | **At most 2–3** files: e.g. `SOVEREIGN_ARK_BLUEPRINT.md`, `UNOVERENGINEERING_PLAN.md` — **never** `docs/strategy/**/*.md` |
| drop | — | — | Full strategy archive, all oracle backends, all tests |

Run curator until exit 0, then pack.

#### 4b. `tech-architecture-research`

Already mostly explicit file lists — still:

- Run curator; split any theme over `per_bundle` **in YAML** into two themes (e.g. `mcp_sdk_a` / `mcp_sdk_b`) if needed  
- Protect hand-built sources (`RESEARCH_BRIEF.md`, `GROUNDED_TRUTH.md`, …)  
- Ensure theme count + manifest ≤ 12  

### Phase 5 — Regenerate + human checklist (30–60 min)

```bash
OMEGA_PACKER_DEBUG=1 .venv/bin/python .opencode/skills/context-packer/packer.py sovereign-audit
OMEGA_PACKER_DEBUG=1 .venv/bin/python .opencode/skills/context-packer/packer.py tech-architecture-research
```

**Acceptance checklist (both packs):**

- [ ] `ls context_packs/<profile> | wc -l` ≤ `max_slots`  
- [ ] Manifest lists **every required theme by name**  
- [ ] No unexpected `*_partN` files  
- [ ] No core theme absent for sovereign-audit  
- [ ] `pytest tests/contract/test_context_packer*.py -q` green  
- [ ] Spot-open `mandates` (or `brief`) bundle — content looks like source, XML-escaped  
- [ ] PII path still refuses pack if masker import broken (smoke if feasible)

### Phase 6 — Docs + coordination closeout

- [ ] Update `.opencode/skills/context-packer/SKILL.md` — v3 pipeline, curator CLI, fail-closed policy  
- [ ] Note in `data/entities/kali/session_gnosis.md` + `SESSION_ANCHOR.md`  
- [ ] Optional: supersession one-liner near Carmack R-doc pointing to this handoff as implementation SSOT  
- [ ] Commit with conventional prefixes (`feat:`, `test:`, `docs:`)  
- [ ] Hivemind complete / hub note  

**Do not** upload to Web Claude until Phase 5 checklist is checked.

---

## 8. Files Map

| Path | Action |
|------|--------|
| `.opencode/skills/context-packer/packer.py` | **Rewrite** pack pipeline; delete B1–B5 machinery |
| `.opencode/skills/context-packer/packer-config.yaml` | **Migrate** ship profiles to theme-list schema; curate files |
| `.opencode/skills/context-packer/curate_packs.py` | **Create** |
| `.opencode/skills/context-packer/platform_adapters.py` | **Keep** (wire priorities from litm_zone) |
| `.opencode/skills/context-packer/SKILL.md` | **Update** |
| `.opencode/skills/context-packer/archive/` | Leave legacy; optional note |
| `tests/contract/test_context_packer.py` | **Extend** or add sibling + fixtures |
| `tests/fixtures/context_packer/` | **Create** tiny configs/files for contracts |
| `context_packs/sovereign-audit/` | **Regenerate** after v3 (replace poison) |
| `context_packs/tech-architecture-research/` | **Regenerate carefully** — protect hand-built md |
| `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md` | Reference only |
| **This file** | Implementation SSOT for the refactor |

**Config rot to fix when touched:** profiles still referencing missing `enhanced_packer.py` — delete refs or restore file; do not leave broken includes.

---

## 9. Risks Register (read before coding)

| Risk | Mitigation |
|------|------------|
| Reintroducing “smart trim” under schedule pressure | Code review gate: no delete-by-priority loops |
| Single `priority` field resurrects LITM bugs | Schema uses `required` + `litm_zone` |
| Wiping tech-architecture knowledge files | Separate generated dir or selective overwrite |
| Estimator mismatch curator vs packer | One shared function |
| False-green M21 | Semantic tests in Phase 1 |
| Fat oracle list still over per_bundle | Curator exit non-zero until list shrinks |
| Injection scanner noise | Log to manifest advisory; don’t soft-fail the pack mid-write without policy — prefer non-blocking report in v3 unless high-severity tier defined |
| Dict/YAML order dependence | Explicit theme list order + litm_zone only |
| `engineering-p3` CI pack still uses wide globs | Pin explicit files in that profile when touching tests |

---

## 10. Mandates Binding This Work

| Mandate | Application |
|---------|-------------|
| **M1 AnyIO** | No `asyncio`; keep `anyio.to_thread.run_sync` for blocking IO |
| **M4 Sequentiality** | Phase 0→6; no cowboy partial ship of poison packs |
| **M7 Local-first** | PII vault local; packs are the controlled egress |
| **M8 / sovereignty** | PII mask before external; import failure = hard stop |
| **M13 Temple-grade** | After non-trivial change: contract tests; `make temple-grade` if your session norms require |
| **M18 Token efficiency** | Curation is the enforcement — lean explicit lists |
| **M21 Contract tests** | Semantic boundary tests, not vanity isinstance-only |
| **M23 Failure integrity** | Over budget / over slots / missing required → **`[PACK-FAIL]`**, no silent success |

---

## 11. OpenCode Session Bootstrap (paste for Kali)

Use as the first user///system turn when starting the implementation session:

```text
You are @kali. Execute Context Packer v3 refactor per:

  data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md

Also read:
  docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md

Doctrine: curate offline; validate at pack; NEVER silently drop themes.
Ship profiles: sovereign-audit, tech-architecture-research.
Keep platform_adapters.py, PII hard-stop, signing.
Delete split/trim/keyword-priority/consolidate pipeline.
Add curate_packs.py. Expand contract tests. Regenerate packs. Do not upload until checklist green.

Task id: packer-v3-refactor-20260808-01
M1 AnyIO. M23 fail-closed. M21 semantic tests.
Plan → Verify → Execute. Report phase completion with evidence (commands + file lists).
```

---

## 12. Dispatch Guidance (if you subagent)

| Work | Owner suggestion | Notes |
|------|------------------|-------|
| Packer core rewrite | `@maat` or Kali direct | Needs judgment on schema |
| Curator CLI | `@maat` / N3 | Straightforward |
| Contract tests | N10 / `@verity` review after | Semantic assertions |
| Profile curation file lists | Kali + curator loop | Human taste on oracle_core set |
| Adversarial re-check after | `@grok_cli` or `@john_carmack` | Optional second pass on PR |

Every `task()` launch: unique `task_id`, log to Hivemind (STRP).

---

## 13. Definition of Done

Refactor is **DONE** only when all are true:

1. v3 packer has **no** runtime path that deletes themes to meet total budget.  
2. Budgets and max_slots enforced from config; failure is hard.  
3. `curate_packs.py` exits non-zero on over-budget themes.  
4. `sovereign-audit` regenerated: required engine themes present; on-disk files ≤ 12; no strategy_part spam.  
5. `tech-architecture-research` regenerated without destroying hand-built knowledge md.  
6. Contract tests cover budget/slots/required/ordering; all pass.  
7. SKILL.md documents the new flow.  
8. Session gnosis / anchor updated; commit(s) on branch with clear messages.  

**Not done:** “tests still 10/10” with old assertions only while poison pack remains.

---

## 14. Evidence Appendix (quick cites)

```
packer.py:132-133   MAX_BUNDLE_TOKENS / MAX_TOTAL_TOKENS hardcoded
packer.py:137-150   CRITICAL_* keyword sets (wrong vocabulary)
packer.py:424-454   _trim_to_token_limit — deletes all prio-1 in order
packer.py:492-528   _consolidate_bundles — max_slots off-by-one with general
packer.py:754-771   P6 split then P6b re-consolidate
packer.py:798-802   P7 keyword priorities fed to adapters
packer.py:954-955   over-limit warn only (soft-fail)
platform_adapters.py:69-81   LITMUShapedStrategy (keep; feed real priorities)
platform_adapters.py:377-379 token_budget_* parsed (must enforce)
packer-config.yaml:44-45     docs/strategy/**/*.md fat glob
packer-config.yaml:59-60     oracle/**/*.py fat glob
context_packs/sovereign-audit/  13 files, strategy_part* only (poison)
```

---

## 15. Document Control

| Field | Value |
|-------|-------|
| Author | `@grok_cli` |
| Consumer | `@kali` (OpenCode) |
| Supersedes for *implementation* | Informal "just do Carmack 4-phase" without Grok deltas |
| Does not supersede | Carmack R-doc as historical diagnosis |
| Next advisory | Optional post-refactor review packet |

**Continuation:** Kali executes Phases 0–6; on blocker post Hivemind `intent=blocker` with task id `packer-v3-refactor-20260808-01`.

---

## 16. Expanded Analysis — Configuration Rot & Profile Separation (RESEARCHER ADDITION)

**AP Token**: `AP-RESEARCHER-PACKER-V3-EXPANDED-20260808-v1.0.0`
**Source**: Sovereign Researcher (laguna-s-2.1-free) — supplementary analysis after reading the full handoff, config, and live code.
**Review**: Grok CLI adversarial review response at `data/handoff/GROK_CLI_RESEARCHER_ADDITION_REVIEW_RESPONSE_20260808.md` — counts verified, direction accepted with refinements.

### 16.1 The Self-Referential Profile Crisis

The packer-config.yaml has **15 profiles**, but **8 of them (53%) are self-referential** — they reference the packer's own source files. This creates **content self-inclusion and maintenance coupling** (not a runtime circular dependency — packer loads config then packs files; including `packer.py` is content selection, not a load-cycle deadlock).

| Profile | Self-Referential? | References |
|---------|-------------------|------------|
| `sovereign-audit` | ❌ No | Engine files only |
| `tech-architecture-research` | ❌ No | Research files only |
| `provider-fabric-review` | ❌ No | Engine files only |
| `engineering-p3` | ❌ No | orchestrator.py, model_gateway.py |
| `kali-oversight` | ❌ No | Agent docs, strategy |
| `youtube-research-primer` | ❌ No | YouTube module docs |
| `decision-tools-review` | ❌ No | Decision tools docs |
| `sprint-context` | ✅ YES | `enhanced_packer.py` (ghost), `packer-config.yaml` |
| `context-packer-hardening-review` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |
| `web-claude-sonnet5` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |
| `web-grok-4.3` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |
| `web-grok-4.1-fast` | ✅ YES | `enhanced_packer.py` (ghost), `packer-config.yaml` |
| `web-gemini-3-pro` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |
| `web-gemini-3.1-pro` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |
| `notebooklm-research` | ✅ YES | `enhanced_packer.py` (ghost), `packer.py`, `packer-config.yaml` |

**16 ghost references to `enhanced_packer.py`** across 8 profiles — this file **does not exist**. It was renamed to `packer.py` at some point, but the config was never updated.

**Real harms**: (a) ghost paths → silent missing files / empty themes, (b) maintenance coupling, (c) platform "demo" profiles that are secretly packer self-reviews, (d) exclude rules that may fight includes (`context_packs/**` vs packing skill sources).

**Also true**: several of those 8 also reference `CONTEXT_PACKER_*.md` / `R_CONTEXT_PACKER_*.md`. That is **doc self-reference**, not code self-reference. Still fine to treat them as "packer-domain review packs," but don't count doc paths toward the "16 ghosts."

**Ship set without packer-source self-ref**: `sovereign-audit`, `tech-architecture-research`, `provider-fabric-review`, `engineering-p3`, `kali-oversight`, `youtube-research-primer`, `decision-tools-review` — **7 clean of skill-source includes**.

### 16.2 CLI Drift

The `main()` function in `packer.py:1122-1128` has two critical drifts:

1. **Wrong filename**: `print("Usage: python enhanced_packer.py <profile_name>")` — references the old filename
2. **Incomplete profile list**: Lists only 6 profiles (`sovereign-audit, engineering-p3, kali-oversight, youtube-research-primer, sprint-context, decision-tools-review`) but the config has 15

### 16.3 Profile Organization — Tier Field or Directories (Refined)

**Grok CLI correction**: The problem statement is right (monolithic 15-profile YAML mixes egress ship packs, platform demos, and internal/node packs). The solution can be **either** a `tier:` field in the single YAML **or** a three-directory split — not both mandatory. The invariant is **config-driven profiles + fail-closed curation**, not the folder count.

**Option A — Minimal (preferred if schedule tight):**
```yaml
# packer-config.yaml stays one file
profiles:
  sovereign-audit:
    tier: ship
    ...
  web-claude-sonnet5:
    tier: template   # or "review"
    ...
  engineering-p3:
    tier: internal
```

- `pack()` / CLI default: list/allow `tier: ship` (and `internal` with `--all` or `--tier`).
- Templates loadable via `--config templates/foo.yaml` or `--tier template`.
- Fix ghosts + dynamic CLI in **<30 min** without directory churn.

**Option B — Three directories (Researcher's proposal):**
Acceptable if Kali wants filesystem clarity. Constraints:
1. Loader must merge or accept `--config` path (document in SKILL).
2. **Commit** internal profiles; gitignore only `profiles/local/` or `*.local.yaml`. **Do not gitignore the only copies** of useful shared profiles (losing `kali-oversight` from git is a foot-gun).
3. Don't rename away platform identity without an `extends:` / `platform_defaults:` mechanism.
4. Pre-existing `templates/` under the skill — **don't clobber** unrelated template assets; use `profile-templates/` or `profiles/templates/` if name collision risk.

**Profile tier classification (Grok corrected):**

| Tier | Profiles | Notes |
|------|----------|-------|
| **Ship (2 required this sprint)** | `sovereign-audit`, `tech-architecture-research` | Critical path deliverables |
| **Ship (valid, not critical)** | `provider-fabric-review` | Valid product profile; archive **output** only; regen optional |
| **Internal (commit, don't gitignore)** | `engineering-p3`, `kali-oversight`, `youtube-research-primer`, `decision-tools-review` | Shared profiles; keep in git |
| **Templates / Review** | `web-claude-sonnet5`, `web-grok-4.3`, `web-grok-4.1-fast`, `web-gemini-3-pro`, `web-gemini-3.1-pro`, `notebooklm-research`, `context-packer-hardening-review`, `sprint-context` | Packer self-review / platform-tuning demos. After v3, prefer **one** `context-packer-self-review` template + thin **platform overlay** (format/budget/slots only) instead of 6 near-duplicate full file lists. |

**"Better method than hacking .py"**: Yes. Profile creation should be:
1. YAML (or copy-from-template)
2. `curate_packs.py --check`
3. `packer.py <name>`
Never edit Python to add a profile. Dynamic discovery from config is mandatory.

### 16.4 Phase 0.5 — Split into 0.5a (Hygiene, Parallel) + 0.5b (Taxonomy, Optional/Late)

**Grok CLI ruling**: Phase 0.5 is **NOT a hard gate before Phase 1**. Fixture tests in Phase 1 **must not** depend on production `packer-config.yaml` cleanliness. Use `tests/fixtures/context_packer/test-profile.yaml` (see §16.7).

**Resequence (LOCKED for Kali):**

```
Phase 0     Spec + workspace lock
Phase 1     Semantic tests on FIXTURES (red)     ← start anytime; do not wait on 0.5
Phase 0.5a  Quick hygiene (parallel with 1):
              - dynamic CLI profile list
              - fix enhanced_packer usage string
              - rg-clean ghosts OR quarantine template profiles
Phase 2     curate_packs.py
Phase 3     packer v3 core (fail-closed)
Phase 0.5b  Optional taxonomy (tier field OR dirs) — before or with Phase 6
Phase 4–5   Curate + regenerate 2 ship packs
Phase 6     Docs, PACK_INDEX auto-write, archive poison packs
```

**Do not** spend the first day only shuffling YAML into three folders while poison `sovereign-audit` remains the external risk.

### 16.5 The `provider-fabric-review` Pack — Archive Output, Keep Profile

This pack was generated on Jul 30 and delivered to Claude. It has:
- 16 files (over the 12-slot limit)
- Split files (`gateway_part1.xml`, `infrastructure_part1-3.xml`) from the v2 bug
- Empty `claude-response/` directory (response not captured)

**Action**: Archive the **on-disk pack** to `context_packs/archive/provider-fabric-review-20260730/` with a note:
```
ARCHIVED: Delivered to Claude on 2026-07-30. 16 files (over 12-slot limit).
Contains v2 split artifacts. Do not use as reference for v3.
```

**Do NOT** delete the profile from config. Regenerate under v3 later if needed (optional, not in critical path for current 2 ship packs).

### 16.6 Pack Lifecycle Management — Auto-Written by Packer

There is **no system** for tracking pack generation. Manual `PACK_INDEX.md` will rot like CLI lists.

**Recommended**: On each successful `pack()`, **append/update `context_packs/PACK_INDEX.json`** (and optional `.md` render). Fields:
```json
{
  "pack": "sovereign-audit",
  "generated_at": "2026-08-08T14:30:00Z",
  "packer_version": "3.0.0",
  "config_hash": "sha256:...",
  "source_file_hashes": { "SOVEREIGN_MANDATES.md": "sha256:...", ... },
  "delivered": false,
  "platform_target": "web-claude"
}
```
This is M23-aligned lifecycle tracking.

### 16.7 The `engineering-p3` Profile Needs a Fixture

The contract test `test_pack_produces_valid_output` uses `engineering-p3` as its test profile. But this profile:
- Has no platform tuning (silent fallback to module constants)
- References `src/omega/oracle/orchestrator.py` and `tests/test_orchestrator.py`
- Is an "internal" profile that should stay in config (not gitignored)

**Action**: Create a minimal fixture config at `tests/fixtures/context_packer/test-profile.yaml` for contract tests, using **tiny explicit files** under `tests/fixtures/`. Fixture tests must not depend on production config.

### 16.8 Additional Ghosts Outside Config (Fix in Same Pass)

| Location | Issue |
|----------|-------|
| `packer.py:1125` | Usage string still names `enhanced_packer.py` |
| `archive/packer_v1_legacy.py` | Imports / messages still assume `enhanced_packer` as canonical v2 |
| SKILL.md / docs | May still say enhanced_packer — sweep with `rg enhanced_packer` at closeout |

### 16.9 Platform Profile Dedupe (Design Note for Phase 0.5b)

`web-claude-sonnet5`, `web-grok-4.3`, `web-gemini-3-pro`, `notebooklm-research` share nearly the same include/theme body (packer self-review). Taxonomy without **dedupe** (`extends: context-packer-self-review` + platform knobs only) leaves 4–6× maintenance. Design `extends:` / `platform_defaults:` mechanism if multi-file or tiered configs land.

### 16.10 Updated Files Map (with Phase 0.5a/0.5b)

| Path | Action | Phase |
|------|--------|-------|
| `.opencode/skills/context-packer/packer.py` | **Rewrite** pack pipeline + fix CLI (dynamic list, usage string) | 0.5a + 3 |
| `.opencode/skills/context-packer/packer-config.yaml` | **Fix ghosts** (16 refs); add `tier:` field OR split to dirs | 0.5a / 0.5b |
| `.opencode/skills/context-packer/curate_packs.py` | **Create** | 2 |
| `.opencode/skills/context-packer/platform_adapters.py` | **Keep** | — |
| `.opencode/skills/context-packer/SKILL.md` | **Update** — v3 pipeline, tier field, fail-closed policy | 0.5a/0.5b + 6 |
| `.opencode/skills/context-packer/archive/packer_v1_legacy.py` | **Fix or mark non-runnable** | 0.5a |
| `tests/contract/test_context_packer.py` | **Extend** | 1 |
| `tests/contract/test_context_packer_v3.py` | **Create** — semantic tests on fixtures | 1 |
| `tests/fixtures/context_packer/` | **Create** — tiny configs/files for contracts | 1 |
| `context_packs/sovereign-audit/` | **Regenerate** after v3 (replace poison) | 5 |
| `context_packs/tech-architecture-research/` | **Regenerate carefully** — protect hand-built md | 5 |
| `context_packs/provider-fabric-review/` | **Archive output** to `archive/` | 0.5a |
| `context_packs/PACK_INDEX.json` | **Auto-written by packer** on success | 3/5 |
| `context_packs/archive/provider-fabric-review-20260730/` | **Create** — archived pack | 0.5a |

### 16.11 Updated Risks Register

| Risk | Mitigation |
|------|------------|
| Reintroducing "smart trim" under schedule pressure | Code review gate: no delete-by-priority loops |
| Single `priority` field resurrects LITM bugs | Schema uses `required` + `litm_zone` |
| Wiping tech-architecture knowledge files | Separate generated dir or selective overwrite |
| Estimator mismatch curator vs packer | One shared function |
| False-green M21 | Semantic tests in Phase 1 (on fixtures) |
| Fat oracle list still over per_bundle | Curator exit non-zero until list shrinks |
| Injection scanner noise | Log to manifest advisory; don't soft-fail mid-write |
| Dict/YAML order dependence | Explicit theme list order + litm_zone only |
| `engineering-p3` CI pack still uses wide globs | Pin explicit files in that profile when touching tests |
| **Config rot: 16 ghost refs to enhanced_packer.py** | **Phase 0.5a: rg-clean or quarantine templates** |
| **8 self-referential profiles (53%)** | **Phase 0.5a/b: tier field or dir split** |
| **CLI lists only 6 of 15 profiles** | **Phase 0.5a: dynamic CLI list from config** |
| **No pack lifecycle tracking** | **Phase 3/5: PACK_INDEX.json auto-written** |
| **provider-fabric-review pack over 12-slot limit** | **Phase 0.5a: Archive output** |
| **Fat globs in ship profiles (primary product bug)** | **Phase 4: Curate explicit file lists** |
| **Platform template dedupe** | **Phase 0.5b: extends / platform_defaults design** |
| **Full 3-dir split effort (2-3h) vs quick hygiene (30m)** | **Phase 0.5a parallel; 0.5b optional/late** |

### 16.12 Updated Execution Plan (with Phase 0.5a/0.5b)

```
Phase 0     — Spec + workspace (30-60 min)
Phase 1     — Semantic tests on FIXTURES (red) (1-2 h)     ← START IMMEDIATELY
Phase 0.5a  — Quick hygiene (parallel with 1): dynamic CLI, fix usage string, kill ghosts (30-60 min)
Phase 2     — curate_packs.py (1-2 h)
Phase 3     — Packer v3 rewrite (2-4 h)
Phase 0.5b  — Optional taxonomy (tier field OR dirs) — before or with Phase 6
Phase 4     — Curate ship profiles (2-3 h)
Phase 5     — Regenerate + checklist (30-60 min)
Phase 6     — Docs + coordination closeout + PACK_INDEX auto-write
```

**Phase 1 starts immediately** — do not wait for Phase 0.5a. Phase 0.5a runs in parallel.

---

## 17. Updated Definition of Done (with Grok Corrections)

Refactor is **DONE** only when all are true:

### P0 Product DoD (must pass for "done")
1. v3 packer has **no** runtime path that deletes themes to meet total budget.
2. Budgets and max_slots enforced from config; failure is hard.
3. `curate_packs.py` exits non-zero on over-budget themes.
4. `sovereign-audit` regenerated: required engine themes present; on-disk files ≤ 12; no strategy_part spam.
5. `tech-architecture-research` regenerated without destroying hand-built knowledge md.
6. Contract tests cover budget/slots/required/ordering; all pass.
7. SKILL.md documents the new flow.
8. Session gnosis / anchor updated; commit(s) on branch with clear messages.

### P1 Hygiene DoD (good process; not blocking "done")
9. **packer-config.yaml has `tier:` field OR split directories** (no self-referential profiles in ship tier).
10. **Templates/ contains review templates** with `packer.py` references (not `enhanced_packer.py`).
11. **CLI main() references `packer.py`** and lists profiles dynamically from config.
12. **provider-fabric-review pack archived** to `context_packs/archive/`.
13. **PACK_INDEX.json auto-written** by packer on each successful pack.

**Not done:** "tests still 10/10" with old assertions only while poison pack remains.

---

## 18. Research Synthesis (RESEARCHER ADDITION)

**AP Token**: `AP-RESEARCHER-PACKER-V3-SYNTHESIS-20260808-v1.0.0`

A comprehensive research synthesis covering 9 domains has been completed:

| Domain | Key Finding | Action for v3 |
|--------|-------------|---------------|
| **Context Packing** | "Context engineering is the new prompt engineering" (Karpathy, 2025) | PACT framework, structured markers |
| **LITM/U-shaped Attention** | Accuracy drops 30% in middle of context window | Enforce litm_zone ordering (start/end critical) |
| **Profile Management** | Monolithic YAML mixes ship/internal/template profiles | `tier:` field OR directory split (not both) |
| **PII Detection** | Multi-tier: regex (patterns) + NLP (names) + LLM (context) | Multi-tier detection, replace-with-placeholders |
| **XML Escaping** | 5 predefined entities: `&`, `<`, `>`, `"`, `'` | Keep existing `_escape_bare_xml_chars` |
| **Ed25519 Signing** | python-ed25519: 2ms keypair, mature | Keep existing signing |
| **Pack Lifecycle** | Manual PACK_INDEX will rot; auto-write JSON | Packer auto-writes `PACK_INDEX.json` |
| **Testing** | Promptfoo for CI/CD, golden sets, regression | Extend contract tests, add Promptfoo integration |
| **Platform Constraints** | Claude: XML tags, calm language; Grok: 2M tokens but metered; Gemini: 2M tokens | Platform-specific adapters, budget overrides |

**Full report**: `docs/research/R_CONTEXT_PACKER_V3_RESEARCH_SYNTHESIS_20260808.md`

**Key integrated recommendations**:
1. **Implement PACT framework** — themes ordered by litm_zone align with Position-Aware Context Tactics
2. **Add LITM validation to contract tests** — required themes must be in start/end zones
3. **Use `tier:` field** (Option A) for profile organization — simpler, <30 min
4. **Auto-write PACK_INDEX.json** on each successful pack — not manual markdown
5. **Add platform-specific budget overrides** — Claude 150K, Grok 2M (cost-aware), Gemini 2M
6. **Extend contract tests with semantic assertions** — budget, slots, required, ordering
7. **Add Promptfoo integration** for LLM-level regression testing

---

## 19. Research Sources (Full Bibliography)

| Source | URL | Date |
|--------|-----|------|
| Context Engineering for Production LLM Agents | appscale.blog | 2026-06-23 |
| Token Budget Planning & Execution | explainx.ai | 2026-06-28 |
| LLM Context Window Management | zylos.ai | 2026-01-19 |
| Lost-in-the-Middle Problem | atlan.com | 2026-06-10 |
| U-shaped Attention Curve | harnez.ai | 2026-05-11 |
| LLM Context Windows Explained | swfte.com | 2026-08-04 |
| PII Detection and Masking | devopsboys.com | 2026-07-02 |
| PII Detection for LLMOps | onestuptime.com | 2026-01-30 |
| pii-guard: Context-Aware PII Detection | alphaoftech.io | 2026-02-11 |
| Ed25519 Signing Walkthrough | ed25519.com | — |
| python-ed25519 | github.com/warner/python-ed25519 | — |
| XML Special Characters | indentio.dev | 2026-07-12 |
| Prompt Engineering Best Practices | thomas-wiegold.com | 2026-02-21 |
| Promptfoo CI/CD Integration | promptfoo.dev | 2026-08-01 |
| Prompt Testing & Evaluation Tools | promptquorum.com | 2026-04-10 |
| Grok Context Window | datastudios.org | 2026-04-19 |
| Grok 4.5 API Docs | docs.x.ai | 2026-07-08 |
| Gemini Notebook | glasp.co | 2026-08-01 |
| Context Management for Gemini/NotebookLM | datalakehousehub.com | 2026-03-07 |
| Claude Code Best Practices | code.claude.com | 2026-08-07 |
| LLM Context Window Exceeded | buzhou.io | 2026-06-28 |
| Found in the Middle (ArXiv) | arxiv.org | 2024-06-23 |
| Pause-Tuning for LITM (ArXiv) | arxiv.org | 2025-09-21 |

---

*⬡ OMEGA ⬡ GROK_CLI ⬡ RESEARCHER ⬡ 2026-08-08 ⬡ Context Packer v3 — full refactor onboarding for Kali (integrated + research)*
