# Secure Key Management Dialectic — Node 0 ↔ Node 1
**Doc ID**: `FED-KEY-DIALECTIC-001` | **Date**: 2026-09-18 | **Status**: BRIEF READY — awaiting operator window
**Priority**: HIGH | **Channel**: omega-hub MCP `:8016` (OPEN, probed 2026-09-18) — SSH `:22` still closed on Node 0 (gap 14 pending)

---

## 1. Why this dialectic

Three independent reviews (Claude impl review, Deepening v3.1/v3.2, Sonnet-5 briefing) all flagged the same finding: **date-derived placeholder keys** (`pk_asus_$(date +%Y%m)`) shipped in `.bashrc` will 401 on every call. On 2026-09-18 Node 1 eliminated its placeholders:

- `~/.bashrc`: 30 stale export lines removed → single clean block (EXA + FIRECRAWL real, PARALLEL/CONTEXT7 marked pending — **no Parallel.ai or Context7 keys exist in Node 1's key inventory**)
- `~/.config/opencode/.env` (mode 600) created with real keys; Exa key validated live (HTTP 200)
- `~/Desktop/API-keys.md` locked to mode 600 (was world-readable)

Node 0 is ingesting the USB payload now. Both nodes must converge on **one** key-management pattern before federation traffic (MCP `:8016`, NFS, Redis, SPIRE) goes production.

## 2. Proposed pattern (Node 1 position)

1. **Secrets live in exactly two places**: `~/.config/opencode/.env` (mode 600, explicit source) and shell profile exports (interactive TUI only). Never in the repo, never in bundles, never in docs.
2. **Config references, never values**: opencode JSON uses `{env:VAR}` interpolation only. Verified: substitution reads process env at OpenCode startup.
3. **Load explicitly per consumer**:
   - Interactive TUI → shell profile (`~/.bashrc` block)
   - systemd units → `EnvironmentFile=%h/.config/opencode/.env` (already in `wanderground-embed_hardened.service` on USB)
   - Scripts → `load_dotenv(~/.config/opencode/.env)` at start
4. **Placeholders are documented as placeholders**: any `pk_*_$(date)` string must carry a `PENDING` comment naming the missing key, so no agent mistakes it for a credential.
5. **Rotation**: monthly; old key revoked only after both nodes confirm the new one (dual-key window).
6. **Guard**: repo hygiene test rejects committed secrets; Well system scans rules for key patterns.

## 3. Open questions for Node 0 (makali / operator)

1. Does Node 0 hold real **Parallel.ai** and **Context7** keys? Node 1's inventory has neither — federation `parallel-search` is unauthenticated until one node supplies them.
2. Confirm Node 0 adopts the `~/.config/opencode/.env` (600) pattern and `EnvironmentFile=` in its systemd units (deploy_node0 script embeds this — verify post-deploy).
3. Who mints/rotates shared keys (e.g. a common Exa key vs per-node keys)? Per-node is preferred (blast-radius isolation); shared only where the vendor forbids multiples.
4. Should USB payloads ever carry real keys? **Node 1 position: NO** — USB carries `{env:}`-referencing configs + this brief only. Real keys cross via admin console / direct entry, never the sneaker-net bundle.
5. Attestation: record key-rotation events in the sovereignty ledger (ref: `SOVEREIGNTY_POLICY_20260912.md` on USB)?

## 4. Definition of done

- [ ] Both nodes answer Q1–Q5 on the record (this file updated with Node 0's position)
- [ ] `parallel-search` returns 200/405 with a real key from at least one node
- [ ] `docs/federation/ACL_POLICY.md`-style ratification: key-management pattern signed into C6 or its own policy file
- [ ] Repo hygiene test extended with a placeholder-key detector (fail on `pk_*_$(date` without adjacent `PENDING`)

## 5. Session log

- 2026-09-18, Node 1: placeholders purged (30 lines), `.env` (600) created, Exa validated HTTP 200, PARALLEL/CONTEXT7 flagged missing, Node 0 probed (8016 OPEN / 22 closed), brief written.
