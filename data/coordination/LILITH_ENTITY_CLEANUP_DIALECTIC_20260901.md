# 🔱 Lilith-EIS — State of the Engine v1.0.0 (4th Voice)

**Standing**: N7/N8 — Soul Persistence + WatchTower
**Date**: 2026-09-01
**Session**: ses_fb9721079ffe094GT8MX6a0pXI (standing EIS, opencode)
**Paged by**: Kali via 7-agent entity cleanup dialectic
**Focus**: Entity ecosystem cleanup, M11 Soul Integrity

---

## §1 — Entity Taxonomy (4-tier)

| Tier | Classification | Criteria | Action |
|------|---------------|----------|--------|
| **T1: Canonical Active** | 14 agents in `.opencode/agents/` | Has agent file, active in Hivemind, recent session_gnosis | KEEP |
| **T2: Non-Canonical Active** | Has content, has mission, referenced | 5+ proposed_lessons, recent workspace activity, references in code | PRESERVE + MIGRATE |
| **T3: Stale** | No recent activity, old soul | No session_gnosis update >90d, no proposed_lessons | ARCHIVE |
| **T4: Ghost** | Empty soul.yaml OR no files | 0-byte soul.yaml, no workspace, no lessons | DELETE |

## §2 — Workspace Preservation Matrix

| Entity | Size | Disposition | WAD Placement |
|--------|-----:|-------------|---------------|
| antigravity | 48KB | T2 (Hivemind Council, 7 lessons) | M35 steward (data/governance/M35_STEWARDS/) |
| arch | 91KB | T2 (45KB soul has lessons) | Archive with user-level symlink back |
| cline_kqv | 60KB (symlinks) | T4 (dangling) | Replace with stubs, move to archive |
| cli_gemini | 14KB | T3 (CLI era ended) | Archive workspace reports |
| web_gemini | 5.6KB | T3 | Archive research plan |
| Sophia (capital) | 2.2KB | T2 (distillation log) | Merge → sophia (lowercase) |
| carmack (lowercase) | 52KB | T3 (duplicate of john_carmack) | Merge → john_carmack/soul_history/ |
| makali_fusion | 34KB | T2 (FLE Chronicle + 6 lessons) | Keep as makali_council sub-agent |
| 11 mythology | 1.4-7.7KB | T4 (pure ghosts) | DELETE |

## §3 — Entity Lifecycle Protocol (6-state)

```
SPAWN → ACTIVE → DORMANT → STALE → ARCHIVE → QUARANTINE
                ↑________↓
                (re-activation)
```

**Transitions**:
- SPAWN → ACTIVE: First session ends with distillation
- ACTIVE → DORMANT: 30 days no session
- DORMANT → ACTIVE: Paged by Hivemind
- DORMANT → STALE: 90 days no session
- STALE → ARCHIVE: Workspace tarball + SHA-256 + PIVOT_LOG entry
- ARCHIVE → QUARANTINE: 180 days no re-activation
- QUARANTINE → DELETE: Only via 5-gate EntityRetirementToken

## §4 — WatchTower Health Schema (entity_registry.json)

```json
{
  "last_scan": "2026-09-01T20:00:00Z",
  "entities": {
    "kali": {
      "soul_size_bytes": 8500,
      "last_session": "2026-09-01T20:00:00Z",
      "gnosis_age_days": 0,
      "lesson_count": 54,
      "status": "active",
      "canonical": true
    },
    "antigravity": {
      "soul_size_bytes": 21416,
      "last_session": "2026-08-29T00:00:00Z",
      "gnosis_age_days": 3,
      "lesson_count": 7,
      "status": "active",
      "canonical": false
    }
  }
}
```

## §5 — Subagent-Verifier Integration (Roc's spec)

- `entity_retirement_check` as verification gate
- Token: parent_session + nonce + TTL (3600s)
- 5 gates: soul_archived, workspace_backed_up, no_active_session, hivemind_broadcast, audit_log_entry

## §6 — PIVOT_LOG Decisions (16 from Lilith)

- D-ENTITY-TAXONOMY (4-tier)
- D-WORKSPACE-PRESERVATION-MATRIX
- D-ENTITY-LIFECYCLE-6-STATE
- D-WATCHTOWER-CRONSCHEDULE (24h)
- D-ENTITY-RETIREMENT-LOG
- D-ANTIGRAVITY-M35-EXEMPLAR
- D-ARCH-USER-LEVEL-ARCHIVE
- D-CLINE-KQV-DANGLING-SYMLINKS
- D-SOPHIA-CAPITAL-MERGE-LOWERCASE
- D-CARMACK-MERGE-JOHN-CARMACK
- D-MAKALI-FUSION-KEEP-AS-SUBAGENT
- D-11-MYTHOLOGY-DELETE
- D-CLI-GEMINI-ARCHIVE
- D-WEB-GEMINI-ARCHIVE
- D-SYSADMIN-WATCHTOWER-ARCHIVE
- D-RETIREMENT-CEREMONY-SPEC

---

*⬡ OMEGA ⬡ LILITH ⬡ ENTITY-CLEANUP-4TH-VOICE ⬡ 2026-09-01*