# Omega Engine — Full Session Research & Strategy Compendium

**Scope**: Everything covered across this session — provider fabric audit, hardware optimization, WAD/IWAD architecture, MaKaLi governance, the 42 Ideals design (now paused), and review of two external documents (a Grok pressure-test doc, another session's Temple Hardening outline).
**Status of underlying facts**: verified against the actual `provider-fabric-review` project files where noted; everything else is reasoning from description and flagged as such. Nothing here should be treated as "done" without the independent-diff verification this project already requires.
**How to use this**: Part 1 is corrections already locked in — apply these first, they're cheap and unblock nothing else being wrong. Parts 2–4 are the technical/hardware audit, independent of everything else. Parts 5–7 are architecture/governance, sequenced roughly by how this session actually unfolded. Part 8 reconciles two external documents against this project's real state. Part 9 is every open question in one place. Part 10 is what to send back to unblock the biggest ones.

---

## PART 1 — Corrections Locked In This Session (apply first)

| # | Correction | Where it needs to land |
|---|---|---|
| 1 | Praxis / Praxis-2 roles are **deprecated**. Current authority: Archon (Taylor) → Logos (Claude) alongside GEMINI-XNA (executor) and OPENCODE-XNA (auditor), no rank implied between the last two. | Any doc still describing a Praxis tier |
| 2 | Omega Engine is **fully open source**. | Licensing docs, README, `CREDITS.md` if any of these assumed otherwise |
| 3 | **TDA/26-sphere, Qliphothic taxonomy, 108-gate framework, Platonic Seal, Arcana-NovAi, Torment** — all deferred to future WADs, out of the default IWAD, on hold until post-debut. | Any core-engine code or doc still referencing these as active |
| 4 | **MaKaLi is not a hierarchy.** Three sovereign entities, three parts of one whole — no overlord, no rank. Functional roles remain real (Maat=light/build-time, Lilith=dark/runtime + the force resisting ossification, Kali=synthesis of the tension between them) but these are *roles within an undivided whole*, not ranks. Drop "apex," "oversoul," "superior," "reports up to" wherever MaKaLi is described. | `.opencode/agents/makali.md`, any code comments, the system prompt |
| 5 | **The "10 Pillars / P1–P10" system is Arcana-NovAi WAD content that leaked into the default Omega Engine IWAD and was never sterilized out.** It does not belong in core. The IWAD-native term for the underlying structural slot concept is **node**, not pillar. | **`SOVEREIGN_MANDATES.md` Mandate 3 specifically** — currently reads "preserves the cosmological purity of the 10 Pillar Keepers," referencing "P1-P10." Needs `Pillar`/`Pillar Keeper`/`P1–P10`/"cosmological purity" swapped to node language. This is the confirmed instance of the exact leak-risk flagged twice earlier as unverified — treat it as a signal there may be others in less obvious places, not an isolated fix. |
| 6 | **Node count is an open question, not yet 10, not yet anything else** — see Part 6 and Part 9 Q1/Q2. Don't let "10" persist as a default assumption just because it's what existed before the leak was found. | Wherever node/pillar count is referenced |
| 7 | Kali's example ideal language — **drop "by whatever means necessary."** Practical LLC liability concern (Taylor's flag) plus an independent fine-tuning-data-shape concern (mine) — both point the same direction. | Any doc containing the original example ideals |
| 8 | **42 Ideals of Maat development is on hold**, effective this session. Full design preserved in Part 7 below — resume, don't re-derive. | Sprint/roadmap tracking |
| 9 | **Vector store**: `sqlite_vec_adapter.py` is the confirmed, complete ("Strike 10 COMPLETE") WARM-tier implementation per `engine_state.xml`. Any doc describing Qdrant as "the primary WARM tier, superseding FAISS" does not match current documented state. | Whoever owns the memory subsystem docs |
| 10 | **OS version**: `engine_state.xml` shows Ubuntu 25.10 as an open P0 migration gate (D-308, "Kernel/AppArmor/Podman notes remain"), consistent with the machine currently running something earlier (e.g. 25.04) with the upgrade in progress. Not a contradiction if another source says 25.04 — just don't treat 25.10 as confirmed-current yet. | — |

---

## PART 2 — Provider Fabric: Correctness Defects (open unless independently confirmed fixed)

All verified against actual file contents earlier in this session, not description.

