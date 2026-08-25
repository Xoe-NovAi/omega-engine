# 📋 P1 REPORT — NODE N1 INFRASTRUCTURE (Surface S7: Config Surfaces)
⬡ OMEGA ⬡ NODE1 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1 ⬡ Stage-1 RAW
**source_node**: N1 Infrastructure | **arm**: maat | **tier**: node | **session**: 20260825-094633-first-light
**task_id**: `express-c1-node1-20260825` (registered in Task Registry)
**Date**: 2026-08-25 | **Mode**: RECON ONLY — zero production mutations
**Surface S7 scope**: `opencode.json`, `config/*.yaml`, `config/wads/**` (manifests), `.opencode/plugins/`, `.opencode/hooks/`

---

## §0 EXECUTIVE VERDICT

The config layer is **structurally rich but partially decayed**. One CRITICAL wiring defect
(broken plugin paths), one HIGH security finding (`"/*": "allow"` wildcard), a three-way
provider-order contradiction between the two constitution files and providers.yaml, and a
wide gap between **configured** providers and **credentialed** reality (5 of 10 cloud chain
entries have no API key in env). No CRITICAL-HALTED finding: **no active external telemetry
discovered** (M8 bright line holds at the config layer). Stale placeholder secrets found =
logged as FINDING per mandate §C.4, continued.

---

## §1 FINDINGS

### F-01 · CRITICAL — opencode.json registers plugins on DEAD PATHS
- **Evidence**: `opencode.json:7-8` registers
  `file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts`
  and `.../.opencode/plugin/awareness.ts`.
  Verified: `.opencode/plugin/` **does not exist** — actual dir is `.opencode/plugins/` (plural):
  ```
  ls -d .opencode/plugin        # → "No such file or directory"
  ls .opencode/plugins/         # → awareness.ts error-capture.ts silent-stall-sensor.ts test-event.js.DISABLED
  ```
- **Impact**: The two plugins that technically implement instruction-level behaviors are wired
  to nothing: `error-capture.ts` (subagent-failure capture → JSONL log → Hivemind notify →
  synthetic `<subagent-failure>` injection into parent session — the technical arm of M23/M12)
  and `awareness.ts` (stream-death/restart/compaction awareness injection). No
  `data/coordination/errors/subagent-errors-*.jsonl` file has EVER been written (dir checked),
  consistent with error-capture never having fired.
- **Nuance / open question**: `silent-stall-sensor.ts` is NOT in the `plugin` array yet is
  demonstrably LIVE (`data/coordination/errors/silent-stalls-2026-08-25.jsonl` written today
  13:02:44Z; hourly snapshot updated 13:06Z). This implies OpenCode may auto-load
  `.opencode/plugins/` by directory convention — in which case error-capture/awareness may
  also load despite the broken explicit paths, and the defect is "config lies about mechanism"
  rather than "tools dead". Empirical confirmation belongs to N6/@researcher (S3 live-vs-decorative tests).
- **Recommended fix (bash-verifiable)**:
  ```bash
  # Fix: correct paths in opencode.json
  sed -i 's#\.opencode/plugin/#.opencode/plugins/#g' opencode.json
  # Acceptance: every registered plugin path exists
  jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" && echo "OK $f" || echo "MISSING $f"; done
  # Acceptance: zero MISSING lines.
  ```

### F-02 · HIGH — Permission wildcard `"/*": "allow"` makes the entire external_directory block decorative
- **Evidence**: `opencode.json:10-26`. Eleven specific allow-rules are followed by
  `"/*": "allow"` — a universal grant covering every path on the filesystem.
- **Impact**: Config-instruction inconsistency: instruction layers preach sandbox discipline
  (M8, T11, tainted-data quarantine), while the runtime grants agents access to everything.
  The enumerated rules are dead weight; the effective policy is "allow all".
- **Recommended fix**: remove the `"/*"` entry; keep the enumeration.
  ```bash
  # Acceptance: wildcard gone, enumeration intact
  jq '.permission.external_directory | has("/*")' opencode.json   # → false
  jq '.permission.external_directory | keys | length' opencode.json # → ≥ 10
  ```

