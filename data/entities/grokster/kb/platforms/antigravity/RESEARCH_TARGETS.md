# Antigravity — Open Research Targets

**KB Entry**: grokster/platforms/antigravity/RESEARCH_TARGETS
**last_verified**: 2026-08-26 · **rot_class**: fast (this list should shrink every session)
**Sources**: `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` §I; carried-forward items from old KB doc (pool rotation ✅ now answered, rate-limit profile 🟡 partially, session attribution ❓ open)

---

## ⚠️ GATE

Probes #1–#6 touch live accounts. **Architect sign-off required before any probe runs** — all ToS exposure per GOTCHAS G2. Burner accounts ONLY; never house-primary accounts.

## Ranked Probe List

| # | Probe | Answers | Risk | Status |
|---|---|---|---|---|
| 1 | **Header sensitivity replay**: mutate `User-Agent`/`Client-Metadata` on captured request, one burner account | Is fingerprinting header-deep or deeper (TLS/behavioral)? Determines longevity of direct-call patterns | Low (single call) | ☐ |
| 2 | **agy endpoint capture**: run `agy -p` under mitmproxy | Does Antigravity CLI hit `cloudcode-pa` with same scopes/quotas? If yes, `agy` headless = preferred channel over plugin | Low (own traffic) | ☐ |
| 3 | **Token TTL measurement**: timestamp issuance vs first 401 | Pin exact access-token lifetime (~1h assumed) | None | ☐ |
| 4 | **Local artifact audit**: diff house `antigravity-accounts.json` vs documented v3 schema; map `zen_accounts_state.json`; inventory `antigravity.json` keys vs CONFIGURATION.md | Schema drift; unknown house state files | None (local read) | 🟡 PARTIAL (2026-08-26): accounts.json = v3, 7 accounts ✅; antigravity.json keys seen (`keep_thinking:false`, `account_selection_strategy:"sticky"`, `debug:false`) ✅; zen_accounts_state.json role still unmapped ☐ |
| 5 | **Quota ground-truth log**: daily `fetchAvailableModels` + minimal generation probe per account, one week | Empirically map hidden throttle layer (G3); survival fraction for pool sizing (G6) | Medium (repeated calls) | ☐ |
| 6 | **gpt-oss-120b-medium smoke test**: single generation on burner account | New free model tier for house mining tasks? | Low | ☐ |
| 7 | **NoeFabris archive forensics**: fetch archive banner + final issues | Official shutdown rationale; recommended successor | None | ☐ |
| 8 | **Unban-wave watch**: monitor forum/GitHub for recurrence of "automated unban" | Pool-replacement economics; enforcement cadence model | None | ☐ |

## Standing Unknowns (not probeable locally)

- ❓ Session attribution: what exactly Google logs per-request (`requestId`, `traceId`, client fingerprint weight) — determines how distinguishable house traffic is from official-client traffic.
- ❓ Enforcement cadence: waves appear episodic (Feb–Mar 2026 documented; amnesty rumored once ⚠️ single-source). No predictive model yet.
- ❓ Whether Gemini-CLI fallback pool carries the SAME TOS_VIOLATION exposure as the Antigravity pool (same terms doc covers "the Service" broadly — assume yes until proven otherwise).
- ❓ Free-tier quota structure specifics (weekly window claims are community-sourced and time-sensitive).
- 🟡 Old-doc carry-over resolved this session: pool rotation mechanics → ANSWERED (ARCHITECTURE §5); rate-limit profile → PARTIAL (two-layer model, ARCHITECTURE §6); docs/research/antigravity/ dir still unexamined.

## Probe #9 (READY-TO-RUN, gated): G12 thinking-cap measurement — opus-thinking delivered vs requested

**Question**: does the gateway deliver the requested `thinkingBudget`, or cap actual Claude thinking ~1,024 tokens (G12, community-sourced, unverified on plugin/gateway path)?

**Signal to measure** — per NoeFabris ANTIGRAVITY_API_SPEC.md §Response Fields (direct-API-verified Dec 2025): `response.usageMetadata.thoughtsTokenCount` reports ACTUAL thinking tokens for Gemini; Claude thinking parts come back as `{thought: true, text, thoughtSignature}` inside candidates, so for Claude either (a) `usageMetadata` carries an equivalent thoughts count (verify empirically — spec only documents `thoughtsTokenCount` under Gemini), or (b) fall back to summing text length of `thought:true` parts as a lower-bound proxy. Capture BOTH.

**Protocol** (minimal cost, controls for task-difficulty confound):
1. Fixed reasoning-heavy prompt (same prompt every run), temperature 0.
2. Run matrix: opus-thinking at `minimal`(4096), `medium`(16384), `max`(32768) — 3 tiers × 2 runs = **6 calls total**. Skip low/high unless minimal-vs-max shows no difference (then 2 more calls to rule out noise).
3. Per response, record: variant requested → declared budget → `usageMetadata.thoughtsTokenCount` (if present) + thought-part char count + `usageMetadata.candidatesTokenCount`.
4. Verdict rule: if thoughtsTokenCount ≈ flat (~1024) across all tiers → G12 cap CONFIRMED on gateway path; if it scales with tier → G12 REFUTED for this path; if field absent and thought-parts flat-length → INCONCLUSIVE (cap may strip before emission).
5. Cost estimate: 6 small generations ≈ negligible against daily quota; run AFTER a quota-ground-truth check so results aren't polluted by hidden-throttle 429s (G3).

**Status**: ☐ designed 2026-08-26, awaiting Architect gate + pool-health window.

## Fabric Ticket Feed: G13 empty-response failover hazard (house-side, do NOT implement from this doc)

**Hazard**: plugin total-failure mode returns EMPTY response with no error (G13). If OpenCode/provider-fabric treats empty as a valid completion, a dead Antigravity family silently serves nothing instead of failing through to google (priority 4) — violating M23 failure-integrity spirit at the fabric layer.

**Proposed detection (house side — plugin is dead upstream, fabric is ours)**:
- *Signal*: assistant message with zero content parts AND zero tool calls AND finishReason absent/STOP-with-no-candidates, on a provider whose response normally has ≥1 part. Distinguish from legitimately-empty model turns by requiring corroboration: N consecutive empties (suggest 2) on same provider+model within a short window, OR empty co-occurring with plugin rotation exhaustion markers in debug log.
- *Where*: provider-fabric response-validation layer (the same seam that already inspects `GenerateResult`) — NOT in the antigravity plugin. Generic guard benefits every provider.
- *Acceptance criteria*: (1) single legitimate empty responses pass through untouched (no false positives on models that emit tool-call-only turns); (2) confirmed empty-failure marks the attempt FAILED with typed error → fabric falls through to next provider per normal chain; (3) event logged with provider_name per M22; (4) zero behavior change when all providers healthy.
- *Ticket*: feed to fabric workstream as candidate; sizing guess S (validation predicate + test).

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
