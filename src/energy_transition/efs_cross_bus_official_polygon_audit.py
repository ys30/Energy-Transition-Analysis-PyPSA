"""Independent Census TIGER/Line boundary overlay for two cross-denominator buses.

The Census state geometry is independent context, NOT the original dropped
PyPSA-USA 'full_state' polygon or independent authorization for EFS admission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry import Point

TARGETS={"2030005":{"export_state":"Nevada","denominator_source":"California"},
         "2013019":{"export_state":"Washington","denominator_source":"Oregon"}}
TIGER_URL="https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"

def audit(points:pd.DataFrame, states, *, source_archive_sha256:str)->dict:
    if not {"bus_id","x","y","state","Pd","LAF_state"}.issubset(points.columns):
        raise ValueError("Missing source point fields")
    if len(points)!=2 or set(points.bus_id.astype(str))!=set(TARGETS):
        raise ValueError("Must independently audit exactly two pinned source buses")
    if states.crs is None or states.crs.to_epsg()!=4269 and states.crs.to_epsg()!=4326:
        raise ValueError("Expected Census state boundaries in NAD83/longitude-latitude")
    if "NAME" not in states.columns:
        raise ValueError("Missing Census state name column")
    sub=states[states.NAME.isin({"Nevada","California","Washington","Oregon"})].copy()
    if set(sub.NAME)!={"Nevada","California","Washington","Oregon"} or sub.geometry.isna().any():
        raise ValueError("Incomplete authoritative source polygons")
    projected=sub.to_crs(epsg=5070)
    rows=[]
    for _,record in points.iterrows():
        bid=str(record.bus_id); expected=TARGETS[bid]
        if str(record.state)!=expected["export_state"]:
            raise ValueError(f"Exported bus state has changed: {bid}")
        lon=float(record.x); lat=float(record.y)
        if not np.isfinite((lon,lat)).all() or not(-125<=lon<=-114 and 35<=lat<=49):
            raise ValueError("Invalid West Coast crossing-bus coordinate")
        pt=Point(lon,lat)
        if states.crs.to_epsg()==4269:
            from geopandas import GeoSeries
            pt_geom=GeoSeries([pt],crs="EPSG:4326").to_crs("EPSG:4269").iloc[0]
        else:
            pt_geom=pt
        state_hits=[str(row.NAME) for _,row in sub.iterrows() if row.geometry.covers(pt_geom)]
        proj_pt = __import__("geopandas").GeoSeries([pt],crs="EPSG:4326").to_crs(epsg=5070).iloc[0]
        dists={str(row.NAME):float(row.geometry.boundary.distance(proj_pt))
               for _,row in projected.iterrows() if row.NAME in
               (expected["export_state"],expected["denominator_source"])}
        if len(state_hits)>1:
            classification="state_boundary_overlap_or_touch"
        elif len(state_hits)==0:
            classification="not_contained_by_target_state_polygons"
        elif state_hits[0]==expected["denominator_source"]:
            classification="independent_polygon_supports_inferred_denominator_state"
        elif state_hits[0]==expected["export_state"]:
            classification="independent_polygon_supports_export_state"
        else:
            classification="independent_polygon_other_state"
        rows.append({"bus_id":bid,"longitude":lon,"latitude":lat,
                     "export_state":expected["export_state"],
                     "inferred_denominator_source":expected["denominator_source"],
                     "tiger_2023_polygon_matches":state_hits,
                     "boundary_distance_m_for_relevant_states":dists,
                     "boundary_proximity_under_1000m":bool(min(dists.values())<1000),
                     "classification":classification,
                     "independent_polygon_is_original_upstream_full_state":False})
    return {"official_boundary_source_url":TIGER_URL,
            "official_boundary_vintage":2023,
            "original_zip_sha256":source_archive_sha256,
            "coordinates_source":"archived pinned Western PyPSA-USA NetCDF",
            "bus_audits":rows,
            "independent_state_polygon_point_overlay_performed":True,
            "original_pinned_full_state_polygon_recovered":False,
            "candidate_4_state_EFS_weights_empirically_admitted":False,
            "reeds_geographic_allocation_certified":False,
            "simultaneous_utc_weather_alignment_verified":False,
            "note":"2023 TIGER and projected meter distances are independent context; source era and borders may differ. Border-proximate points need exact pinned GIS overlay before an EFS state-load reassignment.",
            }

def main():
    import geopandas as gpd
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",required=True,type=Path)
    p.add_argument("--tiger-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    archive_sha256=hashlib.sha256(a.tiger_zip.read_bytes()).hexdigest()
    net=pypsa.Network(str(a.network))
    names=net.buses.index.astype(str)
    selected=net.buses.loc[names.isin(TARGETS)].copy()
    selected["bus_id"]=selected.index.astype(str)
    layer=gpd.read_file("zip://"+str(a.tiger_zip))
    report=audit(selected,layer,source_archive_sha256=archive_sha256)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
