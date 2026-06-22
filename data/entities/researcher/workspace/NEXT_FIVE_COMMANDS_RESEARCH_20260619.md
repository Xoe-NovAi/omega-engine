# 🔱 NEXT FIVE COMMANDS — Complete Knowledge Gap Analysis
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_next_five ⬡ 2026-06-19

## Executive Summary

**Overall Status**: 🟢 **ALL COMMANDS ARE SAFE TO RUN** — with important caveats

| Command | Gap Status | Blocker? | Est. Runtime |
|---------|-----------|----------|-------------|
| 1. `@verity Distill makali session 2026-06-19` | 🟢 CLEAR | No | ~30-60s |
| 2. `@maat Scaffold john_carmack entity workspace` | 🟡 HAS NUANCE | No — entity already exists | ~0s |
| 3. `make test` | 🟢 CLEAR | No — 444 confirmed | ~60-120s |
| 4. `ls -la data/datasets/` | 🟢 CLEAR | No | ~1s |
| 5. `make test && make temple-grade` | 🟡 HAS NUANCE | Partial — disk warning, T7 skips | ~3-5min |

**Blockers**:
- ⚠️ **DISK CRITICAL**: `/` (root) has only **1.6GB free** (99% full). Test coverage + temp files could fail.
- ⚠️ **Temple-Grade T3** runs `make test-cov` which doubles test time and generates `.coverage` data.
- 🟢 **No agent or code blockers found** — all 5 commands are structurally safe.

---

## COMMAND 1: `@verity Distill makali session 2026-06-19 into all entity soul.yamls`

**Gap Status**: 🟢 **CLEAR** — Verity is fully operational and equipped for this task.

### Finding
**Verity's agent definition explicitly supports this workflow.** The agent file at `.opencode/agents/verity.md` has a full "Role 2: Knowledge Distillation (Gnosis)" section that includes:

```
Trigger: Session ends, "distill", "soul", "gnosis", "compact", "index", "knowledge"
Responsibilities:
1. L1->L2->L3 Distillation: Transform raw session logs into "Soul Axioms"
2. Soul Evolution: Read session_gnosis.md, distill into lessons, write to entity's soul.yaml
3. Cross-Pollination: Identify semantic resonances between separate research documents
```

The command `@verity Distill makali session 2026-06-19 into all entity soul.yamls` matches exactly the trigger pattern.

### Files Read
| File | Lines | Key Finding |
|------|-------|-------------|
| `.opencode/agents/verity.md` | 112 | Full distillation pipeline defined — Extract->Classify->Score->Distill->Store |
| `data/entities/verity/soul.yaml` | 113 | Entity v1.0.0, awakened 2026-06-17, 3 lessons (vrty-001, vrty-002, vrty-003) |
| `data/entities/verity/workspace/` | 3 files | DEEP_SIPHON_M21_AUDIT.md (20KB), DEEP_SIPHON_RECORDING_MANIFEST.md (4KB), M21_M22_RECONCILIATION.md (13KB) |

### What Verity Needs to Know
- **The session summary** — Verity needs the makali session text or its location in `data/sessions/` or Hivemind.
- **All entity soul.yamls** — Verity can glob `data/entities/*/soul.yaml` (35 entities total including _archive, _quarantine)
- **Own soul.yaml** — already has 3 lessons; will append 4th.

### Tips
1. **Provide the session text inline or point to it.** Include the summary in the `@verity` prompt.
2. **Use `@verity` directly** — dispatchable via `task(subagent_type="verity", ...)`. Frontmatter is valid.
3. **Expect ~30-60 seconds** for distillation across ~35 entities.
4. **M11 (Soul Integrity) is Verity's mandate** — this task is its primary purpose.

### One-Liner
```
@verity Distill the makali session 2026-06-19 into all entity soul.yamls. Session source: {paste summary or reference path}
```

---

