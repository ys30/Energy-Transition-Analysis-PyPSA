"""Audit the real NLR EFS CSV without assuming a particular demand schema.

Streams a sample and records header, source checksum and calendar hints; this
is an input-discovery report, not a conversion to state-hour load.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def inspect(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("Missing or empty EFS source CSV")
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        sample = [row for _, row in zip(range(4), reader)]
    if not header or len(header) != len(set(header)):
        raise ValueError("Empty or duplicate EFS header")
    if any(len(row) != len(header) for row in sample):
        raise ValueError("EFS sample width inconsistent with header")
    with path.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": digest,
        "columns": header,
        "sample_rows": sample,
        "source_download_completed": True,
        "year_coverage_verified": False,
        "state_coverage_verified": False,
        "hourly_semantics_verified": False,
        "western_demand_admitted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
