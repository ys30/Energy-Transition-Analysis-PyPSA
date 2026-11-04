import pandas as pd
import pytest
from energy_transition.eia860_top3_candidate_network_topology import topology_review

class Net:
    def __init__(self):
        self.buses=pd.DataFrame({"x":[-105.,-105.1,-105.2,-108.],"y":[35.,35.1,35.2,46.],
           "state":["New Mexico","New Mexico","New Mexico","Montana"],
           "reeds_state":["NM","NM","NM","MT"],"reeds_zone":["p1","p1","p1","p3"]},
           index=["2053003","2053000","x1","2077001"])
        self.lines=pd.DataFrame({"bus0":["2053003","2053000"],"bus1":["x1","x1"]},
            index=["L1","L2"])
        self.transformers=pd.DataFrame({"bus0":["2053003"],"bus1":["2053000"]},index=["T1"])
def plants():
    rows=[]
    for id,b,la,lo,c in [("1","2053003",35.,-105.,200.),
                         ("2","2053000",35.1,-105.1,300.),
                         ("3","2077001",46.,-108.,400.)]:
        rows.append({"plant_id":id,"nearest_candidate_bus":b,"distance_km":100.,
                    "operating_nameplate_mw":c,"plant_latitude":la+1,"plant_longitude":lo+1,
                    "bus_latitude":la,"bus_longitude":lo,"generator_count":1})
    # Real archive requires exactly 63 plants; assign each ID uniquely
    return pd.DataFrame([dict(rows[i%3],plant_id=str(i+1)) for i in range(63)])

def test_real_source_network_incidences_without_poi_approval():
    r=topology_review(Net(),plants())
    d={x["synthetic_candidate_bus_id"]:x for x in r["audited_top_candidate_buses"]}
    assert d["2053003"]["archived_line_count"]==1
    assert d["2053003"]["archived_transformer_count"]==1
    assert d["2077001"]["distinct_topological_neighbors"]==0
    assert r["line_transformer_graph_connected_component_count"]==2
    assert r["real_utility_POI_connections_verified"]==0
    assert r["future_2030_2050_generation_dispatch_admitted"] is False

def test_wrong_bus_coordinates_rejected():
    p=plants()
    p.loc[0,"bus_latitude"]=33.
    with pytest.raises(ValueError,match="coordinate drift"):
        topology_review(Net(),p)

def test_invalid_plant_review_subset_rejected():
    p=plants().iloc[:-1]
    with pytest.raises(ValueError,match="63 EIA"):
        topology_review(Net(),p)
