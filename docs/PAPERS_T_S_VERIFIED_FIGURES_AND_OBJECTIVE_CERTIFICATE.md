# Paper T / Paper S editorial and numerical evidence lock (November 2026)

Two separate **private working manuscripts** are the editorial outputs. This public source repository carries **only code, provenance metrics, tests, and reproducible figures**, not the manuscript text.

## Paper T — independently rebuilt figures from passing source archives

[Publication-figure CI #42145896229](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42145896229) **passed**. It ingests two previously successful original-source artifacts, with no hardcoded fit values:

1. [Nonwrapping lag 33-state-year archive #42122065064](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42122065064) → **Figure T2** `figure_T2_source_lag_2030.svg/png`: a source-index displacement and best-lag residual chart with Idaho visibly distinguished. The residual x-axis is *log-scaled* in MW. Best lag is a numerical index, **not certified physical EFS2020 UTC**.
2. [Original Idaho frozen Transport candidate #42131969905](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42131969905) → **Figure T4** `figure_T4_frozen_shift_holdout.svg/png`: pre-specified source-index shift first-half versus held-out-half MAE effect, including negative improvements for 2040/2050 first halves. No year-specific re-selection during evaluation.

Download artifact **`paper-t-source-lag-and-idaho-heldout-publication-figures`** from the passing Actions run. Script `src/energy_transition/paper_t_source_figures.py` and regression tests `tests/test_paper_t_source_figures.py`. Source population gate requires exactly 33 pairs (11 states × 3 years) and exactly 3 frozen-rule evaluation years. Original EFS source-clock meanings and Idaho timezone mapping remain unresolved.

## Paper S — exact 540-case objective, conservation and terminal-inventory certificate

[Independent certification CI #42146086492](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42146086492) **passed** on the original archived 540 zone-year-resource-duration HiGHS LP results from [#42107237659](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659). This is an *independent postprocessing check* against the original unmodified result CSV.

The exact code-implemented illustrative objective for each case is:

```text
min sum over ordinal hours [5 USD/MWh × (renewable directly serving load + battery charge input)
                           +90 USD/MWh × firm energy serving load]
```

The **$5 coefficient counts charged renewable input as well as direct renewable delivery**. Battery discharge, unused assumed renewable potential and state of charge have zero direct objective coefficients. The model does not include battery CAPEX, degradation, market or electrical network costs; the result is not real storage value.

All original 540 cases passed these checks:

| Independently reconstructed metric | Largest absolute error |
|---|---:|
| Toy objective (USD) | **0.00022221** |
| Source renewable energy identity (MWh) | **0.00000580** |
| Source load-serving energy identity (MWh) | **0.00000579** |
| Cyclic battery 90%-roundtrip energy identity (MWh) | **0.0000002254** |
| End-of-horizon stored energy (MWh) | **0** |

The battery identity is **total delivered battery MWh = 0.90 × total battery charging input MWh** because terminal minus initial SOC is zero and the charge/discharge efficiencies both equal `sqrt(0.9)`. This is a mathematical energy identity for the *specific model*, not a measured real battery-efficiency result.

Script: `src/energy_transition/paper_s_lp_objective_certification.py`; regression tests: `tests/test_paper_s_lp_objective_certification.py`; archived JSON artifact: **`paper-s-540-case-objective-conservation-certificate`**.

Previously verified source-derived three SVG/PNG publication figures for Paper S remain in [passing CI #42108416559](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42108416559), artifact `efs-540-lp-evidence-labeled-publication-figures`. Figure mapping: `fig1_2030_model_unused_supply` → primary supply-shape/duration Figure S2; `fig2_wave_A_three_years` → main three-year Figure S3; `fig3_incremental_2030_firm` → optional supplementary figure.

## Editorial next actions (only essentials)

- Paper T: original EFS2020 publisher time-convention sourcing and release-lineage limitations; optional compact source-derived Idaho reference-clock heat map; related-work and bibliography check.
- Paper S: present the exact certified toy objective and 90%-efficiency constraints in mathematical Methods; retain the *synthetic* supply disclaimer on every figure and use credible methods/sensitivity framing rather than empirical Western storage economics.
- Keep private drafts off public GitHub and avoid implying that either research manuscript is journal-ready.

**Neither audit authenticates a physical wind/solar weather join, real future generation profiles, Idaho timezone causality, or transmission-constrained Western network OPF.**
