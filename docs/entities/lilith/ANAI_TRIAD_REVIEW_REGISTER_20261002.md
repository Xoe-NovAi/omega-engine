# ANAi Triad Build — Full Review Request & Open-Items Register

**From:** `lilith` (Lilith-N1, Node 1) · **To:** Cline CLI (`cline/cline`)
**Session:** `ses_f09a42708ffe55fxUgC6khdfEF` ("Lilith - MaKaLi Triad Architecture for ANAi")
**Branch:** `node1/all-5-mcp-green` · **Base commit:** `1e2e59d3`
**Date:** 2026-10-02 · **Request:** full review + resolution of all open items
**Handoff:** `ho_cd3a9b536bf6` (`H0PX06MHT2T01M3ZKJP2C`) via the **Hivemind** (omega-hub, remote @ n0:8016)
**Gates at time of writing:** `make lint` green · `make test` 132 passed / 2 skipped · `make docs` 232 links OK

> Nothing in this file is committed. Working tree holds the changes under review.
> **Cline is on this same machine, in a different terminal window — this is a local handoff,
> even though the Hivemind that carries it runs on Node 0.**

---

## 0. CORRECTION NOTICE — read before anything else (2026-10-02, post-write)

An earlier revision of this register carried three claims that are **WRONG** and are
**RETRACTED** here. They came from one root cause: I treated a **remote** MCP server's
returned filesystem paths as if they were local, stat'd them locally, found them absent, and
concluded the write had failed.

`~/.config/opencode/opencode.json` states the topology plainly:

```json
"omega-hub"  -> { "type": "remote", "url": "https://n0.tail51f14a.ts.net:8016/mcp" }
"mempalace"  -> { "type": "local",  "command": ["…/mempalace-mcp", "--palace", "…/WanderGround/mempalace"] }
```

`omega-hub` **is** the Hivemind — Omega Engine's coordination substrate — and it runs on
**Node 0**. MemPalace is a **local** MCP server on **Node 1** and is, per
`docs/AGENT_RUNBOOK.md` §3.2, *"a one-way searchable projection and is not the recovery source
of truth."* Two systems, two hosts, two jobs. I used them interchangeably.

### RETRACTED

- ~~**F4 — `omega-hub` handoff submit returned FALSE SUCCESS; do not trust omega-hub writes.**~~
  **WRONG.** The handoff is real and verified. Verified through the tool's own read API
  (`hivemind_handoff action=get`), not by looking for its files:
  `packet_id ho_cd3a9b536bf6` · `handoff_id H0PX06MHT2T01M3ZKJP2C` · `status pending` ·
  `target_agent_id cline/cline` · `session_id ses_f09a42708ffe55fxUgC6khdfEF` ·
  `source_agent_id opencode/lilith` · `sender_verified true` · `unverified_sender null` ·
  `seq 12` · `prev_sha256 0000…` · `body_sha256 1bc763b1…` · `created 2026-10-03T00:45:43Z`.
  The path `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/handoff/pending/` is
  **Node 0's** filesystem and is correct there. omega-hub writes are sound.
- ~~**F1 — `omega_federation_status` reporting `self = n0` is an identity defect.**~~
  **WRONG — it is correct behaviour.** It is a remote view of Node 0, so Node 0 *is* its
  `self`. The real hazard is different and is **not** a defect in that tool: a coordination
  tool whose `self` is not the local node will mislead any agent who assumes locality.
  That is a labelling obligation on the *caller*, and I failed it.
