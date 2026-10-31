# Verified EIA plant-ID serialization audit — 2024

Evidence: [successful GitHub Actions run #41161308306](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41161308306), using the archived `eia2024-plant-ba-qualification-match` artifact from run `41085325552` and producing `bpat-wind-plant-id-format-2024`.

| Audit field | Observed |
|---|---:|
| Source rows scanned | 1,988 |
| Unique raw plant IDs | 1,650 |
| Unique normalized plant IDs | 1,650 |
| Decimal-suffixed plant-ID rows | 0 |
| Canonical IDs with multiple raw forms | 0 |

**Interpretation:** Decimal-suffix normalization is an important defensive code fix, but the particular archived source-qualified dataset contains no `.0` plant IDs and no normalization collisions. The change therefore cannot be credited with reconciling the previously observed **1,980,701.41 MWh** BPAT EIA-923 versus EIA-930 wind difference.

**Scope:** The source artifact includes 1,988 qualification rows across the audited plant population; these are **not** 1,988 BPAT wind plants. The separately verified BPAT wind concentration analysis identifies 28 BPAT-matched wind plant records. This audit checks identifier serialization only, not the accounting or population differences between EIA-923 and EIA-930.

Validation: [CI #41161308283](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41161308283) passed.
