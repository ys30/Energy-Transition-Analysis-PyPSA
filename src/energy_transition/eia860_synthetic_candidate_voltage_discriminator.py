"""Evidence-graduated EIA-860 source facility vs synthetic bus compatibility screening.

Never treat voltage matching, shared names, or nearest geospatial bus IDs as
authenticated interconnection. This consumes a reviewed 2024 source ledger.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .eia860_spptop3_poi_evidence_gate import check_manifest

CANDIDATE_BUS = "2053003"
CANDIDATE_NOMINAL_KV = 115.0
PLANT_IDS = {"63578", "56458", "2454"}

def audit(evidence: dict, network_metadata: dict) -> dict:
    base = check_manifest(evidence)
    if network_metadata.get("source_bus_id_meaning") != "synthetic_source_model_bus_id":
        raise ValueError("Unknown bus provenance; cannot admit electrical POI")
    if network_metadata.get("utility_authenticated_electrical_facility_identities") is not False:
        raise ValueError("Unexpected source network facility authentication claim")
    if network_metadata.get("eia860_electrical_interconnection_approved") is not False:
        raise ValueError("Unsupported electrical connection approval")
    rows = []
    for e in sorted(evidence["records"], key=lambda x: str(x["eia_plant_id"])):
        if str(e["eia_plant_id"]) not in PLANT_IDS or str(e["synthetic_candidate_bus"]) != CANDIDATE_BUS:
            raise ValueError("Unexpected geographic candidate bus")
        external = e.get("external_voltage_kv")
        if external is None:
            voltage_class = "unit_side_voltage_not_comparable_to_high_voltage_bus"
            direct_match = None
        else:
            voltage_class = ("different_nominal_voltage" if float(external) != CANDIDATE_NOMINAL_KV
                             else "same_nominal_voltage_not_poi_proof")
            direct_match = bool(float(external) == CANDIDATE_NOMINAL_KV)
        rows.append({
            "eia_plant_id": str(e["eia_plant_id"]),
            "plant_name": e["eia_plant_name"],
            "historic_2024_nameplate_mw": e["eia_nameplate_mw"],
            "synthetic_candidate_bus": CANDIDATE_BUS,
            "archived_candidate_bus_v_nom_kv": CANDIDATE_NOMINAL_KV,
            "external_evidence_voltage_kv": external,
            "comparison_class": voltage_class,
            "same_nominal_voltage": direct_match,
            "external_evidence_type": e["evidence_type"],
            "exact_eia_to_external_interconnection_id_verified": False,
            "facility_to_synthetic_bus_equivalence_verified": False,
            "physical_generator_connection_admitted": False,
        })
    return {
        "status": "EVIDENCE_ONLY_NO_ELECTRICAL_BUS_ADMISSION",
        "source_network": network_metadata["source_network_family"],
        "plant_records": rows,
        "historic_nameplate_reviewed_mw": base["documented_2024_eia_nameplate_mw"],
        "documented_plant_count": len(rows),
        "named_high_voltage_comparisons_with_mismatch": sum(r["comparison_class"] == "different_nominal_voltage" for r in rows),
        "unit_voltage_noncomparable_count": sum(r["comparison_class"].startswith("unit_side") for r in rows),
        "verified_utility_POI_to_synthetic_bus_connections": 0,
        "approved_generator_injection_mw": 0,
        "real_western_OPF_admitted": False,
        "limitations": [
            "115 kV candidate voltage is from archived synthetic source bus 2053003, not a utility-certified station",
            "Reported 345 kV/230 kV named source facility evidence is not proof that a stepped-down 115 kV bus cannot be connected",
            "Cunningham 13.8/20 kV unit-side voltages cannot be compared as a high-voltage point-of-interconnection",
            "All 2024 nameplate values are historical source inventory, not approved future fleet capacity"
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--network-metadata",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(json.loads(a.evidence.read_text()),json.loads(a.network_metadata.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__ == "__main__": main()
