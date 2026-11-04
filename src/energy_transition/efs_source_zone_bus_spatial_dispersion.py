"""Compare archived EFS representative buses to their entire source-labelled zone geography.

This is a within-source-region consistency/dispersion check, NOT a ReEDS
polygon overlay, verified delivery-point mapping, or an OPF study.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

import numpy as np
import pandas as pd

def _haversine(lat,lon,others_lat,others_lon):
    lat0,lon0=np.radians(float(lat)),np.radians(float(lon))
    lat1,lon1=np.radians(others_lat),np.radians(others_lon)
    a=np.sin((lat1-lat0)/2)**2+np.cos(lat0)*np.cos(lat1)*np.sin((lon1-lon0)/2)**2
    return 12742.0176*np.arcsin(np.sqrt(np.clip(a,0,1)))

def audit(buses,selected):
    required={"state","reeds_zone","x","y","Pd"}
    if required-set(buses.columns):raise ValueError("Original bus zone identity or coordinate missing")
    fields={"Load_id","original_first_bus_id","single_largest_positive_pd_connected_bus_id",
            "original_zone_annual_mwh"}
    if fields-set(selected.columns):raise ValueError("Missing saved candidate comparison columns")
    if len(selected)!=20 or selected.Load_id.duplicated().any():raise ValueError("Expected 20 archived Load IDs")
    b=buses.copy()
    b.index=b.index.astype(str)
    if b.index.duplicated().any():raise ValueError("Duplicate archived source bus IDs")
    for key in ("x","y"):
        b[key]=pd.to_numeric(b[key],errors="coerce")
        if b[key].isna().any() or not np.isfinite(b[key].to_numpy()).all():raise ValueError("Nonfinite source coordinates")
    if not b.x.between(-180,180).all() or not b.y.between(-90,90).all():
        raise ValueError("Source coordinate domain violated")
    records=[]
    for r in selected.itertuples(index=False):
        old=str(r.original_first_bus_id)
        new=str(r.single_largest_positive_pd_connected_bus_id)
        if old not in b.index or new not in b.index:raise ValueError("Candidate source ID not found")
        s=b.loc[old]
        n=b.loc[new]
        if s.state!=n.state or s.reeds_zone!=n.reeds_zone:
            raise ValueError("Candidate original source zone keys disagree")
        zone=b.loc[b.state.eq(s.state)&b.reeds_zone.eq(s.reeds_zone)]
        if len(zone)<2:raise ValueError("Source spatial region unexpectedly missing buses")
        zlat=zone.y.to_numpy(dtype=float);zlon=zone.x.to_numpy(dtype=float)
        # Median bus coordinates give a robust descriptive center; not a polygon centroid.
        med_lat=float(np.median(zlat));med_lon=float(np.median(zlon))
        # Quantile distribution over all source buses, not distances within any utility zone.
        center_distance=_haversine(med_lat,med_lon,zlat,zlon)
        d0=float(_haversine(med_lat,med_lon,[s.y],[s.x])[0])
        d1=float(_haversine(med_lat,med_lon,[n.y],[n.x])[0])
        pair=float(_haversine(s.y,s.x,[n.y],[n.x])[0])
        samples=int(len(zone))
        energy=float(r.original_zone_annual_mwh)
        if not np.isfinite(energy) or energy<0:raise ValueError("Invalid archived annual EFS source energy")
        records.append({
          "source_Load_id":str(r.Load_id),
          "exported_state":str(s.state),
          "source_reeds_zone":str(s.reeds_zone),
          "source_region_bus_count":samples,
          "original_first_bus_id":old,"max_source_Pd_bus_id":new,
          "original_first_bus_nominal_Pd":float(s.Pd),
          "max_source_Pd_bus_nominal_Pd":float(n.Pd),
          "coordinate_median_center_lat":med_lat,
          "coordinate_median_center_lon":med_lon,
          "source_region_bus_coordinate_radius_p50_km":float(np.percentile(center_distance,50)),
          "source_region_bus_coordinate_radius_p90_km":float(np.percentile(center_distance,90)),
          "source_region_bus_coordinate_radius_max_km":float(center_distance.max()),
          "original_first_bus_distance_to_zone_median_center_km":d0,
          "max_Pd_bus_distance_to_zone_median_center_km":d1,
          "original_first_bus_distance_center_percentile":100*float((center_distance<=d0+1e-8).mean()),
          "max_Pd_bus_distance_center_percentile":100*float((center_distance<=d1+1e-8).mean()),
          "between_candidate_source_bus_haversine_km":pair,
          "original_annual_source_EFS_mwh":energy,
          "original_and_max_pd_candidates_share_exported_zone_labels":True,
          "independent_reeds_zone_polygon_verified":False,
        })
    out=pd.DataFrame(records)
    total=float(out.original_annual_source_EFS_mwh.sum())
    if abs(total-274706987.114121)>.05:raise ValueError("Archived EFS total mismatch")
    return out,{
      "archived_source_load_zones":len(out),
      "archived_source_annual_load_mwh":total,
      "all_pairs_share_same_exported_state_and_reeds_zone_labels":True,
      "zone_median_coordinate_not_actual_polygon_centroid":True,
      "original_load_bus_farther_than_max_pd_from_zone_median_count":int((out.original_first_bus_distance_to_zone_median_center_km>out.max_Pd_bus_distance_to_zone_median_center_km).sum()),
      "max_pd_bus_farther_than_original_from_zone_median_count":int((out.max_Pd_bus_distance_to_zone_median_center_km>out.original_first_bus_distance_to_zone_median_center_km).sum()),
      "source_region_bus_coordinate_radius_p90_km_median_of_20_zones":float(out.source_region_bus_coordinate_radius_p90_km.median()),
      "source_candidate_pair_distance_km_median":float(out.between_candidate_source_bus_haversine_km.median()),
      "source_candidate_pair_distance_km_max":float(out.between_candidate_source_bus_haversine_km.max()),
      "independent_reeds_zone_polygon_available":False,
      "actual_electricity_delivery_points_verified":False,
      "generator_POI_verified":False,
      "full_western_OPF_solved":False,
      "note":"Within exported state×ReEDS-zone source bus-label dispersion only; not proof of true ReEDS polygons, physical delivery locations, line length or load suitability.",
    }

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--base-network",required=True,type=Path)
    p.add_argument("--three-method-table",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    a=p.parse_args()
    network=pypsa.Network(str(a.base_network))
    selected=pd.read_csv(a.three_method_table,
             dtype={"original_first_bus_id":"string","single_largest_positive_pd_connected_bus_id":"string"})
    tab,result=audit(network.buses,selected)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    tab.to_csv(a.output_dir/"efs_2030_source_zone_bus_coordinate_dispersion.csv",index=False)
    (a.output_dir/"efs_2030_source_zone_bus_coordinate_dispersion.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print(tab[["source_Load_id","source_region_bus_count","source_region_bus_coordinate_radius_p90_km",
       "original_first_bus_distance_to_zone_median_center_km",
       "max_Pd_bus_distance_to_zone_median_center_km","between_candidate_source_bus_haversine_km"]].to_string(index=False))
if __name__=="__main__":main()
