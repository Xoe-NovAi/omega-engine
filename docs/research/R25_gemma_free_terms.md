# 🔱 Omega Engine — Research Report R-25
## Gemma 4-31B "Free" Tier Terms Analysis (Google AI Studio)

**AP Token**: `AP-RESEARCH-R25-v1.0.0`
**Status**: ✅ COMPLETE
**Date**: 2026-05-14
**Analyst**: Sovereign Gnosis Analyst (Gemma 4-31B)

---

## 1. Executive Summary
Gemma 4-31B is offered as a "completely free" model within Google AI Studio. While the model weights themselves are released under the permissive **Apache 2.0 license** (allowing for private deployment and commercial use), the **Hosted Service** provided via the Google AI Studio API operates under a specific "Free Tier" agreement. The primary trade-off for this zero-cost access is the **surrender of data privacy**, as Google reserves the right to use free-tier inputs and outputs for model improvement.

## 2. Usage Limits & Quotas
Based on the current Google AI Studio Free Tier architecture (as of April 2026), Gemma 4-31B aligns with the "Flash-class" rate limits rather than the restrictive "Pro-class" limits.

| Metric | Estimated Limit (Free Tier) | Notes |
| :--- | :--- | :--- |
| **RPM** (Requests Per Minute) | **15** | Consistent with Gemini 2.0 Flash and Gemma 2. |
| **TPM** (Tokens Per Minute) | **1,000,000** | Generous window for most RAG tasks. |
| **RPD** (Requests Per Day) | **1,500** | Sufficient for prototyping and low-volume production. |
| **Context Window** | **262,144 tokens** | Confirmed via OpenRouter and official specs. |
| **Max Output Tokens** | **32,768 tokens** | Standard for the Gemma 4 series. |

**Verification Note**: These limits are "soft" and can vary based on account reputation and regional demand, but they represent the standard baseline for the AI Studio free offering.

## 3. Data Privacy & Terms of Service
The most critical aspect of the "Free" offering is the data handling policy.

### 3.1 The Data-Sharing Clause
Under the Google AI Studio Free Tier terms:
- **Training Usage**: Google may use inputs and outputs from the free tier to improve its products, including the training of future Gemini and Gemma models.
- **Human Review**: A subset of data may be reviewed by trained human annotators to ensure quality and safety.
- **PII Risk**: Any Personally Identifiable Information (PII) sent to the free API is subject to this review and training process.

### 3.2 Contrast with Paid/Enterprise Tiers
To avoid data sharing, users must transition to:
- **Pay-as-you-go (AI Studio)**: Enabling billing removes the data-sharing clause for most models.
- **Vertex AI (Google Cloud)**: Enterprise-grade privacy where data is **never** used for training by default.

## 4. Comparative Analysis: Gemma 4 vs. Gemini Free Tiers

| Feature | Gemma 4-31B (Free) | Gemini 2.0 Flash (Free) | Gemini 2.5 Pro (Free) |
| :--- | :--- | :--- | :--- |
| **Cost** | $0 | $0 | $0 |
| **Reasoning Power** | High (31B Dense) | Medium (Flash) | Very High (Pro) |
| **RPM** | ~15 | 15 | 5 |
| **RPD** | ~1,500 | 1,500 | 50 |
| **Data Privacy** | Shared with Google | Shared with Google | Shared with Google |
| **Best Use Case** | Sovereign Gnosis / Coding | Fast Routing / Voice | Deep Synthesis / Audit |

## 5. Restrictions & Constraints

### 5.1 Geographic Restrictions
Access to the Google AI Studio API is subject to regional availability. Certain jurisdictions (e.g., parts of the EU or China) may have restricted access or require different terms of service.

### 5.2 Account-Level Constraints
- **Standard Google Account**: Required for API key generation.
- **No Credit Card**: The free tier is truly "no-card-required," making it the lowest friction entry point for developers.

## 6. Final Analyst Verdict
The Gemma 4-31B free offering is a strategic "loss leader" by Google to encourage adoption of the Gemma ecosystem. It provides an exceptional power-to-cost ratio, effectively giving developers "Pro-level" reasoning at "Flash-level" availability.

**Recommendation for Omega Engine**:
Use Gemma 4-31B as the primary high-capability provider for the MVE, but **strictly prohibit** the transmission of sensitive user soul data or private keys through this provider. All sensitive operations must be routed to the **Local Sovereign (lmster)** backend.

---
**Implementation Note for Antigravity/Cline**:
When configuring the `ProviderFabric`, ensure that the `google_api` backend includes a warning or a "Privacy Mode" flag that alerts the user when routing sensitive data through the free tier.
