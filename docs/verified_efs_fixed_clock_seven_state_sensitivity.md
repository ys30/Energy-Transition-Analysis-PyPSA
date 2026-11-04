# Seven-state real EFS fixed-offset chronology sensitivity

**Verified successful GitHub Action:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41754815574

This read-only exercise uses the actual archived seven-state EFS-to-PyPSA-USA-LAF zonal pilot, not simulated source profiles. It audits the fixed UTC-hour-ID permutation in **pinned upstream PyPSA-USA** commit `338af9912addbaf038c6098fe27e1e6ef099d8aa`:

```text
compatible_utc_hour_ordinal = (local_hour_id + state_fixed_offset - 1) % 8760 + 1
```

All seven previously accepted pilot states—Arizona, Colorado, Idaho, Montana, New Mexico, Utah and Wyoming—are mapped to **+7 h** by that pinned upstream implementation. Thus the aggregate of the *same seven states* is merely circularly rotated, not temporally reweighted.

## Measured real-input sensitivity

| EFS planning year | Peak seven-state allocated load (MW), local vs pinned shift | Peak ordinal, local → shifted | Seven-state annual allocated energy (MWh) |
|---|---:|---|---:|
| 2030 | 48,930.88447 vs 48,930.88447 | 5297 → 5304 | 274,706,987.114 |
| 2040 | 54,656.82948 vs 54,656.82948 | 5297 → 5304 | 306,839,206.741 |
| 2050 | 62,503.90642 vs 62,503.90642 | 5297 → 5304 | 350,871,474.847 |

**60** state-year-zone sequences passed the exact permutation and annual-MWh conservation checks; the peak delta is **0 MW** for each target year. This confirms the expected mathematical invariance given the homogeneous +7 h shift, **not** that the local-hour axis is a physically synchronized Western UTC chronology.

Four excluded pilot states (CA, NV, OR, WA) map to **+8 h** in the same implementation. Expanding to them will require actual source-approved geography and time semantics: adding a different shift can alter coincident regional peaks. It is *not* valid to simulate their contribution by fabricating LAF coefficients.

## Interpretation limits

- Hour indices are source ordinals. No independently verified EFS source hourly timestamp conventions, intra-state split time zones, daylight-saving shifts, or hour-ending conventions.
- No externally verified correlation against actual wind/solar weather profiles, generator availability, or PyPSA UTC snapshots.
- The seven-state archive remains a spatial demand projection with an upstream compatibility experiment, not a calibrated full-Western power-flow, reliability, capacity expansion or economic dispatch result.
- Archive retention is limited by GitHub Actions; this report stores verified aggregate metrics but not the full raw EFS or network files.

**Reproduce:** `.github/workflows/efs-fixed-clock-sensitivity.yml`; source module `src/energy_transition/efs_fixed_clock_sensitivity.py`; input archived from run 41276635829; audit JSON artifact in run 41754815574.
