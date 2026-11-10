# Paper S v9 — source-citation correction and journal-fit admission gate (10 Nov 2026)

**Public-safe editorial record.** A new private Word draft, v9, was directly revised from the mounted v8 working manuscript and visually rendered as 25 pages. It preserves all **5 main + 2 supplementary** embedded figure assets. No private full text or images are committed here, and no new source-backed LP was executed.

## Verified bibliographic correction and consistency issues

- Original private v8 Ref. [6] abbreviated the author list of *Battery degradation: Impact on economic dispatch* (2024) to Schade alone. The publisher DOI [10.1002/est2.588](https://doi.org/10.1002/est2.588) lists **Curd Schade AND Ruud Egging-Bratseth**. The private v9 reference was corrected.
- The 2024 original [Journal of Energy Storage DOI 10.1016/j.est.2024.112941](https://doi.org/10.1016/j.est.2024.112941) confirms the prior art on degradation-aware dispatch and charging/discharging exclusivity. This literature does not certify our source-ordinal LP's empirical dispatch realism.
- The v8 Appendix D contained a stale note claiming that image artworks still retained old working-stage figure numbers. That conflicted with v8's actual artwork-cleaning steps. The private v9 corrects the editorial audit to report that the old in-image figure headlines were removed in v8, while high-resolution **vector** source regeneration and journal-specific art specifications remain open.
- Dataset DOI [10.7799/1593122](https://doi.org/10.7799/1593122) has been assigned a separate **working dataset reference** in the private bibliography. Its complete publisher-recommended author list must still be confirmed; this new entry is marked as provisional rather than presenting an inferred list as fact.
- The current body uses predominantly **author-year** scholarly citations while the reference list is numbered. This is a **style-unification gate**, not an internally acceptable final journal reference style. Final numeric/author-year rendering must follow the selected journal and be checked against every reference.

## Editorial journal-fit comparison (scope only; no ranking or acceptance claim)

| Outlet | Confirmed journal scope | Main risk for the present paper |
|---|---|---|
| **Energy Systems** (Springer Nature) | Mathematical programming, optimization, power-system planning and modeling | Most plausible **methods-oriented outlet** given an explicitly simplified original-source LP, if true incremental novelty over MGA can be demonstrated |
| **Journal of Energy Storage** (Elsevier) | Battery storage engineering, modeling, sizing and optimization; publisher emphasizes substantial storage-specific contribution | Model lacks physically calibrated storage degradation; original synthetic-resource screen could be deemed insufficient; *an optimization technique alone is not novel* |
| **Energy** (Elsevier) | Multidisciplinary energy planning and modeling including storage | Limited generalizability of two-zone near-optimal case study and toy supply source |
| **Applied Energy** (Elsevier) | Applied energy system operations and optimization with meaningful practical systems relevance | Higher risk without observed renewable time series or actual synchronizable EFS UTC and network-constrained validation |

Publisher descriptions checked 10 Nov 2026:
- https://shop.elsevier.com/journals/journal-of-energy-storage/2352-152X
- https://shop.elsevier.com/journals/energy/0360-5442
- https://shop.elsevier.com/journals/applied-energy/0306-2619
- https://link.springer.com/journal/12667 (journal home, publisher)
No impact-factor ranking, acceptance prediction, journal paper-length, author instructions or open-access cost is claimed as verified.

## Core paper scientific admission remains unchanged

- The operation is *SciPy / HiGHS directly formulated LP*; not a PyPSA Network OPF.
- Five main / two supplementary images remain physically embedded in the private document.
- Annual versus 168-source-hour near-optimal discharge percentages have different denominators.
- The source EFS 2020 LocalHourID remains **ordinal-only** pending physical clock evidence. The ReEDS2022 CST metadata does not authenticate EFS 2020.
- The cost tolerance is strictly positive (plus solver feasibility limits), so exact multiple-optimum claims remain inadmissible.
- The 0/1/10 USD per MWh discharge penalty is an illustrative **linear cycling proxy**, not measured battery degradation.
- Data rights from original EFS are conditional on its publisher's notice, while code ownership, mixed ReEDS source rights, coauthor rights and permanent archived release remain separate.
- As yet the full literature review is **not systematic**. The novelty claim is narrower than established MGA and investment-alternative analysis.

## Private v9 completed/remaining

Private v9 now includes a new Appendix E with a four-journal scope-fit table, quantitative provenance risk checks and priority pre-submission actions. All 25 rendered page previews were reviewed as a contact sheet. A separate private machine-readable audit log is available to the author.

**Remaining gates:** confirm EFS original author list and its physical hour semantics; unify literature citation style; identify actual incremental novelty beyond prior art; regenerate final source SVG artwork to the target journal's specifications; formal code/data statements, funding/declarations and coauthor signoff.