### F-03 · HIGH — Three-way provider-order contradiction (Mandates vs Ark vs providers.yaml)
- **Evidence**:
  - `SOVEREIGN_MANDATES.md` M7 pattern: `native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6)`
  - `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §7 + D-355: cloud order **Antigravity → Google → OCZ → OpenRouter**
  - `config/providers.yaml:62-135`: `antigravity(3), google(4), openrouter(5), opencode-zen(6)` — i.e. **OpenRouter BEFORE OCZ**, contradicting the Ark; and Google at 4 (not 3), contradicting M7's literal chain.
- **Impact**: An agent obeying the constitution text routes differently than the engine does.
  Exactly the "strategy docs claiming different critical paths" structural-debt gate (Ark §9.5) — but in config form.
- **Recommended fix**: pick ONE canonical order (recommend Ark/D-355: swap openrouter↔opencode-zen priorities in providers.yaml), then amend M7 text to name antigravity.
  ```bash
  # Acceptance: OCZ priority < openrouter priority in the flat chain
  python3 -c "
  import yaml; c=yaml.safe_load(open('config/providers.yaml'))
  p={e['provider']:e['priority'] for e in c['inference']['fallback_chain']}
  assert p['opencode-zen'] < p['openrouter'], p"
  ```

### F-04 · HIGH — Credential-reality drift: majority of the cloud chain is configured but dead
- **Evidence** (env probe, names only, this session):
  `EXA_API_KEY=UNSET · GOOGLE_API_KEY=UNSET · ANTHROPIC_API_KEY=UNSET · XAI_API_KEY=UNSET · ANTIGRAVITY_API_KEY=UNSET`; SET: `OPENCODE_API_KEY, OPENROUTER_API_KEY, OMEGA_MODELS_DIR`.
  providers.yaml enables google/google-compat/anthropic/xai/antigravity with `api_key: env:*`;
  opencode.json enables exa MCP with `${EXA_API_KEY}` header.
- **Impact**: Effective working fabric = native-gguf + lmster (local) + opencode-zen + openrouter (cloud). All `fallback_resolver` chains terminate in providers that will 401/drop. `maakali_routing.kali.fallback: antigravity` points at an uncredentialed provider. Sovereignty claims and failover design should be stated against the REAL fabric, not the paper one.
- **Recommended fix**: either provision keys (Architect action) or mark uncredentialed providers `enabled: false` until keyed.
  ```bash
  # Acceptance: every enabled provider with api_key env:* resolves to a set var
  python3 -c "
  import yaml, os
  c=yaml.safe_load(open('config/providers.yaml'))
  for e in c['inference']['fallback_chain']:
      k=e.get('api_key','')
      if e['enabled'] and k.startswith('env:') and not k.endswith('*'):
          pass
  provs=c['inference']['providers']
  bad=[n for n,p in provs.items() if p.get('enabled') and str(p.get('api_key','')).startswith('env:') and str(p['api_key']).split(':',1)[1] not in os.environ]
  print('DEAD:',bad); assert not bad"
  ```

### F-05 · MED — Archived strategy doc injected into EVERY session's instructions
- **Evidence**: `opencode.json:27-33` `instructions[]` includes
  `docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md`. Verified live: this node's own
  system prompt contains that document, including its stale provider fabric ("native-gguf(0) → … → Google(3)") and Horizon-status claims that contradict SOVEREIGN_ARK_BLUEPRINT (also injected) — a per-session, every-session contradiction.
- **Impact**: Every agent every session burns tokens absorbing a superseded roadmap as instruction. Direct violation of Ark §10.8 ("Do not resurrect archived roadmaps as competing masters") — committed by config itself.
- **Recommended fix**: drop the archive path from `instructions[]`.
  ```bash
  # Acceptance: no docs/archive/** path in instructions[]
  jq -r '.instructions[]' opencode.json | grep -c '^docs/archive/'   # → 0
  ```

### F-06 · MED — council.yaml references nonexistent models + contradicts M7
- **Evidence**: `config/council.yaml:18-23` — `model_tiers` claims "(references providers.yaml)"
  but names `gemma-4b-local`, `nemotron-8b-cloud`, `nemotron-12b-cloud`; NONE exist anywhere in
  providers.yaml/models.yaml. Line 68: `M7_local_first: false  # Advisory — cloud is acceptable during dev`
  contradicts M7 (NON-NEGOTIABLE local-first) and providers.yaml `strategy: local_first`.
