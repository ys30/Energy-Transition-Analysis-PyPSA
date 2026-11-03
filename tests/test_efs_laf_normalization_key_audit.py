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
