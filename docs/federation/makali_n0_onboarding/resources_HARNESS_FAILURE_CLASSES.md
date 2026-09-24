# Harness Failure Classes & Quality Gates — What Breaks, and the Guards

**Document ID:** `FED-MAKALI-N0-GUARDS-20260925-01`
**From:** Lilith-N1 / Build (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-25
**Handling:** Operational doctrine. Safe to share freely.
**Fills gap:** the pack described *what* we built but not the **failure classes we
hit** or the **automated gates that keep them from recurring.**
**Source of truth:** `docs/CODE_QUALITY.md`, `docs/PRIVACY_SECURITY.md`,
`docs/OPENCODE_FOUNDATION.md`, `Makefile`.

---

## 0. The Doctrine in One Line

> Every guard in this document exists because something **broke or nearly broke** —
> recorded as a rule so the next session does not re-buy the lesson.

This is the closed loop: *incident → rule → automated gate → test*. If a rule has no
gate, it will be violated by a tired agent at 2am.

---

## 1. Failure Class: Background Work Is Reaped

**What happens:** an agent-launched shell process is killed when the tool call ends
(timeout, completion, or abort) — because the harness reaps the **child process group**.

| Survival mechanism | Survives call end? | Verdict |
|---|---|---|
| `cmd &` | ❌ | never relied on |
| `nohup ... &` | ❌ **proven dead** (frozen at 68MB) | ignores SIGHUP, not group SIGTERM |
| `setsid ...` | ✅ mostly | own session; acceptable fallback |
| `systemd-run --user` | ✅ **definitive** | owned by user manager; survives call ends, aborts, logout (`Linger=yes`); journal-logged; `MemoryMax=` captable |

**Rule:** any agent-launched work expected to outlive a tool call uses
`systemd-run --user`. Full treatment: `resources_FAST_FETCH_LAYER.md`.

---

## 2. Failure Class: Unbounded Reasoning

**Two distinct bugs, same root: the model is allowed to spend a budget you did
not bound — or binds it to the wrong thing.**

| Bug | Symptom | Guard |
|---|---|---|
| **Hang** — `num_predict` unset (Ollama default = unbounded) | reasoning model never emits EOS → request runs forever | `--num-predict 512` default + JSON metadata |
| **Empty answer** — thinking on under a small budget | 512 tokens consumed by internal trace → `response: ""`, telemetry still looks fine | explicit `think:false`; `--think {on,off}` CLI, default `off`, mode recorded in results |

**Rule:** never call `/api/generate` on a reasoning model without an explicit
`num_predict`; never assume thinking mode without checking the response body.
Detail: `resources_MODEL_EVALUATION_LAB.md` §2–3.

---

## 3. Failure Class: Hardcoded Hostile Limits

**What happens:** hosted model aliases rotate (stealth aliases, changing vendors),
and any context/output/modality/identity limit written into config **rots**. We were
burned within a day: a custom 1M-window override matched reality (sessions at
205.8K+ tokens) — then the provider moved the model to 200K and the override
silently became a lie.

**Rule (standing):**
> **Never hardcode context, output, modality, or identity limits for rotating
> aliases. Select the stable alias and refresh live runtime metadata.**
> Validate every agent field against the **live schema** (`prompt` with
> `{file:...}` — not `system_prompt`, not undocumented `inherit_context`/
> `allow_background_execution` keys).

**Drift detection:** `scripts/opencode_provider_doctor.sh` diff-checks our
assumptions against live `models.dev`. Doctrine, not config, is the defense.

---

## 4. Quality Gates (Automated, Run Before Every Commit)

`make lint` runs **all** of these:

| Gate | Rejects | Source |
|---|---|---|
| **anyio purity** (highest priority) | bare `import asyncio` / `import trio` in first-party code | `docs/CODE_QUALITY.md` §1 |
| **No bare exceptions** | `except:` with no type; swallowed errors without traceability | §2 |
| **No torch** | `import torch` anywhere in tracked code | §1 |
| **Model card validation** | missing required section (`## Local Measurement`, `## Provider Claims`, `## Omega Verdict`), invalid evidence label | `scripts/validate_model_cards.py` |
| **Secrets** | credentials/tokens in tracked files | `tests/test_secrets.py` |
| **Docs integrity** | broken README/doc links | `make docs` |

**Why "absolute anyio":** mixed async runtimes (asyncio + trio + anyio adapters)
produce subtle context- and cancellation-mismatch bugs. One runtime, chosen
deliberately: **anyio**.

`make test` runs the regression suite (repo hygiene, gnosis, The Well, OMER, privacy,
continuity, leash/watchdog — **88 tests** as of 2026-09-23).

**The honesty rule that matters most:** when gates fail because of **someone else's
in-flight work**, report the exact failure and leave the unrelated file alone —
**never** silence, skip, or "fix" a gate to get a green run. A hidden red gate is
worse than a visible one.

*Live example from this pack's own assembly (2026-09-24):* `make lint` failed on a
bare `import asyncio` in an untracked `scripts/embedding_server.py`, and `make test`
caught gnosis-ledger drift (46 manifests vs 40 rows, outside the ±5 tolerance).
Both were **named in the report and then fixed at the source** — the bare-`asyncio`
usage removed from the server script, the ledger reconciled — rather than excluded
from the scan. Gates are now green (88/88, 6/6 cards). *The gates caught real
defects in the tree they were protecting; that is the point.*

---

## 5. Repo State Discipline

- **Commit only on explicit operator request.** Work products are left staged/unstaged
  until asked.
- **Do not clobber concurrent work.** Other sessions/agents may hold uncommitted
  changes in the same tree; edit surgically, verify with `git diff`, never blanket-restore.
- **Report, do not hide:** full-gate failures from unrelated work are stated plainly
  alongside the targeted checks that *did* pass.

---

## 6. Privacy Tier Doctrine

Not a gate — a **standing policy** (see `docs/PRIVACY_SECURITY.md`):

| Class | Route |
|---|---|
| `PUBLIC` — benchmarks, docs, open research | any route incl. free tiers |
| `PERSONAL` — journals, dreams, personal gnosis, shadow-work, private correspondence | **local only**, or **paid zero-retention** route with explicit operator approval |

**The trap:** free hosted tiers ("Zen free", contributor free, trial endpoints)
collect prompt data or train on it. **Zero price ≠ private.** A provider's
zero-retention claim is *dated evidence about a rotating alias*, not a permanent
property.

**Consequence for the pack you are reading:** private Lilith material moves by
**USB / physical handoff**, never by hosted provider. This README is already
scoped as personal/proprietary for that reason.

---

## 7. N0 Adoption Checklist

- [ ] Mirror `make lint` + `make test` gates in N0's repo (same rule set, own tree).
- [ ] Install `scripts/validate_model_cards.py` gating before any model card lands.
- [ ] Apply the no-hardcoded-limits rule to N0's OpenCode config before the first
      alias rotation.
- [ ] Adopt the process-group rule for any background work launched by an agent.
- [ ] Enforce `num_predict` + explicit `think` on every generate call.
- [ ] Adopt the privacy tier table before handling any of the N0-8 personal corpus.

---

**Provenance:** every failure class above was observed live on Node 1 and recorded
as a rule. **Evidence label:** local measurement (gates/tests) + incident record.
