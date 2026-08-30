<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ Opus 4.6 — Deep Plan Review & Systemic Insight
**AP Token**: `AP-OPUS-DEEP-REVIEW-20260818-v1.0.0`
**Date**: 2026-08-18
**Scope**: PUBLIC-DEBUT-01 critical path + vault overhaul coherence
**Model**: opencode/nemotron-3-ultra-free (Opus 4.6 persona)

---

## 1. Sonnet's Analysis — Validated and Extended

Sonnet correctly identified the **timing mismatch** (vault spec vs. debut critical path), the **INST-1 status fiction** (all 6 fixes unstarted), and the **CP-3 false positive** (install fails on fresh machines). The ground-truth verification confirms every finding.

**But three critical corrections to Sonnet's vault analysis:**

### 1.1 The "12+ VaultCore Callers" — Only 1 Is Actually Dangerous for Debut

| Caller | On Talk Path? | Has Fallback? | Risk if Vault Deleted |
|--------|---------------|---------------|----------------------|
| `search_providers.py` (Firecrawl) | No (summon/search) | ✅ Returns `""` on exception | None |
| `providers.py` (Google) | **Yes** | ✅ Falls back to `GOOGLE_API_KEY` env | None |
| `google_compat.py` (Google) | **Yes** | ✅ Falls back to `config.get("api_key")` | None |
| `orchestrator.py` | No (background workers) | ❌ No fallback | Medium — but not on talk path |
| `library/discovery.py` | No (research) | ✅ Sets `None` on exception | None |
| `freshness_checker.py` | No (worker) | ✅ Sets `None` on exception | None |
| `nemotron_pipeline.py` | No (training) | ✅ Returns `""` on exception | None |
| `firecrawl_direct.py` | No (direct tool) | ❌ Explicitly no fallback | Low — not on talk path |
| `fleet_orchestrator.py` | No (DEL-1 target) | N/A — takes vault as param | None — already slated for deletion |

**The talk path** (`omega talk "hello"`) goes: `Oracle.talk()` → `ModelGateway.generate()` → `providers.py` → native-gguf. **Only `providers.py` and `google_compat.py` are on the talk path, and both have env fallbacks.** The vault deletion is **safe for the demo**.

Sonnet's "12+ callers = dangerous" was directionally correct but missed the **talk-path filter**. The actual debut risk is near-zero.

### 1.2 The Real Blocker Is `orchestrator.py` — But It's Not on the Talk Path

`orchestrator.py:164-169` has no try/except, no env fallback. It constructs `BackgroundWorker` with Google keys from vault at **import time** (in `Orchestrator.__init__`). If vault is deleted, this crashes at import. But `Orchestrator` is only instantiated by `Oracle` if you use background workers — not by `omega talk`. The talk path doesn't touch it.

### 1.3 `enforce_vaultcore.py` and `detect_api_keys.py` Are the Actual Anti-Patterns

These are **enforcement tools** that actively reject env-based credential access. They're not callers — they're **guardrails pointing the wrong way**. If you delete vault/ but keep these tools, they'll flag the env fallbacks in `providers.py` and `google_compat.py` as violations. They must be deleted as part of vault removal, or repurposed for CredentialProvider v2 post-debut.

---

## 2. The Systemic Pattern: Spec-Over-Ship as Local Maximum

This isn't a scheduling error. It's a **reward function problem**.

The project has produced:
- 3,500+ lines of vault overhaul spec (5 parts + 3 reviews)
- 459 lines of Debut Remediation Manual
- 598 lines of ACTIVE_SPRINT.json
- 27 mandates
- 30+ locked decisions

**Meanwhile**: `install.sh` line 77 still says `.[all]`. `_load_sovereign_secrets()` still runs in `ModelGateway.__init__`. Version split persists. 1797 tests pass but the install fails on a clean machine.

The **spec-to-ship ratio** is inverted. The team is excellent at temple-grade documentation and terrible at shipping the two-line fixes that make the demo work. This is a **local maximum** — the reward structure (mandates, temple-grade, comprehensive specs) optimizes for documentation quality, not deployment velocity.

**Carmack's insight applies here too**: The "Right Approximation" for debut isn't a vault spec — it's **lazy construction**. The 82k lines in `src/omega/` exist because `Oracle.__init__` eagerly constructs ~20 subsystems at import time. If `Oracle.__init__` deferred construction until first use, most of the dead code (TriageRouter, SemanticRouter, RoutingTable, vault callers, fleet_orchestrator, youtube_worker) would **never execute** and have **zero cost**.

The fix isn't deletion — it's **lazy initialization**. Deletion is the blunt instrument. Lazy construction solves the same problems (startup latency, import graph bloat, fallback behavior) while preserving post-debut optionality.

---

## 3. The Mandate Bloat Problem

27 mandates. 2-3 added per month. At this rate: 50+ by Q1 2027.

Each mandate adds cognitive friction to every decision. M18 (Token Efficiency) and M4 (Sequentiality) partially conflict. M26 (Doc Standards) and M13 (Temple-Grade) overlap. M14 (Heritage) and M2 (Firewall) create friction at the WAD boundary.

