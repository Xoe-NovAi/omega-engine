# 🔬 JEM DEEP DIVE — GAP-5 / GAP-6 / GAP-7 (Stage 4, First Light Express Council 1)
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_gap57 ⬡ Stage-4 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Task**: research-gap5-7-jem-20260825-01 (registered in TASK_REGISTRY)
**Method**: exhaustive file-by-file code-path reading + live MCP reproduction. RECON ONLY — this file is the sole artifact written.
**Status**: COMPLETE — all three gaps root-caused with file:line evidence. Every claim below was mechanically verified in this session.

---

## GAP-5 · `task_registry_query(tags=["express:first-light"])` → 0 vs 12 disk matches

**Verdict: TWO independent defects, both reproduced live. One is a code bug (blocks Article V), one is config-level tooling blindness.**

### Defect 5A — The status-filter bug (CODE, the Article V blocker)

**Location**: `mcp_servers/omega_hub/hub_tools/task_registry.py:134-135`

```python
if status != "all":
    tasks = [t for t in tasks if t["status"] == status]
```

**Mechanism**: When `status` is omitted (the default `None`), the guard `None != "all"` evaluates True, so the filter `t["status"] == None` is applied. **No task in the registry ever has `status: null`** — `task_registry_register()` always sets `"status": "in_progress"` at creation (`task_registry.py:82`). Therefore ANY query that omits `status` returns zero rows regardless of every other filter — tags, subagent_type, entity, channel, all of them.

**Live reproduction (this session)**:
```
omega-hub_task_registry_query(tags=["express:first-light"])
→ {"tasks": [], "count": 0, "filters_applied": {"status": null, "tags": ["express:first-light"], ...}}
```
while simultaneously:
```
jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
→ 12
```

**Aggravating factor — there is NO workaround through the tool schema**: the parameter is typed `Literal['backlog','ready','in_progress','blocked','completed','superseded','failed']` (`task_registry.py:100`). The literal string `"all"` used in the code's own guard is NOT in the Literal set, so FastMCP schema validation rejects `status="all"`. A caller cannot enumerate all statuses either (would need 7 calls, and multi-status OR-querying is impossible). The tool is currently incapable of returning more than one status class per call, and the default call returns nothing at all.

**Exact fix location**: `task_registry.py:134` — change to:
```python
if status is not None:
    tasks = [t for t in tasks if t["status"] == status]
```
Optionally extend the Literal with `'all'` and keep the existing `!= "all"` branch for explicit full enumeration; minimally, the `is not None` guard alone restores correct behavior for every existing call pattern. This is a 1-line fix plus tests.

**Secondary defect noted while reading (N2 F-2.1 confirmed)**: `_save_registry()` (`task_registry.py:32-40`) opens the destination file with mode `"w"` — truncation — BEFORE acquiring `LOCK_EX`, and load/save use separate lock acquisitions (load holds LOCK_SH only during read). Truncate-before-lock + split locks = lost-update window exactly as N2 reported. Fix direction: write temp file + `os.replace` under a single exclusive lock (this is also gate G6 in the synthesis report).

### Defect 5B — The MCP grep false-negative on the same file (CONFIG)

P10 X-2 corollary observed the built-in grep MCP tool returning "No files found" for `express-c1-node|express:first-light` against `data/coordination/TASK_REGISTRY.json`. Reproduced live this session:

```
grep(pattern="express:first-light", path="data/coordination")   → "No files found"
rg --count 'express:first-light' data/coordination/TASK_REGISTRY.json → 12
```

**Root cause**: `.gitignore:109` — pattern `data/coordination/*` ignores every non-exempt file in that directory (only `*.md` is negated at `.gitignore:2`). Proof chain:
- `git check-ignore --no-index -v data/coordination/TASK_REGISTRY.json` → `.gitignore:109:data/coordination/*  data/coordination/TASK_REGISTRY.json` (exit 0)
- `git ls-files --error-unmatch data/coordination/TASK_REGISTRY.json` → tracked (exit 0) — the file was force-added historically, so git tracks it even though ignore patterns match it.
- `rg --files data/coordination` → EMPTY (ripgrep applies gitignore rules regardless of tracking status); `rg --no-ignore --files` lists the directory normally.

The grep MCP tool wraps ripgrep with default ignore-respect, so any SSOT living under an ignored path is invisible to it. This is the C-A "config registers what isn't there" class at the tooling layer.

