# Paper S — common-AC source-capacity normalization changes storage sizing conclusions (2026-11-11)

## Reproducible authenticated-source results

1. ReEDS 2012 source PV original v1 publisher record: https://zenodo.org/records/18407660 — original utility PV CF is AC output / DC array MW; multiply once by documented 1.34 ILR to express per AC inverter-nameplate MW. Wind AC and solar AC now use a common nameplate denominator.
2. Original 180-case 2030 source-denominator model: [GitHub Actions run 43051615043](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43051615043). Original source-weather data from HDF5 MD5-verified run 42962740548. Original label-source weather instantaneous, approximated to hourly supply with a trapezoid and first-hour endpoint fallback.
3. New independent common-AC 180 HiGHS LP solutions: [GitHub Actions run 43058074434](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43058074434), SUCCESS; 180 fully matched old/new model rows, 144 storage scenarios each paired with corresponding zero-storage control. Artifact `paper-s-reeds2022-2030-common-ac-pv-ilr-180-original-source-lps`.
4. Source-archive postprocessing of **144 incremental storage-sizing comparisons (72 fixed power 4→8h and 72 fixed 4/8h duration power 10→25% peak)** for old vs AC sources: [GitHub Actions run 43058722043](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43058722043), SUCCESS. Artifact `paper-s-reeds2022-ac-versus-original-144-marginal-storage-hurdles` with two exact 72-row CSVs and JSON manifest.

## Common 2030 example (r=1.5× 2030 state demand peak, nominal 50% wind nameplate, 4h battery at 0.25 peak power)

**Variable operating cost avoided by 4h storage compared with no storage** (USD/year, positive; no battery CAPEX):
| State | Original mixed source-nameplate convention | Common AC nameplate |
|---|---:|---:|
| AZ | 218,243,846 | 387,849,800 |
| CO | 64,082,810 | 162,251,900 |
| ID | 21,144,468 | 55,487,100 |
| WY | 11,610,384 | 27,588,170 |

**Fixed power, extend 4h → 8h (2030, r=1.5×, wind share 0.5, P=0.25× peak):**

| State | Original extra savings USD/year | Common AC extra savings USD/year | Original energy-only hurdle $/kWh-year | Common AC energy-only hurdle $/kWh-year |
|---|---:|---:|---:|---:|
| AZ | 76,756,534.78 | 212,589,545.18 | 3.955503 | 10.955400 |
| CO | 20,810,090.47 | 71,251,564.86 | 1.816840 | 6.220671 |
| ID | 6,727,986.28 | 21,517,738.64 | 1.292849 | 4.134846 |
| WY | 4,315,881.97 | 10,866,006.24 | 1.406283 | 3.540569 |

**Fixed 4h duration, increase storage power 10% → 25% state peak** (also increases energy capacity by 4 × added power):
| State | Original extra savings USD/year | Common AC extra savings USD/year | Original power-only hurdle $/kW-year | Common AC power-only hurdle $/kW-year |
|---|---:|---:|---:|---:|
| AZ | ~105,282,700 | ~208,904,400 | 36.170289 | 71.769968 |
| CO | ~29,134,310 | ~83,468,310 | 16.957285 | 48.581755 |
| ID | ~9,492,355 | ~26,699,230 | 12.160332 | 34.203470 |
| WY | ~5,487,196 | ~13,328,560 | 11.919617 | 28.953091 |

These numbers are not net economic benefit or actual financial investment viability. With an *illustrative* annual energy capacity annuity of $10/kWh-year and zero incremental power/fixed costs, **AC-normalized Arizona 4h→8h only just exceeds the energy-only hurdle (10.9554 vs 10)**; all other three states in this representative central case fail it. This reverses the earlier conclusion that all four failed under the heterogeneous source-denominator mix. It also shows the importance of original-source unit conventions.

## Crucial equivalence warning for reviewers

**These are different *physical hypothetical installed PV portfolios*, not simply a bookkeeping rescaling of a fixed installed PV array.** At a fixed common scenario ratio r and nominal 50/50 wind share, the new common-AC experiment has an assumed DC array of 1.34 × the solar inverter AC MW whereas the old source-denominator simulation implicitly applied half the total ratio directly in DC units. The fixed ratio therefore represents a different actual source solar DC nameplate. Wind and source weather, demand, cost objective, storage power/energy and solver constraints remain identical. Do not treat the increase in savings as an empirical observation or estimate of a data-processing bias in real operating costs; it is a **controlled normalization/scenario-definition sensitivity**.

ReEDS PV publisher's 1.34 ILR is an assumed plant technology parameter; the data are 2012 modeled instantaneous weather CF, the demand is 2030 scenario projection, and neither is observed 2030 fleet energy. Trapezoidal hour-energy approximation (including first-hour endpoint) is not publisher-certified. Resource capacity county weights refer to developable potential not installed siting. The LP assumes within-state copperplate, no transmission, reliability, firm-capacity credit, battery fixed cost, degradation, financing, ancillary services, or build-out costs.

## Manuscript revision required

- Update headline economic interpretations to give the **AC-normalized scenario** a separately labeled main results section and move original mixed source-denominator outcomes into a diagnostic sensitivity/appendix, with exact labels.
- Include raw source unit conversion `CF_PV,AC = min(1, 1.34 × CF_PV,source)`, and separate stated installed MW_AC vs implied PV array MW_DC. Tiny >1 values from rounded publisher max (0.7463×1.34=1.000042) are capped with tolerance 1e-4; larger inconsistencies trigger error.
- Introduce 2030 180-LP matched old/new results plus 144 source-archive incremental comparisons before making optimization-economic statements; figures should use new AC-normalized values, not the legacy headline plots without relabeling.
- Primary conclusion is conditional source-backed **operational avoided-cost sensitivity**, not investability, NPV, or reliability.
- A meaningful next check is 1.34 vs nearby ILR assumptions (strict bounds), storage efficiency and operating cost scenarios with physically consistent AC bases; this is secondary to checking original time-label energy integration.
- Legacy EFS2020 original Paper S experiments unchanged. PR remains Draft until CI fully green and scientific caveats resolved.
