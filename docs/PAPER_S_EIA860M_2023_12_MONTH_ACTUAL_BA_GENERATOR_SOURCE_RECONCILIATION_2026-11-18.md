# Paper S: 2023 official EIA-860M 12-month generator BA roster and EIA-930 scope reconciliation (2026-11-18)

## Execution evidence, source boundaries
**Successful** workflow [44391834613](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44391834613); verified source artifact **14472021718**. All twelve official preliminary monthly EIA-860M Operating workbooks were downloaded, month-identified, SHA256-inventoried, and processed; July original SHA256 independently pinned to `9a7b3f4051f1edb55f4d6508a1b963d2b344d687de6ea464ac538f2929122510`. The observed EIA-930 full-year BA net MW comes from successful [44246001519](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44246001519), artifact **14406998900**. This is a **generator-population-source coverage diagnostic**, NOT a source-certified EIA-930 physical metered fleet, BA=state match, verified observed capacity factor or ReEDS external model validation.

Completed monthly outputs: **96 month×BA×fuel operating generator nameplate cohorts**, **192 month×BA×fuel×reported/adjusted observed net-MW comparisons**, complete month-specific source SHA256 inventory and physical-state breakdown.

## 2023 July independently comparable original nameplate versus reported BA solar

| BA | July 2023 official EIA-860M OP source solar nameplate MW | Reported BA solar peak MW | July source net MW > candidate source OP nameplate hours |
|---|---:|---:|---:|
| IPCO | 478.3 | 459 | 0 |
| PNM | 546.3 | 580 | 12 |
| PSCO | 1666.9 | 1806 | 37 |
| WACM | 243.9 | 286 | 115 |
| **total exceedance BA-hours** | | | **164** |

Previous **narrower** July EIA-930A Schedule 2 identified roster: IPCO 473.5 MW, PNM 544.0 MW, PSCO 1666.9 MW, WACM 161.9 MW; excess reported solar BA-hours **324** = 12 PNM +37 PSCO +275 WACM. Under actual July monthly EIA-860M main-Operating BA source-code candidate, July WACM solar changed **161.9 -> 243.9 MW**, and WACM reported hourly excess changed **275 ->115**. These are changes to the **subset denominator definition**, not new physical plant performance evidence.

## Exact ID basis for WACM additional capacity

Source-keyed exact July generator ID set difference, crosschecked against previously official-July-matched 22 EIA-930A identifiable WACM PV rows (July run 44242291685):

- 22 shared ID rows = 161.9 MW;
- **25 additional EIA-860M official July Operating PV ID rows = 82.0 MW**;
- all 47 July official WACM PV generator ID rows = 243.9 MW.

Additional 25 records by source *physical state*:
| State | Generator ID rows | Added MW |
|---|---:|---:|
| CO | 21 | 39.6 |
| NM | 1 | 30.6 |
| NE | 1 | 8.5 |
| UT | 2 | 3.3 |

The 15 *different* WACM EIA-930A source-roster rows lacking both original and alternate plant-generator ID pairs remain **unmatched, unknown 2023 July operating identity**. No row-level inference equates those 15 source entries to the 25 newly covered IDs. The complete July EIA-860M WACM source PV population is **CO 201.5, NM 30.6, NE 8.5, UT 3.3 MW; no WY PV**. The **Wyoming 150 MW date/identity-missing EIA-930A row** is NOT authenticated by this source.

## Actual whole-year same-month screening results (not true observed CF)

| BA-fuel | Source reported EIA-930 BA-hours above candidate same-month EIA-860M OP nameplate | Months with any exceedance |
|---|---:|---:|
| IPCO solar | 14 | 1 |
| PNM solar | 85 | 8 |
| PSCO solar | 696 | 7 |
| WACM solar | 523 | 7 |
| WACM wind | 2 | 2 |
| Other 3 BA wind | 0 | 0 |

The 2023-06 PSCO raw reported solar spike **15,914 MW** (adjusted 1,327 MW) and 2023-06 WACM wind spike **7,194 MW** (also adjusted 7,194 MW) are **separately flagged unresolved source-QA exceptions** and therefore these raw yearly counts are descriptive and not independently validated physical exceedances. A source-by-source corrected/adjusted sensitivity remains required. The PNM, PSCO, WACM solar source-roster mismatch persists outside July in several months even with month-specific EIA-860M inventory; exact generation accounting/boundary remains unresolved.

## Reproducibility package
The conversation-local verified source-derived `Paper_S_2023_12_Month_EIA860M_EIA930_Reconciled_Scope_Audit_2026-11-18.zip` contains all **six original successful workflow CSV/JSON outputs**, new exact-ID crosswalk `Table_R1`, 25 extra IDs `Table_R2`, crosswalk summary `Table_R3`, 96 monthly reported exceedance flags `Table_R4`, annual BA-fuel totals `Table_R5`, `reconcile.py`, README and SHA256 provenance manifest. This is an available conversation output, **not a GitHub release artifact**. Original independent source authenticating GitHub artifacts remain authoritative.

## Research conclusion and limits
This is an actual stronger **2023 monthly contemporaneous capacity-scope screening**. It shows part of the previously apparent WACM solar missing capacity came from the EIA-930A identified subset omission, but cannot demonstrate EIA-930 hourly BA solar boundary equals EIA-860M BA-code generator set. The paper's original 1,440 fixed LP, 360 new 2×2 LP, 2,880 new 3×3 LP, 2,160 ATB, and C-2 experiments are unchanged. Do NOT report authentic model skill, annual CF, plant physical exceedance, or BA=state verification based on this screen.

**Next**: Compare EIA-930 raw-versus-adjusted yearly exception counts in the 192 contemporaneous month cohorts, source-audit BA solar reporting membership (especially WACM 25 extra IDs and 15 identity-less entries), and draft manuscript SI under strictly descriptive source diagnostics.
