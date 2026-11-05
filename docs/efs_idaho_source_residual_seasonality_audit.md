# EFS2020–ReEDS2022 Idaho source-hour residual localization

## Why this diagnostic matters

Previous real-source checks compared all 289,080 annual hour pairs, established stable nonwrapping best offsets of −2 h for the Mountain-group states and −3 h for Pacific-group states, and isolated an unresolved **Idaho exception**. In 2030/2040/2050, Idaho retained roughly 17.3/19.3/22.1 MW best-lag mean absolute error, while control-state pairs were about 0.25 MW and no control-state comparison residual exceeded 1 MW.

The pinned PyPSA-USA implementation uses one state timezone (Idaho designated US/Mountain) despite the source code warning that multitimezone states and exceptions are not represented. That downstream implementation is a documented potential attribution issue, **not** an authoritative Idaho original source clock or explanation for ReEDS2022 differences.

## New source-driven falsification test

This audit compares the *original archived EFS 2020 state-hour series* to the *separately downloaded and publisher MD5-verified ReEDS2022 HDF5 state series* on only truly overlapping, nonwrapping hours. It compares Idaho with Arizona (−2 h) and California (−3 h) as controls, and examines three years independently.

For each year/state, it exports:
- Mean absolute error, fraction above 1 MW, 95th-percentile error, maximum 24-hour moving mean error, number and longest run of consecutive abnormal hours.
- Monthly and 24-hour reference-clock distributions of errors, signed bias, 95th-percentile, maxima and abnormal counts.
- Provenance hashes and a machine-readable warning that month and hour labels are **the 2012 UTC−06 ReEDS2022 published reference index**, not original 2020 EFS certified physical hours.

Scientific use: if Idaho error is consistently spread across months and clock hours, an isolated Jan/Dec wrap or one-off DST discontinuity becomes less plausible; however **neither a persistent residual nor time-of-day structure uniquely identifies an Idaho timezone split**. Other possible causes include release-specific aggregation, population mapping, mixed source curves, rounding and interpolation. The original EFS source is published at state/sector/subsector scope and does not identify substate timezones.

## Reproduction

- `src/energy_transition/efs_idaho_source_residual_diagnostics.py`
- `tests/test_efs_idaho_source_residual_diagnostics.py`
- [Source-backed GitHub Actions workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-idaho-residual-diagnostics.yml)
- Input artifacts: EFS source run `41262154939`, and independent publisher source HDF5 `demand_EFS_REFERENCE.h5` checked against MD5 `7b2055d43200744a16a8c4fed68b1a17`.
- Output artifact: `efs-idaho-source-residual-month-hour-2030-2050`

**Acceptance:** Source CI results must be verified before making numerical claims. This diagnostic **never** authorizes EFS2020 UTC alignment, EIA-930/NSRDB/WIND Toolkit join, generator-to-bus electrical mapping or physical Western OPF. Its main value is making Idaho's unresolved discrepancy inspectable and falsifiable for a provenance-methods manuscript.
