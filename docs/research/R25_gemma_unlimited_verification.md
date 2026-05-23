# 🔱 Omega Engine — Gemma 4-31B "Unlimited" Verification Report
**AP Token**: `AP-RESEARCH-VERIFY-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ VERIFICATION

---

## 🎯 Executive Summary

The claim that Gemma 4-31B is "completely free" on Google AI Studio is **accurate regarding monetary cost but inaccurate regarding usage limits**. While there is no charge per token, the service is subject to strict rate limits (RPM/RPD) and specific data-usage agreements characteristic of Google's developer free tiers.

**Verdict**: ⚠️ **NOT UNLIMITED**. It is a "Free Tier" with quotas, not an "Unlimited" service.

---

## 📊 Verified Limits & Quotas

Based on synthesis of official documentation and community-observed behavior (2026):

| Metric | Observed / Reported Value | Note |
| :--- | :--- | :--- |
| **Cost** | $0.00 / 1M tokens | No credit card required for basic free tier. |
| **Requests Per Minute (RPM)** | ~15 RPM | Rolling 60-second window. |
| **Requests Per Day (RPD)** | ~1,500 RPD | Resets at midnight Pacific Time (PT). |
| **Context Window** | 262,144 tokens | High capacity for RAG and long-context analysis. |
| **Max Output Tokens** | 32,768 tokens | Sufficient for complex code generation. |
| **Reset Cycle** | Rolling (RPM) / Daily (RPD) | Standard Google AI Studio quota behavior. |

---

## 🔍 Detailed Investigation

### 1. "Hidden" or Soft Limits
There are no "hidden" limits in the sense of secret throttles, but there are **dynamic quotas**. Google AI Studio rate limits are not static; they can fluctuate based on:
- **Project Standing**: New projects may have lower initial limits.
- **Global Demand**: During peak load, "Free Tier" users may experience increased latency or temporary 429 (Too Many Requests) errors even below the nominal limit.
- **Account History**: Accounts with a history of compliant usage may see slight quota increases.

### 2. Comparison with Gemini 2.0 Flash/Pro
Gemma 4-31B follows the same quota architecture as the Gemini 2.0 family. The primary difference is the **model capability vs. cost trade-off**. While Gemini 2.0 Pro Thinking has much stricter limits due to compute intensity, Gemma 4-31B is more "generous" because it is a smaller, dense model, but it still adheres to the RPD/RPM framework.

### 3. Geographic and Account Quotas
- **Regional Availability**: Access is restricted to eligible regions. Users in unsupported regions must use VPNs or Vertex AI (Paid), which changes the pricing model entirely.
- **Account Tiers**: There is a distinction between the "Free of Charge" tier and the "Pay-as-you-go" tier. The latter removes some RPD limits but introduces costs.

### 4. Data Usage & Privacy Terms
The "completely free" nature of the API comes with a significant trade-off:
- **Data Training**: In the Free Tier, Google reserves the right to use inputs and outputs to improve their products. This means **sensitive data, secrets, or proprietary code should NOT be sent to the free tier API**.
- **Privacy**: This is the primary "cost" of the free tier. For sovereign privacy, the user must transition to **local sovereign inference (lmster/Ollama)**.

---

## 🛠️ Strategic Recommendations for Omega Engine

To mitigate the risk of quota exhaustion and data leakage:

1.  **Implement Exponential Backoff**: The `ModelGateway` must handle HTTP 429 errors with a jittered exponential backoff to avoid permanent blocks.
2.  **Strict Secret Sanitization**: Because the free tier is used for training, the `omega-sanitizer` (R-09) is **CRITICAL** and must be positioned *before* the request leaves the local environment.
3.  **Hybrid Fallback Chain**:
    - `Primary`: Remote Gemma 4-31B (for high-reasoning tasks).
    - `Secondary`: Local `lmster` (for privacy-sensitive or high-volume tasks).
    - `Tertiary`: Mock/Fallback.
4.  **Quota Tracking**: Implement a local counter to track RPD and proactively switch to local inference when approaching the 1,500 request limit.

---

**Implementation Note for Antigravity/Cline**: 
Ensure the `ProviderFabric` does not assume "unlimited" capacity. Configure the default timeout for Google AI Studio to be slightly higher than local backends to account for potential "Free Tier" queuing/latency.
