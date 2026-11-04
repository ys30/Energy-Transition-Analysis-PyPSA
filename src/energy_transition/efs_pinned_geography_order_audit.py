"""Pin geographic assignment *order* for interpreting EFS LAF provenance.

Source-order assertions document separate full_state, exported state and
county-majority ReEDS semantics. They do not reconstruct lost GIS variables.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

PIN = "338af9912addbaf038c6098fe27e1e6ef099d8aa"


def audit_geography_order(base_source: str, shape_source: str) -> dict:
    anchors = {
        "full_state_overlay": 'map_bus_to_region(gdf_bus, na_shape, ["full_state"])',
        "export_state_overlay": 'map_bus_to_region(gdf_bus, state_shape, ["state"])',
        "reeds_zone_overlay": 'map_bus_to_region(gdf_bus, reeds_shape, ["reeds_zone", "reeds_ba"])',
        "county_overlay": 'map_bus_to_region(gdf_bus, county_shape, ["county"])',
        "source_state_missing_fill": "gdf_bus = assign_missing_state_regions(gdf_bus)",
        "source_denominator": 'group_sums = gdf_bus.groupby("full_state")["Pd"].transform("sum")',
        "laf_compute": 'gdf_bus["LAF_state"] = gdf_bus["Pd"] / group_sums',
        "drop_source_state": 'gdf_bus = gdf_bus.drop(columns=["full_state"])',
        "offshore_add": "n = add_offshore_buses(n, offshore_buses)",
        "county_majority_reeds": "assign_reeds_memberships(n, snakemake.input.reeds_memberships)",
    }
    missing=[label for label,needle in anchors.items() if needle not in base_source]
    if missing: raise ValueError("Missing pinned geographic source anchors: "+", ".join(missing))
    positions=[base_source.index(anchors[label]) for label in anchors]
    if positions!=sorted(positions):
        raise ValueError("Pinned geographic processing order changed")
    required_shape=[
        "def load_na_shapes(",
        'resolution="10m"',
        'name=state_shape',
        "gdf_states = trim_states_to_interconnect(gdf_states, gdf_nerc, interconnect)",
        'state_boundaries = gdf_states[["name", "country", "geometry"]]',
    ]
    if not all(needle in shape_source for needle in required_shape):
        raise ValueError("Pinned Natural Earth source and clipped-state construction not verified")
    mode='n.buses.groupby("county")["reeds_state"].transform('
    if mode not in base_source or 'lambda x: x.mode()[0]' not in base_source:
        raise ValueError("County majority ReEDS state assignment source changed")
    return {
        "pinned_upstream_commit":PIN,
        "build_base_network_sha256":hashlib.sha256(base_source.encode()).hexdigest(),
        "build_shapes_sha256":hashlib.sha256(shape_source.encode()).hexdigest(),
        "source_assignment_steps_in_order":list(anchors),
        "original_full_state_shape":"untrimmed North America Natural Earth 10m admin_1",
        "export_state_shape":"NERC-trimmed interconnection Natural Earth 10m state boundaries",
        "reeds_state_definition":"reeds_zone membership followed by county-majority reassignment",
        "full_state_normalization_uses_Pd":True,
        "full_state_and_exported_state_same_semantics":False,
        "reeds_state_matches_export_state_guaranteed":False,
        "original_build_time_shape_bytes_verified":False,
        "original_full_state_bus_labels_recovered":False,
        "independent_efs_geographic_admission":False,
        "network_solve_completed":False,
        "interpretation":"Source implementation explains distinct normalization and exported region keys, but cannot alone verify each original bus geometry.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--shapes",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit_geography_order(a.base.read_text(),a.shapes.read_text())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))

if __name__=="__main__":main()
