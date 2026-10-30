# Verified 2024 CISO/BPAT technology annual supply feasibility screen

Source: successful [GitHub Actions run 41092923726](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41092923726), artifact `2024-ba-supply-feasibility`: `ba_technology_annual_energy_feasibility.csv` and `provenance.json`. Combines independently audited 2024 EIA-860 BA/fuel nameplate source with EIA-923 Page 1 annual/monthly reconciled **qualified** BA/fuel generation records. Numerator is qualified-source net generation, denominator is supported nameplate MW × **8,784 hours**. These are *not* established physical capacity factors, hourly availability or BA-validated dispatch.

| Technology | CISO nameplate MW | CISO qualified MWh | CISO ratio | BPAT nameplate MW | BPAT qualified MWh | BPAT ratio |
|---|---:|---:|---:|---:|---:|---:|
| Natural gas | 31,888 | 69,665,638.826 | 24.87% | 2,167 | 11,320,381.639 | 59.47% |
| Hydro | 7,220.6 | 21,344,699 | 33.65% | 19,302.6 | 60,871,208 | 35.90% |
| Nuclear | 2,323 | 18,378,835 | 90.07% | 1,200 | 9,967,139 | 94.56% |
| Geothermal | 2,034.9 | 7,808,582 | 43.69% | 18 | 92,031 | 58.21% |
| Wind | 6,334.7 | 15,340,449 | 27.57% | 3,617.1 | 8,820,435.410 | 27.76% |
| Solar | 23,085.9 | 47,198,887.070 | 23.28% | 223.7 | 341,312 | 17.37% |
| Coal | 55 | 245,553.520 | 50.83% | 729.9 | 2,846,593.565 | 44.40% |

Among **20 BA×technology rows**, 15 have both eligible positive EIA-860 supported nameplate and EIA-923 qualified annual generation, and **none** of the 15 exceeds the trivial full-output nameplate×hours upper ceiling. Five have no supported nameplate denominator (CISO biomass/storage, BPAT biomass/oil/storage), despite observed generation; they must not be interpreted as zero capacity.

### Data coverage / qualification

- CISO gas: 374/384 qualified EIA-923 source rows, with 211,593.964 MWh reported but withheld. CISO solar: 732/748 qualified rows, 2,264,209 MWh withheld. CISO wind: 107/108, 80,117.350 MWh withheld.
- BPAT solar: 14/15 qualified, 4,714 MWh withheld. Other included major fuel combinations generally fully qualify within the currently extracted Page 1 rows, which does not establish a full BA generation census.
- EIA-923 net generation and EIA-860 plant-reported BA capacity may have different accounting boundaries and missing carrier coverage; BPAT wind specifically has an unresolved 1.981 TWh difference with the EIA-930 hourly aggregate, with EIA-930A reporting-inventory differences now documented at generator level.

### Model calibration decision

**Annual source plausibility screening: pass for the 15 comparable rows; physical hourly dispatch calibration: not ready.** It is invalid to set hourly generator `p_max_pu` equal to these ratios, or to set all nameplate capacities to always available. Separate EIA-930 observed wind/solar hourly injection cannot be added to historical wind/solar nameplate modeled as always-on supply. The illustrative 55 GW always-available firm + 20 GW peaker model remains a comparator, not a calibrated historical supply representation.

**Next model step:** implement a bounded, clearly labeled multi-BA *scenario* for non-variable sources, with generator capacity ceilings anchored to EIA-860, annual source-qualified energy benchmarks treated only as feasibility checks, explicit hydro/thermal seasonal dispatch hypotheses, and network deliverability constraints before interpreting any storage reliability or monetary estimates. EIA-923 coverage and EIA-930 BA boundary differences must remain visible in all reports.
