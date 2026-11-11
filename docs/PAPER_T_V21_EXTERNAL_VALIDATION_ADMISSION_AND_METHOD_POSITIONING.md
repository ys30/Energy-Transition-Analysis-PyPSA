# Paper T v21 — external validation candidate screening and method positioning (11 Nov 2026)

**Current status:** Private manuscript v21 has editorial revisions to Introduction (research gap and contributions), Discussion §5.6, and Limitations §6. **No second independent release-pair test has been run. No real irradiance/PV joining has been admitted.**

## Distinguish three questions
1. Are annual energy totals equal?
2. Are values equal at some nonwrapping *ordinal* shift?
3. Does the publisher authorize those ordinals as corresponding *physical hours*?

An affirmative answer to question 2 is **not** an answer to question 3. Current Paper T source pair remains BLOCK_PHYSICAL_JOIN.

## Candidate screening

| Proposed extension | Eligibility | Why |
|---|---|---|
| EFS 2020 Reference/Moderate against other EFS electrification/technology scenarios | **Reject as version replication** | Different scenarios rather than reissues of the same scenario |
| ReEDS historical demand (https://zenodo.org/records/18462671) against modeled EFS_REFERENCE demand (https://zenodo.org/records/18461543) | **Reject as version replication** | Historical observed-derived versus modeled scenario |
| NASA POWER UTC vs LST | **Existing known-transform control, not an independent release** | Different time representations of one product |
| Successive releases of same scenario / quantity with authenticated lineage | **Pending suitable matched source** | Requires identical scenario and compatible region, units, weather basis, and clock evidence before running O1/O2 |

EFS source: https://data.nlr.gov/submissions/126

## Controlled real-solar experiment acceptance gates

Candidate: NASA POWER 2012 hourly irradiance in **UTC** against the ReEDS2022 published **hour-ending CST** 2012 representative time index. Before an actual join, explicitly reconcile NASA's hour-beginning convention (https://power.larc.nasa.gov/docs/faqs/other/) against ReEDS hour-ending convention; map timestamps to UTC, verify 2012 leap day retained and December 31 omitted, and enforce unique matching intervals. A single-location irradiance series is **not** state-level actual PV generation; any scaling to MW is an assumed proxy and must be labelled as such. Do not imply a validated EFS2020 physical clock. If any temporal/geographic gate cannot be independently satisfied, stop rather than producing a visually convincing but false model result.

## Publication preparation

The corrected v4 300-case synthetic analysis [CI #43052039916](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43052039916) and the actual-source 825-point lag analysis [CI #43052221098](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43052221098) are completed. No new DOI or license has been issued. Funding and competing-interest declarations require author confirmation; AI-assisted research code/data analysis must be recorded in Methods and manuscript preparation in a separate declaration under Elsevier policy: https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals .

**No private manuscript, publisher raw data, or unsanctioned derivatives are included in this public note.**
