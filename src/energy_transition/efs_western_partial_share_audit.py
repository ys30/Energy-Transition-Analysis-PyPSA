"""Gate EFS-to-ReEDS zonal allocation against proven external weights.

Do not treat ReEDS membership counts, equal division, or bus counts as LAF.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def audit(weights: Path, expected_states: set[str]) -> dict:
    with weights.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"state", "reeds_zone", "weight"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Weights need state,reeds_zone,weight columns")
        by_state = defaultdict(float)
        count = defaultdict(int)
        for row in reader:
            state = row["state"].strip()
            zone = row["reeds_zone"].strip()
            if not state or not zone:
                raise ValueError("Empty weight geography")
            w = float(row["weight"])
            if not (0 <= w <= 1):
                raise ValueError("Invalid weight")
            by_state[state] += w
            count[state] += 1
    missing = sorted(expected_states - set(by_state))
    invalid = sorted(s for s, total in by_state.items() if total > 1.000001)
    # For split-interconnect states, a Western-only allocation often sums below 1.
    if missing or invalid:
        raise ValueError(f"Missing source states: {missing}; excess mass: {invalid}")
    return {
        "states_with_weights": sorted(by_state),
        "state_western_allocation_fraction": dict(sorted(by_state.items())),
        "zone_weight_counts": dict(sorted(count.items())),
        "full_state_conservation_implied": False,
        "external_empirical_weights_verified": False,
        "note": "Numerical mass check only. This cannot certify geographic provenance or empirical LAF.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weights",type=Path,required=True)
    p.add_argument("--states",nargs="+",required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.weights,set(a.states))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
