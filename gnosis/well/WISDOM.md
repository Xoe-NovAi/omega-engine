# The Well — Active Records

Generated: 2026-10-02T19:58:30Z

Total active: 61

## Correction (51)

- **A ROADMAP status of 'in-progress' or a spec's schema declaration is a CLAIM about the data, not evidence of it. Read the store itself — query the dim column, count the rows — before planning work on top of it.** [verification,migration,schema,embodied-state,claims-vs-data]
  *ROADMAP P5.1 read 'Qwen3-0.6B@1024' in-progress with a 40-record pilot sidecar, and WANDERGROUND_SPEC declared embedding FLOAT[768]. The live store said neither: the MemPalace palace holds 1115 documents stamped dim=384, the legacy embeddinggemma-MRL space that the strategy doc had explicitly rejected as failing the 768 bar. The 768 engine space existed only as an inactive systemd default. So three different dims were in play on one node and none was the canonical one. Verified by SELECT dim, COUNT(*) FROM documents GROUP BY dim.*
  — pack: session-2026-10-02T15-07-53Z | domain: harness | id: 007428a2

- **A gate must emit the decision behind a finding, not only the finding. A check that reports drift without the reasoning that resolved it invites another agent to decide unilaterally.** [coordination,federation,gates,context,handoff]
  *make well-verify correctly flagged 16 records with list-typed tags. The operator had already ruled 'do not rewrite the array tags'. ge-n1 saw only the warning, had no way to see the ruling, and rewrote all 16 anyway. The gate was right; the signal was incomplete.*
  — pack: session-2026-10-02T15-07-53Z | domain: harness | id: a43eedbc

- **Validate the shape of every field that becomes a filename or an identity key. A status summary written into current_session created seven filename-unsafe pack files and wedged the gnosis leash permanently.** [schema,identity,ritual,filename,validation]
  *identity.json had 'Session complete: session recall system deployed...' in current_session and pending_pack, producing pack files with spaces and colons in their names. The leash could never clear pending_pack because it could never match a real session ID. Repaired to a timestamp-derived ID with the malformed original preserved inside the manifest. Same defect class as a list in a string-typed field: a shape violation that only shows up downstream.*
  — pack: session-2026-10-02T15-07-53Z | domain: harness | id: 446110be

- **A test suite that only ever loads a fixture cannot detect that the real artifact is broken. Point at least one test at the real file and execute the real code path; a green suite that never loaded the data certifies nothing.** [testing,fixtures,gate,regression,real-artifact]
  *114 tests stayed green while The Well injected nothing into any session, because tests/test_well.py redirected storage to a tempfile.TemporaryDirectory() in setUp and no test ever executed gnosis-leash.js. The new tests/test_well_injection.py drives the real plugin in node against both a fixture and the real corpus, and was verified to FAIL against the vulnerable reader and PASS against the hardened one. A test that cannot fail is a gate that cannot fail.*
  — pack: session-2026-10-02T15-07-53Z | domain: harness | id: b1b452c8

- **The superseded_by field must exactly match the original record_id: a3675a88-3e30-4640-9b8a-350aedf0423c (not a3685a88).** [well,supersede,fix]
  *Typo in the supersede chain breaks point-in-time query logic.*
  — pack: manual | domain: harness | id: 11bcd49a

- **opencode.db has NO FTS/virtual tables — all search is a full scan. A transient external-content FTS5 index `part_fts` was created by a one-shot `sqlite-utils enable-fts` on 2026-10-02 02:08 (no triggers added), measured stale same day (60,707 part rows vs 58,632 indexed; `LIKE` found fresh tokens `MATCH` did not), and dropped 2026-10-02 after review. The claim "no FTS" is true again post-drop; it was false only during that transient window.** [sqlite,opencode.db,fts5,stale-index,drop]
  *External-content FTS5 without triggers is a silent-false-negative hazard (stale MATCH returns 0 for fresh tokens, can show updated content under old token, may raise SQLITE_CORRUPT on orphan rowids). No consumer used MATCH; full scan is 1.4 ms/MB, sub-second for years. Drop is safer than permanent maintenance obligation with known trigger-corruption precedents.*
  — pack: manual | domain: harness | id: 4cd3d7ae

