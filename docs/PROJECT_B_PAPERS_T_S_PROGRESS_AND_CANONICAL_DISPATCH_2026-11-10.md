# Project B — Verified progress and paper decision gate (10 November 2026)

**This report separates engineering completion, accepted numerical experiments, manuscript drafts and outstanding scientific admission criteria.** It is not a percentage-complete claim. Full Paper S and Paper T manuscripts remain private.

## Validated project engineering

- Original NLR EFS2020 original demand and LAF derived 2030–2050 chronology pipeline, seven states, 20 load zones; source clock physically uncertified, 2040 leap-hour label pathology admitted.
- Paper S original 540 full-year HiGHS LP cases for the original 20×3×3×3 factorial, zero terminal SOC. Synthetic source availability only, not measured renewables or Western network OPF.
- Orthogonal MW/MWh: 189 LP cases, 252 independent-factor comparisons and 84 four-corner interactions, source archived and reconciled.
- Annual storage objective / local bound dual finite-difference diagnostics and SOC mean occupancy envelopes.
- Annual discharged MWh cost-capped envelopes; selected 168-source-hour discharge min/max; original dollar-cost tolerance ladder; 52,560 full-source-hour records with 24-source-hour block net redistribution; Figure S20 certified.

Relevant original archived runs: [full-year source LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42107237659), [orthogonal LP](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42674534963), [full-hour alternative dispatch reconstructions](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558), [Figure S20](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42852393262).

## NEW acceptance: minimum annual battery throughput as secondary dispatch convention

The source-backed [original archived annual min-throughput and fixed-window audit #42853226638](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42853226638) **passed all jobs**. This re-solved the unchanged source-ordinal full-year LP for Arizona p28 and Wyoming p24 using synthetic ordinal Wave A, battery P=25% of source peak and E=1 peak-hour. It then minimized **annual discharged battery energy** subject to the explicitly documented `C_original <= C* + max(USD 0.05, 10^-9 × C*)` tolerance, and directly compared the selected-window service (LocalHourID 4001–4168) to previously accepted min/max window LPs. All candidate annual original costs and hourly balances matched existing archives. This is **minimum delivered energy**, not minimization of absolute sum of all charging+discharging transactions; the nomenclature is deliberately precise.

| Source demand | Original HiGHS window discharged (MWh) | Annual-min-discharge convention in window (MWh) | Previous accepted window lower (MWh) | Previous accepted window upper (MWh) | Canonical normalized position |
|---|---:|---:|---:|---:|---:|
| Arizona p28 | 108,166.156 | **102,721.738** | 88,047.183 | 117,399.519 | **49.9945%** |
| Wyoming p24 | 260.530 | **260.530** | 0 | 1,616.753 | **16.1144%** |

The convention is one specific optimal solution of a second-stage LP. **It does not narrow the original cost-capped feasible set or establish unique timing of delivered energy.** No claim of a universal least-cycle schedule is justified: cycling can be measured through charge energy, discharge energy, weighted throughput, battery degradation cost or cycle counts, and these need not have identical secondary minimizers. This secondary objective can also have multiple optimal dispatch trajectories. Its objective-cap is still a narrow, but nonzero, near-optimal cost allowance.

## Paper T — manuscript readiness

Private complete collaborator v13.3, five original source-derived primary figure reviews, 33 original state-year lag cases and matched NASA POWER clock-source control already developed. Critical blockers:
- Demonstrate incremental methodological novelty beyond existing synchronization / provenance conventions, or present a narrower falsification/source audit contribution.
- Original EFS LocalHourID physical clock meaning and Idaho source anomaly attribution still unresolved.
- Final journal fit, source rights/DOI, coauthor review and legally appropriate reproducibility release incomplete.
- Not submission-ready; no public manuscript DOI or published result claimed.

Reference [Paper T novelty review](PAPER_T_V13_3_SCIENTIFIC_NOVELTY_AND_METHOD_SCOPE_REVIEW.md).

## Paper S — manuscript readiness

Private manuscript working draft plus many verified source audit and supplemental figures (latest Figure S20). Its strongest bounded methodological narrative is the **difference between aggregate objective/annual throughput stability and failure to uniquely identify subannual hourly delivery** under synthetic source-ordinal LP dispatch. However:
- Current resource profiles are hypothetical mathematical wave/flat sequences rather than actual weather-year wind/PV.
- LocalHourID physically unverified, no transmission, no realistic generator mix/POI, storage capex/degradation or reliability constraints.
- Large 20-figure experimental history is **not a recommended 20-figure main article**. Freeze the claims, select about 5–6 main figures with directly certified numerical results and move deep derivative/degeneracy tests to supplement.
- Manuscript is **not submission-ready**. A sharply bounded methods paper may be possible with explicit synthetic model limitations and direct relevant literature, while an empirical Western energy-transition forecasting paper is not yet justified.
- The new minimum-annual-discharge convention does not resolve the time-allocation nonidentification and should appear as a diagnostic, not an engineered dispatch prescription.

## Next actionable decisions

1. **Freeze Paper S source-verified evidence** and build a private figure-to-claim matrix selecting publication-grade primary vs supplementary evidence. Do not add unsupported headline physics claims.
2. If prioritizing real-system policy: obtain independently verified source time, actual renewable resource, fleet/network and economics; this is a substantive distinct data/model workstream.
3. For Paper T: conduct one independent method/novelty comparison or reframe as a transparent published-data case study.
4. Archive final CI status for this commit; a specific successful research workflow does not imply the latest main CI has finished.

**Claims gate:** accepted workflow success certifies computational and archive checks on the stated inputs; it never upgrades assumed synthetic physics to observed renewable operations or real Western OPF.
