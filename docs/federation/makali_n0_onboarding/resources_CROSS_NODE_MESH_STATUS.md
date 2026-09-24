# Cross-Node Mesh — Measured State & Join Procedure (2026-09-25)

## Measured State (live query, Node 1)

```
self:      XNAi-Asus — rep_f7d73403488e5b32ff8fd8d57d804adc
drawers:   4,971
peers:     []                      ← Node 0 not yet connected
sync:      15s interval, RFC 004 version-vector protocol
embedder:  minilm (local hermetic)
estate:    no live hub publisher observed at query time
```

## How Traversal Works (Designed)

1. **Mesh sync (RFC 004):** Node 0 registers as peer → drawers/diary/KG converge automatically on 15s ticks. Store-and-forward; works over intermittent links.
2. **Event bus (RFC 003):** `event_append` / `event_list` / `event_wait` — append-only coordination log (`task.request`, `task.reply`, `patch.ready`). N1 appends, N0 waits on correlation ID. This is the async inter-agent message bus.
3. **Hivemind** (`omega-sweeteners/mempalace-hivemind/`): the coordination backbone package — client, CLI, JSON Schemas, validator. See §2b for the core realization.
4. **USB `omega-exchange`:** remains the sneakernet fallback and the preferred carrier for private material.
5. **Federation Drive (NFS-over-Tailscale):** N1 exports `~/node-drive` to N0's mesh IP only (`all_squash`, `anonuid=1000`, `fsid=0`); `exchange/n0-to-n1/` + `exchange/n1-to-node0/` are the drop boxes; `omega-sweeteners/` is staged at the export root. Full runbook: `../NODE0_ACTION_BRIEFING_NFS_L2.md`.

## 2b. The Hivemind Realization (2026-09-22 — Load-Bearing)

The Hivemind **is** the MemPalace event logstream. Not a separate system, not
a metaphor — a literal mapping:

| Hivemind | MemPalace |
|---|---|
| Stream | Wing |
| Room | Room |
| Topic | Sub-room |
| Event | Drawer |
| Agent | Entity — **always `-n1`/`-n0` suffixed** |
| Correlation ID | Tunnel |

**Entity naming is enforced, not conventional.** `kali-n1`, `makali-n0`,
`mempalace-n1` — at client init, at the CLI, and at schema validation
(`schemas/event.json`, `event_validator.py`). No bare names cross the wire, so
no event is ever ambiguous about which node authored it. Adopt the same
enforcement on N0 from the first event you append.

**Operational consequence:** there is one coordination substrate, not two. The
"message bus" (§2, item 2) and the "real-time layer" (§2, item 3) are the same
logstream read two ways (`event_wait` for async, Hivemind CLI `subscribe` for
live). Do not build a second bus.

## Transport State (Measured 2026-09-21 → 2026-09-24, Honest Deltas)

| Layer | Last verified | Current state 2026-09-24 |
|---|---|---|
| Tailscale ACL Phase A → **Phase B** (default-deny, tag rules only) | ✅ **Phase B LIVE, 9/9 checks green, 2026-09-21** (`../NODE0_ACTION_BRIEFING_NFS_L2.md`) | policy unchanged since; re-verify on N0's side before join |
| SSH | ✅ bidirectional over mesh (N0 via Tailscale SSH `arcana-novai`) | standing |
| MCP | ✅ bidirectional initialize over mesh IPs | standing |
| NFS export config | ✅ scoped to N0 IP `100.123.51.67` | config present; **`nfs-server` NOT running on N1 as of 2026-09-24** — Federation Drive is unreachable until N1 restarts it (`sudo systemctl start nfs-server`; then N0 mounts per the L2 briefing) |
| Exchange drop boxes | `n1-to-node0/` carries N1 briefings | **`n0-to-n1/` is EMPTY as of 2026-09-24** — no inbound material from N0 via this route yet |
| Hivemind events heard from N0 | — | **zero** — N0 has appended nothing visible to N1's replica (mesh: 0 peers, so this is expected, not alarming) |

## Join Steps for Node 0

1. Bring up `mempalace` MCP on Node 0 (see `MCP_PARITY_CHECKLIST.md`).
2. Initialize Node 0 palace; confirm local drawer count and embedder.
3. Register Node 1 as peer (Tailscale identity per federation README L2; Phase B
   ACL already live — re-verify tags `tag:node0`/`tag:node1` on N0's side) — Node 1 registers Node 0 symmetrically.
4. Verify: `mesh_peers` shows both replicas; run a test drawer + KG triple round-trip.
5. Exchange one test event (`task.request` → `task.reply`, **from `makali-n0`** —
   suffixed, per §2b) to prove the bus.
6. Mount the Federation Drive on N0 per `../NODE0_ACTION_BRIEFING_NFS_L2.md`
   (confirm with N1 that `nfs-server` is running first — it was down on
   2026-09-24); drop a probe file in `exchange/n0-to-n1/` as the transport proof.
7. Then: converge wings. Node 0 reads `wing_lilith` (read-only); maintains `wing_makali`; shared `wing_tarot` card material merges by version vector.

## Known Frictions (Honest)

1. **Embedder divergence:** mesh advertises `minilm`; federated WAD decision is `qwen3-embedding:0.6b@768` (RES-EMBED-001). Synced *text* travels today; shared *meaning-space* needs the migration. Do not mix geometries in one index.
2. **Identity decision (N0-5):** federated replicas of one entity vs. distinct namespaced entities — undecided by design; Makali-N0 stays distinctly Makali either way.
3. **Soul files travel by git/USB, not MCP.** Full replica needs the repo synced, not just the palace.
4. **Concurrent writes:** two nodes, one operator model — reconcile by version vector + operator arbitration on conflicts about the operator.
5. **Consent middleware is per-host.** Every new host (platform or node) must carry its own gates; never rely on the other node's good intentions.
