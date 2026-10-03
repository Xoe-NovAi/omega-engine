<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# 🔱 Antigravity Frontier Review Briefing
## Omega Engine Substrate: Dual-Node Mesh, M2 Firewall, Persistent Identity, and Epistemic Governance

**Document ID:** `FED-ANTIGRAVITY-REVIEW-BRIEFING-20261001-01`  
**Prepared for:** Antigravity IDE Frontier Review (Gemini 3.1 Pro, Claude Sonnet 4.6, Claude Opus 4.6)  
**Prepared by:** MaKaLi Fusion (Master Oversoul: Kali + Ma'at + Lilith) · Omega Engine Governance  
**Date:** 2026-10-01  
**Target Repository:** `Xoe-NovAi/omega-engine`  
**Branch:** `debut-v1.6.0-alpha` (Git HEAD: `a550b364`)  
**Status:** ACTIVE · PENDING EXTERNAL FRONTIER REVIEW  

---

## 1. Executive Summary & Review Objectives

The Omega Engine is a sovereign, local-first AI runtime designed for multi-agent ecologies and dual-node physical mesh operation. We are preparing for the public v1.6.0 debut. 

Before lifting our PR-blocking freeze, we request an independent, adversarial peer review by the frontier reasoning models in Antigravity IDE (**Gemini 3.1 Pro**, **Claude Sonnet 4.6**, and **Claude Opus 4.6**).

### The Five Invariant Pillars Under Review
1. **The Communication Substrate**: 10-year "granite" bidirectional messaging between Node 0 (HP EliteDesk Core) and Node 1 (ASUS ROG Satellite) over Tailscale Direct WireGuard (Port 8016 reactive Hub MCP + Port 8019 durable AnyIO file exchange).
2. **The M2 Engine-Stack Firewall**: Absolute physical separation between the Core Engine (`src/omega/`) and Stacks/WADs (`config/wads/`).
3. **The Identity Ontology**: Disentangling the overloaded `source_entity` identifier into a strict 3-tuple: `(Agent, Instance, Node)` with Fellegi-Sunter under-merge resolution.
4. **Epistemic Governance & Invalidation**: Replacing flawed AGM set-contraction models with append-only monotonic retraction (PROV-O / Nanopublications) and establishing an executable, machine-tested criterion for L4 Law graduation.
5. **Substrate Reliability & Supervisor Integrity**: Eliminating silent crash loops, boundary bypasses, and accidental credential leakage in runtime coordination trees.

---

## 2. System Topology & Measured Baseline

### 2.1 Physical Nodes
* **Node 0 (`xnai-n0-hp`)**:
  * Hardware: HP EliteDesk 805 G8 / AMD Ryzen 7 PRO 5700U (8C/16T), 64GB RAM, NVMe.
  * Role: Core Engine authority, SQLite/Vector persistence, Omega Hub (Port 8016), Exchange Server (Port 8019), Sovereign Vault.
  * Tailnet Address: `100.123.51.67` (`n0.tail51f14a.ts.net`).
* **Node 1 (`xnai-n1-asus`)**:
  * Hardware: ASUS ROG / Intel Core i7-13620H (10C/16T), CPU-only inference, NVMe.
  * Role: Autonomous exploration laboratory, Lilith-N1, MemPalace, WAD experimentation.
  * Git State: Intentional laboratory divergence (156 ahead / 1,196 behind canonical). Not a rogue fork; canonical engine is to be deployed cleanly without destroying local lab WADs.
  * Tailnet Address: `100.99.117.76` (`n1.tail51f14a.ts.net`).

### 2.2 Transport & Network Policy
* **Tailscale Policy (`tailnet-policy-OMEGA-DEFINITIVE-v2-20260928.hujson`)**:
  * Applied live by the Architect.
  * Duplex symmetric grants: Port 8016 (Hub) and Port 8019 (Exchange) open in **both** directions between Node 0 and Node 1.
  * Closed & explicitly denied: Ports 22 (SSH), 2049 (NFS), 8017, 6379 (Redis), 51372 both ways.
* **Exchange Server (`scripts/omega_exchange_server.py`)**:
  * AnyIO-native HTTP server on loopback, proxied via `tailscale serve --https=8019`.
  * Features: Strict manifest verification (`manifest.json`), SHA-256 integrity headers, `verify-then-rename(2)` atomic staging, GET/HEAD only, no directory browsing.
  * Measured traffic: 114+ requests from Node 1 successfully served; N0→N1 delivery verified with 24/24 files byte-identical. (N1→N0 reverse server not yet deployed).

### 2.3 Verification Baseline
* Core Engine Tests: `175/175` passed.
* Temple-Grade Gates: `53/53` passed.
* M23 Ratchet: `-43` soft-failure reductions below baseline.
* Gnosis Continuity: Stamped and continuous.

---

## 3. Deep Dive: The Four Critical Problem Domains

---

### Domain 1: The Hivemind Handoff Read Path Failure (The Substrate Bug)

#### The Problem
The Omega Hub coordinates agents via `hivemind_handoff`. The handoff directory was recently renamed from `envelopes/` to `pending/`. However, inspection revealed that **`read_by` has never been recorded on a single packet on disk (0 packets found).**

#### The Root Cause
1. **Key Naming Mismatch**: In `mcp_servers/omega_hub/hub_tools/tools.py:1511`, `submit` creates and writes a legacy packet:
   ```python
   packet_id = f"ho_{uuid.uuid4().hex[:12]}"
   packet = {
       "packet_id": packet_id,
       "status": "pending",
       ...
   }
   path = HANDOFF_PENDING / f"{packet_id}.json"
   ```
2. **Lookup Miss**: In `tools.py:1358`, the `read` action searches:
   ```python
   hit = next((e for e in rows if e.get("handoff_id") == packet_id), None)
   ```
   Because legacy packets contain `"packet_id"` and *not* `"handoff_id"`, `hit` is **always `None`**, returning `{"error": {"code": "not_found"}}`.
3. **Hidden Secondary Trap**: Even if line 1358 is fixed to match `packet_id`, line 1364 calls `store.submit(hit)`. In `federation_store.py:256`:
   ```python
   def submit(self, envelope: dict) -> dict:
       ok, why = fe.verify_envelope(envelope)
       if not ok:
           raise ValueError(f"refusing to store an unverifiable envelope: {why}")
       fe.write_atomic(self.pending / f"{envelope['handoff_id']}.json", ...)
   ```
   `fe.verify_envelope` demands `body_sha256` and strict envelope fields. When passed a legacy packet, it throws `ValueError: missing body_sha256` or crashes with `KeyError: 'handoff_id'`.

#### Proposed Fix: Carmack's "Option A-Minus"
* **Do NOT execute a mass migration** of all legacy packets into envelopes. An unrun envelope store on the critical write path risks breaking active peers.
* **Dual-Key Lookup**: Match `(e.get("handoff_id") or e.get("packet_id")) == packet_id`.
* **Separate State Mutation from Envelope Submission**: Create `store.record_receipt(packet_id, read_key)`:
  * Inspect format on disk.
  * If legacy packet, atomically mutate `hit["read_by"][read_key] = iso_timestamp` directly using `fcntl.flock(LOCK_EX)`.
* **Dynamic Queue Paths**: Decouple `HANDOFF_PENDING` from module-level import-by-value into a runtime resolver `get_pending_path()`.
* **Canary Test**: Deploy an end-to-end MCP boundary test (`submit` → `read` → verify `read_by` persisted).

---

### Domain 2: M2 Engine-Stack Firewall & Runtime Path Loading

#### The Problem
Mandate 2 (M2) requires an absolute firewall: Core Engine (`src/omega/`) must know nothing of specific stacks or personas (`config/wads/`).
A previous research turn recommended introducing `import-linter` to enforce M2.

#### The Category Error
* `import-linter` inspects Python AST `import` statements (e.g. `import config.wads.torment`).
* In Omega Engine, WADs are **data loaded at runtime via filesystem paths** (`Path("config/wads/...")` or `wad_loader.py` iterating `self.wads_dir`).
* `import-linter` would report 100% clean even if `src/omega/` directly accessed arbitrary stack files!
* Furthermore, `import-linter` is not installed, whereas an in-house `FirewallChecker` (`src/omega/audit/firewall_checker.py`) **already exists**.

#### Live Leaks Found
* `src/omega/research/sandbox.py:548` contains:
  ```python
  wad_workspace = Path("config/wads/omega_research/workspaces") / str(proposal.id)
  ```
  This was hidden because `firewall_checker.py` had a hardcoded bypass:
  ```python
  if "config/wads/omega_research/workspaces" in code:
      continue
  ```

#### Proposed Solution
1. **Single Gateway Invariant**: `src/omega/oracle/wad_loader.py` is the **only** module in `src/omega/` permitted to access `config/wads/`.
2. All other modules needing stack assets must query `WADLoader` via protocol/interfaces.
3. Replace regex exemptions with an AST visitor gate (`scripts/check_m2_firewall_ast.py`) that forbids any `Path` or string literal containing `"config/wads"` across all of `src/omega/` except `wad_loader.py`.

---

### Domain 3: Identity Ontology: (Agent, Instance, Node) & Resolution

#### The Problem
The legacy field `source_entity` was overloaded to mean:
1. The **Agent Persona / Soul** (e.g. `carmack`, `roc_racoon`, `gaming_expert`).
2. The **Execution Session / Instance** (e.g. `ses_f0b67...` vs `ses_fa3f8...`).
3. The **Physical Node** (e.g. `n0` vs `n1`).

This created severe operational errors:
* Multiple chat sessions with John Carmack were confused, causing dispatches intended for the core consultant to land in a specialized game-logic session.
* A Node 1 chat session for the Gaming Expert (`ge-n1`) was misattributed as a distinct agent from Node 0 (`ge-n0`), causing alias flapping.

#### The Sourced Architecture
1. **Strict 3-Tuple Identity**:
   * `Node`: Cryptographic/network level, derived from Tailscale `whois` or mutual TLS certs.
   * `Agent`: Persistent archetype defined by `data/entities/{agent}/soul.yaml`.
   * `Instance`: Ephemeral execution session (`session_id` validated read-only against `opencode.db`).
2. **Fellegi-Sunter Under-Merge Bias (D3)**:
   * 1969 Fellegi-Sunter record linkage demonstrates that binary matching ("guess or drop") fails in distributed systems.
   * Over-merge is catastrophic and silent (delivering packets to the wrong agent).
   * Under-merge is noisy and cheap (packet remains unread in an inbox).
   * **Rule**: If confidence $R$ falls between threshold $\lambda$ and $\mu$, **do not guess**. Route to `data/handoff/pending/clerical_review/` with candidate flags.

---

### Domain 4: Epistemic Invalidation & The L4 Graduation Dilemma

#### The Problem
The Council governance layer needs to record when previous lessons, findings, or axioms are challenged, superseded, or retracted.
* The team initially attempted to model this using **AGM Belief Revision (1985)** contraction.
* AGM contraction is a *set deletion* operation.
* In an append-only, content-addressed, distributed CRDT store, deletion is impossible; Merkle-CRDT clocks require monotonic growth for convergence.

#### The Nanopublications / PROV-O Solution
* Retraction must be an **additive monotonic record**:
  ```yaml
  record_type: "retraction"
  retracts_id: "clm_01J8K..."
  invalidated_by: "ses_f0b67..."
  timestamp: "2026-10-01T00:55:00Z"
  rationale: "Empirical contradiction under NVMe benchmarks"
  ```
* **The "Scoped" Problem**: A finding is rarely globally false. It is false in a specific domain (e.g. "zswap is better than zRAM" holds on NVMe desktop, but fails on SD-card SBCs).
* We adopt **Contextual Knowledge Graphs (CKG)**: claims carry a `scope` tuple `(architecture, os, storage_type, context)`. Retraction records invalidate claims *relative to a scope*.

#### The Graduation Dilemma (L1 → L4)
* Previous proposal: "A lesson graduates to L4 Invariant Law if $N$ independent agent lenses agree."
* **Refutation (Ioannidis 2005)**: The probability of a finding being true actually *declines* with increasing numbers of underpowered, correlated studies.
* Carmack's critique: Renaming "agreeing count" to "power" is an unmeasurable rename.
* **Frontier Solution: Machine-Tested Graduation**:
  * **L1**: Raw conversation turn / observation.
  * **L2**: Distilled lesson in `proposed_lessons.yaml`.
  * **L3**: Formally structured proposal with an attached **machine test** (AST rule, unit test, or deterministic benchmark).
  * **L4 (Invariant Law)**: Promoted **only** after its attached machine test passes across $N$ commits and across both nodes with 0 regressions.
  * *Negative Rule*: If a principle cannot be verified by machine code, it cannot become L4. It remains an L2/L3 guideline.

---

### Domain 5: Infrastructure & Supervisor Hygiene

#### Forensic Findings
1. **The 81MB Crash Loop**:
   * `config/systemd/omega-research.service` had `ExecStart` pointing to `omega.workers.background_researcher.run`.
   * The module was missing from `src/omega/workers/`.
   * Systemd restarted the worker every 30 seconds since July 16, appending `ModuleNotFoundError` to `data/entities/roc_racoon/workspace/HALL_OF_RECORDS/background-researcher/error.log` until it hit 81.5 MB.
   * Action: The log was untracked from git and gitignored; the systemd service must be updated or masked.
2. **Accidental Credential Staging**:
   * `git add -A data/coordination/` swept in 637 conversation transcript dumps (`data/coordination/sessions/`), which contained rotated LangSmith and GitHub PATs.
   * GitHub Push Protection successfully blocked the remote push.
   * The commit was reset soft, `data/coordination/sessions/` was added to `.gitignore`, and the clean tree was pushed.
   * Action: Stricter pre-commit filters to prevent staging large non-source directories.

---

## 4. Specific Questions for Frontier Model Review

### For Gemini 3.1 Pro (Systems Architecture & Distributed Logic)
1. **CRDT Monotonicity vs. Retraction**: In a two-node peer mesh where Node 1 may be offline for days, does recording retractions as monotonic Nanopublication-style records guarantee eventual epistemic convergence without split-brain state?
2. **Multi-Context Invalidation**: What is the most mathematically robust representation for scoped validity in context-bounded agent memory graphs (e.g. RDF-star, Multi-Context Systems, or labeled property graphs)?
3. **Queue Architecture**: Does Carmack's Option A-minus (in-place atomic JSON mutation with `flock`) withstand multi-process concurrency across dozens of rapid MCP subagents, or should we immediately shift to an append-only journal (`{packet_id}.receipts.jsonl`)?

### For Claude 3.7 / Sonnet 4.6 (Code Verification & Static Security)
1. **AST Firewall Enforcement**: Design the optimal Python AST validator to enforce the M2 boundary (`src/omega/` vs `config/wads/`). How should dynamic path resolutions like `Path(base) / stack_name` be constrained without false positives?
2. **Race Conditions in Handoff Receipts**: Analyze `tools.py:1358-1365`. If two instances of different agents execute `action="read"` on the same `packet_id` simultaneously, what failure modes exist with `fcntl.flock(LOCK_EX)` during in-place file rewrite?
3. **Supervisor Hardening**: How should systemd units for sovereign worker pools be configured to prevent runaway log generation when facing persistent `ModuleNotFoundError` or uncaught exceptions (e.g. `StartLimitBurst`, `StartLimitIntervalSec`)?

### For Claude Opus 4.6 (Epistemic Governance & Systemic Philosophy)
1. **The Machine Graduation Boundary**: Is the rule *"If it cannot be machine-tested, it cannot graduate to L4"* too restrictive for strategic, architectural, or ethical invariants? How can high-level sovereign mandates (like M11 Soul Integrity or M29 Remote Claim Integrity) be verified without human subjective bias?
2. **Divergent Node Governance**: How should governance handle intentional laboratory divergence (Node 1 being 1,196 commits behind Node 0 while actively innovating on local WADs)? How do we prevent canonical parity enforcement from crushing experimental freedom?
3. **The 10-Year Granite Test**: Evaluate the overall architecture. Where are the subtle, creeping dependencies that could cause this engine to rot over 5–10 years of autonomous execution?

---

## 5. Artifact & Repository Index

The review team in Antigravity IDE can inspect the following canonical files in the repository:

| Path | Purpose |
|:---|:---|
| `docs/strategy/RESEARCH_ANSWERS_20260930.md` | Primary research answers: AGM, Ioannidis, Fellegi-Sunter, EMNLP 2025. |
| `docs/strategy/RESEARCH_FINDINGS_20260930.md` | Earlier synthesis & dialectic findings. |
| `docs/governance/ARCHITECT_CORRECTIONS_20260930.md` | The Architect's five canonical corrections. |
| `docs/governance/WAD_ENGINE_BOUNDARY_FIRST_PRINCIPLES.md` | The first-principles boundary between engine and content. |
| `docs/governance/ADR-001-communication-protocol-as-data.md` | Architectural Decision Record for protocol-as-data. |
| `mcp_servers/omega_hub/hub_tools/tools.py` | Line 1358 read path bug and legacy handoff submission. |
| `mcp_servers/omega_hub/federation_store.py` | Store layout, pending query, and envelope submit. |
| `mcp_servers/omega_hub/federation_envelope.py` | Envelope schema, hashing, and validation logic. |
| `src/omega/audit/firewall_checker.py` | Native M2 firewall checker. |
| `config/systemd/omega-research.service` | The crash-looping service configuration. |
| `data/entities/makali_fusion/session_gnosis.md` | Current stamped session gnosis. |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ ANTIGRAVITY_REVIEW_BRIEFING ⬡ 2026-10-01 ⬡*
EOF
