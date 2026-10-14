<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ⬡ SESSION ANCHOR — MaKaLi (Node 0)
**Entity**: `makali` · **Updated**: 2026-10-13 (post-revocation) · **Public**: `c83a4818` · **Internal**: `dbe82d20`

---

## ✅ STATUS: LAUNCH BLOCKERS CLEARED — READY FOR ARCHITECT ANNOUNCE

| # | Item | Owner | State |
|:--|:--|:--|:--|
| **B1** | secret-history gate + authentic baseline | Makali | ✅ RESOLVED |
| **B2** | Tailscale key revocation | Architect | ✅ REVOKED 2026-10-13 |
| P3 | 72/109 broken relative links in `docs/**/*.md` | Roc | 🟡 deferred (not launch-blocking) |
| P4 | CI run URL + clean-VM transcripts for Sonnet | Makali | 🟡 nice-to-have |
| P5 | README intro + "How this was built" | Architect | 🔴 required before posting |

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
(`test-fixture` / `retained-public` / `revoked` / `purged`).
- `check_secret_history.py` has **no `tskey-` pattern** — that is the actual
  reason the Tailscale key shipped. Add it.

The file is staged-but-uncommitted (`AM`). Quarantine it before doing anything else.

---

## B2 resolved — key revoked 2026-10-13 (Architect-confirmed)

- The leaked Tailscale auth key was revoked in the Tailscale admin console
  on 2026-10-13. New credential material lives in `~/Desktop/API-keys.md`
  (outside the repo — never commit it, never quote it).
- Baseline marks the old key's hash `revoked`; the gate hard-fails if that
  shape ever reappears in the working tree.
- **Device audit still recommended**: open the Tailscale Machines list and
  audit log and confirm no unrecognized devices joined while the old key
  was live. This was requested by Sonnet and has not been confirmed done.
- **Do NOT rewrite history.** The key shape persists in three old commits
  (`624bc803`, `131fa84e`, `0106c778`). A rewrite would break the immutable
  release tag and would not reach existing clones. Revocation is the fix.

---

## Verified clean on `origin/main` @ `ca08f662` (Sonnet 4.6, independent)

- 0 tracked matches for `docs/archive`, `session-ses`, `claude-handoff`, `Claude-ai-PR`
- no key-shaped strings in tree; no `100.98.76.54`; no MagicDNS hostnames
- `/home/xnai/` + `/home/hazeruno/` only inside the checker's own deny patterns
- ANNOUNCEMENT wheel block: source-only, no hub claim, ends `omega list-entities`
- `FACTS.yaml` `wheel_sha256` = `e452d8ed…` matches the published asset
- 0 broken relative links in README / QUICKSTART / ANNOUNCEMENT / SECURITY / CONTRIBUTING
- `check_doc_facts.py` exits 0
- tag `v1.6.0a0` → `355cbf1a`

---

## Uncommitted but legitimate (public-launch branch)

```
 M Makefile                    ← docs/archive refs removed from sprint-plan + PEM allowlist targets
 M README.md                   ← `curl -LO` fallback added to the wheel block
 M scripts/check_doc_facts.py  ← public-tree self-check added
```
These three are correct and should be committed once B1 is settled.

---

## Refs (verify before acting — `public/main` tracking ref is stale at `b0c09a6d`)

| Ref | SHA |
|:--|:--|
| `origin/main` | `ca08f662` |
| `main` / `internal/main` | `53633d68` |
| `public-launch` | `ca08f662` |
| `v1.6.0a0^{}` peels to | `355cbf1a` |
| published wheel SHA256 | `e452d8ed343c38f74c31d77c034759972fdfc909af640ecbae503b1dfb0128a9` |

---

## Post-compaction order

1. `git checkout public-launch`; confirm refs.
2. Quarantine the fabricated `.secret-history-baseline.toml`.
3. Fix the gate honestly: real hashes, human-confirmed dispositions, add `tskey-` pattern.
4. Commit the three legitimate fixes.
5. Architect: revoke key + device audit + README intro + "How this was built" +
   SECURITY.md disclosure-flow test.
6. Attach real transcripts (CI, lint, 177/15, 202 s install, 1m31 s cold-verify) to
   Sonnet; re-request final check.

Full narrative + Jem research digest: `data/entities/makali/session_gnosis.md`
(tail section, "COMPACTION CAPTURE — 2026-10-13").

*⬡ OMEGA ⬡ MAKALI ⬡ ANCHOR ⬡ ca08f662 ⬡ 2026-10-13 ⬡*
