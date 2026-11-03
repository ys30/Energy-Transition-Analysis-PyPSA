"""Identify whether source buses without LAF carry PyPSA loads.

This is a read-only diagnostic, not permission to treat an absent LAF as
zero. Static, dynamic, and network component presence are recorded separately.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def classify_missing_laf_buses(network) -> dict:
    buses = network.buses
    required = {"LAF_state", "reeds_state", "reeds_zone"}
    if not required.issubset(buses.columns):
        raise ValueError("Required geographic bus columns missing")
    missing_ids = buses.index[buses["LAF_state"].isna()]
    loads = network.loads
    load_buses = set(loads.bus.astype(str))
    generator_buses = set(network.generators.bus.astype(str))
    storage_buses = set(network.storage_units.bus.astype(str))
    link_ends = set(network.links.bus0.astype(str)) | set(network.links.bus1.astype(str))
    line_ends = set(network.lines.bus0.astype(str)) | set(network.lines.bus1.astype(str))
    dynamic = getattr(network.loads_t, "p_set", pd.DataFrame())
    rows = []
    for bus_id in missing_ids:
        load_names = list(loads.index[loads.bus.astype(str).eq(str(bus_id))])
        static_nonzero = False
        dynamic_nonzero = False
        dynamic_values_present = False
        for name in load_names:
            static_value = pd.to_numeric(pd.Series([loads.loc[name, "p_set"]]), errors="coerce").iloc[0]
            if pd.notna(static_value) and abs(float(static_value)) > 1e-9:
                static_nonzero = True
            if name in dynamic.columns:
                series = pd.to_numeric(dynamic[name], errors="coerce")
                if series.notna().any():
                    dynamic_values_present = True
                if (series.abs() > 1e-9).any():
                    dynamic_nonzero = True
        rows.append({
            "bus": str(bus_id),
            "state": str(buses.loc[bus_id, "reeds_state"]),
            "zone": str(buses.loc[bus_id, "reeds_zone"]),
            "has_load_component": bool(str(bus_id) in load_buses),
            "static_nonzero_load": bool(static_nonzero),
            "dynamic_nonzero_load": bool(dynamic_nonzero),
            "dynamic_values_present": bool(dynamic_values_present),
            "has_generator": bool(str(bus_id) in generator_buses),
            "has_storage_unit": bool(str(bus_id) in storage_buses),
            "has_link_endpoint": bool(str(bus_id) in link_ends),
            "has_line_endpoint": bool(str(bus_id) in line_ends),
        })
    df = pd.DataFrame(rows)
    flags = ["has_load_component", "static_nonzero_load", "dynamic_nonzero_load",
             "has_generator", "has_storage_unit", "has_link_endpoint",
             "has_line_endpoint"]
    return {
        "missing_laf_bus_count": len(rows),
        "missing_laf_load_component_buses": int(df["has_load_component"].sum()) if len(df) else 0,
        "missing_laf_static_nonzero_load_buses": int(df["static_nonzero_load"].sum()) if len(df) else 0,
        "missing_laf_dynamic_nonzero_load_buses": int(df["dynamic_nonzero_load"].sum()) if len(df) else 0,
        "missing_laf_generator_buses": int(df["has_generator"].sum()) if len(df) else 0,
        "missing_laf_storage_buses": int(df["has_storage_unit"].sum()) if len(df) else 0,
        "missing_laf_transmission_endpoint_buses": int(
            (df["has_link_endpoint"] | df["has_line_endpoint"]).sum()) if len(df) else 0,
        "network_component_counts": {
            "loads": int(len(network.loads)),
            "generators": int(len(network.generators)),
            "storage_units": int(len(network.storage_units)),
            "links": int(len(network.links)),
            "lines": int(len(network.lines)),
        },
        "topology_only_network_for_load_generation": bool(
            len(network.loads)==0 and len(network.generators)==0
            and len(network.storage_units)==0
        ),
        "load_absence_proves_zero_future_efs_demand": False,
        "classification_by_bus": rows,
        "missing_laf_can_be_assumed_zero": False,
        "missing_laf_buses_may_be_excluded": False,
        "empirical_laf_admitted": False,
        "interpretation": "No explicit Load component does not prove that a bus has zero future EFS demand; upstream LAF methodology still requires source validation",
    }
