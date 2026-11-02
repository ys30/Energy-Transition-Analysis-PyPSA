import pandas as pd
from energy_transition.electrical_interconnection_evidence_gate import audit, REQUIRED

def test_nearest_bus_not_admitted(tmp_path):
    evidence={k:"" for k in REQUIRED}
    evidence.update(plant_id="66183",generator_id="CWE",network_bus_id="123",
      substation_id="example",connection_voltage_kv="230",
      source_document_url="https://example.org/unverified",
      source_document_year="2024",source_network_bus_evidence="nearest neighbor",
      evidence_type="geographic_nearest_bus",review_status="independently_verified")
    f=tmp_path/"e.csv";pd.DataFrame([evidence]).to_csv(f,index=False)
    r=audit(f,tmp_path/"report.json")
    assert r["verified_unique_generator_bus_keys"]==0
    assert r["automated_approval_of_empirical_dispatch"] is False

def test_missing_document_rejected(tmp_path):
    e={k:"x" for k in REQUIRED}
    e.update(plant_id="66183",generator_id="CWE",network_bus_id="123",substation_id="station",
      connection_voltage_kv="230",source_document_url="",
      source_document_year="2024",source_network_bus_evidence="claimed",
      evidence_type="official_interconnection_agreement",review_status="independently_verified")
    f=tmp_path/"e.csv";pd.DataFrame([e]).to_csv(f,index=False)
    r=audit(f,tmp_path/"report.json")
    assert r["rejected_rows"]==1
