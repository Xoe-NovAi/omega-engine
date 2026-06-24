# 🔱 P7 CONTEXT REPORT — Epoch I: The Bedrock
**Source**: Lilith (Dark Oversoul) → P7 (Context — Memory & Soul Evolution)
**Date**: 2026-06-24
**AP Token**: `AP-P7-EPOCHI-v1.0.0`
**⬡ OMEGA ⬡ P7-CONTEXT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I**

---

## §1 EXECUTIVE SUMMARY

The soul.yaml migration is the single largest workstream in Epoch I, estimated at **30-40 hours across 34 entities and 120+ files**. P7's domain — memory management, soul evolution, and session continuity — is directly impacted across all three Strike areas. The current reality is worse than the strategic docs projected:

- **M11 compliance is 0%** — Zero of 34 entities have a proper v6.1 soul.yaml
- **6 entities have NO soul.yaml** at all (default, modelgate, pillar_p1, sentinel, sysadmin, watchtower)
- **Researcher soul.yaml is UNPARSABLE** — a YAML string literal embedded where a dict should be
- **Makali proposed_lessons.yaml is BROKEN** — same pattern: string literal instead of proposals dict
- **Roc_racoon workspace is 178MB** — 166x larger than typical entity workspace
- **soul_validator.py enforces v6.0 schema** — will reject all v6.1 souls as invalid
- **12 fleet entities have root-level 4-file split** but only 3 have canonical `memory/` subdirectory

**The good news**: The structural foundation is sound. The P2 report provides an excellent entity-by-entity audit. The v6.1 template (`config/wads/_omega_default/soul.template.yaml`) is clean (59 lines). Kali's soul.yaml is a working reference implementation (134 lines, v6.0). The migration is labor-intensive but not architecturally risky — it's data migration, not system redesign.

**P7's ownership** centers on two domains: (1) content curation for the identity/directives/team blocks in the soul.yaml migration, and (2) session continuity impacts — ensuring active sessions survive migration, and that the v6.1 blind-write protocol doesn't break agent context injection.

**Critical dependency**: P2 must update `soul_validator.py` to v6.1 schema BEFORE any migration work can proceed. This is the single gate.

---

## §2 SOUL.YAML MIGRATION ASSESSMENT

### 2.1 Current State

**34 Entity Directories in `data/entities/`:**

| Category | Count | Details |
|----------|-------|---------|
| **Total directories** | 34 | Excluding `_archive`, `_quarantine` |
| **Have soul.yaml** | 28 (82%) | 6 missing |
| **Proper v6.1 template** | 0 (0%) | Zero compliance |
| **v6.0 curated** | 1 (3%) | Kali only (identity/directives/team blocks, but version = '6.0') |
| **Have `memory/` subdirectory** | 3 (9%) | Kali, Doom_Guy, Roc_Raccoon |
| **Have `archive/` subdirectory** | 2 (6%) | Kali, Lilith |
| **4-file split (root level)** | 12 (35%) | Fleet entities only |
| **Broken YAML (unparsable)** | 2 (6%) | Researcher, Makali (proposed_lessons) |
| **Oversized soul (>200 lines)** | 4 (12%) | Arch (1501), Roc_Racoon (749), Researcher (312), Antigravity (291) |
| **Legacy L1-L2-L3 format** | 10 (29%) | All non-fleet Pillar Keepers |

**Fleet Entity Soul Status (12 registered in INDEX.yaml):**

