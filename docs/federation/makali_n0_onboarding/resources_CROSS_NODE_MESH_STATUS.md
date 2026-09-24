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
3. **Hivemind** (`omega-sweeteners/mempalace-hivemind/`): staged for the real-time layer when live dialectic is wanted.
4. **USB `omega-exchange`:** remains the sneakernet fallback and the preferred carrier for private material.

## Join Steps for Node 0

1. Bring up `mempalace` MCP on Node 0 (see `MCP_PARITY_CHECKLIST.md`).
2. Initialize Node 0 palace; confirm local drawer count and embedder.
3. Register Node 1 as peer (Tailscale identity per federation README L2) — Node 1 registers Node 0 symmetrically.
4. Verify: `mesh_peers` shows both replicas; run a test drawer + KG triple round-trip.
5. Exchange one test event (`task.request` → `task.reply`) to prove the bus.
6. Then: converge wings. Node 0 reads `wing_lilith` (read-only); maintains `wing_makali`; shared `wing_tarot` card material merges by version vector.

## Known Frictions (Honest)

1. **Embedder divergence:** mesh advertises `minilm`; federated WAD decision is `qwen3-embedding:0.6b@768` (RES-EMBED-001). Synced *text* travels today; shared *meaning-space* needs the migration. Do not mix geometries in one index.
2. **Identity decision (N0-5):** federated replicas of one entity vs. distinct namespaced entities — undecided by design; Makali-N0 stays distinctly Makali either way.
3. **Soul files travel by git/USB, not MCP.** Full replica needs the repo synced, not just the palace.
4. **Concurrent writes:** two nodes, one operator model — reconcile by version vector + operator arbitration on conflicts about the operator.
5. **Consent middleware is per-host.** Every new host (platform or node) must carry its own gates; never rely on the other node's good intentions.
