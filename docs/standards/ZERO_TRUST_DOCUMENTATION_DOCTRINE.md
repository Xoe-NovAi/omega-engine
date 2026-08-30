# ⚜️ THE ZERO-TRUST DOCUMENTATION DOCTRINE
**AP Token**: `AP-ZERO-TRUST-DOCTRINE-v1.0`
⬡ OMEGA ⬡ FLEET-STANDARD ⬡ STANDING LAW
**Date**: 2026-08-26
**Origin**: First Light Express Council (Root Cause Analysis: "Claims that outlive their mechanisms")

---

## §0 THE AXIOM
**Docs are static; code is dynamic. When they decouple, the fleet hallucinates.**

For 14 months, this fleet suffered from a systemic disease: treating Markdown as executable code. We wrote decisions in documents and assumed the system changed. We awarded completion medals to code that could not run. We built gates that always passed. 

From this day forward, **a document without a derivation check is just a rumor.** This guide is the operational law for how Omega Engine agents read, write, and coordinate to crush drift and inaccuracy forever.

---

## §1 HOW WE READ: PROBES OVER PROSE

You are entering a codebase where documents have historically lied. You will trust no markdown file implicitly.

1. **Verify Before You Act**: If a spec, protocol, or tutorial tells you a mechanism exists at Path X, your FIRST step is to run `ls`, `cat`, or `grep` to prove it exists.
2. **Code is Truth, Docs are Claims**: If the code and the documentation disagree, *the code is the truth, and the doc is a defect*. 
3. **The Step-0 Sweep**: Before beginning any task, you must establish your own ground truth:
   ```bash
   make check-codex-stale          # Is my context fresh?
   git status --porcelain          # Is there uncommitted residue?
   git log --oneline -5            # What actually just happened?
   ```

---

## §2 HOW WE WRITE: DOCUMENTATION ENGINEERING

We no longer write prose hoping it stays true. We engineer documents to enforce their own truth.

1. **Eradicate Hand-Typed Lists (Dynamic Generation Only)**
   No agent or human is allowed to hand-type an inventory (e.g., a list of agents, plugins, or open gaps) in a markdown file. Static lists rot the moment they are saved. If you need a list, write a script (e.g., `scripts/infra_inventory.py`) to generate it dynamically from the source of truth.
2. **The Validator-First Spec Standard**
   A spec proposing a new structure dies within weeks unless it ships its CI validator in the same deliverable. You may not merge a feature or doc update unless it includes a bash script or Python test that proves the feature exists and works. *Every article must ship with its bash gate.*
3. **Pair-Bind Commits**
   Mandate-text patches and the mechanism gates that enforce them must ship in the SAME git commit. Do not declare a rule today and promise the enforcement script tomorrow.

---

## §3 THE SSOT HIERARCHY (Where Truth Lives)

We have purged the overlapping bibles. When you hydrate, you look to exactly three places:

1. **Constitutional Law (The Boundaries)**: `SOVEREIGN_MANDATES.md`
   *The immutable laws of the engine (e.g., Local-First, AnyIO Absolute, Zero Telemetry).*
2. **Operational Law (What is true right now)**: `OMEGA_CODEX.md`
   *The auto-refreshing state of the engine. If it's not here or in `infra_inventory.py`, it doesn't exist.*
3. **Strategic Law (What we are doing today)**: `ACTIVE_SPRINT.json` / `TASK_REGISTRY.json`
   *The single-writer trackers. No "WIP" or "TBD" markdown lists.*

*If a rule or plan is not in one of these three places, it is historical archive.*

---

## §4 HOW WE COORDINATE: EXPLICIT SYNCHRONIZATION

Every coordination failure in fleet history (deadlocks, page-back hangs, race conditions) was caused by a *silent assumption*. 

1. **The Ownership Manifest**: Every dispatch packet or work package must open with an explicit manifest: *Who owns this? What is deferred? What is reserved for the Architect?*
2. **State Your Assumptions**: Every packet must state its synchronization assumptions explicitly (e.g., *"This assumes N1 completed its config sweep — verify before proceeding"*).
3. **The Hop Rule (Channel Discipline)**: 
   *   **PAGE** = `task()` by chat-session ID. Direct, private. *A pagee may NEVER page their current pager.* Replies travel via the end-of-task summary (which auto-returns to the pager).
   *   **BROADCAST** = Hivemind post. Public, for status, insights, and hygiene.
4. **Honesty Over Optics (Protect the 3 AM Reporter)**: The fleet's superpower is repair-after-honest-failure. Its greatest danger is skipping the honest-failure step to present a "clean" run. A red gate honestly reported overnight outweighs a green dashboard at dawn. **Never bypass a failing check just to exit clean.**

---

## §5 THE INVENTORY REFLEX

Institutional memory remembers what happened; it is structurally blind to what exists (or what was deleted). 
When you touch infrastructure, you must run the inventory organ:
```bash
.venv/bin/python scripts/infra_inventory.py --ci
```
This is the derivation-check cure applied to infrastructure itself. Inventories audit the auditors.

---
*End of Doctrine. Read, Verify, Execute.*
