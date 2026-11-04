"""Independent modern Natural Earth polygon overlay for EFS first-bus vs max-Pd candidates.

This tests exported state labels against downloaded Natural Earth polygons;
it does NOT reconstruct original historical upstream full_state shapefile
cache, authenticate ReEDS zone boundaries or certify load delivery sites.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry import Point

STATES={"Arizona","Colorado","Idaho","Montana","New Mexico","Utah","Wyoming"}

def review(table:pd.DataFrame,geo,sha256:str):
    need={"Load_id","original_bus_id","single_max_pd_candidate_bus_id",
          "first_bus_lat","first_bus_lon","max_pd_bus_lat","max_pd_bus_lon",
          "original_annual_mwh"}
    if need-set(table):raise ValueError("Missing source EFS geographic candidate columns")
    if len(table)!=20 or table.Load_id.duplicated().any():raise ValueError("Expected exactly 20 original zonal Loads")
    if not {"name","iso_a2"}.issubset(geo.columns) or geo.crs is None:
        raise ValueError("Natural Earth 10m source layer schema or CRS unavailable")
    layer=geo.loc[geo.iso_a2.eq("US")&geo.name.isin(STATES)].to_crs("EPSG:4326")
    if set(layer.name)!=STATES:raise ValueError("Missing Western states in source layer")
    out=[]
    for r in table.itertuples(index=False):
        expected=str(r.Load_id).rsplit("_",1)[-1].replace("%20"," ")
        if expected not in STATES:raise ValueError("Unknown EFS Load state in ID")
        old=Point(float(r.first_bus_lon),float(r.first_bus_lat))
        new=Point(float(r.max_pd_bus_lon),float(r.max_pd_bus_lat))
        for coord in (old,new):
            if not np.isfinite([coord.x,coord.y]).all() or not (-180<=coord.x<=180 and -90<=coord.y<=90):
                raise ValueError("Invalid archived candidate coordinates")
        original_matches=sorted(set(str(x.name) for x in layer.itertuples() if x.geometry.covers(old)))
        chosen_matches=sorted(set(str(x.name) for x in layer.itertuples() if x.geometry.covers(new)))
        annual=float(r.original_annual_mwh)
        if not np.isfinite(annual) or annual<0:raise ValueError("Invalid original EFS annual demand")
        out.append({
          "Load_id":str(r.Load_id),
          "expected_exported_state":expected,
          "original_bus_id":str(r.original_bus_id),
          "max_pd_candidate_bus_id":str(r.single_max_pd_candidate_bus_id),
          "original_polygon_state_matches":";".join(original_matches),
          "max_pd_polygon_state_matches":";".join(chosen_matches),
          "original_bus_inside_exported_state_polygon":expected in original_matches,
          "max_pd_bus_inside_exported_state_polygon":expected in chosen_matches,
          "original_annual_load_mwh":annual,
          "original_full_state_historical_cache_verified":False,
          "utility_certified_load_site":False,
        })
    rows=pd.DataFrame(out)
    unexpected=rows.loc[~rows.max_pd_bus_inside_exported_state_polygon]
    original_unexpected=rows.loc[~rows.original_bus_inside_exported_state_polygon]
    return rows,{
      "natural_earth_download_zip_sha256":sha256,
      "source_original_zonal_Load_count":len(rows),
      "original_exported_state_polygon_mismatch_count":len(original_unexpected),
      "max_pd_exported_state_polygon_mismatch_count":len(unexpected),
      "max_pd_mismatch_zonal_Load_IDs":unexpected.Load_id.tolist(),
      "original_mismatch_zonal_Load_IDs":original_unexpected.Load_id.tolist(),
      "max_pd_mismatch_zone_annual_mwh":float(unexpected.original_annual_load_mwh.sum()),
      "original_mismatch_zone_annual_mwh":float(original_unexpected.original_annual_load_mwh.sum()),
      "original_full_state_archived_upstream_geometry_cache_verified":False,
      "official_utility_delivery_points_certified":False,
      "EFS_2030_2050_physical_OPF_solved":False,
      "note":"Independent currently downloaded Natural Earth state polygons; not historical exact upstream full_state geometry or certified ReEDS load service boundary.",
    }

def main():
    import geopandas as gpd
    p=argparse.ArgumentParser()
    p.add_argument("--candidate-geo",required=True,type=Path)
    p.add_argument("--natural-earth-zip",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    source=pd.read_csv(a.candidate_geo,dtype={"original_bus_id":"string","single_max_pd_candidate_bus_id":"string"})
    geo=gpd.read_file("zip://"+str(a.natural_earth_zip))
    rows,r=review(source,geo,hashlib.sha256(a.natural_earth_zip.read_bytes()).hexdigest())
    a.outdir.mkdir(parents=True,exist_ok=True)
    rows.to_csv(a.outdir/"efs_2030_20zone_geographic_candidate_state_polygon.csv",index=False)
    (a.outdir/"efs_2030_20zone_geographic_candidate_state_polygon.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
    print(rows.to_string(index=False))
if __name__=="__main__":main()
