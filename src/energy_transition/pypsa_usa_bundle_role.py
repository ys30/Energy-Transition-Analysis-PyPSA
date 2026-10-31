"""Classify downloaded PyPSA-USA support bundles without confusing GIS with grid physics."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

NETWORK_EXTENSIONS={".raw",".sav",".m",".mdb",".accdb"}
GEOSPATIAL_EXTENSIONS={".tif",".tiff",".gpkg",".shp",".shx",".dbf",".prj",".cpg",".nc"}

def classify_inventory(data:dict)->dict:
    files=data.get("files",[])
    if not isinstance(files,list) or not files:
        raise ValueError("Empty or invalid archive inventory")
    by_ext={}
    for item in files:
        ext=str(item.get("extension","")).lower()
        by_ext[ext]=by_ext.get(ext,0)+1
    candidates=[f["name"] for f in files if f.get("extension") in NETWORK_EXTENSIONS]
    spatial=[f["name"] for f in files if f.get("extension") in GEOSPATIAL_EXTENSIONS]
    # A .csv could be a bus/branch table, but cannot be certified from its suffix.
    csv=[f["name"] for f in files if f.get("extension")==".csv"]
    return {"archive":data.get("archive"),"member_count":len(files),
            "extension_counts":by_ext,"geospatial_member_count":len(spatial),
            "possible_network_model_members":candidates,"ambiguous_csv_members":csv,
            "network_model_verified":False,"network_case_solved":False,
            "decision":"inspect_upstream_build_base_network" if not candidates and not csv else "manual_schema_inspection_required",
            "warning":"Inventory-only identification; actual topology and electrical metadata unverified"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=classify_inventory(json.loads(a.inventory.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
