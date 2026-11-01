"""Audit pinned ReEDS Western membership against an EFS state-hour cohort.

This is a geography admission test, NOT a spatial disaggregation or approval
to assign full-state EFS demand to a partial-state interconnect.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

NON_US = {"AB", "BC", "MEX"}
CORE = {"AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY"}


def audit_membership(membership: Path) -> dict:
    rows = list(csv.DictReader(membership.open(newline="", encoding="utf-8-sig")))
    if not rows or not {"ba", "st", "interconnect", "st_interconnect"}.issubset(rows[0]):
        raise ValueError("Pinned ReEDS membership lacks expected provenance columns")
    by_state = defaultdict(lambda: {"western": [], "other": []})
    seen = set()
    for row in rows:
        key = row["ba"]
        if key in seen:
            raise ValueError(f"Duplicate ReEDS BA identifier: {key}")
        seen.add(key)
        state = row["st"]
        if row["interconnect"] == "western":
            by_state[state]["western"].append(key)
        else:
            by_state[state]["other"].append(key)
    west = sorted(state for state, counts in by_state.items() if counts["western"])
    partial = sorted(state for state in west if by_state[state]["other"])
    missing = sorted((set(west) - NON_US) - CORE)
    non_us = sorted(set(west) & NON_US)
    extras = sorted(CORE - set(west))
    return {
        "upstream": "PyPSA/pypsa-usa pinned v0.8.0 ReEDS_Constraints/membership.csv",
        "western_reeds_states": west,
        "western_us_states": sorted(set(west) - NON_US),
        "western_cross_border_regions": non_us,
        "western_cross_border_ba_count": sum(len(by_state[s]["western"]) for s in non_us),
        "western_reeds_ba_count": sum(len(by_state[s]["western"]) for s in west),
        "core_11_efs_pilot_states": sorted(CORE),
        "western_us_states_missing_from_core_efs_pilot": missing,
        "western_states_missing_from_core_efs_pilot": missing,
        "core_pilot_states_absent_from_western": extras,
        "states_split_across_interconnects": partial,
        "western_ba_by_state": {s: sorted(by_state[s]["western"]) for s in west},
        "all_state_efs_load_to_western_allowed": False,
        "laf_weights_empirically_verified": False,
        "note": "Membership includes Canada/Mexico cross-border regions without US EFS load; state coverage does not imply full-state Western shares for split states.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--membership", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = audit_membership(a.membership)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
