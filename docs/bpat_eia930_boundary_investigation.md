# Investigating BPAT's persistent EIA-930 balance residual (2024)

**Status:** unresolved; prohibit use of BPAT hourly total interchange for transmission calibration.

## Verified evidence
The [2024 hourly residual audit](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40943712858) finds 8,783 common complete BPAT hours, 100% positive residual `D - NG + TI`, and approximately +36.04 TWh summed residual. The monthly residual is consistently positive. CISO has separate missing-hour coverage limitations.

## Official definitions and reporting caveats
The [EIA Hourly Electric Grid Monitor documentation](https://www.eia.gov/electricity/930-content/about.html) says demand is generally calculated as net generation minus total net interchange; positive TI denotes net flows **out**, negative TI denotes flows **in**. However, EIA specifically describes physical boundary measurement versus commercial dispatch and adjustments for **pseudo-ties** and **dynamic scheduling**. EIA explicitly warns that some BAs cannot fully eliminate these arrangements, and corrections can change reported demand materially.

EIA also notes that EIA-930 generation is a subset of all utility-scale generation in other EIA publications. Hence EIA-923 plant-level BA-coded net generation is **not** an appropriate substitute for EIA-930 hourly NG in an accounting identity.

[Catalyst Cooperative PUDL hourly operations documentation](https://data.catalyst.coop/preview/pudl/out_eia930__hourly_operations) exposes *separate* reported, adjusted, and EIA-imputed generation/interchange/demand fields. These distinctions are potential avenues to investigate, but **do not establish** which adjustment caused BPAT's residual.

## Recommended independent next checks
1. Verify whether the EIA API's `D`, `NG` and `TI` represent the same reported/adjusted/imputed processing stage. The project currently obtains demand through `fetch_eia_demand`, with independently audited short-gap QC, but NG and TI via other fetchers. Do not call these three series an independently certified physical-energy identity.
2. Compare PUDL *reported* triplets and *adjusted* triplets separately for the same BPAT hours, with an explicit source version/date.
3. If accessible, compare Bonneville published actual interchange/net-load reporting **with definitions and boundaries**; do not merge incompatible samples or import scheduled rather than physical flows.
4. Re-evaluate the screened calibration gate only if same-definition, same-hour measurements pass. Do not infer line transfer capability or silently subtract a fitted 4-GW offset.

## Modeling policy
Keep BPAT hourly TI as **observed but not eligible for capacity calibration**; CISO also remains unqualified for annual interchange calibration because of missingness. Continue independent EIA-923 generation-technology benchmarking and sensitivity analysis, clearly distinguished from a validated interconnected dispatch model.
