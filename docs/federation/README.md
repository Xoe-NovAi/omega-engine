# 🌐 Omega Engine Federation Subsystem
**Dual-Node Sovereign P2P Architecture (Node 0 ↔ Node 1)**

---

## Overview
Omega Engine operates as a federated, dual-node system:
- **Node 0 (HP Pavilion)**: Archival Bastion (Git SSOT, omega-hub MCP, Qdrant/SQLite stores, Hivemind coordination).
- **Node 1 (ASUS ExpertBook)**: Exploration Vanguard (CPU inference, spatial knowledge, real-time experimentation).

## Ingested Node 0 Materials
External materials received from Node 0 are cataloged in `docs/federation/node0_received/`.

Key documents:
- **[INTAKE_MANUAL.md](INTAKE_MANUAL.md)**: Procedures, safety invariants, and staging workflow for all incoming node payloads.
- **[CSS_PROTOCOL.md](node0_received/CSS_PROTOCOL.md)**: Sovereign communications contract.
- **[SOVEREIGNTY_POLICY.md](node0_received/SOVEREIGNTY_POLICY_20260912.md)**: Local-vs-cloud inference ratio benchmarks and mandates.
- **[DATA_GOVERNANCE_POLICY.md](node0_received/DATA_GOVERNANCE_POLICY_20260912.md)**: Data retention, classification, and air-gap exchange protocol.
- **[STALE_HANDOFF_POLICY.md](node0_received/STALE_HANDOFF_POLICY_20260912.md)**: Hivemind coordination pruning rules.

## Intake Tooling
- `scripts/federation/intake_node0.py`: Automated manifest verification, staging, doc triage, and bundle validation.
- Usage: `python3 scripts/federation/intake_node0.py [--source <dir>] [--verify-only] [--ingest]`
