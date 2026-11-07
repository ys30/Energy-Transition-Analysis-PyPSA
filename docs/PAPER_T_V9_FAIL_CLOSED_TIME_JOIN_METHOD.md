# Paper T v9 — Executable, fail-closed physical-hour join admission contract

**Research status:** journal-oriented *Energy Informatics* methodology draft, **not** journal submitted, without data DOI, original EFS2020 physical clock certification, or a legal decision for redistributing publisher-derived tables.

## Independently checked implementation status

- [Passing source-agnostic six-gate policy CI #42399304704](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42399304704).
- [Passing full main CI #42399304765](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42399304765).
- Implemented in `src/energy_transition/temporal_join_admission_policy.py`.
- Tested in `tests/test_temporal_join_admission_policy.py`, including incomplete passport, missing evidence basis, mislabeled Boolean, near-perfect numerical-only match, positive synthetic all-pass contract and one-blocked-gate cases.
- CI artifact `paper-t-physical-hour-join-admission-passport` contains `efs2020_reeds2022_hour_join_decision.json`. Its result for the current EFS2020/ReEDS2022 pair is **BLOCK_PHYSICAL_JOIN**.

## Six separate mandatory gates

| Gate | Requirement | EFS2020/ReEDS2022 evidence result |
|---|---|---|
| G1 Original-source integrity | Source-file checksums and scenario identity verified | **Pass** (independent archived original EFS source and MD5-verified HDF5) |
| G2 Native physical calendar | Hour-ending/start, leap/DST, local/UTC offset for BOTH releases authoritatively documented | **Blocked** (old EFS `LocalHourID` physical calendar unresolved) |
| G3 Physical-hour crosswalk | Reversible authority-backed mapping from BOTH source hour identities to a common physical timestamp | **Blocked** (best-fit numerical lag is NOT time certification) |
| G4 Weather-year provenance | Compatible representative chronological/weather-year semantics verified | **Blocked** |
| G5 Spatial compatibility | Matching geographical domain or verified substate allocation/timezone footprint | **Blocked** (Idaho sector/subsector labels are end uses, not geographic zones) |
| G6 One-to-one physical join keys | No duplicate source timestamp, missing nonwrapping border, or fabricated cross-year values | **Blocked** (no admitted physical timestamp join) |

Define `A_physical = AND(G1,G2,G3,G4,G5,G6)`. Only a pair with all independently evidenced gates passed may be admitted to a physical hour join. *This is an explicit conservative policy contract, not a statistically estimated mapping.* A high Pearson correlation, 1 MW near-match threshold, 0.01 MW strict screen, or −2/−3 source-index shift does not satisfy the metadata requirements.

### What this improvement does and does not establish

This addresses a **transferability-of-method question** by turning the earlier EFS/ReEDS narrative into a source-independent, executable metadata admission interface. It records an auditable explicit outcome and fails on malformed or incomplete evidence.

**Limitations:**
- The generic function checks that justifications exist; it cannot verify the *truth* of caller-provided evidence. Independent human, source-author or publisher documentation remains necessary.
- Synthetic all-pass unit tests exercise software logic; they do **not** validate a real independent source pair.
- Empirical transferability to unrelated climate/energy products remains untested. Do not claim quantitative generalization, a source-clock transformation, or demonstrated improvement over existing interoperability frameworks.
- The original 16-source-evidence supplement is already SHA256 frozen, but is a time-limited Actions archive, not a repository DOI. Its license and permanent distribution must be checked independently.
- Paper T complete manuscript v9 remains **private**; public repository contains only code, machine-readable evidence passport and technical methods notes.

## Suggested publication-methods framing

1. Method: two layers of assurance—**numerical source-series comparability** and **physical join admissibility**—must be separated.
2. Case study: EFS2020/ReEDS2022 annual TWh agreement, 30/33 state-year numerical lag near-matches and unresolved Idaho residuals.
3. Reusable software: six evidence gates; automatic fail-closed decision for a source pair with documented missing provenance.
4. Generalization limit: methods code is source independent but the present numerical experiment involves one related model-data lineage. Broader empirical validation would require a separate source family, not new claims about this particular one.
5. Submission readiness: target first journal for scope assessment is *Energy Informatics*, with editorial fit pending actual peer review; no approval, DOI or publication has occurred.

## Reproduction

```bash
python -m pip install pytest
PYTHONPATH=src python -m pytest -q tests/test_temporal_join_admission_policy.py
PYTHONPATH=src python -m energy_transition.temporal_join_admission_policy \
  --out outputs/paper_t_temporal_admission/efs2020_reeds2022_hour_join_decision.json
```

For original data and figures T1–T4, refer to `docs/PAPER_T_V6_SOURCE_SUPPLEMENT_SHA256_REPRODUCIBILITY.md` and `docs/paper_t_frozen_supplement_sha256.txt`; the policy output is a distinct provenance decision artifact, not an alteration to the 16 accepted evidence bytes.