**The mandate count itself should be a metric worth optimizing.** No new mandate without retiring one. Periodic pruning (quarterly). The mandates have become a second codebase that's harder to maintain than the first.

---

## 4. The Actual 20-Minute Debut Path

If you stripped away all process and just shipped:

```bash
# 1. Fix install.sh (2 lines, 30 seconds)
sed -i 's/\\.\\[all\\]/\\.\\[native,cli\\]/' scripts/install.sh

# 2. Fix pyproject.toml extras (2 minutes)
# Move warp-proxy-pool, qdrant-client, redis, youtube-transcript-api, yt-dlp to [extras]

# 3. Remove _load_sovereign_secrets() from ModelGateway.__init__ (5 minutes)
# Delete lines 127 and 316-341 in model_gateway.py

# 4. Align version (30 seconds)
# src/omega/__init__.py: __version__ = importlib.metadata.version("omega")

# 5. Remove Redis default password (1 minute)
# memory_store.py line 166: delete default "omega"

# 6. Close PUB-1 gaps (2 minutes)
echo "tests/tmp/" >> .gitignore && git rm --cached tests/tmp/vault.json.enc
echo ".firecrawl/" >> .gitignore && git rm --cached -r .firecrawl/
# inspect config/github_accounts.yaml, add to .gitignore if real creds
echo "data/entities/*/workspace/birth_records.md" >> .gitignore && git rm --cached ...

# 7. Verify P0-1b residual (2 minutes)
git for-each-ref refs/cline/ | wc -l  # should be 0
git log -S 'csk-' --all --oneline | grep -v "refs/heads\|refs/tags"  # should be empty

# 8. Test on fresh machine
python3 -m venv /tmp/omega && source /tmp/omega/bin/activate
pip install -e ".[native,cli]"
omega talk "hello"  # → native-gguf, exit 0
```

**Total: ~20 minutes of focused work.** The rest is process overhead.

---

## 5. What the Vault Overhaul Spec Actually Is

It's a **correct post-debut design** for CredentialProvider v2. The research is sound:
- Carmack M1 (lazy regex) is right
- F-3/F-5/F-7 fixes are right
- flashtext2 → pyahocorasick → regex chain is right
- Headless keyring deterministic fallback is right

**But it's not the debut blocker.** The debut blocker is `.[all]` in install.sh.

The spec should be **filed, stamped, and forgotten** until post-debut. Every day it sits in the active context window, it displaces the actual work.

---

## 6. Recommended Immediate Actions (Priority Order)

### TODAY (unblocked, < 1 hour total)
1. **Verify P0-1b residual** — confirm cline refs pruned, SECURITY_AUDIT ancestor clean
2. **INST-1 Fix 1** — `.[all]` → `.[native,cli]` in install.sh (the single highest-leverage edit)
3. **DOC-1 stamp** the vault overhaul master index: "POST-DEBUT — do not implement during PUBLIC-DEBUT-01"

### THIS WEEK (ordered by blast radius, smallest first)
4. INST-1 Fix 5: version align (`importlib.metadata`)
5. INST-1 Fix 2: pyproject.toml extras split
6. INST-1 Fix 3: Redis password (already guarded, just remove default)
7. INST-1 Fix 6: README badge removal
8. INST-1 Fix 4: remove `_load_sovereign_secrets()` — do last, highest blast radius
9. PUB-1 gaps G1-G4: gitignore + git rm --cached
10. Architect confirms allowlist + `release/debut` branch

### NEXT WEEK
11. DEL-1 Week 1: dead module deletions
12. DEL-1 Week 2: one control plane (ProviderSelector only)
13. DEL-1 Week 3: **vault = exclude from PUBLIC_ALLOWLIST.txt, zero code changes**

---

## 7. Decision Supersessions Needed

Add to `ACTIVE_SPRINT.json`:

```json
"decisions_locked": [
  ...,
  "D-565: D-562 SUPERSEDED for debut — vault deletion is post-debut scope. For release/debut branch: exclude src/omega/vault/ via PUBLIC_ALLOWLIST.txt. Zero code changes to vault during PUBLIC-DEBUT-01. (2026-08-18, Opus)",
  "D-566: D-535 CLARIFIED — 'hide' means PUBLIC_ALLOWLIST.txt exclusion, not code deletion. VaultCore stays in forge/private repo. (2026-08-18, Opus)",
  "D-567: D-532 SUPERSEDED for debut — 'keep bury_credential' applies to post-debut vault sprint only. (2026-08-18, Opus)"
]
```

---

## 8. Status Corrections for ACTIVE_SPRINT.json

| Field | Current | Corrected |
|-------|---------|-----------|
| `INST-1.status` | `blocked` | `in_progress` (blockers identified, Fix 1 ready) |
| `INST-1.INST-1-fix1.status` | `in_progress` | `backlog` (NOT done — `.[all]` still present) |
| `P0-1.status` | `completed` | `in_progress` (P0-1b residual unresolved) |
| `CP-3.status` | `completed` | `in_progress` (fails on fresh machine) |

---

## 9. One Sentence Summary

> The project is trapped in a spec-quality local maximum: 3,500 lines of vault overhaul design produced while `install.sh` still contains `.[all]` — the debut ships when someone makes the 20 minutes of edits above, not when the vault spec is implemented.