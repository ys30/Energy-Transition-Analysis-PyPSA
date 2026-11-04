"""Fail-closed grading of public transmission evidence linked to 2024 EIA source plant IDs.

These classes are document claims, NOT authorized physical bus mappings.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ALLOWED={
 "named_project_and_interconnection_substation",
 "named_network_receipt_point_not_verified_generator_poi",
 "named_unit_receipt_voltage_not_high_voltage_poi",
}
EXPECTED={"63578":("Sagamore Wind",522.0,"2053003"),
          "56458":("Hobbs Generating Station",681.5,"2053003"),
          "2454":("Cunningham",444.2,"2053003")}

def check_manifest(data:dict)->dict:
    if data.get("schema_version")!=1:raise ValueError("Unsupported source ledger schema")
    rows=data.get("records")
    if not isinstance(rows,list) or len(rows)!=3:raise ValueError("Exactly three independently documented source plant records required")
    if {str(r.get("eia_plant_id")) for r in rows}!=set(EXPECTED):
        raise ValueError("Unexpected EIA source plant identity")
    for record in rows:
        pid=str(record["eia_plant_id"])
        name,mw,bus=EXPECTED[pid]
        if (record.get("eia_plant_name")!=name or
            abs(float(record.get("eia_nameplate_mw",0))-mw)>1e-6 or
            str(record.get("synthetic_candidate_bus"))!=bus):
            raise ValueError(f"EIA source identity and 2024 nameplate mismatch: {pid}")
        if record.get("evidence_type") not in ALLOWED:raise ValueError("Unreviewed transmission claim type")
        if not str(record.get("source_url","")).startswith("https://"):
            raise ValueError("Missing public source URL")
        if not str(record.get("source_document","")).strip() or not str(record.get("unresolved","")).strip():
            raise ValueError("Provenance and review gap must be explicit")
        if record.get("synthetic_bus_electrical_connection_verified") is not False:
            raise ValueError("No synthetic-grid bus electrical connection certified")
        if record.get("exact_eia_id_to_interconnection_request_verified") is not False:
            raise ValueError("EIA-to-interconnection ID must remain unverified")
        if record.get("underlying_eia_2024_nameplate_is_future_capacity") is not False:
            raise ValueError("Historic EIA nameplate not source-approved future capacity")
    ids={r["eia_plant_id"]:r for r in rows}
    if ids["63578"]["evidence_type"]!="named_project_and_interconnection_substation" or ids["63578"].get("external_voltage_kv")!=345.0:
        raise ValueError("Sagamore claim must remain 345 kV named substation evidence")
    if ids["56458"]["evidence_type"]!="named_network_receipt_point_not_verified_generator_poi" or ids["56458"].get("external_voltage_kv")!=230.0:
        raise ValueError("Hobbs entry is not a certified high-voltage POI")
    if ids["2454"]["evidence_type"]!="named_unit_receipt_voltage_not_high_voltage_poi" or sorted(ids["2454"].get("observed_unit_voltages_kv",[]))!=[13.8,20.0] or ids["2454"].get("external_voltage_kv") is not None:
        raise ValueError("Cunningham unit-side voltages must not be misread as a transmission POI")
    if data.get("verified_synthetic_bus_connections")!=0 or data.get("physical_2030_2050_western_opf_admitted") is not False:
        raise ValueError("Unsupported model admission")
    return {
      "source_year":2024,
      "documented_eia_plant_count":len(rows),
      "documented_2024_eia_nameplate_mw":sum(r["eia_nameplate_mw"] for r in rows),
      "source_evidence_classes":{r["eia_plant_id"]:r["evidence_type"] for r in rows},
      "named_interconnection_substation_evidence_count":1,
      "named_network_receipt_point_evidence_count":1,
      "unit_voltage_only_evidence_count":1,
      "synthetic_grid_bus_connections_verified":0,
      "electrically_admitted_generator_capacity_mw":0,
      "generator_fleet_2030_2050_verified":False,
      "full_western_opf_admitted":False,
      "note":"Classification is a provenance ledger over the named SPP sources. URLs do not establish a translation to the synthetic network buses."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=check_manifest(json.loads(a.manifest.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