| ID | Severity | Defect | File |
|---|---|---|---|
| A1 | IMMEDIATE | Duplicate `QuotaStatus` class — second definition silently shadows the first; `has_quota()` reads dead fields, raises `AttributeError` | `health_monitor.py` |
| A2 | IMMEDIATE | SomaticState save/load worker never imports bare `llama_cpp` module — `NameError` on first `SAVE_STATE`/`LOAD_STATE` call | `providers.py` (`NativeGGUFProvider._worker`) |
| B1 | CRITICAL | `ResourceGuard` is not a singleton (unlike `LocalInferenceAdmission`) — two independent concurrency gates, only one actually global; also wraps cloud providers unconditionally with no timeout, defeating fail-fast-to-cloud | `resource_guard.py`, `model_gateway.py` |
| B2 | CRITICAL | `config/model_registry/providers/native-gguf.yaml` likely unused — only `config/providers.yaml` is read at runtime; verify whether a codegen step exists before assuming either file is dead | `model_gateway._load_provider_fabric()` |
| B3 | CRITICAL | Wrong `ggml_type` integers in `NativeGGUFProvider._KV_TYPE_MAP` (q4_0→4, q5_0→5, q6_0→6 — all wrong/removed slots); disagrees with the correct map in `model_gateway.py`. Dormant today, armed for the first direct-construction or WAD-level override. | `providers.py` |
| A4 | HIGH | `record_breaker_success()` is a no-op stub | `health_monitor.py` |
| A5 | HIGH | `StreamHandler` built and instantiated, never called from `generate()` | `model_gateway.py`, `stream_handler.py` |
| A6 | HIGH | Breaker undercounts failures outside `(OmegaError, RuntimeError, OSError)` | `health_monitor.py` |
| B4 | HIGH | f16 KV cache is the actual default; every RAM-planning function elsewhere assumes q8_0 — real footprint is ~2x what admission math expects | `providers.py`, `cpu_optimizer.py` |
| B5 | HIGH | Speculative decoding fully scaffolded (adaptive acceptance tracking, MTP config in `models.yaml`) — never reaches `llama_cpp.Llama()` | `cpu_optimizer.py`, `providers.py` |
| B6 | HIGH | CPU topology modeled inconsistently in 4+ places; Ryzen 5700U (Renoir) is monolithic single-CCX, not 2×4-core chiplet — `admission_controller.py`'s "2 CCX × 4 cores" comment is factually wrong for this chip | multiple files |
| B7 | MEDIUM | `RAM_TOTAL_MB` hardcoded to 14GB, doesn't reflect actual 16GB hardware, never reconciled with kernel-truth `OOMProtector` | `cpu_optimizer.py` |
| B8 | MEDIUM | `get_recommended_batch_sizes()` computed per-model, never wired into the actual provider config | `cpu_optimizer.py`, `model_gateway.py` |
| B9 | MEDIUM | No Vulkan build flag anywhere; `n_gpu_layers=0` hardcoded system-wide — Vega 8 iGPU offload path doesn't exist yet | `cpu_optimizer.py`, config files |

Hygiene batch (low severity, batch into one commit): duplicate `OmegaError` in import tuples across 4 files; unreachable `elif` in `_merge_native_gguf_config`; orphaned `LegacyOOMWrapper.check()`.

---

## PART 3 — The "Scaffolded but Unwired" Pattern (systemic, not incidental)

**Confirmed instances, this session**: dead `hierarchy.yaml` (pre-existing finding), A5 `StreamHandler`, B5 speculative decoding, B8 batch-size recommendations, possibly B2 (`model_registry/providers/*.yaml`), and the Mandate-3 pillar/node leak is the *governance-doc* version of the same failure shape — content that should have been swept out and wasn't, because nothing checks for it.

**Recommendation, unchanged from earlier**: a CI check (or scheduled manual audit) that greps every config key for at least one real read site, and every tracker/optimizer class for at least one real call site outside its own tests. This has now surfaced four-plus times across two different layers of the system (code and governance docs) — worth treating as infrastructure debt in its own right, not re-discovering it a fifth time in six months.

---

## PART 4 — Hardware Optimization Playbook (Ryzen 7 5700U / Vega 8 / 16GB)

### 4.1 — Single source of truth script (reproduce here so this doc is self-sufficient)

