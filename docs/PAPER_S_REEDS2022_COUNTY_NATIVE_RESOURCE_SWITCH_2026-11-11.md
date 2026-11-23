# ReEDS 2022 Paper S — county-native wind/PV source switching (11 Nov 2026 UTC)

## Key methodological simplification

Both original ReEDS v1 wind and PV releases provide separate **county-native** HDF5 and supply curves. For our **state-level** ReEDS 2022 demand experiment (AZ, CO, ID, WY), directly aggregate county resource-class capacities into states using the **five-digit county FIPS**. This avoids model-BA-to-state fractional allocations, a material issue when using the smaller `*_ba.h5` files. County-source aggregation does not validate the older EFS2020 p-zone geography; those analyses remain separate.

Source and MD5:
- wind CF `cf_wind-ons_reference_county.h5`, 2.9GB, `0670813d0a18b688d698ca24cf67fb92`
- wind supply `sc_wind-ons_reference_county.csv`, `49ab4e41dc386453b5fd32e5810774d4`
- PV CF `cf_upv_reference_county.h5`, 757.5MB, `aba834ea4c592023bca47de2ba79e7ec`
- PV supply `sc_upv_reference_county.csv`, `e10b1a64f3a67d163e739b735938eb78`
- shared county2zone `county2zone.csv`, `f269adef29b6d96317a845f6129b5ad9`
- wind https://zenodo.org/records/18422200; PV https://zenodo.org/records/18407660

The low-cost source-schema probe workflow is `.github/workflows/paper-s-reeds2022-county-capacity-probe.yml`. It authenticates and reports exact original CSV schemas before implementing official HDF5 resource-class matching. Any schema-to-capacity mapping remains **pending actual publisher CSV inspection**. Full HDF5 authentication and 2012 matrix extraction remain pending.

## Correct PV DC/AC accounting

Published PV CF has units **MW_AC_grid / MW_DC_array** and ILR=1.34. There are two consistent algebraic alternatives:

1. If supply capacity is DC MW, `P_AC(t)=K_DC * CF_native(t)`. No ILR multiplication of the native CF.
2. If supply capacity is AC MW, `P_AC(t)=K_AC * (1.34 * CF_native(t))`, assuming `K_DC=1.34 * K_AC` and coherent turbine/inverter definitions.

Never mix DC installed MW with ILR-scaled CF or double-count AC. **The native supply curve basis must be established** before choosing either path. Code: `src/energy_transition/reeds2022_county_state_resources.py`.

## What is and isn't certified

- ReEDS 2022 projected demand source + 2012 fixed CST hour-ending index: PASS (prior original publisher source run).
- Publication of original county wind/PV dataset, MD5 identities and FIPS class structure: independently documented.
- Official county supply CSV extraction and schema: **probe workflow now committed; runtime evidence still pending**.
- Full county HDF5 original MD5, encoding, capacity key alignment: NOT VERIFIED in this branch.
- State instantaneous aggregate CF: **implementation prepared, not executed with authenticated county data**.
- Wind/PV temporal integration with demand's hour-ending energy: BLOCKED. The publisher's weather CF is instantaneous at the hour, not proven one-hour integrated energy; no silent shift, simple row-match or cyclic wrap.
- New ReEDS 2022 wind/PV LP scenario: NOT RUN. No new dispatch numbers or article claims.

## Code acceptance sequence

1. Run CSV schema probe, inspect columns and state resource availability.
2. Bind the actual official supply-curve technology/class/county keys and confirm MW_AC or MW_DC denominator.
3. MD5-authenticate both county HDF5 files, decode every 2012 resource column and its source encoding, verify complete calendar and data, then write independent country-source-free aggregate statistics/artifacts.
4. Introduce a documented, independently justified interval-to-hour-energy policy and quantify its sensitivity; explicitly distinguish assumptions from publisher-proven facts.
5. Solve new independent 4-state × 3-demand-year storage scenarios and separate all claims/figures from historical EFS2020 ordinal synthetic work.
