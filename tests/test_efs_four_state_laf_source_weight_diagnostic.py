"""Blocked-state real source weight diagnostics must never impute LAF."""
import pandas as pd
import pytest
from energy_transition.efs_four_state_laf_source_weight_diagnostic import audit_blocked_states


def sample():
    return pd.DataFrame({
        "state":["California","California","Nevada","Oregon","Washington"],
        "reeds_state":["CA","CA","NV","WA","WA"],
        "reeds_zone":["p9","p9","p10","p2","p2"],
        "LAF_state":[0.3,float("nan"),1.000522,float("nan"),float("nan")],
        "load_weight":[2.0,0.0,5.0,4.0,float("nan")],
        "Pd":[100.0,0.0,20.0,30.0,0.0],
    })


def test_zero_weight_laf_missing_remains_blocked():
    r=audit_blocked_states(sample())
    rows={x["state"]:x for x in r["blocked_state_diagnostics"]}
    assert rows["California"]["missing_laf_with_zero_load_weight"]==1
    assert rows["California"]["Pd_zero_on_missing_laf"]==1
    assert rows["California"]["laf_numerical_gate_passed"] is False
    assert rows["Nevada"]["observed_laf_mass"]==pytest.approx(1.000522)
    assert rows["Nevada"]["laf_numerical_gate_passed"] is False
    assert rows["Oregon"]["missing_laf_with_positive_load_weight"]==1
    assert rows["Oregon"]["Pd_positive_on_missing_laf"]==1
    assert rows["Oregon"]["Pd_is_verified_EFS_allocation_weight"] is False
    assert rows["Washington"]["missing_laf_with_invalid_or_absent_load_weight"]==1
    assert rows["Oregon"]["native_reeds_state_difference_count"]==1
    assert r["missing_laf_can_be_imputed"] is False
    assert r["all_four_states_empirically_admitted"] is False


def test_optional_source_weight_absence_is_visible_not_filled():
    r=audit_blocked_states(sample().drop(columns=["load_weight","Pd"]))
    assert not r["source_bus_load_weight_present"]
    assert not r["source_bus_Pd_present"]
    assert all(not x["Pd_attribute_present"] for x in r["blocked_state_diagnostics"])
    assert all(not x["load_weight_attribute_present"] for x in r["blocked_state_diagnostics"])


def test_bad_weight_and_missing_state_are_not_silently_accepted():
    x=sample()
    x.loc[x.state=="Oregon","load_weight"]=float("inf")
    r=audit_blocked_states(x)
    o=next(x for x in r["blocked_state_diagnostics"] if x["state"]=="Oregon")
    assert o["missing_laf_with_invalid_or_absent_load_weight"]==1
    with pytest.raises(ValueError,match="All four"):
        audit_blocked_states(sample().query("state != 'Washington'"))
