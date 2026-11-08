# Paper T — 2026-11-07 rights-aware deposit and reproducibility preflight

**No journal submission, GitHub Release, Zenodo deposit, new software license or DOI was created.** The private coauthor package remains off this public repository.

## Evidence state

- Actual T1–T5 files, five source-derived tables, three provenance records and original NASA POWER UTC/LST JSON are included in the private v13.2 review package.
- All **16** previous original-source evidence files match the accepted independent SHA-256 lock `docs/paper_t_frozen_supplement_sha256.txt`; both original NASA responses also match the pinned SHA-256 checksums.
- Main CI [#42444571836](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42444571836) **passed** for the complete-figures documentation commit `29a61656`.
- Programmatically verified that the private preflight ZIP contains exactly five original major PNG figures, four T1–T4 SVGs, source files and manuscript, with its own file-level SHA-256 index; **no** new scientific results are implied.

## Verified publisher terms, with separate source rights

| Source | Publisher statement checked | Operational decision |
|---|---|---|
| [NLR EFS 2020 catalog](https://data.nlr.gov/submissions/126) and [dataset license](https://data.nlr.gov/node/126/license) | Use/copy at no fee provided **full license notice appears in copies**, plus credit DOE/NREL/Alliance in publications | Original dataset and reproduced copies must preserve source notice; do not claim there was no license |
| [ReEDS demand profiles 2022, DOI 10.5281/zenodo.18461543](https://zenodo.org/records/18461543) | Open-access file; its viewed record did **not** show a specific readable license term | **Do not infer a redistribution license from open access**; check repository/maintainer terms before releasing upstream-derived table bytes |
| [NASA POWER](https://registry.opendata.aws/nasa-power/) | Data use, download and access are unrestricted; requests NASA POWER citation | Include source acknowledgment and citation |
| [This public GitHub repository](https://github.com/ys30/Energy-Transition-Analysis-PyPSA) | GitHub API currently reports `license:null`; no published Releases | Choose a code license only after copyright-holder approval; do not assign MIT/Apache by default |

[Zenodo's guidance](https://support.zenodo.org/help/en-gb/24-github-integration/149-how-to-specify-a-license-for-a-software-record-on-github) describes metadata license inheritance from `.zenodo.json`, `CITATION.cff`, GitHub metadata, then default; **never permit a default metadata value to substitute for an approved copyright license**.

## Author sign-off requirements before a permanent release

1. Determine which people/organizations own new repository code. Request agreement on the code-license choice; verify company/student/employer IP obligations.
2. Check ReEDS-derived tables/figures for applicable grant of reuse; do not assume the EFS license covers independent ReEDS distribution.
3. If distributing original EFS data copied from the publisher, include the **entire original license notice** in each relevant distributed copy; name source DOI `10.7799/1593122`, cite DOE/NREL/Alliance and preserve attribution.
4. Cite NASA POWER source; retain UTC/LST original byte hashes and paired 89-anchor comparison (8.186629 vs 0°C), not unequal-support 96 vs 89 as a direct effect comparison.
5. Decide whether the public artifact will include code, source-derived tables, figures, or only provenance and reproduction instructions. Avoid including the **private manuscript** without explicit publication approval.
6. Prepare a **code-only release** and optional separate rights-cleared **derived-data deposit**. A GitHub Release will not automatically preserve GitHub Actions artifact binaries.
7. Obtain and verify the **actual DOI after publication**, not a guessed DOI, preassigned placeholder or source dataset DOI treated as a new DOI.
8. Update manuscript Data Availability / Code Availability text based on what is **actually deposited** and reproducible.

**Scientific limits remain unchanged:** original EFS2020 `LocalHourID` physical time semantics unverified; NASA POWER is the same data returned in UTC/LST and is not independent observational validation; six-gate screening only supports abstention or submission for independent evidence review, not self-attested physical join authorization.

This report documents publisher terms and a conservative preflight decision; it is not legal advice or a proof of public redistribution authority.
