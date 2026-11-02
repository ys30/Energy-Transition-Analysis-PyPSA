# CI-verified generator-level OP transitions (priority common-plant cohort)

Source [workflow 41488973218](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41488973218), successful at commit `04d543b11cc89436137b3ef43fd0698825179330`. This table describes original EIA-860 yearly generator statuses in 71 overlapping priority plants, **not** the full Western fleet.

| EIA plant | Generator | 2023 status | 2024 status in audited Operable/Proposed sheets | OP delta MW |
|---|---|---|---|---:|
| 2454 | 1 | OP | missing from current matched status inventory | -75.0 |
| 394 | 1 | OA | OP | +0.8 |
| 66183 | CWE | TS | OP | +207.9 |
| 66811 | CW3 | V | OP | +100.0 |
| 6704 | MT03 | OP | OS | -0.1 |
| 6704 | MT17 | OS | OP | +0.1 |
| 6704 | MT18 | OP | OS | -0.1 |
| 6704 | NASB1 | OP | OS | -1.0 |

These 8 transition rows sum to +232.6 MW. Continuing OP generator nameplate revisions contribute +20.0 MW. Reconciliation: +232.6 + 20.0 = **+252.6 MW**, year-over-year in the 71-plant common-priority subcohort.

Important: `2454 / 1` absent from the 2024 **Operable/Proposed** matched input is *not proof of retirement or cancellation*. Search the original 2024 `Retired and Canceled` sheet by **plant ID and generator ID** to classify this properly. More broadly, source status changes in year-end inventories are not necessarily proof of physical commissioning or outage causes.

The 2023–2024 status code names and historical capacity scope require source-vintage verification. Zero generator-to-PyPSA-original-bus electrical tie records independently verified. Exclude from actual empirical network dispatch pending POI and source network linkage.

## Follow-up resolved from original year-specific source sheets

[Successful five-case original EIA-860 audit 41489652926](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41489652926) confirms:

- Plant `2454`, generator `1`: **2024 Retired and Canceled**, status **RE**, fuel **NG**, nameplate **75.0 MW**. This resolves the prior one-sided Operable/Proposed file absence: the generator is present in the complete annual original source, but not the restricted status inventory.
- Plant `66183`, generator `CWE`: 2023 **Proposed**, status **TS**, 207.9 MW wind; 2024 **Operable**, status **OP**, 207.9 MW wind.
- Plant `66811`, generator `CW3`: 2023 **Proposed**, status **V**, 100.0 MW wind; 2024 **Operable**, status **OP**, 100.0 MW wind.

The three records account for **+232.9 MW** of the +252.6 MW OP nameplate delta. The other generator transitions collectively contribute -0.3 MW; continuing OP generators contribute +20.0 MW. This confirms source-year status changes, **not** the exact commissioning or retirement dates or an independently verified network tie.

**Correction of scope:** the previous `2454 / 1` absence was only from the restricted two-sheet matching input, not from the complete EIA-860 original workbook. Its current audited status is **RE** in 2024, with original sheet provenance. Update any manuscript or display using the older “missing in 2024” phrase.

