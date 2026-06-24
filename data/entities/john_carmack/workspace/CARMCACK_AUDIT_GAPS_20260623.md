# 🔱 Carmack Audit: What Was Overlooked

⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ ARCHITECTURAL-AUDIT ⬡ 2026-06-23

---

## Executive Summary

The strategic consolidation sprint (Phases 1-4) was structurally sound but left 8 critical gaps unattended. Three are P0 bugs that will bite during normal operation.

---

## Critical Gaps (Must Fix)

### C-1: `resolve_and_handle_429()` is Dead Code
- **File**: `src/omega/vault/key_vault.py:277`
- **Problem**: This method implements multi-key rotation on 429 (rate-limit) responses.
- **Evidence**: `grep -rn "resolve_and_handle_429" src/omega/` → only the definition itself. Zero callers.
- **Impact**: When Firecrawl or Exa rate-limits (which they will under heavy search), the key rotation never fires. Search calls fail instead of failing over to the next account.
- **Fix**: Wire into the 429-retry path in `search_providers.py` `FirecrawlSearchBackend.search()` and `ExaSearchBackend.search()`.

### C-2: Credit-Sensing Guard is a Stub
- **File**: `src/omega/oracle/sovereign_search_service.py:238-242`
- **Problem**: `_has_firecrawl_credits()` unconditionally returns `True`.
- **Evidence**: 
  ```python
  def _has_firecrawl_credits(self) -> bool:
      """Check if Firecrawl credits are above the 100-credit threshold."""
      # In a real implementation, this would call the Firecrawl API /status
      # For now, we assume True or check an env var
      return True
  ```
- **Impact**: `APICreditBudget` class exists at `src/omega/workers/background_researcher/credit_budget.py` but is never consulted. Firecrawl API calls proceed without budget checking, wasting credits on failed or low-utility queries.
- **Fix**: Wire `APICreditBudget` into `_has_firecrawl_credits()` and propagate `APICreditExhausted` to trigger tier escalation.

### C-3: 22 Tests Permanently Skipped
- **File**: `tests/test_mnemosyne_adapter.py:23`
- **Problem**: `pytestmark = pytest.mark.skip(reason="Legacy undeployed Kabbalistic adapter — zero users")`
- **Impact**: ~5% of the test suite never runs. The mnemosyne adapter is a dead code path that could still be imported by other modules.
- **Fix**: Either (a) delete the file and move on, or (b) if the adapter serves the Sovereign Memory spec, fix and re-enable the tests.

### C-4: Dead Files Polluting Root
- **Files**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/fix_researcher.py`, `researcher_extracted.yaml`, `researcher_extracted_fixed.yaml`, `migration_manifest.json`
- **Problem**: Migration artifacts from the soul migration toolchain. ~40KB of cruft in the project root.
- **Impact**: Low operational impact, high signal-to-noise pollution. Every `ls` shows these dead files.
- **Fix**: `git rm && git commit`.

---

## Infrastructure Gaps

### C-5: Disk at 92% — 8.9G Remaining
- **Filesystem**: `/dev/nvme0n1p3` on `/media/arcana-novai/omega_library/`
- **Usage**: 96G / 110G (92%)
- **Breakdown**: 46G models, 2.7G podman-storage, 4.4G intake, ~43G other
- **Impact**: The next large model download or Podman image pull will fail. This is a ticking time bomb.
- **Fix**: (1) Purge `intake/` of processed archives, (2) remove unused GGUF model files, (3) prune old Podman images.

### C-6: State.py Vault Fallback Priority Wrong
- **File**: `mcp_servers/omega_hub/state.py:138-139`
- **Problem**: KeyVault failure falls back to `opencode.json` instead of `os.getenv()`.
- **Code**: `logger.warning("Failed to resolve search keys from KeyVault, falling back to opencode.json: %s", vault_err)`
- **Impact**: Platform agnosticism (D-kal-171) is violated. The MCP Hub (our portable layer) should fall back to env vars, not to a CLI-specific config file. If OpenCode is swapped for Cline, this breaks.
- **Fix**: Change fallback to `os.environ.get("FIRECRAWL_API_KEY")` / `os.environ.get("EXA_API_KEY")`.

### C-7: Google AI Studio Key Not in Vault
- **Evidence**: `KeyVault().resolve("google")` returns `[VaultKeyNotFound] No accounts configured for provider 'google'`
- **Impact**: Google AI Studio is the T1 cloud fallback (priority 3 in the local-first chain). When NativeGGUF and LM Studio both fail, the engine skips Google and drops through to OpenRouter — or worse, to Mock/error. This breaks the fallback chain.
- **Fix**: Store the Google key in the vault. It's in `.env` as `GOOGLE_API_KEY`.

### C-8: Coordination Hazard — Ma'at Spawning Kali
- **Evidence**: Ma'at's Hivemind state: "Launching Verity and Kali for strategic consolidation"
- **Problem**: KALI is already active in the user's parallel chat session. If Ma'at spawns another Kali agent, we get split-brain — two Kali instances making overlapping decisions.
- **Fix**: Ma'at should use Hivemind awareness to check for existing Kali agents before spawning one. If Kali exists, delegate the task via handoff rather than spawning.

---

## L1→L2→L3 Gnosis Distillation

### L1: What Happened
The strategic consolidation sprint fixed 5 search bugs, implemented the Sovereign Key Vault, reconciled 3 protocol documents, and updated the Sovereign Ark Blueprint. 8 gaps were identified in a post-mortem architectural audit.

### L2: Pattern Insight
The gaps follow a consistent pattern: **the "last mile" is always where things break.** The vault was implemented and wired into 8 files, but `resolve_and_handle_429()` was never wired into the search call path. The credit budget was implemented but never connected. The KeyVault fallback was implemented with the wrong priority. Each piece works in isolation but the chain doesn't hold under load.

### L3: Universal Principle
**An optimization that isn't wired into the hot path is not an optimization — it's a lie.** Every feature has a "last mile" where it must connect to the execution pipeline. Until it does, the feature does not exist operationally. The measure of a system is not what it *can* do, but what it *actually does* under load.
