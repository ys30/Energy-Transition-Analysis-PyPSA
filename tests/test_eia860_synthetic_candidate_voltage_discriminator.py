import copy
import json
from pathlib import Path
import pytest
from energy_transition.eia860_synthetic_candidate_voltage_discriminator import audit

ROOT=Path(__file__).resolve().parents[1]

def fixture():
    e=json.loads((ROOT/"data/eia860_top3_official_transmission_evidence.json").read_text())
    p=json.loads((ROOT/"docs/western_source_network_provenance.json").read_text())
    return e,p

def test_evidence_only_voltage_discriminator():
    e,p=fixture()
    r=audit(e,p)
    assert r["documented_plant_count"]==3
    assert r["historic_nameplate_reviewed_mw"]==pytest.approx(1647.7)
    assert r["named_high_voltage_comparisons_with_mismatch"]==2
    assert r["unit_voltage_noncomparable_count"]==1
    assert not r["real_western_OPF_admitted"]
    assert r["approved_generator_injection_mw"]==0

def test_refuse_approved_poi_claim():
    e,p=fixture()
    p["eia860_electrical_interconnection_approved"]=True
    with pytest.raises(ValueError,match="Unsupported"):
        audit(e,p)

def test_refuse_bus_misattribution():
    e,p=fixture()
    e["records"][0]["synthetic_candidate_bus"]="2053000"
    with pytest.raises(ValueError):
        audit(e,p)
