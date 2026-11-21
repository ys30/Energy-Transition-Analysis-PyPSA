# Paper S — Daily 4→8h energy-transfer proxy, authentic 2023 IPCO shape, and falsification gates

## Experiment 1 — within-day renewable surplus/deficit indicator, NOT dispatched MWh

**Code:** `src/energy_transition/paper_s_daily_transfer_proxy_and_ipco_shape.py` (`--mode daily`). From authentic 15 source weather years, original ReEDS county resource-class wind/PV curves, the 2025 operating-county versus source-resource-potential geographic weights, and **the existing fixed 2030 load on synthetic 2012 support**, independently compute per-reference-day:

`surplus_t=max(available_t−load_t,0)`, `deficit_t=max(load_t−available_t,0)`. Aggregate each to 24h blocks. With round-trip efficiency 0.9, installed battery power `P=0.25*peak_load`, usable deliverable-day potential `Q=min(0.9*sum(surplus),sum(deficit))` and deliverable from an internal battery energy capacity `4P*sqrt(.9)`, the proxy is

`max(0,min(Q,8P*sqrt(.9))−4P*sqrt(.9))`.

This produces a **per-day bounded numerical indicator**. It does NOT enforce chronological surplus-before-deficit, the charge/discharge power constraints, interday carryover, or all LP optimal dispatch degeneracies. It is NOT a feasible 4→8h shift, upper bound on full-year LP energy, certified storage mechanism, or empirical weather inference. Compute **240** year×state×weight×ratio cases (15×4×2×2 at wind=50%), **87,600** day rows, and 120 within-year spatial pairs. Match every candidate to the existing **1080 frozen duration-value rows** to examine explanatory alignment with actual LP incremental cost and firm displacement. Prespecify R=1.5 and R=2.0 separately; do not mix them. Report positive/negative direction for AZ/CO/ID/WY rather than assuming ID/WY positive and AZ negative.

## Experiment 2 — authentic 2023 ReEDS ID state shape versus 2023 EIA-930 IPCO BA wind/solar net MW

**Code:** same module `--mode ipco`. **Read original native 2023 weather-year indices directly from publisher HDF5**. DO NOT use synthetic 2012 supports created in the 15-year fixed-demand LP; 2023 is a calendar year with 365 days, originally native timezone-naive publisher **fixed CST UTC−06:00** labels. Explicitly localize original source labels before conversion to UTC; EIA-930 BA has UTC-hour-end report labels. Match by exact UTC label, no imputation, no invented time zone offsets. For solar, use the original utility PV AC normalization; normalization by matched sample mean removes overall scaling. Compute same-hour means and Pearson correlations, normalized MAE/RMSE, 24 fixed-CST mean-diurnal values, and 101-point descending duration curves for each source fuel and spatial weight. Contrast reported and source-adjusted EIA930 measurements, preserve nulls, and explicitly evaluate negative source MW variants separately.

**Critical population limit:** `IPCO` is Idaho Power's BA, **not** all Idaho state electricity production. The ReEDS aggregated Idaho curves represent source state resource classes and 2025 county fleet siting, **not a verified 2023 IPCO-specific cohort**, despite annual-mean normalization. No claim of 2023 installed fleet weight superiority, external predictive skill or proven ReEDS error follows unless BA-to-state physical reporting population is independently reconciled.

## Experiment 3 — falsification and scope QA

- `--mode ipco` reports original/adjusted source results at **0, ±1, ±6 hours**. ±1 hour detects sensitivity to the instantaneous CF versus hourly BA reporting semantics. ±6 hours are **deliberately incorrect clock placebo offsets**, not valid alignments. Do NOT optimize a clock lag and call it validation.
- Preserve source 2023 missing observations, source-negative output warnings, and report **exact matched valid denominator N** per technology/metric. All normalization is performed only on exactly identical matched non-null hours for both siting weights.
- The true source-year 2023 physical geography and **2025 county weights vs 2023 actual fleet mismatch** are reported; normalized curves do not fix geographic or vintage mismatches.
- Daily indicator is tested against actual preserved LP 4→8h firm substitution and objective. If AZ/ID/WY signs fail, falsify the simple daily surplus mechanism instead of presenting a selective story. A 15-year sign agreement is not causal proof.

## Source authenticated inputs and reproducibility

- Official publisher original county wind/PV HDF5/CSV pinned by MD5: wind CF `0670813d0a18b688d698ca24cf67fb92`, PV CF `aba834ea4c592023bca47de2ba79e7ec`, source wind county potential curve `49ab4e41dc386453b5fd32e5810774d4`, PV county potential curve `e10b1a64f3a67d163e739b735938eb78`.
- ReEDS fixed 2030 demand EFS reference MD5 `7b2055d43200744a16a8c4fed68b1a17`.
- Source-authenticated EIA 2025 county siting reference original GitHub run 43124063185.
- Frozen 3×3 1080 duration source run 44209543001, artifact 14388326204.
- Entire 2023 EIA-930 BA/source reported and adjusted hourly source from run 44246001519, artifact 14406998900.

**New workflow:** [#44461694202](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44461694202), `.github/workflows/paper-s-daily-mechanism-ipco-shape-2023.yml`. The workflow exists, tests and code are committed; **until job succeeds and artifact is read, DO NOT claim new experimental numerical results**. Existing 1,440 base LP, 360 mechanism LP, 2,880 3×3 LP, 720 R2 share-continuity LP and ATB results are unchanged. Paper C-2 remains independent.
