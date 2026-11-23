# Paper S — submission candidate packaging and evidence gates (2026-11-13)

**Status: review manuscript reproducibly generated, NOT journal-submission certified.** This register protects the frozen original-source results and explicitly avoids converting engineering tests into claims about physical observed generation.

## Confirmed latest build after manuscript figure-number revision

- Reviewed branch source commit: `8d4b88922c9dc00be826083047c23f2439510ce8`.
- [Full CI run 43550443784](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43550443784) completed **success** for this commit, including the new manuscript/Word caption numbering regression test.
- [Word build run 43550443881](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43550443881) completed **success**, producing [artifact 14096256889](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43550443881/artifacts/14096256889), name `paper-s-2026-11-13-source-audited-integrated-review-manuscript-docx` (reported artifact ZIP 455,193 bytes, unexpired when checked). Artifact ZIP byte size is not the internal DOCX byte size.
- This build used two previously verified manuscript figure PNGs from [source figure run 43288856607](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607). Main manuscript sources and builder captions now use **Figure 1** and **Figure 2**, consistently. The build script embeds source display equations as Matplotlib image graphics, not native editable Word equation objects.
- Build and CI are for the **listed prior source commit**. This status register itself is a subsequent documentation commit, which must not be described as independently CI-passed without its own check.

## Protected scientific evidence

| Provenance and analysis | Verified source | Interpretation |
|---|---|---|
| Original source weather calendar | [43281182402](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182402) | 2007–2013, 2016–2023 present; 2014/2015 absent, 2012 unusual Feb 29/Dec 31 index |
| 2025 EIA operating generator county mapping | [43124063185](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43124063185) | Census FIPS matched for selected records, not generation profile validation |
| Original 2012 siting 24 LP | [43159121663](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43159121663) | Historical weather × 2025 county shares × fixed 2030 demand |
| Four-weather-year 96 LP | [43281182390](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43281182390) | Historical 2010–2013 controlled operating-cost scenarios |
| Two hour approximations 192 LP | [43317414772](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43317414772) | 15/16 direction agreement; **AZ 2012 $10 threshold not robust** |
| Publication plots | [43288856607](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/43288856607) | Trapezoid mode results; label numerical limitation |

**Frozen result rule:** Never replace original source HDF5, 24/96/192 LP outputs, figure input numerical CSV/JSON or claim new physical validation based merely on fresh CI.

## Manuscript content acceptance

- **PASS** — single integrated Abstract, Introduction, Methods, Results, Discussion, Conclusions, Code/Data Availability and source-backed reference sections in `docs/PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V1_2026-11-12.md`.
- **PASS** — verified numeric anchors: Arizona 2012 trapezoid potential/EIA **10.955/9.868** and endpoint hold **11.900/10.876** USD per incremental kWh-year. The binary USD 10 cost screen flips only under trapezoid.
- **PASS** — both displayed main figures use consistent Figure 1 and Figure 2 numbers in Markdown and Word builder source.
- **PASS** — Word review file produced by GitHub Actions, with reproducible script and structural acceptance tests.
- **NOT VERIFIED FOR THIS EXACT NEW ARTIFACT** — visual pagination of latest 43550443881 output after rebuild; an earlier DOCX revision was visually inspected, but visual QA should be performed on the specific artifact to be submitted.
- **OPEN** — final target-journal formatting, native-equation requirements, affiliations, author contributions, funding, conflict-of-interest and reference bibliographic style.
- **OPEN SCIENCE** — independent physically hour-integrated renewable generation matching hour-ending demand; alternative method checks alone do not resolve physical source interval semantics.
- **OPEN SCIENCE** — observed generator turbine/solar class/vintage, installed 2030 fleet, actual market cost/financing and transmission/adequacy fidelity.

## Submission-ready package acceptance, still to do

1. Download the exact successful DOCX artifact and record a **SHA-256 of the internal DOCX**, not the GitHub ZIP, plus file name and Git commit/Action IDs. Never invent a checksum.
2. Visually render the exact internally extracted DOCX and examine all pages, equations, figures, captions, table borders, heading hierarchy, URLs, reference completeness and final blank pages.
3. Align journal style with a selected target journal and ensure its policies allow equations embedded as images; replace with native equations when required.
4. Create author-approved declarations and permissions, verify each source dataset's license individually, and separate code licenses from data/figure licenses.
5. Pin a tagged source commit and durable DOI-linked research archive (where allowed), including original provenance hashes, immutable CSV/JSON results and this decision register. Do not label a GitHub Actions artifact as permanent preservation.
6. Final decision: either obtain independent physically integrated hourly source validation, **or explicitly position the manuscript as a conditional point-to-hour numerical and county-weighting sensitivity study**. Neither option warrants claims of observed/future 2030 operational profits.

**Decision:** preserve Draft PR #2; stop broad new LP sweeps; complete evidence-preserving editorial release and scientific-scope review before submission.
