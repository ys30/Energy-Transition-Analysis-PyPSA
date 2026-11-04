from types import SimpleNamespace
import pandas as pd
from energy_transition.efs_actual_representative_load_bus_audit import audit

class Network:
    def __init__(self):
        self.buses=pd.DataFrame({
          "state":["New Mexico"]*3,"reeds_zone":["p1"]*3,
          "Pd":[0.,10.,30.],"LAF_state":[0.,0.25,0.75],
          "v_nom":[13.8,115.,115.],"substation_off":[False]*3,
        },index=["a","b","c"])
        self.lines=pd.DataFrame({"bus0":["a","b"],"bus1":["b","c"]})
        self.transformers=pd.DataFrame(columns=["bus0","bus1"])
        self.loads=pd.DataFrame({"bus":["a"]},index=["EFS_2030_p1_NM"])

def test_first_bus_rule_can_choose_zero_pd_despite_connected_positive_candidates():
    n=Network()
    df,r=audit(n,n)
    assert r["all_Load_targets_match_first_source_bus_per_zone"]
    assert r["selected_zero_original_pd_Load_count"]==1
    assert r["zones_with_connected_positive_pd_alternatives"]==1
    assert r["selected_zero_line_transformer_degree_Load_count"]==0
    assert not r["zone_representation_is_utility_certified"]
