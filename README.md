# Energy Transition Analysis — PyPSA-ready Portfolio

[![CI](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml/badge.svg)](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/ci.yml)

A reproducible, visualization-first study of **illustrative** electricity transitions across 2025–2040. It reports generation mix, renewable generation share, and operational CO₂ emissions. The analytical pipeline is designed for future integration with PyPSA optimization outputs.

> **Evidence boundary:** All current scenario values are synthetic assumptions, **not empirical energy statistics and not PyPSA optimization results**. The title indicates the intended modeling ecosystem, not a claim that PyPSA currently solves these scenarios.

## Questions

1. How does the generation mix change under a stylized transition?
2. What is the renewable share of annual generation?
3. How do operational emissions change using explicitly documented factors?

## Reproduce

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m energy_transition --output outputs
jupyter lab
```

Figures: `outputs/generation_mix.png`, `outputs/renewable_share.png`, and `outputs/emissions.png`. Numerical data: `outputs/metrics.csv` and `outputs/generation_twh.csv`. The CI workflow saves generated figures as an artifact.

## Assumptions and methods

Annual generation totals are fixed at 100 TWh. Synthetic coal, gas, wind and solar generation for 2025/2030/2035/2040 are hardcoded in `scenario_data()`. Renewable share = (wind + solar) / total generation. Emissions = sum(generation in TWh × emissions factor in tCO₂/MWh), yielding MtCO₂. Illustrative direct operational factors are coal 0.9 and gas 0.4 tCO₂/MWh, wind and solar zero. These are **illustrative factors, not measured regional lifecycle intensities**. No dispatch, network, investment, or policy optimization is performed.

## Next research phase

Replace illustrative annual generation with a **versioned PyPSA output adapter** (`generators_t.p` × snapshot weights, technology mapping, carrier emission factors, and region definitions); then compare scenarios with identical assumptions and explicitly separate solved outputs from scenario inputs. Add system costs, capacity expansion, curtailment, spatial analysis and uncertainty intervals only when supported by actual model outputs.

## Repository contents

- `src/energy_transition/analysis.py`: scenario data, metrics, plots
- `notebooks/01_analysis.ipynb`: interactive execution
- `tests/`: regression and figure-generation checks
- `.github/workflows/ci.yml`: automated testing and figure artifacts

## Interpretation

Figures are examples of **how** transition results can be communicated, not evidence of an actual transition forecast.


## New: Western US EIA-930 demand-driven PyPSA workflow (experimental)

See [the Western US EIA-930 study guide](docs/western_us_eia930.md) for download and optimization commands, geographic coverage, assumptions, and evidence limits. This workflow has **not** yet produced a verified EIA-based optimization result; it does not supersede the synthetic plots described above.
