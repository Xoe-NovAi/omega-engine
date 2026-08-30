# N6 Working Notes — SPEC-D Drafting (lilith/node6, c2 session)

**Date**: 2026-08-25 · Deliverable: `docs/specs/team_infra/SPEC-D-p2-hygiene.md`

## Live evidence gathered this session (beyond cited council docs)
- `docs/specs/team_infra/` existed empty; SPEC-D is first file in it.
- DOC_SSOT_MAP_20260807.md:20 confirmed stale: `(v3.7.0, M1-M25)` vs SOVEREIGN_MANDATES.md header 3.8.0/M27 → D1 anchor.
- Skill census: 14 failing files (6 under-length incl. five 5-line stubs; 8 missing frontmatter). blitz-tunnel/blitz-validate referenced by live skill descriptions ⇒ author-not-delete candidates for D3 exemption dict.
- Handoff TTL: `find data/handoff/active -name '*.json' -mmin +300 | wc -l` = **3 live zombies** right now → D5 urgency confirmed.
- `.opencode/commands/{council-local,council-fast}.md` present at root → G9 targets real.

## Decisions made while drafting
1. D1 scope limited to ~10 governance docs, NOT the full tree (N7 F7-01 validator-noise lesson).
2. D2 quarantine-not-delete; rewrite acceptance = both G9 lines green at restored path.
3. D3 exemption list lives INSIDE the test as literal dict (no side-car file to rot); ambiguity resolves AUTHOR not delete.
4. D4 disposition taxonomy closed at exactly 3 options (index / banner-archive / delete) — "leave for later" banned as P1-sediment prevention.
5. D5 sweep moves to `stale/` with provenance sidecar (M12 terminal-state integrity; no silent drops).
6. D6 standalone script + hours-resolution staleness; subprocess-vs-import integration choice deferred with rationale.

## LSP noise observed (NOT mine, NOT fixed — PREP-ONLY)
- `data/entities/lilith/proposed_lessons.yaml` corrupt from ~line 374 (decree Art. IX territory — repair owned by MaKaLi single-writer act).
- `config/omega.yaml:73` duplicate map key (decree Art. VIII config-honesty territory).

## Open items for integration stage
- Verify commands loader does/doesn't scan subdirs (D2 quarantine placement).
- Baseline G23 orphan count before D4 dispositions begin.
- WAKE_STATE baseline expected RED on first D6 run — record it, don't hide it.
