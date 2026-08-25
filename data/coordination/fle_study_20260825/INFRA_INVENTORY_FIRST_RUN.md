# INFRA INVENTORY — FIRST RUN (the deliverable's proof)
⬡ OMEGA ⬡ MAAT ⬡ opencode/x-preview-f-free ⬡ trc_infra_inventory ⬡ BUILD-REPORT
**Date**: 2026-08-25T23:26Z · **Commissioned by**: kali (Consultant, ses_fdef2be4effe4pAaLXCTUx62GO)
**Source spec**: CARMACK_CONTEXT_INFRA_AUDIT.md §5 remediation #5 · **Runtime**: 0.88s (limit 10s)

---

## §1 WHAT BUILT

| File | Role |
|---|---|
| `scripts/infra_inventory.py` | The anti-blindspot organ. 25-component registry, E/I/D/C probes, verdict engine (KEEP/FIX/CUT/GHOST/CEREMONY), human table + `--json`, `--ci` regression gate vs baseline, `--update-baseline` atomic snapshot, `--registry` YAML override. stdlib+PyYAML only, sync, idempotent. |
| `tests/scripts/test_infra_inventory.py` | 26 contract tests (M21): registry validity, typed ProbeResults, wiring-ignores-tests, exhaustive verdict-engine class coverage, CI exit codes (0/1/2), GHOST→CUT remediation semantics, negate doc-ref defect detector, freshness gate. All tmp-fixture isolated. **26/26 PASS.** |
| `data/coordination/infra_inventory_baseline.json` | Baseline snapshot (atomic `.tmp→replace` write). `--ci` exits non-zero on any severity increase or E/I/W/D True→False flip; GHOST/CEREMONY→CUT counts as remediation, not regression. |

**Registry design decision**: embedded in-script (typed dataclasses) rather than seed YAML — the bright-lines constrain new files to exactly four; registry schema and probe logic must co-evolve in one versioned unit; `--registry <yaml>` preserves the migration path (M16). Two mechanisms were added beyond spec because the first run proved they were necessary:
- **Negated doc-refs** (`DocRef.negate`) — documented requires a keyword ABSENT. Turns "doc cites a nonexistent mechanism" into a mechanical FIX signal.
- **Freshness gates** (`freshness_path` + `freshness_hours`) — implemented requires the mechanism's output file mtime < N hours. Directly encodes the codex-refresh failure class that Carmack caught.

## §2 FIRST-RUN MATRIX (2026-08-25T23:26Z)

```
CONTEXT:        MemoryStore KEEP · memory module KEEP · ContextBuilder KEEP · headroom KEEP ·
                CompactionHarvester KEEP · anchored-summary KEEP · SESSION_ANCHOR KEEP(fresh 0.2h) ·
                session_gnosis KEEP · Hivemind continuation KEEP · HMC Hub v2 KEEP · HMC Watcher CUT
INSTRUCTIONS:   AGENTS.md GHOST · OMEGA_CODEX KEEP · codex freshness KEEP(codex 0.2h old) ·
                agent .md defs KEEP · agent instructions[] FIX · root instructions[] KEEP · scribe GHOST
CONTINUATION:   native compaction KEEP · session_end hook KEEP · lesson staging KEEP ·
                soul_promote KEEP · WAKE_STATE KEEP · handoff/ KEEP · data/handoffs CUT · tutorial KEEP
SUMMARY: KEEP=21 FIX=1 CUT=2 GHOST=2 · CI vs baseline: PASS
```

## §3 FINDINGS — THE REGISTRY EXPOSED REAL DRIFT (including in the audit itself)

### F1. NEW GHOST-CLASS CATCH: the audit's own §0 was stale — HMC Hub is ALIVE
Carmack §0 ruled the HMC Collaboration Hub "Dead by supersession, correctly archived… Verdict: CUT (done)" — based on the archived v1.5.1 July-outage forum. **Ground truth**: `data/coordination/HMC_COLLABORATION_HUB.md` is a live **v2.0** rewrite (2026-08-22, pre-debut, kali-owned, EXECUTION_MINIMAL, pointing at PUBLIC-DEBUT-01). The hub was resurrected three days before the audit declared it dead. My initial seed inherited the audit's verdict and the machine flagged the contradiction within one run. *The inventory audits its auditors.*

### F2. Remediation #1–#4 largely executed same-day (audit → build window ~20:00–20:19 local)
- `hmc_watcher.py` source deleted (stale `.pyc` still in `__pycache__` — cosmetic residue); "HMC Quad-Forge ✅" struck from OMEGA_ENGINE.md.
- `.opencode/agents/scribe.md` deleted — but M11 still cites "Scribe agent" as canonical executor of the scrapped pipeline → residual **GHOST** (de-document or re-document).
- `scripts/soul_promote.py` IMPLEMENTED 20:16 (review-gated, dry-run default, atomic, schema-guarded) — the one-way door is closed.
- Tutorial line 40 rewritten 20:19 to cite the real implementation; OMEGA_CODEX regenerated 20:18; SESSION_ANCHOR rewritten 20:13.

### F3. Remaining open defects (mechanically confirmed, unchanged from audit)
1. **Root AGENTS.md = GHOST** — absent from disk and git history while cited by OMEGA_CODEX/mandates (WP-E).
2. **Agent-level `instructions[]` = FIX** — 12/12 agents carry `instructions[]`, zero `prompt:{file:}` migrations (WP-B2 / GAP-4 exposure class).
3. **Scribe residual GHOST** — SOVEREIGN_MANDATES M11 text outlives the cut agent def.

### F4. Freshness gates now make silent automation death visible
Codex freshness (`OMEGA_CODEX.md <24h`) and anchor freshness (`SESSION_ANCHOR.md <48h`) are wired into `implemented`. If either automation silently dies again — the exact failure that fooled the audit — `--ci` exits non-zero instead of anyone having to notice.

## §4 LIMITATIONS (honesty per M23)
- Wire evidence for doc-only components is reference-based, not execution-based; a cited-but-dead doc still reads W=Y (AGENTS.md correctly lands GHOST via E=N, not via W).
- `soul_promote` W=Y partially self-matches (its own filename under `scripts/`); CLI registration in Makefile would be the stronger signal — not yet present.
- Hivemind continuation store probes only the in-repo cold-store dir; the omega-hub MCP server itself is external to this repo and out of probe reach.
- Freshness gates assume wall-clock hygiene; clock skew or bulk `touch` could mask staleness.

## §5 RECOMMENDED NEXT ACTIONS
1. Consultant integrates (no commit made, per bright lines).
2. Add `check-infra-inventory` Makefile target + wire into `temple-grade` so the gate runs in CI.
3. Resolve F3 items: WP-E (AGENTS.md), WP-B2 (prompt-file migration), M11 Scribe de-documentation (5 min).
4. Sweep stale `__pycache__` residues of deleted sources (`hmc_watcher.cpython-313.pyc`).

---
*Every claim above mechanically derived by scripts/infra_inventory.py at 2026-08-25T23:26Z; baseline frozen at data/coordination/infra_inventory_baseline.json.*
