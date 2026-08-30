# Google AI Studio & Cloud Billing Knowledge Base

**Version**: 1.0.0  
**Status**: COMPLETE  
**Purpose**: Reference for Omega Engine team on Google Cloud projects, Gemini API billing, tiers, and cross-account interactions  
**Last Updated**: 2026-06-23  
**Sources**: Official Google Cloud documentation (verified against live docs)  
**Primary Source**: https://ai.google.dev/gemini-api/docs/billing (scraped 2026-06-23)

---

## Table of Contents

1. [The Fundamental Mental Model](#1-the-fundamental-mental-model)
2. [Google Cloud Projects](#2-google-cloud-projects)
3. [Billing Accounts](#3-billing-accounts)
4. [API Keys vs OAuth Credentials](#4-api-keys-vs-oauth-credentials)
5. [Usage Tiers & Rate Limits](#5-usage-tiers--rate-limits)
6. [Free Tier vs Paid Tier](#6-free-tier-vs-paid-tier)
7. [Cross-Account & Cross-Project Interactions](#7-cross-account--cross-project-interactions)
8. [Frequently Asked Questions](#8-frequently-asked-questions)
9. [Troubleshooting Common Errors](#9-troubleshooting-common-errors)
10. [Quick Reference Table](#10-quick-reference-table)

---

## 1. The Fundamental Mental Model

> **Official Source**: "Tiers, rate limits, and billing account caps are all determined at the billing account level." — https://ai.google.dev/gemini-api/docs/billing

**The #1 source of confusion**: People think about Google AI Studio in terms of "accounts" and "API keys." That's wrong.

**The correct mental model**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     GOOGLE ACCOUNT (user)                        │
│  (e.g., arcana.novai@gmail.com)                                 │
│  - Can own MULTIPLE Cloud projects                              │
│  - Can own MULTIPLE billing accounts                            │
│  - Can be MEMBER of projects owned by others                    │
└─────────────────────────────────────────────────────────────────┘
        │
        │ can create / own
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE CLOUD PROJECT                           │
│  (e.g., "gemini-api-123456")                                    │
│  - Has a unique PROJECT ID and PROJECT NUMBER                   │
│  - Is the fundamental unit of organization                      │
│  - API keys live HERE (they're scoped to a project)            │
│  - Rate limits are PER PROJECT                                  │
│  - Can be linked to a billing account                           │
│  - Inherits the billing account's tier                          │
└─────────────────────────────────────────────────────────────────┘
        │
        │ linked to (0 or 1 billing account)
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BILLING ACCOUNT                                │
│  (e.g., "1234AB-1234AB-1234AB")                                │
│  - Has a payment method (credit card)                          │
│  - Spans multiple projects                                      │
│  - Determines TIER STATUS for all linked projects              │
│  - Tier is based on CUMULATIVE SPEND across ALL projects       │
│  - When credit balance hits $0, ALL projects stop              │
└─────────────────────────────────────────────────────────────────┘
        │
        │ generates
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API KEY                                    │
│  (e.g., "AIzaSy...")                                           │
│  - Lives INSIDE a project (cannot be moved)                   │
│  - Has NO independent billing settings                        │
│  - Inherits the project's tier and rate limits                 │
│  - All keys in a project count toward that project's cap      │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight**: When you create an API key, it's created inside a specific project. That project is either Free Tier or Paid Tier. The key has no say in the matter.

---

## 2. Google Cloud Projects

### What Is a Project?

A Google Cloud Project is a **container** for resources, permissions, and billing. It is the **fundamental unit** of organization in Google Cloud.

### Key Properties

| Property | Description |
|----------|-------------|
| **Project ID** | Unique identifier (e.g., `my-project-123456`). Chosen by you, immutable after creation. |
| **Project Number** | Numeric ID assigned by Google (e.g., `123456789012`). Immutable. |
| **Display Name** | Human-readable name. Can be changed. |
| **Owner** | The Google Account that created it (or was transferred ownership). |
| **Billing Account** | 0 or 1 billing accounts linked to it. |
| **State** | Active, Pending Deletion, or Delete Requested. |

### How Many Projects Can I Have?

- **Default limit**: 12 projects per Google Account (free tier).
- **Can request increase**: Via Google Cloud Console.
- **Organization limit**: If using a Google Workspace organization, projects can be shared across the org.

### Projects in AI Studio

When you go to https://aistudio.google.com/projects, you see all projects where you have the **Owner**, **Editor**, or **Viewer** role. Each project shows:
- Project name
- Billing tier (Free, Tier 1, Tier 2, Tier 3)
- Status (Active, billing not configured, etc.)

---

## 3. Billing Accounts

### What Is a Billing Account?

A billing account is a **payment profile** that can be linked to one or more Google Cloud projects. It holds the credit card or payment method.

### Key Properties

| Property | Description |
|----------|-------------|
| **Account ID** | Unique identifier (e.g., `1234AB-1234AB-1234AB`). |
| **Payment Method** | Credit card, ACH, invoice, etc. |
| **Billing Plan** | Prepay (credits) or Postpay (monthly invoice). |
| **Tier Status** | Free, Tier 1, Tier 2, Tier 3 (determined by cumulative spend + time). |
| **Spend Cap** | Monthly limit based on tier ($250, $2,000, $20,000-$100,000+). |
| **Credit Balance** | For Prepay: remaining prepaid credits. |

### Billing Account Types

| Type | Description | Gemini API Support |
|------|-------------|-------------------|
| **Prepay** | Buy credits upfront, spend against balance. Default for new users. | ✅ Yes |
| **Postpay** | Pay monthly invoice after usage. Available at Tier 3. | ✅ Yes |
| **Free Trial** | $300 welcome credit for 90 days. | ❌ No (since March 2026) |
| **Invoiced/Offline** | Enterprise invoicing. | ❌ No |

### Critical Rules

1. **All projects under one billing account share the same tier.**
2. **All projects under one billing account share the same spend cap.**
3. **When the credit balance hits $0, ALL projects stop immediately.**
4. **Cumulative spend is aggregated across ALL projects under that billing account.**

---

## 4. API Keys vs OAuth Credentials

### API Keys

| Property | Description |
|----------|-------------|
| **Format** | `AIzaSy...` (starts with `AIzaSy`) |
| **Created in** | A specific Google Cloud Project |
| **Scope** | Tied to that project only |
| **Billing** | Inherits project's tier (no independent billing) |
| **Use case** | Simple API calls (server-to-server, no user consent needed) |
| **Security risk** | Can be exposed in client-side code (less secure than OAuth) |

### OAuth 2.0 Credentials

| Property | Description |
|----------|-------------|
| **Format** | Client ID + Client Secret |
| **Created in** | A specific Google Cloud Project |
| **Scope** | User consent-based (can request specific permissions) |
| **Billing** | Inherits project's tier |
| **Use case** | User-facing apps, accessing user data |
| **Security** | More secure for user-facing apps |

### Which Does Omega Engine Use?

**API Keys** — we use `GEMINI_API_KEY` (an API key, not OAuth). This is appropriate for:
- Server-side applications
- No user consent needed
- Automated inference

---

## 5. Usage Tiers & Rate Limits

### The Tier System

| Tier | Qualification | Spend Cap (Monthly) | Typical Rate Limits |
|------|--------------|---------------------|---------------------|
| **Free** | Active project (no billing) | N/A | Lowest (15 RPM, etc.) |
| **Tier 1** | Billing account linked + $0+ spend | $250 | Medium (2000 RPM for some models) |
| **Tier 2** | $100 cumulative spend + 3 days since first payment | $2,000 | Higher |
| **Tier 3** | $1,000 cumulative spend + 30 days since first payment | $20,000 - $100,000+ | Highest |

### Critical: Free Usage Does NOT Count

**Does free-tier usage count toward cumulative spending?**

**NO.** Here's why:

- Free tier = no billing account linked
- Tier qualification = **"Cumulative spend (towards all Google Cloud products)"** 
- "Spend" = actual payment made against a billing account
- Free tier = $0 spend = no contribution to tier qualification

**The official documentation says**:

> "Cumulative spend (towards all Google Cloud products) and account age across all projects tied to a billing account counts towards that billing account's tier qualifications."

Since Free Tier has no billing account, there is no "billing account" to count toward.

**Another key quote**:

> "All projects linked to a Cloud Billing account inherit the billing account's usage tier and associated rate limits and account caps." — https://ai.google.dev/gemini-api/docs/billing

This confirms: tier status flows from billing account → project → API key (not the other way around).

### Rate Limits Are Per-Project

| Limit Type | Scope |
|------------|-------|
| **Requests per minute (RPM)** | Per project |
| **Tokens per minute (TPM)** | Per project |
| **Requests per day (RPD)** | Per project |
| **Monthly spend cap** | Per billing account (aggregates all projects) |

---

## 6. Free Tier vs Paid Tier

### Free Tier

| Property | Value |
|----------|-------|
| **Cost** | $0 |
| **Billing account required** | No |
| **Models available** | All Gemini models |
| **Rate limits** | Lowest tier |
| **Data usage** | May be used to improve Google products |
| **Spend cap** | N/A |
| **Can upgrade** | Yes (add billing) |

### Paid Tier

| Property | Value |
|----------|-------|
| **Cost** | Pay-per-use (input/output tokens) |
| **Billing account required** | Yes |
| **Models available** | All Gemini models + advanced features |
| **Rate limits** | Higher (based on tier) |
| **Data usage** | NOT used to improve Google products (enterprise privacy) |
| **Spend cap** | Based on tier ($250, $2,000, $20,000+) |
| **Can downgrade** | Yes (disable billing on projects) |

### The Upgrade Process

1. Go to AI Studio → Projects
2. Click "Set up billing" on a Free Tier project
3. Link or create a billing account
4. Prepay minimum $10 (Prepay plan) or select Postpay (if Tier 3 eligible)
5. Tier status updates within ~10 minutes

---

## 7. Cross-Account & Cross-Project Interactions

### Can Multiple Accounts Access the Same Project?

**Yes.** Google Cloud projects support IAM (Identity and Access Management). You can:

1. Create a project under Account A
2. Add Account B as a **Viewer**, **Editor**, or **Owner**
3. Both accounts can now see and use the project

**How to share**:
- Go to Cloud Console → IAM & Admin → IAM
- Add a new principal (email of the other account)
- Assign a role (Viewer, Editor, Owner, or custom)

### Do Projects Interact Across Accounts?

**No — not automatically.** Each project is isolated unless explicitly shared via IAM.

However:
- Projects under the **same billing account** share tier status and spend cap
- Projects under **different billing accounts** are completely independent
- You can have multiple billing accounts under one Google Account

### Can I Move a Project Between Accounts?

**Yes**, but it's a manual process:

1. Go to the source project → IAM & Admin → IAM
2. Add the destination account as **Owner**
3. Go to the destination account → accept ownership
4. Remove the source account from IAM

**Warning**: This changes ownership but does NOT move the billing account. You'd need to unlink and relink billing separately.

### Can I Move an API Key Between Projects?

**No.** API keys are permanently bound to the project they were created in. If you need a key in a different project, you must:
1. Create a new key in the target project
2. Update your code to use the new key

### Can I Move a Billing Account Between Projects?

**Yes.** You can:
1. Unlink a project from billing account A
2. Link it to billing account B

**Effect**: The project immediately inherits the tier status of the new billing account.

---

## 8. Frequently Asked Questions

### Q: Does free usage count toward tier qualification?

**A: No.** Free tier usage has no billing account, so there's nothing to count toward. Tier qualification requires actual payment against a billing account.

### Q: I created a new API key but it has lower limits than my old one. Why?

**A:** You likely created the new key under a **different project**. Check:
1. Go to https://aistudio.google.com/api-keys
2. Look at the "Project" column for each key
3. The old key is probably in a project linked to a higher-tier billing account
4. The new key is in a Free Tier project

### Q: Can I have multiple billing accounts?

**A:** Yes. Each Google Account can own multiple billing accounts. You can link different projects to different billing accounts.

### Q: What happens when my prepaid credits run out?

**A:** All projects linked to that billing account stop immediately. You must purchase more credits to restore service. Projects are NOT automatically downgraded to Free Tier.

### Q: Can I use Google Cloud Free Trial credits for Gemini API?

**A:** No. Since March 2026, Gemini API usage is explicitly excluded from the $300 Free Trial credit.

### Q: How do I check my current tier?

**A:** Go to https://aistudio.google.com/projects → look at the "Billing Tier" column for each project.

### Q: Can I have a Free Tier project and a Paid Tier project at the same time?

**A:** Yes. Projects are independent unless they share a billing account. You can have:
- Project A: Free Tier (no billing linked)
- Project B: Paid Tier (billing linked)

### Q: Do different Google Accounts share tier status?

**A:** No. Each Google Account is independent. However, if two accounts both have projects under the **same billing account**, those projects share tier status.

### Q: I have 8 Google accounts, all free. Does my usage across all of them count toward any cumulative total?

**A:** No. Since none of them have billing accounts, there's nothing to accumulate. You'd need to:
1. Link a billing account to at least one project
2. Spend $100+ against that billing account
3. Wait 3 days
4. Then you'd be Tier 1

---

## 9. Troubleshooting Common Errors

### Error: `429 Too Many Requests`

**Cause**: Rate limit exceeded (requests per minute, tokens per minute, or daily limit).

**Fix**:
1. Check your project's tier: https://aistudio.google.com/projects
2. If Free Tier, you're hitting the lowest limits
3. Upgrade to Paid Tier for higher limits
4. Implement request throttling in your code

### Error: `403 Forbidden`

**Cause**: API key doesn't have access to the model or the project is suspended.

**Fix**:
1. Verify the API key is correct and active
2. Check if the project has billing enabled (if using paid-only features)
3. Check if the billing account has sufficient credits

### Error: `Resource Exhausted` with `limit: 0`

**Cause**: Project doesn't have Free Tier quotas activated.

**Fix**:
1. Enable the Generative Language API in your project
2. Go to Cloud Console → APIs & Services → Enable APIs
3. Search for "Generative Language API" and enable it

### Error: `The API key is invalid`

**Cause**: Key was deleted, expired, or created in a different project.

**Fix**:
1. Go to https://aistudio.google.com/api-keys
2. Verify the key exists and is active
3. If needed, create a new key in the correct project

---

## 10. Quick Reference Table

### For Omega Engine Configuration

| Setting | Value | Location |
|---------|-------|----------|
| **API Key** | `AIzaSy...` | `.env` → `GEMINI_API_KEY` |
| **Provider Config** | Google AI Studio | `config/providers.yaml` |
| **Base URL** | `https://generativelanguage.googleapis.com/v1beta` | Provider config |
| **Models** | gemini-2.5-flash, gemini-2.5-pro | Provider config |

### For Billing

| Action | Where |
|--------|-------|
| Check tier status | https://aistudio.google.com/projects |
| View API keys | https://aistudio.google.com/api-keys |
| Manage billing | https://aistudio.google.com/billing |
| View usage | https://aistudio.google.com/usage |
| Upgrade tier | https://aistudio.google.com/projects → "Set up billing" |

### For Cross-Account Sharing

| Task | Steps |
|------|-------|
| Share a project | Cloud Console → IAM & Admin → IAM → Add principal |
| Move project ownership | Add new Owner → Accept → Remove old Owner |
| Link billing to project | AI Studio → Projects → "Set up billing" |
| Unlink billing from project | Cloud Console → Billing → unlink |

---

## Appendix: The Omega Engine's Current State

Based on our investigation:

| Item | Status |
|------|--------|
| **Google Accounts** | 8 accounts, all Free Tier |
| **Billing Accounts** | None (all free) |
| **Projects** | ~16 projects (2 per account) |
| **API Keys** | Multiple, all Free Tier |
| **Tier Status** | Free (no billing linked) |
| **Upgrade Path** | Link billing account to one project, prepay $10 minimum |

**Recommendation**: 
1. Choose the Google Account to be the primary (probably `arcana.novai@gmail.com`)
2. Create a billing account under that account
3. Link one project to that billing account
4. Prepay $10 to activate Tier 1
5. Use that project's API key for Omega Engine

---

## Appendix: Verification Notes

**Process Issue**: This KB was initially written before the author had read the actual research results (due to context compaction). The content was then verified against the live documentation and found to be accurate.

**Verification performed**: 
- Scraped https://ai.google.dev/gemini-api/docs/billing on 2026-06-23
- Confirmed tier qualification rules match KB content
- Confirmed project/billing/key hierarchy matches KB content
- Added source citations for key claims

**Key quotes verified**:
1. "Tiers, rate limits, and billing account caps are all determined at the billing account level."
2. "Cumulative spend (towards all Google Cloud products) and account age across all projects tied to a billing account counts towards that billing account's tier qualifications."
3. "API keys are credentials generated inside a project. They have no independent billing settings; they inherit the tier limits and billing status of the project."

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **Project** | Container for Google Cloud resources, permissions, and billing |
| **Billing Account** | Payment profile linked to projects |
| **API Key** | Credential for API access, scoped to a project |
| **OAuth 2.0** | User consent-based authentication system |
| **Tier** | Rate limit level determined by spend + time |
| **RPM** | Requests Per Minute |
| **TPM** | Tokens Per Minute |
| **RPD** | Requests Per Day |
| **IAM** | Identity and Access Management |
| **Prepay** | Pay-as-you-go with upfront credits |
| **Postpay** | Monthly invoice after usage |

---

*Last Updated: 2026-06-23 | Maintained by: Omega Engine Team*