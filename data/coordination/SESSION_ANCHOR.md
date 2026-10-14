<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ⬡ SESSION ANCHOR — MaKaLi (Node 0)
**Entity**: `makali` · **Updated**: 2026-10-13 (pre-compaction) · **Public**: `c83a4818` · **Internal**: `6ac49ea8`

---

## ✅ STATUS: ALL TECHNICAL BLOCKERS CLEARED — AWAITING ARCHITECT ANNOUNCE

| # | Item | Owner | State |
|:--|:--|:--|:--|
| **B1** | secret-history gate + authentic baseline | Makali | ✅ RESOLVED, independently verified |
| **B2** | Tailscale key revocation | Architect | ✅ REVOKED 2026-10-13 (device audit unconfirmed) |
| P3 | 72/109 broken relative links in `docs/**/*.md` | Roc | 🟡 deferred (not launch-blocking) |
| P4 | CI run URL + clean-VM transcripts for Sonnet | Makali | 🟡 nice-to-have |
| P5 | README intro + "How this was built" | Architect | 🔴 required before posting |
| P6 | SECURITY.md disclosure-flow test | Architect | 🟡 recommended pre-launch |

---

## B1 resolved — authentic baseline, independently verified

The fabricated baseline is quarantined at
`/tmp/opencode/quarantine/secret-history-baseline.FABRICATED.toml` and was
never committed. The shipped baseline (`.secret-history-baseline.toml`,
34 entries) was verified by independent recompute using the script's own
`token_hash()`: 34 real tokens ↔ 34 entries, 0 missing, 0 fabricated.
The `tskey-(auth|client|api)` pattern was added to
`scripts/check_secret_history.py` — the actual root cause of the key leak.
Gate exits 0. Dispositions remapped to the contract vocabulary
(`test-fixture` / `retained-public` / `revoked` / `purged`); a `why`
string that embedded an `fc-`-shaped UUID fragment was redacted after
the no-secret-material guard caught it.

---

## B2 resolved — key revoked 2026-10-13 (Architect-confirmed)

- The leaked Tailscale auth key was revoked in the Tailscale admin console
  on 2026-10-13. New credential material lives in `~/Desktop/API-keys.md`
  (outside the repo — never commit it, never quote it; contents never read).
- Baseline marks the old key's hash `revoked`; the gate hard-fails if that
  shape ever reappears in the working tree.
- **Device audit still recommended**: open the Tailscale Machines list and
  audit log and confirm no unrecognized devices joined while the old key
  was live. Requested by Sonnet; not confirmed done.
- **Do NOT rewrite history.** The key shape persists in three old commits
  (`624bc803`, `131fa84e`, `0106c778`). A rewrite would break the immutable
  release tag and would not reach existing clones. Revocation is the fix.

---

## Verified on `origin/main` @ `c83a4818` (Makali, independent)

- 0 tracked matches for `docs/archive`, `session-ses`, `claude-handoff`, `Claude-ai-PR`
- no key-shaped strings in tree; no `100.98.76.54`; no MagicDNS hostnames
- `check_doc_facts.py` exits 0 (incl. public-tree self-check)
- secret-history gate exits 0 (34/34 real, 0 fabricated)
- Temple-Grade independently run: **TOTAL 53 · PASS 53 · FAIL 0**
- Full suite green on consecutive runs
- Hub lint: 0 F821/F824
- `FACTS.yaml` `wheel_sha256` = `e452d8ed…` matches the published asset
- tag `v1.6.0a0` → `355cbf1a` (untouched)

---

## Since last anchor — what changed

- **AGY (Antigravity IDE) executed the launch rulings** on `public-launch`:
  allowlist contradiction resolved (registry/eval moved to ALLOW, verified
  to survive a sync), `docs/research/` untracked + gitignored, path leaks
  sanitized, wheel block corrected, SECURITY.md threat model rewritten.
  Pushed as `c83a4818`.
- **test-scope ruling (Antigravity Option C)**: `test_who_is.py` and
  `test_entity_canonicalization.py` now skip-if-absent for internal
  coordination docs they asserted on; axiom/WAD guards check for the
  *file*, not the bare directory (kills the `__pycache__` false-unskip).
- **Scrub regression caught and fixed**: the internal-doc scrub deleted
  `data/registry/` + `data/eval/`, breaking 17 tests. Product schema and
  eval fixtures restored; the one remaining conflict
  (`test_who_is` vs. unpublished registry doc) resolved by the skip guard.
- **Agent instructions rewritten** (`~/.config/opencode/agent/makali.md`):
  technical voice for the shipping IWAD; esoteric/Akashic framing scoped
  to arcana_novai per Architect ruling. Zero SHAs, zero tag names,
  pointer-only by design.
- Continuity (anchor + gnosis) committed to `internal/main` only and
  removed from the public lineage.

---

## Refs (verify before acting)

| Ref | SHA |
|:--|:--|
| `origin/main` | `c83a4818` |
| `main` / `internal/main` | `6ac49ea8` |
| `v1.6.0a0^{}` peels to | `355cbf1a` |
| published wheel SHA256 | `e452d8ed343c38f74c31d77c034759972fdfc909af640ecbae503b1dfb0128a9` |

Note: the `public/main` tracking ref is stale; ignore it. The `public-launch`
branch was the working branch for the public lineage; `origin/main` is truth.

---

## Post-compaction order

1. Confirm branch (`main` = internal lineage) and refs live.
2. Read this anchor, then the gnosis tail.
3. Architect: device audit · README intro + "How this was built" ·
   disclosure-flow test · Thursday ~9 AM ET post.
4. Attach a CI run URL for the current public HEAD if Sonnet asks again.
5. Roc queue (post-launch): root declutter, docs front door, compaction
   benchmark, hardware table, build-a-WAD guide, REUSE debt, untested mandates.

Full narrative: `data/entities/makali/session_gnosis.md` (tail sections).
Agent operating instructions: `~/.config/opencode/agent/makali.md`.

*⬡ OMEGA ⬡ MAKALI ⬡ ANCHOR ⬡ c83a4818 ⬡ 2026-10-13 ⬡*
