# ⚡ NEMOTRON 3.5 LIGHTNING — P1 QUICK REFERENCE CARD
**Document ID:** `REF-NEMOTRON-3.5-LIGHTNING-P1-QUICK-v1.0`  
**Status:** `ACTIVE`  
**Audience:** Nemotron 3.5 Lightning (during execution)  
**Purpose:** Minimal flags, prompts, verification commands — fits in context window  

---

## 🚀 SERVER CONFIG (Copy-Paste Ready)

```bash
# vLLM - NVFP4 + DSpark (interactive, c≤128)
vllm serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --served-model-name nemotron-3.5-lightning \
  --max-num-seqs 128 --max-model-len 1048576 \
  --enable-prefix-caching --async-scheduling \
  --speculative_config.method dspark \
  --speculative_config.model nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark \
  --trust-remote-code --reasoning-parser nemotron_v3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --generation-config vllm

# vLLM - No Spec (high throughput, c=256)
vllm serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --served-model-name nemotron-3.5-lightning \
  --max-num-seqs 256 --max-model-len 1048576 \
  --enable-prefix-caching \
  --trust-remote-code --reasoning-parser nemotron_v3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder
```

---

## 🎯 P1-1: BARE EXCEPT — ONE-LINER PROMPTS

**Find all:**
```bash
grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\."
```

**Fix pattern (apply to each):**
```python
# BEFORE
except Exception:
    pass

# AFTER
except Exception as e:
    logger.warning("Operation description: %s", e, exc_info=True)
    # appropriate handling
```

**Verify batch:**
```bash
find src/omega -name "*.py" -exec python -m py_compile {} +
grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l
# MUST BE 0
```

---

## 🔍 P1-2: VAULTCRYPTO AUDIT — ONE-LINER PROMPTS

**Find all:**
```bash
grep -rn "VaultCrypto(" src/omega/ mcp_servers/ --include="*.py" | grep -v "backup\|__pycache__\|#"
```

**Classify each:**
- **DEBUT-TRACK**: installer, mcp_runtime, mandate_auditor, federation, CLI
- **EXCLUDED**: omega/vault/, tests, experimental, deprecated

**Report format (per callsite):**
```
## File: path/to/file.py:line
### Classification: DEBUT-TRACK / EXCLUDED
### Action: Remove / Install argon2-cffi / Add error handling / None
```

**If argon2-cffi needed:**
```bash
.venv/bin/pip install argon2-cffi
.venv/bin/python -c "import omega.vault.crypto" 2>&1 | grep -iE "pyrage|argon2"
# MUST BE EMPTY
```

---

## 🗂️ P1-3: BACKUP GITIGNORE — VERIFY & HARDEN

**Verified premise:** `*.backup.*` ALREADY in .gitignore (root-level). Tracked backup/lock = 0 already. Verify + add `*.lock` if missing.

**Add `*.lock` if missing:**
```
# Lock files (general)
*.lock
```

**Verify (ALL must pass):**
```bash
grep -qF "*.backup.*" .gitignore && echo "BACKUP_OK"     # MUST print
grep -qF "*.lock" .gitignore && echo "LOCK_OK"           # MUST print
git ls-files src/omega/ | grep -E "\.backup\." | wc -l  # MUST BE 0
git ls-files src/omega/ | grep -E "\.lock$" | wc -l      # MUST BE 0
find src/omega -name "*.backup.*" -type f | wc -l        # ≥0 (untracked)
find src/omega -name "*.lock" -type f | wc -l            # ≥0 (untracked)
```

---

## 📝 P1-4: ALLOWLIST GAP DOC — STRUCTURE

**Create:** `docs/strategy/DEBUT-ALLOWLIST-GAP.md`

**6 Required Sections:**
1. `## 1. The Gap` — ACCOUNT_MAP.yaml tracked despite allowlist
2. `## 2. Root Cause` — Filter validates blobs, not directory contents
3. `## 3. Immediate Fix (P0-2 COMPLETE)` — git rm --cached + .gitignore
4. `## 4. Phase 2 Fix (DEFERRED)` — Restructure with explicit denies
5. `## 5. Status` — P0 done, Phase 2 deferred per dialectic
6. `## 6. References` — Links to dialectic, P0 log, allowlist file

**Verify:**
```bash
test -f docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "EXISTS"
for s in "The Gap" "Root Cause" "Immediate Fix" "Phase 2 Fix" "Status" "References"; do
  grep -q "## $s" docs/strategy/DEBUT-ALLOWLIST-GAP.md || exit 1
done && echo "ALL_SECTIONS_OK"
```