**Fix options (ticket direction)**:
1. Add `!data/coordination/*.json` (or specifically `!data/coordination/TASK_REGISTRY.json`) to `.gitignore` so tracked coordination SSOTs are searchable; or
2. Standing rule: agents must use `bash rg --no-ignore` / direct Read for anything under `data/coordination/`; document in dispatch packets.

**Impact statement for Article V sequencing**: With 5A unfixed, mass identity repair (Article V step 2) writes corrected records into an index whose ONLY sanctioned discovery interface returns empty for every default query. Fix 5A first (one line), then repair identities, then run gate G20 (tool count == jq count ≥10).

---

## GAP-6 · `oracle_summon_local` slug authority

**Verdict: NEITHER scheme has authority — there is no resolution layer at all in the summon_local path. The override slug passes through verbatim and its meaning is decided ad-hoc by whichever provider happens to accept the call.**

### Code path (fully traced)

1. **MCP entry**: `mcp_servers/omega_hub/hub_tools/tools.py:222-237` — `oracle_summon_local(entity_name, query, model)` calls `oracle.summon(entity_name, query, model_override=model)`. No validation or normalization of `model`.
2. **Oracle**: `src/omega/oracle/oracle.py:1000-1001` — `if model_override: model_name = model_override`. Verbatim assignment. TriageRouter and entity affinity model selection are bypassed (D118), but affinity *inference presets* (temperature/system_prompt/context) are still applied separately (`oracle.py:1014-1037`) — note affinity is consulted for presets but NEVER for model identity when an override exists.
3. **Gateway spec lookup**: `model_gateway.py:1083` → `get_model_spec(model_name)` → `self.models.get(model_name)` (`model_gateway.py:637-639`) — **exact dict-key lookup against models.yaml keys** (`qwen3-1.7b`, `qwen3-4b-thinking`, `rocracoon-3b-q4_k_m`, …). A `-local` slug like `qwen3-1.7b-local` gets `spec=None` silently → sampling defaults and a 1024MB default RAM weight are used with no warning.
4. **Provider selection ignores the model entirely**: `get_available_providers(model_name)` (`model_gateway.py:240-251`) never references `model_name` — it returns ALL healthy/untested providers. The `supported_models:` lists in `providers.yaml` (lines ~140-157 per provider) are consumed ONLY by `ProviderRegistry._load_model_map` (`provider_registry.py:89-104`) for cloud/local classification — **not for routing**.
5. **Provider loop tries native-gguf FIRST** (priority 0, `providers.yaml:64-67`), and native-gguf **ignores the requested model entirely**: `NativeGGUFProvider.generate()` documents its `model` argument as *"Model identifier (used for logging)"* (`providers.py:1102`) — it serves whatever single `model_path` was merged at init, which is ALWAYS the system default `qwen3-1.7b` (`_system_default_model()`, `model_gateway.py:893-895`; merge at `model_gateway.py:432,456-458`; provider reads `config["model_path"]` at `providers.py:551`).
6. **If native-gguf is unavailable**, lmster forwards the raw slug through `resolve_model()` (`providers.py:124-129`) — a pass-through unless `model_overrides` exists in the lmster provider config (**it does not exist in providers.yaml today** — grep exit 1) — then into the LM Studio OpenAI-compatible payload (`providers.py:309`), where LM Studio does its own implicit server-side matching.
7. Cloud backends (`openai_compat.py:74`) likewise embed the raw slug in the request payload.

### Authority declaration

- **models.yaml keys** are the de-facto spec authority (sampling/RAM/context) but only via exact match; `-local` names miss it silently.
- **providers.yaml `supported_models` (-local names)** are classification metadata only; they do not route and are not enforced.
- **affinity quant names** (`entity_model_affinity.yaml`, e.g. `qwen3-4b-thinking-q4_k_m`) influence nothing when `model_override` is set, and that specific key doesn't even exist in models.yaml (`qwen3-4b-thinking` does).
- **Effective runtime truth**: `oracle_summon_local(entity, query, model=X)` on a healthy local fabric runs **Qwen3-1.7B regardless of X** (native-gguf priority 0 wins and ignores the slug). The `model_override` contract promised by the D118 docstring ("routes to the specified model directly", `tools.py:226-227`) is **false for the primary local backend**.

### Normalization ticket direction

