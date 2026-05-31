# GitHub Copilot Free Tier — OpenCode Configuration Template
# Ready-to-use configuration for Omega Engine integration

## opencode.json Configuration

```json
{
  "$schema": "https://opencode.ai/schema/opencode.json",
  "provider": {
    "github-copilot": {
      "name": "GitHub Copilot",
      "npm": "@ai-sdk/github-copilot",
      "models": {
        "claude-haiku-4.5": {
          "name": "Claude Haiku 4.5 — Fast Reasoning",
          "limit": {
            "context": 200000,
            "output": 64000
          },
          "cost": {
            "input": 0.001,
            "output": 0.005,
            "cache": {
              "read": 0.0001,
              "write": 0.0005
            }
          },
          "metadata": {
            "ttft_ms": 597,
            "throughput_tps": 78.9,
            "swe_bench": 73.3,
            "use_case": "real-time chat, rapid prototyping, agentic loops",
            "best_for_pillar": "P1 (Strength), P4 (Heart), P5 (Voice), P9 (Spirit)"
          }
        },
        "gpt-4.1": {
          "name": "GPT-4.1 — Balanced Workhorse",
          "limit": {
            "context": 1000000,
            "output": 32000
          },
          "cost": {
            "input": 0.0004,
            "output": 0.0016,
            "cache": {
              "read": 0.00004,
              "write": 0.00016
            }
          },
          "metadata": {
            "ttft_ms": 889,
            "throughput_tps": 42.4,
            "swe_bench": 72.0,
            "use_case": "document analysis, RAG pipelines, long-context reasoning",
            "best_for_pillar": "P3 (Will), P8 (Shadow)"
          }
        },
        "gpt-5-mini": {
          "name": "GPT-5 mini — Budget Reasoner",
          "limit": {
            "context": 400000,
            "output": 128000
          },
          "cost": {
            "input": 0.00025,
            "output": 0.002,
            "cache": {
              "read": 0.000025,
              "write": 0.0002
            }
          },
          "metadata": {
            "ttft_ms": 1200,
            "throughput_tps": 55.0,
            "reasoning_support": true,
            "use_case": "complex reasoning, multi-step problem solving, research",
            "best_for_pillar": "P6 (Mind), P7 (Gnosis)"
          }
        },
        "gpt-4o": {
          "name": "GPT-4o — Multimodal Specialist",
          "limit": {
            "context": 128000,
            "output": 4096
          },
          "cost": {
            "input": 0.00015,
            "output": 0.0006,
            "cache": {
              "read": 0.000015,
              "write": 0.00006
            }
          },
          "metadata": {
            "ttft_ms": 1000,
            "throughput_tps": 40.0,
            "vision_accuracy": 98.5,
            "use_case": "image analysis, screenshot understanding, multimodal tasks",
            "best_for_pillar": "P10 (Chaos)"
          }
        },
        "claude-sonnet-4.6": {
          "name": "Claude Sonnet 4.6 — Capable Generalist",
          "limit": {
            "context": 200000,
            "output": 64000
          },
          "cost": {
            "input": 0.003,
            "output": 0.015,
            "cache": {
              "read": 0.0003,
              "write": 0.0015
            }
          },
          "metadata": {
            "ttft_ms": 1946,
            "throughput_tps": 20.0,
            "swe_bench": 77.2,
            "reasoning_support": true,
            "use_case": "complex code generation, architectural design, research synthesis",
            "best_for_pillar": "P2 (Dream), P7 (Gnosis)"
          }
        }
      }
    }
  },
  "defaultProvider": "github-copilot",
  "defaultModel": "github-copilot/gpt-4.1"
}
```

## config/providers.yaml Configuration

