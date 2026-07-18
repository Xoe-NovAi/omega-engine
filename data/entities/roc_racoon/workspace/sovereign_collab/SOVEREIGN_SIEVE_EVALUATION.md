# 🔱 SOVEREIGN-SDK-SIEVE TECHNICAL EVALUATION
**AP Token**: `AP-SIEVE_EVAL-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sieve_eval ⬡ PLANNING

**Date**: 2026-07-18
**Status**: PLANNING — Evaluation protocol defined, execution pending
**Source**: `kenwalger/sovereign-sdk/packages/sovereign-sieve/`
**Package**: `sovereign-sdk-sieve` on PyPI (MIT license)

---

## 📦 PACKAGE OVERVIEW

| Attribute | Value |
|-----------|-------|
| **Package** | `sovereign-sdk-sieve` |
| **Install** | `pip install sovereign-sdk-sieve` |
| **Dependencies** | **Zero** — pure Python, no external deps |
| **Python** | 3.10+ |
| **License** | MIT |
| **Source** | `packages/sovereign-sieve/src/sovereign_sieve/sieve.py` |
| **Tests** | `packages/sovereign-sieve/tests/test_sieve.py` |

---

## 🔧 API SURFACE

```python
from sovereign_sieve import pure_sieve, sieve_with_metrics, SieveOutput

# 1. Pure synchronous sieve — drop-in string cleaner
clean = pure_sieve("Hello! Please just help me analyze this dataset.")
# → "! help me analyze this dataset."

# 2. Sieve with immediate FinOps telemetry
result = sieve_with_metrics("Hi! I hope this helps. Please just run the pipeline.")
print(result.text)                    # "! helps. run the pipeline."
print(result.raw_token_count)         # estimated tokens before
print(result.optimized_token_count)   # estimated tokens after
print(result.tax_savings_percentage)  # e.g. 66.6667

# 3. SieveOutput dataclass
@dataclass
class SieveOutput:
    text: str
    raw_token_count: int
    optimized_token_count: int
    tax_savings_percentage: float
```

---

## 🎯 SIEVE PATTERNS (from source)

| Category | Patterns Stripped | Negative Lookahead Guards |
|----------|-------------------|---------------------------|
| Greeting tokens | `hi`, `hello`, `hey`, `greetings` | `(?![-\w])` |
| Hedging adverbs | `just`, `simply`, `actually`, `basically`, `probably` | `(?![-\w])` |
| Affirmation filler | `of course`, `certainly`, `absolutely`, `sure` | word boundaries |
| Preamble phrases | `I hope this`, `I hope that`, `I hope you` | word boundaries |
| Politeness tokens | `please`, `kindly` | `(?![-\w])` |

**Key Design**: All patterns carry negative lookahead `(?![-\w])` so technical compounds pass through unmarred:
- `hi-fi` ✓ (not stripped)
- `just-in-time` ✓
- `certainly-not` ✓
- `hi` ✗ (stripped)

---

## 📊 EVALUATION PROTOCOL

### Phase 1: Correctness & False Positive Rate
**Corpus**: Omega test fixtures + real session transcripts
**Metrics**:
- False positive rate on technical terminology (target: <0.5%)
- False negative rate on conversational boilerplate (target: <5%)
- Unicode handling (emoji, multi-byte, RTL)

### Phase 2: Token Reduction Benchmarks
**Corpus**: 
- Omega Hivemind context snapshots (100 samples)
- MemoryStore ingestion payloads (100 samples)
- Real user prompts from OpenCode DB (100 samples)

**Metrics**:
- Mean token reduction % (target: >40%)
- Median token reduction %
- P95 token reduction %
- Distribution histogram

### Phase 3: Performance
**Metrics**:
- Latency per KB (target: <1ms/KB)
- Memory allocation profile
- Throughput (MB/s)

### Phase 4: Integration Compatibility
**Integration Points**:
1. `MemoryStore.add_exchange()` — sieve user input before storage
2. `MemoryStore.search()` — sieve query before retrieval
3. Hivemind context compression — sieve before token budget enforcement
4. Ingestion pipeline — sieve at Ingestion Boundary (Write-Side Custody)

**Compatibility Checks**:
- AnyIO async wrapper needed? (sieve is sync)
- Token estimation method compatibility (tiktoken vs rough heuristic)
- Pydantic model integration
- Configurable pattern overrides (Omega-specific boilerplate)

---

## 🧪 TEST MATRIX

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Basic greeting | "Hi! Please help me." | "! help me." |
| Technical compound | "Configure hi-fi audio for just-in-time processing." | UNCHANGED |
| Hedging | "I basically just want to simply run it." | "want to run it." |
| Affirmation | "Of course! Certainly I can absolutely help." | "help." |
| Preamble | "I hope this helps you understand the problem." | "understand the problem." |
| Politeness | "Please kindly run the analysis." | "run the analysis." |
| Mixed | "Hey! I hope you're well. Just please help me with this hi-fi setup." | "help me with this hi-fi setup." |
| Empty | "" | "" |
| Only boilerplate | "Hi hello hey please thanks" | "" |
| Unicode | "Hola! Por favor ayuda." | "ayuda." |
| Code-like | "def hello():\n    print('hi')" | UNCHANGED |

---

## 📈 SUCCESS CRITERIA

| Criterion | Threshold | Decision |
|-----------|-----------|----------|
| False positive rate (technical terms) | < 0.5% | **GO/NO-GO** |
| Mean token reduction (real prompts) | > 40% | **GO/NO-GO** |
| Latency | < 1ms/KB | **GO/NO-GO** |
| Integration complexity | < 2 hours | **GO/NO-GO** |
| License compatibility | MIT ✓ | **PASS** |
| Maintenance velocity | 39 releases, active | **PASS** |

---

## 🔄 INTEGRATION DESIGN (Post-GO)

### Option A: Ingestion Boundary (Write-Side Custody)
```python
# src/omega/memory_store.py
from sovereign_sieve import pure_sieve

