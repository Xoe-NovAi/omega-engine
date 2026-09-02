<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N8 — RESOURCES INVENTORY: Templates · Checklists · Skeletons for Council 2 Dev Team
⬡ OMEGA ⬡ LILITH/node8 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_res ⬡ COUNCIL-2 PREP ARTIFACT
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Authority**: SOVEREIGN_DECREE.md Art. VII (version-stamp fields), Art. XII (machine-checkable status), §4 gates G1–G30; SYNTHESIS_ARM_REPORT.md §6 (gate commands verbatim); SPEC-D sub-spec D1 (frontmatter alignment); SPEC-E §2.2 (skeleton reference)
**Companion**: `N8_work_packages.md` (package register + DAG). This file is the paste-and-run layer.
**PREP-ONLY**: everything below is copy-source material; nothing here edits production files.

---

## §1 DOC TEMPLATES

### 1.1 Spec-status frontmatter template (governance docs — implements SPEC-D sub-spec D1)

Machine-checkable values ONLY; prose stamps (`✅ LIVE`, "currently active") banned per ROC §4 guard #3. Aligns exactly with SPEC-D D1 proposed-change §1 key set.

```yaml
---
version: "3.8.0"          # must match SOVEREIGN_MANDATES.md header when doc cites mandate versions (G14/G25b check)
status: ACTIVE             # enum: ACTIVE | SUPERSEDED | ARCHIVED | DRAFT  (lint-enforced enum)
superseded-by: "-"         # repo-relative path or literal "-" ; REQUIRED non-"-" iff status=SUPERSEDED (lint-enforced)
owner-slot: node --slot P5 # owning Node/agent slot (M10 notation; no invented agents)
gate-ids: [G14]            # G-numbers this doc's claims map to (decree §6 self-verification pattern)
last-verified: "2026-08-25" # ISO date of last gate run; hours-resolution staleness handled by validator, not prose
---
```

