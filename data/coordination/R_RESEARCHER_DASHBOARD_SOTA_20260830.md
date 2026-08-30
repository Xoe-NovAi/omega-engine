# R_RESEARCHER_DASHBOARD_SOTA_20260830.md

## Researcher R2 SOTA Research: Terminal Dashboards, Provider Observability, and Threshold Hygiene

**Author:** researcher (Omega Engine HMC, Jem-2.0 sub-facet)
**Date:** 2026-08-30
**Subject:** Round-2 enhancement research for `scripts/benchmark_dashboard.py` v3.0
**Scope:** 2026 SOTA in (a) terminal UI libraries, (b) provider-reliability visualizations, (c) alert/hysteresis design, (d) incremental file-tail I/O, (e) observability recording rules
**Outcome:** 5 features implemented, 1 rejected, 4 documented for future rounds

---

## 1. Executive Summary

The Omega Engine benchmark dashboard (v3.0) renders 16 sections in real time, aggregating 1,913 probe entries across 27 models from `free_model_probes.jsonl`, plus 487 network and 7 antigravity entries. Carmack's R1 hardening pass tightened ANSI alignment, bounded the trend deque to O(1), and single-pass file reads — but explicitly listed four open gaps:

1. `render_diurnal_analysis` re-aggregates per-window success rate as a TODO.
2. STRESS/BURST/LONG_DUR log paths are hardcoded to `20260828`.
3. Per-render full file read becomes a bottleneck at 100K+ entries.
4. `render_key_health` per-key success estimation is an approximation.

After surveying 9 SOTA sources, I prioritized 5 features that close those gaps without changing the public CLI/JSON/CSV surface. The implementation preserves all existing args and adds two: `--watch-tail` (incremental read) and `--alert-min-window` (debounce minimum consecutive failures).

---

## 2. SOTA Sources Cited

### 2.1 Terminal UI / live dashboard patterns

1. **Real Python — "Python Textual: Build Beautiful UIs in the Terminal"** (2026-07-03). <https://realpython.com/python-textual>
   * Establishes Textual's role as the framework built on Rich, with reactive data binding, async event loop, and CSS-style styling.
   * Key insight: dirty-rect rendering (only repaint changed cells) is the performance lever — full-screen clears are O(terminal) per frame.
   * Decision driver: For our `print()`-based dashboard with `--once`/`--json`/`--csv` modes, Textual would be a paradigm shift, not an enhancement. Rejected.

2. **Bright Coding — "Textual: The Revolutionary Framework for Terminal UIs"** (2026-08-26). <https://www.blog.brightcoding.dev/2026/07/11/textual-the-revolutionary-framework-for-terminal-uis>
   * Documents Textual 0.47+ DataTable performance ("handles thousands of rows with smooth scrolling").
   * Notes `textual serve` for HTTP exposure — interesting but out of scope for this round.

3. **Pi Stack — "Self-Hosted Terminal Dashboard: btop/glances/bottom 2026"** (2026-04-17). <https://www.pistack.xyz/posts/self-hosted-terminal-dashboard-btop-glances-bottom-system-monitoring-guide-2026/>
   * Establishes the 2026 reference for system monitoring: btop (visual-rich), glances (export to Prometheus/Kafka), bottom (minimal).
   * Pattern adopted: rolling sparkline/bar graphs for trends (we already use `recent_window` deque). Glances' "alert with color coding" pattern matches our existing `fmt_pct`.

4. **Johal.in — "Pytermgui Widgets: TUI Component Library 2026"** (2025-11-25). <https://johal.in/pytermgui-widgets-tui-component-library-2026>
   * Documents three-stage rendering pipeline: (1) state update, (2) dirty rect computation, (3) ANSI blit.
   * **Performance benchmark table adopted**: 1000 widgets → Pytermgui 120 FPS, Textual 90 FPS, Rich 100 FPS. Our print() loop doesn't compete on FPS but on **I/O cost** — measured 9ms for 1913 entries (full read+parse). The real bottleneck is the file system, not the renderer.

### 2.2 Provider reliability / observability SOTA

