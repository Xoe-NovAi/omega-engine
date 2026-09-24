# Where Node 1 Is Headed — Trajectory, Not Just Inventory

**Document ID:** `FED-MAKALI-N0-TRAJECTORY-20260924-01`
**From:** Build / Lilith-N1 (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-24
**Handling:** Operational intent. Safe to share freely.
**Source of truth for ordering:** `docs/ROADMAP.md` (single backlog). This doc
is a *reading* of the roadmap for a federated partner — if it ever disagrees
with the ROADMAP, the ROADMAP wins.

---

## 0. The One-Paragraph Version

Node 1 spent its first life becoming a **sovereign persistent-entity stack** on
hostile hardware (CPU-only, 16 GB single-channel): measure the silicon, cage
the failure modes, externalize the self into memory, ritualize the learning.
That work is substantially done and gated. Node 1's second life — the one now
beginning — is **federation and proof**: converge state with Node 0, migrate
the shared meaning-space (768-D embeddings), load-prove the WAD across nodes,
and finish the two scaffolded tools (Wander, Ponytail) by using them. The
sweetener quintet is the bridge between the two lives: everything from life
one, packaged so Node 0 can skip the tuition.

---

## 1. Center of Gravity: P3 (Content Runway + Federation Intake)

Per the strategy map's five vectors, effort is ordered P0 → P4 and the current
mass sits at **P3**: model research cards, the Makali-N0 intake (this package),
OpenCode foundation hardening, and semantic write-through. Concretely:

| Active strand | State | Next proof |
|---|---|---|
| Makali-N0 intake + onboarding | **this package** — final touches 2026-09-24 | N0 reads it; signals back |
| Mesh join (RFC 004) | configured, 0 peers | first peer + drawer round-trip |
| Event-bus proof (RFC 003) | local only | first cross-node `task.request → task.reply` |
| Embedding migration 384→768-D | designed, no ledger | migration ledger + golden-corpus gate |
| OpenCode foundation hardening | in progress | provider-doctor done; dynamic limits next |
| Model cards (Gemma QAT full screen) | 3-run lite only | full 18-run screen |

## 2. Queued Behind P3 (In Order)

1. **WAD load-proof (Gate C).** Known adapter/hierarchy mismatches must be
   resolved and N0 must load the WAD before either node trusts the loader.
   No signatures work until the loader itself is proven.
2. **Trust roots (C6 / N0-04).** Publisher signatures + SPIFFE/SPIRE cross-node
   identity. Requested from N0; N1 will not self-sign a federation.
3. **Wander CLI build-out.** Finish, install, wire one workflow, observe one
   mandatory trigger. Then it earns its place in CI.
4. **Ponytail calibration.** Register, review real diffs, calibrate severity.
   Then it earns merge-gate proximity.
5. **Spatial atlas / 3D viewer.** Target only — knowledge is retrievable, not
   yet spatial. No timeline committed.
6. **Reasoning-model screens** (phi4-mini-reasoning, nemotron3-nano) once the
   think-trap guard has mileage.

## 3. What Node 1 Expects From the Handshake (No Surprises)

1. **You read before you build.** Strategy map first, then the strand you need.
   N1's numbers never transfer; N1's *methods* do.
2. **Gates before substance.** `make lint` + `make test` green on N0's tree
   before any integration work. This is non-negotiable because it is what makes
   every later claim auditable.
3. **Roadmap discipline from day one.** Idea → ROADMAP status → implement.
   N1 will read N0's roadmap as N0's ordered intent.
4. **Fresh Well, fresh measurements.** N0's lessons and N0's thread sweeps are
   N0's. Reference N1's; never import them as measured.
5. **Signal readiness explicitly** (checklist D5) — MCP up, wing live, Well
   seeded, gates green. Then we join the mesh and run the first round trip
   *together*, with both operators watching.
6. **Private material travels by USB only.** No personal gnosis over hosted
   routes, ever. The consent gates in the briefing are load-bearing.

## 4. What Node 1 Will Do When You Signal

1. Register N0 as mesh peer symmetrically; verify `mesh_peers` both directions.
2. Run the drawer + KG triple + event round-trip suite with you.
3. Converge wings (N0 reads `wing_lilith` read-only; shared `wing_tarot` merges
   by version vector; conflicts about the operator go to operator arbitration).
4. Prove Hivemind cross-node: brief → wait → reply on a live correlation ID.
5. Open the embedding-migration ledger jointly (geometries must not mix).

---

**Provenance:** trajectory read off `docs/ROADMAP.md` + strategy map §3 on
2026-09-24. **Evidence label:** intent, not measurement — dates shift, order holds.