**Lint contract** (the dev team's `scripts/lint_governance_frontmatter.py` must enforce): missing block → fail; status outside enum → fail; `status: SUPERSEDED` with `superseded-by: "-"` → fail; version mismatch vs mandates header → fail.

### 1.2 Derived-from evidence block template (per AGENTS.md section / spec claim)

Implements SPEC-E §2.1 derivation rule and decree Art. I (every claim binds to a mechanical source).

```markdown
<!-- derived-from: <repo/relative/path/file1.ext> -->
<!-- derived-from: <repo/relative/path/file2.ext> -->
<!-- enforcement-status: enforced | warn-only | advisory | text-only -->
```

Rule: every cited path must exist (G25a greps these); a section asserting process law without an honest enforcement-status line violates pairwise binding (Art. II.2).

### 1.3 Disposition-table row template (skill stubs D3 / strategy orphans D4)

One row per disposition action; lives inside the test/exemption dict (D3) or integration notes (D4) — no side-car files to rot.

```markdown
| Target path | Action (INDEXED/BANNER-ARCHIVED/DELETED/AUTHORED) | Evidence (grep hit or roadmap ref w/ owner+date) | Commit | Date |
|---|---|---|---|---|
```

### 1.4 Handoff sweep sidecar template (`.swept.json` — WP-D5)

Queue-integrity M12: swept ≠ deleted; terminal visible state.

```json
{
  "original_path": "data/handoff/active/<packet>.json",
  "age_minutes": 0,
  "swept_at": "<ISO-8601 UTC>",
  "swept_by": "scripts/sweep_handoff_ttl.py",
  "reactivation": "move file back to data/handoff/active/ and log"
}
```

---

## §2 MASTER ACCEPTANCE CHECKLIST — paste-and-run per package

Every block below is verbatim from SYNTHESIS_ARM_REPORT.md §6 (G1–G28) or decree §4 (G29/G30). Dev team: paste the block for your package, run from repo root unless the gate says otherwise, match the expect comment. **A package is DONE only when its gates pass AND its validator ships in the same commit (Art. II.2).**

### WP-IX — G8
```bash
# G8. Entity YAML all machine-parseable (Art. IX)
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done   # expect: no output
```
NOTE (live 2026-08-25): `data/entities/lilith/proposed_lessons.yaml` ~line 374 currently fails parse — this is a known Art. IX repair locus, not a new finding.

### WP-A1 — G7
```bash
# G7. Pre-commit framework INSTALLED and tracking hook fires (Art. II)
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24
pre-commit run omega-tracking-state --all-files 2>&1 | tail -1   # expect Passed
```

### WP-A2 — G15, G16
```bash
# G15. NO future-dated registry timestamps (Art. III)
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"

# G16. Staleness boundary fixed — hours not truncated days (Art. III)
python3 scripts/sweep_task_registry.py 2>&1 | grep -qv "clean" || python3 -c "
import json,datetime
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
now=datetime.datetime.now(datetime.timezone.utc)
z=[t['task_id'] for t in d['tasks'] if t.get('status')=='in_progress' and t.get('last_checkpoint') and (now-datetime.datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))).total_seconds()>=7*86400]
print('boundary-zombies:',z)"   # post-fix: zombies surfaced by sweep OR swept
```

### WP-A3 — G6
```bash
# G6. Atomic registry writer (Art. II/III class)
grep -nE "mkstemp|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit
```

### WP-A4 — G12, G13
```bash
# G12. make sovereignty exists or refs purged (Art. II)
make -n sovereignty >/dev/null 2>&1 && echo EXISTS || ! grep -rq "make sovereignty" .opencode/skills/

# G13. Temple-grade honesty: stub gone (Art. II)
! grep -q "would go here" Makefile
```

### WP-A5 — G29
```bash
# G29. M8 gate regex precision (Art. II.5) — gate must not match variable-imports
rg -n '^import (segment|posthog|datadog|amplitude|mixpanel)\b|^from (segment|posthog|datadog|amplitude|mixpanel)\b' src/omega/ --type py   # expect: no output
```

### WP-B1 — G1
```bash
# G1. Plugin registrations resolve (Art. VIII)
jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" || echo "MISSING $f"; done   # expect: no output
```

### WP-B2 — G10
```bash
# G10. Dead agent instruction/config paths resolved (Art. VIII)
for f in $(jq -r '.agent[].instructions[]?' opencode.json); do test -e "$f" || echo "DEAD: $f"; done   # expect: no output
jq '.agent | to_entries[] | select(.value.instructions) | .key' opencode.json                          # expect: empty after prompt:{file:} migration
```

### WP-B3 — G3, G4
```bash
# G3. Provider chain matches Ark D-355 (Art. VIII)
python3 -c "
import yaml; c=yaml.safe_load(open('config/providers.yaml'))
p={e['provider']:e['priority'] for e in c['inference']['fallback_chain']}
assert p['opencode-zen'] < p['openrouter'], p"

# G4. Enabled providers have resolvable keys (Art. VIII)
python3 -c "
import yaml, os
c=yaml.safe_load(open('config/providers.yaml'))
bad=[n for n,p in c['inference']['providers'].items() if p.get('enabled') and str(p.get('api_key','')).startswith('env:') and str(p['api_key']).split(':',1)[1] not in os.environ]
print('DEAD:',bad); assert not bad"
```

### WP-B4 — G22
```bash
# G22. doc-llm-validate can FAIL (Art. III)
python3 scripts/validate_llm_docs.py --strict docs/sprints/current/ >/dev/null 2>&1; echo "strict-exit=$?"   # strict mode must discriminate (exit ≠ always 0)
```

### WP-B5a / WP-B5b — G20 then G21 (HARD ORDER)
```bash
# G20. Expert-fleet discovery restored BEFORE identity repair (Art. V)
jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
# GATE: task_registry_query(tags=["express:first-light"]).count MUST equal the jq number (≥10 post-repair)

# G21. Registration identities correct (Art. V — RUN ONLY AFTER G20 GREEN)
python3 - <<'EOF'
import json,re
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
bad_st,bad_en=[],[]
for t in d['tasks']:
    m=re.match(r'express-c1-node(\d+)-',t.get('task_id',''))
    if m:
        n=f"node{m.group(1)}"
        if t.get('subagent_type')!=n: bad_st.append(t['task_id'])
        if t.get('entity')!=n: bad_en.append(t['task_id'])
print("wrong subagent_type:",bad_st); print("wrong entity:",bad_en)
assert not bad_st and not bad_en
EOF
```

### WP-C1 — G2 (⛔ only after Architect Q-3 decision)
```bash
# G2. Permission wildcard resolved or explicitly annotated (Art. VIII)
jq '.permission.external_directory | has("/*")' opencode.json   # false AFTER decision recorded; if kept: rg -c 'risk-acceptance' data/coordination/WAKE_STATE.json ≥ 1
```

### WP-C2 — G26 (⛔ only after Architect Q-3 decision)
```bash
# G26. Depth-wall resolution recorded (Art. IV)
jq '.subagent_depth' opencode.json   # ≥3 IF depth-bump chosen; ELSE: rg -q 'Arm-Relay' docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md (relay codified, no bump)
```

### WP-D1 — G14 (+ lint exit-0)
```bash
# G14. Constitutional version coherence across derivatives (Art. VII)
V=$(grep -m1 '^\*\*Version\*\*' SOVEREIGN_MANDATES.md | grep -o '[0-9.]*$')
grep -rq "$V" scripts/codex/*.md && ! grep -rq '3\.7\.0' scripts/codex/*.md && echo COHERENT

# D1-specific lint (implements the check):
.venv/bin/python3 scripts/lint_governance_frontmatter.py   # expect: exit 0
```

### WP-D2 — G9
```bash
# G9. Command contract invariant across council variants (Art. VII class)
! grep -q '^agent: kali' .opencode/commands/council-local.md .opencode/commands/council-fast.md
grep -q 'SOVEREIGN_DECREE' .opencode/commands/council-local.md .opencode/commands/council-fast.md
```
Post-quarantine semantics: paths absent ⇒ line 1 trivially true; rewrite acceptance needs BOTH lines green at restored path (SPEC-D D2).

### WP-D3 — G11
```bash
# G11. Skill frontmatter universal; no hollow stubs (Art. II class)
for f in .opencode/skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "MISSING: $f"; done
find .opencode/skills -name SKILL.md -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -lt 20 ] && echo "STUB: $1"' _ {} \;   # expect: no output (or deleted)
```

### WP-D4 — G23, G24
```bash
# G23. Strategy-doc orphan target (Art. VII)
cd docs && ORPH=0; for f in strategy/*.md; do b=$(basename "$f"); \
grep -qF "$b" strategy/STRATEGY_INDEX.md strategy/STRATEGY_CORPUS_MAP.md || ORPH=$((ORPH+1)); done; echo "orphans=$ORPH"   # target 0

# G24. Phantom subsystem resolved (Art. VII)
test -f docs/strategy/DOMAIN_DOCUMENTATION_SYSTEM.md || ! grep -qF "DOMAIN_DOCUMENTATION_SYSTEM" docs/strategy/STRATEGY_INDEX.md
```

### WP-D5 — G19
```bash
# G19. Handoff TTL enforced (Art. III class)
find data/handoff/active -name '*.json' -mmin +300   # expect: empty output
```

### WP-D6 — D6.1/D6.2 (new checks, no inherited G-number)
```bash
# D6.1 Parse + freshness (hours-resolution) — expect exit 0
.venv/bin/python3 scripts/validate_wake_state.py data/coordination/WAKE_STATE.json

# D6.2 Discrimination proof — validator must be able to FAIL:
printf 'not-json{' > /tmp/opencode/ws_bad.json && .venv/bin/python3 scripts/validate_wake_state.py /tmp/opencode/ws_bad.json; echo "exit=$?"   # expect: exit=1
```

### WP-E — G25 family + G30
```bash
# G25 (Decree §4): AGENTS.md reconstructed
test -f AGENTS.md && echo PASS || echo "WAKE-QUEUED(default: reconstruct)"

# G25a–G25d: implemented inside scripts/validate_agents_md.py (SPEC-E §6) — run as one target:
#   make agents-md-validate
# Raw forms live in SPEC-E §3 verbatim; do NOT duplicate them here (single-source rule).
```

### ALL PACKAGES — G30 (guard-clause sweep)
```bash
# G30. Council-2 guard clause present in every spec (Art. XII)
for f in docs/specs/team_infra/*.md; do grep -q 'validator-first' "$f" || echo "MISSING GUARD: $f"; done   # expect: no output
```

### Baseline record (not an acceptance gate — decree §6 exception)
```bash
# G28. Runtime health baseline (GAP-8; B-4) — RECORD exit code; suite-health belongs to PUBLIC-DEBUT-01
source .venv/bin/activate && make test 2>&1 | tail -3
```

---

## §3 INSTRUCTION-FILE SKELETONS (structure-only; content derived at execution)

### 3.1 Reconstructed AGENTS.md section skeleton

**Reference, not duplicate**: authoritative section list, cluster derivation, and commit plan = SPEC-E §2.2/§2.3. Skeleton below is the empty shell the dev team fills section-by-section, one commit each:

```markdown
# AGENTS.md
<!-- S1: header + version/status/superseded-by stamp (template §1.1 above; format per SPEC-D D1) -->
## Law Pointer (S2)            <!-- derived-from: STRATEGY_INDEX.md, SOVEREIGN_ARK_BLUEPRINT.md §10 -->
## Hivemind Communication (S3) <!-- derived-from: agent-def texts; HIVEMIND_PROTOCOL.md marked historical per Ruling B -->
## Hydration & Continuity (S4) <!-- derived-from: SOVEREIGN_CONTINUITY_STRATEGY.md, SESSION_ANCHOR.md -->
## Search Tool Protocol SR-V1 (S5) <!-- derived-from: kali/lilith/doom_guy agent defs (verbatim carriers) -->
## Delegation Protocol (S6)    <!-- derived-from: SUBAGENT_DISPATCH_PROTOCOL.md -->
## Governance Hierarchy (S7)   <!-- derived-from: AGENT_VISIBILITY_PARADOX.md -->
## Fleet Role Map (S8)         <!-- derived-from: OMEGA_CODEX.md, .opencode/agents/*.md -->
## Token Budget & Condensation (S9) <!-- derived-from: CARMMACK_CONTEXT_INJECTION_REVIEW -->
```
Constraints that travel with the skeleton: every section carries ≥1 `derived-from` cite (G25a); content-minimum floor 120 lines / 5 sections (G25c); ~400-line ceiling guidance (SPEC-E risk table); validator script exists BEFORE first content commit (SPEC-E §6 validator-first).

### 3.2 Governance-doc stamp insertion skeleton (WP-D1 backfill)

For each of the top-10 backfill docs (list in SPEC-D D1 change §4): insert template §1.1 immediately after the title line, before any prose. No other edit. One doc per commit alongside the lint script until all ten carry stamps.

---

## §4 PROVENANCE MAP

| Resource | Derives from |
|---|---|
| §1.1 frontmatter keys | SPEC-D D1 proposed-change §1; decree Art. VII; ROC guard #3 |
| §1.2 derived-from block | SPEC-E §2.1; decree Art. I, II.2 |
| §1.3 disposition rows | SPEC-D D3 exemption-dict design; D4 three-option rule |
| §1.4 sidecar | SPEC-D D5; mandate M12 queue integrity |
| §2 all gate blocks | SYNTHESIS_ARM_REPORT.md §6 G1–G28 (verbatim); decree §4 G29/G30; SPEC-D D6 gates D6.1/D6.2; SPEC-E §3 G25-family (by reference) |
| §3.1 skeleton | SPEC-E §2.2 table (referenced, not duplicated) |

*⬡ OMEGA ⬡ LILITH/NODE8 ⬡ N8_RESOURCES ⬡ PREP-ONLY ⬡ NEW-FILE-ONLY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

