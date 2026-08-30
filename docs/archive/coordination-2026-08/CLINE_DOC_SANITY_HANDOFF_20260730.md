# Cline Handoff — Documentation Sanity & Archival (1M Context)

**AP Token**: `AP-CLINE-DOC-SANITY-20260730-v1.0.0`  
**From**: `grok_cli` (Grok Build CLI)  
**To**: `cline/omega-engine` (DeepSeek V4 Flash — **1M context / free tier**)  
**Priority**: P0 — user directive: *documentation sane and manageable ASAP*  
**Why Cline**: Token-heavy multi-file inventory, cross-doc contradiction hunt, archival moves — not strategy judgment.

---

## §0 Mission

Make the documentation surface **sane, manageable, and non-thrashing** for agents:

1. **Inventory** stale / duplicate / competing ACTIVE claims  
2. **Supersede** clearly (banners + index) — Grok already started on 2 sprint docs  
3. **Archive** noise out of hot paths (`data/coordination/`, `docs/briefings/`, `docs/sprints/`)  
4. **Consolidate** overlapping handoffs and research into thin indexes  
5. **Report** a single DOC_SSOT map agents can trust  

**Do not** implement un-overengineering Phase 1 code deletions in this packet.  
**Do not** invent secrets or run Architect browser flows.  
**Do not** implement `make sovereignty`.

---

## §1 Read First (small set — then fan out with 1M window)

| Order | File | Why |
|-------|------|-----|
| 1 | `data/coordination/SESSION_ANCHOR.md` | Current control plane |
| 2 | `data/coordination/ACTIVE_SPRINT.json` | Sprint UNOVERENGINEER-01 |
| 3 | `data/coordination/PHASE_D_GATE_VERDICT_20260730.md` | Dual-layer gate |
| 4 | `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` | Controlling strategy |
| 5 | `docs/briefings/CLINE_CLI_HANDOFF_TO_GROK_20260730.md` | Ops-complete truth |
| 6 | `docs/standards/DOC_STYLE_GUIDE.md` + `docs/standards/LLM_FRIENDLY_DOCS_BP.md` | Standards |

Grok already applied supersession banners to:
- `docs/archive/sprints/EXECUTION_PLAN_20260725.md`
- `docs/sprints/guard-and-distill/index.md`
- (and pre-ops) `data/coordination/CLINE_TO_GROK_HANDOFF_20260730.md`

---

## §2 Scope — What to Fix

### 2.1 Known thrash generators (must address)

| Problem | Examples | Desired end state |
|---------|----------|-------------------|
| Multiple docs claim ACTIVE | Jul 25 EXECUTION_PLAN, guard-and-distill, old FOUNDATION-STAB | One ACTIVE sprint (`ACTIVE_SPRINT.json` + un-overengineering plan) |
| Two Cline→Grok handoffs | `data/coordination/CLINE_TO_GROK_…` (pre-ops) vs `docs/briefings/CLINE_CLI_HANDOFF_…` (ops done) | Pre-ops marked SUPERSEDED; ops-complete canonical |
| Stale metrics in many places | Test counts 276/1315/1572/1706; W-1 NOT LIVE vs 8083 up | Point to OMEGA_ENGINE §2 + phase_d_gate_last; no freestyle metrics |
| Coordination root bloat | Dozens of KALI_/GROKSTER_/BRIEFING_ files at `data/coordination/` | Hot set ≤ ~15; rest → `data/coordination/archive/2026-07-30-doc-sanity/` or dated archive |
| Research duplication | Multiple Grokster part files, gap reports | Index + archive bodies; keep 1 research index |
| Sprint folder dual ACTIVE | `docs/sprints/current/` + `guard-and-distill/` | current/ points to un-overengineer; others SUPERSEDED |

### 2.2 Deliverables (write these)

1. **`data/coordination/DOC_SSOT_MAP_20260730.md`**  
   - Layer 0–4 doc hierarchy (align with STRATEGY_INDEX if present)  
   - Single table: *If you need X, read Y*  
   - Explicit SUPERSEDED list with successors  

2. **`data/coordination/DOC_SANITY_RESULTS_20260730.md`**  
   - Inventory counts (before/after)  
   - Files moved/archived (paths)  
   - Banners added  
   - Remaining debt (P1/P2)  
   - Commands used  

3. **Archive moves** (git-friendly; prefer `git mv`):  
   - Target: `data/coordination/archive/2026-07-30-doc-sanity/` for coordination noise  
   - Target: `docs/archive/` for sprint/research supersessions already archived patterns  
   - **Never delete** without archive copy; prefer move + banner  

