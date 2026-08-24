# 🔱 Antigravity CLI — Unknowns & Gaps

**AP Token**: `AP-ANTIGRAVITY-GAPS-v2.0.0`
⬡ OMEGA ⬡ HECATE ⬡ research-fleet ⬡ antigravity ⬡ trc_antigravity_gaps_v2

**Last Updated**: 2026-05-22

---

## §1 Resolved Unknowns (Live Testing — 2026-05-22)

### Installation & Setup

| ID | Question | Result | Confidence |
|----|----------|--------|------------|
| **U1** | Does the installer work on this system? | ✅ **YES** — Binary at `~/.local/bin/agy`, v1.0.1 | HIGH |
| **U2** | Does OAuth work via Linux libsecret? | ✅ **YES** — Authenticated as `taylorbare27@gmail.com` | HIGH |
| **U5** | What is the binary size? | ✅ **175 MB** | HIGH |
| **U6** | Does `--version` exist? | ✅ **No `--version` flag**; version obtained via `--help` footer = 1.0.1 | HIGH |

### Feature Verification

| ID | Question | Result | Confidence |
|----|----------|--------|------------|
| **F1** | Can `agy` accept piped input? | ✅ **YES** — `echo "prompt" \| agy --print` works | HIGH |
| **F3** | Can `agy` accept direct argument prompts? | ✅ **YES** — `agy --print "prompt"` works | HIGH |
| **F10** | Can CLI run in headless (non-interactive) mode? | ✅ **YES** — `--print` flag confirmed | HIGH |

### Quota System

| ID | Question | Result | Confidence |
|----|----------|--------|------------|
| **Q1** | What is the exact per-model quota on Pro plan? | ✅ **ALL PREMIUM EXHAUSTED** — 166h reset. Only Flash likely functional. | HIGH |
| **Q2** | Is the "2 prompts → quota exhausted" issue reproduced? | ✅ **CONFIRMED** — On this account with Opus selected. | HIGH |
| **Q3** | Does `/usage` show time-until-reset? | ✅ **YES** — Log shows `Resets in 166h28m35s` | HIGH |

### Ecosystem

| ID | Question | Result | Confidence |
|----|----------|--------|------------|
| **M3** | Are all 5 models available on Pro? | ✅ **YES** — All listed; all premium exhausted | HIGH |
| **T1** | When does Gemini CLI sunset? | ✅ **June 18, 2026** | HIGH |

---

## §2 Still-Unresolved Unknowns

### P0 — Blocks Integration

| ID | Question | Effort | How |
|----|----------|--------|-----|
| U3 | Does `ANTIGRAVITY_API_KEY` env var work for headless auth? | 15m | Test with env var set vs current keyring flow |

### P1 — Important

| ID | Question | Effort | How |
|----|----------|--------|-----|
| Q5 | Do subagents drain the same quota pool as main agent? | 30m | Spawn subagents in IDE, check `/usage` |
| F2 | Can `agy` output JSON/machine-parseable format? | 15m | Test `--json` flag, check for `--format` |

### P2 — Nice to Have

| ID | Question | Effort | How |
|----|----------|--------|-----|
| M1 | Opus 4.6 context window on this platform? (200K vs 1M beta) | 10m | Load known document, check `/context` |
| C1 | Is `opencode-antigravity-auth` still maintained? | 30m | Check GitHub stars, commits |
| S1 | What telemetry does the CLI send? | 30m | Network capture during use |

---

## §3 Source Reliability

| Source | Reliability | Notes |
|--------|-------------|-------|
| Live CLI execution | **ABSOLUTE** | Primary verification source |
| Official Google docs | **HIGH** | Primary documentation |
| DEV.to community posts | **MEDIUM** | Hands-on, may be incomplete |
| Medium articles | **MEDIUM** | Anecdotal |
| GitHub Issues | **HIGH** for bugs | Verified user reports |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: research-fleet | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
