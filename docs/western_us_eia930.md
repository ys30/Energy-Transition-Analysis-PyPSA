# Western US EIA-930 empirical-demand study (phase B)

## Status (2026-10-29)
**Implementation committed, not yet an empirical solved result.** This extension downloads real
EIA-930 hourly balancing-authority **actual demand** (type `D`) and solves an explicitly
assumption-driven, single-node economic dispatch with PyPSA/HiGHS. It does **not**
yet constitute a multi-period investment model or a calibrated Western Interconnection.

## Data and geographic scope
- Primary source: [EIA-930 hourly operating data](https://www.eia.gov/electricity/930-content/about.html).
- API: `https://api.eia.gov/v2/electricity/rto/region-data/data/`.
- Default non-exhaustive Western BA sample: CISO, BPAT, PACE, PACW, AZPS, NEVP, PNM, IPCO.
- Exact BA identifiers, revisions and temporal coverage must be confirmed by downloaded
  EIA data; the script refuses missing BAs or incomplete hourly month coverage.
- Demand is observed **MW**; the included gas/wind/solar capacities, costs, emissions,
  and availability factors are **scenario assumptions**, never represented as measured data.
- EIA reported BA demand must not be interpreted as transmission, plant capacity or generation.
- Overlapping reporting hierarchies, missing data and data revisions need audit prior to a
  comprehensive Western Interconnection aggregate.

## Reproduce

```bash
python -m pip install -e '.[model,dev]'
export EIA_API_KEY="YOUR_OWN_EIA_KEY"
python -m energy_transition.eia930_west --years 2023 2024 --output outputs/eia930_west
# Re-run offline using previously downloaded annual CSVs:
python -m energy_transition.eia930_west --years 2023 2024 --cached
```

Every year produces `eia930_demand_<year>.csv`,
`representative_hours_<year>.csv`,
`<year>/solved_network.nc`, `<year>/metrics.json`.
The comparative table is `yearly_summary.csv`.
The study records source and chosen BAs in `input_manifest.json`.
The original illustrative CLI remains intact and is **not** replaced by solved outputs.

## Temporal representation
Each calendar month is approximated by its mean 24-hour UTC demand shape.
The 24 timestamps for the month each receive a weight equal to the number of days
in that month; weighted energy thus approximates the full-year observed energy
(for fully covered data). This is not suitable for peak capacity adequacy,
extreme-weather analysis or storage chronological studies. The 2023/2024 examples
are independent historical dispatch runs, **not** investment periods.

## Next steps required for defensible 2025–2040 transition scenarios
1. Audit BA coverage and EIA revisions, obtain full observed 2019–2025 hourly series.
2. Integrate EIA-860/923 generation capability, operating histories and fuel cost,
   plus NREL wind/solar time-series; calibrate technology and regional capacities.
3. Add physical subregional nodes, verified transmission capacities and interchanges.
4. Construct PyPSA `investment_periods` (2025/2030/2035/2040), explicit
   multi-index snapshots, correctly discounted objective and period lengths;
   add build years, lifetimes, annualized investment costs, storage and CO2 budgets.
5. Run sensitivity analysis and comparison to observed generation shares; report
   full parameter provenance, solver logs, costs and emissions separately from observations.

## Caveat
If `EIA_API_KEY` is missing or the EIA API cannot be reached, the command fails explicitly;
it never silently fabricates data. This repository does not currently bundle
redistributed third-party EIA data or present invented model results.


## Seven-year automated historical input pipeline (2019–2025)

GitHub Actions workflow: [eia930-multiyear.yml](../.github/workflows/eia930-multiyear.yml).
It runs seven separate annual EIA-930 downloads and independent PyPSA dispatch
optimizations using the repository's `EIA_API_KEY` Actions secret. Each year
exports hourly observed-demand CSV, BA audit, representative snapshots, model
NetCDF, and metrics JSON. A dependent aggregation job writes
`yearly_summary.csv` and `ba_audit_all_years.csv` as a downloadable artifact.

This workflow runs when its workflow file or the EIA module changes, and
can also be launched via Actions > Western US multi-year EIA-930 PyPSA >
Run workflow. The workflow must complete successfully before results can
be described as verified. A failed year prevents aggregate publication.

**Scope warning:** the eight selected balancing authorities are a *subset*,
not all of WECC. Annual observations are historical demand, not measured
generation mix. The generator fleet and its costs remain illustrative.
The 288 representative hours per year smooth daily variation and cannot
support resource adequacy, peak reliability, storage chronology, or extreme
event conclusions. These are seven *independent* annual dispatch runs,
not seven PyPSA investment periods. Do not describe them as capacity-expansion
forecasts or a calibrated Western grid.

### Acceptance checks

- All seven annual jobs and the aggregation job pass.
- Each BA-year has exactly 8760 hourly rows, or 8784 in leap years.
- Every year contains all requested BAs; QC anomaly share stays within the
  configured 1% threshold; missing long gaps are rejected.
- The resulting yearly metrics have `solve_status=optimal`, and
  `unserved_share` is reported, never hidden.
- Downloaded CSVs and logs are retained as Actions artifacts for audit.
