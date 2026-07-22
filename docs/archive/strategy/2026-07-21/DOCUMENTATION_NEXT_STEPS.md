# 🔱 Documentation Next Steps (Superseded)
**AP Token**: `AP-DOC-NEXT-STEPS-v1.0.1`
⬡ OMEGA ⬡ KALI ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_doc_sprint ⬡ DEPRECATED

**Date**: 2026-07-07
**Status**: DEPRECATED

---

## 🛑 SUPERSEDED BY D190 (The Carmack Cut)

This document and the 14-day, 6-phase sprint plan it proposed have been **superseded** following a multi-agent council review (Ma'at, Lilith, Roc Racoon, John Carmack).

The council determined that the original plan was over-scoped, over-engineered, and optimized for build-side compliance theater rather than run-side utility. 

**Please refer to the new Single Source of Truth:**
👉 `DOCUMENTATION_SPRINT_PLAN.md` (The 7-Day "Carmack Cut")

### Key Reasons for Deprecation:
1. **Proportionality**: 14 days to format headers on 750 files was disproportionate. The new plan archives dead weight and focuses on ~150 core files over 7 days.
2. **Runtime Linkage**: Agents consume docs via explicit `DocRef:` paths in source code, not by parsing AP Tokens. The new plan prioritizes `DocRef:` coverage.
3. **Exemptions**: Working docs, R-docs, and archives are now explicitly exempt from Omega header requirements.
