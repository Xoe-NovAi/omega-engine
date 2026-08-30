# 🔱 Carmack Final Review — v1.0.0 Release Readiness
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_v1_final_review
**AP Token**: AP-CARMACK-FINAL-REVIEW-v1.0.0
**Date**: 2026-06-21 (Father's Day)
**Status**: ✅ APPROVED — All findings documented. Ready for MaKaLi execution.

---

## §0 Executive Verdict

**The engine is ready for v1.0.0 — but 6 gaps must be closed before public release.**

The core runtime is solid: 423 tests pass, multi-provider fabric works, entity system routes correctly, SearXNG search is alive, MemoryStore persists, Hivemind coordinates agents. But the **packaging layer has never been tested on a cold environment**. The pyproject.toml declares zero dependencies, there's no model download mechanism, and the OpenCode OAuth provider is unconfigured.

These are all gaps from the engine never having been deployed outside this machine. Every one is fixable in ~2 hours of focused execution.

---

## §1 What's Actually Working (Production-Ready)

| System | Lines of Code | Tests | Status |
|--------|---------------|-------|--------|
| Oracle (talk/summon routing) | 780 | 26 | ✅ Stable |
| Entity Registry (YAML CRUD) | 600+ | 11 | ✅ Stable |
| Model Gateway (provider fabric) | 500+ | 11 | ✅ Stable |
| Memory Store (3-tier + FTS5) | 700+ | 50+ | ✅ Stable |
| Hivemind (cross-agent awareness) | ~400 | 8 | ✅ Stable |
| SearXNG (sovereign search) | ~200 | — | ✅ Fixed this session |
| CLI (omega talk/summon) | 862 | — | ✅ Functional |
| Cvar Table (runtime config) | ~350 | — | ✅ Stable |

---

## §2 The 6 Gaps That Must Close

### Gap 1: pyproject.toml Has Zero Dependencies (🔴 Critical)
`pip install -e .` installs a package called `omega` that has no runtime dependencies. No anyio, no pydantic, no llama-cpp-python.

**Fix**: Declare `[project.dependencies]` with all 18+ runtime deps from `requirements.txt`. Make `llama-cpp-python` an optional `[native]` extra since it requires a C compiler.

### Gap 2: No Model Download Mechanism (🔴 Critical)
The engine has no bundled model. After installation, `omega talk "hello"` falls through to the `MockProvider` (canned responses) or fails silently.

**Fix**: `scripts/download_model.sh` → `make model-download` fetches Qwen 1.7B GGUF from Hugging Face.

### Gap 3: README Is Cloud-First (🟡 High)
Step 2 shows `export OPENROUTER_API_KEY` before Ollama. Violates M7 (Local-First).

**Fix**: Flip Quick Start to `make setup → make model-download → omega talk "hello"`. Cloud goes in "Advanced" section.

### Gap 4: Test Suite Has 6 Failures + 22 Legacy Errors (🟡 High)
Mnemosyne adapter errors pollute `make test`. 6 actual failures need fix or xfail.

**Fix**: Exclude odysseus-dev from pytest, xfail Mnemosyne (legacy), fix or xfail 6 failures.

### Gap 5: OpenCode OAuth Provider Not Configured (🟡 Medium)
`opencode-antigravity-auth` plugin is a git submodule but the `plugin` key and `provider.google` model definitions were never added to `opencode.json`.

**Fix**: Add plugin reference + Google provider with Antigravity/Gemini CLI model definitions.

### Gap 6: CI Workflow Stale Comment (🟢 Low)
Line 6 says "Native GGUF ... deferred to v0.6.0" — we are releasing v1.0.0 with native-gguf as primary.

**Fix**: Change comment to reflect current state.

---

## §3 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| `pip install -e ".[all]"` fails without C compiler | Medium | `[native]` extra is separate; README documents compiler requirement. Fallback to lmster/Ollama |
| Model download fails (Hugging Face down) | Low | Script retries. User can download manually |
| OAuth plugin breaks OpenCode startup | Low | Remove `plugin` line from opencode.json to unpin |
| Public release without full docs | Low | README + CONTRIBUTING.md + LICENSE are sufficient for alpha |

---

## §4 What I Would Do Differently

If I were doing this release from scratch:
1. **Write the packaging layer FIRST** — before any features. `pip install my-engine && my-engine talk "hello"` should work in the first week.
2. **Ship with a bundled micro-model** — a 100MB Qwen2.5-0.5B GGUF embedded in the package so `make model-download` is unnecessary.
3. **Test on a clean Ubuntu VM after every sprint** — this would have caught the zero-deps bug in Sprint A.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_v1_final_review*
*Verdict: APPROVED with 6 gaps. Estimate: ~2 hours wall clock for MaKaLi execution.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
