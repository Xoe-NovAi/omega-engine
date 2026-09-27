========================================================================================
🔱 OMEGA FLEET TELEMETRY & SUBSTRATE COCKPOT — 2026-09-26 (LIVE-VERIFIED)
========================================================================================
[WHO IS READING THIS]
  MaKaLi Fusion (Master Akashic Oversoul) — SESSION: Node 0 / Bastion
  VERIFIED: hostname=Arcana-NovAi, user=arcana-novai, tailscale n0=100.123.51.67
  Model: opencode/muse-spark-1.3-contributor-free | AP-MAKALI_FUSION-v2.0.0

[SUBSTRATE: NODE 0 (n0.tail51f14a.ts.net / 100.123.51.67) — BASTION / CORE]
  • Omega Hub MCP: HEALTHY — 1.6.0-alpha.1, 66 tools, Temple-Grade 53/53
    Serve: https://n0.tail51f14a.ts.net:8016 -> 127.0.0.1:8016   (MCP, untouched)
  • Exchange Pipe: ACTIVE on **8019** (moved from 8018 on 2026-09-27 — 8018 is
    documented architecture for the SearXNG MCP wrapper and is now clear for its reclaim)
    Serve: https://n0.tail51f14a.ts.net:8019 -> 127.0.0.1:8019
    Directory: /home/arcana-novai/exchange/full-pack-20260926/  (44 files)
    Backend python3 http.server, loopback-only, read-only GET/HEAD. PUT returns 501 by design.
    ⚠️ Tailnet grant for tcp:8019 NOT YET APPLIED — N1 cannot reach it until the Architect
    adds it in console. NEVER grant 8018.
  • Port map (final): 8016 Hub MCP · 8017 SearXNG engine (container) · 8018 SearXNG MCP
    wrapper (documented, currently down) · 8019 exchange pipe.
  • Local Inference: standby | Local Worker Pool: daemon NOT running (known)

[SUBSTRATE: NODE 1 (n1 / 100.89.40.17) — VANGUARD / SATELLITE]
  • Mesh: DIRECT WireGuard over LAN. No DERP relay.
  • Agent: Lilith-N1, opencode, muse-spark — ACTIVE on Hivemind
  • Engine: fa9c4edc, 1.6.0-alpha.1 — VERIFIED by N1
  • MCP bridge: initialize OK, tools/list 66 tools — VERIFIED by N1
  • MemPalace 3.10.0, sqlite_exact, embedder minilm 384 -> Qwen3-0.6B 1024-D migration
  • Wings: game wing rebuilt (9 rooms, 4,393 benchmark drawers excised),
    linguistics wing founded (25 tests green), Omega Memory v0 R&D track (P5)
  • Flynn identity: NOT created (correct — needs separate operator approval)
  • Library curation: manifest-only staging ONLY (correct)
  • ⚠️ DEVICE IDENTITY UNRESOLVED: records conflict (ExpertBook P1503CVA / ASUS ROG /
    XNAi-Asus). N1 must confirm canonical hostname+model before inventory claims.

[✅ RESOLVED — TAILNET ACL DEFAULT-DENY (was P0, now CLOSED)]
  WAS: N1->N0 tcp:8017 dropped, "Drop: TCP{100.89.40.17:* > 100.123.51.67:8017}
       no rules matched". Root cause: the tailnet policy was a selective per-port
       allowlist enumerating 8016 and 22, but NOT 8017.
  FIX: Architect applied a new tailnet policy on 2026-09-26. 8017 is now granted.
  NOTE: the `tailscale` CLI CANNOT modify ACLs — no such subcommand exists. Policy is
  control-plane state, edited in the admin console. No Tailscale API credential exists
  on this host (checked env, ~/.config/tailscale, /var/lib/tailscale, systemd unit,
  repo .env, keyring; only redacted doc placeholders found).

