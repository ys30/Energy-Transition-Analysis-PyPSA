# Verified EIA-923 2024 qualified generation by BA and technology

Source: successful [GitHub Actions #41083881986](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41083881986), artifact `eia923-ba-technology-qualification-2024`, file `eia923_qualified_by_ba_technology.csv`. The workflow reads the previously qualified original EIA-923 Page 1 records from [run 40937912804](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/40937912804). No incomplete rows are silently counted as full qualified data.

| Technology | CAISO qualified generation (MWh) | CAISO qualified/source rows | BPAT qualified generation (MWh) | BPAT qualified/source rows |
|---|---:|---:|---:|---:|
| Natural gas | 69,665,638.826 | 374/384 | 11,320,381.639 | 20/20 |
| Hydro | 21,344,699 | 192/192 | 60,871,208 | 56/56 |
| Nuclear | 18,378,835 | 2/2 | 9,967,139 | 1/1 |
| Geothermal | 7,808,582 | 15/15 | 92,031 | 1/1 |
| Coal | 245,553.520 | 3/4 | 2,846,593.565 | 6/6 |
| Solar | 47,198,887.070 | 732/748 | 341,312 | 14/15 |
| Wind | 15,340,449 | 107/108 | 8,820,435.410 | 28/28 |

Selected withheld reported annual net generation (MWh) outside qualified totals: CAISO gas 211,593.964, CAISO solar 2,264,209, CAISO wind 80,117.350, BPAT solar 4,714; CAISO storage also has -249,866 MWh withheld (signed net value). Coverage ratios refer to **rows available in this audited Page 1 dataset**, not a census of all possible assets or a proof of 100% BA generation coverage.

This is a **BA-specific annual energy audit**, not hourly power availability, reservoir or dispatchable generation limits, or storage investment calibration. EIA-923 plant-reported BA attribution can differ from EIA-930 operational balancing-area reporting; notably BPAT wind has ~8.82 TWh qualified EIA-923 generation compared with ~6.84 TWh reported EIA-930 net wind generation over covered hours. This difference is not yet reconciled; the sources must not be combined or used interchangeably without a plant/BA and accounting boundary audit.

**Next:** match qualified plant-level EIA-923 Page 1 generation with 2024 EIA-860 individual generators, preserve source-row qualification flags and withheld data, and establish BA/fuel coverage before deriving justified historical generation capacity assumptions. Current 55 GW firm + 20 GW peaker remains an illustrative model supply.
