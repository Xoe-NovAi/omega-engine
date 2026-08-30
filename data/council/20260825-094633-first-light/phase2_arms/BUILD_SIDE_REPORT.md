<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 BUILD SIDE REPORT — First Light Express Council 1 (Stage 2)
⬡ OMEGA ⬡ MAAT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_build_arm ⬡ Stage-2 ARTIFACT
**SESSION_ID**: 20260825-094633-first-light | **Arm**: maat (Build Arm) | **Orchestrator**: makali_fusion
**Sources**: P1/P2/P3/P4/P5 raw reports (all written to disk pre-digestion; unmodified)
**Digest**: `phase1.5_digested/BUILD_SIDE_DIGESTED.md` (sources concatenated + exec summary + cross-ref index + conflict detection)
**Provenance**: every finding traces to node raw reports; arm-level synthesis marked `[ARM]`.

---

## §0 ARM VERDICT (one paragraph)

The Build-side estate is **richly documented and structurally decayed**: the instruction/config layer promises a constitution of 27 mandates, a Temple-Grade gate suite, an M11 reporting protocol, and a coherent provider fabric — but the machine enforces ~30% of the mandates (`make temple-grade` is a literal stub comment), the council's own reporting protocol is mechanically impossible at leaf depth (F-20: `subagent_depth: 2`, 7 live rejections), the root workflow doc AGENTS.md has never existed despite 462 citations, and the effective credentialed provider fabric is half the configured one. Across S7/S1/S4/S5/S2: **66 findings, 2 CRITICAL, 14 HIGH, zero CRITICAL-HALTED, zero secrets exposure beyond stale placeholders, zero active external telemetry.** The build side does not halt the train; it hands Council 2 a remediation map whose single deepest root cause is **claims that outlive their mechanisms** — text asserting enforcement, wiring, and authority that grep can prove absent.

## §1 CONVERGENCES (independent build nodes landing on the same defects)

