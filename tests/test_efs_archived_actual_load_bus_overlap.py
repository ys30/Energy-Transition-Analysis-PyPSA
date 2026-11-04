import pandas as pd
import pytest
from types import SimpleNamespace
from energy_transition.efs_archived_actual_load_bus_overlap import audit

class Net:
    def __init__(self,selected_bus):
        ids=[str(i) for i in range(879)]
        self.buses=pd.DataFrame({
            "Pd":[1.]*55+[0.]*824,
            "LAF_state":[0.01]*879,
            "state":["New Mexico"]*53+["Texas"]*2+["New Mexico"]*824,
            "v_nom":[13.8]*55+[115.]*824,
            "substation_off":[False]*879,
        },index=ids)
        self.lines=pd.DataFrame({"bus0":["877"],"bus1":["878"]})
        self.transformers=pd.DataFrame(columns=["bus0","bus1"])
        self.generators=pd.DataFrame(columns=["bus"])
        self.loads=pd.DataFrame({"bus":[selected_bus],"p_set":[0.]},index=["EFS_test"])
        self.snapshots=pd.RangeIndex(8760)
        self.loads_t=SimpleNamespace(p_set=pd.DataFrame({"EFS_test":[10.]*8760}))

def test_actual_load_bus_overlaps_only_when_directly_attached():
    base=Net("877")
    r=audit(base,[(2030,Net("877")),(2040,Net("877")),(2050,Net("877"))])
    assert r["actual_source_53_bus_ids_ever_used_as_Load_bus"]==[]
    assert all(x["annual_EFS_load_mwh_on_53_positive_pd_zero_degree_buses"]==0 for x in r["archived_load_bearing_network_years"])
    assert all(x["load_components_outside_largest_line_transformer_connected_component"]==0 for x in r["archived_load_bearing_network_years"])
    assert not r["generator_POI_and_dispatch_validated"]

def test_real_direct_attachment_would_be_detected():
    base=Net("877")
    r=audit(base,[(2030,Net("2")),(2040,Net("2")),(2050,Net("2"))])
    assert r["actual_source_53_bus_ids_ever_used_as_Load_bus"]==["2"]
    assert all(x["annual_EFS_load_mwh_on_53_positive_pd_zero_degree_buses"]==87600 for x in r["archived_load_bearing_network_years"])

def test_missing_snapshot_hour_rejected():
    base=Net("877")
    bad=Net("877")
    bad.snapshots=pd.RangeIndex(8759)
    with pytest.raises(ValueError,match="time axis"):
        audit(base,[(2030,bad),(2040,Net("877")),(2050,Net("877"))])