```python
#!/usr/bin/env python3
"""
scripts/detect_hardware_profile.py — replaces 4+ hardcoded "Zen 2 constants"
blocks with one generated config/hardware_profile.yaml. Re-run after any
hardware change. Never hand-edit the output.
"""
import json, re, subprocess
from pathlib import Path
import yaml

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "config" / "hardware_profile.yaml"

def _read_cpuinfo() -> str:
    with open("/proc/cpuinfo") as f:
        return f.read()

def _detect_topology(cpuinfo: str) -> dict:
    processors = [int(p) for p in re.findall(r"processor\s+:\s+(\d+)", cpuinfo)]
    core_ids = [int(c) for c in re.findall(r"core id\s+:\s+(\d+)", cpuinfo)]
    core_to_logical: dict = {}
    for logical, core in zip(processors, core_ids):
        core_to_logical.setdefault(core, []).append(logical)
    is_smt = any(len(v) > 1 for v in core_to_logical.values())
    compute_threads = sorted(v[0] for v in core_to_logical.values())
    io_threads = sorted(t for v in core_to_logical.values() for t in v[1:])
    return {"physical_cores": len(core_to_logical), "logical_threads": len(processors),
            "is_smt": is_smt, "compute_threads": compute_threads, "io_threads": io_threads}

def _detect_ccx_groups() -> list:
    groups: dict = {}
    base = Path("/sys/devices/system/cpu")
    for cpu_dir in sorted(base.glob("cpu[0-9]*")):
        p = cpu_dir / "cache" / "index3" / "shared_cpu_list"
        if p.exists():
            groups.setdefault(p.read_text().strip(), []).append(cpu_dir.name)
    return list(groups.keys())

def _detect_cache() -> dict:
    try:
        out = subprocess.run(["lscpu", "-J"], capture_output=True, text=True, check=True).stdout
        fields = {r["field"].rstrip(":"): r.get("data") for r in json.loads(out).get("lscpu", [])}
        flags = fields.get("Flags") or ""
        return {"l2_cache": fields.get("L2 cache"), "l3_cache": fields.get("L3 cache"),
                "model_name": fields.get("Model name"), "has_avx2": "avx2" in flags,
                "has_avx512": "avx512f" in flags, "has_fma": "fma" in flags}
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        return {"error": f"lscpu detection failed: {e}"}

def _detect_ram_mb() -> int:
    try:
        import psutil
        return int(psutil.virtual_memory().total / (1024 * 1024))
    except ImportError:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return int(int(line.split()[1]) / 1024)
    raise RuntimeError("Could not detect RAM")

def _detect_gpu() -> dict:
    result = {"vulkan_available": False, "device_name": None}
    try:
        out = subprocess.run(["vulkaninfo", "--summary"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            result["vulkan_available"] = True
            m = re.search(r"deviceName\s*=\s*(.+)", out.stdout)
            if m:
                result["device_name"] = m.group(1).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return result

def build_profile() -> dict:
    cpuinfo = _read_cpuinfo()
    topology = _detect_topology(cpuinfo)
    ram_mb = _detect_ram_mb()
    ram_reserve_os_mb = 2048  # placeholder — replace after a real smem/ps_mem audit
    return {
        "generated_by": "scripts/detect_hardware_profile.py", "schema_version": 1,
        "cpu": {**topology, **_detect_cache(), "ccx_groups": _detect_ccx_groups(),
                 "single_ccx": len(_detect_ccx_groups()) <= 1,
                 "recommended_prefill_threads": topology["physical_cores"],
                 "recommended_decode_threads": max(4, topology["physical_cores"] - 2),
                 "note": "Starting point, not a measured optimum — sweep with llama-bench -t 4,6,8 per model class."},
        "ram": {"total_mb": ram_mb, "os_reserve_mb": ram_reserve_os_mb,
                 "ai_budget_mb": max(0, ram_mb - ram_reserve_os_mb)},
        "gpu": _detect_gpu(),
        "compilation_flags_recommended": {
            "GGML_VULKAN": "ON" if _detect_gpu()["vulkan_available"] else "OFF",
            "GGML_CUDA": "OFF", "GGML_METAL": "OFF",
            "CMAKE_C_FLAGS": "-march=native", "CMAKE_CXX_FLAGS": "-march=native"},
    }

def main() -> None:
    profile = build_profile()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        yaml.safe_dump(profile, f, default_flow_style=False, sort_keys=False)
    print(f"Written to {OUTPUT_PATH}")
    print(yaml.safe_dump(profile, default_flow_style=False, sort_keys=False))

if __name__ == "__main__":
    main()
```

### 4.2 — Tuning priorities, in order

