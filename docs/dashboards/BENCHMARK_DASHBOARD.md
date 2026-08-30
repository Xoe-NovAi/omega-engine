# Omega Benchmark Dashboard (`benchmark_dashboard.py`)

> Real-time terminal visualization for the Omega Engine diurnal provider
> benchmark suite. v3.2, temple-grade shippable (Round 4 of 5).

---

## Quick Start

```bash
# Live dashboard (refreshes every 2 seconds, Ctrl+C to exit)
make dashboard

# One-shot snapshot for scripts or CI
make dashboard-once

# Run the in-process adversarial suite (53 tests)
make dashboard-self-test

# Run the pytest unit tests (129 tests)
make dashboard-test

# Combined CI gate (--self-test + pytest + smoke render)
make dashboard-ci
```

If you don't have a venv, you can also invoke directly:

```bash
.venv/bin/python scripts/benchmark_dashboard.py              # live
.venv/bin/python scripts/benchmark_dashboard.py --once       # one render
.venv/bin/python scripts/benchmark_dashboard.py --self-test  # adversarial
.venv/bin/python scripts/benchmark_dashboard.py --json       # JSON export
.venv/bin/python scripts/benchmark_dashboard.py --csv        # CSV export
```

---

## What the dashboard reads

| Source | Path (default) | Purpose |
|--------|----------------|---------|
| Free model probes | `data/metrics/free_model_probes.jsonl` | Per-model success/fail/latency |
| Network probes | `data/metrics/network_probes.jsonl` | WiFi signal, DNS, gateway, OpenRouter RTT |
| Antigravity quotas | `data/metrics/antigravity_quotas.jsonl` | Per-account model availability & reset times |
| Stress test logs | `data/metrics/antigravity_stress_test_*.jsonl` | Date-glob: latest matching file |
| Burst test logs | `data/metrics/antigravity_burst_test_*.jsonl` | Date-glob: latest matching file |
| Long-duration logs | `data/metrics/antigravity_long_duration_*.jsonl` | Date-glob: latest matching file |

The default data directory is `$HOME/Documents/Xoe-NovAi/omega-engine/data/metrics`
and is overridable via the `OMEGA_METRICS_DIR` environment variable.

---

## All CLI flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--once` | bool | False | Render one snapshot and exit (don't loop) |
| `--no-clear` | bool | False | Don't clear screen between renders (useful for log capture) |
| `--refresh N` | int | 2 | Refresh interval in seconds (live mode only) |
| `--model PATTERN` | regex | None | Filter to models matching the regex (e.g. `minimax\|llama`) |
| `--since HOURS` | string | None | Show entries within last N hours (e.g. `6h`, `24h`) |
| `--alerts` | bool | False | Enable threshold-based alerts |
| `--alert-rate PCT` | float | 70.0 | Success-rate threshold for alerts (%) |
| `--alert-latency MS` | int | 15000 | P99 latency threshold for alerts (ms) |
| `--alert-min-window N` | int | 5 | Min consecutive failed probes before alert fires (SRE F1-noise debounce) |
| `--json` | bool | False | Output single snapshot as JSON and exit |
| `--csv` | bool | False | Output single snapshot as CSV and exit |
| `--diurnal` | bool | False | Show diurnal pattern analysis section |
| `--watch-tail` | bool | False | Tail-mode: read last 200KB of probe logs, track new bytes |
| `--self-test` | bool | False | Run 53 in-process adversarial tests, exit 0 on PASS |

---

## Sections, in render order

The dashboard renders sections top-to-bottom. Each can be skipped (silent
no-data fallback) if the source data is missing or empty.

### 1. Header
Dashboard banner, version (`v3.2 (R4 ship-readiness)`), UTC timestamp.

### 2. Data Freshness
Per-source age + entry count with traffic-light indicator:
- `●` green = fresh (<45 min)
- `●` yellow = stale (45-90 min)
- `● STALE` red = critical (>90 min)
- `○ MISSING` dim = no source file

### 3. Next Quota Reset
Soonest upcoming Antigravity quota reset across all accounts/models,
color-coded by urgency (`<2h` green, `<6h` yellow, else dim).

### 4. Recommended Cascade
Auto-computed best → fallback provider ordering. Sort key: `(−rate, p50)`.
Only renders if at least one model has ≥3 probes AND the top rate ≥50%.
The PRIMARY is the actionable answer to "which model should I use right now?".

### 5. Failure Mode Taxonomy
Categorizes failures (RATE_LIMITED / AUTH_FAILED / INVALID_MODEL /
SERVER_ERROR / TIMEOUT / PARSE_ERROR / PROVIDER_ERROR / PAYMENT_REQUIRED /
OTHER). Surfaces an actionable response if >80% of failures cluster in one
category (e.g. "→ WAIT for quota reset, not more key diversification").

