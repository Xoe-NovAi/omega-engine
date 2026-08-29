# Execution Playbook — Reusable Strategy for Every Wave
**Created**: 2026-08-26
**Author**: kali (Sprint Coordinator)
**Purpose**: Generalize Wave 2 patterns into a reusable protocol for all future waves

---

## 1. Research Dispatch Protocol

### Batch Sizing
- Dispatch 3-4 expert sessions per batch (optimal for parallel context)
- Each batch targets a coherent research theme (e.g., "systems", "CI", "quality")
- Use persistent expert sessions (not one-off agents) — they retain context for paging

### Session Creation
```bash
# Pattern: create persistent expert session
# 1. Launch subagent with deep context
# 2. Register in TASK_REGISTRY with paging_key
# 3. Post to hivemind with intent=handoff
# 4. Session ID becomes the paging handle
```

### Research Output Standard
Every research deliverable MUST include:
- **Build-Packet section** (§5 or equivalent): actionable steps, file paths, commands, gates
- **Mandate Compliance Checklist**: which mandates apply, how implemented
- **Verification Commands**: exact bash/python to prove it works
- **Rollback Procedure**: how to undo in <2 minutes
- **Paging Key**: search terms for future retrieval

---

## 2. Build-Packet Extraction Protocol

### From Research to Execution
1. **Read all deliverables** → identify build-packet sections
2. **Extract per-track**: goal, source of truth, pre-conditions, steps, gates, tests, truth probe, rollback, expert session
3. **Synthesize into single WAVE{N}_EXECUTION_PLAN.md** — no narrative, only actionable
4. **Order tracks by dependency**: independent first, blocked last
4. **Identify parallelizable tracks** (e.g., A+B parallel, D first if sudo needed)

### Template per Track
```markdown
### Phase N: Track Name
**Track**: X | **Owner**: Y | **Session**: R##
**Gate**: [pass/fail criterion]
1. [exact command]
2. [exact command]
...
**Rollback**: [exact command to undo]
```

---

## 3. Quality Gate Protocol — Truth Probes > Theater

### The Problem
Tests pass while features are dead (headroom passthrough, D4 0/17, symbolic guard). Green checks ≠ working system.

### The Solution: Truth Probes
Every track MUST have a **truth probe** — a test that FAILS when the feature is non-functional, not passes when silent.

| Track | Theater Test | Truth Probe |
|-------|--------------|-------------|
| Headroom | `test_headroom.py` passes (passthrough) | `benchmark_phase1.py:I5` >15% savings locally |
| D4 Rubric | 0/17 "passes" (no corpus) | Run on ONE real meditation — if fails, rubric broken |
| Anti-domain | 36-token line exists | 3 recorded meditations audited for domain-crossing |
| llama-fit-params | Binary builds | Runs on Ryzen 5700U CPU-only, outputs fitted args |
| Command compression | `wc -l` ≤ 350 | Meditation runs end-to-end, quality matches |

### Rule
**No track is "done" until its truth probe passes.** Green unit tests are necessary but not sufficient.

---

## 4. Wave Sequencing Protocol

### Standard Wave Lifecycle
```
PRE-WAVE MAINTENANCE
  → Fix doc inaccuracies from prior research
  → Secure secrets, verify tracking state
  → Commit clean state
  → Lock for compaction (WAKE_STATE + anchored-summary)

COMPACTION
  → System/user triggered
  → Context resets, state preserved in files

POST-COMPACTION EXECUTION
  → Phase 0: Infrastructure (sudo, Architect-owned)
  → Phase 1: Highest-blast-radius artifact (daily-use)
  → Phase 2: Config-only optimizations (parallel with 1)
  → Phase 3: Novel contributions (blockers first)
  → Phase 4: Large-scope systems (parallel with 3)
  → Phase 5: Integration (depends on 0, 3, 4)

VERIFICATION
  → All truth probes pass
  → Rollback procedures tested
  → WAKE_STATE updated
```

