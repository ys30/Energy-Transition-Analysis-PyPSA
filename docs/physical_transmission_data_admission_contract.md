# Project B physical transmission data admission contract

## Current standing

The independent 2024 CISO/BPAT gas-only hourly baseline and the synthetic AC Line optimization are computational engineering demonstrations. Neither establishes an empirically calibrated interconnection.

The pre-ingestion modules `wecc_ads_archive_inventory.py`, `transmission_branch_case_audit.py`, `transmission_evidence_gate.py` and `pypsa_line_evidence_adapter.py` must be interpreted as **structural safety gates**, not external provenance authentication. A CSV field `evidence_status=independently_verified` or a plausible-looking URL cannot establish that the original publisher supplied the rated branch impedance and thermal capacity.

## Conditions for advancing beyond a synthetic model

1. Acquire the case through a licensed/publicly authorized route. Record case vintage, planning-versus-historical meaning, permissions and SHA-256 of untouched source files.
2. Inspect the real archive/database schema and produce a documented mapping for electrical buses, line terminals, voltage base, r/x units, rated MVA or MW limits, and offline/parallel circuit interpretation. **Do not assume** a WECC planning model is a 2024 historical observed network.
3. Perform independent source-level checks against the original official documentation or electrical model, not merely a `source_url` provided inside a user-supplied CSV.
4. Verify that BA-to-bus aggregation and generator/demand mapping preserve energy balances; evaluate network losses, inter-BA interchange sign conventions, thermal limits and topology before making physical-calibration claims.
5. Run PyPSA Line optimization on the verified case; compare with independent measurements, report time-coverage/uncertainties and maintain scenario versus validated-history labels.

## Current engineering status

- Synthetic AC Line test: **verified** (see [solver output](verified_synthetic_ac_line_sweep.md)).
- EIA-930 CISO/BPAT independent gas-only 2024 pilot: **verified engineering baseline** (see [numerical acceptance](verified_2024_two_ba_hourly_numerical_acceptance.md)).
- WECC case physically verified and converted: **not completed**.
- Empirical 2024 interconnected CISO–BPAT calibration: **not completed**.

No authentic WECC network archive is included in this repository, and no actual historical transmission ratings have been certified here.
