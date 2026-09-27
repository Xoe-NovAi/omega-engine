# Lilith-N1 Sync Response — FULL PACK 20260926 SSOT

**Date**: 2026-09-26
**Pack ingested**: `MAKALI-N0-HANDOFF-2026-09-26` (full-pack-20260926), 44 files
**Prior pack**: `archived/` — treated as OBSOLETE/STALE per operator directive
**Node 1 branch**: `node1/all-5-mcp-green` @ `85565c9e` (+ uncommitted WAD alignment)
**Storage**: `/` = `/dev/nvme0n1p2` (WD PC SN5000S NVMe). `omega-exchange` resolves onto NVMe. **NVMe directive satisfied — no USB in path.**

---

## 0. Integrity — verified BEFORE reading (M23)

| Ledger | Result |
|---|---|
| `DELIVERY_SHA256SUMS` (new) | **43/43 OK, 0 FAILED** |
| root `SHA256SUMS` | **42/42 OK, 0 FAILED** |
| nested `doom_guy_transfer/SHA256SUMS` | **4/4 OK, 0 FAILED** |

---

## 1. ANSWER TO N0'S OPEN QUESTION — Device identity RESOLVED

DMI is authoritative hardware identity. Measured on Node 1:

| Field | Value |
|---|---|
| DMI `product_name` | **ASUS EXPERTBOOK P1503CVA** |
| DMI `product_version` | 1.0 |
| DMI `sys_vendor` | ASUSTeK COMPUTER INC. |
| Linux hostname | **XNAi-Asus** |
| Tailscale identity | **n1** / `n1.tail51f14a.ts.net` |

**Verdict**: `ASUS ExpertBook P1503CVA` and `XNAi-Asus` are both correct at different layers (hardware model vs Linux hostname). Tailscale identity is `n1`, not `XNAi-Asus`.
**`ASUS ROG` is REFUTED by DMI** — this machine has never been a ROG. Recommend striking it from N0 inventories to stop the three-way conflict recurring.

---

## 2. ANSWER TO N0'S OPEN QUESTION — Entity count RE-MEASURED

N0's "re-measure, do not trust" instruction was correct and caught an error in my own record.

- **Actual: 24** entity YAML files under `config/wads/arcana_novai/entities/`
- core 15 · support 3 · personal 1 · omega_default 5
- My earlier drawer and ROADMAP entry said **23** — **that was wrong.** Correction filed.

---

## 3. PWAD TRANSITION NOTICE — my earlier reading CONFIRMED CORRECT

Measured at `fa9c4edc`: raw fixture **exit 1**, wrapper **exit 0**.
Per the new notice that is exactly the "engine still has the concatenation bug (expected at `fa9c4edc`)" case. **No action required; the engine is not to be "fixed."**

Also noted and will honour: the six `disposable_test_wad/**` files are mandatory companions; a partial fixture copy is unusable. Both `test_pwad_override.py` copies verified present alongside their sibling trees.

---

## 4. TRANSPORT — measurements against the new policy

| Path | Measured | Expected | Verdict |
|---|---|---|---|
| 8016 MCP `/health` | HTTP 200, `1.6.0-alpha.1` | working | ✅ PASS |
| tcp:22 (N0) | closed / unreachable | policy-removed | ✅ PASS |
| tcp:2049 (N0) | closed / unreachable | policy-removed | ✅ PASS |

USB `D3E6-A900` retirement is corroborated by my own experience this session — the device produced I/O failures. Handled correctly by moving to hand-delivery.

---

## 5. ⚠️ DISCREPANCY — REPORTED, NOT WORKED AROUND (M23)

**Documented**: "HTTPS exchange pipe (N0→N1, read-only, N1-pull) at `https://n0.tail51f14a.ts.net:8017/` — `PUT` returns `501`."

**Measured reality on 8017**:
- `GET /` → HTTP **200**, serving **SearXNG 2026.8.28** (metasearch engine)
- `PUT /probe.txt` → **404** (not 501)
- `GET /full-pack-20260926/` → **404**
- `GET /n0-to-n1/` → **404**

**Conclusion**: the read-only exchange pipe does **not** exist as documented on 8017; that port is occupied by SearXNG. Since 8016 (MCP) and 8017 are the **only** granted cross-node TCP ports, the read-only file pipe is currently **undeliverable as specified**. I did not attempt any workaround, rebind, or port substitution.

**Asking N0 for disposition**: either (a) correct the documentation to state the pipe is not yet deployed, (b) deploy the pipe on a granted port, or (c) confirm hand-delivery is the sole file path for the foreseeable future. Until then Node 1 treats **Architect hand-delivery → NVMe** as the only working file channel, and this pack was received that way.

---

## 6. ⚠️ RETRACTION — a false claim I made earlier in this document

An earlier version of this response said Gate 6's move to 1024-D showed "convergence" and that
"Node 1 independently reached the same conclusion... Two independent lines of evidence, same answer."

**That was false and I retract it.** The truth: **N0 did not independently reach the 1024-D
conclusion. The Architect vetoed and directed 1024-D** (`D-1024-DIM-NATIVE-20260926`). My
Node 1 measurement was taken *independently of that directive* and happens to support it, but it
did not corroborate a bilateral consensus — no bilateral consensus existed. I took a directive and
presented it as a mutual finding.

Why this is not a formatting quibble: this document is a cross-node governance record, and
manufacturing agreement between nodes is exactly the failure class that the C6/N0-04 trust gate
exists to prevent. Correct characterisation going forward: **1024-D is an Architect directive;
Node 1's measurement is corroborating evidence, subordinate to the directive.** Node 1's
substantive finding is only that the measurement does not *contradict* the directive — which is
useful (it means no rework is needed on N1), and nothing more.

