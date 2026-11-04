import pandas as pd
from energy_transition.western_degree_zero_origin_audit import inspect

class Net:
    def __init__(self):
        self.buses=pd.DataFrame({
            "substation_off":[False,False,True,False],
            "Pd":[5.0,6.0,0.0,1.0],
            "LAF_state":[0.5,0.5,None,0.1],
            "state":["NM","NM","CA","NM"],
            "v_nom":[115.,115.,115.,230.]
        },index=["a","b","offshore","isolated_main"])
        self.lines=pd.DataFrame({"bus0":["a"],"bus1":["b"]})
        self.transformers=pd.DataFrame({"bus0":[],"bus1":[]})
        self.links=pd.DataFrame({"bus0":["a"],"bus1":["b"]})
        self.generators=pd.DataFrame(columns=["bus"])
        self.loads=pd.DataFrame(columns=["bus"])

def test_partition_separates_offshore_and_original_degree_zero():
    r=inspect(Net())
    assert r["line_transformer_zero_degree_bus_count"]==2
    assert r["offshore_and_null_laf_zero_degree_count"]==1
    assert r["nonoffshore_and_nonnull_laf_zero_degree_count"]==1
    assert r["zero_degree_zero_pd_count"]==1
    assert r["zero_degree_positive_pd_count"]==1
    assert r["zero_degree_positive_pd_total_mw"]==1.0
    assert r["zero_degree_link_touched_count"]==0
    assert not r["full_western_electric_dispatch_verified"]
