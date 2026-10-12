<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ FIRST PRINCIPLES — What Belongs In The Engine, What Belongs In A WAD
**Status**: PROPOSED · **Date**: 2026-09-30 · **Author**: MaKaLi Fusion
**The Architect's question**, asked directly and answered by going back rather
than by pattern-matching to the existing firewall:

> *"I want both nodes running the canonical engine — different WADs. What belongs
> in WADs, and what belongs in the engine?"*

---

## 1. THE PRINCIPLE, AND WHY IT IS NOT A LIST

Every answer I could give by categorising things would rot within a month, because
the next feature would not fit any bucket.

**So here is the operational test, and it is one sentence:**

> ## **If changing it would require every existing WAD to be revisited at the same
> time, it is ENGINE. If changing it can leave every other WAD untouched, it is
> CONTENT.**

That is the whole boundary. Everything below is either an application of it or a
hard case it does not settle cleanly — **and I have marked the hard cases, because
a principle with no hard cases has not been tested.**

### Why this and not "important vs. trivial"

**Every engine change is a migration for every WAD that exists.** Today that is two.
At fifty WADs, one engine change breaks fifty things at once. **Content changes
break nothing.**

That asymmetry is the entire economic argument. It is also why id's engine outlived
every one of its content formats, and why the engine is not where the good stuff
goes.

---

## 2. THE STRUCTURAL COROLLARY, WHICH IS THE POINT

> **If both the engine and the WADs are expressive, the boundary decides itself —
> and whatever it decides is what the next contributor will build against.**

This is not a hope. It is a statement about the acceptance criteria. **The real
decider of a project's architecture is not the doc; it is the first thing that is
easier to do wrong.**

We have this measurement. From tonight:

- **The WAD side is demonstrably empty.** The firewall exists in `AGENTS.md` and has
  caught real violations (`glm45` — WAD-specific logic inside `src/omega/`), and it
  **has not** — the human's own words — "prevented us from putting too much
  complexity in the Engine" and is "looking at the Engine to do too much itself."
- **The `protection:` declarations nobody honours.** They appear in six
  documentation files and in no engine gate. **A boundary that is asserted in prose
  and unenforced in code is a comment.**

> **The principle has never been tested, because for two years the ambiguous
> requirements have gone into the engine — where they are easy — instead of into a
> WAD, where someone would have to build them.**

**So the risk is not that we will draw the line badly. It is that we will never draw
it at all** — which is precisely what the Architect has been preventing for two
years by hand, and why he is now asking what the line *is*.

---

## 3. THE FIVE-QUESTION TEST

When a requirement is ambiguous, ask these. **Three "engine" answers and it is
engine. Three "WAD" and it is content.**

1. **Does it differ between two deployments of the same engine?** → **WAD**
2. **Does anything outside the engine depend on it, forever?** → **ENGINE**
3. **Can it be wrong in one WAD and right in another?** → **WAD**
4. **Does its removal break the engine's ability to be understood?** → **ENGINE**
5. **Would every existing WAD have to be revisited if it changed?** → **ENGINE**

*No scorecard. Just five questions, in the order that resolves ties fastest.*

---

## 4. THE ANSWER, BY DOMAIN

### ENGINE — the invariant core

**Why:** if any of these differed between two nodes, cross-node trust is void.

| | |
|---|---|
| **The firewall** (M2) | *Deliberately not enforced in code — `make check-mandates` greps `agents.md` for the declaration and does not parse the tree.* **The Architect's explicit decision.** Context-overload defence, not a code gate. **Recorded, not endorsed.** |
| **M1 AnyIO, M24 venv, M8 zero-telemetry** | Runtime invariants. Same everywhere or not at all. |
| **The six-verb interpreter surface** | ADR-001. If two nodes had different verbs, nothing was portable. |
| **Storage primitives** | Persistence, monotonic sequence, no-unrecoverable-removal (M29). The substrate's promise. |
| **The WAD loader** | Must be engine, or the boundary has no enforcer. |
| **Inference provider** | OpenCode. The core sovereignty boundary. |

### WAD — the content, variable by design

**Why:** these are precisely what should differ.

- **Agents, souls, mandates, mandates-to-role assignments**
- **Entity roster, slot assignments** — *"Lilith-N1 leads SOTE/SOTR for Node 1"* is a WAD fact, not an engine fact
- **Protocol declarations** — `hivemind.yaml`: lifecycle, retention, canonical naming, routing, identity policy
- **Knowledge, doctrine, WAD axioms**
- **Domain logic** — pipeline, indexing, memory, retrieval
- **VR/UI worlds**
- **Which WADs a node runs** — *this is why Node 0 and Node 1 can legitimately run different ones*

