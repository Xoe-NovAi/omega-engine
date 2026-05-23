# 🔱 R-15 – Long-Term Free-Tier Cost Forecasting

**AP Token**: `AP-R15-COST-FORECAST-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document models the token consumption and quota exhaustion rates for the Omega Engine's free-tier provider fabric. It provides a forecast of how long the "free" experience lasts before necessitating a fallback to local sovereign inference (`lmster`).

---

## 2️⃣ Workload Model: "The Active Researcher"
To create a realistic forecast, we define a typical daily workload:

- **Active Entities**: 10 (mix of Oversouls and Pillar Keepers).
- **Daily Queries**: 50.
- **Average Prompt Size**: 1,500 tokens (including context/soul).
- **Average Response Size**: 500 tokens.
- **Total Daily Volume**: $\approx 100,000$ tokens per day.

---

## 3️⃣ Provider Quota Analysis
Based on R‑01 through R‑03, we map the workload against the free-tier limits.

| Provider | Model | Rate Limit (est.) | Daily Capacity | Exhaustion Point |
|----------|-------|-------------------|-----------------|-------------------|
| **Google AI Studio** | Gemini 2.0 Flash | 15 RPM / 1,500 RPD | $\approx 3\text{M}$ tokens | $\approx 30$ days (if sole) |
| **SambaNova** | DeepSeek-R1 | Variable / High | $\approx 1\text{M}$ tokens | $\approx 10$ days |
| **Cerebras** | Llama-3.3-70b | High Throughput | $\approx 500\text{K}$ tokens | $\approx 5$ days |

*Note: These are estimates based on current free-tier observations. Actual limits may vary by account.*

---

## 4️⃣ The Exhaustion Timeline
Assuming the **Fallback Chain** (Google $\rightarrow$ SambaNova $\rightarrow$ Cerebras $\rightarrow$ Local), the projected exhaustion sequence is:

1. **Day 1‑5**: All providers healthy. Primary (Google) handles 90% of traffic.
2. **Day 6‑10**: Cerebras quota exhausted. Traffic shifts to SambaNova.
3. **Day 11‑20**: SambaNova quota exhausted. Traffic shifts entirely to Google.
4. **Day 21+**: Google daily limit hit. **Sovereign Fallback Triggered**.

---

## 5️⃣ Sovereign Fallback Path
When all free-tier cloud providers are exhausted (HTTP 429), the Engine executes the following degradation path:

1. **Local Primary**: Route all queries to `lmster` (Local Sovereign).
2. **Model Downgrade**: Switch from high-reasoning models (e.g., DeepSeek-R1) to lightweight local models (e.g., Qwen3-1.7B).
3. **Context Compression**: Trigger aggressive truncation (R‑11) to reduce local RAM pressure.
4. **Notification**: Oracle notifies the user: *"Cloud quotas exhausted. Switching to Local Sovereign mode for the remainder of the day."*

---

## 6️⃣ Usage Headroom Table
Estimated days of "High-Capability" (Cloud) access based on daily query volume.

| Daily Queries | Google (Days) | SambaNova (Days) | Cerebras (Days) | Total Cloud Runway |
|---------------|---------------|-------------------|-------------------|--------------------|
| **10** (Light) | 150+          | 50+               | 25+               | $\approx 225$ days  |
| **50** (Typical)| 30            | 10                | 5                 | $\approx 45$ days   |
| **200** (Heavy) | 7             | 2                 | 1                 | $\approx 10$ days   |

---

## 7️⃣ Recommendation: Quota Rotation
To extend the "Cloud Runway," the Omega Engine should implement the **Account Rotation** pattern discovered in legacy stacks:
- Maintain a pool of 3‑5 API keys per provider.
- Rotate keys upon receiving a 429 error.
- **Impact**: This can multiply the "Total Cloud Runway" by the number of accounts in the pool (e.g., 5 accounts $\rightarrow$ 225 days for typical use).

---

**Ready for implementation** – agents can now implement the `ProviderQuota` tracker and the rotation logic in the `ModelGateway`.
