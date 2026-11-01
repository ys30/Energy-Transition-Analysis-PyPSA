"""Physical structural validation of a real PyPSA base network NetCDF."""
import argparse
import json
from pathlib import Path

import pypsa


def validate(path: Path) -> dict:
    n = pypsa.Network(str(path))
    bus_names = set(n.buses.index)
    if not bus_names or n.lines.empty:
        raise ValueError("Empty network topology")
    report = {"buses": len(n.buses), "lines": len(n.lines),
              "links": len(n.links), "transformers": len(n.transformers),
              "snapshots": len(n.snapshots)}
    for kind, frame in (("lines", n.lines), ("links", n.links), ("transformers", n.transformers)):
        if frame.empty:
            continue
        missing = set(frame.bus0).union(frame.bus1) - bus_names
        if missing:
            raise ValueError(f"{kind} refer to {len(missing)} nonexistent buses")
        self_loops = int((frame.bus0 == frame.bus1).sum())
        report[f"{kind}_self_loops"] = self_loops
        if self_loops:
            raise ValueError(f"{kind} have {self_loops} self loops")
    if len(n.snapshots) != 1:
        raise ValueError("Expected one-snapshot base topology, not a solved hourly model")
    report.update({
        "all_branch_endpoints_exist": True,
        "base_topology_verified": True,
        "hourly_load_attached": False,
        "model_solved": False,
        "western_only_membership_verified": False,
    })
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = validate(a.network)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
