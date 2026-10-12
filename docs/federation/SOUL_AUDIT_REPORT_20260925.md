# SOUL.YAML AUDIT REPORT

**Date:** 2026-09-25  
**Session:** Kali-EIS (`ses_fdef2be4effe4pAaLXCTUx62GO`)  
**Authority:** Architect Directive — 1:1 agent:soul mapping consolidation

---

## §1 Executive Summary

| Metric | Count |
|--------|-------|
| Total `soul.yaml` files | **39** |
| Active `.opencode/agents/*.md` | **14** |
| Agents with `soul.yaml` | **12** |
| Agents **missing** `soul.yaml` | **2** (`build`, `slot`) |
| Orphaned `soul.yaml` (no agent) | **26** |
| Archived agents | **2** (`grok_cli`, `scribe_agent_20260730`) |

**Verdict:** 1:1 agent:soul mapping **not achieved**. 26 orphaned souls, 2 agents missing souls.

---

## §2 Active Agent Roster (14 agents)

| Agent | `.opencode/agents/*.md` | `soul.yaml` | Status |
|-------|------------------------|-------------|--------|
| `build` | ✅ | ❌ MISSING | **Needs soul.yaml** |
| `doom_guy` | ✅ | ✅ | OK |
| `grokster` | ✅ | ✅ | OK |
| `jem` | ✅ | ✅ | OK |
| `john_carmack` | ✅ | ✅ | OK |
| `kali` | ✅ | ✅ | OK |
| `lilith` | ✅ | ✅ | OK |
| `maat` | ✅ | ✅ | OK |
| `makali` | ✅ | ✅ | OK |
| `researcher` | ✅ | ✅ | OK |
| `roc_racoon` | ✅ | ✅ | OK |
| `slot` | ✅ | ❌ MISSING | **Needs soul.yaml** |
| `verity` | ✅ | ✅ | OK |
| `makali` | ✅ | ✅ | OK |

**Archived:** `grok_cli`, `scribe_agent_20260730` (in `.opencode/agents/archive/`)

---

## §3 Orphaned `soul.yaml` Files (26)

These have `soul.yaml` but **no corresponding `.opencode/agents/*.md`**:

