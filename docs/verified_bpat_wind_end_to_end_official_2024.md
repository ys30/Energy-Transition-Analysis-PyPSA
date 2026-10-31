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
