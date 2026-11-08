"""Derive marginal battery-duration effects from original archived 540 cyclic LP cases.

No rounded Markdown inputs; checks source coverage and objective identities first.
Results are illustrative independent-zone LP comparisons, not economic returns.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .paper_s_lp_objective_certification import audit

METRICS = {
    "unused_renewable_mwh": "unused_renewable_mwh",
    "firm_generation_mwh": "firm_generation_mwh",
    "objective_illustrative_variable_usd": "objective_illustrative_variable_usd",
}
KEY = ["planning_year", "synthetic_supply_shape"]
DURATIONS = (0, 4, 8)


def derive(cases: pd.DataFrame) -> pd.DataFrame:
    """Return 9 sourced year/shape comparisons; no partial/duplicate inputs allowed."""
    audit(cases)
    # Every zone must have every supply-shape/duration cell, not just a global total.
    zone_keys = ["planning_year", "state", "reeds_zone"]
    for _, group in cases.groupby(zone_keys):
        if len(group) != 9 or len(group[["synthetic_supply_shape", "battery_duration_h"]].drop_duplicates()) != 9:
            raise ValueError("Incomplete within-zone supply shape/duration grid")
    if cases.synthetic_supply_shape.nunique() != 3:
        raise ValueError("Expected exactly three synthetic supply shapes")
    if not np.isfinite(cases[list(METRICS)].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite marginal inputs")
    summary = cases.groupby(KEY + ["battery_duration_h"], as_index=False)[list(METRICS)].sum()
    if len(summary) != 27:
        raise ValueError("Expected 27 annual summary rows")
    out = []
    for (year, shape), g in summary.groupby(KEY):
        g = g.set_index("battery_duration_h")
        if set(g.index) != set(DURATIONS):
            raise ValueError("Duration grid missing")
        row = {"planning_year": int(year), "synthetic_supply_shape": str(shape),
               "scope": "source EFS demand + synthetic supply, independent zones",
               "source_ordinal_hours_per_case": 8760, "zones": 20}
        for source_col, label in METRICS.items():
            at = [float(g.loc[d, source_col]) for d in DURATIONS]
            reduction_04 = at[0] - at[1]
            reduction_48 = at[1] - at[2]
            row[f"{label}_0h"] = at[0]
            row[f"{label}_4h"] = at[1]
            row[f"{label}_8h"] = at[2]
            row[f"{label}_reduction_0to4h"] = reduction_04
            row[f"{label}_reduction_4to8h"] = reduction_48
            row[f"{label}_increment_ratio_4to8_over_0to4"] = (
                reduction_48 / reduction_04 if abs(reduction_04) > 1e-8 else np.nan
            )
        out.append(row)
    result = pd.DataFrame(out).sort_values(KEY).reset_index(drop=True)
    assert len(result) == 9
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cases", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    rows = derive(pd.read_csv(a.cases))
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(a.out_csv, index=False, float_format="%.12g")
    report = {
        "status": "MARGINAL_DURATION_ARCHIVED_540_CASES_VERIFIED",
        "source_rows": 540, "annual_comparisons": len(rows), "source_years": [2030, 2040, 2050],
        "hypothetical_supply_shapes": sorted(rows.synthetic_supply_shape.tolist()[0:0] + rows.synthetic_supply_shape.unique().tolist()),
        "duration_hours": list(DURATIONS), "zone_count": 20,
        "source_clock_UTC_certified": False, "actual_renewable_profiles": False,
        "western_transmission_constrained_opf": False,
        "storage_capex_included": False,
        "interpretation": "Toy variable-objective marginal reductions, not net savings or optimal duration",
    }
    a.out_json.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
