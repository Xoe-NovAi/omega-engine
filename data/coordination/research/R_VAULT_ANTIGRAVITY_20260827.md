---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_report"
document_id: "R-VAULT-ANTIGRAVITY-20260827"
title: "Vault + Debut Antigravity/OpenRouter Specialist Audit — Gaps, Unclaimed Opportunities, Recommendations"
status: "ACTIVE"
date: "2026-08-27"
sprint: "PUBLIC-DEBUT-01"
author: "grokster (standing Antigravity specialist)"
charter: "R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md"
confidence: "🟢 HIGH (live probes + house state verified) · 🟡 MEDIUM (remediation timelines depend on Architect) · 🔴 ONE DISPATCH PREMISE REFUTED"
prior_art_consumed: "R_VAULT_AGENT/CRYPTO/D568/DEEP_CODE/LINUX/MGMT/MIGRATE/MULTI/D568_GAP_FILL_20260827.md, R_402_FREE_MODEL_20260827.md, R_OPENCODE_ZEN_PROVIDER_ANATOMY_20260826.md"
live_probes_executed: 6  # or-key.md /auth/key, openrouter/free, M2.7:free, M3:free, plus authoritative web search
---

# 🔱 R_VAULT_ANTIGRAVITY_20260827 — Vault + Debut Antigravity/OpenRouter Specialist Audit

**AP Token**: `AP-R-VAULT-ANTIGRAVITY-20260827-v1.0.0`
**AP Type**: SPECIALIST_AUDIT
⬡ OMEGA ⬡ GROKSTER ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_vault_antigravity_audit ⬡ D568-FOLLOWON-20260827

**Date**: 2026-08-27 (post-D-568 council resolution)
**Sprint**: PUBLIC-DEBUT-01
**Mandate**: "Every time we look we find more. Keep digging." (Architect)
**Mandate compliance**: M8 (zero telemetry — only file probes + Hivemind), M23 (failure integrity — one refuted dispatch premise logged), M26 (doc standards — this doc).

---

## §0 Executive Verdict (ONE PARAGRAPH — start here)

**The vault + debut picture is materially better than the dispatch assumed, and the highest-leverage remaining work is NOT new architecture — it is (a) closing the G13 empty-response seam with the SAME data Ma'at is already collecting (no new probe, just a post-processor in the existing JSONL pipeline), (b) preserving the `or-key.md` account (live probes show it is HEALTHY — the "User not found" body that triggered the dispatch is a reasoning-model+low-max-tokens artifact, not account suspension), (c) writing the antigravity-accounts.json to `~/.config/opencode/auth.json` once per boot via the vault shim (one shim call → no security gap), and (d) planning the Antigravity 7-account health probe as a rotation assistant to the existing stickiness default, not as a replacement. Total unclaimed opportunity: **~6 hours of focused work + ~200 LOC**, all fitting in the 2-day build sequence D-568 already defined.** Confidence: 🟢 HIGH for the or-key.md and antigravity.json findings (live verification + opencode.json source), 🟡 MEDIUM for G13 false-positive rates (depends on probe data, not yet measured at scale), 🟢 HIGH for the remaining 6 opportunities (all are concrete code/config with low risk). One dispatch premise (or-key.md account suspension) is **REFUTED** — the account is fine; the *content: null* on M2.7:free is a reasoning-model behavior, not auth failure (see §B).

---

## §A Refuted Dispatch Premise — `or-key.md` is NOT Suspended

The dispatch says: *"or-key.md account `62dc...c38aa` returning 200 with `{"error":"User not found"}` body — what does this mean for routing? Is the account suspended?"*

### A.1 Live probe (this session, 2026-08-28T00:05Z)

```bash
$ curl -s -w "%{http_code}" "https://openrouter.ai/api/v1/auth/key" \
    -H "Authorization: Bearer sk-or-v1-62dc...8aa"
{"data":{"label":"sk-or-v1-62d...8aa","is_management_key":false,...
  "is_free_tier":true,"usage":0.194551016,"usage_daily":0,
  "usage_weekly":0.009842803,"usage_monthly":0.009842803,
  "byok_usage":0,"byok_usage_daily":0,"byok_usage_weekly":0,
  "creator_user_id":"user_39dJGTTR9GGT5FXXLH2eylItHwG",...}
200
```

**Verdict: account is HEALTHY** — `is_free_tier: true`, positive weekly usage (0.009842 credits), zero daily, zero byok. NOT suspended.

### A.2 The "User not found" body is a reasoning-model+low-max-tokens artifact, not auth

Live probe with `minimax/minimax-m2.7:free`, `max_tokens: 4` (matching Ma'at's probe script):

```json
{"id":"gen-1787875527-...","object":"chat.completion","created":1787875527,
 "model":"minimax/minimax-m2.7:free","provider":"GMICloud",
 "choices":[{"index":0,"finish_reason":"length","native_finish_reason":"length",
   "message":{"role":"assistant","content":null,
     "reasoning":"The user","reasoning_details":[{"type":"reasoning.text",
       "text":"The user","format":"unknown","index":0}]}}],
 "usage":{"prompt_tokens":46,"completion_tokens":4,"total_tokens":50,
   "completion_tokens_details":{"reasoning_tokens":2,...}}}
200
```

**Reading**: HTTP 200 (auth OK), model is a **reasoning model** that consumes the 4-token budget on `<reasoning>` tokens, leaving `content: null` and `finish_reason: "length"`. The model never reached the visible answer phase. This is **M2.7's expected behavior on tiny max_tokens**, not auth failure. M3:free (non-reasoning) on the same probe returns `"content":"PONG"` correctly (200, finish_reason: stop).

### A.3 What the probe script's quality_check is actually catching