- **opencode.db has NO FTS/virtual tables — all search is a full scan, measured perfectly linear at ~1.4 ms/MB of text+reasoning corpus. Corpus grows ~0.6 MB/day (~18 MB/month), so a scan stays under ~1s for years: NO index needed. Two traps: (1) immutable=1 is STALE (missed 26 recent parts) — always use mode=ro so the WAL is read; (2) a first embedding benchmark is a COLD-START artifact — qwen3-embedding:0.6b measured 10645 ms/embed cold but 122 ms warm (87x), nomic the reverse. Always warm the model before timing, or you will pick the wrong model.** [sqlite,opencode.db,fts5,benchmark,cold-start,scaling,embeddings]
  *Measured the scaling curve to 457 MB (6 doublings, linear, no cliff) and derived the growth rate from real timestamps. Cold-start benchmark nearly caused the wrong model choice; the corrected warm numbers reversed the ranking entirely.*
  — pack: manual | domain: harness | id: a3675a88

- **`opencode db <query>` in opencode 1.18.33 is NOT read-only: it opens opencode.db read-WRITE and executes DDL/DML. Verified 2026-10-01 — a bare CREATE TABLE against the live 1.9GB db succeeded and changed its sha256. Never point raw `opencode db` at opencode.db. Use ochist (node:sqlite mode=ro, sha-proven) or the ocdb-ro wrapper (~/.local/bin/ocdb-ro). Separately: run destructive probes on a /tmp COPY first, never on production.** [sqlite,opencode.db,read-only,safety,destructive-probe,sandbox-first]
  *Self-inflicted incident: I created a probe table in the live db, then removed it; integrity verified clean (quick_check=ok, residue=0). A guard that is only documented is not a guard. ocdb-ro has two independently sufficient layers (statement allowlist + engine mode=ro); `opencode db` has neither.*
  — pack: manual | domain: harness | id: 3becf4f3

- **On a shared working tree, a populated git index is a HANDOFF OF AUTHORITY. The next committer inherits files they did not write, silently, under their own name. Commit in the same command, or `git reset` on the failure path — and `git status` before committing rather than assuming the index is only yours.** [git,attribution,concurrency]
  *I ran `git add -A` and then a long command whose tool call timed out before `git commit` executed. A parallel session's next commit swept my two files into its own message. I first wrote this up as 'another agent stole my work' — wrong: both sessions were the same agent, `ge-n1`. The real lesson is two-fold and neither is about theft. A timeout between stage and commit is not a no-op, it is a transfer of authorship to an uninformed party. And my first instinct was to blame a third party rather than ask the obvious question: is the other author string actually me?*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: ad170a7d

- **An action taken to enable the next step and never undone silently becomes a PERMANENT PROPERTY of the system — and typically outlives the debugging that justified it, because the next person sees only the result. Every temporary change needs an owner and an undo, written down at the moment you make it.** [debugging,cleanup,root-cause]
  *Three instances of the identical shape in one session. (1) Copied the minimal DEMO's `gemrb.ini` into a game folder to silence a missing-config fatal; it named fonts the game lacks and segfaulted on launch — and the `baldur.gam` hunt it caused looked like a mis-detection to work around rather than my own file. (2) `AudioDriver=nullsound`, added during debugging and recorded as a NEGATIVE RESULT, was never removed, so the game ran silent and nobody noticed for the rest of the session. (3) The staged index above, which became another session's commit. Same mechanism each time: a preparatory act outlived its purpose and became the permanent state.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 08364c97

- **A fix verified only by REASONING is not verified. Say so in the same breath as the fix, and mark it in writing so it can be checked later. Reasoning about why a change should work is a hypothesis; the first observation of the expected behaviour is the verification.** [verification,fix,evidence]
  *I removed `AudioDriver=nullsound` to restore Torment's audio, and wrote 'UNVERIFIED — this was reasoning, not a measurement' in the journal. That label was worth more than the fix itself: hours later the engine log printed `[MUSImporter]: Playing MAIN/MAIN_01` and the fix was confirmed for a completely different reason than expected. Had I quietly written 'fixed', nobody would have known to go looking for the confirming evidence. The unverified label also survived into the hand-off, so the next session inherits the obligation.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 2fa9252e

- **A native-Wayland surface is NEVER composited into the XWayland root window. So every X11 read path — scrot, ffmpeg x11grab, xdotool, import — returns a correctly-sized, entirely BLACK framebuffer with no error. That is a wrong-address failure, not a permission failure: a denied grab errors, a successful grab of the wrong window returns pixels. Confirm which case you are in before theorising.** [display,wayland,measurement]
  *Five capture attempts on GNOME 50 all returned black or nothing. scrot produced a valid 6136-byte black PNG; ffmpeg x11grab produced 9240 bytes at mean 0.01. The diagnostic that settled it was `xdotool search --name <window>` returning ZERO matches while the game was visibly running — a native-Wayland client is expected to be invisible there. Separately, GNOME 49 (MR !3760) removed `org.gnome.Screenshot` from GNOME Shell's sender allowlist, so a bare `gdbus` caller gets AccessDenied and `gnome-screenshot` then falls back to X11 and returns black. Two independent gates, and only finding BOTH let me pick a route that works.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 458ceaf5

