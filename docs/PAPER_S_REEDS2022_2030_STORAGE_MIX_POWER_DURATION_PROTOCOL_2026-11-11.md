# Paper S — 2030 storage power-duration-resource mix sensitivity protocol (2026-11-11)

## Frozen experiment and why

After the independently certified 144-case county wind/PV buildout-ratio results ([run #42966023512](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42966023512)), a new **2030-only, 180-LP** protocol adds storage-design and resource-mix dimensions without confounding them with cross-year demand.

Four original-source state demand profiles (AZ/CO/ID/WY, 2012 fixed CST reference meteorology, projected 2030 demand); three *hypothetical* resource nameplate deployment ratios to 2030 peak demand (0.9/1.5/2.0); three wind share values (0.25/0.5/0.75; complement is PV); one no-storage reference and four battery design alternatives (0.10 or 0.25 times peak MW charge/discharge power, 4h or 8h energy duration). Total **4 × 3 × 3 × (1+2×2) = 180 LPs**, of which 144 have storage and are each matched against one of 36 no-storage references.

A separate 2030 baseline anchor must reproduce the source-backed 0.9x wind 50% / 4h battery / power 25% original LP saving of **$25,125,374.79** to within $0.10. All LPs must report optimum, verify hourly primal conservation and terminal SOC 0, and be associated with the original source dataset MD5.

## State LP and calendar restrictions

- Original resource CF is **instantaneous, not hourly integrated MWh**. Primary time conversion here uses prespecified trapezoidal neighboring-hour interpolation with an endpoint first-hour fallback, not a publisher-certified electricity measurement. The earlier 144-case experiment independently audits end-instant versus trapezoid, max observed percentage-savings sensitivity 0.3614 percentage points.
- Original ReEDS2022 county supply potential is NOT installed capacity. The deployment ratio is a clearly labeled hypothetical scenario.
- Wind MW denotes source wind capacity basis; PV is source `MW_DC` with CF defined as grid AC output per DC array capacity. **The 25/50/75% wind shares here are shares of combined heterogeneous source-nameplate denominators (wind AC and PV DC), not a verified common AC capacity share**. This is an important interpretation limitation and a priority for an AC-normalized sensitivity experiment.
- Simple isolated-state copperplate LP without transmission, commitment, hourly capacity adequacy or projected actual fleet buildout.

## Bounded cost screening (NOT realized net benefits)

The original LP minimizes only $5/MWh hypothetical renewable delivery + $90/MWh firm generation (and storage charging efficiency losses), no installed battery fixed cost.

Let `S = C_no_battery - C_battery` be annual source-reference variable operating objective savings in USD; `P` be battery power in kW and `E` storage energy in kWh. The case's **upper bound on combined annualized battery fixed costs** is `S`, if no other costs/revenues are considered. Conditional break-even annualized investment-cost frontiers:

`A_P + duration × A_E ≤ S / P`

where `A_P` is $/kW-year and `A_E` is $/kWh-year. The analysis exports power-only and energy-only break-even upper bounds, and conditional allowed `A_P` for assumed annualized energy costs `A_E=0, 10, 25 $/kWh-year`. A negative allowed power annuity indicates the assumed energy annuity already exceeds modeled avoided variable cost. This is an accounting hurdle, **not** a financing rate, IRR, NPV, or investability result; it excludes degradation, maintenance, project life, replacement and revenue stacking.

## Publication admission gates

- Confirm numerical workflow success, exact source lineage, archived 180 raw LP rows and 144 paired hurdle rows.
- Compare full spatial ordering and source denominator caveat, not just absolute savings.
- Avoid interpreting annual source-reference $ savings as real calendar-year system savings.
- Future controlled follow-up should vary PV AC/DC basis and installed-fleet representativeness, energy prices and hour-integration rules. Prior EFS2020 p-zone Paper S remains separately frozen.
