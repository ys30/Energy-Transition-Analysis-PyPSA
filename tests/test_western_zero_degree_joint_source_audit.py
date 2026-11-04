import pandas as pd
import pytest
from energy_transition.western_zero_degree_joint_source_audit import audit

class Network:
    def __init__(self):
        self.buses=pd.DataFrame({
            "substation_off":[False,False,False,True],
            "Pd":[2.0,0.0,6.0,0.0],
            "LAF_state":[0.4,0.0,0.6,None],
            "v_nom":[13.8,115.0,20.0,230.0],
            "state":["NM","NM","NM","CA"],
            "sub_id":[12,13,14,None],
        },index=["pos","zero","connected","offshore"])
        self.lines=pd.DataFrame({"bus0":["zero"],"bus1":["connected"]})
        self.transformers=pd.DataFrame({"bus0":[],"bus1":[]})

def test_joint_partition_preserves_exact_pd_source():
    cross,positive,r=audit(Network())
    assert r["line_transformer_zero_degree_count"]==2
    assert r["offshore_source_zero_degree_nodes"]==1
    assert r["nonoffshore_source_zero_degree_nodes"]==1
    assert r["zero_degree_positive_pd_count"]==1
    assert r["zero_degree_positive_source_pd_mw"]==pytest.approx(2)
    assert r["nonoffshore_low_voltage_25kv_or_less"]==1
    assert len(positive)==1
    assert positive.iloc[0].bus_id=="pos"
    assert cross.bus_count.sum()==2
    assert r["bus_pruning_authorized"] is False
    assert r["source_type_generator_terminal_verified"] is False

def test_bad_source_metadata_fails():
    n=Network()
    n.buses.loc["pos","Pd"]=float("nan")
    with pytest.raises(ValueError,match="Invalid"):
        audit(n)
