import pandas as pd
import pytest
from energy_transition.efs_four_state_denominator_candidate import four_state_candidate

def toy():
    return pd.DataFrame({
        "state":["California","Nevada","Oregon","Washington",
                 "Nevada","Washington","California"],
        "reeds_state":["CA","NV","OR","WA","NV","WA","CA"],
        "reeds_zone":["p9","p12","p5","p2","p12","p2","p9"],
        "Pd":[67028.96-34.99,8033.08,9281.36-17.49,16058.07,34.99,17.49,0.0],
        "LAF_state":[(67028.96-34.99)/67028.96,1.0,
                     (9281.36-17.49)/9281.36,1.0,
                     34.99/67028.96,17.49/9281.36,float("nan")],
        "substation_off":[False,False,False,False,False,False,True],
    },index=["2020001","2030001","2012001","2010001","2030005","2013019","3008161"])


def test_four_state_numerical_conservation_without_promotion():
    r=four_state_candidate(toy())
    assert r["offshore_auxiliaries_excluded_count"]==1
    assert all(v==pytest.approx(1.0) for v in r["source_state_weight_totals"].values())
    assert not r["EFS_demand_admitted"]
    assert not r["source_geography_independently_validated"]
    weights={(q["source_state"],q["reeds_zone"]):q["weight"]
             for q in r["source_to_reeds_zone_candidate_weights"]}
    assert weights[("CA","p12")]==pytest.approx(34.99/67028.96)
    assert weights[("OR","p2")]==pytest.approx(17.49/9281.36)


def test_new_missing_laf_without_offshore_signature_fails():
    b=toy()
    b.loc["3008161","substation_off"]=False
    with pytest.raises(ValueError,match="offshore auxiliary signature"):
        four_state_candidate(b)


def test_unexplained_denominator_change_fails():
    b=toy()
    b.loc["2020001","LAF_state"]*=0.99
    with pytest.raises(ValueError,match="denominator records"):
        four_state_candidate(b)