- **Recommended fix**: remap tiers to real model ids; flip M7 flag or document Architect exception.
  ```bash
  # Acceptance: every council model_tiers value appears in providers.yaml or models.yaml
  grep -q 'gemma-4b-local' config/providers.yaml config/models.yaml   # currently fails → must pass after fix
  ```

### F-07 · MED — Placeholder PATs presented as ACTIVE credentials; perms violate own header
- **Evidence**: `config/github_accounts.yaml:10,20` — `pat: "ghp_placeholder_…"` with
  `status: "active"`; header line 4 demands `0400 permissions`; actual `stat` = `664`.
- **Classification per §C.4**: STALE SECRET = FINDING (logged, continued). Values are obvious
  placeholders — NOT real credentials; no HALT.
- **Recommended fix**: `chmod 600 config/github_accounts.yaml`; move PATs to env/vault (V-1);
  set status `placeholder` until real tokens land.
  ```bash
  # Acceptance: stat -c "%a" config/github_accounts.yaml → 600 ; grep -c ghp_placeholder → 0 (post-V-1)
  ```

### F-08 · MED — omega.yaml duplicates the entire sovereignty_gate block
- **Evidence**: `config/omega.yaml:50-55` and `:71-77` — identical `sovereignty_gate` blocks,
  second copy pasted under "# Hardware optimization" section header region.
- **Fix**: delete one block. `grep -c 'sovereignty_gate:' config/omega.yaml` → must equal 1.

### F-09 · MED — IWAD manifest drift: manifest lists 15 entities, disk has 24
- **Evidence**: `config/wads/_omega_default/manifest.yaml` entities list (15 entries) vs
  `ls config/wads/_omega_default/entities/` = 24 files. Unlisted: dispatch, doom_guy, jem,
  john_carmack, quality, researcher, roc_racoon, scribe, verity.
- **Impact**: Anything consuming the manifest (WAD loader, community stacks) sees a ghost fleet.
- **Fix**: regenerate manifest from disk.
  ```bash
  # Acceptance: manifest entity count == dir count
  diff <(ls config/wads/_omega_default/entities/ | sort) \
       <(grep -oE '"[a-z_]+\.yaml"' config/wads/_omega_default/manifest.yaml | tr -d '"' | sort)
  ```

### F-10 · MED — Triple agent-manifest drift (opencode.json vs agents/*.md vs MANIFEST.md)
- **Evidence**:
  - `.opencode/MANIFEST.md` claims "13-agent fleet, deprecated build stub, ghost agents removed" — yet `.opencode/agents/build.md` (deprecated stub) still exists; MANIFEST primary-modes table omits `grok_cli` which opencode.json defines; `scribe` claimed as primary mode but has no opencode.json block (file-auto-reg only).
  - Dual definitions disagree: opencode.json `kali.description` = "Grand Oversight — Sees all…" vs `.opencode/agents/kali.md` frontmatter = "Sovereign Agent: kali (Sovereign Agent)". Which description an agent presents depends on which layer wins — undocumented.