class MemoryStore:
    async def add_exchange(self, entity: str, user: str, assistant: str):
        # Sieve at write-time — Pre-Paid Retrieval Precision
        clean_user = pure_sieve(user)
        clean_assistant = pure_sieve(assistant)
        await self._write(clean_user, clean_assistant)
```

### Option B: Query Optimization
```python
# src/omega/memory_store.py
from sovereign_sieve import pure_sieve

async def search(self, query: str, ...):
    clean_query = pure_sieve(query)
    return await self._search(clean_query, ...)
```

### Option C: Hivemind Context Compression
```python
# src/omega/hivemind/context_compressor.py
from sovereign_sieve import sieve_with_metrics

def compress_context(context: str, budget: int) -> CompressedContext:
    result = sieve_with_metrics(context)
    # If still over budget, apply additional compression
    return CompressedContext(
        text=result.text,
        tokens_saved=result.raw_token_count - result.optimized_token_count,
        tax_savings_pct=result.tax_savings_percentage
    )
```

### Option D: Configurable Omega Patterns
```python
# config/sieve_patterns.yaml
omega_patterns:
  - pattern: r"\b(?:omega|engine|stack|wad|pillar|mandate)\b"
    action: "preserve"  # Never strip domain terms
  - pattern: r"\b(?:please|kindly)\b"
    action: "strip"     # Override default if needed
```

---

## 📋 EXECUTION CHECKLIST

- [ ] Install `sovereign-sdk-sieve` in Omega venv
- [ ] Run package tests: `uv run pytest packages/sovereign-sieve/tests/`
- [ ] Create Omega test corpus (300 samples)
- [ ] Run Phase 1: Correctness
- [ ] Run Phase 2: Token reduction benchmarks
- [ ] Run Phase 3: Performance
- [ ] Run Phase 4: Integration prototype
- [ ] Document results in this file
- [ ] GO/NO-GO decision
- [ ] If GO: Implement integration Option A + B + C
- [ ] Add `sovereign-sdk-sieve` to `pyproject.toml` optional dependencies
- [ ] Create `config/sieve_patterns.yaml` for Omega domain terms

---

## 📝 NOTES & OBSERVATIONS

**Strengths**:
- Zero dependencies — aligns with M8, M16, M18
- Synchronous, pure — trivial to wrap in `anyio.to_thread.run_sync`
- Negative lookahead guards — handles technical compounds correctly
- Published on PyPI with 39 releases — maintained
- MIT license — compatible

**Risks**:
- Token estimation is heuristic (rough chars/4) — not tiktoken
- Patterns are English-centric — may need multilingual extension
- No streaming/chunked API — whole string at once
- Pattern list is fixed — not user-extensible without fork

**Mitigations**:
- Wrap with tiktoken for accurate counts if needed
- Add Omega-specific preserve patterns via pre/post processing
- For streaming: sieve per-chunk or buffer

---

*⬡ OMEGA ⬡ SIEVE_EVAL v1.0 ⬡ 2026-07-18 ⬡ PLANNING*