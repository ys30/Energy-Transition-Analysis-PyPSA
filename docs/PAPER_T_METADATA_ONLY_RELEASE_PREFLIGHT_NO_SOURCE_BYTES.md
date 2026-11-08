# Paper T — metadata-only release candidate, NOT PUBLISHED (2026-11-07)

## Source-specific rights findings

The 2022 ReEDS source [Zenodo record 18461543](https://zenodo.org/records/18461543) clearly gives source citation, a public file list and 2012 weather-year/CST hour-ending data semantics, but the public Rights/License display checked here has **no readable named license**. Zenodo's [permission guidance](https://support.zenodo.org/help/en-gb/2-content/21-can-i-get-permission-to-use-a-specific-record) states reuse depends on that **specific** record's license; metadata itself can be reused CC0, whereas files and derivatives need their own authorization. Zenodo default CC BY in new-deposit forms must NOT be assigned retroactively to someone else's source record. ReEDS original/derived numeric source bytes and figures remain **on hold for public deposit** until a rights holder confirms permissions.

EFS2020 has a publisher-specific use/copy notice requiring full notice retention and credit, and NASA POWER requests source acknowledgment. This repository still has no approved software LICENSE or GitHub Release. Source integrity and SHA256 are not grants of reuse permission.

## Prepared private metadata-only candidate

A six-file preflight ZIP (kept **outside** public GitHub) contains **only our original descriptive metadata, source URLs, reproducibility workflow links, draft citation relationships, a rights-status JSON, questions for rights holders and a no-release checklist**. It deliberately excludes all original ReEDS/EFS and NASA numerical files, derived source tables, figures, unpublished manuscripts and unapproved licensed code. Each staged file has SHA256 in its own manifest. It is **not** a published dataset and receives **no DOI**.

This avoids accidentally distributing publisher source-derived files merely to advertise reproducibility. The existing private full-data review bundle remains unchanged for collaborator use.

## Ready-for-coauthor/maintainer questions

1. ReEDS 2022 maintainer: What exact license, rights URL and attribution notice applies to `demand_EFS_REFERENCE.h5`? Can users openly deposit state-year lag comparison tables, Idaho subsector totals, residual marginals and figures derived partly from that file? Is a written permissions statement possible?
2. Analysis code authors: who owns repository code and may approve a software license (consider employer IP policies)?
3. Manuscript authors: approve paper disclosure and Figure T1–T5/publication scope separately.
4. Data archivist: determine separate code and data releases, permanent licenses/rights, creators/ORCIDs, versioned deposits and verified DOIs **only after approval**.

## Gates remaining blocked

- ReEDS data-specific redistribution rights unresolved.
- Full publisher license notice needed for applicable EFS copies.
- Code copyright/licensing decision unresolved.
- Private manuscript dissemination not authorized.
- No permanent versioned deposit or DOI actually issued.
- Original EFS2020 physical time clock not independently certified; NASA UTC/LST known-transform control is not independent-source observational validation.

No CI experiment, publication, release, license or Zenodo deposition is claimed by this note.
