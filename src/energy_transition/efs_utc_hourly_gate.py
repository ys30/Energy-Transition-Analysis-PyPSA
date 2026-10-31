"""Strict UTC hourly time-series gate for externally sourced EFS/state load.

Do not interpret local timestamps without explicit offset as UTC. Reject gaps,
duplicate hours, malformed timestamps, and non-finite/negative demand.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import math


def validate_utc_hourly(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("Empty demand time series")
    series = defaultdict(dict)
    for row in rows:
        state = row["state"].strip()
        if not state:
            raise ValueError("Missing state")
        raw = row["snapshot"]
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() != timedelta(0):
            raise ValueError(f"Timestamp must carry UTC offset: {raw}")
        if dt.minute or dt.second or dt.microsecond:
            raise ValueError(f"Timestamp must align to UTC hour: {raw}")
        demand = float(row["demand_mw"])
        if not math.isfinite(demand) or demand < 0:
            raise ValueError(f"Invalid demand at {state}/{raw}")
        timestamp = dt.astimezone(timezone.utc)
        if timestamp in series[state]:
            raise ValueError(f"Duplicate UTC hour: {state}/{raw}")
        series[state][timestamp] = demand
    expected = None
    for state, values in series.items():
        hours = sorted(values)
        if any(b - a != timedelta(hours=1) for a, b in zip(hours, hours[1:])):
            raise ValueError(f"Missing or non-hourly UTC snapshots for {state}")
        if expected is None:
            expected = hours
        elif hours != expected:
            raise ValueError(f"Cross-state UTC coverage mismatch: {state}")
    return {"states": len(series), "hours_per_state": len(expected),
            "start_utc": expected[0].isoformat(), "end_utc": expected[-1].isoformat(),
            "all_utc_hourly_contiguous": True,
            "note": "UTC timestamps validated; upstream source and demand meaning require separate provenance audit"}