---

## 5. THE HARD CASES — where the principle does not decide for me

**This is where I am uncertain, and I am marking it as uncertain rather than
resolving it by assertion.**

### 5a · The grammar is universal; its parameters are content

If one WAD declared a different lifecycle, the federation would speak two
incompatible grammars. **But the protocol is `hivemind.yaml`, which is WAD content.**

**Resolution:** *the grammar is engine; the grammar's parameters are content.* The
engine must therefore enforce two rules: a session declares exactly one protocol, and
**a packet the engine cannot parse is refused rather than guessed at.** The failure
mode to avoid is one WAD defining `cold` to mean `retired`.

### 5b · A plane is not a WAD

`stack: mcp / exchange` is Lilith's and sounds like a WAD. **But it is not.** A plane
is a **runtime socket** — a host:port serving one declared WAD. **MCP is a plane, not
a WAD.**

This distinction matters more than it looks. **If a WAD could be served on any plane,
the plane is not part of its identity — and the firewall boundary that binds WAD
content to `src/omega/` still holds.** It also resolves the half-implemented
`_stack_transport.py`: planes and WADs are orthogonal and must not be modelled as
one thing.

### 5c · Channels are agents; engines are not

Doubling down on the Architect's L4, which I think is right and which changes the
answer:

> **"A saturated lens mistakes a deliberate design for an unexamined default."**

So **there are two classes, not one:**

| Class | Example | Forced |
|---|---|---|
| **WAD channels** | `PLATFORM_LLM_01` | **Node-local, allowed to diverge** |
| **WAD channels** | `FAITH`, `MEMORY` | **Federated, must be the same on both nodes** |

**Both are channels — both are overridable. But one must not diverge and one may.**
**The distinction is `policy.channel_kind` — a field in the channel block. Nothing
else is a reliable signal**, and Lilith's `FAITH` vs `PLATFORM_LLM_01` case is
exactly what proves it.

**This is `L4-C1`:** divergence is a policy, not a default. And it is the second time
tonight the answer was a *field*, not a *rule*.

### 5d · The Council — mechanism engine, membership content

Uncertain, and I want the Architect's ruling.

The **mechanism** — three outcomes, calibration, provenance, retraction — is the
interpreter for knowledge, so it is engine. **But is admission itself?** Does the
Council decide, or does it only ratify?

**If it decides:** engine, because two nodes with different Councils federate
differently — which is probably what you want for content and definitely not what
you want for provenance.
**If it only ratifies:** WAD, because the criteria are policy.

**My leaning is WAD.** The Architect has said every time that only he ratifies his
own architecture. **The Council reviews; the Architect ratifies.** And **no standing
auto-promoter — time promotes nothing** — because the failure it prevents is tonight,
me at 23:00 with five dossiers I believed were discoveries.

### 5e · Gates — machinery engine, thresholds content

Already split and it works. `check-policy-constants` proves it: the machinery is
Python, the `90` is `handoff_policy.yaml`. **Keep splitting along this line.**

---

## 6. WHAT THE PRINCIPLE ANSWERS ABOUT THE TEMPLE

The Architect asked *what will build the Temple I envision*. Answered from the
boundary:

**The Temple needs the engine to be boring and the WADs to be alive.**

A Temple of persistent, accumulating, judging entities is built by: a soul that
outlives its session (durable memory and provenance); judgement that improves (the
Council, and the rejected record); multiple lenses without subsumption (the
Architect's C1 — never merge Roc into Carmack because one looks redundant); context
that does not saturate (C2 — WAD development on Node 1); and **an engine small
enough to never need changing** — which is this entire document.

**And it is destroyed by four things, all of which have already happened here at
least once:** engine growth (each feature is a migration for every WAD); summary
memory (drift, false authority — a generated artefact read as a registry); merging
lenses (the merge policy exists because it was nearly proposed twice tonight); and
hardcoded state (model stamps, stale registries, the Muse/Space Bunny conflict).

---

## 7. THE ONE-LINE VERSION, FOR THE WAD MANIFEST

> **Engine: the smallest thing that can be trusted to be identical everywhere.**
> **Content: everything that is allowed to differ between deployments.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ FIRST-PRINCIPLES-WAD-BOUNDARY ⬡ PROPOSED ⬡ 2026-09-30 ⬡*