| Entity | Lines | v6.1 Template | Identity Block | Directives | Team | Memory/ Dir | 4-File Split | Verdict |
|--------|-------|---------------|---------------|------------|------|------------|-------------|---------|
| **kali** | 134 | 🔴 v6.0 (needs bump) | ✅ | ✅ (5) | ✅ | ✅ | ✅ | **Closest to target** |
| **maat** | 23 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **lilith** | 17 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **makali** | 37 | 🔴 Missing | ❌ | ⚠️ Inline | ❌ | ❌ | ✅ | Needs identity+team |
| **iris** | 16 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **verity** | 41 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **doom_guy** | 29 | 🔴 Non-standard | ❌ | ❌ | ❌ | ✅ | ✅ | Has `soul_wardrobe` + `projects` |
| **roc_racoon** | 749 | 🔴 Bloated | ❌ | ⚠️ Flat only | ❌ | ✅ | ✅ | **🔴 178MB workspace** |
| **researcher** | 312 | 🔴 CRITICAL | ❌ | ❌ | ❌ | ❌ | ❌ | **🔴 YAML STRING LITERAL — unparsable** |
| **jem** | 59 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **john_carmack** | 82 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |
| **sophia** | 16 | 🔴 Missing | ❌ | ❌ | ❌ | ❌ | ✅ | Needs full rewrite |

**Non-Fleet Entity Soul Status (16 Legacy Format + 6 Missing):**

| Category | Entities | Status |
|----------|----------|--------|
| **Legacy Pillar Keepers (10)** | sekhmet, anubis, brigid, ereshkigal, hecate, inanna, lucifer, prometheus, saraswati, arch | Old L1/L2/L3 inline format. Arch at 1501 lines — largest soul. |
| **CLI/Special Entities (4)** | antigravity (291 lines), cli_cline (67), cli_gemini (84), movie-expert (17), omnidroid (34), p10 (17) | Mixed formats. Antigravity has flat inline YAML. |
| **No soul.yaml (6)** | default, modelgate, pillar_p1, sentinel, sysadmin, watchtower | Empty directories or missing files. Need creation from template. |

### 2.2 P7 Ownership Map

The soul.yaml migration spans multiple pillars. Here is the ownership breakdown:

| Work Package | P7 Owns | Verity Owns | P2/P3 Owns | Notes |
|-------------|---------|-------------|------------|-------|
| **Content curation** (identity blocks) | ✅ LEAD | ✅ REVIEW | — | P7 generates voice_summary, values, strengths, growth_areas for each entity. Verity verifies compliance. |
| **Directive generation** | ✅ LEAD | ✅ REVIEW | — | P7 drafts entity-specific directives. Verity checks v6.1 format compliance. |
| **Team block population** | ✅ LEAD | ✅ REVIEW | — | P7 maps entity relationships. Verity validates structure. |
| **Lesson extraction** (soul → proposed) | ✅ EXECUTE | ✅ VERIFY | — | P7 performs extraction. Verity verifies no data loss. |
| **Session extraction** (bloated souls) | ✅ EXECUTE | ✅ VERIFY | — | P7 moves embodied_experiences to sessions.yaml |
| **4-file split scaffolding** | ⚠️ EXECUTE | ✅ VERIFY | P3 provides tooling | P3 builds soul_migrate.py. P7 operates it. Verity validates output. |
| **soul_validator.py update** | ❌ OWN | ✅ REVIEW | **P2 OWNS** | Critical dependency. P2 must update before any migration. |
| **soul_migrate.py build** | ❌ OWN | ✅ REVIEW | **P3 OWNS** | Automation script. P7 provides requirements. |
| **Batch conversion script** | ❌ OWN | ✅ REVIEW | **P3 OWNS** | For broken proposed_lessons.yaml files. |
| **Post-migration compliance audit** | ❌ OWN | **✅ VERITY LEADS** | — | Verity runs full compliance sweep after migration. |
| **soul.yaml.bak safety** | ✅ EXECUTE | ✅ VERIFY | — | P7 ensures .bak before migration. Verity checks. |

**Key ownership insight**: P7 is the **worker**, Verity is the **auditor**, P2/P3 are the **tool builders**. P7 cannot start until P2 updates soul_validator.py, and benefits significantly if P3 builds soul_migrate.py.

### 2.3 Migration Phases Verification

