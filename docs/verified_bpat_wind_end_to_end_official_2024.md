# Verified end-to-end BPAT 2024 official wind reconciliation

Successful full source download and reconciliation: [GitHub Actions #41162114345](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41162114345), code revision `79eccfae`. [CI #41162114409](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41162114409) also passed.

This run independently retrieved EIA-923 plant-month generation, EIA-860 annual plant-BA crosswalk and EIA-930 BPAT WND hourly generation, then executed the actual reconciliation. It is more than unit-test-only CI.

| Field | Actual run result |
|---|---:|
| EIA-923 BPAT-attributed wind generation | 8,820,435.41 MWh |
| EIA-930 BPAT WND signed hourly generation | 6,839,734.00 MWh |
| EIA-923 less EIA-930 | **1,980,701.41 MWh** |
| BPAT-attributed EIA-923 wind plants | 28 |
| EIA-930 BPAT hourly coverage | 8,784 / 8,784 |
| EIA-923 wind generation with unmatched plant crosswalk | 358,706,713.807 MWh |
| EIA-923 wind generation mapped to other BAs | 78,103,599.63 MWh |
| Wind plants unmatched across all BAs | 993 |

**Important population warning:** the unmatched and other-BA quantities are *not* BPAT-specific wind generation. They are diagnostics calculated across the broader raw EIA-923 population before filtering to BPAT. They are neither parts of nor explanations for the BPAT discrepancy.

The 1.981-TWh gap survived repair of the EIA-860 `mapping_year` output schema and EIA plant-ID decimal-suffix normalization. This confirms the persistence of a descriptive cross-source accounting difference; it does **not** establish loss, curtailment, interchange, or which agency/facilities cause the difference.

Next: audit official definitions and plant populations, including the interpretation of EIA-923 plant accounting and EIA-930 BA operational reports. Do not calibrate transmission transfers from the raw difference.

## Quantitative magnitude and interpretation guardrails

The measured EIA-923-minus-EIA-930 difference is **22.46% of the BPAT-attributed EIA-923 wind total**, or **28.96% of the EIA-930 BPAT hourly wind total**. These ratios use different denominators and must not be described as curtailment rates or measurement-error percentages. The EIA-923/EIA-930 ratio is approximately **1.290**.

The 2024 EIA-930 hourly series has all 8,784 expected UTC-hour timestamps; this rules out **missing EIA-930 timestamps** as the arithmetic explanation for the 1.981-TWh difference. It does not rule out a source definition, BA boundary, plant ownership/operation assignment, negative-value reporting, or differences in the underlying measurement processes.

**Next empirical discriminator:** compare the 28 BPAT-attributed plant IDs with source-level ownership/operating BA metadata and document the official EIA-923 and EIA-930 reporting definitions. Do not add the national unmatched plant population to BPAT totals. Retain the signed wind values, do not clip negatives, and never force the two totals to match through an inferred transmission or curtailment adjustment.

## Plant-level concentration from retained numerical artifact

Independently re-read the `bpat_wind_reconciliation/wind_plant_ba_totals.csv` artifact from successful run [41162114345](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41162114345). The 28 BPAT-attributed plants sum to **8,820,435.41 MWh**, matching the reported BA total.

| EIA plant ID | 2024 EIA-923 wind MWh |
|---|---:|
| 57195 | 864,875.00 |
| 57159 | 671,560.00 |
| 57549 | 619,466.82 |
| 57526 | 619,333.48 |
| 62745 | 616,871.00 |

Top five plants: **3,392,106.30 MWh (38.46%)** of the BPAT-attributed plant generation; top ten plants: **65.11%**. These are **plant-generation concentration metrics, not identified contributions to the 1.981-TWh cross-source difference**. EIA-930 BPAT WND is a BA-level hourly aggregate and does not supply plant-level differences.

The retained EIA-923 normalization manifest also reports **3,894 excluded valid numeric monthly cells** totaling **104,010,865.211 MWh** nationally across fuels. This cannot be assigned to BPAT wind. **The subsequently verified BPAT-specific intersection audit below found zero excluded BPAT WND records**; the national excluded-cell total must not be invoked to explain the BPAT difference.

## Verified BPAT-specific source exclusion audit

The [successful end-to-end BPAT run #41167672392](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41167672392), at commit `477a6ba5`, generated `excluded_source_wind_audit.json` from the official EIA-923 normalization exclusions and the 2024 EIA-860 BPAT plant crosswalk.

| Field | Measured result |
|---|---:|
| Excluded BPAT wind monthly source cells | 0 |
| Affected BPAT wind plant IDs | 0 |
| Excluded valid numeric BPAT wind cells | 0 |
| Excluded numeric BPAT wind generation | 0 MWh |

The artifact reports **no excluded EIA-923 WND source rows intersecting the 2024 BPAT EIA-860 plant crosswalk**. Therefore, observed exclusions within this specific mapped BPAT population cannot explain the previously verified 1,980,701.41 MWh EIA-923–EIA-930 difference. This audit does not certify perfect source completeness outside the matched plant population or establish the root cause of the discrepancy. [CI #41167672506](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41167672506) passed.

## Evidence status of the 1.981 TWh wind discrepancy

| Possible cause | Verified evidence | Status |
|---|---|---|
| Missing EIA-930 BPAT WND hourly timestamps | 8,784/8,784 timestamps observed | Missing timestamps ruled out |
| Excluded EIA-923 WND cells at BPAT-mapped plants | Zero BPAT WND excluded monthly/numeric cells in [run 41167672392](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41167672392) | Unsupported in the mapped population |
| Decimal-suffix plant-ID join error | No observed x.0 plant IDs in official source scan; normalization fixed | Unsupported by observed ID format |
| Different EIA-923 plant and EIA-930 BA reporting boundaries | 28 BPAT-mapped EIA-923 plants, EIA-930 only BA-level WND | Open; independent assignment audit required |
| Curtailment, losses, transfers, or accounting adjustments | No independent decomposition | Unresolved; never infer magnitudes from the difference |

Do not reassign national unmatched plants or other-BA generation to BPAT. Next: independently corroborate which of the 28 mapped wind plants report operational output in BPAT's EIA-930 BA boundary. Without source-specific evidence, retain the 1,980,701.41 MWh difference as an unresolved descriptive accounting gap, not a calibrated physical model parameter.