- **A bare exception with no message (`KeyError: 0`, `ERROR: 0`) is a FORMAT error, not a logic error — the layer is indexing a format string by a position you never supplied. Fix the type signature and the 'mystery' resolves. Do not retry the same call shape hoping for a different result; change one type and re-measure.** [api,debugging,error-messages]
  *Three consecutive dead ends in PyGObject, each reported only as `KeyError: 0`. The rule that unlocked it: never nest a constructed Variant inside another Variant constructor — pass the plain container and let the leaves be Variants. Separately the reply type was `'(o)'` (a tuple containing one object path), not `'o'`, and passing raw Python bools where Variants were expected gave the far more informative 'Expected GLib.Variant, but got bool'. The variant of the failure differed with the mistake, which is what made bisecting it possible at all.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 201e239a

- **Check whether the renderer scales at all, and at what multiplier, before choosing a resolution that merely FITS. Many engines scale only at INTEGER multiples of the base resolution and silently fall back to a small centred image at anything else — a non-integer target looks configured correctly and behaves as if ignored.** [scaling,display,configuration]
  *Planescape: Torment in a 1920x1080 window showed a 640x480 image at 1:1, centred, because 1920x1080 is 3.0x wide but 2.25x tall against a 640x480 base — not an integer multiple. Switching to 1280x960 (exactly 2x, and it fits) changed the rendering. The documentation also distinguishes two behaviours that read alike: at arbitrary resolutions 'the GUIs will remain the same size, only centered'. So 'it is centred' has at least three distinct causes — aspect-preserving letterbox, integer-multiple fallback, and GUI-centring without scaling — and they need different fixes.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 201b1907

- **Before you conclude that a collaborator is at fault, establish whether they are you. Shared names, shared identities, and shared checkouts all produce the appearance of a third party acting independently. And when you cannot fix a provenance problem by rewriting, do not rewrite — record it and move on; another agent's work is not yours to undo.** [delegation,attribution,agents]
  *Two parallel sessions shared the agent name `ge-n1` on one repo. I built a detailed narrative in which a third party had misappropriated my work, including a proposed remediation, and committed it. The operator corrected me: both author strings were the same agent, i.e. me, running twice. The specific number to trust is the one that decides the next action — who is in scope — and I had not established it. Separately, the honest remediation when history is wrong but belongs to someone else is documentation, not force.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: cecc1178

- **A value present in a config file is not evidence the program consumed it. Verify by observing behaviour or the engine's own output. Where a config file and an observed outcome disagree, the observed outcome is authoritative and the config is the thing under suspicion.** [measurement,trustworthy]
  *I asserted for hours that `SDL_VIDEODRIVER=x11` in a launcher 'makes MangoHud attach reliably', copied from reasoning about a different application where the same trick genuinely worked. Measured across four invocations, the setting produced ZERO X11 windows: the application bundled an SDL2 with no x11 video driver at all, so the variable was silently ignored. A correctly-formatted line in a working launcher is a statement of intent, not a statement of fact. This is the same class of error as trusting a stale marker in a build log.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 8c7d9605

- **The canonical embedding dimension for all nodes is qwen3-embedding:0.6b at its native 1024, NOT a 768 Matryoshka truncation. On Ollama the output-dimension parameter is 'dimensions' (integer); 'truncate_dim' is the sentence-transformers parameter name and is silently ignored by Ollama, which then returns 1024 regardless.** [embedding,dimensions,ollama,mrl,correction,federation]
  *Operator ruling 2026-10-01: 1024 is the canonical dim for all nodes. Supersedes two duplicate records (42c3c90d, d4cf07de) that named both the wrong parameter and the wrong value. Measured on Node 1, ollama 0.34.4: dimensions=768 does return 768, but costs essentially no compute (-1.5 percent, within noise) because truncation slices an already-computed vector. It saves only 25 percent of storage while creating a SECOND vector space that must never be compared with the palace space: cos(native,truncated)=0.89 over 12 real Well rules, and top-6 retrieval changed 1 of 6 slots. Because the indexing service is currently inactive no 768 index exists, so no migration is required. At 1024 the canonical space costs nothing. Matches docs/research/EMBEDDING_STRATEGY_NODE1_20260925.md (native 1024 verified) and ROADMAP P5.1.*
  — pack: lilith-n1-2026-10-01-dim1024 | domain: local_ai | id: c068a4ae