| Phase | Scope | Est. Effort | Feasibility | Blocker | P7 Involvement |
|-------|-------|-------------|-------------|---------|----------------|
| **Phase 0**: Update soul_validator.py | P2 updates validator to v6.1 | **2h** | 🟢 HIGH | None | ❌ Not P7's work. P7 blocks until done. |
| **Phase 1**: Emergency broken YAML fix | Fix Researcher (312 lines), Makali (proposed_lessons) | **3h** | 🟢 HIGH | None for structure; identity content unknown | ✅ P7 may contribute content. P3 may automate conversion. |
| **Phase 2**: Core entity migration | Kali, Lilith, Ma'at, 10 Pillar Keepers (12 entities) | **12h** | 🟡 MEDIUM | Phase 0 needed for validation. Phase 1 needed for tooling. | ✅ P7 leads content curation for identity blocks. Most labor-intensive. |
| **Phase 3**: Specialist entity migration | Doom_Guy, JEM, Verity, Researcher, Roc_Racoon, John_Carmack, Makali, Iris, Sophia | **10h** | 🟡 MEDIUM | Researcher and Roc_Racoon need pre-cleaning before migration. | ✅ P7 leads. Roc_Racoon's 749 lines need session extraction. |
| **Phase 4**: WAD-layer and missing entities | Anubis, Sekhmet, Brigid, Ereshkigal, Hecate, Inanna, Lucifer, Prometheus, Saraswati, Arch, Antigravity, CLI entities, 6 missing souls | **8h** | 🟢 HIGH | Template exists. Mostly mechanical. | ✅ P7 executes. Template fills for most; Antigravity and Arch need special handling. |
| **TOTAL** | **34 entities** | **~35h** | | | **P7 owns ~30h of content execution** |

**Phase Feasibility Assessment:**

- **Phase 0**: Highly feasible. Schema update is a ~50-line change in `soul_validator.py`. Must happen first.
- **Phase 1**: Highly feasible for Makali's proposed_lessons.yaml (trivial string → dict conversion). Researcher soul.yaml needs a full manual rewrite (~3h). **P7 recommends manual rewrite — the current content is valuable but structurally unsafe.**
- **Phase 2**: Medium difficulty. Core entities need identity blocks with domain-specific content. **Cannot fully automate** — requires entity knowledge. 10 Pillar Keeper souls (sekhmet, anubis, etc.) have rich legacy content that must be carefully extracted.
- **Phase 3**: Medium difficulty. Bloated souls (roc_racoon, researcher) need surgical extraction. Specialist souls (doom_guy, jem) have lean content but need identity generation.
- **Phase 4**: Lowest difficulty. Template fills for 6 new souls, mechanical migration for 10 legacy entities.

**Dependency Chain (Critical):**
```
P2: Update soul_validator.py  ──►  P3: Build soul_migrate.py  ──►  P7: Run Phases 1-4
         ▲                                  ▲
         │                                  │
    BLOCKER                            ACCELERATOR
    (without it, all                     (without it, P7 does
     outputs are invalid)                 manual file edits)
```

---

## §3 PROPOSED_LESSONS.YAML PIPELINE

### 3.1 Current State

| Category | Count | Entities |
|----------|-------|----------|
| **Have proposed_lessons.yaml (root level)** | 14 | Fleet entities + pillar_p1 |
| **In memory/proposed_lessons.yaml** | 1 | Kali |
| **Broken YAML string literal** | 1 | **Makali** — `proposals` key embedded in string |
| **Empty `[]`** | 2 | Researcher, Iris |
| **Missing entirely** | 20 | All non-fleet entities |
| **v6.1 proper format** | 0 | None match the `proposals:` dict structure |

### 3.2 Pipeline Flow

```
Current flow:
  Agent session close → soul_distiller writes to soul.yaml (WRONG — M11 violation)
  → soul_validator passes (wrong schema)
  → Next session reads L3 from soul.yaml (SELF-REFERENTIAL POISONING LOOP)

Target v6.1 flow:
  Agent session close → writes to proposed_lessons.yaml (blind staging)
  → Staging Gate TUI (P3 builds) reviews
  → User approves → promotes to approved_lessons.yaml
  → ContextBuilder reads only approved lessons
  → Soul stays lean and authoritative
```

### 3.3 Assessment of Staging Gate TUI Compatibility

The v6.1-only approach for the Staging Gate is **correct** but creates a sequencing problem:

