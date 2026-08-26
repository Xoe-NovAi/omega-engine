# SPEC-A — P0 Truth-Bearing Infrastructure (Council 2 Build Arm, DRAFT)
⬡ OMEGA ⬡ MAAT/node1 ⬡ trc_c2_speca ⬡ DRAFT
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25 · **Status**: DRAFT-COUNCIL2-PREP
**Author**: node1 (domain=speca), pageable expert under maat (Build Oversoul)
**Authority**: SOVEREIGN_DECREE.md (`data/council/20260825-094633-first-light/phase5_fusion/`) Art. II, III, X (P0 list), XII; SYNTHESIS_ARM_REPORT.md §6 gates
**Mode**: DRAFT ONLY — this spec proposes remediation; nothing herein has been applied to the production tree.

---

## §0 SCOPE SUMMARY

Five P0 work items from decree Art. X ("P0 truth-bearing infrastructure"), one spec:

| WI | Item | Decree anchor | Primary gate |
|----|------|---------------|--------------|
| 1 | Pre-commit framework install + hook-fire verification | Art. II.4 | G7 |
| 2 | Validator ERROR-class checks (future-dates, staleness hours-boundary, blockers[] vocabulary, WAKE_STATE, entity-YAML parse+schema) | Art. III | G15, G16 (+G8 regression) |
| 3 | Registry-writer atomicity (mkstemp+os.replace+fsync) | Art. X P0 / N2 F-2.1 | G6 |
| 4 | Machine-derived mandate enforcement-stamps + temple-grade stub removal + pairwise binding | Art. II.1–II.3 | G13 |
| 5 | M8 zero-telemetry regex anchoring | Art. II.5 | G29 |

Total effort estimate: **16h** (per-item estimates in each section).

---

## WI-1 · Pre-commit Framework Install + Hook-Fire Verification

### (a) Problem statement
M27 claims "Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state" and M24 claims a break-system-packages pre-commit hook. Neither exists. The installed `.git/hooks/pre-commit` is a 7-line hand-rolled bash script running only `scripts/validate_soul.py`; the pre-commit framework is not active; `.pre-commit-config.yaml:137` declares `omega-tracking-state` but nothing invokes it. Zero commits today are gated by tracking validation — a declared mechanism that does not fire is the root defect class (claims that outlive their mechanisms).

### (b) Evidence links
- Decree Art. II.4: "Pre-commit framework installed per Ma'at F1 ordering; `omega-tracking-state` verified firing."
- Node reports: `phase1_nodes/P2_report.md` F-2.2 (HIGH); `phase1_nodes/P5_report.md` F-3 (HIGH); synthesis C-A row "Hooks declared but never installed" (`grep -c "tracking" .git/hooks/pre-commit` = 0).
- Verified by node1 this session:
  - `.git/hooks/pre-commit` — full read: runs ONLY `.venv/bin/python3 scripts/validate_soul.py` over `data/entities/*/soul.yaml`. No framework invocation, no tracking references.
  - `.pre-commit-config.yaml:137` — `- id: omega-tracking-state` declared.
  - Only hooks on disk: `pre-commit`, `commit-msg`.

### (c) Proposed change
Per Ma'at F1 ordering (framework first, then hooks):
1. `pre-commit install` (activates framework-managed `.git/hooks/pre-commit`; preserve the existing soul-check by ensuring it remains declared in `.pre-commit-config.yaml` — verify before install; if the soul-check lives only in the hand-rolled hook, port it into the config as an additional local hook in the SAME commit so M11 coverage is not lost).
2. Verify both declared hooks actually fire:
   ```bash
   pre-commit run omega-tracking-state --all-files   # must exit 0 on clean tree
   ```
