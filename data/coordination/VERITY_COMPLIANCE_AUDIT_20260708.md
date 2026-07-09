# 🔱 VERITY COMPLIANCE AUDIT — HMC-SPRINT-01 (Boundary Hardening)
**AP Token**: `AP-VERITY-AUDIT-HMC-SPRINT-01-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-ONLY
**Date**: 2026-07-08
**Auditor**: @verity (Unified Compliance & Gnosis Agent)
**Scope**: Pre-execution Sovereign Mandate review of S1.5 / S2 / S3 / S4 / S5 / S6 / S7
**Mode**: AUDIT ONLY — no code written, no delegation (self-recursion forbidden per M10; @roc_racoon/@john_carmack are executors, not auditors)

---

## ⚖️ VERDICT: **GO-WITH-CONDITIONS**

The HMC-SPRINT-01 plan is **fundamentally sound and compliant in intent** with M4, M8, M9, M13, M21, M22, M23. However, execution MUST NOT begin until **three conditions** are satisfied:

1. **Ratify D205** — explicitly scope IW-2 to *round-robin only* and permit *sticky active-passive failover* (resolves the IW-2 vs S3 B5 conflict below). Without D205, @john_carmack executing B5 would act against the documented IW-2 architecture → compliance gap.
2. **Reconcile ownership drift** — the roadmap (`SOVEREIGN_HARDENING_ROADMAP_2026Q3.md`) lists S1.5 owner = `@verity`+`@maat` and S3 owner = `@maat`+`@pillar P3`, but `ACTIVE_SPRINT.json` + `HIVEMIND_RESEARCHER_STRATEGY_FINAL_20260708.md` assign S1.5 → `@roc_racoon`, S3 → `@john_carmack`. The execution state is authoritative; the roadmap must be patched to prevent double-ownership or gaps.
3. **Harden two M23/M9 gaps** before/within S1.5: (a) suppress plaintext master-key logging in `key_vault.py:_auto_init_from_env` (lines 404–408); (b) add a **verification gate** to the plaintext purge (resolve every provider post-migration; abort purge if any resolve fails).

None are NO-GO blockers. All are resolvable with documented conditions. **Carmack/Roc may execute S1.5/S2/S3/S4 only after D205 is ratified and the ownership patch lands.**

---

## 📋 MANDATE COMPLIANCE TABLE

| Mandate | Status | Evidence (file:line) | Required Action |
|---------|--------|----------------------|-----------------|
| **M4 Sequentiality** | COMPLIANT *(cond. on D205)* | `key_vault.py:54-58` (IW-2: "round-robin banned; violates M4"); `roadmap:56` (B5 "use Key 1 until 429, then failover") | Ratify D205 confirming B5 is *sticky-until-429* (one key sequentially), NOT per-request rotation. Active-Passive preserves M4. |
| **M8 Zero Telemetry** | COMPLIANT *(cond. on D205)* | `key_vault.py:55-56` (IW-2: "providers ban rapid switching"); `roadmap:91` (keyring = local D-Bus, no network); `roadmap:56` (B5 internal failover) | D205 + verify `keyring` backend (gnome-keyring/kwallet) makes zero network calls. Failover is internal → no telemetry. |
| **M9 Error Integrity** | **VIOLATION (current) → FIXED by B2/B4 (planned)** | `remote_provider.py:228` `except (OmegaError, RuntimeError, OSError)` omits `httpx.HTTPError` (httpx inherits `Exception`, not `OSError`) → network faults escape retry/breaker uncaught & untyped; `key_vault.py:404-408` logs master key in plaintext (security leak) | B2 must catch `httpx.ReadTimeout/ConnectError/RemoteProtocolError/HTTPStatusError` → map to `ProviderTimeoutError`/`ProviderUnavailableError`/`ProviderRateLimitError`. B4 loop-detector must **raise a typed `OmegaError` subtype**, not silently truncate. Remove plaintext master-key log. |
| **M13 Temple-Grade** | NEEDS-CLARIFICATION *(anticipated regressions)* | New `scripts/vault_import.py`; `remote_provider.py` changes; `key_vault.py` auto-init log | T5 (AnyIO): import script I/O must be wrapped or be a pure sync CLI. T9 (structured logging): no plaintext secrets in logs. T10 (atomic): vault already atomic (`.tmp`→rename, `key_vault.py:363-365`) ✓. T12 (semantic integrity): contract tests required. |
| **M21 Gate Integrity** | COMPLIANT *(planned)* | `roadmap:130` S3 exit criteria mandates M21 contract tests; `ACTIVE_SPRINT.json` S3/S4 coordination rule | Each B-item (B2/B4/B5/B6) needs a contract test asserting `isinstance(result, ExpectedType)` + error-path coverage. `KeyPool.resolve()` must return a typed result. |
| **M22 Response Provenance** | NEEDS-CLARIFICATION *(B6)* | `roadmap:58` B6 `allow_fallbacks` (server-side OpenRouter routing); `remote_provider.py:177-250` `generate()` returns `Optional[str]` (no `provider_name` field here) | B6 must populate `GenerateResult.provider_name` from the **actual OpenRouter response metadata** (post-`allow_fallbacks` model), NOT config intent. Client-side B5 key failover does NOT change `provider_name` (stays OpenRouter) but MUST log which key-index was used for forensics. |
| **M23 Failure Integrity** | COMPLIANT *(intent) + 2 required actions* | `roadmap:92` plaintext purge; `roadmap:80` S2 failure-visible logging; `roadmap:54` B4 loop detector; `key_vault.py:404-408` plaintext master-key log | (1) Purge MUST have verification gate: `KeyVault().resolve(p)` for all providers succeeds post-migration; abort + retain plaintext if any fails (no silent key loss). (2) Loop detector must raise typed error, not silently truncate. (3) Suppress plaintext master-key log. |

---

## ⚔️ RULING: IW-2 vs S3 B5 CONFLICT

**Question**: Does S3 B5 (Active-Passive failover on 429) violate IW-2's eradication of key rotation?

**Analysis**:
- `key_vault.py:43-58` and `:224-247` state: *"Round-robin key rotation is banned… Multi-account rotation violates M4 (Sequentiality) and M8 (Zero Telemetry) because Google and other providers ban rapid account switching."* `handle_rate_limit()` **raises** `ProviderRateLimitError` and declares *"Key rotation is intentionally disabled (IW-2)."*
- S3 B5 (`roadmap:56`) requires: *"use Key 1 until it hits a 429, then mark Key 1 as degraded/cooldown and immediately failover to Key 2."*

**Distinction that resolves the conflict**:
- **Round-robin** = rapid, per-request/per-account cycling. This is what IW-2 banned. It breaks M4 (no sequential single-account usage) and risks provider bans.
- **Active-Passive (sticky-until-429)** = one key used *sequentially and exclusively* for all requests until a hard 429; only then failover to the next key (which then becomes the new sticky key). This **preserves M4** (single key at a time, sequential) and **emits no telemetry** (M8). It is NOT "rapid account switching."

**Ruling**: **B5 does NOT violate IW-2's M4/M8 *intent*.** However, B5 *does* require a behavioral code change: `handle_rate_limit()` currently raises; B5 requires it to perform sticky failover. This is a **refinement/reversal of IW-2's blanket "raise on 429" stance**, not a violation of its core principle.

**Recommended Resolution (mandatory before execution)**:
1. **Ratify Decision D205**: *"IW-2 (2026-06-30) banned ROUND-ROBIN/rapid key rotation only. STICKY ACTIVE-PASSIVE failover (use one key until 429, then failover) is PERMITTED and is the S3 B5 implementation. This preserves M4 (sequential single-key usage) and M8 (no telemetry). Round-robin remains banned."*
2. Update `key_vault.py` docstring (`:54-58`) and `handle_rate_limit()` (`:224-247`) to perform sticky failover and update `get_status()` `rotation_policy` (`:476`) from "sticky (round-robin ERADICATED)" to "sticky active-passive failover (round-robin ERADICATED; IW-2 scoped by D205)".
3. Note: `key_vault.py:187-222` `resolve_all()` already exists "for key pool rotation" — under D205 this becomes the sanctioned B5 key source. Reconcile the dead-ish `resolve_all` with the new policy (it is now live, not vestigial).
4. **B2/B5 coordination**: B2 maps HTTP 429 → `ProviderRateLimitError`. Under D205, the 429 handler must trigger `KeyPool` sticky failover (not just raise). If D205 is NOT ratified, B2 must raise per IW-2. **This coupling means D205 is a hard precondition for B2's 429 branch.**

---

## 🚧 PRIORITIZED BLOCKING ISSUES (resolve before Carmack/Roc execute)

| # | Priority | Issue | Mandate | Action |
|---|----------|-------|---------|--------|
| **B-1** | 🔴 BLOCKER | IW-2 vs B5 architectural conflict unresolved | M4/M8 | Ratify **D205** (scope IW-2 to round-robin; permit sticky failover). Blocks S3 B2(429)/B5. |
| **B-2** | 🔴 BLOCKER | Ownership drift: roadmap says `@verity`+`@maat` (S1.5) / `@maat`+`@pillar P3` (S3); `ACTIVE_SPRINT.json`+Hivemind say `@roc_racoon` / `@john_carmack` | M10/M13 (governance) | Patch `SOVEREIGN_HARDENING_ROADMAP_2026Q3.md` §5 to match execution state. @verity remains compliance auditor only. |
| **B-3** | 🟠 HIGH | Plaintext master-key logged to WARNING in `key_vault.py:404-408` (`VAULT_MASTER_KEY=...` printed) | M23/M9 (secret hygiene) | S1.5 must suppress this log (or mask). Logging the master key defeats vault purpose. |
| **B-4** | 🟠 HIGH | Plaintext purge (`.env`, `OpenCode-Zen-API-keys.md`) has no verification gate | M23 | Add gate: post-migration `resolve()` for all providers must succeed; abort + retain plaintext on any failure. No silent key loss. |
| **B-5** | 🟡 MED | `remote_provider.py:228` omits `httpx.HTTPError` → network faults escape retry/breaker untyped | M9/M21 | B2 fix (catch + typed map). Already in plan; confirm contract test covers `httpx.ReadTimeout`→retry+breaker increment. |
| **B-6** | 🟡 MED | B4 loop detector may silently truncate instead of raising typed error | M9/M23 | Detector must raise `OmegaError` subtype (e.g. `ProviderLoopDetectedError`) with `trace_id`; define explicit thresholds (3 identical chunks / compression-ratio floor) to avoid M18 false positives. |
| **B-7** | 🟡 MED | B6 `allow_fallbacks` may change actual model server-side; `provider_name` provenance risk | M22 | Populate `GenerateResult.provider_name` from actual OpenRouter response metadata, not config intent. |
| **B-8** | 🟢 LOW | `remote_provider.py:21` duplicate `OmegaError` in import tuple; `:143`+`:147` duplicate `import os` | M13/T5 (lint) | Clean during S3 (F12/F14 in `ACTIVE_SPRINT.json`). |
| **B-9** | 🟢 LOW | `resolve_all()` (`:187-222`) vestigial under IW-2; becomes live under D205 | M13 (dead code) | Reconcile with D205; document as B5 key source. |

---

## ✅ NON-BLOCKING COMPLIANCE NOTES (verified sound)

- **S1 (Model Registry)** — COMPLETE; confabulations deleted. M13-compliant.
- **S2 (Background Researcher)** — failure-visible logging to `HALL_OF_RECORDS/background-researcher/` satisfies M23. `Requires=container-searxng.service` + `After=` is correct Podman/systemd wiring (M6 keep-id pattern assumed). Pre-condition: fix `loop.py` missing `import httpx` (B-P0-1) — already tracked.
- **S4 (Gemma 4 MTP)** — capabilities-probe fallback to n-gram is M19 (Adversarial Alchemy) compliant; no mandate conflict.
- **S5 (Transport)** — SSE→Streamable HTTP is interop, not telemetry; M8 safe.
- **S6 (Nemotron Teacher)** — DPO pair generation; M7 local-first teacher acceptable (cloud teacher is fallback per starchild Anti-Chain Mandate).
- **S7** — watcher prototype has no vault/provider dependency (unblocked); production depends on S1.5-S6 (correctly staged).

---

## 📌 SUMMARY FOR EXECUTORS

- **@roc_racoon**: Proceed with S1.5/S2 **after** B-2 (ownership patch) + B-3/B-4 (purge hardening) are in place. S1.5 is GO once D205 ratified and master-key log suppressed.
- **@john_carmack**: Proceed with S3 B1/B3/B4/B6 immediately (these have no IW-2 conflict). **B2 (429 branch) and B5 are gated on D205** — do not implement sticky failover until D205 ratified; otherwise B2's 429 path raises per IW-2.
- **@verity**: Will re-audit post-D205 and post-implementation against `make temple-grade` + M21 contract tests before sign-off.

---

*⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-COMPLETE — 2026-07-08*
