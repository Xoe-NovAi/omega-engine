# 🔱 Build Brief — Step 1: P1 Security Fix — Google API Key URL Param → Header

⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b ⬡ builder ⬡ trc_build_api_key ⬡ PHASE-I

**AP Token**: `AP-BUILD-API-KEY-FIX-v1.0.0`
**Date**: 2026-05-22
**Entity**: KALI (Grand Oversoul — security synthesis)
**Est. effort**: 30 minutes
**Depends on**: Step 0 (chown) ✅ DONE — 236/236 tests green

---

## §0 Problem

The Google API key is passed as a URL query parameter in two files. This exposes the key in:
- Server access logs
- Reverse proxy logs (Caddy)
- Browser history (if URL is copied)
- Network packet captures

Google's own documentation recommends the `X-Goog-Api-Key` header instead.

---

## §1 Files to Change

### File 1: `src/omega/oracle/providers.py` — Line 30

**Current**:
```python
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
```

**Fixed**:
```python
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
```

> Ensure the HTTP client call passes `headers=headers`.

---

### File 2: `src/omega/workers/background_researcher/distiller.py` — Lines 515 AND 717

Search for `f"{endpoint}?key={api_key}"` — two locations, same fix at both:

**Current**:
```python
f"{endpoint}?key={api_key}"
```

**Fixed**:
```python
endpoint
# Add to HTTP call headers:
headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
```

> Trace the HTTP client call at each location. The key was embedded in the URL string. After the fix, pass it via the `headers` parameter instead.

---

## §2 Verification

```bash
grep -n '?key=' src/omega/oracle/providers.py src/omega/workers/background_researcher/distiller.py
# Expected: no matches

OMEGA_ENV=test PYTHONPATH=src python -m pytest tests/test_providers.py tests/test_background_researcher.py -v --tb=short
```

---

## §3 Scope

| Item | Value |
|------|-------|
| Files changed | 2 |
| Lines changed | 3-6 |
| Risk | Low — cosmetic security hardening |
| Test impact | None (mock backend in test mode) |