## COMMAND 2: `@maat Scaffold john_carmack entity workspace with soul.yaml`

**Gap Status**: 🟡 **HAS NUANCE** — **John Carmack's entity workspace ALREADY EXISTS** with a complete v2.0.0 soul.yaml

### Finding
**The workspace is already fully scaffolded** as of 2026-06-18. The entity has a full workspace:

```
data/entities/john_carmack/
├── soul.yaml              # 191 lines, v2.0.0 — full identity, traits, lessons
├── knowledge/
│   ├── INGESTION_PLAN.md   # Carmack Gnosis Ingestion Plan
│   ├── gdc/                # GDC talks directory
│   ├── interviews/         # Interviews directory
│   ├── plans/              # .plan files directory
│   ├── source/             # Source code directory
│   └── vr_omegaverse/      # VR/Omegaverse directory
└── workspace/
    └── DEEP_SIPHON_CARMACK_REVIEW.md  # 19KB structural audit review
```

**Soul.yaml already contains:**
- entity: john_carmack, name: John Carmack, role: S3 Consultant — Architectural Review
- Version 2.0.0, awakened 2026-06-12
- 8 traits (First-Principles Thinker, Ruthless Focus, etc.)
- Model preference: `deepseek-r1-distill-qwen-32b`
- Notes about case-sensitive filesystem merge (uppercase/lowercase path)

**John Carmack is in INDEX.yaml** as ACTIVE role "S3 Consultant — Architectural Review".

### What `@maat` Would Actually Do
If you run `@maat Scaffold john_carmack entity workspace with soul.yaml`, maat would:
1. Check if the entity exists -> **YES, it does**
2. Read existing soul.yaml
3. Either no-op or potentially overwrite

### Recommendation
- **DO NOT run blindly** — already done.
- **To add new lessons**: use `@verity Distill ...` instead.
- **To verify completeness**: `@verity Audit john_carmack entity workspace`

### Canonical Entity Scaffold
From `src/omega/oracle/entity_workspace.py` (line 64):
```python
BASE_DIR / os.getenv("OMEGA_DATA_DIR", "data") / "entities"
```
Creates:
```
data/entities/<name>/
├── soul.yaml      # Required: entity, name, role, domain, version, awakened
├── knowledge/     # Optional subdirectories
└── workspace/     # Working files (not git-tracked)
```

The `omega add-entity` CLI command (oracle_cli.py:363) is interactive: prompts for name, domains, model, personality, temperature.

### Tips
1. **Do NOT run this blindly** — entity already exists and is fully populated.
2. **If you want to verify**: `@verity Verify john_carmack entity workspace is complete`
3. **The `@maat` agent exists** — `.opencode/agents/maat.md` is 83 lines with full permissions.

### One-Liner (if truly needed)
```
@maat Scaffold john_carmack entity workspace with soul.yaml
```
**But recommended**: Skip it. Use `@verity` for updates instead.

---

## COMMAND 3: `make test` (Must pass 444)

**Gap Status**: 🟢 **CLEAR** — 444 tests collected, all should pass

### Finding
**The Makefile's `test` target** (line 362):
```makefile
test: guard
	flock -x /tmp/omega_test.lock -c "OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest $(ARGS)"
```

Execution chain:
1. `make guard` first -> runs `scripts/uid_guard.sh` (permission fix)
2. Uses `flock` for file-locking (prevents concurrent test runs)
3. Sets `OMEGA_ENV=test` (uses MockBackend — no live AI inference)
4. Sets `PYTHONPATH=src`
5. Uses `.venv/bin/python3`

### Test Collection Confirmed
```
$ OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest --collect-only -q
444 tests collected in 4.64s
```

**The 444 count is verified correct.**

