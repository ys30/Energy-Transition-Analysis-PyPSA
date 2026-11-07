# Paper T v11 — independent NASA POWER UTC/LST external source-clock validation

**Execution state:** [NASA POWER source-retrieval and conversion CI #42415066759](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42415066759) **passed**. This is the **first authentic, independent-of-EFS/ReEDS source-family case** in the Paper T method program.

## Official authoritative time metadata

[NASA POWER hourly API official documentation](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) says the hourly archive is stored in UTC, an explicitly requested `time-standard=UTC` delivers UTC, and `time-standard=LST` produces a local-solar-time axis using longitude-based 15-degree swaths. Crucially the service defaults to LST if unspecified. The POWER FAQ says hourly timestamps represent the **start of an hour**: https://power.larc.nasa.gov/docs/faqs/other/. LST here is **not** the legal civil timezone and does not establish DST conventions for other sources.

## Actual original API comparison

- Location: 35.0° N, 105.0° W, chosen exactly at the longitude-center of the −7 h solar swath to avoid offset rounding ambiguity
- Date: 2024-01-15 through 2024-01-18 inclusive
- Parameter: T2M (°C), temperature at 2 meters; this is **real NASA POWER source response data**, not an assumed EFS-generated shape
- Two explicit original POWER requests: UTC and LST, 96 hourly keys each
- NASA publisher-defined transformation: **LST = UTC − 7 h** at −105°
- Correct nonwrapping overlap: **89** hourly pairs; never circularly wrap boundary values
- *Incorrect* same-label UTC/LST comparison MAE: **7.787395833333335 °C** over 96 label pairs
- After physical UTC/LST label normalization, matching 89 timestamps: **MAE = 0.0 °C**, max absolute difference 0.0 °C (the two API outputs are transformed representations of the **same NASA data**, not independent observations)

Exact source-byte SHA256 (from the passing real-source workflow):
```text
3d24f1604da17daea9126c7384ec9f4a9132760e224a7cab3d3c833feea81837  nasa_power_hourly_UTC_original.json
1bf50d3c1852e100e4c8dfb4989c56a93fa86cde9beaa097f828355612f4f886  nasa_power_hourly_LST_original.json
```

The **three original-source JSON files** (two API responses plus derived audit) are retained as CI artifact `paper-t-nasa-power-actual-utc-lst-2024-source-verified`; its content is separate from the already SHA256-frozen 16-file EFS/ReEDS supplement and does not rewrite it.

## What this external case validates

This is an authentic independent **product family** where the publisher supplies the true physical time transform. It demonstrates that:
1. Two hourly sources can have equally complete calendars yet show large numeric error under naive label matching.
2. An **explicit publisher-specified mapping**, instead of data-fitted lag alone, can recover identical physical hours without inventing boundary records.
3. The original data and the transformation can be independently downloaded, checked, re-run and hashed.

It does **not** validate that an arbitrary filled-out six-gate passport is true. The six-gate screening software still only emits `READY_FOR_INDEPENDENT_SOURCE_REVIEW` for all self-declared passes, NEVER a final `ADMIT_PHYSICAL_JOIN`. The NASA test is a **documented known-transform positive control**, not a universal benchmark of prediction accuracy or a demonstration of the accuracy of a human evidence reviewer.

## Methods and reproducibility

- `src/energy_transition/paper_t_nasa_power_external_clock.py`
- `tests/test_paper_t_nasa_power_external_clock.py`
- `.github/workflows/paper-t-nasa-power-clock.yml`
- CI independently downloads both real API responses; tests reject missing hours, sentinel values, duplicate labels and incorrect physical time transforms.

Retrieval can be rerun with:
```bash
PYTHONPATH=src python -m energy_transition.paper_t_nasa_power_external_clock \
  --out outputs/paper_t_nasa_power_external_clock
```
Or use the *exact archived JSON bytes* with `--utc-file` and `--lst-file` for deterministic source reruns. An API rerun may reflect upstream revision of NASA products, so compare SHA256 and keep both the archived input and retrieval date.

## Implications for publication

The case materially improves generality versus v10, which had only a single related EFS/ReEDS release pair and synthetic unit tests. However, it is **one within-product clock-standard transformation** and should be presented as an *external known-transform positive control*, not an external independent second energy-demand dataset, long-term benchmark or new NASA data discovery.

The original EFS2020 LocalHourID physical reference, Idaho cause, wind/solar joins, network OPF, and durable dataset DOI remain unresolved. The private v11 coauthor manuscript is not uploaded to GitHub.
