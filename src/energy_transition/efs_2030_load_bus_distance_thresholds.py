"""Summarize the already CI-verified first-bus versus max-Pd candidate geodesic results.

Counts source zones and source annual EFS load beyond distance thresholds.
Numbers are hypothetical placement *sensitivity*, not physical relocation,
transmission line distance, real utility topology or OPF.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

THRESHOLDS_KM=(25,50,100,200,300,400,500)

def summarize(source:pd.DataFrame):
    cols={"Load_id","original_bus_id","single_max_pd_candidate_bus_id",
          "single_bus_straight_line_coordinate_distance_km",
          "original_annual_mwh","candidate_id_changed"}
    if cols-set(source.columns):
        raise ValueError("Original 20-zone source-distance columns unavailable")
    d=source.copy()
    if len(d)!=20 or d.Load_id.duplicated().any():
        raise ValueError("Missing or duplicate original EFS zone records")
    for key in ("original_annual_mwh","single_bus_straight_line_coordinate_distance_km"):
        d[key]=pd.to_numeric(d[key],errors="coerce")
        if not np.isfinite(d[key].to_numpy(dtype=float)).all() or (d[key]<0).any():
            raise ValueError("Nonfinite or negative source distance/energy")
    flag=d.candidate_id_changed.astype("string").str.lower()
    if not flag.isin(["true","false"]).all():
        raise ValueError("Unrecognized source change flag")
    actual=d.original_bus_id.astype("string").ne(d.single_max_pd_candidate_bus_id.astype("string"))
    if not flag.eq(actual.astype("string").str.lower()).all():
        raise ValueError("Source candidate ID-change flags inconsistent")
    total=float(d.original_annual_mwh.sum())
    if not np.isclose(total,274706987.114121,atol=0.05,rtol=0):
        raise ValueError("Unrecognized EFS seven-state 2030 annual source demand")
    detail=[]
    for threshold in THRESHOLDS_KM:
        subset=d[d.single_bus_straight_line_coordinate_distance_km.gt(threshold)]
        mwh=float(subset.original_annual_mwh.sum())
        detail.append({"distance_threshold_km_strictly_greater":threshold,
            "source_zones_above_threshold":int(len(subset)),
            "positive_source_zones_above_threshold":int(subset.original_annual_mwh.gt(0).sum()),
            "annual_source_efs_load_mwh_in_zones_above_threshold":mwh,
            "fraction_of_total_source_efs_annual_load":mwh/total})
    distance=d.single_bus_straight_line_coordinate_distance_km
    d["expected_exported_state"]=d.Load_id.astype(str).str.rsplit("_",n=1).str[-1]
    ranked=d.sort_values(["single_bus_straight_line_coordinate_distance_km","original_annual_mwh"],
                         ascending=[False,False]).reset_index(drop=True)
    result={
      "source_planning_year":2030,
      "original_source_load_zone_count":20,
      "original_source_annual_load_mwh":total,
      "positive_source_load_zone_count":int(d.original_annual_mwh.gt(0).sum()),
      "strict_threshold_summary":detail,
      "median_source_candidate_geodesic_km":float(distance.median()),
      "source_load_weighted_mean_geodesic_km":float(np.average(distance,weights=d.original_annual_mwh)),
      "top_three_source_distances":ranked[["Load_id","original_bus_id","single_max_pd_candidate_bus_id",
          "single_bus_straight_line_coordinate_distance_km"]].head(3).to_dict("records"),
      "real_transmission_path_measured":False,
      "official_zone_polygon_placement_certified":False,
      "original_load_network_modified":False,
      "physically_validated_bus_loads_created":False,
      "full_western_opf_solved":False,
      "note":"The thresholds measure distance between two synthetic original bus coordinate candidates, weighted by original zonal MWh. They are NOT movement of real load or real network distance.",
    }
    return ranked, result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--distance-archive",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    source=pd.read_csv(a.distance_archive,dtype={"original_bus_id":"string","single_max_pd_candidate_bus_id":"string"})
    ranked,report=summarize(source)
    a.outdir.mkdir(parents=True,exist_ok=True)
    ranked.to_csv(a.outdir/"efs_2030_20_zone_bus_distance_priority_queue.csv",index=False)
    (a.outdir/"efs_2030_bus_distance_threshold_exposure.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