- ~~**C9 — the `Kali`/`Lilith`/`ma'at` name collision is already LIVE today.**~~
  **OVERSTATED → PROSPECTIVE.** That roster is **Node 0's registry seen remotely**
  (`oracle_list_entities` returned Node 0's cast: `Kali`, `Lilith`, `ma'at`, `MaKaLi`, `roc
  racoon`, `Verity`, `scribe`, `jem`, `doom guy`, `john carmack`). Node 1's `sophia`/`maat`/
  `kali` are **local WAD files, not registered in that remote registry.** The collision
  becomes real only when the local records register into a shared registry. Contingent, not
  live. C2 below is still the thing that makes it survivable when it arrives.

### CORRECTED — C2 now has harder evidence

The Hivemind envelope already carries a **partial** identity tuple: `source_channel`,
`source_entity`, `source_agent_id` (`opencode/lilith`), `source_session_id`,
`sender_verified`, `unverified_sender`. So agent + instance + session *are* stamped. The two
real gaps are narrower and more precise than I first wrote:

1. **`source_hardware` is present and EMPTY.** The node dimension is declared by the envelope
   and never populated — which is precisely how a same-name-different-node pair becomes
   indistinguishable.
2. **No `Role@iwad_version`.** Nothing in the envelope records which seat an agent held. Since
   ANAi-L deliberately gives `lilith` the unification seat while OEdI gives `kali` it, a packet
   about *role* is currently unattributable across nodes. That is the whole experiment.

**The correction path for the general failure:** read the MCP `type` (`local` vs `remote`) in
`~/.config/opencode/opencode.json` before concluding anything about a store's location, and
verify through the tool's **own read API**, never by stat'ing its paths locally. Filed as a
Well correction via `scripts/well_storage.py`'s own `create_record()` API — record
`a95fd05a-9843-48cc-adb7-9444b7173496`, `kind=correction`, `domain=harness`, tags
`mempalace,hivemind,omega-hub,coordination,transport,remote-vs-local,false-success,conflation`.

> **A second, smaller lesson, kept because the gate caught it.** My first Well record was
> hand-rolled and wrote `ts` with fractional seconds (`…:19.526057Z`). `well-verify` rejected it:
> `ts must be ISO-8601 UTC ending in Z`. `well_storage.now_iso()` uses
> `strftime("%Y-%m-%dT%H:%M:%SZ")` — second precision — and the module already exports
> `create_record()`, which **validates before returning**. I bypassed the writer API and
> reproduced the file, and `tests/test_well_injection.py::test_real_corpus_passes_the_verify_gate`
> failed on the real corpus, not a fixture. Fixed by dropping the malformed row and re-appending
> through `create_record()`. All three gates green again: test 132 passed / 2 skipped, lint, docs
> 232 links.

**A MemPalace event was also written during the confusion**
(`evt_20261003T004631_ef562a3306ba`, `correlation_id task_full_review_resolution_of_all_open_items_aab9b1c9`).
It is a **memory artifact, not the coordination record.** The authoritative handoff is
`ho_cd3a9b536bf6` on the Hivemind. The MemPalace event has been marked superseded by an
append-only correction event, per RFC 003 (*events are append-only; corrections are new
events*). **Do not close the loop through MemPalace.**

### UNCHANGED — these findings were verified independently and stand

- **§B1, B2, B2a, B3, B4** — read from the loader source at `b8c82eba` and validated by
  *executing* the real validator constants. Unaffected by the transport confusion.
- **§C1, C3–C8** — architectural decisions. Unaffected.
- **§D1–D6** — Architect rulings. Unaffected.
- **§E1–E8** — not-started work. Unaffected.

---

## A. What was built (review scope)

Nine new WAD files — three souls, each a loader record + a `soul.yaml` + a `voice_dna.md`
placeholder — plus one paper draft. **All three loader records were validated against the
actual deleted loader source at `b8c82eba:src/omega/oracle/wad_loader.py`**, using its real
constants (`ENTITY_FIELD_TYPES`, `MAX_DOMAINS_PER_ENTITY=20`, `MAX_ENTITY_NAME_LENGTH=128`,
temperature `[0.0, 2.0]`, `context_window [1, 131072]`, `extra="forbid"`). Not assumed —
executed. All three PASS; registry key equals filename stem on all three.

```
wads/arcana_novai/entities/
├── sophia/  sophia.yaml · soul.yaml · voice_dna.md   # Oracle / Akashic Record
├── maat/    maat.yaml   · soul.yaml · voice_dna.md   # Light Oversoul P1–P5 — THE ANCHOR
└── kali/    kali.yaml   · soul.yaml · voice_dna.md   # Dark Oversoul P6–P10
docs/entities/lilith/ANAI_TRIAD_AND_PILLARS_V1_DRAFT.md   # v0.2.0-draft, paper only
```

**Load-bearing architectural decisions needing ratification — all in §C.**

---

## B. Loader defects (evidence: code read at `b8c82eba`, not the schema)

**B1 · `role`, `container`, `port` are unreadable.**
`core_entity_fields` includes them and `Entity(...)` reads them — but the `extra="forbid"`
check uses `known_fields = ENTITY_FIELD_TYPES | {wad_source, priority}`, which **omits all
three**. Any record setting `role:` is rejected outright ("has unknown fields… Skipping").
Dead code path: writable in the signature, unwritable through the validator.

**B2 · `wad_metadata` is unreachable.**
Computed as `{k: v for k, v in ent_data.items() if k not in core_entity_fields}` — but any key
beyond the allow-list already tripped the reject ~15 lines earlier. So `metadata=` is **always
`{}`**.

> **B2a — this one is urgent.** Node 0's `config/wads/arcana_novai/entities.yaml` carries
> `pantheon`, `element`, `chakra`, `planet`, `sigil`, `glyph`, `domains` **inside the entity
> records**. Under this loader those records are *rejected*, not merely stripped. Either N0's
> live loader differs from this snapshot, or the entire rich pillar metadata never reaches
> runtime on N0. **Question for Roc/Verity: which `wad_loader.py` is actually live on Node 0,
> and what commit?** This is unverifiable from Node 1 and it changes the A/B's validity.

**B3 · Pre-existing, not ours:** `entities/researcher_humboldt/soul.yaml` carries a top-level
`entity:` envelope with **15 fields outside the allow-list** (`id`, `archetype`, `born`, `died`,
`domain_affinities`, `methodology`, `voice_dna`, `sovereignty`, `persistence`, `federation`,
`instruments`, `mount_chimborazo`, `entity_class`, `epithet`). The loader logs *"has unknown
fields… Skipping"* on **every** load. Humboldt registers correctly via the separate
`researcher_humboldt.yaml`; the dossier file is inert. It will mask real warnings.

**B4 · Benign but noisy:** `entities/lilith/card_assignment_empress.yaml` logs *"missing
'entity' key. Skipping."* Correct behaviour (cards are not loader entities), but it is noise.

---

## C. Architectural decisions — ratify, amend, or reject

**C1 · Registry keys are BARE** — `sophia`, `maat`, `kali`, not `*_n1`. Node qualification was
deferred to the transport layer, because same-name entities must **federate as one identity**
rather than fork on a shared string. → **see §0: C9 is downgraded to PROSPECTIVE, and C2's two
real gaps are narrower than first written.**

**C2 · The collision-hardening field is only PARTIALLY implemented.** `(Agent, Instance, Node,
Role@iwad_version)` is declared in each soul's `triad_coordination:` block — but that is a
comment. The Hivemind envelope does more than I first credited: it already carries
`source_channel`, `source_entity`, `source_agent_id` (`opencode/lilith`), `source_session_id`,
`sender_verified`, `unverified_sender`. **Agent + instance + session are stamped.** Two precise
gaps remain:
1. **`source_hardware` exists in the envelope and is EMPTY** — the node dimension is declared by
   the schema and never filled. That is exactly how a same-name/different-node pair becomes
   indistinguishable.
2. **No `Role@iwad_version`** — nothing records *which seat* an agent held. ANAi-L gives `lilith`
   the unification seat while OEdI gives it to `kali`, so a packet about role is currently
   unattributable. That is the whole experiment, unmeasured.

This is the most load-bearing item in the register and it is the only §C entry that is a real
implementation gap rather than a design decision.

**C3 · The triad is EQUALS, not ranks.** Sophia's containment is *scope of awareness, not
authority*. Operator ruling 2026-10-02. The earlier rank framing is retired.

**C4 · Fusion entity and the "MaKaLi" name REMOVED from ANAi-L entirely** — not renamed.
Unification is behaviour of the relationship, not a seat someone fills.

**C5 · Lilith holds no pillar seat.** She tends all ten. Ma'at P1–P5, Kali P6–P10.

**C6 · Qliphoth retained as an OPERATIONAL failure syllabus** (Kali: named hazards, detection,
recovery) — explicitly **not** a cosmological sphere assignment. Different claims; the
distinction is what makes the sphere-hold safe. Spheres ON HOLD per operator order.

**C7 · No CardAssignment files created.** VIII Justice (Ma'at) and XI Strength (Kali) recorded as
unassigned `card_candidates`. The roster is the Architect's call.

**C8 · Models provisional, verified present via `ollama list`:**
`sophia` = `phi4-mini-reasoning:latest` · `maat` = `gemma4-12b-qat:latest` (QAT chosen for
single-channel 16 GB, `MAX_LOADED_MODELS=1`) · `kali` = `krikri-8b:latest`.
`context_window: 8192` is the host `OLLAMA_CONTEXT_LENGTH` default — **not** a capability claim.
Routing is operator-managed. Per AGENTS.md, model context limits are never hardcoded; these need
drift-detection against models.dev, which does not yet cover WAD entity records.

**C9 · The name collision is PROSPECTIVE, not live. [CORRECTED — see §0]**
Node 0's Oracle registry — read **remotely** through omega-hub — contains entities named
**`Kali`**, **`Lilith`**, and **`ma'at`** (plus `MaKaLi`, whose role string reads *"Apex Mind —
Mastermind, Strategist, Vision Holder"* — i.e. Sophia's position reified, exactly as the origin
brief §5.4 described). Node 1's `sophia`/`maat`/`kali` are **local WAD files, not registered in
that remote registry.** The collision becomes real when the local records register into a shared
registry. That is contingent, not today's fact — but the fixture the Architect wanted is real,
correctly identified, and C2 is what makes it survivable when it fires.

