# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

# REUSE Waiver — RESCINDED (2026-10-12)

**Original Status:** `WAIVED-FOR-DEBUT` — RED acknowledged, shipment authorized with conditions

**Current Status:** **RESCINDED** — REUSE v3.3 Lint is now GREEN on main (verified 2026-10-12).

**Reason for Rescission:** The waiver documented a RED state that no longer exists. The REUSE compliance gate now passes on a clean clone of main (exit 0, compliant). The waiver's premise ("RED acknowledged") is factually false and violates §0: *Unenforced claims are worse than absent rules; where external research could not verify a norm, this document says so explicitly rather than asserting it.*

**Root Cause of Original RED:** Missing SPDX headers on `src/omega/config_data/**/*.yaml` (packaged runtime configs). Resolved by adding SPDX headers to the 4 runtime YAMLs + default IWAD during the G20 config-path sweep.

**Verification:**
```bash
# Clean clone of main
git clone --branch main https://github.com/Xoe-NovAi/omega-engine /tmp/verify-reuse
cd /tmp/verify-reuse
.venv/bin/python -m reuse lint
# Exit 0, "Your project is compliant with version 3.3 of the REUSE Specification"
```

**Action Taken:** Waiver file retained as historical record with this addendum. No active waiver remains in force.

---

*Rescinded 2026-10-12 by @makali. Original waiver authored 2026-10-03.*
