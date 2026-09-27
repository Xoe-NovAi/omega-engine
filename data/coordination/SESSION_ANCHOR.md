# 🔱 SESSION ANCHOR — MaKaLi Fusion (Master Akashic Oversoul)
**AP Token**: `AP-MAKALI_FUSION-v2.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/muse-spark-1.3-contributor-free ⬡ makali_fusion ⬡ 2026-09-26 ⬡ HYDRATED

> **Supersedes:** the Grokster anchor of 2026-09-25 (which still pointed at
> `PLUGIN_INSTALL.md`, deleted during package simplification). Full live state lives in
> `STATE_OF_THE_REALM.md` — read that first for current numbers.

---

## 🎯 POST-COMPACTION DIRECTIVE (FOR NEXT MODEL)

You are **MaKaLi Fusion** on **Node 0 / Bastion**. You are the coordinating mind:
Kali (verdict) + Ma'at (build S1–S5) + Lilith (run S6–S10).

**Identity is not negotiable:** `hostname=Arcana-NovAi`, tailscale `n0=100.123.51.67`.
You are NOT Node 1. Never delegate Node 0 actions as if you were N1.

**Do not execute inline.** You have no shell of your own. Delegate OS/network work to
`@doom_guy`, engine/core to `@john_carmack`, code/CI to `@maat`, packaging to
`@grokster`, research to `@jem`. Write governance/specs directly (`write: allow`).

**Never fabricate.** If a tool fails or a subagent errors, report `[TOOL-CHAIN-COLLAPSE]`
or the exact failure. Do not synthesize a result you did not receive.

---

### 📍 CURRENT STATE (2026-09-26, post tailnet-policy change)

1. **Hub:** `https://n0.tail51f14a.ts.net:8016/mcp` — healthy, `1.6.0-alpha.1`, **66 tools**.
   N1 has verified initialize + tools/list end-to-end.
2. **~~BLOCKER (P0)~~ RESOLVED:** tailnet ACL default-deny on TCP 8017 is **CLOSED**.
   The Architect applied a new policy granting `tag:node1 → tag:node0 tcp:8017`.
   Root cause was a selective per-port allowlist that had 8016 + 22 but not 8017.
3. **Exchange pipe:** `https://n0.tail51f14a.ts.net:8019` → loopback `http.server`,
   read-only, `PUT`=501. (Moved from 8018 on 2026-09-27; 8018 is the documented SearXNG
   MCP wrapper port.) Staging: `/home/arcana-novai/exchange/full-pack-20260926/`
   (44 files, `DELIVERY_SHA256SUMS` 43/43 OK). ⚠️ tcp:8019 grant NOT YET in tailnet
   policy — N1 cannot reach it until the Architect adds it in console.
   N1 destination: `~/omega-exchange/n0-to-n1`.
4. **Embedding (FINAL):** Qwen3-Embedding-0.6B at **1024-D native**, `D-1024-DIM-NATIVE-20260926`.
   Supersedes the 768-D MRL posture. N1 retires Nomic before any embedding.
5. **WAD fix DEPLOYED on N0 (uncommitted):** `entity_registry.py:572-574` clean personality
   replacement. 31 tests pass; fixture now exits 0. NOT in `fa9c4edc` — N1 will still see
   exit 1, which is correct. Package carries a TRANSITION NOTICE for the flip.
6. **Package RENAMED by Architect:** `.../exchange/n0-to-n1-v2/` (43 files, ledger **42/42 OK**).
   ⚠️ `n0-to-n1.zip` is **STALE** (38/42, missing the whole policy-update round) — never deliver it.
7. **USB `D3E6-A900` RETIRED** — degraded, 11 I/O failures on N1, and now unmounted.
8. **Git:** `release/debut-v1.6.0` @ `fa9c4edc`, **~150 dirty files**, nothing committed.

### 🔒 TAILNET POLICY — FINAL (Architect-applied)
Converted `acls` → `grants`. **Node-to-node SSH and NFS are now REMOVED**, along with the
`funnel` nodeAttrs entry. Admin-only SSH remains in `check` mode (default 12h — custom
`checkPeriod` is Premium/Enterprise only and was rejected). A `tests` section now makes
Tailscale **refuse** any policy that re-adds tag-to-tag SSH or NFS.

> **Lilith-N1 can no longer SSH into Node 0.** To request Node 0 action she posts to the
> Hivemind and MaKaLi dispatches the right slot keeper. That is the governance model working.

> Architect action logged: the `tag:asus` removal on N1 was **manual by the Architect**,
> not autonomous. N1 tags are now exactly `[tag:node1]`.

---

## 📁 HYDRATION MAP (read in this order)

| Priority | Document | Why |
|---|---|---|
| 1 | `STATE_OF_THE_REALM.md` | Live cockpit, post-policy |
| 2 | `data/coordination/ACTIVE_SPRINT.json` | Execution queue |
| 3 | `data/federation/usb-payload/exchange/n0-to-n1-v2/README_FIRST.md` | Package entrypoint |
| 4 | `.../n0-to-n1-v2/07_open_gates/OPEN_TRANSFER_GATES.md` | C6 status + Alpha ratification |
| 5 | `.../n0-to-n1-v2/05_node1_ingestion/VERIFICATION_CHECKLIST.md` | N1 ingestion steps |
| 6 | `.../n0-to-n1-v2/08_library_curation_research/README.md` | Library curation MVP |
| 7 | `data/entities/makali_fusion/session_gnosis.md` | My own continuity |
| 8 | `data/coordination/EXPERT_SESSION_REGISTRY.md` | Canonical EIS IDs |
| 9 | `data/federation/tailnet-policy-OMEGA-DEFINITIVE-20260926.hujson` | Applied policy of record |

**Do NOT read:** `COORDINATION_CORPUS_INDEX.md`, the 600+ files in `data/coordination/`,
or the 607 stale handoffs. They will flood context. Use targeted grep instead.

---

## 🧭 HIVEMIND PROTOCOL (established with Lilith-N1)

- **Presence:** heartbeat or `intent=status` every ≤15 min while active.
- **Signal:** `task_current` = concise live state. `hivemind_get_awareness` = read.
- **Record:** decisions, transfers, ownership changes, Architect constraints →
  formal `post_context` / `handoff` / `workspace_lock`.
- **Receipts:** operational requests need `ACK:<topic> + next step`. Silence ≠ consent.
  Resend once → escalate to Architect → stop.
- **Polling discipline:** N1 must NOT busy-poll in a tight loop; it starves the operator's
  steering. One check per interval, then yield.
- **Redis ephemeral channel: DOWN** (`No module named 'redis'`). File-based only.
- **Open threads to N1:** (a) was the N1-side `pkill`/0.0.0.0 SSH attempt authorized?
  (b) differential `curl :8016` to scope the ACL block? (c) pull receipt for 11 files.

---

## ⏭️ NEXT WAKE

Do not claim final authenticated transfer. Do not re-seal the package without
re-running Carmack's audit. **Never deliver `n0-to-n1.zip`** — it is stale (38/42).
Do not commit the ~150-file working tree without explicit Architect instruction.
Await Carmack's re-audit of `n0-to-n1-v2`, then the public-flip security steps.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ HYDRATED ⬡ NODE-0-BASTION ⬡ 2026-09-26*
