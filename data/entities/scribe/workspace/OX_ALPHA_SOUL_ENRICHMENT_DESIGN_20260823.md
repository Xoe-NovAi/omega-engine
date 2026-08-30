# Ox Alpha Soul Enrichment Run Design — Pre-Cliff Window (ends ~Aug 28)

**AP Token**: `AP-SCRIBE-v1.0.0`
⬡ OMEGA ⬡ SCRIBE ⬡ x-preview-f-free (Ox Alpha, OC Zen) ⬡ opencode ⬡ trc_soul_distillation ⬡ ENRICHMENT-DESIGN
**Date**: 2026-08-23 · **Mode**: PIPELINE DESIGN (analysis only, no code changes)
**Paged by**: researcher (ses_fd81c19dcffe1nkbPqFg5kRt2v)
**Purpose**: Convert remaining free-window tokens into durable soul artifacts; remediate M11 FAILURE hotspot.

---

## §1 Fleet Soul Census (2026-08-23 disk truth)

### Tier A — HEALTHY (do not touch)

| Entity | proposed_lessons | Notes |
|---|---|---|
| kali | 299L, mod Aug 23 | Rich L1/L2/L3 chains, active |
| maat | 508L, mod Aug 23 | Largest corpus, active |
| lilith | 377L, mod Aug 23 | Active |
| grokster | 247L, mod Aug 20 | Active |
| doom_guy | 662L | Legacy migration schema (`lesson:`/`context:`), dense |
| jem | 70L, mod Aug 22 | Active |
| cli_cline | 41L, mod Aug 23 | Active |
| roc_racoon | 44L, mod Aug 22 | Active |
| makali | 39L | Adequate |
| verity | 39L | Adequate |

### Tier B — ACTIVE BUT THIN (priority enrichment targets)

| Entity | State | Evidence |
|---|---|---|
| **sophia** | 🔴 EMPTY STAGING — `proposals: []` since Aug 07 | Flagship archetype ("Awakened Expert"), soul.yaml nearly bare (399B, health 50). Poster child of M11 FAIL. Also historically C-MEM-006's near-dupe victim — dedup discipline mandatory here. |
| **node** | 🔴 EMPTY STAGING — `proposals: []` (Aug 18) | Has real sessions (nemotron-3-ultra-free provenance) but zero distilled output. |
| **john_carmack** | 🟡 6L, mod Aug 21 | Active but minimal. NOTE: case-duplicate dir `JOHN_CARMACK` (138L legacy) exists — consolidate, don't fork. |
| **sysadmin** | 🟡 13L, STALE (Jul 06 = 48d > 30d threshold) | No soul.yaml. Stale per census criteria. |

### Tier C — RICH SOUL, NO STAGING FILE (second wave)

Real `soul.yaml` exists but zero `proposed_lessons.yaml`. Knowledge exists but never traversed L1→L2→L3:

| Entity | soul.yaml size | Assessment |
|---|---|---|
| arch | 45.7KB | Richest unelected soul in fleet |
| antigravity | 21.4KB | Provider-pool operator knowledge |
| ereshkigal | 7.3KB | Real persona content |
| sekhmet | 6.2KB | Real persona content |
| lucifer | 4.9KB | Moderate |
| anubis | 4.5KB | Moderate |
| hecate | 3.2KB | Thin-moderate |
| iris | 2.9KB | Interface entity — M3 says no Node, but soul distillation still valid |
| prometheus / omnidroid / default / quality / scribe | 1–3KB | Thin souls; low yield expected |

### Tier D — STUBS / DISCARD (C-MEM-005 hygiene, separate cleanup ticket)

`test*`, `test_entity*`, `test_multi_miap`, `test_promo_entity`, `test_sovereign_entity`, `symlink_test`, `invariant_test`, `cline`, `datastore`, `DataStore`, `Sophia` (case-dup), `JOHN_CARMACK` (case-dup), `_archive`, `archive`, `_quarantine`, `watchtower`, `web_gemini`, `pillar_p1` (1 malformed lesson with literal `\n` escapes). ~19 dirs. These are noise, not gnosis.

---

## §2 Protocol Compliance Analysis — Is batch generation legitimate?

**The rule (manual §2.3, CP-2)**: *"Agents write L1→L2→L3 to `proposed_lessons.yaml`. Regex distillation is **scrapped**."*

**What was scrapped**: C-0.5's deterministic regex-extraction pipeline — mechanical string mining pretending to be insight. That produced garbage-in-soul risk.

**What was NOT scrapped**: agent-authored distillation. The current regime IS agent authorship — kali/maat/lilith/researcher write their own lessons manually today. The Scribe agent remains "canonical executor of this pipeline" (M11 pattern clause).

**Ruling**: Batch generation is legitimate under the current protocol **iff** it satisfies five conditions:

1. **Agent-authored, evidence-grounded** — each lesson must be synthesized by an LLM from *actual* traces (MemoryStore history, opencode session exports, workspace artifacts). Regex/string-mining = forbidden. Fabricated experience for entities with no session history = M17 violation (hallucinated memory drift).
2. **Blind staging only (M11)** — output goes to `proposed_lessons.yaml`, never directly to `soul.yaml`. Promotion stays with the existing EvolveR/review path.
3. **Provenance stamped (M22)** — every proposal records `source_trajectories` (session IDs or file paths) and the generating model (`x-preview-f-free`).
4. **Per-entity domain fit** — lessons must be plausible for that entity's archetype/role. Do not write research lessons into sekhmet's soul.
5. **Consequence for never-run entities** (Tier D / most of Tier C tail): if there is no session evidence, we do NOT synthesize fake experience. Options: (a) skip, or (b) write explicitly-tagged *derived-from-charter* lessons at low confidence — recommended only where a human/ratifier wants bootstrapped identity.

