"""LAF numerator must match the immutable pinned PyPSA-USA Pd formula."""
import pandas as pd
import pytest
from energy_transition.efs_pinned_pd_laf_denominator_audit import audit,FORMULA,GROUP

PIN_SOURCE=GROUP+"\n"+FORMULA+"\n"

def test_inferred_Pd_denominator_and_zero_Pd_missing_factors():
    b=pd.DataFrame({
        "state":["California"]*4,
        "reeds_state":["CA"]*4,
        "reeds_zone":["p9"]*4,
        "Pd":[20.0,30.0,0.0,10.0],
        "LAF_state":[0.2,0.3,float("nan"),0.1],
    })
    a=audit(b,PIN_SOURCE)
    ca=a["states"][0]
    assert ca["inferred_full_state_denominator_median_Pd"]==pytest.approx(100.0)
    assert ca["inferred_denominator_max_relative_deviation"]==pytest.approx(0)
    assert ca["missing_LAF_with_zero_Pd"]==1
    assert a["all_missing_laf_zero_Pd"]
    assert not a["missing_LAF_imputed"]
    assert not a["national_denominators_independently_verified"]
    assert a["original_LAF_numerator"]=="Pd"


def test_pos_Pd_zero_LAF_is_flagged():
    b=pd.DataFrame({
        "state":["Nevada"],"reeds_state":["NV"],"reeds_zone":["p9"],
        "Pd":[10.0],"LAF_state":[0.0],
    })
    a=audit(b,PIN_SOURCE)
    assert a["states"][0]["positive_Pd_zero_LAF_bus_count"]==1


def test_wrong_upstream_formula_fails_closed():
    b=pd.DataFrame({
        "state":["Oregon"],"reeds_state":["OR"],"reeds_zone":["p5"],
        "Pd":[10.0],"LAF_state":[1.0],
    })
    with pytest.raises(ValueError,match="formula not verified"):
        audit(b,PIN_SOURCE.replace('"Pd"','"load_weight"'))


def test_mixed_source_denominators_are_exposed_as_two_clusters():
    b=pd.DataFrame({
        "state":["Nevada","Nevada","Nevada"],
        "reeds_state":["NV","NV","NV"],
        "reeds_zone":["p9","p9","p9"],
        "Pd":[80.0,20.0,34.99],
        "LAF_state":[0.01,0.0025,34.99/67028.96],
    },index=["original_a","original_b","suspect_cross_border"])
    r=audit(b,PIN_SOURCE)
    clusters={c["inferred_denominator_Pd"]:c for c in r["states"][0]["inferred_denominator_clusters"]}
    assert set(clusters)=={8000.0,67028.96}
    assert clusters[67028.96]["positive_Pd_positive_LAF_buses"]==1
    assert "suspect_cross_border" in clusters[67028.96]["bus_examples"]
    assert clusters[67028.96]["original_full_state_label_verified"] is False
