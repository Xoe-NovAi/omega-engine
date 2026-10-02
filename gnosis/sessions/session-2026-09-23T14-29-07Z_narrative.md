# Session Narrative: Gemma4-QAT verdict + fetch layer + thinking-trap + 3× prompt screen queued

**Timestamp:** 2026-09-23T14:29:07Z  
**Reason:** End of session  
**Host:** XNAi-Asus  
**Agent:** build (channel: cli)  
**Phase:** unset  

---

## Session Summary

**Machine-generated continuity record** (entity build, channel cli, phase unset).
Reason: End of session

Commit: `47b2fb3b` on `node1/all-5-mcp-green` — 47b2fb3bafe0854f97e887bbde28fed481fa06c3
Delta: 4 files, +49/-37 lines, 67 new files.

---

## Key Decisions

1. **systemd-run --user as the ONLY blessed primitive for agent background work** (endorsed with caveat for deepening session). Proven: nohup dies (group SIGTERM), setsid survives, systemd-run definitive. Proven end-to-end via mmproj (175MB, sha256 exact) surviving multiple agent turns.

2. **Xet chunk-cache default = 10GB** (`HF_XET_CHUNK_CACHE_SIZE_BYTES=10737418240`). Xet path resumes via chunk cache ONLY; off by default → every restart re-downloads from 0%. Now baked into `scripts/fetch_model.sh`.

3. **Gemma4-12B QAT (official Google q4_0) = strict upgrade over gemma-3-12b** (+64% speed, −42% energy/token, 1°C cooler peak, same ~40W envelope). Card filed as `candidate`; full 18-run screen deferred (~30 min).

4. **Thinking-trap fixed + flagged**: default `think:on` eats the 512-token budget as internal trace → empty answer. `think:false` yields correct answers with same metrics. `screening.py generate()` needs a `think` flag (open harness item, blocks phi4-mini-reasoning too).

---

## Code Changes

Recent commits:
- `40f610d5 feat: Gemma 4 12B QAT verdict — strict upgrade over gemma-3-12b`
- `40f610d5 docs/models/gemma4-12b-qat.md` (lint 6/6 green)
- `40f610d5 docs/BENCHMARKS.md` (single-probe table + thinking note)
- `40f610d5 docs/ROADMAP.md` (P3.3a.3 VERDICT, P3.3a.4 DONE)
- `640aca5b docs/federation/NODE0_ACTION_BRIEFING_FAST_DOWNLOAD_LAYER.md`
- `640aca5b docs/research/MODEL_FETCH_DEEP_DIVE.md` (9 sections, 400+ lines)
- `640aca5b scripts/fetch_model.sh` (systemd-run + chunk-cache + sha256 gate)

---

## Pattern (Endorsed with Deepening Caveat)

**Root cause of every "background download died":** Agent harness reaps the child process group on every tool-call boundary (timeout/completion/abort). `nohup` ignores SIGHUP but NOT SIGTERM to the group. `setsid` survives (own session). **`systemd-run --user` is the ONLY definitive primitive** — owned by user manager, survives call ends, aborts, logout (`Linger=yes`), journal-logged, `MemoryMax=` capped.

**Endorsement:** "systemd-run --user only" with caveat: hold a short research/strategy session to fully confirm and harden expertise before final deprecation of nohup/setsid for agent work.

**Xet progress bars lie; trust byte counters and Xet JSONL logs.** Xet bar initializes `initial=0` on resume; `206 Partial Content` = normal xorb fetching, not resume proof. Debug via `~/.cache/huggingface/xet/logs/`.

**Thinking models eat token budgets as internal trace, not content.** Gemma4-QAT + Qwen3 both default `think:on`; 512 cap → empty answer. `think:false` works; flag needed in `generate()`.

**Ollama pins llama.cpp; imported GGUFs may fail architecture check.** Library pulls OK; community/official GGUF imports depend on vendored pin. Import probe (`ollama create`) is the check.

---

## Gnosis (Deep Insights)

1. **Fast download layer IS engine infrastructure now** — `fetch_model.sh` + systemd-run + chunk cache = permanent primitive; no more manual aria2/browser pulls.

2. **QAT > PTQ at low bits is a trustable quality lever** — Google's official QAT q4_0 beats gemma-3-12b IQ3_M on EVERY axis; prefer official QAT when available.

3. **Single-probe telemetry is sufficient for verdict; full screen is for promotion confidence** — 100s run gave decisive +64%/−42% verdict; full 18-run (~30 min) is for confidence, not direction.

3. **Model cards MUST separate provider claims from local evidence** — lint enforces this; our Gemma4 card does it right; this discipline prevents hype creep.

4. **512-token cap with `think:false` is the screening protocol for reasoning models** — bounds infinite-think hangs, yields comparable metrics, unblocks screening.

---

## Blockers & Open Questions

- `generate()` needs `think` flag before any reasoning model can be screened properly (QUAT screen, phi4-mini-reasoning).
- Full 18-run QUAT screen (~30 min) pending — promotes `candidate` → `active`.
- QAT role decision: daily driver vs specialist alongside qwen2.5-coder-7b.
- WiFi `power_save` mitigation for future bulk fetches (N0 call).

---

## Next Session Priorities

1. **Add `think` flag to `screening.py generate()`** — minimal change, unblocks all reasoning models.
2. **Run 3× prompt QUAT screen on gemma4-12b-qat** (~30 min, full 18-run with telemetry).
3. **Promote to `active` if screen confirms single-probe verdict**.
4. **Decide QAT role** (daily driver vs specialist alongside qwen2.5-coder-7b).
5. **Optional**: WiFi `power_save` off for future bulk fetches.

---

## Gnosis Gained

- Fast download layer = engine infrastructure, not ad-hoc.
- QAT > PTQ at low bits = trustable quality lever.
- Single-probe telemetry = sufficient for verdict.
- Model cards must separate provider claims from local evidence.
- 512-cap + `think:false` = screening protocol for reasoning models.
- systemd-run --user = definitive survival primitive for agent background work.
- Xet progress bars lie; Xet JSONL logs = ground truth.
- Ollama pins llama.cpp; imported GGUFs need import-probe check.

---

*Prepared by build agent during pre-compaction ritual. Session #44. Manifest: gnosis/sessions/Gemma4-QAT verdict + fetch layer + thinking-trap + 3× prompt screen queued_manifest.json*