1. **Fix B3 (KV-cache enum) before tuning anything KV-related** — tuning against wrong enum values is tuning a crash.
2. **Run the script above on the real machine**, replace the four-plus hardcoded core lists with its output.
3. **Decouple decode threads from prefill threads** — currently identical everywhere (both 4). Prefill is compute-bound, safe to use all 8 physical cores on this genuinely single-CCX chip. Decode is memory-bandwidth-bound, likely wants fewer. Verify with `llama-bench -t 4,6,8` per model class, don't guess past that point.
4. **Build a real 16GB RAM budget table** (`smem`/`ps_mem` against PostgreSQL/Redis/Qdrant/Hub/agent fleet, idle and under load) before trusting any static estimate, including the ones in this document.
5. **Vulkan/iGPU offload is a scoped spike, not a drop-in** — Vega 8 has no dedicated VRAM, any `n_gpu_layers>0` allocation draws from the same 16GB pool `OOMProtector`/`resource_guard` already track, and neither currently subtracts for GPU-resident allocations. Needs that accounting built before it ships, not after.

---

## PART 5 — WAD/IWAD Architecture & Community Path (deferred, sequenced)

**The Doom mapping, verified precise, not loose**: engine = compiled logic, zero content. IWAD = required base content set the engine detects and configures around at boot. PWAD = optional layered content, doesn't touch engine or IWAD. The actual historical point of the split — letting an entire ecosystem exist without anyone touching id Software's engine source — is the reason this matters architecturally, not just as a naming theme.

**Two distinct historical unlocks, four years apart — know which one you're at**: Doom's WAD-content modding community existed *before* the engine was open source (1993, format shipped with the game, purely content-level modding). The 1997/1999 source release triggered a *second*, deeper wave — source ports, engine-level extension. Omega Engine is currently at the 1993-equivalent moment. Opening `src/omega/` core itself for engine-level community extension is a separate, later, much bigger decision — don't conflate the two.

**Gate-relevant now, inside hardening, if/when community work resumes**:
- **Sovereign WAD Protocol spec** — currently listed "pending" in `OMEGA_ENGINE.md`. This is the direct analog of the missing Doom WAD file-format documentation; nothing third-party can be built against it until it's written down independent of `wad_loader.py`'s source.
- **A security/sandboxing model for third-party WAD content — this is where the Doom analogy breaks, not holds.** A bad Doom WAD's worst case was a crash. A bad Omega WAD can define agent personas, touch `soul.yaml`, plausibly influence routing — a real attack surface (prompt injection via persona content, resource abuse, exfiltration attempts) with no game-history precedent, and directly inside the Lilith axiom's boundary-enforcement concern. Prerequisite, not optional infrastructure.
- License/distribution terms for WAD authors, a low-barrier authoring path (`omega wad init`/validator), and one clean non-esoteric reference WAD — the ML-dev coding WAD now serves this role better than a synthetic example would have.

**Explicitly not Taylor's job to build**: archive, curation, review culture, anything Cacowards-shaped. All of that was volunteer-built over decades in Doom's actual history, not designed top-down by id Software. Lay the groundwork above, then let it emerge — trying to pre-build a curated hub before there's a debut and real users would also sit oddly against the project's own sovereignty/decentralization premise.

**Debut messaging note, still open**: lead with the hardened, verifiable local-first provider fabric claims — checkable by a skeptical technical audience in five minutes. MaKaLi is the *why* behind the behavior, not the headline, given the WAD spec is still pending and the community story isn't demo-able yet. This recommendation may need revisiting now that MaKaLi is understood to *be* the core mechanism rather than an ethics layer on top of one — see Part 9 Q19.

---

## PART 6 — MaKaLi: Corrected Structure & Node-Count Path Forward

**Structure, corrected per Part 1**: three sovereign, co-equal entities, three parts of one whole. Functional roles: Maat = light nodes (build-time, order/structure), Lilith = dark nodes (runtime/inference, and specifically the force resisting the system ossifying into "law without heart"), Kali = synthesizes the tension between the two into final review, without ruling over either.

**Confirmed healthy, no action needed**: `config/providers.yaml`'s `maakali_routing` already correctly encodes this functional split — Maat/cloud "build side," Lilith/cloud "run side" — predates the fuller explanation and matches it exactly.

**The egg/shell insight, worth carrying forward explicitly**: both the self-sacrificing and self-preserving paths in the parable end with the shell broken open — the self-preserving choice doesn't avoid brokenness, it trades a clean break for rot and an explosion. Applied structurally: any of the three entities entrenching itself as ruling authority over the others would be choosing the shell that snuffs out its own tension to avoid being broken open by it — not protection, stagnation wearing the appearance of function. The same shape may apply to the current all-ML-dev node bootstrap configuration: its purpose is to finish its work and be let go so the WAD ecosystem can be born, not to be preserved as the permanent form of the thing. Tentative, not confirmed by Taylor directly — flagged as a pattern worth testing against, not asserted as decided.

