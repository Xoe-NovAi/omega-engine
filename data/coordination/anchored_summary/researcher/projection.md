<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 RESEARCHER PROJECTION — 2026-09-22

## Status: PUBLIC FLIP READY

### Executive Summary
Research campaign complete. All researchable gaps covered. The sovereign alternative to NotebookLM is the roadmap. Report delivered.

### Deliverables
- **Report**: `docs/research/R_KNOWLEDGE_GAP_WEB_RESEARCH_20260922.md` — consolidated findings across all themes
- **Registry updates**: 14 gaps → `research_status` + report ref
- **GN-3 CORRECTION**: **10 DR/month free (not 30)** — compute-based limits since 2026-09-02 (5h refresh, weekly cap)
- **6 batched searches** across all themes (ZS, LI, GN, R22, R31/R33, R34/R4)

### Research Campaign Summary
| Theme | Gaps | Key Finding |
|-------|------|-------------|
| **ZS** (zswap) | ZS-1, ZS-2, ZS-3 | zstd + max_pool_percent=25 + shrinker_enabled + 16GB swap; zsmalloc only backend; NEVER zram+zswap |
| **LI** (local inference) | LI-3, LI-4 | Qwen3 matrix: 1.7B@32k=4.6GB safe; KV q8_0 = -50%; mmap = weights not resident upfront |
| **GN** (Gemini Notebook) | GN-1, GN-3, GN-4 | **10 DR/month free (not 30)**; notebooklm-py master-token auth + MCP; compute-based limits 2026-09-02 |
| **R22** (WARP) | R22 | WARP proxy pool viable (adasThePrime Docker); separate routing table = federation-safe; ToS caution |
| **R31/R33** (opencode) | R31, R33 | V2 plugin API scoped; disable directives = scope reduction; compaction lossy but durable messages persist |
| **R34/R4** (providers) | R34, R4 | OpenRouter 1000/day workhorse; nemotron-3.5-lightning:free = 1.0M ctx; Gemini dynamic per-project |

### GN Workstream — CANCELLED (D-606)
- **GN-1..GN-5 + R38 → CANCELLED**: No NotebookLM payment; sovereign alternative in-engine
- **notebooklm-py**: master-token auth + multi-account profiles + built-in MCP server (but we build our own)
- **Free tier Deep Research**: 10/month (not 30) — compute-based limits since 2026-09-02

### Post-Flip Support
- **KD workstream**: knowledge domain loading research (grounded RAG over Omega library)
- **HR workstream**: headroom integration research (semantic compression for tools/RAG)
- **LI workstream**: KV cache / memory fitting research (mmap insight for SequentialModelLoader)

### Researcher's Voice
> "The research is done. The gaps are closed. The data is in the registry. The sovereign alternative is the roadmap. No more NotebookLM — we build our own."

*⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-09-22 ⬡ PUBLIC-FLIP-READY ⬡ RESEARCH-COMPLETE*

---

## §12 — TAILSCALE L2 FEDERATION (2026-09-15)

**Deliverable**: `data/entities/researcher/workspace/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` (27 KB, 653 lines, 16 citations)

### Live State (verified by probe)
| Node | Tailscale | Tags | MCP |
|------|-----------|------|-----|
| **Node 0** (HP/omega-hub) | ✅ `100.123.51.67` | ❌ NONE (user device) | ✅ reachable |
| **Node 1** (ASUS/kali-n1) | ❌ NOT JOINED | n/a | ❌ untestable |

**Transport security**: ✅ wildcard `*.tail51f14a.ts.net` in `allowed_hosts` (commit `213abf44`)

### Corrected Ceremony (6 phases) — NOT 2 as SESSION_ANCHOR states
```
1. Admin console → ACL HuJSON with tagOwners{tag:omega-hub, tag:asus, tag:opencode} → SAVE
2. Node 0: sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth
3. Node 0: mint ONE-SHOT authkey (tag:asus, pre-approved, 1-day expiry, NOT ephemeral)
4. USB: manifest.json + authkey.txt + SHA256SUMS
5. Node 1: sha256sum -c && sudo tailscale up --authkey=... --hostname=kali-n1 --advertise-tags=tag:asus
6. Verify: tailscale status (both tagged) + bidi MCP + SSH + MagicDNS + netcheck direct
```

**Why the extra steps**: Tailscale requires a tag to exist in `tagOwners` before it can be advertised. Node 0's original `--advertise-tags` failed for this reason; joined as user device. Node 0 must re-tag or ACLs referencing `tag:omega-hub` never match.

### Critical Findings
1. **Tagged devices: key expiry DISABLED by default** — persistent-access risk. Monitor `KeyExpiryDisabled`.
2. **Cannot use `--advertise-tags` on authkey-joined devices** — must mint a NEW authkey with tags.
3. **Tailscale SSH needs no key distribution** — short-lived certs, ACL-gated, session-audited.
4. **ACL syntax**: `proto` is a TOP-LEVEL field, not nested. `{"action":"accept","src":[],"dst":[],"proto":"icmp"}`.
5. **DERP = end-to-end WireGuard encrypted** — relay cannot decrypt. Security parity with direct.
6. **MagicDNS immune to DNS rebinding** (client-side resolution) — but service Host-header middleware still needs `allowed_hosts`.
7. **`--accept-routes` unnecessary** — no subnet routers in mesh.