- **Fix**: single source decision (recommend: agents/*.md frontmatter is SSOT; opencode.json only adds env/model overrides), then reconcile MANIFEST counts.
  ```bash
  # Acceptance: no agent defined with differing descriptions in both layers
  for a in kali maat lilith; do diff <(jq -r ".agent.$a.description" opencode.json) <(awk '/^description:/{print; exit}' .opencode/agents/$a.md) && echo "$a OK"; done
  ```

### F-11 · MED — Unvetted heritage tag in config (M14)
- **Evidence**: `config/models.yaml:101` `[id-soft: gemma-4-mtp-s4]` — no vet record matches
  this tag id in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (closest is vet-069
  "Speculative Decode" tagged `[id-soft: quake3-1999]`). Other id-soft-tagged config files:
  `config/wads/_omega_default/ethics.yaml`, `config/domains/engineering/MEMORY_BLOCKS/project-gotchas.block`, `config/omega/requirements.omega` (vet coverage unverified — flag for N5/verity).
- **Fix**: add vet record with file:line + scope declaration, or re-tag as METAPHORICAL.
  ```bash
  # Acceptance: grep 'gemma-4-mtp-s4' data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md → ≥1 hit
  ```

### F-12 · MED — entity_model_affinity.yaml names models/providers that don't match the other configs
- **Evidence**: `config/entity_model_affinity.yaml` — `local_deep: qwen3-4b-thinking-q4_k_m @ native-gguf`
  (providers.yaml native-gguf knows `qwen3-4b-thinking-local`; models.yaml puts qwen3-4b-thinking on lmster);
  `__default__.preferred_models.cloud: gemini-3.5-flash @ google` (providers.yaml lists
  gemini-3.5-flash under **antigravity**, not google).
- **Fix**: normalize model-id namespace across the four config files (single registry).
  ```bash
  # Acceptance: every affinity (model,provider) pair resolves in providers.yaml supported_models
  ```

### F-13 · MED — Search-tier config disagrees with MCP config
- **Evidence**: `config/search.yaml:37-46` T3 firecrawl `enabled: true` vs `opencode.json:45-49`
  firecrawl MCP `enabled: false`; T2 exa enabled but `EXA_API_KEY` unset (dead tier);
  `routing.fallback_chain` uses bare integers (`1: 2`) while tiers are named `T0..T3` — ambiguous keys.
- **Fix**: align enabled flags; key the fallback map by tier names.
  ```bash
  # Acceptance: python3 -c "import yaml;s=yaml.safe_load(open('config/search.yaml'));assert all(k.startswith('T') for m in s['routing']['fallback_chain'].values() for k in [m])"
  ```

### F-14 · MED — silent-stall-sensor active but unregistered; plugins carry hardcoded absolute paths
- **Evidence**: `silent-stalls-*.jsonl` written daily Aug 22–25 incl. today 13:02:44Z, yet
  `opencode.json .plugin[]` does not list it. All three plugins hardcode
  `logDir: "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/errors"`
  (M16 portability concern at plugin layer; engine src/ is clean but plugins aren't).
- **Also**: `awareness.ts:103` hardcodes `s.agent === "kali"` for injection target — stale in
  the MaKaLi-orchestrator era (non-kali orchestrators get no awareness injection).
  `error-capture.ts:109` hardcodes `model: "opencode/nemotron-3-ultra-free"` in Hivemind
  notifications — M22 provenance smell (records intent, not actual model).

### F-15 · LOW — providers.yaml internal blemishes
- Typo `native-gguff` (line 26 comment); duplicate priority 4 (google AND google-compat both 4);
  native-gguf `supported_models` advertises `llama-4-scout-local`, `gpt-oss-120b-local`,
  `qwen-3.5-72b-local` etc. that cannot load on this 16GB RAM box whose single `model_path` is
  Qwen3-1.7B-Q6_K.gguf — aspirational roster presented as capacity.

### F-16 · LOW — models.yaml `frontier` role contradicts D-352 routing
- **Evidence**: `config/models.yaml:51-54` — `frontier: provider: google, role: "Kali Grand Oversoul"`
  vs providers.yaml `maakali_routing.kali: prefer native-gguf, fallback antigravity` (D-352/C-5).

### F-17 · LOW — default_agent "kali" vs council topology "MaKaLi top-level"
- **Evidence**: `opencode.json:323` `default_agent: kali`; council-cloud v2.1 deadlock fix made
  makali the top-level orchestrator. Possibly intentional (Architect's interactive sessions are
  kali) — flagged as observation for N9/N6, not a defect claim.

---

## §2 POSITIVE VERIFICATIONS (things that CHECK OUT)

| Claim | Verification |
|---|---|
| M25 streaming sections on all cloud providers | ✅ present for antigravity/google/google-compat/openrouter/opencode-zen/cline/anthropic/xai (providers.yaml) |
| Port consistency hub/searxng/firecrawl | ✅ 8016/8018/8015 agree across omega.yaml, opencode.json, search.yaml |
| SR-V1 `.firecrawl/` cache dir exists | ✅ |
| models.yaml GGUF paths resolve | ✅ Qwen3-1.7B-Q6_K, MiMo-7B-RL, RocRacoon-3b Q4/Q5 all present in OMEGA_MODELS_DIR |
| session_end.py hook quality | ✅ AnyIO-only, atomic tmp→rename write, preserves agent-written proposals, fsync |
| hardware_profile.yaml honesty | ✅ self-documents its contradiction with ARK SS4 zswap claim + provenance note (FP-12 regeneration) |
| council.yaml hardware block | ✅ roughly consistent with hardware_profile.yaml (8 cores/16GB) |

---

## §3 SECURITY BRIGHT LINE DISPOSITION (§C.4)

- **Stale secrets**: F-07 placeholder PATs → FINDING logged, continued. Old backups
  (`.opencode/opencode.json.bak`, `backup.20260809_*`) contain no credential material (spot-checked headers).
- **Active external telemetry**: NONE discovered. Cloud MCP endpoints (exa, parallel-search) are
  on-demand tools, not telemetry channels; `opencode-antigravity-auth` performs local OAuth.
  **No CRITICAL-HALTED.**

## §4 HANDOFF PACKET (Delivered-Home Doctrine)

**Warm-start reading list (in order)**:
1. `opencode.json` (whole file — 324 lines, the spine)
2. `config/providers.yaml` §inference (chain + maakali_routing)
3. `.opencode/plugins/silent-stall-sensor.ts` header comment (lines 1-42) — best doc on what the sensor does
4. `config/council.yaml` + `config/search.yaml` (small, high-drift)
5. `data/coordination/errors/provider-health-2026-08-25.json` (live stall telemetry)

**Standing orders for future councils paging node1 (domain:N1-infrastructure)**:
- NEVER trust a config path until `test -f` passes — this repo renames dirs (`plugin`→`plugins`) without updating referencers.
- Env-probe provider keys (names only) before claiming the fabric works; the paper chain ≠ credentialed chain.
- When instructions and config disagree, log BOTH sides with file:line — the delta IS the finding.
- Open question reserved for @researcher/N6: empirically determine OpenCode's plugin auto-load convention (does `.opencode/plugins/` plural auto-load? did error-capture/awareness ever load?) — decides whether F-01 is "dead tools" or "lying config".

### F-20 · HIGH — `subagent_depth: 2` makes the M11 Reporting Protocol impossible for nodes (DISCOVERED LIVE)
- **Evidence**: `opencode.json:3` sets `"subagent_depth": 2`. Node N1 executes AT depth 2
  (arm→node = two nested task() calls). Final mandate step §C.9 / plan measure M11 requires
  every node to PAGE the Consultant via `task(subagent_type="kali", task_id="ses_…")`.
  Executed live at 2026-08-25T13:16Z → **rejected**: `Subagent depth limit reached (2).
  Increase "subagent_depth" to allow nested subagents.`
- **Impact**: Config-instruction contradiction of the first order: the council's own dispatch
  protocol mandates a mechanism the config forbids at exactly the tier it mandates it for.
  Every N1-N10 node will hit this wall. Arms (depth 1) can still page; nodes cannot.
- **Classification**: Tool-chain failure reported per M23 — NOT silently swallowed. Workaround
  used: failure logged here + Hivemind broadcast; Consultant notification delegated to arm.
- **Recommended fix**: raise `subagent_depth` to 3, OR amend M11/§C.9 so nodes deliver their
  report to their ARM (which pages onward), making the hop rule structural rather than aspirational.
  ```bash
  # Acceptance (option A): jq '.subagent_depth' opencode.json → ≥ 3
  # Acceptance (option B): node packets no longer contain §C.9 paging step
  ```

---

*source_node: N1 | arm: maat | tier: node | raw report written to disk BEFORE digestion per §C.5*
