# Paper S — 2030 180-LP storage power-duration-mix run and cost hurdle (verified 11 Nov 2026 UTC)

## Status

Successful original data/solver/artifact run: [Actions 43051615043](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43051615043). Source-weather derived CSVs retained in artifact `paper-s-reeds2022-2030-county-180-storage-dimensions-and-hurdles`:
- `paper_s_reeds2022_2030_180_mix_power_duration_LPs.csv` (180 matched ReEDS2022 demand+source-profile optimum LPs);
- `paper_s_reeds2022_2030_144_storage_annuity_hurdles.csv` (144 distinct battery designs paired to 36 no-battery controls);
- `paper_s_reeds2022_2030_180_mix_power_duration_manifest.json`.

Checks: design/units tests passed, official original-demand MD5 checked, all 180 full-year LPs optimal, primal residual and storage cost-monotonicity gates checked, original Arizona 2030 wind50%/0.9×/4h/25% peak-power cost saving matched **$25,125,374.792839** within $0.10.

## Prespecified central case

2030 demand, 2012 fixed-CST reference weather, 1.5× peak demand assumed wind+PV nameplate, nominal source-denominator wind/PV 50:50, 4h storage at 0.25× peak charge/discharge power, 90% round-trip efficiency, trapezoidal numerical instantaneous-CF-to-hourly approximation with explicit first-hour fallback.

| State | Modeled annual variable operating cost avoided ($/year) | Battery power MW | Battery energy MWh | Break-even power-only annualized cost ($/kW-year) |
|---|---:|---:|---:|---:|
| Arizona | ~218,243,846 | 4851.25 | 19405 | 44.987136 |
| Colorado | ~64,082,810 | 2863.50 | 11454 | 22.379190 |
| Idaho | ~21,144,468 | 1301.00 | 5204 | 16.252474 |
| Wyoming | ~11,610,384 | 767.25 | 3069 | 15.132465 |

**Conditional annuity frontier:** $/kW-year power cost + 4 × $/kWh-year energy cost ≤ power-only break-even threshold. For an entirely illustrative energy-annuity assumption $10/kWh-year, remaining maximum $/kW-year is AZ ≈ $4.99, CO ≈ −$17.62, ID ≈ −$23.75, WY ≈ −$24.87. Negative values mean the assumed energy annuity alone exceeds the savings (under this model), not that true economics are negative in real power markets.

## Strong limitations for manuscript

1. Wind is modeled in wind source capacity units (approximately AC), while utility PV supply potential and CF denominator are DC. The 25/50/75% wind shares are heterogeneous source-nameplate shares, **not a calibrated common AC share**. Do not generalize the precise between-mix ordering to actual installed grid capacities.
2. The ReEDS county resource supply MW describes developable potential, **not installed or forecast fleet**; state-nameplate ratios are scenario controls, not inferred actual buildout.
3. Publisher 2012 hourly CF labels refer to **instantaneous** resource values. The 2030 modeled hour-energy proxy is numerically integrated with a first-hour boundary fallback and has not been publisher-certified as hourly generation energy.
4. The LP assumes fully independent state copperplates, no network, reserves, resource adequacy, minimum stable dispatch, or cross-state transfers. No battery CAPEX, augmentation, degradation, fixed O&M, financing, actual power-system tariffs or market capacity revenues are included in LP objective.
5. Break-even annuity values bound **modeled operating-value-only** from one 2012 reference weather realization. They are not bankable profitability estimates, current cost benchmarks, NPV, IRR or optimal storage procurement recommendations.
6. Earlier source-backed 144 renewable-penetration LP and 48 LP original source experiments are preserved independently. Legacy EFS2020 p-zone Paper S remains frozen.

## Next admission tasks

Create original-artifact-derived heat maps of wind share × battery design and optional energy-cost hurdle, then report whether 4h-to-8h energy raises operating savings enough to support incremental annualized cost. Address AC-normalized PV mixes and variation in round-trip efficiency before final article integration. Full repo CI currently includes a separate unresolved Paper T helper API mismatch; the specialized 180-LP workflow is successful.
