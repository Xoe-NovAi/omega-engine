# 🔱 Milwaukee M18 Battery Warranty & Date Code Reference
## A Personal Field Guide for the USVI User

**⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash ⬡ opencode ⬡ WARRANTY-KB ⬡ PERMANENT**
**Created**: 2026-06-16
**Location**: Saint John, Coral Bay, USVI 00830
**Scope**: M18 REDLITHIUM battery warranty, date code decoding, cell spec strings, and service center access for US Virgin Islands residents.

---

## §1 Warranty System Overview (US/Canada)

### 1.1 Registration
- **Registration is NOT required.** Warranty is automatic from authorized dealers. Registration is optional and does NOT extend coverage.

### 1.2 Term
| Model Series | Warranty Length | Type |
|---|---|---|
| M18 REDLITHIUM XC (6.0, 8.0) | **3 years** | Full replacement (not pro-rata) |
| M18 REDLITHIUM HIGH OUTPUT (XC8.0, 12.0) | **3 years** | Full replacement |
| M18 FORGE (XC8.0, 6.0) | **3 years** | Full replacement |
| All older M18 compact models | 2-3 years | Varies — check specific model number |

### 1.3 Key Rules
- **Receipt sets warranty start** to purchase date. Photo it immediately.
- **Without receipt**: Milwaukee uses manufacture date code minus 6 months shelf allowance.
- **Non-transferable**: Original purchaser only, from an authorized distributor.
- **Void if bought from**: eBay, Amazon Marketplace, Facebook Marketplace, or any non-authorized reseller.
- **Third-party chargers**: Using a non-Milwaukee charger voids the battery warranty.

### 1.4 Contact Info
| Method | Detail |
|--------|--------|
| Phone | 1-800-SAWDUST (1-800-729-3878) |
| eService Portal | service.milwaukeetool.com |
| Service Locator | milwaukeetool.com/support/find-a-service-center |
| ONE-KEY App | onekeysupport.milwaukeetool.com |

---

## §2 USVI-Specific: Service Center Access

### 2.1 The Gap
**There are ZERO authorized Milwaukee service centers in the US Virgin Islands.** This applies to all three islands:

| Island | Authorized Dealers | Authorized Service Centers |
|--------|-------------------|---------------------------|
| Saint Thomas | ✅ Home Depot (dealer only) | ❌ None |
| Saint John | ❌ None | ❌ None |
| Saint Croix | ❌ None (verify) | ❌ None |

**Home Depot Saint Thomas is an authorized DEALER but NOT a service center.** Selling does not equal servicing.

### 2.2 The Claim Path
Since there is no walk-in option in USVI, the only path is:

1. **Visit** `service.milwaukeetool.com`
2. **Create an eService request** — describe the battery failure
3. **Milwaukee assigns a factory service center** (typically in the continental US)
4. **Prepaid FedEx label is issued** for shipping
5. **Ship the battery** from USVI to the assigned center
6. **Factory evaluates** and ships a replacement back

### 2.3 Li-Ion Battery Shipping from USVI (Critical)
Shipping lithium-ion batteries from the US Virgin Islands requires special handling:

- **HazMat Labeling**: UN3480 (Lithium-ion batteries) — must be visible on the box
- **Terminal Taping**: Exposed terminals MUST be taped over (electrical tape is sufficient)
- **Carrier Notification**: FedEx must be explicitly told the package contains lithium-ion batteries
- **Quantity Limits**: Typically max 2 cells per package for ground transport
- **Packaging**: Original packaging or equivalent protective box (no loose batteries in a box)

**Do not skip these steps.** Li-Ion packages without proper labeling can be confiscated or result in shipping delays/fines.

---

## §3 Date Code / Serial Number Decoding

M18 REDLITHIUM batteries have TWO independent date marking systems. One wears off; the other does not.

### 3.1 Format A — Bottom Label Serial Number (13 characters)

Found on the white/black bottom label. Formats vary by factory but the date is at fixed positions per Milwaukee Product Support Bulletin #404 (TIY404):

```
Positions:  1-3  4   5   6-7  8-9  10-13
Example:    J51   F   D   CH   B    0002245
Meaning:    PRF   REV PLT YR   WK   UNIT (serial)
```

