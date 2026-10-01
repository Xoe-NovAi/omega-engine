# 🔱 Omega Engine Hardening Plan — Phase 0: Measurement Baseline

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Phase**: 0 — Empirical Baseline  
**Days**: 1-2  
**Hardware Profile**: Light CPU, Heavy I/O — **Parallel OK**

---

## 📋 What I Am Working On
Establish empirical baseline for all subsequent phases. No optimization without measurement.

---

## 🔍 First Principles
**Carmack's Law of Empirical Truth**: Mastery is earned through implementation. Measure before optimizing. The 3-month Quake Pentium optimization blitz: measure → analyze → implement → verify.

**Current State**: Zero baseline data. All subsequent phases are guesswork without this.

---

## 🎯 Phase 0 Objectives

| Objective | Success Metric | Tool |
|-----------|----------------|------|
| Hardware baseline | CPU/memory/thermal at idle & load | `omega-hub_get_hardware_stats` |
| Test suite honesty | Real pass/fail/skip counts | `make test` + output parsing |
| Integration chain map | All MCP endpoints documented | Manual audit + `curl` tests |
| Thermal profile | Sustained load < 85°C | 30-min soak test |
| Memory pressure | OOM risk at concurrent loads | `omega-hub_get_system_stats` |

---

## 📋 Detailed Actions

### Day 1 Morning: Hardware Baseline (2 hours)

```bash
# 1. Idle baseline (30s sample)
omega-hub_get_hardware_stats --interval 0.3 --include_threads

# 2. Cold-start inference signature (native-gguf)
source .venv/bin/activate && python -c "
from omega.oracle.model_gateway import ModelGateway
gw = ModelGateway()
import time
start = time.time()
result = gw.generate(model_name='qwen3-1.7b', user_query='test', max_tokens=10)
print(f'Latency: {time.time()-start:.2f}s, Provider: {result.provider_name}')
"

# 3. Concurrent inference test (4 threads = LLAMA_CPP_N_THREADS)
# Run 4 simultaneous generations, measure thermal

# 4. Memory pressure test
# Load 3 models sequentially, measure RSS + zRAM
```

**Expected Outputs**:
- `data/coordination/hardware_baseline_20260721.json`
- `data/coordination/inference_signature_20260721.json`
- `data/coordination/thermal_profile_20260721.json`

### Day 1 Afternoon: Test Suite Honesty Audit (3 hours)

```bash
# 1. Run full test suite with verbose output
make test 2>&1 | tee data/coordination/test_output_20260721.txt

# 2. Parse for vanity counts vs real results
python scripts/audit_test_honesty.py data/coordination/test_output_20260721.txt

# 3. Identify quarantined/skipped tests
grep -E "(SKIP|XFAIL|xfail)" data/coordination/test_output_20260721.txt

# 4. Contract test coverage audit
pytest --collect-only -q | grep -E "contract|GenerateResult|isinstance" | wc -l
```

**Deliverable**: `data/coordination/test_honesty_report_20260721.md`

### Day 2 Morning: Integration Chain Mapping (3 hours)

```bash
# 1. MCP server inventory
ls -la mcp_servers/
ls -la mcp_servers/omega_hub/tools/

# 2. Endpoint discovery
curl -s http://127.0.0.1:8016/health
curl -s http://127.0.0.1:8016/debug/tools
curl -s http://127.0.0.1:8018/mcp/health  # SearXNG

# 3. Tool registration audit
python -c "
from mcp_servers.omega_hub.server import mcp
print(f'Registered tools: {len(mcp._tool_manager._tools)}')
for name in sorted(mcp._tool_manager._tools.keys()):
    print(f'  {name}')
"

# 4. Provider fabric trace
# Check gateway.py proxy_request implementation
# Verify ModelGateway.generate() is actually called
```

**Deliverable**: `data/coordination/integration_chain_map_20260721.md`

### Day 2 Afternoon: Thermal Soak Test (2 hours)

```bash
# 30-minute sustained load test
# Run continuous inference while monitoring thermal

for i in {1..60}; do
    omega-hub_get_hardware_stats --interval 0.3 >> data/coordination/thermal_soak_20260721.jsonl
    sleep 30
done

# Analyze: sustained temp, throttling events, frequency scaling
python scripts/analyze_thermal.py data/coordination/thermal_soak_20260721.jsonl
```

**Deliverable**: `data/coordination/thermal_analysis_20260721.md`

---

## 📊 Measurement Artifacts (All Must Exist Before Phase 1)

| Artifact | Location | Required Fields |
|----------|----------|-----------------|
| Hardware Baseline | `data/coordination/hardware_baseline_*.json` | cpu_per_core, memory, thermal, threads |
| Inference Signature | `data/coordination/inference_signature_*.json` | latency_p50, latency_p99, provider_name, threads_used |
| Test Honesty Report | `data/coordination/test_honesty_report_*.md` | real_pass, real_fail, real_skip, vanity_count |
| Integration Chain Map | `data/coordination/integration_chain_map_*.md` | endpoints, tools, providers, fallbacks |
| Thermal Analysis | `data/coordination/thermal_analysis_*.md` | max_temp, avg_temp, throttle_events, freq_scaling |

---

## ⚠️ Gate Criteria (Phase 0 → Phase 1)

**ALL must pass**:

- [ ] Hardware baseline documented with per-core CPU at idle
- [ ] Inference signature shows native-gguf as provider_name
- [ ] Test honesty report: 0 vanity counts, real pass/fail/skip
- [ ] Integration chain map: 100% MCP endpoints responding
- [ ] Thermal analysis: max_temp < 85°C under sustained load
- [ ] Memory pressure: no OOM risk at 4 concurrent inferences

---

## 🔧 Scripts Needed (Create if Missing)

```bash
# scripts/audit_test_honesty.py
# scripts/analyze_thermal.py
# scripts/map_integration_chain.py
```

---

## 📋 Confidence: 10/10
**Primary Source**: Hardware specs, empirical mandate, Carmack's Law of Empirical Truth.

**No assumptions. Only measurements.**

---

**Next**: See `PART_02_PHASE_1_SOUL_ARCHITECTURE.md` for Phase 1 detailed actions.