import copy
import pytest
from energy_transition.temporal_join_admission_policy import assess,DEFAULT_PASSPORT,GATES

def test_real_source_pair_blocks_physical_join():
    result=assess(DEFAULT_PASSPORT)
    assert result["decision"]=="BLOCK_PHYSICAL_JOIN"
    assert result["failed_gates"]==[g for g in GATES if g!="source_integrity"]
    assert result["fitted_source_index_lag_counts_as_authoritative_clock"] is False
    assert "published scenario labels" in GATES["source_integrity"]
    assert "not authenticated" in DEFAULT_PASSPORT["evidence"]["source_integrity"]["basis"]
    assert result["gate_results"]["source_integrity"]["passed"] is True

def test_numerical_alignment_cannot_override_source_clock_evidence():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    passport["numerical_MAE_mw"]=0.
    passport["selected_lag_hours"]=-2
    assert not assess(passport)["physical_hour_join_admitted"]

def test_positive_fixture_requires_every_documented_gate():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    for item in passport["evidence"].values():
        item["passed"]=True
        item["basis"]="Synthetic valid-contract fixture for a fully documented source pair"
    ready=assess(passport)
    assert ready["decision"]=="READY_FOR_INDEPENDENT_SOURCE_REVIEW"
    assert ready["declared_gate_evidence_complete"]
    assert not ready["physical_hour_join_admitted"]
    assert not ready["independent_evidence_verification_performed"]
    passport["evidence"]["weather_year"]["passed"]=False
    assert assess(passport)["decision"]=="BLOCK_PHYSICAL_JOIN"

def test_unknown_missing_gate_fails():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    del passport["evidence"]["physical_crosswalk"]
    with pytest.raises(ValueError,match="six gates"):
        assess(passport)

def test_missing_basis_fails():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    passport["evidence"]["geography"]["basis"]=""
    with pytest.raises(ValueError,match="nonempty"):
        assess(passport)

def test_truthy_text_cannot_be_accepted_as_boolean():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    passport["evidence"]["native_calendar"]["passed"]="true"
    with pytest.raises(ValueError,match="explicit boolean"):
        assess(passport)

def test_malicious_all_true_self_attestation_cannot_authorize_join():
    passport=copy.deepcopy(DEFAULT_PASSPORT)
    for item in passport["evidence"].values():
        item["passed"]=True
        item["basis"]="I say this has been verified"
    result=assess(passport)
    assert result["decision"]=="READY_FOR_INDEPENDENT_SOURCE_REVIEW"
    assert not result["physical_hour_join_admitted"]
    assert not result["independent_evidence_verification_performed"]
