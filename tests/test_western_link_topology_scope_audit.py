import pandas as pd
from energy_transition.western_link_topology_scope_audit import audit_link_scope

class Net:
    def __init__(self):
        self.buses=pd.DataFrame(index=["2053003","2053000","2077001","a","b"])
        self.lines=pd.DataFrame({"bus0":["2053003"],"bus1":["a"]})
        self.transformers=pd.DataFrame({"bus0":["2053000"],"bus1":["a"]})
        self.links=pd.DataFrame({"bus0":["2077001","b"],"bus1":["a","2053003"],
                                 "carrier":["DC","DC"],"p_nom":[100.,200.],
                                 "efficiency":[0.98,0.98]})
        self.generators=pd.DataFrame()

def test_links_change_descriptive_components_without_certifying_physics():
    r=audit_link_scope(Net())
    assert r["source_link_count"]==2
    assert r["line_transformer_component_count"]==3
    assert r["line_transformer_degree_zero_bus_count"]==2
    assert r["undirected_all_branch_types_component_count"]==1
    assert r["undirected_all_branch_types_degree_zero_bus_count"]==0
    assert r["zero_degree_bus_reduction_after_link_edges"]==2
    assert not r["full_electrical_network_islanding_certified"]
    assert not r["empirical_2030_2050_generation_dispatch_admitted"]
    a={x["bus"]:x for x in r["high_risk_candidates"]}
    assert a["2077001"]["additional_incident_links"]==1

def test_no_links_does_not_fake_connectivity():
    n=Net()
    n.links=n.links.iloc[0:0]
    r=audit_link_scope(n)
    assert r["undirected_all_branch_types_component_count"]==3
    assert r["zero_degree_bus_reduction_after_link_edges"]==0
