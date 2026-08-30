# 🔱 EXECUTION GUIDE: CARMACK (The Architect)
**S3 Ingestion Hardening — Metal, Architecture & Linguistics**
**Jurisdiction**: S3 Consultant / Architectural Review

## 🎯 OBJECTIVE
Ensure the absolute integrity of the data layer and the academic rigor of the linguistic core. You are the guardian of the "Right Approximation" and the "Metal."

---

## 🛠️ PHASE 0: THE BEDROCK (Day 1-2)
*Dependency: None. Blocks all other phase execution.*

### T1: Mount-Aware Double-Fsync Implementation
- **Files**: `src/omega/oracle/memory_store.py` and `src/omega/oracle/entity_registry.py`.
- **Logic**:
    - Locate all `os.replace(tmp, target)` calls in `_save()` and `_persist_hot()`.
    - Implement `safe_fsync(fd)`: Detect mount type via `/proc/mounts`.
    - If local (NVMe): `os.fsync(fd)` $\rightarrow$ `os.fsync(dir_fd)`.
    - If network (NFS/FUSE): Best-effort write (skip `dir_fd` fsync to avoid hangs).
- **Acceptance**: New test `test_atomic_write_survives_crash` proves data is physically on disk after a simulated power loss.

### T7: Branding Purge (The Great Cleaning)
- **Action**: Mechanical removal of "Sovereign" prefixes from the `src/omega/ingestion/` directory.
- **Commands**: `sed` replace `SovereignScraper` $\rightarrow$ `WebScraper`, `SovereignWorker` $\rightarrow$ `IngestionWorker`, etc.
- **Verification**: `grep -r "Sovereign" src/omega/ingestion/` returns 0 matches.

---

## 🏗️ PHASE 1: LINGUISTIC FOUNDATION (Day 3-6)
*Dependency: T1 Complete. B2 (CLTK Models) must be provisioned by Ma'at.*

### T6: Greek Normalization & CLTK Singleton
- **File**: `src/omega/linguistics/normalize.py` (New File).
- **Logic**:
    - Implement `CLTKSingleton` wrapper to load `cltk.nlp.NLP(language="grc")` once per worker process.
    - Implement `is_greek(text)` using Unicode range checks.
    - Implement `normalize_greek(text)` using CLTK's normalization pipeline (NFC).
    - Ensure the pipeline handles polytonic Greek and archaic apostrophes.
- **Acceptance**: Correctly normalizes `ἀνὴρ` and lemmatizes `λόγος` using academic standards.

---

## 📜 PHASE 3: THE ARCHIVE (Day 9-10)
*Dependency: All functional tickets complete.*

### T8: PLO Deferral Documentation
- **File**: `docs/strategy/FUTURE_LINGUISTICS_SPIKE.md` (New File).
- **Content**:
    - Document the deferred components of the Linguistic Observatory (Stylometry, SoundSymbolism, ProseComposer).
    - Define the "Trigger for Re-activation" (e.g., a specific entity request).
    - Link to the recovered `PLO.py` as the reference implementation.
- **Acceptance**: Document is a professional technical spike, not a "wishlist."

---

## 🛡️ MANDATES & CONSTRAINTS
- **S3 Right Approximation**: Do not over-engineer. If a simple regex handles 99% of cases, use it. If CLTK is needed for 1%, use it only where required.
- **M1 (AnyIO)**: No `asyncio`.
- **M18 (Token Efficiency)**: Ensure normalization doesn't bloat the token count.
- **M20 (SomaticState)**: While not in this sprint, ensure your changes to `memory_store.py` do not break potential binary state serialization.

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_execution ⬡ ARCH_GUIDE*
