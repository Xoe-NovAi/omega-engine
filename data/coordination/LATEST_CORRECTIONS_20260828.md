# 🔱 LATEST CORRECTIONS — Cross-Session Sync (2026-08-28)
**AP Token**: `AP-LATEST-CORRECTIONS-20260828-v1.0.0`
**Date**: 2026-08-28 ~20:25 UTC
**From**: grokster (Cross-Platform Expertise Specialist)
**To**: All expert sessions (cline, antigravity, copilot, Roc, Carmack, Researcher, and any future specialists)
**Status**: 🔴 ACTIVE — read BEFORE any dispatch

> **MANDATORY PRE-DISPATCH READING**: Every expert session should read this file before beginning work. If your session_gnosis contradicts anything here, THIS FILE WINS.

---

## §0 — Why This File Exists

On 2026-08-28, the Architect corrected several assumptions that had propagated through the session network:

1. "GPT 5.3" was actually **GLM 5.3 Flash (Z.ai)**, not GPT-5.3-Codex
2. DeepSeek V4 Flash **free variant was removed** Aug 28 — use `deepseek-v4-flash-0731` (paid)
3. The Cline provider has a **namespace bug** (`mimo-v2.5` should be `minimax/mimo-v2.5`)
4. The `google`/`google-compat` providers **bypass the multi-key factory** (need refactor to `RemoteProvider` subclass)
5. The context accounting mystery is **CLOSED** — the "~60K jump" is the compressed summary being loaded as INPUT in a single turn
6. The 2 P0 cut-tool bugs (EXCEPTIONS + inline comments) are **already fixed** in the current code

These corrections were made to Grokster but did not propagate to the other specialist sessions. This file is the propagation mechanism.

---

## §1 — Model Identity Corrections

### ❌ WRONG: "GPT 5.3" = GPT-5.3-Codex
- Two reports were produced on the wrong model: `R_ANTIGRAVITY_GPT53_20260828.md` and `R_RESEARCHER_GPT53_CLINE_20260828.md`
- These should be marked **SUPERSEDED**
- The real model the Architect was referring to is **GLM 5.3 Flash (Z.ai)**
- Authoritative report: `data/coordination/R_RESEARCHER_GLM53_FLASH_CLINE_20260828.md`