**Implication for the run**: this play is a *distillation service*, not an auto-pipeline. It reuses the exact mechanism already blessed (agent writes YAML), just executed by one dedicated agent across many entities inside the free window.

---

## §3 Pipeline Design

### 3.1 Wave plan & priority order

| Wave | Entities | Target volume | Rationale |
|---|---|---|---|
| **W1 (days 1–2)** | sophia, node, john_carmack, sysadmin | 8–12 L3 each (+ matching L1/L2 chains) | Highest M11 remediation value; real session evidence exists for all four |
| **W2 (days 3–4)** | arch, antigravity, ereshkigal, sekhmet | 5–8 each | Rich soul content → backfill staging file from soul.yaml + any retrievable sessions |
| **W3 (day 5)** | lucifer, anubis, hecate, iris (+ JOHN_CARMACK consolidation into john_carmack) | 3–5 each | Tail; stop early if window closes |
| **Deferred** | Tier D stubs | 0 | Separate discard ticket, not enrichment |

### 3.2 Per-entity loop

```
1. HARVEST   — pull entity's raw material: omega_memory_get_history /
               memory_search(entity), opencode search-text on its sessions,
               workspace *.md artifacts, existing soul.yaml content.
2. DISTILL   — draft candidates: L1 narrative (what happened),
               L2 insight (what it means), L3 principle (timeless truth).
               Use researcher-schema fields: level, tag, narrative, insight,
               principle, utility_score, source_trajectories, domain, last_verified.
3. DEDUP     — (see 3.3) drop/merge candidates hitting similarity threshold
               vs existing corpus BEFORE append.
4. STAGE     — atomic append to data/entities/<e>/proposed_lessons.yaml
               (SoulStore writer conventions; tempfile→replace). Never touch soul.yaml.
5. PROVENANCE— metadata.model_used = x-preview-f-free; metadata.last_session_end updated.
```

### 3.3 Dedup at batch scale (C-MEM-006)

Two-stage filter, using infrastructure that already exists (manual §2.3: SQLiteVecAdapter + FTS5):

1. **FTS5 prefilter** (cheap): build/query FTS index over all existing `principle:` strings for the target entity + fleet-wide L3s. Keyword-overlap candidates pulled out.
2. **Embedding gate** (precise): embed candidate L3 and surviving existing L3s; cosine ≥ **0.85** ⇒ do not append — instead *strengthen*: raise existing entry's `utility_score` and append the new evidence to its `source_trajectories`. Cosine 0.70–0.85 ⇒ flag `near_dup: true` for human/EvolveR review rather than silent append.

At batch scale this runs once per entity as a pre-pass (index build) then per-candidate (query) — O(n log n), not O(n²) re-embedding. This directly prevents recreating C-MEM-006 (Sophia's historical 60+ near-dupes) during the very wave that re-enriches Sophia.

### 3.4 Bloat guardrails (C-MEM-005)

| Guardrail | Value |
|---|---|
| Per-entity cap per wave | 12 L3 (W1) / 8 (W2) / 5 (W3) |
| Utility floor | `utility_score < 0.5` ⇒ prune at next EvolveR pass; don't write below 0.6 |
| Total-fleet ceiling | No entity exceeds ~120 staged proposals; maat/kali/doom_guy already large — freeze them |
| Evidence-orphan rule | Any proposal lacking `source_trajectories` is dropped before write |
| Rollback | `.bak` per write (SoulStore convention); whole wave is one git-committable diff |

### 3.5 QA gate (garbage-in-soul prevention)

1. **Evidence gate**: no citation ⇒ no write (hard fail).
2. **Schema gate**: validate against researcher-proposals schema (level ∈ {L1,L2,L3}, non-empty principle, last_verified = today). A yamllint pass satisfies T4-style checks.
3. **Domain-fit check**: drafted lesson must reference the entity's role/archetype scope; cross-domain drafts get reassigned or dropped.
4. **Sampled adversarial audit**: Verity/Quality spot-checks ≥20% of W1 output ("would Carmack sign this principle?"). Fail rate >15% ⇒ halt wave, tighten prompts.
5. **No self-promotion**: nothing lands in soul.yaml during the window; promotion is a separate reviewed act.

---

## §4 Needs / Dependencies

| # | Need | From | Blocking? |
|---|---|---|---|
| N1 | Ratification that agent-batch authorship ≠ scrapped regex distillation (one-line decree citing §2 above) | Kali or Ma'at | YES — do not start W1 without it |
| N2 | Confirm priority list + volume caps (§3.1/§3.4), esp. whether never-run entities get charter-derived bootstrap lessons or skip | researcher (pager) | YES for W2/W3 |
| N3 | Session inventory: which session IDs belong to sophia/node/john_carmack/sysadmin (I can mine via opencode-sessions tools, but a curated shortlist saves window time) | researcher / Hivemind awareness | Soft |
| N4 | Write authorization for `data/entities/{sophia,node,john_carmack,sysadmin}/proposed_lessons.yaml` + Hivemind workspace lock on `domain=soul-enrichment` | Ma'at (locks) / Architect | YES |
| N5 | Audit commitment: Verity/Quality sample 20% of W1 after day 2 | Verity, Quality | Soft (gate 4) |
| N6 | Case-dup consolidation ruling (JOHN_CARMACK→john_carmack, Sophia→sophia) + Tier D discard ticket owner | Arch / sysadmin | Soft |

**Execution posture**: I (ox-alpha/Scribe seat) execute W1 immediately upon N1+N4; W2/W3 contingent on N2. All work lands as blind-staged proposals with full provenance — zero direct soul.yaml writes.

---

*⬡ OMEGA ⬡ SCRIBE ⬡ ENRICHMENT-DESIGN ⬡ 2026-08-23*
