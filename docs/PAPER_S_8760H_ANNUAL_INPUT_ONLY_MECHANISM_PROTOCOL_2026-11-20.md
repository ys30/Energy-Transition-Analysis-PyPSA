# Paper S — same-8760h source-only optimal storage-transfer mechanism pilot (2026-11-20)

## Scientific rationale
The previously verified 24h greedy policy and two handpicked 168h windows failed to provide robust explanations of the annual spatial value effect across AZ/CO/ID/WY. The new calculation uses **identical 8,760 hourly source arrays** under all SOC horizons, making it possible to isolate SOC boundary conditions without comparing week-long mechanistic aggregates with annual energy amounts.

## Precisely what is optimized
For a battery rated P = 0.25 × max annual 2030 fixed reference load (MW), durations 4 and 8h, and η_charge=η_discharge=sqrt(0.9), maximize the **unpriced renewable surplus delivered into subsequent deficit hours**. Available source is defined by R×annual peak×AC-normalized combined wind/PV CF, with wind share 50%. Only surplus to load is eligible for battery charging and only load deficit is eligible for discharge. Charge and discharge are each bounded by the same power rating; SOC recursion is enforced each hour. This is an input-only energy-only LP, NOT avoided-firm-cost or merchant-profit dispatch.

Three optimization cases for the same 8,760 hours:
- **Daily**: terminal zero SOC every 24h (365 intervals)
- **Weekly**: terminal zero SOC every 168h (52 intervals plus last 24h tail)
- **Annual**: zero initial and terminal SOC over one 8,760h interval

At each duration total delivered MWh must satisfy annual >= weekly >= daily, since the feasible sets are nested. However the **incremental** 8h minus 4h MWh is not necessarily monotonically increasing across boundary scenarios; differences in differences must not be artificially constrained.

## Study design and sample admission
- The initial end-to-end **pilot** is all four prespecified states (AZ R=1.5, CO R=2.0, ID R=1.5, WY R=1.5), two originally included weather years (2012 and 2023) and two original frozen county weights. This is **16 full-year source cases** and **96 LP optimizations**.
- Four independent state matrix jobs prevent a single slow or failing state hiding the others.
- Every input follows the authenticated publisher HDF5, supply-curve hash, original 2012 source time support, 2030 EFS load source identity, and prevalidated county weights.
- The 16 cases are a **runtime/feasibility pilot**, not an adequate climate-year or population-wide test. Do NOT calculate/report Pearson correlations over n=2 as evidence of a mechanism.
- If all pilot gates succeed, extend this same workflow to all 15 source-weather years × two weights × four predeclared state/penetration scenarios (120 full-year cases and 720 LPs) with year-batch sharding. Preserve both signs and nulls; do not select favorable years.

## Fail-closed checks and outputs
- The source original 1,080 duration LP value CSV is filtered to wind share exactly 50%; each selected case joins 1:1 by weather year, state, siting and ratio.
- Validate hourly mass balance, SOC upper limit and terminal zero for *all* daily/weekly/annual boundaries.
- Source-year record counts, unique case keys and absence of partial CSVs are required.
- `Y1_annual_input_only_case_results.csv`: absolute MWh energy at 4/8h and three horizon schedules, annual source surplus/deficit and the frozen annual economic LP value.
- `Y2_annual_paired_siting_effects.csv`: EIA-minus-potential matched 4→8h source-only MWh effects and matched annual economic value effect.
- `Y3_annual_group_summary.csv`: pilot counts only (no statistically interpretable multi-year correlation unless expanded to all 15 years).
- `Y0_manifest.json`: source scope, horizon semantics, caveats and immutable input-data policy.

**Current admission:** code and workflow authored, await successful CI and original artifact audit. Original 213/1080 cheapest ATB threshold crossings and two-window falsification findings remain unchanged.
