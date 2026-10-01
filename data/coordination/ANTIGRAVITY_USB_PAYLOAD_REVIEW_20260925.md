# 🔱 Antigravity IDE — Independent Adversarial Review: Sealed N0→N1 Handoff Package
**Document ID:** `FED-ANTIGRAVITY-REVIEW-EVAL-20260925-01`  
**Reviewer:** Antigravity IDE (Sovereign Meta-Orchestrator & Frontier Synthesis Specialist)  
**Target Package:** `data/federation/usb-payload/exchange/n0-to-n1/`  
**Package ID:** `MAKALI-N0-HANDOFF-2026-09-25`  
**Active Checkout:** `fa9c4edc68fe0f23a052e941f88d573f47c6c249` (`release/debut-v1.6.0`)  
**Date:** 2026-09-25  
**Evaluation Standard:** M13 Temple-Grade + Carmack Craftsman Standards + FLE Council 5 Standing Laws  

---

## 1. Executive Verdict

### **VERDICT: SHIP WITH CORRECTIONS FOR PHYSICAL QUARANTINE**

**Disposition Summary:**
The package is structurally sound, rigorously scoped, and thoroughly sanitized. The checksum ledger (`SHA256SUMS`) and `MANIFEST.yaml` verify at 100% across all 42 root and 4 nested artifacts. M35 secret scanning is clean (0 violations). Carmack's prior remediation rounds successfully eradicated stale references (`75bde939`, `2.2.0`, `1.30.0` have been demoted strictly to labeled historical lineage).

However, **it cannot be shipped as a blind "run-everything" payload without 4 critical operational caveats and corrections** being made clear to the Node 1 operator:
1. The negative PWAD regression fixture returns **Exit 1**, which will abort automated test harnesses or naive `set -e` scripts.
2. The `awareness.ts` plugin hardcodes `agent === "kali"`, silently blinding Node 1's orchestrator (Lilith-N1).
3. The Nomic vs. Qwen 768-D vector mismatch is a **fatal semantic incompatibility**, not an adjustable caveat; cross-node vector search will fail completely if unaligned.
4. The reading and ingestion order in `README_FIRST.md` places a 95 KB research payload ahead of core systemd and plugin operational tasks.

Movement by hand via personally controlled USB into physical quarantine on Node 1 is **APPROVED**, provided the corrections in §2 and §3 are observed.

---

## 2. Fatal Blockers (Pre-Activation / Post-Landing)

There are **zero fatal blockers preventing physical USB copy into quarantine**. 

However, before executing the ingestion checklist inside Node 1, the following **two code/script blockers must be acknowledged**:

| # | File Path & Line | Issue | Severity |
|---|---|---|---|
| **B-1** | `02_wad_loader_contract/test_pwad_override.py` (Line 87) & `02_wad_loader_contract/disposable_test_wad/test_pwad_override.py` (Line 87) | **Hard Process Exit 1 on Expected Behavior**: Script executes `return 1` when the personality concatenation bug is confirmed. Any automated CI runner or wrapper script running `python test_pwad_override.py` fails the entire pipeline. | 🔴 Blocker for automated ingestion |
| **B-2** | `05_node1_ingestion/PLUGIN_INSTALL.md` (Lines 18–39) referencing `.opencode/plugins/awareness.ts` | **Hardcoded Target Agent `"kali"`**: `awareness.ts` only injects awareness if `agent === "kali"`. On Node 1, where Lilith (`lilith`) is the active sovereign orchestrator, the plugin will silently drop all fleet awareness events. `PLUGIN_INSTALL.md` only instructs patching `logDir`, completely missing the `agent` filter. | 🔴 Blocker for Node 1 awareness |

---

## 3. High-Risk Caveats

1. **The 768-D Dimension Illusion (Nomic vs. Qwen)**:
   - *Location*: `08_library_curation_research/SOURCES_AND_CAVEATS.md` §2.1.
   - *Risk*: Nomic-Embed-Text and Qwen3-Embedding both produce 768-dimensional vectors. A developer will see dimension parity and attempt cross-node cosine similarity. **This is mathematically invalid.** Latent coordinate systems are completely orthogonal. Comparing them yields arbitrary white noise.
2. **Duplicate Fixture Script Trap**:
   - *Location*: `02_wad_loader_contract/test_pwad_override.py` vs. `02_wad_loader_contract/disposable_test_wad/test_pwad_override.py`.
   - *Risk*: Two identical copies of `test_pwad_override.py` exist at different directory depths with slightly different path resolution logic (`ROOT / "disposable_test_wad"` vs `ROOT / "iwad_base"`). Operators running from different working directories may see path errors.