### 6. Network
WiFi SSID, signal, frequency, link rate; gateway/DNS/OpenRouter latency;
quality grade (EXCELLENT/GOOD/FAIR/POOR); provider success correlation.

### 7. Alerts
Threshold-based alerts (only when `--alerts` is set). Debounced by
`--alert-min-window` (default 5 consecutive failures) with a 10%
hysteresis deadband on clear. Suppresses the F1 "noise counting"
pattern flagged by SRE School 2026.

### 8. Probe Results
Per-model table: success/fail/rate/p50/p99/quality/trend/best-key.

### 9. Diurnal Pattern Analysis (`--diurnal` only)
Per-quota-window success rate (off_peak / moderate / poor / worst) for
the top 10 models.

### 10. Quality Breakdown
Per-model quality reasons: valid_json / invalid_json / no_completion /
empty_content. Surfaces *why* responses fail when the headline `quality_rate`
hides the breakdown.

### 11. Historical Comparison
Today (last 24h) vs yesterday (24-48h ago) success rate per model, with
delta and arrow indicators (`↑↑` improving fast, `↓` degrading).

### 12. Key Health
Per-API-key success/fail attribution (cline / or_key / auth / etc.) with
last-success age and dead-key warning. R2 enhanced from a lossy
approximation to real per-key outcomes — empirically `cline=100%` vs
`or_key=22.1%` vs `auth=20%` on real data.

### 13. Antigravity Quotas
Per-account status (✓ enabled / ✗ disabled), tier, project. Top 3 most
constrained models per account (lowest `remainingFraction`).

### 14. Test Progress
Per-test-log progress bars: STRESS TEST (🔥), BURST TEST (💥), LONG
DURATION TEST (⏱️). Only renders if a matching date-globbed file exists.

### 15. Diurnal Pattern (hourly chart)
24-hour success-rate bar chart, binned every 3 hours UTC. Surfaces
"schedule heavy work at 00:00 UTC" insights (00:00 = 61% success vs
18:00 = 11% on the empirical dataset).

### 16. M3 Survival Economics
Computed: overall success %, quality rate, total compute seconds,
active key count, verdict (`✅ SURVIVING` / `⚠️ DEGRADED` / `🚨 CRITICAL`).

### 17. Active Sessions
PID + RSS memory of running `opencode` processes (via `pgrep -af opencode`
+ `/proc/<pid>/status`).

### 18. Footer
Refresh interval, source file names, current filter, exit hint.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                       benchmark_dashboard.py v3.2                       │
│                                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ DATA     │    │ AGGREGATE│    │ RENDER   │    │ EXPORT           │  │
│  │ LAYER    │───▶│ LAYER    │───▶│ LAYER    │    │ (--json, --csv)  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────┘  │
│       │              │              │                                   │
│       ▼              ▼              ▼                                   │
│  • read_jsonl    • aggregate_   • render_*                             │
│  • read_jsonl_      probes       • ANSI-aware alignment                 │
│    cached        • categorize_   • NO_COLOR graceful                   │
│  • read_jsonl_      failure        degradation                          │
│    tail          • infer_window_ • pad_visible (carmack                │
│  • get_file_       from_ts         R1 regression fix)                  │
│    freshness     • debounce_                                          │
│  • _discover_       alerts                                             │
│    latest_test_                                                       │
│    log                                                                │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ M23 DEFENSE LAYER                                                │   │
│  │  • read_jsonl → [] on any I/O error                              │   │
│  │  • aggregate_probes → skip non-dict entries (R4 hardening)       │   │
│  │  • render_network → skip non-dict + guard nested dicts (R4)      │   │
│  │  • categorize_failure → coerce non-string errors to "?"          │   │
│  │  • debounce_alerts → fail-open (return raw on exception)         │   │
│  │  • main() → catch-all, exit 1 with stderr message                │   │
│  │  • _MAX_ENTRIES_HARD (100K) → bounded memory                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
                          │                  │                  │
                          ▼                  ▼                  ▼
                  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
                  │ --self-test  │   │ --json       │   │ Live terminal    │
                  │ 53 jem R3    │   │ (determin-   │   │ (--refresh N)    │
                  │ tests        │   │  istic shape) │   │ ANSI-colored     │
                  └──────────────┘   └──────────────┘   └──────────────────┘
