# Paper S — five-main-figure editorial freeze and private manuscript integration (10 November 2026)

## Decision and scope

The existing six original-source-verified *journal-figure candidates* are now reorganized into a **recommended five-main-figure draft**, with the former projected-year normalized firm/demand chart moved to **Supplementary Figure S1**. This is a narrative and manuscript editing decision, **not a new LP experiment, publication acceptance or coauthor-approved final manuscript**.

A separately delivered **private, 11-page English working document** integrates a working abstract, definitions capsule, Results subsections, Discussion, Conclusions, all five existing candidate image assets, the Supplementary Figure S1 image and an evidence/provenance checklist. Its full text remains **outside** the public repository.

## New private manuscript figure-to-claim map

| Private draft designation | Previously validated candidate | Original-source acceptance | Exact claim and limitation |
|---|---|---|---|
| Main Figure 1 | Original proposed main Fig. 1 — EFS/provenance/factor workflow | [Figure workflow #42856072109](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42856072109) | Observed-source demand versus independent synthetic assumptions; seven unique nonzero normalized shapes within each projection year; not physical UTC |
| Main Figure 2 | Original proposed main Fig. 2 — 2030 unused fraction | [Figure workflow #42877258094](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42877258094) | Conditional modeled unused hypothetical renewable availability; not measured renewable curtailment |
| Main Figure 3 | Original proposed main Fig. 4 — marginal 0→4h/4→8h toy cost | [Marginal original #42455745341](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42455745341) and [figure audit #42877258094](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42877258094) | Nine condition-dependent modeled variable-objective differences; not net storage economic value |
| Main Figure 4 | Original proposed main Fig. 5 — independent MW/MWh | [Source-archive original 189 LP #42674534963](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42674534963), [84-interaction source #42675999423](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42675999423), [plot audit #42857238238](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42857238238) | Conditional power/energy interaction and saturation, descriptive group counts rather than statistical replicates |
| Main Figure 5 | Original proposed main Fig. 6 — annual/window identification | [Annual discharge extrema #42747095388](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42747095388), [window extrema #42780417107](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42780417107), [plot audit #42854783701](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42854783701) | Annual LP discharge robust but 168-source-hour allocation nonunique under narrow nonzero original-cost allowance; not exact optimal-face proof |
| **Supplementary Figure S1** | Original proposed main Fig. 3 — planning-year normalization | [Figure workflow #42877258094](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42877258094) | Near-overlap of normalized firm-energy response despite projection-year load-scale increase; negative result, no independent weather-year replication |

**Five figure slots have source-verified rendered inputs**, but a full journal-ready formatting/target-journal re-numbering check, in-image figure titles, complete bibliographic citations and copyright/source-rights audit are still pending. The private document embeds the original verified figure bitmap assets; it does not imply that these original PNG internals have already been re-rendered with the new five-figure numbering.

## Working manuscript integration completed privately

- Working abstract and numerical-scope paragraph;
- Methods capsule specifying original objective, synthetic supply and cost-capped near-optimal feasible set;
- Results 3.1–3.5 corresponding to main Figures 1–5;
- Discussion 4.1–4.5 (marginal duration, P/E design, model primal nonidentification, pseudoreplication, reporting);
- Working Conclusions, Supplementary Figure S1 and source-provenance table;
- No claim of real Western grid dispatch, empirically calibrated renewable availability, storage CAPEX / NPV, exact multiple optimal bases or reliability-event inference.

## Key reviewer-gate red flags

1. **Novelty:** must compare explicitly with near-optimal LP feasible-space and storage-dispatch nonuniqueness literature. Merely generating deterministic synthetic waveforms is not an independent methodology breakthrough.
2. **Data:** source LocalHourID still lacks certified UTC; 2040 ordinal-hour/clock interpretation must not be assumed.
3. **Sampling:** the original 20 zones yield only seven unique nonzero peak-normalized chronology classes within a year; do not treat shapes or years as independent samples.
4. **Economics:** $5/$90 per MWh coefficients describe the hypothetical LP objective and exclude storage CAPEX/degradation.
5. **Optimization:** min/max interval results are from different LP schedules in a **nonzero** cost-tolerance sublevel set, not an exact-optimal-face proof. Annual and window percentages have distinct denominators.
6. **Private document completion:** cited Introduction, detailed mathematical Methods, reference validation, data permissions, reproducibility statement, target-journal formatting and coauthor review remain mandatory.
7. **Figure 3 negative result:** 2030–2050 normalized differences are only ~0.00386 / 0.00581 / 0.00937 percentage points at 0/4/8h. Retain as Supplement S1, not independent main-year evidence.

## Status check

The latest full repository CI for the preceding six-figure matrix commit [#42877767428](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42877767428) **succeeded**. Adding this public editorial note will trigger another standard CI and should not be conflated with validating unpublished private manuscript text.

**Next substantive work:** Verify externally sourced scholarly literature and address novelty/limitations, fill complete mathematical Methods and source-data rights, then conduct a full private manuscript red-team review. Avoid adding further largely duplicative LP figure series without a new identified reviewer objection.