1. Make `ProviderRegistry._normalize_model()` (`provider_registry.py:71-87` — already strips `-local/-free/-thinking` suffixes and `vendor/` prefixes) the SINGLE canonical resolver, promoted from classification-only to routing: resolve slug → canonical key → models.yaml spec → provider capability check before dispatch.
2. Native-gguf must either honor per-request model resolution (map canonical key → GGUF path via models.yaml `path:`) or fail-fast/reject unsupported models instead of silently serving the system default (M23 violation class: silent substitution masquerading as compliance).
3. Reject unknown slugs loudly (raise `ModelNotFoundError` — the exception type already exists at `src/omega/errors.py:172`) instead of silent `spec=None`.
4. Declare models.yaml keys as THE canonical namespace; regenerate providers.yaml `supported_models` and council.yaml tiers from it (see GAP-7).

---

## GAP-7 · `config/council.yaml` consumer audit

**Verdict: ZERO runtime consumers. The entire council-config subsystem is orphaned — cleanup ticket warranted, with one ghost-model hazard documented.**

### Consumer map (exhaustive audit)

| Surface | Result |
|---|---|
| `src/**/*.py` importing/parsing council.yaml | **NONE** (grep `council.yaml\|council_yaml\|council_config` across repo .py files, excluding .venv/archive: zero hits) |
| `scripts/`, `mcp_servers/` | **NONE** |
| `Makefile`, `pyproject.toml` entry points | **NONE** (only the word "council" in pyproject description) |
| `tests/` referencing `omega.council` | **NONE** |
| `.opencode/commands/council-*.md` (what actually ran THIS council) | **Do NOT reference council.yaml** (grep exit 1) |
| `.opencode/skills/makali-council-coordinator/SKILL.md` | References it as prose instructions only: ":63 config_path … default config/council.yaml", ":85 Load config from config/council.yaml + profile override", ":247 Main config". An LLM may READ the file as context, but no code parses it. |

**The dead module**: `src/omega/council/` (coordinator.py, execution_mode.py, failure_layer.py, hardware_detector.py, models.py, report_digestion.py) has **zero importers anywhere** — no `from omega.council` / `import omega.council` hits in src/, mcp_servers/, scripts/, or tests/. Its `models.py:157` hardcodes default `nodes_model: str = "gemma-4b-local"`.

**Ghost-model hazard (routing impact note)**: `council.yaml` `model_tiers` values reference models that exist in NO authoritative scheme:
- `gemma-4b-local` — absent from providers.yaml `supported_models` lists AND models.yaml keys (N1 F-12 already flagged this exact name).
- `nemotron-8b-cloud`, `nemotron-12b-cloud` — neither exists anywhere; only `nemotron-3-ultra-local` (providers.yaml) / `nemotron-3-ultra` (council.yaml research_execution.cloud_fallback) exist.
- `M7_local_first: false` (`council.yaml:68`, self-labeled "Advisory") — read by NOTHING; M7 enforcement actually lives in `provider_selector._calculate_score` PII penalty + fallback-chain priorities. No conflict is ACTIVE because nothing consumes the flag, but if anyone ever wires council.yaml up per SKILL.md instructions, they would inherit three ghost slugs and an M7-contradicting flag.

### Ticket direction
Cleanup ticket: (a) delete or explicitly archive `src/omega/council/` (dead module, M10 fleet-integrity analog for code); (b) purge or rewrite `config/council.yaml` + `config/council/profiles/{hybrid_local_pillars,local_8gb,local_16gb}.yaml` against the canonical models.yaml namespace IF the makali-council-coordinator skill is meant to be real — otherwise mark SKILL.md's config references as historical; (c) until then, record in WAKE_STATE that council tiering is governed by command files (`council-cloud/fast/local.md`), not council.yaml.

---

## VERIFICATION APPENDIX (commands run this session)

```bash
jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json   # → 12
git check-ignore --no-index -v data/coordination/TASK_REGISTRY.json  # → .gitignore:109 match
git ls-files --error-unmatch data/coordination/TASK_REGISTRY.json    # → tracked
rg --files data/coordination                                         # → empty (ignore-respect)
wc -l -c data/coordination/TASK_REGISTRY.json                        # → 2035 lines / 79066 bytes (normal shape — rules out size/binary causes)
```
Plus live MCP calls: `task_registry_query(tags=["express:first-light"])` → count 0 (repro); `grep` tool on data/coordination → "No files found" (repro).

*⬡ OMEGA ⬡ JEM ⬡ JEM_DEEP_DIVE_GAPS_5_7 ⬡ recon-only-complete ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

