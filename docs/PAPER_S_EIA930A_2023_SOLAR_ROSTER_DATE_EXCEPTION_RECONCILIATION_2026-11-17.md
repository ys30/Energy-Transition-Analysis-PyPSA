# Paper S — EIA-930A July 2023 solar roster-date exceptions (2026-11-17)

**Source-verified inputs:** Official EIA-930A 2023 previously authenticated generator-row export (original workbook SHA-256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`), official EIA-930 July 2023 common 160-hour reported net MW CSV SHA-256 `0e72513a99c920391c0fc51a1691e84780ca5da81ba0c34b2fe218ed3fbc2f5a`. Existing source extracts were re-opened and independently cross-checked. Reported and adjusted values coincide in the entire examined 160-hour PSCO and WACM solar cohorts; imputed columns are missing throughout. These findings are **candidate denominator exception triage, not external validation**.

## Actual date-classification results

| BA/fuel | Eligible SCH2 rows | Eligible candidate MW (operation date ≤2023-07) | Undated rows | Undated MW | Known-after-July rows | After-July MW (excluded) | EIA930 observed 160h peak net MW | Minimum unmatched peak MW | Breach hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PSCO solar | 91 | 1666.9 | 0 | 0 | 8 | 274.5 | 1806 | 139.1 | 14/160 |
| WACM solar | 22 | 161.9 | 15 | 376.3 | 0 | 0 | 277 | 115.1 | 50/160 |

**WACM:** As a diagnostic **only**, adding all undated roster rows increases the hypothetical candidate capacity from 161.9 to 538.2 MW and eliminates these 50 exceedances. This does not establish whether any such generator operated in July 2023 or belonged to the BA-measured source footprint. The undated WACM solar roster contains sites listed in Colorado, Wyoming, Arizona, New Mexico, South Dakota and unresolved geography; it is NOT an observed Wyoming solar denominator.

**PSCO:** The only eight additional excluded solar rows have original commissioning months Aug–Dec 2023 (known future relative to July). Adding their 274.5 MW merely to eliminate the 139.1 MW breach would be historically invalid. The PSCO gap remains unresolved by known eligibility data.

For the audited solar cohorts the **64 total observed breach hours** cannot be attributed to choosing reported rather than adjusted values (they are identical), nor to data filled with the imputed column (none). However, BA roster completeness, dynamic schedule/pseudo-tie treatment, net-vs-nameplate basis and historical operational state must still be traced. These are necessary bounds for a validated capacity denominator, **not** reasons to force observed capacity factors below one.

## Deliverables

Conversation-local `Paper_S_EIA930_Roster_Date_Exception_Audit_2026-11-17.zip` contains:
- `audit.py`: source-ref checks (pinned observed SHA256), date grouping and fail-closed 64-hour validation;
- `Table_E7_solar_generator_rows_with_date_group.csv`: all original PSCO/WACM Schedule 2 solar rows with provenance and date grouping;
- `Table_E8_date_exclusion_denominator_sensitivity.csv`: two-BA reconciliation;
- `Table_E9_reported_vs_adjusted_64_exception_hours.csv`: all 64 time-stamped discrepancies;
- `Figure_E5_roster_date_group_capacity_gap.png` and a SHA-256 manifest.

This archive is accessible through the conversation, **not falsely claimed to exist as a GitHub binary artifact**. Prior credible EIA 930/930A original source files and 2012/2023 ReEDS inputs remain unchanged. So do Paper S's frozen 1,440 original LPs, the 360 new 2×2 attribution LPs, 2,880 3×3 sensitivity LPs, 2,160 ATB cost comparisons, and Paper C-2.

## Next empirical acceptance gates

1. For WACM: resolve individual 15 unknown-commissioning-date generators against contemporary *2023* EIA-860 operating status; trace their BA participation and scheduling. No share-by-capacity approximation is accepted as an hourly power allocation without evidence.
2. For PSCO: inspect 2023 source roster omission/reporting definitions and 2023 July generator statuses, not the known Aug–Dec future units.
3. Reconcile Schedule 4, cross-BA shared generator 59975/CW1 (150 MW), and geographically misaligned BA/state footprints; check same-year **full-year** observed EIA-930 panel completeness.
4. Only after those are audited should the 160-hour exploratory proxy become a candidate external-validation calculation.
