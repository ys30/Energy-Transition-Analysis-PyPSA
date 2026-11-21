# Paper S — 2026-11-18 submission figure/citation and manuscript-to-SI consistency audit

The latest source documents were directly reopened and audited:
- `Paper_S_Main_Manuscript_With_2023_Annual_EIA930_QA_2026-11-18.docx` (22 rendered pages, 8 embedded figures, 4 tables, 206 paragraphs).
- `Paper_S_Supplementary_Integrated_With_2023_Annual_EIA930_QA_2026-11-18.docx` (8 rendered pages, 5 supplementary figures, 3 tables, 49 paragraphs).

**Corrected actual manuscript defect:** main text figures appeared in the order **1,2,5,6,7,8,3,4**, with mechanisms and 3×3 figures preceding the ATB comparison figures. Renumbered by occurrence so new main Figure captions are **1,2,3,4,5,6,7,8**. Mapping: old 5→3, 6→4, 7→5, 8→6, 3→7, 4→8; old 1,2 unchanged. Updated matching main inline Fig. references and SI prose references: the previous main Figure 7/8 3×3 references are now Figure 5/6.

**Reference-list audit:** expanded numbered cite ranges (e.g. [1–4]) rather than naively matching single IDs. All **73 bibliography entries** are referenced in the main text, none missing; added an explicit EIA-930 source citation [73] to the main §4.5 observation-audit paragraph, which had not cited its EIA-930 bibliography entry. This is **citation-number coverage only**: publication DOI, bibliography metadata and factual correspondence were not independently externally verified.

**Rendered and checked:** updated main 22 pages, updated SI 8 pages; all original 8 main and 5 SI embedded figures, four main and three SI data tables remain. There was no alteration to LP results, source curves, empirical values or statistics.

**Actual conversation-local file outputs** (not GitHub binary or Zenodo releases):
- `Paper_S_Main_Submission_QA_Figure_Sequence_Corrected.docx`
- `Paper_S_SI_Submission_QA_Figure_References_Corrected.docx`
- `Paper_S_Submission_Figure_Citation_QA_2026-11-18.zip` with both Word files, audit JSONs and SHA-256 manifest.

## Remaining submission blockers

1. Author-specific funding, conflict-of-interest, contributions and AI-tool declarations need confirmed language, not invented claims.
2. Paper-specific immutable Zenodo DOI, license scope and durable archive of source/output provenance still pending.
3. Substantive **LP dollar basis versus 2023-dollar ATB hurdle comparability** remains unreconciled in main §4.5; costs must remain conditional or be harmonized.
4. EIA-930 BA net MW population, month-specific EIA-860M BA generator code and ReEDS state model geography remain non-equivalent until source-audited mapping; 1,320 raw/1,319 adjusted candidate threshold hours are **scope flags**, not proof of physical overproduction or validated model skill.
5. Journal-specific submission formatting, bibliography DOI/metadata spot-check and anonymity requirements remain.

Frozen 1,440 base LPs, 360 2×2, 2,880 3×3, 2,160 ATB screens, prior descriptive observation findings and Paper C-2 remain unchanged.
