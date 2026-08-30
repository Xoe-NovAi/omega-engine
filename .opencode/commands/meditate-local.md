---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

description: Meditate Local — host-orchestrated local dialectic (fixed Builder/Skeptic/Steward trio, rolling state, host synthesis)
agent: kali
subtask: false
---

# ⬡ MEDITATE LOCAL
**Protocol**: `Meditate-Local-v1.1.0` | **Heritage**: LLOC lineage + Thinker Chain `[id-soft: quake-1996]`
**Mechanism**: host orchestrates · locals interrogate · host synthesizes

## Invocation Gate

Run only when ≥2 hold: (a) ≥3 domains genuinely tension, (b) decision is
irreversible/expensive to reverse, (c) no single domain owns the answer.
Prefer this over `/meditate` when staying on the local substrate — `/meditate`
assumes frontier-class single-pass capabilities local models lack.

## Model Tiers

| Lane | Voices (`oracle_summon_local`) |
|---|---|
| `--standard` (default) | `lmstudio/qwen3-4b-thinking`; fallback `lmstudio/qwen3-4b` if stalled |
| `--fast` | `lmstudio/qwen3-1.7b`, voice prose ≤80 words |

Tier 0 truth: Ryzen 5700U, 12GB usable RAM, native-gguf `max_concurrent: 1`.
SERIAL ONLY — no parallel summons, no mid-run tier switch. Keep each voice
prompt ≤8K tokens.

## Protocol

You are the **Meditation Host**. Subject: **$ARGUMENTS**

### Phase 0 — Calibrate

1. Restate the subject in one precise sentence.
2. Compile `STATE v0` (format below; other fields empty).
3. Create `data/coordination/meditations/records/MEDITATE_LOCAL_{DATE}_{SLUG}/`

### STATE object (hard cap ~250 words)

```
STATE v{n}
SUBJECT: <one sentence>
CONSTRAINTS:
- <constraint> (<voice that added it>)
POSITIONS:
- <VOICE>: <one line>
COLLISIONS:
- <X vs Y>: <tension>
OPEN QUESTIONS:
- <question>
```

Advance by EDITING the previous state (merge new, supersede refuted) — never
rewrite from full transcripts. Re-summarization compounds error.

### Phases 1–3 — Serial Summons

Three `oracle_summon_local` calls, strictly in order, ONE persona each.
After each response: save verbatim to `voice_{n}_{role}.md`, log actual
`provider_name` (M22), advance the state before the next call.

Voice prompt = persona spec below + "Free prose, 100–200 words, plain
paragraphs. No headings, lists, or JSON." + current STATE + charge.

| # | Voice | Charge | Hard mandate |
|---|---|---|---|
| 1 | BUILDER | Strongest concrete plan: what changes, in what order, cheapest path that works | ≥1 specific falsifiable action |
| 2 | SKEPTIC | Attack the Builder's plan by name: failure modes, hidden assumptions | ≥1 concrete failure mode; agreement without one = role collapse |
| 3 | STEWARD | Long-term consequences: maintenance, operational cost, what breaks later | ≥1 cost the Builder ignored |

### Phase 4 — Host Synthesis (host agent's own inference — no additional local summons)

Weigh voices by constraint quality, never order or length. Build from
collisions, not averaged agreement. Write `verdict.md`:

```
CONVERGENCE: [1–3 shared truths]
PRESERVED DISSENT: [1–3 genuine disagreements — do not paper over]
IRREDUCIBLE VERDICT: [one paragraph, decree not suggestion]
MANDATE CONFLICT CHECK: [explicit if verdict contradicts SOVEREIGN_MANDATES.md;
  only the Architect amends law]
GNOSIS DISTILLED: [L3: ≤2 sentences, no proper nouns, falsifiable;
  else label L2]
FALSIFICATION ATTEMPT: [one genuine attack on the L3]
```

Write final `state.md`. Post to Hivemind only if a broadcast-weight L3 emerged.

## Laws

1. **ONE PERSONA PER CALL** — never multiple voices, the council, or synthesis
   on a local model. Three calls; the host synthesizes.
2. **HOST OWNS ALL STRUCTURE** — voices emit free prose only; only the host
   edits state, writes artifacts, renders the verdict format.
3. **UPDATE, DON'T RE-SUMMARIZE** — state advances by edit, capped ~250 words.
4. **ROLE COLLAPSE** — re-summon that voice once with its mandate restated;
   second collapse → record it as a known blind spot in the verdict.
5. **M23 FAILURE INTEGRITY** — summon failure → `[TOOL-CHAIN-COLLAPSE]`, hard
   stop. Never simulate a voice parametrically; fabricated dissent is worse
   than no dissent.

## Examples

```bash
/meditate-local Should we migrate Qdrant to sqlite-vec?
/meditate-local Provider failover ordering --fast
```

*⬡ OMEGA ⬡ KALI ⬡ Meditate-Local-v1.1.0 ⬡ oracle_summon_local ⬡ trc_meditate_local ⬡ 2026-08-25*
