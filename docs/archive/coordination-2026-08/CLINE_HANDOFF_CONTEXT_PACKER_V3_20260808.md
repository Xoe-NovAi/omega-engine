# 🔱 Cline CLI Handoff — Context Packer v3 Refactoring
**AP Token**: `AP-CLINE-HANDOFF-PACKER-V3-20260808`
**Date**: 2026-08-08
**From**: Kali (OpenCode) → Cline CLI
**Task**: Execute Context Packer v3 refactoring per Master Manual

---

## 🎯 Mission Summary

Replace the broken Context Packer v2 (9-phase pipeline with silent truncation bugs) with **Context Packer v3** — a deterministic 5-step fail-closed architecture using community libraries already installed in the venv.

**Implementation SSOT**: `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` (312 lines, v2.0.0)

**All knowledge gaps closed** — Researcher verified all 7 library APIs via live introspection.

---

## 📋 Current State

### ✅ Completed (Research Phase)
- Master Manual created (SSOT)
- Library API verification complete (`docs/research/R_CONTEXT_PACKER_V3_LIBRARY_APIS_20260808.md`)
- Codebase audit complete (Sonnet 4.6 + Nemotron 3 Ultra insights integrated)
- All corrections applied to manual

### 🔄 Ready to Execute
- Phase 0: Workspace lock
- Phase 1: Contract tests on fixtures
- Phase 0.5a: Quick hygiene
- Phase 2-5: Implementation

### 📁 Key Files

| File | Role | Status |
|------|------|--------|
| `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` | **SSOT — READ FIRST** | ✅ Complete |
| `.opencode/skills/context-packer/packer.py` | Target rewrite (1158 lines) | 🔄 v2 broken |
| `.opencode/skills/context-packer/packer-config.yaml` | Config SSOT (835 lines) | 🔄 Needs `tier:`, `tokenizer_encoding:` |
| `.opencode/skills/context-packer/pii_masker.py` | PII masking (468 lines) | ✅ Keep (API correct) |
| `src/omega/oracle/token_estimator.py` | **Create new** shared utility | 🔄 Not exists |
| `.opencode/skills/context-packer/platform_adapters.py` | Wire `litm_zone` → `priority` | 🔄 Needs mapping |
| `tests/contract/test_context_packer_v3.py` | **Create new** contract tests | 🔄 Not exists |

---

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)

| Mandate | Requirement |
|---------|-------------|
| **M1 AnyIO** | All async I/O via `anyio`; file-loop concurrency in `pack()` via `anyio.create_task_group()` |
| **M4 Sequentiality** | Plan → Verify → Execute. No cowboy coding. |
| **M7 Local-First** | Local inference PRIMARY. Cloud = FALLBACK. |
| **M13 Temple-Grade** | `make temple-grade` must pass T1-T11 after changes |
| **M14 Heritage** | `[id-soft:]` tags need vet record per `CREDITS.md` |
| **M22 Provenance** | `provider_name` from actual response, not config intent |
| **M23 Failure Integrity** | No soft-failures. Hard fail on validation. `[TOOL-CHAIN-COLLAPSE]` if mandatory tools broken |
| **M24 Venv Sovereignty** | All Python ops in `.venv`. Never `--break-system-packages` |
| **M25 Streaming Resilience** | Chunk timeout 30s, total timeout 5min, heartbeat on stall |

---

## 🚀 Execution Plan (from Manual)

### Phase 0 — Workspace Lock (Immediate)
```bash
# Acquire lock for context-packer domain
# Use Omega Hub MCP tools or create lock file manually
touch data/coordination/locks/context-packer.lock
echo "kali:$(date +%s):7200" > data/coordination/locks/context-packer.lock
```

### Phase 1 — Contract Tests (P0) — **START HERE**

Create `tests/contract/test_context_packer_v3.py`:

```python
"""Contract tests for Context Packer v3 — defines exact behavior."""
import pytest
from pathlib import Path

# These tests define the v3 contract. Implementation MUST pass all.

class TestResolvePhase:
    def test_gitignorespec_handles_recursive_globs(self):
        """GitIgnoreSpec.from_lines() handles ** and negation !"""
        pass
    
    def test_gitignorespec_negation_patterns(self):
        """! patterns correctly exclude files from ** matches"""
        pass

class TestCountPhase:
    def test_shared_token_estimator(self):
        """Single TokenEstimator used by curator + packer"""
        pass
    
    def test_platform_specific_encoding(self):
        """cl100k_base (Claude) vs o200k_base (Grok/Gemini)"""
        pass
    
    def test_token_margin_multiplier_from_config(self):
        """PlatformConfig.token_margin_multiplier applied"""
        pass

class TestValidatePhase:
    def test_fail_closed_budget_exceeded(self):
        """Budget exceeded → [PACK-FAIL] + top 3 offending files"""
        pass
    
    def test_fail_closed_required_theme_missing(self):
        """Required theme absent → [PACK-FAIL] with theme name"""
        pass

class TestOrderPhase:
    def test_litm_zone_priority_mapping(self):
        """litm_zone → priority: start=3, middle=2, end=1"""
        pass

class TestWritePhase:
    def test_pii_vault_encapsulation(self):
        """pii_vault.json written to context_packs/<profile>/"""
        pass
    
    def test_defusedxml_parse_only(self):
        """XML parsing uses defusedxml, creation uses stdlib Element"""
        pass
    
    def test_ed25519_signature(self):
        """Manifest signed, public key in PEM format"""
        pass
```

