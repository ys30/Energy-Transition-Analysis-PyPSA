"""Inspect a genuine upstream built PyPSA-USA network before LAF admission.

Reports source-file digest and Western membership coverage; this check does not
infer LAF shares, calibrate dispatch, or establish source geographic validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pypsa

from .naris2024_western_subset import western_region_ids


def inspect_built_network(network_path: Path, membership_path: Path) -> dict:
    network_path = Path(network_path)
    membership_path = Path(membership_path)
    required = western_region_ids(membership_path.read_bytes())
    n = pypsa.Network(network_path)
    columns = {"reeds_state", "reeds_zone", "LAF_state"}
    missing_columns = sorted(columns - set(n.buses.columns))
    if missing_columns:
        raise ValueError(f"Built network missing LAF input columns: {missing_columns}")
    zone = n.buses["reeds_zone"].astype("string")
    western = n.buses.loc[zone.isin(required)].copy()
    observed = set(western["reeds_zone"].dropna().astype(str))
    missing = sorted(required - observed)
    if western.empty or missing:
        raise ValueError(f"Built source lacks Western ReEDS zone coverage: {missing}")
    if western[["reeds_state", "reeds_zone", "LAF_state"]].isna().any().any():
        raise ValueError("Western bus geography or LAF_state is missing")
    laf = np.asarray(western["LAF_state"], dtype=float)
    if not np.isfinite(laf).all() or (laf < 0).any():
        raise ValueError("Western buses contain invalid LAF_state")
    return {
        "network_sha256": hashlib.file_digest(network_path.open("rb"), "sha256").hexdigest(),
        "official_membership_sha256": hashlib.sha256(membership_path.read_bytes()).hexdigest(),
        "western_zones_expected": len(required),
        "western_zones_observed": len(observed),
        "western_bus_count": len(western),
        "states_observed": sorted(western["reeds_state"].astype(str).unique().tolist()),
        "laf_state_present": True,
        "annual_demand_or_dispatch_validated": False,
        "geographic_laf_derivation_independently_verified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = inspect_built_network(args.network, args.membership)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