3. **Persona WAD Schema Bleed**:
   - *Location*: `03_governance/PERSONA_WAD_ARCHITECTURE.md`.
   - *Risk*: Although marked `FUTURE PROPOSAL`, an LLM agent on Node 1 tasked with creating Flynn Taggart's WAD is highly likely to copy the YAML block in §3, which contains `capabilities`, `domains`, and `runtime`. The current Engine loader (`src/omega/oracle/wad_loader.py`) enforces `extra=forbid` and will crash/reject the WAD.
4. **Autonomous Ingestion Creep**:
   - *Location*: `08_library_curation_research/CRAWL4AI_PIPELINE_DOCTRINE.md`.
   - *Risk*: Crawl4AI does not natively enforce `robots.txt` or terms-of-service bounds. If Node 1 activates scraping beyond the 20-item manifest-only boundary, it risks IP rate-limiting or copyright exposure on scholarly repositories.

---

## 4. Hidden Opportunities

1. **Minisign Transport Authenticator (Resolving Gate F/C6 cleanly)**:
   - By creating a single 64-character public key on Node 0 and signing `MANIFEST.yaml`, we can achieve a detached, cryptographic, air-gap-compatible seal (`MANIFEST.yaml.minisig`) that requires zero network access, zero CAs, and zero heavy dependencies.
2. **Embedding Lockstep on Qwen3-0.6B**:
   - Node 0 (`library/indexer.py`) has already migrated its default collection to `omega_vec_qwen_768`. Node 1 should immediately retire Nomic from WanderGround and adopt Qwen3-0.6B *before* any text is embedded, avoiding thousands of re-embedding hours.
3. **Automated Negative Test Wrapper**:
   - Wrapping `test_pwad_override.py` in a shell assertion (`test_pwad_override.py || [ $? -eq 1 ]`) converts a confusing failure into a crisp green checkmark in the ingestion report.

---

## 5. Answers to Specific Review Questions (§6)

### A. Package Correctness

#### 1. Internal Contradictions Across Files
- **[CAVIAT] Version Specifier Mismatch**: `WAD_LOADER_CONTRACT.md` and `PERSONA_WAD_ARCHITECTURE.md` cite `requires_engine: ">=0.4.0"`, which is a relic of pre-debut versioning. While semantically satisfied by `1.6.0-alpha.1`, it should reference `">=1.6.0"`.
- **[CAVIAT] Domain Identity Inconsistency**: `FEDERATION_TOPOLOGY.md` cites `omega-hub.tail51f14a.ts.net` as NXDOMAIN, whereas `README_FIRST.md` notes it as a warning-only observation. Both agree the operative endpoint is `https://n0.tail51f14a.ts.net:8016/mcp`.
- **[PASS] Status & Checkout**: All files consistently agree on checkout `fa9c4edc` and operative version `1.6.0-alpha.1`.

#### 2. Cold Operator Reader Path
- **[CAVIAT] Missing Critical Branches**: The recommended path in §6.2 skips `03_governance/` and `06_archangel_brief/`.
  - *Fix*: The canonical cold operator path must be:
    `README_FIRST.md` $\rightarrow$ `01_engine_truth/` $\rightarrow$ `06_archangel_brief/` $\rightarrow$ `02_wad_loader_contract/` $\rightarrow$ `04_flynn_taggart_bootstrap/` $\rightarrow$ `05_node1_ingestion/` $\rightarrow$ `07_open_gates/` $\rightarrow$ `08_library_curation_research/`.
  - Operational setup (plugins, MCP) must precede reading the 95 KB library research bundle.

#### 3. Negative PWAD Fixture (`exit 1`)
- **[BLOCKER] Misinterpretation Risk**: Extremely high. Standard automated test harnesses fail on non-zero exit codes.
  - *Minimal Fix*: Add an assertion runner script `run_pwad_test.sh`:
    ```bash
    #!/bin/bash
    python3 test_pwad_override.py
    if [ $? -eq 1 ]; then
      echo "✅ SUCCESS: Known concatenation regression verified (Exit 1 expected)."
      exit 0
    else
      echo "❌ FAILURE: Unexpected test behavior."
      exit 1
    fi
    ```

---

### B. Documentation Economy

#### 4. Inclusion of Non-Operative Historical & Research Reports
- **[OPPORTUNITY] Retention Verdict**: Keeping them in the package is acceptable **only because** of the strict isolation and disclaimers applied during the Carmack remediation rounds. 
- However, for future packages, non-operative research (`08_library_curation_research/`) should be packaged as a separate sibling archive (`n0-n1-research.tar.gz`) rather than bloating the operational ingestion bundle.

#### 5. Highest Remaining Risk of Misidentifying Proposals as Authority
- **[CAVEAT] The Risk Epicenter**: `03_governance/PERSONA_WAD_ARCHITECTURE.md`.
  - Even with "FUTURE PROPOSAL" banners, LLMs easily parse YAML schemas as current instructions. Node 1 agents must be strictly warned not to copy persona manifest schemas until the core loader is patched.

