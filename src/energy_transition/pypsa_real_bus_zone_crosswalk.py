"""Export observed state-to-ReEDS zone assignments from real base network.

Bus counts are observations of model topology, never demand/LAF weights.
"""
import argparse
import csv
import json
from pathlib import Path
import pypsa


def export(network: Path, csv_path: Path, report_path: Path):
    n = pypsa.Network(str(network))
    required = {"state", "reeds_zone", "country"}
    if not required.issubset(n.buses.columns):
        raise ValueError(f"Missing bus geography columns: {required - set(n.buses.columns)}")
    frame = n.buses[list(required)].copy()
    if frame.isna().any().any() or frame.eq("").any().any():
        raise ValueError("Null or blank geographic tags on base buses")
    grouped = frame.groupby(["state", "reeds_zone", "country"], dropna=False).size().sort_index()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["state", "reeds_zone", "country", "bus_count"])
        for (state, zone, country), count in grouped.items():
            w.writerow([state, zone, country, int(count)])
    counts = frame.groupby("state").size().sort_index()
    report = {
        "network_buses": len(n.buses),
        "state_count": len(counts),
        "reeds_zone_count": int(frame["reeds_zone"].nunique()),
        "state_bus_counts": {str(k): int(v) for k, v in counts.items()},
        "bus_geography_pairs": len(grouped),
        "observed_topology_only": True,
        "bus_count_is_not_load_allocation_factor": True,
        "empirical_laf_available": False,
        "network_demand_allocated": False,
    }
    if int(grouped.sum()) != len(n.buses):
        raise ValueError("Bus crosswalk does not conserve model bus population")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    export(a.network, a.csv, a.report)
