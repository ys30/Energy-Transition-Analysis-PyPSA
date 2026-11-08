# Paper T v13.2 — Original Figures T1–T5 retrieved and checksummed into private review package

**Date:** 2026-11-07. **Status:** original-source **private complete-figure collaborator-review package** assembled, **not** manuscript submitted or a DOI-backed public journal artifact.

## Verified delivery gap closed

The previous private editorial package v13.1 did not include the actual T1–T4 figure binaries. Those originals have now been **downloaded**, not copied from sample drawings or regenerated from manually transcribed values:

- Figures **T1**: [archived verified run #42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314), SVG+PNG.
- **T2/T4**: [run #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229), SVG+PNG.
- **T3**: [run #42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936), SVG+PNG.
- Canonical original T1–T4 and five supplementary tables plus three provenance JSON files were independently retrieved together from the accepted 16-file [supplement run #42332230767](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42332230767).
- **T5**: paired 89-UTC-anchor NASA POWER primary comparison figure, PNG only; naive **8.186629213483148 °C** versus correctly publisher-mapped **0 °C**.
- Actual original NASA POWER UTC and LST API JSON responses were retrieved from [#42419334016](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42419334016), with SHA256 `3d24f1604da17daea9126c7384ec9f4a9132760e224a7cab3d3c833feea81837` (UTC) and `1bf50d3c1852e100e4c8dfb4989c56a93fa86cde9beaa097f828355612f4f886` (LST).

**Actual archive audit:** five readable publication PNG figure files, four original SVG figure files, all 16 original EFS/ReEDS evidence files matched to the accepted `SHA256SUMS.txt` and [independent repository frozen checksum lock](paper_t_frozen_supplement_sha256.txt), with byte-hashed NASA original source files. All source-derived results preserved: no new energy-model or demand simulation.

The newly packaged **private** manuscript v13.2 updates section 7.2, which previously incorrectly said the private ZIP contained no T1–T4, and supplies relative links for each actual figure. It also preserves the explicit known-transform NASA caveat and the original EFS source clock's unresolved physical-time mapping.

### Still blocking actual submission

This closes the missing-image delivery issue only. **Code license, derived data redistribution rights, permanent derived-data/source DOI, coauthor approval, and journal-specific proofing are not complete.** NASA UTC and LST are two encodings of the same product; original EFS2020 clock and Idaho geography remain unresolved. No private manuscript or source-publisher original data have been published by this GitHub documentation update.