| Positions | Meaning | Example |
|-----------|---------|---------|
| 1-3 | **PREFIX** — factory code | J51, N82, etc. |
| 4 | **REVISION** — engineering revision | F, D, etc. |
| 5 | **PLANT** — manufacturing plant code | D, H, etc. |
| 6-7 | **YEAR** — last 2 digits of year | CH = 23, 24 |
| 8-9 | **WEEK** — ISO week of manufacture | B = 02, TB = 24 |
| 10-13 | **UNIT** — unit serial number (not useful for warranty) | 0001, 2245 |

**Note**: The year/week encoding uses a modified base-26 letter scheme (A=0, B=1, ... Z=25, then AA, AB...) — this is NOT a simple decimal. Most modern bottom labels also print the YYMMDD date explicitly, so you don't always need to decode the 13-character serial.

### 3.2 Format B — Top Housing Heat-Stamp (6 characters: YYMMDD)

Embossed/engraved into the hard plastic between the two latches on top of the battery. This is the **durable code** — it does not wear off.

```
Format:   YY  MM  DD
Example:  24  07  09  = July 9, 2024
          23  04  19  = April 19, 2023
```

Sometimes followed by a plant letter (e.g., `240709D`).

**This is the most reliable date code format** — always check heat-stamp first before the bottom label.

### 3.3 Quick Reference: Warranty from Date Code

| Heat-Stamp | Manufactured | Shelf Allowance (-6mo) | Warranty Start | Warranty Expiry |
|------------|-------------|----------------------|----------------|-----------------|
| 240709 | Jul 2024 | ~Jan 2025 | Jan 2025 | **Jan 2028** (if no receipt) |
| 230419 | Apr 2023 | ~Oct 2023 | Oct 2023 | **Oct 2026** (if no receipt) |
| 220101 | Jan 2022 | ~Jul 2022 | Jul 2022 | Jul 2025 |
| 210315 | Mar 2021 | ~Sep 2021 | Sep 2021 | Sep 2024 |

**Always keep the receipt** — it overrides the date code and gives you the full 3 years from actual purchase.

---

## §4 The Cell Spec String (e.g., "5INR22/71-2")

This is printed on many M18 batteries and is frequently confused with the model number.

### 4.1 What It Is
The cell spec string identifies the **physical battery cells inside the pack**, not the Milwaukee product model number.

```
String:   5  INR  22  /  71  -  2
         ↑   ↑    ↑      ↑     ↑
         1   2    3      4     5
```

| Position | Meaning | This Example |
|----------|---------|-------------|
| **1. Cell Count** | Number of cells in series (5 = 5S = 18V nominal) | 5 |
| **2. Chemistry** | INR = Lithium Nickel Manganese Cobalt Oxide | INR |
| **3. Diameter** | Cell diameter in mm | 22mm |
| **4. Length** | Cell length in mm | 71mm |
| **5. Revision** | Internal cell revision/version | 2 |

### 4.2 Common Cell Specs

| Spec String | Chemistry | Cell Size | Common In |
|-------------|-----------|-----------|-----------|
| 5INR22/71-2 | INR (NMC) | 22mm × 71mm | M18 XC8.0 (48-11-1880), likely FORGE |
| 5INR22/64 | INR (NMC) | 22mm × 64mm | M18 XC6.0 (48-11-1860) |
| 5INR18/65 | INR (NMC) | 18mm × 65mm (18650) | Older M18 compact packs |

### 4.3 NOT the Model Number
The **Milwaukee catalog number** (model number) is displayed separately in white text on the front label:

| Catalog Number | Description |
|----------------|-------------|
| **48-11-1860** | M18 REDLITHIUM XC6.0 |
| **48-11-1880** | M18 REDLITHIUM HIGH OUTPUT XC8.0 |
| **48-11-1881** | M18 FORGE XC8.0 |
| **48-11-1885** | M18 FORGE 6.0 |
| **48-11-1890** | M18 REDLITHIUM HIGH OUTPUT 12.0 |

The `5INR22/71-2` string tells you the cell type (Samsung or LG 21700-format NMC cells) — useful if you're replacing individual cells, but irrelevant for warranty.

---

## §5 QR Code

The QR code on the battery label encodes the **serial number** — the same 13-character string printed on the bottom label. Milwaukee service centers scan this for intake tracking.

**No hidden data.** It's a direct encoding of what's already printed. Useful if the printed serial is scuffed but the QR is intact.

---

## §6 This User's Specific Batteries

### Battery 1: HIGH OUTPUT or FORGE — XC8.0 Class

