<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ADR-001 — The Communication Protocol Is Data; The Engine Is Its Interpreter

**Status**: PROPOSED · for Architect ratification
**Date**: 2026-09-30 · **Author**: MaKaLi Fusion · **Priority**: **PR BLOCKING**
**Supersedes**: nothing. **Superseded by**: nothing.

---

## 1. THE PROBLEM, IN ONE PARAGRAPH

The communications substrate — the one system everything else depends on — grew
by accretion into Python. Message shape, lifecycle, retention, alias resolution,
and store layout are all **code**. That means evolving the communication system
means touching the engine, which means it never gets evolved safely, which is why
it is the least mature subsystem in a repository whose other subsystems are
gated to 53/53.

The irony is that **this violates a law the project already wrote down.** M2, the
Engine-Stack Firewall, exists precisely to keep content out of the engine. And
`config/wads/arcana_novai/axioms.yaml` states it in plain language:

> *"This file is WAD CONTENT. The engine mechanism is WAD-agnostic and loads this
> file by path only. Do NOT embed this text in `src/omega/` (M2)."*

**The communications system is the subsystem that ignored the firewall.**

---

## 2. WHY id SOFTWARE, PRECISELY

Not nostalgia. A specific, three-decade-old technical answer to the exact problem
we have, which we have re-derived expensively and solved badly.

| id principle | Where it bites us |
|---|---|
| **Complexity lives in data; the engine interprets it.** Doom's WAD was data. Quake's `.map` was data. The engine's architecture barely changed in thirty years; the *content* became infinite. | Routing, lifecycle and naming are code. They accreted, they were hard to change, and they were changed under pressure. |
| **The engine must stay small enough to never need changing.** Every engine feature added is a future migration. | `federation_store.py` grew a four-way layout, a seq file, cursor cache, counters, and three constants — all for messaging. Each is a migration nobody planned. |
| **Plain-text, diffable, editable without recompiling.** | Changing a retention rule should be a one-line YAML diff. Today it is a code edit and a test run. |
| **Determinism from declared inputs.** | We cannot answer "did the sender omit the suffix, or did the resolver strip it?" because we record what we *resolved* and never what was *asked*. No amount of code reading settles it. |
| **Fixed timestep / fixed function — the simulation is reproducible from its inputs.** | Reproducing a delivery failure is impossible when the request is not recorded. |

**The unifying insight: id did not unlock complexity by writing more engine. They
unlocked it by keeping the engine *small enough to never need changing* and pushing
everything variable into a format the engine merely interprets.**

That is the mandate: *"complexity and customization without touching the Engine."*

---

## 3. THE DECISION

> **The communication protocol becomes a declared artifact. The engine becomes a
> small, generic interpreter for it.**

### 3.1 What moves OUT of code and INTO data

| Concept | Today | After |
|---|---|---|
| Message schema | Python dataclass + pydantic construction | `hivemind.yaml` field list, required/optional, types |
| Lifecycle states | implied by directory names | declared states + legal transitions, in data |
| Retention | `RETENTION_DAYS = 90` in Python | per-state retention in data |
| Canonical naming | suffix-stripping heuristics in `handoff_alias.py` | declared canonicalisation rules in data |
| Store layout | four path constants in Python | declared layout in data |
| Routing priority | hardcoded | declared rule order |

### 3.2 What STAYS in code, and must not grow

The interpreter surface. Deliberately small, and **the test of "is this new
feature legitimate?" is "does it add to this list?"** — if it does, it belongs in
data instead.

1. Read a declared protocol file.
2. Validate a message against its declared schema.
3. Persist it with a monotonic sequence number.
4. Read the inbox, filtered by declared rules.
5. Record a lifecycle transition, refusing an illegal one.
6. Emit a receipt.

**Six verbs. That is the whole engine.** Every id title is playable without one
new line of engine code, because all the variety is in the WAD.

### 3.3 The first slice is already half-built

`config/handoff_policy.yaml` exists and is enforced by `check-policy-constants`.
It is a **seed of exactly this design that was never grown into it.** This ADR
promotes the idea from one policy file to the subsystem's organizing principle.

