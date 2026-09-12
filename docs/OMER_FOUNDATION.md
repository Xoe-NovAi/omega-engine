# Omega Model Evaluation Registry (OMER)

**Git-native, evidence-disciplined model evaluation registry for sovereign AI workflows**

*Version: 1.0 | Status: Design Complete | Date: 2026-09-11*

---

## 1. Philosophy & Scope

| Principle | Implementation | Research Basis |
|-----------|----------------|----------------|
| **Decision records, not leaderboards** | Every card ends with go/no-go verdict + promotion checklist | HF Model Cards are transparency docs; we need decision artifacts |
| **Evidence-first** | 5 standardized labels + 5-level reproduction status legend | CORE-AI-7 reproduction legend + EvalEval 4 signals |
| **Local-first, git-native** | Markdown + YAML frontmatter in repo; zero DB, zero cloud deps | HF Model Cards use YAML frontmatter; git is the sync layer |
| **Hardware context as first-class data** | CPU pin, RAM, KV cache, quantization, threads captured per measurement | MLPerf KV Cache Benchmark DESIGN.md hardware tables |
| **Pytest-style ergonomics** | `omer measure`, `omer promote`, `omer validate` | DeepEval is pytest-native; LM-Eval-Harness has CLI subcommands |
| **Framework-agnostic ingestion** | Adapters for LM-Eval-Harness, DeepEval, custom scripts, manual entry | LM-Eval-Harness JSON output; DeepEval test_run_*.json |
| **Community-ready** | Schema versioning, PR-based contributions, automated validation | MLPerf submission guidelines; HF PR-based model cards |

**Out of scope**: Model hosting, leaderboard UI, cloud sync, proprietary APIs, auto-scheduling.

---

## 2. Core Data Model (v1 Schema)

### 2.1 Model Card Frontmatter (Extended from HF + MLPerf)

```yaml
# --- Required (validated by `omer validate`) ---
card_version: "1.0"
model_id: "nex-agi/nex-n2.5-pro:free"
provider: "OpenRouter (Nex AGI)"
research_status: "candidate"           # candidate | active | rejected | retired
deployment: "hosted_trial"             # hosted_trial | local | hybrid | not_deployed
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text", "image"]
modalities_out: ["text"]

# --- Hardware Profile for Local Deployments (from MLPerf KV Cache Benchmark) ---
local_hardware_profile:
  cpu: "i7-13620H"
  cpu_cores: 10                         # 6P+4E
  cpu_threads: 16
  allowed_cpus: "0-11"                  # P-cores + HT siblings (not physical-only!)
  threads: 8                            # OLLAMA_NUM_THREADS
  ram_gb: 16
  ram_type: "DDR5-5200 single-channel"
  kv_cache_type: "q8_0"
  flash_attention: true
  max_loaded_models: 1
  quantization: "Q4_K_M"
  gpu: null                             # CPU-only node

# --- MLPerf-style Reproducibility ---
reproducibility:
  seed: 42
  config_hash: "sha256:abc123..."       # hash of config used for measurements
  environment:                          # captured via `omer measure --capture-env`
    ollama_version: "0.33.3"
    llama_cpp_version: "b1234..."
    python_version: "3.12.3"
    kernel: "6.8.0-...-generic"
```

### 2.2 Measurement Entry (Appended to Card's Evidence Section)

```markdown
## Local Measurement — 2026-09-11 — Terminal-Bench 2.1

| Field | Value |
|---|---|
| Benchmark | Terminal-Bench 2.1 (v1.0) |
| Score | 81.2 |
| Metric | pass_rate (higher better) |
| Evidence label | **Local measurement** |
| Reproduction status | **Controlled** |
| Hardware | i7-13620H, AllowedCPUs=0-11, THREADS=8, 16GB DDR5-5200 |
| Software | Ollama 0.33.3, llama.cpp b1234, KV q8_0, flash-attn |
| Config | `{"temperature":0.7,"top_p":0.95,"top_k":40,"ctx":8192,"seed":42}` |
| Command | `make bench MODEL=phi4-mini PROMPTS=3 WARM=1` |
| Trials | 3 (median reported) |
| Duration | 20.7s avg |
| Tokens/sec | 13.5 |
| CV | 2.1% |
| Source | `scripts/bench.py` commit `a1b2c3d` |
| Notes | Steady-state after warmup; swap ~0; P95 latency 120ms |

> **Reproduction status**: Controlled (ran through full validation methodology chain; public materials sufficient for external party to re-run)
> **Confidence interval**: 13.5 ± 0.3 tok/s (95% CI, n=3)
```

