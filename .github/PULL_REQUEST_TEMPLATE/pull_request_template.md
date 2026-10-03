<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Pull Request

## Summary
<!-- Brief description of what this PR does -->

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📝 Documentation
- [ ] ♻️ Refactor
- [ ] 🧪 Test
- [ ] 🔧 Chore / CI
- [ ] 🏗️ Build / Config

## Mandate Compliance (check all that apply)
- [ ] M1 AnyIO — No `asyncio` imports in `src/omega/`
- [ ] M7 Local-First — Local inference primary, cloud fallback only
- [ ] M8 Zero Telemetry — No external analytics
- [ ] M9 Error Integrity — No bare `except:` in `src/omega/`
- [ ] M11 Soul Integrity — Session distillation to `proposed_lessons.yaml`
- [ ] M13 Temple-Grade — `make temple-grade` passes
- [ ] M22 Response Provenance — Provider name in response metadata
- [ ] M23 Failure Integrity — No soft failures, structured errors
- [ ] M24 Venv Sovereignty — No `--break-system-packages`
- [ ] M26 Doc Standards — `make doc-llm-validate` passes
- [ ] M27 Tracking Integrity — 5-Tier tracking state valid

## Testing
- [ ] `make temple-grade` passes locally
- [ ] Unit tests pass: `python -m pytest tests/ -x`
- [ ] Integration tests pass (if applicable)
- [ ] Manual verification: `omega talk "hello"` works

## Documentation
- [ ] Updated relevant docs (README, QUICKSTART, config examples)
- [ ] Updated CHANGELOG.md (if user-facing change)
- [ ] Added/updated docstrings for new public APIs

## Checklist
- [ ] No secrets, API keys, or credentials in code
- [ ] No `--break-system-packages` in install commands
- [ ] No `asyncio` imports in `src/omega/`
- [ ] No bare `except:` in `src/omega/`
- [ ] `make temple-grade` passes
- [ ] `make check-mandates` passes

## Related Issues
<!-- Link to related issues: Fixes #123, Related to #456 -->

## Screenshots / Logs (if applicable)
<!-- Add screenshots or relevant log output -->

---

**By submitting this PR, I confirm this contribution is made under the Apache 2.0 license and I have read the CONTRIBUTING.md guidelines.**
