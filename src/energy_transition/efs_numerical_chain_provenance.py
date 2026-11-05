"""Emit immutable input hashes and admission gates for the verified EFS numerical chain."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return {"sha256":h.hexdigest(),"bytes":Path(path).stat().st_size}

def report(inputs, source_report, archive_report):
    a=json.loads(Path(source_report).read_text())
    b=json.loads(Path(archive_report).read_text())
    if a.get("status")!="SOURCE_STATE_TO_LAF_ZONE_HOURLY_MATCH":
        raise ValueError("State-to-zone hourly source gate not passed")
    if b.get("status")!="EXACT_ZONAL_TO_ARCHIVE_MW_MATCH":
        raise ValueError("Zonal-to-archive hourly gate not passed")
    if a["mismatched_zonal_hour_values"]!=0:
        raise ValueError("Zonal hourly mismatch")
    years=sorted(int(x["year"]) for x in b["year_results"])
    if years!=[2030,2040,2050]:
        raise ValueError("Missing planning year")
    if any(x["hourly_mw_mismatches"]!=0 for x in b["year_results"]):
        raise ValueError("Archive hourly MW mismatches")
    if a["joint_utc_dispatch_admitted"] or b["actual_Western_OPF_admitted"]:
        raise ValueError("Unsafe physical admission flag")
    return {
        "status":"NUMERICAL_CHAIN_VERIFIED_PHYSICAL_ADMISSION_BLOCKED",
        "input_artifacts":{key:digest(p) for key,p in inputs.items()},
        "state_to_zonal_comparisons":a["zonal_hour_rows_compared"],
        "zone_to_netcdf_comparisons":sum(x["hourly_load_values_compared"] for x in b["year_results"]),
        "all_years":[2030,2040,2050],
        "utc_provenance_certified":False,
        "generator_weather_join_admitted":False,
        "full_western_physical_opf_admitted":False,
        "note":"SHA256 identifies exact inputs; data semantics and generator/branch provenance remain unverified."
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("source","zonal","network","net2030","net2040","net2050",
                 "source-report","archive-report","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    r=report({name:getattr(a,name) for name in ("source","zonal","network","net2030","net2040","net2050")},
             a.source_report,a.archive_report)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))

if __name__=="__main__":
    main()