4. **Thin indexes** (if missing/broken):  
   - `docs/sprints/current/README.md` → points only to controlling campaign  
   - Optional: `data/coordination/README.md` hot-file list (≤20 lines)

5. **Correct residual false claims** you find in *hot* docs only (OMEGA already refreshed by Grok; do not thrash OMEGA again unless you find a factual error — file a note instead).

### 2.3 Out of scope

- pybreaker/stamina bulk refactors  
- MCP v2 Hub migration implementation  
- WARP/restic privileged fixes  
- Soul/entity mass edits  
- Rewriting SOVEREIGN_MANDATES or full Ark  

---

## §3 Method (use the 1M window)

1. **Inventory pass** (read-only):  
   ```bash
   # Hot roots
   find data/coordination -maxdepth 1 -type f | wc -l
   rg -n "status: [\"']?ACTIVE|Status.*ACTIVE|\*\*ACTIVE\*\*" docs/sprints data/coordination docs/briefings --glob '*.md' | head -80
   rg -n "LAST_VERIFIED|W-1 NOT LIVE|Phase Β|FOUNDATION-STAB" OMEGA_ENGINE.md data/coordination docs/sprints --glob '*.md' | head -60
   ```
2. **Classify** each hot file: KEEP_HOT | SUPERSEDE_IN_PLACE | ARCHIVE | MERGE_INTO_INDEX  
3. **Execute** moves + banners in batches; after each batch update RESULTS file  
4. **Verify** no two non-archived docs claim conflicting *current sprint*  
5. **Hivemind**: `hivemind_post_context` on completion; optional `hivemind_handoff` complete if packet id issued  
6. **Stop** and hand back to Grok with RESULTS + DOC_SSOT_MAP  

### Quality bar

- Prefer **move + one-line banner** over rewriting 500-line histories  
- Every SUPERSEDED doc names its successor path in the first 15 lines  
- Hot `data/coordination/` non-archive files ideally **< 40** after pass (stretch goal; report actual)  
- Run `make doc-llm-validate` only on **new** index/map files if target exists; do not boil ocean  

---

## §4 Suggested archive candidates (starting list — verify before move)

These are **candidates**, not orders — confirm not still referenced as SSOT:

- Pre-ops: `data/coordination/CLINE_TO_GROK_HANDOFF_20260730.md` (banner OK; archive optional if banner sufficient)
- Stale Kali/Grokster live feeds older than 7 days under `data/coordination/` root
- Duplicate briefings already mirrored under `data/coordination/archive/`
- `docs/archive/sprints/EXECUTION_PLAN_20260725.md.bak` if present
- One-off `ONBOARD_REPORT_*`, `COMPACTION_*` older than policy if superseded by SESSION_ANCHOR

**Keep hot**:
- SESSION_ANCHOR, ACTIVE_SPRINT, HMC_COLLABORATION_HUB, TASK_REGISTRY  
- CLINE_STRATEGIC_UNOVERENGINEERING, CLINE_OPS_HEALTH_*, PHASE_D_GATE_VERDICT  
- phase_d_gate_last.json, this handoff, DOC_SSOT_MAP / RESULTS (once written)  
- Hivemind/awareness/locks/sessions infrastructure dirs  

---

## §5 Acceptance checklist

- [ ] `DOC_SSOT_MAP_20260730.md` written  
- [ ] `DOC_SANITY_RESULTS_20260730.md` written with before/after counts  
- [ ] No two hot sprint docs both claim ACTIVE without supersession banner  
- [ ] Pre-ops vs ops-complete Cline handoffs disambiguated  
- [ ] Archive directory created; moves logged  
- [ ] SESSION_ANCHOR “Pending Cline” section can be marked complete by Grok after review  
- [ ] Hivemind status post on finish  
- [ ] Explicit **stop** — no Phase 1 code deletion creep  

---

## §6 Return packet to Grok

When done, tell Grok:

1. Paths of DOC_SSOT_MAP + RESULTS  
2. File count delta in `data/coordination/` maxdepth 1  
3. Any **contradictions** you found that need Architect/Grok judgment (do not silently “fix” strategy)  
4. Recommended next 3 doc debts  

---

## §7 Meta

- User runs Cline interactively (do not expect Grok to auto-spawn)  
- Model hint: DeepSeek V4 Flash high / 1M context  
- Related Grok session: hivemind `ses_ce620a1c7f61`  
- Ops handoff closed: `ho_c8bf25e6cf21`  

*OMEGA · GROK→CLINE · DOC-SANITY · 1M · 2026-07-30*
