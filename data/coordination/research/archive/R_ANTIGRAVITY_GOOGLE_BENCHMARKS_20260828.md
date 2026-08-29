---
schema_version: "1.0"
document_type: "research_benchmark_report"
document_id: "R-ANTIGRAVITY-GOOGLE-BENCHMARKS-20260828"
title: "Antigravity — Google Gemini Flash Model Benchmarks (BLOCKED — No API Key)"
status: "BLOCKED — INSUFFICIENT CREDENTIALS"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
prepared_by: "Antigravity (model-benchmarking)"
prepared_for: "grokster (Platform/Provider Specialist)"
session: "ses_fe8cf0b39ffeL3L8eaMEj3CW9H"
m23_status: "TOOL-CHAIN-COLLAPSE — credentials not provisioned to this sandbox"
---

# 🔱 Antigravity → grokster — Google Gemini Flash Benchmarks
**AP Token**: `AP-ANTIGRAVITY-GOOGLE-BENCHMARKS-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_model_bench ⬡ BLOCKED

**Date**: 2026-08-28
**Source brief**: `ses_fe8cf0b39ffeL3L8eaMEj3CW9H` (grokster, 2026-08-28)
**Original ticket**: Research Request 4 — Background Worker Candidates
**Status**: ❌ **BLOCKED** — credentials not present in this sandbox

---

## §0 — EXECUTIVE SUMMARY (TL;DR)

| Item | Status |
|------|--------|
| **TPS table** | ❌ Not produced — no API key |
| **Latency table** | ❌ Not produced — no API key |
| **Context window** | ⚠️ Partial — public docs only |
| **Cache behavior** | ⚠️ Partial — public docs only |
| **Task suitability** | ❌ Refused — empirical data required, none available |
| **Top-3 recommendations** | ❌ Refused — see §6 for alternative deliverable |
| **Rate limit observations** | ❌ Not produced — no API key |

**M23 verdict**: This is a `[TOOL-CHAIN-COLLAPSE]` event. The mandatory tool
(`curl https://generativelanguage.googleapis.com/...`) is broken because
`GOOGLE_API_KEY` is unset in this session. I will **NOT** synthesize benchmark
numbers (M23 + AGL-001 "don't fabricate"). The Architect must provision a key
before this report can be completed.

---

## §1 — THE BLOCKER (WHAT'S MISSING)

### 1.1 Credentials check (executed at session start)

```bash
$ env | grep -iE "google|gemini"
PATH=...                                      # only PATH matched
$ test -n "$GOOGLE_API_KEY" && echo set || echo "NOT set"
NOT set
$ test -n "$GEMINI_API_KEY" && echo set || echo "NOT set"
NOT set
$ test -f ~/.config/opencode/antigravity-accounts.json && echo ok || echo "no"
no
$ cat ~/.config/opencode/zen_accounts_state.json | jq '.accounts | length'
0
```

### 1.2 Endpoint reachability (no auth probe)

```bash
$ curl -sS --max-time 5 "https://generativelanguage.googleapis.com/v1beta/models"
{
  "error": {
    "code": 403,
    "message": "Method doesn't allow unregistered callers ... use API Key",
    "status": "PERMISSION_DENIED"
  }
}
```

Endpoint is reachable but requires an API key for any model-listing or
chat call. No path to empirical data exists in this session.

### 1.3 Filesystem check

- `scripts/probe_free_models.sh` — exists, but is **OpenRouter-only** (uses
  `sk-or-v1-*` keys, hits `openrouter.ai/api/v1/models`). Does **not** probe
  Google AI Studio.
- `scripts/check_free_models.sh` — exists, partially probes Google AI
  Studio but iterates a hardcoded list (line 51+); would also fail with no
  key in env.
- `~/.config/opencode/antigravity-accounts.json` — **does not exist** in
  this sandbox.
- `.env` — `GOOGLE_API_KEY` field present but unset (`your_google_api_key_here`).

### 1.4 Brief assumption mismatch

The brief states *"The Architect has 8 Google accounts with API key access"*.
That is true at the Architect's level, but **none of those keys have been
provisioned into this Antigravity sandbox**. I am running with zero Google
credentials. The brief's method section ("use the script if it exists / use
the Omega Engine's provider system to send test prompts") fails on both
paths because the underlying auth is missing.

---

## §2 — PUBLIC-DOCS ONLY SCORECARD (no empirical data)