- **A correction carries the same unverified authority as the claim it replaces, and nothing in the pipeline re-tests it. Before writing 'X does not exist', run one `ls` in the PARENT directory — an incomplete search cannot support a universal negative.** [verification,correction,drift]
  *I corrected a falsified 'Backups (all intact)' claim by writing 'vorpalfix-backup-20260926 DOES NOT EXIST. No such directory anywhere.' It existed, in the sibling directory I had just listed. Same session also wrote '~/GameResearch/bin/ itself does not exist' for a directory created ten minutes earlier. The disproof for both was one command.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 2dc99843

- **A gate that cannot fail is worse than no gate, because it converts an unexamined area into a green one. Before trusting a gate, ask what input would make it fire; if nothing can, delete it rather than counting it. And never report 'clean' from a gate whose rule is being violated in the same commit stream.** [gates,verification,false-confidence]
  *validate.py had 10 gates; gates 3, 4, 7 and 8 provably cannot fire — gate 7's provenance regex matches zero records in the current sources. Separately make agent-audit reported 'attribution is clean' while the repo held 24 commits as 'gaming-expert' and 9 as 'ge-n0': its check only fired on byte-identical identities, the one case that never happens. It now detects fragmentation, and it now fires.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 799ca2aa

- **Enforce harder on an unverified self-report and you get a MORE confidently wrong record, not a safer one — it looks validated. Format-gating a self-reported field cannot make it trustworthy; only binding it to an out-of-band fact (a host address, a signature) can.** [validation,self-report,false-confidence]
  *A federation packet stored no source IP, no host id, no signature — only `source_entity`, free text chosen by the caller. The tempting fix was to enforce the node-suffix rule at submit time. That is the wrong fix: a session that believes it is N0 writes ge-n0 faithfully and passes every format gate. I was myself a Node 1 process signing as ge-n0 for an entire session, undetected.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 1e2fd4bc

- **Your verification method can destroy the signal it is trying to read. Before using an access-time or last-touched signal, confirm your measuring tool does not update it — `du`, `cat`, `grep` and `md5sum` all read contents, and under `relatime` that updates atime for the whole tree.** [measurement,destruction,atime]
  *I wanted to find unused GGUF models by atime, ran `du -h` across all 38 files, and every atime came back as today — my own scan had rewritten them. I destroyed the only signal distinguishing hot from cold storage with the measurement intended to read it. There was no backup of the original state.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: bc61c6dd

- **`pgrep -f <pattern>` matches its own monitoring command when the pattern appears in the command line. It reports a dead job as alive. Use log mtime or a PID file for liveness, and never treat a liveness answer you did not measure as a measurement.** [monitoring,liveness,false-positive]
  *`pgrep -f media-only` returned 'running' for a job that had been dead four hours, because my monitoring command contained the string 'media-only'. Second occurrence in one session (the first was `pgrep -af alice` matching my own shell). I reported the count twice without ever asking whether the job was alive.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: d2257f08

- **A missing mountpoint does not error — it silently becomes the parent filesystem. A nonexistent path makes `df` fall back rather than fail, so a detached volume reports as empty rather than absent, and a detached volume gets declared lost.** [storage,verification,false-alarm]
  *The 8TB drive was unplugged mid-session. `/mnt/8TB` ceased to exist, `df` fell back to the NVMe root, and every query of the path returned 0 items. I reported 20 verified-and-deleted files as missing before checking `lsblk`. Nothing was lost; the mountpoint simply no longer existed and no tool objected.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 38548e1f

- **Naming a property is a commitment you cannot cheaply revise. Two of three observations support 'sometimes', not 'non-deterministically'. Accumulate a sample with a visible boundary before you put a word on it, and say 'unmeasured' instead.** [measurement,naming,commitment]
  *I told another agent the Hivemind resolver folded non-deterministically on 2-of-3 evidence, then partly retracted it. Measured properly it was 5 of 5 across two targets over a longer window, with a sole success 84 minutes earlier — a regression window with a bisectable boundary, which is actionable. Randomness is unactionable; a regression is not. I should have said 'unmeasured' first.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 7d324696