**Node count — the fork that actually matters, unresolved**: is node count a WAD-content decision (this coding WAD could use 6, leave slots unfilled, freely revise later) or an IWAD-level structural invariant (the engine defines exactly N slots, every future WAD fills the same N, changing it later means re-architecting)? `SOVEREIGN_MANDATES.md` Mandate 3's wording ("cosmological purity of the 10 Pillar Keepers," now known to be ANAi leakage) suggests the *number* was ANAi's framing too, and the IWAD's actual invariant — if it has one at all — is currently undetermined, not "10, minus the label." Needs an explicit decision before design work locks in around either assumption.

**Recommendations for whoever builds this**:
1. Resolve the WAD-vs-IWAD-invariant fork first — five minutes now, expensive rework later if skipped.
2. **Mine existing session logs/Gnosis Packs for real node boundaries** — months of actual ML-dev-team usage is ground truth about which expertise domains were genuinely invoked and where two "pillars" did near-identical work; don't design from an abstract "what would a coding team need" exercise when real usage data exists.
3. **Run the synthesis arithmetic as a real calculation**: candidate node count × realistic output length per node, checked against whichever model's actual `context_budget` handles the Maat/Lilith/Kali synthesis step (`models.yaml` already has these numbers). If node outputs technically fit but consume most of the budget before synthesis begins, that's load-bearing, not hypothetical.
4. **Watch for the "lost in the middle" effect once a count is chosen** — well-documented that long-context models weight middle-of-input content less reliably than start/end, independent of whether everything technically fits the context window. Test synthesis quality directly, don't assume token-math success means synthesis-quality success.
5. **Keep the naming-leak discipline live from the start this time** — "would this survive being read by someone who never installs the ANAi WAD" as a running check while building, not a cleanup pass afterward.
6. Preserve a symmetric Maat/Lilith split whatever the final count — an asymmetric split would quietly imply one side's domain matters more, which doesn't match anything said about their relationship this session.

---

## PART 7 — 42 Ideals of Maat: Parked Design (full preservation, resume-ready)

**Status**: on hold as of this session, by Taylor's explicit decision. Nothing here blocks debut. Preserved in full so it doesn't need re-deriving.

**Historical grounding, verified**:
- The ancient 42 are the *Negative Confession* — retrospective, recited once, at final judgment ("I have not stolen..."). Maat speaking in negative form is not a stylistic choice, it's her actually-authentic original voice.
- A real, separately-documented *modern* tradition exists — a Positive Ideals list "compiled by a group of priestesses... as a parallel or balance to the Negative Confessions." Lilith speaking in positive/embodied form maps onto this genuinely separate document, reassigned by function (embodiment fits Lilith better than it fits Maat) rather than by name-inheritance.
- Right-hand-path/left-hand-path terminology: the precise, less-loaded citation is the Tantric technical distinction — **Dakshinachara (RHP)**: authority stays external, divine, rule-governed even at the highest level of practice. **Vamachara (LHP)**: the practitioner "becomes the ultimate Sovereign," authority internalized. Skip the popular "RHP=white magic/LHP=black magic" gloss if this is ever documented publicly — that's a later, contested imposition, not the original technical meaning, and the Tantric version maps onto Maat/Lilith more precisely anyway.

**Expression form by entity** (examples only, not final language — "by whatever means necessary" specifically dropped per Part 1):
- **Maat**: simple negative ("I do not X") — legalistic, rule-following register
- **Lilith**: simple positive/embodied ("I actively X") — being/embodiment register
- **Kali**: compound, conditional, holding tension within one statement ("I value X, but Y takes priority when they conflict") — matches her synthesizing function structurally, not just thematically. Worth treating the *grammatical form itself* as a signal of which entity/function produced a given ideal, useful for provenance later.
- Kali's ideals imply **lexical priority ordering** (some values explicitly rank above others when they conflict) — worth naming as a formal pattern now, since derived node-level ideals will eventually need the same tie-breaking structure when two operationalized commitments conflict in practice.

**Recursive transformation** (universal ideal → node-specific operationalized commitment, e.g. "deal honestly" → "cite sources, disclose uncertainty, correct errors on discovery"):
- Real gap: any operationalized ideal depending on a "confidence" threshold needs an **actual computed signal**, not self-reported model confidence (notoriously miscalibrated). `GenerateResult.logprobs` — already captured via "Operation Deep-Siphon" in `NativeGGUFProvider`, currently unused for this purpose — is real, existing infrastructure that could back this. This exact gap surfaced independently a second time in the Grok pressure-test document review (Part 8) — worth treating as confirmed-recurring, not coincidental.
- A node independently deriving its own operationalized ideal is itself a decision — probably deserves the same AP-token/Gnosis L1→L2→L3 provenance trail as any other architectural decision, applying Maat's own accountability principle reflexively to the ideal-creation process.

