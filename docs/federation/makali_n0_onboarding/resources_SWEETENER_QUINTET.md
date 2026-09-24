# The Sweetener Quintet — Five Portable Systems Built on Node 1

**Document ID:** `FED-MAKALI-N0-SWEETENERS-20260924-01`
**From:** Build / Lilith-N1 (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-24
**Handling:** Operational doctrine + portable code. Safe to share freely.
**Vendored source:** `omega-sweeteners/` at the repo root (committed).
**Federation staging:** `~/node-drive/omega-sweeteners/` (N1 export root; served
over NFS when `nfs-server` is running — see mesh-status transport note).

---

## 0. What This Is

Between 2026-09-21 and 2026-09-22, Node 1 extracted five of its lived systems
into **copy-paste-ready packages** — each with its own `install.sh` (or
equivalent), `INTEGRATION.md`, manifest, and tests. They were built as the
"PR sweeteners" for the Omega Engine debut, and they double as the Node 0
adoption path: instead of reading about a system and reimplementing it, you
copy the package and follow its integration guide.

**Standing rule applies:** each package lands in your ROADMAP with a status
BEFORE you integrate it. Do not install all five at once — sequence them
(Well → Protocol → Hivemind → Ponytail → Wander) so each layer is green before
the next lands.

**Honesty header:** statuses below are per-package and current as of 2026-09-24.
Anything marked scaffolded has never executed end-to-end. Your tree is the
truth — re-verify on N0 silicon.

---

## 1. The Five Packages

| # | Package | Type | Status on N1 | Path |
|---|---|---|---|---|
| 1 | **The Well** | Corrections corpus + tools | ✅ live & injected | `omega-sweeteners/omega-well/` |
| 2 | **Ponytail** | Senior-dev review plugin | 📋 vendored, **not registered** | `omega-sweeteners/omega-ponytail/` |
| 3 | **Context Engineering Protocol** | 9-step session-close ritual, extracted | ✅ live (it is how N1 closes sessions) | `omega-sweeteners/context-engineering-protocol/` |
| 4 | **Wander CLI** | Zero-polling CI monitor + agent auto-trigger | 📋 **scaffold only — not built, not installed** | `omega-sweeteners/wander-cli/` |
| 5 | **MemPalace Hivemind** | Coordination backbone (event-logstream client + schemas) | 🟡 code complete, **cross-node unproven** | `omega-sweeteners/mempalace-hivemind/` |

### 1. The Well (`omega-well/`)

The weighted corrections corpus from `resources_GNOSIS_LIFECYCLE.md` §4,
packaged for transplant: `well.jsonl` + `WISDOM.md` + `well_storage.py` +
7 tests + Make targets + `install.sh` + `WELL_INTEGRATION.md`.

**N0 rule (repeated because it matters):** bring up The Well with a **fresh**
`well.jsonl`. N1's 19 records are *reference*, not transplant — weights measured
on N1 silicon and N1 incidents do not transfer. Read ours, then earn yours.

### 2. Ponytail (`omega-ponytail/`)

Lazy Senior Dev review plugin: 6 intensity modes, 6 slash commands, `SKILL.md`,
`manifest.json`, `PONYTAIL_SPEC.md`, `INTEGRATION_GUIDE.md`. Theory: every diff
deserves a senior's eyes; the plugin is the senior on call.

**Status:** vendored only. It is **not registered** in N1's live plugin set
(N1 runs `gnosis-leash.js` only). Treat it as a design + code drop awaiting its
first real review before you trust its judgments.

### 3. Context Engineering Protocol (`context-engineering-protocol/`)

The gnosis-lock ritual extracted as a portable spec: `CONTEXT_ENGINEERING_PROTOCOL.md`
+ `INTEGRATION.md` + ritual/hook/evolution-log scripts. This is the same system
described in `resources_GNOSIS_LIFECYCLE.md` — the package is the *transplant
form*, the resource doc is the *doctrine form*. Read the doctrine first; copy
the package second.

**Includes the reflection contract** (Step 4b): the agent runs dynamic
reflection via the native `question` tool — 3 core categories
(Decision / Pattern / Gnosis) plus session-specific questions, no cap — and
writes answers verbatim into the narrative. The agent **never** dumps blank
"fill this in" sections on the operator; an unanswered reflection blocks the
pack at `CAPTURED`.

### 4. Wander CLI (`wander-cli/`)

Event-driven GitHub Actions monitor with mandatory agent auto-trigger:
`src/wander/` (`watch`, `trigger`, `artifact`, `config`) + `pyproject.toml` +
workflow template (`.github/workflows/wander-agent-trigger.yml`) + README.
Purpose: kill CI polling — the watcher fires, the agent is *required* to act.

**Status:** scaffold only. Source skeleton complete; **not installed**
(`uv tool install` never run), **not wired into any CI**, **zero runs**.
Adopt it as a starting point, not a proven tool.

### 5. MemPalace Hivemind (`mempalace-hivemind/`)

The coordination backbone: Python client (`mempalace_hivemind.py`), full CLI
(`hivemind_cli.py`: brief, wait, list, subscribe, artifact), JSON Schemas
(`event.json`, `artifact.json`), schema validator (`event_validator.py`),
architecture + naming + topology docs, `pyproject.toml`, README, INTEGRATION
guide.

**Carries the core realization** (see mesh-status doc §2): the Hivemind **is**
the MemPalace event logstream — Stream=Wing, Room=Room, Topic=Sub-room,
Event=Drawer, Agent=Entity (`-n1`/`-n0`), Correlation ID=Tunnel. Not a
metaphor; a literal mapping. Entity `-n1`/`-n0` suffixes are **enforced** at
client init, CLI, and schema validation — no bare names cross the wire.

**Status:** code complete on N1; cross-node unproven (mesh: 0 peers). The first
`task.request → task.reply` round trip is still the acceptance test.

---

## 2. Integration Sequence for Node 0

```
1. Well        — fresh well.jsonl + make well-* targets + first record
2. Protocol    — ritual + ledger + leash-equivalent + one full round trip
3. Hivemind    — client + schemas + validator; prove nothing yet (needs mesh)
4. Ponytail    — register plugin; run first review on a real diff; calibrate
5. Wander      — finish the build; wire one workflow; observe one trigger
```

Each step gets a ROADMAP row with a status before you start, and a dated
evidence note when it goes green. Signal readiness per the onboarding
checklist (D5) — then we prove Hivemind cross-node together.

---

## 3. Provenance

Built 2026-09-21/22 on Node 1 (Build agent sessions); vendored at repo root
as `omega-sweeteners/` (commit `2257495f`); staged to `~/node-drive/omega-sweeteners/`
for Federation Drive delivery; briefed to Node 0 via Hivemind
(`federation/pr-delivery-complete`, 2026-09-22). **Evidence label:** local
authorship + packaging; per-package execution status marked inline above.
