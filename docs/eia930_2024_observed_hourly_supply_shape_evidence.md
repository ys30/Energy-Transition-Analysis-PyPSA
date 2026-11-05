# Project B: observed 2024 EIA-930 renewable net-generation shape, separately audited

## Data provenance and intended role

The project already retains source-derived **2024 EIA-930** hourly signed *net generation* for solar (SUN) and wind (WND), separately for **California ISO (CISO)** and **Bonneville Power Administration (BPAT)**, from [previous successful official-source ingestion run #41003777337](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41003777337). The current check reopens that archived data and audits the four complete 168-hour UTC weeks in the original seasonal artifact (winter, spring, summer, autumn): **4 weeks × 168 hours × 2 BA × 2 fuel = 2,688 source records, organized as 16 individual BA×fuel×season panels**.

This is distinct from the prior [EFS projected load 540-cyclic-LP mathematical sensitivity](efs_8760h_cyclic_storage_scaleup.md). These observed 2024 EIA-930 records are real *reported* BA-level net production, but they are **not unconstrained wind/solar potential, plant-capacity-normalized resource profiles, or forecasts for 2030–2050**. The project does not join the EIA-930 periods to EFS future LocalHourID, because [original EFS source time semantics are not independently certified](efs_vs_reeds_hourly_clock_source_admission_2026.md).

## Why the signed-value boundary is necessary

The official [EIA-930 explanatory documentation](https://www.eia.gov/electricity/930-content/about.html) defines hourly integrated data and **hour-ending** reporting semantics. Local BA reporting time zones and DST reporting issues are explicitly documented. The present archived extraction already parses its period to UTC. Before any physical combination, the period field's exact interpretation must be reconciled with the source EFS chronology.

Negative hourly reported generation is retained in this audit; it is not imputed or silently clipped. If a `positive-only` aggregation is used, it must be labeled as such rather than substituted for the signed energy totals. Both sums are included separately with negative-hour counts.

The new script computes for each of 16 observed panels:
- Hour count, 1-hour UTC continuity and duplicated/missing detection;
- Signed reported net generation MWh, positive component MWh, and negative component MWh;
- Number of negative, zero, and positive observed net-generation hours;
- Within-week positive peak, signed mean/standard deviation and magnitude of 1-hour signed net-generation changes.

**None of these are generator capacity factors** because the audited BA fuel panel is not tied to a verified source-year generator fleet/nameplate population, and reported production may reflect operational dispatch/curtailment. Moreover, the four selected 2024 weeks do **not** represent an unbiased complete year.

## New acceptance and manuscript integration

- Source audit: `src/energy_transition/eia930_observed_shape_boundary.py`.
- Negative/duplicate/incomplete regression tests: `tests/test_eia930_observed_shape_boundary.py`.
- Official archive CI: [EIA-930 2024 signed shape boundary](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/eia930-observed-shapes-boundary.yml).
- Output: `observed_2024_eia930_four_week_ba_fuel_shapes.csv` and `observed_2024_eia930_shape_provenance.json`, including original input SHA-256 and explicit no-EFS-future-hour-join admission flags.

**Scientific use if CI passes:** a measured historical net-generation-shape descriptive supplement and a provenance/feasibility bridge to resource modeling, not a direct renewable input for the 540 future-year LP cases.

## Next external-data gate

To advance toward real future resource profiles, acquire independently sourced meteorological or wind/solar production-availability data with named weather year, site or zone geography, capacity normalization basis, complete hourly timestamps (including DST/leap handling), and permission/provenance. Match that to verified EFS source LocalHourID only through a separately audited weather-year/clock crosswalk. Keep observed net injection and available generation distinctly labeled.
