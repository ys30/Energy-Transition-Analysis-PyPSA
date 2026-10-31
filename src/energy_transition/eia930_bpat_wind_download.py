"""Download official EIA-930 BPAT WND hourly generation, preserving source coverage."""
import argparse
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

import pandas as pd

API = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"


def fetch_bpat_wind(year: int, api_key: str | None = None):
    key = api_key or os.environ.get("EIA_API_KEY")
    if not key:
        raise ValueError("EIA_API_KEY is required")
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", "BPAT"), ("facets[fueltype][]", "WND"),
        ("start", f"{year}-01-01T00"), ("end", f"{year}-12-31T23"),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", "0"), ("length", "5000"),
    ]
    rows = []
    offset = 0
    while True:
        query = [(k, str(offset) if k == "offset" else v) for k, v in params]
        request = urllib.request.Request(API + "?" + urllib.parse.urlencode(query),
                                         headers={"User-Agent": "energy-transition-pypsa/0.5"})
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.load(response)
        data = payload.get("response", {}).get("data")
        if data is None:
            raise ValueError("EIA-930 fuel-type API response missing data")
        total = int(payload["response"].get("total", offset + len(data)))
        if total < 0 or (not data and offset < total):
            raise ValueError("Invalid EIA-930 pagination")
        rows.extend(data)
        offset += len(data)
        if offset >= total:
            break
    if not rows:
        raise ValueError("No BPAT WND source observations")
    frame = pd.DataFrame(rows)
    required = {"period", "respondent", "fueltype", "value"}
    if required - set(frame):
        raise ValueError(f"Missing EIA-930 fields: {sorted(required-set(frame))}")
    frame = frame[["period", "respondent", "fueltype", "value"]].copy()
    if not frame.respondent.eq("BPAT").all() or not frame.fueltype.eq("WND").all():
        raise ValueError("EIA-930 returned non-BPAT or non-WND records")
    frame["period"] = pd.to_datetime(frame.period, utc=True, errors="raise")
    raw = frame.value
    frame["value"] = pd.to_numeric(raw, errors="coerce")
    if (raw.notna() & frame.value.isna()).any():
        raise ValueError("Malformed non-null EIA-930 WND measurement")
    if frame.period.duplicated().any():
        raise ValueError("Duplicate BPAT WND timestamps")
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                             freq="h", inclusive="left", tz="UTC")
    missing = expected.difference(pd.DatetimeIndex(frame.period))
    extra = pd.DatetimeIndex(frame.period).difference(expected)
    summary = {
        "source": API, "year": year, "ba": "BPAT", "fueltype": "WND",
        "units": "MW hourly (sum equals MWh for one-hour intervals)",
        "expected_hours": len(expected), "received_hours": len(frame),
        "missing_timestamp_hours": len(missing), "extra_timestamp_hours": len(extra),
        "null_value_hours": int(frame.value.isna().sum()),
        "complete": bool(not len(missing) and not len(extra) and frame.value.notna().all()),
        "observed_wind_mwh_nonmissing_only": float(frame.value.sum()),
        "warning": "Incomplete annual coverage cannot establish annual wind generation."
    }
    return frame, summary, missing


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--output", type=Path, default=Path("outputs/bpat_wind_source"))
    args = p.parse_args()
    frame, summary, missing = fetch_bpat_wind(args.year)
    args.output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output / "eia930_bpat_wnd_hourly.csv", index=False)
    pd.DataFrame({"timestamp_utc": missing}).to_csv(args.output / "missing_hours.csv", index=False)
    (args.output / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