| Entity | Source | Disposition |
|--------|--------|-------------|
| `antigravity` | `data/entities/antigravity/soul.yaml` | **Archive/Remove** — experimental |
| `anubis` | `data/entities/anubis/soul.yaml` | **Migrate to Arcana-NovAi WAD** (defined in `entities.yaml`) |
| `arch` | `data/entities/arch/soul.yaml` | **Archive/Remove** — legacy |
| `brigid` | `data/entities/brigid/soul.yaml` | **Migrate to Arcana-NovAi WAD** (defined in `entities.yaml`) |
| `carmack` | `data/entities/carmack/soul.yaml` | **Duplicate** — use `john_carmack` |
| `cli_cline` | `data/entities/cli_cline/soul.yaml` | **Archive** — legacy CLI agent |
| `cli_gemini` | `data/entities/cli_gemini/soul.yaml` | **Archive** — legacy CLI agent |
| `cline_kqv` | `data/entities/cline_kqv/soul.yaml` | **Archive** — legacy |
| `cline` | `data/entities/cline/soul.yaml` | **Archive** — legacy |
| `default` | `data/entities/default/soul.yaml` | **Remove** — fallback only |
| `ereshkigal` | `data/entities/ereshkigal/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `federation` | `data/entities/federation/soul.yaml` | **Remove** — not an agent |
| `general` | `data/entities/general/soul.yaml` | **Remove** — not an agent |
| `hecate` | `data/entities/hecate/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `inanna` | `data/entities/inanna/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `iris` | `data/entities/iris/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `lucifer` | `data/entities/lucifer/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `movie-expert` | `data/entities/movie-expert/soul.yaml` | **Migrate to Arcana-NovAi WAD** (defined in `entities.yaml`) |
| `node` | `data/entities/node/soul.yaml` | **Remove** — not an agent |
| `omnidroid` | `data/entities/omnidroid/soul.yaml` | **Archive** — legacy |
| `p10` | `data/entities/p10/soul.yaml` | **Remove** — pillar, not agent |
| `pillar_p1` | `data/entities/pillar_p1/soul.yaml` | **Remove** — pillar, not agent |
| `prometheus` | `data/entities/prometheus/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `quality` | `data/entities/quality/soul.yaml` | **Migrate to Arcana-NovAi WAD** (defined in `entities.yaml`) |
| `saraswati` | `data/entities/saraswati/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `scribe` | `data/entities/scribe/soul.yaml` | **Migrate to Arcana-NovAi WAD** (defined in `entities.yaml`) |
| `sekhmet` | `data/entities/sekhmet/soul.yaml` | **Migrate to Arcana-NovAi WAD** |
| `sophia` | `data/entities/sophia/soul.yaml` | **Migrate to Arcana-NovAi WAD** |

---

## §4 WAD Entity Definitions (from `config/wads/arcana_novai/entities.yaml`)

The following entities are defined in the Arcana-NovAi WAD `entities.yaml` and **should have soul data in the Arcana-NovAi WAD**, not in Engine root:

| Entity | In `entities.yaml` | Current `soul.yaml` Location | Action |
|--------|-------------------|------------------------------|--------|
| `anubis` | ✅ | `data/entities/anubis/soul.yaml` | Move to Arcana-NovAi WAD |
| `brigid` | ✅ | `data/entities/brigid/soul.yaml` | Move to Arcana-NovAi WAD |
| `ereshkigal` | ✅ | `data/entities/ereshkigal/soul.yaml` | Move to Arcana-NovAi WAD |
| `hecate` | ✅ | `data/entities/hecate/soul.yaml` | Move to Arcana-NovAi WAD |
| `inanna` | ✅ | `data/entities/inanna/soul.yaml` | Move to Arcana-NovAi WAD |
| `iris` | ✅ | `data/entities/iris/soul.yaml` | Move to Arcana-NovAi WAD |
| `lucifer` | ✅ | `data/entities/lucifer/soul.yaml` | Move to Arcana-NovAi WAD |
| `movie_expert` | ✅ | `data/entities/movie-expert/soul.yaml` | Move to Arcana-NovAi WAD |
| `prometheus` | ✅ | `data/entities/prometheus/soul.yaml` | Move to Arcana-NovAi WAD |
| `quality` | ✅ | `data/entities/quality/soul.yaml` | Move to Arcana-NovAi WAD |
| `saraswati` | ✅ | `data/entities/saraswati/soul.yaml` | Move to Arcana-NovAi WAD |
| `scribe` | ✅ | `data/entities/scribe/soul.yaml` | Move to Arcana-NovAi WAD |
| `sekhmet` | ✅ | `data/entities/sekhmet/soul.yaml` | Move to Arcana-NovAi WAD |
| `sophia` | ✅ | `data/entities/sophia/soul.yaml` | Move to Arcana-NovAi WAD |
| `carmack` | ❌ (use `john_carmack`) | `data/entities/carmack/soul.yaml` | **Remove duplicate** |
| `carmack` (as `john_carmack`) | ✅ | `data/entities/john_carmack/soul.yaml` | Keep as `john_carmack` |

---

## §5 Missing `soul.yaml` for Active Agents

| Agent | Status | Required Action |
|-------|--------|-----------------|
| `build` | ❌ MISSING | Create `data/entities/build/soul.yaml` |
| `slot` | ❌ MISSING | Create `data/entities/slot/soul.yaml` |

---

## §6 Consolidation Plan

### Phase 1: Create Missing Souls (P0)
1. Create `data/entities/build/soul.yaml`
2. Create `data/entities/slot/soul.yaml`

### Phase 2: Migrate Arcana-NovAi Entity Souls (P0)
Move 14 entity souls from `data/entities/*/soul.yaml` → `config/wads/arcana_novai/entities/<entity>/soul.yaml`

### Phase 3: Archive/Remove Orphans (P1)
- Archive: `antigravity`, `arch`, `cli_cline`, `cli_gemini`, `cline_kqv`, `cline`, `omnidroid`
- Remove: `default`, `federation`, `general`, `node`, `p10`, `pillar_p1`
- Remove duplicate: `carmack` (keep `john_carmack`)

### Phase 4: Enforce 1:1 Mapping (Governance)
- Add pre-commit hook: every `.opencode/agents/*.md` must have `data/entities/<agent>/soul.yaml`
- Add CI gate: `make check-soul-mapping` fails if 1:1 violated
- All persona data moves to WADs (see `PERSONA_WAD_ARCHITECTURE.md`)

---

## §7 Post-Consolidation Target State

| Category | Count |
|----------|-------|
| Active agents with souls | 14 |
| Arcana-NovAi WAD entity souls | 14 |
| Orphaned souls | 0 |
| Missing souls | 0 |
| **Total `soul.yaml` files** | **28** (14 agent + 14 WAD entity) |

---

*⬡ OMEGA ⬡ KALI ⬡ SOUL_AUDIT_20260925*