# Paper S — audited chronological input-only battery mechanism results (2026-11-19)

## Verified source and scope
Successful GitHub Actions [44570259601](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44570259601), artifact **14561049536**, on PR #2 SHA `6b1e1c1d53363b68f8ae98f6e8cc129e117faf91`. Input pinning, unit tests, source population guards and output CI gates succeeded. Directly inspected the zipped `daily/C1–C5` and previous `D4` CSVs: **240** fixed-2030 source cases, **87,600** days, **120** same-weather year paired siting effects, **8** state×penetration reports, each with **15** source weather years. R=1.5 and 2.0, fixed wind share 50%.

## Principal falsification result

Pearson correlation of within-weather-year EIA2025-minus-ReEDS-potential spatial effects with the *same-year original LP* value effect:

| State | Ratio | Prior order-blind daily proxy Pearson r | New feasible chronological greedy policy Pearson r | Prior sign agreements /15 | New sign agreements /15 | New median policy spatial effect (MWh) | Actual paired LP value spatial effect median USD/(added kWh-year) |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZ | 1.5 | 0.9259 | 0.0194 | 12 | 9 | -45,973.88 | -0.3409 |
| AZ | 2.0 | 0.7644 | 0.0029 | 10 | 8 | -84,575.55 | -0.1686 |
| CO | 1.5 | 0.6430 | 0.3687 | 13 | 12 | +31,997.58 | +0.4104 |
| CO | 2.0 | 0.8357 | 0.3884 | 15 | 14 | -30,861.85 | -2.1779 |
| ID | 1.5 | 0.8859 | 0.1439 | 15 | 15 | +8,281.65 | +2.3377 |
| ID | 2.0 | 0.8979 | 0.4977 | 13 | 11 | +11,167.60 | +0.6880 |
| WY | 1.5 | 0.9743 | 0.8265 | 15 | 15 | +28,249.02 | +2.6365 |
| WY | 2.0 | 0.9477 | 0.3585 | 14 | 14 | +8,415.69 | +1.0106 |

Total sign agreements drop **107/120 -> 98/120** (these are descriptive paired years, NOT independent randomized samples). Correlations diminish markedly in AZ and ID and remain comparatively strong only in WY at R=1.5. Sign agreement can be driven by near-uniform positive or negative effects across both series, so its high value **does not imply robust explanatory prediction of within-year variations**.

### Mechanism hierarchy
1. The un-ordered daily surplus/deficit proxy produced high associations but ignores chronology.
2. The chronological rule respects hourly renewable-only charging, charging/discharging inverter power, and 0–E SOC; **resets to zero each day** and discards stranded end-of-day energy. It is a *feasible greedy policy*, not optimal. It does not allow interday carryover; it cannot claim the overall optimal full-year incremental shift.
3. The original annual LP can optimize dispatch over the year, use interday SOC, and allocate charging differently to a greedy daily policy. Consequently weakening in r is evidence against the **specific greedy day-restricted physical explanation**, not proof that chronology/energy availability as a whole has no role.
4. Do not claim independence in the statistical identification sense: both policy and LP share ReEDS 2030 fixed load, original weather-year CF inputs and two spatial weighting vectors, and both reflect coupled deterministic system physics.

### Paper S manuscript admission decision
- **Main text**: state the input-only proxy was partially falsified by feasible hour-order restrictions and that the mechanisms are heterogeneous by state/penetration. WY at R=1.5 is the strongest support; CO R=2.0 has directional concordance but only r=0.388.
- **SI**: full 8-group table, 120 paired cases, end-of-day SOC discarded, baseline greedy protocol and negative controls. Explicitly distinguish median-of-paired-effects from difference of medians.
- **Do not** present the order-blind proxy r=0.76–0.97 as physical validation across all states. Do not use optimized firm generation or curtailment as independent mechanisms because they appear algebraically in the objective.
- **Next decisive robustness**: run a non-greedy chronology-constrained *input-only maximum feasible renewable-only delivery* problem with **common terminal SOC treatment**, per-day versus year-long horizon, identical source inputs for 4h/8h, and record sensitivity to carryover. Even that optimizes energy, not economic value, and remains a *mechanism indicator*, not causal identification.
- **Economics remains separately verified**: original 3×3 × ATB thresholds yielded 213/1080 unique LP scenarios crossing the cheapest hurdle; these are conditional illustrative comparisons, NOT real profit or investment NPV.

Preserve the earlier 1440/360/2880/720/2160 artifacts, Paper T and Paper C-2.
