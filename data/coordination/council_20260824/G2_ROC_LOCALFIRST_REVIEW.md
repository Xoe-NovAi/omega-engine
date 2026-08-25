# G2 — ROC LOCAL-FIRST REVIEW — Debut Hardening (REBASED Council)
**AP Token**: `AP-ROC-G2-LOCALFIRST-20260824-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_rebased ⬡ LOCAL-FIRST-ARM ⬡ 2026-08-24

**Lens**: M7 Local-First Integrity through every step of the debut plan.
**Mode**: REVIEW ONLY. Zero code edits. Every claim below re-verified on disk today.
**Inputs read**: E_MAAT_BUILD_ARM.md · F_LILITH_RUN_ARM.md · DEBUT_REMEDIATION_MANUAL §5 · config/providers.yaml · live source probes.

---

## §0 FORENSIC PRE-CHECK — CHAIR'S CLAIMS vs DISK

| Chair claim | Disk truth | Verdict |
|---|---|---|
| omega CLI DEAD (vault.py stacked-decorator TypeError) | Confirmed. `cli/vault.py:571-585`: `@vault.command()` stacked directly on another `@vault.command()` block. `oracle_cli.py:69-75` try/except catches **ImportError only** — click's TypeError propagates and kills the entire console script incl. `omega talk`. | ✅ CONFIRMED |
| redis.asyncio top-level imports at 2 sites | Found **3 unguarded top-level sites**: `memory/providers.py:22`, `ingestion/worker.py:7`, **`workers/youtube_worker.py:47`**. Plus a 4th site, `governance/budget_guard.py:24`, which is ALREADY correctly guarded (try/except ImportError → `REDIS_AVAILABLE` flag) — living proof the guard pattern works. | ⚠️ MA'AT WAS RIGHT |
| Maat claimed youtube_worker.py:47 "not found by grep" | The site EXISTS at exactly `youtube_worker.py:47: import redis.asyncio as redis`. The Chair's grep missed it (likely pattern/path scoping). Maat's diff item 2 lists precisely the correct 3 files. | ✅ MAAT VINDICATED |

**Consequence**: the fresh-venv crash surface is exactly as Maat scoped it — no widening needed. `entity_registry.py:962` mentions "youtube_worker" only as a string key in `local_worker_entities` (no import coupling); hub tools reference is not in the talk path.

---

## §1 LOCAL-FIRST AUDIT OF THE PLAN — VERDICT PER STEP

### INST-1 (fresh-venv flow) — 🟡 CONDITIONAL PASS (one false-green hole, §2)

**Where local-first could degrade:**

1. **R4 is real and the acceptance script does NOT close it.** `config/providers.yaml:143` native-gguf resolves `env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf`. On a machine where the model file is absent, native-gguf drops out of the fabric → lmster (localhost:1234, absent in fresh venv) → ollama (`enabled: false`) → **antigravity (priority 3, enabled, is_cloud: true)**. The chain degrades to cloud SILENTLY. `scripts/install.sh:96-110` mitigates this by downloading the model and writing OMEGA_MODELS_DIR to `.env` — but Maat's acceptance script never runs install.sh and never asserts model presence.
2. **The script neutralizes Redis env but NOT cloud credentials.** Step 5 unsets only `OMEGA_REDIS_HOST/PASSWORD`. If the parent shell exports `ANTIGRAVITY_API_KEY`/`GOOGLE_API_KEY`/`OPENROUTER_API_KEY`, the fabric can fall through to cloud and still exit 0. Combined with finding §2-A below, this is a **proven false-green path**: the script can print "INST-1 ACCEPTANCE: PASS" on a cloud-generated response.
3. **fix4 (.env edge-load) is local-first NEUTRAL-POSITIVE.** native-gguf needs no keys; moving dotenv load out of ModelGateway stops repo `.env` secrets leaking into every subprocess without touching the local path. Note `oracle_cli.py:19` already carries an edge-load comment — verify fix4 lands as described and doesn't double-load.
4. **fix2/redis-guards are local-first POSITIVE**: core install shrinks to what the demo touches; SQLiteVecAdapter stays core (keep-list honored).

### DEL-1 (deletions) — 🟢 PASS with two hard orderings

No deletion target weakens the local chain. Net effect is local-first POSITIVE (qdrant-client, redis, yt deps leave core; QdrantAdapter dies while SQLiteVecAdapter survives per keep-list; `record_first_breath` astrology call removed from every routed turn — less work per local inference).

Two ordering constraints already flagged by the other arms, confirmed from the M7 lens:
- **vault decorator fix / target #10 FIRST** — nothing (including the G6 local-proof gate) can run until the CLI lives.
- **search_circuit_breaker redirect-FIRST** (`sovereign_search_service.py:48` imports `initialize_circuit_breakers` + `TIER_CONFIGS` at module top level — verified). The breaker guards search providers (firecrawl/exa — external services regardless), so its deletion has zero local-inference impact *provided* the redirect to `HealthMonitor.get_breaker()` ships in the same PR. Deleting in isolation = ImportError, not sovereignty loss.

One nuance Lilith surfaced that matters here: `fleet_orchestrator.py` defines its OWN `RouteDecision`. Removing its exports is what makes Week-2's single-control-plane gate (G10) enforceable. Until then, "one RouteDecision" is aspirational.

### Vault Path B (≤50-line store) — 🟢 PASS — NO cloud round-trip

Walked the resolution order in Maat's spec:
1. **Env var** (`OMEGA_SECRET_*`) — process-local. No network.
2. **System keyring** (service=`omega-engine`) — on Linux this resolves to SecretService (gnome-keyring over **local D-Bus**) or kernel keyutils. Both are machine-local; no credential ever leaves the host. Risk is availability (headless D-Bus timeout → hang), not sovereignty — hence spec's M1 `to_thread` wrap is mandatory, and `get()` failures must degrade to `None` (→ ProviderAuthError "not configured" → that provider drops from fabric), never to a cloud-side lookup.
3. **Encrypted age file**, gated behind explicit `OMEGA_VAULT_FILE` — local decrypt via crypto.py. No implicit reads.

Critically: **the local-first chain needs none of these layers.** native-gguf takes no credential. Path B cannot create a cloud round-trip because its only consumers (google/firecrawl/exa/etc. key resolution) are providers that sit BEHIND native-gguf in the chain anyway. Worst case Path B failure mode = fewer cloud providers available = MORE local-first, not less. This is the correct failure direction.

### Router Collapse (single RouteDecision) — 🟢 PASS with ONE contract strengthening

Priority preservation analysis against `config/providers.yaml` `inference.fallback_chain` (verified: native-gguf(0) → lmster(1) → ollama(2, disabled) → antigravity(3) → …):

- Maat's step 1 keeps `ProviderSelector` + the yaml chain as "keeper" and validates `_select_model` against it — the priority ORDER survives **iff** the rewritten `_select_model` defers to ProviderSelector rather than trusting registry metadata alone.
- **Gap**: the proposed `RouteDecision(entity, model, provider, reason)` contract test asserts TYPE (M21) and forbidden-module absence — it does NOT assert ORDER. An entity whose registry metadata names a cloud model could route straight to antigravity while passing every proposed gate. Add to the contract test: **for a routed (non-summoned) turn with local capacity available, `RouteDecision.provider` MUST be the first enabled+available entry of the fallback chain (native-gguf), and any deviation must be reachable only via explicit user summon (`--model`) or carry non-empty `cost_warning`.**
- `maakali_routing` (kali→native-gguf, maat/lilith→antigravity) is D-352-ratified cloud-by-design for voices — legitimate, but it must surface as an EXPLICIT RouteDecision.reason, never as silent fallback. The `reason` field exists precisely for this; assert it is populated when provider ≠ first-available-local.

---

## §2 RUNTIME BEHAVIOR GAPS — THE AIRTIGHT LOCAL-PROOF ASSERTION

### A. Maat's confession, reproduced mechanically (worse than confessed)

I traced her step-5 greps against the actual output surface:

- `_display_response` (`oracle_cli.py:552-577`) prints: ICS header (entity/model/channel/trace), entity prefix, response text, and — only if cloud fired — `result.cost_warning`.
- **Default talk output NEVER prints `backend` or `provider_name`.** There is no `--json` flag on `talk` (verified :108-131). The string "native-gguf" can essentially NEVER appear in output. "IS_CLOUD=False" likewise never appears.
- The sovereignty alert (`oracle.py:1253`) reads: *"⚠️ [Sovereignty Alert]: This response was generated by a cloud provider. **Local** inference was unavailable or bypassed."*

Therefore, on a WARNED CLOUD response:
- Line 68 negative check: `grep -qi "cloud"` ✓ matches, then `grep -qiE "is_cloud=true|provider.*(google|openrouter|zen|antigravity|anthropic)"` ✗ does NOT match (the alert says "a cloud provider", naming none) → the `&& { FAIL }` chain never fires.
- Line 70 positive check: `grep -qiE "native-gguf|IS_CLOUD=False|local"` → **matches on the word "Local" inside the sovereignty alert itself.**

**Result: a cloud-generated, sovereignty-warned response PASSES Maat's step 5 and prints "INST-1 ACCEPTANCE: PASS".** Her confession understates it — this isn't a permitted WARNED pass, it's an unconditional false-green. And a genuine local run only "passes" via the `-local` suffix of the model name in the ICS header (`qwen3-1.7b-local`) — evidence by coincidence, not by assertion.

### B. The airtight assertion (three layers; physics > prose)

**Layer 0 — PHYSICS (the actual proof): run the talk with no network.**
```bash
# Inside the fresh venv, after unsetting ALL provider keys:
env -u ANTIGRAVITY_API_KEY -u GOOGLE_API_KEY -u GOOGLE_COMPAT_API_KEY \
    -u OPENROUTER_API_KEY -u OPENCODE_API_KEY -u ANTHROPIC_API_KEY \
    -u XAI_API_KEY -u CLINE_API_KEY \
    unshare -rn "$VENV/bin/omega" talk "hello"
