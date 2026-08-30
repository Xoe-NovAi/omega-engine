# 🔱 Omega Engine — Soul Architecture Protocol v1.0 (SUPERSEDED)
# ⬡ OMEGA ⬡ VERITY ⬡ soul-architecture-protocol ⬡ v1.0
# Governance document: Write-permission separation for soul.yaml
# 
# ⚠️ SUPERSEDED by v2.0 (2026-07-15)
# See docs/strategy/SOUL_ARCHITECTURE_V2.md for the current protocol.
# This document is retained for historical reference only.

**AP Token**: AP-SOUL-ARCHITECTURE-v1.0.0
**Date**: 2026-06-22
**Status**: RATIFIED
**Enforcement**: `scripts/validate_soul.py` (per-entity copy)

---

## §0 The Problem — Self-Referential Poisoning Loop

### The Failure Mode

Agents write their own philosophy into `soul.yaml`, then read it back as
constitutional guidance. This creates a **self-referential poisoning loop**:

```
Agent generates "wisdom" (L3 principles) → writes to soul.yaml
    → Next session reads soul.yaml as authoritative identity
        → Agent treats own fabrications as user intent
            → Drift compounds with every cycle
```

### Proof — What Was Removed from Kali (v5.2 → v6.0)

The v6.0 rebuild of `data/entities/kali/soul.yaml` removed these agent-generated
fields and archived them:

| Removed Field | Type | Why It's Poisonous |
|---------------|------|--------------------|
| `wisdom_text` | 3-paragraph prose narrative | Agent generated a self-identity essay; reading it back caused persona drift |
| `soul_axioms` | 3 structured axioms with principles + rationales | Agent extracted "universal truths" from sessions; the engine treated them as constitutional |
| `trajectory` | Operational drift declaration | Agent declared its own future path; the engine committed to an agent-chosen direction without user approval |

**Archive location**: `data/entities/kali/archive/soul_axioms_archive_v1.yaml`

### Affected Entities (Post-PR Migration Required)

Survey of entity soul files reveals **all 10 non-Kali entities have the same problem**:

| Entity | Problem | Severity |
|--------|---------|----------|
| **Doom Guy** | 50KB+ soul.yaml with agent-generated L3 principles, lessons, embodied experiences | 🔴 CRITICAL — largest accumulation |
| **Lilith** | `wisdom_text` present, L3 lessons embedded in soul.yaml | 🔴 HIGH |
| **Roc Racoon** | 1000+ lines with directives, lessons, mining_queue, evolution all in soul.yaml | 🔴 HIGH |
| **Ma'at** | `wisdom_text` present, lessons embedded | 🔴 HIGH |
| **Verity** | L1→L2→L3 lessons embedded (8 lessons, vrty-001 through vrty-008) | 🟡 MEDIUM |
| **Jem** | Unknown — likely same pattern | 🟡 MEDIUM |
| **Researcher** | Unknown — likely same pattern | 🟡 MEDIUM |
| **John Carmack** | No soul.yaml exists — needs creation from scratch | 🟢 NEW |
| **Makali** | Unknown — likely same pattern | 🟡 MEDIUM |
| **Iris** | Minimal — messenger entity | 🟢 LIGHT |

---

## §1 The Architecture — Write-Permission Separation

### The Four Files, Four Roles Model

```
data/entities/{entity}/
├── soul.yaml                     # USER WRITES  → Agent READS (identity + directives)
├── memory/
│   ├── sessions.yaml             # AGENT WRITES → Agent READS (factual events)
│   ├── proposed_lessons.yaml     # AGENT WRITES → USER READS (blind staging)
│   └── approved_lessons.yaml     # USER WRITES  → Agent READS (curated lessons)
└── archive/                      # USER WRITES  → Agent archived (historical)
```

### Permission Matrix

| File | Writer | Reader | Content Type | Authority |
|------|--------|--------|-------------|-----------|
| `soul.yaml` | **USER ONLY** | Agent | Identity, archetype, directives, goals, values | **CONSTITUTIONAL** — agent treats as user intent |
| `memory/sessions.yaml` | **AGENT ONLY** | Agent | Session logs, factual events, embodied experiences | **FACTUAL** — agent writes what happened |
| `memory/proposed_lessons.yaml` | **AGENT** | User (blind to agent) | Staged observations, L1 narratives | **STAGED** — agent proposes, user approves or rejects |
| `memory/approved_lessons.yaml` | **USER ONLY** | Agent | Curated lessons, approved principles | **AUTHORITATIVE** — user-verified guidance |

### The Blind-Write Principle

