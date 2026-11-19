# Paper S — full-year EIA-930 scope QA integrated into manuscript and SI (2026-11-18)

## Artifact status

Verified conversation-local Word deliverables were created from the **existing** 2026-11-17 integrated 22-page main manuscript and 8-page integrated Supplementary Information, rather than replacing or rerunning frozen LP outputs:

- `Paper_S_Main_Manuscript_With_2023_Annual_EIA930_QA_2026-11-18.docx` — discussion §4.5 limitations revised, document still 22 rendered pages.
- `Paper_S_Supplementary_Integrated_With_2023_Annual_EIA930_QA_2026-11-18.docx` — stale pending-status Supplementary Note S5 corrected; new **Supplementary Note S6**, **Table S3**, data-quality bounds and sources appended; 8 rendered pages.
- `Paper_S_2023_Annual_Observation_QA_Integrated_Manuscript_SI_2026-11-18.zip` — both Word outputs, README and three detailed CSV companion tables. These conversation files **have not been committed as repository binary files or deposited to Zenodo**.

Full 2023 BA source data GitHub Actions **44246001519** (artifact **14406998900**) and source-month EIA-860M check GitHub Actions **44391834613** (artifact **14472021718**) had already succeeded.

## Explicitly manuscript-admitted findings

1. Eight EIA-930 BA × fuel source series in 2023: **69,952** actual source-hour rows on **70,080** potential UTC BA–fuel hour slots; **128** absent source timestamps and **241** present timestamps with null reported MW; **69,711** nonnull reported MW observations. These are source coverage figures, not a verified state-curve crosswalk.
2. **96** contemporaneous 2023 monthly BA–fuel EIA-860M Operating generator inventory candidate-nameplate cohorts were paired to **reported and adjusted** EIA-930 BA net power using source month. The monthly generator list is a subset/definition test, not a verified denominator for the BA's physically reported generator population.
3. Source hour flags above the monthly candidate nameplate: **1,320 reported** and **1,319 adjusted**. The sole changed classification is **PSCO PV at 2023-06-02 21:00 UTC** (reported 15,914 MW; adjusted/imputed 1,327 MW; contemporaneous BA-code candidate nameplate 1,666.9 MW).
4. The July WACM official Operating roster has **47** identified solar PV source generators (243.9 MW), versus **22** identified original EIA-930A generator records (161.9 MW); the added **25 independently keyed** generators total **82.0 MW**, and **cannot be equated** to the unrelated 15 undated/unidentified EIA-930A rows.
5. No source-derived exceedance flag implies physical generator overproduction. **EIA-930 BA boundary ≠ modeled state boundary**, source MW measurement conventions differ from instantaneous sampled ReEDS CF, and generator inclusion/BA dynamic transfers remain unresolved. No independently validated observed CF, ReEDS model-skill metric or BA-state energy comparison is claimed.

## Reproducibility and frozen work

Local companion Tables **SI-R6** (96 paired month-level rows), **SI-R7** (8 BA/fuel annual summaries), **SI-R8** (single source classification-changing hour) are included with the integrated Word package; main manuscript and existing SI table/figure numbering are unchanged apart from new **Table S3**. Original **1,440** LPs, **360** new 2×2 LPs, **2,880** new 3×3 LPs and **2,160** ATB comparisons were **not** rerun or rewritten. Paper C-2 is out of scope.

**Remaining submission gates:** verify manuscript internal consistency and source citations, confirm BA dynamic measurement population or explicitly keep this as an SI limitation, prepare permanent reproducibility archive/DOI and journal-specific formatting. The manuscript is still a review draft, not a published/submitted article.
