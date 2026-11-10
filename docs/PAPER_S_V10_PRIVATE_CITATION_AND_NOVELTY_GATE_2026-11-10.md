# Paper S v10 — private citation-system and novelty-differentiation quality gate (10 November 2026)

**Scope:** A private Word manuscript was revised from v9 to v10 and rendered to 25 pages. Its full text and seven embedded illustrations have not been uploaded to this public repository. The previous public repository CI [#42916280351](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42916280351) is successful; this editorial note introduces no new LP experiment.

## Concrete corrections admitted

1. **One consistent working citation system.** Removed numeric bibliography prefixes [1]–[9] and an anomalous combined `(Brown et al., 2018) [5]` citation. Narrative now follows author–year style pending target-journal-specific punctuation.
2. **EFS source has a definitive full citation, not placeholder authorship.** The official [EFS Load Profiles catalog](https://data.nlr.gov/submissions/126) provides a 12-author publisher citation: Trieu Mai, Paige Jadun, Jeffrey Logan, Colin McMillan, Matteo Muratori, Daniel Steinberg, Laura Vimmerstedt, Ryan Jones, Ben Haley, Brent Nelson, Caitlin Murphy, and Yinong Sun (2020), *Electrification Futures Study Load Profiles*, DOI [10.7799/1593122](https://doi.org/10.7799/1593122). This replaces the private draft's incomplete `Mai, T., et al.` source entry.
3. **Corrected cited author references** for Schade **and** Egging-Bratseth (2024) (DOI [10.1002/est2.588](https://doi.org/10.1002/est2.588)); the cited 2024 Vaičys et al. dispatch paper and its six authors (DOI [10.1016/j.est.2024.112941](https://doi.org/10.1016/j.est.2024.112941)) are independently verifiable from research-institution metadata.
4. **Clear literature overlap and bounded contribution.** DeCarolis (2011) and DeCarolis et al. (2016) already established MGA in energy model optimization. Neumann and Brown (2021) and Pedersen et al. (2021) already studied near-optimal energy system alternative spaces. Schade and Egging-Bratseth (2024) examine cycle-depth and SOC-aware battery degradation, which cannot be equated with the present manuscript's simple illustrative linear discharge-throughput charge. The candidate incremental contribution remains the auditable annual-versus-specified-window energy-delivery contrast under a stated small nonzero original-cost allowance, together with a source-shape independence audit.
5. **Private Appendix F** records exact citation/source gates and novelty differentiation; existing working main Figures 1–5 and Supplements S1–S2 were retained unchanged. No numerical LP claims were altered.

## Remaining editorial blockers

- The current literature sample is a **targeted prior-art check**, not a reproducible systematic search of temporal dispatch ambiguity, battery dispatch identifiability and temporal near-optimal service metrics.
- The EFS physical source-hour clock remains unverified. The source 2020 catalog does not establish original `LocalHourID` UTC, hour-ending or DST semantics.
- The final target journal's complete author instructions, bibliography style, code/data rights, and coauthor authorizations remain outstanding.
- The existing direct SciPy/HiGHS original-source ordinal LP should not be called a PyPSA Network optimization, actual Western Interconnection OPF, observed renewable dispatch, or an experimentally calibrated degradation model.
- Cost-sublevel-set window intervals with positive tolerance do not establish exactly equal-cost alternative optimum faces, empirical service reliability or independent sampled load chronologies.

This record documents editing/review activity, not acceptance, physical validation, permission receipt or paper submission.