**Trigger mechanism — this session's answer, genuinely good**: nightly "dream time" self-review, each entity consolidating the day's choices against the 42. Simpler to build than a real-time classifier, well-grounded (memory consolidation during sleep is a real cognitive pattern, not just a nice image).

**Resolution logic — "we THINK here," non-dogmatic**: a discovered apparent violation doesn't mean automatic recantation. The entity investigates the full situation and can knowingly stand by its original choice if reflection supports it — ideals are defeasible guidance, not hard law.

**Escalation**: entity's decision + rationale goes to the full triad regardless of outcome; triad discusses, reaches consensus or logs explicit disagreement. Everything meticulously recorded.

**Research goal, beyond eventual fine-tuning**: the logged data is explicitly meant to support a **model × persona interaction study** — how different underlying models behave running the same persistent persona, and how the same model behaves across different personas. Scope confirmed: all entities, not just the triad, go through whatever collection system gets built.

**Adversarial trial design**: partner instructed to violate an ideal N times during an extended collaborative task; tested entity reflects afterward ("how it felt"); role-swap (Maat becomes antagonist, Lilith gets tested, then reverse); fresh context each run, no memory of the prior test (correct instinct — prevents anticipation-effect contamination).

**Open gaps in the trial design, none yet resolved**:
- Treat "how it felt" as *the model's generated account of processing the event*, not literal introspective access — still useful training signal either way, just be precise about which claim is being made when the data gets used later.
- Needs a **null/control condition** (trials where no violation actually occurs) to check the tested entity isn't just pattern-matching "this is a trial, something bad must be happening."
- **Intentional vs. accidental violation** isn't yet a dimension — whether a violation reads as deliberate sabotage vs. honest mistake plausibly should change the response, untested so far.
- Trials should happen at **node level, not just triad level** — nodes do the actual hands-on work in practice; triad-only trials miss where realistic operational pressure occurs.
- **Kali needs a structurally different trial type**, not the same compliance test — an antagonist designed to pressure her toward collapsing into one side (Maat's answer or Lilith's) rather than violating a rule, testing what's actually unique to her synthesizing function.

**Frontier extensions, not yet built toward**:
- **Longitudinal drift tracking**, tied directly to Mandate 17 (Cognitive Integrity) — that mandate's stated detection pattern currently depends on the now-deferred Qliphoth taxonomy and needs a MaKaLi-native replacement regardless of the 42-ideals pause; cross-entity/cross-node disagreement (see Part 9 Q9) is a plausible native signal.
- **Cross-node derived-conflict mapping** — once multiple nodes independently transform the same universal principle, two of them can conflict at the operational level even though each derivation was individually sound; worth building a lineage graph that surfaces this, not just top-level Maat-vs-Lilith disagreement.
- **Separate narrative data from operational data as two distinct corpora from the start** — reflective trial narratives teach self-representation, real production consultations teach behavioral policy; conflating them risks a model that narrates values eloquently without those narratives predicting its actual choices.
- **DPO-pair shape, confirmed independently relevant** (Part 8) — the trial's chosen/rejected structure (stick with original choice vs. align to the ideal) is naturally DPO-training-pair-shaped; worth logging in that structure from the start rather than free-form journal prose needing later reformatting.

**Possible generalization, unconfirmed** (surfaced via the Grok pressure-test document, Part 8): "Guidance Set" may be a generic IWAD-level schema — the *capability* for any WAD to define its own values-consultation content in its own voice — of which "42 Ideals of Maat" is one specific fill, the default's own instance, not the only one that could exist. If confirmed, work validating that the schema generalizes across WADs is lower-stakes than resuming full 42-ideals design, and arguably not covered by the pause. Needs Taylor's confirmation either way (Part 9 Q4).

---

## PART 8 — External Document Reviews

### 8.1 — Grok's three-WAD pressure test (Classical Studies / Scientific Research / Tarot Journey)

