# Paper S main Figure 6 candidate — certified source-to-claim and required caption

**Execution status:** [Figure 6 original-archive matching / plot CI #42854783701](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42854783701) **success**. Previous [eight annual delivered-energy interval workflow #42747095388](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42747095388) and [four original 168-hour interval workflow #42780417107](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42780417107) were also successful. This plot is a verified **main-figure candidate**, not a finished, coauthor-approved or submitted manuscript figure.

## Source matched inputs

Both comparison bars use the **same** original LP:
- 2030 EFS original source-ordinal hourly demand, Arizona p28 or Wyoming p24;
- synthetic ordinal Wave A renewable availability;
- battery power `0.25 × source peak load MW`, energy `1.0 × source peak MW × 1h` (4h at rated power);
- original illustrative variable cost `C=5*(direct renewable MWh + renewable charging input MWh) + 90*(firm MWh)`;
- same original near-optimal cost cap `C(x)<=C*+max(USD0.05, 10^-9 C*)`, with zero original/terminal SOC and independent-zone LP constraints;
- annual interval `max annual discharge − min annual discharge` from one pair of secondary LPs, versus separately optimized window interval for **original LocalHourID 4001–4168** from a different secondary-LP pair.

Both percentages are `100*(max-min)/original HiGHS amount` **for that metric's own interval population**. The denominators differ: whole-year original discharged MWh versus the selected window's original discharged MWh. They are **not effect sizes on a shared denominator**, confidence intervals, or estimates of energy system reliability.

## Exact accepted CSV values

| 2030 source group | Original full-year delivered battery energy (MWh) | Annual min–max span (MWh) | Annual relative span (%) | Original source-window delivered battery energy (MWh) | Window min–max span (MWh) | Window relative span (%) |
|---|---:|---:|---:|---:|---:|---:|
| Arizona p28 | 5,216,555 (rounded) | 3.268170 | 0.00006265 | 108,166.156441 | 29,352.336139 | 27.136340 |
| Wyoming p24 | 76,868.91 (rounded) | 0.045027 | 0.00005858 | 260.529565 | 1,616.753223 | 620.564204 |

The full unrounded source values are delivered as Actions artifact `paper-s-proposed-main-figure-6-original-source-evidence`, in `paper_s_main_figure_6_two_source_comparisons.csv`.

## Proposed printed figure caption

**Figure 6. Aggregated annual storage discharge does not determine its within-year temporal allocation under the illustrative LP objective.** Comparison of the relative minimum-to-maximum discharged-energy range at the full-year scale and within a predetermined 168-source-hour interval (LocalHourID 4001–4168) for the Arizona p28 and Wyoming p24 original 2030 EFS projected-demand groups. In each case, separate secondary LPs independently minimized or maximized the displayed delivered-MWh metric subject to the same original objective ceiling `C(x)≤C*+max(USD 0.05,10⁻⁹C*)`, unchanged original resource/load/storage constraints, and cyclic terminal SOC. Bars show `(max−min)/original HiGHS discharge ×100`, on a logarithmic y-axis. Whole-year and window percentages **have different metric-specific denominators**. The case is a synthetic mathematical Wave-A resource scenario, not weather-observed renewable operation; `LocalHourID` is not physically authenticated UTC. The nonzero near-optimal allowance and numerical precision do not establish an exactly degenerate optimal face; no real grid reliability or investment consequence is inferred.

## Gate before final manuscript

- Avoid calling this figure `Figure 6` until the whole manuscript figure order is frozen. It is a **proposed final Figure 6**, separate from working-analysis Figure S6.
- Refine visual presentation if needed: annual fractions are around `0.00006%`; label in decimal rather than scientific notation where feasible, and explicitly note logarithmic axis.
- The Wyoming relative span exceeding 100% reflects a small baseline window MWh and an alternative maximum more than six times that baseline. Do not label it a >600% increase in *actual service*.
- Consider an accompanying **absolute MWh interval** table to prevent the percentage denominator distinction being overlooked.
- Verify journal-specific figure typography and the private manuscript's exact cross-references before publication; the public repo must not contain full private draft text.

Code: [validated figure generator](../src/energy_transition/paper_s_main_figure_6.py), [source-integrity test](../tests/test_paper_s_main_figure_6.py), [source-archive workflow](../.github/workflows/paper-s-main-figure-6.yml). Six-display selection context: [submission evidence matrix](PAPER_S_SUBMISSION_SIX_FIGURE_EVIDENCE_MATRIX_2026-11-10.md).
