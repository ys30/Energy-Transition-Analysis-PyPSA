"""Audit pinned EFS fixed-offset ordinal transforms, without claiming UTC provenance.

Mathematical compatibility with upstream code is not independent evidence that
original EFS LocalHourID is in a particular timezone or DST convention.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

SHIFTS = {"AZ": 7, "CA": 8, "CO": 7, "ID": 7, "MT": 7,
          "NM": 7, "NV": 8, "OR": 8, "UT": 7, "WA": 8, "WY": 7}
N = 8760


def forward(local_hour_id: int, offset: int) -> int:
    if not 1 <= local_hour_id <= N or offset not in (7, 8):
        raise ValueError("Invalid original ordinal or pinned offset")
    return (local_hour_id + offset - 1) % N + 1


def inverse(upstream_utc_hour_id: int, offset: int) -> int:
    if not 1 <= upstream_utc_hour_id <= N or offset not in (7, 8):
        raise ValueError("Invalid transformed ordinal or pinned offset")
    return (upstream_utc_hour_id - offset - 1) % N + 1


def audit():
    records = []
    for state, shift in sorted(SHIFTS.items()):
        transformed = [forward(i, shift) for i in range(1, N + 1)]
        if len(set(transformed)) != N:
            raise ValueError("Non-bijective pinned source transformation")
        if any(inverse(t, shift) != i for i, t in enumerate(transformed, start=1)):
            raise ValueError("Broken inverse pinned source transformation")
        records.append({
            "state": state, "pinned_fixed_offset_hours": shift,
            "source_ordinal_1_maps_to_pinned_utc_ordinal": forward(1, shift),
            "source_ordinal_8760_maps_to_pinned_utc_ordinal": forward(N, shift),
            "source_ordinal_at_wrap": N - shift + 1,
            "wrapped_utc_ordinal": forward(N - shift + 1, shift),
            "bijection_checked_hours": N,
            "source_hour_timezone_verified": False,
        })
    return {
        "status": "UPSTREAM_MATHEMATICAL_COMPATIBILITY_ONLY",
        "upstream_pinned_commit": "338af9912addbaf038c6098fe27e1e6ef099d8aa",
        "state_count": len(records),
        "states": records,
        "original_EFS_LocalHourID_to_archived_sequence_identity_verified": False,
        "actual_UTC_hourly_source_provenance_verified": False,
        "DST_convention_verified": False,
        "synchronous_OPF_admitted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "state_count": result["state_count"]}))


if __name__ == "__main__":
    main()
