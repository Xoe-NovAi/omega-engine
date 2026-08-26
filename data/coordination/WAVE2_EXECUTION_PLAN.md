# Wave 2 Execution Plan
**Created**: 2026-08-26 (pre-compaction)
**Author**: kali (Sprint Coordinator)
**Source**: 8 research deliverables (R01-R08), deep introspection, Architect decisions
**Status**: READY FOR EXECUTION (post-compaction)

## Pre-Conditions (MUST be true before execution)
- [ ] Compaction complete
- [ ] WAKE_STATE.json readable
- [ ] anchored-summary.md readable
- [ ] git status clean (except gitignored or-key.md)

## Execution Order

### Phase 0: ZSWAP Enablement (Architect executes, parallel with Phase 1)
**Track**: D | **Owner**: Architect (sudo) | **Session**: R03 (ses_fc03337c3ffewlIl3RbrLDhznl)
**Gate**: `swapon --show` shows 16GB swap, `cat /sys/module/zswap/parameters/enabled` = Y

1. Verify omega_library has 20GB+ free: `df -h /media/arcana-novai/omega_library`
2. Create swap: `sudo dd if=/dev/zero of=/media/arcana-novai/omega_library/swapfile bs=1G count=16 status=progress`
3. `sudo chmod 600 /media/arcana-novai/omega_library/swapfile && sudo mkswap /media/arcana-novai/omega_library/swapfile && sudo swapon /media/arcana-novai/omega_library/swapfile`
4. Disable zram: `sudo swapoff /dev/zram1 && echo '' | sudo tee /etc/systemd/zram-generator.conf && sudo systemctl mask dev-zram*.swap`
5. Enable zswap: `echo 'enabled=Y compressor=lzo_rle zpool=zsmalloc max_pool_percent=25' | sudo tee /etc/modprobe.d/omega-zswap.conf && sudo modprobe -r zswap && sudo modprobe zswap`
6. Set swappiness: `echo 'vm.swappiness=100' | sudo tee /etc/sysctl.d/99-omega-swap.conf && sudo sysctl vm.swappiness=100`
7. Add cgroup limits: `sudo mkdir -p /etc/systemd/system/omega-engine.service.d && echo -e '[Service]\nMemoryMax=6G' | sudo tee /etc/systemd/system/omega-engine.service.d/memory.conf`
8. Add to fstab: `echo '/media/arcana-novai/omega_library/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab`
9. Verify: Run R03 §6 verification script

**Rollback**: `sudo swapoff /media/arcana-novai/omega_library/swapfile && sudo rm /media/arcana-novai/omega_library/swapfile && sudo swapoff /dev/zram1`

### Phase 1: Command Compression (kali executes)
**Track**: A | **Owner**: kali | **Session**: R01 (ses_fc07ce00bffeeUVDTOMjWWCAU8)
**Gate**: `wc -l .opencode/commands/meditate.md` ≤ 350

1. Read current meditate.md (530 lines)
2. Read SR §11 (350 lines — rebuild target)
3. Compress using R01 token-cost curve:
   - Preserve §3 collision→imperative (structural, cannot compress)
   - Preserve §8 anti-domain guard (36 tokens, keep)
   - Compress ceremony prose (remove redundancy, merge similar phases)
   - Compress examples (keep 1 representative per pattern)
   - Compress behavioral invariants (extract to bullet list)
4. Verify: `wc -l .opencode/commands/meditate.md` ≤ 350
5. Verify: meditation runs end-to-end (test with sample query)
6. Truth probe: Run meditation on a real architectural question, verify output quality matches pre-compression

**Rollback**: `git checkout .opencode/commands/meditate.md`

### Phase 2: Context-Injection Ph1 (kali executes, parallel with Phase 1)
**Track**: B | **Owner**: kali | **Session**: R02 (ses_fc0335de9ffegYf88MEunkBHof)
**Gate**: All 17 steps from R02 §7 pass

1. Binary revalidation: `opencode --version` → confirm 1.18.23
2. Behavioral probe: test V1 vs V2 key family on 1.18.23
3. Backup: `cp opencode.json opencode.json.backup`
4. Steps 2-13 from R02 §7 (jq edits to opencode.json)
5. Gate check (step 14): `opencode --version && grep -cE '^\| M[0-9]+' MANDATES_CONDENSED.md`
6. E2E test (step 15): researcher + kali agent tests
7. Plugin load test (step 16): sovereign-compaction loads
8. Commit (step 17): `git add MANDATES_CONDENSED.md opencode.json && git commit`

**Rollback**: `git checkout opencode.json && rm -f MANDATES_CONDENSED.md`

