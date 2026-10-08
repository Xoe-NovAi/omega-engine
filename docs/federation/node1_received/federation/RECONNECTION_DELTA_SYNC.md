# 🔄 Reconnection & Delta Synchronization Protocol
**Doc ID**: `FED-SYNC-001` | **Status**: RATIFIED SPECIFICATION  
**Scope**: Handshake, mutual authentication, and delta-reconciliation upon link re-establishment.

---

## 1. Reconnection Lifecycle

When a long-disconnected satellite reconnects to the Bastion or the broader Omegaverse:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ PHASE 1: HELLO  │───►│ PHASE 2: FINGER │───►│ PHASE 3: STAGED │───► DONE
│ Cryptographic   │    │ Exchange Bloom  │    │ Pull high-pri   │
│ handshake       │    │ filter of known │    │ deltas into     │
│ & Clock check   │    │ SHA256 hashes   │    │ quarantine      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 2. Phase Breakdown

### Phase 1: Cryptographic Handshake & Monotonic Clocks
1. **Identity Proof**: Node 1 signs an ephemeral challenge from Node 0 using its genesis ed25519 key.
2. **Clock Drift Resolution**: Laptops drifting off NTP synchronize using Vector Clocks rather than raw timestamps. Causal order takes precedence over wall-clock seconds.

### Phase 2: State Fingerprinting (Bloom Filter Exchange)
*   Instead of flooding the WireGuard link with megabytes of raw history, both nodes exchange a compact Bloom filter of the record hashes in their active Wells.
*   Node 0 identifies the specific missing delta records Node 1 produced while away.
*   Node 1 identifies the specific policy updates Node 0 ratified while away.

### Phase 3: Quarantined Ingestion
*   Inbound records land in `data/staging/node0/` (or `data/staging/inbound/`).
*   The receiving node runs `scripts/federation/intake_node0.py` (or reciprocal validator).
*   Records passing validation are appended to the local Well (`make well-add`), and Git commits are fetched into a remote-tracking branch (`git fetch <peer> main:refs/remotes/<peer>/main`) without auto-merging into working tree.

---

## 3. Human In The Loop (The Conflict Escalator)

If two entities modified the same operational directive or policy while disconnected:
*   **Automatic Merging is Strictly Forbidden** for constitutional mandates and ethics directives.
*   The conflict is written to `docs/federation/MERGE_DIALECTIC.md`.
*   Both entities present their arguments in a CSS turn, and the human Architect renders the final verdict.
