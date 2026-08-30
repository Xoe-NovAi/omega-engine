# 🔱 Documentation Sprint Plan — The "Carmack Cut"
**AP Token**: `AP-DOC-SPRINT-PLAN-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_doc_sprint ⬡ ACTIVE

**Date**: 2026-07-07
**Purpose**: A pragmatic, 7-day, runtime-focused documentation sprint. Synthesized from the Ma'at, Lilith, Roc Racoon, and John Carmack council session.

---

## 🎯 Sprint Goals (Revised)

1. **Runtime Linkage**: Expand `DocRef:` backlinks from source code to documentation. This is how agents *actually* find information.
2. **Domain Organization**: Port the legacy `expert-knowledge/` pattern to `docs/knowledge/` to house operational wisdom.
3. **Pragmatic Standardization**: Apply Omega headers *only* to reference docs (~150 files). Exempt R-docs, working docs, and archives.
4. **Dead Weight Elimination**: Archive or delete documentation that hasn't been read in 30 days.
5. **Deepening**: Write the 3 critical architecture deep-dives (Oracle, Provider Fabric, MemoryStore).

---

## 📋 The 7-Day Execution Plan

### Day 1: Style Guide & Validator Calibration
**Goal**: Stop over-enforcing. Define what actually needs headers.
- **1.1 Update `DOC_STYLE_GUIDE.md`**: Define File Categories.
  - *Reference docs* (architecture, strategy, standards, user guides) → Omega header mandatory.
  - *R-docs* (`docs/research/R*.md`) → R-doc format (exempt from Omega header).
  - *Working docs* (team handoffs, intake) → EXEMPT.
  - *Archives* → EXEMPT (frozen).
  - *Skills* → OpenCode YAML only.
- **1.2 Simplify Validator**: Remove 120-char line length enforcement from CI (keep as guideline). Add orphan detection.
- **1.3 Directory Cleanup**: Populate or remove empty directories (`docs/audit/`, `docs/engine/`, `docs/handoff/`).

### Day 2: Core Headers & Archival
**Goal**: Standardize what matters, archive the rest.
- **2.1 Core Headers**: Add Omega headers to ~40 active core docs (`docs/strategy/*.md` active only, `docs/standards/*.md`, `docs/user/*.md`).
- **2.2 Archive Dead Weight**: Identify files untouched/unread in 30 days. Move to `docs/archive/`. Target: reduce 750 files to ~300 active files.
- **2.3 Metric Freshness**: Wire `make test-badge` into public-facing docs to prevent stale metrics (e.g., USER_MANUAL).

### Day 3: Runtime Linkage (`DocRef:`)
**Goal**: Build the wiring agents actually use.
- **3.1 Expand `DocRef:` Coverage**: Add `# DocRef: docs/...` comments to every file in `src/omega/oracle/` linking to their respective documentation.
- **3.2 Handoff Standardization**: Create `data/handoff/INDEX.md` and a standardized handoff template (porting the legacy `OPUS_SUMMONING_BRIEF.md` pattern).

### Day 4: Domain Organization
**Goal**: Give operational wisdom a home.
- **4.1 Create `docs/knowledge/`**: Port the `expert-knowledge/` pattern from legacy. Create subdirectories: `architect/`, `infrastructure/`, `agent-tooling/`, `environment/`, `patterns/`.
- **4.2 Migrate Wisdom**: Move actionable operational wisdom from the flat `docs/strategy/` folder into the new domain-organized knowledge base.
- **4.3 Header Evolution**: Update `DOC_STYLE_GUIDE.md` to include `# Tags:` and `# Cross-references:` in the Omega header.

### Days 5-6: Architecture Deep-Dives
**Goal**: Document the core engine.
- **5.1 Oracle Deep-Dive**: `docs/architecture/ORACLE_DEEP_DIVE.md`
- **5.2 Provider Fabric Deep-Dive**: `docs/architecture/PROVIDER_FABRIC_DEEP_DIVE.md`
- **5.3 Memory Store Deep-Dive**: `docs/architecture/MEMORY_STORE_DEEP_DIVE.md`

### Day 7: Verification & Ship
**Goal**: Ensure freshness and ship.
- **7.1 Final Validation**: Run validator against the newly scoped ruleset. Fix failures.
- **7.2 Freshness Gate**: Create `make doc-freshness` CI gate to flag docs >30 days stale.
- **7.3 Ship**: Commit and conclude sprint.

---

## 💡 Success Metrics (The Run-Side View)

- **Agent Retrieval**: Agents find the right doc on the first try (measured by `DocRef:` coverage in source code).
- **Signal-to-Noise**: Total active documentation files reduced by at least 40% (moved to archive).
- **Freshness**: Zero active reference docs older than 30 days without a freshness verification touch.
- **Compliance**: 100% of *Reference Docs* have Omega headers. 0% of *Working Docs* are flagged for missing them.

---

**Sovereign Verdict**: Documentation exists to solve a problem. If nobody reads it, it's not documentation — it's clutter. This 7-day sprint strips away compliance theater to focus on runtime linkage, domain organization, and architectural truth.
