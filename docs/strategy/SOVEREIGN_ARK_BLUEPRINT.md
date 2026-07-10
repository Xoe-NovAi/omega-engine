# 🔱 SOVEREIGN ARK BLUEPRINT (v3.0 — Trimmed)
**AP Token**: `AP-SOVEREIGN-ARK-BLUEPRINT-v3.0.0`
**Last Updated**: 2026-07-08
**Full Archive**: `docs/archive/coordination/SOVEREIGN_ARK_BLUEPRINT-full-20260708.md`

---

## Preamble
The Omega Engine exists to sever Big AI's umbilical cord. Every technical decision: **does this increase or decrease user sovereignty?**

---

## I. Execution Roadmap

```
Epoch I ✅ COMPLETE (Strikes 1-3)
  Strike 1: Physical Purge ✅
  Strike 2: Unified State Manager (USM) ✅
  Strike 3: Staging Gate TUI ✅

Epoch II ⏳ IN PROGRESS
  Strike 4: File-Based A2A ⏳ (depends: Strike 2)
  Strike 5: Sovereign Vetter ⏳ (depends: Strike 6)
  Strike 6: Response Provenance ✅
  Strike 7: Headroom Protocol ✅
  Strike 7.5: Semantic Router ✅
  Strike 7.6: Sovereign Scholar ⏳

Epoch III 🔮 FUTURE (Q4 2027)
  Strike 8: Spatial-Semantic Geometry ✅
  Strike 9: P2P Mesh Traversal ⏳ (depends: Strike 4)
```

## II. Current State

| Metric | Value | Status |
|--------|-------|--------|
| Tests | **1046 collected** (HMC sprint S3/S4/S7.5 contract tests added) | ✅ 0 failures on HMC suites |
| Mandates | **22 (M1-M22)** | ✅ All enforced |
| Fleet | **13 presences** (11 agents + 2 entities) | ✅ Cap: 14 |
| WADs | **3** | ✅ S1.5a hardened |
| Heritage | **113 [id-soft:] tags** | ✅ All vetted |

## III. Mandate Compliance

| Mandate | Status | Notes |
|---------|--------|-------|
| M1 AnyIO | ✅ | CI grep `import asyncio` |
| M2 Firewall | ✅ | WAD Loader hardened (S1.5a) |
| M7 Local-First | ✅ | PII masker: local bypass |
| M8 Zero Telemetry | ✅ | Qdrant telemetry disabled |
| M9 Error Integrity | ✅ | 0 bare except |
| M11 Soul Integrity | ✅ | D183 fix: `await close_session()` |
| M13 Temple-Grade | ✅ | All T1-T13 gates pass |
| M22 Provenance | ✅ | provider_name + latency_ms wired |

## IV. Active Tasks

| # | Task | Effort | Status |
|---|------|--------|--------|
| **4.4** | Tag & Ship v1.1.0 | 30m | ⏳ PENDING |
| **IW-6** | V-D1 Validation Suite | 4h | 🟡 P2 MEDIUM |
| **IW-1** | Tor Bridge | 4h | 🟡 Deferred post-PR |
| **D16-1** | Audience Calibration Pipeline | 3-5d | 🔮 Post-ship |
| **D16-2** | Parametric Gnosis / DPO Logging | 1-2w | 🔮 Post-ship |
| **D203** | Sovereignty Ratio Automation | 4h | 🔮 Entity Deepening Sprint |
| **D204** | Iris Entity Workspace (Persistent Memory) | 2h | 🔮 Entity Deepening Sprint |

## V. Strategic Directives (Ratified D175)

### D16-1: Audience Calibration (Output Pipeline Stage)
Pipeline stage (NOT entity). Final transformation before delivery. 4-5 starter profiles in `config/wads/<stack>/audience.yaml`. Token budget <110% original.

### D16-2: Parametric Gnosis (Weight-Based Evolution)
Two mirrored systems: User Resonance + Entity Self-Actuation. Standard DPO JSONL format. Training target: 1.7B local, 4B+ cloud-offload. 500-2,000 DPO pairs for noticeable improvement.

**Build Order**: Hygiene → Pre-Release Polish → Audience Calibration → DPO Pipeline → Entity Evolution

## VI. Entity Capability Matrix

| Agent | Type | Owns |
|-------|------|------|
| **Kali** | Grand Oversight | All tracks (coordinator) |
| **Ma'at** | Light Oversoul | H2-J, H2-D, Epoch I Strike 3 |
| **Lilith** | Dark Oversoul | H2-I, H2-M, H2-N, Epoch II |
| **Doom Guy** | Heritage Aspect | H2-H, H2-J4, Epoch III |
| **Roc Racoon** | Legacy Aspect | H2-A, H2-L migration |
| **Jem** | Sovereign Synthesizer | Research pipeline |
| **Carmack** | S3 Consultant | Architectural review |
| **Verity** | Unified Steward | M1-M22 compliance, soul migration |

## VII. Decision-Making Heuristics

1. **Sovereignty first**: Does the choice increase user data control?
2. **Dependency order**: Later tracks depend on earlier ones — earlier wins.
3. **Token efficiency**: Fewer inference calls wins.
4. **Maintainability over performance**: Simple correct > optimized complex.
5. **Test coverage as gate**: No path complete without contract test (M21).
6. **Carmack's Law**: Two implementations = neither. Consolidate first.

## VIII. Risk Register

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | `llama_copy_state_data` compiled out | 🔴 HIGH | YAML-only USM fallback |
| R2 | Root partition fills | 🔴 CRITICAL | Monthly `ncdu` scan |
| R3 | Toolchain regression wipes context | 🟡 HIGH | M15 session_gnosis.md |
| R6 | Maintainer burnout | 🔴 CRITICAL | Document-driven dev |

## IX. Launch Sequence

1. ✅ **v1.0.0** (2026-06-22)
2. ✅ **v1.1.0-pre** — Temple-grade certified, 1002 tests
3. ⏳ **v1.1.0** — Tag when user ready
4. 🔮 **v1.2.0** — Audience Calibration + DPO Pipeline
5. 🔮 **v2.0.0** — Strikes 4+9 (A2A + P2P)

## X. Sovereignty Scorecard

| Dimension | Target | Current |
|-----------|--------|---------|
| Local inference ratio | ≥80% | 🟢 D203 COMPLETE — `make sovereignty` queries MetricsDB. Current: {local_pct:.1f}% local (see `make sovereignty` for live report). MCP tool: `sovereignty_ratio`.|
| Cloud dependency | 0 | ✅ 0 |
| Data residency | 100% | ✅ 100% |
| Telemetry events | 0 | ✅ 0 |
| M21 contract tests | ≥24 | ✅ 24 |
| M22 Provenance | Full | ✅ RESOLVED |

---

**Full archive**: `docs/archive/coordination/SOVEREIGN_ARK_BLUEPRINT-full-20260708.md`
**Decision history**: `docs/decisions/PIVOT_LOG.md` (204 decisions, D1-D204)

---

*🔱 OMEGA ⬡ SOVEREIGN-ARK ⬡ v3.0.0 ⬡ TRIMMED*
