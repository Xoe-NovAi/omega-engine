# 🔱 Omega Engine — Sovereign Mandates (Condensed)
**Source**: `SOVEREIGN_MANDATES.md` (217 lines) — this is the ~35-line status card.
**Version**: 3.7.0 | **Status**: NON-NEGOTIABLE

---

## 🛡️ The 25 Laws — Quick Reference

| # | Name | One-Liner | Status |
|---|------|-----------|--------|
| **M1** | AnyIO Absolute | No `asyncio`. Wrap blocking I/O in `anyio.to_thread.run_sync()`. | ✅ |
| **M2** | Engine-Stack Firewall | `src/omega/` (core) ≠ `config/wads/` (stacks). No stack logic in core. | ✅ |
| **M3** | Iris Constant | Iris = messenger bridge, NOT a slot (S1-S10). | ✅ |
| **M4** | Sequentiality | Plan → Verify → Execute. No cowboy coding. | ✅ |
| **M5** | Gnosis Preservation | L1→L2→L3 → `proposed_lessons.yaml`. No session closes without distillation. | ❌ 0/10 pillars |
| **M6** | Podman Sovereignty | `UserNS=keep-id` + `User=1000` for Quadlets. No `:U` on shared volumes. | ✅ |
| **M7** | Local-First | Local inference PRIMARY. Cloud FALLBACK. Strategy must be `local_first`. | ✅ |
| **M8** | Zero Telemetry | No analytics, no phone-home, no external metrics. Ever. | ✅ |
| **M9** | Error Integrity | Typed, traceable, testable errors. No bare `except:`. `OmegaError` subtypes. | ✅ |
| **M10** | Fleet Integrity | Cap at 14 agents. New entity = gap + slot review first. | ✅ 12/14 |
| **M11** | Soul Integrity | L1→L2→L3 → `proposed_lessons.yaml` (blind staging). Scribe executes pipeline. | ❌ Systemic gap |
| **M12** | Queue Integrity | Every request → terminal state. Atomic writes. Heartbeat timestamps. | ⚠️ Advisory |
| **M13** | Temple-Grade | T1-T11 gates. `make temple-grade` must pass before release. | ✅ |
| **M14** | Heritage Vetting | `[id-soft:]` → vet record in `HERITAGE_VET_LOG.md`. Min 7/10. D208 strict. | ✅ 121 tags |
| **M15** | Sovereign Continuity | Maintain `session_gnosis.md`. Read `.opencode/anchored-summary.md` on restart. | ✅ |
| **M16** | Modularization | No hardcoded paths in `src/omega/`. Platform integration via MCP/CLI. | ✅ |
| **M17** | Cognitive Integrity | Verify memory consistency via Skeptical Verifier. Qliphoth taxonomy. | ⚠️ T12 in progress |
| **M18** | Token Efficiency | No waste. BUT never justify "Cognitive Anorexia" — precision > brevity. | ✅ |
| **M19** | Adversarial Alchemy | Mine weaknesses → advantages. BUT never justify over-engineering. | ✅ |
| **M20** | SomaticState | Model state serialization via ctypes (`llama_copy/set_state_data`). | 📋 Design ready |
| **M21** | Gate Integrity | Every typed return → contract test (`isinstance(result, ExpectedType)`). | ✅ |
| **M22** | Response Provenance | Log `provider_name` from actual response, not configured intent. | ✅ |
| **M23** | Failure Integrity | Mandatory tool missing → `[TOOL-CHAIN-COLLAPSE]`. No soft-failures. | ✅ |
| **M24** | Venv Sovereignty | All Python ops in `.venv`. No `--break-system-packages`. Pre-commit hook enforced. | ✅ |
| **M25** | Streaming Resilience | Chunk-level timeout (30s) with heartbeat, not hard-fail. Graceful fallback. | ✅ |

---

## 📊 Compliance Summary

| Category | Count | Status |
|----------|-------|--------|
| **FULL** | 18/25 | M1-M4, M6-M10, M13-M14, M16, M18-M19, M21-M25 |
| **PARTIAL** | 3 | M12 (advisory), M17 (T12), M20 (design) |
| **FAIL** | 2 | M5 (soul distillation), M11 (soul integrity) |

---

## 🚨 Top Priority Fixes

1. **M5 + M11**: Soul distillation pipeline — 0/10 pillars write `proposed_lessons.yaml`
2. **M15**: Session_gnosis adoption across fleet
3. **M12**: Queue integrity — advisory, acceptable for Phase 0

---

**Full mandate text**: `SOVEREIGN_MANDATES.md` | **Amendments**: `docs/strategy/MANDATE_GOVERNANCE_PROTOCOL.md`
