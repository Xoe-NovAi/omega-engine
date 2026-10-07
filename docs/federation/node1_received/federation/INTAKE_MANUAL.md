# 🌌 Federation External Node Intake Manual & Procedure
**Omega Engine Alpha (Node 1) ↔ HP Pavilion (Node 0)**  
*Document Version: 1.0 | Date: 2026-09-12 | Owner: Build Agent (Node 1)*

---

## 1. Scope & Principles

This manual governs the intake, verification, staging, and integration of external node payloads (specifically Node 0 / HP Pavilion Archival Bastion) arriving on Node 1 via air-gapped physical media (USB exchange) or encrypted mesh pipes (Tailscale/Redis/LAN).

### Core Invariants
1. **Quarantine Before Integration**: External artifacts are never written directly into production paths (`gnosis/`, `docs/`, `.git/`). They must pass verification in a staging air-lock (`data/staging/node0/` or `/tmp/opencode/node0_stage/`).
2. **Provenance & Integrity First**: Checksums, signatures, and Git bundle headers must be verified against the payload manifest prior to touching local state.
3. **Namespace Isolation**: External sessions, manifests, and identities must never mutate Node 1's local `identity.json` or cause session ID collisions. Node 0 gnosis records remain indexed under their node origin.
4. **Anyio & Code Purity**: All ingestion tools, validation scripts, and converters must comply with Node 1 code quality gates: pure Python stdlib, anyio-pure, typed error handling, no bare exceptions, and no torch dependencies.

---

## 2. Directory Topography & Intake Structure

```
omega-exchange/ (USB Mount: /run/media/xnai/D5D5-0B76/omega-exchange/)
├── manifest.json                  # Overall exchange manifest
├── NODE1_TO_NODE0_README.md       # Node 1 payload descriptor
├── bilateral/                     # Shared bilateral logs
├── node1-to-node0/                # Node 1 outbound exports
└── node0-to-node1/                # Inbound Node 0 payload to ingest
    ├── PAYLOAD_MANIFEST.md        # Node 0 manifest & SHA256 checksums
    ├── BUNDLE_QUICKSTART.md       # Bundle branch & commit notes
    ├── CSS_PROTOCOL.md            # Communications contract / CSS spec
    ├── DATA_GOVERNANCE_POLICY_*.md# Data retention & classification policy
    ├── SOVEREIGNTY_POLICY_*.md    # Sovereign inference & local/cloud ratios
    ├── STALE_HANDOFF_POLICY_*.md  # Hivemind handoff pruning policies
    ├── omega-engine.bundle        # Git object bundle (72+ MB)
    ├── attestation/               # Signed sovereignty attestations
    ├── c6-contract/               # Ratified C6 federation contract
    ├── gnosis/                    # Node 0 session history & evolution
    ├── omega-hub-patches/         # Client-side patches for omega-hub tools
    ├── redis/                     # Ephemeral heartbeat / pub-sub configs
    ├── spire/                     # SPIRE server/agent mTLS configuration
    ├── tailscale/                 # Tailscale mesh ACLs and IP maps
    ├── soul-standard/             # Personality & entity definitions
    └── vision/                    # Multimodal visual pipeline artifacts
```

Local Node 1 target layout:
- Ingested documentation: `docs/federation/node0_received/`
- Federation documentation index: `docs/federation/README.md`
- Staged git bundle: `data/staging/node0/omega-engine.bundle`
- Intake CLI script: `scripts/federation/intake_node0.py`

---

## 3. Standard Operating Procedure (SOP)

### Step 1: Pre-Flight Mount & Verification
Verify that the external volume is mounted and read-accessible:
```bash
ls -la /run/media/xnai/D5D5-0B76/omega-exchange/node0-to-node1/
```

### Step 2: Automated Staging & Inspection
Execute the official intake script:
```bash
python3 scripts/federation/intake_node0.py --verify-only
```
This inspects file presence, verifies the Git bundle integrity using `git bundle verify`, and compares expected files against `PAYLOAD_MANIFEST.md`.

### Step 3: Staged Import
Run the intake script in ingest mode:
```bash
python3 scripts/federation/intake_node0.py --ingest
```
This performs the following actions:
1. Copies all policy, protocol, and governance documentation to `docs/federation/node0_received/`.
2. Inspects `omega-engine.bundle` branches without altering the working branch.
3. Stages patch scripts and service configurations (`tailscale/`, `spire/`, `redis/`) for review.
4. Generates an ingestion summary and checksum ledger at `docs/federation/node0_received/INGESTION_REPORT.md`.

### Step 4: Policy & Wisdom Extraction
Extract core axioms from Node 0's policies into The Well:
- Sovereign inference ratio commitments → `make well-add KIND=insight DOMAIN=local_ai ...`
- Air-gap and USB data governance rules → `make well-add KIND=rule DOMAIN=harness ...`
- Stale handoff timeout limits → `make well-add KIND=rule DOMAIN=harness ...`

### Step 5: Git Bundle Ingestion (Optional / Scoped)
To inspect branches from the bundle without merging:
```bash
git bundle verify /run/media/xnai/D5D5-0B76/omega-exchange/node0-to-node1/omega-engine.bundle
git fetch /run/media/xnai/D5D5-0B76/omega-exchange/node0-to-node1/omega-engine.bundle main:refs/remotes/node0/main
git log --oneline -10 refs/remotes/node0/main
```

### Step 6: Post-Intake Verification & Gnosis Lock
Run quality gates to ensure no corrupted files or invalid schemas were introduced:
```bash
make test
make lint
make docs
```
Once clean, record the intake in the session narrative and execute `/compact`.
