# Paper T — hypothetical downstream sensitivity (illustrative only)

**Status:** synthetic-only demonstration, not EFS/ReEDS physical-hour join and not an empirical grid simulation.

## Question and setup
Could a 2–3 hour numeric time shift alter downstream resource-load alignment even with unchanged annual totals?

We construct *both* illustrative demand and solar curves on a synthetic 365 x 24 hourly index (8760 slots, no time-zone/DST claim), with units in arbitrary normalized MW. Demand has a summer seasonal uplift and daily morning and evening peaks. Solar has a summer seasonal uplift and a daytime clear-sky bell. We keep solar fixed and advance only synthetic demand, at lag 0, -2, or -3 hours. Negative lag means a demand value at hour t+2 is assigned to index t. Circular-year shifts deliberately preserve annual energy; these are not physical-hour timestamp conversions.

Coincidence fraction = sum_t min(demand_t, solar_t) / sum_t solar_t.
Potential solar surplus = sum_t max(solar_t - demand_t, 0).
Net-load peak = max_t(demand_t - solar_t).
These are **descriptive proxies**, not curtailment or actual dispatch.

## Reproducibility
```bash
python research/paper_t_hypothetical_downstream/paper_t_downstream_sensitivity.py --outdir results/paper_t_hypothetical_downstream
python -m unittest discover -s research/paper_t_hypothetical_downstream -p 'test_*.py' -v
```

## Illustrative output (locally verified; repository CI not yet verified)
| Demand lag | Net-load peak MW | Change from 0 h | Solar overlap | Potential solar surplus MWh |
|---|---:|---:|---:|---:|
| 0 h | 1300.000 | reference | 96.535858% | 87637.421 |
| -2 h | 1285.703 | -1.099758% | 97.625887% | 60061.376 |
| -3 h | 1246.773 | -4.094388% | 98.518545% | 37478.499 |

**Interpretation:** Hourly misalignment can alter synthetic peak net load and a simple contemporaneous solar-load proxy without affecting either annual energy total. The direction and size of the effect are *assumption-dependent*. They do not estimate Idaho's observed change, causal impact, costs, operational adequacy, or the real temporal relationship of EFS2020 and ReEDS2022. The project's temporal join admission gates remain blocked.

## Proposed manuscript wording
*To illustrate potential downstream consequences without asserting a physical-hour join between the audited releases, we constructed a fully synthetic 8,760-index demand series and a separate synthetic solar series. We advanced demand by 0, 2, or 3 index hours relative to unchanged solar, maintaining both annual energy totals by circular indexing. In this illustrative configuration, peak net demand decreased by 1.10% and 4.09% under the two shifts, while the solar-overlap fraction rose by 1.09 and 1.98 percentage points, respectively. These are scenario-specific illustrations of timing sensitivity, not estimates for Idaho or a validated ReEDS/EFS source-clock transformation. All empirical temporal-join admission restrictions remain in force.*