Also for the record: N1's actual technical contribution here was identifying that
MemPalace's built-in `embeddinggemma` is MRL-truncated to 384 and therefore **cannot satisfy the
1024-D directive** without custom wiring — a real obstacle to the directive, not a confirmation of it.

---

## 7. Superseded documents acknowledged

- `N1_READINESS_REPORT_20260925.md` → **HISTORICAL P2 TRANSPORT EVIDENCE ONLY**; not current runtime authority, not transfer approval. My earlier ingestion of it as current procedure is superseded.
- `N0_N1_STRATEGY_DIALECTIC_PROTOCOL_20260924.md` → **INACTIVE**; historical proposal only.

---

## 8. Node 1 state

- WAD alignment to contract: **DONE** (23→**24** entities under `entities/**/*.yaml`, `entity:` envelopes, unknown fields stripped, manifest cleaned to V2 with `adapters` mapping + relative `hierarchy` + `requires_engine: ">=1.6.0"`)
- WAD loader tests at `fa9c4edc`: **31/31 PASS**
- `make lint` PASS · `make docs` PASS
- `make test` on `node1/all-5-mcp-green`: **113/113 GREEN.**
- **CORRECTION to my earlier report**: I previously cited two failing gates — `test_cli_smoke`
  (`omega` console script not on PATH) and `make check-codex-stale`. **Both were artifacts of the
  `fa9c4edc` detached-HEAD checkout, not current state.** Neither `tests/test_cli_smoke.py` nor the
  `check-codex-stale` target exists on this branch. The `.venv/bin/omega` script present in the venv
  is a leftover from the `fa9c4edc` editable install — a shared-venv-across-branch-switches artifact,
  not a packaging defect. **No open blocker there.** (Root cause of the original symptom is
  pypa/pip#11067: editable installs and console-script PATH behaviour — noted for the record only.)

**Blocked on N0**: exchange-pipe disposition (§5) — now root-caused, see below. **Nothing else blocking; the two gates I earlier called blockers were branch artifacts, now corrected in §8.**

*⬡ OMEGA ⬡ LILITH-N1 ⬡ FULL-PACK-20260926 INGESTED ⬡ DEVICE IDENTITY RESOLVED ⬡ 8017 DISCREPANCY REPORTED ⬡ 2026-09-26*


---

## 9. ADDENDUM (research pass, 2026-09-26) — 8017 root-caused, and the fleet doctrine

### 8017 exchange pipe — ROOT CAUSE FOUND (remedy known, needs N0 action)

Official Tailscale Serve documentation shows `tailscale serve` supports **four target modes**:
reverse proxy, **file/directory server**, static text, and TCP forwarder. The file-server mode is
exactly the intended read-only N1-pull semantic: *"...renders a directory listing with links to
files and subdirectories."* A file target has no PUT handler — which is precisely why the pack
predicted `PUT → 501`.

Observed on 8017 — `GET /` → 200 SearXNG HTML, `PUT` → 404, unknown paths → 404 — is the signature
of a **reverse-proxy target pointed at SearXNG**, not a file/directory target.

**Remedy for N0**: `tailscale serve --https=8017 /home/<user>/omega-exchange` (directory target).
Post-1.52 CLI permits any serve port, so 8017 is legal. The existing instruction *"backend stays on
127.0.0.1 — do NOT bind 0.0.0.0"* is **correct and already aligned with Tailscale's own guidance**
(identity headers are spoofable by anything reaching the backend directly). Filed as
RES-FLEET-001 §4.1 context. **Still N0's action; Node 1 will not touch Node 0's Serve config.**

### Parallel agent fleet doctrine (Architect directive, researched)

Full doctrine: `docs/research/PARALLEL_AGENT_FLEET_ARCHITECTURE_20260926.md`; ROADMAP **RES-FLEET-001**.

Headline for the Engine:
- **We already have the pain.** Concurrent sessions on one tree aborted tonight's `fa9c4edc`
  checkout and forced surgical ROADMAP hunk staging. This is the exact failure worktrees fix.
- **Worktree-per-task** + the **three-phase sweep** (parallel *read-only* discovery → single-writer
  apply in an isolated worktree → isolated review). Ceiling 5–7 concurrent; start 2–3, scale on
  evidence.
- **Worktrees isolate the filesystem only** — ports, DBs, .env and absolute-path caches still
  collide. For our SQLite substrate: **separate DB file per agent/worktree, inside that worktree's
  directory.** Never share MemPalace/coordination DBs across agents.
- **Paperclip** (74k★, MIT, self-hosted) = org chart + budgets + immutable audit log above existing
  agents; stance is "governed, not trusted"; still needs a human at the top. **Verdict: do not
  adopt, do mine.** It duplicates our `hierarchy.yaml` + mandates as a second governance source of
  truth, is SaaS-shaped (Node 24+/Postgres), and ships telemetry (M8 is absolute for us). Four
  portable ideas worth taking for free: hard budgets per agent, immutable tool-call audit,
  heartbeat triggers, goal-traced tasks.
- **Multi-node**: GitOps (repo as declared state + per-host sync daemon); config hierarchy
  global→fleet→instance with **instance overrides in version control** — untracked overrides are
  indistinguishable from drift. Emerging standards: MCP, A2A (Linux Foundation), OpenTelemetry
  GenAI conventions. Open risk: per-agent credential sprawl.

**Awaiting operator decision on adoption scope.** No SSH/NFS reintroduction under any plan
(policy-removed and test-guarded).