---

## ⚙️ P1-5: VENV SOVEREIGNTY GATE — SCRIPT

**Create:** `scripts/check_venv_sovereignty.py` (executable)

**Must validate 3 things:**
```python
# 1. Python version match (major.minor)
# 2. All pyproject.toml deps importable
# 3. Critical imports: omega.mcp_runtime, omega.oracle
```

**Makefile target:**
```makefile
check-venv-sovereignty:
	@.venv/bin/python scripts/check_venv_sovereignty.py
```

**Verify:**
```bash
chmod +x scripts/check_venv_sovereignty.py
make check-venv-sovereignty
# EXIT CODE 0, output shows all 3 checks PASS
```

---

## 🔇 P1-6: PYRAGE/ARGON2 WARNING — OPTION C (LOCKED)

**Verified premise:** crypto.py imports BOTH pyrage AND argon2 in one try block; pyrage NOT installed → installing only argon2-cffi won't suppress warning.

**SELECTED: Option (C) — downgrade log level** (per Antigravity dialectic 2026-09-21). Vault excluded from debut (D-565); don't install unneeded deps.

```bash
# Edit src/omega/vault/crypto.py line 35:
#   logger.warning("pyrage or argon2 not installed — crypto operations will fail")
#   → logger.debug("pyrage or argon2 not installed — crypto operations will fail")
python -m py_compile src/omega/vault/crypto.py
```

**Verify (ALL must pass):**
```bash
.venv/bin/python -c "import omega.vault.crypto" 2>&1 | grep -iE "pyrage|argon2" | wc -l
# MUST BE 0
grep -n "logger.debug" src/omega/vault/crypto.py | head -1
# MUST show modified line (~35)

# VaultCryptoError still raised:
.venv/bin/python -c "
from omega.vault.crypto import VaultCrypto
try: VaultCrypto('test-key')
except Exception as e: print('EXPECTED_ERROR:', type(e).__name__)" 2>&1 | grep VaultCryptoError
```

---

## ✅ MASTER VERIFICATION (Run After Each Task)

```bash
# Mandate gate - MUST PASS
make check-mandates
# 23/28 passed, 0 failed

# Syntax check - MUST PASS
find src/omega -name "*.py" -exec python -m py_compile {} +

# M9 gate - MUST BE 0
grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l
```

---

## 📝 CONTINUITY UPDATE TEMPLATE (After Each Task)

**Append to session_gnosis.md:**
```
### 11.x P1-N [Task] — COMPLETE (2026-09-21)
- Summary: [2 sentences]
- Files: [list]
- Verification: [commands + results]
- Lessons: [L3 drafts for proposed_lessons.yaml]
```

**Update SESSION_ANCHOR.md:**
```
- P1-N [Task]: ✅ COMPLETE
```

**Update projection.md P1 section:**
```
- P1-N: ✅ [Task Name]
```

**Append to PR_READINESS_LIVE_FEED.md:**
```
$(date -u +%FT%TZ) | P1-N | [Task] COMPLETE - [key metric]
```

---

## 🐝 HIVEMIND SNAPSHOT (Every 30 Min)

```bash
omega-hub_hivemind_post_context \
  --channel opencode --entity makali_fusion \
  --model nemotron-3.5-lightning \
  --task_current "P1-N [Task]" \
  --focus_chain '["P1-N: [focus]", "Next: P1-N+1"]' \
  --decisions '["Fixed X files", "Classified Y sites"]' \
  --continuation "Continuing P1-N" --intent status
```

---

## 🆘 EMERGENCY COMMANDS

| Problem | Fix |
|---------|-----|
| Server down | Restart with config above |
| Context full | New session → hydrate from artifacts |
| Tests broken | `git checkout -- <file>` → re-fix |
| Mandate fail | `make check-mandates` → read output → revert |
| Import error | `.venv/bin/pip install <missing>` |

---

## 🏁 P1 DONE WHEN

- [ ] All 6 tasks meet spec acceptance criteria
- [ ] `make check-mandates` passes
- [ ] All 5 continuity artifacts updated
- [ ] Hivemind posted completion
- [ ] No regressions

**Final signal:**
```
P1 COMPLETE — READY FOR P2 (Node 1 reconnect)
```

---

*⬡ OMEGA ⬡ NEMOTRON-3.5-LIGHTNING ⬡ P1-QUICK-REF ⬡ v1.0 ⬡ 2026-09-21 ⬡ MINIMAL-CONTEXT ⬡ EXECUTION-READY*