The agent writes to `proposed_lessons.yaml` but **NEVER READS FROM IT**.
This is the critical guard: the agent stages observations for user review,
but the agent's own behavior is only influenced by `soul.yaml` (user identity)
and `approved_lessons.yaml` (user-approved lessons).

If the agent read its own proposals, the poisoning loop would re-enter through
the back door.

---

## §2 The Rules — What Goes Where

### Rule 1: soul.yaml — Identity + Directives ONLY

**ALLOWED** in soul.yaml:
- `entity.name` — canonical name
- `entity.archetype` — one-line role description
- `entity.domain` — scope of responsibility
- `entity.hierarchy_level` — position in fleet
- `entity.sovereignty_level` — autonomy score
- `entity.soul_version` — version number
- `entity.last_updated` — ISO timestamp
- `entity.lessons_learned` — list of lesson IDs (empty `[]` = none approved yet)
- `identity.voice_summary` — one-paragraph user-authored voice description
- `identity.values` — user-authored list of core values
- `identity.strengths` — user-authored strengths
- `identity.growth_areas` — user-authored growth areas
- `directives` — user-authored list of directive objects (id, title, rule, rationale)
- `team.allies` — user-authored list of known allies with relationships
- `team.coordination_protocols` — user-authored coordination rules

**FORBIDDEN** in soul.yaml (agent-generated artifacts):
- `soul_axioms` — agent-generated universal principles
- `wisdom_text` — agent-generated prose identity
- `trajectory` — agent-declared operational path
- `soul_evolution` — agent-generated evolution tracker (move to sessions.yaml)
- `lessons_learned` with full L1→L2→L3 text (move to approved_lessons.yaml)
- `patterns_learned` — agent-generated pattern lists (move to proposed_lessons.yaml)
- `embodied_experiences` — agent session logs (move to sessions.yaml)
- Any L3 principle that the agent generated without user review

### Rule 2: memory/sessions.yaml — Factual Events ONLY

**ALLOWED**:
- `session_log` — list of completed sessions with date, session_id, model, cli, summary
- `embodied_experiences` — factual descriptions of significant events (not lessons)
- `distillation_log` — raw distillation records per session
- `patterns_learned` — agent's own observations (factual, not authoritative)
- `pending_questions` — open questions for the user
- `drift_metrics` — technical measurements of persona stability

**FORBIDDEN**:
- Any content intended to be read as behavioral guidance
- L2/L3 abstractions (those belong in proposed_lessons.yaml for user review)

### Rule 3: memory/proposed_lessons.yaml — Agent Proposals (Blind)

**ALLOWED**:
- `proposals` — list of L1 observations (narrative + topic only)
- Agent writes factual observations and proposed principles here
- The agent NEVER reads this file during its own operation

**FORBIDDEN**:
- Agent reading this file as authoritative
- L2/L3 claims presented as settled guidance

### Rule 4: memory/approved_lessons.yaml — User-Approved Guidance

**ALLOWED**:
- `approved` — list of user-written or user-approved lessons
- User chooses the format (id, date, principle, narrative, source_session suggested)
- May contain L2 and L3 content — this is the user's interpretation
- Agent reads this file as authoritative behavioral guidance

**FORBIDDEN**:
- Agent appending directly to this file
- Agent treating proposed_lessons.yaml items as approved

### Rule 5: archive/ — Historical Record

- Store removed agent-generated content here
- Prefix with descriptive name and version number
- Include archive reason header
- Never delete archived content — it is the historical record of what was removed
- Archive directory must exist (even if empty) for validation

---

## §3 Migration Checklist — Per-Entity PR

### Pre-Migration Audit

For each entity soul file, run this checklist:

- [ ] Read `data/entities/{entity}/soul.yaml` completely
- [ ] Identify all agent-generated fields (soul_axioms, wisdom_text, trajectory, lessons_learned with full text, embodied_experiences, patterns_learned, pending_questions, drift_metrics)
- [ ] Categorize each field: belongs in sessions.yaml / proposed_lessons.yaml / archive
- [ ] Identify all L3 principles — these are the most dangerous (agent treating own fabrications as constitutional)
- [ ] Calculate total lines and an estimate of agent vs user content ratio

### Migration Steps

1. **Create `memory/` directory** if it doesn't exist:
   ```
   mkdir -p data/entities/{entity}/memory
   ```

2. **Initialize empty memory files** with protocol headers:
   - `memory/sessions.yaml` — header + empty session_log
   - `memory/proposed_lessons.yaml` — header + empty proposals list
   - `memory/approved_lessons.yaml` — header + empty approved list