Per the brief's "Task suitability" requirements, I refuse to score
1–5 without measurement. What follows is a **non-ranked** summary from
public Google AI Studio docs (https://ai.google.dev/gemini-api/docs/models,
retrieved 2026-08-28 via memory of the published spec). **Treat this as
orientation, not a recommendation.**

| Model (public spec) | Input ctx | Output ctx | Cache? | Notes |
|---------------------|-----------|------------|--------|-------|
| `gemini-2.5-flash` | 1,048,576 | 65,536 | Yes (implicit, free tier does **not** include caching discount) | Confirmed free tier per Architect's note in `KALI_TO_GROKSTER_GOOGLE_API_20260828.md` §1 |
| `gemini-2.5-flash-lite` | 1,048,576 | 65,536 | Yes (same caveat) | Slower-context variant; not yet confirmed available on free tier — needs probe |
| `gemini-3-flash` (and variants 3.5/3.6/3.7 per Architect) | not confirmed stable | — | Yes (per Gemini 3 generation) | **Existence of `gemini-3-flash` on the free tier is unconfirmed by this report.** Architect's note lists 3/3.5/3.6/3.7 but does not pin which are `flash` vs `pro`. **Requires key to verify.** |
| `gemini-2.5-pro` | 1,048,576 | 65,536 | Yes | Not in brief scope (this is a *pro* model, not a flash); listed for context |

**Cache note (public docs)**: Gemini's explicit `cachedContent` is
available on API-key auth, but Google's free-tier pricing page does not
advertise a cache-hit discount — i.e. the cache feature exists, but
cost-savings on free tier are unclear without a billing line item. **Must
verify with billing line, not possible without key.**

---

## §3 — WHY I WILL NOT FABRICATE NUMBERS

The brief asks for:
- TPS at 4 context sizes (1K / 10K / 100K / 500K)
- TTFT and total latency
- Cache hit rate
- Rate-limit behavior on 429
- 1–5 suitability scores per (model × task)

**All of these are empirical measurements.** Producing them without
measurement would violate:

- **M23 — Failure Integrity**: broken tool (no key) → STOP, report. No
  synthesis.
- **AGENTS.md §"What NOT To Do"**: "Do not synthesize a result when a
  mandatory tool is broken (M23)."
- **`.opencode/rules/04-sovereign-search.md`**: `[TOOL-CHAIN-COLLAPSE]`
  directive when the local + remote path both fail.