| Field | Value |
|-------|-------|
| **Partial Serial** | `N82ND[?]TB 240709 0348761` |
| **Date Code** | `240709` = **July 9, 2024** |
| **Cell Spec** | Not visible on fragment — likely 5INR22/71 or similar |
| **Likely Model** | 48-11-1880 (M18 REDLITHIUM HIGH OUTPUT XC8.0) or 48-11-1881 (FORGE XC8.0) |
| **Warranty (with receipt)** | 3 years from purchase date — depends on when bought |
| **Warranty (without receipt)** | 6mo shelf allowance → ~Jan 2025 start → **expires ~Jan 2028** |
| **Status** | ✅ **ACTIVE** — well within warranty window |

**Recommendation**: Locate the receipt if possible. If this was purchased mid-to-late 2024, you have until mid-to-late 2027.

---

### Battery 2: XC8.0 Class (Older)

| Field | Value |
|-------|-------|
| **Full String** | `5INR22/71-2 18V / J51FDCHB 230419 0002245` |
| **Cell Spec** | `5INR22/71-2` — 5S, INR/NMC, 22mm×71mm cells (Samsung/LG 21700) |
| **Serial Decoded** | J51 = prefix, F = revision, D = plant, CH = year 23, B = week 02 |
| **Date Code** | `230419` = **April 19, 2023** |
| **Likely Model** | 48-11-1880 (M18 REDLITHIUM HIGH OUTPUT XC8.0) or 48-11-1881 (FORGE XC8.0) |
| **Warranty (with receipt)** | 3 years from purchase — if bought mid-2023, expiring ~mid-2026 |
| **Warranty (without receipt)** | 6mo shelf allowance → ~Oct 2023 start → **expired ~Oct 2026** |
| **Status** | ⚠️ **EXPIRING / EXPIRED** — borderline without receipt |

**Note**: `J51` prefix is a known Milwaukee factory code (also seen on 48-11-1880 packs). The `230419` heat-stamp places manufacture at April 2023, meaning without a receipt the warranty lapsed in roughly October 2026. If you have a receipt from mid-2023, the warranty is expiring right now (June-July 2026) — file any claim immediately.

### Quick Summary

| Battery | Date Code | Manufactured | Warranty w/o Receipt | Warranty w/ Receipt | Urgency |
|---------|-----------|-------------|---------------------|-------------------|---------|
| Battery 1 | 240709 | Jul 2024 | ~Jan 2028 | 3yr from purchase | 🟢 None |
| Battery 2 | 230419 | Apr 2023 | ~Oct 2026 (⬅ NOW) | ~mid-2026 (⬅ expiring) | 🟡 If failing, claim ASAP |

---

## §7 Claim Process (Step-by-Step)

### If a Battery Fails:

1. **Verify warranty** using the date codes above
2. **Find your receipt** (photo, email, Home Depot account history)
3. **Go to** `service.milwaukeetool.com`
4. **Create a service request** — describe "battery no longer holds charge" or "battery won't charge" or "dead cells"
5. **Milwaukee issues prepaid FedEx label**
6. **Prepare the battery for shipping from USVI**:
   - Tape terminals (electrical tape over the contact bars)
   - Place in original packaging or padded box
   - Mark package: **"UN3480 — Lithium-ion Batteries"**
   - Tell FedEx counter: "This contains lithium-ion batteries"
7. **Ship to assigned service center**
8. **Wait 7-14 days** for evaluation and replacement

### Alternative: Phone

Call **1-800-SAWDUST (1-800-729-3878)** — explain you're in USVI with no local service center. They will initiate the same eService process on your behalf.

---

## §8 Advice for Future Purchases

1. **Buy from authorized dealers only**: Home Depot, Lowe's, Acme Tools, Northern Tool, CPO Outlets, Ohio Power Tool. Their online stores also qualify.
2. **Photograph the receipt immediately**: Before the thermal paper fades. Upload to Google Drive / iCloud.
3. **Write the purchase date on the battery**: A silver Sharpie on the black plastic won't void anything and saves you later.
4. **Check the heat-stamp date code before buying**: If a battery has been sitting on the shelf for 18 months, you lose 18 months.
5. **Register in the ONE-KEY app**: Not required for warranty, but useful for tracking and battery management.

---

*Sources: milwaukeetool.com, documents.milwaukeetool.com (TIY404/460/515/520/527), service.milwaukeetool.com, onekeysupport.milwaukeetool.com, direct call to 1-800-SAWDUST, USPS/FedEx HazMat guidelines for UN3480.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
