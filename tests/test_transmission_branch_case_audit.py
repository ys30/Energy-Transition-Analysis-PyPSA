import pandas as pd
import pytest
from energy_transition.transmission_branch_case_audit import audit_branch_case


def sample():
    return pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":100.,
        "reactance_pu":0.12,"reactance_ohm":6.,
        "resistance_ohm":0.4,"nominal_kv":230.,
        "source_url":"https://example.org/test-only","source_year":2034,
        "evidence_status":"independently_verified",
    }])


def test_planning_case_never_becomes_historical_calibration():
    audit=audit_branch_case(sample(),case_year=2034,kind="planning")
    assert audit["ready_for_engineering_review"]
    assert not audit["ready_for_historical_2024_calibration"]
    assert not audit["ready_for_pypsa_physical_calibration"]
    assert not audit["source_authenticity_independently_confirmed"]


def test_mismatched_source_year_rejected():
    with pytest.raises(ValueError,match="year"):
        audit_branch_case(sample(),case_year=2024,kind="historical")


def test_unverified_provenance_rejected():
    data=sample()
    data.loc[0,"evidence_status"]="unknown"
    with pytest.raises(ValueError,match="independently verified"):
        audit_branch_case(data,case_year=2034,kind="planning")
