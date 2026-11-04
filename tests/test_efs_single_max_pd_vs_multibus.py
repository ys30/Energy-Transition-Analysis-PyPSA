import pandas as pd
import pytest
from energy_transition.efs_single_max_pd_vs_multibus import compare

def source():
    a=[]
    for i in range(20):
        fallback=i==0
        a.append({"Load_id":f"L{i}","original_bus_id":f"a{i}",
          "candidate_buses_source_ids":f"a{i}" if fallback else f"a{i};b{i}",
          "candidate_bus_pd_shares":"1" if fallback else "0.1;0.9",
          "original_zone_annual_mwh":100.0,
          "share_of_zone_load_relocated_from_original_bus":0. if fallback else 0.9,
          "fallback_original_bus_no_positive_pd_candidate":fallback})
    return pd.DataFrame(a)

def test_separate_single_bus_from_multibus_effect():
    rows,r=compare(source())
    assert r["original_zone_count"]==20
    assert r["candidate_fallback_zones"]==1
    assert r["zones_differing_under_single_max_pd"]==19
    assert r["zones_differing_under_pd_weighted_multibus"]==19
    assert r["original_2030_archived_annual_mwh"]==2000.
    assert r["single_max_pd_annual_mwh_on_different_bus"]==1900.
    assert r["multi_pd_weighted_annual_mwh_on_different_bus"]==pytest.approx(1710.)
    assert not r["full_western_opf_solved"]

def test_invalid_weights_rejected():
    d=source()
    d.loc[1,"candidate_bus_pd_shares"]="0.2;0.9"
    with pytest.raises(ValueError,match="Nonconservative"):
        compare(d)

def test_fallback_mismatch_rejected():
    d=source()
    d.loc[0,"candidate_buses_source_ids"]="wrong"
    with pytest.raises(ValueError,match="Fallback"):
        compare(d)