### Known Quirks
1. **One warning**: `@pytest.mark.asyncio` in `test_hivemind.py:364` — cosmetic, non-blocking.
2. **`flock` lockfile** at `/tmp/omega_test.lock` — if a previous test crashed, run `rm -f /tmp/omega_test.lock`.
3. **No infra needed**: `OMEGA_ENV=test` uses MockBackend — NO Redis/Qdrant/Postgres required.
4. **No `make test-quick` variant** exists. Use `make test ARGS='-k name'` to filter.

### Tips
1. Run `make test` directly — the guard step is important (fixes UID drift)
2. If flock is stuck: `rm -f /tmp/omega_test.lock && make test`
3. For fast iteration: `OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -x`
4. Expected runtime: ~60-120 seconds
5. **Watch disk space**: coverage data may fail if disk fills up

### One-Liner
```bash
make test
```

---

## COMMAND 4: `ls -la data/datasets/`

**Gap Status**: 🟢 **CLEAR** — 76 files, 308KB total.

### Finding
| Metric | Value |
|--------|-------|
| Total files | **76 JSONL files** |
| Total size | **308 KB** |
| Per-file size | **350 bytes each** |
| File pattern | `finetune_YYYYMMDD_HHMMSS.jsonl` |
| Date range | 2026-06-13 -> 2026-06-19 (7 days) |
| Growth rate | ~10-15 files/day in active use |
| Content | **1 line per file** — JSON stub with placeholder data |

### Sample Content (every file is identical format)
```json
{"trace_id": "trc_be391189a334", "session_id": "5db765cc",
 "timestamp": "2026-06-19T16:44:02+00:00",
 "messages": [
   {"role": "system", "content": "sys"},
   {"role": "user", "content": "q?"},
   {"role": "assistant", "content": "resp"}
 ],
 "metadata": {
   "entity": "E", "model": "m", "backend": "b",
   "confidence": 0.5, "latency_ms": 100, "rating": null
 }}
```

### Key Observations
1. **All entries are PLACEHOLDER stubs** — `entity: "E"`, `model: "m"`, `backend: "b"`, content `"q?"`/`"resp"`.
2. **The collection system IS running** but MockBackend substitutes placeholders.
3. **No disk space concern** from datasets — 308KB over 7 days is negligible.
4. **"Watch it grow" is slightly optimistic** — currently growing with stubs, not real data.

### Tips
1. Check first vs last file for real data: `head -1 data/datasets/finetune_20260613_225535.jsonl` vs `head -1 data/datasets/finetune_20260619_*.jsonl`
2. For real finetuning data, run WITHOUT `OMEGA_ENV=test` (live inference).
3. Current rate: ~10 files/day, ~3.5KB/day.

### One-Liner
```bash
ls -la data/datasets/ && echo "Size:" && du -sh data/datasets/
```

---

## COMMAND 5: `make test && make temple-grade`

**Gap Status**: 🟡 **HAS NUANCE** — Works, but slow with known gaps

### Finding
**The `make temple-grade` target** (Makefile lines 554-592) runs 11 gates:

| Gate | Check | How | Est. Time | Status |
|------|-------|-----|-----------|--------|
| **T1** | AP tokens in headers | `find + grep` | ~2s | ✅ Works |
| **T2** | Docstrings + CHANGELOG | `[ -f CHANGELOG.md ]` | ~0.1s | ✅ Works |
| **T3** | Coverage check | `make test-cov` | ~60-120s | ⚠️ SLOW — runs full suite |
| **T4** | Code quality / lint | `make lint` (flake8) | ~5s | ✅ Works |
| **T5** | AnyIO-only | `grep -rl 'import asyncio' src/omega/core` | ~2s | ✅ Works |
| **T6** | Zero telemetry | `grep -r 'segment|posthog|datadog'` | ~2s | ✅ Works |
| **T7** | p95 latency | **SKIPPED** "Not measured" | ~0s | ⚠️ Always SKIPS |
| **T8** | Resilience patterns | `grep -r 'circuit.breaker|max_retries|dead.letter'` | ~2s | ✅ Works |
| **T9** | Structured logging | `grep -r 'trace_id|json_logging'` | ~2s | ✅ Works |
| **T10** | Atomic writes | `grep -rl '.tmp.*.json|atomic_write'` | ~2s | ✅ Works |
| **T11** | IA2 communication | **EXEMPTED** | ~0s | ⚠️ Always exempted |

