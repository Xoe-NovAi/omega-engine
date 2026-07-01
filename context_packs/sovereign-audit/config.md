---
FILE: config/providers.yaml
SIZE: 2589
LANG: YAML
SHA256: 11e90aff15893ddf778483a42fe52a85bc96cfe96da55469960098d39d23b5e2
PURPOSE: General implementation
---
inference:
  strategy: local_first
  fallback_chain:
  - provider: native-gguf
    # Default model path: models/gguf/ (created by make model-download)
    priority: 0
    n_ctx: 8192
    n_ctx_max: 32768
    cores:
    - 0
    - 2
    - 4
    - 6
    n_threads: 6
    n_threads_batch: 6
    type_k: 8
    type_v: 1
    n_batch: 512
    n_ubatch: 32
    use_mmap: true
    use_mlock: false
    n_gpu_layers: 0
  - provider: lmster
    priority: 1
    endpoint: http://127.0.0.1:1234
    model_overrides:
      qwen3-4b-thinking-q4_k_m: qwen3-4b-thinking
      qwen3-1.7b-q6_k: qwen3-1.7b
      qwen3-1.7b: qwen3-1.7b
      phi-4-mini: phi-4-mini
      deepseek-r1-qwen3-8b-q3_k_l: deepseek-r1-qwen3-8b
      krikri-8b-q4_k_m: krikri-8b
      rocracoon-3b-instruct: RocRacoon-3b
      phi-4-mini-reasoning-abliterated-q4_k_m: phi-4-mini-abliterated
  - provider: ollama
    priority: 2
    endpoint: http://127.0.0.1:11434
    model_overrides:
      qwen3-1.7b-q6_k: qwen3:1.7b
      qwen3-1.7b: qwen3:1.7b
      qwen3-0.6b-q6_k: qwen3:0.6b
      qwen3-4b-thinking-q4_k_m: qwen3:4b
      deepseek-r1-qwen3-8b-q3_k_l: deepseek-r1:8b
      krikri-8b-q4_k_m: krikri:8b
      phi-2-omnimatrix-i1-q4_k_m: ministral:3b
      phi-4-mini: phi-4-mini
      rocracoon-3b-instruct: rocracoon:3b
      phi-4-mini-reasoning-abliterated-q4_k_m: phi-4-mini
  - provider: google
    priority: 3
    api_key: env:GOOGLE_API_KEY
    model_overrides:
      phi-4-mini: gemma-4-31b-it
      deepseek-r1-qwen3-8b-q3_k_l: gemma-4-31b-it
      krikri-8b-q4_k_m: gemma-4-31b-it
      qwen3-4b-thinking-q4_k_m: gemma-4-31b-it
      phi-2-omnimatrix-i1-q4_k_m: gemma-4-31b-it
    models:
    - gemma-4-31b-it
    - gemma-4-26b-it
  - provider: opencode-zen
    priority: 4
    api_key: env:OPENCODE_ZEN_API_KEY
    base_url: https://api.opencode.ai/zen/v1
    model_overrides:
      qwen3-1.7b-q6_k: minimax/minimax-m3
      qwen3-1.7b: minimax/minimax-m3
      qwen3-4b-thinking-q4_k_m: minimax/minimax-m3
      qwen3-0.6b-q6_k: minimax/minimax-m3
      deepseek-r1-qwen3-8b-q3_k_l: deepseek/deepseek-v4-flash
      krikri-8b-q4_k_m: minimax/minimax-m2.5
      phi-2-omnimatrix-i1-q4_k_m: minimax/minimax-m3
      phi-4-mini: minimax/minimax-m3
    models:
    - minimax/minimax-m3
    - deepseek/deepseek-v4-flash
    - minimax/minimax-m2.5
  - provider: cline
    priority: 5
  - provider: github-copilot
    priority: 6
    models:
    - github-copilot/claude-haiku-4.5
    - github-copilot/gpt-4.1
    - github-copilot/gpt-4o
    - github-copilot/gpt-5-mini
  - provider: mock
    priority: 99
    enabled: true

---

---
FILE: config/models.yaml
SIZE: 8233
LANG: YAML
SHA256: 74e71fedeb49095b505e2783ca0f8a429ca9732ff7a5bcc7b8e1fb89cd356709
PURPOSE: General implementation
---
embedding:
  model: embeddinggemma-300m-q6_k
  local_path: /media/arcana-novai/omega_library/lmstudio-models/local/all/embeddinggemma-300m-Q6_K.gguf
  dimensions: 768
  backend: llama-server
  quantization: Q6_K
  device: cpu
  ram_estimate_mb: 200
