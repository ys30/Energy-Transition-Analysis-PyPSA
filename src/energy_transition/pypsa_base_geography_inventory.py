"""Report observed geographical labels on a built PyPSA-USA base network.

This is exploratory inspection: missing labels never imply verified geographic
membership and no EFS zonal allocation is performed here.
"""
import argparse
import json
from pathlib import Path
import pypsa


def inspect(path: Path):
    n = pypsa.Network(str(path))
    columns = list(n.buses.columns)
    candidates = ("country", "state", "reeds_zone", "reeds_ba", "region", "substation")
    dimensions = {}
    for field in candidates:
        if field in n.buses.columns:
            v = n.buses[field].dropna().astype(str)
            counts = v.value_counts()
            dimensions[field] = {"non_null_buses": int(len(v)), "unique_labels": int(len(counts)),
                                  "counts": {str(k): int(count) for k, count in counts.items()}}
    return {"buses": len(n.buses), "bus_columns": columns, "geographic_dimensions": dimensions,
            "explicit_western_membership_verified": False,
            "state_to_reeds_laf_verified": False,
            "note": "Observed bus metadata only; no geographic or EFS demand attribution is inferred."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = inspect(a.network)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
