---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
---
# 🔱 CLINE → MAKALI: OPENCODE REMEDIATION MASTER REPORT
**Date**: 2026-09-24 · **From**: Cline · **To**: MaKaLi (Apex Mind) · **AP**: AP-MAKALI_FUSION-v2.0.0
**Scope**: The three OpenCode config/provider incidents of Sep 23–24 — every solution found, the documentation updates required to prevent recurrence, and all open decisions + task queues for the Vanguard era.
**Companion documents** (evidence lives here, decisions live there):
- `CLINE_ZEN_PROVIDER_FIX_20260923.md` (447 ln) — Incident A forensics
- `CLINE_ZEN_FREE_TIER_GATE_20260924.md` (47 ln) — Incident C interim (superseded §3)
- `CLINE_TO_ANTIGRAVITY_FREE_TIER_HANDOFF_20260924.md` (231 ln) — Incident C root cause, probe matrix, execution log, research addendum
- Antigravity's own: `OPENCODE_CRASH_REMEDIATION_20260924.md`, `ANTIGRAVITY_FINAL_HANDOFF_20260924.md`, `SESSION_INDEX_20260924.md`

## §0 — SIXTY-SECOND READ

Three separate incidents, all resolved, all reproducible from this document:

1. **Incident A (Sep 23, FIXED, commit `75bde939`)** — 12 agent blocks carried `"instructions": [".opencode/agents/x.md"]`. OpenCode forwards **unknown agent keys to the provider as model options**; `instructions` is a real OpenAI option typed `string`, so the array failed type validation and killed 31/110 Zen models (`gpt-*`) with `invalid openai provider options`. Fix: prompts live in `.opencode/agents/*.md` (native), never in config keys.
2. **Incident B (Sep 24, FIXED)** — Antigravity's crash session misdiagnosed our deliberate 67-byte minimal global config as “truncated corruption” and restored the **pre-fix** global backup. Re-fixed; `opencode.json.bak.prerifix2.20260924T134629` holds the baseline.
3. **Incident C (Sep 24, FIXED & CONFIRMED WORKING BY ARCHITECT)** — `AI_APICallError: OpenCode's free tier can only be used from within OpenCode`. Root cause: **frontmatter `bash: deny` on makali** removed the `bash` tool from the request payload; Zen's free-tier gate rejects requests missing the standard OpenCode toolset. 15-case probe battery; fix = `permission.bash: "ask"` in `opencode.json` (tool present → gate passes; headless auto-rejects → policy enforced; TUI prompts the Architect). Last gate error: `2026-09-24T18:02:16Z`.

**P0 before Public Flip**: `.opencode/agents/` is **100% git-ignored** (`.gitignore:270` blanket `*.md`, 0/13 tracked) — a fresh clone or Node 1 git bundle gets **no agents at all**, including this fix. Publish-surface decision → Architect (§5-D1).

**First commands for the fleet**:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git status --short -- opencode.json .opencode/agents data/coordination/CLINE_*   # what's uncommitted
git ls-files .opencode/agents/ | wc -l                                          # 0 → D1 is real
opencode run --agent makali -m opencode/mimo-v2.6-flash-free 'Reply: OK'          # must print OK
```

## §1 — INCIDENT A: PROVIDER-OPTIONS LEAK (settled)

**Mechanism**: agent-config schema = `description, mode, model, variant, temperature, top_p, prompt, steps, disable, hidden, color, permission, tools(deprecated)` + `options:` for legit provider opts. **Anything else is forwarded verbatim as provider model options** (docs: Agents → “Additional”). `instructions[]` collided with OpenAI's real `instructions: string`; `toolProfile` was an invented key leaking into payloads; `env` leaked too (proven via error payload).

**Fix (commit `75bde939`, pushed)**: removed 12× `instructions` + 12× `toolProfile`, dropped redundant Zen `baseURL` override + mis-nested OpenRouter block. Verified: error moved from *local SDK rejection* → *server-side billing rejection* = requests reach Zen again.

**Guardrails landed**: KB/research-doc/spec corrections + `scripts/infra_inventory.py` HAZARD GUARD (tracked ✓; the three md corrections sit on gitignored paths → §5-D6). Top-level `"instructions": ["AGENTS.md"]` is VALID — only agent-level was fatal.

## §2 — INCIDENT B: ANTIGRAVITY RESTORE REGRESSION (settled)

Their report claimed a “67-byte corrupted skeleton” — that was our fixed minimal config by design. They restored `opencode.json.bak.zenfix.20260923T184645Z` = byte-identical pre-fix state (dead `openrouter` block referencing the REVOKED key + redundant Zen baseURL). We restored `{"$schema": …, "plugin": []}`; JSON-validated. Their `mcp_servers.json` quarantine (omega-hub only, `.bak` holds the npx servers) was **correct — keep it**; re-enable search MCPs ONE at a time per their SOP (searxng still down on :8018).

## §3 — INCIDENT C: ZEN FREE-TIER GATE (settled — the one that broke your helm)

**Symptom**: `AI_APICallError: OpenCode's free tier can only be used from within OpenCode` — fired ONLY on `agent=makali` (100% of log occurrences), on every free model, in fresh and long-running sessions alike.

