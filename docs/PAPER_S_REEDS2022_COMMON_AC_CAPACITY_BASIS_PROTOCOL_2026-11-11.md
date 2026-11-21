# Paper S — common AC-nameplate model units: controlled correction protocol (2026-11-11)

## Original publisher evidence, not an independent real-world fleet measurement

Frozen ReEDS utility PV original v1 publisher record: https://zenodo.org/records/18407660. The publisher states capacity factor values are **MW_AC,grid / MW_DC,array**, and a common AC-nameplate denominator can be formed by multiplying by the explicitly documented **ILR=1.34 MW_DC,array/MW_AC,nameplate**. The publisher also specifies hourly source observations are **instantaneous on the hour**, fixed CST UTC−06:00, with 2012 containing exactly 8760 entries and the last calendar day omitted. ReEDS published resource supply curve available capacity is **MW_DC for utility PV**, not the installed or projected fleet.

We verified the original PV 2012 county state weighted source profile against MD5 and clock in Actions [42962740548](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42962740548). The original profile has a maximum rounded source CF of ~0.7463, which yields ~1.000042 after ×1.34. Small values above 1 stemming solely from this publisher decimal rounding are capped to 1 by the revised model, with strict max tolerance 0.0001 and tests. Values exceeding tolerance fail.

## Corrected model expression

For the new **AC-nameplate** experiment, let r be hypothetical (total wind+PV) AC-nameplate MW / state peak-load MW; f is wind fraction of this combined AC nameplate. Set P_W,AC = r * peak * f; P_PV,AC = r * peak * (1−f), P_PV,DC = 1.34 P_PV,AC. The original publisher PV instantaneous CF is CF_PV,source = P_PV,gridAC / P_PV,DC, so the AC-nameplate equivalent is CF_PV,AC = 1.34 CF_PV,source (bounded to 1 within rounding tolerance). In the source-backed zonal LP, normalized available renewable MW is

`r * peak * [f * CF_W,AC + (1−f) * CF_PV,AC]`.

**Do not multiply by ILR twice.** The old mixed-denominator case used `r * peak * [f * CF_W + (1−f) * CF_PV,source]`, with the nominal 50/50 weight applied to heterogeneous AC and DC nominal MW. It was useful as a bounded illustrative sensitivity but **not a common AC MW mix**. The revised model changes the meaning of nameplate ratio/f only; both are still **hypothetical**, and cannot be treated as actual installed state generation.

## Tests and experimental design

Re-run **all 180 cases** exactly matched to the successful original [43051615043](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43051615043): AZ/CO/ID/WY, 2030 source demand and 2012 source weather, r=0.9, 1.5, 2.0, f=0.25, 0.50, 0.75, and no battery plus 4h/8h batteries with power 0.10/0.25× peak. 90% roundtrip battery efficiency, source instantaneous-to-hour numerical trapezoid with first-hour endpoint fallback, source capacity-by-county weights and the same illustrative $5/$90 per MWh generation costs.

Require all 180 to be optimal with primal residual ≤1e−5, **144** storage-vs-no-storage matched operating-cost savings and investment annuity hurdles, and **180** legacy-vs-common-AC source-denominator matched scenario comparisons. Preserve previous CSV, never overwrite the frozen old results; publish corrected numerical values in a separate artifact.

## Non-admission caveats

- Both the old and revised weather supply curves represent 2012 original county developable-resource weighting, not actual or forecast 2030 plant build-out.
- Source hourly PV CF is an exact-hour instantaneous observation, while ReEDS hourly demand is an end-hour load; trapezoidal hour-energy approximation is not publisher-certified.
- The LP is a one-zone-per-state copperplate with no AC network power flow, inter-state transfers, reliability adequacy, transmission, operating reserves or generator unit commitment.
- Battery cost comparisons remain variable operating-value only; installed capital and financing costs are not in the optimization.
- The 1.34 PV inverter loading ratio is a frozen ReEDS **technology assumption**, not a measured ILR for the user's actual or future assets.
- Original EFS2020 Paper S and independent ReEDS pure-state BA subset remain frozen; no claim of full paper reproducibility or publication approval pending independent cross-validation and complete repo CI.
