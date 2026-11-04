from types import SimpleNamespace
import pandas as pd
import pytest
from energy_transition.efs_pd_weighted_bus_placement_sensitivity import compare

class Net:
    def __init__(self):
        # 20 source zones, one positive-Pd alternative in 19, and one fallback.
        ids=[];state=[];zone=[];pdv=[];v=[]
        edges=[]
        for i in range(20):
            name=f"z{i}"
            a=f"{name}_first";b=f"{name}_positive"
            ids.extend([a,b]);state.extend(["New Mexico"]*2);zone.extend([name]*2)
            pdv.extend([0.,20. if i else 0.]);v.extend([115.,115.])
            edges.append((a,b))
        self.buses=pd.DataFrame({"state":state,"reeds_zone":zone,
          "Pd":pdv,"v_nom":v,"substation_off":[False]*40},index=ids)
        self.lines=pd.DataFrame(edges,columns=["bus0","bus1"])
        self.transformers=pd.DataFrame(columns=["bus0","bus1"])
        # Connect all zones into one main component
        self.lines=pd.concat([self.lines,pd.DataFrame(
            [(f"z{i}_first",f"z{i+1}_first") for i in range(19)],
            columns=["bus0","bus1"])],ignore_index=True)
        self.loads=pd.DataFrame({"bus":[f"z{i}_first" for i in range(20)],
            "p_set":[0.]*20},index=[f"L{i}" for i in range(20)])
        self.generators=pd.DataFrame()
        self.snapshots=pd.RangeIndex(8760)
        self.loads_t=SimpleNamespace(p_set=pd.DataFrame(
            {f"L{i}":[float(i+1)]*8760 for i in range(19)}))

def test_conservation_and_explicit_zero_candidate_fallback():
    n=Net()
    d,r=compare(n,n)
    assert r["source_original_2030_loads"]==20
    assert r["zones_with_pd_weighted_connected_alternative"]==19
    assert r["zones_falling_back_to_first_bus"]==1
    assert r["original_and_candidate_each_hour_demand_equal"]
    assert r["hourly_zonal_demand_preserved"]
    assert r["OPF_solved"] is False
    assert d.loc[d.Load_id.eq("L0"),"fallback_original_bus_no_positive_pd_candidate"].iloc[0]
    assert r["hypothetical_reassigned_fraction_of_original_annual_load"]==pytest.approx(189/190)
    assert r["original_annual_load_mwh"]==pytest.approx(sum(range(1,20))*8760)

def test_missing_archived_hour_rejected():
    n=Net();n.snapshots=pd.RangeIndex(8759)
    with pytest.raises(ValueError,match="original 2030"):
        compare(n,n)

def test_invalid_source_pd_rejected():
    n=Net();n.buses.loc["z2_positive","Pd"]=-1.
    with pytest.raises(ValueError,match="Invalid original candidate Pd"):
        compare(n,n)