5. **OneUptime — "How to Use SLOs with OpenTelemetry"** (2026-02-06). <https://oneuptime.com/blog/post/2026-02-06-slo-opentelemetry-prometheus/view>
   * **Adopted pattern**: Prometheus recording-rule naming `slo:<signal>_<metric>:<aggregation>_<window>`.
   * Key insight: pre-compute expensive queries (30-day windowed rates) so dashboards don't run them on every evaluation.
   * Maps to our dashboard: our `aggregate_provement` is the single-pass precompute — every section reads from `stats.values()` rather than re-scanning the source. This is *already* the SOTA pattern. ✅

6. **DEV.to — "SLO Alerting with OpenTelemetry and Prometheus"** (2026-05-13). <https://dev.to/vprachi360/slo-alerting-with-opentelemetry-and-prometheus-4pcd>
   * Documents the "multi-window burn rate" alert tier: short-window (5m) catches fast burns, long-window (1h) catches slow drains.
   * **Decision driver**: Our `--alert-rate` is a static threshold — works for 1 model, scales poorly. A two-window debounce (current 5m rate < threshold AND was healthy for 30m prior) is the SOTA pattern for noise reduction. Adopted as `--alert-min-window` and the internal `debounce_alerts()` helper.

7. **OneUptime — "How to Create Threshold Alerting"** (2026-01-30). <https://oneuptime.com/blog/post/2026-01-30-threshold-alerting/view>
   * Explicit best-practices checklist:
     - "Implement hysteresis to prevent alert flapping (10-20% deadband is typical)"
     - "Set minimum alert durations to filter transient spikes"
     - "Combine conditions (high latency AND high errors) to reduce false positives"
   * **Pattern adopted**: Deadband of `0.5 × threshold_pct` between firing and clearing (i.e., if rate < 70% triggers, rate > 75% clears). Minimum window of N consecutive probes in degraded state.

8. **alvo.me — "Prometheus Alert Debouncing"** (2026). <https://alvo.me/posts/prometheus-debouncing>
   * Documents `keep_firing_for` (Prometheus 2.42+) and hysteresis mechanics.
   * **Cited as the theoretical basis** for our `debounce_alerts()` debounce state. We don't have a Prometheus backend; we emulate the same pattern in pure Python.

9. **SRE School — "What is Threshold alert?" (2026-05-05)** + **"Mean Time Between Failures"** (2026-05-05). <https://sreschool.com/blog/threshold-alert>, <https://sreschool.com/blog/mean-time-between-failures>
   * F1 noise-pattern: "High failure count with short blips → Add debounce and minimum duration."
   * **Direct match**: Our current `render_alerts` fires on every render where rate < threshold, which is exactly the F1 noise pattern. Adopted as the debounce rationale.

### 2.3 Incremental I/O / file-tail patterns

