"""Create an evidence-first review queue for BPAT-mapped wind plants.

The EIA-860 annual BA crosswalk is not independent proof of EIA-930
operational dispatch attribution. Unknown attribution stays unknown.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def review_queue(plant_totals: pd.DataFrame) -> pd.DataFrame:
    needed={"plant_id","ba_code","net_generation_mwh"}
    if needed-set(plant_totals.columns):
        raise ValueError("Missing reconciliation plant totals")
    p=plant_totals.loc[plant_totals.ba_code.eq("BPAT")].copy()
    if p.empty or p.plant_id.duplicated().any():
        raise ValueError("Missing or duplicate BPAT wind plants")
    p["net_generation_mwh"]=pd.to_numeric(p.net_generation_mwh,errors="raise")
    if not p.net_generation_mwh.notna().all():
        raise ValueError("Missing source generation")
    p=p.sort_values("net_generation_mwh",ascending=False).reset_index(drop=True)
    p["priority_rank"]=range(1,len(p)+1)
    total=float(p.net_generation_mwh.sum())
    if not total>0:
        raise ValueError("BPAT plant generation total must be positive for prioritization")
    p["share_of_mapped_bpat_wind"]=p.net_generation_mwh/total
    p["cumulative_share_of_mapped_bpat_wind"]=p.net_generation_mwh.cumsum()/total
    p["review_tier"]=["first_5" if n<=5 else "next_5" if n<=10 else "remaining" for n in p.priority_rank]
    p["annual_ba_mapping"]="BPAT"
    p["eia930_operational_ba_verified"]=False
    p["independent_source_required"]=True
    p["eia930_plant_specific_generation_mwh"]=pd.NA
    p["status"]="unresolved_operational_attribution"
    return p[["priority_rank","review_tier","plant_id","net_generation_mwh",
              "share_of_mapped_bpat_wind","cumulative_share_of_mapped_bpat_wind","annual_ba_mapping",
              "eia930_operational_ba_verified","independent_source_required",
              "eia930_plant_specific_generation_mwh","status"]]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plant-totals",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    queue=review_queue(pd.read_csv(a.plant_totals,dtype={"plant_id":"string"}))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    queue.to_csv(a.output,index=False)
    print(f"BPAT plants requiring independent operating-BA attribution: {len(queue)}")


if __name__=="__main__":
    main()
