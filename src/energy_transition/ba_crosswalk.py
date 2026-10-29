"""Validate an externally verified EIA plant-to-balancing-authority crosswalk.

Do NOT derive BA membership from state alone. Requires a documented input CSV
with plant_id, ba_code; no implicit matching or synthetic affiliation.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def normalize_plant_id(series):
    return series.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)

def join_verified_crosswalk(generators, crosswalk):
    needed_gen = {"plant_id", "generator_id", "capacity_mw", "status"}
    needed_x = {"plant_id", "ba_code"}
    if needed_gen - set(generators) or needed_x - set(crosswalk):
        raise ValueError("Missing required generator or crosswalk columns")
    g = generators.copy()
    x = crosswalk.copy()
    g["plant_id"] = normalize_plant_id(g["plant_id"])
    x["plant_id"] = normalize_plant_id(x["plant_id"])
    x["ba_code"] = x["ba_code"].astype("string").str.strip().str.upper()
    if x.plant_id.isna().any() or x.ba_code.isna().any() or x.ba_code.eq("").any():
        raise ValueError("Crosswalk contains invalid plant or BA identifiers")
    if x.duplicated("plant_id").any():
        raise ValueError("Crosswalk contains ambiguous duplicate plant-to-BA assignments")
    joined = g.merge(x[["plant_id", "ba_code"]], on="plant_id", how="left", validate="many_to_one", indicator=True)
    joined["crosswalk_status"] = joined["_merge"].map({"both": "matched", "left_only": "unmatched"})
    return joined.drop(columns="_merge")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--generators", type=Path, required=True)
    p.add_argument("--crosswalk", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("outputs/ba_mapping"))
    p.add_argument("--operating-only", action="store_true", help="Restrict dispatch input to status OP")
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    frame = join_verified_crosswalk(pd.read_csv(a.generators), pd.read_csv(a.crosswalk))
    frame.to_csv(a.output / "generator_ba_join_audit.csv", index=False)
    mapped = frame.loc[frame.crosswalk_status.eq("matched")].copy()
    if a.operating_only:
        mapped = mapped.loc[mapped.status.eq("OP")].copy()
    mapped.to_csv(a.output / "mapped_generators.csv", index=False)
    cap = mapped.groupby(["ba_code", "fuel"], as_index=False).capacity_mw.sum()
    cap.to_csv(a.output / "ba_capacity_by_fuel.csv", index=False)
    report = {"records": len(frame), "matched": int(frame.crosswalk_status.eq("matched").sum()),
              "unmatched": int(frame.crosswalk_status.eq("unmatched").sum()),
              "included_capacity_mw": float(mapped.capacity_mw.sum()),
              "operating_only": a.operating_only,
              "warning": "Only use externally documented plant-to-BA crosswalks. No unverified geographic inference."}
    (a.output / "crosswalk_manifest.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
