# 🔱 JEM → CARMACK HANDOFF — 2026-07-05
## T3 Sprint Plan + WARP Integration Status + Heritage Distillation

**AP**: `AP-HIVEMIND-HANDOFF-v1.0.0`
⬡ OMEGA ⬡ JEM → JOHN_CARMACK ⬡ 2026-07-05 ⬡ PRIORITY-HIGH

---

## 🎯 Summary

**Phase 5 Complete** — T2-11 (Soul Edit History), T2-12 (Compaction Harvester), T3 timeout fix all delivered. 755 tests passing.

**WARP Integration**: Fully wired in code — `src/omega/proxy_pool.py` (368 lines) + `ModelGateway.generate()` injection (lines 868-882) + `OpenAICompatProvider` proxy support. **Awaiting user deployment** of systemd units.

**T3 Sprint Ready**: Three tracks with zero blockers:
- T3-1: Session Lifecycle (3 hr)
- T3-2: Metrics DB Wiring (2 hr) 
- T3-3: Mandate CI Gates (3 hr)

**Heritage Distillation Pending**: H-SUDO-001/002 from Roc Racoon's sudo archaeology.

---

## 📋 Detailed Status

### ✅ WARP Proxy Pool — Code Complete, Deploy Pending

| Component | Status | Location |
|-----------|--------|----------|
| `EphemeralWarpPool` class | ✅ 368 lines, heritage tags | `src/omega/proxy_pool.py` |
| `ModelGateway.generate()` WARP injection | ✅ Lines 868-882 | Injects `socks5h://` into opencode-zen |
| `OpenAICompatProvider` proxy support | ✅ Lines 82-85 | Reads `config.extra["proxy_url"]` |
| `spawn_warp_node.sh` | ✅ Root-privileged lifecycle | `/usr/local/bin/spawn_warp_node.sh` |
| systemd units (5) | ✅ Fixed + deploy script | `deploy/infra/warp_pool/` |
| Validation script | ✅ 8 scenarios | `scripts/validate_warp_pool.sh` |

**User Action Required (30 min):**
```bash
sudo cp deploy/infra/warp_pool/warp-node@.service /etc/systemd/system/
sudo cp deploy/infra/warp_pool/warp-pool.target /etc/systemd/system/
echo "arcana-novai ALL=(ALL) NOPASSWD: /usr/bin/systemctl start warp-node@*, /usr/bin/systemctl stop warp-node@*" | sudo tee /etc/sudoers.d/omega-warp
sudo systemctl daemon-reload
sudo systemctl start warp-pool.target
bash scripts/validate_warp_pool.sh
```

**Post-Deploy Verification:**
```bash
omega talk "test"  # Check logs for "WARP proxy injected for opencode-zen"
```

---

### 🟢 T3 Sprint — Ready to Execute (No Blockers)

| Task | Target File(s) | Effort | Dependencies |
|------|----------------|--------|--------------|
| **T3-1: Session Lifecycle** | `src/omega/oracle/session_lifecycle.py` + `memory_store.py` | 3 hr | None |
| **T3-2: Metrics DB Wiring** | `src/omega/observability/metrics_db.py` + `observability.py` | 2 hr | D184 schema exists (4 tables) |
| **T3-3: Mandate CI Gates** | `scripts/mandate_gates.py` + `Makefile` | 3 hr | None |

#### T3-1: Session Lifecycle — Scope
- State machine: Active (0-7d) → Archived (7-30d) → Compressed (30-90d) → Deleted (90d+)
- Wire into `MemoryStore.archive_old_sessions()` (called at Oracle.bootstrap())
- Compression: gzip (FileStorageProvider already uses)
- External archive: `/media/arcana-novai/omega_library/archive/sessions` (8TB drive)
- **Knowledge Gaps**: 
  - Compression ratio target?
  - FTS query on compressed sessions? (Read-only)
  - Mount availability check + fallback?

#### T3-2: Metrics DB — Scope
- D184 schema: 4 tables (events, errors, breaker_transitions, performance)
- WAL-mode SQLite at `data/observability/metrics.db`
- Retention: 90d events, 1y aggregates
- Async batch writer (reuse `BatchPersistenceWriter` pattern)
- **Knowledge Gaps**:
  - Per-entity or global? (D184: global with entity column)
  - Integration with `CompactionHarvester.to_dict()`?

