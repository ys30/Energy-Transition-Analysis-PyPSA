"""One source substation may have multiple buses; neither is an approved POI."""
import pandas as pd
import pytest
from energy_transition.eia860_source_substation_group_audit import audit


def fixtures(tmp_path):
    buses=tmp_path/"bus.csv"
    edges=tmp_path/"edges.csv"
    pd.DataFrame([
        {"plant_id":"6008","bus_id":"100","sub_id":"38478.0","candidate_voltage_kv":500,
         "x":-112.8,"y":33.3,"line_count":1,"transformer_count":1,
         "geographic_distance_km":0.03},
        {"plant_id":"6008","bus_id":"101","sub_id":"38511.0","candidate_voltage_kv":500,
         "x":-112.9,"y":33.4,"line_count":1,"transformer_count":0,
         "geographic_distance_km":4.8},
        {"plant_id":"6008","bus_id":"102","sub_id":"38511.0","candidate_voltage_kv":500,
         "x":-112.9,"y":33.4,"line_count":0,"transformer_count":0,
         "geographic_distance_km":4.8},
    ]).to_csv(buses,index=False)
    pd.DataFrame([
        {"plant_id":"6008","bus_id":"100","edge_type":"line","edge_id":"L1",
         "other_bus_id":"101","other_bus_sub_id":"38511.0"},
        {"plant_id":"6008","bus_id":"100","edge_type":"transformer","edge_id":"T1",
         "other_bus_id":"103","other_bus_sub_id":"38478.0"},
        {"plant_id":"6008","bus_id":"101","edge_type":"line","edge_id":"L1",
         "other_bus_id":"100","other_bus_sub_id":"38478.0"}
    ]).to_csv(edges,index=False)
    return buses,edges


def test_groups_preserve_source_identity_and_no_approval(tmp_path):
    buses,edges=fixtures(tmp_path)
    out=tmp_path/"out"
    summary=audit(buses,edges,out)
    groups=pd.read_csv(out/"palo_verde_source_substation_groups.csv")
    assert summary["unique_source_substation_ids"]==2
    assert summary["source_substations_with_multiple_bus_records"]==1
    assert summary["candidate_bus_count"]==3
    assert summary["total_incident_records"]==3
    assert summary["same_substation_incident_records"]==1
    assert summary["generator_injections_approved"]==0
    assert groups.set_index("source_sub_id").loc[38511,"bus_count"]==2
    assert groups.set_index("source_sub_id").loc[38511,"unique_coordinate_pairs"]==1
    assert not groups.independently_verified_facility_identity.any()


def test_incorrect_branch_count_blocks_audit(tmp_path):
    buses,edges=fixtures(tmp_path)
    b=pd.read_csv(buses)
    b.loc[0,"line_count"]=99
    b.to_csv(buses,index=False)
    with pytest.raises(ValueError,match="incidence count mismatch"):
        audit(buses,edges,tmp_path/"out")
