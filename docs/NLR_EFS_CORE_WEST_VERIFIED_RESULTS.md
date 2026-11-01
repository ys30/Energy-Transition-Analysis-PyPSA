# Verified EFS 2030/2040/2050 core-Western hourly demand

**Verified GitHub Actions:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41261290082

- Real NLR EFS Reference / Moderate source downloaded with pinned PyPSA-USA v0.8.0 workflow.
- Source CSV: 35,320,320 records; years 2018, 2020, 2024, 2030, 2040, 2050; 48 states.
- The full CSV has nonnegative finite LoadMW values and no source scenario mismatches.
- Genuine core-Western 11-state aggregation completed for 2030, 2040 and 2050.
- State-year-local-hour output pairs: **289,080**, equal to 11 × 3 × 8760; 4,047,120 source sector/subsector records included.
- Artifact: `efs-core-west-2030-2040-2050-hourly.csv.gz`.
- Associated verification: `efs-core-west-2030-2040-2050-audit.json`.
- CSV columns: year, state, local_hour_id, load_mw.
- Geographic scope: AZ, CA, CO, ID, MT, NM, NV, OR, UT, WA, WY. This is a **core 11-state study pilot**, not proven to cover the full PyPSA-USA Western interconnection.

**Do not claim real Western PyPSA multiyear solves yet.** Outstanding gates:

1. `LocalHourID` is source-local hour ordinal, **not** independently verified UTC or DST-aligned snapshot time.
2. Actual ReEDS membership, `LAF_state` weights, and 35-zone weighted conservation are **not** empirically verified.
3. The upstream `data_model` Snakemake DAG can be parsed (29 tasks) but the complete network `elec_s75_c33_ec_lv1.0_REM-3h_E.nc` has not been built.
4. Source EFS scenario, regional constraints and spatial-temporal semantics must be reconciled before calibration and historical comparison.

For transparent job-portfolio presentation, cite the successful CI run above and distinguish **empirically sourced demand preparation** from **synthetic PyPSA dispatch**.
