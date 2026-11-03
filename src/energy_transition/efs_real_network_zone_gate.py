"""Preflight EFS allocation zones against a built-network zone crosswalk.

This allows partial state weights for screening only. It does not authenticate
LAF provenance, enforce full state conservation, or attach hourly demand.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def _read_rows(path: Path, required: set[str], description: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"Invalid {description} columns")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Duplicate {description} columns")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Empty {description}")
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Malformed {description} row")
        if any(not row[name].strip() for name in required):
            raise ValueError(f"Blank {description} field")
    return rows


def validate(bus_crosswalk: Path, weights: Path) -> dict:
    buses = _read_rows(
        bus_crosswalk, {"state", "reeds_zone", "bus_count"}, "real-network crosswalk"
    )
    allowed = set()
    zone_owners = {}
    for row in buses:
        key = (row["state"].strip(), row["reeds_zone"].strip())
        if key in allowed:
            raise ValueError(f"Duplicate real-network zone: {key}")
        allowed.add(key)
        owner = zone_owners.setdefault(key[1], key[0])
        if owner != key[0]:
            raise ValueError(f"Network zone assigned to multiple states: {key[1]}")
        try:
            count = int(row["bus_count"])
        except ValueError as exc:
            raise ValueError(f"Invalid bus_count for {key}") from exc
        if count <= 0:
            raise ValueError(f"Invalid bus_count for {key}")

    rows = _read_rows(weights, {"state", "reeds_zone", "weight"}, "EFS LAF")
    missing = sorted(
        {(r["state"].strip(), r["reeds_zone"].strip()) for r in rows} - allowed
    )
    if missing:
        raise ValueError(f"LAF includes zones absent from real network: {missing}")
    state_total = defaultdict(float)
    pairs = set()
    for row in rows:
        key = (row["state"].strip(), row["reeds_zone"].strip())
        if key in pairs:
            raise ValueError(f"Duplicate allocation zone: {key}")
        pairs.add(key)
        try:
            weight = float(row["weight"])
        except ValueError as exc:
            raise ValueError(f"Invalid LAF share: {key}") from exc
        if not math.isfinite(weight) or not 0 <= weight <= 1:
            raise ValueError(f"Invalid LAF share: {key}")
        state_total[key[0]] += weight
    excess = {state: total for state, total in state_total.items() if total > 1.000001}
    if excess:
        raise ValueError(f"Overallocation: {excess}")
    return {
        "real_bus_zone_pairs": len(allowed),
        "laf_pairs_checked": len(pairs),
        "state_weight_sums": dict(state_total),
        "all_laf_zones_in_real_network": True,
        "empirical_laf_provenance_confirmed": False,
        "hourly_efs_attached": False,
        "preflight_only_partial_state_weights_allowed": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus-crosswalk", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.bus_crosswalk, args.weights)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
