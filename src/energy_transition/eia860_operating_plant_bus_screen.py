"""Cross-check geographic plant candidates with official EIA-860 operating generators.

A geographic candidate is never a verified electrical connection. Do not
interpret operating nameplate as hourly available generation.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def audit(candidates_path: Path, generators_path: Path, out: Path):
    c = pd.read_csv(candidates_path, dtype={"plant_id": "string", "nearest_candidate_bus": "string"})
    g = pd.read_csv(generators_path, dtype={"plant_id": "string", "generator_id": "string"})
    needed_c = {"plant_id", "state", "nearest_candidate_bus", "distance_km",
                "assignment_status", "electrical_connection_verified"}
    needed_g = {"plant_id", "generator_id", "state", "capacity_mw", "status",
                "crosswalk_status", "ba_code"}
    if needed_c - set(c) or needed_g - set(g):
        raise ValueError(f"Missing columns: candidate={sorted(needed_c-set(c))} generator={sorted(needed_g-set(g))}")
    if c.empty or g.empty:
        raise ValueError("Empty candidate or generator inventory")
    if c.plant_id.isna().any() or c.plant_id.duplicated().any() or c.nearest_candidate_bus.isna().any():
        raise ValueError("Missing or duplicate plant candidate identifiers")
    if g[["plant_id", "generator_id"]].isna().any().any() or g.duplicated(["plant_id", "generator_id"]).any():
        raise ValueError("Missing or duplicate EIA860 plant/generator identifiers")
    candidate_flags = c.electrical_connection_verified.astype("string").str.strip().str.lower()
    if not c.assignment_status.eq("geographic_candidate_only").all() or not candidate_flags.eq("false").all():
        raise ValueError("Geographic candidates cannot be treated as verified connections")
    g["capacity_mw"] = pd.to_numeric(g.capacity_mw, errors="coerce")
    g["operating"] = g.status.astype("string").str.strip().str.upper().eq("OP")
    g["ba_matched"] = g.crosswalk_status.astype("string").str.strip().str.lower().eq("matched")
    g["valid_nameplate"] = g.capacity_mw.notna() & g.capacity_mw.ge(0)
    g["eligible_for_screen"] = g.operating & g.ba_matched & g.valid_nameplate
    g["state"] = g.state.astype("string").str.upper().str.strip()
    c["state"] = c.state.astype("string").str.upper().str.strip()
    op = g[g.eligible_for_screen].copy()
    if op.empty:
        raise ValueError("No OP generators with matched BA and valid nameplate")
    disagreements = op.merge(c[["plant_id", "state"]], on="plant_id", how="inner",
                             suffixes=("_generator", "_candidate"))
    disagree = disagreements.state_generator.ne(disagreements.state_candidate).fillna(True)
    if disagree.any():
        raise ValueError("EIA860 generator state disagrees with EIA860 plant coordinate state")
    groups = op.groupby("plant_id").agg(
        operating_generator_count=("generator_id", "size"),
        operating_nameplate_mw=("capacity_mw", "sum"),
        ba_count=("ba_code", "nunique"),
    )
    if groups.ba_count.gt(1).any():
        raise ValueError("Conflicting BA codes on an operating plant")
    group_ba = op.groupby("plant_id").ba_code.first()
    groups["ba_code"] = group_ba
    groups = groups.drop(columns="ba_count")
    result = c.merge(groups, left_on="plant_id", right_index=True, how="left", validate="one_to_one")
    result["has_qualified_operating_generator"] = result.operating_generator_count.notna()
    result["operating_generator_count"] = result.operating_generator_count.fillna(0).astype(int)
    result["operating_nameplate_mw"] = result.operating_nameplate_mw.fillna(0.0)
    result["electrical_connection_verified"] = False
    result["ready_for_real_generator_injection"] = False
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    covered = result.has_qualified_operating_generator
    matched_ids = set(result.loc[covered, "plant_id"].astype(str))
    uncovered_op = op.loc[~op.plant_id.isin(matched_ids)]
    report = {
        "candidate_plants_all_statuses": int(len(c)),
        "candidate_plants_with_qualified_op_generator": int(covered.sum()),
        "candidate_plants_without_qualified_op_generator": int((~covered).sum()),
        "qualified_operating_generator_rows_all_states": int(len(op)),
        "qualified_operating_generator_rows_on_candidate_plants": int(result.operating_generator_count.sum()),
        "qualified_operating_nameplate_mw_on_candidate_plants": float(result.operating_nameplate_mw.sum()),
        "qualified_operating_nameplate_mw_without_candidate": float(uncovered_op.capacity_mw.sum()),
        "candidate_op_plants_over_50km": int((covered & pd.to_numeric(result.distance_km,errors="coerce").gt(50)).sum()),
        "approved_electrical_connections": 0,
        "full_western_opf_ready": False,
        "limitations": "Plant-level candidate screening for status=OP and BA-matched EIA860 units only. Not an official POI, a historical hourly capacity factor, nor a future 2030/2040/2050 generation fleet.",
    }
    out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidates",type=Path,required=True)
    parser.add_argument("--generators",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    audit(a.candidates,a.generators,a.out)


if __name__=="__main__":
    main()
