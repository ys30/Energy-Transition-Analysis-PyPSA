"""Derive state-to-ReEDS weights from an actual PyPSA-USA bus LAF_state inventory.

Requires an externally obtained, source-identifiable network. No regional
membership, line capacities or guessed population proxies are used as weights.
A derived file is still subject to independent provenance review.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np


def derive_state_zone_weights(buses: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    needed = {"reeds_state", "reeds_zone", "LAF_state"}
    if not needed.issubset(buses.columns):
        raise ValueError(f"PyPSA bus inventory missing {sorted(needed - set(buses.columns))}")
    targets = mapping["state_to_all_membership_zones"]
    if not targets:
        raise ValueError("Empty ReEDS state-zone membership")
    df = buses.loc[:, ["reeds_state", "reeds_zone", "LAF_state"]].copy()
    if df.isna().any().any():
        raise ValueError("Missing state, zone or LAF_state in source buses")
    df["LAF_state"] = pd.to_numeric(df["LAF_state"], errors="raise")
    values = df["LAF_state"].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Invalid source LAF_state values")
    observed = set(zip(df["reeds_state"].astype(str), df["reeds_zone"].astype(str)))
    allowed = {(st, z) for st, zones in targets.items() for z in zones}
    if observed - allowed:
        raise ValueError(f"Source has unrecognized state-zone pairs: {sorted(observed - allowed)}")
    grouped = df.groupby(["reeds_state", "reeds_zone"])["LAF_state"].sum()
    if set(grouped.index.tolist()) != allowed:
        raise ValueError(f"Missing source state-zone pairs: {sorted(allowed - set(grouped.index.tolist()))}")
    result = grouped.rename("weight").reset_index().rename(
        columns={"reeds_state": "state", "reeds_zone": "zone"})
    sums = result.groupby("state")["weight"].sum()
    if set(sums.index) != set(targets):
        raise ValueError("Source state coverage differs from membership")
    if not np.allclose(sums.to_numpy(dtype=float), 1.0, rtol=0, atol=1e-6):
        raise ValueError(f"Original bus LAF_state fails state conservation: {sums.to_dict()}")
    return result.sort_values(["state", "zone"]).reset_index(drop=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True, help="Locally obtained PyPSA-USA network NetCDF")
    p.add_argument("--mapping", type=Path, required=True, help="Official audited membership JSON")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    import pypsa
    from .efs_zonal_weight_admission import validate_weights
    network = pypsa.Network(args.network)
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    weights = derive_state_zone_weights(network.buses, mapping)
    data = weights.to_csv(index=False).encode("utf-8")
    validate_weights(mapping, data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"Derived {len(weights)} zonal allocation rows from provided network; provenance not yet independently verified")


if __name__ == "__main__":
    main()
