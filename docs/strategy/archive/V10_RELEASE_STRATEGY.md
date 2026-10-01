# 🔱 Omega Engine v1.0.0 — Father's Day Release Strategy
# ⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_v1_strategy_final
**AP Token**: AP-V1-RELEASE-STRATEGY-v1.0.0
**Date**: 2026-06-21 (Father's Day)
**Status**: ✅ PLAN MODE — Finalized by Ma'at, ready for MaKaLi execution
**Baseline**: 423 tests passing · 22 Sovereign Mandates · 98 source files

---

## §0 Executive Summary

**Version**: v1.0.0 — First unified public release. Clean break from legacy.

**Target**: A working, presentable, sovereign AI runtime that anyone can install on Linux and get running with zero cloud dependencies.

**Value Proposition**: `git clone → make setup → make model-download → omega talk "hello"` — 4 commands, fully local, zero telemetry, no cloud signup.

**Key Messaging**: *Local-first by default. Cloud is a config option, not a requirement.*

---

## §1 Critical Blockers & Enhancements (Ma'at Build Audit)

During the final structural audit, the following critical packaging, configuration, and portability blockers were identified and must be resolved during execution:

1. **`omega` CLI entry point is broken** — `[project.scripts]` is missing from `pyproject.toml`. After `pip install -e .`, the command `omega` does not exist on PATH. Quick Start fails at step 4.
2. **`make setup` fails** — References `.[cli,nova,dev]` but `nova` is not defined as an optional dependency in `pyproject.toml`. Nova is a WAD-layer component (lives in `src/omega/nova/` as part of the Arcana-NovAi WAD) and must be excluded from core engine dependencies.
3. **No model download script** — `scripts/download_model.sh` does not exist. `make model-download` and `make model-list` targets are not defined in the Makefile.
4. **README is cloud-first** — Quick Start shows `export OPENROUTER_API_KEY` as step 2. Violates M7 (Local-First). Shows 259 tests (actual: 423). Shows v0.5.0-alpha (should be v1.0.0). Shows Native GGUF as "Deferred to v0.6.0" (it IS the primary provider).
5. **Hardcoded Path Bug in `config/omega.yaml` (M16 Violation)** — Line 17 hardcodes `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data` as the data directory. This will crash the engine on any other machine. Must be resolved to relative path `data`.
6. **Version mismatch** — `pyproject.toml` says `2.3.0`, `Makefile` says `v2.2.0`, `README` says `v0.5.0-alpha`. Must unify to `1.0.0`.

---

## §2 The Provider Chain — Local-First Default

The `config/providers.yaml` priority must be accurately reflected in ALL documentation:

| Priority | Provider | Type | Default | Status |
|----------|----------|------|---------|--------|
| 0 | **native-gguf** (llama-cpp-python) | Local | **ON** — primary | Must be `[native]` extra |
| 1 | **lmster** (LM Studio :1234) | Local | **ON** — fallback | Already configured |
| 2 | **Ollama** (:11434) | Local | **ON** — fallback | Already configured |
| 3 | **Google AI Studio** | Cloud | **OFF** — opt-in only | Requires API key |
| 4 | **OpenRouter** | Cloud | **OFF** — opt-in only | Requires API key |
| 5 | **OpenCode** | Cloud | **OFF** — opt-in only | Requires OAuth |
| 6 | **Copilot** | Cloud | **OFF** — opt-in only | Requires subscription |
| 7 | **Mock** | Test | **OFF** | Dev/test only |

**Rule**: Cloud providers NEVER appear in the Quick Start. They are documented in a separate "Advanced: Cloud Fallbacks" section at the bottom of the README.

---

## §3 Release Phases — Execution Plan for MaKaLi

### Phase 1: Packaging & Dependency Hardening (Owner: Ma'at/P3)

**Objective**: Make `pip install -e .` install a working engine with a functional `omega` CLI command.

| # | Task | File | Change | Est. Time |
|---|------|------|--------|-----------|
| **1.1** | **ADD CLI ENTRY POINT** (BLOCKER) | `pyproject.toml` | Add `[project.scripts]` section: `omega = "omega.cli.oracle_cli:main"`. Without this, `omega talk "hello"` fails with `command not found`. | 5 min |
| **1.2** | Add core dependencies | `pyproject.toml` | Add `[project.dependencies]` with all 18+ runtime deps: anyio, pydantic, PyYAML, typer, python-dotenv, fastapi, uvicorn, httpx, click, rich, mcp, aiosqlite, tenacity, sse-starlette, starlette, APScheduler, jsonschema, cryptography, PyJWT | 10 min |
| **1.3** | Add optional extras | `pyproject.toml` | `[project.optional-dependencies]`: `native = ["llama-cpp-python>=0.3.0,<0.4.0"]`, `cli = ["typer[full]", "rich", "shellingham"]`, `dev = ["pytest>=9", "pytest-asyncio", "pytest-cov", "flake8"]`, `all = ["omega[native,cli]"]`. **DO NOT define `nova` — it is WAD-layer infrastructure, not a Python extra.** | 10 min |
| **1.4** | **FIX `make setup`** (BLOCKER) | `Makefile:282` | Change `pip install -e ".[cli,nova,dev]"` to `pip install -e ".[all]"`. `nova` is not a valid extra — it is a Podman container. | 2 min |
| **1.5** | Update `make demo` | `Makefile:290-294` | Remove `PYTHONPATH=src` prefix. After entry point is added, `omega list-entities` works directly. | 2 min |
| **1.6** | Update version in all files | `pyproject.toml`, `config/omega.yaml`, `Makefile`, `README.md` | Unify all to `1.0.0`. | 5 min |
| **1.7** | Add `[tool.pytest.ini_options]` | `pyproject.toml` | Add `testpaths = ["tests"]` and `ignore` for odysseus-dev and data dirs. Without this, pytest walks the entire tree including odysseus-dev (1605 files). | 2 min |
| **1.8** | Add `[project.urls]` | `pyproject.toml` | `Homepage = "https://github.com/Xoe-NovAi/omega-engine"`, `Repository = "https://github.com/Xoe-NovAi/omega-engine"`, `Issues = "https://github.com/Xoe-NovAi/omega-engine/issues"` | 2 min |
| **1.9** | Verify `pip install -e ".[all]"` works | — | Run `pip install -e ".[all]"` in clean venv and verify `omega --help` works | 5 min |
| 1.10 | Merge `requirements.txt` into `pyproject.toml` | `pyproject.toml` | Pin exact versions from requirements.txt. Keep requirements.txt for CI reproducibility. | 10 min |

**Total**: ~55 min

---

### Phase 2: Model Download & Config Portability (Owner: Ma'at/P1)

**Objective**: Enable `make model-download` to fetch a Qwen 1.7B GGUF model and ensure configuration portability.

| # | Task | File | Change | Est. Time |
|---|------|------|--------|-----------|
| 2.1 | Create download script | `scripts/download_model.sh` | Download `qwen3-1.7b-q6_k` GGUF from Hugging Face (`Qwen/Qwen3-1.7B-GGUF`) using `wget` or `curl` (dynamically detect whichever is available). Place in `models/gguf/`. Verify sha256 after download. Include retry logic (3 attempts), progress bar, disk space check, and clean error reporting. | 20 min |
| 2.2 | Add Makefile targets | `Makefile` | `model-download: ## 📥 Download local model (Qwen 1.7B GGUF, ~1GB)` and `model-list: ## 📋 List downloaded models` with `ls -lh models/gguf/*.gguf 2>/dev/null`. Also add `model-clean: ## 🧹 Delete downloaded models` to safely reclaim space. | 5 min |
| 2.3 | **FIX CONFIG PATH** (BLOCKER) | `config/omega.yaml:17` | Change hardcoded absolute path `/home/arcana-novai/...` to relative path `data` to ensure portability (Mandate 16). | 2 min |
| 2.4 | Add `models/` to `.gitignore` | `.gitignore` | Add `models/` after `# ── Build Artifacts` section. Models are downloaded, not source code. | 1 min |
| 2.5 | Add `odysseus-dev/` to `.gitignore` | `.gitignore` | Add `data/entities/roc_racoon/workspace/odysseus-dev/` to prevent git tracking. | 1 min |
| 2.6 | Update default config path | `config/providers.yaml` | Add comment: `# Default model path: models/gguf/ (created by make model-download)` | 2 min |
| 2.7 | Create `models/` directory with `.gitkeep` | `models/gguf/.gitkeep` | Ensures directory exists after clone but is empty. | 1 min |

**Total**: ~32 min

---

### Phase 3: README Overhaul — Local-First Default (Owner: Lilith/P7)

**Objective**: First impression communicates sovereignty immediately.

**Current README problems** (all must be fixed):
- Line 14: "Quick Start — 3 Commands" → should be 4 (with model-download)
- Line 20: `pip install -e .` → should be `make setup`
- Lines 23-25: Shows `export OPENROUTER_API_KEY` as step 2 → cloud-first, M7 violation
- Line 31: Shows OpenRouter → Ollama → LM Studio → Mock → must be native-gguf first
- Line 73: Native GGUF shows "pip install llama-cpp-python" → should be auto-installed by `make setup`
- Line 121: Shows "v0.5.0-alpha" → must be v1.0.0
- Line 129: Shows "259 tests" → must be 423
- Line 131: Shows "Native GGUF — Deferred to v0.6.0" → it IS the primary provider

**Target README Quick Start**:
```markdown
## Quick Start — 4 Commands

\```bash
# 1. Clone and install
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
make setup                    # Python venv + all dependencies (includes llama-cpp-python)

# 2. Download the local model (Qwen 1.7B, ~1GB)
make model-download

# 3. Talk to it — runs entirely on your CPU, no cloud keys needed
omega talk "hello"
\```

That's it. Your first sovereign AI interaction.
```

| # | Task | Change | Est. Time |
|---|------|--------|-----------|
| 3.1 | Rewrite Quick Start | Flip to local-first. Remove OpenRouter from step 2. Add `make model-download` as step 2. | 10 min |
| 3.2 | Rewrite Provider Setup table | Local providers FIRST. Native GGUF is #1. Cloud = "Advanced" section at bottom. | 10 min |
| 3.3 | Update Architecture diagram | Show native-gguf as first in fallback chain, not OpenRouter. | 5 min |
| 3.4 | Update version/status section | v0.5.0-alpha → v1.0.0. 259 tests → 423. Native GGUF "Deferred" → "✅ Production-ready". | 5 min |
| 3.5 | Remove stale alpha badges | PIVOT badge, Firewall badge. Update Python badge to 3.12+. | 5 min |
| 3.6 | Add "Advanced: Cloud Fallbacks" section | OpenRouter, Google AI Studio, LM Studio (cloud), Copilot — each with setup instructions. Add ToS warning for Antigravity. | 10 min |
| 3.7 | Add "System Requirements" update | Python 3.12+ (not 3.13+). Add note about C compiler for llama-cpp-python. | 3 min |
| 3.8 | Add "Contributing" section | Link to CONTRIBUTING.md (create if missing). Link to Issues. | 3 min |

**Total**: ~50 min

---

### Phase 4: Test Suite Cleanup (Owner: Verity/P10)

**Objective**: `make test` passes clean with 0 unexpected failures.

**Current state**: 423 collected, 6 failed, 22 Mnemosyne errors (legacy adapter)

| # | Task | File | Change | Est. Time |
|---|------|------|--------|-----------|
| 4.1 | Exclude odysseus-dev from pytest | `pyproject.toml` `[tool.pytest.ini_options]` | `ignore = ["data/entities/roc_racoon/workspace/odysseus-dev", "data/entities/roc_racoon/workspace/mining_reports"]` | 2 min |
| 4.2 | Mark Mnemosyne tests xfail | `tests/test_mnemosyne_adapter.py` | Add `@pytest.mark.xfail(reason="Legacy undeployed Kabbalistic adapter")` at class level. These 22 errors are from an undeployed system. | 2 min |
| 4.3 | Fix `test_bug_001_fix.py` | `tests/test_bug_001_fix.py` | Fix async fixture — likely missing `@pytest.mark.asyncio` or incorrect test function signature. | 10 min |
| 4.4 | Fix MCP client contract tests (3) | `tests/test_mcp_client.py` | These require a running MCP hub server (port 8016). Mark as `xfail` with reason "requires running MCP hub server" — integration test, not unit test. | 5 min |
| 4.5 | Fix memory adapter tests (2) | `tests/test_memory_adapters.py` | Interface mismatch — read the actual test code, identify whether the interface changed or the test is stale. Fix or xfail. | 10 min |
| 4.6 | Update CI stale comment | `.github/workflows/test.yml:6` | Remove `Native GGUF (llama-cpp-python) is NOT installed — deferred to v0.6.0`. Replace with `# Tests use MockProvider — no live inference needed`. | 1 min |
| 4.7 | Run `make test` and verify | — | All 423+ tests pass, 0 unexpected failures, 0 collection errors | 10 min |

**Total**: ~40 min

---

### Phase 5: Restore OpenCode OAuth Provider (Owner: Lilith/P4)

**Objective**: Enable Antigravity OAuth fallback in OpenCode CLI for cloud model access.

**Background**: The `opencode-antigravity-auth` plugin is a git submodule at `opencode-antigravity-auth/`. The `plugin` key and `provider.google` model definitions were never added to the repo-level `opencode.json`. The user-level `~/.config/opencode/opencode.json` also lacks these sections.

| # | Task | File | Change | Est. Time |
|---|------|------|--------|-----------|
| 5.1 | Add `plugin` reference | `opencode.json` | `"plugin": ["opencode-antigravity-auth@latest"]` | 2 min |
| 5.2 | Add Google provider with model definitions | `opencode.json` | Add `"provider": { "google": { "models": { ... } } }` with all Antigravity + Gemini CLI models from the plugin README | 15 min |
| 5.3 | Initialize git submodule | `git submodule update --init` | Ensure `opencode-antigravity-auth/` is populated | 5 min |
| 5.4 | Add OAuth login instructions to README | `README.md` | In "Advanced: Cloud Fallbacks" section, add note about `opencode auth login`. Include ToS warning. | 5 min |
| 5.5 | Test end-to-end | CLI | `opencode run "hello" --model=google/antigravity-gemini-3-flash --variant=low` | 10 min |

**Model definitions to add** (from `opencode-antigravity-auth/README.md §Models`):
- `antigravity-gemini-3-pro` (context: 1048576, output: 65535)
- `antigravity-gemini-3.1-pro` (context: 1048576, output: 65535)
- `antigravity-gemini-3-flash` (context: 1048576, output: 65536)
- `antigravity-claude-sonnet-4-6` (context: 200000, output: 64000)
- `antigravity-claude-opus-4-6-thinking` (context: 200000, output: 64000)
- `gemini-2.5-flash` (context: 1048576, output: 65536)
- `gemini-2.5-pro` (context: 1048576, output: 65536)
- `gemini-3-flash-preview` (context: 1048576, output: 65536)
- `gemini-3-pro-preview` (context: 1048576, output: 65535)

**Note**: These are FALLBACK providers for when no local model is available. They must NOT appear in the Quick Start.

**Total**: ~35 min

---

### Phase 6: Git Hygiene & Release (Owner: Ma'at/P3 + Kali)

**Objective**: Clean history, correct version, tagged release.

| # | Task | Action | Est. Time |
|---|------|--------|-----------|
| 6.1 | Add `models/` to `.gitignore` | Done in Phase 2.4. Verify. | 1 min |
| 6.2 | Add `odysseus-dev/` to `.gitignore` | Done in Phase 2.5. Verify. | 1 min |
| 6.3 | Review all modified files | Ensure no secrets, no stale data, no orphan artifacts. Check: `opencode.json` for API keys, `config/` for hardcoded paths, `data/` for runtime data. | 10 min |
| 6.4 | Commit Phase 1-2 | `feat(packaging): v1.0.0 dependency hardening + model download` | 2 min |
| 6.5 | Commit Phase 3 | `docs: README v1.0.0 local-first overhaul` | 2 min |
| 6.6 | Commit Phase 4 | `test: cleanup test suite for v1.0.0 release` | 2 min |
| 6.7 | Commit Phase 5 | `feat(opencode): restore Antigravity OAuth provider` | 2 min |
| 6.8 | Tag release | `git tag -a v1.0.0 -m "Omega Engine v1.0.0 — Father's Day Release"` | 2 min |
| 6.9 | Push to GitHub | `git push origin main --tags` | 2 min |

**Total**: ~25 min

---

## §4 Implementation Order — Dependencies

```
Phase 1 (Packaging) ───── Must be first: everything depends on it
     │                     └── BLOCKERS: entry_point + deps + extras
     ▼
Phase 2 (Model DL) ────── Can start after Phase 1. Independent of Phase 3-5
     │                     └── Creates download script + Makefile targets
     ▼
Phase 3 (README) ──────── Can start after Phase 1. Independent of Phase 2, 4, 5
     │                     └── Depends on Phase 1 version being correct
     ▼
Phase 4 (Tests) ───────── Can start after Phase 1. Independent of Phase 2, 3, 5
     │                     └── Depends on Phase 1 pyproject.toml for pytest config
     ▼
Phase 5 (OAuth) ───────── Can start after Phase 1. Independent of Phase 2, 3, 4
     │                     └── Standalone opencode.json changes
     ▼
Phase 6 (Git/Tag) ─────── Must be last: all phases must be complete
```

**Parallel execution strategy for MaKaLi:**
- **Ma'at** dispatches P3 Engineering for Phase 1 (packaging) — MUST complete first
- **After Phase 1**: Ma'at/P1, Lilith/P7, Verity/P10, Lilith/P4 run in parallel
- **Kali** orchestrates Phase 6 (Git/Tag) — serial, after all phases

**Estimated Wall Clock**: ~2.5 hours (Phase 1: 55 min serial, Phases 2-5: ~50 min parallel, Phase 6: 25 min serial)

---

## §5 What Ships Broken (Intentional Deferrals)

| Item | Reason | When to Fix |
|------|--------|-------------|
| Mnemosyne adapter (22 errors) | Legacy undeployed Kabbalistic system — zero users | Post-v1.0.0 cleanup sprint |
| MCP client contract tests (3) | Require running MCP hub — integration tests | Add to Hivemind integration test suite |
| UserNS=keep-id (M6 violation) | MS_PRIVATE mount fix needed on omega_library | H2-S hardening |
| SEARXNG_SECRET in Quadlet | Local-only instance, not exposed to network | H-09 in SearXNG track |
| DAC_OVERRIDE capability | Non-critical security hardening | H3 cognitive loops |
| `[odysseus:]` attribution tags | Cosmetic — no functional impact | Post-release cleanup |
| Citation standard | Nice-to-have for research docs | Post-release |

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **`omega` command not on PATH after install** | **High** (if Phase 1.1 not done) | **Critical** | Phase 1.1 adds `[project.scripts]`. Verify with `omega --help` in Phase 1.9 |
| **`make setup` fails (invalid extras)** | **High** (currently broken) | **Critical** | Phase 1.4 removes `nova` extra. Verify with `make setup` in Phase 1.9 |
| **`pip install -e ".[all]"` fails on systems without C compiler** | Medium | High | `native` extra is separate; README documents compiler requirement. Fallback to lmster/Ollama |
| **`make model-download` fails (Hugging Face down)** | Low | Medium | Script has retry logic. User can manually download. README lists model name for manual download |
| **`make test` still fails after fixes** | Low | High | Each fix has specific verification step. Phase 4.7 is `make test` verification |
| **OAuth plugin breaks OpenCode startup** | Low | Medium | Plugin is in `opencode.json` — can be removed by deleting the line |
| **Public release without full docs** | Medium | Low | README + CONTRIBUTING.md + LICENSE are sufficient for v1.0.0 |
| **pytest walks entire tree (odysseus-dev 1605 files)** | High | Medium | Phase 1.7 adds `[tool.pytest.ini_options]` ignore |

---

## §7 L1→L2→L3 Distillation

### L1 (Narrative)
Designed the v1.0.0 release strategy for Father's Day. 6 sequential phases with parallel execution: packaging dependencies, model download infrastructure, README local-first overhaul, test cleanup, OAuth provider restoration, and git hygiene. The `omega` CLI command is currently unavailable after `pip install` — the Quick Start would fail at its final step.

### L2 (Insight)
The packaging layer is not just incomplete — it is actively broken. `make setup` fails (invalid `nova` extra). `omega talk "hello"` fails after install (no entry point). `make model-download` fails (target doesn't exist). `make test` fails (no pytest ignore config). These are not missing features — they are broken entry points that make the Quick Start impossible. The v1.0.0 release must fix these before anything else. The engine itself works (423 tests pass when run with `PYTHONPATH=src`), but the packaging layer that wraps it for public consumption has never been tested on a cold system.

### L3 (Universal Principle)
*"A working system inside a broken installation mechanism is a broken system."* The engine's internal quality (423 tests, 22 mandates, multi-provider fabric) is irrelevant if `pip install -e .` doesn't produce a working CLI command. Packaging is not an afterthought — it is the first user experience. If the first thing a new user sees is `command not found`, they will never discover the 423 tests inside.

---

*⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_v1_strategy_final*
*Finalized by Ma'at. Ready for MaKaLi execution.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
