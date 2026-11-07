# Paper T v6 — Original-source supplemental evidence bundle

## Acceptance: successfully built from independent previously passing sources

The [Paper T unified SHA-256 supplementary workflow #42332230767](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42332230767) **passed**. Artifact name: `paper-t-original-source-supplement-16-files-sha256` (GitHub Actions retention: **90 days**, **not** a permanent DOI).

This workflow downloaded six independently archived source and figure artifacts from verified workflows; copied only actual source-result data and figure files; checked their population/unique keys; and generated `source_sha256_manifest.json` and `SHA256SUMS.txt` in a consolidated supplement directory.

### Contents and source provenance

| Supplement item | Content / expected coverage | Verifiable source run |
| --- | --- | --- |
| T_S1 | 33 nonwrapping state-year source-lag records, 11 West states × three years | [#42122065064](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42122065064) |
| T_S2 | 42 original Idaho source Sector×Subsector/year records (14 original groups × three years) | [#42131969905](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969905) |
| T_S3 | 3-year fixed 2030 Transportation +1 source-index-hour validation, including training and held-out halves | [#42131969905](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969905) |
| T_S4 | 324 separate month/hour marginal source-residual records, ID/AZ/CA × three years | [#42125517759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42125517759) |
| T_S5 | 9 Idaho/control original-state/year source-residual overview rows | [#42125517759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42125517759) |
| Figure T1 | Source provenance and **blocked** physical-hour join, SVG + PNG | [#42177083314](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42177083314) |
| Figures T2/T4 | Original-source best-lag figure and frozen source-index-hour candidate figure, SVG + PNG | [#42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229) |
| Figure T3 | Published ReEDS2022 reference month and hour **separate marginal** source errors, SVG + PNG | [#42162565936](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42162565936) |

Five CSV files + three source-provenance JSON files + eight SVG/PNG files = **16 copied input evidence files**. The generated README, checksum text and machine-readable manifest are **additional administrative files**, not counted among the 16.

The `source_sha256_manifest.json` records every copied file's SHA-256, byte size, source Actions run ID, scenario scope, and fail-closed claims. Run `sha256sum -c SHA256SUMS.txt` inside the extracted supplement directory; do not substitute a hand-typed figure or copied table for original archived results.

### Reproduction instructions

```bash
gh run download 42332230767 -R ys30/Energy-Transition-Analysis-PyPSA \
  -n paper-t-original-source-supplement-16-files-sha256 \
  -D paper-t-supplement
cd paper-t-supplement
sha256sum -c SHA256SUMS.txt
```

The source assembly implementation is `src/energy_transition/paper_t_supplement_bundle.py`; regression tests are `tests/test_paper_t_supplement_bundle.py`; the workflow is `.github/workflows/paper-t-source-supplement-bundle.yml`. A failed/missing original file, repeated source hour identity, incomplete 33 source cases, incomplete 14 Idaho subsector groups, incomplete 324 source month/hour margins, or missing SVG/PNG must **stop** assembly.

### Paper T private collaborator manuscript v6

The *private*, fully preserved v5 manuscript is now revised into v6 with a new section detailing the canonical T_S1–T_S5 supplementary tables and SHA-256 bundle provenance, including reproducibility command and explicit **90-day Actions expiration**. The manuscript is not committed to this public repository.

### Scientific and archival boundaries

- The **numeric** EFS2020→ReEDS2022 nonwrapping best shifts and Idaho source discrepancies were independently verified. **Original EFS2020 `LocalHourID` is not certified as physical UTC/CST**; the source time/weather-year and substate Idaho geography remain unresolved.
- No joint month×hour matrix has been recovered; Figure T3 reports separate marginals only.
- There is **no causal time-zone attribution**, no empirical renewable weather-year join, and no real Western interconnection network OPF.
- A GitHub Actions combined artifact is not long-term preservation. **Next journal-publication data task:** select an appropriate public versioned code/data deposit (e.g., GitHub release and Zenodo DOI) with immutable source hashes. Do not claim that a DOI exists until published and independently verified.

The current result is a **coauthor-verifiable supplementary evidence package**, not a formally deposited journal data set.
