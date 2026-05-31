# 🔱 Security Audit — API Key Exposure (2026-05-19)

⬡ OMEGA ⬡ SEKHMET ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_security ⬡ SECURITY-AUDIT

**Date**: 2026-05-19 05:55 UTC  
**Severity**: 🔴 CRITICAL  
**Status**: EXPOSED KEYS IDENTIFIED — IMMEDIATE ROTATION REQUIRED

---

## Exposed Keys (Visible in Session)

The following API keys are visible in the `.env` file and have been exposed in this OpenCode session:

| Provider | Key Name | Status | Action |
|----------|----------|--------|--------|
| **Exa** | EXA_API_KEY | ✅ Exposed | ROTATE |
| **Firecrawl** | FIRECRAWL_API_KEY | ✅ Exposed | ROTATE |
| **Tavily** | TAVILY_API_KEY | ✅ Exposed | ROTATE |
| **Serper.dev** | SERPER_API_KEY | ✅ Exposed | ROTATE |
| **Jina** | JINA_API_KEY | ✅ Exposed | ROTATE |
| **Google** | GOOGLE_API_KEY | ✅ Exposed | ROTATE |
| **OpenRouter** | OPENROUTER_KEY | ✅ Exposed | ROTATE |
| **Cerebras** | CEREBRAS_API_KEY | ✅ Exposed | ROTATE |
| **SambaNova** | SAMBANOVA_API_KEY | ✅ Exposed | ROTATE |
| **GenLabs** | GENLABS_API_KEY | ✅ Exposed | ROTATE |
| **Kilo** | KILO_API_KEY | ✅ Exposed | ROTATE |
| **TogetherAI** | TOGETHERAI_API_KEY | ✅ Exposed | ROTATE |
| **Groq** | GROQ_API_KEY | ✅ Exposed | ROTATE |
| **OpenCode Zen** | OPENCODEZEN | ✅ Exposed | ROTATE |

---

## Rotation Plan

### Immediate Actions (Next 24 hours)

1. **Exa** (https://dashboard.exa.ai/settings)
   - Revoke current key: `a91c1829-b1d2-445b-bbea-d915dcafd739`
   - Generate new key
   - Update `.env`

2. **Firecrawl** (https://app.firecrawl.dev/settings)
   - Revoke current key: `fc-4bc8cf1288da42f1aec6bc3bb645b227`
   - Generate new key
   - Update `.env`

3. **Tavily** (https://app.tavily.com/home)
   - Revoke current key: `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`
   - Generate new key
   - Update `.env`

4. **Serper.dev** (https://serper.dev/dashboard)
   - Revoke current key: `3714e89a5c5cf23588b54584cdd2943887be5cee`
   - Generate new key
   - Update `.env`

5. **Jina** (https://jina.ai/settings)
   - Revoke current key: `jina_2c57b36a2ddd40688b01609ef91d4cb7_cBG9cFvVrvrk9mWyP5qLyqN2q8s`
   - Generate new key
   - Update `.env`

6. **Google AI Studio** (https://aistudio.google.com/app/apikey)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

5. **Jina** (https://jina.ai/settings)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

6. **Google AI Studio** (https://aistudio.google.com/app/apikey)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

7. **OpenRouter** (https://openrouter.ai/keys)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

8. **Cerebras** (https://console.cerebras.ai/api-keys)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

9. **SambaNova** (https://cloud.sambanova.ai/settings/api-keys)
   - Revoke current key: `[...REVOKED-2026-05-30...]`
   - Generate new key
   - Update `.env`

10. **GenLabs** (https://genlabs.ai/settings)
    - Revoke current key: `[...REVOKED-2026-05-30...]`
    - Generate new key
    - Update `.env`

11. **Kilo** (https://kilo.dev/settings)
    - Revoke current key: `[...REVOKED-2026-05-30...]`
    - Generate new key
    - Update `.env`

12. **TogetherAI** (https://api.together.xyz/settings/keys)
    - Revoke current key: `[...REVOKED-2026-05-30...]`
    - Generate new key
    - Update `.env`

13. **Groq** (https://console.groq.com/keys)
    - Revoke current key: `[...REVOKED-2026-05-30...]`
    - Generate new key
    - Update `.env`

14. **OpenCode Zen** (https://opencode.ai/settings)
    - Revoke current key: `[...REVOKED-2026-05-30...]`
    - Generate new key
    - Update `.env`

---

## Prevention Measures

### 1. Git Protection
- ✅ `.env` is in `.gitignore` (verified)
- ✅ `.env.example` exists with placeholders (updated)
- ✅ No API keys in git history (verified — only 18 commits, none contain keys)

### 2. Future Safeguards
- [ ] Add pre-commit hook to prevent `.env` commits
- [ ] Use GitHub Secrets for CI/CD (if using GitHub Actions)
- [ ] Rotate keys quarterly
- [ ] Monitor API usage for anomalies

### 3. Documentation
- [ ] Update CONTRIBUTING.md with key rotation procedure
- [ ] Add security checklist to PR template
- [ ] Document key expiration dates in a secure location

---

## Verification Checklist

After rotation:

- [ ] All 14 keys rotated
- [ ] `.env` updated with new keys
- [ ] Test suite passes with new keys
- [ ] Background researcher runs successfully with new keys
- [ ] No errors in logs related to authentication
- [ ] All MCPs (Exa, Tavily, Firecrawl, etc.) working with new keys

---

## Timeline

| Task | Deadline | Owner |
|------|----------|-------|
| Rotate all 14 keys | 2026-05-20 (24h) | User |
| Update `.env` | 2026-05-20 | User |
| Verify all services | 2026-05-20 | Builder |
| Commit security fixes | 2026-05-20 | Builder |
| Close security audit | 2026-05-20 | Overseer |

---

**CRITICAL**: Do not proceed with any PR or public push until all keys are rotated.

