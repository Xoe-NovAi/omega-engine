# 🔱 ElevenLabs Sovereign Console – Hackathon Blitz Full Plan

**Prepared for:** Gemini CLI review
**Author:** PROMETHEUS (Sovereign Master Researcher)
**Version:** 1.0.0
**Date:** 2026-05-14

---

## 1️⃣ Sub‑Agent Prompt Library

Below is the complete set of **OpenCode sub‑agent prompts** that drive the Sovereign Blitz workflow.  Each prompt can be launched via the `task` tool (or any sub‑agent executor) and will run autonomously.

| Sub‑Agent | Trigger Command (`task`) | Prompt |
|-----------|--------------------------|--------|
| **knowledge‑miner** | `task(description="Mine patterns", prompt="/knowledge‑miner <prompt>", subagent_type="explore")` | *Prompt #A* (see below) |
| **provider‑validator** | `task(description="Validate providers", prompt="/provider‑validator <prompt>", subagent_type="general")` | *Prompt #B* |
| **spec‑generator** | `task(description="Generate spec", prompt="/spec‑generator <prompt>", subagent_type="general")` | *Prompt #C* |
| **the‑compiler** | `task(description="Compile plugin", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #D* |
| **the‑tester** | `task(description="Run heartbeat tests", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #E* |
| **the‑scribe** | `task(description="Live journal", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #F* |
| **blitz‑tunnel‑operator** | `task(description="Spawn tunnel", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #G* |
| **blitz‑validator** | `task(description="Validate blitz stack", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #H* |
| **rubric‑mapper** | `task(description="Map rubric", prompt="/research <prompt>", subagent_type="general")` | *Prompt #I* |
| **voice‑persona‑designer** | `task(description="Create voice personas", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #J* |
| **latency‑benchmark‑engine** | `task(description="Benchmark hardware", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #K* |
| **ci‑pipeline‑assembler** | `task(description="Create CI workflow", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #L* |
| **risk‑manager** | `task(description="Build risk dashboard", prompt="/builder <prompt>", subagent_type="general")` | *Prompt #M* |

---

### Prompt #A – knowledge‑miner
```
You are the **knowledge‑miner** sub‑agent. Your mission: locate, extract, and summarise any pattern or specification required for the ElevenLabs Sovereign Voice Console.

1. Use `grep` (or the provided `knowledge‑miner` skill) to find occurrences of the target term in:
   - `src/omega/oracle/`
   - `mcp/omega_hub/`
   - `docs/`
2. For each hit, `read` the surrounding 30 lines.
3. Distil the info into a high‑density bullet list (max 5 bullets per source).
4. Return a JSON object:
```json
{
  "source": "<path>",
  "snippet": "<excerpt>",
  "summary": ["..."]
}
```
5. If the term is a URL or external API, also `webfetch` it and include the fetched summary.

End with **"Knowledge‑miner complete"**.
```

---

### Prompt #B – provider‑validator
```
You are the **provider‑validator** sub‑agent.

Read `config/providers.yaml`, iterate each entry, and perform a live health‑check:
- HTTP backends: `curl -s -o /dev/null -w "%{http_code}" <url>`
- Token‑based services: minimal `POST` with dummy payload, check for 2xx.

Produce a markdown table:
| Provider | URL | Status | Notes |
|----------|-----|--------|-------|

If any provider fails, suggest the immediate fallback (e.g., switch to `lmster`).

Conclude with **"Provider‑validator complete"**.
```

---

### Prompt #C – spec‑generator
```
You are the **spec‑generator** sub‑agent.

Input: raw research markdown (e.g., `R‑B1_elevenlabs_spec.md`).

Produce an Omega‑standard spec:
1. Front‑matter block (YAML) with title, author, created‑timestamp, status, related files.
2. Sections: Summary, Technical Details (code / JSON), Implementation Note (directed at Builder agents), Validation.

Export to `docs/research/<slug>.md` and return **"Spec‑generator done"**.
```

---

### Prompt #D – the‑compiler
```
You are **the‑compiler** sub‑agent.

1. `cd plugins/sovereign`
2. `npm install` (or `bun install`).
3. `npm run lint` – auto‑fix if possible.
4. `npm run build` – capture stdout/stderr.
5. On success write `BUILD_SUCCESS=true` to `/.env.blitz`.

Return JSON `{ "build": "success|failure", "log": "<first‑200‑chars>" }`.
Conclude with **"the‑compiler finished"**.
```

---

### Prompt #E – the‑tester
```
You are **the‑tester**.

Run the full **Sovereign Heartbeat** checklist:
1. Tunnel health (`curl -I $PUBLIC_URL/health`).
2. Tool latency (`oracle_talk` round‑trip ≤ 800 ms).
3. Interrupt test (start a long tool call, issue cancel, verify voice stops ≤ 300 ms).
4. Filler fallback (throttle `library_search` and confirm filler phrase).

Output JSON matrix:
```json
{ "tunnel": "ok", "latency_ms": 642, "interrupt_ms": 274, "filler_used": true }
```
Finish with **"the‑tester complete"**.
```

---

### Prompt #F – the‑scribe
```
You are **the‑scribe**.

Create/append `docs/demo/blitz_journal.md`:
- Timestamped headings for each sub‑agent completion.
- Copy JSON results as fenced code.
- Capture stdout/err (truncate to 500 chars) as fenced blocks.
- When a screenshot is requested, run `scrot /tmp/blitz_<step>.png` and embed `![step](/tmp/blitz_<step>.png)`.
- Add a short “Lessons Learned” section at the end.

End with **"the‑scribe done"**.
```

---

### Prompt #G – blitz‑tunnel‑operator
```
You are **blitz‑tunnel‑operator**.

1. Verify `cloudflared` exists (`which cloudflared`).
2. Run `cloudflared tunnel --url http://127.0.0.1:8016 --logfile /tmp/cloudflared.log`.
3. Capture the public URL from stdout (`https://<random>.trycloudflare.com`).
4. Write `PUBLIC_URL="<url>"` to `.env.blitz`.
5. If cloudflared fails, fallback to `ngrok http 8016`.

Return JSON `{ "public_url": "<url>", "engine": "cloudflared|ngrok", "status": "ready" }`.
Finish with **"blitz‑tunnel‑operator complete"**.
```

---

### Prompt #H – blitz‑validator
```
You are **blitz‑validator**.

1. Load `PUBLIC_URL` from `.env.blitz`.
2. POST to `$PUBLIC_URL/blitz‑validate` (the ElevenLabs tool).
3. Parse JSON – if `"status":"ready"`, write `BLITZ_READY=true` to `.env.blitz`.
4. On failure, output error payload and suggest re‑run `blitz‑tunnel‑operator`.

Return `{ "validation": "pass|fail", "details": "<msg>" }`.
Finish with **"blitz‑validator done"**.
```

---

### Prompt #I – rubric‑mapper
```
You are **rubric‑mapper**.

1. `webfetch` the hackathon rules PDF (`https://elevenlabs.com/hackathon/2024/rules.pdf`).
2. Extract the **Evaluation Criteria** table.
3. Map each criterion to the relevant research work‑packages (R‑B1…R‑B8).
4. Write a markdown matrix to `docs/research/RB2_judge_rubric.md`.

Conclude with **"rubric‑mapper finished"**.
```

---

### Prompt #J – voice‑persona‑designer
```
You are **voice‑persona‑designer**.

1. Define `entity_voice_map.json` mapping each Pillar Keeper/Oversoul to an ElevenLabs `voice_id`, `prosody`, and optional `emotion`.
2. For each entry, call the ElevenLabs TTS endpoint (`POST /v1/tts`) with a one‑sentence line (e.g., “I am SOPHIA, the Akashic Record.”).
3. Save each MP3 to `docs/demo/voice_samples/<entity>.mp3`.
4. Log any failures and fallback to a default voice.

Return `{ "voice_map_written": true, "samples_created": 14 }`.
Finish with **"voice‑persona‑designer done"**.
```

---

### Prompt #K – latency‑benchmark‑engine
```
You are **latency‑benchmark‑engine**.

Create `benchmark_latency.py` that measures:
- HTTP round‑trip for each `omega‑hub` tool (oracle_talk, library_search, hivemind_get_awareness).
- CPU/RAM usage during 5 concurrent calls (use `psutil`).
- Impact under thermal throttling (`stress‑ng --cpu 8 --timeout 30s`).

Output `benchmark_report.csv` and a markdown summary `docs/research/RB6_hardware_benchmark.md` with key numbers and a recommendation (max concurrent tools = 2).
Return `{ "benchmark": "complete", "csv_path": ".../benchmark_report.csv" }`.
Finish with **"latency‑benchmark‑engine done"**.
```

---

### Prompt #L – ci‑pipeline‑assembler
```
You are **ci‑pipeline‑assembler**.

Generate `.github/workflows/elevenlabs_demo.yml` with jobs:
1. `setup` – install Python, Node/Bun, cloudflared.
2. `hub` – start `python mcp/omega_hub/server.py` in background.
3. `tunnel` – run `cloudflared tunnel …` and export `$PUBLIC_URL`.
4. `test` – invoke `the‑tester` to verify health.
5. `record` – use `ffmpeg` to capture terminal + ElevenLabs audio into `demo_build.mp4`.
6. `artifact` – upload the mp4 and the pitch deck.

Add a manual `workflow_dispatch` trigger for local runs and a `timeout-minutes: 120`.
Write the file, commit a **draft PR** titled “Add ElevenLabs Demo CI”.
Return JSON `{ "workflow_path": ".github/workflows/elevenlabs_demo.yml", "pr_created": "draft", "status": "ready" }`.
Finish with **"ci‑pipeline‑assembler done"**.
```

---

### Prompt #M – risk‑manager
```
You are **risk‑manager**.

Build `docs/ops/health_dashboard.html` showing:
- Tunnel ping (`$PUBLIC_URL/health`).
- ElevenLabs API quota usage (`/v1/account/usage`).
- Countdown timer from the start of the 2‑hour demo window.
- Green/red indicators for critical sub‑agents.
Refresh every 5 seconds via JavaScript.
Open the HTML file in the default browser and log the path.
Return `{ "dashboard": "docs/ops/health_dashboard.html", "opened": true }`.
Finish with **"risk‑manager complete"**.
```

---

## 2️⃣ Full Roadmap (Phase‑wise)

| Phase | Time | Activities | Sub‑Agents | Deliverables |
|-------|------|------------|------------|--------------|
| **Phase 0 – Preparation** (≈ 2 h) | 0‑120 min | Clone repo, fetch API spec, validate providers, generate voice map, spin up tunnel, run validator, compile plugin, run heartbeat, benchmark hardware. | #A, #B, #J, #G, #H, #D, #E, #K | `.env.blitz` (ready), `BUILD_SUCCESS=true`, `heartbeat_report.json`, `benchmark_report.csv` |
| **Phase 1 – Development Sprint** (≈ 6 h) | 0‑360 min | Finalize tool schema, implement filler state‑machine, set concurrency cap, produce rubric matrix, assemble CI workflow, deploy risk dashboard. | #A, #C, #E, #K, #I, #L, #M | `elevenlabs_tool_schema.json`, updated plugin source, `RB2_judge_rubric.md`, `.github/workflows/elevenlabs_demo.yml`, `health_dashboard.html` |
| **Phase 2 – Live Hackathon** (≈ 2 h) | 0‑120 min | Start hub, launch tunnel, validate, load ElevenLabs console, demo walkthrough (questions, summons, slow research with filler, interrupt, risk dashboard), play voice‑samples, close pitch. | — (human‑driven, but all services pre‑validated) | Live video (`demo_build.mp4`), pitch deck (`JUDGE_PITCH.md`), final submission package |

All steps are logged by **the‑scribe** (running in background) for the demo journal.

---

## 3️⃣ Resources Index

| Resource | Path / URL | Purpose |
|----------|------------|---------|
| **Full plan** | `docs/team/BLITZ_FULL_PLAN.md` (this file) | Reference for all agents and timeline |
| **Tool schema** | `docs/research/elevenlabs_tool_schema.json` | JSON uploaded to ElevenLabs |
| **Voice map** | `plugins/sovereign/entity_voice_map.json` | Entity → ElevenLabs voice mapping |
| **Tunnel env** | `.env.blitz` | Holds `PUBLIC_URL` and readiness flags |
| **Benchmark** | `tools/benchmark_latency.py` + `docs/research/RB6_hardware_benchmark.md` | Hardware performance data |
| **CI workflow** | `.github/workflows/elevenlabs_demo.yml` | Automated end‑to‑end demo build |
| **Risk dashboard** | `docs/ops/health_dashboard.html` | Live health monitor |
| **Demo journal** | `docs/demo/blitz_journal.md` | Chronological log for video narration |
| **Pitch deck** | `docs/research/JUDGE_PITCH.md` | One‑page judge summary |

---

## 4️⃣ Acceptance Checklist (Done Criteria)

- [ ] All sub‑agents have a documented prompt (see above).
- [ ] `blitz‑tunnel‑operator` creates a working public URL.
- [ ] `blitz‑validator` returns `status: ready` and sets `BLITZ_READY=true`.
- [ ] `the‑compiler` builds the Sovereign Plugin (`BUILD_SUCCESS=true`).
- [ ] `the‑tester` heartbeat JSON shows latency ≤ 800 ms, interrupt ≤ 300 ms, filler used.
- [ ] Benchmark recommends **max_concurrent_tools = 2**.
- [ ] `rubric‑mapper` produces `RB2_judge_rubric.md` covering every rubric item.
- [ ] CI workflow runs cleanly and publishes `demo_build.mp4`.
- [ ] Risk dashboard displays green health and a countdown.
- [ ] Final submission bundle contains video, pitch deck, all research markdowns, and the one‑page README.

When every ✅ is ticked, the Sovereign Voice Console is **contest‑ready**.

---

*End of document.*
