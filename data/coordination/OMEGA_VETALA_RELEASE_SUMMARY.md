# 🔱 omega-vetala v2.0.0 — Release Summary

**Date**: 2026-07-11
**Status**: ✅ RELEASED
**Tests**: 137 passing (was 78 at sprint start)

---

## §1 What Was Done

### P0 Fixes (Blockers Resolved)
| # | Fix | Owner | Status |
|---|-----|-------|--------|
| P0-1 | Add `merkle-audit`, `cryptography` to `pyproject.toml` | Ma'at | ✅ |
| P0-2 | Add LICENSE (MIT) + CI workflow | Ma'at | ✅ |
| P0-3 | Async-safe `record_event()` with `anyio.Lock` + `to_thread` | Verity | ✅ |
| P0-4 | Add `test_imports_clean.py` + `test_load_config_from_wheel.py` | Ma'at | ✅ |

### Package Rename
| Change | From | To |
|--------|------|-----|
| Package name | `omega-moderation` | `omega-vetala` |
| Import path | `omega_moderation` | `omega_vetala` |
| Version | 0.1.0 | 2.0.0 |

### CLI Commands
```bash
omega-vetala moderate "hello world" --user-id test-user --json
omega-vetala serve --port 8080
omega-vetala verify-audit 0 --audit-path data/audit_chain.jsonl --json
```

### Dependencies (all declared in `pyproject.toml`)
- `merkle-audit>=0.1`
- `cryptography>=42.0`
- `pydantic>=2.6`
- `pydantic-settings>=2.2`
- `anyio>=4.3`
- `pyyaml>=6.0`
- `structlog>=24.1`
- `httpx>=0.27`

### Extras
- `[cli]` — typer + rich
- `[api]` — FastAPI + uvicorn
- `[db]` — SQLAlchemy + aiosqlite
- `[observability]` — prometheus-client
- `[all]` — everything

---

## §2 Test Coverage

| Suite | Tests | Purpose |
|-------|-------|---------|
| `test_adversarial.py` | 53 | Obfuscation: leetspeak, homoglyphs, tag-char, bidi, Greek, repeated-char, dual-pass |
| `test_contracts.py` | 7 | M21 gate-integrity (type contracts) |
| `test_smoke_test.py` | 17 | Core functionality smoke tests |
| `test_audit_verify.py` | 5 | Merkle + Ed25519 audit chain |
| `test_differential_privacy.py` | 13 | ε-DP metrics |
| `test_engine_integration.py` | 5 | Engine integration |
| `test_gdpr_erasure.py` | 3 | GDPR Article 17 tombstoning |
| `test_huggingface_detector.py` | 6 | HF ensemble voting, lazy load |
| `test_imports_clean.py` | 6 | M1 AnyIO (no asyncio imports) |
| `test_load_config_from_wheel.py` | 7 | Config loader fallback |
| `test_privacy_dp.py` | 9 | Privacy + DP |
| `test_regression.py` | 8 | Edge cases (empty, None, 100K, emoji, concurrent) |
| **Total** | **137** | |

---

## §3 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Overview, install, quick start |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT (sovereign-aligned) |
| `SECURITY.md` | Vulnerability reporting |
| `CONTRIBUTING.md` | Community PR guide |
| `docs/USER_GUIDE.md` | Install, configure, run, integrate |
| `docs/DEVELOPER_GUIDE.md` | Add detectors, governance backends, tests |
| `docs/ARCHITECTURE.md` | Data-flow + component map |
| `docs/API_REFERENCE.md` | CLI + API endpoints |
| `docs/OPERATIONS_GUIDE.md` | Metrics, audit verify, GDPR erasure |
| `docs/SOVEREIGN_COMPLIANCE.md` | Mandate compliance + gaps |
| `docs/MODULE_MANIFEST_SPEC.md` | `module.yaml` schema |
| `docs/MODULE_STANDARD.md` | Omega Module Standard (template for all modules) |
| `docs/MIGRATION_GUIDE.md` | `omega-moderation` → `omega-vetala` |

---

## §4 Mandate Compliance

| Mandate | Status |
|---------|--------|
| M1 AnyIO | ✅ Zero `asyncio` imports |
| M2 Firewall | ✅ No core engine imports |
| M7 Local-First | ✅ `use_local: true` default |
| M8 Zero Telemetry | ✅ No external calls |
| M9 Error Integrity | ✅ Typed exceptions |
| M13 Temple-Grade | ✅ 137 tests passing |
| M16 Portability | ✅ `pip install -e .` works |
| M20 SomaticState | ✅ Async-safe lock pattern |
| M21 Gate Integrity | ✅ Contract tests |
| M23 Failure Integrity | ✅ No soft-failures |

---

## §5 Next Steps

| Task | Priority | Status |
|------|----------|--------|
| Omega Module Standard v1.0 | P1 | Roadmap |
| ProvenanceSpan implementation | P2 | Roadmap |
| Entry_points plugin discovery | P2 | Roadmap |
| SIGTERM handler for uvicorn | P2 | Roadmap |

---

*⬡ OMEGA ⬡ omega-vetala ⬡ v2.0.0 Release Summary*