llama_server:
  port: 8080
  host: 127.0.0.1
  log_level: info
  threads: 6
  batch_size: 512
  ubatch_size: 32
  context_size: 8192
  gpu_layers: 0
  startup_timeout_sec: 120
models:
  qwen3-1.7b:
    path: /media/arcana-novai/omega_library/models/local/all/Qwen3-1.7B-Q6_K.gguf
    size_gb: 1.6
    ram_mb: 1800
    context_window: 4096
    threads: 4
    load_strategy: on_demand_5min
    entity: nova
  qwen3-0.6b-q6_k:
    path: /media/arcana-novai/omega_library/models/local/all/Qwen3-0.6B-Q6_K.gguf
    size_gb: 0.47
    ram_mb: 500
    context_window: 4096
    threads: 4
    load_strategy: warm
    entity: iris
  qwen3-1.7b-q6_k:
    path: /media/arcana-novai/omega_library/models/local/all/Qwen3-1.7B-Q6_K.gguf
    size_gb: 1.6
    ram_mb: 1800
    context_window: 8192
    threads: 6
    load_strategy: on_demand_10min
    entity: sekhmet, hecate
  phi-4-mini:
    path: /media/arcana-novai/omega_library/models/local/all/Phi-4-mini-instruct-Q5_K_M.gguf
    size_gb: 2.85
    ram_mb: 3500
    context_window: 16384
    threads: 6
    load_strategy: on_demand_10min
    entity: SOPHIA
  phi-2-omnimatrix-i1-q4_k_m:
    path: /media/arcana-novai/omega_library/models/local/all/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf
    size_gb: 2.5
    ram_mb: 2800
    context_window: 8192
    threads: 6
    load_strategy: on_demand_10min
    entity: brigid
  qwen3-4b-thinking-q4_k_m:
    path: /media/arcana-novai/omega_library/models/local/all/Qwen3-4B-Thinking-2507-Q4_K_M.gguf
    size_gb: 2.4
    ram_mb: 2700
    context_window: 8192
    threads: 6
    load_strategy: on_demand_5min
    entity: maat, anubis
    kv_cache_key_type: q8_0
    kv_cache_value_type: q8_0
    thinking_budget: 512
  deepseek-r1-qwen3-8b-q3_k_l:
    path: /media/arcana-novai/omega_library/models/local/all/DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf
    size_gb: 4.2
    ram_mb: 4500
    context_window: 8192
    threads: 6
    load_strategy: on_demand_5min
    entity: lucifer
    thinking_budget: 512
  rocracoon-3b-instruct:
    path: /media/arcana-novai/omega_library/models/local/all/RocRacoon-3b.Q4_K_M.gguf
    size_gb: 2.1
    ram_mb: 2500
    context_window: 8192
    threads: 6
    load_strategy: on_demand_10min
    entity: roc_racoon
  phi-4-mini-reasoning-abliterated-q4_k_m:
    path: /media/arcana-novai/omega_library/models/local/all/phi-4-mini-reasoning-abliterated-q4_k_m.gguf
    size_gb: 1.4
    ram_mb: 2000
    context_window: 16384
    threads: 6
    load_strategy: on_demand_10min
    entity: SOPHIA
  qwen3-vl:
    path: /media/arcana-novai/omega_library/models/local/all/Qwen3-VL-4B-Instruct-Q4_K_M.gguf
    size_gb: 2.4
    ram_mb: 3200
    context_window: 8192
    threads: 6
    load_strategy: on_demand_5min
    multimodal: true
    mmproj: /media/arcana-novai/omega_library/models/local/all/mmproj-model-f16.gguf
    entity: ARGUS
  krikri-8b-q4_k_m:
    path: /media/arcana-novai/omega_library/models/local/all/Krikri-8B-Instruct.Q4_K_M.gguf
    size_gb: 4.7
    ram_mb: 4900
    context_window: 16384
    threads: 6
    load_strategy: on_demand_5min
    entity: inanna, isis, lilith
kv_cache:
  default_key_type: q8_0
  default_value_type: q8_0
  models:
    qwen3-1.7b:
      key_type: f16
      value_type: f16
    qwen3-0.6b-q6_k:
      key_type: f16
      value_type: f16
    qwen3-4b-thinking-q4_k_m:
      key_type: q8_0
      value_type: q8_0