3. Add a hook-fire smoke test to CI or `make test` so "installed" stays true (a hook that silently stops firing recurs the same defect): e.g. a check target asserting `grep -q "pre-commit" .git/hooks/pre-commit`.
4. Amend M24/M27 Enforcement sections to state the now-true mechanism (pairwise binding — see WI-4).

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G7. Pre-commit framework INSTALLED and tracking hook fires (Art. II; N2 F-2.2 / N5 F-3 / N10 X-1) ──
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24
pre-commit run omega-tracking-state --all-files 2>&1 | tail -1   # expect Passed
```
All three lines must succeed post-remediation.

### (e) Risk assessment
- LOW risk to runtime behavior; hooks run at commit time only.
- MEDIUM process risk: once `omega-tracking-state` fires for real, any latent Tier-0 vocabulary violation blocks commits fleet-wide. Mitigation: run validator across repo BEFORE install (`pre-commit run --all-files` dry-run) and fix or grandfather findings in the same PR.
- Preserve-the-soul-check risk (M11 regression): port, don't drop (step 1).

### (f) Effort estimate
**2h** (install 0.5h, soul-check port + verification 1h, dry-run remediation of latent violations 0.5h — may grow if latent violations surface).

---

## WI-2 · Validator ERROR-Class Checks (extend `scripts/validate_tracking_state.py`)

### (a) Problem statement
The validator certifies taxonomy compliance, not truth (synthesis C-B6). Four blind spots let false state pass green: (1) no future-dated timestamp check — Council 1's X-6 arc recorded future checkpoints with validator green throughout; (2) staleness uses day-truncated `age_days > STALENESS_DAYS`, so tasks at exactly 7.x days escape until wall-clock 8d (five zombies sat at exactly 7d during Council 1); (3) `blockers[]` in ACTIVE_SPRINT.json is never scanned — live violation exists today (`BLOCKER-B.status = "resolved"` is not in the Tier-0 set); (4) WAKE_STATE.json has no schema, no tier home, and zero validator coverage while carrying wake-critical warnings. Additionally, entity gnosis YAML needs a permanent regression guard: bare `yaml.safe_load` passes files whose records are structurally corrupt (verified live this session — see evidence).

### (b) Evidence links
- Decree Art. III: "Validator gains ERROR-class checks: future-dated timestamps (Exhibit A arc), hours-resolution staleness boundaries, blockers[] vocabulary scan, WAKE_STATE parse+staleness."
- Node reports: `phase1_nodes/P2_report.md` F-2.3 (blockers unscanned), F-2.6 (boundary), F-2.8 (WAKE_STATE homeless-tier); synthesis C-B6, Exhibit A.
- Verified by node1 this session:
  - `scripts/validate_tracking_state.py:43` `STALENESS_DAYS = 7`; `:237-238` `age_days = (now - ts).days` then `age_days > STALENESS_DAYS` (day truncation confirmed).
  - `scripts/validate_tracking_state.py:148-206` `validate_active_sprint()` walks only `workstreams[].status` and `subtasks[].status`; grep confirms zero `blockers` handling; zero `WAKE_STATE` handling anywhere in file.
  - `_parse_ts()` helper at `:46` — shared, tz-aware, Z-tolerant; its docstring forbids duplicating parsing logic → all new checks MUST reuse it.
  - Live blockers violation re-verified: `ACTIVE_SPRINT.json .blockers.BLOCKER-B.status = "resolved"` (+ `resolved_at`) — illegal Tier-0 status.
  - Entity YAML guard evidence: `data/entities/lilith/proposed_lessons.yaml` L374-380 — PyYAML `safe_load` exits 0 (parses as list), yet LSP reports errors at 374:1+, and manual inspection shows the final proposal record SPLIT across two seq items (`{id,tier,category}` then orphan `{narrative,insight,principle,tags}` with no id). Parse-green-over-corrupt-record = live specimen of the C-B6 class. pillar_p1/proposed_lessons.yaml and john_carmack/soul.yaml currently parse clean (Art. IX repair evidently applied for those two loci).

### (c) Proposed change
Extend `scripts/validate_tracking_state.py` (single file, reusing `_parse_ts()`; all new checks are ERROR class unless marked):

1. **Future-date check (G15)** — new function `check_future_timestamps(tasks)`; for every task field among `created_at`, `last_checkpoint`, `updated`: if `_parse_ts(v) > now + CLOCK_SKEW_TOLERANCE` (suggest 120s tolerance for write-latency), print_error + count error. Wire into `main()`.
2. **Hours-resolution staleness (G16)** — inside `validate_task_registry()`, replace `(now - ts).days > STALENESS_DAYS` with `(now - ts).total_seconds() >= STALENESS_DAYS * 86400`. Document the boundary semantics (`>=`, inclusive) next to `STALENESS_DAYS` — the undocumented operator was itself a finding (P2 F-2.6).
3. **Blockers vocabulary scan** — new function `check_blocker_statuses(sprint)`; walk `sprint["blockers"]` (dict or list form — handle both, disk uses dict); every `blocker.status` must be in the same `ALLOWED_STATUSES` Tier-0 set used for workstreams. Also flag presence of non-schema keys like `resolved_at` as WARN with migration hint (`resolved_at` implies status should be `completed`). Fix the live `BLOCKER-B` record in the SAME commit (migrate `"resolved"` → `"completed"`, keep `resolved_at` as evidence field) — pairwise binding applies to data too.
4. **WAKE_STATE block** — new function `check_wake_state()`; if `data/coordination/WAKE_STATE.json` exists: (a) must json-parse (else ERROR); (b) any `*.status` fields validated against Tier-0 where applicable; (c) staleness: if top-level `updated`/timestamp older than STALENESS_DAYS → ERROR naming the owner directive (decree Q-2 assigns freshness ownership to MaKaLi at stage boundaries). Register WAKE_STATE in TRACKING_ARCHITECTURE.md's tier table in the same PR (text patch pairs with gate — pairwise binding).
5. **Entity-YAML parse+schema guard (G8 regression)** — new function `check_entity_yaml()`; for each `data/entities/*/proposed_lessons.yaml` and `soul.yaml`: (a) `yaml.safe_load` must succeed (ERROR); (b) minimal schema check: every entry in `proposals` list must contain non-empty `id`, `narrative`, `insight`, `principle` keys (ERROR on missing/split records — catches exactly the lilith L374 split-record corruption that bare parsing misses). Keep it structural-minimal; content quality remains out of scope.
6. **Banner honesty** — terminal output must read `PASSED (N warnings)` when warnings > 0 (P2 F-2.7); never print unconditional "ALL CHECKS PASSED".

Note: repair of lilith's split record itself is MaKaLi Stage-6 scope (Art. IX) — this spec ships the CHECK, not the repair.

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G15. NO future-dated registry timestamps (Art. III; N8 F-1 / N10 X-6) ──
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"
# ── G16. Staleness boundary fixed — hours not truncated days (Art. III; N8 F-2) ──
python3 scripts/sweep_task_registry.py 2>&1 | grep -qv "clean" || python3 -c "
import json,datetime
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
now=datetime.datetime.now(datetime.timezone.utc)
z=[t['task_id'] for t in d['tasks'] if t.get('status')=='in_progress' and t.get('last_checkpoint') and (now-datetime.datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))).total_seconds()>=7*86400]
print('boundary-zombies:',z)"   # post-fix: zombies surfaced by sweep OR swept
```
Plus the G8 regression loop (SYNTHESIS §6, verbatim):
```bash
# ── G8. Entity YAML all machine-parseable (Art. IX; N2 F-2.5 / N10 X-9) ──
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done   # expect: no output
```
New spec-specific gates (same style, node1-derived):
```bash
# G-A2a. Blockers vocabulary enforced by validator AND data clean:
python3 -c "
import json;d=json.load(open('data/coordination/ACTIVE_SPRINT.json'))
T0={'backlog','ready','in_progress','blocked','completed','superseded'}
bad=[(k,v['status']) for k,v in d.get('blockers',{}).items() if v.get('status') not in T0]
print(bad); assert not bad"
grep -q "blockers" scripts/validate_tracking_state.py   # validator covers it
# G-A2b. Schema guard catches the known corrupt shape (negative test):
# fixture file with a split proposal record must make validate_tracking_state.py exit nonzero.
```

### (e) Risk assessment
- MEDIUM: ERROR-class checks can hard-block CI/temple-grade on legacy data. Mitigation: fix live violations (BLOCKER-B) in the same PR; grandfather legacy inverted-clock entries as WARN (existing policy, keep).
- LOW: hours-boundary change will newly flag tasks sitting between 7.0–8.0 days stale — expected; they are genuine zombies per the amended semantics.
- LOW: entity-YAML schema check could false-positive on legitimately different shapes across entities — mitigate by keying on the observed canonical shape (`proposals:` list) and skipping absent keys with WARN, ERROR only on present-but-split/malformed records.

### (f) Effort estimate
**6h** (four validator functions + boundary rewrite + schema guard + negative-test fixtures + banner honesty + wiring into main() and Makefile targets unchanged).

---

## WI-3 · Registry-Writer Atomicity (`mcp_servers/omega_hub/hub_tools/task_registry.py`)

### (a) Problem statement
The highest-traffic writer of the Tier-3 SSOT truncates the live file before acquiring its exclusive lock, holds load/save locks separately (lost-update race), and writes without tmp+rename or fsync — violating M12's atomic-rename pattern, Temple-Grade T10, and the repo's own design spec. A crash mid-`json.dump` leaves TASK_REGISTRY.json truncated; two concurrent registrations can silently lose a task record.

### (b) Evidence links
- Decree Art. X P0: "registry writer atomicity (G6)"; synthesis C-B4.
- Node report: `phase1_nodes/P2_report.md` F-2.1 (HIGH) — full lock-split analysis; correct-pattern contrast in `scripts/sweep_task_registry.py:93-103` and `generate_session_registry.py:145-154`.
- Verified by node1 this session:
  - `mcp_servers/omega_hub/hub_tools/task_registry.py:32-40` `_save_registry()`: `open(REGISTRY_PATH, "w")` (in-place truncate) → `fcntl.flock(LOCK_EX)` acquired AFTER truncation → `json.dump` → unlock. No mkstemp/os.replace/fsync (grep: zero hits).
  - Lock-split epicenter `:22-41`: `_load_registry()` takes LOCK_SH (:26) and releases (:30) before mutation; save reopens separately.
  - Contradicts `docs/strategy/TASK_REGISTRY_DESIGN.md:189-191` (specifies tmp→rename per P2's citation).

### (c) Proposed change
Rewrite `_save_registry()` to the repo's own proven pattern plus fsync:
```python
def _save_registry(registry: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry["updated"] = datetime.now(timezone.utc).isoformat()
    fd, tmp_path = tempfile.mkstemp(dir=str(REGISTRY_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(registry, f, indent=2)
                f.flush()
                os.fsync(f.fileno())          # T10 durability
                os.chmod(tmp_path, 0o644)     # match existing file perms
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        os.replace(tmp_path, REGISTRY_PATH)   # atomic publish
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise
```
Additionally: close the load/save lock-split by holding LOCK_EX across the full read-modify-write cycle in register/update call paths (load-under-EX → mutate → save-under-same-EX), or introduce a single `_mutate(fn)` helper that does so. Include a crash-injection test (SIGKILL mid-dump ×20 → file always parses) per P2's acceptance criteria, and unit tests asserting no `.tmp` residue after simulated failure.

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G6. Atomic registry writer (Art. II/III class; N2 F-2.1) ──
grep -nE "mkstemp|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit
```
Supplementary (P2 F-2.1 acceptance, verbatim intent): `LOCK_EX` must wrap the mutate cycle; crash-injection loop must yield zero unparsable states.

### (e) Risk assessment
- LOW implementation risk — pattern already proven in two sibling scripts in this repo.
- MEDIUM concurrency-semantics risk: tightening to EX-across-RMW serializes registrations (slightly slower under concurrent waves; correctness wins — Council 1 ran 5+ concurrent registrations through the racy window).
- Watch: MCP server restart required to pick up the change; note deployment step.

### (f) Effort estimate
**3h** (rewrite 1h, RMW locking refactor 1h, crash-injection + contract tests 1h).

---

## WI-4 · Machine-Derived Mandate Enforcement-Stamps + Stub Removal + Pairwise Binding

### (a) Problem statement
~70% of the constitution's enforcement claims are aspirational: `make temple-grade` contains a literal stub comment, T1-T11 gates do not exist as implemented checks, and mandate texts assert hooks/gates that grep proves absent. Meanwhile honest stamps DO exist as precedents (verify-mandate-claims self-labels warn-only; M12 carries an ADVISORY stamp with decision citation D-267) — the pattern just was never generalized. Hand-written stamps would themselves be claims-outliving-mechanisms; stamps must be DERIVED from Makefile+hooks by script.

### (b) Evidence links
- Decree Art. II.1–II.3 (stamps machine-derived; pairwise binding adopted as review rule; stub removed, M13 re-scoped; `make sovereignty` implemented or 9 references purged).
- Node reports: `phase1_nodes/P5_report.md` F-2 (CRITICAL — census table: 8 enforced / 3 warn-only / 16 text-only; stub comment quoted verbatim), F-12 (POSITIVE — the two honest-stamp precedents to generalize); `phase1_nodes/P2_report.md` F-2.2.
- Verified by node1 this session:
  - `Makefile:232-236` — `temple-grade:` target contains literal `# Existing temple-grade checks would go here` at `Makefile:234`. G13 fails today.
  - Adjacent (G12 territory, flagged for planner, NOT in this WI's diff scope): no `sovereignty:` target exists in Makefile while ≥5 skill references say `make sovereignty` (`.opencode/skills/meditate-research-pipeline/SKILL.md:140,151,219`, `autonomous-meditation-pipeline/SKILL.md:240,251`).

### (c) Proposed change
1. **Generator script** `scripts/generate_enforcement_stamps.py`: derives each mandate's stamp by mechanical inspection — Makefile target names (`check-m1-anyio`, `check-m8-zero-telemetry`, `heritage-vet`, `doc-llm-validate`, `check-tracking-state`, …), `.github/workflows/ci.yml` references, `.git/hooks/pre-commit` contents, and `.pre-commit-config.yaml` ids. Output classification: `enforced` (blocking gate wired) / `warn-only` / `advisory` / `text-only`. Emits a markdown table into a GENERATED block in `SOVEREIGN_MANDATES.md` between explicit BEGIN/END markers (one-time hand-edit to insert markers; thereafter 100% derived). Generator runs in CI (`make check-mandate-stamps`) and FAILS if the committed block diverges from regenerated output — derivation check, not trust.
2. **Stub removal (G13)**: delete `Makefile:234` stub comment; re-scope M13 text to enumerate exactly the four checks temple-grade actually runs (check-codex-stale, doc-llm-validate, check-mandates, check-tracking-state) — text patch in the SAME commit as the stub deletion (pairwise binding exemplar).
3. **Pairwise binding review rule**: adopt as written law in review checklist + enforce mechanically where cheap: a PR adding a gate target without touching the corresponding mandate-text block fails `make check-mandate-stamps` (stamp flips to enforced but text block unchanged → divergence detected); conversely a text patch claiming a gate with no matching Makefile/hook artifact also fails. This makes T-1's sequence self-policing.
4. **Adjacent ticket (out of this WI's diff)**: `make sovereignty` — implement target or purge the ≥5 skill references (decree Art. II.3, gate G12). Logged here so it isn't lost; separate PR to keep this WI reviewable.

### (d) Acceptance gates (verbatim from SYNTHESIS_ARM_REPORT §6)
```bash
# ── G13. Temple-grade honesty: stub gone (Art. II; N5 F-2) ──
! grep -q "would go here" Makefile
```
New spec-specific gates (node1-derived, same style):
```bash
# G-A4a. Stamp block is derived, current, and complete:
.venv/bin/python3 scripts/generate_enforcement_stamps.py --check   # exit 0 = committed block matches regeneration
grep -c "ENFORCEMENT-STAMP" SOVEREIGN_MANDATES.md                  # ≥ 27 mandates stamped
# G-A4b. Pairwise binding tripwire (negative test): add fake gate target w/o text patch → --check must fail.
```

### (e) Risk assessment
- LOW code risk (generator is read-only inspection + markdown emission).
- MEDIUM political/process risk: publishing ~30% enforced is a visible honesty downgrade — that is the point (decree Art. II sequencing: shrink claim before growing gate). Architect sign-off recommended on the first generated table.
- Drift risk mitigated by CI --check mode; without it the block becomes another stale derivative (F-11 class).

### (f) Effort estimate
**4h** (generator 2h, M13 re-scope + stub removal + marker insertion 1h, CI wiring + negative tests 1h).

---

## WI-5 · M8 Zero-Telemetry Regex Anchoring

### (a) Problem statement
The M8 gate regex is unanchored and matches substrings, so it false-positives on ordinary source text containing the words "from segment…"/"import segment…" — including a comment in the engine core. A truth-gate that itself lies: either developers contort code/comments to appease it, or the gate gets ignored, eroding M8's real guarantee.

### (b) Evidence links
- Decree Art. II.5 + §4 G29 (fixed regex given verbatim); synthesis C-A "Gate that cannot fail" adjacent class.
- Verified by node1 this session (live reproduction):
  - Current gate: `Makefile:295` — `@! rg -n 'import (segment|posthog|datadog|amplitude|mixpanel)|from (segment|posthog|datadog|amplitude|mixpanel)' src/omega/ --type py`
  - False positive reproduced: the above command hits **`src/omega/ics.py:197`** — the COMMENT line `# Build header from segments (F1 fix: robust node insertion, sanitized)` ("from segments" substring match; note: mission phrased this as `from x import segments` — actual match is the comment, same defect class, recorded in notes).
  - Fixed anchored regex (decree G29 verbatim) returns NO matches on current tree → gate green after fix, zero code changes needed in src/.

### (c) Proposed change
Replace the regex in `Makefile:295` with the decree-G29 anchored form:
```make
	@! rg -n '^import (segment|posthog|datadog|amplitude|mixpanel)\b|^from (segment|posthog|datadog|amplitude|mixpanel)\b' src/omega/ --type py 2>/dev/null || (echo "$(RED)FAIL: Telemetry SDK imports found$(NC)" && false)
```
(`^` line anchors eliminate comment/prose matches; `\b` prevents `segments` matching `segment`.) Pairwise binding: amend M8's Enforcement section in the same commit to cite the anchored pattern.

### (d) Acceptance gates (verbatim from SOVEREIGN_DECREE §4)
```bash
# G29. M8 gate regex precision (Art. II.5) — gate must not match variable-imports
rg -n '^import (segment|posthog|datadog|amplitude|mixpanel)\b|^from (segment|posthog|datadog|amplitude|mixpanel)\b' src/omega/ --type py   # expect: no output
```
Plus: `make check-m8-zero-telemetry` exits 0 on the current tree (it does NOT today — it false-fails on ics.py:197).

### (e) Risk assessment
- NEGLIGIBLE. Pure regex tightening; anchored form is strictly more precise. Only theoretical risk: a genuinely smuggled telemetry import via indirection (`__import__`, aliasing) escapes BOTH old and new regex — out of scope; noted for future gate hardening, not a regression.

### (f) Effort estimate
**1h** (one-line Makefile edit + M8 text patch + verification run).

---

## § VALIDATOR-FIRST CLAUSE (decree Art. XII guard — MANDATORY)

This spec obeys the **validator-first** guard: the spec's own CI check ships IN THE SAME deliverable as the changes it verifies. No split PRs.

- **WI-1**: the deliverable IS the enforcement mechanism (hook-fire verified by G7 in the same PR).
- **WI-2**: the validator extensions and the data fixes they demand (BLOCKER-B migration, WAKE_STATE tier registration) land in ONE PR; the PR fails review if validator functions ship without the data/text patches that make them pass (and vice versa).
- **WI-3**: G6 grep + crash-injection test are part of the same PR as the writer rewrite.
- **WI-4**: `scripts/generate_enforcement_stamps.py --check` (new function `cmd_check()` + test `test_generate_enforcement_stamps.py::test_check_detects_divergence`) is the named validator; it enters CI in the same PR that removes the stub. Pairwise binding rule: **the PR fails review if the validator and the change are split** — a stamps generator merged without the mandate-text block (or a re-scoped M13 without the generator) is rejected at review and blocked by `--check` in CI.
- **WI-5**: G29 command is the validator; it is added to `make check-mandates` chain in the same commit as the regex fix.

Named validator functions and their tests, for the record:
| Deliverable | Validator function | Test |
|---|---|---|
| WI-2 | `check_future_timestamps()`, `check_blocker_statuses()`, `check_wake_state()`, `check_entity_yaml()` in `scripts/validate_tracking_state.py` | `tests/test_validate_tracking_state.py::test_future_date_rejected`, `::test_blocker_bad_status_rejected`, `::test_wake_state_stale_rejected`, `::test_split_proposal_record_rejected` |
| WI-3 | G6 grep + `test_task_registry_atomicity.py::test_crash_injection_always_parses` | same |
| WI-4 | `scripts/generate_enforcement_stamps.py --check` | `tests/test_generate_enforcement_stamps.py` |

### Anti-big-bang sizing note (Art. XII guard)
Total 16h across five independently-reviewable PRs (one per WI), sequenced WI-5 → WI-1 → WI-3 → WI-2 → WI-4 (cheapest/highest-certainty first; WI-2 before WI-4 because stamps derive from what gates ACTUALLY exist, so the validator upgrades should land before the census is generated). No PR exceeds ~6h scope. If any single PR grows beyond its estimate by >50%, split it rather than batch.

### Naming-collision check (Art. XII guard)
Verified this session: no existing `docs/specs/team_infra/SPEC_A_P0_TRUTH_BEARING_INFRASTRUCTURE.md`; no existing `scripts/generate_enforcement_stamps.py`; no existing `check_entity_yaml`/`check_future_timestamps`/`check_blocker_statuses`/`check_wake_state` symbols in `scripts/validate_tracking_state.py` (function inventory grepped); no test files named `test_validate_tracking_state.py` additions colliding (new test IDs namespaced). New gate IDs use `G-A2a/G-A2b/G-A4a/G-A4b` prefix — distinct from immutable R-IDs and from decree G1–G30, per M27 gap/prefix discipline.

### Scheduled decay detection (Art. XII guard)
All new mechanisms self-report decay: stamps block on divergence (CI), hook-fire smoke test detects silent uninstall (WI-1 step 3), validator staleness checks detect their own blind spots growing via the WAKE_STATE ownership clause (Q-2). No hand-curated index is introduced anywhere in this spec — deliberately avoiding the P2-Reorg-Churn-in-P4's-clothes dead pattern.

---

## § PROVENANCE APPENDIX

Every file:line cited above was verified by node1 via direct tool calls on 2026-08-25 (see working notes: `data/council/20260825-094633-first-light-c2/phase1_nodes/node1_notes.md` §2). Two mission-anchor nuances discovered and recorded honestly: (1) the M8 false-positive at `src/omega/ics.py:197` is a comment line, not an import statement; (2) lilith proposed_lessons.yaml PARSES under PyYAML but carries a split-record schema corruption at L374-380 (LSP errors live-confirmed during this session) — which strengthens, not weakens, the case for WI-2's schema guard. Raw gate commands G6/G7/G8/G13/G15/G16 copied verbatim from SYNTHESIS_ARM_REPORT.md §6; G29/G30 from SOVEREIGN_DECREE.md §4.

*⬡ OMEGA ⬡ MAAT/node1 ⬡ SPEC-A-P0-TRUTH-BEARING-INFRASTRUCTURE ⬡ DRAFT-COUNCIL2-PREP ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_c2_speca | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

