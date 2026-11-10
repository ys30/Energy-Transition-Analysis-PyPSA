# Paper S — exact LP Methods audit and prior-art novelty gate (10 Nov 2026)

**Status:** source-code-audited, literature-verified editorial note, **not a new physical-grid simulation or completed journal submission**. The private English working manuscript has been revised separately and remains outside public GitHub.

## Executed LP, not an inferred PyPSA network model

The source implementation [`efs_cyclic_storage_lp.py`](../src/energy_transition/efs_cyclic_storage_lp.py) solves six nonnegative hourly variables per zone: direct renewable use `r`, renewable charge input `c`, battery discharge to load `d`, firm energy `f`, unused synthetic potential `u`, and end-hour battery SOC `s`. Each original ordinal hour has:

- Renewable conservation: `r_t + c_t + u_t = A_t`
- Load conservation: `r_t + d_t + f_t = L_t`
- Battery SOC recursion: `s_t - s_(t-1) = sqrt(0.9)*c_t - d_t/sqrt(0.9)`
- Source bounds: `0 <= r_t <= min(A_t,L_t)`, `0 <= c_t,d_t <= P`, `0 <= f_t <= 1.2 L_peak`, `0 <= u_t`, `0 <= s_t <= E`; `s_0=s_8760=0`.
- Source-specified illustrative variable objective: `min C= sum_t[5*(r_t+c_t)+90*f_t]` in model USD.

The synthetic renewable availability is `A_t=0.9 L_peak * phi(t)`, with `phi=0.5` for flat and `phi=0.5 +/- 0.35*cos(2*pi*(t-1)/24)` for the two ordinal waves. **Supply is synthetic, not measured solar/wind.** The solver is direct **SciPy linprog / HiGHS** rather than the PyPSA Network/OPF engine. No interzonal network, battery CAPEX, degradation, weather-year certified UTC or physical Western dispatch is identified.

Original baseline ratings are 0/4/8h at storage power 25% of peak demand and `E=P*duration`; the orthogonal experiment uses independent P ratios 12.5%, 25%, 50% and E ratios 0.5/1/2 peak-MW-hour. The source audit finds 19 positive-demand and one zero-demand original zones per planning year, but only seven distinct within-year peak-normalized positive-load shapes. Do not mistake these seven shapes or the three planning years for IID replicates.

## Near-optimal dispatch method and terminology

The primary original optimal objective is `C*`. Secondary LPs retain its source balances/bounds and impose `C_original(x) <= C* + max(USD 0.05, 1e-9*C*)`. Secondary objectives separately min/max total SOC, annual battery discharge and discharge in original LocalHourID 4001–4168, with archived original objective rescoring and numerical tolerance checks. The resulting ranges are **near-optimal cost-sublevel sets**, not proved exact alternate-optimum faces. Source-hour ordinals are not certified calendar weeks.

## Critical prior art: no claim to have invented MGA

1. DeCarolis, J. F. (2011), *Using modeling to generate alternatives (MGA) to expand our thinking on energy futures*, **Energy Economics**, 33, 145–152. DOI [10.1016/j.eneco.2010.05.002](https://doi.org/10.1016/j.eneco.2010.05.002).
2. DeCarolis, J. F., Babaee, S., Li, B., Kanungo, S. (2016), *Modelling to generate alternatives with an energy system optimization model*, **Environmental Modelling & Software**, 79, 300–310. DOI [10.1016/j.envsoft.2015.11.019](https://doi.org/10.1016/j.envsoft.2015.11.019).
3. Neumann, F., Brown, T. (2021), *The near-optimal feasible space of a renewable power system model*, **Electric Power Systems Research**, 190, 106690. DOI [10.1016/j.epsr.2020.106690](https://doi.org/10.1016/j.epsr.2020.106690).
4. Pedersen, T. T., Victoria, M., Rasmussen, M. G., Andresen, G. B. (2021), *Modeling all alternative solutions for highly renewable energy systems*, **Energy**, 234, 121294. DOI [10.1016/j.energy.2021.121294](https://doi.org/10.1016/j.energy.2021.121294).
5. Brown, T., Hörsch, J., Schlachtberger, D. (2018), *PyPSA: Python for Power System Analysis*, **Journal of Open Research Software**, 6(1), 4. DOI [10.5334/jors.188](https://doi.org/10.5334/jors.188). **Context reference only** for this experiment, not its direct computational solver.

**Novelty positioning:** near-optimal alternate dispatches and MGA are established. The candidate, narrower contribution is a reproducibly archived **comparison between annual aggregate identifiability and the lack of uniquely identified prespecified temporal allocation**, with a distinct independent P/MWh sensitivity and source-data pseudoreplication audit. This is a testable *application and reporting* contribution, not a claim of inventing optimization methods or describing measured Western dispatch.

## Private document revision and still-open gates

The new private manuscript revision adds a precise mathematical methods section (source units, availability shape, original objective and all constraints, independent power/energy factorial, secondary-objective rules and numerical acceptance criteria), plus a critical literature-positioning section with verified DOI references. **Full private manuscript text and figure images were not copied into public GitHub.**

Remaining mandatory review: independent original EFS source-time semantics and reuse permission; physically grounded external model validation if policy claims are desired; complete systematically researched Introduction and full bibliography; target-journal novelty/word-count/style review; references to all five main figures plus Supplementary S1; author/coauthor signoff and statements of reproducibility. Source-code audit and CI success do not establish these outstanding claims.
