# Paper S — E3 final two distinct shape groups and experiment freeze (10 November 2026)

**Status: accepted E3 source-certified final additional experiment.** The scientific experimental matrix defined in the three-item E1/E2/E3 closeout plan is **now frozen**. No further source shapes, source windows, synthetic supply patterns, degradation penalties, or additional main/supplementary graphics should be appended merely for completeness. Reopen only for a demonstrated scientific defect or a substantive journal/coauthor requirement.

## Source selection before outcomes

Original 2030 EFS archived 20-zone input: 19 positive source-load zones representing seven distinct peak-normalized source-hour shapes. Prior window-robustness analysis used one Arizona representative (group 1, p28) and one Wyoming representative (group 7, p24). E3 independently and **before viewing new discharge results** fixed source groups 2 (Colorado p33) and 3 (Idaho p15), which are distinct groups from each other and the original two. Not independent identically distributed regional sampling. The original EFS `LocalHourID` physical UTC and daylight-saving clock remain unverified.

The same **five predeclared disjoint 168-source-ordinal-hour windows** were retained: 1–168; 2001–2168; 4001–4168; 6001–6168; 8001–8168. No selection after outcome inspection.

Original source LP model: SciPy/HiGHS; 2030 original EFS source load; Wave A synthetic renewable availability; battery rated power 25% of zone peak load; energy capacity equal to one peak-MW-hour; round-trip battery efficiency 90%; original hypothetical dispatch variable objective; strictly positive source-original near-optimal cost sublevel tolerance `max(USD 0.05, 10^-9 C*)`. All primary objective costs independently reconciled to original archived year/case records and source-hour conservation and cyclic SOC checks passed.

## Verified source-CI outcomes

[GitHub Actions #42924241109](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42924241109): **SUCCESS**, separate original-source group jobs (2,3) and successful consolidation. Archived data: `paper-s-e3-final-two-source-shape-closed-results`, 10 window interval rows and 30 group-window schedule rows. Each group repeats one full-year primary LP baseline and solves ten additional window max/min LPs: **22 unique new full-year LPs**, not 30 independent LP optimizations.

| Source window | Colorado p33 span, MWh | Idaho p15 span, MWh |
|---|---:|---:|
| 1–168 | 2,028.144011 | 0.812716 |
| 2001–2168 | 3,956.892710 | 1,060.582588 |
| 4001–4168 | **16,513.393290** | **5,214.254992** |
| 6001–6168 | 1,130.751939 | 0.812716 |
| 8001–8168 | 12,402.274690 | 2,210.364089 |

All five Colorado spans exceed 1,000 MWh. In Idaho, two windows have extremely small positive span (0.813 MWh), which should not be characterized as practically substantial flexibility. Original 4001–4168 group-specific percent-of-baseline-window discharge: **Colorado 59.9002%**, **Idaho 48.9721%**. Both ratios are relative to the original source-optimal **window discharge denominator**, not storage capacity, probability or a confidence interval.

## Scientific conclusion

With the previously archived Arizona p28 and Wyoming p24 cases, the final contrast now covers **four original distinct source-demand temporal shapes and twenty group×preselected-window comparisons**. Strong, but nonuniform, window-discharge nonidentification exists within this precisely defined hypothetical-source LP cost sublevel set. Some preselected source windows have effectively tiny intervals. The analysis is not a random sample of source-hour weeks; cannot infer incidence frequencies across all years, seven source shapes, physical UTC simultaneity, calibrated economic battery value, or actual Western-grid reliability. Existing MGA and OPF alternative-solution literatures remain prior art. Its possible contribution is a transparent source-verified annual-vs-preselected-window operational metric diagnostic, not first principles of near-optimal alternative analysis.

**Counterexample honesty:** E3 does not produce a *strict zero mathematical* span among these cases; near-zero Idaho intervals are important quantitative counterexamples to any claim that every week has large degrees of freedom. Cost tolerance and numerical feasibility cannot support exact optimum-face nonuniqueness.

## Finite three-experiment closure

- **E2 PASS:** independent 52,560 original source-hour differential conservation/SOC and cost accounting, no reoptimization. [E2 report](PAPER_S_E2_WINDOW_OUTSIDE_CONSERVATION_CLOSED_2026-11-10.md).
- **E1 PASS (descriptive only):** archived source-state hourly load/supply/SOC diagnostic, no causal predictive claims. [E1 report](PAPER_S_E1_SOURCE_STATE_WINDOW_HETEROGENEITY_CLOSED_2026-11-10.md).
- **E3 PASS:** two prespecified additional independent demand-shape groups, five fixed original windows, independent 22 LP original-source CI reproducibility.

## Paper and publishing boundary

Private **Paper S v15** retains **5 main + 3 supplementary figures** and integrates E3 in the existing Results 3.8, Discussion 4.8 and Conclusions, without new figures or appendices. This private manuscript is **not committed**. It is a working draft, not an accepted final journal submission.

The next work package is strictly **non-experimental manuscript finalization**: figure cross-references, harmonization of full references, critical literature comparison (Viens et al. 2026), confirmed EFS source-hour semantics or carefully bounded failure-to-certify statement, source/code/data rights and coauthor authorization, selection of journal author instructions, and manuscript-native editorial trimming. Inability to establish source clock may require keeping this research as source-ordinal toy diagnostic; it must not be masked by more LP runs.
