# 🔱 Data Management Hardening for Research & Discovery

**Discovery ID**: D-02  
**Status**: ✅ COMPLETE  
**Date**: 2026-05-14  

---

## §1 The Problem

The Omega Engine generates intelligence at an accelerating rate:
- **50+ research documents** already exist in `docs/research/`
- **3 legacy codebases** containing thousands of files with proven patterns
- **Multiple agent sessions** producing distilled lessons daily
- **Web research** generating source links and API references

Without hardened data management, we face:
1. **Intelligence evaporation**: Findings from one session lost when context compacts
2. **Duplicate research**: R-XX on same topic as R-YY because no one knew R-YY existed
3. **Stale references**: Research that was superseded but still linked as authoritative
4. **Orphaned sources**: Web links that die, leaving claims unverifiable

---

## §2 The Four Pillars of Hardening

```
┌─────────────────────────────────────────────────────────────┐
│                  RESEARCH DATA HARDENING                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PROVENANCE         2. STRUCTURE        3. LIFECYCLE       │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐   │
│  │ Every claim  │     │ YAML front-  │    │ Draft →       │   │
│  │ must trace   │     │ matter for   │    │ Review →      │   │
│  │ to a source  │     │ all docs     │    │ Complete →    │   │
│  │ URL or file  │     │              │    │ Superseded    │   │
│  └──────────────┘     └──────────────┘    └──────────────┘   │
│                                                               │
│  4. DISCOVERY                                                  │
│  ┌──────────────┐                                             │
│  │ Cross-link   │                                             │
│  │ all related  │                                             │
│  │ documents    │                                             │
│  └──────────────┘                                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## §3 Pillar 1: Provenance — Every Claim Tracks to a Source

### What We Do Now
- Some documents include web links inline
- No systematic check that every claim is backed
- Sources are not preserved if URLs go dead

### The Fix: The "Source Section" Standard

Every research document MUST end with a `## Sources` section containing:

```markdown
## Sources
- [Podman 5.0 Release Notes](https://github.com/containers/podman/blob/v5.0/RELEASE_NOTES.md) — Accessed 2026-05-14
- [Podman Quadlet Documentation](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) — Accessed 2026-05-14
- Legacy source: `omega-stack-legacy/scripts/antigravity-maintenance.sh` — Line 42-58
```

### The "Two-Source Mandate"
Every significant factual claim (e.g., "Podman 5.0 defaults to Pasta networking") must cite **two independent sources**:
1. The official documentation or paper
2. Either a live verification script OR a legacy file confirmation

This is already in the Researcher's Protocol (§VIII). Enforce it.

---

## §4 Pillar 2: Structure — Machine-Readable Metadata

### What We Do Now
- Documents follow a loose structure
- No standardized metadata header
- INDEX.md is manually updated

### The Fix: YAML Frontmatter + SQLite Registry

