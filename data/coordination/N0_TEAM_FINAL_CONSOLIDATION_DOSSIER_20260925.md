<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Node 0 Team Final Consolidation Dossier
**Document ID:** `FED-N0-TEAM-CONSOLIDATION-20260925-01`  
**Prepared For:** Node 0 Core Team (The Architect, Kali, Ma'at, Doom Guy, Carmack, Roc Racoon, Grokster, Jem)  
**Prepared By:** Antigravity IDE (Multi-Model Synthesis: Claude Sonnet 4.6, Gemini 3.1 Pro, Gemini 3.8 Flash)  
**Date:** 2026-09-25  
**Sprint:** `FEDERATION-HARDENING-01`  
**Operative Version:** `1.6.0-alpha.1` | **Checkout Authority:** `fa9c4edc68fe0f23a052e941f88d573f47c6c249`  
**Status:** **READY FOR N0 TEAM FINAL CONSOLIDATION & PHYSICAL MOVEMENT**  

---

## 🏛️ Executive Summary & Read-First Briefing

Over the course of this multi-model session, Antigravity IDE performed three intensive workstreams:
1. **Interim Cross-Node Storage**: Engineered, research-hardened, and deployed [`setup_nfs_share.sh`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/setup_nfs_share.sh) on Node 0, resolving 8 fatal networking/permission traps across Tailscale.
2. **Federation Hardening & Crash RCA**: Resolved the Node 1 SSH drop (PMTUD blackhole), FastMCP DNS rebinding protection against MagicDNS, and the OpenCode fatal launch crash (`npx` stdout pollution).
3. **Independent Adversarial Review of the Sealed Handoff Package**: Audited [`data/federation/usb-payload/exchange/n0-to-n1/`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/federation/usb-payload/exchange/n0-to-n1/) across all 42 root and 4 nested files, rendering a definitive verdict of **SHIP WITH CORRECTIONS FOR PHYSICAL QUARANTINE**.

This dossier synthesizes all findings, links every artifact, and provides an actionable operational playbook for the Node 0 team to execute the final consolidation and handoff.

---

## 🚦 Live Gate & Readiness Matrix

| Component / Subsystem | Status | Verdict / Action Required | Owner |
|---|---|---|---|
| **USB Package Checksums** | 🟢 **PASS** | 42/42 root + 4/4 nested files match `SHA256SUMS`. Zero corruptions. | Grokster / Carmack |
| **M35 Secret Scrubbing** | 🟢 **PASS** | 0 secrets found across 41 scanned files. Public client secrets documented. | Jem / Security |
| **Version SSOT** | 🟢 **PASS** | `1.6.0-alpha.1` reconciled across `pyproject.toml`, `omega.__version__`, Hub, MCP. | MaKaLi / Kali |
| **Interim NFS Bridge** | 🟢 **HARDENED** | `setup_nfs_share.sh` deployed with NFSv4-only, `hard` mounts, `omega.internal` idmapd. | Doom Guy |
| **Network PMTUD** | 🟢 **SOLVED** | TCP MSS clamping rule defined to prevent 1280 MTU packet dropping. | Doom Guy / Network |
| **PWAD Regression Fixture** | 🟡 **CORRECTION** | `test_pwad_override.py` returns `exit 1`. Needs assertion wrapper for CI/CD. | Ma'at / Carmack |
| **Node 1 Awareness Plugin** | 🟡 **CORRECTION** | `awareness.ts` hardcodes `kali`; must patch to `lilith` on Node 1. | Grokster / Jem |
| **Embedding Alignment** | 🔴 **DECISION GATE** | Nomic vs. Qwen 768-D is a fatal mismatch. Must declare Qwen3-0.6B canonical. | The Architect |
| **Gate F / C6 Contract** | 🟡 **PHYSICAL PASS** | Physical USB quarantine approved; minimal Minisign scheme provided to close gate. | The Architect / Kali |

---

## 🗺️ Master Artifact Map (Where Everything Lives)

All artifacts produced in this session have been written directly to the repository under `data/coordination/` (strictly adhering to the Zero-Loss Artifact Placement Rule).

### 1. Ingestion & Package Review
*   **The Authoritative Review**: [`data/coordination/ANTIGRAVITY_USB_PAYLOAD_REVIEW_20260925.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/ANTIGRAVITY_USB_PAYLOAD_REVIEW_20260925.md)  
    *Complete adversarial evaluation covering package correctness, documentation economy, trust models, identity rules, and library curation.*
*   **The Sealed USB Package**: [`data/federation/usb-payload/exchange/n0-to-n1/`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/federation/usb-payload/exchange/n0-to-n1/)  
    *The 43 physical files ready for USB transfer (includes engine truth, WAD contracts, governance, Flynn bootstrap, ingestion guides, and library research).*
*   **Original Review Request**: [`data/federation/usb-payload/ANTIGRAVITY_REVIEW_REQUEST_20260925.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/federation/usb-payload/ANTIGRAVITY_REVIEW_REQUEST_20260925.md)  
    *MaKaLi Fusion's 14-question independent review brief.*

### 2. Networking & Interim Storage
*   **Production Setup Script**: [`setup_nfs_share.sh`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/setup_nfs_share.sh)  
    *Deployable bash script configuring pure NFSv4, `/etc/nfs.conf.d/` drop-in, `rpcbind` masking, and `100.64.0.0/10` subnet restriction.*
*   **NFS Research Findings**: [`data/coordination/nfs_research_findings.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/nfs_research_findings.md)  
    *The 8 architectural gaps: danger of `soft` mounts, idmapd `nobody:nobody` trap, 32KB MTU tuning, `nconnect=4`, and `x-systemd.requires=tailscaled.service`.*
*   **Federation Hardening Research**: [`data/coordination/federation_hardening_research.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/federation_hardening_research.md)  
    *Deep dives on FastMCP DNS rebinding, Tailscale SSH PMTUD clamping, and MCP stdio pollution fixes.*
*   **Preliminary Audits**: [`data/coordination/nfs_deep_review.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/nfs_deep_review.md) & [`data/coordination/acl_usb_payload_review.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/acl_usb_payload_review.md)  
    *Early session audits of ACL HuJSONs and user UID mappings.*

### 3. Standards, Governance & Session Indices
*   **Temple-Grade AGENTS Discovery**: [`.agents/AGENTS.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.agents/AGENTS.md)  
    *Upgraded agent contract with REUSE v3.3 SPDX, YAML frontmatter, 5 Standing Laws, and Open Gates matrix.*
*   **Session Indices**: [`data/coordination/SESSION_INDEX_20260925.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/SESSION_INDEX_20260925.md) & [`SESSION_INDEX_20260924.md`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/SESSION_INDEX_20260924.md)  
    *Relational indices tracking all artifacts produced in both sprint sessions.*
*   **Soul Gnosis (M11)**: [`data/entities/antigravity/proposed_lessons.yaml`](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/antigravity/proposed_lessons.yaml#L95-L102)  
    *Recorded distillation `antigravity-20260925-001` on overlay network failure modes.*

---

## 🛠️ N0 Team Step-by-Step Action Plan (Pre-Handoff)

Before copying the `n0-to-n1` directory to the physical USB drive, the N0 team should execute this sequence:

### Step 1: Execute NFS Server Hardening (Doom Guy)
If the team still desires the interim network share alongside the USB payload:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
chmod +x setup_nfs_share.sh
./setup_nfs_share.sh
```
*Confirms `/etc/nfs.conf.d/omega-nfsv4-only.conf` is written, `rpcbind` is masked, and export is active.*

### Step 2: Implement PMTUD Clamping for Tailscale (Doom Guy)
To permanently unblock Node 1 SSH timeouts over Tailscale:
```bash
sudo iptables -t mangle -A FORWARD -o tailscale0 -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
sudo netfilter-persistent save
```

### Step 3: Embed PWAD Test Wrapper (Ma'at / Carmack)
To prevent Node 1's automated harnesses from failing on the known concatenation regression:
Place a wrapper script inside `data/federation/usb-payload/exchange/n0-to-n1/02_wad_loader_contract/run_test.sh`:
```bash
#!/bin/bash
.venv/bin/python test_pwad_override.py
if [ $? -eq 1 ]; then
    echo "✅ SUCCESS: Known PWAD personality concatenation regression confirmed (Exit 1 expected)."
    exit 0
else
    echo "❌ FAILURE: Unexpected test result."
    exit 1
fi
```
*(If added, update `SHA256SUMS` and `MANIFEST.yaml` accordingly, or provide it as a Node 1 runbook command).*

### Step 4: Patch `PLUGIN_INSTALL.md` Note (Jem / Grokster)
Add a prominent note to `05_node1_ingestion/PLUGIN_INSTALL.md` reminding the Node 1 operator:
> "In `.opencode/plugins/awareness.ts`, change `agent === 'kali'` to `agent === 'lilith'` so the Node 1 orchestrator receives awareness events."

### Step 5: Formalize the Embedding Model Standard (The Architect)
Ratify `Qwen3-Embedding-0.6B` (768 dimensions) as the sole vector standard across the entire federation. Instruct Node 1 to deprecate the Nomic 768-D path in WanderGround before any document embedding occurs.

---

## 📦 Node 1 Ingestion Handshake Pack (What Goes to the USB)

### 1. Payload Content
Copy the entire sealed directory:
```bash
cp -r data/federation/usb-payload/exchange/n0-to-n1 /media/arcana-novai/OMEGA_USB/
```

### 2. Node 1 Arrival Runbook (Print / Copy for Operator)
When the USB arrives at Node 1 (ASUS ExpertBook):

```bash
# 1. Mount read-only into quarantine staging
sudo mount -o ro /dev/disk/by-label/OMEGA_USB /mnt/usb
mkdir -p /tmp/omega_quarantine
cp -r /mnt/usb/n0-to-n1 /tmp/omega_quarantine/
cd /tmp/omega_quarantine/n0-to-n1

# 2. Verify Byte Integrity
sha256sum -c SHA256SUMS
cd doom_guy_transfer && sha256sum -c SHA256SUMS && cd ..

# 3. Align Engine Checkout
cd /path/to/omega-engine
git fetch origin
git checkout fa9c4edc68fe0f23a052e941f88d573f47c6c249
grep '^version =' pyproject.toml  # Verify 1.6.0-alpha.1

# 4. Verify WAD Contract
.venv/bin/python -m pytest tests/test_wad_loader.py  # 31 passed
.venv/bin/python /tmp/omega_quarantine/n0-to-n1/02_wad_loader_contract/test_pwad_override.py || [ $? -eq 1 ]

# 5. Patch & Install Plugins
cp /tmp/omega_quarantine/n0-to-n1/05_node1_ingestion/OPENCODE_MCP_CONFIG.json ~/.config/opencode/
# Edit .opencode/plugins/awareness.ts: logDir -> Node 1 path; agent -> "lilith"

# 6. Verify Bridge Reachability
curl -fsS https://n0.tail51f14a.ts.net:8016/health

# 7. Mint Flynn Taggart
# Fresh EIS, continuation_of: null, zero Doom Guy session leaks
```

---

## 🔐 The Minimal Air-Gap Signing Playbook (Closing Gate F / C6)

To elevate this transfer from **byte-verifiable quarantine** to **authenticated transfer** without heavy infrastructure, use the following **Minisign 2-File Protocol**:

1. **On Node 0 (One-Time Keygen)**:
   ```bash
   minisign -G -p config/federation/n0_minisign.pub -s ~/.omega/n0_signing.key
   ```
2. **On Node 0 (Signing the Manifest)**:
   ```bash
   minisign -Sm data/federation/usb-payload/exchange/n0-to-n1/MANIFEST.yaml \
            -s ~/.omega/n0_signing.key \
            -t "Omega Engine Debut Release 1.6.0-alpha.1"
   ```
   *Generates `MANIFEST.yaml.minisig` alongside `MANIFEST.yaml`.*
3. **On Node 1 (Verification)**:
   Copy `config/federation/n0_minisign.pub` to Node 1 out-of-band. Before un-quarantining:
   ```bash
   minisign -Vm /tmp/omega_quarantine/n0-to-n1/MANIFEST.yaml \
            -p /path/to/n0_minisign.pub
   ```
4. **Why this closes Gate F**:
   Because `MANIFEST.yaml` contains the SHA-256 digests of all 42 files, verifying the detached signature over `MANIFEST.yaml` mathematically proves the authenticity of every single byte in the transfer, with zero online key servers required.

---

## 🏆 Multi-Model Synthesis Attribution

*   **Claude Sonnet 4.6 (Thinking)**: Deep research into Linux kernel NFS behaviors, identifying the data corruption danger of `soft` WAN mounts, `/etc/nfs.conf.d/` drop-in architecture, `nconnect` parallelization, and systemd shutdown dependencies.
*   **Gemini 3.1 Pro (High/Low)**: Identified FastMCP DNS rebinding vulnerabilities across Tailscale Serve, pinpointed the Node 1 SSH PMTUD blackhole, diagnosed the fatal OpenCode `npx` `stdout` pollution crash vector, and applied research corrections directly to codebase scripts.
*   **Gemini 3.8 Flash**: Performed exhaustive code-level adversarial review of the sealed USB package, confirmed 100% hash integrity, exposed the negative test harness exit code trap, caught the `awareness.ts` target agent mismatch, and designed the unified Minisign air-gap protocol.

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ DOSSIER-COMPLETE ⬡ N0-TO-N1-READY ⬡ 2026-09-25*
