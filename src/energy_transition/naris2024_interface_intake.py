"""Fetch and validate published NARIS2024 BA interface capacities (not AC impedances)."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

SOURCE = "https://raw.githubusercontent.com/PyPSA/pypsa-usa/master/workflow/repo_data/ReEDS_Constraints/transmission/transmission_capacity_init_AC_ba_NARIS2024.csv"
COLUMNS = ("interface", "r", "rr", "MW_f0", "MW_r0", "MW_f1", "MW_r1")


def inspect_csv(data: bytes) -> dict:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise ValueError(f"Unexpected NARIS interface columns: {reader.fieldnames}")
    rows = list(reader)
    if not rows:
        raise ValueError("Empty NARIS interface dataset")
    seen = set()
    areas = set()
    zero_both = 0
    directional = 0
    for row in rows:
        a, b = row["r"].strip(), row["rr"].strip()
        if not a or not b or a == b or row["interface"] != f"{a}||{b}":
            raise ValueError(f"Invalid interface identifier: {row['interface']}")
        pair = (a, b)
        if pair in seen:
            raise ValueError(f"Duplicate interface: {pair}")
        seen.add(pair)
        areas.update(pair)
        values = []
        for key in COLUMNS[3:]:
            value = float(row[key])
            if not (0 <= value < float("inf")):
                raise ValueError(f"Invalid {key} on {pair}: {row[key]}")
            values.append(value)
        zero_both += values[0] == values[1] == 0
        directional += values[0] != values[1]
    return {
        "source": SOURCE,
        "sha256": hashlib.sha256(data).hexdigest(),
        "rows": len(rows),
        "regions": len(areas),
        "zero_capacity_both_directions": zero_both,
        "asymmetric_base_directional_capacity": directional,
        "capacity_units": "MW",
        "interpretation": "planning zonal interface limits; NOT physical AC Line impedances",
        "network_solved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with urlopen(SOURCE, timeout=40) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Unexpectedly large source")
    report = inspect_csv(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
