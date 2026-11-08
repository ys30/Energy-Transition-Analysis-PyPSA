# Paper S: verified 2030 Arizona p28 temporal opportunity and storage utilization diagnostic

## Evidence and status

Derived from the accepted original 78,840 hourly-primal rows for **2030 Arizona p28**, [hourly solve #42460995051](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42460995051). The new reproducible run-length/SOC workflow [#42462518562](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42462518562) **completed successfully**, using the same archived hourly source and verifying the corresponding nine original annual mechanism summary rows. Script: [paper_s_trace_mechanism.py](../src/energy_transition/paper_s_trace_mechanism.py). The hourly input represents original EFS load against artificially constructed flat or 24-ordinal-wave renewable availability, **not physical weather time**.

Run lengths are defined on ordered `LocalHourID=1..8760`, using contiguous positive pre-dispatch `max(synthetic_available - source_load,0)` or deficit intervals. They do **not wrap** across the year's endpoints. These intervals are pre-dispatch opportunities, not the actual battery charge/discharge sequences.

## Actual results

| Synthetic profile | Mean surplus-run duration (h) | Mean deficit-run duration (h) | 4h battery discharged (TWh) | 8h battery discharged (TWh) | Mean SOC fraction, 4h | Mean SOC fraction, 8h |
|---|---:|---:|---:|---:|---:|---:|
| Flat 50% | 8.342 | 16.879 | 0.951 | 1.015 | 13.60% | 10.89% |
| Wave A | 10.186 | 13.786 | 5.217 | 8.950 | 39.19% | 39.28% |
| Wave B | 9.664 | 16.129 | 4.015 | 6.809 | 29.78% | 29.49% |

Under the assumed **8-hour** battery design, the original dispatch yields **~34.6, ~305.0 and ~232.0 equivalent full discharge cycles** for Flat, Wave A and Wave B, respectively. The cycle metric divides delivered discharge MWh by usable delivered MWh per nominal full SOC swing, `capacity_MWh * sqrt(0.9)`. This is a model-dependent usage measure, **not measured battery degradation, throughput warranty or economic lifetime**.

The Wave A / Flat discharged-energy ratio for the 8-hour case is approximately 8.8 within this one selected source zone. However, differing synthetic supply levels at individual hours drive these differences; do not infer that the longer average surplus runs, by themselves, caused the improvement. Source-independent comparison and controlled perturbations are necessary for causal attribution.

## Methodological interpretation

- Source demand and battery power ratio were held fixed across the synthetic profiles for the selected zone; the artificial supply profiles have equal annual mean capacity factors but substantially different daily ordinal patterns.
- SOC occupancy, run-length statistics and delivered energy provide a more informative mechanism diagnostic than charging-hour counts alone.
- **Every duration within each profile shares the exact same pre-dispatch surplus and deficit run distribution**, by design.
- The tests validate full-hour ordering, nonwrapping run lengths, source-hour population, hourly renewable/load accounting, battery SOC recursion, and consistency of recorded annual activity counts with the source archive.
- LP solutions may not be unique in all hourly decisions: count- and mean-SOC-level metrics can depend on which mathematically equivalent optimum HiGHS returned.
- Source clocks and 2040 calendar label semantics remain unresolved; there is no physical UTC or meteorological conclusion.
- The synthetic resource shapes, cost coefficients, 20 independent-zone framework and lack of battery CAPEX prevent claims about real Western Interconnection storage value or economic optimal duration.

## Publication use

**Figure S7:** Representative-zone annual storage delivered energy under the same three artificial profiles, 4h vs 8h assumed storage.

**Figure S8:** Representative-zone mean SOC relative to installed capacity under the same settings. These are supplementary mechanism displays rather than cross-region generalizable evidence.

Prioritize a *pre-registered contrasting-zone replication*, e.g. select additional zones based on their source-demand size quantiles before inspecting storage responses. For physical credibility, obtain a separately authenticated resource data source and enforce timestamp/granularity geographic admission before any grid-wide interpretation. The paper manuscript stays private.
