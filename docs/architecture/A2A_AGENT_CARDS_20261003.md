<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# A2A v1.0 Agent Cards for the Sovereign Seats

**AP Token**: `AP-A2A-AGENT-CARDS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ space-bunny-free ⬡ opencode ⬡ trc_research ⬡ IMPLEMENTED

**Date**: 2026-10-03
**Status**: `IMPLEMENTED — A2A-informed, NOT A2A-compliant`
**Author**: @researcher (Sovereign Researcher, Jem Analyst facet)
**Ticket**: P1-2 (knowledge-gap remediation)
**Normative reference**: A2A v1.0.0 — <https://a2a-protocol.org/latest/specification>
**Artifacts**: `config/a2a/agent_cards/*.json` (committed) ·
`scripts/a2a_agent_cards.py` (committed) · `tests/test_a2a_agent_cards.py`
(committed) · `data/coordination/a2a/agent_index.json` (generated, **not**
committed — see §7.1)

> **The one sentence that matters.** Omega speaks **MCP**, not A2A. These cards
> are a *descriptive manifest* of our seats written in the shape of an A2A v1.0
> AgentCard. They are **A2A-informed, NOT A2A-compliant**, and every card says so
> in its own body. See §5 for the precise gap.

---

## L1 — Executive Summary

We hold **10 sovereign seats**. A2A v1.0 defines one manifest format for
advertising an agent's identity, capabilities, skills, endpoints and auth. This
ticket builds those 10 manifests, a validator that enforces the spec's field
tables, and a local discovery index — while being scrupulous about the fact that
**we implement none of the A2A method set**.

Three decisions carry the honesty burden:

1. **No official A2A binding is claimed.** We do not implement `message/send`,
   `tasks/get`, or any other §3.1 operation. Declaring
   `protocolBinding: "JSONRPC"` would assert the A2A JSON-RPC binding and be
   false. §5.8 explicitly sanctions URI-identified custom bindings, so every
   card declares `https://xoe-novai.dev/bindings/omega-hub-mcp/v1`. A conforming
   A2A client reads that, does not recognise it, and correctly declines to speak
   to us as if we were an A2A server. **The non-standard value is the safety
   feature.**
2. **`mtlsSecurityScheme` is used and labelled an approximation.** §4.5.1's
   oneof has no member for mesh-layer identity, and §4.5.6 gives that member
   exactly one optional field (`description`). Our real auth is Tailscale/
   WireGuard mesh identity — not HTTP mTLS, not an API key. We use the nearest
   available marker and say precisely why in the card.
3. **No signatures.** We have no signing key and no RFC 8785 canonicalizer. A
   placeholder JWS would be forgery, so `signatures` (§4.4.7) is absent from
   every card and §4.1 below states exactly what signing would require.

**Slot honesty.** `config/wads/_omega_default/entities.yaml` records a `slots:`
key for exactly **one** real seat — `john carmack: [S3]`. Every other card
reports `"slot": "unassigned"` and cites the authority for that claim in
`x-omega.seat.slot_authority`. **No slot number was invented.**

---

## §1 — Concept → A2A field mapping

Every normative field we emit, with its spec section. "Emitted" means present in
all 10 cards unless noted.

| Our concept | A2A field | Spec § | Required | Emitted | Note |
|---|---|---|---|---|---|
| Seat display identity | `name` | §4.4.1 | **Yes** | ✅ all | e.g. `Kali — Sovereign Grand Oversight` |
| Seat remit (prose) | `description` | §4.4.1 | **Yes** | ✅ all | grounded in `entities.yaml` `role` |
| Card revision | `version` | §4.4.1 | **Yes** | ✅ all | `"1.0.0"` (card version, *not* engine version) |
| Federation endpoint | `supportedInterfaces[]` | §4.4.1 → §4.4.6 | **Yes** | ✅ all | exactly one entry |
| Endpoint URL | `AgentInterface.url` | §4.4.6 | **Yes** | ✅ all | `https://n0.tail51f14a.ts.net:8016/` |
| Wire protocol identity | `AgentInterface.protocolBinding` | §4.4.6, §5.8 | **Yes** | ✅ all | custom URI, **not** an official binding |
| Spec version targeted | `AgentInterface.protocolVersion` | §4.4.6 | **Yes** | ✅ all | `"1.0"` — see §3.3 caveat |
| Multi-tenant routing hint | `AgentInterface.tenant` | §4.4.6 | No | ❌ omitted | not implemented; §4.4.6 makes it a client MUST when set |
| A2A behaviour flags | `capabilities.{streaming,pushNotifications,extendedAgentCard}` | §4.4.3 | Yes (object) | ✅ all | all three `false` — see §3.2 |
| Our provenance extension | `capabilities.extensions[]` | §4.4.3 → §4.4.4 | No | ✅ all | the spec's own place to declare extensions |
| Extension identity | `AgentExtension.{uri,description,required,params}` | §4.4.4 | No (all) | ✅ all | only `required` is meaningful; all optional |
| Common input media types | `defaultInputModes` | §4.4.1 | **Yes** | ✅ all | `application/json`, `text/plain` |
| Common output media types | `defaultOutputModes` | §4.4.1 | **Yes** | ✅ all | `application/json`, `text/markdown` |
| Seat remit, discrete | `skills[]` | §4.4.1 → §4.4.5 | **Yes** | ✅ all | 23 skills across 10 seats |
| Skill slug | `AgentSkill.id` | §4.4.5 | **Yes** | ✅ all | |
| Skill title | `AgentSkill.name` | §4.4.5 | **Yes** | ✅ all | |
| Skill description | `AgentSkill.description` | §4.4.5 | **Yes** | ✅ all | |
| Skill keywords | `AgentSkill.tags` | §4.4.5 | **Yes** | ✅ all | **required**; see §3.2 |
| Example asks | `AgentSkill.examples` | §4.4.5 | No | ✅ some | |
| Per-skill media overrides | `AgentSkill.{inputModes,outputModes}` | §4.4.5 | No | ❌ omitted | defaults already cover the seam |
| Per-skill auth | `AgentSkill.securityRequirements` | §4.4.5 | No | ❌ omitted | identical to card-level; no extra signal |
| Vendor | `provider` | §4.4.2 | No | ✅ all | `organization` + `url`, **both** required |
| Mesh identity | `securitySchemes.meshIdentity.mtlsSecurityScheme` | §4.5.1 → §4.5.6 | No | ✅ all | **approximation** — see §4 |
| Auth actually required | `securityRequirements[]` | §4.4.1 (shape §8.5) | No | ✅ all | `{"schemes":{"meshIdentity":{"list":[]}}}` |
| Extra docs link | `documentationUrl` | §4.4.1 | No | ❌ omitted | §3.4 |
| Seat icon | `iconUrl` | §4.4.1 | No | ❌ omitted | §3.4 |
| Card authenticity | `signatures[]` | §4.4.7 | No | ❌ omitted | §4.3 |
| **Slot number (S1–S10)** | — *no A2A field* | — | — | `x-omega.seat.slot` | §3.5 |
| **Seat id / role / domains** | — *no A2A field* | — | — | `x-omega.seat.*` | §3.5 |
| **Real MCP tool names** | — *no A2A field* | — | — | `x-omega.hub_tools` | §3.5 |
| **Conformance level** | — *no A2A field* | — | — | `x-omega.a2a_conformance` | §3.5 |

**§5.5 (camelCase).** All A2A-protocol JSON is camelCase, as §5.5 requires. The
`x-omega` sidecar deliberately uses snake_case — it is *not* A2C protocol data
(§3.5) — and the validator's §5.5 check is scoped so it does not reach it.

---

## §2 — What a publisher is required to do (§8)

| Publisher obligation | Spec § | Status |
|---|---|---|
| Make an Agent Card available | §8.1 | ❌ **Not met.** Cards are files in this repo; nothing serves them. |
| Serve `https://{domain}/.well-known/agent-card.json` | §8.2, §14.3 | ❌ **Not met.** Probed 2026-10-03 — both endpoints return **404** on that path. |
| Publish to a registry/catalog | §8.2 (one of three options) | ❌ **Not done, deliberately.** M8 forbids it; publishing internal seats to an external catalog would leak the fleet's shape. |
| Pre-configured card URL/content | §8.2 (one of three options) | ⚠️ **Partially.** Cards are readable at a known repo path — this is the §8.2 "Direct Configuration" route. |
| Declare all supported interfaces in preference order | §8.3.1 | ⚠️ One entry, honestly declared. §8.3.1 also requires each interface "**MUST** accurately declare its transport protocol and URL" — a custom binding URI is how we satisfy that truthfully. |
| First `supportedInterfaces` entry = preferred | §8.3.1 | ✅ Single entry, so preferred is unambiguous. |
| Clients select first supported transport and echo `tenant` | §8.3.2 | N/A for us; `tenant` unset, so §4.4.6's echo-MUST does not apply. |
| Canonicalize with JCS (RFC 8785) before signing | §8.4.1 | ❌ Not implemented — no signer exists. |
| Exclude `signatures` from the signed payload | §8.4.1 | N/A (unsigned). Honoured *by construction* by omitting the field. |
| JWS protected header carries `alg`, `typ`, `kid` (`jku` optional) | §8.4.2 | ❌ Not implemented. |
| Verify ≥1 signature before trusting a card | §8.4.3 | ❌ Not implemented. |
| Serve an extended card when authenticated | §3.1.11, §11.3.4 (`GET /extendedAgentCard`) | ❌ `extendedAgentCard: false`. |
| Don't put secrets in a card | §14.3 | ✅ No credentials, endpoints or internal tokens in any card. |

**Well-known path.** §14.3 registers URI suffix **`agent-card.json`**, and §8.2
gives `/.well-known/agent-card.json`. The older `/.well-known/agent.json` is
**v0.3**; it appears zero times in the v1.0 spec. Confirmed against three
implementations: a2a-python `A2ACardResolver(agent_card_path='/.well-known/agent-card.json')`,
a2a-go v2 `agentcard.DefaultResolver.Resolve`, and litellm's vendored resolver,
which defines `AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent-card.json"` and
`PREV_AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"`.

---

## §3 — Deliberate non-adoptions, and why

### 3.1 v0.3 shape — rejected outright

The v0.3 singular `url` + `preferredTransport` pair is **gone** in v1.0; the
string `preferredTransport` occurs zero times in the spec, and the v1.0
AgentCard table (§4.4.1) has no top-level `url`. The validator rejects `url`,
`preferredTransport` and `additionalInterfaces` at the top level with an
explicit §4.4.1 citation, so a v0.3-shaped card cannot ship quietly.

### 3.2 Fields set to `false` or omitted on purpose

- **All three `capabilities` booleans are `false`.** Not laziness — accuracy. We
  have no A2A `message/stream` (SSE stream of `TaskStatusUpdateEvent` /
  `TaskArtifactUpdateEvent`), no `tasks/pushNotificationConfig/*`, and no
  authenticated extended card. Our hub *does* speak MCP-over-SSE, but that is
  not the A2A capability. Flipping these to `true` to look capable is precisely
  the overclaim this ticket exists to prevent.
- **`AgentSkill.tags` is populated everywhere.** §4.4.5 marks it required. It is
  the single most commonly omitted required field in hand-written cards, so the
  validator and the test suite both assert it explicitly.
- **`securityRequirements[].schemes.meshIdentity.list` is `[]`.** The spec gives
  `SecurityRequirement` no field table of its own; its shape is defined by
  example in §8.5 as `{"schemes": {"<name>": {"list": [...]}}}`. OAuth carries
  a scope list; mTLS has no scopes, so an empty list is the faithful rendering
  rather than an invented scope string.
- **`extensions[].required` is `false`.** Our extension is descriptive. Marking
  it `required: true` would tell clients they *must* understand Omega-specific
  provenance to proceed — which is false, and would make an otherwise valid card
  unusable by any stock client.

### 3.3 The `protocolVersion` caveat — a forced field we cannot honestly fill

`AgentInterface.protocolVersion` is **required** (§4.4.6) and defined as "the
version of the A2A protocol this interface exposes". We expose no A2A protocol.
The field is therefore emitted as `"1.0"` because the spec gives no way to
omit it and §5.7 forbids omitting required fields — **it denotes the A2A
specification version our card conforms to as a document, not an implemented
binding.** This is the closest honest encoding available; it is recorded here so
nobody later reads `"1.0"` as "we speak A2A 1.0".

### 3.4 `documentationUrl` and `iconUrl` omitted

Both are optional (§4.4.1). `documentationUrl` must be "a URL providing
additional documentation" — our doc is a **repo-local path**
(`docs/architecture/A2A_AGENT_CARDS_20261003.md`), not a URL. Fabricating
`https://xoe-novai.dev/...` would point at a host we do not control and cannot
verify (M29: an untested remote claim is not a claim). The real path is recorded
as `x-omega.documentation_path` instead. `iconUrl` is omitted because no icon
asset exists; inventing a URL would be the same fabrication.

### 3.5 Non-normative sidecar — `x-omega`

Slot numbers, seat roles, real MCP tool names, conformance level and endpoint
probe results have **no A2A v1.0 field**. §5.7 states implementations **SHOULD
ignore unrecognized fields** "allowing for forward compatibility" — that is what
makes a namespaced sidecar legitimate rather than a violation. Rules enforced by
the validator:

- `x-omega` must declare `"normative": false`;
- any top-level field outside the §4.4.1 set must live inside a declared
  namespace (an undeclared top-level key is an **error**);
- `a2a_conformance` must be present;
- **a card may not claim compliance while also listing conformity gaps** — that
  self-contradiction is an error;
- `seat.slot` must be present, and `unassigned` is the correct value when no
  slot is recorded.

---

## §4 — Auth: what we actually have

### 4.1 The real mechanism

Omega identity is enforced at the **mesh layer**: Tailscale/WireGuard, tailnet
only, ACL-gated, with `tailscaled` Serve routes. Tailnet addresses are
`100.123.51.67` (IPv4) and `fd7a:115c:a1e0::d835:3344` (IPv6). The policy lives
in `config/lan_exposure_allowlist.yaml`; the hub port is registered in
`config/omega.yaml` (`mcp.hub_port: 8016`).

### 4.2 Why `mtlsSecurityScheme` is an approximation

Three separate mismatches, all stated in the card's own `description`:

1. **Wrong layer.** §4.5.6 means mutual TLS *on the transport* — certificate
   exchange during the TLS handshake. Omega's identity is established by the
   WireGuard tunnel *beneath* the transport. No client certificate is presented
   to the hub.
2. **No field to carry it.** §4.5.6 defines **exactly one** field, an optional
   `description`. There is no CA bundle, key id, trust domain or realm member —
   which is precisely why the approximation has to be explained in prose. The
   validator rejects any other key inside that member (§4.5.6).
3. **Not an API key either.** `apiKeySecurityScheme` (§4.5.2) would demand a
   `location` (`query`/`header`/`cookie`) and a `name`. Omega has no such
   header; choosing it would invent one.

So `mtlsSecurityScheme` is the **nearest available marker**, and the card says
in its own body: *"A client MUST NOT read this scheme as evidence of negotiated
mTLS on the transport."* An httpAuth or apiKey scheme would have been a cleaner
lie.

### 4.3 Signing not implemented (§8.4)

Omitting `signatures` is the honest state, not an oversight. Compliance would
require, per §8.4.1–§8.4.3:

- an **RFC 8785 (JCS)** canonicalizer — remove protobuf-default-valued fields,
  omit unset optionals, keep explicitly-set optionals even at default, exclude
  `signatures` itself, then lexicographically order keys;
- a **JWS (RFC 7515)** signer with a protected header carrying `alg`,
  `typ: "JOSE"`, `kid` (and optionally `jku`);
- signing input `ASCII(BASE64URL(UTF8(header)) || '.' || BASE64URL(payload))`;
- a **JWKS endpoint** and a key-rotation story (multiple signatures are allowed
  for rotation, §8.4.3).

Emitting a hand-written `protected`/`signature` pair with no key behind it would
be a forgery that clients would fail to verify — or worse, appear to verify.
**We do not have that, so we do not claim it.**

---

## §5 — The gap statement: informed vs compliant

### 5.1 What "A2A-informed" means here

We have adopted the **AgentCard document model** — its field names, its required
field set, its capability semantics, its skill taxonomy, its security-scheme
shape and its discovery path — as a *description* of our seats, plus a validator
that enforces the spec's own field tables. That is the whole of it.

### 5.2 What compliance would additionally require

| # | Requirement | Spec § | Status |
|---|---|---|---|
| 1 | Implement `message/send` | §3.1.1 | ❌ absent |
| 2 | Implement `message/stream` over SSE | §3.1.2, §3.5.2 | ❌ absent |
| 3 | Implement `tasks/get` | §3.1.3 | ❌ absent |
| 4 | Implement `tasks/list` | §3.1.4 | ❌ absent |
| 5 | Implement `tasks/cancel` | §3.1.5 | ❌ absent |
| 6 | Implement `tasks/subscribe` | §3.1.6 | ❌ absent |
| 7 | Implement push-notification config CRUD | §3.1.7–§3.1.10 | ❌ absent |
| 8 | Implement authenticated extended card (`GET /extendedAgentCard`) | §3.1.11, §11.3.4 | ❌ absent |
| 9 | Serve `/.well-known/agent-card.json` | §8.2, §14.3 | ❌ 404 on both endpoints |
| 10 | Serve the §4.1 data model (`Task`, `Message`, `Part`, `Artifact`) | §4.1 | ❌ no such objects exist |
| 11 | A protocol binding from `JSONRPC`/`GRPC`/`HTTP+JSON` | §4.4.6 | ❌ none declared |
| 12 | Version negotiation + `A2A-Version` header | §3.6, §14.2.1 | ❌ absent |
| 13 | JCS canonicalization + JWS signing | §8.4.1–§8.4.2 | ❌ absent |
| 14 | Signature verification path + JWKS + rotation | §8.4.3 | ❌ absent |
| 15 | `capabilities.streaming` / `pushNotifications` / `extendedAgentCard` = `true` | §4.4.3 | ❌ all `false` |
| 16 | A2A error-code mapping | §5.4 | ❌ absent |
| 17 | Correct `Content-Type` (`application/a2a+json`) | §14.1.1 | ❌ absent |

**Verdict: 17 of 17 unmet. Omega is A2A-informed and is NOT A2A-compliant.**
Nothing in this ticket changes that, and no artifact here should ever be cited as
evidence of A2A interoperability.

### 5.3 Endpoint reachability — measured, not assumed

Probed on 2026-10-03 against the live host:

| Endpoint | Port | Reachable | Actually speaks | Serves agent card | Speaks A2A |
|---|---|---|---|---|---|
| `https://n0.tail51f14a.ts.net:8016/` | 8016 | ✅ `GET /sse` → 200 (MCP SSE, `text/event-stream`); `GET /` → 404 | MCP over SSE + JSON-RPC 2.0 | ❌ 404 | ❌ |
| `https://n0.tail51f14a.ts.net:8019/` | 8019 | ✅ `GET /` → 200 (`"service":"omega-exchange/2.0"`) | read-only artifact exchange | ❌ 404 (`"No artifact at '.well-known/agent-card.json'"`) | ❌ |

Both are declared reachable because they are — but reachability is recorded
separately from A2A conformance precisely so the two are never conflated.

---

## §6 — Seats

| Card | Seat | Slot | One-line remit | Skills |
|---|---|---|---|---|
| `kali.json` | Kali | `unassigned` | Sovereign Grand Oversight; mandate arbitration and cross-slot veto | mandate-arbitration, fleet-oversight |
| `maat.json` | Ma'at | `unassigned` | CTO; governs **build slots S1–S5**; architecture, debt, security posture | build-side-governance, system-design-review |
| `lilith.json` | Lilith | `unassigned` | Oversoul; governs **run slots S6–S10**; sovereignty boundaries and refusal | run-side-governance, sovereignty-boundary |
| `doom_guy.json` | Doom Guy | `unassigned` | id Software Architect; infrastructure, systemd, mesh, zone memory, WAD | infrastructure-supervision, mesh-connectivity, zone-and-wad-layout |
| `john_carmack.json` | John Carmack | **`S3`** | Ultimate Technical Consultant; first-principles architecture and performance | architectural-review, performance-engineering |
| `roc_racoon.json` | Roc Racoon | `unassigned` | Sovereign Miner (→ Lilith); legacy archaeology and pattern mining | legacy-archaeology, pattern-extraction |
| `researcher.json` | Researcher | `unassigned` | Master Researcher (→ Lilith); deep research, dialectic synthesis, curation | deep-research, dialectic-synthesis, knowledge-curation |
| `verity.json` | Verity | `unassigned` | Compliance & Gnosis; mandate audit, L1→L3 distillation, M33/M34 verification | mandate-audit, soul-distillation, deliverable-verification |
| `antigravity.json` | Antigravity | `unassigned` | Antigravity IDE as Hivemind Council peer; **strategy-only, never implements** | strategic-review, cross-platform-hivemind |
| `makali_fusion.json` | Makali Fusion | `unassigned` | Kali + Ma'at + Lilith unified; three-oversoul orchestration | unified-orchestration, cross-seat-dispatch |

**Naming and identity traps, recorded so they are not re-derived wrongly:**

- `entities.yaml` keys use **spaces and an apostrophe**: `ma'at`, `doom guy`,
  `roc racoon`, `john carmack`. Cards are filed by entity-directory name
  (`maat.json`, `doom_guy.json`, …). A regex that assumes `\w+` keys silently
  mis-attributes slot `S3` to `researcher` — a real trap we hit and corrected
  with a real YAML parse.
- **`makali` is a different seat** from `makali_fusion`. `makali` is the Apex
  Mind / mastermind (strategy-only, `qwen3-4b-thinking-q4_k_m`); the ticket
  excludes it. `makali_fusion` is the unified Kali+Ma'at+Lilith identity
  (hierarchy level 1, sovereignty level 5, element Aether) per its own
  `soul.yaml`. **No `makali.json` card exists.**
- **`antigravity` has no `entities.yaml` entry at all.** Its remit is grounded
  in `data/entities/antigravity/soul.yaml`. Note its honesty flag: the
  Antigravity IDE **plugin remains banned** from the provider fabric per D-1
  (2026-06-29); only the IDE is admitted, as a Council peer. The card says so.
- Only `john carmack` has a recorded slot. **9 of 10 seats are `unassigned`**,
  and each card cites that authority.

---

## §7 — Tooling

```bash
.venv/bin/python scripts/a2a_agent_cards.py                # validate all (exit 1 on violation)
.venv/bin/python scripts/a2a_agent_cards.py --list         # seat × skill capability matrix
.venv/bin/python scripts/a2a_agent_cards.py --publish      # write local discovery index
.venv/bin/python scripts/a2a_agent_cards.py --diff         # index drift, writes nothing
.venv/bin/python scripts/a2a_agent_cards.py --json         # machine-readable report
```

Guarantees, each test-covered:

- **M23** — every violation is `file: field.path: what's wrong [spec §x.y]`;
  exit 1; **no index is published from invalid cards**; nothing is coerced,
  defaulted or auto-repaired.
- **M8** — no network egress. The module imports no socket, urllib, http,
  httpx or requests; a test asserts this structurally.
- **M28** — cards are **read-only** to the tool under every flag combination
  (tested). `--diff` reports index drift without writing. Publishing is an
  atomic `mkstemp` + `os.replace`, so a reader never sees a half-written index
  and no temp file is leaked.
- **`--json` can go red** — it emits a JSON report on failure too. A machine
  surface that printed nothing on error would be indistinguishable from a crash.

`REQUIRED_SEATS` is an explicit tuple, not "whatever is in the directory", so a
**deleted** card fails validation instead of quietly shrinking the fleet's
declared surface. Unexpected extra files are reported as warnings and never
deleted.

### 7.1 The index is deliberately NOT committed

`.gitignore:116` carries `data/coordination/*`, with only selected `*.md`
files un-ignored. The repo therefore classifies `data/coordination/` as
**runtime state, not source**, and `data/coordination/a2a/agent_index.json`
inherits that rule. We leave it untracked rather than force-adding it, for
three reasons:

1. **Repo policy already decided this.** The path is excluded by design; a
   `git add -f` would be a unilateral override of a maintainer choice.
2. **Zero information content.** The index is 100% derived from the cards.
   Anything that matters is reviewable in the card diffs themselves.
3. **No test depends on it.** `test_committed_index_matches_the_cards`
   skips when the file is absent, so removing it from version control costs no
   coverage.

It is nevertheless **byte-deterministic** (no wall-clock timestamp unless
`--stamp` is passed), so anyone can regenerate it and diff it against a
colleague's copy with zero noise, and `test_index_is_byte_deterministic`
locks that property in. Anyone wanting a tracked copy should first raise the
`.gitignore` policy change explicitly rather than smuggling a `-f` add.

### 7.2 A permissions note worth keeping

`mkstemp` creates files as `0600`. Left alone, the published index would have
been owner-only — inconsistent with every other data artifact in the repo, and
a quiet breakage for any local tooling running as another user. `publish()`
therefore `chmod`s the temp file to `0644` **before** the atomic swap.

---

## §8 — Data integrity guarantees

`tests/test_a2a_agent_cards.py` (80 tests, all passing) asserts:

- all 10 cards load and validate with **zero** errors;
- every §4.4.1 required field is present in every card;
- no card carries a v0.3 field;
- every interface has `url`/`protocolBinding`/`protocolVersion` over HTTPS;
- every skill has non-empty `tags` (§4.4.5 + §5.7);
- `provider` has both required members (§4.4.2);
- every `securitySchemes` entry is a valid oneof (§4.5.1), and any
  `mtlsSecurityScheme` carries **only** `description` (§4.5.6);
- **every `hub_tools` name is a real `@mcp.tool` registration** found by parsing
  `mcp_servers/omega_hub/hub_tools/` — the fabrication guard;
- slot assignment is exactly `{john_carmack: S3}` and everything else
  `unassigned`;
- no card claims an official A2A binding, and none emits a signature;
- the committed index matches the cards (stale index fails the suite);
- CLI exit codes, located error text, and the located
  `verity.json: skills[0].tags: … [§4.4.5]` message shape.

---

## §9 — Sources

**Normative**
- A2A v1.0.0 specification — <https://a2a-protocol.org/latest/specification>
  §4.4.1 AgentCard · §4.4.2 AgentProvider · §4.4.3 AgentCapabilities ·
  §4.4.4 AgentExtension · §4.4.5 AgentSkill · §4.4.6 AgentInterface ·
  §4.4.7 AgentCardSignature · §4.5 Security Objects · §5.4 Error Mappings ·
  §5.5 JSON Field Naming · §5.7 Field Presence · §5.8 Custom Bindings ·
  §8.1–§8.6 Discovery/Signing/Caching · §11.3.4 Agent Card (REST) ·
  §14.1.1 Media Type · §14.2.1 A2A-Version · §14.3 Well-Known URI.
- §1.4 makes `spec/a2a.proto` the authoritative normative definition; the
  markdown spec is the human-readable rendering of it. Where they could diverge,
  the proto wins.

**Implementation practice**
- a2a-python `A2ACardResolver` (default `agent_card_path='/.well-known/agent-card.json'`, accepts a `signature_verifier`) — <https://a2a-protocol.org/dev/sdk/python/api/a2a.client.card_resolver.html>
- a2a-python `a2a.utils.signing` (`ProtectedHeader`, `create_agent_card_signer`, `create_signature_verifier`; verifier succeeds if ≥1 signature valid) — <https://a2a-protocol.org/latest/sdk/python/api/a2a.utils.signing.html>
- a2a-go v2 `a2aclient/agentcard` (`Resolve` defaults to the well-known card path; `WithPath` to override) — <https://pkg.go.dev/github.com/a2aproject/a2a-go/v2@v2.1.0/a2aclient/agentcard>
- a2a-go v2 `a2a` types (`SupportedInterfaces`, `ExtendedAgentCard`, `Tenant` with `json:"..."` camelCase tags) — <https://pkg.go.dev/github.com/a2aproject/a2a-go/v2@v2.0.1/a2a>
- a2a-samples `sign_and_verify_agent_card` — server canonicalizes with JCS then signs with JWS — <https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/sign_and_verify_agent_card>
- A2A tutorial §3 "Agent Skills & Agent Card" (`supported_interfaces` = ordered list of A2A-reachable endpoints) — <https://github.com/a2aproject/A2A/blob/main/docs/tutorials/python/3-agent-skills-and-card.md>
- A2A issue #160 (`.well-known/agent.json` — the **v0.3** path, evidence of the rename) — <https://github.com/a2aproject/A2A/issues/160>

**Local secondary reference** (field-name cross-check only; the spec is
normative): litellm's vendored resolver at
`.venv/lib/python3.13/site-packages/litellm/a2a_protocol/card_resolver.py`,
which defines `AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent-card.json"` and
`PREV_AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"`, and reads
`supported_interfaces`.

**Repo facts cited**: `config/wads/_omega_default/entities.yaml` (slots, roles,
domains), `config/omega.yaml` (`mcp.hub_port: 8016`),
`config/lan_exposure_allowlist.yaml` (8016/8019 as `tailscaled` Serve routes,
tailnet addresses), `mcp_servers/omega_hub/hub_tools/*.py` (63 `@mcp.tool`
registrations), `data/entities/antigravity/soul.yaml`,
`data/entities/makali_fusion/soul.yaml`.

---

## §10 — Follow-on work, if compliance is ever wanted

Not in scope for P1-2. Listed so the gap is actionable rather than decorative,
and deliberately **not** estimated as committed work.

1. Decide whether Omega wants A2A at all, or whether MCP + mesh identity is the
   intended terminal state. **This ticket's honest output is compatible with
   "never"** — that is a legitimate answer.
2. If yes: a seat-level adapter translating MCP tool calls into the §4.1 data
   model (`Message` → `Task` → `TaskStatusUpdateEvent`/`Artifact`), so
   `message/send` and `message/stream` become real.
3. Then, and only then: declare an official `protocolBinding`, flip the three
   capability booleans truthfully, and serve `/.well-known/agent-card.json`.
4. Signing last — it is the least valuable and the most expensive (JCS + JWKS +
   rotation) and buys nothing until 1–3 are real.
5. Whatever is chosen, update the `a2a_conformance` value in all 10 cards and
   `scripts/a2a_agent_cards.py` in the same commit, so the declaration and the
   implementation cannot drift apart.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ AP-A2A-AGENT-CARDS-v1.0.0 ⬡ 2026-10-03 ⬡ A2A-informed, NOT A2A-compliant*
<!-- PROVENANCE-CORRECTED 2026-10-04T04:03:43Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: space-bunny-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

