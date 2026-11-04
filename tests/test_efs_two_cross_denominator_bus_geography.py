import pandas as pd
import pytest
from energy_transition.efs_two_cross_denominator_bus_geography import inspect_bus_crossings

def data():
    return pd.DataFrame({
        "Pd":[34.99,17.49],
        "LAF_state":[34.99/67028.96,17.49/9281.36],
        "state":["Nevada","Washington"],
        "reeds_state":["NV","WA"],
        "reeds_zone":["p10","p2"],
        "county":["A","B"],
        "x":[-115.0,-123.0],"y":[36.0,46.0],
    },index=["2030005","2013019"])

def test_both_source_denominators_and_metadata_are_reproduced():
    r=inspect_bus_crossings(data())
    assert r["target_bus_count"]==2
    assert r["buses"][0]["exported_geography"]["county"]=="A"
    assert r["buses"][1]["inferred_source_denominator_Pd"]==pytest.approx(9281.36)
    assert not r["source_full_state_recovered"]
    assert not r["empirical_EFS_admitted"]

def test_changed_source_weight_is_not_silently_accepted():
    b=data()
    b.loc["2030005","LAF_state"]=0.1
    with pytest.raises(ValueError,match="Source denominator changed"):
        inspect_bus_crossings(b)