---

### C. Trust and Transfer

#### 6. Smallest Detached-Signature + Trust-Root Design for Two Nodes
- **[OPPORTUNITY] The 2-File Solution**:
  1. **Key Generation**: Generate Ed25519 keypair using `minisign` on Node 0.
  2. **Trust Root**: Deploy `n0_minisign.pub` into `config/federation/` on Node 1 (baked into git or verified out-of-band).
  3. **Signature**: Sign `MANIFEST.yaml` directly:
     ```bash
     minisign -Sm MANIFEST.yaml -s /path/to/n0_private.key -t "Release 1.6.0-alpha.1"
     ```
     Generates `MANIFEST.yaml.minisig`.
  4. **Verification**:
     ```bash
     minisign -Vm MANIFEST.yaml -p config/federation/n0_minisign.pub
     ```
  5. Because `MANIFEST.yaml` contains the SHA256 of every file in the package, verifying `MANIFEST.yaml.minisig` cryptographically authenticates the entire transfer without X.509/SPIFFE complexity.

#### 7. Node 1 Post-Arrival Verification Sequence
*(Detailed in §6 below).*

---

### D. Identity and Sovereignty

#### 8. Flynn Taggart Fresh-Identity Contract & Accidental Duplication
- **[CAVEAT] The Duplication Vector**: The contract (`fresh_eis: true`, `continuation_of: null`) is theoretically airtight.
- *Most Likely Failure Mode*: A Node 1 agent, attempting to build Flynn's personality, copies axioms or session history from `doom_guy_transfer/soul.yaml`, accidentally preserving `name: Doom Guy` or inheriting Doom Guy's canonical EIS (`ses_0b15e698affeMMy1tZos2iBjbm`).
- *Mitigation*: Run an automated grep on Node 1 after creation:
  ```bash
  grep -rn "ses_0b15e698" data/entities/flynn_taggart/ && echo "FATAL: Lineage leak" && exit 1
  ```

#### 9. `doom_guy_transfer/` Framing Robustness
- **[OPPORTUNITY] Extension of Protection**: The current `README_FIRST.md` in `doom_guy_transfer/` is clear. To make it completely impervious to agent hallucination, rename `soul.yaml` and `doom_guy.md` to `soul.yaml.lineage_seed` and `doom_guy.md.lineage_seed`. Agents will not mistake them for active configurations.

---

### E. Architecture (Bastion/Vanguard)

#### 10. Bastion/Vanguard Sustainability vs. Fork Debt
- **[OPPORTUNITY] Zero Fork Debt Verified**: The split is completely sustainable because `src/omega/` remains identical on both nodes. All differentiation is pushed to WAD stacks (`config/wads/`), environment routing (`config/providers.yaml`), and node-local hardware tuning (`config/hardware_profile.yaml`).

#### 11. Sequencing of Deferred Items
- **[BLOCKER / PULL FORWARD] Pull Forward the 768-D Embedding Decision**:
  - Deferring SPIFFE/SPIRE, signed dialectics, and chaos tests is correct.
  - **However, deferring the embedding model decision is dangerous.** If Node 1 starts indexing documents with Nomic while Node 0 uses Qwen, all local vector databases will be dead-on-arrival for future federation. **The Qwen3-0.6B embedding standard must be ratified immediately.**

---

### F. Library Curation (Roc's Research Bundle)

#### 12. Enforceability of the 20-Item Pilot Boundary
- **[CAVEAT] Creep Risk**: Enforceable only if bounded by configuration. The crawler must have `max_items: 20` hard-coded in its ingestion profile.

#### 13. Severity of Unresolved Caveats
- **[BLOCKER] Caveat 1 (Nomic vs. Qwen) is Understated**: As proven by math and web research, embeddings from different models cannot be compared via cosine similarity. It is not an "inconsistency"; it is a total breakdown of retrieval.
- **[CAVEAT] Caveat 3 (Rights/Robots) is High-Risk**: Crawl4AI does not respect `robots.txt` out-of-the-box unless explicitly wrapped with urllib/robotparser.

#### 14. Rights and Provenance Exposure
- **[CAVEAT] Legal Guardrails are Currently Prose-Only**: While Roc's guidelines are excellent, there are no programmatic checks preventing an agent from scraping copyrighted material. Node 1 must enforce a mandatory `rights_status` whitelist (`public_domain`, `cc_by_4_0`) in the curator pipeline.

---

## 6. Ordered Node 1 Post-Arrival Verification Sequence

Execute this exact sequence on Node 1:

