"""Audit original-source county-majority mechanism behind two ReEDS polygon mismatches.

The pinned PyPSA-USA build_base_network.py applies
  n.buses.groupby('county')['reeds_zone'].transform(lambda x: x.mode()[0])
after original zone GIS matching. Original post-trim and pre-reassignment
zone tags were not saved in base NetCDF; this is a *consistency diagnostic*
and does not claim to reproduce historical intermediate data.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
from shapely.geometry import Point

TARGETS={
  "EFS_2030_p28_Arizona":("2040000","p28"),
  "EFS_2030_p18_Montana":("2077004","p18"),
}

def audit(buses,raw_regions):
    required={"x","y","county","reeds_zone","state"}
    if required-set(buses):raise ValueError("Missing original archived network attributes")
    if "rb" not in raw_regions or raw_regions.crs is None:raise ValueError("Pinned raw ReEDS GIS missing")
    b=buses.copy();b.index=b.index.astype(str)
    if b.index.duplicated().any():raise ValueError("Duplicate original bus ID")
    for key in ("x","y"):
        b[key]=pd.to_numeric(b[key],errors="coerce")
    if not np.isfinite(b[["x","y"]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid source bus coordinates")
    shape=raw_regions.to_crs("EPSG:4326")
    valid=shape.loc[shape.rb.notna()].copy()
    matched=[]
    for load,(bus_id,expected) in TARGETS.items():
        if bus_id not in b.index:raise ValueError(f"Missing target bus {bus_id}")
        target=b.loc[bus_id]
        county=target.county
        if pd.isna(county):raise ValueError("Target has no source county label")
        cohort=b.loc[b.county.eq(county)].copy()
        if cohort.empty:raise ValueError("Source county cohort missing")
        final_counts=cohort.reeds_zone.astype("string").value_counts().to_dict()
        # geometries of original source zones, before upstream county-majority reassignment
        geometries={}
        for _,r in valid.iterrows():
            name=str(r.rb)
            geometries.setdefault(name,[]).append(r.geometry)
        from shapely.ops import unary_union
        geometries={zone:unary_union(polys) for zone,polys in geometries.items()}
        raw_labels=[]
        for _,row in cohort.iterrows():
            point=Point(float(row.x),float(row.y))
            claims=[name for name,geometry in geometries.items() if geometry.covers(point)]
            raw_labels.append(sorted(claims))
        raw_single=[claims[0] if len(claims)==1 else None for claims in raw_labels]
        single_series=pd.Series(raw_single,index=cohort.index,dtype="string")
        raw_counts=single_series.value_counts().to_dict()
        raw_unmatched=int(single_series.isna().sum())
        raw_mode=sorted(k for k,v in raw_counts.items() if v==max(raw_counts.values())) if raw_counts else []
        saved_mode=sorted(k for k,v in final_counts.items() if v==max(final_counts.values()))
        if str(target.reeds_zone)!=expected:raise ValueError("Pinned postcounty zone label drift")
        matched.append({
          "EFS_zone_load":load,"original_firstbus_id":bus_id,
          "archived_source_county":str(county),
          "source_target_postprocessed_reeds_zone":str(target.reeds_zone),
          "source_county_bus_count":len(cohort),
          "source_county_final_reeds_zone_counts":{str(k):int(v) for k,v in final_counts.items()},
          "source_county_final_mode":saved_mode,
          "source_county_final_all_same_reeds_zone":len(final_counts)==1,
          "source_county_raw_polygon_single_cover_counts":{str(k):int(v) for k,v in raw_counts.items()},
          "source_county_raw_polygon_unmatched_or_multiple_bus_count":raw_unmatched,
          "source_county_raw_polygon_mode":raw_mode,
          "archived_final_zone_is_raw_polygon_county_mode":str(target.reeds_zone) in raw_mode,
          "raw_polygon_overlay_reproduces_original_premajority_zone_assignments":False,
          "actual_utility_delivery_verified":False,
        })
    return {
      "pinned_upstream_mode_rule":"groupby(county).reeds_zone.transform(lambda x: x.mode()[0])",
      "historical_premajority_bus_labels_recovered":False,
      "historical_posttrimmed_zone_geometry_recovered":False,
      "all_target_archived_counties_finally_uniform":all(x["source_county_final_all_same_reeds_zone"] for x in matched),
      "reviewed_source_load_cases":matched,
      "original_load_relocation_approved":False,
      "physically_validated_western_OPF":False,
      "note":"Raw pinned polygons and saved post-processed county labels are compared as source consistency only; raw geometry != original intermediate zone labels if trim, nearest-fill or other remapping occurred.",
    }

def main():
    import pypsa
    import geopandas as gpd
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--raw-reeds",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(pypsa.Network(str(a.base)).buses,gpd.read_file(str(a.raw_reeds)))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
