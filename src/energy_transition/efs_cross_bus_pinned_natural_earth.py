"""Recreate pinned PyPSA-USA full_state *polygon method* using Natural Earth 10m.

Current Natural Earth archive is not guaranteed to equal the exact cached
shape bytes when historical PyPSA-USA base network was built.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry import Point

NATURAL_EARTH_URL=(
    "https://naturalearth.s3.amazonaws.com/10m_cultural/"
    "ne_10m_admin_1_states_provinces_lakes.zip"
)
TARGETS={
    "2030005":{"exported_state":"Nevada","inferred_source":"California","source_denominator":67028.96},
    "2013019":{"exported_state":"Washington","inferred_source":"Oregon","source_denominator":9281.36},
}
PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"

def audit_natural_earth(points:pd.DataFrame, ne, *, archive_sha256:str, source_code:str)->dict:
    required_code=[
        'shpreader.natural_earth(',
        'resolution="10m"',
        'name=state_shape',
        'attr["iso_a2"] in countries',
    ]
    if not all(token in source_code for token in required_code):
        raise ValueError("Pinned Natural Earth full_state source algorithm not verified")
    required_point={"bus_id","x","y","state","Pd","LAF_state"}
    if not required_point.issubset(points.columns) or set(points.bus_id.astype(str))!=set(TARGETS):
        raise ValueError("Missing two exact original network bus coordinates")
    if not {"name","iso_a2"}.issubset(ne.columns) or ne.crs is None:
        raise ValueError("Unexpected Natural Earth layer schema/CRS")
    subset=ne.loc[ne.iso_a2.eq("US") & ne["name"].isin(
        {"California","Nevada","Oregon","Washington"}
    )].to_crs("EPSG:4326")
    if set(subset["name"])!={"California","Nevada","Oregon","Washington"}:
        raise ValueError("Natural Earth four-state coverage is incomplete")
    result=[]
    for _,row in points.iterrows():
        bid=str(row.bus_id)
        cfg=TARGETS[bid]
        if str(row.state)!=cfg["exported_state"]:
            raise ValueError("Pinned exported state changed")
        pdv=float(row.Pd);laf=float(row.LAF_state)
        if pdv<=0 or laf<=0 or abs(pdv/laf-cfg["source_denominator"])>0.01:
            raise ValueError("Pinned source denominator changed")
        x=float(row.x);y=float(row.y)
        if not np.isfinite([x,y]).all():raise ValueError("Missing source point coordinates")
        pt=Point(x,y)
        matches=sorted(str(g["name"]) for _,g in subset.iterrows() if g.geometry.covers(pt))
        result.append({
            "bus_id":bid,
            "coordinates":[x,y],
            "pinned_exported_state":cfg["exported_state"],
            "inferred_pd_denominator_state":cfg["inferred_source"],
            "natural_earth_10m_polygon_matches":matches,
            "polygon_matches_inferred_denominator_state":matches==[cfg["inferred_source"]],
            "matches_original_full_state_attribute_from_archived_build":False,
        })
    return {
        "pinned_pypsa_usa_commit":PIN,
        "pinned_full_state_implementation":"cartopy shapereader natural_earth 10m cultural admin_1_states_provinces_lakes",
        "download_url":NATURAL_EARTH_URL,
        "download_zip_sha256":archive_sha256,
        "bus_results":result,
        "all_matches_inferred_source":all(x["polygon_matches_inferred_denominator_state"] for x in result),
        "contemporaneous_natural_earth_shape_version_verified":False,
        "original_archived_build_full_state_labels_recovered":False,
        "candidate_source_geography_independently_admitted":False,
        "empirically_admitted_11_state_EFS":False,
        "note":"Replicates named upstream GIS data family, but current downloaded Natural Earth bytes may differ from original cartopy cache; no EFS geographic admission.",
    }

def main():
    import pypsa
    import geopandas as gpd
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--natural-earth-zip",type=Path,required=True)
    p.add_argument("--upstream-build-shapes",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    net=pypsa.Network(str(a.network))
    wanted=net.buses.index.astype(str).isin(TARGETS)
    points=net.buses.loc[wanted].copy()
    points["bus_id"]=points.index.astype(str)
    layer=gpd.read_file("zip://"+str(a.natural_earth_zip))
    report=audit_natural_earth(
        points,layer,
        archive_sha256=hashlib.sha256(a.natural_earth_zip.read_bytes()).hexdigest(),
        source_code=a.upstream_build_shapes.read_text(encoding="utf-8"),
    )
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