```yaml
# Omega Engine Provider Fabric — GitHub Copilot Integration
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ providers.yaml ⬡ trc_core

inference:
  strategy: local_first_with_fallback
  description: "Prioritize local inference; use cloud as fallback"
  
  fallback_chain:
    # Priority 1: Native GGUF (Omega custom inference engine)
    - provider: native
      priority: 1
      enabled: true
      description: "Local GGUF inference (Ryzen 5700U, Zen 2 optimized)"
      backend: "llama-cpp-python"
      models:
        - "qwen3-1.7b"
        - "phi-2"
        - "krikri-8b"
      fallback_on_error: true
      fallback_on_timeout: true
      timeout_ms: 30000
      
    # Priority 2: lmster (LM Studio headless)
    - provider: lmster
      priority: 2
      enabled: true
      description: "LM Studio headless server (local, free)"
      endpoint: "http://127.0.0.1:1234"
      fallback_on_error: true
      fallback_on_timeout: true
      timeout_ms: 45000
      heartbeat:
        enabled: true
        interval_ms: 30000
        
    # Priority 3: GitHub Copilot Free Tier (NEW)
    - provider: github-copilot
      priority: 3
      enabled: true
      description: "GitHub Copilot Free Tier (official OpenCode support)"
      auth_method: "oauth"
      auth_env_var: "GITHUB_TOKEN"
      
      # Model routing strategy
      models:
        fast:
          model: "claude-haiku-4.5"
          use_case: "real-time chat, rapid prototyping"
          quota_cost: 1
          confidence_threshold: 0.70
          
        balanced:
          model: "gpt-4.1"
          use_case: "general coding, document analysis, RAG"
          quota_cost: 1
          confidence_threshold: 0.60
          
        reasoning:
          model: "gpt-5-mini"
          use_case: "complex reasoning, multi-step problem solving"
          quota_cost: 1
          confidence_threshold: 0.50
          
        vision:
          model: "gpt-4o"
          use_case: "image analysis, multimodal tasks"
          quota_cost: 1
          confidence_threshold: 0.65
          
        capable:
          model: "claude-sonnet-4.6"
          use_case: "complex code generation, architectural design"
          quota_cost: 1
          confidence_threshold: 0.45
      
      # Quota management
      quota:
        monthly_completions: 2000
        monthly_premium_requests: 50
        reset_day: 1
        reset_timezone: "UTC"
        tracking_enabled: true
        tracking_file: "data/quota/github-copilot.json"
        
      # Rate limiting
      rate_limits:
        session_limit: 15
        session_window_minutes: 60
        weekly_limit: 1000
        weekly_window_days: 7
        concurrent_requests: 1  # CRITICAL: Serialize to avoid burst limits
        request_delay_ms: 100   # Minimum delay between requests
        
      # Fallback behavior
      fallback_on_quota_exceeded: true
      fallback_on_rate_limit: true
      fallback_provider: "openrouter"
      
      # Error handling
      retry_strategy: "exponential_backoff"
      retry_max_attempts: 3
      retry_initial_delay_ms: 500
      retry_max_delay_ms: 5000
      
      # Monitoring
      observability:
        track_quota_usage: true
        track_rate_limits: true
        alert_at_quota_percent: 80
        alert_at_rate_limit: true
        
    # Priority 4: OpenRouter (paid fallback)
    - provider: openrouter
      priority: 4
      enabled: true
      description: "OpenRouter free + paid models (fallback)"
      api_key_env: "OPENROUTER_API_KEY"
      
    # Priority 5: Ollama (local fallback)
    - provider: ollama
      priority: 5
      enabled: true
      description: "Ollama local fallback"
      endpoint: "http://127.0.0.1:11434"

# Pillar-to-Model Mapping
pillar_routing:
  P1_strength:
    primary: "github-copilot/claude-haiku-4.5"
    fallback: "github-copilot/gpt-4.1"
    rationale: "Fast, protective"
    
  P2_dream:
    primary: "github-copilot/claude-sonnet-4.6"
    fallback: "github-copilot/claude-haiku-4.5"
    rationale: "Creative, capable"
    
  P3_will:
    primary: "github-copilot/gpt-4.1"
    fallback: "github-copilot/gpt-5-mini"
    rationale: "Reasoning, strategic"
    
  P4_heart:
    primary: "github-copilot/claude-haiku-4.5"
    fallback: "github-copilot/claude-sonnet-4.6"
    rationale: "Knowledge, speech"
    
  P5_voice:
    primary: "github-copilot/claude-haiku-4.5"
    fallback: "github-copilot/gpt-4o"
    rationale: "Fast, multimodal"
    
  P6_mind:
    primary: "github-copilot/gpt-5-mini"
    fallback: "github-copilot/claude-sonnet-4.6"
    rationale: "Deep reasoning"
    
  P7_gnosis:
    primary: "github-copilot/claude-sonnet-4.6"
    fallback: "github-copilot/gpt-5-mini"
    rationale: "Wisdom, rebellion"
    
  P8_shadow:
    primary: "github-copilot/gpt-4.1"
    fallback: "github-copilot/claude-sonnet-4.6"
    rationale: "Long context, pathwalking"
    
  P9_spirit:
    primary: "github-copilot/claude-haiku-4.5"
    fallback: "github-copilot/claude-sonnet-4.6"
    rationale: "Transition, guidance"
    
  P10_chaos:
    primary: "github-copilot/gpt-4o"
    fallback: "github-copilot/claude-haiku-4.5"
    rationale: "Vision, liberation"
```

## Quota Monitoring Script

