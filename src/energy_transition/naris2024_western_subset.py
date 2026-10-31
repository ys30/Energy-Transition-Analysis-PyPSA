"""Select Western Interconnection regions using upstream ReEDS membership, not guessed BA IDs."""
from __future__ import annotations
import argparse
import csv
import io
import json
from pathlib import Path
from urllib.request import urlopen

MEMBERSHIP_URL = "https://raw.githubusercontent.com/PyPSA/pypsa-usa/master/workflow/repo_data/ReEDS_Constraints/membership.csv"


def western_region_ids(membership_csv: bytes) -> set[str]:
    rows = list(csv.DictReader(io.StringIO(membership_csv.decode("utf-8-sig"))))
    if not rows or not {"ba", "interconnect", "country"} <= set(rows[0]):
        raise ValueError("Unexpected ReEDS membership schema")
    ids = [r["ba"] for r in rows
           if r["interconnect"].strip().lower() == "western"
           and r["country"].strip().upper() == "USA"]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("Empty or duplicate Western region IDs")
    return set(ids)


def subset(network, membership_csv: bytes):
    ids = western_region_ids(membership_csv)
    keep = ids & set(network.buses.index)
    if not keep:
        raise ValueError("No overlap between Western membership and network buses")
    boundary = network.links.loc[
        network.links.bus0.isin(keep) ^ network.links.bus1.isin(keep)
    ]
    internal = network.links.loc[
        network.links.bus0.isin(keep) & network.links.bus1.isin(keep)
    ]
    result = network.copy()
    result.remove("Link", result.links.index.difference(internal.index))
    result.remove("Bus", result.buses.index.difference(keep))
    if not set(result.links.bus0).union(result.links.bus1) <= set(result.buses.index):
        raise ValueError("Dangling Link after subsetting")
    return result, {
        "membership_source": MEMBERSHIP_URL,
        "western_membership_regions": len(ids),
        "matched_buses": len(keep),
        "internal_directed_links": len(internal),
        "excluded_boundary_directed_links": len(boundary),
        "boundary_assumption": "cross-interconnection transfers excluded, not modeled as zero historically",
        "has_generation_or_demand": False,
        "network_solved": False,
    }


def main():
    import pypsa
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    with urlopen(MEMBERSHIP_URL, timeout=40) as response:
        membership = response.read(1_000_001)
    if len(membership) > 1_000_000:
        raise ValueError("Membership source exceeds size bound")
    network, report = subset(pypsa.Network(str(args.input)), membership)
    args.network.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(args.network)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
