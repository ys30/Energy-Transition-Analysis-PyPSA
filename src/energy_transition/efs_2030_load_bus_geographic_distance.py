"""Quantify geographic source-coordinate sensitivity of verified 2030 EFS bus-placement rules.

Distances are haversine between synthetic archived bus coordinates. They are
not transmission line lengths, actual relocation, POIs or network dispatch.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def haversine_km(lat0,lon0,lat1,lon1):
    a,b,c,d=map(np.radians,[lat0,lon0,lat1,lon1])
    z=np.sin((c-a)/2.)**2+np.cos(a)*np.cos(c)*np.sin((d-b)/2.)**2
    return 6371.0088*2*np.arcsin(np.sqrt(np.clip(z,0,1)))

def geographic_sensitivity(buses:pd.DataFrame,source:pd.DataFrame):
    need={"Load_id","original_first_bus_id","single_largest_positive_pd_connected_bus_id",
      "candidate_eligible_bus_count","original_zone_annual_mwh",
      "single_bus_source_candidate_changed","multibus_share_changed"}
    if need-set(source):raise ValueError("Incomplete saved source placement schema")
    if not {"x","y"}.issubset(buses):raise ValueError("No original bus coordinates")
    d=source.copy()
    if len(d)!=20 or d.Load_id.duplicated().any():raise ValueError("Unexpected original Load cohort")
    coords=buses[["x","y"]].copy()
    coords.index=coords.index.astype(str)
    if coords.index.duplicated().any():raise ValueError("Duplicate original source bus")
    for col in ["x","y"]:coords[col]=pd.to_numeric(coords[col],errors="coerce")
    if not np.isfinite(coords[["x","y"]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid archived source bus coordinates")
    if not coords.x.between(-180,180).all() or not coords.y.between(-90,90).all():
        raise ValueError("Out-of-bounds original source coordinates")
    result=[]
    for row in d.itertuples(index=False):
        old=str(row.original_first_bus_id)
        top=str(row.single_largest_positive_pd_connected_bus_id)
        if old not in coords.index or top not in coords.index:raise ValueError("Chosen source ID not in real archived topology")
        original=coords.loc[old];single=coords.loc[top]
        distance=float(haversine_km(original.y,original.x,single.y,single.x))
        annual=float(row.original_zone_annual_mwh)
        if not np.isfinite(annual) or annual<0:raise ValueError("Negative or nonfinite source demand")
        changed=str(row.single_bus_source_candidate_changed).lower()=="true"
        if changed!=(old!=top):raise ValueError("Original single-bus change flag mismatch")
        result.append({
          "Load_id":str(row.Load_id),
          "original_bus_id":old,
          "single_max_pd_candidate_bus_id":top,
          "first_bus_lat":float(original.y),"first_bus_lon":float(original.x),
          "max_pd_bus_lat":float(single.y),"max_pd_bus_lon":float(single.x),
          "single_bus_straight_line_coordinate_distance_km":distance,
          "original_annual_mwh":annual,
          "candidate_id_changed":changed,
          "source_location_utility_certified":False,
        })
    out=pd.DataFrame(result)
    total=out.original_annual_mwh.sum()
    if total<=0:raise ValueError("Original source annual EFS demand is zero")
    weighted=float((out.single_bus_straight_line_coordinate_distance_km*out.original_annual_mwh).sum()/total)
    positive=out.loc[out.original_annual_mwh.gt(0)]
    rep={
      "original_source_zone_count":len(out),
      "original_source_annual_load_mwh":float(total),
      "source_bus_coordinate_method":"haversine straight-line distance between original synthetic bus coordinates",
      "zones_changing_single_max_pd_bus_id":int(out.candidate_id_changed.sum()),
      "nonzero_annual_load_zones":len(positive),
      "nonzero_load_zones_changing_bus_id":int(positive.candidate_id_changed.sum()),
      "single_max_pd_geodesic_distance_km_median_all_zones":float(out.single_bus_straight_line_coordinate_distance_km.median()),
      "single_max_pd_geodesic_distance_km_max":float(out.single_bus_straight_line_coordinate_distance_km.max()),
      "single_max_pd_geodesic_distance_km_load_weighted_mean":weighted,
      "single_max_pd_geodesic_distance_km_p90_nonzero_load_zones":float(positive.single_bus_straight_line_coordinate_distance_km.quantile(0.9)),
      "real_grid_branch_path_lengths_measured":False,
      "utility_points_of_delivery_certified":False,
      "original_EFS_load_network_modified":False,
      "historical_generator_POI_approved":False,
      "future_Western_OPF_solved":False,
      "note":"Distance between candidate synthetic bus coordinates only; not real load movement, path distance, power-flow impact or a superior validated placement.",
    }
    return out,rep

def main():
    import pypsa
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True,type=Path)
    ap.add_argument("--placement",required=True,type=Path)
    ap.add_argument("--outdir",required=True,type=Path)
    a=ap.parse_args()
    n=pypsa.Network(str(a.base))
    source=pd.read_csv(a.placement,dtype={"original_first_bus_id":"string","single_largest_positive_pd_connected_bus_id":"string"})
    out,r=geographic_sensitivity(n.buses,source)
    a.outdir.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.outdir/"efs_2030_single_max_pd_geographic_bus_distance.csv",index=False)
    (a.outdir/"efs_2030_single_max_pd_geographic_bus_summary.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
    print(out.sort_values("single_bus_straight_line_coordinate_distance_km",ascending=False).head(10).to_string(index=False))
if __name__=="__main__":main()
