import copy
import json
from pathlib import Path
import pytest
from energy_transition.eia860_spptop3_poi_evidence_gate import check_manifest

ROOT=Path(__file__).resolve().parents[1]
def original():
    return json.loads((ROOT/"data/eia860_top3_official_transmission_evidence.json").read_text())

def test_original_transmission_evidence_is_not_generator_bus_approval():
    out=check_manifest(original())
    assert out["documented_eia_plant_count"]==3
    assert out["documented_2024_eia_nameplate_mw"]==pytest.approx(1647.7)
    assert out["named_interconnection_substation_evidence_count"]==1
    assert out["unit_voltage_only_evidence_count"]==1
    assert out["synthetic_grid_bus_connections_verified"]==0
    assert not out["full_western_opf_admitted"]

def test_claiming_real_bus_mapping_fails():
    x=original()
    x["records"][0]["synthetic_bus_electrical_connection_verified"]=True
    with pytest.raises(ValueError,match="No synthetic-grid"):
        check_manifest(x)

def test_cunningham_low_voltage_is_not_promoted():
    x=original()
    x["records"][2]["external_voltage_kv"]=115.0
    with pytest.raises(ValueError,match="Cunningham"):
        check_manifest(x)

def test_historical_capacity_cannot_be_future_capacity():
    x=original()
    x["records"][1]["underlying_eia_2024_nameplate_is_future_capacity"]=True
    with pytest.raises(ValueError,match="Historic"):
        check_manifest(x)

def test_unmatched_eia_plant_id_rejected():
    x=original()
    x["records"][0]["eia_plant_id"]="99999"
    with pytest.raises(ValueError,match="source plant identity"):
        check_manifest(x)