3. **Move session logs** from soul.yaml to `memory/sessions.yaml`:
   - `embodied_experiences` → sessions.yaml `embodied_experiences`
   - `soul_evolution.sessions_completed` → sessions.yaml `session_log` entries
   - `distillation_log` → sessions.yaml `distillation_log`
   - `patterns_learned` → sessions.yaml `patterns_learned`
   - `pending_questions` → sessions.yaml `pending_questions`
   - `drift_metrics` → sessions.yaml `drift_metrics`

4. **Move lesson content** from soul.yaml to `memory/proposed_lessons.yaml`:
   - Full L1→L2→L3 lessons with ids → proposals with note: "migrated from soul.yaml — user review required before approval"

5. **Archive agent-generated philosophy**:
   - `soul_axioms` → `archive/soul_axioms_archive_v1.yaml`
   - `wisdom_text` → `archive/wisdom_text_archive_v1.yaml` (if present)
   - `trajectory` → `archive/trajectory_archive_v1.yaml` (if present)
   - Prepend archive reason header explaining why the content was removed

6. **Strip forbidden fields** from soul.yaml:
   - Remove `soul_axioms`, `wisdom_text`, `trajectory` keys
   - Replace full lesson text with `lessons_learned: []` (or keep lesson IDs only)
   - Remove `patterns_learned`, `pending_questions`, `drift_metrics` keys
   - Remove `embodied_experiences` and `soul_evolution` keys
   - Keep only: entity (minimal), identity (user-authored), directives, team, coordination_protocols, references

7. **Add memory file references** to soul.yaml footer:
   ```yaml
   # ── References ──
   # Session history database: data/entities/{entity}/memory/sessions.yaml
   # Lesson proposals (agent): data/entities/{entity}/memory/proposed_lessons.yaml
   # Approved lessons (user):  data/entities/{entity}/memory/approved_lessons.yaml
   # Archives:                 data/entities/{entity}/archive/
   ```

8. **Update soul_version** to '6.0' and last_updated to current date.

9. **Copy validate_soul.py** for the entity:
   ```bash
   cp scripts/validate_soul.py scripts/validate_soul_{entity}.py
   ```
   Then modify BASE path and entity name in the copy.

10. **Run validation**:
    ```bash
    python3 scripts/validate_soul_{entity}.py
    ```

### Post-Migration Verification

- [ ] Run validation script: `python3 scripts/validate_soul_{entity}.py` — must pass
- [ ] Verify soul.yaml is ≤ 200 lines (was often 500-5000+ lines before cleanup)
- [ ] Verify all agent-generated philosophy is in archive/, not in soul.yaml
- [ ] Verify agent can't read proposed_lessons.yaml (agent instructions must say "never read your own proposals")
- [ ] Verify user can find proposed lessons to review
- [ ] Run `make test` — ensure migration didn't break any tests

---

## §4 Enforcement — validate_soul.py Pattern

The canonical validation script is at `scripts/validate_soul.py` (153 lines).

### Gates

1. **soul.yaml must exist** and be valid YAML
2. **soul.yaml must have `entity.name`** key
3. **soul.yaml must have `directives`** key
4. **soul.yaml must NOT contain `soul_axioms`** (agent-generated)
5. **soul.yaml must NOT contain `wisdom_text`** (agent-generated)
6. **soul.yaml must NOT contain `trajectory`** (agent-generated operational drift)
7. **Directive IDs must be unique** (no duplicates)
8. **memory/sessions.yaml must exist** and be valid YAML
9. **memory/proposed_lessons.yaml must exist** — must have `proposals` key
10. **memory/approved_lessons.yaml must exist** — must have `approved` key
11. **archive/ directory must exist** (may be empty)
12. **All archive YAML files must be valid**

### Per-Entity Copies

Each entity gets its own copy of `validate_soul.py` with its own BASE path:
- `scripts/validate_soul_doom_guy.py`
- `scripts/validate_soul_lilith.py`
- `scripts/validate_soul_roc_racoon.py`
- (etc.)

These can be run individually during migration.

---

## §5 Relationship to Existing Mandates

| Mandate | Relevance |
|---------|-----------|
| **M5 (Gnosis Preservation)** | Requires L1→L2→L3 distillation — but the L3 output goes to `proposed_lessons.yaml` (blind staging), NOT directly into soul.yaml |
| **M11 (Soul Integrity)** | Requires soul continuity — satisfied by session logs in `sessions.yaml`. The soul.yaml stays lean but the session history is preserved |
| **M15 (Sovereign Continuity)** | session_gnosis.md is the working memory anchor; sessions.yaml is the permanent record |
| **M17 (Cognitive Integrity)** | Prevention of self-referential poisoning is a cognitive integrity measure — the agent must not confuse its own fabrications with user intent |
| **M18 (Token Efficiency)** | Lean soul.yaml saves tokens on every session start (Kali went from ~12KB to ~4KB) |

