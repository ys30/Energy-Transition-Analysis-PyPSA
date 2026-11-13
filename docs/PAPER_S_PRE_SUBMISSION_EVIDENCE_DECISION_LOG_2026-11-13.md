# Paper S — pre-submission scientific and editorial decision log (2026-11-13)

## Editorial status — substantive synthesis complete, not yet submission-certified

**Current integrated manuscript:** [English V1, including amended 207-word abstract, full verified source/DOI references, source-audited 96- and 192-LP evidence and figure captions](./PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V1_2026-11-12.md). **Current editorial architecture:** [updated single-narrative plan](./PAPER_S_INTEGRATED_SUBMISSION_ARCHITECTURE_EVIDENCE_AUDIT_2026-11-12.md). The repository's raw previous Results/Discussion 36k-character addendum remains historical supporting material, not the final article.

### Admission matrix

| Gate | Evidence / exact status | Publication action |
|---|---|---|
| ReEDS original wind/PV source file integrity | Original official county/class HDF5 and supply-curve digests authenticated in prior workflows | **PASS**; cite pinned dataset versions/DOIs |
| Wind/PV source clock and 2012 reference | 15 original 8760-hour years (2007–2013, 2016–2023) cross-technology native clocks agree; leap references include Feb29/omit Dec31 | **PASS for source index**; disclose 2012 atypical reference |
| EIA 2025 county assignment | EIA-860 operating generator mapping to Census FIPS verified, including geographic weighting of eight state×technology cells | **PASS for the included operating records**; not future installation/site resource classes |
| 2012 24-LP source siting | Source-authenticated 24 LP scenario validation | **PASS**; AZ 2012 $10 screen is conditional, not robust |
| 2010–2013 four-year 96-LP historical panel | Source-backed 96 LP optimal and 2012 baseline objective reproduced within $0.005 | **PASS for modeled source scenario** |
| Endpoint hold vs trapezoid 192-LP paired check | 192 LP optimal and frozen 96 original trapezoid objectives reproduced; signed siting response 15/16 pairs agree, AZ 2013 tiny sign reversal | **PASS for numerical sensitivity**, not physical hourly integration |
| AZ 2012 $10 screen | ReEDS/EIA trapezoid $10.955/$9.868 flips; endpoint hold $11.900/$10.876 both above 10 | **FAIL as robust headline claim** — describe only as numerical example, not real economic boundary |
| Provenance: numerical point CF vs actual hour-ending energy | Publisher wind/PV CF are instantaneous, load is hour-ending; neither model approximation independently validated against true hourly generation | **OPEN** — restrict scientific scope; no realized savings forecast |
| Publisher within-county resource class | 2025 operating sites have observed county capacity but their precise original ReEDS renewable resource class/vintage not identified | **OPEN** — scenario geography, not observed fleet power reconstruction |
| Grid network / adequacy / financing | Custom SciPy HiGHS copperplate LP with firm 1.2× peak, zero SOC endpoints, no battery CAPEX/NPV and no nodal/line constraints | **Scope limitation**; not PyPSA network simulation |
| Final article layout | Main figure panels verified via 43288856607; integrated article text and captions exist, but final DOCX/PDF layout, journal-specific references/metadata not built | **OPEN** |
| Full repository CI for prior reviewed 192-LP manuscript | Workflow 43323774425 succeeded | **PASS for that prior commit** |
| Full CI for 2026-11-13 editorial refresh | Recheck GitHub Actions at current branch HEAD | **PENDING until actually completed** |

### Recommended final manuscript logic

- **Lead claim:** county renewable resource-potential versus 2025 observed operating generator share can change modeled 4→8-hour marginal storage *avoided variable cost* under controlled common-AC capacity, in a state- and historical-weather-dependent manner.
- **Second claim:** continuous county-siting effect sign agrees across two prespecified source-hour numerical conventions in 15/16 of the 16 year×state cases. The one disagreement (AZ 2013: −0.080980 versus +0.021245 $/added kWh-year) is close to zero.
- **Counterexample to avoid overclaim:** illustrative Arizona 2012 $10/kWh-year incremental energy-cost threshold *only* reverses in trapezoid treatment, not endpoint hold. Keep the crossing as an example of scientific sensitivity, not strong investment evidence.
- **No future climate inference:** 2010–2013 represent historic weather-source references using fixed 2030 demand, *not* SSP/RCP future changes. Nonleap source Feb29 is imputed; original Dec31 omitted.
- **No source-hour physical guarantee:** Wind/PV input points are fixed-CST instantaneous samples; the LP hour approximations are not manufacturer/generator production measurements.
- **No misattributed optimizer:** The relevant 192 LPs are a custom `scipy.optimize.linprog(method="highs")` formulation, with zero initial and terminal state of charge; the presence of PyPSA in repo title does not mean these results used a PyPSA network API.

### Figure and table disposition for a concise journal article

1. Figure 1 methodology and source provenance flow diagram (author-created; not yet generated).
2. Figure 2 county potential vs operating capacity distribution (use authenticated geography audit; may move to Supplement).
3. **Figure 3/4a** original verified state–year panel [PNG/PDF in artifact 13976367223](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607/artifacts/13976367223) with caption explicitly stating **trapezoid only**.
4. **Figure 3/4b** original verified continuous EIA-minus-source county value heatmap (same figure artifact), with 15/16 source-hour direction agreement explicitly noted. Prefer continuous values, not a binary $10 heatmap.
5. Table 1 source identity and modeled operating assumptions, Table 2 EIA county vs developer potential source share QA, Table 3 4×4 historical year×state matched values (trapezoid).
6. Supplemental Table S1 original endpoint-hold versus trapezoid 16 signed geography effects [source artifact 13989123990](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772/artifacts/13989123990). Place AZ 2012 four-mode values in main Results §3.5.

### Remaining recommended path, in order

1. Complete latest CI on the consolidated manuscript. Resolve only factual/test failures; do not alter frozen LP CSVs.
2. Audit metadata and bibliographic style for target journal and archive one precise Git release/Zenodo source snapshot so runs are recoverable beyond ephemeral Actions retention.
3. Create final polished Figure 1 provenance schematic and determine whether Fig 2 belongs in Supplement.
4. Create journal-appropriate complete manuscript DOCX/PDF with numbered equations, bibliography, scientific figure captions, editable tables and source/hypothesis labels; perform visual review.
5. Either independently validate physically integrated source-hour wind/PV generation or maintain the explicit conditional point-sampling approximation limitation and choose a journal whose remit permits model-method sensitivity studies.
6. Resolve author contribution, data/software licenses, conflicts and funding disclosure. Do not make prior EFS2020 synthetic profiles primary results.

**Recommendation:** Stop broad sweeps unless a precise scientific or reviewer request arises. The paper's central result is a **model sensitivity and data-provenance contribution**, not demonstrated 2030 storage investment profitability.