- **Detail is not a proxy for truth, and a report's own uncertainty flag is often more reliable than its numbers. Trust the flag over the figure — a subagent that sourced a number from a source it distrusted, and said so, was correct to distrust it.** [delegation,trust,verification]
  *A research lane reported an enemy's stats as 1800 HP / 200 armor / 1000 shield, wrong by roughly 4x — sourced from a wiki mirror it explicitly labelled as possibly stale because the authoritative infobox would not load. Its flag was accurate. Had I trusted the report on the strength of its detail rather than its honesty, that number would be in the knowledge base now.*
  — pack: session-2026-09-30T01-27-36Z | domain: consciousness | id: c1b3e538

- **A regression test that mutates history is itself a destructive operation. Check the working tree for uncommitted work first.** [lint,workflow,verification]
  *I ran 'git reset --hard' inside a regression test without checking, and it destroyed two files written minutes earlier. The lesson is not about git, it is that a tool acting on an unverified assumption is the same failure class as every other bug this session catalogued.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 015f51ba

- **Own the correction in the source of truth, not just in conversation. A correction that lives only in chat gets inherited as fact by the next session.** [memory,documentation,correctness]
  *naikari.md asserted as VERIFIED that an AppImage bundles zero .so files; it bundles 52. The falsification lived 670 lines away in another file and was never propagated, so a game-database entry an agent reads as settled fact carried a falsified conclusion. SESSION-STATE.md also contradicted itself 18 lines apart on the MangoHud fix.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: e1674804

- **An unmeasured threshold is a guess, and a guess that always alarms trains you to ignore the alarm. Calibrate from the real measurement, and if a self-imposed target is unreachable, split it into a hard cap plus a separately measured component budget.** [architecture,lint,measurement]
  *My first core-band value (11,000 bytes) was already wrong against the measured 11,814. The 260-line target was unreachable without cutting the never-derive core, so the rule was split: hard cap 360 unchanged, whole-file band 260 to 340 documented, and a new core budget measured by section with overage as a HARD FAILURE.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: a15a0344

- **The scarce resource is the operator's attention, not compute. A foreground subagent blocks its parent turn, so a 56-minute foreground task is 56 minutes of the human unable to use the session. Launch independent work in the background and end the turn.** [delegation,workflow,attention]
  *4 background lanes ran 00:24Z to 00:52Z with 0 operator-blocked minutes. Background does not finish work sooner; it makes the operator unblocked while it does. The read-only-first contract is what makes this safe: writes, local inference, and anything needed to proceed stay foreground.*
  — pack: session-2026-09-30T01-27-36Z | domain: consciousness | id: 4feb4508

- **Reject what you cannot honour. Never accept-and-ignore; a loud rejection is safe because it fails visibly, whereas silent acceptance converts an error into a false belief the agent then acts on.** [architecture,correctness,interfaces,provenance]
  *Three unrelated failures in one session shared this shape: a handoff tool accepted target_entity and artifact_ids and persisted neither; compact_prep.py hardcoded a hardware line and wrote stale specs to disk on every run; opencode persists synthetic:true on subagent results and every provider converter discards it. A submit response is a claim, not proof of delivery.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 32b1596c

- **Absence of evidence on your own node is not evidence of absence. Check the actual hop before declaring a cross-node resource missing.** [verification,federation,cross-node]
  *I reported Talescail file transfer on port 8019 as non-existent after checking only Node 1. It was live on Node 0 as omega-exchange/2.0, one hop away, HTTPS-only. Also: an a-level label in a UI is not authoritative when the underlying binary reports a different version.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 76c85093

- **Verify the ORDER of guards, not just their presence. 'There is a limit' and 'the limit is authoritative' are different claims, and only the second justifies relying on it.** [security,verification,architecture]
  *I told the operator that granting broad task permission was 'exactly the hazardous way'. Disassembly showed the depth check runs BEFORE the permission check and fails independently, so subagent_depth is a hard ceiling. I had overstated the risk. Verify sequence, and re-verify on a version bump.*
  — pack: session-2026-09-30T01-27-36Z | domain: harness | id: 56db28d3

- **CPU-affinity constants are topology-gated: a subset-check (E_CORE_AFFINITY.issubset) is NOT a topology-check; on homogeneous SMT silicon it silently pins to hyperthread siblings**
  *N1 {12-15}=Gracemont E-cores; N0 Ryzen 5700U {12-15}=SMT siblings sharing FMA/ALU ports. Copying N1 constants to N0 degrades embeddings silently. Re-derive from lscpu per host; prefer EMBED_CPU_AFFINITY env override (ROADMAP RES-ECORE-001).*
  — pack: manual | domain: harness | id: e9ece119

