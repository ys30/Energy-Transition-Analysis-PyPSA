# Paper S — 168h transport failure diagnosis and repaired source-to-LP join (2026-11-19)

## Execution evidence
GitHub Actions [44668829347](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44668829347), two 168-hour windows (start 0 and 4320), failed in `report()`, **after** source downloads and scientific unit tests completed successfully and the code reached CSV matching. Job logs:
- start 4320: job 136064614782;
- start 0: job 136064615023.
Both failed at an invalid Pandas merge:
`prior.merge(cases[KEY], on=KEY, validate="one_to_one")`
because `prior` is the original **1,080** row 3×3 LP duration-value grid while the subset is only **120** input-only source cases. The LP rows also include three wind shares whereas the mechanism's wind share is fixed at 50%; without narrowing that dimension, ignoring `wind_share_ac` produces duplicate keys.

## Repair
The code now fails closed if the frozen LP grid lacks `wind_share_ac`, filters to `wind_share_ac=0.5`, rejects duplicate selected source keys, and left-joins **from the 120 selected source cases to** the filtered LP value table with `validate='one_to_one'` and `indicator=True`. It rejects missing source matches and nonfinite LP values rather than allowing accidental row multiplication. A synthetic 1,080-source-grid regression test (three shares × three capacity ratios) covers selected 120 records across four predeclared scenarios, fifteen source years and two siting weights.

## Important scope
The failed runs uploaded no usable output artifact and do **not** certify 168-hour physical mechanism conclusions. This repair changes the analytical join/QA only, not the source inputs, duration definitions or optimization formulation. Passing source-independent unit tests is distinct from successful source-backed artifact verification.

## Admission after rerun
- Both week starts (0, 4320) must finish successfully and upload `W0–W3`.
- Exactly 120 source cases, 120 paired horizon records and 4 state–ratio summaries per week.
- Verify 24h-vs-168h nested feasible sets, 4h-vs-8h nested capacities, conservation residuals and common zero initial/terminal SOC.
- Analyze both weeks without selecting the favorable one; compare cross-day optimal MWh indicators against frozen annual cost-optimal LP value as **descriptive, horizon-mismatched correlations**.
- Do not revise manuscript mechanism conclusions before artifact verification; maintain previously verified 213/1080 illustrative cheapest-ATB crossings and earlier chronological greedy falsification intact.
