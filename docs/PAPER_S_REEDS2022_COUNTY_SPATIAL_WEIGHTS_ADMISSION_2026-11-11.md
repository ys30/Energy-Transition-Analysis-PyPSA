# Paper S — spatial weighting and fleet representativeness admission audit (2026-11-11)

## Why the current state CF is not a fleet-generation curve

Original ReEDS2022 reference county resource HDF5 contains class × five-digit FIPS instantaneous wind/PV CF. The source `sc_wind-ons_reference_county.csv` available-potential MW (wind AC) and `sc_upv_reference_county.csv` available-potential MW (PV DC) were exact-key matched and used as state-level source potential weights in the currently verified LP branches. These are geographic *developable resource availability* proxies, **not measured 2012 wind/PV generating assets, installed 2030 plant locations, or an officially forecast state fleet mix**.

The correct first admission test is to quantify how concentrated these potential weights are before claiming representative fleet geography. In a reproducible publisher-MD5-verified audit, aggregate each source class/county key to its five-digit county FIPS using original potential MW. For each state and technology, define county fractions `w_c = potential_c / Σ potential`, county concentration index `HHI=Σ w_c²`, effective county count `N_eff=1/HHI`, top-one/top-five county potential share, and total variation distance to equal county share `0.5×Σ|w_c - 1/K|`. Source PV potential and wind potential use their own original denominators, never add mixed DC/AC MW directly.

The optional **equal-positive-county** counterfactual is a sensitivity parameter only: each county having positive source resource gets weight `1/K`; class shares inside a county remain proportional to published resource potential, `potential_class / potential_county`. This is not an approximation of true installed plants. A later full HDF5 weight-swap analysis must preserve all 8760 original time instants and native FIPS/class keys and compare each counterfactual with the current 2012 source-potential weighted state curve without changing AC/DC conversion, weather-hour convention, load or storage model.

## Reproducible provenance contract

Publisher original CSV:
- Wind: https://zenodo.org/records/18422200/files/sc_wind-ons_reference_county.csv?download=1, exact MD5 `49ab4e41dc386453b5fd32e5810774d4`, MW_AC source potential.
- Utility PV: https://zenodo.org/records/18407660/files/sc_upv_reference_county.csv?download=1, exact MD5 `e10b1a64f3a67d163e739b735938eb78`, MW_DC source potential.

New dedicated workflow [source county concentration](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/paper-s-reeds2022-county-spatial-weights.yml) produces an **8-row four-state by two-technology concentration table**, keyed FIPS county weight detail CSV, and machine-readable manifest. Unit tests must reject unknown schema, duplicated class/FIPS source keys and negative capacity. Manuscript will only report numerical concentration after verified output.

## Scientific interpretation gate

When county potential has low effective county count or high top-five share, the state CF is especially determined by a few geographic resource potential locations. This motivates **future** equal-county *stress-testing*, but even a large counterfactual sensitivity does not recover actual-fleet power. True fleet weighting requires independent EIA-860/EIA-923, NREL or authenticated deployment dataset with matching plant/geographic siting, wind/PV technology and AC/DC capacity denominator, plus a defensible time/CF linkage. Never infer future 2030 buildout from supply curve potential alone.

The same-release ReEDS 2012 source fixed CST 8760 data contain leap day but exclude Dec 31; instantaneous CF is not publisher-certified interval-integrated generation. The LP does not calibrate transmission, adequacy, installation cost, replacement or market revenues. Paper S and Paper T separate cross-release clock gates remain independent. Full engineering CI [43109407850](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43109407850) passed 975 tests, but this is not physical-model validation.

**Submission admission status: pending authenticated spatial concentration values, actual siting or documented counterfactual reweighting and weather-year replication.** The original published source potential-weighted LP values remain frozen.
