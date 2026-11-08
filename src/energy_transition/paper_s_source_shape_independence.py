"""Detect non-independent source demand shapes among preregistered zones.

Uses 0h flat-profile demand values exported from successfully matched hourly LPs.
No assumption that equal normalized shapes represent independent replications.
"""
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd

def compare(traces):
    series={}
    for rank,df in traces.items():
        g=df[(df.synthetic_supply_shape=="flat_50pct")&(df.battery_duration_h==0)].sort_values("local_hour_id")
        if len(g)!=8760 or not np.array_equal(g.local_hour_id.to_numpy(),np.arange(1,8761)):
            raise ValueError("Incorrect original 8760-hour source sequence")
        if g[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1:
            raise ValueError("Invalid source zone identity")
        y=g.demand_mwh.to_numpy(dtype=float)
        if not np.isfinite(y).all() or y.max()<=0 or (y<0).any():
            raise ValueError("Invalid original source load profile")
        series[rank]={"y":y,"year":int(g.planning_year.iloc[0]),
                      "state":str(g.state.iloc[0]),"zone":str(g.reeds_zone.iloc[0])}
    if set(series)!={0,9,18}:raise ValueError("Expected exactly ranks 0,9,18")
    records=[]
    for a,b in combinations(sorted(series),2):
        x,y=series[a]["y"],series[b]["y"]
        normalized_x=x/x.max();normalized_y=y/y.max()
        diff=np.abs(normalized_x-normalized_y)
        correlation=float(np.corrcoef(normalized_x,normalized_y)[0,1]) if np.std(normalized_x)>1e-12 and np.std(normalized_y)>1e-12 else None
        scale=float(y.max()/x.max())
        original_error=np.max(np.abs(y-scale*x))
        records.append({"rank_a":a,"rank_b":b,
                        "source_a":series[a]["state"]+" "+series[a]["zone"],
                        "source_b":series[b]["state"]+" "+series[b]["zone"],
                        "relative_peak_scale_b_over_a":scale,
                        "max_normalized_demand_absolute_difference":float(diff.max()),
                        "mean_normalized_demand_absolute_difference":float(diff.mean()),
                        "max_mw_error_after_scalar_rescaling":float(original_error),
                        "pearson_normalized_hourly_demand":correlation,
                        "normalized_profiles_equal_within_1e_10":bool(diff.max()<1e-10)})
    return pd.DataFrame(records)

def main():
    p=argparse.ArgumentParser()
    for rank in (0,9,18):p.add_argument(f"--trace-rank-{rank}",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    inputs={rank:pd.read_csv(getattr(a,f"trace_rank_{rank}"),compression="infer") for rank in (0,9,18)}
    frame=compare(inputs)
    out=a.out_dir;out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/"paper_s_cross_zone_source_shape_independence.csv",index=False,float_format="%.14g")
    report={"status":"CROSS_ZONE_SOURCE_SHAPE_INDEPENDENCE_AUDIT",
            "zones":3,"zone_pairs":len(frame),"equal_normalized_pairs":int(frame.normalized_profiles_equal_within_1e_10.sum()),
            "strict_threshold":1e-10,"hour_axis":"ordinal source LocalHourID, not physical UTC",
            "replications_independent_by_default":False}
    (out/"paper_s_cross_zone_source_shape_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(frame.to_string(index=False))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
