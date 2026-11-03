"""Original bus identity trace preserves provenance, does not approve generator injections."""
import pandas as pd
import pytest
import pypsa
from energy_transition.eia860_source_bus_identity_trace import trace


def setup(tmp_path):
    n=pypsa.Network()
    n.add("Bus","a",v_nom=500,sub_id="sub-alpha",state="AZ",x=-112,y=33)
    n.add("Bus","b",v_nom=115,sub_id="sub-beta",state="AZ",x=-112.1,y=33.1)
    n.add("Line","l1",bus0="a",bus1="b",r=0.01,x=0.1,s_nom=50)
    n.add("Transformer","t1",bus0="a",bus1="b",s_nom=30)
    grid=tmp_path/"grid.nc"
    n.export_to_netcdf(grid)
    c=tmp_path/"c.csv"
    pd.DataFrame([{"plant_id":"6008","candidate_bus_id":"a","candidate_bus_voltage_kv":500.0,
                   "distance_km":0.02,"electrical_connection_verified":False}]).to_csv(c,index=False)
    return grid,c


def test_traces_real_edges_and_never_approves(tmp_path):
    grid,c=setup(tmp_path)
    out=tmp_path/"trace.csv"
    summary=trace(grid,c,out)
    assert summary["source_bus_records"]==1
    assert summary["source_line_and_transformer_incidents"]==2
    assert summary["with_substation_identifier"]==1
    assert summary["facility_to_original_bus_identity_verified"] is False
    b=pd.read_csv(out)
    e=pd.read_csv(tmp_path/"trace_edges.csv")
    assert b.loc[0,"sub_id"]=="sub-alpha"
    assert b.loc[0,"line_count"]==1
    assert b.loc[0,"transformer_count"]==1
    assert set(e.edge_type)=={"line","transformer"}
    assert set(e.other_bus_sub_id)=={"sub-beta"}


def test_voltage_mismatch_rejected(tmp_path):
    grid,c=setup(tmp_path)
    d=pd.read_csv(c)
    d.loc[0,"candidate_bus_voltage_kv"]=345
    d.to_csv(c,index=False)
    with pytest.raises(ValueError,match="voltage inconsistent"):
        trace(grid,c,tmp_path/"trace.csv")


def test_self_approval_rejected(tmp_path):
    grid,c=setup(tmp_path)
    d=pd.read_csv(c)
    d.loc[0,"electrical_connection_verified"]=True
    d.to_csv(c,index=False)
    with pytest.raises(ValueError,match="cannot self-certify"):
        trace(grid,c,tmp_path/"trace.csv")
