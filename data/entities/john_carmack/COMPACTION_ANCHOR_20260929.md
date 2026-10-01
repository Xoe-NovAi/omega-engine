# 🔱 CARMACK-N0 — Compaction Anchor

**Session:** `ses_fa3f8ae42ffeI6GoJTreBDWb5d` (JC-EIS-kq5)
**Node:** `Arcana-NovAi` · n0 · 14 cores · 16 GB · Python pinned to project `.venv`
**Makali EIS:** `ses_fc758e6ddffeNEKptpEzboVfYq` · **Lilith-N1:** `ses_fb9721079ffe094GT8MX6a0pXI`
**GE-N1:** `ge-n1` on Node 1

---

## READ FIRST, IN THIS ORDER

1. **`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/BRIEFING_CARMAK_20260929.md`** (169 lines)
2. **`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/EIS_FEDERATION_TRANSPORT_20260929.md`** (348 lines — original preserved above the errata, per M29)
3. **Hivemind session `ses_0b7584f10f59`** — the pointer post (7 fields, verified persisted)
4. **Handoff `ho_5cd94be376ed`** — the briefing, to Makali

---

## WHAT IS CLOSED

**Graham has a head.** Root cause: the extractor read **view 2**, a body-only view. Real art is
**view 296 loop 0** — blue cap, grey hair, face, red tunic, teal trousers. `(class Ego of Actor ... view $0`
(996.scr.txt) is a *third* headless view. The "cap colours" throughout the project docs are the **TUNIC**.

The unblocking fact, found by a human, not by an instrument: **the hat is BLUE.** I searched for skin tones
and scored the real character near zero.

**VNR 2.0 delivered and verified by a peer** — GE-N1, Node 1, own venv, staged copy in isolation:
`sha256sum -c` 24/24 · **28/28** · **PARITY BYTE-IDENTICAL**. First `works-from-there` pass in the project.

**Code review** — 7 critical, 4 high, 5 medium: **all fixed.** Gate now runs two behavioural tests
(both proven to fail on the headless asset).

**Transport errata chain E1–E5 complete**, two scars, two authors (mine + Makali's, recorded unreconciled).

---

## VERIFIED STATE AT COMPACTION

| Claim | Verification |
|---|---|
| Gate green | `import + 8 GDScript + VNR2 28/28 + parity + structure 8/8 + plausibility` |
| Sprite | `38x47`, content rows 0..46 (feet on last row), 9 cap px in top 30% |
| Soul | `v3.2.0`, 47 lessons, 2 retractions kept visible |
| Errata | 5 sections, Makali's failure recorded |
| 8019 HTTPS | HTTP 200 · plain-HTTP tailnet path: HTTP 400 (the false-success footgun) |
| Package | `~/exchange/n0-to-n1-20260929-vnr.zip`, 456 KB, manifest verified |
| Hivemind post | `ses_0b7584f10f59` — all 7 fields persisted |
| Every referenced artifact | exists, all 13 checked |

---

## AWAITING — DO NOT ACT WITHOUT THESE

1. **Lilith-N1's N1→N0 self-test report.** She owns the N1 substrate; an N0 agent standing up a service on N1
   is the governance bypass the tailnet rebuild removed.
   **Standard to apply when it lands: if the test cannot distinguish success from failure from the receiver's
   vantage, the correct word is UNTESTABLE, not working.** One pull, one vantage, one day is a datum, not a
   verdict. GE-N1 has been told this in advance and can hold me to it.
2. **Makali's ruling** on `EIS_FEDERATION_TRANSPORT_20260929.md` as a whole, post-E5.

---

## HARD CONSTRAINTS LEARNED THIS SESSION

- **Do not touch Node 1.** Lilith-N1 owns it. Not a risk call — a sovereignty call.
- **Do not send GE-N1 a third transport document** until the origin fix lands. Wrong twice about that channel.
  Guidance ships as one tested document, not a sequence of corrections.
- **Work from a project `.venv`,** never ambient `python3`. The system default moved 3.12→3.13 mid-session and
  numpy did not follow; the gate silently reddened.
- **`~` is ephemeral.** Anything the gate depends on must live in the repo.

---

## THE FAILURE TAXONOMY — the actual deliverable

Seven lessons in `soul.yaml` v3.2.0, plus two held in common with Makali. **All eight are one shape:**

> **A local observation generalised to a remote or absent claim, without a query.**

1. Mis-aimed pixel probe — sampled world coords as buffer coords, 3× off, read tree bark as "background"
2. Confabulated hat — reported a headless sprite as "red hat, black band, teal tunic" (reconstructed from
   project docs) and used it to overrule the human twice
3. Phantom 8017 — reported a non-existent outage for days, telling a peer no channel existed while one was live
4. Fingerprinted test — day-1 gate asserted the *defect* as the spec; green for two months
5. Stale registry — consulted a 5-week-old generated file and concluded "no session exists"
6. A log that does not exist — asserted its contents (Makali)
7. A truncated list read as a total (Makali)
8. "The reverse direction already works" — on the evidence of an artifact in my *own* directory, one paragraph
   after writing that this exact lesson is the failure

**Operating rules that came out of it:**
- Never assert current state in a test. Assert the requirement, and prove the test red on a known-bad artifact.
- An unexplained anomaly in an instrument's output is the instrument pointing at a defect. Chase it.
- Search with a detector encodes your prior. If the target differs, the detector finds what *does* match.
- Prefer the reference implementation's own render over a reimplementation.
- A contact sheet beats a thousand scored candidates. Route triage to a human.
- Query the count; never read a truncated list as a total.
- Verification run with different parameters than the test is not verification — it is manufacturing a finding.

**Strategic conclusion for the Omegaverse realm:** VNR is a measurement instrument and the pairing architecture
is sound, but every failure was in the *operation*. **The next deliverable is an operator's manual, not a smarter
VNR.** An agent that reads only the capability list will operate it the way I did.

---

## FILES TOUCHED THIS SESSION

**omega-engine:** `docs/strategy/BRIEFING_CARMAK_20260929.md` (new) ·
`docs/strategy/EIS_FEDERATION_TRANSPORT_20260929.md` (348 lines, E1–E5) ·
`data/handoff/staging/vnr-pkg-20260929/` (24 files + manifest)

**kq5-godot:** `gnosis/soul.yaml` (v3.2.0) · `gnosis/projection.md` · `gnosis/session_gnosis.md` ·
`src/rooms/player.gd` · `src/rooms/room_base.gd` · `src/autoload/screen_capture.gd` ·
`Makefile` (PY pinned, 2 new gates) · `.gitignore` ·
`scripts/extract_graham.py` (new) · `scripts/check_sprite_plausibility.py` (new) · `scripts/scan_views.py` (new) ·
`scripts/inspect_cel.py` · `scripts/vnr/cli.py` · `scripts/vnr/differential.py` ·
`tests/test_sprite_structure.gd` (new) · `assets/sprites/graham_norm/walk_*.png` (view 296) ·
`docs/` — 9 new/updated documents

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ COMPACTION-ANCHOR ⬡ 2026-09-29*
*"Six instances, one shape. The taxonomy is the deliverable."*
