"""Group exact normalized source-hour demand shapes, excluding zero-demand zones.

This audits source EFS/LAF zonal data only; no synthetic dispatch is involved.
A group indicates identical peak-normalized hour sequences, not equivalent
real geography, weather, costs, transmission, or independent replication.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def audit_shapes(source, years=(2030,2040,2050), hours=8760, expected_zones=20, atol=1e-10):
    req={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if not req.issubset(source):raise ValueError("Missing zonal source columns")
    if source[list(req)].isna().any().any():raise ValueError("Null source inputs")
    if source.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Duplicate original zone-hour")
    if set(source.year)!=set(years):raise ValueError("Unexpected source year population")
    output=[];summary=[]
    for year in years:
        groups=[]
        for (state,zone),g in source.loc[source.year==year].groupby(["state","reeds_zone"]):
            g=g.sort_values("local_hour_id")
            if not np.array_equal(g.local_hour_id.to_numpy(),np.arange(1,hours+1)):
                raise ValueError("Incomplete source-hour sequence")
            load=g.allocated_mw.to_numpy(dtype=float)
            if not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid source hourly demand")
            peak=float(load.max())
            groups.append((str(state),str(zone),float(load.sum()),peak,
                           load/peak if peak>0 else np.zeros(hours)))
        if len(groups)!=expected_zones:raise ValueError("Unexpected source zone population")
        groups.sort(key=lambda z:(z[0],z[1]))
        representatives=[];sizes={}
        counts={"positive":0,"zero":0}
        for state,zone,total,peak,profile in groups:
            zero=peak==0
            counts["zero" if zero else "positive"]+=1
            match=None
            if not zero:
                for rid,ref in enumerate(representatives):
                    if np.max(np.abs(profile-ref)) <= atol:
                        match=rid
                        break
                if match is None:
                    match=len(representatives)
                    representatives.append(profile)
            group_id=("zero_source" if zero else f"normalized_shape_{match+1:02d}")
            sizes[group_id]=sizes.get(group_id,0)+1
            output.append({"planning_year":int(year),"state":state,"reeds_zone":zone,
                           "source_demand_mwh":total,"source_peak_mw":peak,
                           "normalized_shape_group":group_id,
                           "source_zero_demand":bool(zero)})
        summary.append({"planning_year":int(year),"total_zones":len(groups),
                        "positive_source_zones":counts["positive"],
                        "zero_demand_zones":counts["zero"],
                        "unique_positive_normalized_shapes":len(representatives),
                        "positive_zones_in_duplicated_shape_groups":sum(
                            count for key,count in sizes.items()
                            if key!="zero_source" and count>1),
                        "duplicate_positive_shape_groups":sum(
                            1 for key,count in sizes.items()
                            if key!="zero_source" and count>1)})
    assigned=pd.DataFrame(output).sort_values(["planning_year","state","reeds_zone"]).reset_index(drop=True)
    s=pd.DataFrame(summary)
    return assigned,s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    z,s=audit_shapes(pd.read_csv(a.source,compression="infer"))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    z.to_csv(a.out_dir/"efs_source_normalized_shape_groups.csv",index=False)
    s.to_csv(a.out_dir/"efs_source_normalized_shape_group_summary.csv",index=False)
    manifest={"status":"ALL_20_SOURCE_ZONES_3_YEAR_NORMALIZED_SHAPE_AUDIT_PASS",
              "source_hours_per_zone_year":8760,
              "group_rule":"peak-normalized sequence max absolute difference <= 1e-10, never crosses year",
              "years":[2030,2040,2050],
              "zero_source_separate":True,"utc_clock_certified":False,
              "not_independent_temporal_replication":True}
    (a.out_dir/"efs_source_normalized_shape_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(s.to_string(index=False))
    for year,g in z.groupby("planning_year"):
        print("SOURCE_SHAPE_GROUPS_YEAR",year)
        for label,gg in g.groupby("normalized_shape_group"):
            print(label,":",",".join(gg.state+" "+gg.reeds_zone))
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