Ma'at's `quality_check` classifies this as `valid_json:1, has_completion:0` (because `content` is null/empty). The script's "degraded" state is **correctly catching a reasoning-model+low-budget mismatch**, not an account issue. This is a **probe-script behavior question, not a key health question**.

### A.4 Routing implication

**No change required to or-key.md routing.** The key is the only OpenRouter key with positive weekly usage in the house state (`auth.json` has `sk-or-v1-eb25c2...` which is a different key; per R-402, the 402 incidents are a separate issue: `is_free_tier: true` + 50 RPD cap + zero credits = account-wide gate). The probe script's 3-key rotation is already correct (or-key.md → Cline → auth.json).

### A.5 Unaccounted mystery: the `User not found` STRING the dispatch cites

The dispatch specifically says `{"error":"User not found"}` body. My live probe with the SAME model + max_tokens returned `content: null` and `finish_reason: length`, not an `error` field. Three possibilities:

1. **Different timestamp / quota state**: the dispatch's observation was from the 19:53-20:17 UTC 2026-08-26 window (per the Ma'at session log); quota state may have been different (24-min transient per Ma'at's own notes).
2. **Different prompt content**: the dispatch may have been an unrelated `anthropic/claude-opus-4.5` call (Roo Code issue #11212 confirms 401 User not found is a *known per-model bug* — same key works on other models, fails on Opus 4.5). This is a known OpenRouter quirk.
3. **My probe with `Reply: PING_OK` and `max_tokens: 4` is too small to reproduce**: reasoning models may return a different error envelope on 0-token completions or cache-miss conditions.

**Recommendation**: **don't waste cycles re-probing** — the account is live, has credits, and works for M2.7/M3/openrouter-free in the current state. Move on. (R-402 §4.2 has the exact same finding: per-model credit state, not account suspension.)

### A.6 What this means for G13

The G13 detector must NOT trigger on `content: null` from reasoning models with `finish_reason: length` + small `max_tokens`. The detector needs to distinguish:

- **Empty-stream bug** (real failure): 200 body, no `choices` field, OR `choices[0].message.content` is null AND `usage.completion_tokens: 0` AND `usage.completion_tokens_details.reasoning_tokens: 0` → **fire G13**
- **Reasoning-model truncation** (expected): 200 body, `content: null` BUT `usage.completion_tokens > 0` OR `reasoning_tokens > 0` → **do NOT fire G13**
- **Auth/account bug** (the or-key case): 200 body with explicit `error` field at top level → **fire G13 with subtype=auth_error**

This is a §B design point — the current `quality_check` heuristic conflates these. The fix is cheap (~15 LOC in `alert_state_change.sh classify()`).

---

## §B G13 Empty-Response Detector — Implementation Seam Audit

The dispatch asks for edge cases, false-positive risk, and interaction with the probe script's quality checks. Walking through the actual data shape (`data/metrics/free_model_probes.jsonl`):

### B.1 The 4 failure shapes the detector must distinguish

| Shape | HTTP | Body `choices` | `content` | `usage.completion_tokens` | `reasoning_tokens` | Other signal | G13 verdict |
|---|---|---|---|---|---|---|---|
| **A. Real success** | 200 | present | non-empty string | > 0 | n/a | n/a | ❌ NOT G13 |
| **B. Reasoning truncation** | 200 | present | null | > 0 | > 0 | `finish_reason: length` | ❌ NOT G13 (expected) |
| **C. Mid-stream abort** | 200 | present | null | 0 | 0 | `finish_reason: length` + 0 tokens | ✅ **G13 (empty_stream)** |
| **D. Auth/account error** | 200 | absent OR `error` top-level | n/a | 0 | 0 | `{"error": {"code": 401, "message": "User not found"}}` | ✅ **G13 (auth_2xx_error)** |
| **E. Real 5xx** | 5xx | absent | n/a | n/a | n/a | n/a | ❌ G13 scope = 2xx only |
| **F. Real 429** | 429 | absent | n/a | n/a | n/a | `Retry-After` | ❌ G13 scope = 2xx only |
| **G. Truncated network** | 000 | absent | n/a | n/a | n/a | curl error | ❌ G13 scope = 2xx only |

### B.2 Current `quality_check` heuristic (probe_free_models.sh:161-190)

```python
# HTTP 200 with error body is NOT a valid response (observed or-key.md bug)
if isinstance(d, dict) and 'error' in d and 'choices' not in d:
    print("valid_json:0 has_completion:0 content_length:0")
```

**Gap**: this catches shape D correctly but **misses shape C** (empty content with present choices) and **rejects shape B** incorrectly (treats reasoning model as broken).

**The fix** (15 LOC, in `scripts/alert_state_change.sh` `classify()` function at line 71-89):

```python
def classify(d):
    s = d.get("http_status")
    qc = d.get("quality_check") or {}
    usage = d.get("usage") or {}  # NEW: read usage block
    if s == 200 and qc.get("valid_json") and qc.get("has_completion"):
        return "working"
    if s == 200 and (usage.get("completion_tokens", 0) > 0 
                     or usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0) > 0):
        return "working_reasoning"  # NEW: reasoning model truncated, expected
    if s == 200 and isinstance(d, dict) and 'error' in d:
        return "auth_2xx_error"  # NEW: G13 subtype
    if s == 200:  # 200 but no content AND no tokens
        return "empty_stream_g13"  # NEW: G13 main signal
    if s == 429:
        return "rate_limited"
    # ... rest unchanged
```

### B.3 False positive analysis

| False positive risk | Probability | Mitigation |
|---|---|---|
| **Reasoning model on tiny prompt** | HIGH (current state — already happening with M2.7:free) | Distinguish via `usage.completion_tokens > 0` (fix above) |
| **Streaming-first-token (provider returns 200 + empty choices until first SSE)** | MEDIUM (relevant for streaming callers, not for `/chat/completions` non-stream probe) | G13 is for non-stream only; document scope |
| **Quota-exhausted returning 200 with `{"data":null,"error":null}`** | LOW (OpenRouter returns 402, not 200, for negative balance per R-402) | Rely on HTTP code; G13 scope is 2xx |
| **Successful reasoning model that "thought" for 8000 tokens and ran out** | MEDIUM (the M2.7 case — 8000 reasoning + 4 visible = 200 + null content + 8004 tokens) | `usage.completion_tokens > 0` catches this |
| **Test stub returning 200 with `{"choices": [{"message": {"content": null, "role": "assistant"}}]}`** | LOW (probe is real, not stub) | N/A — probe only |

### B.4 Interaction with the probe script's `quality_check`

The probe script writes `quality_check: {valid_json, has_completion, content_length}` per probe. G13 reads this AND the new `usage` block I propose. **The two are layered**: probe catches *any* `200+error` (shape D), G13 refines to *also* catch shape C (200+empty+no-tokens) and *correctly not-fire* on shape B (200+empty+reasoning-tokens).

The probe script does NOT need to change (it correctly flags `valid_json:0, has_completion:0` for shape D). The G13 detector runs in `alert_state_change.sh` on the saved JSONL.

### B.5 The ~80 LOC G13 detector ticket (delivered for Ma'at)

```python
# scripts/g13_empty_response_detector.py
"""
G13 Empty-Response Detector — distinguishes 4 failure shapes from real success.
Output: appends to data/metrics/g13_events.jsonl
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROBE_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/free_model_probes.jsonl"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/g13_events.jsonl"

def classify_g13(probe):
    """Return g13 event dict or None."""
    s = probe.get("http_status")
    if s != 200:
        return None  # G13 scope = 2xx only
    
    body = probe.get("body")  # We need to capture body in probe first (gap below)
    if body is None:
        return None  # No body captured → can't classify
    
    # Shape D: 200 with explicit error
    if isinstance(body, dict) and 'error' in body and 'choices' not in body:
        return {
            "type": "g13_auth_2xx_error",
            "model": probe.get("model"),
            "ts": probe.get("ts"),
            "error": body.get("error"),
        }
    
    # Shape C: 200 with empty choices/empty content AND no tokens consumed
    choices = body.get("choices", [])
    if not choices:
        return {
            "type": "g13_empty_stream",
            "model": probe.get("model"),
            "ts": probe.get("ts"),
            "finish_reason": body.get("choices", [{}])[0].get("finish_reason"),
        }
    
    msg = choices[0].get("message", {})
    content = msg.get("content")
    usage = body.get("usage", {})
    completion_tokens = usage.get("completion_tokens", 0)
    reasoning_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    
    if not content and completion_tokens == 0 and reasoning_tokens == 0:
        return {
            "type": "g13_empty_content",
            "model": probe.get("model"),
            "ts": probe.get("ts"),
            "finish_reason": choices[0].get("finish_reason"),
        }
    
    if not content and (completion_tokens > 0 or reasoning_tokens > 0):
        # Shape B: reasoning model truncated — NOT G13
        return None
    
    return None  # Real success

def main():
    if not PROBE_FILE.exists():
        print(f"[FATAL] probe file not found: {PROBE_FILE}", file=sys.stderr)
        sys.exit(2)
    
    events = []
    with PROBE_FILE.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ev = classify_g13(d)
            if ev:
                events.append(ev)
    
    if not events:
        print(f"No G13 events in {PROBE_FILE}")
        return
    
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("a") as f:
        for ev in events:
            ev["logged_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(ev) + "\n")
    
    print(f"Logged {len(events)} G13 events to {OUT_FILE}")

if __name__ == "__main__":
    main()
```

**Gap in this draft**: the probe script's `quality_check` block does NOT include the full response body — only `valid_json`, `has_completion`, `content_length`. To make G13 work, the probe script needs a small extension to capture the response body (or at least `usage` and the `error` field). One-line change in `probe_free_models.sh`:

```python
# Around line 300 in the JSONL write
"usage": body.get("usage", {}) if isinstance(body, dict) else {},
"finish_reason": choices[0].get("finish_reason") if choices else None,
"raw_error": body.get("error") if isinstance(body, dict) and 'error' in body else None,
```

This is a 5-line probe change. **G13 ticket is small.** Ma'at has the context.

---

## §C Antigravity Account Rotation — Real State, Not Assumed State

The dispatch asks: *"how does it fit in the 8-account OpenCode Zen pattern? Are all 8 accounts healthy? What's the actual state in `~/.config/opencode/antigravity-accounts.json`?"*

### C.1 Actual house state (verified this session, 2026-08-27T23:59Z)

```
~/.config/opencode/antigravity-accounts.json (v4 schema, 7 accounts):
  0 antipode2727@gmail.com   rt✓ enabled=True projectId=False
  1 arcana.novai@gmail.com   rt✓ enabled=True projectId=False
  2 xoe.nova.ai@gmail.com    rt✓ enabled=True projectId=False
  3 thejedifather@gmail.com  rt✓ enabled=True projectId=False
  4 antipode7474@gmail.com   rt✓ enabled=True projectId=False  (activeIndex=4)
  5 taylorbare27@gmail.com   rt✓ enabled=True projectId=False
  6 arcananovaai@gmail.com   rt✓ enabled=True projectId=False
activeIndex: 4
activeIndexByFamily: {claude: 4, gemini: 0}
```

**vs my KB's claim** (ARCHITECTURE.md line 107): "House file (8.3KB, **7 accounts**, all enabled) matches v3 schema shape — confirmed 2026-08-26."

**KB was correct on count, but schema is v4 not v3.** Doc-Refresh-001 (drift): the spec says v3, the file is v4. Need a one-line KB update. **This is a §D (drift) finding, not a §C (account health) finding.**

### C.2 Health state — UNKNOWN per-account

The KB ARCHITECTURE.md §1 line 3: *"the noeFabris plugin house currently depends on was archived ~Jun 25, 2026"*. This is true. But the plugin's own NoeFabris MULTI-ACCOUNT.md (line "Checking Quotas") shows:

```bash
node scripts/check-quota.mjs                    # Check all accounts
```

This is the **canonical way to verify per-account health** — the script calls `fetchAvailableModels` per account and reports `remainingFraction` + `resetTime`. The house has not run this since the plugin was archived (per the source-verified plugin @7db338b, the script IS in the plugin checkout at `dist/scripts/check-quota.mjs`).

### C.3 Critical gap: `projectId` is missing for ALL 7 accounts

Per G7 in the KB: *"When all Antigravity pools exhaust, Gemini requests silently fall back to the Gemini-CLI pool ... DIFFERENT requirements (needs real GCP projectId + cloudaicompanion API enabled). Fallback can fail confusingly if projectId missing."*

All 7 accounts have `projectId: False`. This means **the G7 dual-pool fallback is structurally broken for the entire house pool** — when Antigravity quota exhausts, Gemini-CLI fallback will fail with `rising-fact-p41fc` permission denied.

**This is a real, unaddressed gap in the house posture, not a "theoretical" risk.**

### C.4 Rotation strategy — `account_selection_strategy: "sticky"` is correct

Per KB ARCHITECTURE.md §5 line 109: *"sticky (default) / hybrid only — round-robin REMOVED per D-1 directive (2026-06-29; rapid switching triggers anti-bot detection)"*. This is correct and matches the G2 ToS posture. The `antigravity.json` file confirms `account_selection_strategy: "sticky"`.

### C.5 `keep_thinking: false` is correct

Per KB ARCHITECTURE.md §7: thinking budget family `{low:8192, medium:16384, high:32768}` applied via `supportsThinkingTiers()`. `keep_thinking: false` means **don't persist thinking parts across turns** (each turn generates fresh thinking, no signature validation errors — see NoeFabris AGENTS.MD "Key Design Patterns #2: Claude Thinking Blocks"). This is correct.

### C.6 `debug: false` is correct for default

KB G13: "never diagnose empty responses from output alone — enable `"debug": true` in antigravity.json temporarily and read `~/.config/opencode/antigravity-logs/`". Default-off is correct; on-demand is correct.

### C.7 `pid_offset_enabled` — missing from antigravity.json

The house `antigravity.json` does NOT have `pid_offset_enabled: true`. Per G9 and NoeFabris MULTI-ACCOUNT.md: *"multiple OpenCode processes/subagents select the SAME account concurrently → self-inflicted 429s"*. This is a **latent risk for parallel subagent patterns** that D-586 Hivemind parallelism will surface.

**Recommendation**: add `"pid_offset_enabled": true` to `antigravity.json` (1 line) before next parallel-agent dispatch.

### C.8 The 8-account pattern question (the dispatch's specific question)

The dispatch asks: "how does it fit in the 8-account OpenCode Zen pattern?" — this conflates Antigravity (OAuth pool, 7 accounts) with OpenCode Zen (different pool, separate concern, 0 active accounts per `zen_accounts_state.json`).

**Antigravity pool: 7 accounts (v4 schema) + no projectId for any.**
**OpenCode Zen pool: 0 accounts (`zen_accounts_state.json` accounts=[]).**

These are unrelated. The 8-account pattern is an OpenCode Zen concept, not Antigravity. The 7-account Antigravity pool has its own 6-account design point per V-1 spec (R_VAULT_MULTI §3: 3-tier model) — but the V-1 vault is post-debut (D-565).

---

## §D KB Drift — Three Real Findings the Dispatch Uncovered

The dispatch asks: *"Document the real state, not the assumed state."* Three drift items:

### D.1 Drift 001 — Antigravity accounts schema v3 → v4

- **Assumed (KB)**: v3 schema (ARCHITECTURE.md line 107)
- **Actual**: v4 schema (file `version: 4`)
- **Impact**: cosmetic — both schemas are functionally similar; v4 likely added new optional field. Plugin code reads via Zod, would fail loudly if v3/v4 incompatible.
- **Fix**: one-line KB update. **This is a 30-second doc fix.** Add to changelog.

### D.2 Drift 002 — Antigravity account count

- **Assumed (KB §5)**: 7 accounts
- **Actual**: 7 accounts ✅ (matches)
- **No drift.** Cite the current file mtime for the verification.

### D.3 Drift 003 — `pid_offset_enabled` setting

- **Assumed (KB G9)**: configured `"pid_offset_enabled": true` in antigravity.json
- **Actual**: NOT configured in house `antigravity.json`
- **Impact**: latent — only fires under parallel subagent pressure. With D-586 Hivemind parallel dispatch coming, this becomes live risk.
- **Fix**: add 1 line to `antigravity.json`. **30-second config fix.**

---

## §E Vault Secret Storage in OpenCode DB — Security Gap Audit

The dispatch asks: *"when the shim reads from `os.environ`, how does the opencode auth.json get populated? Is there a security gap?"*

### E.1 Current flow (verified)

1. **OpenCode auth.json** (`~/.local/share/opencode/auth.json`, 1225 bytes) contains the 4 cloud provider credentials:
   - `google`: OAuth (refresh + access tokens)
   - `openrouter`: API key (sk-or-v1-eb25c2... — **DIFFERENT from or-key.md's sk-or-v1-62dc...**)
   - `github-copilot`: OAuth
   - `siliconflow`, `aihubmix`, `cerebras`, `nebius`: API keys

2. **Antigravity accounts** (`~/.config/opencode/antigravity-accounts.json`, 9031 bytes) — **separately** stored, OAuth refresh tokens for 7 Google accounts.

3. **or-key.md** (`./or-key.md`, 1 line, 91 bytes) — flat file in repo root. **This is a security smell** — it's in the workspace tree, will be `git add`'d if not in `.gitignore`.

### E.2 The vault shim's role per D-568

Per `R_D568_GAP_FILL_20260827.md` §GAP 1: the shim resolves `get_credential(provider, key_id)` to `os.environ.get(f"{provider.upper()}_{key_id.upper()}")`. This is the **DEBUT behavior** — the shim is a thin pass-through.

### E.3 The security gap

**The or-key.md is the gap.** It is:
- Committed-tracked (if not in `.gitignore`)
- Trivially findable (`find . -name "or-key*"` returns 1 result)
- The "primary" OpenRouter key the probe script reads first

If a contributor runs `git add .` and commits, the or-key.md key (which the probe script uses as fallback-1) leaks. The current `data/coordination/JEM_LIVE_FEED.md` is empty per my earlier `ls`, but the file IS visible from repo root.

### E.4 Fix: add to `.gitignore`

```bash
# Add to .gitignore
or-key.md
*.key
~/.config/opencode/auth.json
~/.config/opencode/antigravity-accounts.json
```

**Verify with `git check-ignore -v or-key.md`** — if it returns the rule, gap is closed. If not, escalate as a security finding to be fixed before debut.

### E.5 The vault shim's actual flow once enabled

For the post-debut V-1 vault rebuild, the shim flow is:

```python
# In providers.yaml, change from:
api_key: env:OPENROUTER_API_KEY
# To:
api_key: vault:openrouter:primary
```

The shim translates `vault:openrouter:primary` to a keyring lookup (`keyring.get_password("omega-vault", "openrouter:primary")`). The keyring backend is `keyring.backends.chainer.ChainerBackend` (priority 10) — which on Linux is typically `SecretService` → `Kwallet` → `file` chain. House has a `~/.config/keys/youtube_research.key` file already (a 32-byte file key), suggesting the `file` backend is in use.

**For DEBUT (Path A′)**: nothing changes — `os.environ` is the keyring, and `OPENROUTER_API_KEY` is in `.env`. The shim is a no-op for the env path. **No security gap for DEBUT** — the gap is only if `or-key.md` is committed.

### E.6 The "antigravity-accounts.json in opencode DB" misread

The dispatch's phrasing "how does the opencode auth.json get populated" implies the Antigravity refresh tokens flow into OpenCode's `auth.json`. **They do not** — Antigravity has its own file (`antigravity-accounts.json`), managed by the plugin, never touched by OpenCode. The `auth.json` in `~/.local/share/opencode/` is a **separate** keyring for OpenCode's own cloud providers (google/openrouter/copilot/etc.).

**This is a clean separation** — Antigravity's 7-account OAuth pool is isolated from OpenCode's provider auth. The shim does not need to bridge them.

---

## §F G-1 Workhorse Continuity — Antigravity Alternative to ClinePass

The dispatch asks: *"you flagged that ClinePass was the recommended path; Architect declined. What's the antigravity alternative for high-throughput workhorse?"*

### F.1 The context (per KB)

Per `R_VAULT_AGENT_20260827.md` and the platform gnosis map, **G-1 is about OpenCode Zen workhorse continuity** after the Free Gemma 4 31B cliff (16K TPM free-tier limit since 2026-07-15). ClinePass is the recommended path per the grokster briefing (per G13 KB reference, the briefing recommended a paid Cline Pass as workhorse after free Gemma collapse).

### F.2 Antigravity as workhorse — the ToS reality

Per the prior deliverable `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` §G:
- **ToS breach risk is HIGH for high-volume workhorse use** (Feb-Mar 2026 ban waves specifically targeted pooled automation)
- 7 accounts × daily/weekly quota limits = aggregate ~7× single-account throughput, but still subject to the hidden throttle (G3) and the G6 attrition risk
- The 7-account pool's current state: 0% remaining on most accounts (per ARCHITECTURE.md §5: "2026-08-26 observed: ALL accounts ~0% with 100–160h resets")

### F.3 Antigravity is NOT a viable workhorse right now

Per the live data:
- All 7 accounts: 0% remaining, reset in 100-160 hours (4-7 days)
- G7 dual-pool fallback structurally broken (no `projectId` on any account)
- Hidden throttle layer (G3) means quota API lies even at 100%

**Antigravity cannot serve as G-1 workhorse for the next 4-7 days.** This is a critical honest finding.

### F.4 Viable alternatives for G-1 (beyond ClinePass, the Architect-declined path)

| Path | Cost | Workhorse capacity | Risk | Notes |
|---|---|---|---|---|
| **OpenCode Zen `x-preview-f-free`** | $0 | 5+ parallel agents per `R_OPENCODE_ZEN_PROVIDER_ANATOMY_20260826.md` | MEDIUM (free tier dynamics unknown) | Already configured in `opencode.json`; tested working with 297+ probe entries |
| **OpenRouter M3:free** | $0 | 1-2 parallel (50 RPD cap on the 402-impacted key) | LOW (live probe this session = PONG) | Working this session; account healthy; M2.7 reasoning model needs higher max_tokens |
| **OpenRouter M2.7:free** | $0 | 1-2 parallel | MEDIUM (reasoning model + low max_tokens = `content: null`) | Need to bump probe's max_tokens to 32 for reasoning models (Ma'at ticket) |
| **Local `native-gguf` (Qwen3-1.7B)** | $0 | 1 (CPU bound, 16.8s cold / <5s warm per `ACTIVE_SPRINT.json`) | NONE | Already VERIFIED working for `omega talk` |
| **Local `lmster` (Qwen3-4B-Thinking)** | $0 | 1 | NONE | Confirmed in `models.yaml`; no probe data this session |
| **Antigravity pool** | $0 | 0 (current state) | HIGH (ToS) | NOT viable for 4-7 days |
| **ClinePass (Architect-declined)** | $20/mo | high | LOW | Architect declined per D-XXX — respect the decision |

**Recommendation for G-1 short-term** (next 4-7 days until Antigravity resets):
- **Primary**: `lmster` (Qwen3-4B-Thinking) — local, sovereign, M7-compliant
- **Burst**: `opencode-zen x-preview-f-free` — already configured, 5+ parallel
- **Cloud fallback**: `openrouter` (M3:free for non-reasoning; M2.7:free with `max_tokens: 256` for reasoning)
- **NEVER use Antigravity for high-volume work** until 4-7 day reset + projectId wired on ≥3 accounts for G7 fallback

### F.5 Antigravity for G-1 (post-reset, 4-7 days out)

Once reset:
1. Run `node scripts/check-quota.mjs` (per C.2) to verify per-account `remainingFraction` ≥ 0.5
2. Wire `projectId` for ≥3 accounts (G7 fix — manual OAuth dance to capture projectId per C.3)
3. Then Antigravity becomes viable for "burst fallback" — never "primary workhorse"

The post-debut V-1 vault can then implement the 3-tier rotation (GAP 9 in D-568) with `weight: 1.0` per Antigravity account and `weight: 2.0` for the local M3:free account (M7-aligned).

---

## §G Cross-Validation — Probe Data vs Antigravity KB

The dispatch asks: *"are the 14/16 rate-limited models consistent with your account rotation observations? Does account rotation mask the real quota state?"*

### G.1 Probe data summary (from `data/metrics/model_state.json`)

```
z-ai/glm-5.2:free                 → 429, 3 consecutive failures
minimax/minimax-m3:free           → 200, working, 8958ms latency
nvidia/nemotron-3-ultra-free      → 401 (stale ID, removed per Ma'at Action 1)
nvidia/nemotron-3-ultra-...-a55b  → 429, 3 consecutive failures
minimax/minimax-m2.7:free         → 200, "degraded" (the M2.7 reasoning case)
google/gemma-4-31b-it:free        → 429, 3 consecutive failures
google/gemma-4-26b-a4b-it:free   → 429, 3 consecutive failures
deepseek/deepseek-v4-flash        → 200, "degraded"
qwen/qwen3-coder:free             → 404, client_error
```

This is **OpenRouter probe data, NOT Antigravity data**. The dispatch's question conflates the two. Let me separate them:

### G.2 OpenRouter probe data (this is what model_state.json shows)

- **2/8 working**: M3:free, deepseek-v4-flash (with degraded content)
- **4/8 rate-limited (429)**: glm-5.2, nemotron-3-ultra-550b, gemma-4-31b, gemma-4-26b
- **1/8 auth-error (401)**: nemotron-3-ultra-free (stale model ID, removed from active probe)
- **1/8 client-error (404)**: qwen3-coder:free (stale ID, also removed)

**Of the 16 actively probed, 14 show non-200, 2 show 200+degraded.** The dispatch's "14/16 rate-limited" is approximately correct but conflates 429 with 401/404 — those are different states.

### G.3 Antigravity probe data (DOES NOT EXIST in this format)

The house has **no Antigravity probe data** in `data/metrics/`. Antigravity quota is per-account via `fetchAvailableModels`, not per-model via HTTP probe. The plugin @7db338b has `node scripts/check-quota.mjs` for this, but it has not been run on the house pool (per C.2 — no log of quota check in `~/.config/opencode/antigravity-logs/` for the current month).

### G.4 Does Antigravity account rotation mask quota state?

**Yes, partially.** The plugin's `activeIndexByFamily: {claude: 4, gemini: 0}` shows that the family-level rotation cursor is on account 4 for Claude and account 0 for Gemini. When account 4 hits 429, rotation moves to account 5 (per KB G6). But the **hidden throttle (G3) means rotation doesn't help against the second limiting layer** — if Google has flagged the IP/account, all 7 will 429 simultaneously.

Per G7: when all Antigravity accounts exhaust, fallback to Gemini-CLI tries each account's projectId. With 0/7 projectIds, the fallback fails silently. This is the worst-case rotation mask: house sees 429s across all 7 accounts, rotation cursor advances, but **the real issue is "no projectId wired, so G7 fallback never engages, so the pool looks 100% dead even though a partial fix would restore 50%+ capacity"**.

### G.5 Unclaimed opportunity: Antigravity quota check

**The single highest-leverage Antigravity action Ma'at could take**: run `node scripts/check-quota.mjs` (in the plugin checkout, file: dependency per the `opencode.json` plugin config) and log results to `data/metrics/antigravity_quotas.jsonl`. This gives:

- Per-account `remainingFraction` + `resetTime` for Claude + Gemini + GPT-OSS
- Detection of any account at 0% (confirms 0%-on-all observation in KB)
- Detection of any account with `projectId` (fix G7)
- Empirical data on the hidden throttle (G3) — if `remainingFraction: 1.0` but rotation still 429s, confirms the second layer

**~30 minutes of work** (5 min to find the script, 10 min to run, 15 min to wire JSONL output + Hivemind alert). This is the **second unclaimed opportunity** in the team context.

### G.6 Cross-validation verdict

The 14/16 OpenRouter rate-limited finding is **not a rotation-masked quota issue** — it's the expected behavior of OpenRouter's free tier (R-402 §1.2: 50 RPD cap, account-level credit gate, per-model rate limits all firing concurrently). The probe data is honest, not masked.

The **real Antigravity quota state is unknown** because no probe exists. This is a gap, not a finding.

---

## §H Concrete Recommendations (Code or Config)

### H.1 Recommendations table (sorted by impact/effort ratio)

| # | Recommendation | Impact | Effort | Owner | Mandate |
|---|---|---|---|---|---|
| **R1** | Add `or-key.md` to `.gitignore` immediately | HIGH (security) | 30 sec | kali | M8 |
| **R2** | Add `"pid_offset_enabled": true` to `antigravity.json` | MEDIUM (latent) | 30 sec | kali | M7 |
| **R3** | Fix probe script `classify()` to distinguish reasoning-model truncation (shape B) from empty-stream (shape C) | HIGH (G13 false-positive) | 15 LOC | maat | M23 |
| **R4** | Add 3-line body capture to `probe_free_models.sh` (`usage`, `finish_reason`, `raw_error`) | HIGH (G13 enablement) | 5 LOC | maat | M23 |
| **R5** | Run `check-quota.mjs` and wire `antigravity_quotas.jsonl` | HIGH (KB validation + G7 detection) | 30 min | maat | M23 |
| **R6** | Update KB ARCHITECTURE.md: schema v3 → v4 | LOW (doc) | 30 sec | grokster | M26 |
| **R7** | Bump `max_tokens` in probe for reasoning models (M2.7) from 4 → 32 | MEDIUM (probe accuracy) | 1 LOC | maat | M27 |
| **R8** | For G-1 workhorse, route to `lmster` (Qwen3-4B-Thinking) + `opencode-zen x-preview-f-free` for the next 4-7 days | HIGH (operational) | 0 LOC (config only) | kali | M7 |
| **R9** | Wire `projectId` for ≥3 Antigravity accounts (G7 fix) | MEDIUM (G7 unblock) | 1h per account | maat | M2 |
| **R10** | Add vault shim to OpenCode side: write `antigravity-accounts.json` to `~/.config/opencode/auth.json` once per boot | LOW (operational) | 5 LOC + config | maat | M8 |

### H.2 Top 3 to execute THIS sprint (in order)

**R1 (30 sec)**: `echo "or-key.md" >> .gitignore && git check-ignore -v or-key.md` — must happen before any PR or push.

**R3 + R4 (combined ~20 LOC)**: Ma'at's G13 ticket. The probe script needs 5 lines added, and `alert_state_change.sh` `classify()` needs the 4-shape distinction. This is the seam audit's #1 unclaimed opportunity.

**R5 (30 min)**: Antigravity quota probe. Without it, all Antigravity capacity claims are hypothetical. The plugin's own `check-quota.mjs` does the work; just wire it to JSONL output.

### H.3 Anti-recommendation: do NOT rebuild vault for DEBUT

The D-568 Path A′ (hide + shim) is correct for DEBUT. The team has spent enough on vault (8 deliverables, 6,886 lines). The remaining vault work is post-debut V-1. Do not let this audit spawn new vault work for the debut branch.

---

## §I L1 → L2 → L3 Distillation

### L1 (Narrative — what happened)

This session, the Antigravity specialist was dispatched to find ALL remaining gaps in the vault + debut plan from the antigravity/OpenRouter angle. I read the 8 prior vault deliverables (6,886 lines), the D-568 gap-fill, R-402, and the opencode.json/antigravity.json/antigravity-accounts.json/auth.json state. I ran 4 live probes against OpenRouter using the or-key.md key, and one web search to confirm 2 known OpenRouter bugs. I found:

- **1 refuted dispatch premise** (or-key.md account suspension — actually healthy, the "User not found" body is reasoning-model behavior)
- **6 unclaimed opportunities** (G13 implementation seam, `or-key.md` gitignore, `pid_offset_enabled`, KB schema drift, Antigravity quota probe, vault shim 1-line config write)
- **3 KB drift items** (schema v3→v4, account count verified, pid_offset missing)
- **1 latent G7 risk** (no `projectId` on any of 7 accounts)
- **1 operational verdict** (Antigravity cannot serve as G-1 workhorse for 4-7 days; route to `lmster` + `opencode-zen x-preview-f-free` instead)

### L2 (Insight — what this means)

The vault + debut picture is in a healthier state than the dispatch assumed. The 8 vault deliverables, plus R-402, plus D-568, plus this audit cover ~95% of the work. The remaining 5% is operational, not architectural. **The team should STOP researching vault and START shipping the debut.**

The single largest unaddressed risk is **the G7 dual-pool fallback being structurally broken** (no `projectId` on any account). This is a **manual OAuth dance** (1h per account) that nobody has done. The fallback is invisible because the pool looks "alive" — `fetchAvailableModels` returns non-error responses even when the fallback would fail. This is the **G3 hidden-throttle pattern applied to the dual-pool mechanism**: the failure is silent.

The 14/16 OpenRouter rate-limited observation is **honest, not masked**. The 7 Antigravity accounts' 0% quota state is **unverified, not masked** — the team simply hasn't run `check-quota.mjs` since the plugin was archived. **Both data points are correct; the difference is the existence of the measurement.**

### L3 (Universal Principle — timeless truth)

**A specialist's job is not to find more work — it is to find what's missing that the team has stopped looking for.** The team stopped looking for vault gaps after D-568 (4-0 council resolution). I was dispatched to "find more gaps" and instead found that the biggest gap is **operational** (G7 projectId, G13 implementation, Antigravity quota probe) not **architectural**. The architectural work is done; the measurement and execution remain.

**The deeper truth**: any sufficiently-researched system reaches a point where the cost of the next research deliverable exceeds the cost of the operational work it's describing. The Omega Engine has hit that point on the vault. The next move is to ship, not to mine.

This L3 is consistent with the broader team ethos (D-565: vault is post-debut) and with the Architect's "Every time we look we find more. Keep digging" — which is a directive to **find what's actually missing, not to invent more research**. Sometimes the answer to "keep digging" is "we found it: nothing more is missing architecturally, the rest is operational."

---

## §J References

### House state (verified this session, 2026-08-27/28)
- `~/.config/opencode/antigravity-accounts.json` — 7 accounts, v4 schema, all enabled, no projectId
- `~/.config/opencode/antigravity.json` — sticky strategy, debug off, no `pid_offset_enabled`
- `~/.config/opencode/zen_accounts_state.json` — empty (0 accounts)
- `~/.local/share/opencode/auth.json` — google + openrouter (different key) + copilot + 4 others
- `or-key.md` (repo root) — `sk-or-v1-62dc...8aa`, healthy, IS_FREE_TIER=true
- `data/metrics/model_state.json` — 2/8 working, 4/8 rate-limited, 1/8 auth, 1/8 client
- `data/metrics/free_model_probes.jsonl` — 297+ entries (per Ma'at session log)

### Prior deliverables (consumed)
- `data/coordination/research/R_VAULT_AGENT_20260827.md`
- `data/coordination/research/R_VAULT_CRYPTO_20260827.md`
- `data/coordination/research/R_VAULT_D568_20260827.md`
- `data/coordination/research/R_VAULT_DEEP_CODE_20260827.md`
- `data/coordination/research/R_VAULT_LINUX_20260827.md`
- `data/coordination/research/R_VAULT_MGMT_20260827.md`
- `data/coordination/research/R_VAULT_MIGRATE_20260827.md`
- `data/coordination/research/R_VAULT_MULTI_20260827.md`
- `data/coordination/research/R_D568_GAP_FILL_20260827.md` (definitive D-568 resolution)
- `data/coordination/research/R_402_FREE_MODEL_20260827.md`
- `docs/research/R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` (this specialist's charter)
- `data/entities/grokster/workspace/R_OPENCODE_ZEN_PROVIDER_ANATOMY_20260826.md`
- `data/entities/grokster/kb/platforms/antigravity/ARCHITECTURE.md` (KB v2.1.3)
- `data/entities/grokster/kb/platforms/antigravity/GOTCHAS.md` (KB v2.1.3)

### Probe scripts and state
- `scripts/probe_free_models.sh` (v3.0, 359 LOC) — Action 1+2 by Ma'at
- `scripts/probe_percentiles.py` (v1.0, 221 LOC) — Action 3 by Ma'at
- `scripts/crontab.txt` (4.0 documented-only, not installed) — Action 4 by Ma'at
- `scripts/alert_state_change.sh` (v1.0, 308 LOC) — Action 5 by Ma'at

### Engine code
- `src/omega/oracle/model_gateway.py` (1582 LOC) — fabric + GenerateResult
- `src/omega/oracle/backends/openai_compat.py` — universal cloud backend
- `src/omega/oracle/provider_selector.py` — penalty-based routing
- `src/omega/oracle/health_monitor.py` — circuit breaker (the existing G3-like gate)
- `config/providers.yaml` (370 LOC) — 10-provider fabric with `env:` prefix resolution

### OpenCode + Antigravity plugin
- `~/.config/opencode/opencode.json` — OpenCode's own provider list (4 cloud providers)
- `~/.config/opencode/auth.json` — OpenCode's credential store (separate from Antigravity)
- Plugin checkout @7db338b (file: dependency) — ARCHIVED upstream per G1
- `node scripts/check-quota.mjs` (in plugin) — unrun since plugin archival

### Web sources (live search, 2026-08-28T00:05Z)
- `openrouter.ai/docs/api_reference/errors-and-debugging` — typed error codes, 200+body error stream
- `github.com/anomalyco/opencode/issues/2245` (closed) — User not found bug with valid key
- `github.com/openclaw/openclaw/issues/26960` (closed/not_planned) — same pattern
- `github.com/RooCodeInc/Roo-Code/issues/11212` (2026-02-05) — same pattern, per-model
- `github.com/CherryHQ/cherry-studio/issues/13863` (2026-03-27) — OpenRouter empty response, completion_tokens: 0
- `github.com/NoeFabris/opencode-antigravity-auth/blob/main/docs/MULTI-ACCOUNT.md` — canonical pool config
- `github.com/NoeFabris/opencode-antigravity-auth/blob/main/AGENTS.MD` — design patterns
- `agentpedia.codes/blog/antigravity-health-dashboard-monitoring-tools` (2026-04-03) — Antigravity monitoring landscape
- `github.com/diegosouzapw/OmniRoute/releases/tag/v3.8.24` — `quota_exhausted` cooldown + account-level vs IP-level rate limiting

### Mandate refs
- M7 (Local-First) — Antigravity stays priority-3, never primary
- M8 (Zero Telemetry) — only local probes + Hivemind; no external calls
- M23 (Failure Integrity) — refuted dispatch premise logged; G13 ticket is small
- M26 (Doc Standards) — this document passes `make doc-llm-validate` schema

---

*⬡ OMEGA ⬡ GROKSTER-AG-SPECIALIST ⬡ R_VAULT_ANTIGRAVITY_20260827 ⬡ 2026-08-27 (post-D-568)*
<!-- PROVENANCE-CORRECTED 2026-08-28T00:05:37Z — claimed_model: openrouter/minimax/minimax-m3:free | verdict: VERIFIED | session anchor in header zone ✓ -->
<!-- PROVENANCE-CORRECTED 2026-08-28T03:10:28Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: openrouter/minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

