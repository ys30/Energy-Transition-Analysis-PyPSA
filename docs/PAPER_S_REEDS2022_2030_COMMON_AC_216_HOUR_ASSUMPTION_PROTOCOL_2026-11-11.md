# Paper S — source-instant versus hour-energy approximation, common AC 216-LP audit protocol (11 November 2026)

## Scientific question

For ReEDS2022 2012 county-source weather and projected 2030 state demand, does the numerical procedure for using original source-instant wind and utility PV capacity factors as hourly renewable energy availability materially alter the operating-value ceiling of four-hour storage or the 4→8-hour incremental energy annuity hurdle? The key admission issue is that the original instantaneous weather-hour label and demand hour-ending convention do **not** certify that weather CF equals the prior-hour average renewable generation.

## Locked source inputs and experiments

The exact independently authenticated and archived 2012 original weather state-CF records (run [42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548)) and ReEDS2022 publisher demand HDF5 with original MD5 `7b2055d43200744a16a8c4fed68b1a17` are used in both modes. Weather and demand native fixed-CST labels are strictly checked. The ReEDS 2012 native reference sequence contains 8760 records including leap day, **excluding December 31**, so the model has neither a conventional complete leap year nor independent verification of hour-boundary interval integrals.

The renewable portfolio is held **common AC nameplate**, using original wind AC CF and one-time conversion of original PV AC-grid/DC-array CF by publisher ILR=1.34; PV value >1 is capped within only documented rounded precision tolerance. Scenario total wind+PV AC nameplate to peak load is 0.9, 1.5, 2.0; wind AC capacity fraction is 25%, 50%, 75%. An assumed battery of power 25% of peak is tested at 0h (no battery), 4h, 8h, 90% round-trip efficiency. Marginal variable-cost assumptions are renewable $5/MWh and firm $90/MWh. No installed-fleet, transmission, capacity adequacy, future weather distribution, reserve scarcity, O&M or battery CAPEX calibration is attempted.

Two numerical interpretations of identical original instantaneous source CF are compared:
1. **End-instant hold:** use source CF at time t as the hourly availability for that t, which is a point-sampling approximation, not publisher-certified interval average.
2. **Trapezoid with first endpoint fallback:** at hour t>0 use [CF(t-1)+CF(t)]/2, at t=0 use CF(0) with *no* implied periodic wrap around the truncated year. The boundary treatment is an explicit unobserved approximation.

Experiment 4 states × 3 renewable penetration ratios × 3 wind fractions × 2 time approximations × 3 battery duration options = **216 full-year original HiGHS LPs**. Controls: 72 matched 0/4/8h triplets and 36 fully matched end-hold vs trapezoid comparisons, all with original source capacity, time and model-year semantics. Require all 216 optimum and hourly equality residual ≤1e-5.

To guard analysis identity, the full 108-case trapezoid subset (4×3×3×0/4/8h) is directly reconciled against the separate original source-backed 180 common-AC LP experiment [43058074434](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43058074434) at battery power 25% of peak: every original objective must match within $0.10. The earlier original source-denominator time experiment [42967335330](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42967335330) is **not** substituted as a common-AC time audit.

## Output contracts

New `paper_s_reeds2022_2030_common_ac_216_hour_assumption_LPs.csv` (216 original solver records), `paper_s_reeds2022_2030_common_ac_72_hour_storage_pairs.csv` (72 paired mode-specific storage triplets), and `paper_s_reeds2022_2030_common_ac_36_hour_assumption_comparisons.csv` (36 matched mode effects) plus machine-readable manifest. Compare both annual four-hour battery variable operating savings and the 4h→8h marginal energy-only annual annuity hurdle. Record for each row whether the hypothetical $10/kWh-year *energy cost only* decision flips across approximation modes, not merely maximum dollar discrepancy.

**Admission threshold:** no claim of publisher-certified true hour-integrated energy. If approximation changes the $10/kWh-year conditional decision, the manuscript must report that parameter sensitivity prominently. If no decision flips in the prespecified 36 cases, the result still does not certify real-world hourly generation or generality beyond this one weather reference year. All conclusions are deterministic model scenario comparisons, not probabilities or net investment metrics.

## Open source / physical modeling gates

A complete Q1 scientific submission additionally needs weather-year replication, source weather CF interval-integral validation (not just timestamp concordance), installed-resource siting/AC fleet calibration, independent market-cost variation and physical network/reliability limitations. Keep older Paper T EFS2020/ReEDS2022 **cross-release clock** gate blocked; these same-release ReEDS2022 fixed-CST reference labels must not be cited as authenticating the EFS2020 clock. Keep PR Draft until dedicated source tests and full CI are green.