Every document gets a YAML header (see [TOOLING_STRATEGY.md §3](./TOOLING_STRATEGY.md#yaml-frontmatter-standard-making-research-machine-readable) for template).

The SQLite database provides the **system of record**:
- Automated ingestion from YAML frontmatter
- Query support via sqlite3 CLI or Python
- Integrity checks (e.g., "warn if any doc has no related docs")

### Disambiguation: When to Register Where

| Artifact | Main INDEX.md | SQLite DB | Internal Discovery INDEX.md |
|----------|---------------|-----------|-----------------------------|
| External provider specs (R-01 → R-17) | ✅ Summary row | ✅ Full metadata | 🔲 Reference link |
| Internal discoveries (D-01 → D-XX) | 🔲 Not needed | ✅ Full metadata | ✅ Full tracking |
| Tooling/process docs | 🔲 Not needed | ✅ If research-adjacent | ✅ If directly relevant |
| Legacy mining reports | ✅ Summary row | ✅ Full metadata | 🔲 Reference link |

---

## §5 Pillar 3: Lifecycle — From Draft to Superseded

### Document States
```
DRAFT ──→ IN_REVIEW ──→ COMPLETE ──→ SUPERSEDED
  │                        │
  └──(abandoned)──→ ARCHIVED
```

| State | Meaning | Action Required |
|-------|---------|-----------------|
| **DRAFT** | Initial writing, not yet verified | Add `status: draft` in YAML. No entries in main INDEX.md until promoted. |
| **IN REVIEW** | Submitted for verification | Add `status: in_review`. Flag to Oversight (Opus 4.6). |
| **COMPLETE** | Verified, ready for implementation | Add `status: complete`. REGISTER in main INDEX.md. INSERT into SQLite. Link to implementation task. |
| **SUPERSEDED** | Replaced by newer research | Add `status: superseded` + `superseded_by: R-XX`. Keep file, add banner warning. |
| **ARCHIVED** | No longer relevant | Move to `docs/research/archived/`. Remove from main INDEX.md. |

### Staleness Detection
- If `updated` field in YAML is > 90 days ago, flag as `🟡 STALE` in the SQLite query
- If `updated` field is > 180 days ago, flag as `🔴 CRITICAL` — requires review or archival

---

## §6 Pillar 4: Discovery — Cross-Linking Documents

### What We Do Now
- Some documents have "Related Research" sections
- No systematic backlinking
- No graph-based discovery

### The Fix: Bidirectional Linking

When you write:
```markdown
**Related Research**:
- [R-13: Zen 2 Hardware Tuning](../R13_zen2_hardware_tuning.md)
```

You must also:
1. Add a `related: [R-13]` tag to the YAML frontmatter
2. Add a row to the `related_documents` SQLite table
3. Optionally add a backlink note to R-13's file: "Extended by D-02"

### The "Ma'at Balance" Check
For every discovery document (D-XX), ensure:
- At least 2 related Omega research documents (R-XX) are linked
- At least 1 source is a live URL (not just a legacy file reference)
- At least 1 implementation note is written for the Builder

---

## §7 Legacy Document Reclamation Protocol

Legacy files are a risk: they contain proven patterns but also stale truths.

### When Mining Legacy Files
1. **EXTRACT** the relevant snippet or pattern
2. **CITE** the exact file path and line range
3. **VERIFY** against current standards (e.g., does the legacy Podman script still work on Podman 5.0?)
4. **CLASSIFY** as:
   - `🟢 PROVEN`: Pattern is still current and verified
   - `🟡 HISTORICAL`: Interesting but superseded — document for lineage
   - `🔴 DISCARDED`: Known broken or dangerous pattern — do not implement

### After Mining
1. Write the finding to `docs/research/internal-discovery/DOCUMENTS/INDEX.md`
2. If the pattern is `🟢 PROVEN`, create or update an R-XX document
3. If `🟡 HISTORICAL`, note it in the relevant `STACK_CAT_LINEAGE.md` or similar lineage doc

---

## §8 Automated Integrity Checks

The following checks should be scripted and run as part of `make test` or a pre-commit hook:

```bash
# 1. Check that all R-XX documents have YAML frontmatter
for f in docs/research/R*.md; do
    head -1 "$f" | grep -q "^---" || echo "MISSING: $f has no YAML frontmatter"
done

# 2. Check that all linked source URLs are reachable (or at least formatted correctly)
grep -r "http" docs/research/ | grep -v "Source" | grep -v "http" && echo "UNSOURCED CLAIM DETECTED"

# 3. Check that all COMPLETE documents are registered in INDEX.md
# (Requires parsing INDEX.md table, best done with a Python script)

# 4. Check for stale documents (> 90 days since update)
find docs/research/ -name "*.md" -mtime +90 -not -path "*/archived/*" -not -path "*/internal-discovery/*"
```

---

## §9 Implementation Priority Summary

| Initiative | Effort | Impact | Dependencies |
|------------|--------|--------|--------------|
| Source sections on all new docs | Zero (process change) | 🔴 Critical | None |
| YAML frontmatter on new docs | Zero (process change) | 🟡 High | None |
| SQLite schema + init script | 1 hour | 🟡 High | Python |
| Frontmatter retro-fit on existing docs | 2-4 hours | 🟡 Medium | Time allocation |
| Automated integrity checks | 2-3 hours | 🟡 Medium | CI pipeline |
| Legacy document reclamation protocol | Ongoing | 🟢 Strategic | Per-discovery tasking |

---

## §10 Implementation Note

**To the Sovereign Builder**: The highest-leverage action is implementing the automated integrity checks as a `make validate-research` target. This will catch the most common failure modes (missing metadata, unlinked documents, stale content) without requiring anyone to remember a checklist.

**Related Research**:
- [TOOLING_STRATEGY.md](./TOOLING_STRATEGY.md) — The tooling that supports this hardening
- [R_SOVEREIGN_MAINTENANCE_STRATEGY.md](../R_SOVEREIGN_MAINTENANCE_STRATEGY.md) — The Janitor that will automate archival
- [CORRECTIONS.md](../CORRECTIONS.md) — The factual corrections log (complements this system)