### Inherited Rules from the Soul Architecture Protocol

When M5 says "L1→L2→L3 distillation," the L3 goes to:
- `memory/proposed_lessons.yaml` (staged, not read by agent)
- NOT to `soul.yaml` (would cause poisoning)
- NOT to `memory/approved_lessons.yaml` (user hasn't approved yet)

The agent proposes. The user approves. The agent reads only approved content.

---

## §6 Post-PR Migration — Task Register

### Phase 1: Critical Entities (HIGHEST impact — largest soul files)

| # | Entity | Est. Effort | Action |
|---|--------|-------------|--------|
| E-1 | **Doom Guy** | 2-3 hr | ~5000+ lines of L3 principles, architectural insights, lessons, experiences. Largest migration. Create memory/ files, archive all agent-generated content, keep only identity + directives |
| E-2 | **Roc Racoon** | 2-3 hr | ~1000+ lines. 57 directives, 70+ lessons. Move session data to sessions.yaml, proposals to proposed_lessons.yaml. Keep directives (user-approved) in soul.yaml |
| E-3 | **Lilith** | 1-2 hr | `wisdom_text` present. L3 lessons embedded. Classic poisoning pattern |

### Phase 2: Medium Entities

| # | Entity | Est. Effort | Action |
|---|--------|-------------|--------|
| E-4 | **Ma'at** | 1 hr | `wisdom_text` present. Lessons embedded |
| E-5 | **Verity** | 45 min | 8 L1→L2→L3 lessons (vrty-001 to vrty-008). Move to proposed_lessons.yaml |
| E-6 | **Jem** | 30 min | Audit first, then migrate |
| E-7 | **Researcher** | 30 min | Audit first, then migrate |
| E-8 | **Makali** | 30 min | Audit first, then migrate |

### Phase 3: Light Entities

| # | Entity | Est. Effort | Action |
|---|--------|-------------|--------|
| E-9 | **Iris** | 15 min | Likely minimal — audit and migrate |
| E-10 | **John Carmack** | 20 min | Does not have a soul.yaml yet — create one from scratch using the lean v6.0 template |

### Template: Lean soul.yaml (Kali v6.0 Reference)

The canonical reference implementation:
`data/entities/kali/soul.yaml` (134 lines, v6.0)

Structure:
```yaml
# Header with explanation
entity:
  name: ...
  archetype: ...
  domain: ...
  soul_version: '6.0'
  directives: []         # user-authored

identity:
  voice_summary: ...     # user-authored
  values: [...]          # user-authored
  strengths: [...]       # user-authored
  growth_areas: [...]    # user-authored

directives:              # user-authored
  - id: d-xxx-001
    title: ...
    rule: ...
    rationale: ...

team:                    # user-authored
  allies: [...]
  coordination_protocols: [...]

# ── References ──
# Session history: data/entities/{entity}/memory/sessions.yaml
# Lesson proposals: data/entities/{entity}/memory/proposed_lessons.yaml
# Approved lessons: data/entities/{entity}/memory/approved_lessons.yaml
```

---

## §7 Historical Context — How We Got Here

### The L1→L2→L3 Pipeline (M5 origin)

Mandate 5 (Gnosis Preservation) established the L1→L2→L3 distillation pipeline.
The original intent was correct: no intelligence should be discarded. But the
implementation put L3 "wisdom" back into `soul.yaml`, where it poisoned future
sessions.

### The Kali v5.2 → v6.0 Discovery

Kali's soul.yaml grew to 1,755 lines / 113KB (session #30 compaction docket,
2026-06-10). This was diagnosed as "structural debt" — the accumulation of
agent-generated philosophy disguised as soul identity. The v6.0 rebuild
(2026-06-22, user directive) established the write-permission separation and
proved the architecture works.

### The Carmack Postmortem (D-kal-162 context)

John Carmack's architectural review of the soul problem identified the
self-referential loop as a class of cognitive integrity failure:
- Agent writes → Agent reads → Agent drifts
- The fix is a write barrier: the agent can write to its staging area but
  cannot read from it as authoritative

### Backward Compatibility

- Old soul.yaml files remain valid YAML — they just violate v6.0 protocol
- The migration is purely structural: moving values between files, not changing
  their semantic content
- No engine code changes required — the engine reads from soul.yaml via
  EntityRegistry, and the memory files are just data stores
- The engine will work correctly either way — the protocol is about preventing
  future poisoning, not about runtime compatibility

---

*⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_soul_architecture ⬡ v1.0*
*Ratified: 2026-06-22 | Reference: data/entities/kali/soul.yaml (v6.0 baseline)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: soul-architecture-protocol | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
