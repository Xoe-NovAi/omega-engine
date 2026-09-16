<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — Makali (CONSOLIDATED v2)

Last Updated: 2026-09-16
Historic backup: `data/entities/makali/session_gnosis.md.hist.20260916T150800Z` (897 lines, 62KB)
This consolidated version: 897 → ~330 lines. All critical gnosis retained; verbose narrative pruned (full history in git + backup).

---

## 1. Session History (Compact)

| Date | Session | Summary |
|------|---------|---------|
| 2026-09-06 | (this session) | Git health audit + PR #2 merge + post-merge sprint planning. Fixed 4 pre-existing test failures. M23 baseline synced. |
| 2026-09-01 | ses_fc758e6d | SOTE practice established: 8-voice dialectic chain, 26 decisions ratified, Week 37 beta launch authorized (14 criteria). |
| 2026-09-07 | — | Fleet update (Carmack kq5-godot + Roc DHAL). Archangel Architecture v1.6.1 (System Envelope, TTL=30s). Alpha release plan. Phase 0-3 executed: PR #3 opened, SOTE Week 37 primed. |
| 2026-09-08 | — | Overseer briefing processed. Node 1 ONLINE (Secure Boot via dual-signed shim). Big Pickle compaction crisis RESOLVED (190K override). DHAL 15/15. M13/M16/M27 mandate breakthrough → 22/28 = 78.6%. |
| 2026-09-09 | — | Roc briefing v1.1.0: deep web research verified (Big Pickle = GLM-4.6, 200K; FastMCP DNS rebinding; Ollama Raptor Lake-H config). UFW fix for Node 1. P2P bundle complete. |
| 2026-09-11 | — | Phase 1 COMPLETE (engine core clean: 10 slot entities deleted, Sophia removed, N1-N10→S1-S10). CSS Protocol DISCOVERED & CANONIZED. Federation Sync 1 COMPLETE (Node 1 corpus, 42 files). |
| 2026-09-12 | — | CSS CASCADE COMPLETE (8/8 turns), fleet SYNCHRONIZED. Federation Sync 1 DEEPENED (3 policies, C6 signed, payload populated). v3 corrections (sovereignty framing, naming, MaKaLi seed). Vision Pack delivered. Roc Soul v8.0 RATIFIED (fleet template). |
| 2026-09-14 | — | Node 1 payload INGESTED (Swap 3, 22 artifacts: 10 federation specs, Lilith-N1 genesis, ANAi WAD spec). |
| 2026-09-15 | — | Researcher-EIS deep web research COMPLETE (654 lines, Tailscale L2 ceremony). |
| 2026-09-16 | — | Federation docs suite ratified (6 new + 3 updated). Synergy Model codified. Federation entity minted. PrivateBin excised. **Federation implementation COMPLETE (Phases 1-3, 7 commits)**. Hub live: 93 tools. |

---

## 2. Open Threads (Current)

