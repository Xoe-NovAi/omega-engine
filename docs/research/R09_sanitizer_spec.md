# 🔱 Omega Engine — PII & Secret Sanitization Spec
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R09

**AP Token**: `AP-RESEARCH-R09-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-14
**Status**: READY

---

## Summary
This specification defines the `omega-sanitizer`, a high-performance, low-latency middleware designed to prevent the leakage of Personally Identifiable Information (PII) and cryptographic secrets to remote LLM providers (specifically Google AI Studio free tier). It implements a hybrid approach combining deterministic regex patterns for secrets and lightweight NER for PII, ensuring minimal impact on the Ryzen 5700U CPU and 14GB RAM envelope.

## Findings

### 1. Target Leakage Surface
The following categories of sensitive data are most likely to appear in Omega Engine prompts:

| Category | Examples | Risk Level |
|----------|----------|------------|
| **Cloud API Keys** | Google AI Studio, SambaNova, Cerebras, OpenAI, Anthropic | 🔴 Critical |
| **Infrastructure** | SSH Private Keys, AWS Access Keys, Database Passwords | 🔴 Critical |
| **User PII** | Emails, Physical Addresses, Phone Numbers, Full Names | 🟡 High |
| **Session Data** | JWTs, Session Cookies, OAuth Tokens | 🟡 High |
| **Network Info** | Internal IP addresses, Private DNS records | 🟢 Medium |

### 2. Solution Evaluation (Ryzen 5700U / 14GB RAM)
A hybrid approach is recommended to balance accuracy and performance:
- **Regex-based**: Used for high-confidence secrets (API keys). Extremely fast, zero memory overhead.
- **Lightweight NER (`spaCy en_core_web_sm`)**: Used for PII (names, locations). Minimal memory footprint (~100MB) and low latency (10-30ms).

### 3. Interface Design: `omega-sanitizer`
- **Pipeline Position**: Pre-ModelGateway interceptor.
- **Masking Strategies**:
    - **Irreversible (Cloud)**: `user@email.com` $\rightarrow$ `[EMAIL_REDACTED]`.
    - **Reversible (Local)**: `SecretValue` $\rightarrow$ `TOKEN_A1` (mapped in transient session memory).

## Recommendations
1. Implement `src/omega/oracle/sanitizer.py` using a singleton for the `spaCy` model.
2. Store regex patterns in `config/sanitizer.yaml` for maintainability.
3. Pre-compile all regex patterns at module load time to minimize per-request latency.

### Top 20 Regex Patterns for Secrets/PII
- **Google API Key**: `AIza[0-9A-Za-z-_]{35}`
- **OpenAI API Key**: `sk-[a-zA-Z0-9]{48}`
- **Anthropic Key**: `sk-ant-api03-[a-zA-Z0-9\-_]{93}`
- **SambaNova Key**: `sn_[a-zA-Z0-9]{32,64}`
- **Cerebras Key**: `cb_[a-zA-Z0-9]{32,64}`
- **AWS Access Key**: `AKIA[0-9A-Z]{16}`
- **AWS Secret Key**: `[a-zA-Z0-9/+=]{40}`
- **Generic Secret**: `(?i)(password|secret|api_key|token|passwd|auth)["']?\s*[:=]\s*["']([^"']+)["']`
- **Email**: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **IPv4 Address**: `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`
- **Credit Card**: `\b(?:\d[ -]*?){13,16}\b`
- **JWT**: `eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*`
- **SSH Private Key**: `-----BEGIN [A-Z ]+ PRIVATE KEY-----`
- **SSH Public Key**: `ssh-rsa\s+[A-Za-z0-9+/=]+`
- **Bearer Token**: `Bearer\s+[a-zA-Z0-9\-\._~\+/]+=*`
- **MAC Address**: `([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})`
- **Phone (Intl)**: `\+?\d{1,3}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}`
- **UUID**: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
- **Mongo URI**: `mongodb\+srv:\/\/([^:]+):([^@]+)@([^/]+)`
- **Postgres URI**: `postgres:\/\/([^:]+):([^@]+)@([^/]+)`

## Implementation Note
_For: Antigravity IDE / Cline_
Implement as a class `OmegaSanitizer` in `src/omega/oracle/sanitizer.py`. Integrate into `ModelGateway._send_request` to ensure all outgoing prompts are cleaned before transmission.
