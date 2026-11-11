# Paper S — ReEDS2022 authentically clocked 2012 wind/PV source-driven storage LP pilot (10 Nov 2026)

**Independent data/source branch completed, original EFS2020 synthetic Wave A/B study preserved unchanged.** GitHub Actions [#42961091781](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42961091781) **SUCCESS**: original publisher MD5 verification of three source HDF5 files and three companion wind/PV supply-curve/county mapping CSVs; 2012 fixed CST native time-index checks; independent state-BA crosswalk and real reV-model-derived capacity-factor aggregation; 16 full-year original-constraint HiGHS LP solves; source and solver output reconciliation.

## Authenticated primary inputs

- ReEDS2022 *EFS_REFERENCE* demand [Zenodo 18461543](https://zenodo.org/records/18461543), original HDF5 `demand_EFS_REFERENCE.h5`, MD5 `7b2055d43200744a16a8c4fed68b1a17`. Native projected demand unit gross end-use MWh/h, **hour-ending**, with 2012 fixed CST UTC−06:00, Feb 29 included and Dec 31 omitted (8760 labels for 2030 model-year load).
- ReEDS land wind **v1** [Zenodo 18422200](https://zenodo.org/records/18422200), original `cf_wind-ons_reference_ba.h5` MD5 `8fd010e1d38f9a8591ba58c9eff1a368`; 804 source resource-class / BA curves, 131,400 hourly source records over 15 calendar years; publisher describes capacity factor **instantaneous on the hour** in fixed CST.
- ReEDS utility solar PV **v1** [Zenodo 18407660](https://zenodo.org/records/18407660), original `cf_upv_reference_ba.h5` MD5 `398165a0a7ec5c21d3e891a28162a217`; 257 BA/class curves, 131,400 hourly source records. Raw factor in `MW_AC,grid / MW_DC,array` converted to `MW_AC,grid / MW_AC,nameplate` by publisher ILR **1.34** (with small publisher decimal rounding tolerated before clipping).
- Wind/PV class resource-potential supply tables `sc_wind-ons_reference_ba.csv` MD5 `f5b5665c7133978bb09c3bb12c77dfba` and `sc_upv_reference_ba.csv` MD5 `d2545544d96ffb1a4645750830856606`; exact class|pBA column matched to source `MW` potential for within-technology CF capacity weights.
- Original identical `county2zone.csv`, MD5 `f269adef29b6d96317a845f6129b5ad9`; only wholly single-state BAs admitted. Four selected states have **100% source county coverage under this rule**: AZ 15/15 counties, 4 BAs; CO 64/64, 2 BAs; ID 44/44, 3 BAs; WY 23/23, 4 BAs. This is *county footprint coverage*, **not** real installed generation/available capacity calibration.

Actual 2012 reference-hour keys are `2012-01-01T00:00:00-06:00` through `2012-12-30T23:00:00-06:00`; both resource curves and state load share these **physical timestamp labels**. Original upstream HDF5 also provides the real preceding `2011-12-31T23:00:00-06:00` capacity factor needed for interval approximation at t=0. The source was validated in UTC absolute instants without mistaking equivalent timezone objects (fixed UTC−06:00 vs Etc/GMT+6) for different clocks.

## Real-source pilot model and scientific limitation

For each state, 2030 projected demand from original ReEDS2022, and 2012 real modeled wind and solar hourly CF *shapes* drawn from published weather/technology sources. Assumed installed renewable nameplate `0.9 × state 2030 peak demand`, with wind/PV **50%/50%** of that assumed installed capacity; this is a model scenario, **not** ReEDS buildout or observed fleet. Original frozen SciPy/HiGHS LP model with zero versus four-hour storage, original battery power ratio 0.25 peak MW, cyclic terminal SOC, efficiency 90%, assumed $5/MWh renewable input versus $90/MWh firm generation. Two boundary conventions:

1. **Trapezoidal previous instant:** `CF_hour_mean(t) ≈ [CF_instant(t-1) + CF_instant(t)]/2` for the hour-ending load interval. True preceding 2011 source row is used at year start. This is a clear numerical integration **assumption**, not publisher-certified measured energy.
2. **Instantaneous end label:** `CF_hour_mean(t) ≈ CF_instant(t)` as separate sensitivity, not presented as correct hourly energy.

No real installed capacity, transmission dispatch, battery CAPEX/degradation/market revenue or empirical resource adequacy inferred. Not a PyPSA network OPF. Source files are **modeled meteorological resource outputs**, not meter-observed wind/PV generation.

## Verified 2030 4h-storage source LP outcomes

| State | 4h discharge MWh, trapezoidal | 4h discharge MWh, direct instant | Direct vs trapezoid difference | 0h→4h firm displacement MWh, trapezoidal | Illustrative original cost reduction, USD million (0h→4h) |
|---|---:|---:|---:|---:|---:|
| Arizona | **845,767.693** | 923,712.241 | +9.216% | 845,767.693 | 71.420 |
| Colorado | **102,841.862** | 111,134.488 | +8.063% | 102,841.862 | 8.684 |
| Idaho | **16,196.871** | 16,674.266 | +2.947% | 16,196.871 | 1.368 |
| Wyoming | **6,344.536** | 6,860.207 | +8.128% | 6,344.536 | 0.536 |

These are source-authenticated numerical model results in four **different state-level** source systems, not changes from the old p-zone EFS2020 LP (which was based on synthetic renewable shapes). The direct end-instant vs trapezoidal difference (roughly 3–9%) shows why the original point-forecast/hour-ending timestamp distinction **cannot be glossed over**. Differences are not forecast uncertainty or confidence intervals.

Original data:
- HDF5 and CSV metadata audits: [source intake program](../src/energy_transition/reeds2022_real_resource_intake.py)
- Real-source aggregation plus LP: [state model program](../src/energy_transition/reeds2022_real_wind_pv_state_storage_lp.py)
- [CI #42961091781](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42961091781), artifact `paper-s-reeds2022-authentic-wind-pv-state-subset-LP-and-source-QA` with 16-case results, capacity/potential summary, official source calendar, four state coverage, and honest source limitations. No publisher HDF5/CSV source bytes were copied into CI artifacts or repo.

## Scientific and legal gates still open

- **Physical hour energy support:** Publisher marks CF **instantaneous**, demand **hour-ending**. Two explicit integration models used, neither is a source-author's time-integrated capacity factor certification. A matched hourly interval-average model may be adopted with this assumption and sensitivity; **do not call it exact observed generation**.
- **Installed fleet and resource potential:** supply curve capacity weights represent *resource potentials*, not realized capacity deployment or historical meter generation. 50% wind / 50% PV assumed. Need independently sourced installed/future buildout to produce geographically calibrated supply.
- **Optimal service window analysis:** the old five-window near-optimal conclusions have **not yet** been recomputed for this new source/data model. Full-year 0h/4h cost pilot alone does not authenticate new temporal near-optimal envelopes.
- **Rights:** ReEDS demand/wind/PV 2026 Zenodo releases are publicly accessible, but their public displayed Rights field was not verified to contain a specific positive named reuse/redistribution license. Data bytes and high-resolution derived CF tables are withheld pending source-specific clearance. Existing outputs are short original optimization summaries.
- **Separate original EFS2020 vintage:** its `LocalHourID` physical clock remains uncertified; this new ReEDS2022 source makes no retroactive claim to resolve that original data's hour semantics.
- **Research interpretation:** a weather-driven storage LP sensitivity pilot, not calibrated Western network dispatch, energy prices, actual savings or reliable local-hour grid service.

**Decision:** a legitimate, bounded real weather *source-input* replacement branch has now produced accepted full-year LP numerical outputs for four states. It does **not** replace Paper S's frozen original published-source synthetic-wave main figures as if the only changed factor were weather. A manuscript revision must transparently frame this as a **new state-level ReEDS2022 analysis** with source-year 2012 and explicitly assumed capacities and hour-integration.