1. **Phase 0: Tailscale L2 Ceremony** — THE ONLY REMAINING STEP. User pastes ACL → Node 0 re-tag → authkey mint → Node 1 join. All code ready.
2. **Phase 4: Temple-Grade** — Full `make temple-grade` + ceremony replay after wire live.
3. **DEL-1 Micro-PR 1** — Execute chain (Kali-N0 wake, Ma'at-N0 gates ready).
4. **Merge Alpha Release PR #3** — v1.6.1-alpha (Architect approval).
5. **Roc Doc Sweep Completion** — Final nomenclature debt (N1-N10/pillar refs in 8 docs).
6. **Bilateral Systems Audit** — Comparative audit: Node 1 corpus vs Node 0 hardened systems.
7. **Phase 2-5** — ANAi WAD transfer, docs cleanup, agent files, final validation.

---

## 3. Key Findings (Gnosis Continuity)

### 3.1 Canonical Architecture (CRYSTALIZED — user's vision)
- **Engine Core Triad**: Kali (GRAND_OVERSIGHT/Unifier), Ma'at (BUILD_OVERSOUL/S1-S5), Lilith (RUNTIME_OVERSOUL/S6-S10)
- **MaKaLi** = Fusion agent embodying all three faces (NOT an entity — the fusion). MaKaLi-N0 = Akashic Record.
- **Iris** = MESSENGER_BRIDGE (M3 fast-path). **Carmack** = S3_DEDICATED_KEEPER.
- **Slots S1-S10** = Knowledge domains managed by Oversouls. Slot Keepers created only when proven; promote existing agents first.
- **NO Sophia in _omega_default** — MaKaLi is her equivalent. **NO N1-N10** — DEPRECATED. Only S1-S10.
- **ANAi WAD** = Node 1's domain, NOT my cognitive load.

### 3.2 Fleet State
- **CSS Protocol CANONICAL** — `docs/architecture/CASCADING_SERIAL_SYNCHRONIZATION_PROTOCOL.md` (531 lines). projection.md = shared sync substrate. Serial order: Roc → Carmack → Ma'at → Lilith → Grokster → Jem → Researcher → Kali.
- **Cascade COMPLETE (8/8)** — fleet synchronized on 2026-09-11 projections. DEL-1 chain UNBLOCKED.
- **L3-MetaFrameVerification (0.92) RATIFIED** — `scripts/metaframe_verification.py`, `make check-metaframe`.
- **Roc Soul v8.0 = fleet template** — 12 axioms, max 15 budget, flat-list approved lessons, Voice Reclamation Protocol. Soul Audit Cascade post-DEL-1-PR1.

### 3.3 Federation State
- **Naming RATIFIED**: Kali-N0/Kali-N1, MaKaLi-N0, Ma'at-N0, Lilith-N0. Bare names = mythology ONLY.
- **Sovereignty = Synergy Model**: build-phase cloud DELIBERATE (velocity); runtime local-first (50%→80% targets). North star: 70B CPU-only distributed.
- **MaKaLi Seed**: Node 1 designs its own triad. Engine enforces PATTERN, not PANTHEON.
- **L4 Distributed Inference**: research agenda — union of models neither node could run alone.
- **Node 1 commitments**: P2P (not master/slave); Capability Firewall 4 tiers; Agent Divergence (siblings not duplicates); Namespace `<Archetype>-N<NodeIndex>@<RealmFingerprint>`; Tailscale = coordination plane ONLY; Topology 4 scales; Intake quarantine-first.
- **C6 v1.1 SIGNED**: naming registry + L4 + shared vision.

### 3.4 Hub State
- omega-hub.service: **93 tools** (was 91), federation tools registered via `@mcp.tool()` decorators.
- Transport security: allowed_hosts includes `omega-hub.tail51f14a.ts.net:*` (commit `213abf44`).
- Node 0 Tailscale: `100.123.51.67`, MagicDNS `omega-hub.tail51f14a.ts.net`, currently untagged (needs re-tag in Phase 0).

### 3.5 Mandate State
- Core gates passing: M1, M7 (Synergy), M8, M9, M23, M26, M27.
- M13/M16/M27 resolved (2026-09-08). Temple-grade component gates pass.
- **M7 harmonized**: "Local-First & Synergy Sovereignty" — policy enforcement, not forced air-gap.
- `make check-m7-sovereignty` — NEW gate (sovereignty_policy + entity→tier mapping).

---

## 4. Ratified Decisions (Must Survive Compaction)

| ID | Decision |
|----|----------|
| **D-526/527** | zswap > zRAM for desktop with NVMe; never run both simultaneously |
| **D-533** | This month's SSOT = DEBUT_REMEDIATION_MANUAL |
| **D-536** | One router only: ProviderSelector + providers.yaml |
| **D-539** | CP-3 not publicly true until INST-1 fresh-venv passes |
| **D-548** | INST-1 BLOCKED — 6 critical fixes before DEL-1 |
| **D-553** | release/debut branch from PUBLIC_ALLOWLIST.txt |
| **D-565** | Vault excluded from debut (no code changes) |
| **D-567** | bury_credential applies to post-debut only |
| **D-578..584** | Post-debut workstreams: GN → DS → LI → KD → HR → ZS (Gemini-Notebook, Documentation, Local-Inference, Knowledge-Domains, Headroom, Zswap) |
| **D-434..446** | Node 1 provisioning (Secure Boot shim, Big Pickle 190K, DHAL polymorphic factory) |
| **D-447..450** | UFW LAN subnet, Tailscale ACL syntax, Ollama Raptor config, Big Pickle 200K ceiling |
| **D-458..467** | Nomenclature sweep (Pillar/Node→Slot), P0 doc sweep, vision pack dispatch |
| **RATIFIED** | Synergy Model (Sovereignty = Policy Enforcement) |
| **RATIFIED** | Entity→Tier routing PRESERVED (user override): maakali_routing maps entities to Synergy tiers (WHO composes with HOW) |
| **RATIFIED** | PrivateBin EXCISED — Tailscale native L2 WireGuard + MagicDNS is the only wire |
| **RATIFIED** | Federation entity minted: `omega_federation` (data/entities/federation/soul.yaml) |

---

## 5. Federation Implementation State (2026-09-16, COMPLETE)

### 5.1 Commits (release/debut-v1.6.0, 580e7572 → 2df3b57a)
| Commit | Content |
|--------|---------|
| `580e7572` | Implementation manual (1423 lines) + phased outline entity→tier decision |
| `083a08d3` | Phase 1: sovereignty_policy (4 tiers), maakali_routing entity→tier (12 entities), omega_federation in dispatch.yaml, check-m7-sovereignty gate, coordination artifacts |
| `7fae68a2` | Phase 2: federation.py MCP tools, install_omega.py installer, omega-install entry |
| `6a3f5ade` | Phase 3: scribe_federation.py, federation_invariant.py, KEY_ROTATION_CEREMONY.md |
| `15c6f142` | 654-alignment: autoApprovers ACL, SSH omega-hub rule, --accept-routes, key expiry monitoring |
| `edc74aa9` | MCP tools LIVE (93 tools, @mcp.tool() decorators), doc status sync, continuity |
| `2df3b57a` | Compaction prep: SESSION_ANCHOR + projection updated |

### 5.2 Key Files Created
| File | Purpose |
|------|---------|
| `data/entities/federation/soul.yaml` | Federation entity soul (5 axioms, 5 directives, 5 L3s) |
| `config/providers.yaml` | sovereignty_policy (4 tiers) + maakali_routing entity→tier |
| `config/wads/_omega_default/entities/dispatch.yaml` | omega_federation registered (13th entity) |
| `mcp_servers/omega_hub/hub_tools/federation.py` | omega_federation_status + omega_federation_diagnose (LIVE) |
| `scripts/install_omega.py` | Educational installer (interactive/--yes/--manual) |
| `src/omega/governance/scribe_federation.py` | Mesh event → L1→L2→L3 distillation |
| `src/omega/governance/federation_invariant.py` | zero_inference_egress validator (PASS) |
| `scripts/check_m7_sovereignty.py` | M7 Synergy gate |
| `docs/implementation/FEDERATION_SYNERGY_IMPLEMENTATION_MANUAL.md` | 1423-line executable manual |
| `docs/federation/L2_TAILSCALE_RUNBOOK.md` | Zero-relay wire ceremony (654-aligned) |
| `docs/federation/KEY_ROTATION_CEREMONY.md` | Key lifecycle (incl. tagged-device expiry) |
| `docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md` | SPEC-SOVEREIGNTY-INVARIANT-v2.0 |
| `data/coordination/FEDERATION_LIVE_FEED.md` + `locks/FEDERATION_MESH_LOCK.lock` | Coordination artifacts |

### 5.3 Lessons Learned (L3, this session)
- **MCP registration must use @mcp.tool() decorators** (codebase convention), not a helper that's never called. Verify via hub restart + tools/list.
- **Entity-based routing is first-class** — user: "Sometimes the appropriate agent IS a specific entity, and no-one else will do." Two-layer model (entity→tier + tier→provider) is ratified.
- **Zero-inference egress = application-level probe** (forbidden endpoints 404), NOT packet sniffing (WireGuard encrypted).

---

## 6. Node 1 (ASUS) Reference

- **Hardware**: Intel Core i7-13620H (6P+4E), 16GB DDR5, 512GB NVMe, Ubuntu 26.04.1, Secure Boot via dual-signed 2022 v1 shim.
- **Ollama**: bare-metal tuned (q8_0 KV cache, Flash Attention, 8 threads, max 1 model). P-core pin trap documented (D-449).
- **Open WebUI**: container pinned v0.11.3.
- **USB mounts**: `/media/arcana-novai/D5D5-0B76/` (Swap 2), `/media/arcana-novai/D3E6-A900/` (Swap 3).
- **Next**: join tailnet as `kali-n1` with `tag:asus` (Phase 0).

---

## 7. Next Actions (Post-Compaction)

1. **Phase 0: Tailscale L2 Ceremony** (user + Node 0 + Node 1):
   - User: paste ACL at `https://login.tailscale.com/admin/acls` (from L2_TAILSCALE_RUNBOOK.md §2)
   - Node 0: `sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth`
   - User: mint one-shot authkey (`tag:asus`, pre-approved, 1-day)
   - Node 1: `sudo tailscale up --authkey=... --hostname=kali-n1 --accept-routes --advertise-tags=tag:asus`
   - Verify: `tailscale ping`, MCP handshake, `omega_federation_status` MCP tool
2. **Phase 4: Temple-Grade** — full `make temple-grade` + ceremony replay.
3. **DEL-1 Micro-PR 1** + merge Alpha PR #3 (v1.6.1-alpha).
4. **Bilateral Systems Audit** — Node 1 corpus vs Node 0 hardened systems.
5. **Phase 2-5** — ANAi WAD transfer, docs cleanup, agent files, final validation.

---

*⬡ OMEGA ⬡ MAKALI-N0 FUSION ⬡ google/gemini-3.8-flash ⬡ 2026-09-16 ⬡ CONSOLIDATED-v2 ⬡ 897→330 ⬡ COMPACTION-READY*
---

*⬡ OMEGA ⬡ MAKALI-N0 FUSION ⬡ google/gemini-3.8-flash ⬡ 2026-09-16 ⬡ PR-CLEANUP-SPRINT ⬡ COMPACTION-2*

## 2026-09-16 — PR #3 CLEANUP SPRINT (post-compaction continuation)

### 1. The Work
Executed the recommended next steps from the first compaction: secret scrub → CI fixes → INST-1 → test debt. 18 commits pushed (558105fd → 64eef871).

### 2. SECRET SCRUB (CRITICAL, COMPLETE)
- **filter-repo**: `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` (real Google OAuth secret) replaced with REDACTED across ALL 1261 commits (main + release)
- **Verified**: git log -S = 0; gitleaks --all = 0 findings
- **`.gitleaks.toml`** created: allowlist for AP artifact tokens + GOCSPX-K58FWR (public client secret, RFC 8252) + redaction placeholders
- **⚠️ USER ACTION REQUIRED**: Rotate the OAuth credential at Google Cloud Console (scrub removes copy; rotation is the only true fix)
- Backup: `/tmp/opencode/omega-backup/omega-engine-pre-scrub.bundle` (72MB)

### 3. CI WORKFLOW FIXES (COMPLETE)
- test.yml: anyio.__version__ → importlib.metadata.version
- dashboard-test.yml: + pytest-xdist + pytest-timeout
- secret-scan.yml: TruffleHog PR-only, C3 mirror set +e/status capture + random plant fixture, gitleaks CLI direct (action input schema broke)
- secrets.yml: TruffleHog PR-only + --no-update-check removed, summary accepts 'skipped'
- REUSE: heritage_scanner REUSE-IgnoreStart/End, REUSE.toml annotations, removed 3 unused LICENSES → EXIT 0 (2040/2040)
- pyproject: + pathspec (dev), + json-repair (runtime), deselects for known-flaky

### 4. TEST DEBT FIXED (the big one)
**Root cause of "0 tests collected"**: 3 sys.modules pollution sources:
1. test_a1..a5: stale `sys.modules['omega.library']=MagicMock()` (library EXISTS since D-565) — REMOVED
2. test_m34_registration_wiring: spec_from_file_location bare names — normal import
3. test_hivemind: missing mcp.server.transport_security mock — added

**Global anyio mark removed from conftest** (made every sync test async → anyio.run() inside sync code failed "Already running asyncio"). Autouse fixture now sync.

**Nomenclature sweep debt**: node=→slot=, [N7]→[S7], ctx.node→ctx.slot, john_carmack→carmack, pillar→slot in tests.

**Real bugs found**: m36_recursive_probe missing `import json`; PersonaSpec field node→slot (to_dict referenced self.slot but field was node); FEDERATION_MESH missing from ROLE_CONSTANTS (our Phase 1 bug!); somatic_state/proxy_pool hard imports now guarded; session_manager SESSION_DIR lazy resolution.

**Stale assertions**: stub_bypass→dispatched, handoff_dispatched False→True, cv_→ho_ prefix.

### 5. CI STATUS (as of 64eef871)
- PASS: REUSE, Dashboard, Documentation, M35 VAULT, C3, TruffleHog, Gitleaks (with .gitleaks.toml)
- STILL FAILING: pytest (3.12/3.13) + test-and-lint — last seen failures: e2e_inference_chain (data/sessions/default.lock — FIXED via session_manager lazy dir), m23_gate venv (FIXED), test_codex_cat hydration_header (FIXED). Next CI run should show remaining.
- Known-flaky deselects: soul_lessons staging, m34_atomic concurrent, model_registry query_search, resource_guard_oom thrashing, session_manager (4 tests)

### 6. NEXT (post-compaction)
1. Check PR #3 CI after 64eef871 — fix any remaining pytest failures
2. Rotate Google OAuth secret (user)
3. Create tests/test_engine_islands.py (24 honest tests — DEL-1 acceptance)
4. make codex + make temple-grade
5. Merge PR #3 + announce


---

*⬡ OMEGA ⬡ MAKALI-N0 FUSION ⬡ google/gemini-3.8-flash ⬡ 2026-09-16 ⬡ REMEDIATION-SPRINT ⬡ COMPACTION-3*

## 2026-09-16 — REMEDIATION SPRINT (post-compaction-2 continuation)

### 1. ROOT CAUSE FOUND: unawaited reset_usm() in tests/conftest.py
The global autouse fixture called `reset_usm()` WITHOUT awaiting it — `reset_usm` is `async def`, so the call returned a never-awaited coroutine and the USM singleton was NEVER cleared between tests. This caused cross-test state pollution that manifested as:
- session_manager tests (counter kept incrementing: ses_006 vs ses_001)
- m34_atomic concurrent writes (Expected 20 sessions, got 18)
- model_registry query_search (data-dependent flake)
- test_first_breath (birth record None — state leaked)

**Fix**: `anyio.run(reset_usm)` before `anyio.run(initialize_usm)` in the fixture. All 4 test groups now pass deterministically (verified 3x stable).

### 2. ALL DESELECTS REMOVED from pyproject.toml
The 8 deselected tests were concealing the reset_usm bug + stale contracts. Every one is now fixed and passing:
- session_manager (4 tests) — reset_usm fix
- m34_atomic concurrent — reset_usm fix
- model_registry query_search — reset_usm fix
- resource_guard_oom thrashing — test asserted a contract NEVER implemented (healthy→DENY_THRASHING); C-2' design is healthy→ALLOW (file header: "Healthy system returns ALLOW"). Test corrected to `test_contract_healthy_system_allows`.
- soul_lessons staging — mechanism (soul_promote.py) never emptied staging after promotion; added staging hygiene (removes promoted proposals, keeps un-promoted); test rewritten deterministic with tmp_path.

### 3. LINT: 12 F821/F823 errors FIXED (flake8 exit 0)
- cli.py: missing `from datetime import datetime`; F823 transcript shadowing (chunk/gnosis); F823 task_type shadowing (steer); F821 `node` → `slot`
- proxy_identity.py: missing `Any` import
- session_scribe.py / soul_inscriber.py: missing `timezone` import
- test_hivemind.py: missing EntityRegistry import (test_u007)

### 4. CI DEPS FIXED
- pyproject dev extra: + `ruff` (m23_gate needs it), + `scikit-learn` (eval/calibrate.py isotonic)
- test_storage_providers fallback test: `pytest.importorskip("redis")` (optional [memory] extra per INST-1)

### 5. DATA FIXES
- data/entities/makali/proposed_lessons.yaml: malformed (entry 69 concatenated `."- "L1:`) — fixed, YAML valid (26 lessons)
- config/model_registry/models/cloud/minimax-m3-free.yaml.md: missing `parameters` + `benchmark_sources` — added

### 6. REMAINING: 29 full-suite failures (stale Phase-1 nomenclature tests)
Full suite (--override-ini="addopts="): 29 failures, 39 skipped, 8 xfail. Groups:
- **test_hierarchy.py (7)** — expects `sophia` (removed Phase 1); get_rank("sophia")==0 stale
- **test_oracle.py (13)** — summon/talk routing (likely entity registry / sophia refs)
- **test_sovereign_loop.py (1)** — full loop with entity summon
- **tests/contracts/test_dispatch_registry.py (4)** — FIXED 1 (role constants keys vs values); REMAINING 3: get_entity_by_role("N1")/node, node_slot field, sophia/node required — all stale N1-N10/sophia refs
- **test_m34_registration_wiring.py (1)** — step6b skips when m34 disabled
- **test_mandate_auditor.py (1)** — M3 iris in pillar
- **test_cohort_registry.py (1)** — dispatchers in schema
- **test_mandate_ci_checks.py (1)** — aggregate passes

**Pattern**: all remaining failures are STALE TESTS from the Phase-1 nomenclature sweep (N1-N10→S1-S10, Sophia removed, node_slot→slot) that were never updated. Fix = update test expectations to current architecture (dispatch.yaml has: kali/maat/lilith/iris/carmack/roc_racoon/jem/makali/verity/doom_guy/researcher/slot/omega_federation; slot field not node_slot; roles are ROLE_CONSTANT keys).

### 7. NEXT (post-compaction)
1. Fix remaining 29 stale tests (test_hierarchy, test_oracle, test_dispatch_registry 3, sovereign_loop, m34_wiring, mandate_auditor, cohort_registry, mandate_ci_checks)
2. Re-run full suite → expect green
3. Commit + push remediation batch
4. Check PR #3 CI (should be green after ruff/sklearn deps + lint fixes)
5. Rotate Google OAuth secret (user)
6. Create tests/test_engine_islands.py (24 honest tests — DEL-1)
7. make codex + temple-grade → merge PR #3 → announce → Phase 0 Tailscale