### 2.3 Reproduction Status Legend (CORE-AI-7 Aligned + MLPerf Rigor)

| Level | Label | Definition | MLPerf Equivalent |
|-------|-------|------------|-------------------|
| 0 | **Indicative** | Informal, not gated; quick sanity check | N/A |
| 1 | **Internal** | Private CI, not independently observed | Internal CI |
| 2 | **Controlled** | Ran through full validation methodology chain | MLPerf "controlled" (standardized params, seed) |
| 3 | **Reproducible** | Public materials sufficient for external re-run | MLPerf "closed" submission (fixed params) |
| 4 | **Independently reproduced** | Third party re-ran and confirmed | MLPerf "audited" (third-party verified) |

> **Rule**: Provider benchmarks default to **Indicative** unless accompanied by reproduction artifacts. Local measurements must achieve ≥ **Controlled** to count toward promotion.

### 2.4 Evidence Labels (Standardized)

| Label | Definition | Color (UI) |
|-------|------------|------------|
| **Verified metadata** | Live provider/API/model-repository metadata (catalog fields, repo stats, API responses) | 🟢 |
| **Provider claim** | Benchmark, capability, or feature reported by the model publisher without independent replication | 🟡 |
| **Independent report** | Third-party evaluation, academic paper, or user report with provenance | 🔵 |
| **Local measurement** | Measured on Omega hardware with a reproducible command/script | 🟣 |
| **Not yet measured locally** | Explicit marker for capabilities we plan to validate but have not yet tested | ⚪ |

---

## 3. Benchmark Definition Schema (from MLPerf + LM-Eval-Harness)

### 3.1 Benchmark Registry Entry (`benchmarks/terminal-bench.md`)

```yaml
# benchmarks/terminal-bench.yaml
benchmark_id: "terminal-bench"
version: "2.1"
category: "coding"
subcategory: "agentic"
description: "End-to-end terminal task completion in realistic environments"
homepage: "https://github.com/terminal-bench/terminal-bench"
license: "Apache-2.0"
paper: "https://arxiv.org/abs/2402.xxxxx"
tags: ["coding", "tool-use", "multi-turn", "agentic"]

# MLPerf-style standardized parameters
standard_params:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  max_tokens: 4096
  few_shot: 0
  seed: 42

# Metric definition (from LM-Eval-Harness)
metrics:
  - name: "pass_rate"
    type: "ratio"
    higher_is_better: true
    aggregation: "median"
    stderr_method: "bootstrap"
    bootstrap_iters: 100000

# Reproduction requirements
reproduction:
  min_trials: 3
  report: "median"
  cv_threshold: 5.0
  required_artifacts:
    - "config.yaml"
    - "seed"
    - "hardware_profile"
    - "software_versions"

# Contamination check
contamination:
  canary_string: "TERMINAL-BENCH-CANARY-2026"
  check_method: "substring_search"
```

### 3.2 Benchmark Registry Index (`benchmarks/registry.yaml`)

```yaml
benchmarks:
  - id: terminal-bench
    version: "2.1"
    file: "terminal-bench.md"
    status: "active"              # active | saturated | deprecated | contaminated
    last_verified: "2026-09-11"
    category: "coding"
  - id: swe-bench
    version: "1.0"
    file: "swe-bench.md"
    status: "active"
    last_verified: "2026-09-11"
    category: "coding"
  - id: mmlu
    version: "1.0"
    file: "mmlu.md"
    status: "saturated"           # no longer separates models
    last_verified: "2026-09-11"
    category: "knowledge"
```

---

## 4. Hardware Profile Schema (from MLPerf KV Cache Benchmark)

