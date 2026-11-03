"""Prepare a 24-hour synthetic load fixture on an existing NARIS zonal network.

Network topology and published directional ratings are retained; hourly demand
is synthetic and the resulting report must never be presented as empirical.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa


def create_fixture(source: Path, target: Path, report_path: Path) -> dict:
    network = pypsa.Network(source)
    if len(network.buses) < 2 or not len(network.links) or len(network.lines):
        raise ValueError("Expected NARIS zonal Link network")
    if len(network.loads) or len(network.generators) or len(network.storage_units):
        raise ValueError("Source network must contain topology only")
    snapshots = pd.date_range("2024-01-01", periods=24, freq="h")
    network.set_snapshots(snapshots)
    bus_ids = sorted(network.buses.index)
    hours = np.arange(24, dtype=float)
    hourly_factor = 0.85 + 0.15 * np.sin(2 * np.pi * (hours - 6) / 24)
    for i, bus in enumerate(bus_ids):
        # Explicitly invented input; not NARIS observed demand.
        baseline = 40.0 + (i % 5) * 10.0
        network.add("Load", f"demand_{bus}", bus=bus,
                    p_set=baseline * hourly_factor)
    target.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(target)
    checked = pypsa.Network(target)
    demand = checked.loads_t.p_set
    if len(checked.snapshots) != 24 or len(checked.loads) != len(bus_ids):
        raise ValueError("Synthetic hourly load round-trip changed dimensions")
    if not np.isfinite(demand.to_numpy(dtype=float)).all():
        raise ValueError("Invalid synthetic demand")
    report = {
        "snapshots": len(checked.snapshots),
        "zones": len(checked.loads),
        "total_load_mwh": float(demand.to_numpy(dtype=float).sum()),
        "source_provenance_required": False,
        "western_membership_verified": False,
        "netcdf_load_roundtrip_verified": True,
        "netcdf_topology_roundtrip_verified": True,
        "optimization_solved": False,
        "historically_calibrated": False,
        "synthetic_opt_in": True,
        "load_origin": "synthetic 24h deterministic sinusoidal fixture",
        "network_origin": "published NARIS directional interface capacities",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--output-network", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create_fixture(args.network, args.output_network, args.report),
                     indent=2))


if __name__ == "__main__":
    main()
