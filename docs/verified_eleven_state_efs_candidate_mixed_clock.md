# Actual archived 11-state EFS + candidate four-state LAF mixed-clock sensitivity

**Verified successful Actions run:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41764316720

The experiment combines three **existing, independently retrievable** repository artifacts, rather than inventing load profiles:

1. Official NLR EFS Reference/Moderate core-11 state-hour demand aggregate, run 41265678862.
2. Pre-existing **seven-state** source-network-LAF-derived zonal load pilot, run 41276635829; those seven original state-hour-zone allocations were retained unchanged.
3. A numerically conservative **four-state candidate LAF** table for CA, NV, OR, WA, from the archived real Western bus network and the pinned `Pd/full_state` formula, run 41763391214. This table excludes 157 post-LAF-generated offshore auxiliary buses and retains both original-source-denominator crossing buses, but the original `full_state` field and GIS provenance remain **unverified**.

For each EFS state `s`, local ordinal `h` and ReEDS receiving zone `z`, the candidate new-state allocation is `MW(y,s,h,z) = EFS_MW(y,s,h) * candidate_LAF(s,z)`. Seven-state allocations are read from the old artifact rather than recomputed. The fixed-clock compatibility transform uses `((h + fixed_offset_s - 1) % 8760) + 1`, with +7 hours for AZ/CO/ID/MT/NM/UT/WY and +8 hours for CA/NV/OR/WA, following pinned upstream implementation. It is **not** independently verified physical UTC.

## Actual measured candidate results

| EFS planning year | Combined local-ordinal peak MW | Pinned mixed-clock peak MW | Difference MW | Candidate allocated annual TWh |
| --- | ---: | ---: | ---: | ---: |
| 2030 | 134,963.152 | 134,986.689 | +23.537 | 768.246784 |
| 2040 | 148,896.228 | 148,928.072 | +31.845 | 848.884570 |
| 2050 | 170,566.345 | 170,602.315 | +35.970 | 972.297918 |

**Both annual sums are the same** before/after applying circular source-state-hour shifts, within floating point precision. The candidate four-state allocation conserves source-hour mass, and seven-state source-to-zone factors were independently checked for constancy and left untouched. A source-hour load in a partially covered state is not assumed to be wholly Western: previous split-state Western fractions remain below one where applicable.

The source has 11 × 3 × 8,760 = **289,080 source-state-hour records**. The result report gives the actual zonal output row count, zero-weight zones omitted from output, source-to-zone checks and each planning year's peak ordinals. All three years' local-ordinal peak occurs at **5417**, and fixed-offset comparison peaks at ordinal **5424**. The shifts change peak *height* slightly as well as hour alignment, unlike the seven-state all-+7 pilot.

## Critical interpretation / restrictions

- These are **real EFS source demand series with an inferred geographic allocation hypothesis**, not observed 2030–2050 dispatch or verified regional load forecasts. The four-state `full_state` geography was not independently recovered.
- A fixed-hour rotation is a reproduction of pinned PyPSA-USA behavior, **not** proof of daylight-saving treatment, EFS hour-ending convention or actual simultaneous UTC. Thus a 23–36 MW difference is a **methodological sensitivity**, not verified physical Western peak bias.
- This does not resolve NARIS–ReEDS interface-vintage compatibility, calibrated generator availability, line flow physics, missing geography outside the chosen 11 states, or cost/capacity planning assumptions. **No full Western calibrated OPF was solved.**
- The figures should not be used as investment, generation adequacy, reliability or emissions projections.

## Reproduction and evidence

Source code: `src/energy_transition/efs_eleven_state_candidate_clock.py`. Regression tests: `tests/test_efs_eleven_state_candidate_clock.py`. Workflow: `.github/workflows/efs-eleven-state-candidate-clock.yml`. Artifact name: `efs-eleven-state-mixed-clock-candidate-report`, JSON `efs-eleven-state-candidate-clock.json`.

The run deliberately **fails closed** on altered seven-state allocations, duplicate/missing hours, non-finite/negative weights, nonconserving candidate weights, missing four-state source coverage and unsigned admission claims. Legitimate zero-weight zones are preserved in candidate provenance but not expanded into artificial zero-MW hourly series.

**Next major evidence gap:** independently reconstruct two crossing buses' original `full_state` geographic source labels (plus state/county ReEDS allocation semantics), then compare the candidate with authoritative EFS/renewables time definitions and official Western transmission/zone crosswalks before considering empirical admission.
