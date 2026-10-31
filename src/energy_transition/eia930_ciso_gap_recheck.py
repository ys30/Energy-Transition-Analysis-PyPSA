"""Re-query official EIA-930 NG and audit the verified CISO 24-hour gap.

This is a source-availability check, not evidence of a DST-related cause.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from .eia930_generation_audit import fetch_net_generation

GAP_START = pd.Timestamp("2024-11-02T08:00:00Z")
GAP_END = pd.Timestamp("2024-11-03T08:00:00Z")


def audit_gap(frame: pd.DataFrame) -> dict:
    expected = pd.date_range(GAP_START, GAP_END, freq="h", inclusive="left")
    observed = frame.loc[frame.respondent.eq("CISO")].copy()
    observed["period"] = pd.to_datetime(observed["period"], utc=True)
    inside = observed.loc[observed.period.isin(expected)]
    timestamps = pd.DatetimeIndex(inside.period)
    missing = expected.difference(timestamps)
    return {
        "ba": "CISO", "source_type": "EIA-930 NG",
        "window_start_utc": GAP_START.isoformat(),
        "window_end_exclusive_utc": GAP_END.isoformat(),
        "expected_hours": len(expected),
        "returned_timestamp_hours": len(inside),
        "returned_nonnull_hours": int(inside.value.notna().sum()),
        "returned_null_hours": int(inside.value.isna().sum()),
        "missing_timestamp_hours": len(missing),
        "missing_timestamps_utc": [t.isoformat() for t in missing],
        "negative_observation_hours": int((inside.value < 0).sum()),
        "interpretation": "Source availability only; DST causation is not established.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs/ciso_ng_gap_recheck.json"))
    args = parser.parse_args()
    # Independent fresh API retrieval; do not replace missing observations with zeros.
    frame = fetch_net_generation(2024, ["CISO"])
    report = audit_gap(frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