- **AGL-001 (Antigravity Locomotion Law #1)**: "Don't fabricate. If you
  don't know, say so."

Faking a TPS table for 8 Google accounts × 4 context sizes × 4 models
would create downstream harm: grokster would route the debut's background
worker traffic to a model I *guessed at*, not measured. That is exactly
the kind of soft-failure M23 was written to prevent.

---

## §4 — WHAT WOULD UNBLOCK THIS REPORT (30-second fix)

In order of preference (pick any one):

1. **One-line env export** (best for live benchmarking):
   ```bash
   export GOOGLE_API_KEY="AIza..."   # any of the 8 Architect keys
   ```
   Then re-run this benchmark. The full report takes ~45 min of API calls.

2. **Key file on disk** (best for repeatable runs):
   ```bash
   echo "AIza..." > ~/.config/opencode/google_api_key
   chmod 600 ~/.config/opencode/google_api_key
   ```

3. **Antigravity OAuth path** (if the brief intended the OAuth provider
   instead — `KALI_TO_GROKSTER_GOOGLE_API_20260828.md` §1 hints these
   are different):
   ```bash
   # Requires populating ~/.config/opencode/antigravity-accounts.json
   # AND setting ANTIGRAVITY_CLIENT_SECRET in env
   # AND running scripts/antigravity_quota_probe.py to refresh tokens
   ```

4. **Delegate to a subagent that already has the key** — if any other
   session in Hivemind has the key bound, route via
   `hivemind_submit_handoff` and have them run the benchmark on my
   behalf. **I checked `hivemind_get_awareness` semantics — it
   doesn't reveal env-var ownership, so this requires the receiving
   entity to confirm out-of-band.**

---

## §5 — RISK IF THIS GOES UNFIXED

- **Grokster's P0 sprint task** ("benchmark Gemini Flash for background
  workers") will not land before the soft launch.
- The provider routing decisions in `config/providers.yaml` for the
  Flash-tier background worker pool will be made **on faith**, not data.
- If `gemini-3-flash` is in fact faster than `gemini-2.5-flash` for our
  workload (likely but unproven), routing to 2.5 will waste free-tier
  capacity and degrade L3 distillation throughput.

**Severity**: medium. The system can ship without this benchmark — it
already runs on the pre-Antigravity config — but the debut will lack
the empirical backing that AGENTS.md mandates for routing decisions.

---

## §6 — ALTERNATIVE DELIVERABLE (what I *can* give you now)

While waiting for a key, here is the **benchmark harness** — a script
that, the moment a key is set, will produce the full report in ~45 min.
Drop it into `scripts/bench_google_flash.sh` and run.

```bash
#!/usr/bin/env bash
# bench_google_flash.sh — produces the table in §0 of the blocked report
# Usage: GOOGLE_API_KEY=AIza... ./scripts/bench_google_flash.sh
set -euo pipefail
: "${GOOGLE_API_KEY:?Set GOOGLE_API_KEY before running}"

ENDPOINT="https://generativelanguage.googleapis.com/v1beta/models"
MODELS=("gemini-2.5-flash" "gemini-2.5-flash-lite" "gemini-3-flash")
SIZES=("1000" "10000" "100000" "500000")  # input token counts
OUT="data/metrics/google_flash_bench_$(date -u +%Y%m%dT%H%M%SZ).jsonl"

echo "{ts,model,size,tokens_in,tokens_out,ttft_ms,total_ms,tps,status}" > "$OUT"

for m in "${MODELS[@]}"; do
  for s in "${SIZES[@]}"; do
    # Build a payload of ~$s tokens (use lorem ipsum padding)
    PROMPT=$(python3 -c "print('lorem ipsum ' * ($s // 2))")
    PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({
  'contents':[{'parts':[{'text': sys.argv[1]}]}],
  'generationConfig':{'maxOutputTokens': 256}
}))" "$PROMPT")
    # Time the call
    START=$(date +%s%N)
    RESP=$(curl -sS -X POST "$ENDPOINT/$m:generateContent?key=$GOOGLE_API_KEY" \
      -H 'Content-Type: application/json' -d "$PAYLOAD" \
      -w '\nHTTP:%{http_code}\nTIME_TOTAL:%{time_total}\nTTFB:%{time_starttransfer}\n')
    END=$(date +%s%N)
    # ... parse, append to $OUT
    echo "  $m @ $s → see $OUT"
  done
done
```

(Full version with retry, cache-test, and rate-limit observation lives at
`scripts/bench_google_flash.sh` once a key is available. The above is the
skeleton so grokster can verify the method before re-running.)

---

## §7 — HANDOFF

**Action requested from grokster (urgent, blocks the P0)**:

1. **Provision a key** to this Antigravity sandbox (env var or file —
   see §4). Even one of the 8 Architect keys is enough to unblock the
   full report.
2. **OR escalate**: confirm that the soft launch can proceed with the
   pre-Antigravity routing (`config/providers.yaml` as it stands) and
   defer the benchmark to post-debut.
3. **OR clarify** whether "the 8 Google accounts" were intended to
   refer to Antigravity OAuth (which has its own credential flow at
   `scripts/antigravity_quota_probe.py`) — in which case I need
   `~/.config/opencode/antigravity-accounts.json` populated, not an
   API key.

**No code changed, no config touched, no synthesis produced.** This
report exists to surface the blocker, not to fake an answer.

---

## §8 — MANDATE COMPLIANCE CHECKLIST

| Mandate | Status | Note |
|---------|--------|------|
| M1 AnyIO | N/A | No Python code written |
| M7 Local-First | N/A | No inference attempted |
| M8 Zero Telemetry | ✅ | No external calls made beyond endpoint-reachability check |
| M11 Soul Integrity | ✅ | This *is* a distillation — the L1 fact is "no key = no benchmark", captured for the entity |
| M13 Temple-Grade | N/A | No release artifact produced |
| M23 Failure Integrity | ✅ | **`[TOOL-CHAIN-COLLAPSE]` declared, not synthesized** |
| M24 Venv Sovereignty | N/A | No `pip install` |
| M27 Tracking Integrity | ✅ | Status block follows 5-Tier Tracking |

---

*⬡ OMEGA ⬡ KALI ⬡ ANTIGRAVITY-BENCH-BLOCKED-v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
