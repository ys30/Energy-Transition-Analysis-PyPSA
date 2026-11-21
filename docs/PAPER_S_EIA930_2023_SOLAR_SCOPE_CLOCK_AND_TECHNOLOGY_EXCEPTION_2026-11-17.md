# Paper S — 2023 July EIA-930 solar BA reporting-scope and clock diagnostic (2026-11-17)

## Source and prior independently authenticated anchors

This is a **descriptive re-audit of source data already obtained**, not a new physical generator reconciliation or EIA-model external validation.

- Official EIA-930 **reported net MW**, the verified July 2023 common 160-hour BA observation CSV, source SHA-256 `0e72513a99c920391c0fc51a1691e84780ca5da81ba0c34b2fe218ed3fbc2f5a`.
- Official EIA-930A 2023 workbook and extracted four-BA `SCH 2`/`SCH 4` generator evidence, official workbook SHA-256 `ed8008bf4f5cbb0799d5a99b4dbc806e892eb150a9b357a709b582a93e28676f`. Same source record set previously identified and cross-checked using 2023 July EIA-860M: **91 PSCO and 22 WACM** source-identified Solar Photovoltaic generator rows, identical nameplate and BA code; 8 PSCO later-2023 generators not in July Operating. July EIA-860M verified run [44242291685](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44242291685), artifact 14399717341.

## Deterministic exceedance-time and source-category findings

160 common UTC hour-end observations per BA: July 1 08:00 to July 7 23:00 UTC inclusive; Denver clock America/Denver (MDT, UTC−6 for July).

| Solar BA | Eligible identifiable SCH2 MW | Max reported net MW | Hour of max (UTC) | Maximum difference (MW) | Hours above roster | Dates with exceedances | Local hour range |
|---|---:|---:|---|---:|---:|---:|---|
| **PSCO** | 1666.9 | 1806 | 2023-07-03 18:00Z | **139.1** | **14/160** | **4** | 09:00–17:00 MDT |
| **WACM** | 161.9 | 277 | 2023-07-01 18:00Z | **115.1** | **50/160** | **6** | 08:00–19:00 MDT |

Dates with positive exceedance: PSCO July 1–3 and 7; WACM July 1–4 and 6–7. The summed positive exceedance indicators, **1062.4 and 3223.0 MW×one-hour records** respectively, are only descriptive discrete-horizon arithmetic; they are **not certified physically integrated MWh shortfalls**. An alternative missing-source interpretation cannot be inferred from timing alone.

**Schedule 4 technology check.** The audited 322-row official EIA-930A four-BA (PNM, PSCO, IPCO, WACM) wind+solar export contains **zero `SCH 4` solar entries**; all nine relevant `SCH 4` entries are **wind** (PNM eight, IPCO one). Thus **adding observed Schedule 4 solar capacity from this scoped workbook cannot explain** either solar discrepancy. This does **not** rule out dynamic transfers, ambiguous BA accounting, source omissions or trade/scheduling behavior not represented in the scoped generator rows.

**WACM 15 undated/unidentified rows** = nominal **376.3 MW** but neither original nor alternate plant+generator IDs, and no verified July-2023 operating status. These are cross-state, cross-technology candidate records:

| Technology | Physical state | Rows | Candidate MW |
|---|---|---:|---:|
| Photovoltaic | AZ | 2 | 58.3 |
| Photovoltaic | CO | 8 | 69.0 |
| Photovoltaic | NM | 1 | 1.0 |
| Photovoltaic | SD | 1 | 80.0 |
| Photovoltaic | WY | 1 | 150.0 |
| Photovoltaic | unresolved | 1 | 6.0 |
| **Solar thermal with energy storage** | CO | **1** | **12.0** |

Importantly, the 12-MW solar-thermal-with-storage source record **cannot silently be treated as photovoltaic capacity** when evaluating ReEDS source PV, even as a hypothetical geography weighting. The 150-MW Wyoming row is still unidentifiable, not proof of 2023 WACM Wyoming production.

## Evidence-limited inference and next gate

1. *Necessary-condition failure*: the identified July Operating Schedule 2 generator subset cannot be assumed a complete BA net-generation denominator at the reported hours. This is a coverage/definition finding, not proof that any generator exceeded its physical nameplate.
2. An EIA-930 **BA** net MW series cannot be equated to modeled **state** source CF, independent of plant ID matching. The earlier same-weather 160-hour shape comparison is an explicitly limited proxy and not validated observed capacity factor.
3. Need original 2023 BA reporting conventions for solar net output, missing installations including id-less rows, local BA area exchanges, source EIA-930A roster completeness and verified generator monthly operating membership. Check full-year observation coverage only after historical BA crosswalk is available.

## Reproducible independent output

A conversation-local audit bundle `Paper_S_2023_July_BA_Solar_Scope_Clock_Audit_2026-11-17.zip` includes **Table E15** (BA peaks and timestamps), **Table E16** (seven Denver local dates), **Table E17** (320 BA-solar-hour records), **Table E18** (seven WACM undated geography/technology categories), source digests, explicit nonvalidation manifest and notes. **The ZIP is not a GitHub release**. Original Paper S 1440 LP, 360 2×2 new LP, 2880 3×3 new LP, 2160 ATB, and Paper C-2 results remain unmodified.

**Suggested SI-safe wording:** “A July 2023 source-year reconciliation revealed reported BA solar net power above the eligible identified generator-nameplate subset in 14 PSCO and 50 WACM hours. The discrepancies occurred in multiple daytime periods; the four-BA EIA-930A Schedule 4 export contained no solar generators. Additional WACM unidentified/undated records were geographically heterogeneous and included a solar-thermal installation. These conditions preclude treating candidate roster nameplate sums as verified BA hourly capacity-factor denominators.”