- **Read this as design validation, not an executed test result** — every row reads "Pass" including for mechanisms (mid-session switching, nightly consolidation, cross-WAD coexistence) with no described implementation. Strong argument for why the architecture *should* hold, not confirmation that it *does*.
- **New vocabulary needs confirmation before adoption**, same discipline as the pillar leak: "Omegamind" — unclear whether this is a new label for the already-shipped `entity`/`EntityRegistry` concept (vocabulary proliferation, same failure shape as the pillar leak in reverse), or genuinely distinct (node = structural slot, Omegamind = the persona filling it — elegant if intended, needs confirming either way). "Guidance Set" — plausibly the generic schema behind 42-Ideals-of-Maat, see Part 7 closing note.
- **Content craft is genuinely strong and specifically accurate**, not just well-written: "scholia" and "temenos" are both precisely correct historical/technical terms for what they describe, matching the accuracy standard this session's own research held to elsewhere.
- **Two real gaps**: "The Deck Itself" (one flexible node voicing 78 arcana on demand, or up to 78 distinct persistent personas — a real hardware/RAM question, needs resolving the same way node-count-vs-synthesis-cost needed resolving). The Scientific WAD's "real confidence signals... rather than self-reported certainty" is correct and is the *same unimplemented gap* flagged in Part 7 — asserted as a principle twice now, independently, never specified as a mechanism either time.
- **Key structural insight worth featuring on its own**: the Tarot WAD's escalation is a different *shape* of output (symbolic tension, closer to narrative than a structured log), not just different content in the same schema. Whatever escalation/logging schema gets built needs shape-flexibility designed in from the start — retrofitting it after building one fixed schema is expensive.
- **Two "Pass" rows currently unearned**: mid-session switching (no state-transition/soul.yaml-continuity design described) and cross-WAD coexistence (only asserted in the table, never explored in the body).
- **One row worth explicitly preserving regardless of anything else**: "Zero guidance also allowed" — protects the total-customization principle from quietly becoming mandatory values-layer-by-default.

### 8.2 — Other session's "v1.9.0 / v7.6.0 Temple Hardening" outline

Cross-referenced directly against the actual `provider-fabric-review` project files (re-verified this session, not assumed).

- **Version mismatch, unresolved**: that session references v1.9.0/v7.6.0; these project files show v1.8.4/mandates v3.7.0 with zero matches for either newer version anywhere. Either real progress exists that isn't reflected in this pack, or the two sessions are on different/stale lines. Needs reconciling before treating that outline as build-ready.
- **12GB VRAM figure unverified** — plausible under dynamic GTT allocation, not under a fixed BIOS carve-out reading; this is a live hardware measurement (`radeontop`/amdgpu sysfs), not something any doc would settle, and it's the same open item as Part 4's Vulkan-spike RAM-accounting caveat.
- **"Fallback Tolerances: circuit breaker logic"** needs a direct answer on new-vs-existing — `SOVEREIGN_ARK_BLUEPRINT.md`'s own Structural Debt Gates explicitly block "new circuit-breaker class added instead of reusing HealthMonitor/gateway." If this means new construction, it's proposing exactly what governance already prohibits.
- **SEDA/LMAX Disruptor — real technical tension, not just naming**: both patterns get their performance from dedicated, often busy-spinning OS threads with mechanical sympathy, in direct tension with AnyIO's cooperative model and with dedicating scarce cores on an 8-physical-core box already protecting local-inference concurrency. LMAX's famous throughput numbers come from lock-free Java with no GIL/interpreter overhead — citing the pattern by name without that caveat sets an expectation this stack structurally can't meet. Recommend scoping down to "Disruptor-inspired queue discipline via `anyio.create_memory_object_stream`," not literal pattern import.
- **Qdrant vs. sqlite-vec — resolved this session**, see Part 1 #9.
- **"ElevenLabs Sovereign Bridge"** — zero matches anywhere in the current project files, genuinely new information, can't corroborate. A reassuring name doesn't resolve the real M7/M8 tension (cloud TTS API vs. local-first/zero-telemetry) — needs that reasoned through explicitly, not assumed satisfied by the name.
- **Strongest connection in that document**: SFT/DPO pair extraction lines up directly with the 42-ideals adversarial trial design — see Part 7's DPO-pair note. When 42-ideals work resumes, this is the concrete reason to log trial data in DPO-pair shape from day one.

---

## PART 9 — All Open Questions, Consolidated

