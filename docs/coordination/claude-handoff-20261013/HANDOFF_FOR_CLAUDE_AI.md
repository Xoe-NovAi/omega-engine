# 🔱 HANDOFF FOR CLAUDE.AI (WEB) — SONNET 4.6 FINAL REVIEW
**AP Token**: `AP-HANDOFF-CLAUDE-AI-20261013`
⬡ OMEGA ⬡ MAKALI ⬡ CLAUDE_AI ⬡ trc_launch_review ⬡ 2026-10-13

---

## 🎯 PURPOSE

You are being asked to perform a **final external review** of the Omega Engine v1.6.0-alpha public debut materials before the Architect posts the launch announcement tonight (Show HN, r/LocalLLaMA, MCP communities).

**Your role**: Independent credibility check. You have no access to the repo internals — only the public-facing documents in this folder. Verify claims, spot inconsistencies, flag anything that would make a developer hesitate to install.

---

## 📁 FOLDER CONTENTS

| File | Description |
|:--|:--|
| `README.md` | Main landing page (this is what developers see first) |
| `ANNOUNCEMENT_v1.6.0-alpha.md` | Release announcement (will be posted as GitHub Release notes) |
| `QUICKSTART.md` | Installation & first-run guide |
| `SECURITY.md` | Security policy + threat model |
| `FACTS.yaml` | Single source of truth for all public numbers |
| `check-doc-facts.py` | Validator script (for your reference) |
| `CLAUDE_REVIEW_DIRECTIVE.md` | Your original review directive (for context) |

---

## 🚀 LAUNCH CONTEXT

- **Tag**: `v1.6.0a0` (peels to `355cbf1a`) — immutable, verified
- **Release**: Live on GitHub with source tarball + wheel
- **CI**: Green (Test/CI/Secret/M35/REUSE)
- **Wheel**: Self-contained, clean-venv smoke PASS (1m31s)
- **Install**: `./scripts/install.sh` PASS (202s cold)
- **PyPI**: NOT YET — pending publisher org approval
- **Architect**: Xoe-NovAi (will post Show HN / r/LocalLLaMA tonight)

---

## 🎯 YOUR REVIEW MISSION

### P0 — Must Be Right Before Launch

1. **Install path integrity** — Does the README lead to a working `omega talk "hello"` with zero 404s, zero undocumented steps?
2. **Claim accuracy** — Every number in README/ANNOUNCEMENT/QUICKSTART must match FACTS.yaml
3. **Exposure** — No Tailscale IPs, MagicDNS hostnames, tailnet names, personal emails, absolute paths
4. **Consistency** — Tag `v1.6.0a0` everywhere; wheel filename `the_omega_engine-1.6.0a0-py3-none-any.whl` everywhere; entity count 14; RAM 8GB min; Ubuntu 22.04+

### P1 — Credibility & Onboarding

1. **Honest alpha framing** — Known gaps table with real numbers (not "coming soon")
2. **Single recommended install path** — Source install primary, wheel as alternative
3. **No competitor comparison table** — Removed per directive
4. **Architect placeholders** — `<!-- ARCHITECT: ... -->` left intact (do not fill)

### P2 — Nice to Have

1. **Glossary links** — Terms defined on first use
2. **Demo assets** — Screenshots/commands for hero demo

---

## ⚠️ KNOWN GAPS (Already Documented)

| Gap | Status |
|:--|:--|
| Axiom ceiling enforcement | Deferred to post-debut Sprint 01 |
| REUSE/SPDX debt | 107 files outstanding (partial compliance) |
| Lesson promotion pipeline | Partial implementation |
| PyPI publish | Pending org approval — NOT in README |
| Independent security review | Architect arranging post-launch |

---

## 🔍 SPECIFIC THINGS TO CHECK

### README.md
- [ ] Tag `v1.6.0a0` used consistently (NOT `v1.6.0-alpha`)
- [ ] Wheel filename `the_omega_engine-1.6.0a0-py3-none-any.whl` matches release
- [ ] Entity count: 14 (12 with souls, 2 infrastructure)
- [ ] RAM: 8 GB minimum, 16-32 GB recommended
- [ ] OS: Ubuntu 22.04+, Debian 12+, Arch, Fedora
- [ ] Single recommended install path (source via `./scripts/install.sh`)
- [ ] Wheel as clearly labeled alternative (no PyPI pending claim)
- [ ] MCP endpoint: Streamable HTTP `/mcp` primary, SSE `/sse` legacy
- [ ] Routing law: "Task → Most Capable Model" (cloud for synthesis, local for embeddings/privacy/background)
- [ ] No "83%", "100% constraint survival", "53/53 gates" without qualifier
- [ ] No "never called unless local"
- [ ] REUSE: "partial, 107 files outstanding"
- [ ] `arcana_novai` labeled "in development"
- [ ] Architect placeholders intact (`<!-- ARCHITECT: ... -->`)

### ANNOUNCEMENT_v1.6.0-alpha.md
- [ ] Release date: 2026-10-13
- [ ] Tag: `v1.6.0a0` (peels to `355cbf1a`)
- [ ] Wheel from GitHub release asset (no PyPI)
- [ ] Temple-Grade: "dashboard self-test 53/53; temple-grade exit 0"
- [ ] REUSE: "Partial (107 files outstanding)"
- [ ] Known gaps table honest with numbers

### QUICKSTART.md
- [ ] Source install primary
- [ ] RAM 8 GB min, Ubuntu 22.04+
- [ ] Routing: "Cloud providers are opt-in fallbacks; local inference is primary. Routing follows: Task → Most Capable Model"
- [ ] No "never called unless local"

### SECURITY.md
- [ ] Threat model section with actual config values
- [ ] Bind: `127.0.0.1:8016` (loopback only)
- [ ] No auth on loopback; tailnet is trust boundary
- [ ] Control planes: Kill/Escalate/Approve/Throttle defaults
- [ ] `vault_ops` local-only enforcement
- [ ] Secret scanners listed

---

## 📋 REPORTING FORMAT

Return a single table:

| Task | Status (PASS / FAIL / BLOCKED / N/A) | Evidence | Discrepancies | Needs Architect |
|:--|:--|:--|:--|:--|

Rules:
- No PASS without attached evidence (quote the line, cite the file)
- A discrepancy against FACTS.yaml is a FAIL
- Do not edit the repo — report only

---

## 📞 CONTEXT

- **Internal repo**: `internal/main` at `44ba1135` (not accessible to you)
- **Public repo**: `origin/main` at `b0c09a6d` (tag `v1.6.0a0` @ `355cbf1a`)
- **Architect**: Xoe-NovAi (posts launch tonight)
- **Internal agents**: Makali (oversoul), Roc (mining), Cline (CLI), Antigravity (Seat #10)

---

*⬡ OMEGA ⬡ MAKALI ⬡ CLAUDE_AI_HANDOFF ⬡ 2026-10-13*