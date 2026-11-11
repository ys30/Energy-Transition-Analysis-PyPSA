# Paper S — submission gate assessment and four verified editorial fixes (2026-11-10)

**This is a public-safe status note, not a new empirical experiment or publication.** The private revised Word article is not committed to GitHub.

## Physical source/meteorological eligibility

1. **Actual wind/solar replacement is technically possible but not yet accomplished.** 2012 WTK site data can be requested at 60-min UTC resolution with `leap_day=false` ([official API](https://developer.nlr.gov/docs/wind/wind-toolkit/wtk-download/)); obtaining year-matched solar irradiance through an admissible NSRDB version, applying well-specified site-zone weights, and converting meteorological variables to turbine/PV capacity factors require additional provenance. No authenticated site-level weather → power profiles are in the Paper S certified LP source case. See [2012 candidate intake plan](verified_candidate_2012_renewable_resource_intake_plan.md).
2. **Original EFS2020 source `LocalHourID` physical clock remains uncertified.** ReEDS2022's [published CST/2012 convention](https://zenodo.org/records/18461543) does not authorize transferring that mapping to different original EFS2020 CSVs. Paper T Idaho -2/-3 source-index mixed offsets reproduce related-source numeric patterns but **do not prove physical UTC mapping**; the existing [six-gate admission tool](PAPER_T_V9_FAIL_CLOSED_TIME_JOIN_METHOD.md) still says `BLOCK_PHYSICAL_JOIN`. Requires publisher/source-author evidence, exact start/end-hour and leap/DST treatment and verified one-to-one source-to-weather crosswalk. The 2040 archived leap-label anomaly is not a source-clock fix.
3. **EFS original rights condition:** [official dataset notice](https://data.nlr.gov/node/126/license) allows no-fee dataset use/copy on condition the full notice accompanies copies and published work credits DOE/NREL/Alliance. Other datasets/code have separate rights and are not automatically cleared.

## Four corrections made in a revised **private** submission candidate

- Replaced contradictory **'zero terminal SOC'** in Discussion with the model's **cyclic terminal SOC (end SOC = initial SOC)**.
- Results 3.3 now states exact archived original annual near-optimal discharge intervals (2030, Wave A, p28 and p24): **Arizona 5,216,554.707–5,216,557.975 MWh; Wyoming 76,868.908–76,868.953 MWh**. Widths: **3.268 MWh**, **0.045 MWh**.
- Results 3.3 explicitly calculates the Arizona **27.136% reference-window relative spread** as 29,352.336 MWh / 108,166.156 MWh. This is not the fraction of annual discharge or capacity utilization; the comparable Wyoming 168-source-hour window width is 1,616.753 MWh.
- Both Methods 2.6 and Declarations 6.4 now identify **OpenAI ChatGPT** manuscript drafting/restructuring/language assistance; the author team remains responsible for correctness and publisher-specific disclosure approval.

Source of archived annual envelopes: accepted original-source `paper_s_eight_cost_capped_discharge_intervals.csv`; reference-window baseline: `E2_six_original_schedule_balances.csv`. **No new LP solve**. Private revised paper rendered successfully (8 pages, five main figures retained); the source/clock/weather gates were not represented as passed.

**Decision:** Paper S remains a valid *conditional source-ordinal synthetic dispatch diagnostic*, but is **not admitted as an empirical real wind/solar and EFS-synchronous research submission** until both scientific gates pass and replacement LPs are rerun.