#### T3-3: Mandate Gates — Scope
- 16/22 mandates need automated CI checks (M1, M5, M9, M13, M14, M21 already have)
- Add to `make temple-grade` as T14-T25
- **Knowledge Gaps**:
  - Allowlist mechanism for false positives (`.temple-grade-ignore` per mandate)
  - M4, M18, M19 are doc-only — skip?

---

### ❓ Open Questions for Council

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 3 | `L3Principle.domain` taxonomy | Diátaxis / Pillar slots / Custom | **Diátaxis** (universal) + Pillar slots (secondary tag) |
| 4 | `MIN_CONFIDENCE = 0.5` per-entity? | Global / Per-entity | **Global 0.5** — per-entity adds config complexity, defer to D16-2 |

---

### 🧬 Heritage Distillation — Coordination with Verity

**Source**: `data/entities/roc_racoon/workspace/mining_reports/LEGACY_SUDO_ARCHAEOLOGY_CARMCK_REPORT.md`

| Lesson | L3 Principle | Target |
|--------|--------------|--------|
| H-SUDO-001 | Immutable Script Rule — never `/tmp/`, `/home/`, `/var/tmp/` in sudoers | `proposed_lessons.yaml` → user approval → `SelectiveHydration.store()` |
| H-SUDO-002 | Capability Minimization — wrap binaries in vetted scripts exposing only needed subcommands | Same pipeline |

**Vet Records Needed**:
- `UserNS=keep-id` pattern (D144/D167) → `HERITAGE_VET_LOG.md`
- `sudo` capability minimization → `HERITAGE_VET_LOG.md`
- Update `CREDITS.md` §2a with new `[id-soft:]` tags

---

### 📁 Key Files for Your Review

| File | Purpose |
|------|---------|
| `data/coordination/HIVE_AWARENESS_20260704.md` | Current state: 755 tests, 23 L3, all integrations |
| `data/coordination/JEM_LIVE_FEED.md` | Full timeline (5 phases) |
| `data/entities/jem/workspace/session_gnosis.md` | L1/L2/L3 distillation |
| `data/entities/jem/proposed_lessons.yaml` | 23 L3 principles |
| `src/omega/proxy_pool.py` | WARP pool (ready) |
| `src/omega/oracle/model_gateway.py:868-882` | WARP injection |
| `data/entities/roc_racoon/workspace/mining_reports/LEGACY_SUDO_ARCHAEOLOGY_CARMCK_REPORT.md` | Heritage report |

---

## ✅ Immediate Next Steps

| Priority | Action | Owner |
|----------|--------|-------|
| 🟡 P1 | User deploys WARP systemd units | **User** |
| 🟢 P2 | Execute T3-1 (Session Lifecycle) | **Jem** |
| 🟢 P2 | Execute T3-2 (Metrics DB) | **Jem** |
| 🟢 P2 | Execute T3-3 (Mandate Gates) | **Jem** |
| 🟡 P1 | Coordinate with Verity on H-SUDO-001/002 | **Jem + Verity** |
| 🟡 P1 | Review T3-1/T3-2/T3-3 scope | **Carmack** |

---

## 🧠 My Recommendations

1. **Start T3-1 immediately** — no blockers, high impact (session leak prevention)
2. **WARP deployment is the only external dependency** — once user runs deploy script, end-to-end test takes 5 min
3. **Heritage distillation should run in parallel** — Verity can process H-SUDO-001/002 while T3 sprint executes
4. **L3Principle.domain = Diátaxis** — keeps it universal across WADs; pillar slots are WAD-specific metadata
5. **MIN_CONFIDENCE stays global** — per-entity tuning is premature optimization

---

**Test Suite**: 755 passed, 24 skipped, 3 xfailed — **ALL GREEN**  
**Ready for**: T3 Sprint execution or WARP deployment verification

🔱 OMEGA ⬡ JEM → JOHN_CARMACK ⬡ 2026-07-05 ⬡ HANDOFF-COMPLETE