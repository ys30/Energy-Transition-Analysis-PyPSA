# Paper T v13 — Editorial consolidation and reviewer-risk assessment

**Status:** private collaborator manuscript v13; no paper submission, public manuscript upload, GitHub release, data publication DOI or new external data work.

## What changed relative to the complete v12 draft

- Reorganized the journal-facing main text instead of appending another chronological amendment. Sections 7.1–7.8 in v12 mixed scientific reporting with a long sequence of source-run logs, SHA256 procedures and historical bug fixes; these have been preserved **outside** the main text in a private Supplement S1 with explicit archived-workflow links and reviewer checks.
- Reduced the main manuscript from ~53 KB to ~41 KB (roughly 23% fewer bytes), while retaining the original main Methods, Results, Discussion, key numerical findings, fail-closed limitations and five-figure reference list.
- Main text remains a **source identity / temporal admission methodology**, not a Western power-system forecast; Paper S's 540 hypothetical storage experiments remain separate.
- Kept NASA POWER primary comparison **8.1866292135 °C vs 0.0 °C on exactly 89 common UTC anchors**, with 7.7873958333 °C over 96 naive-label anchors as separate supplementary description; original two publisher API responses are SHA256 pinned in the earlier source-audit workflow.
- Kept the EFS/ReEDS 33 state-year / 289,080 source-hour data-result scope, 30/33 cross-release numerical near matches, Idaho mismatch, original sector reconstruction and first-half vs second-half fixed-candidate sign reversals. These remain deterministic, related-product diagnostics — not 289,080 independent experiments or certified EFS2020 physical UTC.
- Limited the six-gate software claim to **a machine-readable, conservative screening and abstention contract**. It cannot independently authenticate submitted evidence or authorize a physical join based on all-true self-reports; established [W3C PROV-O](https://www.w3.org/TR/prov-o/), [CF conventions](https://cfconventions.org/cf-conventions/cf-conventions.html), and [Frictionless](https://framework.frictionlessdata.io/docs/guides/validating-data) cover broader, more mature provenance/calendar/schema concerns.

## Target journal positioning

[The June 2026 Energy Informatics field editorial](https://doi.org/10.1186/s42162-026-00677-y) frames energy information representation, exchange, governance, validation, and software as core to the discipline. Its founding editorial [DOI 10.1186/s42162-018-0014-6](https://doi.org/10.1186/s42162-018-0014-6) distinguishes Research, Methodology, Software, and Dataset submission types. The most defensible **conditional** submission type for this draft is **Methodology**, not a new energy capacity-expansion model or independent demand-data measurement.

### Critical reviewer challenges not resolved by editorial shortening

| Criterion | Current evidence | What remains before submission |
|---|---|---|
| Numerically audited EFS/ReEDS source-series results | 33 year-state pairs, Idaho sector analysis, four source-derived figures | Publisher source release lineage and exact physical EFS2020 `LocalHourID` time semantics unresolved |
| External demonstration | Authentic NASA POWER UTC vs LST at one point / four days, correctly paired 89-hour sample | Still within one POWER product; not independently managed energy systems |
| Screening policy implementation | Strict six-gate declarations, untrusted self-attestation cannot authorize join, CI passed | Independent human/source-author evidence verification is not implemented |
| Novelty relative to W3C PROV, CF and schema validation | Clear domain-focused combination with fail-closed explicit decision | No head-to-head quantitative benchmark or demonstrated reduced false-join incidence |
| Data / code reproducibility | 16 EFS/ReEDS evidence files hash-locked; NASA API responses byte-pinned | Expiring Actions artifacts, no repo license, no permanent release/derived data DOI |
| Manuscript literary positioning | Five main figures, ~5,200-word v13 draft, working bibliography | Limited 14-entry reference list, bibliography/full metadata coauthor review and journal formatting pending |

**Editorial recommendation:** circulate v13 + private Supplement S1 to collaborators as a **methods-review draft**. Seek coauthor feedback on the truly novel testable claim and rights/DOI plan before further expansions. Avoid continually adding unneeded lag sensitivity cases. Do not publicly upload this private manuscript from the public repository.

## Code / evidence status

The last accepted NASA matched-support source CI is [#42419334016](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42419334016). Original-source five table / four figure supplement is [#42332230767](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42332230767) and its independently frozen SHA256 lock passed [#42335868902](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42335868902). The corrected six-gate screening implementation passed [#42413234084](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42413234084). The latest prior successful main CI was [#42419560249](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42419560249) if the live run confirms success; otherwise refer to the latest confirmed run rather than extrapolating.
