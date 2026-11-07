# Paper T: journal-fit decision, licensing/release gaps, and v8 manuscript structure

**Research track:** Annual Agreement, Hourly Disagreement — original EFS2020/ReEDS2022 source-hour provenance with a source-index identifiability audit. **Status:** verified numerical evidence, private collaborator-review manuscript; **no submission or registered DOI**.

## 2026-11-07 repository admission audit

The [latest verified main CI #42335978690](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42335978690) passed. The original 16-file source-artifact SHA256 lock was successfully verified in [#42335868902](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42335868902).

The GitHub repository API reports:
- repository is **public**;
- **no detected LICENSE** file and the GitHub API `license` property is `null`;
- **no published GitHub Releases**;
- repository first created **2026-10-29**, so it lacks a six-month public development track record.

These are observed conditions, **not permission** to arbitrarily attach a code or source-data license. Select a software license only after verifying ownership; the original EFS/ReEDS datasets and derived table redistribution have separately applicable source terms.

## Publication choices (conditional ranking, not journal acceptance predictions)

**1. Energy Informatics — preferred first journal to evaluate for current Paper T.**
- Paper T is about energy-model data semantics, interoperability, validation, temporal provenance, and fail-closed temporal joins. These map directly to information representation and governance for energy planning, as highlighted by the journal's 2026 field-defining editorial `10.1186/s42162-026-00677-y`.
- Keep the current evidence-based **original research** Results/Discussion structure, with clearly delimited methods contribution and limitations.
- Before submitting: compare against at least one wider energy-data interoperability method, write clear generalized admission criteria, confirm publisher fees and author instructions at actual submission time, and seek coauthor review.
- Official journal example/context: https://doi.org/10.1186/s42162-026-00677-y.

**2. Environmental Modelling & Software — conditional, higher generalization hurdle.**
- Its official scope emphasizes broadly useful environmental model validation, reproducibility, integration, and quantitative verification, but the current single EFS/ReEDS related-release audit may be too narrow to establish environmental cross-system methodology.
- Choose only if Paper T articulates a transferable validation architecture and demonstrates its utility beyond one related product lineage. More text alone cannot replace that evidence.
- Official scope: https://shop.elsevier.com/journals/environmental-modelling-and-software/1364-8152.

**3. Scientific Data — ARTICLE is a possible reframe; Data Descriptor is not the current manuscript.**
- A Data Descriptor primarily documents a shared dataset, does **not** report substantive hypothesis tests/Results/Discussion, and requires appropriate repository deposition. Thus the current source-anomaly analysis cannot simply be relabeled as a Data Descriptor.
- Its **Article** category can discuss data standards, sharing, curation and re-use but would require a shifted narrative to a broader data-admission standard.
- Submission guidelines: https://www.nature.com/sdata/submission-guidelines ; editorial policy: https://www.nature.com/sdata/policies/editorial-and-publishing-policies.

**4. JOSS / open software papers — NOT presently an appropriate substitute.**
- JOSS focuses on substantial reusable research software rather than a scientific case-study Results manuscript; current screening requires demonstrable research impact and at least six months of public development. The repository is newer and its GitHub API license is not declared.
- Official eligibility: https://joss.readthedocs.io/en/latest/submitting.html.

## Source-archive release route (not yet executed)

1. Freeze source code at a designated commit and preserve `docs/paper_t_frozen_supplement_sha256.txt`; confirm all 16 checked bytes.
2. Audit software copyright ownership and choose a legitimate OSI-compatible license for **code**, independent of the original publisher datasets. Do not apply a license to upstream work without rights.
3. Audit license/redistribution rights for the **derived tables and figures**, including source attribution and metadata. If public redistribution is constrained, deposit allowable derived summaries/provenance and instructions to reproduce from original publisher links.
4. Create a clearly labeled **source-code GitHub Release** only after author approval and inspect its source archive. GitHub/Zenodo integration (if enabled by the account holder) can then archive the public release and assign a DOI: https://help.zenodo.org/docs/github/ and https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content.
5. A derived-data ZIP uploaded separately to an eligible permanent repository may require its **own** DOI and rights review. A GitHub source-release DOI does not automatically certify or preserve the expiring 16-file Actions artifact. Record actual links and issue dates only **after** completion.

**No DOI, source release, Zenodo toggle, data license, journal submission, or manuscript publication was performed by this report.**

## Private manuscript v8 mandatory corrections

The prior v7 contained section `7.2` and `7.3` **after References**. Reorder all `7.*` Data/Code Availability and coauthor-review sections ahead of the final Conclusion and References, preserving numerical Results and verified figure captions. Replace the earlier loose Data Availability implication with this exact scope:
- Public GitHub code and archived, expiring SHA256-verified source tables/figures exist, source run #42332230767 and frozen lock #42335868902.
- No published durable dataset DOI, versioned GitHub Release, or code license is yet verified.
- Original EFS2020 physical UTC/timezone and Idaho source-region cause remain unresolved.
- Publisher-specific source data links and checksums must stay clearly separate from derived-data redistribution permission.

**Publication readiness: collaborator-review, not submission-ready.** Focus remaining effort on legal/release metadata, external/source-owner clock verification, manuscript generality and targeted references. Do not launch another large battery sensitivity campaign.
