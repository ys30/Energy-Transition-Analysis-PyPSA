# Paper S E1 — closed descriptive temporal mechanism audit (10 November 2026)

**Scientific status:** **E1 completed at its prespecified descriptive scope**, not a causal explanation or validated predictor. No additional LP solves, figures, windows, storage penalties or parameter searches were run. E1 directly inspects the accepted 2030 Arizona p28 and Wyoming p24 **two independent original-source baseline hourly archives** and the accepted 10 predeclared-window LP result table. The 17,520 original source hours and all five dispatch variables in the independently accepted baseline-primal ZIPs matched exactly (maximum absolute archived hourly difference **0 MWh**).

## Mechanism-oriented contrast at fixed source windows

Model and constraints remain original source-ordinal EFS loads, synthetic Wave A supply, P=25% source peak MW, E=one source peak MW-hour, eta roundtrip=0.9, original hypothetical objective; no source UTC, observed renewable generation, network-constrained power flow or reliability outcomes were admitted.

| Original source zone | Prespecified window | Near-optimal attainable window discharge span (MWh) | Original synthetic-resource surplus potential (MWh) | Original synthetic-resource deficit potential (MWh) | Original baseline modeled firm generation in window (MWh) | Baseline zero-SOC hours / 168 | Baseline charge-power-limited hours / 168 |
|---|---|---:|---:|---:|---:|---:|---:|
| Arizona p28 | 2001–2168 | 1,286.517 | 289,519.783 | 277,113.958 | 174,429.248 | 58 | 14 |
| Arizona p28 | 4001–4168 | **29,352.336** | 138,404.977 | **678,854.751** | **570,688.594** | 34 | 0 |
| Wyoming p24 | 1–168 | **4.117** | **4.529** | 92,563.584 | 92,559.507 | **165** | 0 |
| Wyoming p24 | 2001–2168 | **2,712.412** | **2,064.804** | 73,081.568 | 71,238.778 | **77** | 0 |

These conditional contrasts suggest that source-hour resource shortfall, timing of renewable surplus and the SOC boundary may help characterize where the **cost-sublevel set can express temporal reallocation**. They **do not** establish a universally monotonic relationship: the same candidate indicators behave differently across the two groups, baseline primal dispatch is itself an optimizer output, and only five nonrandom windows per shape were examined. A descriptive association is not a causal mechanism. In particular, Wyoming has **zero charge-power-limit hours and zero energy-limit hours in all five baseline windows**, so those features cannot explain its within-zone ranking. Any small-n rank correlations were retained in the private audit as exploratory only, with **no p-values or predictive skill claims**.

## Result for Paper S text

A private v14 manuscript has a concise Results 3.8 source-state diagnostic and a Discussion 4.8 caveat inserted into the existing sections. It retains the **5 main + 3 supplementary images**, all pre-existing primary/secondary experiments, and introduces **no new supplement figure or appendix**. E2 was previously closed by independent conservation-difference certification; E1 is closed for its *descriptive* scope. The only remaining planned new scientific LP experiment is **E3: two additional distinct positive-demand source-shape groups**, with a prespecified finite end point. After E3, freeze experiments and proceed to source-clock and rights verification, references/journal fit and coauthor approval.

Original audit anchors: [predeclared five-window CI #42919689808](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42919689808), [E2 conservation](PAPER_S_E2_WINDOW_OUTSIDE_CONSERVATION_CLOSED_2026-11-10.md), [EFS original clock and license](PAPER_S_V6_EFS_LICENSE_CLOCK_AND_RELEASE_GATE_2026-11-10.md). The full private Word draft, source hour CSVs and internal audit bundle were **not uploaded to the public repo**.
