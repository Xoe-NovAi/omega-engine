# Temple-Grade Gates (T1-T11)

The minimum quality bar for every change. Source: `SOVEREIGN_MANDATES.md` Mandate 13.

| Gate | Requirement | Hub-Relevant Check |
|------|-------------|-------------------|
| **T1** | Version Control | Meaningful commit messages. Sentence-case, prefixed (`feat:`, `fix:`, `refactor:`, `test:`). |
| **T2** | Documentation | Function-level Google-style docstrings. Module-level docstrings for new files. |
| **T3** | Testing | Coverage ≥80%. New modules need tests. |
| **T4** | Code Quality | Flake8 linting, type hints, Google-style docstrings. |
| **T5** | Architecture | No circular imports. AnyIO-only async. Zero `import asyncio`. |
| **T6** | Security | Zero telemetry. No hardcoded secrets. Keys from env vars only. |
| **T7** | Performance | Resource bounds on all loops. No O(N²) in hot paths. |
| **T8** | Resilience | Circuit breakers on external calls. Retry with backoff. Graceful degradation. |
| **T9** | Observability | Trace IDs on every request. Structured logging. |
| **T10** | Integrity | Atomic writes (`.tmp` → `os.replace`). ZONEID validation on load. |
| **T11** | Agent Security | Exempted until IA2 spec stabilizes. |

**Non-negotiable for CI**: T3, T5, T6, T8, T9, T10. Run `make temple-grade` to verify.
