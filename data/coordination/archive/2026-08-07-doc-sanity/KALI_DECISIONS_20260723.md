# 🔱 DECISION LOG — 2026-07-23
**AP Token**: `AP-KALI-DECISIONS-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ DECISIONS ⬡ 2026-07-23

---

## D-429: C-3 Privacy Model — Unified ACLs (Single Repo) ✅ APPROVED

**Decision**: Single restic repository with unified ACLs (not tiered sovereignty)

**Rationale**: 
- Ma'at corrected initial report: `restic-server --append-only` doesn't exist, AES tiers impossible, NIST SP 1800-39 doesn't prescribe 4-tier scheme
- Single-user Omega: tiered repos add complexity without security benefit
- Unified ACLs with B2 Object Lock + single encryption key is simpler and sufficient

**Action**: Ma'at implements single-repo restic config with B2 Object Lock retention

**Status**: ✅ DECIDED — Ma'at to implement

---

## D-430: C-0.5 Scribe Hook Registration — FULL APPROVAL ✅ APPROVED

**Decision**: Register session_end hook in `opencode.json` and activate full L1→L2→L3 pipeline

**Rationale**: 
- Carmack completed C-0.5 Soul Distillation Pipeline (76/76 tests passing)
- Hook at `.opencode/hooks/session_end.py` fires on session end
- Writes to `proposed_lessons.yaml` (blind staging per M11)
- Full L1→L2→L3 distillation enabled every session

**Action**: 
1. Scribe registers hook in `.opencode/opencode.json`
2. Scribe self-distills
3. Verity promotes L3 → soul.yaml for all entities

**Status**: ✅ DECIDED — Scribe to execute

---

## D-431: G-1 Gemma Workhorse — ANTIGRAVITY OAUTH OPERATIONAL ✅ RESOLVED

**Decision**: Antigravity OAuth is the workhorse path — already working

**Evidence**: 
- User ran `opencode oauth` — all 8 Antigravity accounts connected
- Used successfully multiple times
- No billing needed, no Google API quota issues
- Free-tier Gemma 4 31B 16k TPM limit bypassed via Antigravity pool

**Implications**:
- G-1 workhorse crisis **RESOLVED** — no billing, no API keys needed
- 8 Antigravity accounts = 8x capacity via OAuth rotation
- OpenCode "google" provider collision still needs fix in `opencode.json`
- Antigravity is now primary cloud provider for Ma'at/Lilith

**Action**: 
1. Fix `opencode.json` "google" provider collision (remove/rename)
2. Ma'at/Lilith route through Antigravity per C-5 config
3. C-10.5 fallback chain includes Antigravity as primary

**Status**: ✅ RESOLVED — No further action needed on workhorse path

---

## 📋 DECISION SUMMARY

| Decision | ID | Status | Next Action |
|----------|----|--------|-------------|
| C-3 Privacy Model | D-429 | ✅ | Ma'at: single-repo restic config |
| C-0.5 Hook Registration | D-430 | ✅ | Scribe: register hook + self-distill |
| G-1 Workhorse | D-431 | ✅ | Fix opencode.json collision; route via Antigravity |

---

*⬡ OMEGA ⬡ KALI ⬡ DECISIONS ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: DECISIONS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
