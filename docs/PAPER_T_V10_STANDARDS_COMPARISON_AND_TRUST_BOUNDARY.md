# Paper T v10 — Temporal join admission versus established data standards

**Status:** methodology critique, corrected executable policy, and source-linked literature comparison. The complete manuscript remains private.

## Standards comparison

| Established practice | What it already supplies | Residual gap addressed by Paper T | What Paper T must NOT claim |
|---|---|---|---|
| [W3C PROV-O](https://www.w3.org/TR/prov-o/) | General representations of provenance entities, activities and agents, plus derivation/usage relationships | A specific **decision contract** for admitting hourly joins across two modeled energy-data releases | A new general provenance ontology or a replacement for PROV |
| [CF Conventions, time metadata](https://cfconventions.org/cf-conventions/cf-conventions.html) | Time coordinates with reference units and calendar semantics, including calendars with non-identical leap handling | Detects when a **cross-product** physical-hour join is underdocumented despite source values' numerical similarity | A replacement for CF calendar validation, or evidence that both specific sources conform to CF |
| [Frictionless Framework validation](https://framework.frictionlessdata.io/docs/guides/validating-data) | Structured tables, schema descriptions and checks for resource/package validity | Separates validated table integrity from permission to treat the records as *the same physical hours* | A new generic schema validator |
| Related demand-data QC and screening (Ruggles et al., 2020) | Screening/imputation of missing or unreliable demand observations | Cross-release provenance and clock admissibility, with abstention rather than guessed corrections | Superiority in predictive accuracy or error detection without an independent benchmark |

The distinctive *combination* is: numerical source-series comparison + independent metadata proof obligations + **conservative explicit abstention** for a physical-time join. The six criteria are a domain-specific workflow policy synthesized from existing ideas, **not six individually novel scientific discoveries**.

## Adversarial software audit: self-attestation problem

The original v9 `assess()` treated six caller-supplied `passed=True` entries plus nonempty justifications as sufficient to emit `ADMIT_PHYSICAL_JOIN`. This is too strong: text entered by an analyst is not authoritative source authentication. v10 therefore **removes automatic physical join authorization entirely** from this simple metadata-screening function. It now has three distinct outcomes:

- `BLOCK_PHYSICAL_JOIN` when any required evidence gate is missing/not declared satisfied.
- `READY_FOR_INDEPENDENT_SOURCE_REVIEW` when all six declarations are present, but **none have been independently verified by this function**.
- Actual physical-hour join authorization is **out of scope**; it requires a separately governed evidence review/checksum/source-authority verification and should never be inferred from a self-authored JSON passport.

The v10 regression suite includes an adversarial all-true passport with only an arbitrary sentence as each “basis”; this **must not authorize a physical join**. The real EFS2020/ReEDS2022 case stays `BLOCK_PHYSICAL_JOIN`, and the source-gap evidence remains unchanged.

## Interpretation of the machine-readable passport

`physical_hour_join_admitted=false` for every outcome from the current policy. `declared_gate_evidence_complete` indicates only that the declarations are present and all self-report a pass. `independent_evidence_verification_performed=false` makes the trust boundary explicit. Thus the software tests assert **logical screening**, not physical source identity and not successful independent assurance.

## Publication contribution and remaining limits

Paper T contributes a **source-linked case study and an executable abstention-oriented evidence contract**. Its demonstrable numerical findings remain the original 33 state-year comparisons, nonwrapping source-index offsets, and Idaho residual/subsector falsification. Its proposed policy is reusable at the interface level but has not demonstrated better interoperability outcomes, lower false-join rates or superior data quality against PROV-O, CF or Frictionless.

The next genuinely meaningful validation—not additional EFS shift searches—would apply the protocol to an unrelated, authority-documented energy/weather source pair with known timestamps, then compare a metadata-naive join to a properly admitted join. Do not claim this result before such external data are obtained.

## Public reproducibility

- Code: `src/energy_transition/temporal_join_admission_policy.py`
- Tests: `tests/test_temporal_join_admission_policy.py`
- Workflow: `.github/workflows/paper-t-hour-join-admission.yml`
- Verified data evidence: `docs/paper_t_frozen_supplement_sha256.txt` (16-file SHA256 lock)
- Source product clock remains unverified: original EFS2020 `LocalHourID` physical UTC conversion and geographic timezone are not established.

**No DOI, software/data license, or public manuscript submission has been authorized or performed.**