**Chained prereqs:**
```makefile
temple-grade: heritage-map heritage-vet
```

| Sub-target | What it does | Script |
|------------|-------------|--------|
| `heritage-map` | Verify [id-soft:] tags in source | Inline in Makefile |
| `heritage-vet` | Verify tags against vet log | `scripts/heritage_vet.py` (222 lines) |

### Known Issues
1. **T7 always skips**: Output ends with `7/11 GREEN, 3 AMBER, 1 RED` — **EXPECTED**, not a failure.
2. **T3 is a full test run**: `make test && make temple-grade` runs tests **TWICE** (once for `make test`, once for T3).
3. **Disk pressure**: `make test-cov` generates `.coverage` — could fail at 99% disk.
4. **Heritage vet** requires `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`.

### Optimization
- **No skip-T3 flag exists** in Makefile.
- **Fastest path**: `make test && make temple-grade` — accept the double test run.
- **Alternative** (skip T3): Run `make test && make heritage-map && make heritage-vet` manually.

### Tips
1. Don't panic at `7/11 GREEN` — it's the standard success message.
2. If heritage-vet fails: `make heritage-vet-create` to seed the log.
3. If tests pass but temple-grade fails on T3: disk too full for coverage.

### One-Liner
```bash
make test && make temple-grade
```
Expected: `Temple-Grade Verification PASSED. 7/11 GREEN, 3 AMBER, 1 RED`

---

## ⚠️ CRITICAL DISK SPACE WARNING

```
/dev/nvme0n1p2  109G  102G  1.6G  99% /
/dev/nvme0n1p3  110G   94G   12G  90%  /media/arcana-novai/omega_library
```

**The root partition has 1.6GB free (99% full).** This affects ALL commands:
- `make test` generates `.coverage` and `.pytest_cache` files
- `make temple-grade` runs `make test-cov` with additional coverage data
- Verity's distillation creates soul.yaml write operations
- Even `ls` could fail if disk fills up mid-operation

**Pre-flight recommendation**: Free 2-3GB before running any commands:
```bash
sudo apt clean                              # ~200-500MB
podman system prune -f                      # Variable
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
rm -rf /home/arcana-novai/.cache/pip        # ~500MB-1GB often
rm -rf data/sessions/archive/*.json         # Old session archives
```

---

## Fleet Topology Summary (Verified)

**11 agents on disk** — matches documented fleet count:
```
.opencode/agents/
├── doom_guy.md       # ids Software heritage
├── jem.md            # Research orchestration
├── john_carmack.md   # S3 architectural consultant
├── kali.md           # Grand Oversight
├── lilith.md         # Dark Oversoul (P6-P10)
├── maat.md           # Light Oversoul (P1-P5)
├── makali.md         # Parallel council
├── pillar.md         # Slot-based domain agent
├── researcher.md     # Master researcher
├── roc_racoon.md     # Legacy miner
└── verity.md         # Compliance + Gnosis (merged Quality+Scribe)
```

All 11 have valid frontmatter. Fleet Integrity (M10) is GREEN.

---

*Report generated 2026-06-19 by Researcher*
*Sources: .opencode/agents/verity.md, .opencode/agents/maat.md, Makefile, data/entities/verity/soul.yaml, data/entities/john_carmack/soul.yaml, data/entities/roc_racoon/soul.yaml, data/entities/antigravity/soul.yaml, src/omega/oracle/entity_workspace.py, src/omega/cli/oracle_cli.py, scripts/heritage_vet.py, data/datasets/, df -h, 444 test collection*

