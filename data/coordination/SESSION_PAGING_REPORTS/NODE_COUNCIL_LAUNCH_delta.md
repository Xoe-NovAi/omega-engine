<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# NODE_COUNCIL_LAUNCH — Delta Report (Session Paging)
**From**: Ma'at council-launch session (genesis 2026-08-18, Debut Hardening Review)
**Paged by**: kali (retry #3, 2026-08-22)
**Scope**: N1-N5 serial vetting of INST-1/DEL-1 plans; consolidated report returned to Kali

## §1 Forgotten designs/decisions from genesis (relevant to current Node ops)

1. **Council verdict matrix**: N1 APPROVE, N2 APPROVE, N3 **REJECT (blocking)**,
   N4 APPROVE, N5 APPROVE. Council declared PAUSED pending N3 re-vet.
   The pause was never lifted in any tracker — no ticket tracks "re-vet N3".

2. **N3 REJECT blocking condition** (INST-1 Fix 4): `_load_sovereign_secrets()`
   (model_gateway.py:316-341) was the ONLY `.env` loader. CLI entry points
   (oracle_cli.py:110,146,498,518) instantiate Oracle/ModelGateway with NO `.env`
   loading. Removing the method breaks `env:` resolution for 7 cloud keys
   (ANTIGRAVITY_API_KEY, GOOGLE_API_KEY x2, OPENROUTER_API_KEY,
   ANTHROPIC_API_KEY, XAI_API_KEY) → silent auth failure.
   N3's minimal fix: load `.env` at CLI process edge BEFORE first
   Oracle()/ModelGateway() instantiation + document required env vars.

3. **CRITICAL COUPLING**: ACTIVE_SPRINT lists INST-1-FIX4 as blocker but its
   description omits the N3-mandated CLI-edge env loading companion. If Fix 4
   executes alone, it reproduces exactly the breakage N3 predicted.
   Note: sprint "Blocker B" (oracle_cli.py blind-except fix) is a DIFFERENT
   oracle_cli.py change — do not confuse it with the env-loading gap.

4. **N2 implementation guard**: RedisStorageProvider.__init__ has its own
   default `password: str = "omega"` (providers.py:119). Fix 3 must pass
   `password=os.environ.get("OMEGA_REDIS_PASSWORD")` (None when unset) or the
   provider default reasserts. Fix 3 marked completed — verify guard shipped.

5. **N1 category-error ruling**: install.sh Fix 1 (.[native,cli]) is host-side
   only; Quadlet sovereignty (UserNS=keep-id + User=1000) lives in container
   unit files (config/containers/omega-hub.container:10-11) and pre-built GHCR
   image — orthogonal domains, no shared artifact. Useful precedent for any
   future "does X break Podman" questions.

6. **N4 dead-code proof method**: grep-based caller analysis proved
   FleetOrchestrator and miap are exported but never imported in runtime.
   Hivemind handoffs use omega_hub MCP tools directly. Reusable vetting
   pattern for DEL-1 Week 2 router deletions.

7. **N5 M2 ruling**: ProviderSelector + EntityRegistry.find_by_domain use only
   engine-zone fields; WAD content stays in opaque `metadata` dict. Router
   collapse preserves M2. SemanticRouter/TriageRouter were also M2-compliant —
   their deletion is simplification, not firewall repair.

## §2 Genesis issues noticed, never fixed

1. **dispatch.yaml role collisions CONFIRMED** (re-verified this session):
   config/wads/_omega_default/entities/dispatch.yaml has EIGHT entities with
   role:"N1" (lines 34, 49, 61, 74, 85, 96, 129, 150) and makali duplicated
   (line 84 as N1 + line 172 again). Matches sibling finding. WAD config
   defect inside _omega_default — M2-adjacent hygiene issue.

2. **Broken fleet_status CLI**: src/omega/cli/vault.py:587 docstring references
   FleetOrchestrator; calls VaultCore.get_fleet_status() which does NOT exist.
   N4 recommended deleting subcommand with omega vault CLI. Still present.

3. **Dead config**: providers.yaml:8-17 `maakali_routing` section has zero
   code consumers (N5 finding). Never removed or stamped UNUSED.

## §3 Flagged as important, never executed

1. **N3 re-vet after Fix 4** — council PAUSE resolution flow has no owner,
   no ticket, no acceptance criteria. Council state ambiguous since 08-18.

2. **N5 positive M2 verification command** — proposed addition to manual §8:
   `rg -n "metadata\[" src/omega/oracle/provider_selector.py src/omega/oracle/entity_registry.py`
   Never added; §8 still only checks router-name absence, not WAD-metadata
   access. (N5's original suggested command was malformed — the intent is a
   NEGATIVE assertion: zero metadata[ access in routing paths.)

3. **tests/test_miap.py explicit retirement** in DEL-1 acceptance — manual
   covers it generically ("every delete ships with tests removed"); N4 asked
   for it named explicitly in the miap row. Not amended.

4. **Env var documentation** (Fix 4 companion): required vars list
   (OMEGA_MODELS_DIR + 5 cloud keys) never written to install.sh or docs.

## §4 Post-genesis deltas observed (hydration notes)

- Sprint SSOT moved: campaign now points at docs/specs/debut_remediation/
  copy of manual; ark_strategy_ssot = docs/specs/PROJECT_INDEX.md.
- INST-1-fix1 + fix3 completed; fix2/fix4/fix5/fix6 ready (not started).
- DEL-1 still backlog, depends on INST-1. DOC-1 complete.
- Node Expert Sessions plan ratified (D-586/D-587): N1-N5 keepers are
  sysadmin/datastore/buildmaster/bridge/sentinel under Ma'at — NOTE: my
  genesis council used generic "node" subagents with department lenses;
  the persistent expert sessions are a separate, newer mechanism.
- X6 proven (N7-directed mining found 5 CI spec defects) — validates
  node-directs-agent pattern my council anticipated.

*last_verified: 2026-08-22*