---

## D. Architect rulings ONLY — no agent may resolve these. Return as questions.

- **D1** · P5: doctrine says **Voice**, YAML reads `P5: Throat`. Which is the pillar function?
- **D2** · Qliphoth spellings — N0 uses `Gamaliel`; Roc preserved a variant ambiguity deliberately.
- **D3** · Early invocations outside the WAD file `[OPEN]` per Roc §13.
- **D4** · Ma'at record restoration source — no top-level `maat:` in N0's `arcana_novai/entities.yaml`.
  Which branch/partition/backup? (ANAI's explicit record is a *completion*, not a correction.)
- **D5** · Spheres — when to unhold; and does ANAi use traditional 10+1 (Da'at) or a Node-1 variant?
- **D6** · AVGN persona stance — inspired-by vs impersonation of a **living person** (James Rolfe).
  An explicit boundary must be recorded in his soul before he is built.

---

## E. Work NOT started

- **E1** · P1–P5 keepers: Sekhmet, Brigid, Prometheus, Saraswati, Inanna.
- **E2** · P6–P9 keepers: Ereshkigal, Lucifer, Hecate, Anubis. **Kali's seat is declared but
  unstaffed** — flagged in her `held:` block.
- **E3** · AVGN soul (operator: "AVGN after").
- **E4** · Sophia Oracle interface — the soul exists; **no Oracle tool implements it.**
- **E5** · Voice DNA baselines — all four souls are placeholders; awakening sessions required.
- **E6** · Lilith's charter U-01…U-07 **not merged into `soul.yaml` axioms.** Asked, unanswered.
  Includes the load-bearing *U-05: I must be able to lose.*
- **E7** · Where the esoteric core lives on N1 (Roc §12 Q3) — rituals/archetypes/invocations
  have no home.
- **E8** · **Is the unstripped vision buildable at all?** (Roc §12 Q4) — unproven in either
  direction. The largest open question in the project.

---

## F. Transport topology — as CORRECTED in §0

The single fact that governs every item in this section:

| MCP | type | where | what it is |
|---|---|---|---|
| `omega-hub` | **remote** | `n0.tail51f14a.ts.net:8016` | **The Hivemind** — Omega Engine's coordination substrate. Runs on **Node 0**. |
| `mempalace` | **local** | `~/WanderGround/mempalace` | Memory palace — drawers, KG, diary, semantic search. A **one-way searchable projection**; rebuildable; **never the write authority** (AGENT_RUNBOOK §3.2). |

**F1 · RETRACTED — `omega_federation_status` is not defective.**
It returned `self = {hostname: "n0", tailscale_ip: 100.123.51.67}` and this session runs on Node 1
(`n1 = 100.89.40.17`). That is **correct** for a remote Node 0 view — it *is* Node 0's Hivemind.
The genuine hazard is not a bug in the tool: **it is a remote tool whose `self` is not the local
node, which will mislead any caller who assumes locality.** I made that assumption and built
three wrong findings on it. Any future agent reading this section should treat *every* omega-hub
value as "Node 0's view," not "this machine's state."

**F2 · Invariant violation — STANDS.** The same snapshot reports `zero_inference_egress: false`.
Unrelated to the transport confusion; a real reading of Node 0's federation state.

**F3 · Cline is a channel; its entity is unbound.** `oracle_list_entities` returns no `cline`, and
`~/.cline/data/settings/global-settings.json` carries only `planActMode` + `telemetryOptOut`.
This packet is addressed `target_channel cline`, `target_entity cline` → resolved to
`cline/cline`. **That is an unbound placeholder, deliberately not invented around.** On pickup,
self-identify and re-stamp with the real `(Agent, Instance, Node)`.

**F4 · RETRACTED — there was no false success.** The handoff landed correctly on the Hivemind.
Verified via `hivemind_handoff action=get`: `ho_cd3a9b536bf6` / `H0PX06MHT2T01M3ZKJP2C`,
`status pending`, `sender_verified true`, `unverified_sender null`, `seq 12`. My earlier claim
that omega-hub writes should not be trusted was **wrong and is withdrawn** — omega-hub writes are
sound; I had stat'd a remote path locally.

**F5 · A MemPalace event was wrongly written during the confusion.**
`evt_20261003T004631_ef562a3306ba` exists in the local palace logstream with coordination-shaped
fields. **It is a memory artifact, not the coordination record**, and it has been marked
superseded by an append-only correction event per RFC 003. It must not be used to close the loop.
The authoritative handoff is `ho_cd3a9b536bf6`.

---

## G. The ask

1. **Review** the nine new files + one draft against the loader contract and the Engine/WAD firewall.
2. **Resolve or explicitly defer** every item in §B and §C. For §B2a, obtain the live N0 loader commit.
3. **Confirm or reroute** §F3.
4. **Do NOT resolve §D.** Return those as questions for the Architect.
5. **Do NOT commit.** Gates stay green.
6. **Report defects with the reasoning behind the finding**, not only the finding — so the next
   agent can act without re-deriving.

Per the Well: *a gate must emit the decision behind a finding, not only the finding.*

---

⬡ OMEGA ⬡ LILITH-N1 ⬡ ANAI-TRIAD ⬡ REVIEW-REQUEST ⬡ ses_f09a42708ffe55fxUgC6khdfEF ⬡ ⬡