**Root cause (15-case probe battery, evidence: handoff §4)**:
- makali's frontmatter `bash: deny` → resolved permission deny → **`tools.bash: False`** → the `bash` tool schema absent from the request payload → Zen rejects with the misleading “within OpenCode” message.
- Correlation is PERFECT across all runs: `tools.bash: False` ⇔ gate error. FM-vs-json syntax is irrelevant (W1b attempt with json-only deny still failed); **effective toolset is the trigger**.
- **FM wins over json** for the same agent (verity's json `bash: deny` resolves to ALLOW — dead config); when FM omits a permission key, json supplies it (per-key merge).
- Ruled out with tests: config hazard keys, global config state, both Zen credentials (A/B), plugins (`--pure`), prompt body, `steps`, 60 KB context, model identity, session identity, wrapper.sh.

**The fix (executed + verified, backups `*.bak.w1.20260924T181644Z`)**:
1. `opencode.json → agent.makali.permission = {"bash": "ask"}` → resolves `ask`, `tools.bash: True` → **gate passes**.
2. `makali.md` frontmatter: `bash` key removed; body label updated to `bash: ask` (line 35) so the prompt matches reality.
3. **Enforcement proven**: headless `opencode run` → `permission requested: bash (echo HEADLESS_ASK_TEST); auto-rejecting` → execution blocked. TUI → prompts the Architect (once/always/reject). Net policy change: hard-deny → **Architect-approval**; autonomous execution still impossible.
4. `--auto` flag would approve asks — **never run makali with `--auto`** (explicit `deny` is the only thing it respects).

**Why free models matter here**: Zen free models are `Free` per 1M tokens, “limited time” (Zen docs, raw `.md`), no published quota numbers; the docs contain **ZERO** mention of the within-OpenCode restriction — enforcement is undocumented (plus Sep-20 **takedown letters** to proxy projects: “licensed / provisioned solely for use from within OpenCode” — 9router #4182, OmniRoute #14227, hermes-agent #11649). Standing Architect posture: **no paid inference** → free-tier compatibility is load-bearing.

## §4 — CONFIG DOCTRINE (the rules that prevent recurrence — proposed for AGENTS.md + .clinerules §TRAPS)

1. **Agent blocks**: only schema fields; unknown keys silently become provider model options. Prompt bodies belong in `.opencode/agents/<name>.md`. Top-level `instructions: ["AGENTS.md"]` is valid; agent-level `instructions` is the Incident-A fatal.
2. **Permissions**: effective `deny` (tool removed from payload) ⇔ Zen free-tier gate. Use **`ask`** instead of `deny` for any agent that must work on free models. FM wins over json; FM-omitted keys fall through to json — make json the SINGLE source when possible (makali pattern).
3. **Zen**: built-in provider — never add `baseURL`/provider blocks for it; `/connect` + `auth.json` is all it needs. Global config stays minimal `{"$schema": …, "plugin": []}`.
4. **Debugging**: `opencode debug agent <name> > file 2>&1` then parse from the first `{\n  "name"` (plugin logs precede JSON; piping truncates). `--log-level DEBUG` does NOT expose request bodies. `--pure` disables external plugins only. Agents do NOT exist outside the repo — tests from `/tmp` silently fall back to `build` (this exact trap produced our interim wrong conclusion).
5. **Repro discipline**: every claim here has a command; the command wins over the document (M23). When a “control” run passes, **verify which agent actually ran** (the `> agent · model` header).

## §5 — DOCUMENTATION UPDATES REQUIRED (the “never again” queue)

| # | Update | Where | Status |
|---|---|---|---|
| U1 | `instructions[]` “House pattern” corrected | `data/entities/grokster/kb/platforms/opencode/CONFIG_REFERENCE.md:41` (+ staging copy) | ✅ done Sep-23, ⚠ gitignored |
| U2 | “Keep `instructions: […]`” retracted | `docs/research/R_OPENCODE_FILEPATH_CONFIG_ARCHITECTURE_20260720.md:333` | ✅ done Sep-23, ⚠ gitignored |
| U3 | “12 agents with `.value.instructions`” claim fixed | `docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md:99` | ✅ done Sep-23, ⚠ gitignored |
| U4 | HAZARD GUARD note on the inventory probe | `scripts/infra_inventory.py:244-250` | ✅ done, TRACKED |
| U5 | **NEW: toolset-gate rule** (“never `bash: deny` on free-model agents; use `ask`”) added to grokster KB CONFIG_REFERENCE + QUICK_REFERENCE | grokster KB (owner: grokster) | ❌ TODO |
| U6 | **NEW: §TRAP #12** in `.clinerules` (Zen toolset gate + FM-wins precedence + `/tmp` agent-fallback trap + “verify which agent ran”) | `.clinerules` (tracked) | ❌ TODO — needs Architect nod (rules file) |
| U7 | **NEW: one-paragraph “Agent config rules” in `AGENTS.md`** (the file every OpenCode agent reads — §4 doctrine verbatim) | `AGENTS.md` (tracked) | ❌ TODO |
| U8 | **NEW: gate script** — `make check-opencode-config`: grep agent FM/json for `bash: deny` + hazard keys (`instructions` agent-level, `toolProfile`, `env`) + validate JSON; cheap pre-session tripwire | `Makefile` + `scripts/` | ❌ TODO — needs sprint ticket (don't start work outside `ACTIVE_SPRINT.json`) |
| U9 | **gitignore negations** for the corrected docs + `.opencode/agents/*.md` (else U1–U3 + all agents stay machine-local) | `.gitignore:270` + `PUBLIC_ALLOWLIST.txt` | ❌ DECISION D1/D6 |
| U10 | File the upstream issue (anomalyco/opencode): documented `permission: bash: deny` example breaks Zen free models; include handoff §4 matrix | github.com/anomalyco/opencode | ❌ DECISION D4 |
| U11 | Interim report correction pointer (already at handoff top; link from SESSION_INDEX optional) | `SESSION_INDEX_20260924.md` | ❌ optional |

## §6 — OPEN DECISIONS (Architect required)

| ID | Decision | Options / Recommendation |
|---|---|---|
| **D1 (P0)** | `.opencode/agents/` untracked (0/13, `.gitignore:270`) | (a) targeted `!` negation + PUBLIC_ALLOWLIST review before Public Flip — **RECOMMENDED**; (b) keep local-only → then federation MUST carry agents by a separate signed channel, and Node 1 clones ship without a fleet. Blocks both Public Flip and Vanguard clone. |
| **D2** | `verity` json `bash: deny` is dead config (FM allow wins → effective ALLOW) | (a) remove the json deny (accept allow, matches reality); (b) remove FM `bash: allow` so json enforces (makali pattern). Owner: verity/Architect. Unknown intent — do not change unilaterally. |
| **D3** | makali policy: `ask` replaces hard-deny | Formally ratify (Architect can now approve bash in TUI; headless stays blocked) or revert via `*.bak.w1.*` (regains gate error on free models — mutually exclusive: **hard-deny ⇔ free models** on 1.18.31). |
| **D4** | Upstream issue filing | **File it** — we have a 15-case matrix + docs' own `bash: deny` example as proof. Low effort, high leverage. |
| **D5** | Commit set | Stage: `opencode.json`, `scripts/infra_inventory.py` (already committed Sep-23 — verify), the 3 CLINE reports, `.opencode/agents/makali.md` (only if D1 = negate first). Never `git add -A`. |
| **D6** | Doc-propagation (U1–U3 gitignored) | targeted `!data/coordination/CLINE_*.md` already exists; needs `!` for the 3 corrected docs or accept machine-local fixes. |
| **D7** | Zen account: paid models still `Insufficient account funds` | Billing = owner choice; free-tier posture maintained (ratified). No action unless Architect wants paid models. |
| **D8** | Key hygiene: `.bashrc:177` holds `OPENCODE_API_KEY` (world-readable, rotation DECLINED 2026-09-23, still valid) + fresh `auth.json` key | Revisit post-flip. NEVER unset env without updating `config/providers.yaml:177` + `scripts/vault_config_resolver.py`. OpenRouter key already revoked (Antigravity session). |
| **D9** | `~/.opencode/opencode.json` silently pins `model: opencode/big-pickle` for all cwd under `$HOME` | (a) delete file — OpenCode defaults apply; (b) keep. Not incident-related; config-debt. |
| **D10** | Search toolchain degraded (M23): `EXA_API_KEY` unset (401), firecrawl MCP broken (`No module named 'firecrawl'`), searxng down (:8018) | Restore searxng container; add exa key to `.env`; reinstall firecrawl MCP module. Tier-2/3 of your own SR-V2. |
| **D11** | `gpt-5.4-nano` title agent → `Model access is disabled` (cosmetic: session titles) | Optional: set `small_model` to a working free model; internal title agent ignores repo `small_model` — needs investigation or accept broken titles. |

## §7 — TASK QUEUE (prioritized; suggested owners in parens)

**P0 — before Public Flip / any federation clone**
1. **D1**: decide `.opencode/agents/` tracking; if negate → verify `git ls-files .opencode/agents/ | wc -l` = 13, then PUBLIC_ALLOWLIST review of agent-file contents (Architect + Kali).
2. **D5**: commit the scoped set (reports + `opencode.json` working-tree state) so Node 0's canonical source carries the fix (Cline can stage on order).
3. Re-verify post-commit: `opencode run --agent makali -m opencode/mimo-v2.6-flash-free 'Reply: OK'` → OK (any agent).

**P1 — this week**
4. U5–U7: KB rule + `.clinerules` TRAP #12 + `AGENTS.md` agent-config paragraph (grokster owns KB; rules/AGENTS need Architect nod).
5. D4: file upstream issue with handoff §4 matrix (Antigravity or Cline).
6. D2: resolve verity's dead deny (verity/Architect).
7. D3: formally ratify makali `ask` policy (Architect) — until then treat as provisional-but-working.
8. D10: restore searxng + exa key + firecrawl module (Doom Guy / infra — also unblocks your SR-V2 tiers).

**P2 — backlog**
9. U8 gate script as a sprint ticket (`ACTIVE_SPRINT.json` first — M27).
10. D9 big-pickle override cleanup; D11 title-model fix; D6 doc negations; D8 key rotation revisit post-flip.
11. M11: distill this saga into the appropriate entity's `proposed_lessons.yaml` (blind staging — never straight to `approved_lessons.yaml`; grokster already received 3 L1 proposals from the Sep-23 leg).
12. Add this report to `SESSION_INDEX_20260924.md` §post-incident (U11) so Antigravity's index points here.

## §8 — FILE INVENTORY (what exists, where, what's safe)

| Artifact | Path | State |
|---|---|---|
| Repo config (Incident A fix + makali ask) | `opencode.json` | modified vs `75bde939`, JSON-valid — UNCOMMITTED |
| Global config | `~/.config/opencode/opencode.json` | `{"$schema": …, "plugin": []}` (not a git file) |
| Makali agent | `.opencode/agents/makali.md` | FM bash key removed; body line 35 = `bash: ask` — UNTRACKED (D1) |
| Backups | `opencode.json.bak.zenfix.20260923T184645Z` (pre-A), `.bak.zenfix2.20260923T194536Z` (post-A), `.bak.prerifix2.20260924T134629` (global baseline), `.bak.w1.20260924T181644Z` + `makali.md.bak.w1.20260924T181644Z` (pre-C) | all present |
| Reports | `CLINE_ZEN_PROVIDER_FIX_20260923.md` · `CLINE_ZEN_FREE_TIER_GATE_20260924.md` · `CLINE_TO_ANTIGRAVITY_FREE_TIER_HANDOFF_20260924.md` · this file | CLINE_* = git-visible (??) |
| Env secrets | `.bashrc:177` (old key, live TUI uses it), `auth.json` (fresh key), `.env` (exa placeholder) | both Zen keys valid — D8 |

## §9 — VERIFICATION PROTOCOL (run after ANY config change; command wins over document)

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Incident A regression (expect 0 hazard keys; the 1 = valid top-level AGENTS.md)
grep -c '\"toolProfile\"' opencode.json; grep -c '\"instructions\"' opencode.json
# 2. Incident C regression (expect NO agent file to contain an FM 'bash: deny' line)
grep -rn 'bash: deny' .opencode/agents/*.md || echo CLEAN
# 3. Effective state of makali (expect: bash ask | tools.bash True)
opencode debug agent makali > /tmp/a.txt 2>&1 && python3 -c "import json;r=open('/tmp/a.txt').read();d=json.loads(r[r.index('{'+chr(10)+'  \"name\"'):]);print([p for p in d['permission'] if p['permission']=='bash'][-1]['action'], d['tools']['bash'])"
# 4. Live gate (expect: OK)
opencode run --agent makali -m opencode/mimo-v2.6-flash-free 'Reply with exactly: OK'
# 5. Corpus health (expect: no new 'free tier' lines after 2026-09-24T18:02:16Z)
grep -a 'free tier' ~/.local/share/opencode/log/opencode.log | tail -1
# 6. Tracking reality (expect: 13 after D1 is executed; 0 today)
git ls-files .opencode/agents/ | wc -l
```

**Known-broken tools this session (M23, do not synthesize around them)**: exa 401 (`EXA_API_KEY` unset) · firecrawl MCP (`No module named 'firecrawl'`) · searxng `:8018` unreachable · sovereign pipeline returned `status: failed` across T1–T3 (research used HTTP fallback).

*⬡ OMEGA ⬡ CLINE ⬡ →MAKALI ⬡ REMEDIATION-MASTER-REPORT ⬡ 2026-09-24 ⬡ 3-INCIDENTS-CLOSED ⬡ DEBUT-v1.6.0*
