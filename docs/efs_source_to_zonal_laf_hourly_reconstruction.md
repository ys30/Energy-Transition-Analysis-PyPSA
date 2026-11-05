# Project B: full original EFS state-hour → archived LAF zone-hour reconstruction

## What this adds

The archive has already passed the numerical **staged zonal hourly CSV → Load-only NetCDF** comparison in [successful Actions run 42055638619](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42055638619).

A new independent audit now reconstructs the **preceding** part of that chain using archived provenance-bearing artifacts:

- Source 11-state 2030/2040/2050 EFS hourly state aggregation: Actions `41265678862`, `pypsa-usa-efs-source-evidence/outputs/efs-core-west-2030-2040-2050-hourly.csv.gz`.
- Archived 7-state original PyPSA source bus `state`, `reeds_zone`, `LAF_state` attributes from the 2030 load-only network and staged 2030/2040/2050 zone-hour CSV: Actions `41281576025`, artifact `real-western-base-network-attempt`.
- New gate: `src/energy_transition/efs_source_to_zonal_laf_hourly_gate.py`.
- CI integration: `.github/workflows/efs-actual-snapshot-semantics.yml`.

For each admitted state `s`, ReEDS zone `z`, planning year `y`, and original `LocalHourID` `h`, independently compute

```text
weight(s,z)   = SUM_original_buses_in(s,z) LAF_state(bus)
expected_MW(y,s,z,h) = EFS_source_state_MW(y,s,h) * weight(s,z)
```

Compare against each **archived** `allocated_mw(y,s,z,h)` using `rtol=1e-9`, `atol=1e-5 MW`. The checker enforces source and zone key uniqueness, all 8,760 source ordinals per state/year, matching state-year populations, valid source and bus weights, no unexpected zone rows, and rejects any mismatch, including a single corrupted hour.

**Scope:** exactly seven admitted states (AZ, CO, ID, MT, NM, UT, WY) across 2030, 2040 and 2050. No four-state Western expansion is inferred. LAF weights are the actual archived network's modeled bus attributes, **not** independently certified geographic demand shares.

## Validation status

- Previously **passed**: original staged zonal rows to Load-only NetCDF, all load-hours, [CI 42055638619](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42055638619).
- New source-state → zone-hour reconstruction: **new CI submitted; must check run result before claiming empirical pass**. [Workflow](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/workflows/efs-actual-snapshot-semantics.yml).

If passed, the overall numerical chain **state EFS hourly aggregation → modeled original-bus LAF zones → staged zonal series → Load-only archived NetCDF** is verified for seven states and three planning years. This is a reproducibility/ingestion finding, **not** a calibrated 2030–2050 Western OPF or source time synchronization proof.

## Remaining research barriers

1. Establish authoritative NLR EFS `LocalHourID` time-zone, DST, and hour-beginning/end conventions. The 2040 saved model year has leap-calendar display labels inconsistent with a nonleap source template.
2. Independently authenticate LAF weights as regional load-allocation assumptions and resolve four omitted states and incomplete ReEDS polygons.
3. Admit physically justified generator electric POIs, dynamic renewable profiles, AC branch impedances and thermal limits; resolve historical BA calibration gates.
4. Run scenario comparisons only after a validated common simultaneous chronology, reliable supply and network evidence.