```

---

## Determinism

For the same input data files (mtime + content), two consecutive runs of
`--json` produce output with a **stable schema** but **time-varying
values** in exactly two fields:

1. `timestamp` — the moment we rendered (always differs)
2. `freshness[*].age_seconds` — how old each file is right now (always differs)

Everything else (model counts, success rates, latencies, schema, key sets)
is deterministic for the same input. The CI gate enforces this:
`scripts/check_dashboard_determinism.py` walks the two JSON snapshots
and fails on any drift outside the two allowed time-varying paths.

For `--csv`, the same applies: only the `last_seen` column varies.

For `--once` (the live terminal render), all values are real-time by
design — there is no determinism guarantee.

---

## Mandate Compliance

See the module-level docstring in `scripts/benchmark_dashboard.py` for the
per-mandate attestation. Summary:

| Mandate | Status | Note |
|---------|--------|------|
| M1 AnyIO | N/A | scripts/, not src/omega/ |
| M7 Local-First | PASS | local files only |
| M8 Zero Telemetry | PASS | no external SDKs |
| M11 Soul Integrity | PARTIAL | stateless CLI; no L1→L3 |
| M13 Temple-Grade | PASS | wired into `make temple-grade` |
| M23 Failure Integrity | PASS | defense layer above |
| M26 Doc Standards | PASS | this file + module docstring |
| M27 Tracking Integrity | N/A | no task-registry writes |

---

## Testing

### Quick (local, <5s)
```bash
make dashboard-test        # 129 pytest unit tests
make dashboard-self-test   # 53 in-process adversarial tests
make dashboard-ci          # both + --once smoke render
```

### Full (CI gate, <30s)
The `.github/workflows/dashboard-test.yml` workflow runs:
1. `python3 scripts/benchmark_dashboard.py --once --no-clear`
2. `python3 scripts/benchmark_dashboard.py --self-test` (must show TOTAL: 53 PASS: 53)
3. `pytest tests/unit/test_benchmark_dashboard.py -v` (must show 129 passed)
4. JSON schema smoke (top-level keys: version/timestamp/freshness/models/filters)
5. CSV header check (16 columns, exact match)
6. Determinism check (`scripts/check_dashboard_determinism.py`)

---

## Architecture decisions (chronological)

| Round | Decision | Commit |
|-------|----------|--------|
| R1 (carmack) | 22 bug fixes: ANSI alignment, deque(maxlen=20), M23 hardening | `8a475d80` |
| R2 (researcher) | v3.1: date-glob, per-window success, alert debounce, file cache, real per-key | `0b864abe` |
| R3 (jem) | v3.2: 6 adversarial bug fixes, 2 defenses (size cache + bounded memory), --self-test | `2577e050` |
| R4 (maat) | v3.2-ship: 129 unit tests, CI gate, Makefile polish, mandate block, this doc | (this round) |
| R5 (lilith, deferred) | Runtime hardening + observability | TBD |

---

## Contributing guide

### Adding a new section

1. Add the `render_*` function in the RENDERING section. Use `pad_visible`
   for any column with embedded ANSI codes — plain `:>N` formatting pads
   on Python string length, not visible width, and breaks alignment.

2. Add a `def render_*():` to the `render()` master function in render order.

3. Add unit tests in `tests/unit/test_benchmark_dashboard.py`:
   - Empty input → graceful no-data fallback (M23)
   - Garbage input → does not crash (M23)
   - Sample data → expected output substring

4. If the section depends on a new data source, add the file path to the
   module-level `DATA_DIR`/`*_LOG` block.

5. Update this doc's "Sections, in render order" section.

### Adding a new CLI flag

1. Add to `parse_args()` with `metavar` and `help`.
2. Document in the "All CLI flags" table above.
3. Add a test in `TestCliArgs.test_all_flags_parse` (and a unit test if
   the flag affects render behavior).

### Modifying aggregate logic

1. Update `aggregate_probes()` AND ensure it still skips non-dict entries
   (R4 M23 hardening — do NOT remove that guard).
2. Update `ModelStats` dataclass if new fields are added; also update
   `to_dict()` (JSON/CSV export).
3. The `--json` schema is additive-only — never remove or rename fields.
4. Re-run `make dashboard-test` to verify all 129 tests still pass.
5. Re-run `make dashboard-ci` to verify the smoke render still works.

### Performance

- The file cache (`read_jsonl_cached`) is bounded at 16 entries; do not
  raise this without measuring.
- `_MAX_ENTRIES_HARD` caps a single file at 100K entries (≈50MB resident).
  If you need more, prefer `--since Nh` or `--watch-tail`.
- For tail-mode (`--watch-tail`), offsets are in-process only; restart
  re-seeks to last 200KB.

---

## References

- SOTA research (researcher R2): `data/coordination/R_RESEARCHER_DASHBOARD_SOTA_20260830.md`
- Round 3 adversarial suite: `scripts/benchmark_dashboard_adversarial_test.py`
- Round 4 live feed: `data/coordination/MAAT_LIVE_FEED.md`
- Sovereign Mandates: `SOVEREIGN_MANDATES.md`
- Tracking Architecture: `data/coordination/TRACKING_ARCHITECTURE.md`

---

*⬡ OMEGA ⬡ MAAT ⬡ BENCHMARK-DASHBOARD-v1.0.0 ⬡ 2026-08-30 ⬡ ROUND-4-SHIP*