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


def test_crossing_laf_mass_preserves_missing_weight_as_unknown():
    buses=pd.DataFrame({
        "state":["Arizona","Arizona","Oregon","Oregon","Washington"],
        "reeds_state":["AZ","NV","OR","ID","OR"],
        "reeds_zone":["p8","p9","p5","p6","p2"],
        "LAF_state":[0.2,0.3,0.4,float("nan"),0.1],
    })
    report=audit_laf_key_semantics(buses)
    crosses={(v["native_state"],v["reeds_state"]):v
             for v in report["cross_state_observed_laf_mass"]}
    assert crosses[("AZ","NV")]["observed_laf_mass"]==pytest.approx(0.3)
    assert crosses[("OR","ID")]["missing_laf_bus_count"]==1
    assert crosses[("OR","ID")]["observed_laf_mass"]==pytest.approx(0.0)
    assert crosses[("OR","ID")]["original_full_state_mass_reconciled"] is False
    origins={v["native_state"]:v for v in report["observed_laf_by_native_state"]}
    assert origins["AZ"]["observed_crossing_laf_mass"]==pytest.approx(0.3)
    assert origins["OR"]["missing_laf_bus_count"]==1
    assert not origins["OR"]["is_full_state_denominator_verified"]
    assert report["historical_demand_admitted"] is False


def test_target_reeds_mass_decomposition_separates_native_and_inbound():
    buses=pd.DataFrame({
        "state":["Arizona","Nevada","Oregon","Oregon","Washington"],
        "reeds_state":["NV","NV","OR","WA","OR"],
        "reeds_zone":["p9","p9","p5","p2","p5"],
        "LAF_state":[0.1,0.5,0.4,0.2,float("nan")],
    })
    report=audit_laf_key_semantics(buses)
    zones={r["reeds_state"]:r for r in report["target_reeds_state_laf_decomposition"]}
    assert zones["NV"]["native_state_matching_observed_laf"]==pytest.approx(0.5)
    assert zones["NV"]["other_native_state_inbound_observed_laf"]==pytest.approx(0.1)
    assert zones["NV"]["total_observed_laf"]==pytest.approx(0.6)
    assert zones["OR"]["missing_laf_bus_count"]==1
    assert zones["OR"]["other_native_state_inbound_observed_laf"]==pytest.approx(0.0)
    assert zones["WA"]["other_native_state_inbound_observed_laf"]==pytest.approx(0.2)
    assert not zones["NV"]["empirical_state_load_transfer_verified"]
