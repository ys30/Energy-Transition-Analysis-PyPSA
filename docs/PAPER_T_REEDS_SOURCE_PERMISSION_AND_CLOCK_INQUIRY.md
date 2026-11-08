# Paper T — ReEDS 2022 source-license and original EFS clock inquiry (prepared, NOT SENT)

**State:** one formal source inquiry has been prepared privately, but **no email was sent and no publisher permissions were granted**.

## Verified publisher/team contacts

- [ReEDS staff official NLR page](https://www.nlr.gov/analysis/reeds/): **ReEDS.Inquiries@nlr.gov**.
- [ReEDS 2022 electricity demand profiles](https://doi.org/10.5281/zenodo.18461543), published **2026-02-04**, DOI `10.5281/zenodo.18461543`; the creators listed on the publisher record are Caitlin Murphy, Trieu Mai, Paige Jadun, Jonathan Ho, Colin McMillan and Jack Mayernik.
- Source file `demand_EFS_REFERENCE.h5` has published MD5 `7b2055d43200744a16a8c4fed68b1a17`.
- The publication explicitly documents a **2012 reference weather/calendar, CST (UTC−06:00), hour-ending** convention, and 8760-hour truncation. These are characteristics of the **ReEDS 2022 released product**, not authoritative declarations that all original EFS2020 `LocalHourID` labels share this timestamp mapping.

The published Zenodo record's Rights/License field currently exposes no verifiable named license in the public page text inspected. **Open accessibility is not the same as an affirmative permission to redistribute the ReEDS-derived numerical table or source-inclusive figure files.** No CC-BY license is assumed.

## Two questions to send via the verified ReEDS channel

1. What exact reuse and redistribution terms apply to `demand_EFS_REFERENCE.h5`, and specifically to derived state-year lag summaries, Idaho subsector comparisons, residual month/hour marginal tables and Figures T1–T5? Which attribution and notice requirements apply to mixed-origin original EFS and ReEDS derivative results? Obtain a link to a rights statement or written answer.
2. What is the authoritative clock convention of **original EFS2020** `LocalHourID` (start/end hour, weather/calendar year, timezone, DST/leap treatment, geography/timezone within Idaho, and any mapping performed for the ReEDS2022 model product)? If the ReEDS team does not own that older source definition, ask for the source-author contact.

The **privately prepared outreach email** includes exact DOI references and a narrowly stated scientific finding; it is **not uploaded as a public manuscript** and remains unsent. Under no circumstances should a fitted numerical −2/−3 hour offset be presented as an authority-verified source-to-UTC conversion. The six-gate screening must continue to **BLOCK_PHYSICAL_JOIN** for this pair.

## Release decision table

| Source-author response | Public source-derived deposit decision |
|---|---|
| Explicit written permission and scope confirmed | Release only expressly permitted derivatives with correct notices, after author/coauthor approval |
| Permission limited to aggregates | Exclude disallowed high-resolution tables/figures and original files |
| No answer or license remains ambiguous | Metadata-only reproducibility links; no ReEDS-derived bytes |
| Source physical clock not certified | Physical weather-hour joining remains blocked regardless of reuse permission |

**Outstanding:** original EFS clock, ReEDS source license, code copyright ownership/license, coauthor disclosure approval, stable deposit and actual DOI. These are separate conditions; getting one answer does not automatically resolve the others.
