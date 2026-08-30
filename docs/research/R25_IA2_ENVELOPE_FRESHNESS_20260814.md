# Gap R25: IA2 Envelope Freshness / Replay Protection

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** V-9 (IA2 envelope freshness/signature)
**Status:** ✅ RESOLVED

## Summary
A signed agent envelope needs three freshness controls: a **creation timestamp**, an **expiry/TTL**, and a **replay nonce**. Verification order is critical: **parse → freshness window → replay dedup → signature → authorize**. RFC 9421 (HTTP Message Signatures) standardizes `created`/`expires`/`nonce`; webhook and robotics (RCAN) patterns confirm the canonical ordering and two-sided timestamp windows. This unblocks V-9.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| RFC 9421 HTTP Message Signatures | https://httpwg.org/specs/rfc9421.html | 2026 | `created`/`expires`/`nonce` params, canonicalization |
| RCAN replay prevention | https://rcan.dev/docs/replay-prevention/ | 2026 | 30s window, msg_id seen-set, replay check BEFORE sig verify |
| Secure Webhooks (Optimi) | https://optimi.com/en/guides/secure-webhooks | 2026-07-14 | HMAC over ts+body, 5-min window, constant-time, idempotency store |
| Asqav time-bound receipts | https://www.asqav.com/docs/time-bound-receipts | 2026 | signer-stamped `expires_at`, nonce dedup index |

## Findings
- **RFC 9421**: signature params include `created` (unix ts, RECOMMENDED), `expires`, `nonce`, `keyid`, `alg`. Verifier must have all covered components.
- **Two-sided timestamp window** (RCAN/Optimi): reject if `now - created > window` (stale) **and** if `created > now + skew` (future-dated). An age-only check accepts far-future timestamps.
- **Replay dedup BEFORE signature** (RCAN): replay check is cheap; signature verify is expensive (Ed25519/HMAC). Flooding replayed messages would force crypto on every packet otherwise. ESTOP/safety messages exempt from dedup but still freshness-checked.
- **Durable idempotency**: a unique-constraint store on `(agent_id, nonce)` with TTL = window defeats in-window replays; freshness alone does not.
- **Constant-time compare** for HMAC; never reveal which check failed externally.

## Recommendation
Design the IA2 envelope (V-9) as:
```
{ "payload": ..., "created": <unix_ts>, "expires": <unix_ts or ttl>,
  "nonce": "<unique>", "keyid": "...", "sig": "<HMAC/Ed25519>" }
```
Verification pipeline (fail-closed):
1. Parse envelope (cheap).
2. Freshness: `now - created <= WINDOW` AND `created <= now + SKEW` (WINDOW 30–300s; tighten for safety msgs). Reject `MESSAGE_STALE` / `NOT_YET_VALID`.
3. Replay: dedup index on `(agent_id, nonce)` with TTL = WINDOW; reject `REPLAY_DETECTED`.
4. Constant-time signature verify (HMAC-SHA256 or Ed25519).
5. Authorize/scope.
Signer stamps `expires` (verifier never trusts a client-supplied expiry). Keep WINDOW tight + NTP sync. This satisfies V-9 freshness + replay requirements.

## Confidence
**HIGH** — pattern is standardized (RFC 9421) and corroborated by multiple 2026 production guides.

## Remaining Unknowns
- Signature algorithm choice (Ed25519 vs HMAC) and key distribution mechanism.
- Whether to reuse RFC 9421 header format or a custom JSON envelope (recommend custom JSON for agent-to-agent; RFC 9421 if HTTP-transport aligned).