### Phase 3: Headroom Local-First (kali executes, after Phase 0)
**Track**: E | **Owner**: kali | **Session**: R05 (ses_fc0331204ffeVes3nvKIYOX4jY)
**Gate**: `scripts/benchmark_phase1.py:I5` shows >15% savings locally

**Task 0 (BLOCKER)**:
1. Read headroom library source for local-only mode
2. Configure ContentRouter with `optimize=False` or local-only flag
3. Use `EstimatingTokenCounter` (no tiktoken/network)
4. Test: SmartCrusher returns actual compression, not passthrough
5. If SmartCrusher cannot work locally, investigate Kompress-v2-base as local HF model

**Tasks 1-6** (after Task 0 passes):
- Task 1: Wire ContentRouter into ModelGateway._prepare_messages()
- Task 2: Wire into RAG retrieval
- Task 3: Add MCP headroom_compress tool
- Task 4: Create config/headroom.yaml
- Task 5: CCR store + headroom_retrieve
- Task 6: Verification tests

**Rollback**: Revert headroom.py to pre-Task 0 state

### Phase 4: DS/KD (kali executes, parallel with Phase 3)
**Track**: C | **Owner**: kali | **Session**: R06 (ses_fc02ce92bffes8IRAatNLFUXaX)
**Gate**: 13 domain dirs exist, each with metadata.yaml + PLAYBOOK.md + AFFINITY_PRESETS.yaml

1. DS-1: Write DOMAIN_DOCUMENTATION_SYSTEM.md
2. DS-2: Create 11 missing domain dirs
3. KD-2: Generate 12 missing AFFINITY_PRESETS.yaml (from engineering/ template)
4. KD-1: Write curator model spec
5. DS-3: Implement domain_loader.py
6. KD-3: Write domain primers
7. DS-4: Implement sync_domain_docs.py
8. DS-5: Update STRATEGY_INDEX/CORPUS_MAP

**Rollback**: `git rm -r config/domains/<new_dirs>`

### Phase 5: LI/HR (kali executes, after Phase 0 + Phase 3)
**Track**: F | **Owner**: kali | **Session**: R04 (ses_fc02d0ae3ffegM0BKWV8KQFuAq)
**Gate**: llama-fit-params runs on Ryzen 5700U OR LI strategy pivoted to q8_0 KV + sequential

**Pre-gate**: Verify llama-fit-params on CPU-only
1. `cd tools/fit-params && make && ./llama-fit-params --model <qwen3-path>`
2. If CUDA-dependent: pivot LI to q8_0 KV + sequential loading only
3. If works: proceed with full LI integration

**Implementation**:
- BP-R04: llama-fit-params integration into ModelGateway
- BP-R09: NVMe swap configuration (if not already done in Phase 0)
- BP-R12: Documentation system (if not already done in Phase 4)

**Rollback**: Revert llama_fit_probe.py

## Quality Gates (Truth Probes)

### Gate G1: Empty Corpus Seed (before Phase 4)
- Write ONE real meditation record
- Run D4 rubric against it
- If rubric fails: fix rubric, not meditation
- If rubric passes: proceed with DS/KD

### Gate G2: Headroom Local Proof (before Phase 3 Tasks 1-6)
- `scripts/benchmark_phase1.py:I5` shows >15% savings locally
- SmartCrusher returns actual compression (not passthrough)
- If fails: kill cloud default, implement local model override from scratch

### Gate G3: llama-fit-params Verification (before Phase 5)
- Run on Ryzen 5700U CPU-only
- If CUDA-dependent: pivot LI strategy
- Record result in WAKE_STATE.json

### Gate G4: Command Compression Quality (after Phase 1)
- Meditation runs end-to-end
- Output quality matches pre-compression
- Token count ≤ 350 lines

## Expert Session Paging

| Session | Domain | When to Page |
|---------|--------|-------------|
| `ses_fc07ce00bffeeUVDTOMjWWCAU8` | 16K ceiling, token economics | Track A disputes |
| `ses_fc0335de9ffegYf88MEunkBHof` | CI Ph1 spec, compaction keys | Track B disputes |
| `ses_fc03337c3ffewlIl3RbrLDhznl` | ZSWAP, swap, cgroup | Track D disputes |
| `ses_fc0331204ffeVes3nvKIYOX4jY` | headroom-ai, SmartCrusher | Track E disputes |
| `ses_fc02d0ae3ffegM0BKWV8KQFuAq` | llama-fit-params, NVMe, doc-gen | Track F disputes |
| `ses_fc02ce92bffes8IRAatNLFUXaX` | Curator, affinity presets, D4 rubric | Track C disputes |
| `ses_fc02cd428ffezaOBlWucaBzajs` | Anti-domains, quality audit | Gate G1 disputes |
| `ses_fc02cbcfcffedlzXRvzcLXY2jv` | CI failure evidence, validation | Track B verification |