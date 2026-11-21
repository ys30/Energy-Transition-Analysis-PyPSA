# Paper S: all 15 original weather years, year-aligned storage-transfer mechanism — audit (2026-11-20)

## Verified source execution and local postprocessing
Run [44849783992](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44849783992) succeeded for **12/12** state×five-weather-year source partitions; each successfully uploaded immutable `Y0–Y3` artifacts. The final aggregation job **failed**, because each partition's Y1 CSV already carried the original frozen-LP marginal-value field, which the aggregator joined again and Pandas renamed to `_x/_y` fields. This is a **postprocessing join error, not an LP failure**. Fixed in `paper_s_input_only_annual_optimal.summarize()` by comparing pre-existing partition LP values against frozen original values before retaining one authoritative source column. Regression test rejects mismatched saved vs frozen values.

The 12 original artifacts were downloaded and directly reassembled independently for an immediate numerical audit: **120 unique full-year (8760h) source cases**, 60 original-weather-year EIA-minus-source-potential matched spatial contrasts, 15 weather years per state; 720 duration×boundary energy LP solves. Every fixed-duration annual≥weekly≥daily feasible-set inequality passed; maximum original solver SOC equality residual **7.276e-12 MWh**. The official GitHub-only aggregate-recovery workflow may still be queued or may require separate verification; do not mark its result successful until observed.

## Verified year-aligned descriptive figures

| State, R | 24h SOC reset: r | 168h SOC reset: r | 8760h continuous: r | 24h sign | 168h sign | Continuous sign |
|---|---:|---:|---:|---:|---:|---:|
| AZ, 1.5 | +0.019414 | +0.958747 | +1.000000 | 9/15 | 13/15 | 15/15 |
| CO, 2.0 | +0.388377 | +0.954618 | +1.000000 | 14/15 | 15/15 | 15/15 |
| ID, 1.5 | +0.143886 | +0.963586 | +1.000000 | 15/15 | 15/15 | 15/15 |
| WY, 1.5 | +0.826549 | +0.952937 | +1.000000 | 15/15 | 15/15 | 15/15 |

Across 60 within-weather-year county-weight spatial pairs: 24h reset sign 53/60, weekly reset 58/60, continuous SOC 60/60.

## Essential correction — r=1 is objective equivalence, NOT independent mechanism confirmation

The continuous full-year physical-delivery optimum is an almost *exact state-specific linear rescaling* of the original yearly economic LP siting value contrast. Fitted affine slope (USD per added kWh·year, per physically shifted MWh), intercept and max within-state residual:

| State | Slope | Intercept | Max absolute residual (USD/added kWh·year) |
|---|---:|---:|---:|
| AZ | 4.35168484598e-6 | -1.427e-11 | 6.076e-10 |
| CO | 7.37248510949e-6 | -1.410e-11 | 6.453e-11 |
| ID | 1.62268340668e-5 | -1.214e-9 | 1.200e-9 |
| WY | 2.75152963331e-5 | -1.058e-10 | 4.238e-10 |

The original model minimizes a linear, fixed-price energy cost with an illustrative $90/MWh firm supply and $5/MWh renewable dispatch. Under this set of constraints, maximize shifted renewable-surplus MWh can be an equivalent optimization objective to minimizing avoided firm/renewable variable cost. Both share identical original demand, wind/PV source arrays and energy constraints, making near-perfect correspondence *structural*. It must **never** be reported as independent causal proof, real-world predictability, price validation, or observed storage economic returns. At present it is a correct and informative **model identity, consistency and SOC horizon finding**.

Crucially, weekly SOC r≈0.95–0.96 in all four state-specific 15-year groups, while same-year daily reset correlations vary. This demonstrates that constrained SOC horizons materially affect the ability to reproduce the original economic model's annual margin, but cannot distinguish economic-price physics with a fixed marginal cost. The earlier two 168h windows are not representative of annual week-by-week accumulation and should remain supplementary falsification/sensitivity results.

## Manuscript decision
- **Admit** the 120-case annual numerical results as model-consistency/horizon sensitivity, with source-pinned artifacts, numerical accuracy and clearly labeled objective equivalence.
- **Reject** the tempting false claim that 60/60 sign matches or r=1 constitute independent validation.
- The fixed-2030 3×3 sensitivity and original ATB 213/1080 lowest-hurdle crossings are unchanged, illustrative and require no rerun.
- Next independently informative experiment must introduce a *non-proportional outcome* (exogenous time-varying price/firm scarcity or alternative charging/terminal constraints) or actual out-of-sample dispatch observations. Predefine the test, including adverse/negative results, without adjusting thresholds post hoc.
- When the separate aggregate-recovery GitHub job succeeds, reconcile its official CSV and figures to these original downloaded partition artifacts before manuscript finalization.

## Provenance
- Original 12 source partitions: [run 44849783992](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44849783992).
- Recovery from original artifacts: `.github/workflows/paper-s-recover-annual-all15-aggregate.yml`.
- Original models: `paper_s_input_only_annual_optimal.py` and `paper_s_input_only_weekly_optimal.py`.
