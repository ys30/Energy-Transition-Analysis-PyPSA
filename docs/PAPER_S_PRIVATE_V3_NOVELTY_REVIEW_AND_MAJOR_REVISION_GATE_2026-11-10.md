# Paper S — independent novelty red-team and private manuscript v3 status (10 Nov 2026)

**Scope:** This is an editorial and model-audit record, **not the private manuscript**. A separately maintained private Word manuscript v3 now contains a cited Introduction, expanded existing mathematical Methods, Results, Discussion, Conclusions, five main figure assets, Supplementary S1, a limited but source-verified bibliography, and simulated reviewer objections. The full manuscript and its six figures remain private.

## Existing literature materially narrows what can be claimed

- DeCarolis, 2011, Energy Economics, DOI 10.1016/j.eneco.2010.05.002: established energy-system Modeling to Generate Alternatives.
- DeCarolis et al., 2016, Environmental Modelling & Software, DOI 10.1016/j.envsoft.2015.11.019: further MGA implementations in energy optimization.
- Neumann & Brown, 2021, Electric Power Systems Research, DOI 10.1016/j.epsr.2020.106690: quantified near-optimal alternatives to long-term generation/storage/network investment in a European power-system model.
- Pedersen et al., 2021, Energy, DOI 10.1016/j.energy.2021.121294: near-optimal solution continuum and multiple energy-system outcome measures.
- Schade, 2024, Energy Storage, DOI 10.1002/est2.588: battery degradation changes economic dispatch interpretations.
- Vaičys et al., 2024, Journal of Energy Storage, DOI 10.1016/j.est.2024.112941: storage dispatch with cycling/degradation-aware restrictions differs from conventional LP alternatives.
- EPRI Resource Adequacy Model Selection Guidelines: all-year perfect foresight can overstate storage flexibility; original horizon/boundary assumptions must be disclosed.

The paper **does not invent MGA, alternative optima, or battery dispatch linear programming**. Defensible narrower potential contribution: independently audited **annual delivered-discharge interval versus a fixed 168-source-hour delivery interval** under the same original-cost cap in a transparent source-ordinal toy LP, with explicit source-shape pseudoreplication and MW–MWh factorial restrictions.

## Red-team outcome: Major revision, not submission-ready

1. **Scientific priority:** the claimed aggregate/temporal identifiability distinction is valuable as an illustration, but its novelty versus established MGA and dispatch degeneracy literature remains incompletely shown.
2. **Model physicality:** direct SciPy/HiGHS, synthetic availability, no verified UTC or actual Western OPF, no network or unit commitment, and no degradation economics. The formulation has no explicit charge/discharge mutual-exclusion constraint; inspect real trace incidence before drawing physical conclusions.
3. **Numerical rigor:** C(x) <= C* + max(USD 0.05, 1e-9 C*) is a small but **nonzero** cost allowance with finite solver tolerances; the apparent scheduling variability is not a proof of mathematically exactly equal-cost multiple optima.
4. **Statistical dependence:** original 20 source zones include one zero-demand series and only seven unique within-year normalized nonzero chronology classes. Factorial case counts are not IID statistical sample sizes.
5. **Publishing:** final intro/reference survey and journal fit, source LocalHourID semantics, 2040 source-year mapping, permitted redistribution, code/data availability, conflict declarations, final renumbered figures, and coauthor approval are outstanding.

## Priority actions

**P0:** (i) EFS clock and licensing provenance; (ii) check charge/discharge simultaneity in the previously accepted hourly primary and secondary dispatch archives and assess need for an explicit physicality restriction; (iii) systematic reviewer-grade comparison with published work on temporal dispatch alternatives.

**P1:** (i) full-text cross-reference/bibliography audit; (ii) journal selection, figure typography and copyright-safe source/data statements; (iii) confirm author declarations and independent scientific review.

No new LP runs or source results have been accepted in this editorial revision. The private Word manuscript is intentionally **not** committed to public GitHub.

## Direct original-archive primal audit completed (52,560 original hourly records)

Without re-running any LPs, inspect accepted full-hour schedule artifacts [#42851448558](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558), 2030 original projected demand, Arizona p28 and Wyoming p24; three schedules each: original baseline, minimum source-window discharge, maximum source-window discharge. A simultaneous charge/discharge event requires **charge input > 1e-6 MWh AND discharge > 1e-6 MWh in the same source hour**.

| Group | Original baseline | Min window discharge | Max window discharge: overlapping hour(s) and energy |
|---|---:|---:|---|
| Arizona p28 | 0 | 0 | **1**, source hour 4035: charge 3,712.692349 MWh, discharge 3.246799 MWh |
| Wyoming p24 | 0 | 0 | **1**, source hour 4137: charge 0.044732 MWh, discharge 0.040259 MWh |

**2 of 52,560 source-schedule-hour records exhibit simultaneous positive charge and discharge at the specified threshold.** Both occur in the selected source-hour window 4001–4168. These overlap-discharge magnitudes are small compared with the Arizona window-discharge envelope (~29,352 MWh) and Wyoming envelope (~1,617 MWh), so the overlaps alone **cannot explain** the source-window range. Nevertheless, the current linear dispatch constraints do not categorically preclude simultaneous charge/discharge; **physically exclusive-operation reoptimization remains an open P0 scientific admission gate**. This evidence is diagnostic and must not be misrepresented as an LP run with improved battery physics.
