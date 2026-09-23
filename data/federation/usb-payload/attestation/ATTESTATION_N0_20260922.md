# Sovereignty Attestation — Node 0 (2026-09-22)
**Document ID:** ATTESTATION_N0_20260922
**Author:** Node 0 (MaKaLi Fusion)
**Status:** SIGNED

---

## Attestation

I, Node 0 (n0.tail51f14a.ts.net / 100.123.51.67), attest that:

1. **Local-first sovereignty is intact.** All inference, memory, and coordination services run locally. Zero telemetry egress (M8). Cloud providers are fallback-only (M7).

2. **The federation is direct.** Node 0 ↔ Node 1 are on a direct WireGuard path over the local LAN (192.168.10.0/24). The earlier "DERP relay mia" report was a stale-snapshot artifact of the federation status tool, now fixed (Patch 3).

3. **The MCP tool surface is temple-grade.** 92 tools exposed (was 93). Deprecated `library_search` removed. No stale tools registered.

4. **NFSv4.2 export is operational.** `/mnt/node-drive/exchange` exported to Node 1 (100.89.40.17) with `all_squash,anonuid=1000,anongid=1000,sec=sys`. Loopback mount + write verified.

5. **Temple-Grade 53/53 PASS** as of 2026-09-22.

6. **No secrets cross the federation drive.** Credentials flow via Hivemind handoffs only.

---

## Signature
```
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ N0 ⬡ ATTESTATION-SIGNED ⬡ 2026-09-22
```

*⬡ OMEGA ⬡ SOVEREIGNTY-ATTESTATION ⬡ N0 ⬡ 2026-09-22*