**Run**: `source .venv/bin/activate && pytest tests/contract/test_context_packer_v3.py -v`

### Phase 0.5a — Quick Hygiene (Parallel)

1. **Add `tier:` and `tokenizer_encoding:` to all 15 profiles** in `packer-config.yaml`:
   ```yaml
   profiles:
     sovereign-audit:
       tier: ship                    # NEW
       tokenizer_encoding: "cl100k_base"  # NEW
       token_margin_multiplier: 1.3
       # ... existing fields
   ```

2. **Fix 16 ghost references** to `enhanced_packer.py` in config

3. **Remove hardcoded constants** from `packer.py:132-133`:
   ```python
   # DELETE THESE:
   MAX_BUNDLE_TOKENS = 15000
   MAX_TOTAL_TOKENS = 120000
   ```

### Phase 2 — Curator CLI (`curate_packs.py`)

Create `.opencode/skills/context-packer/curate_packs.py`:

```python
#!/usr/bin/env python3
"""Context Packer v3 Curator — Config-driven validation & lock generation."""
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
import yaml

app = typer.Typer(
    no_args_is_help=True,
    help="Context Packer v3 Curator — Validate packs, generate locks",
    rich_markup=True,
)

@app.command()
def curate(
    profile: str = typer.Argument(..., help="Profile name from packer-config.yaml"),
    config: Path = typer.Option(Path("packer-config.yaml"), "--config", "-c", exists=True),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Validate without writing"),
    write_lock: bool = typer.Option(False, "--write-lock", help="Write theme_lock.json with SHA256"),
):
    """Validate a profile's pack against budgets and optionally write lock file."""
    # 1. Load config
    # 2. Resolve files using GitIgnoreSpec
    # 3. Count tokens using shared TokenEstimator
    # 4. Validate (fail-closed with diagnostics)
    # 5. Print rich.Table diagnostic
    # 6. If write_lock: write theme_lock.json with SHA256
    pass

@app.command()
def list_profiles(
    config: Path = typer.Option(Path("packer-config.yaml"), "--config", "-c"),
):
    """List all available profiles from config."""
    pass

if __name__ == "__main__":
    app()
```

**Diagnostic Table Format**:
```
Theme | Files | Tokens | Budget | Headroom | Required | Status
mandates | 3 | 5560 | 15000 | 9440 | yes | [green]OK[/green]
oracle_core | 6 | 16200 | 15000 | -1200 | yes | [red]OVER[/red]
```

### Phase 3 — Packer Core Rewrite

Replace 9-phase v2 pipeline in `packer.py` with 5-step v3:

```python
# 1. RESOLVE — GitIgnoreSpec
from pathspec import GitIgnoreSpec
spec = GitIgnoreSpec.from_lines(include_patterns + exclude_patterns)
matched = [f for f in walk_all_files() if spec.match_file(f)]

# 2. COUNT — Shared TokenEstimator
from src.omega.oracle.token_estimator import estimate_tokens
tokens = estimate_tokens(content, encoding_name=profile.tokenizer_encoding)
tokens = int(tokens * profile.token_margin_multiplier)

# 3. VALIDATE — Fail-closed
if theme_tokens > theme_budget:
    raise PackFail(f"[PACK-FAIL] Theme '{theme}' exceeds budget: {theme_tokens}/{theme_budget}. Top files: {top_3_files}")

# 4. ORDER — litm_zone → priority
LITM_ZONE_PRIORITY = {"start": 3, "middle": 2, "end": 1}
bundle["priority"] = LITM_ZONE_PRIORITY.get(bundle.get("litm_zone", "middle"), 2)

# 5. WRITE — Per-profile artifacts
# - PII masking (file-loop AnyIO)
# - XML escape before CDATA
# - Ed25519 signature
# - Write to context_packs/<profile>/
```

### Phase 4 — Shared TokenEstimator (Create New)

Create `src/omega/oracle/token_estimator.py`:

