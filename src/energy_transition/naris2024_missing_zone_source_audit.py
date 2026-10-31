"""Audit upstream NARIS AC and non-AC evidence for missing Western zones.

Absence of a row does not prove physical isolation in the real power system.
"""
from __future__ import annotations
import argparse,csv,io,json
from pathlib import Path
from urllib.request import urlopen

BASE="https://raw.githubusercontent.com/PyPSA/pypsa-usa/master/workflow/repo_data/ReEDS_Constraints/transmission/"
SOURCES={"ac":"transmission_capacity_init_AC_ba_NARIS2024.csv",
         "non_ac":"transmission_capacity_init_nonAC_ba.csv"}

def audit_zone(zone:str, datasets:dict[str,bytes])->dict:
    if not zone: raise ValueError("Empty zone identifier")
    matches={}
    for kind,data in datasets.items():
        rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        if not rows or not {"r","rr"}.issubset(rows[0]): raise ValueError("Unexpected interface schema")
        matches[kind]=[r for r in rows if zone in (r["r"].strip(),r["rr"].strip())]
    return {"zone":zone,"matched_interface_rows":{k:len(v) for k,v in matches.items()},
            "interface_record_found":any(matches.values()),
            "interpretation":"No record in these published source tables does not prove historical physical isolation",
            "allow_invented_link":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zone",default="p19")
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    datasets={}
    for kind,path in SOURCES.items():
        with urlopen(BASE+path,timeout=40) as response: datasets[kind]=response.read(2_000_001)
        if len(datasets[kind])>2_000_000:raise ValueError("Source exceeds bound")
    report=audit_zone(a.zone,datasets)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
