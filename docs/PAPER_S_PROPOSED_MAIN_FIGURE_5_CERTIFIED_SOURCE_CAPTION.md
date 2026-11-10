# Paper S proposed main Figure 5 — accepted independent MW/MWh mechanisms (2026-11-10)

**Status: original-archive-derived figure, automated source certification and rendering passed.** Figure 5 workflow [#42857238238](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42857238238) restored **two independent accepted artifacts** — original 189-LP / 252 one-axis contrasts [#42674534963](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42674534963) and the source-verified 84 adjacent 2×2 interaction cells [#42675999423](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42675999423). These are **not independent new LP replications** made during plotting.

## Proposed journal Figure 5 caption

**Figure 5. Independent storage power and energy ratings change the marginal delivered-energy response and their modeled cross-effect.** (A) Counts of unique source-demand temporal shapes among seven for which raising the energy storage capacity from 0.5 to 1 or from 1 to 2 peak-MW-hour equivalents increases annual delivered battery discharge at fixed battery power = 25% of source-zone peak demand. (B) Equivalent positive-response counts for increasing battery power from 12.5% to 25%, or 25% to 50%, at fixed capacity = one peak-MW-hour. (C) Number of positive and near-zero four-corner interactions of the **illustrative variable operating LP cost**, based on independent adjacent power and energy increases, for each of three synthetic resource availability profiles (28 interactions per supply shape). Positive means that increasing MWh saves more toy variable cost at higher power; near-zero is determined by a numerical USD 1 threshold and is **not** a statistical significance category. All results use the original 2030 EFS source-ordinal projected demand, seven distinct nonzero peak-normalized demand shapes and assumed flat or synthetic ordinal-wave renewable profiles; they do not estimate real grid storage value, investment returns, reliability or physical UTC effects.

## Verified values

| Synthetic supply | More E, P fixed 25%: 0.5→1 | More E, P fixed 25%: 1→2 | More P, E fixed 1: 12.5%→25% | More P, E fixed 1: 25%→50% | Positive interactions / 28 | Near-zero interactions / 28 | Negative interactions (<−USD 1) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Flat | 1/7 | 1/7 | 6/7 | 0/7 | 1 | 27 | 0 |
| Ordinal wave A | 7/7 | 6/7 | 7/7 | 1/7 | 20 | 8 | 0 |
| Ordinal wave B | 7/7 | 6/7 | 7/7 | 0/7 | 15 | 13 | 0 |

One-axis positive responses are judged by `added_discharge_mwh > 0.001`. The cost interaction is defined
`I = [C(P_hi,E_lo)-C(P_hi,E_hi)] - [C(P_lo,E_lo)-C(P_lo,E_hi)]`.
A value `I > USD 1` is positive; `I < -USD 1` is negative; else classified as numerical near zero. The definition is independent of storage investment economics. All 84 interactions match their corresponding archived four-corner cost differences and component-accounting checks.

The 20 original zones are *not* 20 independent temporal replicates: the original 2030 EFS source contains 19 positive-load zones with **seven unique** normalized demand patterns. Each source-demand shape is counted once. These seven shapes should not be treated as independent random samples and their counts must never be called statistically significant proportions.

## Figure source and limitations

The actual plot file `Paper_S_proposed_main_Figure_5_independent_MW_MWh.png` plus SVG and numerical CSVs are archived by [workflow #42857238238](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42857238238), artifact `paper-s-proposed-main-figure-5-independent-mw-mwh`. Rebuild using [generator](../src/energy_transition/paper_s_main_figure_5.py), [integrity tests](../tests/test_paper_s_main_figure_5.py), and [GitHub workflow](../.github/workflows/paper-s-main-figure-5.yml).

- Plot panel A/B are **descriptive counts**, not uncertainty intervals. Panel C counts **cost interactions** rather than MWh discharge outcomes; avoid conflating these different response variables.
- The input source is 2030 projected demand and deliberately synthetic equal-mean renewable availability; no observed wind/PV availability, no source-verified physical UTC, no full Western transmission-constrained OPF.
- Battery capex, replacement, lifetime, degradation and market financing are not included, hence neither design nor cost differences define an economic optimal size.
- Main Figure 5 is one *candidate* in the private manuscript six-display editorial plan; manuscript figure numbering is not yet submission-frozen. Retain the existing full Figure S13 heatmap in the supplement for the source-shape-specific interaction magnitude distribution.

## Manuscript status

In the proposed six-main-figure organization, source-grounded Figure 1, Figure 5 and Figure 6 are now rendered and independently CI-verified. Figure slots 2–4 still require final editorial selection, renumbering, and journal-compatible figure/caption production. The private full manuscript has **not** been automatically updated or published by this public-document addition.