```python
"""Shared token estimator — single source of truth for curator + packer."""
import tiktoken
from functools import lru_cache

@lru_cache(maxsize=8)
def _get_encoding(name: str):
    return tiktoken.get_encoding(name)

def estimate_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Estimate tokens using tiktoken. Single shared implementation."""
    if not text:
        return 0
    enc = _get_encoding(encoding_name)
    return len(enc.encode(text))

def estimate_tokens_with_margin(text: str, encoding_name: str, margin_multiplier: float) -> int:
    """Estimate tokens with platform-specific margin applied."""
    return int(estimate_tokens(text, encoding_name) * margin_multiplier)
```

**Replace all three existing estimators**:
- `packer.py:254` `_estimate_token_count` → use shared
- `src/omega/oracle/context_builder.py:527` `_estimate_tokens` → use shared
- `src/omega/training/rewards.py:134` `estimate_tokens` → use shared

### Phase 5 — Integration & Verification

```bash
# 1. Run contract tests
source .venv/bin/activate && pytest tests/contract/test_context_packer_v3.py -v

# 2. Run integration test
python -m .opencode.skills.context-packer.curate_packs sovereign-audit --dry-run

# 3. Full pack
python -m .opencode.skills.context-packer.packer sovereign-audit

# 4. Temple-Grade
make temple-grade

# 5. Full test suite
make test
```

---

## 🔑 Critical Corrections (from Sonnet 4.6 + Nemotron Audits)

| Issue | Correction | Location |
|-------|------------|----------|
| `pathspec` deprecated `gitwildmatch` | Use `GitIgnoreSpec.from_lines(patterns)` | Manual §1.2, §1.3, §1.7.5 |
| `defusedxml` NOT drop-in | Parse with `defusedxml`, create with stdlib `Element`/`SubElement` | Manual §1.2, §1.3, §5 |
| PII vault global dir | Move to `context_packs/<profile>/pii_vault.json` | Manual §1.7, §6 |
| 3 different token estimators | Single shared `TokenEstimator` utility | Manual §1.5, §1.7.6 |
| `litm_zone` not mapped | Explicit mapping: `start=3, middle=2, end=1` | Manual §1.6, §4 |
| No diagnostic on fail | Print top 3 offending files | Manual §1.3 Insight #1 |
| `_prune_content` on code files | Only for `.md/.txt/.yaml` | Nemotron insight |
| No change detection | SHA256 in `theme_lock.json` | Nemotron insight |

---

## 📦 Per-Profile Artifact Layout

```
context_packs/
└── sovereign-audit/
    ├── manifest.xml          # Signed manifest
    ├── pack_index.json       # Per-profile index
    ├── pii_vault.json        # Reversible token map (gitignored)
    ├── theme_lock.json       # Explicit file list + SHA256
    └── generated/
        ├── mandates.xml
        ├── oracle_core.xml
        └── ...
```

**`pack_index.json` schema**:
```json
{
  "profile": "sovereign-audit",
  "timestamp": "2026-08-08T18:00:00Z",
  "bundles": [
    {"theme": "mandates", "file": "mandates.xml", "tokens": 5560, "litm_zone": "start", "required": true},
    {"theme": "oracle_core", "file": "oracle_core.xml", "tokens": 12000, "litm_zone": "middle", "required": true}
  ],
  "pii_vault": "pii_vault.json",
  "signature": "ed25519:...",
  "public_key": "-----BEGIN PUBLIC KEY-----\n..."
}
```

---

## ✅ Definition of Done (13 Criteria)

### P0 (Blocking)
- [ ] All contract tests pass (`pytest tests/contract/test_context_packer_v3.py -v`)
- [ ] `curate_packs.py` validates budgets, prints diagnostic table, writes `theme_lock.json` with SHA256
- [ ] `packer.py` executes 5-step pipeline, writes per-profile artifacts
- [ ] PII vault in `context_packs/<profile>/` (not global), excluded from git
- [ ] `tokenizer_encoding` + `token_margin_multiplier` in `PlatformConfig`, used by shared `TokenEstimator`
- [ ] `litm_zone` → `priority` mapping wired for platform adapters
- [ ] `make temple-grade` passes T1-T11
- [ ] `make test` passes (no new failures)

### P1 (Required)
- [ ] `tier:` field on all 15 profiles in `packer-config.yaml`
- [ ] 16 ghost `enhanced_packer.py` references removed
- [ ] `MAX_BUNDLE_TOKENS`/`MAX_TOTAL_TOKENS` constants deleted
- [ ] `context_packs/*/pii_vault.json` in `.gitignore`
- [ ] `theme_lock.json` includes SHA256 for change detection
- [ ] Injection scanner hardened: required-theme → `[PACK-FAIL]`
- [ ] `_prune_content` only processes `.md/.txt/.yaml`

---

## 🐝 Hivemind Coordination

If working in parallel with other agents:
1. Check awareness: `omega-hub_hivemind_get_awareness()`
2. Post context: `omega-hub_hivemind_post_context(...)` with intent="command"
3. Heartbeat every 5-10 min: `omega-hub_hivemind_heartbeat(channel="cline", entity="kali")`

