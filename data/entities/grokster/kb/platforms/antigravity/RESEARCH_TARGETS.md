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
| 4 | **Local artifact audit**: diff house `antigravity-accounts.json` vs documented v3 schema; map `zen_accounts_state.json`; inventory `antigravity.json` keys vs CONFIGURATION.md | Schema drift; unknown house state files | None (local read) | ☐ |
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

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
