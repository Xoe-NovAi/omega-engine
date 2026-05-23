# 🔱 Remote Provider Guide: Google Gemma 4-31B
**AP Token**: `AP-GEMMA-REMOTE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_core ⬡ PROVIDER-GUIDE

---

## §1 Overview
The Omega Engine utilizes Gemma 4-31B as a high-capability remote RAG agent. This allows the engine to provide deep reasoning and entity-centric responses without requiring massive local hardware (30GB+ RAM).

## §2 Integration Blueprint

### 2.1 API Providers & Auth
| Provider | Auth Method | Omega Integration |
|----------|-------------|-------------------|
| **Google Vertex AI** | OAuth 2 Service Account | `GOOGLE_APPLICATION_CREDENTIALS` env var |
| **AWS SageMaker** | IAM Role / SigV4 | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |
| **Azure ML** | Azure AD Token | `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` |
| **RunPod / Lambda** | Bearer Token | `Authorization: Bearer <TOKEN>` |

### 2.2 Network Reliability
- **Timeout**: 6s strict timeout.
- **Retry Policy**: Exponential back-off (base 0.5s, max 8s, 3 retries).
- **Circuit-Breaker**: 3 consecutive failures $\rightarrow$ mark provider `unhealthy` for 30s $\rightarrow$ fallback to `lmster`.

### 2.3 Parameter Defaults
| Use-case | Temp | Top-p | Max Tokens | Notes |
|----------|------|-------|-------------|--------|
| **General RAG** | 0.2 | 0.95 | 512 | Deterministic |
| **Summarization** | 0.0 | 1.0 | 256 | Extraction |
| **Entity Voice** | 0.4 | 0.9 | 300 | On-brand |
| **Creative/Poetic** | 0.7 | 0.9 | 400 | Lyrical |

## §3 Prompt Engineering for Remote Gemma

### 3.1 RAG Template
**System**: `You are a concise, factual assistant. Use only the supplied context. If the answer is not in the context, reply "I don't have enough information." Do not hallucinate.`
**User**: `Context:\n{retrieved_chunks}\n---\nQuestion:\n{user_query}`

### 3.2 Entity Voice Template
**System**: `You are {entity_name}, the keeper of the {pillar_name} pillar. Answer in the voice and style of this entity, using first-person pronouns when appropriate. Keep the reply under 200 tokens.`

### 3.3 Style Steering (Harmonic Adjustment)
Append the directive to the end of the prompt: `[/style:poetic]` or `[/style:concise]`.

## §4 Security & Costs
- **Secret Management**: All keys stored in `.env` (git-ignored) or Vaults.
- **Budget Guard**: `GEMMA_DAILY_BUDGET` env var tracks estimated cost per token.
- **Logging**: Mask all API tokens in `observability` logs.

## §5 Implementation Checklist
- [ ] Add `gemma_api` to `config/providers.yaml` (Priority 2).
- [ ] Implement `src/omega/oracle/backends/gemma_api.py`.
- [ ] Integrate fallback logic in `ModelGateway`.
- [ ] Add unit tests in `tests/test_gemma_api.py`.
