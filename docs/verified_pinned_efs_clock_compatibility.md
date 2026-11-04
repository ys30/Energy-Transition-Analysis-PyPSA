# Pinned PyPSA-USA EFS clock compatibility audit

**Verified run:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41754320402

On 2026-11-03, source inspection of PyPSA-USA commit `338af9912addbaf038c6098fe27e1e6ef099d8aa` (the commit used to build the archived Western base network) confirmed that `workflow/scripts/build_demand.py` and `workflow/scripts/constants.py` implement the following **fixed-offset** EFS transformation:

```text
UtcHourID = LocalHourID + fixed_source_state_offset
if UtcHourID > 8760: UtcHourID -= 8760
hour_ordinal = UtcHourID - 1
calendar_template = 2018-01-01 + hour_ordinal hours
snapshot = template month/day/hour with EFS planning year substituted
```

### State-level shifts actually in the pinned constants

| Fixed offset | 11-state source labels |
|---|---|
| +7 hours | AZ, CO, ID, MT, NM, UT, WY |
| +8 hours | CA, NV, OR, WA |

The pinned constants choose *one* representative time zone per state. They do not handle intrastate exceptions (e.g., split-time-zone states). The code uses a fixed shift rather than hour-specific daylight-saving adjustments and a non-leap 2018 template, though the EFS scenario has planning years 2030, 2040, 2050. Its naive timestamp construction does not carry explicit `+00:00` UTC offsets in the returned index.

The [NLR EFS source catalog](https://data.nlr.gov/submissions/126) confirms scenario/year scope but does not independently certify the source CSV's local-hour timezone, DST or hour-ending convention. Passing the archived pilot's strict **1…8760 per-state-zone ordinal coverage** does not resolve those questions.

The code and CI evidence are in `src/energy_transition/efs_pinned_upstream_clock_audit.py` and `.github/workflows/efs-pinned-upstream-clock.yml`; the audit pins the upstream revision and records source SHA256 digests. It **never** treats compatibility as independent weather/renewables chronology validation.

**Status:** pinned upstream algorithm reproduced and source state offsets documented. Actual simultaneous UTC EFS–wind–solar hourly alignment, four blocked states, complete geography and empirically calibrated Western OPF remain **unverified**.
