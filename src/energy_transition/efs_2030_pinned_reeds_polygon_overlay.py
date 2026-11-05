"""Independent overlay of archived EFS source load buses on PINNED ReEDS polygons.

The pinned PyPSA-USA repository includes the original Reeds_Shapes
rb_and_ba_areas shapefile, whose 'rb' is renamed to 'name' by build_shapes.
This is an upstream geometry *family* audit; does not recreate later
interconnect clipping, county-majority reassignment or actual utility POIs.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry import Point

PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"

def review(buses:pd.DataFrame,choices:pd.DataFrame,reeds):
    need={"Load_id","original_first_bus_id","single_largest_positive_pd_connected_bus_id","original_zone_annual_mwh"}
    if need-set(choices.columns) or len(choices)!=20 or choices.Load_id.duplicated().any():
        raise ValueError("20 archived EFS source-zone pairs required")
    if not {"rb","geometry"}.issubset(reeds.columns) or reeds.crs is None:
        raise ValueError("Pinned upstream ReEDS shape missing original rb field/CRS")
    if not {"state","reeds_zone","x","y"}.issubset(buses.columns):
        raise ValueError("Original pinned bus source geography missing")
    b=buses.copy();b.index=b.index.astype(str)
    if b.index.duplicated().any():raise ValueError("Duplicate source bus ID")
    for coord in ("x","y"):
        b[coord]=pd.to_numeric(b[coord],errors="coerce")
    if not np.isfinite(b[["x","y"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite original source bus locations")
    layer=reeds.to_crs("EPSG:4326")
    if layer.empty:raise ValueError("Empty pinned ReEDS polygons")
    matches_by_zone={}
    for zone in sorted(set(choices.Load_id.astype(str).str.extract(r"(p\d+)")[0])):
        z=layer.loc[layer.rb.astype(str).eq(zone)]
        if z.empty:raise ValueError(f"Official pinned ReEDS polygon missing zone {zone}")
        matches_by_zone[zone]=z.geometry.unary_union
    rows=[]
    for r in choices.itertuples(index=False):
        id=str(r.Load_id)
        match=__import__("re").match(r"^EFS_2030_(p\d+)_(.+)$",id)
        if not match:raise ValueError("Unexpected original EFS Load naming")
        zone,state=match.groups()
        a=str(r.original_first_bus_id);c=str(r.single_largest_positive_pd_connected_bus_id)
        if a not in b.index or c not in b.index:raise ValueError("Missing source bus ID")
        before,after=b.loc[a],b.loc[c]
        if str(before.reeds_zone)!=zone or str(after.reeds_zone)!=zone:
            raise ValueError("Archived zone labels disagree with EFS selection")
        if str(before.state)!=state or str(after.state)!=state:
            raise ValueError("Exported state disagrees with EFS selection")
        poly=matches_by_zone[zone]
        original=Point(float(before.x),float(before.y))
        alternative=Point(float(after.x),float(after.y))
        mwh=float(r.original_zone_annual_mwh)
        if not np.isfinite(mwh) or mwh<0:raise ValueError("Invalid archived EFS demand")
        rows.append({
           "source_Load_id":id,"source_exported_state":state,"source_ReEDS_zone":zone,
           "original_first_bus_id":a,"max_source_Pd_bus_id":c,
           "original_bus_in_upstream_pinned_raw_ReEDS_polygon":bool(poly.covers(original)),
           "max_Pd_bus_in_upstream_pinned_raw_ReEDS_polygon":bool(poly.covers(alternative)),
           "original_annual_efs_source_mwh":mwh,
           "source_polygon_reproduces_later_interconnect_clipping":False,
           "source_polygon_reproduces_county_majority_label_reassignment":False,
           "utility_load_point_geography_certified":False,
        })
    d=pd.DataFrame(rows)
    total=float(d.original_annual_efs_source_mwh.sum())
    if abs(total-274706987.114121)>.05:raise ValueError("Original source EFS annual MWh drift")
    orig_bad=d.loc[~d.original_bus_in_upstream_pinned_raw_ReEDS_polygon]
    max_bad=d.loc[~d.max_Pd_bus_in_upstream_pinned_raw_ReEDS_polygon]
    r={
      "pinned_PyPSA_USA_commit":PIN,
      "original_archived_2030_source_load_count":len(d),
      "original_source_efs_load_mwh":total,
      "source_ReEDS_polygon_unique_rb_count":int(layer.rb.astype(str).nunique()),
      "source_pilot_ReEDS_zone_count":len(matches_by_zone),
      "original_firstbus_raw_polygon_mismatch_count":len(orig_bad),
      "max_pd_raw_polygon_mismatch_count":len(max_bad),
      "original_firstbus_raw_polygon_mismatch_Load_IDs":orig_bad.source_Load_id.tolist(),
      "max_pd_raw_polygon_mismatch_Load_IDs":max_bad.source_Load_id.tolist(),
      "original_firstbus_mismatch_source_load_mwh":float(orig_bad.original_annual_efs_source_mwh.sum()),
      "max_pd_mismatch_source_load_mwh":float(max_bad.original_annual_efs_source_mwh.sum()),
      "source_raw_polygon_does_not_reproduce_post_processing":True,
      "full_original_network_ReEDS_region_membership_certified":False,
      "empirical_11_state_EFS_geography_admitted":False,
      "real_grid_OPF_solved":False,
      "note":"The exact pinned upstream raw ReEDS rb geometry is independently checked. Post-interconnection trimming, county-majority remapping, and actual utility delivery remain unaudited; raw polygon disagreement is a provenance diagnostic, not proof of wrong loads.",
    }
    return d,r

def main():
    import pypsa
    import geopandas as gpd
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--choices",type=Path,required=True)
    p.add_argument("--reeds-shapefile",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    net=pypsa.Network(str(a.network))
    choices=pd.read_csv(a.choices,dtype={"original_first_bus_id":"string",
        "single_largest_positive_pd_connected_bus_id":"string"})
    reeds=gpd.read_file(str(a.reeds_shapefile))
    d,report=review(net.buses,choices,reeds)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    d.to_csv(a.out_dir/"efs_2030_original_vs_maxPd_pinned_ReEDS_polygon.csv",index=False)
    (a.out_dir/"efs_2030_pinned_ReEDS_polygon_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print(d.to_string(index=False))
if __name__=="__main__":main()
