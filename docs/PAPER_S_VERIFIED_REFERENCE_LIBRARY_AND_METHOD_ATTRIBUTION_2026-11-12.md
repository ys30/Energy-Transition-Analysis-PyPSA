# Paper S — verified source/paper bibliography and solver attribution (2026-11-12)

**Scope:** Original-source literature/source register for the integrated journal manuscript. Bibliographic identities checked against authoritative publisher, DOE, EIA or official software documentation on 2026-11-12. Do not invent paper contents or use citations for evidence they do not directly establish.

## Research literature (authentic DOI and bibliographic source)

**[R1] Zerrahn, A., Schill, W.-P., & Kemfert, C. (2018).** On the economics of electrical storage for variable renewable energy sources. *European Economic Review*, **108**, 259–279. DOI: https://doi.org/10.1016/j.euroecorev.2018.07.004 . Publisher metadata: https://www.sciencedirect.com/science/article/pii/S0014292118301107 . **Use:** Storage valuation in variable renewable systems; relevance of optimizing renewable curtailment and operating choices. **Do not use:** as validation of this paper's source HDF5 semantics or annual EIA siting effects.

**[R2] Sepulveda, N. A., Jenkins, J. D., de Sisternes, F. J., & Lester, R. K. (2018).** The role of firm low-carbon electricity resources in deep decarbonization of power generation. *Joule*, **2**(11), 2403–2420. DOI: https://doi.org/10.1016/j.joule.2018.08.006 . Publisher: https://www.sciencedirect.com/science/article/pii/S2542435118303866 . **Use:** system-level literature context: full-year balancing of VRE, storage and dispatchable resources, and limitations of overinterpreting simple constrained storage experiments. **Do not use:** as empirical support for an EIA county distribution or a modelled AZ $10 threshold.

**[R3] Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020).** SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods*, **17**, 261–272. DOI: https://doi.org/10.1038/s41592-019-0686-2 . Publisher: https://www.nature.com/articles/s41592-019-0686-2 . **Use:** Python scientific optimization stack for `scipy.optimize.linprog(method="highs")`. The HiGHS LP method is an implementation setting observed in the actual frozen solver `src/energy_transition/efs_cyclic_storage_lp.py`. SciPy reference is **not** validation of the scientific model's assumptions.

**[R4] Brown, T., Hörsch, J., & Schlachtberger, D. (2018).** PyPSA: Python for Power System Analysis. *Journal of Open Research Software*, **6**(1), article 4. DOI: https://doi.org/10.5334/jors.188 . Official software citation: https://docs.pypsa.org/v1.1.1/home/citing/ . **Use:** optional background when describing PyPSA ecosystem/project context. **Mandatory attribution restriction:** the 24- and 96-LP battery experimental solver in *this* paper is a **custom SciPy HiGHS LP**, **not a PyPSA network optimization**. Never imply these LP results were run through PyPSA APIs solely because the GitHub project name includes PyPSA.

**[R5] Ho, J., Becker, J., Brown, M., et al. (2021).** Regional Energy Deployment System (ReEDS) Model Documentation: Version 2020. National Renewable Energy Laboratory, NREL/TP-6A20-78195. https://www.nrel.gov/docs/fy21osti/78195.pdf . **Use:** general ReEDS framework background **only**. **Not** a certified specification of the separately authenticated *2022 data-product* HDF5 source hour-integral, nor the source reference-year 2012 leap/calendar truncation, and not a substitute for specific publisher dataset documentation.

## Primary datasets (cite the original release, not later paper as method validation)

**[D1]** National Laboratory of the Rockies / ReEDS official publisher HDF5 and supply-curve weather products, original source files available at:
- Wind source county HDF5 and supply curve: https://zenodo.org/records/18422200
- Solar utility-PV source county HDF5 and supply curve: https://zenodo.org/records/18407660
- ReEDS2022 projected reference load publisher product: https://zenodo.org/records/18461543

The integrity MD5 checks and source county/instant semantics are part of this paper's **own** documented reproducible audit; do not claim a source DOI or original author/publication year that has not been independently verified on the source landing page. Cite the exact Zenodo version and public metadata as a dataset source after review.

**[D2]** U.S. Energy Information Administration, Form EIA-860, 2025 annual original generator data (Plant and `Operable` sheets). Official annual release and survey coverage: https://www.eia.gov/electricity/data/eia860/ . The EIA survey covers 1 MW+ combined plant nameplate facilities; therefore this paper's operational solar inventory **does not claim complete distributed/rooftop PV coverage**.

**[D3]** U.S. Census Bureau, official 2020 National County FIPS codes: https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt . Used only for state-constrained exact county-name→FIPS matching, never for hour-resource semantics.

## Reproducible study-generated evidence (not external references)

- [Verified EIA county capacity and geography audit](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185)
- [Verified original 15 native source weather-year calendar](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402)
- [Verified original 2012 24 siting-weight LP sensitivity](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663)
- [Verified original 2010–2013 96 LP interannual sensitivity](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390)
- [Verified source-only 96 LP paper graphics](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607)

## Manuscript edits and evidence boundaries

- Introduction: cite [R1, R2] for prior *general* electricity storage operating economics and whole-system balancing context.
- Methods (solver): cite [R3], refer specifically to the **actual custom LP code**. Cite [R4] only when the PyPSA framework itself is discussed; it was not the solver for the 96 experiments.
- Methods (source): cite [D1–D3] and original audit outputs. [R5] only supplies a background explanation of the ReEDS *framework*, not the specific 2022 publisher file.
- Conclusion: numerical county TV, AZ 2012 threshold crossing, cross-year weather effects rely on archived run IDs, **not** on generic peer-reviewed background papers.
- Final submission reference style needs target journal instructions and final confirmation of the archived source datasets' author/title/license/year metadata.
