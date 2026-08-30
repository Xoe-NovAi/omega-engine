# 🔱 KG-2: OAuth Security Best Practices for Plugins
**AP Token**: `AP-KG2-OAUTH-SECURITY-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-25

<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Xoe-NovAi Foundation -->

## Executive Summary

This document synthesizes OAuth 2.0 and OpenID Connect security best practices from authoritative sources (RFC 9700, RFC 6819, OpenID Connect Core 1.0) to create a comprehensive security checklist for OAuth plugin development in the Omega Engine ecosystem.

## Methodology

Analyzed three authoritative sources:
1. **RFC 9700** - OAuth 2.0 Security Best Current Practice (January 2025)
2. **RFC 6819** - OAuth 2.0 Threat Model and Security Considerations (January 2013)
3. **OpenID Connect Core 1.0** - Identity layer on top of OAuth 2.0 (December 2023)

## Critical Security Threats and Mitigations

Based on the threat models in RFC 6819 and RFC 9700, here are the most critical threats for OAuth plugins and their mitigations:

### 🔴 CRITICAL THREATS & MANDATORY MITIGATIONS

| Threat | Description | Mitigation (RFC 9700/6819/OIDC) |
|--------|-------------|----------------------------------|
| **Authorization Code Injection** | Attacker steals authorization code and exchanges it for tokens | **MUST** use PKCE (RFC 7636) for public clients; **SHOULD** use PKCE for confidential clients |
| **Access Token Leakage via Browser History** | Access tokens in URL fragments leaked through browser history/referrer | **MUST NOT** use implicit grant (response_type=token); **USE** authorization code flow with PKCE |
| **Redirect URI Validation Attacks** | Inadequate validation allowing attacker to redirect codes/tokens to malicious sites | **MUST** use exact string matching for redirect URIs (except localhost port variation) |
| **CSRF on Authorization Request** | Attacker tricks user into authorizing attacker's client instead of victim's | **MUST** use state parameter with cryptographically random value tied to user agent session |
| **Token Replay** | Stolen tokens reused by attacker | **SHOULD** implement sender-constrained access tokens via DPoP (RFC 9449) or mTLS (RFC 8705) |
| **Refresh Token Theft** | Long-lived refresh tokens stolen and abused | **MUST** implement refresh token rotation (RFC 6819 5.2.2.3) for public clients; **SHOULD** bind to client_id |
| **Credential Leakage via Referrer** | Sensitive data in URLs leaked via HTTP Referer header | **MUST** use form post response mode for sensitive responses; **AVOID** putting tokens in URL parameters |

### 🟠 HIGH PRIORITY SECURITY PRACTICES

| Practice | Description | Implementation Guidance |
|----------|-------------|-------------------------|
| **Token Audience Restriction** | Limit access tokens to specific resource servers | **USE** `aud` claim in JWT tokens; **VERIFY** audience at resource server |
| **Token Scope Minimization** | Grant minimum necessary permissions | **APPLY** principle of least privilege; **AVOID** over-scoped tokens |
| **Short-Lived Access Tokens** | Reduce window of opportunity for token misuse | **TARGET** access token lifetime of 5-15 minutes; use refresh tokens for long-term access |
| **Proof Key for Code Exchange (PKCE)** | Prevent authorization code interception attacks | **IMPLEMENT** S256 code challenge method; **GENERATE** cryptographically random code_verifier (43-128 chars) |
| **State Parameter Protection** | Prevent CSRF in OAuth flows | **USE** cryptographically random state (min 128 bits); **BIND** to user agent session; **VALIDATE** exact match |
| **TLS Everywhere** | Protect all communications in transit | **ENFORCE** TLS 1.2+ for all OAuth endpoints; **USE** HSTS; **AVOID** TLS termination at proxies when possible |
| **Client Authentication** | Prevent unauthorized token requests | **USE** asymmetric client authentication (private_key_jwt) when possible; **AVOID** client secrets in public clients |

### 🟡 MEDIUM PRIORITY SECURITY PRACTICES

| Practice | Description | Implementation Guidance |
|----------|-------------|-------------------------|
| **Token Binding** | Cryptographically bind tokens to client/device | **CONSIDER** DPoP (RFC 9449) or mTLS (RFC 8705) for high-security applications |
| **JWT Best Practices** | Secure handling of JSON Web Tokens | **USE** appropriate signing algorithms (RS256, ES256); **AVOID** `none` algorithm; **VALIDATE** issuer, audience, expiration |
| **Nonce Usage** | Prevent ID token replay in implicit/hybrid flows | **INCLUDE** nonce in authentication requests; **VERIFY** nonce in ID token matches request |
| **Issuer Validation** | Prevent token acceptance from unauthorized issuers | **VALIDATE** `iss` claim against trusted issuers; **USE** issuer discovery when available |
| **Token Storage Security** | Protect tokens at rest | **USE** secure storage (Keychain, Keystore, encrypted storage); **AVOID** plain text storage |
| **Memory Protection** | Prevent token leakage via memory dumps | **ZEROIZE** sensitive memory after use; **USE** secure memory allocation when possible |
| **Dependency Scanning** | Prevent vulnerabilities in dependencies | **REGULARLY** scan dependencies for known vulnerabilities; **USE** lockfiles for reproducible builds |

## Omega Engine Plugin-Specific Recommendations

### 🔐 Auth Plugin Development Guidelines

1. **Always Use Authorization Code Flow with PKCE**
   - Never use implicit grant for browser-based plugins
   - Implement PKCE with S256 code challenge method
   - Generate cryptographically random code_verifier (43-128 characters)
   - Use code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))

2. **Implement Proper State Handling**
   - Generate cryptographically random state value (min 128 bits/16 bytes)
   - Store state in user agent session (not local/session storage)
   - Verify state parameter exactly matches original value
   - Clear state after use to prevent replay

3. **Secure Token Storage**
   - Access tokens: Short-lived, store in memory when possible
   - Refresh tokens: Use secure storage (OS credential manager, encrypted storage)
   - Never store tokens in plain text or local/session storage
   - Implement token rotation for refresh tokens

4. **Validate All Incoming Tokens**
   - Verify signature using trusted public keys/JWKS
   - Check issuer (iss) claim against trusted issuers
   - Validate audience (aud) contains your client ID
   - Check expiration (exp) and not-before (nbf) claims
   - Validate token is not revoked (if applicable)

5. **Implement Proper Error Handling**
   - Never leak sensitive information in error messages
   - Log security-relevant events for audit trails
   - Fail securely - deny access by default on uncertainty

### 📋 Security Checklist for OAuth Plugin Development

#### 🛡️ Before Development
- [ ] Review OAuth 2.0 threat model (RFC 6819 Sections 4-5)
- [ ] Study OAuth 2.0 Security BCP (RFC 9700)
- [ ] Understand OpenID Connect security considerations (Section 16)
- [ ] Define threat model for your specific plugin use case
- [ ] Identify assets to protect (tokens, user data, etc.)

#### 🔧 During Development
- [ ] **NEVER** use implicit grant (response_type=token) in browser plugins
- [ ] **ALWAYS** implement PKCE for authorization code flow
- [ ] **ALWAYS** use state parameter with CSRF protection
- [ ] **ALWAYS** validate redirect URIs with exact string matching
- [ ] **ALWAYS** use HTTPS/TLS 1.2+ for all communications
- [ ] **NEVER** put access tokens in URL parameters
- [ ] **ALWAYS** verify token signatures and claims
- [ ] **ALWAYS** implement proper error handling (no info leakage)
- [ ] **CONSIDER** implementing refresh token rotation
- [ ] **CONSIDER** using DPoP or mTLS for sender-constrained tokens

#### 🧪 Testing & Validation
- [ ] Test error conditions (invalid tokens, expired tokens, etc.)
- [ ] Test token storage security (attempt to extract from storage)
- [ ] Test CSRF protections (attempt to forge state parameter)
- [ ] Test redirect URI validation (attempt to use malicious redirect)
- [ ] Test PKCE implementation (attempt authorization code interception)
- [ ] Test token validation (wrong issuer, audience, expired, etc.)
- [ ] Test memory safety (attempt to extract tokens from memory dumps)

#### 🚀 Deployment & Maintenance
- [ ] Monitor for security advisories on OAuth/OIDC libraries
- [ ] Regularly update dependencies to patch known vulnerabilities
- [ ] Implement logging for security-relevant events
- [ ] Plan for key/certificate rotation if using asymmetric crypto
- [ ] Establish process for responding to security vulnerability reports

## Decision Gate: Security Checklist for Auth Plugins

✅ **ACHIEVED**: This document provides a comprehensive security checklist for OAuth plugin development, synthesized from RFC 9700, RFC 6819, and OpenID Connect Core 1.0.

## References

1. **RFC 9700** - OAuth 2.0 Security Best Current Practice (January 2025)
   https://www.rfc-editor.org/rfc/rfc9700.txt

2. **RFC 6819** - OAuth 2.0 Threat Model and Security Considerations (January 2013)
   https://www.rfc-editor.org/rfc/rfc6819.txt

3. **OpenID Connect Core 1.0** (December 2023)
   https://openid.net/specs/openid-connect-core-1_0.html

4. **RFC 7636** - Proof Key for Code Exchange (PKCE) by OAuth Public Clients
   https://www.rfc-editor.org/rfc/rfc7636.txt

5. **RFC 9449** - OAuth 2.0 Demonstrating Proof of Possession (DPoP)
   https://www.rfc-editor.org/rfc/rfc9449.txt

6. **RFC 8705** - OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens
   https://www.rfc-editor.org/rfc/rfc8705.txt

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ GUIDE COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
