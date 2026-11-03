"""Read-only audit of LAF availability on existing Western PyPSA artifacts.

No missing LAF is inferred, no source file is modified, and numeric
field availability does not certify geographic provenance or dispatch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .efs_source_bus_laf_extraction import candidate_weights


def audit_bus_laf(buses: pd.DataFrame) -> dict:
    required = ["reeds_state", "reeds_zone", "LAF_state"]
    available = [c for c in required if c in buses.columns]
    report = {
        "bus_count": int(len(buses)),
        "required_laf_columns": required,
        "available_laf_columns": available,
        "missing_laf_columns": [c for c in required if c not in buses.columns],
        "candidate_laf_extraction_passed": False,
        "candidate_weights_verified_source": False,
        "empirical_load_admitted": False,
        "network_physical_calibration_verified": False,
    }
    if len(available) != len(required):
        report["blocker"] = "Missing source bus fields; cannot derive LAF from this network"
        return report
    try:
        _, evidence = candidate_weights(buses)
    except (ValueError, TypeError, KeyError) as exc:
        report["blocker"] = str(exc)
        return report
    report.update({
        "candidate_laf_extraction_passed": True,
        "candidate_zone_pairs": evidence["reeds_zone_pairs"],
        "candidate_states": evidence["covered_states"],
        "blocker": "Source revision, geography methodology and Western membership still require independent admission",
    })
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    import pypsa
    network = pypsa.Network(args.network)
    report = audit_bus_laf(network.buses)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
