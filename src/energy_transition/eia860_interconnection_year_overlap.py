"""Deduplicate year-specific EIA-860 interconnection-review queues by plant ID.

This is an evidence-only tracking table, never a generator-bus interconnection approval.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def merge_queues(p2023, p2024, out):
    files = {2023: p2023, 2024: p2024}
    frames = []
    for year, path in files.items():
        d = pd.read_csv(path, dtype={"plant_id": "string", "nearest_candidate_bus": "string"})
        required = {"plant_id", "distance_km", "long_distance",
                    "material_grid_candidate_change", "electrical_connection_verified",
                    "eligible_for_real_dispatch", "priority_reason"}
        if required - set(d.columns):
            raise ValueError(f"{year} missing required queue columns")
        if d.plant_id.isna().any() or d.plant_id.duplicated().any():
            raise ValueError(f"{year} has duplicate or null plant identifiers")
        for flag in ("long_distance", "material_grid_candidate_change",
                     "electrical_connection_verified", "eligible_for_real_dispatch"):
            values = d[flag].astype("string").str.lower().str.strip()
            if values.isna().any() or not values.isin({"true", "false"}).all():
                raise ValueError(f"{year} has malformed {flag}")
            d[flag] = values.eq("true")
        if d.electrical_connection_verified.any() or d.eligible_for_real_dispatch.any():
            raise ValueError(f"{year} includes unverified approved electrical ties")
        d["distance_km"] = pd.to_numeric(d.distance_km, errors="coerce")
        if d.distance_km.isna().any() or not d.distance_km.map(__import__("math").isfinite).all() or d.distance_km.lt(0).any():
            raise ValueError(f"{year} contains invalid distances")
        if not (d.long_distance | d.material_grid_candidate_change).all():
            raise ValueError(f"{year} contains non-priority entries")
        d["year"] = year
        frames.append(d)
    combined = pd.concat(frames, ignore_index=True)
    records = []
    for plant_id, group in combined.groupby("plant_id", sort=True):
        a = group.loc[group.year.eq(2023)]
        b = group.loc[group.year.eq(2024)]
        records.append({
            "plant_id": str(plant_id),
            "review_2023": not a.empty,
            "review_2024": not b.empty,
            "review_both_years": not a.empty and not b.empty,
            "reason_2023": a.priority_reason.iloc[0] if not a.empty else "",
            "reason_2024": b.priority_reason.iloc[0] if not b.empty else "",
            "distance_km_2023": float(a.distance_km.iloc[0]) if not a.empty else None,
            "distance_km_2024": float(b.distance_km.iloc[0]) if not b.empty else None,
            "candidate_bus_2023": str(a.nearest_candidate_bus.iloc[0]) if not a.empty else "",
            "candidate_bus_2024": str(b.nearest_candidate_bus.iloc[0]) if not b.empty else "",
            "electrical_connection_verified": False,
            "eligible_for_real_dispatch": False,
        })
    result = pd.DataFrame(records)
    if result.empty:
        raise ValueError("No priority plants in either year")
    result = result.sort_values(["review_both_years", "plant_id"], ascending=[False, True])
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    # Actionable files, preserving the original ID-level provenance.
    persistent = result.loc[result.review_both_years].copy()
    persistent.to_csv(out.with_name(out.stem + "_persistent.csv"), index=False)
    year_specific = result.loc[~result.review_both_years].copy()
    year_specific.to_csv(out.with_name(out.stem + "_year_specific.csv"), index=False)
    if len(persistent) + len(year_specific) != len(result):
        raise ValueError("Cross-year partition does not reconcile")

    report = {
        "unique_priority_plant_ids": len(result),
        "year_2023_records": len(frames[0]),
        "year_2024_records": len(frames[1]),
        "review_both_years": int(result.review_both_years.sum()),
        "persistent_review_fraction_of_unique": float(result.review_both_years.mean()),
        "only_2023": int((result.review_2023 & ~result.review_2024).sum()),
        "only_2024": int((~result.review_2023 & result.review_2024).sum()),
        "electrical_connections_verified": 0,
        "real_generator_dispatch_approved": False,
        "note": "Year-specific priority lists are not independent plants; matched plant IDs are deduplicated.",
    }
    out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue-2023", type=Path, required=True)
    p.add_argument("--queue-2024", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    merge_queues(a.queue_2023, a.queue_2024, a.out)


if __name__ == "__main__":
    main()