---

## 🔍 Verification Commands

```bash
# Verify no deprecated patterns
grep -r "gitwildmatch" .opencode/skills/context-packer/  # Should be 0

# Verify defusedxml usage
grep -n "defusedxml" .opencode/skills/context-packer/packer.py
# Should show: from defusedxml import ElementTree as DET (parse only)
# Should NOT show: DET.Element or DET.SubElement

# Verify PII vault location
grep -n "pii_vault" .opencode/skills/context-packer/packer.py
# Should write to: context_packs/<profile>/pii_vault.json

# Verify shared estimator
grep -rn "estimate_tokens" src/omega/oracle/ | grep -v "token_estimator.py"
# Should be 0 (all use shared utility)

# Verify litm_zone mapping
grep -n "litm_zone" .opencode/skills/context-packer/packer.py
# Should show explicit mapping dict

# Run tests
source .venv/bin/activate && pytest tests/contract/test_context_packer_v3.py -v

# Temple-Grade
make temple-grade
```

---

## 📚 Reference Documents

| Document | Purpose |
|----------|---------|
| `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` | **Primary SSOT** |
| `docs/research/R_CONTEXT_PACKER_V3_LIBRARY_APIS_20260808.md` | Library API signatures |
| `docs/research/R_CONTEXT_PACKER_V3_RESEARCH_SYNTHESIS_20260808.md` | Research synthesis |
| `SOVEREIGN_MANDATES.md` | 25 Non-negotiable laws |
| `AGENTS.md` | OpenCode workflow (for reference) |
| `CREDITS.md` | Heritage registry |

---

## ⚠️ Known Issues (Pre-Existing, Not Blocking)

- ~94 test failures in baseline (vault pydantic, call_with_retry, cascade_router, world_state) — **do not fix in this sprint**
- Stale `__pycache__` may contain old strings — clear before greps: `find src -name __pycache__ -type d -exec rm -rf {} +`

---

## 🧠 Gemini's Strategic Insights & Corrections (READ CAREFULLY)

Before you begin, I have reviewed this handoff and identified a few critical edge cases and path corrections you must be aware of:

1. **Path Correction**: `platform_adapters.py` lives in `.opencode/skills/context-packer/`, NOT `src/omega/oracle/`. The `PlatformConfig` class is defined there.
2. **AnyIO CPU-Bound Blocking (M1 Violation Risk)**: When you implement the file-loop concurrency using `anyio.create_task_group()`, remember that `tiktoken` encoding and `pii-shield` scanning are **CPU-bound**. You MUST wrap them in `anyio.to_thread.run_sync()` inside your async tasks, or you will block the event loop and violate Mandate 1.
3. **Pathspec POSIX Requirement**: `GitIgnoreSpec.match_file()` expects POSIX-style paths (forward slashes). When walking the filesystem, ensure you pass `path.as_posix()` to the matcher, not raw Windows paths (if cross-platform compatibility is tested).
4. **Typer CLI Testing**: To test `curate_packs.py` in your contract tests, use `from typer.testing import CliRunner`.
5. **XML Creation vs Parsing**: `defusedxml` is ONLY for parsing (e.g., verifying a manifest). When *generating* the XML bundles and manifest, use the standard library: `from xml.etree.ElementTree import Element, SubElement, tostring`.
6. **`theme_lock.json` Schema**: Keep it simple. It should map the theme name to a list of file objects containing the path, token count, and SHA256 hash. Example: `{"theme_name": [{"file": "path/to/file.py", "tokens": 150, "sha256": "..."}]}`.

---

## 🎯 First Action for Cline CLI

```bash
# 1. Read the SSOT
cat docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md

# 2. Acquire workspace lock
touch data/coordination/locks/context-packer.lock
echo "cline:$(date +%s):7200" > data/coordination/locks/context-packer.lock

# 3. Create contract tests (Phase 1)
# Edit tests/contract/test_context_packer_v3.py

# 4. Run tests to see failures (TDD)
source .venv/bin/activate && pytest tests/contract/test_context_packer_v3.py -v

# 5. Implement to make tests pass
```

---

## 📞 Escalation

If blocked on:
- **Library API uncertainty** → Check `docs/research/R_CONTEXT_PACKER_V3_LIBRARY_APIS_20260808.md`
- **Mandate interpretation** → Check `SOVEREIGN_MANDATES.md`
- **Architecture decision** → Check `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` §1.3, §1.4
- **Tool chain failure** → Report `[TOOL-CHAIN-COLLAPSE]` per M23

---

*⬡ OMEGA ⬡ KALI → CLINE ⬡ PACKER-V3-REFACTOR ⬡ 2026-08-08*

**The manual is the contract. The tests are the specification. The implementation is the fulfillment.**