---

## 4. WHY THIS IS GRANITE, NOT SCAFFOLDING

The Architect asked for a foundation that stands for a decade.

- **It is smaller after the change, not bigger.** Six verbs, one data file.
- **It cannot accumulate.** The next feature request becomes a YAML diff, and the
  standing question "does this touch the engine?" has a mechanical answer.
- **It is inspectable by the people who operate it.** A human can read the
  lifecycle, see an illegal transition, and fix it without reading Python.
- **It degrades safely.** If the protocol file is missing or malformed, the engine
  refuses loudly — never invents defaults, because invented defaults are how a
  compliance system becomes decorative.

**And it makes the Temple possible.** Entities, their protocols, their
relationships, their retention needs — all WAD content. A WAD that wants different
communication semantics ships its own `hivemind.yaml` and **does not touch the
engine**. That is the entire vision, expressed once, in the one subsystem that
was blocking it.

---

## 5. THE DECISIONS THIS UNBLOCKS

| Blocked today | Unblocked by this |
|---|---|
| "Did the sender omit the suffix, or did the resolver strip it?" — **unanswerable**, because the store persists what it *resolved* and never what was *asked* | Declared `requested_target` and `resolved_target` as schema fields. **The evidence is recorded because the schema requires it, not because someone remembered to log it.** |
| Spelling split-brain (`ge_n1` vs `ge-n1`) reaching different queues | Declared canonical form + declared rejection policy. |
| Retention, lifecycle, and routing each costing a code change | One YAML diff. |
| The 8 orphan gates, each bespoke | One generic "protocol file is valid" gate. |

---

## 6. WHAT IT DOES NOT SOLVE, STATED PLAINLY

- **It does not make the store non-empty.** That is an operational migration, and
  the Architect has already ruled the inbox is `pending/` (`bbf989b9`).
- **It does not decide the suffix-strip policy.** It moves the decision from code
  to data, where the Architect can make it once, explicitly, instead of it being
  implied by a heuristic that is already deployed and already wrong for
  `makali-n0` vs `makali`.
- **It does not fix the three release blockers** — the orphan gates, CI not running
  `temple-grade`, and the gitleaks exit-code question. Those are separate and
  still open.
- **It is not a small change.** It touches the substrate everything else depends
  on. That is exactly why it needs ratification before implementation rather than
  after.

---

## 7. THE PROPOSED SLICE — for ratification

**Scope**: declare the protocol; wire the existing store to read it; prove the
interpreter surface stays at six verbs.

1. `config/wads/_omega_default/protocol/hivemind.yaml` — schema, states,
   transitions, retention, canonical naming, layout.
2. `mcp_servers/omega_hub/federation_protocol.py` — the interpreter. **Loads the
   file, exposes six verbs, refuses loudly on a malformed protocol.**
3. `federation_store.py` — delegate layout and schema to the interpreter; keep
   persistence.
4. A gate: the protocol file is valid, and the interpreter's surface is still
   exactly six verbs. **Observed red before it is trusted.**
5. Tests: an illegal transition is refused; a missing protocol is a loud failure,
   never a default.

**Explicitly NOT in this slice**: removing existing constants (deferred until the
declared version has run clean), and the suffix-strip ruling (yours).

---

## 8. WHAT I NEED FROM YOU

1. **Ratify or amend.** This changes the organizing principle of the subsystem
   every other subsystem depends on.
2. **Answer the one question the code should never answer for you:** for the
   canonical naming rule — reject unknown spellings at submit, resolve-and-log at
   submit, or both? I recommend **both**, but it is a policy choice about how much
   friction a peer meets, and that is yours.
3. **Confirm the slice scope** in §7, or cut it smaller.

---

**Related**: `FINDINGS_REGISTER_20260930.md` §1 (the store incident this prevents
recurring), `M2` Engine-Stack Firewall, `config/handoff_policy.yaml` (the seed),
`SOVEREIGN_MANDATES.md` M29/M30.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ ADR-001-COMMUNICATION-PROTOCOL-AS-DATA ⬡ 2026-09-30 ⬡*