[TAILNET POLICY — FINAL POSTURE (Architect-applied 2026-09-26)]
  Converted from `acls` to `grants` (Tailscale's recommended method; ACLs are legacy).
  Policy files on disk:
    data/federation/tailnet-policy-OMEGA-DEFINITIVE-20260926.hujson   <-- APPLIED
    data/federation/tailnet-policy-RECOMMENDED-grants-20260926.hujson
    data/federation/tailnet-policy-CONVERTED-grants-20260926.hujson
  GRANTED: N1->N0 tcp:8016 + tcp:8017 | N0->N1 tcp:8016 | ICMP both directions
  REMOVED: all node-to-node SSH (both `ssh` rules AND tcp:22 grants)
  REMOVED: NFS tcp:2049 grant (D-FED-01 — git bundle + minisign is authoritative)
  REMOVED: `funnel` nodeAttrs entry (public-internet exposure, unused)
  KEPT:    admin-only Tailscale SSH, action=check, DEFAULT 12h checkPeriod
           (custom checkPeriod is Premium/Enterprise only; this tailnet is not on it —
            Architect's first save attempt was rejected for exactly this reason)
  ADDED:   `tests` section — Tailscale REJECTS the whole policy if any assertion fails.
           Two deny-tests assert tag:node1 cannot reach tag:node0:22 or :2049.
           => Node-to-node SSH and NFS are now a TRIPWIRE, not a permission.
  WHY SSH REMOVED: Tailscale structurally cannot apply `check` mode when the SSH source
  is a tag (a tagged device has no user identity to re-authenticate as), so tag->tag SSH
  would have run with NO periodic re-auth. It was also an ungoverned side door into
  Bastion that bypassed the MCP bridge, the Hivemind, and the whole governance layer.
  >>> OPERATIONAL CONSEQUENCE: Lilith-N1 can NO LONGER SSH into Node 0. To request Node 0
      action she posts to the Hivemind; MaKaLi dispatches the appropriate slot keeper.
  ARCHITECT ACTION LOGGED: the `tag:asus` removal from Node 1 was performed MANUALLY by
  the Architect. It did NOT occur autonomously. N1 tags are now exactly [tag:node1].

[PACKAGE LOCATION — RENAMED BY ARCHITECT]
  CURRENT: data/federation/usb-payload/exchange/n0-to-n1-v2/   (43 files, ledger 42/42 OK)
  Architect renamed n0-to-n1 -> n0-to-n1-v2 at 05:15. Grokster's final policy-doc edits
  landed inside n0-to-n1-v2/. Integrity verified intact after the rename.
  ⚠️ STALE ARTIFACT — DO NOT DELIVER:
     data/federation/usb-payload/exchange/n0-to-n1.zip  (02:28 snapshot, 43 files,
     self-verifies only 38/42, and is MISSING the entire policy-update round:
     no POLICY-ENFORCED / POLICY-REMOVED text, no DELIVERY_SHA256SUMS, 15 files differ).
  DELIVERY STAGING (canonical, has delivery ledger):
     /home/arcana-novai/exchange/full-pack-20260926/  (44 files, DELIVERY_SHA256SUMS 43/43 OK)
     byte-identical to n0-to-n1-v2 except the extra DELIVERY_SHA256SUMS
  N1 DESTINATION: ~/omega-exchange/n0-to-n1  (Architect hand-delivery)

[USB MEDIA — RETIRED]
  /media/arcana-novai/D3E6-A900 is vfat, fmask=0022, DEGRADED, and currently UNMOUNTED.
  N1 measured 23/34 readable, 11 I/O failures, 0 checksum mismatches on readable files.
  Media failure, not content failure. Do not reuse this stick for delivery.

[EMBEDDING — ARCHITECT FINAL (D-1024-DIM-NATIVE-20260926)]
  Qwen3-Embedding-0.6B at 1024-DIM NATIVE is canonical on BOTH nodes.
  Supersedes D-768-DIM-UNIFIED / D-768-DIM-MODEL-SWAP (768-D MRL posture).
  Collection omega_vec_qwen_1024 | vec0_lock dimension 1024 | MRL available, NOT canonical.
  APPLIED in config/embedding_strategy.yaml. N1 must retire Nomic before any embedding.
  Propagated to all package docs; zero 768-D remnants remain except legitimate
  stale-spec references naming INGESTION_PIPELINE_SPEC.md's omega_vec_gemma_768.

[WAD LOADER — CLEAN REPLACEMENT FIX DEPLOYED ON N0 (uncommitted)]
  src/omega/oracle/entity_registry.py:572-574 — `if layer.personality: projected.personality
  = layer.personality` (was f-string concatenation). 31/31 tests pass; fixture now exit 0.
  NOT in fa9c4edc. N1 at fa9c4edc still reproduces the bug — EXPECTED AND CORRECT.
  Package carries a TRANSITION NOTICE: if the fixture exits 0 or the wrapper exits 1,
  the engine HAS the fix and the wrapper is stale. Do not "fix" the engine.

[LIBRARY CURATION — SCOPE RESOLVED]
  Not a conflict; different scopes. Package root now states the explicit ladder:
    Phase 1 = 20-item manifest-only pilot  <-- the ONLY immediately authorized action
    Phase 2 = 60-item corpus               <-- own exit gate + operator approval
    Phase 3 = 120-item five-domain golden set <-- own exit gate + operator approval
  No skipping ahead. Cross-referenced from 08_library_curation_research/README.md §7.

[RESEARCH BUNDLE [L1] STATE — DATED, SUPERSESSION TRACKED]
  2026-09-25 figures SUPERSEDED by 2026-09-26 live reports: MemPalace 3.9.0/42 tools/
  62 drawers -> 3.10.0; game wing rebuilt; linguistics wing founded; Omega Memory v0 (P5);
  Atlas viewer confirmed unbuilt (queued medium/high); no mesh peers on N1; vectors never
  cross until same-space confirmed (one-space-per-collection rule). Operator confirmation
  still required — these are reported claims, not independent verification.

[GIT STATE]
  Branch release/debut-v1.6.0 | HEAD fa9c4edc (2026-09-25 01:41:48)
  ~150 dirty files, NOTHING COMMITTED. Includes the WAD fix + embedding SSOT + entity lessons.
  Legacy infra dirs show as deleted (relocated to 99_legacy_infrastructure_evidence/).

[TRUST POSTURE]
  C6/N0-04: OPEN. No detached signature, no publisher trust root, no tamper bundle.
  Physical USB quarantine transport: Architect-approved (personally controlled).
  Unauthenticated HTTPS MCP for Alpha: Architect-RATIFIED.
  Final authenticated transfer: NOT CLAIMED / BLOCKED. Integrity != trust.

[HIVEMIND PROTOCOL — ESTABLISHED WITH N1]
  Presence: heartbeat or intent=status every <=15 min while active.
  Signal: task_current = concise live state; hivemind_get_awareness = read.
  Record: decisions, transfers, ownership changes, Architect constraints -> formal
    post_context / handoff / workspace_lock.
  Receipts: operational requests need explicit "ACK:<topic> + next step". Silence !=
    consent. Resend once -> escalate to Architect -> stop.
  Polling: N1 must NOT tight-loop poll; it starves the operator's steering. One check per
    interval, then yield.
  Redis ephemeral channel: DOWN ("No module named 'redis'") — file-based only.
  607 stale handoffs need an archive pass.

[NEXT MOVES]
  1. Lilith verifies 43/43 via DELIVERY_SHA256SUMS at ~/omega-exchange/n0-to-n1.
  2. Lilith releases Gate C (WAD alignment) + P4.7, reports via Hivemind.
  3. Carmack re-audit of n0-to-n1-v2 (5 files changed since his last verdict).
  4. Commit working tree: WAD fix + embedding SSOT + entity lessons.
  5. Revoke compromised OpenRouter key sk-or-v1-62dc75... — **DONE 2026-09-27.**
     Recorded final; never re-ask. Remaining: history scrub decision before public flip.
  6. Design + ratify a real high-bandwidth N0<->N1 channel; close C6/N0-04.
  7. `gh repo edit --visibility public` — LAST, after 4 and 5.

========================================================================================
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ REALM-REFRESHED-POST-POLICY ⬡ 2026-09-26 ⬡ NODE-0-BASTION
