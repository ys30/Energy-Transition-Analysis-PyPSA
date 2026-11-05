"""Forensic audit of two original EFS Load representative buses off raw pinned ReEDS polygons.

Identifies nearest raw rb polygon and projected boundary distance, without
claiming invalid loads: upstream county-majority and interconnection trims
are not reconstructed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.ops import transform
from pyproj import Transformer

EXPECTED={
 "EFS_2030_p28_Arizona":("2040000","2040003","p28"),
 "EFS_2030_p18_Montana":("2077004","2077101","p18"),
}

def audit(network,choices,shapes):
    if "rb" not in shapes or shapes.crs is None:raise ValueError("Original ReEDS rb geometry missing")
    layer=shapes.to_crs("EPSG:4326").copy()
    projector=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
    grouped={}
    for zone,frame in layer.groupby("rb",dropna=True):
        grouped[str(zone)]=frame.geometry.union_all()
    if not set(x[2] for x in EXPECTED.values()).issubset(grouped):
        raise ValueError("Pinned zone polygon unavailable")
    rows=[]
    for load,(first,alternate,zone) in EXPECTED.items():
        c=choices.loc[choices.Load_id.eq(load)]
        if len(c)!=1:raise ValueError("Missing source Load record")
        r=c.iloc[0]
        if str(r.original_first_bus_id)!=first or str(r.single_largest_positive_pd_connected_bus_id)!=alternate:
            raise ValueError("Archived original bus IDs changed")
        for role,bid in [("original_first_bus",first),("candidate_max_pd_bus",alternate)]:
            b=network.buses.loc[bid]
            if str(b.reeds_zone)!=zone:raise ValueError("Original network reeds_zone label drift")
            lon=float(b.x);lat=float(b.y)
            if not np.isfinite([lon,lat]).all():raise ValueError("Nonfinite coordinate")
            point=Point(lon,lat)
            in_zones=sorted(zoneid for zoneid,polygon in grouped.items() if polygon.covers(point))
            p2=transform(projector.transform,point)
            dists={zoneid:float(p2.distance(transform(projector.transform,polygon)))/1000
                    for zoneid,polygon in grouped.items()}
            nearest=min(dists,key=dists.get)
            rows.append({"EFS_Load_id":load,"source_role":role,
              "source_bus_id":bid,"source_reeds_zone_label":zone,
              "source_exported_state":str(b.state),
              "latitude":lat,"longitude":lon,
              "raw_pinned_ReEDS_polygon_matches":in_zones,
              "inside_source_label_raw_polygon":zone in in_zones,
              "projected_distance_to_source_label_raw_polygon_km":dists[zone],
              "nearest_raw_reeds_zone":nearest,
              "nearest_raw_reeds_zone_distance_km":dists[nearest],
              "original_2030_zone_annual_EFS_mwh":float(r.original_zone_annual_mwh),
              "original_county_majority_reassignment_reconstructed":False,
              "utility_certified_load_target":False})
    return {"source_mismatch_Load_IDs":list(EXPECTED),
            "source_bus_results":rows,
            "raw_ReEDS_source_polygon_count":len(grouped),
            "upstream_county_majority_reassignment_recovered":False,
            "upstream_interconnection_trimmed_shapes_recovered":False,
            "physical_load_delivery_approved":False,
            "actual_Western_OPF_solved":False,
            "note":"Distances to original pinned upstream raw rb polygons are not an independent replica of clipped postprocessed reeds_zone or electric delivery boundaries."}

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--choices",type=Path,required=True)
    p.add_argument("--shp",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    n=pypsa.Network(str(a.base))
    choices=pd.read_csv(a.choices,dtype={"original_first_bus_id":"string","single_largest_positive_pd_connected_bus_id":"string"})
    result=audit(n,choices,gpd.read_file(str(a.shp)))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
