# Paper T bidirectional downstream sensitivity v3

**SYNTHETIC-ONLY.** No actual EFS2020/ReEDS2022 physical-hour join, no observed photovoltaic generation, no actual dispatch.

The study extends prior hypothetical unidirectional tests to 4 solar amplitude scales (0.5,1,1.5,2), 5 evening demand peak hours (16,18,19,20,22), 3 solar phase shifts (−2,0,+2 h) and 5 demand shifts (−3,−2,0,+2,+3 h): 300 deterministic runs and 60 configurations. Each configuration has its own zero-demand-shift comparator. Circular indexing preserves each annual energy total and represents **index shifts only**, not valid physical time-zone conversions.

Reproduce:
```sh
python research/paper_t_hypothetical_downstream/paper_t_directional_v3.py
python -m unittest discover -s research/paper_t_hypothetical_downstream -p 'test_*.py' -v
```

| Demand shift | Peak rises | Peak falls | Unchanged | Peak delta % min..max | Solar overlap rises | Solar overlap falls | Overlap pp min..max |
|---|---:|---:|---:|---:|---:|---:|---:|
| −3 h | 0 | 44 | 16 | −12.3920..0 | 39 | 6 | −1.5948..+5.9085 |
| −2 h | 0 | 32 | 28 | −8.7767..0 | 34 | 11 | −1.3190..+3.9228 |
| 0 h | 0 | 0 | 60 | 0 | 0 | 0 | 0 |
| +2 h | 16 | 0 | 44 | 0..+9.6212 | 20 | 25 | −3.1920..+1.3190 |
| +3 h | 16 | 0 | 44 | 0..+13.0456 | 20 | 25 | −4.4116..+1.8909 |

**Interpretation:** Depending on synthetic relative phase, time-index shifts can change the sign of downstream peak net-demand sensitivity. This is a deterministic illustrative result, not a forecast, causal estimate, statistical confidence interval or Idaho-specific observation. Solar overlap is sum(min(load,solar))/sum(solar); it is not observed curtailment. The repository's original-data temporal-join admission gates remain blocked.

Suggested Results text: *Across 60 wholly synthetic demand–solar configurations, advancing synthetic demand by three index hours reduced the net-load peak in 44 configurations (up to 12.39%), whereas delaying it by three hours increased the peak in 16 configurations (up to 13.05%). All runs preserved annual demand and solar totals. The direction-dependent behavior illustrates the downstream importance of trustworthy hourly alignment but should not be read as a measured Idaho or Western-grid impact.*
