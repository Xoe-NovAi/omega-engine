# 🔱 Community Engagement & Maintainer Trust Guide
**AP Token**: `AP-COMMUNITY-ENGAGEMENT-GUIDE-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_community_engagement ⬡ 2026-07-25

<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Xoe-NovAi Foundation -->

---

## Executive Summary

This guide provides a comprehensive framework for building trust with maintainers and contributors, synthesized from KG-5 research findings. The maintainer is the interface — every interaction shapes the project's culture more powerfully than any governance document.

**Purpose**: Establish sustainable community engagement practices that build long-term trust.

**Scope**: Applies to all community interactions across the Omega Engine ecosystem.

---

## 🎯 Core Principle: The Maintainer as Interface

**Rule**: Every interaction with a contributor shapes their perception of the project.

**Why**: A same-day human reply makes a newcomer ~15% more likely to ever contribute again. The first human response matters more than the speed of the merge.

---

## 🤝 Building Trust as a Contributor

### First Interaction Checklist

- [ ] **Read CONTRIBUTING.md** — Thoroughly review before opening issues/PRs
- [ ] **Search Existing Issues** — Show you did your homework
- [ ] **Start Small** — Begin with docs, typos, or clear bugs
- [ ] **Follow PR Template** — Every field filled shows respect for reviewer time
- [ ] **Respond Quickly** — Within 24 hours to feedback
- [ ] **Acknowledge Every Comment** — Agree, explain, or push back
- [ ] **Say Thank You** — It costs nothing and builds goodwill

### Long-Term Contribution Strategy

| Phase | Actions | Timeline |
|-------|---------|----------|
| **Observer** | Read issues, understand culture, learn conventions | 1-2 weeks |
| **First PR** | Small fix following all conventions | Week 2-3 |
| **Regular** | Consistent contributions, respond to feedback | Months 1-3 |
| **Trusted** | Review others' PRs, help triage issues | Months 3-6 |
| **Maintainer** | Invited to maintainer team, given commit access | 6-12 months |

---

## 🏗️ Building Trust as a Maintainer

### The 30-Second Impression

The newcomer doesn't read CONTRIBUTING.md to decide if the project is welcoming. They read the maintainer's tone in a single interaction. One dismissive response can lose a contributor permanently.

### Trust-Building Practices

| Principle | Implementation |
|-----------|----------------|
| **Assume Good Faith** | Default assumption: contributor is trying to help, not wasting time |
| **Graceful Degradation** | Handle imperfect PRs like well-designed API handles unexpected input |
| **Predictability** | Consistent response times and clear expectations beat sporadic excellence |
| **Distribute the Interface** | Co-maintainers as load balancers — don't be the single point of failure |
| **Repair is Powerful** | A bad day followed by "I was terse yesterday, sorry" teaches accountability |

### Response Time Targets

| Interaction | Target | Maximum |
|-------------|--------|---------|
| **First Response** | Same day | 48 hours |
| **Code Review** | 2-3 days | 1 week |
| **Merge Decision** | 1 week | 2 weeks |
| **Security Issue** | 24 hours | 48 hours |

---

## 🚨 The AI Slop Crisis (2026)

AI-generated code has created new community engagement challenges:

| Project | Response |
|---------|----------|
| **Ghostty** | Disclosure required, human must understand every line, bad-faith blocklisted |
| **tldraw** | Paused all external contributions entirely |
| **GitHub** | Building volume controls for PR spam |

### What This Means for Contributors

1. **AI Disclosure is Mandatory** — All AI-generated code must be disclosed
2. **Human Understanding Required** — You must understand every line you submit
3. **Quality Over Quantity** — One good PR beats ten AI-generated slop PRs
4. **Build Trust First** — Start with human-written contributions before using AI

### What This Means for Maintainers

1. **Volume Controls** — Implement PR rate limiting
2. **Disclosure Checks** — Require AI disclosure in PR template
3. **Human Review** — All AI-generated code must be reviewed by human
4. **Quality Gates** — Automated checks for AI slop patterns

---

## 📊 Metrics & Monitoring

### Track These Metrics

| Metric | Target | Alert If |
|--------|--------|----------|
| **First Response Time** | <24 hours | >48 hours |
| **PR Review Time** | <3 days | >1 week |
| **Merge Time** | <1 week | >2 weeks |
| **Contributor Retention** | >50% | <30% |
| **AI Disclosure Rate** | 100% | <90% |

### Monitoring Commands

```bash
# Check PR response times
gh pr list --json createdAt,reviewDecision --jq '.[] | select(.reviewDecision == null) | .createdAt'

# Check contributor retention
gh pr list --author="@me" --state=merged --json author --jq '.[].author.login' | sort | uniq -c

# Check AI disclosure rate
gh pr list --json body --jq '.[].body | select(. | contains("AI-generated"))' | wc -l
```

---

## 🛠️ Implementation Checklist

### For Maintainers

- [ ] **Set Response Time Targets** — Document and enforce
- [ ] **Create Good First Issues** — Label beginner-friendly issues
- [ ] **Implement AI Disclosure** — Add to PR template
- [ ] **Distribute Interface** — Add co-maintainers
- [ ] **Monitor Metrics** — Track response times and retention

### For Contributors

- [ ] **Read CONTRIBUTING.md** — Before first interaction
- [ ] **Start Small** — Build trust with small contributions
- [ ] **Respond Quickly** — Within 24 hours to feedback
- [ ] **Disclose AI Usage** — In PR descriptions
- [ ] **Build Relationships** — With maintainers and other contributors

---

## 🚨 Emergency Procedures

### Contributor Conflict

1. **Immediate**: De-escalate — assume good faith
2. **Assess**: Determine root cause
3. **Mediate**: Facilitate constructive discussion
4. **Resolve**: Find mutually acceptable solution
5. **Document**: Record resolution for future reference

### Maintainer Burnout

1. **Recognize**: Signs of burnout (delayed responses, terse comments)
2. **Support**: Offer to share load
3. **Distribute**: Add co-maintainers
4. **Reduce**: Simplify maintenance burden
5. **Recover**: Allow time off, rotate responsibilities

### AI Slop Attack

1. **Immediate**: Rate limit PRs from new contributors
2. **Assess**: Determine scope of attack
3. **Block**: Bad-faith contributors
4. **Review**: All recent PRs for AI slop
5. **Update**: Improve detection and prevention

---

## Decision Gate: Community Engagement Compliance

✅ **ACHIEVED**: This guide provides comprehensive community engagement strategy, synthesized from KG-5 research findings.

**Next Steps**:
1. Apply this guide to Omega Engine community
2. Set up response time monitoring
3. Implement AI disclosure in PR template
4. Create good first issues for new contributors

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_community_engagement ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
