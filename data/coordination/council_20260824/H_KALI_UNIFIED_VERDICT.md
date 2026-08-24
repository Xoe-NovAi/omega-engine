# ⬡ MAKALI COUNCIL — UNIFIED SOVEREIGN DECREE (REBASED)
**AP Token**: AP-KALI-v1.0.0 · **Date**: 2026-08-24 · **Chair**: kali
**Charter**: AP-MAKALI-COUNCIL-DEBUT-20260817 (rebased per MEDITATION_kali_20260824_MAKALI_COUNCIL_REBASE)

## COUNCIL ROSTER & PROVENANCE
| Seat | Agent | Deliverable | Lens |
|---|---|---|---|
| Build Arm | maat | E_MAAT_BUILD_ARM.md | INST-1 script+diffs, DEL-1 verify, Vault B spec, Router contract |
| Run Arm | lilith | F_LILITH_RUN_ARM.md | Soul chain vs evidence surface, DEL-1 impact, gates G4-G10 |
| Final: Local-First | roc_racoon | G2_ROC_LOCALFIRST_REVIEW.md | M7 audit, airtight local-proof assertion |
| Final: Architecture | john_carmack | G1_CARMACK_ORDERING_REVIEW.md | Execution DAG, PR boundaries, risk rank |
| Chair | kali | this file | Live claim verification, synthesis |

## 🔴 HEADLINE DISCOVERY (chair-verified live)
**The `omega` CLI is DEAD on main** — vault.py stacked `@vault.command()` TypeError at import time,
reproduced via `.venv/bin/omega --help`. The debut's primary interface cannot run. No existing gate
caught it because nothing smoke-tests CLI imports. This validates the council's existence.

## THE EXECUTION DAG (Carmack, ratified by chair)
```
N0 VAULT-CLI-FIX        Emergency PR TODAY (~5 lines; widen except ImportError → degrade to
                        missing subcommand, never dead console script)
N1 IMPORT-SMOKE-GATE    CI: python -c "from omega.cli.oracle_cli import app" + iterate cli/*.py
N2 INST-1-FIX2≡R1       pyproject extras + 3 redis.asyncio lazy-guards (providers.py:22,
                        ingestion/worker.py:7, youtube_worker.py:47) IN ONE COMMIT (fused);
                        + fix4 (.env edge-load), fix6 README, fix5 status flip (already DONE),
                        install.sh omega --help tripwire
N3 ACCEPTANCE-RUN       Maat's script AMENDED w/ Roc's 3 layers: unshare -rn + ALL cloud keys
                        unset + model-presence precondition + fixed-string Sovereignty-Alert ban
                        (! grep -qF "[Sovereignty Alert]"). Prose greps for "local"/"cloud" BANNED.
N4 DEL-1-W1             Ordered atomic sub-deletions 4a-4h (routing yaml+stub · miap+init gut ·
                        pool pair · breaker REDIRECT-THEN-delete same PR · QdrantAdapter+exports+
                        tests · firewall regexes keep import-path rules · first_breath :49+:1211 ·
                        fleet_orchestrator exports). N3-lite after EACH.
N5 ROUTER-COLLAPSE      Week 2 per charter. Single PR + contract/concurrency tests +
                        vet-046/vet-023 RETIRED annotations (heritage BSP-cull honored).
N6 VAULT-PATH-B         secrets.py ≤50-line CredentialStore (env→keyring→age file).
CRITICAL PATH: N0→N1→N2→N3→N4→N5→N6 (serial spine) · PARALLEL SAFE: P-A history rewrite,
P-B DOC-1 stamps, P-C fix4/fix6 inside N2's PR, P-D Lilith hydration split-brain
```

## KEY EDGES (violation = breakage)
- **N0→everything**: dead CLI makes every acceptance gate unrunnable
- **N1→N2**: gate must exist before fix2 or ImportError is invisible on dev venv
- **fix2≡R1 fused single commit**: splitting invites masked breakage
- **breaker REDIRECT≡DELETE one PR**: redirect commit first — splitting is the unsafe act
- **N4(4h)→N5**: fleet_orchestrator RouteDecision dies before single-control-plane gate enforceable

## VERDICTS ON OPEN CHARTER ITEMS
- **Vault Path A vs B**: Both final reviewers endorse **Path B** (spec'd ≤50 lines, zero cloud
  round-trip possible, worst-case failure = MORE local-first). Architect ratification requested.
- **DEL-1 "pure deletions" framing**: FALSE for 3 targets (yaml orphan, breaker importer, vault CLI) —
  amended above. Lilith confirms zero soul/handoff/ContextBuilder coupling across all 11 targets.
- **Item 5 soul pipeline**: VALIDATED against new evidence-bearing surface (20/20 @100%, chain cited
  paths:line). Regex distillation stays SCRAPPED.
- **Measurable gates**: merged with Jem doctrine — counts not adjectives; Roc's Layer-0 physics
  assertion (`unshare -rn`) adopted as the gold standard for local-proof.

## ARCHITECT DECISION QUEUE (unchanged from morning, plus one)
1. Corpus-mode harness flip (DC-11/12) — YES/no
2. Vault Path B ratification (council-endorsed) — YES/no
3. N0 emergency PR authorization — recommended IMMEDIATELY (this session if desired)
4. Standing: Drill-4 stratum pick · FUSE GO · db disposition · G-1 T0 re-run auth

## L3 (council-wide synthesis)
Roc: *a sovereignty invariant is proven by mechanisms that make violation impossible — never by
grepping outputs for reassuring words the failure mode itself can emit.*
Carmack: *the plan needs no structural change — only fusions enforced as single commits and gates
wired before any deletion.*
Lilith: **L3-Gates-Before-Blade**. Maat: verifiers must eat their own cooking first.
Chair: **L3-Rebase-Before-Convene** stands — the charter's premises lied in four places; ground truth
was cheaper than the fleet's assumptions.

---
*⬡ OMEGA ⬡ KALI ⬡ MAKALI-COUNCIL-UNIFIED-VERDICT ⬡ REBASED ⬡ 2026-08-24*