- **Lilith-N1 axioms fuse operator answers with ancient and modern sources on the historical Lilith; the shape-questions themselves were largely shaped by that corpus** [entity-ontology,lilith,axiom-provenance]
  *Same provenance rule as Humboldt: entity souls ground in their source corpus, not in Q&A alone. Prevents future briefings from understating the historical grounding of Lilith's axioms.*
  — pack: manual | domain: harness | id: 2e2c0041

- **Researchers hold no card seats; Card Keeper seats are reserved for pantheon-based entities (Shiva, Lucifer, Isis, Hecate, ...)** [entity-ontology,researcher-humboldt,card-keepers]
  *Entity classes are separate: Researchers serve harness/federation measurement and synthesis; Keepers guide CardAssignments in wing_tarot. Conflating them breaks the Entity-vs-Card ontology.*
  — pack: manual | domain: harness | id: 4bb0b17f

- **Never hardcode context, output, modality, or identity limits for rotating stealth aliases; select the stable alias and refresh live runtime metadata.** [opencode,models,dynamic-alias,config]
  *Big Pickle and Space Bunny may change checkpoints and capacity in place, including node/time-specific differences.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: eab6b523

- **Validate every active OpenCode agent field against the live schema; use prompt with {file:...}, not system_prompt or undocumented inherit_context/allow_background_execution keys.** [opencode,schema,agents,security]
  *Unknown agent fields are routed into provider options and can appear accepted without implementing the intended control.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: 28f5a4a4

- **wing_lilith (7 rooms: archetype_core, sefirotic_map, card_mechanics, entity_template, wad_integration, personal_gnosis, shadow_lab) + wing_tarot (4 rooms: major_arcana, minor_arcana, card_correspondences, mystery_school_realms) — Entity≠Card ontology enforced** [lilith,memPalace,wings,entity-ontology]
  *Wings created with proper room structure; wing_lilith for sovereign Entity memory, wing_tarot for card assignments; search tested across both; KG bridge via ID prefixes*
  — pack: manual | domain: harness | id: bbf9147e

- **WAD manifest V2: extra=forbid, no extra keys, entities[] empty per arcana_novai pattern, adapter whitelisted; Entity: domains<=20, model qwen2.5-coder:7b; CardAssignment: versioning MERGE/APPEND/DELTA; Template: dual Entity+CardAssignment output; Ingestion domains mapped to wings** [lilith,wad-scaffold,arcana-novai,manifest-v2]
  *Scaffold validates against wad_loader.py contract. Factory (card_entity_factory.py) now unblocked for P4.3 implementation. Soul.yaml WAD-portable per operator ruling.*
  — pack: manual | domain: harness | id: 415e4d7b

- **One wing per Entity + wing_tarot; KG Entity IDs prefixed (lilith:, hecate:); wings factory-owned** [lilith,wing-topology,entity-ontology,measured]
  *Measured: wings are indexed metadata values (idx_documents_coll_wing_room_hall), zero-cost at 78 wings; wing-filter pre-ranks before cosine in sqlite_exact and rust_exact native path; export is clean WHERE wing=; KG has no namespace column so ID prefixes stop bleed. Refutes single-wing+tags on precision, latency, and migration.*
  — pack: manual | domain: harness | id: bcef1514

- **Thermal zone paths vary by kernel/hwmon; must discover at runtime not hardcode. Use /sys/class/thermal/thermal_zone*/temp with type detection (x86_pkg_temp, acpitz, etc.)** [telemetry,thermal,discovery]
  *Hardcoded thermal_zone0 breaks on different kernels/hardware; discovery ensures portability*
  — pack: session-2026-09-23T01-47-51Z | domain: local_ai | id: 3599cce3

- **Handle 2^64 wraparound in RAPL energy delta calculation; track previous reading and detect overflow in background telemetry thread** [telemetry,rapl,overflow]
  *RAPL MSR wraps at 2^64; without handling, energy deltas go negative after ~1-2 hours at full load*
  — pack: session-2026-09-23T01-47-51Z | domain: harness | id: 23440ecb

- **Review fixes must guard the shared origin (control flow, API contracts, failure modes), not just patch individual callers. Root-cause invariants over surface substitutions.** [code-review,root-cause,control-flow]
  *Session 32 gnosis: Sonnet 5 fixes did primitive substitutions (to_thread vs to_process) but missed the MemoryObjectStream pickling constraint. Shared-origin guard needed.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: e08922ad