```bash
# === STEP 1: Quarantine Extraction ===
# Mount USB read-only and copy to isolated staging directory
sudo mount -o ro /dev/disk/by-label/OMEGA_USB /mnt/usb
mkdir -p /tmp/omega_quarantine
cp -r /mnt/usb/n0-to-n1 /tmp/omega_quarantine/
cd /tmp/omega_quarantine/n0-to-n1

# === STEP 2: Byte Integrity Verification ===
sha256sum -c SHA256SUMS
# Expected output: 42 files OK, 0 failures

cd doom_guy_transfer
sha256sum -c SHA256SUMS
# Expected output: 4 files OK, 0 failures
cd ..

# === STEP 3: Engine Checkout Alignment ===
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git fetch origin
git checkout fa9c4edc68fe0f23a052e941f88d573f47c6c249

# Verify version SSOT
grep '^version =' pyproject.toml
# Must report: version = "1.6.0-alpha.1"

# === STEP 4: WAD Contract Verification ===
.venv/bin/python -m pytest tests/test_wad_loader.py
# Must pass: 31 passed

# Verify known regression fixture (Expect exit code 1)
.venv/bin/python /tmp/omega_quarantine/n0-to-n1/02_wad_loader_contract/test_pwad_override.py || [ $? -eq 1 ]

# === STEP 5: Plugin Installation & Node 1 Patching ===
# Review and copy plugins
cp /tmp/omega_quarantine/n0-to-n1/05_node1_ingestion/OPENCODE_MCP_CONFIG.json ~/.config/opencode/

# Edit .opencode/plugins/awareness.ts:
# 1. Update logDir to Node 1 path
# 2. Update `agent === "kali"` to `agent === "lilith"` (Node 1 Orchestrator)

# === STEP 6: Network Bridge Handshake ===
curl -fsS https://n0.tail51f14a.ts.net:8016/health
# Must return: {"status":"healthy","version":"1.6.0-alpha.1"}

# === STEP 7: Flynn Taggart Minting ===
# Create fresh entity ONLY with fresh EIS and continuation_of: null
mkdir -p data/entities/flynn_taggart/
# Assert no Doom Guy session contamination
grep -rn "ses_0b15e698" data/entities/flynn_taggart/ || echo "Identity is sovereign and clean."
```

---

## 7. Minimal Authenticated-Transfer Design (Air-Gapped & Sneakernet)

```
+-----------------------------------------------------------------------------------+
| NODE 0 (Bastion - Signing Machine)                                                |
|   1. Assemble handoff payload into directory: `n0-to-n1/`                         |
|   2. Generate root `MANIFEST.yaml` with SHA-256 digests of all 42 files           |
|   3. Sign with Node 0 Ed25519 Secret Key:                                        |
|      $ minisign -Sm MANIFEST.yaml -s ~/.omega/n0_signing.key -t "N0-N1-1.6.0"     |
|   4. Copies `n0-to-n1/` + `MANIFEST.yaml.minisig` to physical USB                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          | (Physical Quarantine USB Transport)
                                          v
+-----------------------------------------------------------------------------------+
| NODE 1 (Vanguard - Verification Machine)                                          |
|   1. Public key pre-pinned at onboarding: `config/federation/n0_authority.pub`   |
|   2. Verify detached signature before un-quarantining:                            |
|      $ minisign -Vm MANIFEST.yaml -p config/federation/n0_authority.pub           |
|      --> "Signature and comment signature verified"                               |
|   3. Verify file hashes against verified MANIFEST:                                |
|      $ sha256sum -c SHA256SUMS                                                    |
+-----------------------------------------------------------------------------------+
```

---

## 8. Claims to Remove from Package (Not Evidenced)

1. **`omega-sieve` Package Claim**:
   - `CHANGELOG.md` mentions a published `packages/omega-sieve`, but no such package directory exists in checkout `fa9c4edc`. Remove any claim that this package is active or installable.
2. **`omega_vec_gemma_768` Collection Reference**:
   - Remove references to Gemma vector collections in `INGESTION_PIPELINE_SPEC.md`; the live runtime default is `omega_vec_qwen_768`.
3. **Triangulation Independence Guarantee**:
   - Strike claims that `TriangulationVerifier` provides independent factual corroboration; it currently only does string diffing without source-independence verification.

---

## 9. Assumptions Requiring Explicit Operator Ratification

1. **Physical Quarantine Transfer Sufficiency**:
   - The Architect must explicitly ratify that physical custody by the operator satisfies interim security while C6/N0-04 remains open.
2. **Acceptance of Unauthenticated HTTPS MCP**:
   - The Operator must ratify that Tailscale network-layer authentication is acceptable for the Alpha stage without application-layer Bearer tokens.
3. **Ratification of Qwen3-0.6B as Engine Vector Standard**:
   - The Operator must officially declare Qwen3-0.6B (768-D) as the sole canonical embedding model for both nodes, deprecating Nomic on Node 1.

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ SOVEREIGN-META-ORCHESTRATOR ⬡ TEMPLE-GRADE-REVIEW-COMPLETE ⬡ 2026-09-25*