### 4.1 Hardware Registry Entry (`hardware/i7-13620H.yaml`)

```yaml
# hardware/i7-13620H.yaml
hardware_id: "i7-13620H"
category: "laptop_cpu"
vendor: "Intel"
architecture: "Raptor Lake-H"
cores:
  total: 10
  performance: 6
  efficient: 4
threads: 16
base_freq_ghz: 2.4
max_turbo_ghz: 5.0
cache:
  l1_per_core_kb: 80
  l2_per_core_kb: 1280
  l3_shared_mb: 24
memory:
  type: "DDR5"
  speed_mt_s: 5200
  channels: 1
  capacity_gb: 16
  ecc: false
numa_nodes: 1
pci_gen: 4
instruction_sets: ["AVX2", "AVX-VNNI", "AMX-BF16"]
thermal_design_power_w: 45
max_junction_temp_c: 100
recommended_ollama:
  allowed_cpus: "0-11"          # P-cores + HT siblings (NOT physical-only 0,2,4,6,8,10!)
  num_threads: 8
  kv_cache_type: "q8_0"
  flash_attention: true
  max_loaded_models: 1
  context_length: 8192
kv_cache_per_token_kb:
  llama3_8b: 128
  mistral_7b: 125
  phi4_mini: 64
expected_throughput_tok_s:
  phi4_mini_q4km: 13.5
  qwen25_coder_7b_q4km: 7.1
  deepseek_r1_8b_q4km: 6.8
last_verified: "2026-09-11"
source: "Omega Engine Alpha BENCHMARKS.md + MLPerf KV Cache Benchmark methodology"
```

### 4.2 Hardware Registry Index (`hardware/registry.yaml`)

```yaml
hardware_profiles:
  - id: "i7-13620H"
    file: "i7-13620H.yaml"
    status: "verified"
    node: "ASUS ExpertBook P1503CVA (Node 1)"
  - id: "ryzen7-5700U"
    file: "ryzen7-5700U.yaml"
    status: "planned"
    node: "HP Pavilion (Node 0)"
```

---

## 4. Metric Normalization (LM-Eval-Harness + DeepEval)

### 4.1 Canonical Metric Representation

Every measurement normalizes to this structure:

```python
# Internal representation (Pydantic model)
class Measurement(BaseModel):
    benchmark_id: str
    benchmark_version: str
    metric_name: str                    # canonical name (e.g., "pass_rate")
    metric_value: float                 # 0.812
    metric_stderr: float | None         # 0.003
    metric_unit: str                    # "ratio" | "tok_s" | "ms" | "bytes"
    higher_is_better: bool
    aggregation: str                    # "median" | "mean" | "max"
    trials: int                         # 3
    cv_percent: float | None            # 2.1
    confidence_interval: tuple[float, float] | None  # (13.2, 13.8)
```

### 4.2 Adapter Output Normalization

| Source Framework | Raw Output | OMER Canonical Mapping |
|------------------|------------|------------------------|
| **LM-Eval-Harness** | `results[task]["acc"]`, `results[task]["acc_stderr"]` | `metric_name="acc"`, `metric_stderr=...` |
| **LM-Eval-Harness** | `results[task]["exact_match"]`, `results[task]["exact_match_stderr"]` | `metric_name="exact_match"` |
| **DeepEval** | `test_run.results[0].metrics[0].score` | `metric_name=metric.__class__.__name__` |
| **Custom** | Any JSON | `--metric-map '{"acc":"accuracy","em":"exact_match"}'` |

**Normalization Rules:**
1. Stderr → always included if available
2. CV% = (stderr / value) × 100 / sqrt(trials)
3. CI95 = value ± 1.96 × stderr (for n≥30) or t-distribution (n<30)
4. All scores stored as 0-1 ratios internally; percentages only for display

---

## 5. Schema Versioning Strategy

### 5.1 Frontmatter Versioning

```yaml
card_version: "1.0"           # MAJOR.MINOR - bump on breaking changes
schema_version: "2026-09-11"  # Date-based for traceability
```

