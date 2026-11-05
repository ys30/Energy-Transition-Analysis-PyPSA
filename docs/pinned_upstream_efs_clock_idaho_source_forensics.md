# Source forensic checkpoint: pinned PyPSA-USA EFS timezone implementation and Idaho limitation (2026-11-05)

## Summary

A source audit at **pinned PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa`**, the same version used by this project's original EFS acquisition path, establishes the *downstream PyPSA-USA transform* (not original NLR EFS 2020 publisher metadata).

Exact upstream files:
- [`workflow/scripts/build_demand.py` at pinned revision](https://github.com/PyPSA/pypsa-usa/blob/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/scripts/build_demand.py)
- [`workflow/scripts/constants.py` at pinned revision](https://github.com/PyPSA/pypsa-usa/blob/338af9912addbaf038c6098fe27e1e6ef099d8aa/workflow/scripts/constants.py)

The `ReadEfs._apply_timezones()` implementation uses an **entire-state fixed timezone** from `STATE_2_TIMEZONE`: `US/Mountain` becomes **+7 source-hour positions relative to UTC**, `US/Pacific` **+8**, `US/Central` +6 and `US/Eastern` +5. It computes `UtcHourID=LocalHourID+utc_shift` and wraps past 8760 by subtracting 8760. Then `_build_datetime()` uses a **2018 nonleap year template** before replacing the displayed model year. The comments explicitly state the EFS data “does not do leap-years.”

The pinned `constants.py` maps **Idaho (`ID`) to `US/Mountain` only**, even though the same file explicitly cautions that `STATE_2_TIMEZONE` **does not account for states with multiple time zones or exceptions**. Other relevant pinned mappings include CA/NV/OR/WA → Pacific and AZ/CO/MT/NM/UT/WY → Mountain.

## Relationship to the independent EFS2020 / ReEDS2022 comparison

[Verified full original-source hourly comparison](original_efs2020_vs_reeds2022_hourly_cross_release_audit.md) showed 30 non-Idaho state/model-year series with a source-index shift of −2 or −3 hours and each overlapping comparison below 1 MW error. [Verified nonwrapping check](efs2020_reeds2022_nonwrapping_lag_review.md) confirms the shift selection is not due to circular Jan/Dec edge wrapping. Idaho is systematically different, with best one-lag residual MAE 17.264, 19.304 and 22.100 MW in 2030/2040/2050, and source-level numerical two-shift mixtures remain materially imperfect.

**What source code now establishes:** the pinned downstream PyPSA-USA EFS workflow **made a simplifying state-timezone assumption**, which does not model geographically split states and gives Idaho one fixed Mountain designation. The previously observed old-versus-new hour discrepancy therefore has a concrete software-provenance issue worthy of scrutiny.

**What it does not establish:** This PyPSA-USA code alone is **not proof** of why the *independent* 2022 ReEDS HDF5 differs by −2/−3 source-index hours; it does not say what original **2020 NLR EFS `LocalHourID`** meant (actual UTC, CST, local-standard/hour ending, weather year), and it cannot reveal which Idaho counties/loads were assigned Mountain/Pacific source clocks. A UTC+7/8 conversion and a ReEDS UTC−6 time index are *not* enough to derive the observed offsets without the upstream original EFS calendar convention and HDF5 indexing rules.

[Official EIA-930 reporting documentation](https://www.eia.gov/electricity/930-content/about.html) notes that Idaho Power (IPCO) reports its balancing-authority data in Pacific time despite being located in Mountain time. This is independent evidence of a potential Idaho time-label complication **for EIA-930 reporting**, not evidence that original EFS2020 or ReEDS2022 used IPCO's convention. Do not attribute the 83.44% two-shift regression fit to IPCO or Idaho's actual physical timezone split.

## New reproducibility gate

[`pinned-efs-clock-source-audit.yml`](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/pinned-efs-clock-source-audit.yml) retrieves the **exact upstream pinned commit** and checks all stated facts against the actual source files, then archives their SHA-256 and a machine-readable admission report. Its tests fail if the EFS `UtcHourID` formula, year wrap, state map, or upstream multi-timezone warning is changed. This is source-provenance verification, not source-clock certification.

## Scientific priority for manuscript

The most defensible immediate result is **cross-release hourly-source chronology is sensitive to upstream processing and documented single-state timezone simplification**, with a strong Idaho counterexample. The publisher/source authority chain remains unresolved. No EFS2020 to weather/NSRDB/WIND Toolkit hourly synchronization or real physical Western OPF is authorized based on this finding.
