# Verified Western NARIS zonal dispatch and empirical load admission (2026-10-31)

## Verified compute evidence

- GitHub Actions workflow 41230714539 passed; PyPSA HiGHS optimization uses 34 upstream-defined Western regions and 131 published directional NARIS transfer Links.
- Stress tests set **synthetic demand of 100, 1,000, 5,000 MW per region**, synthetic generation and marginal-cost coefficients 1 and 100, with both published NARIS interface limits and tenfold relaxed limits.
- At 3,400 MW total demand, local backup is 0 MW for both cases; objective difference is floating-point noise.
- At 34,000 MW total demand, local backup is 15,576.93 MW (published limits), 0 MW (tenfold); synthetic objective decreases from 1,576,116.07 to 34,000.
- At 170,000 MW total demand, local backup is 147,576.93 MW (published limits), 23,785.61 MW (tenfold); synthetic objective decreases from 14,780,116.07 to 2,524,775.39.
- All results are single-snapshot *illustrative* transmission stress tests. Objectives are in arbitrary synthetic cost units and **must not be reported as USD, historical congestion, or a policy return**.
- Counting links exactly at capacity is not sufficient proof of economically priced congestion. Marginal objective effects require shadow-price or finite-difference validation.

## Empirical data compatibility gate

Official upstream documentation: [PyPSA-USA Electricity Demand](https://pypsa-usa.readthedocs.io/en/latest/data-demand.html) and upstream source [docs/source/data-demand.md](https://github.com/PyPSA/pypsa-usa/blob/master/docs/source/data-demand.md).

- Historical demand: GridEmissions / EIA-930 **2018–2023**, at **balancing-authority** resolution; these are not the 34 ReEDS NARIS zonal IDs. **Never join on superficial name resemblance.**
- Future demand: NREL Electrification Futures Study (EFS) **2030, 2040, 2050**, originally defined by **state**, requires valid state-to-ReEDS-zone allocation weights.
- Alternative EER demand: state-level 2021–2050 model horizons, weather-year indexed. **Separate scenario provenance from the planning-year NARIS interface case**.
- CPUC SERVM: California-only; not suitable as a blanket 34-zone Western system load source.
- NARIS2024 transfer interface capacities are **zonal planning assumptions**, not 2024 historical AC network impedance or simultaneously deliverable interconnection capacities.

### Minimum acceptance checks before empirical solve

1. Freeze immutable upstream versions, dataset URI, license, publication year, and data checksum.
2. Obtain official balancing-authority-to-ReEDS-zone or state-to-zone assignment weights; independently verify each source region's weight sum (within declared tolerance), unmatched source zones, and double counting.
3. Validate timestamps, timezone, daylight-saving gaps/duplicates and missingness for the selected empirical year.
4. Audit hourly total modeled load vs source aggregate (MWh conservation) and compare with an independent check where available.
5. Record generator capacity, fuel mix, cost assumptions, and boundary flows; do **not** calibrate generation against all-fuel EIA-930 NG using only gas generation.
6. Only after all admission checks, solve the 34-zone case with actual hourly source-backed demands; publish solver status, nodal balances, capacity violations, curtailment and unmet demand.

Current status: **real source-backed zonal topology and constrained optimization demonstrated; historical demand / generation mapping not yet admitted.**
