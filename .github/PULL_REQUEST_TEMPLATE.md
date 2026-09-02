<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Pull Request

## Description

A clear and concise description of what this PR does.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] CI/CD improvement
- [ ] Refactor (no functional change)
- [ ] Security fix

## Related Issues

Closes #(issue number)

## Changes Made

- Change 1
- Change 2
- Change 3

## Testing

Describe how you tested this change:

- [ ] `make test` passes (fast unit tier)
- [ ] `make test-all` passes (integration tier)
- [ ] `make temple-grade` passes (all 11 gates)
- [ ] Manual testing: `omega talk "test prompt"` works
- [ ] Tested with local inference (native-gguf)
- [ ] Tested with cloud fallback (if applicable)

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Sovereign Mandates Compliance

- [ ] M1 AnyIO: No `import asyncio` in `src/omega/`
- [ ] M7 Local-First: Local inference primary, cloud opt-in
- [ ] M8 Zero Telemetry: No external analytics
- [ ] M22 Provenance: Provider identity preserved
- [ ] M23 Failure Integrity: No soft failures

## Screenshots / Logs (if applicable)

```bash
# Paste relevant output
```

## Additional Notes

Any additional information, configuration, or context that reviewers should know.