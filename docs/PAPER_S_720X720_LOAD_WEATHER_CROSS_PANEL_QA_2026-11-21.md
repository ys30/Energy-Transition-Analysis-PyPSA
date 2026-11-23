# Paper S — 720×720 authenticated fixed-demand versus matched-weather-load comparison (2026-11-21)

## Evidence and execution

- GitHub Actions successful run: https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128403
- Official uploaded artifact: `paper-s-720x720-weather-load-cross-panel-verified-comparison`, artifact ID **14712877100**, 33,014 bytes compressed.
- Run commit: `163be7844a4942fd3ada21c5fbb13cd690b3740d`.
- Pinned earlier successful LP inputs: fixed-2030-demand source run **43651682920** and historical weather-year matched load run **43665299980**.
- Unit tests: **3 passed**. Official job gates and artifact upload succeeded.
- Exact manifest/log checks: **720** unique matching LP objective pairs, **240** storage-duration triplets, **120** geography comparisons. Required two load-mode identities were present and unique; all 120 spatial effect direction flags are non-null.

## Interpretation boundary

This comparison separates and labels two fixed-demand versus historical-year-load populations, and prevents inadvertent mixing of LP experiment settings. It does **not** isolate a shape-only causal effect, does **not** validate a 2030 installed-fleet projection, and does **not** establish observed dispatch or actual investment profitability. In particular, scaling historical weather-shaped load to 2030 annual energy also changes the peak-based installed-power normalization; it is not a pure shape contrast.

Manifest fields explicitly confirm `shape_only_causal_effect_established=false`, `source_same_weather_2030_fleet_projection=false`, and `load_annual_energy_scaling_also_changes_peak_based_installed_power=true`.

## Publication gate

- **ACCEPT**: the successful controlled comparison and complete pair counts in numerical methods/SI.
- **DO NOT CLAIM**: an independent causal attribution to load-weather synchronization or same-weather empirical validity.
- **PENDING**: inspect full 120-row geography comparison and 240-row duration-value comparison to report state-specific directional changes with appropriate uncertainty; avoid substituting unsupported numerical claims based on CI status alone.
- **IN PROGRESS** at this writing: distinct CO R=1.5 common-design 180-LP source-year control, https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44919128370. Do not report its result until complete artifact validation.
- Keep the original frozen 3×3 source experiments and historical-demand source runs unchanged.