| Version | Trigger | Migration |
|---------|---------|-----------|
| 1.0 → 1.1 | New optional field added | Auto-add with default |
| 1.1 → 2.0 | Required field added/removed/renamed | `omer migrate --to 2.0` script |

### 5.2 Config File Versioning (`config.yaml`)

```yaml
# config.yaml
config_version: "1.0"
defaults: ...
```

Same semver policy. `omer migrate` handles forward/backward compatibility.

---

## 6. Cross-Model Comparison Methodology (MLPerf Rigor)

### 6.1 Statistical Protocol

| Aspect | Protocol | Source |
|--------|----------|--------|
| **Trials per measurement** | Minimum 3, median reported | MLPerf requires 3-5 trials |
| **Reported statistic** | Median (not mean) | MLPerf: "Report median rather than mean" |
| **Variance reporting** | CV% + 95% CI | MLPerf: CV 50-125%, report median |
| **Significance testing** | Paired bootstrap (n=10000) for A/B | LM-Eval-Harness bootstrap_iters=100000 |
| **Multiple comparison correction** | Bonferroni for >2 models | Standard practice |
| **Effect size reporting** | Cohen's d + 95% CI | Standard |

### 6.2 A/B Promotion Gate

```bash
omer promote nex-n2-5-pro --status active \
  --require "A/B vs phi4-mini on 4 tasks (Terminal-Bench, SWE-Bench, ToolAthlon, UI-interpret)" \
  --require "Paired bootstrap p<0.05 on primary metric" \
  --require "Effect size d>0.3 on at least 2/4 tasks" \
  --require "Rate-limit confirmed >100 reqs/day over 7 days" \
  --require "Structured-output fidelity >95% on JSON schema"
```

---

## 7. Contamination Detection

### 7.1 Canary String Protocol

```yaml
# In benchmark definition
contamination:
  canary_string: "TERMINAL-BENCH-CANARY-2026-UNIQUE"
  check_method: "substring_search"
  check_locations:
    - "model_card"
    - "training_data"
    - "provider_catalog"
  action_on_detect: "flag"  # flag | reject | quarantine
```

### 7.2 Automated Check (CI Gate)

```bash
# In CI pipeline
omer check-contamination --model nex-n2-5-pro --benchmarks all
# Scans: model card, provider catalog, training data snapshots
```

---

## 7. Long-Term Storage & Archival

### 7.1 Artifact Storage Policy

| Artifact Type | Storage | Retention | Format |
|---------------|---------|-----------|--------|
| Model cards | Git (text) | Forever | Markdown + YAML |
| Measurement logs | Git (text) | Forever | Markdown tables |
| Raw benchmark outputs | Git LFS (if >1MB) | 2 years | JSON |
| Environment captures | Git LFS | 1 year | JSON |
| Excel exports | Git LFS | 2 years | .xlsx (MLPerf-style) |

### 7.2 Archival Command

```bash
omer archive --older-than 2y --compress --verify
# Compresses old JSON artifacts to .json.zst, verifies integrity
```

---

## 8. License Compliance Tracking

### 8.1 License Fields in Frontmatter

```yaml
license: "Apache-2.0"
license_url: "https://www.apache.org/licenses/LICENSE-2.0"
weights_license: "Apache-2.0"
code_license: "MIT"
data_license: "CC-BY-4.0"
third_party_licenses:
  - "llama.cpp: MIT"
  - "ggml: MIT"
  - "OpenRouter ToS: proprietary (hosted only)"
```

### 8.2 License Compliance Gate

```bash
omer validate --check-licenses
# Fails if:
# - License missing for any component
# - Incompatible licenses (GPLv3 + proprietary weights)
# - License URL unreachable
```

---

## 8. Attribution & Provenance Chain

### 8.1 Full Provenance Per Measurement

```markdown
## Provenance Chain

1. **Source**: LM-Eval-Harness v0.4.3 (`lm_eval --model hf --tasks terminal-bench`)
2. **Config**: `configs/terminal-bench.yaml` (hash: sha256:abc123)
3. **Hardware**: i7-13620H profile (hash: sha256:def456)
4. **Software**: Ollama 0.33.3, llama.cpp b1234 (commit hash)
5. **Seed**: 42
6. **Command**: `make bench MODEL=phi4-mini PROMPTS=3 WARM=1`
7. **Raw output**: `results/terminal-bench_20260911_143022.json` (Git LFS)
8. **Normalized**: `omer ingest lm-eval-harness results/... --model phi4-mini`
9. **Appended to**: `docs/models/phi4-mini.md` (git commit a1b2c3d)
```

