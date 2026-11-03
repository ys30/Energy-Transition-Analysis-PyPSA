"""Extract candidate ReEDS-zone EFS demand weights from source-network LAF_state.

PyPSA-USA defines LAF_state = bus Pd / full-state Pd. We must NOT
renormalize Western-only partial states to 100%, or fabricate population
weights when source LAFs are absent. Numeric acceptance is not independent
empirical provenance confirmation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def candidate_weights(buses: pd.DataFrame, *, tolerance: float = 1e-6):
    required = {"reeds_state", "reeds_zone", "LAF_state"}
    if not required.issubset(buses.columns):
        raise ValueError(f"Source bus attributes missing: {sorted(required - set(buses.columns))}")
    if buses.empty or buses.index.has_duplicates:
        raise ValueError("Missing or duplicated source bus identities")
    data = buses.loc[:, ["reeds_state", "reeds_zone", "LAF_state"]].copy()
    if data.isna().any().any():
        raise ValueError("Missing LAF, state, or ReEDS zone in source buses")
    for key in ("reeds_state", "reeds_zone"):
        data[key] = data[key].astype(str).str.strip()
        if data[key].eq("").any():
            raise ValueError(f"Blank source {key}")
    data["LAF_state"] = pd.to_numeric(data["LAF_state"], errors="raise")
    vals = data["LAF_state"].to_numpy(dtype=float)
    if not np.isfinite(vals).all() or (vals < 0).any() or (vals > 1 + tolerance).any():
        raise ValueError("Invalid source bus LAF_state")
    # Each zone must have one and only one source state.
    owners = data.groupby("reeds_zone")["reeds_state"].nunique()
    if (owners > 1).any():
        raise ValueError("ReEDS zone assigned to multiple states")
    sums = data.groupby("reeds_state")["LAF_state"].sum()
    partial = {str(s): float(v) for s,v in sums.items() if abs(float(v) - 1) > tolerance}
    if partial:
        raise ValueError(
            f"Full-state LAF coverage not proven (possibly outside-Western buses): {partial}. "
            "Do not re-normalize incomplete state footprints."
        )
    zone = (data.groupby(["reeds_state", "reeds_zone"], as_index=False)["LAF_state"]
            .sum().rename(columns={"reeds_state": "state",
                                   "reeds_zone": "zone", "LAF_state": "weight"}))
    zone = zone.sort_values(["state", "zone"], kind="stable").reset_index(drop=True)
    if (zone["weight"] < 0).any() or not np.isfinite(zone["weight"].to_numpy()).all():
        raise ValueError("Invalid zonal LAF aggregation")
    return zone, {
        "source_bus_count": int(len(data)),
        "covered_states": int(len(sums)),
        "reeds_zone_pairs": int(len(zone)),
        "raw_state_laf_sums": {str(k): float(v) for k,v in sums.items()},
        "no_renormalization_performed": True,
        "state_laf_conservation_verified": True,
        "candidate_numeric_weights_generated": True,
        "independent_geographic_source_provenance_verified": False,
        "admitted_for_empirical_dispatch": False,
        "note": "Requires upstream network revision, LAF method and coverage source verification before empirical use.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--weights", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    import pypsa
    network = pypsa.Network(args.network)
    weights, report = candidate_weights(network.buses)
    args.weights.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    weights.to_csv(args.weights, index=False, float_format="%.17g")
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
