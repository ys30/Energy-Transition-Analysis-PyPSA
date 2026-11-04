# Verified four-state LAF numerical candidate — NOT empirical admission

**Verified archived Western network audit:** https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/41763391214

The pinned real Western PyPSA-USA network had four EFS pilot states blocked by missing or overfull LAFs. This project now has a **read-only provenance-gated numerical candidate** for California, Nevada, Oregon and Washington that conserves each inferred original `full_state` source allocation across receiving ReEDS zones.

## Source-specific construction

1. Confirm pinned upstream `LAF_state = Pd / sum(Pd by full_state)`, with source `full_state` removed after computation.
2. Identify all **157** post-LAF added offshore auxiliary buses by *simultaneous* missing LAF, zero `Pd`, `substation_off=True`, and source-generated offshore bus ID range. Exclude these auxiliaries from the *candidate eligible load-bus inventory* rather than assigning invented zero LAFs. All original network and coefficient values remain intact.
3. Preserve all other source bus `Pd/LAF` ratios. There are precisely two **explicit inferred-denominator** source grouping exceptions: current Nevada bus `2030005` uses California denominator 67,028.96, and Washington bus `2013019` uses Oregon denominator 9,281.36. The ReEDS **destination zone remains unchanged** (p12/NEVP and p2/BPAT respectively).
4. Require every positive `Pd/LAF` ratio to match the expected pinned denominator for the inferred source state and fail closed on additional unexplained records.
5. Sum original valid LAFs by **inferred source state × existing receiving `reeds_zone`**. Require each source state's summed coefficients equal one within 1e-9.

## Measured numerical result

| Candidate source state | LAF total after explicit source grouping | Status |
| --- | ---: | --- |
| California | 0.9999999999999999 | numerical gate pass |
| Nevada | 1.0 | numerical gate pass |
| Oregon | 1.0 | numerical gate pass |
| Washington | 1.0 | numerical gate pass |

**All four source totals conserve mathematically** without LAF renormalization or imputation. The full zone-level candidate coefficients are in the GitHub Actions artifact `outputs/western_four_state_denominator_candidate.json` under `western-existing-network-laf-evidence`.

## Scientific limits

- Original `full_state` field was dropped from the archived network. Assigning two buses to CA/OR source demand is inferred from exact `Pd/LAF` denominators, **not** independently confirmed state polygon or source-bus GIS overlay.
- The numerical candidate is not an authorized empirical EFS state-to-zone crosswalk. The existing `reeds_zone` destinations and the original EFS state-hour demand convention still need external provenance and geography checks.
- Pacific- and Mountain-fixed-hour shifts must be reconciled before treating these as synchronized Western hourly demand profiles. The successful older seven-state pilot used only +7.
- **No full Western 11-state or 35-zone empirically calibrated OPF has been solved.** The existing seven-state archive results and synthetic model runs remain separate.

**Next milestone:** Apply the numerical candidate to the archived 11-state EFS Reference/Moderate hourly source **only as a clearly marked four-state source-conservation diagnostic**, leaving the rest of the network and model untouched; then independently validate geography and simultaneous temporal alignment before admission.