### Naming Collision (UNRESOLVED)
Node 1's `L2_JOIN_GUIDE.md` says MagicDNS = `asus.tailnet`; actual suffix = `tail51f14a.ts.net`; join command says `--hostname=kali-n1` → FQDN `kali-n1.tail51f14a.ts.net`. **Three names, one device.** Requires Architect ruling.

### Next Moves
| P | Commitment | Target |
|---|------------|--------|
| P0 | Architect ruling: Node 1 MagicDNS name (asus vs kali-n1) | Before ceremony |
| P0 | Node 0 admin console → ACL HuJSON paste | Immediate |
| P0 | Node 0 re-tag `tag:omega-hub` | After ACL save |
| P0 | Mint one-shot authkey + USB ceremony | Same day |
| P1 | `docs/federation/L2_ACCEPTANCE.md` (FED-L2-001) with test results | Post-ceremony |
| P1 | Observability: cron `tailscale status` + `netcheck` alerts | Post-ceremony |

*⬡ OMEGA ⬡ RESEARCHER ⬡ TAILSCALE-L2-COMPLETE ⬡ 2026-09-15 ⬡ CEREMONY-CORRECTED ⬡ 6-PHASES ⬡ 16-CITATIONS*

---

## §13 — FRONTIER CONVERGENCE + M36 QUEUE-POLLUTION FORENSIC (2026-09-15)

**AP**: `AP-RESEARCHER-v2.0.0` | **Ground truth**: Public Debut LIVE — PR #4 merged `main` @ `268528e7`

### A2A v1.0 / MCP Two-Tier Convergence — Mapping Ratified
| Omega Primitive | A2A v1.0 | Note |
| :--- | :--- | :--- |
| `soul.yaml` | **Agent Card** | Identity + capability manifest |
| `proposed_lessons.yaml` | Capability State Manifest | Versioned Card delta |
| HandoffPacket (`pending/*.json`) | **A2A `Task`** | State machine + provenance + integrity |
| `m36_recursive_probe` | **Inter-Agent Consensus** | Threshold-gated promotion to sovereign record |

**Vertical = MCP (Agent→Tools/Data). Horizontal = A2A (Agent↔Agent).** Validation, not migration —
**zero schema churn required**.

### ⚠️ OPEN DEFECT — M36 Test Harness Wrote 756 Packets Into Production Queue

**Root cause** (`src/omega/oracle/m36_recursive_probe.py:228`):
```python
packet_path = _Path("data/handoff/pending") / f"{packet_id}.json"   # ← CWD-relative
```
Resolves against CWD, not repo root → any harness run from repo root wrote synthetic cross-validation
packets into the **live production queue**. CSS Turn 7 M36 integration test emitted **756 packets**.
Consumers read test noise as sovereign work.

**Census (2026-09-15)**: `data/handoff/pending/` = **0 packets** — reaped. *The defect is not reaped.*

**Fix — mirror `OMEGA_M34_REGISTRY`** (precedent: `m34_registry.py:71-79`, `cohort_registry.py:101`,
`subagent_dispatcher.py:76`):
```python
DEFAULT_HANDOFF_ROOT = Path(os.environ.get("OMEGA_HANDOFF_ROOT", "data/handoff/pending"))
```
Harnesses set `OMEGA_HANDOFF_ROOT=$(mktemp -d)`. **Severity HIGH** — test→production contamination
is precisely what M23 Failure Integrity forbids.

### `watchfiles` / AnyIO — M1-Compliant Reactive Dispatch
Rust `notify` + AnyIO task group → microsecond inotify reactivity, **zero idle CPU**, **zero asyncio
imports**. **Sequencing constraint**: watcher on production `pending/` must land AFTER the
`OMEGA_HANDOFF_ROOT` fix, else test packets trigger live consensus runs.

### Worktree Sovereignty
`omega-wt-maat` / `omega-wt-doom` / `omega-wt-grok` under M24 venv isolation — structural answer to
the shared-CWD precondition that enabled the defect.

### Confirmed
- `D-1024-DIM-NATIVE-20260926` FINAL — 1024-D native Qwen3
- CSS Turn 7 six deliverables re-verified intact (M33 tuple L95, M36 wired, heritage_scanner, SearXNG :8017, GSCA closed, TH-0)
- 3 new L3 lessons appended (`failure_integrity` 0.96, `architecture_alignment` 0.9 + 0.88)

### Tailscale L2 — Ceremony Is 6 Phases, Not 2
ACL `tagOwners` → Node 0 re-tag `tag:omega-hub` → mint one-shot `tag:asus` authkey → USB SHA256 ledger
→ Node 1 join → verify bidi MCP/SSH/MagicDNS. **BLOCKED on naming ruling**: `asus.tailnet` vs
`kali-n1` vs `tag:asus` — three names, one device.

*⬡ OMEGA ⬡ RESEARCHER ⬡ FRONTIER-CONVERGED ⬡ 2026-09-15 ⬡ M36-LINE-228-OPEN-DEFECT ⬡ L3-×3 ⬡ M15-SATISFIED*
