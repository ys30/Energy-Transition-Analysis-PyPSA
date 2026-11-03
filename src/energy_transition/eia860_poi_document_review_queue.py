"""Create finite, auditable POI-document review queues for 2024 operating plants.

Geographic candidates remain unverified, regardless of proximity. This exports
investigation priorities, not approved physical connections or dispatch supply.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def audit(screen_path: Path, out_dir: Path, top_n: int = 20):
    if top_n < 1:
        raise ValueError("top_n must be positive")
    d = pd.read_csv(screen_path, dtype={"plant_id": "string", "nearest_candidate_bus": "string", "ba_code": "string"})
    required = {"plant_id", "ba_code", "state", "nearest_candidate_bus", "distance_km",
                "operating_generator_count", "operating_nameplate_mw",
                "has_qualified_operating_generator", "electrical_connection_verified",
                "ready_for_real_generator_injection"}
    if required-set(d):
        raise ValueError(f"Missing screening columns: {sorted(required-set(d))}")
    if d.empty or d.plant_id.isna().any() or d.plant_id.duplicated().any():
        raise ValueError("Empty or duplicate plant inventory")
    for k in ("distance_km", "operating_nameplate_mw", "operating_generator_count"):
        d[k] = pd.to_numeric(d[k], errors="coerce")
        if d[k].isna().any() or not np.isfinite(d[k]).all() or d[k].lt(0).any():
            raise ValueError(f"Invalid {k}")
    eligible = d.has_qualified_operating_generator.astype("string").str.lower()
    if not eligible.isin(["true", "false"]).all():
        raise ValueError("Invalid operating status flag")
    if not ((d.operating_generator_count.gt(0)) == eligible.eq("true")).all():
        raise ValueError("Inconsistent OP generator counts")
    for k in ("electrical_connection_verified", "ready_for_real_generator_injection"):
        if not d[k].astype("string").str.lower().eq("false").all():
            raise ValueError("No geographic candidate may be treated as an approved connection")
    op = d.loc[eligible.eq("true")].copy()
    if op.empty or op.ba_code.isna().any() or op.state.isna().any():
        raise ValueError("Missing operating plants or source BA/state")
    op["needs_independent_poi_evidence"] = True
    op["electrical_connection_verified"] = False
    op["eligible_for_empirical_dispatch"] = False
    op["geographic_distance_over_50km"] = op.distance_km.gt(50)
    if "plant_name" not in op:
        op["plant_name"] = pd.NA
    cols = ["plant_id", "plant_name", "ba_code", "state", "nearest_candidate_bus", "distance_km",
            "operating_generator_count", "operating_nameplate_mw",
            "geographic_distance_over_50km", "needs_independent_poi_evidence",
            "electrical_connection_verified", "eligible_for_empirical_dispatch"]
    ranked = op.sort_values(["operating_nameplate_mw", "distance_km", "plant_id"],
                            ascending=[False, False, True])
    long_distance = op.loc[op.geographic_distance_over_50km].sort_values(
        ["operating_nameplate_mw", "distance_km", "plant_id"], ascending=[False,False,True])
    by_ba = (op.groupby(["ba_code", "state"], as_index=False)
             .agg(plants=("plant_id","size"), generators=("operating_generator_count","sum"),
                  operating_nameplate_mw=("operating_nameplate_mw","sum"),
                  long_distance_plants=("geographic_distance_over_50km","sum"))
             .sort_values("operating_nameplate_mw",ascending=False))
    out_dir.mkdir(parents=True,exist_ok=True)
    ranked[cols].head(top_n).to_csv(out_dir/"top_operating_plant_poi_review.csv",index=False)
    long_distance[cols].head(top_n).to_csv(out_dir/"top_long_distance_operating_plant_poi_review.csv",index=False)
    by_ba.to_csv(out_dir/"operating_poi_review_by_ba_state.csv",index=False)
    result={
        "source_operating_plants":int(len(op)),
        "source_operating_generator_count":int(op.operating_generator_count.sum()),
        "source_operating_nameplate_mw":float(op.operating_nameplate_mw.sum()),
        "long_distance_plants":int(len(long_distance)),
        "long_distance_nameplate_mw":float(long_distance.operating_nameplate_mw.sum()),
        "top_capacity_review_rows":int(min(top_n,len(ranked))),
        "top_long_distance_review_rows":int(min(top_n,len(long_distance))),
        "top_capacity_review_nameplate_mw":float(ranked.head(top_n).operating_nameplate_mw.sum()),
        "top_long_distance_review_nameplate_mw":float(long_distance.head(top_n).operating_nameplate_mw.sum()),
        "ba_state_groups":int(len(by_ba)),
        "source_capacity_reconciles_with_ba_state_groups":bool(
            abs(float(by_ba.operating_nameplate_mw.sum())-float(op.operating_nameplate_mw.sum()))<1e-5),
        "independent_poi_document_review_performed":False,
        "electrical_connections_verified":0,
        "empirical_opf_ready":False,
        "warning":"Ranking is for collecting independent POI documents; no geographic association proves an electrical connection.",
    }
    (out_dir/"operating_plant_poi_review_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--screen",type=Path,required=True)
    parser.add_argument("--out-dir",type=Path,required=True)
    parser.add_argument("--top-n",type=int,default=20)
    args=parser.parse_args()
    audit(args.screen,args.out_dir,args.top_n)


if __name__=="__main__":
    main()