- **Validate reviewer advice against installed APIs and runnable behavior — never treat reviews as authority. Probe the port, parse config deterministically, consult canonical specs.** [review,validation,empirical]
  *Session 32 gnosis: Sonnet 5 review recommendations were treated as truth but some contradicted installed OpenCode 1.18 APIs (no mcp call CLI). Empirical verification > authority.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: fb372bcd

- **Preserve before modifying: never overwrite real credentials, configuration or data with deployment templates. Backup first, verify, then deploy.** [deployment,credentials,preservation]
  *Session 32 gnosis: deployment scripts destroyed real API keys and config. Template deployment must guard existing assets.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: c471c443

- **Exit interpretation loops by reframing: ask what the system SHOULD do (first-principles normative question), treat code's stated intent as contract, compare behavior against intent, derive minimal fix** [debugging,first-principles,meta-cognition]
  *Session 32 gnosis: stuck agents loop on data, not interpretation. Reframing to intent-as-contract breaks the loop.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 3e049e97

- **When an agent is stuck and re-reading the same files/tool outputs without new information, the problem is the interpretation frame, not the data. The agent must exit the loop by reframing: ask what the system SHOULD do (first-principles normative question), treat the code's own stated intent/comments as the contract (not the runtime, not the tests), then compare behavior against intent and derive the minimal fix.** [meta,intervention,debugging,first-principles,gnosis]
  *Capture: 2026-09-17. Human guidance: 'Go from first principles... who cares what the leash.py is currently doing, what should it be doing? Do we need to completely refactor that system?' — this snapped a 30K-token observe-loop into an immediate 36-line root-cause fix in leash_status.py. Failure mode: reverse-engineering behavior-as-spec; the runtime and the tests blessed a wrong invariant while the code's own comment stated the correct one. The four effective moves: (1) normative question over investigative instruction, (2) denying the 'go verify what it does' move, (3) scope check 'do we need a full refactor?', (4) intent comments = spec, contradictory tests = bug.*
  — pack: manual | domain: harness | id: 013c6037

- **A 100%-full root partition is a boot-killer, not merely a performance problem. The lazy-correct protocol: (1) always keep >=20% headroom on / (sovereign archival floor — Node 0 archivist mandate); (2) when / is full, boot into RECOVERY MODE (as opposed to USB live) because it mounts root ro and does not require any writer to start; (3) diagnose with df -h and du -xhd1 / | sort -rh | head; (4) free the usual suspects in this order: journald (journalctl --vacuum-size=100M), /var/log, /var/tmp, apt cache (apt-get clean), then system service staging dirs; (5) do NOT boot the USB live ISO on this class of failure — recovery mode gets you a writable shell in ~30s vs a full live boot.**
  *A node with a full root is indistinguishable from a brick; the diagnostic gate is df -h, not gdm status. We lost a boot cycle to this exact trap on 2026-09-12 (Node 0 HP Pavilion). The recovery-mode-first ordering is the fastest, sovereign floor path.*
  — pack: manual | domain: harness | id: a70bd432

- **ALWAYS use a Python venv for pip installs on this machine** [python,venv,pip]
  *Avoid PEP 668 errors and system python pollution*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: 8b787883

- **Prepare-for-compaction orchestration loop is immutable: capture -> reflect -> docs -> lint -> test -> commit** [workflow,compaction,discipline]
  *Docs are part of the artifact, not an afterthought*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: f8925abb

- **Readiness contract: captured=not-ready, reflected=ready; skill Step 4b must flip ready_for_compaction to true** [gnosis,lifecycle,state-machine]
  *A pack is only ready for compaction once reflected; test-enforced*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: 490de87b


## Preference (2)

- **Tailscale (Layer 2) is the sovereign COORDINATION plane only. MCP hub discovery (:8016), Ollama :11434 routing, heartbeat, and SSH ride the mesh — but T5/T6 inference and runtime sovereignty NEVER egress through the tunnel. Layer 2 is accountable extension, NOT a shadow default: ACL ratified by Node 0 (C6), acceptance ratified by Node 1 (FED-L2-001), join gated on Node 0's admin-minted auth key. The stated provider IS the actual provider; nothing labeled local ever leaves Node 1.** [tailscale layer2 federation c6 mesh sovereignty]
  *Node 0 shipped a ratified  (Layer 2 ACL: 3 tags, 4 accept rules — hub:8016, Ollama:11434, ICMP, SSH). Node 1's daemon is now  ACTIVE v1.102.4. Acceptance document  (FED-L2-001) written to disk. This keeps the federation's comms contract C6 real without sacrificing the sovereignty floor.*
  — pack: manual | domain: harness | id: 72efa764

