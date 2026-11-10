# Paper S — verified linear discharge-throughput sensitivity (10 November 2026)

**Evidence status:** [GitHub Actions #42907978370](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42907978370) **SUCCESS**, including Arizona p28 and Wyoming p24 independent 8,760-hour LPs, unit tests, archival checks, and six-case synthesis. 18 LP schedules (two original source-demand groups × three discharged-MWh penalty levels × original baseline/min/max fixed-window discharge) were solved. The complete private manuscript v5 is maintained outside this public repo.

## Experimental definition

At each explicit rate `p=0,1,10 USD per discharged battery MWh`, re-solve the primary source-hour LP using `Cp=C0+p*sum_t(d_t)`, where `C0=5*sum_t(r_t+c_t)+90*sum_t(f_t)`. Then independently minimize/maximize battery discharge in predeclared source hours 4001–4168 under **the matched cost ceiling** `Cp(x) <= Cp* + max(USD 0.05,1e-9 Cp*)`. Source: accepted original 2030 EFS source demand, synthetic ordinal Wave A, P=0.25 source peak MW and E=1 source peak MW-hour, 90% roundtrip, zero terminal SOC. For p=0, original optimal objective and window extrema independently reconcile with the existing source archives.

## Source-verified results

| Zone | Assumed penalty per discharged MWh (USD) | Feasible window discharge span (MWh) | Fraction of p=0 span |
|---|---:|---:|---:|
| Arizona p28 | 0 | 29,352.336139 | 100.000000% |
| Arizona p28 | 1 | 29,350.252566 | 99.992902% |
| Arizona p28 | 10 | 29,349.268735 | **99.989550%** |
| Wyoming p24 | 0 | 1,616.753223 | 100.000000% |
| Wyoming p24 | 1 | 1,616.749570 | 99.999774% |
| Wyoming p24 | 10 | 1,616.733132 | **99.998757%** |

The primary optimized annual discharged energy stayed unchanged to the original archive display precision at all three specified rates: Arizona ~5,216,555 MWh, Wyoming ~76,868.9 MWh. Baseline window discharged MWh similarly remained about 108,166.156 (Arizona) and 260.530 (Wyoming). **These are fixed-source, deterministic toy-LP results, not independent observations of battery assets.**

The window-discharge feasible range retains almost all of its original width even when the illustrated primary objective explicitly penalizes discharged throughput at USD 10/MWh. This argues against lack of any throughput price being the sole cause of observed temporal allocation non-identification. It **does not establish** robustness to calibrated battery degradation, cycle-depth-dependent lifetime models, explicit charge/discharge exclusivity constraints at each penalty rate, thermal/calendar aging, warranty operating limits, real weather or reserve/Western transmission-constrained OPF.

## Key source and figure references

- [Opt-in augmented-source solver](../src/energy_transition/efs_cyclic_storage_lp.py): default p=0 preserves original solver objective and outcomes; secondary cost ceiling uses Cp when p>0 and is explicitly rescaled to that primary objective.
- [18-LP experiment](../src/energy_transition/paper_s_throughput_penalty_sensitivity.py) and [unit tests](../tests/test_paper_s_throughput_penalty_sensitivity.py)
- [Original-source archival CI](../.github/workflows/paper-s-throughput-penalty.yml), successful run 42907978370, source artifact `paper-s-six-accepted-throughput-penalty-window-envelopes`.
- [Predeclared methodology and limitations](PAPER_S_THROUGHPUT_PENALTY_COST_CAP_PROTOCOL_2026-11-10.md).

The privately generated Supplementary Figure S2 plots **retained window span / original no-penalty span (%)**, separately for Arizona and Wyoming, alongside an 18-schedule source result CSV and six-interval table. Do **not** add the full private Word manuscript or raw EFS licensed data to this public repository.

## Publication claim to admit

> Under a small positive original-cost sublevel set, the fixed source-hour discharge delivery interval remains wide when the illustrative objective is augmented by a linear discharge-throughput penalty of up to USD 10/MWh. The 168-source-hour window range retained 99.9896% (Arizona) and 99.9988% (Wyoming) of the no-penalty spans, under the fixed synthetic source assumptions. These rates are experimental sensitivity values rather than calibrated degradation costs.

**Remaining scientific gates:** verify source clock/rights; measure robustness to a physically specific depth-of-discharge aging function and tighter operations; compare with existing MGA prior art; final journal source-to-claim and full bibliography audits. A near-optimal envelope is not proof of alternate *exact* LP optima or real dispatch reliability.
