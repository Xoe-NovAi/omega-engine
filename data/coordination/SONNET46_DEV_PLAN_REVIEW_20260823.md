<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sonnet 4.6 Dev Plan Review — PUBLIC-DEBUT-01
**AP Token**: `AP-SONNET46-REVIEW-20260823-v1.0.0`
⬡ OMEGA ⬡ SONNET-4.6 ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ trc_sonnet46_review ⬡ ACTIVE

**Date**: 2026-08-23 (persisted from session `ses_fdef2be4effe4pAaLXCTUx62GO` before compaction — original delivered in-conversation)
**Scope**: Accuracy audit + strategic review of full PUBLIC-DEBUT-01 plan

---

## VERDICT: CONDITIONALLY SOUND — 6 CORRECTIONS REQUIRED

Core thesis correct and disciplined. Ticket sequence right. Forbidden list right. Three critical path items verified. Six inaccuracies between plan claims and live tree needed fixing.

## SECTION 1 — Verified Accurate ✅
3 critical path gates passed · RoutingTable deleted (`src/omega/routing/` gone) · 13 active agents confirmed · DOC-1 stamps landed · P0-1a+P0-1b done · SoulStore/OOMProtector/HealthMonitor/SQLiteVecAdapter kept · zswap>zRAM locked (D-526/D-527) · qwen3-4b-thinking registered · god-module freeze intent correct

## SECTION 2 — Inaccuracies Found ❌

### Inaccuracy 1 — roles.yaml Confirmed Stale ✅ FIXED 2026-08-23
N9=`qwen3-4b`→should be `qwen3-4b-thinking`; N10=`qwen3-0.6b`→`qwen3-1.7b`. `qwen3-0.6b` not even registered in models.yaml — runtime error on any N10 session. **Fixed by N3 (Fix 1); Roc independently verified.**

### Inaccuracy 2 — opencode.json CI-2 Confirmed 0/8 criteria ⚠️ STILL OPEN
Live file is provider-definitions only. No instructions key, no compaction keys, plugin registered as npm name not path, no global model, no per-agent routing, no toolProfile, no agent.verity config.
**ADDITIONAL FINDING**: plugins live at `.opencode/plugins/` (awareness.ts, error-capture.ts, silent-stall-sensor.ts) but `"plugin"` key registers npm package names. **UNRESOLVED QUESTION: does OpenCode's `"plugin"` key accept local .ts file paths or only npm names?** If npm-only, sovereign-compaction plugin needs publishing or `~/.config/opencode/plugin/` placement per CI-3 spec. **10-minute prototype test required before landing CI-2 — HIGHEST-RISK CI-2 UNKNOWN, still not run.**

### Inaccuracy 3 — God-Module Lines Already Exceeded Freeze ⚠️ NEEDS BASELINE RULING
Manual §7 (2026-08-17) vs live 2026-08-23: oracle.py 1253→1455 (+202), model_gateway.py 1481→1606 (+125), providers.py 1088→1303 (+215), memory_store.py 1077→1224 (+147). Freeze not enforced. Decision needed before DEL-1 Week 2: ratify new baselines or audit the growth.

### Inaccuracy 4 — DEL-1 Week 1 Partially Complete, Untracked ✅ FIXED 2026-08-23
RoutingTable already deleted (commit `313b745b`) but DEL-1 was `backlog`. TriageRouter/SemanticRouter/RAGRouter still present with oracle.py importing both. **Status corrected to in_progress by N1 (Fix 2).**

### Inaccuracy 5 — P0-1d Not Clean, Footer Overclaimed ✅ FIXED 2026-08-23
OMEGA_ENGINE.md claimed "P0-1 secret scrub COMPLETE" while SECURITY_AUDIT ancestor residual remained. **Footer corrected by N5 (Fix 3).** Underlying P0-1d work still open (ancestor commit `0c40b108` carries 3 real keys).

### Inaccuracy 6 — MANIFEST.md Stale ✅ FIXED 2026-08-23
v4.0 listed ghost agents, wrong count. **v5.0 shipped by N5 (Fix 5): 13 agents, ghosts removed.**

## SECTION 3 — Strategic Assessment
**Right**: ticket order; forbidden list (Qdrant/JIT/Instruction Router/Vault/WARP/SDP correctly parked); one-router thesis w/ RouteDecision contract test; GN→DS→LI→KD→HR→ZS ordering (note: LI+ZS both touch memory/kernel — consider merged acceptance gate "sequential loader works with 16GB NVMe swap active").

**Needs clarification**: KD missing from tracker (✅ fixed by N7 Fix 4); INST-1 Fix 2+4 marked ready but stalled — document blocker or execute; HIVEMIND_PROTOCOL v2.0 + OVERSIGHT_HIERARCHY need ticket homes (PROTOCOL-1 backlog item suggested); CI-2 plugin-path prototype before CI-2 spec finalization.

## Recommendations (priority order at time of review)
1. ~~Fix roles.yaml~~ ✅
2. Execute INST-1 Fix 2+4 (gate to DEL-1) — still open
3. ~~Update DEL-1 status~~ ✅
4. ~~Update OMEGA_ENGINE.md footer~~ ✅
5. Prototype CI-3 plugin path mechanism — STILL OPEN (10-min test)
6. Establish new god-module freeze baselines — open, needs Kali ratification
7. ~~Add KD to tracker~~ ✅
8. Add PROTOCOL-1 ticket (HIVEMIND v2.0) — open
9. Re-run `omega talk "hello"` after each DEL-1 week — standing checkpoint
10. Verify SECURITY_AUDIT residual resolved (`git log -S 'csk-' --all` clean) before PUB-1 declared done

## What NOT To Change
Scope cut is correct. RouteDecision contract test is the right DEL-1 gate. 6 workstreams well-scoped. release/debut branch from allowlist (D-553) over mass-deleting main is architecturally sound.

*⬡ OMEGA ⬡ SONNET-4.6 ⬡ Dev Plan Review Persisted ⬡ 2026-08-23*