### 8.2 Provenance Graph (Queryable)

```bash
omer provenance nex-n2-5-pro --graph
# Outputs Mermaid diagram: model → measurements → hardware → software → config → seed
```

---

## 9. Integration with Omega Systems

| Omega System | Integration Point | Mechanism |
|--------------|-------------------|-----------|
| **The Well** | `omer measure` contradictions → auto-add corrections | `kind:correction` with `source_pack:omer-<model>-<date>` |
| **Gnosis Lock** | `omer promote` triggers gnosis-lock reflection | Pre-promotion ritual with `question` tool |
| **WanderGround** | Cards exported via `make well-export` → ingested as dossiers | `wanderd ingest --source omer --model nex-n2-5-pro` |
| **BENCHMARKS.md** | Hardware profiles in `hardware/` registry; `omer measure` auto-links | `omer measure --hardware i7-13620H` |
| **ROADMAP** | Promotion = ROADMAP status change (`candidate` → `active`) | `omer promote` updates ROADMAP status line |
| **Gnosis-Leash** | Card summaries injected at session start/compaction | Plugin reads `docs/models/*.md` frontmatter |

---

## 9. Community Governance Model (MLPerf + HF Inspired)

### 9.1 Contribution Tiers

| Tier | Who | Scope | Gate |
|------|-----|-------|------|
| **Core Maintainers** | Omega team | Schema changes, core adapters, CI | Consensus (2/3) |
| **Benchmark Curators** | Community | Benchmark definitions, reproduction status | `omer validate` + 1 maintainer |
| **Hardware Curators** | Community | Hardware profiles, KV cache tables | Measured on that hardware |
| **Contributors** | Anyone | Local measurements, typo fixes | `omer validate --strict` passes |

### 9.2 Decision Process

| Decision Type | Process | Timeline |
|---------------|---------|----------|
| Schema change (v1.x → v2.0) | RFC → 2-week discussion → core maintainer vote | 3 weeks |
| New benchmark adoption | Curator PR → reproduction verification → merge | 1-2 weeks |
| Hardware profile | Curator PR → measurement verification → merge | 1 week |
| Evidence label addition | RFC → core maintainer vote | 2 weeks |

### 9.3 Code of Conduct