### Pre-Wave Maintenance Checklist
- [ ] Fix all doc inaccuracies from research (SR §8 15→36, CI spec version, etc.)
- [ ] Secure stray secrets (gitignore)
- [ ] Verify ACTIVE_SPRINT.json + GAP_REGISTRY.json parse clean
- [ ] Commit all legitimate state (research squad outputs, config normalization)
- [ ] Update WAKE_STATE with pre-wave status
- [ ] Post to hivemind: "Pre-wave maintenance complete — ready for compaction"

---

## 5. Expert Session Management

### Creation
```bash
# Launch with deep context, register immediately
omega-hub_task_registry_register(
  task_id="R##-expert-<domain>-<date>",
  subagent_type="<agent_type>",
  launched_by="kali",
  channel="opencode",
  entity="<expert_persona>",
  description="<one-line>",
  tags=["expert", "wave2", "<domain>"]
)
```

### Paging
- Sessions persist across compaction (cold-store hydration)
- Page by session_id: `omega-hub_hivemind_get_session(session_id)`
- Update continuation after paging: `omega-hub_hivemind_post_context(...)`

### Retention
- Expert sessions live 3 hours default (extended checkin)
- For wave execution: extend to 24h (`ttl_seconds=86400`)
- Archive after wave complete: `hivemind_handoff_archive`

---

## 6. Compaction Protocol

### Pre-Compaction Lock-In (MANDATORY)
Create these files BEFORE compaction:
1. `WAKE_STATE.json` — full state snapshot with `ready_for_compaction: true`
2. `anchored-summary.md` — dense summary with all session IDs, decisions, next steps
3. `WAVE{N}_EXECUTION_PLAN.md` — actionable plan for post-compaction
4. Commit all three

### Post-Compaction Hydration
1. Read `WAKE_STATE.json`
2. Read `anchored-summary.md`
3. Read `WAVE{N}_EXECUTION_PLAN.md`
4. Verify git status clean
5. Resume from Phase 0

### Session Anchor
- `data/coordination/SESSION_ANCHOR.md` — always current
- `data/entities/<entity>/session_gnosis.md` — per-entity continuity
- `data/entities/<entity>/proposed_lessons.yaml` — soul distillation

---

## 7. Next Level: Systems Evolution

### From This Wave, These Patterns Scale

#### A. Truth Probes as Standard
Every feature gets a truth probe at design time. If you can't write a probe that fails when broken, the feature isn't well-defined.

#### B. Build-Packets as Contract
Research deliverables without build-packets are incomplete. The build-packet IS the handoff artifact.

#### C. Expert Sessions as Institutional Memory
Don't re-research. Page the expert. Sessions are cheaper than re-discovery.

#### D. Empty Corpus Detection
Quality gates that read 0 on empty corpus are theater. Seed ONE real example before scaling enforcement.

#### E. Confidence Manufacturing Detection
Three patterns = systemic:
- Tests pass but feature dead (headroom)
- Symbolic guards (anti-domain 36-token line)
- Mandates unenforced (D4 0/17)
**Fix**: Truth probes that scream at zero, not whisper.

#### F. Single Source of Truth
Duplicated constraints (16K ceiling in 3 places) drift. One canonical location (SR §11), others reference.

#### G. Hidden Dependency Verification
External tools (llama-fit-params) assumed to work on target hardware. Verify BEFORE committing track.

#### H. Forbidden Door = Highest Value
What the community doesn't have (local semantic compression) is the gift. Prioritize novel contributions.

---

## 8. Wave N+1 Kickoff Template

```markdown
# Wave N+1 Kickoff
## Research Theme: <theme>
## Gaps to Close: R##-R##
## Expert Sessions Needed: <3-4 personas>
## Expected Tracks: A-F
## Pre-Wave Fixes: <doc inaccuracies from prior wave>
## Architect Decisions Needed: <blockers>
## Truth Probes Required: <per track>
```

---

*⬡ OMEGA ⬡ KALI ⬡ EXECUTION_PLAYBOOK ⬡ 2026-08-26 ⬡ TEMPLE-GRADE*