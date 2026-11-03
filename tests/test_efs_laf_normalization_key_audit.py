"""Prove differing native state and ReEDS assignment are not renormalized."""
import pandas as pd
import pytest
from energy_transition.efs_laf_normalization_key_audit import audit_laf_key_semantics


def test_two_key_semantics_are_reported_without_reallocation():
    buses=pd.DataFrame({
        "state":["CA","CA","NM"],
        "reeds_state":["CA","NV","NM"],
        "reeds_zone":["p9","p10","p31"],
        "LAF_state":[0.4,0.6,1.0],
    })
    report=audit_laf_key_semantics(buses)
    assert report["state_vs_reeds_state_disagreement_buses"]==1
    assert report["renormalization_performed"] is False
    assert report["historical_demand_admitted"] is False
    assert report["original_full_state_grouping_reconstructible_from_this_network"] is False
    by_state={x["reeds_state"]:x for x in report["observed_laf_by_reeds_state"]}
    assert by_state["CA"]["observed_laf_sum"]==pytest.approx(0.4)
    assert by_state["NV"]["observed_laf_sum"]==pytest.approx(0.6)
    assert not by_state["CA"]["raw_laf_sum_is_full_state_normalization_proof"]


def test_missing_laf_does_not_hide_state_assignment_differences():
    buses=pd.DataFrame({
        "state":["CA","CA"],"reeds_state":["CA","NV"],
        "reeds_zone":["p9","p10"],"LAF_state":[0.4,float("nan")]
    })
    r=audit_laf_key_semantics(buses)
    assert r["state_vs_reeds_state_disagreement_buses"]==1
    assert sum(x["missing_laf_count"] for x in r["observed_laf_by_reeds_state"])==1
    assert r["historical_demand_admitted"] is False


def test_missing_semantic_fields_block_audit():
    with pytest.raises(ValueError,match="Source network missing fields"):
        audit_laf_key_semantics(pd.DataFrame({"LAF_state":[1.0]}))


def test_full_state_names_compare_correctly_to_reeds_codes():
    buses=pd.DataFrame({
        "state":["Arizona","Arizona","Oregon","Oregon","Washington"],
        "reeds_state":["AZ","NV","OR","ID","OR"],
        "reeds_zone":["p8","p9","p5","p6","p2"],
        "LAF_state":[0.2,0.3,0.2,0.2,0.1],
    })
    report=audit_laf_key_semantics(buses)
    assert report["state_vs_reeds_state_disagreement_buses"]==3
    assert {(x["state"],x["reeds_state"]) for x in report["state_reeds_state_mismatch_examples"]} == {
        ("AZ","NV"),("OR","ID"),("WA","OR")
    }


def test_unknown_native_state_name_is_rejected_not_overcounted():
    buses=pd.DataFrame({
        "state":["Unknown State"],"reeds_state":["AZ"],
        "reeds_zone":["p8"],"LAF_state":[1.0],
    })
    with pytest.raises(ValueError,match="Unrecognized native state label"):
        audit_laf_key_semantics(buses)