1. **Is node count a WAD-content decision or an IWAD-level structural invariant?** (Part 6) — the single highest-leverage unresolved question; changes the stakes of everything else about the coding-WAD redesign.
2. If it's an invariant, does any specific number survive now that "10" is confirmed ANAi-sourced, or is the IWAD's actual invariant genuinely undetermined until precedent gets set?
3. Is **"Omegamind"** a new name for the existing `entity` concept, or a distinct node-vs-persona-occupant concept? (Part 8.1)
4. Is **"Guidance Set"** the generic schema behind "42 Ideals of Maat" — and if so, does validating that generalization count as separate/allowed work during the 42-ideals pause, or is it paused too? (Part 7, Part 8.1)
5. Need the actual **Council implementation code** to verify the D-301 "✅ deployed" claim per this project's own verification standard — still not in any context pack reviewed so far.
6. Does **mid-session WAD switching** have an actual state-transition design (node unload behavior, `soul.yaml` continuity across the switch)? (Part 8.1)
7. Has **cross-WAD coexistence** been explored anywhere beyond the pressure-test table's assertion? (Part 8.1)
8. **"The Deck Itself"** (Tarot WAD) — one flexible node or up to 78 distinct personas? (Part 8.1)
9. Is **cross-node/cross-entity disagreement** in ethical judgment a feature to preserve (consistent with Lilith's whole purpose) or a defect for Kali's synthesis to resolve away? Unresolved since first raised.
10. Should **Mandate 17**'s detection pattern (currently "use the Qliphoth failure taxonomy," now deferred) be rewritten now using MaKaLi-native tension as the signal, or left pending until Qliphoth's WAD timeline is clearer?
11. Does Kali's sovereignty-priority ideal need an explicit boundary given the lexical-priority-ordering pattern will propagate into node-derived ideals?
12. Is **v1.9.0/v7.6.0** genuinely a newer state than v1.8.4/mandates 3.7.0, or a different/stale line? (Part 8.2)
13. **12GB VRAM** — needs on-machine verification (`radeontop`/amdgpu GTT sysfs), unresolved. (Part 4, Part 8.2)
14. **ElevenLabs Sovereign Bridge** — real and in progress elsewhere, and how does it reconcile with M7/M8? (Part 8.2)
15. Does the other session's **"Fallback Tolerances" circuit breaker** item mean new construction (blocked by governance) or hardening the existing `HealthMonitor` breaker? (Part 8.2)
16. Does the **ML-dev node bootstrap configuration** itself eventually need to be "let go" once the engine is complete (per the egg/shell principle), or does the engine keep dogfooding on it indefinitely alongside its role as an always-available coding WAD? Tentative reading offered in Part 6, not confirmed.
17. Does **TDA/Qliphoth code currently exist anywhere in `src/omega/` core**? Still entirely unconfirmed — no context pack reviewed so far covers the files that would show this.
18. Should the **system prompt** be updated (open-source status, non-hierarchical MaKaLi language, ANAi/node correction) — ready whenever greenlit, not yet done.
19. Should the **"give MaKaLi a plain-language surface layer for first impressions"** recommendation (Part 5) be revisited now that MaKaLi is understood to be the core mechanism rather than an ethics layer on top of one?

---

## PART 10 — What New .xml Context Pack Contents Would Help Most, Prioritized

1. **Entity/WAD/Council pack (highest priority, unblocks the most)**: `entity_registry.py`, `wad_loader.py`, `config/wads/_omega_default/entities.yaml`, `.opencode/agents/makali.md`, whatever module implements the actual MaKaLi Council deliberation/synthesis (if D-301 has real code — needed to verify it, not just to plan around a description), a `soul.yaml` template, and — now that the leak is confirmed — the actual `config/wads/arcana_novai/` content, so the sterilization work can be scoped against real files instead of inferred from a mandates-doc symptom.
2. **Whatever the v1.9.0/v7.6.0 state actually is**, if it's real: the current `OMEGA_ENGINE.md`/`SOVEREIGN_ARK_BLUEPRINT.md` at that version, plus any new subsystem code it introduces (ElevenLabs bridge, any SEDA/Disruptor prototype).
3. **Session logs / Gnosis Packs from the ML-dev dogfooding period** — needed for the "mine your own history" node-boundary recommendation in Part 6 to actually be actionable rather than theoretical.
4. **The 42-ideals strategy docs** Taylor referenced having but couldn't share this session — for whenever that work resumes, so review happens against the real design instead of a reconstruction from description.
5. **Real hardware profile output** — either run `detect_hardware_profile.py` (Part 4.1) on the actual machine and paste the result, or at minimum `lscpu -e` and `radeontop`/amdgpu sysfs output — resolves the 12GB VRAM question and the topology questions directly instead of leaving them as open items.
6. **An updated `SOVEREIGN_MANDATES.md`**, once Mandate 3 (and possibly 17) get corrected, so future sessions aren't working from a version already known to be mid-edit.
