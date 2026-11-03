"""Prioritize EIA860 operating-plant geographic bus candidates for POI evidence review.

Distances are geographic screening only. No score grants electrical approval.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def audit(screen: Path, out: Path):
    df = pd.read_csv(screen, dtype={"plant_id": "string", "nearest_candidate_bus": "string"})
    needed = {"plant_id", "state", "nearest_candidate_bus", "distance_km",
              "operating_generator_count", "operating_nameplate_mw",
              "has_qualified_operating_generator", "electrical_connection_verified",
              "ready_for_real_generator_injection"}
    if needed - set(df):
        raise ValueError(f"Missing required screening fields: {sorted(needed-set(df))}")
    if df.empty or df.plant_id.isna().any() or df.plant_id.duplicated().any():
        raise ValueError("Invalid or empty plant identities")
    for col in ("distance_km", "operating_generator_count", "operating_nameplate_mw"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any() or not np.isfinite(df[col]).all() or df[col].lt(0).any():
            raise ValueError(f"Invalid {col}")
    if not df.operating_generator_count.mod(1).eq(0).all():
        raise ValueError("Noninteger generator count")
    op = df.has_qualified_operating_generator.astype("string").str.lower().eq("true")
    if op.isna().any() or ((df.operating_generator_count.gt(0)) != op).any():
        raise ValueError("Operating generator coverage flag inconsistent with generator counts")
    for col in ("electrical_connection_verified", "ready_for_real_generator_injection"):
        if not df[col].astype("string").str.lower().eq("false").all():
            raise ValueError("Geographic matches must not be approved for electrical injection")
    df = df.loc[op].copy()
    if df.empty:
        raise ValueError("No eligible operating plants")
    df["distance_band"] = pd.cut(
        df.distance_km, [-0.001, 1, 5, 10, 25, 50, float("inf")],
        labels=["0-1", "1-5", "5-10", "10-25", "25-50", ">50"])
    df["requires_long_distance_review"] = df.distance_km.gt(50)
    df["evidence_priority"] = "standard_unverified"
    df.loc[df.requires_long_distance_review, "evidence_priority"] = "long_distance_unverified"
    df = df.sort_values(
        ["requires_long_distance_review", "operating_nameplate_mw", "distance_km", "plant_id"],
        ascending=[False, False, False, True])
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    far = df[df.requires_long_distance_review]
    far.to_csv(out.with_name(out.stem + "_over50km.csv"), index=False)
    bands = (df.groupby("distance_band", observed=True, dropna=False)
               .agg(operating_plants=("plant_id", "size"),
                    operating_generators=("operating_generator_count", "sum"),
                    nameplate_mw=("operating_nameplate_mw", "sum"))
               .reset_index())
    bands.to_csv(out.with_name(out.stem + "_distance_bands.csv"), index=False)
    total = float(df.operating_nameplate_mw.sum())
    far_mw = float(far.operating_nameplate_mw.sum())
    report = {
        "screened_operating_plants": int(len(df)),
        "screened_operating_generators": int(df.operating_generator_count.sum()),
        "screened_operating_nameplate_mw": total,
        "operating_plants_over_50km": int(len(far)),
        "operating_nameplate_mw_over_50km": far_mw,
        "operating_nameplate_fraction_over_50km": far_mw / total if total else None,
        "distance_band_counts": {str(r.distance_band): int(r.operating_plants) for r in bands.itertuples()},
        "electrical_connections_verified": 0,
        "dispatch_ready": False,
        "warning": "Evidence review priority only; no POI or electrical network connection certified.",
    }
    out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--screen", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    z = a.parse_args()
    audit(z.screen, z.out)


if __name__ == "__main__":
    main()
