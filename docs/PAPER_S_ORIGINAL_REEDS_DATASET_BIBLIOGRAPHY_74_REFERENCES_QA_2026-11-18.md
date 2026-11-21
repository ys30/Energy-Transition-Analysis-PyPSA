# Paper S — targeted original-source and bibliography metadata QA (2026-11-18)

**Status: source-based scholarly citation and reproducibility audit, limited scope.** No changes to frozen LP/ATB/BA source numerical results.

## Actual Word document inspection

Directly reopened the then-current 22-page original `Paper_S_Main_Currency_Consistency_Corrected_2026-11-18.docx` and 9-page SI. The main bibliography listed 73 numbered items. In Methods §2.2, the **original historical ReEDS demand dataset `demand_historic.h5`** was correctly described with Zenodo DOI and source MD5 but was **not present as a separately numbered reference**. This omission has now been corrected.

**New citation [74]:** Obika, K., & Cole, W. (2026). *ReEDS: Historical electricity demand profiles (v1)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18462671. Original source record https://zenodo.org/records/18462671 independently confirms author pair, year, dataset version and `demand_historic.h5` MD5 `06ca6b65088a870afafc25191dcfd6f3`. Main Methods paragraph now explicitly cites [74]. All existing 1–73 reference numbering remains unchanged.

## Three missing journal-article DOIs externally checked and appended

- **[25]** Bistline (2021), *Environmental Research Letters* 16(8), 084005: https://doi.org/10.1088/1748-9326/ac10df (Crossref and publisher-derived bibliography).
- **[30]** Kumler et al. (2019), *Environmental Research Letters* 14(4), 044032: https://doi.org/10.1088/1748-9326/aaf935.
- **[31]** Craig et al. (2019), *Environmental Research Letters* 14(3), 034014: https://doi.org/10.1088/1748-9326/aaf93b (University of Colorado Boulder metadata).

**Version and clock source preservation:** the cited original 2026 ReEDS **wind v1** (https://zenodo.org/records/18422200) and **PV v1** (https://zenodo.org/records/18407660) datasets explicitly say the timestamp basis is fixed **CST UTC−06:00**, represent instantaneous capacity factors on the hour and preserve 15 source weather years. Their newer v2 versions are **not substituted**, because doing so changes the model input edition/structure and would require a fresh scientific source audit. The 2022 ReEDS demand v1 (https://zenodo.org/records/18461543) and historic demand v1 also state fixed CST hour-ending semantics. This matches the manuscript's native-source clock description, not any naive UTC equality.

**ATB v2 source provenance:** the OEDI 2025 ATB collection (https://data.openei.org/submissions/8759) is confirmed, and the US official Data.gov catalog lists the exact `2025_v2_Workbook_11-11-2026.xlsx` download URL already in bibliography [17]. No retrospective price-year normalization is inferred from that source verification.

## Deliverable and QA

Conversation-local `Paper_S_Submission_Source_Bibliography_Audit_2026-11-18.zip` contains:
- `Paper_S_Main_Submission_References_74_DOIs_Updated.docx`: 22-page regenerated main Word with numbered citation [74] and three verified DOI additions, preserving the 22-page layout and all other content/results;
- `Paper_S_SI_Unchanged_Source_Version_Frozen.docx`: prior 9-page SI copied byte-for-byte, no results rewritten;
- `Table_QR1_key_source_metadata_verification.csv`, README and source/output SHA-256 manifest.

This ZIP and DOCX are conversation-local outputs, **not binaries uploaded to GitHub, not a GitHub release and not a Zenodo deposit**.

## Still open

No claim of verifying full publication metadata of all 74 references. The paper-specific Zenodo DOI is not deposited. Funding/conflict/AI-assistance declarations are still placeholders pending author/journal-specific facts. The illustrative LP `cR=5`, `cF=90` common-2023-dollar comparison remains explicitly conditional; the model is single-node copperplate rather than source-validated real BA power production or network results. Frozen Paper S original 1440 LP, new 360 2×2, new 2880 3×3, ATB 2160 and Paper C-2 are unchanged.