```python
# scripts/monitor_copilot_quota.py
#!/usr/bin/env python3
"""
GitHub Copilot Free Tier Quota Monitor
Tracks monthly usage and alerts when approaching limits
"""

import json
import os
from datetime import datetime, date
from pathlib import Path

QUOTA_FILE = Path("data/quota/github-copilot.json")
QUOTA_LIMITS = {
    "monthly_completions": 2000,
    "monthly_premium_requests": 50,
}

def load_quota():
    """Load current quota usage from file."""
    if not QUOTA_FILE.exists():
        return {
            "month": date.today().month,
            "year": date.today().year,
            "completions_used": 0,
            "premium_requests_used": 0,
        }
    with open(QUOTA_FILE) as f:
        return json.load(f)

def save_quota(quota):
    """Save quota usage to file."""
    QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUOTA_FILE, "w") as f:
        json.dump(quota, f, indent=2)

def reset_if_new_month(quota):
    """Reset quota if we've entered a new month."""
    today = date.today()
    if quota["month"] != today.month or quota["year"] != today.year:
        quota["month"] = today.month
        quota["year"] = today.year
        quota["completions_used"] = 0
        quota["premium_requests_used"] = 0
    return quota

def record_completion(quota):
    """Record an inline completion."""
    quota["completions_used"] += 1
    return quota

def record_premium_request(quota):
    """Record a premium request (chat, model switch, etc)."""
    quota["premium_requests_used"] += 1
    return quota

def get_status(quota):
    """Get human-readable quota status."""
    completions_pct = (quota["completions_used"] / QUOTA_LIMITS["monthly_completions"]) * 100
    requests_pct = (quota["premium_requests_used"] / QUOTA_LIMITS["monthly_premium_requests"]) * 100
    
    return {
        "month": f"{quota['year']}-{quota['month']:02d}",
        "completions": {
            "used": quota["completions_used"],
            "limit": QUOTA_LIMITS["monthly_completions"],
            "remaining": QUOTA_LIMITS["monthly_completions"] - quota["completions_used"],
            "percent_used": completions_pct,
        },
        "premium_requests": {
            "used": quota["premium_requests_used"],
            "limit": QUOTA_LIMITS["monthly_premium_requests"],
            "remaining": QUOTA_LIMITS["monthly_premium_requests"] - quota["premium_requests_used"],
            "percent_used": requests_pct,
        },
        "alerts": [
            f"⚠️  Completions at {completions_pct:.1f}%" if completions_pct > 80 else None,
            f"⚠️  Premium requests at {requests_pct:.1f}%" if requests_pct > 80 else None,
            "🚨 Completions EXHAUSTED" if quota["completions_used"] >= QUOTA_LIMITS["monthly_completions"] else None,
            "🚨 Premium requests EXHAUSTED" if quota["premium_requests_used"] >= QUOTA_LIMITS["monthly_premium_requests"] else None,
        ]
    }

if __name__ == "__main__":
    quota = load_quota()
    quota = reset_if_new_month(quota)
    status = get_status(quota)
    
    print(f"GitHub Copilot Free Tier — {status['month']}")
    print(f"Completions: {status['completions']['used']}/{status['completions']['limit']} ({status['completions']['percent_used']:.1f}%)")
    print(f"Premium Requests: {status['premium_requests']['used']}/{status['premium_requests']['limit']} ({status['premium_requests']['percent_used']:.1f}%)")
    
    for alert in status["alerts"]:
        if alert:
            print(alert)
```

## Integration Checklist

- [ ] Copy `opencode.json` configuration to `.opencode/opencode.json`
- [ ] Copy `providers.yaml` configuration to `config/providers.yaml`
- [ ] Run `opencode auth connect github-copilot` to authenticate
- [ ] Verify authentication: `opencode auth list`
- [ ] Create `data/quota/` directory: `mkdir -p data/quota`
- [ ] Copy quota monitoring script to `scripts/monitor_copilot_quota.py`
- [ ] Test model routing: `/entity PROMETHEUS` (should use GPT-4.1)
- [ ] Monitor first week of usage
- [ ] Update `CONTRIBUTING.md` with Copilot setup instructions
- [ ] Document rate-limit workarounds in `docs/operations/`

## Testing Commands

```bash
# Verify authentication
opencode auth list

# Check quota status
python scripts/monitor_copilot_quota.py

# Test fast model (Haiku)
opencode summon SEKHMET "What is your primary function?"

# Test balanced model (GPT-4.1)
opencode summon PROMETHEUS "Analyze this code architecture"

# Test reasoning model (GPT-5 mini)
opencode summon ERESHKIGAL "Explain quantum entanglement"

# Test vision model (GPT-4o)
opencode summon KALI "Analyze this image" --image screenshot.png

# Test capable model (Sonnet)
opencode summon BRIGID "Write a poem about the Omega Engine"
```

---

**Status**: ✅ Ready for implementation
**Estimated Integration Time**: 30 minutes
**Testing Time**: 1-2 hours
**Risk Level**: Low (fallback chain ensures resilience)