Adapted from [MLPerf Participation Rules](https://mlcommons.org/en/policies/) + [HF Community Guidelines](https://huggingface.co/docs/hub/en/community-guidelines).

---

## 10. What We Explicitly Don't Build (Reaffirmed)

| Feature | Reason | Alternative |
|---------|--------|-------------|
| Web UI / Dashboard | Markdown in git is the UI; `git log -p docs/models/` is history | `omer show --format markdown \| pandoc -o card.html` |
| Real-time leaderboard | Evidence discipline > speed; use LARIkoz for that | `omer compare` for pairwise |
| Cloud sync / multi-user | Single-machine sovereignty; git is the sync layer | `git push/pull` |
| Auto-benchmark scheduling | Cron + `omer measure` is explicit and auditable | Systemd timer + `omer measure` |
| LLM-as-judge metrics | Provider claims; keep in card as labeled evidence only | DeepEval adapter for local LLM-as-judge |

---

## 11. MVP Milestones (Refined with Research)

| Milestone | Deliverable | Gate | Research Basis |
|-----------|-------------|------|----------------|
| **M1: Schema & Validation** | `validate_model_cards.py` + frontmatter schema + `make lint` integration | All existing cards pass | HF frontmatter + MLPerf config.yaml |
| **M2: Measurement CLI** | `omer measure` + `log_local_measurement.py` + hardware context capture | Logs Terminal-Bench for phi4-mini | MLPerf hardware tables + CORE-AI-7 reproduction legend |
| **M3: Adapter Framework** | `omer ingest` + LM-Eval-Harness + DeepEval adapters | Ingests existing `results/llama2-7b-eval.json` | LM-Eval-Harness JSON output + DeepEval test_run_*.json |
| **M4: Promotion Gate** | `omer promote` + checklist enforcement | Nex-N2.5-Pro promotion PR passes | MLPerf promotion rigor + CORE-AI-7 reproduction legend |
| **M5: Registry Queries** | `omer list/show/compare` + provenance graph | `omer compare nex-n2-5-pro phi4-mini` works | MLPerf comparison rigor + DeepEval test_run comparison |
| **M6: Community Packaging** | PyPI package `omer`, `pipx install omer`, man pages | `pipx install omer` works on fresh machine | MLPerf `pip install .[full]` + HF `pip install huggingface_hub` |

---

## 12. Why This Fills Every Community Gap

| Gap (from deep research) | OMER Solution | Source |
|--------------------------|---------------|--------|
| No standard reproduction status | 5-level legend (Indicative→Independent) adopted from CORE-AI-7 + MLPerf rigor | CORE-AI-7 BENCHMARK-REGISTRY.md + MLPerf |
| Hardware context lost in benchmarks | Mandatory hardware block per measurement; `hardware/` registry with KV cache tables | MLPerf KV Cache Benchmark DESIGN.md |
| Provider claims ≠ independent validation | 5 evidence labels; provider claims default to Indicative | EvalEval 4 signals + CORE-AI-7 |
| No local-measurement workflow | `omer measure` CLI + dated append to card + hardware capture | MLPerf CLI + CORE-AI-7 |
| Framework output silos | Adapter interface normalizes LM-Eval-Harness, DeepEval, custom | LM-Eval-Harness JSON + DeepEval test_run_*.json |
| No promotion criteria | `omer promote` with explicit statistical checklist | MLPerf promotion + bootstrap significance |
| Cards rot / drift | `omer validate --strict` in CI; frontmatter versioning + config_hash | HF frontmatter + MLPerf config.yaml |
| Community contributions lack evidence discipline | PR gate = same validation + evidence labels required | MLPerf submission guidelines + HF PR model |
| No contamination detection | Canary string protocol + CI gate | BetterBench + MLPerf |
| No license compliance tracking | License fields in frontmatter + CI gate | HF Model Card license field |
| No attribution/provenance chain | Full provenance per measurement + graph query | MLPerf config_hash + seed |
| No hardware context standardization | MLPerf-style hardware profiles with KV cache per token tables | MLPerf KV Cache Benchmark DESIGN.md |
| No metric normalization across frameworks | Canonical measurement schema + adapter mapping table | LM-Eval-Harness + DeepEval metric taxonomy |

---

## 13. Next Step

**➡ M2 (Measurement CLI)** — build the local measurement path so cards
can rise past `Indicative`:

1. Define `omer measure` skeleton: hardware capture (P-core+HT mask `0-11`,
   KV cache type, RAM, quantization, threads via `ollama ps`/`/api/ps`),
   dated append to a card's `## Local Measurement` section.
2. Implement `scripts/measure_model.py` with anyio-pure + hard timeout
   (`</dev/null`), recording `tokens/sec`, P95 latency, seed, config_hash
   (mirror `scripts/bench.py` but write into the card).
3. Add `## Local Measurement` evidence labels + promotion rule: only
   `Controlled`+ local measurements promote a card past `candidate`.
4. Wire `omer measure` into `make lint`.

**M1 (Schema & Validation) is ✅ DONE (2026-09-11)** — `scripts/validate_model_cards.py`
(Pydantic v1.0 schema) is live; validates `docs/models/*.md` cards inside
`make lint`; evidence labels (5) + reproduction status (5-level) enforced; the
P-core trap guard rejects `allowed_cpus: 0,2,4,6,8,10`; Nex-N2.5-Pro card passes
(commit `85cde0f`). OMER design complete in this file (555 lines).

The Nex-N2.5-Pro card is the first real test case. All research is complete; the design is ready for implementation.

---

*End of OMER Foundation Document — Ready for Implementation*