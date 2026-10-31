"""Validate externally sourced state-to-zone demand shares before empirical dispatch.

This module intentionally does not infer weights from categorical membership.
Input CSV columns: state,zone,weight,source. Each state must be complete and sum
to one; source must identify independent evidence for the numeric allocation.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def validate_weights(mapping_report: dict, weight_rows: list[dict]) -> dict:
    expected = mapping_report["state_to_network_zones"]
    if mapping_report.get("unmatched_membership_zones"):
        raise ValueError("Unmatched upstream zones require explicit coverage decision")
    by_state: dict[str, dict[str, float]] = defaultdict(dict)
    sources: dict[str, set[str]] = defaultdict(set)
    for row in weight_rows:
        state, zone = row["state"].strip(), row["zone"].strip()
        source = row["source"].strip()
        if not source or source.lower() in {"unknown", "assumed", "equal", "synthetic"}:
            raise ValueError(f"Missing independent allocation evidence: {state}/{zone}")
        if state not in expected or zone not in expected[state]:
            raise ValueError(f"Unrecognized state/zone: {state}/{zone}")
        if zone in by_state[state]:
            raise ValueError(f"Duplicate allocation: {state}/{zone}")
        weight = float(row["weight"])
        if not math.isfinite(weight) or weight < 0 or weight > 1:
            raise ValueError(f"Invalid weight: {state}/{zone}")
        by_state[state][zone] = weight
        sources[state].add(source)
    for state, zones in expected.items():
        if set(by_state[state]) != set(zones):
            raise ValueError(f"Incomplete allocation for {state}: expected {sorted(zones)}, got {sorted(by_state[state])}")
        if abs(sum(by_state[state].values()) - 1) > 1e-6:
            raise ValueError(f"Shares do not sum to one for {state}")
    return {"states": len(expected), "zones": sum(map(len, expected.values())),
            "allocation_weights_validated": True,
            "sources_by_state": {k: sorted(v) for k, v in sorted(sources.items())},
            "note": "Source labels are supplied by data provider; provenance still requires independent verification"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mapping", type=Path, required=True)
    p.add_argument("--weights", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    mapping = json.loads(args.mapping.read_text())
    with args.weights.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {"state", "zone", "weight", "source"} <= set(reader.fieldnames):
            raise ValueError("Expected CSV columns: state,zone,weight,source")
        result = validate_weights(mapping, list(reader))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
