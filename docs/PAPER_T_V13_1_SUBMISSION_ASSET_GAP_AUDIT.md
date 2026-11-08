# Paper T v13.1 — Submission-asset gap audit and scientific language correction

**2026-11-07 | Status: private editorial revision only; no new numerical experiment.** Latest main CI for published v13 documentation: [#42441327885](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42441327885) — success.

## Concrete findings

1. **The private v13 collaborator ZIP contains the main manuscript, Supplement S1 and Figure T5 PNG, but not Figure T1–T4 actual image binaries.** The T1–T4 source images exist in successful public Actions outputs and have a frozen repository SHA-256 list; the collaborator ZIP should therefore be called a **manuscript review bundle, not a complete journal submission package**. Before journal upload, retrieve the four SVG+PNG figure pairs, check the source hash lock and inspect images at print size.
2. Section 4.7 previously called NASA a form of **external validation**. The v13.1 private manuscript uses **external known-transform demonstration** instead. NASA UTC and LST are alternative timestamp encodings of the same source product, not independent observations or independently managed energy-demand systems.
3. The paired 89-hour NASA quantitative result remains **8.186629213483148 °C** naive same-label versus **0 °C** publisher-mapped MAE; the 96-hour naive **7.787395833333335 °C** is a separate descriptive sample.
4. The six-gate passport verifies declared schema completeness and produces an abstention/review-ready state. It cannot independently certify the submitted documentary basis and cannot automatically admit physical-hour joins.
5. The EFS2020 original `LocalHourID` clock remains unverified. An observed fitted source-index lag is not a physical timestamp transformation.
6. Source rights, GitHub repository license, publication-ready artifact retention and independently verifiable durable DOI have not yet been resolved.

## Verified figure retrieval

- T1: [#42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314)
- T2/T4: [#42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229)
- T3: [#42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936)
- T5: NASA originals [#42415066759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42415066759); equal-support analysis [#42419334016](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42419334016)
- Original T1–T4 16-source evidence SHA-256 hashes: [frozen source lock](paper_t_frozen_supplement_sha256.txt).

## Next genuinely blocking steps

1. Assemble all five **actual** figures in the private submission package and audit every caption for consistency.
2. Request coauthor methodology/novelty feedback, especially relative to PROV-O, CF metadata and Frictionless validation, and confirm appropriate journal article type.
3. Determine legal rights to distribute original-data-derived records, finalize software license, and create versioned permanent deposits only after owner approval.
4. Obtain original EFS clock authoritative evidence, or preserve an explicitly unresolved conclusion.

**No submission-ready, publisher-approved, independently authorized or DOI-deposited package is claimed.** The private manuscript is not published in this public repository.