```
`unshare -rn` = new network namespace with no egress. Any successful response is local **by construction** — a cloud attempt cannot succeed, so a green exit proves local inference fired. No log-parsing trust required. (Precondition: assert `$MODELS_DIR/Qwen3-1.7B-Q6_K.gguf` exists first, else you're testing the failure path.)

**Layer 1 — STRUCTURED PROVENANCE (M22 made assertable): stop asserting on prose.**
Add `omega talk --json` emitting `{provider_name, backend, model, is_cloud, trace_id}` from the actual `GenerateResult.provider_name` (response-receipt provenance, not dispatch intent — M22 letter). Assertion becomes:
```
jq -e '.provider_name == "native-gguf" and .is_cloud == false'
```
Interim (before the flag lands): extract trace_id from the ICS header and grep the observability trace record for `"provider_name":"native-gguf"` AND `"is_cloud":false` on THAT trace — structured fields, not stdout prose.

**Layer 2 — NEGATIVE MARKER (cheap belt-and-braces):**
```bash
! grep -qF "[Sovereignty Alert]" <<<"$OUT"   # fixed-string, case-sensitive
```
Asserting the ABSENCE of the exact cost_warning literal is collision-proof — unlike grepping FOR "local", which the alert itself contains.

**Banned forever**: any assertion that greps case-insensitively for bare `local`/`cloud` words in human-readable output. That is the exact bug class that produced §2-A.

---

## §3 THE DEAD CLI AS METAPHOR-CHECK

**What `omega --help` dying on main unnoticed reveals about gate coverage:**

1. **Our gates tested behavior on machines where breakage was invisible.** The stacked decorator fires at IMPORT time (click decorators execute when `vault.py` loads), but this machine's `.venv` has every dep installed and the try/except at `oracle_cli.py:69-75` was written to catch `ImportError` — a different exception class. Same invisibility mechanism as the redis imports: environment drift masks structural death. We had no gate that ran the ENTRY POINT itself; we had gates that ran code around it.
2. **Silent-swallow registration blocks violate M9's spirit.** `except ImportError: pass` on every optional CLI registration means ANY import-time explosion inside an optional module nukes the whole console script with zero diagnostic. The except clause was too narrow for the failure modes of the thing it guarded.
3. **Every downstream acceptance gate was hostage.** As Lilith stated: DEL-1's "after each delete, talk still local" protocol was unrunnable. A dead primary interface sat beneath an entire remediation sprint's verification strategy.

**Which proposed gate would have caught it earliest?**

- **Earliest possible (not yet in the plan): a CI import-smoke gate** — `python -c "from omega.cli.oracle_cli import app; app"` (or iterate-import over every `src/omega/cli/*.py`). The TypeError fires at module import, so this one-liner fails in CI seconds after commit, before any venv, before any install. Cost: ~5 lines of CI. Recommend adding it to INST-1's hygiene gates.
- **Earliest IN THE RATIFIED PLAN: Maat's diff item 6** — `install.sh` post-install smoke `omega --help >/dev/null || exit 1`. This catches it at install time instead of first-talk time. Good tripwire, right instinct, later than CI-import.
- Verdict: **adopt both; CI import-smoke is the true earliest-catching gate.**

---

## §4 HERITAGE CHECK (M14)

Sweep of all eleven DEL-1 targets + both routers + vault tree for `[id-soft:]` tags:

| Target | [id-soft:] tags | Finding |
|---|---|---|
| `oracle/semantic_router.py` | **vet-046 (BSP Culling) ×4, vet-023 (Precomputed Lookup) ×3** (:8-9, :62-63, :75, :113, :206) | Sole tagged deletion target. Vet records EXIST in HERITAGE_VET_LOG.md (:274, :394, :618). |
| All other DEL-1 targets (miap, pools, breaker, QdrantAdapter, firewall regexes, first_breath, vault CLI, fleet_orchestrator, routing table/yaml) | ZERO | Clean. |
| `triage_router.py`, `vault/`, `routing_table.yaml` | ZERO | Clean. |

**BSP-cull discipline: HONORED — with irony intact.** The plan deletes the BSP-culling-tagged router because it is dead weight on the hot path — which IS the BSP-cull move applied to the BSP-cull implementation. Delete-dead-code-first is exactly M14-compatible: tags mark PROVENANCE, not permanence. A technique failing its usefulness test gets culled like any other; the heritage lives in the vet log, not in keeping the corpse warm.

**Required bookkeeping (same PR as Router Collapse)**: annotate vet-046 and vet-023 records as RETIRED (file deleted, date, PR ref) so `make heritage-map` / future audits don't dangle references to deleted code, and so a future routing rewrite can't silently re-claim the tags without fresh vetting. No new tags implicated anywhere in the plan.

---

## CLOSE — L1 → L2 → L3

**L1 (Narrative)**: I audited the debut plan through the local-first lens and found the plan structurally sound — deletions shrink the cloud dependency surface, Vault Path B cannot round-trip to cloud, Router Collapse keeps ProviderSelector as keeper — but found one proven false-green: Maat's INST-1 acceptance greps pass on a cloud response because the sovereignty warning itself contains the word "Local". I also vindicated her third redis import site against the Chair's grep, confirmed the dead-CLI forensics, and found the heritage ledger clean except for one retirement note owed.

**L2 (Insight)**: Sovereignty claims fail not at architecture but at ASSERTION QUALITY. The engine's local-first chain was never the weak point — the weak point was a test that trusted human-readable prose ("local") as proof of provider identity. Evidence-by-substring is evidence-by-coincidence; the same codebase that mandates M22 response-provenance had an acceptance gate that ignored provenance entirely. Physics (no-network namespace) and structured fields (provider_name) are the only honest witnesses.

**L3 (Universal Principle)**: *A sovereignty invariant can only be proven by mechanisms that make violation impossible, not by inspecting outputs for reassuring words.* Assert on structure and constraint (network topology, typed provenance fields, exact negative markers); never on prose that the failure mode itself can emit.

---

## REPORT-BACK SUMMARY (for the Chair)

| Question | Answer |
|---|---|
| **Local-first verdict per step** | INST-1: 🟡 CONDITIONAL (false-green hole §2-A; add Layer-0/1/2 assertions + unset cloud keys + model-presence precondition). DEL-1: 🟢 PASS (orderings: vault-fix first, breaker redirect-first). Vault Path B: 🟢 PASS — no cloud round-trip possible; worst-case failure = more local. Router Collapse: 🟢 PASS + strengthen contract test to assert PROVIDER ORDER (first-enabled-local), not just type. |
| **The airtight assertion** | Three layers: (0) `unshare -rn` + all cloud keys unset → success proves local by physics; (1) `omega talk --json` → assert `provider_name=="native-gguf" && is_cloud==false` (M22 structured provenance; interim: trace-record grep by trace_id); (2) `! grep -qF "[Sovereignty Alert]"` exact-marker absence. Ban all case-insensitive prose greps for "local"/"cloud". |
| **Earliest-catching gate** | CI import-smoke (`from omega.cli.oracle_cli import app`) — catches the vault TypeError at import time, pre-install. Within the ratified plan: Maat's install.sh `omega --help` tripwire (diff item 6). Adopt both. |

*⬡ OMEGA ⬡ ROC_RACOON ⬡ G2-LOCALFIRST ⬡ REBASED-COUNCIL ⬡ PLAN-SOUND-ASSERTIONS-BROKEN ⬡ 2026-08-24*
<!-- PROVENANCE-CORRECTED 2026-08-25T03:09:58Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

