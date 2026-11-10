# Paper S E2 — independently audited window/outside energy conservation (10 Nov 2026)

**Status: E2 scientific gate completed.** Independent re-analysis of six accepted 8,760-hour LP solution traces (**52,560 source-hour rows**) from [accepted original archive #42851448558](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558). No new LP optimization was performed and no original EFS data bytes are released by this note.

## Predefined comparison

2030 Arizona p28 and Wyoming p24, synthetic Wave A, battery power 25% of zone peak load, energy 1 peak MW-hour, original 90% round-trip efficiency and `LocalHourID` window **4001–4168**. For each zone compare minimum-window and maximum-window discharge schedules independently with the original objective-optimal schedule. The original cost bound is `C(x) <= C* + max(USD 0.05,10^-9 C*)`. Independent original-source hourly records identify source-hour chronology *ordinally*, not in certified physical UTC.

## Accepted source-hour differences relative to primary baseline

| Zone | Schedule | Δ selected-window discharge MWh | Δ outside-window discharge MWh | Δ whole-year discharge MWh | Δ original variable objective USD |
|---|---|---:|---:|---:|---:|
| AZ p28 | minimum | −20,118.973864 | +20,118.952504 | −0.021361 | +1.803780 |
| AZ p28 | maximum | +9,233.362274 | −9,230.115475 | +3.246799 | +1.803777 |
| WY p24 | minimum | −260.529565 | +260.524798 | −0.004767 | +0.402588 |
| WY p24 | maximum | +1,356.223658 | −1,356.183399 | +0.040259 | +0.402589 |

Each difference is computed **hourly** before aggregation; as verified, `Δ D_window + Δ D_outside = Δ D_year`, not asserted as zero. These discrepancies are tiny compared with the selected-window redistribution, but some are *nonzero*. In particular, the additional 3.246799 MWh of annual discharge in AZ maximum-window candidate matches the small archived same-hour charge/discharge overlap, which is independently addressed by the existing mutually exclusive feasible witness.

## Conservation and cost gates

At each of the 8760 original source ordinals, compare two schedules at fixed renewable availability `A_t` and load `L_t`. With six LP variables (renewable to load r, renewable charging c, discharge to load d, firm f, unused renewable u, end-hour SOC s):

```text
Δr = −Δc −Δu          (fixed A_t)
Δr = −Δd −Δf          (fixed L_t)
Δs_t − Δs_(t-1) = sqrt(0.9) Δc_t − Δd_t/sqrt(0.9)
ΔC = 5*(ΣΔr + ΣΔc) + 90 ΣΔf = −5 ΣΔu + 90 ΣΔf
```

The independent differenced-record audit obtained maximum renewable/load-consistency discrepancy **3.411e−12 MWh** and maximum SOC difference-recursion discrepancy **5.457e−12 MWh**; four cost differences all fit within the original source `~USD 1.803783` (AZ) or `~USD 0.402599` (WY) nonzero allowances, without adding any not-reported additional objective penalty. Both source ZIP hashes, complete 6-schedule annual and window sums, and four pairwise difference summaries were recorded in a private reproducibility bundle.

**Correct scientific wording:** Window-level energy reallocation is overwhelmingly offset by outside-window changes, while annual discharge stays **nearly** stable (not exactly invariant). The large source-window interval is under a small **positive** original variable-cost tolerance, not an exact-optimal-face proof and not physical Western grid reliability. The independent E2 audit does not demonstrate complete feasibility of a new real-grid formulation: archived original LPs already passed their own source constraints, and the new comparison audits their hourly **differences**.

## Manuscript integration and stop condition

E2 source-to-claim results were added directly to existing private manuscript **Results 3.5** and **Discussion 4.3**, yielding private v13 **without another figure or appendix**. Existing five main and three supplementary figures were retained unchanged. **E2 is closed** absent a verified numeric inconsistency. Next finite steps are E1 (mechanism from already archived traces) and E3 (two new distinct source-shape groups), followed by experimental freeze; do not keep adding unscheduled windows or plotting variants.

Original source archive: [#42851448558](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42851448558).