zen2_build:
  march: znver2
  cmake_flags:
  - -DLLAMA_AVX2=ON
  - -DLLAMA_FMA=ON
  - -DLLAMA_F16C=ON
  - -DLLAMA_NO_AVX512=ON
  - -DGGML_FLASH_ATTN=ON
  - -DLLAMA_BLAS=OFF
  - -DLLAMA_CUDA=OFF
  - -DLLAMA_METAL=OFF
  - -DCMAKE_C_FLAGS='-march=znver2'
  - -DCMAKE_CXX_FLAGS='-march=znver2'
  runtime_env:
    OMP_NUM_THREADS: '6'
    OMP_PROC_BIND: close
    OMP_PLACES: cores
    OPENBLAS_CORETYPE: ZEN
loading:
  max_concurrent_models: 1
  nova_always_on: true
  warm_models:
  - qwen3-0.6b-q6_k
  unload_after_idle_minutes: 5
  emergency_swap_threshold_mb: 1024
agent_roles:
  jem_discovery:
    # CONSOLIDATED into jem (Sprint B)
    tier: lite
    default_model: qwen3-0.6b-q6_k
    min_ram_gb: 8
  jem_synthesis:
    # CONSOLIDATED into jem (Sprint B)
    tier: medium
    default_model: qwen3-1.7b
    min_ram_gb: 16
  jem_verification:
    # CONSOLIDATED into jem (Sprint B)
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  scribe:
    # CONSOLIDATED into verity (Sprint C)
    tier: medium
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  quality:
    # CONSOLIDATED into verity (Sprint C)
    tier: medium
    default_model: qwen3-1.7b
    min_ram_gb: 16
  verity:
    # Sprint C: Unified Sentry (compliance/audit) + Scribe (gnosis distillation)
    tier: medium
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  doom_guy:
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  roc_racoon:
    tier: lite
    default_model: qwen3-1.7b
    min_ram_gb: 8
  kali:
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  pillar:
    tier: lite
    default_model: qwen3-1.7b
    min_ram_gb: 8
  plan:
    # REPLACED by makali (D117)
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  jem:
    tier: medium
    default_model: qwen3-1.7b
    min_ram_gb: 16
    # Sprint B: 3 KBs consolidated (Discovery/Synthesis/Verification) with self-dispatch
  maat:
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  lilith:
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
  researcher:
    tier: heavy
    default_model: qwen3-4b-thinking-q4_k_m
    min_ram_gb: 16
cloud_models:
  deepseek-v4-flash:
    provider: opencode / cline
    context_window:
      opencode_zen_free: 204800
      cline: 1048576
    strengths:
    - Code generation and analysis
    - Long-context task decomposition
    - Multi-file editing
    - Agent orchestration
    best_for: Primary coding session; agent dispatch (Kali/Ma'at/Lilith)
    tier: primary
  gemini-3.5-flash:
    provider: google_ai_studio
    context_window: 262144
    strengths:
    - Deep research and synthesis
    - Document analysis at scale
    - MaKaLi parallel council (fast)
    - Multi-perspective reasoning
    best_for: Research synthesis; parallel council; Roc Racoon deep analysis
    tier: primary
  gemini-4-31b:
    provider: google_ai_studio
    context_window: 262144
    strengths:
    - Very deep analysis
    - Complex reasoning chains
    - Long-form document generation
    best_for: Skeptical verifier; Roc Racoon heritage mining; deep research
    tier: secondary
  gemma-4-26b-it:
    provider: google_ai_studio
    context_window: 262144
    strengths:
    - Strict structural output (YAML/JSON/Code) with low entropy
    - Deep reasoning with Grouped-Query Attention
    - Scribe gnosis distillation and structural formatting
    - Multi-turn technical auditing with high precision
    best_for: Scribe gnosis distillation; structural code audits; Lucifer reasoning
      chains; SOPHIA deep analysis (cloud fallback)
    tier: secondary
    tuning_guide: data/entities/JOHN_CARMACK/workspace/gemma_4_26b_tuning_guide.md
  mimo-v2.5:
    provider: opencode / cline
    context_window: 128000
    strengths:
    - Structural pathology analysis
    - Deep architecture audits
    - Hidden layer detection
    best_for: Codebase archaeology; deep structural audits; oversight reviews
    tier: secondary
  nemotron-3-ultra:
    provider: UNVERIFIED — requires Researcher discovery
    context_window: UNVERIFIED
    strengths:
    - UNVERIFIED
    best_for: UNVERIFIED
    tier: fallback
  claude-sonnet-4:
    provider: UNVERIFIED — requires Researcher discovery
    context_window: UNVERIFIED
    strengths:
    - UNVERIFIED
    best_for: UNVERIFIED
    tier: fallback
  gemma-4-9b:
    provider: UNVERIFIED — requires Researcher discovery
    context_window: UNVERIFIED
    strengths:
    - UNVERIFIED
    best_for: UNVERIFIED
    tier: fallback

---