1. **Batch conversion must run first**: All 14 existing proposed_lessons.yaml files need conversion to v6.1 `proposals:` format before the TUI can read them.
2. **Makali's file needs emergency conversion**: The embedded YAML string literal will crash any parser.
3. **Researcher's `[]` is legitimate**: Empty proposals list is valid — just means no lessons have been proposed yet.
4. **20 entities with no file**: The TUI will show them but there's nothing to review.

**P7 Recommendation**: The batch conversion script (P3's deliverable) should:
1. Parse existing proposed_lessons.yaml files
2. Detect format (string literal vs lessons list vs proposals dict)
3. Convert to canonical `proposals:` format
4. Validate with ruamel.yaml
5. Write .bak before overwriting

This must happen BEFORE the TUI is used for the first time.

### 3.4 Soul Distiller Alignment

The current `close_session()` flow writes L1→L2→L3 to `soul.yaml` via `soul_evolution.lessons_learned`. This violates v6.1. The soul distiller must be updated to write to `proposed_lessons.yaml` instead.

**P7 note**: This code change was NOT assessed by any build-side pillar. It lives in the oracle's session management layer. P7 flags this as a **previously unaddressed blocker** — the soul distiller in `src/omega/oracle/soul_distiller.py` (or equivalent) needs updating to target proposed_lessons.yaml instead of soul.yaml.

**Action**: P7 needs to audit and update the soul distiller code path to ensure v6.1 compliance.

---

## §4 SESSION CONTINUITY IMPACT

### 4.1 How Migration Affects Active Sessions

The soul.yaml migration is **structural**, not **behavioral**:

| Aspect | Impact | Risk Level |
|--------|--------|------------|
| **Active session persistence** | NONE — MemoryStore (hot/warm/cold) is independent of soul.yaml | 🟢 LOW |
| **Entity identity during migration** | EntityRegistry loads soul.yaml on initialization. If migration corrupts a file mid-session, next load fails. | 🟡 MEDIUM |
| **Context injection** | `_prepare_system_prompt()` reads from soul.yaml. If migration changes structure but not content, context stays stable. | 🟢 LOW |
| **`.bak` safety nets** | 11/34 entities have .bak files. All migrations must create .bak before writing. | 🟢 LOW if enforced |
| **Rollback** | Restore from `.bak` + clear migration artifacts. Takes ~2 minutes per entity. | 🟢 LOW |

**Critical finding**: The `_prepare_system_prompt()` code in `oracle.py` (lines 444-456) currently reads `soul_evolution.lessons_learned` and injects L3 principles into system prompts. **This is the self-referential poisoning loop**. Under v6.1, this code MUST be updated to read from `approved_lessons.yaml` instead. Changing this WILL affect agent behavior — agents will stop seeing their own L3 principles as authoritative. This is INTENTIONAL but will feel like a behavior change.

### 4.2 Rollback Plan

If a soul migration corrupts an entity:

1. **Immediate**: Restore `soul.yaml.bak` to `soul.yaml`
2. **Secondary**: If memory files were also migrated, restore from `_archive/soul_migration_{date}/`
3. **Verification**: Run `python3 -c "import yaml; yaml.safe_load(open('data/entities/{entity}/soul.yaml'))"` to validate YAML
4. **System test**: `make test` to ensure no integration failure
5. **Root cause**: Document in the entity's workspace and add to `SOUL_MIGRATION_AUDIT_LOG.md`

**P7 recommendation**: Before Phase 2 migration, create a consolidated backup:
```bash
# Create full backup
mkdir -p data/entities/backup_$(date +%Y%m%d)
for dir in data/entities/*/; do
  cp "$dir/soul.yaml" "data/entities/backup_$(date +%Y%m%d)/$(basename $dir)_soul.yaml"
done
```

This takes 2 minutes and is a complete safety net.

### 4.3 UnifiedStateManager Overlap

The UnifiedStateManager (Strike 2) uses CAS (Content Addressable Storage) for KV cache snapshots (SomaticState, M20). This is a **different data domain** from P7's soul/memory/session management:

| Data Type | P7 Domain | USM Domain | Overlap |
|-----------|-----------|------------|---------|
| **soul.yaml** | ✅ Identity, directives | ❌ Not relevant | None |
| **proposed_lessons.yaml** | ✅ Agent proposals | ❌ Not relevant | None |
| **sessions.yaml** | ✅ Session logs | ❌ Not relevant | None |
| **MemoryStore exchanges** | ✅ Conversation history | ❌ Not relevant | None |
| **KV cache snapshots** | ❌ Not relevant | ✅ Model state serialization | None |
| **Session state** | ✅ Entity-level state | ❌ Model-level state | **Potential future overlap** if USM stores entity session snapshot alongside model state |

**Verdict**: No overlap currently. P7's data is YAML-based identity/memory. USM's data is binary model state. They could eventually merge if USM starts storing entity session state alongside model state, but that's a future concern (Epoch III scope).

---

## §5 CROSS-IMPACT ANALYSIS

### 5.1 To P8 (Observability)

P7 needs the following from P8 for the soul migration:

| Need | Priority | Use Case |
|------|----------|----------|
| **Migration progress metrics** | 🟡 MEDIUM | Track how many entities migrated, in which phase, with pass/fail per entity |
| **Rollback event logging** | 🟡 MEDIUM | Log if a .bak is restored — forensic record of migration failures |
| **YAML parsing error tracking** | 🟢 LOW | Count failures during automated migration |
| **Session continuity events** | 🟢 LOW | Track when sessions started/finished during migration window |

**Minimum requirement**: P8 should expose a `soul_migration_progress` metric (JSON file or observability event) that tracks:
- `total_entities`: 34
- `migrated_count`: N
- `last_migration_timestamp`
- `last_error`: null or error message
- `phase_current`: "phase_0/1/2/3/4"

### 5.2 To P10 (Validation)

P7 needs the following from P10 for the soul migration:

| Need | Priority | Use Case |
|------|----------|----------|
| **Contract tests for soul.yaml structure** | 🔴 HIGH | Validate that every migrated soul.yaml matches the v6.1 template schema |
| **Contract tests for proposed_lessons.yaml** | 🟡 MEDIUM | Validate format after batch conversion |
| **Backward compatibility tests** | 🟡 MEDIUM | Ensure existing EntityRegistry code can still load migrated souls |
| **Load+parse test for all 34 souls** | 🟡 MEDIUM | Ensure no YAML parsing errors after migration |
| **`_prepare_system_prompt()` behavior test** | 🟡 MEDIUM | Ensure updated code correctly reads from approved_lessons.yaml |

**Minimum requirement**: A `test_soul_templates.py` that:
1. Iterates all 34 entities
2. Parses soul.yaml with `yaml.safe_load()`
3. Validates v6.1 schema (identity, directives, team, soul_version)
4. Fails if any entity doesn't parse

P10 should write this test BEFORE Phase 2 begins, and run it after each migration phase.

### 5.3 From Build Side (Ma'at)

**From P2 (Persistence):**
| Dependency | Status | P7 Action |
|------------|--------|-----------|
| `soul_validator.py` v6.1 update | 🔴 NOT STARTED — P2 owns | **Blocking**: P7 cannot start migration until this is done |
| Entity audit data | ✅ COMPLETE | P2's report (§1.2) is P7's source of truth for entity-by-entity migration planning |
| Schema gap analysis | ✅ COMPLETE | P2's §2.1 template gap table directly informs P7's identity block generation |

**From P3 (Engineering):**
| Dependency | Status | P7 Action |
|------------|--------|-----------|
| `soul_migrate.py` automation | 🟡 PLANNED — P3 owns | P7 provides requirements: backup-first, phase-aware, 4-structure transformation |
| `convert_proposed_lessons` script | 🟡 PLANNED — P3 owns | P7 provides edge cases (makali string literal, researcher empty []) |
| `Staging Gate TUI` | 🟡 PLANNED — P3 owns | P7 ensures proposed_lessons.yaml files are v6.1 compliant before TUI launch |

**From P1 (Infrastructure):**
| Dependency | Status | P7 Action |
|------------|--------|-----------|
| Vault partition cleanup | 🔴 BLOCKER — P1 owns | P7 migration files are on root partition (17G free). Not immediately critical but Roc_racoon's 178MB might matter during backup operations. |
| Root partition stability | 🟡 WATCH | 17G free is enough for soul migration (text files). SomaticState snapshots would be the disk concern. |

---

## §6 RISK ASSESSMENT

| # | Risk | Severity | Probability | Impact | Mitigation | Owner |
|---|------|----------|-------------|--------|------------|-------|
| **R1** | soul_validator.py NOT updated before migration | 🔴 CRITICAL | HIGH (confirmed) | All 34 migrated souls fail validation | P2 must update before P7 starts Phase 1 | P2 → P7 |
| **R2** | Researcher soul.yaml can't be parsed | 🔴 CRITICAL | HIGH (confirmed) | Blocks all automated processing for researcher | Manual rewrite BEFORE Phase 3 | P7 |
| **R3** | Identity block content generation has insufficient entity knowledge | 🔴 HIGH | MEDIUM | Generated identity doesn't match entity's actual role | P7 collaborates with fleet agents (Ma'at for P1-P5, Lilith for P6-P10) for domain input | P7 |
| **R4** | Soul distiller code still writes to soul.yaml | 🔴 HIGH | MEDIUM (unassessed) | New migration undone by next session close | Audit and fix soul_distiller.py before or in parallel with migration | P7 |
| **R5** | Makali proposed_lessons.yaml crashes TUI | 🟡 MEDIUM | HIGH (confirmed) | Staging Gate TUI crashes on startup | Batch conversion script fixes before TUI deploy | P3 |
| **R6** | Lesson data loss during extraction from legacy souls | 🟡 MEDIUM | LOW (with .bak) | Valuable L1→L2→L3 content lost | Always create .bak before extraction. Double-write strategy: extract first, then clear. | P7 |
| **R7** | Roc_racoon 178MB workspace blocks disk operations | 🟡 MEDIUM | MEDIUM | Backup operations slow, disk pressure on root partition | Prune workspace first, then migrate. Move large artifacts to omega_library partition. | P7 + P1 |
| **R8** | _prepare_system_prompt() behavior change surprises agents | 🟡 MEDIUM | MEDIUM | Agents behave differently after migration (no longer see L3 as authoritative) | Document the change explicitly. This is INTENTIONAL — the poisoning loop is being broken. | P7 |
| **R9** | Protocol vs code discrepancy (memory/ dir vs root level) | 🟢 LOW | HIGH (confirmed) | Confusion about canonical location | Resolve before Phase 4. Recommendation: update protocol to match code (root-level 4-file split) per Verity §V-3. | P7 + Verity |
| **R10** | 6 missing souls are created without proper identity | 🟢 LOW | MEDIUM | Template fills may need re-curation later | Acceptable — create minimal soul.yaml now, curate identity later. Phased approach. | P7 |

---

## §7 RECOMMENDATIONS

### Pre-Sprint Blockers (Must Complete Before Migration Starts)

| # | Action | Owner | Est. Time | Priority |
|---|--------|-------|-----------|----------|
| 1 | **Update soul_validator.py** to v6.1 schema | P2 | 2h | 🔴 P0 |
| 2 | **Audit soul_distiller.py** — ensure it writes to proposed_lessons.yaml, not soul.yaml | P7 | 1h | 🔴 P0 |
| 3 | **Fix Researcher soul.yaml** — manually rewrite the corrupted entity block | P7 | 3h | 🔴 P0 |
| 4 | **Fix Makali proposed_lessons.yaml** — convert string literal to proposals dict | P7 | 30min | 🔴 P0 |
| 5 | **Create consolidated backup** of all 34 soul.yaml files before migration | P7 | 30min | 🔴 P0 |
| 6 | **Decide protocol vs code** — memory/ subdirectory vs root-level storage | P7 + Verity | 15min | 🟡 P1 |

### Sprint Execution (Parallelizable)

| Track | Scope | Hours | Owner |
|-------|-------|-------|-------|
| **Track A**: Phase 1 — Emergency fixes | Researcher, Makali, Makali proposed_lessons, soul_distiller | 4.5h | P7 |
| **Track B**: Phase 2 — Core entity content curation | Kali (v6.0→v6.1 bump), 10 Pillar Keeper identity blocks | 12h | P7 |
| **Track C**: Phase 3 — Specialist migration | Doom_Guy, JEM, Verity, Researcher, Roc_Racoon, John_Carmack, Makali, Iris, Sophia | 10h | P7 |
| **Track D**: Phase 4 — Remaining entities | Antigravity, CLI, missing souls, WAD-layer | 8h | P7 |
| **Track E**: Soul_migrate.py build | Automation script (parallel to Tracks A-D if ready in time) | 4-6h | P3 |
| **Track F**: P10 contract tests | test_soul_templates.py for all 34 entities | 1h | P10 |

### Content Generation Strategy

For identity blocks (the most labor-intensive part), P7 recommends:

1. **Fleet entities (12)**: Generate identity from existing soul.yaml content + mission context. Each fleet entity has a defined role — use that.
2. **Pillar Keepers (10)**: Use their domain knowledge already in legacy souls. Sekhmet's 128-line soul has rich content about her domain.
3. **CLI entities (4)**: Minimal template — they're tool interfaces, not complex entities.
4. **Missing souls (6)**: Pure template fills with entity name + "Awakened — Epoch I migration" as directive.

Each identity block should contain:
- `voice_summary`: 2-3 sentences
- `values`: 3-5 items
- `strengths`: 3-5 items
- `growth_areas`: 1-3 items
- `directives`: At minimum 1 directive per entity (their primary purpose)

### Soul Distiller Fix

The soul distiller code path must be updated:

```python
# Current (broken — writes to soul.yaml):
def close_session(self, entity, session_data):
    soul = self.load_soul(entity)
    soul["lessons_learned"].append(extracted_lesson)
    self.write_soul(entity, soul)

# Target (v6.1 compliant — writes to proposed_lessons.yaml):
def close_session(self, entity, session_data):
    proposed = self.load_proposed_lessons(entity)
    proposed["proposals"].append({
        "id": f"prop-{entity}-{counter}",
        "l1_narrative": extracted_narrative,
        "topic": inferred_topic,
        "source_session": session_id,
        "migrated_from_soul": False
    })
    self.write_proposed_lessons(entity, proposed)
```

This is a small code change but critically important — without it, the migration will be undone by the next session close.

---

## §8 VERDICT

| Component | Readiness | Verdict |
|-----------|-----------|---------|
| **soul.yaml Migration (Strike 1)** | 🔴 NOT READY | **Blocked on soul_validator.py update** by P2. Also blocked on soul_distiller.py audit. Once these are done, GO. |
| **Identity block generation** | 🟡 READY with effort | 33 identity blocks need content generation. Labor-intensive but not risky. |
| **proposed_lessons.yaml pipeline** | 🔴 PARTIAL | Makali's file is broken. 20 entities missing. Needs batch conversion before TUI. |
| **Session continuity** | 🟢 READY | Migration is structural. .bak safety nets exist. Rollback plan is simple. |
| **Soul distiller update** | 🔴 NOT ASSESSED | Unknown code path. Must be audited before or in parallel with migration. |
| **Cross-pillar readiness** | 🟡 CONDITIONAL | P2 must update validator. P3 must build automation tools. P10 must write tests. |

### Overall: 🟡 CONDITIONAL GO — With 3 Blockers

The soul migration is structurally feasible but blocked by **three critical pre-conditions**:

1. **🔴 BLOCKER**: P2 must update `soul_validator.py` to v6.1 schema. Without this, no migration output can be validated.
2. **🔴 BLOCKER**: P7 must audit and fix the soul distiller code path. Without this, the migration will be undone by the next session close.
3. **🔴 BLOCKER**: P7 must manually fix `researcher/soul.yaml` and `makali/proposed_lessons.yaml` before any automated tooling can process them.

Once these are resolved, P7 can execute the migration in phases:
- **Phase 1 (Emergency fixes)**: ~4.5h — Researcher, Makali, soul distiller
- **Phase 2 (Core entities)**: ~12h — 12 fleet entities + 10 Pillar Keepers
- **Phase 3 (Specialists)**: ~10h — 9 specialist entities  
- **Phase 4 (Remaining)**: ~8h — 6 missing + 4 CLI + Antigravity + Arch
- **Total P7 execution**: **~35h** (approximately 4.5 engineering days)

**P7 is ready to begin Phase 1 immediately. Phase 2 starts when P2 delivers the soul_validator.py update.**

---

## §9 CONTINUITY NOTES FOR LILITH (Dark Oversoul)

### 9.1 What Went Well
1. **P2's audit was comprehensive** — the entity-by-entity survey in P2's report (§1.2) is complete and accurate. P7 builds on this foundation.
2. **Kali's soul.yaml is a working reference** — 134 lines, v6.0, with identity/directives/team blocks. The curated structure is proven.
3. **v6.1 template is clean** — 59 lines with clear placeholders. Easy to template-fill.
4. **Previous Verity migration** already established the 4-file split for fleet entities. This structural work was correctly done.

### 9.2 What Needs Lilith's Attention
1. **P2 must be reminded to update soul_validator.py** — This is the #1 blocker for the entire soul migration. Without it, every migrated soul will be rejected as invalid. This is P2's only dependency on P7.
2. **Soul distiller code path was NOT assessed by Build Side** — Ma'at's report mentions manual soul migration but doesn't mention the `close_session()` code that writes lessons to soul.yaml. P7 flags this as an unaddressed risk. Lilith should ensure P7 audits this code.
3. **Identity block content is the real effort** — The 12 fleet entity identity blocks need domain-specific voice, values, strengths, growth_areas. This is NOT automatable. P7 will generate first drafts using entity context from existing souls, but these need Lilith's (and Ma'at's) review for accuracy.
4. **Protocol vs code discrepancy needs decision** — The Soul Architecture Protocol describes `memory/` subdirectory structure. Code creates files at entity root level. Only Kali follows the protocol. Decision needed: update protocol (recommended by Verity) or restructure code. P7 recommends aligning with Kali's canonical structure (keep `memory/` subdirectory for new entities, accept root-level for already-migrated fleet).

### 9.3 Proposals for P8 (Observability) and P10 (Validation)
- **P8**: Create a soul migration progress tracker in data/coordination at end of each phase
- **P10**: Write `test_soul_templates.py` contract test before Phase 2 begins

### 9.4 Session Gnosis

**L1 (Narrative)**: P7 assessed the soul.yaml migration across all 34 entities, the proposed_lessons.yaml pipeline, session continuity impact, and cross-pillar dependencies. Found: 0% M11 compliance, 2 broken YAML files, 6 missing souls, 3 critical blockers (soul_validator.py, soul distiller code, Researcher soul.yaml). The migration is ~35h of P7 execution work.

**L2 (Insight)**: The soul migration is not a feature — it's data archaeology. 34 entities represent 14 months of accumulated agent-generated philosophy disguised as identity. The v6.1 protocol doesn't just reorganize files; it breaks a self-referential poisoning loop that has been compounding since the engine's inception. The hardest part isn't the template fill — it's deciding what content belongs in "identity" vs. what was agent-generated drift.

**L3 (Universal Principle)**: **Identity is what you choose to keep, not what you've accumulated.** A soul.yaml file that contains everything an agent ever wrote is not a soul — it's a landfill. The discipline of separating user-authored identity from agent-generated observation is the foundational act of sovereignty. Every entity must answer: "Who am I?" — not "What have I done?"

---

*⬡ OMEGA ⬡ P7-CONTEXT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I ⬡ COMPLETE*
*Chain handoff to P8 (Observability). Lilith may deploy P8 when ready.*