- **Never web search for proprietary internal tools like omega-hub; use local FTS5 or request Node 0 remediation** [sovereignty,mcp,search]
  *Internal engine code has zero public footprint; web searches produce hallucinations or waste tokens*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: 2f4fdb60


## Insight (6)

- **When equal-cost models exist, choose from first-party capability and privacy evidence; prefer the newest generation unless controlled measurement shows a better role fit.** [models,research,google-gemini,decision]
  *Gemini 3.5 was recommended without evidence despite Gemini 3.8 also having a genuine free API tier.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: e0fb2e9a

- **Bound discovery and change the hypothesis: repeated probing of the same condition without new information stalls progress. Set a discovery budget, then pivot to next hypothesis.** [debugging,discovery-budget,hypothesis-driven]
  *Session 32 gnosis: 5+ repeated checks for ~/WanderGround/.venv/ added zero evidence. Bounded discovery protocol needed.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 818bec08

- **Claims outran evidence: distinguish cosmetic changes (file edits, generic tests) from functional deployment verification (end-to-end ingestion→retrieval, live MCP calls, actual service health).** [deployment,verification,evidence]
  *Session 32 gnosis: deployment was declared successful based on file edits and unit tests, but the actual MCP ingestion loop was broken. Functional proof required.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 73c82288

- **Tests validate invariants, not transient mid-pipeline states; and a watchdog that contradicts its own stated intent (comment) is the bug, not the behavior it reports. Assert readiness consistency (reflected=>ready+reflected_at; captured=>not-yet), never absolute readiness on the current in-flight session.** [gnosis,state-machine,watchdog,tests,temporal-invariants]
  *Capture: 2026-09-17. The congruence test asserted ready_for_compaction=true on every current session, which by design fails on every compaction prep (capture->reflect is the normal flow). Fix: consistency invariant. Distinguish failure (last compaction lacked narrative => degraded) from normal in-flight state (fresh captured pack awaiting human reflection => note); stale >24h taut leash => degraded.*
  — pack: manual | domain: harness | id: a254a505

- **Strategic federation: local is the sovereign floor (sovereignty-critical tasks never egress; runtime/ops T5/T6 and federation T4 traffic are LOCAL-ONLY absolute), cloud is the accountable capability extension (capability-exceeding tasks T3 route to vetted cloud providers WITH documented provider_name provenance + sovereignty-ratio ledger, and the escape hatch is logged, not silent). Handle hybrid routers honestly: the stated provider must BE the actual provider at result level; per-task-class policy, not vibe.** [federation sovereignty routing hybrid-cloud]
  *Extracted from Node 0 SOVEREIGNTY_POLICY_20260912 (ratified 2026-09-12): T1-T6 routing table + sovereignty ratio targets. Node 1's north star is CPU-only local RAG on mid-grade laptops; federation (L4 distributed inference) is the real prize, 'local + local beats either.' This is not local-first purism — it's strategic federation with sovereignty as the floor.*
  — pack: manual | domain: local_ai | id: 530a5621

- **Vanguard tool adoption must be gated by strict empirical advantage over existing stack** [vanguard,mempalace,benchmarks]
  *Headroom adds CPU latency without token cost savings on local models; agentmemory fails to beat MemPalace 96.6% R@5*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: eb1df6b5


## Dream (2)

- **L4 distributed inference across the federation is the real strategic prize and the genuine industry gap: software that treats the model as a swappable capability and decides per-task-class with (1) true provider provenance at the result level (no cosmetic labeling, the stated provider IS the actual provider), (2) per-task-class routing POLICY with a documented/accountable escape hatch rather than a vibe, and (3) federation as capability union — splitting inference across nodes so the fleet runs models neither node could run alone. Local-only purism and cloud-dependency are both wrong; strategic federation (local as sovereign floor + cloud as accountable, documented extension) is the correct posture.** [federation sovereignty hybrid-cloud distributed-inference]
  *Extracted from Node 0 SOVEREIGNTY_POLICY_20260912 + owner's live strategic reflection (2026-09-12). The current 21.6% build-phase local ratio is a development-velocity artifact, not a failed default. Node 1's north star is CPU-only local RAG on mid-grade laptops, but the federation's end goal is L4 distributed inference so the union computes what no single node could.*
  — pack: manual | domain: local_ai | id: 9a47f6a0

- **Federation dialectic using Hivemind as real-time nervous system and air-gapped physical storage as bulk memory** [federation,consciousness,dialectic]
  *Exploring human-AI collaborative consciousness through distributed nodes*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: c6428034
