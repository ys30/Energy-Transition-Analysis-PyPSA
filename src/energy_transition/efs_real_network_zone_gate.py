"""Check whether a real EFS allocation crosswalk matches actual built-network zones.

A bus crosswalk is an allowed-zone list only; never normalize bus counts
into demand factors. Numerical weights are admitted only from an external
provenance-checked LAF file.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def validate(bus_crosswalk: Path, weights: Path) -> dict:
    with bus_crosswalk.open(newline="", encoding="utf-8") as f:
        buses = list(csv.DictReader(f))
    if not buses or not {"state","reeds_zone","bus_count"}.issubset(buses[0]):
        raise ValueError("Invalid real-network crosswalk")
    allowed = {(r["state"],r["reeds_zone"]) for r in buses}
    with weights.open(newline="",encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows or not {"state","reeds_zone","weight"}.issubset(rows[0]):
        raise ValueError("Missing EFS LAF columns")
    missing = sorted({(r["state"],r["reeds_zone"]) for r in rows} - allowed)
    if missing:
        raise ValueError(f"LAF includes zones absent from real network: {missing}")
    zone_total=defaultdict(float)
    pairs=set()
    for r in rows:
        k=(r["state"],r["reeds_zone"])
        if k in pairs: raise ValueError(f"Duplicate allocation zone: {k}")
        pairs.add(k)
        weight=float(r["weight"])
        if not 0 <= weight <= 1: raise ValueError("Invalid LAF share")
        zone_total[r["state"]]+=weight
    excess={s:v for s,v in zone_total.items() if v>1.000001}
    if excess: raise ValueError(f"Overallocation: {excess}")
    return {"real_bus_zone_pairs":len(allowed),"laf_pairs_checked":len(pairs),
            "state_weight_sums":dict(zone_total),
            "all_laf_zones_in_real_network":True,
            "empirical_laf_provenance_confirmed":False,
            "hourly_efs_attached":False}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--bus-crosswalk",type=Path,required=True)
    p.add_argument("--weights",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=validate(a.bus_crosswalk,a.weights)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