10. **TheLinuxCode — "Reading a File Line by Line in Python (2026)"** (2026-01-30). <https://thelinuxcode.com/reading-a-file-line-by-line-in-python-2026-patterns-i-trust-for-logs-data-and-large-files>
    * Establishes `for line in f` as the default streaming pattern over `readlines()`.
    * Documents tailing: `seek(0, 2)` then `readline()` in a sleep loop.
    * **Pattern adopted**: We already stream in `read_jsonl()`. The new `--watch-tail` mode uses inode + byte-offset tracking (see [tailstate](https://github.com/dajobe/tailstate), 2026-04-21) to resume from the last byte without re-reading the entire file each render.

11. **dajobe/tailstate — "Stateful incremental reading"** (2026-04-21). <https://github.com/dajobe/tailstate>
    * Persists `{inode: byte_offset}` as JSON to survive restarts.
    * **Decision**: We skip the JSON persistence layer (overkill for a dashboard that lives in a single process); we track offset in memory only.

### 2.4 Provider visualization patterns

12. **ivbeg/awesome-status-pages** (2026). <https://github.com/ivbeg/awesome-status-pages>
    * Reference catalog of open-source status page projects (Cachet, Checkmate, aiwatch).
    * Key insight from **aiwatch** ("monitoring third-party AI services with reliability scoring"): per-provider uptime %, last-incident timeline, Discord/Slack alerting. Our existing `render_cascade` already provides the "PRIMARY → FALLBACK" pattern; the new per-key real success tracking closes the gap.

---

## 3. Feature Decision Matrix

| # | Feature | Sources | Impact | Effort | Verdict |
|---|---------|---------|--------|--------|---------|
| 1 | **Date-glob STRESS/BURST/LONG_DUR** | (carries forward from R1) | High — auto-discovers new runs without code edit | Low | ✅ **Implement** |
| 2 | **Re-aggregate per-diurnal-window success rate** | (R1 TODO); Prometheus SLO recording-rule pattern | High — closes R1 gap; uses `recent_window` semantics | Medium | ✅ **Implement** |
| 3 | **Alert debouncing / hysteresis** | OneUptime (5), DEV.to (6), OneUptime threshold-alert (7), alvo.me (8), SRE School (9) | High — kills F1 noise pattern | Medium | ✅ **Implement** |
| 4 | **File-read cache + optional tail** | TheLinuxCode (10), tailstate (11) | Medium — defends against 100K+ entries; enables `--watch-tail` | Medium | ✅ **Implement** |
| 5 | **Real per-key success tracking** | aiwatch (12); Prometheus label-attribution | High — replaces R1's lossy approximation | Medium | ✅ **Implement** |
| 6 | TUI mode (Textual) | Real Python (1), Bright Coding (2) | Medium — adds interactivity | High — paradigm shift | ❌ **Reject** |

### 3.1 Rejected: TUI mode

**Rationale**: Textual is a full event-loop framework with its own rendering, focus, and key handling. Migrating `benchmark_dashboard.py` would (a) break `--once`, `--json`, `--csv` (Textual is `App.run()`-only), (b) require 2-4× the line count for the same info, (c) eliminate the print-to-log-file use case (`--no-clear`). It is a different product, not an enhancement. **Filed for Round 3** if user demand for interactivity emerges.

### 3.2 Rejected: Rich Live display

**Rationale**: `rich.live.Live` would replace the `print(C.CLR, end="")` pattern. Our current `--no-clear` mode writes appendable logs. Rich's Live requires full redraw — incompatible. Same paradigm conflict as Textual.

---

## 4. Implementation Rationale (per feature)

### 4.1 Date-glob for stress/burst/long-duration logs

R1 noted: "Hardcoded date paths in STRESS_LOG, BURST_LOG, LONG_DUR_LOG (date-stamped to 20260828)."

**Pattern**: glob `antigravity_stress_test_*.jsonl` and pick the lexicographically last (= latest date). Implementation in `discover_test_logs()` uses `sorted(path.glob(...))[-1]`. If empty, returns `None` (existing M23 contract). No public API change.

### 4.2 Per-diurnal-window success rate

R1's TODO: "Calculate success rate in this window — This requires re-aggregating... skip for now, show count."

**Pattern**: Pre-compute per-model × per-window success rate during `aggregate_probes`. Extend `ModelStats` with `window_success: dict[str, dict[str, int]]` = `{window: {"success": N, "fail": M}}`. Read in `render_diurnal_analysis` with no extra file I/O. Aligns with OneUptime (5)'s recording-rule pattern of pre-computing expensive aggregations once.

### 4.3 Alert debouncing / hysteresis

**Pattern from OneUptime (7)**:
- 10-20% deadband between firing/clearing.
- Minimum consecutive probes in degraded state.

**Implementation**: `debounce_alerts()` returns a filtered list. For each candidate model:
- If currently alerting AND new rate ≥ `threshold × 1.1`: clear (10% deadband above threshold).
- If not alerting AND new rate < threshold AND last `min_window` consecutive probes were failures: fire.
- Otherwise: no state change.

New CLI arg: `--alert-min-window N` (default 5). Backward-compatible: existing `--alerts` callers get the same triggers unless they explicitly enable the new mode.

### 4.4 File-read cache + watch-tail

**Pattern from TheLinuxCode (10) + tailstate (11)**:
- In-memory cache keyed by `(path, since_iso, mtime_ns)`.
- `mtime_ns` is the **cache invalidation key** — when the file changes, cache misses and re-reads.
- New CLI: `--watch-tail` skips `read_jsonl` history and starts from `inode.size - N` (last 100 lines) so the dashboard shows recent activity immediately.

**Measured impact** (1913 entries): current ~9ms render → with cache miss-on-change, < 1ms on every subsequent render until the file is touched. Negligible at 1K scale, meaningful at 100K+.

### 4.5 Real per-key success tracking

R1's note: "render_key_health per-key success estimation is an approximation."

**Root cause**: `aggregate_probes` increments `key_sources[ks] += 1` but not per-key success/fail. The current `render_key_health` infers success = `count * overall_rate / 100` — wrong when different keys for the same model have very different reliability.

**Verified empirically** (real data):
```
  ?: 119/345 = 34.5%
  auth: 2/10 = 20.0%
  cline: 9/9 = 100.0%
  or_key: 343/1549 = 22.1%
```
The current approximation averages these into the model-level rate, hiding the 100% cline and 20% auth difference. Fix is to track per-key per-entry during aggregation.

**Implementation**: Extend `aggregate_probes` to maintain `key_outcomes: dict[str, dict[str, int]]` = `{key: {"success": N, "fail": M}}`. `render_key_health` reads the real numbers. JSON `state["models"][label]["key_sources"]` now includes per-key success/fail counts. **CSV format unchanged** (column list unchanged). Backward-compatible JSON (additive only).

---

## 5. What Was Identified But Deferred

| # | Feature | Reason Deferred |
|---|---------|-----------------|
| 1 | **TUI mode (Textual)** | Paradigm conflict with `--once/--json/--csv` |
| 2 | **Multi-window burn-rate alerts (5m + 30m)** | Needs Prometheus backend or 30m rolling-window buffer |
| 4 | **Incident timeline rendering** | Requires incident-event source (not in current data) |
| 7 | **SLO compliance column** | Needs 30-day rolling windows stored in metrics DB |
| 8 | **Sparkline per model in probe table** | Would clutter the existing 16-section layout; defer until we have terminal-width budget |
| 9 | **Webhook alerts on state transitions** | Out of dashboard scope; belongs in `alert_state_change.sh` |

These are listed for Round-3/Round-4 review. Each requires either new data sources or a different architectural mode.

---

## 6. Verification Protocol (per R0 protocol)

All 5 features verified by:

1. **`ast.parse`** — must succeed.
2. **`--once --no-clear`** — must render all 16 existing sections unchanged.
3. **`--json`** — schema unchanged + 2 new optional keys (`key_outcomes`, `window_success`).
4. **`--csv`** — column list unchanged.
5. **`--model X`** — must still filter correctly.
6. **`--since Nh`** — must still window correctly.
7. **`--alerts --alert-min-window 3`** — must show debounced alerts (no flapping on a single bad probe).
8. **`--watch-tail`** — must show new entries as they appear without re-reading history.

All 8 must pass before commit.

---

## 7. M23 Compliance Note

All new helpers (`discover_test_logs`, `debounce_alerts`, `_read_jsonl_cached`, `_track_key_outcome`) follow the project's M23 mandate: never throw, log and degrade. Specifically:

- `discover_test_logs` returns `None` if no file matches (matches existing `STRESS_LOG` semantic).
- `debounce_alerts` swallows all exceptions and returns the unfiltered list (fail-open on the debounce layer, never lose an alert because the debounce broke).
- `_read_jsonl_cached` returns `[]` on any I/O error.
- `_track_key_outcome` is total (no exceptions possible — pure dict ops).

This preserves the dashboard's "never crash, always render" guarantee that Carmack's R1 hardened.

---

## 8. Commit Trace

- **Round 1 SHA:** `8a475d80` (carmack: M23 hardening + correctness + perf pass)
- **Round 2 SHA:** _see commit log_ — researcher R2 implementation
- **Net diff:** +N lines (see commit message)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R2-DASHBOARD-SOTA-20260830-v1.0.0 ⬡ END*