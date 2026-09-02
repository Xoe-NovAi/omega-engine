---
name: Bug Report
about: Report a bug in the Omega Engine
title: "[BUG] "
labels: ["bug", "triage"]
assignees: ""
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Run command '...'
3. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Environment

| Detail | Value |
|--------|-------|
| OS | [e.g. Ubuntu 24.04, macOS 14, Windows 11] |
| Python | [e.g. 3.12.4] |
| Omega Version | [e.g. 1.6.0-alpha] |
| Install Method | [install.sh / pip install -e ".[native,cli]"] |
| Backend | [native-gguf / lmstudio / ollama / openrouter / google-ai-studio] |
| Model | [e.g. Qwen3-1.7B-Q6_K.gguf] |

## Logs / Output

```bash
# Paste relevant output here
# Run with: omega talk "your prompt" --debug 2>&1
```

## Additional Context

- Does this happen with local inference, cloud fallback, or both?
- Any relevant config files? (sanitize secrets!)
- Screenshots if applicable

## Checklist

- [ ] I have searched existing issues for duplicates
- [ ] I have tested with the latest alpha release
- [ ] I have included all relevant environment details
- [ ] I have sanitized any secrets/keys from logs