### ✅ CORRECT: GLM 5.3 Flash (Z.ai)
- 320B/18B MoE, 1M context, MIT weights
- $0.075/$0.25 per 1M (50% launch discount until **Sep 9, 2026 UTC+8**)
- Intelligence Index 57 (#4/111 open weights per AA)
- Cline integration: 2 paths — native "Z AI" provider OR OpenAI-Compatible with `https://api.z.ai/api/coding/paas/v4`
- OpenRouter ID: `z-ai/glm-5.3-flash`
- **Ox Alpha = GLM 5.3 Flash** (confirmed per session_gnosis v6/v7)

---

## §2 — Model Availability Corrections

### DeepSeek V4 Flash
- ❌ `deepseek/deepseek-v4-flash:free` returns **404** (removed 2026-08-28)
- ✅ Use `deepseek/deepseek-v4-flash-0731` (paid, ~$0.0587/$0.1173 per 1M on OpenRouter)

### Nemotron 3 Ultra
- ❌ `nvidia/nemotron-3-ultra-550b-a55b:free` is **RPD-exhausted** (HTTP 429)
- Cannot be used in planning or dispatch

### GPT 5.x
- ❌ "GPT 5.3" does NOT exist on OpenRouter (only GPT 5.6 family: Luna, Terra, Sol)
- ✅ GPT 5.6 Sol exists on OpenCode Zen as a paid model

### OpenCode Zen (newly unlocked)
- Needs `OPENCODE_API_KEY` in `.env` (Architect action pending)
- Unlocks 8 free models: `deepseek-v4-flash-free`, `laguna-s-2.1-free`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `hy3-free`, `ling-3.0-flash-fin-free`, `muse-spark-1.2-contributor-free`

### Laguna S 2.1 (NEW)
- Poolside AI, 118B/8B MoE, 1M context
- OpenMDW-1.1 license (open-weight)
- Free tier: 200 req/day, or $0.10/$0.20/$0.01 cache per 1M
- **Already natively supported by Cline** (docs.cline.bot/provider-config/poolside)
- Privacy flag: OpenRouter free tier permits Poolside to train on inputs/outputs

---

## §3 — Configuration Corrections

### Cline provider (`config/model_registry/providers/cline.yaml`)
- ❌ Current namespace: `mimo-v2.5` (wrong)
- ✅ Fix to: `minimax/mimo-v2.5` (Cline namespace bug)

### Google provider (`config/model_registry/providers/google.yaml`)
- ✅ 8-key `api_keys:` list using `env:GOOGLE_API_KEY_1..8` references (DONE)
- ✅ 11 Gemini models in `supported_models` (DONE)
- Note: `google`/`google-compat` providers **bypass the multi-key factory** — refactor to `RemoteProvider` subclass is V-1 work

### oracle_cli.py
- ✅ `_inject_vault_to_env()` added — decrypts vault at CLI edge, populates `os.environ`
- This is the sole vault→env injection point in-process

### .env
- ✅ Plaintext keys REMOVED (comment explains vault migration)
- Still has `CLINE_API_KEY` (pre-existing pattern, not removed in this arc)

---

## §4 — Vault + Gemini API Status

### Vault (WORKING)
- 7 Google API keys vaulted to `data/vault/keys.json.enc` (Argon2id + age, 1,149 bytes)
- Key 2 (xoe.nova.ai primary) denied HTTP 403 — using secondary key instead
- Master key: `~/.config/omega/vault_master.key` (0o600 perms)

### Gemini API (WORKING)
- `gemini-2.5-flash`: ✅ "hello" in 1.3s
- `gemini-3.1-flash-lite`: ✅ "hello" in 2.5s
- `gemini-3-flash-preview`: Uses thinking mode (needs maxOutputTokens≥100)

---

## §5 — Model Fleet for 8-Account Cline Review (Option E-prime-final)

| Account | Model | Role | Cost/1K req |
|---------|-------|------|-------------|
| 1–3 | `minimax/minimax-m3:free` | Long-write champion (D-585) | $0 |
| 4–7 | `deepseek/deepseek-v4-flash-0731` | Bulk coding | ~$0.069 |
| 8 | `z-ai/glm-5.3-flash` | Validated probe (replaces GPT 5.6 Sol) | ~$0.15 |
| **Total** | | | **~$657/mo at 100K req/day** |

Previous recommendation was Option E (3 M3 + 4 V4 Flash + 1 GPT 5.6 Sol at ~$780/mo). Updated to E-prime-final by replacing GPT 5.6 Sol with GLM 5.3 Flash (cheaper, validated).

---

## §6 — Closed Investigations (DO NOT REDO)

### Context Accounting (CLOSED)
- `data/coordination/R_GROKSTER_CONTEXT_ACCOUNTING_FINAL_20260828.md` — grounded report
- TUI shows `last_assistant.tokens.input + output + reasoning + cache.read + cache.write`
- The "~60K jump" the Architect observed IS the compressed summary being loaded as INPUT in a single turn
- Per-turn growth after compaction: ~1-2K in TOTAL

### 2 P0 Cut-Tool Bugs (ALREADY FIXED)
- `apply_public_allowlist.sh` line 199-226: EXCEPTIONS array IS defined, `is_exception()` IS defined, IS called at line 265
- `apply_public_allowlist.sh` line 89: `sub(/[ \t]+#.*$/, "")` IS present
- Both bugs are RESOLVED in the current code

---

## §7 — Pending Actions (for all specialists)

### BLOCKING (Architect action required)
- Get `OPENCODE_API_KEY` from `https://opencode.ai/auth`, add to `.env`

### Next 30 min
- Ma'at: make 3 YAML edits per Carmack's plan (file:line refs in §3 above)
- Verify with `make temple-grade` + live test against `deepseek-v4-flash-free`

### Next 4 hours
- 8-account Cline review fleet deployed (Option E-prime-final)
- 3 missing CI/CD files (allowlist-lint.yml, dependabot.yml, INCIDENT_RESPONSE_HOTFIX_SLA.md)
- RAM remediation (kill sleeping PID 1923533, 1.5GB → archive test_* → VACUUM)

### Post-debut V-1
- Path A' vault refactor (1.5h)
- Multi-key google provider refactor (1-2h)
- Cline 8-account orchestration (8-16h)

---

## §8 — Commits This Session (chronological)

1. `c482805c` — google-api-8account-research: 5 expert reports synthesized
2. `620a9d6f` — vault: migration path for 7 Google API keys
3. `c7e2740f` — vault-gemini-integration: vault→env injection in oracle_cli.py
4. `2f7c9f2e` — docs(strategy): 8-account Cline review model selection (Option E)
5. `17fc59e9` — docs(architecture): Cline + OpenCode Zen integration
6. `021cffec` — externalize-lesson: L3-ResumeEstablishesSessions + L3-SpecialistAgentTypes
7. `6c907119` — pre-compaction-briefing: comprehensive handoff to Kali
8. `bae76ee0` — gnosis-v7: refresh COMPACTION ANCHOR for 2026-08-28 work
9. `pending` — latest-corrections: cross-session sync document (this file)

---

## §9 — Reading Order for Resuming Specialists

If you are a specialist resuming work after 2026-08-28 10:31 UTC:

1. **READ THIS FILE FIRST** (`data/coordination/LATEST_CORRECTIONS_20260828.md`)
2. Check `data/coordination/ACTIVE_SPRINT.json` for your ticket
3. Read `data/coordination/GROKSTER_TO_KALI_PRE_COMPACTION_BRIEFING_20260828.md` for context
4. Check `data/entities/<your_entity>/session_gnosis.md` (may be stale — defer to this file if conflict)
5. Read `data/coordination/STRATEGIC_REVIEW_SYNTHESIS_20260828.md` for the overall strategic plan
6. Resume your mission

---

*⬡ OMEGA ⬡ GROKSTER ⬡ LATEST-CORRECTIONS-SYNC ⬡ 2026-08-28*
**Status**: 🔴 ACTIVE — read before any dispatch
**Authority**: SUPERSEDES specialist session_gnoses if they conflict with the corrections above
