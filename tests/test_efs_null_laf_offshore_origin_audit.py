import pandas as pd
import pytest
from energy_transition.efs_null_laf_offshore_origin_audit import audit_offshore_laf_origin

SRC='''gdf_bus["LAF_state"] = gdf_bus["Pd"] / group_sums
offshore_buses.index = np.arange(3008161, 3008161 + len(offshore_buses))
Pd=0,
substation_off=True,
n = add_offshore_buses(n, offshore_buses)
'''

def test_offshore_added_after_laf_has_null_and_zero_pd():
    b=pd.DataFrame({
        "Pd":[0,10], "LAF_state":[float("nan"),1.],
        "substation_off":[True,False], "state":["California","California"],
        "reeds_state":["CA","CA"],"reeds_zone":["p9","p9"],
    },index=["3008161","2020001"])
    r=audit_offshore_laf_origin(b,SRC)
    assert r["null_laf_bus_count"]==1
    assert r["null_laf_offshore_both_indicators"]==1
    assert r["all_null_laf_buses_match_pinned_offshore_insertion_signature"] is True
    assert r["missing_laf_values_zero_imputed"] is False
    assert r["four_state_EFS_load_admitted"] is False

def test_missing_flag_means_offshore_origin_not_proven():
    b=pd.DataFrame({
        "Pd":[0], "LAF_state":[float("nan")],
        "substation_off":[False], "state":["Oregon"],
        "reeds_state":["OR"],"reeds_zone":["p5"],
    },index=["3008161"])
    r=audit_offshore_laf_origin(b,SRC)
    assert not r["all_null_laf_buses_match_pinned_offshore_insertion_signature"]

def test_wrong_upstream_insertion_order_rejected():
    b=pd.DataFrame({
        "Pd":[0],"LAF_state":[float("nan")],"substation_off":[True],
        "state":["Washington"],"reeds_state":["WA"],"reeds_zone":["p2"],
    },index=["3008161"])
    altered=SRC.replace('n = add_offshore_buses(n, offshore_buses)', 'something else')
    with pytest.raises(ValueError,match="anchors missing"):
        audit_offshore_laf_origin(b,altered)