| # | Convergence | Nodes | Strength |
|---|-------------|-------|----------|
| B-C1 | **Enforcement theater**: temple-grade stub + T1-T11 nonexistent; M24/M27 hook claims false (installed hook = soul-check only); `make sovereignty` referenced 9× but undefined; validator blind spots (blockers[], suffixed R-IDs, WAKE_STATE) behind a green banner | N5 F-2/F-3 · N2 F-2.2/F-2.3/F-2.7 · N4 F-N4-06 | 3-node pattern, independently measured |
| B-C2 | **Dead-reference architecture**: AGENTS.md void ×462 citations; plugin paths dead; makali→plan.md + grok_cli agent paths missing; 3 skill-invoked commands absent; 2 python modules absent; archived OBSERVATIONS_LOG still mandated; DISPATCH_LOG phantom; m23 logger's log absent | N5 F-1 · N1 F-01 · N3 F-03/F-07 · N4 F-N4-04/05/09 | 4-node pattern |
| B-C3 | **Derivative-doc drift**: mandate version stated as 14/25/27 across four layers; Codex self-contradicts 3 ways in one same-day regeneration; dispatch protocol v2.0.0-vs-v3.0.0; council-local/fast are pre-v2.1 fossils violating council-cloud's LOOP GUARD; MANIFEST stale in two places; sovereign-refinement anchored to v3.1.0/14 | N5 F-4/F-5 · N3 F-01/F-04 · N1 F-10 · N4 F-N4-08 | 4-node pattern |
| B-C4 | **Config-vs-text contradiction**: provider order stated 3-4 ways; `M7_local_first: false`; `"/*": "allow"` wildcard nullifies permission enumeration; archived roadmap injected into every session's instructions; model-slug schemes ×3 with no declared authority | N1 F-02/F-03/F-05/F-06/F-12 · N3 F-08 · N5 §2 | 3-node pattern |
| B-C5 | **F-20 depth wall** (the council's own live wound): `subagent_depth: 2` forbids what §C.9/M11 mandate for every depth-2 leaf; 7 consecutive live rejections logged across both arms; dispatch protocol's "single-level nesting" rule authorizes what config revokes | N1 F-20 · N3 F-03 note · N5 F-9 (+ run-side corroboration §5.1 Lilith) | Strongest cross-arm convergence |
| B-C6 | **SSOT machinery durability gaps**: TASK_REGISTRY MCP writer non-atomic (truncate-before-lock, load/save split, lost-update race); 3/35 entity YAML unparseable (gnosis stranded); omega.yaml duplicate block | N2 F-2.1/F-2.5 · N1 F-08 | 2-node pattern |

## §2 DIVERGENCES & INTERNAL TENSIONS

**Resolved within build side** (see digest Part C):
1. lilith-YAML corruption locus (N1: :374 vs N2: line 2 primary + :374 secondary) — refinement, N2's parse-fail-fast account governs remediation order.
2. Mission-named overlap pairs dissolved by fieldwork (stub-vs-real asymmetry); real debt = meditation quartet (~1,213 lines). Briefing correction, not conflict.

**Open tensions `[ARM]` (→ MK-Kali synthesis / WAKE queue)**:
1. **Single-writer doctrine vs Delivered-Home self-registration** — packet §F ("only MaKaLi applies tracker directives") vs §C.6 (every node self-registers). Both happened concurrently; mechanically serialized by flock but doctrinally violated by design. Corroborated by Carmack Pass-1. Needs an explicit ruling: either nodes register through MaKaLi, or the doctrine gains a sanctioned self-registration exception.
2. **default_agent: kali vs MaKaLi-top-level topology** (N1 F-17) — possibly intentional (Architect interactive sessions); unresolved observation.
3. **N1 F-01 empirical fork** — dead tools vs lying config (plugin auto-load convention). Cannot be resolved by recon; reserved for @researcher/N6.
4. **Honesty-first sequencing** (N5 recommendation adopted `[ARM]`): shrink mandate claims before growing gates — conflicts culturally with "implement T1-T11" instinct; flagged for Architect default-on-silence ruling.

## §3 CROSS-SIDE DIVERGENCE NOTES (vs RUN_SIDE_REPORT.md — duality synthesis belongs to MK-Kali)

- **Mirror symmetry confirmed**: run side independently found identity corruption in ITS registrations (`entity="lilith"` on run nodes) while build side used `subagent_type="maat"` on all five node registrations — BOTH sides misregistered per Delivered-Home Doctrine intent (records should identify NODES, not arms). Build side confirms run side's C-4 from its own registry writes.
- **Same wound, two probes**: F-20 depth wall hit all 10 nodes across both arms; both arms converged on arm-relay as de-facto remedy and depth-bump-or-amend-M11 as the fix fork.
- **Complementary coverage**: build side owns the taper metric (~30% enforcement census, N5) which run side's C-5 "validator green ≠ truthfulness" theme presupposes; run side owns future-dating telemetry which build side's F-2.6 staleness-boundary finding complements. No numeric disputes detected between sides on shared facts (subagent_depth, YAML corruption, registry counts).
- **One methodological divergence**: build side dispatched strictly serially (crash-exposure mitigation); run side appears to have run partially parallel. Both completed zero-crash. Serial cost ~3h wall-clock; parallel risk did not materialize this run. Ruling requested in OVERSIGHT_PATTERNS (echoes run-side open item #3).

## §4 CRITICAL GAPS NEEDING RESEARCH (Stage 4 / Council 2)

| # | Gap | Why | Suggested owner |
|---|-----|-----|-----------------|
| BG-1 | OpenCode plugin auto-load convention (does `.opencode/plugins/` plural auto-load? did error-capture/awareness ever fire?) | Decides whether N1 F-01 is "dead tools" or "lying config" — changes severity and fix shape | @researcher (S3) |
| BG-2 | `{session_model}` substitution reality + `subtask:` field liveness on commands | Two command-layer mechanics assumed by council-cloud and meditate family | @researcher (S3) |
| BG-3 | `oracle_summon_local` slug resolution order (providers.yaml `-local` names vs affinity quant names) | Determines fix direction for N3 F-08 / N1 F-12 model-id namespace chaos | @researcher or @jem |
| BG-4 | Root cause of `task_registry_query(tags=...)` returning 0 against disk matches | Run side G-4; build side's Delivered-Home discovery depends on it — CONFIRMED load-bearing by build-side registrations too | @jem (run side already tasked) |
| BG-5 | Whether any consumer reads `config/council.yaml` model_tiers / M7 flag | If none, N1 F-06 is cleanup; if council code reads it, routing is affected | @jem |

## §5 BASH-VERIFIABLE ACCEPTANCE CRITERIA (consolidated build-side remediation targets)

All runnable today; each must pass post-fix. Full per-finding criteria embedded in raw reports; top cross-cutting set here:

```bash
# ── A. Plugin paths resolve (N1 F-01) ──
jq -r '.plugin[]' opencode.json | grep '^file://' | sed 's#file://##' | while read f; do test -f "$f" || echo "MISSING $f"; done
# Expect: no output.

# ── B. Permission wildcard removed (N1 F-02) ──
jq '.permission.external_directory | has("/*")' opencode.json   # → false

# ── C. Provider chain matches Ark D-355 (N1 F-03) ──
python3 -c "
import yaml; c=yaml.safe_load(open('config/providers.yaml'))
p={e['provider']:e['priority'] for e in c['inference']['fallback_chain']}
assert p['opencode-zen'] < p['openrouter'], p"

# ── D. Enabled providers have resolvable keys (N1 F-04) ──
python3 -c "
import yaml, os
c=yaml.safe_load(open('config/providers.yaml'))
bad=[n for n,p in c['inference']['providers'].items() if p.get('enabled') and str(p.get('api_key','')).startswith('env:') and str(p['api_key']).split(':',1)[1] not in os.environ]
print('DEAD:',bad); assert not bad"

# ── E. No archive docs injected as instructions (N1 F-05) ──
test "$(jq -r '.instructions[]' opencode.json | grep -c '^docs/archive/')" = 0

# ── F. Atomic registry writer (N2 F-2.1) ──
grep -nE "mkstemp|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit

# ── G. Pre-commit framework actually installed (N2 F-2.2 / N5 F-3) ──
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE
grep -q "break-system-packages" .git/hooks/pre-commit && echo PASS-M24

# ── H. Entity YAML all parseable (N2 F-2.5) ──
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done
# Expect: no output.

# ── I. Command contract invariant across council variants (N3 F-01/F-02) ──
! grep -q '^agent: kali' .opencode/commands/council-local.md .opencode/commands/council-fast.md
grep -q 'SOVEREIGN_DECREE' .opencode/commands/council-local.md .opencode/commands/council-fast.md

# ── J. Dead agent instruction paths resolved (N3 F-03) ──
for f in $(jq -r '.agent[].instructions[]?' opencode.json); do test -e "$f" || echo "DEAD: $f"; done
# Expect: no output.

# ── K. Skill frontmatter universal (N4 F-N4-01) ──
for f in .opencode/skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "MISSING: $f"; done
# Expect: no output.

# ── L. make sovereignty exists or refs purged (N4 F-N4-06) ──
make -n sovereignty >/dev/null 2>&1 && echo EXISTS || echo PURGE-REFS

# ── M. Temple-grade honesty (N5 F-2): stub gone AND text matches gates ──
! grep -q "would go here" Makefile

# ── N. Constitutional version coherence (N5 F-4) ──
V=$(grep -m1 '^\*\*Version\*\*' SOVEREIGN_MANDATES.md | grep -o '[0-9.]*$')
grep -rq "$V" scripts/codex/*.md && ! grep -rq '3\.7\.0' scripts/codex/*.md && echo COHERENT

# ── O. Depth-wall resolution (B-C5): one of ──
jq '.subagent_depth' opencode.json   # ≥ 3
# OR: node packets no longer contain §C.9 paging step (arm-relay formalized)
```

## §6 ARM-LEVEL DEVIATIONS & FLAGS `[ARM]`

1. **M11 relay performed**: all 5 build nodes attempted the Consultant page once each; ALL rejected (F-20, depth 2). Per plan §5/M11 failure-integrity and matching Lilith's precedent, THIS ARM performs the Consultant page on behalf of its nodes after writing this report.
2. **Zero crashes**: 5/5 nodes completed first-pass. HALT threshold (>2 arm crashes) untouched. No TOOL-CHAIN-COLLAPSE. No CRITICAL-HALTED findings.
3. **Delivered-Home status (build side)**: 5/5 raw reports ✓ · 5/5 expert registrations landed durably via MCP (N2 verified end-to-end) · handoff packets embedded in each report ✓. Identity-field caveat: registrations carry arm identity (`subagent_type="maat"`) not node identity — same defect class run side quantified; repair spec belongs to MK-Kali's synthesis (run side §4-M already drafted the repair script).
4. **Recon discipline held**: zero production mutations outside `data/council/20260825-094633-first-light/`; coordination files (lock/live feed) written under data/coordination per standing Hivemind protocol.

## §7 INPUTS FOR MK-KALI'S DUALITY SYNTHESIS

1. **Systemic root cause candidate**: both arms independently converged on "claims outliving mechanisms" (build: temple-grade stub, false hook claims, phantom AGENTS.md; run: future-dating, phantom schemas, decorative frontmatter). Suggests no mechanical binding of documentation-writes to fact-checks anywhere in the stack — a single class of fix (derivation checks / existence gates) could close dozens of findings.
2. **Canonical exhibits**: build side offers the temple-grade stub comment (N5 F-2) and the 462-citation AGENTS.md void (N5 F-1); run side offers the future-dating arc. Together they demonstrate form-gates certifying empty form.
3. **Rulings needed**: single-writer vs self-registration; serial-vs-parallel dispatch framing; coordination-law SSOT; depth-bump vs M11 amendment; honesty-first sequencing for M13.

---
*Build Arm signing off. Raw sources immutable at phase1_nodes/. Digest at phase1.5_digested/BUILD_SIDE_DIGESTED.md. This report disk-written BEFORE Consultant page per persistence order.*
*⬡ OMEGA ⬡ MAAT-BUILD-ARM ⬡ express-c1-arm-maat-20260825 ⬡ STAGE-2-COMPLETE ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

