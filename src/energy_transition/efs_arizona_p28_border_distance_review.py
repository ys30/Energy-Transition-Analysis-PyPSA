"""Independent detailed GIS review of original EFS Arizona p28 load candidate pair.

Uses the same Natural Earth admin-1 source family as the accepted independent
20-zone polygon audit. Reports ALL US-state polygon intersections and
projected point-to-Arizona polygon distances in EPSG:5070.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.ops import transform
from pyproj import Transformer

EXPECTED_LOAD="EFS_2030_p28_Arizona"
FIRST_ID="2040000"
CANDIDATE_ID="2040003"

def review(source:pd.DataFrame,admin):
    need={"Load_id","original_bus_id","single_max_pd_candidate_bus_id",
          "first_bus_lon","first_bus_lat","max_pd_bus_lon","max_pd_bus_lat",
          "original_annual_mwh"}
    if need-set(source):raise ValueError("Original source candidate columns missing")
    found=source.loc[source.Load_id.eq(EXPECTED_LOAD)]
    if len(found)!=1:raise ValueError("Exact Arizona p28 zone missing or duplicated")
    r=found.iloc[0]
    if str(r.original_bus_id)!=FIRST_ID or str(r.single_max_pd_candidate_bus_id)!=CANDIDATE_ID:
        raise ValueError("Previously verified original source candidate ID changed")
    if admin.crs is None or not {"iso_a2","name"}.issubset(admin.columns):
        raise ValueError("Natural Earth geometry lacks named US states or CRS")
    usa=admin.loc[admin.iso_a2.eq("US")].to_crs("EPSG:4326").copy()
    if not usa.name.eq("Arizona").any():raise ValueError("Arizona GIS shape missing")
    az=usa.loc[usa.name.eq("Arizona")]
    trans=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
    polygons=[transform(trans.transform,g) for g in az.geometry]
    rows=[]
    for label,bus,latkey,lonkey in [
        ("original_first_bus",FIRST_ID,"first_bus_lat","first_bus_lon"),
        ("connected_max_pd",CANDIDATE_ID,"max_pd_bus_lat","max_pd_bus_lon")]:
        lat=float(r[latkey]);lon=float(r[lonkey])
        if not np.isfinite([lat,lon]).all() or not (25<=lat<=50 and -125<=lon<=-100):
            raise ValueError("Invalid source bus geography")
        point=Point(lon,lat)
        all_us_matches=sorted(set(str(z["name"]) for _,z in usa.iterrows()
                if z.geometry.covers(point)))
        projected=transform(trans.transform,point)
        distance_km=min(projected.distance(poly) for poly in polygons)/1000.
        rows.append({"role":label,"source_bus_id":bus,"latitude":lat,"longitude":lon,
            "all_US_Natural_Earth_state_polygon_matches":all_us_matches,
            "inside_Natural_Earth_Arizona_polygon":"Arizona" in all_us_matches,
            "minimum_EPSG5070_point_to_Arizona_polygon_km":distance_km,
            "source_load_year":2030,
            "original_zone_EFS_load_mwh":float(r.original_annual_mwh),
            "certified_utility_load_delivery_site":False})
    out={"source_zone_id":EXPECTED_LOAD,"source_first_bus_id":FIRST_ID,
         "source_alternative_bus_id":CANDIDATE_ID,"actual_source_geographic_review":rows,
         "original_full_state_cached_shapefile_version_verified":False,
         "exported_state_is_utility_certified":False,
         "ReEDS_zone_polygon_membership_verified":False,
         "candidate_load_reassignment_admitted":False,
         "grid_dispatch_solved":False,
         "note":"Independent current Natural Earth polygon only; distance to polygon does not establish an EFS bus or electrical service-area mapping."}
    return out

def main():
    import geopandas as gpd
    p=argparse.ArgumentParser()
    p.add_argument("--original-candidate-pairs",type=Path,required=True)
    p.add_argument("--natural-earth-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    df=pd.read_csv(a.original_candidate_pairs,
       dtype={"original_bus_id":"string","single_max_pd_candidate_bus_id":"string"})
    geo=gpd.read_file("zip://"+str(a.natural_earth_zip))
    result=review(df,geo)
    result["natural_earth_download_zip_sha256"]=hashlib.sha256(a.natural_earth_zip.read_bytes()).hexdigest()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
